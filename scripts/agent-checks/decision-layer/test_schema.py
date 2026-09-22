#!/usr/bin/env python3
"""TDD tests for the decision-layer request/response schema (build item 1)."""

from __future__ import annotations

import importlib.util
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


schema = load_module("schema")


def valid_request(**overrides):
    request = {
        "schema_version": schema.SCHEMA_VERSION,
        "decision_type": "triage.priority",
        "options": ["low", "medium", "high"],
        "context": "Customer reports a broken checkout button.",
        "sensitivity": "low",
    }
    request.update(overrides)
    return request


class SchemaVersionTest(unittest.TestCase):
    def test_current_schema_version_is_an_int(self) -> None:
        self.assertIsInstance(schema.SCHEMA_VERSION, int)
        self.assertGreaterEqual(schema.SCHEMA_VERSION, 1)


class ValidateRequestTest(unittest.TestCase):
    def test_accepts_well_formed_options_request(self) -> None:
        self.assertEqual(schema.validate_request(valid_request()), [])

    def test_accepts_well_formed_scale_request(self) -> None:
        request = valid_request(options=None, scale={"min": 0, "max": 1})
        self.assertEqual(schema.validate_request(request), [])

    def test_rejects_non_object_request(self) -> None:
        self.assertIn("request:object_required", schema.validate_request("not a dict"))

    def test_rejects_wrong_schema_version(self) -> None:
        errors = schema.validate_request(valid_request(schema_version=999))
        self.assertIn("schema_version:unsupported", errors)

    def test_rejects_missing_decision_type(self) -> None:
        request = valid_request()
        del request["decision_type"]
        self.assertIn("decision_type:nonempty_text_required", schema.validate_request(request))

    def test_rejects_blank_decision_type(self) -> None:
        errors = schema.validate_request(valid_request(decision_type="   "))
        self.assertIn("decision_type:nonempty_text_required", errors)

    def test_rejects_request_missing_both_options_and_scale(self) -> None:
        request = valid_request(options=None)
        errors = schema.validate_request(request)
        self.assertIn("options_or_scale:required", errors)

    def test_rejects_empty_options_list(self) -> None:
        errors = schema.validate_request(valid_request(options=[]))
        self.assertIn("options:nonempty_string_list_required", errors)

    def test_rejects_malformed_scale(self) -> None:
        request = valid_request(options=None, scale={"min": 1, "max": 0})
        errors = schema.validate_request(request)
        self.assertIn("scale:min_max_numeric_required", errors)

    def test_rejects_non_string_context(self) -> None:
        errors = schema.validate_request(valid_request(context=123))
        self.assertIn("context:text_required", errors)

    def test_rejects_invalid_sensitivity(self) -> None:
        errors = schema.validate_request(valid_request(sensitivity="extreme"))
        self.assertIn("sensitivity:invalid_choice", errors)

    def test_defaults_sensitivity_to_low_when_absent(self) -> None:
        request = valid_request()
        del request["sensitivity"]
        self.assertEqual(schema.validate_request(request), [])


class ResponseFieldsTest(unittest.TestCase):
    def test_response_schema_fields_cover_required_shape(self) -> None:
        fields = schema.response_schema_fields()
        for required in (
            "schema_version", "decision_type", "answer", "confidence", "provider",
            "fallback_used", "authoritative", "latency_ms", "cost", "outcome", "reason",
        ):
            self.assertIn(required, fields)


class RequestValidationErrorTest(unittest.TestCase):
    def test_carries_the_error_list(self) -> None:
        exc = schema.RequestValidationError(["decision_type:nonempty_text_required"])
        self.assertEqual(exc.errors, ["decision_type:nonempty_text_required"])


if __name__ == "__main__":
    unittest.main()
