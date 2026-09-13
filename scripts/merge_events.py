#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_events.py — 把 data/proposals/events_*.py 的新事件卡增量合并进 data/events.js

增量、幂等：已存在的 id 跳过（不覆盖已合入内容），只追加新事件。
字段契约与 scripts/sync_event_summaries.py 共用（含可选 day / battle）。
校验：字段类型、受控词表、chars/place/theme/arc/ch/battle 引用、字数与版权门禁；
      导入失败与重复提案 id 一律非零退出；写盘用临时文件 + 原子替换。

用法：
  python3 scripts/merge_events.py --dry
  python3 scripts/merge_events.py
"""
import sys
import pathlib
import importlib.util

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import jsio

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROP = ROOT / "data" / "proposals"
EV = ROOT / "data" / "events.js"
DRY = "--dry" in sys.argv[1:]


def load_proposals():
    """逐文件导入 EVENTS_PROPOSAL；导入失败计入 problems（调用方非零退出）。"""
    rows, problems = [], []
    for f in sorted(PROP.glob("events_*.py")):
        spec = importlib.util.spec_from_file_location("evprop_" + f.stem, f)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            problems.append("%s: 导入失败 — %s" % (f.name, e))
            continue
        items = getattr(mod, "EVENTS_PROPOSAL", None)
        if not isinstance(items, list):
            problems.append("%s: 缺 EVENTS_PROPOSAL 列表" % f.name)
            continue
        rows += [(f.name, r) for r in items]
    return rows, problems


def main():
    try:
        data = jsio.load_data(ROOT)
        refs = jsio.refs_from(data)
        text = EV.read_text(encoding="utf-8")
    except jsio.JsDataError as e:
        raise SystemExit("✗ 数据载入失败：%s" % e)
    array_start, _, records = jsio.parse_records(text)
    existing = {rid for _, _, rid, _ in records}

    rows, problems = load_proposals()
    seen, fresh = {}, []
    for src, r in rows:
        rid = r.get("id") if isinstance(r, dict) else None
        if not isinstance(rid, str) or not rid:
            problems.append("%s: 提案缺 id（%r）" % (src, r))
            continue
        if rid in seen:
            problems.append("%s: 重复提案 id %s（已见于 %s）" % (src, rid, seen[rid]))
            continue
        seen[rid] = src
        if rid in existing:
            continue                      # 增量：已合入则跳过，不回滚
        found = jsio.validate_event(r, refs)
        if found:
            problems += ["%s: %s — %s" % (src, rid, m) for m in found]
            continue
        fresh.append(r)

    print("提案 %d 条 → 可新增 %d 条（已在册 %d 条）"
          % (len(rows), len(fresh), len(seen) - len(fresh)))
    if problems:
        print("\n✗ %d 个问题（未改文件）：" % len(problems))
        for p in problems[:25]:
            print("  " + p)
        if len(problems) > 25:
            print("  …另有 %d 条" % (len(problems) - 25))
        sys.exit(1)
    if not fresh:
        print("\n[dry] 未改文件" if DRY else "\n无新增")
        return

    blocks = ["  " + jsio.render_event(r) for r in fresh]
    idx = records[-1][1] if records else array_start + 1
    new_text = text[:idx] + ("," if records else "") + "\n\n" + ",\n\n".join(blocks) + text[idx:]

    expect = {r["id"]: r for r in fresh}
    try:
        total = jsio.assert_const_text(new_text, "EVENTS", expect)
    except jsio.JsDataError as e:
        raise SystemExit("✗ 合并结果校验失败，未写入：%s" % e)
    if DRY:
        print("✓ --dry：语法与字段落地已复验（未改文件）")
        return

    jsio.atomic_write(EV, new_text)
    print("\n✓ 已写入 data/events.js（事件总数 %d，新增 %d）" % (total, len(fresh)))


if __name__ == "__main__":
    main()
