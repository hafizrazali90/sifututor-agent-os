#!/usr/bin/env python3
"""Validate Sifututor Agent OS Session Map files."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TEMPLATE = ROOT / "docs" / "agent-playbooks" / "templates" / "session-map.md"
SESSION_FILENAME_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{6}-[a-z0-9][a-z0-9-]*\.md$")

REQUIRED_SECTIONS = [
    "Human Snapshot",
    "Mindmap",
    "Progress Board",
    "Decisions",
    "Side Paths And Return Path",
    "Agent Context",
    "Links And Evidence",
    "Reference Pack",
    "Continuation Prompt",
]

HUMAN_SNAPSHOT_FIELDS = [
    "Started because",
    "Right now",
    "What changed so far",
    "Next recommended move",
    "Decision needed from Hafiz",
]

AGENT_CONTEXT_FIELDS = [
    "Date",
    "Session ID",
    "Project",
    "Agent",
    "Repo/worktree",
    "Branch",
    "Main goal",
    "Current focus",
    "Done means",
    "Recommended stop point",
    "Approved boundary",
    "Risk lane",
    "Related sessions",
]


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def has_section(text: str, section: str) -> bool:
    return f"## {section}" in text


def has_field(text: str, field: str) -> bool:
    return f"- **{field}:**" in text


def value_for_field(text: str, field: str) -> str:
    prefix = f"- **{field}:**"
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip()
    return ""


def is_placeholder(value: str) -> bool:
    normalized = value.strip().lower()
    return (
        not normalized
        or normalized in {"none", "n/a", "tbd", "todo", "unknown"}
        or normalized.startswith("<")
    )


def progress_rows(text: str) -> list[str]:
    if "## Progress Board" not in text:
        return []
    progress = text.split("## Progress Board", 1)[1]
    if "\n## " in progress:
        progress = progress.split("\n## ", 1)[0]

    rows = []
    for line in progress.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if "---" in stripped:
            continue
        if "Item" in stripped and "Status" in stripped:
            continue
        rows.append(stripped)
    return rows


def validate(path: Path, *, allow_placeholders: bool) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    label = relative(path)

    if path != DEFAULT_TEMPLATE and not SESSION_FILENAME_PATTERN.match(path.name):
        errors.append(
            f"{label}: filename must use 'YYYY-MM-DD-HHMMSS-agent-short-topic.md'"
        )

    if not text.startswith("# Session Map:"):
        errors.append(f"{label}: title must start with '# Session Map:'")

    for section in REQUIRED_SECTIONS:
        if not has_section(text, section):
            errors.append(f"{label}: missing section '## {section}'")

    for field in HUMAN_SNAPSHOT_FIELDS:
        if not has_field(text, field):
            errors.append(f"{label}: missing Human Snapshot field '{field}'")
            continue
        if not allow_placeholders and is_placeholder(value_for_field(text, field)):
            errors.append(f"{label}: Human Snapshot field '{field}' is still placeholder")

    for field in AGENT_CONTEXT_FIELDS:
        if not has_field(text, field):
            errors.append(f"{label}: missing Agent Context field '{field}'")
            continue
        if not allow_placeholders and is_placeholder(value_for_field(text, field)):
            errors.append(f"{label}: Agent Context field '{field}' is still placeholder")

    if path != DEFAULT_TEMPLATE and has_field(text, "Session ID"):
        session_id = value_for_field(text, "Session ID")
        expected = path.stem
        if session_id != expected:
            errors.append(f"{label}: Session ID must match filename stem '{expected}'")

    rows = progress_rows(text)
    if not rows:
        errors.append(f"{label}: Progress Board needs at least one item row")
    elif not allow_placeholders and any("<" in row and ">" in row for row in rows):
        errors.append(f"{label}: Progress Board still contains placeholder row")

    if "```text" not in text or "Continue from " not in text:
        errors.append(f"{label}: Continuation Prompt must include a text block starting with 'Continue from'")

    return errors


def discover_paths(args: argparse.Namespace) -> list[Path]:
    if args.paths:
        return [Path(raw).resolve() for raw in args.paths]

    paths = [DEFAULT_TEMPLATE]
    session_dir = ROOT / ".agent-os" / "session-maps"
    if session_dir.exists():
        paths.extend(sorted(session_dir.glob("*.md")))
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Session Map Markdown files.")
    parser.add_argument("paths", nargs="*", help="Specific session map files to validate")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="fail on placeholder values; intended for active session maps, not templates",
    )
    args = parser.parse_args()

    paths = discover_paths(args)
    if not paths:
        print("session-map-check: no files to validate")
        return 1

    errors: list[str] = []
    checked = 0
    for path in paths:
        if not path.exists():
            errors.append(f"{relative(path)}: file missing")
            continue
        allow_placeholders = not args.strict or path == DEFAULT_TEMPLATE
        errors.extend(validate(path, allow_placeholders=allow_placeholders))
        checked += 1

    if errors:
        for error in errors:
            print(f"FAIL {error}")
        print(f"session-map-check: {len(errors)} issue(s) across {checked} file(s)")
        return 1

    print(f"session-map-check: {checked}/{checked} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
