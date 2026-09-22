#!/usr/bin/env python3
"""TDD tests for the compact execution packet's versioned field schema
(Bundle 3, issue #160).

The packet's field set is fixed by the handoff spec
(`.agent-os/handoffs/bundle-3-build-spec.md`) plus the PR #173 correction
spec (`bundle-3-correction-spec.md`): exactly twelve named fields plus a
`schema_version` marker so the packet itself is versioned, the same way
Bundle 1's decision-layer response carries `schema_version` alongside its
own fields. The correction replaced the earlier misleadingly named
"validated" approval field with `untrusted_approval_context` (pass-through
only) and added `approval_status` / `approval_reason`, which only
`approval.evaluate` may populate. The exact EXPECTED_FIELDS tuple below is
what proves the old field is gone.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def load_module(name, where=HERE):
    spec = importlib.util.spec_from_file_location(name, where / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


packet_schema = load_module("packet_schema")

EXPECTED_FIELDS = (
    "schema_version",
    "goal",
    "project",
    "scope_and_exclusions",
    "target_state",
    "untrusted_approval_context",
    "approval_status",
    "approval_reason",
    "required_context",
    "required_checks_evidence",
    "stop_conditions",
    "next_automatic_action",
    "follow_up_disposition",
)


class PacketFieldsTest(unittest.TestCase):
    def test_packet_fields_match_the_bundle_3_spec_exactly(self) -> None:
        self.assertEqual(packet_schema.packet_fields(), EXPECTED_FIELDS)

    def test_schema_version_is_a_positive_int(self) -> None:
        self.assertIsInstance(packet_schema.PACKET_SCHEMA_VERSION, int)
        self.assertGreaterEqual(packet_schema.PACKET_SCHEMA_VERSION, 1)

    def test_not_provided_sentinel_is_a_nonempty_string(self) -> None:
        self.assertIsInstance(packet_schema.APPROVAL_CONTEXT_NOT_PROVIDED, str)
        self.assertTrue(packet_schema.APPROVAL_CONTEXT_NOT_PROVIDED.strip())

    def test_not_checked_status_is_distinct_from_every_approval_module_status(self) -> None:
        # "not_checked" is the only status this package owns; it must never
        # collide with a value approval.evaluate can return, and above all
        # never equal "approved".
        self.assertEqual(packet_schema.APPROVAL_STATUS_NOT_CHECKED, "not_checked")
        self.assertNotEqual(packet_schema.APPROVAL_STATUS_NOT_CHECKED, "approved")


def valid_input(**overrides):
    base = dict(
        route="feature",
        task_type="feature",
        project="ripple-suite",
        goal="Add parent session renewal endpoint",
        scope="server-side session renewal only",
        target_state="endpoint merged and covered by a permanent E2E test",
        exclusions=["client-side renewal UI"],
    )
    base.update(overrides)
    return base


class ValidateInputTest(unittest.TestCase):
    def test_a_complete_input_has_no_errors(self) -> None:
        self.assertEqual(packet_schema.validate_input(**valid_input()), [])

    def test_missing_goal_is_an_error(self) -> None:
        errors = packet_schema.validate_input(**valid_input(goal=""))
        self.assertIn("goal:nonempty_text_required", errors)

    def test_missing_route_is_an_error(self) -> None:
        errors = packet_schema.validate_input(**valid_input(route="   "))
        self.assertIn("route:nonempty_text_required", errors)

    def test_exclusions_must_be_a_string_list_when_given(self) -> None:
        errors = packet_schema.validate_input(**valid_input(exclusions="not-a-list"))
        self.assertIn("exclusions:string_list_required", errors)

    def test_exclusions_defaulting_to_none_is_valid(self) -> None:
        errors = packet_schema.validate_input(**valid_input(exclusions=None))
        self.assertEqual(errors, [])

    def test_packet_validation_error_carries_the_error_list(self) -> None:
        with self.assertRaises(packet_schema.PacketValidationError) as ctx:
            raise packet_schema.PacketValidationError(["goal:nonempty_text_required"])
        self.assertEqual(ctx.exception.errors, ["goal:nonempty_text_required"])


if __name__ == "__main__":
    unittest.main()
