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
