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
                e2e_exception="not user-facing: demo", fix_paths=None, na={}, route="direct-prod", staging=None)
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

    def test_start_ships_the_staging_deploy_script_and_the_box_program(self) -> None:
        ssh = FakeSsh()
        pc_release.start(readiness_file(self.tmp), runner=ssh, out=self.out.append)
        files = self.installed_files(ssh)
        self.assertEqual(files["staging_remote.py"], (HERE / "staging_remote.py").read_text())
        self.assertEqual(files["staging_deploy.py"], (HERE / "staging_deploy.py").read_text())

    def test_start_says_plainly_that_the_pc_will_deploy_staging_only_when_the_release_asks_for_it(self) -> None:
        path = readiness_file(self.tmp, repo="ripple-suite", branch="release/1700-proof", route="staging-first", na={"4": "docs only"},
                              staging={"target": "ripple", "mode": "normal", "approval": "Hafiz, test",
                                       "smoke_commands": ["npm run test:staging-luna-auth-smoke"]})
        pc_release.start(path, dry_run=True, runner=FakeSsh(), out=self.out.append)
        text = "\n".join(self.out)
        self.assertIn("deploys STAGING only", text)
        self.assertIn("never deploys production", text)
        self.assertNotIn("the loop never merges, deploys, migrates", text)

    def test_deploy_status_reads_the_staging_gates_on_the_pc(self) -> None:
        ssh = FakeSsh(stdout="Release x: PC staging deploy to ripple")
        text = pc_release.deploy_status("20261009-120000-ripple-cx-audit", runner=ssh)
        self.assertIn("PC staging deploy", text)
        self.assertIn("python3 staging_deploy.py report readiness.json", ssh.calls[0]["input"])
        with self.assertRaises(ValueError):
            pc_release.deploy_status("../x", runner=ssh)

    def test_staging_switch_uses_the_fixed_alias_and_only_on_off_show(self) -> None:
        calls = []

        class Shell:
            def run(self, argv, **kw):
                calls.append(argv)
                return 0, "STOP switch is ON"

        self.assertIn("ON", pc_release.staging_switch("ripple", "off", shell=Shell()))
        self.assertEqual(calls[0][-2], "staging")
        for bad in (("prod", "off"), ("ripple", "rm")):
            with self.assertRaises((ValueError, SystemExit)):
                pc_release.staging_switch(*bad, shell=Shell())

    def test_start_stamps_the_release_id_into_both_copies_so_gate_and_route_can_find_the_release(self) -> None:
        ssh = FakeSsh()
        path = readiness_file(self.tmp)
        pc_release.start(path, runner=ssh, out=self.out.append)
        sent = json.loads(self.installed_files(ssh)["readiness.json"])
        started = re.search(r"Started (\S+) on the PC", "\n".join(self.out)).group(1)
        self.assertEqual(sent["release_id"], started)
        self.assertEqual(rr.load(path)["release_id"], started)
        self.assertIn("route direct-prod", "\n".join(self.out))
        self.assertIn("Prod readiness", "\n".join(self.out))

    def test_dry_run_does_not_stamp_the_local_file(self) -> None:
        path = readiness_file(self.tmp)
        pc_release.start(path, dry_run=True, runner=FakeSsh(), out=self.out.append)
        self.assertNotIn("release_id", rr.load(path))

    def test_gate_runs_the_gate_command_in_the_release_folder_on_the_pc(self) -> None:
        ssh = FakeSsh(stdout="Gate S2: queued")
        text = pc_release.gate("20261009-120000-ripple-cx-audit", "S2", "staging deployed", by="Hafiz", sha="a" * 40, simulated=True,
                               runner=ssh)
        script = ssh.calls[0]["input"]
        self.assertEqual(text, "Gate S2: queued")
        self.assertIn('cd "$HOME/releases/20261009-120000-ripple-cx-audit"', script)
        self.assertIn("python3 release_readiness.py gate readiness.json S2 --evidence 'staging deployed' --by Hafiz --sha " + "a" * 40
                      + " --simulated", script)

    def test_gate_evidence_is_shell_quoted(self) -> None:
        ssh = FakeSsh()
        pc_release.gate("20261009-120000-ripple-cx-audit", "G1", "ok'; rm -rf / #", runner=ssh)
        self.assertIn("'ok'\"'\"'; rm -rf / #'", ssh.calls[0]["input"])
        self.assertNotIn("--evidence ok'; rm", ssh.calls[0]["input"])

    def test_gate_and_route_find_the_release_from_the_local_readiness_file(self) -> None:
        path = readiness_file(self.tmp)
        with self.assertRaises(ValueError):
            pc_release.gate(str(path), "G1", "ok", runner=FakeSsh())  # never started: no id yet
        pc_release.start(path, runner=FakeSsh(), out=self.out.append)
        release_id = rr.load(path)["release_id"]
        ssh = FakeSsh()
        pc_release.gate(str(path), "G1", "ok", runner=ssh)
        pc_release.route(str(path), "staging-first", by="Hafiz", runner=ssh)
        self.assertIn(release_id, ssh.calls[0]["input"])
        self.assertIn("release_readiness.py route readiness.json staging-first --by Hafiz", ssh.calls[1]["input"])

    def test_an_unknown_route_or_id_is_refused_before_anything_is_sent(self) -> None:
        ssh = FakeSsh()
        with self.assertRaises(ValueError):
            pc_release.route("20261009-120000-ripple-cx-audit", "sideways", runner=ssh)
        with self.assertRaises(ValueError):
            pc_release.gate("../../etc", "G1", "x", runner=ssh)
        self.assertEqual(ssh.calls, [])

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

    def test_clean_removes_only_the_scheduler_task(self) -> None:
        ssh = FakeSsh(stdout="SUCCESS: deleted")
        self.assertEqual(pc_release.clean("20261009-120000-ripple-cx-audit", runner=ssh), "SUCCESS: deleted")
        self.assertEqual(ssh.calls[0]["argv"][-1], 'schtasks /delete /tn "release-20261009-120000-ripple-cx-audit" /f')
        with self.assertRaises(ValueError):
            pc_release.clean("bad", runner=ssh)

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
