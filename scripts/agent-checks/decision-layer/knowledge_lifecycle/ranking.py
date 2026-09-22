#!/usr/bin/env python3
"""Knowledge-lifecycle candidate ranking (issue #167, Bundle 6).

Given a list of candidate memories retrieved for a query, produce a
relevance-ordered list instead of returning everything. This module only
ranks; it never stores, deletes, or mutates a candidate.

NOT WIRED. This function is not called from any retrieval path. Koda's
own `memory_search` ranking, the memory-flush hooks, and every session-map
flow are unchanged by this bundle. It is a standalone, tested function a
later bundle may choose to place in front of a retrieval result; until
then it changes nothing about what any agent actually sees.

Pipeline, in order, for every call to `rank_candidates`:

1. Deterministic sensitive/PII filter (Bundle 1's `secret_filter`, reused
   not reimplemented). A secret-shaped candidate is dropped before scoring
   and never surfaced, regardless of provider.
2. Deterministic relevance score per remaining candidate: shared word
   tokens between the query and the candidate's content.
3. Deterministic pre-policy: if the query text appears verbatim (case-
   insensitive, whitespace-normalized) inside a candidate's content, that
   candidate is the forced top result and no provider is ever consulted --
   pre-policy always overrides a provider's opinion, exactly like
   `pre_policy.py` overrides a provider in the decision-layer engine.
4. Otherwise, when the deterministic top score is tied across two or more
   candidates AND a `provider` was supplied, the provider is offered the
   tied candidate ids (in deterministic, id-ascending order) and its
   answer -- if well-formed and confident enough -- decides which of the
   tied candidates leads. A provider error, malformed answer, or low
   confidence answer is ignored and the deterministic order (id-ascending)
   is used instead.
5. Every remaining tie (elsewhere in the list, or once the provider step
   above is done) is broken deterministically: score descending, then id
   ascending.
"""

from __future__ import annotations

import importlib
from pathlib import Path
import re
import sys

_HERE = Path(__file__).resolve().parent
_DECISION_LAYER_DIR = _HERE.parent


def _load_sibling_module(name: str):
    """Import a sibling decision-layer module by its plain name so the
    `ProviderAnswer` / `ProviderError` classes are the same objects the
    providers themselves use (an aliased path-load would make `isinstance`
    and `except` silently never match)."""
    if name in sys.modules:
        return sys.modules[name]
    if str(_DECISION_LAYER_DIR) not in sys.path:
        sys.path.insert(0, str(_DECISION_LAYER_DIR))
    return importlib.import_module(name)


secret_filter = _load_sibling_module("secret_filter")
provider_base = _load_sibling_module("provider_base")

PROVIDER_CONFIDENCE_THRESHOLD = 0.55

_WORD_PATTERN = re.compile(r"[a-z0-9.]+")


def _tokens(text: str) -> set[str]:
    return set(_WORD_PATTERN.findall(text.lower()))


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _score(query_tokens: set[str], candidate: dict) -> int:
    return len(query_tokens & _tokens(str(candidate.get("content") or "")))


def _is_sensitive(candidate: dict) -> bool:
    return bool(secret_filter.scan(str(candidate.get("content") or "")))


def _ask_provider_to_break_tie(query: str, tied: list[dict], provider: object) -> dict | None:
    tied_by_id = sorted(tied, key=lambda c: str(c.get("id")))
    request = {
        "schema_version": 1,
        "decision_type": "knowledge_lifecycle.rank",
        "options": [str(c.get("id")) for c in tied_by_id],
        "context": query,
        "sensitivity": "low",
    }
    try:
        raw = provider.dispatch(request)
    except provider_base.ProviderError:
        return None
    try:
        raw = provider_base.normalize_provider_answer(raw)
    except provider_base.ProviderMalformedOutput:
        return None
    if raw.confidence < PROVIDER_CONFIDENCE_THRESHOLD:
        return None
    for candidate in tied_by_id:
        if str(candidate.get("id")) == str(raw.answer):
            return candidate
    return None


def rank_candidates(
    query: str,
    candidates: list[dict],
    *,
    provider: object | None = None,
) -> list[dict]:
    """Return `candidates` ordered by relevance to `query`. Never mutates
    the input candidates or performs any storage/delete action."""
    safe_candidates = [c for c in candidates if not _is_sensitive(c)]
    if not safe_candidates:
        return []

    normalized_query = _normalize(query)

    # Step 3: deterministic exact-phrase pre-policy, always wins, never
    # consults a provider.
    exact_matches = [
        c for c in safe_candidates if normalized_query and normalized_query in _normalize(str(c.get("content") or ""))
    ]
    if exact_matches:
        winner = sorted(exact_matches, key=lambda c: str(c.get("id")))[0]
        rest = [c for c in safe_candidates if c is not winner]
        return [winner, *_deterministic_order(query, rest)]

    return _deterministic_order(query, safe_candidates, provider=provider)


def _deterministic_order(
    query: str,
    candidates: list[dict],
    *,
    provider: object | None = None,
) -> list[dict]:
    if not candidates:
        return []

    query_tokens = _tokens(query)
    scored = [(_score(query_tokens, c), c) for c in candidates]
    best_score = max(score for score, _ in scored)
    tied = [c for score, c in scored if score == best_score]

    winner: dict | None = None
    if len(tied) > 1 and provider is not None:
        winner = _ask_provider_to_break_tie(query, tied, provider)
    if winner is None:
        winner = sorted(tied, key=lambda c: str(c.get("id")))[0]

    remaining = [c for c in candidates if c is not winner]
    remaining_sorted = sorted(
        remaining,
        key=lambda c: (-_score(query_tokens, c), str(c.get("id"))),
    )
    return [winner, *remaining_sorted]
