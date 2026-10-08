#!/usr/bin/env python3
"""The file-mode checks in the access scripts must work with Mac and Linux stat.

On Linux (GNU), `stat -f` means "file system status" and prints several lines
before failing on the format string, so trying the Mac form first poisons the
captured value. These tests run the real `stat` expression from each script
against small fake `stat` programs that behave like each system.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
ACCESS = ROOT / "scripts" / "agent-access"
SCRIPTS = (
    "ripple-destination-readonly-run.sh",
    "check-ripple-destination-readonly.sh",
    "agent-access-doctor.sh",
)
EXPR = re.compile(r"\$\((stat .*?)\)")

GNU_STAT = """#!/bin/sh
# behaves like GNU stat: -c FORMAT works; -f is file-system status, noisy and failing
if [ "$1" = "-c" ]; then echo 600; exit 0; fi
if [ "$1" = "-f" ]; then
  echo '  File: "x"'; echo '    ID: 1 Namelen: 255 Type: ext4'
  echo "stat: cannot read file system information for '%Lp'" >&2; exit 1
fi
exit 1
"""

BSD_STAT = """#!/bin/sh
# behaves like BSD/macOS stat: -f FORMAT works; -c is an illegal option
if [ "$1" = "-f" ]; then echo 600; exit 0; fi
echo "stat: illegal option -- c" >&2; exit 1
"""


def extract_expression(script: str) -> str:
    for line in (ACCESS / script).read_text().splitlines():
        if "stat " in line and "%Lp" in line:
            match = EXPR.search(line)
            if match:
                return match.group(1)
    raise AssertionError(f"no stat expression found in {script}")


def run_expression(expression: str, fake_stat: str) -> str:
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        stat = tmp / "stat"
        stat.write_text(fake_stat)
        stat.chmod(0o755)
        env = {"PATH": f"{tmp}:/usr/bin:/bin", "CONF": "/x", "SHAREPOINT_CONFIG": "/x"}
        result = subprocess.run(
            ["sh", "-c", f'printf "%s" "$({expression})"'],
            env=env, capture_output=True, text=True, check=False,
        )
        return result.stdout


class StatModePortabilityTest(unittest.TestCase):
    def test_each_script_reads_mode_600_on_linux_stat(self) -> None:
        for script in SCRIPTS:
            with self.subTest(script=script):
                self.assertEqual(run_expression(extract_expression(script), GNU_STAT), "600")

    def test_each_script_reads_mode_600_on_mac_stat(self) -> None:
        for script in SCRIPTS:
            with self.subTest(script=script):
                self.assertEqual(run_expression(extract_expression(script), BSD_STAT), "600")


if __name__ == "__main__":
    unittest.main()
