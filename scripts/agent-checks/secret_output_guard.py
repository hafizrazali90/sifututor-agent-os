#!/usr/bin/env python3
"""Block tool commands that can print complete credentials before execution.

The guard intentionally reports only a generic reason. It never reflects the
submitted command because the command itself may contain a credential.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import sys
import time
from typing import Any


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str = ""


_BLOCKS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"\bpm2\s+(?:jlist|prettylist|env|show|describe)\b", re.I),
        "Use an approved PM2 status wrapper; raw PM2 environment output is blocked.",
    ),
    (
        re.compile(r"/proc/(?:\d+|\$\{?[^/\s}]+\}?)/(?:environ|cmdline)\b", re.I),
        "Direct process environment and command-line reads are blocked.",
    ),
    (
        re.compile(r"\b(?:printenv|export\s+-p)(?:\s|[;&|'\"\)]|$)", re.I),
        "Whole-environment output is blocked; request only a non-secret status field.",
    ),
    (
        re.compile(r"\benv\s*(?:[;&|'\"\)]|$)", re.I),
        "Whole-environment output is blocked; use env only to launch a scoped command.",
    ),
    (
        re.compile(r"(?:^|[;&|]\s*)set\s*(?:[;&|]|$)", re.I),
        "Shell state output is blocked because it may contain exported credentials.",
    ),
    (
        re.compile(r"\bsystemctl\s+(?:show-environment|show\b[^;&|]*(?:--property|-p)[=\s]*Environment\b)", re.I),
        "System service environment output is blocked.",
    ),
    (
        re.compile(r"\bsystemctl\s+show\b(?![^;&|]*(?:--property|-p)(?:=|\s))", re.I),
        "Raw system service inspection is blocked; request one approved non-secret property.",
    ),
    (
        re.compile(r"\b(?:ps\s+(?:aux(?:ww)?|-[a-z]*[ef][a-z]*)|pgrep\s+-[a-z]*[af][a-z]*)\b", re.I),
        "Broad process argument output is blocked; request only PID, user, and executable fields.",
    ),
    (
        re.compile(
            r"(?:^|[;&|\n\r]\s*|['\"]\s*)(?:history|fc\s+-l)(?:\s|['\";&|]|$)|"
            r"(?:^|[/\s])\.(?:bash|zsh)_history\b",
            re.I,
        ),
        "Shell history output is blocked because commands may contain credentials.",
    ),
    (
        re.compile(
            r"(?:console\.log|print|json\.dumps|var_dump|print_r)\s*\([^)]*"
            r"(?:os\.environ|process\.env|\$_ENV|\$_SERVER)|"
            r"\b(?:node|python3?)\b[^\n;&|]*\s-[p]\s+[^\n;&|]*"
            r"(?:os\.environ|process\.env)",
            re.I,
        ),
        "Programming-language environment dumps are blocked.",
    ),
    (
        re.compile(r"\blaunchctl\s+(?:print|export|getenv)\b", re.I),
        "Raw launch service output is blocked because it may include environment values.",
    ),
    (
        re.compile(r"\bdocker\s+compose\s+config\b", re.I),
        "Rendered container configuration is blocked because interpolation may reveal credentials.",
    ),
    (
        re.compile(r"\bkubectl\s+(?:get|describe|edit)\s+secrets?\b", re.I),
        "Raw Kubernetes secret inspection is blocked.",
    ),
    (
        re.compile(r"\baws\s+secretsmanager\s+get-secret-value\b", re.I),
        "Secret-store value retrieval must use an approved non-printing wrapper.",
    ),
    (
        re.compile(r"\bgcloud\s+secrets\s+versions\s+access\b", re.I),
        "Secret-store value retrieval must use an approved non-printing wrapper.",
    ),
    (
        re.compile(r"\bvault\s+kv\s+get\b", re.I),
        "Secret-store value retrieval must use an approved non-printing wrapper.",
    ),
    (
        re.compile(r"\b(?:vercel\s+env\s+pull|heroku\s+config(?:\s|$)|doppler\s+secrets(?:\s|$))", re.I),
        "Provider environment export is blocked; use scoped owner entry or a non-printing wrapper.",
    ),
    (
        re.compile(
            r"\b(?:security\s+find-generic-password\b[^;&|]*\s-w\b|"
            r"op\s+read\s+op://|pass\s+show\b)",
            re.I,
        ),
        "Password-store value retrieval must use an owner-only or non-printing wrapper.",
    ),
    (
        re.compile(
            r"\b(?:cat|head|tail|less|more|sed|awk|grep|rg|jq|cut|tr|base64|xxd|strings|perl|python3?|node)\b"
            r"[^\n;&|]*(?:\.env(?:\b|[._-])|\.config/sifututor/[^\s'\"]*"
            r"(?:\.conf|\.env)|credentials(?:\.json)?|id_(?:rsa|ed25519))",
            re.I,
        ),
        "Direct output from a credential-bearing file is blocked; use an approved wrapper.",
    ),
    (
        re.compile(
            r"\b(?:echo|printf)\b[^\n;&|]*\$\{?[A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD|PASS|CREDENTIAL)[A-Z0-9_]*\}?",
            re.I,
        ),
        "Printing a credential-shaped environment variable is blocked.",
    ),
    (
        re.compile(r"(?:^|[;&|]\s*)(?:set\s+-x|(?:bash|sh|zsh)\s+-x)\b", re.I),
        "Shell tracing is blocked for agent commands because expanded secrets may be logged.",
    ),
    (
        re.compile(r"\bcurl\b[^\n;&|]*(?:-v\b|--verbose\b)[^\n]*(?:authorization|bearer|api[_-]?key|token|secret)", re.I),
        "Verbose authenticated HTTP output is blocked because request headers may be exposed.",
    ),
)


def _safe_inspect_formats(command: str) -> bool:
    """Accept only literal scalar status templates, never whole inspect objects.

    This is a deliberately narrow command recognizer, not a shell interpreter.
    Unknown/dynamic templates need a reviewed non-printing wrapper.
    """
    for docker in re.finditer(r"\bdocker\b([^;\n\r&|#]*)", command, re.I):
        tail = docker.group(1)
        if tail.rstrip().endswith("\\"):
            return False
        if not re.search(r"\binspect\b", tail, re.I):
            continue
        inspect = re.match(r"\s+(?:container\s+)?inspect\b(.*)", tail, re.I)
        if inspect is None:
            # Global options/unknown command forms require a reviewed wrapper.
            return False
        arguments = inspect.group(1)
        # Tokenize only this bounded simple segment. A format-looking string
        # inside one quoted positional argument is not a Docker option.
        try:
            tokens = shlex.split(arguments)
        except ValueError:
            return False
        if any(any(c in token for c in "$`<>()") for token in tokens):
            return False
        templates = []
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token == "--":
                break
            if token in {"--format", "-f"}:
                index += 1
                if index >= len(tokens):
                    return False
                templates.append(tokens[index])
            elif token.startswith("--format="):
                templates.append(token[len("--format="):])
            elif token.startswith("-f"):
                templates.append(token[2:].removeprefix("="))
            index += 1
        if not templates:
            return False
        for template in templates:
            if not template:
                return False
            if not re.fullmatch(
                r"\{\{\s*(?:json\s+)?\.(?:State\.(?:Status|Running|Restarting|Paused|Dead|ExitCode|Health\.Status)|RestartCount|Id)\s*\}\}",
                template,
            ):
                return False
    return True


def evaluate_command(command: str) -> Decision:
    """Return a safe decision without including submitted command text."""

    # Newlines delimit shell commands; flattening them lets a following command
    # lend its harmless-looking format to a preceding raw inspect command.
    compact = str(command).strip()
    if not compact:
        return Decision(True)
    if (
        re.match(r"^\s*(?:rg|grep)\b", compact, re.I)
        and not re.search(r"(?:\$|<)\(|[;&|\n\r]", compact)
        and not re.search(
            r"(?:\.env(?:\b|[._-])|\.config/sifututor/[^\s'\"]*(?:\.conf|\.env)|"
            r"credentials(?:\.json)?|id_(?:rsa|ed25519))",
            compact,
            re.I,
        )
    ):
        return Decision(True)
    if not _safe_inspect_formats(compact):
        return Decision(False, "Container inspection requires a literal approved non-secret status field; use a reviewed wrapper for other output.")
    for pattern, reason in _BLOCKS:
        if pattern.search(compact):
            return Decision(False, reason)
    return Decision(True)


def prompt_requests_secret_reveal(prompt: str) -> bool:
    """Detect requests to visually expose a complete provider credential."""

    normalized = " ".join(str(prompt).lower().split())
    reveal = re.search(
        r"\b(?:screenshot|snapshot|capture|photograph|record|dump|download|inspect|view|show|read|copy|extract)\b",
        normalized,
    )
    secret = re.search(r"\b(?:api[ _-]?key|token|credential|secret|password|private key)\b", normalized)
    surface = re.search(r"\b(?:page|dashboard|provider|console|accessibility|ax tree|developer portal)\b", normalized)
    if not (reveal and secret):
        return False
    complete = re.search(
        r"\b(?:full|complete|entire|unmasked|revealed|plain[ -]?text)\b",
        normalized,
    )
    if complete:
        return True
    if not surface:
        return False
    safe_display = re.search(
        r"\b(?:redacted|masked|hidden|concealed|last four|last 4|prefix only|not visible|no longer visible)\b",
        normalized,
    )
    return not bool(safe_display)


def prompt_clears_secret_visual_boundary(prompt: str) -> bool:
    """Recognize an explicit statement that the credential surface is closed."""

    normalized = " ".join(str(prompt).lower().split())
    if re.search(r"\b(?:do not|don't|never)\s+(?:clear|reset)\s+(?:the\s+)?visual guard\b", normalized):
        return False
    if "clear the visual guard" in normalized or "reset the visual guard" in normalized:
        return True
    secret = re.search(r"\b(?:api[ _-]?key|token|credential|secret|password|private key)\b", normalized)
    safe_state = re.search(
        r"\b(?:is|page is|screen is|now)\s+(?:closed|hidden|masked|concealed)\b|"
        r"\b(?:closed|left|exited|navigated away from)\s+(?:the\s+)?(?:provider|credential|key|secret)\b",
        normalized,
    )
    return bool(secret and safe_state)


def _visual_scope(payload: dict[str, Any]) -> str:
    for key in ("session_id", "sessionId", "conversation_id", "conversationId"):
        value = str(payload.get(key) or "").strip()
        if value:
            return f"session:{value}"
    cwd = str(payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or "").strip()
    return f"cwd:{cwd}" if cwd else ""


def _visual_state_root(state_dir: Path | None = None) -> Path:
    if state_dir is not None:
        return Path(state_dir)
    configured = os.environ.get("SIFUTUTOR_SECRET_GUARD_STATE_DIR", "").strip()
    if configured:
        return Path(configured)
    return Path.home() / ".cache" / "sifututor-agent-os" / "secret-visual-guard"


def _visual_marker(payload: dict[str, Any], state_dir: Path | None = None) -> Path | None:
    scope = _visual_scope(payload)
    if not scope:
        return None
    digest = hashlib.sha256(scope.encode("utf-8")).hexdigest()
    return _visual_state_root(state_dir) / f"{digest}.active"


def mark_secret_visual_boundary(
    payload: dict[str, Any], *, state_dir: Path | None = None, now: float | None = None
) -> bool:
    """Create a short-lived metadata-only marker for a credential reveal surface."""

    marker = _visual_marker(payload, state_dir)
    if marker is None:
        return False
    marker.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        marker.parent.chmod(0o700)
    except OSError:
        pass
    marker.write_text("active\n", encoding="utf-8")
    try:
        marker.chmod(0o600)
    except OSError:
        pass
    timestamp = time.time() if now is None else now
    os.utime(marker, (timestamp, timestamp))
    return True


def clear_secret_visual_boundary(
    payload: dict[str, Any], *, state_dir: Path | None = None
) -> None:
    marker = _visual_marker(payload, state_dir)
    if marker is not None:
        marker.unlink(missing_ok=True)


def secret_visual_boundary_active(
    payload: dict[str, Any], *, state_dir: Path | None = None, now: float | None = None
) -> bool:
    marker = _visual_marker(payload, state_dir)
    return bool(marker is not None and marker.is_file())


def sync_secret_visual_boundary(
    payload: dict[str, Any],
    prompt: str,
    *,
    state_dir: Path | None = None,
    now: float | None = None,
) -> bool:
    """Update the marker from a prompt and return the resulting active state."""

    if prompt_requests_secret_reveal(prompt):
        mark_secret_visual_boundary(payload, state_dir=state_dir, now=now)
    elif prompt_clears_secret_visual_boundary(prompt):
        clear_secret_visual_boundary(payload, state_dir=state_dir)
    return secret_visual_boundary_active(payload, state_dir=state_dir, now=now)


def _direct_patch_data(tool_name: str, tool_input: Any) -> bool:
    """Recognize inert direct editor payloads, never executable wrappers."""
    if tool_name in {"Edit", "Write", "edit", "write"}:
        return True
    if tool_name not in {"apply_patch", "functions.apply_patch"}:
        return False
    value = tool_input
    if isinstance(value, dict):
        if set(value) not in ({"input"}, {"patch"}, {"command"}):
            return False
        value = next(iter(value.values()))
    return (
        isinstance(value, str)
        and value.startswith("*** Begin Patch\n")
        and value.rstrip().endswith("\n*** End Patch")
    )


def _visual_capture_request(tool_name: str, tool_input: Any) -> bool:
    """Return True only for tools capable of capturing a visible credential."""

    normalized_name = tool_name.lower()
    if any(marker in normalized_name for marker in ("cua", "computer_use", "view_image", "screenshot")):
        return True
    if normalized_name in {"web__run", "web.run"}:
        return "screenshot" in json.dumps(tool_input).lower()
    if normalized_name in {"functions.exec", "exec", "exec_command", "bash"}:
        source = json.dumps(tool_input).lower()
        return any(marker in source for marker in (
            "cua.", "getstate", "screenshot", "screencapture", "view_image", "emitimage",
        ))
    return False


def evaluate_tool_request(
    tool_name: str,
    tool_input: Any,
    payload: dict[str, Any],
    *,
    state_dir: Path | None = None,
    now: float | None = None,
) -> Decision:
    """Block visual capture during a credential reveal, then check commands."""

    if (
        secret_visual_boundary_active(payload, state_dir=state_dir, now=now)
        and _visual_capture_request(tool_name, tool_input)
    ):
        return Decision(
            False,
            "Visual capture is blocked while a complete credential may be visible. Hide or leave the credential page before capturing it.",
        )
    # Direct editor contents are inert data, not shell invocations. Native
    # path permissions and the separate secret-artifact scan remain responsible
    # for writes. Execution wrappers retain command inspection.
    if _direct_patch_data(tool_name, tool_input):
        return Decision(True)
    for command in _collect_command_text(tool_input):
        decision = evaluate_command(command)
        if not decision.allowed:
            return decision
    return Decision(True)


def safe_command_label(command: str) -> str:
    """Return only a coarse executable label suitable for a failure log."""

    normalized = " ".join(str(command).split()).lower()
    allowed_labels = (
        "git",
        "gh",
        "rg",
        "python",
        "python3",
        "node",
        "npm",
        "pnpm",
        "yarn",
        "php",
        "composer",
        "pytest",
        "curl",
        "ssh",
        "rsync",
        "docker",
        "kubectl",
        "pm2",
        "bash",
        "sh",
        "zsh",
    )
    match = re.search(
        r"(?:^|[;&|]\s*)(?:(?:sudo|env)\s+)?(?:" +
        r"(?:[a-z_][a-z0-9_]*=[^\s]+\s+)*)([a-z0-9._/-]+)",
        normalized,
    )
    if not match:
        return "redacted"
    executable = match.group(1).rsplit("/", 1)[-1]
    return executable if executable in allowed_labels else "redacted"


def _collect_command_text(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        source = value.get("input")
        if isinstance(source, str) and "tools." in source:
            if "tools.exec_command" not in source:
                return []
            matches = re.findall(
                r"\bcmd\s*:\s*(\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`|[A-Za-z_$][A-Za-z0-9_$]*)",
                source,
                flags=re.S,
            )
            extracted: list[str] = []
            for expression in matches:
                encoded = expression
                if expression[0] not in "\"'`":
                    assignment = re.search(
                        rf"\b(?:const|let|var)\s+{re.escape(expression)}\s*=\s*"
                        r"(\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`)",
                        source,
                        flags=re.S,
                    )
                    if assignment is None:
                        return [source]
                    encoded = assignment.group(1)
                try:
                    if encoded.startswith('"'):
                        extracted.append(json.loads(encoded))
                    else:
                        extracted.append(encoded[1:-1])
                except (json.JSONDecodeError, IndexError):
                    return [source]
            if extracted:
                return extracted
            return [source]
        preferred = [
            value[key]
            for key in ("command", "cmd", "input", "source", "code")
            if key in value
        ]
        if preferred:
            parts: list[str] = []
            for item in preferred:
                parts.extend(_collect_command_text(item))
            return parts
        parts = []
        for item in value.values():
            parts.extend(_collect_command_text(item))
        return parts
    if isinstance(value, list):
        parts = []
        for item in value:
            parts.extend(_collect_command_text(item))
        return parts
    return []


def _deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, TypeError):
        return 0

    tool_name = str(payload.get("tool_name") or payload.get("toolName") or "")
    tool_input = payload.get("tool_input") or payload.get("toolInput") or {}
    decision = evaluate_tool_request(tool_name, tool_input, payload)
    if not decision.allowed:
        _deny(decision.reason)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
