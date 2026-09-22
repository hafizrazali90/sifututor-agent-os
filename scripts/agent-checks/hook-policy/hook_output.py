#!/usr/bin/env python3
"""One shared decision -> hookSpecificOutput JSON formatter.

Both real hook families already emit the same wire shape (see SURVEY.md
sections 1, 2, and 5):

    {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                             "permissionDecision": "deny"|"ask_user",
                             "permissionDecisionReason": "..."}}

and Codex additionally uses `additionalContext` (no `permissionDecision`)
for a non-blocking note (see codex-pre-tool-use.py's `context()`). Neither
adapter should format this JSON itself; both call this function.

Precedence for one DispatchResult: a DENY wins over everything (the
request is blocked); otherwise an ASK_USER wins over a plain degrade note
(degrade notes are folded into the ask_user reason so nothing is dropped);
otherwise, if only DEGRADED decisions exist, emit additionalContext only
-- never a permissionDecision, because nothing here blocks or needs human
confirmation, it is purely visible-but-non-blocking; otherwise (all ALLOW,
no notes) emit nothing, exactly like today's real hooks on a clean allow.
"""
from __future__ import annotations

from dispatcher import DispatchResult
from models import Outcome


def _reason_with_guidance(decision) -> str:
    if decision.guidance:
        return f"{decision.reason}\n\n{decision.guidance}"
    return decision.reason


def dispatch_result_to_hook_output(result: DispatchResult) -> dict | None:
    deny = result.blocking_decision
    if deny is not None:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": _reason_with_guidance(deny),
            }
        }

    ask_user_decisions = result.ask_user_decisions
    degraded_decisions = result.degraded_decisions

    if ask_user_decisions:
        reason_parts = [_reason_with_guidance(d) for d in ask_user_decisions]
        reason_parts.extend(d.note for d in degraded_decisions)
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask_user",
                "permissionDecisionReason": "\n\n".join(reason_parts),
            }
        }

    if degraded_decisions:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": "\n\n".join(d.note for d in degraded_decisions),
            }
        }

    return None
