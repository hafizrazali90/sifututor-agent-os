#!/usr/bin/env python3
"""TDD tests for the fake/offline provider (build item 4).

The fake provider is the only provider this bundle's tests actually
exercise end to end. It must be fully scriptable, deterministic, and make
zero network calls under any scenario.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
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
provider_fake = load_module("provider_fake")


def request(**overrides):
    base = {
        "schema_version": 1,
        "decision_type": "triage.priority",
        "options": ["low", "medium", "high"],
        "context": "irrelevant for the fake provider",
        "sensitivity": "low",
    }
    base.update(overrides)
    return base


class FakeProviderOkScenarioTest(unittest.TestCase):
    def test_returns_a_well_formed_high_confidence_answer(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        result = fake.dispatch(request())
        self.assertIsInstance(result, provider_base.ProviderAnswer)
        self.assertIn(result.answer, request()["options"])
        self.assertGreaterEqual(result.confidence, 0.8)

    def test_is_deterministic_across_calls(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        first = fake.dispatch(request())
        second = fake.dispatch(request())
        self.assertEqual(first, second)

    def test_counts_every_dispatch_call(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        self.assertEqual(fake.call_count, 0)
        fake.dispatch(request())
        fake.dispatch(request())
        self.assertEqual(fake.call_count, 2)


class FakeProviderLowConfidenceScenarioTest(unittest.TestCase):
    def test_returns_confidence_below_a_typical_threshold(self) -> None:
        fake = provider_fake.FakeProvider(scenario="low_confidence")
        result = fake.dispatch(request())
        self.assertLess(result.confidence, 0.5)


class FakeProviderMalformedScenarioTest(unittest.TestCase):
    def test_returns_something_that_is_not_a_provider_answer(self) -> None:
        fake = provider_fake.FakeProvider(scenario="malformed")
        result = fake.dispatch(request())
        self.assertNotIsInstance(result, provider_base.ProviderAnswer)


class FakeProviderUnavailableScenarioTest(unittest.TestCase):
    def test_raises_provider_unavailable(self) -> None:
        fake = provider_fake.FakeProvider(scenario="unavailable")
        with self.assertRaises(provider_base.ProviderUnavailable):
            fake.dispatch(request())


class FakeProviderHangScenarioTest(unittest.TestCase):
    def test_reports_a_simulated_abort_instead_of_sleeping(self) -> None:
        fake = provider_fake.FakeProvider(scenario="hang", hang_seconds=5.0)
        started = time.monotonic()
        with self.assertRaises(provider_base.ProviderTimeout):
            fake.dispatch(request(), timeout_s=0.01)
        self.assertLess(time.monotonic() - started, 0.5)


class FakeProviderBlockScenarioTest(unittest.TestCase):
    def test_block_holds_the_call_until_released(self) -> None:
        import threading

        fake = provider_fake.FakeProvider(scenario="block")
        results: list[object] = []
        worker = threading.Thread(target=lambda: results.append(fake.dispatch(request())))
        worker.start()
        self.assertTrue(fake.started.wait(timeout=1.0))
        self.assertEqual(results, [])
        fake.release.set()
        worker.join(timeout=1.0)
        self.assertIsInstance(results[0], provider_base.ProviderAnswer)


class FakeProviderUnknownScenarioTest(unittest.TestCase):
    def test_raises_a_clear_error_for_an_unscripted_scenario(self) -> None:
        fake = provider_fake.FakeProvider(scenario="not-a-real-scenario")
        with self.assertRaises(ValueError):
            fake.dispatch(request())


class FakeProviderNeverTouchesNetworkTest(unittest.TestCase):
    def test_module_imports_no_networking_library(self) -> None:
        source = (HERE / "provider_fake.py").read_text(encoding="utf-8")
        for forbidden in ("socket", "urllib", "http.client", "requests"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
