#!/usr/bin/env python3
"""Deterministic structural checks for the governed TEKUN sourcebook."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def cells(line: str) -> list[str]:
    """Split a Markdown table row while preserving escaped pipe characters."""
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith(r"\|"):
        body = body[:-1]
    return [part.strip() for part in re.split(r"(?<!\\)\|", body)]


def is_separator(line: str) -> bool:
    return bool(re.fullmatch(r"\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*", line))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    args = parser.parse_args()

    text = args.source.read_text(encoding="utf-8")
    lines = text.splitlines()
    errors: list[str] = []
    table_count = 0
    row_count = 0

    index = 0
    while index + 1 < len(lines):
        if lines[index].lstrip().startswith("|") and is_separator(lines[index + 1]):
            table_count += 1
            expected = len(cells(lines[index]))
            separator_count = len(cells(lines[index + 1]))
            if separator_count != expected:
                errors.append(
                    f"line {index + 2}: separator has {separator_count} cells; expected {expected}"
                )
            cursor = index + 2
            while cursor < len(lines) and lines[cursor].lstrip().startswith("|"):
                actual = len(cells(lines[cursor]))
                row_count += 1
                if actual != expected:
                    errors.append(
                        f"line {cursor + 1}: table row has {actual} cells; expected {expected}"
                    )
                cursor += 1
            index = cursor
            continue
        index += 1

    chapters = [int(value) for value in re.findall(r"^## Chapter (\d+)\b", text, re.MULTILINE)]
    if chapters != list(range(1, 29)):
        errors.append(f"chapter sequence is {chapters}; expected 1 through 28")

    appendices = re.findall(r"^## Appendix ([A-H])\b", text, re.MULTILINE)
    if appendices != list("ABCDEFGH"):
        errors.append(f"appendix sequence is {appendices}; expected A through H")

    diagram_count = text.count("```mermaid")
    if diagram_count != 15:
        errors.append(f"Mermaid diagram count is {diagram_count}; expected 15")

    if errors:
        print("sourcebook-structure-check: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "sourcebook-structure-check: PASS "
        f"tables={table_count} rows={row_count} chapters=28 appendices=8 diagrams=15"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
