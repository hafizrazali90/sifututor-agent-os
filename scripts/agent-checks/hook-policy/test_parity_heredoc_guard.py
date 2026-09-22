#!/usr/bin/env python3
"""Parity fixture: HeredocCommitGuard vs the real, unmodified
scripts/agent-checks/codex-pre-tool-use.py, invoked by its real path.

Only HEREDOC-shaped commit commands are exercised here (not plain `git
commit`, which would make the real script shell out to pre-commit-guard.sh
against this checkout's live git state -- out of scope for this fixture and
liable to fail on an unrelated dirty-tree reason unrelated to the policy
being tested).
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

from check_heredoc_guard import HeredocCommitGuard  # noqa: E402
from models import HookRequest, Outcome  # noqa: E402

CODEX_SCRIPT = ROOT / "scripts" / "agent-checks" / "codex-pre-tool-use.py"

FIXTURE_COMMANDS = [
    "git commit -m \"$(cat <<'EOF'\nfeat: add x\nEOF\n)\"",
    "git commit -m <<EOF",
    "git commit -m \"$(cat <<EOF\nfix: y\nEOF\n)\"",
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


@unittest.skipUnless(CODEX_SCRIPT.is_file(), "real Codex hook not present in this checkout")
class HeredocGuardParityTests(unittest.TestCase):
    def test_matches_real_codex_hook_for_every_fixture(self):
        check = HeredocCommitGuard()
        mismatches = []
        for command in FIXTURE_COMMANDS:
            original_allows = run_codex_original(command)
            ours_allows = check.run(HookRequest(tool_name="Bash", command=command)).outcome == Outcome.ALLOW
            if original_allows != ours_allows:
                mismatches.append((command, original_allows, ours_allows))
        self.assertEqual(mismatches, [], f"parity mismatches: {mismatches}")


if __name__ == "__main__":
    unittest.main()
