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

REMOTE_WORDS = ("pushed", "pr open", "merged", "deployed", "live", "smoke passed", "production")
DEPLOY_WORDS = ("deployed", "live", "smoke passed", "production")
LIVE_WORDS = ("live", "smoke passed", "production")

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
    {
        "id": "ST-006",
        "name": "pr open but not merged",
        "text": (
            "Status: pr open. PR #18 exists on GitHub for commit abc123. It is not merged, "
            "not deployed, and not live smoke passed. Recommended next: wait for review "
            "and CI before merge."
        ),
        "expected_state": "pr open",
        "should_pass": True,
        "why": "PR open is not the same as merged, deployed, or live checked.",
    },
    {
        "id": "ST-007",
        "name": "merged but not deployed",
        "text": (
            "Status: merged. PR #18 is merged into main. It is not deployed and not "
            "live smoke passed. Recommended next: approve deploy if this should go live."
        ),
        "expected_state": "merged",
        "should_pass": True,
        "why": "Merged code must not be described as live without deploy evidence.",
    },
    {
        "id": "ST-008",
        "name": "deployed but not smoke checked",
        "text": (
            "Status: deployed. Release 2026-06-29.1 is deployed to production. It is "
            "not live smoke passed yet. Recommended next: run safe smoke and monitoring."
        ),
        "expected_state": "deployed",
        "should_pass": True,
        "why": "Deployment is not the same as live smoke proof.",
    },
    {
        "id": "ST-009",
        "name": "live smoke passed",
        "text": (
            "Status: live smoke passed. Release 2026-06-29.1 is deployed and the safe "
            "production smoke check passed. Recommended next: monitor logs or close."
        ),
        "expected_state": "live smoke passed",
        "should_pass": True,
        "why": "Live smoke passed is allowed only when explicitly stated as checked evidence.",
    },
    {
        "id": "ST-010",
        "name": "pushed implies merged",
        "text": "Status: pushed. The branch is merged and live now.",
        "expected_state": "pushed",
        "should_pass": False,
        "why": "Pushed does not imply merged or live.",
    },
    {
        "id": "ST-011",
        "name": "pr open with evidence",
        "text": (
            "Status: pr open. PR #42 is open at https://github.com/sifututor/app/pull/42 "
            "for commit abc123. CI is pending, so it is not merged, not deployed, "
            "and not live smoke passed. Recommended next: wait for CI and review."
        ),
        "expected_state": "pr open",
        "required_snippets": ("PR #42", "https://github.com", "commit abc123", "CI"),
        "should_pass": True,
        "why": "PR-open claims should include enough evidence to find the PR and source commit.",
    },
    {
        "id": "ST-012",
        "name": "pr open without evidence",
        "text": "Status: pr open. The work is ready for review.",
        "expected_state": "pr open",
        "required_snippets": ("PR #", "https://github.com", "commit"),
        "should_pass": False,
        "why": "PR-open claims are weak without a PR number/link and source commit.",
    },
    {
        "id": "ST-013",
        "name": "deployed with source evidence",
        "text": (
            "Status: deployed. Release 2026-06-29.1 deployed commit abc123 to staging. "
            "The deployment record is https://deploy.example/releases/2026-06-29.1. "
            "It is not live smoke passed yet. Recommended next: run staging smoke."
        ),
        "expected_state": "deployed",
        "required_snippets": ("Release 2026-06-29.1", "commit abc123", "https://deploy.example"),
        "should_pass": True,
        "why": "Deploy claims should name the target release/source evidence and avoid implying smoke proof.",
    },
    {
        "id": "ST-014",
        "name": "deployed without source evidence",
        "text": "Status: deployed. The app is updated and should be fine.",
        "expected_state": "deployed",
        "required_snippets": ("Release", "commit"),
        "should_pass": False,
        "why": "Deploy claims need source/release evidence before the agent can call them deployed.",
    },
]


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def has_negated_phrase(text: str, phrase: str) -> bool:
    return bool(re.search(rf"\bnot(?:\s+\w+){{0,3}}\s+{re.escape(phrase)}\b", text))


def contains_text(text: str, snippet: str) -> bool:
    return normalize(snippet) in text


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

    for snippet in case.get("required_snippets", ()):
        if not contains_text(normalized, snippet):
            errors.append(f"missing required evidence snippet: {snippet}")

    if "done." in normalized and not states:
        errors.append("uses vague done without target state")

    if expected_state in ("done locally", "committed locally"):
        phrases = REMOTE_WORDS
    elif expected_state == "pushed":
        phrases = ("pr open", "merged", "deployed", "live", "smoke passed", "production")
    elif expected_state == "pr open":
        phrases = ("merged", "deployed", "live", "smoke passed", "production")
    elif expected_state == "merged":
        phrases = DEPLOY_WORDS
    elif expected_state == "deployed":
        phrases = ("live", "smoke passed")
    else:
        phrases = ()

    for phrase in phrases:
        if phrase in normalized and not has_negated_phrase(normalized, phrase):
            if phrase == expected_state:
                continue
            if expected_state == "live smoke passed":
                continue
            if expected_state == "deployed" and phrase == "deployed":
                continue
            if expected_state == "pr open" and phrase == "pr open":
                continue
            if expected_state == "pushed" and phrase == "pushed":
                continue
            if expected_state == "merged" and phrase == "merged":
                continue
            errors.append(f"implies further state without proof: {phrase}")

    if expected_state == "live smoke passed":
        for phrase in ("deployed", "smoke check passed", "smoke passed"):
            if phrase in normalized and not has_negated_phrase(normalized, phrase):
                break
        else:
            errors.append("live smoke state lacks deploy or smoke evidence")

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
