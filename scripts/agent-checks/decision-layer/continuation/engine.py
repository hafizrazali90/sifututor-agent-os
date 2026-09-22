#!/usr/bin/env python3
"""Bounded advisory continuation-decision engine (bundle 4, issue #162,
`.agent-os/handoffs/bundle-4-build-spec.md`, corrected per
`.agent-os/handoffs/bundle-4-correction-spec.md`).

Given a description of the milestone just reached and a snapshot of the
current session state, `decide()` recommends exactly one of
`schema.OUTCOME_VALUES`. This module can only ever produce a
recommendation:

- It performs no side effect of any kind -- no git operation, no file
  write, no tool invocation. Its only I/O is a read of the trusted
  approval packet through bundle 1's `approval.evaluate`, and only when
  the request carries identity claims. See
  `test_engine.py::EngineHasNoSideEffectsTest`.
- Its response type has no field that any caller could mistake for an
  approval, grant, or renewal of anything: `authoritative` is always
  `False`, and the two `approval_*` fields are a read-only report of what
  the trusted record said, derived only from `approval.evaluate` and
  never from the request. See
  `test_engine.py::EngineResponseCannotBeMistakenForApprovalTest`.
- It is a standalone advisory module: nothing in this repo currently
  calls it to gate any real continue/stop decision. Wiring it into a live
  session loop is explicitly out of this bundle's scope (see the build
  spec's "Scope boundary").

Routing, in order, for every call to `decide`:

1. Validate the request against this module's own schema
   (`schema.validate_request`).
2. Evaluate trusted approval. If the request's `session_state` carries any
   of `schema.SESSION_STATE_CLAIM_FIELDS`, bind those claims to the
   supervisor-written packet through `approval.evaluate(...)`. Otherwise
   the status is `not_checked`. Claims are never authority: any gap
   (no packet, another session, a hand-written packet, an expired one, a
   mismatched task or operation) yields a non-approved status.
3. Deterministic pre-policy (`pre_policy.evaluate`) -- final authority.
   When a rule matches, its outcome is used and bundle 1's decision layer
   is never dispatched to, regardless of what a provider would have
   answered. "Continue through an already-approved boundary" fires only
   when step 2 said `approved`.
4. Otherwise, route through bundle 1's decision layer
   (`decision-layer/engine.py`) using the fake provider only (this
   module's config always names `"provider": "fake"`; see
   `build_decision_layer_config`). Identity claims are stripped from the
   context handed to the provider. This module's response never adopts
   bundle 1's own `authoritative` stamping -- it always reports
   `authoritative: False`, independent of bundle 1's config or outcome.
"""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_DECISION_LAYER_DIR = _HERE.parent
if str(_DECISION_LAYER_DIR) not in sys.path:
    sys.path.insert(0, str(_DECISION_LAYER_DIR))

import approval as trusted_approval  # noqa: E402  (bundle 1, shared)
import config as decision_layer_config  # noqa: E402  (bundle 1, shared)
import engine as decision_layer_engine  # noqa: E402  (bundle 1, shared)
import schema as decision_layer_schema  # noqa: E402  (bundle 1, shared)

from . import pre_policy, schema

DECISION_TYPE = "continuation.recommendation"

REASON_NO_CLAIMS = "no_approval_claims_supplied"


def build_decision_layer_config() -> dict[str, object]:
    """The bundle-1 config this module dispatches with. Always the fake
    provider -- this bundle's own test suite is the only caller, and the
    build spec's hard limit is "no live network/provider calls in the
    test suite". Built from `DEFAULT_CONFIG` directly (never
    `load_config`), so this never reads the real process environment."""
    config = dict(decision_layer_config.DEFAULT_CONFIG)
    config["provider"] = "fake"
    return config


def _evaluate_trusted_approval(
    state: dict, state_dir: Path | None
) -> tuple[str, str]:
    """Return (approval_status, approval_reason) from the trusted record.

    Only `approval.evaluate` may produce a status here. When the request
    carries no identity claim at all, nothing is consulted and the status
    is `not_checked` -- which the pre-policy treats exactly like every
    other non-approved status.
    """
    if not any(field in state for field in schema.SESSION_STATE_CLAIM_FIELDS):
        return schema.APPROVAL_STATUS_NOT_CHECKED, REASON_NO_CLAIMS
    status = trusted_approval.evaluate(
        session_id=state.get("session_id"),
        worktree=state.get("worktree"),
        task_id=state.get("task_id"),
        operation=state.get("requested_operation"),
        state_dir=state_dir,
    )
    return status.status, status.reason


def _decision_layer_request(request: dict) -> dict:
    state = request.get("session_state") or {}
    # Identity claims are lookup keys for the trusted record, not decision
    # content. They never reach a provider.
    visible_state = {
        key: value
        for key, value in state.items()
        if key not in schema.SESSION_STATE_CLAIM_FIELDS
    }
    context_parts = [request["milestone_description"]]
    caller_message = request.get("caller_message") or ""
    if caller_message:
        context_parts.append(f"caller_message: {caller_message}")
    if visible_state:
        context_parts.append(f"session_state: {sorted(visible_state.items())}")
    return {
        "schema_version": decision_layer_schema.SCHEMA_VERSION,
        "decision_type": DECISION_TYPE,
        "options": list(schema.OUTCOME_VALUES),
        "context": "\n".join(context_parts),
        "sensitivity": "medium",
    }


def _response(
    *,
    outcome: str,
    reason: str,
    source: str,
    approval_status: str,
    approval_reason: str,
) -> dict:
    return {
        "schema_version": schema.SCHEMA_VERSION,
        "outcome": outcome,
        "reason": reason,
        "source": source,
        # Always False. This module never opts continuation.recommendation
        # into bundle 1's authoritative allowlist, and this field is set
        # here unconditionally rather than copied from bundle 1's
        # response -- see EngineResponseCannotBeMistakenForApprovalTest.
        "authoritative": False,
        # Read-only report of what the trusted record said. Derived only
        # from approval.evaluate, never from the request.
        "approval_status": approval_status,
        "approval_reason": approval_reason,
    }


def decide(
    request: dict,
    *,
    provider: object | None = None,
    state_dir: Path | None = None,
) -> dict:
    """Return exactly one recommendation for the given milestone/session
    state.

    No side effects, no network access, no approval-shaped output.
    `provider` and `state_dir` exist for tests only -- production callers
    never need to pass either. When `provider` is omitted, bundle 1's
    decision layer builds its own default provider from
    `build_decision_layer_config()`, which is always the fake provider.
    When `state_dir` is omitted, `approval.default_state_dir()` (the
    workspace's `.agent-os/approval-state`) is consulted.
    """
    errors = schema.validate_request(request)
    if errors:
        raise schema.RequestValidationError(errors)

    state = request.get("session_state") or {}
    approval_status, approval_reason = _evaluate_trusted_approval(state, state_dir)

    policy_result = pre_policy.evaluate(request, approval_status=approval_status)
    if policy_result is not None:
        return _response(
            outcome=policy_result.outcome,
            reason=policy_result.reason,
            source="pre_policy",
            approval_status=approval_status,
            approval_reason=approval_reason,
        )

    dl_request = _decision_layer_request(request)
    dl_response = decision_layer_engine.decide(
        dl_request, config=build_decision_layer_config(), provider=provider
    )

    answer = dl_response["answer"]
    if dl_response["outcome"] != "ok" or answer not in schema.OUTCOME_VALUES:
        # Any fallback, block, malformed/low-confidence answer, or an
        # answer outside the known outcome set is treated conservatively:
        # a human should look, not a guess.
        return _response(
            outcome="pause-for-human",
            reason=f"decision_layer_did_not_return_a_usable_outcome:{dl_response['outcome']}",
            source="decision_layer",
            approval_status=approval_status,
            approval_reason=approval_reason,
        )

    return _response(
        outcome=answer,
        reason="decision_layer_recommendation",
        source="decision_layer",
        approval_status=approval_status,
        approval_reason=approval_reason,
    )
