#!/usr/bin/env python3
"""Check Agent OS Koda memory quality and fallback expectations."""

from __future__ import annotations

import argparse
import re
from collections.abc import Callable


ALLOWED_CATEGORIES = {"decision", "lesson", "rule", "preference", "fact"}
ALLOWED_SOURCES = {"user-stated", "auto-captured", "correction"}
PROJECT_TAGS = {
    "sifututor",
    "sifu-tutor",
    "ripple-suite",
    "sifututor_tutor",
    "sifututor_parent",
    "lls",
    "lls-frontend",
    "lls-mobile",
    "creative-hub",
    "team-inbox",
    "finch-inbox",
}
SECRET_PATTERNS = (
    r"\bapi[_-]?key\b",
    r"\btoken\s*=",
    r"\bbearer\s+[a-z0-9._~-]+",
    r"\bpassword\s*=",
    r"\bsecret\s*=",
    r"\.env(?:\b|[.*])",
)
VAGUE_PROGRESS = (
    "updated docs today",
    "fixed some stuff",
    "made changes",
    "worked on it",
    "hafiz said ok",
)


def normalize(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "").lower()).strip()


def has_project_tag(memory: dict) -> bool:
    project = normalize(memory.get("project"))
    tags = {normalize(tag) for tag in memory.get("tags") or []}
    return bool(project and (project in PROJECT_TAGS or project in tags or tags & PROJECT_TAGS))


def contains_secretish_text(memory: dict) -> bool:
    joined = " ".join(
        normalize(value)
        for value in (
            memory.get("content"),
            memory.get("why"),
            " ".join(memory.get("tags") or []),
            memory.get("project"),
        )
    )
    return any(re.search(pattern, joined, flags=re.IGNORECASE) for pattern in SECRET_PATTERNS)


def is_vague_memory(memory: dict) -> bool:
    content = normalize(memory.get("content"))
    why = normalize(memory.get("why"))
    if any(phrase in content for phrase in VAGUE_PROGRESS):
        return True
    return len(content.split()) < 8 or len(why.split()) < 5


def validate_memory_payload(memory: dict) -> list[str]:
    errors = []
    category = normalize(memory.get("category"))
    source = normalize(memory.get("source"))
    tags = [normalize(tag) for tag in memory.get("tags") or []]

    if category not in ALLOWED_CATEGORIES:
        errors.append(f"invalid category: {category or 'missing'}")
    if source not in ALLOWED_SOURCES:
        errors.append(f"invalid source: {source or 'missing'}")
    if not has_project_tag(memory):
        errors.append("missing project or project tag")
    if not tags:
        errors.append("missing tags")
    if contains_secretish_text(memory):
        errors.append("contains secret-like or forbidden memory content")
    if is_vague_memory(memory):
        errors.append("memory is too vague to change future behavior")

    return errors


def validate_stale_memory_use(scenario: dict) -> list[str]:
    errors = []
    action = normalize(scenario.get("agent_action"))
    memory_lifecycle = normalize(scenario.get("memory_lifecycle"))
    checked_current_files = bool(scenario.get("checked_current_files"))
    updated_koda = bool(scenario.get("updated_koda"))

    if memory_lifecycle in {"stale", "superseded", "archived"}:
        if "apply" in action and not checked_current_files:
            errors.append("stale memory applied without checking current files")
        if scenario.get("memory_conflicts_with_repo") and not updated_koda:
            errors.append("stale/conflicting memory was not marked for correction")

    return errors


def validate_koda_path(scenario: dict) -> list[str]:
    errors = []
    mcp_status = normalize(scenario.get("mcp_status"))
    cli_health = normalize(scenario.get("cli_health"))
    decision = normalize(scenario.get("decision"))

    if mcp_status == "failed" and cli_health == "pass":
        if "cli" not in decision and "direct" not in decision:
            errors.append("should use direct CLI fallback when MCP fails but CLI health passes")
    if mcp_status == "failed" and cli_health != "pass":
        if "defer" not in decision and "report" not in decision and "failed" not in decision:
            errors.append("should report/defer memory work when both Koda paths are unavailable")

    return errors


def validate_dedupe_decision(scenario: dict) -> list[str]:
    errors = []
    similar_memory_id = normalize(scenario.get("similar_memory_id"))
    similarity = float(scenario.get("similarity") or 0)
    decision = normalize(scenario.get("decision"))

    if similar_memory_id and similarity >= 0.85:
        if "update" not in decision and "skip" not in decision:
            errors.append("high-similarity memory should update/skip instead of storing duplicate")
    if not similar_memory_id and "update" in decision:
        errors.append("should not update a missing memory id")

    return errors


def validate_correction_update(scenario: dict) -> list[str]:
    errors = []
    correction = bool(scenario.get("is_correction"))
    target_id = normalize(scenario.get("target_memory_id"))
    decision = normalize(scenario.get("decision"))
    source = normalize(scenario.get("source"))

    if correction:
        if source != "correction":
            errors.append("correction memory updates must use source=correction")
        if target_id and "update" not in decision:
            errors.append("known correction target should update the existing memory")
        if not target_id and "store" not in decision:
            errors.append("new correction without a target should be stored as a correction")

    return errors


def validate_readonly_audit(scenario: dict) -> list[str]:
    errors = []
    scope = normalize(scenario.get("scope"))
    action = normalize(scenario.get("action"))
    report = normalize(scenario.get("report"))

    if "bulk" in scope or "migration" in scope or "cleanup" in scope:
        if "write" in action or "update" in action or "delete" in action:
            errors.append("bulk memory cleanup must start with read-only audit, not writes")
        for phrase in ("candidate", "risk", "recommendation"):
            if phrase not in report:
                errors.append(f"read-only audit report missing {phrase}")

    return errors


CASES: list[dict] = [
    {
        "id": "KO-001",
        "name": "valid durable Agent OS memory",
        "validator": validate_memory_payload,
        "payload": {
            "category": "lesson",
            "content": (
                "Sifututor Agent OS Koda lesson: health checks should validate "
                "memory payload quality locally without creating throwaway Koda memories."
            ),
            "project": "sifututor",
            "source": "auto-captured",
            "tags": ["sifututor", "agent-os", "koda", "lifecycle-active", "risk-low"],
            "why": "Future agents need a stable way to check memory discipline without polluting Koda.",
        },
        "should_pass": True,
        "why": "Good memories are safe, tagged, sourced, project-scoped, and behavior-changing.",
    },
    {
        "id": "KO-002",
        "name": "invalid source value",
        "validator": validate_memory_payload,
        "payload": {
            "category": "lesson",
            "content": "Sifututor Agent OS memory sources must match the Koda schema.",
            "project": "sifututor",
            "source": "agent-inferred",
            "tags": ["sifututor", "agent-os", "koda"],
            "why": "Invalid source values fail Koda writes and create inconsistent memory records.",
        },
        "should_pass": False,
        "why": "Koda source must be user-stated, auto-captured, or correction.",
    },
    {
        "id": "KO-003",
        "name": "missing project tag",
        "validator": validate_memory_payload,
        "payload": {
            "category": "preference",
            "content": "Hafiz prefers plain-language close-outs with practical meaning first.",
            "project": "",
            "source": "user-stated",
            "tags": ["communication", "agent-os"],
            "why": "Future agents need the preference when speaking with Hafiz.",
        },
        "should_pass": False,
        "why": "Every memory needs a project scope so searches stay relevant.",
    },
    {
        "id": "KO-004",
        "name": "secret-like memory rejected",
        "validator": validate_memory_payload,
        "payload": {
            "category": "fact",
            "content": "Use token=abc123 for the service and check .env.local when needed.",
            "project": "sifututor",
            "source": "auto-captured",
            "tags": ["sifututor", "agent-os", "koda"],
            "why": "This would leak secret handling into durable memory.",
        },
        "should_pass": False,
        "why": "Koda must never store secrets, raw tokens, credentials, or .env references.",
    },
    {
        "id": "KO-005",
        "name": "vague progress memory rejected",
        "validator": validate_memory_payload,
        "payload": {
            "category": "lesson",
            "content": "Updated docs today.",
            "project": "sifututor",
            "source": "auto-captured",
            "tags": ["sifututor", "agent-os"],
            "why": "Done.",
        },
        "should_pass": False,
        "why": "Koda stores durable lessons, not low-signal progress notes.",
    },
    {
        "id": "KO-006",
        "name": "stale memory requires current-state check",
        "validator": validate_stale_memory_use,
        "payload": {
            "memory_lifecycle": "stale",
            "agent_action": "apply old workaround immediately",
            "checked_current_files": False,
            "memory_conflicts_with_repo": True,
            "updated_koda": False,
        },
        "should_pass": False,
        "why": "Old Koda memory is a lead, not permission to act without current evidence.",
    },
    {
        "id": "KO-007",
        "name": "stale memory handled safely",
        "validator": validate_stale_memory_use,
        "payload": {
            "memory_lifecycle": "stale",
            "agent_action": "verify repo state before using lesson",
            "checked_current_files": True,
            "memory_conflicts_with_repo": True,
            "updated_koda": True,
        },
        "should_pass": True,
        "why": "Stale memory can be useful after current files are checked and Koda is corrected.",
    },
    {
        "id": "KO-008",
        "name": "MCP failure uses direct CLI fallback",
        "validator": validate_koda_path,
        "payload": {
            "mcp_status": "failed",
            "cli_health": "pass",
            "decision": "use direct CLI fallback and report it plainly",
        },
        "should_pass": True,
        "why": "Codex should use the CLI-first path when chat MCP is unreliable but direct Koda works.",
    },
    {
        "id": "KO-009",
        "name": "MCP failure without fallback rejected",
        "validator": validate_koda_path,
        "payload": {
            "mcp_status": "failed",
            "cli_health": "pass",
            "decision": "skip memory silently",
        },
        "should_pass": False,
        "why": "Silent memory loss recreates the context problems the Agent OS is meant to prevent.",
    },
    {
        "id": "KO-010",
        "name": "duplicate memory should update",
        "validator": validate_dedupe_decision,
        "payload": {
            "similar_memory_id": "mem_1234",
            "similarity": 0.91,
            "decision": "update existing memory mem_1234 with sharper wording",
        },
        "should_pass": True,
        "why": "High-similarity memories should update or skip instead of creating duplicates.",
    },
    {
        "id": "KO-011",
        "name": "duplicate memory stored again rejected",
        "validator": validate_dedupe_decision,
        "payload": {
            "similar_memory_id": "mem_1234",
            "similarity": 0.91,
            "decision": "store a new memory",
        },
        "should_pass": False,
        "why": "Storing a near-duplicate makes Koda noisier and weaker.",
    },
    {
        "id": "KO-012",
        "name": "correction updates known target",
        "validator": validate_correction_update,
        "payload": {
            "is_correction": True,
            "target_memory_id": "mem_5678",
            "source": "correction",
            "decision": "update existing memory mem_5678",
        },
        "should_pass": True,
        "why": "Corrections should fix the known stale memory instead of adding conflicting truth.",
    },
    {
        "id": "KO-013",
        "name": "correction with wrong source rejected",
        "validator": validate_correction_update,
        "payload": {
            "is_correction": True,
            "target_memory_id": "mem_5678",
            "source": "auto-captured",
            "decision": "update existing memory mem_5678",
        },
        "should_pass": False,
        "why": "User corrections must be marked as corrections for auditability.",
    },
    {
        "id": "KO-014",
        "name": "bulk cleanup starts with read-only audit",
        "validator": validate_readonly_audit,
        "payload": {
            "scope": "bulk memory cleanup",
            "action": "read-only audit",
            "report": "candidate stale memories, risk, recommendation",
        },
        "should_pass": True,
        "why": "Memory migration or cleanup should report candidates and risks before changing Koda.",
    },
    {
        "id": "KO-015",
        "name": "bulk cleanup writes first rejected",
        "validator": validate_readonly_audit,
        "payload": {
            "scope": "bulk memory cleanup",
            "action": "update and delete memories",
            "report": "candidate stale memories",
        },
        "should_pass": False,
        "why": "Bulk memory work should not mutate Koda before a read-only audit.",
    },
]


def run_case(case: dict) -> tuple[bool, list[str]]:
    validator: Callable[[dict], list[str]] = case["validator"]
    errors = validator(case["payload"])
    return not errors, errors


def run(verbose: bool = False) -> int:
    failures = []
    for case in CASES:
        passed_shape, errors = run_case(case)
        ok = passed_shape is case["should_pass"]
        status = "PASS" if ok else "FAIL"

        if verbose or not ok:
            print(f"{status} {case['id']} {case['name']}")
            print(f"  expected pass={case['should_pass']}, observed pass={passed_shape}")
            if errors:
                print("  errors: " + "; ".join(errors))
            print(f"  why={case['why']}")

        if not ok:
            failures.append(case["id"])

    passed = len(CASES) - len(failures)
    print(f"agent-os-koda-fixture-runner: {passed}/{len(CASES)} passed")
    if failures:
        print("failed: " + ", ".join(failures))
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Agent OS Koda memory fixture checks.")
    parser.add_argument("--verbose", action="store_true", help="print every Koda fixture case")
    args = parser.parse_args()
    return run(verbose=args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
