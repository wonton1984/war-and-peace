#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_events.py — 用语料反查事件卡的章节引用

对每个事件，按它的 chars 在全书找出「共现度最高」的章节窗口，
与声明的事件 ch[] 比对，输出可疑引用。

用法：python3 scripts/verify_events.py [--fix]
"""
import re
import sys
import json
import pathlib
import collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
CH = ROOT / "corpus" / "ch"
EV = ROOT / "data" / "events.js"
FIX = "--fix" in sys.argv

# 人物 id → 语料中的宽匹配（含称呼变体）
PAT = {
    "pierre": r"皮埃尔", "kirill": r"老伯爵|垂危的伯爵|病伯爵", "katya": r"卡嘉|公爵小姐",
    "ilya": r"罗斯托夫伯爵(?!夫人)|老伯爵", "countess_r": r"伯爵夫人|母亲",
    "natasha": r"娜塔莎|娜塔丽", "nikolai": r"尼古拉|罗斯托夫", "vera": r"薇拉|维拉",
    "petya": r"彼嘉", "sophia": r"宋尼雅|宋尼卡",
    "old_prince": r"保尔康斯基公爵|老公爵", "andrei": r"安德烈", "marya": r"玛丽雅|玛丽",
    "liza": r"小公爵夫人|丽莎", "nikolushka": r"小尼古拉",
    "vasily": r"华西里", "helen": r"海伦", "anatole": r"阿纳托里|阿纳托利",
    "hippolyte": r"伊波利特", "kuragina": r"华西里公爵夫人",
    "anna_mikh": r"德鲁别茨基公爵夫人|安娜·米哈伊洛夫娜", "boris": r"保里斯",
    "kutuzov": r"库图佐夫", "bagration": r"巴格拉基昂", "denisov": r"杰尼索夫|捷尼索夫",
    "dolokhov": r"陶洛霍夫", "tushin": r"土申", "nesvitsky": r"聂斯维茨基",
    "bilbin": r"比利平", "zhilinsky": r"吉梁宁|基莫兴|热尔科夫", "iljin": r"伊林",
    "napoleon": r"拿破仑|波拿巴", "alexander": r"亚历山大", "franz": r"弗朗茨|奥国皇帝",
    "arakcheev": r"阿拉克切耶夫", "speransky": r"斯佩蓝斯基|斯佩兰斯基",
    "rastopchin": r"拉斯托普庆", "murat": r"缪拉", "davout": r"达武|达乌",
    "barclay": r"巴克莱", "volzogen": r"伏尔佐根", "bennigsen": r"别尼生|贝尼格森",
    "anna_sherer": r"舍勒", "ahrosimova": r"阿赫罗西莫娃", "bourienne": r"布莉恩",
    "julie": r"裘丽|朱丽", "berg": r"别尔格", "platon": r"普拉东",
    "bazdeev": r"巴兹杰耶夫", "villarsky": r"维拉尔斯基", "alpatych": r"阿尔巴端奇",
    "mativier": r"梅蒂维埃", "mikhail": r"米哈伊尔·伊凡内奇", "rossaw": r"让理夫人",
    "balaga": r"巴拉加", "tihon": r"季洪", "lavrushka": r"拉夫鲁什卡", "linguist": r"仑巴尔",
}


def main():
    corpus = {p.stem: p.read_text(encoding="utf-8") for p in sorted(CH.glob("*.txt"))}
    if not corpus:
        print("无语料，请先 corpus_extract.py")
        return
    ids = sorted(corpus)
    idx = {k: i for i, k in enumerate(ids)}

    src = EV.read_text(encoding="utf-8")
    # 用 node 解析更稳妥，但这里只需读字段，用正则抽事件块
    blocks = re.findall(r'\{\s*id:"(e-[a-z0-9\-]+)".*?\n    flag:', src, re.S)
    allblocks = re.findall(r'\{ id:"(e-[a-z0-9\-]+)".*?\n    flag:\w+ \}', src, re.S)
    # 更宽松：按 id 切分
    parts = re.split(r'\n  \{ id:"', src)
    events = []
    for p in parts[1:]:
        eid = p.split('"')[0]
        chs = re.search(r'ch:\[([^\]]*)\]', p)
        chars = re.search(r'chars:\[([^\]]*)\]', p)
        if not chs:
            continue
        events.append({
            "id": eid,
            "ch": re.findall(r'"([\d\-]+)"', chs.group(1)),
            "chars": re.findall(r'"([a-z_]+)"', chars.group(1)) if chars else [],
        })

    print(f"事件 {len(events)} 个\n")
    bad = []
    for e in events:
        if not e["chars"]:
            continue
        # 计算每个章节的命中人数
        score = collections.Counter()
        for cid in ids:
            t = corpus[cid]
            n = sum(1 for c in e["chars"] if PAT.get(c) and re.search(PAT[c], t))
            if n:
                score[cid] = n
        need = max(2, len(e["chars"]) // 2)
        good = {c for c, n in score.items() if n >= need}
        declared = set(e["ch"])
        if not declared:
            continue
        hit = len(declared & good) / max(1, len(declared))
        if hit < 0.5:
            # 找声明区间附近的候选
            first, last = declared and min(declared), max(declared)
            near = sorted(c for c in good if c >= first and c <= last) or sorted(good)[:8]
            bad.append((e["id"], sorted(declared), near[:8], len(e["chars"])))
    print(f"可疑事件 {len(bad)} 个（声明的章节与人物共现不符）：\n")
    for eid, dec, sug, nc in bad:
        print(f"  {eid}  chars={nc}")
        print(f"    声明: {','.join(dec)}")
        print(f"    候选: {','.join(sug)}")


if __name__ == "__main__":
    main()
