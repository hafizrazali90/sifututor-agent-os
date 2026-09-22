#!/usr/bin/env python3
"""Shared quality-gate policy: ADVISORY, config-driven.

ripple-suite, sifututor_tutor, and lls each ship their own
`.claude/hooks/quality-gate.py` with the same two-part shape -- "ask the
human to confirm lint/build ran when code files are staged" then "ask more
insistently when a critical path is staged" -- parameterized by different
file extensions, directories, critical paths, and lint commands (see
SURVEY.md section 3). This module is that one shape, taking the
per-project parameters as a `QualityGateConfig` instead of three separate
copies of the same control flow.

This check is ADVISORY (Severity.ADVISORY): even the real scripts never
hard-deny a commit over lint/build -- they always use `ask_user`, which a
human can accept. A dispatcher-level failure here must degrade, never
block; see check_expensive_examples.py for what "degrade" means when the
check literally cannot run.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
import subprocess

from models import Decision, HookRequest, Severity


@dataclass(frozen=True)
class QualityGateConfig:
    code_extensions: frozenset[str]
    code_dirs: tuple[str, ...]
    critical_paths: tuple[str, ...]
    lint_command: str
    label: str = "quality_gate"


RIPPLE_SUITE_CONFIG = QualityGateConfig(
    code_extensions=frozenset({".ts", ".tsx", ".js", ".jsx"}),
    code_dirs=(
        "src/", "app/", "pages/", "components/", "lib/", "hooks/", "utils/",
        "types/", "modules/",
    ),
    critical_paths=(
        "src/middleware.ts",
        "src/lib/db.ts",
        "src/lib/db-neon.ts",
        "src/lib/db-helpers.ts",
        "src/lib/migrations/",
        "src/app/api/auth/",
        "src/app/api/tutor-payments/",
        "src/modules/tutor-payments/",
        "src/modules/accounts/",
        "src/modules/reconciliation/",
        "src/lib/api-logger.ts",
    ),
    lint_command="npm run lint && npm run build",
    label="ripple-suite",
)


def git_staged_files(project_root: str) -> list[str]:
    """Real staged-file provider -- mirrors the original scripts exactly."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            cwd=project_root or None,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except Exception:
        return []


def _has_code_changes(files: list[str], config: QualityGateConfig) -> bool:
    for f in files:
        _, ext = os.path.splitext(f)
        if ext in config.code_extensions:
            for d in config.code_dirs:
                if f.startswith(d):
                    return True
    return False


def _critical_files(files: list[str], config: QualityGateConfig) -> list[str]:
    hits = []
    for f in files:
        for cp in config.critical_paths:
            if f.startswith(cp) or f == cp:
                hits.append(f)
                break
    return hits


class QualityGateCheck:
    severity = Severity.ADVISORY
    expensive = False

    def __init__(self, config: QualityGateConfig, staged_files_provider=None):
        self.config = config
        self.name = f"quality_gate:{config.label}"
        self._staged_files_provider = staged_files_provider or git_staged_files

    def applies(self, request: HookRequest) -> bool:
        return request.tool_name == "Bash" and "git commit" in request.command

    def run(self, request: HookRequest) -> Decision:
        if "--no-verify" in request.command:
            return Decision.allow(self.name)

        staged = self._staged_files_provider(request.cwd)
        if not staged:
            return Decision.allow(self.name)

        code_files = [
            f for f in staged if os.path.splitext(f)[1] in self.config.code_extensions
        ]
        if not code_files:
            return Decision.allow(self.name)

        if _has_code_changes(staged, self.config):
            listed = "\n".join(f"  - {f}" for f in code_files[:15])
            return Decision.ask_user(
                self.name,
                reason=f"{len(code_files)} code file(s) staged.",
                guidance=f"Confirm `{self.config.lint_command}` passed before "
                f"committing.\n{listed}",
            )

        critical = _critical_files(staged, self.config)
        if critical:
            listed = "\n".join(f"  - {f}" for f in critical)
            return Decision.ask_user(
                self.name,
                reason="Staged files touch critical paths.",
                guidance=f"Confirm `{self.config.lint_command}` and relevant tests "
                f"passed before committing.\n{listed}",
            )

        return Decision.allow(self.name)
