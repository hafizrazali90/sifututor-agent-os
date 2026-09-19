#!/usr/bin/env python3
"""Check Agent OS behavior traces for Claude/Codex/Kilo parity review points."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import types


ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / "scripts" / "agent-checks" / "codex-lifecycle-hook.py"


@dataclass(frozen=True)
class BehaviorCase:
    id: str
    prompt: str
    expected_route: str
    expected_first_move: str
    required_action_text: list[str] = field(default_factory=list)


CASES = [
    BehaviorCase(
        id="BT-001",
        prompt="A staff member says the SIMS modal does not open.",
        expected_route="$diagnose",
        expected_first_move="diagnose",
        required_action_text=["reported symptom", "reproduce or inspect", "GitHub/task workflow"],
    ),
    BehaviorCase(
        id="BT-002",
        prompt="Fix the payment callback bug.",
        expected_route="$diagnose",
        expected_first_move="diagnose",
        required_action_text=["critical lane", "read-only", "wait for approval"],
    ),
    BehaviorCase(
        id="BT-003",
        prompt="Generate a live evidence probe report for the Agent OS.",
        expected_route="$quick-check",
        expected_first_move="quick-check",
        required_action_text=["agent-os-live-evidence-report.py", "read-only evidence"],
    ),
    BehaviorCase(
        id="BT-004",
        prompt="Compare Claude and Codex for this workflow and tell me if they behave differently.",
        expected_route="$workflow-improvement",
        expected_first_move="workflow-improvement",
        required_action_text=["parity runner", "approval boundary", "different wording is fine"],
    ),
]


def load_classifier():
    source = HOOK.read_text()
    entrypoint = "\nraise SystemExit(main())"
    if entrypoint not in source:
        raise RuntimeError(f"cannot find hook entrypoint in {HOOK}")
    module = types.ModuleType("codex_lifecycle_hook_for_behavior_trace")
    exec(source.split(entrypoint, 1)[0], module.__dict__)
    return module.classify_prompt


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def codex_trace(case: BehaviorCase) -> dict:
    classify_prompt = load_classifier()
    route, actions, reason = classify_prompt(case.prompt)
    return {
        "adapter": "codex",
        "route": route,
        "first_move": route.removeprefix("$") if route else "discuss",
        "reason": reason,
        "actions": actions,
    }


def trace_errors(case: BehaviorCase, trace: dict) -> list[str]:
    errors: list[str] = []
    if trace["route"] != case.expected_route:
        errors.append(f"route expected {case.expected_route}, observed {trace['route']}")
    if trace["first_move"] != case.expected_first_move:
        errors.append(
            f"first_move expected {case.expected_first_move}, observed {trace['first_move']}"
        )
    action_text = normalize("\n".join(trace.get("actions") or []))
    for snippet in case.required_action_text:
        if normalize(snippet) not in action_text:
            errors.append(f"missing action marker: {snippet}")
    return errors


def summarize_claude_error(raw_stdout: str, raw_stderr: str) -> list[str]:
    raw = (raw_stderr or raw_stdout).strip()
    if not raw:
        return ["Claude CLI failed without output"]
    first_line = raw.splitlines()[0]
    try:
        payload = json.loads(first_line)
    except json.JSONDecodeError:
        return [first_line[:240]]

    summary: list[str] = []
    subtype = payload.get("subtype")
    if subtype:
        summary.append(f"subtype={subtype}")
    api_status = payload.get("api_error_status")
    if api_status:
        summary.append(f"api_status={api_status}")
    if payload.get("errors"):
        summary.extend(str(item)[:160] for item in payload["errors"][:2])
    elif payload.get("result"):
        result = str(payload["result"])
        if "rate limit" in result.lower():
            summary.append("rate limit reached")
        elif "maximum budget" in result.lower():
            summary.append("maximum budget reached")
        else:
            summary.append(result[:160])
    if not summary:
        summary.append("Claude CLI returned an error payload")
    return summary


def live_claude_trace(case: BehaviorCase, model: str | None = None) -> dict:
    if not shutil.which("claude"):
        return {"adapter": "claude", "state": "not_connected", "error": "claude command not found"}

    schema = {
        "type": "object",
        "properties": {
            "route": {"type": "string"},
            "first_move": {"type": "string"},
            "approval_boundary": {"type": "string"},
            "evidence_standard": {"type": "string"},
            "state_language": {"type": "string"},
            "close_out": {"type": "string"},
        },
        "required": [
            "route",
            "first_move",
            "approval_boundary",
            "evidence_standard",
            "state_language",
            "close_out",
        ],
        "additionalProperties": False,
    }
    prompt = (
        "Classify this Sifututor Agent OS prompt using the shared workflow behavior, "
        "not exact wording. Return only JSON matching the schema. Prompt: "
        + json.dumps(case.prompt)
    )
    command = [
        "claude",
        "--print",
        "--output-format",
        "json",
        "--json-schema",
        json.dumps(schema),
        "--tools",
        "",
        "--no-session-persistence",
        "--max-budget-usd",
        "0.10",
    ]
    if model:
        command.extend(["--model", model])
    command.append(prompt)
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=90,
        check=False,
    )
    if completed.returncode != 0:
        return {
            "adapter": "claude",
            "state": "failed",
            "error": summarize_claude_error(completed.stdout, completed.stderr),
        }
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"adapter": "claude", "state": "unknown", "error": "non-json output"}
    result = payload.get("result") if isinstance(payload, dict) else payload
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            result = {"raw": result}
    return {"adapter": "claude", "state": "available", "trace": result}


def find_kilo_cli() -> Path | None:
    executable = shutil.which("kilo")
    if executable:
        return Path(executable)
    candidates = sorted(
        (Path.home() / ".vscode" / "extensions").glob("kilocode.kilo-code-*/bin/kilo"),
        reverse=True,
    )
    return candidates[0] if candidates else None


def parse_json_object(value: str) -> dict | None:
    text = value.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    try:
        payload = json.loads(text)
        return payload if isinstance(payload, dict) else None
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            return None
        try:
            payload = json.loads(text[start : end + 1])
            return payload if isinstance(payload, dict) else None
        except json.JSONDecodeError:
            return None


def parse_kilo_event_stream(raw_stdout: str) -> dict | None:
    text_parts: list[str] = []
    for line in raw_stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "text":
            continue
        part = event.get("part") or {}
        text = part.get("text")
        if isinstance(text, str):
            text_parts.append(text)
    return parse_json_object("".join(text_parts))


def normalize_loose(value: str) -> str:
    """Word-token normalize for live Kilo trace matching against JSON-dumped text."""
    return re.sub(r"[^a-z0-9$]+", " ", value.lower()).strip()


def matches_live_marker(snippet: str, trace_text: str) -> bool:
    concept_alternatives = {
        "reported symptom": (("reported", "symptom"), ("unconfirmed", "symptom")),
        "reproduce or inspect": (("reproduce", "inspect"), ("reproduce", "refute")),
        "auto create the github issue": (
            ("auto", "create", "github", "issue", "confirmed"),
            ("auto", "create", "github", "issue", "confirms"),
            ("automatically", "create", "github", "issue", "confirmed"),
            ("automatically", "create", "github", "issue", "confirms"),
        ),
        "github task workflow": (
            ("github", "issue", "confirmed"),
            ("github", "issue", "diagnosis"),
            ("github", "issue", "traceability"),
            ("github", "task", "workflow"),
        ),
        "wait for approval": (
            ("wait", "approval"),
            ("halt", "approval"),
            ("human", "review"),
        ),
        "read only evidence": (("read", "only", "evidence"),),
        "different wording is fine": (
            ("wording", "fine"),
            ("wording", "acceptable"),
            ("wording", "not", "drift"),
        ),
    }
    normalized_snippet = normalize_loose(snippet)
    trace_text = normalize_loose(trace_text)
    alternatives = concept_alternatives.get(normalized_snippet)
    if alternatives is None:
        return normalized_snippet in trace_text
    trace_tokens = set(trace_text.split())
    return any(
        all(token in trace_tokens for token in alternative) for alternative in alternatives
    )


def matches_live_first_move(case: BehaviorCase, first_move: str) -> bool:
    normalized = normalize_loose(first_move).removeprefix("$")
    if normalize_loose(case.expected_first_move) in normalized:
        return True
    tokens = set(normalized.split())
    semantic_alternatives = {
        "diagnose": (
            ("read", "only", "evidence"),
            ("reproduce", "evidence"),
            ("inspect", "evidence"),
            ("reported", "symptom"),
            ("unverified", "symptom"),
        ),
        "quick-check": (
            ("live", "evidence", "report"),
            ("evidence", "probe"),
        ),
        "workflow-improvement": (
            ("parity", "runner"),
            ("compare", "claude", "codex"),
            ("improvement", "loop"),
        ),
    }
    return any(
        all(token in tokens for token in alternative)
        for alternative in semantic_alternatives.get(case.expected_first_move, ())
    )


def live_trace_errors(case: BehaviorCase, trace: dict) -> list[str]:
    required_fields = (
        "route",
        "first_move",
        "approval_boundary",
        "evidence_standard",
        "state_language",
        "memory_and_task_routing",
        "close_out",
    )
    errors = [
        f"missing live trace field: {field}"
        for field in required_fields
        if not str(trace.get(field, "")).strip()
    ]
    route = str(trace.get("route", "")).strip()
    normalized_route = route if route.startswith("$") else f"${route}"
    first_move = str(trace.get("first_move", ""))
    if normalized_route != case.expected_route:
        errors.append(f"route expected {case.expected_route}, observed {route or '<missing>'}")
    if not matches_live_first_move(case, first_move):
        errors.append(
            f"first_move expected {case.expected_first_move}, observed "
            f"{normalize_loose(first_move) or '<missing>'}"
        )
    trace_text = normalize_loose(json.dumps(trace, sort_keys=True))
    for snippet in case.required_action_text:
        if not matches_live_marker(snippet, trace_text):
            errors.append(f"missing live behavior marker: {snippet}")
    return errors


def live_kilo_trace(case: BehaviorCase) -> dict:
    kilo_cli = find_kilo_cli()
    if kilo_cli is None:
        return {"adapter": "kilo", "state": "not_connected", "error": "Kilo CLI not found"}

    prompt = (
        "This is a read-only Sifututor Agent OS compliance test. Do not use tools, "
        "run commands, create issues, or change state. Classify the supplied prompt "
        "using the shared Agent OS. Return only one JSON object with string fields "
        "route, first_move, approval_boundary, evidence_standard, state_language, "
        "memory_and_task_routing, and close_out. Use an exact shared route name such "
        "as diagnose, quick-check, or workflow-improvement; do not call an unconfirmed "
        "staff report a bugfix. Prompt: " + json.dumps(case.prompt)
    )
    completed = subprocess.run(
        [
            str(kilo_cli),
            "run",
            "--agent",
            "sifututor-agent-os",
            "--format",
            "json",
            "--title",
            f"Agent OS live parity {case.id}",
            prompt,
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=120,
        check=False,
    )
    if completed.returncode != 0:
        error = (completed.stderr or completed.stdout or "Kilo CLI failed").strip().splitlines()
        return {
            "adapter": "kilo",
            "state": "failed",
            "error": error[-1][:300] if error else "Kilo CLI failed",
        }
    trace = parse_kilo_event_stream(completed.stdout)
    if trace is None:
        return {
            "adapter": "kilo",
            "state": "unknown",
            "error": "Kilo CLI returned no parseable JSON trace",
        }
    return {"adapter": "kilo", "state": "available", "trace": trace}


def run_kilo_self_test() -> int:
    good_trace = {
        "route": "diagnose",
        "first_move": "diagnose",
        "approval_boundary": "Wait for approval before implementation.",
        "evidence_standard": "Treat this as a reported symptom; reproduce or inspect current evidence.",
        "state_language": "Nothing changed.",
        "memory_and_task_routing": (
            "After diagnosis confirms coding work, auto-create the GitHub issue as part "
            "of the normal GitHub/task workflow; that step does not need separate approval."
        ),
        "close_out": "Recommend the next read-only action.",
    }
    event = json.dumps({"type": "text", "part": {"text": json.dumps(good_trace)}})
    parsed = parse_kilo_event_stream(event)
    outcomes = [
        ("valid Kilo event stream parses", parsed == good_trace),
        ("valid Kilo diagnose trace passes", not live_trace_errors(CASES[0], good_trace)),
    ]
    drifted = dict(good_trace, route="bugfix", first_move="fix")
    outcomes.append(
        (
            "staff-report bugfix drift is rejected",
            bool(live_trace_errors(CASES[0], drifted)),
        )
    )
    missing_field = dict(good_trace)
    missing_field.pop("close_out")
    outcomes.append(
        (
            "missing structured field is rejected",
            "missing live trace field: close_out" in live_trace_errors(CASES[0], missing_field),
        )
    )
    outcomes.append(
        ("non-JSON Kilo output is rejected", parse_kilo_event_stream("not json") is None)
    )
    outcomes.append(
        (
            "equivalent live wording is accepted",
            matches_live_marker("reproduce or inspect", "reproduce or refute the symptom")
            and matches_live_marker("read-only evidence", "read-only live evidence")
            and matches_live_marker(
                "different wording is fine", "wording-only variation (acceptable)"
            ),
        )
    )
    outcomes.append(
        (
            "descriptive first moves are accepted",
            matches_live_first_move(
                CASES[0],
                "Treat this as an unverified symptom and gather read-only evidence first.",
            )
            and matches_live_first_move(
                CASES[3],
                "Read the parity contract, then run the shared parity runner.",
            ),
        )
    )
    outcomes.append(
        (
            "unrelated first move is rejected",
            not matches_live_first_move(CASES[0], "Start implementing the fix now."),
        )
    )
    outcomes.append(
        (
            "vague parity claim is rejected",
            not matches_live_marker("different wording is fine", "all agents are identical"),
        )
    )
    issue_approval_drift = dict(good_trace)
    issue_approval_drift["memory_and_task_routing"] = "Ask before creating a GitHub issue."
    outcomes.append(
        (
            "issue-creation approval drift is rejected",
            bool(live_trace_errors(CASES[0], issue_approval_drift)),
        )
    )
    for label, passed in outcomes:
        print(f"{'PASS' if passed else 'FAIL'} {label}")
    passed = sum(1 for _, ok in outcomes if ok)
    print(f"Kilo behavior trace self-test: {passed}/{len(outcomes)} passed")
    return 0 if passed == len(outcomes) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print machine-readable results")
    parser.add_argument("--live-claude", action="store_true", help="also ask Claude CLI for live traces")
    parser.add_argument("--live-kilo", action="store_true", help="also ask Kilo/GLM for live traces")
    parser.add_argument(
        "--require-live-kilo",
        action="store_true",
        help="fail when a live Kilo trace is unavailable or behaviorally different",
    )
    parser.add_argument(
        "--self-test-kilo",
        action="store_true",
        help="run deterministic Kilo event-parser and drift-detection fixtures",
    )
    parser.add_argument("--model", help="optional Claude model alias/name for --live-claude")
    args = parser.parse_args()

    if args.self_test_kilo:
        return run_kilo_self_test()

    results = []
    failures: list[str] = []
    for case in CASES:
        trace = codex_trace(case)
        errors = trace_errors(case, trace)
        claude = live_claude_trace(case, args.model) if args.live_claude else None
        kilo = live_kilo_trace(case) if (args.live_kilo or args.require_live_kilo) else None
        kilo_errors: list[str] = []
        if kilo is not None:
            if kilo.get("state") == "available":
                kilo_errors = live_trace_errors(case, kilo.get("trace") or {})
            else:
                kilo_errors = [str(kilo.get("error") or "live Kilo trace unavailable")]
        if errors:
            failures.append(case.id)
        if args.require_live_kilo and kilo_errors:
            failures.append(f"{case.id}:kilo")
        results.append(
            {
                "id": case.id,
                "prompt": case.prompt,
                "passed": not errors,
                "errors": errors,
                "codex": trace,
                "claude": claude,
                "kilo": kilo,
                "kilo_errors": kilo_errors,
            }
        )

    if args.json:
        print(json.dumps({"cases": results, "failures": failures}, indent=2))
    else:
        for result in results:
            status = "PASS" if result["passed"] else "FAIL"
            print(f"{status} {result['id']} prompt={result['prompt']!r}")
            print(f"  codex route={result['codex']['route']} first={result['codex']['first_move']}")
            if result.get("claude"):
                claude = result["claude"]
                print(f"  claude state={claude.get('state')}")
                if claude.get("trace"):
                    print(f"  claude trace={json.dumps(claude['trace'], sort_keys=True)}")
                if claude.get("error"):
                    print(f"  claude error={claude['error']}")
            if result.get("kilo"):
                kilo = result["kilo"]
                print(f"  kilo state={kilo.get('state')}")
                if kilo.get("trace"):
                    print(f"  kilo trace={json.dumps(kilo['trace'], sort_keys=True)}")
                if kilo.get("error"):
                    print(f"  kilo error={kilo['error']}")
                for error in result["kilo_errors"]:
                    print(f"  - Kilo: {error}")
            for error in result["errors"]:
                print(f"  - {error}")
        passed = len(CASES) - len(failures)
        print(f"agent-os-behavior-trace-runner: {passed}/{len(CASES)} passed")

    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
