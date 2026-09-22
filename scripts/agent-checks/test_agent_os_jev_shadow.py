#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import agent_os_jev_shadow as shadow
import provider_base


class RecordingProvider:
    name = "jev"

    def __init__(self, answer="implementation", confidence=0.91):
        self.answer = answer
        self.confidence = confidence
        self.calls = []
        self.network_call_count = 0

    def dispatch(self, request, *, timeout_s=None):
        self.calls.append(request)
        self.network_call_count += 1
        return provider_base.ProviderAnswer(answer=self.answer, confidence=self.confidence)


class JevShadowTests(unittest.TestCase):
    def test_live_timeout_covers_measured_provider_latency_without_retrying(self):
        config = shadow.shadow_config({})
        self.assertEqual(config["timeout_s"], 3.0)
        self.assertEqual(config["max_retries"], 0)

    def test_missing_credential_falls_back_without_advice(self):
        with tempfile.TemporaryDirectory() as tmp:
            advice = shadow.observe_prompt(
                "Please implement the workflow helper",
                env={"PATH": "/usr/bin"},
                conf_path=Path(tmp) / "missing.conf",
                state_dir=Path(tmp) / "state",
            )
            self.assertEqual(advice, "")
            metrics = json.loads(next((Path(tmp) / "state").glob("*.json")).read_text())
            self.assertEqual(metrics["outcomes"], {"not_configured": 1})
            self.assertEqual(metrics["network_calls"], 0)

    def test_default_success_returns_bounded_routing_assist_and_stores_metadata_only(self):
        provider = RecordingProvider()
        prompt = "Please implement the workflow helper for ripple-suite"
        with tempfile.TemporaryDirectory() as tmp:
            advice = shadow.observe_prompt(
                prompt, project="ripple-suite", env={"PATH": "/usr/bin"}, state_dir=Path(tmp), provider=provider
            )
            self.assertIn("Jev routing assist", advice)
            self.assertIn("cannot approve or execute actions", advice)
            persisted = next(Path(tmp).glob("*.json")).read_text()
            self.assertNotIn(prompt, persisted)
            self.assertNotIn("ripple-suite", persisted)
            self.assertNotIn("implementation", persisted)
            self.assertEqual(provider.calls[0]["sensitivity"], "low")

    def test_explicit_shadow_mode_keeps_observation_only_wording(self):
        provider = RecordingProvider()
        with tempfile.TemporaryDirectory() as tmp:
            advice = shadow.observe_prompt(
                "Please implement the workflow helper",
                env={"PATH": "/usr/bin", "SIFUTUTOR_JEV_MODE": "shadow"},
                state_dir=Path(tmp),
                provider=provider,
            )
            self.assertIn("Jev shadow advisory", advice)
            self.assertIn("advisory only", advice)

    def test_assist_mode_never_opts_a_decision_type_into_authority(self):
        config = shadow.shadow_config({"SIFUTUTOR_JEV_MODE": "assist"})
        self.assertEqual(config["authoritative_decision_types"], [])

    def test_unknown_explicit_mode_fails_safe_to_shadow(self):
        provider = RecordingProvider()
        with tempfile.TemporaryDirectory() as tmp:
            advice = shadow.observe_prompt(
                "Please implement the workflow helper",
                env={"PATH": "/usr/bin", "SIFUTUTOR_JEV_MODE": "typo"},
                state_dir=Path(tmp),
                provider=provider,
            )
            self.assertIn("Jev shadow advisory", advice)
            self.assertNotIn("Jev routing assist", advice)

    def test_critical_lane_never_calls_provider(self):
        provider = RecordingProvider()
        with tempfile.TemporaryDirectory() as tmp:
            advice = shadow.observe_prompt(
                "Deploy the payment migration to production",
                env={"PATH": "/usr/bin"}, state_dir=Path(tmp), provider=provider
            )
            self.assertEqual(advice, "")
            self.assertEqual(provider.calls, [])
            metrics = json.loads(next(Path(tmp).glob("*.json")).read_text())
            self.assertEqual(metrics["critical_local_only"], 1)

    def test_owner_only_conf_is_accepted_but_permissive_conf_is_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            conf = Path(tmp) / "typesafe-jev.conf"
            conf.write_text("TYPESAFE_API_KEY=hidden-value\n")
            conf.chmod(0o600)
            self.assertEqual(shadow.provider_environment({}, conf)["TYPESAFE_API_KEY"], "hidden-value")
            conf.chmod(0o644)
            self.assertNotIn("TYPESAFE_API_KEY", shadow.provider_environment({}, conf))

    def test_explicit_disable_skips_without_writing_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            advice = shadow.observe_prompt(
                "Please implement the workflow helper", env={"SIFUTUTOR_JEV_MODE": "off"}, state_dir=Path(tmp)
            )
            self.assertEqual(advice, "")
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_legacy_shadow_disable_still_turns_jev_off(self):
        with tempfile.TemporaryDirectory() as tmp:
            advice = shadow.observe_prompt(
                "Please implement the workflow helper", env={"SIFUTUTOR_JEV_SHADOW": "0"}, state_dir=Path(tmp)
            )
            self.assertEqual(advice, "")
            self.assertEqual(list(Path(tmp).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
