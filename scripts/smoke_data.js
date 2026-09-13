#!/usr/bin/env node
/**
 * smoke_data.js — 数据装载冒烟测试
 * 在 Node 里按 index.html 的顺序装载全部 data/*.js，检查全局符号与关键计数。
 * 用法：node scripts/smoke_data.js
 */
"use strict";
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..");
const ORDER = ["structure", "places", "characters", "families", "relations",
  "themes", "arcs", "battles", "routes", "glossary", "names", "chapters", "events"];

const code = ORDER.map(f => fs.readFileSync(path.join(ROOT, "data", f + ".js"), "utf8")).join("\n");
const names = ["STRUCTURE", "ALL_CHAPTERS", "TOTAL_CHAPTERS", "PART_TITLES", "PLACES",
  "CHARACTERS", "FAMILIES", "RELATIONS", "THEMES", "ARCS", "BATTLES", "ROUTES",
  "GLOSSARY", "NAMES", "CHAPTERS", "EVENTS"];

const out = {};
const decl = names.map(n => `try{ out[${JSON.stringify(n)}]=${n}; }catch(e){}`).join("\n");
new Function("out", `"use strict";\n${code}\n${decl}`)(out);

const expect = {
  TOTAL_CHAPTERS: 361, PLACES: null, CHARACTERS: null, RELATIONS: null,
  CHAPTERS: 361, EVENTS: null, THEMES: 6, ARCS: 8, BATTLES: 5, ROUTES: 7,
  GLOSSARY: null, FAMILIES: 5, STRUCTURE: 5,
};
let fail = 0;
const line = (k, v, want) => {
  const got = Array.isArray(v) ? v.length : (v && typeof v === "object" ? Object.keys(v).length : v);
  const ok = want === null || got === want;
  if (!ok) fail++;
  console.log(`  ${ok ? "✓" : "✗"} ${k.padEnd(16)} ${got}${want !== null ? " (期望 " + want + ")" : ""}`);
};
console.log("数据装载冒烟测试\n");
Object.keys(expect).forEach(k => line(k, out[k], expect[k]));

// 关键交叉引用抽查
const chIds = new Set((out.CHAPTERS || []).map(c => c.id));
const charIds = new Set((out.CHARACTERS || []).map(c => c.id));
const placeKeys = new Set(Object.keys(out.PLACES || {}));
const evIds = new Set((out.EVENTS || []).map(e => e.id));
const battleIds = new Set((out.BATTLES || []).map(b => b.id));
let xref = 0;
(out.RELATIONS || []).forEach(r => {
  if (!charIds.has(r.a) || !charIds.has(r.b)) { console.log(`  ✗ 关系 ${r.id} 人物缺失`); xref++; }
  (r.phases || []).forEach((p, i) => {
    if (p.ev != null && !evIds.has(p.ev)) { console.log(`  ✗ 关系 ${r.id} phases[${i}] 事件 ${p.ev} 缺失`); xref++; }
  });
});
(out.EVENTS || []).forEach(e => {
  (e.ch || []).forEach(id => { if (!chIds.has(id)) { console.log(`  ✗ 事件 ${e.id} 章节 ${id} 缺失`); xref++; } });
  if (e.place && !placeKeys.has(e.place)) { console.log(`  ✗ 事件 ${e.id} 地点 ${e.place} 缺失`); xref++; }
  if (e.battle != null && !battleIds.has(e.battle)) { console.log(`  ✗ 事件 ${e.id} 战役 ${e.battle} 缺失`); xref++; }
  if (e.day != null && !Number.isInteger(e.day)) { console.log(`  ✗ 事件 ${e.id} day 非法`); xref++; }
});
(out.GLOSSARY || []).forEach(g => {
  (g.events || []).forEach(id => { if (!evIds.has(id)) { console.log(`  ✗ 名物 ${g.id} 事件 ${id} 缺失`); xref++; } });
});
if (!xref) console.log("  ✓ 交叉引用抽查通过");
else fail += xref;

const gists = (out.CHAPTERS || []).filter(c => c.gist).length;
console.log(`  · 章节卡 gist 覆盖 ${gists}/${out.CHAPTERS.length}`);

console.log("\n" + (fail ? `✗ ${fail} 个问题` : "✓ 冒烟测试通过"));
process.exit(fail ? 1 : 0);
