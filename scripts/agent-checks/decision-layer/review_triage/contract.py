#!/usr/bin/env python3
"""Shared output contract for every review-triage signal (Bundle 5, issue #166).

Every signal in this module returns a record built by `build_signal`. The
shape is deliberately narrow and deliberately incapable of expressing "this
passed" or "this was verified":

  - no `status`, `result`, `passed`, or `verified` field exists in the shape
  - `advisory_only` is always `True` and cannot be overridden by a caller
  - `authoritative` is always `False` and cannot be overridden by a caller

`NEVER_REPLACES` documents, in the data itself, the real checks this module
can never stand in for, so the boundary travels with the data and not only
with a code comment. `contains_forbidden_claim` lets tests prove, across
every fixture this module ships, that no output value ever reads as a
pass/verify claim.
"""

from __future__ import annotations

import re

SCHEMA_VERSION = 1

# What this module's output can never be mistaken for. Present in every
# triage report so a consumer sees the boundary in the data itself.
NEVER_REPLACES: tuple[str, ...] = (
    "tests",
    "e2e",
    "qa",
    "security_checks",
    "adversarial_review",
    "release_smoke",
    "monitoring",
    "rollback_evidence",
)

VALID_PRIORITIES = ("low", "medium", "high")

_SIGNAL_FIELDS = (
    "schema_version",
    "signal",
    "priority",
    "flags",
    "reason",
    "decision_source",
    "advisory_only",
    "authoritative",
)

# Whole-word only, case-insensitive: the exact two claims the task
# specification says this module must never make (see the handoff's scope
# boundary: "A test must prove this module never marks anything 'passed' or
# 'verified'"). Word-boundary matching so legitimate words such as
# "bypass" never false-positive.
_FORBIDDEN_CLAIM_PATTERN = re.compile(r"\b(passed|verified)\b", re.IGNORECASE)


def build_signal(
    *,
    signal: str,
    priority: str,
    flags: list[str],
    reason: str,
    decision_source: str,
) -> dict:
    """Build one signal record.

    `advisory_only` and `authoritative` are fixed here and cannot be set by
    a caller -- this is what makes the "never authoritative" contract
    structural rather than a convention every signal must remember to
    apply.
    """
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"invalid priority {priority!r}, expected one of {VALID_PRIORITIES}")
    if decision_source not in ("deterministic", "provider"):
        raise ValueError(f"invalid decision_source {decision_source!r}")
    return {
        "schema_version": SCHEMA_VERSION,
        "signal": signal,
        "priority": priority,
        "flags": list(flags),
        "reason": reason,
        "decision_source": decision_source,
        "advisory_only": True,
        "authoritative": False,
    }


def signal_fields() -> tuple[str, ...]:
    """The full set of fields a signal record always carries."""
    return _SIGNAL_FIELDS


def contains_forbidden_claim(value: object) -> bool:
    """True if `value` is, or recursively contains, a string with the
    standalone word "passed" or "verified". Used by the contract test to
    prove this module's output can never read as a verification result."""
    if isinstance(value, str):
        return bool(_FORBIDDEN_CLAIM_PATTERN.search(value))
    if isinstance(value, dict):
        return any(contains_forbidden_claim(key) or contains_forbidden_claim(v) for key, v in value.items())
    if isinstance(value, (list, tuple, set)):
        return any(contains_forbidden_claim(v) for v in value)
    return False
