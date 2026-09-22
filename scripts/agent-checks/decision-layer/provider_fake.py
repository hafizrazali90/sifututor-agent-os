#!/usr/bin/env python3
"""A fully scriptable, offline, deterministic provider (build item 4).

This is the only provider the decision layer's own test suite dispatches to.
It makes zero network calls in every scenario. "hang" does not sleep: it
reports the same ProviderTimeout a killed live transport would, so tests
prove the retry/fallback path without real waiting or background threads.
"""

from __future__ import annotations

import threading

import provider_base


class FakeProvider:
    """Deterministic stand-in for a real decision provider.

    Scenarios:
        ok             -> a well-formed, high-confidence ProviderAnswer.
        low_confidence -> a well-formed ProviderAnswer below a typical threshold.
        malformed      -> not a ProviderAnswer at all (engine must reject it).
        unavailable    -> raises ProviderUnavailable immediately.
        hang           -> raises ProviderTimeout immediately (simulated abort).
        block          -> waits on `release` (test-controlled) before answering,
                          so a test can hold a call in flight deterministically.
    """

    name = "fake"

    def __init__(self, scenario: str = "ok", hang_seconds: float = 0.0) -> None:
        self.scenario = scenario
        self.hang_seconds = hang_seconds  # kept for call-site compatibility; never slept
        self.call_count = 0
        self.in_flight = threading.Lock()
        self.started = threading.Event()
        self.release = threading.Event()
        self.last_timeout_s: float | None = None

    def dispatch(self, request: dict, *, timeout_s: float | None = None) -> object:
        self.call_count += 1
        self.last_timeout_s = timeout_s
        options = request.get("options") or ["ok"]

        if self.scenario == "ok":
            return provider_base.ProviderAnswer(answer=options[0], confidence=0.92, cost=0.0002)

        if self.scenario == "low_confidence":
            return provider_base.ProviderAnswer(answer=options[0], confidence=0.2, cost=0.0002)

        if self.scenario == "malformed":
            return {"answer": options[0], "confidence": "not-a-number"}

        if self.scenario == "unavailable":
            raise provider_base.ProviderUnavailable("fake provider reports itself unavailable")

        if self.scenario == "hang":
            raise provider_base.ProviderTimeout("fake transport aborted at the deadline")

        if self.scenario == "block":
            self.started.set()
            self.release.wait()
            return provider_base.ProviderAnswer(answer=options[0], confidence=0.92, cost=0.0002)

        raise ValueError(f"FakeProvider: unscripted scenario {self.scenario!r}")
