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
    validated_approval_reference    -- str, pass-through ONLY -- see below
    required_context                -- list[str], triggered by route/task-type
    required_checks_evidence        -- list[str], triggered by route/task-type
    stop_conditions                 -- list[str], triggered by route/task-type
    next_automatic_action           -- str, computed from obligations + approval state
    follow_up_disposition           -- str, computed from route

`validated_approval_reference` hard limit (bundle-3-build-spec.md "Hard
limits"): this module never invents or infers an approval reference. It can
only ever be the exact string the caller supplied as `approval_reference`,
or the `APPROVAL_REFERENCE_NOT_PROVIDED` sentinel when the caller supplied
none. No decision-layer call, obligation lookup, or risk estimate is ever
allowed to populate this field.
"""

from __future__ import annotations

PACKET_SCHEMA_VERSION = 1

APPROVAL_REFERENCE_NOT_PROVIDED = "not_provided"

_PACKET_FIELDS = (
    "schema_version",
    "goal",
    "project",
    "scope_and_exclusions",
    "target_state",
    "validated_approval_reference",
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
