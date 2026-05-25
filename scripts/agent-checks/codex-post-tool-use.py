#!/usr/bin/env python3
"""Codex PostToolUse logger for failed Sifututor Bash commands."""

from __future__ import annotations

import datetime as dt
import json
import os
import sys


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    tool_input = payload.get("tool_input") or {}
    tool_response = payload.get("tool_response") or {}
    command = str(tool_input.get("command") or "").strip()
    exit_code = tool_response.get("exit_code")

    if not command or exit_code in (None, 0):
        return 0

    path = os.path.expanduser("~/.codex-friction.log")
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(f"[{timestamp}] exit={exit_code} cwd={os.getcwd()}\n")
        handle.write(command + "\n\n")

    return 0


raise SystemExit(main())
