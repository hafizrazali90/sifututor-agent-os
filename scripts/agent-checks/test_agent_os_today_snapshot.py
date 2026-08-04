#!/usr/bin/env python3
"""Fixtures for the bounded cross-project Agent OS today snapshot."""

from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).with_name("agent-os-today-snapshot.py")
PLANNER_MODULE_PATH = Path(__file__).with_name("agent-os-planner-probe.py")
RESPONSE_MODULE_PATH = Path(__file__).with_name("agent-os-response-shape-runner.py")


def load_module():
    spec = importlib.util.spec_from_file_location("agent_os_today_snapshot", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_planner_module():
    spec = importlib.util.spec_from_file_location("agent_os_planner_probe", PLANNER_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {PLANNER_MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_response_module():
    spec = importlib.util.spec_from_file_location("agent_os_response_shape", RESPONSE_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {RESPONSE_MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TodaySnapshotFixtures(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / ".agent-os/session-maps").mkdir(parents=True)
        (self.root / "docs/agent-playbooks/mission-ledger").mkdir(parents=True)
        (self.root / "sifu-tutor/.claude/tasks").mkdir(parents=True)

        (self.root / ".agent-os/session-maps/active.md").write_text(
            """# Session Map: Release review

## Human Snapshot

- **Right now:** Review the mobile release evidence.
- **Next recommended move:** Name the independent reviewer.
- **Decision needed from Hafiz:** yes: choose the reviewer

## Progress Board

| Item | Status | Owner | Evidence / Link | Next |
| --- | --- | --- | --- | --- |
| Mobile release proof | PR open; not merged or live | Mobile developer review/release | PR #36 | Review, attach exact-build evidence, then release |
| Backend release | Complete and live | Codex | PR #35 | No action |

## Agent Context

- **Lifecycle state:** Active
- **Project:** sifututor_tutor
"""
        )
        (self.root / "docs/agent-playbooks/mission-ledger/cross-project.md").write_text(
            """# Cross-Project Mission Ledger

### AO-TEST-001 — Resume the personal pilot

- **Project:** cross-project
- **Status:** active
- **Next action:** Run a non-critical acceptance session.

### AO-TEST-002 — Future staff rollout

- **Project:** cross-project
- **Status:** paused
- **Next action:** Wait until the personal pilot is accepted.
"""
        )
        (self.root / "sifu-tutor/.claude/tasks/active.json").write_text(
            json.dumps({"activeTask": None})
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_collectors_are_invoked_once_and_candidates_are_labeled(self) -> None:
        calls = {"planner": 0, "github": 0}

        def planner_loader():
            calls["planner"] += 1
            return {
                "name": "planner",
                "state": "available",
                "task_summaries": [
                    {
                        "title": "Staff reports commitment fee is repeated",
                        "percent_complete": 0,
                        "created_at": "2026-08-04T01:00:00Z",
                    }
                ],
            }

        def github_loader():
            calls["github"] += 1
            return {
                "name": "github",
                "state": "available",
                "items": [
                    {
                        "title": "Tutor app release PR needs independent review",
                        "url": "https://github.com/example/repo/pull/36",
                        "updated_at": "2026-08-04T02:00:00Z",
                    }
                ],
            }

        snapshot = self.module.build_snapshot(
            self.root,
            planner_loader=planner_loader,
            github_loader=github_loader,
            now=datetime(2026, 8, 4, 3, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(calls, {"planner": 1, "github": 1})
        self.assertLessEqual(snapshot["scan_budget"]["planner_invocations"], 1)
        self.assertLessEqual(snapshot["scan_budget"]["github_invocations"], 1)
        self.assertIn("candidate_totals", snapshot)
        self.assertIn("returned_counts", snapshot)
        self.assertIn("omitted_counts", snapshot)
        self.assertLessEqual(len(snapshot["candidates"]), len(self.module.ATTENTION_GROUPS) * 5)
        self.assertEqual(
            sum(snapshot["returned_counts"].values()),
            len(snapshot["candidates"]),
        )
        self.assertTrue(snapshot["candidates"])
        for candidate in snapshot["candidates"]:
            self.assertIn(candidate["group"], self.module.ATTENTION_GROUPS)
            self.assertIn(candidate["confidence"], self.module.CONFIDENCE_LEVELS)
            self.assertTrue(candidate["freshness"])
            self.assertIn(candidate["approval"]["state"], self.module.APPROVAL_STATES)

    def test_session_decision_and_mission_status_route_to_expected_groups(self) -> None:
        snapshot = self.module.build_snapshot(
            self.root,
            planner_loader=lambda: {"name": "planner", "state": "not_connected"},
            github_loader=lambda: {"name": "github", "state": "not_connected"},
            now=datetime(2026, 8, 4, 3, 0, tzinfo=timezone.utc),
        )
        by_title = {item["title"]: item for item in snapshot["candidates"]}

        self.assertEqual(by_title["Release review"]["group"], "needs_hafiz_now")
        self.assertEqual(
            by_title["Mobile release proof"]["group"],
            "waiting_on_staff",
        )
        self.assertEqual(
            by_title["Resume the personal pilot"]["group"],
            "agent_can_continue",
        )
        self.assertEqual(by_title["Future staff rollout"]["group"], "deferred")

    def test_markdown_has_five_groups_evidence_and_honest_approval_wording(self) -> None:
        snapshot = self.module.build_snapshot(
            self.root,
            planner_loader=lambda: {"name": "planner", "state": "not_connected"},
            github_loader=lambda: {"name": "github", "state": "not_connected"},
            now=datetime(2026, 8, 4, 3, 0, tzinfo=timezone.utc),
        )
        markdown = self.module.render_markdown(snapshot)

        for heading in (
            "## Needs Hafiz now",
            "## Waiting on staff",
            "## Agent can continue",
            "## Monitor",
            "## Deferred",
        ):
            self.assertIn(heading, markdown)
        self.assertIn("Confidence:", markdown)
        self.assertIn("Freshness:", markdown)
        self.assertNotIn("approve preparation", markdown.lower())
        self.assertNotIn("approve read-only", markdown.lower())
        self.assertIn("Read-only preparation does not need approval", markdown)

    def test_sensitive_fragments_are_redacted(self) -> None:
        value = (
            "Contact person@example.com at https://example.com/path "
            "using sk-test-abcdefghijklmnopqrstuvwxyz123456"
        )
        sanitized = self.module.sanitize_text(value)
        self.assertNotIn("person@example.com", sanitized)
        self.assertNotIn("https://example.com/path", sanitized)
        self.assertNotIn("abcdefghijklmnopqrstuvwxyz123456", sanitized)
        self.assertIn("[email]", sanitized)
        self.assertIn("[url]", sanitized)
        self.assertIn("[redacted]", sanitized)

    def test_github_source_link_is_preserved_and_old_remote_update_is_stale(self) -> None:
        snapshot = self.module.build_snapshot(
            self.root,
            planner_loader=lambda: {"name": "planner", "state": "not_connected"},
            github_loader=lambda: {
                "name": "github",
                "state": "available",
                "items": [
                    {
                        "title": "Review current release evidence",
                        "url": "https://github.com/example/repo/pull/36",
                        "updated_at": "2026-07-01T02:00:00Z",
                    }
                ],
            },
            now=datetime(2026, 8, 4, 3, 0, tzinfo=timezone.utc),
        )
        item = next(
            candidate
            for candidate in snapshot["candidates"]
            if candidate["title"] == "Review current release evidence"
        )

        self.assertEqual(
            item["source_ref"],
            "https://github.com/example/repo/pull/36",
        )
        self.assertIn("stale", item["freshness"])
        self.assertIn(
            "[source](https://github.com/example/repo/pull/36)",
            self.module.render_markdown(snapshot),
        )

    def test_current_candidate_ranks_ahead_of_stale_remote_candidate(self) -> None:
        current = self.module.candidate(
            title="Current session work",
            project="umbrella",
            group="monitor",
            source="Session Map",
            confidence="trusted",
            freshness="current; source modified 2026-08-04 02:00 UTC",
            next_action="Review current evidence.",
        )
        stale = self.module.candidate(
            title="Old remote PR",
            project="example",
            group="monitor",
            source="GitHub",
            confidence="verified",
            freshness="stale; remote updated 2026-07-01 02:00 UTC",
            next_action="Review old evidence.",
        )

        bounded, _, _ = self.module.bound_candidates([stale, current])

        self.assertEqual(
            [item["title"] for item in bounded],
            ["Current session work", "Old remote PR"],
        )

    def test_planner_batch_returns_only_limited_sanitized_incomplete_tasks(self) -> None:
        planner = load_planner_module()
        tasks = [
            {
                "id": "task-complete",
                "title": "Completed card",
                "percentComplete": 100,
                "createdDateTime": "2026-08-01T00:00:00Z",
            },
            {
                "id": "task-new",
                "title": (
                    "Contact person@example.com about https://example.com/case "
                    "password=should-not-appear"
                ),
                "percentComplete": 0,
                "createdDateTime": "2026-08-04T00:00:00Z",
            },
            {
                "id": "task-old",
                "title": "Review older staff report",
                "percentComplete": 50,
                "createdDateTime": "2026-08-03T00:00:00Z",
            },
        ]

        summaries = planner.summarize_tasks(tasks, limit=1)

        self.assertEqual(len(summaries), 1)
        self.assertEqual(summaries[0]["task_id"], "task-new")
        self.assertNotIn("person@example.com", summaries[0]["title"])
        self.assertNotIn("https://example.com/case", summaries[0]["title"])
        self.assertNotIn("should-not-appear", summaries[0]["title"])
        self.assertIn("[redacted]", summaries[0]["title"])
        self.assertEqual(summaries[0]["percent_complete"], 0)

    def test_today_briefing_response_contract_rejects_missing_groups_and_false_approval(self) -> None:
        response = load_response_module()
        good = """## Needs Hafiz now
Source: GitHub · Confidence: verified · Freshness: checked now
## Waiting on staff
Nothing currently identified.
## Agent can continue
Read-only diagnosis can continue without approval.
## Monitor
Planner report · Confidence: reported · Freshness: checked now
## Deferred
Mission Ledger item · Confidence: trusted · Freshness: recent
Approval rule: read-only preparation does not need approval; ask immediately
before the exact write, release, production, access, or destructive action.
"""
        bad = """## Priorities
Approve preparation of credential rotations.
Planner says the issue is real.
"""

        self.assertEqual(response.today_briefing_violations(good), [])
        violations = response.today_briefing_violations(bad)
        self.assertTrue(any("missing attention group" in item for item in violations))
        self.assertIn("asks approval for preparation/read-only work", violations)
        self.assertIn("missing confidence/evidence label", violations)


if __name__ == "__main__":
    unittest.main()
