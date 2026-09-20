#!/usr/bin/env python3
"""Resolve Claude project hooks for umbrella-launched sessions.

Issue 96. A Claude session started in the umbrella workspace keeps the umbrella
`CLAUDE_PROJECT_DIR` even after work moves into a sub-project worktree. The
tracked sub-project hook commands look like:

    cd "$CLAUDE_PROJECT_DIR" && python3 .claude/hooks/quality-gate.py

so they search the umbrella for a script that only exists inside the
sub-project. `python3` exits 2 for a missing file, and a PreToolUse exit 2
cancels every Bash call.

This module is the single owner of the fix. The umbrella wrappers at
`.claude/hooks/quality-gate.py` and `.claude/hooks/workflow-gate.py` are thin
shells over `dispatch()`.

Two behaviours are deliberately kept apart:

- missing infrastructure warns on stderr and exits 0, so a hook that was never
  installed here cannot block unrelated work
- a real gate that ran keeps its own stdout, stderr and exit code, so a genuine
  rejection stays a rejection

`audit_project_hook_configuration()` is the deterministic readiness side of the
same problem: it reports configured hook paths that cannot resolve for a given
launch scenario, before a session discovers it the hard way.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any, Iterable


# Wrappers carry this marker so the dispatcher can recognise a copy of itself
# anywhere on the search path and refuse to dispatch into it.
DISPATCHER_MARKER = "AGENT-OS-CLAUDE-HOOK-DISPATCHER"

REENTRY_ENV_VAR = "SIFUTUTOR_AGENT_OS_HOOK_DISPATCH"
TIMEOUT_ENV_VAR = "SIFUTUTOR_AGENT_OS_HOOK_TIMEOUT"

# Only PreToolUse can cancel a tool call. A SessionStart or Stop hook that fails
# to resolve is real drift worth reporting, but it does not block work.
BLOCKING_EVENT = "PreToolUse"

# Generous but bounded: a project hook lives at the worktree root, never dozens
# of levels above the directory Claude is working in.
MAX_ANCESTOR_DEPTH = 24

# Claude's own per-hook timeout is the real limit. This is a backstop so a hung
# gate cannot hold the wrapper open indefinitely.
DEFAULT_TIMEOUT_SECONDS = 120

HOOK_DIR_PARTS = (".claude", "hooks")

# Matches the `.claude/hooks/<script>` fragment inside a configured command.
HOOK_SCRIPT_PATTERN = re.compile(r"\.claude/hooks/([A-Za-z0-9._-]+)")

_MARKER_READ_BYTES = 8192


@dataclass(frozen=True)
class Resolution:
    """Outcome of the upward search for a real sub-project hook."""

    hook_path: Path | None = None
    project_dir: Path | None = None
    reason: str = "no-project-hook"

    @property
    def found(self) -> bool:
        return self.hook_path is not None


@dataclass(frozen=True)
class HookConfigFinding:
    """One configured hook script judged against both launch scenarios."""

    project: str
    event: str
    hook_script: str
    resolves_in_project: bool
    resolves_in_umbrella: bool
    umbrella_relative: bool

    @property
    def ok(self) -> bool:
        """True when the script resolves for both launch scenarios."""
        if not self.resolves_in_project:
            return False
        if self.umbrella_relative and not self.resolves_in_umbrella:
            return False
        return True

    @property
    def script_name(self) -> str:
        return self.hook_script.rsplit("/", 1)[-1]

    @property
    def blocks_readiness(self) -> bool:
        """True when this gap must fail readiness rather than only be reported.

        Two cases qualify: a script missing from its own project, which is
        broken under any launch; and every unresolved PreToolUse hook. Hook
        names are intentionally not allowlisted: an unknown missing gate can
        block Claude just as completely as a known one.
        """
        if not self.resolves_in_project:
            return True
        return self.event == BLOCKING_EVENT and not self.resolves_in_umbrella

    @property
    def detail(self) -> str:
        if self.ok:
            return f"{self.project} {self.hook_script} resolves for project and umbrella launches"
        if not self.resolves_in_project:
            return f"{self.project} {self.event} {self.hook_script} missing from the project itself"
        if self.blocks_readiness:
            reason = "blocks every tool call; umbrella dispatcher wrapper missing"
        elif self.event == BLOCKING_EVENT:
            reason = "blocks every tool call; outside the umbrella dispatcher's scope"
        else:
            reason = "degrades only this event"
        return (
            f"{self.project} {self.event} {self.hook_script} cannot resolve from an "
            f"umbrella-launched session ({reason})"
        )


def warn(message: str) -> None:
    """Metadata-only warning.

    Never include payload bodies, command content, or filesystem paths: a hook
    warning is surfaced to the session and paths can carry project or account
    names.
    """
    sys.stderr.write(f"[agent-os] claude hook dispatch: {message}\n")


def is_dispatcher(path: Path) -> bool:
    """True when the candidate script is a dispatcher wrapper, not a real gate."""
    try:
        with path.open("rb") as handle:
            head = handle.read(_MARKER_READ_BYTES)
    except OSError:
        return False
    return DISPATCHER_MARKER.encode() in head


def resolve_payload_cwd(payload: Any) -> Path | None:
    """Return a safe absolute directory from the hook payload, or None.

    Only an absolute path to an existing directory is accepted. A relative or
    malformed value is refused outright rather than resolved against the
    process cwd, which is what keeps a bad payload from escaping the intended
    search boundary.
    """
    if not isinstance(payload, dict):
        return None
    raw = payload.get("cwd")
    if not isinstance(raw, str) or not raw:
        return None
    candidate = Path(raw)
    if not candidate.is_absolute():
        return None
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError):
        return None
    if not resolved.is_dir():
        return None
    return resolved


def find_project_hook(
    hook_name: str,
    start: Path,
    *,
    self_path: Path | None = None,
    max_depth: int = MAX_ANCESTOR_DEPTH,
) -> Resolution:
    """Walk upward from `start` for the nearest real `.claude/hooks/<hook_name>`.

    The walk is bounded three ways: a depth limit, the filesystem root, and the
    owning repository/worktree root (a directory holding `.git`). Stopping at
    the repo root is what stops one project borrowing another project's gate.
    """
    current = start
    for _ in range(max_depth):
        candidate = current.joinpath(*HOOK_DIR_PARTS, hook_name)
        if candidate.is_file():
            resolved = candidate.resolve()
            if (self_path is None or resolved != self_path) and not is_dispatcher(resolved):
                return Resolution(hook_path=resolved, project_dir=current, reason="resolved")
        # Evaluate the repo root, then stop: the hook belongs to this project.
        if (current / ".git").exists():
            break
        parent = current.parent
        if parent == current:
            break
        current = parent
    return Resolution(reason="no-project-hook")


def _exit_code(returncode: int) -> int:
    """Normalise a child return code into a usable process exit status."""
    if returncode < 0:
        returncode = 128 + (-returncode)
    if not 0 <= returncode <= 255:
        return 1
    return returncode


def _timeout_seconds(env: dict[str, str]) -> float:
    raw = env.get(TIMEOUT_ENV_VAR)
    if not raw:
        return DEFAULT_TIMEOUT_SECONDS
    try:
        value = float(raw)
    except ValueError:
        return DEFAULT_TIMEOUT_SECONDS
    return value if value > 0 else DEFAULT_TIMEOUT_SECONDS


def dispatch(
    hook_name: str,
    *,
    self_path: Path | None = None,
    stdin_bytes: bytes | None = None,
    env: dict[str, str] | None = None,
    hook_args: list[str] | None = None,
) -> int:
    """Run the real sub-project hook for this payload and return its exit code."""
    env = dict(os.environ if env is None else env)

    active = {name for name in (env.get(REENTRY_ENV_VAR) or "").split(",") if name}
    if hook_name in active:
        warn(f"re-entry guard stopped a nested dispatch for {hook_name}")
        return 0

    if stdin_bytes is None:
        try:
            stdin_bytes = sys.stdin.buffer.read()
        except OSError:
            stdin_bytes = b""

    try:
        payload = json.loads(stdin_bytes.decode("utf-8")) if stdin_bytes.strip() else None
    except (UnicodeDecodeError, json.JSONDecodeError):
        payload = None

    start = resolve_payload_cwd(payload)
    if start is None:
        warn(f"no usable payload working directory for {hook_name}; skipped without blocking")
        return 0

    resolution = find_project_hook(hook_name, start, self_path=self_path)
    if not resolution.found:
        warn(f"no project hook named {hook_name} for this working directory; skipped without blocking")
        return 0

    hook_args = list(hook_args or [])
    suffix = resolution.hook_path.suffix.lower()
    if suffix == ".py":
        command = [sys.executable, str(resolution.hook_path), *hook_args]
    elif suffix == ".sh":
        command = ["bash", str(resolution.hook_path), *hook_args]
    elif suffix == ".ps1":
        powershell = shutil.which("powershell.exe") or shutil.which("pwsh") or shutil.which("powershell")
        if powershell is None:
            warn(f"{hook_name} requires PowerShell but no interpreter is available; reporting an error")
            return 1
        command = [
            powershell,
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(resolution.hook_path),
            *hook_args,
        ]
    else:
        warn(f"{hook_name} has an unsupported interpreter; reporting an error")
        return 1

    child_env = dict(env)
    child_env[REENTRY_ENV_VAR] = ",".join(sorted(active | {hook_name}))
    # The real gate is a project hook: it must see the project as its own root.
    child_env["CLAUDE_PROJECT_DIR"] = str(resolution.project_dir)

    try:
        # stdout/stderr are intentionally not captured: the gate writes straight
        # through to the session, so its output survives byte-for-byte.
        completed = subprocess.run(
            command,
            cwd=str(resolution.project_dir),
            input=stdin_bytes,
            env=child_env,
            timeout=_timeout_seconds(env),
            check=False,
        )
    except subprocess.TimeoutExpired:
        warn(f"{hook_name} timed out; reporting an error instead of a pass")
        return 1
    except OSError:
        warn(f"{hook_name} could not be executed; reporting an error instead of a pass")
        return 1

    return _exit_code(completed.returncode)


def wrapper_main(hook_name: str, self_file: str, hook_args: list[str] | None = None) -> int:
    """Entry point used by the thin umbrella wrappers."""
    try:
        return dispatch(hook_name, self_path=Path(self_file).resolve(), hook_args=hook_args)
    except Exception:  # noqa: BLE001 - convert crashes into a controlled hook failure
        # Only *missing* hook infrastructure is allowed to fail open. Once the
        # dispatcher itself is present, an unexpected crash means we cannot
        # honestly say that the safety gate passed.
        warn(f"{hook_name} dispatcher failed unexpectedly; reporting an error instead of a pass")
        return 1


# --- readiness / configuration validation ---------------------------------


def _iter_hook_commands(settings: dict[str, Any]) -> Iterable[tuple[str, str]]:
    hooks = settings.get("hooks")
    if not isinstance(hooks, dict):
        return
    for event, groups in hooks.items():
        if not isinstance(groups, list):
            continue
        for group in groups:
            if not isinstance(group, dict):
                continue
            for hook in group.get("hooks") or []:
                if not isinstance(hook, dict):
                    continue
                command = hook.get("command")
                if isinstance(command, str) and command:
                    yield str(event), command


def _relative_hook_scripts(command: str) -> list[str]:
    """Hook scripts in `command` whose resolution depends on the launch directory.

    A literal absolute path is exempt: it already names the file it wants. Both
    a bare `.claude/hooks/x.py` and a `$CLAUDE_PROJECT_DIR`-prefixed path depend
    on where the session was launched, so both are audited.
    """
    scripts: list[str] = []
    for raw_token in command.split():
        token = raw_token.strip("\"'")
        match = HOOK_SCRIPT_PATTERN.search(token)
        if not match:
            continue
        if token.startswith("/"):
            continue
        scripts.append(f".claude/hooks/{match.group(1)}")
    return scripts


def audit_project_hook_configuration(
    umbrella_root: Path, project: Path
) -> list[HookConfigFinding]:
    """Judge one project's Claude hook commands against both launch scenarios.

    Returns one finding per configured `.claude/hooks/<script>` reference. A
    finding fails when the script is missing from the project, or when the
    command resolves relative to `CLAUDE_PROJECT_DIR` and no umbrella-level
    script or dispatcher wrapper exists to answer an umbrella-launched session.
    """
    settings_path = project / ".claude" / "settings.json"
    try:
        settings = json.loads(settings_path.read_text())
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(settings, dict):
        return []

    findings: list[HookConfigFinding] = []
    seen: set[tuple[str, str]] = set()
    for event, command in _iter_hook_commands(settings):
        for script in _relative_hook_scripts(command):
            key = (event, script)
            if key in seen:
                continue
            seen.add(key)
            findings.append(
                HookConfigFinding(
                    project=project.name,
                    event=event,
                    hook_script=script,
                    resolves_in_project=(project / script).is_file(),
                    resolves_in_umbrella=(umbrella_root / script).is_file(),
                    umbrella_relative=True,
                )
            )
    return findings


def audit_workspace_hook_configuration(umbrella_root: Path) -> list[HookConfigFinding]:
    """Audit every sub-project in the umbrella checkout that configures hooks."""
    findings: list[HookConfigFinding] = []
    if not umbrella_root.is_dir():
        return findings
    for project in sorted(umbrella_root.iterdir(), key=lambda item: item.name):
        if not project.is_dir() or project.name.startswith("."):
            continue
        # Retired checkouts keep their old settings; they are not live adapters.
        if ".archived" in project.name:
            continue
        if not (project / ".claude" / "settings.json").is_file():
            continue
        findings.extend(audit_project_hook_configuration(umbrella_root, project))
    return findings


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Audit Claude project hook path resolution.")
    parser.add_argument(
        "--root",
        default=str(Path(__file__).resolve().parents[2]),
        help="umbrella workspace root to audit",
    )
    parser.add_argument("--json", action="store_true", help="print machine-readable findings")
    parser.add_argument("--dispatch-hook", help="dispatch one project hook instead of auditing")
    parser.add_argument("--self-path", help="wrapper path to exclude from project-hook resolution")
    parser.add_argument("hook_args", nargs="*", help="arguments forwarded to the real project hook")
    args = parser.parse_args(argv)

    if args.dispatch_hook:
        self_path = Path(args.self_path).resolve() if args.self_path else None
        return dispatch(args.dispatch_hook, self_path=self_path, hook_args=args.hook_args)

    findings = audit_workspace_hook_configuration(Path(args.root).resolve())
    blocking = [finding for finding in findings if finding.blocks_readiness]
    advisory = [
        finding for finding in findings if not finding.ok and not finding.blocks_readiness
    ]

    def as_dict(finding: HookConfigFinding) -> dict[str, Any]:
        return {
            "project": finding.project,
            "event": finding.event,
            "hook_script": finding.hook_script,
            "resolves_in_project": finding.resolves_in_project,
            "resolves_in_umbrella": finding.resolves_in_umbrella,
        }

    if args.json:
        print(
            json.dumps(
                {
                    "checked": len(findings),
                    "blocking": [as_dict(f) for f in blocking],
                    "advisory": [as_dict(f) for f in advisory],
                }
            )
        )
    else:
        for finding in findings:
            if finding.ok:
                status = "PASS"
            elif finding.blocks_readiness:
                status = "FAIL"
            else:
                status = "WARN"
            print(f"{status} {finding.detail}")
        print(
            f"claude-hook-dispatch: {len(findings) - len(blocking) - len(advisory)}"
            f"/{len(findings)} resolvable, {len(blocking)} blocking, {len(advisory)} advisory"
        )

    return 1 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
