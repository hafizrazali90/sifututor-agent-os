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
    approval_reference: str | None  -- see the hard limit below
    user_facing: bool = False       -- triggers small-change's conditional
                                        E2E/related-impact obligations
    staff_facing: bool = False      -- triggers the staff-documentation
                                        context item
    critical_lane: bool = False     -- triggers the Universal Safety Rule
                                        halt (payments/auth/migrations/etc.)
    config: dict | None = None      -- decision-layer config override; if
                                        omitted, uses a config that is
                                        locked to the fake provider and
                                        never reads the real process
                                        environment (see
                                        `_default_risk_config`)
    provider: object | None = None  -- decision-layer provider override,
                                        threaded straight into
                                        `engine.decide(..., provider=...)`

Hard limit (bundle-3-build-spec.md): `validated_approval_reference` can
only ever be the exact string the caller supplied, or the
`packet_schema.APPROVAL_REFERENCE_NOT_PROVIDED` sentinel when none was
supplied. No obligation lookup, decision-layer call, or risk estimate in
this module is ever allowed to write to that field.
"""

from __future__ import annotations

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
        "after commit, no defect_analysis or review step is owed; close the linked "
        "GitHub issue if one exists"
    ),
    "refactor": (
        "after commit, confirm no behavior actually changed (qa evidence) before "
        "closing the linked issue"
    ),
    "docs": (
        "after commit, no QA/review step is owed for a docs-only route; close the "
        "linked issue if one exists"
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


def _next_automatic_action(
    *,
    resolved: "obligations.ObligationSet",
    unmapped: bool,
    approval_reference_value: str,
    critical_lane: bool,
) -> str:
    if unmapped:
        return (
            "halt: read docs/agent-playbooks/task-router.md, verify.md, qa.md, and "
            "commit.md directly before continuing (no triggered-obligation mapping "
            "for this route/task-type)"
        )
    if critical_lane and approval_reference_value == packet_schema.APPROVAL_REFERENCE_NOT_PROVIDED:
        return (
            "halt: no validated approval reference for this critical-lane action; "
            "request human approval before any implementation step"
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
        # Conservative by design: a blocked/halted packet never carries a
        # real approval reference through, even if the reference itself
        # was clean -- the packet as a whole is not safe to act on yet.
        "validated_approval_reference": packet_schema.APPROVAL_REFERENCE_NOT_PROVIDED,
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
    approval_reference: str | None = None,
    user_facing: bool = False,
    staff_facing: bool = False,
    critical_lane: bool = False,
    config: dict | None = None,
    provider: object | None = None,
) -> dict:
    """Assemble one versioned compact execution packet. Raises
    `packet_schema.PacketValidationError` for missing/malformed required
    input. Returns a blocked packet (never raises) when secret/PII-shaped
    content is detected in the task context."""
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
    if approval_reference:
        scan_targets["approval_reference"] = approval_reference

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

    approval_reference_value = (
        approval_reference if approval_reference else packet_schema.APPROVAL_REFERENCE_NOT_PROVIDED
    )

    next_action = _next_automatic_action(
        resolved=resolved,
        unmapped=unmapped,
        approval_reference_value=approval_reference_value,
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
        "validated_approval_reference": approval_reference_value,
        "required_context": list(resolved.required_context),
        "required_checks_evidence": required_checks_evidence,
        "stop_conditions": list(resolved.stop_conditions),
        "next_automatic_action": next_action,
        "follow_up_disposition": _follow_up_disposition(route=route, unmapped=unmapped),
    }
