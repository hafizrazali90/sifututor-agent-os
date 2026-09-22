#!/usr/bin/env python3
"""TDD tests for decision-layer configuration defaults (build item 10)."""

from __future__ import annotations

import importlib.util
import os
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


config = load_module("config")


class DefaultConfigTest(unittest.TestCase):
    def test_default_authoritative_decision_types_is_empty(self) -> None:
        # Shadow/advisory by default: nothing is opted in out of the box.
        self.assertEqual(config.DEFAULT_CONFIG["authoritative_decision_types"], [])

    def test_default_provider_is_the_fake_offline_provider(self) -> None:
        self.assertEqual(config.DEFAULT_CONFIG["provider"], "fake")

    def test_default_confidence_threshold_is_between_zero_and_one(self) -> None:
        threshold = config.DEFAULT_CONFIG["confidence_threshold"]
        self.assertGreater(threshold, 0.0)
        self.assertLess(threshold, 1.0)

    def test_default_jev_api_key_is_absent(self) -> None:
        self.assertIsNone(config.DEFAULT_CONFIG["jev_api_key"])


class LoadConfigTest(unittest.TestCase):
    def test_returns_the_defaults_when_nothing_overrides_them(self) -> None:
        loaded = config.load_config(env={})
        self.assertEqual(loaded["authoritative_decision_types"], [])
        self.assertEqual(loaded["provider"], "fake")

    def test_overrides_apply_on_top_of_defaults(self) -> None:
        loaded = config.load_config(overrides={"provider": "jev"}, env={})
        self.assertEqual(loaded["provider"], "jev")
        self.assertEqual(loaded["confidence_threshold"], config.DEFAULT_CONFIG["confidence_threshold"])

    def test_jev_api_key_env_var_is_picked_up_without_mutating_defaults(self) -> None:
        loaded = config.load_config(env={"JEV_API_KEY": "test-only-placeholder"})
        self.assertEqual(loaded["jev_api_key"], "test-only-placeholder")
        self.assertIsNone(config.DEFAULT_CONFIG["jev_api_key"])

    def test_does_not_read_the_real_process_environment_unless_asked(self) -> None:
        # Passing env explicitly (even {}) must never fall through to
        # os.environ -- config loading is deterministic and test-isolated.
        os.environ["JEV_API_KEY"] = "must-not-leak-into-this-call"
        try:
            loaded = config.load_config(env={})
            self.assertIsNone(loaded["jev_api_key"])
        finally:
            del os.environ["JEV_API_KEY"]


if __name__ == "__main__":
    unittest.main()
