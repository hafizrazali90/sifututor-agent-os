#!/usr/bin/env python3
"""TDD tests for the scope_creep signal (Bundle 5 signal 2 of 8)."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import scope_creep  # noqa: E402


class ExplicitlyUnrelatedFileTest(unittest.TestCase):
    """Required fixture: a change with unrelated file diffs mixed in."""

    def test_is_flagged_high_priority(self) -> None:
        payload = {
            "task_description": "Fix the tutor payout rounding bug.",
            "changed_files": [
                {"path": "app/Services/PayoutService.php", "additions": 4, "deletions": 2, "related_to_task": True},
                {"path": "resources/js/components/UnrelatedChart.tsx", "additions": 80, "deletions": 0, "related_to_task": False},
            ],
        }
        record = scope_creep.classify(payload)
        self.assertEqual(record["priority"], "high")
        self.assertIn("unrelated_file:resources/js/components/UnrelatedChart.tsx", record["flags"])
        self.assertEqual(record["decision_source"], "deterministic")


class CleanRelatedChangeTest(unittest.TestCase):
    """Required fixture: a clean small fix with complete evidence (low
    priority for attention)."""

    def test_is_low_priority_when_everything_is_marked_related(self) -> None:
        payload = {
            "task_description": "Fix a typo in the tutor list empty-state copy.",
            "changed_files": [
                {"path": "src/modules/tutor/EmptyState.tsx", "additions": 2, "deletions": 1, "related_to_task": True},
            ],
        }
        record = scope_creep.classify(payload)
        self.assertEqual(record["priority"], "low")
        self.assertEqual(record["flags"], [])


class WeakKeywordHeuristicTest(unittest.TestCase):
    def test_flags_a_file_with_no_word_overlap_at_medium_priority(self) -> None:
        payload = {
            "task_description": "Fix invoice rounding for partial refunds.",
            "changed_files": [
                {"path": "app/Services/InvoiceRefundService.php", "additions": 5, "deletions": 1},
                {"path": "resources/js/components/DashboardChart.tsx", "additions": 30, "deletions": 0},
            ],
        }
        record = scope_creep.classify(payload)
        self.assertEqual(record["priority"], "medium")
        self.assertTrue(any(flag.startswith("possibly_unrelated_file:") and "DashboardChart" in flag for flag in record["flags"]))

    def test_does_not_flag_test_files_that_share_no_keywords(self) -> None:
        payload = {
            "task_description": "Fix invoice rounding for partial refunds.",
            "changed_files": [
                {"path": "app/Services/InvoiceRefundService.php", "additions": 5, "deletions": 1},
                {"path": "tests/Feature/RefundRoundingTest.php", "additions": 20, "deletions": 0, "kind": "test"},
            ],
        }
        record = scope_creep.classify(payload)
        self.assertEqual(record["flags"], [])
        self.assertEqual(record["priority"], "low")

    def test_no_task_description_never_raises_a_false_flag(self) -> None:
        payload = {"changed_files": [{"path": "app/Services/InvoiceRefundService.php", "additions": 5, "deletions": 1}]}
        record = scope_creep.classify(payload)
        self.assertEqual(record["priority"], "low")


class ExplicitOverridesHeuristicTest(unittest.TestCase):
    def test_explicit_true_wins_even_with_no_keyword_overlap(self) -> None:
        payload = {
            "task_description": "Fix invoice rounding.",
            "changed_files": [
                {"path": "app/Services/UnrelatedNamePath.php", "additions": 5, "deletions": 1, "related_to_task": True},
            ],
        }
        record = scope_creep.classify(payload)
        self.assertEqual(record["priority"], "low")


if __name__ == "__main__":
    unittest.main()
