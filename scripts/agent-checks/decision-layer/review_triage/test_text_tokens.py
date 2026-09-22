#!/usr/bin/env python3
"""TDD tests for the shared text_tokens helper used by file_risk and
scope_creep."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import text_tokens  # noqa: E402


class TokensTest(unittest.TestCase):
    def test_splits_camel_case_identifiers(self) -> None:
        self.assertEqual(
            text_tokens.tokens("InvoiceRefundService.php"),
            {"invoice", "refund", "service", "php"},
        )

    def test_splits_path_separators_and_punctuation(self) -> None:
        self.assertEqual(
            text_tokens.tokens("database/migrations/2026_09_22_add_payout_index.php"),
            {"database", "migrations", "2026", "09", "22", "add", "payout", "index", "php"},
        )

    def test_does_not_split_a_plain_lowercase_word(self) -> None:
        self.assertEqual(text_tokens.tokens("author.tsx"), {"author", "tsx"})

    def test_empty_string_yields_no_tokens(self) -> None:
        self.assertEqual(text_tokens.tokens(""), set())


if __name__ == "__main__":
    unittest.main()
