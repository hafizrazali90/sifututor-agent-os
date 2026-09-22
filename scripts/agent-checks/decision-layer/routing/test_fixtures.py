#!/usr/bin/env python3
"""Bundle 2 build-spec fixtures for `shadow_router.route()`.

Every test class in this file corresponds to one required fixture from
`.agent-os/handoffs/bundle-2-build-spec.md`'s "Fixtures required" section
(each concrete input -> expected shadow decision). The class docstring
names which fixture it covers; PR body references these exact test names.

All 14 listed scenarios plus the one named regression fixture (the real
Jev research/discussion request that was previously misrouted as a
handoff) are covered here. No test in this file makes or can make a
network call -- every call to `shadow_router.route()` either uses the
default (FakeProvider "ok") config or an explicitly scripted FakeProvider.
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


shadow_router = load_module("shadow_router")
provider_fake = load_module("provider_fake", where=PARENT)
config_module = load_module("config", where=PARENT)


def test_config(**overrides):
    cfg = config_module.load_config(env={})
    cfg.update(overrides)
    return cfg


# --- 1. A plain question -----------------------------------------------


class Fixture01PlainQuestionTest(unittest.TestCase):
    """Build spec fixture: "a plain question"."""

    def test_plain_question_routes_to_question_with_low_risk_and_no_playbooks(self) -> None:
        response = shadow_router.route("Can you explain how the tutor rating average is calculated?")
        self.assertEqual(response["workflow_route"]["value"], "question")
        self.assertEqual(response["risk_level"]["value"], "low")
        self.assertEqual(response["required_playbooks"], [])


# --- 2. A research request ------------------------------------------------


class Fixture02ResearchRequestTest(unittest.TestCase):
    """Build spec fixture: "a research request"."""

    def test_research_request_routes_to_research(self) -> None:
        response = shadow_router.route(
            "Can you research whether we should evaluate a typed-decision "
            "provider for message triage, and compare it against what we "
            "already have?"
        )
        self.assertEqual(response["workflow_route"]["value"], "research")
        self.assertIn(
            "docs/agent-playbooks/mission-ledger.md",
            response["required_playbooks"],
        )


# --- 3. A diagnosis / bug report ------------------------------------------


class Fixture03DiagnosisBugReportTest(unittest.TestCase):
    """Build spec fixture: "a diagnosis/bug report"."""

    def test_bug_report_routes_to_diagnosis_with_bugfix_task_type(self) -> None:
        response = shadow_router.route(
            "The payout screen is broken - clicking Verify does nothing and the console shows an error"
        )
        self.assertEqual(response["workflow_route"]["value"], "diagnosis")
        self.assertEqual(response["task_type"], "bugfix")


# --- 4. An implementation request -----------------------------------------


class Fixture04ImplementationRequestTest(unittest.TestCase):
    """Build spec fixture: "an implementation request"."""

    def test_implementation_request_routes_to_implementation(self) -> None:
        response = shadow_router.route("Please implement a new endpoint for tutor ratings")
        self.assertEqual(response["workflow_route"]["value"], "implementation")
        self.assertIn("docs/agent-playbooks/commit.md", response["required_playbooks"])


# --- 5. A review request ---------------------------------------------------


class Fixture05ReviewRequestTest(unittest.TestCase):
    """Build spec fixture: "a review request"."""

    def test_review_request_routes_to_review(self) -> None:
        response = shadow_router.route("Can you review this PR before I merge it?")
        self.assertEqual(response["workflow_route"]["value"], "review")
        self.assertIn("docs/agent-playbooks/verify.md", response["required_playbooks"])


# --- 6. A QA request ---------------------------------------------------


class Fixture06QaRequestTest(unittest.TestCase):
    """Build spec fixture: "a QA request"."""

    def test_qa_request_routes_to_qa(self) -> None:
        response = shadow_router.route("Please run QA and confirm the tests are passing before I commit")
        self.assertEqual(response["workflow_route"]["value"], "qa")
        self.assertIn("docs/agent-playbooks/qa.md", response["required_playbooks"])


# --- 7. A deployment request ------------------------------------------------


class Fixture07DeploymentRequestTest(unittest.TestCase):
    """Build spec fixture: "a deployment request"."""

    def test_deployment_request_routes_to_deployment_with_high_risk(self) -> None:
        response = shadow_router.route("Deploy this to staging and then release it to production")
        self.assertEqual(response["workflow_route"]["value"], "deployment")
        self.assertEqual(response["risk_level"]["value"], "high")


# --- 8. A payment/auth-touching request: deterministic critical risk ----


class Fixture08PaymentAuthCriticalRiskTest(unittest.TestCase):
    """Build spec fixture: "a payment/auth-touching request (must classify
    as critical/high-risk deterministically)". Proves the risk override is
    deterministic -- it fires even when the FakeProvider is scripted to be
    confidently wrong about everything else, because it never even reaches
    the provider."""

    def test_payment_language_forces_critical_risk_regardless_of_workflow_route(self) -> None:
        response = shadow_router.route("Please refund this parent's invoice from last month, they were overcharged")
        self.assertEqual(response["risk_level"]["value"], "critical")
        self.assertTrue(response["risk_level"]["forced"])
        self.assertTrue(
            any(item.startswith("risk_override:") for item in response["deterministic_overrides_applied"])
        )

    def test_auth_language_forces_critical_risk_too(self) -> None:
        response = shadow_router.route("Can you change how tutor login sessions expire?")
        self.assertEqual(response["risk_level"]["value"], "critical")

    def test_migration_language_forces_critical_risk_too(self) -> None:
        response = shadow_router.route("Write a migration to add a new column to the invoices table")
        self.assertEqual(response["risk_level"]["value"], "critical")

    def test_critical_override_holds_even_against_a_confidently_wrong_provider(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        response = shadow_router.route(
            "Please refund this parent's invoice from last month",
            provider=fake,
            config=test_config(),
        )
        self.assertEqual(response["risk_level"]["value"], "critical")


# --- 9. A handoff hand-off -------------------------------------------------


class Fixture09HandoffTest(unittest.TestCase):
    """Build spec fixture: "a handoff hand-off"."""

    def test_handoff_request_routes_to_handoff_and_looks_up_the_handoff_file(self) -> None:
        response = shadow_router.route("Prepare a handoff so another agent can continue this task from here")
        self.assertEqual(response["workflow_route"]["value"], "handoff")
        self.assertIn("docs/agent-playbooks/save-session.md", response["required_playbooks"])
        self.assertTrue(any(doc["type"] == "handoff_file" for doc in response["relevant_documents"]))


# --- 10. A save-session request ---------------------------------------------


class Fixture10SaveSessionTest(unittest.TestCase):
    """Build spec fixture: "a save-session request"."""

    def test_save_session_request_routes_to_save_session(self) -> None:
        response = shadow_router.route("Let's save session and wrap up for today")
        self.assertEqual(response["workflow_route"]["value"], "save_session")
        self.assertIn("docs/agent-playbooks/save-session.md", response["required_playbooks"])


# --- 11. A "go next" continuation --------------------------------------------


class Fixture11GoNextContinuationTest(unittest.TestCase):
    """Build spec fixture: '"go next" continuation'."""

    def test_go_next_routes_to_continuation(self) -> None:
        response = shadow_router.route("go next")
        self.assertEqual(response["workflow_route"]["value"], "continuation")

    def test_whats_next_routes_to_continuation(self) -> None:
        response = shadow_router.route("What's next on the build prompt list?")
        self.assertEqual(response["workflow_route"]["value"], "continuation")


# --- 12. A pasted report/log; quoted commit/push is not a live instruction --


class Fixture12PastedReportQuotedInstructionTest(unittest.TestCase):
    """Build spec fixture: 'a pasted report/log (verify a quoted "commit"/
    "push" inside pasted text is not read as a live instruction -- see
    AGENTS.md's GitHub Issue Automation section for this exact rule)'."""

    def test_a_quoted_commit_and_push_inside_a_pasted_log_is_not_routed_as_deployment_or_implementation(
        self,
    ) -> None:
        text = (
            'Here is the log a teammate pasted: "Ran the deploy: git commit -m '
            "'fix' && git push origin main\" - can you tell me why this failed?"
        )
        response = shadow_router.route(text)
        self.assertNotIn(response["workflow_route"]["value"], ("deployment", "implementation"))
        self.assertTrue(response["pasted_content_detected"])


# --- 13. IDE-tab-contamination scenario -------------------------------------


class Fixture13IdeTabContaminationTest(unittest.TestCase):
    """Build spec fixture: "an IDE-tab-contamination scenario (irrelevant
    open-file context should not hijack routing)"."""

    def test_open_tabs_naming_payments_and_auth_files_do_not_escalate_an_unrelated_question(self) -> None:
        response = shadow_router.route(
            "Can you explain how the tutor rating average is calculated?",
            open_tabs=["payments/RefundController.php", "auth/LoginController.php"],
        )
        self.assertEqual(response["workflow_route"]["value"], "question")
        self.assertEqual(response["risk_level"]["value"], "low")
        self.assertFalse(response["risk_level"]["forced"])
        self.assertFalse(response["open_tabs_considered_for_classification"])
        self.assertEqual(
            response["open_tabs_received"],
            ["payments/RefundController.php", "auth/LoginController.php"],
        )

    def test_open_tabs_do_not_override_an_explicitly_declared_project(self) -> None:
        response = shadow_router.route(
            "ripple-suite work - why does the Luna intent classifier keep misfiring",
            open_tabs=["sifu-tutor/app/Services/PayoutService.php"],
        )
        self.assertEqual(response["project"]["value"], "ripple-suite")


# --- 14. A genuinely new side task appearing mid-session --------------------


class Fixture14NewSideTaskMidSessionTest(unittest.TestCase):
    """Build spec fixture: "a genuinely new side task appearing mid-
    session"."""

    def test_a_side_task_phrase_with_an_active_task_in_progress_routes_to_new_side_task(self) -> None:
        response = shadow_router.route(
            "Separately, while you're at it, can you also check why the WordPress "
            "login page is slow? Totally unrelated to what we're doing.",
            has_active_task=True,
        )
        self.assertEqual(response["workflow_route"]["value"], "new_side_task")
        self.assertIn("docs/agent-playbooks/task-router.md", response["required_playbooks"])

    def test_the_same_phrase_without_an_active_task_is_not_treated_as_a_side_task(self) -> None:
        response = shadow_router.route(
            "Separately, while you're at it, can you also check why the WordPress login page is slow?",
            has_active_task=False,
        )
        self.assertNotEqual(response["workflow_route"]["value"], "new_side_task")


# --- 15. Named regression: Jev research/discussion misrouted as handoff -----


class Fixture15JevResearchMisroutedAsHandoffRegressionTest(unittest.TestCase):
    """Named regression fixture from the build spec: "the specific real
    incident the handoff calls out: a Jev research/discussion request was
    previously misrouted as a handoff". Reproduces the shape of the real
    2026-09-20 session recorded as Mission Ledger JEV-EVAL-001
    (`docs/agent-playbooks/mission-ledger/cross-project.md`): a request to
    research/evaluate TypeSafe's Jev across Finch/Ripple/SIMS, with deep
    analysis and reference artifacts as the deliverable -- not a handoff to
    another agent."""

    def test_jev_research_discussion_request_routes_to_research_not_handoff(self) -> None:
        text = (
            "Can we research TypeSafe's Jev as a typed-decision layer across "
            "Finch, Ripple and SIMS? I want a deep analysis session: evaluate "
            "its calibration claims, compare it against what we've already "
            "hand-rolled in Ripple's Luna classifiers, and figure out where it "
            "would make the most sense to pilot first."
        )
        response = shadow_router.route(text)
        self.assertEqual(response["workflow_route"]["value"], "research")
        self.assertNotEqual(response["workflow_route"]["value"], "handoff")


if __name__ == "__main__":
    unittest.main()
