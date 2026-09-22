#!/usr/bin/env python3
"""Decision-layer configuration and the shadow/advisory default
(build item 10).

Out of the box, `authoritative_decision_types` is empty, so no decision
type can produce an "authoritative" response -- the layer's output is
informational only until Hafiz explicitly opts a specific decision type
in. The deterministic pre-policy layer (`pre_policy.py`) always overrides
regardless of this setting; opting a decision type in only changes
whether a *provider's* own answer may be treated as authoritative.
"""

from __future__ import annotations

import os

DEFAULT_CONFIG: dict[str, object] = {
    # Which provider the engine dispatches to when the pre-policy layer
    # does not already have an answer. "fake" is the only provider this
    # bundle's own tests ever actually dispatch to.
    "provider": "fake",
    # Below this confidence, the engine falls back instead of trusting
    # the provider's answer.
    "confidence_threshold": 0.55,
    # Bounded timeout/retry around a single provider call.
    "timeout_s": 0.2,
    "max_retries": 1,
    # Shadow/advisory opt-in list. Empty by default (build item 10).
    "authoritative_decision_types": [],
    # Jev adapter configuration. Absent by default -- see provider_jev.py
    # for the "not configured" behavior this triggers.
    "jev_api_key": None,
    "jev_base_url": "https://api.typesafe.ai/v1",
}


def load_config(
    overrides: dict[str, object] | None = None,
    env: dict[str, str] | None = None,
) -> dict[str, object]:
    """Build an effective config from defaults, an env mapping, then overrides.

    `env` defaults to the real process environment for normal CLI use, but
    tests should always pass an explicit `env` dict (even `{}`) so config
    loading stays deterministic and never depends on ambient state.
    """
    resolved_env = os.environ if env is None else env

    config = dict(DEFAULT_CONFIG)

    jev_api_key = resolved_env.get("JEV_API_KEY")
    if jev_api_key:
        config["jev_api_key"] = jev_api_key

    jev_base_url = resolved_env.get("JEV_BASE_URL")
    if jev_base_url:
        config["jev_base_url"] = jev_base_url

    if overrides:
        config.update(overrides)

    return config
