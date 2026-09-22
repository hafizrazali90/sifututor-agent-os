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


class ResponseSchemaFieldsTest(unittest.TestCase):
    def test_fields_are_the_expected_stable_set(self) -> None:
        self.assertEqual(
            schema.response_schema_fields(),
            ("schema_version", "outcome", "reason", "source", "authoritative"),
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
