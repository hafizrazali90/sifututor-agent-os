#!/usr/bin/env python3
"""Shared, restriction-only PreToolUse gate for enrolled Agent OS work packets."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys


def main() -> int:
    workspace = Path(os.environ.get("SIFUTUTOR_AGENT_OS_ROOT", Path(__file__).resolve().parents[2]))
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError("Unsupported payload")
        spec = importlib.util.spec_from_file_location(
            "agent_os_task_context", Path(__file__).with_name("agent-os-task-context.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if sys.argv[1:] == ["--identity"]:
            message = module.session_identity_context(payload)
            if message:
                print(json.dumps({"hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit", "additionalContext": message
                }}))
            return 0
        if sys.argv[1:] == ["--resume"]:
            message = module.session_start_context(workspace / ".agent-os" / "approval-state", payload)
            if message:
                print(json.dumps({"hookSpecificOutput": {
                    "hookEventName": "SessionStart", "additionalContext": message
                }}))
            return 0
        decision = module.check_tool_call(workspace / ".agent-os" / "approval-state", payload)
    except Exception:
        # Do not expose raw input, commands, exception messages or stderr.
        if sys.argv[1:] in (["--resume"], ["--identity"]):
            event = "SessionStart" if sys.argv[1:] == ["--resume"] else "UserPromptSubmit"
            message = (
                "The saved approval boundary could not be validated; do not infer authority from it."
                if event == "SessionStart"
                else "The current Agent OS session identity could not be validated; do not infer authority from it."
            )
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": event,
                "additionalContext": message
            }}))
            return 0
        decision = {"status": "deny", "reason": "Approval gate could not validate its input or state"}

    output = {"hookEventName": "PreToolUse"}
    if decision["status"] == "unenrolled":
        # Quiet legacy fallback, NOT authorization. Avoid per-tool token noise.
        return 0
    if decision["status"] == "deny":
        output.update(permissionDecision="deny", permissionDecisionReason=decision["reason"])
    else:
        # Matching a grant is not permission to override another gate.
        output["additionalContext"] = (
            decision["reason"] + ". Existing safety guards and native permissions still apply."
        )
    print(json.dumps({"hookSpecificOutput": output}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
