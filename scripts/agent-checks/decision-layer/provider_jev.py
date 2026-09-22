#!/usr/bin/env python3
"""Jev provider: TypeSafe's System One via the official @typesafe-ai/sdk.

The SDK is JavaScript, so the call runs in a small Node sidecar
(jev-sidecar/sidecar.mjs). This module owns everything that is policy:

* mapping a decision-layer request onto one typed System One question
  (`build_system_one_payload`) and validating the typed answer strictly
  (`parse_system_one_result`) -- both pure functions with contract tests;
* the configuration gate: no TYPESAFE_API_KEY in the provider's environment
  means ProviderNotConfigured and the sidecar is never started;
* the timeout: the sidecar is a child process killed at the deadline, so a
  timed-out request is genuinely gone before any retry can start;
* single in-flight: `in_flight` is handed to retry.call_with_retry so two
  callers can never have two live requests running.

Nothing here reads the key's value for any purpose other than passing the
environment variable through to the child, and no exception carries a
message that came from the network.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import threading
from typing import Callable, Mapping

import provider_base

HERE = Path(__file__).resolve().parent
SIDECAR_DIR = HERE / "jev-sidecar"
SIDECAR = SIDECAR_DIR / "sidecar.mjs"
SDK_INSTALL_MARKER = SIDECAR_DIR / "node_modules" / "@typesafe-ai" / "sdk" / "package.json"

API_KEY_ENV = "TYPESAFE_API_KEY"
PROTOCOL_VERSION = 1
QUESTION_NAME = "answer"
# `score` criteria are descriptions indexed from zero; keep the rubric small.
MAX_SCORE_LEVELS = 11
# Extra time for the child to flush its own timeout label before we kill it.
KILL_GRACE_S = 1.0

_ERROR_KIND_TO_EXCEPTION: dict[str, type[provider_base.ProviderError]] = {
    "timeout": provider_base.ProviderTimeout,
    "abort": provider_base.ProviderTimeout,
    "connection": provider_base.ProviderUnavailable,
    "api_status": provider_base.ProviderUnavailable,
    "api_rate_limit": provider_base.ProviderUnavailable,
    "unknown": provider_base.ProviderUnavailable,
    "api_auth": provider_base.ProviderNotConfigured,
    "config": provider_base.ProviderNotConfigured,
    "config_missing_key": provider_base.ProviderNotConfigured,
    "invalid_input": provider_base.ProviderMalformedOutput,
}

Runner = Callable[[list[str], dict, Mapping[str, str], float], dict]


def build_system_one_payload(
    request: dict, *, base_url: str | None, model: str | None, timeout_ms: int
) -> dict:
    """Map one decision-layer request onto the sidecar protocol.

    options -> one `choice` question whose criteria are the option labels.
    scale   -> one `score` question whose rubric is the integer levels
               min..max (descriptions indexed from zero, per the SDK).
    `state` is exactly the request's `context`; callers are responsible for
    minimising it (the engine has already run the secret filter).
    """
    decision_type = request["decision_type"]
    options = request.get("options")
    scale = request.get("scale")

    if options:
        question = {
            "type": "choice",
            "instructions": f"Decision type: {decision_type}. Select the single best option.",
            "criteria": {str(option): None for option in options},
        }
    else:
        low, high = scale["min"], scale["max"]
        if not (float(low).is_integer() and float(high).is_integer()):
            raise provider_base.ProviderUnsupportedRequest(code="scale_bounds_not_integer")
        low, high = int(low), int(high)
        levels = high - low + 1
        if levels < 2 or levels > MAX_SCORE_LEVELS:
            raise provider_base.ProviderUnsupportedRequest(code="scale_levels_out_of_range")
        question = {
            "type": "score",
            "instructions": f"Decision type: {decision_type}. Score from {low} to {high}.",
            "criteria": [f"level {n}" for n in range(low, high + 1)],
        }

    payload: dict = {
        "schema_version": PROTOCOL_VERSION,
        "timeout_ms": int(timeout_ms),
        "state": str(request.get("context") or ""),
        "questions": {QUESTION_NAME: question},
    }
    if base_url:
        payload["base_url"] = base_url
    if model:
        payload["model"] = model
    return payload


def _as_confidence(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise provider_base.ProviderMalformedOutput(code="confidence_not_numeric")
    if not 0.0 <= float(value) <= 1.0:
        raise provider_base.ProviderMalformedOutput(code="confidence_out_of_range")
    return float(value)


def _as_token_count(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise provider_base.ProviderMalformedOutput(code="usage_not_integer")
    return value


def parse_system_one_result(sidecar_output: object, request: dict) -> provider_base.ProviderAnswer:
    """Validate the sidecar's output strictly against the request that made it."""
    if not isinstance(sidecar_output, dict) or sidecar_output.get("schema_version") != PROTOCOL_VERSION:
        raise provider_base.ProviderMalformedOutput(code="sidecar_protocol_mismatch")

    if sidecar_output.get("ok") is not True:
        kind = sidecar_output.get("error_kind")
        exception = _ERROR_KIND_TO_EXCEPTION.get(kind if isinstance(kind, str) else "unknown")
        if exception is None:
            exception = provider_base.ProviderUnavailable
        raise exception(code=f"jev_{kind}" if isinstance(kind, str) else "jev_unknown")

    result = sidecar_output.get("result")
    if not isinstance(result, dict):
        raise provider_base.ProviderMalformedOutput(code="result_not_object")
    answers = result.get("answers")
    if not isinstance(answers, dict) or not isinstance(answers.get(QUESTION_NAME), dict):
        raise provider_base.ProviderMalformedOutput(code="answer_missing")
    answer = answers[QUESTION_NAME]

    usage = result.get("usage") if isinstance(result.get("usage"), dict) else {}
    usage_in = _as_token_count(usage.get("input_tokens"))
    usage_out = _as_token_count(usage.get("output_tokens"))

    options = request.get("options")
    if options:
        if answer.get("type") != "choice":
            raise provider_base.ProviderMalformedOutput(code="answer_type_mismatch")
        choice = answer.get("choice")
        if not isinstance(choice, str) or choice not in {str(option) for option in options}:
            raise provider_base.ProviderMalformedOutput(code="choice_not_in_options")
        return provider_base.ProviderAnswer(
            answer=choice,
            confidence=_as_confidence(answer.get("confidence")),
            usage_input_tokens=usage_in,
            usage_output_tokens=usage_out,
        )

    if answer.get("type") != "score":
        raise provider_base.ProviderMalformedOutput(code="answer_type_mismatch")
    score = answer.get("score")
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise provider_base.ProviderMalformedOutput(code="score_not_numeric")
    scale = request["scale"]
    levels = int(scale["max"]) - int(scale["min"]) + 1
    if not 0.0 <= float(score) <= levels - 1:
        raise provider_base.ProviderMalformedOutput(code="score_out_of_range")
    return provider_base.ProviderAnswer(
        answer=int(scale["min"]) + float(score),
        confidence=_as_confidence(answer.get("confidence")),
        usage_input_tokens=usage_in,
        usage_output_tokens=usage_out,
    )


def run_sidecar(argv: list[str], payload: dict, env: Mapping[str, str], timeout_s: float) -> dict:
    """Run the sidecar once. A deadline kills the child; nothing survives it."""
    try:
        completed = subprocess.run(
            argv,
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            env=dict(env),
            timeout=timeout_s + KILL_GRACE_S,
            check=False,
        )
    except subprocess.TimeoutExpired:
        # subprocess.run has already killed the child and reaped it.
        raise provider_base.ProviderTimeout(code="sidecar_killed_at_deadline") from None
    except OSError:
        raise provider_base.ProviderNotConfigured(code="sidecar_launch_failed") from None
    if completed.returncode != 0:
        raise provider_base.ProviderUnavailable(code="sidecar_crashed")
    try:
        return json.loads(completed.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        raise provider_base.ProviderMalformedOutput(code="sidecar_output_not_json") from None


class JevProvider:
    """Adapter over the official SDK, gated on TYPESAFE_API_KEY presence."""

    name = "jev"

    def __init__(
        self,
        config: dict | None = None,
        *,
        env: Mapping[str, str] | None = None,
        runner: Runner | None = None,
        node_executable: str | None = None,
    ) -> None:
        config = config or {}
        self.base_url = config.get("jev_base_url") or None
        self.model = config.get("jev_model") or None
        self.env: Mapping[str, str] = os.environ if env is None else env
        self.runner: Runner = runner or run_sidecar
        self.node = node_executable or shutil.which("node")
        self.network_call_count = 0
        self.in_flight = threading.Lock()

    def is_configured(self) -> bool:
        return bool(self.env.get(API_KEY_ENV))

    def dependencies_available(self) -> bool:
        return bool(self.node) and SIDECAR.is_file() and SDK_INSTALL_MARKER.is_file()

    def dispatch(self, request: dict, *, timeout_s: float | None = None) -> provider_base.ProviderAnswer:
        if not self.is_configured():
            raise provider_base.ProviderNotConfigured(
                f"set {API_KEY_ENV} before dispatching to Jev", code="typesafe_api_key_missing"
            )
        if not self.dependencies_available():
            raise provider_base.ProviderNotConfigured(code="sidecar_dependencies_missing")

        effective_timeout = float(timeout_s if timeout_s is not None else 5.0)
        payload = build_system_one_payload(
            request, base_url=self.base_url, model=self.model, timeout_ms=int(effective_timeout * 1000)
        )
        child_env = {"PATH": os.environ.get("PATH", ""), API_KEY_ENV: self.env[API_KEY_ENV]}

        self.network_call_count += 1
        output = self.runner([str(self.node), str(SIDECAR)], payload, child_env, effective_timeout)
        return parse_system_one_result(output, request)
