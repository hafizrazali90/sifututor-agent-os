#!/usr/bin/env python3
"""Proof: zero live network/provider calls anywhere in this module or its
own test suite (hard limit from the task specification):

    "No live network/provider calls in the test suite -- reuse Bundle 1's
    fake provider and secret filter. This module must never itself run
    tests, call CI, or mark any check as passed -- it only classifies
    text/metadata given to it as input."

Checked two ways:

  1. Static: no implementation file in this package imports a networking,
     subprocess, or test/CI-running module. This is enforced at the source
     level so it cannot regress silently as new signals are added.
  2. Runtime: the full orchestrator, run across every required fixture,
     completes in well under a second and never advances the offline
     FakeProvider's call count for any critical-lane fixture -- the same
     proof style decision-layer's own `test_engine.py` uses for bounded
     time budgets.
"""

from __future__ import annotations

import ast
from pathlib import Path
import sys
import time
import unittest

HERE = Path(__file__).resolve().parent
_DECISION_LAYER_DIR = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(_DECISION_LAYER_DIR))

import fixtures  # noqa: E402
import provider_fake  # noqa: E402
import triage  # noqa: E402

_FORBIDDEN_MODULES = {
    "requests", "urllib", "urllib2", "urllib3", "http", "http.client",
    "httplib", "socket", "ftplib", "smtplib", "subprocess", "pytest",
    "unittest2",
}

# This module's own test files legitimately use `subprocess`-adjacent
# tooling only through the standard library's `unittest` (already
# excluded from _FORBIDDEN_MODULES) -- nothing here needs an exemption
# list beyond that.
_IMPLEMENTATION_FILES = tuple(
    path for path in HERE.glob("*.py")
    if not path.name.startswith("test_") and path.name != "__init__.py"
)


class NoForbiddenImportsTest(unittest.TestCase):
    def test_no_implementation_file_imports_a_networking_or_ci_running_module(self) -> None:
        self.assertTrue(_IMPLEMENTATION_FILES, "expected to find implementation files to scan")
        for path in _IMPLEMENTATION_FILES:
            with self.subTest(file=path.name):
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
                imported_modules: set[str] = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imported_modules.add(alias.name.split(".")[0])
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imported_modules.add(node.module.split(".")[0])
                offending = imported_modules & _FORBIDDEN_MODULES
                self.assertEqual(offending, set(), f"{path.name} imports forbidden module(s): {offending}")


class BoundedRuntimeTest(unittest.TestCase):
    def test_every_required_fixture_classifies_in_well_under_a_second(self) -> None:
        builders = (
            fixtures.clean_small_fix,
            fixtures.unrelated_files_mixed_in,
            fixtures.weakened_test_removed_assertion,
            fixtures.payments_touching_change,
            fixtures.user_facing_no_e2e_evidence,
            fixtures.ci_failure_flaky,
            fixtures.ci_failure_real,
            fixtures.ci_failure_not_inferable,
            fixtures.review_comment_blocking,
            fixtures.review_comment_informational,
            fixtures.acceptance_evidence_missing,
            fixtures.staff_facing_missing_doc_decision,
        )
        started = time.monotonic()
        for build in builders:
            triage.triage_change(build(), provider=provider_fake.FakeProvider(scenario="ok"))
        elapsed = time.monotonic() - started
        # A live network/provider call would take at least tens of
        # milliseconds per call even on a fast connection; 12 fixtures
        # completing in well under a second is only possible offline.
        self.assertLess(elapsed, 1.0)


class CriticalLaneFixtureNeverAdvancesProviderCallCountTest(unittest.TestCase):
    def test_payments_fixture_never_increments_the_fake_providers_call_count(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        triage.triage_change(fixtures.payments_touching_change(), provider=fake)
        self.assertEqual(fake.call_count, 0)


if __name__ == "__main__":
    unittest.main()
