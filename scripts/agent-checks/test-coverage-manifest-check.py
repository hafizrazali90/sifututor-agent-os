#!/usr/bin/env python3
"""
Validate a project's TESTING.md coverage manifest.

This is intentionally conservative. It checks that test files named in the
manifest exist, and it summarizes missing/partial/covered feature rows. It does
not claim a test is meaningful; agents and reviewers must still inspect intent.
"""

from __future__ import annotations

import argparse
import glob
import re
import sys
from dataclasses import dataclass
from pathlib import Path


STATUS_MISSING = "missing"
STATUS_PARTIAL = "partial"
STATUS_COVERED = "covered"


@dataclass
class Row:
    feature: str
    status: str
    test_file_cell: str
    line_number: int


def normalize_status(cell: str) -> str:
    lowered = cell.lower()
    if "missing" in lowered or "❌" in cell:
        return STATUS_MISSING
    if "partial" in lowered or "⚠" in cell:
        return STATUS_PARTIAL
    if "covered" in lowered or "✅" in cell:
        return STATUS_COVERED
    return "unknown"


def split_markdown_row(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def parse_manifest(path: Path) -> list[Row]:
    rows: list[Row] = []
    header: list[str] | None = None

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.lstrip().startswith("|"):
            continue

        cells = split_markdown_row(line)
        lowered = [cell.lower() for cell in cells]

        if "feature" in lowered and "status" in lowered:
            header = lowered
            continue

        if header is None or all(set(cell) <= {"-", ":", " "} for cell in cells):
            continue

        try:
            feature_index = header.index("feature")
            status_index = header.index("status")
        except ValueError:
            continue

        test_index = None
        for candidate in ("test file", "test files", "test file(s)"):
            if candidate in header:
                test_index = header.index(candidate)
                break

        if test_index is None:
            continue

        if len(cells) <= max(feature_index, status_index, test_index):
            continue

        rows.append(
            Row(
                feature=cells[feature_index],
                status=normalize_status(cells[status_index]),
                test_file_cell=cells[test_index],
                line_number=line_number,
            )
        )

    return rows


def extract_paths(cell: str) -> list[str]:
    if cell.strip() in {"", "-", "—", "None", "none", "N/A", "n/a"}:
        return []

    paths = re.findall(r"`([^`]+)`", cell)
    if not paths:
        paths = re.split(r",|<br>|;", cell)

    cleaned: list[str] = []
    for raw in paths:
        value = raw.strip()
        if not value or value in {"-", "—"}:
            continue
        if value.endswith("/*") or "*" in value:
            cleaned.append(value)
            continue
        if any(value.endswith(suffix) for suffix in (".php", ".ts", ".tsx", ".js", ".jsx", ".yaml", ".yml", ".spec", ".test")):
            cleaned.append(value)

    return cleaned


def path_exists(project: Path, manifest_path: str) -> bool:
    if "*" in manifest_path:
        return bool(glob.glob(str(project / manifest_path)))

    candidate = project / manifest_path
    if candidate.exists():
        return True

    if manifest_path.endswith("/"):
        return candidate.is_dir()

    if "/" not in manifest_path:
        return any(project.rglob(manifest_path))

    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate TESTING.md test file references.")
    parser.add_argument("--project", default=".", help="Project directory containing TESTING.md")
    parser.add_argument("--strict", action="store_true", help="Fail on missing or partial feature rows")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    manifest = project / "TESTING.md"

    if not manifest.exists():
        print(f"TESTING.md not found in {project}")
        return 0

    rows = parse_manifest(manifest)
    if not rows:
        print(f"No coverage rows found in {manifest}")
        return 1

    broken_refs: list[str] = []
    counts = {STATUS_COVERED: 0, STATUS_PARTIAL: 0, STATUS_MISSING: 0, "unknown": 0}

    for row in rows:
        counts[row.status] = counts.get(row.status, 0) + 1
        if row.status == STATUS_MISSING:
            continue

        for test_path in extract_paths(row.test_file_cell):
            if not path_exists(project, test_path):
                broken_refs.append(f"line {row.line_number}: {row.feature} -> {test_path}")

    print(f"Coverage manifest: {manifest}")
    print(f"Rows: {len(rows)}")
    print(f"Covered: {counts.get(STATUS_COVERED, 0)}")
    print(f"Partial: {counts.get(STATUS_PARTIAL, 0)}")
    print(f"Missing: {counts.get(STATUS_MISSING, 0)}")

    if broken_refs:
        print("")
        print("Missing referenced test files:")
        for item in broken_refs:
            print(f"- {item}")

    if args.strict and (counts.get(STATUS_PARTIAL, 0) or counts.get(STATUS_MISSING, 0)):
        print("")
        print("--strict failed because the manifest still has partial or missing feature rows.")
        return 1

    return 1 if broken_refs else 0


if __name__ == "__main__":
    sys.exit(main())
