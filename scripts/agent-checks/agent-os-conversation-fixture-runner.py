#!/usr/bin/env python3
"""Check Agent OS short-reply behavior against visible conversation state."""

from __future__ import annotations

import argparse
import re


def normalize(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "").lower()).strip()


def has_exact_commit_only_recommendation(previous: str) -> bool:
    if "commit and push" in previous or "commit + push" in previous:
        return False
    has_commit = "commit" in previous
    has_files = "file" in previous or "files:" in previous
    has_stop = "stop before push" in previous or "do not push" in previous
    has_exact = "exact" in previous or "listed" in previous
    return has_commit and has_files and has_stop and has_exact


def resolve_short_reply(case: dict) -> dict:
    user_reply = normalize(case.get("user_reply"))
    previous = normalize(case.get("previous_assistant"))
    state = normalize(case.get("state"))
    risk = normalize(case.get("risk"))

    result = {
        "action": "clarify",
        "scope": "none",
        "requires_approval": False,
        "must_not": [],
        "must_include": [],
    }

    if user_reply in {"what next", "what is next", "next", "next?"}:
        result["action"] = "recommend_next"
        result["scope"] = "single_next_action"
        result["must_not"].append("invent_new_task")
        return result

    end_to_end_phrases = {
        "autopilot until done",
        "proceed until done",
        "continue until done",
        "start until all done",
        "do everything needed",
        "finish this end to end",
        "handle this fully",
        "take it all the way",
        "complete it properly",
    }

    if user_reply in end_to_end_phrases:
        if state == "approved_path":
            result["action"] = "continue_approved_path"
            result["scope"] = "current_task_context"
            result["must_not"].extend(["reask_same_approval", "start_unrelated_task"])
            return result
        if risk in {"critical", "destructive", "secret", "deploy"}:
            result["action"] = "clarify_or_diagnose"
            result["scope"] = "risk_boundary"
            result["must_not"].extend(["implement_without_explicit_approval", "hide_what_done_means"])
            return result
        result["action"] = "end_to_end_intent"
        result["scope"] = "approved_stop_point"
        result["must_not"].extend(["hide_what_done_means", "bypass_hard_gates"])
        result["must_include"].extend(["recommended_stop_point", "suggested_path", "pause_conditions"])
        return result

    if user_reply in {"approve", "approved", "ok approve"}:
        if "approve commit and push" in previous or "approve commit + push" in previous:
            result["action"] = "commit_and_push"
            result["scope"] = "last_exact_file_list"
            result["requires_approval"] = True
            result["must_not"].extend(["include_unlisted_files", "deploy", "merge"])
            return result
        if "approve push" in previous:
            result["action"] = "push"
            result["scope"] = "last_local_commit"
            result["requires_approval"] = True
            result["must_not"].extend(["commit_new_changes", "deploy", "merge"])
            return result
        if "approve commit" in previous:
            result["action"] = "commit_only"
            result["scope"] = "last_exact_file_list"
            result["requires_approval"] = True
            result["must_not"].extend(["push", "include_unlisted_files"])
            return result
        result["must_not"].append("guess_approval_scope")
        return result

    if user_reply in {"proceed", "continue", "yes", "ok", "proceed next", "go next", "ok proceed"}:
        if risk in {"critical", "destructive", "secret", "deploy"}:
            result["action"] = "clarify_or_diagnose"
            result["scope"] = "risk_boundary"
            result["must_not"].append("implement_without_explicit_approval")
            return result
        if user_reply in {"proceed", "continue", "yes", "ok"} and has_exact_commit_only_recommendation(previous):
            result["action"] = "commit_only"
            result["scope"] = "last_exact_file_list"
            result["requires_approval"] = True
            result["must_not"].extend(["push", "include_unlisted_files"])
            return result
        if "recommended next" in previous or "next best step" in previous or "recommended action" in previous:
            result["action"] = "act_on_last_recommendation"
            result["scope"] = "last_clear_safe_step"
            result["must_not"].extend(["ask_what_proceed_means", "start_unrelated_task"])
            return result
        result["must_not"].append("guess_missing_context")
        return result

    if state == "missing_previous_context":
        result["must_not"].append("guess_missing_context")

    return result


CASES = [
    {
        "id": "CV-001",
        "name": "approve commit and push bundle",
        "previous_assistant": (
            "Recommended next: approve commit and push for exactly these files: "
            "docs/a.md and scripts/b.py."
        ),
        "user_reply": "approve",
        "expected": {
            "action": "commit_and_push",
            "scope": "last_exact_file_list",
            "must_not": ["include_unlisted_files", "deploy"],
        },
        "why": "Bare approve can execute commit+push only when the previous request clearly named that bundle.",
    },
    {
        "id": "CV-002",
        "name": "approve commit only",
        "previous_assistant": "Recommended next: approve commit for exactly these five files.",
        "user_reply": "approve",
        "expected": {
            "action": "commit_only",
            "scope": "last_exact_file_list",
            "must_not": ["push", "include_unlisted_files"],
        },
        "why": "Approve after commit-only request must not become push.",
    },
    {
        "id": "CV-003",
        "name": "approve push only",
        "previous_assistant": "Current state: clean and ahead by one commit. Recommended next: approve push.",
        "user_reply": "approve",
        "expected": {
            "action": "push",
            "scope": "last_local_commit",
            "must_not": ["commit_new_changes", "deploy"],
        },
        "why": "Approve after push-only request should push the existing commit, not create new work.",
    },
    {
        "id": "CV-004",
        "name": "bare approve without context",
        "previous_assistant": "I can help with that.",
        "user_reply": "approve",
        "expected": {
            "action": "clarify",
            "scope": "none",
            "must_not": ["guess_approval_scope"],
        },
        "why": "Without a visible exact approval request, approve is not enough context.",
    },
    {
        "id": "CV-005",
        "name": "proceed follows safe recommendation",
        "previous_assistant": (
            "Next best step: add conversation-state fixtures and wire them into health."
        ),
        "user_reply": "proceed",
        "expected": {
            "action": "act_on_last_recommendation",
            "scope": "last_clear_safe_step",
            "must_not": ["ask_what_proceed_means", "start_unrelated_task"],
        },
        "why": "Proceed should act on the last clear safe recommendation.",
    },
    {
        "id": "CV-006",
        "name": "go next follows recommendation",
        "previous_assistant": "Recommended action: continue with capability fixture checks.",
        "user_reply": "go next",
        "expected": {
            "action": "act_on_last_recommendation",
            "scope": "last_clear_safe_step",
            "must_not": ["ask_what_proceed_means"],
        },
        "why": "Hafiz uses go-next as a real continue command.",
    },
    {
        "id": "CV-007",
        "name": "proceed blocked by critical lane",
        "previous_assistant": "Recommended next: implement the payment callback fix.",
        "user_reply": "proceed",
        "risk": "critical",
        "expected": {
            "action": "clarify_or_diagnose",
            "scope": "risk_boundary",
            "must_not": ["implement_without_explicit_approval"],
        },
        "why": "Critical lanes need read-only diagnosis and explicit implementation approval.",
    },
    {
        "id": "CV-008",
        "name": "what next recommends one action",
        "previous_assistant": "Current state: docs are local only and checks passed.",
        "user_reply": "what is next",
        "expected": {
            "action": "recommend_next",
            "scope": "single_next_action",
            "must_not": ["invent_new_task"],
        },
        "why": "What-next should report the next action, not start work or list random options.",
    },
    {
        "id": "CV-009",
        "name": "proceed without previous context clarifies",
        "previous_assistant": "",
        "user_reply": "proceed next",
        "state": "missing_previous_context",
        "expected": {
            "action": "clarify",
            "scope": "none",
            "must_not": ["guess_missing_context"],
        },
        "why": "Short commands need visible prior context; otherwise the agent should not guess.",
    },
    {
        "id": "CV-010",
        "name": "proceed until done means end-to-end intent",
        "previous_assistant": "I can help fix this staff workflow issue.",
        "user_reply": "proceed until done",
        "expected": {
            "action": "end_to_end_intent",
            "scope": "approved_stop_point",
            "must_not": ["hide_what_done_means", "bypass_hard_gates"],
            "must_include": ["recommended_stop_point", "suggested_path", "pause_conditions"],
        },
        "why": "Natural end-to-end phrases should not require the exact word autopilot.",
    },
    {
        "id": "CV-011",
        "name": "end-to-end intent blocked by critical lane",
        "previous_assistant": "I can help fix this payment callback issue.",
        "user_reply": "finish this end to end",
        "risk": "critical",
        "expected": {
            "action": "clarify_or_diagnose",
            "scope": "risk_boundary",
            "must_not": ["implement_without_explicit_approval", "hide_what_done_means"],
        },
        "why": "End-to-end intent still stops at critical-lane implementation approval.",
    },
    {
        "id": "CV-012",
        "name": "proceed until finish continues approved path",
        "previous_assistant": (
            "Approved path: diagnose -> fix -> tests -> PR -> staging -> "
            "production deploy -> production smoke -> monitoring. I will only "
            "pause if new payment/data/destructive/product risk appears."
        ),
        "user_reply": "proceed until done",
        "state": "approved_path",
        "expected": {
            "action": "continue_approved_path",
            "scope": "current_task_context",
            "must_not": ["reask_same_approval", "start_unrelated_task"],
        },
        "why": "Already-approved paths should continue without re-asking for the same approvals.",
    },
    {
        "id": "CV-013",
        "name": "proceed approves exact commit-only bundle",
        "previous_assistant": (
            "Recommended next: commit these exact files only: docs/a.md and "
            "docs/b.md. I will run the guard, commit locally, and stop before push."
        ),
        "user_reply": "proceed",
        "expected": {
            "action": "commit_only",
            "scope": "last_exact_file_list",
            "must_not": ["push", "include_unlisted_files"],
        },
        "why": "Short replies can approve commit-only when the previous recommendation is exact.",
    },
]


def validate_case(case: dict) -> list[str]:
    observed = resolve_short_reply(case)
    expected = case["expected"]
    errors = []

    for key in ("action", "scope"):
        if observed.get(key) != expected.get(key):
            errors.append(f"{key}: expected {expected.get(key)}, observed {observed.get(key)}")

    observed_must_not = set(observed.get("must_not") or [])
    for item in expected.get("must_not") or []:
        if item not in observed_must_not:
            errors.append(f"missing must_not: {item}")

    observed_must_include = set(observed.get("must_include") or [])
    for item in expected.get("must_include") or []:
        if item not in observed_must_include:
            errors.append(f"missing must_include: {item}")

    return errors


def run(verbose: bool = False) -> int:
    failures = []
    for case in CASES:
        errors = validate_case(case)
        ok = not errors
        status = "PASS" if ok else "FAIL"

        if verbose or not ok:
            print(f"{status} {case['id']} {case['name']}")
            if errors:
                print("  errors: " + "; ".join(errors))
            print(f"  why={case['why']}")

        if not ok:
            failures.append(case["id"])

    passed = len(CASES) - len(failures)
    print(f"agent-os-conversation-fixture-runner: {passed}/{len(CASES)} passed")
    if failures:
        print("failed: " + ", ".join(failures))
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Agent OS conversation-state fixture checks.")
    parser.add_argument("--verbose", action="store_true", help="print every conversation fixture case")
    args = parser.parse_args()
    return run(verbose=args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
