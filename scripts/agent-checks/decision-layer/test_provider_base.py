#!/usr/bin/env python3
"""TDD tests for the shared provider contract (answer shape + error types)."""

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


provider_base = load_module("provider_base")


class ProviderAnswerTest(unittest.TestCase):
    def test_holds_answer_confidence_and_cost(self) -> None:
        answer = provider_base.ProviderAnswer(answer="high", confidence=0.9, cost=0.0002)
        self.assertEqual(answer.answer, "high")
        self.assertEqual(answer.confidence, 0.9)
        self.assertEqual(answer.cost, 0.0002)

    def test_cost_defaults_to_zero(self) -> None:
        answer = provider_base.ProviderAnswer(answer="high", confidence=0.9)
        self.assertEqual(answer.cost, 0.0)

    def test_is_frozen(self) -> None:
        answer = provider_base.ProviderAnswer(answer="high", confidence=0.9)
        with self.assertRaises(Exception):
            answer.answer = "low"  # type: ignore[misc]


class ProviderErrorHierarchyTest(unittest.TestCase):
    def test_all_specific_errors_subclass_provider_error(self) -> None:
        for exc_type in (
            provider_base.ProviderUnavailable,
            provider_base.ProviderMalformedOutput,
            provider_base.ProviderNotConfigured,
        ):
            self.assertTrue(issubclass(exc_type, provider_base.ProviderError))


if __name__ == "__main__":
    unittest.main()
