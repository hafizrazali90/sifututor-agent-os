#!/usr/bin/env python3
"""Regression tests for Codex's direct Koda integration."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def load_script(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


contract = load_script("koda_contract", "koda_contract.py")
lifecycle = load_script("codex_lifecycle_hook", "codex-lifecycle-hook.py")
verifier = load_script("koda_verify", "koda-verify.py")


def tool_response(payload: object) -> dict:
    return {
        "result": {
            "content": [{"type": "text", "text": json.dumps(payload)}],
        }
    }


class KodaContractTests(unittest.TestCase):
    def test_capability_tiers_cover_the_current_14_tool_contract(self):
        expected = {
            "memory_context", "memory_flag", "memory_forget", "memory_init",
            "memory_recall", "memory_relate", "memory_search", "memory_store",
            "memory_update", "project_health", "session_end", "session_list",
            "session_start", "validation_run",
        }
        self.assertEqual(contract.ALL_KODA_TOOLS, expected)
        self.assertEqual(len(contract.ALL_KODA_TOOLS), 14)
        self.assertIn("memory_update", contract.REQUIRED_KODA_TOOLS)
        self.assertNotIn("validation_run", contract.REQUIRED_KODA_TOOLS)

    def test_capability_report_blocks_core_only_and_reports_other_tiers(self):
        available = contract.ALL_KODA_TOOLS - {"memory_update", "validation_run"}
        report = contract.capability_report(available)
        self.assertEqual(report["missing_required"], ["memory_update"])
        self.assertEqual(report["tiers"]["administrative"]["missing"], ["validation_run"])

    def test_health_search_explicitly_exercises_project_filter(self):
        args = lifecycle.koda_health_search_arguments()
        self.assertEqual(args["project"], "sifututor")
        self.assertIn("tags", args)


class KodaVerifierTests(unittest.TestCase):
    def test_api_key_status_never_contains_credential_material(self):
        secret = "aee963b9-super-secret-value"
        message = verifier.api_key_status_message(secret)
        self.assertEqual(message, "KODA_API_KEY is set")
        self.assertNotIn(secret[:8], message)

    def test_existing_confirmation_is_updated_not_duplicated(self):
        existing = {"id": "mem_existing", "content": "old", "tags": ["koda-setup"]}
        responses = [
            (tool_response([existing]), "session"),
            (tool_response({"id": "mem_existing", "message": "updated"}), "session"),
        ]
        with patch.object(verifier, "post", side_effect=responses) as mocked:
            result = verifier.ensure_confirmation_memory(
                {"Authorization": "Bearer hidden"},
                "session",
                contract.ALL_KODA_TOOLS,
                machine="test-host",
                system_info="TestOS",
                timestamp="2026-07-13 08:00 UTC",
            )

        self.assertEqual(result, ("mem_existing", "updated"))
        called_tools = [
            call.args[0]["params"]["name"]
            for call in mocked.call_args_list
        ]
        self.assertEqual(called_tools, ["memory_search", "memory_update"])

    def test_missing_confirmation_is_stored_once(self):
        responses = [
            (tool_response([]), "session"),
            (tool_response({"id": "mem_new", "message": "stored"}), "session"),
        ]
        with patch.object(verifier, "post", side_effect=responses) as mocked:
            result = verifier.ensure_confirmation_memory(
                {"Authorization": "Bearer hidden"},
                "session",
                contract.ALL_KODA_TOOLS,
                machine="test-host",
                system_info="TestOS",
                timestamp="2026-07-13 08:00 UTC",
            )

        self.assertEqual(result, ("mem_new", "stored"))
        called_tools = [
            call.args[0]["params"]["name"]
            for call in mocked.call_args_list
        ]
        self.assertEqual(called_tools, ["memory_search", "memory_store"])


if __name__ == "__main__":
    unittest.main()
