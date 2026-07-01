#!/usr/bin/env python3
"""Run the Agent OS executable checks until a target score is reached."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
import sys
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / "scripts" / "agent-checks"


@dataclass(frozen=True)
class Check:
    name: str
    command: tuple[str, ...]
    timeout_seconds: int = 180
    parse_ratios: bool = True


@dataclass
class Result:
    check: Check
    returncode: int
    passed: int
    total: int
    output: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and self.passed == self.total

    @property
    def score(self) -> float:
        if self.total == 0:
            return 0.0
        return self.passed / self.total


CHECKS = [
    Check("router evals", (sys.executable, str(SCRIPT_DIR / "agent-os-eval-runner.py"))),
    Check("response shape", (sys.executable, str(SCRIPT_DIR / "agent-os-response-shape-runner.py"))),
    Check("state fixtures", (sys.executable, str(SCRIPT_DIR / "agent-os-state-fixture-runner.py"))),
    Check("Koda fixtures", (sys.executable, str(SCRIPT_DIR / "agent-os-koda-fixture-runner.py"))),
    Check("capability fixtures", (sys.executable, str(SCRIPT_DIR / "agent-os-capability-fixture-runner.py"))),
    Check("conversation fixtures", (sys.executable, str(SCRIPT_DIR / "agent-os-conversation-fixture-runner.py"))),
    Check("parity fixtures", (sys.executable, str(SCRIPT_DIR / "agent-os-parity-fixture-runner.py"))),
    Check("behavior traces", (sys.executable, str(SCRIPT_DIR / "agent-os-behavior-trace-runner.py"))),
    Check("adapter readiness", (sys.executable, str(SCRIPT_DIR / "agent-os-adapter-readiness.py"))),
    Check("workflow examples", (sys.executable, str(SCRIPT_DIR / "agent-os-workflow-example-runner.py"))),
    Check("scenario lab", (sys.executable, str(SCRIPT_DIR / "agent-os-scenario-lab-runner.py"), "--target", "0.90")),
    Check("health", (str(SCRIPT_DIR / "agent-os-health.sh"),), timeout_seconds=240, parse_ratios=False),
    Check("workflow doctor", (str(SCRIPT_DIR / "workflow-doctor.sh"),), timeout_seconds=240, parse_ratios=False),
]

RATIO_PATTERN = re.compile(r"(?P<passed>\d+)\s*/\s*(?P<total>\d+)")


def parse_ratios(output: str) -> tuple[int, int] | None:
    ratios = [(int(match.group("passed")), int(match.group("total"))) for match in RATIO_PATTERN.finditer(output)]
    ratios = [(passed, total) for passed, total in ratios if total > 0]
    if not ratios:
        return None
    return sum(passed for passed, _total in ratios), sum(total for _passed, total in ratios)


def run_check(check: Check) -> Result:
    try:
        completed = subprocess.run(
            check.command,
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=check.timeout_seconds,
        )
        output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
        ratio = parse_ratios(output) if check.parse_ratios else None
        if ratio is None:
            ratio = (1, 1) if completed.returncode == 0 else (0, 1)
        elif completed.returncode != 0:
            ratio = (ratio[0], ratio[1] + 1)
        return Result(check, completed.returncode, ratio[0], ratio[1], output)
    except subprocess.TimeoutExpired as exc:
        output = "\n".join(part for part in (exc.stdout or "", exc.stderr or "") if part)
        return Result(check, 124, 0, 1, output or f"Timed out after {check.timeout_seconds}s")


def format_percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def tail_lines(text: str, limit: int = 8) -> str:
    lines = [line for line in text.splitlines() if line.strip()]
    return "\n".join(lines[-limit:])


def summarize_round(results: Iterable[Result]) -> tuple[int, int]:
    passed = 0
    total = 0
    for result in results:
        passed += result.passed
        total += result.total
        status = "PASS" if result.ok else "FAIL"
        print(
            f"- {result.check.name}: {result.passed}/{result.total} "
            f"({format_percent(result.score)}) {status}"
        )
        if not result.ok:
            summary = tail_lines(result.output)
            if summary:
                print("  recent output:")
                for line in summary.splitlines():
                    print(f"    {line}")
    return passed, total


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        type=float,
        default=0.90,
        help="Required score as a decimal. Default: 0.90",
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=3,
        help="Maximum loop attempts before failing. Default: 3",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not 0 < args.target <= 1:
        print("--target must be greater than 0 and at most 1", file=sys.stderr)
        return 2
    if args.max_rounds < 1:
        print("--max-rounds must be at least 1", file=sys.stderr)
        return 2

    print("Agent OS validation loop")
    print(f"Target: {format_percent(args.target)}")
    print(
        "Meaning: this score covers executable Agent OS behavior checks. "
        "Human judgment and live LLM response quality still need real-session review."
    )

    best_passed = 0
    best_total = 0
    for round_number in range(1, args.max_rounds + 1):
        print()
        print(f"Round {round_number}/{args.max_rounds}")
        results = [run_check(check) for check in CHECKS]
        passed, total = summarize_round(results)
        current_best_score = best_passed / best_total if best_total else 0.0
        if total and passed / total > current_best_score:
            best_passed, best_total = passed, total
        round_score = passed / total if total else 0.0
        print(f"Round score: {passed}/{total} ({format_percent(round_score)})")

        if round_score >= args.target:
            print("Target reached.")
            return 0

    best_score = best_passed / best_total if best_total else 0.0
    print()
    print(f"Target not reached. Best score: {best_passed}/{best_total} ({format_percent(best_score)})")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
