#!/usr/bin/env python3
"""Thin Claude PreToolUse adapter.

NOT a live hook. Nothing in .claude/hooks/ or settings.json calls this
file (see the PR body's explicit cutover statement and SURVEY.md). It
exists so the shared dispatcher can be exercised with the exact payload
shape a Claude PreToolUse hook actually receives
(`{tool_name, tool_input: {command}, cwd}`), instead of each real hook
reimplementing its own stdin parsing and JSON output formatting, per the
bundle spec's "thin per-agent adapters... that call into the one shared
dispatcher rather than each reimplementing policy."
"""
from __future__ import annotations

from dispatcher import HookDispatcher
from hook_output import dispatch_result_to_hook_output
from models import HookRequest


def build_request(payload: dict) -> HookRequest:
    tool_name = str(payload.get("tool_name") or "")
    tool_input = payload.get("tool_input") or {}
    command = str(tool_input.get("command") or "")
    cwd = str(payload.get("cwd") or tool_input.get("cwd") or "")
    return HookRequest(tool_name=tool_name, command=command, cwd=cwd, payload=payload)


def handle_pretooluse(payload: dict, dispatcher: HookDispatcher) -> dict | None:
    request = build_request(payload)
    result = dispatcher.dispatch(request)
    return dispatch_result_to_hook_output(result)
