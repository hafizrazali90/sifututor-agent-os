#!/usr/bin/env python3
"""Tests for scripts/agent-access/ripple-logs-readonly.sh (lane 45, issue #371).

Masking runs through --mask-stdin and the remote command through the dry-run switch, so nothing touches a server.
Every secret below is a made-up placeholder; long ones are built at run time so the source holds no credential shape.
"""

import os
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = Path(os.environ.get("RIPPLE_LOGS_SCRIPT", ROOT / "scripts/agent-access/ripple-logs-readonly.sh"))


def run(*args, stdin="", **env):
    e = dict(os.environ, RIPPLE_LOGS_DRY_RUN="1", **env)
    r = subprocess.run(["bash", str(SCRIPT), *args], input=stdin, capture_output=True, text=True, env=e)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def mask(*lines, args=()):
    code, out, err = run("--mask-stdin", *args, stdin="\n".join(lines) + "\n")
    assert code == 0, err
    return out


class RippleLogsMasking(unittest.TestCase):
    def assertHidden(self, line, secret, shown=None):
        out = mask(line)
        self.assertNotIn(secret, out, line)
        self.assertTrue(out, f"the error line was dropped: {line!r}")
        if shown is not None:
            self.assertIn(shown, out)

    def test_secret_values_tokens_and_passwords_are_masked(self):
        self.assertHidden("Error: token=tok3nValue9 rejected", "tok3nValue9", "token=***")
        self.assertHidden("error login failed password: plainpw77", "plainpw77", "password: ***")
        self.assertHidden('Error {"apiKey":"k9k9k9k9","client_secret":"cs-1-2-3"}', "k9k9k9k9")
        self.assertHidden('Error {"apiKey":"k9k9k9k9","client_secret":"cs-1-2-3"}', "cs-1-2-3")
        self.assertHidden("Error: session_id=abc999 expired", "abc999")

    def test_cookies_and_authorization_headers_are_masked(self):
        bearer = "Bearer " + "q1w2e3r4" * 3
        self.assertHidden(f"Error: request failed Authorization: {bearer}", "q1w2e3r4", "Authorization: ***")
        self.assertHidden('error headers {"authorization":"Basic dXNlcjpwYXNz"}', "dXNlcjpwYXNz")
        self.assertHidden("Error Cookie: rs_session=s3ss10n; csrf=c5rf", "s3ss10n")
        self.assertHidden("Error Cookie: rs_session=s3ss10n; csrf=c5rf", "c5rf")
        self.assertHidden('Error set-cookie: "rs_session=s3ss10n; Path=/; HttpOnly"', "s3ss10n")

    def test_connection_urls_and_url_passwords_are_masked(self):
        url = "postgres" + "://ripple:pw4db@127.0.0.1:5432/ripple_suite_staging"
        self.assertHidden(f"Error: connect ECONNREFUSED {url}", "pw4db", "[connection-url]")
        self.assertHidden(f"Error: connect ECONNREFUSED {url}", "ripple_suite_staging")
        self.assertHidden("Error: redis" + "://:r3dispw@cache:6379/0 down", "r3dispw")
        self.assertHidden("Error fetching https" + "://svc:httppw1@api.example.test/v1", "httppw1")

    def test_jwts_and_long_opaque_tokens_are_masked(self):
        jwt = "eyJ" + "hbGciOiJIUzI1NiJ9" + "." + "eyJzdWIiOiIxMjM0NSJ9" + "." + "c2lnbmF0dXJl"
        self.assertHidden(f"Error: invalid jwt {jwt}", "c2lnbmF0dXJl", "[token]")
        opaque = "A1b2C3d4" * 5
        self.assertHidden(f"Error: unknown key {opaque}", opaque, "[token]")

    def test_phone_numbers_and_emails_are_masked(self):
        for phone in ("+60 12-345 6789", "+60123456789", "012-345 6789", "0123456789", "60123456789", "03-1234 5678"):
            self.assertHidden(f"Error: SMS failed for {phone} today", phone, "[phone]")
        self.assertHidden("Error: no tutor for ali.bin.abu@example.test", "ali.bin.abu@example.test", "[email]")

    def test_ids_commits_ports_and_times_stay_readable(self):
        line = ("2026-10-13T08:00:00Z Error: request 3f2b1c4d-1111-2222-3333-444455556666 on :3201 commit "
                + "a" * 40 + " digest 2834567")
        out = mask(line)
        self.assertEqual(out, line)

    def test_only_error_level_lines_are_kept_and_stack_frames_are_dropped(self):
        out = mask("info: ready on 3201", "GET /requests 200 in 12ms", " ⨯ Error: client reference manifest does not exist",
                   "    at Object.handler (/var/www/x.js:10:5)", "TypeError: Cannot read properties of undefined",
                   "Unhandled Rejection at promise", "warn: slow query").splitlines()
        self.assertEqual([l.strip() for l in out], ["⨯ Error: client reference manifest does not exist", "TypeError: Cannot read properties of undefined",
                               "Unhandled Rejection at promise"])

    def test_at_most_n_lines_newest_last(self):
        lines = [f"Error number {i}" for i in range(100)]
        self.assertEqual(mask(*lines, args=("--lines", "3")).splitlines(), ["Error number 97", "Error number 98", "Error number 99"])
        self.assertEqual(len(mask(*lines).splitlines()), 30)
        self.assertEqual(len(mask(*lines, args=("--lines", "60")).splitlines()), 60)

    def test_the_pattern_is_matched_against_the_masked_line(self):
        lines = ["Error: token=hidd3n value", "Error: other failure"]
        self.assertEqual(mask(*lines, args=("--pattern", "hidd3n")), "")
        self.assertEqual(mask(*lines, args=("--pattern", "other")), "Error: other failure")


class RippleLogsArguments(unittest.TestCase):
    def test_remote_command_reads_a_bounded_tail_as_the_deploy_account(self):
        code, out, _ = run("staging")
        self.assertEqual((code, out), (0, "runuser -u deploy -- tail -n 400 /home/deploy/.pm2/logs/ripple-suite-staging-error.log"))
        code, out, _ = run("prod", "--lines", "5")
        self.assertEqual((code, out), (0, "runuser -u deploy -- tail -n 400 /home/deploy/.pm2/logs/ripple-suite-prod-error.log"))

    def test_it_never_reads_the_environment_or_pm2_settings(self):
        text = SCRIPT.read_text()
        code_only = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))
        for word in ("pm2 env", "pm2 jlist", "printenv", "/proc/", ".env", "pm2 show", "pm2 describe"):
            self.assertNotIn(word, code_only, word)
        self.assertIn("ssh -o BatchMode=yes", code_only)

    def test_unknown_targets_and_arguments_are_refused(self):
        self.assertEqual(run("production")[0], 2)
        self.assertEqual(run("sims")[0], 2)
        self.assertEqual(run()[0], 2)
        for args in (["--follow"], ["--lines"], ["extra"], ["--lines", "5", "--env"], ["-n", "5"]):
            code, _, err = run("staging", *args)
            self.assertIn(code, (2, 3), args)
            self.assertNotIn("runuser", err)

    def test_line_counts_are_bounded_numbers(self):
        for bad in ("0", "61", "400", "abc", "5;id", "-1", "$(id)"):
            code, out, err = run("staging", "--lines", bad)
            self.assertEqual(code, 3, bad)
            self.assertTrue(err.startswith("refused:"), bad)
            self.assertEqual(out, "")

    def test_a_bad_pattern_or_alias_is_refused_before_ssh(self):
        code, out, err = run("staging", "--pattern", "(")
        self.assertEqual((code, out), (3, ""))
        self.assertIn("not a valid regular expression", err)
        self.assertEqual(run("staging", "--pattern", "x" * 201)[0], 3)
        self.assertEqual(run("staging", RIPPLE_LOGS_SSH_ALIAS="a b")[0], 3)


if __name__ == "__main__":
    unittest.main()
