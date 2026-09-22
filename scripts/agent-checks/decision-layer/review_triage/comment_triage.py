#!/usr/bin/env python3
"""Signal 5 of 8: review comment triage (blocking vs informational).

Deterministic keyword classification. A comment is only ever categorized
"blocking" or "informational" when its text actually contains a
recognizable marker; otherwise it is honestly reported as "unclear" so a
human still reads it, rather than silently defaulting it into either
bucket.
"""

from __future__ import annotations

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from contract import build_signal  # noqa: E402

SIGNAL_NAME = "comment_triage"

_BLOCKING_MARKERS = (
    "must fix", "must be fixed", "blocking", "before merge", "before this can merge",
    "required", "please fix", "this breaks", "needs to be fixed", "not safe to merge",
    "nack", "requesting changes", "change required",
)

_INFORMATIONAL_MARKERS = (
    "nit:", "nit -", "nitpick", "optional", "fyi", "just curious", "consider",
    "non-blocking", "lgtm", "no action needed", "out of scope for this pr",
)


def _categorize(body: str) -> str:
    lowered = body.lower()
    if any(marker in lowered for marker in _BLOCKING_MARKERS):
        return "blocking"
    if any(marker in lowered for marker in _INFORMATIONAL_MARKERS):
        return "informational"
    return "unclear"


def classify(payload: dict) -> dict:
    """Return the comment_triage signal record for one change payload.

    `payload["review_comments"]` is a list of
    `{"author": str, "body": str}` entries.
    """
    comments = payload.get("review_comments") or []

    if not comments:
        return build_signal(
            signal=SIGNAL_NAME,
            priority="low",
            flags=[],
            reason="no review comments were provided",
            decision_source="deterministic",
        )

    blocking: list[str] = []
    unclear: list[str] = []

    for index, entry in enumerate(comments):
        category = _categorize(str(entry.get("body", "")))
        author = entry.get("author", f"comment_{index}")
        if category == "blocking":
            blocking.append(f"blocking_comment:{author}")
        elif category == "unclear":
            unclear.append(f"unclear_comment:{author}")

    if blocking:
        return build_signal(
            signal=SIGNAL_NAME,
            priority="high",
            flags=blocking,
            reason="one or more review comments read as blocking and should be resolved before merge",
            decision_source="deterministic",
        )

    if unclear:
        return build_signal(
            signal=SIGNAL_NAME,
            priority="medium",
            flags=unclear,
            reason="one or more review comments do not match a known blocking or informational marker -- worth a human read",
            decision_source="deterministic",
        )

    return build_signal(
        signal=SIGNAL_NAME,
        priority="low",
        flags=[],
        reason="every review comment reads as informational",
        decision_source="deterministic",
    )
