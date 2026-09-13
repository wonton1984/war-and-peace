#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_names.py — 核对人物称名与草婴底本的一致性

判定语义（重要，避免误报）：
  · `name` 是**界面显示名**，可以是完整姓名（如「娜塔丽·罗斯托娃」），
    不必在正文里逐字出现。
  · `aliases` 是**检索用称名**，必须能在底本正文中命中，否则会污染搜索。
  · `names.cao` 是「草婴译本写法」的记录字段，应等于该人物在底本中的主用法。

因此本脚本报告两类真问题：
  A. 该人物的 name + aliases 全部 0 命中 → 说明整个条目与底本脱节
  B. 某条 alias 0 命中 → 该别名无效，应删（其他译本写法放 names.js 的 variants）
另附提示：names.cao 在正文中 0 命中的条目（C 类，待核，不单独判失败）。

退出码：0 = 无 A/B 类问题（C 类待核不影响退出码）；1 = 有 A/B 类问题；2 = 无语料。

用法：python3 scripts/check_names.py
"""
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
CH = ROOT / "corpus" / "ch"

# 允许「显示名」不必逐字出现在正文中（完整姓名、敬称等）
DISPLAY_OK = True


def load_chars():
    js = ('const fs=require("fs"); const out={};'
          'new Function("out","\\"use strict\\";"+fs.readFileSync("data/characters.js","utf8")'
          '+" out.X=CHARACTERS;")(out); console.log(JSON.stringify(out.X));')
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True, cwd=str(ROOT))
    if r.returncode != 0:
        raise SystemExit("node 解析失败:\n" + r.stderr[:500])
    return json.loads(r.stdout)


def main():
    chars = load_chars()
    files = sorted(CH.glob("*.txt"))
    if not files:
        print("无语料（corpus/ch/ 为空）：未做称名核查 → 退出码 2。")
        raise SystemExit(2)
    all_text = "".join(f.read_text(encoding="utf-8") for f in files)

    orphan, dead_alias, cao_miss = [], [], []
    for c in chars:
        name = c["name"]
        aliases = c.get("aliases") or []
        cao = (c.get("names") or {}).get("cao")

        # 显示名可带限定语（同名区分用），匹配时取括号前的本名
        base = name.replace("（", "(").split("(")[0].strip()
        if all_text.count(base) == 0 and all_text.count(name) == 0 \
           and not any(all_text.count(a) for a in aliases):
            orphan.append((c["id"], name, aliases))

        for a in aliases:
            if all_text.count(a) == 0:
                dead_alias.append((c["id"], name, a))

        if cao and all_text.count(cao) == 0:
            cao_miss.append((c["id"], name, cao))

    n = len(chars)
    print(f"人物 {n} 位（语料 {len(files)} 章）\n")

    print(f"[A] name+aliases 全部无命中（条目与底本脱节）：{len(orphan)}")
    for cid, nm, al in orphan:
        print(f"    ✗ {cid:<16} {nm:<14} aliases={al}")
    if not orphan:
        print("    ✓ 无")

    print(f"\n[B] 无效别名（正文 0 命中，会污染搜索）：{len(dead_alias)}")
    for cid, nm, a in dead_alias:
        print(f"    ✗ {cid:<16} {nm:<12} 「{a}」")
    if not dead_alias:
        print("    ✓ 无")

    print(f"\n[C] names.cao 与底本不符：{len(cao_miss)}")
    for cid, nm, cao in cao_miss:
        print(f"    ⚠ {cid:<16} {nm:<12} cao=「{cao}」")
    if not cao_miss:
        print("    ✓ 无")

    bad = len(orphan) + len(dead_alias)
    print()
    if bad:
        print(f"✗ 有 {bad} 处 A/B 类问题需要修正 → 退出码 1")
        raise SystemExit(1)
    if cao_miss:
        print(f"⚠ A/B 类无问题，但 C 类有 {len(cao_miss)} 条 names.cao 提示待核 —— "
              f"不能据此宣称「全部称名与底本一致」")
        raise SystemExit(0)
    print("✓ 全部称名与底本一致")
    raise SystemExit(0)


if __name__ == "__main__":
    main()
