#!/usr/bin/env python3
"""Advisory lifecycle hooks for Sifututor Codex sessions."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys


WORKSPACE = Path("/Users/hafizrazali/Projects/Sifututor")
PROJECTS = {
    "sifu-tutor",
    "ripple-suite",
    "sifututor_tutor",
    "sifututor_parent",
    "lls",
    "lls-frontend",
    "lls-mobile",
    "creative-hub",
    "team-inbox",
    "finch-inbox",
}


def emit_context(event: str, message: str) -> None:
    print(
        json.dumps(
            {
                "continue": True,
                "hookSpecificOutput": {
                    "hookEventName": event,
                    "additionalContext": message,
                },
            }
        )
    )


def emit_system(message: str) -> None:
    print(json.dumps({"continue": True, "systemMessage": message}))


def read_payload() -> dict:
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def project_from_cwd(cwd: str) -> str:
    try:
        relative = Path(cwd).resolve().relative_to(WORKSPACE)
    except ValueError:
        return "Sifututor"
    if not relative.parts:
        return "Sifututor"
    first = relative.parts[0]
    return first if first in PROJECTS else "Sifututor"


def active_task_summary(project: str) -> str:
    if project == "Sifututor":
        return "Active task: umbrella workspace, no single project task selected."

    active = WORKSPACE / project / ".claude" / "tasks" / "active.json"
    if not active.exists():
        return f"Active task: none found for {project}."

    try:
        data = json.loads(active.read_text())
    except Exception as exc:  # noqa: BLE001 - hook should not break sessions.
        return f"Active task: could not read {active}: {exc}."

    task_id = data.get("activeTask") or data.get("id") or "none"
    route = data.get("route") or "unknown"
    task_file = data.get("taskFile") or data.get("file") or ""
    summary = f"Active task: {task_id}, route={route}."

    if task_id and task_id != "none":
        candidate = active.parent / f"{task_id}.json"
        if task_file:
            candidate = (active.parent / task_file).resolve()
        if candidate.exists():
            try:
                task = json.loads(candidate.read_text())
                for step in task.get("steps", []):
                    if step.get("status") not in ("done", "skipped"):
                        return f"{summary} Next step: {step.get('name', '?')}."
            except Exception:
                pass
    return summary


def nontrivial_prompt(prompt: str) -> bool:
    words = prompt.split()
    if len(words) >= 6:
        return True
    triggers = (
        "fix",
        "implement",
        "proceed",
        "commit",
        "verify",
        "qa",
        "review",
        "diagnose",
        "save",
        "handoff",
        "snapshot",
        "push",
    )
    lower = prompt.lower()
    return any(trigger in lower for trigger in triggers)


def main() -> int:
    payload = read_payload()
    event = payload.get("hook_event_name") or payload.get("hookEventName") or ""
    cwd = payload.get("cwd") or os.getcwd()
    project = project_from_cwd(cwd)
    active_summary = active_task_summary(project)

    if event == "SessionStart":
        source = payload.get("source") or "startup"
        emit_context(
            "SessionStart",
            "\n".join(
                [
                    f"Sifututor Codex session started via {source}.",
                    f"Project detected: {project}.",
                    active_summary,
                    "Use repo skills for workflow parity: $task-router, $verify, $qa, $commit, $save-session, $handoff, $snapshot, $diagnose, $review.",
                    "For non-trivial work: read AGENTS.md, search Koda, check active task state, and follow docs/agent-playbooks/.",
                ]
            ),
        )
        return 0

    if event == "UserPromptSubmit":
        prompt = str(payload.get("prompt") or "")
        if not nontrivial_prompt(prompt):
            return 0
        emit_context(
            "UserPromptSubmit",
            "\n".join(
                [
                    f"Sifututor prompt context: project={project}.",
                    active_summary,
                    "Before editing for non-trivial work, search Koda memory and use the matching repo skill/playbook.",
                    "Critical lanes require Phase A diagnosis before implementation: auth, payments, invoices, commissions, migrations, deployment, and mobile API contracts.",
                ]
            ),
        )
        return 0

    if event == "PreCompact":
        trigger = payload.get("trigger") or "unknown"
        emit_system(
            f"Sifututor PreCompact ({trigger}): before relying on compacted context, preserve current goal, active task, next step, dirty state, and durable lessons with $snapshot or $save-session."
        )
        return 0

    if event == "Stop":
        emit_system(
            "Sifututor Stop reminder: if meaningful work occurred, use $save-session before ending. Report Koda memory status, active task, guards, commits/pushes, remaining work, and blockers."
        )
        return 0

    return 0


raise SystemExit(main())
