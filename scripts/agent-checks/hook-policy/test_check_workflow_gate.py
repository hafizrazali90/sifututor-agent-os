#!/usr/bin/env python3
"""Tests for the shared, config-driven workflow-gate check (slice 8).

Mirrors ripple-suite's workflow-gate.py (SURVEY.md section 4). Uses an
injected task_state_provider so unit behavior does not depend on real
filesystem state; the file-backed default provider and full-script parity
are proven separately in test_parity_workflow_gate.py.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from check_workflow_gate import RIPPLE_SUITE_WORKFLOW_CONFIG, WorkflowGateCheck  # noqa: E402
from models import HookRequest, Outcome, Severity  # noqa: E402


def _req(command: str = 'git commit -m "feat: x"') -> HookRequest:
    return HookRequest(tool_name="Bash", command=command)


def _check(task: dict | None) -> WorkflowGateCheck:
    return WorkflowGateCheck(RIPPLE_SUITE_WORKFLOW_CONFIG, task_state_provider=lambda cwd: task)


class WorkflowGateCheckTests(unittest.TestCase):
    def test_is_required_and_cheap(self):
        check = _check(None)
        self.assertEqual(check.severity, Severity.REQUIRED)
        self.assertFalse(check.expensive)

    def test_applies_only_to_git_commit(self):
        check = _check(None)
        self.assertTrue(check.applies(_req()))
        self.assertFalse(check.applies(_req("git push")))

    def test_allows_when_no_active_task(self):
        decision = _check(None).run(_req())
        self.assertEqual(decision.outcome, Outcome.ALLOW)

    def test_allows_when_all_required_steps_done(self):
        task = {
            "route": "feature",
            "steps": [
                {"name": "verify", "status": "done"},
                {"name": "qa", "status": "done"},
                {"name": "release_notes", "status": "done"},
            ],
        }
        decision = _check(task).run(_req())
        self.assertEqual(decision.outcome, Outcome.ALLOW)

    def test_blocks_when_verify_not_done(self):
        task = {"route": "feature", "steps": [{"name": "verify", "status": "pending"}]}
        decision = _check(task).run(_req())
        self.assertEqual(decision.outcome, Outcome.DENY)
        self.assertIn("verify not done", decision.guidance)

    def test_regression_test_required_only_on_hotfix_and_bugfix(self):
        task = {"route": "feature", "steps": [{"name": "regression_test", "status": "pending"}]}
        # Not a hotfix/bugfix route -> regression_test is not checked at all here.
        decision = _check(task).run(_req())
        self.assertEqual(decision.outcome, Outcome.ALLOW)

        task2 = {"route": "bugfix", "steps": [{"name": "regression_test", "status": "pending"}]}
        decision2 = _check(task2).run(_req())
        self.assertEqual(decision2.outcome, Outcome.DENY)

    def test_regression_test_done_requires_red_and_green_evidence(self):
        task = {
            "route": "hotfix",
            "steps": [
                {
                    "name": "regression_test",
                    "status": "done",
                    "evidence": {"red_output": "", "green_output": "pass"},
                }
            ],
        }
        decision = _check(task).run(_req())
        self.assertEqual(decision.outcome, Outcome.DENY)
        self.assertIn("evidence incomplete", decision.guidance)

    def test_release_notes_required_on_small_change(self):
        task = {"route": "small-change", "steps": [{"name": "release_notes", "status": "pending"}]}
        decision = _check(task).run(_req())
        self.assertEqual(decision.outcome, Outcome.DENY)

    def test_skipped_steps_are_treated_as_satisfied(self):
        task = {
            "route": "hotfix",
            "steps": [
                {"name": "verify", "status": "skipped"},
                {"name": "qa", "status": "skipped"},
                {"name": "regression_test", "status": "skipped"},
                {"name": "defect_analysis", "status": "skipped"},
                {"name": "release_notes", "status": "skipped"},
            ],
        }
        decision = _check(task).run(_req())
        self.assertEqual(decision.outcome, Outcome.ALLOW)

    def test_skips_when_no_verify_present(self):
        task = {"route": "hotfix", "steps": [{"name": "verify", "status": "pending"}]}
        decision = _check(task).run(_req('git commit -m "x" --no-verify'))
        self.assertEqual(decision.outcome, Outcome.ALLOW)


if __name__ == "__main__":
    unittest.main()
