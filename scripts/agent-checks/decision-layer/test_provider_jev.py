#!/usr/bin/env python3
"""Contract tests for the Jev provider (official @typesafe-ai/sdk sidecar).

Three layers, none of which reach a paid or public endpoint:

1. Pure mapping: request -> System One payload, and typed result -> answer.
2. Gate and error mapping with an injected runner (no process spawned).
3. Wire contract through the real sidecar and the real installed SDK
   against a local HTTP server on 127.0.0.1 that plays the TypeSafe API:
   it asserts the SDK sent `POST /v1/systemone` with the Bearer header
   and the exact question JSON, and that a hung server is killed at the
   deadline with nothing left running. These skip, with a stated reason,
   only when Node or the pinned SDK is not installed locally.
"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import threading
import time
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


provider_base = load_module("provider_base")
provider_jev = load_module("provider_jev")

FAKE_KEY = "test-only-placeholder-not-a-real-key"
SIDECAR_READY = bool(shutil.which("node")) and provider_jev.SDK_INSTALL_MARKER.is_file()
SKIP_REASON = "node or the pinned @typesafe-ai/sdk is not installed in jev-sidecar/"


def choice_request(**overrides):
    base = {
        "schema_version": 1,
        "decision_type": "triage.priority",
        "options": ["low", "medium", "high"],
        "context": "Customer reports a broken checkout button.",
        "sensitivity": "low",
    }
    base.update(overrides)
    return base


def scale_request(low=1, high=5):
    return {
        "schema_version": 1,
        "decision_type": "review.risk",
        "scale": {"min": low, "max": high},
        "context": "small docs change",
        "sensitivity": "low",
    }


def ok_output(answer: dict, usage=None):
    return {
        "schema_version": 1,
        "ok": True,
        "result": {"model": "jev-latest", "answers": {"answer": answer}, "usage": usage or {"input_tokens": 12, "output_tokens": 3}},
    }


class BuildPayloadContractTest(unittest.TestCase):
    def test_options_become_one_choice_question_keyed_by_label(self) -> None:
        payload = provider_jev.build_system_one_payload(choice_request(), base_url=None, model=None, timeout_ms=400)
        self.assertEqual(
            payload,
            {
                "schema_version": 1,
                "timeout_ms": 400,
                "state": "Customer reports a broken checkout button.",
                "questions": {
                    "answer": {
                        "type": "choice",
                        "instructions": "Decision type: triage.priority. Select the single best option.",
                        "criteria": {"low": None, "medium": None, "high": None},
                    }
                },
            },
        )

    def test_scale_becomes_one_score_question_with_zero_indexed_rubric(self) -> None:
        payload = provider_jev.build_system_one_payload(scale_request(1, 3), base_url="http://127.0.0.1:9", model="jev-x", timeout_ms=100)
        self.assertEqual(payload["questions"]["answer"]["type"], "score")
        self.assertEqual(payload["questions"]["answer"]["criteria"], ["level 1", "level 2", "level 3"])
        self.assertEqual(payload["base_url"], "http://127.0.0.1:9")
        self.assertEqual(payload["model"], "jev-x")

    def test_scale_that_cannot_be_a_rubric_is_unsupported_not_guessed(self) -> None:
        with self.assertRaises(provider_base.ProviderUnsupportedRequest):
            provider_jev.build_system_one_payload(scale_request(0, 100), base_url=None, model=None, timeout_ms=100)
        with self.assertRaises(provider_base.ProviderUnsupportedRequest):
            provider_jev.build_system_one_payload(scale_request(0.5, 3), base_url=None, model=None, timeout_ms=100)

    def test_payload_carries_only_context_never_other_request_fields(self) -> None:
        payload = provider_jev.build_system_one_payload(choice_request(sensitivity="high"), base_url=None, model=None, timeout_ms=1)
        self.assertNotIn("sensitivity", json.dumps(payload))


class ParseResultContractTest(unittest.TestCase):
    def test_choice_answer_maps_to_provider_answer_with_usage(self) -> None:
        answer = provider_jev.parse_system_one_result(
            ok_output({"type": "choice", "choice": "high", "confidence": 0.81, "probabilities": {"low": 0.1, "medium": 0.09, "high": 0.81}}),
            choice_request(),
        )
        self.assertEqual(answer, provider_base.ProviderAnswer(answer="high", confidence=0.81, cost=0.0, usage_input_tokens=12, usage_output_tokens=3))

    def test_score_answer_is_offset_back_onto_the_request_scale(self) -> None:
        answer = provider_jev.parse_system_one_result(
            ok_output({"type": "score", "score": 1.5, "confidence": 0.7, "legend": {}, "probabilities": {}}),
            scale_request(1, 5),
        )
        self.assertEqual(answer.answer, 2.5)

    def test_malformed_results_are_rejected_with_codes_only(self) -> None:
        cases = {
            "choice_not_in_options": ok_output({"type": "choice", "choice": "urgent", "confidence": 0.9}),
            "answer_type_mismatch": ok_output({"type": "score", "score": 1, "confidence": 0.9}),
            "confidence_out_of_range": ok_output({"type": "choice", "choice": "low", "confidence": 1.7}),
            "confidence_not_numeric": ok_output({"type": "choice", "choice": "low", "confidence": "high"}),
            "answer_missing": {"schema_version": 1, "ok": True, "result": {"answers": {}}},
            "sidecar_protocol_mismatch": {"ok": True},
        }
        for code, output in cases.items():
            with self.assertRaises(provider_base.ProviderMalformedOutput) as ctx:
                provider_jev.parse_system_one_result(output, choice_request())
            self.assertEqual(ctx.exception.code, code)

    def test_error_kinds_map_to_the_engine_error_taxonomy(self) -> None:
        expected = {
            "timeout": provider_base.ProviderTimeout,
            "abort": provider_base.ProviderTimeout,
            "connection": provider_base.ProviderUnavailable,
            "api_status": provider_base.ProviderUnavailable,
            "api_auth": provider_base.ProviderNotConfigured,
            "config_missing_key": provider_base.ProviderNotConfigured,
            "invalid_input": provider_base.ProviderMalformedOutput,
            "something-new": provider_base.ProviderUnavailable,
        }
        for kind, exception in expected.items():
            with self.assertRaises(exception) as ctx:
                provider_jev.parse_system_one_result({"schema_version": 1, "ok": False, "error_kind": kind}, choice_request())
            self.assertEqual(ctx.exception.code, f"jev_{kind}")
            self.assertEqual(str(ctx.exception), "")


class ConfigurationGateTest(unittest.TestCase):
    def test_no_key_means_not_configured_and_no_runner_call(self) -> None:
        calls = []
        jev = provider_jev.JevProvider(env={}, runner=lambda *a: calls.append(a), node_executable="/usr/bin/true")
        for _ in range(3):
            with self.assertRaises(provider_base.ProviderNotConfigured) as ctx:
                jev.dispatch(choice_request())
        self.assertEqual(ctx.exception.code, "typesafe_api_key_missing")
        self.assertEqual(calls, [])
        self.assertEqual(jev.network_call_count, 0)

    def test_empty_key_counts_as_missing(self) -> None:
        jev = provider_jev.JevProvider(env={"TYPESAFE_API_KEY": ""}, runner=lambda *a: None)
        with self.assertRaises(provider_base.ProviderNotConfigured):
            jev.dispatch(choice_request())

    def test_missing_node_is_not_configured_not_a_crash(self) -> None:
        jev = provider_jev.JevProvider(env={"TYPESAFE_API_KEY": FAKE_KEY}, runner=lambda *a: None)
        jev.node = None  # what shutil.which returns on a machine without Node
        with self.assertRaises(provider_base.ProviderNotConfigured) as ctx:
            jev.dispatch(choice_request())
        self.assertEqual(ctx.exception.code, "sidecar_dependencies_missing")

    def test_runner_receives_only_path_and_key_in_the_child_environment(self) -> None:
        seen = {}

        def runner(argv, payload, env, timeout_s):
            seen.update(argv=argv, payload=payload, env=dict(env), timeout_s=timeout_s)
            return ok_output({"type": "choice", "choice": "low", "confidence": 0.9})

        jev = provider_jev.JevProvider(env={"TYPESAFE_API_KEY": FAKE_KEY, "HOME": "/nope", "AWS_SECRET": "x"}, runner=runner, node_executable="/usr/bin/node")
        jev.dependencies_available = lambda: True  # type: ignore[method-assign]
        answer = jev.dispatch(choice_request(), timeout_s=0.5)
        self.assertEqual(answer.answer, "low")
        self.assertEqual(set(seen["env"]), {"PATH", "TYPESAFE_API_KEY"})
        self.assertEqual(seen["payload"]["timeout_ms"], 500)
        self.assertEqual(seen["timeout_s"], 0.5)
        self.assertEqual(jev.network_call_count, 1)


class _LocalTypeSafe(BaseHTTPRequestHandler):
    """Plays https://api.typesafe.ai for the real SDK, on loopback only."""

    requests: list[dict] = []
    hang_seconds = 0.0

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(length) or b"{}")
        type(self).requests.append({"path": self.path, "auth": self.headers.get("Authorization"), "body": body})
        if type(self).hang_seconds:
            time.sleep(type(self).hang_seconds)
        response = {
            "model": "jev-latest",
            "answers": {"answer": {"type": "choice", "choice": "medium", "confidence": 0.66, "probabilities": {"low": 0.2, "medium": 0.66, "high": 0.14}}},
            "usage": {"input_tokens": 21, "output_tokens": 2},
        }
        payload = json.dumps(response).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):  # silence
        return


def _serve():
    server = ThreadingHTTPServer(("127.0.0.1", 0), _LocalTypeSafe)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


@unittest.skipUnless(SIDECAR_READY, SKIP_REASON)
class WireContractThroughRealSdkTest(unittest.TestCase):
    def setUp(self) -> None:
        _LocalTypeSafe.requests = []
        _LocalTypeSafe.hang_seconds = 0.0
        self.server = _serve()
        self.base_url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()

    def provider(self) -> "provider_jev.JevProvider":
        return provider_jev.JevProvider(config={"jev_base_url": self.base_url}, env={"TYPESAFE_API_KEY": FAKE_KEY})

    def test_sdk_posts_v1_systemone_with_bearer_and_typed_question(self) -> None:
        answer = self.provider().dispatch(choice_request(), timeout_s=5.0)
        self.assertEqual(answer, provider_base.ProviderAnswer(answer="medium", confidence=0.66, cost=0.0, usage_input_tokens=21, usage_output_tokens=2))
        self.assertEqual(len(_LocalTypeSafe.requests), 1)
        sent = _LocalTypeSafe.requests[0]
        self.assertEqual(sent["path"], "/v1/systemone")
        self.assertEqual(sent["auth"], f"Bearer {FAKE_KEY}")
        self.assertEqual(sent["body"]["state"], "Customer reports a broken checkout button.")
        self.assertEqual(sent["body"]["questions"]["answer"]["type"], "choice")
        self.assertEqual(sent["body"]["questions"]["answer"]["criteria"], {"low": None, "medium": None, "high": None})
        self.assertIn("model", sent["body"])

    def test_hung_server_is_aborted_at_the_deadline(self) -> None:
        _LocalTypeSafe.hang_seconds = 3.0
        started = time.monotonic()
        with self.assertRaises(provider_base.ProviderTimeout):
            self.provider().dispatch(choice_request(), timeout_s=0.3)
        elapsed = time.monotonic() - started
        self.assertLess(elapsed, 0.3 + provider_jev.KILL_GRACE_S + 1.0)
        self.assertEqual(len(_LocalTypeSafe.requests), 1)

    def test_no_key_never_starts_the_sidecar_process(self) -> None:
        jev = provider_jev.JevProvider(config={"jev_base_url": self.base_url}, env={})
        with self.assertRaises(provider_base.ProviderNotConfigured):
            jev.dispatch(choice_request())
        self.assertEqual(_LocalTypeSafe.requests, [])
        self.assertEqual(jev.network_call_count, 0)

if __name__ == "__main__":
    unittest.main()
