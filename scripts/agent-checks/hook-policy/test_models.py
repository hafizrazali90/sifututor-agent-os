#!/usr/bin/env python3
"""TDD tests for hook-policy's core decision model.

Slice 1: a Decision carries a mandatory, actionable reason whenever it is
not a plain allow, and a deny without recovery guidance is a programming
error, not a valid decision. This is the hard requirement from the bundle
spec: "Actionable recovery guidance in every block message."
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from models import Decision, HookRequest, Outcome, Severity  # noqa: E402


class DecisionConstructionTests(unittest.TestCase):
    def test_allow_has_no_reason_required(self):
        decision = Decision.allow("branch_name")
        self.assertEqual(decision.outcome, Outcome.ALLOW)
        self.assertFalse(decision.blocks)

    def test_deny_requires_guidance(self):
        with self.assertRaises(ValueError):
            Decision.deny("branch_name", reason="bad name", guidance="")

    def test_deny_with_guidance_blocks(self):
        decision = Decision.deny(
            "branch_name",
            reason="bad name",
            guidance="Rename to type/kebab-description.",
        )
        self.assertTrue(decision.blocks)
        self.assertEqual(decision.outcome, Outcome.DENY)
        self.assertIn("Rename", decision.guidance)

    def test_ask_user_does_not_block(self):
        decision = Decision.ask_user("quality_gate", reason="ts files staged")
        self.assertFalse(decision.blocks)
        self.assertEqual(decision.outcome, Outcome.ASK_USER)

    def test_degraded_requires_visible_note_and_does_not_block(self):
        with self.assertRaises(ValueError):
            Decision.degraded("remote_policy", note="")
        decision = Decision.degraded("remote_policy", note="could not verify, proceed with caution")
        self.assertFalse(decision.blocks)
        self.assertEqual(decision.outcome, Outcome.DEGRADED)
        self.assertIn("proceed with caution", decision.note)


class HookRequestTests(unittest.TestCase):
    def test_defaults(self):
        request = HookRequest(tool_name="Bash", command="git status")
        self.assertEqual(request.cwd, "")
        self.assertEqual(request.payload, {})

    def test_severity_values_are_stable_strings(self):
        # Locked because adapters/tests match on these literal values.
        self.assertEqual(Severity.REQUIRED.value, "required")
        self.assertEqual(Severity.ADVISORY.value, "advisory")


if __name__ == "__main__":
    unittest.main()
