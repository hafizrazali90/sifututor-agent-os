#!/usr/bin/env python3
"""Review and evidence triage orchestrator (Bundle 5, issue #166).

Entry point: `triage_change(payload, config=None, provider=None)`.

Runs all eight deterministic signal classifiers -- file_risk, scope_creep,
weakened_tests, ci_failure, comment_triage, acceptance_evidence,
staff_doc_relevance, human_journey_evidence -- and computes one overall
attention priority for the change.

Deterministic pre-policy is given final authority over the overall
priority, mirroring decision-layer's own `pre_policy.py` pattern and
AGENTS.md's critical-lane rule: when any individual signal has already
classified "high" (every signal above is itself fully deterministic --
none of them ever call a provider), the overall priority is
deterministically "high" and Bundle 1's decision layer is never dispatched
to at all. This is what makes a payments/auth/migrations change
deterministically flagged regardless of what a provider would have
guessed: `file_risk.classify()` alone already produces "high" before this
module even considers asking anyone.

Only when no signal came back "high" does this module route the remaining
"how much attention should a human give this, overall" question through
Bundle 1's decision layer (`engine.decide`, provider "fake" by default) --
this is the "Route through Bundle 1's decision layer (fake provider only)"
requirement from the task specification. Only aggregate counts are sent as
context (never comment bodies, file contents, or task free text), the
routed answer is always forced back to non-authoritative in the final
report regardless of what the decision layer itself reports, and nothing
in this module or its tests ever configures a live provider.
"""

from __future__ import annotations

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
_DECISION_LAYER_DIR = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(_DECISION_LAYER_DIR))

import acceptance_evidence  # noqa: E402
import ci_failure  # noqa: E402
import comment_triage  # noqa: E402
import config as decision_layer_config  # noqa: E402
import contract  # noqa: E402
import engine  # noqa: E402
import file_risk  # noqa: E402
import human_journey_evidence  # noqa: E402
import provider_fake  # noqa: E402
import scope_creep  # noqa: E402
import staff_doc_relevance  # noqa: E402
import weakened_tests  # noqa: E402

SCHEMA_VERSION = 1

OVERALL_DECISION_TYPE = "review_triage.overall_attention"
_OVERALL_OPTIONS = ["low", "medium", "high"]

_SIGNAL_MODULES = (
    file_risk,
    scope_creep,
    weakened_tests,
    ci_failure,
    comment_triage,
    acceptance_evidence,
    staff_doc_relevance,
    human_journey_evidence,
)


def _summarize_for_decision_layer(payload: dict, signals: list[dict]) -> str:
    """A short, aggregate-only summary for the decision-layer request's
    `context` field. Deliberately counts, not content: never a comment
    body, a file's contents, or the raw task description, so nothing
    sensitive is ever handed to a provider (data minimization, per Bundle
    1's own design)."""
    changed_file_count = len(payload.get("changed_files") or [])
    flagged_signal_count = sum(1 for signal in signals if signal["flags"])
    total_flag_count = sum(len(signal["flags"]) for signal in signals)
    return (
        f"changed_files={changed_file_count} "
        f"flagged_signals={flagged_signal_count} "
        f"total_flags={total_flag_count}"
    )


def _deterministic_overall(signals: list[dict]) -> str | None:
    """The deterministic pre-policy layer for the overall priority. Returns
    a priority the instant any signal is already "high", before any
    provider is ever considered."""
    if any(signal["priority"] == "high" for signal in signals):
        return "high"
    return None


def run_signals(payload: dict) -> list[dict]:
    """Run every deterministic signal classifier and return the list of
    signal records, in a fixed, documented order."""
    return [module.classify(payload) for module in _SIGNAL_MODULES]


def triage_change(payload: dict, *, config: dict | None = None, provider: object | None = None) -> dict:
    """Classify one change under review.

    Never raises on a well-formed payload, never calls any provider other
    than the one explicitly passed in (or the offline fake provider, by
    default), and never marks anything as passed or verified -- see
    `contract.py` for the structural guarantee and
    `test_never_marks_passed_or_verified.py` for the proof across every
    fixture this module ships.
    """
    signals = run_signals(payload)

    overall_priority = _deterministic_overall(signals)
    if overall_priority is not None:
        overall_source = "deterministic"
        overall_reason = (
            "at least one signal deterministically classified high priority; "
            "the decision layer was never dispatched to"
        )
    else:
        cfg = decision_layer_config.load_config(env={}) if config is None else config
        active_provider = provider if provider is not None else provider_fake.FakeProvider(scenario="ok")
        request = {
            "schema_version": 1,
            "decision_type": OVERALL_DECISION_TYPE,
            "options": list(_OVERALL_OPTIONS),
            "context": _summarize_for_decision_layer(payload, signals),
            "sensitivity": "low",
        }
        response = engine.decide(request, config=cfg, provider=active_provider)
        overall_priority = response["answer"] if response["answer"] in _OVERALL_OPTIONS else "medium"
        overall_source = "provider"
        overall_reason = (
            f"routed through Bundle 1's decision layer "
            f"(provider={response['provider']!r}, outcome={response['outcome']!r}, "
            f"fallback_used={response['fallback_used']!r})"
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "signals": signals,
        "overall_attention_priority": overall_priority,
        "overall_decision_source": overall_source,
        "overall_reason": overall_reason,
        # Fixed, not derived from any signal or provider answer -- this
        # report can never claim to be authoritative or to have verified
        # anything, structurally, regardless of what any signal computes.
        "advisory_only": True,
        "authoritative": False,
        "never_replaces": list(contract.NEVER_REPLACES),
    }
