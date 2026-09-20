#!/usr/bin/env python3
"""Regression tests for canonical active-task pointer freshness (issue 113).

Valid JSON never proved that `.claude/tasks/active.json` still describes the
current task. These tests pin the four dispositions the issue names (stale,
intentionally idle, genuinely active, and an unrelated historical worktree)
plus the unprovable and malformed cases where the checker must report instead
of inventing a task.

Everything here is deterministic: temporary Git repositories with pinned
commit dates, and pure classifier fixtures that never read the wall clock.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "agent_os_active_task_freshness.py"
SPEC = importlib.util.spec_from_file_location("agent_os_active_task_freshness", MODULE_PATH)
freshness = importlib.util.module_from_spec(SPEC)
# Registered before exec so dataclasses can resolve the module's own annotations.
sys.modules[SPEC.name] = freshness
SPEC.loader.exec_module(freshness)


def git(*args: str, cwd: Path, when: str | None = None) -> str:
    env = None
    if when is not None:
        import os

        env = dict(os.environ, GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
    result = subprocess.run(
        ("git", *args), cwd=cwd, text=True, capture_output=True, check=True, env=env
    )
    return result.stdout.strip()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def steps(*pairs: tuple[str, str]) -> list[dict]:
    return [{"name": name, "status": status} for name, status in pairs]


def init_project(root: Path, name: str) -> Path:
    project = root / name
    (project / ".claude" / "tasks").mkdir(parents=True)
    git("init", "-b", "main", cwd=project)
    git("config", "user.name", "Fixture", cwd=project)
    git("config", "user.email", "fixture@example.invalid", cwd=project)
    return project


def commit_all(project: Path, message: str, when: str) -> None:
    git("add", "-A", cwd=project)
    git("commit", "-m", message, cwd=project, when=when)


class ClassifierFixtureTests(unittest.TestCase):
    """The packaged deterministic fixtures are the negative controls."""

    def test_every_packaged_fixture_classifies_as_expected(self):
        results = freshness.run_fixtures()
        failed = [row for row in results if not row["ok"]]
        self.assertEqual(failed, [], f"fixture drift: {failed}")

    def test_fixtures_cover_the_four_required_dispositions(self):
        states = {case.expected_state for case in freshness.FIXTURES}
        for required in (
            freshness.STATE_STALE_COMPLETED,
            freshness.STATE_IDLE,
            freshness.STATE_ACTIVE,
            freshness.STATE_NON_CANONICAL,
        ):
            self.assertIn(required, states)

    def test_fixtures_pin_the_reassessed_false_positive_controls(self):
        """TF-014 through TF-017 are why the merge and drift rules changed."""

        by_id = {case.case_id: case for case in freshness.FIXTURES}
        for case_id in ("TF-014", "TF-015", "TF-016"):
            self.assertEqual(by_id[case_id].expected_state, freshness.STATE_ACTIVE)
            self.assertEqual(by_id[case_id].expected_severity, freshness.SEVERITY_OK)
        self.assertEqual(by_id["TF-017"].expected_state, freshness.STATE_STALE_DRIFTED)

    def test_fixture_ids_are_unique(self):
        ids = [case.case_id for case in freshness.FIXTURES]
        self.assertEqual(len(ids), len(set(ids)))


class WorkspaceScanTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def scan(self, **kwargs):
        return freshness.collect_workspace(self.root, projects=self.projects, **kwargs)

    def by_project(self, reports):
        return {report.project: report for report in reports}

    # --- stale -----------------------------------------------------------
    def test_completed_task_still_claimed_is_stale(self):
        self.projects = ("proj-stale",)
        project = init_project(self.root, "proj-stale")
        write_json(
            project / ".claude/tasks/shipped-thing.json",
            {
                "id": "shipped-thing",
                "route": "feature",
                "branch": "feat/shipped-thing",
                "steps": steps(("build", "done"), ("verify", "done"), ("commit", "done")),
            },
        )
        write_json(
            project / ".claude/tasks/active.json",
            {
                "activeTask": "shipped-thing",
                "taskFile": ".claude/tasks/shipped-thing.json",
                "route": "feature",
            },
        )
        commit_all(project, "claim task", "2026-06-01T09:00:00+08:00")
        (project / "app.txt").write_text("later work\n")
        commit_all(project, "later work", "2026-09-01T09:00:00+08:00")

        report = self.by_project(self.scan())["proj-stale"]
        self.assertEqual(report.state, freshness.STATE_STALE_COMPLETED)
        self.assertEqual(report.severity, freshness.SEVERITY_FAIL)
        self.assertTrue(report.provable)

    def test_unfinished_task_untouched_while_repo_moved_on_is_drifted(self):
        self.projects = ("proj-drift",)
        project = init_project(self.root, "proj-drift")
        write_json(
            project / ".claude/tasks/half-done.json",
            {"id": "half-done", "steps": steps(("build", "done"), ("qa", "pending"))},
        )
        write_json(
            project / ".claude/tasks/active.json",
            {"activeTask": "half-done", "taskFile": ".claude/tasks/half-done.json", "route": "feature"},
        )
        commit_all(project, "claim task", "2026-05-01T09:00:00+08:00")
        (project / "app.txt").write_text("later work\n")
        commit_all(project, "later work", "2026-09-01T09:00:00+08:00")

        report = self.by_project(self.scan())["proj-drift"]
        self.assertEqual(report.state, freshness.STATE_STALE_DRIFTED)
        self.assertEqual(report.severity, freshness.SEVERITY_FAIL)
        self.assertGreater(report.drift_days, 30)

    # --- idle ------------------------------------------------------------
    def test_idle_pointer_never_goes_stale(self):
        self.projects = ("proj-idle",)
        project = init_project(self.root, "proj-idle")
        write_json(
            project / ".claude/tasks/active.json",
            {"activeTask": None, "taskFile": None, "route": None},
        )
        commit_all(project, "idle pointer", "2026-01-01T09:00:00+08:00")
        (project / "app.txt").write_text("months of later work\n")
        commit_all(project, "later work", "2026-09-01T09:00:00+08:00")

        report = self.by_project(self.scan())["proj-idle"]
        self.assertEqual(report.state, freshness.STATE_IDLE)
        self.assertEqual(report.severity, freshness.SEVERITY_OK)

    # --- active ----------------------------------------------------------
    def test_current_unfinished_task_is_active(self):
        self.projects = ("proj-active",)
        project = init_project(self.root, "proj-active")
        write_json(
            project / ".claude/tasks/in-flight.json",
            {"id": "in-flight", "branch": "feat/in-flight", "steps": steps(("build", "done"), ("qa", "in_progress"))},
        )
        write_json(
            project / ".claude/tasks/active.json",
            {"activeTask": "in-flight", "taskFile": ".claude/tasks/in-flight.json", "route": "feature"},
        )
        commit_all(project, "base", "2026-09-01T09:00:00+08:00")
        (project / "app.txt").write_text("work\n")
        commit_all(project, "work", "2026-09-05T09:00:00+08:00")

        report = self.by_project(self.scan())["proj-active"]
        self.assertEqual(report.state, freshness.STATE_ACTIVE)
        self.assertEqual(report.severity, freshness.SEVERITY_OK)

    # --- unrelated worktree ---------------------------------------------
    def test_linked_worktree_pointer_is_never_a_failure(self):
        self.projects = ("proj-active",)
        project = init_project(self.root, "proj-active")
        write_json(
            project / ".claude/tasks/in-flight.json",
            {"id": "in-flight", "steps": steps(("qa", "pending"))},
        )
        write_json(
            project / ".claude/tasks/active.json",
            {"activeTask": "in-flight", "taskFile": ".claude/tasks/in-flight.json", "route": "feature"},
        )
        commit_all(project, "base", "2026-09-01T09:00:00+08:00")

        worktrees = self.root / ".worktrees"
        worktrees.mkdir()
        old = worktrees / "proj-active-old-branch"
        git("worktree", "add", "-b", "old-branch", str(old), "main", cwd=project)
        write_json(
            old / ".claude/tasks/obsolete.json",
            {"id": "obsolete", "steps": steps(("commit", "done"))},
        )
        write_json(
            old / ".claude/tasks/active.json",
            {"activeTask": "obsolete", "taskFile": ".claude/tasks/obsolete.json", "route": "feature"},
        )

        reports = self.scan()
        self.assertEqual([report.project for report in reports], ["proj-active"])
        self.assertFalse([r for r in reports if r.severity == freshness.SEVERITY_FAIL])

        worktree_report = freshness.inspect_pointer(
            self.root, "proj-active-old-branch", checkout=old
        )
        self.assertEqual(worktree_report.state, freshness.STATE_NON_CANONICAL)
        self.assertEqual(worktree_report.severity, freshness.SEVERITY_INFO)

    # --- report-do-not-invent -------------------------------------------
    def test_missing_task_file_is_dangling_not_a_guess(self):
        self.projects = ("proj-dangling",)
        project = init_project(self.root, "proj-dangling")
        write_json(
            project / ".claude/tasks/active.json",
            {"activeTask": "ghost", "taskFile": ".claude/tasks/ghost.json", "route": "feature"},
        )
        commit_all(project, "claim", "2026-09-01T09:00:00+08:00")

        report = self.by_project(self.scan())["proj-dangling"]
        self.assertEqual(report.state, freshness.STATE_DANGLING)
        self.assertEqual(report.severity, freshness.SEVERITY_FAIL)

    def test_invalid_json_is_reported_not_repaired(self):
        self.projects = ("proj-invalid",)
        project = init_project(self.root, "proj-invalid")
        (project / ".claude/tasks/active.json").write_text("{ not json")
        commit_all(project, "claim", "2026-09-01T09:00:00+08:00")

        report = self.by_project(self.scan())["proj-invalid"]
        self.assertEqual(report.state, freshness.STATE_INVALID)
        self.assertEqual(report.severity, freshness.SEVERITY_FAIL)

    def test_no_change_evidence_is_unprovable_not_stale(self):
        self.projects = ("proj-nogit",)
        project = self.root / "proj-nogit"
        (project / ".claude/tasks").mkdir(parents=True)
        write_json(
            project / ".claude/tasks/half-done.json",
            {"id": "half-done", "steps": steps(("qa", "pending"))},
        )
        write_json(
            project / ".claude/tasks/active.json",
            {"activeTask": "half-done", "taskFile": ".claude/tasks/half-done.json", "route": "feature"},
        )

        report = self.by_project(self.scan())["proj-nogit"]
        self.assertEqual(report.state, freshness.STATE_UNPROVABLE)
        self.assertEqual(report.severity, freshness.SEVERITY_WARN)
        self.assertFalse(report.provable)

    def test_missing_pointer_is_absent_warning(self):
        self.projects = ("proj-nopointer",)
        project = init_project(self.root, "proj-nopointer")
        (project / "app.txt").write_text("code\n")
        commit_all(project, "base", "2026-09-01T09:00:00+08:00")

        report = self.by_project(self.scan())["proj-nopointer"]
        self.assertEqual(report.state, freshness.STATE_ABSENT)
        self.assertEqual(report.severity, freshness.SEVERITY_WARN)

    def test_missing_checkout_is_informational_only(self):
        self.projects = ("proj-absent-checkout",)
        reports = self.scan()
        self.assertEqual(reports[0].state, freshness.STATE_NO_CHECKOUT)
        self.assertEqual(reports[0].severity, freshness.SEVERITY_INFO)

    def test_fresh_checkout_mtimes_do_not_mask_staleness(self):
        """A clone rewrites every mtime; Git history must still decide."""

        self.projects = ("proj-cloned",)
        project = init_project(self.root, "proj-cloned")
        write_json(
            project / ".claude/tasks/half-done.json",
            {"id": "half-done", "steps": steps(("qa", "pending"))},
        )
        write_json(
            project / ".claude/tasks/active.json",
            {"activeTask": "half-done", "taskFile": ".claude/tasks/half-done.json", "route": "feature"},
        )
        commit_all(project, "claim task", "2026-04-01T09:00:00+08:00")
        (project / "app.txt").write_text("later work\n")
        commit_all(project, "later work", "2026-09-01T09:00:00+08:00")
        # Simulate the clone: every tracked file now carries a just-now mtime.
        (project / ".claude/tasks/active.json").touch()

        report = self.by_project(self.scan())["proj-cloned"]
        self.assertEqual(report.state, freshness.STATE_STALE_DRIFTED)

    def test_uncommitted_pointer_edit_counts_as_a_real_update(self):
        self.projects = ("proj-dirty",)
        project = init_project(self.root, "proj-dirty")
        write_json(
            project / ".claude/tasks/half-done.json",
            {"id": "half-done", "steps": steps(("qa", "pending"))},
        )
        write_json(
            project / ".claude/tasks/active.json",
            {"activeTask": "half-done", "taskFile": ".claude/tasks/half-done.json", "route": "feature"},
        )
        commit_all(project, "claim task", "2026-04-01T09:00:00+08:00")
        (project / "app.txt").write_text("later work\n")
        commit_all(project, "later work", "2026-09-01T09:00:00+08:00")
        write_json(
            project / ".claude/tasks/active.json",
            {"activeTask": "half-done", "taskFile": ".claude/tasks/half-done.json", "route": "bugfix"},
        )

        report = self.by_project(self.scan())["proj-dirty"]
        self.assertEqual(report.state, freshness.STATE_ACTIVE)
        self.assertTrue(any("uncommitted working tree" in line for line in report.evidence))

    # --- false-positive controls for the reassessed rules ---------------
    def test_merged_branch_with_a_pending_post_merge_step_is_not_a_failure(self):
        """Merging happens mid-task: deploy and smoke run after it."""

        self.projects = ("proj-merged",)
        project = init_project(self.root, "proj-merged")
        (project / "app.txt").write_text("base\n")
        commit_all(project, "base", "2026-09-01T09:00:00+08:00")
        git("checkout", "-b", "feat/shipped", cwd=project)
        (project / "app.txt").write_text("feature\n")
        commit_all(project, "feature", "2026-09-02T09:00:00+08:00")
        git("checkout", "main", cwd=project)
        git("merge", "--no-ff", "-m", "merge feature", "feat/shipped", cwd=project)
        write_json(
            project / ".claude/tasks/shipped.json",
            {
                "id": "shipped",
                "branch": "feat/shipped",
                "steps": steps(("commit", "done"), ("deploy", "pending")),
            },
        )
        write_json(
            project / ".claude/tasks/active.json",
            {"activeTask": "shipped", "taskFile": ".claude/tasks/shipped.json", "route": "feature"},
        )
        commit_all(project, "claim task", "2026-09-04T09:00:00+08:00")

        report = self.by_project(self.scan())["proj-merged"]
        self.assertEqual(report.state, freshness.STATE_ACTIVE)
        self.assertEqual(report.severity, freshness.SEVERITY_OK)
        self.assertTrue(
            any(line.startswith("merge:") for line in report.evidence),
            f"merge state must still be reported: {report.evidence}",
        )

    def test_trunk_declared_branch_never_fails_on_merge_ancestry(self):
        """`main` is always an ancestor of itself."""

        self.projects = ("proj-trunk",)
        project = init_project(self.root, "proj-trunk")
        write_json(
            project / ".claude/tasks/on-trunk.json",
            {"id": "on-trunk", "branch": "main", "steps": steps(("qa", "pending"))},
        )
        write_json(
            project / ".claude/tasks/active.json",
            {"activeTask": "on-trunk", "taskFile": ".claude/tasks/on-trunk.json", "route": "bugfix"},
        )
        commit_all(project, "claim task", "2026-09-01T09:00:00+08:00")
        (project / "app.txt").write_text("work\n")
        commit_all(project, "work", "2026-09-03T09:00:00+08:00")

        report = self.by_project(self.scan())["proj-trunk"]
        self.assertEqual(report.state, freshness.STATE_ACTIVE)
        self.assertEqual(report.severity, freshness.SEVERITY_OK)

    def test_long_task_with_a_recently_updated_task_file_is_active(self):
        """active.json names the task; the task file carries the progress."""

        self.projects = ("proj-long",)
        project = init_project(self.root, "proj-long")
        write_json(
            project / ".claude/tasks/long-haul.json",
            {"id": "long-haul", "steps": steps(("build", "in_progress"), ("qa", "pending"))},
        )
        write_json(
            project / ".claude/tasks/active.json",
            {"activeTask": "long-haul", "taskFile": ".claude/tasks/long-haul.json", "route": "feature"},
        )
        commit_all(project, "claim task", "2026-05-01T09:00:00+08:00")
        write_json(
            project / ".claude/tasks/long-haul.json",
            {"id": "long-haul", "steps": steps(("build", "done"), ("qa", "in_progress"))},
        )
        commit_all(project, "tick a step off", "2026-09-01T09:00:00+08:00")
        (project / "app.txt").write_text("more work\n")
        commit_all(project, "more work", "2026-09-03T09:00:00+08:00")

        report = self.by_project(self.scan())["proj-long"]
        self.assertEqual(report.state, freshness.STATE_ACTIVE)
        self.assertLess(report.drift_days, 30)
        self.assertTrue(
            any("task file" in line for line in report.evidence),
            f"the task file must be named as the claim activity source: {report.evidence}",
        )

    def test_a_claim_whose_both_artifacts_went_quiet_still_drifts(self):
        """Removing the merge rule must not create a blind spot."""

        self.projects = ("proj-abandoned",)
        project = init_project(self.root, "proj-abandoned")
        (project / "app.txt").write_text("base\n")
        commit_all(project, "base", "2026-04-01T09:00:00+08:00")
        git("checkout", "-b", "feat/abandoned", cwd=project)
        (project / "app.txt").write_text("feature\n")
        commit_all(project, "feature", "2026-04-02T09:00:00+08:00")
        git("checkout", "main", cwd=project)
        git("merge", "--no-ff", "-m", "merge feature", "feat/abandoned", cwd=project)
        write_json(
            project / ".claude/tasks/abandoned.json",
            {
                "id": "abandoned",
                "branch": "feat/abandoned",
                "steps": steps(("review", "pending")),
            },
        )
        write_json(
            project / ".claude/tasks/active.json",
            {"activeTask": "abandoned", "taskFile": ".claude/tasks/abandoned.json", "route": "feature"},
        )
        commit_all(project, "claim task", "2026-04-05T09:00:00+08:00")
        (project / "app.txt").write_text("months of later work\n")
        commit_all(project, "later work", "2026-09-01T09:00:00+08:00")

        report = self.by_project(self.scan())["proj-abandoned"]
        self.assertEqual(report.state, freshness.STATE_STALE_DRIFTED)
        self.assertEqual(report.severity, freshness.SEVERITY_FAIL)

    def test_ownership_mismatch_is_reported_without_failing(self):
        self.projects = ("proj-owner",)
        project = init_project(self.root, "proj-owner")
        write_json(
            project / ".claude/tasks/in-flight.json",
            {"id": "in-flight", "branch": "feat/somewhere-else", "steps": steps(("qa", "pending"))},
        )
        write_json(
            project / ".claude/tasks/active.json",
            {"activeTask": "in-flight", "taskFile": ".claude/tasks/in-flight.json", "route": "feature"},
        )
        commit_all(project, "base", "2026-09-01T09:00:00+08:00")

        report = self.by_project(self.scan())["proj-owner"]
        self.assertEqual(report.severity, freshness.SEVERITY_OK)
        self.assertTrue(any("ownership" in line for line in report.evidence))


class CommandLineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def run_cli(self, *args: str):
        return subprocess.run(
            [sys.executable, str(MODULE_PATH), "--root", str(self.root), *args],
            text=True,
            capture_output=True,
        )

    def test_clean_workspace_exits_zero(self):
        project = init_project(self.root, "kelas")
        write_json(
            project / ".claude/tasks/active.json",
            {"activeTask": None, "taskFile": None, "route": None},
        )
        commit_all(project, "idle", "2026-09-01T09:00:00+08:00")
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ACTIVE TASK FRESHNESS: PASS", result.stdout)

    def test_drifted_workspace_exits_one_with_action(self):
        project = init_project(self.root, "kelas")
        write_json(
            project / ".claude/tasks/shipped.json",
            {"id": "shipped", "steps": steps(("commit", "done"))},
        )
        write_json(
            project / ".claude/tasks/active.json",
            {"activeTask": "shipped", "taskFile": ".claude/tasks/shipped.json", "route": "feature"},
        )
        commit_all(project, "claim", "2026-09-01T09:00:00+08:00")
        result = self.run_cli()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("ACTIVE TASK FRESHNESS: FAIL", result.stdout)
        self.assertIn("Reset the pointer", result.stdout)

    def test_checkout_without_canonical_projects_skips(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ACTIVE TASK FRESHNESS: SKIP", result.stdout)

    def test_json_output_is_machine_readable(self):
        project = init_project(self.root, "kelas")
        write_json(
            project / ".claude/tasks/active.json",
            {"activeTask": None, "taskFile": None, "route": None},
        )
        commit_all(project, "idle", "2026-09-01T09:00:00+08:00")
        result = self.run_cli("--json")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["summary"]["fail"], 0)
        self.assertEqual(payload["pointers"][0]["state"], freshness.STATE_IDLE)

    def test_self_test_reports_a_ratio(self):
        result = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--self-test"], text=True, capture_output=True
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        total = len(freshness.FIXTURES)
        self.assertIn(f"{total}/{total}", result.stdout)


class RegistryTests(unittest.TestCase):
    def test_project_list_matches_the_workflow_doctor_registry(self):
        doctor = (HERE / "workflow-doctor.sh").read_text()
        block = doctor.split("PROJECTS=(", 1)[1].split(")", 1)[0]
        doctor_projects = tuple(line.strip() for line in block.splitlines() if line.strip())
        self.assertEqual(set(freshness.PROJECTS), set(doctor_projects))


if __name__ == "__main__":
    unittest.main()
