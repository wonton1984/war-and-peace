#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ctx.py — 在语料中按名字查上下文（替代不可靠的 `grep -o`）

**为什么需要这个脚本**
  `grep -o '.{0,40}名字.{0,80}'` 在中文 UTF-8 文本上**不可靠**：
  grep 的 `.` 按字节计数，汉字占 3 字节，40 字节的窗口只能容约 13 个汉字，
  窗口边界切在半个字符上时整条命中会被丢弃 —— 实测前缀有 5..45 个汉字时
  `grep -o` 会**全部返回空**，而 `grep -c` 计数正常（131 行里仍有 1 行命中）。
  误信 `grep -o` 的空输出，就会把「正面出场」误判成「仅被提及」。

用法：
  python3 scripts/ctx.py 基莫兴                  # 全书列出该名的所有上下文
  python3 scripts/ctx.py 基莫兴 3-2-25           # 只看某章
  python3 scripts/ctx.py 基莫兴 --present        # 只输出「疑似正面出场」的行
  python3 scripts/ctx.py 基莫兴 --chapters       # 只输出出现的章 id（一行一个）

判定标签（供 --present 用）：
  [出场] —— 查询人物**本人**在其所在子句里被绑定为动作 / 体态 / 对白的主体，
            如「玛卡尔走进营房」「玛卡尔说：…」「薇拉和申兴在客厅里下棋」；
  [转述] —— 名字只出现在他人的转述、书信、报告框架里（据说 / 来信 / 报告说，
            或处在别人的引号对白内）→ 本人**不在场**，不算出场；
  [待核] —— 既不能确认本人绑定动作、又疑似在场（如同句有对白但名字只是宾语）
            → 需人读原文判定；
  [提及] —— 其余（大致只是被点到名字）。

**绑定原则（重要）**：动作 / 对白必须由**被查询的人**承担才算在场证据。
  「侍女站在门口报告说，远方的玛卡尔病了。」里 站 / 报告 的主语是侍女，
  玛卡尔只是被转述 → 不计出场；「来信说，玛卡尔走进屋。」同理不计。
  子句外的动作一律不认。

**口径（本项目统一定义）**：「出场」= 本人在该场景中**有在场行动或对白**（含静坐在场
如「薇拉和申兴在客厅里下棋」）。**转述旧话、书信问候、他人谈论其心情，均不算出场**。
启发式只作提示，**最终仍须人读原文判定**；宁可标 [待核]，也不升级为 [出场]。
"""
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CH = ROOT / "corpus" / "ch"

# 子句切分：动作绑定只在子句内判定，避免把别的主语的动作算到查询人物头上。
CLAUSE = re.compile(r'[，,。！？；;：:、\n]')
# 身体动作 / 在场体态（不含言说动词；言说另列，需判定「谁在说」）。
BODY = re.compile(r'(走|跑|站|坐|躺|蹲|跪|望|看|瞧|笑|皱眉|听|叹|摇头|点头|鞠躬|敬礼|'
                  r'进来|出去|走上|走近|转身|抬头|低头|伸手|拿起|放下|跟着|来到|跑到|'
                  r'倒在|靠在|握住|抱住|下棋|打牌|喝茶|吃饭|跳舞|唱歌|骑马|读书|写字|'
                  r'缝|弹|唱|斟|端|递|穿|脱|睡|醒)')
# 言说 / 书写动词：只有它们是**查询人物**的动作时才算对白在场。
SPEECH = re.compile(r'(说|说道|问|答|回答|道|喊|叫|嚷|称|写|来信|回信|报告|转告|告诉|宣布|命令)')
QUOTE = re.compile(r'[「“"『]([^」”"』]{1,200})[」”"』]')
# 转述标志：出现即倾向「本人不在场，只是被谈及言行 / 心情」。
REPORTED = re.compile(r'(据说|听说|说是|据传|报告说|来报告|来信|信中|回信|问候|转告|转述|'
                      r'回忆|想起|提到|谈起|说到|他说|她说|说得|称赞|夸奖|议论|'
                      r'该感谢|开玩笑说)')
# 名字紧跟在这些介词 / 动词后时，它是动作的**宾语**而非主语，不能算本人动作。
OBJECT_BEFORE = re.compile(r'(对|向|跟|给|同|和|与|替|为|朝着|转向)$')


def clauses_with(name, sent):
    return [c for c in CLAUSE.split(sent) if name in c]


def is_possessive(name, s, i):
    """名字后紧跟「的」→ 它是修饰语（「吉梁宁的勤务兵」），不是动作主体。"""
    return s[i + len(name): i + len(name) + 1] == "的"


def subject_before(name, clause, verb_re):
    """只把紧随目标主语的动作作为线索，不跨越使役/领属结构寻找别人的动作。"""
    i = clause.find(name)
    if i < 0 or is_possessive(name, clause, i) or OBJECT_BEFORE.search(clause[:i]):
        return False
    tail = clause[i + len(name):].lstrip()
    return bool(re.match(r"^(?:(?:正在|正|也|又|便|就|仍|忽然|慢慢|缓缓|已经))*"
                         r"(?:在[^，,。！？；;]{1,12})?" + verb_re.pattern, tail))


def speaker_bound(name, sent):
    """名字紧邻言说动词、且不是宾语或修饰语 → 像是说话人本人。"""
    for m in re.finditer(re.escape(name) + r'[^，。！？；：、\n]{0,3}' + SPEECH.pattern, sent):
        i = m.start()
        if is_possessive(name, sent, i):
            continue
        if not OBJECT_BEFORE.search(sent[:i]):
            return True
    return False


def name_in_quote(name, sent):
    return any(name in m.group(1) for m in QUOTE.finditer(sent))


def classify(name, sent):
    pos = sent.find(name)
    in_quote = name_in_quote(name, sent)
    speaker = speaker_bound(name, sent)
    before = sent[:pos]
    reported = bool(REPORTED.search(before)) or bool(SPEECH.search(before))
    body = any(subject_before(name, c, BODY) for c in clauses_with(name, sent))

    if in_quote and not speaker:
        return "转述"                 # 名字只出现在别人的话里
    if REPORTED.search(sent):
        return "待核" if body else "转述"
    if speaker and reported:
        return "待核"                 # 既是说话人、又处在转述框架内 → 模糊
    if speaker:
        return "出场"
    if reported:
        return "转述"                 # 「来信说，X 走进屋」：动作在转述里，不计出场
    if body:
        return "出场"
    if QUOTE.search(sent):
        return "待核"                 # 同句有对白，但无法确认名字参与
    return "提及"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if not args:
        print(__doc__)
        return
    name = args[0]
    only = args[1] if len(args) > 1 else None

    files = sorted(CH.glob("*.txt"))
    if not files:
        raise SystemExit("无语料：corpus/ch/ 为空，请先跑 scripts/corpus_extract.py")

    total, chapter_hits = 0, []
    for f in files:
        cid = f.stem
        if only and cid != only:
            continue
        text = f.read_text(encoding="utf-8")
        if name not in text:
            continue
        chapter_hits.append(cid)
        total += text.count(name)
        if "--chapters" in flags:
            continue
        # 按句切分，逐句判定（比定长窗口可靠）
        for sent in re.split(r'(?<=[。！？；\n])', text):
            if name not in sent:
                continue
            tag = classify(name, sent)
            if "--present" in flags and tag != "出场":
                continue
            s = sent.strip().replace("\n", " ")
            if len(s) > 150:
                # 以名字为中心截取，避免整段刷屏
                i = s.find(name)
                s = ("…" if i > 60 else "") + s[max(0, i - 60): i + 90] + "…"
            print(f"[{cid}][{tag}] {s}")

    if "--chapters" in flags:
        for cid in chapter_hits:
            print(cid)
        return

    print(f"\n— {name}：全书 {total} 次，见于 {len(chapter_hits)} 章")
    print(f"  {' '.join(chapter_hits)}")


if __name__ == "__main__":
    main()
