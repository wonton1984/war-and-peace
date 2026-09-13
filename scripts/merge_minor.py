#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_minor.py — 把 data/proposals/minor_*.py 的简录人物增量合并进 data/characters.js

增量、幂等：已存在的 id 跳过（不覆盖手改），只追加新人物。
按 faction 分组插入，保持文件可读。
校验：字段类型、faction 受控词表、chapters 引用、bio 字数与版权门禁；
      导入失败与重复提案 id 一律非零退出；写盘用临时文件 + 原子替换。

用法：
  python3 scripts/merge_minor.py --dry
  python3 scripts/merge_minor.py
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

FAC_LABEL = {"russian_army": "俄军", "french_army": "法军", "court": "宫廷",
             "folk": "平民/仆役", "rostov": "罗斯托夫家", "bolkonsky": "保尔康斯基家",
             "bezukhov": "别祖霍夫家", "kuragin": "库拉金家", "druzh": "德鲁别茨科伊家",
             "mason": "共济会"}


def load_minor():
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
    array_start, _, records = jsio.parse_records(text)
    existing = {rid for _, _, rid, _ in records}

    rows, problems = load_minor()
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
            continue                      # 增量：已在册则跳过，不回滚手改
        unknown = [k for k in r if k not in jsio.CHAR_ORDER]
        if unknown:
            problems.append("%s: %s — 未知字段 %s（须显式加入契约，拒绝静默丢弃）"
                            % (src, rid, unknown))
            continue
        rec = {"id": rid, "name": r.get("name"), "full": r.get("full"),
               "aliases": r.get("aliases") or [], "faction": r.get("faction"),
               "family": r.get("family"), "born": r.get("born"), "died": r.get("died"),
               "title": r.get("title"), "tier": "minor", "bio": r.get("bio") or "",
               "arc": r.get("arc"), "chapters": r.get("chapters") or [],
               "names": {"cao": r.get("name")}, "flag": r.get("flag")}
        found = jsio.validate_character(rec, refs)
        if found:
            problems += ["%s: %s — %s" % (src, rid, m) for m in found]
            continue
        fresh.append(rec)

    print("提案 %d 条 → 新增 %d 条（已在册 %d 条）"
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

    by_fac = {}
    for r in fresh:
        by_fac.setdefault(r["faction"], []).append(r)
    blocks = []
    for fac in jsio.FACTIONS:
        if fac in by_fac:
            blocks.append("  // ————— 简录 · %s —————" % FAC_LABEL.get(fac, fac))
            for r in sorted(by_fac[fac], key=lambda x: x["id"]):
                blocks.append("  " + jsio.render_character(r) + ",")

    idx = records[-1][1] if records else array_start + 1
    addition = "\n".join(blocks).removesuffix(",")
    new_text = text[:idx] + ("," if records else "") + "\n\n" + addition + text[idx:]

    expect = {r["id"]: r for r in fresh}
    try:
        total = jsio.assert_const_text(new_text, "CHARACTERS", expect)
    except jsio.JsDataError as e:
        raise SystemExit("✗ 合并结果校验失败，未写入：%s" % e)
    if DRY:
        print("✓ --dry：语法与字段落地已复验（未改文件）")
        return

    jsio.atomic_write(CHARS, new_text)
    print("\n✓ 已写入 data/characters.js（人物总数 %d，新增 %d）" % (total, len(fresh)))


if __name__ == "__main__":
    main()
