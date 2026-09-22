#!/usr/bin/env python3
"""TDD tests for the dispatcher's aggregation and fail-safe/degrade rules
(slice 9) -- the core of the bundle spec:

  "Fail-safe behavior for required/blocking checks (a required check that
  cannot run should block with a clear reason, never silently pass) and
  visible, non-blocking degradation for optional/advisory checks only."

Two of these tests are exactly the two required fixtures from the bundle
spec: one proving a REQUIRED check fails closed when it cannot run, one
proving an ADVISORY check degrades visibly without blocking.
"""
from __future__ import annotations

from pathlib import Path
import sys
import time
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from dispatcher import DispatchResult, HookDispatcher  # noqa: E402
from models import Decision, HookRequest, Outcome, Severity  # noqa: E402


class _FixedCheck:
    """A check that always returns a fixed decision, for cheap tests."""

    def __init__(self, name, severity, decision, expensive=False, applies=True):
        self.name = name
        self.severity = severity
        self.expensive = expensive
        self._decision = decision
        self._applies = applies

    def applies(self, request):
        return self._applies

    def run(self, request):
        return self._decision


class _RaisingCheck:
    """An expensive check whose backend call raises -- simulates a network
    error, provider outage, or malformed response, without any real I/O."""

    def __init__(self, name, severity):
        self.name = name
        self.severity = severity
        self.expensive = True

    def applies(self, request):
        return True

    def run(self, request):
        raise ConnectionError("simulated backend outage")


class _SlowCheck:
    """An expensive check whose backend call never returns in time."""

    def __init__(self, name, severity, sleep_s):
        self.name = name
        self.severity = severity
        self.expensive = True
        self._sleep_s = sleep_s

    def applies(self, request):
        return True

    def run(self, request):
        time.sleep(self._sleep_s)
        return Decision.allow(self.name)


def _req() -> HookRequest:
    return HookRequest(tool_name="Bash", command="git commit -m \"feat: x\"")


class DispatcherCheapPathTests(unittest.TestCase):
    def test_all_allow_is_not_blocked(self):
        dispatcher = HookDispatcher([
            _FixedCheck("a", Severity.REQUIRED, Decision.allow("a")),
            _FixedCheck("b", Severity.REQUIRED, Decision.allow("b")),
        ])
        result = dispatcher.dispatch(_req())
        self.assertFalse(result.blocked)
        self.assertEqual(len(result.decisions), 2)

    def test_a_deny_blocks_the_whole_dispatch(self):
        deny = Decision.deny("b", reason="bad thing", guidance="fix the bad thing")
        dispatcher = HookDispatcher([
            _FixedCheck("a", Severity.REQUIRED, Decision.allow("a")),
            _FixedCheck("b", Severity.REQUIRED, deny),
        ])
        result = dispatcher.dispatch(_req())
        self.assertTrue(result.blocked)
        self.assertEqual(result.blocking_decision.check_name, "b")

    def test_deny_short_circuits_remaining_checks(self):
        deny = Decision.deny("a", reason="bad thing", guidance="fix the bad thing")
        never_called = _FixedCheck("b", Severity.REQUIRED, Decision.allow("b"))
        calls = []
        never_called.run = lambda request: calls.append(1) or Decision.allow("b")
        dispatcher = HookDispatcher([
            _FixedCheck("a", Severity.REQUIRED, deny),
            never_called,
        ])
        dispatcher.dispatch(_req())
        self.assertEqual(calls, [])

    def test_ask_user_does_not_block_but_is_recorded(self):
        ask = Decision.ask_user("gate", reason="confirm lint ran")
        dispatcher = HookDispatcher([_FixedCheck("gate", Severity.ADVISORY, ask)])
        result = dispatcher.dispatch(_req())
        self.assertFalse(result.blocked)
        self.assertEqual(len(result.ask_user_decisions), 1)

    def test_check_that_does_not_apply_is_skipped(self):
        dispatcher = HookDispatcher([
            _FixedCheck("a", Severity.REQUIRED, Decision.allow("a"), applies=False)
        ])
        result = dispatcher.dispatch(_req())
        self.assertEqual(result.decisions, [])


class DispatcherFailSafeTests(unittest.TestCase):
    """The two fixtures the bundle spec explicitly asks for."""

    def test_required_check_that_cannot_run_blocks_never_silently_passes(self):
        dispatcher = HookDispatcher([_RaisingCheck("remote_policy", Severity.REQUIRED)])
        result = dispatcher.dispatch(_req())
        self.assertTrue(result.blocked, "a required check that cannot run must block, not pass")
        decision = result.blocking_decision
        self.assertEqual(decision.outcome, Outcome.DENY)
        self.assertTrue(decision.guidance, "block message must carry actionable guidance")
        self.assertIn("required", decision.guidance.lower())

    def test_advisory_check_that_cannot_run_degrades_visibly_without_blocking(self):
        dispatcher = HookDispatcher([_RaisingCheck("staff_notice", Severity.ADVISORY)])
        result = dispatcher.dispatch(_req())
        self.assertFalse(result.blocked, "an advisory check that cannot run must not block")
        self.assertEqual(len(result.degraded_decisions), 1)
        note = result.degraded_decisions[0].note
        self.assertTrue(note)
        self.assertIn("proceed with caution", note.lower())

    def test_required_check_that_times_out_blocks(self):
        dispatcher = HookDispatcher(
            [_SlowCheck("remote_policy", Severity.REQUIRED, sleep_s=0.3)],
            expensive_timeout_s=0.05,
        )
        result = dispatcher.dispatch(_req())
        self.assertTrue(result.blocked)
        self.assertEqual(result.blocking_decision.outcome, Outcome.DENY)

    def test_advisory_check_that_times_out_degrades(self):
        dispatcher = HookDispatcher(
            [_SlowCheck("staff_notice", Severity.ADVISORY, sleep_s=0.3)],
            expensive_timeout_s=0.05,
        )
        result = dispatcher.dispatch(_req())
        self.assertFalse(result.blocked)
        self.assertEqual(len(result.degraded_decisions), 1)

    def test_expensive_check_that_succeeds_in_time_passes_through(self):
        dispatcher = HookDispatcher(
            [_SlowCheck("remote_policy", Severity.REQUIRED, sleep_s=0.01)],
            expensive_timeout_s=2.0,
        )
        result = dispatcher.dispatch(_req())
        self.assertFalse(result.blocked)
        self.assertEqual(result.decisions[0].outcome, Outcome.ALLOW)


if __name__ == "__main__":
    unittest.main()
