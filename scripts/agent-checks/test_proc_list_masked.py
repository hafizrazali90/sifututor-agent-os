#!/usr/bin/env python3
"""Tests for scripts/agent-access/proc-list-masked.sh (issue #321, decision C).

The wrapper prints pid, user, elapsed time and the full command line with
secret-looking values masked. All secrets below are made-up placeholders.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[2]
WRAPPER = ROOT / "scripts" / "agent-access" / "proc-list-masked.sh"


def mask(*lines: str, pattern: str = "") -> str:
    argv = [str(WRAPPER), "--mask-stdin"] + ([pattern] if pattern else [])
    result = subprocess.run(
        argv, input="\n".join(lines) + "\n", text=True, capture_output=True, check=False
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


class MaskingRulesTest(unittest.TestCase):
    def assert_masked(self, line: str, secret: str, expected: str | None = None) -> None:
        out = mask(line)
        self.assertNotIn(secret, out, line)
        self.assertIn("***", out, line)
        if expected is not None:
            self.assertIn(expected, out)

    def test_database_client_password_forms(self) -> None:
        self.assert_masked("10 u 1 mysql -h db -u root -pHUNTER2pw app", "HUNTER2pw", "-p*** app")
        self.assert_masked("10 u 1 mysql -u root -p HUNTER2pw app", "HUNTER2pw", "-p *** app")
        self.assert_masked("10 u 1 /usr/bin/mysqldump -pHUNTER2pw db", "HUNTER2pw")
        self.assert_masked("10 u 1 mariadb -u a -pHUNTER2pw", "HUNTER2pw")

    def test_long_flags(self) -> None:
        for flag in ("--password=Zq9xK2", "--token=Zq9xK2", "--secret=Zq9xK2", "--api-key=Zq9xK2"):
            with self.subTest(flag=flag):
                self.assert_masked(f"11 u 1 app {flag} run", "Zq9xK2", "run")
        self.assert_masked("11 u 1 app --password Zq9xK2 run", "Zq9xK2", "run")
        self.assert_masked('11 u 1 app --password="two words" run', "two words", "run")

    def test_authorization_headers(self) -> None:
        self.assert_masked("12 u 1 curl -H 'Authorization: Bearer abc.DEF-123_xyz' https://x.test", "abc.DEF-123_xyz", "https://x.test")
        self.assert_masked("12 u 1 curl -H Authorization:Basic dXNlcjpwdw== https://x.test", "dXNlcjpwdw==")
        self.assert_masked("12 u 1 tool Bearer abcdefghijklmnop run", "abcdefghijklmnop")

    def test_credentials_inside_urls(self) -> None:
        for scheme in ("postgres", "mysql", "https"):
            with self.subTest(scheme=scheme):
                out = mask(f"13 u 1 tool {scheme}://admin:topS3cret@db.test:5432/app")
                self.assertNotIn("topS3cret", out)
                self.assertIn(f"{scheme}://admin:***@db.test:5432/app", out)

    def test_long_tokens_after_key_like_flags(self) -> None:
        self.assert_masked("14 u 1 tool --access-key AKIAABCDEFGHIJKLMNOP1234 go", "AKIAABCDEFGHIJKLMNOP1234", "go")
        self.assert_masked("14 u 1 tool --auth-key=0123456789abcdef0123456789abcdef go", "0123456789abcdef0123456789abcdef")

    def test_secret_looking_key_value_pairs(self) -> None:
        for pair in ("DB_PASSWORD=Zq9xK2", "API_KEY=Zq9xK2", "GITHUB_TOKEN=Zq9xK2", "CLIENT_SECRET=Zq9xK2", "PGPASSWORD=Zq9xK2", "MYSQL_PWD=Zq9xK2"):
            with self.subTest(pair=pair):
                self.assert_masked(f"15 u 1 env {pair} node app.js", "Zq9xK2", "node app.js")

    def test_ordinary_command_lines_are_untouched(self) -> None:
        for line in (
            "20 u 00:01 php artisan queue:work --queue=default --tries=3",
            "21 u 00:02 node server.js --port=3000 NODE_ENV=production",
            "22 u 00:03 /usr/sbin/php-fpm: pool www",
            "23 u 00:04 mysql -h db -u root app",
            "24 u 00:05 ssh -p 2222 deploy@host",
        ):
            with self.subTest(line=line):
                self.assertEqual(mask(line).strip(), line)

    def test_pattern_filters_the_masked_line_and_cannot_probe_a_hidden_value(self) -> None:
        lines = ("30 u 1 app --token=Zq9xK2 a", "31 u 1 other b")
        self.assertIn("app --token=***", mask(*lines, pattern="app"))
        self.assertNotIn("other", mask(*lines, pattern="app"))
        self.assertEqual(mask(*lines, pattern="Zq9xK2").strip(), "")

    def test_negative_control_unmasked_listing_would_leak(self) -> None:
        """The leak checks below only mean something if a raw listing does leak."""

        raw = "40 u 1 mysql -u root -pHUNTER2pw db"
        self.assertIn("HUNTER2pw", raw)
        self.assertNotIn("HUNTER2pw", mask(raw))


class LiveRunTest(unittest.TestCase):
    def test_live_listing_masks_real_processes(self) -> None:
        fakes = ("LIVEFAKEpw123", "0123456789abcdef0123456789abcdef", "liveurlpw99")
        with tempfile.TemporaryDirectory() as tmp:
            fake_mysql = Path(tmp) / "mysql"
            fake_mysql.write_text("#!/bin/sh\nsleep 20\n")
            fake_mysql.chmod(0o755)
            first = subprocess.Popen([str(fake_mysql), "-u", "root", f"-p{fakes[0]}", "appdb"])
            second = subprocess.Popen(
                [
                    "python3", "-c", "import time; time.sleep(20)",
                    f"--token={fakes[1]}", f"postgres://app:{fakes[2]}@db.test/app",
                ]
            )
            try:
                time.sleep(1.0)
                raw = subprocess.run(
                    ["ps", "-axo", "command="], text=True, capture_output=True, check=False
                ).stdout
                for fake in fakes:
                    self.assertIn(fake, raw, "control: the raw process list shows the fake secret")
                result = subprocess.run(
                    [str(WRAPPER), "time.sleep|mysql"], text=True, capture_output=True, check=False
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                for fake in fakes:
                    self.assertNotIn(fake, result.stdout)
                self.assertIn("-p*** appdb", result.stdout)
                self.assertIn("--token=***", result.stdout)
                self.assertIn("postgres://app:***@db.test/app", result.stdout)
                self.assertIn("PID", result.stdout.splitlines()[0])
            finally:
                for process in (first, second):
                    process.kill()
                    process.wait()


class GuardAllowsWrapperTest(unittest.TestCase):
    def test_guard_allows_the_wrapper_and_still_blocks_raw_listings(self) -> None:
        import importlib.util
        import sys

        spec = importlib.util.spec_from_file_location(
            "guard_for_wrapper_test", ROOT / "scripts" / "agent-checks" / "secret_output_guard.py"
        )
        guard = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = guard
        spec.loader.exec_module(guard)
        for command in (
            "scripts/agent-access/proc-list-masked.sh",
            "scripts/agent-access/proc-list-masked.sh php-fpm",
            "bash scripts/agent-access/proc-list-masked.sh 'worker|queue'",
        ):
            self.assertTrue(guard.evaluate_command(command).allowed, command)
        for command in ("ps -ef", "ps aux", "ps -o command", "ps -axo pid,command", "ps -o args"):
            decision = guard.evaluate_command(command)
            self.assertFalse(decision.allowed, command)
            self.assertIn("proc-list-masked.sh", decision.reason)


if __name__ == "__main__":
    unittest.main()
