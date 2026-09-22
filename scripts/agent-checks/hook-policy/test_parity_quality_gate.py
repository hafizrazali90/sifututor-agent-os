#!/usr/bin/env python3
"""Parity fixture: QualityGateCheck (ripple-suite config) vs the frozen
fixtures/originals/ripple_quality_gate_snapshot.py, exercised in a real
temp git repo so both sides read the same actual `git diff --cached`
output.

The snapshot is copied into <tmp_repo>/.claude/hooks/quality-gate.py before
each case, because the original script derives its own project root from
`dirname(dirname(__file__))` -- reproducing that layout is required for a
faithful run, not just convenient.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from check_quality_gate import RIPPLE_SUITE_CONFIG, QualityGateCheck, git_staged_files  # noqa: E402
from models import HookRequest, Outcome  # noqa: E402

SNAPSHOT = HERE / "fixtures" / "originals" / "ripple_quality_gate_snapshot.py"


class _TempGitRepo:
    """A real git repo with a chosen set of files staged."""

    def __init__(self, staged_files: list[str]):
        self._staged_files = staged_files
        self._tmp: tempfile.TemporaryDirectory | None = None
        self.root: Path | None = None

    def __enter__(self) -> Path:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.root, check=True)
        for rel in self._staged_files:
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("// fixture content\n")
        if self._staged_files:
            subprocess.run(["git", "add", *self._staged_files], cwd=self.root, check=True)
        hooks_dir = self.root / ".claude" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(SNAPSHOT, hooks_dir / "quality-gate.py")
        return self.root

    def __exit__(self, *exc):
        if self._tmp is not None:
            self._tmp.cleanup()


def run_original(repo_root: Path, command: str) -> str:
    """Return the original script's decision: 'allow' or 'ask_user'."""
    payload = {"tool_name": "Bash", "tool_input": {"command": command}}
    result = subprocess.run(
        [sys.executable, str(repo_root / ".claude" / "hooks" / "quality-gate.py")],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        cwd=repo_root,
        timeout=10,
        check=False,
    )
    if not result.stdout.strip():
        return "allow"
    data = json.loads(result.stdout)
    return data.get("hookSpecificOutput", {}).get("permissionDecision", "allow")


FIXTURE_CASES = [
    ("no staged files", [], "allow"),
    ("only docs staged", ["README.md"], "allow"),
    ("code file staged", ["src/modules/matching/lib/score.ts"], "ask_user"),
    ("critical path staged", ["src/middleware.ts"], "ask_user"),
    ("non-code-dir ts file", ["scratch/random.ts"], "allow"),
]


@unittest.skipUnless(SNAPSHOT.is_file(), "frozen quality-gate snapshot missing")
class QualityGateParityTests(unittest.TestCase):
    def test_matches_frozen_original_for_every_fixture(self):
        mismatches = []
        for label, staged, expected in FIXTURE_CASES:
            with _TempGitRepo(staged) as repo_root:
                command = 'git commit -m "feat: x"'
                original_decision = run_original(repo_root, command)

                check = QualityGateCheck(
                    RIPPLE_SUITE_CONFIG,
                    staged_files_provider=lambda cwd, r=repo_root: git_staged_files(str(r)),
                )
                ours = check.run(HookRequest(tool_name="Bash", command=command, cwd=str(repo_root)))
                ours_decision = "ask_user" if ours.outcome == Outcome.ASK_USER else "allow"

                if original_decision != ours_decision:
                    mismatches.append((label, staged, original_decision, ours_decision))
        self.assertEqual(mismatches, [], f"parity mismatches: {mismatches}")


if __name__ == "__main__":
    unittest.main()
