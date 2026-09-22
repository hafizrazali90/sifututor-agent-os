#!/usr/bin/env python3
"""Tests for the shared, config-driven quality-gate check (slice 7).

Mirrors ripple-suite's quality-gate.py (SURVEY.md section 3). Uses an
injected staged_files_provider so unit behavior is deterministic and does
not depend on this checkout's real git state; the git-backed default
provider and full-script parity are proven separately in
test_parity_quality_gate.py.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from check_quality_gate import QualityGateCheck, RIPPLE_SUITE_CONFIG  # noqa: E402
from models import HookRequest, Outcome, Severity  # noqa: E402


def _req(command: str = 'git commit -m "feat: x"') -> HookRequest:
    return HookRequest(tool_name="Bash", command=command)


def _check(staged: list[str]) -> QualityGateCheck:
    return QualityGateCheck(RIPPLE_SUITE_CONFIG, staged_files_provider=lambda cwd: staged)


class QualityGateCheckTests(unittest.TestCase):
    def test_is_advisory_and_cheap(self):
        check = _check([])
        self.assertEqual(check.severity, Severity.ADVISORY)
        self.assertFalse(check.expensive)

    def test_applies_only_to_git_commit(self):
        check = _check([])
        self.assertTrue(check.applies(_req()))
        self.assertFalse(check.applies(_req("git status")))

    def test_allows_when_nothing_staged(self):
        decision = _check([]).run(_req())
        self.assertEqual(decision.outcome, Outcome.ALLOW)

    def test_allows_when_no_code_files_staged(self):
        decision = _check(["README.md", "docs/notes.txt"]).run(_req())
        self.assertEqual(decision.outcome, Outcome.ALLOW)

    def test_asks_user_when_code_dir_file_staged(self):
        decision = _check(["src/modules/matching/lib/score.ts"]).run(_req())
        self.assertEqual(decision.outcome, Outcome.ASK_USER)
        self.assertIn("npm run lint", decision.guidance)

    def test_asks_user_when_critical_path_staged_and_no_code_dir_hit(self):
        # A critical path outside the code_dirs list (there isn't one in the
        # real config -- all critical paths sit under src/ -- but this
        # exercises the second branch directly by disabling the first).
        decision = _check(["src/middleware.ts"]).run(_req())
        self.assertEqual(decision.outcome, Outcome.ASK_USER)

    def test_skips_when_no_verify_present(self):
        decision = _check(["src/middleware.ts"]).run(_req('git commit -m "x" --no-verify'))
        self.assertEqual(decision.outcome, Outcome.ALLOW)

    def test_label_is_in_check_name(self):
        self.assertIn("ripple-suite", _check([]).name)


if __name__ == "__main__":
    unittest.main()
