#!/usr/bin/env python3
"""The commit hook must enforce commit.md: no agent name as a commit co-author unless Hafiz asks."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / ".claude" / "hooks" / "conventional-commits.py"


def run_hook(command: str) -> dict | None:
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    proc = subprocess.run([sys.executable, str(HOOK)], input=payload, capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout) if proc.stdout.strip() else None


def denied(command: str) -> str | None:
    out = run_hook(command)
    if not out:
        return None
    spec = out["hookSpecificOutput"]
    return spec["permissionDecisionReason"] if spec["permissionDecision"] == "deny" else None


GOOD = 'git commit -m "docs(agent-os): fix a typo (#1)"'


class AgentCoauthorTest(unittest.TestCase):
    def test_plain_commit_is_allowed(self) -> None:
        self.assertIsNone(denied(GOOD))

    def test_agent_coauthor_is_denied_and_cites_the_rule(self) -> None:
        for trailer in (
            "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>",
            "Co-authored-by: Claude <noreply@anthropic.com>",
            "Co-Authored-By: Codex <noreply@openai.com>",
            "Co-Authored-By: GitHub Copilot <copilot@github.com>",
            "Co-Authored-By: Gemini <gemini@google.com>",
            "Co-Authored-By: ChatGPT <x@openai.com>",
        ):
            with self.subTest(trailer=trailer):
                reason = denied(f'{GOOD} -m "{trailer}"')
                self.assertIsNotNone(reason)
                self.assertIn("commit.md", reason)

    def test_no_verify_does_not_bypass_it(self) -> None:
        self.assertIsNotNone(denied(f'{GOOD} --no-verify -m "Co-Authored-By: Claude <noreply@anthropic.com>"'))

    def test_a_human_coauthor_is_allowed(self) -> None:
        self.assertIsNone(denied(f'{GOOD} -m "Co-Authored-By: Helmi <helmi@sifututor.my>"'))

    def test_explicit_override_is_allowed(self) -> None:
        self.assertIsNone(denied(f'SIFUTUTOR_ALLOW_AGENT_COAUTHOR=1 {GOOD} -m "Co-Authored-By: Claude <noreply@anthropic.com>"'))

    def test_the_format_check_still_works(self) -> None:
        self.assertIsNotNone(denied('git commit -m "not conventional"'))

    def test_other_commands_are_ignored(self) -> None:
        self.assertIsNone(denied('echo "Co-Authored-By: Claude <noreply@anthropic.com>"'))

    def test_the_hook_no_longer_teaches_the_forbidden_line(self) -> None:
        text = HOOK.read_text()
        self.assertNotIn('-m "Co-Authored-By: ..."', text)


if __name__ == "__main__":
    unittest.main()
