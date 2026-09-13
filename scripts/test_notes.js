#!/usr/bin/env node
/**
 * test_notes.js — js/notes.js 定点回归（F02 / F05 / F06 / F07）
 *
 * js/notes.js 在 vm 沙箱里跑，localStorage / DOM / alert 全部换成桩；
 * 两个沙箱共用一个存储后端，即可复现多标签页场景。
 * 覆盖：输入即保存、关闭重开不丢、整批校验拒绝脏数据、持久化失败如实报错、
 *       草稿可导出、旧 v1 整表安全迁移、多页不同/同条并发。
 *
 * 用法：node scripts/test_notes.js
 */
"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const SRC = fs.readFileSync(path.join(__dirname, "..", "js", "notes.js"), "utf8");
const V1 = "wp_notes_v1";
const P2 = "wp_note_v2:";

let passed = 0;
let failed = 0;
function check(name, cond, detail) {
  if (cond) { passed++; console.log("  \u2713 " + name); }
  else { failed++; console.log("  \u2717 " + name + (detail ? "  \u2192 " + detail : "")); }
}
function group(title) { console.log("\n" + title); }
function quotaError() { const e = new Error("QuotaExceededError"); e.name = "QuotaExceededError"; return e; }

/* ---------- 共享存储后端（可广播 storage 事件给其他标签页） ---------- */
function createBackend(seed) {
  const data = new Map(Object.entries(seed || {}));
  const subscribers = [];
  let seq = 0;
  return {
    data,
    has: k => data.has(k),
    get: k => (data.has(k) ? data.get(k) : null),
    raw: k => (data.has(k) ? JSON.parse(data.get(k)) : null),
    dump: () => JSON.stringify(Object.fromEntries(data)),
    nextId: () => ++seq,
    subscribe(id, fn) { subscribers.push({ id, fn }); },
    broadcast(fromId, ev) { subscribers.forEach(s => { if (s.id !== fromId) s.fn(ev); }); },
  };
}

/* ---------- 一个“标签页” = 一个 vm 沙箱 ---------- */
function createTab(backend, opts) {
  opts = opts || {};
  const id = backend.nextId();
  const ctl = { failWrites: !!opts.failWrites, failAll: !!opts.failAll };
  const els = {
    noteArea: { value: "", oninput: null },
    noteStatus: { textContent: "" },
    jsonFileInput: { files: [], click() {}, onchange: null },
  };
  const listeners = { storage: [], beforeunload: [], pagehide: [] };
  const tab = { id, ctl, els, alerts: [], modal: null, modalClosed: 0 };

  const localStorage = {
    get length() { return backend.data.size; },
    key(i) { const ks = Array.from(backend.data.keys()); return ks[i] === undefined ? null : ks[i]; },
    getItem(k) { if (ctl.failAll) throw quotaError(); return backend.has(k) ? backend.get(k) : null; },
    setItem(k, v) {
      if (ctl.failAll || ctl.failWrites) throw quotaError();
      const oldValue = backend.has(k) ? backend.get(k) : null;
      backend.data.set(k, String(v));
      backend.broadcast(id, { key: k, oldValue: oldValue, newValue: String(v) });
    },
    removeItem(k) {
      if (ctl.failAll || ctl.failWrites) throw quotaError();
      const oldValue = backend.has(k) ? backend.get(k) : null;
      backend.data.delete(k);
      backend.broadcast(id, { key: k, oldValue: oldValue, newValue: null });
    },
  };
  backend.subscribe(id, ev => listeners.storage.forEach(fn => fn(ev)));

  const sandbox = {
    localStorage,
    window: {
      addEventListener(type, fn) { (listeners[type] = listeners[type] || []).push(fn); },
    },
    document: {
      getElementById: k => els[k] || null,
      addEventListener() {},
      createElement: () => ({ style: {}, click() {} }),
      body: { appendChild() {}, removeChild() {} },
      visibilityState: "visible",
    },
    alert: m => tab.alerts.push(String(m)),
    openModal: html => { tab.modal = html; },
    closeModal: () => { tab.modal = null; tab.modalClosed++; },
    esc: s => String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;"),
    Blob: function Blob() {},
    URL: { createObjectURL: () => "blob:test", revokeObjectURL() {} },
    FileReader: class { readAsText(f) { this.result = f.__text; if (this.onload) this.onload(); } },
    setTimeout: () => 0,
    console,
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(SRC, sandbox, { filename: "js/notes.js" });
  tab.sandbox = sandbox;
  tab.eval = code => vm.runInContext(code, sandbox);
  tab.fireBeforeUnload = () => {
    const ev = { defaultPrevented: false, returnValue: undefined, preventDefault() { this.defaultPrevented = true; } };
    listeners.beforeunload.forEach(fn => fn(ev));
    return ev;
  };
  return tab;
}

/* ================= F02 自动保存 ================= */
group("F02 自动保存：输入即写入，关闭卡片再打开不丢");
{
  const be = createBackend();
  const A = createTab(be);
  A.sandbox.loadNote("char:pierre");

  A.els.noteArea.value = "AUDIT_UNSAVED_NOTE";
  A.els.noteArea.oninput();
  const saved = be.raw(P2 + "char:pierre");
  check("input 后存储里就有", !!saved && saved.text === "AUDIT_UNSAVED_NOTE", JSON.stringify(saved));
  check("状态提示已保存", /已保存/.test(A.els.noteStatus.textContent), A.els.noteStatus.textContent);

  A.els.noteArea.value = "";
  A.sandbox.loadNote("char:pierre");                      // 关闭后重新打开
  check("重开后内容还在", A.els.noteArea.value === "AUDIT_UNSAVED_NOTE", A.els.noteArea.value);
}

/* ================= F07 多标签页 ================= */
group("F07 多标签页：各写不同笔记互不覆盖，同一条以最后成功写入为准");
{
  const be = createBackend();
  const A = createTab(be);
  const B = createTab(be);                                 // 同一份存储，启动时都为空
  A.sandbox.loadNote("char:pierre");
  A.els.noteArea.value = "A的皮埃尔笔记";
  A.els.noteArea.oninput();
  B.sandbox.loadNote("char:andrei");
  B.els.noteArea.value = "B的安德烈笔记";
  B.els.noteArea.oninput();
  check("A 的笔记还在", (be.raw(P2 + "char:pierre") || {}).text === "A的皮埃尔笔记");
  check("B 的笔记也在", (be.raw(P2 + "char:andrei") || {}).text === "B的安德烈笔记");

  A.sandbox.loadNote("char:pierre");
  A.els.noteArea.value = "A 改";
  A.els.noteArea.oninput();
  B.sandbox.loadNote("char:pierre");
  B.els.noteArea.value = "B 改";
  B.els.noteArea.oninput();
  check("同条并发最后写入者为准", (be.raw(P2 + "char:pierre") || {}).text === "B 改");
  check("A 页同步到 B 的写入", A.els.noteArea.value === "B 改", A.els.noteArea.value);
  check("A 页提示来自其他页面", /其他页面同步/.test(A.els.noteStatus.textContent), A.els.noteStatus.textContent);

  const be2 = createBackend();
  const C = createTab(be2);
  const D = createTab(be2);
  C.ctl.failWrites = true;
  C.sandbox.loadNote("char:pierre");
  C.els.noteArea.value = "C 的未持久化草稿";
  C.els.noteArea.oninput();
  D.sandbox.loadNote("char:pierre");
  D.els.noteArea.value = "D 的写入";
  D.els.noteArea.oninput();
  check("远端写入不覆盖本页草稿", C.els.noteArea.value === "C 的未持久化草稿", C.els.noteArea.value);
  check("本页状态提示冲突", /其他页面也改过/.test(C.els.noteStatus.textContent), C.els.noteStatus.textContent);
}

/* ================= F05 导入校验 ================= */
group("F05 导入整批先校验：数值 text / 非法键 / 版本 / 时间戳全部拒绝且旧笔记不变");
{
  const be = createBackend();
  const A = createTab(be);
  A.sandbox.loadNote("char:pierre");
  A.els.noteArea.value = "旧笔记";
  A.els.noteArea.oninput();
  const before = be.dump();

  const r1 = A.sandbox.importNotesData({ version: 1, notes: { "char:pierre": { text: 123, at: 0 } } });
  check("数值 text 整批拒绝", r1.ok === false && /不合法/.test(r1.message), r1.message);
  check("存储一字未动", be.dump() === before);

  const r2 = A.sandbox.importNotesData({ version: 1, notes: { pierre: { text: "x" } } });
  check("非法键名整批拒绝", r2.ok === false, r2.message);
  const r3 = A.sandbox.importNotesData({ version: 9, notes: { "char:pierre": { text: "x" } } });
  check("不认识的版本整批拒绝", r3.ok === false && /版本/.test(r3.message), r3.message);
  const r4 = A.sandbox.importNotesData({ version: 1, notes: { "char:pierre": { text: "x", at: "昨天" } } });
  check("非法时间戳整批拒绝", r4.ok === false, r4.message);
  const r5 = A.sandbox.importNotesData(JSON.parse('{"version":1,"notes":{"__proto__":{"text":"x"}}}'));
  check("原型相关键整批拒绝", r5.ok === false, r5.message);
  const r6 = A.sandbox.importNotesData({ version: 2, notes: {} });
  check("空批次不算成功", r6.ok === false, r6.message);
  check("导出不因脏输入崩", typeof A.sandbox.notesToMarkdown() === "string" &&
    /旧笔记/.test(A.sandbox.notesToMarkdown()));
}

/* ================= F06 持久化失败 ================= */
group("F06 持久化失败：如实报错、草稿不丢、离开前提示");
{
  const be = createBackend();
  const C = createTab(be);
  C.ctl.failWrites = true;
  C.sandbox.loadNote("char:pierre");
  C.els.noteArea.value = "配额满时的草稿";
  C.els.noteArea.oninput();
  check("不显示已保存", !/已保存/.test(C.els.noteStatus.textContent) &&
    /保存失败/.test(C.els.noteStatus.textContent) && /草稿/.test(C.els.noteStatus.textContent),
    C.els.noteStatus.textContent);
  check("存储确实没写进去", be.get(P2 + "char:pierre") === null);

  const payload = C.sandbox.buildExportPayload();
  check("导出标记未持久化", payload.unpersisted && payload.unpersisted.indexOf("char:pierre") >= 0);
  check("草稿文本可导出", payload.notes["char:pierre"].text === "配额满时的草稿");
  check("Markdown 标注草稿", /未持久化草稿/.test(C.sandbox.notesToMarkdown()));
  const ev = C.fireBeforeUnload();
  check("离开前提示未持久化", ev.defaultPrevented === true && !!ev.returnValue);

  C.ctl.failWrites = false;
  C.sandbox.loadNote("char:pierre");
  check("存储恢复后草稿补写成功", (be.raw(P2 + "char:pierre") || {}).text === "配额满时的草稿");
  check("补写后提示已保存", /已保存/.test(C.els.noteStatus.textContent), C.els.noteStatus.textContent);
  check("补写后不再提示离开", C.fireBeforeUnload().defaultPrevented === false);
}
{
  const be = createBackend();
  const D = createTab(be);
  D.sandbox.loadNote("ch:1-1-01");
  D.els.noteArea.value = "先存一条";
  D.els.noteArea.oninput();
  check("先保存成功", /已保存/.test(D.els.noteStatus.textContent));
  D.ctl.failWrites = true;
  D.els.noteArea.value = "";
  D.els.noteArea.oninput();
  check("清空失败如实提示", /清空失败/.test(D.els.noteStatus.textContent), D.els.noteStatus.textContent);
  check("原笔记仍在存储里", (be.raw(P2 + "ch:1-1-01") || {}).text === "先存一条");
  D.ctl.failWrites = false;
  D.els.noteArea.value = "";
  D.els.noteArea.oninput();
  const reloaded = createTab(be);
  reloaded.sandbox.loadNote("ch:1-1-01");
  check("正常清空后重新加载仍为空", reloaded.els.noteArea.value === "");
}
{
  const be = createBackend();
  const M = createTab(be, { failAll: true });            // 隐私模式：任何存储访问都抛
  M.sandbox.loadNote("char:pierre");
  check("禁用存储时提示不可用", /存储不可用/.test(M.els.noteStatus.textContent), M.els.noteStatus.textContent);
  M.els.noteArea.value = "隐私模式草稿";
  M.els.noteArea.oninput();
  check("禁用存储时不显示已保存", !/已保存/.test(M.els.noteStatus.textContent), M.els.noteStatus.textContent);
  check("禁用存储时草稿仍可导出", M.sandbox.buildExportPayload().notes["char:pierre"].text === "隐私模式草稿");
  M.sandbox.exportNotes();
  check("禁用存储时导出弹层提示风险", /存储当前不可用/.test(M.modal));
}

/* ================= 旧数据迁移 ================= */
group("旧数据迁移：整表校验通过且写入成功才移除；异常旧数据原样保留");
{
  const be = createBackend({ [V1]: JSON.stringify({ "char:pierre": { text: "旧版笔记", at: 1000 } }) });
  const E = createTab(be);
  check("旧整表迁移为单条存储", (be.raw(P2 + "char:pierre") || {}).text === "旧版笔记");
  check("迁移成功后移除旧键", !be.has(V1));
}
{
  const be = createBackend({
    [V1]: JSON.stringify({ "char:pierre": { text: "好的", at: 1000 }, "ch:1-1-01": { text: 5 } })
  });
  const F = createTab(be);
  check("合法条目已迁移", (be.raw(P2 + "char:pierre") || {}).text === "好的");
  check("含异常记录时不删旧整表", be.has(V1));
  check("异常旧数据原样进入备份",
    F.sandbox.buildExportPayload().quarantine.some(r => r.raw === '{"text":5}'));
  check("导出带走原文", /无法读取的本机旧记录/.test(F.sandbox.notesToMarkdown()));
}
{
  const be = createBackend({ [V1]: "{坏掉的 JSON" });
  const G = createTab(be);
  check("整表解析失败时不删旧数据", be.has(V1) && be.get(V1) === "{坏掉的 JSON");
  check("无法解析的原文仍可备份",
    G.sandbox.buildExportPayload().quarantine.some(r => r.raw === "{坏掉的 JSON"));
}
{
  const be = createBackend({ [P2 + "char:pierre"]: JSON.stringify({ text: "更新的", at: 2000 }) });
  be.data.set(V1, JSON.stringify({ "char:pierre": { text: "更旧的", at: 1000 } }));
  const H = createTab(be);
  check("同键保留更新的记录", (be.raw(P2 + "char:pierre") || {}).text === "更新的");
  check("旧整表仍被移除", !be.has(V1));
}

{
  const be = createBackend({
    [V1]: JSON.stringify({ "char:pierre": { text: "旧笔记", at: 1000 }, "bad": { text: 5 } }),
  });
  const A = createTab(be);
  A.sandbox.loadNote("char:pierre");
  A.els.noteArea.value = "";
  A.els.noteArea.oninput();
  const B = createTab(be);
  B.sandbox.loadNote("char:pierre");
  check("旧表含坏记录时，已清空笔记不会被迁移复活", B.els.noteArea.value === "");
}

{
  const be = createBackend();
  const A = createTab(be);
  A.sandbox.loadNote("char:pierre");
  A.els.noteArea.value = "  保留缩进\n";
  A.els.noteArea.oninput();
  const B = createTab(be);
  B.sandbox.loadNote("char:pierre");
  check("自动保存保留用户输入的空白", B.els.noteArea.value === "  保留缩进\n");
  B.ctl.failWrites = true;
  B.els.noteArea.value = "";
  B.els.noteArea.oninput();
  check("清空失败仍保留删除意图并提示离开",
    B.sandbox.buildExportPayload().notes["char:pierre"].text === "" &&
    B.fireBeforeUnload().defaultPrevented);
}

/* ================= 脏存储不炸导出 ================= */
group("脏存储：读不出/校验失败的历史数据不炸导出 UI，且不被删除");
{
  const be = createBackend({
    [P2 + "char:pierre"]: '{"text":123,"at":0}',
    [P2 + "event:e-sherer-saloon"]: "{不是 JSON",
  });
  const I = createTab(be);
  check("脏记录未被删除", be.get(P2 + "char:pierre") === '{"text":123,"at":0}' &&
    be.get(P2 + "event:e-sherer-saloon") === "{不是 JSON");
  I.sandbox.exportNotes();
  check("导出弹层提示异常旧记录", /无法读取/.test(I.modal));
  const md = I.sandbox.notesToMarkdown();
  check("Markdown 保留无法解析的原文", md.includes("{不是 JSON") && md.includes('"text":123'));
  const backup = I.sandbox.buildExportPayload();
  check("JSON 备份保留两条原始坏记录",
    backup.quarantine.some(r => r.raw === '{"text":123,"at":0}') &&
    backup.quarantine.some(r => r.raw === "{不是 JSON"));
  const beforeImport = be.dump();
  check("含隔离原文的备份不能被静默部分导入",
    !I.sandbox.importNotesData(backup).ok && be.dump() === beforeImport);
}

/* ================= 导入落盘与界面路径 ================= */
group("导入：全部落盘才报成功；界面导入拒绝脏文件且不关弹层");
{
  const be = createBackend();
  const I = createTab(be);
  const ok = I.sandbox.importNotesData({
    version: 2, exportedAt: "x",
    notes: { "char:pierre": { text: "导入一", at: 10 }, "event:e-1": { text: "导入二", at: 11 } },
  });
  check("两条都导入成功", ok.ok === true && ok.imported === 2, ok.message);
  check("两条都落盘", (be.raw(P2 + "char:pierre") || {}).text === "导入一" &&
    (be.raw(P2 + "event:e-1") || {}).text === "导入二");
  const legacy = I.sandbox.importNotesData({ notes: { "ch:1-1-01": { text: "无版本字段" } } });
  check("兼容无 version 的旧文件", legacy.ok === true && (be.raw(P2 + "ch:1-1-01") || {}).text === "无版本字段");

  I.ctl.failWrites = true;
  const part = I.sandbox.importNotesData({ notes: { "ch:2-1-01": { text: "写不进去" } } });
  check("部分失败不谎报全部成功", part.ok === false && /1 条写入失败/.test(part.message), part.message);
  check("失败内容留作可导出草稿", I.sandbox.buildExportPayload().unpersisted.indexOf("ch:2-1-01") >= 0);
}
{
  const be = createBackend();
  const J = createTab(be);
  J.els.jsonFileInput.files = [{ __text: '{"version":1,"notes":{"char:pierre":{"text":123,"at":0}}}' }];
  J.sandbox.importJSON();
  J.els.jsonFileInput.onchange();                        // 桩不弹文件框，手动触发选择后回调
  check("界面导入路径拒绝数值 text", J.alerts.length === 1 && /导入失败/.test(J.alerts[0]), J.alerts.join(" | "));
  check("失败时弹层不关闭", J.modalClosed === 0);
  check("失败时存储未写入", be.get(P2 + "char:pierre") === null);

  const K = createTab(be);
  K.els.jsonFileInput.files = [{ __text: "{不是 JSON" }];
  K.sandbox.importJSON();
  K.els.jsonFileInput.onchange();
  check("坏 JSON 文件不崩", K.alerts.length === 1 && /不是有效的 JSON/.test(K.alerts[0]), K.alerts.join(" | "));

  const L = createTab(be);
  L.els.jsonFileInput.files = [{ __text: '{"version":2,"notes":{"char:pierre":{"text":"界面导入","at":5}}}' }];
  L.sandbox.importJSON();
  L.els.jsonFileInput.onchange();
  check("界面导入成功落盘并关闭弹层", (be.raw(P2 + "char:pierre") || {}).text === "界面导入" &&
    L.modalClosed === 1 && /已导入 1 条/.test(L.alerts[0]), L.alerts.join(" | "));
}

console.log(`\n${passed} passed, ${failed} failed`);
if (failed) process.exitCode = 1;
