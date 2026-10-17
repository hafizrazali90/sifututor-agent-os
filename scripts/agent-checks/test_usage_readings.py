#!/usr/bin/env python3
"""Tests for the Claude usage status line, the usage reader and the installer.

Agreed with Hafiz on 17/10/2026: show real usage per account on the Session Map
page, never an invented number. A Claude reading exists only after the status
line has run for that account, and every reading carries the time it was taken.
"""

from __future__ import annotations

import importlib.util
import io
import json
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


# 17/10/2026 20:00 MYT is 12:00 UTC.
NOW = 1_792_238_400.0
PAYLOAD = {
    "session_id": "abc",
    "rate_limits": {
        "five_hour": {"used_percentage": 23.4, "resets_at": NOW + 3600},
        "seven_day": {"used_percentage": 61.0, "resets_at": NOW + 3 * 86400},
    },
}


class StatusLineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.line = load("claude_usage_statusline", "claude_usage_statusline.py")

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name) / "usage"
        self.config = Path(self.tmp.name) / "profile"
        self.config.mkdir()
        (self.config / ".claude.json").write_text(
            json.dumps({"oauthAccount": {"emailAddress": "hafiz.razali@sifututor.my"}}), encoding="utf-8"
        )
        patcher = mock.patch.dict(os.environ, {"AGENT_OS_USAGE_DIR": str(self.dir), "CLAUDE_CONFIG_DIR": str(self.config)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_a_reading_is_saved_and_a_short_line_is_returned(self) -> None:
        text = self.line.handle(PAYLOAD, now=NOW)
        self.assertEqual(text, "5h 23% · week 61%")
        saved = json.loads((self.dir / "claude-hafiz.razali.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["account"], "hafiz.razali")
        self.assertEqual(saved["seven_day"]["used"], 61.0)
        self.assertEqual(saved["five_hour"]["resets_at"], NOW + 3600)
        self.assertEqual(saved["read_at"], NOW)

    def test_no_rate_limits_saves_nothing_and_prints_nothing(self) -> None:
        self.assertEqual(self.line.handle({"session_id": "abc"}, now=NOW), "")
        self.assertFalse(self.dir.exists())

    def test_an_old_reading_is_not_overwritten_by_an_empty_payload(self) -> None:
        self.line.handle(PAYLOAD, now=NOW)
        self.line.handle({"rate_limits": {}}, now=NOW + 99)
        saved = json.loads((self.dir / "claude-hafiz.razali.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["read_at"], NOW)

    def test_an_unreadable_account_is_saved_as_unknown(self) -> None:
        (self.config / ".claude.json").write_text("not json", encoding="utf-8")
        self.line.handle(PAYLOAD, now=NOW)
        self.assertTrue((self.dir / "claude-unknown.json").is_file())

    def test_percentages_are_kept_between_zero_and_one_hundred(self) -> None:
        payload = {"rate_limits": {"five_hour": {"used_percentage": 250, "resets_at": NOW}, "seven_day": {"used_percentage": -5, "resets_at": NOW}}}
        self.assertEqual(self.line.handle(payload, now=NOW), "5h 100% · week 0%")

    def test_nan_and_infinite_percentages_are_ignored(self) -> None:
        for bad in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(bad=bad):
                payload = {"rate_limits": {"five_hour": {"used_percentage": bad}, "seven_day": {"used_percentage": 40, "resets_at": float("nan")}}}
                self.assertEqual(self.line.handle(payload, now=NOW), "week 40%")
                saved = json.loads((self.dir / "claude-hafiz.razali.json").read_text(encoding="utf-8"))
                self.assertIsNone(saved["five_hour"])
                self.assertIsNone(saved["seven_day"]["resets_at"])

    def test_garbage_input_never_crashes(self) -> None:
        with mock.patch.object(sys, "stdin", io.StringIO("{{{")):
            self.assertEqual(self.line.main(), 0)


class UsageReadingsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.reader = load("usage_readings", "usage_readings.py")
        cls.line = load("claude_usage_statusline", "claude_usage_statusline.py")

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name) / "usage"
        patcher = mock.patch.dict(os.environ, {"AGENT_OS_USAGE_DIR": str(self.dir)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def save(self, account: str, now: float = NOW) -> None:
        with mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": self.write_profile(account)}):
            self.line.handle(PAYLOAD, now=now)

    def write_profile(self, account: str) -> str:
        folder = Path(self.tmp.name) / f"profile-{account}"
        folder.mkdir(exist_ok=True)
        (folder / ".claude.json").write_text(
            json.dumps({"oauthAccount": {"emailAddress": f"{account}@example.com"}}), encoding="utf-8"
        )
        return str(folder)

    def test_a_saved_reading_becomes_a_page_row_in_malaysian_time(self) -> None:
        self.save("hafiz.razali")
        rows = self.reader.claude_rows(["hafiz.razali"], now=NOW + 60)
        row = rows[0]
        self.assertEqual(row["n"], "hafiz.razali")
        self.assertEqual(row["used"], 61.0)
        self.assertEqual(row["window"], "Weekly limit")
        self.assertEqual(row["read"], "17/10 20:00 MYT")
        self.assertEqual(row["resets"], "20/10 20:00 MYT")
        self.assertIn("5-hour", row["note"])
        self.assertIn("23%", row["note"])

    def test_an_account_with_no_reading_says_so_and_has_no_number(self) -> None:
        row = self.reader.claude_rows(["syamil"], now=NOW)[0]
        self.assertIsNone(row["used"])
        self.assertIn("No reading yet", row["note"])

    def test_an_old_reading_is_marked_old(self) -> None:
        self.save("hafiz.razali")
        row = self.reader.claude_rows(["hafiz.razali"], now=NOW + 9 * 3600)[0]
        self.assertIn("old", row["note"].lower())

    def test_codex_reading_comes_from_its_own_log(self) -> None:
        sessions = Path(self.tmp.name) / "sessions" / "2026" / "10" / "17"
        sessions.mkdir(parents=True)
        event = {
            "timestamp": "2026-10-17T08:07:00.000Z",
            "payload": {
                "type": "token_count",
                "rate_limits": {"plan_type": "pro", "primary": {"used_percent": 15.0, "window_minutes": 10080, "resets_at": 1_792_650_000}},
            },
        }
        (sessions / "rollout-a.jsonl").write_text(json.dumps({"payload": {"type": "other"}}) + "\n" + json.dumps(event) + "\n", encoding="utf-8")
        row = self.reader.codex_row(Path(self.tmp.name) / "sessions")
        self.assertEqual(row["n"], "Codex")
        self.assertEqual(row["used"], 15.0)
        self.assertEqual(row["plan"], "Pro")
        self.assertEqual(row["window"], "Weekly limit")
        self.assertEqual(row["read"], "17/10 16:07 MYT")

    def test_codex_reading_is_found_at_the_end_of_a_very_large_log(self) -> None:
        sessions = Path(self.tmp.name) / "sessions" / "2026" / "10" / "17"
        sessions.mkdir(parents=True)
        filler = json.dumps({"payload": {"type": "other", "text": "x" * 900}}) + "\n"
        event = {
            "timestamp": "2026-10-17T08:07:00.000Z",
            "payload": {"type": "token_count", "rate_limits": {"plan_type": "pro", "primary": {"used_percent": 33.0, "window_minutes": 300, "resets_at": 1_792_650_000}}},
        }
        (sessions / "rollout-big.jsonl").write_text(filler * 6000 + json.dumps(event) + "\n", encoding="utf-8")
        row = self.reader.codex_row(Path(self.tmp.name) / "sessions")
        self.assertEqual(row["used"], 33.0)

    def test_codex_log_is_read_from_the_end_only(self) -> None:
        sessions = Path(self.tmp.name) / "sessions"
        sessions.mkdir()
        (sessions / "rollout-a.jsonl").write_text("x" * 5_000_000 + "\n", encoding="utf-8")
        with mock.patch("pathlib.Path.read_text", side_effect=AssertionError("whole file read")):
            row = self.reader.codex_row(sessions)
        self.assertIsNone(row["used"])

    def test_codex_with_no_log_has_no_number(self) -> None:
        row = self.reader.codex_row(Path(self.tmp.name) / "missing")
        self.assertIsNone(row["used"])
        self.assertIn("No reading yet", row["note"])

    def test_rows_are_valid_for_the_session_map_check(self) -> None:
        check = load("session_map_page_check", "session_map_page_check.py")
        self.save("hafiz.razali")
        rows = self.reader.claude_rows(["hafiz.razali", "syamil"], now=NOW + 60)
        rows.append(self.reader.codex_row(Path(self.tmp.name) / "missing"))
        data = {
            "title": "t", "asOf": "17/10 20:00 MYT", "defaultBy": "Mac · a · Claude",
            "groups": [{"name": "g", "steps": [{"n": "s", "s": "discussing", "here": True, "d": "d"}]}],
            "usage": rows,
        }
        self.assertEqual(check.check_data(data), [])


class InstallerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inst = load("install_usage_statusline", "install-usage-statusline.py") if (CHECKS / "install-usage-statusline.py").exists() else None

    def setUp(self) -> None:
        if self.inst is None:
            self.fail("install-usage-statusline.py does not exist yet")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def profile(self, name: str, settings: dict | None = None) -> Path:
        folder = self.root / name
        folder.mkdir()
        (folder / "settings.json").write_text(json.dumps(settings if settings is not None else {"model": "opus"}), encoding="utf-8")
        return folder

    def read(self, folder: Path) -> dict:
        return json.loads((folder / "settings.json").read_text(encoding="utf-8"))

    def test_a_command_from_a_worktree_is_refused(self) -> None:
        for path in (
            "/Users/someone/.local/state/sifututor-agent-os/worktrees/sifututor-383/scripts/agent-checks/claude_usage_statusline.py",
            "/Users/someone/Projects/Sifututor/.claude/worktrees/x/scripts/agent-checks/claude_usage_statusline.py",
        ):
            with self.subTest(path=path):
                self.assertIn("main checkout", self.inst.worktree_problem(f'python3 "{path}"'))
        self.assertIsNone(self.inst.worktree_problem('python3 "/Users/someone/Projects/Sifututor/scripts/agent-checks/claude_usage_statusline.py"'))

    def test_apply_from_a_worktree_changes_nothing(self) -> None:
        folder = self.profile("p")
        before = (folder / "settings.json").read_text(encoding="utf-8")
        with mock.patch.object(self.inst, "default_command", return_value='python3 "/h/.local/state/sifututor-agent-os/worktrees/w/scripts/agent-checks/claude_usage_statusline.py"'):
            code = self.inst.main(["--apply", str(folder)])
        self.assertNotEqual(code, 0)
        self.assertEqual((folder / "settings.json").read_text(encoding="utf-8"), before)

    def test_dry_run_changes_nothing(self) -> None:
        folder = self.profile("p1")
        report = self.inst.install([folder], apply=False)
        self.assertEqual(report[0][1], "would add")
        self.assertNotIn("statusLine", self.read(folder))

    def test_apply_adds_the_status_line_and_a_backup(self) -> None:
        folder = self.profile("p1")
        report = self.inst.install([folder], apply=True)
        self.assertEqual(report[0][1], "added")
        line = self.read(folder)["statusLine"]
        self.assertEqual(line["type"], "command")
        self.assertIn("claude_usage_statusline.py", line["command"])
        self.assertEqual(self.read(folder)["model"], "opus")
        self.assertTrue(list(folder.glob("settings.json.bak-*")))

    def test_an_existing_custom_status_line_is_never_overwritten(self) -> None:
        folder = self.profile("p1", {"statusLine": {"type": "command", "command": "my-own-line"}})
        report = self.inst.install([folder], apply=True)
        self.assertEqual(report[0][1], "skipped: a different status line is already set")
        self.assertEqual(self.read(folder)["statusLine"]["command"], "my-own-line")

    def test_two_profiles_that_share_one_settings_file_are_done_once(self) -> None:
        folder = self.profile("p1")
        other = self.root / "p2"
        other.mkdir()
        (other / "settings.json").symlink_to(folder / "settings.json")
        report = self.inst.install([folder, other], apply=True)
        self.assertEqual([state for _p, state in report].count("added"), 1)
        self.assertTrue(any(state.startswith("same file") for _p, state in report))

    def test_undo_removes_only_ours(self) -> None:
        mine = self.profile("p1")
        self.inst.install([mine], apply=True)
        theirs = self.profile("p2", {"statusLine": {"type": "command", "command": "my-own-line"}})
        report = self.inst.install([mine, theirs], apply=True, undo=True)
        self.assertNotIn("statusLine", self.read(mine))
        self.assertEqual(self.read(theirs)["statusLine"]["command"], "my-own-line")
        self.assertEqual(report[0][1], "removed")

    def test_a_missing_settings_file_is_reported_not_created(self) -> None:
        folder = self.root / "empty"
        folder.mkdir()
        report = self.inst.install([folder], apply=True)
        self.assertEqual(report[0][1], "skipped: no settings.json")
        self.assertFalse((folder / "settings.json").exists())


if __name__ == "__main__":
    unittest.main()
