#!/usr/bin/env python3
"""Test-only helpers shared by this package's test modules.

Not itself a test module (its filename does not match the `test_*.py`
discovery pattern), so `unittest discover` never tries to load test cases
from it directly.
"""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_DECISION_LAYER_DIR = _HERE.parent
if str(_DECISION_LAYER_DIR) not in sys.path:
    sys.path.insert(0, str(_DECISION_LAYER_DIR))

import provider_base  # noqa: E402  (bundle 1, shared)
import provider_fake  # noqa: E402  (bundle 1, shared)


class ScriptedProvider(provider_fake.FakeProvider):
    """A `provider_fake.FakeProvider` that always answers with one
    pre-chosen outcome, regardless of the underlying request's `options`
    ordering.

    Subclasses bundle 1's fake provider rather than replacing it, so this
    fixture stays bound to the same shared contract (`ProviderAnswer`,
    `dispatch(request, *, timeout_s=None)`, zero network calls in every
    scenario) that bundle 1's own tests rely on -- it only overrides
    *which* answer comes back. It also records the last request it was
    handed so a test can prove what a provider is (and is not) shown.
    """

    name = "fake"

    def __init__(self, answer: str) -> None:
        super().__init__(scenario="ok")
        self._answer = answer
        self.last_request: dict | None = None

    def dispatch(self, request: dict, *, timeout_s: float | None = None) -> object:
        self.call_count += 1
        self.last_timeout_s = timeout_s
        self.last_request = request
        return provider_base.ProviderAnswer(answer=self._answer, confidence=0.9, cost=0.0001)


def base_request(**overrides) -> dict:
    request = {
        "schema_version": 1,
        "milestone_description": "Finished implementing the login endpoint's unit tests.",
        "session_state": {},
        "caller_message": "",
    }
    request.update(overrides)
    return request
