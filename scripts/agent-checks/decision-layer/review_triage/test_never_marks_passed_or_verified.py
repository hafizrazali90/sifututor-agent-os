#!/usr/bin/env python3
"""Proof: this module never marks anything "passed" or "verified" (scope
boundary from the task specification):

    "A test must prove this module never marks anything 'passed' or
    'verified' -- it only classifies/prioritizes."

This is checked two ways:

  1. Structural: the shared output contract (`contract.build_signal` and
     `triage.triage_change`'s own report shape) has no field that could
     carry a pass/fail verdict -- no `status`, `result`, `passed`, or
     `verified` key exists anywhere in the shape.
  2. Content: every string value anywhere in the full triage report, for
     every fixture this module ships (including every fixture required by
     the task specification), is scanned for the standalone words "passed"
     or "verified" and must never contain either.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
_DECISION_LAYER_DIR = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(_DECISION_LAYER_DIR))

import contract  # noqa: E402
import fixtures  # noqa: E402
import provider_fake  # noqa: E402
import triage  # noqa: E402

_FORBIDDEN_FIELD_NAMES = {"status", "result", "passed", "verified", "verify", "pass"}

ALL_FIXTURES = (
    fixtures.clean_small_fix,
    fixtures.unrelated_files_mixed_in,
    fixtures.weakened_test_removed_assertion,
    fixtures.payments_touching_change,
    fixtures.user_facing_no_e2e_evidence,
    fixtures.ci_failure_flaky,
    fixtures.ci_failure_real,
    fixtures.ci_failure_not_inferable,
    fixtures.review_comment_blocking,
    fixtures.review_comment_informational,
    fixtures.acceptance_evidence_missing,
    fixtures.staff_facing_missing_doc_decision,
)


def _field_names(value: object, found: set) -> None:
    if isinstance(value, dict):
        for key, inner in value.items():
            found.add(key)
            _field_names(inner, found)
    elif isinstance(value, (list, tuple)):
        for inner in value:
            _field_names(inner, found)


class NoForbiddenFieldNamesTest(unittest.TestCase):
    def test_the_report_shape_never_uses_a_pass_or_verify_flavored_field_name(self) -> None:
        for build in ALL_FIXTURES:
            with self.subTest(fixture=build.__name__):
                report = triage.triage_change(build(), provider=provider_fake.FakeProvider(scenario="ok"))
                field_names: set = set()
                _field_names(report, field_names)
                offending = field_names & _FORBIDDEN_FIELD_NAMES
                self.assertEqual(offending, set(), f"forbidden field name(s) found: {offending}")


class NoForbiddenClaimValuesTest(unittest.TestCase):
    def test_no_output_value_ever_claims_passed_or_verified_for_every_required_fixture(self) -> None:
        for build in ALL_FIXTURES:
            with self.subTest(fixture=build.__name__):
                report = triage.triage_change(build(), provider=provider_fake.FakeProvider(scenario="ok"))
                self.assertFalse(
                    contract.contains_forbidden_claim(report),
                    f"fixture {build.__name__!r} produced a report claiming passed/verified: {report}",
                )

    def test_a_deliberately_adversarial_reason_string_would_be_caught(self) -> None:
        # Sanity-check the checker itself: prove it actually catches a
        # violation, not just that our own fixtures happen to be clean.
        poisoned = {"reason": "all checks passed and the change was verified"}
        self.assertTrue(contract.contains_forbidden_claim(poisoned))


class SignalRecordsNeverAuthoritativeTest(unittest.TestCase):
    def test_every_signal_and_the_overall_report_is_always_non_authoritative(self) -> None:
        for build in ALL_FIXTURES:
            with self.subTest(fixture=build.__name__):
                report = triage.triage_change(build(), provider=provider_fake.FakeProvider(scenario="ok"))
                self.assertFalse(report["authoritative"])
                self.assertTrue(report["advisory_only"])
                for signal in report["signals"]:
                    self.assertFalse(signal["authoritative"])
                    self.assertTrue(signal["advisory_only"])


if __name__ == "__main__":
    unittest.main()
