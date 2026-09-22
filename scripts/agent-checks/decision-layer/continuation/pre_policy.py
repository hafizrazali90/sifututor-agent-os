#!/usr/bin/env python3
"""Deterministic pre-policy layer for continuation decisions (bundle 4,
issue #162, `.agent-os/handoffs/bundle-4-build-spec.md`).

Runs before bundle 1's decision layer is ever consulted and, when it
matches, is final: no provider is dispatched to and its outcome can never
be overridden by a provider's answer. Two families of rule live here:

1. Forced `pause-for-human` -- the conditions the build spec (and issue
   #162's own requirement "pause only for genuine new scope, changed
   evidence, unavailable rollback, critical or destructive expansion, or
   product judgment") name as the only legitimate reasons to interrupt a
   human even under otherwise full autonomous continuation: new scope
   appearing, materially changed risk, unavailable rollback/backup, a
   critical or destructive action about to widen in scope, or a genuinely
   new product judgment call. These are checked first, so nothing below
   can suppress them -- a prior end-to-end approval never overrides a
   *new* reason to pause.
2. Forced `continue` for already-settled ground -- a route that already
   produced its outcome for this exact step, or a milestone that falls
   inside an end-to-end boundary the caller states was already agreed
   (scope, path, and stop point). These exist so the module never
   re-asks for the same already-covered ground.

Pure lookup logic over the request dict: no provider call, no file write,
no other side effect.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PrePolicyResult:
    outcome: str
    reason: str


def evaluate(request: dict) -> PrePolicyResult | None:
    """Return the deterministic override for this request, or None if no
    rule matches (meaning: route through the decision layer instead)."""
    state = request.get("session_state") or {}

    # Forced pause-for-human: final authority, evaluated first so no other
    # signal (including a prior end-to-end approval) can suppress it.
    if state.get("new_scope_appeared"):
        return PrePolicyResult("pause-for-human", "new_scope_appeared")
    if state.get("risk_materially_changed"):
        return PrePolicyResult("pause-for-human", "risk_materially_changed")
    if state.get("rollback_or_backup_unavailable"):
        return PrePolicyResult("pause-for-human", "rollback_or_backup_unavailable")
    if state.get("destructive_action_widening_scope"):
        return PrePolicyResult("pause-for-human", "destructive_action_widening_scope")
    if state.get("new_product_judgment_call"):
        return PrePolicyResult("pause-for-human", "new_product_judgment_call")

    # Forced continue: already-settled ground, do not re-ask.
    if state.get("route_outcome_already_produced"):
        return PrePolicyResult(
            "continue", "route_already_produced_an_outcome_do_not_re_ask"
        )
    if state.get("end_to_end_boundary_already_approved"):
        return PrePolicyResult(
            "continue", "end_to_end_boundary_already_approved_continue_through"
        )

    return None
