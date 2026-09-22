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

    def test_config_never_carries_the_jev_credential(self) -> None:
        # The key lives only in the sidecar's environment (TYPESAFE_API_KEY);
        # no config key may hold it, so it can never land in an overrides file.
        self.assertFalse(any("key" in name.lower() for name in config.DEFAULT_CONFIG))
        self.assertIsNone(config.DEFAULT_CONFIG["jev_base_url"])
        self.assertIsNone(config.DEFAULT_CONFIG["jev_model"])


class LoadConfigTest(unittest.TestCase):
    def test_returns_the_defaults_when_nothing_overrides_them(self) -> None:
        loaded = config.load_config(env={})
        self.assertEqual(loaded["authoritative_decision_types"], [])
        self.assertEqual(loaded["provider"], "fake")

    def test_overrides_apply_on_top_of_defaults(self) -> None:
        loaded = config.load_config(overrides={"provider": "jev"}, env={})
        self.assertEqual(loaded["provider"], "jev")
        self.assertEqual(loaded["confidence_threshold"], config.DEFAULT_CONFIG["confidence_threshold"])

    def test_non_secret_base_url_and_model_env_overrides_apply_without_mutating_defaults(self) -> None:
        loaded = config.load_config(env={"TYPESAFE_BASE_URL": "http://127.0.0.1:1", "TYPESAFE_MODEL": "jev-test"})
        self.assertEqual(loaded["jev_base_url"], "http://127.0.0.1:1")
        self.assertEqual(loaded["jev_model"], "jev-test")
        self.assertIsNone(config.DEFAULT_CONFIG["jev_base_url"])

    def test_api_key_env_var_is_never_copied_into_config(self) -> None:
        loaded = config.load_config(env={"TYPESAFE_API_KEY": "placeholder-not-a-real-key"})
        self.assertNotIn("placeholder-not-a-real-key", repr(loaded))

    def test_does_not_read_the_real_process_environment_unless_asked(self) -> None:
        # Passing env explicitly (even {}) must never fall through to
        # os.environ -- config loading is deterministic and test-isolated.
        os.environ["TYPESAFE_BASE_URL"] = "http://must-not-leak.invalid"
        try:
            loaded = config.load_config(env={})
            self.assertIsNone(loaded["jev_base_url"])
        finally:
            del os.environ["TYPESAFE_BASE_URL"]


if __name__ == "__main__":
    unittest.main()
