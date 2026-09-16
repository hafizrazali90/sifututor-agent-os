#!/usr/bin/env python3
"""Scan newly staged text for credential shapes without printing matches."""

from __future__ import annotations

from dataclasses import dataclass
import re
import subprocess
import sys


@dataclass(frozen=True)
class Finding:
    line: int
    rule: str


_PLACEHOLDER = re.compile(
    r"(?:<redacted>|<secret>|[:=]\s*[\"']?(?:your[_ -]|example[_ -]|dummy[_ -]|"
    r"placeholder|changeme|test[-_ ]token))",
    re.I,
)

_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private-key material", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("Anthropic/OpenAI-style token", re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{24,}\b")),
    ("Google API key", re.compile(r"\bAIza[A-Za-z0-9_-]{30,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[A-Z0-9]{16}\b")),
    ("GitHub token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("bearer credential", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}\b", re.I)),
    (
        "credential assignment",
        re.compile(
            r"\b(?:(?:[a-z0-9]+[_-])*(?:api[_-]?key|token|secret|password|"
            r"private[_-]?key|signing[_-]?key)|database[_-]?url|redis[_-]?url)"
            r"\b\s*[:=]\s*[\"']?[A-Za-z0-9._~+/@:=-]{20,}",
            re.I,
        ),
    ),
)


def find_secret_findings(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        candidate = _PLACEHOLDER.sub("<placeholder>", line)
        for rule, pattern in _RULES:
            if pattern.search(candidate):
                findings.append(Finding(line_number, rule))
    return findings


def staged_added_lines() -> list[tuple[str, int, str]]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--no-ext-diff", "--unified=0", "--no-color", "--"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("could not inspect the staged diff")

    path = "<unknown>"
    new_line = 0
    added: list[tuple[str, int, str]] = []
    for line in result.stdout.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
            continue
        hunk = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
        if hunk:
            new_line = int(hunk.group(1))
            continue
        if line.startswith("+") and not line.startswith("+++"):
            added.append((path, new_line, line[1:]))
            new_line += 1
        elif line.startswith("-") and not line.startswith("---"):
            continue
        elif new_line:
            new_line += 1
    return added


def main() -> int:
    try:
        added = staged_added_lines()
    except RuntimeError as exc:
        print(f"secret-artifact-scan: {exc}", file=sys.stderr)
        return 1

    reported: list[tuple[str, int, str]] = []
    for path, line_number, text in added:
        for finding in find_secret_findings(text):
            reported.append((path, line_number, finding.rule))

    if not reported:
        print("secret-artifact-scan: staged additions contain no recognized credential values")
        return 0

    print("secret-artifact-scan: possible credential material found; values are suppressed", file=sys.stderr)
    for path, line_number, rule in reported:
        print(f"- {path}:{line_number} ({rule})", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
