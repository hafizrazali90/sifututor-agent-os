#!/usr/bin/env python3
"""A fully scriptable, offline, deterministic provider (build item 4).

This is the only provider this bundle's own test suite actually dispatches
to. It makes zero network calls in every scenario, including "unavailable"
and "hang" -- the hang scenario blocks the calling thread with a plain
`time.sleep`, so the engine's timeout/retry wrapper is what bounds it, not
this module.
"""

from __future__ import annotations

import time

import provider_base


class FakeProvider:
    """Deterministic stand-in for a real decision provider.

    Scenarios:
        ok             -> a well-formed, high-confidence ProviderAnswer.
        low_confidence -> a well-formed ProviderAnswer below a typical
                           confidence threshold.
        malformed      -> something that is not a ProviderAnswer at all,
                           to prove the engine rejects bad shape.
        unavailable    -> raises ProviderUnavailable immediately.
        hang           -> sleeps for `hang_seconds` before answering, to
                           exercise bounded timeout/retry.
    """

    name = "fake"

    def __init__(self, scenario: str = "ok", hang_seconds: float = 2.0) -> None:
        self.scenario = scenario
        self.hang_seconds = hang_seconds
        self.call_count = 0

    def dispatch(self, request: dict) -> object:
        self.call_count += 1
        options = request.get("options") or ["ok"]

        if self.scenario == "ok":
            return provider_base.ProviderAnswer(answer=options[0], confidence=0.92, cost=0.0002)

        if self.scenario == "low_confidence":
            return provider_base.ProviderAnswer(answer=options[0], confidence=0.2, cost=0.0002)

        if self.scenario == "malformed":
            # Deliberately not a ProviderAnswer -- the engine must reject
            # this shape rather than pass it through.
            return {"answer": options[0], "confidence": "not-a-number"}

        if self.scenario == "unavailable":
            raise provider_base.ProviderUnavailable("fake provider reports itself unavailable")

        if self.scenario == "hang":
            time.sleep(self.hang_seconds)
            return provider_base.ProviderAnswer(answer=options[0], confidence=0.92, cost=0.0002)

        raise ValueError(f"FakeProvider: unscripted scenario {self.scenario!r}")
