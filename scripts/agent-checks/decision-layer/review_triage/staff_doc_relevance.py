#!/usr/bin/env python3
"""Signal 7 of 8: staff-documentation relevance.

Mirrors the concept in `docs/agent-playbooks/release-documentation.md`:
"A staff-facing change ships with the staff documentation it needs, in the
same release bundle, or it records why it did not." This module does not
run that playbook's actual checker -- it only flags, from the change
description given to it, whether the change looks staff-facing and,
if so, whether a documentation decision (`relevant`, `not_relevant`, or
`urgent_deferral`) was recorded at all.

Deterministic only. `staff_facing` is taken from an explicit payload hint
when given; otherwise it is inferred from changed-file paths using a
conservative keyword list (admin/staff/dashboard screens, Laravel Blade
views, and What's New/changelog-adjacent files).
"""

from __future__ import annotations

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from contract import build_signal  # noqa: E402
import text_tokens  # noqa: E402

SIGNAL_NAME = "staff_doc_relevance"

_STAFF_FACING_PATH_KEYWORDS = (
    "admin", "staff", "dashboard", "backoffice", "cpanel", "sims",
)
_STAFF_FACING_EXTENSIONS = (".blade.php",)

_VALID_DECISIONS = ("relevant", "not_relevant", "urgent_deferral")


def _looks_staff_facing(changed_files: list[dict]) -> bool:
    for entry in changed_files:
        path = str(entry.get("path", ""))
        if any(path.endswith(ext) for ext in _STAFF_FACING_EXTENSIONS):
            return True
        if text_tokens.tokens(path) & set(_STAFF_FACING_PATH_KEYWORDS):
            return True
    return False


def _decision_is_recorded_and_complete(decision: dict | None) -> tuple[bool, str]:
    if not decision:
        return False, "no documentation decision was recorded"

    kind = decision.get("decision")
    if kind not in _VALID_DECISIONS:
        return False, "documentation decision is missing or not one of relevant/not_relevant/urgent_deferral"

    if kind == "relevant":
        if not decision.get("artifacts"):
            return False, "decision is 'relevant' but names no documentation artifacts"
        return True, "relevant decision names documentation artifacts"

    if kind == "not_relevant":
        if not (decision.get("reason") or "").strip():
            return False, "decision is 'not_relevant' but gives no reason"
        return True, "not_relevant decision gives a reason"

    # urgent_deferral
    if not (decision.get("owner") or "").strip() or not (decision.get("follow_up_issue") or "").strip():
        return False, "decision is 'urgent_deferral' but is missing an owner or a follow-up issue"
    return True, "urgent_deferral decision names an owner and a follow-up issue"


def classify(payload: dict) -> dict:
    """Return the staff_doc_relevance signal record for one change payload."""
    changed_files = payload.get("changed_files") or []
    staff_facing = payload.get("staff_facing")
    if staff_facing is None:
        staff_facing = _looks_staff_facing(changed_files)

    if not staff_facing:
        return build_signal(
            signal=SIGNAL_NAME,
            priority="low",
            flags=[],
            reason="change does not look staff-facing",
            decision_source="deterministic",
        )

    complete, why = _decision_is_recorded_and_complete(payload.get("documentation_decision"))
    if complete:
        return build_signal(
            signal=SIGNAL_NAME,
            priority="low",
            flags=[],
            reason=f"change looks staff-facing; {why}",
            decision_source="deterministic",
        )

    return build_signal(
        signal=SIGNAL_NAME,
        priority="high",
        flags=["staff_doc_decision_missing_or_incomplete"],
        reason=f"change looks staff-facing but {why} (see docs/agent-playbooks/release-documentation.md)",
        decision_source="deterministic",
    )
