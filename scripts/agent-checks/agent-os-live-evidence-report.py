#!/usr/bin/env python3
"""Generate a safe Agent OS live-evidence probe report."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
KODA_QUERY = {
    "query": "Agent OS live evidence probe",
    "tags": ["sifututor", "agent-os"],
    "limit": 1,
}


def run_command(command: list[str], timeout: int = 45) -> tuple[int, str, str]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr


def run_json_probe(name: str, command: list[str]) -> dict:
    code, stdout, stderr = run_command(command)
    if code != 0:
        return {
            "name": name,
            "state": "not_connected",
            "evidence": f"{name} probe command failed",
            "note": stderr.strip().splitlines()[:2],
        }
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {
            "name": name,
            "state": "unknown",
            "evidence": f"{name} probe returned non-json output",
            "note": "Probe output was not included to avoid noisy or sensitive details.",
        }


def run_koda_probe() -> dict:
    command = ["scripts/agent-checks/koda", "search", json.dumps(KODA_QUERY)]
    code, stdout, stderr = run_command(command)
    if code != 0:
        return {
            "name": "koda",
            "state": "not_connected",
            "method": "direct-cli-helper",
            "evidence": "Koda memory_search command failed",
            "note": stderr.strip().splitlines()[:2],
        }
    try:
        memories = json.loads(stdout)
    except json.JSONDecodeError:
        return {
            "name": "koda",
            "state": "unknown",
            "method": "direct-cli-helper",
            "evidence": "Koda memory_search returned non-json output",
            "note": "Raw memory output omitted.",
        }
    return {
        "name": "koda",
        "state": "available",
        "method": "direct-cli-helper",
        "evidence": "Koda memory_search read passed",
        "returned_memory_count": len(memories) if isinstance(memories, list) else None,
        "write_actions": "blocked_until_relevant_durable_memory",
        "note": "This report uses read-only memory search; it does not store or update Koda.",
    }


def build_report() -> dict:
    probes = [
        run_json_probe("github", ["python3", "scripts/agent-checks/agent-os-github-probe.py", "--json"]),
        run_json_probe("planner", ["python3", "scripts/agent-checks/agent-os-planner-probe.py", "--json"]),
        run_json_probe(
            "production_logs",
            ["python3", "scripts/agent-checks/agent-os-production-logs-probe.py", "--json"],
        ),
        run_koda_probe(),
    ]
    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "repo_root": str(ROOT),
        "probes": probes,
    }


def source_label(name: str) -> str:
    return {
        "github": "GitHub",
        "planner": "Planner",
        "production_logs": "Production monitoring",
        "koda": "Koda",
    }.get(name, name)


def proves_text(result: dict) -> str:
    name = result.get("name")
    state = result.get("state")
    if state != "available":
        return result.get("evidence", "current access is not proven")
    if name == "github":
        repo = (result.get("repo") or {}).get("nameWithOwner") or "repo metadata"
        return f"read-only GitHub metadata works for `{repo}`"
    if name == "planner":
        return "staff intake board metadata can be read without card content"
    if name == "production_logs":
        return "read-only Sentry and BetterStack checks can run"
    if name == "koda":
        count = result.get("returned_memory_count")
        return f"Koda memory search works; returned {count} item(s)"
    return result.get("evidence", "read-only probe works")


def not_approved_text(name: str) -> str:
    return {
        "github": "push, PR edit, merge, release, deploy",
        "planner": "Planner status, assignment, priority, content changes",
        "production_logs": "deploy, rollback, alert resolution, monitor changes",
        "koda": "treating old memory as current truth, unrelated writes",
    }.get(name, "writes or approval-gated actions")


def render_markdown(report: dict) -> str:
    lines = [
        "# Live Evidence Probe Report",
        "",
        f"- **Generated at:** {report['generated_at']}",
        f"- **Repository:** `{report['repo_root']}`",
        "",
        "## Summary",
        "",
        "| Source | Current state | What this proves | What it does not approve |",
        "| --- | --- | --- | --- |",
    ]
    for result in report["probes"]:
        name = result.get("name", "unknown")
        state = result.get("state", "unknown")
        lines.append(
            f"| {source_label(name)} | `{state}` | {proves_text(result)} | {not_approved_text(name)} |"
        )
    lines.extend(
        [
            "",
            "## Evidence Details",
            "",
        ]
    )
    for result in report["probes"]:
        name = result.get("name", "unknown")
        lines.extend(
            [
                f"### {source_label(name)}",
                "",
                f"- **State:** `{result.get('state', 'unknown')}`",
                f"- **Method:** `{result.get('method', 'unknown')}`",
                f"- **Evidence:** {result.get('evidence', 'not reported')}",
            ]
        )
        note = result.get("note")
        if note:
            if isinstance(note, list):
                note = " ".join(str(item) for item in note)
            lines.append(f"- **Note:** {note}")
        if result.get("write_actions"):
            lines.append(f"- **Write actions:** `{result['write_actions']}`")
        lines.append("")
    lines.extend(
        [
            "## Practical Meaning",
            "",
            "Use available sources as current read-only evidence for the active task.",
            "If a source is `unknown` or `not_connected`, say what evidence is missing instead of guessing.",
            "",
            "## Boundaries",
            "",
            "- Read-only probe success is not approval for writes.",
            "- Do not print secrets, tokens, raw logs, Planner card content, private payloads, or unrelated service data.",
            "- Rerun the relevant probe when current evidence matters.",
            "- Stop before push, PR edit, merge, deploy, production mutation, destructive work, or critical-lane implementation unless Hafiz explicitly approves that boundary.",
            "",
            "## Recommended Next",
            "",
            "Continue only inside the approved task boundary. Ask Hafiz before crossing any write, release, production, or destructive gate.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print machine-readable report data")
    parser.add_argument("-o", "--output", help="write the Markdown report to this path")
    parser.add_argument("--allow-partial", action="store_true", help="return success even when a probe is unavailable")
    args = parser.parse_args()

    report = build_report()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        markdown = render_markdown(report)
        if args.output:
            output = Path(args.output).expanduser()
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(markdown)
            print(f"agent-os-live-evidence-report: wrote {output}")
        else:
            print(markdown, end="")

    all_available = all(result.get("state") == "available" for result in report["probes"])
    return 0 if all_available or args.allow_partial else 1


if __name__ == "__main__":
    raise SystemExit(main())
