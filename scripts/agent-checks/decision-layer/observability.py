#!/usr/bin/env python3
"""Metadata-only observability record builder (build item 9).

A record contains only decision type, provider, latency, reported cost,
confidence, fallback flag, and outcome -- never the raw request or
response body (answer, reason, context, or anything else). This module
deliberately allowlists fields rather than blocklisting them, so a new
field added to the response shape later cannot silently leak into a
stored record without a matching change here.
"""

from __future__ import annotations

RECORD_FIELDS: tuple[str, ...] = (
    "decision_type",
    "provider",
    "latency_ms",
    "cost",
    "confidence",
    "fallback_used",
    "outcome",
)


def build_record(response: dict) -> dict:
    """Return the metadata-only record for one decision response."""
    return {field: response[field] for field in RECORD_FIELDS}
