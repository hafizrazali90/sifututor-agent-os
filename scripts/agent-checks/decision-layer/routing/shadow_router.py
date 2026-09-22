#!/usr/bin/env python3
"""Shadow-mode routing/context decision module (Bundle 2, issue #159).

`route()` is the single public entry point. Given a description of an
incoming task/request, it produces one **shadow decision** -- a
recommendation, never an automatic action -- covering:

    project, workflow_route, task_type, risk_level, required_playbooks,
    relevant_documents, and an explicit note that no frontier-model vs
    fallback-model recommendation is included (see module docstring
    below for why).

Nothing in this module calls or triggers a skill/hook, writes anywhere, or
changes what any real hook, skill, or `.claude/settings.json` registration
does. It is purely a function from a request dict to a decision dict, safe
to import and call from a test suite with zero side effects.

Pipeline, in order, matching the build spec's "deterministic facts and
safety rules must always override the classifier's answer":

  1. Bundle 2's own deterministic pre-policy layer (`deterministic.py`):
     project override resolution and critical-risk forcing. Both can
     short-circuit/override later steps; neither ever calls a provider.
  2. The actual classification call, through Bundle 1's decision layer
     (`engine.decide()`), for the one field that genuinely needs judgment:
     which workflow route applies. `engine.decide()` itself still runs
     Bundle 1's own secret filter and generic pre_policy layer first, and
     dispatches to the configured provider (FakeProvider by default, the
     only provider this module's own tests ever exercise).
  3. Deterministic lookups (`catalog.py`) turn the resolved workflow_route
     into required playbooks, a default risk level (unless step 1 already
     forced one), a default task type (unless a task-type override fired),
     and a short list of documents worth looking up (not their content).

On the frontier-model / fallback-model field: the build spec asks for this
"if this workspace's docs define such a distinction". `AGENTS.md` and
`docs/agent-playbooks/` were checked (see the PR body for the exact
search) and define no such distinction anywhere in this repo today --
there is no documented frontier/fallback model tiering concept to route
against. Per the build spec's own instruction ("skip this field rather
than making it up"), `route()` always returns `model_recommendation` as
`None` with a `model_recommendation_reason` explaining why, instead of
inventing a tiering scheme.
"""

from __future__ import annotations

from pathlib import Path
import sys

_ROUTING_DIR = Path(__file__).resolve().parent
_DECISION_LAYER_DIR = _ROUTING_DIR.parent
for _path in (_ROUTING_DIR, _DECISION_LAYER_DIR):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import catalog  # noqa: E402
import classifier  # noqa: E402
import deterministic  # noqa: E402
import engine  # noqa: E402
import observability  # noqa: E402

SCHEMA_VERSION = 1

MODEL_RECOMMENDATION_REASON = (
    "AGENTS.md and docs/agent-playbooks/ define no frontier-model vs "
    "fallback-model distinction in this workspace; per the build spec, "
    "this field is intentionally left unset rather than invented."
)

_CONTEXT_PREVIEW_CHARS = 2000


def _derive_koda_query(text: str) -> str:
    """A short, deterministic search query -- not a summary -- for a
    caller to hand to Koda memory_search. Just the first sentence/clause
    of the cleaned request text, trimmed to a reasonable length."""
    cleaned = " ".join((text or "").split())
    for stop in (". ", "? ", "! ", "\n"):
        idx = cleaned.find(stop)
        if 0 < idx <= 120:
            return cleaned[: idx + 1].strip()
    return cleaned[:120].strip()


def _build_relevant_documents(
    *, workflow_route: str, project_decision: deterministic.ProjectDecision, text: str
) -> list[dict[str, str]]:
    """Things worth looking up for this request -- a list of lookups, not
    their content. Deterministic given (workflow_route, project, text);
    never itself a provider call."""
    documents: list[dict[str, str]] = []

    if workflow_route != "question":
        documents.append({"type": "koda_memory_search", "query": _derive_koda_query(text)})

    if project_decision.project:
        koda_tag = catalog.KODA_PROJECT_TAGS.get(project_decision.project)
        if koda_tag:
            documents.append({"type": "koda_project_tag", "tag": koda_tag})

    if workflow_route in ("handoff", "continuation", "save_session"):
        documents.append(
            {
                "type": "handoff_file",
                "hint": ".agent-os/handoffs/*.md -- most recent handoff relevant to this thread/project",
            }
        )
        documents.append({"type": "session_map", "hint": "current Session Map entry for this task"})

    if workflow_route in ("research", "new_side_task"):
        documents.append(
            {
                "type": "mission_ledger",
                "scope": project_decision.project or "cross-project",
            }
        )

    return documents


def route(
    text: str,
    *,
    declared_project: str | None = None,
    open_tabs: list[str] | None = None,
    has_active_task: bool = False,
    provider: object | None = None,
    config: dict | None = None,
) -> dict:
    """Produce one shadow routing/context decision for `text`.

    `open_tabs` is accepted purely so a caller can pass IDE context
    through; this module deliberately never reads it for classification
    (build spec: "an IDE-tab-contamination scenario -- irrelevant open-file
    context should not hijack routing"). It is echoed back unmodified in
    the response so a caller can see what was ignored and why.
    """
    text = text or ""

    # Step 1: deterministic facts and safety rules, always first.
    project_decision = deterministic.resolve_project(text, declared_project)
    risk_override = deterministic.detect_critical_risk(text)
    pasted_report = deterministic.is_pasted_report(text)
    task_type_override = deterministic.detect_task_type_override(text)

    # Step 2: the actual classification call, through Bundle 1's decision
    # layer. The classifier module computes the ranked options; FakeProvider
    # (or whatever `provider`/`config` the caller supplies) decides which
    # one is returned as the answer.
    ranked_routes = classifier.rank_workflow_routes(text, has_active_task=has_active_task)
    decision_request = {
        "schema_version": SCHEMA_VERSION,
        "decision_type": "routing.workflow_route",
        "options": list(ranked_routes),
        "context": text[:_CONTEXT_PREVIEW_CHARS],
        "sensitivity": "high" if risk_override is not None else "low",
    }
    decision_response = engine.decide(decision_request, config=config, provider=provider)
    workflow_route = decision_response["answer"]
    if workflow_route not in catalog.WORKFLOW_ROUTES:
        # A provider (fake or otherwise) is not allowed to invent a route
        # outside the known vocabulary; fall back to the classifier's own
        # top pick, which is always a valid route.
        workflow_route = ranked_routes[0]

    # Step 3: deterministic lookups from the resolved route/overrides.
    risk_level = risk_override.risk_level if risk_override is not None else catalog.DEFAULT_RISK_BY_ROUTE[workflow_route]
    task_type = task_type_override or catalog.DEFAULT_TASK_TYPE_BY_ROUTE[workflow_route]
    required_playbooks = list(catalog.REQUIRED_PLAYBOOKS_BY_ROUTE[workflow_route])
    relevant_documents = _build_relevant_documents(
        workflow_route=workflow_route, project_decision=project_decision, text=text
    )

    deterministic_overrides_applied: list[str] = []
    if project_decision.source in ("declared_param", "declared_in_text"):
        deterministic_overrides_applied.append(f"project_override:{project_decision.source}")
    if risk_override is not None:
        deterministic_overrides_applied.append(f"risk_override:{risk_override.reason}")

    return {
        "schema_version": SCHEMA_VERSION,
        "project": {
            "value": project_decision.project,
            "source": project_decision.source,
        },
        "workflow_route": {
            "value": workflow_route,
            "confidence": decision_response["confidence"],
            "authoritative": decision_response["authoritative"],
            "fallback_used": decision_response["fallback_used"],
            "provider": decision_response["provider"],
        },
        "task_type": task_type,
        "risk_level": {
            "value": risk_level,
            "forced": risk_override is not None,
            "reason": risk_override.reason if risk_override is not None else "default_for_workflow_route",
        },
        "required_playbooks": required_playbooks,
        "relevant_documents": relevant_documents,
        "model_recommendation": None,
        "model_recommendation_reason": MODEL_RECOMMENDATION_REASON,
        "pasted_content_detected": pasted_report,
        "open_tabs_considered_for_classification": False,
        "open_tabs_received": list(open_tabs or []),
        "deterministic_overrides_applied": deterministic_overrides_applied,
        "observability": observability.build_record(decision_response),
    }
