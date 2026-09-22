#!/usr/bin/env python3
"""Versioned request/response schema for the continuation-decision module
(bundle 4, issue #162, `.agent-os/handoffs/bundle-4-build-spec.md`).

A request describes a milestone just reached plus a snapshot of session
state; a response is exactly one recommendation. This module only
describes shape -- see `pre_policy.py` for the deterministic override
rules and `engine.py` for the orchestrator that produces a response.

Dependency-free (stdlib only), matching bundle 1's `schema.py` convention.
"""

from __future__ import annotations

SCHEMA_VERSION = 1

# The only seven values this module may ever recommend. Every one is
# advisory language ("recommend", never "grant"/"approve"/"authorize") --
# see engine.py's docstring and test_engine.py's approval-shape proof.
OUTCOME_VALUES = (
    "continue",
    "retry",
    "investigate",
    "rollback",
    "split-follow-up",
    "pause-for-human",
    "complete",
)

# Deterministic pre-policy conditions read these session_state keys. An
# absent key means "no evidence of this condition", never "condition
# satisfied" -- see pre_policy.py.
SESSION_STATE_BOOL_FIELDS = (
    "new_scope_appeared",
    "risk_materially_changed",
    "rollback_or_backup_unavailable",
    "destructive_action_widening_scope",
    "new_product_judgment_call",
    "route_outcome_already_produced",
    "end_to_end_boundary_already_approved",
)

_RESPONSE_FIELDS = (
    "schema_version",
    "outcome",
    "reason",
    "source",
    "authoritative",
)


class RequestValidationError(ValueError):
    """Raised when a request fails schema validation."""

    def __init__(self, errors: list[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


def _is_nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_strict_bool(value: object) -> bool:
    return isinstance(value, bool)


def validate_request(request: object) -> list[str]:
    """Return a list of `field:reason` error codes. Empty list means valid."""
    errors: list[str] = []
    if not isinstance(request, dict):
        return ["request:object_required"]

    if request.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version:unsupported")

    if not _is_nonempty_string(request.get("milestone_description")):
        errors.append("milestone_description:nonempty_text_required")

    session_state = request.get("session_state", {})
    if not isinstance(session_state, dict):
        errors.append("session_state:object_required")
    else:
        for field in SESSION_STATE_BOOL_FIELDS:
            if field in session_state and not _is_strict_bool(session_state[field]):
                errors.append(f"session_state.{field}:bool_required")

    caller_message = request.get("caller_message", "")
    if not isinstance(caller_message, str):
        errors.append("caller_message:text_required")

    return errors


def response_schema_fields() -> tuple[str, ...]:
    """The full set of fields a continuation-decision response always
    carries -- and only these fields."""
    return _RESPONSE_FIELDS
