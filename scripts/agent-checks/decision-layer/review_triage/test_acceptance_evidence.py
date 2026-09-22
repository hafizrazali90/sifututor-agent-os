#!/usr/bin/env python3
"""TDD tests for the acceptance_evidence signal (Bundle 5 signal 6 of 8).

Required fixture: acceptance-criteria-to-evidence mapping (does each stated
acceptance item have a named piece of evidence, or is one missing).
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import acceptance_evidence  # noqa: E402


class NoCriteriaTest(unittest.TestCase):
    def test_is_low_priority(self) -> None:
        record = acceptance_evidence.classify({"acceptance_criteria": []})
        self.assertEqual(record["priority"], "low")


class CompleteEvidenceTest(unittest.TestCase):
    """Required fixture: a clean small fix with complete evidence (low
    priority for attention)."""

    def test_every_item_with_evidence_is_low_priority(self) -> None:
        payload = {
            "acceptance_criteria": [
                {"item": "Tutor list no longer shows a typo", "evidence": "screenshot: docs/evidence/tutor-list-fix.png"},
            ]
        }
        record = acceptance_evidence.classify(payload)
        self.assertEqual(record["priority"], "low")
        self.assertEqual(record["flags"], [])


class MissingEvidenceTest(unittest.TestCase):
    def test_an_item_with_no_evidence_is_flagged_high_priority(self) -> None:
        payload = {
            "acceptance_criteria": [
                {"item": "Refund amount never goes negative", "evidence": "tests/Feature/RefundRoundingTest.php"},
                {"item": "Staff can see the corrected amount on the invoice screen", "evidence": None},
            ]
        }
        record = acceptance_evidence.classify(payload)
        self.assertEqual(record["priority"], "high")
        self.assertIn("missing_evidence:Staff can see the corrected amount on the invoice screen", record["flags"])

    def test_blank_string_evidence_counts_as_missing(self) -> None:
        payload = {"acceptance_criteria": [{"item": "X works", "evidence": "   "}]}
        record = acceptance_evidence.classify(payload)
        self.assertEqual(record["priority"], "high")


if __name__ == "__main__":
    unittest.main()
