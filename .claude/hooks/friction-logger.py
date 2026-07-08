#!/usr/bin/env python3
"""
friction-logger.py — PostToolUse(Bash) hook
Captures Bash command failures (non-zero exit code, interrupted, etc.) and
appends them to ~/.claude-friction.log for later pattern analysis.

Inspired by ECC's continuous-learning pattern and claude-coach's PostToolUse
capture, but built in-house with zero third-party dependencies. No network
calls, no external services, no API costs — pure local observation.

Review with: /friction-review (skill at ~/.claude/skills/friction-review/)

Hard constraints:
- Silent on success — only logs failures
- Append-only — never modifies past entries
- Best-effort logging — failures to write the log do not block the user
- Stdlib only — no third-party deps
"""

import datetime
import json
import os
import sys
from pathlib import Path

LOG_FILE = Path.home() / ".claude-friction.log"
MAX_STDERR_CHARS = 250
MAX_CMD_CHARS = 300


def _detect_project(cwd: str) -> str:
    """Extract project name from cwd. Returns 'umbrella' for parent, 'unknown' otherwise."""
    if "/Sifututor/" in cwd:
        rest = cwd.split("/Sifututor/", 1)[1]
        if not rest:
            return "umbrella"
        parts = rest.split("/", 1)
        return parts[0] if parts[0] else "umbrella"
    if cwd.rstrip("/").endswith("/Sifututor"):
        return "umbrella"
    return "unknown"


def _is_failure(tool_response) -> bool:
    """Check signals to detect a FAILED Bash invocation.

    Conservative — only flag explicit failure signals. Avoid false positives from
    tools that legitimately write to stderr while succeeding (git fetch, find with
    permission warnings, npm install warnings, curl progress, etc.). Better to
    miss some failures than to fill the log with noise.
    """
    if not isinstance(tool_response, dict):
        return False
    # Signal 1: explicit success=false
    if tool_response.get("success") is False:
        return True
    # Signal 2: non-zero exit code
    exit_code = tool_response.get("exit_code")
    if isinstance(exit_code, int) and exit_code != 0:
        return True
    # Signal 3: interrupted (Ctrl+C, timeout)
    if tool_response.get("interrupted") is True:
        return True
    # Signal 4: explicit error field (non-empty)
    err = tool_response.get("error")
    if err and (not isinstance(err, str) or err.strip()):
        return True
    # NOTE: removed the "stderr without stdout" heuristic — too many false
    # positives (git, find, npm, curl all write to stderr while succeeding).
    return False


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if data.get("tool_name") != "Bash":
        sys.exit(0)

    tool_response = data.get("tool_response", {})
    if not _is_failure(tool_response):
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    session_id = data.get("session_id", "unknown")
    cwd = data.get("cwd", "") or os.environ.get("CLAUDE_PROJECT_DIR", "")

    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    cmd_raw = (tool_input.get("command") or "").strip()
    cmd = cmd_raw[:MAX_CMD_CHARS].replace("\n", " ⏎ ")

    stderr_raw = ""
    if isinstance(tool_response, dict):
        stderr_raw = (tool_response.get("stderr") or tool_response.get("error") or "").strip()
    stderr = stderr_raw[:MAX_STDERR_CHARS].replace("\n", " ⏎ ")

    exit_code = tool_response.get("exit_code", "?")
    project = _detect_project(cwd)
    sid = (session_id or "unknown")[:8]

    entry = f"[{timestamp}] [{sid}] [{project}] [exit={exit_code}] {cmd} | {stderr}\n"

    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        # Best-effort logging — never block the user on a failed log write
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
