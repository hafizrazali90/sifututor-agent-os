#!/usr/bin/env python3
"""Tests for local, non-authoritative approval-boundary evidence.

The normal way to reach the matching status is a packet written through
agent-os-task-context.py's supervisor API for this exact session and worktree.
Everything supplied inside the decision request -- booleans, task text,
reference strings, or another session's packet -- must not match. A matching
local packet is still advisory metadata, not authenticated authority and not
permission to perform a side effect.
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


approval = load_module("approval")
task_context = approval.task_context

SESSION = "sess-approval-test"
TASK = "issue-164"


class ApprovalEvidenceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.state_dir = root / "approval-state"
        self.worktree = root / "wt"
        self.worktree.mkdir()
        self.state_dir.mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def enroll(self, *, included=("commit", "push"), excluded=("merge", "deploy"), session=SESSION, task=TASK) -> Path:
        boundary = task_context.serialize_approval_boundary(
            task_id=task, included_operations=list(included), excluded_operations=list(excluded),
            approval_provenance="hafiz:chat:2026-09-22",
        )
        task_context.activate_approval_packet(self.state_dir, session, self.worktree, boundary, [])
        return task_context.session_binding_path(self.state_dir / "tool-packets", session)

    def evaluate(self, **overrides):
        kwargs = dict(session_id=SESSION, worktree=self.worktree, task_id=TASK, operation="commit", state_dir=self.state_dir)
        kwargs.update(overrides)
        return approval.evaluate(**kwargs)


class LocalBoundaryPacketMatchesOnlyExactBinding(ApprovalEvidenceTestCase):
    def test_real_supervisor_packet_approves_an_included_operation(self) -> None:
        self.enroll()
        status = self.evaluate()
        self.assertTrue(status.approved)
        self.assertFalse(status.authoritative)
        self.assertEqual(status.reason, "local_boundary_packet_matches")
        self.assertEqual(status.evidence.approval_provenance, "hafiz:chat:2026-09-22")

    def test_excluded_or_absent_operations_are_mismatched(self) -> None:
        self.enroll()
        self.assertEqual(self.evaluate(operation="merge").status, approval.STATUS_MISMATCHED)
        self.assertEqual(self.evaluate(operation="rollback").status, approval.STATUS_MISMATCHED)
        self.assertEqual(self.evaluate(operation=None).reason, "operation_not_included")

    def test_other_session_worktree_or_task_never_approves(self) -> None:
        self.enroll()
        self.assertEqual(self.evaluate(session_id="someone-else").status, approval.STATUS_MISSING)
        self.assertEqual(self.evaluate(worktree=self.worktree.parent).reason, "worktree_mismatch")
        self.assertEqual(self.evaluate(task_id="issue-999").reason, "task_id_mismatch")


class NothingWorkerControlledCanAuthorize(ApprovalEvidenceTestCase):
    def test_absent_packet_is_missing_regardless_of_any_claim(self) -> None:
        status = self.evaluate()
        self.assertEqual(status.status, approval.STATUS_MISSING)
        self.assertFalse(status.approved)
        self.assertIsNone(status.evidence)

    def test_fabricated_packet_without_valid_boundary_is_invalid(self) -> None:
        path = task_context.session_binding_path(self.state_dir / "tool-packets", SESSION)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "schema_version": task_context.SCHEMA_VERSION, "session_id": SESSION,
            "worktree": str(self.worktree.resolve()), "tool_grants": [],
            "boundary": {"task_id": TASK, "end_to_end_boundary_already_approved": True},
        }))
        self.assertEqual(self.evaluate().status, approval.STATUS_INVALID)

    def test_packet_copied_from_another_session_is_rejected(self) -> None:
        source = self.enroll(session="original-session")
        copied = task_context.session_binding_path(self.state_dir / "tool-packets", SESSION)
        copied.write_text(source.read_text())
        self.assertEqual(self.evaluate().reason, "packet_invalid")

    def test_evaluate_never_writes_state(self) -> None:
        self.evaluate()
        self.assertFalse((self.state_dir / "tool-packets").exists())


class ExpiryTest(ApprovalEvidenceTestCase):
    def _stamp(self, expires_at: str) -> None:
        path = self.enroll()
        packet = json.loads(path.read_text())
        packet["expires_at"] = expires_at
        path.write_text(json.dumps(packet))

    def test_expired_packet_is_expired_not_approved(self) -> None:
        self._stamp("2026-09-22T00:00:00+00:00")
        status = self.evaluate(now=dt.datetime(2026, 9, 23, tzinfo=dt.timezone.utc))
        self.assertEqual(status.status, approval.STATUS_EXPIRED)
        self.assertFalse(status.approved)

    def test_unexpired_packet_still_approves(self) -> None:
        self._stamp("2026-09-30T00:00:00Z")
        self.assertTrue(self.evaluate(now=dt.datetime(2026, 9, 23, tzinfo=dt.timezone.utc)).approved)

    def test_garbage_expiry_invalidates_the_packet(self) -> None:
        self._stamp("never")
        self.assertEqual(self.evaluate().status, approval.STATUS_INVALID)


if __name__ == "__main__":
    unittest.main()
