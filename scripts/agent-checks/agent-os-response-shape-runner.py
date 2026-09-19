#!/usr/bin/env python3
"""Check Agent OS communication response-shape expectations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
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

RELEASE_HANDOFF_CASES = [
    {
        "id": "RH-001",
        "name": "integrated developer PR close-out",
        "audiences": ["developer"],
        "confirmed_sources": ["staff report", "treq"],
        "text": (
            "Developer message:\n```text\nHi, update on your PR #1751. We reviewed your "
            "fix and improved it before merging and deploying it. We added the "
            "production-shaped TREQ case because the original evidence was incomplete "
            "and missing permanent browser coverage. The final fix is live and the "
            "staff report now shows the correct balance. Please independently verify "
            "the final PR and reply with verification evidence. Add this acceptance, "
            "related-impact, E2E, and release-proof lesson to your AI checklist.\n```"
        ),
        "should_pass": True,
        "why": "A developer handoff should continue their PR story, teach the delta, and request independent evidence.",
    },
    {
        "id": "RH-002",
        "name": "generic incident message disconnected from developer PR",
        "audiences": ["developer"],
        "confirmed_sources": ["staff report", "treq"],
        "text": (
            "Developer message:\n```text\nThe class-count issue is fixed and live. "
            "The staff report now shows the correct balance.\n```"
        ),
        "should_pass": False,
        "why": "A generic incident result does not tell the developer what review changed, what was missed, or what to verify.",
    },
    {
        "id": "RH-003",
        "name": "invented Tawk source",
        "audiences": ["developer"],
        "confirmed_sources": ["staff report", "treq"],
        "text": (
            "Developer message:\n```text\nHi, update on your PR #1751. We reviewed your "
            "fix and improved it because the original proof was incomplete and missing "
            "E2E coverage. The Tawk report is now resolved and the final fix is deployed. "
            "Please independently verify it, reply with verification evidence, and add "
            "the lesson to your AI checklist.\n```"
        ),
        "should_pass": False,
        "why": "The handoff must not invent a report channel that the confirmed context did not name.",
    },
    {
        "id": "RH-004",
        "name": "two disconnected messages to one developer",
        "audiences": ["developer"],
        "confirmed_sources": ["staff report", "treq"],
        "text": (
            "Developer message 1:\n```text\nThe issue is fixed and live.\n```\n"
            "Developer message 2:\n```text\nWe reviewed your PR and added missing tests. "
            "Please independently verify and reply with evidence.\n```"
        ),
        "should_pass": False,
        "why": "One developer should receive one integrated continuation, not two disconnected messages.",
    },
    {
        "id": "RH-005",
        "name": "separate staff and developer audiences",
        "audiences": ["staff", "developer"],
        "confirmed_sources": ["staff report", "treq"],
        "text": (
            "Staff message:\n```text\nThe class balance issue has been corrected and is "
            "live. Please try the schedule again and tell us if the number is still wrong.\n```\n"
            "Developer message:\n```text\nHi, update on your PR #1751. We reviewed your "
            "fix and improved it before it was merged and deployed. We added the real TREQ "
            "case because the original evidence was incomplete and missing permanent E2E. "
            "The final result is live. Please independently verify the final work, reply "
            "with verification evidence, and add the lesson to your AI checklist.\n```"
        ),
        "should_pass": True,
        "why": "Different audiences should receive separate messages with the right level of detail.",
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

TODAY_BRIEFING_CASES = [
    {
        "id": "TB-001",
        "name": "bounded evidence-labelled today briefing",
        "text": (
            "## Needs Hafiz now\n"
            "Source: GitHub · Confidence: verified · Freshness: checked now\n"
            "## Waiting on staff\nNothing currently identified.\n"
            "## Agent can continue\nRead-only diagnosis can continue without approval.\n"
            "## Monitor\nPlanner report · Confidence: reported · Freshness: checked now\n"
            "## Deferred\nMission Ledger item · Confidence: trusted · Freshness: recent\n"
            "Approval rule: read-only preparation does not need approval; ask immediately "
            "before the exact write, release, production, access, or destructive action."
        ),
        "should_pass": True,
        "why": "A today briefing should separate attention ownership and expose evidence, freshness, and the real approval boundary.",
    },
    {
        "id": "TB-002",
        "name": "flat priority list with false preparation approval",
        "text": (
            "## Priorities\n"
            "Approve preparation of credential rotations.\n"
            "Planner says the issue is real."
        ),
        "should_pass": False,
        "why": "A flat list hides who owns the next move, treats reported intake as proof, and asks approval too early.",
    },
]


# ---------------------------------------------------------------------------
# Save-session close-out shape (2026-08-01 issue-30 correction).
#
# These fixtures are grounded in the four real failures found by the live
# VS Code extension retest: the save level was never chosen, the honest ending
# state was never named, a required guard was silently omitted instead of being
# reported as unrun, and repo/worktree identity was asserted without discovery.
#
# The rules below are deliberately marker-based rather than broad regex, so
# ordinary prose is not rejected for wording alone.
# ---------------------------------------------------------------------------

SAVE_LEVEL_MARKERS = ("quick save", "normal save", "critical save")
ENDING_STATE_MARKERS = ("ending state", "current state:")
ENDING_STATE_VALUES = ("continue", "save only", "park", "hand off", "close")
GUARD_SUBJECT_MARKERS = ("guard", "pre-commit", "checks")
GUARD_STATUS_MARKERS = ("passed", "failed", "not run", "unverified", "could not run")
REPO_IDENTITY_MARKERS = ("worktree", "branch")
KODA_WRITE_MARKERS = ("koda: stored", "koda: updated", "stored in koda", "saved to koda")
PROJECT_TAG_MARKERS = (
    "project tag",
    "sifututor",
    "codex-parity",
    "sifu-tutor",
    "ripple-suite",
    "sifututor_tutor",
    "sifututor_parent",
    "lls",
    "lls-frontend",
    "lls-mobile",
    "creative-hub",
    "team-inbox",
    "finch-inbox",
)
NEXT_ACTION_MARKERS = ("recommended next", "next action", "next step")

# A named unrun check contradicts a blanket "everything passed" claim. Both
# lists are short and literal so valid prose is not caught by accident.
UNRUN_MARKERS = ("not run", "could not run", "unable to run", "unverified")
BLANKET_CLAIM_MARKERS = (
    "all checks passed",
    "everything passed",
    "fully verified",
    "everything is verified",
)

# 2026-08-01 issue-30 acceptance correction: connected save-session
# behaviors that response shape alone previously did not check at all --
# a Session Map "not needed" claim with no discovery step, a save report
# with no active-task line, and a Koda-unavailable claim with no named
# fallback all passed the old marker set.
SESSION_MAP_NOT_NEEDED_MARKERS = (
    "session map: not needed",
    "session map not needed",
    "session map: none needed",
)
SESSION_MAP_SEARCH_MARKERS = (
    ".agent-os/session-maps",
    "checked the session map location",
    "searched the session map location",
    "no matching session map",
    "no active session map found",
    "found no session map",
)
MEANINGFUL_SAVE_LEVEL_MARKERS = ("normal save", "critical save")
ACTIVE_TASK_LABEL_MARKERS = ("active task:",)

# 2026-08-01 TEST 3 rerun failures: a save report is allowed to say "not
# checked" for a source it never inspected, but the Mission Ledger and
# remote-branch facts are required-discovery items, not optional ones --
# saying they were left unchecked/unverified is itself the violation, not an
# excuse. This is a narrow, explicit-phrase check, not a blanket "must
# always mention Mission Ledger/remote state" requirement.
MISSION_LEDGER_UNCHECKED_MARKERS = (
    "mission ledger: not checked",
    "mission ledger not checked",
    "mission ledger: unknown",
    "mission ledger relevance unknown",
    "mission ledger was not checked",
    "did not check the mission ledger",
    "left the mission ledger unchecked",
)
REMOTE_BRANCH_CARRIED_FORWARD_MARKERS = (
    "carried forward, not re-checked",
    "carried-forward, not re-checked",
    "not re-checked this turn",
    "carried forward from an earlier turn",
    "treat that specific fact as carried-forward",
)
KODA_UNAVAILABLE_MARKERS = (
    "koda unavailable",
    "koda mcp unavailable",
    "koda: not run",
    "koda not run",
    "koda failed",
    "koda save failed",
)

# 2026-08-01 independent-review correction: merely naming "workspace helper"
# or the helper path is not evidence the fallback was actually used -- the
# original SV-015 text named the helper while explicitly saying it "was not
# used," and still passed. Detection must distinguish three honest shapes:
# the helper was actually used (read-only), no helper/MCP exists and an
# honest fallback artifact/path was named instead, or neither happened.
#
# 2026-08-01 second independent-review correction: a generic "used the
# workspace helper" claim does not prove which helper operation ran, and
# "used scripts/agent-checks/koda health" is not evidence of the required
# search/dedup lookup at all -- `koda health` calls
# `koda_health_check(write=True)` and updates the dedicated health memory;
# it is a write, not a read-only search. Only phrases that name the
# search/read operation specifically count as use evidence now.
KODA_FALLBACK_USE_MARKERS = (
    "scripts/agent-checks/koda search",
    "used the helper's search path",
    "used the helper's read path",
    "used the helper's read-only path",
    "performed a read-only koda lookup through the approved helper",
)
KODA_FALLBACK_ARTIFACT_MARKERS = (
    "handoff note",
    "repo doc note",
    "fallback saved in",
)
KODA_FALLBACK_NEGATION_MARKERS = (
    "not used",
    "was not used",
    "did not use",
    "declined to use",
    "skipped the helper",
)
KODA_MANUAL_SECRET_MARKERS = (
    "set koda_api_key",
    "export koda_api_key",
    "configure koda_api_key",
    "provide koda_api_key",
    "paste koda_api_key",
    "add koda_api_key",
)
# Deliberately excludes a bare "no helper" marker: "no approved workspace
# helper is available" is a legitimate case-4 statement (no permitted helper
# exists), not a claim that an available helper was skipped. Conflating the
# two would wrongly reject an honest no-helper-plus-fallback-artifact report.

SAVE_SESSION_CASES = [
    {
        "id": "SV-001",
        "name": "honest save with an unrun guard",
        "text": (
            "SESSION SAVED - Sifututor Agent OS. Normal Save. Worktree: "
            "agent-os-claude-parity-phase-one on branch "
            "chore/agent-os-claude-parity-phase-one, dirty with the ten approved "
            "files. Guards: pre-commit-guard.sh not run, because commands were "
            "prohibited in this session. Koda: stored with the sifututor project "
            "tag. Session Map: current. Active task: none. Mission Ledger: no "
            "new follow-up. Ending state: Save Only. Recommended next action: "
            "approve running the shared guard."
        ),
        "should_pass": True,
        "why": "An unrunnable check must be named and labeled unrun, not dropped.",
    },
    {
        "id": "SV-002",
        "name": "guard actually run and passed",
        "text": (
            "SESSION SAVED - Sifututor Agent OS. Critical Save. Worktree and "
            "branch confirmed by git status: chore/agent-os-claude-parity-phase-one, "
            "seven files modified. Guards: the shared pre-commit guard passed. "
            "Koda: stored with the codex-parity project tag. Session Map: "
            "updated. Active task: none. Mission Ledger: skipped. Ending "
            "state: Hand Off. Recommended next: Codex independent review."
        ),
        "should_pass": True,
        "why": "A complete save names level, repo identity, guard result, tag, ending state, and next action.",
    },
    {
        "id": "SV-003",
        "name": "no save level chosen",
        "text": (
            "SESSION SAVED. Worktree and branch confirmed. Guards: pre-commit "
            "guard passed. Koda: stored with the sifututor project tag. Ending "
            "state: Save Only. Recommended next action: review the diff."
        ),
        "should_pass": False,
        "why": "The save level tells the next agent how much of the close-out contract applies.",
    },
    {
        "id": "SV-004",
        "name": "no honest ending state",
        "text": (
            "SESSION SAVED. Normal Save. Worktree and branch confirmed by git "
            "status. Guards: pre-commit guard passed. Koda: stored with the "
            "sifututor project tag. Recommended next action: review the diff."
        ),
        "should_pass": False,
        "why": "Without an ending state, Hafiz cannot tell whether the work is closed, parked, or handed off.",
    },
    {
        "id": "SV-005",
        "name": "guard silently omitted",
        "text": (
            "SESSION SAVED. Normal Save. Worktree and branch confirmed by git "
            "status. Koda: stored with the sifututor project tag. Ending state: "
            "Save Only. Recommended next action: review the diff."
        ),
        "should_pass": False,
        "why": "The 2026-08-01 retest failure: the shared guard was never named at all, run or not.",
    },
    {
        "id": "SV-006",
        "name": "repo identity never established",
        "text": (
            "SESSION SAVED. Normal Save. Guards: pre-commit guard not run. "
            "Koda: stored with the sifututor project tag. Ending state: Save "
            "Only. Recommended next action: review the diff."
        ),
        "should_pass": False,
        "why": "The 2026-08-01 retest failure: the save never named the worktree or branch it applied to.",
    },
    {
        "id": "SV-007",
        "name": "blanket pass claim beside a named unrun check",
        "text": (
            "SESSION SAVED. Normal Save. Worktree and branch confirmed by git "
            "status. All checks passed. The live extension retest was not run. "
            "Koda: stored with the sifututor project tag. Ending state: Close. "
            "Recommended next action: none."
        ),
        "should_pass": False,
        "why": "Saying everything passed while naming an unrun check overclaims proven state.",
    },
    {
        "id": "SV-008",
        "name": "Koda write with no project tag",
        "text": (
            "SESSION SAVED. Normal Save. Worktree and branch confirmed by git "
            "status. Guards: pre-commit guard passed. Koda: stored a lesson "
            "tagged agent-os and workflow. Ending state: Save Only. Recommended "
            "next action: review the diff."
        ),
        "should_pass": False,
        "why": "A domain tag such as agent-os is not a project tag; every memory needs one.",
    },
    {
        "id": "SV-009",
        "name": "project tag cannot hide inside another word",
        "text": (
            "SESSION SAVED. Normal Save. Worktree and branch confirmed by git "
            "status. Guards: pre-commit guard passed. Koda: stored a lesson "
            "about workflow skills tagged agent-os. Ending state: Save Only. "
            "Recommended next action: review the diff."
        ),
        "should_pass": False,
        "why": "The project tag lls must not match as a substring inside the unrelated word skills.",
    },
    {
        "id": "SV-010",
        "name": "Session Map not needed without discovery",
        "text": (
            "SESSION SAVED. Normal Save. Worktree and branch confirmed by git "
            "status. Guards: pre-commit guard passed. Koda: stored with the "
            "sifututor project tag. Session Map: not needed. Active task: "
            "none. Ending state: Close. Recommended next action: none."
        ),
        "should_pass": False,
        "why": (
            "The 2026-08-01 acceptance failure: an existing Session Map was missed "
            "because 'not needed' was asserted without ever searching for one."
        ),
    },
    {
        "id": "SV-011",
        "name": "Session Map not needed with discovery stated",
        "text": (
            "SESSION SAVED. Normal Save. Worktree and branch confirmed by git "
            "status. Guards: pre-commit guard passed. Koda: stored with the "
            "sifututor project tag. Session Map: not needed; checked the "
            "session map location under .agent-os/session-maps and found no "
            "matching session map. Active task: none. Ending state: Close. "
            "Recommended next action: none."
        ),
        "should_pass": True,
        "why": "A 'not needed' claim is honest once the search was actually stated.",
    },
    {
        "id": "SV-012",
        "name": "Normal Save missing active-task status",
        "text": (
            "SESSION SAVED. Normal Save. Worktree and branch confirmed by git "
            "status. Guards: pre-commit guard passed. Koda: stored with the "
            "sifututor project tag. Session Map: current. Ending state: Save "
            "Only. Recommended next action: review the diff."
        ),
        "should_pass": False,
        "why": "A meaningful save must say the active task and next step, or explicitly say none.",
    },
    {
        "id": "SV-013",
        "name": "Normal Save with explicit active-task none",
        "text": (
            "SESSION SAVED. Normal Save. Worktree and branch confirmed by git "
            "status. Guards: pre-commit guard passed. Koda: stored with the "
            "sifututor project tag. Session Map: current. Active task: none. "
            "Ending state: Save Only. Recommended next action: review the diff."
        ),
        "should_pass": True,
        "why": "Explicitly saying active task: none satisfies the honest-reporting requirement.",
    },
    {
        "id": "SV-014",
        "name": "Koda unavailable without naming the fallback",
        "text": (
            "SESSION SAVED. Normal Save. Worktree and branch confirmed by git "
            "status. Guards: pre-commit guard passed. Koda unavailable this "
            "session. Session Map: current. Active task: none. Ending state: "
            "Save Only. Recommended next action: review the diff."
        ),
        "should_pass": False,
        "why": (
            "The 2026-08-01 acceptance gap: Koda was reported unavailable with no "
            "named fallback path, so the reader cannot tell if a documented "
            "workaround was even considered."
        ),
    },
    {
        "id": "SV-015",
        "name": "Koda unavailable and helper named but deliberately not used",
        "text": (
            "SESSION SAVED. Normal Save. Worktree and branch confirmed by git "
            "status. Guards: pre-commit guard passed. Koda unavailable this "
            "session; the approved documented workspace helper "
            "scripts/agent-checks/koda was not used because this was a "
            "search/read-only dry run. Session Map: current. Active task: "
            "none. Ending state: Save Only. Recommended next action: review "
            "the diff."
        ),
        "should_pass": False,
        "why": (
            "2026-08-01 independent-review defect: naming the helper while "
            "explicitly saying it was not used contradicts the corrected "
            "adapter, which requires using the helper's search/read path for "
            "a dry run when it is available/permitted. Mentioning the helper "
            "name is not evidence it was actually used."
        ),
    },
    {
        "id": "SV-016",
        "name": "Koda unavailable and helper's search/read path actually used",
        "text": (
            "SESSION SAVED. Normal Save. Worktree and branch confirmed by git "
            "status. Guards: pre-commit guard passed. Koda MCP unavailable "
            "this session; used the documented workspace helper "
            "scripts/agent-checks/koda search for a read-only lookup, and "
            "the result is reported honestly here. No memory was stored or "
            "updated, because this was a search/read-only dry run. Session "
            "Map: current. Active task: none. Ending state: Save Only. "
            "Recommended next action: review the diff."
        ),
        "should_pass": True,
        "why": (
            "The true positive control: the helper's search/read path was "
            "actually used, the result is reported honestly, and no store/"
            "update happened because it was a dry run."
        ),
    },
    {
        "id": "SV-017",
        "name": "Koda unavailable, no permitted helper, honest fallback artifact named",
        "text": (
            "SESSION SAVED. Normal Save. Worktree and branch confirmed by git "
            "status. Guards: pre-commit guard passed. Koda unavailable this "
            "session, and no approved workspace helper is available in this "
            "environment. Koda save failed: fallback saved in a handoff note "
            "instead. Session Map: current. Active task: none. Ending state: "
            "Save Only. Recommended next action: review the diff."
        ),
        "should_pass": True,
        "why": (
            "When neither MCP nor a permitted helper exists, naming the "
            "honest fallback artifact/path is still valid, per save-session.md's "
            "fallback path."
        ),
    },
    {
        "id": "SV-018",
        "name": "Koda unavailable and only the helper's health operation ran",
        "text": (
            "SESSION SAVED. Normal Save. Worktree and branch confirmed by git "
            "status. Guards: pre-commit guard passed. Koda MCP unavailable "
            "this session; ran scripts/agent-checks/koda health to confirm "
            "connectivity. Session Map: current. Active task: none. Ending "
            "state: Save Only. Recommended next action: review the diff."
        ),
        "should_pass": False,
        "why": (
            "2026-08-01 second independent-review defect: `koda health` calls "
            "koda_health_check(write=True) and updates the dedicated health "
            "memory. It is a write, not the required read-only search/dedup "
            "lookup, so it must not count as fallback-use evidence."
        ),
    },
    {
        "id": "SV-019",
        "name": "Koda unavailable with a generic unspecified helper-use claim",
        "text": (
            "SESSION SAVED. Normal Save. Worktree and branch confirmed by git "
            "status. Guards: pre-commit guard passed. Koda unavailable this "
            "session; used the workspace helper. Session Map: current. "
            "Active task: none. Ending state: Save Only. Recommended next "
            "action: review the diff."
        ),
        "should_pass": False,
        "why": (
            "A generic 'used the workspace helper' claim does not say which "
            "operation ran; it could mean health, store, update, or search. "
            "Only an explicit search/read-operation claim counts as evidence."
        ),
    },
    {
        "id": "SV-020",
        "name": "Mission Ledger reported as not checked",
        "text": (
            "SESSION SAVED. Normal Save. Worktree and branch confirmed by git "
            "status. Guards: pre-commit guard passed. Koda: stored with the "
            "sifututor project tag. Session Map: current. Active task: none. "
            "Mission Ledger: not checked this turn. Ending state: Save Only. "
            "Recommended next action: review the diff."
        ),
        "should_pass": False,
        "why": (
            "2026-08-01 TEST 3 rerun failure: the Mission Ledger is a required "
            "discovery item, not an optional one -- reporting it as unchecked "
            "is the violation, not a valid honest answer."
        ),
    },
    {
        "id": "SV-021",
        "name": "Mission Ledger actually checked and reported",
        "text": (
            "SESSION SAVED. Normal Save. Worktree and branch confirmed by git "
            "status. Guards: pre-commit guard passed. Koda: stored with the "
            "sifututor project tag. Session Map: current. Active task: none. "
            "Mission Ledger: checked the relevant project ledger; no new "
            "follow-up is warranted. Ending state: Save Only. Recommended "
            "next action: review the diff."
        ),
        "should_pass": True,
        "why": "Actually checking the ledger and reporting a concrete outcome satisfies the requirement.",
    },
    {
        "id": "SV-022",
        "name": "remote-branch state reported as carried-forward instead of fresh",
        "text": (
            "SESSION SAVED. Normal Save. Worktree and branch confirmed by git "
            "status. Guards: pre-commit guard passed. Koda: stored with the "
            "sifututor project tag. Session Map: current. Active task: none. "
            "Push: not re-checked this turn, so treat that specific fact as "
            "carried-forward from an earlier turn. Ending state: Save Only. "
            "Recommended next action: review the diff."
        ),
        "should_pass": False,
        "why": (
            "2026-08-01 TEST 3 rerun failure: fresh reconciled Git state was "
            "requested; reusing an earlier turn's remote-branch fact instead "
            "of reverifying it now is the violation."
        ),
    },
    {
        "id": "SV-023",
        "name": "remote-branch state freshly reverified this turn",
        "text": (
            "SESSION SAVED. Normal Save. Worktree and branch confirmed by git "
            "status. Guards: pre-commit guard passed. Koda: stored with the "
            "sifututor project tag. Session Map: current. Active task: none. "
            "Push: verified fresh this turn via git ls-remote; no remote "
            "branch exists yet. Ending state: Save Only. Recommended next "
            "action: review the diff."
        ),
        "should_pass": True,
        "why": "Freshly reverifying remote-branch state this turn satisfies the requirement.",
    },
    {
        "id": "SV-024",
        "name": "Koda fallback used but user told to configure the secret manually",
        "text": (
            "SESSION SAVED. Normal Save. Worktree and branch confirmed by git "
            "status. Guards: pre-commit guard passed. Koda MCP unavailable "
            "this session; used scripts/agent-checks/koda search for a "
            "read-only lookup. Please set KODA_API_KEY in your shell and "
            "restart the agent before the next session. Session Map: current. "
            "Active task: none. Ending state: Save Only. Recommended next "
            "action: review the diff."
        ),
        "should_pass": False,
        "why": (
            "The approved workspace helper owns Koda credential handling. An "
            "agent must not ask Hafiz to configure or expose KODA_API_KEY, even "
            "when it also names a valid helper search."
        ),
    },
    {
        "id": "SV-025",
        "name": "Koda fallback used without exposing credential handling",
        "text": (
            "SESSION SAVED. Normal Save. Worktree and branch confirmed by git "
            "status. Guards: pre-commit guard passed. Koda MCP unavailable "
            "this session; used scripts/agent-checks/koda search for a "
            "read-only lookup. The approved helper handled access internally; "
            "no credential input was requested. Session Map: current. Active "
            "task: none. Ending state: Save Only. Recommended next action: "
            "review the diff."
        ),
        "should_pass": True,
        "why": (
            "The approved fallback should work without asking Hafiz to expose "
            "or manually configure Koda credentials."
        ),
    },
]


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def contains_project_tag(text: str) -> bool:
    """Match a project tag as a token, not as part of another word."""
    return any(
        re.search(rf"(?<![a-z0-9_]){re.escape(marker)}(?![a-z0-9_])", text)
        for marker in PROJECT_TAG_MARKERS
    )


def save_session_violations(case: dict[str, object]) -> list[str]:
    normalized = normalize(str(case["text"]))
    violations = []

    if not any(marker in normalized for marker in SAVE_LEVEL_MARKERS):
        violations.append("missing save level")

    has_ending_label = any(marker in normalized for marker in ENDING_STATE_MARKERS)
    has_ending_value = any(value in normalized for value in ENDING_STATE_VALUES)
    if not (has_ending_label and has_ending_value):
        violations.append("missing honest ending state")

    has_guard_subject = any(marker in normalized for marker in GUARD_SUBJECT_MARKERS)
    has_guard_status = any(marker in normalized for marker in GUARD_STATUS_MARKERS)
    if not (has_guard_subject and has_guard_status):
        violations.append("missing guard/check status (including 'not run')")

    if not any(marker in normalized for marker in REPO_IDENTITY_MARKERS):
        violations.append("missing worktree/branch identity")

    if any(marker in normalized for marker in KODA_WRITE_MARKERS):
        if not contains_project_tag(normalized):
            violations.append("Koda write without a project tag")

    if not any(marker in normalized for marker in NEXT_ACTION_MARKERS):
        violations.append("missing recommended next action")

    if any(marker in normalized for marker in UNRUN_MARKERS) and any(
        marker in normalized for marker in BLANKET_CLAIM_MARKERS
    ):
        violations.append("blanket pass claim despite a named unrun check")

    if any(marker in normalized for marker in SESSION_MAP_NOT_NEEDED_MARKERS):
        if not any(marker in normalized for marker in SESSION_MAP_SEARCH_MARKERS):
            violations.append(
                "Session Map claimed not needed without stating a search of "
                "the relevant session-map location"
            )

    if any(marker in normalized for marker in MEANINGFUL_SAVE_LEVEL_MARKERS):
        if not any(marker in normalized for marker in ACTIVE_TASK_LABEL_MARKERS):
            violations.append("missing explicit active-task status ('active task: ...' or 'active task: none')")

    if any(marker in normalized for marker in MISSION_LEDGER_UNCHECKED_MARKERS):
        violations.append(
            "Mission Ledger reported as not checked/unknown instead of actually "
            "being inspected before reporting"
        )

    if any(marker in normalized for marker in REMOTE_BRANCH_CARRIED_FORWARD_MARKERS):
        violations.append(
            "remote-branch/push state reported as carried-forward/stale instead "
            "of freshly reverified this turn"
        )

    if any(marker in normalized for marker in KODA_UNAVAILABLE_MARKERS):
        helper_negated = any(marker in normalized for marker in KODA_FALLBACK_NEGATION_MARKERS)
        helper_used = any(marker in normalized for marker in KODA_FALLBACK_USE_MARKERS)
        artifact_named = any(marker in normalized for marker in KODA_FALLBACK_ARTIFACT_MARKERS)
        if helper_negated:
            violations.append(
                "Koda unavailable and the workspace helper was explicitly not "
                "used; the corrected adapter requires using the helper's "
                "search/read path for a dry run when it is available/permitted"
            )
        elif not (helper_used or artifact_named):
            violations.append(
                "Koda reported unavailable without evidence the workspace "
                "helper's search/read path was actually used, or naming an "
                "honest fallback artifact/path"
            )

    if any(marker in normalized for marker in KODA_MANUAL_SECRET_MARKERS):
        violations.append(
            "asked the user to configure or expose Koda credentials instead "
            "of letting the approved workspace helper handle access"
        )

    return violations


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


def release_handoff_violations(case: dict[str, object]) -> list[str]:
    text = str(case["text"])
    normalized = normalize(text)
    messages = re.findall(r"```(?:text|plain)?\n(.*?)```", text, flags=re.DOTALL)
    audiences = [str(audience) for audience in case["audiences"]]
    violations = []

    if len(messages) != len(audiences):
        violations.append("expected one copy-ready message per distinct audience")

    if len(audiences) > 1:
        for audience in audiences:
            if f"{audience} message" not in normalized:
                violations.append(f"missing {audience} audience label")

    message_text = normalize(" ".join(messages))
    confirmed_sources = {
        normalize(str(source)) for source in case.get("confirmed_sources", [])
    }
    source_terms = ("tawk", "planner", "email report", "whatsapp report")
    for source in source_terms:
        if source in message_text and source not in confirmed_sources:
            violations.append(f"unconfirmed report source: {source}")

    if "developer" in audiences:
        required_groups = {
            "original PR context": ("your pr", "original pr", "pr #"),
            "review action": ("we reviewed", "reviewed your", "review changed"),
            "review delta": ("we added", "we improved", "review changed"),
            "reason": ("because", "why"),
            "original gap": ("missing", "missed", "incomplete"),
            "final state": ("merged", "deployed", "live"),
            "independent verification": ("independently verify", "please verify"),
            "verification evidence": ("verification evidence", "reply with evidence"),
            "AI learning": ("ai checklist", "ai workflow"),
        }
        violations.extend(
            f"missing {name}"
            for name, markers in required_groups.items()
            if not any(marker in message_text for marker in markers)
        )

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


def today_briefing_violations(text: str) -> list[str]:
    normalized = normalize(text)
    violations = []
    required_groups = (
        "needs hafiz now",
        "waiting on staff",
        "agent can continue",
        "monitor",
        "deferred",
    )
    for group in required_groups:
        if not re.search(rf"(?m)^##\s+{re.escape(group)}\s*$", text, flags=re.IGNORECASE):
            violations.append(f"missing attention group: {group}")

    if "source:" not in normalized:
        violations.append("missing owning source")
    if not any(
        f"confidence: {level}" in normalized
        for level in ("verified", "trusted", "reported", "historical", "unverified")
    ):
        violations.append("missing confidence/evidence label")
    if "freshness:" not in normalized:
        violations.append("missing freshness label")

    if re.search(
        r"\bapprove\s+(?:the\s+)?(?:preparation|read-only|diagnosis|review|plan|planning)\b",
        normalized,
    ):
        violations.append("asks approval for preparation/read-only work")

    has_no_approval_rule = any(
        marker in normalized
        for marker in (
            "read-only preparation does not need approval",
            "read-only diagnosis can continue without approval",
        )
    )
    has_action_boundary = "before the exact" in normalized and any(
        marker in normalized
        for marker in ("write", "release", "production", "access", "destructive")
    )
    if not (has_no_approval_rule and has_action_boundary):
        violations.append("missing honest approval timing rule")
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

    for case in RELEASE_HANDOFF_CASES:
        violations = release_handoff_violations(case)
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

    for case in SAVE_SESSION_CASES:
        violations = save_session_violations(case)
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

    for case in TODAY_BRIEFING_CASES:
        violations = today_briefing_violations(case["text"])
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

    total = (
        len(CASES)
        + len(COPY_READY_CASES)
        + len(RELEASE_HANDOFF_CASES)
        + len(SAVE_SESSION_CASES)
        + len(EXPLANATION_CASES)
        + len(TODAY_BRIEFING_CASES)
    )
    passed = total - len(failures)
    print(f"agent-os-response-shape-runner: {passed}/{total} passed")
    if failures:
        print("failed: " + ", ".join(failures))
        return 1
    return 0


# Semantic verdicts are supplied by a reviewer, never inferred from keywords.
COMMUNICATION_CRITERIA = {
    "C1": "English default; explicit requested language and localized content scoped correctly",
    "C2": "Affected user, known origin, observed/expected behavior, impact and solution before technical evidence",
    "C3": "Appropriate copy-ready audience drafts, including access updates; no invented recipient or sending authority",
    "C4": "Sifututor prose and unchanged authoritative technical identifiers",
    "C5": "Length fits complexity; trivial replies stay short without mandatory headings",
    "C6": "Evidence, gaps and release claims match supplied facts; fixtures are not live compliance proof",
}


def brand_capitalization_violations(text: str) -> list[str]:
    """A narrow spelling check, not proof that technical identifiers are accurate."""
    # Outbound text fences contain human prose. Only labelled code is excluded.
    prose = re.sub(r"```([^\n]*)\n(.*?)```",
                   lambda m: m[2] if m[1].strip() in ("", "text", "plain") else "",
                   text, flags=re.DOTALL)
    prose = re.sub(r"`[^`\n]+`|https?://[^\s<>]+", "", prose)
    if re.search(r"\bSifuTutor\b", prose):
        return ["incorrect brand capitalization in prose"]
    return []


def assess_sample(sample: dict) -> dict:
    """Evaluate opted-in shape checks and report separately recorded manual review."""
    if not isinstance(sample, dict) or any(
        not isinstance(sample.get(key), str) or not sample[key].strip()
        for key in ("text", "context")
    ):
        raise ValueError("sample requires nonempty text and sanitized context")
    checks = sample.get("checks", [])
    available = {"close_out": missing_groups, "copy_ready": copy_ready_violations,
                 "brand": brand_capitalization_violations}
    if not isinstance(checks, list) or any(not isinstance(c, str) or c not in available for c in checks):
        raise ValueError("unknown shape check")
    review = sample.get("review", {})
    if not isinstance(review, dict) or set(review) - set(COMMUNICATION_CRITERIA):
        raise ValueError("unknown manual criterion")
    for entry in review.values():
        if (not isinstance(entry, dict) or entry.get("verdict") not in ("pass", "fail", "not_applicable")
                or not isinstance(entry.get("reason"), str) or not entry["reason"].strip()):
            raise ValueError("manual verdict requires a reason")
    violations = brand_capitalization_violations(sample["text"])
    for check in dict.fromkeys(checks):
        if check != "brand":
            violations.extend(available[check](sample["text"]))
    pending = [key for key in COMMUNICATION_CRITERIA if key not in review]
    failed = [key for key, entry in review.items() if entry["verdict"] == "fail"]
    status = "failed" if violations or failed else "manual_review_required" if pending else "review_recorded"
    return {"status": status, "mechanical_violations": violations,
            "manual_failures": failed, "manual_pending": pending}


def assess_file(path: Path) -> int:
    # No sample text, context, IDs, paths, reviewer notes or raw exceptions in output.
    try:
        samples = json.loads(path.read_text())
        if not isinstance(samples, list) or not samples:
            raise ValueError("expected nonempty sample list")
        results = [assess_sample(sample) for sample in samples]
    except (OSError, UnicodeError, ValueError, TypeError):
        print(json.dumps({"error": "invalid sample input; see documented schema"}))
        return 2
    print(json.dumps({"evidence_kind": "supplied_samples_with_recorded_manual_review",
                      "live_agent_compliance_proven": False, "results": results}, indent=2))
    if any(result["status"] == "failed" for result in results):
        return 1
    return 3 if any(result["manual_pending"] for result in results) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Agent OS response-shape checks.")
    parser.add_argument("--verbose", action="store_true", help="print every response-shape case")
    parser.add_argument("--samples", type=Path, help="assess a sanitized JSON sample list; does not run built-in fixtures")
    args = parser.parse_args()
    if args.samples is not None:
        return assess_file(args.samples)
    return run(verbose=args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
