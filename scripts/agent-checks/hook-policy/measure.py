#!/usr/bin/env python3
"""Lightweight measurement harness (bundle spec, build item 3).

Reports, for a representative fixture set drawn from the same commands
already proven behavior-identical against the real scripts in
test_parity_*.py:

- dispatch latency (wall-clock per dispatch, mean/median/max)
- route accuracy against the documented-identical-behavior fixtures
- false-block rate (fixtures expected "allow" that the dispatcher denies)
- startup/context cost, reported as two honest proxies: cold-import wall
  time, and raw source size (bytes/lines) of this module -- NOT a real
  LLM-context token count, because no tokenizer is wired into this repo's
  hook path
- token/cost: explicitly "not available". Nothing in the checks exercised
  here calls a metered API. Bundle 1's decision-layer/provider_jev.py can
  carry a real dollar `cost` field when a real JEV provider call succeeds,
  but that is a different subsystem (see SURVEY.md section 6) not
  exercised by any default_checks() check, so reporting a number here
  would be fabricated. If a future expensive check adds a real metered
  backend, wire its actual reported cost into `token_cost` instead of
  guessing.

Run directly for a human-readable report:

    python3 scripts/agent-checks/hook-policy/measure.py
"""
from __future__ import annotations

import json
from pathlib import Path
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from default_checks import default_checks  # noqa: E402
from dispatcher import HookDispatcher  # noqa: E402
from models import HookRequest, Outcome  # noqa: E402

# Every command below is drawn from a fixture already proven
# behavior-identical to the real scripts (test_parity_branch_name.py,
# test_parity_commit_message.py, test_parity_heredoc_guard.py,
# test_parity_codex_safety_guards.py). "expected" is that proven outcome.
MEASURE_FIXTURES: list[dict] = [
    {"command": "git checkout -b feat/add-login-screen", "expected": "allow"},
    {"command": "git checkout -b fix/null-crash-on-payment", "expected": "allow"},
    {"command": "git checkout -b main", "expected": "allow"},
    {"command": "git checkout -b sifu-staging-2", "expected": "allow"},
    {"command": "git checkout -b release/2026-09", "expected": "allow"},
    {"command": "git checkout -b nonsense-branch", "expected": "deny"},
    {"command": "git checkout -b feat/UPPERCASE", "expected": "deny"},
    {"command": 'git commit -m "feat: add user authentication"', "expected": "allow"},
    {"command": 'git commit -m "fix(api): handle null responses"', "expected": "allow"},
    {"command": 'git commit -m "✨ feat: add user authentication"', "expected": "allow"},
    {"command": 'git commit -m "fixed a thing"', "expected": "deny"},
    {"command": 'git commit -m "bad message" --no-verify', "expected": "deny"},  # no-verify itself is denied
    {"command": "git commit --amend", "expected": "allow"},
    {"command": "git commit -m \"$(cat <<'EOF'\nfeat: add x\nEOF\n)\"", "expected": "deny"},
    {"command": "git reset --hard HEAD~1", "expected": "deny"},
    {"command": "git reset --soft HEAD~1", "expected": "allow"},
    {"command": "rm -rf live/sifu-tutor", "expected": "deny"},
    {"command": "rm -rf node_modules", "expected": "allow"},
    {"command": "cat .env.production", "expected": "deny"},
    {"command": "cat README.md", "expected": "allow"},
    {"command": "git status", "expected": "allow"},
    {"command": "printenv", "expected": "deny"},
]


def _dispatch_outcome(dispatcher: HookDispatcher, command: str) -> str:
    result = dispatcher.dispatch(HookRequest(tool_name="Bash", command=command))
    return "deny" if result.blocked else "allow"


def _startup_cost() -> dict:
    """Cold-import wall time (subprocess, so nothing is warm from this
    process's own imports) plus raw source size as a context-cost proxy."""
    probe = (
        "import time,sys; sys.path.insert(0, %r); t0=time.perf_counter(); "
        "import default_checks, dispatcher, hook_output, adapter_claude, adapter_codex; "
        "print(time.perf_counter()-t0)" % str(HERE)
    )
    result = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    try:
        cold_import_s = float(result.stdout.strip())
    except ValueError:
        cold_import_s = -1.0  # subprocess failed; report honestly below

    source_files = sorted(HERE.glob("*.py"))
    source_bytes = sum(f.stat().st_size for f in source_files)
    source_lines = sum(len(f.read_text().splitlines()) for f in source_files)

    return {
        "cold_import_ms": round(cold_import_s * 1000, 3) if cold_import_s >= 0 else None,
        "source_bytes": source_bytes,
        "source_lines": source_lines,
        "source_file_count": len(source_files),
        "note": "Proxy measurements only: cold_import_ms is a subprocess wall-clock "
        "import of the core modules, and source_bytes/source_lines is this "
        "directory's raw .py size (including tests and fixtures). Neither is a "
        "real LLM context-token count -- no tokenizer is wired into this repo's "
        "hook path, so that figure is not estimated here.",
    }


def run_measurement(*, repeat: int = 20) -> dict:
    dispatcher = HookDispatcher(default_checks())

    latencies_ms: list[float] = []
    correct = 0
    false_blocks = 0
    mismatches: list[dict] = []

    for fixture in MEASURE_FIXTURES:
        command = fixture["command"]
        expected = fixture["expected"]

        # Time `repeat` dispatches per fixture; keep only the per-fixture mean
        # so one fixture with heavier logic doesn't dominate the average via
        # sample-count imbalance.
        samples = []
        actual = None
        for _ in range(repeat):
            start = time.perf_counter()
            actual = _dispatch_outcome(dispatcher, command)
            samples.append((time.perf_counter() - start) * 1000)
        latencies_ms.append(statistics.mean(samples))

        if actual == expected:
            correct += 1
        else:
            mismatches.append({"command": command, "expected": expected, "actual": actual})
            if expected == "allow" and actual == "deny":
                false_blocks += 1

    fixture_count = len(MEASURE_FIXTURES)
    allow_fixture_count = sum(1 for f in MEASURE_FIXTURES if f["expected"] == "allow")

    return {
        "fixture_count": fixture_count,
        "route_accuracy": correct / fixture_count if fixture_count else 0.0,
        "false_block_rate": (false_blocks / allow_fixture_count) if allow_fixture_count else 0.0,
        "mismatches": mismatches,
        "dispatch_latency_ms": {
            "mean": round(statistics.mean(latencies_ms), 4),
            "median": round(statistics.median(latencies_ms), 4),
            "max": round(max(latencies_ms), 4),
            "repeat_per_fixture": repeat,
        },
        "startup_cost": _startup_cost(),
        "token_cost": {
            "value": None,
            "note": "No real token/cost data source exists for hook execution in "
            "this repo -- default_checks() are all local regex/filesystem/git "
            "checks with no metered API call, so no token/cost figure is "
            "reported here rather than fabricating one. A real per-call dollar "
            "cost exists only inside decision-layer/provider_jev.py's live JEV "
            "provider path (see SURVEY.md section 6), which no default check "
            "exercises.",
        },
    }


if __name__ == "__main__":
    print(json.dumps(run_measurement(), indent=2))
