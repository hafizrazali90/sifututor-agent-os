#!/usr/bin/env python3
"""Check that Claude/Codex Agent OS parity stays wired to shared playbooks."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
PLAYBOOK_DIR = ROOT / "docs" / "agent-playbooks"
SKILL_DIR = ROOT / ".agents" / "skills"
KILO_AGENT = ROOT / ".kilo" / "agents" / "sifututor-agent-os.md"

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
        "name": "Session Map",
        "playbook": "session-map.md",
        "codex_skill": "session-map",
        "codex_alias": "$session-map",
        "claude_aliases": ["/session-map"],
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
    {
        "name": "Workflow Improvement",
        "playbook": "agent-os-improvement-loop.md",
        "codex_skill": "workflow-improvement",
        "codex_alias": "$workflow-improvement",
        "claude_aliases": ["/workflow-improvement"],
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


REQUIRED_REVIEW_STANDARD_PHRASES = [
    "Behavior Parity Review Standard",
    "Different wording is fine. Different workflow behavior is not fine.",
    "Route",
    "First move",
    "Approval boundary",
    "Evidence standard",
    "State language",
    "Memory and task routing",
    "Close-out",
    "Allowed adapter differences",
    "Parity drift",
    "Kilo",
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
    {
        "id": "BP-009",
        "scenario": "multiple goals or side paths",
        "snippets": ["Session Map", "main goal", "return path"],
    },
    {
        "id": "BP-010",
        "scenario": "workflow improvement request",
        "snippets": ["Agent OS Improvement Loop", "classify the mistake", "connected docs"],
    },
    {
        "id": "BP-014",
        "scenario": "a required check cannot be run in this session",
        "snippets": [
            "report it as not run",
            "never claim an exact state that was not observed",
            "unrun",
        ],
    },
    {
        "id": "BP-015",
        "scenario": "worktree/branch/issue identity before staging",
        "snippets": [
            "worktree, branch, and issue/PR identity",
            "before staging",
            "Ordinary discussion does not need this step",
        ],
    },
]


# Claude adapters whose installed presence can be spot-checked when a Claude
# adapter root is supplied. Real enforcement of the installed adapter *content*
# lives in agent-os-claude-adapter-check.py; this runner only proves that a
# Claude alias promised by the docs is not markdown-only.
#
# This is deliberately opt-in: repo fixtures must stay portable across machines
# and CI, so they must not depend unconditionally on a developer's home
# directory. Supply --claude-adapter-root or CLAUDE_ADAPTER_HOME to enable it.
CLAUDE_ADAPTER_SKILLS = {
    "Task Router": "task-router",
    "Commit": "commit",
    "Save Session": "save-session",
    "Workflow Improvement": "workflow-improvement",
    "Verify": "verify",
    "Review": "review",
    "Handoff": "handoff",
}


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
    kilo_label = f"Native `{codex_skill}` skill"
    if kilo_label not in parity_text:
        errors.append(f"{name}: parity contract does not mention Kilo adapter {kilo_label}")
    for alias in claude_aliases:
        if alias not in parity_text:
            errors.append(f"{name}: parity contract does not mention Claude alias {alias}")

    return errors


def check_kilo_adapter(texts: dict[str, str]) -> list[str]:
    errors = []
    if not KILO_AGENT.is_file():
        return ["missing Kilo project adapter .kilo/agents/sifututor-agent-os.md"]

    kilo_text = read(KILO_AGENT)
    required_agent_markers = [
        "model: zai/glm-5.3",
        ".agents/skills/",
        "reported symptom",
        "diagnose",
        "Reading files",
        "parity contract",
    ]
    for marker in required_agent_markers:
        if not contains(kilo_text, marker):
            errors.append(f"Kilo adapter missing behavior marker: {marker}")

    for doc_name in ("parity", "registry"):
        text = texts[doc_name]
        for marker in ("Kilo Code", ".kilo/agents/sifututor-agent-os.md", ".agents/skills/"):
            if not contains(text, marker):
                errors.append(f"{doc_name} doc missing Kilo marker: {marker}")
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

    for phrase in REQUIRED_REVIEW_STANDARD_PHRASES:
        if not contains(parity_text, phrase):
            errors.append(f"parity contract missing review standard phrase: {phrase}")

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


def check_installed_claude_adapters(adapter_root: Path) -> list[str]:
    """Confirm each promised Claude adapter exists under the supplied root.

    Closes the "alias exists only in markdown" gap without hard-coding a
    developer home: the caller decides which adapter root to inspect.
    """
    errors = []
    for workflow_name, skill_dir in sorted(CLAUDE_ADAPTER_SKILLS.items()):
        skill_path = adapter_root / "skills" / skill_dir / "SKILL.md"
        if not skill_path.is_file():
            errors.append(
                f"{workflow_name}: docs promise a Claude adapter but no installed "
                f"skill file exists at {skill_path}"
            )
    return errors


ADAPTER_SELF_TEST_CASES = [
    {
        "name": "complete adapter root passes",
        "present": sorted(CLAUDE_ADAPTER_SKILLS.values()),
        "expect_errors": False,
    },
    {
        "name": "markdown-only workflow-improvement alias fails",
        "present": [name for name in CLAUDE_ADAPTER_SKILLS.values() if name != "workflow-improvement"],
        "expect_errors": True,
        "expect_substring": "workflow-improvement",
    },
    {
        "name": "missing save-session adapter fails",
        "present": [name for name in CLAUDE_ADAPTER_SKILLS.values() if name != "save-session"],
        "expect_errors": True,
        "expect_substring": "save-session",
    },
    # issue-56 correction: verify/review/handoff must be spot-checked for
    # installed-adapter presence the same way the original four adapters are,
    # so a missing installed Claude Verify/Review/Handoff skill fails loudly
    # here instead of being silently skipped.
    {
        "name": "missing verify adapter fails",
        "present": [name for name in CLAUDE_ADAPTER_SKILLS.values() if name != "verify"],
        "expect_errors": True,
        "expect_substring": "verify",
    },
    {
        "name": "missing review adapter fails",
        "present": [name for name in CLAUDE_ADAPTER_SKILLS.values() if name != "review"],
        "expect_errors": True,
        "expect_substring": "review",
    },
    {
        "name": "missing handoff adapter fails",
        "present": [name for name in CLAUDE_ADAPTER_SKILLS.values() if name != "handoff"],
        "expect_errors": True,
        "expect_substring": "handoff",
    },
    {
        "name": "empty adapter root fails for every promised adapter",
        "present": [],
        "expect_errors": True,
        "expect_substring": "task-router",
    },
]


def run_adapter_self_test() -> int:
    """Portable self-test for check_installed_claude_adapters.

    Uses synthetic temp roots so the negative case is permanent and does not
    depend on any real machine state.
    """
    import tempfile

    all_ok = True
    print("agent-os-parity-fixture-runner -- installed Claude adapter self-test (synthetic roots)")
    for case in ADAPTER_SELF_TEST_CASES:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            for skill_dir in case["present"]:
                skill_path = root / "skills" / skill_dir / "SKILL.md"
                skill_path.parent.mkdir(parents=True, exist_ok=True)
                skill_path.write_text("synthetic self-test fixture\n")
            errors = check_installed_claude_adapters(root)

        problems = []
        if bool(errors) != case["expect_errors"]:
            problems.append(f"expected errors={case['expect_errors']}, got {errors}")
        expect_substring = case.get("expect_substring")
        if expect_substring and not any(expect_substring in error for error in errors):
            problems.append(f"expected an error mentioning {expect_substring!r}, got {errors}")

        status = "PASS" if not problems else "FAIL"
        print(f"{status} {case['name']}")
        for problem in problems:
            print(f"  - {problem}")
        if problems:
            all_ok = False

    overall = "PASS" if all_ok else "FAIL"
    print(f"adapter self-test: {overall} ({len(ADAPTER_SELF_TEST_CASES)} cases)")
    return 0 if all_ok else 1


def run(verbose: bool = False, claude_adapter_root: Path | None = None) -> int:
    required_files = (
        PARITY_CONTRACT,
        SKILL_REGISTRY,
        EVAL_DOC,
        COVERAGE_MAP,
        AGENTS,
        HEALTH,
        KILO_AGENT,
    )
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
    failures.extend(check_kilo_adapter(texts))

    adapter_note = "installed Claude adapter presence: not checked (no adapter root supplied)"
    if claude_adapter_root is not None:
        adapter_failures = check_installed_claude_adapters(claude_adapter_root)
        failures.extend(adapter_failures)
        adapter_note = (
            f"installed Claude adapter presence: checked against {claude_adapter_root}"
        )

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
    print(f"agent-os-parity-fixture-runner: {adapter_note}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Agent OS Claude/Codex parity fixture checks.")
    parser.add_argument("--verbose", action="store_true", help="print detailed parity fixture output")
    parser.add_argument(
        "--claude-adapter-root",
        help=(
            "optional Claude adapter root (for example ~/.claude) to confirm that "
            "documented Claude aliases exist as installed skill files. Defaults to "
            "the CLAUDE_ADAPTER_HOME environment variable when set; otherwise the "
            "check is skipped so this runner stays portable."
        ),
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help=(
            "run the portable synthetic-root self-test for the installed Claude "
            "adapter presence check instead of the repo parity checks"
        ),
    )
    args = parser.parse_args()

    if args.self_test:
        return run_adapter_self_test()

    root_value = args.claude_adapter_root or os.environ.get("CLAUDE_ADAPTER_HOME")
    adapter_root = Path(root_value).expanduser() if root_value else None
    return run(verbose=args.verbose, claude_adapter_root=adapter_root)


if __name__ == "__main__":
    raise SystemExit(main())
