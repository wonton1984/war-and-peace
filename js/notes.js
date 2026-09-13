// js/notes.js — 拆书笔记（localStorage + Markdown / JSON 导出）
"use strict";

/* 存储格式
 *   v1（遗留整表）: wp_notes_v1          = { "char:pierre": { text, at }, … }
 *   v2（当前单条）: wp_note_v2:<noteKey> = { "text": "…", "at": 1699999999999 }
 *   noteKey 形如 char:<id> / event:<id> / ch:<id>，id 只含 [A-Za-z0-9._-]。
 *   导出信封:      { version: 2, exportedAt, notes: { noteKey: { text, at } },
 *                    unpersisted?: [noteKey…], quarantine?: [{ key, raw }] }
 *
 * 写入语义
 *   按条写入、按条合并：一次保存只触碰自己那一条存储键，不再整表覆盖。
 *   自动保存即时进行（textarea 的 input 事件），持久化失败时草稿留在内存并可导出。
 *   同一 noteKey 多页并发：最后一次写入成功者为准；其他页通过 storage 事件同步，
 *   清空写入空文本墓碑，防止尚未完全迁移的 v1 表在重启时复活已删除笔记。
 *   本页存在未持久化草稿时不被远端覆盖。
 */
const NOTE_KEY_V1 = "wp_notes_v1";
const NOTE_PREFIX = "wp_note_v2:";
const NOTE_VERSION = 2;
const NOTE_KEY_RE = /^(char|event|ch):[A-Za-z0-9._-]+$/;
const NOTE_BAD_KEYS = new Set(["__proto__", "constructor", "prototype"]);
const NOTE_MAX_AT = 8640000000000000;   // Date 可表示的最大时间戳

let notes = Object.create(null);        // noteKey → { text, at }，含未持久化草稿
const drafts = Object.create(null);     // noteKey → true：最近一次写入未落到存储
let quarantine = Object.create(null);   // 存储键 → 原始字符串：无法解析/校验的旧数据
let currentKey = null;                  // 当前打开的笔记键
let storageOk = true;                   // localStorage 是否可访问

const DRAFT_HINT = "未持久化（草稿保留在本页，可导出）";

/* ---------- 存储访问：任何异常都不抛出；成功访问即认为存储可用 ---------- */
function rawGet(k) {
  try { const v = localStorage.getItem(k); storageOk = true; return v; }
  catch (e) { storageOk = false; return null; }
}
function rawSet(k, v) {
  try { localStorage.setItem(k, v); storageOk = true; return true; }
  catch (e) { storageOk = false; return false; }   // 隐私模式 / 配额满
}
function rawRemove(k) {
  try { localStorage.removeItem(k); storageOk = true; return true; }
  catch (e) { storageOk = false; return false; }
}
function rawKeys() {
  try {
    const out = [];
    for (let i = 0; i < localStorage.length; i++) out.push(localStorage.key(i));
    storageOk = true;
    return out;
  } catch (e) { storageOk = false; return []; }
}

/* ---------- 校验 ---------- */
/* 普通对象判定：原型链只有一层（对象字面量 / Object.create(null)）。
 * 用链深而非 === Object.prototype，跨 realm（iframe、测试沙箱）同样成立。 */
function plainObject(v) {
  if (!v || typeof v !== "object" || Array.isArray(v)) return false;
  const proto = Object.getPrototypeOf(v);
  return proto === null || Object.getPrototypeOf(proto) === null;
}
function safeStringify(v) {
  try { return JSON.stringify(v); } catch (e) { return String(v); }
}
function brief(v) {
  const s = typeof v === "string" ? v : safeStringify(v);
  return (s === undefined ? String(v) : s).slice(0, 40);
}
function validNoteKey(key) {
  return typeof key === "string" && !NOTE_BAD_KEYS.has(key) && NOTE_KEY_RE.test(key);
}
function validAt(at) {
  return typeof at === "number" && Number.isFinite(at) && at >= 0 && at <= NOTE_MAX_AT;
}
/* 单条记录校验；返回 { ok:true, rec } 或 { ok:false, why }。at 缺省视为现在。 */
function checkRecord(key, rec) {
  if (!validNoteKey(key)) return { ok: false, why: `笔记键格式非法（${brief(key)}）` };
  if (!plainObject(rec)) return { ok: false, why: `记录不是普通对象（${key}）` };
  if (typeof rec.text !== "string") return { ok: false, why: `text 必须是字符串（${key}）` };
  if (rec.at !== undefined && !validAt(rec.at)) return { ok: false, why: `at 不是有限合法时间戳（${key}）` };
  return { ok: true, rec: { text: rec.text, at: rec.at === undefined ? Date.now() : rec.at } };
}
function timeStr(at) { return new Date(at).toLocaleString("zh-CN"); }
function recordText(rec) { return rec && typeof rec.text === "string" ? rec.text : ""; }

/* ---------- 单条读写 ---------- */
function persistRecord(key, rec) {
  return rawSet(NOTE_PREFIX + key, safeStringify({ text: rec.text, at: rec.at }));
}
function dropRecord(key) {
  delete notes[key];
  delete drafts[key];
}

/* ---------- 读取：v2 单条 + v1 安全迁移 ---------- */
function parseStoredRecord(key, raw) {
  if (typeof raw !== "string") return { ok: false, why: "内容缺失" };
  let rec;
  try { rec = JSON.parse(raw); } catch (e) { return { ok: false, why: "不是有效 JSON" }; }
  if (plainObject(rec) && rec.v !== undefined && rec.v !== NOTE_VERSION)
    return { ok: false, why: "存储版本不认识" };
  return checkRecord(key, rec);
}

function loadStoredNotes() {
  rawKeys().forEach(sk => {
    if (typeof sk !== "string" || sk.indexOf(NOTE_PREFIX) !== 0) return;
    const key = sk.slice(NOTE_PREFIX.length);
    const raw = rawGet(sk);
    const chk = parseStoredRecord(key, raw);
    if (chk.ok) { notes[key] = chk.rec; delete drafts[key]; }
    else quarantine[sk] = raw === null ? "" : String(raw);   // 读不出也不能删
  });
}

/* v1 整表只在「全部记录校验通过且全部写入成功」后才移除；
 * 任何一条不合法或写入失败都保留原 wp_notes_v1，避免丢数据。 */
function migrateV1() {
  const raw = rawGet(NOTE_KEY_V1);
  if (typeof raw !== "string") return;
  let table;
  try { table = JSON.parse(raw); } catch (e) { table = null; }
  if (!plainObject(table)) { quarantine[NOTE_KEY_V1] = raw; return; }
  let clean = true;
  let wrote = true;
  Object.keys(table).forEach(key => {
    const chk = checkRecord(key, table[key]);
    if (!chk.ok) { clean = false; quarantine[NOTE_KEY_V1 + ":" + key] = safeStringify(table[key]); return; }
    if (drafts[key]) return;                        // 本页有未持久化草稿，不覆盖
    const stored = rawGet(NOTE_PREFIX + key);
    if (stored !== null && parseStoredRecord(key, stored).ok) return;
    notes[key] = chk.rec;
    if (!persistRecord(key, chk.rec)) { drafts[key] = true; wrote = false; }
  });
  if (clean && wrote) rawRemove(NOTE_KEY_V1);
}

function loadNotes() {
  const pending = Object.create(null);              // 本页未持久化草稿不因重载丢失
  Object.keys(drafts).forEach(k => { if (notes[k]) pending[k] = notes[k]; });
  notes = Object.create(null);
  quarantine = Object.create(null);
  loadStoredNotes();
  migrateV1();
  Object.keys(pending).forEach(k => { notes[k] = pending[k]; drafts[k] = true; });
  Object.keys(drafts).forEach(k => { if (!notes[k]) delete drafts[k]; });
}
loadNotes();

/* ---------- 写入 ---------- */
/* 返回 { ok, status }；status 即 noteStatus 的文案，成功与失败都不含糊。 */
function writeNote(key, text) {
  if (!validNoteKey(key)) return { ok: false, status: `笔记键格式非法（${brief(key)}）` };
  const cur = notes[key];
  if (cur && cur.text === text && !drafts[key]) return { ok: true, status: idleStatus(key) };
  const rec = { text, at: Date.now() };
  notes[key] = rec;
  if (persistRecord(key, rec)) {
    delete drafts[key];
    return { ok: true, status: text === "" ? "已清空" : "已保存 · " + timeStr(rec.at) };
  }
  drafts[key] = true;
  return { ok: false, status: (text === "" ? "清空失败" : "保存失败") +
    "（浏览器可能禁用了本地存储）· 草稿保留在本页，可导出" };
}

/* 补写内存中未持久化的草稿；返回剩余条数 */
function flushDrafts() {
  Object.keys(drafts).forEach(k => {
    const rec = notes[k];
    if (!rec) { delete drafts[k]; return; }
    if (persistRecord(k, rec)) delete drafts[k];
  });
  return Object.keys(drafts).length;
}

function idleStatus(key) {
  if (!storageOk) return "本机存储不可用：笔记只保留在本页内存中，可导出";
  if (drafts[key]) return DRAFT_HINT;
  return notes[key] ? (notes[key].text === "" ? "已清空" : "已保存 · " + timeStr(notes[key].at)) : "";
}

function loadNote(key) {
  const ta = document.getElementById("noteArea");
  const st = document.getElementById("noteStatus");
  if (!ta) return;
  currentKey = key;
  flushDrafts();                                    // 打开卡片时顺手补写上次失败的草稿
  ta.value = notes[key] ? notes[key].text : "";
  if (st) st.textContent = idleStatus(key);
  ta.oninput = () => {
    const res = writeNote(key, ta.value);
    if (st) st.textContent = res.status;
  };
}

function saveNote(key) {
  const ta = document.getElementById("noteArea");
  const st = document.getElementById("noteStatus");
  if (!ta) return;
  const res = writeNote(key, ta.value);
  if (st) st.textContent = res.status;
}

/* 其他页面改动后刷新当前卡片：本页有草稿则不覆盖输入框 */
function syncCard(key, status) {
  if (key !== currentKey) return;
  const ta = document.getElementById("noteArea");
  const st = document.getElementById("noteStatus");
  if (ta && !drafts[key]) ta.value = notes[key] ? notes[key].text : "";
  if (st) st.textContent = status || idleStatus(key);
}

/* ---------- 多页同步（同一条：最后成功写入者为准） ---------- */
function onStorage(e) {
  if (e.key === null) { loadNotes(); syncCard(currentKey, ""); return; }   // 整库被清空
  if (typeof e.key !== "string") return;
  if (e.key === NOTE_KEY_V1) { migrateV1(); return; }
  if (e.key.indexOf(NOTE_PREFIX) !== 0) return;
  const key = e.key.slice(NOTE_PREFIX.length);
  if (e.newValue === null || e.newValue === undefined) {
    if (!drafts[key]) { dropRecord(key); syncCard(key, ""); }
    return;
  }
  const chk = parseStoredRecord(key, e.newValue);
  if (!chk.ok) { quarantine[e.key] = String(e.newValue); return; }
  if (drafts[key]) { syncCard(key, "其他页面也改过这条笔记：本页草稿尚未持久化，保留本页内容"); return; }
  notes[key] = chk.rec;
  syncCard(key, "已从其他页面同步 · " + timeStr(chk.rec.at));
}

if (typeof window !== "undefined") {
  window.addEventListener("storage", onStorage);
  window.addEventListener("beforeunload", e => {
    if (flushDrafts()) {
      e.preventDefault();
      e.returnValue = "有笔记尚未保存到本机浏览器，确定离开？";
      return e.returnValue;
    }
  });
  window.addEventListener("pagehide", flushDrafts);
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") flushDrafts();
  });
}

/* ---------- 导出 Markdown ---------- */
function noteLabel(key) {
  const id = key.split(":")[1];
  if (key.indexOf("char:") === 0)
    return (typeof charById === "function" ? charById(id) || {} : {}).name || key;
  if (key.indexOf("event:") === 0) {
    const e = (typeof EVENT_BY_ID === "object" && EVENT_BY_ID) ? EVENT_BY_ID[id] : null;
    return (e && e.title) || key;
  }
  const c = (typeof CHAPTER_BY_ID === "object" && CHAPTER_BY_ID) ? CHAPTER_BY_ID[id] : null;
  return id + (c && c.gist ? " · " + String(c.gist).slice(0, 24) + "…" : "");
}

function notesToMarkdown() {
  const keys = Object.keys(notes).filter(k => recordText(notes[k]) !== "" || drafts[k]);
  const pending = Object.keys(drafts).filter(k => notes[k]);
  const qkeys = Object.keys(quarantine);
  const out = ["# 战争与和平 · 拆书笔记", "",
    `> 导出时间：${new Date().toLocaleString("zh-CN")}`,
    `> 共 ${keys.length} 条笔记` + (pending.length ? `（其中 ${pending.length} 条未写入本机存储，已一并导出）` : ""),
    ""];
  if (!keys.length) out.push("（暂无笔记）", "");

  const groups = { char: [], event: [], ch: [] };
  keys.forEach(k => { const t = k.split(":")[0]; (groups[t] = groups[t] || []).push(k); });
  [["人物", groups.char], ["事件", groups.event], ["章节", groups.ch]].forEach(([title, list]) => {
    if (!list.length) return;
    out.push("## " + title, "");
    list.slice().sort().forEach(k => {
      out.push(`### ${noteLabel(k)}${drafts[k] ? "（未持久化草稿）" : ""}`, "", recordText(notes[k]), "");
    });
  });

  if (qkeys.length) {
    out.push("## 无法读取的本机旧记录（原样保留）", "",
      `共 ${qkeys.length} 条，无法解析或校验，已原样备份：`, "");
    qkeys.forEach(k => out.push("### " + k, "", "```", String(quarantine[k]), "```", ""));
  }
  return out.join("\n");
}

function download(filename, text, mime) {
  const blob = new Blob([text], { type: mime || "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename;
  document.body.appendChild(a); a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

/* 备份载荷：内存可读记录 + 失败草稿标记 + 无法读取的旧数据原文 */
function buildExportPayload() {
  const exported = Object.create(null);
  Object.keys(notes).forEach(k => {
    const rec = notes[k];
    if (rec) exported[k] = { text: recordText(rec), at: rec.at };
  });
  const payload = {
    version: NOTE_VERSION,
    exportedAt: new Date().toISOString(),
    notes: exported,
  };
  const pending = Object.keys(drafts).filter(k => notes[k]);
  if (pending.length) payload.unpersisted = pending;
  const q = Object.keys(quarantine).map(k => ({ key: k, raw: String(quarantine[k]) }));
  if (q.length) payload.quarantine = q;
  return payload;
}

function exportNotes() {
  const keys = Object.keys(notes).filter(k => recordText(notes[k]) !== "" || drafts[k]);
  const pending = Object.keys(drafts).filter(k => notes[k]);
  const qn = Object.keys(quarantine).length;
  const recent = keys.slice().sort((a, b) => (notes[b].at || 0) - (notes[a].at || 0)).slice(0, 8);
  openModal(`
    <h2>拆书笔记 · 导出</h2>
    <p>当前共 <b>${keys.length}</b> 条笔记；下方会标明尚未写入本机存储的草稿。
       可导出为 Markdown 阅读，或用 JSON 备份／跨设备迁移。</p>
    ${storageOk ? "" : '<p style="color:#c9a227">本机存储当前不可用：以下内容来自本页内存，导出后请另存。</p>'}
    ${pending.length ? `<p style="color:#c9a227">其中 <b>${pending.length}</b> 条草稿尚未写入本机存储，导出会一并带走。</p>` : ""}
    ${qn ? `<p style="color:#c9a227">另有 <b>${qn}</b> 条本机旧记录无法读取，已原样保留，导出 JSON 时会一并备份。</p>` : ""}
    <div class="detail-section"><h4>最近笔记</h4><ul>
      ${recent.map(k => {
        const t = recordText(notes[k]);
        return `<li><b>${esc(noteLabel(k))}</b>${drafts[k] ? '<span style="color:#c9a227;font-size:10px"> · 未持久化</span>' : ""}
          <div style="font-size:11.5px;margin-top:3px">${esc(t.slice(0, 60))}${t.length > 60 ? "…" : ""}</div></li>`;
      }).join("") || '<li style="color:#5d6b7c">暂无</li>'}
    </ul></div>
    <div class="modal-actions">
      <button class="btn-gold" onclick="exportMarkdown()">导出 Markdown</button>
      <button class="btn-ghost" onclick="exportJSON()">导出 JSON 备份</button>
      <button class="btn-ghost" onclick="importJSON()">导入 JSON</button>
      <button class="btn-ghost" onclick="closeModal()">关闭</button>
    </div>
    <input type="file" id="jsonFileInput" accept=".json" style="display:none">
  `);
}

function exportMarkdown() {
  download("战争与和平-拆书笔记.md", notesToMarkdown(), "text/markdown;charset=utf-8");
}
function exportJSON() {
  download("战争与和平-笔记备份.json",
    JSON.stringify(buildExportPayload(), null, 2), "application/json");
}

/* ---------- 导入 JSON ---------- */
/* 整批先校验、再提交：任何一条不合法 → 整批拒绝，现有笔记一字不动。 */
function parseEnvelope(data) {
  if (!plainObject(data)) return { ok: false, why: "顶层不是 JSON 对象" };
  if (data.version !== undefined && data.version !== 1 && data.version !== NOTE_VERSION)
    return { ok: false, why: `不支持的备份版本 ${brief(data.version)}` };
  if (data.quarantine !== undefined &&
      (!Array.isArray(data.quarantine) || data.quarantine.length)) {
    return { ok: false, why: "备份含无法解析的旧记录，请保留原文件并先人工核对，避免静默丢弃" };
  }
  let map;
  if (data.notes !== undefined) {
    if (!plainObject(data.notes)) return { ok: false, why: "notes 字段不是普通对象" };
    map = data.notes;
  } else {                                          // 兼容直接给出记录表的旧文件
    map = Object.create(null);
    Object.keys(data).forEach(k => {
      if (k === "version" || k === "exportedAt" || k === "unpersisted" || k === "quarantine") return;
      map[k] = data[k];
    });
  }
  const records = [];
  const bad = [];
  Object.keys(map).forEach(key => {
    const chk = checkRecord(key, map[key]);
    if (chk.ok) records.push({ key: key, rec: chk.rec });
    else bad.push(chk.why);
  });
  if (bad.length) return { ok: false, why: `${bad.length} 条记录不合法：${bad.slice(0, 3).join("；")}` };
  if (!records.length) return { ok: false, why: "没有可导入的笔记" };
  return { ok: true, records: records };
}

/* 返回 { ok, imported, persisted, message }；ok 表示每条都已写入存储。 */
function importNotesData(data) {
  const parsed = parseEnvelope(data);
  if (!parsed.ok) return { ok: false, imported: 0, persisted: 0, message: `导入失败：${parsed.why}（现有笔记未改动）` };
  let persisted = 0;
  const failed = [];
  parsed.records.forEach(item => {
    notes[item.key] = item.rec;                     // 先合入内存，写失败也不丢
    if (persistRecord(item.key, item.rec)) { delete drafts[item.key]; persisted++; }
    else { drafts[item.key] = true; failed.push(item.key); }
  });
  if (failed.length)
    return {
      ok: false, imported: parsed.records.length, persisted: persisted,
      message: `已导入 ${parsed.records.length} 条，其中 ${persisted} 条写入本机存储，` +
        `${failed.length} 条写入失败（草稿保留在本页，可导出）：${failed.slice(0, 3).join("、")}`
    };
  return { ok: true, imported: persisted, persisted: persisted, message: `已导入 ${persisted} 条笔记。` };
}

function importJSON() {
  const input = document.getElementById("jsonFileInput");
  if (!input) return;
  input.onchange = () => {
    const f = input.files && input.files[0];
    if (!f) return;
    const r = new FileReader();
    r.onload = () => {
      let data;
      try { data = JSON.parse(String(r.result)); }
      catch (e) { alert("导入失败：文件不是有效的 JSON。（现有笔记未改动）"); return; }
      const res = importNotesData(data);
      alert(res.message);
      if (res.ok) closeModal();
    };
    r.onerror = () => alert("导入失败：无法读取文件。（现有笔记未改动）");
    r.readAsText(f);
  };
  input.click();
}
