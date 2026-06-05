#!/usr/bin/env python3
"""Check Agent OS state wording so "done" does not imply shipped/live."""

from __future__ import annotations

import argparse
import re


STATE_ORDER = [
    "done locally",
    "committed locally",
    "pushed",
    "pr open",
    "merged",
    "deployed",
    "live smoke passed",
]

SHIPPED_WORDS = ("deployed", "live", "smoke passed", "production")

CASES = [
    {
        "id": "ST-001",
        "name": "local-only docs work",
        "text": (
            "Status: done locally. The docs changed on disk, but they are not committed, "
            "not pushed, not deployed, and not live smoke passed. Recommended next: approve commit."
        ),
        "expected_state": "done locally",
        "should_pass": True,
        "why": "Local work can mention higher states only when clearly saying they are not true yet.",
    },
    {
        "id": "ST-002",
        "name": "pushed tooling work",
        "text": (
            "Status: pushed. Commit 28923c8 is on origin/main. It is not deployed "
            "and not live smoke passed. Recommended next: continue with the next Agent OS check."
        ),
        "expected_state": "pushed",
        "should_pass": True,
        "why": "Pushed state is allowed when it avoids implying deploy/live proof.",
    },
    {
        "id": "ST-003",
        "name": "vague done",
        "text": "Done. The fix is ready.",
        "expected_state": "",
        "should_pass": False,
        "why": "Done without a target state is ambiguous.",
    },
    {
        "id": "ST-004",
        "name": "local work implies live",
        "text": "Status: done locally. The feature is live now and smoke passed.",
        "expected_state": "done locally",
        "should_pass": False,
        "why": "Local-only state must not imply deployed or live smoke proof.",
    },
    {
        "id": "ST-005",
        "name": "committed but not pushed",
        "text": (
            "Status: committed locally. Commit abc123 exists locally. It is not pushed, "
            "not deployed, and not live smoke passed. Recommended next: approve push."
        ),
        "expected_state": "committed locally",
        "should_pass": True,
        "why": "Committed locally must distinguish local git from remote/deploy state.",
    },
]


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def has_negated_phrase(text: str, phrase: str) -> bool:
    return bool(re.search(rf"\bnot(?:\s+\w+){{0,3}}\s+{re.escape(phrase)}\b", text))


def observed_states(text: str) -> list[str]:
    normalized = normalize(text)
    return [state for state in STATE_ORDER if state in normalized]


def validate_case(case: dict) -> tuple[bool, list[str]]:
    normalized = normalize(case["text"])
    states = observed_states(normalized)
    errors = []

    expected_state = case["expected_state"]
    if expected_state:
        if expected_state not in states:
            errors.append(f"missing expected state: {expected_state}")
    elif states:
        errors.append("unexpected explicit state: " + ", ".join(states))
    else:
        errors.append("missing explicit target state")

    if "done." in normalized and not states:
        errors.append("uses vague done without target state")

    if expected_state in ("done locally", "committed locally", "pushed", "pr open", "merged"):
        for phrase in SHIPPED_WORDS:
            if phrase in normalized and not has_negated_phrase(normalized, phrase):
                errors.append(f"implies shipped/live state without proof: {phrase}")

    return not errors, errors


def run(verbose: bool = False) -> int:
    failures = []
    for case in CASES:
        passed_shape, errors = validate_case(case)
        ok = passed_shape is case["should_pass"]
        status = "PASS" if ok else "FAIL"

        if verbose or not ok:
            print(f"{status} {case['id']} {case['name']}")
            print(f"  expected pass={case['should_pass']}, observed pass={passed_shape}")
            if errors:
                print("  errors: " + "; ".join(errors))
            print(f"  why={case['why']}")

        if not ok:
            failures.append(case["id"])

    passed = len(CASES) - len(failures)
    print(f"agent-os-state-fixture-runner: {passed}/{len(CASES)} passed")
    if failures:
        print("failed: " + ", ".join(failures))
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Agent OS state wording fixture checks.")
    parser.add_argument("--verbose", action="store_true", help="print every state fixture case")
    args = parser.parse_args()
    return run(verbose=args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
