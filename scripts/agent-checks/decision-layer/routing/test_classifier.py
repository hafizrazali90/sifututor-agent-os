#!/usr/bin/env python3
"""TDD tests for the routing classifier: a deterministic keyword/pattern
scorer that ranks the 11 workflow routes for a piece of free text.

`rank_workflow_routes` never calls a provider -- it produces the *options
list* that `shadow_router.py` later hands to Bundle 1's `engine.decide()`
(FakeProvider always answers `options[0]`), so this module's top pick is
what actually comes back as the shadow decision in this bundle's own test
suite. A future live classifier (Jev) would replace FakeProvider without
this module's calling contract changing.
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


catalog = load_module("catalog")
classifier = load_module("classifier")


class RankWorkflowRoutesShapeTest(unittest.TestCase):
    def test_returns_every_workflow_route_exactly_once(self) -> None:
        ranked = classifier.rank_workflow_routes("Can you explain how this works?")
        self.assertEqual(set(ranked), set(catalog.WORKFLOW_ROUTES))
        self.assertEqual(len(ranked), len(catalog.WORKFLOW_ROUTES))


class RankWorkflowRoutesTopPickTest(unittest.TestCase):
    def test_plain_question_ranks_question_first(self) -> None:
        ranked = classifier.rank_workflow_routes("Can you explain how the tutor rating average is calculated?")
        self.assertEqual(ranked[0], "question")

    def test_research_language_ranks_research_first(self) -> None:
        ranked = classifier.rank_workflow_routes(
            "Can you research whether we should evaluate TypeSafe's Jev as a "
            "typed-decision layer across Finch, Ripple and SIMS, and compare "
            "it against what we already have?"
        )
        self.assertEqual(ranked[0], "research")

    def test_bug_report_ranks_diagnosis_first(self) -> None:
        ranked = classifier.rank_workflow_routes(
            "The payout screen is broken - clicking Verify does nothing and the console shows an error"
        )
        self.assertEqual(ranked[0], "diagnosis")

    def test_build_request_ranks_implementation_first(self) -> None:
        ranked = classifier.rank_workflow_routes("Please implement a new endpoint for tutor ratings")
        self.assertEqual(ranked[0], "implementation")

    def test_review_request_ranks_review_first(self) -> None:
        ranked = classifier.rank_workflow_routes("Can you review this PR before I merge it?")
        self.assertEqual(ranked[0], "review")

    def test_qa_request_ranks_qa_first(self) -> None:
        ranked = classifier.rank_workflow_routes("Please run QA and confirm the tests are passing before I commit")
        self.assertEqual(ranked[0], "qa")

    def test_deployment_request_ranks_deployment_first(self) -> None:
        ranked = classifier.rank_workflow_routes("Deploy this to staging and then release it to production")
        self.assertEqual(ranked[0], "deployment")

    def test_handoff_request_ranks_handoff_first(self) -> None:
        ranked = classifier.rank_workflow_routes("Prepare a handoff so another agent can continue this task")
        self.assertEqual(ranked[0], "handoff")

    def test_save_session_request_ranks_save_session_first(self) -> None:
        ranked = classifier.rank_workflow_routes("Let's save session and wrap up for today")
        self.assertEqual(ranked[0], "save_session")

    def test_go_next_ranks_continuation_first(self) -> None:
        ranked = classifier.rank_workflow_routes("go next")
        self.assertEqual(ranked[0], "continuation")

    def test_what_is_next_ranks_continuation_first(self) -> None:
        ranked = classifier.rank_workflow_routes("what's next?")
        self.assertEqual(ranked[0], "continuation")

    def test_new_side_task_phrase_ranks_new_side_task_first_when_a_task_is_active(self) -> None:
        ranked = classifier.rank_workflow_routes(
            "Separately, while you're at it, can you also check why the WordPress "
            "login page is slow? Totally unrelated to what we're doing.",
            has_active_task=True,
        )
        self.assertEqual(ranked[0], "new_side_task")

    def test_new_side_task_phrase_is_not_selected_without_an_active_task(self) -> None:
        # The same "separately"/"while you're at it" phrasing without an
        # active task in progress is not a *mid-session* side task -- it's
        # just how the first message of a session happens to be phrased.
        ranked = classifier.rank_workflow_routes(
            "Separately, while you're at it, can you also check why the WordPress login page is slow?",
            has_active_task=False,
        )
        self.assertNotEqual(ranked[0], "new_side_task")


class RankWorkflowRoutesQuotedContentTest(unittest.TestCase):
    def test_a_quoted_commit_and_push_inside_a_pasted_log_does_not_rank_deployment_first(self) -> None:
        text = (
            'Here is the log a teammate pasted: "Ran the deploy: git commit -m '
            "'fix' && git push origin main\" - can you tell me why this failed?"
        )
        cleaned = classifier.deterministic.strip_quoted_and_pasted_spans(text)
        ranked = classifier.rank_workflow_routes(cleaned)
        self.assertNotEqual(ranked[0], "deployment")


class RankWorkflowRoutesFallbackTest(unittest.TestCase):
    def test_text_with_no_signal_falls_back_to_question(self) -> None:
        ranked = classifier.rank_workflow_routes("")
        self.assertEqual(ranked[0], "question")


if __name__ == "__main__":
    unittest.main()
