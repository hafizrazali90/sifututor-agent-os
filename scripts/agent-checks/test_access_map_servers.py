#!/usr/bin/env python3
"""The access map is the one place for server aliases; keep its two mentions consistent."""

from __future__ import annotations

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
TEXT = (ROOT / "docs" / "agent-playbooks" / "agent-access-map.md").read_text()


def section() -> str:
    start = TEXT.index("## Servers, Zones And Paths")
    return TEXT[start:TEXT.index("\n## ", start + 5)]


class AccessMapServersTest(unittest.TestCase):
    def test_every_alias_has_a_row(self) -> None:
        body = section()
        for alias in ("production", "staging", "finch", "webvoyager"):
            with self.subTest(alias=alias):
                self.assertRegex(body, rf"\| `{alias}` \|")

    def test_webvoyager_is_marked_dead(self) -> None:
        row = next(line for line in section().splitlines() if "| `webvoyager` |" in line)
        self.assertIn("Dead since", row)

    def test_lane_12_staging_alias_is_finch_not_the_dead_host(self) -> None:
        row = next(line for line in TEXT.splitlines() if line.startswith("| **Staging alias**"))
        self.assertIn("`finch`", row)
        self.assertNotRegex(row, r"`webvoyager` +→")

    def test_staging_means_the_finch_box(self) -> None:
        self.assertIn("sifu-staging.tutorla.tech", section())
        self.assertIn("not Web Voyager", section())

    def test_no_credential_values_in_the_section(self) -> None:
        body = section()
        self.assertNotRegex(body, r"(?i)(password|secret|token)\s*[:=]\s*\S+")
        self.assertIn("never printed", body)

    def test_no_em_dashes_in_the_new_section(self) -> None:
        self.assertNotIn("—", section())


if __name__ == "__main__":
    unittest.main()
