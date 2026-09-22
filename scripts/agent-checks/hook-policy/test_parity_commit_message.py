#!/usr/bin/env python3
"""Parity fixture: CommitMessageCheck vs the real, unmodified
.claude/hooks/conventional-commits.py, invoked by its real path.
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

from check_commit_message import CommitMessageCheck  # noqa: E402
from models import HookRequest, Outcome  # noqa: E402

CLAUDE_SCRIPT = ROOT / ".claude" / "hooks" / "conventional-commits.py"

FIXTURE_COMMANDS = [
    'git commit -m "feat: add user authentication"',
    'git commit -m "fix(api): handle null responses"',
    'git commit -m "✨ feat: add user authentication"',
    'git commit -m "fixed a thing"',
    'git commit -m "WIP"',
    'git commit -m "bad message" --no-verify',
    "git commit --amend",
    'git commit -m "chore(deps): bump lodash"',
    'git commit -m "refactor: simplify auth flow"',
]


def run_claude_original(command: str) -> bool:
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


@unittest.skipUnless(CLAUDE_SCRIPT.is_file(), "real Claude hook not present in this checkout")
class CommitMessageParityTests(unittest.TestCase):
    def test_matches_real_claude_hook_for_every_fixture(self):
        check = CommitMessageCheck()
        mismatches = []
        for command in FIXTURE_COMMANDS:
            original_allows = run_claude_original(command)
            ours_allows = check.run(HookRequest(tool_name="Bash", command=command)).outcome == Outcome.ALLOW
            if original_allows != ours_allows:
                mismatches.append((command, original_allows, ours_allows))
        self.assertEqual(mismatches, [], f"parity mismatches: {mismatches}")


if __name__ == "__main__":
    unittest.main()
