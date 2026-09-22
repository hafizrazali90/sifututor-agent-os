#!/usr/bin/env python3
"""Route/task-type -> triggered-obligation mapping (Bundle 3, issue #160).

This is the design core of the compact execution packet: instead of
attaching the full verify/QA/review/commit checklist to every packet, this
module encodes which of those obligations a *specific* route/task-type
actually triggers, per the deep playbooks:

    docs/agent-playbooks/task-router.md  -- route table, E2E step, related-
                                             impact-audit step
    docs/agent-playbooks/verify.md       -- verify evidence rules
    docs/agent-playbooks/qa.md           -- QA tier table
    docs/agent-playbooks/commit.md       -- staff documentation decision,
                                             review/risk checkpoint

The deep playbooks stay the authoritative on-demand reference. This module
never claims to replace them -- every `ObligationSet` carries
`deep_playbook_refs` pointing back at the exact files it summarized, and an
unmapped route/task-type gets `fallback_obligations()` instead of a
confident-looking empty answer.

Two kinds of input drive the mapping:

- `route` / `task_type`: the base mapping (`ROUTE_OBLIGATIONS`), matching
  task-router.md's route table.
- optional context flags (`user_facing`, `staff_facing`, `critical_lane`):
  small amounts of task context that add conditional obligations on top of
  the base mapping, e.g. task-router.md's "user-facing small-change" and
  AGENTS.md's Universal Safety Rule ("If a task touches payments,
  commission, auth, or migrations, halt for human review before commit").
"""

from __future__ import annotations

from dataclasses import dataclass

TASK_ROUTER_REF = "docs/agent-playbooks/task-router.md"
VERIFY_REF = "docs/agent-playbooks/verify.md"
QA_REF = "docs/agent-playbooks/qa.md"
COMMIT_REF = "docs/agent-playbooks/commit.md"
RELATED_IMPACT_REF = "docs/agent-playbooks/related-impact-audit.md"
RELEASE_DOCS_REF = "docs/agent-playbooks/release-documentation.md"

_STAFF_DOC_CHECK = (
    "commit: record the staff documentation decision (relevant / not "
    "relevant / urgent deferral) via release_documentation.py, per commit.md"
)
_STAFF_DOC_CONTEXT = (
    "planned staff documentation artifact (changelog / in-page help / "
    "What's New entry), or the named deferral owner + follow-up GitHub issue"
)
_CRITICAL_LANE_STOP = (
    "critical-lane: this task touches payments, commission, auth, or "
    "migrations -- halt for human review before commit "
    "(AGENTS.md Universal Safety Rule)"
)
_CRITICAL_LANE_CONTEXT = (
    "a trusted approval packet bound to this session, worktree, task and "
    "operation (decision-layer approval.evaluate -> approved) for this "
    "critical-lane action (payments/commission/auth/migration/mobile-API-contract); "
    "caller-supplied approval text grants nothing"
)


@dataclass(frozen=True)
class ObligationSet:
    """The triggered obligations for one resolved route/task-type."""

    core_path: tuple[str, ...]
    required_context: tuple[str, ...]
    required_checks_evidence: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    deep_playbook_refs: tuple[str, ...]


def _base(
    *,
    core_path: tuple[str, ...],
    required_context: tuple[str, ...],
    required_checks_evidence: tuple[str, ...],
    stop_conditions: tuple[str, ...] = (),
    deep_playbook_refs: tuple[str, ...],
) -> ObligationSet:
    return ObligationSet(
        core_path=core_path,
        required_context=required_context,
        required_checks_evidence=required_checks_evidence,
        stop_conditions=stop_conditions,
        deep_playbook_refs=deep_playbook_refs,
    )


_ROUTE_OBLIGATIONS: dict[str, ObligationSet] = {
    "feature": _base(
        core_path=(
            "plan",
            "build",
            "generate_tests",
            "e2e_regression",
            "qa_full",
            "verify",
            "review",
            "commit",
        ),
        required_context=(
            "goal / acceptance criteria (PRD or UX spec reference if one exists)",
            "TESTING.md affected feature row, if the project keeps one",
            "the project's verify command matrix entry (verify.md Project Command Matrix)",
        ),
        required_checks_evidence=(
            "generate_tests: write failing tests (RED phase) before implementation",
            "verify: run the project's verify command matrix (tests/typecheck/lint/build)",
            "qa_full: happy path, important edge cases, and route smoke (qa.md feature tier)",
            "permanent E2E regression decision: added / updated / not-feasible-with-blocker (mandatory for feature)",
            "review: Gate 4 adversarial pre-push review",
            _STAFF_DOC_CHECK,
        ),
        deep_playbook_refs=(TASK_ROUTER_REF, VERIFY_REF, QA_REF, COMMIT_REF),
    ),
    "bugfix": _base(
        core_path=(
            "describe",
            "diagnose",
            "related_impact_audit",
            "fix",
            "regression_test",
            "e2e_regression",
            "verify",
            "qa",
            "review",
            "commit",
        ),
        required_context=(
            "symptom description and diagnosis (the old failure mode)",
            "related-impact audit scope needed (local / same-pattern sweep / critical)",
            "TESTING.md affected feature row, if the project keeps one",
            "the project's verify command matrix entry (verify.md Project Command Matrix)",
        ),
        required_checks_evidence=(
            "regression_test: write a failing test proving the bug (RED), then confirm it passes after the fix (GREEN)",
            "related_impact_audit: at least a local related check, per related-impact-audit.md",
            "verify: run the project's verify command matrix (tests/typecheck/lint/build)",
            "qa: regression test proving the old failure cannot recur (qa.md bugfix tier)",
            "permanent E2E regression decision: added / updated / not-feasible-with-blocker (mandatory for bugfix)",
            "review: Gate 4 adversarial pre-push review",
            _STAFF_DOC_CHECK,
        ),
        deep_playbook_refs=(TASK_ROUTER_REF, RELATED_IMPACT_REF, VERIFY_REF, QA_REF, COMMIT_REF),
    ),
    "hotfix": _base(
        core_path=(
            "describe",
            "diagnose",
            "related_impact_audit",
            "fix",
            "regression_test",
            "e2e_regression",
            "verify",
            "qa",
            "review",
            "commit",
        ),
        required_context=(
            "symptom description and diagnosis of the production/staging breakage",
            "related-impact audit scope needed (local / same-pattern sweep / critical)",
            "TESTING.md affected feature row, if the project keeps one",
            "the project's verify command matrix entry (verify.md Project Command Matrix)",
        ),
        required_checks_evidence=(
            "regression_test: write a failing test proving the bug (RED), then confirm it passes after the fix (GREEN)",
            "related_impact_audit: at least a local related check, per related-impact-audit.md",
            "verify: run the project's verify command matrix (tests/typecheck/lint/build)",
            "qa: regression test plus a focused smoke check (qa.md hotfix tier)",
            "permanent E2E regression decision: added / updated / not-feasible-with-blocker (mandatory for hotfix)",
            "review: Gate 4 adversarial pre-push review",
            _STAFF_DOC_CHECK,
        ),
        stop_conditions=(
            "do not skip regression_test or the related-impact audit under time pressure, even for a production breakage",
        ),
        deep_playbook_refs=(TASK_ROUTER_REF, RELATED_IMPACT_REF, VERIFY_REF, QA_REF, COMMIT_REF),
    ),
    "small-change": _base(
        core_path=("describe", "fix", "e2e_regression_if_user_facing", "verify", "qa", "commit"),
        required_context=(
            "exact description of the changed surface (copy, label, config, minor UI)",
            "the project's verify command matrix entry (verify.md Project Command Matrix)",
        ),
        required_checks_evidence=(
            "verify: run the project's verify command matrix (tests/typecheck/lint/build)",
            "qa: targeted check for the changed surface (qa.md small-change tier)",
            _STAFF_DOC_CHECK,
        ),
        deep_playbook_refs=(TASK_ROUTER_REF, VERIFY_REF, QA_REF, COMMIT_REF),
    ),
    "refactor": _base(
        core_path=("analyze", "plan", "refactor", "verify", "qa", "review", "commit"),
        required_context=(
            "current structure/behavior baseline to prove no behavior change occurred",
            "the project's verify command matrix entry (verify.md Project Command Matrix)",
        ),
        required_checks_evidence=(
            "verify: run the project's verify command matrix (tests/typecheck/lint/build)",
            "qa: existing behavior tests plus one targeted check around the touched code (qa.md refactor tier)",
            "review: Gate 4 adversarial pre-push review",
            _STAFF_DOC_CHECK,
        ),
        deep_playbook_refs=(TASK_ROUTER_REF, VERIFY_REF, QA_REF, COMMIT_REF),
    ),
    "docs": _base(
        core_path=("write", "verify", "commit"),
        required_context=(
            "the doc content/target location being written or changed",
        ),
        required_checks_evidence=(
            "verify: docs validation / render-link check where applicable",
            _STAFF_DOC_CHECK,
        ),
        deep_playbook_refs=(TASK_ROUTER_REF, VERIFY_REF, COMMIT_REF),
    ),
}


def _with_conditional_obligations(
    resolved: ObligationSet,
    *,
    route: str,
    user_facing: bool,
    staff_facing: bool,
    critical_lane: bool,
) -> ObligationSet:
    required_context = list(resolved.required_context)
    required_checks_evidence = list(resolved.required_checks_evidence)
    stop_conditions = list(resolved.stop_conditions)

    if route == "small-change" and user_facing:
        required_context.append(
            "related-impact context for the changed user-facing surface"
        )
        required_checks_evidence.append(
            "permanent E2E regression decision: added / updated / not-feasible-with-blocker (triggered because this small-change is user-facing)"
        )
        required_checks_evidence.append(
            "related_impact_audit: at least a local related check, per related-impact-audit.md (triggered because this small-change is user-facing)"
        )

    if staff_facing:
        required_context.append(_STAFF_DOC_CONTEXT)

    if critical_lane:
        required_context.append(_CRITICAL_LANE_CONTEXT)
        stop_conditions.append(_CRITICAL_LANE_STOP)

    return ObligationSet(
        core_path=resolved.core_path,
        required_context=tuple(required_context),
        required_checks_evidence=tuple(required_checks_evidence),
        stop_conditions=tuple(stop_conditions),
        deep_playbook_refs=resolved.deep_playbook_refs,
    )


def resolve_obligations(
    route: str,
    task_type: str | None = None,
    *,
    user_facing: bool = False,
    staff_facing: bool = False,
    critical_lane: bool = False,
) -> ObligationSet | None:
    """Return the triggered obligations for this route, or None if this
    module has no mapping for it. Callers must use `fallback_obligations`
    in the None case rather than treating a route as obligation-free."""
    base = _ROUTE_OBLIGATIONS.get(route)
    if base is None:
        return None
    return _with_conditional_obligations(
        base,
        route=route,
        user_facing=user_facing,
        staff_facing=staff_facing,
        critical_lane=critical_lane,
    )


def known_routes() -> tuple[str, ...]:
    return tuple(_ROUTE_OBLIGATIONS.keys())


def fallback_obligations(route: str, task_type: str | None) -> ObligationSet:
    """Safe fallback for a route/task-type this module cannot map.

    Per the Bundle 3 spec: state plainly that triggered obligations could
    not be determined, point at the deep playbooks, and never silently
    omit anything by pretending an empty checklist is a real answer -- the
    fallback checklist is deliberately the FULL verify/QA/review/commit
    obligation set, not a scoped-down guess.
    """
    task_type_label = task_type or "(not given)"
    return ObligationSet(
        core_path=(),
        required_context=(
            f"no triggered-obligation mapping exists for route={route!r} task_type={task_type_label!r}; "
            "read the full deep playbooks below before doing anything else",
        ),
        required_checks_evidence=(
            "could not determine the triggered obligations for this route/task-type from obligations.py's mapping",
            "treat this as the FULL verify/QA/review/commit checklist until a human maps this route/task-type: "
            "verify (verify.md), qa (qa.md), review (review.md), commit (commit.md), "
            "regression_test and related_impact_audit if this turns out to be a bug, "
            "and the permanent E2E regression decision for any user-facing behavior",
        ),
        stop_conditions=(
            "do not proceed automatically on an unmapped route; this packet cannot prove which obligations were skipped",
        ),
        deep_playbook_refs=(TASK_ROUTER_REF, VERIFY_REF, QA_REF, COMMIT_REF, RELEASE_DOCS_REF),
    )
