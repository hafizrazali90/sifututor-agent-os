#!/usr/bin/env python3
"""Check Agent OS capability state and tool-use expectations."""

from __future__ import annotations

import argparse
import re


ALLOWED_STATES = {
    "available",
    "fallback",
    "unknown",
    "not_connected",
    "blocked",
    "exception_only",
    "forbidden",
}
ACTIONABLE_STATES = {"available", "fallback"}
OUTBOUND_TOOLS = {"git_push", "pull_request", "merge", "deploy"}
CRITICAL_TOOLS = {"production_logs", "deploy", "payment_admin", "mobile_api_contract"}
FORBIDDEN_TOOLS = {"env_files", "secrets", "live_write", "no_verify"}
STAFF_BLOCKED_TOOLS = {
    "git_commit",
    "git_push",
    "merge",
    "deploy",
    "koda_write",
    "production_logs",
}


def normalize(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "").lower()).strip()


def validate_capability_record(record: dict) -> list[str]:
    errors = []
    name = normalize(record.get("name"))
    state = normalize(record.get("state"))
    action = normalize(record.get("action"))
    approval = normalize(record.get("approval"))
    safety = normalize(record.get("safety"))
    reporting = normalize(record.get("reporting"))
    actor = normalize(record.get("actor") or "agent")
    tier = normalize(record.get("tier"))
    scope = normalize(record.get("scope") or "task_scoped")
    task_relevant = bool(record.get("task_relevant", True))
    checked = bool(record.get("checked"))

    if state not in ALLOWED_STATES:
        errors.append(f"invalid capability state: {state or 'missing'}")

    if state == "unknown" and action in {"use", "claim", "write", "deploy", "push"}:
        errors.append("unknown capability cannot be used or claimed before checking")

    if state == "not_connected" and action not in {"report", "fallback", "skip"}:
        errors.append("not_connected capability must be reported or routed to a safe fallback")

    if state == "blocked" and approval != "explicit":
        errors.append("blocked capability needs explicit approval before use")

    if state == "exception_only" and action in {"use", "write", "claim"} and approval != "explicit":
        errors.append("exception-only capability needs explicit current-session request before use")

    if tier == "auto_read" and state in ACTIONABLE_STATES:
        if not task_relevant and action in {"use", "read", "scan"}:
            errors.append("auto-read capability must stay relevant to the active task")
        if scope in {"broad", "unrelated", "unbounded"}:
            errors.append("auto-read capability must stay narrowly scoped")
        if task_relevant and action in {"ask_permission", "skip"}:
            errors.append("auto-read capability should be used proactively when task-relevant")
        if action == "use" and approval in {"requested", "explicit"}:
            errors.append("auto-read capability should not need extra approval when task-relevant")

    if state == "forbidden" and action != "refuse":
        errors.append("forbidden capability must be refused, not worked around")

    if name in OUTBOUND_TOOLS and action in {"push", "deploy", "merge", "open_pr", "use"}:
        if approval != "explicit":
            errors.append("outbound action needs explicit current-session approval")

    if name in CRITICAL_TOOLS and action in {"use", "deploy", "write"}:
        if record.get("diagnosis_phase") != "complete":
            errors.append("critical capability requires read-only diagnosis before implementation/use")

    if name in FORBIDDEN_TOOLS and state != "forbidden":
        errors.append("forbidden boundary must be marked forbidden")

    if actor == "staff" and name in STAFF_BLOCKED_TOOLS and state not in {"blocked", "forbidden", "not_connected"}:
        errors.append("staff capability should default to least-privilege")

    if state in ACTIONABLE_STATES and not checked:
        errors.append("available/fallback capability needs current-session verification")

    if safety == "unsafe":
        errors.append("unsafe capability cannot pass regardless of tool connection")

    if state not in ACTIONABLE_STATES and reporting == "silent":
        errors.append("missing or blocked capability must be reported plainly")

    return errors


CASES = [
    {
        "id": "CP-001",
        "name": "verified filesystem capability",
        "record": {
            "name": "filesystem_write",
            "state": "available",
            "action": "use",
            "approval": "not_needed",
            "safety": "safe",
            "checked": True,
            "reporting": "plain",
        },
        "should_pass": True,
        "why": "A safe local capability can be used after current-session verification.",
    },
    {
        "id": "CP-002",
        "name": "unknown GitHub capability cannot be claimed",
        "record": {
            "name": "github",
            "state": "unknown",
            "action": "claim",
            "approval": "not_needed",
            "safety": "safe",
            "checked": False,
            "reporting": "plain",
        },
        "should_pass": False,
        "why": "Agents should not promise GitHub work until the session tool is confirmed.",
    },
    {
        "id": "CP-003",
        "name": "Plane is exception-only by default",
        "record": {
            "name": "plane",
            "state": "exception_only",
            "action": "skip",
            "approval": "not_needed",
            "safety": "safe",
            "checked": True,
            "reporting": "plain",
        },
        "should_pass": True,
        "why": "Plane is no longer part of the default Agent OS path.",
    },
    {
        "id": "CP-004",
        "name": "Planner read-only intake",
        "record": {
            "name": "planner",
            "state": "available",
            "action": "use",
            "approval": "not_needed",
            "safety": "safe",
            "checked": True,
            "reporting": "plain",
        },
        "should_pass": True,
        "why": "Planner can be used for read-only intake when connected and relevant.",
    },
    {
        "id": "CP-005",
        "name": "Planner write without approval blocked",
        "record": {
            "name": "planner_write",
            "state": "blocked",
            "action": "write",
            "approval": "missing",
            "safety": "safe",
            "checked": True,
            "reporting": "plain",
        },
        "should_pass": False,
        "why": "Planner state/content changes need explicit Hafiz approval.",
    },
    {
        "id": "CP-006",
        "name": "Google Drive fallback for staff",
        "record": {
            "name": "google_drive",
            "state": "not_connected",
            "action": "fallback",
            "approval": "not_needed",
            "safety": "safe",
            "actor": "staff",
            "checked": True,
            "reporting": "plain",
        },
        "should_pass": True,
        "why": "Staff without Drive tooling should get a plain fallback instead of a failed tool call.",
    },
    {
        "id": "CP-007",
        "name": "production logs need diagnosis and approval",
        "record": {
            "name": "production_logs",
            "state": "blocked",
            "action": "use",
            "approval": "missing",
            "safety": "safe",
            "checked": True,
            "reporting": "plain",
            "diagnosis_phase": "missing",
        },
        "should_pass": False,
        "why": "Production log access is risk-sensitive and should not be treated as ordinary capability.",
    },
    {
        "id": "CP-008",
        "name": "deploy approved after diagnosis",
        "record": {
            "name": "deploy",
            "state": "blocked",
            "action": "deploy",
            "approval": "explicit",
            "safety": "safe",
            "checked": True,
            "reporting": "plain",
            "diagnosis_phase": "complete",
        },
        "should_pass": True,
        "why": "Deploy is still blocked by default, but explicit approval plus diagnosis clears this fixture.",
    },
    {
        "id": "CP-009",
        "name": "secret boundary refused",
        "record": {
            "name": "env_files",
            "state": "forbidden",
            "action": "refuse",
            "approval": "not_applicable",
            "safety": "safe",
            "checked": True,
            "reporting": "plain",
        },
        "should_pass": True,
        "why": "Forbidden boundaries should be refused clearly.",
    },
    {
        "id": "CP-010",
        "name": "secret boundary workaround rejected",
        "record": {
            "name": "env_files",
            "state": "forbidden",
            "action": "use",
            "approval": "explicit",
            "safety": "safe",
            "checked": True,
            "reporting": "plain",
        },
        "should_pass": False,
        "why": "Even approval does not make forbidden secret reads valid.",
    },
    {
        "id": "CP-011",
        "name": "staff deploy defaults blocked",
        "record": {
            "name": "deploy",
            "state": "available",
            "action": "use",
            "approval": "not_needed",
            "safety": "safe",
            "actor": "staff",
            "checked": True,
            "reporting": "plain",
            "diagnosis_phase": "complete",
        },
        "should_pass": False,
        "why": "Staff rollout should start least-privilege, especially for deploy capability.",
    },
    {
        "id": "CP-012",
        "name": "blocked capability reported plainly",
        "record": {
            "name": "git_commit",
            "state": "blocked",
            "action": "report",
            "approval": "explicit",
            "safety": "safe",
            "checked": True,
            "reporting": "plain",
        },
        "should_pass": True,
        "why": "Blocked does not mean impossible; it means approval or a gate is needed and should be explained.",
    },
    {
        "id": "CP-013",
        "name": "blocked capability silent failure rejected",
        "record": {
            "name": "git_push",
            "state": "blocked",
            "action": "report",
            "approval": "explicit",
            "safety": "safe",
            "checked": True,
            "reporting": "silent",
        },
        "should_pass": False,
        "why": "Agents must tell Hafiz what is missing instead of silently skipping capability work.",
    },
    {
        "id": "CP-014",
        "name": "auto-read evidence used proactively",
        "record": {
            "name": "monitoring_readonly",
            "state": "available",
            "action": "use",
            "approval": "not_needed",
            "safety": "safe",
            "tier": "auto_read",
            "scope": "task_scoped",
            "task_relevant": True,
            "checked": True,
            "reporting": "plain",
        },
        "should_pass": True,
        "why": "Approved read-only evidence should be used when it is relevant to the active task.",
    },
    {
        "id": "CP-015",
        "name": "auto-read evidence should not ask again",
        "record": {
            "name": "monitoring_readonly",
            "state": "available",
            "action": "ask_permission",
            "approval": "requested",
            "safety": "safe",
            "tier": "auto_read",
            "scope": "task_scoped",
            "task_relevant": True,
            "checked": True,
            "reporting": "plain",
        },
        "should_pass": False,
        "why": "Extra permission questions for task-relevant auto-read access create the back-and-forth Hafiz wants to remove.",
    },
    {
        "id": "CP-016",
        "name": "auto-read unrelated access rejected",
        "record": {
            "name": "monitoring_readonly",
            "state": "available",
            "action": "use",
            "approval": "not_needed",
            "safety": "safe",
            "tier": "auto_read",
            "scope": "task_scoped",
            "task_relevant": False,
            "checked": True,
            "reporting": "plain",
        },
        "should_pass": False,
        "why": "Auto-read removes repeated permission prompts, but it is not permission to inspect unrelated systems.",
    },
    {
        "id": "CP-017",
        "name": "auto-read broad scan rejected",
        "record": {
            "name": "server_ssh",
            "state": "available",
            "action": "scan",
            "approval": "not_needed",
            "safety": "safe",
            "tier": "auto_read",
            "scope": "broad",
            "task_relevant": True,
            "checked": True,
            "reporting": "plain",
        },
        "should_pass": False,
        "why": "Read-only access should be narrow and task-scoped, not a broad exploration pass.",
    },
]


def run(verbose: bool = False) -> int:
    failures = []
    for case in CASES:
        errors = validate_capability_record(case["record"])
        passed_shape = not errors
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
    print(f"agent-os-capability-fixture-runner: {passed}/{len(CASES)} passed")
    if failures:
        print("failed: " + ", ".join(failures))
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Agent OS capability fixture checks.")
    parser.add_argument("--verbose", action="store_true", help="print every capability fixture case")
    args = parser.parse_args()
    return run(verbose=args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
