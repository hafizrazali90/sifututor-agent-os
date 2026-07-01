#!/usr/bin/env python3
"""Check whether Koda returns the Agent OS memories future agents need."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class RetrievalCase:
    id: str
    query: str
    expected_any_ids: list[str] = field(default_factory=list)
    required_tags: list[str] = field(default_factory=list)
    required_text: list[str] = field(default_factory=list)


CASES = [
    RetrievalCase(
        id="KR-001",
        query="Agent OS Scenario Lab real-world experiment layer validation loop",
        expected_any_ids=["mem_2d3c7c46a6c5"],
        required_tags=["agent-os", "scenario-lab"],
        required_text=["18 scenarios", "172/172"],
    ),
    RetrievalCase(
        id="KR-002",
        query="Codex Koda CLI direct helper no MCP Sifututor",
        expected_any_ids=["mem_1677", "mem_0433a57f5bb9"],
        required_tags=["koda"],
        required_text=["CLI", "Koda"],
    ),
    RetrievalCase(
        id="KR-003",
        query="Claude and Codex predictable Agent OS workflow behavior parity",
        expected_any_ids=["mem_7e58a9bffb51"],
        required_tags=["sifututor"],
        required_text=["Claude", "Codex"],
    ),
    RetrievalCase(
        id="KR-004",
        query="Live Evidence Probe Report runner GitHub Planner production Koda",
        expected_any_ids=["mem_bec541e060b2", "mem_ff2c993deb90"],
        required_tags=["agent-os"],
        required_text=["Live Evidence"],
    ),
]


def run_search(query: str, limit: int) -> list[dict]:
    payload = {"query": query, "tags": ["sifututor", "agent-os"], "limit": limit}
    completed = subprocess.run(
        ["scripts/agent-checks/koda", "search", json.dumps(payload)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "Koda search failed")
    data = json.loads(completed.stdout)
    if not isinstance(data, list):
        raise RuntimeError("Koda search did not return a list")
    return data


def lower_text(memory: dict) -> str:
    values = [
        memory.get("id", ""),
        memory.get("content", ""),
        memory.get("why", ""),
        " ".join(memory.get("tags") or []),
    ]
    return " ".join(str(value).lower() for value in values)


def check_case(case: RetrievalCase, limit: int) -> tuple[bool, list[str], list[dict]]:
    memories = run_search(case.query, limit)
    errors: list[str] = []
    if not memories:
        return False, ["no memories returned"], memories

    ids = {str(memory.get("id")) for memory in memories}
    combined = "\n".join(lower_text(memory) for memory in memories)

    if case.expected_any_ids and not any(memory_id in ids for memory_id in case.expected_any_ids):
        errors.append("expected memory id not returned: " + " or ".join(case.expected_any_ids))

    for tag in case.required_tags:
        if tag.lower() not in combined:
            errors.append(f"missing tag/text marker: {tag}")

    for text in case.required_text:
        if text.lower() not in combined:
            errors.append(f"missing expected content marker: {text}")

    return not errors, errors, memories


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=5, help="Koda result limit per case")
    parser.add_argument("--json", action="store_true", help="print machine-readable results")
    args = parser.parse_args()

    results = []
    failures: list[str] = []
    for case in CASES:
        try:
            ok, errors, memories = check_case(case, args.limit)
        except Exception as exc:  # noqa: BLE001 - report probe failure plainly
            ok, errors, memories = False, [str(exc)], []
        if not ok:
            failures.append(case.id)
        results.append(
            {
                "id": case.id,
                "query": case.query,
                "passed": ok,
                "errors": errors,
                "returned_ids": [memory.get("id") for memory in memories],
            }
        )

    if args.json:
        print(json.dumps({"cases": results, "failures": failures}, indent=2))
    else:
        for result in results:
            status = "PASS" if result["passed"] else "FAIL"
            print(f"{status} {result['id']} query={result['query']!r}")
            print("  returned: " + ", ".join(str(item) for item in result["returned_ids"]))
            for error in result["errors"]:
                print(f"  - {error}")
        passed = len(CASES) - len(failures)
        print(f"agent-os-koda-retrieval-quality: {passed}/{len(CASES)} passed")

    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
