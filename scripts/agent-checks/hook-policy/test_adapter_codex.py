#!/usr/bin/env python3
"""Tests for the thin Codex adapter (slice 10d) -- same shape as
test_adapter_claude.py, but reading the Codex payload shape read from
codex-pre-tool-use.py's read_request() (tool_input.command OR .cmd, and
cwd from tool_input.workdir/cwd or payload.cwd). NOT a live hook -- see
adapter_claude.py's docstring for the same disclaimer, which applies here
too.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from adapter_codex import build_request, handle_pretooluse  # noqa: E402
from default_checks import default_checks  # noqa: E402
from dispatcher import HookDispatcher  # noqa: E402


class CodexAdapterRequestTests(unittest.TestCase):
    def test_build_request_reads_command_field(self):
        payload = {"tool_name": "exec", "tool_input": {"command": "git status", "workdir": "/repo"}}
        request = build_request(payload)
        self.assertEqual(request.command, "git status")
        self.assertEqual(request.cwd, "/repo")

    def test_build_request_falls_back_to_cmd_field(self):
        payload = {"tool_name": "exec", "tool_input": {"cmd": "git status"}}
        request = build_request(payload)
        self.assertEqual(request.command, "git status")

    def test_build_request_falls_back_to_payload_cwd(self):
        payload = {"tool_name": "exec", "tool_input": {"command": "git status"}, "cwd": "/repo2"}
        request = build_request(payload)
        self.assertEqual(request.cwd, "/repo2")


class CodexAdapterEndToEndTests(unittest.TestCase):
    def setUp(self):
        self.dispatcher = HookDispatcher(default_checks())

    def test_invalid_branch_checkout_denies(self):
        payload = {"tool_name": "exec", "tool_input": {"command": "git checkout -b nonsense"}}
        output = handle_pretooluse(payload, self.dispatcher)
        self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_heredoc_commit_denies(self):
        payload = {
            "tool_name": "exec",
            "tool_input": {"command": "git commit -m \"$(cat <<'EOF'\nfeat: x\nEOF\n)\""},
        }
        output = handle_pretooluse(payload, self.dispatcher)
        self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_no_verify_denies(self):
        payload = {"tool_name": "exec", "tool_input": {"command": "git push --no-verify"}}
        output = handle_pretooluse(payload, self.dispatcher)
        self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "deny")


if __name__ == "__main__":
    unittest.main()
