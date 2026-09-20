#!/usr/bin/env python3
"""Regression fixtures for staff documentation release enforcement (issue 112).

Positive controls: an honest decision passes in both modes.
Negative controls: each way a release can skip, fake, or erase its staff
documentation decision produces a finding that names the problem in plain
English.

The fixtures are deterministic. They build throwaway projects on disk, so no
product repository, network, or framework install is required.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("release_documentation.py")


def load_module():
    spec = importlib.util.spec_from_file_location("release_documentation", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()

HEADER = (
    "| Change | Decision | Artifacts | Owner | Follow-up | Reason |\n"
    "| --- | --- | --- | --- | --- | --- |\n"
)

CHANGELOG = """# Changelog

## 2026-09-20

- Finance: the invoice list keeps the status filter after a refresh.
"""

HELP_TS = """export const help = {
  statusFilter: 'The status filter now stays selected after a refresh.',
};
"""

STAFF_GUIDE = """# Recording a manual payout

1. Open Finance.
2. Choose the tutor.
3. Record the payout and attach the bank document.
"""


def row(change, decision, artifacts="-", owner="-", follow_up="-", reason="-"):
    return f"| {change} | {decision} | {artifacts} | {owner} | {follow_up} | {reason} |\n"


class ProjectFixture:
    """A throwaway project on disk, shaped like one of the real products."""

    def __init__(self, shape="next"):
        self.root = Path(tempfile.mkdtemp(prefix="agent-os-release-docs-"))
        if shape == "next":
            (self.root / "src/modules/finance/lib").mkdir(parents=True)
            self.write("src/modules/finance/lib/help.ts", HELP_TS)
            self.write("src/modules/finance/invoices.tsx", "export const Invoices = () => null;\n")
            self.write("CHANGELOG.md", CHANGELOG)
        elif shape == "laravel":
            (self.root / "app/Http/Controllers").mkdir(parents=True)
            self.write("artisan", "#!/usr/bin/env php\n")
            self.write("app/Http/Controllers/InvoiceController.php", "<?php\nclass InvoiceController {}\n")
            self.write("docs/staff-guides/payout.md", STAFF_GUIDE)
            self.write("docs/changelogs/release-notes-2026-09-20-example.md", CHANGELOG)
        elif shape == "bare":
            (self.root / "src").mkdir(parents=True)
            self.write("src/index.js", "export default 1;\n")
        else:
            raise ValueError(shape)

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def remove(self, relative):
        (self.root / relative).unlink()

    def ledger(self, body, name="RELEASE-DOCS.md"):
        self.write(name, "# Release Documentation Decisions\n\n" + HEADER + body)

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)


class ReleaseDocsTestCase(unittest.TestCase):
    shape = "next"

    def setUp(self):
        self.project = ProjectFixture(self.shape)
        self.addCleanup(self.project.cleanup)

    def check(self, changed, previous="", mode=MODULE.MODE_BLOCKING):
        return MODULE.run(
            project=self.project.root,
            mode=mode,
            changed_files=list(changed),
            previous_ledger_text=previous,
        )

    def codes(self, report):
        return sorted({finding.code for finding in report.findings})

    def assertPasses(self, report):
        self.assertTrue(
            report.ok,
            msg="expected a pass, got: " + MODULE.format_report(report),
        )

    def assertFinding(self, report, code):
        self.assertIn(code, self.codes(report), msg=MODULE.format_report(report))


# ──────────────────────────────────────────────────────────────────────────────
# Decision 1 of 3: relevant
# ──────────────────────────────────────────────────────────────────────────────


class RelevantDecision(ReleaseDocsTestCase):
    def relevant_change(self, artifacts):
        self.project.ledger(row("#418 invoice status filter", "relevant", artifacts))
        return [
            "src/modules/finance/invoices.tsx",
            "CHANGELOG.md",
            "src/modules/finance/lib/help.ts",
            "RELEASE-DOCS.md",
        ]

    def test_relevant_change_shipping_its_documentation_passes_both_modes(self):
        changed = self.relevant_change("`CHANGELOG.md`, `src/modules/finance/lib/help.ts`")
        self.assertPasses(self.check(changed, mode=MODULE.MODE_ADVISORY))
        self.assertPasses(self.check(changed, mode=MODULE.MODE_BLOCKING))

    def test_relevant_with_no_named_artifact_fails(self):
        changed = self.relevant_change("-")
        self.assertFinding(self.check(changed), MODULE.CODE_ARTIFACT_NOT_DECLARED)

    def test_relevant_naming_a_file_that_does_not_exist_fails(self):
        changed = self.relevant_change("`CHANGELOG.md`, `docs/guides/invented.md`")
        self.assertFinding(self.check(changed), MODULE.CODE_ARTIFACT_ABSENT)

    def test_documentation_from_an_earlier_release_does_not_count(self):
        self.project.ledger(row("#418 invoice status filter", "relevant", "`CHANGELOG.md`"))
        report = self.check(["src/modules/finance/invoices.tsx", "RELEASE-DOCS.md"])
        self.assertFinding(report, MODULE.CODE_ARTIFACT_NOT_IN_BUNDLE)

    def test_required_project_artifact_must_be_covered(self):
        changed = self.relevant_change("`src/modules/finance/lib/help.ts`")
        self.assertFinding(self.check(changed), MODULE.CODE_REQUIRED_ARTIFACT_MISSING)

    def test_pointing_at_the_ledger_itself_is_not_documentation(self):
        changed = self.relevant_change("`RELEASE-DOCS.md`")
        self.assertFinding(self.check(changed), MODULE.CODE_ARTIFACT_IS_LEDGER)

    def test_a_path_outside_the_project_is_refused(self):
        changed = self.relevant_change("`../other-repo/CHANGELOG.md`")
        self.assertFinding(self.check(changed), MODULE.CODE_ARTIFACT_UNSAFE_PATH)

    def test_a_url_is_not_a_release_artifact(self):
        changed = self.relevant_change("https://example.test/release-notes")
        self.assertFinding(self.check(changed), MODULE.CODE_ARTIFACT_NOT_DECLARED)

    def test_a_glob_artifact_resolves_to_real_files(self):
        changed = self.relevant_change("`CHANGELOG.md`, `src/modules/*/lib/help.ts`")
        self.assertPasses(self.check(changed))

    def test_a_glob_artifact_matching_nothing_fails(self):
        changed = self.relevant_change("`CHANGELOG.md`, `src/modules/*/lib/onboarding.ts`")
        self.assertFinding(self.check(changed), MODULE.CODE_ARTIFACT_ABSENT)


# ──────────────────────────────────────────────────────────────────────────────
# Decision 2 of 3: not relevant
# ──────────────────────────────────────────────────────────────────────────────


class NotRelevantDecision(ReleaseDocsTestCase):
    def not_relevant(self, reason):
        self.project.ledger(row("#421 invoice query index", "not relevant", "-", "-", "-", reason))
        return ["src/modules/finance/invoices.tsx", "RELEASE-DOCS.md"]

    def test_not_relevant_with_a_real_reason_passes(self):
        changed = self.not_relevant("Database index only; nothing staff see or do changes")
        self.assertPasses(self.check(changed))

    def test_not_relevant_without_a_reason_fails(self):
        self.assertFinding(self.check(self.not_relevant("")), MODULE.CODE_REASON_MISSING)

    def test_not_relevant_with_a_placeholder_reason_fails(self):
        self.assertFinding(self.check(self.not_relevant("n/a")), MODULE.CODE_REASON_MISSING)

    def test_not_relevant_is_never_read_as_relevant(self):
        changed = self.not_relevant("Internal only")
        report = self.check(changed)
        self.assertEqual(report.summary_counts, {MODULE.NOT_RELEVANT: 1})


# ──────────────────────────────────────────────────────────────────────────────
# Decision 3 of 3: urgent deferral
# ──────────────────────────────────────────────────────────────────────────────


class UrgentDeferralDecision(ReleaseDocsTestCase):
    REASON = "Hotfix shipped mid payout window; the guide follows this week"

    def deferral(self, owner, follow_up, reason=REASON, change="#430 payout hotfix"):
        self.project.ledger(row(change, "urgent deferral", "-", owner, follow_up, reason))
        return ["src/modules/finance/invoices.tsx", "RELEASE-DOCS.md"]

    def test_named_owner_and_real_follow_up_issue_passes(self):
        self.assertPasses(self.check(self.deferral("Hafiz Razali", "#431")))

    def test_owner_handle_is_accepted(self):
        self.assertPasses(self.check(self.deferral("@hafizrazali90", "#431")))

    def test_cross_repository_issue_reference_is_accepted(self):
        self.assertPasses(self.check(self.deferral("Hafiz Razali", "Sifututor/sifu-tutor#431")))

    def test_issue_url_is_accepted(self):
        self.assertPasses(
            self.check(self.deferral("Hafiz Razali", "https://github.com/Sifututor/sifu-tutor/issues/431"))
        )

    def test_placeholder_owner_fails(self):
        for owner in ("TBD", "-", "", "later", "?"):
            with self.subTest(owner=owner):
                self.assertFinding(self.check(self.deferral(owner, "#431")), MODULE.CODE_OWNER_MISSING)

    def test_a_role_or_queue_is_not_an_owner(self):
        for owner in ("the team", "engineering", "unassigned", "someone"):
            with self.subTest(owner=owner):
                self.assertFinding(self.check(self.deferral(owner, "#431")), MODULE.CODE_OWNER_MISSING)

    def test_the_agent_cannot_own_its_own_deferral(self):
        for owner in ("Claude", "Codex", "agent", "AI"):
            with self.subTest(owner=owner):
                self.assertFinding(self.check(self.deferral(owner, "#431")), MODULE.CODE_OWNER_MISSING)

    def test_vague_follow_up_fails(self):
        for follow_up in ("later", "TODO", "TBD", "-", "", "soon", "next sprint"):
            with self.subTest(follow_up=follow_up):
                self.assertFinding(
                    self.check(self.deferral("Hafiz Razali", follow_up)),
                    MODULE.CODE_FOLLOW_UP_MISSING,
                )

    def test_prose_promising_an_issue_is_not_an_issue(self):
        report = self.check(self.deferral("Hafiz Razali", "will raise an issue after the release"))
        self.assertFinding(report, MODULE.CODE_FOLLOW_UP_MISSING)

    def test_issue_zero_is_not_a_real_issue(self):
        self.assertFinding(self.check(self.deferral("Hafiz Razali", "#0")), MODULE.CODE_FOLLOW_UP_MISSING)

    def test_the_change_own_issue_cannot_be_its_follow_up(self):
        report = self.check(self.deferral("Hafiz Razali", "#430"))
        self.assertFinding(report, MODULE.CODE_FOLLOW_UP_SELF_REFERENCE)

    def test_deferral_without_a_reason_fails(self):
        report = self.check(self.deferral("Hafiz Razali", "#431", reason="-"))
        self.assertFinding(report, MODULE.CODE_REASON_MISSING)

    def test_an_urgent_deferral_is_not_a_way_to_skip_the_owner_and_the_issue_together(self):
        report = self.check(self.deferral("TBD", "later", reason=""))
        self.assertEqual(
            self.codes(report),
            sorted(
                {
                    MODULE.CODE_OWNER_MISSING,
                    MODULE.CODE_FOLLOW_UP_MISSING,
                    MODULE.CODE_REASON_MISSING,
                }
            ),
        )


# ──────────────────────────────────────────────────────────────────────────────
# An unreadable decision is not a decision
# ──────────────────────────────────────────────────────────────────────────────


class DecisionReadability(ReleaseDocsTestCase):
    def decided(self, decision):
        self.project.ledger(row("#418 invoice status filter", decision, "`CHANGELOG.md`"))
        return ["src/modules/finance/invoices.tsx", "CHANGELOG.md", "RELEASE-DOCS.md"]

    def test_a_placeholder_decision_fails(self):
        for decision in ("TBD", "-", "", "?", "pending", "unknown"):
            with self.subTest(decision=decision):
                self.assertFinding(self.check(self.decided(decision)), MODULE.CODE_DECISION_UNREADABLE)

    def test_an_invented_decision_word_fails(self):
        self.assertFinding(self.check(self.decided("probably fine")), MODULE.CODE_DECISION_UNREADABLE)

    def test_the_three_decision_words_are_all_recognised(self):
        for text, expected in (
            ("relevant", MODULE.RELEVANT),
            ("Relevant", MODULE.RELEVANT),
            ("not relevant", MODULE.NOT_RELEVANT),
            ("not-relevant", MODULE.NOT_RELEVANT),
            ("urgent deferral", MODULE.URGENT_DEFERRAL),
            ("Urgent-Deferral", MODULE.URGENT_DEFERRAL),
        ):
            with self.subTest(text=text):
                self.assertEqual(MODULE.classify_decision(text), expected)


# ──────────────────────────────────────────────────────────────────────────────
# Projects do not share paths
# ──────────────────────────────────────────────────────────────────────────────


class NextProjectShape(ReleaseDocsTestCase):
    shape = "next"

    def test_convention_is_detected_from_the_repository(self):
        self.project.ledger("")
        report = self.check(["src/modules/finance/invoices.tsx"])
        self.assertEqual(report.config_source, "convention:next-modules")

    def test_a_module_file_is_staff_facing_here(self):
        self.project.ledger("")
        report = self.check(["src/modules/finance/invoices.tsx"])
        self.assertFinding(report, MODULE.CODE_DECISION_MISSING)

    def test_a_laravel_path_is_not_staff_facing_in_a_next_project(self):
        self.project.ledger("")
        self.assertPasses(self.check(["resources/views/invoice.blade.php"]))


class LaravelProjectShape(ReleaseDocsTestCase):
    shape = "laravel"

    def test_convention_is_detected_from_the_repository(self):
        self.project.ledger("")
        report = self.check(["app/Http/Controllers/InvoiceController.php"])
        self.assertEqual(report.config_source, "convention:laravel")

    def test_a_controller_is_staff_facing_here(self):
        self.project.ledger("")
        report = self.check(["app/Http/Controllers/InvoiceController.php"])
        self.assertFinding(report, MODULE.CODE_DECISION_MISSING)

    def test_a_next_module_path_is_not_staff_facing_in_a_laravel_project(self):
        self.project.ledger("")
        self.assertPasses(self.check(["src/modules/finance/invoices.tsx"]))

    def test_a_staff_guide_is_the_documentation_here(self):
        self.project.ledger(
            row(
                "#502 manual payout",
                "relevant",
                "`docs/changelogs/release-notes-2026-09-20-example.md`, `docs/staff-guides/payout.md`",
            )
        )
        self.assertPasses(
            self.check(
                [
                    "app/Http/Controllers/InvoiceController.php",
                    "docs/changelogs/release-notes-2026-09-20-example.md",
                    "docs/staff-guides/payout.md",
                    "RELEASE-DOCS.md",
                ]
            )
        )

    def test_sims_dated_release_note_satisfies_the_required_release_artifact(self):
        config, problem = MODULE.resolve_config(self.project.root)
        self.assertIsNone(problem)
        required = {kind.name: kind.patterns for kind in config.required_kinds}
        self.assertIn("docs/changelogs/release-notes-*.md", required["release note"])


class RippleReleaseArtifactShape(ReleaseDocsTestCase):
    shape = "next"

    def test_ripple_seed_release_is_recognised_as_whats_new(self):
        config, problem = MODULE.resolve_config(self.project.root)
        self.assertIsNone(problem)
        whats_new = next(kind for kind in config.artifacts if kind.name == "what's new")
        self.assertIn("scripts/seed-releases-*.ts", whats_new.patterns)


class ProjectConfigurationOverridesConvention(ReleaseDocsTestCase):
    shape = "next"

    CONFIG = {
        "ledger": "docs/release-decisions.md",
        "staff_facing": ["packages/admin/**"],
        "not_staff_facing": ["packages/admin/**/*.test.ts"],
        "artifacts": {
            "changelog": {"paths": ["CHANGELOG.md"], "required": True, "meaning": "what changed"},
            "staff guide": {"paths": ["docs/staff-guides/**"], "required": True, "meaning": "how to do it"},
        },
    }

    def configure(self, config=None):
        self.project.write(
            MODULE.CONFIG_NAME,
            json.dumps(config if config is not None else self.CONFIG, indent=2),
        )

    def test_configuration_wins_over_the_detected_convention(self):
        self.configure()
        self.project.write("docs/release-decisions.md", HEADER)
        report = self.check(["packages/admin/billing.ts"])
        self.assertEqual(report.config_source, MODULE.CONFIG_NAME)
        self.assertFinding(report, MODULE.CODE_DECISION_MISSING)

    def test_a_path_the_convention_called_staff_facing_is_not_when_config_says_otherwise(self):
        self.configure()
        self.project.write("docs/release-decisions.md", HEADER)
        self.assertPasses(self.check(["src/modules/finance/invoices.tsx"]))

    def test_the_configured_ledger_name_is_used(self):
        self.configure()
        report = self.check(["packages/admin/billing.ts"])
        self.assertFinding(report, MODULE.CODE_LEDGER_MISSING)
        self.assertIn("docs/release-decisions.md", report.findings[0].detail)

    def test_every_configured_required_artifact_must_be_covered(self):
        self.configure()
        self.project.write("docs/staff-guides/billing.md", STAFF_GUIDE)
        self.project.write(
            "docs/release-decisions.md",
            HEADER + row("#601 billing", "relevant", "`CHANGELOG.md`"),
        )
        report = self.check(["packages/admin/billing.ts", "CHANGELOG.md", "docs/release-decisions.md"])
        self.assertFinding(report, MODULE.CODE_REQUIRED_ARTIFACT_MISSING)
        self.assertIn("staff guide", MODULE.format_report(report))

    def test_configured_exclusions_keep_test_files_out_of_scope(self):
        self.configure()
        self.project.write("docs/release-decisions.md", HEADER)
        self.assertPasses(self.check(["packages/admin/billing.test.ts"]))


# ──────────────────────────────────────────────────────────────────────────────
# Unavailable configuration is reported, never assumed passed
# ──────────────────────────────────────────────────────────────────────────────


class UnavailableConfiguration(ReleaseDocsTestCase):
    shape = "bare"

    def test_a_project_with_no_shape_is_unavailable_and_does_not_block_a_change(self):
        report = self.check(["src/index.js"], mode=MODULE.MODE_ADVISORY)
        self.assertEqual(report.state, MODULE.STATE_UNAVAILABLE)
        self.assertPasses(report)
        self.assertIn("unavailable, not as passed", MODULE.format_report(report))

    def test_a_project_with_no_shape_cannot_prove_a_release(self):
        report = self.check(["src/index.js"], mode=MODULE.MODE_BLOCKING)
        self.assertFinding(report, MODULE.CODE_CONFIG_UNAVAILABLE)

    def test_broken_configuration_json_is_reported_in_both_modes(self):
        self.project.write(MODULE.CONFIG_NAME, "{ not json")
        for mode in (MODULE.MODE_ADVISORY, MODULE.MODE_BLOCKING):
            with self.subTest(mode=mode):
                report = self.check(["src/index.js"], mode=mode)
                self.assertFinding(report, MODULE.CODE_CONFIG_UNREADABLE)

    def test_configuration_that_declares_nothing_is_refused(self):
        self.project.write(MODULE.CONFIG_NAME, json.dumps({"ledger": "RELEASE-DOCS.md"}))
        self.assertFinding(self.check(["src/index.js"]), MODULE.CODE_CONFIG_UNREADABLE)

    def test_configuration_with_an_artifact_that_names_no_path_is_refused(self):
        self.project.write(
            MODULE.CONFIG_NAME,
            json.dumps({"staff_facing": ["src/**"], "artifacts": {"changelog": {"required": True}}}),
        )
        self.assertFinding(self.check(["src/index.js"]), MODULE.CODE_CONFIG_UNREADABLE)

    def test_configuration_pointing_its_ledger_outside_the_project_is_refused(self):
        self.project.write(
            MODULE.CONFIG_NAME,
            json.dumps({"ledger": "../shared/RELEASE-DOCS.md", "staff_facing": ["src/**"]}),
        )
        self.assertFinding(self.check(["src/index.js"]), MODULE.CODE_CONFIG_UNREADABLE)

    def test_an_unscopable_change_is_reported_not_silently_passed(self):
        project = ProjectFixture("next")
        self.addCleanup(project.cleanup)
        project.ledger(row("#418 old release", "relevant", "`CHANGELOG.md`"))
        report = MODULE.run(
            project=project.root,
            mode=MODULE.MODE_BLOCKING,
            changed_files=["src/modules/finance/invoices.tsx"],
            previous_ledger_text=None,
        )
        self.assertFinding(report, MODULE.CODE_SCOPE_UNAVAILABLE)
        self.assertEqual(report.entries_in_scope, 0)


# ──────────────────────────────────────────────────────────────────────────────
# Scope containment: today's release is not an audit of the whole product
# ──────────────────────────────────────────────────────────────────────────────


class ScopeContainment(ReleaseDocsTestCase):
    HISTORY = row("#101 tutor onboarding", "relevant", "`docs/guides/deleted.md`") + row(
        "#102 parent invoices", "urgent deferral", "-", "TBD", "later", "-"
    )

    def test_an_unrelated_historical_decision_never_blocks_todays_change(self):
        self.project.ledger(self.HISTORY)
        report = self.check(
            ["src/modules/finance/lib/tax.ts"],
            previous="# Release Documentation Decisions\n\n" + HEADER + self.HISTORY,
        )
        self.assertFinding(report, MODULE.CODE_DECISION_MISSING)
        self.assertNotIn(MODULE.CODE_ARTIFACT_ABSENT, self.codes(report))
        self.assertNotIn(MODULE.CODE_OWNER_MISSING, self.codes(report))
        self.assertEqual(report.entries_in_scope, 0)

    def test_history_is_untouched_when_todays_change_records_its_own_decision(self):
        body = self.HISTORY + row(
            "#418 invoice status filter", "relevant", "`CHANGELOG.md`, `src/modules/finance/lib/help.ts`"
        )
        self.project.ledger(body)
        report = self.check(
            [
                "src/modules/finance/invoices.tsx",
                "CHANGELOG.md",
                "src/modules/finance/lib/help.ts",
                "RELEASE-DOCS.md",
            ],
            previous="# Release Documentation Decisions\n\n" + HEADER + self.HISTORY,
        )
        self.assertPasses(report)
        self.assertEqual(report.entries_in_scope, 1)
        self.assertEqual(report.entries_total, 3)

    def test_editing_an_old_decision_brings_it_back_into_scope(self):
        edited = row("#101 tutor onboarding", "relevant", "`docs/guides/still-missing.md`") + row(
            "#102 parent invoices", "urgent deferral", "-", "TBD", "later", "-"
        )
        self.project.ledger(edited)
        report = self.check(
            ["src/modules/finance/invoices.tsx", "RELEASE-DOCS.md"],
            previous="# Release Documentation Decisions\n\n" + HEADER + self.HISTORY,
        )
        self.assertFinding(report, MODULE.CODE_ARTIFACT_ABSENT)
        self.assertEqual(report.entries_in_scope, 1)

    def test_this_check_never_asks_for_tests(self):
        self.project.ledger(self.HISTORY)
        report = self.check(
            ["src/modules/finance/lib/tax.ts"],
            previous="# Release Documentation Decisions\n\n" + HEADER + self.HISTORY,
        )
        self.assertNotIn("test", MODULE.format_report(report).lower().replace("latest", ""))


# ──────────────────────────────────────────────────────────────────────────────
# Over-blocking is its own failure
# ──────────────────────────────────────────────────────────────────────────────


class DoesNotOverBlock(ReleaseDocsTestCase):
    def test_a_repository_with_staff_docs_does_not_gate_unrelated_work(self):
        self.project.ledger("")
        self.assertPasses(
            self.check(
                [
                    "package.json",
                    "package-lock.json",
                    ".github/workflows/ci.yml",
                    "scripts/build.mjs",
                    "README.md",
                ]
            )
        )

    def test_a_test_only_change_inside_a_staff_facing_folder_is_not_gated(self):
        self.project.ledger("")
        self.assertPasses(
            self.check(
                [
                    "src/modules/finance/__tests__/invoices.test.tsx",
                    "src/modules/finance/invoices.spec.ts",
                ]
            )
        )

    def test_a_docs_only_change_is_not_gated(self):
        self.project.ledger("")
        self.assertPasses(self.check(["docs/agent-playbooks/commit.md"]))

    def test_an_empty_change_is_not_gated(self):
        self.project.ledger("")
        self.assertPasses(self.check([]))


# ──────────────────────────────────────────────────────────────────────────────
# Bypass attempts
# ──────────────────────────────────────────────────────────────────────────────


class BypassAttempts(ReleaseDocsTestCase):
    EXISTING = row("#418 invoice status filter", "relevant", "`CHANGELOG.md`")
    PREVIOUS = "# Release Documentation Decisions\n\n" + HEADER + EXISTING

    def test_deleting_the_ledger_does_not_make_a_staff_facing_change_green(self):
        report = self.check(["src/modules/finance/invoices.tsx"], previous=self.PREVIOUS)
        self.assertFinding(report, MODULE.CODE_LEDGER_MISSING)

    def test_deleting_a_recorded_decision_is_a_finding(self):
        self.project.ledger(row("#500 something else", "not relevant", "-", "-", "-", "Internal only"))
        report = self.check(["src/modules/finance/invoices.tsx", "RELEASE-DOCS.md"], previous=self.PREVIOUS)
        self.assertFinding(report, MODULE.CODE_ENTRY_REMOVED)

    def test_emptying_the_table_does_not_make_a_staff_facing_change_green(self):
        self.project.ledger("")
        report = self.check(["src/modules/finance/invoices.tsx", "RELEASE-DOCS.md"], previous=self.PREVIOUS)
        self.assertEqual(
            self.codes(report),
            sorted({MODULE.CODE_ENTRY_REMOVED, MODULE.CODE_DECISION_MISSING}),
        )

    def test_replacing_the_table_with_prose_is_a_finding(self):
        self.project.write("RELEASE-DOCS.md", "# Release docs\n\nAll handled, nothing to see here.\n")
        report = self.check(["src/modules/finance/invoices.tsx", "RELEASE-DOCS.md"], previous=self.PREVIOUS)
        self.assertFinding(report, MODULE.CODE_LEDGER_UNPARSEABLE)

    def test_renaming_the_change_does_not_hide_a_broken_decision(self):
        self.project.ledger(row("#418 renamed", "relevant", "`docs/guides/invented.md`"))
        report = self.check(["src/modules/finance/invoices.tsx", "RELEASE-DOCS.md"], previous=self.PREVIOUS)
        self.assertFinding(report, MODULE.CODE_ARTIFACT_ABSENT)
        self.assertFinding(report, MODULE.CODE_ENTRY_REMOVED)

    def test_an_extra_column_cannot_smuggle_an_unreadable_decision(self):
        self.project.write(
            "RELEASE-DOCS.md",
            "| Change | Decision | Artifacts | Owner | Follow-up | Reason | Notes |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n"
            "| #418 invoice status filter | see PR | - | - | - | - | trust me |\n",
        )
        report = self.check(["src/modules/finance/invoices.tsx", "RELEASE-DOCS.md"], previous="")
        self.assertFinding(report, MODULE.CODE_DECISION_UNREADABLE)


# ──────────────────────────────────────────────────────────────────────────────
# Advisory and blocking modes
# ──────────────────────────────────────────────────────────────────────────────


class Modes(ReleaseDocsTestCase):
    def setUp(self):
        super().setUp()
        self.project.ledger(row("#418 invoice status filter", "relevant", "-"))
        self.changed = ["src/modules/finance/invoices.tsx", "RELEASE-DOCS.md"]

    def test_advisory_reports_the_same_finding_without_blocking(self):
        report = self.check(self.changed, mode=MODULE.MODE_ADVISORY)
        self.assertFinding(report, MODULE.CODE_ARTIFACT_NOT_DECLARED)
        self.assertFalse(report.blocking)
        self.assertIn("ADVISORY FINDINGS", MODULE.format_report(report))

    def test_blocking_blocks_on_the_same_finding(self):
        report = self.check(self.changed, mode=MODULE.MODE_BLOCKING)
        self.assertFinding(report, MODULE.CODE_ARTIFACT_NOT_DECLARED)
        self.assertTrue(report.blocking)

    def test_every_finding_is_a_readable_sentence(self):
        report = self.check(self.changed)
        for finding in report.findings:
            self.assertGreater(len(finding.detail.split()), 8, msg=finding.detail)
            self.assertEqual(finding.detail, finding.detail.strip())


# ──────────────────────────────────────────────────────────────────────────────
# Command line
# ──────────────────────────────────────────────────────────────────────────────


class CommandLine(ReleaseDocsTestCase):
    def cli(self, *args):
        return subprocess.run(
            [sys.executable, str(MODULE_PATH), "--project", str(self.project.root), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_a_change_source_is_required(self):
        result = self.cli("--mode", "blocking")
        self.assertEqual(result.returncode, 2)
        self.assertIn("needs a change source", result.stderr)

    def test_advisory_exits_zero_with_findings(self):
        self.project.ledger(row("#418 invoice status filter", "relevant", "-"))
        result = self.cli(
            "--mode",
            "advisory",
            "--changed-file",
            "src/modules/finance/invoices.tsx",
            "--changed-file",
            "RELEASE-DOCS.md",
            "--previous-ledger",
            str(self.project.root / "absent.md"),
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout)
        self.assertIn(MODULE.CODE_ARTIFACT_NOT_DECLARED, result.stdout)

    def test_blocking_exits_one_with_findings(self):
        self.project.ledger(row("#418 invoice status filter", "relevant", "-"))
        result = self.cli(
            "--mode",
            "blocking",
            "--changed-file",
            "src/modules/finance/invoices.tsx",
            "--changed-file",
            "RELEASE-DOCS.md",
            "--previous-ledger",
            str(self.project.root / "absent.md"),
        )
        self.assertEqual(result.returncode, 1, msg=result.stdout)
        self.assertIn("STAFF DOCUMENTATION RELEASE GATE: FAIL", result.stdout)

    def test_json_output_is_machine_readable(self):
        self.project.ledger(row("#418 invoice status filter", "relevant", "-"))
        result = self.cli(
            "--json",
            "--changed-file",
            "src/modules/finance/invoices.tsx",
            "--previous-ledger",
            str(self.project.root / "absent.md"),
        )
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["config_source"], "convention:next-modules")
        self.assertTrue(payload["findings"][0]["detail"])

    def test_outside_a_git_repository_advisory_reports_without_blocking(self):
        result = self.cli("--staged")
        self.assertEqual(result.returncode, 0)
        self.assertIn("UNAVAILABLE", result.stdout)


class GitScoping(ReleaseDocsTestCase):
    def git(self, *args):
        subprocess.run(
            ["git", *args],
            cwd=self.project.root,
            capture_output=True,
            text=True,
            check=True,
        )

    def setUp(self):
        super().setUp()
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.test")
        self.git("config", "user.name", "Fixture")
        self.project.ledger(row("#101 tutor onboarding", "not relevant", "-", "-", "-", "Internal only"))
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "baseline")

    def test_staged_mode_reads_the_index_and_the_previous_ledger(self):
        self.project.write("src/modules/finance/invoices.tsx", "export const Invoices = () => 2;\n")
        self.git("add", "-A")
        result = subprocess.run(
            [
                sys.executable,
                str(MODULE_PATH),
                "--project",
                str(self.project.root),
                "--mode",
                "blocking",
                "--staged",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1, msg=result.stdout)
        self.assertIn(MODULE.CODE_DECISION_MISSING, result.stdout)
        self.assertIn("0 of 1 recorded decisions are in scope", result.stdout)

    def test_staged_mode_passes_once_the_decision_is_recorded(self):
        self.project.write("src/modules/finance/invoices.tsx", "export const Invoices = () => 2;\n")
        self.project.write("CHANGELOG.md", CHANGELOG + "- Finance: status filter fix.\n")
        self.project.ledger(
            row("#101 tutor onboarding", "not relevant", "-", "-", "-", "Internal only")
            + row("#418 invoice status filter", "relevant", "`CHANGELOG.md`")
        )
        self.git("add", "-A")
        result = subprocess.run(
            [
                sys.executable,
                str(MODULE_PATH),
                "--project",
                str(self.project.root),
                "--mode",
                "blocking",
                "--staged",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout)
        self.assertIn("PASS", result.stdout)


# ──────────────────────────────────────────────────────────────────────────────
# Wiring
# ──────────────────────────────────────────────────────────────────────────────


class SharedWiring(unittest.TestCase):
    def test_the_shared_pre_commit_guard_runs_this_engine(self):
        guard = MODULE_PATH.with_name("pre-commit-guard.sh").read_text()
        self.assertIn("release_documentation.py", guard)
        self.assertIn("--mode advisory", guard)

    def test_the_engine_reuses_the_shared_markdown_table_parser(self):
        source = MODULE_PATH.read_text()
        self.assertIn("coverage_enforcement.py", source)
        self.assertIs(MODULE.split_row, sys.modules["coverage_enforcement"].split_row)

    def test_the_playbook_owns_the_rule_and_the_engine_points_at_it(self):
        root = MODULE_PATH.resolve().parents[2]
        playbook = root / "docs/agent-playbooks/release-documentation.md"
        self.assertTrue(playbook.is_file(), msg=f"missing {playbook}")
        text = playbook.read_text()
        self.assertIn("scripts/agent-checks/release_documentation.py", text)
        for decision in ("relevant", "not relevant", "urgent deferral"):
            self.assertIn(decision, text.lower())

    def test_the_secondary_playbooks_point_at_the_single_owner(self):
        root = MODULE_PATH.resolve().parents[2]
        for relative in (
            "docs/agent-playbooks/commit.md",
            "docs/agent-playbooks/review.md",
            "docs/agent-playbooks/release-deploy-live-monitoring.md",
            "docs/agent-playbooks/no-mistakes-lite.md",
        ):
            with self.subTest(playbook=relative):
                self.assertIn("release-documentation.md", (root / relative).read_text())

    def test_the_copyable_examples_exist_and_parse(self):
        root = MODULE_PATH.resolve().parents[2]
        ledger = root / "docs/agent-playbooks/templates/release-docs-ledger.md"
        config = root / "docs/agent-playbooks/templates/release-docs.example.json"
        self.assertTrue(ledger.is_file(), msg=f"missing {ledger}")
        self.assertTrue(config.is_file(), msg=f"missing {config}")

        entries = MODULE.parse_ledger(ledger.read_text())
        decisions = {entry.decision for entry in entries}
        self.assertEqual(
            decisions,
            {MODULE.RELEVANT, MODULE.NOT_RELEVANT, MODULE.URGENT_DEFERRAL},
            msg="the template must show all three decisions",
        )
        self.assertNotIn(MODULE.UNREADABLE, decisions)

        parsed, problem = MODULE.parse_config(
            root, json.loads(config.read_text()), "release-docs.example.json"
        )
        self.assertIsNone(problem)
        self.assertTrue(parsed.required_kinds)

    def test_the_example_ledger_entries_would_pass_their_own_rules(self):
        root = MODULE_PATH.resolve().parents[2]
        ledger = root / "docs/agent-playbooks/templates/release-docs-ledger.md"
        for entry in MODULE.parse_ledger(ledger.read_text()):
            with self.subTest(change=entry.change):
                if entry.decision == MODULE.NOT_RELEVANT:
                    self.assertFalse(MODULE.is_placeholder(entry.reason_cell))
                if entry.decision == MODULE.URGENT_DEFERRAL:
                    self.assertTrue(MODULE.is_concrete_owner(entry.owner_cell))
                    self.assertIsNotNone(MODULE.issue_reference(entry.follow_up_cell))
                    self.assertFalse(MODULE.is_placeholder(entry.reason_cell))
                if entry.decision == MODULE.RELEVANT:
                    self.assertTrue(MODULE.declared_paths(entry.artifacts_cell))


if __name__ == "__main__":
    unittest.main()
