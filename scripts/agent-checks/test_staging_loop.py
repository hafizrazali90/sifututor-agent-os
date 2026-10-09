#!/usr/bin/env python3
"""The release loop closing S1, S2 and S3 itself, with the staging deploy script (issue #356).

A FAKE shell plays ssh, git and the test commands; a FAKE http plays the staging site.
Negative controls: the gates are PC items, so a person cannot close them with typed text;
a refusal on the box blocks the loop after the second try and nothing is started; a STOP
during the deploy leaves the deploy to finish and a restart attaches to it instead of
starting a second one; a moved candidate sends S1 to S4 back to open.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import unittest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import release_loop as rl  # noqa: E402
import release_readiness as rr  # noqa: E402
import staging_deploy as sd  # noqa: E402
import test_release_loop as trl  # noqa: E402
import test_staging_deploy as tsd  # noqa: E402

SHA_A, SHA_B = tsd.SHA_A, tsd.SHA_B
REF = tsd.REF
PROMO = "docs/356-proof"


class LoopShell(tsd.FakeBox):
    """FakeBox plus the git and gh answers the loop needs."""

    def __init__(self) -> None:
        super().__init__()
        self.tip = SHA_A
        self.when("rev-parse", "HEAD", out="1" * 40 + "\n")
        self.when("gh", "pr", "view", out=json.dumps({"number": 5, "state": "OPEN", "headRefName": PROMO,
                                                        "headRefOid": "1" * 40, "baseRefName": "main"}))
        self.rules.insert(0, (("ls-remote",), 0, ""))
        self.reply("check", 0, f"CHECK OK: {SHA_A} on {REF} would be accepted for ripple staging now (mode normal)")
        self.reply("start", 0, f"STARTED run=20261009T060000Z-aaaaaaaa target=ripple ref={REF} sha={SHA_A} mode=normal")
        self.statuses = [f"run=20261009T060000Z-aaaaaaaa state=finished step=verify\n{tsd.RESULT_OK}\n"]
        self.reply("verify", 0, f"expected={SHA_A}\nVERIFY OK")
        self.stop_after_status = False

    def run(self, argv, cwd=None, stop_check=None, input_text=None, env=None, timeout=None):
        if argv[:3] == ["git", "ls-remote", "--heads"]:
            self.calls.append({"argv": list(argv), "cwd": cwd, "input": None, "env": None, "timeout": None})
            return 0, f"{self.tip}\trefs/heads/{argv[-1].removeprefix('refs/heads/')}\n"
        return super().run(argv, cwd=cwd, stop_check=stop_check, input_text=input_text, env=env, timeout=timeout)


def ripple_data(**staging) -> dict:
    cfg = {"target": "ripple", "mode": "normal", "approval": "Hafiz, chat 09/10/2026: PC may deploy STAGING only",
           "ref": REF, "smoke_commands": ["npm run test:staging-luna-auth-smoke"]}
    cfg.update(staging)
    na = {str(i): "not under test here" for i in (1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12)}
    data = rr.build_from_template(trl.TEMPLATE, release="Staging proof", repo="ripple-suite", branch=PROMO, base="origin/main",
                                  pr_numbers_=[5], issue="356", serving_commit="", approval="Hafiz, test", github_repo=None,
                                  suite_commands=None, e2e_commands=[], e2e_exception="not user-facing: docs only", fix_paths=None,
                                  na=na, route="staging-first", staging=cfg)
    for gate in data["items"]:
        if rr.is_gate(gate) and rr.is_applicable(gate) and gate.get("status") == "open":
            rr.close_gate_in_data(data, gate["id"], "closed by the test", by="test")
    return data


class StagingLoopCase(trl.LoopCase):
    def setUp(self) -> None:
        super().setUp()
        import tempfile
        import os
        from unittest import mock
        self.lanes = Path(tempfile.mkdtemp(prefix="lanes-"))
        self.addCleanup(__import__("shutil").rmtree, self.lanes, True)
        (self.lanes / "ripple-staging-smoke.conf").write_text(
            f"RIPPLE_STAGING_SUPERADMIN_EMAIL={tsd.SEKRET_MAIL}\nRIPPLE_STAGING_SUPERADMIN_PASSWORD={tsd.SEKRET_PASS}\n")
        (self.lanes / "ripple-staging-smoke.conf").chmod(0o600)
        patcher = mock.patch.dict(os.environ, {sd.LANE_DIR_ENV: str(self.lanes), sd.PC_STOP_ENV: str(self.tmp / "no-stop")})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.http = tsd.FakeHttp({("GET", "/login"): (200, {}, ""), ("POST", "/api/auth/login"): (200, {}, ""),
                                  ("GET", "/api/auth/me"): (200, {}, ""), ("GET", "/requests"): (200, {}, "")})

    def make_staging(self, data: dict, shell=None, **kwargs):
        shell = shell or LoopShell()
        return self.make(data, shell=shell, http=self.http, deploy_poll_seconds=0, **kwargs)

    def verbs(self) -> list[str]:
        return [re.search(r"remote \w+ (\w+)", c["argv"][-1]).group(1) for c in self.shell.ssh_calls()]


class StagingGatesTest(StagingLoopCase):
    def test_the_loop_closes_s1_s2_s3_s4_with_real_actions_and_reaches_ready(self) -> None:
        loop = self.make_staging(ripple_data())
        self.assertEqual(loop.run(), "ready_for_prod_go")
        data = self.saved()
        items = {i["id"]: i for i in data["items"]}
        for gate in ("S1", "S2", "S3", "S4"):
            self.assertEqual(items[gate]["owner"], "pc", gate)
            self.assertEqual(items[gate]["status"], "green", gate)
            self.assertFalse(any(e.get("simulated") for e in items[gate]["evidence"]), gate)
        self.assertEqual(rr.score(data)["prod_percent"], 100.0)
        self.assertEqual(data["staging_sha"], SHA_A)
        self.assertEqual(self.verbs(), ["check", "check", "start", "status", "verify", "verify"])  # S2 checks again just before it starts
        s2_notes = " | ".join(e.get("note", "") for e in items["S2"]["evidence"])
        for fragment in ("CHECK OK", "STARTED run=", "RESULT run=", "VERIFY OK", "read back"):
            self.assertIn(fragment, s2_notes)
        self.assertIn(SHA_A, json.dumps(items["S1"]["evidence"]))
        report = (self.dir / "release-report.md").read_text()
        self.assertIn("STAGING only", report)
        self.assertNotIn("Nothing was merged, deployed, migrated", report)

    def test_only_the_staging_box_is_ever_contacted_and_nothing_pushes_or_merges(self) -> None:
        self.make_staging(ripple_data()).run()
        for call in self.shell.ssh_calls():
            self.assertEqual(call["argv"][-2], "staging")
        lines = [" ".join(c["argv"]) for c in self.shell.calls if c["argv"][0] != "ssh"]
        for line in lines:
            self.assertNotRegex(line, r"git push|gh pr merge|production")

    def test_a_person_cannot_close_a_staging_gate_with_typed_text(self) -> None:
        loop = self.make_staging(ripple_data())
        for gate in ("S1", "S2", "S3"):
            with self.assertRaises(rr.ReadinessError) as ctx:
                rr.close_gate_in_data(loop.items() if False else rr.load(self.path), gate, "I deployed it by hand", by="Hafiz", sha=SHA_A)
            self.assertIn("PC item", str(ctx.exception))

    def test_without_the_staging_flag_s1_to_s3_stay_mac_gates(self) -> None:
        data = rr.build_from_template(trl.TEMPLATE, release="x", repo="ripple-suite", branch=REF, base="origin/main", pr_numbers_=[],
                                      issue="1", serving_commit="", approval="", github_repo=None, suite_commands=None, e2e_commands=[],
                                      e2e_exception="not user-facing: x", fix_paths=None, na={}, route="staging-first")
        owners = {i["id"]: i["owner"] for i in data["items"] if i["id"] in ("S1", "S2", "S3", "S4")}
        self.assertEqual(owners, {"S1": "mac", "S2": "mac", "S3": "mac", "S4": "pc"})
        self.assertNotIn("staging", data)

    def test_a_refusal_on_the_box_blocks_after_the_second_try_and_starts_nothing(self) -> None:
        shell = LoopShell()
        shell.verbs["check"] = [(2, "REFUSED: the release changes migration, script or build-control files (package.json); this needs a Mac session")]
        loop = self.make_staging(ripple_data(), shell=shell)
        self.assertEqual(loop.run(), "blocked")
        data = self.saved()
        s1 = {i["id"]: i for i in data["items"]}["S1"]
        self.assertEqual(s1["failures"], 2)
        self.assertIn("Mac session", s1["blocked_reason"])
        self.assertNotIn("start", self.verbs())
        self.assertEqual(rr.score(data)["prod_ready"], False)

    def test_a_failed_smoke_blocks_s3_and_prod_readiness_stays_below_100(self) -> None:
        shell = LoopShell()
        shell.when("npm run test:staging-luna-auth-smoke", rc=1, out="1 failed")
        loop = self.make_staging(ripple_data(), shell=shell)
        self.assertEqual(loop.run(), "blocked")
        data = self.saved()
        items = {i["id"]: i for i in data["items"]}
        self.assertEqual((items["S1"]["status"], items["S2"]["status"], items["S3"]["status"]), ("green", "green", "blocked"))
        self.assertLess(rr.score(data)["prod_percent"], 100.0)

    def test_a_stop_during_the_deploy_leaves_it_running_and_a_restart_attaches_to_it(self) -> None:
        shell = LoopShell()
        shell.statuses = ["run=20261009T060000Z-aaaaaaaa state=running step=controller\n"]
        loop = self.make_staging(ripple_data(), shell=shell)
        polls = {"n": 0}
        original = shell.run

        def stopping(argv, **kw):
            out = original(argv, **kw)
            if argv[0] == "ssh" and "remote ripple status" in argv[-1]:
                polls["n"] += 1
                (self.dir / "STOP").write_text("stop")
            return out
        shell.run = stopping
        self.assertEqual(loop.run(), "stopped")
        data = self.saved()
        cfg = data["staging"]
        self.assertEqual(cfg["deploy"]["run"], "20261009T060000Z-aaaaaaaa")
        self.assertEqual(self.verbs().count("start"), 1)
        # restart: the box says the run finished
        (self.dir / "STOP").unlink()
        shell.run = original
        shell.statuses = [f"run=20261009T060000Z-aaaaaaaa state=finished step=verify\n{tsd.RESULT_OK}\n"]
        loop2 = self.make_staging(rr.load(self.path), shell=shell)
        self.assertEqual(loop2.run(), "ready_for_prod_go")
        self.assertEqual(self.verbs().count("start"), 1, "a second deploy must not be started")

    def test_a_moved_candidate_sends_the_staging_proof_back_to_open(self) -> None:
        shell = LoopShell()
        loop = self.make_staging(ripple_data(), shell=shell)
        self.assertEqual(loop.run(), "ready_for_prod_go")
        shell.tip = SHA_B
        loop.data = rr.load(self.path)
        self.assertTrue(loop.staging_candidate_moved())
        data = loop.data
        items = {i["id"]: i for i in data["items"]}
        for gate in ("S1", "S2", "S3", "S4"):
            self.assertEqual(items[gate]["status"], "open", gate)
        self.assertNotIn("staging_sha", data)
        self.assertNotIn("candidate_sha", data["staging"])
        self.assertFalse(loop.staging_candidate_moved(), "nothing is left to reset")

    def test_an_unchanged_candidate_keeps_its_proof(self) -> None:
        shell = LoopShell()
        loop = self.make_staging(ripple_data(), shell=shell)
        loop.run()
        loop.data = rr.load(self.path)
        self.assertFalse(loop.staging_candidate_moved())

    def test_a_pinned_commit_that_no_longer_matches_fails_s1(self) -> None:
        shell = LoopShell()
        shell.tip = SHA_B
        loop = self.make_staging(ripple_data(commit=SHA_A), shell=shell)
        self.assertEqual(loop.run(), "blocked")
        self.assertNotIn("check", self.verbs())

    def test_the_readiness_file_cannot_carry_a_production_target(self) -> None:
        for key, value in (("env", "prod"), ("target", "production")):
            data = ripple_data()
            data["staging"][key] = value
            self.assertTrue(rr.validate(data), key)
            rr.save(self.path, data)
            loop = self.make_staging(data)
            with self.assertRaises(rr.ReadinessError):
                loop.run()
            self.assertEqual(self.shell.ssh_calls(), [])


if __name__ == "__main__":
    unittest.main()
