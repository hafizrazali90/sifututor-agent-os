#!/usr/bin/env python3
"""TDD tests for the deterministic pre-policy layer (build item 3)."""

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


pre_policy = load_module("pre_policy")


class PrePolicyEvaluateTest(unittest.TestCase):
    def test_returns_none_for_an_unmatched_decision_type(self) -> None:
        result = pre_policy.evaluate({"decision_type": "triage.priority"})
        self.assertIsNone(result)

    def test_denies_destructive_release_actions_deterministically(self) -> None:
        result = pre_policy.evaluate({"decision_type": "release.destructive_action"})
        self.assertIsNotNone(result)
        self.assertEqual(result.answer, "deny")
        self.assertEqual(result.confidence, 1.0)
        self.assertTrue(result.reason)

    def test_holds_unreviewed_refunds_for_a_human(self) -> None:
        result = pre_policy.evaluate({"decision_type": "payments.unreviewed_refund"})
        self.assertIsNotNone(result)
        self.assertEqual(result.answer, "hold_for_human")

    def test_result_is_immutable(self) -> None:
        result = pre_policy.evaluate({"decision_type": "release.destructive_action"})
        with self.assertRaises(Exception):
            result.answer = "approve"  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
