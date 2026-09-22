#!/usr/bin/env python3
"""TDD tests for three cheap, always-safe guards read from
scripts/agent-checks/codex-pre-tool-use.py (SURVEY.md section 5), which
today have no Claude-side equivalent:

- NoVerifyBypassGuard: any command containing --no-verify is denied
  outright (Codex's policy is stricter than Claude's own hooks, which use
  --no-verify as their OWN skip switch -- this asymmetry is intentional and
  documented in SURVEY.md, not a bug this bundle "fixes").
- DestructiveGitGuard: `git reset --hard` and `git checkout --` are denied.
- ProtectedPathGuard: `rm -rf` on live/ or .workflow-rollout/, and direct
  reads of .env files via common text tools, are denied.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from check_codex_safety_guards import (  # noqa: E402
    DestructiveGitGuard,
    NoVerifyBypassGuard,
    ProtectedPathGuard,
)
from models import HookRequest, Outcome, Severity  # noqa: E402


def _req(command: str) -> HookRequest:
    return HookRequest(tool_name="Bash", command=command)


class NoVerifyBypassGuardTests(unittest.TestCase):
    def setUp(self):
        self.check = NoVerifyBypassGuard()

    def test_is_required_and_cheap(self):
        self.assertEqual(self.check.severity, Severity.REQUIRED)
        self.assertFalse(self.check.expensive)

    def test_denies_any_no_verify_command(self):
        for command in (
            'git commit -m "feat: x" --no-verify',
            "git push --no-verify",
        ):
            with self.subTest(command=command):
                decision = self.check.run(_req(command))
                self.assertEqual(decision.outcome, Outcome.DENY)

    def test_allows_plain_command(self):
        decision = self.check.run(_req('git commit -m "feat: x"'))
        self.assertEqual(decision.outcome, Outcome.ALLOW)


class DestructiveGitGuardTests(unittest.TestCase):
    def setUp(self):
        self.check = DestructiveGitGuard()

    def test_denies_reset_hard(self):
        decision = self.check.run(_req("git reset --hard HEAD~1"))
        self.assertEqual(decision.outcome, Outcome.DENY)

    def test_denies_checkout_dash_dash_no_space_form(self):
        # The real codex-pre-tool-use.py regex is `--\b`, which only matches
        # when -- is immediately followed by a word character with no space
        # (e.g. --foo). See SURVEY.md section 5 "known upstream gap": this
        # means the common `git checkout -- <path>` form (with a space) is
        # NOT actually caught by the original script today. This check
        # mirrors that exact behavior for parity rather than silently
        # "fixing" it — a real fix is separate, future, reviewed work.
        decision = self.check.run(_req("git checkout --foo"))
        self.assertEqual(decision.outcome, Outcome.DENY)

    def test_checkout_dash_dash_with_space_is_not_caught_matching_original_gap(self):
        decision = self.check.run(_req("git checkout -- file.txt"))
        self.assertEqual(decision.outcome, Outcome.ALLOW)

    def test_allows_soft_reset(self):
        decision = self.check.run(_req("git reset --soft HEAD~1"))
        self.assertEqual(decision.outcome, Outcome.ALLOW)

    def test_allows_normal_checkout(self):
        decision = self.check.run(_req("git checkout -b feat/x"))
        self.assertEqual(decision.outcome, Outcome.ALLOW)


class ProtectedPathGuardTests(unittest.TestCase):
    def setUp(self):
        self.check = ProtectedPathGuard()

    def test_denies_rm_rf_live(self):
        decision = self.check.run(_req("rm -rf live/sifu-tutor"))
        self.assertEqual(decision.outcome, Outcome.DENY)

    def test_denies_rm_rf_workflow_rollout(self):
        decision = self.check.run(_req("rm -rf .workflow-rollout/ripple-suite"))
        self.assertEqual(decision.outcome, Outcome.DENY)

    def test_denies_reading_env_file(self):
        decision = self.check.run(_req("cat .env.production"))
        self.assertEqual(decision.outcome, Outcome.DENY)

    def test_allows_rm_rf_elsewhere(self):
        decision = self.check.run(_req("rm -rf node_modules"))
        self.assertEqual(decision.outcome, Outcome.ALLOW)

    def test_allows_reading_normal_file(self):
        decision = self.check.run(_req("cat README.md"))
        self.assertEqual(decision.outcome, Outcome.ALLOW)


if __name__ == "__main__":
    unittest.main()
