#!/usr/bin/env node
/**
 * lint_data.js — 《战争与和平》拆书地图数据体检
 *
 * 检查：结构调整、引用完整性（含 relations.phases[].ev、events.battle、事件日期）、
 *       受控词表、版权门禁、别名查重、关系约束、章节覆盖、时间一致性；
 *       汇总 flag:"verify" 清单。未知/缺失引用一律记为硬错误并非零退出。
 *
 * 用法：node scripts/lint_data.js
 */
"use strict";
const fs = require("fs");
const path = require("path");
const LIMITS = require("./data_limits.js");

const ROOT = path.join(__dirname, "..");
const DATA = path.join(ROOT, "data");

const problems = [];
const warns = [];
const ok = m => console.log("  \u2713 " + m);
const bad = m => { problems.push(m); console.log("  \u2717 " + m); };
const note = m => { warns.push(m); console.log("  \u26a0 " + m); };

/* ---------- 载入 ---------- */
function loadSandbox() {
  const files = ["structure.js", "characters.js", "places.js", "relations.js",
    "chapters.js", "events.js", "families.js", "themes.js", "arcs.js",
    "battles.js", "routes.js", "glossary.js", "names.js"];
  const present = files.filter(f => fs.existsSync(path.join(DATA, f)));
  const code = present.map(f => fs.readFileSync(path.join(DATA, f), "utf8")).join("\n");
  const exportNames = ["STRUCTURE", "PART_TITLES", "ALL_CHAPTERS", "TOTAL_CHAPTERS",
    "CHARACTERS", "PLACES", "RELATIONS", "CHAPTERS", "EVENTS", "FAMILIES",
    "THEMES", "ARCS", "BATTLES", "ROUTES", "GLOSSARY", "NAMES"];
  const decl = exportNames.map(n => `try{ out.${n}=${n}; }catch(e){}`).join("\n");
  const out = {};
  new Function("out", `"use strict";\n${code}\n${decl}`)(out);
  out.__present = present;
  return out;
}

const S = loadSandbox();
const {
  ALL_CHAPTERS = [], TOTAL_CHAPTERS = 0,
  CHARACTERS = [], PLACES = {}, RELATIONS = [], CHAPTERS = [],
  EVENTS = [], FAMILIES = [], THEMES = [], ARCS = [], BATTLES = [],
  ROUTES = [], GLOSSARY = [], NAMES = [],
} = S;

/* ---------- 引用全集（跨表校验用） ---------- */
const evIds = new Set(EVENTS.map(e => e.id));
const battleIds = new Set(BATTLES.map(b => b.id));

/* ---------- 受控词表 ---------- */
const V = {
  chapterTag: ["peace", "war", "essay", "transition"],
  eventType: ["salon", "family", "ball", "hunt", "battle", "march", "wound", "duel",
    "business", "intrigue", "spirit", "essay"],
  faction: ["bezukhov", "rostov", "bolkonsky", "kuragin", "druzh", "russian_army",
    "french_army", "court", "mason", "folk"],
  relKind: ["kin", "marriage", "courtship", "affair", "friend", "salon",
    "enemy", "service", "patron", "estate"],
  tier: ["core", "minor"],
  phasePrefix: ["初见", "疏远", "靠近", "求婚", "订婚", "受阻", "悔婚", "决裂",
    "和解", "结婚", "丧偶", "死别", "反目", "互助"],
  placeKind: ["estate", "city", "battlefield", "other"],
  themeRole: ["提出", "推进", "解答"],
  themeStatus: ["open", "partial", "answered"],
  glossKind: ["rank", "title", "term", "order"],
};

console.log("《战争与和平》拆书地图 数据体检");
console.log(`  已载入数据文件 ${S.__present.length} 个：${S.__present.join(" ")}\n`);

/* ---------- 工具 ---------- */
const quoteSpan = s => {
  if (typeof s !== "string") return 0;
  let mx = 0;
  for (const m of s.matchAll(/[「“"『]([^」”"』]{1,200})[」”"』]/g)) {
    mx = Math.max(mx, m[1].length);
  }
  return mx;
};
const len = s => (typeof s === "string" ? [...s].length : 0);

/* ---------- 1. 结构 ---------- */
console.log("[结构 structure.js]");
if (TOTAL_CHAPTERS !== 361) bad(`总章数 ${TOTAL_CHAPTERS} != 361`);
else ok(`17 部 ${TOTAL_CHAPTERS} 章`);
const partKeys = new Set(ALL_CHAPTERS.map(c => `${c.book}-${c.part}`));
if (partKeys.size !== 17) bad(`部数 ${partKeys.size} != 17`);
else ok(`部数 17`);
const chIdSet = new Set(ALL_CHAPTERS.map(c => c.id));

/* ---------- 2. 人物 ---------- */
console.log("\n[人物 characters.js]");
const charIds = new Set();
const aliasOwner = new Map();
CHARACTERS.forEach(c => {
  if (charIds.has(c.id)) bad(`人物 id 重复：${c.id}`);
  charIds.add(c.id);
  if (!V.faction.includes(c.faction)) bad(`${c.id}: faction 越界 "${c.faction}"`);
  if (!V.tier.includes(c.tier)) bad(`${c.id}: tier 越界 "${c.tier}"`);
  [c.name, ...(c.aliases || [])].forEach(a => {
    if (aliasOwner.has(a) && aliasOwner.get(a) !== c.id)
      bad(`别名重复：「${a}」同时属于 ${aliasOwner.get(a)} 与 ${c.id}`);
    aliasOwner.set(a, c.id);
  });
  if (len(c.bio) > LIMITS.bio) bad(`${c.id}: bio ${len(c.bio)} > ${LIMITS.bio}`);
  if (c.tier === "core" && !c.bio) bad(`${c.id}: 详录人物缺 bio`);
  if (quoteSpan(c.bio) > LIMITS.quoteSpan) bad(`${c.id}: bio 含过长引文`);
  (c.chapters || []).forEach(id => { if (!chIdSet.has(id)) bad(`${c.id}: 章节 ${id} 不存在`); });
  if (c.family && FAMILIES.length && !FAMILIES.some(f => f.id === c.family))
    bad(`${c.id}: family "${c.family}" 不存在`);
});
const core = CHARACTERS.filter(c => c.tier === "core").length;
ok(`${CHARACTERS.length} 位人物（详录 ${core} / 简录 ${CHARACTERS.length - core}）`);

/* ---------- 3. 地点 ---------- */
console.log("\n[地点 places.js]");
const placeKeys = new Set(Object.keys(PLACES));
Object.entries(PLACES).forEach(([k, p]) => {
  if (typeof p.lat !== "number" || typeof p.lng !== "number") bad(`地点 ${k}: 缺坐标`);
  if (p.lat < -90 || p.lat > 90) bad(`地点 ${k}: lat 越界`);
  if (p.kind && !V.placeKind.includes(p.kind)) bad(`地点 ${k}: kind 越界 "${p.kind}"`);
});
ok(`${placeKeys.size} 处地点`);

/* ---------- 4. 关系 ---------- */
console.log("\n[关系 relations.js]");
const relPairs = new Set();
RELATIONS.forEach(r => {
  if (r.a === r.b) bad(`关系 ${r.id}: a == b`);
  if (!charIds.has(r.a)) bad(`关系 ${r.id}: a "${r.a}" 不存在`);
  if (!charIds.has(r.b)) bad(`关系 ${r.id}: b "${r.b}" 不存在`);
  const key = [r.a, r.b].sort().join("|");
  if (relPairs.has(key)) bad(`关系对重复：${key}`);
  relPairs.add(key);
  if (!V.relKind.includes(r.kind)) bad(`关系 ${r.id}: kind 越界 "${r.kind}"`);
  if (!(r.weight >= 1 && r.weight <= 5)) bad(`关系 ${r.id}: weight ${r.weight} 越界`);
  let prev = -Infinity;
  (r.phases || []).forEach((p, i) => {
    if (p.y < prev) bad(`关系 ${r.id}: phases[${i}] 年份未升序`);
    prev = p.y;
    if (r.from && p.y < r.from.y)
      bad(`关系 ${r.id}: phases[${i}] 年份 ${p.y} 早于 from ${r.from.y}`);
    if (r.to && p.y > r.to.y)
      bad(`关系 ${r.id}: phases[${i}] 年份 ${p.y} 晚于 to ${r.to.y}`);
    const pre = String(p.state || "").split("·")[0];
    if (pre && !V.phasePrefix.includes(pre))
      note(`关系 ${r.id}: phases[${i}] 状态前缀「${pre}」不在受控表`);
    if (p.ev != null && (typeof p.ev !== "string" || !evIds.has(p.ev)))
      bad(`关系 ${r.id}: phases[${i}] ev "${p.ev}" 不存在于 events.js`);
  });
});
ok(`${RELATIONS.length} 条关系边`);

/* ---------- 5. 章节卡 ---------- */
console.log("\n[章节卡 chapters.js]");
const chIds = new Set();
let withChars = 0, withYear = 0;
CHAPTERS.forEach(c => {
  if (chIds.has(c.id)) bad(`章节卡 id 重复：${c.id}`);
  chIds.add(c.id);
  if (!chIdSet.has(c.id)) bad(`章节卡 ${c.id}: 不在 structure 中`);
  if (c.tag && !V.chapterTag.includes(c.tag)) bad(`${c.id}: tag 越界 "${c.tag}"`);
  if (len(c.gist) > LIMITS.gist) bad(`${c.id}: gist ${len(c.gist)} > ${LIMITS.gist}`);
  if (quoteSpan(c.gist) > LIMITS.quoteSpan) bad(`${c.id}: gist 含过长引文`);
  if (c.place && !placeKeys.has(c.place)) bad(`${c.id}: place "${c.place}" 不存在`);
  (c.chars || []).forEach(x => { if (!charIds.has(x)) bad(`${c.id}: char "${x}" 不存在`); });
  if (c.chars && c.chars.length) withChars++;
  if (c.year) withYear++;
});
if (CHAPTERS.length) {
  ok(`${CHAPTERS.length} 张章节卡（${withChars} 张含人物、${withYear} 张含年份）`);
  const missing = [...chIdSet].filter(id => !chIds.has(id));
  if (missing.length) bad(`章节卡未覆盖 ${missing.length} 章：${missing.slice(0, 12).join(",")}${missing.length > 12 ? "…" : ""}`);
  else ok(`361 章全覆盖`);
} else {
  note("chapters.js 为空（Phase 1 前正常）");
}

/* ---------- 6. 事件卡 ---------- */
console.log("\n[事件卡 events.js]");
const seenEv = new Set();
const themeIds = new Set(THEMES.map(t => t.id));
const arcStages = new Map(ARCS.map(a => [a.who, new Set((a.stages || []).map(s => s.label))]));
EVENTS.forEach(e => {
  if (seenEv.has(e.id)) bad(`事件 id 重复：${e.id}`);
  seenEv.add(e.id);
  if (!V.eventType.includes(e.type)) bad(`${e.id}: type 越界 "${e.type}"`);
  if (e.battle != null && !battleIds.has(e.battle))
    bad(`${e.id}: battle "${e.battle}" 不存在于 battles.js`);
  if (e.month != null && (!Number.isInteger(e.month) || e.month < 1 || e.month > 12))
    bad(`${e.id}: month ${e.month} 越界`);
  if (e.day != null) {
    if (!Number.isInteger(e.day) || e.day < 1) bad(`${e.id}: day ${e.day} 非法`);
    else if (!e.month) bad(`${e.id}: day ${e.day} 缺 month`);
    else {
      const dim = new Date(Date.UTC(e.year || 2000, e.month, 0)).getUTCDate();
      if (e.day > dim) bad(`${e.id}: day ${e.day} 超出 ${e.year || "?"} 年 ${e.month} 月的 ${dim} 天`);
    }
  }
  if (len(e.summary) > LIMITS.summary) bad(`${e.id}: summary ${len(e.summary)} > ${LIMITS.summary}`);
  if (e.history && len(e.history) > LIMITS.history) bad(`${e.id}: history 超长`);
  if (quoteSpan(e.summary) > LIMITS.quoteSpan) bad(`${e.id}: summary 含过长引文`);
  if (e.place && !placeKeys.has(e.place)) bad(`${e.id}: place "${e.place}" 不存在`);
  (e.ch || []).forEach(id => { if (!chIdSet.has(id)) bad(`${e.id}: ch "${id}" 不存在`); });
  (e.chars || []).forEach(x => { if (!charIds.has(x)) bad(`${e.id}: char "${x}" 不存在`); });
  (e.factions || []).forEach(f => { if (!V.faction.includes(f)) bad(`${e.id}: faction 越界 "${f}"`); });
  (e.theme || []).forEach(t => {
    if (THEMES.length && !themeIds.has(t)) bad(`${e.id}: theme "${t}" 不存在`);
  });
  (e.rel || []).forEach((r, i) => {
    if (!charIds.has(r.a) || !charIds.has(r.b)) bad(`${e.id}: rel[${i}] 人物不存在`);
    if (!V.relKind.includes(r.kind)) bad(`${e.id}: rel[${i}] kind 越界 "${r.kind}"`);
  });
  (e.arc || []).forEach((a, i) => {
    if (!charIds.has(a.who)) bad(`${e.id}: arc[${i}] 人物 "${a.who}" 不存在`);
    const st = arcStages.get(a.who);
    if (st && !st.has(a.stage)) bad(`${e.id}: arc[${i}] 阶段「${a.stage}」不在 ${a.who} 的弧光中`);
  });
});
if (EVENTS.length) ok(`${EVENTS.length} 张事件卡`);
else note("events.js 为空（Phase 1 前正常）");

/* ---------- 7. 主题 / 弧光 / 战役 / 名物 ---------- */
console.log("\n[主题 / 弧光 / 战役 / 名物]");
THEMES.forEach(t => {
  if (!V.themeStatus.includes(t.status)) bad(`主题 ${t.id}: status 越界 "${t.status}"`);
  (t.nodes || []).forEach((n, i) => {
    if (!chIdSet.has(n.ch)) bad(`主题 ${t.id}: nodes[${i}] 章节 "${n.ch}" 不存在`);
    if (!V.themeRole.includes(n.role)) bad(`主题 ${t.id}: nodes[${i}] role 越界 "${n.role}"`);
  });
});
ARCS.forEach(a => {
  if (!charIds.has(a.who)) bad(`弧光 ${a.id}: 人物 "${a.who}" 不存在`);
  (a.stages || []).forEach((s, i) => {
    (s.ch || []).forEach(id => { if (!chIdSet.has(id)) bad(`弧光 ${a.id}: stages[${i}] 章节 "${id}" 不存在`); });
  });
});
BATTLES.forEach(b => {
  if (b.place && !placeKeys.has(b.place)) bad(`战役 ${b.id}: place "${b.place}" 不存在`);
  (b.chars || []).forEach(x => { if (!charIds.has(x)) bad(`战役 ${b.id}: char "${x}" 不存在`); });
});
ROUTES.forEach(r => {
  if (!["march", "retreat", "person"].includes(r.kind)) bad(`路线 ${r.id}: kind 越界 "${r.kind}"`);
  if (r.who && !charIds.has(r.who)) bad(`路线 ${r.id}: who "${r.who}" 不存在`);
  (r.pts || []).forEach((p, i) => { if (!placeKeys.has(p.p)) bad(`路线 ${r.id}: pts[${i}] 地点 "${p.p}" 不存在`); });
});
GLOSSARY.forEach(g => {
  if (!V.glossKind.includes(g.kind)) bad(`名物 ${g.id}: kind 越界 "${g.kind}"`);
  if (len(g.desc) > LIMITS.desc) bad(`名物 ${g.id}: desc 超长`);
  (g.events || []).forEach(id => { if (!evIds.has(id)) bad(`名物 ${g.id}: 事件 "${id}" 不存在`); });
});
ok(`主题 ${THEMES.length} / 弧光 ${ARCS.length} / 战役 ${BATTLES.length} / 路线 ${ROUTES.length} / 名物 ${GLOSSARY.length}`);

/* ---------- 8. 人名对照 ---------- */
console.log("\n[人名对照 names.js]");
NAMES.forEach(n => {
  if (!n.cao) bad(`names ${n.id}: 缺草婴译名（基准）`);
  if (!charIds.has(n.id)) bad(`names ${n.id}: 人物不存在`);
});
if (NAMES.length) ok(`${NAMES.length} 条译本对照`);

/* ---------- 9. 版权门禁 ---------- */
console.log("\n[版权门禁]");
let violations = 0;
const scanQuoteField = (obj, where) => {
  if (obj && Object.prototype.hasOwnProperty.call(obj, "quote")) {
    bad(`${where}: 出现被禁的 quote 字段`); violations++;
  }
};
[...CHARACTERS, ...CHAPTERS, ...EVENTS, ...THEMES, ...ARCS, ...BATTLES, ...GLOSSARY, ...NAMES]
  .forEach((o, i) => scanQuoteField(o, `记录#${i}`));
if (!violations) ok("无 quote 字段、无超长引文");

/* ---------- 10. verify 汇总 ---------- */
console.log("\n[flag:verify 清单]");
const verify = [];
const FLAG_LABEL = { verify: "待核", mentioned: "仅被提及（未正面出场）", indexPend: "索引待扩" };
ALL_CHAPTERS.filter(c => c.flag).forEach(c => verify.push(`结构 ${c.id} (${c.flag})`));
[...CHARACTERS, ...CHAPTERS, ...EVENTS, ...THEMES, ...ARCS, ...NAMES]
  .filter(o => o.flag).forEach(o =>
    verify.push(`${o.id} [${FLAG_LABEL[o.flag] || o.flag}] ${o.note || ""}`.trim()));
if (verify.length) verify.forEach(v => console.log("  • " + v));
else ok("无待核条目");

/* ---------- 汇总 ---------- */
console.log("\n" + "─".repeat(48));
if (problems.length) {
  console.log(`✗ 体检未通过：${problems.length} 个错误，${warns.length} 个提醒`);
  process.exit(1);
} else {
  console.log(`✓ 体检通过（${warns.length} 个提醒）`);
}
