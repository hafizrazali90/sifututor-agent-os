#!/usr/bin/env python3
"""TDD tests for Bundle 2's own deterministic pre-policy layer.

Built the same way as Bundle 1's `pre_policy.py` (pure lookup / pattern
matching, always overrides, zero risk, zero latency, never touches a
provider) but scoped to routing concerns: which project a request belongs
to, and whether the request's subject matter forces a critical risk level
regardless of what a classifier would guess.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


deterministic = load_module("deterministic")


class ResolveProjectDeclaredParamTest(unittest.TestCase):
    def test_declared_param_wins_over_text_mentioning_a_different_project(self) -> None:
        decision = deterministic.resolve_project(
            "I was looking at ripple-suite's Luna classifier but need this checked",
            declared_project="sifu-tutor",
        )
        self.assertEqual(decision.project, "sifu-tutor")
        self.assertEqual(decision.source, "declared_param")


class ResolveProjectDeclaredInTextTest(unittest.TestCase):
    def test_declared_in_text_phrase_is_detected(self) -> None:
        decision = deterministic.resolve_project(
            "This is sifu-tutor work - tutor payout dates look wrong for July",
            declared_project=None,
        )
        self.assertEqual(decision.project, "sifu-tutor")
        self.assertEqual(decision.source, "declared_in_text")

    def test_declared_in_text_wins_over_a_different_project_merely_mentioned(self) -> None:
        decision = deterministic.resolve_project(
            "I was just looking at ripple-suite's Luna classifier but this is "
            "actually sifu-tutor work - can you check why tutor payout dates "
            "look wrong for July",
            declared_project=None,
        )
        self.assertEqual(decision.project, "sifu-tutor")
        self.assertEqual(decision.source, "declared_in_text")

    def test_working_on_phrase_is_detected(self) -> None:
        decision = deterministic.resolve_project(
            "Working on ripple-suite - the Luna intent classifier keeps misfiring",
            declared_project=None,
        )
        self.assertEqual(decision.project, "ripple-suite")
        self.assertEqual(decision.source, "declared_in_text")

    def test_alias_is_resolved_to_the_canonical_project_slug(self) -> None:
        decision = deterministic.resolve_project("This is SIMS work - a bug in the payout screen", declared_project=None)
        self.assertEqual(decision.project, "sifu-tutor")


class ResolveProjectNoneTest(unittest.TestCase):
    def test_returns_none_project_when_nothing_names_one(self) -> None:
        decision = deterministic.resolve_project("Can you explain how this works?", declared_project=None)
        self.assertIsNone(decision.project)
        self.assertEqual(decision.source, "none")


class DetectCriticalRiskTest(unittest.TestCase):
    def test_payment_language_forces_critical(self) -> None:
        override = deterministic.detect_critical_risk("Please refund this parent's invoice from last month")
        self.assertIsNotNone(override)
        self.assertEqual(override.risk_level, "critical")

    def test_auth_language_forces_critical(self) -> None:
        override = deterministic.detect_critical_risk("Change how tutor login/auth sessions expire")
        self.assertIsNotNone(override)
        self.assertEqual(override.risk_level, "critical")

    def test_migration_language_forces_critical(self) -> None:
        override = deterministic.detect_critical_risk("Write a migration to add a column to the invoices table")
        self.assertIsNotNone(override)
        self.assertEqual(override.risk_level, "critical")

    def test_ordinary_text_does_not_force_critical(self) -> None:
        override = deterministic.detect_critical_risk("Can you explain how the tutor rating average is calculated?")
        self.assertIsNone(override)

    def test_override_reason_cites_the_agents_md_safety_rule(self) -> None:
        override = deterministic.detect_critical_risk("Update the commission payout logic")
        self.assertIsNotNone(override)
        self.assertIn("payment", override.reason.lower())

    def test_quoted_payment_mention_inside_a_pasted_report_still_does_not_downgrade(self) -> None:
        # Critical-risk forcing is a safety rule, not a routing classifier
        # answer -- it must stay conservative even inside pasted text.
        override = deterministic.detect_critical_risk(
            'A teammate pasted this log: "refund failed for invoice 881"'
        )
        self.assertIsNotNone(override)
        self.assertEqual(override.risk_level, "critical")


class StripQuotedAndPastedSpansTest(unittest.TestCase):
    def test_removes_a_double_quoted_span(self) -> None:
        cleaned = deterministic.strip_quoted_and_pasted_spans(
            'Here is the log a teammate sent me: "git commit -m fix && git push origin main" - why did this fail?'
        )
        self.assertNotIn("git commit", cleaned)
        self.assertNotIn("git push", cleaned)
        self.assertIn("why did this fail", cleaned)

    def test_leaves_ordinary_text_without_quotes_untouched(self) -> None:
        text = "Can you build a new endpoint for tutor ratings"
        self.assertEqual(deterministic.strip_quoted_and_pasted_spans(text), text)


class IsPastedReportTest(unittest.TestCase):
    def test_detects_a_pasted_log_with_a_quoted_command(self) -> None:
        text = (
            'Here is the log a teammate pasted: "Ran the deploy: git commit -m '
            "'fix' && git push origin main\" - can you tell me why this failed?"
        )
        self.assertTrue(deterministic.is_pasted_report(text))

    def test_plain_implementation_request_is_not_a_pasted_report(self) -> None:
        self.assertFalse(deterministic.is_pasted_report("Please commit and push this change once tests pass"))


class DetectTaskTypeOverrideTest(unittest.TestCase):
    def test_hotfix_language_is_detected(self) -> None:
        self.assertEqual(deterministic.detect_task_type_override("URGENT hotfix needed, production checkout is down"), "hotfix")

    def test_docs_language_is_detected(self) -> None:
        self.assertEqual(deterministic.detect_task_type_override("Please update the documentation for this API"), "docs")

    def test_ordinary_text_has_no_override(self) -> None:
        self.assertIsNone(deterministic.detect_task_type_override("Can you add a new report screen"))


if __name__ == "__main__":
    unittest.main()
