#!/usr/bin/env python3
"""Tests for the Mac-side release wrapper, with a fake ssh (issue #350)."""

from __future__ import annotations

import base64
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import pc_job  # noqa: E402
import pc_release  # noqa: E402
import release_readiness as rr  # noqa: E402

TEMPLATE = json.loads(rr.TEMPLATE_PATH.read_text())


class FakeSsh:
    def __init__(self, stdout: str = "", code: int = 0) -> None:
        self.calls: list[dict] = []
        self.stdout, self.code = stdout, code

    def __call__(self, argv, input=None, capture_output=True, text=True, check=False):
        self.calls.append({"argv": list(argv), "input": input})

        class Proc:
            returncode = self.code
            stdout = self.stdout
            stderr = "boom" if self.code else ""

        return Proc()


def readiness_file(tmp: Path, **override) -> Path:
    args = dict(release="Ripple CX audit", repo="agent-os", branch="feat/1-demo", base="origin/main", pr_numbers_=[5], issue="1",
                serving_commit="", approval="Hafiz, test", github_repo=None, suite_commands=None, e2e_commands=[],
                e2e_exception="not user-facing: demo", fix_paths=None, na={})
    args.update(override)
    path = tmp / "readiness.json"
    rr.save(path, rr.build_from_template(TEMPLATE, **args))
    return path


class PcReleaseTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.out: list[str] = []

    def installed_files(self, ssh: FakeSsh) -> dict[str, str]:
        script = ssh.calls[0]["input"]
        files = {}
        for match in re.finditer(r"printf '%s' '([A-Za-z0-9+/=]*)' \| base64 -d > \"[^\"]*/([^/\"]+)\"", script):
            files[match.group(2)] = base64.b64decode(match.group(1)).decode()
        return files

    def test_dry_run_sends_nothing(self) -> None:
        ssh = FakeSsh()
        code = pc_release.start(readiness_file(self.tmp), dry_run=True, runner=ssh, out=self.out.append)
        self.assertEqual(code, 0)
        self.assertEqual(ssh.calls, [])
        text = "\n".join(self.out)
        self.assertIn("DRY RUN", text)
        self.assertIn("never merges, deploys, migrates", text)
        self.assertIn("no caps", text)

    def test_start_installs_the_loop_and_starts_it_through_the_task_scheduler(self) -> None:
        ssh = FakeSsh()
        code = pc_release.start(readiness_file(self.tmp), runner=ssh, out=self.out.append)
        self.assertEqual(code, 0)
        self.assertEqual(len(ssh.calls), 2)
        files = self.installed_files(ssh)
        for name in ("readiness.json", "release_loop.py", "release_readiness.py", "pc_job.py", "job_brief.py", "role.txt",
                     "settings.template.json", "render-claude-settings.py", "start.sh"):
            self.assertIn(name, files)
        self.assertIn("$HOME/releases/", ssh.calls[0]["input"])
        schtasks = ssh.calls[1]["argv"][-1]
        self.assertIn('/tn "release-', schtasks)
        self.assertIn("/releases/", schtasks)
        self.assertIn("schtasks /run", schtasks)
        self.assertIn("python3 release_loop.py run readiness.json --clear-stop", files["start.sh"])
        self.assertIn("--drop-task", files["start.sh"])
        self.assertEqual(json.loads(files["readiness.json"])["release"], "Ripple CX audit")

    def test_start_refuses_a_broken_readiness_file(self) -> None:
        path = readiness_file(self.tmp)
        data = rr.load(path)
        data["items"][0]["owner"] = "bob"
        rr.save(path, data)
        ssh = FakeSsh()
        self.assertEqual(pc_release.start(path, runner=ssh, out=self.out.append), 2)
        self.assertEqual(ssh.calls, [])
        self.assertIn("REFUSED", self.out[0])

    def test_start_warns_about_items_it_will_hand_to_hafiz_and_a_missing_approval(self) -> None:
        path = readiness_file(self.tmp, approval="")
        data = rr.load(path)
        data["items"][4]["check"]["commands"] = ["npm test", "gh pr merge 5"]
        rr.save(path, data)
        pc_release.start(path, dry_run=True, runner=FakeSsh(), out=self.out.append)
        text = "\n".join(self.out)
        self.assertIn("handed to you at once", text)
        self.assertIn("no approval line", text)

    def test_resume_reinstalls_code_but_never_overwrites_the_checkpoint(self) -> None:
        ssh = FakeSsh()
        pc_release.resume("20261009-120000-ripple-cx-audit", runner=ssh, out=self.out.append)
        files = self.installed_files(ssh)
        self.assertNotIn("readiness.json", files)
        self.assertIn("release_loop.py", files)
        self.assertIn("schtasks /run", ssh.calls[1]["argv"][-1])

    def test_stop_creates_the_stop_file_next_to_the_checkpoint(self) -> None:
        ssh = FakeSsh()
        text = pc_release.stop("20261009-120000-ripple-cx-audit", runner=ssh)
        self.assertIn('touch "$HOME/releases/20261009-120000-ripple-cx-audit/STOP"', ssh.calls[0]["input"])
        self.assertIn("STOP file created", text)

    def test_status_scores_the_checkpoint_on_the_pc(self) -> None:
        ssh = FakeSsh(stdout="PC readiness: 50.0%")
        self.assertEqual(pc_release.status("20261009-120000-ripple-cx-audit", runner=ssh), "PC readiness: 50.0%")
        script = ssh.calls[0]["input"]
        self.assertIn("release_readiness.py score readiness.json", script)
        self.assertIn("READY FOR YOUR GO", script)
        self.assertIn("STOP file is present", script)

    def test_report_and_file_read_only_inside_the_release_folder(self) -> None:
        ssh = FakeSsh(stdout="# Release report")
        pc_release.read_file("20261009-120000-ripple-cx-audit", "release-report.md", runner=ssh)
        pc_release.read_file("20261009-120000-ripple-cx-audit", "release-pack/11-review-page.md", runner=ssh)
        for bad in ("../../.ssh/id_rsa", "/etc/passwd", "a b", "x;rm", "release-pack/../../x", ""):
            with self.assertRaises(ValueError, msg=bad):
                pc_release.read_file("20261009-120000-ripple-cx-audit", bad, runner=ssh)

    def test_a_bad_release_id_is_refused_before_anything_is_sent(self) -> None:
        ssh = FakeSsh()
        for bad in ("x", "../x", "20261009-120000-a;b", "20261009-120000-"):
            for func in (pc_release.stop, pc_release.status):
                with self.assertRaises(ValueError):
                    func(bad, runner=ssh)
        self.assertEqual(ssh.calls, [])

    def test_it_reuses_the_pc_job_helpers_instead_of_copying_them(self) -> None:
        source = (HERE / "pc_release.py").read_text()
        for helper in ("def run_ssh", "def install_script", "def schtasks_create", "def b64", "def make_job_id"):
            self.assertNotIn(helper, source)
        self.assertIs(pc_release.pc_job, pc_job)

    def test_pc_job_defaults_are_unchanged_by_the_generalised_helpers(self) -> None:
        self.assertIn("$HOME/jobs/20261009-120000-x", pc_job.install_script("20261009-120000-x", {"a": "b"}))
        self.assertIn('/tn "job-20261009-120000-x"', pc_job.schtasks_create("20261009-120000-x"))
        self.assertIn("/jobs/20261009-120000-x/start.sh", pc_job.schtasks_create("20261009-120000-x"))


if __name__ == "__main__":
    unittest.main()
