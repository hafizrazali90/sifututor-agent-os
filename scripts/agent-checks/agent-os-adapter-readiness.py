#!/usr/bin/env python3
"""Check whether Codex and Claude adapters are ready for the Agent OS."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PLAYBOOK_DIR = ROOT / "docs" / "agent-playbooks"
SKILL_DIR = ROOT / ".agents" / "skills"
CLAUDE_SETTINGS = ROOT / ".claude" / "settings.json"
CODEX_CONFIG = ROOT / ".codex" / "config.toml"


REQUIRED_PLAYBOOKS = [
    "agent-os-adapter-readiness.md",
    "agent-os-parity-contract.md",
    "multi-agent-adapter-workflow.md",
    "agent-os-skill-registry.md",
    "task-router.md",
    "verify.md",
    "qa.md",
    "review.md",
    "commit.md",
    "save-session.md",
]

REQUIRED_CODEX_SKILLS = [
    "task-router",
    "diagnose",
    "verify",
    "qa",
    "review",
    "commit",
    "save-session",
    "handoff",
    "snapshot",
    "session-map",
    "quick-check",
    "product-design",
    "workflow-improvement",
]

REQUIRED_CLAUDE_HOOKS = [
    ".claude/hooks/koda-context-injector.py",
    ".claude/hooks/validate-branch-name.py",
    ".claude/hooks/conventional-commits.py",
    ".claude/hooks/test-coverage-gate.py",
    ".claude/hooks/friction-logger.py",
]

REQUIRED_CLAUDE_PROJECTS = [
    "ripple-suite",
    "sifu-tutor",
    "sifututor_tutor",
    "sifututor_parent",
    "lls",
    "lls-frontend",
    "lls-mobile",
    "creative-hub",
    "team-inbox",
    "finch-inbox",
]


@dataclass
class CheckResult:
    id: str
    adapter: str
    passed: bool
    detail: str
    required: bool = True
    warnings: list[str] = field(default_factory=list)


def run_command(command: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def file_check(check_id: str, adapter: str, path: Path, detail: str | None = None) -> CheckResult:
    return CheckResult(
        id=check_id,
        adapter=adapter,
        passed=path.is_file(),
        detail=detail or str(path.relative_to(ROOT)),
    )


def check_shared_core() -> list[CheckResult]:
    results: list[CheckResult] = [
        file_check("SH-001", "shared", ROOT / "AGENTS.md", "root AGENTS.md present"),
        file_check("SH-002", "shared", ROOT / "CLAUDE.md", "root CLAUDE.md present"),
    ]
    for index, playbook in enumerate(REQUIRED_PLAYBOOKS, start=3):
        results.append(
            file_check(
                f"SH-{index:03d}",
                "shared",
                PLAYBOOK_DIR / playbook,
                f"{playbook} present",
            )
        )
    return results


def check_codex_adapter() -> list[CheckResult]:
    results: list[CheckResult] = [file_check("CX-001", "codex", CODEX_CONFIG, "Codex config present")]
    config = CODEX_CONFIG.read_text() if CODEX_CONFIG.is_file() else ""
    for check_id, marker in [
        ("CX-002", "[features]"),
        ("CX-003", "hooks = true"),
        ("CX-004", "UserPromptSubmit"),
        ("CX-005", "SessionStart"),
        ("CX-006", "PreToolUse"),
        ("CX-007", "Stop"),
        ("CX-008", "codex-lifecycle-hook.py"),
    ]:
        results.append(
            CheckResult(
                id=check_id,
                adapter="codex",
                passed=marker in config,
                detail=f"Codex config contains {marker}",
            )
        )

    for index, skill in enumerate(REQUIRED_CODEX_SKILLS, start=9):
        skill_file = SKILL_DIR / skill / "SKILL.md"
        results.append(
            CheckResult(
                id=f"CX-{index:03d}",
                adapter="codex",
                passed=skill_file.is_file(),
                detail=f"${skill} wrapper present",
            )
        )

    behavior = run_command([sys.executable, "scripts/agent-checks/agent-os-behavior-trace-runner.py"])
    results.append(
        CheckResult(
            id="CX-030",
            adapter="codex",
            passed=behavior.returncode == 0,
            detail="Codex behavior trace runner passes",
            warnings=[] if behavior.returncode == 0 else (behavior.stderr or behavior.stdout).splitlines()[-3:],
        )
    )
    return results


def check_claude_adapter() -> list[CheckResult]:
    results: list[CheckResult] = [
        file_check("CL-001", "claude", CLAUDE_SETTINGS, "Claude settings present"),
        file_check("CL-002", "claude", ROOT / "CLAUDE.md", "Claude umbrella reference present"),
    ]

    settings: dict[str, Any] = {}
    if CLAUDE_SETTINGS.is_file():
        try:
            settings = json.loads(CLAUDE_SETTINGS.read_text())
            results.append(CheckResult("CL-003", "claude", True, "Claude settings JSON parses"))
        except json.JSONDecodeError as exc:
            results.append(CheckResult("CL-003", "claude", False, f"Claude settings JSON invalid: {exc}"))
    else:
        results.append(CheckResult("CL-003", "claude", False, "Claude settings JSON unavailable"))

    additional_dirs = set(settings.get("additionalDirectories") or [])
    for index, project in enumerate(REQUIRED_CLAUDE_PROJECTS, start=4):
        results.append(
            CheckResult(
                id=f"CL-{index:03d}",
                adapter="claude",
                passed=project in additional_dirs,
                detail=f"Claude additionalDirectories includes {project}",
            )
        )

    hooks = settings.get("hooks") if isinstance(settings.get("hooks"), dict) else {}
    for offset, hook_name in enumerate(["UserPromptSubmit", "PreToolUse", "PostToolUse"], start=20):
        results.append(
            CheckResult(
                id=f"CL-{offset:03d}",
                adapter="claude",
                passed=hook_name in hooks,
                detail=f"Claude hook configured: {hook_name}",
            )
        )

    for index, hook in enumerate(REQUIRED_CLAUDE_HOOKS, start=30):
        hook_path = ROOT / hook
        results.append(
            CheckResult(
                id=f"CL-{index:03d}",
                adapter="claude",
                passed=hook_path.is_file(),
                detail=f"{hook} present",
            )
        )

    compile_result = run_command([sys.executable, "-m", "py_compile", *REQUIRED_CLAUDE_HOOKS])
    results.append(
        CheckResult(
            id="CL-040",
            adapter="claude",
            passed=compile_result.returncode == 0,
            detail="Claude hook scripts compile",
            warnings=[] if compile_result.returncode == 0 else (compile_result.stderr or compile_result.stdout).splitlines()[-3:],
        )
    )

    parity = (PLAYBOOK_DIR / "agent-os-parity-contract.md").read_text()
    registry = (PLAYBOOK_DIR / "agent-os-skill-registry.md").read_text()
    for check_id, marker in [
        ("CL-041", "/task-router"),
        ("CL-042", "/verify"),
        ("CL-043", "/qa"),
        ("CL-044", "/review"),
        ("CL-045", "/commit"),
        ("CL-046", "/save-session"),
    ]:
        results.append(
            CheckResult(
                id=check_id,
                adapter="claude",
                passed=marker in parity and marker in registry,
                detail=f"Claude adapter marker documented: {marker}",
            )
        )

    return results


def check_optional_live_claude(require_live: bool) -> list[CheckResult]:
    live = run_command(
        [
            sys.executable,
            "scripts/agent-checks/agent-os-behavior-trace-runner.py",
            "--live-claude",
            "--json",
        ],
        timeout=180,
    )
    warnings: list[str] = []
    passed = live.returncode == 0
    detail = "Claude live behavior trace completed"
    if live.returncode == 0:
        try:
            payload = json.loads(live.stdout)
            claude_states = [
                (case.get("claude") or {}).get("state")
                for case in payload.get("cases", [])
                if case.get("claude") is not None
            ]
            available = sum(1 for state in claude_states if state == "available")
            total = len(claude_states)
            detail = f"Claude live behavior traces available for {available}/{total} cases"
            if total == 0 or available != total:
                passed = False
                warnings.append("Claude CLI did not return usable live traces for every case")
        except json.JSONDecodeError:
            passed = False
            warnings.append("live Claude output was not JSON")
    else:
        warnings.extend((live.stderr or live.stdout or "live Claude trace failed").splitlines()[-4:])

    return [
        CheckResult(
            id="LV-001",
            adapter="claude-live",
            passed=passed,
            detail=detail,
            required=require_live,
            warnings=warnings,
        )
    ]


def summarize(results: list[CheckResult], print_json: bool) -> int:
    required_results = [result for result in results if result.required]
    required_failures = [result for result in required_results if not result.passed]

    if print_json:
        print(
            json.dumps(
                {
                    "passed": len(required_results) - len(required_failures),
                    "total": len(required_results),
                    "failures": [result.id for result in required_failures],
                    "results": [result.__dict__ for result in results],
                },
                indent=2,
            )
        )
    else:
        for result in results:
            if result.passed:
                status = "PASS"
            elif result.required:
                status = "FAIL"
            else:
                status = "WARN"
            print(f"{status} {result.id} [{result.adapter}] {result.detail}")
            for warning in result.warnings:
                print(f"  - {warning}")
        print(
            "agent-os-adapter-readiness: "
            f"{len(required_results) - len(required_failures)}/{len(required_results)} passed"
        )

    return 0 if not required_failures else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print machine-readable results")
    parser.add_argument("--live-claude", action="store_true", help="run optional live Claude CLI traces")
    parser.add_argument(
        "--require-live-claude",
        action="store_true",
        help="fail when --live-claude cannot prove every Claude live trace",
    )
    args = parser.parse_args()

    results: list[CheckResult] = []
    results.extend(check_shared_core())
    results.extend(check_codex_adapter())
    results.extend(check_claude_adapter())
    if args.live_claude or args.require_live_claude:
        results.extend(check_optional_live_claude(require_live=args.require_live_claude))
    return summarize(results, args.json)


if __name__ == "__main__":
    raise SystemExit(main())
