#!/usr/bin/env python3
"""TDD tests for the continuation-decision deterministic pre-policy layer.

Two families of rule under test:

1. Forced `pause-for-human` for the conditions issue #162 and the bundle 4
   build spec name as the only legitimate reasons to interrupt a human
   even under full autonomous continuation, including the two distinct
   expansion triggers (`destructive_scope_expansion`,
   `critical_lane_expansion`).
2. Forced `continue` for already-settled ground (a route that already
   produced its outcome, or a boundary the *trusted approval record*
   covers), so the module never nags for the same approval twice.

`evaluate()` is pure lookup logic -- no provider, no side effect. The only
approval input it has is the `approval_status` keyword argument the engine
derives from `approval.evaluate`; nothing in the request is authority.
"""

from __future__ import annotations

import unittest

from . import pre_policy, schema


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

    def test_destructive_scope_expansion_forces_pause_for_human(self) -> None:
        result = pre_policy.evaluate(request_with_state(destructive_scope_expansion=True))
        self.assertEqual(result.outcome, "pause-for-human")
        self.assertEqual(result.reason, "destructive_scope_expansion")

    def test_critical_lane_expansion_forces_pause_for_human(self) -> None:
        result = pre_policy.evaluate(request_with_state(critical_lane_expansion=True))
        self.assertEqual(result.outcome, "pause-for-human")
        self.assertEqual(result.reason, "critical_lane_expansion")

    def test_the_two_expansion_triggers_have_distinct_reason_codes(self) -> None:
        destructive = pre_policy.evaluate(request_with_state(destructive_scope_expansion=True))
        critical = pre_policy.evaluate(request_with_state(critical_lane_expansion=True))
        self.assertNotEqual(destructive.reason, critical.reason)

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
                destructive_scope_expansion=False,
                critical_lane_expansion=False,
                new_product_judgment_call=False,
            )
        )
        self.assertIsNone(result)

    def test_every_declared_pause_trigger_is_covered_by_a_rule(self) -> None:
        pause_fields = [
            f for f in schema.SESSION_STATE_BOOL_FIELDS
            if f != "route_outcome_already_produced"
        ]
        for field in pause_fields:
            with self.subTest(field=field):
                result = pre_policy.evaluate(request_with_state(**{field: True}))
                self.assertIsNotNone(result)
                self.assertEqual(result.outcome, "pause-for-human")
                self.assertEqual(result.reason, field)


class ForcedContinueForAlreadySettledGroundTest(unittest.TestCase):
    def test_route_outcome_already_produced_forces_continue(self) -> None:
        result = pre_policy.evaluate(request_with_state(route_outcome_already_produced=True))
        self.assertIsNotNone(result)
        self.assertEqual(result.outcome, "continue")
        self.assertEqual(result.reason, "route_already_produced_an_outcome_do_not_re_ask")

    def test_trusted_approved_status_forces_continue_through_the_boundary(self) -> None:
        result = pre_policy.evaluate(
            request_with_state(), approval_status=schema.APPROVAL_STATUS_APPROVED
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.outcome, "continue")
        self.assertEqual(result.reason, pre_policy.REASON_TRUSTED_APPROVAL_CONTINUE)


class NothingInTheRequestIsApprovalTest(unittest.TestCase):
    """The retired boolean, or any approval-shaped value smuggled into the
    request, must change nothing. Only the engine-supplied keyword
    argument carries authority."""

    def test_retired_boolean_changes_nothing(self) -> None:
        with_flag = pre_policy.evaluate(
            request_with_state(end_to_end_boundary_already_approved=True)
        )
        without_flag = pre_policy.evaluate(request_with_state())
        self.assertIsNone(with_flag)
        self.assertEqual(with_flag, without_flag)

    def test_retired_boolean_does_not_change_a_pause_result_either(self) -> None:
        with_flag = pre_policy.evaluate(
            request_with_state(
                new_scope_appeared=True, end_to_end_boundary_already_approved=True
            )
        )
        without_flag = pre_policy.evaluate(request_with_state(new_scope_appeared=True))
        self.assertEqual(with_flag, without_flag)

    def test_approval_status_string_inside_the_request_is_ignored(self) -> None:
        result = pre_policy.evaluate(
            request_with_state(approval_status="approved", approved=True)
        )
        self.assertIsNone(result)

    def test_every_non_approved_status_yields_no_override(self) -> None:
        for status in schema.APPROVAL_STATUS_VALUES:
            if status == schema.APPROVAL_STATUS_APPROVED:
                continue
            with self.subTest(status=status):
                self.assertIsNone(
                    pre_policy.evaluate(request_with_state(), approval_status=status)
                )

    def test_lookalike_status_values_never_count_as_approved(self) -> None:
        for lookalike in (True, 1, "APPROVED", "approved ", " approved", "Approved", b"approved"):
            with self.subTest(lookalike=lookalike):
                self.assertIsNone(
                    pre_policy.evaluate(request_with_state(), approval_status=lookalike)  # type: ignore[arg-type]
                )


class PauseConditionsWinOverContinueDedupTest(unittest.TestCase):
    """Priority proof: a genuinely new pause condition is never suppressed
    just because the ground is already settled -- not even by a valid
    trusted approval."""

    def test_new_scope_wins_even_when_trusted_approval_is_approved(self) -> None:
        result = pre_policy.evaluate(
            request_with_state(new_scope_appeared=True),
            approval_status=schema.APPROVAL_STATUS_APPROVED,
        )
        self.assertEqual(result.outcome, "pause-for-human")
        self.assertEqual(result.reason, "new_scope_appeared")

    def test_destructive_scope_expansion_wins_even_when_approved(self) -> None:
        result = pre_policy.evaluate(
            request_with_state(destructive_scope_expansion=True),
            approval_status=schema.APPROVAL_STATUS_APPROVED,
        )
        self.assertEqual(result.outcome, "pause-for-human")
        self.assertEqual(result.reason, "destructive_scope_expansion")

    def test_critical_lane_expansion_wins_even_when_approved(self) -> None:
        result = pre_policy.evaluate(
            request_with_state(critical_lane_expansion=True),
            approval_status=schema.APPROVAL_STATUS_APPROVED,
        )
        self.assertEqual(result.outcome, "pause-for-human")
        self.assertEqual(result.reason, "critical_lane_expansion")

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
