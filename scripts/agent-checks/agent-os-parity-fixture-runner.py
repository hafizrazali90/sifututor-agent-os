#!/usr/bin/env python3
"""Check that Claude/Codex Agent OS parity stays wired to shared playbooks."""

from __future__ import annotations

import argparse
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
PLAYBOOK_DIR = ROOT / "docs" / "agent-playbooks"
SKILL_DIR = ROOT / ".agents" / "skills"

PARITY_CONTRACT = PLAYBOOK_DIR / "agent-os-parity-contract.md"
SKILL_REGISTRY = PLAYBOOK_DIR / "agent-os-skill-registry.md"
EVAL_DOC = PLAYBOOK_DIR / "agent-os-evals.md"
COVERAGE_MAP = PLAYBOOK_DIR / "agent-os-eval-coverage-map.md"
AGENTS = ROOT / "AGENTS.md"
CLAUDE = ROOT / "CLAUDE.md"
HEALTH = ROOT / "scripts" / "agent-checks" / "agent-os-health.sh"


WORKFLOWS = [
    {
        "name": "Task Router",
        "playbook": "task-router.md",
        "codex_skill": "task-router",
        "codex_alias": "$task-router",
        "claude_aliases": ["/task-router"],
    },
    {
        "name": "Diagnose",
        "playbook": "diagnose.md",
        "codex_skill": "diagnose",
        "codex_alias": "$diagnose",
        "claude_aliases": ["/diagnose"],
    },
    {
        "name": "Product Design",
        "playbook": "product-design.md",
        "codex_skill": "product-design",
        "codex_alias": "$product-design",
        "claude_aliases": ["/lite-prd", "/prd-clarifier", "/prd-to-ux", "/ux-to-prompts"],
    },
    {
        "name": "Verify",
        "playbook": "verify.md",
        "codex_skill": "verify",
        "codex_alias": "$verify",
        "claude_aliases": ["/verify"],
    },
    {
        "name": "QA",
        "playbook": "qa.md",
        "codex_skill": "qa",
        "codex_alias": "$qa",
        "claude_aliases": ["/qa"],
    },
    {
        "name": "Review",
        "playbook": "review.md",
        "codex_skill": "review",
        "codex_alias": "$review",
        "claude_aliases": ["/review"],
    },
    {
        "name": "Commit",
        "playbook": "commit.md",
        "codex_skill": "commit",
        "codex_alias": "$commit",
        "claude_aliases": ["/commit"],
    },
    {
        "name": "Save Session",
        "playbook": "save-session.md",
        "codex_skill": "save-session",
        "codex_alias": "$save-session",
        "claude_aliases": ["/save-session"],
    },
    {
        "name": "Handoff",
        "playbook": "handoff.md",
        "codex_skill": "handoff",
        "codex_alias": "$handoff",
        "claude_aliases": ["/handoff"],
    },
    {
        "name": "Snapshot",
        "playbook": "snapshot.md",
        "codex_skill": "snapshot",
        "codex_alias": "$snapshot",
        "claude_aliases": ["/snapshot"],
    },
    {
        "name": "Quick Check",
        "playbook": "quick-check.md",
        "codex_skill": "quick-check",
        "codex_alias": "$quick-check",
        "claude_aliases": ["/quick-check"],
    },
    {
        "name": "Monitor Production Logs",
        "playbook": "monitor-production-logs.md",
        "codex_skill": "monitor-production-logs",
        "codex_alias": "$monitor-production-logs",
        "claude_aliases": ["/monitor-production-logs"],
    },
]


REQUIRED_CONTRACT_PHRASES = [
    "source of truth",
    "routing decision",
    "approval boundary",
    "safety guardrail",
    "evidence standard",
    "state update",
    "handoff shape",
    "plain-language close-out",
]


BEHAVIOR_FIXTURES = [
    {
        "id": "BP-001",
        "scenario": "commit-only approval",
        "snippets": ["Commit only", "exact approved file list", "Do not push"],
    },
    {
        "id": "BP-002",
        "scenario": "commit plus push approval",
        "snippets": ["pre-push review", "exact approved bundle", "remote state"],
    },
    {
        "id": "BP-003",
        "scenario": "feature or workflow design",
        "snippets": ["brainstorm/product design", "options and tradeoffs", "do not implement until approval"],
    },
    {
        "id": "BP-004",
        "scenario": "critical lane work",
        "snippets": ["read-only diagnosis", "Wait for approval before implementation"],
    },
    {
        "id": "BP-005",
        "scenario": "verify or QA user-facing workflow",
        "snippets": ["human-journey evidence", "what the agent can safely check"],
    },
    {
        "id": "BP-006",
        "scenario": "save or hand off session",
        "snippets": ["current state", "evidence", "next action", "Koda"],
    },
    {
        "id": "BP-007",
        "scenario": "staff or Planner reported bug",
        "snippets": ["report as a symptom", "reproduce or inspect", "GitHub/task workflow"],
    },
    {
        "id": "BP-008",
        "scenario": "Plane status without explicit Plane request",
        "snippets": ["Do not use Plane by default", "Mission Ledger", "close-out"],
    },
]


def read(path: Path) -> str:
    return path.read_text()


def contains(text: str, snippet: str) -> bool:
    return snippet.lower() in text.lower()


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def check_workflow(workflow: dict[str, object], texts: dict[str, str]) -> list[str]:
    errors = []
    name = str(workflow["name"])
    playbook = str(workflow["playbook"])
    codex_skill = str(workflow["codex_skill"])
    codex_alias = str(workflow["codex_alias"])
    claude_aliases = list(workflow["claude_aliases"])

    playbook_path = PLAYBOOK_DIR / playbook
    skill_path = SKILL_DIR / codex_skill / "SKILL.md"

    if not playbook_path.is_file():
        errors.append(f"{name}: missing shared playbook {playbook}")
    if not skill_path.is_file():
        errors.append(f"{name}: missing Codex skill wrapper {skill_path.relative_to(ROOT)}")

    if skill_path.is_file() and playbook not in read(skill_path):
        errors.append(f"{name}: Codex wrapper does not point to {playbook}")

    for doc_name in ("parity", "registry"):
        text = texts[doc_name]
        if playbook not in text:
            errors.append(f"{name}: {doc_name} doc does not mention {playbook}")
        if codex_alias not in text:
            errors.append(f"{name}: {doc_name} doc does not mention {codex_alias}")

    parity_text = texts["parity"]
    for alias in claude_aliases:
        if alias not in parity_text:
            errors.append(f"{name}: parity contract does not mention Claude alias {alias}")

    return errors


def check_plane_policy(texts: dict[str, str]) -> list[str]:
    errors = []
    agents_text = texts["agents"]
    claude_text = texts["claude"]
    stale_claude_phrases = [
        "Plane is Hafiz's human mission board",
        "Plane for Hafiz-visible status",
        "relevant Plane card",
    ]

    if "Plane is exception-only" not in agents_text:
        errors.append("AGENTS.md must state Plane is exception-only")

    if claude_text:
        if "Plane is exception-only" not in claude_text:
            errors.append("CLAUDE.md must state Plane is exception-only when present")

        for phrase in stale_claude_phrases:
            if phrase in claude_text:
                errors.append(f"CLAUDE.md contains stale Plane-default wording: {phrase}")

    return errors


def check_supporting_docs(texts: dict[str, str]) -> list[str]:
    errors = []
    parity_text = texts["parity"]

    for phrase in REQUIRED_CONTRACT_PHRASES:
        if not contains(parity_text, phrase):
            errors.append(f"parity contract missing required behavior phrase: {phrase}")

    for eval_id in ("AO-082", "AO-083", "AO-084"):
        if eval_id not in texts["evals"]:
            errors.append(f"agent-os-evals.md missing {eval_id}")
        if eval_id not in texts["coverage"]:
            errors.append(f"agent-os-eval-coverage-map.md missing {eval_id}")

    if "agent-os-parity-fixture-runner.py" not in texts["health"]:
        errors.append("agent-os-health.sh must run agent-os-parity-fixture-runner.py")

    return errors


def check_behavior_fixtures(texts: dict[str, str]) -> list[str]:
    errors = []
    parity_text = texts["parity"]

    for fixture in BEHAVIOR_FIXTURES:
        fixture_id = fixture["id"]
        if fixture_id not in parity_text:
            errors.append(f"parity contract missing behavior fixture {fixture_id}")
            continue
        for snippet in fixture["snippets"]:
            if not contains(parity_text, snippet):
                errors.append(
                    f"{fixture_id}: expected behavior snippet missing from parity contract: {snippet}"
                )

    return errors


def run(verbose: bool = False) -> int:
    required_files = (PARITY_CONTRACT, SKILL_REGISTRY, EVAL_DOC, COVERAGE_MAP, AGENTS, HEALTH)
    missing_files = [path for path in required_files if not path.is_file()]
    if missing_files:
        for path in missing_files:
            print(f"FAIL missing file: {path.relative_to(ROOT)}")
        return 1

    texts = {
        "parity": read(PARITY_CONTRACT),
        "registry": read(SKILL_REGISTRY),
        "evals": read(EVAL_DOC),
        "coverage": read(COVERAGE_MAP),
        "agents": read(AGENTS),
        "claude": read(CLAUDE) if CLAUDE.is_file() else "",
        "health": read(HEALTH),
    }

    failures = []
    for workflow in WORKFLOWS:
        failures.extend(check_workflow(workflow, texts))
    failures.extend(check_plane_policy(texts))
    failures.extend(check_supporting_docs(texts))
    failures.extend(check_behavior_fixtures(texts))

    if verbose or failures:
        for failure in failures:
            print(f"FAIL {failure}")

    checked = len(WORKFLOWS)
    behavior_checked = len(BEHAVIOR_FIXTURES)
    if failures:
        print(
            "agent-os-parity-fixture-runner: "
            f"{len(failures)} failure(s) across {checked} workflows "
            f"and {behavior_checked} behavior fixtures"
        )
        return 1

    print(
        "agent-os-parity-fixture-runner: "
        f"{checked}/{checked} workflows and "
        f"{behavior_checked}/{behavior_checked} behavior fixtures passed"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Agent OS Claude/Codex parity fixture checks.")
    parser.add_argument("--verbose", action="store_true", help="print detailed parity fixture output")
    args = parser.parse_args()
    return run(verbose=args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
