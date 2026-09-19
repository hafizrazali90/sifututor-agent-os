"""Offline capability attestation tests; no provider process is launched."""
import copy
from datetime import datetime, timezone
import unittest
import json
from pathlib import Path
import subprocess
import sys
import importlib.util
import io
from unittest.mock import patch

from agent_os_adapter_contract import evaluate_capabilities

NOW = datetime(2026, 9, 19, 12, tzinfo=timezone.utc)
IDENTITY = dict(tool="example-cli", tool_version="1.0", provider="example", model="model-a", configuration_id="config-v1", environment_id="isolated-worktree-a")

def record():
    return dict(schema_version=1, identity=dict(IDENTITY), observed_at="2026-09-19T11:00:00Z", expires_at="2026-09-19T13:00:00Z", capabilities={"read-files": dict(status="supported", evidence_kind="live", evidence_ref="observation-01")})

class Capabilities(unittest.TestCase):
    def check(self, value, required=None, identity=None):
        return evaluate_capabilities(value, required or ["read-files"], expected_identity=IDENTITY if identity is None else identity, now=NOW)

    def test_exact_fresh_observation_is_eligible_not_parity_or_authority(self):
        result = self.check(record())
        self.assertTrue(result["ready"])
        self.assertFalse(result["live_parity_proven"])
        self.assertFalse(result["execution_authorized"])

    def test_model_name_cannot_supply_missing_capability(self):
        self.assertEqual(self.check(record(), ["image-input"])["reasons"], ["capability_missing:image-input"])

    def test_fixture_and_declaration_do_not_prove_live_support(self):
        for kind in ("fixture", "declared"):
            value = record()
            value["capabilities"]["read-files"]["evidence_kind"] = kind
            self.assertEqual(self.check(value)["reasons"], ["capability_unproven:read-files"])

    def test_unsupported_and_unknown_refuse(self):
        for status in ("unsupported", "unknown"):
            value = record()
            value["capabilities"]["read-files"]["status"] = status
            self.assertEqual(self.check(value)["reasons"], ["capability_unavailable:read-files"])

    def test_identity_bound_to_configuration_and_environment(self):
        for key in IDENTITY:
            expected = dict(IDENTITY)
            expected[key] += "-changed"
            self.assertEqual(self.check(record(), identity=expected)["reasons"], ["identity_mismatch"])

    def test_expired_future_and_reversed_observations_refuse(self):
        for key, value in (("expires_at", "2026-09-19T12:00:00Z"), ("observed_at", "2026-09-19T12:01:00Z"), ("expires_at", "2026-09-19T10:00:00Z")):
            item = record()
            item[key] = value
            self.assertFalse(self.check(item)["ready"])

    def test_invalid_shape_refuses_without_echoing_payload(self):
        values = [None, [], {}, record()]
        values[-1]["secret"] = "sensitive-sentinel"
        for value in values:
            result = self.check(value)
            self.assertFalse(result["ready"])
            self.assertNotIn("sensitive-sentinel", str(result))

    def test_empty_requirements_and_partial_expected_identity_refuse(self):
        self.assertFalse(evaluate_capabilities(record(), [], expected_identity=IDENTITY, now=NOW)["ready"])
        self.assertFalse(self.check(record(), identity={"tool": "example-cli"})["ready"])

    def test_invalid_capability_and_timestamp_types_refuse(self):
        for field, bad in (("status", []), ("evidence_kind", {}), ("evidence_ref", "")):
            value = record()
            value["capabilities"]["read-files"][field] = bad
            self.assertEqual(self.check(value)["reasons"], ["invalid_capabilities"])
        for bad in (True, "2026-09-19T11:00:00", "2026-09-19T11:00:00+08:00"):
            value = record()
            value["observed_at"] = bad
            self.assertEqual(self.check(value)["reasons"], ["invalid_timestamp"])

    def test_input_not_modified(self):
        value = record()
        before = copy.deepcopy(value)
        self.check(value)
        self.assertEqual(before, value)

class PreflightCLI(unittest.TestCase):
    def run_cli(self, payload, *extra):
        return subprocess.run([sys.executable, str(Path(__file__).with_name("agent-os-adapter-readiness.py")), "--capability-preflight", *extra], input=payload, text=True, capture_output=True, check=False)

    def test_real_entrypoint_unknown_capability_no_provider_needed(self):
        item = record()
        item["observed_at"] = "2020-01-01T00:00:00Z"
        item["expires_at"] = "2099-01-01T00:00:00Z"
        proc = self.run_cli(json.dumps(dict(record=item, required=["image-input"], expected_identity=IDENTITY)))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["reasons"], ["capability_missing:image-input"])

    def test_invalid_input_does_not_echo(self):
        proc = self.run_cli("sensitive-sentinel")
        self.assertEqual(proc.returncode, 2)
        self.assertNotIn("sensitive-sentinel", proc.stdout + proc.stderr)

    def test_live_mode_cannot_be_combined(self):
        proc = self.run_cli("{}", "--live-claude")
        self.assertEqual(proc.returncode, 2)

    def test_duplicate_keys_rejected(self):
        proc = self.run_cli('{"record": {}, "record": {}}')
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(json.loads(proc.stdout)["reasons"], ["invalid_input"])

    def test_oversized_input_rejected(self):
        self.assertEqual(self.run_cli(" " * 65537).returncode, 2)

    def test_preflight_bypasses_provider_and_installed_probes(self):
        spec = importlib.util.spec_from_file_location("capability_readiness_under_test", Path(__file__).with_name("agent-os-adapter-readiness.py"))
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {spec.name: module}):
            spec.loader.exec_module(module)
            value = record()
            value["observed_at"] = "2020-01-01T00:00:00Z"
            value["expires_at"] = "2099-01-01T00:00:00Z"
            envelope = json.dumps(dict(record=value, required=["read-files"], expected_identity=IDENTITY))
            with patch.object(module, "run_command", side_effect=AssertionError("provider process prohibited")) as run, patch.object(module, "check_shared_core", side_effect=AssertionError("normal probe prohibited")) as probe, patch.object(sys, "argv", ["readiness", "--capability-preflight"]), patch.object(sys, "stdin", io.StringIO(envelope)), patch.object(sys, "stdout", io.StringIO()) as output:
                self.assertEqual(module.main(), 0)
                self.assertTrue(json.loads(output.getvalue())["ready"])
                run.assert_not_called()
                probe.assert_not_called()


if __name__ == "__main__":
    unittest.main()
