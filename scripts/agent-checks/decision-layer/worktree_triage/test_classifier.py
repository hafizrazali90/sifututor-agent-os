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

import ast
import importlib.util
import json
from pathlib import Path
import re
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
# Reuse the exact provider_base/engine module objects the classifier bound,
# rather than executing provider_base.py a second time under a new module
# identity: a second copy would make engine's isinstance(ProviderAnswer)
# check fail and silently turn every scripted answer into a fallback.
provider_base = classifier.provider_base
engine = classifier.engine
provider_fake = load_module("provider_fake", HERE.parent)

CLASSIFIER_SOURCE_PATH = HERE / "classifier.py"
AGGREGATE_SOURCE_PATH = HERE / "aggregate.py"


class AdversarialProvider:
    """Always answers something a real classifier must never trust blindly.

    Used only to prove the deterministic layer has final authority: it is
    never actually dispatched to for a hard-block entry.

    Matches the foundation's provider contract
    (`dispatch(request, *, timeout_s=None)`, see provider_fake.py).
    """

    name = "adversarial"

    def __init__(self) -> None:
        self.call_count = 0

    def dispatch(self, request: dict, *, timeout_s: float | None = None) -> provider_base.ProviderAnswer:
        self.call_count += 1
        return provider_base.ProviderAnswer(answer="reclaim_now", confidence=0.99)


class RecordingProvider:
    """Captures every request it is dispatched, so a test can inspect
    exactly what the classifier hands to the decision layer."""

    name = "recording"

    def __init__(self) -> None:
        self.requests: list[dict] = []

    def dispatch(self, request: dict, *, timeout_s: float | None = None) -> provider_base.ProviderAnswer:
        self.requests.append(request)
        return provider_base.ProviderAnswer(answer=request["options"][0], confidence=0.95)


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
        self.assertEqual(
            result.decision_response["outcome"],
            "ok",
            "the scripted 'ok' answer must reach the classifier as a clean "
            "provider answer, not be downgraded to a fallback",
        )
        self.assertFalse(result.decision_response["fallback_used"])
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


# Free text a person could have typed, planted on an entry to prove none of
# it ever reaches the decision-layer request. The real inventory entry does
# not carry a lease purpose at all; this covers any caller that merges one
# in, and the tool's own owner-bearing reason strings and recovery commands.
_PLANTED_PURPOSE = "PLANTED-PURPOSE fix the payout export for Kak Ros before Friday"
_PLANTED_OWNER = "PLANTED-OWNER agent-session-42"
_PLANTED_REASON = f"active lease owned by {_PLANTED_OWNER}"
_PLANTED_RECOVERY = "git -C /Users/hafizrazali/Projects/Sifututor/sifu-tutor worktree prune --expire now"


def _entry_with_planted_free_text() -> dict:
    entry = dict(fixtures.UNCERTAIN_ENTRY)
    entry["reasons"] = list(entry["reasons"]) + [_PLANTED_REASON]
    entry["recovery"] = _PLANTED_RECOVERY
    entry["lease"] = {"owner": _PLANTED_OWNER, "purpose": _PLANTED_PURPOSE}
    entry["purpose"] = _PLANTED_PURPOSE
    entry["notes"] = "PLANTED-NOTES anything else a person typed"
    return entry


class RequestContextAllowlistTest(unittest.TestCase):
    """The advisory tie-break request carries metadata only."""

    def test_request_context_keys_match_allowlist_for_every_fixture(self) -> None:
        for entry in fixtures.ALL_ENTRIES + (_entry_with_planted_free_text(),):
            with self.subTest(worktree=entry["worktree"]):
                metadata = classifier.build_request_context(entry)
                self.assertEqual(set(metadata), classifier.REQUEST_CONTEXT_ALLOWED_KEYS)

    def test_request_context_values_are_labels_booleans_counts_or_branch(self) -> None:
        for entry in fixtures.ALL_ENTRIES + (_entry_with_planted_free_text(),):
            with self.subTest(worktree=entry["worktree"]):
                metadata = classifier.build_request_context(entry)
                self.assertIsInstance(metadata["stale_lease"], bool)
                self.assertIsInstance(metadata["has_active_task"], bool)
                self.assertIsInstance(metadata["has_inherited_task_pointer"], bool)
                self.assertIsInstance(metadata["ignored_blocker_count"], int)
                self.assertNotIsInstance(metadata["ignored_blocker_count"], bool)
                self.assertIn(metadata["process_check"], ("clear", "in_use", "not_checked"))
                self.assertEqual(metadata["tool_classification"], entry["classification"])
                self.assertEqual(metadata["branch"], entry["branch"])

    def test_dispatched_request_never_carries_typed_free_text(self) -> None:
        recording = RecordingProvider()
        entry = _entry_with_planted_free_text()
        result = classifier.classify_entry(entry, provider=recording)
        self.assertEqual(result.classification, "uncertain")
        self.assertEqual(len(recording.requests), 1)
        request = recording.requests[0]

        serialized = repr(request)
        for planted in (
            _PLANTED_PURPOSE,
            _PLANTED_OWNER,
            _PLANTED_REASON,
            _PLANTED_RECOVERY,
            "PLANTED-NOTES",
            entry["worktree"],
            entry["repository"],
        ):
            self.assertNotIn(planted, serialized, f"request leaked {planted!r}")

        self.assertEqual(set(request), {"schema_version", "decision_type", "options", "context", "sensitivity"})
        self.assertEqual(request["options"], list(classifier._REQUEST_OPTIONS))
        self.assertEqual(request["decision_type"], classifier.DECISION_TYPE)

        prefix, _, json_part = request["context"].partition("metadata=")
        self.assertEqual(prefix, "worktree_triage advisory tie-break; ")
        self.assertEqual(json.loads(json_part), classifier.build_request_context(entry))

    def test_task_pointer_text_is_reduced_to_a_boolean(self) -> None:
        # A pointer that is not a substring of the (allowed) branch name, so
        # the assertion proves the pointer text itself is absent.
        entry = dict(fixtures.OBSOLETE_TASK_POINTER_ENTRY, active_task="PLANTED-TASK-POINTER-9001")
        metadata = classifier.build_request_context(entry)
        self.assertIs(metadata["has_active_task"], True)
        self.assertNotIn(entry["active_task"], json.dumps(metadata))


class ReadOnlyGuaranteeTest(unittest.TestCase):
    """Only worktree-lifecycle.py enforces the safe-close requirements;
    this module must have no way to reach a mutating action."""

    _MUTATING_CALL = re.compile(r"\b(reclaim|close|prune|rmtree)\s*\(")

    def _sources(self) -> dict[str, str]:
        return {
            path.name: path.read_text(encoding="utf-8")
            for path in (CLASSIFIER_SOURCE_PATH, AGGREGATE_SOURCE_PATH)
        }

    def test_module_source_contains_no_subprocess_or_rmtree(self) -> None:
        for name, source in self._sources().items():
            with self.subTest(module=name):
                self.assertNotIn("subprocess", source)
                self.assertNotIn("shutil", source)
                self.assertNotIn("rmtree", source)

    def test_module_source_calls_no_reclaim_close_or_prune(self) -> None:
        for name, source in self._sources().items():
            with self.subTest(module=name):
                self.assertIsNone(
                    self._MUTATING_CALL.search(source),
                    f"{name} must not call reclaim/close/prune/rmtree",
                )
                tree = ast.parse(source)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        func = node.func
                        called = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
                        self.assertNotIn(called, {"reclaim", "close", "prune", "rmtree", "remove", "unlink", "rmdir", "run", "Popen", "system"})
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        names = [alias.name for alias in node.names]
                        module = getattr(node, "module", None) or ""
                        for imported in names + [module]:
                            self.assertNotIn(imported.split(".")[0], {"subprocess", "shutil", "os"})

    def test_docstring_lists_every_safe_close_requirement(self) -> None:
        doc = classifier.__doc__ or ""
        self.assertIn("Safe-close requirements preserved", doc)
        for requirement in (
            "exact HEAD",
            "clean tracked and untracked state",
            "ignored-file safety",
            "active-task state",
            "lease ownership",
            "base containment",
            "lock/process checks",
            "no deletion based only on age or dormancy",
        ):
            self.assertIn(requirement, doc)
        self.assertIn("Only `worktree-lifecycle.py` enforces these", doc)


if __name__ == "__main__":
    unittest.main()
