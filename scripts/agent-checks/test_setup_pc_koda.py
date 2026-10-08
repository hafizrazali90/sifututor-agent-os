#!/usr/bin/env python3
"""Tests for scripts/agent-access/setup-pc-koda.sh. Driven through a pseudo-terminal; health check skipped; all paths are temporary."""

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
SCRIPT = Path(os.environ.get("KODA_SETUP_SCRIPT", ROOT / "scripts/agent-access/setup-pc-koda.sh"))
FAKE_KEY = "fake-koda-key-Zq9$x\"q\"'a'!"
SAFE_KEY = "fakekey-ABC123xyz"


def run_in_terminal(env_extra, answers, timeout=20):
    env = dict(os.environ, SIFUTUTOR_SKIP_HEALTH="1", **env_extra)
    pid, fd = pty.fork()
    if pid == 0:
        os.execvpe("bash", ["bash", str(SCRIPT)], env)
    output, pending, deadline = b"", list(answers), time.time() + timeout
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
        raise AssertionError(f"stuck; unanswered: {[p for p, _ in pending]}")
    _, status = os.waitpid(pid, 0)
    return os.waitstatus_to_exitcode(status), output.decode(errors="replace")


def answers(key=SAFE_KEY, again=None):
    return [("Koda key (hidden)", key), ("Koda key again", again if again is not None else key)]


class SetupPcKoda(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        t = Path(self.tmp.name)
        self.conf = t / "conf"
        self.profile = t / "bashrc"
        self.repo = t / "repo"
        self.repo.mkdir()
        self.env = {"SIFUTUTOR_CONFIG_DIR": str(self.conf), "SIFUTUTOR_PROFILE_FILE": str(self.profile), "SIFUTUTOR_REPO": str(self.repo)}
        self.keyfile = self.conf / "koda-key.conf"

    def sourced_key(self, value):
        out = subprocess.run(["bash", "-c", f'source "{self.keyfile}"; printf %s "$KODA_API_KEY"'], capture_output=True, text=True, check=True).stdout
        return out

    def test_key_file_is_private_and_sources_back_exactly(self):
        code, _ = run_in_terminal(self.env, answers(FAKE_KEY))
        self.assertEqual(code, 0)
        self.assertEqual(stat.S_IMODE(self.keyfile.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(self.conf.stat().st_mode), 0o700)
        self.assertEqual(self.sourced_key(FAKE_KEY), FAKE_KEY)

    def test_key_is_never_echoed(self):
        code, out = run_in_terminal(self.env, answers(FAKE_KEY))
        self.assertEqual(code, 0)
        self.assertNotIn("fake-koda-key", out)

    def test_profile_line_added_once_even_if_run_twice(self):
        run_in_terminal(self.env, answers())
        run_in_terminal(self.env, answers())
        text = self.profile.read_text()
        self.assertEqual(text.count("sifututor koda key"), 1)
        self.assertIn(str(self.keyfile), text)
        self.assertNotIn(SAFE_KEY, text)

    def test_mcp_json_created_with_variable_reference_and_never_overwritten(self):
        run_in_terminal(self.env, answers())
        mcp = self.repo / ".mcp.json"
        body = mcp.read_text()
        self.assertIn("${KODA_API_KEY}", body)
        self.assertNotIn(SAFE_KEY, body)
        mcp.write_text("{\"mine\": true}\n")
        run_in_terminal(self.env, answers())
        self.assertEqual(mcp.read_text(), "{\"mine\": true}\n")

    def test_refuses_piped_input_and_writes_nothing(self):
        env = dict(os.environ, SIFUTUTOR_SKIP_HEALTH="1", **self.env)
        r = subprocess.run(["bash", str(SCRIPT)], input="a\na\n", capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 2)
        self.assertFalse(self.keyfile.exists())

    def test_empty_mismatched_or_spaced_key_writes_nothing(self):
        for a in (answers(""), answers(SAFE_KEY, "different"), answers("has space")):
            code, _ = run_in_terminal(self.env, a)
            self.assertNotEqual(code, 0)
            self.assertFalse(self.keyfile.exists())

    def test_health_failure_is_reported_and_exits_nonzero(self):
        env = dict(self.env)
        (self.repo / "scripts/agent-checks").mkdir(parents=True)
        fake = self.repo / "scripts/agent-checks/koda"
        fake.write_text("#!/usr/bin/env bash\nexit 1\n")
        fake.chmod(0o755)
        e = dict(os.environ, **env)
        e.pop("SIFUTUTOR_SKIP_HEALTH", None)
        pid, fd = pty.fork()
        if pid == 0:
            os.execvpe("bash", ["bash", str(SCRIPT)], e)
        out, pend, dl = b"", list(answers()), time.time() + 20
        while time.time() < dl:
            r, _, _ = select.select([fd], [], [], 0.2)
            if r:
                try:
                    c = os.read(fd, 4096)
                except OSError:
                    c = b""
                if not c:
                    break
                out += c
                if pend and pend[0][0].encode() in out:
                    time.sleep(0.1)
                    os.write(fd, (pend.pop(0)[1] + "\n").encode())
                    out += b"\0S\0"
        _, st = os.waitpid(pid, 0)
        self.assertNotEqual(os.waitstatus_to_exitcode(st), 0)
        self.assertIn("FAIL", out.decode(errors="replace"))


if __name__ == "__main__":
    unittest.main()
