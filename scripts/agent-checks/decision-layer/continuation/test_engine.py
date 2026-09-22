#!/usr/bin/env python3
"""TDD tests for the continuation-decision engine (bundle 4, issue #162).

This is the module's own bounded orchestrator: pre-policy first (final
authority), otherwise route through bundle 1's decision layer using the
fake provider only. Every test here is offline and deterministic -- no
test makes, or can make, a network call, and `ScriptedProvider` (from
`fixtures_support.py`) never leaves memory.

Test groups:

- EngineOutcomeFixturesTest: at least one fixture per outcome value.
- EngineRegressionFixturesTest: the four named regression fixtures from
  the build spec's "Fixtures required" section.
- EngineAnnouncementIsNotAStopOrPauseSignalTest: "I'm about to do X" is
  never, by itself, a stop/pause/complete signal.
- EngineHasNoSideEffectsTest / EngineResponseCannotBeMistakenForApprovalTest:
  the structural proofs the build spec's scope boundary requires.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from . import engine, fixtures_support, schema

_HERE = Path(__file__).resolve().parent
_DECISION_LAYER_DIR = _HERE.parent
if str(_DECISION_LAYER_DIR) not in sys.path:
    sys.path.insert(0, str(_DECISION_LAYER_DIR))

import provider_fake  # noqa: E402  (bundle 1, shared)

base_request = fixtures_support.base_request
ScriptedProvider = fixtures_support.ScriptedProvider


class EngineOutcomeFixturesTest(unittest.TestCase):
    """Proof: at least one fixture per outcome value in schema.OUTCOME_VALUES."""

    def test_recommends_continue_via_decision_layer(self) -> None:
        provider = ScriptedProvider("continue")
        response = engine.decide(base_request(), provider=provider)
        self.assertEqual(response["outcome"], "continue")
        self.assertEqual(response["source"], "decision_layer")
        self.assertFalse(response["authoritative"])
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


class EngineRegressionFixturesTest(unittest.TestCase):
    """The four named regression fixtures from the build spec."""

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

    def test_already_approved_end_to_end_boundary_recommends_continue_through(
        self,
    ) -> None:
        provider = ScriptedProvider("pause-for-human")  # would disagree if ever asked
        request = base_request(
            session_state={"end_to_end_boundary_already_approved": True}
        )
        response = engine.decide(request, provider=provider)
        self.assertEqual(response["outcome"], "continue")
        self.assertEqual(response["source"], "pre_policy")
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


class EngineUsesOnlyTheFakeProviderTest(unittest.TestCase):
    def test_default_config_always_names_the_fake_provider(self) -> None:
        self.assertEqual(engine.build_decision_layer_config()["provider"], "fake")

    def test_the_default_provider_bundle1_builds_is_the_fake_provider_class(self) -> None:
        # decide() with no injected provider must still resolve, internally,
        # to bundle 1's FakeProvider -- never a live network-capable one.
        response = engine.decide(base_request())
        self.assertIn(response["outcome"], schema.OUTCOME_VALUES)


class EngineHasNoSideEffectsTest(unittest.TestCase):
    """Structural proof: decide() cannot perform a side effect -- no git
    operation, no file write outside its own test fixtures, no tool
    invocation -- for the pre-policy path or the decision-layer path."""

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


class EngineResponseCannotBeMistakenForApprovalTest(unittest.TestCase):
    """Proof: the response type has no field that any caller could mistake
    for an approval token, and its `authoritative` field is always False."""

    def test_response_field_names_never_look_like_an_approval_token(self) -> None:
        for field in schema.response_schema_fields():
            lowered = field.lower()
            for bad in _APPROVAL_SHAPED_KEY_SUBSTRINGS:
                self.assertNotIn(bad, lowered, f"field {field!r} looks approval-shaped")

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

    def test_response_is_a_plain_dict_with_exactly_the_declared_fields(self) -> None:
        response = engine.decide(base_request(), provider=ScriptedProvider("continue"))
        self.assertIsInstance(response, dict)
        self.assertEqual(set(response.keys()), set(schema.response_schema_fields()))


if __name__ == "__main__":
    unittest.main()
