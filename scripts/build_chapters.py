#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_chapters.py — 生成 data/chapters.js 的「初始化候选」

定位：显式初始化，不是日常更新命令。
  · 目标文件已存在 → 非零退出，一个字也不改（没有 --force）。
  · 只允许写到不存在的独立文件：--output <新文件>。
  · gist（自撰概述）来自 data/proposals/notes_*.py（人工稿的唯一来源）；
    该来源缺失时输出明确标记为「骨架」（gist 全为 null、flag:"verify"），
    不冒充人工稿重建，也不具备替换正式数据的能力。
  · year/month/place/chars 由 corpus/ch/ 自动抽取（提示级，需人工校订）。
  · 事件关联不在章节卡上维护：唯一关联源是 data/events.js 的 EVENTS[].ch。
  · 正式 chapters.js 由 merge_proposals.js 在候选上增量合入，不要用本脚本覆盖。

用法：
  python3 scripts/build_chapters.py --output /tmp/chapters.skeleton.js
  python3 scripts/build_chapters.py           # 目标 data/chapters.js 已存在 → 拒绝
"""
import re
import sys
import json
import pathlib
import importlib.util

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import jsio

ROOT = pathlib.Path(__file__).resolve().parent.parent
CH = ROOT / "corpus" / "ch"
OUT = ROOT / "data" / "chapters.js"
PROP = ROOT / "data" / "proposals"

# 人物 id -> 正文匹配正则（与 build_characters.py 的 ROSTER 保持一致）
CHAR_PAT = {
    "pierre": r"皮埃尔", "kirill": r"老别祖霍夫伯爵", "katya": r"卡嘉",
    "ilya": r"罗斯托夫伯爵(?!夫人)", "countess_r": r"罗斯托夫伯爵夫人",
    "natasha": r"娜塔莎", "nikolai": r"尼古拉(?!·安德烈)", "vera": r"薇拉",
    "petya": r"彼嘉", "sophia": r"宋尼雅",
    "old_prince": r"保尔康斯基公爵(?!小姐)|老公爵(?!夫人)",
    "andrei": r"安德烈(?!·)", "marya": r"玛丽雅", "liza": r"小公爵夫人|丽莎(?!·)",
    "nikolushka": r"小尼古拉",
    "vasily": r"华西里公爵", "helen": r"海伦", "anatole": r"阿纳托里",
    "hippolyte": r"伊波利特", "kuragina": r"华西里公爵夫人",
    "anna_mikh": r"德鲁别茨基公爵夫人|安娜·米哈伊洛夫娜", "boris": r"保里斯",
    "kutuzov": r"库图佐夫", "bagration": r"巴格拉基昂", "denisov": r"杰尼索夫",
    "dolokhov": r"陶洛霍夫", "tushin": r"土申", "nesvitsky": r"聂斯维茨基",
    "bilbin": r"比利平", "zhilinsky": r"吉梁宁", "iljin": r"伊林",
    "napoleon": r"拿破仑|波拿巴", "alexander": r"亚历山大皇帝|亚历山大(?!·)",
    "franz": r"弗朗茨|奥国皇帝", "arakcheev": r"阿拉克切耶夫",
    "speransky": r"斯佩蓝斯基|斯佩兰斯基", "rastopchin": r"拉斯托普庆",
    "murat": r"缪拉", "davout": r"达武|达乌", "barclay": r"巴克莱",
    "volzogen": r"伏尔佐根", "bennigsen": r"别尼生",
    "anna_sherer": r"舍勒", "ahrosimova": r"阿赫罗西莫娃", "bourienne": r"布莉恩",
    "julie": r"裘丽", "berg": r"别尔格", "platon": r"普拉东",
    "bazdeev": r"巴兹杰耶夫", "villarsky": r"维拉尔斯基", "alpatych": r"阿尔巴端奇",
    "mativier": r"梅蒂维埃", "mikhail": r"米哈伊尔·伊凡内奇", "rossaw": r"让理夫人",
    "balaga": r"巴拉加", "tihon": r"季洪", "lavrushka": r"拉夫鲁施卡",
    "linguist": r"仑巴尔",
}

# 地点 -> 正文匹配正则（只列可辨识的专名；庄园/城市/战场）
PLACE_PAT = {
    "童山": r"童山", "奥特拉德诺耶": r"奥特拉德诺耶", "保古察罗伏": r"保古察罗伏",
    "彼得堡": r"彼得堡", "莫斯科": r"莫斯科", "维也纳": r"维也纳",
    "布劳瑙": r"布劳瑙", "布尔诺": r"布尔诺", "奥尔米茨": r"奥尔米茨",
    "维尔诺": r"维尔诺", "斯摩棱斯克": r"斯摩棱斯克", "沃罗涅日": r"沃罗涅日",
    "雅罗斯拉夫尔": r"雅罗斯拉夫尔", "奥廖尔": r"奥廖尔", "梁赞": r"梁赞",
    "卡卢加": r"卡卢加", "图拉": r"图拉", "蒂尔西特": r"蒂尔西特",
    "埃尔富特": r"埃尔富特", "德累斯顿": r"德累斯顿", "华沙": r"华沙",
    "申格拉本": r"申格拉本", "奥斯特里茨": r"奥斯特里茨", "霍拉勃隆": r"霍拉勃隆",
    "恩斯河": r"恩斯河", "克雷姆斯": r"克雷姆斯", "普尔土斯克": r"普尔土斯克",
    "埃劳": r"埃劳", "弗里德兰": r"弗里德兰", "奥斯特罗夫诺": r"奥斯特罗夫诺",
    "鲍罗金诺": r"鲍罗金诺", "舍瓦尔季诺": r"舍瓦尔季诺", "塔鲁季诺": r"塔鲁季诺",
    "小雅罗斯拉韦茨": r"小雅罗斯拉韦茨", "克拉斯诺耶": r"克拉斯诺耶",
    "别列津纳": r"别列津纳", "维亚兹马": r"维亚兹马",
    "德里萨": r"德里萨", "波克朗山": r"波克朗山", "菲里": r"菲里",
    "梅基希": r"梅基希",
}
CN = {"〇": 0, "零": 0, "○": 0, "一": 1, "二": 2, "三": 3, "四": 4,
      "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}


def find_year(text):
    """取正文首个明确年份（一八XX年），带月份"""
    m = re.search(r"一八([〇零○一二三四五六七八九]{2})年", text[:400])
    if not m:
        return None, None
    y = 1800 + int("".join(str(CN[c]) for c in m.group(1)))
    mon = None
    mm = re.search(r"[一二三四五六七八九十]{1,2}月", text[max(0, m.start() - 80):m.end() + 120])
    if mm:
        mon = cn_month(mm.group(0))
    return y, mon


def cn_month(s):
    s = s.replace("月", "")
    if s == "十":
        return 10
    if s == "十一":
        return 11
    if s == "十二":
        return 12
    if "十" in s:
        a, b = s.split("十")
        return (CN.get(a, 1) if a else 1) * 10 + (CN.get(b, 0) if b else 0)
    return CN.get(s)


def load_notes():
    """读取人工稿的唯一来源 data/proposals/notes_*.py；返回 (notes, 来源文件名)。

    导入失败或章节 id 重复都直接非零退出：不静默退回空表，也不冒充人工稿。
    """
    notes, sources = {}, []
    for f in sorted(PROP.glob("notes_*.py")):
        spec = importlib.util.spec_from_file_location("notes_" + f.stem, f)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            raise SystemExit("✗ %s 导入失败：%s" % (f.name, e))
        rows = getattr(mod, "NOTES", None)
        if not isinstance(rows, dict):
            raise SystemExit("✗ %s 缺 NOTES 字典" % f.name)
        dup = sorted(set(rows) & set(notes))
        if dup:
            raise SystemExit("✗ 章节 id 在多个提案中重复：%s（%s）" % (dup[:5], f.name))
        notes.update(rows)
        sources.append(f.name)
    return notes, sources


def main():
    try:
        out_arg, rest = jsio.option(sys.argv[1:], "--output")
    except jsio.JsDataError as e:
        raise SystemExit("✗ %s" % e)
    unknown = [a for a in rest if a.startswith("-")]
    if unknown:
        raise SystemExit("✗ 未知参数：%s（本脚本只做初始化，没有 --force）" % unknown)

    target = pathlib.Path(out_arg) if out_arg else OUT
    try:
        jsio.refuse_existing(
            target,
            "本脚本只做显式初始化（没有 --force）；日常更新请用 merge_proposals.js（增量、幂等）。")
    except jsio.JsDataError as e:
        raise SystemExit("✗ %s" % e)

    files = sorted(CH.glob("*.txt"))
    if len(files) != 361:
        raise SystemExit("✗ 语料 %d 章 != 361，请先跑 corpus_extract.py" % len(files))
    notes, sources = load_notes()

    chpat = {k: re.compile(v) for k, v in CHAR_PAT.items()}
    plpat = {k: re.compile(v) for k, v in PLACE_PAT.items()}

    rows = []
    for i, f in enumerate(files, 1):
        cid = f.stem
        book, part, ch = (int(x) for x in cid.split("-"))
        text = f.read_text(encoding="utf-8")
        chars = sorted(k for k, rx in chpat.items() if rx.search(text))
        places = [(k, len(rx.findall(text))) for k, rx in plpat.items() if rx.search(text)]
        places.sort(key=lambda x: -x[1])
        place = places[0][0] if places else None
        year, month = find_year(text)
        n = notes.get(cid, {})
        rows.append({
            "id": cid, "book": book, "part": part, "ch": ch, "seq": i,
            "year": n.get("year", year), "month": n.get("month", month),
            "tag": n.get("tag"), "place": n.get("place", place),
            "chars": n.get("chars", chars),
            "gist": n.get("gist"),
            "flag": None if n.get("gist") else "verify",
        })

    lines = [
        "// data/chapters.js — 全书 361 张章节卡（初始化候选）",
        "// 事件关联不在章节卡上维护：唯一关联源是 data/events.js 的 EVENTS[].ch。",
    ]
    if sources:
        lines.append("// 初始化产物：gist 来自 %s（%d 条）；正式数据以 merge_proposals.js 的合入结果为准。"
                     % (", ".join(sources), sum(1 for r in rows if r["gist"])))
    else:
        lines.append("// ⚠ 骨架（初始化）：data/proposals/notes_*.py 缺失或为空，gist 全为 null、flag:\"verify\"；")
        lines.append("//   这不是对人工稿的安全重建。正式内容须由 merge_proposals.js 从人工稿合入。")
    lines.append("const CHAPTERS = [")
    for r in rows:
        lines.append("  " + jsio.render_chapter(r) + ",")
    lines += ["];", "", 'if (typeof module !== "undefined") module.exports = { CHAPTERS };', ""]

    text = "\n".join(lines)
    try:
        jsio.assert_const_text(text, "CHAPTERS", {r["id"]: {"id": r["id"]} for r in rows})
    except jsio.JsDataError as e:
        raise SystemExit("✗ 生成结果校验失败，未写入：%s" % e)
    jsio.atomic_write(target, text, create=True)

    have = sum(1 for r in rows if r["gist"])
    kind = "初始化候选（含人工稿 gist）" if sources else "骨架（无人工稿）"
    print("✓ %d 张章节卡 → %s（%s）" % (len(rows), target, kind))
    print("  含自撰 gist：%d／%d（待补 %d）" % (have, len(rows), len(rows) - have))
    print("  自动抽取：有年份 %d，有地点 %d，有人物 %d"
          % (sum(1 for r in rows if r["year"]), sum(1 for r in rows if r["place"]),
             sum(1 for r in rows if r["chars"])))
    print("  提示：目标为独立候选文件；正式 data/chapters.js 仍由 merge_proposals.js 维护。")


if __name__ == "__main__":
    main()
