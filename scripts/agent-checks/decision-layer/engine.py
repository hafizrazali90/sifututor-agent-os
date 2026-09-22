#!/usr/bin/env python3
"""Decision-layer engine: wires the pieces from every build item together.

Pipeline, in order, for every call to `decide`:

1. Validate the request against the versioned schema. A bad request raises
   before anything else runs.
2. Deterministic pre-dispatch content filter. Secret- or PII-shaped content
   blocks immediately; no provider, not even the fake one, sees it.
3. Deterministic pre-policy layer. A matching rule answers and no provider
   is dispatched to, even for an opted-in authoritative decision type.
4. Otherwise dispatch to the configured provider through the sequential
   retry layer with the provider's own single-in-flight lock.
5. Confidence/fallback policy: any provider error, timeout, busy signal,
   bad output shape or low-confidence answer falls back to a safe default.
6. Shadow/advisory stamping: `authoritative` is only ever True for a clean
   "ok" outcome on a decision type in the config's opt-in allowlist, which
   is empty by default.

Every `reason` is a short code, never an exception message: a provider
cannot leak a response body or credential fragment into a response or a
diagnostic record through this module.
"""

from __future__ import annotations

import threading
import time

import config as config_module
import pre_policy
import provider_base
import provider_fake
import provider_jev
import retry
import schema
import secret_filter

FALLBACK_ANSWER = "undetermined"

# One lock per live provider for the whole process, so engine-built
# providers share the in-flight guard even when `decide` builds a fresh
# adapter object per call.
_JEV_IN_FLIGHT = threading.Lock()


def _build_provider(config: dict):
    provider_name = config.get("provider", "fake")
    if provider_name == "fake":
        return provider_fake.FakeProvider()
    if provider_name == "jev":
        provider = provider_jev.JevProvider(config=config)
        provider.in_flight = _JEV_IN_FLIGHT
        return provider
    raise ValueError(f"unknown provider {provider_name!r}")


def _is_authoritative(decision_type: str, config: dict, outcome: str) -> bool:
    if outcome != "ok":
        return False
    return decision_type in (config.get("authoritative_decision_types") or [])


def _finish(
    *,
    decision_type: str,
    answer: object,
    confidence: float,
    provider_name: str,
    fallback_used: bool,
    outcome: str,
    reason: str,
    cost: float,
    started: float,
    config: dict,
    usage_input_tokens: int | None = None,
    usage_output_tokens: int | None = None,
) -> dict:
    authoritative = False if fallback_used else _is_authoritative(decision_type, config, outcome)
    return {
        "schema_version": schema.SCHEMA_VERSION,
        "decision_type": decision_type,
        "answer": answer,
        "confidence": confidence,
        "provider": provider_name,
        "fallback_used": fallback_used,
        "authoritative": authoritative,
        "latency_ms": (time.monotonic() - started) * 1000.0,
        "cost": cost,
        "usage_input_tokens": usage_input_tokens,
        "usage_output_tokens": usage_output_tokens,
        "outcome": outcome,
        "reason": reason,
    }


def _validate_provider_answer(raw: object) -> provider_base.ProviderAnswer:
    """Validate and normalize the documented provider-answer contract.

    Test discovery and adapter loading may import provider_base.py under more
    than one module identity. Requiring one exact class object rejects a valid
    answer even when every contract field is present. Treat provider output as
    untrusted structural data, validate every field below, and copy it into the
    engine's canonical ProviderAnswer type.
    """
    return provider_base.normalize_provider_answer(raw)


def decide(request: dict, config: dict | None = None, provider: object | None = None) -> dict:
    """Return a fully-formed decision-layer response for one request."""
    started = time.monotonic()
    config = dict(config_module.DEFAULT_CONFIG) if config is None else config

    errors = schema.validate_request(request)
    if errors:
        raise schema.RequestValidationError(errors)

    decision_type = request["decision_type"]

    def fallback(*, provider_name: str, outcome: str, reason: str, confidence: float = 0.0, cost: float = 0.0) -> dict:
        return _finish(
            decision_type=decision_type,
            answer=FALLBACK_ANSWER,
            confidence=confidence,
            provider_name=provider_name,
            fallback_used=True,
            outcome=outcome,
            reason=reason,
            cost=cost,
            started=started,
            config=config,
        )

    if secret_filter.scan_request(request):
        return fallback(
            provider_name="deterministic_fallback",
            outcome="blocked",
            reason="secret_or_pii_shaped_content_detected",
        )

    policy_result = pre_policy.evaluate(request)
    if policy_result is not None:
        return _finish(
            decision_type=decision_type,
            answer=policy_result.answer,
            confidence=policy_result.confidence,
            provider_name="pre_policy",
            fallback_used=False,
            outcome="ok",
            reason=policy_result.reason,
            cost=0.0,
            started=started,
            config=config,
        )

    active_provider = provider if provider is not None else _build_provider(config)
    provider_name = getattr(active_provider, "name", "unknown")

    try:
        raw = retry.call_with_retry(
            lambda timeout_s: active_provider.dispatch(request, timeout_s=timeout_s),
            timeout_s=config["timeout_s"],
            max_retries=config["max_retries"],
            in_flight=getattr(active_provider, "in_flight", None),
        )
    except provider_base.ProviderNotConfigured as exc:
        return fallback(provider_name=provider_name, outcome="not_configured", reason=exc.code)
    except provider_base.ProviderError as exc:
        # Timeout, unavailable, busy, unsupported, malformed: all fall back
        # and none of their messages are surfaced, only the code.
        return fallback(provider_name=provider_name, outcome="fallback", reason=exc.code)

    try:
        answer = _validate_provider_answer(raw)
    except provider_base.ProviderMalformedOutput as exc:
        return fallback(provider_name=provider_name, outcome="fallback", reason=exc.code)

    if answer.confidence < config["confidence_threshold"]:
        return fallback(
            provider_name=provider_name,
            outcome="fallback",
            reason="confidence_below_threshold",
            confidence=answer.confidence,
            cost=answer.cost,
        )

    return _finish(
        decision_type=decision_type,
        answer=answer.answer,
        confidence=answer.confidence,
        provider_name=provider_name,
        fallback_used=False,
        outcome="ok",
        reason="provider_answer",
        cost=answer.cost,
        started=started,
        config=config,
        usage_input_tokens=answer.usage_input_tokens,
        usage_output_tokens=answer.usage_output_tokens,
    )
