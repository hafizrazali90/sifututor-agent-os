#!/usr/bin/env python3
"""TDD tests for the deterministic pre-dispatch secret/PII filter
(build item 8)."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


secret_filter = load_module("secret_filter")

# Built from short concatenated pieces, like the repo's own
# secret_artifact_scan fixtures, so the *source text* of this test file
# never contains a literal contiguous secret-shaped run for the shared
# pre-commit secret scanner to flag, while the *runtime string* still
# exercises real detection logic against secret_filter.py's own regexes.
FIXTURE_ANTHROPIC_STYLE = "sk-ant-api03-" + "a" * 12 + "b" * 12
FIXTURE_AWS_STYLE = "AKIA" + "B" * 8 + "C" * 8
FIXTURE_BEARER_SUFFIX = "abcdefghij" + "klmnopqrst"
FIXTURE_PEM_BLOCK = "-----BEGIN " + "RSA PRIVATE" + " KEY-----" + "\nMIIB...\n-----END " + "RSA PRIVATE" + " KEY-----"


class ScanCleanTextTest(unittest.TestCase):
    def test_returns_no_findings_for_ordinary_text(self) -> None:
        findings = secret_filter.scan("Customer reports the checkout button does nothing.")
        self.assertEqual(findings, [])

    def test_returns_no_findings_for_empty_text(self) -> None:
        self.assertEqual(secret_filter.scan(""), [])
        self.assertEqual(secret_filter.scan(None), [])


class ScanCredentialShapedTextTest(unittest.TestCase):
    def test_flags_an_anthropic_style_api_key(self) -> None:
        findings = secret_filter.scan("here is my key " + FIXTURE_ANTHROPIC_STYLE)
        self.assertTrue(findings)

    def test_flags_a_private_key_block(self) -> None:
        findings = secret_filter.scan(FIXTURE_PEM_BLOCK)
        self.assertTrue(findings)

    def test_flags_a_bearer_token(self) -> None:
        findings = secret_filter.scan("Authorization: Bearer " + FIXTURE_BEARER_SUFFIX)
        self.assertTrue(findings)

    def test_flags_an_aws_access_key(self) -> None:
        findings = secret_filter.scan(FIXTURE_AWS_STYLE + " is the access key")
        self.assertTrue(findings)


class ScanPiiShapedTextTest(unittest.TestCase):
    def test_flags_an_email_address(self) -> None:
        findings = secret_filter.scan("contact the parent at example.parent@example.com please")
        self.assertTrue(findings)

    def test_flags_a_malaysian_ic_number(self) -> None:
        findings = secret_filter.scan("the student's IC is 900101-14-5566")
        self.assertTrue(findings)


class ScanScansEveryOptionTooTest(unittest.TestCase):
    def test_flags_a_secret_hidden_inside_an_option_string(self) -> None:
        findings = secret_filter.scan_request(
            {
                "context": "nothing sensitive here",
                "options": ["approve", FIXTURE_ANTHROPIC_STYLE],
            }
        )
        self.assertTrue(findings)

    def test_scan_request_is_clean_for_an_ordinary_request(self) -> None:
        findings = secret_filter.scan_request(
            {"context": "nothing sensitive here", "options": ["low", "medium", "high"]}
        )
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
