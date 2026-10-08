#!/usr/bin/env python3
"""Structure checks for the rejected-ideas ledger, the glossary and the decisions folder."""

from __future__ import annotations

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / ".out-of-scope"
DECISIONS = ROOT / "docs" / "decisions"
GLOSSARY = ROOT / "GLOSSARY.md"
EM_DASH = "—"
DATE = re.compile(r"\b\d{2}/\d{2}/\d{4}\b")

LEDGER_HEADINGS = ("## What was proposed", "## Why it is out of scope", "## What would change our mind", "## Decided")
DECISION_HEADINGS = ("## Context", "## Decision", "## Why", "## What we gave up", "## Revisit if")


def entries(folder: Path, pattern: str) -> list[Path]:
    return sorted(p for p in folder.glob(pattern) if p.name != "README.md")


class LedgerTest(unittest.TestCase):
    def test_every_entry_has_the_required_headings_and_a_date(self) -> None:
        files = entries(LEDGER, "*.md")
        self.assertGreaterEqual(len(files), 1)
        for path in files:
            text = path.read_text()
            with self.subTest(entry=path.name):
                self.assertTrue(text.startswith("# "))
                for heading in LEDGER_HEADINGS:
                    self.assertIn(heading, text)
                self.assertRegex(text.split("## Decided", 1)[1], DATE)

    def test_readme_lists_every_entry(self) -> None:
        readme = (LEDGER / "README.md").read_text()
        for path in entries(LEDGER, "*.md"):
            with self.subTest(entry=path.name):
                self.assertIn(f"({path.name})", readme)

    def test_no_em_dashes(self) -> None:
        for path in LEDGER.glob("*.md"):
            with self.subTest(entry=path.name):
                self.assertNotIn(EM_DASH, path.read_text())


class DecisionsTest(unittest.TestCase):
    def test_files_are_numbered_in_order_with_the_required_headings(self) -> None:
        files = entries(DECISIONS, "[0-9][0-9][0-9][0-9]-*.md")
        self.assertGreaterEqual(len(files), 1)
        numbers = [int(p.name[:4]) for p in files]
        self.assertEqual(numbers, list(range(1, len(files) + 1)), "numbers must run 0001, 0002, ... with no gaps")
        for path in files:
            text = path.read_text()
            with self.subTest(decision=path.name):
                self.assertTrue(text.startswith(f"# {path.name[:4]}: "))
                self.assertIn("Status:", text.splitlines()[2])
                self.assertRegex(text.splitlines()[2], DATE)
                for heading in DECISION_HEADINGS:
                    self.assertIn(heading, text)

    def test_readme_index_lists_every_decision(self) -> None:
        readme = (DECISIONS / "README.md").read_text()
        for path in entries(DECISIONS, "[0-9][0-9][0-9][0-9]-*.md"):
            with self.subTest(decision=path.name):
                self.assertIn(f"({path.name})", readme)

    def test_no_em_dashes(self) -> None:
        for path in DECISIONS.glob("*.md"):
            with self.subTest(decision=path.name):
                self.assertNotIn(EM_DASH, path.read_text())


class GlossaryTest(unittest.TestCase):
    def rows(self) -> list[list[str]]:
        rows = []
        for line in GLOSSARY.read_text().splitlines():
            if line.startswith("|") and not line.startswith("| ---") and not line.startswith("| Term"):
                rows.append([cell.strip() for cell in line.strip("|").split("|")])
        return rows

    def test_glossary_has_terms_with_say_and_do_not_say(self) -> None:
        rows = self.rows()
        self.assertGreaterEqual(len(rows), 10)
        for row in rows:
            with self.subTest(term=row[0]):
                self.assertEqual(len(row), 4)
                self.assertTrue(all(row), "every cell must be filled")

    def test_glossary_holds_no_code_details(self) -> None:
        text = GLOSSARY.read_text()
        self.assertNotRegex(text, r"`[a-z]+_[a-z_]+`", "no snake_case table or field names")
        self.assertNotIn(EM_DASH, text)

    def test_the_core_terms_are_present(self) -> None:
        text = GLOSSARY.read_text()
        for term in ("Tutor Request", "Nakngaji", "Kelasapp", "Sifututor", "Area", "staging"):
            with self.subTest(term=term):
                self.assertIn(term, text)

    def test_agents_md_points_to_the_glossary(self) -> None:
        self.assertIn("GLOSSARY.md", (ROOT / "AGENTS.md").read_text())


if __name__ == "__main__":
    unittest.main()
