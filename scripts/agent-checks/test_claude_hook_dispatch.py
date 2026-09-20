#!/usr/bin/env python3
"""Regression tests for umbrella-launched Claude hook resolution.

Issue 96: a Claude session launched from the umbrella workspace keeps the
umbrella `CLAUDE_PROJECT_DIR`, so `cd "$CLAUDE_PROJECT_DIR" && python3
.claude/hooks/quality-gate.py` looks for a sub-project-only hook inside the
umbrella. The missing script makes python exit 2, and a PreToolUse exit 2
cancels every Bash call.

These fixtures lock the dispatcher contract:

- the nested project/worktree gate runs, with the project as cwd
- stdin reaches the real gate byte-for-byte
- a genuine gate rejection keeps its exit code and its output
- missing infrastructure warns on stderr and exits 0 instead of blocking
- a malformed or absent payload cwd never escapes the bounded search
- the dispatcher never dispatches to itself
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import claude_hook_dispatch  # noqa: E402


WRAPPERS = {
    "quality-gate.py": ROOT / ".claude" / "hooks" / "quality-gate.py",
    "workflow-gate.py": ROOT / ".claude" / "hooks" / "workflow-gate.py",
}

RECORDING_GATE = """#!/usr/bin/env python3
import json, os, pathlib, sys

record = pathlib.Path(os.environ["FIXTURE_RECORD"])
payload = sys.stdin.buffer.read()
record.write_bytes(
    json.dumps({{"cwd": os.getcwd(), "stdin": payload.decode("utf-8", "replace")}}).encode()
)
sys.stdout.write({stdout!r})
sys.stderr.write({stderr!r})
sys.exit({code})
"""


def write_gate(path: Path, *, code: int = 0, stdout: str = "", stderr: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(RECORDING_GATE.format(code=code, stdout=stdout, stderr=stderr))
    path.chmod(0o755)


def payload_bytes(cwd, *, command: str = "git status --short") -> bytes:
    body = {
        "session_id": "fixture-session",
        "transcript_path": "/dev/null",
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }
    if cwd is not None:
        body["cwd"] = cwd
    return json.dumps(body).encode()


class DispatchFixture(unittest.TestCase):
    """Umbrella wrapper invoked exactly the way the tracked hook command does."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()

        # Umbrella checkout: the real wrappers plus the shared dispatcher they
        # import, and no project gates of its own.
        self.umbrella = self.base / "umbrella"
        (self.umbrella / ".claude" / "hooks").mkdir(parents=True)
        (self.umbrella / ".git").mkdir()
        shared = self.umbrella / "scripts" / "agent-checks"
        shared.mkdir(parents=True)
        (shared / "claude_hook_dispatch.py").write_text(
            (HERE / "claude_hook_dispatch.py").read_text()
        )
        for name, source in WRAPPERS.items():
            target = self.umbrella / ".claude" / "hooks" / name
            target.write_text(source.read_text())
            target.chmod(0o755)

        # Sub-project worktree living outside the umbrella checkout.
        self.worktree = self.base / "worktrees" / "ripple-feature"
        self.nested = self.worktree / "src" / "app"
        self.nested.mkdir(parents=True)
        (self.worktree / ".git").write_text("gitdir: /elsewhere\n")

        self.record = self.base / "record.json"

    def run_wrapper(
        self,
        hook_name: str,
        payload: bytes,
        *,
        env_extra: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        env = dict(os.environ)
        env["FIXTURE_RECORD"] = str(self.record)
        env.pop("SIFUTUTOR_AGENT_OS_HOOK_DISPATCH", None)
        if env_extra:
            env.update(env_extra)
        # Mirrors the tracked command: cd "$CLAUDE_PROJECT_DIR" && python3 .claude/hooks/<name>
        return subprocess.run(
            [sys.executable, str(Path(".claude") / "hooks" / hook_name)],
            cwd=self.umbrella,
            input=payload,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            timeout=60,
            check=False,
        )

    def recorded(self) -> dict:
        return json.loads(self.record.read_text())

    # --- core issue-96 case -------------------------------------------------

    def test_umbrella_launch_dispatches_to_nested_worktree_gate(self) -> None:
        write_gate(self.worktree / ".claude" / "hooks" / "quality-gate.py")
        payload = payload_bytes(str(self.nested))

        result = self.run_wrapper("quality-gate.py", payload)

        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertTrue(self.record.is_file(), "nested worktree gate never ran")
        self.assertEqual(Path(self.recorded()["cwd"]).resolve(), self.worktree)

    def test_exact_stdin_bytes_reach_the_real_gate(self) -> None:
        write_gate(self.worktree / ".claude" / "hooks" / "quality-gate.py")
        payload = payload_bytes(str(self.nested), command='echo "quoted  spaces"')

        self.run_wrapper("quality-gate.py", payload)

        self.assertEqual(self.recorded()["stdin"].encode(), payload)

    def test_workflow_gate_wrapper_uses_the_same_dispatcher(self) -> None:
        write_gate(self.worktree / ".claude" / "hooks" / "workflow-gate.py", code=2)
        payload = payload_bytes(str(self.worktree))

        result = self.run_wrapper("workflow-gate.py", payload)

        self.assertEqual(result.returncode, 2)
        self.assertEqual(Path(self.recorded()["cwd"]).resolve(), self.worktree)

    # --- a real rejection must survive --------------------------------------

    def test_real_gate_rejection_keeps_exit_code_and_output(self) -> None:
        write_gate(
            self.worktree / ".claude" / "hooks" / "quality-gate.py",
            code=2,
            stdout="GATE-STDOUT-MARKER",
            stderr="GATE-STDERR-MARKER",
        )
        payload = payload_bytes(str(self.nested))

        result = self.run_wrapper("quality-gate.py", payload)

        self.assertEqual(result.returncode, 2, "a genuine gate rejection was swallowed")
        self.assertIn(b"GATE-STDOUT-MARKER", result.stdout)
        self.assertIn(b"GATE-STDERR-MARKER", result.stderr)

    def test_non_blocking_gate_error_code_is_preserved(self) -> None:
        write_gate(self.worktree / ".claude" / "hooks" / "quality-gate.py", code=1)

        result = self.run_wrapper("quality-gate.py", payload_bytes(str(self.nested)))

        self.assertEqual(result.returncode, 1)

    def test_gate_timeout_does_not_become_success(self) -> None:
        gate = self.worktree / ".claude" / "hooks" / "quality-gate.py"
        gate.parent.mkdir(parents=True, exist_ok=True)
        gate.write_text("import time\ntime.sleep(30)\n")

        result = self.run_wrapper(
            "quality-gate.py",
            payload_bytes(str(self.nested)),
            env_extra={"SIFUTUTOR_AGENT_OS_HOOK_TIMEOUT": "1"},
        )

        self.assertNotEqual(result.returncode, 0, "timeout was reported as a pass")

    # --- missing infrastructure must not block ------------------------------

    def test_missing_project_gate_warns_and_exits_zero(self) -> None:
        result = self.run_wrapper("quality-gate.py", payload_bytes(str(self.nested)))

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b"")
        message = result.stderr.decode()
        self.assertIn("quality-gate.py", message)

    def test_warning_is_metadata_only(self) -> None:
        result = self.run_wrapper("quality-gate.py", payload_bytes(str(self.nested)))

        message = result.stderr.decode()
        self.assertNotIn(str(self.base), message)
        self.assertNotIn("/", message, "warning leaked a filesystem path")
        self.assertNotIn("git status", message, "warning leaked command content")

    # --- bounded, non-recursive search --------------------------------------

    def test_absent_cwd_never_reaches_an_unrelated_gate(self) -> None:
        write_gate(self.worktree / ".claude" / "hooks" / "quality-gate.py")

        result = self.run_wrapper("quality-gate.py", payload_bytes(None))

        self.assertEqual(result.returncode, 0)
        self.assertFalse(self.record.is_file(), "unrelated gate ran for a payload with no cwd")

    def test_malformed_cwd_values_are_rejected_safely(self) -> None:
        planted = self.base / ".claude" / "hooks" / "quality-gate.py"
        write_gate(planted)
        a_file = self.base / "not-a-directory"
        a_file.write_text("x")

        for bad in ["", "../../..", "relative/path", str(a_file), str(self.base / "missing"), 17]:
            with self.subTest(cwd=bad):
                if self.record.exists():
                    self.record.unlink()
                result = self.run_wrapper("quality-gate.py", payload_bytes(bad))
                self.assertEqual(result.returncode, 0)
                self.assertFalse(
                    self.record.is_file(),
                    f"search escaped the boundary for cwd={bad!r}",
                )

    def test_malformed_payload_is_not_a_block(self) -> None:
        for raw in [b"", b"not json", b"[]", b"null"]:
            with self.subTest(raw=raw):
                result = self.run_wrapper("quality-gate.py", raw)
                self.assertEqual(result.returncode, 0)

    def test_search_stops_at_the_project_repo_root(self) -> None:
        # A gate one level above the worktree root must not be borrowed.
        write_gate(self.base / "worktrees" / ".claude" / "hooks" / "quality-gate.py")

        result = self.run_wrapper("quality-gate.py", payload_bytes(str(self.nested)))

        self.assertEqual(result.returncode, 0)
        self.assertFalse(self.record.is_file(), "search crossed the project repo boundary")

    def test_dispatcher_does_not_dispatch_to_itself(self) -> None:
        # cwd is the umbrella itself: the only candidate is this very wrapper.
        result = self.run_wrapper("quality-gate.py", payload_bytes(str(self.umbrella)))

        self.assertEqual(result.returncode, 0)
        self.assertFalse(self.record.is_file())

    def test_dispatcher_copy_in_a_project_is_not_dispatched_to(self) -> None:
        copy = self.worktree / ".claude" / "hooks" / "quality-gate.py"
        copy.parent.mkdir(parents=True, exist_ok=True)
        copy.write_text((self.umbrella / ".claude" / "hooks" / "quality-gate.py").read_text())

        result = self.run_wrapper("quality-gate.py", payload_bytes(str(self.nested)))

        self.assertEqual(result.returncode, 0)
        self.assertNotIn(b"RecursionError", result.stderr)

    def test_reentry_guard_stops_a_dispatch_loop(self) -> None:
        write_gate(self.worktree / ".claude" / "hooks" / "quality-gate.py")

        result = self.run_wrapper(
            "quality-gate.py",
            payload_bytes(str(self.nested)),
            env_extra={"SIFUTUTOR_AGENT_OS_HOOK_DISPATCH": "quality-gate.py"},
        )

        self.assertEqual(result.returncode, 0)
        self.assertFalse(self.record.is_file())

    # --- direct sub-project sessions keep working ---------------------------

    def test_direct_subproject_launch_still_runs_the_real_gate(self) -> None:
        """Wrapper invoked with the project itself as cwd and payload cwd."""
        write_gate(self.worktree / ".claude" / "hooks" / "workflow-gate.py", code=2)
        wrapper = self.worktree / ".claude" / "hooks" / "quality-gate.py"
        wrapper.write_text((self.umbrella / ".claude" / "hooks" / "quality-gate.py").read_text())
        write_gate(self.worktree / ".claude" / "hooks" / "real-gate.py")

        env = dict(os.environ)
        env["FIXTURE_RECORD"] = str(self.record)
        result = subprocess.run(
            [sys.executable, ".claude/hooks/workflow-gate.py"],
            cwd=self.umbrella,
            input=payload_bytes(str(self.worktree)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            timeout=60,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertEqual(Path(self.recorded()["cwd"]).resolve(), self.worktree)


class ResolutionUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()

    def test_find_project_hook_returns_the_project_root(self) -> None:
        project = self.base / "project"
        (project / ".claude" / "hooks").mkdir(parents=True)
        (project / ".git").mkdir()
        gate = project / ".claude" / "hooks" / "quality-gate.py"
        gate.write_text("print('x')\n")
        nested = project / "a" / "b"
        nested.mkdir(parents=True)

        found = claude_hook_dispatch.find_project_hook("quality-gate.py", nested)

        self.assertEqual(found.project_dir, project)
        self.assertEqual(found.hook_path, gate)

    def test_depth_is_bounded(self) -> None:
        deep = self.base.joinpath(*[f"level{i}" for i in range(40)])
        deep.mkdir(parents=True)
        (self.base / ".claude" / "hooks").mkdir(parents=True)
        (self.base / ".claude" / "hooks" / "quality-gate.py").write_text("print('x')\n")

        found = claude_hook_dispatch.find_project_hook("quality-gate.py", deep)

        self.assertIsNone(found.hook_path)

    def test_unexpected_dispatcher_failure_does_not_become_success(self) -> None:
        original = claude_hook_dispatch.dispatch

        def crash(*_args, **_kwargs):
            raise RuntimeError("synthetic dispatcher failure")

        claude_hook_dispatch.dispatch = crash
        try:
            result = claude_hook_dispatch.wrapper_main("quality-gate.py", __file__)
        finally:
            claude_hook_dispatch.dispatch = original

        self.assertNotEqual(result, 0)

    def test_shell_hook_runs_with_arguments_and_exact_stdin(self) -> None:
        project = self.base / "project"
        nested = project / "src"
        nested.mkdir(parents=True)
        (project / ".git").mkdir()
        gate = project / ".claude" / "hooks" / "run-shared-hook.sh"
        gate.parent.mkdir(parents=True)
        record = self.base / "shell-record"
        gate.write_text(
            '#!/usr/bin/env bash\n'
            'printf "%s" "$1" > "$FIXTURE_RECORD.arg"\n'
            'cat > "$FIXTURE_RECORD"\n'
            'exit 2\n'
        )
        payload = payload_bytes(str(nested), command='echo "shell fixture"') + b"\n"
        env = dict(os.environ)
        env["FIXTURE_RECORD"] = str(record)

        result = claude_hook_dispatch.dispatch(
            "run-shared-hook.sh",
            stdin_bytes=payload,
            env=env,
            hook_args=["validate-branch-name.py"],
        )

        self.assertEqual(result, 2)
        self.assertEqual(Path(f"{record}.arg").read_text(), "validate-branch-name.py")
        self.assertEqual(record.read_bytes(), payload)


class ConfigurationAuditTests(unittest.TestCase):
    """Readiness validation for hook commands that cannot resolve at launch."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.umbrella = self.base / "umbrella"
        (self.umbrella / ".claude" / "hooks").mkdir(parents=True)
        self.project = self.umbrella / "ripple-suite"
        (self.project / ".claude" / "hooks").mkdir(parents=True)
        for name in ("quality-gate.py", "workflow-gate.py"):
            (self.project / ".claude" / "hooks" / name).write_text("print('x')\n")
        (self.project / ".claude" / "settings.json").write_text(
            json.dumps(
                {
                    "hooks": {
                        "PreToolUse": [
                            {
                                "matcher": "Bash",
                                "hooks": [
                                    {
                                        "type": "command",
                                        "command": 'cd "$CLAUDE_PROJECT_DIR" && python3 .claude/hooks/quality-gate.py',
                                    },
                                    {
                                        "type": "command",
                                        "command": 'cd "$CLAUDE_PROJECT_DIR" && python3 .claude/hooks/workflow-gate.py',
                                    },
                                ],
                            }
                        ]
                    }
                }
            )
        )

    def test_planted_missing_umbrella_hook_is_caught(self) -> None:
        findings = claude_hook_dispatch.audit_project_hook_configuration(
            self.umbrella, self.project
        )

        unresolved = [f for f in findings if not f.ok]
        self.assertEqual(
            sorted(f.hook_script for f in unresolved),
            [".claude/hooks/quality-gate.py", ".claude/hooks/workflow-gate.py"],
        )

    def test_fixed_configuration_is_accepted(self) -> None:
        for name in ("quality-gate.py", "workflow-gate.py"):
            (self.umbrella / ".claude" / "hooks" / name).write_text("print('x')\n")

        findings = claude_hook_dispatch.audit_project_hook_configuration(
            self.umbrella, self.project
        )

        self.assertTrue(findings, "audit produced no findings to judge")
        self.assertTrue(all(f.ok for f in findings), [f.hook_script for f in findings if not f.ok])

    def test_absolute_path_commands_are_not_flagged(self) -> None:
        (self.project / ".claude" / "settings.json").write_text(
            json.dumps(
                {
                    "hooks": {
                        "PreToolUse": [
                            {
                                "hooks": [
                                    {
                                        "type": "command",
                                        "command": f"python3 {self.project}/.claude/hooks/quality-gate.py",
                                    }
                                ]
                            }
                        ]
                    }
                }
            )
        )

        findings = claude_hook_dispatch.audit_project_hook_configuration(
            self.umbrella, self.project
        )

        self.assertTrue(all(f.ok for f in findings), [f.hook_script for f in findings if not f.ok])

    def test_hook_script_missing_from_the_project_itself_is_caught(self) -> None:
        (self.project / ".claude" / "hooks" / "quality-gate.py").unlink()
        (self.umbrella / ".claude" / "hooks" / "quality-gate.py").write_text("print('x')\n")
        (self.umbrella / ".claude" / "hooks" / "workflow-gate.py").write_text("print('x')\n")

        findings = claude_hook_dispatch.audit_project_hook_configuration(
            self.umbrella, self.project
        )

        broken = [f for f in findings if not f.ok]
        self.assertEqual([f.hook_script for f in broken], [".claude/hooks/quality-gate.py"])

    def _settings(self, event: str, script: str) -> None:
        (self.project / ".claude" / "settings.json").write_text(
            json.dumps(
                {
                    "hooks": {
                        event: [
                            {
                                "hooks": [
                                    {
                                        "type": "command",
                                        "command": f'cd "$CLAUDE_PROJECT_DIR" && python3 .claude/hooks/{script}',
                                    }
                                ]
                            }
                        ]
                    }
                }
            )
        )

    def test_pretooluse_dispatcher_gap_blocks_readiness(self) -> None:
        self._settings("PreToolUse", "quality-gate.py")

        findings = claude_hook_dispatch.audit_project_hook_configuration(
            self.umbrella, self.project
        )

        self.assertEqual(len(findings), 1)
        self.assertTrue(findings[0].blocks_readiness)

    def test_unknown_pretooluse_name_also_blocks_readiness(self) -> None:
        (self.project / ".claude" / "hooks" / "new-safety-gate.sh").write_text("exit 0\n")
        self._settings("PreToolUse", "new-safety-gate.sh")

        findings = claude_hook_dispatch.audit_project_hook_configuration(
            self.umbrella, self.project
        )

        self.assertEqual(len(findings), 1)
        self.assertTrue(findings[0].blocks_readiness)

    def test_powershell_configuration_is_resolved_by_umbrella_wrapper(self) -> None:
        (self.project / ".claude" / "hooks" / "validate-branch.ps1").write_text("exit 0\n")
        self._settings("PreToolUse", "validate-branch.ps1")
        (self.umbrella / ".claude" / "hooks" / "validate-branch.ps1").write_text("exit 0\n")

        findings = claude_hook_dispatch.audit_project_hook_configuration(
            self.umbrella, self.project
        )

        self.assertEqual(len(findings), 1)
        self.assertTrue(findings[0].ok)

    def test_session_start_gap_is_reported_but_not_blocking(self) -> None:
        (self.project / ".claude" / "hooks" / "session-start.py").write_text("print('x')\n")
        self._settings("SessionStart", "session-start.py")

        findings = claude_hook_dispatch.audit_project_hook_configuration(
            self.umbrella, self.project
        )

        self.assertEqual(len(findings), 1)
        self.assertFalse(findings[0].ok, "the gap must still be reported")
        self.assertFalse(findings[0].blocks_readiness, "a SessionStart gap cancels no tool call")

    def test_script_missing_from_its_own_project_always_blocks(self) -> None:
        self._settings("SessionStart", "never-existed.py")

        findings = claude_hook_dispatch.audit_project_hook_configuration(
            self.umbrella, self.project
        )

        self.assertTrue(findings[0].blocks_readiness)

    def test_archived_project_checkouts_are_skipped(self) -> None:
        archived = self.umbrella / "team-inbox.archived-2026-08-26"
        (archived / ".claude" / "hooks").mkdir(parents=True)
        (archived / ".claude" / "settings.json").write_text(
            json.dumps(
                {
                    "hooks": {
                        "PreToolUse": [
                            {"hooks": [{"type": "command", "command": "python3 .claude/hooks/quality-gate.py"}]}
                        ]
                    }
                }
            )
        )

        findings = claude_hook_dispatch.audit_workspace_hook_configuration(self.umbrella)

        self.assertNotIn("team-inbox.archived-2026-08-26", {f.project for f in findings})

    def test_tracked_umbrella_configuration_has_no_blocking_gap(self) -> None:
        """This checkout must never ship a PreToolUse gate that cannot resolve."""
        findings = claude_hook_dispatch.audit_workspace_hook_configuration(ROOT)
        blocking = [f for f in findings if f.blocks_readiness]
        self.assertFalse(blocking, [f.detail for f in blocking])


if __name__ == "__main__":
    unittest.main()
