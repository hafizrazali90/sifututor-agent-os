#!/usr/bin/env python3
"""Versioned JSON request/response schema for the decision layer.

Request: decision type, options/scale, context text, a sensitivity hint.
Response: chosen answer, confidence, which provider answered, whether
fallback was used, latency in milliseconds, reported cost, and outcome.

This module is intentionally dependency-free (stdlib only) so the CLI and
tests never need a network install to validate shapes.
"""

from __future__ import annotations

SCHEMA_VERSION = 1

VALID_SENSITIVITY = ("low", "medium", "high")

_RESPONSE_FIELDS = (
    "schema_version",
    "decision_type",
    "answer",
    "confidence",
    "provider",
    "fallback_used",
    "authoritative",
    "latency_ms",
    "cost",
    "outcome",
    "reason",
)


class RequestValidationError(ValueError):
    """Raised when a request fails schema validation."""

    def __init__(self, errors: list[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


def _is_nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_request(request: object) -> list[str]:
    """Return a list of `field:reason` error codes. Empty list means valid."""
    errors: list[str] = []
    if not isinstance(request, dict):
        return ["request:object_required"]

    if request.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version:unsupported")

    if not _is_nonempty_string(request.get("decision_type")):
        errors.append("decision_type:nonempty_text_required")

    options = request.get("options")
    scale = request.get("scale")
    if options is None and scale is None:
        errors.append("options_or_scale:required")

    if options is not None:
        if (
            not isinstance(options, list)
            or not options
            or any(not _is_nonempty_string(option) for option in options)
        ):
            errors.append("options:nonempty_string_list_required")

    if scale is not None:
        if (
            not isinstance(scale, dict)
            or not isinstance(scale.get("min"), (int, float))
            or isinstance(scale.get("min"), bool)
            or not isinstance(scale.get("max"), (int, float))
            or isinstance(scale.get("max"), bool)
            or scale.get("min") >= scale.get("max")
        ):
            errors.append("scale:min_max_numeric_required")

    context = request.get("context", "")
    if not isinstance(context, str):
        errors.append("context:text_required")

    sensitivity = request.get("sensitivity", "low")
    if sensitivity not in VALID_SENSITIVITY:
        errors.append("sensitivity:invalid_choice")

    return errors


def response_schema_fields() -> tuple[str, ...]:
    """The full set of fields a decision-layer response always carries."""
    return _RESPONSE_FIELDS
