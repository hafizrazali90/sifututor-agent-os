#!/usr/bin/env python3
"""Regression fixtures for shared test-coverage enforcement (issue 2, CP-11).

Positive controls: an honest manifest passes every mode.
Negative controls: each way a manifest can lie, or a release can skip proof,
makes the matching mode fail.

The fixtures are deterministic. They build throwaway projects on disk, so no
product repository, network, or framework install is required.
"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("coverage_enforcement.py")


def load_module():
    spec = importlib.util.spec_from_file_location("coverage_enforcement", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


HEADER = "| Feature | Test Type | Status | Test File | Notes |\n|---|---|---|---|---|\n"

PHP_TEST = """<?php

class LoginTest extends TestCase
{
    public function test_staff_can_log_in(): void
    {
        $this->post('/login')->assertRedirect('/dashboard');
    }
}
"""

E2E_TEST = """import { test, expect } from '@playwright/test';

test('staff can log in', async ({ page }) => {
  await page.goto('/login');
  await expect(page.locator('h1')).toHaveText('Dashboard');
});
"""

DART_TEST = """import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('tutor sees schedule', (tester) async {
    expect(find.text('Schedule'), findsOneWidget);
  });
}
"""

COMMENT_ONLY_TEST = """<?php
// TODO: write the real login regression here.
// It should assert the redirect to /dashboard.
/*
 * Placeholder only.
 */
"""


class ProjectFixture:
    """A throwaway project directory with a TESTING.md and real test files."""

    def __init__(self, root: Path):
        self.root = root

    def write(self, relative: str, content: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def manifest(self, *rows: str, header: str = HEADER) -> Path:
        body = "# Testing Manifest\n\n" + header + "".join(row.rstrip("\n") + "\n" for row in rows)
        return self.write("TESTING.md", body)

    def git_init(self) -> None:
        env = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "PATH": "/usr/bin:/bin:/usr/local/bin"}
        for args in (
            ["git", "init", "-q", "-b", "main"],
            ["git", "config", "user.email", "fixture@example.invalid"],
            ["git", "config", "user.name", "Fixture"],
            ["git", "add", "-A"],
            ["git", "commit", "-qm", "base"],
        ):
            subprocess.run(args, cwd=self.root, check=True, env=env, capture_output=True)

    def stage(self, *relative: str) -> None:
        env = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "PATH": "/usr/bin:/bin:/usr/local/bin"}
        subprocess.run(["git", "add", "--", *relative], cwd=self.root, check=True, env=env, capture_output=True)


class EnforcementTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.project = ProjectFixture(self.tmp)

    def codes(self, report) -> list[str]:
        return sorted(finding.code for finding in report.findings)

    def run_mode(self, mode: str, changed_files=None):
        return MODULE.run(
            project=self.tmp,
            mode=mode,
            changed_files=changed_files,
            previous_manifest_text=None,
        )


class CoveredRows(EnforcementTestCase):
    def test_covered_row_with_real_journey_test_passes_every_mode(self):
        self.project.write("tests/e2e/auth/login.spec.ts", E2E_TEST)
        self.project.manifest(
            "| Staff login | browser E2E | ✅ Covered | `tests/e2e/auth/login.spec.ts` | Playwright journey proves redirect |"
        )
        for mode in (MODULE.MODE_MANIFEST, MODULE.MODE_CHANGE, MODULE.MODE_RELEASE):
            report = self.run_mode(mode, changed_files=["TESTING.md"])
            self.assertTrue(report.ok, f"{mode} findings: {self.codes(report)}")
            self.assertEqual(report.state, MODULE.STATE_OK)

    def test_covered_row_with_empty_test_cell_fails(self):
        self.project.manifest("| Staff login | browser E2E | ✅ Covered | — | Nothing named here |")
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_DECLARED_WITHOUT_PATH, self.codes(report))

    def test_covered_row_naming_a_nonexistent_file_fails(self):
        self.project.manifest(
            "| Staff login | browser E2E | ✅ Covered | `tests/e2e/auth/login.spec.ts` | File was never written |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_MISSING_TEST_FILE, self.codes(report))

    def test_covered_row_naming_a_comment_only_file_fails(self):
        self.project.write("tests/Feature/LoginTest.php", COMMENT_ONLY_TEST)
        self.project.manifest(
            "| Staff login | feature | ✅ Covered | `tests/Feature/LoginTest.php` | Looks covered, asserts nothing |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_EMPTY_OR_COMMENT_ONLY, self.codes(report))

    def test_covered_row_naming_a_directory_instead_of_a_test_fails(self):
        (self.tmp / "tests" / "Feature").mkdir(parents=True)
        self.project.manifest(
            "| Staff login | feature | ✅ Covered | `tests/Feature/` | Directory is not proof of a test |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_EMPTY_OR_COMMENT_ONLY, self.codes(report))

    def test_evidence_weaker_than_declared_type_fails(self):
        self.project.write("tests/Unit/LoginRuleTest.php", PHP_TEST)
        self.project.manifest(
            "| Staff login | browser E2E | ✅ Covered | `tests/Unit/LoginRuleTest.php` | Unit test sold as a journey |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_EVIDENCE_WEAKER_THAN_DECLARED, self.codes(report))


class FrameworkAgnostic(EnforcementTestCase):
    def test_non_javascript_non_php_test_paths_are_validated_not_skipped(self):
        self.project.manifest(
            "| Tutor schedule | widget | ✅ Covered | `test/schedule_test.dart` | Flutter widget test never written |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok, "a missing .dart test must not pass silently")
        self.assertIn(MODULE.CODE_MISSING_TEST_FILE, self.codes(report))

    def test_real_flutter_test_passes(self):
        self.project.write("test/schedule_test.dart", DART_TEST)
        self.project.manifest(
            "| Tutor schedule | widget | ✅ Covered | `test/schedule_test.dart` | Real Flutter widget test |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertTrue(report.ok, self.codes(report))

    def test_maestro_flow_counts_as_a_journey(self):
        self.project.write(
            "e2e/flows/login.yaml",
            "appId: my.tutor.app\n---\n- launchApp\n- tapOn: 'Log in'\n- assertVisible: 'Schedule'\n",
        )
        self.project.manifest(
            "| Tutor login | mobile E2E | ✅ Covered | `e2e/flows/login.yaml` | Maestro journey |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertTrue(report.ok, self.codes(report))


class PartialRows(EnforcementTestCase):
    def test_partial_row_with_real_test_and_named_gap_passes_change_mode(self):
        self.project.write("tests/Feature/LoginTest.php", PHP_TEST)
        self.project.manifest(
            "| Staff login | feature | ⚠️ Partial | `tests/Feature/LoginTest.php` | Missing: lockout after five failures |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertTrue(report.ok, self.codes(report))

    def test_partial_row_without_a_named_gap_fails(self):
        self.project.write("tests/Feature/LoginTest.php", PHP_TEST)
        self.project.manifest(
            "| Staff login | feature | ⚠️ Partial | `tests/Feature/LoginTest.php` |  |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_PARTIAL_WITHOUT_GAP, self.codes(report))

    def test_partial_row_blocks_release(self):
        self.project.write("tests/Feature/LoginTest.php", PHP_TEST)
        self.project.manifest(
            "| Staff login | feature | ⚠️ Partial | `tests/Feature/LoginTest.php` | Missing: lockout after five failures |"
        )
        report = self.run_mode(MODULE.MODE_RELEASE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_RELEASE_WITHOUT_PROOF, self.codes(report))


class MissingRows(EnforcementTestCase):
    def test_missing_row_is_reported_but_does_not_block_a_change(self):
        self.project.manifest("| Staff login | none | ❌ Missing | — | Zero coverage |")
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertTrue(report.ok, self.codes(report))
        self.assertIn("missing", report.summary_counts)
        self.assertEqual(report.summary_counts["missing"], 1)

    def test_missing_row_blocks_release(self):
        self.project.manifest("| Staff login | none | ❌ Missing | — | Zero coverage |")
        report = self.run_mode(MODULE.MODE_RELEASE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_RELEASE_WITHOUT_PROOF, self.codes(report))


class NotUserFacingRows(EnforcementTestCase):
    def test_not_user_facing_row_with_a_stated_reason_passes_release(self):
        self.project.manifest(
            "| Internal cache warmer | none | Not user-facing | — | Not user-facing: background command with no UI, API, or mobile surface |"
        )
        report = self.run_mode(MODULE.MODE_RELEASE, changed_files=["TESTING.md"])
        self.assertTrue(report.ok, self.codes(report))

    def test_not_user_facing_row_without_a_reason_fails(self):
        self.project.manifest("| Internal cache warmer | none | Not user-facing | — |  |")
        report = self.run_mode(MODULE.MODE_RELEASE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_UNJUSTIFIED_NOT_USER_FACING, self.codes(report))

    def test_not_user_facing_cannot_be_claimed_for_a_named_human_role(self):
        header = "| Feature | User Role | Test Type | Status | Test File | Notes |\n|---|---|---|---|---|---|\n"
        self.project.manifest(
            "| Parent invoice download | parent | none | Not user-facing | — | Not user-facing: internal only |",
            header=header,
        )
        report = self.run_mode(MODULE.MODE_RELEASE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_UNJUSTIFIED_NOT_USER_FACING, self.codes(report))


class NamedExceptionRows(EnforcementTestCase):
    def test_allowed_named_exception_passes_release(self):
        self.project.write("tests/Feature/PayoutTest.php", PHP_TEST)
        self.project.manifest(
            "| Bank payout release | feature | Exception | `tests/Feature/PayoutTest.php` | "
            "E2E exception, reason: destructive workflow, approved by Hafiz on 2026-09-20 |"
        )
        report = self.run_mode(MODULE.MODE_RELEASE, changed_files=["TESTING.md"])
        self.assertTrue(report.ok, self.codes(report))

    def test_exception_without_an_approver_fails(self):
        self.project.write("tests/Feature/PayoutTest.php", PHP_TEST)
        self.project.manifest(
            "| Bank payout release | feature | Exception | `tests/Feature/PayoutTest.php` | "
            "E2E exception, reason: destructive workflow |"
        )
        report = self.run_mode(MODULE.MODE_RELEASE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_EXCEPTION_WITHOUT_APPROVAL, self.codes(report))

    def test_exception_with_an_unlisted_reason_fails(self):
        self.project.write("tests/Feature/PayoutTest.php", PHP_TEST)
        self.project.manifest(
            "| Bank payout release | feature | Exception | `tests/Feature/PayoutTest.php` | "
            "E2E exception, reason: we ran out of time, approved by Hafiz |"
        )
        report = self.run_mode(MODULE.MODE_RELEASE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_EXCEPTION_WITHOUT_APPROVAL, self.codes(report))

    def test_exception_still_has_to_name_a_real_test_when_it_names_one(self):
        self.project.manifest(
            "| Bank payout release | feature | Exception | `tests/Feature/PayoutTest.php` | "
            "E2E exception, reason: destructive workflow, approved by Hafiz |"
        )
        report = self.run_mode(MODULE.MODE_RELEASE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_MISSING_TEST_FILE, self.codes(report))


class ChangeScoping(EnforcementTestCase):
    def test_untouched_pre_existing_debt_does_not_block_an_unrelated_change(self):
        self.project.write("tests/e2e/auth/login.spec.ts", E2E_TEST)
        self.project.manifest(
            "| Staff login | browser E2E | ✅ Covered | `tests/e2e/auth/login.spec.ts` | Real journey |",
            "| Legacy report | feature | ✅ Covered | `tests/Feature/LegacyReportTest.php` | Pre-existing broken reference |",
        )
        report = MODULE.run(
            project=self.tmp,
            mode=MODULE.MODE_CHANGE,
            changed_files=["tests/e2e/auth/login.spec.ts"],
            previous_manifest_text=(self.tmp / "TESTING.md").read_text(encoding="utf-8"),
        )
        self.assertTrue(report.ok, self.codes(report))
        self.assertEqual(report.rows_in_scope, 1)

    def test_a_newly_added_dishonest_row_is_in_scope(self):
        self.project.write("tests/e2e/auth/login.spec.ts", E2E_TEST)
        previous = (
            "# Testing Manifest\n\n"
            + HEADER
            + "| Staff login | browser E2E | ✅ Covered | `tests/e2e/auth/login.spec.ts` | Real journey |\n"
        )
        self.project.manifest(
            "| Staff login | browser E2E | ✅ Covered | `tests/e2e/auth/login.spec.ts` | Real journey |",
            "| Payout run | browser E2E | ✅ Covered | `tests/e2e/payouts/run.spec.ts` | Added in this change, file absent |",
        )
        report = MODULE.run(
            project=self.tmp,
            mode=MODULE.MODE_CHANGE,
            changed_files=["TESTING.md"],
            previous_manifest_text=previous,
        )
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_MISSING_TEST_FILE, self.codes(report))
        self.assertEqual(report.rows_in_scope, 1)

    def test_downgrading_a_row_to_missing_in_the_same_change_is_in_scope(self):
        previous = (
            "# Testing Manifest\n\n"
            + HEADER
            + "| Payout run | browser E2E | ✅ Covered | `tests/e2e/payouts/run.spec.ts` | Real journey |\n"
        )
        self.project.manifest("| Payout run | none | ❌ Missing | — | Deleted the journey |")
        report = MODULE.run(
            project=self.tmp,
            mode=MODULE.MODE_CHANGE,
            changed_files=["TESTING.md"],
            previous_manifest_text=previous,
        )
        self.assertEqual(report.rows_in_scope, 1)
        self.assertTrue(report.ok, self.codes(report))

    def test_deleting_a_declared_test_file_is_in_scope_and_fails(self):
        self.project.manifest(
            "| Staff login | browser E2E | ✅ Covered | `tests/e2e/auth/login.spec.ts` | Journey file deleted by this change |"
        )
        report = MODULE.run(
            project=self.tmp,
            mode=MODULE.MODE_CHANGE,
            changed_files=["tests/e2e/auth/login.spec.ts"],
            previous_manifest_text=(self.tmp / "TESTING.md").read_text(encoding="utf-8"),
        )
        self.assertEqual(report.rows_in_scope, 1)
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_MISSING_TEST_FILE, self.codes(report))


class UnavailableState(EnforcementTestCase):
    def test_no_manifest_is_reported_as_unavailable_and_does_not_block_a_change(self):
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["src/app.ts"])
        self.assertEqual(report.state, MODULE.STATE_UNAVAILABLE)
        self.assertTrue(report.ok)
        self.assertTrue(any("TESTING.md" in note for note in report.notes))

    def test_no_manifest_blocks_a_release(self):
        report = self.run_mode(MODULE.MODE_RELEASE, changed_files=["src/app.ts"])
        self.assertEqual(report.state, MODULE.STATE_UNAVAILABLE)
        self.assertFalse(report.ok)

    def test_manifest_without_a_parseable_table_is_unavailable_not_silently_ok(self):
        self.project.write("TESTING.md", "# Testing Manifest\n\nWe will add the table later.\n")
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertEqual(report.state, MODULE.STATE_UNAVAILABLE)
        self.assertFalse(report.ok, "a manifest that was changed but has no rows is a real gap")


class CliContract(EnforcementTestCase):
    def run_cli(self, *args: str):
        return subprocess.run(
            [sys.executable, str(MODULE_PATH), "--project", str(self.tmp), *args],
            capture_output=True,
            text=True,
        )

    def test_cli_exits_zero_and_says_pass_for_an_honest_manifest(self):
        self.project.write("tests/e2e/auth/login.spec.ts", E2E_TEST)
        self.project.manifest(
            "| Staff login | browser E2E | ✅ Covered | `tests/e2e/auth/login.spec.ts` | Real journey |"
        )
        result = self.run_cli("--mode", "manifest")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("TEST COVERAGE ENFORCEMENT: PASS", result.stdout)

    def test_cli_exits_one_and_says_fail_for_a_dishonest_manifest(self):
        self.project.manifest(
            "| Staff login | browser E2E | ✅ Covered | `tests/e2e/auth/login.spec.ts` | File absent |"
        )
        result = self.run_cli("--mode", "manifest")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("TEST COVERAGE ENFORCEMENT: FAIL", result.stdout)
        self.assertIn(MODULE.CODE_MISSING_TEST_FILE, result.stdout)

    def test_cli_change_mode_without_a_change_source_is_a_usage_error(self):
        result = self.run_cli("--mode", "change")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_cli_staged_mode_reads_the_git_index(self):
        self.project.write("tests/e2e/auth/login.spec.ts", E2E_TEST)
        self.project.manifest(
            "| Staff login | browser E2E | ✅ Covered | `tests/e2e/auth/login.spec.ts` | Real journey |"
        )
        self.project.git_init()
        manifest = self.tmp / "TESTING.md"
        manifest.write_text(
            manifest.read_text(encoding="utf-8")
            + "| Payout run | browser E2E | ✅ Covered | `tests/e2e/payouts/run.spec.ts` | Never written |\n",
            encoding="utf-8",
        )
        self.project.stage("TESTING.md")
        result = self.run_cli("--mode", "change", "--staged")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(MODULE.CODE_MISSING_TEST_FILE, result.stdout)

    def test_cli_outside_a_git_repository_reports_unavailable_without_blocking(self):
        self.project.write("tests/e2e/auth/login.spec.ts", E2E_TEST)
        self.project.manifest(
            "| Staff login | browser E2E | ✅ Covered | `tests/e2e/auth/login.spec.ts` | Real journey |"
        )
        result = self.run_cli("--mode", "change", "--staged")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("UNAVAILABLE", result.stdout)

    def test_cli_json_output_is_machine_readable(self):
        import json

        self.project.manifest(
            "| Staff login | browser E2E | ✅ Covered | `tests/e2e/auth/login.spec.ts` | File absent |"
        )
        result = self.run_cli("--mode", "manifest", "--json")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["mode"], "manifest")
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["findings"][0]["code"], MODULE.CODE_MISSING_TEST_FILE)


class SharedParser(EnforcementTestCase):
    def test_real_world_manifest_headers_are_all_parsed(self):
        header = (
            "| Feature | Area | User Role | Test Type | Status | Test File(s) | Human Journey and Notes |\n"
            "|---|---|---|---|---|---|---|\n"
        )
        self.project.write("tests/e2e/auth/login.spec.ts", E2E_TEST)
        self.project.manifest(
            "| Staff login | auth | staff | feature, browser E2E | ✅ Covered | `tests/e2e/auth/login.spec.ts` | Real journey |",
            header=header,
        )
        rows = MODULE.parse_manifest((self.tmp / "TESTING.md").read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].status, MODULE.STATUS_COVERED)
        self.assertEqual(rows[0].test_paths, ["tests/e2e/auth/login.spec.ts"])
        self.assertEqual(rows[0].required_level, MODULE.LEVEL_JOURNEY)

    def test_test_type_column_is_not_mistaken_for_the_test_file_column(self):
        rows = MODULE.parse_manifest(
            "# M\n\n" + HEADER + "| Staff login | browser E2E | ✅ Covered | `tests/e2e/a.spec.ts` | note |\n"
        )
        self.assertEqual(rows[0].test_paths, ["tests/e2e/a.spec.ts"])

    def test_legacy_manifest_checker_shares_this_parser(self):
        legacy = Path(__file__).with_name("test-coverage-manifest-check.py")
        source = legacy.read_text(encoding="utf-8")
        self.assertIn("coverage_enforcement", source)


class BareFilenameResolution(EnforcementTestCase):
    """`lls` names some tests by bare filename. That must resolve, but only
    inside the project's own tree."""

    def test_bare_filename_resolves_inside_the_project(self):
        self.project.write("tests/Feature/Xp/StreakMilestoneBadgeTest.php", PHP_TEST)
        self.project.manifest(
            "| Streak badges | feature | ✅ Covered | `StreakMilestoneBadgeTest.php` | Named by filename only |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertTrue(report.ok, self.codes(report))

    def test_bare_filename_found_only_in_vendor_does_not_count(self):
        self.project.write("vendor/acme/tests/StreakMilestoneBadgeTest.php", PHP_TEST)
        self.project.manifest(
            "| Streak badges | feature | ✅ Covered | `StreakMilestoneBadgeTest.php` | Third-party file, not our proof |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_MISSING_TEST_FILE, self.codes(report))

    def test_bare_filename_found_only_in_a_nested_worktree_does_not_count(self):
        self.project.write(".worktrees/other/tests/Feature/Xp/StreakMilestoneBadgeTest.php", PHP_TEST)
        self.project.manifest(
            "| Streak badges | feature | ✅ Covered | `StreakMilestoneBadgeTest.php` | Another branch's copy |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_MISSING_TEST_FILE, self.codes(report))


class AdversarialBypasses(EnforcementTestCase):
    """Each of these is a way an agent could make a row look covered cheaply."""

    def test_a_backticked_prose_sentence_is_not_a_test_path(self):
        self.project.manifest(
            "| Staff login | feature | ✅ Covered | `covered by the existing suite` | Prose dressed as a path |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_DECLARED_WITHOUT_PATH, self.codes(report))

    def test_a_glob_matching_nothing_fails(self):
        self.project.manifest(
            "| Staff login | browser E2E | ✅ Covered | `tests/e2e/**/*.spec.ts` | Glob matches no file |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_MISSING_TEST_FILE, self.codes(report))

    def test_a_glob_matching_only_empty_files_fails(self):
        self.project.write("tests/e2e/auth/login.spec.ts", "\n\n// nothing here yet\n")
        self.project.manifest(
            "| Staff login | browser E2E | ✅ Covered | `tests/e2e/**/*.spec.ts` | Glob matches a stub |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_EMPTY_OR_COMMENT_ONLY, self.codes(report))

    def test_a_url_is_not_evidence(self):
        self.project.manifest(
            "| Staff login | feature | ✅ Covered | `https://github.com/Sifututor/x/pull/1` | Link, not a test |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_DECLARED_WITHOUT_PATH, self.codes(report))

    def test_pointing_at_the_manifest_itself_is_not_a_test(self):
        self.project.manifest(
            "| Staff login | feature | ✅ Covered | `TESTING.md` | The manifest is not the test |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_EMPTY_OR_COMMENT_ONLY, self.codes(report))

    def test_an_unreadable_status_is_blocked_in_every_mode(self):
        """A status no gate can read is not a claim. This slipped through the
        change gate until a CI dry run on a real manifest exposed it."""
        self.project.write("tests/e2e/auth/login.spec.ts", E2E_TEST)
        self.project.manifest(
            "| Staff login | browser E2E | in progress | `tests/e2e/auth/login.spec.ts` | Status says nothing |"
        )
        for mode in (MODULE.MODE_MANIFEST, MODULE.MODE_CHANGE, MODULE.MODE_RELEASE):
            report = self.run_mode(mode, changed_files=["TESTING.md"])
            self.assertFalse(report.ok, mode)
            self.assertIn(MODULE.CODE_UNREADABLE_STATUS, self.codes(report))

    def test_a_row_with_the_wrong_column_count_cannot_read_as_covered(self):
        """Inserting a five-column row into a seven-column table shifts every
        cell. The claim must fail, not land on a cell that happens to parse."""
        header = (
            "| Feature | Area | User Role | Test Type | Status | Test File(s) | Notes |\n"
            "|---|---|---|---|---|---|---|\n"
        )
        self.project.manifest(
            "| Payout release | browser E2E | ✅ Covered | `tests/e2e/payouts/run.spec.ts` | Never written |",
            header=header,
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_UNREADABLE_STATUS, self.codes(report))

    def test_a_sentence_status_is_read_as_a_real_claim(self):
        self.project.write("tests/Feature/LoginTest.php", PHP_TEST)
        self.project.manifest(
            "| Staff login | feature | Passed locally; policy unchanged | `tests/Feature/LoginTest.php` | note |"
        )
        report = self.run_mode(MODULE.MODE_RELEASE, changed_files=["TESTING.md"])
        self.assertTrue(report.ok, self.codes(report))

    def test_a_negated_sentence_status_is_not_read_as_covered(self):
        self.project.write("tests/Feature/LoginTest.php", PHP_TEST)
        self.project.manifest(
            "| Staff login | feature | Not verified on any environment | `tests/Feature/LoginTest.php` | note |"
        )
        report = self.run_mode(MODULE.MODE_RELEASE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_UNREADABLE_STATUS, self.codes(report))

    def test_deleting_every_row_does_not_turn_a_release_green(self):
        self.project.write("TESTING.md", "# Testing Manifest\n\nAll rows removed.\n")
        report = self.run_mode(MODULE.MODE_RELEASE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_MANIFEST_UNAVAILABLE, self.codes(report))

    def test_deleting_the_manifest_does_not_turn_a_release_green(self):
        report = self.run_mode(MODULE.MODE_RELEASE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_MANIFEST_UNAVAILABLE, self.codes(report))


class SharedGuardIntegration(unittest.TestCase):
    """The shared guard is the model-agnostic caller: Claude, Codex and Kilo all
    reach enforcement through it rather than through a per-tool hook."""

    def test_pre_commit_guard_invokes_the_shared_engine(self):
        guard = Path(__file__).resolve().parents[0] / "pre-commit-guard.sh"
        source = guard.read_text(encoding="utf-8")
        self.assertIn("coverage_enforcement.py", source)
        self.assertIn("--mode change", source)
        self.assertIn("--staged", source)

    def test_guard_passes_in_a_repository_with_no_manifest(self):
        root = Path(__file__).resolve().parents[2]
        result = subprocess.run(
            [str(root / "scripts" / "agent-checks" / "pre-commit-guard.sh")],
            cwd=root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class RealWorldManifestShapes(EnforcementTestCase):
    """Every case here was a defect found by running the engine against the four
    live manifests. Each one is locked down so it cannot come back."""

    def test_brace_expansion_resolves_to_real_files(self):
        for name in ("ParentOtpDeliveryFailureTest", "TutorOtpDeliveryFailureTest", "OtpDeliveryAuditTest"):
            self.project.write(f"tests/Feature/Security/{name}.php", PHP_TEST)
        self.project.manifest(
            "| OTP delivery failure | feature | ✅ Covered | "
            "`tests/Feature/Security/{ParentOtpDeliveryFailureTest,TutorOtpDeliveryFailureTest,OtpDeliveryAuditTest}.php` | "
            "Shell brace notation keeps the row readable |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertTrue(report.ok, self.codes(report))

    def test_brace_expansion_still_catches_a_missing_member(self):
        self.project.write("tests/Feature/Security/ParentOtpDeliveryFailureTest.php", PHP_TEST)
        self.project.manifest(
            "| OTP delivery failure | feature | ✅ Covered | "
            "`tests/Feature/Security/{ParentOtpDeliveryFailureTest,GhostTest}.php` | One of the two is fiction |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_MISSING_TEST_FILE, self.codes(report))

    def test_paired_product_path_is_not_required_to_exist_locally(self):
        self.project.write("tests/Feature/API/RippleTutorLifecycleSignalsApiTest.php", PHP_TEST)
        self.project.manifest(
            "| Ripple tutor lifecycle signals | feature API and paired Ripple browser E2E | ✅ Covered | "
            "`tests/Feature/API/RippleTutorLifecycleSignalsApiTest.php`; paired Ripple `tests/e2e/crm/workspace.spec.ts` | "
            "The journey lives in the product that owns the screen |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertTrue(report.ok, self.codes(report))
        self.assertEqual(report.summary_counts.get("external-evidence"), 1)

    def test_a_local_path_in_the_same_cell_must_still_exist(self):
        self.project.manifest(
            "| Ripple tutor lifecycle signals | feature API and paired Ripple browser E2E | ✅ Covered | "
            "`tests/Feature/API/RippleTutorLifecycleSignalsApiTest.php`; paired Ripple `tests/e2e/crm/workspace.spec.ts` | "
            "Local half was never written |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_MISSING_TEST_FILE, self.codes(report))

    def test_external_evidence_is_counted_not_hidden(self):
        self.project.write("tests/Feature/API/RippleApiTest.php", PHP_TEST)
        self.project.manifest(
            "| Ripple settings authority | service, command, Ripple browser E2E | ✅ Covered | "
            "`tests/Feature/API/RippleApiTest.php` | Journey proved in Ripple |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertTrue(report.ok, self.codes(report))
        self.assertEqual(report.summary_counts.get("external-evidence"), 1)

    def test_a_prose_row_mentioning_feature_and_state_is_not_read_as_a_header(self):
        rows = MODULE.parse_manifest(
            "# M\n\n"
            + HEADER
            + "| Staff login | browser E2E | ✅ Covered | `tests/e2e/a.spec.ts` | note |\n"
            + "| Slip wording | Vitest component, feature source/render, permanent browser E2E | ✅ Covered | "
            "`tests/e2e/b.spec.ts` | Refuses when the request changed state after review |\n"
            + "| Console command | real-MySQL console feature | ✅ Covered | `tests/e2e/c.spec.ts` | note |\n"
        )
        self.assertEqual(len(rows), 3)
        self.assertEqual([row.feature for row in rows], ["Staff login", "Slip wording", "Console command"])

    def test_state_column_is_read_as_status(self):
        header = "| Feature | Test Type | State | Test File | Notes |\n|---|---|---|---|---|\n"
        rows = MODULE.parse_manifest(
            "# M\n\n" + header + "| Staff login | browser E2E | ✅ Covered | `tests/e2e/a.spec.ts` | note |\n"
        )
        self.assertEqual(rows[0].status, MODULE.STATUS_COVERED)

    def test_evidence_column_is_read_as_the_test_column(self):
        header = "| Feature | Persona | Evidence | State |\n|---|---|---|---|\n"
        self.project.write("tests/Feature/Security/OtpTest.php", PHP_TEST)
        self.project.manifest(
            "| OTP fails closed | Parent, Finance | `tests/Feature/Security/OtpTest.php` | ✅ Covered |",
            header=header,
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertTrue(report.ok, self.codes(report))

    def test_a_support_file_beside_a_real_test_is_not_a_lie(self):
        self.project.write("tests/Feature/Integration/IdentityTest.php", PHP_TEST)
        self.project.write("tests/Support/identity-http-router.php", "<?php\nreturn ['route' => '/identity'];\n")
        self.project.manifest(
            "| Identity projection | feature | ✅ Covered | "
            "`tests/Feature/Integration/IdentityTest.php`; `tests/Support/identity-http-router.php` | "
            "A test and the fixture it uses |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertTrue(report.ok, self.codes(report))

    def test_a_row_naming_only_a_support_file_is_still_a_lie(self):
        self.project.write("tests/Support/identity-http-router.php", "<?php\nreturn ['route' => '/identity'];\n")
        self.project.manifest(
            "| Identity projection | feature | ✅ Covered | `tests/Support/identity-http-router.php` | Fixture sold as a test |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_EMPTY_OR_COMMENT_ONLY, self.codes(report))


class ScopeContainment(EnforcementTestCase):
    """A manifest is data an agent wrote. It must never steer enforcement
    outside the project, read an environment file, or walk the filesystem."""

    def test_an_absolute_path_is_never_accepted_as_evidence(self):
        self.project.manifest(
            "| Staff login | feature | ✅ Covered | `/etc/passwd` | Absolute path |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_DECLARED_WITHOUT_PATH, self.codes(report))

    def test_a_bare_root_slash_is_rejected(self):
        self.assertEqual(MODULE.extract_paths("`/`"), [])
        self.assertFalse(MODULE.is_safe_project_relative("/"))

    def test_a_parent_traversal_is_rejected(self):
        self.assertEqual(MODULE.extract_paths("`../../other-repo/tests/a.spec.ts`"), [])

    def test_a_home_expansion_is_rejected(self):
        self.assertEqual(MODULE.extract_paths("`~/secrets/a.spec.ts`"), [])

    def test_an_environment_file_is_never_read(self):
        self.assertEqual(MODULE.extract_paths("`.env`"), [])
        self.assertEqual(MODULE.extract_paths("`config/.env.production`"), [])

    def test_a_symlink_escaping_the_project_is_not_counted(self):
        outside = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, outside, True)
        (outside / "LoginTest.php").write_text(PHP_TEST, encoding="utf-8")
        (self.tmp / "tests").mkdir(parents=True)
        (self.tmp / "tests" / "LoginTest.php").symlink_to(outside / "LoginTest.php")
        self.project.manifest(
            "| Staff login | feature | ✅ Covered | `tests/LoginTest.php` | Symlink out of the project |"
        )
        report = self.run_mode(MODULE.MODE_CHANGE, changed_files=["TESTING.md"])
        self.assertFalse(report.ok)
        self.assertIn(MODULE.CODE_MISSING_TEST_FILE, self.codes(report))


class Performance(EnforcementTestCase):
    """Two regexes in this engine once took a real manifest from milliseconds to
    minutes. Both were quadratic on the long prose cells these manifests use."""

    def test_a_very_long_notes_cell_parses_quickly(self):
        import time

        notes = "The narrow integration accepts evidence only when both switches pass. " * 200
        manifest = (
            "# M\n\n"
            + HEADER
            + f"| Staff login | browser E2E | ✅ Covered | `tests/e2e/a.spec.ts` | {notes} |\n"
        )
        started = time.monotonic()
        rows = MODULE.parse_manifest(manifest)
        elapsed = time.monotonic() - started
        self.assertEqual(len(rows), 1)
        self.assertLess(elapsed, 2.0, "manifest parsing must stay linear in cell length")

    def test_stripping_comments_from_a_large_file_stays_linear(self):
        import time

        body = '"""module docstring"""\n' + ("x = 1  # filler\n" * 20000) + "def test_thing():\n    assert True\n"
        started = time.monotonic()
        stripped = MODULE.strip_comments(body)
        elapsed = time.monotonic() - started
        self.assertIn("def test_thing", stripped)
        self.assertLess(elapsed, 2.0, "comment stripping must stay linear in file size")


if __name__ == "__main__":
    unittest.main()
