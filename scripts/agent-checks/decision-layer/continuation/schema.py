#!/usr/bin/env python3
"""Versioned request/response schema for the continuation-decision module
(bundle 4, issue #162, `.agent-os/handoffs/bundle-4-build-spec.md`,
corrected per `.agent-os/handoffs/bundle-4-correction-spec.md`).

A request describes a milestone just reached plus a snapshot of session
state; a response is exactly one recommendation plus a read-only report of
what the trusted approval record said. This module only describes shape --
see `pre_policy.py` for the deterministic override rules and `engine.py`
for the orchestrator that produces a response.

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
#
# There is deliberately no "already approved" boolean here. A caller-supplied
# flag is worker-controlled text and is never authority; approval comes only
# from the trusted packet evaluated through `approval.evaluate` (bundle 1).
# The retired key `end_to_end_boundary_already_approved` is accepted (unknown
# keys are tolerated) and ignored.
SESSION_STATE_BOOL_FIELDS = (
    "new_scope_appeared",
    "risk_materially_changed",
    "rollback_or_backup_unavailable",
    # A destructive operation newly in scope: delete/drop/force/reset/purge/
    # rollback of data.
    "destructive_scope_expansion",
    # A critical lane newly in scope: payments, auth, production migration,
    # mobile API contract, secrets, private production data.
    "critical_lane_expansion",
    "new_product_judgment_call",
    "route_outcome_already_produced",
)

# Identity claims the caller may attach so the engine can look up the trusted
# approval record. They are claims, not authority: the engine binds them to
# the supervisor-written packet through `approval.evaluate`, and any gap
# yields a non-approved status. Each must be a string when present.
SESSION_STATE_CLAIM_FIELDS = (
    "session_id",
    "worktree",
    "task_id",
    "requested_operation",
)

# The closed set of values `approval_status` may carry in a response. The
# first five come from bundle 1's `approval.py`; `not_checked` means the
# request carried no identity claims so no record was consulted.
APPROVAL_STATUS_APPROVED = "approved"
APPROVAL_STATUS_NOT_CHECKED = "not_checked"
APPROVAL_STATUS_VALUES = (
    APPROVAL_STATUS_APPROVED,
    "missing",
    "invalid",
    "mismatched",
    "expired",
    APPROVAL_STATUS_NOT_CHECKED,
)

_RESPONSE_FIELDS = (
    "schema_version",
    "outcome",
    "reason",
    "source",
    "authoritative",
    "approval_status",
    "approval_reason",
)

# The two fields that report, read-only, what the trusted record said. They
# are the only response fields allowed to mention approval at all, and they
# can never be written from a request -- see
# test_engine.EngineResponseCannotBeMistakenForApprovalTest.
APPROVAL_REPORT_FIELDS = ("approval_status", "approval_reason")


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
        for field in SESSION_STATE_CLAIM_FIELDS:
            if field in session_state and not isinstance(session_state[field], str):
                errors.append(f"session_state.{field}:text_required")

    caller_message = request.get("caller_message", "")
    if not isinstance(caller_message, str):
        errors.append("caller_message:text_required")

    return errors


def response_schema_fields() -> tuple[str, ...]:
    """The full set of fields a continuation-decision response always
    carries -- and only these fields."""
    return _RESPONSE_FIELDS
