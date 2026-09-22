#!/usr/bin/env python3
"""Tests for the default check registry (slice 10b) -- the concrete
assembly that demonstrates consolidation: one list of checks covering every
policy surveyed in SURVEY.md, reused by both adapters instead of each
reimplementing it.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from default_checks import default_checks  # noqa: E402
from models import Severity  # noqa: E402


class DefaultChecksTests(unittest.TestCase):
    def test_covers_every_surveyed_policy_by_name(self):
        names = {c.name for c in default_checks()}
        expected_prefixes = [
            "branch_name",
            "commit_message",
            "heredoc_commit_guard",
            "no_verify_bypass_guard",
            "destructive_git_guard",
            "protected_path_guard",
            "command_safety",
            "quality_gate:",
            "workflow_gate:",
        ]
        for prefix in expected_prefixes:
            with self.subTest(prefix=prefix):
                self.assertTrue(
                    any(name == prefix or name.startswith(prefix) for name in names),
                    f"no default check named/prefixed {prefix!r} in {sorted(names)}",
                )

    def test_every_default_check_is_cheap(self):
        # The two expensive example checks need an injected backend, so
        # they are deliberately not part of the always-on default registry
        # -- see check_expensive_examples.py's own docstring.
        for check in default_checks():
            self.assertFalse(check.expensive, f"{check.name} is unexpectedly expensive")

    def test_severities_are_set_meaningfully(self):
        by_name = {c.name: c for c in default_checks()}
        self.assertEqual(by_name["branch_name"].severity, Severity.REQUIRED)
        quality_gate = next(c for n, c in by_name.items() if n.startswith("quality_gate:"))
        self.assertEqual(quality_gate.severity, Severity.ADVISORY)


if __name__ == "__main__":
    unittest.main()
