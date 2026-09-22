#!/usr/bin/env python3
"""TDD tests for the human_journey_evidence signal (Bundle 5 signal 8 of 8).

Required fixture: a user-facing change with no named E2E/QA evidence
(flagged as missing human-journey evidence).
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import human_journey_evidence  # noqa: E402


class NotUserFacingTest(unittest.TestCase):
    def test_a_backend_only_change_is_low_priority(self) -> None:
        record = human_journey_evidence.classify({"is_user_facing": False})
        self.assertEqual(record["priority"], "low")
        self.assertEqual(record["flags"], [])


class UserFacingWithNoEvidenceTest(unittest.TestCase):
    def test_is_flagged_high_priority(self) -> None:
        payload = {"is_user_facing": True, "human_journey_evidence": []}
        record = human_journey_evidence.classify(payload)
        self.assertEqual(record["priority"], "high")
        self.assertIn("missing_human_journey_evidence", record["flags"])

    def test_missing_key_entirely_is_also_flagged(self) -> None:
        record = human_journey_evidence.classify({"is_user_facing": True})
        self.assertEqual(record["priority"], "high")

    def test_a_list_of_only_blank_strings_still_counts_as_missing(self) -> None:
        payload = {"is_user_facing": True, "human_journey_evidence": ["  ", ""]}
        record = human_journey_evidence.classify(payload)
        self.assertEqual(record["priority"], "high")


class UserFacingWithEvidenceTest(unittest.TestCase):
    def test_named_e2e_evidence_is_low_priority(self) -> None:
        payload = {"is_user_facing": True, "human_journey_evidence": ["tests/e2e/tutor-list.spec.ts"]}
        record = human_journey_evidence.classify(payload)
        self.assertEqual(record["priority"], "low")
        self.assertEqual(record["flags"], [])


if __name__ == "__main__":
    unittest.main()
