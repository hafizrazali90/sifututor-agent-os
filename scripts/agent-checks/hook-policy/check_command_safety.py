#!/usr/bin/env python3
"""Command-safety check: a thin wrapper, not a reimplementation.

scripts/agent-checks/secret_output_guard.py is already the single shared
implementation every existing hook routes through (directly, or via
claude_hook_dispatch.py) -- see SURVEY.md section 5. This check imports and
calls its real evaluate_command() function so hook-policy exposes it
through the same uniform Check interface as every other check, without
copying its (deliberately large and carefully ordered) regex table.
"""
from __future__ import annotations

from pathlib import Path
import sys

_AGENT_CHECKS_DIR = Path(__file__).resolve().parent.parent
if str(_AGENT_CHECKS_DIR) not in sys.path:
    sys.path.insert(0, str(_AGENT_CHECKS_DIR))

import secret_output_guard  # noqa: E402

from models import Decision, HookRequest, Severity


class CommandSafetyCheck:
    name = "command_safety"
    severity = Severity.REQUIRED
    expensive = False

    def applies(self, request: HookRequest) -> bool:
        return request.tool_name == "Bash" and bool(request.command.strip())

    def run(self, request: HookRequest) -> Decision:
        result = secret_output_guard.evaluate_command(request.command)
        if result.allowed:
            return Decision.allow(self.name)
        return Decision.deny(
            self.name,
            reason=result.reason,
            guidance=result.reason
            + " Use an approved scripts/agent-checks or scripts/agent-access "
            "wrapper that returns only the exact non-secret status field needed.",
        )
