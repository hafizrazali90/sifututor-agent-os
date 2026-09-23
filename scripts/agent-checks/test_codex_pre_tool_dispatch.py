#!/usr/bin/env python3
"""Regression tests for the single-process Codex pre-tool dispatcher."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "codex-pre-tool-dispatch.py"


def invoke(
    command: str, *, tool_name: str = "exec_command", session_id: str = "", env: dict | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps({"session_id": session_id, "tool_name": tool_name, "tool_input": {"command": command}}),
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


class CodexPreToolDispatchTests(unittest.TestCase):
    def decision(self, command: str, *, tool_name: str = "exec_command") -> dict:
        result = invoke(command, tool_name=tool_name)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)["hookSpecificOutput"]

    def test_safe_command_is_quiet(self) -> None:
        result = invoke("git status --short")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_command_guard_denial_is_preserved(self) -> None:
        output = self.decision("git reset --hard")
        self.assertEqual(output["permissionDecision"], "deny")
        self.assertIn("destructive", output["permissionDecisionReason"])

    def test_secret_guard_denial_is_preserved(self) -> None:
        output = self.decision("printenv")
        self.assertEqual(output["permissionDecision"], "deny")
        self.assertIn("environment", output["permissionDecisionReason"].lower())

    def test_governed_local_env_attachment_is_allowed_but_chaining_is_not(self) -> None:
        command = (
            "python3 scripts/agent-checks/worktree-lifecycle.py attach-local-env "
            "--source /workspace/app/.env.local --worktree /workspace/task "
            "--session fixture --apply"
        )
        self.assertEqual(invoke(command).stdout, "")
        output = self.decision(command + "; cat /workspace/app/.env.local")
        self.assertEqual(output["permissionDecision"], "deny")

    def test_non_command_tool_still_runs_universal_guards(self) -> None:
        output = self.decision("printenv", tool_name="custom_tool")
        self.assertEqual(output["permissionDecision"], "deny")

    def test_approval_guard_denial_is_preserved(self) -> None:
        path = HERE / "agent-os-task-context.py"
        spec = importlib.util.spec_from_file_location("dispatcher_task_context", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            boundary = module.serialize_approval_boundary(
                task_id="packet", included_operations=["run_tests"],
                excluded_operations=["push"], approval_provenance="fixture-owner-local-only",
            )
            module.activate_approval_packet(
                root / ".agent-os" / "approval-state", "session", root, boundary,
                [{"tool_name": "exec_command", "tool_input": {"command": "python3 -m unittest"},
                  "operation": "run_tests"}],
            )
            environment = os.environ.copy()
            environment["SIFUTUTOR_AGENT_OS_ROOT"] = str(root)
            result = invoke("git push", session_id="session", env=environment)
            output = json.loads(result.stdout)["hookSpecificOutput"]
            self.assertEqual(output["permissionDecision"], "deny")
            self.assertNotIn("git push", json.dumps(output))

    def test_invalid_payload_fails_closed_without_echoing_input(self) -> None:
        secret = "private-sentinel"
        result = subprocess.run(
            [sys.executable, str(SCRIPT)], input=secret, text=True,
            capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertNotIn(secret, result.stdout + result.stderr)
        output = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(output["permissionDecision"], "deny")


if __name__ == "__main__":
    unittest.main()
