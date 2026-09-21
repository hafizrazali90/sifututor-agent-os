#!/usr/bin/env python3
"""Regression tests for fail-safe worktree leases and reclamation."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("worktree_lifecycle", HERE / "worktree-lifecycle.py")
worktree_lifecycle = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(worktree_lifecycle)


def run(*args: str, cwd: Path) -> str:
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=True)
    return result.stdout.strip()


def init_repo(root: Path) -> Path:
    repo = root / "repo"
    repo.mkdir()
    run("git", "init", "-b", "main", cwd=repo)
    run("git", "config", "user.name", "Fixture", cwd=repo)
    run("git", "config", "user.email", "fixture@example.invalid", cwd=repo)
    (repo / ".gitignore").write_text("node_modules/\nvendor/\n__pycache__/\n.private-note\n")
    (repo / "tracked.txt").write_text("base\n")
    run("git", "add", ".gitignore", "tracked.txt", cwd=repo)
    run("git", "commit", "-m", "base", cwd=repo)
    run("git", "remote", "add", "origin", str(repo), cwd=repo)
    run("git", "update-ref", "refs/remotes/origin/main", "HEAD", cwd=repo)
    return repo


def add_worktree(repo: Path, root: Path, name: str = "candidate") -> Path:
    path = root / name
    run("git", "worktree", "add", "-b", name, str(path), "main", cwd=repo)
    return path


class LeaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = init_repo(self.root)
        self.worktree = add_worktree(self.repo, self.root)
        self.store = worktree_lifecycle.LeaseStore(self.root / "state")
        self.now = dt.datetime(2026, 9, 19, tzinfo=dt.timezone.utc)

    def lease(self, session="one", worktree=None):
        return self.store.create(
            repo=self.repo, worktree=worktree or self.worktree, owner="Codex",
            session=session, purpose="fixture", issue="#74",
            cleanup_condition="merged and released", ttl_hours=2, now=self.now,
        )

    def test_create_heartbeat_and_release(self):
        lease = self.lease()
        self.assertEqual(lease["status"], "active")
        later = self.now + dt.timedelta(minutes=30)
        refreshed = self.store.heartbeat(self.worktree, "one", now=later)
        self.assertEqual(worktree_lifecycle.parse_time(refreshed["heartbeat_at"]), later)
        released = self.store.set_status(self.worktree, "one", "released", "complete", now=later)
        self.assertFalse(worktree_lifecycle.lease_is_live(released, later))

    def test_another_session_cannot_take_live_lease(self):
        self.lease()
        with self.assertRaises(worktree_lifecycle.LifecycleError):
            self.lease(session="two")

    def test_corrupt_lease_cannot_be_overwritten(self):
        path = self.store.path_for(self.worktree)
        path.parent.mkdir(parents=True)
        path.write_text("not-json")
        with self.assertRaises(worktree_lifecycle.LifecycleError):
            self.lease()

    def test_lease_requires_worktree_from_declared_repository(self):
        other_root = self.root / "other-root"
        other_root.mkdir()
        other_repo = init_repo(other_root)
        with self.assertRaises(worktree_lifecycle.LifecycleError):
            self.store.create(
                repo=other_repo, worktree=self.worktree, owner="Codex",
                session="one", purpose="fixture", issue="#74",
                cleanup_condition="released", ttl_hours=2, now=self.now,
            )

    def test_invalid_schema_lease_cannot_be_overwritten(self):
        path = self.store.path_for(self.worktree)
        path.parent.mkdir(parents=True)
        path.write_text('{}')
        with self.assertRaises(worktree_lifecycle.LifecycleError):
            self.lease()
        self.assertEqual(path.read_text(), '{}')

    def test_expired_lease_can_be_reassigned(self):
        self.lease()
        later = self.now + dt.timedelta(hours=3)
        lease = self.store.create(
            repo=self.repo, worktree=self.worktree, owner="Claude", session="two",
            purpose="resume", issue="#74", cleanup_condition="released",
            ttl_hours=2, now=later,
        )
        self.assertEqual(lease["session"], "two")

    def test_ten_distinct_sessions_are_isolated(self):
        worktrees = [add_worktree(self.repo, self.root, f"task-{index}") for index in range(10)]
        def enroll(item):
            index, path = item
            return self.store.create(
                repo=self.repo, worktree=path, owner="Codex",
                session=f"session-{index}", purpose=f"task-{index}", issue="#74",
                cleanup_condition="released", ttl_hours=4, now=self.now,
            )
        with ThreadPoolExecutor(max_workers=10) as pool:
            leases = list(pool.map(enroll, enumerate(worktrees)))
        self.assertEqual({lease["session"] for lease in leases}, {f"session-{i}" for i in range(10)})
        self.assertEqual(len(list((self.root / "state" / "leases").glob("*.json"))), 10)


class ClassificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = init_repo(self.root)
        self.worktree = add_worktree(self.repo, self.root)
        self.store = worktree_lifecycle.LeaseStore(self.root / "state")

    def inspect(self, check_process=False):
        record = next(item for item in worktree_lifecycle.parse_worktrees(self.repo)
                      if Path(item["path"]).resolve() == self.worktree.resolve())
        return worktree_lifecycle.inspect_worktree(
            self.repo, record, self.store, base_ref="origin/main",
            check_process=check_process,
        )

    def test_clean_merged_worktree_is_candidate(self):
        result = self.inspect()
        self.assertEqual(result["classification"], "reclaim_candidate")
        self.assertEqual(result["process_check"], "not_checked")

    def test_dirty_or_untracked_work_is_preserved(self):
        (self.worktree / "new.txt").write_text("unique")
        result = self.inspect()
        self.assertEqual(result["classification"], "preserve")
        self.assertIn("tracked or untracked", result["reasons"][0])

    def test_non_generated_ignored_file_is_preserved(self):
        (self.worktree / ".private-note").write_text("do not remove")
        result = self.inspect()
        self.assertEqual(result["classification"], "preserve")
        self.assertEqual(result["ignored_blocker_count"], 1)

    def test_generated_ignored_directory_does_not_hide_unique_work(self):
        generated = self.worktree / "node_modules"
        generated.mkdir()
        (generated / "fixture.js").write_text("generated")
        result = self.inspect()
        self.assertEqual(result["classification"], "reclaim_candidate")
        self.assertTrue(any("reproducible" in reason for reason in result["reasons"]))

    def test_nested_python_cache_is_recognized_as_generated(self):
        generated = self.worktree / ".claude" / "hooks" / "__pycache__"
        generated.mkdir(parents=True)
        (generated / "hook.cpython-313.pyc").write_bytes(b"generated")

        result = self.inspect()

        self.assertEqual(result["classification"], "reclaim_candidate")

    def test_active_task_pointer_blocks(self):
        task_dir = self.worktree / ".claude" / "tasks"
        task_dir.mkdir(parents=True)
        (task_dir / "active.json").write_text(json.dumps({"activeTask": "task-1"}))
        result = self.inspect()
        self.assertEqual(result["classification"], "preserve")
        self.assertEqual(result["active_task"], "task-1")

    def test_active_task_pointer_inherited_unchanged_from_base_does_not_block(self):
        task_dir = self.repo / ".claude" / "tasks"
        task_dir.mkdir(parents=True)
        pointer = json.dumps({"activeTask": "old-base-task"})
        (task_dir / "active.json").write_text(pointer)
        run("git", "add", ".claude/tasks/active.json", cwd=self.repo)
        run("git", "commit", "-m", "track base task pointer", cwd=self.repo)
        run("git", "update-ref", "refs/remotes/origin/main", "HEAD", cwd=self.repo)
        run("git", "merge", "--ff-only", "main", cwd=self.worktree)

        result = self.inspect()

        self.assertEqual(result["classification"], "reclaim_candidate")
        self.assertEqual(result["inherited_task_pointer"], "old-base-task")

    def test_invalid_task_state_blocks(self):
        task_dir = self.worktree / ".claude" / "tasks"
        task_dir.mkdir(parents=True)
        (task_dir / "active.json").write_text("not-json")
        result = self.inspect()
        self.assertEqual(result["classification"], "preserve")
        self.assertTrue(any("invalid" in reason for reason in result["reasons"]))

    def test_corrupt_lease_state_blocks(self):
        path = self.store.path_for(self.worktree)
        path.parent.mkdir(parents=True)
        path.write_text("not-json")
        result = self.inspect()
        self.assertEqual(result["classification"], "preserve")
        self.assertTrue(any("malformed" in reason for reason in result["reasons"]))

    def test_live_and_parked_leases_block(self):
        for status in ("active", "parked"):
            self.store.create(
                repo=self.repo, worktree=self.worktree, owner="Codex",
                session="one", purpose="fixture", issue="#74",
                cleanup_condition="released", ttl_hours=2,
            )
            if status == "parked":
                self.store.set_status(self.worktree, "one", "parked")
            result = self.inspect()
            self.assertEqual(result["classification"], "preserve")
            self.store.set_status(self.worktree, "one", "released")

    def test_expired_active_lease_still_blocks_reclamation(self):
        old = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc)
        self.store.create(
            repo=self.repo, worktree=self.worktree, owner="Codex",
            session="old-session", purpose="fixture", issue="#74",
            cleanup_condition="released", ttl_hours=1, now=old,
        )
        result = self.inspect()
        self.assertEqual(result["classification"], "preserve")
        self.assertTrue(result["stale_lease"])
        self.assertTrue(any("explicit release" in reason for reason in result["reasons"]))

    def test_unmerged_head_blocks(self):
        (self.worktree / "tracked.txt").write_text("branch\n")
        run("git", "add", "tracked.txt", cwd=self.worktree)
        run("git", "commit", "-m", "unique", cwd=self.worktree)
        result = self.inspect()
        self.assertEqual(result["classification"], "preserve")
        self.assertTrue(any("not contained" in reason for reason in result["reasons"]))

    def test_primary_checkout_is_never_candidate(self):
        record = next(item for item in worktree_lifecycle.parse_worktrees(self.repo)
                      if Path(item["path"]).resolve() == self.repo.resolve())
        result = worktree_lifecycle.inspect_worktree(
            self.repo, record, self.store, base_ref="origin/main"
        )
        self.assertEqual(result["classification"], "preserve")
        self.assertIn("primary", result["reasons"][0])

    def test_reclaim_dry_run_and_apply_preserve_branch(self):
        head = run("git", "rev-parse", "HEAD", cwd=self.worktree)
        with mock.patch.object(worktree_lifecycle, "process_uses_path", return_value=False):
            planned = worktree_lifecycle.reclaim(
                self.repo, self.worktree, head, self.store,
                base_ref="origin/main", apply=False,
            )
            self.assertFalse(planned["applied"])
            self.assertTrue(self.worktree.exists())
            applied = worktree_lifecycle.reclaim(
                self.repo, self.worktree, head, self.store,
                base_ref="origin/main", apply=True,
            )
        self.assertTrue(applied["applied"])
        self.assertFalse(self.worktree.exists())
        self.assertEqual(run("git", "show-ref", "--verify", "refs/heads/candidate", cwd=self.repo).split()[0], head)

    def test_reclaim_refuses_head_change(self):
        with mock.patch.object(worktree_lifecycle, "process_uses_path", return_value=False):
            with self.assertRaises(worktree_lifecycle.LifecycleError):
                worktree_lifecycle.reclaim(
                    self.repo, self.worktree, "wrong", self.store,
                    base_ref="origin/main", apply=True,
                )
        self.assertTrue(self.worktree.exists())

    def test_lease_acquired_during_size_check_prevents_removal(self):
        head = run("git", "rev-parse", "HEAD", cwd=self.worktree)
        def acquire_lease(path):
            self.store.create(
                repo=self.repo, worktree=path, owner="Claude", session="new",
                purpose="resumed work", issue="#74", cleanup_condition="released",
            )
            return 1
        with mock.patch.object(worktree_lifecycle, "process_uses_path", return_value=False), \
                mock.patch.object(worktree_lifecycle, "disk_kib", side_effect=acquire_lease):
            with self.assertRaises(worktree_lifecycle.LifecycleError):
                worktree_lifecycle.reclaim(self.repo, self.worktree, head, self.store,
                                          base_ref="origin/main", apply=True)
        self.assertTrue(self.worktree.exists())

    def test_prune_missing_registration_keeps_branch(self):
        head = run("git", "rev-parse", "HEAD", cwd=self.worktree)
        shutil_target = self.worktree
        subprocess.run(["git", "-C", str(self.repo), "worktree", "remove", str(shutil_target)],
                       text=True, capture_output=True, check=True)
        # Recreate a deliberately stale registration without deleting its branch.
        admin = Path(run("git", "rev-parse", "--git-path", "worktrees", cwd=self.repo))
        if not admin.is_absolute():
            admin = self.repo / admin
        stale = admin / "stale-fixture"
        stale.mkdir(parents=True)
        (stale / "gitdir").write_text(str(self.root / "missing" / ".git") + "\n")
        (stale / "commondir").write_text("../..\n")
        (stale / "HEAD").write_text(head + "\n")
        planned = worktree_lifecycle.prune_missing_registrations(self.repo, apply=False)
        self.assertTrue(any("missing" in path for path in planned["missing"]))
        applied = worktree_lifecycle.prune_missing_registrations(self.repo, apply=True)
        self.assertTrue(applied["applied"])
        self.assertEqual(applied["remaining_missing"], [])
        self.assertEqual(run("git", "show-ref", "--verify", "refs/heads/candidate", cwd=self.repo).split()[0], head)

    def test_reclaim_result_names_exact_removed_path(self):
        head = run("git", "rev-parse", "HEAD", cwd=self.worktree)
        with mock.patch.object(worktree_lifecycle, "process_uses_path", return_value=False):
            applied = worktree_lifecycle.reclaim(
                self.repo, self.worktree, head, self.store,
                base_ref="origin/main", apply=True,
            )
        self.assertEqual(applied["worktree"], str(self.worktree.resolve()))
        self.assertTrue(applied["applied"])
        self.assertTrue(applied["removed"])


class DependencyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = init_repo(self.root)
        self.source = add_worktree(self.repo, self.root, "source")
        self.target = add_worktree(self.repo, self.root, "target")
        for path in (self.source, self.target):
            (path / "package-lock.json").write_text('{"lockfileVersion":3}\n')
        (self.source / "node_modules").mkdir()
        (self.source / "node_modules" / "fixture.js").write_text("module")

    def test_donor_requires_identical_lockfiles(self):
        donors = worktree_lifecycle.dependency_donors(self.repo, self.target)
        self.assertEqual([item["worktree"] for item in donors], [str(self.source.resolve())])
        (self.target / "package-lock.json").write_text('{"lockfileVersion":2}\n')
        self.assertEqual(worktree_lifecycle.dependency_donors(self.repo, self.target), [])

    def test_seed_dry_run_and_apply(self):
        planned = worktree_lifecycle.seed_dependencies(self.source, self.target, apply=False)
        self.assertFalse(planned["applied"])
        self.assertFalse((self.target / "node_modules").exists())
        applied = worktree_lifecycle.seed_dependencies(self.source, self.target, apply=True)
        self.assertTrue(applied["applied"])
        self.assertEqual((self.target / "node_modules" / "fixture.js").read_text(), "module")

    def test_seed_refuses_existing_target_or_lock_mismatch(self):
        (self.target / "node_modules").mkdir()
        with self.assertRaises(worktree_lifecycle.LifecycleError):
            worktree_lifecycle.seed_dependencies(self.source, self.target, apply=True)
        (self.target / "node_modules").rmdir()
        (self.target / "package-lock.json").write_text("different")
        with self.assertRaises(worktree_lifecycle.LifecycleError):
            worktree_lifecycle.seed_dependencies(self.source, self.target, apply=True)

    def test_install_command_uses_frozen_lockfile(self):
        cases = {
            "package-lock.json": ["npm", "ci"],
            "pnpm-lock.yaml": ["pnpm", "install", "--frozen-lockfile"],
            "yarn.lock": ["yarn", "install", "--frozen-lockfile"],
            "bun.lock": ["bun", "install", "--frozen-lockfile"],
            "composer.lock": ["composer", "install", "--no-interaction", "--no-scripts"],
        }
        for lockfile, expected in cases.items():
            with self.subTest(lockfile=lockfile):
                target = self.root / lockfile.replace(".", "-")
                target.mkdir()
                (target / lockfile).write_text("lock")
                self.assertEqual(worktree_lifecycle.dependency_install_command(target), expected)

    def test_automatic_setup_supports_node_and_composer_together(self):
        target = self.root / "mixed-lockfiles"
        target.mkdir()
        (target / "package-lock.json").write_text("node")
        (target / "composer.lock").write_text("php")

        self.assertEqual(
            worktree_lifecycle.dependency_install_commands(target),
            [
                ("node_modules", ["npm", "ci"]),
                ("vendor", ["composer", "install", "--no-interaction", "--no-scripts"]),
            ],
        )

    def test_create_worktree_leases_and_reuses_matching_dependencies(self):
        (self.repo / "package-lock.json").write_text('{"lockfileVersion":3}\n')
        run("git", "add", "package-lock.json", cwd=self.repo)
        run("git", "commit", "-m", "add lockfile", cwd=self.repo)
        run("git", "update-ref", "refs/remotes/origin/main", "HEAD", cwd=self.repo)
        target = self.root / "created"
        result = worktree_lifecycle.create_worktree(
            self.repo, target, branch="created", base_ref="origin/main",
            store=worktree_lifecycle.LeaseStore(self.root / "create-state"),
            owner="Codex", session="create-session", purpose="fixture",
            issue="#146", cleanup_condition="merged", install_if_needed=True,
        )
        self.assertEqual(result["dependency_action"], "seeded")
        self.assertTrue((target / "node_modules" / "fixture.js").is_file())
        self.assertEqual(result["lease"]["status"], "active")

    def test_create_worktree_reports_no_lockfile_without_installing(self):
        for path in (self.repo, self.source, self.target):
            (path / "package-lock.json").unlink(missing_ok=True)
        target = self.root / "no-lock-created"
        result = worktree_lifecycle.create_worktree(
            self.repo, target, branch="no-lock-created", base_ref="origin/main",
            store=worktree_lifecycle.LeaseStore(self.root / "no-lock-state"),
            owner="Codex", session="create-session", purpose="fixture",
            issue="#146", cleanup_condition="merged", install_if_needed=True,
        )
        self.assertEqual(result["dependency_action"], "not-applicable")

    def test_create_worktree_removes_checkout_when_lease_registration_fails(self):
        target = self.root / "lease-failure"
        store = mock.Mock()
        store.create.side_effect = worktree_lifecycle.LifecycleError("lease failed")

        with self.assertRaises(worktree_lifecycle.LifecycleError):
            worktree_lifecycle.create_worktree(
                self.repo, target, branch="lease-failure", base_ref="origin/main",
                store=store, owner="Codex", session="create-session",
                purpose="fixture", issue="#146", cleanup_condition="merged",
                install_if_needed=False,
            )

        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
