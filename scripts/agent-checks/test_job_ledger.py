#!/usr/bin/env python3
"""Tests for the job ledger: which machine, account and AI ran each job.

Agreed with Hafiz on 17/10/2026: every job shows its machine, account and AI on
the Session Map page. The PC runner writes its entry itself; a Mac launch on a
second account records one with job_ledger.py.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
CHECKS = ROOT / "scripts" / "agent-checks"


def load(name: str, filename: str):
    sys.path.insert(0, str(CHECKS))
    spec = importlib.util.spec_from_file_location(name, CHECKS / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class JobLedgerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ledger = load("job_ledger", "job_ledger.py")

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        patcher = mock.patch.dict(os.environ, {"AGENT_OS_JOBS_DIR": self.tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_a_job_becomes_a_page_row(self) -> None:
        self.assertTrue(self.ledger.record("CRM build job 4", "Mac", "sthafizrazali", "Claude", "running", now=1.0))
        row = self.ledger.rows()[0]
        self.assertEqual(row, {"n": "CRM build job 4", "where": "Mac", "acct": "sthafizrazali", "ai": "Claude", "s": "discussing"})

    def test_the_last_state_of_a_job_wins_and_order_is_kept(self) -> None:
        self.ledger.record("job a", "Mac", "x", "Claude", "running", now=1.0)
        self.ledger.record("job b", "PC", "work", "Claude", "running", now=2.0)
        self.ledger.record("job a", "Mac", "x", "Claude", "done", now=3.0)
        rows = self.ledger.rows()
        self.assertEqual([r["n"] for r in rows], ["job a", "job b"])
        self.assertEqual([r["s"] for r in rows], ["done", "discussing"])

    def test_a_failed_job_is_shown_as_done_and_named_failed(self) -> None:
        self.ledger.record("job a", "Mac", "x", "Codex", "failed", now=1.0)
        row = self.ledger.rows()[0]
        self.assertEqual(row["n"], "job a (failed)")
        self.assertEqual(row["s"], "done")

    def test_a_queued_job_is_not_started(self) -> None:
        self.ledger.record("job a", "Mac", "x", "Claude", "queued", now=1.0)
        self.assertEqual(self.ledger.rows()[0]["s"], "todo")

    def test_blank_fields_and_unknown_states_are_refused(self) -> None:
        self.assertFalse(self.ledger.record("", "Mac", "x", "Claude", "running"))
        self.assertFalse(self.ledger.record("a", "", "x", "Claude", "running"))
        self.assertFalse(self.ledger.record("a", "Mac", " ", "Claude", "running"))
        self.assertFalse(self.ledger.record("a", "Mac", "x", "", "running"))
        self.assertFalse(self.ledger.record("a", "Mac", "x", "Claude", "banana"))
        self.assertEqual(self.ledger.rows(), [])

    def test_broken_lines_are_ignored(self) -> None:
        self.ledger.record("job a", "Mac", "x", "Claude", "running", now=1.0)
        with (Path(self.tmp.name) / "jobs.jsonl").open("a", encoding="utf-8") as handle:
            handle.write("not json\n[1,2]\n")
        self.assertEqual(len(self.ledger.rows()), 1)

    def test_only_recent_jobs_when_asked(self) -> None:
        self.ledger.record("old", "Mac", "x", "Claude", "done", now=1_000.0)
        self.ledger.record("new", "Mac", "x", "Claude", "done", now=1_000.0 + 30 * 3600)
        rows = self.ledger.rows(since_hours=24, now=1_000.0 + 31 * 3600)
        self.assertEqual([r["n"] for r in rows], ["new"])

    def test_rows_pass_the_session_map_check(self) -> None:
        check = load("session_map_page_check", "session_map_page_check.py")
        self.ledger.record("job a", "PC", "work", "Claude", "running", now=1.0)
        data = {
            "title": "t", "asOf": "17/10 20:00 MYT", "defaultBy": "Mac · a · Claude",
            "groups": [{"name": "g", "steps": [{"n": "s", "s": "discussing", "here": True, "d": "d"}]}],
            "jobs": self.ledger.rows(),
        }
        self.assertEqual(check.check_data(data), [])


class PcRunnerRecordsItsJobTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ledger = load("job_ledger", "job_ledger.py")
        cls.pc_job = load("pc_job", "pc_job.py")
        cls.sample = load("test_pc_job", "test_pc_job.py")

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        patcher = mock.patch.dict(os.environ, {"AGENT_OS_JOBS_DIR": str(Path(self.tmp.name) / "jobs")})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.ok_runner = mock.Mock(return_value=mock.Mock(returncode=0, stdout="", stderr=""))
        self.brief = Path(self.tmp.name) / "brief.md"
        self.brief.write_text(self.sample.BRIEF.format(finish="local", extra=""), encoding="utf-8")

    def test_a_started_pc_job_is_recorded_with_its_account(self) -> None:
        code = self.pc_job.submit(self.brief, account="second", runner=self.ok_runner, out=lambda _l: None)
        self.assertEqual(code, 0)
        rows = self.ledger.rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]["where"], rows[0]["acct"], rows[0]["ai"], rows[0]["s"]), ("PC", "second", "Claude", "discussing"))

    def test_a_dry_run_records_nothing(self) -> None:
        self.pc_job.submit(self.brief, account="second", dry_run=True, runner=self.ok_runner, out=lambda _l: None)
        self.assertEqual(self.ledger.rows(), [])

    def test_a_ledger_problem_never_stops_the_job(self) -> None:
        blocker = Path(self.tmp.name) / "blocker"
        blocker.write_text("a file where the folder should be", encoding="utf-8")
        with mock.patch.dict(os.environ, {"AGENT_OS_JOBS_DIR": str(blocker / "jobs")}):
            code = self.pc_job.submit(self.brief, account="second", runner=self.ok_runner, out=lambda _l: None)
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
