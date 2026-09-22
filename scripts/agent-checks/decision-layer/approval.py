#!/usr/bin/env python3
"""Local approval-boundary evidence for advisory decision-layer consumers.

Boundary metadata comes from the approval tool packet that a supervisor binds
to a session through
`scripts/agent-checks/agent-os-task-context.py` (stored under
`.agent-os/approval-state/tool-packets/<session>.json`). This module only
reads and validates that record. It never writes one, and nothing a caller
passes in -- a boolean, a task string, an "approval reference" -- can turn a
missing or mismatched record into an approval.

This is deliberately not an authentication mechanism. The packet lives in a
workspace-writable directory, so a matching record is useful only as advisory
continuity evidence inside the existing trusted-adapter convention. It must
never authorize a tool call or side effect by itself. The existing approval
guard separately checks exact reviewed tool-call signatures and remains the
only restriction layer for those calls.

`evaluate` binds the record to the current session identity, the worktree,
the task id, and the requested operation, and honours an optional
`expires_at` (ISO-8601) if the packet carries one. Any gap yields a
non-approved status with a short reason code; consumers must treat every
status other than "approved" as "no authority" and stay advisory.
"""

from __future__ import annotations

from dataclasses import dataclass
import datetime as _dt
import importlib.util
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
_TASK_CONTEXT_PATH = HERE.parent / "agent-os-task-context.py"

STATUS_APPROVED = "approved"
STATUS_MISSING = "missing"
STATUS_INVALID = "invalid"
STATUS_MISMATCHED = "mismatched"
STATUS_EXPIRED = "expired"
NON_APPROVED_STATUSES = (STATUS_MISSING, STATUS_INVALID, STATUS_MISMATCHED, STATUS_EXPIRED)


def _load_task_context():
    spec = importlib.util.spec_from_file_location("decision_layer_task_context", _TASK_CONTEXT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load agent-os-task-context.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


task_context = _load_task_context()


def default_state_dir() -> Path:
    workspace = os.environ.get("SIFUTUTOR_AGENT_OS_ROOT")
    root = Path(workspace) if workspace else HERE.parents[2]
    return root / ".agent-os" / "approval-state"


@dataclass(frozen=True)
class ApprovalEvidence:
    session_id: str
    worktree: str
    task_id: str
    included_operations: tuple[str, ...]
    excluded_operations: tuple[str, ...]
    approval_provenance: str
    expires_at: str | None


@dataclass(frozen=True)
class ApprovalStatus:
    status: str
    reason: str
    evidence: ApprovalEvidence | None = None

    @property
    def approved(self) -> bool:
        return self.status == STATUS_APPROVED

    @property
    def authoritative(self) -> bool:
        """A local packet match is never authority to perform an action."""
        return False


def _parse_expiry(value: object) -> _dt.datetime | None:
    if not isinstance(value, str) or not value:
        raise ValueError("expires_at must be a non-empty ISO-8601 string")
    parsed = _dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=_dt.timezone.utc)
    return parsed


def load_evidence(state_dir: Path, session_id: str) -> tuple[str, ApprovalEvidence | None]:
    """Return (status_code, evidence). Only a fully valid packet yields evidence."""
    if not isinstance(session_id, str) or not session_id:
        return "no_session_identity", None
    path = task_context.session_binding_path(state_dir / "tool-packets", session_id)
    if not path.exists():
        return "no_packet_for_session", None
    packet = task_context._read_json(path)
    boundary = packet.get("boundary") if isinstance(packet, dict) else None
    if (
        not isinstance(packet, dict)
        or packet.get("schema_version") != task_context.SCHEMA_VERSION
        or packet.get("session_id") != session_id
        or not isinstance(packet.get("worktree"), str)
        or not task_context._valid_boundary(boundary)
        or not isinstance(packet.get("tool_grants"), list)
    ):
        return "packet_invalid", None
    expires_at = packet.get("expires_at")
    if expires_at is not None:
        try:
            _parse_expiry(expires_at)
        except ValueError:
            return "packet_invalid", None
    return "ok", ApprovalEvidence(
        session_id=session_id,
        worktree=packet["worktree"],
        task_id=boundary["task_id"],
        included_operations=tuple(boundary["included_operations"]),
        excluded_operations=tuple(boundary["excluded_operations"]),
        approval_provenance=boundary["approval_provenance"],
        expires_at=expires_at,
    )


def evaluate(
    *,
    session_id: str | None,
    worktree: str | os.PathLike | None,
    task_id: str | None,
    operation: str | None,
    state_dir: Path | None = None,
    now: _dt.datetime | None = None,
) -> ApprovalStatus:
    """Bind the trusted record to this session/worktree/task/operation."""
    state_dir = default_state_dir() if state_dir is None else Path(state_dir)
    code, evidence = load_evidence(state_dir, session_id or "")
    if evidence is None:
        status = STATUS_INVALID if code == "packet_invalid" else STATUS_MISSING
        return ApprovalStatus(status=status, reason=code)

    if not worktree or str(Path(worktree).resolve()) != evidence.worktree:
        return ApprovalStatus(STATUS_MISMATCHED, "worktree_mismatch", evidence)
    if not task_id or task_id != evidence.task_id:
        return ApprovalStatus(STATUS_MISMATCHED, "task_id_mismatch", evidence)

    if evidence.expires_at is not None:
        current = now or _dt.datetime.now(_dt.timezone.utc)
        if current.tzinfo is None:
            current = current.replace(tzinfo=_dt.timezone.utc)
        if current >= _parse_expiry(evidence.expires_at):
            return ApprovalStatus(STATUS_EXPIRED, "packet_expired", evidence)

    boundary = {
        "schema_version": task_context.SCHEMA_VERSION,
        "task_id": evidence.task_id,
        "included_operations": list(evidence.included_operations),
        "excluded_operations": list(evidence.excluded_operations),
        "approval_provenance": evidence.approval_provenance,
    }
    if not operation or not task_context.check_operation_allowed(boundary, operation):
        return ApprovalStatus(STATUS_MISMATCHED, "operation_not_included", evidence)
    return ApprovalStatus(STATUS_APPROVED, "local_boundary_packet_matches", evidence)
