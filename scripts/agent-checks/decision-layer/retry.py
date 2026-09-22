#!/usr/bin/env python3
"""Bounded retry with a single-in-flight guard (build item 7).

This module deliberately runs no threads. The *transport* owns the timeout:
a live provider runs as a child process that the caller kills at the
deadline (see provider_jev.py), and the fake provider reports a simulated
timeout instead of sleeping. So when an attempt raises ProviderTimeout the
request is already gone, and the next attempt can never overlap it.

`in_flight` is a lock owned by the provider. It is acquired non-blocking:
a second caller arriving while a call is running gets ProviderBusy at once
instead of launching a duplicate live request.

Only timeout and unavailable are retried. Malformed output, missing
configuration, busy and unsupported-request are contract states, not
transient faults, so they propagate immediately.
"""

from __future__ import annotations

import threading
from typing import Callable, TypeVar

import provider_base

T = TypeVar("T")

RETRYABLE_ERRORS = (provider_base.ProviderTimeout, provider_base.ProviderUnavailable)


def call_with_retry(
    attempt: Callable[[float], T],
    *,
    timeout_s: float,
    max_retries: int,
    in_flight: threading.Lock | None = None,
) -> T:
    """Run `attempt(timeout_s)` up to `max_retries + 1` times, sequentially.

    Attempts never overlap: each one must have returned or raised before
    the next starts, and `in_flight` (when given) rejects concurrent callers.
    """
    if max_retries < 0:
        raise ValueError("max_retries must be >= 0")
    if in_flight is not None and not in_flight.acquire(blocking=False):
        raise provider_base.ProviderBusy("a call to this provider is still in flight")
    try:
        last_error: BaseException | None = None
        for _ in range(max_retries + 1):
            try:
                return attempt(timeout_s)
            except RETRYABLE_ERRORS as exc:
                last_error = exc
        assert last_error is not None
        raise last_error
    finally:
        if in_flight is not None:
            in_flight.release()
