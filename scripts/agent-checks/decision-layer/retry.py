#!/usr/bin/env python3
"""Bounded timeout, retry, and cancellation around a provider call
(build item 7).

Python cannot forcibly kill a running thread, so "cancellation" here is the
standard best-effort form: the calling code stops waiting at the timeout
and never blocks process exit on the abandoned call, because the worker
thread is always a daemon thread. Retries apply only to the two failure
modes that are plausibly transient (timeout, provider-reported
unavailable); a malformed-output or not-configured error is a contract
violation, not a transient fault, so it is never retried.
"""

from __future__ import annotations

import queue
import threading
from typing import Callable, TypeVar

import provider_base

T = TypeVar("T")

_RETRYABLE_PROVIDER_ERRORS = (provider_base.ProviderUnavailable,)


def _call_with_timeout(fn: Callable[[], T], timeout_s: float) -> T:
    result_queue: "queue.Queue[tuple[str, object]]" = queue.Queue(maxsize=1)

    def worker() -> None:
        try:
            result_queue.put(("ok", fn()))
        except BaseException as exc:  # noqa: BLE001 - re-raised on the caller's thread
            result_queue.put(("error", exc))

    # daemon=True: a hung call keeps sleeping in the background but never
    # blocks the interpreter (or a test runner) from exiting.
    worker_thread = threading.Thread(target=worker, name="decision-layer-retry-worker", daemon=True)
    worker_thread.start()

    try:
        status, payload = result_queue.get(timeout=timeout_s)
    except queue.Empty:
        raise TimeoutError("provider call timed out") from None

    if status == "error":
        raise payload  # type: ignore[misc]
    return payload  # type: ignore[return-value]


def call_with_retry(fn: Callable[[], T], *, timeout_s: float, max_retries: int) -> T:
    """Call `fn` with a bounded timeout, retrying transient failures.

    Retries at most `max_retries` times (so `max_retries + 1` attempts
    total) on TimeoutError or ProviderUnavailable. Any other exception
    (e.g. ProviderMalformedOutput, ProviderNotConfigured) propagates
    immediately without a retry.
    """
    last_error: BaseException | None = None
    for _attempt in range(max_retries + 1):
        try:
            return _call_with_timeout(fn, timeout_s)
        except TimeoutError as exc:
            last_error = exc
            continue
        except _RETRYABLE_PROVIDER_ERRORS as exc:
            last_error = exc
            continue
    assert last_error is not None
    raise last_error
