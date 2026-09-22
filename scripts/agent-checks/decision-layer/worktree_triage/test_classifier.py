#!/usr/bin/env python3
"""TDD tests for worktree_triage.classifier: bounded cleanup-priority
classification on top of `worktree-lifecycle.py inventory` output.

Every test here is offline and deterministic. The only provider ever
actually dispatched to is a scripted fake (either Bundle 1's
provider_fake.FakeProvider or a small adversarial stand-in defined in this
file) -- no test makes, or can make, a network call. No test creates,
reads, or mutates any real git worktree; every fixture entry is synthetic
(see fixtures.py).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def load_module(name, directory=HERE):
    spec = importlib.util.spec_from_file_location(name, directory / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


classifier = load_module("classifier")
fixtures = load_module("fixtures")
provider_base = load_module("provider_base", HERE.parent)
provider_fake = load_module("provider_fake", HERE.parent)


class AdversarialProvider:
    """Always answers something a real classifier must never trust blindly.

    Used only to prove the deterministic layer has final authority: it is
    never actually dispatched to for a hard-block entry.
    """

    name = "adversarial"

    def __init__(self) -> None:
        self.call_count = 0

    def dispatch(self, request: dict) -> provider_base.ProviderAnswer:
        self.call_count += 1
        return provider_base.ProviderAnswer(answer="reclaim_now", confidence=0.99)


class StaleLeaseClassificationTest(unittest.TestCase):
    def test_stale_lease_entry_classifies_as_stale_lease(self) -> None:
        result = classifier.classify_entry(fixtures.STALE_LEASE_ENTRY)
        self.assertEqual(result.classification, "stale_lease")
        self.assertTrue(result.determinable)
        self.assertIn("heartbeat", result.reason)


class HardBlockPreserveClassificationTest(unittest.TestCase):
    def test_active_lease_entry_classifies_as_preserve(self) -> None:
        result = classifier.classify_entry(fixtures.ACTIVE_LEASE_ENTRY)
        self.assertEqual(result.classification, "preserve")

    def test_active_lease_entry_never_dispatches_a_provider(self) -> None:
        adversarial = AdversarialProvider()
        result = classifier.classify_entry(
            fixtures.ACTIVE_LEASE_ENTRY, provider=adversarial
        )
        self.assertEqual(result.classification, "preserve")
        self.assertEqual(
            adversarial.call_count,
            0,
            "the deterministic pre-policy layer must have final authority: "
            "an actively-leased worktree must never be routed to a provider "
            "at all, regardless of what that provider would have guessed",
        )


class ObsoleteTaskPointerClassificationTest(unittest.TestCase):
    def test_stale_completed_freshness_evidence_classifies_obsolete(self) -> None:
        entry = fixtures.OBSOLETE_TASK_POINTER_ENTRY
        freshness = fixtures.OBSOLETE_TASK_POINTER_FRESHNESS[entry["worktree"]]
        result = classifier.classify_entry(entry, task_freshness=freshness)
        self.assertEqual(result.classification, "obsolete_task_pointer")
        self.assertTrue(result.determinable)
        self.assertEqual(result.source, "task_freshness_evidence")

    def test_active_freshness_evidence_keeps_it_preserved(self) -> None:
        entry = fixtures.ACTIVE_TASK_POINTER_ENTRY
        freshness = fixtures.ACTIVE_TASK_POINTER_FRESHNESS[entry["worktree"]]
        result = classifier.classify_entry(entry, task_freshness=freshness)
        self.assertEqual(result.classification, "preserve")

    def test_missing_freshness_evidence_is_preserved_not_guessed(self) -> None:
        entry = fixtures.UNDETERMINABLE_TASK_POINTER_ENTRY
        result = classifier.classify_entry(entry)
        self.assertEqual(result.classification, "preserve")
        self.assertFalse(
            result.determinable,
            "no task-freshness evidence was supplied; the module must say so "
            "honestly rather than guess obsolete/not-obsolete",
        )
        self.assertIn("not determinable", result.reason)


class ReclaimCandidateClassificationTest(unittest.TestCase):
    def test_generated_dependency_note_classifies_as_generated_dependency_blocker(self) -> None:
        result = classifier.classify_entry(fixtures.GENERATED_DEPENDENCY_BLOCKER_ENTRY)
        self.assertEqual(result.classification, "generated_dependency_blocker")

    def test_plain_reclaim_candidate_classifies_as_merged_branch(self) -> None:
        result = classifier.classify_entry(fixtures.MERGED_BRANCH_ENTRY)
        self.assertEqual(result.classification, "merged_branch")


class UncertainClassificationTest(unittest.TestCase):
    def test_prunable_registration_routes_through_decision_layer_as_uncertain(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        result = classifier.classify_entry(fixtures.UNCERTAIN_ENTRY, provider=fake)
        self.assertEqual(result.classification, "uncertain")
        self.assertTrue(result.provider_dispatched)
        self.assertEqual(fake.call_count, 1)
        self.assertIsNotNone(result.decision_response)
        self.assertFalse(
            result.decision_response["authoritative"],
            "the decision-layer tie-break must stay advisory/shadow, never "
            "authoritative, for this bundle's default config",
        )

    def test_uncertain_stays_uncertain_even_when_provider_says_something_else(self) -> None:
        """The final bucket for an uncertain entry is always "uncertain" --
        a provider's guess is recorded for context only, never used to
        silently reclassify the entry as safe."""
        adversarial = AdversarialProvider()
        result = classifier.classify_entry(fixtures.UNCERTAIN_ENTRY, provider=adversarial)
        self.assertEqual(result.classification, "uncertain")
        self.assertEqual(adversarial.call_count, 1)


class MalformedEntryTest(unittest.TestCase):
    def test_entry_missing_required_fields_raises_rather_than_guesses(self) -> None:
        with self.assertRaises(ValueError):
            classifier.classify_entry({"branch": "main"})


if __name__ == "__main__":
    unittest.main()
