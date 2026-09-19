#!/usr/bin/env python3
"""Codex PostToolUse logger for failed Sifututor Bash commands."""

from __future__ import annotations

import datetime as dt
import json
import os
import sys

from secret_output_guard import safe_command_label


def extract_exit_code(tool_response: object) -> int | None:
    """Read structured exit metadata without assuming every response is an object.

    Current Codex releases may send model-facing command output as a string.
    That shape has no stable exit-code field, so it is a successful no-op for
    this metadata-only failure logger rather than a hook crash.
    """

    if not isinstance(tool_response, dict):
        return None
    value = tool_response.get("exit_code")
    return value if isinstance(value, int) else None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return 0
    tool_response = payload.get("tool_response")
    command = str(
        tool_input.get("command")
        or tool_input.get("cmd")
        or tool_input.get("input")
        or ""
    ).strip()
    exit_code = extract_exit_code(tool_response)

    if not command or exit_code in (None, 0):
        return 0

    path = os.path.expanduser("~/.codex-friction.log")
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(f"[{timestamp}] exit={exit_code} cwd={os.getcwd()}\n")
        handle.write(f"command={safe_command_label(command)} output=redacted\n\n")

    return 0


raise SystemExit(main())
