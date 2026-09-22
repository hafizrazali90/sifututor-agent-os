#!/usr/bin/env python3
"""Codex PreToolUse guard for Sifututor Bash commands."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys

WORKSPACE = str(
    Path(os.environ.get("SIFUTUTOR_AGENT_OS_ROOT", Path(__file__).resolve().parents[2])).resolve()
)


def deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    sys.exit(0)


def context(message: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": message,
                }
            }
        )
    )
    sys.exit(0)


def read_request() -> tuple[str, str]:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return "", ""
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command") or tool_input.get("cmd") or ""
    cwd = tool_input.get("workdir") or tool_input.get("cwd") or payload.get("cwd") or ""
    explicit_cd = re.match(r"\s*cd\s+([^;&|]+?)\s*&&", str(command))
    if explicit_cd:
        cwd = explicit_cd.group(1).strip().strip("'\"")
    return str(command), str(cwd)


def run_guard(request_cwd: str = "") -> tuple[bool, str]:
    candidate_cwd = Path(request_cwd).expanduser() if request_cwd else Path.cwd()
    root = subprocess.run(
        ["git", "-C", str(candidate_cwd), "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    ).stdout.strip()
    if not root:
        root = WORKSPACE

    guard = os.path.join(root, "scripts", "agent-checks", "pre-commit-guard.sh")
    if not os.path.exists(guard):
        guard = os.path.join(WORKSPACE, "scripts", "agent-checks", "pre-commit-guard.sh")
    if not os.path.exists(guard):
        return True, "no shared guard in this repo"

    result = subprocess.run(
        [guard],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return result.returncode == 0, result.stdout.strip()


command, request_cwd = read_request()
compact = " ".join(command.split())

if not compact:
    sys.exit(0)

if "--no-verify" in compact:
    deny("Do not bypass hooks or quality gates with --no-verify.")

if re.search(r"(^|[;&|]\s*)git\s+reset\s+--hard\b", compact):
    deny("git reset --hard is destructive. Ask Hafiz explicitly before using it.")

if re.search(r"(^|[;&|]\s*)git\s+checkout\s+--(?:\s|$|\b)", compact):
    deny("git checkout -- can discard user changes. Ask Hafiz explicitly first.")

if re.search(r"(^|[;&|]\s*)rm\s+-rf\s+(\S*/)?(live|\.workflow-rollout)(/|\s|$)", compact):
    deny("Refusing to remove protected live/ or .workflow-rollout/ paths.")

if re.search(r"(^|[;&|]\s*)(cat|sed|awk|perl|python3?|node|vim|nano|code)\b.*\s\.env(\.|\s|$)", compact):
    deny("Refusing to read or edit .env files or secrets.")

if re.search(r"(^|[;&|]\s*)git\s+(checkout\s+-b|switch\s+-c)\s+([^\s]+)", compact):
    branch = re.search(r"(^|[;&|]\s*)git\s+(checkout\s+-b|switch\s+-c)\s+([^\s]+)", compact).group(3)
    allowed = re.compile(
        r"^(main|master|develop|staging|dev|live-qa|integration|sifu-staging|sifu-backport)$"
        r"|^(sifu|lls|learnest|nakngaji)-[a-z0-9][a-z0-9-]*$"
        r"|^release[/-][a-z0-9][a-z0-9./-]*$"
        r"|^(feat|feature|fix|refactor|hotfix|chore|docs|perf|test|ci)/[a-z0-9][a-z0-9-]*$"
    )
    if not allowed.match(branch):
        deny(f"Invalid branch name: {branch}. Use type/kebab-description.")

if re.search(r"(^|[;&|]\s*)git\s+commit\b", compact):
    if "$(cat <<" in compact or "<<EOF" in compact or "<<'EOF'" in compact:
        deny("Use direct git commit -m flags. HEREDOC commit messages are not hook-safe.")
    ok, output = run_guard(request_cwd)
    if not ok:
        deny(f"pre-commit-guard failed before git commit:\n{output}")
    context("pre-commit-guard passed before git commit.")

sys.exit(0)
