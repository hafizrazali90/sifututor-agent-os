#!/usr/bin/env python3
"""TDD tests for the ci_failure signal (Bundle 5 signal 4 of 8).

Required fixture: CI failure category (flaky vs real), including the case
where the distinction is genuinely not inferable from the input given.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import ci_failure  # noqa: E402


class NoFailuresTest(unittest.TestCase):
    def test_all_passed_is_low_priority(self) -> None:
        payload = {"ci_results": [{"job": "unit", "status": "passed", "failure_text": ""}]}
        record = ci_failure.classify(payload)
        self.assertEqual(record["priority"], "low")
        self.assertEqual(record["flags"], [])


class FlakyFailureTest(unittest.TestCase):
    def test_a_timeout_failure_is_categorized_flaky(self) -> None:
        payload = {"ci_results": [{"job": "e2e", "status": "failed", "failure_text": "Test timed out after 30000ms waiting for selector"}]}
        record = ci_failure.classify(payload)
        self.assertIn("ci_failure_flaky:e2e", record["flags"])
        self.assertEqual(record["priority"], "medium")

    def test_econnreset_is_categorized_flaky(self) -> None:
        payload = {"ci_results": [{"job": "integration", "status": "failed", "failure_text": "Error: ECONNRESET while fetching dependency"}]}
        record = ci_failure.classify(payload)
        self.assertIn("ci_failure_flaky:integration", record["flags"])


class RealFailureTest(unittest.TestCase):
    def test_an_assertion_failure_is_categorized_real_and_high_priority(self) -> None:
        payload = {"ci_results": [{"job": "unit", "status": "failed", "failure_text": "AssertionError: expected 100 to equal 90"}]}
        record = ci_failure.classify(payload)
        self.assertIn("ci_failure_real:unit", record["flags"])
        self.assertEqual(record["priority"], "high")

    def test_a_typeerror_is_categorized_real(self) -> None:
        payload = {"ci_results": [{"job": "unit", "status": "failed", "failure_text": "TypeError: cannot read property 'amount' of undefined"}]}
        record = ci_failure.classify(payload)
        self.assertIn("ci_failure_real:unit", record["flags"])


class NotInferableTest(unittest.TestCase):
    """The category must not be guessed when the input gives no real
    signal either way."""

    def test_unrecognized_failure_text_is_reported_unknown_not_guessed(self) -> None:
        payload = {"ci_results": [{"job": "deploy", "status": "failed", "failure_text": "job exited with code 17"}]}
        record = ci_failure.classify(payload)
        self.assertIn("ci_failure_unknown:deploy", record["flags"])
        self.assertNotIn("ci_failure_flaky:deploy", record["flags"])
        self.assertNotIn("ci_failure_real:deploy", record["flags"])


class MixedFailuresRealWinsPriorityTest(unittest.TestCase):
    def test_a_real_failure_alongside_a_flaky_one_is_still_high_priority(self) -> None:
        payload = {
            "ci_results": [
                {"job": "e2e", "status": "failed", "failure_text": "connection reset by peer"},
                {"job": "unit", "status": "failed", "failure_text": "AssertionError: expected true to be false"},
            ]
        }
        record = ci_failure.classify(payload)
        self.assertEqual(record["priority"], "high")
        self.assertIn("ci_failure_flaky:e2e", record["flags"])
        self.assertIn("ci_failure_real:unit", record["flags"])


if __name__ == "__main__":
    unittest.main()
