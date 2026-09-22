#!/usr/bin/env python3
"""Decision-layer engine: wires the pieces from every build item together.

Pipeline, in order, for every call to `decide`:

1. Validate the request against the versioned schema (item 1). A bad
   request raises before anything else runs.
2. Deterministic pre-dispatch content filter (item 8). If the request
   contains anything secret- or PII-shaped, block immediately and never
   call any provider, including the fake one.
3. Deterministic pre-policy layer (item 3). If a rule matches this
   decision type, its answer is used and no provider is ever dispatched
   to -- this holds even when the decision type is opted into the
   authoritative allowlist.
4. Otherwise, dispatch to the configured provider, wrapped in the bounded
   timeout/retry/cancellation layer (item 7).
5. Confidence/fallback policy (item 6): any provider error, timeout, bad
   output shape, or low confidence answer falls back to a safe default
   instead of passing the provider's raw answer through.
6. Shadow/advisory stamping (item 10): the response is only ever marked
   `authoritative` when the outcome is a clean "ok" AND the decision type
   is in the config's opt-in allowlist. The default allowlist is empty.
7. The caller can turn the response into a metadata-only observability
   record with `observability.build_record` (item 9); this module never
   does that logging itself, so it stays a pure function with no side
   effects of its own.
"""

from __future__ import annotations

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


def _build_provider(config: dict):
    provider_name = config.get("provider", "fake")
    if provider_name == "fake":
        return provider_fake.FakeProvider()
    if provider_name == "jev":
        return provider_jev.JevProvider(config=config)
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
        "outcome": outcome,
        "reason": reason,
    }


def _validate_provider_answer(raw: object) -> provider_base.ProviderAnswer:
    if not isinstance(raw, provider_base.ProviderAnswer):
        raise provider_base.ProviderMalformedOutput("provider did not return a ProviderAnswer")
    if isinstance(raw.confidence, bool) or not isinstance(raw.confidence, (int, float)):
        raise provider_base.ProviderMalformedOutput("confidence is not a number")
    if not (0.0 <= raw.confidence <= 1.0):
        raise provider_base.ProviderMalformedOutput("confidence out of range")
    if raw.answer is None or (isinstance(raw.answer, str) and not raw.answer.strip()):
        raise provider_base.ProviderMalformedOutput("answer is empty")
    return raw


def decide(request: dict, config: dict | None = None, provider: object | None = None) -> dict:
    """Return a fully-formed decision-layer response for one request."""
    started = time.monotonic()
    config = dict(config_module.DEFAULT_CONFIG) if config is None else config

    errors = schema.validate_request(request)
    if errors:
        raise schema.RequestValidationError(errors)

    decision_type = request["decision_type"]

    # Step 2: block before any provider ever sees the content.
    if secret_filter.scan_request(request):
        return _finish(
            decision_type=decision_type,
            answer=FALLBACK_ANSWER,
            confidence=0.0,
            provider_name="deterministic_fallback",
            fallback_used=True,
            outcome="blocked",
            reason="secret_or_pii_shaped_content_detected",
            cost=0.0,
            started=started,
            config=config,
        )

    # Step 3: the deterministic pre-policy layer always wins, and never
    # touches a provider.
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

    # Step 4 + 5: dispatch with bounded timeout/retry, then apply the
    # confidence/fallback policy.
    try:
        raw = retry.call_with_retry(
            lambda: active_provider.dispatch(request),
            timeout_s=config["timeout_s"],
            max_retries=config["max_retries"],
        )
    except provider_base.ProviderNotConfigured as exc:
        return _finish(
            decision_type=decision_type,
            answer=FALLBACK_ANSWER,
            confidence=0.0,
            provider_name=getattr(active_provider, "name", "unknown"),
            fallback_used=True,
            outcome="not_configured",
            reason=str(exc),
            cost=0.0,
            started=started,
            config=config,
        )
    except provider_base.ProviderUnavailable as exc:
        return _finish(
            decision_type=decision_type,
            answer=FALLBACK_ANSWER,
            confidence=0.0,
            provider_name=getattr(active_provider, "name", "unknown"),
            fallback_used=True,
            outcome="fallback",
            reason=f"provider_unavailable: {exc}",
            cost=0.0,
            started=started,
            config=config,
        )
    except TimeoutError as exc:
        return _finish(
            decision_type=decision_type,
            answer=FALLBACK_ANSWER,
            confidence=0.0,
            provider_name=getattr(active_provider, "name", "unknown"),
            fallback_used=True,
            outcome="fallback",
            reason=f"provider_timeout: {exc}",
            cost=0.0,
            started=started,
            config=config,
        )

    try:
        answer = _validate_provider_answer(raw)
    except provider_base.ProviderMalformedOutput as exc:
        return _finish(
            decision_type=decision_type,
            answer=FALLBACK_ANSWER,
            confidence=0.0,
            provider_name=getattr(active_provider, "name", "unknown"),
            fallback_used=True,
            outcome="fallback",
            reason=f"malformed_provider_output: {exc}",
            cost=0.0,
            started=started,
            config=config,
        )

    if answer.confidence < config["confidence_threshold"]:
        return _finish(
            decision_type=decision_type,
            answer=FALLBACK_ANSWER,
            confidence=answer.confidence,
            provider_name=getattr(active_provider, "name", "unknown"),
            fallback_used=True,
            outcome="fallback",
            reason="confidence_below_threshold",
            cost=answer.cost,
            started=started,
            config=config,
        )

    return _finish(
        decision_type=decision_type,
        answer=answer.answer,
        confidence=answer.confidence,
        provider_name=getattr(active_provider, "name", "unknown"),
        fallback_used=False,
        outcome="ok",
        reason="provider_answer",
        cost=answer.cost,
        started=started,
        config=config,
    )
