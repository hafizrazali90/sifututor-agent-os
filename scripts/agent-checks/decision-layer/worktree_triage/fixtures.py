#!/usr/bin/env python3
"""Synthetic `worktree-lifecycle.py inventory` entries for worktree_triage.

Every entry here is fabricated, shaped like the real output of
`inspect_worktree()` in `scripts/agent-checks/worktree-lifecycle.py`
(fields: repository, worktree, branch, head, classification, reasons,
recovery, and the conditional fields active_task, inherited_task_pointer,
ignored_blocker_count, stale_lease, process_check). None of these paths,
branches, or heads refer to any of the real 185 registered worktrees --
they are invented for this module's own test suite only, and this suite
never reads or writes any real worktree.
"""

from __future__ import annotations

_REPO = "/Users/hafizrazali/Projects/Sifututor/sifu-tutor"


def _entry(name: str, **overrides: object) -> dict:
    base = {
        "repository": _REPO,
        "worktree": f"/Users/hafizrazali/Projects/Sifututor-worktrees/{name}",
        "branch": f"feat/{name}",
        "head": "0" * 40,
        "classification": "preserve",
        "reasons": [],
        "recovery": "",
    }
    base.update(overrides)
    return base


# A worktree under an active lease whose heartbeat has expired: the tool
# itself flags `stale_lease: True` but keeps `classification: "preserve"`
# because it still requires an explicit release/reassignment, not an
# automatic reclaim.
STALE_LEASE_ENTRY = _entry(
    "900-stale-lease-demo",
    reasons=[
        "active lease heartbeat expired; explicit release or reassignment is required",
    ],
    stale_lease=True,
)

# A worktree with a recorded active task pointer. The real tool has no way
# to know whether the referenced task/issue is closed or merged -- that
# needs task-freshness evidence supplied separately (see
# OBSOLETE_TASK_POINTER_FRESHNESS below).
OBSOLETE_TASK_POINTER_ENTRY = _entry(
    "901-obsolete-task-demo",
    reasons=["active task pointer exists"],
    active_task="901-obsolete-task-demo",
)

# The task-freshness evidence for OBSOLETE_TASK_POINTER_ENTRY, keyed by
# worktree path, as if already produced by the *existing*
# scripts/agent-checks/agent_os_active_task_freshness.py tool (a safe,
# already-available local read path -- this bundle adds no new lookup).
# "stale_completed" means every recorded step in the task file is done or
# skipped: the pointer describes shipped work.
OBSOLETE_TASK_POINTER_FRESHNESS = {
    OBSOLETE_TASK_POINTER_ENTRY["worktree"]: "stale_completed",
}

# Same shape, but freshness evidence says the task is still genuinely
# active -- must NOT be classified obsolete.
ACTIVE_TASK_POINTER_ENTRY = _entry(
    "902-active-task-demo",
    reasons=["active task pointer exists"],
    active_task="902-active-task-demo",
)
ACTIVE_TASK_POINTER_FRESHNESS = {
    ACTIVE_TASK_POINTER_ENTRY["worktree"]: "active",
}

# Same shape, no freshness evidence available at all -- must NOT be
# guessed as obsolete; stays preserved and says so honestly.
UNDETERMINABLE_TASK_POINTER_ENTRY = _entry(
    "903-undeterminable-task-demo",
    reasons=["active task pointer exists"],
    active_task="903-undeterminable-task-demo",
)

# Clean, merged, and safe to reclaim, but a generated dependency directory
# (node_modules/vendor/etc, ignored by git) is still sitting there. This is
# the tool's own "only recognized reproducible ignored directories exist"
# note -- an existing field, not invented by this bundle.
GENERATED_DEPENDENCY_BLOCKER_ENTRY = _entry(
    "904-generated-dependency-demo",
    classification="reclaim_candidate",
    reasons=[
        "clean, unlocked, inactive and fully contained by base",
        "only recognized reproducible ignored directories exist",
    ],
    recovery=f"git -C {_REPO} worktree add "
    "/Users/hafizrazali/Projects/Sifututor-worktrees/904-generated-dependency-demo "
    "feat/904-generated-dependency-demo",
)

# Clean, merged, safe to reclaim, nothing else notable.
MERGED_BRANCH_ENTRY = _entry(
    "905-merged-branch-demo",
    classification="reclaim_candidate",
    reasons=["clean, unlocked, inactive and fully contained by base"],
    recovery=f"git -C {_REPO} worktree add "
    "/Users/hafizrazali/Projects/Sifututor-worktrees/905-merged-branch-demo "
    "feat/905-merged-branch-demo",
)

# A registered worktree whose directory is gone. This is a real
# `inspect_worktree()` outcome (`prunable_registration`) that does not
# clearly fit any of the four working buckets above -- it is genuinely
# uncertain for *triage priority* purposes, so it is routed through the
# decision layer for an advisory (never authoritative) tie-break instead
# of being silently folded into one of the other buckets.
UNCERTAIN_ENTRY = _entry(
    "906-prunable-registration-demo",
    classification="prunable_registration",
    reasons=["registered path is missing; Git branch/commit refs remain"],
    recovery=f"git -C {_REPO} worktree prune --expire now",
)

# A worktree under a live (not expired) lease. The underlying tool's own
# safety checks already block this -- this bundle's classifier must
# preserve it deterministically and must never dispatch a provider for it,
# no matter what the provider would have guessed.
ACTIVE_LEASE_ENTRY = _entry(
    "907-active-lease-demo",
    reasons=["active lease owned by agent-session-42"],
)

ALL_ENTRIES = (
    STALE_LEASE_ENTRY,
    OBSOLETE_TASK_POINTER_ENTRY,
    ACTIVE_TASK_POINTER_ENTRY,
    UNDETERMINABLE_TASK_POINTER_ENTRY,
    GENERATED_DEPENDENCY_BLOCKER_ENTRY,
    MERGED_BRANCH_ENTRY,
    UNCERTAIN_ENTRY,
    ACTIVE_LEASE_ENTRY,
)
