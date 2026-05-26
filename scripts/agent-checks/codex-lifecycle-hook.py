#!/usr/bin/env python3
"""Lifecycle hooks that steer Sifututor Codex sessions into workflow skills."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
import urllib.request


WORKSPACE = Path("/Users/hafizrazali/Projects/Sifututor")
KODA_URL = "http://178.105.120.34:3848/mcp"
KODA_TIMEOUT = 2
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
PROJECT_ALIASES = {
    "sifututor_parent": "sifututor_parent",
    "sifututor-parent": "sifututor_parent",
    "parent-app": "sifututor_parent",
    "sifututor_tutor": "sifututor_tutor",
    "sifututor-tutor": "sifututor_tutor",
    "tutor-app": "sifututor_tutor",
    "ripple-suite": "ripple-suite",
    "ripple": "ripple-suite",
    "dashboard": "ripple-suite",
    "sifu-tutor": "sifu-tutor",
    "sifu": "sifu-tutor",
    "lls-frontend": "lls-frontend",
    "lls-mobile": "lls-mobile",
    "lls": "lls",
    "creative-hub": "creative-hub",
    "team-inbox": "team-inbox",
    "finch-inbox": "finch-inbox",
    "finch": "finch-inbox",
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


def detect_project_from_prompt(prompt: str) -> str:
    lower = prompt.lower()
    matches: list[tuple[int, str]] = []
    for alias, project in sorted(PROJECT_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        idx = lower.find(alias)
        if idx >= 0:
            matches.append((idx, project))
    if not matches:
        return ""
    matches.sort(key=lambda item: item[0])
    return matches[0][1]


def post_koda(payload: dict, headers: dict, session_id: str = "") -> tuple[str, str, str]:
    request_headers = dict(headers)
    if session_id:
        request_headers["Mcp-Session-Id"] = session_id
    try:
        req = urllib.request.Request(
            KODA_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers=request_headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=KODA_TIMEOUT) as resp:
            return (
                resp.read().decode("utf-8"),
                resp.headers.get("Content-Type", ""),
                resp.headers.get("Mcp-Session-Id", ""),
            )
    except Exception:
        return "", "", ""


def unwrap_sse(body: str, content_type: str) -> str:
    if body and "text/event-stream" in content_type:
        for line in body.splitlines():
            if line.startswith("data:"):
                return line[len("data:"):].strip()
    return body


def parse_koda_memories(body: str, content_type: str) -> list[dict]:
    try:
        response = json.loads(unwrap_sse(body, content_type))
        content = response.get("result", {}).get("content", [])
        text = ""
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text") or ""
                break
        memories = json.loads(text) if text else []
        return memories if isinstance(memories, list) else []
    except Exception:
        return []


def koda_context(prompt: str, project: str) -> str:
    api_key = os.environ.get("KODA_API_KEY", "")
    if not api_key or len(prompt.strip()) < 10:
        return ""

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {api_key}",
    }

    init_body, _init_type, session_id = post_koda(
        {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "codex-lifecycle-hook", "version": "1.0"},
            },
            "id": 1,
        },
        headers,
    )
    if not init_body or not session_id:
        return ""

    post_koda({"jsonrpc": "2.0", "method": "notifications/initialized"}, headers, session_id)

    prompt_project = detect_project_from_prompt(prompt)
    tag_project = prompt_project or (project if project != "Sifututor" else "")

    calls = [
        {"query": prompt[:500], "limit": 3},
    ]
    if tag_project:
        calls.insert(0, {"query": prompt[:500], "limit": 3, "tags": [tag_project]})

    memories: list[dict] = []
    seen: set[str] = set()
    for idx, arguments in enumerate(calls, start=2):
        body, content_type, _sid = post_koda(
            {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": "memory_search", "arguments": arguments},
                "id": idx,
            },
            headers,
            session_id,
        )
        for memory in parse_koda_memories(body, content_type):
            if not isinstance(memory, dict):
                continue
            memory_id = memory.get("id") or ""
            if memory_id and memory_id in seen:
                continue
            if memory_id:
                seen.add(memory_id)
            memories.append(memory)

    bullets = []
    for memory in memories[:3]:
        content = (memory.get("content") or "").strip().splitlines()[0][:180]
        memory_id = memory.get("id") or "memory"
        tags = memory.get("tags") or []
        tag_text = f" [{','.join(tags[:3])}]" if tags else ""
        if content:
            bullets.append(f"- ({memory_id}{tag_text}) {content}")

    if not bullets:
        return ""
    return "Relevant Koda memories (auto-injected, verify before relying):\n" + "\n".join(bullets)


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
        r"\$(task-router|verify|qa|commit|save-session|handoff|snapshot|diagnose|review|quick-check)\b",
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

    if any(word in normalized for word in ("quick check", "quick-check", "health check", "workflow doctor", "doctor", "wired correctly")):
        return (
            "$quick-check",
            [
                "Use $quick-check and run scripts/agent-checks/workflow-doctor.sh from the umbrella root.",
                "Report PASS/FAIL/PARTIAL with any workflow wiring problems before implementation.",
            ],
            "Prompt is asking to check workflow health.",
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
        memory_skills = {"$task-router", "$diagnose", "$verify", "$qa", "$review", "$commit"}
        memory_text = koda_context(prompt, project) if skill in memory_skills else ""
        memory_section = memory_text or "Relevant Koda memories: none injected or Koda unavailable; search manually if the task depends on prior decisions."
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
                    memory_section,
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
