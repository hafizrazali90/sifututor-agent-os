#!/usr/bin/env python3
"""Tests for the SIMS read-only lane's MySQL client choice (#340).

Homebrew's MySQL 9.x client dropped the mysql_native_password plugin that the
SIMS read-only account signs in with, so the lane must prefer an installed 8.x
client and, when a connection fails, say the real reason instead of blaming a
firewall. Fake `mysql` executables stand in for the real clients.
"""

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECK = ROOT / "scripts/agent-access/check-sims-db-readonly.sh"
LIB = ROOT / "scripts/agent-access/lib/mysql-client.sh"
FAKE_PASSWORD = "Fake-Pass-340"

OLD_CLIENT = """#!/usr/bin/env bash
# Behaves like a MySQL 8.4 client that can sign in.
for arg in "$@"; do
  case "$arg" in
    *CREATE\\ TABLE*) echo "ERROR 1142 (42000): CREATE command denied to user" >&2; exit 1 ;;
  esac
done
echo "active_tutors"
echo "1"
"""

NEW_CLIENT = """#!/usr/bin/env bash
# Behaves like Homebrew MySQL 9.7 against a mysql_native_password account.
echo "ERROR 2059 (HY000): Authentication plugin 'mysql_native_password' cannot be loaded: dlopen(/opt/homebrew/Cellar/mysql/9.7.1/lib/plugin/mysql_native_password.so, 0x0002): no such file" >&2
exit 1
"""


def write_exe(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


class MysqlClientTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.path_bin = self.tmp / "path-bin"
        write_exe(self.path_bin / "mysql", NEW_CLIENT)
        self.old = write_exe(self.tmp / "mysql84/bin/mysql", OLD_CLIENT)
        conf = self.tmp / "home/.config/sifututor/agent-access/database-readonly.conf"
        conf.parent.mkdir(parents=True)
        conf.write_text(
            "SIMS_DB_READONLY_HOST=db.example.test\n"
            "SIMS_DB_READONLY_PORT=3306\n"
            "SIMS_DB_READONLY_USERNAME=agent_readonly\n"
            f"SIMS_DB_READONLY_PASSWORD={FAKE_PASSWORD}\n"
            "SIMS_DB_READONLY_DATABASE=sims\n"
        )

    def env(self, candidates):
        return dict(
            os.environ,
            HOME=str(self.tmp / "home"),
            PATH=f"{self.path_bin}:/usr/bin:/bin",
            SIFU_MYSQL_CANDIDATES=":".join(str(c) for c in candidates),
        )

    def pick(self, candidates, extra=None):
        env = self.env(candidates)
        env.update(extra or {})
        return subprocess.run(
            ["bash", "-c", f'source "{LIB}"; sifu_mysql_client'],
            env=env, capture_output=True, text=True, check=False,
        )

    def test_prefers_an_installed_8x_client_over_the_path_client(self):
        result = self.pick([self.tmp / "missing/mysql", self.old])
        self.assertEqual(result.stdout.strip(), str(self.old))

    def test_falls_back_to_the_path_client_when_no_8x_client_exists(self):
        result = self.pick([self.tmp / "missing/mysql"])
        self.assertEqual(result.stdout.strip(), str(self.path_bin / "mysql"))

    def test_an_explicit_client_wins(self):
        result = self.pick([self.old], {"SIFU_MYSQL_CLIENT": str(self.path_bin / "mysql")})
        self.assertEqual(result.stdout.strip(), str(self.path_bin / "mysql"))

    def run_check(self, candidates):
        return subprocess.run(
            ["bash", str(CHECK)], env=self.env(candidates),
            capture_output=True, text=True, check=False,
        )

    def test_check_connects_with_the_8x_client(self):
        result = self.run_check([self.old])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Connection: OK", result.stdout)
        self.assertIn("Write permission correctly denied", result.stdout)
        self.assertNotIn(FAKE_PASSWORD, result.stdout + result.stderr)

    def test_check_names_the_missing_plugin_instead_of_a_firewall(self):
        result = self.run_check([self.tmp / "missing/mysql"])
        out = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("mysql_native_password", out)
        self.assertIn("brew install mysql@8.4", out)
        self.assertNotIn("firewalled", out)
        self.assertNotIn(FAKE_PASSWORD, out)


if __name__ == "__main__":
    unittest.main()
