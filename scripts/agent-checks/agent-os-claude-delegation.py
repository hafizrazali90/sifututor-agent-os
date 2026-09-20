#!/usr/bin/env python3
"""Preflight and supervise a bounded Claude Max delegation job.

The runner persists metadata only. Claude's raw stream is inspected in memory
for liveness, setup prompts, and usage counters, but it is never written to the
evidence files.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any


ACTIVE_STATES = {
    "starting",
    "working",
    "working_silent",
    "stalled",
    "waiting_setup",
    "unmonitored",
}
FORBIDDEN_CLAUDE_FLAGS = {
    "--allow-dangerously-skip-permissions",
    "--dangerously-skip-permissions",
    "--bare",
}
USAGE_KEYS = {
    "input_tokens",
    "output_tokens",
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
    "web_search_requests",
    "cost_usd",
    "total_cost_usd",
}
SETUP_MARKERS = (
    "authentication required",
    "please log in",
    "not logged in",
    "trust this folder",
    "workspace trust",
    "mcp authentication",
    "mcp server requires",
    "press enter to continue",
)
DIAGNOSTIC_MARKERS = {
    "nested_session": ("cannot be launched inside another claude", "nested claude"),
    "usage_limit": ("usage limit", "rate limit", "resets at"),
    "authentication": ("authentication required", "not logged in", "please log in"),
    "permission": ("permission denied", "permission mode", "not permitted"),
    "hook_failure": ("hook error", "hook failed", "blocked by hook"),
    "invalid_arguments": ("invalid argument", "unknown option", "invalid choice"),
    "input_too_long": ("prompt is too long", "request too large", "input length", "too many tokens"),
    "invalid_request": ("invalid request", "invalid_request_error", "bad request"),
}
CLAUDE_MODEL_VALUE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
SAFE_DIAGNOSTIC_VALUE = re.compile(r"[A-Za-z0-9_.:-]{1,80}")
CLAUDE_BILLING_OVERRIDE_ENV = {
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_CUSTOM_HEADERS",
    "ANTHROPIC_BEDROCK_BASE_URL",
    "ANTHROPIC_BEDROCK_MANTLE_BASE_URL",
    "ANTHROPIC_VERTEX_BASE_URL",
    "ANTHROPIC_VERTEX_PROJECT_ID",
    "ANTHROPIC_FOUNDRY_BASE_URL",
    "ANTHROPIC_FOUNDRY_API_KEY",
    "ANTHROPIC_FOUNDRY_AUTH_TOKEN",
    "ANTHROPIC_FOUNDRY_RESOURCE",
    "CLAUDE_CODE_USE_BEDROCK",
    "CLAUDE_CODE_USE_VERTEX",
    "CLAUDE_CODE_USE_FOUNDRY",
    "CLAUDE_CODE_USE_MANTLE",
    "CLAUDE_CODE_USE_ANTHROPIC_AWS",
}

BUILDER_PROOF_FIELDS = (
    "acceptance_to_proof_map",
    "entrypoint",
    "production_caller",
    "authoritative_result",
    "bypass_paths",
    "permissions_configuration",
    "disabled_unavailable",
    "failure_retry",
    "negative_control",
    "journey",
    "regression",
    "builder_evidence_not_acceptance",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-.")
    return slug[:80] or "delegation"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temporary.chmod(0o600)
    temporary.replace(path)


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text())
    if not isinstance(payload, dict):
        raise ValueError(f"expected a JSON object in {path}")
    return payload


def safe_child_env() -> dict[str, str]:
    child_env = os.environ.copy()
    for name in CLAUDE_BILLING_OVERRIDE_ENV:
        child_env.pop(name, None)
    return child_env


def api_billing_guard() -> dict[str, Any]:
    """Reject inherited auth, endpoint, and provider overrides before probing."""
    inherited = sorted(name for name in CLAUDE_BILLING_OVERRIDE_ENV if os.environ.get(name, "").strip())
    if inherited:
        return {
            "state": "blocked",
            "billing_override_inherited": True,
            "blocked_variable_names": inherited,
            "reason": (
                "Claude billing auth, endpoint, or provider overrides are inherited by the delegation runner; "
                "remove the named variables before preflight so Claude Max cannot silently use another billing route"
            ),
            "required_action": "unset every blocked_variable_name before relaunch",
        }
    return {"state": "ready", "billing_override_inherited": False}


def paid_evaluation_check(job: dict[str, Any]) -> dict[str, Any]:
    """Validate optional `paid_evaluation` job metadata (approved_by,
    estimate_usd, hard_cap_usd). This is an untrusted planning declaration: a
    valid declaration neither proves approval nor grants this Max-only watchdog permission to launch
    Claude with API billing. Paid provider evaluation or canary work runs
    through a separate, manually-supervised path outside this automated
    runner; see docs/agent-playbooks/handoff.md."""
    spec = job.get("paid_evaluation")
    if spec is None:
        return {"state": "ready", "declared": False}
    if not isinstance(spec, dict):
        return {
            "state": "blocked",
            "declared": True,
            "reason": "paid_evaluation must be an object with approved_by, estimate_usd, and hard_cap_usd",
        }
    errors: list[str] = []
    approved_by = spec.get("approved_by")
    if not isinstance(approved_by, str) or not approved_by.strip():
        errors.append("approved_by must be a non-empty string naming who approved paid billing")
    estimate = spec.get("estimate_usd")
    valid_estimate = isinstance(estimate, (int, float)) and not isinstance(estimate, bool) and estimate > 0
    if not valid_estimate:
        errors.append("estimate_usd must be a positive number")
    hard_cap = spec.get("hard_cap_usd")
    valid_cap = isinstance(hard_cap, (int, float)) and not isinstance(hard_cap, bool) and hard_cap > 0
    if not valid_cap:
        errors.append("hard_cap_usd must be a positive number")
    if valid_estimate and valid_cap and hard_cap < estimate:
        errors.append("hard_cap_usd must be greater than or equal to estimate_usd")
    if errors:
        return {
            "state": "blocked",
            "declared": True,
            "reason": "paid provider evaluation planning metadata is incomplete or invalid",
            "errors": errors,
        }
    return {
        "state": "ready",
        "declared": True,
        "trust": "untrusted_job_declaration",
        "approved_by": approved_by,
        "estimate_usd": estimate,
        "hard_cap_usd": hard_cap,
        "executes_paid_billing": False,
        "proves_human_approval": False,
    }


def run_probe(command: list[str], cwd: Path, timeout: float = 12) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            env=safe_child_env(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return subprocess.CompletedProcess(command, 124, "", type(exc).__name__)


def git_value(worktree: Path, *args: str) -> tuple[int, str]:
    completed = run_probe(["git", "-C", str(worktree), *args], worktree)
    return completed.returncode, completed.stdout.strip()


def git_snapshot(worktree: Path) -> dict[str, Any]:
    root_rc, root = git_value(worktree, "rev-parse", "--show-toplevel")
    branch_rc, branch = git_value(worktree, "branch", "--show-current")
    commit_rc, commit = git_value(worktree, "rev-parse", "HEAD")
    status_probe = run_probe(["git", "-C", str(worktree), "status", "--porcelain"], worktree)
    status_rc = status_probe.returncode
    status = status_probe.stdout.rstrip("\n")
    changed_paths = []
    if status_rc == 0:
        for line in status.splitlines():
            if len(line) > 3:
                changed_paths.append(line[3:].strip())
    return {
        "is_git_worktree": root_rc == 0,
        "root": root if root_rc == 0 else None,
        "branch": branch if branch_rc == 0 else None,
        "commit": commit if commit_rc == 0 else None,
        "dirty": bool(changed_paths),
        "changed_paths": changed_paths,
    }


def pid_alive(pid: Any) -> bool:
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def lane_lock_path(job: dict[str, Any]) -> Path:
    worktree_key = hashlib.sha256(str(Path(job["worktree"]).resolve()).encode()).hexdigest()[:16]
    return (
        Path(tempfile.gettempdir())
        / "sifututor-agent-os-claude-delegation-locks"
        / worktree_key
        / "worktree.json"
    )


def inspect_lane(job: dict[str, Any]) -> dict[str, Any]:
    path = lane_lock_path(job)
    if not path.exists():
        return {"state": "available", "lock": str(path)}
    try:
        lock = read_json(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return {"state": "stale", "lock": str(path), "reason": "invalid lock metadata"}
    owner_alive = pid_alive(lock.get("owner_pid"))
    worker_alive = pid_alive(lock.get("worker_pid"))
    if owner_alive or worker_alive:
        return {
            "state": "busy",
            "lock": str(path),
            "job_id": lock.get("job_id"),
            "lane_owner": lock.get("lane_owner"),
            "watchdog_alive": owner_alive,
            "worker_alive": worker_alive,
        }
    return {
        "state": "stale",
        "lock": str(path),
        "job_id": lock.get("job_id"),
        "reason": "recorded owner process is not alive",
    }


def acquire_lane(job: dict[str, Any]) -> Path:
    path = lane_lock_path(job)
    path.parent.mkdir(parents=True, exist_ok=True)
    for _attempt in range(2):
        payload = {
            "schema_version": 1,
            "job_id": job["job_id"],
            "lane_owner": job["lane_owner"],
            "owner_pid": os.getpid(),
            "acquired_at": utc_now(),
        }
        try:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            lane = inspect_lane(job)
            if lane["state"] == "stale":
                path.unlink(missing_ok=True)
                continue
            raise RuntimeError(f"delegation lane is busy with job {lane.get('job_id', 'unknown')}")
        with os.fdopen(descriptor, "w") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        return path
    raise RuntimeError("could not replace stale delegation lane lock")


def release_lane(path: Path) -> None:
    try:
        lock = read_json(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return
    if lock.get("owner_pid") == os.getpid() and not pid_alive(lock.get("worker_pid")):
        path.unlink(missing_ok=True)


def record_lane_worker(path: Path, worker_pid: int) -> None:
    lock = read_json(path)
    if lock.get("owner_pid") != os.getpid():
        raise RuntimeError("delegation lane ownership changed before worker launch")
    lock["worker_pid"] = worker_pid
    write_json(path, lock)


def command_check(args: Any) -> dict[str, Any]:
    if not isinstance(args, list) or not all(isinstance(item, str) for item in args):
        return {"state": "blocked", "reason": "claude_args must be a list of strings"}
    forbidden = sorted(flag for flag in FORBIDDEN_CLAUDE_FLAGS if flag in args)
    if forbidden:
        return {"state": "blocked", "reason": "unsafe Claude permission bypass flag", "flags": forbidden}
    has_print = "--print" in args or "-p" in args
    has_verbose = "--verbose" in args
    has_stream = "--output-format=stream-json" in args or any(
        args[index : index + 2] == ["--output-format", "stream-json"]
        for index in range(max(0, len(args) - 1))
    )
    missing = []
    if not has_print:
        missing.append("--print")
    if not has_verbose:
        missing.append("--verbose")
    if not has_stream:
        missing.append("--output-format stream-json")
    if missing:
        return {"state": "blocked", "reason": "watchdog-safe non-interactive flags are missing", "missing": missing}
    return {"state": "ready", "mode": "non-interactive stream-json"}


def model_selection_check(args: Any) -> dict[str, Any]:
    """Require the job file to name the Claude model explicitly.

    A job that inherited the workspace `opusplan` selection reached Anthropic
    and came back HTTP 400 before a single token was billed, while an
    otherwise identical `--model opus` job ran normally. The runner therefore
    refuses to launch a job whose model is implicit, and it never picks a
    model itself: the job contract has to say which alias it wants.
    """
    blocked = {
        "state": "blocked",
        "explicit_model_selected": False,
        "reason": (
            "claude_args does not select a Claude model explicitly; an inherited workspace "
            "model selection can fail at the API before any usage is recorded"
        ),
        "required_action": (
            "add an explicit --model <alias> pair, or --model=<alias>, to claude_args and copy "
            "the currently proven alias from docs/agent-playbooks/templates/claude-delegation-job.json"
        ),
    }
    if not isinstance(args, list) or not all(isinstance(item, str) for item in args):
        return blocked
    selected: str | None = None
    for index, item in enumerate(args):
        if item == "--model":
            selected = args[index + 1] if index + 1 < len(args) else None
        elif item.startswith("--model="):
            selected = item.split("=", 1)[1]
        else:
            continue
        break
    if selected is None or not CLAUDE_MODEL_VALUE.fullmatch(selected):
        return blocked
    return {"state": "ready", "explicit_model_selected": True, "model": selected}


def boundary_check(job: dict[str, Any]) -> dict[str, Any]:
    stop_point = str(job.get("approved_stop_point", "")).lower()
    blocked_terms = ("merge", "deploy", "production", "live checked", "monitor")
    matched = sorted(term for term in blocked_terms if term in stop_point)
    if matched:
        return {
            "state": "blocked",
            "reason": "the first delegation runner release stops before merge, deploy, or production",
            "matched_terms": matched,
        }
    return {
        "state": "ready",
        "approved_stop_point": job.get("approved_stop_point"),
        "human_approval_inherited": True,
    }


def validate_job(job: dict[str, Any]) -> list[str]:
    required = {
        "schema_version",
        "job_id",
        "goal",
        "approved_stop_point",
        "forbidden_actions",
        "worktree",
        "branch",
        "lane_owner",
        "required_proof",
        "builder_completion_proof",
        "reporting_cadence_seconds",
        "stall_after_seconds",
        "brief_file",
        "handback_file",
        "state_dir",
        "claude_args",
    }
    errors = [f"missing required job field: {key}" for key in sorted(required - set(job))]
    if job.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    for key in (
        "job_id",
        "goal",
        "approved_stop_point",
        "worktree",
        "branch",
        "lane_owner",
        "brief_file",
        "handback_file",
        "state_dir",
    ):
        if key in job and (not isinstance(job[key], str) or not job[key].strip()):
            errors.append(f"{key} must be a non-empty string")
    for key in ("forbidden_actions", "required_proof"):
        if key in job and (
            not isinstance(job[key], list)
            or not job[key]
            or not all(isinstance(v, str) and v.strip() for v in job[key])
        ):
            errors.append(f"{key} must be a non-empty list of non-empty strings")
    proof_contract = job.get("builder_completion_proof")
    if not isinstance(proof_contract, dict):
        errors.append("builder_completion_proof must be an object")
    else:
        mode = proof_contract.get("mode")
        reason = proof_contract.get("not_applicable_reason")
        if mode not in {"required", "not_applicable"}:
            errors.append("builder_completion_proof.mode must be required or not_applicable")
        if mode == "not_applicable" and (not isinstance(reason, str) or not reason.strip()):
            errors.append(
                "builder_completion_proof.not_applicable_reason must explain why the delegated task is not implementation work"
            )
        if mode == "required" and reason not in {None, ""}:
            errors.append(
                "builder_completion_proof.not_applicable_reason must be empty when mode is required"
            )
    for key in ("reporting_cadence_seconds", "stall_after_seconds"):
        value = job.get(key)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
            errors.append(f"{key} must be a positive number")
    poll = job.get("poll_interval_seconds", 0.5)
    if not isinstance(poll, (int, float)) or isinstance(poll, bool) or poll <= 0:
        errors.append("poll_interval_seconds must be a positive number when present")
    return errors


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def filtered_auth(raw: str, returncode: int) -> dict[str, Any]:
    if returncode != 0:
        return {"state": "failed", "logged_in": False}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {"state": "failed", "logged_in": False, "reason": "non-JSON auth response"}
    logged_in = payload.get("loggedIn") is True
    auth_method = payload.get("authMethod")
    subscription_type = payload.get("subscriptionType")
    api_provider = payload.get("apiProvider")
    # `authMethod`/`subscriptionType` alone can report a genuine Max login
    # while `apiProvider` shows the request is actually routed through
    # metered API billing (the reported #28 incident). Require all three to
    # agree before treating the job as first-party Max-billed.
    is_max = (
        logged_in
        and auth_method == "claude.ai"
        and subscription_type == "max"
        and api_provider == "firstParty"
    )
    return {
        "state": "ready" if is_max else "failed",
        "logged_in": logged_in,
        "auth_method": auth_method,
        "api_provider": api_provider,
        "subscription_type": subscription_type,
        "api_key_env_removed_for_child": True,
    }


def mcp_check(raw: str, returncode: int, required: list[str]) -> dict[str, Any]:
    if returncode != 0:
        return {"state": "failed" if required else "warning", "required": required, "connected": []}
    connected = []
    for line in raw.splitlines():
        if "connected" not in line.lower():
            continue
        name = line.split(":", 1)[0].strip()
        if re.fullmatch(r"[A-Za-z0-9._ -]+", name):
            connected.append(name)
    missing = sorted(set(required) - set(connected))
    return {
        "state": "failed" if missing else "ready",
        "required": required,
        "connected": sorted(set(connected)),
        "missing": missing,
    }


def preflight(job: dict[str, Any]) -> dict[str, Any]:
    errors = validate_job(job)
    if errors:
        return {"schema_version": 1, "checked_at": utc_now(), "ready": False, "errors": errors, "checks": {}}

    paid_evaluation = paid_evaluation_check(job)
    billing_guard = api_billing_guard()
    if billing_guard["state"] == "blocked":
        return {
            "schema_version": 1,
            "job_id": job.get("job_id"),
            "checked_at": utc_now(),
            "ready": False,
            "errors": errors,
            "checks": {"api_billing_guard": billing_guard, "paid_evaluation": paid_evaluation},
        }

    worktree = Path(job["worktree"]).expanduser().resolve()
    brief = Path(job["brief_file"]).expanduser().resolve()
    handback = Path(job["handback_file"]).expanduser().resolve()
    state_dir = Path(job["state_dir"]).expanduser().resolve()
    runtime_root = (worktree / ".agent-os" / "delegations").resolve()
    git = git_snapshot(worktree) if worktree.is_dir() else {"is_git_worktree": False}
    worktree_state = "ready"
    worktree_reason = None
    if not worktree.is_dir() or not git.get("is_git_worktree"):
        worktree_state = "failed"
        worktree_reason = "worktree does not exist or is not a Git worktree"
    elif Path(str(git.get("root"))).resolve() != worktree:
        worktree_state = "failed"
        worktree_reason = "job worktree must be the Git worktree root"
    elif git.get("branch") != job["branch"]:
        worktree_state = "failed"
        worktree_reason = "declared branch does not match current worktree branch"

    claude_path = shutil.which("claude")
    version_probe = run_probe([claude_path, "--version"], worktree) if claude_path and worktree.is_dir() else None
    doctor_probe = run_probe([claude_path, "doctor"], worktree) if claude_path and worktree.is_dir() else None
    auth_probe = (
        run_probe([claude_path, "auth", "status", "--json"], worktree)
        if claude_path and worktree.is_dir()
        else None
    )
    required_mcp = job.get("required_mcp_servers", [])
    if not isinstance(required_mcp, list) or not all(isinstance(v, str) for v in required_mcp):
        required_mcp = []
        errors.append("required_mcp_servers must be a list of strings")
    mcp_probe = (
        run_probe([claude_path, "mcp", "list"], worktree)
        if claude_path and worktree.is_dir()
        else None
    )
    auth = filtered_auth(auth_probe.stdout, auth_probe.returncode) if auth_probe else {"state": "failed"}
    mcp = mcp_check(mcp_probe.stdout, mcp_probe.returncode, required_mcp) if mcp_probe else {"state": "failed"}
    lane = inspect_lane(job)
    command = command_check(job["claude_args"])
    runtime_paths_safe = (
        is_within(brief, runtime_root)
        and is_within(state_dir, runtime_root)
        and is_within(handback, state_dir)
    )
    brief_ignore_rc, _brief_ignore = git_value(worktree, "check-ignore", "-q", str(brief))
    state_ignore_rc, _state_ignore = git_value(worktree, "check-ignore", "-q", str(state_dir))
    runtime_ignored = brief_ignore_rc == 0 and state_ignore_rc == 0
    files = {
        "state": (
            "ready"
            if runtime_paths_safe
            and runtime_ignored
            and brief.is_file()
            and not handback.exists()
            and not state_dir.exists()
            else "failed"
        ),
        "runtime_root": str(runtime_root),
        "runtime_paths_safe": runtime_paths_safe,
        "runtime_paths_git_ignored": runtime_ignored,
        "brief_exists": brief.is_file(),
        "handback_absent_before_start": not handback.exists(),
        "state_dir_absent_before_start": not state_dir.exists(),
    }
    checks = {
        "api_billing_guard": billing_guard,
        "paid_evaluation": paid_evaluation,
        "claude_cli": {
            "state": "ready" if claude_path and version_probe and version_probe.returncode == 0 else "failed",
            "path": claude_path,
            "version": version_probe.stdout.strip()[:120] if version_probe and version_probe.returncode == 0 else None,
        },
        "claude_doctor": {
            "state": (
                "ready"
                if doctor_probe
                and doctor_probe.returncode == 0
                and "no installation issues found" in doctor_probe.stdout.lower()
                else "failed"
            ),
            "installation_issues_reported": (
                False
                if doctor_probe
                and doctor_probe.returncode == 0
                and "no installation issues found" in doctor_probe.stdout.lower()
                else None
            ),
        },
        "auth": auth,
        "mcp": mcp,
        "worktree": {"state": worktree_state, "reason": worktree_reason, **git},
        "lane": lane,
        "boundary": boundary_check(job),
        "command": command,
        "model_selection": model_selection_check(job["claude_args"]),
        "files": files,
    }
    blocking_states = {"failed", "blocked", "busy"}
    ready = not errors and all(check.get("state") not in blocking_states for check in checks.values())
    return {
        "schema_version": 1,
        "job_id": job["job_id"],
        "checked_at": utc_now(),
        "ready": ready,
        "errors": errors,
        "checks": checks,
    }


def numeric_usage(payload: Any, totals: dict[str, float]) -> None:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in USAGE_KEYS and isinstance(value, (int, float)) and not isinstance(value, bool):
                totals[key] = value
            elif isinstance(value, (dict, list)):
                numeric_usage(value, totals)
    elif isinstance(payload, list):
        for item in payload:
            numeric_usage(item, totals)


def _diagnostic_category(value: Any) -> str | None:
    """Classify known terminal failures without persisting raw worker text."""
    if isinstance(value, str):
        lowered = value.lower()
        for category, markers in DIAGNOSTIC_MARKERS.items():
            if any(marker in lowered for marker in markers):
                return category
    elif isinstance(value, dict):
        for child in value.values():
            category = _diagnostic_category(child)
            if category:
                return category
    elif isinstance(value, list):
        for child in value:
            category = _diagnostic_category(child)
            if category:
                return category
    return None


def _safe_diagnostic_enum(value: Any) -> str | int | bool | None:
    """Accept only bounded scalars, so no free-form worker text can be stored."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, str) and SAFE_DIAGNOSTIC_VALUE.fullmatch(value):
        return value
    return None


def _is_error_signal(payload: dict[str, Any]) -> bool:
    """Classify only error-shaped events.

    Ordinary assistant prose routinely contains phrases like `permission
    denied`, and a successful 19-turn run was previously mislabelled from its
    own text. Category detection therefore runs on failure payloads only.
    """
    if payload.get("is_error") is True:
        return True
    if payload.get("api_error_status") is not None:
        return True
    for key in ("type", "subtype", "terminal_reason", "stop_reason"):
        value = payload.get(key)
        if isinstance(value, str) and "error" in value.lower():
            return True
    return False


def new_terminal_diagnostic() -> dict[str, Any]:
    """Fixed, metadata-only shape for the worker's terminal outcome."""
    return {
        "result_seen": False,
        "result_subtype": None,
        "result_is_error": None,
        "result_turns": None,
        "api_error_status": None,
        "terminal_reason": None,
        "stop_reason": None,
        "fast_mode_state": None,
        "fast_mode_disabled_reason": None,
        "permission_denial_count": None,
        "category": None,
        "stderr_lines": 0,
        "raw_worker_output_stored": False,
    }


def event_metadata(
    line: str,
    stream: str,
    usage: dict[str, float],
    diagnostic: dict[str, Any] | None = None,
) -> tuple[str, str | None]:
    if stream == "stderr":
        lower = line.lower()
        if diagnostic is not None:
            diagnostic["stderr_lines"] = int(diagnostic.get("stderr_lines", 0)) + 1
            category = _diagnostic_category(lower)
            if category:
                diagnostic["category"] = category
        if any(marker in lower for marker in SETUP_MARKERS):
            return "setup_prompt", None
        return "stderr", None
    try:
        payload = json.loads(line)
    except json.JSONDecodeError:
        lower = line.lower()
        if any(marker in lower for marker in SETUP_MARKERS):
            return "setup_prompt", None
        return "non_json", None
    event_type = str(payload.get("type", "json")) if isinstance(payload, dict) else "json"
    subtype = str(payload.get("subtype")) if isinstance(payload, dict) and payload.get("subtype") else None
    if diagnostic is not None and isinstance(payload, dict):
        if _is_error_signal(payload):
            category = _diagnostic_category(payload)
            if category:
                diagnostic["category"] = category
        if event_type == "result":
            diagnostic["result_seen"] = True
            diagnostic["result_subtype"] = _safe_diagnostic_enum(subtype)
            is_error = payload.get("is_error")
            diagnostic["result_is_error"] = is_error if isinstance(is_error, bool) else None
            turns = payload.get("num_turns")
            diagnostic["result_turns"] = turns if isinstance(turns, int) and not isinstance(turns, bool) else None
            for field in (
                "api_error_status",
                "terminal_reason",
                "stop_reason",
                "fast_mode_state",
                "fast_mode_disabled_reason",
            ):
                diagnostic[field] = _safe_diagnostic_enum(payload.get(field))
            denials = payload.get("permission_denials")
            if isinstance(denials, list):
                diagnostic["permission_denial_count"] = len(denials)
    if event_type == "result":
        usage.clear()
        numeric_usage(payload, usage)
    return safe_slug(event_type), safe_slug(subtype) if subtype else None


def brief_digest(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"path": str(path), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def handback_digest(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"path": str(path), "exists": False}
    data = path.read_bytes()
    return {"path": str(path), "exists": True, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def structured_handback_fields(text: str) -> dict[str, str]:
    """Parse explicit ``field: value`` proof records without interpreting claims."""
    fields: dict[str, str] = {}
    in_fence = False
    for line in text.splitlines():
        if re.match(r"^\s*```", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = re.match(r"^\s*(?:[-*]\s*)?([a-z][a-z0-9_]*)\s*:\s*(.+?)\s*$", line, re.I)
        if match and match.group(1).lower() not in fields:
            fields[match.group(1).lower()] = match.group(2).strip()
    return fields


def handback_contract(path: Path, job: dict[str, Any]) -> dict[str, Any]:
    """Check the configured artifact shape without accepting its claims."""
    result: dict[str, Any] = {
        "structure_valid": False,
        "configured_items": len(job["required_proof"]),
        "addressed_items": 0,
        "semantic_acceptance_proven": False,
        "errors": [],
    }
    try:
        with path.open("rb") as stream:
            raw = stream.read(1_048_577)
        if len(raw) > 1_048_576:
            result["errors"].append("handback exceeds 1 MiB")
            return result
        text = raw.decode("utf-8")
    except (OSError, UnicodeError):
        result["errors"].append("handback is not readable UTF-8 text")
        return result
    if not text.strip():
        result["errors"].append("handback is empty")
        return result
    fields = structured_handback_fields(text)
    proof_contract = job["builder_completion_proof"]
    if proof_contract["mode"] == "required":
        missing_fields = [field for field in BUILDER_PROOF_FIELDS if not fields.get(field)]
        result["proof_mode"] = "required"
        result["required_fields"] = list(BUILDER_PROOF_FIELDS)
        result["addressed_fields"] = len(BUILDER_PROOF_FIELDS) - len(missing_fields)
        if missing_fields:
            result["errors"].append("builder completion proof fields are missing")
            result["missing_proof_fields"] = missing_fields
            return result
    else:
        result["proof_mode"] = "not_applicable"
        returned_reason = fields.get("builder_proof_not_applicable", "")
        configured_reason = proof_contract["not_applicable_reason"].strip()
        if returned_reason != configured_reason:
            result["errors"].append(
                "builder_proof_not_applicable must exactly match the configured reason"
            )
            return result

    normalized = " ".join(text.lower().split())
    missing = [
        item
        for item in job["required_proof"]
        if " ".join(item.lower().split()) not in normalized
    ]
    result["addressed_items"] = len(job["required_proof"]) - len(missing)
    if missing:
        result["errors"].append("configured proof items are not addressed")
        result["missing_required_proof"] = missing
        return result
    result["structure_valid"] = True
    return result


def diagnostic_text(diagnostic: dict[str, Any], key: str) -> str:
    """Render one safe diagnostic value; absent stays explicitly unavailable."""
    value = diagnostic.get(key)
    if value is None:
        return "unavailable"
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def render_evidence_markdown(evidence: dict[str, Any]) -> str:
    usage = evidence["usage"]
    diagnostic = evidence.get("terminal_diagnostic") or {}
    exit_code = evidence["worker_exit_code"]
    worker_failed = exit_code != 0 or diagnostic.get("result_is_error") is True
    lines = [
        f"# Claude Delegation Evidence — {evidence['job_id']}",
        "",
    ]
    if worker_failed:
        lines.extend(
            [
                f"**Worker failed.** Exit code `{exit_code}`, "
                f"`result_is_error={diagnostic_text(diagnostic, 'result_is_error')}`, "
                f"`api_error_status={diagnostic_text(diagnostic, 'api_error_status')}`, "
                f"terminal reason `{diagnostic_text(diagnostic, 'terminal_reason')}`.",
                "",
            ]
        )
    lines.extend(
        [
            f"- Final state: `{evidence['final_state']}`",
            f"- Worker exit code: `{exit_code}`",
            f"- Model selected: `{evidence.get('model_selected') or 'unavailable'}`",
            f"- Worktree: `{evidence['worktree']['path']}`",
            f"- Branch: `{evidence['worktree']['end'].get('branch')}`",
            f"- Approved stop point: `{evidence['approved_stop_point']}`",
            f"- Stall detected: `{str(evidence['liveness']['stall_detected']).lower()}`",
            f"- Maximum quiet time: `{evidence['liveness']['max_quiet_seconds']:.2f}s`",
            f"- Handback present: `{str(evidence['handback']['exists']).lower()}`",
            f"- Usage: `{usage['state']}`",
            "",
            "## Terminal Diagnostic",
            "",
            f"- Result event seen: `{diagnostic_text(diagnostic, 'result_seen')}`",
            f"- Result reported error: `{diagnostic_text(diagnostic, 'result_is_error')}`",
            f"- API error status: `{diagnostic_text(diagnostic, 'api_error_status')}`",
            f"- Terminal reason: `{diagnostic_text(diagnostic, 'terminal_reason')}`",
            f"- Stop reason: `{diagnostic_text(diagnostic, 'stop_reason')}`",
            f"- Result subtype: `{diagnostic_text(diagnostic, 'result_subtype')}`",
            f"- Turns: `{diagnostic_text(diagnostic, 'result_turns')}`",
            f"- Permission denials: `{diagnostic_text(diagnostic, 'permission_denial_count')}`",
            f"- Known failure category: `{diagnostic_text(diagnostic, 'category')}`",
            f"- Stderr lines: `{diagnostic_text(diagnostic, 'stderr_lines')}`",
            f"- Fast mode: `{diagnostic_text(diagnostic, 'fast_mode_state')}` "
            f"(`{diagnostic_text(diagnostic, 'fast_mode_disabled_reason')}`)",
            "",
            "These are bounded diagnostic values only. Raw Claude stream content, result text,",
            "prompts, stderr, and identities are intentionally not stored in this evidence.",
            "Independent Codex review and all original approval gates still apply.",
            "",
        ]
    )
    return "\n".join(lines)


def run_job(job: dict[str, Any]) -> int:
    preflight_result = preflight(job)
    if not preflight_result["ready"]:
        print(json.dumps(preflight_result, indent=2, sort_keys=True), file=sys.stderr)
        return 1

    state_dir = Path(job["state_dir"]).expanduser().resolve()
    state_dir.mkdir(parents=True, exist_ok=False)
    write_json(state_dir / "preflight.json", preflight_result)
    worktree = Path(job["worktree"]).expanduser().resolve()
    brief = Path(job["brief_file"]).expanduser()
    handback = Path(job["handback_file"]).expanduser()
    handback.parent.mkdir(parents=True, exist_ok=True)
    lock: Path | None = None
    started_at = utc_now()
    monotonic_start = time.monotonic()
    transitions: list[dict[str, Any]] = []
    event_counts: Counter[str] = Counter()
    usage: dict[str, float] = {}
    terminal_diagnostic: dict[str, Any] = new_terminal_diagnostic()
    state = "starting"
    worker_pid: int | None = None
    last_worker_event_at = started_at
    last_output_monotonic = monotonic_start
    max_quiet = 0.0
    stall_detected = False

    def transition(next_state: str, reason: str) -> None:
        nonlocal state
        if next_state == state and transitions:
            return
        state = next_state
        transitions.append({"at": utc_now(), "state": next_state, "reason": reason})

    def persist_state() -> None:
        write_json(
            state_dir / "state.json",
            {
                "schema_version": 1,
                "job_id": job["job_id"],
                "state": state,
                "pid": worker_pid,
                "watchdog_pid": os.getpid(),
                "heartbeat_at": utc_now(),
                "last_worker_event_at": last_worker_event_at,
                "approved_stop_point": job["approved_stop_point"],
                "lane_owner": job["lane_owner"],
            },
        )

    process: subprocess.Popen[str] | None = None
    try:
        lock = acquire_lane(job)
        transition("starting", "preflight passed; starting Claude worker")
        persist_state()
        claude_path = shutil.which("claude")
        if not claude_path:
            raise RuntimeError("claude command disappeared after preflight")
        command = [claude_path, *job["claude_args"]]
        child_env = safe_child_env()
        child_env["CLAUDE_DELEGATION_JOB_ID"] = str(job["job_id"])
        process = subprocess.Popen(
            command,
            cwd=worktree,
            env=child_env,
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
        )
        worker_pid = process.pid
        record_lane_worker(lock, worker_pid)
        if process.stdin is None:
            raise RuntimeError("Claude worker stdin pipe is unavailable")
        process.stdin.write(brief.read_text())
        process.stdin.close()
        transition("working", "worker process is alive")
        persist_state()

        selector = selectors.DefaultSelector()
        if process.stdout:
            selector.register(process.stdout, selectors.EVENT_READ, "stdout")
        if process.stderr:
            selector.register(process.stderr, selectors.EVENT_READ, "stderr")
        poll_interval = max(0.01, float(job.get("poll_interval_seconds", 0.5)))
        stall_after = max(0.05, float(job["stall_after_seconds"]))
        silent_after = max(0.02, stall_after / 2)
        heartbeat_interval = min(5.0, max(poll_interval, float(job["reporting_cadence_seconds"])))
        last_persist = time.monotonic()

        while selector.get_map() or process.poll() is None:
            events = selector.select(timeout=poll_interval)
            for key, _mask in events:
                line = key.fileobj.readline()
                if line == "":
                    selector.unregister(key.fileobj)
                    continue
                now = time.monotonic()
                last_output_monotonic = now
                last_worker_event_at = utc_now()
                kind, subtype = event_metadata(line, key.data, usage, terminal_diagnostic)
                event_counts[kind] += 1
                if subtype:
                    event_counts[f"{kind}:{subtype}"] += 1
                if kind == "setup_prompt":
                    transition("waiting_setup", "setup, trust, authentication, or MCP prompt detected")
                elif state in {"working_silent", "stalled"}:
                    transition("working", "worker emitted a new event")

            quiet = max(0.0, time.monotonic() - last_output_monotonic)
            max_quiet = max(max_quiet, quiet)
            if state not in {"waiting_setup", "stalled"} and quiet >= stall_after and process.poll() is None:
                stall_detected = True
                transition("stalled", "worker is alive but no output crossed the stall threshold")
            elif state == "working" and quiet >= silent_after and process.poll() is None:
                transition("working_silent", "worker is alive with no recent output")

            if time.monotonic() - last_persist >= heartbeat_interval:
                persist_state()
                last_persist = time.monotonic()

        returncode = process.wait()
        handback_info = handback_digest(handback)
        return_contract = (
            handback_contract(handback, job)
            if handback_info["exists"]
            else {
                "structure_valid": False,
                "configured_items": len(job["required_proof"]),
                "addressed_items": 0,
                "semantic_acceptance_proven": False,
                "errors": ["required handback is missing"],
            }
        )
        if returncode != 0:
            final_state = "failed"
            final_reason = "worker process exited unsuccessfully"
        elif not handback_info["exists"]:
            final_state = "incomplete"
            final_reason = "worker exited successfully but required handback is missing"
        elif not return_contract["structure_valid"]:
            final_state = "incomplete"
            final_reason = "worker exited successfully but the configured return contract is incomplete"
        else:
            final_state = "returned"
            final_reason = "worker finished and returned a structurally valid artifact for independent review"
        transition(final_state, final_reason)
        persist_state()

        ended_at = utc_now()
        usage_payload: dict[str, Any]
        if usage:
            usage_payload = {"state": "available", "counters": dict(sorted(usage.items()))}
        else:
            usage_payload = {"state": "unavailable", "reason": "worker stream exposed no usage counters"}
        evidence = {
            "schema_version": 1,
            "job_id": job["job_id"],
            "goal": job["goal"],
            "approved_stop_point": job["approved_stop_point"],
            "forbidden_actions": job["forbidden_actions"],
            "required_proof": job["required_proof"],
            "started_at": started_at,
            "ended_at": ended_at,
            "duration_seconds": round(time.monotonic() - monotonic_start, 3),
            "final_state": final_state,
            "worker_exit_code": returncode,
            "preflight": preflight_result,
            "worktree": {
                "path": str(worktree),
                "start": preflight_result["checks"]["worktree"],
                "end": git_snapshot(worktree),
            },
            "brief": brief_digest(brief),
            "handback": handback_info,
            "worker_outcome": "finished" if returncode == 0 else "failed",
            "model_selected": preflight_result["checks"].get("model_selection", {}).get("model"),
            "terminal_diagnostic": terminal_diagnostic,
            "return_contract": return_contract,
            "state_transitions": transitions,
            "liveness": {
                "watchdog_heartbeat_source": "local process clock; no model call",
                "event_counts": dict(sorted(event_counts.items())),
                "max_quiet_seconds": round(max_quiet, 3),
                "stall_threshold_seconds": float(job["stall_after_seconds"]),
                "stall_detected": stall_detected,
                "raw_worker_output_stored": False,
            },
            "usage": usage_payload,
            "review": {
                "independent_codex_review_required": True,
                "automatic_approval": False,
                "automatic_restart": False,
                "automatic_merge_or_deploy": False,
            },
        }
        write_json(state_dir / "evidence.json", evidence)
        markdown = state_dir / "evidence.md"
        markdown.write_text(render_evidence_markdown(evidence))
        markdown.chmod(0o600)
        print(f"Claude delegation {job['job_id']}: {final_state}")
        print(f"Evidence: {state_dir / 'evidence.json'}")
        print(f"Handback: {handback}")
        return 0 if final_state == "returned" else 1
    except (OSError, RuntimeError, ValueError) as exc:
        if process is not None and process.poll() is None:
            transition("unmonitored", f"watchdog stopped after {type(exc).__name__}")
        else:
            transition("failed", type(exc).__name__)
        persist_state()
        print(f"Claude delegation failed: {type(exc).__name__}", file=sys.stderr)
        return 1
    finally:
        if lock is not None:
            release_lane(lock)


def status(state_dir: Path) -> dict[str, Any]:
    state_path = state_dir / "state.json"
    if not state_path.is_file():
        return {"observed_state": "missing", "state_dir": str(state_dir)}
    payload = read_json(state_path)
    recorded = payload.get("state", "unknown")
    worker_alive = pid_alive(payload.get("pid"))
    watchdog_alive = pid_alive(payload.get("watchdog_pid"))
    if recorded in ACTIVE_STATES and not worker_alive:
        observed = "stale"
    elif recorded in ACTIVE_STATES and not watchdog_alive:
        observed = "unmonitored"
    else:
        observed = recorded

    def age_seconds(value: Any) -> float | None:
        if not isinstance(value, str):
            return None
        try:
            timestamp = datetime.fromisoformat(value)
        except ValueError:
            return None
        return round(max(0.0, (datetime.now(timezone.utc) - timestamp).total_seconds()), 1)

    return {
        "job_id": payload.get("job_id"),
        "recorded_state": recorded,
        "observed_state": observed,
        "worker_alive": worker_alive,
        "watchdog_alive": watchdog_alive,
        "heartbeat_at": payload.get("heartbeat_at"),
        "heartbeat_age_seconds": age_seconds(payload.get("heartbeat_at")),
        "last_worker_event_at": payload.get("last_worker_event_at"),
        "last_worker_event_age_seconds": age_seconds(payload.get("last_worker_event_at")),
        "approved_stop_point": payload.get("approved_stop_point"),
        "lane_owner": payload.get("lane_owner"),
        "state_dir": str(state_dir),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight_parser = subparsers.add_parser("preflight", help="check Claude Max and job readiness")
    preflight_parser.add_argument("--job", required=True, type=Path)
    preflight_parser.add_argument("--json", action="store_true")

    run_parser = subparsers.add_parser("run", help="run and supervise one bounded Claude job")
    run_parser.add_argument("--job", required=True, type=Path)

    status_parser = subparsers.add_parser("status", help="read watchdog state without a model call")
    status_parser.add_argument("--state-dir", required=True, type=Path)
    status_parser.add_argument("--json", action="store_true")

    args = parser.parse_args()
    if args.command == "status":
        payload = status(args.state_dir.expanduser())
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"Claude delegation {payload.get('job_id', 'unknown')}: {payload['observed_state']}")
            print(f"Worker alive: {payload.get('worker_alive', False)}")
            print(f"Heartbeat: {payload.get('heartbeat_at', 'unavailable')}")
        return 1 if payload["observed_state"] in {"missing", "stale", "unmonitored", "failed", "incomplete"} else 0

    try:
        job = read_json(args.job.expanduser())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"invalid job file: {type(exc).__name__}", file=sys.stderr)
        return 2
    if args.command == "preflight":
        payload = preflight(job)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"Claude delegation preflight {job.get('job_id', 'unknown')}: {'READY' if payload['ready'] else 'NOT READY'}")
            for name, check in payload.get("checks", {}).items():
                print(f"- {name}: {check.get('state', 'unknown')}")
        return 0 if payload["ready"] else 1
    return run_job(job)


if __name__ == "__main__":
    raise SystemExit(main())
