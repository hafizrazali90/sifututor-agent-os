#!/usr/bin/env python3
"""TDD tests for the file_risk signal (Bundle 5 signal 1 of 8).

Every test here is pure and offline -- file_risk never dispatches to a
provider, so there is nothing here that could reach a network.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import file_risk  # noqa: E402


def clean_fix_payload():
    """Fixture: a clean small fix with a tiny diff, nothing critical-lane."""
    return {
        "task_description": "Fix a typo in the tutor list empty-state copy.",
        "changed_files": [
            {"path": "src/modules/tutor/EmptyState.tsx", "additions": 2, "deletions": 1, "kind": "code"},
        ],
    }


def payments_touching_payload():
    """Required fixture: a payments-touching change."""
    return {
        "task_description": "Adjust invoice rounding for partial refunds.",
        "changed_files": [
            {"path": "app/Services/InvoiceRefundService.php", "additions": 12, "deletions": 3, "kind": "code"},
        ],
    }


class CleanSmallFixTest(unittest.TestCase):
    def test_is_low_priority(self) -> None:
        record = file_risk.classify(clean_fix_payload())
        self.assertEqual(record["priority"], "low")
        self.assertEqual(record["flags"], [])
        self.assertEqual(record["decision_source"], "deterministic")


class CriticalLanePaymentsTest(unittest.TestCase):
    """Required fixture: payments-touching change deterministically flagged
    regardless of provider output -- this signal never calls a provider at
    all, so there is nothing for a provider to disagree with."""

    def test_is_high_priority_with_a_critical_lane_flag(self) -> None:
        record = file_risk.classify(payments_touching_payload())
        self.assertEqual(record["priority"], "high")
        self.assertTrue(any(flag.startswith("critical_lane:payments:") for flag in record["flags"]))
        self.assertEqual(record["decision_source"], "deterministic")

    def test_small_diff_size_does_not_lower_the_critical_lane_priority(self) -> None:
        payload = {
            "changed_files": [
                {"path": "app/Services/InvoiceRefundService.php", "additions": 1, "deletions": 0},
            ]
        }
        record = file_risk.classify(payload)
        self.assertEqual(record["priority"], "high")


class CriticalLaneAuthTest(unittest.TestCase):
    def test_auth_path_is_flagged(self) -> None:
        payload = {"changed_files": [{"path": "app/Http/Controllers/Auth/LoginController.php", "additions": 5, "deletions": 5}]}
        record = file_risk.classify(payload)
        self.assertEqual(record["priority"], "high")
        self.assertTrue(any("critical_lane:auth:" in flag for flag in record["flags"]))


class CriticalLaneMigrationsTest(unittest.TestCase):
    def test_migration_path_is_flagged(self) -> None:
        payload = {"changed_files": [{"path": "database/migrations/2026_09_22_add_payout_index.php", "additions": 20, "deletions": 0}]}
        record = file_risk.classify(payload)
        self.assertEqual(record["priority"], "high")
        self.assertTrue(any("critical_lane:migrations:" in flag for flag in record["flags"]))


class NonCriticalPathIsNeverFalselyFlaggedTest(unittest.TestCase):
    def test_ordinary_filename_containing_a_substring_is_not_a_false_positive(self) -> None:
        # "author.tsx" must not match the "auth" keyword -- token matching,
        # not substring matching.
        payload = {"changed_files": [{"path": "src/modules/blog/Author.tsx", "additions": 3, "deletions": 1}]}
        record = file_risk.classify(payload)
        self.assertEqual(record["flags"], [])
        self.assertEqual(record["priority"], "low")


class DiffSizeThresholdsTest(unittest.TestCase):
    def test_medium_diff_is_medium_priority(self) -> None:
        payload = {"changed_files": [{"path": "src/foo.ts", "additions": 40, "deletions": 20}]}
        record = file_risk.classify(payload)
        self.assertEqual(record["priority"], "medium")

    def test_large_diff_is_high_priority(self) -> None:
        payload = {"changed_files": [{"path": "src/foo.ts", "additions": 150, "deletions": 100}]}
        record = file_risk.classify(payload)
        self.assertEqual(record["priority"], "high")
        self.assertTrue(any(flag.startswith("large_diff:") for flag in record["flags"]))


class NoChangedFilesTest(unittest.TestCase):
    def test_empty_changed_files_is_low_priority(self) -> None:
        record = file_risk.classify({"changed_files": []})
        self.assertEqual(record["priority"], "low")


if __name__ == "__main__":
    unittest.main()
