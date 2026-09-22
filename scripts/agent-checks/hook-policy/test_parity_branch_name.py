#!/usr/bin/env python3
"""Parity fixtures: prove BranchNameCheck agrees with the REAL, unmodified
scripts on the same inputs — not a copy, not a reimplementation guess.

Two real scripts are invoked, by their real repo path, exactly as a hook
runner would invoke them (JSON on stdin, read their exit code/stdout back):

1. .claude/hooks/validate-branch-name.py (Claude side)
2. scripts/agent-checks/codex-pre-tool-use.py (Codex side, independent
   inline reimplementation of the same policy — see SURVEY.md section 1)

Neither file is modified, written to, or imported. This test only reads
them via subprocess, the same way the real hook runners do, which is the
strongest available proof of behavior parity available inside this repo.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

from check_branch_name import BranchNameCheck  # noqa: E402
from models import HookRequest, Outcome  # noqa: E402

CLAUDE_SCRIPT = ROOT / ".claude" / "hooks" / "validate-branch-name.py"
CODEX_SCRIPT = ROOT / "scripts" / "agent-checks" / "codex-pre-tool-use.py"

FIXTURE_COMMANDS = [
    "git checkout -b feat/add-login-screen",
    "git checkout -b fix/null-crash-on-payment",
    "git switch -c docs/update-readme",
    "git checkout -b main",
    "git checkout -b staging",
    "git checkout -b sifu-staging-2",
    "git checkout -b lls-prod",
    "git checkout -b release/2026-09",
    "git checkout -b nonsense-branch",
    "git checkout -b feat/UPPERCASE",
    "git checkout -b weird_underscore_name",
    "git checkout -b bugfix/typo",  # "bugfix" is not in the valid-types list
]


def run_claude_original(command: str) -> bool:
    """Return True (allow) or False (deny) from the real Claude hook."""
    payload = {"tool_name": "Bash", "tool_input": {"command": command}}
    result = subprocess.run(
        [sys.executable, str(CLAUDE_SCRIPT)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )
    if not result.stdout.strip():
        return True
    data = json.loads(result.stdout)
    decision = data.get("hookSpecificOutput", {}).get("permissionDecision")
    return decision != "deny"


def run_codex_original(command: str) -> bool:
    """Return True (allow) or False (deny) from the real Codex hook."""
    payload = {"tool_name": "exec", "tool_input": {"command": command}}
    result = subprocess.run(
        [sys.executable, str(CODEX_SCRIPT)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )
    if not result.stdout.strip():
        return True
    data = json.loads(result.stdout)
    decision = data.get("hookSpecificOutput", {}).get("permissionDecision")
    return decision != "deny"


@unittest.skipUnless(CLAUDE_SCRIPT.is_file(), "real Claude hook not present in this checkout")
class ClaudeBranchNameParityTests(unittest.TestCase):
    def test_matches_real_claude_hook_for_every_fixture(self):
        check = BranchNameCheck()
        mismatches = []
        for command in FIXTURE_COMMANDS:
            original_allows = run_claude_original(command)
            ours_allows = check.run(HookRequest(tool_name="Bash", command=command)).outcome == Outcome.ALLOW
            if original_allows != ours_allows:
                mismatches.append((command, original_allows, ours_allows))
        self.assertEqual(mismatches, [], f"parity mismatches: {mismatches}")


@unittest.skipUnless(CODEX_SCRIPT.is_file(), "real Codex hook not present in this checkout")
class CodexBranchNameParityTests(unittest.TestCase):
    def test_matches_real_codex_hook_for_every_fixture(self):
        check = BranchNameCheck()
        mismatches = []
        for command in FIXTURE_COMMANDS:
            original_allows = run_codex_original(command)
            ours_allows = check.run(HookRequest(tool_name="Bash", command=command)).outcome == Outcome.ALLOW
            if original_allows != ours_allows:
                mismatches.append((command, original_allows, ours_allows))
        self.assertEqual(mismatches, [], f"parity mismatches: {mismatches}")


if __name__ == "__main__":
    unittest.main()
