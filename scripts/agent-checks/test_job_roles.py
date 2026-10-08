#!/usr/bin/env python3
"""The role files must exist, stay short, and say the things that make them safe."""

from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
ROLES = ROOT / "docs" / "agent-playbooks" / "job-roles"
FILES = ("shared-facts.md", "builder.md", "reviewer.md")
MAX_LINES = 45


def read(name: str) -> str:
    return (ROLES / name).read_text()


class JobRolesTest(unittest.TestCase):
    def test_files_exist_and_are_short(self) -> None:
        for name in FILES:
            with self.subTest(name=name):
                self.assertTrue((ROLES / name).is_file(), f"{name} is missing")
                self.assertLessEqual(len(read(name).splitlines()), MAX_LINES)

    def test_no_em_dashes(self) -> None:
        for name in FILES:
            with self.subTest(name=name):
                self.assertNotIn("—", read(name))

    def test_shared_facts_hold_the_safety_rules(self) -> None:
        text = read("shared-facts.md")
        for needle in ("never merge or deploy", "`.env*`", "--no-verify", "MYT", "AGENTS.md"):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)

    def test_builder_is_bound_to_its_paths_and_does_not_push(self) -> None:
        text = read("builder.md")
        self.assertIn("allowed_paths", text)
        self.assertIn("Do not push", text)

    def test_reviewer_is_read_only_and_skeptical(self) -> None:
        text = read("reviewer.md")
        self.assertIn("read-only", text)
        self.assertIn("Assume it is wrong", text)
        self.assertIn("ACCEPT, CHANGES NEEDED, or BLOCKED", text)


if __name__ == "__main__":
    unittest.main()
