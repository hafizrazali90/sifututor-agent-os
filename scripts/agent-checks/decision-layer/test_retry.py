#!/usr/bin/env python3
"""Tests for sequential retry with a single-in-flight guard (build item 7).

The transport owns the timeout; this layer must never run attempts
concurrently and must never spawn a thread of its own.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import threading
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


provider_base = load_module("provider_base")
retry = load_module("retry")


class SuccessAndTimeoutPropagationTest(unittest.TestCase):
    def test_returns_the_result_and_passes_the_timeout_to_the_attempt(self) -> None:
        seen: list[float] = []

        def attempt(timeout_s: float) -> str:
            seen.append(timeout_s)
            return "ok"

        self.assertEqual(retry.call_with_retry(attempt, timeout_s=0.25, max_retries=2), "ok")
        self.assertEqual(seen, [0.25])

    def test_retries_a_reported_timeout_sequentially_then_raises_it(self) -> None:
        attempts = {"count": 0, "overlap": False, "running": False}

        def attempt(timeout_s: float):
            if attempts["running"]:
                attempts["overlap"] = True
            attempts["running"] = True
            attempts["count"] += 1
            attempts["running"] = False
            raise provider_base.ProviderTimeout("transport aborted")

        with self.assertRaises(provider_base.ProviderTimeout):
            retry.call_with_retry(attempt, timeout_s=0.01, max_retries=2)
        self.assertEqual(attempts["count"], 3)
        self.assertFalse(attempts["overlap"])


class RetryableVersusContractErrorsTest(unittest.TestCase):
    def test_retries_on_provider_unavailable_then_raises(self) -> None:
        attempts = {"count": 0}

        def flaky(timeout_s: float):
            attempts["count"] += 1
            raise provider_base.ProviderUnavailable("down")

        with self.assertRaises(provider_base.ProviderUnavailable):
            retry.call_with_retry(flaky, timeout_s=0.2, max_retries=2)
        self.assertEqual(attempts["count"], 3)

    def test_succeeds_after_a_transient_unavailable_error(self) -> None:
        attempts = {"count": 0}

        def flaky(timeout_s: float):
            attempts["count"] += 1
            if attempts["count"] < 2:
                raise provider_base.ProviderUnavailable("down")
            return "recovered"

        self.assertEqual(retry.call_with_retry(flaky, timeout_s=0.2, max_retries=2), "recovered")
        self.assertEqual(attempts["count"], 2)

    def test_contract_errors_are_never_retried(self) -> None:
        for error in (
            provider_base.ProviderMalformedOutput("bad shape"),
            provider_base.ProviderNotConfigured("no key"),
            provider_base.ProviderUnsupportedRequest("no"),
        ):
            attempts = {"count": 0}

            def attempt(timeout_s: float, error=error):
                attempts["count"] += 1
                raise error

            with self.assertRaises(type(error)):
                retry.call_with_retry(attempt, timeout_s=0.2, max_retries=3)
            self.assertEqual(attempts["count"], 1)


class SingleInFlightGuardTest(unittest.TestCase):
    def test_a_concurrent_caller_gets_busy_instead_of_a_duplicate_attempt(self) -> None:
        lock = threading.Lock()
        started = threading.Event()
        release = threading.Event()
        attempts = {"count": 0}

        def slow(timeout_s: float) -> str:
            attempts["count"] += 1
            started.set()
            release.wait()
            return "done"

        first: list[object] = []
        worker = threading.Thread(target=lambda: first.append(retry.call_with_retry(slow, timeout_s=1, max_retries=3, in_flight=lock)))
        worker.start()
        self.assertTrue(started.wait(timeout=1.0))

        with self.assertRaises(provider_base.ProviderBusy):
            retry.call_with_retry(slow, timeout_s=1, max_retries=3, in_flight=lock)
        self.assertEqual(attempts["count"], 1)

        release.set()
        worker.join(timeout=1.0)
        self.assertEqual(first, ["done"])
        self.assertTrue(lock.acquire(blocking=False))
        lock.release()

    def test_lock_is_released_after_a_failure(self) -> None:
        lock = threading.Lock()

        def bad(timeout_s: float):
            raise provider_base.ProviderMalformedOutput("x")

        with self.assertRaises(provider_base.ProviderMalformedOutput):
            retry.call_with_retry(bad, timeout_s=0.1, max_retries=0, in_flight=lock)
        self.assertTrue(lock.acquire(blocking=False))
        lock.release()


class NoThreadsInThisLayerTest(unittest.TestCase):
    def test_module_never_starts_a_thread(self) -> None:
        source = (HERE / "retry.py").read_text(encoding="utf-8")
        self.assertNotIn("Thread(", source)
        self.assertNotIn("daemon", source)
        self.assertNotIn("time.sleep", source)


if __name__ == "__main__":
    unittest.main()
