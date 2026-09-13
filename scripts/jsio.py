#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jsio.py — data/*.js 的最小结构化读写辅助（生成 / 合并 / 同步脚本共用）

设计要点：
  · 解析：把受信任的仓库数据文件交给 node 求值后按 JSON 读入，不对文本猜解；
    记录切分按大括号配平，不依赖行首 / 换行排版（正式数据既有行内字段也有跨行字段）。
  · 写入：临时文件 + os.replace 原子替换，避免半写入；写前用 node 复验语法与字段。
  · 渲染：与 data/*.js 现有书写风格一致的确定性序列化；只重排被改动的记录。

本模块被 build_chapters.py / build_characters.py / merge_events.py /
merge_minor.py / sync_event_summaries.py / sync_minor.py 共用；
受控词表与字数上限与 scripts/lint_data.js、scripts/data_limits.js 保持一致。
"""
import json
import calendar
import os
import pathlib
import re
import subprocess
import tempfile

# ── 受控词表与上限（与 lint_data.js / data_limits.js 对齐） ──
TYPES = ["salon", "family", "ball", "hunt", "battle", "march", "wound",
         "duel", "business", "intrigue", "spirit", "essay"]
FACTIONS = ["bezukhov", "rostov", "bolkonsky", "kuragin", "druzh",
            "russian_army", "french_army", "court", "mason", "folk"]
REL_KINDS = ["kin", "marriage", "courtship", "affair", "friend", "salon",
             "enemy", "service", "patron", "estate"]
TIERS = ["core", "minor"]
CHAPTER_TAGS = ["peace", "war", "essay", "transition"]

# 正式数据字段契约（顺序即序列化顺序；未列入的字段一律显式报错，禁止静默丢弃）
EVENT_ORDER = ["id", "title", "ch", "book", "part", "year", "month", "day",
               "type", "place", "battle", "factions", "chars", "rel", "theme",
               "arc", "summary", "history", "flag"]
CHAR_ORDER = ["id", "name", "full", "aliases", "faction", "family", "born",
              "died", "title", "tier", "bio", "arc", "chapters", "names", "flag"]
CHAPTER_ORDER = ["id", "book", "part", "ch", "seq", "year", "month", "tag",
                 "place", "chars", "gist", "flag"]
# data/*.js 内 `const <NAME> = ...` 的常量名 → 文件名
DATA_CONSTS = {"CHARACTERS": "characters.js", "PLACES": "places.js",
               "THEMES": "themes.js", "ARCS": "arcs.js",
               "CHAPTERS": "chapters.js", "BATTLES": "battles.js"}

QUOTE_RE = re.compile(r'[「“"『]([^」”"』]{1,200})[」”"』]')


class JsDataError(RuntimeError):
    """数据文件读写过程中的可预期错误（调用方打印后应以非零码退出）。"""


# ─────────────────────────── node 求值 ───────────────────────────

def _node(script, stdin=None):
    try:
        r = subprocess.run(["node", "-e", script], input=stdin,
                           capture_output=True, text=True)
    except FileNotFoundError as e:
        raise JsDataError("找不到 node 可执行文件：%s" % e)
    if r.returncode != 0:
        raise JsDataError((r.stderr or r.stdout or "node 求值失败").strip()[:800])
    return r.stdout


# 与 JavaScript 门禁读取同一份上限，避免同步器与 lint 各自维护一套数字。
LIMITS = json.loads(_node("process.stdout.write(JSON.stringify(require(%s)))" %
                         json.dumps(str(pathlib.Path(__file__).with_name("data_limits.js")))))


_LOAD = r'''
const fs = require("fs");
let s = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", d => s += d);
process.stdin.on("end", () => {
  const files = JSON.parse(s);
  const out = {};
  let code = "";
  for (const [p] of files) code += fs.readFileSync(p, "utf8") + "\n";
  for (const [, n] of files) code += "\nout[" + JSON.stringify(n) + "] = " + n + ";";
  try { new Function("out", code)(out); }
  catch (e) { process.stderr.write(String((e && e.message) || e)); process.exit(1); }
  process.stdout.write(JSON.stringify(out));
});
'''

_PARSE = r'''
let s = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", d => s += d);
process.stdin.on("end", () => {
  let v;
  try { v = new Function("return (" + s + ")")(); }
  catch (e) { process.stderr.write(String((e && e.message) || e)); process.exit(1); }
  process.stdout.write(JSON.stringify(v));
});
'''

_VERIFY = r'''
let s = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", d => s += d);
process.stdin.on("end", () => {
  const name = __NAME__, expect = __EXPECT__;
  const canon = v => Array.isArray(v) ? v.map(canon)
    : (v && typeof v === "object")
      ? Object.fromEntries(Object.keys(v).slice().sort().map(k => [k, canon(v[k])]))
      : v;
  let arr;
  try {
    const out = {};
    new Function("out", s + "\nout[" + JSON.stringify(name) + "] = " + name + ";")(out);
    arr = out[name];
  } catch (e) { process.stderr.write("求值失败：" + String((e && e.message) || e)); process.exit(1); }
  if (!Array.isArray(arr)) { process.stderr.write(name + " 不是数组"); process.exit(1); }
  const by = new Map(arr.map(x => [x && x.id, x]));
  if (by.size !== arr.length || arr.some(x => !x || typeof x.id !== "string")) {
    process.stderr.write("记录 id 缺失或重复"); process.exit(1);
  }
  const missing = Object.keys(expect).filter(id => !by.has(id));
  if (missing.length) {
    process.stderr.write("缺少记录：" + missing.slice(0, 5).join(","));
    process.exit(1);
  }
  for (const [id, want] of Object.entries(expect)) {
    const rec = by.get(id);
    for (const [k, v] of Object.entries(want)) {
      if (JSON.stringify(canon(rec[k])) !== JSON.stringify(canon(v))) {
        process.stderr.write(id + "." + k + " 未落地");
        process.exit(1);
      }
    }
  }
  process.stdout.write(String(arr.length));
});
'''


def load_consts(specs):
    """specs: [(path, NAME), …]；用 node 求值受信任的数据文件，返回 {NAME: value}。"""
    payload = json.dumps([[str(p), n] for p, n in specs], ensure_ascii=False)
    return json.loads(_node(_LOAD, payload))


def load_const(path, name):
    return load_consts([(path, name)])[name]


def load_data(root, names=("CHARACTERS", "PLACES", "THEMES", "ARCS", "CHAPTERS", "BATTLES")):
    """载入校验所需的 data/*.js 常量（只读）；缺失的文件按空表处理。"""
    specs = []
    for n in names:
        p = pathlib.Path(root) / "data" / DATA_CONSTS[n]
        if p.exists():
            specs.append((p, n))
    got = load_consts(specs) if specs else {}
    return {n: got.get(n, {} if n == "PLACES" else []) for n in names}


def refs_from(d):
    """把 load_data() 的结果整理成引用校验上下文。"""
    return {
        "chars": {c["id"] for c in d.get("CHARACTERS") or []},
        "places": set(d.get("PLACES") or {}),
        "themes": {t["id"] for t in d.get("THEMES") or []},
        "arcs": {a["who"]: {s["label"] for s in a.get("stages") or []}
                 for a in d.get("ARCS") or []},
        "chapters": {c["id"] for c in d.get("CHAPTERS") or []},
        "battles": {b["id"] for b in d.get("BATTLES") or []},
    }


# ─────────────────────────── 记录切分 ───────────────────────────



def _skip_string(text, i):
    quote = text[i]
    i += 1
    while i < len(text):
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == quote:
            return i + 1
        i += 1
    raise JsDataError("字符串未闭合")


def _scan_object(text, start):
    """从 start 处的 `{` 起按大括号配平，返回整段对象字面量。"""
    depth = 0
    i = start
    while i < len(text):
        c = text[i]
        if c in "\"'`":
            i = _skip_string(text, i)
            continue
        if c == "/" and text[i:i + 2] == "//":
            j = text.find("\n", i)
            i = len(text) if j < 0 else j + 1
            continue
        if c == "/" and text[i:i + 2] == "/*":
            j = text.find("*/", i)
            i = len(text) if j < 0 else j + 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
        i += 1
    raise JsDataError("对象字面量未闭合")


def parse_records(text):
    """返回数组起止偏移和记录跨度；id 由 Node 解析，不依赖字段顺序或引号风格。"""
    spans, start, depth, i = [], None, 0, 0
    while i < len(text):
        c = text[i]
        if c in "\"'`":
            i = _skip_string(text, i)
            continue
        if text.startswith("//", i):
            j = text.find("\n", i)
            i = len(text) if j < 0 else j + 1
            continue
        if text.startswith("/*", i):
            j = text.find("*/", i + 2)
            if j < 0:
                raise JsDataError("注释未闭合")
            i = j + 2
            continue
        if c == "[":
            if start is None:
                start = i
            depth += 1
        elif c == "]" and start is not None:
            depth -= 1
            if depth == 0:
                records = json.loads(_node(_PARSE, text[start:i + 1]))
                if len(records) != len(spans):
                    raise JsDataError("记录数组必须由对象字面量组成")
                result, seen = [], set()
                for (a, b, raw), rec in zip(spans, records):
                    if not isinstance(rec, dict) or not isinstance(rec.get("id"), str):
                        raise JsDataError("记录缺字符串 id")
                    if rec["id"] in seen:
                        raise JsDataError("记录 id 重复：" + rec["id"])
                    seen.add(rec["id"])
                    result.append((a, b, rec["id"], raw))
                return start, i, result
        elif c == "{" and depth == 1:
            raw = _scan_object(text, i)
            end = i + len(raw)
            spans.append((i, end, raw))
            i = end
            continue
        i += 1
    raise JsDataError("未找到完整记录数组")


def parse_object(raw):
    """把单条对象字面量交给 node 求值，返回 dict。"""
    return json.loads(_node(_PARSE, raw))


# ─────────────────────────── 写入 ───────────────────────────

def atomic_write(path, text, *, create=False):
    """先完整写临时文件；初始化用原子建链拒绝覆盖，更新用原子替换。"""
    path = pathlib.Path(path)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix="." + path.name + ".",
                               suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        if create:
            os.link(tmp, path)  # 即使预检查后有其他写入者，也不会覆盖对方文件。
            os.unlink(tmp)
        else:
            os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def assert_const_text(text, name, expect=None):
    """用 node 复验整段文本：`const NAME` 可求值、为数组，且 expect={id:{字段:值}} 已落地。

    返回数组长度；任一项不满足即抛 JsDataError（调用方据此非零退出且不落盘）。
    """
    script = (_VERIFY.replace("__NAME__", json.dumps(name))
                      .replace("__EXPECT__", json.dumps(expect or {}, ensure_ascii=False)))
    return int(_node(script, text))


def refuse_existing(path, hint=""):
    """目标已存在即抛错：生成器只做显式初始化，没有 --force。"""
    p = pathlib.Path(path)
    if p.exists() or p.is_symlink():
        raise JsDataError("目标已存在，拒绝覆盖：%s%s" % (p, ("\n  " + hint) if hint else ""))
    if not p.parent.exists():
        raise JsDataError("目标目录不存在：%s" % p.parent)


def option(argv, name):
    """取 `--name VALUE` / `--name=VALUE`，返回 (value|None, 其余参数)。

    缺值、空值或以 `-` 开头的值一律报错，避免把下一个开关当成路径。
    """
    rest, val = [], None

    def check(v):
        if not v or v.startswith("-"):
            raise JsDataError("%s 缺参数值" % name)
        return v

    i = 0
    while i < len(argv):
        a = argv[i]
        if a == name:
            if i + 1 >= len(argv):
                raise JsDataError("%s 缺参数值" % name)
            val = check(argv[i + 1])
            i += 2
            continue
        if a.startswith(name + "="):
            val = check(a[len(name) + 1:])
            i += 1
            continue
        rest.append(a)
        i += 1
    return val, rest


# ─────────────────────────── 校验 ───────────────────────────

def text_len(s):
    return len(s) if isinstance(s, str) else 0


def quote_span(s):
    """最长引号内片段长度（版权门禁，与 lint_data.js 一致）。"""
    return max((len(m.group(1)) for m in QUOTE_RE.finditer(s)), default=0) if isinstance(s, str) else 0


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def validate_event(rec, refs):
    """事件记录的类型 / 受控词表 / 引用完整性校验；返回问题列表（空 = 通过）。"""
    p = []
    rid = rec.get("id")
    if not isinstance(rid, str) or not re.fullmatch(r"e-[a-z0-9-]+", rid):
        p.append("id 非法 %r" % (rid,))
    for k in rec:
        if k not in EVENT_ORDER:
            p.append("未知字段 %r（须显式加入契约，拒绝静默丢弃）" % (k,))
    if not isinstance(rec.get("title"), str) or not rec.get("title"):
        p.append("缺 title")
    ch = rec.get("ch")
    if not isinstance(ch, list) or not all(isinstance(x, str) for x in ch):
        p.append("ch 类型错误（应为字符串数组）")
    else:
        p += ["ch 不存在 %r" % x for x in ch if x not in refs["chapters"]]
    for k in ("book", "part"):
        if not _is_int(rec.get(k)):
            p.append("%s 应为整数" % k)
    for k, lo, hi in (("year", 1000, 3000), ("month", 1, 12), ("day", 1, 31)):
        if k not in rec:
            continue
        v = rec[k]
        if v is None:
            continue
        if not _is_int(v):
            p.append("%s 应为整数或 null" % k)
        elif not lo <= v <= hi:
            p.append("%s 越界 %r" % (k, v))
    day, month, year = rec.get("day"), rec.get("month"), rec.get("year")
    if day is not None:
        if month is None:
            p.append("day 缺少 month")
        elif (_is_int(day) and _is_int(month) and 1 <= month <= 12
              and (year is None or _is_int(year))):
            if day > calendar.monthrange(year if year is not None else 2000, month)[1]:
                p.append("day 超出该年月的天数")
    if rec.get("type") not in TYPES:
        p.append("type 越界 %r" % (rec.get("type"),))
    place = rec.get("place")
    if place is not None and place not in refs["places"]:
        p.append("place 不存在 %r" % (place,))
    battle = rec.get("battle")
    if battle is not None and battle not in refs["battles"]:
        p.append("battle 不存在 %r" % (battle,))
    for k, allowed in (("factions", FACTIONS), ("theme", refs["themes"]),
                       ("chars", refs["chars"])):
        v = rec.get(k)
        if v is None:
            continue
        if not isinstance(v, list):
            p.append("%s 类型错误（应为数组）" % k)
            continue
        for x in v:
            if not isinstance(x, str) or (allowed and x not in allowed):
                p.append("%s 引用不存在 %r" % (k, x))
    for k in ("rel", "arc"):
        v = rec.get(k)
        if v is None:
            continue
        if not isinstance(v, list):
            p.append("%s 类型错误（应为数组）" % k)
            continue
        for i, x in enumerate(v):
            if not isinstance(x, dict):
                p.append("%s[%d] 类型错误" % (k, i))
                continue
            if k == "rel":
                if x.get("a") not in refs["chars"] or x.get("b") not in refs["chars"]:
                    p.append("rel[%d] 人物不存在 %r/%r" % (i, x.get("a"), x.get("b")))
                if x.get("kind") not in REL_KINDS:
                    p.append("rel[%d].kind 越界 %r" % (i, x.get("kind")))
                if "delta" in x and x["delta"] is not None and not isinstance(x["delta"], str):
                    p.append("rel[%d].delta 应为字符串或 null" % i)
            else:
                who = x.get("who")
                if who not in refs["chars"]:
                    p.append("arc[%d] 人物不存在 %r" % (i, who))
                elif who in refs["arcs"] and x.get("stage") not in refs["arcs"][who]:
                    p.append("arc[%d].stage %r 不在 %s 的弧光中" % (i, x.get("stage"), who))
    s = rec.get("summary")
    if not isinstance(s, str) or not s:
        p.append("缺 summary")
    else:
        if text_len(s) > LIMITS["summary"]:
            p.append("summary %d 字 > %d" % (text_len(s), LIMITS["summary"]))
        if quote_span(s) > LIMITS["quoteSpan"]:
            p.append("summary 含 >%d 字引文" % LIMITS["quoteSpan"])
    h = rec.get("history")
    if h is not None:
        if not isinstance(h, str):
            p.append("history 应为字符串或 null")
        elif text_len(h) > LIMITS["history"]:
            p.append("history %d 字 > %d" % (text_len(h), LIMITS["history"]))
    flag = rec.get("flag")
    if flag is not None and not isinstance(flag, str):
        p.append("flag 应为字符串或 null")
    return p


def validate_character(rec, refs):
    """人物记录的类型 / 受控词表 / 引用完整性校验；返回问题列表（空 = 通过）。"""
    p = []
    rid = rec.get("id")
    if not isinstance(rid, str) or not re.fullmatch(r"[a-z0-9_]+", rid):
        p.append("id 非法 %r" % (rid,))
    for k in rec:
        if k not in CHAR_ORDER:
            p.append("未知字段 %r（须显式加入契约，拒绝静默丢弃）" % (k,))
    if not isinstance(rec.get("name"), str) or not rec.get("name"):
        p.append("缺 name")
    if rec.get("faction") not in FACTIONS:
        p.append("faction 越界 %r" % (rec.get("faction"),))
    if rec.get("tier") not in TIERS:
        p.append("tier 越界 %r" % (rec.get("tier"),))
    for k in ("aliases", "chapters"):
        v = rec.get(k)
        if v is None:
            continue
        if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
            p.append("%s 类型错误（应为字符串数组）" % k)
            continue
        if k == "chapters":
            p += ["chapters 含不存在的章 %r" % x for x in v if x not in refs["chapters"]]
    for k in ("full", "family", "title", "arc", "flag"):
        v = rec.get(k)
        if v is not None and not isinstance(v, str):
            p.append("%s 应为字符串或 null" % k)
    for k in ("born", "died"):
        v = rec.get(k)
        if v is not None and not _is_int(v):
            p.append("%s 应为整数或 null" % k)
    bio = rec.get("bio")
    if not isinstance(bio, str):
        p.append("bio 应为字符串")
    else:
        if text_len(bio) > LIMITS["bio"]:
            p.append("bio %d 字 > %d" % (text_len(bio), LIMITS["bio"]))
        if quote_span(bio) > LIMITS["quoteSpan"]:
            p.append("bio 含 >%d 字引文" % LIMITS["quoteSpan"])
    names = rec.get("names")
    if names is not None and not isinstance(names, dict):
        p.append("names 应为对象")
    return p


# ─────────────────────────── 序列化 ───────────────────────────

def _str(v):
    return "null" if v is None else json.dumps(v, ensure_ascii=False)


def _num(v):
    if v is None:
        return "null"
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise JsDataError("数字字段类型错误：%r" % (v,))
    return json.dumps(v)


def _arr(v):
    """events.js 风格的紧凑数组（JSON.stringify 形式）。"""
    return json.dumps([] if v is None else v, ensure_ascii=False,
                      separators=(",", ":"))


def _value(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return json.dumps(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    return json.dumps(v, ensure_ascii=False)


def _inline_obj(x):
    items = []
    for k, v in x.items():
        key = k if re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", k) else json.dumps(k)
        items.append("%s:%s" % (key, _value(v)))
    return "{ " + ", ".join(items) + " }"


def _render_rel(items):
    items = items or []
    if not items:
        return "    rel:[],"
    if len(items) == 1:
        return "    rel:[ " + _inline_obj(items[0]) + " ],"
    return "    rel:[ " + ",\n          ".join(_inline_obj(x) for x in items) + " ],"


def _render_arc(items):
    items = items or []
    if not items:
        return "[]"
    return "[ " + ", ".join(_inline_obj(x) for x in items) + " ]"


def render_event(rec):
    """渲染事件记录（events.js 风格的多行字面量，不含行首缩进与尾随逗号）。"""
    extra = [k for k in rec if k not in EVENT_ORDER]
    lines = []
    head = ["id:" + _str(rec.get("id"))]
    if "battle" in rec:                       # 与正式数据的书写位置一致：battle 紧随 id
        head.append("battle:" + _str(rec["battle"]))
    if "title" in rec:
        head.append("title:" + _str(rec["title"]))
    if "ch" in rec:                           # 与正式数据多数写法一致：ch 紧随标题
        head.append("ch:" + _arr(rec["ch"]))
    lines.append("{ " + ", ".join(head) + ",")
    meta = ["%s:%s" % (k, _num(rec[k])) for k in ("book", "part", "year", "month", "day")
            if k in rec]
    meta += ["%s:%s" % (k, _str(rec[k])) for k in ("type", "place") if k in rec]
    if meta:
        lines.append("    " + ", ".join(meta) + ",")
    pair = ["%s:%s" % (k, _arr(rec[k])) for k in ("factions", "chars") if k in rec]
    if pair:
        lines.append("    " + ", ".join(pair) + ",")
    if "rel" in rec:
        lines.append(_render_rel(rec["rel"]))
    ta = []
    if "theme" in rec:
        ta.append("theme:" + _arr(rec["theme"]))
    if "arc" in rec:
        ta.append("arc:" + _render_arc(rec["arc"]))
    if ta:
        lines.append("    " + ", ".join(ta) + ",")
    if "summary" in rec:
        lines.append("    summary:" + _str(rec["summary"]) + ",")
    tail = ["%s:%s" % (k, _str(rec[k])) for k in ("history", "flag") if k in rec]
    tail += ["%s:%s" % (k, _value(rec[k])) for k in extra]
    lines.append("    " + (", ".join(tail) + " }" if tail else "}"))
    return "\n".join(lines)


def render_character(rec):
    """渲染人物记录（characters.js 风格的单行字面量，不含行首缩进与尾随逗号）。"""
    parts = ["%s:%s" % (k, _value(rec[k])) for k in CHAR_ORDER if k in rec]
    parts += ["%s:%s" % (k, _value(rec[k])) for k in rec if k not in CHAR_ORDER]
    return "{ " + ", ".join(parts) + " }"


def render_chapter(rec):
    """渲染章节卡（chapters.js 风格，JSON.stringify 紧凑形式；不含 event 字段）。"""
    parts = []
    for k in CHAPTER_ORDER:
        if k not in rec:
            continue
        v = rec[k]
        if k == "id":
            parts.append("id:" + _str(v))
        elif k in ("book", "part", "ch", "seq", "year", "month"):
            parts.append("%s:%s" % (k, _num(v)))
        elif k == "chars":
            parts.append("chars:" + _arr(v))
        else:
            parts.append("%s:%s" % (k, _str(v)))
    for k in rec:
        if k not in CHAPTER_ORDER and k != "event":   # event 为已删除的遗留字段
            parts.append("%s:%s" % (k, _value(rec[k])))
    return "{ " + ", ".join(parts) + " }"
