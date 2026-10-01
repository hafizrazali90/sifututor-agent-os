#!/usr/bin/env python3
"""#222: the coverage gate must diff against the branch's real base, not a
stale local main that another worktree has checked out."""

from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / ".claude" / "hooks" / "test-coverage-gate.py"


def load_hook():
    spec = importlib.util.spec_from_file_location("coverage_gate", HOOK)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def commit_file(repo: Path, name: str) -> str:
    (repo / name).parent.mkdir(parents=True, exist_ok=True)
    (repo / name).write_text(name)
    git(repo, "add", name)
    git(repo, "commit", "-q", "-m", f"add {name}")
    return git(repo, "rev-parse", "HEAD")


class CoverageGateBaseTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "user.email", "t@example.com")
        git(self.repo, "config", "user.name", "t")
        self.hook = load_hook()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_stale_local_main_does_not_add_other_peoples_files(self) -> None:
        stale = commit_file(self.repo, "README.md")
        # origin/main moved on with someone else's merged work.
        upstream = commit_file(self.repo, "src/others/BankMatchPanel.tsx")
        git(self.repo, "update-ref", "refs/remotes/origin/main", upstream)
        git(self.repo, "checkout", "-q", "-b", "fix/1-mine", upstream)
        # Local main stays behind, as when another worktree has it checked out.
        git(self.repo, "branch", "-f", "main", stale)
        commit_file(self.repo, "src/mine/Feature.tsx")

        self.assertEqual(
            self.hook._get_changed_files(self.repo), ["src/mine/Feature.tsx"]
        )

    def test_up_to_date_local_main_still_works_without_origin(self) -> None:
        base = commit_file(self.repo, "README.md")
        git(self.repo, "checkout", "-q", "-b", "fix/2-mine", base)
        commit_file(self.repo, "src/mine/Other.tsx")

        self.assertEqual(
            self.hook._get_changed_files(self.repo), ["src/mine/Other.tsx"]
        )


if __name__ == "__main__":
    unittest.main()
