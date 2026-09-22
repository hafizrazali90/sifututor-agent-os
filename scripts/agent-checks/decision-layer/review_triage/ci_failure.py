#!/usr/bin/env python3
"""Signal 4 of 8: CI failure category (flaky vs real), when inferable.

Deterministic keyword classification of failure text. This is deliberately
conservative: a failure is only ever categorized "flaky" or "real" when the
failure text actually contains a recognizable marker for that category.
Everything else is honestly reported as "unknown" rather than guessed --
the task specification explicitly allows for the distinction not being
inferable from the input given, and a classifier that always picks one
side when it does not actually know is worse than one that says so.
"""

from __future__ import annotations

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from contract import build_signal  # noqa: E402

SIGNAL_NAME = "ci_failure"

_FLAKY_MARKERS = (
    "timeout", "timed out", "flaky", "econnreset", "network error",
    "connection reset", "rate limit", "socket hang up", "dns lookup failed",
    "temporarily unavailable", "retry succeeded", "rerun passed",
)

_REAL_MARKERS = (
    "assertionerror", "assertion failed", "expected", "typeerror",
    "syntaxerror", "referenceerror", "undefined is not a function",
    "null pointer", "nullpointerexception", "compile error", "compilation failed",
)


def _categorize(failure_text: str) -> str | None:
    lowered = failure_text.lower()
    if any(marker in lowered for marker in _FLAKY_MARKERS):
        return "flaky"
    if any(marker in lowered for marker in _REAL_MARKERS):
        return "real"
    return None


def classify(payload: dict) -> dict:
    """Return the ci_failure signal record for one change payload.

    `payload["ci_results"]` is a list of
    `{"job": str, "status": "failed"|"passed", "failure_text": str}` entries.
    """
    results = payload.get("ci_results") or []
    failed = [entry for entry in results if entry.get("status") == "failed"]

    if not failed:
        return build_signal(
            signal=SIGNAL_NAME,
            priority="low",
            flags=[],
            reason="no failed CI jobs were reported",
            decision_source="deterministic",
        )

    flags: list[str] = []
    any_real = False
    any_unknown = False

    for entry in failed:
        job = entry.get("job", "?")
        category = _categorize(str(entry.get("failure_text", "")))
        if category is None:
            any_unknown = True
            flags.append(f"ci_failure_unknown:{job}")
        elif category == "real":
            any_real = True
            flags.append(f"ci_failure_real:{job}")
        else:
            flags.append(f"ci_failure_flaky:{job}")

    if any_real:
        priority = "high"
        reason = "at least one failed CI job looks like a real (non-flaky) failure from its text"
    elif any_unknown:
        priority = "medium"
        reason = "a failed CI job's failure text does not contain a recognizable flaky or real marker -- flaky-vs-real is not inferable from the input given"
    else:
        priority = "medium"
        reason = "every failed CI job's failure text matches a known flaky-failure marker"

    return build_signal(
        signal=SIGNAL_NAME,
        priority=priority,
        flags=flags,
        reason=reason,
        decision_source="deterministic",
    )
