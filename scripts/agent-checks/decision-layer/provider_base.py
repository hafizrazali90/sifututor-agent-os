#!/usr/bin/env python3
"""Shared provider contract: the answer shape and error taxonomy every
decision-layer provider (fake or real) must use.

Keeping this in one small module means the engine can validate any
provider's output against one shape, regardless of which provider ran.
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


class ProviderError(Exception):
    """Base class for every provider failure the engine knows how to handle."""


class ProviderUnavailable(ProviderError):
    """The provider reported itself unavailable (no network attempt needed)."""


class ProviderMalformedOutput(ProviderError):
    """The provider returned something that does not match ProviderAnswer."""


class ProviderNotConfigured(ProviderError):
    """A required configuration value (e.g. an API key) is absent."""
