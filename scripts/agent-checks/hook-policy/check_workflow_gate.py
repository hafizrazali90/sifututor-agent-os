#!/usr/bin/env python3
"""Shared workflow-gate policy: REQUIRED, config-driven.

Mirrors ripple-suite's workflow-gate.py (SURVEY.md section 4): reads
.claude/tasks/active.json -> the task file it points at -> which mandatory
steps (verify, qa, regression_test, defect_analysis, release_notes) are
done/skipped for the task's route, and blocks commit with one aggregated
reason listing everything still missing. sifu-tutor/sifututor_tutor share
one body and lls has its own -- three real bodies for "the same idea,
parameterized by route names" (SURVEY.md section 4). This module takes
those route sets as a `WorkflowGateConfig` instead.

REQUIRED severity means: if the task-state *file itself* cannot be read
because of an unexpected I/O error (not "file legitimately doesn't exist",
which is a real, allowed "no active task" case exactly like the original
scripts), the dispatcher's fail-safe rule applies -- see
check_expensive_examples.py and dispatcher.py for what "the check could not
run" means for a REQUIRED check versus an ADVISORY one. This check itself
mirrors the originals' own semantics: missing/malformed active.json or task
file is treated as "no active task", which allows, exactly like today.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import os

from models import Decision, HookRequest, Severity


@dataclass(frozen=True)
class WorkflowGateConfig:
    regression_test_routes: frozenset[str]
    defect_analysis_routes: frozenset[str]
    release_notes_routes: frozenset[str]
    label: str = "workflow_gate"


RIPPLE_SUITE_WORKFLOW_CONFIG = WorkflowGateConfig(
    regression_test_routes=frozenset({"hotfix", "bugfix"}),
    defect_analysis_routes=frozenset({"hotfix", "bugfix"}),
    release_notes_routes=frozenset({"hotfix", "bugfix", "feature", "small-change"}),
    label="ripple-suite",
)


def load_task_state(project_root: str) -> dict | None:
    """Real task-state loader -- mirrors the original script exactly.

    Returns None whenever the original script would `sys.exit(0)` (allow):
    no active.json, no taskFile field, missing task file, or unparseable
    JSON at either level.
    """
    if not project_root:
        return None
    active_path = os.path.join(project_root, ".claude", "tasks", "active.json")
    if not os.path.exists(active_path):
        return None
    try:
        with open(active_path) as f:
            active = json.load(f)
    except Exception:
        return None

    task_file = active.get("taskFile")
    if not task_file:
        return None

    task_path = os.path.join(project_root, task_file)
    if not os.path.exists(task_path):
        return None

    try:
        with open(task_path) as f:
            task = json.load(f)
    except Exception:
        return None

    return {
        "route": task.get("route", ""),
        "steps": task.get("steps", []),
        "description": task.get("description", active.get("activeTask", "unknown")),
        "task_file": task_file,
    }


def _get_step(steps: list[dict], name: str) -> dict | None:
    for s in steps:
        if s.get("name") == name:
            return s
    return None


def _step_done(steps: list[dict], name: str) -> bool:
    s = _get_step(steps, name)
    return s is not None and s.get("status") == "done"


def _step_skipped(steps: list[dict], name: str) -> bool:
    s = _get_step(steps, name)
    return s is not None and s.get("status") == "skipped"


def _step_exists(steps: list[dict], name: str) -> bool:
    return _get_step(steps, name) is not None


class WorkflowGateCheck:
    severity = Severity.REQUIRED
    expensive = False

    def __init__(self, config: WorkflowGateConfig, task_state_provider=None):
        self.config = config
        self.name = f"workflow_gate:{config.label}"
        self._task_state_provider = task_state_provider or load_task_state

    def applies(self, request: HookRequest) -> bool:
        return request.tool_name == "Bash" and "git commit" in request.command

    def run(self, request: HookRequest) -> Decision:
        if "--no-verify" in request.command:
            return Decision.allow(self.name)

        task = self._task_state_provider(request.cwd)
        if task is None:
            return Decision.allow(self.name)

        route = task.get("route", "")
        steps = task.get("steps", [])
        blocked_reasons: list[str] = []

        if _step_exists(steps, "verify") and not _step_done(steps, "verify") and not _step_skipped(steps, "verify"):
            blocked_reasons.append("verify not done")
        if _step_exists(steps, "qa") and not _step_done(steps, "qa") and not _step_skipped(steps, "qa"):
            blocked_reasons.append("qa not done")

        if route in self.config.regression_test_routes:
            rt = _get_step(steps, "regression_test")
            if rt is not None:
                status = rt.get("status", "blocked")
                if status not in ("done", "skipped"):
                    blocked_reasons.append("regression_test not done")
                elif status == "done":
                    evidence = rt.get("evidence", {})
                    red = str(evidence.get("red_output", "")).strip()
                    green = str(evidence.get("green_output", "")).strip()
                    if not red or not green:
                        blocked_reasons.append("regression_test evidence incomplete")

        if route in self.config.defect_analysis_routes:
            da = _get_step(steps, "defect_analysis")
            if da is not None:
                status = da.get("status", "blocked")
                if status not in ("done", "skipped"):
                    blocked_reasons.append("defect_analysis not done")

        if route in self.config.release_notes_routes:
            rn = _get_step(steps, "release_notes")
            if rn is not None:
                status = rn.get("status", "blocked")
                if status not in ("done", "skipped"):
                    blocked_reasons.append("release_notes not done")

        if not blocked_reasons:
            return Decision.allow(self.name)

        task_desc = task.get("description", "unknown")
        task_file = task.get("task_file", ".claude/tasks/active.json")
        reasons_text = "\n".join(f"  - {r}" for r in blocked_reasons)
        return Decision.deny(
            self.name,
            reason=f"Workflow gate failed for task: {task_desc}",
            guidance=f"{reasons_text}\n\nComplete the missing steps first, or mark "
            f"them in the task state file at: {task_file}",
        )
