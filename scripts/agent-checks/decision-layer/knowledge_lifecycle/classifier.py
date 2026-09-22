#!/usr/bin/env python3
"""Knowledge-lifecycle memory classifier (issue #167, Bundle 6).

Given one candidate piece of text considered for storage as a memory
(e.g. a Koda memory_store call), classify it into exactly one of:

    durable    -- a durable correction/lesson, worth storing.
    ephemeral  -- temporary/ephemeral state, should not be stored. Matches
                  this repo's own umbrella CLAUDE.md "When to AVOID Koda"
                  guidance (current branch name, working directory, etc.).
    duplicate  -- a near-duplicate of something already known, should not
                  be stored again.
    stale      -- contradicted by newer stated information already known;
                  flagged for review, never silently stored as fact.
    sensitive  -- secret- or PII-shaped; must never reach storage.

This module only classifies. It never writes to Koda, never deletes or
mutates anything, and never decides storage on its own -- something else
(unchanged by this bundle) still performs the actual deterministic write
and the actual deterministic sensitive-data filtering. See
`.agent-os/handoffs/bundle-6-build-spec.md` scope boundary.

Pipeline, in order, for every call to `classify_memory`:

1. Deterministic sensitive/PII check, reusing Bundle 1's `secret_filter`
   module (no reimplementation). This runs before anything else, including
   before any provider is ever constructed or consulted -- a secret-shaped
   candidate is rejected even if a provider would otherwise approve it.
2. Deterministic ephemeral-state check (pattern rules mirroring the
   umbrella CLAUDE.md guidance). Never touches a provider.
3. Deterministic near-duplicate check against `known_memories`, using
   normalized text similarity. Never touches a provider.
4. Deterministic stale/contradiction check against `known_memories`: same
   subject, different content, and the known memory's `stated_at` is the
   same age or newer than the candidate's -- i.e. something already known
   more recently contradicts what the candidate states. Never touches a
   provider.
5. Otherwise, the candidate is classified `durable` by default. If a
   `provider` is supplied, it is optionally consulted at this final step
   only (after every deterministic check above has already cleared the
   candidate) to corroborate the durable/ephemeral call; a low-confidence
   or unavailable provider answer never overrides the deterministic
   default.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
from pathlib import Path
import re
import sys

_HERE = Path(__file__).resolve().parent
_DECISION_LAYER_DIR = _HERE.parent


def _load_sibling_module(name: str):
    """Load a module from the parent decision-layer directory by path.

    Mirrors the loader pattern `secret_filter.py` itself already uses to
    reach `secret_artifact_scan.py`, so this module works whether it is
    imported as part of a package or loaded standalone by tests.
    """
    module_name = f"decision_layer_{name}"
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, _DECISION_LAYER_DIR / f"{name}.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load sibling decision-layer module {name!r}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


secret_filter = _load_sibling_module("secret_filter")
provider_base = _load_sibling_module("provider_base")

DUPLICATE_SIMILARITY_THRESHOLD = 0.8

_WORD_PATTERN = re.compile(r"[a-z0-9.]+")

_EPHEMERAL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bcurrent(?:ly)? (?:on |working on )?branch\b", re.IGNORECASE),
    re.compile(r"\bworking directory\b", re.IGNORECASE),
    re.compile(r"\bcurrent working directory\b", re.IGNORECASE),
    re.compile(r"\bcwd (?:is|=)\b", re.IGNORECASE),
    re.compile(r"\bpwd (?:is|=)\b", re.IGNORECASE),
    re.compile(r"\bsession (?:state|id) (?:is|=)\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class ClassificationResult:
    """The classifier's output. Proposal/label only -- no storage or
    delete capability lives on this type."""

    classification: str
    reason: str
    confidence: float = 1.0
    matched_memory_id: str | None = None


def _tokens(text: str) -> set[str]:
    return set(_WORD_PATTERN.findall(text.lower()))


def _text_similarity(a: str, b: str) -> float:
    """Word-token Jaccard similarity.

    Deliberately token-based rather than character-based: two sentences
    that differ only by a single distinctive entity (a hostname, an
    amount, a status word) can still score high on character-level
    similarity because most of the surrounding characters overlap. Word
    tokenization treats a changed entity as a fully distinct token, which
    is what actually separates "near duplicate of the same fact" from
    "same subject, different -- possibly contradicting -- fact".
    """
    tokens_a = _tokens(a)
    tokens_b = _tokens(b)
    if not tokens_a and not tokens_b:
        return 1.0
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)


def _is_sensitive(candidate: dict) -> bool:
    content = str(candidate.get("content") or "")
    subject = str(candidate.get("subject") or "")
    return bool(secret_filter.scan(content) or secret_filter.scan(subject))


def _is_ephemeral(candidate: dict) -> bool:
    content = str(candidate.get("content") or "")
    return any(pattern.search(content) for pattern in _EPHEMERAL_PATTERNS)


def _find_duplicate(candidate: dict, known_memories: list[dict]) -> dict | None:
    candidate_content = str(candidate.get("content") or "")
    for known in known_memories:
        similarity = _text_similarity(candidate_content, str(known.get("content") or ""))
        if similarity >= DUPLICATE_SIMILARITY_THRESHOLD:
            return known
    return None


def _find_contradiction(candidate: dict, known_memories: list[dict]) -> dict | None:
    candidate_subject = candidate.get("subject")
    if not candidate_subject:
        return None
    candidate_content = str(candidate.get("content") or "")
    candidate_stated_at = str(candidate.get("stated_at") or "")

    for known in known_memories:
        if known.get("subject") != candidate_subject:
            continue
        known_content = str(known.get("content") or "")
        if _text_similarity(candidate_content, known_content) >= DUPLICATE_SIMILARITY_THRESHOLD:
            # Same subject, effectively the same content -- that is a
            # duplicate, not a contradiction; let duplicate detection own it.
            continue
        known_stated_at = str(known.get("stated_at") or "")
        # Only a contradiction worth flagging when what's already known is
        # the same age or newer than the candidate -- i.e. the candidate
        # would be stored as if it were still current when newer
        # information already says otherwise.
        if known_stated_at and candidate_stated_at and known_stated_at >= candidate_stated_at:
            return known
    return None


def classify_memory(
    candidate: dict,
    *,
    known_memories: list[dict] | None = None,
    provider: object | None = None,
) -> ClassificationResult:
    """Classify one candidate memory. Never stores, deletes, or mutates
    anything -- callers act on `.classification` themselves."""
    known_memories = known_memories or []

    # Step 1: deterministic, reused, and runs before any provider exists.
    if _is_sensitive(candidate):
        return ClassificationResult(
            classification="sensitive",
            reason="secret_or_pii_shaped_content_detected",
            confidence=1.0,
        )

    # Step 2: deterministic ephemeral-state rules.
    if _is_ephemeral(candidate):
        return ClassificationResult(
            classification="ephemeral",
            reason="matches_ephemeral_state_pattern",
            confidence=1.0,
        )

    # Step 3: deterministic near-duplicate check.
    duplicate = _find_duplicate(candidate, known_memories)
    if duplicate is not None:
        return ClassificationResult(
            classification="duplicate",
            reason="near_duplicate_of_known_memory",
            confidence=1.0,
            matched_memory_id=duplicate.get("id"),
        )

    # Step 4: deterministic stale/contradiction check.
    contradiction = _find_contradiction(candidate, known_memories)
    if contradiction is not None:
        return ClassificationResult(
            classification="stale",
            reason="contradicted_by_newer_stated_information",
            confidence=1.0,
            matched_memory_id=contradiction.get("id"),
        )

    # Step 5: default durable, optionally corroborated by a provider.
    # A provider is never able to move the outcome away from "durable"
    # into any of the deterministic-only categories above -- it can only
    # be consulted once every deterministic check has already cleared the
    # candidate, mirroring engine.py's confidence/fallback policy.
    if provider is not None:
        request = {
            "schema_version": 1,
            "decision_type": "knowledge_lifecycle.classify",
            "options": ["durable", "ephemeral"],
            "context": str(candidate.get("content") or ""),
            "sensitivity": "low",
        }
        try:
            raw = provider.dispatch(request)
        except provider_base.ProviderError:
            raw = None
        if isinstance(raw, provider_base.ProviderAnswer) and raw.confidence >= 0.55:
            if raw.answer == "ephemeral":
                return ClassificationResult(
                    classification="ephemeral",
                    reason="provider_corroborated_ephemeral",
                    confidence=raw.confidence,
                )
            return ClassificationResult(
                classification="durable",
                reason="provider_corroborated_durable",
                confidence=raw.confidence,
            )

    return ClassificationResult(
        classification="durable",
        reason="no_deterministic_rule_matched_default_durable",
        confidence=1.0,
    )
