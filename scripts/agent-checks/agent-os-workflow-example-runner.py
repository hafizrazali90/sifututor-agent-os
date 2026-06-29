#!/usr/bin/env python3
"""Check that every Agent OS workflow section has practical examples."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / "docs" / "agent-playbooks" / "agent-os-workflows.md"

SECTION_RE = re.compile(r"^## (?P<title>[0-9][0-9A-Z]*\. .+)$", re.MULTILINE)


def iter_sections(text: str) -> list[tuple[str, str]]:
    matches = list(SECTION_RE.finditer(text))
    sections: list[tuple[str, str]] = []

    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append((match.group("title"), text[start:end]))

    return sections


def has_examples(body: str) -> bool:
    lowered = body.lower()
    return (
        "scenario examples:" in lowered
        or "scenario matrix:" in lowered
        or "\nscenario:\n" in lowered
    )


def main() -> int:
    if not WORKFLOWS.exists():
        print(f"workflow-example-runner: missing {WORKFLOWS}", file=sys.stderr)
        return 1

    text = WORKFLOWS.read_text()
    sections = iter_sections(text)
    missing = [title for title, body in sections if not has_examples(body)]

    if missing:
        print(
            f"workflow-example-runner: {len(sections) - len(missing)}/{len(sections)} "
            "sections have examples"
        )
        print("Missing examples:")
        for title in missing:
            print(f"- {title}")
        return 1

    print(f"workflow-example-runner: {len(sections)}/{len(sections)} sections have examples")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
