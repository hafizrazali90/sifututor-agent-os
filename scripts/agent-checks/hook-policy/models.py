#!/usr/bin/env python3
"""Core decision model shared by every check, the dispatcher, and both
per-agent adapters.

This is the vocabulary the rest of hook-policy is built on:

- `Severity` says what happens when a check *cannot run* (see
  `dispatcher.py`): a REQUIRED check that cannot run blocks with a clear
  reason; an ADVISORY check that cannot run degrades visibly instead.
- `Outcome`/`Decision` is what a check returns for one request. A DENY
  decision without `guidance` is refused at construction time — the bundle
  spec requires actionable recovery guidance in every block message, so
  this makes "blocked, no guidance" impossible to construct rather than a
  reviewable-but-skippable convention.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    """What a check's unavailability means for the overall dispatch."""

    REQUIRED = "required"
    ADVISORY = "advisory"


class Outcome(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    ASK_USER = "ask_user"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class Decision:
    """The result of one check evaluating one request."""

    outcome: Outcome
    check_name: str
    reason: str = ""
    guidance: str = ""
    note: str = ""

    @property
    def blocks(self) -> bool:
        return self.outcome == Outcome.DENY

    @staticmethod
    def allow(check_name: str, note: str = "") -> "Decision":
        return Decision(Outcome.ALLOW, check_name, note=note)

    @staticmethod
    def deny(check_name: str, reason: str, guidance: str) -> "Decision":
        if not guidance or not guidance.strip():
            raise ValueError(
                f"deny decision from check {check_name!r} is missing actionable "
                "recovery guidance; every block message must tell the caller what "
                "to actually do"
            )
        if not reason or not reason.strip():
            raise ValueError(f"deny decision from check {check_name!r} is missing a reason")
        return Decision(Outcome.DENY, check_name, reason=reason, guidance=guidance)

    @staticmethod
    def ask_user(check_name: str, reason: str, guidance: str = "") -> "Decision":
        if not reason or not reason.strip():
            raise ValueError(f"ask_user decision from check {check_name!r} is missing a reason")
        return Decision(Outcome.ASK_USER, check_name, reason=reason, guidance=guidance)

    @staticmethod
    def degraded(check_name: str, note: str) -> "Decision":
        if not note or not note.strip():
            raise ValueError(
                f"degraded decision from check {check_name!r} is missing a visible note; "
                "an advisory check that cannot run must still say so, not silently pass"
            )
        return Decision(Outcome.DEGRADED, check_name, note=note)


@dataclass(frozen=True)
class HookRequest:
    """Normalized shape both the Claude and Codex adapters translate into.

    `payload` keeps the raw adapter-specific dict for checks that need more
    than command/cwd (currently unused by any shipped check, kept for
    forward compatibility so adapters don't need to change shape later).
    """

    tool_name: str
    command: str
    cwd: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
