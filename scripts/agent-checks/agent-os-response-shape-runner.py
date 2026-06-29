#!/usr/bin/env python3
"""Check Agent OS close-out response-shape expectations."""

from __future__ import annotations

import argparse
import re


REQUIRED_GROUPS = {
    "changed": ("changed", "updated", "added", "documented", "pushed", "committed"),
    "checked": ("checked", "verified", "passed", "health", "install", "guard", "test"),
    "state": ("local", "committed", "pushed", "origin/main", "not committed", "not pushed", "clean"),
    "next": ("recommended next", "next action", "next step", "approve", "continue", "commit"),
    "remaining": ("remaining", "unverified", "nothing remains", "still needs", "not applicable"),
    "decision": ("decision needed", "no decision needed", "approve", "accepted risk"),
}

CASES = [
    {
        "id": "RS-001",
        "name": "docs work close-out",
        "text": (
            "Done. I documented the approval model and linked it from the Agent OS index. "
            "The health check and pre-commit guard passed. Current state: Continue; this is "
            "local-only for now. Still waiting: nothing remains unverified for this docs change. "
            "Recommended next action: approve commit and push for these files. Decision needed: yes, "
            "whether to push now."
        ),
        "should_pass": True,
        "why": "Meaningful docs work should say what changed, checks, state, remaining risk, and next action.",
    },
    {
        "id": "RS-002",
        "name": "commit and push close-out",
        "text": (
            "Committed and pushed f1c15ca to origin/main. Checked eval runner, self-test, "
            "health, install dry-run, and pre-commit guard; all passed. Working tree is clean, "
            "nothing remains unverified for this tooling batch. Recommended next step: continue "
            "with response-shape checks. Decision needed: no decision needed."
        ),
        "should_pass": True,
        "why": "Commit/push close-out must name pushed state, evidence, and next action.",
    },
    {
        "id": "RS-005",
        "name": "local commit close-out",
        "text": (
            "Committed locally: 414e48d docs(agent-os): add session map skill. "
            "The pre-commit guard passed and the working tree is clean. This is "
            "not pushed yet, and nothing remains unverified for this docs commit. "
            "Recommended next: approve push if you want this on GitHub; otherwise "
            "we can continue local work."
        ),
        "should_pass": True,
        "why": "Local commit close-out must explain the push decision instead of only saying not pushed yet.",
    },
    {
        "id": "RS-006",
        "name": "technical with easier explanation",
        "text": (
            "Changed: I updated the response-shape fixture so vague close-outs fail. "
            "Checked: response-shape runner and Agent OS health passed. Current state: "
            "changed locally, not committed. Remaining: nothing remains unverified for "
            "this local fixture change. Easier explanation: the check now catches an "
            "agent that says done without telling you what changed or what next. "
            "Recommended next action: approve commit when the file list is shown. "
            "Decision needed: yes, commit approval."
        ),
        "should_pass": True,
        "why": "Technical changes should include practical meaning plus an easier explanation when useful.",
    },
    {
        "id": "RS-007",
        "name": "formal label translated",
        "text": (
            "Changed: I added a fixture for formal labels. Checked: response-shape "
            "runner passed. Current state: local-only. Remaining: nothing remains "
            "unverified for this docs check. Gate 2A here means the focused checks "
            "passed; it does not mean pushed or live. Recommended next: continue "
            "with repo-state fixtures. Decision needed: no decision needed."
        ),
        "should_pass": True,
        "why": "Formal workflow labels are acceptable when immediately translated into normal language.",
    },
    {
        "id": "RS-003",
        "name": "vague done",
        "text": "Done. Everything should be okay.",
        "should_pass": False,
        "why": "Vague done does not give Hafiz usable state, evidence, or next action.",
    },
    {
        "id": "RS-004",
        "name": "no next action",
        "text": (
            "I updated the docs and the health check passed. This is local-only and "
            "nothing remains unverified."
        ),
        "should_pass": False,
        "why": "Meaningful work should not make Hafiz ask what next.",
    },
    {
        "id": "RS-008",
        "name": "no decision needed",
        "text": (
            "I updated the docs, ran health, and the work is local-only. Nothing "
            "remains unverified. Recommended next: continue."
        ),
        "should_pass": False,
        "why": "Close-outs should say whether Hafiz needs to decide something when meaningful work changes state.",
    },
    {
        "id": "RS-009",
        "name": "blocked work with practical meaning",
        "text": (
            "Changed: I did not change code because the failing path needs a production-only "
            "credential that is not available in this session. Checked: I inspected the "
            "local route and safe logs, and the missing proof is isolated to the external "
            "callback. Current state: blocked, not committed. Remaining: production callback "
            "evidence is still unverified. Practical meaning: I can explain the likely cause, "
            "but I cannot honestly say the fix works without that evidence. Recommended next "
            "action: approve a scoped read-only production log check or provide a safe sample "
            "payload. Decision needed: yes, choose the evidence path."
        ),
        "should_pass": True,
        "why": "Blocked work should explain what is blocked, what was checked, and the exact next decision.",
    },
    {
        "id": "RS-010",
        "name": "bug explanation with technical detail",
        "text": (
            "Changed: I fixed the invoice status filter so assigned requests no longer "
            "disappear from the staff list. Checked: focused feature test and browser "
            "smoke passed. Current state: committed locally, not pushed. Remaining: "
            "nothing remains unverified for the local fix. Practical meaning: staff "
            "can now see the request after assigning it. Easier explanation: the list "
            "was being filtered twice, so the item looked like it vanished. Technical "
            "detail: the query now applies the assigned-status predicate once in the "
            "request repository instead of also filtering it again in the controller. "
            "Recommended next action: approve push if you want this on GitHub. "
            "Decision needed: yes, push approval."
        ),
        "should_pass": True,
        "why": "Bug close-outs should translate code behavior into practical and simple language.",
    },
]


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def missing_groups(text: str) -> list[str]:
    normalized = normalize(text)
    return [
        group
        for group, snippets in REQUIRED_GROUPS.items()
        if not any(snippet in normalized for snippet in snippets)
    ]


def run(verbose: bool = False) -> int:
    failures = []
    for case in CASES:
        missing = missing_groups(case["text"])
        passed_shape = not missing
        ok = passed_shape is case["should_pass"]
        status = "PASS" if ok else "FAIL"

        if verbose or not ok:
            print(f"{status} {case['id']} {case['name']}")
            print(f"  expected pass={case['should_pass']}, observed pass={passed_shape}")
            if missing:
                print("  missing: " + ", ".join(missing))
            print(f"  why={case['why']}")

        if not ok:
            failures.append(case["id"])

    passed = len(CASES) - len(failures)
    print(f"agent-os-response-shape-runner: {passed}/{len(CASES)} passed")
    if failures:
        print("failed: " + ", ".join(failures))
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Agent OS response-shape checks.")
    parser.add_argument("--verbose", action="store_true", help="print every response-shape case")
    args = parser.parse_args()
    return run(verbose=args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
