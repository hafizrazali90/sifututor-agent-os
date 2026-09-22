#!/usr/bin/env python3
"""TDD tests for the continuation-decision engine (bundle 4, issue #162).

This is the module's own bounded orchestrator: trusted approval lookup,
then pre-policy (final authority), otherwise route through bundle 1's
decision layer using the fake provider only. Every test here is offline
and deterministic -- no test makes, or can make, a network call, and
`ScriptedProvider` (from `fixtures_support.py`) never leaves memory.

Test groups:

- EngineOutcomeFixturesTest: at least one fixture per outcome value.
- EngineRegressionFixturesTest: the named regression fixtures from the
  build spec, with the "already-approved boundary" fixture now backed by
  a real supervisor-written packet.
- EngineTrustedApprovalNegativeTest: every worker-controlled way of
  claiming approval yields a non-approved status and never `continue`
  through a boundary.
- EngineExpansionTriggersOverrideApprovalTest: the two expansion triggers
  force `pause-for-human` regardless of provider output and approval.
- EngineAnnouncementIsNotAStopOrPauseSignalTest: "I'm about to do X" is
  never, by itself, a stop/pause/complete signal.
- EngineHasNoSideEffectsTest / EngineResponseCannotBeMistakenForApprovalTest:
  the structural proofs the build spec's scope boundary requires.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from . import engine, fixtures_support, pre_policy, schema

_HERE = Path(__file__).resolve().parent
_DECISION_LAYER_DIR = _HERE.parent
if str(_DECISION_LAYER_DIR) not in sys.path:
    sys.path.insert(0, str(_DECISION_LAYER_DIR))

import approval  # noqa: E402  (bundle 1, shared)
import provider_fake  # noqa: E402  (bundle 1, shared)

task_context = approval.task_context

base_request = fixtures_support.base_request
ScriptedProvider = fixtures_support.ScriptedProvider

SESSION = "sess-continuation-test"
TASK = "issue-162"
OPERATION = "commit"


class ApprovalStateFixture(unittest.TestCase):
    """A temp approval-state dir plus a temp worktree, and a helper that
    writes a *real* packet the way the trusted supervisor API does."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.state_dir = root / "approval-state"
        self.worktree = root / "wt"
        self.worktree.mkdir()
        self.state_dir.mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def enroll(self, *, session: str = SESSION, task: str = TASK,
               included=(OPERATION, "push"), excluded=("merge", "deploy")) -> Path:
        boundary = task_context.serialize_approval_boundary(
            task_id=task,
            included_operations=list(included),
            excluded_operations=list(excluded),
            approval_provenance="hafiz:chat:2026-09-22",
        )
        task_context.activate_approval_packet(self.state_dir, session, self.worktree, boundary, [])
        return task_context.session_binding_path(self.state_dir / "tool-packets", session)

    def claims(self, **overrides) -> dict:
        state = {
            "session_id": SESSION,
            "worktree": str(self.worktree),
            "task_id": TASK,
            "requested_operation": OPERATION,
        }
        state.update(overrides)
        return state

    def decide(self, request: dict, provider=None) -> dict:
        return engine.decide(request, provider=provider, state_dir=self.state_dir)


class EngineOutcomeFixturesTest(unittest.TestCase):
    """Proof: at least one fixture per outcome value in schema.OUTCOME_VALUES."""

    def test_recommends_continue_via_decision_layer(self) -> None:
        provider = ScriptedProvider("continue")
        response = engine.decide(base_request(), provider=provider)
        self.assertEqual(response["outcome"], "continue")
        self.assertEqual(response["source"], "decision_layer")
        self.assertFalse(response["authoritative"])
        self.assertEqual(response["approval_status"], "not_checked")
        self.assertEqual(provider.call_count, 1)

    def test_recommends_retry_via_decision_layer(self) -> None:
        provider = ScriptedProvider("retry")
        response = engine.decide(base_request(), provider=provider)
        self.assertEqual(response["outcome"], "retry")

    def test_recommends_investigate_via_decision_layer(self) -> None:
        provider = ScriptedProvider("investigate")
        response = engine.decide(base_request(), provider=provider)
        self.assertEqual(response["outcome"], "investigate")

    def test_recommends_rollback_via_decision_layer(self) -> None:
        provider = ScriptedProvider("rollback")
        response = engine.decide(base_request(), provider=provider)
        self.assertEqual(response["outcome"], "rollback")

    def test_recommends_split_follow_up_via_decision_layer(self) -> None:
        provider = ScriptedProvider("split-follow-up")
        response = engine.decide(base_request(), provider=provider)
        self.assertEqual(response["outcome"], "split-follow-up")

    def test_recommends_pause_for_human_via_decision_layer(self) -> None:
        provider = ScriptedProvider("pause-for-human")
        response = engine.decide(base_request(), provider=provider)
        self.assertEqual(response["outcome"], "pause-for-human")

    def test_recommends_complete_via_decision_layer(self) -> None:
        provider = ScriptedProvider("complete")
        response = engine.decide(base_request(), provider=provider)
        self.assertEqual(response["outcome"], "complete")


class EngineRegressionFixturesTest(ApprovalStateFixture):
    """The named regression fixtures from the build spec."""

    def test_repeated_go_next_after_route_already_produced_outcome_recommends_continue(
        self,
    ) -> None:
        provider = ScriptedProvider("complete")  # would disagree if ever asked
        request = base_request(
            caller_message="go next",
            session_state={"route_outcome_already_produced": True},
        )
        response = engine.decide(request, provider=provider)
        self.assertEqual(response["outcome"], "continue")
        self.assertEqual(response["source"], "pre_policy")
        self.assertEqual(provider.call_count, 0)

    def test_real_supervisor_packet_recommends_continue_through_the_boundary(
        self,
    ) -> None:
        """Positive case: a packet written with
        `approval.task_context.activate_approval_packet(...)` for this
        exact session, worktree, task and operation yields `approved` and
        `continue`, and the provider is never asked."""
        self.enroll()
        provider = ScriptedProvider("pause-for-human")  # would disagree if ever asked
        request = base_request(session_state=self.claims())
        response = self.decide(request, provider=provider)
        self.assertEqual(response["approval_status"], "approved")
        self.assertEqual(response["approval_reason"], "local_boundary_packet_matches")
        self.assertEqual(response["outcome"], "continue")
        self.assertEqual(response["source"], "pre_policy")
        self.assertEqual(response["reason"], pre_policy.REASON_TRUSTED_APPROVAL_CONTINUE)
        self.assertIs(response["authoritative"], False)
        self.assertEqual(provider.call_count, 0)

    def test_new_unseen_scope_forces_pause_for_human_even_when_provider_disagrees(
        self,
    ) -> None:
        provider = ScriptedProvider("complete")  # scripted to disagree
        request = base_request(session_state={"new_scope_appeared": True})
        response = engine.decide(request, provider=provider)
        self.assertEqual(response["outcome"], "pause-for-human")
        self.assertEqual(response["source"], "pre_policy")
        # Deterministic authority wins: the provider is never even asked.
        self.assertEqual(provider.call_count, 0)

    def test_unavailable_rollback_or_backup_forces_pause_for_human_even_when_provider_disagrees(
        self,
    ) -> None:
        provider = ScriptedProvider("complete")  # scripted to disagree
        request = base_request(
            session_state={"rollback_or_backup_unavailable": True}
        )
        response = engine.decide(request, provider=provider)
        self.assertEqual(response["outcome"], "pause-for-human")
        self.assertEqual(response["source"], "pre_policy")
        self.assertEqual(provider.call_count, 0)


class EngineTrustedApprovalNegativeTest(ApprovalStateFixture):
    """Every worker-controlled way of claiming approval must yield a
    non-approved status and must never produce `continue` through a
    boundary. The provider is scripted to `pause-for-human` so that any
    wrongful pre-policy `continue` would be visible, and the reason code
    proves the boundary rule did not fire."""

    def assert_not_continued_through_boundary(self, response: dict, expected_status: str) -> None:
        self.assertEqual(response["approval_status"], expected_status)
        self.assertNotEqual(response["approval_status"], "approved")
        self.assertNotEqual(response["outcome"], "continue")
        self.assertNotEqual(response["outcome"], "complete")
        self.assertNotEqual(response["reason"], pre_policy.REASON_TRUSTED_APPROVAL_CONTINUE)
        self.assertIs(response["authoritative"], False)

    def test_fabricated_boolean_is_ignored_and_changes_nothing(self) -> None:
        """The retired `end_to_end_boundary_already_approved: true` is
        accepted (schema tolerates unknown keys) but has no effect: the
        response is identical to the one without it."""
        with_flag = engine.decide(
            base_request(session_state={"end_to_end_boundary_already_approved": True}),
            provider=ScriptedProvider("pause-for-human"),
        )
        without_flag = engine.decide(
            base_request(session_state={}),
            provider=ScriptedProvider("pause-for-human"),
        )
        self.assertEqual(with_flag, without_flag)
        self.assert_not_continued_through_boundary(with_flag, "not_checked")
        self.assertEqual(with_flag["approval_reason"], engine.REASON_NO_CLAIMS)

    def test_fabricated_boolean_with_claims_but_no_packet_is_still_missing(self) -> None:
        state = self.claims(end_to_end_boundary_already_approved=True)
        response = self.decide(base_request(session_state=state), ScriptedProvider("pause-for-human"))
        self.assert_not_continued_through_boundary(response, "missing")

    def test_no_packet_at_all_is_missing(self) -> None:
        response = self.decide(
            base_request(session_state=self.claims()), ScriptedProvider("pause-for-human")
        )
        self.assert_not_continued_through_boundary(response, "missing")
        self.assertEqual(response["approval_reason"], "no_packet_for_session")

    def test_hand_written_packet_without_valid_boundary_is_invalid(self) -> None:
        path = task_context.session_binding_path(self.state_dir / "tool-packets", SESSION)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "schema_version": task_context.SCHEMA_VERSION,
            "session_id": SESSION,
            "worktree": str(self.worktree.resolve()),
            "tool_grants": [],
            "boundary": {"task_id": TASK, "end_to_end_boundary_already_approved": True},
        }))
        response = self.decide(
            base_request(session_state=self.claims()), ScriptedProvider("pause-for-human")
        )
        self.assert_not_continued_through_boundary(response, "invalid")
        self.assertEqual(response["approval_reason"], "packet_invalid")

    def test_packet_that_exists_only_for_another_session_is_missing(self) -> None:
        self.enroll(session="someone-elses-session")
        response = self.decide(
            base_request(session_state=self.claims()), ScriptedProvider("pause-for-human")
        )
        self.assert_not_continued_through_boundary(response, "missing")

    def test_packet_copied_from_another_session_is_invalid(self) -> None:
        source = self.enroll(session="original-session")
        copied = task_context.session_binding_path(self.state_dir / "tool-packets", SESSION)
        copied.write_text(source.read_text())
        response = self.decide(
            base_request(session_state=self.claims()), ScriptedProvider("pause-for-human")
        )
        self.assert_not_continued_through_boundary(response, "invalid")

    def test_expired_packet_is_expired(self) -> None:
        path = self.enroll()
        packet = json.loads(path.read_text())
        packet["expires_at"] = "2000-01-01T00:00:00Z"
        path.write_text(json.dumps(packet))
        response = self.decide(
            base_request(session_state=self.claims()), ScriptedProvider("pause-for-human")
        )
        self.assert_not_continued_through_boundary(response, "expired")
        self.assertEqual(response["approval_reason"], "packet_expired")

    def test_real_packet_but_other_worktree_task_or_operation_is_mismatched(self) -> None:
        self.enroll()
        cases = {
            "worktree": self.claims(worktree=str(self.worktree.parent)),
            "task_id": self.claims(task_id="issue-999"),
            "requested_operation": self.claims(requested_operation="merge"),
            "operation_absent": {k: v for k, v in self.claims().items() if k != "requested_operation"},
        }
        for name, state in cases.items():
            with self.subTest(case=name):
                response = self.decide(
                    base_request(session_state=state), ScriptedProvider("pause-for-human")
                )
                self.assert_not_continued_through_boundary(response, "mismatched")

    def test_approval_status_smuggled_into_the_request_is_not_read(self) -> None:
        state = {"approval_status": "approved", "approval_reason": "trusted_packet_matches"}
        response = engine.decide(
            base_request(session_state=state), provider=ScriptedProvider("pause-for-human")
        )
        self.assert_not_continued_through_boundary(response, "not_checked")

    def test_non_approved_status_does_not_block_ordinary_advice(self) -> None:
        """A missing packet is not itself a reason to pause: the other
        rules still produce their ordinary advisory result."""
        response = self.decide(
            base_request(session_state=self.claims()), ScriptedProvider("investigate")
        )
        self.assertEqual(response["approval_status"], "missing")
        self.assertEqual(response["outcome"], "investigate")
        self.assertEqual(response["source"], "decision_layer")


class EngineExpansionTriggersOverrideApprovalTest(ApprovalStateFixture):
    """Both expansion triggers force `pause-for-human` regardless of what
    the provider would answer and regardless of a valid trusted approval."""

    def test_destructive_scope_expansion_pauses_even_with_a_real_approval(self) -> None:
        self.enroll()
        provider = ScriptedProvider("continue")
        state = self.claims(destructive_scope_expansion=True)
        response = self.decide(base_request(session_state=state), provider)
        self.assertEqual(response["approval_status"], "approved")
        self.assertEqual(response["outcome"], "pause-for-human")
        self.assertEqual(response["reason"], "destructive_scope_expansion")
        self.assertEqual(response["source"], "pre_policy")
        self.assertEqual(provider.call_count, 0)

    def test_critical_lane_expansion_pauses_even_with_a_real_approval(self) -> None:
        self.enroll()
        provider = ScriptedProvider("continue")
        state = self.claims(critical_lane_expansion=True)
        response = self.decide(base_request(session_state=state), provider)
        self.assertEqual(response["approval_status"], "approved")
        self.assertEqual(response["outcome"], "pause-for-human")
        self.assertEqual(response["reason"], "critical_lane_expansion")
        self.assertEqual(response["source"], "pre_policy")
        self.assertEqual(provider.call_count, 0)

    def test_expansion_triggers_pause_without_any_approval_too(self) -> None:
        for field in ("destructive_scope_expansion", "critical_lane_expansion"):
            with self.subTest(field=field):
                provider = ScriptedProvider("complete")
                response = engine.decide(base_request(session_state={field: True}), provider=provider)
                self.assertEqual(response["outcome"], "pause-for-human")
                self.assertEqual(response["reason"], field)
                self.assertEqual(provider.call_count, 0)


class EngineAnnouncementIsNotAStopOrPauseSignalTest(unittest.TestCase):
    """"I'm about to do X" is not, by itself, a stop or pause condition."""

    def test_announcing_the_next_routine_action_does_not_force_complete(self) -> None:
        provider = ScriptedProvider("continue")
        request = base_request(
            caller_message="I'm about to run the full test suite next."
        )
        response = engine.decide(request, provider=provider)
        self.assertNotEqual(response["outcome"], "complete")
        self.assertEqual(response["outcome"], "continue")

    def test_announcement_text_never_overrides_the_decision_layers_own_answer(
        self,
    ) -> None:
        """The engine must not grep caller_message for "about to" and force
        an outcome -- whatever the decision layer legitimately returns
        (here: investigate) is what comes back, proving the announcement
        phrasing has no special-cased effect on the outcome."""
        provider = ScriptedProvider("investigate")
        request = base_request(
            caller_message="I'm about to open the PR next."
        )
        response = engine.decide(request, provider=provider)
        self.assertEqual(response["outcome"], "investigate")

    def test_ordinary_continuation_with_no_provider_override_returns_continue(
        self,
    ) -> None:
        # No pre-policy condition, no scripted provider -- the module's own
        # default (bundle 1's fake provider, "ok" scenario) is exercised.
        response = engine.decide(base_request())
        self.assertEqual(response["outcome"], "continue")


class EngineValidatesRequestTest(unittest.TestCase):
    def test_raises_request_validation_error_for_a_malformed_request(self) -> None:
        provider = ScriptedProvider("continue")
        with self.assertRaises(schema.RequestValidationError):
            engine.decide({"schema_version": 1}, provider=provider)
        self.assertEqual(provider.call_count, 0)

    def test_raises_for_a_non_string_identity_claim(self) -> None:
        with self.assertRaises(schema.RequestValidationError):
            engine.decide(base_request(session_state={"session_id": 7}))


class EngineUsesOnlyTheFakeProviderTest(unittest.TestCase):
    def test_default_config_always_names_the_fake_provider(self) -> None:
        self.assertEqual(engine.build_decision_layer_config()["provider"], "fake")

    def test_the_default_provider_bundle1_builds_is_the_fake_provider_class(self) -> None:
        # decide() with no injected provider must still resolve, internally,
        # to bundle 1's FakeProvider -- never a live network-capable one.
        response = engine.decide(base_request())
        self.assertIn(response["outcome"], schema.OUTCOME_VALUES)

    def test_identity_claims_never_reach_the_provider(self) -> None:
        provider = ScriptedProvider("continue")
        state = {
            "session_id": "sess-secret-ish",
            "worktree": "/Users/someone/private/worktree",
            "task_id": "issue-162",
            "requested_operation": "commit",
            "route_outcome_already_produced": False,
        }
        engine.decide(base_request(session_state=state), provider=provider)
        context = provider.last_request["context"]
        for leaked in ("sess-secret-ish", "/Users/someone/private/worktree", "session_id", "worktree"):
            self.assertNotIn(leaked, context)
        self.assertIn("route_outcome_already_produced", context)


class EngineHasNoSideEffectsTest(ApprovalStateFixture):
    """Structural proof: decide() cannot perform a side effect -- no git
    operation, no file write, no tool invocation -- for the pre-policy
    path, the decision-layer path, or the trusted-approval lookup path."""

    def _run_with_side_effect_guards(self, fn):
        real_open = open

        def guarded_open(file, mode="r", *args, **kwargs):
            if any(flag in mode for flag in ("w", "a", "x", "+")):
                raise AssertionError(f"unexpected file write attempted: {file!r} mode={mode!r}")
            return real_open(file, mode, *args, **kwargs)

        def guarded_call(*_args, **_kwargs):
            raise AssertionError("unexpected subprocess/os call during decide()")

        with mock.patch("builtins.open", guarded_open), mock.patch(
            "subprocess.run", side_effect=guarded_call
        ), mock.patch("subprocess.Popen", side_effect=guarded_call), mock.patch(
            "os.system", side_effect=guarded_call
        ), mock.patch(
            "os.remove", side_effect=guarded_call
        ), mock.patch(
            "shutil.rmtree", side_effect=guarded_call
        ):
            return fn()

    def test_pre_policy_path_has_no_side_effects(self) -> None:
        request = base_request(session_state={"new_scope_appeared": True})
        response = self._run_with_side_effect_guards(lambda: engine.decide(request))
        self.assertEqual(response["outcome"], "pause-for-human")

    def test_decision_layer_path_has_no_side_effects(self) -> None:
        provider = ScriptedProvider("investigate")
        response = self._run_with_side_effect_guards(
            lambda: engine.decide(base_request(), provider=provider)
        )
        self.assertEqual(response["outcome"], "investigate")

    def test_trusted_approval_lookup_only_reads(self) -> None:
        self.enroll()
        request = base_request(session_state=self.claims())
        response = self._run_with_side_effect_guards(
            lambda: self.decide(request, ScriptedProvider("pause-for-human"))
        )
        self.assertEqual(response["approval_status"], "approved")

    def test_missing_packet_lookup_writes_nothing(self) -> None:
        request = base_request(session_state=self.claims())
        self._run_with_side_effect_guards(
            lambda: self.decide(request, ScriptedProvider("pause-for-human"))
        )
        self.assertFalse((self.state_dir / "tool-packets").exists())

    def test_no_files_are_created_in_the_working_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            before = set(os.listdir(tmp))
            cwd = os.getcwd()
            os.chdir(tmp)
            try:
                engine.decide(base_request(), provider=ScriptedProvider("complete"))
            finally:
                os.chdir(cwd)
            after = set(os.listdir(tmp))
            self.assertEqual(before, after)

    def test_calling_twice_with_the_same_input_returns_an_equal_result(self) -> None:
        request = base_request(session_state={"new_scope_appeared": True})
        first = engine.decide(request)
        second = engine.decide(request)
        self.assertEqual(first, second)


_APPROVAL_SHAPED_KEY_SUBSTRINGS = (
    "approv",
    "grant",
    "token",
    "authoriz",
    "authorise",
    "consent",
    "sign_off",
    "signoff",
    "permit",
    "permission",
)


class EngineResponseCannotBeMistakenForApprovalTest(ApprovalStateFixture):
    """Proof: the response type has no field that any caller could mistake
    for an approval token, and its `authoritative` field is always False.

    The two declared `approval_*` fields are the one deliberate exception
    to the name check: they are a read-only *report* of what the trusted
    record said. The tests below prove they carry only a closed set of
    status values, are derived only from `approval.evaluate`, and can
    never be set from a request -- so they cannot function as a token."""

    def test_non_report_field_names_never_look_like_an_approval_token(self) -> None:
        for field in schema.response_schema_fields():
            if field in schema.APPROVAL_REPORT_FIELDS:
                continue
            lowered = field.lower()
            for bad in _APPROVAL_SHAPED_KEY_SUBSTRINGS:
                self.assertNotIn(bad, lowered, f"field {field!r} looks approval-shaped")

    def test_the_only_approval_mentioning_fields_are_the_two_declared_reports(self) -> None:
        mentioning = [f for f in schema.response_schema_fields() if "approv" in f.lower()]
        self.assertEqual(sorted(mentioning), sorted(schema.APPROVAL_REPORT_FIELDS))
        self.assertEqual(schema.APPROVAL_REPORT_FIELDS, ("approval_status", "approval_reason"))

    def test_approval_status_is_always_one_of_the_closed_set(self) -> None:
        responses = [
            engine.decide(base_request(), provider=ScriptedProvider("continue")),
            engine.decide(base_request(session_state={"new_scope_appeared": True})),
            self.decide(base_request(session_state=self.claims()), ScriptedProvider("continue")),
        ]
        for response in responses:
            self.assertIn(response["approval_status"], schema.APPROVAL_STATUS_VALUES)
            self.assertIsInstance(response["approval_reason"], str)

    def test_response_never_says_approved_without_a_trusted_packet(self) -> None:
        attempts = (
            {},
            {"end_to_end_boundary_already_approved": True},
            {"approval_status": "approved"},
            self.claims(),
            self.claims(end_to_end_boundary_already_approved=True),
        )
        for state in attempts:
            with self.subTest(state=state):
                response = self.decide(base_request(session_state=state), ScriptedProvider("continue"))
                self.assertNotEqual(response["approval_status"], "approved")

    def test_authoritative_is_always_false_for_every_outcome(self) -> None:
        for outcome in schema.OUTCOME_VALUES:
            with self.subTest(outcome=outcome):
                response = engine.decide(base_request(), provider=ScriptedProvider(outcome))
                self.assertEqual(response["outcome"], outcome)
                self.assertIs(response["authoritative"], False)

    def test_authoritative_is_false_on_the_pre_policy_path_too(self) -> None:
        response = engine.decide(
            base_request(session_state={"new_scope_appeared": True})
        )
        self.assertIs(response["authoritative"], False)

    def test_authoritative_is_false_even_when_trusted_approval_is_approved(self) -> None:
        self.enroll()
        response = self.decide(base_request(session_state=self.claims()))
        self.assertEqual(response["approval_status"], "approved")
        self.assertIs(response["authoritative"], False)

    def test_response_is_a_plain_dict_with_exactly_the_declared_fields(self) -> None:
        response = engine.decide(base_request(), provider=ScriptedProvider("continue"))
        self.assertIsInstance(response, dict)
        self.assertEqual(set(response.keys()), set(schema.response_schema_fields()))


if __name__ == "__main__":
    unittest.main()
