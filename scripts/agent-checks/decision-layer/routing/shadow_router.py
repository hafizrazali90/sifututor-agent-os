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
to import and call from a test suite with zero side effects. Nothing in
this repo imports it yet: it is advisory and not wired live.

Pipeline, in order, matching the build spec's "deterministic facts and
safety rules must always override the classifier's answer" and the PR #172
review finding that critical lanes must never be delegated to a provider:

  1. Deterministic facts and safety rules (`deterministic.py` and Bundle
     1's `secret_filter.py`), run on the raw text **before any provider
     request exists**. If the secret filter fires, or the text lands in
     any of the eight critical lanes, the router answers fully
     deterministically: the classifier's own top-ranked route, risk
     `critical`, `provider_called: False`, provider `"deterministic"`, and
     a `critical_lane:<lane>` reason. `engine.decide()` is never called.
  2. For non-critical text only, the classification call through Bundle
     1's decision layer (`engine.decide()`), for the one field that
     genuinely needs judgment: which workflow route applies. The provider
     never receives raw request text. Its `context` is a compact derived
     summary: the first sentence trimmed to at most 240 characters plus
     the short list of matched keyword tags. `sensitivity` is always
     `"low"` because anything higher never reaches this step.
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
import re
import sys
import time

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
import schema  # noqa: E402
import secret_filter  # noqa: E402

SCHEMA_VERSION = 1
DECISION_TYPE = "routing.workflow_route"
DETERMINISTIC_PROVIDER = "deterministic"

MODEL_RECOMMENDATION_REASON = (
    "AGENTS.md and docs/agent-playbooks/ define no frontier-model vs "
    "fallback-model distinction in this workspace; per the build spec, "
    "this field is intentionally left unset rather than invented."
)

# The provider context is a derived summary, never raw text: the first
# sentence, trimmed to this many characters, plus matched keyword tags.
CONTEXT_SUMMARY_CHARS = 240
_CONTEXT_MAX_TAGS = 8

_SENTENCE_BOUNDARY = re.compile(r"(?<=[.?!])\s+")


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


def derive_context_summary(text: str, *, limit: int = CONTEXT_SUMMARY_CHARS) -> str:
    """The first sentence of the request, quoted/pasted spans removed and
    whitespace collapsed, trimmed to at most `limit` characters. This is
    the only fragment of the request a provider ever sees."""
    cleaned = " ".join(deterministic.strip_quoted_and_pasted_spans(text or "").split())
    if not cleaned:
        return ""
    first_sentence = _SENTENCE_BOUNDARY.split(cleaned, maxsplit=1)[0]
    return first_sentence[:limit].rstrip()


def build_provider_context(
    text: str, *, task_type_override: str | None, pasted_report: bool
) -> str:
    """Compact derived context for a provider request: summary plus tags.
    Never the raw text and never `text[:N]` of it."""
    tags = list(classifier.matched_route_tags(text))
    if task_type_override:
        tags.append(f"task_type:{task_type_override}")
    if pasted_report:
        tags.append("pasted_report")
    tags = tags[:_CONTEXT_MAX_TAGS]
    summary = derive_context_summary(text)
    return f"summary: {summary}\ntags: {', '.join(tags) if tags else 'none'}"


def _deterministic_decision_response(*, answer: str, reason: str, started: float) -> dict:
    """A decision-layer-shaped response for the path that never reaches
    `engine.decide()`. Same field set as `schema.response_schema_fields()`
    so `observability.build_record` treats it exactly like any other."""
    return {
        "schema_version": schema.SCHEMA_VERSION,
        "decision_type": DECISION_TYPE,
        "answer": answer,
        "confidence": 1.0,
        "provider": DETERMINISTIC_PROVIDER,
        "fallback_used": False,
        "authoritative": False,
        "latency_ms": (time.monotonic() - started) * 1000.0,
        "cost": 0.0,
        "usage_input_tokens": None,
        "usage_output_tokens": None,
        "outcome": "deterministic",
        "reason": reason,
    }


def _secret_filter_override(text: str) -> deterministic.RiskOverride | None:
    """Map Bundle 1's secret-filter findings onto a critical lane. A
    credential-shaped finding is the secrets lane; a PII-shaped finding is
    the private-production-data lane. Either way the text is never sent."""
    findings = secret_filter.scan(text)
    if not findings:
        return None
    lane = "secrets_credentials" if any(f.startswith("credential:") for f in findings) else "private_production_data"
    return deterministic.RiskOverride(
        risk_level="critical", reason=deterministic.critical_lane_reason(lane), lane=lane
    )


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
    started = time.monotonic()
    text = text or ""

    # Step 1: deterministic facts and safety rules, always first, and
    # always before any provider request is constructed.
    project_decision = deterministic.resolve_project(text, declared_project)
    risk_override = _secret_filter_override(text) or deterministic.detect_critical_risk(text)
    pasted_report = deterministic.is_pasted_report(text)
    task_type_override = deterministic.detect_task_type_override(text)
    ranked_routes = classifier.rank_workflow_routes(text, has_active_task=has_active_task)

    if risk_override is not None:
        # Critical lane: fully deterministic. The classifier's own top pick
        # is the route; no provider request exists and engine.decide() is
        # never reached. "High sensitivity" is not permission to transmit.
        provider_called = False
        workflow_route = ranked_routes[0]
        decision_response = _deterministic_decision_response(
            answer=workflow_route, reason=risk_override.reason, started=started
        )
    else:
        # Step 2: the classification call, for non-critical text only. The
        # provider sees a compact derived summary plus tags, never raw text.
        provider_called = True
        decision_request = {
            "schema_version": SCHEMA_VERSION,
            "decision_type": DECISION_TYPE,
            "options": list(ranked_routes),
            "context": build_provider_context(
                text, task_type_override=task_type_override, pasted_report=pasted_report
            ),
            "sensitivity": "low",
        }
        decision_response = engine.decide(decision_request, config=config, provider=provider)
        workflow_route = decision_response["answer"]
        if workflow_route not in catalog.WORKFLOW_ROUTES:
            # A provider (fake or otherwise) is not allowed to invent a
            # route outside the known vocabulary; fall back to the
            # classifier's own top pick, which is always a valid route.
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
            "lane": risk_override.lane if risk_override is not None else None,
            "reason": risk_override.reason if risk_override is not None else "default_for_workflow_route",
        },
        "required_playbooks": required_playbooks,
        "relevant_documents": relevant_documents,
        "model_recommendation": None,
        "model_recommendation_reason": MODEL_RECOMMENDATION_REASON,
        "provider_called": provider_called,
        "pasted_content_detected": pasted_report,
        "open_tabs_considered_for_classification": False,
        "open_tabs_received": list(open_tabs or []),
        "deterministic_overrides_applied": deterministic_overrides_applied,
        "observability": observability.build_record(decision_response),
    }
