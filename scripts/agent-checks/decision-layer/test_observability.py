#!/usr/bin/env python3
"""TDD tests for metadata-only observability records (build item 9)."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


observability = load_module("observability")

# Built from short concatenated pieces so this file's source text never
# contains a literal contiguous secret-shaped run (same convention as the
# repo's own secret_artifact_scan fixtures).
SENSITIVE_ANSWER = "sk-ant-api03-" + "a" * 12 + "b" * 12
SENSITIVE_CONTEXT = "the parent's IC number is 900101-14-5566"
SENSITIVE_REASON = "provider replied with raw payload: " + SENSITIVE_ANSWER


def full_response(**overrides):
    response = {
        "schema_version": 1,
        "decision_type": "triage.priority",
        "answer": SENSITIVE_ANSWER,
        "confidence": 0.92,
        "provider": "fake",
        "fallback_used": False,
        "authoritative": False,
        "latency_ms": 12.5,
        "cost": 0.0002,
        "outcome": "ok",
        "reason": SENSITIVE_REASON,
        # Extra fields a caller might attach that must never leak through.
        "request_context": SENSITIVE_CONTEXT,
    }
    response.update(overrides)
    return response


class BuildRecordFieldsTest(unittest.TestCase):
    def test_record_contains_exactly_the_metadata_fields(self) -> None:
        record = observability.build_record(full_response())
        self.assertEqual(
            set(record.keys()),
            {"decision_type", "provider", "latency_ms", "cost", "usage_input_tokens", "usage_output_tokens", "confidence", "fallback_used", "outcome"},
        )

    def test_record_values_match_the_response(self) -> None:
        response = full_response()
        record = observability.build_record(response)
        self.assertEqual(record["decision_type"], response["decision_type"])
        self.assertEqual(record["provider"], response["provider"])
        self.assertEqual(record["latency_ms"], response["latency_ms"])
        self.assertEqual(record["cost"], response["cost"])
        self.assertEqual(record["confidence"], response["confidence"])
        self.assertEqual(record["fallback_used"], response["fallback_used"])
        self.assertEqual(record["outcome"], response["outcome"])


class BuildRecordExcludesRawContentTest(unittest.TestCase):
    def test_record_never_contains_the_answer_field(self) -> None:
        record = observability.build_record(full_response())
        self.assertNotIn("answer", record)

    def test_record_never_contains_the_reason_field(self) -> None:
        record = observability.build_record(full_response())
        self.assertNotIn("reason", record)

    def test_record_never_contains_request_context(self) -> None:
        record = observability.build_record(full_response())
        self.assertNotIn("request_context", record)

    def test_serialized_record_does_not_contain_the_sensitive_answer(self) -> None:
        record = observability.build_record(full_response())
        serialized = json.dumps(record)
        self.assertNotIn(SENSITIVE_ANSWER, serialized)

    def test_serialized_record_does_not_contain_the_sensitive_context(self) -> None:
        record = observability.build_record(full_response())
        serialized = json.dumps(record)
        self.assertNotIn(SENSITIVE_CONTEXT, serialized)

    def test_serialized_record_does_not_contain_the_sensitive_reason(self) -> None:
        record = observability.build_record(full_response())
        serialized = json.dumps(record)
        self.assertNotIn(SENSITIVE_REASON, serialized)


if __name__ == "__main__":
    unittest.main()
