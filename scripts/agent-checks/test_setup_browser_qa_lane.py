#!/usr/bin/env python3
"""Tests for scripts/agent-access/setup-sims-browser-qa-lane.sh (lane 39).

The script must work only in a real terminal, hide the password, write a mode
600 file that bash can source back to the same values, refuse non-staging
URLs, and never leave a half-written file. Each test drives the script through
a pseudo-terminal, because a piped run must be refused.
"""

import os
import pty
import select
import stat
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = Path(os.environ.get("QA_LANE_SCRIPT", ROOT / "scripts/agent-access/setup-sims-browser-qa-lane.sh"))
CONF_NAME = "sims-staging-browser-qa.conf"
FAKE_PASSWORD = "Zq9 $x \"q\" 'a' \\ ! `t` #end"
FAKE_EMAIL = "browser.qa@example.test"


def run_in_terminal(conf_dir, answers, timeout=20):
    """Run the script on a pty, sending each answer after its prompt appears.

    answers is a list of (prompt_substring, text). Returns (exit_code, output).
    """
    env = dict(os.environ, SIFUTUTOR_AGENT_ACCESS_DIR=str(conf_dir))
    pid, fd = pty.fork()
    if pid == 0:
        os.execvpe("bash", ["bash", str(SCRIPT)], env)
    output = b""
    pending = list(answers)
    deadline = time.time() + timeout
    status = None
    while time.time() < deadline:
        ready, _, _ = select.select([fd], [], [], 0.2)
        if ready:
            try:
                chunk = os.read(fd, 4096)
            except OSError:
                chunk = b""
            if not chunk:
                break
            output += chunk
            if pending and pending[0][0].encode() in output:
                _, text = pending.pop(0)
                time.sleep(0.1)
                os.write(fd, (text + "\n").encode())
                output += b"\0SENT\0"
    else:
        os.kill(pid, 9)
        os.waitpid(pid, 0)
        raise AssertionError(f"script stuck waiting; unanswered prompts: {[p for p, _ in pending]}")
    _, status = os.waitpid(pid, 0)
    return os.waitstatus_to_exitcode(status), output.decode(errors="replace")


FULL_ANSWERS = [
    ("Staging URL", ""),
    ("account email", FAKE_EMAIL),
    ("Password (hidden)", FAKE_PASSWORD),
    ("Password again", FAKE_PASSWORD),
]


class SetupBrowserQaLane(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.conf_dir = Path(self.tmp.name) / "agent-access"
        self.conf = self.conf_dir / CONF_NAME

    def source_back(self):
        probe = (
            f'source "{self.conf}"; '
            'printf "%s\\n%s\\n%s" "$SIMS_BROWSER_QA_BASE_URL" '
            '"$SIMS_BROWSER_QA_EMAIL" "$SIMS_BROWSER_QA_PASSWORD"'
        )
        out = subprocess.run(["bash", "-c", probe], capture_output=True, text=True, check=True).stdout
        return out.split("\n", 2)

    def test_writes_private_file_that_sources_back_to_the_same_values(self):
        code, _ = run_in_terminal(self.conf_dir, FULL_ANSWERS)
        self.assertEqual(code, 0)
        self.assertEqual(stat.S_IMODE(self.conf.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(self.conf_dir.stat().st_mode), 0o700)
        url, email, password = self.source_back()
        self.assertEqual(url, "https://sifu-staging.tutorla.tech")
        self.assertEqual(email, FAKE_EMAIL)
        self.assertEqual(password, FAKE_PASSWORD)

    def test_password_is_never_echoed_or_printed(self):
        code, output = run_in_terminal(self.conf_dir, FULL_ANSWERS)
        self.assertEqual(code, 0)
        self.assertNotIn(FAKE_PASSWORD, output)
        self.assertNotIn("Zq9", output)

    def test_refuses_piped_input_and_writes_nothing(self):
        env = dict(os.environ, SIFUTUTOR_AGENT_ACCESS_DIR=str(self.conf_dir))
        result = subprocess.run(
            ["bash", str(SCRIPT)], input="a\nb\nc\nd\n", capture_output=True, text=True, env=env
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("real terminal", result.stderr)
        self.assertFalse(self.conf.exists())

    def test_refuses_production_looking_url(self):
        answers = [("Staging URL", "https://st.admin.sifututor.my")] + FULL_ANSWERS[1:]
        code, _ = run_in_terminal(self.conf_dir, answers)
        self.assertNotEqual(code, 0)
        self.assertFalse(self.conf.exists())

    def test_refuses_http_or_non_staging_host(self):
        for url in ("http://sifu-staging.tutorla.tech", "https://example.test"):
            answers = [("Staging URL", url)] + FULL_ANSWERS[1:]
            code, _ = run_in_terminal(self.conf_dir, answers)
            self.assertNotEqual(code, 0, url)
            self.assertFalse(self.conf.exists(), url)

    def test_mismatched_passwords_write_nothing(self):
        answers = FULL_ANSWERS[:3] + [("Password again", "different")]
        code, _ = run_in_terminal(self.conf_dir, answers)
        self.assertNotEqual(code, 0)
        self.assertFalse(self.conf.exists())

    def test_empty_password_writes_nothing(self):
        answers = FULL_ANSWERS[:2] + [("Password (hidden)", ""), ("Password again", "")]
        code, _ = run_in_terminal(self.conf_dir, answers)
        self.assertNotEqual(code, 0)
        self.assertFalse(self.conf.exists())

    def test_bad_email_writes_nothing(self):
        answers = [FULL_ANSWERS[0], ("account email", "not-an-email")] + FULL_ANSWERS[2:]
        code, _ = run_in_terminal(self.conf_dir, answers)
        self.assertNotEqual(code, 0)
        self.assertFalse(self.conf.exists())

    def test_existing_file_is_kept_unless_replacement_is_confirmed(self):
        self.conf_dir.mkdir(mode=0o700)
        self.conf.write_text("SIMS_BROWSER_QA_PASSWORD=old\n")
        code, output = run_in_terminal(self.conf_dir, [("Replace it?", "n")])
        self.assertEqual(code, 0)
        self.assertEqual(self.conf.read_text(), "SIMS_BROWSER_QA_PASSWORD=old\n")
        code, _ = run_in_terminal(self.conf_dir, [("Replace it?", "y")] + FULL_ANSWERS)
        self.assertEqual(code, 0)
        self.assertEqual(self.source_back()[2], FAKE_PASSWORD)
        self.assertEqual(stat.S_IMODE(self.conf.stat().st_mode), 0o600)

    def test_leaves_no_temporary_file_behind(self):
        run_in_terminal(self.conf_dir, FULL_ANSWERS)
        mismatch = [("Replace it?", "y")] + FULL_ANSWERS[:3] + [("Password again", "different")]
        run_in_terminal(self.conf_dir, mismatch)
        leftovers = sorted(p.name for p in self.conf_dir.iterdir())
        self.assertEqual(leftovers, [CONF_NAME])


if __name__ == "__main__":
    unittest.main()
