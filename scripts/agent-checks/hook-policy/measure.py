#!/usr/bin/env python3
"""Measure the LIVE hooks over the parity fixtures.

Reports, per live script, wall-clock latency of a real subprocess invocation
(mean/median/max ms over `repeat` runs per fixture) and the false-block rate
(fixtures documented as allow that the live script denied). Uses exactly the
fixture set in parity_harness.py, so the numbers describe the same behaviour
the tests assert.

Token cost is reported as null on purpose: none of these hooks calls a
metered API, and no tokenizer is wired into the hook path, so any number here
would be fabricated.

    python3 scripts/agent-checks/hook-policy/measure.py
"""
from __future__ import annotations

import json
from pathlib import Path
import statistics
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import parity_harness as ph  # noqa: E402


def measure_suite(label: str, script: Path, tool_name: str, fixtures, *, repeat: int) -> dict:
    latencies_ms: list[float] = []
    false_blocks = 0
    mismatches: list[dict] = []
    allow_count = sum(1 for f in fixtures if f.expected == ph.ALLOW)

    for fixture in fixtures:
        samples = []
        decision = None
        for _ in range(repeat):
            run = ph.run_hook(script, fixture.command, tool_name)
            samples.append(run.seconds * 1000)
            decision = run.decision
        latencies_ms.append(statistics.mean(samples))
        if decision != fixture.expected:
            mismatches.append({"command": fixture.command, "expected": fixture.expected, "actual": decision})
            if fixture.expected == ph.ALLOW and decision == ph.DENY:
                false_blocks += 1

    return {
        "suite": label,
        "script": str(script.relative_to(ph.ROOT)),
        "fixture_count": len(fixtures),
        "mismatches": mismatches,
        "false_block_rate": (false_blocks / allow_count) if allow_count else 0.0,
        "latency_ms": {
            "mean": round(statistics.mean(latencies_ms), 2),
            "median": round(statistics.median(latencies_ms), 2),
            "max": round(max(latencies_ms), 2),
            "repeat_per_fixture": repeat,
        },
    }


def run_measurement(*, repeat: int = 5) -> dict:
    suites = [measure_suite(label, script, tool, fixtures, repeat=repeat) for label, script, tool, fixtures in ph.SUITES]
    return {
        "suites": suites,
        "token_cost": {
            "value": None,
            "note": "No metered API call exists in any live hook measured here; not estimated.",
        },
    }


if __name__ == "__main__":
    print(json.dumps(run_measurement(), indent=2))
