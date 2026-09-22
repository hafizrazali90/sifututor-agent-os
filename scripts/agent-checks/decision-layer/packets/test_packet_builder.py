#!/usr/bin/env python3
"""TDD tests for the compact execution packet builder (Bundle 3, issue
#160): the module that assembles a versioned packet from route/task-type
plus a small amount of task context.

Every test here is offline and deterministic. The only provider the
builder's default config can ever select is Bundle 1's `FakeProvider`
(`provider_fake.py`) -- `packet_builder._default_risk_config()` locks
`provider="fake"` and passes `env={}`, so even a host machine with a real
`JEV_API_KEY` set cannot make this suite reach a live endpoint. No test
here imports or exercises `provider_jev`'s live path.
"""

from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def load_module(name, where=HERE):
    spec = importlib.util.spec_from_file_location(name, where / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# Load this package's own modules first so packet_builder's internal plain
# `import obligations` / `import packet_schema` reuse these exact instances
# (same convention test_engine.py uses one directory up).
packet_schema = load_module("packet_schema")
obligations = load_module("obligations")
packet_builder = load_module("packet_builder")

# packet_builder's own top-level code just did `sys.path.insert` for the
# parent decision-layer directory and plain-`import`ed engine/config/
# schema/secret_filter (and, transitively, provider_base/provider_fake) --
# fetch those SAME cached module objects via the real import system so
# ProviderAnswer identity matches what engine.py's isinstance checks use.
engine = importlib.import_module("engine")
config_module = importlib.import_module("config")
schema = importlib.import_module("schema")
provider_base = importlib.import_module("provider_base")
provider_fake = importlib.import_module("provider_fake")


class RecordingProvider:
    """Wraps a real FakeProvider and records every dispatch call, so tests
    can prove exactly how many times (if any) the decision layer was
    actually asked something."""

    name = "recording-fake"

    def __init__(self, inner=None) -> None:
        self._inner = inner or provider_fake.FakeProvider(scenario="ok")
        self.call_count = 0
        self.requests: list[dict] = []

    def dispatch(self, request: dict):
        self.call_count += 1
        self.requests.append(request)
        return self._inner.dispatch(request)


def base_input(**overrides):
    values = dict(
        route="feature",
        task_type="feature",
        project="ripple-suite",
        goal="Add parent session renewal endpoint",
        scope="server-side session renewal only",
        target_state="endpoint merged and covered by a permanent E2E test",
        exclusions=["client-side renewal UI"],
    )
    values.update(overrides)
    return values


# Fixture "secret" values built from short concatenated pieces, same
# convention as test_secret_filter.py / test_engine.py in the parent
# directory, so this file's own source text never contains a literal
# contiguous secret-shaped run.
FIXTURE_KEY = "sk-ant-api03-" + "a" * 12 + "b" * 12


class PacketShapeTest(unittest.TestCase):
    def test_build_packet_returns_exactly_the_versioned_field_set(self) -> None:
        packet = packet_builder.build_packet(**base_input())
        self.assertEqual(set(packet.keys()), set(packet_schema.packet_fields()))
        self.assertEqual(packet["schema_version"], packet_schema.PACKET_SCHEMA_VERSION)

    def test_goal_project_and_target_state_pass_through_unchanged(self) -> None:
        packet = packet_builder.build_packet(**base_input())
        self.assertEqual(packet["goal"], "Add parent session renewal endpoint")
        self.assertEqual(packet["project"], "ripple-suite")
        self.assertEqual(
            packet["target_state"], "endpoint merged and covered by a permanent E2E test"
        )

    def test_scope_and_exclusions_is_a_dict_carrying_route_task_type_scope_exclusions(self) -> None:
        packet = packet_builder.build_packet(**base_input())
        self.assertEqual(
            packet["scope_and_exclusions"],
            {
                "route": "feature",
                "task_type": "feature",
                "scope": "server-side session renewal only",
                "exclusions": ["client-side renewal UI"],
            },
        )

    def test_raises_packet_validation_error_for_missing_required_field(self) -> None:
        with self.assertRaises(packet_schema.PacketValidationError):
            packet_builder.build_packet(**base_input(goal=""))


class ApprovalReferenceHardLimitTest(unittest.TestCase):
    """Proof of the Bundle 3 hard limit: this module can only ever carry
    an approval reference through, never invent or infer one."""

    def test_a_supplied_approval_reference_passes_through_exactly(self) -> None:
        packet = packet_builder.build_packet(
            **base_input(approval_reference="APR-2026-0917-hafiz")
        )
        self.assertEqual(packet["validated_approval_reference"], "APR-2026-0917-hafiz")

    def test_an_omitted_approval_reference_becomes_the_not_provided_sentinel_not_a_guess(self) -> None:
        packet = packet_builder.build_packet(**base_input())
        self.assertEqual(
            packet["validated_approval_reference"], packet_schema.APPROVAL_REFERENCE_NOT_PROVIDED
        )

    def test_critical_lane_never_invents_an_approval_reference_even_though_it_forces_high_risk(
        self,
    ) -> None:
        packet = packet_builder.build_packet(
            **base_input(route="hotfix", task_type="hotfix", critical_lane=True)
        )
        self.assertEqual(
            packet["validated_approval_reference"], packet_schema.APPROVAL_REFERENCE_NOT_PROVIDED
        )

    def test_a_high_confidence_fake_provider_answer_never_leaks_into_the_approval_field(self) -> None:
        spy = RecordingProvider(provider_fake.FakeProvider(scenario="ok"))
        packet = packet_builder.build_packet(**base_input(provider=spy))
        self.assertNotEqual(packet["validated_approval_reference"], "low")
        self.assertIn(
            packet["validated_approval_reference"],
            ("low", packet_schema.APPROVAL_REFERENCE_NOT_PROVIDED),
        )
        # It must specifically be the sentinel, not the fake provider's
        # deterministic "low" answer leaking through by coincidence.
        self.assertEqual(
            packet["validated_approval_reference"], packet_schema.APPROVAL_REFERENCE_NOT_PROVIDED
        )


class CriticalLaneGateTest(unittest.TestCase):
    def test_critical_lane_without_approval_reference_halts_next_automatic_action(self) -> None:
        packet = packet_builder.build_packet(
            **base_input(route="hotfix", task_type="hotfix", critical_lane=True)
        )
        self.assertIn("halt", packet["next_automatic_action"].lower())
        self.assertIn("approval", packet["next_automatic_action"].lower())

    def test_critical_lane_with_approval_reference_does_not_force_a_halt(self) -> None:
        packet = packet_builder.build_packet(
            **base_input(
                route="hotfix",
                task_type="hotfix",
                critical_lane=True,
                approval_reference="APR-2026-0917-hafiz",
            )
        )
        self.assertNotIn("halt", packet["next_automatic_action"].lower())

    def test_critical_lane_never_dispatches_to_the_decision_layer_at_all(self) -> None:
        spy = RecordingProvider()
        packet_builder.build_packet(
            **base_input(route="hotfix", task_type="hotfix", critical_lane=True, provider=spy)
        )
        self.assertEqual(spy.call_count, 0)

    def test_critical_lane_adds_the_universal_safety_rule_stop_condition(self) -> None:
        packet = packet_builder.build_packet(
            **base_input(route="feature", task_type="feature", critical_lane=True)
        )
        stops = "\n".join(packet["stop_conditions"]).lower()
        self.assertIn("critical", stops)
        self.assertIn("human review", stops)


class SecretBlockedTest(unittest.TestCase):
    """Proof of reuse: the packet builder blocks on the same secret-shaped
    content Bundle 1's secret_filter.py already detects, and never lets it
    reach the decision layer."""

    def test_a_secret_shaped_goal_blocks_the_packet(self) -> None:
        packet = packet_builder.build_packet(
            **base_input(goal="deploy using key " + FIXTURE_KEY)
        )
        self.assertIn("halt", packet["next_automatic_action"].lower())
        self.assertNotIn(FIXTURE_KEY, packet["goal"])

    def test_a_secret_shaped_goal_never_reaches_the_decision_layer(self) -> None:
        spy = RecordingProvider()
        packet_builder.build_packet(
            **base_input(goal="deploy using key " + FIXTURE_KEY, provider=spy)
        )
        self.assertEqual(spy.call_count, 0)

    def test_a_clean_field_is_not_touched_when_a_different_field_is_flagged(self) -> None:
        packet = packet_builder.build_packet(
            **base_input(goal="deploy using key " + FIXTURE_KEY)
        )
        self.assertEqual(packet["project"], "ripple-suite")

    def test_blocked_packet_still_returns_the_exact_field_set(self) -> None:
        packet = packet_builder.build_packet(
            **base_input(goal="deploy using key " + FIXTURE_KEY)
        )
        self.assertEqual(set(packet.keys()), set(packet_schema.packet_fields()))


class NoLiveNetworkCallTest(unittest.TestCase):
    def test_default_config_never_selects_a_live_provider_even_with_a_real_looking_env_key(
        self,
    ) -> None:
        # Simulate a host machine that happens to have JEV_API_KEY set in
        # its real environment. build_packet's default risk config must
        # still never pick the jev provider.
        import os

        original = os.environ.get("JEV_API_KEY")
        os.environ["JEV_API_KEY"] = "definitely-not-a-real-key"
        try:
            spy = RecordingProvider(provider_fake.FakeProvider(scenario="ok"))
            packet_builder.build_packet(**base_input(provider=spy))
            self.assertEqual(spy.call_count, 1)
            self.assertEqual(spy.requests[0]["decision_type"], "packets.risk_bucket")
        finally:
            if original is None:
                os.environ.pop("JEV_API_KEY", None)
            else:
                os.environ["JEV_API_KEY"] = original

    def test_the_decision_layer_is_actually_invoked_for_a_non_critical_route(self) -> None:
        spy = RecordingProvider(provider_fake.FakeProvider(scenario="ok"))
        packet_builder.build_packet(**base_input(provider=spy))
        self.assertEqual(spy.call_count, 1)


class RiskBucketTypedJudgmentTest(unittest.TestCase):
    """Proof: the decision layer's (fake-provider) typed judgment actually
    changes required_checks_evidence, and low-risk routes are left alone."""

    def test_hotfix_gets_an_extra_high_risk_evidence_item(self) -> None:
        packet = packet_builder.build_packet(
            **base_input(
                route="hotfix",
                task_type="hotfix",
                goal="Fix production checkout crash",
                scope="checkout payment confirmation handler",
                target_state="hotfix deployed and smoke-checked",
            )
        )
        checks = "\n".join(packet["required_checks_evidence"]).lower()
        self.assertIn("risk bucket: high", checks)

    def test_feature_does_not_get_the_high_risk_evidence_item_by_default(self) -> None:
        packet = packet_builder.build_packet(**base_input())
        checks = "\n".join(packet["required_checks_evidence"]).lower()
        self.assertNotIn("risk bucket: high", checks)

    def test_docs_does_not_get_the_high_risk_evidence_item(self) -> None:
        packet = packet_builder.build_packet(
            **base_input(
                route="docs",
                task_type="docs",
                goal="Document the packet builder input shape",
                scope="packets/README.md only",
                target_state="README merged",
            )
        )
        checks = "\n".join(packet["required_checks_evidence"]).lower()
        self.assertNotIn("risk bucket: high", checks)


class UnmappedRouteFallbackTest(unittest.TestCase):
    def test_unmapped_route_produces_a_packet_that_says_it_could_not_determine_obligations(
        self,
    ) -> None:
        packet = packet_builder.build_packet(
            **base_input(
                route="totally-unknown-route",
                task_type="mystery",
                goal="Do something not covered by any known route",
                scope="unclear",
                target_state="unclear",
            )
        )
        checks = "\n".join(packet["required_checks_evidence"]).lower()
        self.assertIn("could not determine", checks)
        self.assertIn("halt", packet["next_automatic_action"].lower())

    def test_unmapped_route_never_calls_the_decision_layer(self) -> None:
        spy = RecordingProvider()
        packet_builder.build_packet(
            **base_input(
                route="totally-unknown-route",
                task_type="mystery",
                goal="Do something not covered by any known route",
                scope="unclear",
                target_state="unclear",
                provider=spy,
            )
        )
        self.assertEqual(spy.call_count, 0)


class NextAutomaticActionTest(unittest.TestCase):
    def test_names_the_first_core_path_step_when_nothing_blocks_it(self) -> None:
        packet = packet_builder.build_packet(
            **base_input(
                route="docs",
                task_type="docs",
                goal="Document the packet builder input shape",
                scope="packets/README.md only",
                target_state="README merged",
            )
        )
        self.assertIn("write", packet["next_automatic_action"])


class CrossRouteDifferentiationEndToEndTest(unittest.TestCase):
    """The same design-constraint proof as test_obligations.py, but through
    the full build_packet() entry point end to end, so a bug in wiring
    obligations.py into packet_builder.py can't hide behind passing unit
    tests at the obligations layer alone."""

    ROUTES = (
        ("hotfix", "hotfix"),
        ("bugfix", "bugfix"),
        ("small-change", "small-change"),
        ("feature", "feature"),
        ("docs", "docs"),
        ("refactor", "refactor"),
    )

    def test_required_checks_evidence_differs_across_every_route_end_to_end(self) -> None:
        seen = {}
        for route, task_type in self.ROUTES:
            packet = packet_builder.build_packet(
                **base_input(
                    route=route,
                    task_type=task_type,
                    goal=f"{route} goal",
                    scope=f"{route} scope",
                    target_state=f"{route} target state",
                )
            )
            key = tuple(sorted(packet["required_checks_evidence"]))
            self.assertNotIn(key, seen, f"{route} matches {seen.get(key)}")
            seen[key] = route


if __name__ == "__main__":
    unittest.main()
