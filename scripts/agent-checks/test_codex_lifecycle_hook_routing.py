#!/usr/bin/env python3
"""Tests for the Codex prompt routing: when it tells Codex to stop and wait.

Agreed with Hafiz on 17/10/2026: the diagnose-then-wait rule applies only to
production work, only on whole words, and not when he already said to proceed.
Commit and push follow the finish line he names.
"""

from __future__ import annotations

from pathlib import Path
import sys
import types
import unittest


ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = ROOT / "scripts" / "agent-checks" / "codex-lifecycle-hook.py"


def load_hook():
    """Load the hook without running it, the same way agent-os-eval-runner.py does."""
    sys.path.insert(0, str(HOOK_PATH.parent))  # the hook imports its sibling scripts
    source = HOOK_PATH.read_text(encoding="utf-8")
    entrypoint = "\nraise SystemExit(main())"
    if entrypoint not in source:
        raise RuntimeError(f"cannot find hook entrypoint in {HOOK_PATH}")
    module = types.ModuleType("codex_lifecycle_hook_for_test")
    module.__file__ = str(HOOK_PATH)
    exec(source.split(entrypoint, 1)[0], module.__dict__)
    return module


class CodexRoutingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hook = load_hook()

    def text(self, prompt: str) -> str:
        _skill, lines, reason = self.hook.classify_prompt(prompt)
        return " ".join(lines) + " " + reason

    def assert_no_stop(self, prompt: str) -> None:
        out = self.text(prompt).lower()
        self.assertNotIn("wait for approval", out, prompt)
        self.assertNotIn("phase a", out, prompt)

    def test_word_author_does_not_trigger_the_stop(self) -> None:
        self.assert_no_stop("Review the author's update to the invoice page")

    def test_reviewing_migration_changes_does_not_trigger_the_stop(self) -> None:
        self.assert_no_stop("review the migration changes in this branch")

    def test_payment_fix_without_production_does_not_stop(self) -> None:
        self.assert_no_stop("fix the payment rounding bug in the staging checkout")

    def test_production_fix_still_stops_for_approval(self) -> None:
        out = self.text("fix the invoice calculation on production").lower()
        self.assertIn("production", out)
        self.assertIn("wait for", out)

    def test_proceed_to_production_is_respected(self) -> None:
        self.assert_no_stop("fix the invoice bug on production, proceed until prod deploy, deploy ok")

    def test_skip_the_stop_is_respected(self) -> None:
        self.assert_no_stop("fix the invoice calculation on production, skip the diagnosis stop")

    def test_diagnose_route_does_not_stop_outside_production(self) -> None:
        self.assert_no_stop("why is the tutor page broken")
        self.assertNotIn("For critical lanes", self.text("why is the tutor page broken"))

    def test_diagnose_route_stops_for_production_trouble(self) -> None:
        out = self.text("why is production broken after the release").lower()
        self.assertIn("production", out)
        self.assertIn("wait for", out)

    def test_diagnose_route_respects_proceed_on_production(self) -> None:
        self.assert_no_stop("why is production broken, proceed and fix it, deploy ok")

    def test_commit_follows_the_finish_line(self) -> None:
        out = self.text("commit these changes")
        self.assertNotIn("exact file list", out)
        self.assertIn("finish line includes a commit", out)
        self.assertIn("finish line includes a push", out)


if __name__ == "__main__":
    unittest.main()
