#!/usr/bin/env python3
"""Tests for the two representative expensive-check examples (slice 9b).

These test the checks' own success-path logic in isolation (fast backend,
no dispatcher). Unavailability/degrade behavior is the dispatcher's job and
is exercised through the real dispatcher in test_dispatcher.py and, for
these two concrete checks specifically, in
test_check_expensive_examples_via_dispatcher.py below.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from check_expensive_examples import RemotePolicyCheck, StaffNoticeCheck  # noqa: E402
from dispatcher import HookDispatcher  # noqa: E402
from models import HookRequest, Outcome, Severity  # noqa: E402


class RemotePolicyCheckTests(unittest.TestCase):
    def test_is_required_and_expensive(self):
        check = RemotePolicyCheck(backend=lambda r: True)
        self.assertEqual(check.severity, Severity.REQUIRED)
        self.assertTrue(check.expensive)

    def test_applies_to_git_push(self):
        check = RemotePolicyCheck(backend=lambda r: True)
        self.assertTrue(check.applies(HookRequest(tool_name="Bash", command="git push")))
        self.assertFalse(check.applies(HookRequest(tool_name="Bash", command="git status")))

    def test_allows_when_backend_approves(self):
        check = RemotePolicyCheck(backend=lambda r: True)
        decision = check.run(HookRequest(tool_name="Bash", command="git push"))
        self.assertEqual(decision.outcome, Outcome.ALLOW)

    def test_denies_when_backend_rejects(self):
        check = RemotePolicyCheck(backend=lambda r: False)
        decision = check.run(HookRequest(tool_name="Bash", command="git push"))
        self.assertEqual(decision.outcome, Outcome.DENY)
        self.assertTrue(decision.guidance)


class StaffNoticeCheckTests(unittest.TestCase):
    def test_is_advisory_and_expensive(self):
        check = StaffNoticeCheck(backend=lambda r: None)
        self.assertEqual(check.severity, Severity.ADVISORY)
        self.assertTrue(check.expensive)

    def test_allows_with_note_when_backend_has_something_to_say(self):
        check = StaffNoticeCheck(backend=lambda r: "Koda memory is 92% confirmed.")
        decision = check.run(HookRequest(tool_name="Bash", command='git commit -m "x"'))
        self.assertEqual(decision.outcome, Outcome.ALLOW)
        self.assertIn("Koda", decision.note)

    def test_allows_silently_when_backend_has_nothing_to_say(self):
        check = StaffNoticeCheck(backend=lambda r: None)
        decision = check.run(HookRequest(tool_name="Bash", command='git commit -m "x"'))
        self.assertEqual(decision.outcome, Outcome.ALLOW)
        self.assertEqual(decision.note, "")


class ExpensiveChecksViaDispatcherTests(unittest.TestCase):
    """The bundle's two required fixtures, exercised with the actual named
    example checks rather than a generic test double."""

    def test_remote_policy_check_blocks_when_backend_raises(self):
        def flaky_backend(request):
            raise ConnectionError("policy service unreachable")

        dispatcher = HookDispatcher([RemotePolicyCheck(backend=flaky_backend)])
        result = dispatcher.dispatch(HookRequest(tool_name="Bash", command="git push"))
        self.assertTrue(result.blocked)
        self.assertIn("required", result.blocking_decision.guidance.lower())

    def test_staff_notice_check_degrades_when_backend_raises(self):
        def flaky_backend(request):
            raise TimeoutError("koda unreachable")

        dispatcher = HookDispatcher([StaffNoticeCheck(backend=flaky_backend)])
        result = dispatcher.dispatch(HookRequest(tool_name="Bash", command='git commit -m "x"'))
        self.assertFalse(result.blocked)
        self.assertEqual(len(result.degraded_decisions), 1)
        self.assertIn("proceed with caution", result.degraded_decisions[0].note.lower())


if __name__ == "__main__":
    unittest.main()
