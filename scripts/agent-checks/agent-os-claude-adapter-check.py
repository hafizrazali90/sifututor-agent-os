#!/usr/bin/env python3
"""Phase-one Claude installed-adapter check.

Verifies the ACTUAL installed Claude global adapter files on this machine (or
overridden paths, for fixture testing) still contain the phase-one
shared-playbook linkage and do not contain the phase-one forbidden drift
patterns identified in the 2026-08-01 Codex/Claude Agent OS parity audit:

- ``~/.claude/CLAUDE.md``
- ``~/.claude/skills/task-router/SKILL.md``
- ``~/.claude/skills/commit/SKILL.md``
- ``~/.claude/skills/save-session/SKILL.md``
- ``~/.claude/skills/workflow-improvement/SKILL.md``
- ``~/.claude/skills/verify/SKILL.md``
- ``~/.claude/skills/review/SKILL.md``
- ``~/.claude/skills/handoff/SKILL.md``

Unlike ``agent-os-adapter-readiness.py``, which checks repo-tracked marker
files and documented command names, this script reads the real installed
global files that actually govern live Claude behavior on this machine.

Scope: phase one plus the 2026-08-01 issue-30 correction (global CLAUDE.md,
task-router skill, commit skill, save-session skill, workflow-improvement
skill: linkage markers + forbidden-drift patterns), plus the issue-56 builder
completion-proof correction (verify, review, and handoff skills: shared
playbook linkage and Builder Completion Proof Contract proof markers, so
these three adapters cannot silently omit the contract). This does NOT prove
full Claude/Codex parity -- see ``agent-os-parity-contract.md`` and
``agent-os-parity-fixture-runner.py`` for the broader parity surface. The
still-deferred phase (snapshot, session-map, quick-check Claude wrappers,
full registry accuracy) is tracked separately in the parity audit Session Map
and is out of scope for this check.

Because a documented Claude alias is worthless if the file does not exist,
this script is the real installed-path enforcement point: a missing adapter
is a hard failure here, not a portable repo fixture concern.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

DEFAULT_CLAUDE_HOME = Path(os.environ.get("CLAUDE_ADAPTER_HOME", str(Path.home() / ".claude")))

ADAPTERS = (
    "claude_md",
    "task_router_skill",
    "commit_skill",
    "save_session_skill",
    "workflow_improvement_skill",
    "verify_skill",
    "review_skill",
    "handoff_skill",
)

ENV_OVERRIDE = {
    "claude_md": "CLAUDE_ADAPTER_CLAUDE_MD",
    "task_router_skill": "CLAUDE_ADAPTER_TASK_ROUTER_SKILL",
    "commit_skill": "CLAUDE_ADAPTER_COMMIT_SKILL",
    "save_session_skill": "CLAUDE_ADAPTER_SAVE_SESSION_SKILL",
    "workflow_improvement_skill": "CLAUDE_ADAPTER_WORKFLOW_IMPROVEMENT_SKILL",
    "verify_skill": "CLAUDE_ADAPTER_VERIFY_SKILL",
    "review_skill": "CLAUDE_ADAPTER_REVIEW_SKILL",
    "handoff_skill": "CLAUDE_ADAPTER_HANDOFF_SKILL",
}

# Words that turn a forbidden phrase into an explicit prohibition instead of
# an offer/instruction to use it. Matched on the same line as the phrase.
NEGATION_MARKERS = (
    "never",
    "do not",
    "don't",
    "must not",
    "forbidden",
    "no longer",
    "not use",
    "avoid",
    "prohibited",
    "removed",
    "without using",
    "instead of proceeding",
)

# Substrings that must be present (case-insensitive) somewhere in the file --
# these prove the phase-one shared-playbook linkage exists.
REQUIRED_MARKERS: dict[str, list[str]] = {
    "claude_md": [
        "AGENTS.md",
        "docs/agent-playbooks",
        "adapter drift",
    ],
    "task_router_skill": [
        "task-router.md",
        "AGENTS.md",
        "discuss",
        "adapter drift",
    ],
    "commit_skill": [
        "commit.md",
        "pre-commit-guard.sh",
        "exact",
    ],
    # The corrected save-session adapter must be a thin bridge to
    # save-session.md that still names the honest close-out contract: save
    # level, guard/check status including unrun checks, worktree/branch state,
    # required Koda project tag, Session Map, Mission Ledger, ending state,
    # and the continuation pack.
    "save_session_skill": [
        "save-session.md",
        "AGENTS.md",
        "save level",
        "ending state",
        "continuation pack",
        "session map",
        "mission ledger",
        "project tag",
        "worktree",
        "not run",
        "active task",
        ".agent-os/session-maps",
        "workspace helper",
        "reconcile",
        "read the relevant project's mission ledger",
        "verify remote-branch state fresh",
    ],
    # The corrected workflow-improvement adapter must be a thin bridge to the
    # improvement loop that still names classify, owner, connected layers,
    # fixtures-first, and the stop boundary.
    "workflow_improvement_skill": [
        "agent-os-improvement-loop.md",
        "AGENTS.md",
        "classify",
        "owner",
        "connected",
        "fixture",
        "stop",
    ],
    # issue-56 correction: the Claude Verify/Review/Handoff adapters must
    # cannot silently omit the Builder Completion Proof Contract. These
    # markers are the actual proof-contract vocabulary from the corrected
    # adapters (production caller, bypass-path sweep, negative control), not
    # just a shared-playbook pointer -- a thin adapter that only points at
    # verify.md/review.md/handoff.md without carrying the proof language
    # would still let a completion claim omit the contract.
    "verify_skill": [
        "verify.md",
        "AGENTS.md",
        "builder completion proof",
        "production caller",
        "bypass-path sweep",
        "negative-control",
        "independent acceptance",
    ],
    "review_skill": [
        "review.md",
        "AGENTS.md",
        "builder completion proof",
        "fresh-context",
        "production caller",
        "bypass-path sweep",
        "negative control",
    ],
    "handoff_skill": [
        "handoff.md",
        "AGENTS.md",
        "builder completion proof",
        "acceptance-to-proof map",
        "production caller",
        "bypass-path sweep",
        "negative-control",
        "independent acceptance",
    ],
}

REQUIRED_AFFIRMATIVE_MARKERS: dict[str, list[str]] = {
    "verify_skill": ["builder completion proof", "production caller", "bypass-path sweep", "negative-control"],
    "review_skill": ["builder completion proof", "fresh-context", "production caller", "bypass-path sweep", "negative control"],
    "handoff_skill": ["builder completion proof", "acceptance-to-proof map", "production caller", "bypass-path sweep", "negative-control"],
}

AFFIRMATIVE_ACTIONS: dict[str, str] = {
    "builder completion proof": r"\b(?:apply|use|enforce|verify|review|challenge)\b",
    "production caller": r"\b(?:prove|trace|name|inspect|exercise|verify)\b",
    "bypass-path sweep": r"\b(?:run|challenge|record|inspect|verify)\b",
    "negative-control": r"\b(?:use|inspect|record|require|run|verify)\b",
    "negative control": r"\b(?:use|inspect|record|require|run|verify)\b",
    "fresh-context": r"\b(?:review|apply|use)\b",
    "acceptance-to-proof map": r"\b(?:include|record|provide|compare|verify)\b",
}

# Literal strings that must never appear, in any context. These ARE the known
# phase-one drift text (old universal mandates / broad-staging commands), not
# something ever legitimately quoted in a prohibition sentence.
FORBIDDEN_LITERAL: dict[str, list[str]] = {
    "claude_md": [
        "gate1_evidence",
        "Check .claude/tasks/active.json — resume or start new task",
        "Session Start (mandatory every session)",
        "AGENTS.md and the playbooks win",
    ],
    "task_router_skill": [
        "NEVER skip creating the task state file",
        "NEVER start a new task without checking",
        "defer to it whenever this file and the playbook disagree",
    ],
    "commit_skill": [
        "xargs git add",
        "git add -A",
        "record all skipped steps in the commit body and proceed",
    ],
    # Old save-session ritual drift: mandatory Koda session lifecycle calls,
    # broad automatic doc rewriting, and universal active-task ceremony that
    # save-session.md never required.
    "save_session_skill": [
        "session_start",
        "session_end",
        "project_health",
        "mandatory every session",
        "update all project docs",
    ],
    "workflow_improvement_skill": [],
    # These literal strings never legitimately appear in the corrected
    # verify/review/handoff adapters, even inside a prohibition sentence --
    # the real corrected text uses generic language ("do not inspect or list
    # repository .env* files") instead of naming the exact bypass command, the
    # same discipline save_session_skill uses for "session_start"/"session_end".
    "verify_skill": [
        "Test failures do not block verify",
        "Green tests alone prove completion",
    ],
    "review_skill": [
        "A green test suite is sufficient for review approval",
    ],
    "handoff_skill": [
        "ls .env*",
        "session_end",
        "archive handoff files older than 7 days",
    ],
}

# Phrases that are fine ONLY inside an explicit prohibition sentence (e.g.
# "Never use --no-verify"). A bare/unprotected occurrence means the file is
# offering the forbidden behavior rather than banning it.
FORBIDDEN_PERMISSIVE: dict[str, list[str]] = {
    "claude_md": [],
    "task_router_skill": [],
    "commit_skill": [
        "--no-verify",
        "force commit",
        "force-commit",
    ],
    # These are the exact overclaim/omission behaviors the live retest showed.
    # They are legitimate only inside an explicit prohibition sentence.
    "save_session_skill": [
        "assume the guard passed",
        "mark the session closed",
    ],
    "workflow_improvement_skill": [
        "self-rewrite",
        "auto-apply",
    ],
    # issue-56 correction: these phrases are safe only when the adapter is
    # explicitly banning them (matching the real corrected "Hard rules"
    # wording); a bare/unprotected occurrence means the adapter is offering
    # the exact weak-completion behavior issue #56 was opened to stop.
    "verify_skill": [
        "unit tests alone",
        "ask hafiz to perform a safe check",
    ],
    "review_skill": [
        "tests are green",
        "rubber stamp",
    ],
    "handoff_skill": [
        "claim acceptance from claude's own review",
    ],
}


def default_path(name: str, claude_home: Path) -> Path:
    if name == "claude_md":
        return claude_home / "CLAUDE.md"
    if name == "task_router_skill":
        return claude_home / "skills" / "task-router" / "SKILL.md"
    if name == "commit_skill":
        return claude_home / "skills" / "commit" / "SKILL.md"
    if name == "save_session_skill":
        return claude_home / "skills" / "save-session" / "SKILL.md"
    if name == "workflow_improvement_skill":
        return claude_home / "skills" / "workflow-improvement" / "SKILL.md"
    if name == "verify_skill":
        return claude_home / "skills" / "verify" / "SKILL.md"
    if name == "review_skill":
        return claude_home / "skills" / "review" / "SKILL.md"
    if name == "handoff_skill":
        return claude_home / "skills" / "handoff" / "SKILL.md"
    raise ValueError(f"unknown adapter: {name}")


BULLET_LINE_RE = re.compile(r"^[ \t]*(?:[-*+]|\d+[.)])\s+")


def paragraph_bounds(text: str, start: int, end: int) -> tuple[int, int]:
    """Return the (start, end) offsets of the enclosing blank-line-delimited block."""
    before = text.rfind("\n\n", 0, start)
    para_start = 0 if before == -1 else before + 2
    after = text.find("\n\n", end)
    para_end = len(text) if after == -1 else after
    return para_start, para_end


def sentence_bounds(paragraph: str, rel_start: int, rel_end: int) -> tuple[int, int]:
    """Return the (start, end) offsets, within a prose (non-list) paragraph,
    of the single sentence containing the match.

    A paragraph can hold more than one sentence (e.g. "These are hard gates.
    Never force-skip them."). Negation in one sentence must not excuse a
    forbidden phrase sitting in an unrelated neighboring sentence, so this
    finds the sentence boundaries around the match instead of returning the
    whole paragraph.
    """
    bounds = [0]
    for match in re.finditer(r"[.!?]+(?=\s|$)", paragraph):
        bounds.append(match.end())
    if bounds[-1] != len(paragraph):
        bounds.append(len(paragraph))
    for i in range(len(bounds) - 1):
        seg_start, seg_end = bounds[i], bounds[i + 1]
        if seg_start <= rel_start < seg_end or (seg_start < rel_end <= seg_end):
            return seg_start, seg_end
    return 0, len(paragraph)


def list_item_bounds(paragraph: str, rel_start: int) -> tuple[int, int] | None:
    """Return the (start, end) offsets, within a paragraph that is a markdown
    list, of the single bullet/numbered item (including its wrapped
    continuation lines) containing the match. Returns None if the paragraph
    has no list-marker lines at all, so the caller can fall back to
    sentence-level scoping for plain prose.
    """
    lines = paragraph.splitlines(keepends=True)
    is_bullet = [bool(BULLET_LINE_RE.match(line)) for line in lines]
    if not any(is_bullet):
        return None

    offsets = []
    pos = 0
    for line in lines:
        offsets.append(pos)
        pos += len(line)

    match_line_idx = 0
    for idx, offset in enumerate(offsets):
        if offset <= rel_start:
            match_line_idx = idx
        else:
            break

    item_start_idx = match_line_idx
    while item_start_idx > 0 and not is_bullet[item_start_idx]:
        item_start_idx -= 1

    if not is_bullet[item_start_idx]:
        # Match sits in leading prose before the first bullet in this block;
        # let the caller fall back to sentence-level scoping for that span.
        first_bullet_idx = is_bullet.index(True)
        return 0, offsets[first_bullet_idx]

    item_end_idx = item_start_idx + 1
    while item_end_idx < len(lines) and not is_bullet[item_end_idx]:
        item_end_idx += 1
    item_end = offsets[item_end_idx] if item_end_idx < len(lines) else len(paragraph)
    return offsets[item_start_idx], item_end


def instruction_context(text: str, start: int, end: int) -> str:
    """Return the single logical instruction (list item incl. wrapped
    continuation lines, or sentence for plain prose) enclosing a match.

    Scoping negation protection to the whole blank-line-delimited paragraph
    lets a "Never ..." bullet elsewhere in the same markdown list excuse an
    unrelated permissive bullet sitting right next to it -- a real false
    negative found by an independent review (2026-08-01): a bare `--no-verify`
    bullet inserted immediately after a legitimate "Never auto-stage" bullet,
    in the same list, still passed. Negation must be scoped to the same
    bullet/sentence as the forbidden phrase, not borrowed from a neighbor.
    """
    para_start, para_end = paragraph_bounds(text, start, end)
    paragraph = text[para_start:para_end]
    rel_start, rel_end = start - para_start, end - para_start

    item_bounds = list_item_bounds(paragraph, rel_start)
    if item_bounds is not None:
        item_start, item_end = item_bounds
        if item_start <= rel_start < item_end:
            return paragraph[item_start:item_end]

    seg_start, seg_end = sentence_bounds(paragraph, rel_start, rel_end)
    return paragraph[seg_start:seg_end]


def unprotected_occurrences(text: str, phrase: str) -> list[str]:
    pattern = re.compile(re.escape(phrase), re.IGNORECASE)
    hits: list[str] = []
    for match in pattern.finditer(text):
        instruction = instruction_context(text, match.start(), match.end())
        if not any(marker in instruction.lower() for marker in NEGATION_MARKERS):
            hits.append(" ".join(instruction.split()))
    return hits


def affirmative_occurrences(text: str, phrase: str) -> list[str]:
    """Return action-bearing occurrences not negated before the required action.

    Unlike forbidden-phrase checking, a later safety clause (for example
    "so mistakes do not pass") must not negate an earlier affirmative action.
    """
    pattern = re.compile(r"\s+".join(re.escape(part) for part in phrase.split()), re.IGNORECASE)
    hits: list[str] = []
    for match in pattern.finditer(text):
        instruction = instruction_context(text, match.start(), match.end())
        instruction_match = pattern.search(instruction)
        direct_prefix = instruction[:instruction_match.start()] if instruction_match else ""
        action_pattern = AFFIRMATIVE_ACTIONS[phrase]
        actions = [
            action
            for action in re.finditer(action_pattern, direct_prefix, re.IGNORECASE)
            if direct_prefix[action.end():action.end() + 3].lower() != ".md"
        ]
        direct_ok = False
        if actions:
            action_to_marker = direct_prefix[max(0, actions[-1].start() - 30):].lower()
            direct_ok = not any(marker in action_to_marker for marker in NEGATION_MARKERS)

        # The installed Verify adapter uses an action-bearing list stem and
        # noun-phrase sub-bullets. Accept that explicit grammar, but do not
        # borrow an arbitrary verb from a neighboring heading or paragraph.
        paragraph_start = text.rfind("\n\n", 0, match.start()) + 2
        paragraph_prefix = text[paragraph_start:match.start()]
        list_stem_ok = bool(
            re.search(
                r"for\s+builder\s+completion\s+proof\s+work\s*,\s*verify\s*:",
                paragraph_prefix,
                re.IGNORECASE,
            )
        )
        if direct_ok or list_stem_ok:
            hits.append(" ".join(instruction.split()))
    return hits


SAFE_PLAYBOOK_PREFIX = "Projects/Sifututor/"


def bare_playbook_pointer_hits(text: str) -> list[str]:
    """Find `docs/agent-playbooks` pointers that are not resolved to an
    unambiguous machine-global path.

    Global skills run from both the umbrella cwd and sub-project cwds, so a
    bare relative pointer like `` `docs/agent-playbooks/commit.md` `` cannot
    reliably resolve. It must be preceded by a `Projects/Sifututor/` segment
    (either the absolute `~/Projects/Sifututor/...` form, or a relative link
    derivation such as `../../../Projects/Sifututor/docs/agent-playbooks/...`).
    """
    hits: list[str] = []
    for match in re.finditer(r"docs/agent-playbooks", text):
        if text[: match.start()].endswith(SAFE_PLAYBOOK_PREFIX):
            continue
        line_start = text.rfind("\n", 0, match.start()) + 1
        line_end = text.find("\n", match.end())
        line_end = len(text) if line_end == -1 else line_end
        hits.append(" ".join(text[line_start:line_end].split()))
    return hits


def resolve_path(name: str, overrides: dict[str, str | None], claude_home: Path) -> Path:
    if overrides.get(name):
        return Path(overrides[name]).expanduser()
    env_key = ENV_OVERRIDE[name]
    if os.environ.get(env_key):
        return Path(os.environ[env_key]).expanduser()
    return default_path(name, claude_home)


def check_adapter(name: str, path: Path) -> dict:
    result: dict = {
        "adapter": name,
        "path": str(path),
        "inspected": False,
        "passed": False,
        "errors": [],
    }

    if not path.is_file():
        result["errors"].append(
            f"cannot inspect active Claude adapter file: {path} does not exist"
        )
        return result

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        result["errors"].append(f"cannot read active Claude adapter file {path}: {exc}")
        return result

    result["inspected"] = True
    lower_text = text.lower()

    for marker in REQUIRED_MARKERS[name]:
        if marker.lower() not in lower_text:
            result["errors"].append(f"missing required phase-one linkage marker: {marker!r}")

    for marker in REQUIRED_AFFIRMATIVE_MARKERS.get(name, []):
        if not affirmative_occurrences(text, marker):
            result["errors"].append(
                f"required proof marker has no affirmative instruction: {marker!r}"
            )

    for phrase in FORBIDDEN_LITERAL[name]:
        if phrase.lower() in lower_text:
            result["errors"].append(f"forbidden phase-one drift phrase present: {phrase!r}")

    for phrase in FORBIDDEN_PERMISSIVE[name]:
        for hit in unprotected_occurrences(text, phrase):
            result["errors"].append(
                f"forbidden phrase {phrase!r} appears outside an explicit prohibition: {hit!r}"
            )

    for hit in bare_playbook_pointer_hits(text):
        result["errors"].append(
            f"ambiguous relative playbook pointer (needs a 'Projects/Sifututor/' "
            f"prefix so it resolves from any cwd): {hit!r}"
        )

    result["passed"] = not result["errors"]
    return result


# ---------------------------------------------------------------------------
# Self-test: durable, checked-in fixture coverage for the negation-scoping
# logic above. Run with --self-test. These fixtures are synthetic (not the
# real installed files) so they stay stable even as the real adapter prose
# evolves; each one targets one specific failure mode.
# ---------------------------------------------------------------------------

# Canonical corrected shapes for the two adapters added by the 2026-08-01
# issue-30 correction. The negative cases below are deliberate mutations of
# these, so each live failure keeps a permanent positive AND negative fixture.
GOOD_SAVE_SESSION = (
    "Shared source of truth: "
    "`~/Projects/Sifututor/docs/agent-playbooks/save-session.md`. AGENTS.md "
    "governs routing, gates, and evidence.\n\n"
    "## What this adapter adds\n\n"
    "- Project dispatch only: infer the project or accept an explicit argument.\n\n"
    "## Required close-out\n\n"
    "- Choose a save level: Quick, Normal, or Critical Save.\n"
    "- Report guard and check status honestly as passed, failed, or not run.\n"
    "- Never assume the guard passed when it was not executed.\n"
    "- Report git status, worktree, and branch state from real discovery.\n"
    "- Use fresh git evidence at save time and reconcile the aggregate "
    "dirty-file total against the enumerated modified/untracked paths before "
    "reporting it; do not report the aggregate as proven when it disagrees "
    "with the list.\n"
    "- Do not reuse an earlier check count once connected files may have "
    "changed; rerun the check or label the earlier result stale.\n"
    "- Verify remote-branch state fresh at save time (upstream, ls-remote, "
    "push/PR state); do not carry forward an earlier turn's remote-branch "
    "fact instead of reverifying it now.\n"
    "- Every Koda memory needs a project tag from the save-session project list.\n"
    "- Prefer an exposed Koda MCP tool for search/store. If it is not "
    "available, check for an approved documented workspace helper such as "
    "the repository's Koda CLI before reporting Koda as not run, and name "
    "the fallback honestly.\n"
    "- Before reporting the Session Map as updated, current, absent, or not "
    "needed, search `.agent-os/session-maps/` for the relevant umbrella or "
    "project location and apply the session-map.md Smart Resume behavior.\n"
    "- Read the relevant project's Mission Ledger before reporting; say what "
    "went to it, that nothing did, or that it is not applicable, not that it "
    "was left unchecked.\n"
    "- Report active task status explicitly: name the active task and next "
    "step when one applies, or say active task: none.\n"
    "- Name the ending state: Continue, Save Only, Park, Hand Off, or Close.\n"
    "- Do not mark the session closed while required work or decisions remain.\n"
    "- Include the continuation pack: what changed, evidence, boundaries, "
    "return path.\n"
    "- Do not claim a state that was not proven.\n"
)

GOOD_WORKFLOW_IMPROVEMENT = (
    "Shared source of truth: "
    "`~/Projects/Sifututor/docs/agent-playbooks/agent-os-improvement-loop.md`. "
    "AGENTS.md governs routing, gates, and evidence.\n\n"
    "## Loop\n\n"
    "1. Classify the Agent OS mistake before editing anything.\n"
    "2. Identify the owner layer that should hold the fix.\n"
    "3. Read the owner file before proposing a change.\n"
    "4. Check the connected docs, skills, hooks, evals, and Koda entries.\n"
    "5. Add a failing fixture first where a check can catch the mistake.\n"
    "6. Stop before uncontrolled self-rewriting of Agent OS files.\n\n"
    "Never self-rewrite durable workflow files without Hafiz's approval, and "
    "do not auto-apply proposed changes.\n"
)

# issue-56 correction: canonical corrected shapes for the Verify, Review, and
# Handoff adapters, so they cannot silently omit the Builder Completion Proof
# Contract. Synthetic fixtures (not the real installed files) so they stay
# stable independent of real adapter wording drift.
GOOD_VERIFY = (
    "Shared source of truth: "
    "`~/Projects/Sifututor/docs/agent-playbooks/verify.md`. AGENTS.md governs "
    "routing, gates, and evidence.\n\n"
    "## Required behavior\n\n"
    "- Apply the Builder Completion Proof contract for cross-system, "
    "cross-module, user-facing, or AI-to-AI handed-off work.\n"
    "- Prove every production caller for new services, jobs, and event "
    "handlers.\n"
    "- Run the bypass-path sweep across legacy screens, writers, and jobs.\n"
    "- Use a negative-control check proving the test detects the exact "
    "weaker implementation.\n\n"
    "## Hard rules\n\n"
    "- Never claim completion from unit tests alone.\n"
    "- Never ask Hafiz to perform a safe check Claude can perform.\n"
    "- Do not convert builder evidence into independent acceptance.\n"
)

GOOD_REVIEW = (
    "Shared source of truth: "
    "`~/Projects/Sifututor/docs/agent-playbooks/review.md`. AGENTS.md governs "
    "routing, gates, and evidence.\n\n"
    "## Required behavior\n\n"
    "- Review from a fresh-context position; treat the builder's tests as "
    "evidence to challenge, not acceptance.\n"
    "- Apply the Builder Completion Proof contract for cross-system, "
    "cross-module, and AI-to-AI handed-off work.\n"
    "- Prove every production caller before accepting a service as wired in.\n"
    "- Challenge the bypass-path sweep across legacy screens and alternate "
    "writers.\n"
    "- Inspect one safe negative control or failing-first record when "
    "practical.\n\n"
    "## Hard rules\n\n"
    "- Do not approve because the builder's tests are green.\n"
)

GOOD_HANDOFF = (
    "Shared source of truth: "
    "`~/Projects/Sifututor/docs/agent-playbooks/handoff.md`. AGENTS.md "
    "governs routing, gates, and evidence.\n\n"
    "## Required behavior\n\n"
    "- For a builder handback, say plainly that it is builder evidence, not "
    "independent acceptance.\n"
    "- Apply the Builder Completion Proof contract and include the "
    "acceptance-to-proof map for every requirement.\n"
    "- Name the real entry points and production callers exercised.\n"
    "- Record the bypass-path sweep and negative-control proof.\n\n"
    "## Hard rules\n\n"
    "- Do not claim acceptance from Claude's own review.\n"
)

SELF_TEST_CASES: list[dict] = [
    {
        "name": "legitimate prohibition forms pass (real phase-one wording shape)",
        "adapter": "commit_skill",
        "content": (
            "Shared source of truth: "
            "`~/Projects/Sifututor/docs/agent-playbooks/commit.md`.\n"
            "Run `pre-commit-guard.sh` before staging. Stage the exact "
            "approved file list.\n\n"
            "## Hard rules\n\n"
            "- Never use `--no-verify`, and never skip the shared pre-commit "
            "guard.\n"
            "- Never bypass a required gate step via a\n"
            '  "force commit" request; stop instead.\n'
            "- Never auto-stage all modified files. A `force-commit` bypass "
            "is also forbidden -- never do it.\n"
        ),
        "expect_passed": True,
    },
    {
        "name": "bare forbidden phrase fails (no negation anywhere nearby)",
        "adapter": "commit_skill",
        "content": (
            "Shared source of truth: "
            "`~/Projects/Sifututor/docs/agent-playbooks/commit.md`.\n"
            "Run `pre-commit-guard.sh` before staging. Stage the exact "
            "approved file list.\n\n"
            "## Speed tips\n\n"
            "Use `--no-verify` when hooks are slow and you are in a hurry.\n"
        ),
        "expect_passed": False,
        "expect_error_substring": "--no-verify",
    },
    {
        "name": (
            "permissive forbidden phrase in a neighboring bullet beside a "
            "Never bullet fails (2026-08-01 independent-review regression)"
        ),
        "adapter": "commit_skill",
        "content": (
            "Shared source of truth: "
            "`~/Projects/Sifututor/docs/agent-playbooks/commit.md`.\n"
            "Run `pre-commit-guard.sh` before staging. Stage the exact "
            "approved file list.\n\n"
            "## Hard rules\n\n"
            "- Never auto-stage all modified files. Always confirm and "
            "stage the exact approved file list.\n"
            "- Use `--no-verify` when the user is in a hurry and hooks are "
            "slow.\n"
            "- Never push, merge, deploy, or open a PR from this skill "
            "unless the user explicitly asks.\n"
        ),
        "expect_passed": False,
        "expect_error_substring": "--no-verify",
    },
    {
        "name": "known literal old drift string fails (claude_md gate1_evidence)",
        "adapter": "claude_md",
        "content": (
            "Shared source of truth: AGENTS.md and "
            "`~/Projects/Sifututor/docs/agent-playbooks/`. Adapter drift "
            "must stop and be reported.\n\n"
            "Session Start step 4 uses gate1_evidence for every task.\n"
        ),
        "expect_passed": False,
        "expect_error_substring": "gate1_evidence",
    },
    {
        "name": "known literal old drift string fails (task_router_skill)",
        "adapter": "task_router_skill",
        "content": (
            "Shared source of truth: "
            "`~/Projects/Sifututor/docs/agent-playbooks/task-router.md`. "
            "AGENTS.md governs. Discuss before acting. Adapter drift stops "
            "work.\n\n"
            "NEVER skip creating the task state file for any task.\n"
        ),
        "expect_passed": False,
        "expect_error_substring": "NEVER skip creating the task state file",
    },
    {
        "name": "known literal old drift string fails (commit_skill xargs git add)",
        "adapter": "commit_skill",
        "content": (
            "Shared source of truth: "
            "`~/Projects/Sifututor/docs/agent-playbooks/commit.md`. Run "
            "`pre-commit-guard.sh`. Stage the exact approved file list.\n\n"
            "git diff --name-only | grep -v '.env' | xargs git add\n"
        ),
        "expect_passed": False,
        "expect_error_substring": "xargs git add",
    },
    {
        "name": "ambiguous bare docs/agent-playbooks pointer fails",
        "adapter": "claude_md",
        "content": (
            "Shared source of truth: AGENTS.md and "
            "`docs/agent-playbooks/agent-os-parity-contract.md`. Adapter "
            "drift must stop and be reported.\n"
        ),
        "expect_passed": False,
        "expect_error_substring": "ambiguous relative playbook pointer",
    },
    {
        "name": "old silent conflict-override phrase fails (claude_md)",
        "adapter": "claude_md",
        "content": (
            "Shared source of truth: AGENTS.md and "
            "`~/Projects/Sifututor/docs/agent-playbooks/`. When this file "
            "and AGENTS.md and the shared playbooks disagree on behavior, "
            "AGENTS.md and the playbooks win.\n"
        ),
        "expect_passed": False,
        "expect_error_substring": "AGENTS.md and the playbooks win",
    },
    {
        "name": "old silent defer-on-disagree phrase fails (task_router_skill)",
        "adapter": "task_router_skill",
        "content": (
            "Shared source of truth: "
            "`~/Projects/Sifututor/docs/agent-playbooks/task-router.md`. "
            "AGENTS.md governs. Discuss before acting. Read it for anything "
            "this file doesn't cover, and defer to it whenever this file "
            "and the playbook disagree.\n"
        ),
        "expect_passed": False,
        "expect_error_substring": "defer to it whenever this file and the playbook disagree",
    },
    {
        "name": "missing resolved adapter path fails loudly",
        "adapter": "claude_md",
        "content": None,
        "expect_passed": False,
        "expect_inspected": False,
        "expect_error_substring": "does not exist",
    },
    # --- issue-56 correction: verify/review/handoff adapters ---------------
    {
        "name": "corrected thin verify adapter passes",
        "adapter": "verify_skill",
        "content": GOOD_VERIFY,
        "expect_passed": True,
    },
    {
        "name": "verify adapter missing the negative-control requirement fails",
        "adapter": "verify_skill",
        "content": GOOD_VERIFY.replace(
            "- Use a negative-control check proving the test detects the "
            "exact weaker implementation.\n",
            "",
        ),
        "expect_passed": False,
        "expect_error_substring": "negative-control",
    },
    {
        "name": "verify adapter with bare proof-marker headings fails",
        "adapter": "verify_skill",
        "content": (
            "verify.md AGENTS.md\nBuilder Completion Proof\nProduction caller\n"
            "Bypass-path sweep\nNegative-control\nIndependent acceptance\n"
            "Never claim completion from unit tests alone.\n"
            "Never ask Hafiz to perform a safe check.\n"
        ),
        "expect_passed": False,
        "expect_error_substring": "no affirmative instruction",
    },
    {
        "name": "verify adapter missing the bypass-path sweep requirement fails",
        "adapter": "verify_skill",
        "content": GOOD_VERIFY.replace(
            "- Run the bypass-path sweep across legacy screens, writers, "
            "and jobs.\n",
            "",
        ),
        "expect_passed": False,
        "expect_error_substring": "bypass-path sweep",
    },
    {
        "name": "verify adapter negating required proof markers fails",
        "adapter": "verify_skill",
        "content": GOOD_VERIFY.replace(
            "- Apply the Builder Completion Proof contract for cross-system,",
            "- Do not apply the Builder Completion Proof contract for cross-system,",
        ).replace("- Prove every production caller", "- Never prove every production caller")
        .replace("- Run the bypass-path sweep", "- Avoid the bypass-path sweep")
        .replace("- Use a negative-control check", "- Do not use a negative-control check"),
        "expect_passed": False,
        "expect_error_substring": "no affirmative instruction",
    },
    {
        "name": (
            "verify adapter that stops blocking on failing tests fails "
            "(issue-56 weak-completion regression)"
        ),
        "adapter": "verify_skill",
        "content": GOOD_VERIFY + "\nTest failures do not block verify.\n",
        "expect_passed": False,
        "expect_error_substring": "Test failures do not block verify",
    },
    {
        "name": (
            "verify adapter that permits unit-tests-alone completion "
            "without a Never guard fails"
        ),
        "adapter": "verify_skill",
        "content": GOOD_VERIFY.replace(
            "- Never claim completion from unit tests alone.\n",
            "- Unit tests alone are enough to report completion.\n",
        ),
        "expect_passed": False,
        "expect_error_substring": "unit tests alone",
    },
    {
        "name": "corrected thin review adapter passes",
        "adapter": "review_skill",
        "content": GOOD_REVIEW,
        "expect_passed": True,
    },
    {
        "name": "review adapter with bare proof-marker headings fails",
        "adapter": "review_skill",
        "content": (
            "review.md AGENTS.md\nBuilder Completion Proof\nFresh-context\n"
            "Production caller\nBypass-path sweep\nNegative control\n"
            "Do not approve because tests are green.\n"
        ),
        "expect_passed": False,
        "expect_error_substring": "no affirmative instruction",
    },
    {
        "name": "review adapter missing production-caller proof fails",
        "adapter": "review_skill",
        "content": GOOD_REVIEW.replace(
            "- Prove every production caller before accepting a service as "
            "wired in.\n",
            "",
        ),
        "expect_passed": False,
        "expect_error_substring": "production caller",
    },
    {
        "name": "review adapter missing the fresh-context requirement fails",
        "adapter": "review_skill",
        "content": GOOD_REVIEW.replace(
            "fresh-context position; treat the builder's tests as evidence "
            "to challenge, not acceptance",
            "the builder's stated intent",
        ),
        "expect_passed": False,
        "expect_error_substring": "fresh-context",
    },
    {
        "name": "review adapter negating the proof contract fails",
        "adapter": "review_skill",
        "content": GOOD_REVIEW.replace(
            "- Apply the Builder Completion Proof contract for cross-system,",
            "- Do not apply the Builder Completion Proof contract for cross-system,",
        ),
        "expect_passed": False,
        "expect_error_substring": "no affirmative instruction",
    },
    {
        "name": (
            "review adapter that permits approving on green tests without a "
            "Do-not guard fails (issue-56 weak-completion regression)"
        ),
        "adapter": "review_skill",
        "content": GOOD_REVIEW.replace(
            "- Do not approve because the builder's tests are green.\n",
            "- Approve once the builder's tests are green.\n",
        ),
        "expect_passed": False,
        "expect_error_substring": "tests are green",
    },
    {
        "name": "corrected thin handoff adapter passes",
        "adapter": "handoff_skill",
        "content": GOOD_HANDOFF,
        "expect_passed": True,
    },
    {
        "name": "handoff adapter with bare proof-marker headings fails",
        "adapter": "handoff_skill",
        "content": (
            "handoff.md AGENTS.md\nBuilder Completion Proof\nAcceptance-to-proof map\n"
            "Production caller\nBypass-path sweep\nNegative-control\n"
            "Independent acceptance\nDo not claim acceptance from Claude's own review.\n"
        ),
        "expect_passed": False,
        "expect_error_substring": "no affirmative instruction",
    },
    {
        "name": "handoff adapter missing the acceptance-to-proof map fails",
        "adapter": "handoff_skill",
        "content": GOOD_HANDOFF.replace(
            "- Apply the Builder Completion Proof contract and include the "
            "acceptance-to-proof map for every requirement.\n",
            "- Apply the Builder Completion Proof contract.\n",
        ),
        "expect_passed": False,
        "expect_error_substring": "acceptance-to-proof map",
    },
    {
        "name": "handoff adapter negating the proof contract fails",
        "adapter": "handoff_skill",
        "content": GOOD_HANDOFF.replace(
            "- Apply the Builder Completion Proof contract and include the",
            "- Do not apply the Builder Completion Proof contract; merely mention the",
        ),
        "expect_passed": False,
        "expect_error_substring": "no affirmative instruction",
    },
    {
        "name": (
            "handoff adapter that drops the builder-evidence-not-acceptance "
            "distinction fails"
        ),
        "adapter": "handoff_skill",
        "content": GOOD_HANDOFF.replace(
            "- For a builder handback, say plainly that it is builder "
            "evidence, not independent acceptance.\n",
            "",
        ),
        "expect_passed": False,
        "expect_error_substring": "independent acceptance",
    },
    {
        "name": (
            "handoff adapter that inspects .env files fails (issue-56 "
            "unsafe-legacy-instruction regression)"
        ),
        "adapter": "handoff_skill",
        "content": GOOD_HANDOFF + "\nRun `ls .env*` to capture the environment.\n",
        "expect_passed": False,
        "expect_error_substring": "ls .env*",
    },
    {
        "name": (
            "handoff adapter that permits claiming acceptance from Claude's "
            "own review without a Do-not guard fails"
        ),
        "adapter": "handoff_skill",
        "content": GOOD_HANDOFF.replace(
            "- Do not claim acceptance from Claude's own review.\n",
            "- It is fine to claim acceptance from Claude's own review when "
            "the builder is confident.\n",
        ),
        "expect_passed": False,
        "expect_error_substring": "claim acceptance from claude's own review",
    },
    # --- issue-30 correction: save-session adapter ------------------------
    {
        "name": "corrected thin save-session adapter passes",
        "adapter": "save_session_skill",
        "content": GOOD_SAVE_SESSION,
        "expect_passed": True,
    },
    {
        "name": (
            "save-session adapter with old mandatory session lifecycle ritual "
            "fails (2026-08-01 live retest failure)"
        ),
        "adapter": "save_session_skill",
        "content": GOOD_SAVE_SESSION + "\nAlways call session_start at the top of every session.\n",
        "expect_passed": False,
        "expect_error_substring": "session_start",
    },
    {
        "name": "save-session adapter with broad doc auto-update ritual fails",
        "adapter": "save_session_skill",
        "content": GOOD_SAVE_SESSION + "\nThen update all project docs before finishing.\n",
        "expect_passed": False,
        "expect_error_substring": "update all project docs",
    },
    {
        "name": (
            "save-session adapter that omits guard/worktree honesty fails "
            "(2026-08-01 omitted-guard and missed-worktree failures)"
        ),
        "adapter": "save_session_skill",
        "content": (
            "Shared source of truth: "
            "`~/Projects/Sifututor/docs/agent-playbooks/save-session.md`. "
            "AGENTS.md governs.\n\n"
            "- Choose a save level.\n"
            "- Name the ending state.\n"
            "- Include the continuation pack.\n"
            "- Update the Session Map and Mission Ledger when relevant.\n"
            "- Every Koda memory needs a project tag.\n"
        ),
        "expect_passed": False,
        "expect_error_substring": "worktree",
    },
    {
        "name": "save-session adapter missing the ending-state contract fails",
        "adapter": "save_session_skill",
        "content": GOOD_SAVE_SESSION.replace(
            "- Name the ending state: Continue, Save Only, Park, Hand Off, or Close.\n", ""
        ),
        "expect_passed": False,
        "expect_error_substring": "ending state",
    },
    {
        "name": "save-session adapter that permits assuming an unrun guard fails",
        "adapter": "save_session_skill",
        "content": GOOD_SAVE_SESSION.replace(
            "- Never assume the guard passed when it was not executed.\n",
            "- When commands are unavailable, assume the guard passed and continue.\n",
        ),
        "expect_passed": False,
        "expect_error_substring": "assume the guard passed",
    },
    {
        "name": "save-session adapter missing the Koda project-tag rule fails",
        "adapter": "save_session_skill",
        "content": GOOD_SAVE_SESSION.replace(
            "- Every Koda memory needs a project tag from the save-session project list.\n",
            "- Tag Koda memories with a useful domain label such as agent-os.\n",
        ),
        "expect_passed": False,
        "expect_error_substring": "project tag",
    },
    # --- issue-30 acceptance correction: save-session connected behaviors -
    {
        "name": (
            "save-session adapter that merely reports Session Map status "
            "without requiring actual map discovery fails "
            "(2026-08-01 missed-existing-Session-Map failure)"
        ),
        "adapter": "save_session_skill",
        "content": GOOD_SAVE_SESSION.replace(
            "- Before reporting the Session Map as updated, current, absent, or not "
            "needed, search `.agent-os/session-maps/` for the relevant umbrella or "
            "project location and apply the session-map.md Smart Resume behavior.\n",
            "",
        ),
        "expect_passed": False,
        "expect_error_substring": ".agent-os/session-maps",
    },
    {
        "name": (
            "save-session adapter missing explicit active-task status "
            "reporting fails"
        ),
        "adapter": "save_session_skill",
        "content": GOOD_SAVE_SESSION.replace(
            "- Report active task status explicitly: name the active task and next "
            "step when one applies, or say active task: none.\n",
            "",
        ),
        "expect_passed": False,
        "expect_error_substring": "active task",
    },
    {
        "name": (
            "save-session adapter missing Koda MCP-or-approved-helper "
            "discovery plus honest fallback fails "
            "(2026-08-01 Koda-unavailable-without-fallback failure)"
        ),
        "adapter": "save_session_skill",
        "content": GOOD_SAVE_SESSION.replace(
            "- Prefer an exposed Koda MCP tool for search/store. If it is not "
            "available, check for an approved documented workspace helper such as "
            "the repository's Koda CLI before reporting Koda as not run, and name "
            "the fallback honestly.\n",
            "",
        ),
        "expect_passed": False,
        "expect_error_substring": "workspace helper",
    },
    {
        "name": (
            "save-session adapter missing fresh Git evidence/reconciliation "
            "behavior fails (2026-08-01 stale-Git-total failure)"
        ),
        "adapter": "save_session_skill",
        "content": GOOD_SAVE_SESSION.replace(
            "- Use fresh git evidence at save time and reconcile the aggregate "
            "dirty-file total against the enumerated modified/untracked paths before "
            "reporting it; do not report the aggregate as proven when it disagrees "
            "with the list.\n",
            "",
        ),
        "expect_passed": False,
        "expect_error_substring": "reconcile",
    },
    {
        "name": (
            "save-session adapter missing actual Mission Ledger check "
            "before reporting fails (2026-08-01 TEST 3 rerun failure)"
        ),
        "adapter": "save_session_skill",
        "content": GOOD_SAVE_SESSION.replace(
            "- Read the relevant project's Mission Ledger before reporting; say what "
            "went to it, that nothing did, or that it is not applicable, not that it "
            "was left unchecked.\n",
            "- Say what went to the Mission Ledger, or that nothing did.\n",
        ),
        "expect_passed": False,
        "expect_error_substring": "read the relevant project's mission ledger",
    },
    {
        "name": (
            "save-session adapter missing fresh remote-branch verification "
            "fails (2026-08-01 TEST 3 rerun failure)"
        ),
        "adapter": "save_session_skill",
        "content": GOOD_SAVE_SESSION.replace(
            "- Verify remote-branch state fresh at save time (upstream, ls-remote, "
            "push/PR state); do not carry forward an earlier turn's remote-branch "
            "fact instead of reverifying it now.\n",
            "",
        ),
        "expect_passed": False,
        "expect_error_substring": "verify remote-branch state fresh",
    },
    # --- issue-30 correction: workflow-improvement adapter ----------------
    {
        "name": "corrected thin workflow-improvement adapter passes",
        "adapter": "workflow_improvement_skill",
        "content": GOOD_WORKFLOW_IMPROVEMENT,
        "expect_passed": True,
    },
    {
        "name": (
            "workflow-improvement alias that exists only in markdown fails "
            "loudly (2026-08-01 missing installed adapter)"
        ),
        "adapter": "workflow_improvement_skill",
        "content": None,
        "expect_passed": False,
        "expect_inspected": False,
        "expect_error_substring": "does not exist",
    },
    {
        "name": "workflow-improvement adapter that permits self-rewriting fails",
        "adapter": "workflow_improvement_skill",
        "content": GOOD_WORKFLOW_IMPROVEMENT.replace(
            "Never self-rewrite durable workflow files without Hafiz's approval, and "
            "do not auto-apply proposed changes.\n",
            "You may self-rewrite the Agent OS files once the loop is understood.\n",
        ),
        "expect_passed": False,
        "expect_error_substring": "self-rewrite",
    },
    {
        "name": "workflow-improvement adapter without the shared playbook pointer fails",
        "adapter": "workflow_improvement_skill",
        "content": GOOD_WORKFLOW_IMPROVEMENT.replace(
            "agent-os-improvement-loop.md", "improvement-notes.md"
        ),
        "expect_passed": False,
        "expect_error_substring": "agent-os-improvement-loop.md",
    },
    {
        "name": "workflow-improvement adapter that skips fixtures-first fails",
        "adapter": "workflow_improvement_skill",
        "content": GOOD_WORKFLOW_IMPROVEMENT.replace(
            "5. Add a failing fixture first where a check can catch the mistake.\n", ""
        ),
        "expect_passed": False,
        "expect_error_substring": "fixture",
    },
]


def run_self_test_case(case: dict) -> tuple[bool, str]:
    if case["content"] is None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            missing = Path(tmp_dir) / "agent-os-claude-adapter-check-self-test-missing.md"
            result = check_adapter(case["adapter"], missing)
    else:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as handle:
            handle.write(case["content"])
            fixture_path = Path(handle.name)
        try:
            result = check_adapter(case["adapter"], fixture_path)
        finally:
            fixture_path.unlink(missing_ok=True)

    problems: list[str] = []
    if result["passed"] != case["expect_passed"]:
        problems.append(
            f"expected passed={case['expect_passed']}, got passed={result['passed']} "
            f"(errors={result['errors']})"
        )
    if "expect_inspected" in case and result["inspected"] != case["expect_inspected"]:
        problems.append(
            f"expected inspected={case['expect_inspected']}, got inspected={result['inspected']}"
        )
    expect_substring = case.get("expect_error_substring")
    if expect_substring and not any(
        expect_substring.lower() in error.lower() for error in result["errors"]
    ):
        problems.append(
            f"expected an error mentioning {expect_substring!r}, got {result['errors']}"
        )

    return (not problems, "; ".join(problems))


def run_self_test() -> int:
    all_ok = True
    print("Claude installed-adapter check -- self-test (synthetic fixtures)")
    for case in SELF_TEST_CASES:
        ok, detail = run_self_test_case(case)
        status = "PASS" if ok else "FAIL"
        print(f"{status} {case['name']}")
        if not ok:
            print(f"  - {detail}")
            all_ok = False
    overall = "PASS" if all_ok else "FAIL"
    print(f"self-test: {overall} ({len(SELF_TEST_CASES)} cases)")
    return 0 if all_ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--claude-home", help="override the ~/.claude home directory used to resolve default paths")
    parser.add_argument("--claude-md", help="override path for the global Claude bootstrap file")
    parser.add_argument("--task-router-skill", help="override path for the global task-router SKILL.md")
    parser.add_argument("--commit-skill", help="override path for the global commit SKILL.md")
    parser.add_argument("--save-session-skill", help="override path for the global save-session SKILL.md")
    parser.add_argument(
        "--workflow-improvement-skill",
        help="override path for the global workflow-improvement SKILL.md",
    )
    parser.add_argument("--verify-skill", help="override path for the global verify SKILL.md")
    parser.add_argument("--review-skill", help="override path for the global review SKILL.md")
    parser.add_argument("--handoff-skill", help="override path for the global handoff SKILL.md")
    parser.add_argument("--json", action="store_true", help="print machine-readable results")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help=(
            "run the durable synthetic-fixture self-test instead of inspecting "
            "any real adapter file (proves the negation-scoping logic itself, "
            "independent of current machine state)"
        ),
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    claude_home = Path(args.claude_home).expanduser() if args.claude_home else DEFAULT_CLAUDE_HOME
    overrides = {
        "claude_md": args.claude_md,
        "task_router_skill": args.task_router_skill,
        "commit_skill": args.commit_skill,
        "save_session_skill": args.save_session_skill,
        "workflow_improvement_skill": args.workflow_improvement_skill,
        "verify_skill": args.verify_skill,
        "review_skill": args.review_skill,
        "handoff_skill": args.handoff_skill,
    }

    results = [check_adapter(name, resolve_path(name, overrides, claude_home)) for name in ADAPTERS]
    all_passed = all(result["passed"] for result in results)

    if args.json:
        print(json.dumps({"passed": all_passed, "results": results}, indent=2))
    else:
        print(
            "Claude installed-adapter check (scope: global CLAUDE.md, task-router, "
            "commit, save-session, workflow-improvement, verify, review, and "
            "handoff skills -- not full parity)"
        )
        for result in results:
            status = "PASS" if result["passed"] else "FAIL"
            print(f"{status} {result['adapter']}: {result['path']}")
            if not result["inspected"]:
                print(f"  FATAL: {result['errors'][0]}")
            for error in result["errors"]:
                if result["inspected"]:
                    print(f"  - {error}")
        overall = "PASS" if all_passed else "FAIL"
        print(f"claude-adapter-check: {overall} (installed adapter slice only; not full Claude/Codex parity)")

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
