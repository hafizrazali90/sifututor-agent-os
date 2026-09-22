#!/usr/bin/env python3
"""Versioned field schema for a compact execution packet (Bundle 3, issue
#160).

A packet is the triggered-obligation summary `packet_builder.build_packet`
produces for one route/task-type. It always carries exactly these fields,
plus `schema_version` so callers can detect a future shape change the same
way Bundle 1's decision-layer response schema does:

    schema_version                 -- int, this module's PACKET_SCHEMA_VERSION
    goal                            -- str, pass-through from the caller
    project                         -- str, pass-through from the caller
    scope_and_exclusions            -- dict: route, task_type, scope, exclusions
    target_state                    -- str, pass-through from the caller
    untrusted_approval_context      -- str, pass-through ONLY, grants nothing
    approval_status                 -- str, computed ONLY by approval.evaluate
    approval_reason                 -- str, the short reason code behind it
    required_context                -- list[str], triggered by route/task-type
    required_checks_evidence        -- list[str], triggered by route/task-type
    stop_conditions                 -- list[str], triggered by route/task-type
    next_automatic_action           -- str, computed from obligations + approval_status
    follow_up_disposition           -- str, computed from route

`untrusted_approval_context` is caller-supplied free text carried through
for traceability (a chat quote, a ticket id, a note). It is never validated
and it grants NO authority: nothing in this package reads it to decide
whether a critical-lane packet may proceed. It is always exactly the string
the caller supplied, or the `APPROVAL_CONTEXT_NOT_PROVIDED` sentinel when
the caller supplied none.

`approval_status` / `approval_reason` are the only approval signal a packet
carries. They are computed solely by `approval.evaluate(...)` (the one
approval authority in the decision layer) from the session identity,
worktree, task id and operation the caller passes to `build_packet`. When
those are absent the status is `APPROVAL_STATUS_NOT_CHECKED` and a
critical-lane packet stays halted. No obligation lookup, decision-layer
call, risk estimate, or caller string can ever set the status to
`approved`.
"""

from __future__ import annotations

# Bumped from 1 -> 2 when the earlier single "validated" approval field was
# replaced by `untrusted_approval_context` + `approval_status` +
# `approval_reason` (PR #173 correction).
PACKET_SCHEMA_VERSION = 2

APPROVAL_CONTEXT_NOT_PROVIDED = "not_provided"

# The one status this module owns. Every other status value a packet can
# carry ("approved", "missing", "invalid", "mismatched", "expired") comes
# verbatim from `approval.evaluate`.
APPROVAL_STATUS_NOT_CHECKED = "not_checked"

_PACKET_FIELDS = (
    "schema_version",
    "goal",
    "project",
    "scope_and_exclusions",
    "target_state",
    "untrusted_approval_context",
    "approval_status",
    "approval_reason",
    "required_context",
    "required_checks_evidence",
    "stop_conditions",
    "next_automatic_action",
    "follow_up_disposition",
)


def packet_fields() -> tuple[str, ...]:
    """The full, exact set of fields every generated packet carries."""
    return _PACKET_FIELDS


class PacketValidationError(ValueError):
    """Raised when packet-builder input fails schema validation."""

    def __init__(self, errors: list[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


def _is_nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_input(
    *,
    route: str,
    task_type: str,
    project: str,
    goal: str,
    scope: str,
    target_state: str,
    exclusions: list[str] | None = None,
    **_ignored: object,
) -> list[str]:
    """Return a list of `field:reason` error codes for build_packet's raw
    input. Empty list means valid. Mirrors schema.validate_request's shape
    from the decision-layer module one directory up."""
    errors: list[str] = []
    for name, value in (
        ("route", route),
        ("task_type", task_type),
        ("project", project),
        ("goal", goal),
        ("scope", scope),
        ("target_state", target_state),
    ):
        if not _is_nonempty_string(value):
            errors.append(f"{name}:nonempty_text_required")

    if exclusions is not None:
        if not isinstance(exclusions, list) or any(
            not isinstance(item, str) for item in exclusions
        ):
            errors.append("exclusions:string_list_required")

    return errors
