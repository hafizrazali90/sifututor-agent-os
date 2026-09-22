#!/usr/bin/env python3
"""Three cheap, always-safe guards read from
scripts/agent-checks/codex-pre-tool-use.py (SURVEY.md section 5).

Today these exist only on the Codex side. Folding them into shared checks
lets the Claude adapter opt into the same policy instead of relying solely
on settings.local.json deny rules for an overlapping-but-not-identical set
of protections. test_parity_codex_safety_guards.py proves these three
agree with the real Codex script.
"""
from __future__ import annotations

import re

from models import Decision, HookRequest, Severity

_RESET_HARD_RE = re.compile(r"(^|[;&|]\s*)git\s+reset\s+--hard\b")
_CHECKOUT_DASHDASH_RE = re.compile(r"(^|[;&|]\s*)git\s+checkout\s+--\b")
_RM_RF_PROTECTED_RE = re.compile(
    r"(^|[;&|]\s*)rm\s+-rf\s+(\S*/)?(live|\.workflow-rollout)(/|\s|$)"
)
_ENV_READ_RE = re.compile(
    r"(^|[;&|]\s*)(cat|sed|awk|perl|python3?|node|vim|nano|code)\b.*\s\.env(\.|\s|$)"
)


class NoVerifyBypassGuard:
    """Deny any command that tries to bypass hooks with --no-verify.

    This is a stricter policy than a Claude hook's own --no-verify skip
    switch (see SURVEY.md section 5): those hooks use --no-verify to skip
    THEMSELVES on explicit human override; this guard instead treats the
    presence of --no-verify anywhere as itself deniable. Both behaviors are
    real and intentional in the surveyed originals — this check reproduces
    the Codex one exactly, it does not reconcile the asymmetry.
    """

    name = "no_verify_bypass_guard"
    severity = Severity.REQUIRED
    expensive = False

    def applies(self, request: HookRequest) -> bool:
        return request.tool_name == "Bash" and bool(request.command.strip())

    def run(self, request: HookRequest) -> Decision:
        if "--no-verify" in request.command:
            return Decision.deny(
                self.name,
                reason="Command attempts to bypass hooks with --no-verify.",
                guidance="Do not bypass hooks or quality gates with --no-verify. "
                "Fix the underlying check instead of skipping it.",
            )
        return Decision.allow(self.name)


class DestructiveGitGuard:
    """Deny `git reset --hard` and `git checkout --` (discards work)."""

    name = "destructive_git_guard"
    severity = Severity.REQUIRED
    expensive = False

    def applies(self, request: HookRequest) -> bool:
        return request.tool_name == "Bash" and bool(request.command.strip())

    def run(self, request: HookRequest) -> Decision:
        command = request.command
        if _RESET_HARD_RE.search(command):
            return Decision.deny(
                self.name,
                reason="git reset --hard is destructive.",
                guidance="Ask Hafiz explicitly before using git reset --hard; it "
                "discards uncommitted work with no recovery path.",
            )
        if _CHECKOUT_DASHDASH_RE.search(command):
            return Decision.deny(
                self.name,
                reason="git checkout -- can discard user changes.",
                guidance="Ask Hafiz explicitly before using git checkout --; it "
                "discards unstaged changes to the named files with no recovery path.",
            )
        return Decision.allow(self.name)


class ProtectedPathGuard:
    """Deny rm -rf on live/.workflow-rollout, and direct .env reads."""

    name = "protected_path_guard"
    severity = Severity.REQUIRED
    expensive = False

    def applies(self, request: HookRequest) -> bool:
        return request.tool_name == "Bash" and bool(request.command.strip())

    def run(self, request: HookRequest) -> Decision:
        command = request.command
        if _RM_RF_PROTECTED_RE.search(command):
            return Decision.deny(
                self.name,
                reason="Command removes a protected live/ or .workflow-rollout/ path.",
                guidance="live/ is a read-only production snapshot and "
                ".workflow-rollout/ is a cross-project staging area; never delete "
                "either without explicit, path-specific human approval.",
            )
        if _ENV_READ_RE.search(command):
            return Decision.deny(
                self.name,
                reason="Command reads a .env file directly.",
                guidance="Do not read or print .env files or secrets. Use an "
                "approved scripts/agent-checks or scripts/agent-access wrapper "
                "that returns only a non-secret status field.",
            )
        return Decision.allow(self.name)
