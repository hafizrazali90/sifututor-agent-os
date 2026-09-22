#!/usr/bin/env python3
"""Parity fixtures: NoVerifyBypassGuard, DestructiveGitGuard, and
ProtectedPathGuard vs the real, unmodified
scripts/agent-checks/codex-pre-tool-use.py, invoked by its real path.

Only non-`git commit` fixtures are used so the real script never reaches
its pre-commit-guard.sh call (which depends on live git/worktree state and
is out of scope for this fixture).
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

from check_codex_safety_guards import (  # noqa: E402
    DestructiveGitGuard,
    NoVerifyBypassGuard,
    ProtectedPathGuard,
)
from models import HookRequest, Outcome  # noqa: E402

CODEX_SCRIPT = ROOT / "scripts" / "agent-checks" / "codex-pre-tool-use.py"

FIXTURE_COMMANDS = [
    "git push --no-verify",
    "git checkout -b feat/x --no-verify",
    "git reset --hard HEAD~1",
    "git reset --soft HEAD~1",
    "git checkout --foo",
    "git checkout -- file.txt",  # known upstream gap, see SURVEY.md section 5
    "rm -rf live/sifu-tutor",
    "rm -rf .workflow-rollout/ripple-suite",
    "rm -rf node_modules",
    "cat .env.production",
    "cat README.md",
    "git status",
]


def run_codex_original(command: str) -> bool:
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


def our_allows(command: str) -> bool:
    request = HookRequest(tool_name="Bash", command=command)
    for check in (NoVerifyBypassGuard(), DestructiveGitGuard(), ProtectedPathGuard()):
        if check.run(request).outcome != Outcome.ALLOW:
            return False
    return True


@unittest.skipUnless(CODEX_SCRIPT.is_file(), "real Codex hook not present in this checkout")
class CodexSafetyGuardsParityTests(unittest.TestCase):
    def test_matches_real_codex_hook_for_every_fixture(self):
        mismatches = []
        for command in FIXTURE_COMMANDS:
            original_allows = run_codex_original(command)
            ours = our_allows(command)
            if original_allows != ours:
                mismatches.append((command, original_allows, ours))
        self.assertEqual(mismatches, [], f"parity mismatches: {mismatches}")


if __name__ == "__main__":
    unittest.main()
