#!/usr/bin/env python3
"""TDD tests for the continuation-decision deterministic pre-policy layer.

Two families of rule under test:

1. Forced `pause-for-human` for the conditions issue #162 and the bundle 4
   build spec name as the only legitimate reasons to interrupt a human
   even under full autonomous continuation.
2. Forced `continue` for already-settled ground (a route that already
   produced its outcome, or an already-approved end-to-end boundary), so
   the module never nags for the same approval twice.

`evaluate()` is pure lookup logic -- no provider, no side effect.
"""

from __future__ import annotations

import unittest

from . import pre_policy


def request_with_state(**state_overrides) -> dict:
    return {
        "schema_version": 1,
        "milestone_description": "Finished writing the payment refund migration.",
        "session_state": state_overrides,
        "caller_message": "",
    }


class NoConditionMatchesTest(unittest.TestCase):
    def test_returns_none_for_an_empty_session_state(self) -> None:
        self.assertIsNone(pre_policy.evaluate(request_with_state()))

    def test_returns_none_when_no_session_state_key_is_present(self) -> None:
        request = {"schema_version": 1, "milestone_description": "x"}
        self.assertIsNone(pre_policy.evaluate(request))


class ForcedPauseForHumanTest(unittest.TestCase):
    def test_new_scope_appeared_forces_pause_for_human(self) -> None:
        result = pre_policy.evaluate(request_with_state(new_scope_appeared=True))
        self.assertIsNotNone(result)
        self.assertEqual(result.outcome, "pause-for-human")
        self.assertEqual(result.reason, "new_scope_appeared")

    def test_risk_materially_changed_forces_pause_for_human(self) -> None:
        result = pre_policy.evaluate(request_with_state(risk_materially_changed=True))
        self.assertEqual(result.outcome, "pause-for-human")
        self.assertEqual(result.reason, "risk_materially_changed")

    def test_rollback_or_backup_unavailable_forces_pause_for_human(self) -> None:
        result = pre_policy.evaluate(request_with_state(rollback_or_backup_unavailable=True))
        self.assertEqual(result.outcome, "pause-for-human")
        self.assertEqual(result.reason, "rollback_or_backup_unavailable")

    def test_destructive_action_widening_scope_forces_pause_for_human(self) -> None:
        result = pre_policy.evaluate(
            request_with_state(destructive_action_widening_scope=True)
        )
        self.assertEqual(result.outcome, "pause-for-human")
        self.assertEqual(result.reason, "destructive_action_widening_scope")

    def test_new_product_judgment_call_forces_pause_for_human(self) -> None:
        result = pre_policy.evaluate(request_with_state(new_product_judgment_call=True))
        self.assertEqual(result.outcome, "pause-for-human")
        self.assertEqual(result.reason, "new_product_judgment_call")

    def test_false_flags_do_not_trigger_pause_for_human(self) -> None:
        result = pre_policy.evaluate(
            request_with_state(
                new_scope_appeared=False,
                risk_materially_changed=False,
                rollback_or_backup_unavailable=False,
                destructive_action_widening_scope=False,
                new_product_judgment_call=False,
            )
        )
        self.assertIsNone(result)


class ForcedContinueForAlreadySettledGroundTest(unittest.TestCase):
    def test_route_outcome_already_produced_forces_continue(self) -> None:
        result = pre_policy.evaluate(request_with_state(route_outcome_already_produced=True))
        self.assertIsNotNone(result)
        self.assertEqual(result.outcome, "continue")
        self.assertEqual(result.reason, "route_already_produced_an_outcome_do_not_re_ask")

    def test_end_to_end_boundary_already_approved_forces_continue(self) -> None:
        result = pre_policy.evaluate(
            request_with_state(end_to_end_boundary_already_approved=True)
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.outcome, "continue")
        self.assertEqual(
            result.reason, "end_to_end_boundary_already_approved_continue_through"
        )


class PauseConditionsWinOverContinueDedupTest(unittest.TestCase):
    """Priority proof: a genuinely new pause condition is never suppressed
    just because the caller also claims already-settled ground."""

    def test_new_scope_wins_even_when_boundary_already_approved(self) -> None:
        result = pre_policy.evaluate(
            request_with_state(
                new_scope_appeared=True,
                end_to_end_boundary_already_approved=True,
            )
        )
        self.assertEqual(result.outcome, "pause-for-human")
        self.assertEqual(result.reason, "new_scope_appeared")

    def test_rollback_unavailable_wins_even_when_route_already_produced_outcome(
        self,
    ) -> None:
        result = pre_policy.evaluate(
            request_with_state(
                rollback_or_backup_unavailable=True,
                route_outcome_already_produced=True,
            )
        )
        self.assertEqual(result.outcome, "pause-for-human")
        self.assertEqual(result.reason, "rollback_or_backup_unavailable")


class PrePolicyResultIsImmutableTest(unittest.TestCase):
    def test_result_fields_cannot_be_reassigned(self) -> None:
        result = pre_policy.evaluate(request_with_state(new_scope_appeared=True))
        with self.assertRaises(Exception):
            result.outcome = "complete"  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
