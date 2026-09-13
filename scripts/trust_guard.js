#!/usr/bin/env node
/**
 * trust_guard.js — 双模式校验
 *
 *   corpus/ch/ 无文件 → 弱校验：实际执行 scripts/lint_data.js，并透传其退出状态
 *   corpus/ch/ 有文件 → 强校验（先执行 lint，再叠加语料内容核查）：
 *     0. 结构引用完整性：scripts/lint_data.js（章节/事件/战役/名物引用全量校验）
 *     1. 结构骨架：corpus 章数、章 id vs structure.js
 *     2. 章级称名核查：chapters.chars 的人物在正文里的**精确称名**
 *     3. 人物章节索引核对：characters.chapters 与正文精确称名比对
 *     4. 事件卡称名核查：events.chars 在覆盖章节中的精确称名
 *     5. 关系边共现核查：a/b 是否有精确称名的同章共现
 *
 * 结果分三类（见审核报告 F10 / F12）：
 *   ✗ 结构错误 —— 引用悬空、id 不存在、语料与骨架不符等；**非零退出**。
 *   ⚠ 待核     —— 精确称名之外的歧义 / 未证实；**仅供人工复核，不参与退出码**。
 *   ✓ 精确称名 —— 正文出现该人物的确切称名。这只表示「称名可见」，
 *                 既不证明其在场或身份，也**绝不等同**于泛称（伯爵/女儿/妹妹/
 *                 大尉）或他人姓名可以充作出场证据。宽匹配一律不计入通过判定。
 *
 * 退出码：0 = 通过（可能仍有待核项，不代表全部正确）；1 = 结构错误；
 *         语料缺失时透传 lint_data.js 的退出状态。
 *
 * 语料永不提交；本脚本的报告可入库。
 * 用法：node scripts/trust_guard.js
 */
"use strict";
const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const ROOT = path.join(__dirname, "..");
const CHDIR = path.join(ROOT, "corpus", "ch");

/* ---------- 载入数据 ---------- */
function sandbox() {
  const files = ["structure.js", "characters.js", "places.js", "relations.js",
    "chapters.js", "events.js", "themes.js", "arcs.js", "battles.js", "routes.js"];
  const code = files.filter(f => fs.existsSync(path.join(ROOT, "data", f)))
    .map(f => fs.readFileSync(path.join(ROOT, "data", f), "utf8")).join("\n");
  const out = {};
  new Function("out", `"use strict";\n${code}\n
    try{out.ALL_CHAPTERS=ALL_CHAPTERS}catch(e){}
    try{out.CHARACTERS=CHARACTERS}catch(e){}
    try{out.CHAPTERS=CHAPTERS}catch(e){}
    try{out.EVENTS=EVENTS}catch(e){}
    try{out.RELATIONS=RELATIONS}catch(e){}`)(out);
  return out;
}
const S = sandbox();
const { ALL_CHAPTERS = [], CHARACTERS = [], CHAPTERS = [], EVENTS = [], RELATIONS = [] } = S;

/* ---------- 是否具备强校验条件 ---------- */
const hasCorpus = fs.existsSync(CHDIR) &&
  fs.readdirSync(CHDIR).filter(f => f.endsWith(".txt")).length > 0;

console.log("《战争与和平》拆书地图 · trust_guard");
console.log(hasCorpus ? "模式：强校验（corpus/ch/ 有语料）" : "模式：弱校验（corpus/ch/ 无文件）");
console.log("");

/* ---------- 0. 结构引用完整性（两种模式都执行） ---------- */
function runLint() {
  console.log("[0] 结构引用完整性（scripts/lint_data.js）");
  const r = spawnSync(process.execPath, [path.join(__dirname, "lint_data.js")], { stdio: "inherit" });
  if (r.error) {
    console.error("无法执行 lint_data.js：" + r.error.message);
    return 1;
  }
  return r.status === 0 ? 0 : 1;
}
const lintStatus = runLint();
console.log("");

if (!hasCorpus) {
  console.log("语料缺失（corpus/ch/ 为空）：弱校验到此为止，已执行结构校验。");
  console.log("如需内容强校验，请先运行：python3 scripts/corpus_extract.py");
  console.log(`退出状态透传自 lint_data.js：${lintStatus}`);
  process.exit(lintStatus);
}

/* ---------- 读语料 ---------- */
const corpus = {};
fs.readdirSync(CHDIR).filter(f => f.endsWith(".txt")).forEach(f => {
  corpus[f.replace(/\.txt$/, "")] = fs.readFileSync(path.join(CHDIR, f), "utf8");
});
const corpusIds = Object.keys(corpus).sort();
console.log(`语料：${corpusIds.length} 章\n`);

const problems = [];
const notes = [];
const ok = m => console.log("  ✓ " + m);
const bad = m => { problems.push(m); console.log("  ✗ " + m); };
const note = m => { notes.push(m); console.log("  ⚠ " + m); };
const sample = arr => arr.slice(0, 12).join("，") + (arr.length > 12 ? " …" : "");

/* ---------- 称名表：只认数据里登记的准确称名 ---------- */
const aliasOwners = new Map();
const NAME_PAT = {};
CHARACTERS.forEach(c => {
  const forms = new Set([c.name, c.full, c.name.replace(/[（(].*$/, "").trim(), ...(c.aliases || [])]
    .filter(a => typeof a === "string" && a.length >= 2));
  NAME_PAT[c.id] = forms;
  forms.forEach(a => {
    if (!aliasOwners.has(a)) aliasOwners.set(a, new Set());
    aliasOwners.get(a).add(c.id);
  });
});

// 泛称（爵位 / 军衔 / 亲属称谓）：**只用于把「未命中」标成歧义待核**，
// 绝不作为任何人物的出场证据 —— 见审核报告 F10。
// 姓名与别名一律以 data/characters.js 的登记为准，此处不再维护第二份映射。
const GENERIC = /(伯爵夫人|公爵夫人|公爵小姐|老公爵夫人|老公爵|伯爵|公爵|男爵|大尉|中尉|上尉|少校|上校|将军|元帅|皇帝|皇后|陛下|殿下|亲王|公主|女儿|儿子|妹妹|姐姐|哥哥|弟弟|母亲|父亲|妻子|丈夫|夫人|老爷|少爷|小姐|侄儿|侄女|表姐|表妹|使女|侍女|女伴|家庭教师)/;
const genericName = new RegExp("^(?:老|小)?" + GENERIC.source + "$");
const nameMatcher = new RegExp([...aliasOwners.keys()].sort((a, b) => b.length - a.length)
  .map(a => a.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|"), "g");
const mentions = new Map();
function namedPeople(text) {
  if (mentions.has(text)) return mentions.get(text);
  const ids = new Set();
  // 最长称名先匹配，避免把「罗斯托夫伯爵夫人」里的前缀认作伯爵本人。
  for (const match of text.matchAll(nameMatcher)) {
    const owners = aliasOwners.get(match[0]);
    if (owners.size === 1 && !genericName.test(match[0])) ids.add(owners.values().next().value);
  }
  mentions.set(text, ids);
  return ids;
}

// named = 精确称名；ambiguous = 只有泛称、无法绑定；unverified = 毫无痕迹；
// structural = 人物 id 不在 characters.js（硬错误）。
const classify = (cid, text) => {
  if (!NAME_PAT[cid]) return "structural";
  if (namedPeople(text).has(cid)) return "named";
  if (GENERIC.test(text)) return "ambiguous";
  return "unverified";
};

/* ---------- 1. 结构骨架 ---------- */
console.log("[1] 结构骨架");
const structIds = ALL_CHAPTERS.map(c => c.id).sort();
if (structIds.length !== corpusIds.length) {
  bad(`structure ${structIds.length} 章 vs corpus ${corpusIds.length} 章`);
} else {
  const diff = structIds.filter((id, i) => id !== corpusIds[i]);
  if (diff.length) bad(`章 id 不一致：${diff.slice(0, 8).join(",")}`);
  else ok(`${structIds.length} 章 id 逐一对应`);
}

/* ---------- 2. 章级称名核查 ---------- */
console.log("\n[2] 章级称名核查（chapters.chars → 正文精确称名）");
let namedGroups = 0, emptyChapter = 0;
const ambiguous = [], unverified = [];
CHAPTERS.forEach(ch => {
  const text = corpus[ch.id];
  if (!text) return;
  (ch.chars || []).forEach(cid => {
    const kind = classify(cid, text);
    if (kind === "structural") { bad(`${ch.id}: 人物 ${cid} 不在 characters.js`); return; }
    if (kind === "named") { namedGroups++; return; }
    (kind === "ambiguous" ? ambiguous : unverified).push(`${ch.id}·${cid}`);
  });
  if (!(ch.chars || []).length) emptyChapter++;
});
ok(`精确称名命中 ${namedGroups} 组（称名可见 ≠ 在场，更非身份确证）`);
if (ambiguous.length)
  note(`歧义待核 ${ambiguous.length} 组：正文只有泛称，无法绑定本角色 → ${sample(ambiguous)}`);
if (unverified.length)
  note(`未证实待核 ${unverified.length} 组：正文未见本角色任何称名 → ${sample(unverified)}`);
if (emptyChapter) note(`${emptyChapter} 张章节卡无 chars（议论/过场章属正常）`);

/* ---------- 3. 人物章节索引核对 ---------- */
console.log("\n[3] 人物章节索引核对（characters.chapters vs 正文精确称名）");
let idxChecked = 0, idxGap = 0, idxMissed = 0;
const gapChars = [], missedChars = [];
CHARACTERS.forEach(c => {
  const named = new Set(corpusIds.filter(id => classify(c.id, corpus[id]) === "named"));
  const claimed = c.chapters || [];
  idxChecked += claimed.length;
  const gap = claimed.filter(id => !named.has(id)).length;          // 声称出现但正文无精确称名
  const missed = [...named].filter(id => claimed.indexOf(id) < 0).length; // 有精确称名却未入索引
  idxGap += gap; idxMissed += missed;
  if (gap) gapChars.push(`${c.id}(${gap}/${claimed.length})`);
  if (missed > 3) missedChars.push(`${c.id}(+${missed})`);
});
ok(`共核对 ${idxChecked} 条索引`);
if (gapChars.length)
  note(`索引章节正文无精确称名 ${idxGap} 条（待核，不等于缺席）→ ${sample(gapChars)}`);
if (missedChars.length)
  note(`正文有精确称名但未入索引 >3 章的人物 ${missedChars.length} 位（待核）→ ${sample(missedChars)}`);

/* ---------- 4. 事件卡称名核查 ---------- */
console.log("\n[4] 事件卡称名核查（events.chars → 覆盖章节正文精确称名）");
let evNamed = 0;
const evPending = [];
EVENTS.forEach(e => {
  const chs = (e.ch || []).filter(id => corpus[id]);
  if (!chs.length) return;
  const joined = chs.map(id => corpus[id]).join("\n");
  (e.chars || []).forEach(cid => {
    const kind = classify(cid, joined);
    if (kind === "structural") { bad(`${e.id}: 人物 ${cid} 不在 characters.js`); return; }
    if (kind === "named") { evNamed++; return; }
    evPending.push(`${e.id}·${cid}`);
  });
});
ok(`事件人物精确称名命中 ${evNamed} 组`);
if (evPending.length) note(`事件人物歧义/未证实 ${evPending.length} 组（待核）→ ${sample(evPending)}`);

/* ---------- 5. 关系边共现核查 ---------- */
console.log("\n[5] 关系边共现核查（a、b 精确称名同章共现）");
const relPending = [];
RELATIONS.forEach(r => {
  if (!NAME_PAT[r.a] || !NAME_PAT[r.b]) {
    bad(`关系 ${r.id}: 人物 ${!NAME_PAT[r.a] ? r.a : r.b} 不在 characters.js`);
    return;
  }
  const co = corpusIds.some(id => {
    const t = corpus[id];
    return classify(r.a, t) === "named" && classify(r.b, t) === "named";
  });
  if (!co) relPending.push(r.id);
});
ok(`共核查 ${RELATIONS.length} 条关系边`);
if (relPending.length)
  note(`无精确称名同章共现的关系边 ${relPending.length} 条（待核，不等于无关系）→ ${sample(relPending)}`);

/* ---------- 汇总 ---------- */
console.log("\n" + "─".repeat(52));
if (problems.length || lintStatus !== 0) {
  console.log(`✗ 强校验未通过：结构错误 ${problems.length} 个（lint 状态 ${lintStatus}），待核 ${notes.length} 条`);
  process.exit(1);
} else {
  console.log(`✓ 强校验：无结构错误；${notes.length} 条待核项需人工复核（不构成「全部正确」证明）`);
}
