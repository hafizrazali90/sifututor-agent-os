#!/usr/bin/env python3
"""Tests for the single Koda endpoint source (issue #163)."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

spec = importlib.util.spec_from_file_location("koda_endpoint", HERE / "koda_endpoint.py")
koda_endpoint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(koda_endpoint)


class ResolutionOrderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.conf = Path(self.tmp.name) / "koda.conf"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_environment_wins_over_conf_and_default(self) -> None:
        self.conf.write_text("KODA_MCP_URL=http://conf.invalid/mcp\n")
        self.assertEqual(
            koda_endpoint.resolve_koda_mcp_url(env={"KODA_MCP_URL": "http://env.invalid/mcp"}, conf_path=self.conf),
            "http://env.invalid/mcp",
        )

    def test_shared_conf_wins_over_default(self) -> None:
        self.conf.write_text("# shared lane\nKODA_MCP_URL = 'http://conf.invalid/mcp'\n")
        self.assertEqual(koda_endpoint.resolve_koda_mcp_url(env={}, conf_path=self.conf), "http://conf.invalid/mcp")

    def test_default_when_nothing_is_set(self) -> None:
        self.assertEqual(koda_endpoint.resolve_koda_mcp_url(env={}, conf_path=self.conf), "https://koda.tutorla.tech/mcp")

    def test_blank_env_and_unrelated_conf_keys_fall_through(self) -> None:
        self.conf.write_text("OTHER=1\nKODA_MCP_URL=\n")
        self.assertEqual(koda_endpoint.resolve_koda_mcp_url(env={"KODA_MCP_URL": "  "}, conf_path=self.conf), "https://koda.tutorla.tech/mcp")

    def test_module_never_touches_the_api_key(self) -> None:
        self.assertNotIn("KODA_API_KEY", (HERE / "koda_endpoint.py").read_text(encoding="utf-8").replace("`KODA_API_KEY`", ""))


class CallersUseTheSingleSourceTest(unittest.TestCase):
    def test_no_umbrella_helper_hardcodes_the_endpoint_any_more(self) -> None:
        root = HERE.parent.parent
        offenders = []
        for rel in ("scripts/agent-checks/koda-verify.py", "scripts/agent-checks/codex-lifecycle-hook.py", ".claude/hooks/koda-context-injector.py"):
            text = (root / rel).read_text(encoding="utf-8")
            if 'KODA_URL = "https://' in text:
                offenders.append(rel)
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
