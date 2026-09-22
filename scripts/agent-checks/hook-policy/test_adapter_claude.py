#!/usr/bin/env python3
"""Tests for the thin Claude adapter (slice 10c).

This adapter is IMPORTABLE, DEMONSTRATION code only -- it is never invoked
by any real .claude/hooks/*.py file or settings.json registration (that is
the whole point of this bundle; see the PR body / SURVEY.md). These tests
call it directly, the same way a future real wrapper would, to prove the
payload translation and end-to-end wiring work.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from adapter_claude import build_request, handle_pretooluse  # noqa: E402
from default_checks import default_checks  # noqa: E402
from dispatcher import HookDispatcher  # noqa: E402


class ClaudeAdapterRequestTests(unittest.TestCase):
    def test_build_request_reads_claude_shape(self):
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "git status"},
            "cwd": "/repo",
        }
        request = build_request(payload)
        self.assertEqual(request.tool_name, "Bash")
        self.assertEqual(request.command, "git status")
        self.assertEqual(request.cwd, "/repo")

    def test_build_request_tolerates_missing_fields(self):
        request = build_request({})
        self.assertEqual(request.tool_name, "")
        self.assertEqual(request.command, "")
        self.assertEqual(request.cwd, "")


class ClaudeAdapterEndToEndTests(unittest.TestCase):
    def setUp(self):
        self.dispatcher = HookDispatcher(default_checks())

    def test_valid_branch_checkout_produces_no_output(self):
        payload = {"tool_name": "Bash", "tool_input": {"command": "git checkout -b feat/add-x"}}
        self.assertIsNone(handle_pretooluse(payload, self.dispatcher))

    def test_invalid_branch_checkout_denies(self):
        payload = {"tool_name": "Bash", "tool_input": {"command": "git checkout -b nonsense"}}
        output = handle_pretooluse(payload, self.dispatcher)
        self.assertIsNotNone(output)
        self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_bad_commit_message_denies(self):
        payload = {"tool_name": "Bash", "tool_input": {"command": 'git commit -m "no type here"'}}
        output = handle_pretooluse(payload, self.dispatcher)
        self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_printenv_denies_via_command_safety(self):
        payload = {"tool_name": "Bash", "tool_input": {"command": "printenv"}}
        output = handle_pretooluse(payload, self.dispatcher)
        self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_non_bash_tool_is_a_no_op(self):
        payload = {"tool_name": "Edit", "tool_input": {"command": "git checkout -b nonsense"}}
        self.assertIsNone(handle_pretooluse(payload, self.dispatcher))


if __name__ == "__main__":
    unittest.main()
