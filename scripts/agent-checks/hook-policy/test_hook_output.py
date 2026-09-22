#!/usr/bin/env python3
"""Tests for the shared decision -> hookSpecificOutput JSON formatter
(slice 10a). Both existing agents already use the same wire shape (see
SURVEY.md sections 1-2 and 5): {"hookSpecificOutput": {"hookEventName":
"PreToolUse", "permissionDecision": ..., "permissionDecisionReason": ...}}.
This is the one place that shape gets written.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from dispatcher import DispatchResult  # noqa: E402
from hook_output import dispatch_result_to_hook_output  # noqa: E402
from models import Decision, HookRequest  # noqa: E402


def _result(decisions):
    return DispatchResult(HookRequest(tool_name="Bash", command="x"), decisions)


class HookOutputTests(unittest.TestCase):
    def test_all_allow_produces_no_output(self):
        output = dispatch_result_to_hook_output(_result([Decision.allow("a")]))
        self.assertIsNone(output)

    def test_deny_produces_deny_permission_decision(self):
        deny = Decision.deny("a", reason="bad", guidance="do the good thing")
        output = dispatch_result_to_hook_output(_result([deny]))
        self.assertEqual(
            output["hookSpecificOutput"]["permissionDecision"], "deny"
        )
        self.assertIn("bad", output["hookSpecificOutput"]["permissionDecisionReason"])
        self.assertIn("do the good thing", output["hookSpecificOutput"]["permissionDecisionReason"])
        self.assertEqual(output["hookSpecificOutput"]["hookEventName"], "PreToolUse")

    def test_ask_user_produces_ask_user_permission_decision(self):
        ask = Decision.ask_user("a", reason="confirm lint ran", guidance="run npm run lint")
        output = dispatch_result_to_hook_output(_result([ask]))
        self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "ask_user")

    def test_deny_wins_over_ask_user(self):
        ask = Decision.ask_user("a", reason="confirm lint ran")
        deny = Decision.deny("b", reason="bad", guidance="fix it")
        output = dispatch_result_to_hook_output(_result([ask, deny]))
        self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_degraded_alone_produces_additional_context_not_a_block(self):
        degraded = Decision.degraded("a", note="could not verify, proceed with caution")
        output = dispatch_result_to_hook_output(_result([degraded]))
        self.assertNotIn("permissionDecision", output["hookSpecificOutput"])
        self.assertIn("proceed with caution", output["hookSpecificOutput"]["additionalContext"])

    def test_degraded_combined_with_ask_user_keeps_ask_user_and_notes_degrade(self):
        degraded = Decision.degraded("a", note="could not verify staff notices")
        ask = Decision.ask_user("b", reason="confirm lint ran")
        output = dispatch_result_to_hook_output(_result([degraded, ask]))
        self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "ask_user")
        self.assertIn("could not verify staff notices", output["hookSpecificOutput"]["permissionDecisionReason"])


if __name__ == "__main__":
    unittest.main()
