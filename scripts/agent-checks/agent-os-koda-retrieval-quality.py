#!/usr/bin/env python3
"""Check whether Koda returns the Agent OS memories future agents need.

A compound multi-topic query can return zero while a narrower query with the
same filters finds the record. This runner therefore separates "the client
asked badly" from "retrieval could not return a record that exists", without
relaxing filters and without turning a diagnosed failure into a pass.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from dataclasses import dataclass, field
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
BASE_TAGS = ("sifututor", "agent-os")

ATTRIBUTION_MEANING = {
    "retrieved": "The compound query returned the expected record.",
    "upstream_compound_query_gap": (
        "The compound query returned nothing usable, but a narrower query with the same "
        "filters returned the expected record. The record exists; compound retrieval is "
        "the weak link, which is upstream Koda behavior rather than a client defect."
    ),
    "not_retrievable": (
        "Neither the compound nor the narrowed same-filter probes returned the expected "
        "record. This is not proof of absence; treat it as unretrievable by these probes "
        "and check by exact ID before concluding anything."
    ),
    "client_filter_relaxation": (
        "A probe changed the project/tag filters. That is a client defect: relaxing "
        "filters to obtain results invalidates the comparison."
    ),
}


@dataclass(frozen=True)
class RetrievalCase:
    id: str
    query: str
    expected_any_ids: list[str] = field(default_factory=list)
    required_tags: list[str] = field(default_factory=list)
    required_text: list[str] = field(default_factory=list)
    narrow_queries: list[str] = field(default_factory=list)


CASES = [
    RetrievalCase(
        id="KR-001",
        query="Agent OS Scenario Lab real-world experiment layer validation loop",
        expected_any_ids=["mem_2d3c7c46a6c5"],
        required_tags=["agent-os", "scenario-lab"],
        required_text=["18 scenarios", "172/172"],
        narrow_queries=["Agent OS Scenario Lab", "validation loop"],
    ),
    RetrievalCase(
        id="KR-002",
        query="Codex Koda CLI direct helper no MCP Sifututor",
        expected_any_ids=["mem_1677", "mem_0433a57f5bb9"],
        required_tags=["koda"],
        required_text=["CLI", "Koda"],
        narrow_queries=["Codex Koda CLI", "direct Koda helper"],
    ),
    RetrievalCase(
        id="KR-003",
        query="Claude and Codex predictable Agent OS workflow behavior parity",
        expected_any_ids=["mem_7e58a9bffb51"],
        required_tags=["sifututor"],
        required_text=["Claude", "Codex"],
        narrow_queries=["Claude Codex parity", "Agent OS workflow behavior"],
    ),
    RetrievalCase(
        id="KR-004",
        query="Live Evidence Probe Report runner GitHub Planner production Koda",
        expected_any_ids=["mem_bec541e060b2", "mem_ff2c993deb90"],
        required_tags=["agent-os"],
        required_text=["Live Evidence"],
        narrow_queries=["Live Evidence Probe Report", "probe report runner"],
    ),
]


def search_payload(query: str, limit: int, *, tags: tuple[str, ...] = BASE_TAGS) -> dict:
    """Build one probe. Every probe for a case must carry identical filters."""

    return {"query": query, "tags": list(tags), "limit": limit}


def filters_of(payload: dict) -> tuple:
    return (tuple(sorted(payload.get("tags") or [])), payload.get("project"), payload.get("scope"))


def narrowed_queries(case: RetrievalCase) -> list[str]:
    """Narrower individual topics for the same case, authored or derived."""

    if case.narrow_queries:
        return list(case.narrow_queries)
    words = [word for word in case.query.split() if len(word) > 3]
    return [" ".join(words[index:index + 3]) for index in range(0, max(len(words) - 2, 1), 3)][:3]


def found_expected(case: RetrievalCase, memories: list[dict]) -> bool:
    if not case.expected_any_ids:
        return bool(memories)
    ids = {str(memory.get("id")) for memory in memories if isinstance(memory, dict)}
    return any(memory_id in ids for memory_id in case.expected_any_ids)


def diagnose(
    case: RetrievalCase,
    limit: int,
    search: Callable[[dict], list[dict]],
    *,
    payload_builder: Callable[..., dict] = search_payload,
) -> dict:
    """Read-only attribution of a compound-query miss. Never repairs, never relaxes filters."""

    canonical = search_payload(case.query, limit)
    base = payload_builder(case.query, limit)
    probes = [{"query": case.query, "kind": "compound"}]
    compound = search(base)
    probes[0]["returned_ids"] = [memory.get("id") for memory in compound if isinstance(memory, dict)]
    probes[0]["found"] = found_expected(case, compound)

    report = {
        "case": case.id,
        "compound_found": probes[0]["found"],
        "narrow_found": False,
        "filters_unchanged": True,
        "probes": probes,
    }
    if report["compound_found"]:
        report["attribution"] = "retrieved"
        report["meaning"] = ATTRIBUTION_MEANING["retrieved"]
        return report

    narrow_payloads = [payload_builder(query, limit) for query in narrowed_queries(case)]
    if any(filters_of(payload) != filters_of(canonical) for payload in [base] + narrow_payloads):
        report["filters_unchanged"] = False
        report["attribution"] = "client_filter_relaxation"
        report["meaning"] = ATTRIBUTION_MEANING["client_filter_relaxation"]
        return report

    for payload in narrow_payloads:
        query = payload["query"]
        memories = search(payload)
        probe = {
            "query": query,
            "kind": "narrow",
            "returned_ids": [memory.get("id") for memory in memories if isinstance(memory, dict)],
            "found": found_expected(case, memories),
        }
        probes.append(probe)
        report["narrow_found"] = report["narrow_found"] or probe["found"]

    report["attribution"] = "upstream_compound_query_gap" if report["narrow_found"] else "not_retrievable"
    report["meaning"] = ATTRIBUTION_MEANING[report["attribution"]]
    return report


def live_search(payload: dict) -> list[dict]:
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


def run_search(query: str, limit: int) -> list[dict]:
    """Retained entry point for the single compound query."""

    return live_search(search_payload(query, limit))


def lower_text(memory: dict) -> str:
    values = [
        memory.get("id", ""),
        memory.get("content", ""),
        memory.get("why", ""),
        " ".join(memory.get("tags") or []),
    ]
    return " ".join(str(value).lower() for value in values)


def check_case(
    case: RetrievalCase,
    limit: int,
    *,
    search: Callable[[dict], list[dict]] = live_search,
) -> tuple[bool, list[str], list[dict], dict]:
    report = diagnose(case, limit, search)
    memories = search(search_payload(case.query, limit)) if report["compound_found"] else []
    errors: list[str] = []

    if not report["compound_found"]:
        # Diagnosis explains the miss; it never converts the miss into a pass.
        errors.append(f"compound query miss attributed to {report['attribution']}")
        if case.expected_any_ids:
            errors.append("expected memory id not returned: " + " or ".join(case.expected_any_ids))
        else:
            errors.append("no memories returned")
        return False, errors, memories, report

    combined = "\n".join(lower_text(memory) for memory in memories if isinstance(memory, dict))

    for tag in case.required_tags:
        if tag.lower() not in combined:
            errors.append(f"missing tag/text marker: {tag}")

    for text in case.required_text:
        if text.lower() not in combined:
            errors.append(f"missing expected content marker: {text}")

    return not errors, errors, memories, report


SELF_TEST_CASE = RetrievalCase(
    id="KRF-000",
    query="Agent OS Koda compound retrieval self test fixture",
    expected_any_ids=["mem_000000000000"],
    narrow_queries=["Koda compound retrieval", "retrieval self test"],
)

SELF_TEST_FIXTURES = [
    ("KRF-001", {"Koda compound retrieval": [{"id": "mem_000000000000"}]},
     "upstream_compound_query_gap", "compound zero, narrower same-filter probe finds it"),
    ("KRF-002", {}, "not_retrievable", "zero everywhere is not proof of absence"),
    ("KRF-003", {SELF_TEST_CASE.query: [{"id": "mem_000000000000"}]},
     "retrieved", "compound query already returns the expected record"),
]


def self_test() -> int:
    """Deterministic offline proof of the compound-query diagnosis. No Koda calls."""

    failures = []
    for case_id, corpus, expected, why in SELF_TEST_FIXTURES:
        report = diagnose(SELF_TEST_CASE, 5, lambda payload: corpus.get(payload["query"], []))
        ok = report["attribution"] == expected and report["filters_unchanged"]
        print(f"{'PASS' if ok else 'FAIL'} {case_id} {why}")
        if not ok:
            print(f"  expected {expected}, observed {report['attribution']}")
            failures.append(case_id)

    def relaxing(query, limit, **_):
        return {"query": query, "limit": limit, "tags": []}

    relaxed = diagnose(SELF_TEST_CASE, 5, lambda payload: [], payload_builder=relaxing)
    ok = relaxed["attribution"] == "client_filter_relaxation" and not relaxed["filters_unchanged"]
    print(f"{'PASS' if ok else 'FAIL'} KRF-004 relaxing filters to get results is a client defect")
    if not ok:
        failures.append("KRF-004")

    total = len(SELF_TEST_FIXTURES) + 1
    print(f"agent-os-koda-retrieval-quality self-test: {total - len(failures)}/{total} passed")
    if failures:
        print("failed: " + ", ".join(failures))
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=5, help="Koda result limit per case")
    parser.add_argument("--json", action="store_true", help="print machine-readable results")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the offline compound-query diagnosis fixtures without calling Koda",
    )
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    results = []
    failures: list[str] = []
    for case in CASES:
        try:
            ok, errors, memories, report = check_case(case, args.limit)
        except Exception as exc:  # noqa: BLE001 - report probe failure plainly
            ok, errors, memories, report = False, [str(exc)], [], {"attribution": "probe_failed"}
        if not ok:
            failures.append(case.id)
        results.append(
            {
                "id": case.id,
                "query": case.query,
                "passed": ok,
                "errors": errors,
                "returned_ids": [memory.get("id") for memory in memories],
                "attribution": report.get("attribution"),
                "probes": report.get("probes", []),
            }
        )

    if args.json:
        print(json.dumps({"cases": results, "failures": failures}, indent=2))
    else:
        for result in results:
            status = "PASS" if result["passed"] else "FAIL"
            print(f"{status} {result['id']} query={result['query']!r}")
            print("  returned: " + ", ".join(str(item) for item in result["returned_ids"]))
            if not result["passed"]:
                print(f"  attribution: {result['attribution']}")
                for probe in result["probes"]:
                    if probe.get("kind") == "narrow":
                        print(f"  narrow probe {probe['query']!r} found={probe['found']}")
            for error in result["errors"]:
                print(f"  - {error}")
        passed = len(CASES) - len(failures)
        print(f"agent-os-koda-retrieval-quality: {passed}/{len(CASES)} passed")

    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
