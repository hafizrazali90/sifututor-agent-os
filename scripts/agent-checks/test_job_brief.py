#!/usr/bin/env python3
"""Tests for the unattended job brief: parsing, caps and finish states."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import job_brief  # noqa: E402

ROOT = HERE.parents[1]
TEMPLATE = ROOT / "docs" / "agent-playbooks" / "templates" / "job-brief.md"

GOOD_BUILDER = """---
title: Add writing rules to the pruning playbook
role: builder
branch: docs/277-writing-rules
finish: local
issue: 277
max_usd: 2
max_turns: 30
max_minutes: 30
allowed_paths: docs/agent-playbooks/skill-quality-and-pruning.md
---
Add the instruction-writing rules described in issue 277 to the playbook.
"""


def brief(**overrides: str) -> str:
    lines = [line for line in GOOD_BUILDER.splitlines()]
    out: list[str] = []
    seen = set()
    for line in lines:
        key = line.split(":", 1)[0] if ":" in line and not line.startswith("---") else None
        if key in overrides:
            seen.add(key)
            if overrides[key] != "":
                out.append(f"{key}: {overrides[key]}")
            continue
        out.append(line)
    # insert unseen overrides before the closing marker
    closing = max(i for i, line in enumerate(out) if line == "---")
    extras = [f"{k}: {v}" for k, v in overrides.items() if k not in seen and v != ""]
    out[closing:closing] = extras
    return "\n".join(out) + "\n"


class ParseTest(unittest.TestCase):
    def test_parses_front_matter_and_body(self) -> None:
        parsed = job_brief.parse(GOOD_BUILDER)
        self.assertEqual(parsed["fields"]["role"], "builder")
        self.assertIn("issue 277", parsed["body"])

    def test_comments_after_a_value_are_ignored(self) -> None:
        parsed = job_brief.parse(brief(max_usd="3   # a small job"))
        self.assertEqual(parsed["fields"]["max_usd"], "3")

    def test_missing_front_matter_is_an_error(self) -> None:
        with self.assertRaises(job_brief.BriefError):
            job_brief.parse("no front matter here\n")


class ValidateTest(unittest.TestCase):
    def check(self, text: str):
        return job_brief.validate(job_brief.parse(text))

    def test_good_builder_brief_is_valid(self) -> None:
        errors, normal = self.check(GOOD_BUILDER)
        self.assertEqual(errors, [])
        self.assertEqual(normal["finish"], "local")
        self.assertEqual(normal["max_usd"], 2.0)
        self.assertEqual(normal["allowed_paths"], ["docs/agent-playbooks/skill-quality-and-pruning.md"])

    def test_missing_finish_defaults_to_local_and_is_recorded(self) -> None:
        errors, normal = self.check(brief(finish=""))
        self.assertEqual(errors, [])
        self.assertEqual(normal["finish"], "local")
        self.assertTrue(normal["finish_defaulted"])

    def test_merged_and_deployed_are_refused(self) -> None:
        for state in ("merged", "deployed"):
            with self.subTest(state=state):
                errors, _ = self.check(brief(finish=state))
                self.assertTrue(any("cannot merge or deploy" in e for e in errors), errors)

    def test_pr_open_needs_a_recorded_approval(self) -> None:
        errors, _ = self.check(brief(finish="pr-open"))
        self.assertTrue(any("approval" in e for e in errors), errors)
        errors, _ = self.check(brief(finish="pr-open", approval="Hafiz, chat 08/10/2026: push and open the PR"))
        self.assertEqual(errors, [])

    def test_caps_get_safe_defaults(self) -> None:
        errors, normal = self.check(brief(max_usd="", max_turns="", max_minutes=""))
        self.assertEqual(errors, [])
        self.assertEqual((normal["max_usd"], normal["max_turns"], normal["max_minutes"]), (2.0, 30, 30))
        self.assertEqual(normal["caps_defaulted"], ["max_usd", "max_turns", "max_minutes"])

    def test_caps_above_the_hard_limit_are_refused(self) -> None:
        for field, value in (("max_usd", "50"), ("max_turns", "500"), ("max_minutes", "600")):
            with self.subTest(field=field):
                errors, _ = self.check(brief(**{field: value}))
                self.assertTrue(any(field in e for e in errors), errors)

    def test_budget_below_half_a_dollar_is_refused(self) -> None:
        errors, _ = self.check(brief(max_usd="0.1"))
        self.assertTrue(any("0.5" in e for e in errors), errors)

    def test_builder_needs_a_valid_branch_name(self) -> None:
        for bad in ("main", "feature-x", "feat/Has Space", "badtype/x"):
            with self.subTest(branch=bad):
                errors, _ = self.check(brief(branch=bad))
                self.assertTrue(any("branch" in e for e in errors), errors)

    def test_builder_needs_allowed_paths_and_rejects_the_whole_repo(self) -> None:
        errors, _ = self.check(brief(allowed_paths=""))
        self.assertTrue(any("allowed_paths" in e for e in errors), errors)
        for bad in (".", "/", "../x", "*"):
            with self.subTest(path=bad):
                errors, _ = self.check(brief(allowed_paths=bad))
                self.assertTrue(any("allowed_paths" in e for e in errors), errors)

    def test_unknown_role_and_unknown_keys_are_refused(self) -> None:
        errors, _ = self.check(brief(role="admin"))
        self.assertTrue(any("role" in e for e in errors), errors)
        errors, _ = self.check(brief(surprise="x"))
        self.assertTrue(any("surprise" in e for e in errors), errors)

    def test_empty_body_is_refused(self) -> None:
        errors, _ = self.check(GOOD_BUILDER.split("---\n")[0] + "---\n" + GOOD_BUILDER.split("---\n")[1] + "---\n\n")
        self.assertTrue(any("body" in e for e in errors), errors)

    def test_reviewer_needs_a_target_and_cannot_push(self) -> None:
        reviewer = "---\ntitle: Review PR 302\nrole: reviewer\ntarget: feat/265-hook-wiring-template\n---\nReview this change against issue 265.\n"
        errors, normal = self.check(reviewer)
        self.assertEqual(errors, [])
        self.assertEqual(normal["finish"], "local")
        no_target = reviewer.replace("target: feat/265-hook-wiring-template\n", "")
        errors, _ = self.check(no_target)
        self.assertTrue(any("target" in e for e in errors), errors)
        errors, _ = self.check(reviewer.replace("role: reviewer\n", "role: reviewer\nfinish: pr-open\napproval: x\n"))
        self.assertTrue(any("reviewer" in e and "finish" in e for e in errors), errors)


class RepoFieldTest(unittest.TestCase):
    def check(self, text: str):
        return job_brief.validate(job_brief.parse(text))

    def test_missing_repo_means_the_agent_os_repo(self) -> None:
        errors, normal = self.check(brief())
        self.assertEqual(errors, [])
        self.assertEqual(normal["repo"], "")

    def test_listed_project_repo_is_accepted(self) -> None:
        errors, normal = self.check(brief(repo="ripple-suite"))
        self.assertEqual(errors, [])
        self.assertEqual(normal["repo"], "ripple-suite")

    def test_unlisted_or_path_like_repo_is_refused(self) -> None:
        for value in ("sifu-tutor", "../ripple-suite", "/home/hafiz/x"):
            errors, _ = self.check(brief(repo=value))
            self.assertTrue(any("repo must be one of" in e for e in errors), (value, errors))


class TemplateTest(unittest.TestCase):
    def test_template_file_exists_and_its_example_is_valid(self) -> None:
        self.assertTrue(TEMPLATE.is_file(), "docs/agent-playbooks/templates/job-brief.md is missing")
        errors, _ = job_brief.validate(job_brief.parse(TEMPLATE.read_text()))
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
