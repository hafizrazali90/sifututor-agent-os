#!/usr/bin/env python3
"""Bounded advisory continuation-decision engine (bundle 4, issue #162,
`.agent-os/handoffs/bundle-4-build-spec.md`).

Given a description of the milestone just reached and a snapshot of the
current session state, `decide()` recommends exactly one of
`schema.OUTCOME_VALUES`. This module can only ever produce a
recommendation:

- It performs no side effect of any kind -- no git operation, no file
  write outside its own test fixtures, no tool invocation. It is a pure
  function of its input. See `test_engine.py::EngineHasNoSideEffectsTest`.
- Its response type has no field that any caller could mistake for an
  approval, grant, or renewal of anything, and `authoritative` is always
  `False`. See
  `test_engine.py::EngineResponseCannotBeMistakenForApprovalTest`.
- It is a standalone advisory module: nothing in this repo currently
  calls it to gate any real continue/stop decision. Wiring it into a live
  session loop is explicitly out of this bundle's scope (see the build
  spec's "Scope boundary").

Routing, in order, for every call to `decide`:

1. Validate the request against this module's own schema
   (`schema.validate_request`).
2. Deterministic pre-policy (`pre_policy.evaluate`) -- final authority.
   When a rule matches, its outcome is used and bundle 1's decision layer
   is never dispatched to, regardless of what a provider would have
   answered.
3. Otherwise, route through bundle 1's decision layer
   (`decision-layer/engine.py`) using the fake provider only (this
   module's config always names `"provider": "fake"`; see
   `build_decision_layer_config`). This module's response never adopts
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

import config as decision_layer_config  # noqa: E402  (bundle 1, shared)
import engine as decision_layer_engine  # noqa: E402  (bundle 1, shared)
import schema as decision_layer_schema  # noqa: E402  (bundle 1, shared)

from . import pre_policy, schema

DECISION_TYPE = "continuation.recommendation"


def build_decision_layer_config() -> dict[str, object]:
    """The bundle-1 config this module dispatches with. Always the fake
    provider -- this bundle's own test suite is the only caller, and the
    build spec's hard limit is "no live network/provider calls in the
    test suite". Built from `DEFAULT_CONFIG` directly (never
    `load_config`), so this never reads the real process environment."""
    config = dict(decision_layer_config.DEFAULT_CONFIG)
    config["provider"] = "fake"
    return config


def _decision_layer_request(request: dict) -> dict:
    state = request.get("session_state") or {}
    context_parts = [request["milestone_description"]]
    caller_message = request.get("caller_message") or ""
    if caller_message:
        context_parts.append(f"caller_message: {caller_message}")
    if state:
        context_parts.append(f"session_state: {sorted(state.items())}")
    return {
        "schema_version": decision_layer_schema.SCHEMA_VERSION,
        "decision_type": DECISION_TYPE,
        "options": list(schema.OUTCOME_VALUES),
        "context": "\n".join(context_parts),
        "sensitivity": "medium",
    }


def _response(*, outcome: str, reason: str, source: str) -> dict:
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
    }


def decide(request: dict, *, provider: object | None = None) -> dict:
    """Return exactly one recommendation for the given milestone/session
    state.

    Pure function: no side effects, no network access, no approval-shaped
    output. `provider` exists for tests only -- production callers never
    need to pass one; when omitted, bundle 1's decision layer builds its
    own default provider from `build_decision_layer_config()`, which is
    always the fake provider.
    """
    errors = schema.validate_request(request)
    if errors:
        raise schema.RequestValidationError(errors)

    policy_result = pre_policy.evaluate(request)
    if policy_result is not None:
        return _response(
            outcome=policy_result.outcome,
            reason=policy_result.reason,
            source="pre_policy",
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
        )

    return _response(
        outcome=answer,
        reason="decision_layer_recommendation",
        source="decision_layer",
    )
