#!/usr/bin/env python3
"""TDD tests for the review-triage orchestrator (Bundle 5, issue #166).

Integration-level proof for every fixture the task specification requires,
plus the two structural guarantees the scope boundary calls out:

  1. A payments/auth/migrations change is deterministically flagged
     regardless of what a provider would guess -- proven here by handing
     `triage_change` a FakeProvider that would answer "low" and confirming
     it is never even dispatched to (`call_count == 0`), the same proof
     pattern decision-layer's own `test_engine.py` uses for its
     `pre_policy` layer.
  2. Every test here is offline: the only provider ever used is
     `provider_fake.FakeProvider`, scripted per scenario. Nothing here can
     reach a network.
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

EXPECTED_SIGNAL_NAMES = {
    "file_risk", "scope_creep", "weakened_tests", "ci_failure",
    "comment_triage", "acceptance_evidence", "staff_doc_relevance",
    "human_journey_evidence",
}


def _flags(report: dict, signal_name: str) -> list[str]:
    for signal in report["signals"]:
        if signal["signal"] == signal_name:
            return signal["flags"]
    raise AssertionError(f"no signal named {signal_name!r} in report")


def _priority(report: dict, signal_name: str) -> str:
    for signal in report["signals"]:
        if signal["signal"] == signal_name:
            return signal["priority"]
    raise AssertionError(f"no signal named {signal_name!r} in report")


class ReportShapeTest(unittest.TestCase):
    def test_runs_all_eight_signals_exactly_once(self) -> None:
        report = triage.triage_change(fixtures.clean_small_fix())
        signal_names = [signal["signal"] for signal in report["signals"]]
        self.assertEqual(set(signal_names), EXPECTED_SIGNAL_NAMES)
        self.assertEqual(len(signal_names), 8)

    def test_report_is_always_advisory_only_and_non_authoritative(self) -> None:
        report = triage.triage_change(fixtures.clean_small_fix())
        self.assertTrue(report["advisory_only"])
        self.assertFalse(report["authoritative"])

    def test_report_names_what_it_never_replaces(self) -> None:
        report = triage.triage_change(fixtures.clean_small_fix())
        self.assertEqual(report["never_replaces"], list(contract.NEVER_REPLACES))


class CleanSmallFixTest(unittest.TestCase):
    """Required fixture: a clean small fix with complete evidence (low
    priority for attention)."""

    def test_every_signal_is_low_and_overall_is_low(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        report = triage.triage_change(fixtures.clean_small_fix(), provider=fake)
        for signal in report["signals"]:
            self.assertEqual(signal["priority"], "low", signal)
        self.assertEqual(report["overall_attention_priority"], "low")

    def test_overall_is_routed_through_the_decision_layer_when_nothing_is_high(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        report = triage.triage_change(fixtures.clean_small_fix(), provider=fake)
        self.assertEqual(report["overall_decision_source"], "provider")
        self.assertEqual(fake.call_count, 1)


class UnrelatedFilesMixedInTest(unittest.TestCase):
    """Required fixture: a change with unrelated file diffs mixed in
    (flagged)."""

    def test_scope_creep_is_flagged_and_overall_is_deterministically_high(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        report = triage.triage_change(fixtures.unrelated_files_mixed_in(), provider=fake)
        self.assertEqual(_priority(report, "scope_creep"), "high")
        self.assertEqual(report["overall_attention_priority"], "high")
        self.assertEqual(report["overall_decision_source"], "deterministic")
        self.assertEqual(fake.call_count, 0)


class WeakenedTestRemovedAssertionTest(unittest.TestCase):
    """Required fixture: a test file with a removed assertion (flagged as
    possibly-weakened)."""

    def test_weakened_tests_is_flagged(self) -> None:
        report = triage.triage_change(fixtures.weakened_test_removed_assertion())
        self.assertEqual(_priority(report, "weakened_tests"), "high")
        self.assertTrue(any(flag.startswith("possibly_weakened_test:") for flag in _flags(report, "weakened_tests")))
        self.assertEqual(report["overall_attention_priority"], "high")


class PaymentsTouchingChangeTest(unittest.TestCase):
    """Required fixture: a payments-touching change (deterministically
    flagged regardless of provider output).

    Uses a FakeProvider that, if it were ever dispatched to, would answer
    "low" (options[0] in the "ok" scenario) -- proving the deterministic
    file_risk critical-lane rule wins without ever asking it.
    """

    def test_is_deterministically_high_and_the_provider_is_never_called(self) -> None:
        disagreeing_fake = provider_fake.FakeProvider(scenario="ok")
        report = triage.triage_change(fixtures.payments_touching_change(), provider=disagreeing_fake)

        self.assertEqual(_priority(report, "file_risk"), "high")
        self.assertTrue(any(flag.startswith("critical_lane:payments:") for flag in _flags(report, "file_risk")))
        self.assertEqual(report["overall_attention_priority"], "high")
        self.assertEqual(report["overall_decision_source"], "deterministic")
        self.assertEqual(disagreeing_fake.call_count, 0, "the decision layer must never be dispatched to for a critical-lane change")

    def test_even_an_unavailable_provider_cannot_change_the_outcome(self) -> None:
        # A provider that would raise if ever dispatched to -- if this
        # signal's deterministic override were ever bypassed, this test
        # would fail with a ProviderUnavailable error instead of a clean
        # "high" result.
        unavailable_fake = provider_fake.FakeProvider(scenario="unavailable")
        report = triage.triage_change(fixtures.payments_touching_change(), provider=unavailable_fake)
        self.assertEqual(report["overall_attention_priority"], "high")
        self.assertEqual(unavailable_fake.call_count, 0)


class UserFacingNoE2eEvidenceTest(unittest.TestCase):
    """Required fixture: a user-facing change with no named E2E/QA evidence
    (flagged as missing human-journey evidence)."""

    def test_human_journey_evidence_is_flagged(self) -> None:
        report = triage.triage_change(fixtures.user_facing_no_e2e_evidence())
        self.assertEqual(_priority(report, "human_journey_evidence"), "high")
        self.assertIn("missing_human_journey_evidence", _flags(report, "human_journey_evidence"))
        self.assertEqual(report["overall_attention_priority"], "high")


class CiFailureFixturesTest(unittest.TestCase):
    def test_flaky_failure_is_categorized_and_does_not_force_overall_high(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        report = triage.triage_change(fixtures.ci_failure_flaky(), provider=fake)
        self.assertTrue(any(flag.startswith("ci_failure_flaky:") for flag in _flags(report, "ci_failure")))
        self.assertEqual(_priority(report, "ci_failure"), "medium")

    def test_real_failure_is_categorized_and_forces_overall_high(self) -> None:
        report = triage.triage_change(fixtures.ci_failure_real())
        self.assertTrue(any(flag.startswith("ci_failure_real:") for flag in _flags(report, "ci_failure")))
        self.assertEqual(report["overall_attention_priority"], "high")

    def test_not_inferable_failure_is_reported_unknown(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        report = triage.triage_change(fixtures.ci_failure_not_inferable(), provider=fake)
        self.assertTrue(any(flag.startswith("ci_failure_unknown:") for flag in _flags(report, "ci_failure")))


class CommentTriageFixturesTest(unittest.TestCase):
    def test_blocking_comment_forces_overall_high(self) -> None:
        report = triage.triage_change(fixtures.review_comment_blocking())
        self.assertEqual(_priority(report, "comment_triage"), "high")
        self.assertEqual(report["overall_attention_priority"], "high")

    def test_informational_comment_is_low_priority(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        report = triage.triage_change(fixtures.review_comment_informational(), provider=fake)
        self.assertEqual(_priority(report, "comment_triage"), "low")


class AcceptanceEvidenceFixtureTest(unittest.TestCase):
    """Required fixture: acceptance-criteria-to-evidence mapping with one
    missing item."""

    def test_missing_evidence_is_flagged_and_forces_overall_high(self) -> None:
        report = triage.triage_change(fixtures.acceptance_evidence_missing())
        self.assertTrue(any(flag.startswith("missing_evidence:") for flag in _flags(report, "acceptance_evidence")))
        self.assertEqual(report["overall_attention_priority"], "high")


class StaffDocRelevanceFixtureTest(unittest.TestCase):
    """Required fixture: staff-documentation relevance with no recorded
    decision."""

    def test_missing_decision_is_flagged_and_forces_overall_high(self) -> None:
        report = triage.triage_change(fixtures.staff_facing_missing_doc_decision())
        self.assertIn("staff_doc_decision_missing_or_incomplete", _flags(report, "staff_doc_relevance"))
        self.assertEqual(report["overall_attention_priority"], "high")


class ConfiguredProviderNameIsIgnoredWhenAProviderIsSuppliedTest(unittest.TestCase):
    """Proof this module cannot be tricked into calling a live provider via
    config: triage_change always dispatches to the explicit `provider`
    argument (or the fake default), never to whatever `config["provider"]`
    names, because it never calls decision-layer's own `_build_provider`."""

    def test_a_jev_flavored_config_still_only_calls_the_supplied_fake(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        cfg = {
            "provider": "jev",  # would build a live-flavored provider if triage.py ever looked at this
            "confidence_threshold": 0.55,
            "timeout_s": 0.2,
            "max_retries": 1,
            "authoritative_decision_types": [],
            "jev_api_key": None,
            "jev_base_url": "https://api.typesafe.ai/v1",
        }
        report = triage.triage_change(fixtures.clean_small_fix(), config=cfg, provider=fake)
        self.assertEqual(fake.call_count, 1)
        self.assertEqual(report["overall_decision_source"], "provider")


if __name__ == "__main__":
    unittest.main()
