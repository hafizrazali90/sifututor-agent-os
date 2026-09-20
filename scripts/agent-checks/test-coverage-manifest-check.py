#!/usr/bin/env python3
"""
Validate a project's TESTING.md coverage manifest.

This is the long-standing audit entrypoint named by AGENTS.md and
docs/agent-playbooks/test-coverage.md. Its command line and summary output are
unchanged:

    python3 scripts/agent-checks/test-coverage-manifest-check.py --project <dir>
    python3 scripts/agent-checks/test-coverage-manifest-check.py --project . --strict

The rules themselves now live in `coverage_enforcement.py`, which is the single
enforcement entrypoint shared by every agent and every gate. Keeping one parser
is the point: this script used to carry its own copy, the Claude push hook
carries another, and three parsers meant three different answers to "is this
feature covered?".

What changed in behaviour, deliberately: a row that names a test which does not
exist, is empty, is comments only, or is weaker than the evidence the row claims
now fails here too, not only a missing file reference.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path


def _load_engine():
    module_path = Path(__file__).with_name("coverage_enforcement.py")
    spec = importlib.util.spec_from_file_location("coverage_enforcement", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


engine = _load_engine()


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate TESTING.md test file references.")
    parser.add_argument("--project", default=".", help="Project directory containing TESTING.md")
    parser.add_argument("--strict", action="store_true", help="Fail on missing or partial feature rows")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    manifest = project / engine.MANIFEST_NAME

    if not manifest.exists():
        print(f"{engine.MANIFEST_NAME} not found in {project}")
        return 0

    report = engine.run(project=project, mode=engine.MODE_MANIFEST)

    if report.state == engine.STATE_UNAVAILABLE:
        print(f"No coverage rows found in {manifest}")
        return 1

    counts = report.summary_counts
    print(f"Coverage manifest: {manifest}")
    print(f"Rows: {report.rows_total}")
    print(f"Covered: {counts.get(engine.STATUS_COVERED, 0)}")
    print(f"Partial: {counts.get(engine.STATUS_PARTIAL, 0)}")
    print(f"Missing: {counts.get(engine.STATUS_MISSING, 0)}")
    print(f"Not user-facing: {counts.get(engine.STATUS_NOT_USER_FACING, 0)}")
    print(f"Named exception: {counts.get(engine.STATUS_EXCEPTION, 0)}")

    if report.findings:
        print("")
        print("Coverage integrity problems:")
        for finding in report.findings:
            print(f"- line {finding.line_number}: {finding.feature} -> {finding.code}: {finding.detail}")

    if args.strict and (counts.get(engine.STATUS_PARTIAL, 0) or counts.get(engine.STATUS_MISSING, 0)):
        print("")
        print("--strict failed because the manifest still has partial or missing feature rows.")
        return 1

    return 1 if report.findings else 0


if __name__ == "__main__":
    sys.exit(main())
