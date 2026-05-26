#!/usr/bin/env python3
"""Lifecycle hooks that steer Sifututor Codex sessions into workflow skills."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
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


def classify_prompt(prompt: str) -> tuple[str, list[str], str]:
    """Return a workflow skill, required actions, and a short reason."""

    lower = prompt.lower()
    normalized = re.sub(r"\s+", " ", lower).strip()

    direct_skill = re.search(
        r"\$(task-router|verify|qa|commit|save-session|handoff|snapshot|diagnose|review)\b",
        normalized,
    )
    if direct_skill:
        skill = f"${direct_skill.group(1)}"
        return (
            skill,
            [
                f"Use the explicitly requested {skill} skill.",
                "Read the skill body, then the linked shared playbook before acting.",
            ],
            "User explicitly invoked a Codex workflow skill.",
        )

    if any(word in normalized for word in ("save session", "save-session", "wrap up", "end session", "finish session")):
        return (
            "$save-session",
            [
                "Use $save-session before final response.",
                "Report Koda status, active task, guards, commits/pushes, remaining work, and blockers.",
            ],
            "Prompt is asking to preserve or close session state.",
        )

    if any(word in normalized for word in ("handoff", "hand off", "pass to claude", "pass to codex")):
        return (
            "$handoff",
            [
                "Use $handoff to produce a continuation-ready state summary.",
                "If this is also the end of meaningful work, follow with $save-session.",
            ],
            "Prompt is asking to transfer work to another agent or human.",
        )

    if any(word in normalized for word in ("snapshot", "compact", "compaction", "pause here", "context save")):
        return (
            "$snapshot",
            [
                "Use $snapshot to preserve current goal, task state, next move, and dirty files.",
                "Do not mark the task complete unless the user explicitly asks for a full save-session.",
            ],
            "Prompt is asking to preserve temporary working context.",
        )

    if any(word in normalized for word in ("review", "audit", "code review", "risk review", "pre-commit review")):
        return (
            "$review",
            [
                "Use $review and lead with findings.",
                "Check AGENTS.md, relevant CLAUDE.md, diffs, tests, and workflow violations.",
            ],
            "Prompt is asking for review/audit behavior.",
        )

    if any(word in normalized for word in ("diagnose", "debug", "root cause", "why", "failing", "failure", "broken", "bug")):
        return (
            "$diagnose",
            [
                "Use $diagnose before editing.",
                "For critical lanes, stop after Phase A diagnosis and wait for approval before implementation.",
            ],
            "Prompt is about bug/root-cause analysis.",
        )

    if any(word in normalized for word in ("verify", "gate 2a", "prove it works", "run checks", "test this")):
        return (
            "$verify",
            [
                "Use $verify and run checks from the project directory.",
                "Separate baseline failures from task-caused failures.",
            ],
            "Prompt is asking for implementation verification.",
        )

    if re.search(r"\bqa\b", normalized) or any(word in normalized for word in ("regression", "smoke", "manual qa", "visual qa")):
        return (
            "$qa",
            [
                "Use $qa and pick the QA tier from route/surface area.",
                "For bugfix/hotfix work, state the old failure mode and regression evidence.",
            ],
            "Prompt is asking for QA or regression evidence.",
        )

    if any(word in normalized for word in ("commit", "stage", "staging changes")):
        return (
            "$commit",
            [
                "Use $commit and run the shared pre-commit guard.",
                "Do not commit without explicit current-session approval of the exact file list.",
                "Do not push unless explicitly asked in the current session.",
            ],
            "Prompt is asking for commit preparation or commit execution.",
        )

    if any(word in normalized for word in ("push", "deploy", "release", "merge", "pull request", " pr ")):
        return (
            "$review",
            [
                "Use $review first as a pre-push/pre-release risk check.",
                "Confirm explicit approval before push, deploy, merge, or PR actions.",
                "Run $verify and $qa first if evidence is missing.",
            ],
            "Prompt is about a high-risk outbound action.",
        )

    if nontrivial_prompt(prompt):
        return (
            "$task-router",
            [
                "Use $task-router before implementation.",
                "Read nearest AGENTS.md and relevant CLAUDE.md.",
                "Search Koda memory and read active task state when present.",
            ],
            "Prompt appears to be non-trivial work.",
        )

    return (
        "",
        [],
        "Prompt appears trivial; no workflow skill required.",
    )


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
                    "Workflow automation is active. For non-trivial prompts, the UserPromptSubmit hook will select the required Codex workflow skill.",
                    "Available skills: $task-router, $verify, $qa, $commit, $save-session, $handoff, $snapshot, $diagnose, $review.",
                    "Default implementation path: $task-router -> $verify -> $qa -> $review -> $commit -> $save-session.",
                ]
            ),
        )
        return 0

    if event == "UserPromptSubmit":
        prompt = str(payload.get("prompt") or "")
        skill, actions, reason = classify_prompt(prompt)
        if not skill:
            return 0
        action_text = "\n".join(f"- {action}" for action in actions)
        emit_context(
            "UserPromptSubmit",
            "\n".join(
                [
                    "Sifututor workflow dispatcher:",
                    f"- Detected project: {project}.",
                    f"- Selected workflow skill: {skill}.",
                    f"- Reason: {reason}",
                    active_summary,
                    "Required actions:",
                    action_text,
                    "Do not bypass the selected skill. Read its SKILL.md and the linked docs/agent-playbooks/ file before acting.",
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
            "Sifututor Stop reminder: if meaningful work occurred, use $save-session before ending. Do not finish with only 'done.' Report Koda memory status, active task, guards, commits/pushes, remaining work, and blockers."
        )
        return 0

    return 0


raise SystemExit(main())
