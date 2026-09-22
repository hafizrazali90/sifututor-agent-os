#!/usr/bin/env python3
"""Structurally real adapter for TypeSafe AI's Jev typed-decision product
(build item 5).

There is no live access to Jev yet: it is waitlist-gated, and Mission
Ledger JEV-EVAL-001 (docs/agent-playbooks/mission-ledger/cross-project.md)
is explicitly paused pending calibration verification against real
Sifututor data. This module is shaped like a real future SDK integration
-- request payload, auth header, HTTP call, response parsing -- but every
path that would touch the network is gated behind a configuration check
that runs first. When the required `jev_api_key` is absent, `dispatch`
raises ProviderNotConfigured immediately and `_call_live` is never
reached, so `network_call_count` stays at 0.

No test in this bundle sets a real Jev API key, so no test in this bundle
can reach `_call_live` or the network.
"""

from __future__ import annotations

import json
import urllib.request

import provider_base


class JevProvider:
    """Adapter shaped like a real Jev SDK call, gated on configuration."""

    name = "jev"

    def __init__(self, config: dict | None = None) -> None:
        config = config or {}
        self.api_key = config.get("jev_api_key") or None
        self.base_url = config.get("jev_base_url") or "https://api.typesafe.ai/v1"
        self.timeout_s = float(config.get("jev_http_timeout_s") or 5.0)
        self.network_call_count = 0

    def dispatch(self, request: dict) -> provider_base.ProviderAnswer:
        if not self.api_key:
            raise provider_base.ProviderNotConfigured(
                "Jev provider is not configured: set jev_api_key (or the "
                "JEV_API_KEY environment variable) before dispatching to Jev."
            )
        return self._call_live(request)

    def _build_payload(self, request: dict) -> dict:
        payload: dict = {
            "decision_type": request.get("decision_type"),
            "context": request.get("context", ""),
            "sensitivity": request.get("sensitivity", "low"),
        }
        if request.get("options") is not None:
            payload["options"] = request["options"]
        if request.get("scale") is not None:
            payload["scale"] = request["scale"]
        return payload

    def _call_live(self, request: dict) -> provider_base.ProviderAnswer:
        # Reached only after the configured check above passes. No test in
        # this bundle ever supplies a real jev_api_key, so this method is
        # dead code under test -- see the "not configured" proof in
        # test_provider_jev.py.
        self.network_call_count += 1
        body = json.dumps(self._build_payload(request)).encode("utf-8")
        http_request = urllib.request.Request(
            f"{self.base_url}/decide",
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(http_request, timeout=self.timeout_s) as response:
                parsed = json.loads(response.read())
        except Exception as exc:  # noqa: BLE001 - any transport failure is "unavailable"
            raise provider_base.ProviderUnavailable(f"Jev request failed: {exc}") from exc

        if not isinstance(parsed, dict) or "answer" not in parsed or "confidence" not in parsed:
            raise provider_base.ProviderMalformedOutput("Jev response missing answer/confidence")

        return provider_base.ProviderAnswer(
            answer=parsed["answer"],
            confidence=parsed["confidence"],
            cost=parsed.get("cost", 0.0),
        )
