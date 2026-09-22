#!/usr/bin/env python3
"""Tests for the live-hook parity harness.

Every assertion here is against a LIVE script invoked by its real path. If a
test fails, the live script's behaviour changed (or a documented outcome in
parity_harness.FIXTURES is wrong); there is no second implementation to be
out of sync with.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))  # scripts/agent-checks, for claude_hook_dispatch

import parity_harness as ph  # noqa: E402
import claude_hook_dispatch  # noqa: E402


class LiveScriptsPresentTests(unittest.TestCase):
    def test_every_authoritative_script_exists(self):
        for script in (ph.CLAUDE_BRANCH_HOOK, ph.CLAUDE_COMMIT_HOOK, ph.CODEX_GUARD):
            self.assertTrue(script.is_file(), f"missing live hook: {script}")


class ClaudeBranchNameParityTests(unittest.TestCase):
    def test_fixtures_match_documented_outcome(self):
        mismatches = ph.run_suite("claude:branch", ph.CLAUDE_BRANCH_HOOK, "Bash", ph.BRANCH_FIXTURES)
        self.assertEqual(mismatches, [])

    def test_non_bash_tool_is_ignored(self):
        run = ph.run_hook(ph.CLAUDE_BRANCH_HOOK, "git checkout -b nonsense-branch", tool_name="Read")
        self.assertEqual(run.decision, ph.ALLOW)


class ClaudeCommitMessageParityTests(unittest.TestCase):
    def test_fixtures_match_documented_outcome(self):
        mismatches = ph.run_suite("claude:commit", ph.CLAUDE_COMMIT_HOOK, "Bash", ph.COMMIT_FIXTURES)
        self.assertEqual(mismatches, [])


class CodexGuardParityTests(unittest.TestCase):
    def test_branch_fixtures_match_documented_outcome(self):
        mismatches = ph.run_suite("codex:branch", ph.CODEX_GUARD, "exec", ph.BRANCH_FIXTURES)
        self.assertEqual(mismatches, [])

    def test_safety_fixtures_match_documented_outcome(self):
        mismatches = ph.run_suite("codex:safety", ph.CODEX_GUARD, "exec", ph.CODEX_FIXTURES)
        self.assertEqual(mismatches, [])

    # Issue #177 regression fixtures, named so a future regex edit fails loudly.
    def test_issue_177_checkout_dashdash_path_is_denied(self):
        self.assertEqual(ph.run_hook(ph.CODEX_GUARD, "git checkout -- file.txt", "exec").decision, ph.DENY)

    def test_issue_177_bare_checkout_dashdash_is_denied(self):
        self.assertEqual(ph.run_hook(ph.CODEX_GUARD, "git checkout --", "exec").decision, ph.DENY)

    def test_issue_177_checkout_dashdash_nospace_is_still_denied(self):
        self.assertEqual(ph.run_hook(ph.CODEX_GUARD, "git checkout --foo", "exec").decision, ph.DENY)

    def test_issue_177_checkout_new_branch_is_still_allowed(self):
        self.assertEqual(ph.run_hook(ph.CODEX_GUARD, "git checkout -b feat/x", "exec").decision, ph.ALLOW)

    def test_issue_177_chained_checkout_dashdash_is_denied(self):
        self.assertEqual(ph.run_hook(ph.CODEX_GUARD, "git status && git checkout -- src/", "exec").decision, ph.DENY)

    def test_empty_command_is_allowed(self):
        self.assertEqual(ph.run_hook(ph.CODEX_GUARD, "", "exec").decision, ph.ALLOW)


class HookConfigurationAuditTests(unittest.TestCase):
    """The live audit_project_hook_configuration() judged on a planted fixture."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.umbrella = Path(self.tmp.name).resolve() / "umbrella"
        (self.umbrella / ".claude" / "hooks").mkdir(parents=True)
        self.project = self.umbrella / "ripple-suite"
        (self.project / ".claude" / "hooks").mkdir(parents=True)
        (self.project / ".claude" / "hooks" / "quality-gate.py").write_text("print('x')\n")
        (self.project / ".claude" / "settings.json").write_text(
            json.dumps(
                {
                    "hooks": {
                        "PreToolUse": [
                            {
                                "matcher": "Bash",
                                "hooks": [
                                    {
                                        "type": "command",
                                        "command": 'cd "$CLAUDE_PROJECT_DIR" && python3 .claude/hooks/quality-gate.py',
                                    }
                                ],
                            }
                        ]
                    }
                }
            )
        )

    def test_missing_umbrella_wrapper_blocks_readiness(self):
        findings = claude_hook_dispatch.audit_project_hook_configuration(self.umbrella, self.project)
        self.assertEqual([f.hook_script for f in findings], [".claude/hooks/quality-gate.py"])
        self.assertFalse(findings[0].ok)
        self.assertTrue(findings[0].blocks_readiness)

    def test_present_umbrella_wrapper_is_accepted(self):
        (self.umbrella / ".claude" / "hooks" / "quality-gate.py").write_text("print('x')\n")
        findings = claude_hook_dispatch.audit_project_hook_configuration(self.umbrella, self.project)
        self.assertEqual(len(findings), 1)
        self.assertTrue(findings[0].ok)


class DriftReportTests(unittest.TestCase):
    def test_planted_drift_is_reported_not_failed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            umbrella = root  # umbrella copy lives at the workspace root
            (umbrella / ".claude" / "hooks").mkdir(parents=True)
            for hook in ph.DRIFT_TRACKED_HOOKS:
                (umbrella / ".claude" / "hooks" / hook).write_text("shared\n")
            same = root / "same-project"
            drifted = root / "drifted-project"
            absent = root / "absent-project"
            for p in (same, drifted, absent):
                (p / ".claude" / "hooks").mkdir(parents=True)
            for hook in ph.DRIFT_TRACKED_HOOKS:
                (same / ".claude" / "hooks" / hook).write_text("shared\n")
                (drifted / ".claude" / "hooks" / hook).write_text("changed\n")
            (root / "live").mkdir()
            (root / "live" / ".claude" / "hooks").mkdir(parents=True)

            rows = ph.drift_report(root, umbrella=umbrella)

            by_project = {(r.project, r.hook): r.status for r in rows}
            for hook in ph.DRIFT_TRACKED_HOOKS:
                self.assertEqual(by_project[("same-project", hook)], "identical")
                self.assertEqual(by_project[("drifted-project", hook)], "drifted")
                self.assertEqual(by_project[("absent-project", hook)], "absent")
            self.assertNotIn("live", {r.project for r in rows})

    def test_live_workspace_drift_report_has_valid_shape(self):
        rows = ph.drift_report()
        if not rows:
            self.skipTest(f"no sub-project checkouts under {ph.workspace_root()}; set SIFUTUTOR_WORKSPACE_ROOT")
        for row in rows:
            self.assertIn(row.status, {"identical", "drifted", "absent"})
            self.assertIn(row.hook, ph.DRIFT_TRACKED_HOOKS)


if __name__ == "__main__":
    unittest.main()
