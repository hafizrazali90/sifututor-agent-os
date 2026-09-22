#!/usr/bin/env python3
"""Signal 8 of 8: missing human-journey evidence.

Mirrors AGENTS.md's Permanent E2E Regression Rule and Agent-As-Tester
Evidence section: a user-facing change needs named E2E or manual-QA
evidence, not backend/unit tests alone. Deterministic only -- this module
only checks whether the payload names any human-journey evidence when the
change is declared user-facing; it does not judge whether the named
evidence is adequate.
"""

from __future__ import annotations

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from contract import build_signal  # noqa: E402

SIGNAL_NAME = "human_journey_evidence"


def classify(payload: dict) -> dict:
    """Return the human_journey_evidence signal record for one change
    payload.

    `payload["is_user_facing"]` is a bool. `payload["human_journey_evidence"]`
    is a list of named E2E/manual-QA evidence strings.
    """
    if not payload.get("is_user_facing"):
        return build_signal(
            signal=SIGNAL_NAME,
            priority="low",
            flags=[],
            reason="change is not declared user-facing",
            decision_source="deterministic",
        )

    evidence = [item for item in (payload.get("human_journey_evidence") or []) if str(item).strip()]

    if evidence:
        return build_signal(
            signal=SIGNAL_NAME,
            priority="low",
            flags=[],
            reason=f"user-facing change names {len(evidence)} piece(s) of human-journey evidence",
            decision_source="deterministic",
        )

    return build_signal(
        signal=SIGNAL_NAME,
        priority="high",
        flags=["missing_human_journey_evidence"],
        reason="change is declared user-facing but names no E2E or manual-QA evidence",
        decision_source="deterministic",
    )
