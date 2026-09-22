#!/usr/bin/env python3
"""Shared branch-name policy check.

Behavior mirrors .claude/hooks/validate-branch-name.py (the umbrella,
non-drifted copy — see SURVEY.md section 1) exactly: same base-branch
allowlist, same deployment/release patterns, same SSH skip, same
type/kebab-description pattern. test_parity_branch_name.py proves this
check and the real script agree on the same inputs.
"""
from __future__ import annotations

import re

from models import Decision, HookRequest, Severity

_BASE_BRANCHES = {
    "main", "master", "develop", "staging", "dev", "live-qa",
    "integration", "sifu-staging", "sifu-backport",
}
_DEPLOYMENT_RE = re.compile(r"^(sifu|lls|learnest|nakngaji)-[a-z0-9][a-z0-9-]*$")
_RELEASE_RE = re.compile(r"^release[/-][a-z0-9][a-z0-9./-]*$")
_VALID_TYPES = "feat|feature|fix|refactor|hotfix|chore|docs|perf|test|ci"
_CONVENTIONAL_RE = re.compile(rf"^({_VALID_TYPES})/[a-z0-9][a-z0-9-]*$")
_BRANCH_COMMAND_RE = re.compile(r"git (?:checkout -b|switch -c)\s+([^\s]+)")

_GUIDANCE = """All Sifututor projects use the same branch pattern:
  type/description

Valid types: feat, feature, fix, refactor, hotfix, chore, docs, perf, test, ci
Description: lowercase letters, numbers, hyphens only.

Examples:
  feat/add-login-screen
  fix/null-crash-on-payment
  docs/update-api-reference

Also allowed without validation: base branches (main, master, develop,
staging, dev, live-qa, integration, sifu-staging, sifu-backport),
deployment branches (sifu-*, lls-*, learnest-*, nakngaji-*), and release
branches (release/* or release-*)."""


class BranchNameCheck:
    name = "branch_name"
    severity = Severity.REQUIRED
    expensive = False

    def applies(self, request: HookRequest) -> bool:
        if request.tool_name != "Bash":
            return False
        return "git checkout -b" in request.command or "git switch -c" in request.command

    def run(self, request: HookRequest) -> Decision:
        command = request.command
        match = _BRANCH_COMMAND_RE.search(command)
        if not match:
            return Decision.allow(self.name)
        branch_name = match.group(1)

        if branch_name in _BASE_BRANCHES:
            return Decision.allow(self.name)
        if _DEPLOYMENT_RE.match(branch_name):
            return Decision.allow(self.name)
        if _RELEASE_RE.match(branch_name):
            return Decision.allow(self.name)
        if "ssh " in command and branch_name in command:
            return Decision.allow(self.name)
        if _CONVENTIONAL_RE.match(branch_name):
            return Decision.allow(self.name)

        return Decision.deny(
            self.name,
            reason=f"Branch name rejected: {branch_name}",
            guidance=_GUIDANCE,
        )
