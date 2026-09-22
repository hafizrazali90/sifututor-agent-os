#!/usr/bin/env python3
"""Bounded worktree cleanup-priority classification (bundle 7, issue #168).

Consumes the JSON shape returned by `worktree-lifecycle.py inventory`
(read `inspect_worktree()` in `scripts/agent-checks/worktree-lifecycle.py`
for the real field names -- this module does not guess them) and, for each
entry, produces a priority classification for human cleanup review:

    preserve                        -- do not touch (deterministic; the
                                        underlying tool already reports an
                                        active lease or a failed safety
                                        check for this entry)
    stale_lease                     -- lease heartbeat is past its own TTL;
                                        needs explicit release/reassignment
    obsolete_task_pointer           -- a recorded task pointer whose own
                                        freshness evidence (an EXISTING
                                        local, safe read path -- see below)
                                        shows the task is shipped/gone
    generated_dependency_blocker    -- clean and merged, but a generated
                                        dependency directory is still
                                        sitting there
    merged_branch                   -- clean and merged, nothing else
                                        notable
    uncertain                       -- does not clearly fit any of the
                                        above; routed through Bundle 1's
                                        decision layer for a non-
                                        authoritative, advisory tie-break,
                                        and always flagged for human
                                        review -- never silently assumed
                                        safe

This module never deletes, prunes, or force-removes anything. Only
`worktree-lifecycle.py` retains that authority, and only via its own
unmodified safety checks. This module is read-only: it classifies and (in
aggregate.py) summarizes; it performs no action of its own. It is an
advisory cleanup-review classifier, not a cleanup tool: it does not solve
worktree cleanup or automatic close-out, and nothing here is wired to any
live command.

## Safe-close requirements preserved

Every requirement `worktree-lifecycle.py` applies before it will touch a
worktree is preserved untouched by this module, because this module never
enforces any of them and never calls the code that does:

  - exact HEAD: the recorded HEAD must still match at action time
  - clean tracked and untracked state: no tracked or untracked changes
  - ignored-file safety: only recognized reproducible ignored directories
    may exist; any other ignored file blocks
  - active-task state: a present, inherited, or invalid active task
    pointer blocks
  - lease ownership: a live or unreadable lease blocks; an expired active
    lease needs an explicit release or reassignment
  - base containment: HEAD must be contained by the configured base ref
  - lock/process checks: a locked worktree, a running process inside it,
    or unverifiable process ownership blocks
  - no deletion based only on age or dormancy: age and inactivity are
    never sufficient on their own

Only `worktree-lifecycle.py` enforces these, through its own unmodified
checks. This module calls none of that tool's mutating commands, spawns no
child process, removes no directory, and has no code path that can reach a
reclaim, close, park, or prune action. A test asserts this against the
module source.

## Determinism and provider use

A deterministic layer, local to this module, always runs first and has
final authority. It never calls a provider. Every entry the underlying
tool itself already reports as under an active lease, or as failing one
of its own safety checks (`classification == "preserve"`, no stale_lease
flag, no obsolete-task evidence), is classified `preserve` without ever
constructing a decision-layer request -- so no provider is ever dispatched
to for it, regardless of what a provider would have guessed.

Only entries that do not clearly match one of the four working buckets
above (today: `prunable_registration`, or any future/unrecognized tool
classification) are routed through Bundle 1's decision layer
(`engine.decide`) for an advisory tie-break. That routing is always
non-authoritative shadow output (Bundle 1's default `authoritative_
decision_types` allowlist is empty and this module never opts in) and the
final classification for that entry stays `uncertain` regardless of what
the provider answers -- the provider's guess is recorded for context only,
never used to silently mark something safe.

The request handed to the decision layer for that tie-break carries
metadata only: the tool's classification label, the branch name, booleans
(stale lease, active task pointer present, inherited task pointer present),
an ignored-blocker count, and the process-check label. It never carries a
lease's `purpose`, its `owner`, the tool's reason prose, recovery commands,
filesystem paths, or anything else a person typed. `build_request_context`
is the single place that shapes it, and `REQUEST_CONTEXT_ALLOWED_KEYS` is
the allowlist a test holds it to. (The inventory entry carries no day
counts today; if one is ever added, it belongs in that allowlist, not in
free text.)

## Obsolete task pointers: why this needs external evidence

`worktree-lifecycle.py`'s own inventory entry only ever records that an
active task pointer exists (field `active_task`); it has no read path,
local or remote, to know whether the referenced task/issue is closed or
merged, and this bundle adds no new lookup to find out. What *is* already
available, locally and safely, is
`scripts/agent-checks/agent_os_active_task_freshness.py`, which reads the
worktree's own task file and can report `stale_completed` (every recorded
step is done or skipped -- the pointer describes shipped work) or
`dangling` (the task file itself is gone). Callers that have already run
that existing tool may pass its per-worktree verdict in via
`task_freshness=`. Without that evidence, this module does not guess: the
entry stays `preserve` and says exactly why.
"""

from __future__ import annotations

import importlib.util
import json
from dataclasses import dataclass
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
DECISION_LAYER_DIR = HERE.parent


def _load(name: str, directory: Path = DECISION_LAYER_DIR):
    sys.path.insert(0, str(directory))
    spec = importlib.util.spec_from_file_location(name, directory / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


provider_base = _load("provider_base")
schema = _load("schema")
engine = _load("engine")

# The decision-layer decision_type this module uses for its "uncertain"
# tie-break. Deliberately not in Bundle 1's pre_policy._RULES and
# deliberately not opted into any config's authoritative_decision_types --
# its answer is always advisory, never authoritative.
DECISION_TYPE = "worktree_triage.uncertain_bucket"

BUCKETS = (
    "preserve",
    "stale_lease",
    "obsolete_task_pointer",
    "generated_dependency_blocker",
    "merged_branch",
    "uncertain",
)

_GENERATED_DEPENDENCY_REASON = "only recognized reproducible ignored directories exist"
_OBSOLETE_FRESHNESS_STATES = frozenset({"stale_completed", "dangling"})

# The only keys a decision-layer request built by this module may carry in
# its context. Metadata only: labels, booleans, a count, and the branch
# name. No lease purpose/owner, no reason prose, no recovery command, no
# filesystem path, nothing a person typed.
REQUEST_CONTEXT_ALLOWED_KEYS = frozenset(
    {
        "tool_classification",  # label reported by worktree-lifecycle.py
        "branch",  # branch name
        "stale_lease",  # bool
        "has_active_task",  # bool (the pointer's text is never included)
        "has_inherited_task_pointer",  # bool (the pointer's text is never included)
        "ignored_blocker_count",  # int
        "process_check",  # label: clear / in_use / not_checked
    }
)

_PROCESS_CHECK_LABELS = frozenset({"clear", "in_use", "not_checked"})
_REQUEST_OPTIONS = ("flag_for_human_review", "treat_as_merged_branch", "treat_as_preserve")


def build_request_context(entry: dict) -> dict:
    """Reduce an inventory entry to the allowlisted metadata the advisory
    tie-break request may carry. Every key is in REQUEST_CONTEXT_ALLOWED_KEYS;
    every value is a label, a bool, an int, or the branch name."""
    ignored_blocker_count = entry.get("ignored_blocker_count")
    process_check = entry.get("process_check")
    metadata = {
        "tool_classification": str(entry.get("classification", "")),
        "branch": str(entry.get("branch", "detached")),
        "stale_lease": entry.get("stale_lease") is True,
        "has_active_task": bool(entry.get("active_task")),
        "has_inherited_task_pointer": bool(entry.get("inherited_task_pointer")),
        "ignored_blocker_count": (
            ignored_blocker_count
            if isinstance(ignored_blocker_count, int) and not isinstance(ignored_blocker_count, bool)
            else 0
        ),
        "process_check": (
            process_check if process_check in _PROCESS_CHECK_LABELS else "not_checked"
        ),
    }
    assert set(metadata) <= REQUEST_CONTEXT_ALLOWED_KEYS
    return metadata


def _render_request_context(metadata: dict) -> str:
    """The schema requires `context` to be text; serialize the allowlisted
    metadata deterministically so nothing outside it can slip in."""
    return "worktree_triage advisory tie-break; metadata=" + json.dumps(
        metadata, sort_keys=True, separators=(",", ":")
    )


@dataclass(frozen=True)
class ClassificationResult:
    """One entry's triage classification.

    `source` names which layer produced the classification:
      "tool_signal"             -- read directly off the inventory entry's
                                    own fields, no inference
      "task_freshness_evidence" -- combined with externally supplied task
                                    freshness evidence
      "deterministic_default"   -- the safe default when evidence is
                                    absent or inconclusive
      "decision_layer"          -- routed through Bundle 1's decision
                                    layer (always non-authoritative here)
    """

    worktree: str
    branch: str
    classification: str
    reason: str
    determinable: bool
    source: str
    provider_dispatched: bool = False
    decision_response: dict | None = None


def _hard_block_preserve(entry: dict) -> ClassificationResult:
    reasons = entry.get("reasons") or []
    return ClassificationResult(
        worktree=entry["worktree"],
        branch=entry.get("branch", "detached"),
        classification="preserve",
        reason="; ".join(reasons) or "tool reports preserve",
        determinable=True,
        source="tool_signal",
    )


def _classify_preserve(entry: dict, task_freshness: str | None) -> ClassificationResult:
    worktree = entry["worktree"]
    branch = entry.get("branch", "detached")

    if entry.get("stale_lease") is True:
        return ClassificationResult(
            worktree=worktree,
            branch=branch,
            classification="stale_lease",
            reason=(
                "tool reports an active lease whose heartbeat has expired; "
                "needs explicit release or reassignment before reclaim"
            ),
            determinable=True,
            source="tool_signal",
        )

    active_task = entry.get("active_task")
    if active_task:
        if task_freshness in _OBSOLETE_FRESHNESS_STATES:
            return ClassificationResult(
                worktree=worktree,
                branch=branch,
                classification="obsolete_task_pointer",
                reason=(
                    f"active task pointer {active_task!r} is recorded, but its own "
                    f"freshness evidence is {task_freshness!r} "
                    "(from the existing agent_os_active_task_freshness.py local "
                    "read path) -- the pointer describes shipped or removed work"
                ),
                determinable=True,
                source="task_freshness_evidence",
            )
        if task_freshness is None:
            reason = (
                f"active task pointer {active_task!r} is recorded; whether it is "
                "closed/merged is not determinable from the inventory entry alone "
                "and no task-freshness evidence was supplied -- preserved rather "
                "than guessed"
            )
        else:
            reason = (
                f"active task pointer {active_task!r} is recorded; its freshness "
                f"evidence ({task_freshness!r}) does not show it is obsolete"
            )
        return ClassificationResult(
            worktree=worktree,
            branch=branch,
            classification="preserve",
            reason=reason,
            determinable=task_freshness is not None,
            source="deterministic_default",
        )

    return _hard_block_preserve(entry)


def _classify_reclaim_candidate(entry: dict) -> ClassificationResult:
    worktree = entry["worktree"]
    branch = entry.get("branch", "detached")
    reasons = entry.get("reasons") or []

    if _GENERATED_DEPENDENCY_REASON in reasons:
        return ClassificationResult(
            worktree=worktree,
            branch=branch,
            classification="generated_dependency_blocker",
            reason=(
                "clean and merged, but a generated dependency directory "
                "(e.g. node_modules/vendor) is present per the tool's own "
                f"{_GENERATED_DEPENDENCY_REASON!r} note and should be cleared "
                "before reclaim"
            ),
            determinable=True,
            source="tool_signal",
        )

    return ClassificationResult(
        worktree=worktree,
        branch=branch,
        classification="merged_branch",
        reason="branch is fully merged/contained by base and the worktree is clean",
        determinable=True,
        source="tool_signal",
    )


def _classify_uncertain(
    entry: dict,
    *,
    provider: object | None,
    config: dict | None,
) -> ClassificationResult:
    worktree = entry["worktree"]
    branch = entry.get("branch", "detached")
    tool_classification = entry.get("classification")

    # Metadata only (see REQUEST_CONTEXT_ALLOWED_KEYS): the tool's reason
    # prose, any lease owner/purpose text, recovery commands and paths are
    # deliberately never placed in the request.
    request = {
        "schema_version": schema.SCHEMA_VERSION,
        "decision_type": DECISION_TYPE,
        "options": list(_REQUEST_OPTIONS),
        "context": _render_request_context(build_request_context(entry)),
        "sensitivity": "low",
    }
    response = engine.decide(request, config=config, provider=provider)

    return ClassificationResult(
        worktree=worktree,
        branch=branch,
        classification="uncertain",
        reason=(
            f"tool classification {tool_classification!r} does not clearly fit "
            "one of the four working buckets; routed to the decision layer for "
            f"an advisory (non-authoritative) tie-break -- suggested "
            f"{response['answer']!r} via provider {response['provider']!r} -- "
            "flagged for human review, never silently assumed safe"
        ),
        determinable=False,
        source="decision_layer",
        provider_dispatched=response["provider"] not in ("pre_policy", "deterministic_fallback"),
        decision_response=response,
    )


def classify_entry(
    entry: dict,
    *,
    task_freshness: str | None = None,
    provider: object | None = None,
    config: dict | None = None,
) -> ClassificationResult:
    """Classify one `worktree-lifecycle.py inventory` entry for cleanup
    review priority. Never deletes, prunes, or mutates anything.

    `task_freshness` is optional external evidence for the entry's
    `active_task` pointer (see module docstring) -- e.g. "stale_completed"
    or "dangling" from the existing agent_os_active_task_freshness.py
    tool. When absent, an active task pointer is never guessed obsolete.

    `provider`/`config` are only ever consulted for entries that reach the
    `uncertain` bucket; every deterministic bucket above short-circuits
    before either is touched.
    """
    if not isinstance(entry, dict) or "worktree" not in entry or "classification" not in entry:
        raise ValueError(
            "worktree_triage.classify_entry: entry does not match the "
            "worktree-lifecycle.py inventory schema (missing 'worktree' or "
            "'classification')"
        )

    tool_classification = entry["classification"]

    if tool_classification == "preserve":
        return _classify_preserve(entry, task_freshness)

    if tool_classification == "reclaim_candidate":
        return _classify_reclaim_candidate(entry)

    return _classify_uncertain(entry, provider=provider, config=config)
