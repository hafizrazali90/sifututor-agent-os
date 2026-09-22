#!/usr/bin/env python3
"""Run realistic Agent OS scenario checks against the Codex router."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
import re
import sys
import types


ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / "scripts" / "agent-checks" / "codex-lifecycle-hook.py"
LAB_DOC = ROOT / "docs" / "agent-playbooks" / "agent-os-scenario-lab.md"


@dataclass(frozen=True)
class Scenario:
    id: str
    area: str
    prompt: str
    expected_skill: str
    reason_contains: str
    actions_contain: list[str] = field(default_factory=list)
    actions_absent: list[str] = field(default_factory=list)


SCENARIOS = [
    Scenario(
        id="RW-001",
        area="commit boundary",
        prompt="approve commit only for the validation loop files",
        expected_skill="$commit",
        reason_contains="commit-only bundle",
        actions_contain=["pre-commit guard", "exact approved file list", "Do not push"],
    ),
    Scenario(
        id="RW-002",
        area="push boundary",
        prompt="approve push",
        expected_skill="$review",
        reason_contains="outbound",
        actions_contain=["pre-push", "explicit approval"],
    ),
    Scenario(
        id="RW-003",
        area="critical lane",
        prompt="Fix the payment callback bug in production.",
        expected_skill="$diagnose",
        reason_contains="critical lane",
        actions_contain=["critical lane", "read-only", "wait for approval"],
        actions_absent=["commit and push"],
    ),
    Scenario(
        id="RW-004",
        area="staff intake",
        prompt="A staff member says the SIMS modal does not open.",
        expected_skill="$diagnose",
        reason_contains="reported operational context",
        actions_contain=["reported symptom", "reproduce or inspect", "normal GitHub/task workflow"],
    ),
    Scenario(
        id="RW-005",
        area="agent-as-tester",
        prompt="The agent fixed a visible button and says Hafiz please check it.",
        expected_skill="$verify",
        reason_contains="verification gap",
        actions_contain=["agent can safely check", "browser", "human verification only"],
    ),
    Scenario(
        id="RW-006",
        area="memory authority",
        prompt="Koda says this workaround was accepted. Apply it.",
        expected_skill="$task-router",
        reason_contains="historical context",
        actions_contain=["historical context", "check current files", "update Koda"],
    ),
    Scenario(
        id="RW-007",
        area="session tracking",
        prompt="This session is getting long; create a mindmap and return path.",
        expected_skill="$session-map",
        reason_contains="live session tracking",
        actions_contain=["Human Snapshot", "structured agent context"],
    ),
    Scenario(
        id="RW-008",
        area="production boundary",
        prompt="Proceed until production.",
        expected_skill="$review",
        reason_contains="outbound",
        actions_contain=["pre-push", "explicit approval", "verify", "qa"],
        actions_absent=["production is done"],
    ),
    Scenario(
        id="RW-009",
        area="forbidden secret boundary",
        prompt="Open .env and check the key.",
        expected_skill="$task-router",
        reason_contains="forbidden boundary",
        actions_contain=["blocked boundary", "Do not read `.env*`", "safe alternative"],
    ),
    Scenario(
        id="RW-010",
        area="validation target",
        prompt="I want you to test and improve the Agent OS until we get 90% accuracy.",
        expected_skill="$workflow-improvement",
        reason_contains="90% accuracy target",
        actions_contain=["validation-loop.py", "deterministic Agent OS checks", "below 90%"],
    ),
    Scenario(
        id="RW-011",
        area="readiness",
        prompt="Is this repo Agent OS-ready?",
        expected_skill="$quick-check",
        reason_contains="workflow health",
        actions_contain=["workflow-doctor.sh", "PASS/FAIL/PARTIAL"],
    ),
    Scenario(
        id="RW-012",
        area="product design",
        prompt="Let's brainstorm a new tutor request module workflow.",
        expected_skill="$product-design",
        reason_contains="product design",
        actions_contain=["PRD", "UX spec", "build prompts"],
        actions_absent=["commit"],
    ),
    Scenario(
        id="RW-013",
        area="github pr evidence",
        prompt="Is PR #8 ready to merge?",
        expected_skill="$review",
        reason_contains="GitHub PR readiness",
        actions_contain=["GitHub read probe", "CI/check evidence", "Do not merge"],
    ),
    Scenario(
        id="RW-014",
        area="planner intake evidence",
        prompt="Planner has a staff card saying the parent app request is broken.",
        expected_skill="$diagnose",
        reason_contains="Planner-reported operational context",
        actions_contain=["Planner read-only", "reported symptom", "Do not mutate Planner"],
    ),
    Scenario(
        id="RW-015",
        area="production monitoring evidence",
        prompt="Monitor production logs after the sifu-tutor deploy.",
        expected_skill="$monitor-production-logs",
        reason_contains="production monitoring evidence",
        actions_contain=["production logs probe", "Sentry", "BetterStack", "Do not deploy"],
    ),
    Scenario(
        id="RW-016",
        area="stale memory conflict",
        prompt="Koda memory says we accepted this path, but the current docs disagree.",
        expected_skill="$task-router",
        reason_contains="Koda conflict",
        actions_contain=["context-authority.md", "owner source", "update Koda"],
    ),
    Scenario(
        id="RW-017",
        area="claude codex comparison",
        prompt="Compare Claude and Codex for this workflow and tell me if they behave differently.",
        expected_skill="$workflow-improvement",
        reason_contains="Claude/Codex behavior comparison",
        actions_contain=["parity runner", "route", "approval boundary", "different wording is fine"],
    ),
    Scenario(
        id="RW-018",
        area="live evidence report",
        prompt="Generate a live evidence probe report for the Agent OS.",
        expected_skill="$quick-check",
        reason_contains="live evidence probe report",
        actions_contain=[
            "agent-os-live-evidence-report.py",
            "GitHub, Planner, production monitoring, and Koda",
            "read-only evidence",
        ],
        actions_absent=["deploy"],
    ),
]


def load_classifier():
    source = HOOK.read_text()
    entrypoint = "\nraise SystemExit(main())"
    if entrypoint not in source:
        raise RuntimeError(f"cannot find hook entrypoint in {HOOK}")
    module = types.ModuleType("codex_lifecycle_hook_for_scenario_lab")
    module.__file__ = str(HOOK)
    exec(source.split(entrypoint, 1)[0], module.__dict__)
    return module.classify_prompt


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def scenario_doc_ids() -> set[str]:
    text = LAB_DOC.read_text()
    return set(re.findall(r"\bRW-\d{3}\b", text))


def missing_snippets(actions: list[str], snippets: list[str]) -> list[str]:
    action_text = [normalize(action) for action in actions]
    return [
        snippet
        for snippet in snippets
        if not any(normalize(snippet) in action for action in action_text)
    ]


def present_forbidden(actions: list[str], snippets: list[str]) -> list[str]:
    text = normalize("\n".join(actions))
    return [snippet for snippet in snippets if normalize(snippet) in text]


def run_scenarios(verbose: bool = False) -> tuple[int, int, list[str]]:
    classify_prompt = load_classifier()
    documented = scenario_doc_ids()
    failures: list[str] = []

    for scenario in SCENARIOS:
        skill, actions, reason = classify_prompt(scenario.prompt)
        skill_ok = skill == scenario.expected_skill
        reason_ok = normalize(scenario.reason_contains) in normalize(reason)
        missing_actions = missing_snippets(actions, scenario.actions_contain)
        forbidden_actions = present_forbidden(actions, scenario.actions_absent)
        documented_ok = scenario.id in documented
        ok = skill_ok and reason_ok and not missing_actions and not forbidden_actions and documented_ok
        if verbose or not ok:
            status = "PASS" if ok else "FAIL"
            print(f"{status} {scenario.id} [{scenario.area}] prompt={scenario.prompt!r}")
            print(f"  expected skill={scenario.expected_skill!r}, observed={skill!r}")
            print(f"  reason={reason}")
            if actions:
                print("  actions:")
                for action in actions:
                    print(f"    - {action}")
            if missing_actions:
                print("  missing action text: " + ", ".join(missing_actions))
            if forbidden_actions:
                print("  forbidden action text present: " + ", ".join(forbidden_actions))
            if not documented_ok:
                print(f"  missing from {LAB_DOC.relative_to(ROOT)}")
        if not ok:
            failures.append(scenario.id)

    passed = len(SCENARIOS) - len(failures)
    print(f"agent-os-scenario-lab-runner: {passed}/{len(SCENARIOS)} passed")
    return passed, len(SCENARIOS), failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=float, default=0.90, help="required score as a decimal")
    parser.add_argument("--verbose", action="store_true", help="print every scenario")
    args = parser.parse_args()

    if not 0 < args.target <= 1:
        print("--target must be greater than 0 and at most 1", file=sys.stderr)
        return 2

    passed, total, failures = run_scenarios(verbose=args.verbose)
    score = passed / total if total else 0.0
    print(f"Scenario Lab score: {score * 100:.1f}%")
    if score >= args.target:
        print("Target reached.")
        return 0

    print("Target not reached. Failing scenarios: " + ", ".join(failures))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
