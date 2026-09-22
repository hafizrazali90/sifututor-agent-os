#!/usr/bin/env python3
"""TDD tests for bounded timeout/retry/cancellation around a provider call
(build item 7)."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import time
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


class CallWithRetrySuccessTest(unittest.TestCase):
    def test_returns_the_function_result_on_first_success(self) -> None:
        result = retry.call_with_retry(lambda: "ok", timeout_s=0.2, max_retries=2)
        self.assertEqual(result, "ok")


class CallWithRetryTimeoutTest(unittest.TestCase):
    def test_raises_timeout_error_after_exhausting_retries(self) -> None:
        attempts = {"count": 0}

        def hang():
            attempts["count"] += 1
            time.sleep(1.0)
            return "too_late"

        started = time.monotonic()
        with self.assertRaises(TimeoutError):
            retry.call_with_retry(hang, timeout_s=0.02, max_retries=2)
        elapsed = time.monotonic() - started

        # 3 attempts (1 + 2 retries) bounded near 3 * timeout_s, never
        # anywhere close to the 1s hang -- this is the "never unbounded
        # wait" proof.
        self.assertEqual(attempts["count"], 3)
        self.assertLess(elapsed, 0.5)

    def test_does_not_block_process_exit_on_a_hang(self) -> None:
        # The background thread from a timed-out call must be a daemon
        # thread so it never prevents the interpreter (or the test
        # runner) from exiting while it keeps sleeping.
        def hang():
            time.sleep(1.0)

        with self.assertRaises(TimeoutError):
            retry.call_with_retry(hang, timeout_s=0.01, max_retries=0)
        leftover = [t for t in retry.threading.enumerate() if t.name.startswith("decision-layer-retry")]
        self.assertTrue(all(t.daemon for t in leftover))


class CallWithRetryUnavailableTest(unittest.TestCase):
    def test_retries_on_provider_unavailable_then_raises(self) -> None:
        attempts = {"count": 0}

        def flaky():
            attempts["count"] += 1
            raise provider_base.ProviderUnavailable("down")

        with self.assertRaises(provider_base.ProviderUnavailable):
            retry.call_with_retry(flaky, timeout_s=0.2, max_retries=2)
        self.assertEqual(attempts["count"], 3)

    def test_succeeds_after_a_transient_unavailable_error(self) -> None:
        attempts = {"count": 0}

        def flaky():
            attempts["count"] += 1
            if attempts["count"] < 2:
                raise provider_base.ProviderUnavailable("down")
            return "recovered"

        result = retry.call_with_retry(flaky, timeout_s=0.2, max_retries=2)
        self.assertEqual(result, "recovered")
        self.assertEqual(attempts["count"], 2)


class CallWithRetryNonRetryableErrorTest(unittest.TestCase):
    def test_malformed_output_error_is_not_retried(self) -> None:
        attempts = {"count": 0}

        def bad():
            attempts["count"] += 1
            raise provider_base.ProviderMalformedOutput("bad shape")

        with self.assertRaises(provider_base.ProviderMalformedOutput):
            retry.call_with_retry(bad, timeout_s=0.2, max_retries=3)
        self.assertEqual(attempts["count"], 1)

    def test_not_configured_error_is_not_retried(self) -> None:
        attempts = {"count": 0}

        def unconfigured():
            attempts["count"] += 1
            raise provider_base.ProviderNotConfigured("no key")

        with self.assertRaises(provider_base.ProviderNotConfigured):
            retry.call_with_retry(unconfigured, timeout_s=0.2, max_retries=3)
        self.assertEqual(attempts["count"], 1)


if __name__ == "__main__":
    unittest.main()
