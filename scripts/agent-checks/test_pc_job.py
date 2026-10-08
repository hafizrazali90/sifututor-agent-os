#!/usr/bin/env python3
"""Tests for the unattended job runner, with a real temporary git repo and fake claude and gh."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import pc_job  # noqa: E402

REAL_RENDER = HERE / "render-claude-settings.py"

FAKE_CLAUDE = r"""#!/bin/sh
# fake claude: behaviour chosen by FAKE_MODE
printf '%s\n' "$@" > "$ARGV_LOG"
ok='{"type":"result","subtype":"success","is_error":false,"num_turns":2,"total_cost_usd":0.12,"result":"%s"}'
case "$FAKE_MODE" in
  edit_commit)   echo x >> docs/a.md; git add docs/a.md; git commit -q -m "docs: change a"; printf "$ok" "Status: done" ;;
  edit_nocommit) echo x >> docs/a.md; printf "$ok" "Status: done" ;;
  outside)       echo x >> docs/b.md; git add docs/b.md; git commit -q -m "docs: change b"; printf "$ok" "Status: done" ;;
  nochange)      printf "$ok" "Status: done" ;;
  maxturns)      printf '{"type":"result","subtype":"error_max_turns","is_error":true,"num_turns":3,"total_cost_usd":0.4}' ;;
  garbage)       echo "this is not json" ;;
  hang)          sleep 30 ;;
  review_ok)     printf "$ok" "Verdict: ACCEPT" ;;
  review_edit)   echo x >> docs/a.md; printf "$ok" "Verdict: ACCEPT" ;;
  *)             echo "unknown FAKE_MODE" >&2; exit 3 ;;
esac
"""

FAKE_GH = """#!/bin/sh
printf '%s\\n' "$@" > "$GH_LOG"
echo https://github.com/example/repo/pull/9
"""

BRIEF = """---
title: Change a
role: builder
branch: docs/900-change-a
finish: {finish}
{extra}allowed_paths: docs/a.md
---
Add one line to docs/a.md as described.
"""

REVIEW_BRIEF = """---
title: Review change
role: reviewer
target: docs/900-reviewed
---
Review the branch against the base and report.
"""


def git(cwd: Path, *args: str) -> str:
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    return subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True, check=True).stdout


class RunnerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.origin = self.tmp / "origin.git"
        self.repo = self.tmp / "repo"
        git(self.tmp, "init", "-q", "--bare", "-b", "main", str(self.origin))
        git(self.tmp, "clone", "-q", str(self.origin), str(self.repo))
        git(self.repo, "checkout", "-q", "-b", "main")
        (self.repo / "docs").mkdir()
        (self.repo / "docs" / "a.md").write_text("a\n")
        (self.repo / "docs" / "b.md").write_text("b\n")
        (self.repo / "scripts" / "agent-checks").mkdir(parents=True)
        (self.repo / "scripts" / "agent-checks" / "hook.py").write_text("")
        shutil.copy(REAL_RENDER, self.repo / "scripts" / "agent-checks" / "render-claude-settings.py")
        (self.repo / ".claude").mkdir()
        template = {"$schema": "x", "hooks": {"PreToolUse": [{"matcher": ".*", "hooks": [
            {"type": "command", "command": 'python3 "${CLAUDE_PROJECT_DIR}"/scripts/agent-checks/hook.py'}]}]}}
        (self.repo / ".claude" / "settings.template.json").write_text(json.dumps(template))
        (self.repo / ".gitignore").write_text(".claude/*\n!.claude/settings.template.json\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "init")
        git(self.repo, "push", "-q", "origin", "main")

        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        for name, body in (("claude", FAKE_CLAUDE), ("gh", FAKE_GH)):
            (self.bin / name).write_text(body)
            (self.bin / name).chmod(0o755)
        self.argv_log, self.gh_log = self.tmp / "argv.log", self.tmp / "gh.log"
        self.worktrees = self.tmp / "worktrees"
        env = {
            "PATH": f"{self.bin}:{os.environ['PATH']}", "ARGV_LOG": str(self.argv_log), "GH_LOG": str(self.gh_log),
            "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
        }
        patcher = mock.patch.dict(os.environ, env)
        patcher.start()
        self.addCleanup(patcher.stop)

    def job(self, brief: str, mode: str, name: str = "20261008-100000-test") -> Path:
        job_dir = self.tmp / "jobs" / name
        job_dir.mkdir(parents=True)
        (job_dir / "brief.md").write_text(brief)
        (job_dir / "role.txt").write_text("ROLE TEXT")
        os.environ["FAKE_MODE"] = mode
        return job_dir

    def run_job(self, job_dir: Path, **kwargs) -> dict:
        pc_job.run(job_dir, repo=self.repo, claude=str(self.bin / "claude"), worktrees=self.worktrees,
                   drop_task=False, **kwargs)
        return json.loads((job_dir / "status.json").read_text())

    def builder(self, finish: str = "local", extra: str = "", mode: str = "edit_commit") -> tuple[Path, dict]:
        job_dir = self.job(BRIEF.format(finish=finish, extra=extra), mode)
        return job_dir, self.run_job(job_dir)

    # ------------------------------------------------------------ builder ----

    def test_local_success_writes_status_and_result(self) -> None:
        job_dir, status = self.builder()
        self.assertEqual(status["state"], "done", status)
        self.assertEqual(status["commits"], 1)
        self.assertEqual(status["changed_files"], ["docs/a.md"])
        self.assertEqual(status["cost_usd"], 0.12)
        result = (job_dir / "result.md").read_text()
        self.assertIn("DONE", result)
        self.assertIn("MYT", result)
        self.assertTrue((job_dir / "result.json").is_file())

    def test_local_job_does_not_push(self) -> None:
        self.builder()
        self.assertEqual(git(self.repo, "ls-remote", "--heads", "origin", "docs/900-change-a").strip(), "")

    def test_change_outside_allowed_paths_is_blocked(self) -> None:
        _, status = self.builder(mode="outside")
        self.assertEqual(status["state"], "blocked")
        self.assertIn("docs/b.md", status["reason"])

    def test_blocked_job_is_never_pushed_even_with_pr_open(self) -> None:
        _, status = self.builder(finish="pr-open", extra="approval: Hafiz, chat\n", mode="outside")
        self.assertEqual(status["state"], "blocked")
        self.assertEqual(git(self.repo, "ls-remote", "--heads", "origin", "docs/900-change-a").strip(), "")
        self.assertFalse(self.gh_log.exists())

    def test_committed_without_a_commit_is_blocked(self) -> None:
        _, status = self.builder(finish="committed", mode="edit_nocommit")
        self.assertEqual(status["state"], "blocked")
        self.assertIn("commit", status["reason"])

    def test_pr_open_pushes_the_branch_and_opens_the_pull_request(self) -> None:
        _, status = self.builder(finish="pr-open", extra="approval: Hafiz, chat\n")
        self.assertEqual(status["state"], "done", status)
        self.assertNotEqual(git(self.repo, "ls-remote", "--heads", "origin", "docs/900-change-a").strip(), "")
        self.assertEqual(status["pr_url"], "https://github.com/example/repo/pull/9")
        args = self.gh_log.read_text().split()
        self.assertIn("--base", args)
        self.assertEqual(args[args.index("--base") + 1], "main")
        self.assertEqual(args[args.index("--head") + 1], "docs/900-change-a")

    def test_max_turns_marks_the_job_failed(self) -> None:
        _, status = self.builder(mode="maxturns")
        self.assertEqual(status["state"], "failed")
        self.assertEqual(status["reason"], "error_max_turns")

    def test_unreadable_claude_output_marks_the_job_failed(self) -> None:
        _, status = self.builder(mode="garbage")
        self.assertEqual(status["state"], "failed")

    def test_test_time_limit_marks_the_job_timeout(self) -> None:
        job_dir = self.job(BRIEF.format(finish="local", extra=""), "hang")
        status = self.run_job(job_dir, timeout_override=1)
        self.assertEqual(status["state"], "timeout")

    def test_existing_branch_is_blocked(self) -> None:
        git(self.repo, "branch", "docs/900-change-a")
        _, status = self.builder()
        self.assertEqual(status["state"], "blocked")
        self.assertIn("already exists", status["reason"])

    def test_invalid_brief_is_re_checked_on_the_pc(self) -> None:
        _, status = self.builder(finish="merged")
        self.assertEqual(status["state"], "blocked")
        self.assertIn("cannot merge or deploy", status["reason"])

    def drop_template_from_branch(self) -> str:
        template = (self.repo / ".claude" / "settings.template.json").read_text()
        git(self.repo, "rm", "-q", ".claude/settings.template.json")
        git(self.repo, "commit", "-q", "-m", "drop template")
        git(self.repo, "push", "-q", "origin", "main")
        return template

    def test_missing_guards_stop_the_job_before_claude_starts(self) -> None:
        self.drop_template_from_branch()
        _, status = self.builder()
        self.assertEqual(status["state"], "blocked")
        self.assertIn("without guards", status["reason"])
        self.assertFalse(self.argv_log.exists(), "claude must not start without guards")

    def test_branch_without_a_template_uses_the_copy_that_travelled_with_the_job(self) -> None:
        template = self.drop_template_from_branch()
        job_dir = self.job(BRIEF.format(finish="local", extra=""), "edit_commit")
        (job_dir / "settings.template.json").write_text(template)
        shutil.copy(REAL_RENDER, job_dir / "render-claude-settings.py")
        status = self.run_job(job_dir)
        self.assertEqual(status["state"], "done", status)
        self.assertTrue((Path(status["worktree"]) / ".claude" / "settings.json").is_file())
        self.assertEqual(status["changed_files"], ["docs/a.md"], "the shipped template must not show up as a change")

    def test_shipped_template_naming_a_missing_script_is_refused(self) -> None:
        template = json.loads(self.drop_template_from_branch())
        template["hooks"]["PreToolUse"][0]["hooks"][0]["command"] = 'python3 "${CLAUDE_PROJECT_DIR}"/scripts/agent-checks/not-there.py'
        job_dir = self.job(BRIEF.format(finish="local", extra=""), "edit_commit")
        (job_dir / "settings.template.json").write_text(json.dumps(template))
        shutil.copy(REAL_RENDER, job_dir / "render-claude-settings.py")
        status = self.run_job(job_dir)
        self.assertEqual(status["state"], "blocked")
        self.assertIn("not-there.py", status["reason"])
        self.assertFalse(self.argv_log.exists(), "claude must not start when a guard script is missing")

    def test_missing_git_identity_stops_a_committing_job_before_claude_starts(self) -> None:
        empty = self.tmp / "empty-gitconfig"
        empty.write_text("")
        with mock.patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": str(empty), "GIT_CONFIG_SYSTEM": str(empty), "HOME": str(self.tmp)}):
            for name in ("GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL"):
                os.environ.pop(name, None)
            _, status = self.builder(finish="committed")
        self.assertEqual(status["state"], "blocked")
        self.assertIn("git identity", status["reason"])
        self.assertFalse(self.argv_log.exists(), "claude must not start without a git identity")

    def test_local_job_does_not_need_a_git_identity(self) -> None:
        empty = self.tmp / "empty-gitconfig"
        empty.write_text("")
        with mock.patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": str(empty), "GIT_CONFIG_SYSTEM": str(empty), "HOME": str(self.tmp)}):
            _, status = self.builder(finish="local", mode="nochange")
        self.assertEqual(status["state"], "done", status)

    def test_guards_are_wired_in_the_job_worktree(self) -> None:
        _, status = self.builder()
        settings = Path(status["worktree"]) / ".claude" / "settings.json"
        self.assertTrue(settings.is_file())

    # ------------------------------------------------------- project repo ----

    def project_layout(self) -> Path:
        """Put the repo under an umbrella folder as a project, with tracked settings."""
        root = self.tmp / "umbrella"
        root.mkdir()
        git(self.repo, "rm", "-q", "--cached", ".claude/settings.template.json")
        (self.repo / ".claude" / "settings.template.json").unlink()
        settings = {"hooks": {"PreToolUse": [{"matcher": ".*", "hooks": [{"type": "command", "command": "true"}]}]}}
        (self.repo / ".claude" / "settings.json").write_text(json.dumps(settings))
        (self.repo / ".gitignore").write_text("")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "project settings")
        git(self.repo, "push", "-q", "origin", "main")
        shutil.move(str(self.repo), str(root / "ripple-suite"))
        self.repo = root / "ripple-suite"
        return root

    def test_project_repo_job_runs_in_the_named_repo(self) -> None:
        root = self.project_layout()
        job_dir = self.job(BRIEF.format(finish="local", extra="repo: ripple-suite\n"), "edit_commit")
        pc_job.run(job_dir, repo=root, claude=str(self.bin / "claude"), worktrees=self.worktrees, drop_task=False)
        status = json.loads((job_dir / "status.json").read_text())
        self.assertEqual(status["state"], "done", status)
        self.assertEqual(status["repo"], "ripple-suite")
        self.assertEqual(status["changed_files"], ["docs/a.md"])
        allowed = self.argv()[self.argv().index("--allowedTools") + 1].split(",")
        self.assertIn("Bash(npx vitest:*)", allowed)
        self.assertNotIn("Bash(git push:*)", allowed)

    def test_project_repo_without_tracked_settings_is_refused(self) -> None:
        root = self.project_layout()
        git(self.repo, "rm", "-q", ".claude/settings.json")
        git(self.repo, "commit", "-q", "-m", "drop settings")
        git(self.repo, "push", "-q", "origin", "main")
        job_dir = self.job(BRIEF.format(finish="local", extra="repo: ripple-suite\n"), "edit_commit")
        pc_job.run(job_dir, repo=root, claude=str(self.bin / "claude"), worktrees=self.worktrees, drop_task=False)
        status = json.loads((job_dir / "status.json").read_text())
        self.assertEqual(status["state"], "blocked")
        self.assertIn("without guards", status["reason"])
        self.assertFalse(self.argv_log.exists(), "claude must not start without guards")

    def test_project_repo_not_checked_out_is_blocked(self) -> None:
        root = self.tmp / "empty-umbrella"
        root.mkdir()
        job_dir = self.job(BRIEF.format(finish="local", extra="repo: ripple-suite\n"), "edit_commit")
        pc_job.run(job_dir, repo=root, claude=str(self.bin / "claude"), worktrees=self.worktrees, drop_task=False)
        status = json.loads((job_dir / "status.json").read_text())
        self.assertEqual(status["state"], "blocked")
        self.assertIn("not checked out", status["reason"])

    def test_linux_user_bin_goes_first_on_the_pc(self) -> None:
        home = self.tmp / "home"
        (home / ".local" / "bin").mkdir(parents=True)
        with mock.patch.object(pc_job.sys, "platform", "linux"), \
                mock.patch.object(pc_job.Path, "home", return_value=home), \
                mock.patch.dict(os.environ, {"PATH": f"/mnt/c/nvm4w/nodejs:{home}/.local/bin:/usr/bin"}):
            pc_job.prefer_linux_user_tools()
            self.assertEqual(os.environ["PATH"].split(os.pathsep), [f"{home}/.local/bin", "/mnt/c/nvm4w/nodejs", "/usr/bin"])

    def test_umbrella_job_does_not_get_project_tools(self) -> None:
        self.builder()
        self.assertNotIn("Bash(npx vitest:*)", self.argv()[self.argv().index("--allowedTools") + 1].split(","))

    # ----------------------------------------------------------- reviewer ----

    def make_review_target(self) -> None:
        git(self.repo, "checkout", "-q", "-b", "docs/900-reviewed")
        (self.repo / "docs" / "a.md").write_text("changed\n")
        git(self.repo, "commit", "-q", "-am", "docs: reviewed change")
        git(self.repo, "push", "-q", "origin", "docs/900-reviewed")
        git(self.repo, "checkout", "-q", "main")

    def test_reviewer_reads_the_target_and_reports_a_verdict(self) -> None:
        self.make_review_target()
        job_dir = self.job(REVIEW_BRIEF, "review_ok")
        status = self.run_job(job_dir)
        self.assertEqual(status["state"], "done", status)
        self.assertEqual(status["verdict"], "ACCEPT")

    def test_reviewer_that_changes_a_file_is_blocked(self) -> None:
        self.make_review_target()
        job_dir = self.job(REVIEW_BRIEF, "review_edit")
        status = self.run_job(job_dir)
        self.assertEqual(status["state"], "blocked")
        self.assertIn("read-only", status["reason"])

    # -------------------------------------------------------------- flags ----

    def argv(self) -> list[str]:
        return self.argv_log.read_text().splitlines()

    def test_builder_command_has_no_caps_and_never_skips_permissions(self) -> None:
        self.builder()
        argv = self.argv()
        self.assertNotIn("--dangerously-skip-permissions", argv)
        self.assertNotIn("--max-budget-usd", argv)
        self.assertNotIn("--max-turns", argv)
        self.assertEqual(argv[argv.index("--permission-prompts") + 1], "none")
        self.assertEqual(argv[argv.index("--permission-mode") + 1], "acceptEdits")
        allowed = argv[argv.index("--allowedTools") + 1]
        self.assertIn("Edit", allowed.split(","))
        self.assertNotIn("Bash(git push:*)", allowed)
        self.assertEqual(argv[argv.index("--append-system-prompt") + 1], "ROLE TEXT")

    def test_reviewer_command_denies_edit_and_write(self) -> None:
        self.make_review_target()
        self.run_job(self.job(REVIEW_BRIEF, "review_ok"))
        argv = self.argv()
        self.assertEqual(argv[argv.index("--permission-mode") + 1], "dontAsk")
        denied = argv[argv.index("--disallowedTools") + 1].split(",")
        self.assertTrue({"Edit", "Write"} <= set(denied))
        self.assertNotIn("Edit", argv[argv.index("--allowedTools") + 1].split(","))


class MacSideTest(unittest.TestCase):
    def brief_file(self, text: str) -> Path:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        path = tmp / "brief.md"
        path.write_text(text)
        return path

    def test_job_id_is_dated_in_myt_and_safe(self) -> None:
        import datetime as dt
        moment = dt.datetime(2026, 10, 8, 2, 30, tzinfo=dt.timezone.utc)
        self.assertEqual(pc_job.make_job_id("Add rules: v2!", moment), "20261008-103000-add-rules-v2")
        self.assertRegex(pc_job.make_job_id("###"), r"^\d{8}-\d{6}-job$")
        long = pc_job.make_job_id("Review hook template pull request 302", moment)
        self.assertEqual(long, "20261008-103000-review-hook-template-pull")

    def test_invalid_brief_is_refused_without_calling_the_pc(self) -> None:
        runner = mock.Mock()
        lines: list[str] = []
        code = pc_job.submit(self.brief_file(BRIEF.format(finish="deployed", extra="")), runner=runner, out=lines.append)
        self.assertEqual(code, 2)
        runner.assert_not_called()
        self.assertTrue(any("cannot merge or deploy" in line for line in lines))

    def test_dry_run_calls_nothing(self) -> None:
        runner = mock.Mock()
        code = pc_job.submit(self.brief_file(BRIEF.format(finish="local", extra="")), dry_run=True, runner=runner, out=lambda _: None)
        self.assertEqual(code, 0)
        runner.assert_not_called()

    def test_submit_installs_the_files_then_starts_a_scheduler_task(self) -> None:
        calls: list[tuple[list[str], str | None]] = []

        def fake_runner(cmd, input=None, **kwargs):
            calls.append((cmd, input))
            return subprocess.CompletedProcess(cmd, 0, stdout="ok", stderr="")

        lines: list[str] = []
        code = pc_job.submit(self.brief_file(BRIEF.format(finish="local", extra="")), runner=fake_runner, out=lines.append)
        self.assertEqual(code, 0)
        self.assertEqual(len(calls), 2)
        install_cmd, install_input = calls[0]
        self.assertEqual(install_cmd[-1], "wsl -d Ubuntu -u hafiz -e sh -s")
        for name in ("brief.md", "pc_job.py", "job_brief.py", "role.txt", "start.sh", "settings.template.json", "render-claude-settings.py"):
            self.assertIn(f'/{name}"', install_input)
        job_id = re.search(r"Job (\S+):", lines[0]).group(1)
        schtasks = calls[1][0][-1]
        self.assertIn(f'/tn "job-{job_id}"', schtasks)
        self.assertIn(f"wsl.exe -d Ubuntu -u hafiz -e /home/hafiz/jobs/{job_id}/start.sh", schtasks)
        self.assertIn("schtasks /run", schtasks)

    def test_remote_cat_refuses_a_path_trick(self) -> None:
        for bad in ("../etc/passwd", "x; rm -rf ~", ""):
            with self.subTest(job_id=bad):
                with self.assertRaises(ValueError):
                    pc_job.remote_cat(bad, "status.json", runner=mock.Mock())

    def test_start_script_runs_the_copied_runner_and_logs(self) -> None:
        script = pc_job.start_sh("20261008-100000-x")
        self.assertIn("python3 pc_job.py run", script)
        self.assertIn("runner.log", script)


if __name__ == "__main__":
    unittest.main()
