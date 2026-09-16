#!/usr/bin/env python3
"""Tests for staged secret-artifact detection."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCANNER_PATH = ROOT / "scripts" / "agent-checks" / "secret_artifact_scan.py"


def load_scanner():
    spec = importlib.util.spec_from_file_location("secret_artifact_scan", SCANNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load secret artifact scanner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SecretArtifactScanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scanner = load_scanner()

    def test_detects_secret_shapes_without_returning_values(self) -> None:
        samples = [
            "ANTHROPIC_API_KEY=sk-ant-api03-" + "A" * 40,
            "GOOGLE_API_KEY=AIza" + "B" * 35,
            "Authorization: Bearer " + "C" * 36,
            "AWS_ACCESS_KEY_ID=AKIA" + "D" * 16,
            "-----BEGIN " + "PRIVATE KEY-----",
            "client_secret: " + "E" * 32,
            "QSTASH_CURRENT_SIGNING_KEY=" + "F" * 40,
            "DATABASE_URL=" + "postgresql://app:real-password@example.test/app",
        ]
        for sample in samples:
            with self.subTest(sample=sample[:12]):
                findings = self.scanner.find_secret_findings(sample)
                self.assertTrue(findings)
                rendered = " ".join(f.rule for f in findings)
                self.assertNotIn(sample, rendered)

    def test_allows_placeholders_and_documentation(self) -> None:
        safe = """
API_KEY=<redacted>
CLIENT_SECRET=your_client_secret_here
TOKEN=test-token
Use `pm2 jlist` only as an example of a blocked command.
"""
        self.assertEqual(self.scanner.find_secret_findings(safe), [])

    def test_placeholder_does_not_hide_a_real_secret_on_the_same_line(self) -> None:
        real_token = "sk-ant-api03-" + "Z" * 40
        findings = self.scanner.find_secret_findings(
            f"EXAMPLE_KEY=<redacted> ANTHROPIC_API_KEY={real_token}"
        )
        self.assertTrue(findings)
        self.assertNotIn(real_token, " ".join(f.rule for f in findings))


if __name__ == "__main__":
    unittest.main()
