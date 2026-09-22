#!/usr/bin/env python3
"""Session Map archive classifier (issue #167, Bundle 6).

Given a Session Map entry, classify it as "propose archive" or "keep
active". This classifier's "propose archive" output must never by itself
cause a deletion or mutation -- it only returns a proposal value.

This is enforced structurally, not just by convention: `ArchiveProposal`
is a frozen dataclass with exactly three plain fields (`proposal`,
`reason`, `confidence`) and no method whatsoever. There is nothing on the
type a caller could invoke to make an archive actually happen.

A real archive action requires a separate, deterministic reference/state
check -- e.g. "is this Session Map entry still referenced by an open
GitHub issue, an active worktree, or a pending PR?" -- before anything is
actually archived. That check is stubbed here as
`check_references_before_archive`, which is intentionally unimplemented
(it raises `NotImplementedError`) so nothing can mistake an unfinished
stub for a real "safe to archive" signal. `classify_for_archive` never
calls it. A later bundle, or an explicit human step, must implement real
reference/state checking there before any code path is allowed to
actually archive a Session Map entry.
"""

from __future__ import annotations

from dataclasses import dataclass
import datetime

# An entry marked "done" is only proposed for archive once it has been
# inactive for at least this many days. This avoids proposing archival of
# something that was only just closed out, which a human may still want
# open in front of them.
_DONE_COOLDOWN_DAYS = 3
_ARCHIVABLE_STATUSES = ("done", "resolved", "superseded", "cancelled")


@dataclass(frozen=True)
class ArchiveProposal:
    """A proposal only. No field or method here can delete, apply, or
    otherwise mutate a Session Map entry or any external store."""

    proposal: str  # "propose_archive" or "keep_active"
    reason: str
    confidence: float = 1.0


def _days_since(last_touched_at: str, today: str) -> int:
    last_touched = datetime.date.fromisoformat(last_touched_at)
    today_date = datetime.date.fromisoformat(today)
    return (today_date - last_touched).days


def classify_for_archive(entry: dict, *, today: str) -> ArchiveProposal:
    """Classify one Session Map entry. Read-only: never mutates `entry`
    and never touches any archive store."""
    status = entry.get("status")
    last_touched_at = entry.get("last_touched_at")

    if status not in _ARCHIVABLE_STATUSES:
        return ArchiveProposal(
            proposal="keep_active",
            reason=f"status_{status}_is_not_an_archivable_status",
        )

    if not last_touched_at:
        return ArchiveProposal(
            proposal="keep_active",
            reason="missing_last_touched_at_cannot_confirm_cooldown",
        )

    inactive_days = _days_since(str(last_touched_at), today)
    if inactive_days < _DONE_COOLDOWN_DAYS:
        return ArchiveProposal(
            proposal="keep_active",
            reason=f"within_{_DONE_COOLDOWN_DAYS}_day_cooldown_since_marked_{status}",
        )

    return ArchiveProposal(
        proposal="propose_archive",
        reason=f"status_{status}_and_inactive_{inactive_days}_days",
    )


def check_references_before_archive(entry: dict, *, reference_index: object) -> bool:
    """Deterministic reference/state check -- STUB, not implemented.

    A real implementation must confirm, deterministically, that nothing
    still depends on this Session Map entry (e.g. no open GitHub issue, no
    active worktree, no pending PR references it) before any code path is
    allowed to actually archive it. This bundle only builds the
    classifier above; the actual archive action, and this check, are
    explicitly out of scope here (see the Bundle 6 build spec's scope
    boundary) and are left for a later bundle or an explicit human step.

    Raises `NotImplementedError` unconditionally so nothing can silently
    treat an unimplemented check as "cleared to archive".
    """
    raise NotImplementedError(
        "the reference/state check before archiving is not implemented in "
        "this bundle; a later bundle or an explicit human step must "
        "implement and run it before any Session Map entry is actually "
        "archived"
    )
