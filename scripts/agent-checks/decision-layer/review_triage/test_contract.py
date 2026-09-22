#!/usr/bin/env python3
"""TDD tests for the review-triage shared output contract.

Proves the shape is structurally incapable of claiming "passed" or
"verified" and that every signal record carries the fixed advisory-only,
non-authoritative fields (scope boundary: this module only classifies or
prioritizes, it never marks anything as passed or verified).
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import contract  # noqa: E402


class BuildSignalShapeTest(unittest.TestCase):
    def test_returns_every_declared_field(self) -> None:
        record = contract.build_signal(
            signal="file_risk",
            priority="low",
            flags=[],
            reason="clean change",
            decision_source="deterministic",
        )
        self.assertEqual(set(record.keys()), set(contract.signal_fields()))

    def test_advisory_only_is_always_true(self) -> None:
        record = contract.build_signal(
            signal="file_risk", priority="high", flags=["x"], reason="r", decision_source="deterministic"
        )
        self.assertTrue(record["advisory_only"])

    def test_authoritative_is_always_false_and_not_settable(self) -> None:
        record = contract.build_signal(
            signal="file_risk", priority="high", flags=["x"], reason="r", decision_source="provider"
        )
        self.assertFalse(record["authoritative"])

    def test_rejects_invalid_priority(self) -> None:
        with self.assertRaises(ValueError):
            contract.build_signal(
                signal="file_risk", priority="urgent", flags=[], reason="r", decision_source="deterministic"
            )

    def test_rejects_invalid_decision_source(self) -> None:
        with self.assertRaises(ValueError):
            contract.build_signal(
                signal="file_risk", priority="low", flags=[], reason="r", decision_source="guess"
            )


class NeverReplacesTest(unittest.TestCase):
    def test_names_the_real_checks_it_can_never_stand_in_for(self) -> None:
        for real_check in ("tests", "e2e", "qa", "security_checks", "adversarial_review", "release_smoke", "monitoring", "rollback_evidence"):
            self.assertIn(real_check, contract.NEVER_REPLACES)


class ContainsForbiddenClaimTest(unittest.TestCase):
    def test_flags_the_word_passed(self) -> None:
        self.assertTrue(contract.contains_forbidden_claim("all checks passed"))

    def test_flags_the_word_verified(self) -> None:
        self.assertTrue(contract.contains_forbidden_claim({"reason": "evidence verified"}))

    def test_flags_inside_nested_structures(self) -> None:
        self.assertTrue(contract.contains_forbidden_claim({"flags": ["ok", "this was verified"]}))

    def test_does_not_false_positive_on_substrings(self) -> None:
        # "bypass" contains "pass" as a substring but is not the word
        # "passed"; word-boundary matching must not flag it.
        self.assertFalse(contract.contains_forbidden_claim("do not bypass review"))

    def test_clean_text_is_not_flagged(self) -> None:
        self.assertFalse(contract.contains_forbidden_claim("test file has a removed assertion with no stated reason"))


if __name__ == "__main__":
    unittest.main()
