#!/usr/bin/env python3
"""TDD tests for the comment_triage signal (Bundle 5 signal 5 of 8).

Required fixture: review comment triage (which comments look blocking vs
informational).
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import comment_triage  # noqa: E402


class NoCommentsTest(unittest.TestCase):
    def test_is_low_priority(self) -> None:
        record = comment_triage.classify({"review_comments": []})
        self.assertEqual(record["priority"], "low")


class BlockingCommentTest(unittest.TestCase):
    def test_a_must_fix_comment_is_high_priority(self) -> None:
        payload = {"review_comments": [{"author": "codex", "body": "This must be fixed before merge: the refund amount can go negative."}]}
        record = comment_triage.classify(payload)
        self.assertEqual(record["priority"], "high")
        self.assertIn("blocking_comment:codex", record["flags"])

    def test_requesting_changes_is_blocking(self) -> None:
        payload = {"review_comments": [{"author": "hafiz", "body": "Requesting changes: please add a null check here."}]}
        record = comment_triage.classify(payload)
        self.assertEqual(record["priority"], "high")


class InformationalCommentTest(unittest.TestCase):
    def test_a_nit_comment_is_low_priority(self) -> None:
        payload = {"review_comments": [{"author": "codex", "body": "nit: consider renaming this variable for clarity."}]}
        record = comment_triage.classify(payload)
        self.assertEqual(record["priority"], "low")
        self.assertEqual(record["flags"], [])

    def test_lgtm_is_low_priority(self) -> None:
        payload = {"review_comments": [{"author": "hafiz", "body": "LGTM, nice work."}]}
        record = comment_triage.classify(payload)
        self.assertEqual(record["priority"], "low")


class UnclearCommentTest(unittest.TestCase):
    def test_an_unrecognized_comment_is_reported_unclear_not_guessed(self) -> None:
        payload = {"review_comments": [{"author": "someone", "body": "Interesting approach here."}]}
        record = comment_triage.classify(payload)
        self.assertEqual(record["priority"], "medium")
        self.assertIn("unclear_comment:someone", record["flags"])


class MixedCommentsBlockingWinsTest(unittest.TestCase):
    def test_one_blocking_comment_outranks_an_informational_one(self) -> None:
        payload = {
            "review_comments": [
                {"author": "codex", "body": "nit: minor style thing"},
                {"author": "hafiz", "body": "This must be fixed before merge."},
            ]
        }
        record = comment_triage.classify(payload)
        self.assertEqual(record["priority"], "high")
        self.assertIn("blocking_comment:hafiz", record["flags"])


if __name__ == "__main__":
    unittest.main()
