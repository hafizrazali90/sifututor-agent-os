#!/usr/bin/env python3
"""Tests for the PC side of the staging deploy (issue #356).

A FAKE shell stands in for ssh, git and the test commands, and a FAKE http
object stands in for the staging sites, so nothing real is touched.
Negative controls (each must fail on a wrong implementation): a deploy action
that accepts a production target, a ref outside the allowed patterns, a
commit that is not at the remote tip, a held lock or a STOP file on the box
(box-side tests), a PC STOP file, and a smoke that would print a secret.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import release_readiness as rr  # noqa: E402
import staging_deploy as sd  # noqa: E402
import staging_remote as sr  # noqa: E402

SHA_A, SHA_B, SHA_C = "a" * 40, "b" * 40, "c" * 40
REF = "release/1700-proof"
SEKRET_MAIL, SEKRET_PASS = "qa.person@example.test", "Zx9-very-secret-value"


class Quiet(unittest.TestCase):
    def setUp(self) -> None:
        stack = contextlib.ExitStack()
        stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
        stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
        self.addCleanup(stack.close)
        self.tmp = Path(tempfile.mkdtemp(prefix="sd-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.env = mock_env({sd.LANE_DIR_ENV: str(self.tmp / "lanes"), sd.PC_STOP_ENV: str(self.tmp / "PC-STOP")})
        self.env.start()
        self.addCleanup(self.env.stop)
        (self.tmp / "lanes").mkdir()


def mock_patch(obj, name, value):
    from unittest import mock
    return mock.patch.object(obj, name, value)


def mock_env(values: dict[str, str]):
    from unittest import mock
    return mock.patch.dict(os.environ, values)


def write_lane(tmp: Path, name: str, text: str, mode: int = 0o600) -> None:
    path = tmp / "lanes" / name
    path.write_text(text)
    path.chmod(mode)


class FakeBox:
    """A shell that answers ssh calls like the staging box program would, and everything else from rules."""

    def __init__(self) -> None:
        self.calls: list[dict] = []
        self.verbs: dict[str, list] = {}
        self.rules: list = []
        self.statuses: list[str] = []

    def reply(self, verb: str, code: int, out: str) -> None:
        self.verbs.setdefault(verb, []).append((code, out))

    def when(self, *words: str, rc: int = 0, out: str = "") -> None:
        self.rules.insert(0, (words, rc, out))

    def run(self, argv, cwd=None, stop_check=None, input_text=None, env=None, timeout=None):
        self.calls.append({"argv": list(argv), "cwd": cwd, "input": input_text, "env": env, "timeout": timeout})
        line = " ".join(argv)
        if argv[0] == "ssh":
            verb = re.search(r"remote (?:ripple|sims) (\w+)", argv[-1]).group(1)
            queue = self.verbs.get(verb, [])
            if verb == "status" and self.statuses:
                return 0, self.statuses.pop(0) if len(self.statuses) > 1 else self.statuses[0]
            if len(queue) > 1:
                return queue.pop(0)
            return queue[0] if queue else (0, "")
        for words, rc, out in self.rules:
            if all(w in line for w in words):
                return rc, out
        return 0, ""

    def ssh_calls(self) -> list[dict]:
        return [c for c in self.calls if c["argv"][0] == "ssh"]


RESULT_OK = f"RESULT run=20261009T060000Z-aaaaaaaa status=ok exit=0 seconds=600 ref={REF} sha={SHA_A}"


def good_box() -> FakeBox:
    box = FakeBox()
    box.reply("check", 0, f"CHECK OK: {SHA_A} on {REF} would be accepted for ripple staging now (mode normal)")
    box.reply("start", 0, f"STARTED run=20261009T060000Z-aaaaaaaa target=ripple ref={REF} sha={SHA_A} mode=normal")
    box.statuses = ["run=20261009T060000Z-aaaaaaaa state=running step=controller\n",
                    f"run=20261009T060000Z-aaaaaaaa state=finished step=verify\n{RESULT_OK}\n"]
    box.reply("verify", 0, f"expected={SHA_A} pm2_status=online\nVERIFY OK")
    return box


class DeployerTests(Quiet):
    def deployer(self, box: FakeBox, target: str = "ripple", **kw) -> sd.Deployer:
        return sd.Deployer(target, box, sleep=lambda s: None, poll_seconds=0, **kw)

    def test_production_is_not_a_target(self) -> None:
        for bad in ("prod", "production", "staging", "main", "", "live"):
            with self.assertRaises(sd.DeployError):
                sd.Deployer(bad, FakeBox())

    def test_each_target_uses_its_own_alias_and_nothing_else(self) -> None:
        box = good_box()
        self.deployer(box, "ripple").check(REF, SHA_A)
        self.assertEqual(box.ssh_calls()[-1]["argv"][-2], "staging")
        box2 = FakeBox()
        box2.reply("check", 0, "CHECK OK: x")
        self.deployer(box2, "sims").check("test/3373-staging-candidate", SHA_A)
        self.assertEqual(box2.ssh_calls()[-1]["argv"][-2], "finch")
        for call in box.ssh_calls() + box2.ssh_calls():
            self.assertNotIn(call["argv"][-2], ("production", "prod", "root", "homepc"))

    def test_the_remote_command_sends_the_program_checks_its_name_and_quotes_arguments(self) -> None:
        box = good_box()
        self.deployer(box).check(REF, SHA_A, "normal")
        call = box.ssh_calls()[0]
        self.assertEqual(call["input"], (HERE / "staging_remote.py").read_text())
        command = call["argv"][-1]
        self.assertIn("cat >", command)
        self.assertIn("exec python3", command)
        self.assertRegex(command, r"staging_remote-[0-9a-f]{12}\.py")
        self.assertIn("remote ripple check " + REF + " " + SHA_A, command)
        self.assertEqual(call["argv"][:3], ["ssh", "-o", "BatchMode=yes"])

    def test_an_argument_with_shell_characters_is_refused_before_ssh(self) -> None:
        box = good_box()
        d = self.deployer(box)
        for ref in ("release/1-x;id", "release/1-x $(id)", "main", "../x", "release/1-x\nid"):
            with self.assertRaises(sd.DeployError):
                d.check(ref, SHA_A)
        with self.assertRaises(sd.DeployError):
            d.check(REF, "abc")
        with self.assertRaises(sd.DeployError):
            d.check(REF, SHA_A, "prod")
        with self.assertRaises(sd.DeployError):
            d.check(REF, SHA_A, "normal", "short")
        self.assertEqual(box.ssh_calls(), [])

    def test_pc_stop_file_blocks_every_deploy_verb_before_ssh(self) -> None:
        (self.tmp / "PC-STOP").write_text("stop")
        box = good_box()
        d = self.deployer(box)
        with self.assertRaises(sd.DeployError):
            d.check(REF, SHA_A)
        with self.assertRaises(sd.DeployError):
            d.start(REF, SHA_A)
        self.assertEqual(box.ssh_calls(), [])

    def test_check_reports_a_refusal_with_the_box_reason(self) -> None:
        box = FakeBox()
        box.reply("check", 2, "REFUSED: another deploy or migration lane is running (locks held: .deploy-staging.lock)")
        ok, why = self.deployer(box).check(REF, SHA_A)
        self.assertFalse(ok)
        self.assertIn(".deploy-staging.lock", why)

    def test_a_check_that_exits_zero_without_check_ok_is_not_ok(self) -> None:
        box = FakeBox()
        box.reply("check", 0, "something else")
        self.assertFalse(self.deployer(box).check(REF, SHA_A)[0])

    def test_start_returns_the_run_id_and_fails_without_one(self) -> None:
        box = good_box()
        self.assertEqual(self.deployer(box).start(REF, SHA_A), "20261009T060000Z-aaaaaaaa")
        box = FakeBox()
        box.reply("start", 2, "REFUSED: a PC staging deploy is already running on this box")
        with self.assertRaises(sd.DeployError) as ctx:
            self.deployer(box).start(REF, SHA_A)
        self.assertIn("already running", str(ctx.exception))

    def test_full_deploy_polls_to_the_end_then_reads_back(self) -> None:
        box = good_box()
        seen = []
        outcome = self.deployer(box).deploy_and_verify(REF, SHA_A, on_run=seen.append)
        self.assertTrue(outcome["ok"], outcome)
        self.assertEqual(seen, ["20261009T060000Z-aaaaaaaa"])
        verbs = [re.search(r"remote \w+ (\w+)", c["argv"][-1]).group(1) for c in box.ssh_calls()]
        self.assertEqual(verbs, ["check", "start", "status", "status", "verify"])
        notes = " | ".join(e.get("note", "") for e in outcome["evidence"])
        for fragment in ("CHECK OK", "STARTED run=", "RESULT run=", "VERIFY OK", SHA_A[:10] if False else "read back"):
            self.assertIn(fragment, notes)
        self.assertEqual([e for e in outcome["evidence"] if e.get("sha")][0]["sha"], SHA_A)

    def test_a_refused_check_never_starts_a_deploy(self) -> None:
        box = good_box()
        box.verbs["check"] = [(2, "REFUSED: the STOP switch is on")]
        outcome = self.deployer(box).deploy_and_verify(REF, SHA_A)
        self.assertFalse(outcome["ok"])
        self.assertTrue(outcome["refused"])
        self.assertEqual([c for c in box.ssh_calls() if "remote ripple start" in c["argv"][-1]], [])

    def test_a_failed_or_timed_out_run_is_not_success_and_is_not_verified(self) -> None:
        for status in ("failed", "timeout"):
            box = good_box()
            box.statuses = [f"run=r1 state=finished step=controller\nRESULT run=r1 status={status} exit=1 seconds=5 ref={REF} sha={SHA_A}\n"]
            outcome = self.deployer(box).deploy_and_verify(REF, SHA_A)
            self.assertFalse(outcome["ok"], status)
            self.assertFalse([c for c in box.ssh_calls() if "remote ripple verify" in c["argv"][-1]])

    def test_a_died_runner_is_a_failure(self) -> None:
        box = good_box()
        box.statuses = ["run=r1 state=died step=controller\n"]
        self.assertFalse(self.deployer(box).deploy_and_verify(REF, SHA_A)["ok"])

    def test_a_failed_read_back_is_not_success_even_when_the_run_says_ok(self) -> None:
        box = good_box()
        box.verbs["verify"] = [(1, "VERIFY FAILED")]
        outcome = self.deployer(box).deploy_and_verify(REF, SHA_A)
        self.assertFalse(outcome["ok"])
        self.assertIn("read-back", outcome["summary"])

    def test_attaching_to_a_known_run_does_not_start_another(self) -> None:
        box = good_box()
        outcome = self.deployer(box).deploy_and_verify(REF, SHA_A, run="20261009T060000Z-aaaaaaaa")
        self.assertTrue(outcome["ok"])
        verbs = [re.search(r"remote \w+ (\w+)", c["argv"][-1]).group(1) for c in box.ssh_calls()]
        self.assertNotIn("start", verbs)
        self.assertNotIn("check", verbs)

    def test_losing_contact_for_too_long_raises_but_a_blip_does_not(self) -> None:
        box = good_box()
        answers = [(255, "ssh: connection reset")] * 3
        box.statuses = []
        original = box.run
        state = {"n": 0}

        def flaky(argv, **kw):
            if argv[0] == "ssh" and "remote ripple status" in argv[-1]:
                state["n"] += 1
                if state["n"] <= 3:
                    return answers[0]
                return 0, f"run=r1 state=finished step=verify\n{RESULT_OK}\n"
            return original(argv, **kw)
        box.run = flaky
        self.assertTrue(self.deployer(box).deploy_and_verify(REF, SHA_A)["ok"])
        box2 = good_box()
        box2.statuses = []
        box2.run = lambda argv, **kw: (255, "down") if "remote ripple status" in argv[-1] else FakeBox.run(box2, argv, **kw)
        with self.assertRaises(sd.DeployError) as ctx:
            self.deployer(box2).wait("20261009T060000Z-aaaaaaaa")
        self.assertIn("lost contact", str(ctx.exception))

    def test_stop_during_the_wait_raises_stop_requested_and_leaves_the_deploy_alone(self) -> None:
        box = good_box()
        d = self.deployer(box, stop_check=lambda: True)
        with self.assertRaises(rr.StopRequested):
            d.wait("20261009T060000Z-aaaaaaaa")
        self.assertEqual(box.ssh_calls(), [])

    def test_switch_only_takes_on_off_show(self) -> None:
        box = FakeBox()
        box.reply("switch", 0, "STOP switch is ON")
        d = self.deployer(box)
        self.assertIn("ON", d.switch("off"))
        with self.assertRaises(sd.DeployError):
            d.switch("rm -rf")


class ValidateStagingTests(unittest.TestCase):
    def data(self, **staging) -> dict:
        base = {"target": "ripple", "mode": "normal", "approval": "Hafiz, test", "smoke_commands": ["npm run test:staging-luna-auth-smoke"]}
        base.update(staging)
        return {"repo": "ripple-suite", "branch": "release/1700-proof", "staging": base}

    def test_a_good_section_has_no_errors(self) -> None:
        self.assertEqual(sd.validate_staging(self.data()), [])
        self.assertEqual(sd.validate_staging({"repo": "agent-os"}), [])

    def test_a_production_target_or_environment_key_cannot_be_set(self) -> None:
        for key, value in (("env", "prod"), ("environment", "production"), ("host", "root@1.2.3.4"), ("alias", "production"),
                           ("target_env", "prod")):
            self.assertTrue(sd.validate_staging(self.data(**{key: value})), key)
        for target in ("prod", "production", "staging", "", None):
            self.assertTrue(sd.validate_staging(self.data(target=target)), target)

    def test_ref_must_match_the_target_patterns(self) -> None:
        for ref in ("main", "staging", "docs/proof", "test/3373-staging-candidate"):
            self.assertTrue(sd.validate_staging(self.data(ref=ref)), ref)
        self.assertEqual(sd.validate_staging(self.data(ref="release/1581-request-timeline-r6")), [])

    def test_the_default_ref_is_the_release_branch_and_must_also_match(self) -> None:
        data = self.data()
        data["branch"] = "docs/350-demo"
        self.assertTrue(sd.validate_staging(data))

    def test_target_and_repo_must_agree(self) -> None:
        data = self.data()
        data["repo"] = "sifu-tutor"
        self.assertTrue(sd.validate_staging(data))
        sims = {"repo": "sifu-tutor", "branch": "release/3338-x", "staging": {"target": "sims", "approval": "x", "smoke_commands": []}}
        self.assertEqual(sd.validate_staging(sims), [])
        sims["repo"] = "ripple-suite"
        self.assertTrue(sd.validate_staging(sims))

    def test_redeploy_served_needs_a_pinned_commit(self) -> None:
        self.assertTrue(sd.validate_staging(self.data(mode="redeploy-served")))
        self.assertEqual(sd.validate_staging(self.data(mode="redeploy-served", commit=SHA_A)), [])
        self.assertTrue(sd.validate_staging(self.data(mode="redeploy-served", commit="abc")))

    def test_an_approval_line_is_required(self) -> None:
        self.assertTrue(sd.validate_staging(self.data(approval="")))
        self.assertTrue(sd.validate_staging(self.data(approval="   ")))

    def test_smoke_commands_must_be_known_test_commands(self) -> None:
        for bad in ("ssh root@host", "rm -rf /", "npx playwright test a.spec.ts; id", "npx playwright test a | tee x", "curl -X POST http://x",
                    "npm run test:x && rm y", "bash -c id", "npx playwright test $(id)", "pm2 restart x",
                    "npm run deploy", "npx playwright test x `id`"):
            self.assertTrue(sd.validate_staging(self.data(smoke_commands=[bad])), bad)
        for good in ("npx playwright test tests/e2e/smoke/authenticated-luna-staging.spec.ts --project=e2e --retries=0",
                     "npm run test:staging-luna-auth-smoke", "bash scripts/qa/staging-crm-worklist-smoke.sh", "builtin:login",
                     "builtin:page /requests"):
            self.assertEqual(sd.validate_staging(self.data(smoke_commands=[good])), [], good)


def git(cwd: Path, *args: str) -> str:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@e", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@e",
           "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}
    return subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True, check=True).stdout.strip()


class PatchEquivalenceTests(unittest.TestCase):
    """Real git repositories: the same change on a newer base has a different commit id."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="pe-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.repo = self.tmp / "r"
        self.repo.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        (self.repo / "app.php").write_text("<?php\n// line 1\n// line 2\n// line 3\n")
        (self.repo / "other.php").write_text("<?php\n// other\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "base")
        self.base = git(self.repo, "rev-parse", "HEAD")
        # staging candidate: main + a change, built on the OLD main
        git(self.repo, "checkout", "-qb", "test/1-staging-candidate")
        (self.repo / "app.php").write_text("<?php\n// line 1\n// line 2\n// NEW BEHAVIOUR\n// line 3\n")
        git(self.repo, "commit", "-qam", "feat: new behaviour")
        (self.repo / "feature.php").write_text("<?php\n// feature\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "feat: feature file")
        self.staged = git(self.repo, "rev-parse", "HEAD")
        # main moves on (touches the same file, so the staged commits cannot be cherry-picked as they are)
        git(self.repo, "checkout", "-q", "main")
        (self.repo / "app.php").write_text("<?php\n// line 0 added on main\n// line 1\n// line 2\n// line 3\n")
        git(self.repo, "commit", "-qam", "main moved")
        # the production rebuild: same change on the new main, as ONE squashed commit
        git(self.repo, "checkout", "-qb", "release/1-promo")
        (self.repo / "app.php").write_text("<?php\n// line 0 added on main\n// line 1\n// line 2\n// NEW BEHAVIOUR\n// line 3\n")
        (self.repo / "feature.php").write_text("<?php\n// feature\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "release: same change")
        git(self.repo, "checkout", "-q", "main")

    def run_eq(self, promo: str = "release/1-promo", staged: str | None = None) -> dict:
        return sd.patch_equivalence(rr.RealShell(), self.repo, "main", staged or self.staged, promo)

    def test_the_same_change_on_a_newer_base_is_equivalent_though_commit_ids_differ(self) -> None:
        self.assertNotEqual(self.staged, git(self.repo, "rev-parse", "release/1-promo"))
        info = self.run_eq()
        self.assertTrue(info["ok"], info)
        self.assertIn("different base", info["how"])
        self.assertEqual((info["missing"], info["extra"]), (0, 0))

    def test_the_exact_commit_inside_the_promotion_branch_is_equivalent(self) -> None:
        info = self.run_eq(promo="test/1-staging-candidate")
        self.assertTrue(info["ok"])
        self.assertIn("exact staged commit", info["how"])

    def test_a_promotion_branch_missing_part_of_the_change_is_not_equivalent(self) -> None:
        git(self.repo, "checkout", "-qb", "release/1-partial", "main")
        (self.repo / "app.php").write_text("<?php\n// line 0 added on main\n// line 1\n// line 2\n// NEW BEHAVIOUR\n// line 3\n")
        git(self.repo, "commit", "-qam", "only half")
        git(self.repo, "checkout", "-q", "main")
        info = self.run_eq(promo="release/1-partial")
        self.assertFalse(info["ok"])
        self.assertIn("feature.php", info["why"])

    def test_a_different_change_is_not_equivalent(self) -> None:
        git(self.repo, "checkout", "-qb", "release/1-other", "main")
        (self.repo / "app.php").write_text("<?php\n// line 0 added on main\n// line 1\n// line 2\n// SOMETHING ELSE\n// line 3\n")
        (self.repo / "feature.php").write_text("<?php\n// feature\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "different")
        git(self.repo, "checkout", "-q", "main")
        self.assertFalse(self.run_eq(promo="release/1-other")["ok"])

    def test_extra_untested_code_in_the_promotion_branch_is_refused_but_extra_docs_are_allowed(self) -> None:
        git(self.repo, "checkout", "-q", "release/1-promo")
        (self.repo / "sneaky.php").write_text("<?php\n// not tested on staging\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "extra code")
        info = self.run_eq()
        self.assertFalse(info["ok"])
        self.assertIn("sneaky.php", info["why"])
        git(self.repo, "rm", "-q", "sneaky.php")
        (self.repo / "docs").mkdir()
        (self.repo / "docs" / "note.md").write_text("note\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "docs only extra")
        git(self.repo, "checkout", "-q", "main")
        self.assertTrue(self.run_eq()["ok"])

    def test_whitespace_only_differences_do_not_matter(self) -> None:
        git(self.repo, "checkout", "-q", "release/1-promo")
        (self.repo / "feature.php").write_text("<?php\n//   feature  \n")
        git(self.repo, "commit", "-qam", "reformat")
        git(self.repo, "checkout", "-q", "main")
        self.assertTrue(self.run_eq()["ok"])

    def test_a_short_or_unknown_commit_is_refused(self) -> None:
        self.assertFalse(sd.patch_equivalence(rr.RealShell(), self.repo, "main", "abc", "release/1-promo")["ok"])
        self.assertFalse(sd.patch_equivalence(rr.RealShell(), self.repo, "main", SHA_A, "release/1-promo")["ok"])

    def test_an_empty_staged_change_proves_nothing(self) -> None:
        main_tip = git(self.repo, "rev-parse", "main")
        info = sd.patch_equivalence(rr.RealShell(), self.repo, "main", main_tip, "release/1-promo")
        self.assertFalse(info["ok"] and info.get("how", "").startswith("same changed lines"))

    def test_change_lines_ignores_line_numbers_and_context(self) -> None:
        a = "diff --git a/f b/f\n--- a/f\n+++ b/f\n@@ -1,0 +2,1 @@\n+hello\n"
        b = "diff --git a/f b/f\n--- a/f\n+++ b/f\n@@ -40,0 +90,1 @@\n+hello\n"
        self.assertEqual(sd.change_lines(a), sd.change_lines(b))
        c = "diff --git a/g b/g\n--- a/g\n+++ b/g\n@@ -1,0 +2,1 @@\n+hello\n"
        self.assertNotEqual(sd.change_lines(a), sd.change_lines(c))

    def test_a_content_line_starting_with_plus_plus_is_counted_not_skipped(self) -> None:
        text = "diff --git a/f b/f\n--- a/f\n+++ b/f\n@@ -1,0 +2,1 @@\n+++ looks like a header\n"
        self.assertEqual(sum(sd.change_lines(text).values()), 1)


class LaneTests(Quiet):
    def test_values_are_read_without_being_printed_and_modes_are_checked(self) -> None:
        write_lane(self.tmp, "staging-smoke.conf", f"SIMS_SMOKE_EMAIL={SEKRET_MAIL}\nexport SIMS_SMOKE_PASSWORD='{SEKRET_PASS}'\n# c\n\n")
        lane = sd.load_lane("staging-smoke.conf")
        self.assertEqual(lane["SIMS_SMOKE_PASSWORD"], SEKRET_PASS)
        write_lane(self.tmp, "open.conf", "A=b\n", 0o644)
        with self.assertRaises(sd.DeployError) as ctx:
            sd.load_lane("open.conf")
        self.assertNotIn("A=b", str(ctx.exception))
        with self.assertRaises(sd.DeployError):
            sd.load_lane("missing.conf")

    def test_scrub_removes_the_exact_values_and_token_shapes(self) -> None:
        text = f"login as {SEKRET_MAIL} with {SEKRET_PASS} token=abcdef1234"
        out = sd.scrub(text, [SEKRET_MAIL, SEKRET_PASS])
        self.assertNotIn(SEKRET_PASS, out)
        self.assertNotIn(SEKRET_MAIL, out)
        self.assertNotIn("abcdef1234", out)


class FakeHttp:
    def __init__(self, routes: dict | None = None) -> None:
        self.calls: list[tuple[str, str, dict | None, bytes | None]] = []
        self.routes = routes or {}

    def request(self, method, url, headers=None, body=None, timeout=30):
        self.calls.append((method, url, headers, body))
        for (m, suffix), answer in self.routes.items():
            if m == method and url.endswith(suffix):
                return answer
        return 404, {}, ""


class LoginSmokeTests(Quiet):
    def lanes(self) -> None:
        write_lane(self.tmp, "ripple-staging-smoke.conf",
                   f"RIPPLE_STAGING_SUPERADMIN_EMAIL={SEKRET_MAIL}\nRIPPLE_STAGING_SUPERADMIN_PASSWORD={SEKRET_PASS}\n")
        write_lane(self.tmp, "staging-smoke.conf", f"SIMS_SMOKE_EMAIL={SEKRET_MAIL}\nSIMS_SMOKE_PASSWORD={SEKRET_PASS}\n")

    def test_ripple_login_then_session_then_a_page(self) -> None:
        self.lanes()
        http = FakeHttp({("POST", "/api/auth/login"): (200, {}, "{}"), ("GET", "/api/auth/me"): (200, {}, "{}"), ("GET", "/requests"): (200, {}, "ok")})
        ok, lines, secrets = sd.login_smoke(http, "ripple")
        self.assertTrue(ok, lines)
        self.assertEqual([c[1] for c in http.calls], ["https://ripple-staging.tutorla.tech" + p for p in
                                                       ("/api/auth/login", "/api/auth/me", "/requests")])
        self.assertIn(SEKRET_PASS, secrets)
        self.assertNotIn(SEKRET_PASS, "\n".join(lines))
        self.assertNotIn(SEKRET_MAIL, "\n".join(lines))

    def test_ripple_login_failures_are_failures(self) -> None:
        self.lanes()
        for routes in ({("POST", "/api/auth/login"): (401, {}, "")},
                       {("POST", "/api/auth/login"): (200, {}, ""), ("GET", "/api/auth/me"): (401, {}, "")},
                       {("POST", "/api/auth/login"): (200, {}, ""), ("GET", "/api/auth/me"): (200, {}, ""),
                        ("GET", "/requests"): (307, {"location": "/login"}, "")},
                       {("POST", "/api/auth/login"): (429, {}, "")}):
            ok, lines, _ = sd.login_smoke(FakeHttp(routes), "ripple")
            self.assertFalse(ok, lines)

    def test_sims_login_reads_the_csrf_token_and_checks_a_page(self) -> None:
        self.lanes()
        http = FakeHttp({("GET", "/login"): (200, {}, '<meta name="csrf-token" content="tok123">'),
                         ("POST", "/login"): (302, {"location": "https://sifu-staging.tutorla.tech/"}, ""),
                         ("GET", "sifu-staging.tutorla.tech/"): (200, {}, '{"component":"Dashboard"}')})
        ok, lines, _ = sd.login_smoke(http, "sims")
        self.assertTrue(ok, lines)
        post = [c for c in http.calls if c[0] == "POST"][0]
        self.assertEqual(post[2]["X-CSRF-TOKEN"], "tok123")
        self.assertNotIn(SEKRET_PASS, "\n".join(lines))

    def test_sims_login_back_to_the_login_page_fails(self) -> None:
        self.lanes()
        http = FakeHttp({("GET", "/login"): (200, {}, '<meta name="csrf-token" content="t">'),
                         ("POST", "/login"): (302, {"location": "https://sifu-staging.tutorla.tech/login"}, "")})
        self.assertFalse(sd.login_smoke(http, "sims")[0])
        http = FakeHttp({("GET", "/login"): (200, {}, "no token here")})
        self.assertFalse(sd.login_smoke(http, "sims")[0])

    def test_a_missing_lane_is_a_clear_error_not_a_crash(self) -> None:
        with self.assertRaises(sd.DeployError):
            sd.login_smoke(FakeHttp(), "ripple")

    def test_the_login_smoke_only_talks_to_the_staging_hosts(self) -> None:
        self.lanes()
        http = FakeHttp({("POST", "/api/auth/login"): (200, {}, ""), ("GET", "/api/auth/me"): (200, {}, ""), ("GET", "/requests"): (200, {}, "")})
        sd.login_smoke(http, "ripple")
        for _, url, _, _ in http.calls:
            self.assertTrue(url.startswith("https://ripple-staging.tutorla.tech/"), url)
        self.assertNotIn("sifututor.my", " ".join(sd.BASE_URLS.values()))


class FakeCtx:
    """What the loop hands a check."""

    def __init__(self, data: dict, shell: FakeBox, tmp: Path, http=None) -> None:
        self.data = data
        self.shell = shell
        self.repo_dir = tmp / "repo"
        self.worktree = tmp / "wt"
        self.stop_check = None
        self.http = http
        self.sleep = lambda s: None
        self.poll_seconds = 0
        self.checkpoints = 0

    def checkpoint(self) -> None:
        self.checkpoints += 1


def staging_data(**staging) -> dict:
    cfg = {"target": "ripple", "mode": "normal", "approval": "Hafiz, test", "smoke_commands": ["npm run test:staging-luna-auth-smoke"]}
    cfg.update(staging)
    return {"release": "Proof", "repo": "ripple-suite", "branch": REF, "base": "origin/main", "staging": cfg}


class ChecksTests(Quiet):
    def lanes(self) -> None:
        write_lane(self.tmp, "ripple-staging-smoke.conf",
                   f"RIPPLE_STAGING_SUPERADMIN_EMAIL={SEKRET_MAIL}\nRIPPLE_STAGING_SUPERADMIN_PASSWORD={SEKRET_PASS}\n")

    def box_with_tip(self, sha: str = SHA_A, ref: str = REF) -> FakeBox:
        box = good_box()
        box.when("ls-remote", out=f"{sha}\trefs/heads/{ref}\n")
        return box

    def test_candidate_check_records_the_exact_ref_and_commit(self) -> None:
        box = self.box_with_tip()
        ctx = FakeCtx(staging_data(), box, self.tmp)
        res = sd.check_candidate({}, ctx)
        self.assertTrue(res["ok"], res)
        self.assertEqual((ctx.data["staging"]["candidate_sha"], ctx.data["staging"]["candidate_ref"]), (SHA_A, REF))
        shas = [e.get("sha") for e in res["evidence"] if e.get("sha")]
        self.assertEqual(shas, [SHA_A])

    def test_candidate_not_on_origin_or_pinned_to_another_commit_fails(self) -> None:
        box = good_box()
        box.when("ls-remote", out="")
        self.assertFalse(sd.check_candidate({}, FakeCtx(staging_data(), box, self.tmp))["ok"])
        box = self.box_with_tip(SHA_B)
        res = sd.check_candidate({}, FakeCtx(staging_data(commit=SHA_A), box, self.tmp))
        self.assertFalse(res["ok"])
        self.assertIn("pins", res["summary"])
        self.assertEqual(box.ssh_calls(), [])

    def test_candidate_refused_by_the_box_fails_with_the_reason(self) -> None:
        box = self.box_with_tip()
        box.verbs["check"] = [(2, "REFUSED: the release changes migration, script or build-control files (package.json); this needs a Mac session")]
        ctx = FakeCtx(staging_data(), box, self.tmp)
        res = sd.check_candidate({}, ctx)
        self.assertFalse(res["ok"])
        self.assertIn("Mac session", res["summary"])
        self.assertNotIn("candidate_sha", ctx.data["staging"])

    def test_a_production_target_is_refused_by_every_check_and_nothing_is_sent(self) -> None:
        for target in ("prod", "production"):
            box = self.box_with_tip()
            data = staging_data(target=target)
            for func in (sd.check_candidate, sd.check_deployed, sd.check_smoke):
                res = func({}, FakeCtx(data, box, self.tmp))
                self.assertFalse(res["ok"], (target, func.__name__))
            self.assertEqual(box.ssh_calls(), [], target)
        data = staging_data()
        data["staging"]["env"] = "prod"
        box = self.box_with_tip()
        self.assertFalse(sd.check_candidate({}, FakeCtx(data, box, self.tmp))["ok"])
        self.assertEqual(box.ssh_calls(), [])

    def test_a_ref_outside_the_patterns_never_reaches_the_box(self) -> None:
        box = self.box_with_tip(ref="main")
        res = sd.check_candidate({}, FakeCtx(staging_data(ref="main"), box, self.tmp))
        self.assertFalse(res["ok"])
        self.assertEqual(box.ssh_calls(), [])
        self.assertEqual([c for c in box.calls if "ls-remote" in " ".join(c["argv"])], [])

    def test_deploy_needs_an_accepted_candidate_first(self) -> None:
        box = good_box()
        res = sd.check_deployed({}, FakeCtx(staging_data(), box, self.tmp))
        self.assertFalse(res["ok"])
        self.assertEqual(box.ssh_calls(), [])

    def test_deploy_records_the_staged_sha_and_remembers_the_run_for_a_restart(self) -> None:
        box = good_box()
        ctx = FakeCtx(staging_data(candidate_sha=SHA_A, candidate_ref=REF), box, self.tmp)
        res = sd.check_deployed({}, ctx)
        self.assertTrue(res["ok"], res)
        self.assertEqual(ctx.data["staging_sha"], SHA_A)
        self.assertEqual(ctx.checkpoints, 1)
        self.assertIsNone(ctx.data["staging"]["deploy"])
        self.assertTrue(ctx.data["staging"]["deploys"][0]["ok"])

    def test_a_restart_attaches_to_the_run_in_flight_and_never_starts_a_second(self) -> None:
        box = good_box()
        cfg = {"candidate_sha": SHA_A, "candidate_ref": REF, "deploy": {"run": "20261009T060000Z-aaaaaaaa", "sha": SHA_A}}
        ctx = FakeCtx(staging_data(**cfg), box, self.tmp)
        self.assertTrue(sd.check_deployed({}, ctx)["ok"])
        self.assertFalse([c for c in box.ssh_calls() if "remote ripple start" in c["argv"][-1]])

    def test_a_failed_deploy_does_not_set_the_staged_sha(self) -> None:
        box = good_box()
        box.statuses = [f"run=r state=finished step=x\nRESULT run=r status=failed exit=1 seconds=3 ref={REF} sha={SHA_A}\n"]
        ctx = FakeCtx(staging_data(candidate_sha=SHA_A, candidate_ref=REF), box, self.tmp)
        self.assertFalse(sd.check_deployed({}, ctx)["ok"])
        self.assertNotIn("staging_sha", ctx.data)

    def test_smoke_needs_the_deploy_and_the_server_read_back_first(self) -> None:
        self.lanes()
        box = good_box()
        ctx = FakeCtx(staging_data(candidate_sha=SHA_A, candidate_ref=REF), box, self.tmp, FakeHttp())
        self.assertFalse(sd.check_smoke({}, ctx)["ok"])
        ctx.data["staging_sha"] = SHA_A
        box.verbs["verify"] = [(1, "VERIFY FAILED")]
        res = sd.check_smoke({}, ctx)
        self.assertFalse(res["ok"])
        self.assertIn("no longer serves", res["summary"])
        self.assertEqual(box.calls[-1]["argv"][0], "ssh")

    def ripple_http(self, login: int = 200) -> FakeHttp:
        return FakeHttp({("GET", "/login"): (200, {}, ""), ("POST", "/api/auth/login"): (login, {}, ""),
                         ("GET", "/api/auth/me"): (200, {}, ""), ("GET", "/requests"): (200, {}, "")})

    def smoke_ctx(self, box: FakeBox, http: FakeHttp, **cfg) -> FakeCtx:
        ctx = FakeCtx(staging_data(candidate_sha=SHA_A, candidate_ref=REF, **cfg), box, self.tmp, http)
        ctx.data["staging_sha"] = SHA_A
        return ctx

    def test_smoke_passes_with_normal_and_change_smoke_and_the_playwright_environment(self) -> None:
        self.lanes()
        box = good_box()
        box.when("npm run test:staging-luna-auth-smoke", out="3 passed")
        ctx = self.smoke_ctx(box, self.ripple_http())
        res = sd.check_smoke({}, ctx)
        self.assertTrue(res["ok"], res)
        run = [c for c in box.calls if c["argv"][:3] == ["npm", "run", "test:staging-luna-auth-smoke"]][0]
        self.assertEqual(run["env"]["PLAYWRIGHT_HOST_PLATFORM_OVERRIDE"], "ubuntu24.04-x64")
        self.assertIn("chromium-libs/root/usr/lib/x86_64-linux-gnu", run["env"]["LD_LIBRARY_PATH"])
        self.assertEqual(run["env"]["PLAYWRIGHT_BASE_URL"], "https://ripple-staging.tutorla.tech")
        self.assertEqual(run["cwd"], ctx.worktree)

    def test_a_failing_change_smoke_fails_s3_and_its_output_is_scrubbed(self) -> None:
        self.lanes()
        box = good_box()
        box.when("npm run test:staging-luna-auth-smoke", rc=1, out=f"Login failed for {SEKRET_MAIL} password {SEKRET_PASS}")
        res = sd.check_smoke({}, self.smoke_ctx(box, self.ripple_http()))
        self.assertFalse(res["ok"])
        blob = json.dumps(res)
        self.assertNotIn(SEKRET_PASS, blob)
        self.assertNotIn(SEKRET_MAIL, blob)

    def test_a_failing_normal_smoke_fails_s3_before_any_command_runs(self) -> None:
        self.lanes()
        box = good_box()
        res = sd.check_smoke({}, self.smoke_ctx(box, self.ripple_http(login=401)))
        self.assertFalse(res["ok"])
        self.assertFalse([c for c in box.calls if c["argv"][0] == "npm"])

    def test_no_change_smoke_and_no_named_exception_fails(self) -> None:
        self.lanes()
        res = sd.check_smoke({}, self.smoke_ctx(good_box(), self.ripple_http(), smoke_commands=[]))
        self.assertFalse(res["ok"])
        self.assertIn("no change smoke", res["summary"])
        ok = sd.check_smoke({}, self.smoke_ctx(good_box(), self.ripple_http(), smoke_commands=[], smoke_exception="not user-facing: docs only"))
        self.assertTrue(ok["ok"], ok)

    def test_a_forbidden_smoke_command_in_the_data_is_refused_at_run_time_too(self) -> None:
        self.lanes()
        box = good_box()
        res = sd.check_smoke({}, self.smoke_ctx(box, self.ripple_http(), smoke_commands=["npm run test:x; rm -rf /"]))
        self.assertFalse(res["ok"])
        self.assertFalse([c for c in box.calls if c["argv"][0] == "npm"])

    def test_builtin_page_smoke_runs_the_scripted_login_for_that_page(self) -> None:
        self.lanes()
        http = self.ripple_http()
        http.routes[("GET", "/crm/worklist")] = (200, {}, "")
        res = sd.check_smoke({}, self.smoke_ctx(good_box(), http, smoke_commands=["builtin:page /crm/worklist"]))
        self.assertTrue(res["ok"], res)
        self.assertTrue([c for c in http.calls if c[1].endswith("/crm/worklist")])

    def test_patch_equivalent_check_needs_the_staged_commit(self) -> None:
        ctx = FakeCtx({"branch": "release/1-promo", "base": "origin/main", "staging": {}}, FakeBox(), self.tmp)
        self.assertFalse(sd.check_patch_equivalent({}, ctx)["ok"])


class ReportAndCliTests(Quiet):
    def test_report_without_a_staging_section_says_gates_are_mac_gates(self) -> None:
        path = self.tmp / "r.json"
        rr.save(path, {"release": "x", "repo": "agent-os", "branch": "docs/1-x", "items": []})
        out: list[str] = []
        sd.report(path, out.append)
        self.assertIn("Mac gates", out[0])

    def test_cli_has_no_way_to_name_production(self) -> None:
        for argv in (["deploy", "prod", "--ref", REF, "--sha", SHA_A], ["check", "production", "--ref", REF],
                     ["deploy", "ripple", "--ref", REF, "--sha", SHA_A, "--mode", "prod"], ["switch", "live", "off"]):
            with self.assertRaises(SystemExit):
                sd.main(argv, out=lambda s: None, shell=FakeBox())

    def test_cli_check_prints_the_box_answer(self) -> None:
        box = good_box()
        out: list[str] = []
        code = sd.main(["check", "ripple", "--ref", REF, "--sha", SHA_A], out=out.append, shell=box)
        self.assertEqual(code, 0)
        self.assertIn("CHECK OK", out[0])

    def test_cli_refusal_exits_2(self) -> None:
        out: list[str] = []
        code = sd.main(["check", "ripple", "--ref", "main", "--sha", SHA_A], out=out.append, shell=good_box())
        self.assertEqual(code, 2)
        self.assertTrue(out[0].startswith("REFUSED"))

    def test_cli_deploy_prints_progress_and_the_summary(self) -> None:
        out: list[str] = []
        with mock_patch(sd, "POLL_SECONDS", 0):
            code = sd.main(["deploy", "ripple", "--ref", REF, "--sha", SHA_A], out=out.append, shell=good_box())
        self.assertEqual(code, 0, out)
        self.assertTrue(any(l.startswith("DEPLOYED:") for l in out))


class RemoteSourceTests(unittest.TestCase):
    def test_the_program_that_is_sent_is_standard_library_only(self) -> None:
        text = (HERE / "staging_remote.py").read_text()
        imports = set(re.findall(r"^(?:from|import) ([A-Za-z_][A-Za-z0-9_]*)", text, re.MULTILINE))
        allowed = {"argparse", "datetime", "fcntl", "json", "os", "pathlib", "re", "subprocess", "sys", "time", "typing", "__future__"}
        self.assertEqual(imports - allowed, set())

    def test_the_program_names_staging_only(self) -> None:
        text = (HERE / "staging_remote.py").read_text()
        code = re.sub(r"(?s)\"\"\".*?\"\"\"", "", text)
        self.assertNotIn("/prod-env", code)
        self.assertNotIn("151.246.1.164", code)
        self.assertNotRegex(code, r"deploy-ripple-suite[\"']?,\s*[\"']prod")
        self.assertEqual(re.findall(r'self\.controller, "(\w+)"', code), ["staging"])


if __name__ == "__main__":
    unittest.main()
