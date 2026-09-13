#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
find_missing.py — 从语料中挖出「尚未收录」的具名人物候选

方法（三层过滤，逐步收紧）：
  1. 候选来源：带称号的专名（X公爵/伯爵/将军/小姐/夫人/大尉…）+ 说话人（X说/X问/X答）
  2. 排除：已在 characters.js 的 name/aliases 中出现者（含互为子串）
  3. 排除：普通词、代词、抽象名词（内置停用表 + 词频分布启发）
  4. 汇总：出现在 ≥N 章、总次数 ≥M 的候选，按章数降序

输出每条的「出现章 id」与一句上下文，便于人工判断是否真有出场。

用法：
  python3 scripts/find_missing.py            # 默认 ≥3章 且 ≥5次
  python3 scripts/find_missing.py --min-ch 2 --min-n 4
"""
import re
import sys
import json
import glob
import pathlib
import subprocess
import collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
CH = ROOT / "corpus" / "ch"

SUFFIX = ("公爵小姐|公爵夫人|伯爵夫人|伯爵小姐|子爵|男爵|公爵|伯爵|将军|元帅|"
          "上尉|大尉|中尉|少尉|亲王|小姐|夫人|医生|神父|主教|总督|大臣|"
          "村长|管家|使女|女仆|神父|修士|商人|军官|副官|参谋")

# 常见非人物词（含词首匹配）
STOP = re.compile(
    r'^(?:我|你|他|她|它|您|咱|谁|什么|怎么|为什么|因为|所以|但是|如果|于是|接着|然后|'
    r'现在|这时|那时|大家|人们|有人|一个|这个|那个|每个|自己|彼此|'
    r'大|小|老|新|好|坏|高|矮|胖|瘦|年|青|'
    r'心|眼|脸|手|嘴|头|声|嘴|背|胸|腿|脚|'
    r'不|没|是|的|了|着|过|要|会|能|可|该|把|被|给|对|向|从|和|与|跟|同|为|在|有|无|'
    r'上|下|里|外|前|后|中|间|时|候|样|些|个|只|就|也|都|还|却|才|又|再|很|太|最|更|'
    r'这|那|哪|此|彼|各|某|全|整|半|几|多|少|许|些)'
)
# 显然不是人名的高频搭配
NOT_NAME = re.compile(r'(?:公爵夫人|伯爵夫人|公爵小姐|伯爵小姐|将军夫人|省长|团长|连长|营长|'
                      r'军需官|军法官|副官|传令兵|勤务兵|使女|女仆|保姆|家庭教师|'
                      r'外科医生|主治医生|军医|兽医)')
# 以这些字结尾 → 几乎不是人名（副词/状态/虚词）
BAD_TAIL = re.compile(r'(?:地|的|了|着|过|们|在|有|是|不|没|很|太|更|最|再|又|也|都|还|就|'
                      r'却|只|才|便|而|且|或|和|与|及|以|为|被|把|给|对|向|从|到|于|'
                      r'来|去|上|下|里|外|前|后|中|间|时|候|样|些|个|种|类|般|似|如)')
# 常见非名称组合（含这些字则大概率不是音译人名）
BAD_CHARS = re.compile(r'(?:们|地|得|很|太|更|最|再|又|也|都|还|就|却|只|才|便|而|且|或|'
                      r'没|不|无|有|是|的|了|着|过|和|与|及|以|为|被|把|给|对|向|从|'
                      r'说|问|答|看|听|想|知|道|来|去|走|跑|坐|站|笑|哭|喊|叫|'
                      r'继|续|皱|起|眉|但|又|而|他|她|它|我|你)')
# 泛称（职业/兵种/身份），不是具名人物
GENERIC = re.compile(r'(?:哥萨克|骠骑兵|骑兵|步兵|炮兵|士兵|军官|将军们|司务长|军士|'
                     r'共济会会员|会员|商人|农民|仆人|听差|勤务兵|副官们|'
                     r'用法语|用法|用俄语|用德语)')


def load_known():
    js = ('const fs=require("fs"); const out={};'
          'new Function("out","\\"use strict\\";"+fs.readFileSync("data/characters.js","utf8")'
          '+" out.X=CHARACTERS;")(out); console.log(JSON.stringify(out.X));')
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True, cwd=str(ROOT))
    chars = json.loads(r.stdout)
    known = set()
    for c in chars:
        known.add(c["name"])
        # 显示名可带限定语
        known.add(c["name"].replace("（", "(").split("(")[0].strip())
        for a in (c.get("aliases") or []):
            known.add(a)
    return known, chars


def main():
    argv = sys.argv[1:]
    min_ch = 3
    min_n = 5
    for i, a in enumerate(argv):
        if a == "--min-ch" and i + 1 < len(argv):
            min_ch = int(argv[i + 1])
        if a == "--min-n" and i + 1 < len(argv):
            min_n = int(argv[i + 1])

    files = sorted(CH.glob("*.txt"))
    if not files:
        raise SystemExit("无语料：corpus/ch/ 为空")
    txt = {f.stem: f.read_text(encoding="utf-8") for f in files}
    alls = "".join(txt.values())
    known, chars = load_known()

    def is_known(w):
        return any(w in k or k in w for k in known if len(k) >= 2)

    cand = collections.Counter()
    # 源 1：带称号的专名
    for m in re.finditer(r'([\u4e00-\u9fff]{2,6})(?:' + SUFFIX + r')', alls):
        cand[m.group(1)] += 1
    # 源 2：说话人
    for m in re.finditer(r'([\u4e00-\u9fff]{3,6})(?:说|问|答|回答|喊道|叫道|嚷道|接着说)', alls):
        cand[m.group(1)] += 2      # 有对白者权重更高

    rows = []
    for w, n in cand.most_common(1200):
        if n < min_n:
            break
        if len(w) < 3:                       # 两字名歧义太大，本项目一律不收
            continue
        if STOP.match(w) or NOT_NAME.match(w) or GENERIC.search(w):
            continue
        if BAD_TAIL.search(w):
            continue
        # 音译人名特征：整体不应含太多常见动词/虚词字
        if len(BAD_CHARS.findall(w)) >= 1 and not re.match(r'^[\u4e00-\u9fff]{3,5}$', w):
            continue
        if is_known(w):
            continue
        chs = [k for k in sorted(txt) if w in txt[k]]
        if len(chs) < min_ch:
            continue
        sample = ""
        for k in chs:
            m = re.search(r'.{0,40}' + re.escape(w) + r'.{0,50}', txt[k])
            if m:
                sample = m.group(0).replace("\n", " ")
                break
        rows.append((len(chs), n, w, chs, sample))

    rows.sort(key=lambda r: (-r[0], -r[1]))
    print(f"未收录候选（≥{min_ch}章 且 ≥{min_n}次）：{len(rows)} 个")
    print(f"现网已收 {len(chars)} 位\n")
    for nc, n, w, chs, sample in rows:
        print(f"  {nc:>3}章 {n:>4}次  {w}")
        print(f"         章: {' '.join(chs[:10])}{' …' if len(chs) > 10 else ''}")
        if sample:
            print(f"         例: {sample[:96]}")


if __name__ == "__main__":
    main()
