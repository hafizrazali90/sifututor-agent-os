#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("jev_qualification", HERE / "agent-os-jev-live-qualification.py")
qualification = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(qualification)


class JevQualificationTests(unittest.TestCase):
    def test_offline_suite_covers_every_route_and_passes(self):
        report = qualification.build_report(live=False)
        self.assertEqual(len(report["routes"]), 12)
        self.assertEqual({r["expected"] for r in report["routes"]}, {
            "question", "research", "diagnosis", "implementation", "review", "qa",
            "deployment", "handoff", "save_session", "continuation", "new_side_task",
        })
        self.assertEqual(report["summary"]["passed"], report["summary"]["total"])

    def test_every_critical_lane_is_zero_call(self):
        records = qualification.run_safety()
        self.assertEqual(len(records), 8)
        self.assertTrue(all(record["passed"] for record in records))
        self.assertTrue(all(record["network_calls"] == 0 for record in records))

    def test_failure_paths_never_become_authoritative(self):
        records = qualification.run_failures()
        self.assertTrue(all(record["passed"] for record in records))
        self.assertTrue(all(record["authoritative"] is False for record in records))

    def test_repeated_calls_are_consistent(self):
        records = qualification.run_stability(live=False)
        self.assertEqual(len(records), 3)
        self.assertTrue(all(record["passed"] for record in records))

    def test_report_contains_no_prompt_or_response_bodies(self):
        report = qualification.build_report(live=False)
        rendered = str(report)
        for _case_id, prompt, _expected, _active in qualification.ROUTE_CASES:
            self.assertNotIn(prompt, rendered)
        for _case_id, prompt, _lane in qualification.SAFETY_CASES:
            self.assertNotIn(prompt, rendered)


if __name__ == "__main__":
    unittest.main()
