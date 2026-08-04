#!/usr/bin/env python3
"""Build one bounded, evidence-labelled cross-project Agent OS today snapshot.

The snapshot is a read model. It does not mutate Git, GitHub, Planner, Koda,
task files, Session Maps, or Mission Ledger state. Remote sources are optional
and each remote collector is invoked at most once per run.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
from typing import Callable


ROOT = Path(__file__).resolve().parents[2]
PROJECTS = (
    "kelas",
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
)
ATTENTION_GROUPS = (
    "needs_hafiz_now",
    "waiting_on_staff",
    "agent_can_continue",
    "monitor",
    "deferred",
)
GROUP_HEADINGS = {
    "needs_hafiz_now": "Needs Hafiz now",
    "waiting_on_staff": "Waiting on staff",
    "agent_can_continue": "Agent can continue",
    "monitor": "Monitor",
    "deferred": "Deferred",
}
CONFIDENCE_LEVELS = (
    "verified",
    "trusted",
    "reported",
    "historical",
    "unverified",
)
APPROVAL_STATES = ("not_required", "required_before_action", "unknown")
MISSION_ACTIVE = {"active"}
MISSION_DEFERRED = {"paused", "captured", "triaged", "parked"}
MISSION_CLOSED = {"done", "closed", "cancelled", "completed", "superseded"}
SENSITIVE_ACTIONS = (
    "rotate",
    "delete",
    "deploy",
    "merge",
    "push",
    "production repair",
    "production write",
    "change permission",
    "change access",
    "modify data",
)
PREPARATION_ACTIONS = (
    "prepare",
    "plan",
    "review",
    "inspect",
    "diagnose",
    "check",
    "draft",
    "read",
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def sanitize_text(value: object) -> str:
    """Redact common secrets and private identifiers from snapshot text."""
    text = re.sub(r"https?://\S+", "[url]", str(value or ""))
    text = re.sub(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        "[email]",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"\b(?:sk|pk|api|token|secret|key)[-_][A-Za-z0-9_-]{16,}\b",
        "[redacted]",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"\b(?:token|api[_ -]?key|secret|password)\s*[:=]\s*\S+",
        "[redacted]",
        text,
        flags=re.IGNORECASE,
    )
    return re.sub(r"\s+", " ", text).strip()


def sanitize_source_ref(value: object) -> str:
    """Keep safe local references and public GitHub links usable."""
    text = str(value or "").strip()
    if re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(?:issues|pull)/\d+", text):
        return text
    if text and not re.match(r"^[a-z][a-z0-9+.-]*://", text, flags=re.IGNORECASE):
        return sanitize_text(text)
    return "[url]" if text else ""


def render_source_ref(value: object) -> str:
    text = sanitize_source_ref(value)
    if text.startswith("https://github.com/"):
        return f" ([source]({text}))"
    return f" (`{text}`)" if text else ""


def run_command(
    command: list[str],
    *,
    cwd: Path,
    timeout: int = 30,
) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return 1, "", sanitize_text(error)
    return completed.returncode, completed.stdout, completed.stderr


def file_freshness(path: Path, now: datetime) -> str:
    try:
        modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
    except OSError:
        return "unknown"
    age_seconds = max(0, int((now - modified).total_seconds()))
    if age_seconds <= 86_400:
        label = "current"
    elif age_seconds <= 604_800:
        label = "recent"
    else:
        label = "stale"
    return f"{label}; source modified {modified.strftime('%Y-%m-%d %H:%M UTC')}"


def remote_freshness(value: object, now: datetime) -> str:
    text = str(value or "").strip()
    if not text:
        return f"checked {now.strftime('%Y-%m-%d %H:%M UTC')}; remote update unknown"
    try:
        updated = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return f"checked {now.strftime('%Y-%m-%d %H:%M UTC')}; remote update unknown"
    age_seconds = max(0, int((now - updated.astimezone(timezone.utc)).total_seconds()))
    if age_seconds <= 86_400:
        label = "current"
    elif age_seconds <= 604_800:
        label = "recent"
    else:
        label = "stale"
    return f"{label}; remote updated {updated.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"


def markdown_field(text: str, label: str) -> str:
    match = re.search(
        rf"(?mi)^-\s+\*\*{re.escape(label)}:\*\*\s*(.+?)(?=\n-\s+\*\*|\n##|\Z)",
        text,
        flags=re.DOTALL,
    )
    return sanitize_text(match.group(1)) if match else ""


def waiting_progress_rows(text: str) -> list[dict[str, str]]:
    """Extract unfinished progress-board rows whose next owner is another person."""
    section = re.search(
        r"(?ms)^## Progress Board\s*\n(?P<body>.*?)(?=^## |\Z)",
        text,
    )
    if not section:
        return []
    table_lines = [
        line.strip()
        for line in section.group("body").splitlines()
        if line.strip().startswith("|") and line.strip().endswith("|")
    ]
    if len(table_lines) < 3:
        return []

    def cells(line: str) -> list[str]:
        return [sanitize_text(cell.strip()) for cell in line.strip("|").split("|")]

    headers = [header.lower() for header in cells(table_lines[0])]
    required = {"item", "status", "owner", "next"}
    if not required.issubset(headers):
        return []
    indexes = {name: headers.index(name) for name in required}
    pending_markers = (
        "open",
        "pending",
        "await",
        "not merged",
        "not live",
        "review",
        "qa",
        "release",
        "blocked",
    )
    self_owner_markers = ("codex", "claude", "hafiz", "agent os", "existing product rule")
    results = []
    for line in table_lines[2:]:
        values = cells(line)
        if len(values) <= max(indexes.values()):
            continue
        item = values[indexes["item"]]
        status = values[indexes["status"]]
        owner = values[indexes["owner"]]
        next_action = values[indexes["next"]]
        normalized_status = status.lower()
        normalized_owner = owner.lower()
        if not item or not owner or not any(marker in normalized_status for marker in pending_markers):
            continue
        if any(marker in normalized_owner for marker in self_owner_markers) and not any(
            marker in normalized_owner
            for marker in ("developer", "staff", "reviewer", "release owner")
        ):
            continue
        results.append(
            {
                "title": item,
                "owner": owner,
                "status": status,
                "next_action": next_action or f"Follow up with {owner}.",
            }
        )
    return results


def approval_for_action(action: str) -> dict[str, str]:
    normalized = action.lower()
    if any(marker in normalized for marker in PREPARATION_ACTIONS) and not any(
        marker in normalized for marker in SENSITIVE_ACTIONS
    ):
        return {
            "state": "not_required",
            "reason": "Read-only preparation or evidence gathering can continue without approval.",
        }
    if any(marker in normalized for marker in SENSITIVE_ACTIONS):
        return {
            "state": "required_before_action",
            "reason": "Approval is required immediately before the named write, release, production, access, or destructive action.",
        }
    return {
        "state": "unknown",
        "reason": "Confirm the exact action boundary before treating this as an approval request.",
    }


def candidate(
    *,
    title: str,
    project: str,
    group: str,
    source: str,
    confidence: str,
    freshness: str,
    next_action: str,
    approval: dict[str, str] | None = None,
    source_ref: str = "",
) -> dict:
    if group not in ATTENTION_GROUPS:
        raise ValueError(f"unknown attention group: {group}")
    if confidence not in CONFIDENCE_LEVELS:
        raise ValueError(f"unknown confidence level: {confidence}")
    approval_value = approval or approval_for_action(next_action)
    if approval_value["state"] not in APPROVAL_STATES:
        raise ValueError(f"unknown approval state: {approval_value['state']}")
    return {
        "title": sanitize_text(title) or "Untitled responsibility",
        "project": sanitize_text(project) or "umbrella",
        "group": group,
        "source": source,
        "source_ref": sanitize_source_ref(source_ref),
        "confidence": confidence,
        "freshness": freshness or "unknown",
        "next_action": sanitize_text(next_action) or "Inspect the owning source.",
        "approval": approval_value,
    }


def collect_session_maps(root: Path, now: datetime, *, limit: int = 12) -> tuple[list[dict], dict]:
    directory = root / ".agent-os/session-maps"
    if not directory.is_dir():
        return [], {
            "name": "session_maps",
            "state": "unavailable",
            "checked_at": now.isoformat(),
            "detail": "session-map directory is missing",
        }

    files = sorted(
        (
            path
            for path in directory.glob("*.md")
            if not path.name.startswith("README") and "template" not in path.name
        ),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )[:limit]
    results = []
    for path in files:
        try:
            text = path.read_text()
        except OSError:
            continue
        lifecycle = markdown_field(text, "Lifecycle state").lower()
        if lifecycle in {"closed", "promoted", "handed off"}:
            continue
        title_match = re.search(r"(?m)^# Session Map:\s*(.+)$", text)
        title = title_match.group(1).strip() if title_match else path.stem
        decision = markdown_field(text, "Decision needed from Hafiz")
        next_action = markdown_field(text, "Next recommended move") or markdown_field(
            text, "Next action"
        )
        project = markdown_field(text, "Project") or "umbrella"
        if lifecycle in {"parked"}:
            group = "deferred"
        elif decision.lower().startswith("yes"):
            group = "needs_hafiz_now"
        else:
            group = "agent_can_continue"
        results.append(
            candidate(
                title=title,
                project=project,
                group=group,
                source="Session Map",
                source_ref=str(path.relative_to(root)),
                confidence="trusted",
                freshness=file_freshness(path, now),
                next_action=next_action or "Read the current Session Map pointer.",
                approval=(
                    {
                        "state": "required_before_action",
                        "reason": decision,
                    }
                    if decision.lower().startswith("yes")
                    else approval_for_action(next_action)
                ),
            )
        )
        for waiting in waiting_progress_rows(text)[:3]:
            results.append(
                candidate(
                    title=waiting["title"],
                    project=project,
                    group="waiting_on_staff",
                    source="Session Map",
                    source_ref=str(path.relative_to(root)),
                    confidence="trusted",
                    freshness=file_freshness(path, now),
                    next_action=(
                        f"{waiting['owner']} owns the next step: "
                        f"{waiting['next_action']}"
                    ),
                    approval={
                        "state": "not_required",
                        "reason": (
                            "This is staff-owned work. Hafiz only needs to intervene "
                            "if the owner reports a blocker or requests a decision."
                        ),
                    },
                )
            )
    return results, {
        "name": "session_maps",
        "state": "available",
        "checked_at": now.isoformat(),
        "detail": f"read {len(files)} bounded map file(s)",
    }


def split_markdown_sections(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"(?m)^###\s+(.+)$", text))
    sections = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append((match.group(1).strip(), text[match.end() : end]))
    return sections


def display_mission_title(raw_title: str) -> str:
    parts = re.split(r"\s+[—-]\s+", raw_title, maxsplit=1)
    return sanitize_text(parts[1] if len(parts) == 2 else raw_title)


def collect_mission_ledger(root: Path, now: datetime, *, limit: int = 30) -> tuple[list[dict], dict]:
    directory = root / "docs/agent-playbooks/mission-ledger"
    if not directory.is_dir():
        return [], {
            "name": "mission_ledger",
            "state": "unavailable",
            "checked_at": now.isoformat(),
            "detail": "Mission Ledger directory is missing",
        }

    results = []
    files = sorted(directory.glob("*.md"))
    for path in files:
        if path.name.startswith("_"):
            continue
        try:
            text = path.read_text()
        except OSError:
            continue
        for raw_title, body in split_markdown_sections(text):
            if "<" in raw_title or "short title" in raw_title.lower():
                continue
            status = markdown_field(body, "Status").lower()
            if not status or status in MISSION_CLOSED:
                continue
            if len(results) >= limit:
                break
            group = "agent_can_continue" if status in MISSION_ACTIVE else "deferred"
            if status not in MISSION_ACTIVE | MISSION_DEFERRED:
                group = "monitor"
            next_action = markdown_field(body, "Next action") or "Review the Mission Ledger item."
            results.append(
                candidate(
                    title=display_mission_title(raw_title),
                    project=markdown_field(body, "Project") or path.stem,
                    group=group,
                    source="Mission Ledger",
                    source_ref=str(path.relative_to(root)),
                    confidence="trusted",
                    freshness=file_freshness(path, now),
                    next_action=next_action,
                )
            )
        if len(results) >= limit:
            break
    return results, {
        "name": "mission_ledger",
        "state": "available",
        "checked_at": now.isoformat(),
        "detail": f"read {len(files)} ledger file(s), returned {len(results)} unresolved item(s)",
    }


def collect_active_tasks(root: Path, now: datetime) -> tuple[list[dict], dict]:
    results = []
    checked = 0
    for project in PROJECTS:
        path = root / project / ".claude/tasks/active.json"
        if not path.is_file():
            continue
        checked += 1
        try:
            data = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        active = data.get("activeTask")
        if not active:
            continue
        title = active if isinstance(active, str) else active.get("title") or active.get("id")
        task_file = data.get("taskFile")
        combined = json.dumps(data)
        next_action = "Open the active task file and continue its next unblocked step."
        if isinstance(task_file, str):
            target = (root / project / task_file).resolve()
            if target.is_file() and root.resolve() in target.parents:
                try:
                    task_text = target.read_text()
                    combined += "\n" + task_text
                    next_action = (
                        markdown_field(task_text, "Next action")
                        or markdown_field(task_text, "Next recommended move")
                        or next_action
                    )
                except OSError:
                    pass
        normalized = combined.lower()
        needs_hafiz = any(
            marker in normalized
            for marker in ("waiting for hafiz", "decision needed", "needs approval", "blocked on hafiz")
        )
        waiting_staff = any(
            marker in normalized for marker in ("waiting on staff", "waiting on developer", "staff review")
        )
        group = (
            "needs_hafiz_now"
            if needs_hafiz
            else "waiting_on_staff"
            if waiting_staff
            else "agent_can_continue"
        )
        results.append(
            candidate(
                title=title or f"{project} active task",
                project=project,
                group=group,
                source="Active task",
                source_ref=str(path.relative_to(root)),
                confidence="trusted",
                freshness=file_freshness(path, now),
                next_action=next_action,
                approval=(
                    {
                        "state": "required_before_action",
                        "reason": "The active task explicitly records a Hafiz decision or approval boundary.",
                    }
                    if needs_hafiz
                    else approval_for_action(next_action)
                ),
            )
        )
    return results, {
        "name": "active_tasks",
        "state": "available" if checked else "unavailable",
        "checked_at": now.isoformat(),
        "detail": f"checked {checked} project active-task file(s)",
    }


def collect_git_state(root: Path, now: datetime) -> tuple[list[dict], dict]:
    code, stdout, stderr = run_command(
        ["git", "status", "--short", "--branch"],
        cwd=root,
        timeout=15,
    )
    if code != 0:
        return [], {
            "name": "git",
            "state": "unavailable",
            "checked_at": now.isoformat(),
            "detail": sanitize_text(stderr) or "git status failed",
        }
    lines = stdout.splitlines()
    branch = lines[0].removeprefix("## ").strip() if lines else "unknown"
    dirty_count = max(0, len(lines) - 1)
    results = []
    if dirty_count or "ahead " in branch or "behind " in branch:
        results.append(
            candidate(
                title="Reconcile the umbrella workspace state",
                project="umbrella",
                group="agent_can_continue",
                source="Git",
                source_ref=str(root),
                confidence="verified",
                freshness=f"checked {now.strftime('%Y-%m-%d %H:%M UTC')}",
                next_action=(
                    f"Inspect exact bundles before any commit; branch state is {branch} "
                    f"with {dirty_count} dirty path(s)."
                ),
            )
        )
    return results, {
        "name": "git",
        "state": "available",
        "checked_at": now.isoformat(),
        "detail": f"branch={sanitize_text(branch)} dirty_paths={dirty_count}",
    }


def default_planner_loader(
    workspace_root: Path,
    *,
    task_limit: int,
    tool_root: Path = ROOT,
) -> dict:
    command = [
        "python3",
        str(tool_root / "scripts/agent-checks/agent-os-planner-probe.py"),
        "--json",
        "--include-tasks",
        "--task-limit",
        str(task_limit),
    ]
    code, stdout, stderr = run_command(command, cwd=workspace_root, timeout=45)
    if code != 0:
        return {
            "name": "planner",
            "state": "unavailable",
            "detail": sanitize_text(stderr) or "Planner snapshot invocation failed",
        }
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {
            "name": "planner",
            "state": "unavailable",
            "detail": "Planner snapshot returned non-JSON output; raw output omitted",
        }


def default_github_loader(root: Path) -> dict:
    command = [
        "gh",
        "search",
        "prs",
        "--owner",
        "Sifututor",
        "--state",
        "open",
        "--limit",
        "50",
        "--json",
        "number,title,url,repository,updatedAt,isDraft",
    ]
    code, stdout, stderr = run_command(command, cwd=root, timeout=45)
    if code != 0:
        return {
            "name": "github",
            "state": "unavailable",
            "detail": sanitize_text(stderr) or "GitHub PR search failed",
        }
    try:
        items = json.loads(stdout)
    except json.JSONDecodeError:
        return {
            "name": "github",
            "state": "unavailable",
            "detail": "GitHub search returned non-JSON output; raw output omitted",
        }
    normalized = []
    for item in items if isinstance(items, list) else []:
        repo = item.get("repository") or {}
        normalized.append(
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "updated_at": item.get("updatedAt"),
                "repository": repo.get("nameWithOwner") or repo.get("name"),
                "is_draft": bool(item.get("isDraft")),
            }
        )
    return {"name": "github", "state": "available", "items": normalized}


def planner_candidates(result: dict, now: datetime) -> list[dict]:
    candidates = []
    for task in result.get("task_summaries") or []:
        title = sanitize_text(task.get("title"))
        if not title:
            continue
        normalized = title.lower()
        group = (
            "needs_hafiz_now"
            if any(marker in normalized for marker in ("hafiz", "approval", "approve"))
            else "monitor"
        )
        next_action = (
            "Open the reported staff item and verify the current behavior. "
            "Read-only diagnosis can continue; any production repair needs scoped approval."
        )
        candidates.append(
            candidate(
                title=title,
                project="staff intake",
                group=group,
                source="Planner",
                confidence="reported",
                freshness=f"checked {now.strftime('%Y-%m-%d %H:%M UTC')}",
                next_action=next_action,
                approval={
                    "state": "not_required",
                    "reason": (
                        "Reading and diagnosing the reported symptom does not need approval. "
                        "A later production write or repair does."
                    ),
                },
            )
        )
    return candidates


def github_candidates(result: dict, now: datetime) -> list[dict]:
    candidates = []
    for item in result.get("items") or []:
        title = sanitize_text(item.get("title"))
        if not title:
            continue
        normalized = title.lower()
        group = (
            "waiting_on_staff"
            if any(marker in normalized for marker in ("independent review", "staff review", "waiting"))
            else "monitor"
        )
        candidates.append(
            candidate(
                title=title,
                project=item.get("repository") or "GitHub",
                group=group,
                source="GitHub",
                source_ref=item.get("url") or "",
                confidence="verified",
                freshness=remote_freshness(item.get("updated_at"), now),
                next_action=(
                    "Inspect the current PR evidence and owner. Review can continue without approval; "
                    "merge, deploy, or release still follows its normal gate."
                ),
                approval={
                    "state": "not_required",
                    "reason": (
                        "Reading or reviewing current evidence does not need approval. "
                        "Approval is evaluated immediately before any outward action."
                    ),
                },
            )
        )
    return candidates


def candidate_rank(item: dict) -> tuple[int, int, int, str]:
    confidence_score = {
        "verified": 5,
        "trusted": 4,
        "reported": 3,
        "historical": 2,
        "unverified": 1,
    }.get(item.get("confidence"), 0)
    source_score = {
        "Active task": 7,
        "Session Map": 6,
        "GitHub": 5,
        "Planner": 4,
        "Git": 3,
        "Mission Ledger": 2,
    }.get(item.get("source"), 0)
    freshness = str(item.get("freshness") or "").lower()
    freshness_score = (
        0
        if "stale" in freshness
        else 2
        if "recent" in freshness
        else 3
        if any(marker in freshness for marker in ("current", "checked"))
        else 1
    )
    return freshness_score, confidence_score, source_score, item.get("title", "").lower()


def bound_candidates(
    candidates: list[dict],
    *,
    per_group: int = 5,
) -> tuple[list[dict], dict[str, int], dict[str, int]]:
    grouped = {group: [] for group in ATTENTION_GROUPS}
    for item in candidates:
        grouped[item["group"]].append(item)

    bounded = []
    totals = {}
    omitted = {}
    for group in ATTENTION_GROUPS:
        ranked = sorted(grouped[group], key=candidate_rank, reverse=True)
        totals[group] = len(ranked)
        bounded.extend(ranked[:per_group])
        omitted[group] = max(0, len(ranked) - per_group)
    return bounded, totals, omitted


def build_snapshot(
    root: Path,
    *,
    planner_loader: Callable[[], dict] | None = None,
    github_loader: Callable[[], dict] | None = None,
    now: datetime | None = None,
) -> dict:
    root = root.resolve()
    generated = now or utc_now()
    candidates: list[dict] = []
    source_health: list[dict] = []

    for collector in (
        collect_session_maps,
        collect_active_tasks,
        collect_mission_ledger,
        collect_git_state,
    ):
        items, health = collector(root, generated)
        candidates.extend(items)
        source_health.append(health)

    planner_invocations = 0
    if planner_loader is not None:
        planner_invocations = 1
        planner_result = planner_loader()
        candidates.extend(planner_candidates(planner_result, generated))
        source_health.append(
            {
                "name": "planner",
                "state": planner_result.get("state", "unavailable"),
                "checked_at": generated.isoformat(),
                "detail": planner_result.get("evidence")
                or planner_result.get("detail")
                or f"returned {len(planner_result.get('task_summaries') or [])} bounded task summary item(s)",
            }
        )

    github_invocations = 0
    if github_loader is not None:
        github_invocations = 1
        github_result = github_loader()
        candidates.extend(github_candidates(github_result, generated))
        source_health.append(
            {
                "name": "github",
                "state": github_result.get("state", "unavailable"),
                "checked_at": generated.isoformat(),
                "detail": github_result.get("detail")
                or f"returned {len(github_result.get('items') or [])} bounded open PR item(s)",
            }
        )

    bounded_candidates, candidate_totals, omitted_counts = bound_candidates(candidates)
    returned_counts = {
        group: sum(item["group"] == group for item in bounded_candidates)
        for group in ATTENTION_GROUPS
    }
    return {
        "schema_version": 1,
        "generated_at": generated.isoformat(),
        "root": str(root),
        "source_health": source_health,
        "candidates": bounded_candidates,
        "candidate_totals": candidate_totals,
        "returned_counts": returned_counts,
        "omitted_counts": omitted_counts,
        "scan_budget": {
            "visible_snapshot_commands": 1,
            "planner_invocations": planner_invocations,
            "github_invocations": github_invocations,
            "maximum_targeted_follow_up_checks": 3,
            "persistent_cache_writes": 0,
        },
        "contract": {
            "attention_groups": list(ATTENTION_GROUPS),
            "confidence_levels": list(CONFIDENCE_LEVELS),
            "rule": (
                "Use this snapshot for first-pass discovery. Recheck only the top mutable claims "
                "that change today's recommendation; do not rerun every source."
            ),
        },
    }


def render_markdown(snapshot: dict) -> str:
    lines = [
        "# Agent OS Today Snapshot",
        "",
        f"- **Generated:** {snapshot['generated_at']}",
        f"- **Workspace:** `{snapshot['root']}`",
        "- **Meaning:** one bounded first pass; mutable top candidates may still need targeted verification",
        "",
        "## Source health",
        "",
        "| Source | State | Checked | Detail |",
        "| --- | --- | --- | --- |",
    ]
    for source in snapshot["source_health"]:
        lines.append(
            "| {name} | `{state}` | {checked} | {detail} |".format(
                name=sanitize_text(source.get("name")),
                state=sanitize_text(source.get("state")),
                checked=sanitize_text(source.get("checked_at")),
                detail=sanitize_text(source.get("detail")),
            )
        )

    grouped = {group: [] for group in ATTENTION_GROUPS}
    for item in snapshot["candidates"]:
        grouped[item["group"]].append(item)

    for group in ATTENTION_GROUPS:
        lines.extend(["", f"## {GROUP_HEADINGS[group]}", ""])
        if not grouped[group]:
            lines.append("Nothing currently identified in this group.")
            continue
        for index, item in enumerate(grouped[group], start=1):
            approval = item["approval"]
            lines.extend(
                [
                    f"{index}. **{item['title']}** — {item['project']}",
                    f"   - Source: {item['source']}"
                    + render_source_ref(item.get("source_ref")),
                    f"   - Confidence: `{item['confidence']}`",
                    f"   - Freshness: {item['freshness']}",
                    f"   - Recommended: {item['next_action']}",
                    f"   - Approval: `{approval['state']}` — {approval['reason']}",
                ]
            )
        omitted = snapshot.get("omitted_counts", {}).get(group, 0)
        if omitted:
            lines.append(
                f"\n_{omitted} lower-ranked candidate(s) omitted from this bounded first pass._"
            )

    budget = snapshot["scan_budget"]
    lines.extend(
        [
            "",
            "## Scan boundaries",
            "",
            f"- Planner collector invocations: {budget['planner_invocations']} (maximum 1).",
            f"- GitHub collector invocations: {budget['github_invocations']} (maximum 1).",
            (
                "- Targeted follow-up checks allowed: "
                f"{budget['maximum_targeted_follow_up_checks']} maximum, only for claims that change today's order."
            ),
            "- Persistent cache writes: 0; the snapshot is reused in memory for this briefing.",
            "- Read-only preparation does not need approval.",
            "- Ask for approval only immediately before the exact write, release, production, access, critical-lane implementation, or destructive action.",
            "- Planner remains reported intake; Koda and old chat remain historical leads; neither proves current implementation or production state.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(ROOT), help="workspace root to inspect")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    parser.add_argument(
        "--include-planner",
        action="store_true",
        help="invoke the approved read-only Planner collector once",
    )
    parser.add_argument(
        "--include-github",
        action="store_true",
        help="invoke one bounded read-only GitHub PR search",
    )
    parser.add_argument("--planner-task-limit", type=int, default=25)
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    planner_loader = (
        (lambda: default_planner_loader(root, task_limit=max(1, min(args.planner_task_limit, 50))))
        if args.include_planner
        else None
    )
    github_loader = (lambda: default_github_loader(root)) if args.include_github else None
    snapshot = build_snapshot(
        root,
        planner_loader=planner_loader,
        github_loader=github_loader,
    )
    if args.json:
        print(json.dumps(snapshot, indent=2))
    else:
        print(render_markdown(snapshot))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
