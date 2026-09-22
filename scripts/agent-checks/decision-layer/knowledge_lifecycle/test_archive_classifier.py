#!/usr/bin/env python3
"""TDD tests for the Session Map archive classifier (issue #167).

The classifier's "propose archive" output must never by itself cause a
deletion or mutation. This is encoded structurally: `ArchiveProposal` is a
frozen dataclass carrying only a proposal value, with no delete/apply
capability. A real archive action requires a separate deterministic
reference/state check, stubbed here and never called by the classifier.
"""

from __future__ import annotations

import copy
import dataclasses
import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def load_module(name: str, directory: Path):
    spec = importlib.util.spec_from_file_location(name, directory / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


archive_classifier = load_module("archive_classifier", HERE)


class ClassifyForArchiveTest(unittest.TestCase):
    def test_proposes_archive_for_a_done_and_inactive_entry(self) -> None:
        entry = {
            "id": "session_map_042",
            "title": "sims-staging to finch migration",
            "status": "done",
            "last_touched_at": "2026-07-01",
        }
        result = archive_classifier.classify_for_archive(entry, today="2026-09-22")
        self.assertEqual(result.proposal, "propose_archive")
        self.assertTrue(result.reason)

    def test_keeps_an_active_entry_active(self) -> None:
        entry = {
            "id": "session_map_100",
            "title": "koda lifecycle classification build",
            "status": "in_progress",
            "last_touched_at": "2026-09-21",
        }
        result = archive_classifier.classify_for_archive(entry, today="2026-09-22")
        self.assertEqual(result.proposal, "keep_active")

    def test_keeps_a_recently_done_entry_active_pending_a_cooldown(self) -> None:
        entry = {
            "id": "session_map_101",
            "title": "just finished today",
            "status": "done",
            "last_touched_at": "2026-09-21",
        }
        result = archive_classifier.classify_for_archive(entry, today="2026-09-22")
        self.assertEqual(result.proposal, "keep_active")


class ArchiveProposalStructuralSafetyTest(unittest.TestCase):
    def test_proposal_type_has_no_mutation_capability(self) -> None:
        entry = {
            "id": "session_map_042",
            "status": "done",
            "last_touched_at": "2026-07-01",
        }
        result = archive_classifier.classify_for_archive(entry, today="2026-09-22")

        # Structural fact: the return type is a plain frozen dataclass with
        # only a proposal/reason/confidence value -- no method that could
        # delete, apply, or otherwise mutate anything.
        self.assertTrue(dataclasses.is_dataclass(result))
        field_names = {f.name for f in dataclasses.fields(result)}
        self.assertEqual(field_names, {"proposal", "reason", "confidence"})
        for forbidden in ("delete", "apply", "archive", "mutate", "execute"):
            self.assertFalse(hasattr(result, forbidden))
        with self.assertRaises(dataclasses.FrozenInstanceError):
            result.proposal = "propose_archive"  # type: ignore[misc]

    def test_classification_alone_never_mutates_the_entry_or_any_external_store(self) -> None:
        entry = {
            "id": "session_map_042",
            "status": "done",
            "last_touched_at": "2026-07-01",
        }
        entry_before = copy.deepcopy(entry)
        archive_store: list[str] = []
        archive_store_before = list(archive_store)

        for _ in range(5):
            result = archive_classifier.classify_for_archive(entry, today="2026-09-22")
            self.assertEqual(result.proposal, "propose_archive")

        self.assertEqual(entry, entry_before)
        self.assertEqual(archive_store, archive_store_before)


class ReferenceCheckStubTest(unittest.TestCase):
    def test_reference_check_is_an_unimplemented_stub_never_called_by_the_classifier(self) -> None:
        # Documents the contract: a later bundle or explicit human step
        # must implement real reference/state checking before any code
        # path is allowed to actually archive an entry. Until then this
        # stub refuses to silently approve anything.
        with self.assertRaises(NotImplementedError):
            archive_classifier.check_references_before_archive({"id": "session_map_042"}, reference_index={})


if __name__ == "__main__":
    unittest.main()
