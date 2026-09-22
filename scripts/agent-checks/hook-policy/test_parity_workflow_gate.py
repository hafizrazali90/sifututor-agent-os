#!/usr/bin/env python3
"""Parity fixture: WorkflowGateCheck (ripple-suite config) vs the frozen
fixtures/originals/ripple_workflow_gate_snapshot.py, exercised against a
real temp project layout (.claude/tasks/active.json + task file) so both
sides read the same actual files.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from check_workflow_gate import RIPPLE_SUITE_WORKFLOW_CONFIG, WorkflowGateCheck, load_task_state  # noqa: E402
from models import HookRequest, Outcome  # noqa: E402

SNAPSHOT = HERE / "fixtures" / "originals" / "ripple_workflow_gate_snapshot.py"


class _TempProject:
    def __init__(self, task: dict | None):
        self._task = task
        self._tmp: tempfile.TemporaryDirectory | None = None
        self.root: Path | None = None

    def __enter__(self) -> Path:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        hooks_dir = self.root / ".claude" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(SNAPSHOT, hooks_dir / "workflow-gate.py")

        tasks_dir = self.root / ".claude" / "tasks"
        tasks_dir.mkdir(parents=True, exist_ok=True)
        if self._task is not None:
            task_file_rel = ".claude/tasks/current.json"
            (self.root / task_file_rel).write_text(json.dumps(self._task))
            (tasks_dir / "active.json").write_text(
                json.dumps({"activeTask": "t1", "taskFile": task_file_rel})
            )
        return self.root

    def __exit__(self, *exc):
        if self._tmp is not None:
            self._tmp.cleanup()


def run_original(repo_root: Path, command: str) -> str:
    payload = {"tool_name": "Bash", "tool_input": {"command": command}}
    result = subprocess.run(
        [sys.executable, str(repo_root / ".claude" / "hooks" / "workflow-gate.py")],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        cwd=repo_root,
        timeout=10,
        check=False,
    )
    if not result.stdout.strip():
        return "allow"
    data = json.loads(result.stdout)
    return data.get("hookSpecificOutput", {}).get("permissionDecision", "allow")


FIXTURE_CASES = [
    ("no active task", None, "allow"),
    (
        "verify pending",
        {"route": "feature", "steps": [{"name": "verify", "status": "pending"}]},
        "deny",
    ),
    (
        "everything done",
        {
            "route": "feature",
            "steps": [
                {"name": "verify", "status": "done"},
                {"name": "qa", "status": "done"},
                {"name": "release_notes", "status": "done"},
            ],
        },
        "allow",
    ),
    (
        "bugfix regression_test pending",
        {"route": "bugfix", "steps": [{"name": "regression_test", "status": "pending"}]},
        "deny",
    ),
    (
        "feature regression_test pending is not checked",
        {"route": "feature", "steps": [{"name": "regression_test", "status": "pending"}]},
        "allow",
    ),
    (
        "hotfix regression_test done but evidence incomplete",
        {
            "route": "hotfix",
            "steps": [
                {
                    "name": "regression_test",
                    "status": "done",
                    "evidence": {"red_output": "", "green_output": "pass"},
                }
            ],
        },
        "deny",
    ),
    (
        "small-change release_notes pending",
        {"route": "small-change", "steps": [{"name": "release_notes", "status": "pending"}]},
        "deny",
    ),
]


@unittest.skipUnless(SNAPSHOT.is_file(), "frozen workflow-gate snapshot missing")
class WorkflowGateParityTests(unittest.TestCase):
    def test_matches_frozen_original_for_every_fixture(self):
        mismatches = []
        for label, task, expected in FIXTURE_CASES:
            with _TempProject(task) as repo_root:
                command = 'git commit -m "feat: x"'
                original_decision = run_original(repo_root, command)
                self.assertEqual(
                    original_decision, expected,
                    f"fixture setup assumption wrong for {label!r}: "
                    f"original said {original_decision!r}, expected {expected!r}",
                )

                check = WorkflowGateCheck(
                    RIPPLE_SUITE_WORKFLOW_CONFIG,
                    task_state_provider=lambda cwd, r=repo_root: load_task_state(str(r)),
                )
                ours = check.run(HookRequest(tool_name="Bash", command=command, cwd=str(repo_root)))
                ours_decision = "deny" if ours.outcome == Outcome.DENY else "allow"

                if original_decision != ours_decision:
                    mismatches.append((label, original_decision, ours_decision))
        self.assertEqual(mismatches, [], f"parity mismatches: {mismatches}")


if __name__ == "__main__":
    unittest.main()
