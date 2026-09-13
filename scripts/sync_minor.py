#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_minor.py — 用提案终稿覆盖 data/characters.js 中已合入的简录人物字段

与 merge_minor.py 的分工：
  merge_minor = 增量追加（已存在则跳过，幂等、不回滚手改）
  sync_minor  = 按 id 覆盖提案里显式给出的字段（同步，不是合并）

行为契约：
  · 结构化解析：整条记录交给 node 求值 → 更新字段 → 统一序列化，
    不依赖行首 / 换行 / 正则替值；无关记录一个字节也不动
    （events.js 的字段 / 排版调整不会影响本脚本）。
  · 覆盖字段 = characters.js 的完整字段契约（name/full/aliases/faction/family/
    born/died/title/bio/arc/chapters/flag）；未给出的字段保持语义不变。
  · 提案 id 在 characters.js 中不存在 → 明确报错（同步不新增）；
    重复提案 id、导入失败、未知字段、类型 / 引用校验失败均非零退出且不落盘。
  · 写盘用临时文件 + 原子替换，并在替换前用 node 复验语法与字段落地。

用法：
  python3 scripts/sync_minor.py --dry
  python3 scripts/sync_minor.py
"""
import sys
import pathlib
import importlib.util

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import jsio

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROP = ROOT / "data" / "proposals"
CHARS = ROOT / "data" / "characters.js"
DRY = "--dry" in sys.argv[1:]

# 允许被覆盖的字段（其余字段不动，避免误伤已合入的手改）
FIELDS = [k for k in jsio.CHAR_ORDER if k != "id"]


def load_proposals():
    rows, problems = [], []
    for f in sorted(PROP.glob("minor_*.py")):
        spec = importlib.util.spec_from_file_location("minprop_" + f.stem, f)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            problems.append("%s: 导入失败 — %s" % (f.name, e))
            continue
        items = getattr(mod, "MINOR", None)
        if not isinstance(items, list):
            problems.append("%s: 缺 MINOR 列表" % f.name)
            continue
        rows += [(f.name, r) for r in items]
    return rows, problems


def main():
    try:
        refs = jsio.refs_from(jsio.load_data(ROOT))
        text = CHARS.read_text(encoding="utf-8")
    except jsio.JsDataError as e:
        raise SystemExit("✗ 数据载入失败：%s" % e)

    problems = []
    by_id = {}
    for start, end, rid, raw in jsio.parse_records(text)[2]:
        if rid in by_id:
            problems.append("characters.js 中 id 重复：%s" % rid)
            continue
        by_id[rid] = (start, end, raw)

    rows, load_problems = load_proposals()
    problems += load_problems

    seen, edits, updated = {}, [], []
    for src, r in rows:
        rid = r.get("id") if isinstance(r, dict) else None
        if not isinstance(rid, str) or not rid:
            problems.append("%s: 提案缺 id（%r）" % (src, r))
            continue
        if rid in seen:
            problems.append("%s: 重复提案 id %s（已见于 %s）" % (src, rid, seen[rid]))
            continue
        seen[rid] = src
        if rid not in by_id:
            problems.append("%s: %s — characters.js 中不存在（同步按 id 覆盖，不新增；"
                            "新增请用 merge_minor.py）" % (src, rid))
            continue
        unknown = [k for k in r if k not in jsio.CHAR_ORDER]
        if unknown:
            problems.append("%s: %s — 未知字段 %s（须显式加入契约，拒绝静默丢弃）"
                            % (src, rid, unknown))
            continue
        try:
            rec = jsio.parse_object(by_id[rid][2])
        except jsio.JsDataError as e:
            problems.append("%s: %s — 记录解析失败：%s" % (src, rid, e))
            continue
        merged = dict(rec)
        merged.update(r)
        found = jsio.validate_character(merged, refs)
        if found:
            problems += ["%s: %s — %s" % (src, rid, m) for m in found]
            continue
        diffs = [k for k in FIELDS if k in r and rec.get(k) != r[k]]
        if not diffs:
            continue
        start, end, _ = by_id[rid]
        edits.append((start, end, jsio.render_character(merged)))
        updated.append((rid, src, diffs, merged))

    for rid, src, diffs, _ in updated:
        print("  %-18s %-18s 覆盖 %s" % (rid, src, ", ".join(diffs)))
    print("\n%s共 %d 条被更新" % ("[dry] " if DRY else "", len(updated)))

    if problems:
        print("\n✗ %d 个问题（未改文件）：" % len(problems))
        for p in problems[:25]:
            print("  " + p)
        if len(problems) > 25:
            print("  …另有 %d 条" % (len(problems) - 25))
        sys.exit(1)
    if not updated:
        return

    new_text = text
    for start, end, rendered in sorted(edits, key=lambda x: -x[0]):
        new_text = new_text[:start] + rendered + new_text[end:]

    try:
        jsio.assert_const_text(new_text, "CHARACTERS", {rid: rec for rid, _, _, rec in updated})
    except jsio.JsDataError as e:
        raise SystemExit("✗ 同步结果校验失败，未写入：%s" % e)
    if DRY:
        print("✓ --dry：语法与字段落地已复验（未改文件）")
        return
    jsio.atomic_write(CHARS, new_text)
    print("✓ 已写入 data/characters.js")


if __name__ == "__main__":
    main()
