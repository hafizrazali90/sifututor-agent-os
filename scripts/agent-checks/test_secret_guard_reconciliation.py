"""Synthetic safety regression journeys; never execute inspected commands."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

GUARD_PATH = Path(__file__).with_name("secret_output_guard.py")


def load_guard():
    spec = importlib.util.spec_from_file_location("reconciliation_guard", GUARD_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class InspectFormatSafetyTest(unittest.TestCase):
    def test_broad_inspect_format_is_blocked(self):
        guard = load_guard()
        for template in ("{{json .}}", "{{json .Config}}", "{{.Config}}", "{{.Config.Env}}"):
            with self.subTest(template=template):
                self.assertFalse(guard.evaluate_command(
                    "docker inspect --format '" + template + "' sample"
                ).allowed)

    def test_dynamic_and_duplicate_formats_are_blocked(self):
        guard = load_guard()
        commands = (
            "docker inspect --format '$FORMAT' sample",
            "docker inspect --format '{{.State.Status}} {{json .}}' sample",
            "docker inspect --format '{{.State.Status}}' -f'{{json .}}' sample",
            "docker inspect --format '{{.State.Status}}' --format='{{json .}}' sample",
            "docker inspect --format '{{.State.Status}}' sample; docker inspect sample",
            "docker inspect --format '{{.State.Health.Log}}' sample",
            "docker inspect --format '{{.State.Error}}' sample",
            "docker inspect --format '{{.State}}' sample",
            "docker inspect --format '{{index .Config \"Env\"}}' sample",
        )
        for command in commands:
            with self.subTest(command=command):
                self.assertFalse(guard.evaluate_command(command).allowed)

    def test_format_cannot_be_borrowed_from_comment_or_next_command(self):
        guard = load_guard()
        for command in (
            "docker inspect sample # --format {{.State.Status}}",
            "docker inspect sample\necho --format {{.State.Status}}",
            "docker inspect sample\recho --format {{.State.Status}}",
            "rg status docs\ndocker inspect sample",
            "docker inspect sample \"decoy --format '{{.State.Status}}' x\"",
            "docker inspect sample > --format '{{.State.Status}}'",
            "docker inspect sample 2> --format '{{.State.Status}}'",
            "docker inspect sample -- --format '{{.State.Status}}'",
        ):
            with self.subTest(command=command):
                self.assertFalse(guard.evaluate_command(command).allowed)

    def test_unsupported_docker_option_forms_fail_closed(self):
        guard = load_guard()
        for command in (
            "docker --host unix:///var/run/docker.sock inspect --format '{{json .}}' sample",
            "docker --context local inspect sample",
            "docker -H local container inspect --format '{{.State.Status}}' sample",
            "docker \\\n inspect sample",
        ):
            with self.subTest(command=command):
                self.assertFalse(guard.evaluate_command(command).allowed)

    def test_literal_status_variants_remain_allowed(self):
        guard = load_guard()
        for field in ("State.Status", "State.Running", "State.Health.Status", "State.ExitCode", "RestartCount", "Id"):
            for option in ("--format ", "--format=", "-f ", "-f"):
                command = "docker container inspect " + option + "'{{ " + "." + field + " }}' sample"
                with self.subTest(field=field, option=option):
                    self.assertTrue(guard.evaluate_command(command).allowed)
        self.assertTrue(guard.evaluate_command("docker inspect --format '{{json .State.Running}}' sample").allowed)

    def test_status_wrapper_and_documentation_search_remain_allowed(self):
        guard = load_guard()
        for command in (
            "scripts/agent-access/check-ripple-prod.sh",
            "rg -n 'docker inspect --format' docs/agent-playbooks",
            "git status --short",
        ):
            self.assertTrue(guard.evaluate_command(command).allowed)

    def test_cli_denies_without_reflecting_command(self):
        for tool_name, tool_input in (
            ("Bash", {"command": "docker inspect --format '{{json .}}' synthetic-container"}),
            ("functions.exec", {"input": 'await tools.exec_command({cmd: "docker inspect --format \'{{json .Config}}\' synthetic-container"});'}),
        ):
            with self.subTest(tool=tool_name), tempfile.TemporaryDirectory() as state_dir:
                result = subprocess.run(
                    [sys.executable, str(GUARD_PATH)],
                    input=json.dumps({"tool_name": tool_name, "tool_input": tool_input}),
                    text=True, capture_output=True, check=False,
                    env={"SIFUTUTOR_SECRET_GUARD_STATE_DIR": state_dir},
                )
                self.assertEqual(result.returncode, 0)
                verdict = json.loads(result.stdout)["hookSpecificOutput"]
                self.assertEqual(verdict["permissionDecision"], "deny")
                self.assertNotIn("synthetic-container", result.stdout + result.stderr)
                self.assertNotIn(".Config", result.stdout + result.stderr)
                self.assertEqual(list(Path(state_dir).iterdir()), [])

    def test_cli_allows_status_without_running_it(self):
        with tempfile.TemporaryDirectory() as state_dir:
            result = subprocess.run(
                [sys.executable, str(GUARD_PATH)],
                input=json.dumps({"tool_name": "Bash", "tool_input": {
                    "command": "docker inspect --format '{{.State.Health.Status}}' sample"
                }}),
                text=True, capture_output=True, check=False,
                env={"SIFUTUTOR_SECRET_GUARD_STATE_DIR": state_dir},
            )
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
