#!/usr/bin/env python3
"""Signal 1 of 8: changed-file / diff risk level.

Deterministic only -- no provider is ever consulted for this signal. Risk
comes from two sources, both plain metadata, never judgment:

  1. Critical-lane path matching, mirroring AGENTS.md's own Universal
     Safety Rule: "If a task touches payments, commission, auth,
     migrations, or mobile API contracts, halt for human review before
     commit." A matching file always produces `priority="high"` and a
     `critical_lane:<lane>:<path>` flag, regardless of diff size and
     regardless of what any provider would have guessed -- this signal
     never calls one.
  2. Diff size thresholds for everything else, as a plain proxy for review
     attention. Still deterministic arithmetic, not judgment.
"""

from __future__ import annotations

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from contract import build_signal  # noqa: E402
import text_tokens  # noqa: E402

SIGNAL_NAME = "file_risk"

# Keyword sets per critical lane, matched against path tokens (path split on
# path separators, underscores, hyphens, and dots). Mirrors the lanes named
# in AGENTS.md's Universal Safety Rule.
_CRITICAL_LANE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "payments": (
        "payment", "payments", "billing", "invoice", "invoices", "refund",
        "refunds", "commission", "checkout", "payout", "payouts",
    ),
    "auth": ("auth", "authentication", "login", "session", "sessions", "oauth", "sso"),
    "migrations": ("migration", "migrations", "migrate"),
    "mobile_api_contract": ("mobileapi", "mobileapicontract"),
}

_LARGE_DIFF_LINES = 200
_MEDIUM_DIFF_LINES = 50


def critical_lanes_for_path(path: str) -> list[str]:
    """Return the critical-lane labels one file path matches, if any."""
    path_tokens = text_tokens.tokens(path)
    return [lane for lane, keywords in _CRITICAL_LANE_KEYWORDS.items() if path_tokens & set(keywords)]


def classify(payload: dict) -> dict:
    """Return the file_risk signal record for one change payload.

    `payload["changed_files"]` is a list of
    `{"path": str, "additions": int, "deletions": int, ...}` entries.
    """
    changed_files = payload.get("changed_files") or []

    critical_flags: list[str] = []
    size_priority = "low"
    largest_path: str | None = None
    largest_lines = -1

    for entry in changed_files:
        path = str(entry.get("path", ""))
        for lane in critical_lanes_for_path(path):
            critical_flags.append(f"critical_lane:{lane}:{path}")

        lines = int(entry.get("additions", 0) or 0) + int(entry.get("deletions", 0) or 0)
        if lines > largest_lines:
            largest_lines = lines
            largest_path = path
        if lines > _LARGE_DIFF_LINES:
            size_priority = "high"
        elif lines > _MEDIUM_DIFF_LINES and size_priority == "low":
            size_priority = "medium"

    if critical_flags:
        return build_signal(
            signal=SIGNAL_NAME,
            priority="high",
            flags=sorted(set(critical_flags)),
            reason=(
                "change touches a critical-lane path (payments, auth, or migrations); "
                "AGENTS.md requires human review before commit regardless of diff size"
            ),
            decision_source="deterministic",
        )

    if not changed_files:
        return build_signal(
            signal=SIGNAL_NAME,
            priority="low",
            flags=[],
            reason="no changed files were provided",
            decision_source="deterministic",
        )

    reason = f"largest diff is {largest_path!r} at {largest_lines} changed lines"
    return build_signal(
        signal=SIGNAL_NAME,
        priority=size_priority,
        flags=[] if size_priority == "low" else [f"large_diff:{largest_path}"],
        reason=reason,
        decision_source="deterministic",
    )
