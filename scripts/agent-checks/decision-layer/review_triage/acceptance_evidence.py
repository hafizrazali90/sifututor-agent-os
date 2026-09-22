#!/usr/bin/env python3
"""Signal 6 of 8: acceptance-criteria-to-evidence mapping.

Deterministic only. For each stated acceptance-criteria item, checks
whether a named piece of evidence is attached. This module does not judge
whether the evidence is *good* evidence -- only whether one was named at
all. Judging evidence quality is a human/adversarial-review job.
"""

from __future__ import annotations

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from contract import build_signal  # noqa: E402

SIGNAL_NAME = "acceptance_evidence"


def _has_evidence(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def classify(payload: dict) -> dict:
    """Return the acceptance_evidence signal record for one change payload.

    `payload["acceptance_criteria"]` is a list of
    `{"item": str, "evidence": str | None}` entries.
    """
    criteria = payload.get("acceptance_criteria") or []

    if not criteria:
        return build_signal(
            signal=SIGNAL_NAME,
            priority="low",
            flags=[],
            reason="no acceptance criteria were provided to check evidence against",
            decision_source="deterministic",
        )

    missing = [entry.get("item", "?") for entry in criteria if not _has_evidence(entry.get("evidence"))]

    if missing:
        return build_signal(
            signal=SIGNAL_NAME,
            priority="high",
            flags=[f"missing_evidence:{item}" for item in missing],
            reason="one or more stated acceptance-criteria items have no named evidence",
            decision_source="deterministic",
        )

    return build_signal(
        signal=SIGNAL_NAME,
        priority="low",
        flags=[],
        reason="every stated acceptance-criteria item names a piece of evidence",
        decision_source="deterministic",
    )
