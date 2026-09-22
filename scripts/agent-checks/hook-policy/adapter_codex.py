#!/usr/bin/env python3
"""Thin Codex PreToolUse adapter.

NOT a live hook. Nothing in .codex/config.toml or
scripts/agent-checks/codex-pre-tool-use.py calls this file (see the PR
body's explicit cutover statement and SURVEY.md). Reads the same payload
shape codex-pre-tool-use.py's own `read_request()` reads (`tool_input.command`
OR `tool_input.cmd`; cwd from `tool_input.workdir`/`tool_input.cwd`/`cwd`),
so the same shared dispatcher used by adapter_claude.py can be exercised
against Codex's real wire shape too -- the "thin per-agent adapters...
that call into the one shared dispatcher" the bundle spec asks for.
"""
from __future__ import annotations

from dispatcher import HookDispatcher
from hook_output import dispatch_result_to_hook_output
from models import HookRequest


def build_request(payload: dict) -> HookRequest:
    """Normalize a Codex payload into the shared canonical HookRequest.

    codex-pre-tool-use.py itself does not branch on `tool_name` at all --
    Codex only ever registers this hook for its shell-execution tool, so
    the script's own policy is "any command text present is a shell
    command to evaluate." The shared checks, by contrast, were written
    against Claude's literal `tool_name == "Bash"` gate (see
    check_branch_name.py etc.) so they don't accidentally fire on an Edit
    or Write payload. Bridging that difference is exactly this adapter's
    job: when command text is present, this adapter reports the canonical
    tool name "Bash" regardless of Codex's actual tool label (`exec`,
    `exec_command`, `functions.exec`, ...), so the same shared checks apply
    identically for both agents. The raw payload (including the real
    `tool_name`) is still preserved on `HookRequest.payload` for any check
    that needs it.
    """
    tool_input = payload.get("tool_input") or {}
    command = str(tool_input.get("command") or tool_input.get("cmd") or "")
    cwd = str(tool_input.get("workdir") or tool_input.get("cwd") or payload.get("cwd") or "")
    tool_name = "Bash" if command else str(payload.get("tool_name") or "")
    return HookRequest(tool_name=tool_name, command=command, cwd=cwd, payload=payload)


def handle_pretooluse(payload: dict, dispatcher: HookDispatcher) -> dict | None:
    request = build_request(payload)
    result = dispatcher.dispatch(request)
    return dispatch_result_to_hook_output(result)
