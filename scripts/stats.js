#!/usr/bin/env node
/**
 * stats.js — 输出项目数据规模，供 README 校对。
 * 用法：node scripts/stats.js
 */
"use strict";
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..");
const FILES = ["structure", "places", "characters", "families", "relations",
  "themes", "arcs", "battles", "routes", "glossary", "names", "chapters", "events"];
const NAMES = ["STRUCTURE", "PLACES", "CHARACTERS", "FAMILIES", "RELATIONS",
  "THEMES", "ARCS", "BATTLES", "ROUTES", "GLOSSARY", "NAMES", "CHAPTERS", "EVENTS"];

const code = FILES.map(f => fs.readFileSync(path.join(ROOT, "data", f + ".js"), "utf8")).join("\n");
const out = {};
new Function("out", `"use strict";\n${code}\n${NAMES.map(n => `try{out.${n}=${n}}catch(e){}`).join("\n")}`)(out);

const mainParts = out.STRUCTURE.filter(b => !b.epilogue).reduce((a, b) => a + b.parts.length, 0);
const epiParts = out.STRUCTURE.filter(b => b.epilogue).reduce((a, b) => a + b.parts.length, 0);
const phases = out.RELATIONS.reduce((a, r) => a + (r.phases || []).length, 0);
const gists = out.CHAPTERS.filter(c => c.gist).length;
const withChars = out.CHAPTERS.filter(c => (c.chars || []).length).length;
const withYear = out.CHAPTERS.filter(c => c.year).length;
const minor = out.CHARACTERS.filter(c => c.tier === "minor").length;
const core = out.CHARACTERS.length - minor;

console.log("《战争与和平》拆书地图 · 数据规模");
console.log("─".repeat(40));
console.log(`卷部章        正文 4 卷 ${mainParts} 部 + 尾声 ${epiParts} 部 = ${mainParts + epiParts} 部 / ${out.CHAPTERS.length} 章`);
console.log(`章节卡        ${out.CHAPTERS.length}（gist ${gists}，含人物 ${withChars}，含年份 ${withYear}）`);
console.log(`事件卡        ${out.EVENTS.length}`);
console.log(`关系边        ${out.RELATIONS.length}（阶段总数 ${phases}）`);
console.log(`人物          ${out.CHARACTERS.length}（详录 ${core} / 简录 ${minor}）`);
console.log(`家族          ${out.FAMILIES.length}`);
console.log(`地点          ${Object.keys(out.PLACES).length}`);
console.log(`战役          ${out.BATTLES.length}`);
console.log(`路线          ${out.ROUTES.length}`);
console.log(`主题线        ${out.THEMES.length}`);
console.log(`人物弧光      ${out.ARCS.length}`);
console.log(`名物          ${out.GLOSSARY.length}`);
console.log(`译本对照      ${out.NAMES.length}`);
