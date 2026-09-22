#!/usr/bin/env python3
"""TDD tests for the knowledge-lifecycle memory classifier (issue #167).

Every test here is offline and deterministic. The only provider ever
dispatched to is FakeProvider (from Bundle 1's decision layer), scripted
per scenario. No test makes, or can make, a network call.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
DECISION_LAYER_DIR = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(DECISION_LAYER_DIR))


def load_module(name: str, directory: Path):
    spec = importlib.util.spec_from_file_location(name, directory / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


provider_base = load_module("provider_base", DECISION_LAYER_DIR)
provider_fake = load_module("provider_fake", DECISION_LAYER_DIR)
classifier = load_module("classifier", HERE)

# Built from short concatenated pieces so the *source text* of this test
# file never contains a literal contiguous secret-shaped run for the
# repo's own pre-commit secret scanner to flag, while the *runtime
# string* still exercises real detection logic. Mirrors the convention
# already used in test_secret_filter.py.
FIXTURE_ANTHROPIC_STYLE = "sk-ant-api03-" + "a" * 12 + "b" * 12


class ClassifyDurableLessonTest(unittest.TestCase):
    def test_classifies_a_clear_durable_lesson_as_durable(self) -> None:
        candidate = {
            "content": (
                "InvoiceStatus is a PHP 8.1 backed enum; comparing it with "
                "!== string is always true, so callers must compare against "
                "InvoiceStatus::Paid instead of a raw string."
            ),
            "subject": "invoice_status_enum_guard",
            "stated_at": "2026-09-20",
        }
        result = classifier.classify_memory(candidate)
        self.assertEqual(result.classification, "durable")
        self.assertTrue(result.reason)


class ClassifySensitiveTest(unittest.TestCase):
    def test_rejects_secret_shaped_candidate_before_any_provider_is_consulted(self) -> None:
        candidate = {
            "content": "Here is the koda api key: " + FIXTURE_ANTHROPIC_STYLE,
            "subject": "koda_api_key",
        }
        # Scripted to APPROVE as durable if it were ever asked -- proves
        # the sensitive check runs and blocks *before* dispatch, not that
        # the provider happened to agree.
        approving_provider = provider_fake.FakeProvider(scenario="ok")

        result = classifier.classify_memory(candidate, provider=approving_provider)

        self.assertEqual(result.classification, "sensitive")
        self.assertEqual(approving_provider.call_count, 0)


class ClassifyEphemeralTest(unittest.TestCase):
    def test_classifies_ephemeral_status_update_as_ephemeral(self) -> None:
        candidate = {
            "content": (
                "Currently on branch feat/167-koda-lifecycle-classification "
                "in /Users/hafizrazali/Projects/Sifututor-worktrees/"
                "agent-os-167-koda-lifecycle."
            ),
            "subject": "session_state",
        }
        result = classifier.classify_memory(candidate)
        self.assertEqual(result.classification, "ephemeral")


class ClassifyDuplicateTest(unittest.TestCase):
    def test_classifies_a_near_duplicate_of_a_known_memory_as_duplicate(self) -> None:
        known_memories = [
            {
                "id": "mem_001",
                "subject": "fiuu_declined_callback",
                "content": (
                    "FIUU declined callback must map to UnPaid, always "
                    "return HTTP 200, and the guard must run before the DB "
                    "transaction opens."
                ),
                "stated_at": "2026-06-01",
            }
        ]
        candidate = {
            "subject": "fiuu_declined_callback",
            "content": (
                "FIUU declined callback should map to UnPaid, always "
                "return HTTP 200, and the guard should run before the DB "
                "transaction opens."
            ),
            "stated_at": "2026-09-15",
        }
        result = classifier.classify_memory(candidate, known_memories=known_memories)
        self.assertEqual(result.classification, "duplicate")
        self.assertEqual(result.matched_memory_id, "mem_001")


class ClassifyStaleTest(unittest.TestCase):
    def test_flags_a_fact_contradicted_by_newer_stated_information_as_stale(self) -> None:
        known_memories = [
            {
                "id": "mem_042",
                "subject": "sifu_staging_domain",
                "content": "sifu-tutor staging domain is sifu-staging.tutorla.tech on Web Voyager.",
                "stated_at": "2026-08-09",
            }
        ]
        # Older stated_at than the known memory above, and it contradicts
        # (different domain) what is already known more recently -- this
        # must be flagged for review, never silently stored as current fact.
        candidate = {
            "subject": "sifu_staging_domain",
            "content": "sifu-tutor staging domain is sims-staging.tutorla.tech on Hostinger VPS.",
            "stated_at": "2026-05-01",
        }
        result = classifier.classify_memory(candidate, known_memories=known_memories)
        self.assertEqual(result.classification, "stale")
        self.assertEqual(result.matched_memory_id, "mem_042")


if __name__ == "__main__":
    unittest.main()
