#!/usr/bin/env python3
"""Shared Conventional Commits format check.

Behavior mirrors .claude/hooks/conventional-commits.py (the umbrella copy
— see SURVEY.md section 2) exactly, including the "allow if no -m message
can be extracted" escape hatch. test_parity_commit_message.py proves this
check and the real script agree on the same inputs.
"""
from __future__ import annotations

import re

from models import Decision, HookRequest, Severity

_MESSAGE_RE = re.compile(r'git commit.*?-m\s+["\']([^"\']+)["\']')
_CONVENTIONAL_RE = re.compile(
    r"^[^\x00-\x7F\s]*\s*?(feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert|wip)"
    r"(\(.+\))?:\s.+"
)

_GUIDANCE = """Commit messages must follow Conventional Commits:
  [emoji] type(scope): description

Types: feat, fix, docs, style, refactor, perf, test, chore, ci, build, revert, wip

Examples:
  feat: add user authentication
  fix(api): handle null responses
  ✨ feat: add user authentication

Use -m flags directly, not HEREDOC."""


class CommitMessageCheck:
    name = "commit_message"
    severity = Severity.REQUIRED
    expensive = False

    def applies(self, request: HookRequest) -> bool:
        return request.tool_name == "Bash" and "git commit" in request.command

    def run(self, request: HookRequest) -> Decision:
        command = request.command
        if "--no-verify" in command:
            return Decision.allow(self.name)

        match = _MESSAGE_RE.search(command)
        if not match:
            return Decision.allow(self.name)

        first_line = match.group(1).split("\n")[0].strip()
        if _CONVENTIONAL_RE.match(first_line):
            return Decision.allow(self.name)

        return Decision.deny(
            self.name,
            reason=f"Invalid commit message format: {first_line}",
            guidance=_GUIDANCE,
        )
