#!/usr/bin/env python3
"""Tests for the Session Map page check.

The check opens a filled Session Map page and fails when the data block would
show a blank, a misspelled state, or an unfilled placeholder.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
CHECK_PATH = ROOT / "scripts" / "agent-checks" / "session_map_page_check.py"
TEMPLATE_PATH = ROOT / "docs" / "agent-playbooks" / "templates" / "session-map.html"

GOOD = {
    "title": "Fewer stops in the Agent OS",
    "asOf": "17/10 19:29 MYT",
    "defaultBy": "Mac · hafiz.razali · Claude",
    "groups": [
        {
            "name": "Decision policy",
            "steps": [
                {"n": "Rule 1", "s": "written", "d": "The rule is in AGENTS.md."},
                {"n": "Rule 2", "s": "discussing", "here": True, "d": "We are talking it through."},
            ],
        }
    ],
    "usage": [
        {"n": "Codex", "where": "Mac", "plan": "Pro", "used": 15, "window": "Weekly limit",
         "resets": "22/10 14:20 MYT", "read": "17/10 16:07 MYT"},
        {"n": "hafiz.razali", "where": "Mac", "plan": "Claude Max", "used": None, "note": "No reading yet."},
    ],
    "jobs": [{"n": "This chat", "where": "Mac", "acct": "hafiz.razali", "ai": "Claude", "s": "discussing"}],
}


def load_check():
    spec = importlib.util.spec_from_file_location("session_map_page_check", CHECK_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load session map page check")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def page_with(data: dict, base: str) -> str:
    block = "/* SESSION DATA START */\nvar SESSION = " + json.dumps(data, ensure_ascii=False) + ";\n/* SESSION DATA END */"
    return re.sub(r"/\* SESSION DATA START \*/.*?/\* SESSION DATA END \*/", lambda _m: block, base, flags=re.S)


class SessionMapPageCheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.check = load_check()
        cls.base = TEMPLATE_PATH.read_text(encoding="utf-8")

    def problems(self, data: dict) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            path.write_text(page_with(data, self.base), encoding="utf-8")
            return self.check.check_page(path)

    def mutated(self, fn):
        data = json.loads(json.dumps(GOOD))
        fn(data)
        return data

    def test_filled_page_passes(self) -> None:
        self.assertEqual(self.problems(GOOD), [])

    def test_unknown_state_is_reported(self) -> None:
        data = self.mutated(lambda d: d["groups"][0]["steps"][0].update(s="Agreed!"))
        self.assertTrue(any("state" in p for p in self.problems(data)))

    def test_missing_description_is_reported(self) -> None:
        data = self.mutated(lambda d: d["groups"][0]["steps"][0].update(d=""))
        self.assertTrue(any("description" in p for p in self.problems(data)))

    def test_two_here_steps_are_reported(self) -> None:
        data = self.mutated(lambda d: d["groups"][0]["steps"][0].update(here=True))
        self.assertTrue(any("here" in p for p in self.problems(data)))

    def test_no_here_step_is_reported_when_work_is_open(self) -> None:
        data = self.mutated(lambda d: d["groups"][0]["steps"][1].pop("here"))
        self.assertTrue(any("here" in p for p in self.problems(data)))

    def test_time_without_myt_is_reported(self) -> None:
        data = self.mutated(lambda d: d.update(asOf="17/10 19:29"))
        self.assertTrue(any("MYT" in p for p in self.problems(data)))

    def test_em_dash_is_reported(self) -> None:
        data = self.mutated(lambda d: d["groups"][0]["steps"][0].update(d="It is done — mostly."))
        self.assertTrue(any("em dash" in p for p in self.problems(data)))

    def test_unfilled_placeholder_is_reported(self) -> None:
        data = self.mutated(lambda d: d.update(title="REPLACE: the session goal"))
        self.assertTrue(any("REPLACE" in p for p in self.problems(data)))

    def test_group_without_steps_is_reported(self) -> None:
        data = self.mutated(lambda d: d["groups"].append({"name": "Empty goal", "steps": []}))
        self.assertTrue(any("no steps" in p for p in self.problems(data)))

    def test_usage_number_without_reading_time_is_reported(self) -> None:
        data = self.mutated(lambda d: d["usage"][0].pop("read"))
        self.assertTrue(any("reading" in p for p in self.problems(data)))

    def test_job_with_unknown_state_is_reported(self) -> None:
        data = self.mutated(lambda d: d["jobs"][0].update(s="running"))
        self.assertTrue(any("state" in p for p in self.problems(data)))

    def test_data_block_cannot_write_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "written-by-data-block.txt"
            hostile = (
                "/* SESSION DATA START */\n"
                "var SESSION = (function () {\n"
                '  var p = this.constructor.constructor("return process")();\n'
                f'  p.getBuiltinModule("fs").writeFileSync({json.dumps(str(marker))}, "x");\n'
                "  return {};\n"
                "})();\n"
                "/* SESSION DATA END */"
            )
            path = Path(tmp) / "page.html"
            path.write_text(hostile, encoding="utf-8")
            problems = self.check.check_page(path)
            self.assertFalse(marker.exists(), "the data block wrote a file")
            self.assertTrue(problems)

    def test_page_without_data_block_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            path.write_text("<html><body>no data here</body></html>", encoding="utf-8")
            self.assertTrue(any("data block" in p for p in self.check.check_page(path)))


if __name__ == "__main__":
    unittest.main()
