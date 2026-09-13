#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_gists.py — 章节卡 gist 的结构检查与内容反查

结构检查（长度、悬标点、重复字符）发现错误 → **非零退出**。
人名反查（gist 提到的人是否在该章正文出现）只作**待核线索**：正文无此名
可能是异写、简称、转述或 gist 归章有误，须人工判定，故**不据此宣称「全部
命中」，也不单独触发非零退出**。

退出码：0 = 无结构错误（可能仍有待核项）；1 = 有结构错误；2 = 无语料，未做内容反查。

用法：python3 scripts/check_gists.py
"""
import re
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
CH = ROOT / "corpus" / "ch"


def load(names_js, file_js, var):
    js = ('const fs=require("fs"); const out={};'
          'new Function("out","\\"use strict\\";"+fs.readFileSync(%s,"utf8")+" out.X=%s;")(out);'
          'console.log(JSON.stringify(out.X));' % (json.dumps(names_js), var))
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True,
                       cwd=str(ROOT))
    if r.returncode != 0:
        raise SystemExit("node 解析失败:\n" + r.stderr[:600])
    return json.loads(r.stdout)


def main():
    chars = load("data/characters.js", None, "CHARACTERS")
    chapters = load("data/chapters.js", None, "CHAPTERS")

    # 人物 -> 称名（长的优先匹配，避免「安德烈」命中「安德烈公爵」的局部）
    names = []
    for c in chars:
        for a in [c["name"]] + (c.get("aliases") or []):
            if len(a) >= 3:            # 两字名太容易误伤（如「彼得」「谢苗」）
                names.append((a, c["id"]))
    names.sort(key=lambda x: -len(x[0]))

    corpus = {}
    for f in sorted(CH.glob("*.txt")):
        corpus[f.stem] = f.read_text(encoding="utf-8")

    struct, mismatch = [], []
    for ch in chapters:
        g = ch.get("gist") or ""
        cid = ch["id"]
        if not g:
            continue
        # 结构检查
        if re.search(r"[，、；：]$", g):
            struct.append(("悬标点", cid, g[-24:]))
        if len(g) < 12:
            struct.append(("过短", cid, g))
        if re.search(r"(.)\1{4,}", g):
            struct.append(("重复字符", cid, g[:30]))
        # 人名反查（在有人名表且该章有语料时）
        text = corpus.get(cid)
        if not text:
            continue
        hit = set()
        for nm, cid2 in names:
            if nm in g and nm not in text:
                hit.add(nm)
        if hit:
            mismatch.append((cid, sorted(hit), g[:44]))

    print(f"章节卡 {len(chapters)} 张\n")
    print(f"[结构问题] {len(struct)} 条")
    for k, cid, s in struct[:20]:
        print(f"  {k}  {cid}  …{s}")

    if not corpus:
        print("\n无语料（corpus/ch/ 为空）：内容反查未执行，不能据此判定内容通过。")
    else:
        print(f"\n[人名反查待核] {len(mismatch)} 条"
              f"（gist 提到但该章正文无此名；可能是异写 / 简称 / 转述，"
              f"须人工核对，不等于已确认错误）")
        for cid, hit, g in mismatch[:30]:
            print(f"  {cid}  {','.join(hit)}   | {g}…")

    print()
    if struct:
        print(f"✗ 有 {len(struct)} 条结构问题 → 退出码 1")
        raise SystemExit(1)
    if not corpus:
        print("⚠ 前提缺失：无语料，内容反查未执行 → 退出码 2")
        raise SystemExit(2)
    if mismatch:
        print(f"✓ 无结构问题；{len(mismatch)} 条人名反查待核（非失败，需人工判定）")
    else:
        print("✓ 无结构问题；人名反查无疑点")


if __name__ == "__main__":
    main()
