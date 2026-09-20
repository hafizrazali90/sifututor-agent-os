#!/usr/bin/env python3
"""Check whether Codex, Claude, and Kilo adapters are ready for the Agent OS."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import claude_hook_dispatch  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
PLAYBOOK_DIR = ROOT / "docs" / "agent-playbooks"
SKILL_DIR = ROOT / ".agents" / "skills"
CLAUDE_SETTINGS = ROOT / ".claude" / "settings.json"
CODEX_CONFIG = ROOT / ".codex" / "config.toml"
KILO_AGENT = ROOT / ".kilo" / "agents" / "sifututor-agent-os.md"
GLOBAL_CLAUDE_INSTRUCTIONS = Path.home() / ".claude" / "CLAUDE.md"
ACTIVE_ADAPTER_INSTRUCTIONS = (
    GLOBAL_CLAUDE_INSTRUCTIONS,
    ROOT / "CLAUDE.md",
    ROOT / "AGENTS.md",
    ROOT / ".codex" / "config.toml",
)


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
    "handoff.md",
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
    # Umbrella dispatcher wrappers for sub-project-only gates (issue 96).
    ".claude/hooks/quality-gate.py",
    ".claude/hooks/workflow-gate.py",
]

REQUIRED_CLAUDE_PROJECTS = [
    "kelas",
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


def run_command(
    command: list[str],
    timeout: int = 120,
    *,
    input_text: str | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        input=input_text,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def file_check(
    check_id: str,
    adapter: str,
    path: Path,
    detail: str | None = None,
    *,
    required: bool = True,
) -> CheckResult:
    return CheckResult(
        id=check_id,
        adapter=adapter,
        passed=path.is_file(),
        detail=detail or str(path.relative_to(ROOT)),
        required=required,
    )


def check_shared_core() -> list[CheckResult]:
    root_claude = ROOT / "CLAUDE.md"
    results: list[CheckResult] = [
        file_check("SH-001", "shared", ROOT / "AGENTS.md", "root AGENTS.md present"),
        file_check(
            "SH-002",
            "shared",
            root_claude,
            "root CLAUDE.md present for full umbrella workspace",
            required=root_claude.is_file(),
        ),
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


def project_claude_dirs() -> list[Path]:
    projects: list[Path] = []
    for path in sorted(ROOT.iterdir(), key=lambda item: item.name):
        if not path.is_dir() or path.name.startswith("."):
            continue
        if (path / "AGENTS.md").is_file() and (path / ".claude/settings.json").is_file():
            projects.append(path)
    return projects


def hook_keys_present(settings: dict[str, Any]) -> bool:
    hooks = settings.get("hooks") if isinstance(settings.get("hooks"), dict) else {}
    return all(key in hooks for key in ["UserPromptSubmit", "PreToolUse", "PostToolUse"])


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
        ("CX-032", "secret_output_guard.py"),
    ]:
        results.append(
            CheckResult(
                id=check_id,
                adapter="codex",
                passed=marker in config,
                detail=f"Codex config contains {marker}",
            )
        )

    try:
        codex_hooks = tomllib.loads(config).get("hooks", {})
        visual_guard_wildcard = any(
            isinstance(group, dict)
            and group.get("matcher") == ".*"
            and any(
                isinstance(hook, dict)
                and "secret_output_guard.py" in str(hook.get("command") or "")
                for hook in group.get("hooks", [])
            )
            for group in codex_hooks.get("PreToolUse", [])
        )
    except tomllib.TOMLDecodeError:
        visual_guard_wildcard = False
    results.append(
        CheckResult(
            id="CX-033",
            adapter="codex",
            passed=visual_guard_wildcard,
            detail="Codex secret guard runs before every tool type",
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
    codex_prompt = run_command(
        [sys.executable, "scripts/agent-checks/codex-lifecycle-hook.py"],
        input_text=json.dumps(
            {
                "hook_event_name": "UserPromptSubmit",
                "prompt": "Save this session for another agent.",
                "cwd": str(ROOT),
            }
        ),
    )
    codex_output = codex_prompt.stdout if codex_prompt.returncode == 0 else ""
    closeout_markers = (
        "Close-out default:",
        "Explanation-first default:",
        "who uses the workflow",
        "intended build",
        "evidence plan in English once",
        "go one by one",
        "highest proven state",
        "recommended next action",
        "whether Hafiz needs to decide",
    )
    results.append(
        CheckResult(
            id="CX-031",
            adapter="codex",
            passed=all(marker in codex_output for marker in closeout_markers),
            detail="Codex prompt adapter emits the shared communication reminders",
            warnings=[]
            if codex_prompt.returncode == 0
            else (codex_prompt.stderr or codex_prompt.stdout).splitlines()[-3:],
        )
    )
    return results


def check_claude_common_runtime() -> list[CheckResult]:
    credential_assignment = re.compile(
        r"(?im)^\s*(?:[-*]\s*)?(?:db credentials?|admin login|api key|access token|password)"
        r"\s*[:=]\s*(?!<|see\b|scoped\b|none\b|not\b)\S+"
    )
    instruction_files = [path for path in ACTIVE_ADAPTER_INSTRUCTIONS if path.is_file()]
    unsafe_instruction_files = [
        path
        for path in instruction_files
        if credential_assignment.search(path.read_text(errors="replace"))
    ]
    results = [
        CheckResult(
            id="CL-047",
            adapter="claude",
            passed=not unsafe_instruction_files,
            detail="active Claude/Codex instructions contain no credential-shaped assignments",
            required=bool(instruction_files),
        )
    ]
    detector_self_test = bool(
        credential_assignment.search("DB credentials: fixture-user / fixture-password")
    ) and not credential_assignment.search("DB credentials: scoped access registry")
    results.append(
        CheckResult(
            id="CL-049",
            adapter="claude",
            passed=detector_self_test,
            detail="credential-assignment detector catches synthetic values and allows scoped references",
        )
    )

    bridge_env = dict(os.environ)
    bridge_env.pop("KODA_API_KEY", None)
    bridge = run_command(
        [sys.executable, ".claude/hooks/koda-context-injector.py"],
        input_text=json.dumps({"user_prompt": "Please improve this workflow comprehensively"}),
        env=bridge_env,
    )
    bridge_output = bridge.stdout if bridge.returncode == 0 else ""
    bridge_markers = (
        "Agent OS close-out reminder",
        "Agent OS explanation-first reminder",
        "who uses the workflow",
        "intended build",
        "evidence plan in English once",
        "go one by one",
        "highest proven state",
        "recommended next action",
        "whether Hafiz needs to decide",
    )
    results.append(
        CheckResult(
            id="CL-048",
            adapter="claude",
            passed=all(marker in bridge_output for marker in bridge_markers),
            detail="Claude prompt bridge emits shared communication guidance without Koda",
            warnings=[] if bridge.returncode == 0 else (bridge.stderr or bridge.stdout).splitlines()[-3:],
        )
    )
    results.extend(check_claude_hook_resolution())
    return results


def check_claude_hook_resolution() -> list[CheckResult]:
    """Catch configured hook paths that cannot resolve for a launch scenario.

    Issue 96: a sub-project hook command that resolves relative to
    `CLAUDE_PROJECT_DIR` silently breaks for an umbrella-launched session unless
    the umbrella also answers that hook name. A missing PreToolUse script exits
    2, which Claude reads as a hard block on every Bash call.
    """
    results: list[CheckResult] = []

    dispatch_self_test = run_command(
        [sys.executable, "-m", "unittest", "discover", "-s", "scripts/agent-checks", "-p", "test_claude_hook_dispatch.py"]
    )
    results.append(
        CheckResult(
            id="CL-052",
            adapter="claude",
            passed=dispatch_self_test.returncode == 0,
            detail="Claude hook dispatcher fixtures pass (worktree resolution, rejection preserved, missing hook warns)",
            warnings=[]
            if dispatch_self_test.returncode == 0
            else (dispatch_self_test.stderr or dispatch_self_test.stdout).splitlines()[-4:],
        )
    )

    findings = claude_hook_dispatch.audit_workspace_hook_configuration(ROOT)
    blocking = [finding for finding in findings if finding.blocks_readiness]
    advisory = [
        finding for finding in findings if not finding.ok and not finding.blocks_readiness
    ]
    results.append(
        CheckResult(
            id="CL-053",
            adapter="claude",
            passed=not blocking,
            # No product projects in this checkout means nothing to prove here.
            required=bool(findings),
            detail=(
                "every configured PreToolUse gate resolves for project and umbrella "
                f"launches ({len(findings)} hook paths checked)"
            ),
            warnings=[finding.detail for finding in blocking[:8]],
        )
    )
    results.append(
        CheckResult(
            id="CL-054",
            adapter="claude",
            passed=not advisory,
            # Non-PreToolUse gaps degrade one event; they never cancel a tool call.
            required=False,
            detail=(
                f"no non-blocking umbrella-launch hook gaps ({len(advisory)} reported)"
            ),
            warnings=[finding.detail for finding in advisory[:8]],
        )
    )
    return results


def check_developer_claude_adapter(*, strict_project_hooks: bool) -> list[CheckResult]:
    results: list[CheckResult] = [
        file_check(
            "CL-001",
            "claude",
            CLAUDE_SETTINGS,
            "root Claude settings present for full umbrella workspace",
            required=False,
        ),
        file_check(
            "CL-002",
            "claude",
            ROOT / "CLAUDE.md",
            "root Claude umbrella reference present for full umbrella workspace",
            required=False,
        ),
    ]

    for index, hook in enumerate(REQUIRED_CLAUDE_HOOKS, start=30):
        hook_path = ROOT / hook
        results.append(
            CheckResult(
                id=f"CL-{index:03d}",
                adapter="claude",
                passed=hook_path.is_file(),
                detail=f"{hook} present for project-level bridge",
            )
        )

    compile_result = run_command([sys.executable, "-m", "py_compile", *REQUIRED_CLAUDE_HOOKS])
    results.append(
        CheckResult(
            id="CL-040",
            adapter="claude",
            passed=compile_result.returncode == 0,
            detail="shared Claude hook scripts compile",
            warnings=[] if compile_result.returncode == 0 else (compile_result.stderr or compile_result.stdout).splitlines()[-3:],
        )
    )

    projects = project_claude_dirs()
    product_workspace_present = any((ROOT / project).is_dir() for project in REQUIRED_CLAUDE_PROJECTS)
    results.append(
        CheckResult(
            id="CL-D001",
            adapter="claude",
            passed=bool(projects),
            detail="at least one project-level Claude settings file present",
            required=product_workspace_present,
        )
    )

    for index, project in enumerate(projects, start=2):
        settings_path = project / ".claude/settings.json"
        settings: dict[str, Any] = {}
        parsed = False
        try:
            settings = json.loads(settings_path.read_text())
            parsed = True
        except json.JSONDecodeError:
            parsed = False
        results.append(
            CheckResult(
                id=f"CL-D{index:03d}",
                adapter="claude",
                passed=parsed,
                detail=f"{project.name} Claude settings JSON parses",
            )
        )
        results.append(
            CheckResult(
                id=f"CL-D{index + 40:03d}",
                adapter="claude",
                passed=parsed and hook_keys_present(settings),
                detail=f"{project.name} Claude hooks configured",
                required=strict_project_hooks,
            )
        )
        results.append(
            CheckResult(
                id=f"CL-D{index + 80:03d}",
                adapter="claude",
                passed=(project / ".claude/hooks/run-shared-hook.sh").is_file(),
                detail=f"{project.name} shared hook bridge present",
                required=strict_project_hooks,
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

    results.extend(check_claude_common_runtime())
    return results


def check_claude_adapter(*, strict_project_hooks: bool) -> list[CheckResult]:
    if not CLAUDE_SETTINGS.is_file():
        return check_developer_claude_adapter(strict_project_hooks=strict_project_hooks)

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

    claude_visual_guard_wildcard = any(
        isinstance(group, dict)
        and group.get("matcher") == ".*"
        and any(
            isinstance(hook, dict)
            and "secret_output_guard.py" in str(hook.get("command") or "")
            for hook in group.get("hooks", [])
        )
        for group in hooks.get("PreToolUse", [])
    )
    results.append(
        CheckResult(
            id="CL-023",
            adapter="claude",
            passed=claude_visual_guard_wildcard,
            detail="Claude PreToolUse runs the shared secret-output guard for every tool type",
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

    results.extend(check_claude_common_runtime())
    return results


def check_claude_installed_adapter() -> list[CheckResult]:
    """Run the phase-one installed-adapter check against the REAL ~/.claude files.

    This complements check_claude_adapter/check_developer_claude_adapter,
    which only inspect repo-tracked marker files: this check reads the actual
    installed global CLAUDE.md, task-router, commit, save-session, and
    workflow-improvement adapter bodies that govern live Claude behavior on
    this machine. A documented alias with no installed file is a hard failure
    here. Phase-one scope plus the 2026-08-01 issue-30 correction only -- see
    agent-os-claude-adapter-check.py's module docstring.
    """
    proc = run_command(
        [sys.executable, "scripts/agent-checks/agent-os-claude-adapter-check.py", "--json"]
    )
    warnings: list[str] = []
    passed = proc.returncode == 0
    try:
        payload = json.loads(proc.stdout)
        passed = bool(payload.get("passed")) and proc.returncode == 0
        if not passed:
            for result in payload.get("results", []):
                for error in result.get("errors", []):
                    warnings.append(f"{result.get('adapter')}: {error}")
    except json.JSONDecodeError:
        passed = False
        warnings.append((proc.stderr or proc.stdout or "no output").strip()[-500:])

    return [
        CheckResult(
            id="CL-050",
            adapter="claude",
            passed=passed,
            detail=(
                "installed Claude global adapters pass the linkage/drift "
                "check (CLAUDE.md, task-router, commit, save-session, "
                "workflow-improvement, verify, review, and handoff skills; "
                "a missing installed file fails here; not full parity)"
            ),
            warnings=warnings[:10],
        )
    ]


def check_claude_installed_adapter_self_test() -> list[CheckResult]:
    """Run agent-os-claude-adapter-check.py's own durable synthetic-fixture
    self-test, so readiness/health fail if the checker's negation-scoping
    logic itself regresses -- even while the real installed adapters happen
    to look safe. This is distinct from CL-050, which checks the actual
    installed adapter files. Phase-one scope only.
    """
    proc = run_command(
        [sys.executable, "scripts/agent-checks/agent-os-claude-adapter-check.py", "--self-test"]
    )
    passed = proc.returncode == 0
    warnings: list[str] = []
    if not passed:
        warnings.append((proc.stdout or proc.stderr or "no output").strip()[-2000:])

    return [
        CheckResult(
            id="CL-051",
            adapter="claude",
            passed=passed,
            detail=(
                "installed-adapter checker's own synthetic-fixture self-test "
                "passes (proves the negation-scoping/detection logic itself "
                "across all eight checked adapters, including the "
                "save-session, workflow-improvement, and issue-56 "
                "verify/review/handoff correction fixtures)"
            ),
            warnings=warnings[:10],
        )
    ]


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


def check_kilo_adapter(*, check_installed: bool, require_installed: bool) -> list[CheckResult]:
    results = [file_check("KO-001", "kilo", KILO_AGENT, "Kilo project agent present")]
    checks = [
        (
            "KO-002",
            [sys.executable, "scripts/agent-checks/kilo-agent-os-adapter-check.py"],
            "portable Kilo adapter definition passes",
        ),
        (
            "KO-003",
            [sys.executable, "scripts/agent-checks/kilo-agent-os-adapter-check.py", "--self-test"],
            "Kilo adapter checker rejects unsafe and drifted fixtures",
        ),
        (
            "KO-004",
            [
                sys.executable,
                "scripts/agent-checks/agent-os-behavior-trace-runner.py",
                "--self-test-kilo",
            ],
            "Kilo event parser and staff-report drift detector pass",
        ),
    ]
    for check_id, command, detail in checks:
        proc = run_command(command)
        results.append(
            CheckResult(
                id=check_id,
                adapter="kilo",
                passed=proc.returncode == 0,
                detail=detail,
                warnings=[]
                if proc.returncode == 0
                else (proc.stderr or proc.stdout or "no output").splitlines()[-4:],
            )
        )

    if check_installed:
        proc = run_command(
            [sys.executable, "scripts/agent-checks/kilo-agent-os-adapter-check.py", "--installed"],
            timeout=90,
        )
        results.append(
            CheckResult(
                id="KO-005",
                adapter="kilo-installed",
                passed=proc.returncode == 0,
                detail=(
                    "installed Kilo agent, configured Z.ai/GLM default, extension CLI, "
                    "and Vision MCP pass; runtime model identity is unobserved"
                ),
                required=require_installed,
                warnings=[]
                if proc.returncode == 0
                else (proc.stderr or proc.stdout or "no output").splitlines()[-4:],
            )
        )
    return results


def check_optional_live_kilo(require_live: bool) -> list[CheckResult]:
    live = run_command(
        [
            sys.executable,
            "scripts/agent-checks/agent-os-behavior-trace-runner.py",
            "--live-kilo",
            "--json",
        ],
        timeout=540,
    )
    warnings: list[str] = []
    passed = live.returncode == 0
    detail = "Kilo live behavior trace completed"
    if live.returncode == 0:
        try:
            payload = json.loads(live.stdout)
            kilo_results = [case.get("kilo") or {} for case in payload.get("cases", [])]
            available = sum(1 for result in kilo_results if result.get("state") == "available")
            behavior_failures = sum(
                1 for case in payload.get("cases", []) if case.get("kilo_errors")
            )
            total = len(kilo_results)
            passed = total > 0 and available == total and behavior_failures == 0
            detail = (
                f"Kilo live behavior traces available for {available}/{total}; "
                f"behavior drift in {behavior_failures}/{total}"
            )
            if not passed:
                warnings.append("Kilo did not return a conforming live trace for every case")
        except json.JSONDecodeError:
            passed = False
            warnings.append("live Kilo output was not JSON")
    else:
        warnings.extend((live.stderr or live.stdout or "live Kilo trace failed").splitlines()[-4:])

    return [
        CheckResult(
            id="LV-002",
            adapter="kilo-live",
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
    parser.add_argument("--capability-preflight", action="store_true", help="validate a vendor-neutral attestation envelope from stdin only; never launch providers")
    parser.add_argument("--json", action="store_true", help="print machine-readable results")
    parser.add_argument("--live-claude", action="store_true", help="run optional live Claude CLI traces")
    parser.add_argument(
        "--require-live-claude",
        action="store_true",
        help="fail when --live-claude cannot prove every Claude live trace",
    )
    parser.add_argument(
        "--strict-project-hooks",
        action="store_true",
        help="fail instead of warn when cloned project repos lack Claude hook wiring",
    )
    parser.add_argument(
        "--installed-kilo",
        action="store_true",
        help="check this machine's installed Kilo adapter and GLM/Vision wiring",
    )
    parser.add_argument(
        "--require-installed-kilo",
        action="store_true",
        help="fail when this machine's installed Kilo adapter is not ready",
    )
    parser.add_argument(
        "--live-kilo", action="store_true", help="run optional live Kilo/GLM traces"
    )
    parser.add_argument(
        "--require-live-kilo",
        action="store_true",
        help="fail when live Kilo traces are unavailable or behaviorally different",
    )
    args = parser.parse_args()

    if args.capability_preflight:
        # This branch deliberately precedes every installed/config/hook check.
        # No provider calls, credential/config discovery, or external subprocess.
        from agent_os_adapter_contract import evaluate_capabilities
        if args.live_claude or args.require_live_claude or args.strict_project_hooks:
            print(json.dumps({"ready": False, "reasons": ["incompatible_modes"], "live_parity_proven": False, "execution_authorized": False}))
            return 2
        try:
            raw = sys.stdin.read(65537)
            if len(raw) > 65536:
                raise ValueError("input_too_large")
            def unique_keys(pairs):
                value = {}
                for key, item in pairs:
                    if key in value:
                        raise ValueError("duplicate_key")
                    value[key] = item
                return value
            envelope = json.loads(raw, object_pairs_hook=unique_keys)
            if not isinstance(envelope, dict) or set(envelope) != {"record", "required", "expected_identity"}:
                raise ValueError("invalid_envelope")
            result = evaluate_capabilities(envelope["record"], envelope["required"], expected_identity=envelope["expected_identity"])
        except (ValueError, TypeError, RecursionError):
            print(json.dumps({"ready": False, "reasons": ["invalid_input"], "live_parity_proven": False, "execution_authorized": False}))
            return 2
        print(json.dumps(result))
        return 0 if result["ready"] else 1

    results: list[CheckResult] = []
    results.extend(check_shared_core())
    results.extend(check_codex_adapter())
    results.extend(check_claude_adapter(strict_project_hooks=args.strict_project_hooks))
    results.extend(check_claude_installed_adapter())
    results.extend(check_claude_installed_adapter_self_test())
    results.extend(
        check_kilo_adapter(
            check_installed=(
                args.installed_kilo
                or args.require_installed_kilo
                or args.live_kilo
                or args.require_live_kilo
            ),
            require_installed=args.require_installed_kilo,
        )
    )
    if args.live_claude or args.require_live_claude:
        results.extend(check_optional_live_claude(require_live=args.require_live_claude))
    if args.live_kilo or args.require_live_kilo:
        results.extend(check_optional_live_kilo(require_live=args.require_live_kilo))
    return summarize(results, args.json)


if __name__ == "__main__":
    raise SystemExit(main())
