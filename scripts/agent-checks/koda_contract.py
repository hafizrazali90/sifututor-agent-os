#!/usr/bin/env python3
"""Shared capability contract for Codex's direct Koda integration."""

from __future__ import annotations

from collections.abc import Iterable


KODA_CAPABILITY_TIERS = {
    "core": {
        "memory_search",
        "memory_store",
        "memory_update",
        "memory_context",
    },
    "session": {
        "session_start",
        "session_end",
        "session_list",
    },
    "governance": {
        "memory_init",
        "memory_recall",
        "memory_relate",
        "memory_flag",
        "project_health",
    },
    "administrative": {
        "memory_forget",
        "validation_run",
    },
}

REQUIRED_KODA_TIERS = {"core"}
REQUIRED_KODA_TOOLS = set().union(
    *(KODA_CAPABILITY_TIERS[tier] for tier in REQUIRED_KODA_TIERS)
)
ALL_KODA_TOOLS = set().union(*KODA_CAPABILITY_TIERS.values())


def capability_report(tool_names: Iterable[str]) -> dict:
    """Return deterministic availability details without making admin tools startup-critical."""

    available = set(tool_names)
    tiers = {}
    for tier, expected in KODA_CAPABILITY_TIERS.items():
        tiers[tier] = {
            "available": sorted(expected & available),
            "missing": sorted(expected - available),
            "required": tier in REQUIRED_KODA_TIERS,
        }
    return {
        "tiers": tiers,
        "missing_required": sorted(REQUIRED_KODA_TOOLS - available),
        "unexpected": sorted(available - ALL_KODA_TOOLS),
    }
