#!/usr/bin/env python3
"""Portable supervisor packet preparation and receipt reconciliation.

Never launches providers, executes evidence commands or grants authority.
Capability observations and review attestations still require trusted review.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess


FIELDS = frozenset({"schema_version", "task_id", "goal", "issue", "supervisor", "worker",
    "worktree", "branch", "base_revision", "expires_at", "finish", "owned_paths", "exclusions",
    "acceptance_ids", "required_capabilities", "adapter_identity", "brief_file", "handback_file",
    "state_dir", "brief_sha256", "max_correction_rounds"})
IDENTITY_FIELDS = {"tool", "tool_version", "provider", "model", "configuration_id", "environment_id"}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def safe_relative(value):
    if not nonempty(value) or "\\" in value or "\x00" in value:
        return False
    p = PurePosixPath(value)
    return (not p.is_absolute() and bool(p.parts) and ".." not in p.parts
            and not any(part.startswith(".env") or part in {"live", ".git"} for part in p.parts)
            and not any(c in value for c in "*?[]"))


def validate_packet(p, *, now=None):
    if not isinstance(p, dict):
        return ["packet.object_required"]
    errors = []
    if set(p) != FIELDS:
        errors.append("packet.fields")
    if type(p.get("schema_version")) is not int or p["schema_version"] != 1:
        errors.append("packet.version")
    for key in ("task_id", "goal", "issue", "supervisor", "worker", "worktree", "branch"):
        if not nonempty(p.get(key)):
            errors.append("packet."+key)
    if not isinstance(p.get("base_revision"), str) or not re.fullmatch(r"[a-f0-9]{40}", p["base_revision"]):
        errors.append("packet.base_revision")
    if p.get("finish") not in ("local implementation", "local proof"):
        errors.append("packet.finish")
    if nonempty(p.get("worktree")) and not Path(p["worktree"]).is_absolute():
        errors.append("packet.worktree")
    try:
        expiry = datetime.fromisoformat(p["expires_at"].replace("Z", "+00:00"))
        if expiry.tzinfo is None or expiry <= (now or datetime.now(timezone.utc)):
            errors.append("packet.expired")
    except (KeyError, ValueError, TypeError, AttributeError):
        errors.append("packet.expires_at")
    for key in ("owned_paths", "exclusions", "acceptance_ids", "required_capabilities"):
        value = p.get(key)
        if not isinstance(value, list) or not value or not all(nonempty(v) for v in value):
            errors.append("packet."+key)
        elif len(set(value)) != len(value):
            errors.append("packet."+key+".duplicates")
    if isinstance(p.get("owned_paths"), list) and any(not safe_relative(v) for v in p["owned_paths"]):
        errors.append("packet.owned_paths.unsafe")
    for key in ("brief_file", "handback_file", "state_dir"):
        value = p.get(key)
        if not safe_relative(value) or not value.startswith(".agent-os/delegations/"):
            errors.append("packet."+key)
    if not isinstance(p.get("brief_sha256"), str) or not re.fullmatch(r"[a-f0-9]{64}", p["brief_sha256"]):
        errors.append("packet.brief_sha256")
    identity = p.get("adapter_identity")
    if not isinstance(identity, dict) or set(identity) != IDENTITY_FIELDS or not all(nonempty(v) for v in identity.values()):
        errors.append("packet.adapter_identity")
    rounds = p.get("max_correction_rounds")
    if type(rounds) is not int or not 0 <= rounds <= 3:
        errors.append("packet.max_correction_rounds")
    return errors


def contract_digest(packet):
    return hashlib.sha256(json.dumps(packet, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def render_brief(p):
    return "\n".join([
        "# Delegated work packet", "", p["goal"], "",
        "This packet is not authorization; the supervisor must verify the owner's boundary.",
        "Task: "+p["task_id"], "Supervisor: "+p["supervisor"], "Worker: "+p["worker"],
        "Contract SHA256: "+contract_digest(p), "Finish: "+p["finish"],
        "Worktree: "+p["worktree"], "Branch: "+p["branch"], "Base revision: "+p["base_revision"],
        "Owned paths: "+", ".join(p["owned_paths"]), "Exclusions: "+"; ".join(p["exclusions"]),
        "Acceptance IDs: "+", ".join(p["acceptance_ids"]),
        "Read the task's source-backed build brief: "+p["brief_file"],
        "Return the completion_receipt.py format at: "+p["handback_file"],
        "Do not commit, push, merge, deploy, change production, read secrets or delete unrelated work.",
        "Ordinary test failures: diagnose and continue within scope. New scope: route to supervisor.",
        "A worker exit or accepted-shaped receipt is not independent semantic acceptance.",
        "No automatic restart after timeout; reconcile Git, worker state and evidence first.",
        "Unknown usage counters stay unavailable. Do not claim savings from transferred work.", ""])


def binding_errors(p, receipt, expected_digest, expected_target_revision):
    errors = []
    if expected_digest != contract_digest(p):
        errors.append("contract.changed")
    if not isinstance(receipt, dict):
        return errors+["receipt.object_required"]
    if receipt.get("task_id") != p["task_id"]:
        errors.append("receipt.task_id")
    if receipt.get("contract_sha256") != expected_digest:
        errors.append("receipt.contract_sha256")
    worker = receipt.get("worker")
    if not isinstance(worker, dict) or worker.get("id") != p["worker"]:
        errors.append("receipt.worker")
    if not nonempty(expected_target_revision) or receipt.get("target") != {"state": "changed_locally", "revision": expected_target_revision, "environment": p["worktree"]}:
        errors.append("receipt.target")
    rows = receipt.get("acceptance")
    ids = [r.get("id") for r in rows if isinstance(r, dict)] if isinstance(rows, list) else []
    if len(ids) != len(p["acceptance_ids"]) or any(not isinstance(x, str) for x in ids) or set(ids) != set(p["acceptance_ids"]):
        errors.append("receipt.acceptance_ids")
    return errors


def next_action(verdict, correction_round, maximum):
    if verdict == "accepted":
        return "independent_evidence_review"
    if verdict == "returned":
        return "supervisor_review_correction" if correction_round < maximum else "reconcile_before_new_packet"
    return "await_evidence"


def worktree_errors(p):
    """Check exact current checkout without reading user content or executing a worker."""
    try:
        root = Path(p["worktree"]).resolve(strict=True)
        def git(*args):
            return subprocess.check_output(["git", "-C", str(root), *args], text=True, stderr=subprocess.DEVNULL, timeout=10).strip()
        if Path(git("rev-parse", "--show-toplevel")).resolve() != root:
            return ["worktree.root_mismatch"]
        if git("branch", "--show-current") != p["branch"] or git("rev-parse", "HEAD") != p["base_revision"]:
            return ["worktree.identity_changed"]
        for value in p["owned_paths"]:
            resolved = (root/value).resolve()
            if not resolved.is_relative_to(root) or not safe_relative(resolved.relative_to(root).as_posix()):
                return ["worktree.owned_path_escape"]
        for key in ("brief_file", "handback_file", "state_dir"):
            resolved = (root/p[key]).resolve()
            if not resolved.is_relative_to(root/".agent-os"/"delegations") or not safe_relative(resolved.relative_to(root).as_posix()):
                return ["worktree.runtime_escape"]
            if key == "brief_file":
                vetted_brief = resolved
        with vetted_brief.open("rb") as stream:
            brief = stream.read(1048577)
        if len(brief) > 1048576 or hashlib.sha256(brief).hexdigest() != p["brief_sha256"]:
            return ["worktree.brief_changed"]
        return []
    except (OSError, ValueError, subprocess.SubprocessError):
        return ["worktree.unavailable"]


def read_safe_json(path):
    resolved = path.resolve()
    if resolved.suffix != ".json" or any(part.startswith(".env") or part == "live" for part in resolved.parts):
        raise ValueError("protected_input")
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate_key")
            result[key] = value
        return result
    with resolved.open("rb") as stream:
        raw = stream.read(1048577)
    if len(raw) > 1048576:
        raise ValueError("oversized")
    try:
        value = json.loads(raw, object_pairs_hook=unique_keys)
    except RecursionError:
        raise ValueError("nested_input") from None
    stack = [(value, 0)]
    while stack:
        item, depth = stack.pop()
        if depth > 64:
            raise ValueError("nested_input")
        children = item.values() if isinstance(item, dict) else item if isinstance(item, list) else []
        stack.extend((child, depth+1) for child in children)
    return value


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, '{"errors":["invalid_cli_arguments"],"authority_granted":false,"semantic_acceptance_proven":false}\n')


def main():
    parser = SafeParser(description=__doc__)
    parser.add_argument("action", choices=["check", "brief", "preflight", "assess-handback"])
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--capabilities", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--expected-contract-sha256")
    parser.add_argument("--expected-target-revision")
    parser.add_argument("--correction-round", type=int, default=0)
    args = parser.parse_args()
    try:
        p = read_safe_json(args.packet)
        errors = validate_packet(p)
        result = {"errors": errors, "authority_granted": False, "semantic_acceptance_proven": False}
        if errors:
            print(json.dumps(result)); return 2
        result["contract_sha256"] = contract_digest(p)
        if args.action == "brief":
            print(render_brief(p)); return 0
        if args.action == "preflight":
            from agent_os_adapter_contract import evaluate_capabilities
            errors.extend(worktree_errors(p))
            if args.capabilities is None:
                errors.append("capabilities.required")
            else:
                evaluated = evaluate_capabilities(read_safe_json(args.capabilities), p["required_capabilities"], expected_identity=p["adapter_identity"])
                if not evaluated["ready"]:
                    errors.append("capabilities.not_ready")
            result["next"] = "supervisor_verify_access_and_launch_adapter" if not errors else "resolve_preflight"
        if args.action == "assess-handback":
            from completion_receipt import validate_receipt
            errors.extend(worktree_errors(p))
            if args.receipt is None or not args.expected_contract_sha256 or not args.expected_target_revision or args.correction_round < 0:
                errors.append("reconciliation.arguments")
            else:
                receipt = read_safe_json(args.receipt)
                errors.extend(validate_receipt(receipt))
                errors.extend(binding_errors(p, receipt, args.expected_contract_sha256, args.expected_target_revision))
                if not errors:
                    result["next"] = next_action(receipt["review"]["verdict"], args.correction_round, p["max_correction_rounds"])
        print(json.dumps(result, sort_keys=True))
        return 1 if errors else 0
    except (OSError, ValueError, TypeError, KeyError, ImportError, RecursionError):
        print(json.dumps({"errors": ["input_or_dependency_unavailable"], "authority_granted": False, "semantic_acceptance_proven": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
