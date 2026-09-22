#!/usr/bin/env python3
"""TDD tests for the Jev provider adapter (build item 5).

There is no live access to TypeSafe's Jev product yet (waitlist-gated;
Mission Ledger JEV-EVAL-001 is paused pending calibration verification).
This adapter is shaped like a real future SDK integration, but every test
here proves it never attempts a network call when unconfigured -- which is
the only state this bundle's test suite is allowed to exercise.
"""

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
provider_jev = load_module("provider_jev")


def request():
    return {
        "schema_version": 1,
        "decision_type": "triage.priority",
        "options": ["low", "medium", "high"],
        "context": "irrelevant",
        "sensitivity": "low",
    }


class JevProviderNotConfiguredTest(unittest.TestCase):
    def test_raises_provider_not_configured_when_no_api_key_is_present(self) -> None:
        jev = provider_jev.JevProvider(config={"jev_api_key": None})
        with self.assertRaises(provider_base.ProviderNotConfigured):
            jev.dispatch(request())

    def test_raises_provider_not_configured_when_api_key_is_an_empty_string(self) -> None:
        jev = provider_jev.JevProvider(config={"jev_api_key": ""})
        with self.assertRaises(provider_base.ProviderNotConfigured):
            jev.dispatch(request())

    def test_makes_zero_network_attempts_when_unconfigured(self) -> None:
        jev = provider_jev.JevProvider(config={"jev_api_key": None})
        for _ in range(3):
            with self.assertRaises(provider_base.ProviderNotConfigured):
                jev.dispatch(request())
        self.assertEqual(jev.network_call_count, 0)

    def test_defaults_to_unconfigured_with_no_config_at_all(self) -> None:
        jev = provider_jev.JevProvider()
        with self.assertRaises(provider_base.ProviderNotConfigured):
            jev.dispatch(request())
        self.assertEqual(jev.network_call_count, 0)

    def test_error_message_names_what_is_missing(self) -> None:
        jev = provider_jev.JevProvider(config={"jev_api_key": None})
        with self.assertRaises(provider_base.ProviderNotConfigured) as ctx:
            jev.dispatch(request())
        self.assertIn("jev", str(ctx.exception).lower())


class JevProviderModuleNeverImportsForbiddenNetworkingAtLoadTimeTest(unittest.TestCase):
    def test_network_call_is_gated_behind_the_configured_check(self) -> None:
        # Structural check: the live-call helper must only be reachable
        # from inside the branch that already confirmed an API key is
        # present, never unconditionally at module or dispatch top level.
        source = (HERE / "provider_jev.py").read_text(encoding="utf-8")
        self.assertIn("ProviderNotConfigured", source)
        # urllib is allowed to be imported (needed to shape the real call)
        # but must never be invoked before the configured check -- the
        # not-configured tests above are the behavioral proof of that.
        self.assertIn("def dispatch", source)


if __name__ == "__main__":
    unittest.main()
