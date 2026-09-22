#!/usr/bin/env python3
"""The default, cheap-only check registry.

This is the concrete "one shared dispatcher module that could, in
principle, replace the duplicated logic across those hooks" (bundle spec,
build item 2): one list, covering every policy documented in SURVEY.md,
that both adapter_claude.py and adapter_codex.py hand to a single
HookDispatcher instead of each reimplementing the policies separately.

Deliberately excludes the two expensive example checks
(check_expensive_examples.py) -- those need a real injected backend
(network client, model client, etc.) that this repo does not have, and
wiring them in here with a fake always-succeeding backend would misrepresent
them as live. Callers that do have a real backend add those checks
themselves; see hook_policy_cli.py for how a caller assembles the full set.

Uses ripple-suite's quality-gate/workflow-gate configs as the shipped
default parameterization (the best-documented, most complete of the
surveyed variants — see SURVEY.md sections 3-4). A real per-project
deployment would pass its own QualityGateConfig/WorkflowGateConfig instead.
"""
from __future__ import annotations

from check_branch_name import BranchNameCheck
from check_codex_safety_guards import DestructiveGitGuard, NoVerifyBypassGuard, ProtectedPathGuard
from check_command_safety import CommandSafetyCheck
from check_commit_message import CommitMessageCheck
from check_heredoc_guard import HeredocCommitGuard
from check_quality_gate import RIPPLE_SUITE_CONFIG, QualityGateCheck
from check_workflow_gate import RIPPLE_SUITE_WORKFLOW_CONFIG, WorkflowGateCheck


def default_checks() -> list:
    """Return a fresh list of check instances (checks are stateless per
    dispatch but constructed fresh to avoid any accidental cross-call
    state should a future check add caching)."""
    return [
        BranchNameCheck(),
        CommitMessageCheck(),
        HeredocCommitGuard(),
        NoVerifyBypassGuard(),
        DestructiveGitGuard(),
        ProtectedPathGuard(),
        CommandSafetyCheck(),
        QualityGateCheck(RIPPLE_SUITE_CONFIG),
        WorkflowGateCheck(RIPPLE_SUITE_WORKFLOW_CONFIG),
    ]
