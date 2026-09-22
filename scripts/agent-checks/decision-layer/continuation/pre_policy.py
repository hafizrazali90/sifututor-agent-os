#!/usr/bin/env python3
"""Deterministic pre-policy layer for continuation decisions (bundle 4,
issue #162, `.agent-os/handoffs/bundle-4-build-spec.md`, corrected per
`.agent-os/handoffs/bundle-4-correction-spec.md`).

Runs before bundle 1's decision layer is ever consulted and, when it
matches, is final: no provider is dispatched to and its outcome can never
be overridden by a provider's answer. Two families of rule live here:

1. Forced `pause-for-human` -- the conditions the build spec (and issue
   #162's own requirement "pause only for genuine new scope, changed
   evidence, unavailable rollback, critical or destructive expansion, or
   product judgment") name as the only legitimate reasons to interrupt a
   human even under otherwise full autonomous continuation: new scope
   appearing, materially changed risk, unavailable rollback/backup, a
   destructive operation newly in scope, a critical lane newly in scope,
   or a genuinely new product judgment call. These are checked first, so
   nothing below can suppress them -- neither a repeated instruction nor
   a valid trusted approval ever overrides a *new* reason to pause.
2. Forced `continue` for already-settled ground -- a route that already
   produced its outcome for this exact step, or a milestone that falls
   inside an end-to-end boundary the *trusted approval record* covers.
   These exist so the module never re-asks for the same already-covered
   ground.

Authority for rule 2's second branch comes only from `approval_status`,
which the engine computes through bundle 1's `approval.evaluate(...)` and
passes in as a keyword argument. Nothing inside the request -- not a
boolean, not a string that happens to say "approved" -- is ever read as
approval. The retired request key `end_to_end_boundary_already_approved`
is ignored.

Pure lookup logic over the request dict plus that one trusted argument: no
provider call, no file read or write, no other side effect.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import schema

REASON_TRUSTED_APPROVAL_CONTINUE = "trusted_approval_covers_boundary_continue_through"

# (session_state key, reason code). Order is priority order.
_FORCED_PAUSE_TRIGGERS = (
    ("new_scope_appeared", "new_scope_appeared"),
    ("risk_materially_changed", "risk_materially_changed"),
    ("rollback_or_backup_unavailable", "rollback_or_backup_unavailable"),
    ("destructive_scope_expansion", "destructive_scope_expansion"),
    ("critical_lane_expansion", "critical_lane_expansion"),
    ("new_product_judgment_call", "new_product_judgment_call"),
)


@dataclass(frozen=True)
class PrePolicyResult:
    outcome: str
    reason: str


def evaluate(
    request: dict,
    *,
    approval_status: str = schema.APPROVAL_STATUS_NOT_CHECKED,
) -> PrePolicyResult | None:
    """Return the deterministic override for this request, or None if no
    rule matches (meaning: route through the decision layer instead).

    `approval_status` must be the status string produced by
    `approval.evaluate(...)` (or `not_checked`). It is compared by exact
    identity with the literal `"approved"`; any other value, of any type,
    is treated as "no authority".
    """
    state = request.get("session_state") or {}

    # Forced pause-for-human: final authority, evaluated first so no other
    # signal (including a valid trusted approval) can suppress it.
    for key, reason in _FORCED_PAUSE_TRIGGERS:
        if state.get(key) is True:
            return PrePolicyResult("pause-for-human", reason)

    # Forced continue: already-settled ground, do not re-ask.
    if state.get("route_outcome_already_produced") is True:
        return PrePolicyResult(
            "continue", "route_already_produced_an_outcome_do_not_re_ask"
        )
    if approval_status == schema.APPROVAL_STATUS_APPROVED and isinstance(approval_status, str):
        return PrePolicyResult("continue", REASON_TRUSTED_APPROVAL_CONTINUE)

    return None
