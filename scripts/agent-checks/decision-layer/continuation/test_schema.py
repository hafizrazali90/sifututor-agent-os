#!/usr/bin/env python3
"""TDD tests for the continuation-decision request/response schema."""

from __future__ import annotations

import unittest

from . import schema


def valid_request(**overrides) -> dict:
    request = {
        "schema_version": 1,
        "milestone_description": "Finished implementing the login endpoint's unit tests.",
        "session_state": {},
        "caller_message": "",
    }
    request.update(overrides)
    return request


class ValidateRequestTest(unittest.TestCase):
    def test_a_well_formed_request_has_no_errors(self) -> None:
        self.assertEqual(schema.validate_request(valid_request()), [])

    def test_non_dict_request_is_rejected(self) -> None:
        self.assertEqual(schema.validate_request("not a dict"), ["request:object_required"])

    def test_wrong_schema_version_is_rejected(self) -> None:
        errors = schema.validate_request(valid_request(schema_version=2))
        self.assertIn("schema_version:unsupported", errors)

    def test_missing_milestone_description_is_rejected(self) -> None:
        request = valid_request()
        del request["milestone_description"]
        errors = schema.validate_request(request)
        self.assertIn("milestone_description:nonempty_text_required", errors)

    def test_blank_milestone_description_is_rejected(self) -> None:
        errors = schema.validate_request(valid_request(milestone_description="   "))
        self.assertIn("milestone_description:nonempty_text_required", errors)

    def test_non_dict_session_state_is_rejected(self) -> None:
        errors = schema.validate_request(valid_request(session_state="not a dict"))
        self.assertIn("session_state:object_required", errors)

    def test_non_bool_session_state_field_is_rejected(self) -> None:
        errors = schema.validate_request(
            valid_request(session_state={"new_scope_appeared": "yes"})
        )
        self.assertIn("session_state.new_scope_appeared:bool_required", errors)

    def test_unknown_session_state_keys_are_tolerated(self) -> None:
        errors = schema.validate_request(
            valid_request(session_state={"some_future_field": True})
        )
        self.assertEqual(errors, [])

    def test_retired_approval_boolean_is_accepted_but_not_a_schema_field(self) -> None:
        # Backwards-compatible: an old caller sending the retired key still
        # validates. But the key is no longer a declared field, so nothing
        # downstream can read it as a condition (pre_policy/engine tests
        # prove it changes nothing).
        errors = schema.validate_request(
            valid_request(session_state={"end_to_end_boundary_already_approved": True})
        )
        self.assertEqual(errors, [])
        self.assertNotIn(
            "end_to_end_boundary_already_approved", schema.SESSION_STATE_BOOL_FIELDS
        )
        self.assertNotIn(
            "end_to_end_boundary_already_approved", schema.SESSION_STATE_CLAIM_FIELDS
        )

    def test_missing_session_state_defaults_cleanly(self) -> None:
        request = valid_request()
        del request["session_state"]
        self.assertEqual(schema.validate_request(request), [])

    def test_non_string_caller_message_is_rejected(self) -> None:
        errors = schema.validate_request(valid_request(caller_message=123))
        self.assertIn("caller_message:text_required", errors)

    def test_missing_caller_message_defaults_cleanly(self) -> None:
        request = valid_request()
        del request["caller_message"]
        self.assertEqual(schema.validate_request(request), [])

    def test_string_identity_claims_are_accepted(self) -> None:
        errors = schema.validate_request(
            valid_request(
                session_state={
                    "session_id": "sess-1",
                    "worktree": "/tmp/wt",
                    "task_id": "issue-162",
                    "requested_operation": "commit",
                }
            )
        )
        self.assertEqual(errors, [])

    def test_non_string_identity_claim_is_rejected(self) -> None:
        errors = schema.validate_request(
            valid_request(session_state={"session_id": 42, "task_id": True})
        )
        self.assertIn("session_state.session_id:text_required", errors)
        self.assertIn("session_state.task_id:text_required", errors)


class ResponseSchemaFieldsTest(unittest.TestCase):
    def test_fields_are_the_expected_stable_set(self) -> None:
        self.assertEqual(
            schema.response_schema_fields(),
            (
                "schema_version",
                "outcome",
                "reason",
                "source",
                "authoritative",
                "approval_status",
                "approval_reason",
            ),
        )

    def test_approval_report_fields_are_declared_response_fields(self) -> None:
        for field in schema.APPROVAL_REPORT_FIELDS:
            self.assertIn(field, schema.response_schema_fields())


class SessionStateFieldsTest(unittest.TestCase):
    def test_two_distinct_expansion_triggers_replace_the_single_destructive_flag(
        self,
    ) -> None:
        self.assertIn("destructive_scope_expansion", schema.SESSION_STATE_BOOL_FIELDS)
        self.assertIn("critical_lane_expansion", schema.SESSION_STATE_BOOL_FIELDS)
        self.assertNotIn(
            "destructive_action_widening_scope", schema.SESSION_STATE_BOOL_FIELDS
        )

    def test_no_bool_field_is_approval_shaped(self) -> None:
        for field in schema.SESSION_STATE_BOOL_FIELDS:
            self.assertNotIn("approv", field)


class ApprovalStatusValuesTest(unittest.TestCase):
    def test_status_values_are_the_closed_documented_set(self) -> None:
        self.assertEqual(
            schema.APPROVAL_STATUS_VALUES,
            ("approved", "missing", "invalid", "mismatched", "expired", "not_checked"),
        )


class OutcomeValuesTest(unittest.TestCase):
    def test_outcome_values_are_exactly_the_seven_named_recommendations(self) -> None:
        self.assertEqual(
            schema.OUTCOME_VALUES,
            (
                "continue",
                "retry",
                "investigate",
                "rollback",
                "split-follow-up",
                "pause-for-human",
                "complete",
            ),
        )


if __name__ == "__main__":
    unittest.main()
