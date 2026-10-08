#!/usr/bin/env python3
"""Tests for scripts/agent-access/lls-server-readonly.sh (lane 41). Dry-run only: nothing touches a server."""

import os
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = Path(os.environ.get("LLS_SERVER_SCRIPT", ROOT / "scripts/agent-access/lls-server-readonly.sh"))


def run(*args, **env):
    e = dict(os.environ, LLS_SERVER_DRY_RUN="1", **env)
    r = subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True, env=e)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


class LlsServerReadonly(unittest.TestCase):
    def test_read_commands_run_as_the_app_account_in_the_right_folder(self):
        code, out, _ = run("prod", "artisan", "about")
        self.assertEqual(code, 0)
        self.assertEqual(out, "cd /var/www/learnest && runuser -u www-data -- php artisan about")
        self.assertNotIn("root", out.replace("/var/www", ""))
        self.assertIn("/var/www/learnest-staging", run("staging", "artisan", "env")[1])
        self.assertIn("/var/www/learnest-develop", run("develop", "artisan", "route:list", "--json")[1])

    def test_allowed_flags_pass_and_are_appended(self):
        code, out, _ = run("prod", "artisan", "migrate:status", "--pending")
        self.assertEqual(code, 0)
        self.assertTrue(out.endswith("php artisan migrate:status --pending"))
        self.assertEqual(run("prod", "artisan", "route:list", "--path=api/v1", "--method=GET")[0], 0)

    def test_commands_that_could_write_or_print_settings_are_refused(self):
        for name in ["tinker", "migrate", "db:seed", "config:show", "queue:retry", "queue:flush", "down", "up",
                     "cache:clear", "optimize", "key:generate", "db:wipe", "migrate:fresh", "about; id"]:
            code, _, err = run("prod", "artisan", name)
            self.assertEqual(code, 3, name)
            self.assertTrue(err.startswith("refused:"), name)

    def test_unlisted_or_unsafe_flags_are_refused(self):
        for flag in ["--force", "--env=local", "--pretend", "--path=a;rm", "--path=$(id)", "--json;id", "-v"]:
            self.assertEqual(run("prod", "artisan", "about", flag)[0], 3, flag)

    def test_logs_are_bounded_numbers_read_as_the_app_account(self):
        code, out, _ = run("prod", "logs")
        self.assertEqual((code, out), (0, "runuser -u www-data -- tail -n 200 /var/www/learnest/storage/logs/laravel.log"))
        self.assertIn("tail -n 2000 ", run("prod", "logs", "2000")[1])
        for bad in ["0", "2001", "abc", "5;id", "-1"]:
            self.assertEqual(run("prod", "logs", bad)[0], 3, bad)

    def test_pm2_lists_names_and_status_only(self):
        code, out, _ = run("prod", "pm2")
        self.assertEqual(code, 0)
        self.assertIn("pm2 jlist", out)
        self.assertNotIn("env", out.split("python3")[0].replace("pm2_env", ""))

    def test_unknown_environment_or_action_is_refused(self):
        self.assertEqual(run("production", "artisan", "about")[0], 2)
        self.assertEqual(run("prod", "shell")[0], 2)
        self.assertEqual(run("prod")[0], 2)
        self.assertEqual(run("prod", "artisan", "about", LLS_SERVER_SSH_ALIAS="a b")[0], 3)


if __name__ == "__main__":
    unittest.main()
