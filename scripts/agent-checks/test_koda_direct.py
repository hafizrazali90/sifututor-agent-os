#!/usr/bin/env python3
"""Regression tests for the koda-direct.py compatibility entry point."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent


def load_helper():
    path = HERE / "koda-direct.py"
    spec = importlib.util.spec_from_file_location("koda_direct", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class KodaDirectCompatibilityTests(unittest.TestCase):
    def test_forwards_arguments_to_the_canonical_helper(self):
        helper = load_helper()
        argv = ["koda-direct.py", "--check-koda", "--write-check"]

        with patch.object(sys, "argv", argv), patch.object(
            helper.os, "execv", side_effect=RuntimeError("process replaced")
        ) as execv:
            with self.assertRaisesRegex(RuntimeError, "process replaced"):
                helper.main()

        execv.assert_called_once_with(
            sys.executable,
            [sys.executable, str(helper.CANONICAL_HELPER), *argv[1:]],
        )


if __name__ == "__main__":
    unittest.main()
