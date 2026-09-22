#!/usr/bin/env python3
"""TDD tests for the command-safety check (slice 6).

Unlike the other checks, this one does not reimplement anything: it wraps
scripts/agent-checks/secret_output_guard.py's real evaluate_command()
directly (SURVEY.md section 5). That module is already the one shared
implementation every existing hook is supposed to route through, so
"parity" here is definitional -- the wrapper test still asserts it
explicitly rather than assuming it.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from check_command_safety import CommandSafetyCheck  # noqa: E402
from models import HookRequest, Outcome, Severity  # noqa: E402

AGENT_CHECKS_DIR = HERE.parent
sys.path.insert(0, str(AGENT_CHECKS_DIR))
import secret_output_guard  # noqa: E402


def _req(command: str) -> HookRequest:
    return HookRequest(tool_name="Bash", command=command)


class CommandSafetyCheckTests(unittest.TestCase):
    def setUp(self):
        self.check = CommandSafetyCheck()

    def test_is_required_and_cheap(self):
        # Regex-only, no network/model call -- cheap despite the large
        # pattern table.
        self.assertEqual(self.check.severity, Severity.REQUIRED)
        self.assertFalse(self.check.expensive)

    def test_applies_to_every_bash_command(self):
        self.assertTrue(self.check.applies(_req("git status")))
        self.assertTrue(self.check.applies(_req("printenv")))

    def test_allows_ordinary_command(self):
        decision = self.check.run(_req("git status"))
        self.assertEqual(decision.outcome, Outcome.ALLOW)

    def test_denies_whole_environment_dump(self):
        decision = self.check.run(_req("printenv"))
        self.assertEqual(decision.outcome, Outcome.DENY)
        self.assertTrue(decision.guidance)

    def test_deny_reason_never_echoes_the_raw_command(self):
        # secret_output_guard deliberately never reflects the command text,
        # because the command itself may contain the credential.
        command = "echo $SUPER_SECRET_API_KEY"
        decision = self.check.run(_req(command))
        self.assertEqual(decision.outcome, Outcome.DENY)
        self.assertNotIn("SUPER_SECRET_API_KEY", decision.reason)
        self.assertNotIn("SUPER_SECRET_API_KEY", decision.guidance)

    def test_agrees_with_the_real_module_for_a_spread_of_commands(self):
        commands = [
            "git status",
            "printenv",
            "pm2 jlist",
            "cat .env.production",
            "cat README.md",
            "history",
            "curl -v -H 'Authorization: Bearer xyz' https://example.com",
        ]
        for command in commands:
            with self.subTest(command=command):
                expected = secret_output_guard.evaluate_command(command).allowed
                actual = self.check.run(_req(command)).outcome == Outcome.ALLOW
                self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
