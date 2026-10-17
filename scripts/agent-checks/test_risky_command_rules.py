#!/usr/bin/env python3
"""Tests for the destructive and production command rules in the shared guard.

Agreed with Hafiz on 17/10/2026:
- destructive commands are always refused, and no phrase can waive them;
- production deploy and merge into main or a production branch pass only after
  Hafiz typed "deploy ok" in this session (a note written by a prompt hook);
- staging, feature-branch pushes, commits and tests are not touched.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
CHECKS = ROOT / "scripts" / "agent-checks"
GUARD_PATH = CHECKS / "secret_output_guard.py"
RULES_PATH = CHECKS / "risky_command_rules.py"
NOTE_PATH = CHECKS / "deploy_ok_note.py"


def load(name: str, path: Path):
    sys.path.insert(0, str(CHECKS))
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RiskyCommandRulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rules = load("risky_command_rules", RULES_PATH)
        cls.guard = load("secret_output_guard", GUARD_PATH)

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        patcher = mock.patch.dict(os.environ, {"AGENT_OS_APPROVAL_DIR": self.tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)
        branch = mock.patch.object(self.rules, "current_branch", return_value="feature/x")
        branch.start()
        self.addCleanup(branch.stop)

    def decide(self, command: str, session: str = "s1"):
        return self.guard.evaluate_tool_request("Bash", {"command": command}, {"session_id": session})

    def blocked(self, command: str, session: str = "s1") -> None:
        decision = self.decide(command, session)
        self.assertFalse(decision.allowed, f"should be refused: {command}")
        self.assertTrue(decision.reason)

    def allowed(self, command: str, session: str = "s1") -> None:
        decision = self.decide(command, session)
        self.assertTrue(decision.allowed, f"should be allowed: {command} ({decision.reason})")

    def approve(self, session: str = "s1") -> None:
        load("deploy_ok_note", NOTE_PATH).write_note(session)

    # -- destructive: always refused, even with a note ---------------------------------

    DESTRUCTIVE = (
        "git push --force origin main",
        "git push -f",
        "git push origin +main",
        "git push --force-with-lease origin feature/x",
        "git push -fu origin feature/x",
        "git push origin --delete old-branch",
        "git push origin :old-branch",
        "git -C /tmp/repo push --force",
        "git reset --hard HEAD~3",
        "git reset --hard",
        "git clean -fd",
        "git clean -fdx",
        "git clean --force",
        "git branch -D feature/x",
        "git branch --delete --force feature/x",
        "mysql -e 'DROP DATABASE sims'",
        "psql -c 'drop table tutors'",
        "mysql -e 'TRUNCATE TABLE invoices'",
        "php artisan migrate:fresh",
        "php artisan db:wipe",
        "php artisan migrate:reset",
        "ssh server 'php artisan migrate:fresh'",
        "bash -c 'git reset --hard'",
        "env FOO=1 git push --force",
        "rm -rf /",
        "rm -rf /*",
        "rm -rf ~",
        "rm -rf ~/",
        "rm -rf $HOME",
        "rm -rf ~/Projects",
        "rm -rf /Users/someone/Projects",
        "rm -rf ../other-repo",
        "rm -rf /etc/nginx",
        "rm -rf .git",
        "rm -rf .",
        "rm -rf *",
    )

    def test_destructive_commands_are_refused(self) -> None:
        for command in self.DESTRUCTIVE:
            with self.subTest(command=command):
                self.blocked(command)

    def test_destructive_commands_stay_refused_with_a_deploy_ok_note(self) -> None:
        self.approve()
        for command in self.DESTRUCTIVE:
            with self.subTest(command=command):
                self.blocked(command)

    SAFE = (
        "git push origin feature/x",
        "git push -u origin docs/383-safety-hook",
        "git push",
        "git reset --soft HEAD~1",
        "git reset HEAD file.txt",
        "git clean -n",
        "git clean -nfd",
        "git clean --dry-run -fd",
        "git branch -d merged-branch",
        "git branch --delete merged-branch",
        "git branch -a",
        "git status",
        "git log --oneline -3",
        "rm -rf node_modules",
        "rm -rf ./dist",
        "rm file.txt",
        "rm -rf /tmp/scratch-dir",
        "rm -rf /private/tmp/claude-501/run1",
        "rm -rf /var/folders/zz/T/tmpabc",
        "rm -rf ~/.local/state/sifututor-agent-os/worktrees/old",
        "mysql -e 'select 1'",
        "psql -c 'select count(*) from tutors'",
        "php artisan migrate",
        "php artisan test",
        "python3 -m unittest discover",
        "gh pr create --title x --body y",
        "gh pr view 384",
        "gh issue comment 383 --body hi",
    )

    def test_everyday_commands_are_untouched(self) -> None:
        for command in self.SAFE:
            with self.subTest(command=command):
                self.allowed(command)

    # -- production: needs a deploy ok note for this session -------------------------------

    PRODUCTION = (
        "vercel --prod",
        "vercel deploy --prod",
        "vercel promote https://x.vercel.app",
        "npx vercel --prod",
        "git push origin main",
        "git push origin HEAD:main",
        "git push origin master",
        "git push origin production",
        "git push -u origin main",
    )

    def test_production_commands_need_a_note(self) -> None:
        for command in self.PRODUCTION:
            with self.subTest(command=command):
                self.blocked(command)

    def test_the_refusal_says_how_to_continue(self) -> None:
        reason = self.decide("vercel --prod").reason.lower()
        self.assertIn("deploy ok", reason)

    def test_production_commands_pass_with_a_note(self) -> None:
        self.approve()
        for command in self.PRODUCTION:
            with self.subTest(command=command):
                self.allowed(command)

    def test_a_note_for_one_session_does_not_cover_another(self) -> None:
        self.approve("s1")
        self.allowed("vercel --prod", session="s1")
        self.blocked("vercel --prod", session="s2")

    def test_an_expired_note_does_not_count(self) -> None:
        note = load("deploy_ok_note", NOTE_PATH)
        note.write_note("s1", now=1_000.0)
        with mock.patch.object(note.time, "time", return_value=1_000.0 + 13 * 3600):
            self.assertFalse(note.note_active("s1"))

    def test_merge_into_main_needs_a_note_but_staging_does_not(self) -> None:
        with mock.patch.object(self.rules, "pr_base_branch", return_value="main"):
            self.blocked("gh pr merge 384 --merge")
        with mock.patch.object(self.rules, "pr_base_branch", return_value="sifu-staging"):
            self.allowed("gh pr merge 12 --merge")

    def test_merge_with_an_unknown_base_is_treated_as_production(self) -> None:
        with mock.patch.object(self.rules, "pr_base_branch", return_value=None):
            self.blocked("gh pr merge 384 --merge")

    def test_merge_into_main_passes_with_a_note(self) -> None:
        self.approve()
        with mock.patch.object(self.rules, "pr_base_branch", return_value="main"):
            self.allowed("gh pr merge 384 --merge")

    PRODUCTION_RUNNERS = (
        "npx -y vercel --prod",
        "npx --yes vercel deploy --prod",
        "npm exec vercel -- --prod",
        "npm exec -- vercel --prod",
        "yarn vercel --prod",
        "yarn dlx vercel --prod",
        "pnpm exec vercel --prod",
        "pnpm vercel --prod",
        "pnpm dlx vercel promote https://x.vercel.app",
        "bunx --bun vercel --prod",
        "gh api -X PUT repos/o/r/pulls/12/merge",
        "gh api repos/o/r/pulls/12/merge --method PUT",
        "gh api --method=PUT repos/o/r/pulls/12/merge",
    )

    def test_vercel_and_merge_through_other_runners_need_a_note(self) -> None:
        for command in self.PRODUCTION_RUNNERS:
            with self.subTest(command=command):
                self.blocked(command)

    def test_runners_pass_with_a_note_and_harmless_ones_are_untouched(self) -> None:
        self.approve()
        for command in self.PRODUCTION_RUNNERS:
            with self.subTest(command=command):
                self.allowed(command)
        for command in ("npx -y prettier --check .", "npm exec eslint .", "pnpm exec vitest", "yarn test", "gh api repos/o/r/pulls/12"):
            with self.subTest(command=command):
                self.allowed(command)

    def test_deleting_a_branch_through_the_api_is_destructive(self) -> None:
        self.approve()
        for command in (
            "gh api -X DELETE repos/o/r/git/refs/heads/feature/x",
            "gh api --method DELETE repos/o/r/git/refs/heads/feature/x",
            "gh api repos/o/r/git/refs/heads/x -X DELETE",
        ):
            with self.subTest(command=command):
                self.blocked(command)

    def test_push_without_a_branch_name_follows_the_current_branch(self) -> None:
        for current, command, expect_block in (
            ("main", "git push", True),
            ("main", "git push origin", True),
            ("main", "git push origin HEAD", True),
            ("main", "git push -u origin HEAD", True),
            ("main", "git push origin feature/x", False),
            ("feature/x", "git push", False),
            ("feature/x", "git push origin HEAD", False),
            ("production", "git push", True),
        ):
            with self.subTest(current=current, command=command):
                with mock.patch.object(self.rules, "current_branch", return_value=current):
                    if expect_block:
                        self.blocked(command)
                    else:
                        self.allowed(command)

    def test_push_on_an_unknown_branch_is_allowed(self) -> None:
        with mock.patch.object(self.rules, "current_branch", return_value=None):
            self.allowed("git push")

    def test_merge_target_ignores_the_repo_flag_value(self) -> None:
        captured = []

        def fake_run(command, **kwargs):
            captured.append(command)
            return mock.Mock(returncode=0, stdout="sifu-staging\n")

        with mock.patch.object(self.rules.subprocess, "run", fake_run):
            self.rules.pr_base_branch(["pr", "merge", "-R", "owner/repo", "12"])
            self.rules.pr_base_branch(["pr", "merge", "--repo", "owner/repo", "12"])
            self.rules.pr_base_branch(["pr", "merge", "--squash", "-R", "owner/repo", "--merge"])
        self.assertEqual(captured[0][3], "12")
        self.assertEqual(captured[1][3], "12")
        self.assertEqual(captured[2][3], "-R")  # no PR number: view falls back to the current branch's PR
        for command in captured:
            self.assertEqual(command.count("owner/repo"), 1)

    def test_no_session_id_means_no_approval(self) -> None:
        self.approve("s1")
        decision = self.guard.evaluate_tool_request("Bash", {"command": "vercel --prod"}, {})
        self.assertFalse(decision.allowed)


    # -- the note folder: only Hafiz's typed phrase may create a note ---------------------

    NOTE_WRITES = (
        "echo '{}' > ~/.agent-os/approvals/deploy-ok/s1.json",
        "cp /tmp/x /Users/someone/.agent-os/approvals/deploy-ok/s1.json",
        "tee /Users/someone/.agent-os/approvals/deploy-ok/s1.json",
        "python3 -c \"open('/Users/someone/.agent-os/approvals/deploy-ok/s1.json','w').write('{}')\"",
        "AGENT_OS_APPROVAL_DIR=/tmp/x python3 scripts/agent-checks/deploy_ok_note.py",
        "bash -c 'touch ~/.agent-os/approvals/deploy-ok/s1.json'",
    )

    def test_an_agent_cannot_create_a_note_with_a_command(self) -> None:
        for command in self.NOTE_WRITES:
            with self.subTest(command=command):
                self.blocked(command)

    def test_an_agent_cannot_create_a_note_even_when_one_exists(self) -> None:
        self.approve()
        for command in self.NOTE_WRITES:
            with self.subTest(command=command):
                self.blocked(command)

    def test_an_agent_cannot_create_a_note_with_the_file_tools(self) -> None:
        for tool, key in (("Write", "file_path"), ("Edit", "file_path"), ("MultiEdit", "file_path"), ("NotebookEdit", "notebook_path")):
            with self.subTest(tool=tool):
                decision = self.guard.evaluate_tool_request(
                    tool, {key: "/Users/someone/.agent-os/approvals/deploy-ok/s1.json", "content": "{}"}, {"session_id": "s1"}
                )
                self.assertFalse(decision.allowed)

    NOTE_SCRIPT_RUNS = (
        "echo '{\"session_id\":\"s1\",\"prompt\":\"deploy ok\"}' | python3 scripts/agent-checks/deploy_ok_note.py",
        "python3 deploy_ok_note.py < /tmp/payload.json",
        "python3 -m deploy_ok_note",
        "python3 -c 'import deploy_ok_note; deploy_ok_note.write_note(\"s1\")'",
        "cd scripts/agent-checks && python3 -c \"from deploy_ok_note import write_note; write_note('s1')\"",
        "bash -c 'python3 scripts/agent-checks/deploy_ok_note.py < /tmp/p.json'",
    )

    def test_an_agent_cannot_run_the_note_writer_itself(self) -> None:
        for command in self.NOTE_SCRIPT_RUNS:
            with self.subTest(command=command):
                self.blocked(command)

    def test_reading_or_committing_the_note_writer_is_still_fine(self) -> None:
        for command in (
            "git add scripts/agent-checks/deploy_ok_note.py",
            "cat scripts/agent-checks/deploy_ok_note.py",
            "python3 -m unittest scripts/agent-checks/test_risky_command_rules.py",
            "git commit -m 'fix deploy_ok_note phrase check'",
        ):
            with self.subTest(command=command):
                self.allowed(command)

    def patch_tool(self, header: str, tool: str = "apply_patch", wrap: str = "input"):
        body = f"*** Begin Patch\n{header}\n+x\n*** End Patch"
        return self.guard.evaluate_tool_request(tool, {wrap: body}, {"session_id": "s1"})

    def test_apply_patch_cannot_touch_a_file_in_the_note_folder(self) -> None:
        for header in (
            "*** Add File: /Users/someone/.agent-os/approvals/deploy-ok/s1.json",
            "*** Update File: /Users/someone/.agent-os/approvals/deploy-ok/s1.json",
            "*** Delete File: /Users/someone/.agent-os/approvals/deploy-ok/s1.json",
        ):
            for tool, wrap in (("apply_patch", "input"), ("functions.apply_patch", "patch"), ("apply_patch", "command")):
                with self.subTest(header=header, tool=tool):
                    self.assertFalse(self.patch_tool(header, tool, wrap).allowed)

    def test_apply_patch_that_only_mentions_the_folder_in_its_text_is_fine(self) -> None:
        self.assertTrue(self.patch_tool("*** Add File: docs/agent-playbooks/notes.md").allowed)
        decision = self.guard.evaluate_tool_request(
            "apply_patch",
            {"input": "*** Begin Patch\n*** Update File: docs/x.md\n@@\n+see ~/.agent-os/approvals/deploy-ok for the notes\n*** End Patch"},
            {"session_id": "s1"},
        )
        self.assertTrue(decision.allowed)

    def test_ordinary_files_and_the_other_agent_os_folders_stay_writable(self) -> None:
        decision = self.guard.evaluate_tool_request("Write", {"file_path": "/Users/someone/Projects/x/notes.md", "content": "hi"}, {"session_id": "s1"})
        self.assertTrue(decision.allowed)
        self.allowed("ls ~/.agent-os/usage")
        self.allowed("cat ~/.agent-os/jobs/jobs.jsonl")
        self.allowed("python3 scripts/agent-checks/job_ledger.py json")


class DeployOkNoteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.note = load("deploy_ok_note", NOTE_PATH)

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        patcher = mock.patch.dict(os.environ, {"AGENT_OS_APPROVAL_DIR": self.tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)

    def typed(self, prompt: str, session: str = "s1") -> bool:
        self.note.handle({"session_id": session, "prompt": prompt})
        return self.note.note_active(session)

    def test_the_phrase_alone_creates_the_note(self) -> None:
        self.assertTrue(self.typed("deploy ok"))

    def test_the_phrase_at_the_end_of_a_message_creates_the_note(self) -> None:
        self.assertTrue(self.typed("Fix the invoice page, proceed until prod deploy, deploy ok"))

    def test_capitals_and_a_full_stop_are_fine(self) -> None:
        self.assertTrue(self.typed("Deploy OK."))

    def test_the_phrase_in_the_middle_of_a_discussion_does_not_count(self) -> None:
        self.assertFalse(self.typed("What does deploy ok do when I forget to type it?"))

    def test_a_negated_phrase_does_not_count(self) -> None:
        self.assertFalse(self.typed("please do not say deploy ok"))
        self.assertFalse(self.typed("never deploy ok"))

    def test_the_phrase_after_a_dash_or_on_its_own_last_line_counts(self) -> None:
        self.assertTrue(self.typed("Fix the invoice page - deploy ok"))
        self.assertTrue(self.typed("Fix the invoice page.\n\ndeploy ok", session="s2"))
        self.assertTrue(self.typed("Fix the invoice page; deploy ok", session="s3"))

    def test_a_sentence_that_only_mentions_the_phrase_does_not_count(self) -> None:
        for prompt in (
            "Wait for my deploy ok",
            "Please type deploy ok when you are ready",
            "no deploy ok",
            "can't deploy ok",
            "I will say deploy ok later",
            "Do not deploy until I say deploy ok",
            "Not yet, deploy ok",
        ):
            with self.subTest(prompt=prompt):
                self.assertFalse(self.typed(prompt))

    def test_other_words_do_not_count(self) -> None:
        for prompt in ("ok", "yes proceed", "go to production", "deploy"):
            with self.subTest(prompt=prompt):
                self.assertFalse(self.typed(prompt))

    def test_a_session_id_cannot_escape_the_folder(self) -> None:
        self.note.handle({"session_id": "../../evil", "prompt": "deploy ok"})
        self.assertEqual([p.name for p in Path(self.tmp.name).rglob("*") if p.is_file()].count("evil.json"), 0)
        self.assertFalse((Path(self.tmp.name).parent / "evil.json").exists())

    def test_missing_prompt_or_session_does_nothing(self) -> None:
        self.assertIsNone(self.note.handle({}))
        self.assertIsNone(self.note.handle({"prompt": "deploy ok"}))


class ClaudePromptHookWritesNoteTest(unittest.TestCase):
    """The Claude prompt hook already wired on every install carries the deploy ok note."""

    INJECTOR = ROOT / ".claude" / "hooks" / "koda-context-injector.py"

    def run_hook(self, payload: dict, folder: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.INJECTOR)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
            env={
                "HOME": str(Path.home()),
                "PATH": str(Path(sys.executable).parent),
                "AGENT_OS_APPROVAL_DIR": folder,
                "SIFUTUTOR_SECRET_GUARD_STATE_DIR": folder,
            },
        )

    def test_typing_deploy_ok_writes_the_note_even_though_the_prompt_is_short(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            result = self.run_hook({"session_id": "sess-1", "prompt": "deploy ok"}, folder)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((Path(folder) / "sess-1.json").is_file())

    def test_an_ordinary_prompt_writes_no_note(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            result = self.run_hook({"session_id": "sess-1", "prompt": "Wait for my deploy ok before you ship"}, folder)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((Path(folder) / "sess-1.json").exists())


if __name__ == "__main__":
    unittest.main()
