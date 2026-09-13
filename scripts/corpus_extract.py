#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
corpus_extract.py — 从底本 epub 抽取私有用语料与结构索引。

产物：
  corpus/ch/<卷>-<部>-<章>.txt   逐章正文（私有，.gitignore，永不提交）
  corpus/structure.json          卷/部/章骨架（可提交：结构性事实）
  corpus/cooccur.json            章级人名共现矩阵（可提交：本方索引的派生元数据）
  corpus/appendix-outline.txt    读客版《各章内容梳理》正文（私有，仅供人工比对，永不提交）

用法：python3 scripts/corpus_extract.py
"""
import re
import json
import html
import zipfile
import pathlib
import collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus"
EPUB = CORPUS / "war-and-peace-caoying-2019.epub"

# 底本本版实测的 spine 阅读顺序（正文章节文件）
SPINE = [
    "text/part0001_split_001.html", "text/part0001_split_002.html",
    "text/part0001_split_003.html", "text/part0001_split_004.html",
    "text/part0002_split_001.html", "text/part0002_split_002.html",
    "text/part0002_split_003.html", "text/part0002_split_004.html",
    "text/part0002_split_005.html",
    "text/part0003_split_001.html", "text/part0003_split_002.html",
    "text/part0003_split_003.html", "text/part0003_split_004.html",
    "text/part0003_split_005.html",
    "text/part0004_split_001.html", "text/part0004_split_002.html",
    "text/part0004_split_003.html", "text/part0004_split_004.html",
]
APPENDIX_OUTLINE = "text/part0011_split_002.html"

CN = "一二三四五六七八九十"
CN2INT = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
          "六": 6, "七": 7, "八": 8, "九": 9}


def cn2int(s):
    """'第一卷' / '第一部' / '十二' -> int"""
    s = s.strip().strip("第").strip().rstrip("卷部").strip()
    if s == "十":
        return 10
    if "十" in s:
        a, b = s.split("十")
        return (CN2INT.get(a, 1) if a else 1) * 10 + (CN2INT.get(b, 0) if b else 0)
    return CN2INT.get(s, 0)


def strip_tags(fragment):
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).replace("\ufeff", "").strip()


def main():
    CORPUS.mkdir(exist_ok=True)
    (CORPUS / "ch").mkdir(exist_ok=True)

    z = zipfile.ZipFile(EPUB)
    read = lambda name: z.read(name).decode("utf-8", errors="replace")

    # ---------- 1. 正文逐章切分 ----------
    # 标记：<h2>卷</h2> / <h3>部</h3> / <p class="center|conquot"><span class="bold">N</span>
    book = part = None
    chapters = []  # {book,part,ch,text}
    buf = []
    cur = None

    def flush():
        if cur is not None:
            cur["text"] = re.sub(r"\n{3,}", "\n\n", "\n".join(buf).strip())
            chapters.append(cur)

    # 单趟顺序扫描：卷头 / 部头 / 章号 / 正文段落，按出现顺序归位
    TOKEN = re.compile(
        r'<h2[^>]*>(?P<h2>.*?)</h2>'
        r'|<h3[^>]*>(?P<h3>.*?)</h3>'
        r'|<p[^>]*class="(?P<pc>center|conquot)"[^>]*>\s*<span class="bold">(?P<num>[^<]+)</span>'
        r'|<p[^>]*>(?P<body>.*?)</p>',
        re.S,
    )
    for name in SPINE:
        raw = read(name)
        for m in TOKEN.finditer(raw):
            if m.group("h2") is not None:
                flush(); cur, buf = None, []
                bt = strip_tags(m.group("h2"))
                book = 5 if bt.startswith("尾声") else cn2int(bt)
            elif m.group("h3") is not None:
                flush(); cur, buf = None, []
                part = cn2int(strip_tags(m.group("h3")))
            elif m.group("num") is not None:
                tok = strip_tags(m.group("num"))
                if re.fullmatch(r"\d+", tok):     # 非数字（如「布告」）仅作正文
                    flush()
                    cur, buf = {"book": book, "part": part, "ch": int(tok)}, []
                else:
                    buf.append(tok)
            else:
                txt = strip_tags(m.group("body"))
                if txt and cur is not None:
                    buf.append(txt)
    flush()

    # ---------- 2. 落盘语料 ----------
    for c in chapters:
        fn = CORPUS / "ch" / f"{c['book']}-{c['part']}-{c['ch']:02d}.txt"
        fn.write_text(c["text"], encoding="utf-8")

    # ---------- 3. 结构索引 ----------
    parts = collections.OrderedDict()
    for c in chapters:
        key = f"{c['book']}-{c['part']}"
        parts.setdefault(key, 0)
        parts[key] = max(parts[key], c["ch"])
    # 尾声 = 卷 5
    struct = {"books": [], "epilogue": [], "totalChapters": len(chapters), "parts": parts}
    for b in (1, 2, 3, 4):
        bl = [{"id": int(k.split("-")[1]), "chapters": v}
              for k, v in parts.items() if k.startswith(f"{b}-")]
        struct["books"].append({"id": b, "parts": bl})
    for k, v in parts.items():
        if k.startswith("5-"):
            struct["epilogue"].append({"id": int(k.split("-")[1]), "chapters": v})
    (CORPUS / "structure.json").write_text(
        json.dumps(struct, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---------- 4. 章级人名共现 ----------
    NAME_IDS = [
        "皮埃尔", "安德烈", "娜塔莎", "尼古拉", "玛丽雅", "海伦", "华西里",
        "陶洛霍夫", "杰尼索夫", "阿纳托里", "保尔康斯基", "别祖霍夫", "罗斯托夫",
        "库拉金", "舍勒", "宋尼雅", "彼嘉", "薇拉", "库图佐夫", "拿破仑",
        "普拉东", "阿赫罗西莫娃", "伊波利特", "丽莎", "裘丽", "保里斯",
        "斯佩蓝斯基", "拉斯托普庆", "巴格拉基昂", "莫特玛", "阿尔巴端奇",
        "布莉恩", "德鲁别茨基", "卡嘉", "薇拉", "巴兹杰耶夫", "伊林",
        "丹尼洛", "巴拉加", "仑巴尔", "季洪", "卡佩尔",
    ]
    cooc = {}
    for c in chapters:
        key = f"{c['book']}-{c['part']}-{c['ch']}"
        cooc[key] = sorted({n for n in NAME_IDS if n in c["text"]})
    (CORPUS / "cooccur.json").write_text(
        json.dumps(cooc, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---------- 5. 读客版《各章内容梳理》（私有，仅供人工比对） ----------
    if APPENDIX_OUTLINE in z.namelist():
        raw = read(APPENDIX_OUTLINE)
        txt = "\n".join(
            l.strip() for l in html.unescape(re.sub(r"<[^>]+>", "\n", raw)).split("\n")
            if l.strip())
        (CORPUS / "appendix-outline.txt").write_text(txt, encoding="utf-8")

    print(f"章节 {len(chapters)} 条")
    for k, v in parts.items():
        print(f"  {k}: {v} 章")
    print(f"语料 -> corpus/ch/（{len(chapters)} 文件）")


if __name__ == "__main__":
    main()
