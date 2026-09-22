#!/usr/bin/env python3
"""TDD tests for the route/task-type -> triggered-obligation mapping
(Bundle 3, issue #160).

Source of truth for what each route actually requires: this repo's
docs/agent-playbooks/task-router.md (route table + E2E/related-impact
steps), verify.md (project command matrix + evidence rules), qa.md (QA
tier table), and commit.md (staff documentation decision, review/risk
checkpoint). These tests assert the mapping differs correctly between
routes -- the whole point of a "triggered obligations only" packet -- and
that an unmapped route/task-type falls back safely instead of silently
omitting something a deep playbook would have required.
"""

from __future__ import annotations

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


obligations = load_module("obligations")


def joined(items) -> str:
    return "\n".join(items)


class HotfixRouteTest(unittest.TestCase):
    def test_hotfix_demands_regression_test_and_smoke(self) -> None:
        resolved = obligations.resolve_obligations("hotfix", "hotfix")
        self.assertIsNotNone(resolved)
        checks = joined(resolved.required_checks_evidence)
        self.assertIn("regression_test", checks)
        self.assertIn("smoke", checks.lower())
        self.assertIn("related_impact_audit", checks)

    def test_hotfix_requires_permanent_e2e_decision_unconditionally(self) -> None:
        resolved = obligations.resolve_obligations("hotfix", "hotfix")
        checks = joined(resolved.required_checks_evidence)
        self.assertIn("permanent E2E regression decision", checks)


class BugfixRouteTest(unittest.TestCase):
    def test_bugfix_demands_regression_test(self) -> None:
        resolved = obligations.resolve_obligations("bugfix", "bugfix")
        checks = joined(resolved.required_checks_evidence)
        self.assertIn("regression_test", checks)
        self.assertIn("related_impact_audit", checks)

    def test_bugfix_does_not_demand_hotfix_only_smoke_language(self) -> None:
        resolved = obligations.resolve_obligations("bugfix", "bugfix")
        checks = joined(resolved.required_checks_evidence)
        self.assertNotIn("focused smoke check", checks)


class FeatureRouteTest(unittest.TestCase):
    def test_feature_demands_generate_tests_and_full_qa_but_not_regression_test(self) -> None:
        resolved = obligations.resolve_obligations("feature", "feature")
        checks = joined(resolved.required_checks_evidence)
        self.assertIn("generate_tests", checks)
        self.assertIn("qa_full", checks)
        self.assertNotIn("regression_test", checks)
        self.assertNotIn("related_impact_audit", checks)

    def test_feature_requires_permanent_e2e_decision_unconditionally(self) -> None:
        resolved = obligations.resolve_obligations("feature", "feature")
        checks = joined(resolved.required_checks_evidence)
        self.assertIn("permanent E2E regression decision", checks)


class SmallChangeRouteTest(unittest.TestCase):
    def test_small_change_default_excludes_e2e_and_related_impact_and_review(self) -> None:
        resolved = obligations.resolve_obligations(
            "small-change", "small-change", user_facing=False
        )
        checks = joined(resolved.required_checks_evidence)
        self.assertNotIn("permanent E2E regression decision", checks)
        self.assertNotIn("related_impact_audit", checks)
        self.assertNotIn("review:", checks)
        self.assertNotIn("regression_test", checks)

    def test_small_change_user_facing_adds_e2e_and_related_impact(self) -> None:
        resolved = obligations.resolve_obligations(
            "small-change", "small-change", user_facing=True
        )
        checks = joined(resolved.required_checks_evidence)
        self.assertIn("permanent E2E regression decision", checks)
        self.assertIn("related_impact_audit", checks)

    def test_small_change_has_no_review_step_in_its_core_path(self) -> None:
        resolved = obligations.resolve_obligations("small-change", "small-change")
        self.assertNotIn("review", resolved.core_path)


class RefactorRouteTest(unittest.TestCase):
    def test_refactor_demands_review_but_not_regression_test_or_e2e(self) -> None:
        resolved = obligations.resolve_obligations("refactor", "refactor")
        checks = joined(resolved.required_checks_evidence)
        self.assertIn("review:", checks)
        self.assertNotIn("regression_test", checks)
        self.assertNotIn("permanent E2E regression decision", checks)
        self.assertNotIn("generate_tests", checks)


class DocsRouteTest(unittest.TestCase):
    def test_docs_only_packet_must_not_demand_a_regression_test(self) -> None:
        resolved = obligations.resolve_obligations("docs", "docs")
        checks = joined(resolved.required_checks_evidence)
        self.assertNotIn("regression_test", checks)
        self.assertNotIn("related_impact_audit", checks)
        self.assertNotIn("permanent E2E regression decision", checks)
        self.assertNotIn("review:", checks)
        self.assertNotIn("qa", checks.lower())

    def test_docs_has_the_smallest_required_checks_list_of_all_routes(self) -> None:
        docs_count = len(obligations.resolve_obligations("docs", "docs").required_checks_evidence)
        for route, task_type in (
            ("hotfix", "hotfix"),
            ("bugfix", "bugfix"),
            ("feature", "feature"),
            ("refactor", "refactor"),
        ):
            other_count = len(
                obligations.resolve_obligations(route, task_type).required_checks_evidence
            )
            self.assertLess(
                docs_count, other_count, f"docs should require fewer checks than {route}"
            )


class CrossRouteDifferentiationTest(unittest.TestCase):
    """Direct proof of the design constraint: required_context and
    required_checks_evidence actually differ between every route pair, not
    just between the two extremes (docs vs hotfix)."""

    ROUTES = (
        ("hotfix", "hotfix"),
        ("bugfix", "bugfix"),
        ("small-change", "small-change"),
        ("feature", "feature"),
        ("docs", "docs"),
        ("refactor", "refactor"),
    )

    def test_every_route_pair_has_a_distinct_required_checks_evidence_set(self) -> None:
        resolved_by_route = {
            route: obligations.resolve_obligations(route, task_type)
            for route, task_type in self.ROUTES
        }
        seen = {}
        for route, resolved in resolved_by_route.items():
            key = tuple(sorted(resolved.required_checks_evidence))
            self.assertNotIn(
                key,
                seen,
                f"{route} has an identical required_checks_evidence set to {seen.get(key)}",
            )
            seen[key] = route

    def test_every_route_pair_has_a_distinct_required_context_set(self) -> None:
        resolved_by_route = {
            route: obligations.resolve_obligations(route, task_type)
            for route, task_type in self.ROUTES
        }
        seen = {}
        for route, resolved in resolved_by_route.items():
            key = tuple(sorted(resolved.required_context))
            self.assertNotIn(
                key,
                seen,
                f"{route} has an identical required_context set to {seen.get(key)}",
            )
            seen[key] = route


class CriticalLaneFlagTest(unittest.TestCase):
    def test_critical_lane_adds_the_universal_safety_rule_halt_to_any_route(self) -> None:
        resolved = obligations.resolve_obligations("feature", "feature", critical_lane=True)
        stops = joined(resolved.stop_conditions)
        self.assertIn("critical", stops.lower())
        self.assertIn("human review", stops.lower())

    def test_non_critical_lane_does_not_add_the_critical_lane_stop_condition(self) -> None:
        resolved = obligations.resolve_obligations("feature", "feature", critical_lane=False)
        stops = joined(resolved.stop_conditions)
        self.assertNotIn("critical-lane", stops.lower())


class StaffFacingFlagTest(unittest.TestCase):
    def test_staff_facing_adds_the_release_documentation_context_item(self) -> None:
        resolved = obligations.resolve_obligations("feature", "feature", staff_facing=True)
        context = joined(resolved.required_context)
        self.assertIn("staff documentation", context.lower())


class DeepPlaybookPointerTest(unittest.TestCase):
    def test_every_mapped_route_points_back_at_the_owning_deep_playbooks(self) -> None:
        for route, task_type in CrossRouteDifferentiationTest.ROUTES:
            resolved = obligations.resolve_obligations(route, task_type)
            self.assertTrue(resolved.deep_playbook_refs)
            for ref in resolved.deep_playbook_refs:
                self.assertTrue(ref.startswith("docs/agent-playbooks/"))


class UnmappedRouteFallbackTest(unittest.TestCase):
    """Proof: a route/task-type this module has no mapping for falls back
    safely -- it must say it could not determine obligations, point at the
    deep playbook, and never silently omit something by pretending an empty
    checklist is a real answer."""

    def test_unmapped_route_returns_none_from_resolve(self) -> None:
        self.assertIsNone(obligations.resolve_obligations("totally-unknown-route", "mystery"))

    def test_fallback_obligations_says_it_could_not_determine_and_points_at_playbooks(self) -> None:
        fallback = obligations.fallback_obligations("totally-unknown-route", "mystery")
        checks = joined(fallback.required_checks_evidence)
        self.assertIn("could not determine", checks.lower())
        self.assertTrue(fallback.deep_playbook_refs)
        for ref in fallback.deep_playbook_refs:
            self.assertTrue(ref.startswith("docs/agent-playbooks/"))

    def test_fallback_never_produces_an_empty_checklist(self) -> None:
        fallback = obligations.fallback_obligations("totally-unknown-route", "mystery")
        self.assertTrue(fallback.required_checks_evidence)
        self.assertTrue(fallback.required_context)
        self.assertTrue(fallback.stop_conditions)


if __name__ == "__main__":
    unittest.main()
