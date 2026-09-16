#!/usr/bin/env python3
"""Block tool commands that can print complete credentials before execution.

The guard intentionally reports only a generic reason. It never reflects the
submitted command because the command itself may contain a credential.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
import sys
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
        re.compile(r"\b(?:history|fc\s+-l)\b|(?:^|[/\s])\.(?:bash|zsh)_history\b", re.I),
        "Shell history output is blocked because commands may contain credentials.",
    ),
    (
        re.compile(r"\b(?:os\.environ|process\.env|\\$_ENV|\\$_SERVER)\b", re.I),
        "Programming-language environment dumps are blocked.",
    ),
    (
        re.compile(r"\blaunchctl\s+(?:print|export|getenv)\b", re.I),
        "Raw launch service output is blocked because it may include environment values.",
    ),
    (
        re.compile(r"\bdocker\s+(?:container\s+)?inspect\b(?![^;&|]*(?:--format|-f)\s)", re.I),
        "Raw container inspection is blocked; use --format for one approved non-secret field.",
    ),
    (
        re.compile(r"\bdocker\s+(?:container\s+)?inspect\b[^;&|]*(?:\.Config\.Env|json\s+\.Config\.Env)", re.I),
        "Container environment inspection is blocked.",
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


def evaluate_command(command: str) -> Decision:
    """Return a safe decision without including submitted command text."""

    compact = " ".join(str(command).split())
    if not compact:
        return Decision(True)
    if (
        re.match(r"^\s*(?:rg|grep)\b", compact, re.I)
        and not re.search(r"(?:\$|<)\(|[;&|]", compact)
        and not re.search(
            r"(?:\.env(?:\b|[._-])|\.config/sifututor/[^\s'\"]*(?:\.conf|\.env)|"
            r"credentials(?:\.json)?|id_(?:rsa|ed25519))",
            compact,
            re.I,
        )
    ):
        return Decision(True)
    for pattern, reason in _BLOCKS:
        if pattern.search(compact):
            return Decision(False, reason)
    return Decision(True)


def prompt_requests_secret_reveal(prompt: str) -> bool:
    """Detect requests to visually expose a complete provider credential."""

    normalized = " ".join(str(prompt).lower().split())
    if re.search(r"\b(?:redacted|masked|hidden|concealed|last four|last 4|prefix only)\b", normalized):
        return False
    reveal = re.search(r"\b(?:screenshot|snapshot|inspect|view|show|read|copy|extract)\b", normalized)
    secret = re.search(r"\b(?:api[ _-]?key|token|credential|secret|password|private key)\b", normalized)
    surface = re.search(r"\b(?:page|dashboard|provider|console|accessibility|ax tree|developer portal)\b", normalized)
    return bool(reveal and secret and surface)


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

    tool_input = payload.get("tool_input") or payload.get("toolInput") or {}
    for command in _collect_command_text(tool_input):
        decision = evaluate_command(command)
        if not decision.allowed:
            _deny(decision.reason)
            return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
