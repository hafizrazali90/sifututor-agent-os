#!/usr/bin/env python3
"""TDD tests for the weakened_tests signal (Bundle 5 signal 3 of 8)."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import weakened_tests  # noqa: E402


class RemovedAssertionWithNoReasonTest(unittest.TestCase):
    """Required fixture: a test file with a removed assertion."""

    def test_is_flagged_high_priority(self) -> None:
        payload = {
            "test_diff_notes": [
                {"file": "tests/Feature/InvoiceTest.php", "note": "removed assertRefundAmount check", "assertion_removed": True, "reason_stated": False},
            ]
        }
        record = weakened_tests.classify(payload)
        self.assertEqual(record["priority"], "high")
        self.assertIn("possibly_weakened_test:tests/Feature/InvoiceTest.php", record["flags"])
        self.assertEqual(record["decision_source"], "deterministic")


class RemovedAssertionWithStatedReasonTest(unittest.TestCase):
    def test_is_not_flagged_when_a_reason_was_stated(self) -> None:
        payload = {
            "test_diff_notes": [
                {
                    "file": "tests/Feature/InvoiceTest.php",
                    "note": "assertion moved to its own dedicated RefundRoundingTest",
                    "assertion_removed": True,
                    "reason_stated": True,
                },
            ]
        }
        record = weakened_tests.classify(payload)
        self.assertEqual(record["priority"], "low")
        self.assertEqual(record["flags"], [])


class CleanChangeTest(unittest.TestCase):
    """Required fixture: a clean small fix with complete evidence (low
    priority for attention)."""

    def test_no_test_diff_notes_is_low_priority(self) -> None:
        record = weakened_tests.classify({"test_diff_notes": []})
        self.assertEqual(record["priority"], "low")
        self.assertEqual(record["flags"], [])

    def test_missing_key_entirely_is_low_priority(self) -> None:
        record = weakened_tests.classify({})
        self.assertEqual(record["priority"], "low")


class MultipleWeakenedFilesTest(unittest.TestCase):
    def test_flags_every_weakened_file(self) -> None:
        payload = {
            "test_diff_notes": [
                {"file": "tests/A.php", "assertion_removed": True, "reason_stated": False},
                {"file": "tests/B.php", "assertion_removed": True, "reason_stated": False},
                {"file": "tests/C.php", "assertion_removed": False, "reason_stated": False},
            ]
        }
        record = weakened_tests.classify(payload)
        self.assertEqual(len(record["flags"]), 2)


if __name__ == "__main__":
    unittest.main()
