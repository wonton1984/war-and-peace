#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_pipeline.py — 数据管线的针对性回归测试

覆盖（全程在临时副本里跑，绝不改正式 data/）：
  · 生成器是显式初始化：默认目标存在 → 非零退出且不改一字；--output 只写新文件。
  · 事件同步按结构多字段落地（title/year/chars/summary/day/battle），
    未指定字段与未命中记录保持语义不变；转义引号不损坏 JS。
  · merge 保留 day / battle；章节卡不再序列化遗留 event 字段。
  · 未知目标 id / 重复提案 id / 导入失败一律非零退出且不落盘。

用法：python3 scripts/test_pipeline.py
"""
import hashlib
import json
import os
import runpy
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
PY = sys.executable
FAILED = []

EVENT_FIELDS = ["id", "title", "ch", "book", "part", "year", "month", "day",
                "type", "place", "battle", "factions", "chars", "rel", "theme",
                "arc", "summary", "history", "flag"]


def check(ok, label):
    print(("  ✓ " if ok else "  ✗ ") + label)
    if not ok:
        FAILED.append(label)


def run(tmp, argv):
    r = subprocess.run(argv, cwd=str(tmp), capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def load_js(tmp, rel, name):
    script = ('const NM=%s,fs=require("fs"),o={};'
              'new Function("out",fs.readFileSync(process.argv[1],"utf8")+'
              '"\\nout."+NM+"="+NM+";")(o);'
              'process.stdout.write(JSON.stringify(o[NM]));' % json.dumps(name))
    r = subprocess.run(["node", "-e", script, str(tmp / rel)], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[:400])
    return json.loads(r.stdout)


def digest(path):
    return hashlib.md5(pathlib.Path(path).read_bytes()).hexdigest()


def write_prop(tmp, name, record):
    p = tmp / "data" / "proposals" / name
    p.write_text("# -*- coding: utf-8 -*-\nEVENTS_PROPOSAL = [%r]\n" % (record,), encoding="utf-8")
    return p


def main():
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="wp_pipeline_test_"))
    try:
        shutil.copytree(ROOT / "scripts", tmp / "scripts",
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(ROOT / "data", tmp / "data")
        has_corpus = (ROOT / "corpus" / "ch").is_dir()
        if has_corpus:
            os.symlink(str(ROOT / "corpus"), str(tmp / "corpus"))

        chapters, chars, events = (tmp / "data" / n for n in
                                   ("chapters.js", "characters.js", "events.js"))

        print("[生成器：显式初始化]")
        h1, h2 = digest(chapters), digest(chars)
        rc, _ = run(tmp, [PY, "scripts/build_chapters.py"])
        check(rc != 0 and digest(chapters) == h1, "默认 build_chapters 拒绝覆盖且不改文件")
        rc, _ = run(tmp, [PY, "scripts/build_characters.py"])
        check(rc != 0 and digest(chars) == h2, "默认 build_characters 拒绝覆盖且不改文件")
        out = tmp / "out_chapters.js"
        rc, txt = run(tmp, [PY, "scripts/build_chapters.py", "--output", str(out)])
        if has_corpus:
            check(rc == 0 and out.exists(), "build_chapters --output 生成独立候选")
            cards = load_js(tmp, "out_chapters.js", "CHAPTERS")
            check(len(cards) == 361 and not any("event" in c for c in cards),
                  "候选可加载、361 张卡且无 event 字段")
            rc, _ = run(tmp, [PY, "scripts/build_chapters.py", "--output", str(out)])
            check(rc != 0, "--output 拒绝覆盖已有文件（无 --force）")
        else:
            check(rc != 0, "无 corpus 时 build_chapters 明确失败（跳过候选检查）")
        check(digest(chapters) == h1, "生成器全程未改动正式 chapters.js")
        helpers = runpy.run_path(str(tmp / "scripts/jsio.py"))
        race_target = tmp / "racing-output.js"
        helpers["refuse_existing"](race_target)
        race_target.write_text("另一写入者的数据", encoding="utf-8")
        refused = False
        try:
            helpers["atomic_write"](race_target, "不应覆盖", create=True)
        except FileExistsError:
            refused = True
        check(refused and race_target.read_text() == "另一写入者的数据",
              "初始化预检查后出现其他写入者，仍拒绝覆盖")

        print("[事件同步：结构化多字段 + 字段保留]")
        old_events = load_js(tmp, "data/events.js", "EVENTS")
        first = old_events[0]
        char_id = load_js(tmp, "data/characters.js", "CHARACTERS")[0]["id"]
        battle_id = load_js(tmp, "data/battles.js", "BATTLES")[0]["id"]
        title = 'AUDIT "引号" \\ 反斜杠'
        summary = 'AUDIT_SUMMARY 修订与转义：\\ "q" 「内引号」。'
        prop = write_prop(tmp, "events_zz_regress.py", {
            "id": first["id"], "title": title, "year": 1807, "chars": [char_id],
            "day": 16, "battle": battle_id, "summary": summary})
        rc, txt = run(tmp, [PY, "scripts/sync_event_summaries.py"])
        check(rc == 0, "sync_event_summaries 成功")
        now = load_js(tmp, "data/events.js", "EVENTS")
        got = [e for e in now if e["id"] == first["id"]][0]
        check(got["title"] == title and got.get("day") == 16 and got.get("battle") == battle_id
              and got["year"] == 1807 and got["chars"] == [char_id] and got["summary"] == summary,
              "title/year/chars/day/battle/summary 全部落地（含转义引号）")
        changed = [k for k in EVENT_FIELDS if first.get(k) != got.get(k)]
        check(sorted(changed) == sorted(["title", "year", "chars", "day", "battle", "summary"]),
              "改动字段恰为提案显式指定：%s" % changed)
        rest_now = [e for e in now if e["id"] != first["id"]]
        rest_old = [e for e in old_events if e["id"] != first["id"]]
        check(rest_now == rest_old, "未命中记录语义不变")
        prop.unlink()
        events.write_text('// 示例不是记录：{ id:"phantom" }\nconst EVENTS = ' +
                          json.dumps(now, ensure_ascii=False) + ";", encoding="utf-8")
        reformatted = write_prop(tmp, "events_zz_format.py", {
            "summary": "字段重新排版后仍正确同步。", "id": first["id"]})
        rc, txt = run(tmp, [PY, "scripts/sync_event_summaries.py"])
        now = load_js(tmp, "data/events.js", "EVENTS")
        check(rc == 0 and next(e for e in now if e["id"] == first["id"])["summary"]
              == "字段重新排版后仍正确同步。", "带引号字段名和注释示例不影响记录识别")
        reformatted.unlink()

        print("[merge：保留 day / battle]")
        chapter_id = load_js(tmp, "data/chapters.js", "CHAPTERS")[0]["id"]
        new_rec = {"id": "e-zz-regress", "title": "AUDIT 新增", "ch": [chapter_id],
                   "book": 1, "part": 1, "year": 1805, "month": 11, "day": 16,
                   "type": "battle", "place": None, "battle": battle_id,
                   "factions": [], "chars": [], "rel": [], "theme": [], "arc": [],
                   "summary": "AUDIT.", "history": None, "flag": None}
        prop2 = write_prop(tmp, "events_zz_regress2.py", new_rec)
        rc, txt = run(tmp, [PY, "scripts/merge_events.py"])
        check(rc == 0, "merge_events 追加成功")
        merged = load_js(tmp, "data/events.js", "EVENTS")
        rec = [e for e in merged if e["id"] == "e-zz-regress"][0]
        check(rec["day"] == 16 and rec["battle"] == battle_id, "新增事件写入 day / battle")
        check([e for e in merged if e["id"] != "e-zz-regress"] == now,
              "新增事件后所有既有记录完整保留")
        prop2.unlink()
        bad = dict(new_rec, id="e-zz-bad", battle="b-nope")
        prop3 = write_prop(tmp, "events_zz_bad.py", bad)
        before = digest(events)
        rc, txt = run(tmp, [PY, "scripts/merge_events.py"])
        check(rc != 0 and digest(events) == before, "无效 battle 引用非零退出且不落盘")
        prop3.unlink()
        bad_date = write_prop(tmp, "events_zz_bad_date.py",
                              dict(new_rec, id="e-zz-bad-date", year=1805, month=2, day=30))
        before = digest(events)
        rc, txt = run(tmp, [PY, "scripts/merge_events.py"])
        check(rc != 0 and digest(events) == before, "不存在的日历日期不落盘")
        bad_date.unlink()

        print("[同步：未知目标 / 重复 id / 导入失败]")
        p = write_prop(tmp, "events_zz_unknown.py", {"id": "e-no-such-event", "summary": "X"})
        before = digest(events)
        rc, txt = run(tmp, [PY, "scripts/sync_event_summaries.py"])
        check(rc != 0 and digest(events) == before, "未知目标 id 非零退出且不落盘")
        p.unlink()
        p1 = write_prop(tmp, "events_zz_dup1.py", {"id": "e-zz-regress", "summary": "A"})
        p2 = write_prop(tmp, "events_zz_dup2.py", {"id": "e-zz-regress", "summary": "B"})
        before = digest(events)
        rc, txt = run(tmp, [PY, "scripts/sync_event_summaries.py"])
        check(rc != 0 and digest(events) == before, "重复提案 id 非零退出且不落盘")
        p1.unlink()
        p2.unlink()
        broken = tmp / "data" / "proposals" / "events_zz_broken.py"
        broken.write_text("# -*- coding: utf-8 -*-\nEVENTS_PROPOSAL = [ oops\n", encoding="utf-8")
        before = digest(events)
        rc, txt = run(tmp, [PY, "scripts/sync_event_summaries.py"])
        check(rc != 0 and digest(events) == before, "导入失败非零退出且不落盘")
        broken.unlink()

        print("[章节卡：不再序列化 event]")
        before_gist = {c["id"]: c["gist"] for c in load_js(tmp, "data/chapters.js", "CHAPTERS")}
        rc, txt = run(tmp, ["node", "scripts/merge_proposals.js"])
        cards = load_js(tmp, "data/chapters.js", "CHAPTERS")
        check(rc == 0 and len(cards) == 361, "merge_proposals 落盘成功")
        check(not any("event" in c for c in cards), "章节卡不再包含 event 字段")
        check({c["id"]: c["gist"] for c in cards} == before_gist, "人工 gist 内容完整保留")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if FAILED:
        print("✗ %d 项失败：" % len(FAILED))
        for f in FAILED:
            print("  " + f)
        sys.exit(1)
    print("✓ 数据管线回归测试全部通过")


if __name__ == "__main__":
    main()
