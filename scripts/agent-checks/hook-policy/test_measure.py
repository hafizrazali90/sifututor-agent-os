#!/usr/bin/env python3
"""TDD tests for the measurement harness (bundle spec, build item 3).

The harness must report: dispatch latency, route accuracy against the
documented-identical-behavior fixtures, false-block rate, and -- only if a
real source exists -- a token/cost figure. Import/context cost is reported
as an honest proxy (source size + cold-import time), not fabricated.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from measure import MEASURE_FIXTURES, run_measurement  # noqa: E402


class MeasureFixtureSetTests(unittest.TestCase):
    def test_fixture_set_is_nonempty_and_labeled_allow_or_deny(self):
        self.assertGreater(len(MEASURE_FIXTURES), 10)
        for fixture in MEASURE_FIXTURES:
            with self.subTest(fixture=fixture):
                self.assertIn("command", fixture)
                self.assertIn("expected", fixture)
                self.assertIn(fixture["expected"], ("allow", "deny"))


class RunMeasurementTests(unittest.TestCase):
    def setUp(self):
        self.report = run_measurement(repeat=3)

    def test_reports_route_accuracy_of_one(self):
        # Every fixture here is drawn from the same commands already proven
        # to match the real scripts in test_parity_*.py, so the dispatcher
        # built from default_checks() must classify all of them correctly.
        self.assertEqual(self.report["route_accuracy"], 1.0)
        self.assertEqual(self.report["fixture_count"], len(MEASURE_FIXTURES))

    def test_reports_zero_false_blocks_on_this_fixture_set(self):
        self.assertEqual(self.report["false_block_rate"], 0.0)

    def test_reports_dispatch_latency_stats(self):
        latency = self.report["dispatch_latency_ms"]
        self.assertIn("mean", latency)
        self.assertIn("max", latency)
        self.assertGreaterEqual(latency["mean"], 0.0)

    def test_reports_startup_cost_as_a_labeled_proxy(self):
        startup = self.report["startup_cost"]
        self.assertIn("cold_import_ms", startup)
        self.assertIn("source_bytes", startup)
        self.assertIn("source_lines", startup)
        self.assertGreater(startup["source_bytes"], 0)
        self.assertIn("note", startup)
        self.assertIn("proxy", startup["note"].lower())

    def test_reports_token_cost_honestly_as_unavailable(self):
        token_cost = self.report["token_cost"]
        self.assertIsNone(token_cost["value"])
        self.assertIn("no real token/cost", token_cost["note"].lower())


if __name__ == "__main__":
    unittest.main()
