#!/usr/bin/env python3
"""Knowledge-lifecycle memory classifier (issue #167, Bundle 6).

Given one candidate piece of text considered for storage as a memory
(e.g. a Koda memory_store call), classify it into exactly one of:

    durable       -- a durable correction/lesson, worth storing. Only ever
                     produced when a provider corroborates it (advisory).
    ephemeral     -- temporary/ephemeral state, should not be stored. Matches
                     this repo's own umbrella CLAUDE.md "When to AVOID Koda"
                     guidance (current branch name, working directory, etc.).
    duplicate     -- a near-duplicate of something already known, should not
                     be stored again.
    stale         -- contradicted by newer stated information already known;
                     flagged for review, never silently stored as fact.
    sensitive     -- secret- or PII-shaped; must never reach storage.
    needs_review  -- no deterministic rule matched and no provider
                     corroborated a call. The classifier does NOT guess
                     `durable` here; it hands the candidate to a reviewer
                     at low confidence (0.3).

NOT WIRED. This module is a standalone classifier with fixtures. It is not
called from any memory-flush hook, session-map flow, or Koda write path.
It never writes to Koda, never deletes or mutates anything, and never
decides storage on its own -- something else (unchanged by this bundle)
still performs the actual deterministic write and the actual deterministic
sensitive-data filtering. See `.agent-os/handoffs/bundle-6-build-spec.md`
scope boundary and `.agent-os/handoffs/bundle-6-correction-spec.md`.

Confidence semantics:

    1.0                 only where the rule is exact: sensitive (secret
                        scanner hit) and an exact duplicate (similarity 1.0),
                        plus the ephemeral pattern rules.
    similarity score    near-duplicate and stale/contradiction results carry
                        the word-token similarity they were decided on, so a
                        reviewer can see how close the two texts were.
    provider confidence durable / ephemeral corroborated by a provider carry
                        the provider's own confidence. Advisory only.
    0.3                 needs_review.

Pipeline, in order, for every call to `classify_memory`:

1. Deterministic sensitive/PII check, reusing Bundle 1's `secret_filter`
   module (no reimplementation). This runs before anything else, including
   before any provider is ever consulted -- a secret-shaped candidate is
   rejected even if a provider would otherwise approve it.
2. Deterministic ephemeral-state check (pattern rules mirroring the
   umbrella CLAUDE.md guidance). Never touches a provider.
3. Deterministic near-duplicate check against `known_memories`, using
   normalized word-token similarity. Never touches a provider.
4. Deterministic stale/contradiction check against `known_memories`: same
   subject, different content, and the known memory's `stated_at` is the
   same age or newer than the candidate's -- i.e. something already known
   more recently contradicts what the candidate states. Never touches a
   provider.
5. Otherwise the candidate is `needs_review` (confidence 0.3). If a
   `provider` is supplied it may corroborate `durable` or `ephemeral`; the
   result then carries the provider's confidence and is still advisory. A
   provider error, malformed answer, or answer below
   `PROVIDER_CONFIDENCE_THRESHOLD` leaves the result at `needs_review`. In
   this bundle the only provider ever passed is Bundle 1's offline
   `FakeProvider` (tests); no live provider is wired.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib
from pathlib import Path
import re
import sys

_HERE = Path(__file__).resolve().parent
_DECISION_LAYER_DIR = _HERE.parent


def _load_sibling_module(name: str):
    """Import a module from the parent decision-layer directory by its
    plain module name.

    Loaded under the plain name (not an alias) on purpose: `provider_fake`,
    `engine` and the rest of the decision layer do `import provider_base`,
    so the `ProviderAnswer` / `ProviderError` classes this module compares
    against must be the very same objects, or `isinstance` and `except`
    silently never match.
    """
    if name in sys.modules:
        return sys.modules[name]
    if str(_DECISION_LAYER_DIR) not in sys.path:
        sys.path.insert(0, str(_DECISION_LAYER_DIR))
    return importlib.import_module(name)


secret_filter = _load_sibling_module("secret_filter")
provider_base = _load_sibling_module("provider_base")

DUPLICATE_SIMILARITY_THRESHOLD = 0.8
PROVIDER_CONFIDENCE_THRESHOLD = 0.55
NEEDS_REVIEW_CONFIDENCE = 0.3

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
    confidence: float
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


def _find_duplicate(candidate: dict, known_memories: list[dict]) -> tuple[dict, float] | None:
    """Return (known memory, similarity) for the first near-duplicate."""
    candidate_content = str(candidate.get("content") or "")
    for known in known_memories:
        similarity = _text_similarity(candidate_content, str(known.get("content") or ""))
        if similarity >= DUPLICATE_SIMILARITY_THRESHOLD:
            return known, similarity
    return None


def _find_contradiction(candidate: dict, known_memories: list[dict]) -> tuple[dict, float] | None:
    """Return (known memory, similarity) for the first contradiction."""
    candidate_subject = candidate.get("subject")
    if not candidate_subject:
        return None
    candidate_content = str(candidate.get("content") or "")
    candidate_stated_at = str(candidate.get("stated_at") or "")

    for known in known_memories:
        if known.get("subject") != candidate_subject:
            continue
        known_content = str(known.get("content") or "")
        similarity = _text_similarity(candidate_content, known_content)
        if similarity >= DUPLICATE_SIMILARITY_THRESHOLD:
            # Same subject, effectively the same content -- that is a
            # duplicate, not a contradiction; let duplicate detection own it.
            continue
        known_stated_at = str(known.get("stated_at") or "")
        # Only a contradiction worth flagging when what's already known is
        # the same age or newer than the candidate -- i.e. the candidate
        # would be stored as if it were still current when newer
        # information already says otherwise.
        if known_stated_at and candidate_stated_at and known_stated_at >= candidate_stated_at:
            return known, similarity
    return None


def _ask_provider(candidate: dict, provider: object) -> ClassificationResult | None:
    """Advisory provider corroboration. Returns None on any error, malformed
    answer, low confidence, or an answer outside the offered options."""
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
        return None
    try:
        raw = provider_base.normalize_provider_answer(raw)
    except provider_base.ProviderMalformedOutput:
        return None
    confidence = raw.confidence
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        return None
    if not (0.0 <= confidence <= 1.0) or confidence < PROVIDER_CONFIDENCE_THRESHOLD:
        return None
    if raw.answer == "ephemeral":
        return ClassificationResult(
            classification="ephemeral",
            reason="provider_corroborated_ephemeral",
            confidence=float(confidence),
        )
    if raw.answer == "durable":
        return ClassificationResult(
            classification="durable",
            reason="provider_corroborated_durable",
            confidence=float(confidence),
        )
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

    # Step 1: deterministic, reused, and runs before any provider is asked.
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

    # Step 3: deterministic near-duplicate check. Confidence is the
    # similarity the decision was made on (1.0 only for an exact match).
    duplicate = _find_duplicate(candidate, known_memories)
    if duplicate is not None:
        known, similarity = duplicate
        return ClassificationResult(
            classification="duplicate",
            reason="near_duplicate_of_known_memory",
            confidence=similarity,
            matched_memory_id=known.get("id"),
        )

    # Step 4: deterministic stale/contradiction check. Confidence is the
    # similarity to the contradicting memory (below the duplicate
    # threshold by construction), never a hard 1.0.
    contradiction = _find_contradiction(candidate, known_memories)
    if contradiction is not None:
        known, similarity = contradiction
        return ClassificationResult(
            classification="stale",
            reason="contradicted_by_newer_stated_information",
            confidence=similarity,
            matched_memory_id=known.get("id"),
        )

    # Step 5: no deterministic rule matched. A provider may corroborate a
    # durable/ephemeral call (advisory, carrying its own confidence). It is
    # never able to move the outcome into any deterministic-only category
    # above. Without corroboration the honest answer is "needs review".
    if provider is not None:
        corroborated = _ask_provider(candidate, provider)
        if corroborated is not None:
            return corroborated

    return ClassificationResult(
        classification="needs_review",
        reason="no_deterministic_rule_matched_needs_review",
        confidence=NEEDS_REVIEW_CONFIDENCE,
    )
