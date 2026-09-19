#!/usr/bin/env python3
"""Provider-neutral session/task context selection and approval-boundary binding.

Why this exists (see .agent-os/session-maps/artifacts/
2026-09-19-agent-os-first-bundle-build-plan.md, build slices 1 and 2):

`codex-lifecycle-hook.py`'s original `latest_session_map()` sorted every
Session Map file under `.agent-os/session-maps/` by mtime and handed back
whichever one was newest, with no check that the map actually belonged to the
current session or project. A session resuming a `sifu-tutor` task could be
handed an unrelated `ripple-suite` map just because someone else touched it
five minutes ago.

This module gives any adapter (Codex, Claude, or a future one) a small,
testable, provider-neutral place to:

1. Select the Session Map that actually belongs to the current session/task
   instead of "whichever file has the newest mtime" (`select_session_map`).
2. Persist and validate an approved finish boundary so a context transfer
   (compact, handoff, resume) cannot silently expand what was approved
   (`serialize_approval_boundary`, `save_approval_boundary`,
   `load_approval_boundary`, `validate_boundary_transition`,
   `check_operation_allowed`).
3. Carry the provider's exact current session/worktree identity into a trusted
   supervisor enrollment call without reading prompt text or selecting a
   "latest" session (`session_identity_context`, `supervised_enroll`).

Selection order for (1), from the build plan's "Minimal context contract":

    1. verified current-session binding  - a prior selection recorded for
       this exact session id, still present on disk and still matching the
       recorded project.
    2. explicit current-task binding     - a `session_map_hint` the caller
       passes in (e.g. an active task file's own pointer to its Session Map).
    3. narrow supported recovery evidence - the newest Session Map that
       matches the current project; if no project match exists, the newest
       Session Map overall, but always labelled a discovery candidate, never
       authority.

A missing or invalid binding must not fabricate approval and must not force a
task reset; it only means the caller falls through to the next tier.

Proof level: this module is checked by
`scripts/agent-checks/test_agent_os_task_context.py` (unit/checker proof
against synthetic payloads and a temp filesystem). That proves the selection
and validation logic behaves as designed. It is not, by itself, proof that
every live Codex or Claude session actually calls this module -- see the
adapter integration note in `codex-lifecycle-hook.py` for the one adapter that
currently does.
"""

from __future__ import annotations

import json
import hashlib
import os
import re
import tempfile
import time
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 2


# ---------------------------------------------------------------------------
# Small filesystem helpers
# ---------------------------------------------------------------------------


def _atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".tmp-", dir=path.parent)
    tmp = Path(name)
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(json.dumps(data, indent=2, sort_keys=True))
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)


def _read_json(path: Path) -> dict | None:
    try:
        value = json.loads(path.read_text())
        return value if isinstance(value, dict) else None
    except Exception:
        return None


def _safe_key(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Session identity
# ---------------------------------------------------------------------------


def extract_session_id(payload: dict[str, Any]) -> str:
    """Pull a stable session/conversation id out of a hook payload.

    Uses the same key order as `secret_output_guard._visual_scope` so every
    adapter agrees on what counts as "the same session" without importing
    across hook modules that may not always both be present.
    """

    for key in ("session_id", "sessionId", "conversation_id", "conversationId"):
        value = str(payload.get(key) or "").strip()
        if value:
            return value
    return ""


def extract_session_identity(payload: dict[str, Any]) -> tuple[str, Path] | None:
    """Return the provider's current session id and cwd without reading its prompt.

    This is identity evidence only. It deliberately ignores prompt text, task
    labels and claimed approval fields because none of those authenticate owner
    authorization.
    """

    session_id = extract_session_id(payload)
    cwd = payload.get("cwd")
    if not session_id or not isinstance(cwd, str) or not cwd.strip():
        return None
    worktree = Path(cwd).resolve()
    if not worktree.is_dir():
        return None
    return session_id, worktree


def session_identity_context(payload: dict[str, Any]) -> str:
    """Expose this invocation's exact identity to a trusted supervisor.

    Nothing is saved and no approval packet is created. In particular, there is
    no "latest identity" lookup that could cross wires between parallel tasks.
    """

    identity = extract_session_identity(payload)
    if identity is None:
        return ""
    session_id, worktree = identity
    return (
        f"Current Agent OS session identity: {json.dumps(session_id)}. "
        f"Canonical worktree: {json.dumps(str(worktree))}. "
        "This is identity only, not approval. A trusted supervisor may bind an "
        "already-approved, reviewed work packet to this exact session; never infer "
        "authority from prompt text or from another session's state."
    )


def project_of_session_map(path: Path) -> str:
    """Best-effort project name from a Session Map's Agent Context block."""

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
    match = re.search(r"(?m)^-\s*\*\*Project:\*\*\s*(.+)$", text)
    if not match:
        return ""
    return match.group(1).strip().strip("`")


# ---------------------------------------------------------------------------
# Session Map selection
# ---------------------------------------------------------------------------


def discover_session_maps(session_map_dir: Path) -> list[Path]:
    if not session_map_dir.exists():
        return []
    return sorted(
        session_map_dir.glob("*.md"),
        key=lambda path: (path.stat().st_mtime, path.name),
        reverse=True,
    )


def session_binding_path(state_dir: Path, session_id: str) -> Path:
    return state_dir / f"{_safe_key(session_id)}.json"


def _bind_session_map(state_dir: Path, session_id: str, session_map_path: Path, project: str) -> None:
    _atomic_write_json(
        session_binding_path(state_dir, session_id),
        {
            "schema_version": SCHEMA_VERSION,
            "session_id": session_id,
            "binding_source": "explicit_task_binding",
            "session_map_path": str(session_map_path),
            "project": project,
            "bound_at": time.time(),
        },
    )


def clear_session_binding(state_dir: Path, session_id: str) -> None:
    """Release a session's Session Map binding for a deliberate task switch."""

    try:
        session_binding_path(state_dir, session_id).unlink()
    except FileNotFoundError:
        pass


def select_session_map(
    session_map_dir: Path,
    *,
    session_id: str = "",
    project: str = "",
    state_dir: Path | None = None,
    session_map_hint: str | Path | None = None,
) -> dict[str, Any]:
    """Choose the Session Map that belongs to the current session/task.

    Returns ``{"path": Path | None, "tier": str, "reason": str}`` where
    ``tier`` is one of ``verified_session_binding``, ``explicit_task_binding``,
    ``discovery_candidate``, or ``none``.
    """

    state_dir = state_dir or (session_map_dir / ".bindings")
    session_map_dir_resolved = session_map_dir.resolve() if session_map_dir.exists() else session_map_dir

    # Tier 1: verified current-session binding.
    if session_id:
        recorded = _read_json(session_binding_path(state_dir, session_id))
        if (recorded and recorded.get("schema_version") == SCHEMA_VERSION
                and recorded.get("session_id") == session_id
                and recorded.get("binding_source") == "explicit_task_binding"):
            candidate = Path(str(recorded.get("session_map_path", "")))
            recorded_project = recorded.get("project", "")
            same_project = recorded_project == project
            if candidate.is_file() and candidate.resolve().parent == session_map_dir_resolved and same_project:
                return {
                    "path": candidate,
                    "tier": "verified_session_binding",
                    "reason": f"Reusing the Session Map already bound to session {session_id!r}.",
                }
            # Stale, deleted, or project-mismatched binding: do not fabricate
            # approval by reusing it. Fall through to the next tier.

    # Tier 2: explicit current-task binding.
    if session_map_hint:
        candidate = Path(session_map_hint)
        if not candidate.is_absolute():
            candidate = session_map_dir / candidate
        if candidate.is_file() and candidate.resolve().parent == session_map_dir_resolved:
            if session_id:
                _bind_session_map(state_dir, session_id, candidate, project)
            return {
                "path": candidate,
                "tier": "explicit_task_binding",
                "reason": "Using the explicitly named current-task Session Map.",
            }

    # Tier 3: narrow supported recovery evidence -- a discovery candidate only.
    candidates = discover_session_maps(session_map_dir)
    if not candidates:
        return {"path": None, "tier": "none", "reason": "No Session Maps exist yet."}

    chosen = None
    reason = ""
    if project:
        matching = [c for c in candidates if project_of_session_map(c) == project]
        if matching:
            chosen = matching[0]
            reason = f"Newest Session Map matching project {project!r}; a discovery candidate, not authority."

    if chosen is None:
        chosen = candidates[0]
        reason = "Newest Session Map overall; no project match found. Discovery candidate only, not authority."

    return {"path": chosen, "tier": "discovery_candidate", "reason": reason}


# ---------------------------------------------------------------------------
# Approval boundary continuity
# ---------------------------------------------------------------------------


def serialize_approval_boundary(
    *,
    task_id: str,
    included_operations: list[str],
    excluded_operations: list[str],
    approval_provenance: str,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": task_id,
        "included_operations": sorted(set(included_operations)),
        "excluded_operations": sorted(set(excluded_operations)),
        "approval_provenance": approval_provenance,
    }


def _approval_boundary_path(state_dir: Path, task_id: str) -> Path:
    return state_dir / f"approval-{_safe_key(task_id)}.json"


def save_approval_boundary(state_dir: Path, task_id: str, boundary: dict) -> Path:
    if not _valid_boundary(boundary) or boundary["task_id"] != task_id:
        raise ValueError("Invalid or mismatched task boundary")
    path = _approval_boundary_path(state_dir, task_id)
    previous = load_approval_boundary(state_dir, task_id)
    if previous is not None:
        ok, reason = validate_boundary_transition(previous, boundary)
        if not ok:
            raise ValueError(reason)
    _atomic_write_json(path, boundary)
    return path


def load_approval_boundary(state_dir: Path, task_id: str) -> dict | None:
    boundary = _read_json(_approval_boundary_path(state_dir, task_id))
    if not _valid_boundary(boundary) or boundary["task_id"] != task_id:
        return None
    return boundary


def _valid_boundary(boundary: Any) -> bool:
    return (
        isinstance(boundary, dict)
        and boundary.get("schema_version") == SCHEMA_VERSION
        and isinstance(boundary.get("task_id"), str) and bool(boundary["task_id"])
        and isinstance(boundary.get("approval_provenance"), str)
        and bool(boundary["approval_provenance"])
        and all(isinstance(boundary.get(key), list)
                and all(isinstance(item, str) and bool(item) for item in boundary[key])
                for key in ("included_operations", "excluded_operations"))
    )


def check_operation_allowed(boundary: dict, operation: str) -> bool:
    """True only if `operation` was explicitly included and not excluded.

    The worker cannot manufacture, renew, or broaden approval: an operation
    that is simply absent from both lists is NOT allowed by default, and an
    explicit exclusion always wins over an accidental inclusion.
    """

    if not _valid_boundary(boundary):
        return False
    if operation in boundary.get("excluded_operations", []):
        return False
    return operation in boundary.get("included_operations", [])


def execute_approved_operation(state_dir: Path, task_id: str, operation: str, action):
    """Adapter seam: reload the task boundary BEFORE invoking a tool callback.

    Trusted adapters own creation of the initial boundary from actual owner
    authorization. This seam does not authenticate arbitrary worker-written
    files, classify shell commands, or override any existing safety guard.
    Controlled fixture tests call it; live-provider enforcement is not implied.
    """
    boundary = load_approval_boundary(state_dir, task_id)
    if boundary is None or not check_operation_allowed(boundary, operation):
        raise PermissionError("Operation is outside the recorded task boundary")
    return action()


def validate_boundary_transition(previous: dict, proposed: dict) -> tuple[bool, str]:
    """Validate that a reloaded/updated boundary does not silently expand scope.

    This is a transfer validator, NOT an authorization issuer. No string supplied
    by a worker proves fresh owner approval. Scope expansion is always rejected;
    a future trusted authorization adapter must independently verify new approval.
    """

    if not _valid_boundary(previous) or not _valid_boundary(proposed):
        return False, "Rejected: invalid boundary schema."
    if previous["task_id"] != proposed["task_id"]:
        return False, "Rejected: task identity changed."
    prev_included = set(previous.get("included_operations", []))
    new_included = set(proposed.get("included_operations", []))
    added = new_included - prev_included

    prev_excluded = set(previous.get("excluded_operations", []))
    new_excluded = set(proposed.get("excluded_operations", []))
    removed_exclusions = prev_excluded - new_excluded

    if added:
        return False, f"Rejected: operations {sorted(added)} were added without new approval provenance."
    if removed_exclusions:
        return (
            False,
            f"Rejected: exclusions {sorted(removed_exclusions)} were removed without new approval provenance.",
        )
    if proposed["approval_provenance"] != previous["approval_provenance"]:
        return False, "Rejected: transfer changed the owner approval reference."
    return True, "ok"


# Tool-gate packets are separate from Session Map discovery. A map is not approval.
def _tool_signature(tool_name: str, tool_input: dict) -> str:
    """Hash a reviewed NON-SECRET tool invocation; never use with credentials."""
    encoded = json.dumps([tool_name, tool_input], sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _reviewed_grants(boundary: dict, tool_calls: list[dict]) -> list[dict[str, str]]:
    grants = []
    for call in tool_calls:
        if (not isinstance(call, dict) or not isinstance(call.get("tool_name"), str)
                or not call["tool_name"] or not isinstance(call.get("tool_input"), dict)
                or not isinstance(call.get("operation"), str)
                or not check_operation_allowed(boundary, call["operation"])):
            raise ValueError("Tool grant exceeds the verified task boundary")
        grants.append({"signature": _tool_signature(call["tool_name"], call["tool_input"]),
                       "operation": call["operation"]})
    return grants


def activate_approval_packet(state_dir: Path, session_id: str, worktree: Path,
                             boundary: dict, tool_calls: list[dict]) -> None:
    """Trusted-supervisor API, not an owner-authentication mechanism.

    The caller must verify real owner scope and review NON-SECRET invocations.
    Workers must not issue their own grants. The hook only restricts execution;
    it does not bypass native permissions or other safety guards.
    """
    if not session_id or not _valid_boundary(boundary) or not worktree.is_dir():
        raise ValueError("Invalid packet identity or worktree")
    grants = _reviewed_grants(boundary, tool_calls)
    packet = {"schema_version": SCHEMA_VERSION, "session_id": session_id,
              "worktree": str(worktree.resolve()), "boundary": boundary,
              "tool_grants": grants}
    path = session_binding_path(state_dir / "tool-packets", session_id)
    if path.exists():
        previous = _read_json(path)
        if (not previous or previous.get("schema_version") != SCHEMA_VERSION
                or previous.get("session_id") != session_id
                or not isinstance(previous.get("tool_grants"), list)
                or previous.get("worktree") != packet["worktree"]):
            raise ValueError("Existing packet is invalid or belongs to another worktree")
        ok, reason = validate_boundary_transition(previous.get("boundary"), boundary)
        if not ok:
            raise ValueError(reason)
        old_grants = previous.get("tool_grants", [])
        if any(grant not in old_grants for grant in grants):
            raise ValueError("Transfer cannot add tool grants; requires separate supervisor review")
    _atomic_write_json(path, packet)


def supervised_enroll(state_dir: Path, identity_payload: dict, boundary: dict,
                      tool_calls: list[dict]) -> None:
    """Bind a reviewed packet to the exact provider identity in this payload.

    The trusted caller remains responsible for verifying the real owner
    instruction and reviewing non-secret tool calls. This function authenticates
    neither the caller nor natural-language approval; it intentionally consumes
    only the provider session id and cwd from ``identity_payload``.
    """

    identity = extract_session_identity(identity_payload)
    if identity is None:
        raise ValueError("A supported current session identity and worktree are required")
    session_id, worktree = identity
    activate_approval_packet(state_dir, session_id, worktree, boundary, tool_calls)


def supervisor_extend_packet(state_dir: Path, identity_payload: dict,
                             tool_calls: list[dict]) -> None:
    """Append reviewed calls without changing the saved owner boundary.

    This is another trusted-supervisor seam, not worker self-authorization. It
    derives task scope and approval provenance only from the existing validated
    packet and binds the update to the exact current session/worktree identity.
    """

    identity = extract_session_identity(identity_payload)
    if identity is None:
        raise ValueError("A supported current session identity and worktree are required")
    session_id, worktree = identity
    path = session_binding_path(state_dir / "tool-packets", session_id)
    packet = _read_json(path)
    if (not packet or packet.get("schema_version") != SCHEMA_VERSION
            or packet.get("session_id") != session_id
            or packet.get("worktree") != str(worktree)
            or not _valid_boundary(packet.get("boundary"))
            or not isinstance(packet.get("tool_grants"), list)):
        raise ValueError("No valid approval packet for this session and worktree")
    additions = _reviewed_grants(packet["boundary"], tool_calls)
    merged = list(packet["tool_grants"])
    for grant in additions:
        if grant not in merged:
            merged.append(grant)
    packet["tool_grants"] = merged
    _atomic_write_json(path, packet)


def check_tool_call(state_dir: Path, payload: dict) -> dict[str, str]:
    """Check the actual invocation against a session-specific tool packet.

    No packet means unenrolled, not authorized. Existing native/Agent OS gates
    still apply. A present but invalid packet denies. Payload task IDs, operation
    labels, and approval references are deliberately ignored as authority.
    """
    session_id = extract_session_id(payload)
    if not session_id:
        return {"status": "unenrolled", "reason": "No supported session identifier"}
    path = session_binding_path(state_dir / "tool-packets", session_id)
    if not path.exists():
        return {"status": "unenrolled", "reason": "No approval tool packet for this session"}
    packet = _read_json(path)
    if (not packet or packet.get("schema_version") != SCHEMA_VERSION
            or packet.get("session_id") != session_id
            or not _valid_boundary(packet.get("boundary"))
            or not isinstance(packet.get("tool_grants"), list)):
        return {"status": "deny", "reason": "Invalid approval tool packet"}
    cwd = payload.get("cwd")
    if not isinstance(cwd, str) or not cwd or str(Path(cwd).resolve()) != packet.get("worktree"):
        return {"status": "deny", "reason": "Approval packet does not match the current worktree"}
    name, inputs = payload.get("tool_name"), payload.get("tool_input")
    if not isinstance(name, str) or not isinstance(inputs, dict):
        return {"status": "deny", "reason": "Unsupported tool-call payload"}
    signature = _tool_signature(name, inputs)
    for grant in packet["tool_grants"]:
        if (isinstance(grant, dict) and grant.get("signature") == signature
                and check_operation_allowed(packet["boundary"], grant.get("operation"))):
            return {"status": "matched", "reason": "Invocation matches the recorded task boundary"}
    return {"status": "deny", "reason": "Invocation is outside the reviewed tool grants"}


def approval_resume_context(state_dir: Path, payload: dict) -> str:
    """Recover scope from this session's packet, never from newest-map discovery."""
    session_id = extract_session_id(payload)
    if not session_id:
        return ""
    path = session_binding_path(state_dir / "tool-packets", session_id)
    if not path.exists():
        return ""
    packet = _read_json(path)
    cwd = payload.get("cwd")
    if (not packet or packet.get("schema_version") != SCHEMA_VERSION
            or packet.get("session_id") != session_id
            or not _valid_boundary(packet.get("boundary"))
            or not isinstance(packet.get("tool_grants"), list)
            or not isinstance(cwd, str) or not cwd
            or str(Path(cwd).resolve()) != packet.get("worktree")):
        return "The saved approval packet is invalid or belongs to another worktree; do not infer authority from it."
    boundary = packet["boundary"]
    return (
        f"Recorded task boundary: {boundary['task_id']}. "
        f"Included operations: {', '.join(boundary['included_operations']) or 'none'}. "
        f"Excluded operations: {', '.join(boundary['excluded_operations']) or 'none'}. "
        "Continue routine work inside the already-approved boundary without asking for the same approval again. "
        "The tool gate checks reviewed invocations; this record does not renew or expand approval. "
        "Current owner instructions, existing safety guards and native permissions still apply."
    )


def session_start_context(state_dir: Path, payload: dict) -> str:
    """Return current identity plus any valid saved boundary for SessionStart.

    SessionStart is the portable delivery point used by the installed Codex and
    Claude adapters. Identity is emitted even when the session is not enrolled;
    a saved approval summary is appended only when it validates for the same
    session and worktree.
    """

    parts = [session_identity_context(payload), approval_resume_context(state_dir, payload)]
    return " ".join(part for part in parts if part)
