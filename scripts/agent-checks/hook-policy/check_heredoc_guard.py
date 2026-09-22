#!/usr/bin/env python3
"""Shared HEREDOC-commit-message guard.

Behavior mirrors the inline check in scripts/agent-checks/codex-pre-tool-use.py
(SURVEY.md section 2): deny any `git commit` whose command text contains
`$(cat <<`, `<<EOF`, or `<<'EOF'`. Today only Codex enforces this; Claude's
conventional-commits.py silently mis-parses a HEREDOC message instead of
blocking it (documented as a known footgun in that script's own docstring).
test_parity_heredoc_guard.py proves this check agrees with the real Codex
script.
"""
from __future__ import annotations

from models import Decision, HookRequest, Severity

_GUIDANCE = """Use direct git commit -m flags. HEREDOC commit messages are not hook-safe.

  git commit -m "emoji type(scope): title" -m "Body." -m "Co-Authored-By: ..."

Do not use: git commit -m "$(cat <<'EOF' ... EOF)" """


class HeredocCommitGuard:
    name = "heredoc_commit_guard"
    severity = Severity.REQUIRED
    expensive = False

    def applies(self, request: HookRequest) -> bool:
        return request.tool_name == "Bash" and "git commit" in request.command

    def run(self, request: HookRequest) -> Decision:
        command = request.command
        if "$(cat <<" in command or "<<EOF" in command or "<<'EOF'" in command:
            return Decision.deny(
                self.name,
                reason="Commit command uses a HEREDOC-style message.",
                guidance=_GUIDANCE,
            )
        return Decision.allow(self.name)
