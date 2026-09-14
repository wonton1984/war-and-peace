#!/usr/bin/env python3
"""Deterministic regressions for structural gates and conservative presence hints."""
import json
import pathlib
import runpy
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent


class GuardRegressions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="wp-guard-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        shutil.copytree(ROOT / "scripts", self.root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(ROOT / "data", self.root / "data", ignore=shutil.ignore_patterns("proposals"))
        shutil.copy2(ROOT / "index.html", self.root / "index.html")

    def run_script(self, name):
        executable = "node" if name.endswith(".js") else "python3"
        return subprocess.run([executable, str(self.root / "scripts" / name)],
                              capture_output=True, text=True, cwd=self.root)

    def mutate_data(self, filename, symbol, mutation):
        code = ("const fs=require('fs'),vm=require('vm');const file=process.argv[1];"
                "const ctx={};vm.runInNewContext(fs.readFileSync(file,'utf8')+"
                + json.dumps(";out=" + symbol) + ",ctx);const rows=ctx.out;" + mutation + ";"
                "fs.writeFileSync(file," + json.dumps("const " + symbol + " = ")
                + "+JSON.stringify(rows)+';');")
        subprocess.run(["node", "-e", code, str(self.root / "data" / filename)], check=True)

    def test_dangling_event_is_rejected_even_without_corpus(self):
        self.mutate_data("relations.js", "RELATIONS", "rows[0].phases[0].ev='e-no-such-event'")
        for name in ["lint_data.js", "trust_guard.js", "smoke_data.js"]:
            result = self.run_script(name)
            self.assertNotEqual(result.returncode, 0, name + " accepted a dangling event")

    def test_invalid_battle_and_calendar_date_are_rejected(self):
        for mutation in ["rows[0].battle='b-no-such-battle'", "rows[0].month=2;rows[0].day=30"]:
            original = (ROOT / "data/events.js").read_text()
            (self.root / "data/events.js").write_text(original)
            self.mutate_data("events.js", "EVENTS", mutation)
            result = self.run_script("lint_data.js")
            self.assertNotEqual(result.returncode, 0, mutation)

    def test_gist_structural_error_is_not_success(self):
        self.mutate_data("chapters.js", "CHAPTERS", "rows[0].gist='x'")
        result = self.run_script("check_gists.py")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_missing_corpus_is_distinct_from_pass(self):
        for name in ["check_gists.py", "check_names.py"]:
            result = self.run_script(name)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_background_missing_or_invalid_is_rejected(self):
        original = (self.root / "data/background.js").read_text()
        for mutation in [
            "delete rows.topics",
            "rows.timeline={}",
            "rows.sources=[null]",
            "rows.topics[0].reading=''",
            "rows.timeline[0].year=1804",
            "rows.timeline[0].year='1805'",
            "rows.sources[0].url='javascript:alert(1)'",
        ]:
            with self.subTest(mutation=mutation):
                (self.root / "data/background.js").write_text(original)
                self.mutate_data("background.js", "ERA_BACKGROUND", mutation)
                result = self.run_script("lint_data.js")
                self.assertNotEqual(result.returncode, 0, mutation)
                self.assertIn("ERA_BACKGROUND", result.stdout + result.stderr)
        (self.root / "data/background.js").unlink()
        for name in ["lint_data.js", "smoke_data.js"]:
            self.assertNotEqual(self.run_script(name).returncode, 0, name)
        (self.root / "data/background.js").write_text("const UNDECLARED_BACKGROUND = {};")
        self.assertNotEqual(self.run_script("smoke_data.js").returncode, 0,
                            "smoke accepted a missing ERA_BACKGROUND symbol")

    def test_unregistered_page_data_dependency_is_rejected(self):
        (self.root / "data/audit-extra.js").write_text("const AUDIT_EXTRA = {};")
        page = self.root / "index.html"
        page.write_text(page.read_text().replace(
            "</body>", '<script src="data/audit-extra.js?v=1"></script></body>'))
        for name in ["lint_data.js", "smoke_data.js"]:
            result = self.run_script(name)
            self.assertNotEqual(result.returncode, 0, name + " skipped a page dependency")

    def test_nested_copyright_and_description_limits_are_enforced(self):
        cases = [
            ("background.js", "ERA_BACKGROUND", "rows.topics[0].text='“'+'文'.repeat(201)+'”'"),
            ("events.js", "EVENTS", "rows[0].history='「'+'文'.repeat(21)+'」'"),
            ("relations.js", "RELATIONS", "rows[0].phases[0].quote='禁止收录'"),
            ("battles.js", "BATTLES", "rows[0].phase[0].desc='文'.repeat(81)"),
            ("places.js", "PLACES", "Object.values(rows)[0].note='『'+'文'.repeat(21)+'』'"),
        ]
        for filename, symbol, mutation in cases:
            with self.subTest(filename=filename):
                original = (self.root / "data" / filename).read_text()
                self.mutate_data(filename, symbol, mutation)
                result = self.run_script("lint_data.js")
                (self.root / "data" / filename).write_text(original)
                self.assertNotEqual(result.returncode, 0, mutation)
                self.assertNotIn("无 quote 字段、无超长引文", result.stdout)

    def test_copyright_boundary_counts_unicode_characters(self):
        self.mutate_data("background.js", "ERA_BACKGROUND",
                         "rows.topics[0].text='“'+String.fromCodePoint(0x20000).repeat(20)+'”'")
        result = self.run_script("lint_data.js")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.mutate_data("background.js", "ERA_BACKGROUND",
                         "rows.topics[0].text='“'+String.fromCodePoint(0x20000).repeat(21)+'”'")
        self.assertNotEqual(self.run_script("lint_data.js").returncode, 0)


class PresenceRegressions(unittest.TestCase):
    def test_subject_binding_and_reported_actions(self):
        classify = runpy.run_path(str(ROOT / "scripts/ctx.py"))["classify"]
        for sentence in [
            "侍女站在门口报告说，远方的玛卡尔病了。",
            "来信说，玛卡尔走进屋。",
            "安德烈对玛卡尔点头。",
            "玛卡尔的仆人走进屋。",
            "玛卡尔让仆人站起来。",
            "玛卡尔说得不错。",
        ]:
            self.assertNotEqual(classify("玛卡尔", sentence), "出场", sentence)
        self.assertEqual(classify("玛卡尔", "玛卡尔站在门口。"), "出场")


if __name__ == "__main__":
    unittest.main()
