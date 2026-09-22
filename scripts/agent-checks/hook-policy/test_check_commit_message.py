#!/usr/bin/env python3
"""TDD tests for the shared commit-message-format check (slice 3).

Mirrors .claude/hooks/conventional-commits.py (SURVEY.md section 2).
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from check_commit_message import CommitMessageCheck  # noqa: E402
from models import HookRequest, Outcome, Severity  # noqa: E402


def _req(command: str) -> HookRequest:
    return HookRequest(tool_name="Bash", command=command)


class CommitMessageCheckTests(unittest.TestCase):
    def setUp(self):
        self.check = CommitMessageCheck()

    def test_is_required_and_cheap(self):
        self.assertEqual(self.check.severity, Severity.REQUIRED)
        self.assertFalse(self.check.expensive)

    def test_ignores_non_commit_commands(self):
        self.assertFalse(self.check.applies(_req("git status")))
        self.assertFalse(self.check.applies(_req("git push")))

    def test_applies_to_git_commit(self):
        self.assertTrue(self.check.applies(_req('git commit -m "feat: add x"')))

    def test_skips_when_no_verify_present(self):
        decision = self.check.run(_req('git commit -m "bad message" --no-verify'))
        self.assertEqual(decision.outcome, Outcome.ALLOW)

    def test_allows_conventional_message(self):
        decision = self.check.run(_req('git commit -m "feat: add user authentication"'))
        self.assertEqual(decision.outcome, Outcome.ALLOW)

    def test_allows_conventional_message_with_scope(self):
        decision = self.check.run(_req('git commit -m "fix(api): handle null responses"'))
        self.assertEqual(decision.outcome, Outcome.ALLOW)

    def test_allows_emoji_prefixed_message(self):
        decision = self.check.run(_req('git commit -m "✨ feat: add user authentication"'))
        self.assertEqual(decision.outcome, Outcome.ALLOW)

    def test_rejects_non_conventional_message(self):
        decision = self.check.run(_req('git commit -m "fixed a thing"'))
        self.assertEqual(decision.outcome, Outcome.DENY)
        self.assertIn("Conventional Commits", decision.guidance)

    def test_allows_when_message_cannot_be_extracted(self):
        decision = self.check.run(_req("git commit --amend"))
        self.assertEqual(decision.outcome, Outcome.ALLOW)


if __name__ == "__main__":
    unittest.main()
