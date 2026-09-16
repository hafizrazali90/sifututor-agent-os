#!/usr/bin/env python3
"""Regression tests for the shared secret-output guard."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
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
            "node -e 'console.log(process.env)'",
            "python3 -c 'import os; print(os.environ)'",
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
            "user_prompt": (
                "Open the provider dashboard and take an accessibility snapshot "
                "of the complete API key."
            )
        }
        result = subprocess.run(
            [sys.executable, str(ROOT / ".claude" / "hooks" / "koda-context-injector.py")],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
            env={"HOME": str(Path.home()), "PATH": str(Path(sys.executable).parent)},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("do not take screenshots", context.lower())
        self.assertIn("owner-only", context.lower())

    def test_codex_hook_matches_nested_exec_tools(self) -> None:
        config = (ROOT / ".codex" / "config.toml").read_text()
        self.assertIn("exec_command", config)
        self.assertIn("functions\\\\.exec", config)
        self.assertIn("secret_output_guard.py", config)


if __name__ == "__main__":
    unittest.main()
