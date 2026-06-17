#!/usr/bin/env python3
"""Validate Agent OS Mission Ledger files.

The checker is intentionally lightweight. It validates structure and parent
links without trying to understand product priority.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEDGER_DIR = ROOT / "docs" / "agent-playbooks" / "mission-ledger"
ALLOWED_STATUSES = {
    "captured",
    "triaged",
    "active",
    "promoted",
    "paused",
    "done",
    "dropped",
}
ALLOWED_TYPES = {
    "mission",
    "task",
    "adjacent",
    "question",
    "risk",
    "research",
}
REQUIRED_FIELDS = [
    "Project",
    "Status",
    "Type",
    "Parent",
    "End goal",
    "Why it matters",
    "Source",
    "Next action",
    "Promote to",
    "Links",
]


@dataclass
class LedgerItem:
    item_id: str
    title: str
    path: Path
    line: int
    fields: dict[str, str]


def is_placeholder_file(text: str) -> bool:
    return "No mission-ledger items captured yet." in text


def parse_items(path: Path) -> list[LedgerItem]:
    text = path.read_text(encoding="utf-8")
    if is_placeholder_file(text):
        return []

    lines = text.splitlines()
    heading_indexes: list[tuple[int, re.Match[str]]] = []
    heading_pattern = re.compile(r"^###\s+([A-Z0-9][A-Z0-9_.-]*)\s+—\s+(.+)$")

    for index, line in enumerate(lines):
        match = heading_pattern.match(line)
        if match:
            heading_indexes.append((index, match))

    items: list[LedgerItem] = []
    for position, (start_index, match) in enumerate(heading_indexes):
        end_index = (
            heading_indexes[position + 1][0]
            if position + 1 < len(heading_indexes)
            else len(lines)
        )
        fields: dict[str, str] = {}
        field_pattern = re.compile(r"^- \*\*(.+?):\*\*\s*(.*)$")
        for line in lines[start_index + 1 : end_index]:
            field_match = field_pattern.match(line)
            if field_match:
                fields[field_match.group(1)] = field_match.group(2).strip()

        items.append(
            LedgerItem(
                item_id=match.group(1),
                title=match.group(2).strip(),
                path=path,
                line=start_index + 1,
                fields=fields,
            )
        )

    return items


def is_empty_value(value: str) -> bool:
    normalized = value.strip().lower()
    return normalized in {"", "tbd", "todo", "unknown", "<none>"}


def validate_item(item: LedgerItem, all_ids: set[str], errors: list[str]) -> None:
    label = f"{item.path.relative_to(ROOT)}:{item.line} {item.item_id}"

    for field in REQUIRED_FIELDS:
        if field not in item.fields:
            errors.append(f"{label}: missing required field '{field}'")
            continue
        if is_empty_value(item.fields[field]):
            errors.append(f"{label}: field '{field}' must not be empty")

    status = item.fields.get("Status", "")
    if status and status not in ALLOWED_STATUSES:
        errors.append(
            f"{label}: invalid Status '{status}' "
            f"(allowed: {', '.join(sorted(ALLOWED_STATUSES))})"
        )

    item_type = item.fields.get("Type", "")
    if item_type and item_type not in ALLOWED_TYPES:
        errors.append(
            f"{label}: invalid Type '{item_type}' "
            f"(allowed: {', '.join(sorted(ALLOWED_TYPES))})"
        )

    parent = item.fields.get("Parent", "")
    if parent and parent != "none" and parent not in all_ids:
        errors.append(f"{label}: Parent '{parent}' does not match any ledger item")

    if item_type and item_type != "mission" and parent == "none":
        errors.append(f"{label}: non-mission items must point to a parent mission")

    if status == "promoted":
        links = item.fields.get("Links", "").lower()
        promote_to = item.fields.get("Promote to", "").lower()
        if links in {"none", "none yet"} and promote_to in {"none", "none yet"}:
            errors.append(
                f"{label}: promoted items need a link or promotion target"
            )


def main() -> int:
    if not LEDGER_DIR.exists():
        print(f"mission-ledger: missing {LEDGER_DIR.relative_to(ROOT)}")
        return 1

    files = sorted(LEDGER_DIR.glob("*.md"))
    if not files:
        print(f"mission-ledger: no markdown files in {LEDGER_DIR.relative_to(ROOT)}")
        return 1

    items: list[LedgerItem] = []
    errors: list[str] = []
    for path in files:
        try:
            items.extend(parse_items(path))
        except UnicodeDecodeError as exc:
            errors.append(f"{path.relative_to(ROOT)}: could not decode file: {exc}")

    all_ids = {item.item_id for item in items}
    if len(all_ids) != len(items):
        seen: set[str] = set()
        for item in items:
            if item.item_id in seen:
                errors.append(
                    f"{item.path.relative_to(ROOT)}:{item.line} "
                    f"duplicate item id '{item.item_id}'"
                )
            seen.add(item.item_id)

    for item in items:
        validate_item(item, all_ids, errors)

    if errors:
        print("mission-ledger: failed")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"mission-ledger: ok ({len(items)} items)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
