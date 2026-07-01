#!/usr/bin/env python3
"""Check Agent OS behavior traces for Claude/Codex parity review points."""

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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print machine-readable results")
    parser.add_argument("--live-claude", action="store_true", help="also ask Claude CLI for live traces")
    parser.add_argument("--model", help="optional Claude model alias/name for --live-claude")
    args = parser.parse_args()

    results = []
    failures: list[str] = []
    for case in CASES:
        trace = codex_trace(case)
        errors = trace_errors(case, trace)
        claude = live_claude_trace(case, args.model) if args.live_claude else None
        if errors:
            failures.append(case.id)
        results.append(
            {
                "id": case.id,
                "prompt": case.prompt,
                "passed": not errors,
                "errors": errors,
                "codex": trace,
                "claude": claude,
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
            for error in result["errors"]:
                print(f"  - {error}")
        passed = len(CASES) - len(failures)
        print(f"agent-os-behavior-trace-runner: {passed}/{len(CASES)} passed")

    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
