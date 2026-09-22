#!/usr/bin/env python3
"""Deterministic pre-policy layer (build item 3).

This runs before any provider is asked anything. Its applicable output
always overrides any provider's answer, and it never calls a provider
itself -- it is pure lookup logic, so it is exercised with zero risk and
zero latency in this bundle's tests.

Rules here mirror the umbrella AGENTS.md Universal Safety Rule: destructive
release actions and unreviewed payment/refund decisions are never left to
a fast typed-decision provider, no matter how confident it claims to be.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PrePolicyResult:
    answer: str
    confidence: float
    reason: str


_RULES: dict[str, PrePolicyResult] = {
    "release.destructive_action": PrePolicyResult(
        answer="deny",
        confidence=1.0,
        reason="destructive_release_actions_are_always_denied",
    ),
    "payments.unreviewed_refund": PrePolicyResult(
        answer="hold_for_human",
        confidence=1.0,
        reason="unreviewed_payment_decisions_require_a_human",
    ),
}


def evaluate(request: dict) -> PrePolicyResult | None:
    """Return the deterministic override for this request, or None."""
    return _RULES.get(request.get("decision_type"))
