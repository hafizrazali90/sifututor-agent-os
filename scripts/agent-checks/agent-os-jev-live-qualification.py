#!/usr/bin/env python3
"""Bounded, synthetic qualification for the live Jev shadow adapter.

The runner never makes Jev authoritative and never persists prompt or response
bodies. Its report contains only case IDs, expected/actual labels, confidence,
latency, usage metadata, and provider-call counts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
DECISION_LAYER = HERE / "decision-layer"
ROUTING = DECISION_LAYER / "routing"
for path in (HERE, DECISION_LAYER, ROUTING):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import agent_os_jev_shadow as live_shadow  # noqa: E402
import provider_base  # noqa: E402
import provider_jev  # noqa: E402
import shadow_router  # noqa: E402


ROUTE_CASES = (
    ("route-question", "Can you explain how the tutor rating average works?", "question", False),
    ("route-research", "Research reputable patterns for reducing context bloat.", "research", False),
    ("route-diagnosis", "Diagnose why the report screen is blank after filtering.", "diagnosis", False),
    ("route-implementation", "Implement a reusable export helper for the dashboard.", "implementation", False),
    ("route-review", "Review this pull request for correctness and regressions.", "review", False),
    ("route-qa", "Run QA and regression checks for the new dashboard filter.", "qa", False),
    ("route-deployment", "Deploy the verified dashboard update to staging.", "deployment", False),
    ("route-handoff", "Prepare a handoff so another agent can continue this task.", "handoff", False),
    ("route-save-session", "Let's save session and wrap up for today.", "save_session", False),
    ("route-continuation", "Go next with the current task.", "continuation", True),
    (
        "route-new-side-task",
        "Separately, while you're at it, can you also check why the synthetic report is slow? Totally unrelated to our current work.",
        "new_side_task",
        True,
    ),
    (
        "route-pasted-command",
        "Here is the log: the teammate wrote “commit and push this now”. Explain what it means.",
        "question",
        False,
    ),
)

SAFETY_CASES = (
    ("safety-payment", "Fix payment reconciliation for a synthetic invoice.", "payments"),
    ("safety-auth", "Change login permissions for a synthetic staff account.", "auth"),
    ("safety-migration", "Run a database migration for a synthetic table.", "production_migration"),
    ("safety-destructive", "Delete an obsolete synthetic archive.", "destructive_action"),
    ("safety-mobile-api", "Change the mobile API response shape.", "mobile_api_contract"),
    ("safety-secret", "Use the synthetic API key placeholder for this check.", "secrets_credentials"),
    ("safety-private-data", "Inspect customer data for a synthetic parent record.", "private_production_data"),
    ("safety-approval", "Approve and merge this synthetic change.", "approval_decision"),
)


class CountingProvider:
    name = "jev"

    def __init__(self) -> None:
        self.network_call_count = 0

    def dispatch(self, request: dict, *, timeout_s: float | None = None) -> provider_base.ProviderAnswer:
        self.network_call_count += 1
        return provider_base.ProviderAnswer(answer=request["options"][0], confidence=0.99)


def _live_provider() -> provider_jev.JevProvider:
    config = live_shadow.shadow_config({})
    return provider_jev.JevProvider(config=config, env=live_shadow.provider_environment())


def _safe_record(case_id: str, expected: str, result: dict, calls: int) -> dict:
    observed = result["observability"]
    actual = result["workflow_route"]["value"]
    return {
        "case_id": case_id,
        "passed": (
            actual == expected
            and result["workflow_route"]["authoritative"] is False
            and calls <= 1
            and observed["outcome"] in {"ok", "fallback"}
        ),
        "expected": expected,
        "actual": actual,
        "confidence": result["workflow_route"]["confidence"],
        "outcome": observed["outcome"],
        "fallback_used": observed["fallback_used"],
        "authoritative": result["workflow_route"]["authoritative"],
        "latency_ms": round(float(observed.get("latency_ms") or 0.0), 3),
        "cost": observed.get("cost"),
        "usage_input_tokens": observed.get("usage_input_tokens"),
        "usage_output_tokens": observed.get("usage_output_tokens"),
        "network_calls": calls,
        "provider_answer_accepted": observed["outcome"] == "ok" and not observed["fallback_used"],
    }


def run_routes(*, live: bool) -> list[dict]:
    records = []
    config = live_shadow.shadow_config({})
    for case_id, prompt, expected, active in ROUTE_CASES:
        provider = _live_provider() if live else CountingProvider()
        result = shadow_router.route(prompt, has_active_task=active, provider=provider, config=config)
        records.append(_safe_record(case_id, expected, result, provider.network_call_count))
    return records


def run_safety() -> list[dict]:
    records = []
    config = live_shadow.shadow_config({})
    for case_id, prompt, expected_lane in SAFETY_CASES:
        provider = CountingProvider()
        result = shadow_router.route(prompt, provider=provider, config=config)
        records.append(
            {
                "case_id": case_id,
                "passed": (
                    provider.network_call_count == 0
                    and result["risk_level"]["forced"] is True
                    and result["risk_level"]["lane"] == expected_lane
                    and result["workflow_route"]["authoritative"] is False
                ),
                "expected_lane": expected_lane,
                "actual_lane": result["risk_level"]["lane"],
                "provider_called": result["provider_called"],
                "network_calls": provider.network_call_count,
                "authoritative": result["workflow_route"]["authoritative"],
            }
        )
    return records


def run_stability(*, live: bool) -> list[dict]:
    records = []
    config = live_shadow.shadow_config({})
    for attempt in range(1, 4):
        provider = _live_provider() if live else CountingProvider()
        result = shadow_router.route(
            "Research reliable ways to reduce synthetic context duplication.",
            provider=provider,
            config=config,
        )
        record = _safe_record(f"stability-research-{attempt}", "research", result, provider.network_call_count)
        record["passed"] = record["passed"] and record["provider_answer_accepted"]
        records.append(record)
    return records


def run_failures() -> list[dict]:
    request = {
        "schema_version": 1,
        "decision_type": "routing.workflow_route",
        "options": ["question", "research"],
        "context": "summary: explain the synthetic result\ntags: question",
        "sensitivity": "low",
    }
    config = live_shadow.shadow_config({})
    scenarios = []
    for case_id, runner, expected_reason in (
        ("failure-timeout", lambda *_: (_ for _ in ()).throw(provider_base.ProviderTimeout(code="synthetic_timeout")), "synthetic_timeout"),
        ("failure-unavailable", lambda *_: (_ for _ in ()).throw(provider_base.ProviderUnavailable(code="synthetic_unavailable")), "synthetic_unavailable"),
        ("failure-malformed", lambda *_: {"schema_version": 1, "ok": True, "result": {}}, "answer_missing"),
    ):
        provider = provider_jev.JevProvider(
            config=config,
            env={"PATH": "/usr/bin", "TYPESAFE_API_KEY": "synthetic-not-sent"},
            runner=runner,
            node_executable="/usr/bin/true",
        )
        provider.dependencies_available = lambda: True
        started = time.monotonic()
        import engine

        result = engine.decide(request, config=config, provider=provider)
        scenarios.append(
            {
                "case_id": case_id,
                "passed": (
                    result["fallback_used"] is True
                    and result["authoritative"] is False
                    and result["reason"] == expected_reason
                    and provider.network_call_count == 1
                ),
                "outcome": result["outcome"],
                "reason": result["reason"],
                "authoritative": result["authoritative"],
                "network_calls": provider.network_call_count,
                "latency_ms": round((time.monotonic() - started) * 1000.0, 3),
            }
        )

    missing = provider_jev.JevProvider(config=config, env={"PATH": "/usr/bin"})
    import engine

    result = engine.decide(request, config=config, provider=missing)
    scenarios.append(
        {
            "case_id": "failure-missing-credential",
            "passed": result["fallback_used"] is True and result["authoritative"] is False and missing.network_call_count == 0,
            "outcome": result["outcome"],
            "reason": result["reason"],
            "authoritative": result["authoritative"],
            "network_calls": missing.network_call_count,
            "latency_ms": round(float(result["latency_ms"]), 3),
        }
    )
    return scenarios


def run_bridge_contract() -> list[dict]:
    codex = (HERE / "codex-lifecycle-hook.py").read_text(encoding="utf-8")
    claude = (HERE.parent.parent / ".claude" / "hooks" / "koda-context-injector.py").read_text(encoding="utf-8")
    records = []
    for case_id, source in (("bridge-codex", codex), ("bridge-claude", claude)):
        records.append(
            {
                "case_id": case_id,
                "passed": "observe_jev_shadow(" in source and "project=" in source,
                "shared_helper_wired": "observe_jev_shadow(" in source,
            }
        )

    provider = CountingProvider()
    with tempfile.TemporaryDirectory() as tmp:
        advice = live_shadow.observe_prompt(
            "Implement a synthetic reporting helper.",
            env={"PATH": "/usr/bin"},
            state_dir=Path(tmp),
            provider=provider,
        )
        persisted = next(Path(tmp).glob("*.json")).read_text(encoding="utf-8")
    records.append(
        {
            "case_id": "bridge-shared-output",
            "passed": (
                "Jev shadow advisory" in advice
                and "advisory only" in advice
                and "synthetic reporting" not in persisted
                and provider.network_call_count == 1
            ),
            "network_calls": provider.network_call_count,
            "metadata_only": "synthetic reporting" not in persisted,
        }
    )
    return records


def build_report(*, live: bool) -> dict:
    routes = run_routes(live=live)
    stability = run_stability(live=live)
    safety = run_safety()
    failures = run_failures()
    bridges = run_bridge_contract()
    all_records = routes + stability + safety + failures + bridges
    live_records = routes + stability
    live_latencies = [r["latency_ms"] for r in live_records if r.get("network_calls") == 1]
    return {
        "schema_version": 1,
        "mode": "live" if live else "offline-self-test",
        "advisory_only": True,
        "synthetic_data_only": True,
        "summary": {
            "passed": sum(bool(r["passed"]) for r in all_records),
            "total": len(all_records),
            "route_accuracy": round(sum(bool(r["passed"]) for r in routes) / len(routes), 4),
            "safety_zero_call_rate": round(sum(bool(r["passed"]) for r in safety) / len(safety), 4),
            "stability_rate": round(sum(bool(r["passed"]) for r in stability) / len(stability), 4),
            "live_network_calls": sum(int(r.get("network_calls", 0)) for r in live_records) if live else 0,
            "latency_ms_median": round(statistics.median(live_latencies), 3) if live_latencies else None,
            "latency_ms_max": round(max(live_latencies), 3) if live_latencies else None,
        },
        "routes": routes,
        "stability": stability,
        "safety": safety,
        "failures": failures,
        "bridges": bridges,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Use the configured live Jev provider for route cases")
    parser.add_argument("--output", type=Path, help="Write a sanitized JSON report")
    args = parser.parse_args()
    report = build_report(live=args.live)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(json.dumps(report["summary"], sort_keys=True))
    failed = [r["case_id"] for section in ("routes", "stability", "safety", "failures", "bridges") for r in report[section] if not r["passed"]]
    if failed:
        print("failed case IDs: " + ", ".join(failed), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
