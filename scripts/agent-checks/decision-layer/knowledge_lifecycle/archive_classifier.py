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
check -- "is this Session Map entry still referenced by an open GitHub
issue, an active worktree, or an open PR?" -- before anything is actually
archived. That check is `check_references_before_archive`, a pure
function over a caller-supplied `reference_index`. This bundle does NOT
build that index (nothing here calls `gh`, reads worktrees, or touches
GitHub); a later bundle or an explicit human step must build it and pass
it in. `classify_for_archive` never calls the check, and no code path in
this bundle performs an archive.

NOT WIRED. Nothing in any session-map flow calls this module yet.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
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


def check_references_before_archive(
    entry: dict,
    *,
    reference_index: Mapping[str, Sequence[object]] | None,
) -> bool:
    """Deterministic reference/state check over a caller-supplied index.

    `reference_index` maps a Session Map entry id to the list of items
    that still reference it (open issues, active worktrees, open PRs).
    The caller builds and supplies it; this bundle does not build it.

    Returns True only when the entry's id is present in the index with an
    empty reference list. Every uncertain case is conservative and returns
    False: a missing index (`None` or not a mapping), an entry with no id,
    an id absent from the index, or any remaining reference.

    Pure: never mutates `entry` or `reference_index`, never archives.
    """
    if not isinstance(reference_index, Mapping):
        return False
    entry_id = entry.get("id")
    if not entry_id:
        return False
    if entry_id not in reference_index:
        return False
    references = reference_index[entry_id]
    if references is None:
        return False
    return len(references) == 0
