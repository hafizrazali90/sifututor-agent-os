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
    path = HERE / filename
    source = path.read_text()
    entrypoint = "\nraise SystemExit(main())"
    if entrypoint in source:
        source = source.split(entrypoint, 1)[0]
    spec = importlib.util.spec_from_loader(name, loader=None)
    module = importlib.util.module_from_spec(spec)
    exec(compile(source, str(path), "exec"), module.__dict__)
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

    def test_check_koda_is_read_only_by_default(self):
        with (
            patch.object(sys, "argv", ["codex-lifecycle-hook.py", "--check-koda"]),
            patch.object(lifecycle, "koda_health_check", return_value=(True, [])) as health,
        ):
            self.assertEqual(lifecycle.main(), 0)
        health.assert_called_once_with(write=False)

    def test_check_koda_write_probe_is_explicit(self):
        with (
            patch.object(
                sys,
                "argv",
                ["codex-lifecycle-hook.py", "--check-koda", "--write-check"],
            ),
            patch.object(lifecycle, "koda_health_check", return_value=(True, [])) as health,
        ):
            self.assertEqual(lifecycle.main(), 0)
        health.assert_called_once_with(write=True)

    def test_initialize_accepts_stateless_transport_without_session_header(self):
        initialize = json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}})
        with (
            patch.object(lifecycle, "koda_headers", return_value=({"Authorization": "Bearer hidden"}, "")),
            patch.object(
                lifecycle,
                "post_koda",
                side_effect=[(initialize, "application/json", ""), ("", "", "")],
            ) as post,
        ):
            session, error = lifecycle.koda_initialize("stateless-test")

        self.assertEqual(error, "")
        self.assertEqual(session["session_id"], "")
        self.assertEqual(session["transport"], "stateless")
        self.assertEqual(post.call_count, 2)

    def test_initialize_retains_legacy_session_transport(self):
        initialize = json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}})
        with (
            patch.object(lifecycle, "koda_headers", return_value=({"Authorization": "Bearer hidden"}, "")),
            patch.object(
                lifecycle,
                "post_koda",
                side_effect=[(initialize, "application/json", "legacy-session"), ("", "", "legacy-session")],
            ),
        ):
            session, error = lifecycle.koda_initialize("sessionful-test")

        self.assertEqual(error, "")
        self.assertEqual(session["session_id"], "legacy-session")
        self.assertEqual(session["transport"], "sessionful")

    def test_exact_duplicate_store_is_skipped(self):
        arguments = {
            "category": "lesson",
            "content": "Use one full Agent OS health sweep after focused checks.",
            "project": "sifututor",
            "source": "auto-captured",
            "tags": ["sifututor", "agent-os"],
            "why": "Avoid repeating the same deterministic suite.",
        }
        duplicate = {
            "id": "mem_existing",
            "content": "  use one FULL agent os health sweep after focused checks. ",
        }
        with (
            patch.object(lifecycle, "koda_initialize", return_value=({"headers": {}, "session_id": "x"}, "")),
            patch.object(
                lifecycle,
                "koda_tool_call",
                return_value=(tool_response([duplicate]), ""),
            ) as tool_call,
            patch.object(lifecycle, "print", create=True),
        ):
            self.assertEqual(lifecycle.koda_store_deduplicated(arguments), 0)
        self.assertEqual(tool_call.call_count, 1)
        self.assertEqual(tool_call.call_args.args[1], "memory_search")

    def test_unique_memory_is_stored_after_duplicate_preflight(self):
        arguments = {
            "category": "lesson",
            "content": "Use the read-only worktree inventory before release state reporting.",
            "project": "sifututor",
            "source": "auto-captured",
            "tags": ["sifututor", "agent-os"],
            "why": "One inventory command avoids inconsistent manual discovery.",
        }
        responses = [
            (tool_response([]), ""),
            (tool_response({"id": "mem_new"}), ""),
        ]
        with (
            patch.object(lifecycle, "koda_initialize", return_value=({"headers": {}, "session_id": "x"}, "")),
            patch.object(lifecycle, "koda_tool_call", side_effect=responses) as tool_call,
            patch.object(lifecycle, "print_koda_tool_result"),
        ):
            self.assertEqual(lifecycle.koda_store_deduplicated(arguments), 0)
        self.assertEqual(
            [call.args[1] for call in tool_call.call_args_list],
            ["memory_search", "memory_store"],
        )


class KodaVerifierTests(unittest.TestCase):
    def test_connection_message_supports_stateless_transport(self):
        self.assertEqual(
            verifier.connection_status_message(""),
            "Connected — stateless per-request transport",
        )

    def test_connection_message_keeps_legacy_session_detail(self):
        self.assertEqual(
            verifier.connection_status_message("legacy-session-id"),
            "Connected — session legacy-sessi...",
        )

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
