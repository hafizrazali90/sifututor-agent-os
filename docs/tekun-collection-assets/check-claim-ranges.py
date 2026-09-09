#!/usr/bin/env python3
"""Validate TEKUN numeric claim ranges used by the governed sourcebook."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: check-claim-ranges.py <sourcebook.md> <claim-register.md>")
        return 2

    source_path = Path(sys.argv[1])
    register_path = Path(sys.argv[2])
    source = source_path.read_text(encoding="utf-8")
    register_lines = register_path.read_text(encoding="utf-8").splitlines()

    claims: dict[int, tuple[str, str]] = {}
    section = "unknown"
    for line in register_lines:
        heading = re.match(r"^## ([A-Z]) - ", line)
        if heading:
            section = heading.group(1)
        row = re.match(r"^\| CLM-(\d{3}) \|", line)
        if row:
            claims[int(row.group(1))] = (section, line)

    failures: list[str] = []
    checked = 0
    for match in re.finditer(r"CLM-(\d{3})[–-](\d{3})", source):
        start, end = int(match.group(1)), int(match.group(2))
        checked += 1
        if end < start:
            failures.append(f"descending range {match.group(0)}")
            continue
        resolved = list(range(start, end + 1))
        missing = [claim for claim in resolved if claim not in claims]
        if missing:
            failures.append(f"{match.group(0)} has missing claims {missing}")
            continue
        sections = {claims[claim][0] for claim in resolved}
        if len(sections) != 1:
            failures.append(
                f"{match.group(0)} crosses register sections {sorted(sections)}"
            )
        for claim in resolved:
            row = claims[claim][1].lower()
            if any(
                marker in row
                for marker in (
                    "do not use",
                    "discovery only",
                    "internal / discovery",
                    "internal; external only",
                )
            ):
                failures.append(
                    f"{match.group(0)} includes restricted CLM-{claim:03d}"
                )

    if failures:
        print("claim-range-check: FAIL")
        for failure in sorted(set(failures)):
            print(f"- {failure}")
        return 1

    print(f"claim-range-check: PASS ranges={checked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
