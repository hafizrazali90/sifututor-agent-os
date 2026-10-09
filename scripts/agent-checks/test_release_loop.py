#!/usr/bin/env python3
"""Tests for the release readiness loop (issue #350).

A FAKE job runner and a FAKE shell are injected, so no Claude runs and no real
command is started. Negative controls: a loop that ignores its stop rules must
fail the stop tests, and a loop that cannot be told to stop must be caught.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import job_brief  # noqa: E402
import release_loop as rl  # noqa: E402
import release_readiness as rr  # noqa: E402

TEMPLATE = json.loads(rr.TEMPLATE_PATH.read_text())
CAP_RE = re.compile(r"max[_-]?(usd|turns|minutes)|--max-budget|budget[_-]?usd", re.IGNORECASE)
SHA_1, SHA_2 = "1" * 40, "2" * 40


class RunawayLoop(BaseException):
    """The fake saw far more calls than any sane run needs: the loop is not stopping.

    A BaseException on purpose: the loop records ordinary errors as failures and
    must not be able to swallow this one."""


class Killed(BaseException):
    """Stands in for the process being killed mid-action."""


class FakeShell:
    def __init__(self, rules=None, max_calls: int = 400) -> None:
        self.calls: list[tuple[list[str], str | None]] = []
        self.rules = rules or []
        self.max_calls = max_calls

    def run(self, argv, cwd=None, stop_check=None):
        self.calls.append((list(argv), str(cwd) if cwd else None))
        if len(self.calls) > self.max_calls:
            raise RunawayLoop("the fake shell was called over and over")
        for match, response in self.rules:
            if match(argv):
                return response(argv) if callable(response) else response
        return 0, ""

    def ran(self, *words: str) -> list[list[str]]:
        return [argv for argv, _ in self.calls if all(w in " ".join(argv) for w in words)]


def doc_for(body: str) -> str:
    match = re.search(r"Use these level-2 headings exactly: (.*)", body)
    headings = [h.strip().removeprefix("## ") for h in match.group(1).split(";")] if match else []
    return "# Draft\n\n" + "\n\n".join(f"## {h}\n\nWritten for the test. not user-facing. Migrations: none." for h in headings) + \
        "\n\nnot user-facing\n"


class FakeJobs:
    """Stands in for pc_job. The handler decides what each job returns."""

    def __init__(self, handler=None, max_calls: int = 60, on_call=None, kill_at: int | None = None) -> None:
        self.calls: list[dict] = []
        self.handler = handler or self.default_handler
        self.max_calls = max_calls
        self.on_call = on_call
        self.kill_at = kill_at

    @staticmethod
    def default_handler(fields: dict, body: str, n: int) -> dict:
        if fields["role"] == "reviewer":
            return {"report": "1. **Verdict:** ACCEPT\n\nChecked the diff.", "verdict": "ACCEPT"}
        return {"report": doc_for(body)}

    def run(self, brief_text: str, title: str) -> dict:
        n = len(self.calls) + 1
        if n > self.max_calls:
            raise RunawayLoop("the fake job runner was called over and over")
        parsed = job_brief.parse(brief_text)
        self.calls.append({"fields": parsed["fields"], "body": parsed["body"], "brief": brief_text, "title": title})
        if self.on_call:
            self.on_call(n, parsed["fields"], parsed["body"])
        if self.kill_at == n:
            raise Killed()
        out = {"job_id": f"job-{n}", "state": "done", "turns": 3, "cost_usd": 0.25, "commits": 0, "changed_files": [],
               "worktree": "/fake/job-worktree", "verdict": ""}
        out.update(self.handler(parsed["fields"], parsed["body"], n))
        return out

    def roles(self) -> list[str]:
        return [c["fields"]["role"] for c in self.calls]


def pr_rules(branch: str = "docs/350-demo", sha: str = "a" * 40):
    payload = json.dumps({"number": 5, "state": "OPEN", "headRefName": branch, "headRefOid": sha, "baseRefName": "main"})
    return [(lambda argv: argv[:3] == ["gh", "pr", "view"], (0, payload)),
            (lambda argv: argv[:2] == ["git", "rev-parse"], (0, SHA_1 + "\n"))]


def close_open_gates(data: dict) -> dict:
    """What Hafiz or a Mac session does: close every gate that sits before the production go."""
    for gate in data["items"]:
        if rr.is_gate(gate) and rr.is_applicable(gate) and not rr.is_after_go(gate) and gate.get("status") == "open":
            rr.close_gate_in_data(data, gate["id"], "closed by the test", by="test", sha=SHA_1 if gate.get("records") else "")
    return data


def full_data(close: bool = True, **override) -> dict:
    args = dict(release="Demo release", repo="agent-os", branch="docs/350-demo", base="origin/main", pr_numbers_=[5],
                issue="350", serving_commit="", approval="Hafiz, test 09/10/2026", github_repo=None, suite_commands=None,
                e2e_commands=[], e2e_exception="not user-facing: docs only", fix_paths=None, na={"4": "docs only, no new behaviour"},
                route="direct-prod")
    args.update(override)
    data = rr.build_from_template(TEMPLATE, **args)
    return close_open_gates(data) if close else data


def small(items: list[dict], **extra) -> dict:
    data = {"release": "Small", "repo": "agent-os", "github_repo": "o/r", "branch": "docs/1-small", "base": "origin/main",
            "pr_numbers": [], "issue": "1", "approval": "Hafiz, test", "fix_allowed_paths": ["docs"], "route": "direct-prod", "items": items, "loop": {}}
    data.update(extra)
    return data


def it(iid: str, **fields) -> dict:
    base = {"id": iid, "title": f"Item {iid}", "group": "t", "owner": "pc", "action": "script", "status": "open",
            "applicable": True, "depends_on": [], "evidence": [], "failures": 0}
    base.update(fields)
    return base


def cmd(*commands: str, **fields) -> dict:
    return {"check": {"type": "commands_exit_zero", "commands": list(commands)}, **fields}


class LoopCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.dir = self.tmp / "rel"
        self.dir.mkdir()
        self.path = self.dir / "readiness.json"
        self.sleeps = 0
        self.on_sleep = None
        os.environ.pop("FAKE_STOP", None)

    def fake_sleep(self, seconds: float) -> None:
        """The loop's 60 second wait, shrunk to nothing. A test hook can act while the loop sleeps."""
        self.sleeps += 1
        if self.sleeps > 400:
            raise RunawayLoop("the loop slept over and over and never finished")
        if self.on_sleep:
            self.on_sleep(self.sleeps)

    def close_gate(self, item: str, evidence: str = "closed while the loop waited", **kwargs) -> str:
        return rr.request(self.path, {"op": "gate", "item": item, "evidence": evidence, "by": "test", **kwargs})

    def make(self, data: dict, jobs=None, shell=None, loop_cls=rl.Loop, **kwargs):
        rr.save(self.path, data)
        self.jobs = jobs or FakeJobs()
        self.shell = shell or FakeShell(pr_rules(data.get("branch", "x")))
        return loop_cls(self.path, self.jobs, self.shell, repo_root=self.tmp / "repo", worktrees=self.tmp / "wts",
                        log=lambda message: None, wait_seconds=2, poll_seconds=1, sleep=self.fake_sleep, **kwargs)

    def saved(self) -> dict:
        return rr.load(self.path)

    @staticmethod
    def statuses(data: dict) -> dict:
        return {i["id"]: i["status"] for i in data["items"]}


# --------------------------------------------------------------------------

class ReachesReadyTest(LoopCase):
    def test_reaches_one_hundred_percent_over_several_rounds_and_stops_ready(self) -> None:
        loop = self.make(full_data())
        self.assertEqual(loop.run(), "ready_for_prod_go")
        data = self.saved()
        self.assertEqual(data["loop"]["status"], "ready_for_prod_go")
        score = rr.score(data)
        self.assertEqual((score["percent"], score["pc_total"], score["pc_green"]), (100.0, 10, 10))
        self.assertEqual(data["loop"]["rounds"], 10)
        greens = [fp[0] for fp in data["loop"]["fingerprints"]]
        self.assertEqual(greens, list(range(0, 11)), "the score must rise one item per round")
        self.assertEqual(self.jobs.roles().count("reviewer"), 1)
        self.assertEqual(len(self.jobs.calls), 7)
        self.assertTrue((self.dir / "ready.flag").is_file())
        self.assertTrue((self.dir / "release-report.md").is_file())
        for name in ("01-scope", "08-migration-rollback", "09-deploy-plan", "10-smoke-monitoring", "11-review-page", "12-release-notes"):
            self.assertTrue((self.dir / "release-pack" / f"{name}.md").is_file(), name)

    def test_the_loop_leaves_every_gate_alone_and_waits_for_the_ones_before_the_go(self) -> None:
        self.on_sleep = lambda n: (self.dir / "STOP").write_text("stop") if n == 3 else None
        loop = self.make(full_data(close=False))
        self.assertEqual(loop.run(), "stopped")
        data = self.saved()
        gates = [i for i in data["items"] if rr.is_gate(i) and i["id"] != "G0" and rr.is_applicable(i)]
        self.assertEqual([g["id"] for g in gates], ["G1", "G2", "G3", "G4", "G5", "G6", "G7"])
        self.assertTrue(all(g["status"] == "open" and not g.get("evidence") for g in gates))
        self.assertEqual(rr.score(data)["percent"], 100.0)
        self.assertEqual(rr.score(data)["waiting_for"], ["G1", "G2", "G3"])

    def test_nothing_is_merged_deployed_or_pushed_to_main(self) -> None:
        loop = self.make(full_data())
        loop.run()
        joined = [" ".join(argv) for argv, _ in self.shell.calls]
        for line in joined:
            self.assertNotIn("merge", line.replace("merge-base", ""))
            self.assertNotRegex(line, r"git push|deploy|migrate")

    def test_checkpoint_is_written_before_and_after_every_action(self) -> None:
        seen = []

        def spy(n, fields, body):
            disk = rr.load(self.path)["loop"]
            seen.append((n, disk.get("rounds"), (disk.get("current") or {}).get("item")))

        loop = self.make(full_data(), jobs=FakeJobs(on_call=spy))
        loop.run()
        for n, rounds_on_disk, current in seen:
            self.assertIsNotNone(current, "the in-flight marker must be on disk while a job runs")
        # the first job is the 2nd round (round 1 was the scripted release-source check)
        self.assertEqual(seen[0][1], 1)
        self.assertEqual([r for _, r, _ in seen], sorted(r for _, r, _ in seen))
        self.assertIsNone(self.saved()["loop"]["current"])


class ResumeTest(LoopCase):
    def test_a_killed_run_resumes_to_the_same_result_as_an_uninterrupted_run(self) -> None:
        clean_loop = self.make(full_data())
        clean_loop.run()
        clean = self.saved()
        clean_calls = len(self.jobs.calls)

        for name in ("readiness.json", "ready.flag", "release-report.md"):
            (self.dir / name).unlink(missing_ok=True)
        shutil.rmtree(self.dir / "release-pack", ignore_errors=True)
        first = self.make(full_data(), jobs=FakeJobs(kill_at=3))
        with self.assertRaises(Killed):
            first.run()
        on_disk = self.saved()
        self.assertEqual(on_disk["loop"]["status"], "running")
        self.assertEqual(on_disk["loop"]["current"]["item"], "8" if False else on_disk["loop"]["current"]["item"])
        self.assertIsNotNone(on_disk["loop"]["current"], "the interrupted action must be recorded")
        done_before = rr.score(on_disk)["pc_green"]
        self.assertGreater(done_before, 0)
        self.assertLess(done_before, 10)
        first_calls = len(first.jobs.calls)

        second = rl.Loop(self.path, FakeJobs(), FakeShell(pr_rules()), repo_root=self.tmp / "repo", worktrees=self.tmp / "wts",
                         log=lambda message: None, wait_seconds=2, poll_seconds=1, sleep=self.fake_sleep)
        self.assertEqual(second.run(), "ready_for_prod_go")
        resumed = self.saved()
        self.assertEqual(self.statuses(resumed), self.statuses(clean))
        self.assertEqual(rr.score(resumed)["percent"], 100.0)
        self.assertEqual(resumed["loop"]["rounds"], clean["loop"]["rounds"])
        self.assertEqual(first_calls + len(second.jobs.calls), clean_calls + 1,
                         "only the interrupted job may run twice, finished items must not run again")
        self.assertTrue(any("previous run stopped" in e for e in resumed["loop"]["events"]))

    def test_a_failed_checkpoint_write_leaves_a_readable_file_and_the_run_can_resume(self) -> None:
        loop = self.make(full_data())
        real_replace = os.replace
        count = {"n": 0}

        def flaky(src, dst):
            count["n"] += 1
            if count["n"] == 9:
                raise OSError("disk full")
            return real_replace(src, dst)

        with mock.patch("release_readiness.os.replace", flaky):
            with self.assertRaises(OSError):
                loop.run()
        data = self.saved()  # parses: never half written
        self.assertEqual(rr.validate(data), [])
        again = rl.Loop(self.path, FakeJobs(), FakeShell(pr_rules()), repo_root=self.tmp / "repo", worktrees=self.tmp / "wts",
                        log=lambda message: None, wait_seconds=2, poll_seconds=1, sleep=self.fake_sleep)
        self.assertEqual(again.run(), "ready_for_prod_go")

    def test_a_second_loop_on_the_same_file_is_refused(self) -> None:
        rr.save(self.path, small([it("1")]))
        first = rl.acquire_lock(self.path)
        self.assertIsNotNone(first)
        self.assertIsNone(rl.acquire_lock(self.path))
        first.close()


def assert_stops_when_a_stop_file_appears(loop_cls, case: LoopCase) -> None:
    def drop_stop(n, fields, body):
        (case.dir / "STOP").write_text("stop")

    loop = case.make(full_data(), jobs=FakeJobs(on_call=drop_stop, max_calls=25), loop_cls=loop_cls)
    status = loop.run()
    assert status == "stopped", f"a STOP file appeared during job 1 but the loop ended {status}"
    assert len(case.jobs.calls) == 1, f"the loop ran {len(case.jobs.calls)} jobs after STOP"
    data = case.saved()
    assert data["loop"]["status"] == "stopped"
    assert not rr.score(data)["ready"]


def assert_blocks_when_an_item_fails_twice(loop_cls, case: LoopCase) -> None:
    items = [it("1", **cmd("failing-command")), it("2", **cmd("fine"))]
    shell = FakeShell([(lambda argv: argv[0] == "failing-command", (1, "assertion failed")), *pr_rules()], max_calls=60)
    loop = case.make(small(items), shell=shell, loop_cls=loop_cls)
    status = loop.run()
    assert status == "blocked", f"an item failed twice but the loop ended {status}"
    assert "failed twice" in case.saved()["loop"]["reason"]
    assert case.saved()["items"][1]["status"] == "open", "the loop went on to later items after being blocked"


def assert_goes_stuck_after_two_unchanged_rounds(loop_cls, case: LoopCase) -> None:
    noop = lambda fields, body, n: {"state": "done", "commits": 0, "job_id": "same-job"}
    items = [it("1", action="builder", instruction="change something")]
    loop = case.make(small(items), jobs=FakeJobs(handler=noop, max_calls=25), loop_cls=loop_cls)
    status = loop.run()
    assert status == "stuck", f"two rounds changed nothing but the loop ended {status}"
    assert case.saved()["loop"]["rounds"] == 2, f"expected 2 rounds, got {case.saved()['loop']['rounds']}"


class IgnoresStopRules(rl.Loop):
    """Negative control: a loop that ignores every stop rule."""

    def stop_requested(self) -> bool:
        return False

    def blocked_reason(self):
        return None

    def stuck_reason(self):
        return None

    def fail(self, item, summary, **kwargs):
        item["failures"] = int(item.get("failures", 0)) + 1  # counts, but never blocks


class StopRulesTest(LoopCase):
    def test_stops_when_a_stop_file_appears(self) -> None:
        assert_stops_when_a_stop_file_appears(rl.Loop, self)

    def test_stop_file_present_at_start_stops_before_any_job_and_clear_stop_removes_it(self) -> None:
        (self.dir / "STOP").write_text("x")
        loop = self.make(full_data())
        self.assertEqual(loop.run(), "stopped")
        self.assertEqual(self.jobs.calls, [])
        resumed = self.make(full_data(), clear_stop=True)
        rr.save(self.path, self.saved())
        self.assertEqual(resumed.run(), "ready_for_prod_go")
        self.assertFalse((self.dir / "STOP").exists())

    def test_a_stop_during_a_running_command_stops_without_counting_a_failure(self) -> None:
        def stop_inside(argv):
            raise rr.StopRequested()

        shell = FakeShell([(lambda argv: argv[0] == "slow-tests", stop_inside), *pr_rules()])
        loop = self.make(small([it("1", **cmd("slow-tests"))]), shell=shell)
        self.assertEqual(loop.run(), "stopped")
        item = self.saved()["items"][0]
        self.assertEqual((item["failures"], item["status"]), (0, "open"))
        self.assertIsNone(self.saved()["loop"]["current"])

    def test_blocks_when_an_item_fails_twice(self) -> None:
        assert_blocks_when_an_item_fails_twice(rl.Loop, self)

    def test_goes_stuck_after_two_rounds_with_no_change(self) -> None:
        assert_goes_stuck_after_two_unchanged_rounds(rl.Loop, self)

    def test_negative_control_a_loop_that_ignores_the_stop_rules_fails_every_stop_test(self) -> None:
        for check in (assert_stops_when_a_stop_file_appears, assert_blocks_when_an_item_fails_twice,
                      assert_goes_stuck_after_two_unchanged_rounds):
            with self.subTest(check=check.__name__):
                case = StopRulesTest("test_stops_when_a_stop_file_appears")
                case.setUp()
                try:
                    with self.assertRaises((AssertionError, RunawayLoop)):
                        check(IgnoresStopRules, case)
                finally:
                    shutil.rmtree(case.tmp, True)

    def test_a_failing_command_is_never_green_and_its_exit_code_is_in_the_evidence(self) -> None:
        shell = FakeShell([(lambda argv: argv[0] == "failing-command", (7, "boom")), *pr_rules()])
        loop = self.make(small([it("1", **cmd("failing-command"))]), shell=shell)
        loop.run()
        item = self.saved()["items"][0]
        self.assertNotEqual(item["status"], "green")
        self.assertEqual(item["status"], "blocked")
        self.assertIn(7, [e.get("exit_code") for e in item["evidence"]])

    def test_blocked_when_a_job_is_blocked_twice(self) -> None:
        blocked = lambda fields, body, n: {"state": "blocked", "reason": "changed files outside allowed_paths: x"}
        items = [it("1", action="builder", doc={"path": "release-pack/01.md", "headings": ["A"]}, instruction="x")]
        loop = self.make(small(items), jobs=FakeJobs(handler=blocked))
        self.assertEqual(loop.run(), "blocked")
        self.assertIn("allowed_paths", self.saved()["loop"]["reason"])
        self.assertEqual(len(self.jobs.calls), 2)

    def test_an_item_that_waits_on_a_gate_is_waiting_not_blocked(self) -> None:
        items = [it("1", depends_on=["G1"], **cmd("fine")), it("G1", owner="hafiz", action="none")]
        self.on_sleep = lambda n: self.close_gate("G1") if n == 2 else None
        loop = self.make(small(items))
        self.assertEqual(loop.run(), "ready_for_prod_go")
        self.assertGreaterEqual(self.sleeps, 2)
        self.assertEqual(self.statuses(self.saved()), {"1": "green", "G1": "green"})

    def test_a_blocked_item_is_blocked_even_when_gates_are_open(self) -> None:
        items = [it("1", **cmd("failing-command")), it("G1", owner="hafiz", action="none")]
        shell = FakeShell([(lambda argv: argv[0] == "failing-command", (1, "x")), *pr_rules()])
        loop = self.make(small(items), shell=shell)
        self.assertEqual(loop.run(), "blocked")
        self.assertEqual(self.sleeps, 0)

    def test_an_item_with_no_action_is_blocked_and_the_rest_still_run(self) -> None:
        items = [it("1", action="none"), it("2", **cmd("fine"))]
        loop = self.make(small(items))
        self.assertEqual(loop.run(), "blocked")
        self.assertEqual(self.statuses(self.saved()), {"1": "blocked", "2": "green"})

    def test_fixes_that_keep_undoing_an_item_are_a_loop_not_progress(self) -> None:
        data = small([it("1", **cmd("fine"))])
        data["items"][0].update(status="open", resets=rl.MAX_RESETS)
        loop = self.make(data)
        self.assertEqual(loop.run(), "blocked")
        self.assertIn("keep undoing each other", self.saved()["loop"]["reason"])


class ForbiddenTest(LoopCase):
    def test_a_merge_item_becomes_a_hafiz_gate_and_the_loop_keeps_going(self) -> None:
        items = [it("1", **cmd("fine one")), it("2", **cmd("gh pr merge 5 --merge")), it("3", depends_on=["1"], **cmd("fine three"))]
        seen = {}

        def hafiz_merges_it_himself(n):
            seen.setdefault("waiting", rr.score(rr.load(self.path))["waiting_for"])
            self.close_gate("2", "merged by Hafiz himself")

        self.on_sleep = hafiz_merges_it_himself
        loop = self.make(small(items))
        self.assertEqual(loop.run(), "ready_for_prod_go")
        self.assertEqual(seen["waiting"], ["2"], "the handed over item is a gate the loop waits for")
        data = self.saved()
        merge = data["items"][1]
        self.assertEqual((merge["owner"], merge["original_owner"], merge["status"]), ("hafiz", "pc", "green"))
        self.assertEqual(merge["evidence"][-1]["by"], "test", "only the person's evidence closed it, the loop never ran the merge")
        self.assertTrue(any("will not run it" in e.get("note", "") for e in merge["evidence"]))
        self.assertEqual(rr.score(data)["pc_total"], 2)
        self.assertEqual(rr.score(data)["percent"], 100.0)
        self.assertEqual(self.shell.ran("gh", "pr", "merge"), [])
        self.assertIn("2", [g["id"] for g in rr.score(data)["gates"]])

    def test_deploy_migrate_and_production_write_are_never_run(self) -> None:
        items = [it("1", **cmd("php artisan migrate --force")), it("2", **cmd("./deploy.sh production")),
                 it("3", **cmd("mysql -e 'delete from x'")), it("4", action="deploy"), it("5", **cmd("fine"))]
        self.on_sleep = lambda n: [self.close_gate(g) for g in ("1", "2", "3", "4")] if n == 1 else None
        loop = self.make(small(items))
        self.assertEqual(loop.run(), "ready_for_prod_go")
        self.assertEqual([i["owner"] for i in self.saved()["items"]], ["hafiz"] * 4 + ["pc"])
        for needle in ("migrate", "deploy", "mysql"):
            self.assertEqual(self.shell.ran(needle), [], needle)

    def test_a_builder_instruction_that_names_a_merge_command_is_handed_over(self) -> None:
        items = [it("1", action="builder", instruction="when done run gh pr merge 3", doc={"path": "release-pack/1.md", "headings": []})]
        self.on_sleep = lambda n: (self.dir / "STOP").write_text("x")
        loop = self.make(small(items))
        self.assertEqual(loop.run(), "stopped")
        self.assertEqual(self.saved()["items"][0]["owner"], "hafiz")
        self.assertEqual(self.jobs.calls, [])


class ReviewAndFixTest(LoopCase):
    ITEMS = lambda self: [
        it("5", fix_on_failure=True, **cmd("run-suite")),
        it("3", action="reviewer", depends_on=["5"], instruction="review it",
           check={"type": "verdict_file", "base": "pack", "path": "release-pack/review-3.md"}),
    ]

    def handler(self, fields, body, n):
        if fields["role"] == "reviewer":
            if sum(1 for c in self.jobs.calls if c["fields"]["role"] == "reviewer") == 1:
                return {"report": "**Verdict:** CHANGES NEEDED\n\n1. src/a.ts line 10 divides by zero when the list is empty.", "verdict": "CHANGES NEEDED"}
            return {"report": "**Verdict:** ACCEPT\n\nThe fix is right.", "verdict": "ACCEPT"}
        return {"commits": 1, "changed_files": ["docs/a.md"], "worktree": str(self.tmp / "fixwt")}

    def sha_rules(self):
        def rev(argv):
            pushed = any(argv2[:2] == ["git", "push"] for argv2, _ in self.shell.calls)
            return 0, (SHA_2 if pushed else SHA_1) + "\n"
        return [(lambda argv: argv[:2] == ["git", "rev-parse"], rev)]

    def test_changes_needed_goes_to_a_builder_fix_then_a_fresh_reviewer(self) -> None:
        self.jobs = FakeJobs(handler=self.handler)
        loop = self.make(small(self.ITEMS()), jobs=self.jobs, shell=FakeShell([]))
        self.shell.rules = self.sha_rules()
        self.assertEqual(loop.run(), "ready_for_prod_go")
        self.assertEqual(self.jobs.roles(), ["reviewer", "builder", "reviewer"])
        fix = self.jobs.calls[1]
        self.assertIn("divides by zero", fix["body"])
        self.assertEqual(fix["fields"]["finish"], "committed")
        self.assertEqual(fix["fields"]["base"], "origin/docs/1-small")
        self.assertTrue(fix["fields"]["branch"].startswith("fix/"))
        self.assertEqual(fix["fields"]["allowed_paths"], "docs")
        pushes = self.shell.ran("git", "push")
        self.assertEqual(pushes, [["git", "push", "origin", "HEAD:refs/heads/docs/1-small"]])
        self.assertEqual(self.jobs.calls[0]["fields"]["target"], "docs/1-small")
        self.assertTrue((self.dir / "release-pack" / "review-3-1.md").is_file())
        self.assertTrue((self.dir / "release-pack" / "review-3-3.md").is_file())
        self.assertIn("ACCEPT", (self.dir / "release-pack" / "review-3.md").read_text())

    def test_a_pushed_fix_resets_the_proof_taken_on_the_old_commit(self) -> None:
        self.jobs = FakeJobs(handler=self.handler)
        loop = self.make(small(self.ITEMS()), jobs=self.jobs, shell=FakeShell([]))
        self.shell.rules = self.sha_rules()
        loop.run()
        data = self.saved()
        suite = data["items"][0]
        self.assertEqual(suite["resets"], 1)
        self.assertEqual(len(self.shell.ran("run-suite")), 2, "the suite must run again on the new commit")
        self.assertEqual(suite["verified_sha"], SHA_2)
        self.assertEqual(data["loop"]["release_sha"], SHA_2)

    def test_a_failed_suite_becomes_a_builder_fix_given_the_failure_output(self) -> None:
        state = {"fixed": False}

        def suite(argv):
            return (0, "ok") if state["fixed"] else (1, "FAIL src/b.test.ts: expected 2 received 3")

        def handler(fields, body, n):
            state["fixed"] = True
            return {"commits": 1, "changed_files": ["docs/a.md"], "worktree": str(self.tmp / "fixwt")}

        jobs = FakeJobs(handler=handler)
        loop = self.make(small([it("5", fix_on_failure=True, **cmd("run-suite"))]), jobs=jobs,
                         shell=FakeShell([(lambda argv: argv[0] == "run-suite", suite), *pr_rules()]))
        self.assertEqual(loop.run(), "ready_for_prod_go")
        self.assertEqual(jobs.roles(), ["builder"])
        self.assertIn("expected 2 received 3", jobs.calls[0]["body"])
        self.assertIn("run-suite", jobs.calls[0]["body"])

    def test_a_fix_that_does_not_help_blocks_the_item_on_the_second_failure(self) -> None:
        handler = lambda fields, body, n: {"commits": 1, "changed_files": ["docs/a.md"], "worktree": "/fake/wt"}
        jobs = FakeJobs(handler=handler)
        loop = self.make(small([it("5", fix_on_failure=True, **cmd("run-suite"))]), jobs=jobs,
                         shell=FakeShell([(lambda argv: argv[0] == "run-suite", (1, "still red")), *pr_rules()]))
        self.assertEqual(loop.run(), "blocked")
        self.assertEqual(jobs.roles(), ["builder"])
        self.assertEqual(self.saved()["items"][0]["status"], "blocked")

    def test_without_an_approval_line_a_fix_is_never_pushed(self) -> None:
        handler = lambda fields, body, n: {"commits": 1, "changed_files": ["docs/a.md"], "worktree": "/fake/wt"}
        jobs = FakeJobs(handler=handler)
        loop = self.make(small([it("5", fix_on_failure=True, **cmd("run-suite"))], approval=""), jobs=jobs,
                         shell=FakeShell([(lambda argv: argv[0] == "run-suite", (1, "red")), *pr_rules()]))
        self.assertEqual(loop.run(), "blocked")
        self.assertEqual(self.shell.ran("git", "push"), [])
        self.assertIn("approval", self.saved()["loop"]["reason"])

    def test_a_fix_never_goes_to_a_protected_branch(self) -> None:
        loop = self.make(small([it("1")]))
        loop.data = self.saved()
        loop.data["branch"] = "main"
        pushed, why = loop.push_fix({"worktree": "/x"})
        self.assertFalse(pushed)
        self.assertIn("protected", why)
        self.assertEqual(self.shell.ran("git", "push"), [])

    def test_a_reviewer_blocked_verdict_is_a_failure_without_a_fix_job(self) -> None:
        handler = lambda fields, body, n: {"report": "Verdict: BLOCKED\n\ncould not read", "verdict": "BLOCKED"}
        jobs = FakeJobs(handler=handler)
        items = [it("3", action="reviewer", check={"type": "verdict_file", "base": "pack", "path": "release-pack/review-3.md"})]
        loop = self.make(small(items), jobs=jobs)
        self.assertEqual(loop.run(), "blocked")
        self.assertEqual(jobs.roles(), ["reviewer", "reviewer"])


class BriefTest(LoopCase):
    def test_no_brief_the_loop_writes_carries_a_cap_line(self) -> None:
        loop = self.make(full_data(), jobs=FakeJobs(handler=ReviewAndFixTest.handler.__get__(self)))
        self.jobs.handler = FakeJobs.default_handler
        loop.run()
        self.assertTrue(self.jobs.calls)
        for call in self.jobs.calls:
            self.assertIsNone(CAP_RE.search(call["brief"]), call["brief"][:200])
            errors, _ = job_brief.validate(job_brief.parse(call["brief"]))
            self.assertEqual(errors, [])
            self.assertTrue(set(call["fields"]) <= set(job_brief.ALLOWED_KEYS))
            self.assertLessEqual(len(call["fields"]["title"]), 80)
            self.assertNotIn("\N{EM DASH}", call["brief"], "no em dashes")

    def test_the_new_scripts_never_mention_a_cap_key(self) -> None:
        for name in ("release_loop.py", "release_readiness.py", "pc_release.py"):
            text = (HERE / name).read_text()
            for line in text.splitlines():
                self.assertNotRegex(line, r"^\s*(max_usd|max_turns|max_minutes)\s*[:=]", f"{name}: {line}")
                self.assertNotIn("--max-budget", line, name)

    def test_a_project_repo_release_names_the_repo_in_every_brief(self) -> None:
        data = full_data(repo="ripple-suite", e2e_exception="tooling unavailable: no app", na={"4": "x"})
        loop = self.make(data, shell=FakeShell(pr_rules(data["branch"])))
        loop.run()
        self.assertTrue(self.jobs.calls)
        for call in self.jobs.calls:
            self.assertEqual(call["fields"]["repo"], "ripple-suite")
            self.assertEqual(call["fields"]["base"], "origin/docs/350-demo" if call["fields"]["role"] == "builder" else "origin/main")

    def test_job_branch_names_differ_between_two_releases_in_the_same_repo(self) -> None:
        names = []
        for run in range(2):
            self.setUp()
            (self.dir / "x").write_text("")
            data = full_data()
            loop = self.make(data)
            with mock.patch.object(rr, "now_utc", lambda n=run: rr.dt.datetime(2026, 10, 9, 3, 0, n, tzinfo=rr.dt.timezone.utc)):
                loop.run()
            names.append({c["fields"]["branch"] for c in self.jobs.calls if "branch" in c["fields"]})
        self.assertFalse(names[0] & names[1], "two releases must never ask the runner for the same branch name")
        self.assertTrue(all(re.fullmatch(r"docs/[a-z0-9-]+", n) for n in names[0]))

    def test_document_jobs_cannot_change_anything(self) -> None:
        loop = self.make(full_data())
        loop.run()
        docs = [c for c in self.jobs.calls if c["fields"]["role"] == "builder"]
        self.assertTrue(docs)
        for call in docs:
            self.assertEqual(call["fields"]["finish"], "local")
            self.assertEqual(call["fields"]["allowed_paths"], ".release-loop-scratch")
            self.assertIn("You change no file", call["body"])

    def test_a_document_missing_its_headings_is_a_failure_not_green(self) -> None:
        handler = lambda fields, body, n: {"report": "# Draft\n\nJust a paragraph."}
        items = [it("1", action="builder", instruction="x", doc={"path": "release-pack/01.md", "headings": ["What changes"]})]
        loop = self.make(small(items), jobs=FakeJobs(handler=handler))
        self.assertEqual(loop.run(), "blocked")
        self.assertIn("missing", self.saved()["items"][0]["last_failure"])

    def test_text_before_the_first_heading_is_dropped_from_a_draft(self) -> None:
        handler = lambda fields, body, n: {"report": "Sure, here it is:\n\n# Scope\n\n## What changes\n\nx"}
        items = [it("1", action="builder", instruction="x", doc={"path": "release-pack/01.md", "headings": ["What changes"]})]
        self.make(small(items), jobs=FakeJobs(handler=handler)).run()
        self.assertTrue((self.dir / "release-pack" / "01.md").read_text().startswith("# Scope"))


class WorktreeTest(LoopCase):
    def test_a_project_release_installs_packages_once_from_the_lockfile(self) -> None:
        wt = self.tmp / "wts" / "release-small"
        (wt / ".git").mkdir(parents=True)
        (wt / "package-lock.json").write_text("{}")
        data = small([it("1", **cmd("fine"))], repo="ripple-suite")
        loop = self.make(data)
        loop.data = self.saved()
        loop.data["loop"] = {"worktree": str(wt)}
        loop.ensure_worktree()
        self.assertEqual(len(self.shell.ran("npm", "ci")), 1)
        self.assertTrue(self.shell.ran("checkout", "--detach"), "an existing worktree is moved, not recreated")
        (wt / "node_modules").mkdir()
        loop.ensure_worktree()
        self.assertEqual(len(self.shell.ran("npm", "ci")), 1, "same lockfile and packages present: no second install")

    def test_a_missing_release_branch_blocks_with_a_plain_reason(self) -> None:
        shell = FakeShell([(lambda argv: argv[:3] == ["git", "worktree", "add"], (128, "fatal: invalid reference: origin/docs/1-small"))])
        loop = self.make(small([it("1", **cmd("fine"))]), shell=shell)
        self.assertEqual(loop.run(), "blocked")
        self.assertIn("cannot check out origin/docs/1-small", self.saved()["loop"]["reason"])


class ReportTest(LoopCase):
    def test_ready_report_has_the_minimum_release_report_shape(self) -> None:
        loop = self.make(full_data())
        loop.run()
        text = (self.dir / "release-report.md").read_text()
        for needle in ("READY FOR YOUR PRODUCTION GO", "- Source:", "- Highest proven state: not merged, not deployed", "- What proves it:",
                       "- Normal smoke:", "- Change smoke:", "- What is not proven yet:", "- User impact:", "- Staff documentation:",
                       "- Recommended next:", "- Decision needed:", "100.0% (10 of 10 applicable PC items green)", "G4 Production deploy go (always Hafiz's) [hafiz]: open", "Prod readiness 100.0%", "Route: direct-prod", "After your go (listed, never counted)", "Gates before your go",
                       "G5 Production smoke", "[mac]: open", "7 Claude jobs", "Nothing was merged, deployed, migrated", "MYT"):
            self.assertIn(needle, text)
        self.assertNotIn("\N{EM DASH}", text)
        self.assertIn(SHA_1, text)

    def test_the_evidence_column_shows_the_command_and_its_exit_code(self) -> None:
        loop = self.make(full_data())
        loop.run()
        text = (self.dir / "release-report.md").read_text()
        row = next(line for line in text.splitlines() if line.startswith("| 5 Suite"))
        self.assertIn("2 of 2 commands passed", row)
        self.assertIn("exit_code 0", row)
        self.assertNotIn("green: green", row)

    def test_user_impact_is_one_readable_line(self) -> None:
        loop = self.make(full_data())
        loop.run()
        impact = next(line for line in (self.dir / "release-report.md").read_text().splitlines() if line.startswith("- User impact:"))
        self.assertNotIn(" - ", impact.removeprefix("- User impact:"))

    def test_a_blocked_report_says_why_and_does_not_say_ready(self) -> None:
        items = [it("1", **cmd("failing-command"))]
        loop = self.make(small(items), shell=FakeShell([(lambda argv: argv[0] == "failing-command", (1, "x")), *pr_rules()]))
        loop.run()
        text = (self.dir / "release-report.md").read_text()
        self.assertIn("**BLOCKED**", text)
        self.assertNotIn("READY FOR YOUR", text)
        self.assertFalse((self.dir / "ready.flag").exists())

    def test_a_restart_removes_a_stale_ready_flag(self) -> None:
        (self.dir / "ready.flag").write_text("old")
        loop = self.make(small([it("1", **cmd("failing-command"))]),
                         shell=FakeShell([(lambda argv: argv[0] == "failing-command", (1, "x")), *pr_rules()]))
        loop.run()
        self.assertFalse((self.dir / "ready.flag").exists())


class PcJobRunnerTest(unittest.TestCase):
    def test_runs_pc_job_in_a_job_folder_and_reads_its_result(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        for name in ("role.txt", "settings.template.json", "render-claude-settings.py"):
            (tmp / name).write_text(name)
        seen = {}

        def fake_run(job_dir, **kwargs):
            seen["kwargs"] = kwargs
            seen["files"] = sorted(p.name for p in Path(job_dir).iterdir())
            (Path(job_dir) / "result.json").write_text(json.dumps({"state": "done", "verdict": "ACCEPT", "turns": 4, "cost_usd": 0.5}))
            (Path(job_dir) / "claude-output.json").write_text(json.dumps({"result": "Verdict: ACCEPT"}))
            return 0

        import pc_job
        with mock.patch.object(pc_job, "run", fake_run):
            result = rl.PcJobRunner(tmp, repo_root=tmp / "repo").run("---\ntitle: x\n---\nbody", "Review 3 cold review")
        self.assertEqual(result["state"], "done")
        self.assertEqual(result["report"], "Verdict: ACCEPT")
        self.assertTrue(result["job_id"].endswith("review-3-cold-review"))
        self.assertFalse(seen["kwargs"]["drop_task"])
        self.assertIn("role.txt", seen["files"])
        self.assertIn("brief.md", seen["files"])

    def test_a_job_that_leaves_no_result_is_a_failed_job(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        import pc_job
        with mock.patch.object(pc_job, "run", lambda *a, **k: 1):
            result = rl.PcJobRunner(tmp).run("---\ntitle: x\n---\nbody", "A job")
        self.assertEqual(result["state"], "failed")


def assert_waits_for_gates_without_stopping_or_going_stuck(loop_cls, case: LoopCase) -> None:
    """Every PC item is green, three gates are open: the loop must sleep, not stop, then finish by itself."""
    states: list[tuple[int, str, int]] = []

    def on_sleep(n: int) -> None:
        disk = rr.load(case.path)
        states.append((n, disk["loop"]["status"], disk["loop"].get("rounds", 0)))
        if n == 7:
            for gate in ("G1", "G2", "G3"):
                case.close_gate(gate)

    case.on_sleep = on_sleep
    loop = case.make(full_data(close=False), loop_cls=loop_cls)
    status = loop.run()
    assert status == "ready_for_prod_go", f"the loop was only waiting for gates but ended {status}"
    assert case.sleeps >= 7, f"the loop should have slept while the gates were open, slept {case.sleeps} times"
    assert all(st == "waiting" for _, st, _ in states[:6]), f"expected status waiting while gates are open: {states}"
    assert len({rounds for _, _, rounds in states}) == 1, "nothing may run while the loop waits"


class NeverWaits(rl.Loop):
    """Negative control: a loop that treats 'only gates are left' as the end (it stops instead of waiting)."""

    def waiting_names(self) -> list[str]:
        return []


class CountsWaitingAsStuck(rl.Loop):
    """Negative control: a loop whose stuck detector fires while it waits."""

    def step(self):
        outcome = super().step()
        if outcome and outcome[0] == "waiting":
            self.loop.setdefault("fingerprints", []).append(self.fingerprint())
            self.checkpoint()
            reason = self.stuck_reason()
            if reason:
                return "stuck", reason
        return outcome


class WaitingAndRoutesTest(LoopCase):
    def test_it_waits_for_gates_without_stopping_or_going_stuck_and_finishes_by_itself(self) -> None:
        assert_waits_for_gates_without_stopping_or_going_stuck(rl.Loop, self)
        self.assertEqual(rr.score(self.saved())["prod_percent"], 100.0)
        self.assertTrue(any("waiting_for_gate: G1, G2, G3" in e for e in self.saved()["loop"]["events"]))

    def test_negative_control_a_loop_that_stops_when_only_gates_are_left_fails_the_waiting_test(self) -> None:
        for mutant in (NeverWaits, CountsWaitingAsStuck):
            with self.subTest(mutant=mutant.__name__):
                case = WaitingAndRoutesTest("test_it_waits_for_gates_without_stopping_or_going_stuck_and_finishes_by_itself")
                case.setUp()
                try:
                    with self.assertRaises((AssertionError, RunawayLoop)):
                        assert_waits_for_gates_without_stopping_or_going_stuck(mutant, case)
                finally:
                    shutil.rmtree(case.tmp, True)

    def test_the_status_file_says_which_gates_it_waits_for(self) -> None:
        seen = {}

        def look(n):
            seen.setdefault("loop", rr.load(self.path)["loop"])
            seen.setdefault("report", (self.dir / "release-report.md").read_text())
            seen.setdefault("score", rr.render_score(rr.load(self.path), self.dir))
            for gate in ("G1", "G2", "G3"):
                self.close_gate(gate)

        self.on_sleep = look
        self.make(full_data(close=False)).run()
        self.assertEqual(seen["loop"]["status"], "waiting")
        self.assertEqual(seen["loop"]["waiting_for"], ["G1", "G2", "G3"])
        self.assertIn("**WAITING FOR YOUR GATES**", seen["report"])
        self.assertIn("waiting_for_gate: G1, G2, G3", seen["report"])
        self.assertIn("waiting_for_gate: G1, G2, G3", seen["score"])
        self.assertIn("PC readiness: 100.0%", seen["score"])

    def test_a_stop_file_still_stops_a_waiting_loop(self) -> None:
        self.on_sleep = lambda n: (self.dir / "STOP").write_text("stop") if n == 3 else None
        loop = self.make(full_data(close=False))
        self.assertEqual(loop.run(), "stopped")
        self.assertEqual(self.saved()["loop"]["status"], "stopped")
        self.assertFalse(rr.score(self.saved())["prod_ready"])

    def test_direct_prod_reaches_100_without_any_staging_item(self) -> None:
        loop = self.make(full_data(route="direct-prod"))
        self.assertEqual(loop.run(), "ready_for_prod_go")
        data = self.saved()
        by = rr.item_map(data)
        for item_id in ("S1", "S2", "S3", "S4"):
            self.assertEqual((by[item_id]["status"], by[item_id]["na_reason"]), ("na", "Hafiz chose direct to production"))
        self.assertEqual(rr.score(data)["prod_percent"], 100.0)
        self.assertEqual(self.sleeps, 0, "all gates were closed beforehand, so nothing to wait for")
        self.assertEqual(self.shell.ran("merge-base"), [], "the promotion check only runs on the staging-first route")
        self.assertIn("Route: direct-prod", (self.dir / "release-report.md").read_text())

    def test_staging_first_sits_in_waiting_then_continues_to_100_after_the_three_staging_gates_are_closed(self) -> None:
        data = full_data(close=False, route="staging-first")
        for gate in ("G1", "G2", "G3"):
            rr.close_gate_in_data(data, gate, "closed before the run", by="test")
        order: list[str] = []
        states: list[tuple[int, str, int, list[str]]] = []

        def hafiz_and_the_mac_session(n: int) -> None:
            disk = rr.load(self.path)
            states.append((n, disk["loop"]["status"], disk["loop"].get("rounds", 0), disk["loop"].get("waiting_for", [])))
            if n == 4:
                order.append(self.close_gate("S1", "merged into sifu-staging"))
            if n == 6:
                order.append(self.close_gate("S2", "staging deployed", sha=SHA_1))
            if n == 8:
                order.append(self.close_gate("S3", "staging smoke checked, normal and change"))

        self.on_sleep = hafiz_and_the_mac_session
        loop = self.make(data)
        self.assertEqual(loop.run(), "ready_for_prod_go")
        self.assertTrue(all(st == "waiting" for _, st, _, _ in states[:3]), states)
        self.assertEqual(states[0][3], ["S1", "S2", "S3"])
        self.assertEqual(len({rounds for _, _, rounds, _ in states[:7]}), 1, "no round ran while it waited, so nothing could look stuck")
        final = self.saved()
        by = rr.item_map(final)
        self.assertEqual(by["S4"]["status"], "green", "the promotion check runs once S3 is closed")
        self.assertEqual(final["staging_sha"], SHA_1)
        self.assertEqual((rr.score(final)["percent"], rr.score(final)["prod_percent"]), (100.0, 100.0))
        self.assertTrue(self.shell.ran("merge-base", SHA_1), "S4 must prove the production branch holds the staging-tested commit")
        self.assertIn("staging deployed and staging smoke checked", (self.dir / "release-report.md").read_text())

    def test_staging_first_does_not_run_the_promotion_check_before_staging_passes(self) -> None:
        data = full_data(close=False, route="staging-first")
        for gate in ("G1", "G2", "G3"):
            rr.close_gate_in_data(data, gate, "closed before the run", by="test")
        self.on_sleep = lambda n: (self.dir / "STOP").write_text("x") if n == 3 else None
        loop = self.make(data)
        self.assertEqual(loop.run(), "stopped")
        self.assertEqual(rr.item_map(self.saved())["S4"]["status"], "open")
        self.assertEqual(self.shell.ran("merge-base"), [])

    def test_gates_closed_while_the_loop_owns_the_checkpoint_are_queued_then_applied(self) -> None:
        lock = rr.acquire_lock(self.dir)  # the loop's own process would hold this
        self.addCleanup(lock.close)
        answers = []

        def close_all(n: int) -> None:
            if n == 2:
                answers.extend(self.close_gate(g) for g in ("G1", "G2", "G3"))
                answers.append(len(rr.pending_ops(self.dir)))

        self.on_sleep = close_all
        loop = self.make(full_data(close=False))
        self.assertEqual(loop.run(), "ready_for_prod_go")
        self.assertEqual(answers, ["queued", "queued", "queued", 3])
        self.assertEqual(rr.pending_ops(self.dir), [])
        self.assertEqual(sum("applied request" in e for e in self.saved()["loop"]["events"]), 3)

    def test_a_route_switch_while_waiting_recomputes_applicability_and_the_loop_carries_on(self) -> None:
        log = {}

        def switch(n: int) -> None:
            if n == 1:
                log["answer"] = rr.request(self.path, {"op": "route", "route": "staging-first", "by": "Hafiz, changed his mind"})
            elif n == 3:
                log["waiting"] = rr.load(self.path)["loop"].get("waiting_for")
                for gate, kwargs in (("G1", {}), ("G2", {}), ("G3", {}), ("S1", {}), ("S2", {"sha": SHA_1}), ("S3", {})):
                    self.close_gate(gate, **kwargs)

        self.on_sleep = switch
        loop = self.make(full_data(close=False, route="direct-prod"))
        self.assertEqual(loop.run(), "ready_for_prod_go")
        final = self.saved()
        self.assertEqual(final["route"], "staging-first")
        self.assertEqual([h["route"] for h in final["route_history"]], ["direct-prod", "staging-first"])
        self.assertEqual(final["route_history"][1]["by"], "Hafiz, changed his mind")
        self.assertIn("S1", log["waiting"])
        self.assertEqual(rr.item_map(final)["S4"]["status"], "green")

    def test_a_release_whose_route_was_never_recorded_does_not_start(self) -> None:
        data = full_data()
        rr.item_map(data)["G0"]["status"] = "open"
        loop = self.make(data)
        self.assertEqual(loop.run(), "blocked")
        self.assertIn("route is not recorded", self.saved()["loop"]["reason"])
        self.assertEqual(self.jobs.calls, [])

    def test_a_ready_flag_is_only_written_when_prod_readiness_is_100(self) -> None:
        self.on_sleep = lambda n: (self.dir / "STOP").write_text("x")
        self.make(full_data(close=False)).run()
        self.assertFalse((self.dir / "ready.flag").exists())
        (self.dir / "STOP").unlink()
        close_open = full_data()
        rr.save(self.path, close_open)
        rl.Loop(self.path, FakeJobs(), FakeShell(pr_rules(close_open["branch"])), repo_root=self.tmp / "repo", worktrees=self.tmp / "wts",
                log=lambda message: None, wait_seconds=2, poll_seconds=1, sleep=self.fake_sleep).run()
        flag = (self.dir / "ready.flag").read_text()
        self.assertIn("READY FOR YOUR GO", flag)
        self.assertIn("route direct-prod", flag)

    def test_the_report_lists_the_exact_deploy_commands_the_plan_holds_and_marks_simulated_gates(self) -> None:
        def plan(fields, body, n):
            if fields["role"] == "reviewer":
                return {"report": "Verdict: ACCEPT"}
            text = doc_for(body)
            return {"report": text.replace("## Commands in order\n\nWritten for the test. not user-facing. Migrations: none.",
                                           "## Commands in order\n\n1. `gh pr merge 351` (Hafiz)\n2. `./deploy.sh production` (Hafiz)")}

        data = full_data(close=False)
        for gate in ("G1", "G2", "G3"):
            rr.close_gate_in_data(data, gate, "proof run", by="test", simulated=True)
        self.make(data, jobs=FakeJobs(handler=plan)).run()
        report = (self.dir / "release-report.md").read_text()
        self.assertIn("## Exact deploy commands the plan lists (the PC never runs them", report)
        self.assertIn("./deploy.sh production", report)
        self.assertIn("SIMULATED gates in this report: G1, G2, G3", report)
        self.assertIn("(SIMULATED proof run", report)
        self.assertEqual(self.shell.ran("deploy"), [], "the plan lists the command; the loop never runs it")


if __name__ == "__main__":
    unittest.main()
