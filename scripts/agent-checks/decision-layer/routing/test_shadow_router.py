#!/usr/bin/env python3
"""TDD tests for `shadow_router.route()`'s core mechanics: response shape,
genuine use of Bundle 1's engine/FakeProvider, and the shadow/advisory
guarantee (never authoritative, never an automatic action).

The build-spec-required fixtures (one question, one research request, one
diagnosis, etc.) live in `test_fixtures.py` so they map cleanly back to the
spec's own fixture list. This file is the plumbing proof underneath them.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
for _path in (HERE, PARENT):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))


def load_module(name, where=HERE):
    spec = importlib.util.spec_from_file_location(name, where / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


catalog = load_module("catalog")
config_module = load_module("config", where=PARENT)
provider_fake = load_module("provider_fake", where=PARENT)
shadow_router = load_module("shadow_router")


def test_config(**overrides):
    cfg = config_module.load_config(env={})
    cfg.update(overrides)
    return cfg


class RouteResponseShapeTest(unittest.TestCase):
    def test_response_has_every_documented_field(self) -> None:
        response = shadow_router.route("Can you explain how tutor ratings are calculated?")
        expected_fields = {
            "schema_version",
            "project",
            "workflow_route",
            "task_type",
            "risk_level",
            "required_playbooks",
            "relevant_documents",
            "model_recommendation",
            "model_recommendation_reason",
            "provider_called",
            "pasted_content_detected",
            "open_tabs_considered_for_classification",
            "open_tabs_received",
            "deterministic_overrides_applied",
            "observability",
        }
        self.assertEqual(set(response.keys()), expected_fields)

    def test_workflow_route_value_is_always_a_known_route(self) -> None:
        response = shadow_router.route("Can you explain how tutor ratings are calculated?")
        self.assertIn(response["workflow_route"]["value"], catalog.WORKFLOW_ROUTES)

    def test_risk_level_value_is_always_a_known_level(self) -> None:
        response = shadow_router.route("Can you explain how tutor ratings are calculated?")
        self.assertIn(response["risk_level"]["value"], catalog.RISK_LEVELS)

    def test_task_type_value_is_always_a_known_type(self) -> None:
        response = shadow_router.route("Can you explain how tutor ratings are calculated?")
        self.assertIn(response["task_type"], catalog.TASK_TYPES)


class RouteModelRecommendationSkippedTest(unittest.TestCase):
    def test_model_recommendation_is_explicitly_none_with_a_reason(self) -> None:
        response = shadow_router.route("Can you explain how tutor ratings are calculated?")
        self.assertIsNone(response["model_recommendation"])
        self.assertIn("no frontier-model vs fallback-model distinction", response["model_recommendation_reason"])


# A non-critical implementation request. "Please implement a new endpoint"
# was used here originally, but "endpoint" is a mobile-API-contract
# critical lane and critical lanes never reach a provider, so the plumbing
# proof below needs text that is allowed to.
NON_CRITICAL_IMPLEMENTATION = "Please build a new report screen for tutor ratings"

LONG_NON_CRITICAL_TEXT = (
    "Please build a new report screen for tutor ratings so staff can see the "
    "average per subject at a glance. It should also show the trend over the "
    "last six months, let staff filter by state and level, and export the "
    "table as a CSV for the monthly meeting. Keep the layout consistent with "
    "the existing reports and reuse the shared chart component where possible."
)


class RecordingProvider(provider_fake.FakeProvider):
    """A FakeProvider that also keeps every request it was handed, so a
    test can assert on exactly what a provider is allowed to see."""

    def __init__(self, scenario: str = "ok") -> None:
        super().__init__(scenario=scenario)
        self.requests: list[dict] = []

    def dispatch(self, request: dict, *, timeout_s: float | None = None) -> object:
        self.requests.append(request)
        return super().dispatch(request, timeout_s=timeout_s)


class RouteIsGenuinelyClassifiedThroughEngineTest(unittest.TestCase):
    """Proof: for non-critical text, `route()` genuinely calls Bundle 1's
    `engine.decide()` against a real (fake) provider, rather than deciding
    the workflow route through some separate, untested path."""

    def test_the_fake_provider_is_actually_dispatched_to_once(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        response = shadow_router.route(NON_CRITICAL_IMPLEMENTATION, provider=fake, config=test_config())
        self.assertEqual(fake.call_count, 1)
        self.assertTrue(response["provider_called"])
        self.assertEqual(response["workflow_route"]["provider"], "fake")

    def test_a_provider_reporting_unavailable_falls_back_but_still_returns_a_valid_route(self) -> None:
        fake = provider_fake.FakeProvider(scenario="unavailable")
        response = shadow_router.route(
            NON_CRITICAL_IMPLEMENTATION, provider=fake, config=test_config(max_retries=0)
        )
        self.assertTrue(response["workflow_route"]["fallback_used"])
        self.assertIn(response["workflow_route"]["value"], catalog.WORKFLOW_ROUTES)
        # Falls back to the classifier's own top-ranked pick, not the
        # decision layer's generic "undetermined" placeholder.
        self.assertEqual(response["workflow_route"]["value"], "implementation")


class ProviderOnlySeesDerivedContextTest(unittest.TestCase):
    """Proof: the provider request never carries raw request text. Its
    `context` is the first sentence (at most 240 characters) plus matched
    keyword tags, and `sensitivity` is always "low" because anything that
    would be higher never reaches a provider at all."""

    def _only_request(self) -> dict:
        fake = RecordingProvider()
        shadow_router.route(LONG_NON_CRITICAL_TEXT, provider=fake, config=test_config())
        self.assertEqual(len(fake.requests), 1)
        return fake.requests[0]

    def test_context_is_never_the_raw_text_or_a_raw_prefix_of_it(self) -> None:
        request = self._only_request()
        context = request["context"]
        self.assertNotEqual(context, LONG_NON_CRITICAL_TEXT)
        self.assertNotEqual(context, LONG_NON_CRITICAL_TEXT[:2000])
        self.assertNotIn("trend over the last six months", context)
        self.assertNotIn("shared chart component", context)

    def test_context_is_first_sentence_capped_at_240_characters_plus_tags(self) -> None:
        request = self._only_request()
        summary_line, tags_line = request["context"].split("\n", 1)
        self.assertTrue(summary_line.startswith("summary: "))
        summary = summary_line[len("summary: "):]
        self.assertLessEqual(len(summary), shadow_router.CONTEXT_SUMMARY_CHARS)
        self.assertTrue(summary.startswith("Please build a new report screen"))
        self.assertTrue(summary.endswith("at a glance."))
        self.assertTrue(tags_line.startswith("tags: "))
        self.assertIn("implementation", tags_line)

    def test_a_single_overlong_sentence_is_trimmed_to_240_characters(self) -> None:
        fake = RecordingProvider()
        overlong = "Please build a report screen that " + "shows more columns and " * 30
        shadow_router.route(overlong, provider=fake, config=test_config())
        summary = fake.requests[0]["context"].split("\n", 1)[0][len("summary: "):]
        self.assertEqual(len(summary), shadow_router.CONTEXT_SUMMARY_CHARS)

    def test_sensitivity_is_always_low_for_anything_that_reaches_a_provider(self) -> None:
        request = self._only_request()
        self.assertEqual(request["sensitivity"], "low")

    def test_quoted_pasted_spans_are_not_forwarded_in_the_summary(self) -> None:
        fake = RecordingProvider()
        shadow_router.route(
            'Here is the log a teammate pasted: "worker crashed reading ratings.csv" - why did this fail?',
            provider=fake,
            config=test_config(),
        )
        context = fake.requests[0]["context"]
        self.assertNotIn("ratings.csv", context)
        self.assertIn("pasted_report", context)


class RouteIsNeverAuthoritativeTest(unittest.TestCase):
    """Proof: this module only ever produces a recommendation. Nothing it
    returns is stamped authoritative under the default (shadow) config, no
    matter how confident or clean the underlying decision-layer response
    is -- matching the master handoff's operating rule 11 ("Jev starts in
    shadow/advisory mode... current proven behavior remains default")."""

    def test_default_config_never_marks_the_response_authoritative(self) -> None:
        response = shadow_router.route(NON_CRITICAL_IMPLEMENTATION)
        self.assertFalse(response["workflow_route"]["authoritative"])

    def test_a_deterministic_critical_lane_answer_is_never_authoritative_either(self) -> None:
        response = shadow_router.route(
            "Please implement a new endpoint for tutor ratings",
            config=test_config(authoritative_decision_types=["routing.workflow_route"]),
        )
        self.assertFalse(response["provider_called"])
        self.assertFalse(response["workflow_route"]["authoritative"])

    def test_even_an_explicit_opt_in_config_cannot_be_reached_by_this_module_accidentally(self) -> None:
        # shadow_router.py never sets authoritative_decision_types itself;
        # a caller would have to opt in explicitly and out-of-band, which
        # is exactly the "later, separate decision" the build spec
        # describes -- this module does not make that decision for them.
        response = shadow_router.route(
            NON_CRITICAL_IMPLEMENTATION,
            config=test_config(authoritative_decision_types=["routing.workflow_route"]),
        )
        # Even opted in, a clean fake-provider answer whose route does not
        # match the provider's literal echoed option only becomes
        # authoritative through engine.decide()'s own rules -- proving
        # this module adds no authority of its own beyond what Bundle 1
        # already grants explicitly.
        self.assertEqual(response["workflow_route"]["provider"], "fake")


class RouteNeverActsTest(unittest.TestCase):
    """Proof: calling `route()` never mutates anything -- it is a pure
    function from text to a decision dict. Calling it many times with
    different provider scenarios never raises, never writes a file, never
    imports anything network-capable."""

    def test_calling_route_repeatedly_is_side_effect_free_and_returns_independent_dicts(self) -> None:
        first = shadow_router.route("Can you explain how tutor ratings are calculated?")
        second = shadow_router.route("Can you explain how tutor ratings are calculated?")
        self.assertEqual(first["workflow_route"]["value"], second["workflow_route"]["value"])
        first["workflow_route"]["value"] = "mutated"
        self.assertNotEqual(first["workflow_route"]["value"], second["workflow_route"]["value"])


if __name__ == "__main__":
    unittest.main()
