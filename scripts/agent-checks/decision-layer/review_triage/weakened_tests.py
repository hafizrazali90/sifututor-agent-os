#!/usr/bin/env python3
"""Signal 3 of 8: whether test changes look weakened.

Deterministic only. Flags a test-diff note when an assertion was removed
and no reason was stated for removing it. A removal with a stated reason
(e.g. "assertion moved to its own dedicated test file") is not flagged --
this module trusts the caller's stated reason rather than trying to judge
whether the reason is a *good* one; that judgment call belongs to a human
or adversarial reviewer, not this classifier.
"""

from __future__ import annotations

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from contract import build_signal  # noqa: E402

SIGNAL_NAME = "weakened_tests"


def classify(payload: dict) -> dict:
    """Return the weakened_tests signal record for one change payload.

    `payload["test_diff_notes"]` is a list of
    `{"file": str, "note": str, "assertion_removed": bool, "reason_stated": bool}`
    entries.
    """
    notes = payload.get("test_diff_notes") or []

    weakened = [entry for entry in notes if entry.get("assertion_removed") and not entry.get("reason_stated")]
    removed_with_reason = [entry for entry in notes if entry.get("assertion_removed") and entry.get("reason_stated")]

    if weakened:
        return build_signal(
            signal=SIGNAL_NAME,
            priority="high",
            flags=[f"possibly_weakened_test:{entry.get('file', '?')}" for entry in weakened],
            reason="a test diff removed an assertion with no stated reason -- coverage may have quietly weakened",
            decision_source="deterministic",
        )

    if removed_with_reason:
        return build_signal(
            signal=SIGNAL_NAME,
            priority="low",
            flags=[],
            reason="test diffs removed an assertion but stated a reason for each removal",
            decision_source="deterministic",
        )

    return build_signal(
        signal=SIGNAL_NAME,
        priority="low",
        flags=[],
        reason="no test diff notes indicate a removed assertion",
        decision_source="deterministic",
    )
