#!/usr/bin/env python3
"""Check Agent OS communication response-shape expectations."""

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
    {
        "id": "RS-011",
        "name": "done plus next but no evidence or state",
        "text": "Done. Implemented. Recommended next: commit.",
        "should_pass": False,
        "why": "A next action does not compensate for missing checks, state, remaining work, and decision status.",
    },
    {
        "id": "RS-012",
        "name": "tests passed but no usable close-out",
        "text": "Tests passed. Done.",
        "should_pass": False,
        "why": "Evidence alone does not tell Hafiz what changed, the current state, what remains, or what to do next.",
    },
]

COPY_READY_CASES = [
    {
        "id": "WM-001",
        "name": "copy-safe WhatsApp message",
        "text": (
            "Copy and send this:\n\n```text\n*Localisation is live.*\n\n"
            "Backend PR:\nhttps://github.com/example/project/pull/123\n\n"
            "- Please complete native-device UAT.\n```"
        ),
        "should_pass": True,
        "why": "A send-ready message should use one text block, a bare URL, and channel-native formatting.",
    },
    {
        "id": "WM-002",
        "name": "rendered Markdown link inside copy block",
        "text": (
            "```text\nBackend PR:\n"
            "[PR #123](https://github.com/example/project/pull/123)\n```"
        ),
        "should_pass": False,
        "why": "Rendered Markdown link syntax becomes copy noise in WhatsApp.",
    },
    {
        "id": "WM-003",
        "name": "blockquote instead of copy block",
        "text": "> *Localisation is live.*\n> https://github.com/example/project/pull/123",
        "should_pass": False,
        "why": "A Markdown blockquote is not the required copy-safe plain-text block.",
    },
    {
        "id": "WM-004",
        "name": "message split across copy blocks",
        "text": (
            "```text\n*Localisation is live.*\n```\n"
            "```text\nhttps://github.com/example/project/pull/123\n```"
        ),
        "should_pass": False,
        "why": "The complete send-ready message must be copyable from one block.",
    },
]

EXPLANATION_CASES = [
    {
        "id": "EX-001",
        "name": "user story before PR finding",
        "kind": "explanation_first",
        "text": (
            "What this is: the Parent Invoice Journal is the page Finance staff use "
            "to find and manage parent invoices. What happens now: filtering can hide "
            "an invoice after assignment. What should happen: the row should remain "
            "visible. Why it matters: staff otherwise think the invoice disappeared. "
            "Finding: the controller applies the status filter twice."
        ),
        "should_pass": True,
        "why": "A technical finding should follow the user and workflow story.",
    },
    {
        "id": "EX-002",
        "name": "finding before explanation",
        "kind": "explanation_first",
        "text": (
            "REVIEW - PARTIAL. Finding: ClassService applies an invalid predicate. "
            "Simple version: staff see the wrong remaining-class count."
        ),
        "should_pass": False,
        "why": "Adding a simple sentence after the code finding is not explanation-first.",
    },
    {
        "id": "EX-003",
        "name": "one-by-one walkthrough stops",
        "kind": "one_by_one",
        "text": (
            "Item 1 only. What it is: the invoice filter. What it does: helps Finance "
            "find unpaid invoices. Improvement: keep assigned invoices visible. "
            "Evidence: the browser regression reproduces the old disappearance. "
            "Decision needed: none for this item. I will stop here; say go next for item 2."
        ),
        "should_pass": True,
        "why": "One-by-one means one complete item followed by a deliberate stop.",
    },
    {
        "id": "EX-004",
        "name": "one-by-one request receives every finding",
        "kind": "one_by_one",
        "text": (
            "Here are all findings. Item 1: invoice filter. Item 2: export. "
            "Item 3: permissions."
        ),
        "should_pass": False,
        "why": "A one-by-one walkthrough must not dump later items before Hafiz says go next.",
    },
    {
        "id": "PB-001",
        "name": "plain-English preview before implementation",
        "kind": "implementation_preview",
        "text": (
            "Before implementation: who uses this is Finance staff reconciling a receipt. "
            "What happens now: one receipt can look covered in Ripple while SIMS remains unpaid. "
            "Intended change: use one shared allocation result across both systems. Options: "
            "patch only Ripple, or align the cross-system contract. Recommendation: align the "
            "contract so the same bug cannot reappear. Evidence plan: contract tests plus the "
            "real staff browser journey. Decision needed: approve this direction once, then I "
            "will continue inside the agreed boundary."
        ),
        "should_pass": True,
        "why": "A non-trivial build should be understandable in English before coding starts.",
    },
    {
        "id": "PB-002",
        "name": "implementation starts before explanation",
        "kind": "implementation_preview",
        "text": (
            "Implemented the CRM redesign and changed twelve files. Here is the diff. "
            "I can explain what the page does afterward."
        ),
        "should_pass": False,
        "why": "Explaining after implementation does not let Hafiz understand or correct the direction first.",
    },
    {
        "id": "TI-001",
        "name": "browser proof includes target identity",
        "kind": "target_identity",
        "text": (
            "Target checked: http://localhost:8018 in the local environment. Serving process: "
            "the restarted Vite server, served from worktree sifu-tutor-ui on branch "
            "chore/admin-ui at commit abc123 with local-dirty changes. Rebuilt after the change. "
            "The Playwright screenshot now shows the modern sidebar and aligned filter."
        ),
        "should_pass": True,
        "why": "Visual proof is meaningful only when the checked URL is tied to the intended source and version.",
    },
    {
        "id": "TI-002",
        "name": "screenshot from unidentified local server",
        "kind": "target_identity",
        "text": (
            "I opened http://localhost:8018 and the screenshot looks correct, so the UI fix is verified."
        ),
        "should_pass": False,
        "why": "A local URL alone does not prove which checkout, branch, process, or version served the screenshot.",
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


def copy_ready_violations(text: str) -> list[str]:
    text_blocks = re.findall(r"```(?:text|plain)?\n(.*?)```", text, flags=re.DOTALL)
    if len(text_blocks) != 1:
        return ["expected exactly one fenced plain-text block"]

    message = text_blocks[0]
    violations = []
    if re.search(r"\[[^\]]+\]\(https?://[^)]+\)", message):
        violations.append("rendered Markdown link inside message")
    if any(line.lstrip().startswith(">") for line in message.splitlines()):
        violations.append("Markdown blockquote inside message")
    return violations


def explanation_violations(case: dict[str, object]) -> list[str]:
    normalized = normalize(str(case["text"]))
    if case["kind"] == "explanation_first":
        practical_markers = (
            "what this is",
            "who uses",
            "what happens now",
            "what should happen",
            "why it matters",
            "plain language",
            "simple version",
        )
        technical_markers = ("finding:", "technical detail", "classservice", "controller", "function")
        practical_positions = [normalized.find(marker) for marker in practical_markers if marker in normalized]
        technical_positions = [normalized.find(marker) for marker in technical_markers if marker in normalized]
        if not practical_positions:
            return ["missing user/workflow explanation"]
        if technical_positions and min(practical_positions) > min(technical_positions):
            return ["technical finding appears before practical explanation"]
        return []

    if case["kind"] == "implementation_preview":
        required_groups = {
            "before implementation": ("before implementation", "before coding"),
            "user/workflow": ("who uses", "user flow", "business flow"),
            "current behavior": ("what happens now", "current behavior"),
            "intended change": ("intended change", "what will change"),
            "options": ("options", "tradeoff"),
            "recommendation": ("recommendation", "recommend"),
            "evidence plan": ("evidence plan", "how i will check"),
        }
        violations = [
            f"missing {name}"
            for name, markers in required_groups.items()
            if not any(marker in normalized for marker in markers)
        ]
        preview_position = min(
            (
                normalized.find(marker)
                for marker in ("before implementation", "before coding")
                if marker in normalized
            ),
            default=-1,
        )
        implemented_position = normalized.find("implemented")
        if implemented_position >= 0 and (preview_position < 0 or implemented_position < preview_position):
            violations.append("implementation appears before the English preview")
        return violations

    if case["kind"] == "target_identity":
        required_groups = {
            "URL/environment": ("target checked", "exact url", "environment"),
            "serving process": ("serving process", "served from"),
            "worktree/checkout": ("worktree", "checkout"),
            "branch": ("branch",),
            "commit/version": ("commit", "sha", "version", "local-dirty"),
            "restart/rebuild": ("restart", "rebuilt"),
        }
        return [
            f"missing {name}"
            for name, markers in required_groups.items()
            if not any(marker in normalized for marker in markers)
        ]

    violations = []
    for marker in ("item 1", "what it is", "what it does", "improvement", "evidence", "decision needed"):
        if marker not in normalized:
            violations.append(f"missing {marker}")
    if not any(marker in normalized for marker in ("stop here", "wait here", "say go next")):
        violations.append("missing stop before next item")
    if any(marker in normalized for marker in ("here are all", "item 3")):
        violations.append("walkthrough includes later items")
    return violations


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

    for case in COPY_READY_CASES:
        violations = copy_ready_violations(case["text"])
        passed_shape = not violations
        ok = passed_shape is case["should_pass"]
        status = "PASS" if ok else "FAIL"

        if verbose or not ok:
            print(f"{status} {case['id']} {case['name']}")
            print(f"  expected pass={case['should_pass']}, observed pass={passed_shape}")
            if violations:
                print("  violations: " + ", ".join(violations))
            print(f"  why={case['why']}")

        if not ok:
            failures.append(case["id"])

    for case in EXPLANATION_CASES:
        violations = explanation_violations(case)
        passed_shape = not violations
        ok = passed_shape is case["should_pass"]
        status = "PASS" if ok else "FAIL"

        if verbose or not ok:
            print(f"{status} {case['id']} {case['name']}")
            print(f"  expected pass={case['should_pass']}, observed pass={passed_shape}")
            if violations:
                print("  violations: " + ", ".join(violations))
            print(f"  why={case['why']}")

        if not ok:
            failures.append(case["id"])

    total = len(CASES) + len(COPY_READY_CASES) + len(EXPLANATION_CASES)
    passed = total - len(failures)
    print(f"agent-os-response-shape-runner: {passed}/{total} passed")
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
