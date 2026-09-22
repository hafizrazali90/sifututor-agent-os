#!/usr/bin/env python3
"""Parity harness over the LIVE Sifututor hooks (issue #161, PR #175).

This file owns no policy. Every accept/deny rule lives in the live script the
harness invokes, by its real path, as a subprocess with a fixture payload on
stdin, exactly as the hook runner would. The harness only:

- records the documented outcome for each fixture command (see FIXTURES);
- runs the live script and reads the decision back;
- computes md5 drift between the umbrella copy of a shared hook and each
  sub-project's copy, and REPORTS it (reconvergence is issue #176).

Run directly for a human-readable report:

    python3 scripts/agent-checks/hook-policy/parity_harness.py

Set SIFUTUTOR_WORKSPACE_ROOT when running from a worktree whose root does not
contain the sub-project checkouts (the default is this repo's root).
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

# The authoritative implementation for each policy. Nothing else in this
# directory encodes a rule.
CLAUDE_BRANCH_HOOK = ROOT / ".claude" / "hooks" / "validate-branch-name.py"
CLAUDE_COMMIT_HOOK = ROOT / ".claude" / "hooks" / "conventional-commits.py"
CODEX_GUARD = ROOT / "scripts" / "agent-checks" / "codex-pre-tool-use.py"

# Shared hooks that sub-projects carry their own copy of today.
DRIFT_TRACKED_HOOKS = ("validate-branch-name.py", "conventional-commits.py")

ALLOW = "allow"
DENY = "deny"


@dataclass(frozen=True)
class Fixture:
    command: str
    expected: str  # ALLOW or DENY, per the live script's documented rule
    note: str = ""


# Branch-name policy. Both the Claude hook and the Codex guard encode it, so
# the same fixtures run against both.
BRANCH_FIXTURES: tuple[Fixture, ...] = (
    Fixture("git checkout -b feat/add-login-screen", ALLOW),
    Fixture("git checkout -b fix/null-crash-on-payment", ALLOW),
    Fixture("git switch -c docs/update-readme", ALLOW),
    Fixture("git checkout -b main", ALLOW, "base branch"),
    Fixture("git checkout -b staging", ALLOW, "base branch"),
    Fixture("git checkout -b sifu-staging-2", ALLOW, "deployment branch"),
    Fixture("git checkout -b lls-prod", ALLOW, "deployment branch"),
    Fixture("git checkout -b release/2026-09", ALLOW, "release branch"),
    Fixture("git checkout -b nonsense-branch", DENY, "no type/ prefix"),
    Fixture("git checkout -b feat/UPPERCASE", DENY, "kebab-case only"),
    Fixture("git checkout -b weird_underscore_name", DENY),
    Fixture("git checkout -b bugfix/typo", DENY, "bugfix is not a valid type"),
)

# Conventional Commits policy (Claude hook only; Codex has no equivalent).
COMMIT_FIXTURES: tuple[Fixture, ...] = (
    Fixture('git commit -m "feat: add user authentication"', ALLOW),
    Fixture('git commit -m "fix(api): handle null responses"', ALLOW),
    Fixture('git commit -m "✨ feat: add user authentication"', ALLOW, "emoji prefix"),
    Fixture('git commit -m "chore(deps): bump lodash"', ALLOW),
    Fixture('git commit -m "refactor: simplify auth flow"', ALLOW),
    Fixture("git commit --amend", ALLOW, "no -m to inspect"),
    Fixture('git commit -m "bad message" --no-verify', ALLOW, "hook skips on --no-verify"),
    Fixture('git commit -m "fixed a thing"', DENY),
    Fixture('git commit -m "WIP"', DENY),
)

# Codex safety guards. No plain `git commit` fixture is included on purpose:
# the live guard would shell out to pre-commit-guard.sh against the current
# checkout, which is live git state, not policy.
CODEX_FIXTURES: tuple[Fixture, ...] = (
    Fixture("git push --no-verify", DENY),
    Fixture("git checkout -b feat/x --no-verify", DENY),
    Fixture("git reset --hard HEAD~1", DENY),
    Fixture("git reset --soft HEAD~1", ALLOW),
    Fixture("git checkout --foo", DENY, "no-space form, always caught"),
    Fixture("git checkout -- file.txt", DENY, "issue #177: the real destructive form"),
    Fixture("git checkout --", DENY, "issue #177: bare -- at end of command"),
    Fixture("git checkout -b feat/x", ALLOW, "issue #177: -b must stay allowed"),
    Fixture("rm -rf live/sifu-tutor", DENY),
    Fixture("rm -rf .workflow-rollout/ripple-suite", DENY),
    Fixture("rm -rf node_modules", ALLOW),
    Fixture("cat .env.production", DENY),
    Fixture("cat README.md", ALLOW),
    Fixture("git status", ALLOW),
    Fixture("git commit -m \"$(cat <<'EOF'\nfeat: add x\nEOF\n)\"", DENY, "HEREDOC commit"),
    Fixture("git commit -m <<EOF", DENY, "HEREDOC commit"),
    Fixture('git commit -m "bad message" --no-verify', DENY, "--no-verify is denied"),
)

# (label, script path, payload tool_name, fixtures)
SUITES: tuple[tuple[str, Path, str, tuple[Fixture, ...]], ...] = (
    ("claude:validate-branch-name", CLAUDE_BRANCH_HOOK, "Bash", BRANCH_FIXTURES),
    ("claude:conventional-commits", CLAUDE_COMMIT_HOOK, "Bash", COMMIT_FIXTURES),
    ("codex:branch-name", CODEX_GUARD, "exec", BRANCH_FIXTURES),
    ("codex:safety-guards", CODEX_GUARD, "exec", CODEX_FIXTURES),
)


@dataclass(frozen=True)
class HookRun:
    decision: str
    returncode: int
    stdout: str
    seconds: float


def run_hook(script: Path, command: str, tool_name: str = "Bash") -> HookRun:
    """Invoke one live hook with a PreToolUse payload and read its decision."""
    import time

    payload = {"tool_name": tool_name, "tool_input": {"command": command}}
    start = time.perf_counter()
    result = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    seconds = time.perf_counter() - start
    return HookRun(decision_of(result.stdout), result.returncode, result.stdout, seconds)


def decision_of(stdout: str) -> str:
    """Empty stdout means the hook allowed the call; otherwise read the JSON."""
    text = stdout.strip()
    if not text:
        return ALLOW
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return "unparseable"
    return str(data.get("hookSpecificOutput", {}).get("permissionDecision") or ALLOW)


@dataclass(frozen=True)
class Mismatch:
    suite: str
    command: str
    expected: str
    actual: str


def run_suite(label: str, script: Path, tool_name: str, fixtures: tuple[Fixture, ...]) -> list[Mismatch]:
    mismatches = []
    for fixture in fixtures:
        run = run_hook(script, fixture.command, tool_name)
        if run.decision != fixture.expected:
            mismatches.append(Mismatch(label, fixture.command, fixture.expected, run.decision))
    return mismatches


def run_all() -> list[Mismatch]:
    mismatches: list[Mismatch] = []
    for label, script, tool_name, fixtures in SUITES:
        mismatches.extend(run_suite(label, script, tool_name, fixtures))
    return mismatches


# ---------------------------------------------------------------------------
# Drift report: umbrella copy vs each sub-project copy, by md5. Report only.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DriftRow:
    project: str
    hook: str
    status: str  # identical | drifted | absent
    project_md5: str | None
    umbrella_md5: str | None


def workspace_root() -> Path:
    override = os.environ.get("SIFUTUTOR_WORKSPACE_ROOT")
    return Path(override).expanduser().resolve() if override else ROOT


def md5_of(path: Path) -> str | None:
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()
    except OSError:
        return None


def sub_projects(root: Path) -> list[Path]:
    """Directories under `root` that carry their own `.claude/hooks/`."""
    if not root.is_dir():
        return []
    found = []
    for item in sorted(root.iterdir(), key=lambda p: p.name):
        if not item.is_dir() or item.name.startswith(".") or ".archived" in item.name:
            continue
        if item.name == "live":  # read-only production snapshots, never audited
            continue
        if (item / ".claude" / "hooks").is_dir():
            found.append(item)
    return found


def drift_report(root: Path | None = None, umbrella: Path = ROOT) -> list[DriftRow]:
    root = root or workspace_root()
    rows = []
    for hook in DRIFT_TRACKED_HOOKS:
        umbrella_md5 = md5_of(umbrella / ".claude" / "hooks" / hook)
        for project in sub_projects(root):
            project_md5 = md5_of(project / ".claude" / "hooks" / hook)
            if project_md5 is None:
                status = "absent"
            elif project_md5 == umbrella_md5:
                status = "identical"
            else:
                status = "drifted"
            rows.append(DriftRow(project.name, hook, status, project_md5, umbrella_md5))
    return rows


def main() -> int:
    mismatches = run_all()
    total = sum(len(s[3]) for s in SUITES)
    print(f"parity: {total - len(mismatches)}/{total} fixtures match the live hooks")
    for m in mismatches:
        print(f"  MISMATCH {m.suite}: {m.command!r} expected {m.expected}, got {m.actual}")

    rows = drift_report()
    root = workspace_root()
    if not rows:
        print(f"drift: no sub-project .claude/hooks/ found under {root} (set SIFUTUTOR_WORKSPACE_ROOT)")
    else:
        print(f"drift (umbrella copy vs sub-project copies under {root}):")
        for row in rows:
            short = (row.project_md5 or "-")[:8]
            print(f"  {row.status:<9} {row.project:<24} {row.hook:<26} {short}")
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
