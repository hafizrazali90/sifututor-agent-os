#!/usr/bin/env python3
"""TDD tests for the shared HEREDOC-commit-message guard (slice 4).

Mirrors the HEREDOC block in scripts/agent-checks/codex-pre-tool-use.py
(SURVEY.md section 2) — a check that today exists ONLY on the Codex side.
Claude's conventional-commits.py only warns in its docstring that HEREDOC
messages parse wrong; it never blocks them. Folding this into the shared
dispatcher closes that gap for both adapters.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from check_heredoc_guard import HeredocCommitGuard  # noqa: E402
from models import HookRequest, Outcome, Severity  # noqa: E402


def _req(command: str) -> HookRequest:
    return HookRequest(tool_name="Bash", command=command)


class HeredocCommitGuardTests(unittest.TestCase):
    def setUp(self):
        self.check = HeredocCommitGuard()

    def test_is_required_and_cheap(self):
        self.assertEqual(self.check.severity, Severity.REQUIRED)
        self.assertFalse(self.check.expensive)

    def test_ignores_non_commit_commands(self):
        self.assertFalse(self.check.applies(_req("echo '$(cat <<EOF'")))

    def test_allows_direct_dash_m_commit(self):
        decision = self.check.run(_req('git commit -m "feat: add x" -m "body"'))
        self.assertEqual(decision.outcome, Outcome.ALLOW)

    def test_rejects_heredoc_commit(self):
        command = "git commit -m \"$(cat <<'EOF'\nfeat: add x\nEOF\n)\""
        decision = self.check.run(_req(command))
        self.assertEqual(decision.outcome, Outcome.DENY)
        self.assertIn("HEREDOC", decision.guidance)

    def test_rejects_heredoc_variant_without_quotes(self):
        decision = self.check.run(_req("git commit -m <<EOF"))
        self.assertEqual(decision.outcome, Outcome.DENY)


if __name__ == "__main__":
    unittest.main()
