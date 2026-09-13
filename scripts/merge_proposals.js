#!/usr/bin/env node
/**
 * merge_proposals.js — 把 data/proposals/notes_*.py 的章节卡提案合并进 data/chapters.js
 *
 * 增量、幂等：已入库的 gist 不覆盖，只补缺失。
 * 事件关联不在章节卡上维护：唯一关联源是 data/events.js 的 EVENTS[].ch；
 * 本脚本不写、也不接受遗留的 chapters[].event 字段。
 * 写盘用临时文件 + rename，避免半写入。
 * 用法：
 *   node scripts/merge_proposals.js --dry     # 只校验不改文件
 *   node scripts/merge_proposals.js           # 落盘
 */
"use strict";
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const LIMITS = require("./data_limits.js");

const ROOT = path.join(__dirname, "..");
const PROPOSALS = path.join(ROOT, "data", "proposals");
const CHAPTERS_JS = path.join(ROOT, "data", "chapters.js");
const DRY = process.argv.includes("--dry");

// 章卡字段契约（不含已删除的 event）
const CHAPTER_FIELDS = ["id", "book", "part", "ch", "seq", "year", "month",
  "tag", "place", "chars", "gist", "flag"];
const VALID_TAG = ["peace", "war", "essay", "transition"];

/* ---------- 载入提案（用 python3 解析 .py） ---------- */
function loadProposal(file) {
  const out = execFileSync("python3", ["-c", `
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location("p", sys.argv[1])
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
print(json.dumps(m.NOTES, ensure_ascii=False))
`, file], { encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });
  return JSON.parse(out);
}

/* ---------- 载入现有 chapters.js ---------- */
function loadChapters() {
  const code = fs.readFileSync(CHAPTERS_JS, "utf8");
  const out = {};
  new Function("out", `"use strict";\n${code}\n try{ out.CHAPTERS=CHAPTERS; }catch(e){}`)(out);
  return out.CHAPTERS || [];
}

function main() {
  if (!fs.existsSync(PROPOSALS)) { console.log("无 proposals 目录"); return; }

  const files = fs.readdirSync(PROPOSALS).filter(f => f.startsWith("notes_") && f.endsWith(".py")).sort();
  if (!files.length) { console.log("无提案文件"); return; }

  const chapters = loadChapters();
  const byId = new Map(chapters.map(c => [c.id, c]));
  const charIds = new Set();
  const places = new Set();
  {
    const out = {};
    const code = ["characters.js", "places.js"]
      .map(f => fs.readFileSync(path.join(ROOT, "data", f), "utf8")).join("\n");
    new Function("out", `"use strict";\n${code}\n try{ out.C=CHARACTERS; out.P=PLACES; }catch(e){}`)(out);
    (out.C || []).forEach(c => charIds.add(c.id));
    Object.keys(out.P || {}).forEach(k => places.add(k));
  }

  const problems = [];
  let merged = 0, skipped = 0;
  const seen = new Set();

  files.forEach(f => {
    let props;
    try { props = loadProposal(path.join(PROPOSALS, f)); }
    catch (e) { problems.push(`${f}: 解析失败 — ${e.message.split("\n")[0]}`); return; }

    Object.entries(props).forEach(([id, v]) => {
      if (seen.has(id)) problems.push(`${f}: ${id} 在多个提案中重复`);
      seen.add(id);

      const target = byId.get(id);
      if (!target) { problems.push(`${f}: ${id} 不在 structure 中`); return; }

      if (Object.prototype.hasOwnProperty.call(v, "event"))
        problems.push(`${f}: ${id} 带遗留字段 event（章节事件关联唯一来源是 EVENTS[].ch，本脚本不接受）`);
      if (target.event != null)
        problems.push(`${f}: ${id} 目标章卡仍带遗留字段 event（请先在 data/chapters.js 中删除）`);

      const g = v.gist;
      if (!g) { problems.push(`${f}: ${id} 缺 gist`); return; }
      const glen = [...g].length;
      if (glen > LIMITS.gist) problems.push(`${f}: ${id} gist ${glen} 字 > ${LIMITS.gist}`);
      for (const m of g.matchAll(/[「“"『]([^」”"』]{1,200})[」”"』]/g)) {
        if (m[1].length > LIMITS.quoteSpan) problems.push(`${f}: ${id} gist 含 >${LIMITS.quoteSpan} 字引文`);
      }
      if (v.tag && !VALID_TAG.includes(v.tag)) problems.push(`${f}: ${id} tag 越界 "${v.tag}"`);
      (v.chars || []).forEach(c => {
        if (!charIds.has(c)) problems.push(`${f}: ${id} char "${c}" 不在人物表`);
      });
      if (v.place && !places.has(v.place)) problems.push(`${f}: ${id} place "${v.place}" 不在地点表`);

      // 增量：已有 gist 则跳过
      if (target.gist) { skipped++; return; }

      if (!DRY) {
        target.gist = g;
        if (v.tag) target.tag = v.tag;
        if (v.place) target.place = v.place;
        if (v.chars && v.chars.length) target.chars = v.chars;
        if (v.year != null) target.year = v.year;
        if (v.month != null) target.month = v.month;
        target.flag = null;
      }
      merged++;
    });
  });

  const total = chapters.length;
  const have = chapters.filter(c => c.gist).length;

  console.log(`提案文件 ${files.length} 个，条目 ${seen.size} 条`);
  console.log(`  合并 ${merged} 条 / 跳过（已有 gist）${skipped} 条`);
  console.log(`  章节卡 gist 覆盖：${DRY ? (have + merged) : have} / ${total}`);

  if (problems.length) {
    console.log(`\n✗ ${problems.length} 个问题：`);
    problems.slice(0, 40).forEach(p => console.log("  " + p));
    if (problems.length > 40) console.log(`  …另有 ${problems.length - 40} 条`);
    process.exit(1);
  }

  if (DRY) { console.log("\n✓ --dry 校验通过（未改文件）"); return; }

  // 落盘
  const js = v => JSON.stringify(v);
  const lines = [
    "// data/chapters.js — 全书 361 张章节卡",
    "// year/month/place/chars 由 scripts/build_chapters.py 从 corpus/ 自动抽取；",
    "// gist（自撰概述）来自 data/proposals/notes_*.py，经 scripts/merge_proposals.js 合并。",
    "// 事件关联不在章节卡上维护：唯一关联源是 data/events.js 的 EVENTS[].ch。",
    "const CHAPTERS = [",
  ];
  chapters.forEach(c => {
    const parts = [];
    CHAPTER_FIELDS.forEach(k => {
      if (!(k in c)) return;
      switch (k) {
        case "id": parts.push(`id:${js(c.id)}`); break;
        case "book": case "part": case "ch": case "seq": parts.push(`${k}:${c[k]}`); break;
        case "year": case "month": parts.push(`${k}:${c[k] == null ? "null" : c[k]}`); break;
        case "chars": parts.push(`chars:${js(c.chars || [])}`); break;
        default: parts.push(`${k}:${c[k] ? js(c[k]) : "null"}`);
      }
    });
    Object.keys(c).forEach(k => {
      if (!CHAPTER_FIELDS.includes(k) && k !== "event") parts.push(`${k}:${js(c[k])}`);
    });
    lines.push("  { " + parts.join(", ") + " },");
  });
  lines.push("];", "", 'if (typeof module !== "undefined") module.exports = { CHAPTERS };', "");
  const tmp = CHAPTERS_JS + ".tmp";
  fs.writeFileSync(tmp, lines.join("\n"), "utf8");
  fs.renameSync(tmp, CHAPTERS_JS);

  const now = chapters.filter(c => c.gist).length;
  console.log(`\n✓ 已写入 data/chapters.js（gist 覆盖 ${now} / ${total}）`);
}

main();
