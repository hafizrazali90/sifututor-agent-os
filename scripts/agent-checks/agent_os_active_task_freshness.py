#!/usr/bin/env python3
"""Judge whether a canonical active-task pointer still describes current work.

Issue 113. Every project keeps its agent work pointer in
`.claude/tasks/active.json`. Until now the only automated check was
`python3 -m json.tool`, so a pointer written months ago, naming a task whose
steps are all finished and whose branch is long merged, passed every gate. A
fresh agent reading it resumes obsolete work with full confidence.

This module adds the missing signal. It answers one question per pointer:

    Does current repository evidence still support this claim?

Four rules keep it honest rather than noisy.

1. An idle pointer is never stale. `activeTask: null` claims nothing, so no
   agent can resume the wrong thing from it. Age alone is not a defect.
2. Only *canonical* checkouts are judged. A canonical project checkout is a
   registered project directly under the workspace root whose `.git` is a
   directory. A linked worktree carries a `.git` *file*, and the workspace
   currently holds dozens of historical worktrees with their own pointers.
   Those are history, not authority, and must never produce a failure.
3. Missing evidence is reported as unprovable, never resolved by guessing.
   The checker never invents, rewrites, or closes a task.
4. Only rules that survive their own false positives can fail a pointer.
   Branch-merge state is reported as evidence and never fails a claim on its
   own (see `_merge_note`), and the drift window is measured from the last
   change to *either* claim artifact (see `_last_claim_activity`).

Freshness is measured against repository activity, not the wall clock: a
pointer is drifted when the project's own Git history moved on far past the
last change to the claim. A genuinely paused project with no commits cannot
drift, and the result is reproducible on any day.

A claim is two files, not one. `active.json` records only *which* task is
claimed, so it legitimately never changes while a long task runs; progress
lands in the task file it names. Freshness therefore uses the more recent of
the two, which is what stops a six-week task from failing for an untouched
pointer.

Usage:
    agent_os_active_task_freshness.py [--root PATH] [--json] [--self-test]
                                      [--max-drift-days N] [--base-ref REF]

Exit codes: 0 clean or nothing canonical to check, 1 actionable drift,
2 the workspace root could not be read.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys


_THIS_FILE = globals().get("__file__")
_DEFAULT_ROOT = Path(_THIS_FILE).resolve().parents[2] if _THIS_FILE else Path.cwd()
ROOT = Path(os.environ.get("SIFUTUTOR_AGENT_OS_ROOT", _DEFAULT_ROOT)).resolve()

# Canonical project registry. Kept name-for-name with the other live registries
# by scripts/agent-checks/agent-os-project-registry-check.py.
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
    "finch-inbox",
    "cx-call-capture-android",
    "sims-owner-analytics",
)

POINTER_RELPATH = ".claude/tasks/active.json"
TERMINAL_STEP_STATUSES = frozenset({"done", "skipped"})
DEFAULT_MAX_DRIFT_DAYS = 30
DEFAULT_BASE_REFS = ("origin/main", "origin/master", "main", "master")
GIT_TIMEOUT_SECONDS = 20

STATE_ACTIVE = "active"
STATE_IDLE = "idle"
STATE_STALE_COMPLETED = "stale_completed"
STATE_STALE_DRIFTED = "stale_drifted"
STATE_DANGLING = "dangling"
STATE_INVALID = "invalid"
STATE_UNPROVABLE = "unprovable"
STATE_ABSENT = "absent"
STATE_NO_CHECKOUT = "no_checkout"
STATE_NON_CANONICAL = "non_canonical"

SEVERITY_OK = "ok"
SEVERITY_INFO = "info"
SEVERITY_WARN = "warn"
SEVERITY_FAIL = "fail"

CHECKOUT_CANONICAL = "canonical"
CHECKOUT_LINKED_WORKTREE = "linked-worktree"
CHECKOUT_UNTRACKED = "no-git"
CHECKOUT_MISSING = "missing"


# --------------------------------------------------------------------------
# Evidence and disposition
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class PointerEvidence:
    """Everything the classifier is allowed to reason from.

    Every field is either a fact read from disk/Git or ``None`` meaning "could
    not be proven here". The classifier never reaches outside this record, so
    the same inputs always produce the same disposition.
    """

    project: str
    pointer_path: str = ""
    checkout_kind: str = CHECKOUT_CANONICAL
    pointer_present: bool = True
    parse_error: str = ""
    active_task: str | None = None
    route: str | None = None
    task_file: str | None = None
    task_file_present: bool | None = None
    task_steps: tuple[dict, ...] | None = None
    declared_branch: str | None = None
    checkout_branch: str | None = None
    declared_branch_merged: bool | None = None
    pointer_changed_at: dt.datetime | None = None
    pointer_change_source: str = ""
    task_file_changed_at: dt.datetime | None = None
    task_file_change_source: str = ""
    repo_changed_at: dt.datetime | None = None


@dataclass
class PointerDisposition:
    project: str
    pointer_path: str
    state: str
    severity: str
    provable: bool
    recommended_action: str
    active_task: str | None = None
    drift_days: float | None = None
    evidence: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "project": self.project,
            "pointer_path": self.pointer_path,
            "state": self.state,
            "severity": self.severity,
            "provable": self.provable,
            "active_task": self.active_task,
            "drift_days": self.drift_days,
            "recommended_action": self.recommended_action,
            "evidence": list(self.evidence),
        }


def _ownership_note(evidence: PointerEvidence) -> str | None:
    """Ownership is reported, never a failure: lanes legitimately move."""

    declared = evidence.declared_branch
    current = evidence.checkout_branch
    if not declared or not current:
        return None
    if declared == current:
        return f"ownership: canonical checkout is on the declared branch {declared}"
    return (
        f"ownership: pointer declares branch {declared} but the canonical "
        f"checkout is on {current}; the task may be owned by another lane"
    )


def _unfinished_step_names(evidence: PointerEvidence) -> tuple[str, ...]:
    if not evidence.task_steps:
        return ()
    return tuple(
        str(step.get("name", "?"))
        for step in evidence.task_steps
        if str(step.get("status", "")) not in TERMINAL_STEP_STATUSES
    )


def _merge_note(evidence: PointerEvidence) -> str | None:
    """Branch-merge state is reported, never a failure on its own.

    The rule "declared branch merged means the pointer is stale" was dropped
    because it fails honest work in two provable ways:

    1. Merging is normal *mid*-task. `push`, `deploy`, and `smoke` are
       post-merge steps in several routes, so the rule fired hardest during
       the window where a task is most active (fixture TF-014).
    2. A trunk branch is always an ancestor of itself, so any pointer
       declaring `main` tested as "merged" the moment it was written and
       could never stop failing (fixture TF-015).

    Nothing is lost by reporting it: a pointer whose work really did ship is
    already caught by `stale_completed` when every step is terminal, and an
    abandoned merged branch is caught by drift (fixture TF-017).
    """

    if evidence.declared_branch_merged is not True or not evidence.declared_branch:
        return None
    line = (
        f"merge: declared branch {evidence.declared_branch} is already merged "
        f"into the base branch"
    )
    if _unfinished_step_names(evidence):
        line += (
            "; reported only, because post-merge steps are normal and a trunk "
            "branch is always its own ancestor"
        )
    return line


def _last_claim_activity(evidence: PointerEvidence) -> tuple[dt.datetime | None, str]:
    """When the claim last moved, from whichever claim artifact moved last.

    `active.json` names the task; the task file carries the steps. A task that
    runs for months updates the second and not the first, so measuring drift
    from the pointer alone would fail every long-running lane. Taking the more
    recent of the two removes that false positive without weakening anything:
    an abandoned claim moves neither file.
    """

    candidates = [
        (evidence.pointer_changed_at, f"pointer, {evidence.pointer_change_source or 'unknown source'}"),
        (evidence.task_file_changed_at, f"task file, {evidence.task_file_change_source or 'unknown source'}"),
    ]
    known = [(when, source) for when, source in candidates if when is not None]
    if not known:
        return None, ""
    return max(known, key=lambda item: item[0])


def _drift_days(evidence: PointerEvidence) -> float | None:
    changed_at, _ = _last_claim_activity(evidence)
    if changed_at is None or evidence.repo_changed_at is None:
        return None
    delta = evidence.repo_changed_at - changed_at
    return round(delta.total_seconds() / 86400.0, 2)


def classify(
    evidence: PointerEvidence, *, max_drift_days: int = DEFAULT_MAX_DRIFT_DAYS
) -> PointerDisposition:
    """Map one pointer's evidence to exactly one disposition."""

    lines: list[str] = []

    def build(state, severity, action, *, provable=True, drift=None) -> PointerDisposition:
        for note in (_ownership_note(evidence), _merge_note(evidence)):
            if note:
                lines.append(note)
        return PointerDisposition(
            project=evidence.project,
            pointer_path=evidence.pointer_path,
            state=state,
            severity=severity,
            provable=provable,
            recommended_action=action,
            active_task=evidence.active_task,
            drift_days=drift,
            evidence=lines,
        )

    if evidence.checkout_kind == CHECKOUT_MISSING:
        lines.append("no checkout for this project in the current workspace root")
        return build(
            STATE_NO_CHECKOUT,
            SEVERITY_INFO,
            "Nothing to check here. Run this against the canonical workspace root.",
        )

    if evidence.checkout_kind == CHECKOUT_LINKED_WORKTREE:
        lines.append(
            "checkout is a linked Git worktree (.git is a file), so it is a "
            "historical lane and never owns canonical task state"
        )
        return build(
            STATE_NON_CANONICAL,
            SEVERITY_INFO,
            "Ignore for freshness. Only the canonical project checkout is authoritative.",
        )

    if not evidence.pointer_present:
        lines.append(f"no {POINTER_RELPATH} in the canonical checkout")
        return build(
            STATE_ABSENT,
            SEVERITY_WARN,
            "Install the Agent OS task-state baseline so the project has an idle pointer.",
        )

    if evidence.parse_error:
        lines.append(f"pointer could not be parsed: {evidence.parse_error}")
        return build(
            STATE_INVALID,
            SEVERITY_FAIL,
            "Repair the pointer by hand. Do not guess a task from a malformed file.",
        )

    if not evidence.active_task:
        lines.append("pointer claims no task (activeTask is empty)")
        lines.append("an idle pointer cannot resume obsolete work, so age is not a defect")
        return build(
            STATE_IDLE,
            SEVERITY_OK,
            "None. The project is intentionally idle.",
        )

    lines.append(f"pointer claims task {evidence.active_task}")

    if evidence.task_file_present is False:
        lines.append(f"named task file {evidence.task_file} does not exist")
        return build(
            STATE_DANGLING,
            SEVERITY_FAIL,
            "Reset the pointer to idle, or restore the task file it names. Do not invent one.",
        )

    if evidence.task_steps is None:
        lines.append("the task file could not be read, so its progress is unknown")
        return build(
            STATE_UNPROVABLE,
            SEVERITY_WARN,
            "Report only. Confirm with the task owner before changing the pointer.",
            provable=False,
        )

    if not evidence.task_steps:
        lines.append("the task file records no steps, so progress cannot be judged")
        return build(
            STATE_UNPROVABLE,
            SEVERITY_WARN,
            "Report only. Confirm with the task owner before changing the pointer.",
            provable=False,
        )

    unfinished = _unfinished_step_names(evidence)

    if not unfinished:
        lines.append(
            f"every one of the {len(evidence.task_steps)} recorded steps is done or skipped"
        )
        return build(
            STATE_STALE_COMPLETED,
            SEVERITY_FAIL,
            "Reset the pointer to idle and archive the finished task file.",
            drift=_drift_days(evidence),
        )

    lines.append(f"next unfinished step is {unfinished[0]}")

    drift = _drift_days(evidence)
    if drift is None:
        lines.append("no claim-change or repository-activity evidence is available")
        return build(
            STATE_UNPROVABLE,
            SEVERITY_WARN,
            "Report only. Freshness cannot be proven without Git history for this checkout.",
            provable=False,
        )

    claim_changed_at, claim_source = _last_claim_activity(evidence)
    lines.append(
        f"claim last changed {claim_changed_at.date()} ({claim_source}); "
        f"repository last moved {evidence.repo_changed_at.date()}; "
        f"drift {drift} day(s)"
    )

    if drift > max_drift_days:
        return build(
            STATE_STALE_DRIFTED,
            SEVERITY_FAIL,
            "Reset the pointer to idle, or update it to the task actually in flight.",
            drift=drift,
        )

    return build(
        STATE_ACTIVE,
        SEVERITY_OK,
        "None. Continue the next unfinished step.",
        drift=drift,
    )


# --------------------------------------------------------------------------
# Evidence collection
# --------------------------------------------------------------------------


def _git(checkout: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ("git", "-C", str(checkout), *args),
        text=True,
        capture_output=True,
        check=False,
        timeout=GIT_TIMEOUT_SECONDS,
    )


def _parse_iso(value: str) -> dt.datetime | None:
    value = value.strip()
    if not value:
        return None
    try:
        parsed = dt.datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def _mtime(path: Path) -> dt.datetime | None:
    try:
        return dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc)
    except OSError:
        return None


def checkout_kind(checkout: Path) -> str:
    """Canonical checkout vs historical linked worktree vs plain directory."""

    if not checkout.is_dir():
        return CHECKOUT_MISSING
    marker = checkout / ".git"
    if marker.is_dir():
        return CHECKOUT_CANONICAL
    if marker.is_file():
        return CHECKOUT_LINKED_WORKTREE
    return CHECKOUT_UNTRACKED


def _path_changed_at(checkout: Path, relpath: str) -> tuple[dt.datetime | None, str]:
    """When one claim artifact last genuinely changed.

    Git history is the primary source. File mtime is used only when the file
    is uncommitted or untracked, because a clone or a branch checkout rewrites
    every mtime to the moment of checkout. Trusting mtime there would make
    every stale pointer in a fresh checkout look brand new, which is the exact
    failure this check exists to catch.
    """

    path = checkout / relpath
    status = _git(checkout, "status", "--porcelain=v1", "--", relpath)
    dirty = status.returncode == 0 and bool(status.stdout.strip())
    untracked = status.returncode == 0 and status.stdout.strip().startswith("??")

    if dirty:
        on_disk = _mtime(path)
        if on_disk:
            source = "untracked working tree" if untracked else "uncommitted working tree"
            return on_disk, source

    result = _git(checkout, "log", "-1", "--format=%cI", "--", relpath)
    if result.returncode == 0:
        committed = _parse_iso(result.stdout)
        if committed:
            return committed, "git"

    on_disk = _mtime(path)
    if on_disk:
        return on_disk, "working tree (no git history)"
    return None, ""


def _repo_changed_at(checkout: Path) -> dt.datetime | None:
    result = _git(checkout, "log", "-1", "--format=%cI", "--all")
    if result.returncode != 0:
        return None
    return _parse_iso(result.stdout)


def _current_branch(checkout: Path) -> str | None:
    result = _git(checkout, "rev-parse", "--abbrev-ref", "HEAD")
    if result.returncode != 0:
        return None
    branch = result.stdout.strip()
    return branch or None


def _branch_merged(checkout: Path, branch: str, base_refs: tuple[str, ...]) -> bool | None:
    if _git(checkout, "rev-parse", "--verify", "--quiet", branch).returncode != 0:
        return None
    for base in base_refs:
        if _git(checkout, "rev-parse", "--verify", "--quiet", base).returncode != 0:
            continue
        result = _git(checkout, "merge-base", "--is-ancestor", branch, base)
        if result.returncode == 0:
            return True
        if result.returncode == 1:
            return False
    return None


def gather_evidence(
    project: str,
    checkout: Path,
    *,
    base_refs: tuple[str, ...] = DEFAULT_BASE_REFS,
) -> PointerEvidence:
    """Read one checkout's pointer and the Git facts around it."""

    kind = checkout_kind(checkout)
    pointer = checkout / POINTER_RELPATH
    if kind == CHECKOUT_MISSING:
        return PointerEvidence(project=project, pointer_path=str(pointer), checkout_kind=kind)
    if kind == CHECKOUT_LINKED_WORKTREE:
        return PointerEvidence(
            project=project,
            pointer_path=str(pointer),
            checkout_kind=kind,
            pointer_present=pointer.is_file(),
        )

    if not pointer.is_file():
        return PointerEvidence(
            project=project,
            pointer_path=str(pointer),
            checkout_kind=kind,
            pointer_present=False,
        )

    try:
        raw = json.loads(pointer.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return PointerEvidence(
            project=project,
            pointer_path=str(pointer),
            checkout_kind=kind,
            parse_error=str(exc),
        )
    if not isinstance(raw, dict):
        return PointerEvidence(
            project=project,
            pointer_path=str(pointer),
            checkout_kind=kind,
            parse_error="pointer is not a JSON object",
        )

    active_task = raw.get("activeTask") or raw.get("id")
    active_task = str(active_task) if active_task else None
    task_file = raw.get("taskFile") or raw.get("file") or None
    route = raw.get("route") or None

    changed_at, change_source = _path_changed_at(checkout, POINTER_RELPATH)
    repo_changed_at = _repo_changed_at(checkout)
    current_branch = _current_branch(checkout)

    if not active_task:
        return PointerEvidence(
            project=project,
            pointer_path=str(pointer),
            checkout_kind=kind,
            route=route,
            checkout_branch=current_branch,
            pointer_changed_at=changed_at,
            pointer_change_source=change_source,
            repo_changed_at=repo_changed_at,
        )

    candidate = (checkout / task_file) if task_file else (pointer.parent / f"{active_task}.json")
    task_file_present = candidate.is_file()
    task_changed_at: dt.datetime | None = None
    task_change_source = ""
    task_steps: tuple[dict, ...] | None = None
    declared_branch: str | None = None
    if task_file_present:
        try:
            task_relpath = candidate.relative_to(checkout).as_posix()
        except ValueError:
            task_relpath = ""
        if task_relpath:
            task_changed_at, task_change_source = _path_changed_at(checkout, task_relpath)
        try:
            task = json.loads(candidate.read_text())
        except (OSError, json.JSONDecodeError):
            task = None
        if isinstance(task, dict):
            raw_steps = task.get("steps")
            if isinstance(raw_steps, list):
                task_steps = tuple(step for step in raw_steps if isinstance(step, dict))
            branch = task.get("branch")
            declared_branch = str(branch) if branch else None

    merged = (
        _branch_merged(checkout, declared_branch, base_refs) if declared_branch else None
    )

    return PointerEvidence(
        project=project,
        pointer_path=str(pointer),
        checkout_kind=kind,
        route=route,
        active_task=active_task,
        task_file=str(task_file) if task_file else str(candidate.name),
        task_file_present=task_file_present,
        task_steps=task_steps,
        declared_branch=declared_branch,
        checkout_branch=current_branch,
        declared_branch_merged=merged,
        pointer_changed_at=changed_at,
        pointer_change_source=change_source,
        task_file_changed_at=task_changed_at,
        task_file_change_source=task_change_source,
        repo_changed_at=repo_changed_at,
    )


def inspect_pointer(
    root: Path,
    project: str,
    *,
    checkout: Path | None = None,
    base_refs: tuple[str, ...] = DEFAULT_BASE_REFS,
    max_drift_days: int = DEFAULT_MAX_DRIFT_DAYS,
) -> PointerDisposition:
    """Gather evidence for one checkout and classify it."""

    target = checkout if checkout is not None else root / project
    evidence = gather_evidence(project, target, base_refs=base_refs)
    return classify(evidence, max_drift_days=max_drift_days)


def collect_workspace(
    root: Path,
    *,
    projects: tuple[str, ...] = PROJECTS,
    base_refs: tuple[str, ...] = DEFAULT_BASE_REFS,
    max_drift_days: int = DEFAULT_MAX_DRIFT_DAYS,
) -> list[PointerDisposition]:
    """Judge only the canonical pointer of each registered project.

    Historical worktrees under `.worktrees/` or `Sifututor-worktrees/` are not
    reachable from here by construction: the scan walks the registry, not the
    filesystem, so an old lane can never become a current failure.
    """

    root = Path(root).resolve()
    return [
        inspect_pointer(
            root, project, base_refs=base_refs, max_drift_days=max_drift_days
        )
        for project in projects
    ]


def summarize(dispositions: list[PointerDisposition]) -> dict:
    counts = {SEVERITY_OK: 0, SEVERITY_INFO: 0, SEVERITY_WARN: 0, SEVERITY_FAIL: 0}
    for item in dispositions:
        counts[item.severity] = counts.get(item.severity, 0) + 1
    judged = [d for d in dispositions if d.state not in (STATE_NO_CHECKOUT, STATE_NON_CANONICAL)]
    return {
        "checked": len(judged),
        "reported": len(dispositions),
        "ok": counts[SEVERITY_OK],
        "info": counts[SEVERITY_INFO],
        "warn": counts[SEVERITY_WARN],
        "fail": counts[SEVERITY_FAIL],
    }


# --------------------------------------------------------------------------
# Deterministic fixtures (no clock, no filesystem, no Git)
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class FixtureCase:
    case_id: str
    name: str
    evidence: PointerEvidence
    expected_state: str
    expected_severity: str
    why: str


def _at(day: str) -> dt.datetime:
    return dt.datetime.fromisoformat(day).replace(tzinfo=dt.timezone.utc)


FIXTURES = (
    FixtureCase(
        "TF-001",
        "completed task still claimed",
        PointerEvidence(
            project="ripple-suite",
            pointer_path="ripple-suite/.claude/tasks/active.json",
            active_task="crm-v3-worklist",
            task_file=".claude/tasks/crm-v3-worklist.json",
            task_file_present=True,
            task_steps=({"name": "build", "status": "done"}, {"name": "push", "status": "done"}),
            declared_branch="feature/181-crm-v3-worklist",
            checkout_branch="feature/181-crm-v3-worklist",
            declared_branch_merged=True,
            pointer_changed_at=_at("2026-07-11"),
            pointer_change_source="git",
            repo_changed_at=_at("2026-09-20"),
        ),
        STATE_STALE_COMPLETED,
        SEVERITY_FAIL,
        "Every step finished and the branch merged, so the pointer describes shipped work.",
    ),
    FixtureCase(
        "TF-002",
        "intentionally idle pointer that is months old",
        PointerEvidence(
            project="lls",
            pointer_path="lls/.claude/tasks/active.json",
            active_task=None,
            pointer_changed_at=_at("2026-05-26"),
            pointer_change_source="git",
            repo_changed_at=_at("2026-09-20"),
        ),
        STATE_IDLE,
        SEVERITY_OK,
        "An idle pointer claims nothing, so no agent can resume obsolete work from it.",
    ),
    FixtureCase(
        "TF-003",
        "genuinely active task",
        PointerEvidence(
            project="kelas",
            pointer_path="kelas/.claude/tasks/active.json",
            active_task="h11-auto-billing",
            task_file=".claude/tasks/h11-auto-billing.json",
            task_file_present=True,
            task_steps=({"name": "build", "status": "done"}, {"name": "qa", "status": "in_progress"}),
            declared_branch="feat/h11-auto-billing",
            checkout_branch="feat/h11-auto-billing",
            declared_branch_merged=False,
            pointer_changed_at=_at("2026-09-18"),
            pointer_change_source="git",
            repo_changed_at=_at("2026-09-20"),
        ),
        STATE_ACTIVE,
        SEVERITY_OK,
        "Unfinished steps plus recent pointer activity is exactly what an active lane looks like.",
    ),
    FixtureCase(
        "TF-004",
        "old pointer inside an unrelated historical worktree",
        PointerEvidence(
            project="ripple-885-watcher-owner-retry",
            pointer_path=".worktrees/ripple-885-watcher-owner-retry/.claude/tasks/active.json",
            checkout_kind=CHECKOUT_LINKED_WORKTREE,
            active_task="885-watcher-owner-retry",
        ),
        STATE_NON_CANONICAL,
        SEVERITY_INFO,
        "Historical lanes keep their own pointers; treating them as current would fail the workspace dozens of times.",
    ),
    FixtureCase(
        "TF-005",
        "unfinished task the project moved past months ago",
        PointerEvidence(
            project="sifututor_tutor",
            pointer_path="sifututor_tutor/.claude/tasks/active.json",
            active_task="tut-auth-firstrun-rebuild",
            task_file=".claude/tasks/tut-auth-firstrun-rebuild.json",
            task_file_present=True,
            task_steps=({"name": "build", "status": "done"}, {"name": "generate_tests", "status": "pending"}),
            pointer_changed_at=_at("2026-05-26"),
            pointer_change_source="git",
            repo_changed_at=_at("2026-09-20"),
        ),
        STATE_STALE_DRIFTED,
        SEVERITY_FAIL,
        "The pointer stood still for months while its own repository kept moving.",
    ),
    FixtureCase(
        "TF-006",
        "unfinished task in a quiet project",
        PointerEvidence(
            project="creative-hub",
            pointer_path="creative-hub/.claude/tasks/active.json",
            active_task="dns-cutover",
            task_file=".claude/tasks/dns-cutover.json",
            task_file_present=True,
            task_steps=({"name": "verify", "status": "pending"},),
            pointer_changed_at=_at("2026-08-02"),
            pointer_change_source="working tree",
            repo_changed_at=_at("2026-08-03"),
        ),
        STATE_ACTIVE,
        SEVERITY_OK,
        "Freshness is measured against repository activity, so a paused project cannot drift.",
    ),
    FixtureCase(
        "TF-007",
        "pointer naming a task file that does not exist",
        PointerEvidence(
            project="sifu-tutor",
            pointer_path="sifu-tutor/.claude/tasks/active.json",
            active_task="bugfix-20260524-4023",
            task_file=".claude/tasks/bugfix-20260524-4023.json",
            task_file_present=False,
            pointer_changed_at=_at("2026-05-29"),
            pointer_change_source="git",
            repo_changed_at=_at("2026-09-19"),
        ),
        STATE_DANGLING,
        SEVERITY_FAIL,
        "A pointer to a missing task file is broken state, not a task to resume.",
    ),
    FixtureCase(
        "TF-008",
        "malformed pointer",
        PointerEvidence(
            project="lls-mobile",
            pointer_path="lls-mobile/.claude/tasks/active.json",
            parse_error="Expecting value: line 1 column 3 (char 2)",
        ),
        STATE_INVALID,
        SEVERITY_FAIL,
        "Unparseable state must be repaired by a human, never inferred.",
    ),
    FixtureCase(
        "TF-009",
        "claimed task with no change evidence at all",
        PointerEvidence(
            project="finch-inbox",
            pointer_path="finch-inbox/.claude/tasks/active.json",
            active_task="inbox-threading",
            task_file=".claude/tasks/inbox-threading.json",
            task_file_present=True,
            task_steps=({"name": "qa", "status": "pending"},),
            pointer_changed_at=None,
            repo_changed_at=None,
        ),
        STATE_UNPROVABLE,
        SEVERITY_WARN,
        "Without Git or mtime evidence the honest answer is unprovable, not stale.",
    ),
    FixtureCase(
        "TF-010",
        "claimed task whose task file could not be read",
        PointerEvidence(
            project="lls-frontend",
            pointer_path="lls-frontend/.claude/tasks/active.json",
            active_task="spa-auth",
            task_file=".claude/tasks/spa-auth.json",
            task_file_present=True,
            task_steps=None,
            pointer_changed_at=_at("2026-05-26"),
            repo_changed_at=_at("2026-09-20"),
        ),
        STATE_UNPROVABLE,
        SEVERITY_WARN,
        "A present but unreadable task file proves nothing about progress.",
    ),
    FixtureCase(
        "TF-011",
        "canonical project with no pointer installed",
        PointerEvidence(
            project="finch-inbox",
            pointer_path="finch-inbox/.claude/tasks/active.json",
            pointer_present=False,
        ),
        STATE_ABSENT,
        SEVERITY_WARN,
        "A missing pointer is an adoption gap to report, not a silent pass.",
    ),
    FixtureCase(
        "TF-012",
        "registered project absent from this checkout",
        PointerEvidence(
            project="kelas",
            pointer_path="kelas/.claude/tasks/active.json",
            checkout_kind=CHECKOUT_MISSING,
        ),
        STATE_NO_CHECKOUT,
        SEVERITY_INFO,
        "A standalone Agent OS worktree holds no product checkouts and must not fail for it.",
    ),
    FixtureCase(
        "TF-013",
        "active task whose lane moved to another branch",
        PointerEvidence(
            project="ripple-suite",
            pointer_path="ripple-suite/.claude/tasks/active.json",
            active_task="scanner-import",
            task_file=".claude/tasks/scanner-import.json",
            task_file_present=True,
            task_steps=({"name": "qa", "status": "pending"},),
            declared_branch="fix/1091-scanner-import-bypasses",
            checkout_branch="main",
            declared_branch_merged=False,
            pointer_changed_at=_at("2026-09-19"),
            pointer_change_source="git",
            repo_changed_at=_at("2026-09-20"),
        ),
        STATE_ACTIVE,
        SEVERITY_OK,
        "Ownership drift is reported in the evidence lines but never fails a current task.",
    ),
    FixtureCase(
        "TF-014",
        "merged branch whose only unfinished step is a post-merge step",
        PointerEvidence(
            project="sifututor_parent",
            pointer_path="sifututor_parent/.claude/tasks/active.json",
            active_task="76-legacy-payment-recovery",
            task_file=".claude/tasks/76-legacy-payment-recovery.json",
            task_file_present=True,
            task_steps=(
                {"name": "commit", "status": "done"},
                {"name": "deploy", "status": "pending"},
            ),
            declared_branch="fix/76-legacy-payment-recovery",
            checkout_branch="main",
            declared_branch_merged=True,
            pointer_changed_at=_at("2026-09-10"),
            pointer_change_source="git",
            repo_changed_at=_at("2026-09-20"),
        ),
        STATE_ACTIVE,
        SEVERITY_OK,
        "Deploy and smoke run after the merge, so failing on merge alone would flag a task at its most active. The merge is reported as evidence instead.",
    ),
    FixtureCase(
        "TF-015",
        "unfinished task that declares the trunk branch",
        PointerEvidence(
            project="sifu-tutor",
            pointer_path="sifu-tutor/.claude/tasks/active.json",
            active_task="invoice-enum-guard",
            task_file=".claude/tasks/invoice-enum-guard.json",
            task_file_present=True,
            task_steps=({"name": "qa", "status": "pending"},),
            declared_branch="main",
            checkout_branch="main",
            declared_branch_merged=True,
            pointer_changed_at=_at("2026-09-18"),
            pointer_change_source="git",
            repo_changed_at=_at("2026-09-20"),
        ),
        STATE_ACTIVE,
        SEVERITY_OK,
        "A trunk branch is always an ancestor of itself, so merge-ancestry alone would fail such a pointer on the day it was written and every day after.",
    ),
    FixtureCase(
        "TF-016",
        "long task whose pointer is old but whose steps keep moving",
        PointerEvidence(
            project="kelas",
            pointer_path="kelas/.claude/tasks/active.json",
            active_task="billing-rewrite",
            task_file=".claude/tasks/billing-rewrite.json",
            task_file_present=True,
            task_steps=(
                {"name": "build", "status": "done"},
                {"name": "qa", "status": "in_progress"},
            ),
            pointer_changed_at=_at("2026-07-01"),
            pointer_change_source="git",
            task_file_changed_at=_at("2026-09-19"),
            task_file_change_source="git",
            repo_changed_at=_at("2026-09-20"),
        ),
        STATE_ACTIVE,
        SEVERITY_OK,
        "active.json records only which task is claimed; an 80-day task ticks its steps off in the task file, so drift must be measured from whichever claim artifact moved last.",
    ),
    FixtureCase(
        "TF-017",
        "merged branch abandoned long ago",
        PointerEvidence(
            project="lls",
            pointer_path="lls/.claude/tasks/active.json",
            active_task="attendance-import",
            task_file=".claude/tasks/attendance-import.json",
            task_file_present=True,
            task_steps=({"name": "review", "status": "pending"},),
            declared_branch="feat/attendance-import",
            checkout_branch="main",
            declared_branch_merged=True,
            pointer_changed_at=_at("2026-05-02"),
            pointer_change_source="git",
            task_file_changed_at=_at("2026-05-02"),
            task_file_change_source="git",
            repo_changed_at=_at("2026-09-20"),
        ),
        STATE_STALE_DRIFTED,
        SEVERITY_FAIL,
        "Demoting the merge rule loses no real finding: an abandoned claim moves neither claim artifact, so drift still fails it.",
    ),
)


def run_fixtures(max_drift_days: int = DEFAULT_MAX_DRIFT_DAYS) -> list[dict]:
    results = []
    for case in FIXTURES:
        got = classify(case.evidence, max_drift_days=max_drift_days)
        ok = got.state == case.expected_state and got.severity == case.expected_severity
        results.append(
            {
                "id": case.case_id,
                "name": case.name,
                "ok": ok,
                "expected_state": case.expected_state,
                "actual_state": got.state,
                "expected_severity": case.expected_severity,
                "actual_severity": got.severity,
                "why": case.why,
            }
        )
    return results


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


STATE_LABELS = {
    STATE_ACTIVE: "PASS",
    STATE_IDLE: "PASS",
    STATE_STALE_COMPLETED: "FAIL",
    STATE_STALE_DRIFTED: "FAIL",
    STATE_DANGLING: "FAIL",
    STATE_INVALID: "FAIL",
    STATE_UNPROVABLE: "WARN",
    STATE_ABSENT: "WARN",
    STATE_NO_CHECKOUT: "INFO",
    STATE_NON_CANONICAL: "INFO",
}


def _print_text(dispositions: list[PointerDisposition], summary: dict, root: Path) -> None:
    """One block per judged pointer.

    Projects with no checkout here are collapsed into a single line. A
    standalone Agent OS worktree has eleven of them, and repeating the same
    "no checkout" sentence would bury the one finding that matters.
    """

    print("Canonical active-task freshness")
    print(f"Root: {root}")
    print()
    absent_checkouts = []
    for item in dispositions:
        if item.state == STATE_NO_CHECKOUT:
            absent_checkouts.append(item.project)
            continue
        label = STATE_LABELS.get(item.state, "INFO")
        print(f"{label:4} {item.project:26} {item.state}")
        for line in item.evidence:
            print(f"       - {line}")
        if item.severity in (SEVERITY_FAIL, SEVERITY_WARN):
            print(f"       -> {item.recommended_action}")
    if absent_checkouts:
        print(f"INFO {'(no checkout here)':26} {', '.join(absent_checkouts)}")
    print()


def _self_test() -> int:
    results = run_fixtures()
    for row in results:
        status = "PASS" if row["ok"] else "FAIL"
        detail = "" if row["ok"] else f" (got {row['actual_state']}/{row['actual_severity']})"
        print(f"{status} {row['id']} {row['name']}{detail}")
    passed = sum(1 for row in results if row["ok"])
    print()
    print(f"Active task freshness fixtures: {passed}/{len(results)}")
    return 0 if passed == len(results) else 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(ROOT), help="Workspace root to scan.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument(
        "--max-drift-days",
        type=int,
        default=DEFAULT_MAX_DRIFT_DAYS,
        help=f"Repository activity gap that makes a claim stale. Default: {DEFAULT_MAX_DRIFT_DAYS}",
    )
    parser.add_argument(
        "--base-ref",
        action="append",
        default=None,
        help="Base ref used to test whether a declared branch already merged.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run packaged fixtures only.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.self_test:
        return _self_test()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ACTIVE TASK FRESHNESS: ERROR ({root} is not a directory)")
        return 2

    base_refs = tuple(args.base_ref) if args.base_ref else DEFAULT_BASE_REFS
    dispositions = collect_workspace(
        root, base_refs=base_refs, max_drift_days=args.max_drift_days
    )
    summary = summarize(dispositions)

    if args.json:
        print(
            json.dumps(
                {
                    "root": str(root),
                    "max_drift_days": args.max_drift_days,
                    "summary": summary,
                    "pointers": [item.as_dict() for item in dispositions],
                },
                indent=2,
            )
        )
    else:
        _print_text(dispositions, summary, root)

    counts = (
        f"{summary['checked']} canonical pointer(s) checked, "
        f"{summary['fail']} drift, {summary['warn']} warning(s), {summary['info']} skipped"
    )
    if summary["checked"] == 0:
        if not args.json:
            print(f"ACTIVE TASK FRESHNESS: SKIP (no canonical project checkouts here; {counts})")
        return 0
    if summary["fail"]:
        if not args.json:
            print(f"ACTIVE TASK FRESHNESS: FAIL ({counts})")
        return 1
    if not args.json:
        print(f"ACTIVE TASK FRESHNESS: PASS ({counts})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
