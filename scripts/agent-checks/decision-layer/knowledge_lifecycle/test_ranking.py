#!/usr/bin/env python3
"""TDD tests for the knowledge-lifecycle ranking function (issue #167).

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
ranking = load_module("ranking", HERE)

FIXTURE_ANTHROPIC_STYLE = "sk-ant-api03-" + "a" * 12 + "b" * 12


class RankCandidatesTest(unittest.TestCase):
    def test_ranks_the_most_relevant_candidate_first(self) -> None:
        candidates = [
            {"id": "mem_a", "content": "Malaysian formats: DD/MM/YYYY, Asia/KL 12h, RM currency."},
            {
                "id": "mem_b",
                "content": (
                    "Tutor payout rule: verified before the 5th pays 5th to "
                    "15th; verified after pays after the 15th; no fixed date."
                ),
            },
            {"id": "mem_c", "content": "Nakngaji is always spelled as one word."},
        ]
        ranked = ranking.rank_candidates("tutor payout verified before the 5th", candidates)
        self.assertEqual(ranked[0]["id"], "mem_b")
        self.assertEqual({c["id"] for c in ranked}, {"mem_a", "mem_b", "mem_c"})

    def test_tie_breaking_is_deterministic_across_repeated_calls(self) -> None:
        candidates = [
            {"id": "mem_z", "content": "staging deploy"},
            {"id": "mem_y", "content": "staging deploy"},
            {"id": "mem_x", "content": "staging deploy"},
        ]
        first = [c["id"] for c in ranking.rank_candidates("staging deploy", candidates)]
        second = [c["id"] for c in ranking.rank_candidates("staging deploy", candidates)]
        self.assertEqual(first, second)
        # Equal scores, same content -- deterministic tie-break falls back
        # to candidate id, ascending.
        self.assertEqual(first, ["mem_x", "mem_y", "mem_z"])

    def test_never_surfaces_a_secret_shaped_candidate(self) -> None:
        candidates = [
            {"id": "mem_safe", "content": "billing cycle rules locked 2026-06-07"},
            {"id": "mem_secret", "content": "koda api key " + FIXTURE_ANTHROPIC_STYLE},
        ]
        ranked = ranking.rank_candidates("billing cycle rules", candidates)
        self.assertEqual([c["id"] for c in ranked], ["mem_safe"])

    def test_exact_phrase_pre_policy_match_overrides_provider_entirely(self) -> None:
        candidates = [
            {"id": "mem_generic", "content": "billing cycle revamp rules"},
            {"id": "mem_exact", "content": "billing cycle rules locked 2026-06-07 PRD and US written"},
        ]
        # Scripted to prefer mem_generic if it were ever asked -- proves
        # the deterministic exact-phrase pre-policy match wins and the
        # provider is never dispatched to.
        class _AlwaysPrefersGeneric:
            name = "fake"

            def __init__(self) -> None:
                self.call_count = 0

            def dispatch(self, request):
                self.call_count += 1
                return provider_base.ProviderAnswer(answer="mem_generic", confidence=0.99)

        provider = _AlwaysPrefersGeneric()
        ranked = ranking.rank_candidates(
            "billing cycle rules locked 2026-06-07", candidates, provider=provider
        )
        self.assertEqual(ranked[0]["id"], "mem_exact")
        self.assertEqual(provider.call_count, 0)

    def test_provider_assisted_ordering_breaks_a_genuine_deterministic_tie(self) -> None:
        # Both candidates share the same 3 query tokens -> a genuine tie on
        # the deterministic score. Word order is deliberately scrambled
        # relative to the query so the exact-phrase pre-policy rule never
        # fires here (that path is covered by a separate test). Listed
        # with mem_two first to prove the provider's answer (not input
        # list order) decides the winner.
        candidates = [
            {"id": "mem_two", "content": "deploy pipeline staging sifu staging"},
            {"id": "mem_one", "content": "deploy pipeline staging sifu backport"},
        ]
        fake_provider = provider_fake.FakeProvider(scenario="ok")
        ranked = ranking.rank_candidates(
            "staging deploy pipeline", candidates, provider=fake_provider
        )
        # The tied options are offered to the provider in deterministic
        # (id-ascending) order; FakeProvider's "ok" scenario always answers
        # with the first option offered, so this proves real wiring rather
        # than a coincidence of input order.
        self.assertEqual(fake_provider.call_count, 1)
        self.assertEqual(ranked[0]["id"], "mem_one")


if __name__ == "__main__":
    unittest.main()
