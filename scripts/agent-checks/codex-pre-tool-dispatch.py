#!/usr/bin/env python3
"""Run the shared Codex pre-tool guards once and combine their decisions."""

from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import runpy
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
GUARDS = (
    ("approval", HERE / "agent-os-approval-guard.py", None),
    ("secret-output", HERE / "secret_output_guard.py", None),
    ("command", HERE / "codex-pre-tool-use.py", {"Bash", "exec_command", "functions.exec", "exec"}),
)


def _run_guard(path: Path, payload_text: str) -> dict[str, Any] | None:
    old_stdin = sys.stdin
    old_argv = sys.argv
    output = io.StringIO()
    try:
        sys.stdin = io.StringIO(payload_text)
        sys.argv = [str(path)]
        with redirect_stdout(output):
            try:
                runpy.run_path(str(path), run_name="__main__")
            except SystemExit as exc:
                if exc.code not in (None, 0):
                    raise RuntimeError("guard exited unsuccessfully")
    finally:
        sys.stdin = old_stdin
        sys.argv = old_argv
    text = output.getvalue().strip()
    if not text:
        return None
    value = json.loads(text)
    return value.get("hookSpecificOutput") if isinstance(value, dict) else None


def dispatch(payload: dict[str, Any]) -> dict[str, Any] | None:
    payload_text = json.dumps(payload)
    tool_name = str(payload.get("tool_name") or payload.get("toolName") or "")
    contexts: list[str] = []
    for _label, path, tool_names in GUARDS:
        if tool_names is not None and tool_name not in tool_names:
            continue
        result = _run_guard(path, payload_text)
        if not result:
            continue
        if result.get("permissionDecision") == "deny":
            return result
        context = result.get("additionalContext")
        if isinstance(context, str) and context.strip():
            contexts.append(context.strip())
    if contexts:
        return {"hookEventName": "PreToolUse", "additionalContext": "\n".join(contexts)}
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError("unsupported payload")
        result = dispatch(payload)
    except Exception:
        result = {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "The unified safety check could not validate this tool call.",
        }
    if result:
        print(json.dumps({"hookSpecificOutput": result}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
