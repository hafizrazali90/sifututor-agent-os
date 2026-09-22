#!/usr/bin/env python3
"""Compact execution packet builder (Bundle 3, issue #160).

`build_packet(...)` takes a route/task-type plus a small amount of plain
task context and returns one versioned packet (see `packet_schema.py`)
containing only the obligations that route/task-type actually triggers
(see `obligations.py`), instead of the full verify/QA/review/commit
checklist every time.

Input shape (all keyword-only; see README.md for the documented contract):

    route: str                      -- e.g. "feature", "bugfix", "hotfix",
                                        "small-change", "refactor", "docs"
    task_type: str                  -- free text; carried through for
                                        traceability, not itself the lookup
                                        key (route drives the mapping)
    project: str                    -- e.g. "sifu-tutor", "ripple-suite"
    goal: str                       -- what this packet is for
    scope: str                      -- what is in scope
    target_state: str               -- what "done" looks like
    exclusions: list[str] | None    -- what is explicitly out of scope
    untrusted_approval_context: str | None
                                    -- free text carried through unchanged;
                                        grants NO authority (see below)
    user_facing: bool = False       -- triggers small-change's conditional
                                        E2E/related-impact obligations
    staff_facing: bool = False      -- triggers the staff-documentation
                                        context item
    critical_lane: bool = False     -- triggers the Universal Safety Rule
                                        halt (payments/auth/migrations/etc.)
    session_id: str | None          -- the four identity parameters that
    worktree: str | Path | None        `approval.evaluate` binds a trusted
    task_id: str | None                approval packet to; all omitted means
    operation: str | None              approval_status == "not_checked"
    state_dir: Path | None          -- approval-state directory override
                                        (test injection point; defaults to
                                        approval.default_state_dir())
    config: dict | None = None      -- decision-layer config override; if
                                        omitted, uses a config that is
                                        locked to the fake provider and
                                        never reads the real process
                                        environment (see
                                        `_default_risk_config`)
    provider: object | None = None  -- decision-layer provider override,
                                        threaded straight into
                                        `engine.decide(..., provider=...)`

Approval hard limits:

- `untrusted_approval_context` is pass-through only. It is always exactly
  the caller's string, or `packet_schema.APPROVAL_CONTEXT_NOT_PROVIDED`
  when none was supplied. Nothing in this module reads it to decide
  anything; a non-empty value never makes a critical-lane packet
  executable.
- `approval_status` / `approval_reason` are computed ONLY by
  `approval.evaluate(...)`, the single approval authority in the decision
  layer, from the session identity, worktree, task id and operation the
  caller passes in. With none of those present the status is
  `not_checked`. No obligation lookup, decision-layer call, or risk
  estimate can write to those fields.
- A critical-lane packet's `next_automatic_action` halts unless
  `approval_status == "approved"`.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_DECISION_LAYER_DIR = _HERE.parent

# `engine.py` (and its own internal imports of config/schema/secret_filter/
# provider_base/provider_fake/provider_jev/pre_policy/retry/observability)
# all use plain top-level `import x` statements, matching this repo's own
# `cli.py` convention -- so this module puts both the decision-layer
# directory and this package's own directory on sys.path once, then uses
# ordinary imports rather than re-implementing per-module file loading.
for _dir in (_DECISION_LAYER_DIR, _HERE):
    _dir_str = str(_dir)
    if _dir_str not in sys.path:
        sys.path.insert(0, _dir_str)

import approval  # noqa: E402  (decision-layer/approval.py, the only approval authority)
import config as config_module  # noqa: E402  (decision-layer/config.py)
import engine  # noqa: E402  (decision-layer/engine.py)
import schema  # noqa: E402  (decision-layer/schema.py)
import secret_filter  # noqa: E402  (decision-layer/secret_filter.py, reused, not rebuilt)

import obligations  # noqa: E402  (packets/obligations.py)
import packet_schema  # noqa: E402  (packets/packet_schema.py)

_REDACTION_MARKER = "[REDACTED - possible secret/PII-shaped content detected]"

# Base ranking each route's default risk options list, most-likely-answer
# first. FakeProvider's "ok" scenario always answers `options[0]`
# deterministically (see provider_fake.py), so this ranking is this
# module's own domain-knowledge prior about typical risk per route --
# the decision layer is asked to confirm/pick from it, not to invent a
# judgment from nothing. A real provider (e.g. Jev) would reason over the
# request's context field instead of relying on that ordering.
_RISK_OPTIONS_BY_ROUTE: dict[str, tuple[str, str, str]] = {
    "docs": ("low", "medium", "high"),
    "refactor": ("low", "medium", "high"),
    "feature": ("low", "medium", "high"),
    "small-change": ("low", "medium", "high"),
    "bugfix": ("medium", "low", "high"),
    "hotfix": ("high", "medium", "low"),
}

# Proportionate verification is route-specific; the Gate 4 adversarial
# pre-push review (AGENTS.md "Gate 4: adversarial pre-push review, never
# skipped") is not. Every disposition below that lightens the in-route
# checklist still names Gate 4 as owed before push.
_FOLLOW_UP_BY_ROUTE: dict[str, str] = {
    "feature": (
        "after commit, confirm the staff documentation decision landed in the same "
        "bundle if staff-facing, then hand off for merge approval"
    ),
    "bugfix": (
        "after commit, run defect_analysis if this closes a tracked bug pattern; "
        "otherwise close the linked GitHub issue with the fix evidence"
    ),
    "hotfix": (
        "after commit, close the linked GitHub issue and update the Session Release "
        "Ledger if this session touched more than one fix; confirm deploy and smoke "
        "check before calling it live"
    ),
    "small-change": (
        "after commit, verification is proportionate (targeted QA of the changed "
        "surface, no defect_analysis), but Gate 4 adversarial pre-push review still "
        "applies before push; then close the linked GitHub issue if one exists"
    ),
    "refactor": (
        "after commit, confirm no behavior actually changed (qa evidence) before "
        "closing the linked issue"
    ),
    "docs": (
        "after commit, verification is proportionate (docs validation / render-link "
        "check, no regression test), but Gate 4 adversarial pre-push review still "
        "applies before push; then close the linked issue if one exists"
    ),
}


def _default_risk_config() -> dict:
    """A decision-layer config for the risk-bucket call that can never pick
    a live provider, even if the host process happens to have a real
    JEV_API_KEY set. `env={}` means the real process environment is never
    read, and `provider` is explicitly locked to `"fake"` on top of that."""
    return config_module.load_config(env={}, overrides={"provider": "fake"})


def _resolve_risk_bucket(*, route: str, critical_lane: bool, config: dict, provider) -> str:
    if critical_lane:
        # Deterministic override, matching AGENTS.md's Critical Lanes gate:
        # critical-lane work is always treated as high risk. This never
        # calls the decision layer at all -- zero provider dispatch, the
        # same "hard rule wins, no provider touched" spirit as
        # decision-layer/pre_policy.py's own rules.
        return "high"

    options = _RISK_OPTIONS_BY_ROUTE.get(route)
    if options is None:
        return "medium"

    request = {
        "schema_version": schema.SCHEMA_VERSION,
        "decision_type": "packets.risk_bucket",
        "options": list(options),
        "context": f"estimate the risk bucket for route={route}",
        "sensitivity": "low",
    }
    response = engine.decide(request, config=config, provider=provider)
    if response["outcome"] == "ok" and response["answer"] in options:
        return response["answer"]
    # A fallback/blocked decision-layer response is not itself a risk
    # judgment -- treat it as the conservative middle bucket rather than
    # trusting "undetermined" as though it meant "low".
    return "medium"


def _resolve_approval(
    *,
    session_id: str | None,
    worktree: str | os.PathLike | None,
    task_id: str | None,
    operation: str | None,
    state_dir: Path | None,
) -> tuple[str, str]:
    """Return (approval_status, approval_reason).

    The ONLY source of an approval status is `approval.evaluate`, which
    reads the trusted supervisor packet bound to this session. When the
    caller passed none of the four identity parameters there is nothing to
    bind against, so the status is `not_checked` (never "approved"). Any
    partial identity is handed to `approval.evaluate` as-is so it can
    report the exact gap (missing / mismatched / ...)."""
    if session_id is None and worktree is None and task_id is None and operation is None:
        return packet_schema.APPROVAL_STATUS_NOT_CHECKED, "no_session_identity_supplied"
    status = approval.evaluate(
        session_id=session_id,
        worktree=worktree,
        task_id=task_id,
        operation=operation,
        state_dir=state_dir,
    )
    return status.status, status.reason


def _next_automatic_action(
    *,
    resolved: "obligations.ObligationSet",
    unmapped: bool,
    approval_status: str,
    approval_reason: str,
    critical_lane: bool,
) -> str:
    if unmapped:
        return (
            "halt: read docs/agent-playbooks/task-router.md, verify.md, qa.md, and "
            "commit.md directly before continuing (no triggered-obligation mapping "
            "for this route/task-type)"
        )
    # The only thing that can lift a critical-lane halt is a trusted
    # approval packet that approval.evaluate bound to this exact session,
    # worktree, task and operation. `untrusted_approval_context` is
    # deliberately not consulted here.
    if critical_lane and approval_status != approval.STATUS_APPROVED:
        return (
            f"halt: approval_status is '{approval_status}' ({approval_reason}) for this "
            "critical-lane action; only a trusted approval packet bound to this session "
            "can lift this -- request human approval before any implementation step"
        )
    first_step = resolved.core_path[0] if resolved.core_path else "the route's deep playbook"
    return f"proceed to the '{first_step}' step"


def _follow_up_disposition(*, route: str, unmapped: bool) -> str:
    if unmapped:
        return "none until a human maps this route/task-type into obligations.py"
    return _FOLLOW_UP_BY_ROUTE.get(route, "follow the route's deep playbook for close-out")


def _scan_findings(fields: dict[str, str]) -> list[str]:
    return [name for name, text in fields.items() if secret_filter.scan(text)]


def _blocked_packet(
    *,
    route: str,
    task_type: str,
    project: str,
    goal: str,
    scope: str,
    target_state: str,
    exclusions: list[str],
    flagged_fields: list[str],
) -> dict:
    def redact(name: str, value: str) -> str:
        return _REDACTION_MARKER if name in flagged_fields else value

    exclusions_out = [redact(f"exclusions[{i}]", item) for i, item in enumerate(exclusions)]

    return {
        "schema_version": packet_schema.PACKET_SCHEMA_VERSION,
        "goal": redact("goal", goal),
        "project": project,
        "scope_and_exclusions": {
            "route": route,
            "task_type": task_type,
            "scope": redact("scope", scope),
            "exclusions": exclusions_out,
        },
        "target_state": redact("target_state", target_state),
        # Conservative by design: a blocked packet never carries the
        # caller's approval context through, and approval is not evaluated
        # at all -- the packet as a whole is not safe to act on yet.
        "untrusted_approval_context": packet_schema.APPROVAL_CONTEXT_NOT_PROVIDED,
        "approval_status": packet_schema.APPROVAL_STATUS_NOT_CHECKED,
        "approval_reason": "packet_blocked_before_approval_check",
        "required_context": [
            "blocked: possible secret/PII-shaped content detected in packet input "
            f"(fields: {', '.join(sorted(flagged_fields))}); redact and resubmit"
        ],
        "required_checks_evidence": [
            "blocked: do not proceed automatically until the flagged content is removed"
        ],
        "stop_conditions": [
            "possible secret or PII detected in packet input; halt and get human "
            "review before any automatic action"
        ],
        "next_automatic_action": (
            "halt: possible secret/PII detected in task input; do not dispatch to "
            "any provider or proceed automatically"
        ),
        "follow_up_disposition": "none until content is redacted and the packet is regenerated",
    }


def build_packet(
    *,
    route: str,
    task_type: str,
    project: str,
    goal: str,
    scope: str,
    target_state: str,
    exclusions: list[str] | None = None,
    untrusted_approval_context: str | None = None,
    user_facing: bool = False,
    staff_facing: bool = False,
    critical_lane: bool = False,
    session_id: str | None = None,
    worktree: str | os.PathLike | None = None,
    task_id: str | None = None,
    operation: str | None = None,
    state_dir: Path | None = None,
    config: dict | None = None,
    provider: object | None = None,
) -> dict:
    """Assemble one versioned compact execution packet. Raises
    `packet_schema.PacketValidationError` for missing/malformed required
    input. Returns a blocked packet (never raises) when secret/PII-shaped
    content is detected in the task context.

    `untrusted_approval_context` is carried through verbatim and grants no
    authority. `approval_status` / `approval_reason` come only from
    `approval.evaluate(...)` over `session_id`, `worktree`, `task_id`,
    `operation` (and `state_dir`); omit all four and the status is
    `not_checked`, which keeps a critical-lane packet halted."""
    errors = packet_schema.validate_input(
        route=route,
        task_type=task_type,
        project=project,
        goal=goal,
        scope=scope,
        target_state=target_state,
        exclusions=exclusions,
    )
    if errors:
        raise packet_schema.PacketValidationError(errors)

    exclusions = list(exclusions or [])

    scan_targets = {
        "goal": goal,
        "scope": scope,
        "target_state": target_state,
    }
    scan_targets.update({f"exclusions[{i}]": item for i, item in enumerate(exclusions)})
    if untrusted_approval_context:
        scan_targets["untrusted_approval_context"] = untrusted_approval_context

    flagged_fields = _scan_findings(scan_targets)
    if flagged_fields:
        return _blocked_packet(
            route=route,
            task_type=task_type,
            project=project,
            goal=goal,
            scope=scope,
            target_state=target_state,
            exclusions=exclusions,
            flagged_fields=flagged_fields,
        )

    resolved = obligations.resolve_obligations(
        route,
        task_type,
        user_facing=user_facing,
        staff_facing=staff_facing,
        critical_lane=critical_lane,
    )
    unmapped = resolved is None
    if unmapped:
        resolved = obligations.fallback_obligations(route, task_type)

    required_checks_evidence = list(resolved.required_checks_evidence)
    if not unmapped:
        risk_config = config if config is not None else _default_risk_config()
        risk_bucket = _resolve_risk_bucket(
            route=route, critical_lane=critical_lane, config=risk_config, provider=provider
        )
        if risk_bucket == "high":
            source = (
                "deterministic critical-lane override, decision layer not consulted"
                if critical_lane
                else "decision-layer typed judgment via the fake provider"
            )
            required_checks_evidence.append(
                f"risk bucket: high ({source}) -- add an independent second reviewer "
                "or Hafiz sign-off before commit"
            )

    approval_context_value = (
        untrusted_approval_context
        if untrusted_approval_context
        else packet_schema.APPROVAL_CONTEXT_NOT_PROVIDED
    )

    approval_status, approval_reason = _resolve_approval(
        session_id=session_id,
        worktree=worktree,
        task_id=task_id,
        operation=operation,
        state_dir=state_dir,
    )

    next_action = _next_automatic_action(
        resolved=resolved,
        unmapped=unmapped,
        approval_status=approval_status,
        approval_reason=approval_reason,
        critical_lane=critical_lane,
    )

    return {
        "schema_version": packet_schema.PACKET_SCHEMA_VERSION,
        "goal": goal,
        "project": project,
        "scope_and_exclusions": {
            "route": route,
            "task_type": task_type,
            "scope": scope,
            "exclusions": exclusions,
        },
        "target_state": target_state,
        "untrusted_approval_context": approval_context_value,
        "approval_status": approval_status,
        "approval_reason": approval_reason,
        "required_context": list(resolved.required_context),
        "required_checks_evidence": required_checks_evidence,
        "stop_conditions": list(resolved.stop_conditions),
        "next_automatic_action": next_action,
        "follow_up_disposition": _follow_up_disposition(route=route, unmapped=unmapped),
    }
