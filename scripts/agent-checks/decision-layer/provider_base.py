#!/usr/bin/env python3
"""Shared provider contract: the answer shape and error taxonomy every
decision-layer provider (fake or real) must use.

Every error carries a short machine-readable `code`. The engine logs only
that code, never the exception message, so a provider can never leak a
response body, stack trace or credential fragment into a diagnostic record.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProviderAnswer:
    """A well-formed provider result. Anything else is malformed output."""

    answer: Any
    confidence: float
    cost: float = 0.0
    usage_input_tokens: int | None = None
    usage_output_tokens: int | None = None


class ProviderError(Exception):
    """Base class for every provider failure the engine knows how to handle."""

    code = "provider_error"

    def __init__(self, message: str = "", *, code: str | None = None) -> None:
        super().__init__(message)
        if code:
            self.code = code


class ProviderUnavailable(ProviderError):
    """The provider could not answer (down, network failure, server error)."""

    code = "provider_unavailable"


class ProviderTimeout(ProviderError):
    """The transport gave up waiting and the request was genuinely aborted."""

    code = "provider_timeout"


class ProviderBusy(ProviderError):
    """Another call to the same provider is still in flight; never duplicate it."""

    code = "provider_busy"


class ProviderMalformedOutput(ProviderError):
    """The provider returned something that does not match ProviderAnswer."""

    code = "malformed_provider_output"


class ProviderNotConfigured(ProviderError):
    """A required configuration value (e.g. an API key) is absent."""

    code = "provider_not_configured"


class ProviderUnsupportedRequest(ProviderError):
    """The request is valid for the schema but this provider cannot express it."""

    code = "unsupported_request"


def normalize_provider_answer(raw: object) -> ProviderAnswer:
    """Validate structural provider output and return this module's type.

    Providers and test adapters may load this contract under an independent
    Python module identity. The fields, rather than one in-memory class object,
    define the boundary. Every value remains untrusted and is validated here.
    """
    try:
        answer = raw.answer
        confidence = raw.confidence
        cost = raw.cost
        usage_input_tokens = raw.usage_input_tokens
        usage_output_tokens = raw.usage_output_tokens
    except (AttributeError, TypeError):
        raise ProviderMalformedOutput(code="not_a_provider_answer") from None
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        raise ProviderMalformedOutput(code="confidence_not_numeric")
    if not 0.0 <= confidence <= 1.0:
        raise ProviderMalformedOutput(code="confidence_out_of_range")
    if answer is None or (isinstance(answer, str) and not answer.strip()):
        raise ProviderMalformedOutput(code="answer_empty")
    if isinstance(cost, bool) or not isinstance(cost, (int, float)) or cost < 0:
        raise ProviderMalformedOutput(code="cost_invalid")
    for value in (usage_input_tokens, usage_output_tokens):
        if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 0):
            raise ProviderMalformedOutput(code="usage_invalid")
    return ProviderAnswer(
        answer=answer,
        confidence=float(confidence),
        cost=float(cost),
        usage_input_tokens=usage_input_tokens,
        usage_output_tokens=usage_output_tokens,
    )
