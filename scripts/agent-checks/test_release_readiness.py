#!/usr/bin/env python3
"""Tests for the release readiness file, its scoring and its scripted checks (issue #350)."""

from __future__ import annotations

import copy
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import release_readiness as rr  # noqa: E402

TEMPLATE = json.loads(rr.TEMPLATE_PATH.read_text())


def item(iid: str, owner: str = "pc", status: str = "open", **extra) -> dict:
    base = {"id": iid, "title": f"Item {iid}", "owner": owner, "status": status, "applicable": True,
            "action": "script", "depends_on": [], "evidence": []}
    base.update(extra)
    return base


def readiness(items: list[dict], **extra) -> dict:
    data = {"release": "demo", "repo": "agent-os", "github_repo": "o/r", "branch": "docs/1-demo",
            "base": "origin/main", "items": items, "loop": {}}
    data.update(extra)
    return data


class FakeShell:
    def __init__(self, rules=None) -> None:
        self.calls: list[tuple[list[str], str | None]] = []
        self.rules = rules or []

    def run(self, argv, cwd=None, stop_check=None):
        self.calls.append((list(argv), str(cwd) if cwd else None))
        for match, response in self.rules:
            if match(argv):
                return response(argv) if callable(response) else response
        return 0, ""


def context(data: dict, tmp: Path, shell, worktree: Path | None = None) -> rr.CheckContext:
    pack = tmp / "release-pack"
    pack.mkdir(exist_ok=True)
    return rr.CheckContext(data, pack, worktree or tmp, tmp, shell)


# ----------------------------------------------- properties used twice ------
# Each helper states one rule. The real test passes the real implementation; a
# negative control passes a deliberately wrong one and must see the helper fail.

def assert_gates_never_count(score_fn) -> None:
    pc_only = readiness([item("1", status="green"), item("2"), item("3", status="na", applicable=False, na_reason="x")])
    with_gates = copy.deepcopy(pc_only)
    with_gates["items"] += [item("G1", owner="hafiz", status="green", action="none"),
                            item("G2", owner="mac", status="green", action="none")]
    a, b = score_fn(pc_only), score_fn(with_gates)
    assert a["percent"] == 50.0, f"1 of 2 applicable PC items is 50 percent, got {a['percent']}"
    assert b["percent"] == a["percent"], f"green gates changed PC readiness from {a['percent']} to {b['percent']}"
    assert b["pc_total"] == 2, f"gates or n/a items were counted into the total: {b['pc_total']}"
    open_gates = copy.deepcopy(with_gates)
    for gate in open_gates["items"]:
        if gate["owner"] != "pc":
            gate["status"] = "open"
    done = copy.deepcopy(open_gates)
    done["items"][1]["status"] = "green"
    assert score_fn(done)["ready"] is True, "open gates must not stop PC readiness reaching 100"


def assert_failing_command_is_never_green(check_fn, tmp: Path) -> None:
    shell = FakeShell([(lambda argv: argv[:1] == ["falsy"], (3, "tests failed"))])
    check = {"type": "commands_exit_zero", "commands": ["truthy ok", "falsy"]}
    res = check_fn(check, context(readiness([]), tmp, shell))
    assert res["ok"] is False, "a command that exited 3 was reported green"
    codes = [e["exit_code"] for e in res["evidence"]]
    assert codes == [0, 3], f"the real exit codes must be kept, got {codes}"


# ------------------------------------------------------------------ tests --

class ScoringTest(unittest.TestCase):
    def test_gates_and_not_applicable_items_never_count(self) -> None:
        assert_gates_never_count(rr.score)

    def test_negative_control_a_scorer_that_counts_hafiz_gates_is_caught(self) -> None:
        def counts_gates(data):
            items = [i for i in data["items"] if rr.is_applicable(i)]
            green = [i for i in items if i["status"] == "green"]
            total = len(items)
            return {"percent": round(100.0 * len(green) / total, 1), "pc_total": total,
                    "ready": len(green) == total}
        with self.assertRaises(AssertionError):
            assert_gates_never_count(counts_gates)

    def test_percent_open_blocked_and_ready(self) -> None:
        data = readiness([item("1", status="green"), item("2"), item("3", status="blocked"), item("4", status="green"),
                          item("5", status="na", applicable=False, na_reason="docs only")])
        s = rr.score(data)
        self.assertEqual((s["pc_green"], s["pc_total"], s["percent"]), (2, 4, 50.0))
        self.assertEqual(s["open_pc"], ["2"])
        self.assertEqual(s["blocked_pc"], ["3"])
        self.assertFalse(s["ready"])
        data["items"][1]["status"] = "green"
        data["items"][2]["status"] = "green"
        self.assertTrue(rr.score(data)["ready"])
        self.assertEqual(rr.score(data)["percent"], 100.0)

    def test_one_third_rounds_to_one_decimal(self) -> None:
        data = readiness([item("1", status="green"), item("2"), item("3")])
        self.assertEqual(rr.score(data)["percent"], 33.3)

    def test_gates_are_listed_with_their_owner(self) -> None:
        data = readiness([item("1"), item("G1", owner="hafiz", action="none"), item("G2", owner="mac", action="none")])
        self.assertEqual([(g["id"], g["owner"]) for g in rr.score(data)["gates"]], [("G1", "hafiz"), ("G2", "mac")])


class NextItemTest(unittest.TestCase):
    def test_picks_first_open_item_whose_dependencies_are_green(self) -> None:
        data = readiness([item("1", depends_on=["2"]), item("2"), item("3")])
        self.assertEqual(rr.next_item(data)["id"], "2")
        data["items"][1]["status"] = "green"
        self.assertEqual(rr.next_item(data)["id"], "1")

    def test_a_dependency_that_is_not_applicable_does_not_block(self) -> None:
        data = readiness([item("1", depends_on=["2"]), item("2", status="na", applicable=False, na_reason="x")])
        self.assertEqual(rr.next_item(data)["id"], "1")

    def test_a_dependency_on_a_hafiz_gate_never_runs(self) -> None:
        data = readiness([item("1", depends_on=["G1"]), item("G1", owner="hafiz", action="none")])
        self.assertIsNone(rr.next_item(data))

    def test_blocked_and_gate_items_are_never_next(self) -> None:
        data = readiness([item("1", status="blocked"), item("G1", owner="hafiz", action="none")])
        self.assertIsNone(rr.next_item(data))


class ValidateTest(unittest.TestCase):
    def test_good_file_has_no_errors(self) -> None:
        self.assertEqual(rr.validate(readiness([item("1")])), [])

    def test_problems_are_named(self) -> None:
        data = readiness([item("1", owner="bob"), item("1"), item("2", status="weird"),
                          item("3", status="na", applicable=False), item("4", depends_on=["99"]),
                          item("5", action="banana")])
        text = " ".join(rr.validate(data))
        for fragment in ("owner must be", "duplicated", "status must be", "na_reason", "does not exist", "action must be"):
            self.assertIn(fragment, text)

    def test_an_action_that_names_a_forbidden_step_is_valid_so_the_loop_can_hand_it_over(self) -> None:
        self.assertEqual(rr.validate(readiness([item("1", action="merge"), item("2", action="deploy")])), [])

    def test_cycle_is_an_error(self) -> None:
        data = readiness([item("1", depends_on=["2"]), item("2", depends_on=["1"])])
        self.assertIn("cycle", " ".join(rr.validate(data)))

    def test_release_branch_cannot_be_main_or_the_base(self) -> None:
        self.assertIn("protected", " ".join(rr.validate(readiness([item("1")], branch="main"))))
        self.assertIn("protected", " ".join(rr.validate(readiness([item("1")], branch="develop", base="origin/develop"))))


class FileTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_save_and_load_round_trip(self) -> None:
        data = readiness([item("1")])
        rr.save(self.tmp / "r.json", data)
        self.assertEqual(rr.load(self.tmp / "r.json"), data)

    def test_save_is_atomic_a_failed_replace_leaves_the_old_file(self) -> None:
        path = self.tmp / "r.json"
        rr.save(path, readiness([item("1")]))
        before = path.read_text()
        with mock.patch("release_readiness.os.replace", side_effect=OSError("disk gone")):
            with self.assertRaises(OSError):
                rr.save(path, readiness([item("1", status="green")]))
        self.assertEqual(path.read_text(), before)
        self.assertEqual(json.loads(before)["items"][0]["status"], "open")

    def test_save_never_writes_the_target_directly(self) -> None:
        path = self.tmp / "r.json"
        rr.save(path, readiness([item("1")]))
        opened: list[str] = []
        real_open = open

        def spy(file, *args, **kwargs):
            opened.append(str(file))
            return real_open(file, *args, **kwargs)

        with mock.patch("builtins.open", spy):
            rr.save(path, readiness([item("1", status="green")]))
        self.assertNotIn(str(path), opened)
        self.assertTrue(any(name.endswith(".tmp") for name in opened))

    def test_load_rejects_a_file_that_is_not_readiness(self) -> None:
        (self.tmp / "x.json").write_text("{}")
        with self.assertRaises(rr.ReadinessError):
            rr.load(self.tmp / "x.json")


class EvidenceTest(unittest.TestCase):
    def test_a_repeat_is_not_new_evidence(self) -> None:
        it = item("1")
        self.assertTrue(rr.add_evidence(it, command="npm test", exit_code=1))
        self.assertFalse(rr.add_evidence(it, command="npm test", exit_code=1))
        self.assertTrue(rr.add_evidence(it, command="npm test", exit_code=0))
        self.assertEqual(len(it["evidence"]), 2)
        self.assertIn("MYT", it["evidence"][0]["at"])

    def test_a_pc_item_cannot_be_marked_green_without_evidence(self) -> None:
        with self.assertRaises(rr.ReadinessError):
            rr.set_status(item("1"), "green")
        it = item("1")
        rr.set_status(it, "green", note="checked by hand")
        self.assertEqual(it["status"], "green")


class CommandsCheckTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_a_failing_command_is_never_green_and_its_exit_code_is_kept(self) -> None:
        assert_failing_command_is_never_green(rr.check_commands_exit_zero, self.tmp)

    def test_negative_control_a_check_that_swallows_the_exit_code_is_caught(self) -> None:
        def swallows(check, ctx):
            evidence = []
            for command, _ in rr._commands(check):
                code, _out = ctx.shell.run(command.split(), cwd=ctx.worktree)
                evidence.append({"command": command, "exit_code": code})
            return rr.result(True, "all commands ran", evidence)  # wrong: ignores the code
        with self.assertRaises(AssertionError):
            assert_failing_command_is_never_green(swallows, self.tmp)

    def test_real_process_exit_code_three_is_kept(self) -> None:
        check = {"type": "commands_exit_zero", "commands": [f'{sys.executable} -c "import sys; print(1); sys.exit(3)"',
                                                            f'{sys.executable} -c "pass"']}
        res = rr.check_commands_exit_zero(check, context(readiness([]), self.tmp, rr.RealShell()))
        self.assertFalse(res["ok"])
        self.assertEqual([e["exit_code"] for e in res["evidence"]], [3, 0])
        self.assertIn("exit 3", res["summary"])

    def test_missing_program_is_a_failure_not_a_pass(self) -> None:
        check = {"type": "commands_exit_zero", "commands": ["definitely-not-a-program-xyz"]}
        res = rr.check_commands_exit_zero(check, context(readiness([]), self.tmp, rr.RealShell()))
        self.assertFalse(res["ok"])
        self.assertEqual(res["evidence"][0]["exit_code"], 127)

    def test_all_zero_is_green(self) -> None:
        res = rr.check_commands_exit_zero({"commands": ["a", "b"]}, context(readiness([]), self.tmp, FakeShell()))
        self.assertTrue(res["ok"])

    def test_baseline_failure_is_reported_separately_and_other_failures_still_count(self) -> None:
        shell = FakeShell([(lambda argv: argv[0] in ("lint", "tests"), (1, "bad"))])
        check = {"commands": [{"run": "lint", "baseline_reason": "known failing on main, issue 817"}, "typecheck"]}
        res = rr.check_commands_exit_zero(check, context(readiness([]), self.tmp, shell))
        self.assertTrue(res["ok"])
        self.assertIn("baseline failures reported separately", res["summary"])
        self.assertEqual(res["evidence"][0]["exit_code"], 1)
        self.assertIn("baseline_failure", res["evidence"][0])
        check["commands"].append("tests")
        self.assertFalse(rr.check_commands_exit_zero(check, context(readiness([]), self.tmp, shell))["ok"])

    def test_a_forbidden_command_is_refused_not_run(self) -> None:
        shell = FakeShell()
        res = rr.check_commands_exit_zero({"commands": ["gh pr merge 5"]}, context(readiness([]), self.tmp, shell))
        self.assertFalse(res["ok"])
        self.assertEqual(shell.calls, [])

    def test_output_tail_has_secret_looking_values_masked(self) -> None:
        shell = FakeShell([(lambda argv: True, (1, "API_TOKEN=abc123secret\nbearer abcdefghijkl\nok line"))])
        res = rr.check_commands_exit_zero({"commands": ["x"]}, context(readiness([]), self.tmp, shell))
        text = json.dumps(res)
        self.assertNotIn("abc123secret", text)
        self.assertNotIn("abcdefghijkl", text)
        self.assertIn("ok line", text)


class FileChecksTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        (self.tmp / "TESTING.md").write_text("row for issue 1630 covered\n")
        (self.tmp / ".env").write_text("SECRET=1\n")
        (self.tmp / "release-pack").mkdir()
        (self.tmp / "release-pack" / "r.md").write_text("**Verdict:** CHANGES NEEDED\nfinding\n")

    def ctx(self) -> rr.CheckContext:
        return context(readiness([]), self.tmp, FakeShell(), worktree=self.tmp)

    def test_file_contains_needle(self) -> None:
        self.assertTrue(rr.check_file_contains({"path": "TESTING.md", "needle": "1630"}, self.ctx())["ok"])
        res = rr.check_file_contains({"path": "TESTING.md", "needle": "9999"}, self.ctx())
        self.assertFalse(res["ok"])
        self.assertIn("9999", res["summary"])

    def test_file_contains_all_needles_and_any_of(self) -> None:
        self.assertTrue(rr.check_file_contains({"path": "TESTING.md", "needles": ["row", "covered"]}, self.ctx())["ok"])
        self.assertFalse(rr.check_file_contains({"path": "TESTING.md", "needles": ["row", "absent"]}, self.ctx())["ok"])
        self.assertTrue(rr.check_file_contains({"path": "TESTING.md", "any_of": ["nope", "COVERED"]}, self.ctx())["ok"])
        self.assertFalse(rr.check_file_contains({"path": "TESTING.md", "any_of": ["nope", "nada"]}, self.ctx())["ok"])

    def test_missing_file_fails(self) -> None:
        self.assertFalse(rr.check_file_contains({"path": "NOPE.md", "needle": "x"}, self.ctx())["ok"])

    def test_environment_files_paths_leaving_the_folder_and_key_files_are_never_read(self) -> None:
        for path in (".env", "../outside.txt", "/etc/hosts", "keys/server.pem", "id_rsa"):
            res = rr.check_file_contains({"path": path, "needle": "SECRET"}, self.ctx())
            self.assertFalse(res["ok"], path)
        (self.tmp / ".env.example").write_text("KEY=\n")
        self.assertTrue(rr.check_file_contains({"path": ".env.example", "needle": "KEY"}, self.ctx())["ok"])

    def test_pack_files_are_read_relative_to_the_release_folder(self) -> None:
        check = {"base": "pack", "path": "release-pack/r.md", "needle": "finding"}
        self.assertTrue(rr.check_file_contains(check, self.ctx())["ok"])

    def test_verdict_file_needs_accept(self) -> None:
        check = {"type": "verdict_file", "path": "release-pack/r.md"}
        res = rr.check_verdict_file(check, self.ctx())
        self.assertFalse(res["ok"])
        self.assertEqual(res["evidence"][0]["verdict"], "CHANGES NEEDED")
        (self.tmp / "release-pack" / "r.md").write_text("1. **Verdict:** ACCEPT\nall good\n")
        self.assertTrue(rr.check_verdict_file(check, self.ctx())["ok"])
        (self.tmp / "release-pack" / "r.md").write_text("no verdict here")
        self.assertFalse(rr.check_verdict_file(check, self.ctx())["ok"])
        self.assertFalse(rr.check_verdict_file({"path": "release-pack/missing.md"}, self.ctx())["ok"])


class PrAndCommitChecksTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def view(self, **info):
        payload = {"number": 12, "state": "OPEN", "headRefName": "docs/1-demo", "headRefOid": "a" * 40, "baseRefName": "main"}
        payload.update(info)
        return FakeShell([(lambda argv: argv[:3] == ["gh", "pr", "view"], (0, json.dumps(payload)))])

    def test_open_pr_on_the_release_branch_records_the_exact_sha(self) -> None:
        data = readiness([], pr_numbers=[12])
        res = rr.check_pr_exists({"type": "pr_exists"}, context(data, self.tmp, self.view()))
        self.assertTrue(res["ok"], res)
        self.assertEqual(res["evidence"][0]["sha"], "a" * 40)
        self.assertEqual(res["evidence"][0]["pr"], 12)

    def test_closed_merged_or_wrong_branch_pr_is_not_ok(self) -> None:
        data = readiness([], pr_numbers=[12])
        self.assertFalse(rr.check_pr_exists({}, context(data, self.tmp, self.view(state="MERGED")))["ok"])
        self.assertFalse(rr.check_pr_exists({}, context(data, self.tmp, self.view(headRefName="other")))["ok"])

    def test_gh_failure_is_not_ok(self) -> None:
        shell = FakeShell([(lambda argv: True, (1, "no such pr"))])
        res = rr.check_pr_exists({}, context(readiness([], pr_numbers=[12]), self.tmp, shell))
        self.assertFalse(res["ok"])
        self.assertEqual(res["evidence"][0]["exit_code"], 1)

    def test_branch_only_release_checks_the_branch_on_origin(self) -> None:
        shell = FakeShell([(lambda argv: argv[:2] == ["git", "ls-remote"], (0, "b" * 40 + "\trefs/heads/docs/1-demo\n"))])
        res = rr.check_pr_exists({}, context(readiness([]), self.tmp, shell))
        self.assertTrue(res["ok"])
        shell = FakeShell([(lambda argv: argv[:2] == ["git", "ls-remote"], (2, ""))])
        self.assertFalse(rr.check_pr_exists({}, context(readiness([]), self.tmp, shell))["ok"])

    def test_commit_in_branch_uses_the_real_exit_code(self) -> None:
        ok = FakeShell([(lambda argv: "merge-base" in argv, (0, ""))])
        no = FakeShell([(lambda argv: "merge-base" in argv, (1, ""))])
        check = {"type": "commit_in_branch", "sha": "abc1234"}
        self.assertTrue(rr.check_commit_in_branch(check, context(readiness([]), self.tmp, ok))["ok"])
        self.assertFalse(rr.check_commit_in_branch(check, context(readiness([]), self.tmp, no))["ok"])
        self.assertFalse(rr.check_commit_in_branch({"sha": "not a sha"}, context(readiness([]), self.tmp, ok))["ok"])

    def test_all_of_needs_every_part(self) -> None:
        data = readiness([], pr_numbers=[12])
        both = {"type": "all_of", "checks": [{"type": "pr_exists"}, {"type": "commit_in_branch", "sha": "abc1234"}]}
        shell = FakeShell([(lambda argv: argv[:3] == ["gh", "pr", "view"], (0, json.dumps(
            {"number": 12, "state": "OPEN", "headRefName": "docs/1-demo", "headRefOid": "a" * 40, "baseRefName": "main"}))),
            (lambda argv: "merge-base" in argv, (1, ""))])
        res = rr.run_check(both, context(data, self.tmp, shell))
        self.assertFalse(res["ok"])
        self.assertEqual(len(res["evidence"]), 2)

    def test_unknown_check_type_fails(self) -> None:
        self.assertFalse(rr.run_check({"type": "magic"}, context(readiness([]), self.tmp, FakeShell()))["ok"])


GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, env={**os.environ, **GIT_ENV}, capture_output=True, text=True, check=True).stdout


class FailingFirstTest(unittest.TestCase):
    """A real git repository: the check copies the release's tests onto the base and runs them there."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.origin = self.tmp / "origin.git"
        self.repo = self.tmp / "repo"
        git(self.tmp, "init", "-q", "--bare", "-b", "main", str(self.origin))
        git(self.tmp, "clone", "-q", str(self.origin), str(self.repo))
        git(self.repo, "checkout", "-q", "-b", "main")
        (self.repo / "feature.py").write_text("def f():\n    return 1\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "init")
        git(self.repo, "push", "-q", "origin", "main")
        git(self.repo, "checkout", "-q", "-b", "feat/1-demo")
        self.pack = self.tmp / "loop"
        self.pack.mkdir()

    def release(self, *, change_feature: bool, test_value: int) -> rr.CheckContext:
        if change_feature:
            (self.repo / "feature.py").write_text("def f():\n    return 2\n")
        (self.repo / "test_feature.py").write_text(
            f"import unittest\nimport feature\n\n\nclass T(unittest.TestCase):\n    def test_f(self):\n"
            f"        self.assertEqual(feature.f(), {test_value})\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "feat: change")
        git(self.repo, "push", "-q", "origin", "feat/1-demo")
        wt = self.tmp / "wt"
        git(self.repo, "worktree", "add", "-q", "--detach", str(wt), "origin/feat/1-demo")
        data = readiness([], branch="feat/1-demo", base="origin/main")
        return rr.CheckContext(data, self.pack / "release-pack", wt, self.repo, rr.RealShell())

    CHECK = {"type": "failing_first", "test_command": f"{sys.executable} -m unittest {{files}}", "install": []}

    def test_a_test_that_fails_on_the_base_and_passes_on_the_release_is_green(self) -> None:
        res = rr.check_failing_first(self.CHECK, self.release(change_feature=True, test_value=2))
        self.assertTrue(res["ok"], res)
        codes = [e["exit_code"] for e in res["evidence"]]
        self.assertNotEqual(codes[0], 0)
        self.assertEqual(codes[1], 0)
        self.assertFalse((self.pack / "scratch" / "failing-first").exists(), "the scratch checkout must be removed")

    def test_a_test_that_also_passes_on_the_base_proves_nothing(self) -> None:
        res = rr.check_failing_first(self.CHECK, self.release(change_feature=False, test_value=1))
        self.assertFalse(res["ok"])
        self.assertIn("PASS on the base", res["summary"])

    def test_a_test_that_fails_on_the_release_is_red(self) -> None:
        res = rr.check_failing_first(self.CHECK, self.release(change_feature=True, test_value=99))
        self.assertFalse(res["ok"])
        self.assertIn("fail on the release", res["summary"])

    def test_no_test_file_in_the_release_is_red(self) -> None:
        (self.repo / "notes.txt").write_text("x")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "docs: notes")
        git(self.repo, "push", "-q", "origin", "feat/1-demo")
        wt = self.tmp / "wt"
        git(self.repo, "worktree", "add", "-q", "--detach", str(wt), "origin/feat/1-demo")
        ctx = rr.CheckContext(readiness([], branch="feat/1-demo"), self.pack / "release-pack", wt, self.repo, rr.RealShell())
        res = rr.check_failing_first(self.CHECK, ctx)
        self.assertFalse(res["ok"])
        self.assertIn("no test file", res["summary"])


class ForbiddenTest(unittest.TestCase):
    FORBIDDEN = [
        "gh pr merge 12 --merge", "git merge origin/main", "git push origin main", "git push --force origin x",
        "git push origin HEAD:production", "php artisan migrate --force", "npx prisma migrate deploy",
        "npm run deploy", "./deploy.sh prod", "bash deploy-ripple.sh", "ssh root@server ls", "scp a b:/x",
        "mysql -e 'select 1'", "psql -c x", 'DELETE FROM invoices WHERE id=1', "curl -X POST https://x/api",
        "pm2 restart ripple", "set-runtime-flag foo on", "kubectl apply -f x",
    ]
    ALLOWED = [
        "npm run lint", "npx tsc --noEmit", "npm run test:unit", "python3 -m unittest discover -s scripts/agent-checks",
        "git push origin HEAD:refs/heads/feat/350-demo", "gh pr view 12 --json state", "git diff origin/main...HEAD",
        "python3 scripts/agent-checks/agent-os-doc-navigation-check.py", "npx vitest run src/a.test.ts",
        "curl https://example.com/health", "update the file set up", "write the deploy plan",
    ]

    def test_forbidden_commands_are_detected(self) -> None:
        for command in self.FORBIDDEN:
            self.assertIsNotNone(rr.forbidden_text(command), command)

    def test_ordinary_commands_and_prose_are_allowed(self) -> None:
        for command in self.ALLOWED:
            self.assertIsNone(rr.forbidden_text(command), command)

    def test_an_item_with_a_forbidden_check_or_action_is_flagged(self) -> None:
        bad = item("1", check={"type": "commands_exit_zero", "commands": ["npm run lint", "gh pr merge 3"]})
        self.assertIn("merge", rr.forbidden_in_item(bad))
        nested = item("1", check={"type": "all_of", "checks": [{"type": "commands_exit_zero", "commands": [{"run": "php artisan migrate"}]}]})
        self.assertIn("migrate", rr.forbidden_in_item(nested))
        self.assertIn("deploy", rr.forbidden_in_item(item("1", action="deploy")))
        self.assertIn("merge", rr.forbidden_in_item(item("1", action="builder", instruction="then run gh pr merge 4")))
        self.assertIsNone(rr.forbidden_in_item(item("1", check={"type": "commands_exit_zero", "commands": ["npm run lint"]})))

    def test_no_template_item_is_forbidden(self) -> None:
        for repo in rr.REPOS:
            data = rr.build_from_template(TEMPLATE, **init_args(repo))
            for it in data["items"]:
                self.assertIsNone(rr.forbidden_in_item(it), it["id"])


def init_args(repo: str, **override) -> dict:
    args = dict(release="Demo release", repo=repo, branch="feat/1-demo", base="origin/main", pr_numbers_=[5], issue="1",
                serving_commit="", approval="Hafiz, test", github_repo=None, suite_commands=None, e2e_commands=[],
                e2e_exception="not user-facing: test", fix_paths=None, na={})
    args.update(override)
    return args


class TemplateInitTest(unittest.TestCase):
    def test_both_repos_build_a_valid_file_with_all_twelve_items_and_seven_gates(self) -> None:
        for repo in rr.REPOS:
            data = rr.build_from_template(TEMPLATE, **init_args(repo))
            self.assertEqual(rr.validate(data), [])
            pc = [i for i in data["items"] if i["owner"] == "pc"]
            gates = [i for i in data["items"] if i["owner"] in rr.GATE_OWNERS]
            self.assertEqual((len(pc), len(gates)), (12, 7))
            self.assertEqual(sorted(g["owner"] for g in gates), ["hafiz"] * 5 + ["mac"] * 2)
            self.assertNotIn("<<", json.dumps(data))
            self.assertNotIn('"@', json.dumps(data))

    def test_repo_defaults_differ(self) -> None:
        agent = rr.build_from_template(TEMPLATE, **init_args("agent-os"))
        ripple = rr.build_from_template(TEMPLATE, **init_args("ripple-suite"))
        suite = lambda d: next(i for i in d["items"] if i["id"] == "5")["check"]["commands"]
        self.assertIn("npm run test:unit", suite(ripple))
        self.assertTrue(any("unittest" in c for c in suite(agent)))
        self.assertEqual(ripple["github_repo"], "Sifututor/ripple-suite")

    def test_serving_commit_adds_the_contains_check_and_without_it_the_check_is_dropped(self) -> None:
        with_sha = rr.build_from_template(TEMPLATE, **init_args("ripple-suite", serving_commit="abc1234"))
        without = rr.build_from_template(TEMPLATE, **init_args("ripple-suite"))
        types = lambda d: [c["type"] for c in next(i for i in d["items"] if i["id"] == "2")["check"]["checks"]]
        self.assertEqual(types(with_sha), ["pr_exists", "commit_in_branch"])
        self.assertEqual(types(without), ["pr_exists"])

    def test_na_items_need_a_reason_and_leave_the_denominator(self) -> None:
        data = rr.build_from_template(TEMPLATE, **init_args("agent-os", na={"4": "docs only", "7": "no staff change"}))
        self.assertEqual(rr.score(data)["pc_total"], 12 - 3)  # item 6 is na through the e2e exception
        with self.assertRaises(rr.ReadinessError):
            rr.build_from_template(TEMPLATE, **init_args("agent-os", na={"99": "x"}))

    def test_e2e_exception_must_be_one_agents_md_names(self) -> None:
        data = rr.build_from_template(TEMPLATE, **init_args("agent-os", e2e_exception="tooling unavailable: no app on the PC"))
        six = next(i for i in data["items"] if i["id"] == "6")
        self.assertEqual(six["status"], "na")
        self.assertIn("tooling unavailable", six["na_reason"])
        with self.assertRaises(rr.ReadinessError):
            rr.build_from_template(TEMPLATE, **init_args("agent-os", e2e_exception="I did not feel like it"))

    def test_e2e_commands_make_item_six_a_script(self) -> None:
        data = rr.build_from_template(TEMPLATE, **init_args("ripple-suite", e2e_exception="", e2e_commands=["npx playwright test --grep @smoke"]))
        six = next(i for i in data["items"] if i["id"] == "6")
        self.assertEqual((six["action"], six["check"]["type"]), ("script", "commands_exit_zero"))

    def test_a_protected_branch_is_refused(self) -> None:
        with self.assertRaises(rr.ReadinessError):
            rr.build_from_template(TEMPLATE, **init_args("agent-os", branch="main"))

    def test_the_template_file_itself_carries_no_cap_lines(self) -> None:
        text = rr.TEMPLATE_PATH.read_text()
        for word in ("max_usd", "max_turns", "max_minutes"):
            self.assertNotIn(word, text)


class CliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.out: list[str] = []

    def run_cli(self, *argv: str) -> int:
        return rr.main(list(argv), out=self.out.append)

    def init(self) -> Path:
        path = self.tmp / "r.json"
        code = self.run_cli("init", "--release", "Demo", "--repo", "agent-os", "--branch", "feat/1-demo", "--pr", "5",
                            "--issue", "1", "--e2e-exception", "not user-facing: demo", "--na", "4=docs only", "--out", str(path))
        self.assertEqual(code, 0, self.out)
        return path

    def test_init_refuses_to_overwrite_without_force(self) -> None:
        path = self.init()
        self.out.clear()
        self.assertEqual(self.run_cli("init", "--release", "Demo", "--repo", "agent-os", "--branch", "feat/1-demo", "--out", str(path)), 2)
        self.assertIn("exists", "\n".join(self.out))

    def test_score_says_ready_only_at_one_hundred_percent(self) -> None:
        path = self.init()
        self.out.clear()
        self.run_cli("score", str(path))
        self.assertNotIn("READY FOR YOUR GO", "\n".join(self.out))
        self.assertIn("Your gates", "\n".join(self.out))
        data = rr.load(path)
        for it in data["items"]:
            if it["owner"] == "pc" and it["status"] == "open":
                it["status"] = "green"
                it["evidence"].append({"note": "test"})
        rr.save(path, data)
        self.out.clear()
        self.run_cli("score", str(path))
        text = "\n".join(self.out)
        self.assertIn("PC readiness: 100.0%", text)
        self.assertIn("READY FOR YOUR GO", text)
        self.assertIn("G4 Production deploy go [hafiz] open", text)

    def test_mark_needs_evidence_for_green_and_next_follows_dependencies(self) -> None:
        path = self.init()
        self.out.clear()
        self.run_cli("next", str(path))
        self.assertTrue(self.out[-1].startswith("2:"), self.out)
        self.out.clear()
        self.assertEqual(self.run_cli("mark", str(path), "2", "--status", "green"), 2)
        self.assertEqual(self.run_cli("mark", str(path), "2", "--status", "green", "--pr", "5", "--note", "checked"), 0)
        self.out.clear()
        self.run_cli("next", str(path))
        self.assertTrue(self.out[-1].startswith("1:"), self.out)

    def test_mark_can_reset_failures_to_unblock_a_blocked_item(self) -> None:
        path = self.init()
        data = rr.load(path)
        data["items"][1].update(status="blocked", failures=2, blocked_reason="x", pending_fix="y")
        rr.save(path, data)
        self.assertEqual(self.run_cli("mark", str(path), data["items"][1]["id"], "--status", "open", "--note", "fixed by hand",
                                      "--reset-failures"), 0)
        again = rr.load(path)["items"][1]
        self.assertEqual((again["status"], again["failures"]), ("open", 0))
        self.assertNotIn("pending_fix", again)


if __name__ == "__main__":
    unittest.main()
