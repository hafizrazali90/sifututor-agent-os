#!/usr/bin/env python3
"""TDD tests for the decision-layer engine: the orchestrator that wires the
secret filter, pre-policy layer, provider dispatch, and confidence/
fallback policy together (build items 3, 6, 7, 10).

Every test here is offline and deterministic: the only provider ever
dispatched to is FakeProvider, scripted per scenario. No test makes, or
can make, a network call.
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
provider_jev = load_module("provider_jev")
pre_policy = load_module("pre_policy")
secret_filter = load_module("secret_filter")
observability = load_module("observability")
schema = load_module("schema")
retry = load_module("retry")
config_module = load_module("config")
engine = load_module("engine")

RESPONSE_FIELDS = set(schema.response_schema_fields())


def request(**overrides):
    base = {
        "schema_version": 1,
        "decision_type": "triage.priority",
        "options": ["low", "medium", "high"],
        "context": "Customer reports a broken checkout button.",
        "sensitivity": "low",
    }
    base.update(overrides)
    return base


def test_config(**overrides):
    cfg = config_module.load_config(env={})
    cfg.update(overrides)
    return cfg


class EngineOkRoundTripTest(unittest.TestCase):
    """Proof: normal round trip through the fake provider."""

    def test_returns_a_well_formed_response_for_a_clean_request(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        response = engine.decide(request(), config=test_config(), provider=fake)
        self.assertEqual(set(response.keys()), RESPONSE_FIELDS)
        self.assertEqual(response["outcome"], "ok")
        self.assertEqual(response["provider"], "fake")
        self.assertFalse(response["fallback_used"])
        self.assertIn(response["answer"], request()["options"])
        self.assertEqual(fake.call_count, 1)

    def test_latency_ms_is_a_nonnegative_number(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        response = engine.decide(request(), config=test_config(), provider=fake)
        self.assertIsInstance(response["latency_ms"], (int, float))
        self.assertGreaterEqual(response["latency_ms"], 0)


class EngineUnavailableFallbackTest(unittest.TestCase):
    """Proof: safe fallback when the provider reports itself unavailable."""

    def test_falls_back_instead_of_raising(self) -> None:
        fake = provider_fake.FakeProvider(scenario="unavailable")
        response = engine.decide(request(), config=test_config(max_retries=0), provider=fake)
        self.assertEqual(response["outcome"], "fallback")
        self.assertTrue(response["fallback_used"])
        self.assertFalse(response["authoritative"])
        self.assertEqual(response["confidence"], 0.0)


class EngineMalformedOutputTest(unittest.TestCase):
    """Proof: rejection of malformed provider output -- fallback, never
    pass-through."""

    def test_never_passes_the_malformed_payload_through(self) -> None:
        fake = provider_fake.FakeProvider(scenario="malformed")
        response = engine.decide(request(), config=test_config(), provider=fake)
        self.assertEqual(response["outcome"], "fallback")
        self.assertTrue(response["fallback_used"])
        self.assertNotEqual(response["answer"], "not-a-number")
        self.assertNotIsInstance(response["confidence"], str)


class EngineBoundedRetryThenFallbackOnHangTest(unittest.TestCase):
    """Proof: bounded retries then fallback on a simulated hang -- never an
    unbounded wait."""

    def test_falls_back_within_a_bounded_time_budget(self) -> None:
        fake = provider_fake.FakeProvider(scenario="hang", hang_seconds=1.0)
        cfg = test_config(timeout_s=0.02, max_retries=1)
        started = time.monotonic()
        response = engine.decide(request(), config=cfg, provider=fake)
        elapsed = time.monotonic() - started

        self.assertEqual(response["outcome"], "fallback")
        self.assertTrue(response["fallback_used"])
        # 2 attempts (1 + 1 retry) bounded near 2 * timeout_s, nowhere
        # near the 1s hang.
        self.assertEqual(fake.call_count, 2)
        self.assertLess(elapsed, 0.5)


class EngineLowConfidenceTest(unittest.TestCase):
    """Proof: a low-confidence answer marked non-authoritative or
    triggering fallback."""

    def test_below_threshold_triggers_fallback(self) -> None:
        fake = provider_fake.FakeProvider(scenario="low_confidence")
        response = engine.decide(
            request(), config=test_config(confidence_threshold=0.55), provider=fake
        )
        self.assertEqual(response["outcome"], "fallback")
        self.assertTrue(response["fallback_used"])
        self.assertFalse(response["authoritative"])


class EngineSecretBlockedBeforeProviderTest(unittest.TestCase):
    """Proof: a live-secret-shaped input is blocked before reaching any
    provider."""

    # Built from short concatenated pieces so this file's source text
    # never contains a literal contiguous secret-shaped run (same
    # convention as the repo's own secret_artifact_scan fixtures).
    FIXTURE_KEY = "sk-ant-api03-" + "a" * 12 + "b" * 12

    def test_provider_is_never_dispatched_to_when_context_has_a_secret(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        secret_request = request(context="here is my key " + self.FIXTURE_KEY)
        response = engine.decide(secret_request, config=test_config(), provider=fake)

        self.assertEqual(fake.call_count, 0)
        self.assertEqual(response["outcome"], "blocked")
        self.assertTrue(response["fallback_used"])
        self.assertFalse(response["authoritative"])

    def test_provider_is_never_dispatched_to_when_an_option_has_a_secret(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        secret_request = request(options=["approve", self.FIXTURE_KEY])
        engine.decide(secret_request, config=test_config(), provider=fake)
        self.assertEqual(fake.call_count, 0)


class EngineDefaultConfigIsNonAuthoritativeTest(unittest.TestCase):
    """Proof: default config produces non-authoritative output."""

    def test_a_clean_high_confidence_answer_is_still_not_authoritative_by_default(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        response = engine.decide(request(), config=config_module.load_config(env={}), provider=fake)
        self.assertEqual(response["outcome"], "ok")
        self.assertFalse(response["authoritative"])

    def test_opting_a_decision_type_in_makes_a_clean_answer_authoritative(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        cfg = test_config(authoritative_decision_types=["triage.priority"])
        response = engine.decide(request(), config=cfg, provider=fake)
        self.assertTrue(response["authoritative"])

    def test_opt_in_never_makes_a_fallback_answer_authoritative(self) -> None:
        fake = provider_fake.FakeProvider(scenario="unavailable")
        cfg = test_config(authoritative_decision_types=["triage.priority"], max_retries=0)
        response = engine.decide(request(), config=cfg, provider=fake)
        self.assertFalse(response["authoritative"])


class EnginePrePolicyOverridesProviderTest(unittest.TestCase):
    """Proof: the pre-policy layer wins over a disagreeing provider
    answer."""

    def test_pre_policy_answer_wins_even_though_fake_provider_disagrees(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")  # would answer "low" (first option)
        override_request = {
            "schema_version": 1,
            "decision_type": "release.destructive_action",
            "options": ["approve", "deny"],
            "context": "delete the production database",
            "sensitivity": "high",
        }
        response = engine.decide(override_request, config=test_config(), provider=fake)

        self.assertEqual(response["answer"], "deny")
        self.assertEqual(response["provider"], "pre_policy")
        self.assertFalse(response["fallback_used"])
        # Pre-policy runs first and never needs the provider at all.
        self.assertEqual(fake.call_count, 0)

    def test_pre_policy_overrides_even_when_the_decision_type_is_opted_in_authoritative(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        cfg = test_config(authoritative_decision_types=["release.destructive_action"])
        override_request = {
            "schema_version": 1,
            "decision_type": "release.destructive_action",
            "options": ["approve", "deny"],
            "context": "delete the production database",
            "sensitivity": "high",
        }
        response = engine.decide(override_request, config=cfg, provider=fake)
        self.assertEqual(response["answer"], "deny")
        self.assertEqual(fake.call_count, 0)


class EngineJevNotConfiguredFallsBackTest(unittest.TestCase):
    """Proof (engine-level companion to test_provider_jev.py): the Jev
    adapter returning not-configured flows through the engine as a clean
    fallback, with zero network attempts."""

    def test_falls_back_when_jev_is_not_configured(self) -> None:
        jev = provider_jev.JevProvider(env={})
        response = engine.decide(request(), config=test_config(), provider=jev)
        self.assertEqual(response["outcome"], "not_configured")
        self.assertTrue(response["fallback_used"])
        self.assertFalse(response["authoritative"])
        self.assertEqual(jev.network_call_count, 0)


class EngineValidatesRequestTest(unittest.TestCase):
    def test_raises_request_validation_error_for_a_malformed_request(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        with self.assertRaises(schema.RequestValidationError):
            engine.decide({"schema_version": 1}, config=test_config(), provider=fake)
        self.assertEqual(fake.call_count, 0)


class EngineObservabilityIntegrationTest(unittest.TestCase):
    def test_response_can_be_turned_into_a_metadata_only_record(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        response = engine.decide(request(), config=test_config(), provider=fake)
        record = observability.build_record(response)
        self.assertEqual(
            set(record.keys()),
            {"decision_type", "provider", "latency_ms", "cost", "usage_input_tokens", "usage_output_tokens", "confidence", "fallback_used", "outcome"},
        )


if __name__ == "__main__":
    unittest.main()
