#!/usr/bin/env python3
"""Regression tests for the shared secret-output guard."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]
GUARD_PATH = ROOT / "scripts" / "agent-checks" / "secret_output_guard.py"


def load_guard():
    spec = importlib.util.spec_from_file_location("secret_output_guard", GUARD_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load secret output guard")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SecretOutputGuardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.guard = load_guard()

    def assert_blocked(self, command: str) -> None:
        decision = self.guard.evaluate_command(command)
        self.assertFalse(decision.allowed, command)
        self.assertTrue(decision.reason)

    def assert_allowed(self, command: str) -> None:
        decision = self.guard.evaluate_command(command)
        self.assertTrue(decision.allowed, f"{command}: {decision.reason}")

    def test_blocks_raw_process_environment_commands(self) -> None:
        for command in (
            "pm2 jlist",
            "ssh production 'PM2_HOME=/home/deploy/.pm2 pm2 prettylist'",
            "pm2 env 12 | grep DATABASE_URL",
            "pm2 show ripple-suite-prod",
            "printenv",
            "ssh production 'printenv'",
            "env | sort",
            "docker exec ripple-suite-prod env",
            "cat /proc/1234/environ | tr '\\0' '\\n'",
            "systemctl show ripple --property=Environment",
            "systemctl show ripple",
            "ps aux",
            "ps -ef",
            "pgrep -af node",
            "history",
            "ssh production 'history'",
            "node -e 'console.log(process.env)'",
            "node -p 'process.env'",
            "python3 -c 'import os; print(os.environ)'",
            "php -r 'var_dump($_ENV);'",
            "launchctl print system/com.example.app",
        ):
            with self.subTest(command=command):
                self.assert_blocked(command)

    def test_blocks_raw_container_and_secret_store_commands(self) -> None:
        for command in (
            "docker inspect ripple-suite-prod",
            "docker inspect --format '{{json .Config.Env}}' ripple-suite-prod",
            "docker compose config",
            "kubectl get secret ripple -o yaml",
            "aws secretsmanager get-secret-value --secret-id ripple",
            "gcloud secrets versions access latest --secret=ripple",
            "vault kv get secret/ripple",
            "vercel env pull .env.local",
            "security find-generic-password -s ripple -w",
            "op read op://Production/Ripple/password",
            "pass show production/ripple",
        ):
            with self.subTest(command=command):
                self.assert_blocked(command)

    def test_blocks_direct_secret_file_and_shell_expansion_output(self) -> None:
        for command in (
            "cat ~/.config/sifututor/agent-access/ripple-prod.conf",
            "jq . ~/.config/sifututor/agent-access/ripple-prod.conf",
            "python3 -c 'print(open(\"/tmp/credentials.json\").read())'",
            "echo $ANTHROPIC_API_KEY",
            "printf '%s\\n' \"${DATABASE_PASSWORD}\"",
            "set -x; source ~/.config/sifututor/agent-access/ripple-prod.conf",
            "curl -v -H 'Authorization: Bearer '$API_TOKEN https://example.test",
        ):
            with self.subTest(command=command):
                self.assert_blocked(command)

    def test_allows_safe_operational_commands(self) -> None:
        for command in (
            "scripts/agent-access/check-ripple-prod.sh",
            "PM2_HOME=/home/deploy/.pm2 pm2 list --no-color",
            "systemctl show ripple --property=ActiveState",
            "ps -o pid,user,comm -p 1234",
            "docker inspect --format '{{.State.Health.Status}}' finch-prod",
            "env NODE_ENV=test npm test",
            "source ~/.config/sifututor/agent-access/ripple-prod.conf; curl -fsS https://example.test/health",
            "rg -n 'secret handling' docs/agent-playbooks",
            "rg -n 'pm2 jlist' docs/agent-playbooks",
        ):
            with self.subTest(command=command):
                self.assert_allowed(command)

    def test_allows_benign_prose_and_github_body_text(self) -> None:
        for command in (
            "rg -n 'Shell history output' scripts/agent-checks",
            "gh issue create --body 'Read from process.env with a safe default; do not print it.'",
            (
                "gh pr create --body \"$(cat <<'EOF'\n"
                "This change reads from os.environ with a safe default.\n"
                "It does not print configuration or shell history.\n"
                "EOF\n)\""
            ),
            (
                "gh pr create --body \"$(cat <<'EOF'\n"
                "```js\nconst mode = process.env.NODE_ENV || 'test';\n```\n"
                "EOF\n)\""
            ),
        ):
            with self.subTest(command=command):
                self.assert_allowed(command)

                decision = self.guard.evaluate_tool_request(
                    "functions.exec",
                    {
                        "input": (
                            "await tools.exec_command({cmd: "
                            f"{json.dumps(command)}"
                            "});"
                        )
                    },
                    {},
                )
                self.assertTrue(decision.allowed, decision.reason)

    def test_recognizes_provider_secret_reveal_prompts(self) -> None:
        self.assertTrue(
            self.guard.prompt_requests_secret_reveal(
                "Open the DeepInfra API key page and take an accessibility snapshot so we can copy the key"
            )
        )
        self.assertTrue(
            self.guard.prompt_requests_secret_reveal(
                "Screenshot the provider page that shows the full token"
            )
        )
        self.assertTrue(
            self.guard.prompt_requests_secret_reveal(
                "Capture the complete token from the provider page"
            )
        )
        self.assertTrue(
            self.guard.prompt_requests_secret_reveal(
                "Copy the full password"
            )
        )
        self.assertTrue(
            self.guard.prompt_requests_secret_reveal(
                "Screenshot the provider page with the complete token even though the field says hidden"
            )
        )
        self.assertFalse(
            self.guard.prompt_requests_secret_reveal(
                "Create a new API key and let me enter it through a hidden prompt"
            )
        )
        self.assertFalse(
            self.guard.prompt_requests_secret_reveal(
                "Inspect the provider dashboard to verify the API key is masked"
            )
        )
        self.assertFalse(
            self.guard.prompt_requests_secret_reveal(
                "Inspect the provider page to verify the API key is not visible"
            )
        )

    def test_secret_visual_boundary_stores_metadata_only(self) -> None:
        payload = {"session_id": "private-session-name", "cwd": str(ROOT)}
        prompt = "Screenshot the provider page showing the complete API key"
        with tempfile.TemporaryDirectory() as state_dir:
            self.assertTrue(
                self.guard.sync_secret_visual_boundary(
                    payload, prompt, state_dir=Path(state_dir), now=1000
                )
            )
            markers = list(Path(state_dir).iterdir())
            self.assertEqual(len(markers), 1)
            marker = markers[0]
            self.assertNotIn("private-session-name", marker.name)
            contents = marker.read_text()
            self.assertNotIn(prompt, contents)
            self.assertNotIn("API key", contents)
            self.assertTrue(
                self.guard.secret_visual_boundary_active(
                    payload, state_dir=Path(state_dir), now=1001
                )
            )

    def test_active_boundary_blocks_visual_capture_without_freezing_work(self) -> None:
        payload = {"session_id": "visual-boundary", "cwd": str(ROOT)}
        with tempfile.TemporaryDirectory() as state_dir:
            state_path = Path(state_dir)
            self.guard.mark_secret_visual_boundary(payload, state_dir=state_path, now=1000)
            self.assertFalse(
                self.guard.evaluate_tool_request(
                    "mcp__browser__take_screenshot",
                    {"ref_id": "opaque-page-reference"},
                    payload,
                    state_dir=state_path,
                    now=1001,
                ).allowed
            )
            self.assertFalse(
                self.guard.evaluate_tool_request(
                    "functions.exec",
                    {"input": "await tools.web__run({screenshot: [{ref_id: 'opaque'}]});"},
                    payload,
                    state_dir=state_path,
                    now=1001,
                ).allowed
            )
            self.assertFalse(
                self.guard.evaluate_tool_request(
                    "functions.exec",
                    {
                        "input": (
                            "const request = {\"screenshot\": [{ref_id: 'opaque'}]}; "
                            "await tools.web__run(request);"
                        )
                    },
                    payload,
                    state_dir=state_path,
                    now=1001,
                ).allowed
            )
            self.assertFalse(
                self.guard.evaluate_tool_request(
                    "exec_command",
                    {"cmd": "screencapture /tmp/provider-page.png"},
                    payload,
                    state_dir=state_path,
                    now=1001,
                ).allowed
            )
            self.assertTrue(
                self.guard.evaluate_tool_request(
                    "functions.exec",
                    {"input": "await tools.web__run({open: [{ref_id: 'opaque'}]});"},
                    payload,
                    state_dir=state_path,
                    now=1001,
                ).allowed
            )
            self.assertTrue(
                self.guard.evaluate_tool_request(
                    "exec_command",
                    {"cmd": "git status --short"},
                    payload,
                    state_dir=state_path,
                    now=1001,
                ).allowed
            )

    def test_visual_capture_is_allowed_outside_secret_boundary(self) -> None:
        payload = {"session_id": "ordinary-visual-review", "cwd": str(ROOT)}
        with tempfile.TemporaryDirectory() as state_dir:
            self.assertTrue(
                self.guard.evaluate_tool_request(
                    "mcp__browser__take_screenshot",
                    {"ref_id": "ordinary-page"},
                    payload,
                    state_dir=Path(state_dir),
                    now=1000,
                ).allowed
            )

    def test_cli_denies_visual_tool_during_active_boundary(self) -> None:
        payload = {
            "hook_event_name": "PreToolUse",
            "tool_name": "mcp__browser__take_screenshot",
            "tool_input": {"ref_id": "opaque-page-reference"},
            "session_id": "cli-visual-boundary",
            "cwd": str(ROOT),
        }
        with tempfile.TemporaryDirectory() as state_dir:
            self.guard.mark_secret_visual_boundary(
                payload, state_dir=Path(state_dir)
            )
            result = subprocess.run(
                [sys.executable, str(GUARD_PATH)],
                input=json.dumps(payload),
                text=True,
                capture_output=True,
                check=False,
                env={
                    "HOME": str(Path.home()),
                    "PATH": str(Path(sys.executable).parent),
                    "SIFUTUTOR_SECRET_GUARD_STATE_DIR": state_dir,
                },
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            response = json.loads(result.stdout)
            reason = response["hookSpecificOutput"]["permissionDecisionReason"]
            self.assertEqual(
                response["hookSpecificOutput"]["permissionDecision"], "deny"
            )
            self.assertNotIn("opaque-page-reference", reason)

    def test_boundary_clears_explicitly_and_does_not_expire_unsafe(self) -> None:
        payload = {"session_id": "reset-boundary", "cwd": str(ROOT)}
        with tempfile.TemporaryDirectory() as state_dir:
            state_path = Path(state_dir)
            self.guard.mark_secret_visual_boundary(payload, state_dir=state_path, now=1000)
            self.assertFalse(
                self.guard.sync_secret_visual_boundary(
                    payload,
                    "The credential page is closed and the key is hidden; clear the visual guard",
                    state_dir=state_path,
                    now=1001,
                )
            )
            self.assertFalse(
                self.guard.secret_visual_boundary_active(
                    payload, state_dir=state_path, now=1002
                )
            )
            self.guard.mark_secret_visual_boundary(payload, state_dir=state_path, now=2000)
            self.assertTrue(
                self.guard.sync_secret_visual_boundary(
                    payload,
                    "Do not clear the visual guard because the API key is still visible",
                    state_dir=state_path,
                    now=2001,
                )
            )
            self.assertTrue(
                self.guard.secret_visual_boundary_active(
                    payload,
                    state_dir=state_path,
                    now=2000 + 365 * 24 * 60 * 60,
                )
            )

    def test_cli_blocks_functions_exec_payload_before_execution(self) -> None:
        payload = {
            "hook_event_name": "PreToolUse",
            "tool_name": "functions.exec",
            "tool_input": {
                "input": "await tools.exec_command({cmd: \"ssh production 'pm2 jlist'\"});"
            },
        }
        result = subprocess.run(
            [sys.executable, str(GUARD_PATH)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        response = json.loads(result.stdout)
        hook = response["hookSpecificOutput"]
        self.assertEqual(hook["permissionDecision"], "deny")
        self.assertNotIn("pm2 jlist", hook["permissionDecisionReason"])

    def test_cli_scans_entire_mixed_functions_exec_payload(self) -> None:
        payload = {
            "hook_event_name": "PreToolUse",
            "tool_name": "functions.exec",
            "tool_input": {
                "input": (
                    "const unsafe = `pm2 jlist`; "
                    "await tools.exec_command({cmd: \"git status --short\"}); "
                    "await tools.exec_command({cmd: unsafe});"
                )
            },
        }
        result = subprocess.run(
            [sys.executable, str(GUARD_PATH)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        response = json.loads(result.stdout)
        self.assertEqual(
            response["hookSpecificOutput"]["permissionDecision"], "deny"
        )

    def test_cli_ignores_apply_patch_documentation_text(self) -> None:
        payload = {
            "hook_event_name": "PreToolUse",
            "tool_name": "functions.exec",
            "tool_input": {
                "input": (
                    "const patch = \"Update docs to say pm2 jlist is blocked\"; "
                    "text(await tools.apply_patch(patch));"
                )
            },
        }
        result = subprocess.run(
            [sys.executable, str(GUARD_PATH)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_failure_loggers_never_persist_command_or_error_content(self) -> None:
        secret = "sensitive-value-" + "Z" * 32
        payloads = [
            (
                ROOT / "scripts" / "agent-checks" / "codex-post-tool-use.py",
                {
                    "tool_input": {"command": f"curl -H 'Authorization: Bearer {secret}' https://example.test"},
                    "tool_response": {"exit_code": 1, "error": secret},
                },
                ".codex-friction.log",
            ),
            (
                ROOT / ".claude" / "hooks" / "friction-logger.py",
                {
                    "tool_name": "Bash",
                    "tool_input": {"command": f"curl -H 'Authorization: Bearer {secret}' https://example.test"},
                    "tool_response": {"exit_code": 1, "stderr": secret},
                    "session_id": "test-session",
                    "cwd": str(ROOT),
                },
                ".claude-friction.log",
            ),
        ]
        for script, payload, log_name in payloads:
            with self.subTest(script=script.name), tempfile.TemporaryDirectory() as home:
                result = subprocess.run(
                    [sys.executable, str(script)],
                    input=json.dumps(payload),
                    text=True,
                    capture_output=True,
                    check=False,
                    env={"HOME": home, "PATH": str(Path(sys.executable).parent)},
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                log = (Path(home) / log_name).read_text()
                self.assertNotIn(secret, log)
                self.assertIn("output=redacted", log)

    def test_claude_prompt_bridge_warns_before_provider_visual_capture(self) -> None:
        payload = {
            "session_id": "claude-secret-visual-fixture",
            "cwd": str(ROOT),
            "user_prompt": (
                "Open the provider dashboard and take an accessibility snapshot "
                "of the complete API key."
            )
        }
        with tempfile.TemporaryDirectory() as state_dir:
            result = subprocess.run(
                [sys.executable, str(ROOT / ".claude" / "hooks" / "koda-context-injector.py")],
                input=json.dumps(payload),
                text=True,
                capture_output=True,
                check=False,
                env={
                    "HOME": str(Path.home()),
                    "PATH": str(Path(sys.executable).parent),
                    "SIFUTUTOR_SECRET_GUARD_STATE_DIR": state_dir,
                },
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("do not take screenshots", context.lower())
            self.assertIn("owner-only", context.lower())
            self.assertEqual(len(list(Path(state_dir).iterdir())), 1)

    def test_codex_guard_runs_for_all_tools(self) -> None:
        config = tomllib.loads((ROOT / ".codex" / "config.toml").read_text())
        groups = config["hooks"]["PreToolUse"]
        self.assertEqual(len(groups), 1)
        self.assertTrue(
            any(
                group.get("matcher") == ".*"
                and any(
                    (
                        "secret_output_guard.py" in hook.get("command", "")
                        or "codex-pre-tool-dispatch.py" in hook.get("command", "")
                    )
                    for hook in group.get("hooks", [])
                )
                for group in groups
            )
        )

    def test_installer_requires_wildcard_claude_guard(self) -> None:
        installer = (ROOT / "scripts" / "agent-checks" / "agent-os-install.sh").read_text()
        self.assertIn('group.get("matcher") == ".*"', installer)
        self.assertIn('\"matcher\": \".*\"', installer)
        self.assertIn(
            '"secret_output_guard.py" in str(hook.get("command") or "")',
            installer,
        )


if __name__ == "__main__":
    unittest.main()
