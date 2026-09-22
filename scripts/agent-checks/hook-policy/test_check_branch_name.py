#!/usr/bin/env python3
"""TDD tests for the shared branch-name check (slice 2).

Mirrors the policy read from .claude/hooks/validate-branch-name.py in
SURVEY.md section 1. Behavior-identical parity against the real script (and
against codex-pre-tool-use.py's independent reimplementation) is proven
separately in test_parity_branch_name.py; this file locks the check's own
unit behavior first.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from check_branch_name import BranchNameCheck  # noqa: E402
from models import HookRequest, Outcome, Severity  # noqa: E402


def _req(command: str) -> HookRequest:
    return HookRequest(tool_name="Bash", command=command)


class BranchNameCheckTests(unittest.TestCase):
    def setUp(self):
        self.check = BranchNameCheck()

    def test_is_required_and_cheap(self):
        self.assertEqual(self.check.severity, Severity.REQUIRED)
        self.assertFalse(self.check.expensive)

    def test_ignores_non_branch_commands(self):
        self.assertFalse(self.check.applies(_req("git status")))
        self.assertFalse(self.check.applies(_req("npm test")))

    def test_applies_to_checkout_b_and_switch_c(self):
        self.assertTrue(self.check.applies(_req("git checkout -b feat/x")))
        self.assertTrue(self.check.applies(_req("git switch -c fix/y")))

    def test_only_bash_tool_applies(self):
        request = HookRequest(tool_name="Edit", command="git checkout -b feat/x")
        self.assertFalse(self.check.applies(request))

    def test_allows_valid_conventional_branch(self):
        decision = self.check.run(_req("git checkout -b feat/add-login-screen"))
        self.assertEqual(decision.outcome, Outcome.ALLOW)

    def test_allows_base_branches(self):
        for branch in ("main", "master", "develop", "staging", "dev", "live-qa",
                        "integration", "sifu-staging", "sifu-backport"):
            with self.subTest(branch=branch):
                decision = self.check.run(_req(f"git checkout -b {branch}"))
                self.assertEqual(decision.outcome, Outcome.ALLOW)

    def test_allows_deployment_branches(self):
        for branch in ("sifu-staging-2", "lls-prod", "learnest-dev", "nakngaji-dev"):
            with self.subTest(branch=branch):
                decision = self.check.run(_req(f"git checkout -b {branch}"))
                self.assertEqual(decision.outcome, Outcome.ALLOW)

    def test_allows_release_branches(self):
        decision = self.check.run(_req("git checkout -b release/2026-09"))
        self.assertEqual(decision.outcome, Outcome.ALLOW)

    def test_skips_validation_inside_ssh(self):
        decision = self.check.run(_req("ssh staging 'git checkout -b weirdName'"))
        self.assertEqual(decision.outcome, Outcome.ALLOW)

    def test_rejects_invalid_type(self):
        decision = self.check.run(_req("git checkout -b nonsense-branch"))
        self.assertEqual(decision.outcome, Outcome.DENY)
        self.assertIn("nonsense-branch", decision.reason)
        self.assertIn("type/description", decision.guidance)

    def test_rejects_uppercase_description(self):
        decision = self.check.run(_req("git checkout -b feat/AddLogin"))
        self.assertEqual(decision.outcome, Outcome.DENY)

    def test_malformed_command_does_not_crash(self):
        decision = self.check.run(_req("git checkout -b"))
        self.assertEqual(decision.outcome, Outcome.ALLOW)  # no branch name extracted -> skip


if __name__ == "__main__":
    unittest.main()
