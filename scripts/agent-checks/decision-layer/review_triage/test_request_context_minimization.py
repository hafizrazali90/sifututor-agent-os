#!/usr/bin/env python3
"""Proof: the decision-layer request built by `triage.triage_change` never
carries raw review content.

`_summarize_for_decision_layer` is meant to send counts only -- never diff
text, file contents, review-comment bodies, commit messages, file paths or
the task description. This module pins that down three ways:

  1. For every fixture that actually reaches the provider, no string value
     anywhere in the input payload appears anywhere in the request the
     provider receives (checked against the whole serialized request, not
     only the `context` field).
  2. A payload deliberately poisoned with sentinel diff text, file
     contents, commit messages and a comment body still produces a request
     containing none of them, even though those keys are not part of the
     documented payload shape -- unknown free-text keys are dropped, not
     forwarded.
  3. The `context` field matches the exact counts-only format, so any
     future change that adds free text has to change this test on purpose.

The checker itself is sanity-tested against a request that does contain a
comment body, so a silently broken checker cannot make this suite pass.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import unittest

HERE = Path(__file__).resolve().parent
_DECISION_LAYER_DIR = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(_DECISION_LAYER_DIR))

import fixtures  # noqa: E402
import provider_fake  # noqa: E402
import triage  # noqa: E402

_CONTEXT_FORMAT = re.compile(r"^changed_files=\d+ flagged_signals=\d+ total_flags=\d+$")

# Fixtures whose signals are all below "high", so the orchestrator really
# does build a request and dispatch it. A fixture that is deterministically
# "high" never builds a request at all (see `test_triage.py`), so it cannot
# be used to inspect one.
_PROVIDER_REACHING_FIXTURES = (
    fixtures.clean_small_fix,
    fixtures.ci_failure_flaky,
    fixtures.ci_failure_not_inferable,
    fixtures.review_comment_informational,
)


class RecordingFakeProvider(provider_fake.FakeProvider):
    """The offline FakeProvider, plus a copy of every request it was handed."""

    def __init__(self) -> None:
        super().__init__(scenario="ok")
        self.requests: list[dict] = []

    def dispatch(self, request: dict, *, timeout_s: float | None = None) -> object:
        self.requests.append(json.loads(json.dumps(request)))
        return super().dispatch(request, timeout_s=timeout_s)


def _string_leaves(value: object) -> set[str]:
    """Every non-empty string value (not key) anywhere inside `value`."""
    if isinstance(value, str):
        return {value} if value else set()
    if isinstance(value, dict):
        found: set[str] = set()
        for child in value.values():
            found |= _string_leaves(child)
        return found
    if isinstance(value, (list, tuple, set)):
        found = set()
        for child in value:
            found |= _string_leaves(child)
        return found
    return set()


def _leaked_strings(payload: dict, request: dict) -> set[str]:
    serialized = json.dumps(request, sort_keys=True)
    return {leaf for leaf in _string_leaves(payload) if leaf in serialized}


class NoPayloadStringReachesTheProviderTest(unittest.TestCase):
    def test_every_provider_reaching_fixture_leaks_nothing(self) -> None:
        for build in _PROVIDER_REACHING_FIXTURES:
            with self.subTest(fixture=build.__name__):
                payload = build()
                recorder = RecordingFakeProvider()
                triage.triage_change(payload, provider=recorder)
                self.assertEqual(len(recorder.requests), 1, "fixture must actually reach the provider for this check to mean anything")
                self.assertEqual(_leaked_strings(payload, recorder.requests[0]), set())

    def test_context_is_counts_only(self) -> None:
        for build in _PROVIDER_REACHING_FIXTURES:
            with self.subTest(fixture=build.__name__):
                recorder = RecordingFakeProvider()
                triage.triage_change(build(), provider=recorder)
                context = recorder.requests[0]["context"]
                self.assertRegex(context, _CONTEXT_FORMAT)


class PoisonedPayloadNeverReachesTheProviderTest(unittest.TestCase):
    SENTINELS = {
        "diff_text": "SENTINEL_DIFF_TEXT_a91f @@ -1,3 +1,4 @@ +const secretishLine = 1;",
        "file_contents": "SENTINEL_FILE_CONTENTS_c02e export default function EmptyState() {}",
        "commit_messages": ["SENTINEL_COMMIT_MESSAGE_5d7b fix typo in empty state"],
        "comment_body": "SENTINEL_COMMENT_BODY_e34a LGTM, nice small fix.",
        "task_description": "SENTINEL_TASK_DESCRIPTION_77b1 fix a typo in the tutor list empty state copy.",
    }

    def _poisoned_payload(self) -> dict:
        payload = fixtures.clean_small_fix()
        payload["task_description"] = self.SENTINELS["task_description"]
        payload["review_comments"] = [{"author": "codex", "body": self.SENTINELS["comment_body"]}]
        # Keys outside the documented payload shape: a careless caller could
        # hand these over, and they still must never be forwarded.
        payload["diff_text"] = self.SENTINELS["diff_text"]
        payload["file_contents"] = self.SENTINELS["file_contents"]
        payload["commit_messages"] = list(self.SENTINELS["commit_messages"])
        return payload

    def test_no_sentinel_appears_anywhere_in_the_request(self) -> None:
        payload = self._poisoned_payload()
        recorder = RecordingFakeProvider()
        report = triage.triage_change(payload, provider=recorder)

        self.assertEqual(report["overall_decision_source"], "provider")
        self.assertEqual(len(recorder.requests), 1)
        serialized = json.dumps(recorder.requests[0], sort_keys=True)
        for name, sentinel in self.SENTINELS.items():
            with self.subTest(field=name):
                for piece in (sentinel if isinstance(sentinel, list) else [sentinel]):
                    self.assertNotIn(piece, serialized)
                    self.assertNotIn(piece.split(" ")[0], serialized)
        self.assertEqual(_leaked_strings(payload, recorder.requests[0]), set())

    def test_a_critical_lane_payload_with_sentinels_builds_no_request_at_all(self) -> None:
        payload = fixtures.payments_touching_change()
        payload["diff_text"] = self.SENTINELS["diff_text"]
        payload["review_comments"] = [{"author": "codex", "body": self.SENTINELS["comment_body"]}]
        recorder = RecordingFakeProvider()
        report = triage.triage_change(payload, provider=recorder)
        self.assertEqual(report["overall_decision_source"], "deterministic")
        self.assertEqual(recorder.requests, [])


class CheckerSanityTest(unittest.TestCase):
    """If `_leaked_strings` were broken, every test above would pass for the
    wrong reason. Prove it catches a real leak."""

    def test_checker_catches_a_comment_body_in_the_request(self) -> None:
        payload = fixtures.review_comment_informational()
        body = payload["review_comments"][0]["body"]
        leaking_request = {
            "schema_version": 1,
            "decision_type": triage.OVERALL_DECISION_TYPE,
            "options": ["low", "medium", "high"],
            "context": f"changed_files=0 comment={body}",
            "sensitivity": "low",
        }
        self.assertIn(body, _leaked_strings(payload, leaking_request))

    def test_checker_catches_a_file_path_in_the_request(self) -> None:
        payload = fixtures.clean_small_fix()
        path = payload["changed_files"][0]["path"]
        leaking_request = {"context": f"files: {path}"}
        self.assertIn(path, _leaked_strings(payload, leaking_request))


if __name__ == "__main__":
    unittest.main()
