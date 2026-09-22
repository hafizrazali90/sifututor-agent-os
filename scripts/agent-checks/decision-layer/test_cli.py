#!/usr/bin/env python3
"""TDD tests for the decision-layer CLI (build item 2).

These run the CLI as a real subprocess over stdin/stdout, the same way a
future caller would, and never set a live provider API key -- so no test
here can reach a network endpoint.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
CLI_PATH = HERE / "cli.py"


def run_cli(payload, env_overrides=None):
    import os

    env = dict(os.environ)
    env.pop("JEV_API_KEY", None)
    env.pop("JEV_BASE_URL", None)
    if env_overrides:
        env.update(env_overrides)
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [sys.executable, str(CLI_PATH)],
        input=stdin,
        text=True,
        capture_output=True,
        env=env,
        timeout=10,
    )


def valid_request(**overrides):
    request = {
        "schema_version": 1,
        "decision_type": "triage.priority",
        "options": ["low", "medium", "high"],
        "context": "Customer reports a broken checkout button.",
        "sensitivity": "low",
    }
    request.update(overrides)
    return request


class CliNormalRoundTripTest(unittest.TestCase):
    """Proof: normal round trip through the fake provider, end to end."""

    def test_exits_zero_and_prints_a_well_formed_response(self) -> None:
        result = run_cli(valid_request())
        self.assertEqual(result.returncode, 0, result.stderr)
        response = json.loads(result.stdout)
        self.assertEqual(response["outcome"], "ok")
        self.assertEqual(response["provider"], "fake")
        self.assertFalse(response["authoritative"])


class CliBadInputTest(unittest.TestCase):
    """Proof: a clear non-zero-exit error path for bad input."""

    def test_invalid_json_exits_nonzero(self) -> None:
        result = run_cli("{not json")
        self.assertNotEqual(result.returncode, 0)

    def test_schema_invalid_request_exits_nonzero(self) -> None:
        result = run_cli({"schema_version": 1})
        self.assertNotEqual(result.returncode, 0)

    def test_bad_input_still_prints_parseable_json(self) -> None:
        result = run_cli({"schema_version": 1})
        parsed = json.loads(result.stdout)
        self.assertIn("error", parsed)


class CliSecretBlockedTest(unittest.TestCase):
    def test_secret_shaped_context_is_blocked_end_to_end(self) -> None:
        # Built from short concatenated pieces so this file's source text
        # never contains a literal contiguous secret-shaped run (same
        # convention as the repo's own secret_artifact_scan fixtures).
        fixture_key = "sk-ant-api03-" + "a" * 12 + "b" * 12
        result = run_cli(valid_request(context="my key is " + fixture_key))
        self.assertEqual(result.returncode, 0)
        response = json.loads(result.stdout)
        self.assertEqual(response["outcome"], "blocked")


if __name__ == "__main__":
    unittest.main()
