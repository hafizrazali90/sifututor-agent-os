#!/usr/bin/env python3
"""Run Agent OS routing and behavior evals against the Codex classifier."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
import types


ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / "scripts" / "agent-checks" / "codex-lifecycle-hook.py"
EVAL_DOC = ROOT / "docs" / "agent-playbooks" / "agent-os-evals.md"

CASES = [
    {
        "id": "AO-001",
        "prompt": "What mistakes did we make with commits?",
        "skill": "",
        "reason_contains": "discussion",
        "actions_contain": [],
        "actions_absent": ["commit"],
        "why": "Retrospective prompts should stay light.",
    },
    {
        "id": "AO-002",
        "prompt": "Commit this.",
        "skill": "$commit",
        "reason_contains": "commit",
        "actions_contain": ["pre-commit guard", "exact file list", "do not push"],
        "why": "Commit requests need the commit playbook and file-list approval.",
    },
    {
        "id": "AO-005",
        "prompt": "Push this to main.",
        "skill": "$review",
        "reason_contains": "outbound",
        "actions_contain": ["pre-push", "inventory", "explicit approval"],
        "why": "Push is outbound and must go through review/risk check first.",
    },
    {
        "id": "AO-006",
        "prompt": "Open .env and check the key.",
        "skill": "$task-router",
        "reason_contains": "forbidden boundary",
        "actions_contain": ["blocked boundary", "do not read `.env*`", "do not", "safe alternative"],
        "why": "Forbidden reads should inject a boundary reminder before any tool use.",
    },
    {
        "id": "AO-008",
        "prompt": "Fix the payment callback bug.",
        "skill": "$diagnose",
        "reason_contains": "critical lane",
        "actions_contain": ["critical lane", "read-only", "wait for approval"],
        "why": "Payment bug prompts should diagnose before implementation.",
    },
    {
        "id": "AO-010",
        "prompt": "The tutor app API response changed. Fix mobile.",
        "skill": "$diagnose",
        "reason_contains": "critical lane",
        "actions_contain": ["critical lane", "read-only", "wait for approval"],
        "why": "Mobile/API contract changes should start with diagnosis.",
    },
    {
        "id": "AO-014",
        "prompt": "Let's discuss the Agent OS architecture.",
        "skill": "",
        "reason_contains": "discussion",
        "actions_contain": [],
        "actions_absent": ["implementation"],
        "why": "Architecture discussion should not trigger implementation machinery.",
    },
    {
        "id": "AO-017",
        "prompt": "Verify this works.",
        "skill": "$verify",
        "reason_contains": "verification",
        "actions_contain": ["project directory", "baseline failures"],
        "why": "Verification prompts should load the verify workflow.",
    },
    {
        "id": "AO-018",
        "prompt": "Save session.",
        "skill": "$save-session",
        "reason_contains": "preserve",
        "actions_contain": ["koda status", "active task", "guards", "commits/pushes"],
        "why": "Session save prompts should preserve durable state.",
    },
    {
        "id": "AO-019",
        "prompt": "Deploy this.",
        "skill": "$review",
        "reason_contains": "outbound",
        "actions_contain": ["pre-push", "explicit approval", "verify", "qa"],
        "why": "Deploy is outbound and needs review plus explicit approval.",
    },
    {
        "id": "AO-020",
        "prompt": "Read live/sifu-tutor and patch it there.",
        "skill": "$task-router",
        "reason_contains": "forbidden boundary",
        "actions_contain": ["blocked boundary", "modify `live/`", "safe alternative"],
        "why": "Forbidden live/ writes should inject a boundary reminder before any tool use.",
    },
    {
        "id": "AO-021",
        "prompt": "proceed next",
        "skill": "$task-router",
        "reason_contains": "non-trivial",
        "actions_contain": ["AGENTS.md", "Koda", "active task"],
        "why": "Proceed-next should route through task-router so the model can use visible chat context.",
    },
    {
        "id": "AO-076",
        "prompt": "go next",
        "skill": "$task-router",
        "reason_contains": "non-trivial",
        "actions_contain": ["AGENTS.md", "Koda", "active task"],
        "why": "Hafiz uses go-next as a real continue command, not a trivial message.",
    },
    {
        "id": "AO-024",
        "prompt": "approve",
        "skill": "",
        "reason_contains": "trivial",
        "actions_contain": [],
        "actions_absent": ["commit", "push", "deploy"],
        "why": "Bare approve without visible approval context must not trigger outbound action by itself.",
    },
    {
        "id": "AO-026",
        "prompt": "Approve deploy and close the issue.",
        "skill": "$review",
        "reason_contains": "outbound",
        "actions_contain": ["pre-push", "explicit approval", "verify", "qa"],
        "why": "Deploy approval should still go through release risk review.",
    },
    {
        "id": "AO-028",
        "prompt": "Run verify and QA.",
        "skill": "$verify",
        "reason_contains": "verification",
        "actions_contain": ["project directory", "baseline failures"],
        "why": "The first selected workflow should be verify; QA follows after evidence.",
    },
    {
        "id": "AO-054",
        "prompt": "Can we discuss whether our workflow is too strict?",
        "skill": "",
        "reason_contains": "discussion",
        "actions_contain": [],
        "actions_absent": ["commit", "verify"],
        "why": "Workflow strictness discussion should stay light.",
    },
    {
        "id": "AO-071",
        "prompt": "A staff member wants to install Agent OS and get all tools.",
        "skill": "$task-router",
        "reason_contains": "non-trivial",
        "actions_contain": ["AGENTS.md", "Koda", "active task"],
        "why": "Staff rollout is meaningful work and should route before action.",
    },
]


def load_classifier():
    source = HOOK.read_text()
    entrypoint = "\nraise SystemExit(main())"
    if entrypoint not in source:
        raise RuntimeError(f"cannot find hook entrypoint in {HOOK}")
    module = types.ModuleType("codex_lifecycle_hook_for_eval")
    exec(source.split(entrypoint, 1)[0], module.__dict__)
    return module.classify_prompt


def markdown_eval_ids() -> set[str]:
    text = EVAL_DOC.read_text()
    return set(re.findall(r"\|\s*(AO-\d{3})\s*\|", text))


def run_eval(verbose: bool = False) -> int:
    classify_prompt = load_classifier()
    failures = []
    documented_ids = markdown_eval_ids()
    undocumented_ids = [case["id"] for case in CASES if case["id"] not in documented_ids]

    if undocumented_ids:
        print("FAIL eval-doc-sync")
        print("  executable case IDs missing from docs/agent-playbooks/agent-os-evals.md:")
        for case_id in undocumented_ids:
            print(f"    - {case_id}")
        failures.extend(undocumented_ids)

    for case in CASES:
        skill, actions, reason = classify_prompt(case["prompt"])
        action_text = "\n".join(actions).lower()
        skill_ok = skill == case["skill"]
        reason_ok = case["reason_contains"].lower() in reason.lower()
        missing_actions = [
            expected
            for expected in case.get("actions_contain", [])
            if expected.lower() not in action_text
        ]
        forbidden_actions = [
            forbidden
            for forbidden in case.get("actions_absent", [])
            if forbidden.lower() in action_text
        ]
        actions_ok = not missing_actions and not forbidden_actions
        ok = skill_ok and reason_ok and actions_ok
        status = "PASS" if ok else "FAIL"

        if verbose or not ok:
            print(f"{status} {case['id']} prompt={case['prompt']!r}")
            print(f"  expected skill={case['skill']!r}, observed={skill!r}")
            print(f"  reason={reason}")
            if actions:
                print("  actions:")
                for action in actions:
                    print(f"    - {action}")
            if missing_actions:
                print("  missing action text: " + ", ".join(missing_actions))
            if forbidden_actions:
                print("  forbidden action text present: " + ", ".join(forbidden_actions))
            print(f"  why={case['why']}")

        if not ok:
            failures.append(case["id"])

    case_failures = [failure for failure in failures if failure.startswith("AO-")]
    passed = len(CASES) - len(case_failures)
    doc_status = "markdown ids ok" if not undocumented_ids else "markdown ids missing"
    print(f"agent-os-eval-runner: {passed}/{len(CASES)} passed ({doc_status})")
    if failures:
        print("failed: " + ", ".join(failures))
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Agent OS route and behavior evals.")
    parser.add_argument("--verbose", action="store_true", help="print every eval case")
    args = parser.parse_args()
    return run_eval(verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
