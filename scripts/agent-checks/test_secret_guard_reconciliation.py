"""Synthetic safety regression journeys; never execute inspected commands."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

GUARD_PATH = Path(__file__).with_name("secret_output_guard.py")


def load_guard():
    spec = importlib.util.spec_from_file_location("reconciliation_guard", GUARD_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PatchToolClassificationTest(unittest.TestCase):
    def test_direct_patch_data_does_not_enter_command_classifier(self):
        guard = load_guard()
        data = "*** Begin Patch\n*** Add File: example.txt\n+synthetic prose\n*** End Patch"
        for name in ("apply_patch", "functions.apply_patch"):
            for value in (data, {"input": data}, {"patch": data}, {"command": data}):
                with self.subTest(name=name, shape=type(value).__name__), patch.object(
                    guard, "evaluate_command", return_value=guard.Decision(False, "synthetic denial")
                ) as classifier:
                    self.assertTrue(guard.evaluate_tool_request(name, value, {}).allowed)
                    classifier.assert_not_called()

    def test_execution_unknown_and_malformed_payloads_still_inspected(self):
        guard = load_guard()
        data = "*** Begin Patch\n*** Add File: example.txt\n+synthetic prose\n*** End Patch"
        cases = [(name, {"input": data}) for name in
                 ("Bash", "exec_command", "functions.exec", "untrusted.apply_patch")]
        cases.extend(("apply_patch", value) for value in (
            {"input": data, "command": "synthetic"}, {"input": data, "patch": data},
            {"input": [data]}, "not a patch", data + "\ntrailing executable text"))
        for name, value in cases:
            with self.subTest(name=name, shape=type(value).__name__), patch.object(
                guard, "evaluate_command", return_value=guard.Decision(False, "synthetic denial")
            ) as classifier:
                self.assertFalse(guard.evaluate_tool_request(name, value, {}).allowed)
                classifier.assert_called()

    def test_quarantine_precedes_direct_patch_classification(self):
        guard = load_guard()
        data = "*** Begin Patch\n*** Add File: example.txt\n+synthetic prose\n*** End Patch"
        with patch.object(guard, "secret_visual_boundary_active", return_value=True), patch.object(
            guard, "_direct_patch_data"
        ) as classify:
            self.assertFalse(guard.evaluate_tool_request("apply_patch", data, {}).allowed)
            classify.assert_not_called()


class PatchToolCLIJourneyTest(unittest.TestCase):
    DATA = "*** Begin Patch\n*** Add File: docs/example.md\n+Synthetic example: pm2 jlist\n*** End Patch"

    def run_hook(self, name, value, *, active=False, aliases=False):
        guard = load_guard()
        with tempfile.TemporaryDirectory() as state_dir:
            payload = {"session_id": "synthetic-patch-journey"}
            payload.update({"toolName" if aliases else "tool_name": name,
                            "toolInput" if aliases else "tool_input": value})
            if active:
                guard.mark_secret_visual_boundary(payload, state_dir=Path(state_dir))
            result = subprocess.run(
                [sys.executable, str(GUARD_PATH)], input=json.dumps(payload),
                text=True, capture_output=True, check=False,
                env={"SIFUTUTOR_SECRET_GUARD_STATE_DIR": state_dir},
            )
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")
            return result.stdout

    def assert_denied_without_payload(self, output):
        verdict = json.loads(output)["hookSpecificOutput"]
        self.assertEqual(verdict["permissionDecision"], "deny")
        for fragment in (self.DATA, "pm2 jlist", "docs/example.md", "SYNTHETIC_PRIVATE_MARKER"):
            self.assertNotIn(fragment, output)

    def test_cli_accepts_known_direct_patch_shapes(self):
        for name in ("apply_patch", "functions.apply_patch"):
            for value in (self.DATA, {"input": self.DATA}, {"patch": self.DATA}, {"command": self.DATA}):
                for aliases in (False, True):
                    with self.subTest(name=name, shape=type(value).__name__, aliases=aliases):
                        self.assertEqual(self.run_hook(name, value, aliases=aliases), "")

    def test_cli_retains_malformed_mixed_unknown_and_execution_denials(self):
        cases = [
            ("apply_patch", "pm2 jlist SYNTHETIC_PRIVATE_MARKER"),
            ("apply_patch", self.DATA + "\ntrailing text"),
            ("apply_patch", {"input": self.DATA, "command": "pm2 jlist"}),
            ("apply_patch", {"input": self.DATA, "patch": self.DATA}),
            ("apply_patch", {"input": [self.DATA]}),
            ("Bash", {"command": "pm2 jlist"}),
            ("exec_command", {"cmd": "pm2 jlist"}),
            ("untrusted.apply_patch", self.DATA),
            ("apply_patch_extra", {"input": self.DATA}),
            ("functions.exec", {"input": 'await tools.apply_patch("synthetic"); await tools.exec_command({cmd: "pm2 jlist"});'}),
        ]
        for name, value in cases:
            with self.subTest(name=name, shape=type(value).__name__):
                self.assert_denied_without_payload(self.run_hook(name, value))

    def test_cli_quarantine_still_denies_every_tool(self):
        for name, value in (
            ("apply_patch", self.DATA),
            ("functions.apply_patch", {"command": self.DATA}),
            ("functions.exec", {"input": 'await tools.apply_patch("synthetic");'}),
            ("Bash", {"command": "git status --short"}),
            ("unknown_tool", {}),
        ):
            with self.subTest(name=name):
                self.assert_denied_without_payload(self.run_hook(name, value, active=True))


class InspectFormatSafetyTest(unittest.TestCase):
    def test_direct_patch_payload_is_inert_data(self):
        guard = load_guard()
        patch = "*** Begin Patch\n*** Add File: docs/example.md\n+Synthetic example: pm2 jlist\n*** End Patch"
        for name in ("apply_patch", "functions.apply_patch"):
            for tool_input in (patch, {"input": patch}, {"patch": patch}, {"command": patch}):
                with self.subTest(name=name, shape=type(tool_input).__name__):
                    self.assertTrue(guard.evaluate_tool_request(name, tool_input, {}).allowed)
                    self.assertTrue(guard.evaluate_tool_request(name, tool_input, {}).allowed)

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
