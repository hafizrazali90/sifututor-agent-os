#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

MODULE = Path(__file__).with_name("weekly-delivery-data.py")
spec = importlib.util.spec_from_file_location("weekly_delivery_data", MODULE)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def completed(code: int, stdout: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess([], code, stdout, "not persisted")


class WeeklyDeliveryDataTests(unittest.TestCase):
    def test_successful_zero_result_week_is_quiet(self):
        calls = iter([completed(0, "[]"), completed(0, "0\n")])
        report = module.build_report(["Sifututor/ripple-suite"], "2026-09-01", "2026-09-07", lambda _cmd: next(calls))
        self.assertEqual(report["status"], "quiet")
        self.assertEqual(report["repositories"][0]["status"], "empty")
        self.assertTrue(report["shareable_summary_allowed"])

    def test_failed_query_is_not_reported_as_quiet(self):
        report = module.build_report(
            ["Sifututor/ripple-suite"], "2026-09-01", "2026-09-07", lambda _cmd: completed(4)
        )
        self.assertEqual(report["status"], "unavailable")
        self.assertEqual(report["repositories"][0]["status"], "failed")
        self.assertFalse(report["shareable_summary_allowed"])

    def test_one_failed_repo_makes_report_partial(self):
        calls = iter([
            completed(0, json.dumps([{"number": 1}])), completed(0, "1\n"), completed(1),
        ])
        report = module.build_report(["Sifututor/one", "Sifututor/two"], "2026-09-01", "2026-09-07", lambda _cmd: next(calls))
        self.assertEqual(report["status"], "partial")
        self.assertFalse(report["shareable_summary_allowed"])

    def test_count_mismatch_is_partial(self):
        calls = iter([completed(0, json.dumps([{"number": 1}])), completed(0, "2\n")])
        result = module.collect_repo("Sifututor/ripple-suite", "2026-09-01", "2026-09-07", lambda _cmd: next(calls))
        self.assertEqual(result.status, "partial")
        self.assertEqual(result.item_count, 1)
        self.assertEqual(result.expected_count, 2)

    def test_output_does_not_include_command_error_text(self):
        report = module.build_report(
            ["Sifututor/ripple-suite"], "2026-09-01", "2026-09-07",
            lambda _cmd: subprocess.CompletedProcess([], 1, "", "credential-shaped output"),
        )
        self.assertNotIn("credential-shaped output", json.dumps(report))


if __name__ == "__main__":
    unittest.main()
