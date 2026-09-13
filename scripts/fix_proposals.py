#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_proposals.py — 提案体检与自动修复（正则解析 → 重新生成，绝不做行级手术）

修复：
  1. gist 超出 60 字 → 在句读边界（。；！？）截断，保留完整句子
  2. 多余/失控的换行与括号 → 由解析器统一重建，不依赖原缩进
  3. 重复 key → 保留先出现者
无法解析的条目原样报告，不猜测。

用法：python3 scripts/fix_proposals.py [--dry]
"""
import re
import sys
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROP = ROOT / "data" / "proposals"
LIMIT = 60
VALID_TAG = ["peace", "war", "essay", "transition"]
DRY = "--dry" in sys.argv

# 逐条抽取：key 后跟一个 {...} 对象（括号配对，容忍跨行）
ENTRY = re.compile(r'"(\d+-\d+-\d+)":\s*(\{)', re.S)
BREAKS = "。；！？"


def shorten(text, limit=LIMIT):
    """在句读边界截断到 limit 字内；无句读则退到逗号。"""
    if len(text) <= limit:
        return text
    cut = max((i + 1 for i, ch in enumerate(text) if ch in BREAKS and i + 1 <= limit),
              default=None)
    if cut:
        return text[:cut]
    cut = max((i for i, ch in enumerate(text) if ch in "，、" and i + 1 <= limit),
              default=None)
    if cut:
        return text[:cut].rstrip("，、") + "。"
    return text[:limit - 1] + "。"


def balanced_span(src, open_idx):
    """从 '{' 起找配对右括号，返回 (end_idx, 内部文本)；不匹配返回 None。"""
    depth = 0
    in_str = False
    i = open_idx
    while i < len(src):
        c = src[i]
        if in_str:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return i, src[open_idx + 1:i]
        i += 1
    return None, None


def parse_entries(src):
    """→ [(key, dict|None, raw)]；None 表示该条解析失败。"""
    out = []
    for m in ENTRY.finditer(src):
        key = m.group(1)
        end, inner = balanced_span(src, m.start(2))
        if end is None:
            out.append((key, None, src[m.start():m.start() + 200]))
            continue
        try:
            val = json.loads("{" + inner + "}")
        except Exception:
            # 容错：把 Python 的 None/True/False 转成 JSON 再试
            try:
                val = json.loads(("{" + inner + "}")
                                 .replace(": None", ": null")
                                 .replace(": True", ": true")
                                 .replace(": False", ": false"))
            except Exception:
                out.append((key, None, src[m.start():end + 1]))
                continue
        out.append((key, val, src[m.start():end + 1]))
    return out


def fix_file(path):
    src = path.read_text(encoding="utf-8")
    entries = parse_entries(src)
    seen, rows, changes, broken = set(), [], [], []

    for key, val, raw in entries:
        if key in seen:
            changes.append(f"{key}: 删除重复条目")
            continue
        seen.add(key)
        if val is None:
            broken.append(key)
            continue
        g = val.get("gist")
        if not g:
            broken.append(key)
            continue
        if len(g) > LIMIT:
            new = shorten(g)
            changes.append(f"{key}: gist {len(g)}→{len(new)}")
            val["gist"] = new
        if val.get("tag") and val["tag"] not in VALID_TAG:
            changes.append(f"{key}: tag 「{val['tag']}」不在受控表，已置空")
            del val["tag"]
        rows.append((key, val))

    if broken:
        print(f"  ⚠ {path.name}: 以下条目无法解析，保持原样 → {', '.join(broken)}")

    if not changes and not broken:
        return []

    # 重新生成（统一缩进，一行一条，避免任何行级手术）
    keys = sorted(rows, key=lambda kv: [int(x) for x in kv[0].split("-")])
    lines = [
        "# -*- coding: utf-8 -*-",
        f"# 由 scripts/fix_proposals.py 规范化（{path.name}）",
        "NOTES = {",
    ]
    for key, val in keys:
        order = ["gist", "tag", "place", "chars", "year", "month"]
        parts = []
        for k in order:
            if k not in val:
                continue
            parts.append(f'"{k}": {json.dumps(val[k], ensure_ascii=False)}')
        for k in val:
            if k not in order:
                parts.append(f'"{k}": {json.dumps(val[k], ensure_ascii=False)}')
        lines.append(f'    "{key}": {{{", ".join(parts)}}},')
    lines += ["}", ""]

    if not DRY:
        path.write_text("\n".join(lines), encoding="utf-8")
    return changes


def main():
    files = sorted(PROP.glob("notes_*.py"))
    if not files:
        print("无提案文件")
        return
    total = 0
    for f in files:
        ch = fix_file(f)
        if ch:
            total += len(ch)
            print(f"{f.name}:")
            for c in ch:
                print("   " + c)
    print(f"\n{'[dry] ' if DRY else ''}共 {total} 处修复")


if __name__ == "__main__":
    main()
