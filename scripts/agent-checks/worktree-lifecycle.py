#!/usr/bin/env python3
"""Lease, classify, seed and safely reclaim Sifututor Git worktrees.

The tool is deliberately fail-safe:

* inventory/propose never mutate repositories;
* an active or parked lease blocks reclamation;
* dirty, unmerged, locked, primary, process-owned or uncertain work blocks;
* removal re-runs every check and requires the exact expected HEAD;
* branches are never deleted;
* dependency seeding requires identical lockfiles and an empty target.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
from typing import Any


SCHEMA_VERSION = 1
DEFAULT_TTL_HOURS = 72
PROJECTS = (
    ".", "kelas", "sifu-tutor", "ripple-suite", "sifututor_tutor",
    "sifututor_parent", "lls", "lls-frontend", "lls-mobile",
    "creative-hub", "finch-inbox", "cx-call-capture-android",
    "sims-owner-analytics",
)
LOCKFILES = (
    "pnpm-lock.yaml", "package-lock.json", "yarn.lock", "bun.lock",
    "composer.lock",
)
DEPENDENCY_DIRS = {
    "node": "node_modules",
    "composer": "vendor",
}
GENERATED_IGNORED_ROOTS = {
    "node_modules", "vendor", ".next", ".nuxt", "dist", "build",
    "coverage", ".cache", ".turbo", ".parcel-cache", "target",
    ".gradle", "Pods", "DerivedData",
}


class LifecycleError(RuntimeError):
    """A safe refusal with a user-readable reason."""


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def iso(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).isoformat()


def parse_time(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def run(*args: str, cwd: Path | None = None, check: bool = True,
        timeout: int = 120) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(args), cwd=cwd, text=True, capture_output=True, timeout=timeout,
        check=False,
    )
    if check and result.returncode != 0:
        raise LifecycleError(f"Command failed without exposing raw output: {args[0]}")
    return result


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run("git", "-C", str(repo), *args, check=check)


def default_state_dir() -> Path:
    configured = os.environ.get("SIFUTUTOR_WORKTREE_STATE_DIR", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return Path.home() / ".local" / "state" / "sifututor-agent-os" / "worktrees"


def safe_key(path: Path) -> str:
    return hashlib.sha256(str(path.resolve()).encode()).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".tmp-", dir=path.parent)
    tmp = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write("\n")
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)


class LeaseStore:
    def __init__(self, state_dir: Path):
        self.root = state_dir.resolve()
        self.leases = self.root / "leases"
        self.lock_path = self.root / ".lease.lock"

    def path_for(self, worktree: Path) -> Path:
        return self.leases / f"{safe_key(worktree)}.json"

    def _read(self, worktree: Path) -> dict[str, Any] | None:
        try:
            value = json.loads(self.path_for(worktree).read_text())
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return None
        return value if isinstance(value, dict) else None

    def _locked(self):
        self.root.mkdir(parents=True, exist_ok=True)
        handle = self.lock_path.open("a+")
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        return handle

    def create(self, *, repo: Path, worktree: Path, owner: str, session: str,
               purpose: str, issue: str, cleanup_condition: str,
               ttl_hours: int = DEFAULT_TTL_HOURS,
               now: dt.datetime | None = None) -> dict[str, Any]:
        now = now or utc_now()
        repo, worktree = repo.resolve(), worktree.resolve()
        if not repo.is_dir() or not worktree.is_dir():
            raise LifecycleError("Repository and worktree must both exist")
        repo_common = git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()
        worktree_common = git(worktree, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()
        if Path(repo_common).resolve() != Path(worktree_common).resolve():
            raise LifecycleError("Worktree does not belong to the declared repository")
        if not all((owner.strip(), session.strip(), purpose.strip(), cleanup_condition.strip())):
            raise LifecycleError("Owner, session, purpose and cleanup condition are required")
        if ttl_hours < 1:
            raise LifecycleError("TTL must be at least one hour")
        branch = git(worktree, "symbolic-ref", "--quiet", "--short", "HEAD", check=False).stdout.strip()
        head = git(worktree, "rev-parse", "HEAD").stdout.strip()
        handle = self._locked()
        try:
            # Reclamation uses this lock too. A checkout may have disappeared
            # while this caller waited; never register ownership of a removed path.
            if not worktree.is_dir():
                raise LifecycleError("Worktree disappeared before lease registration")
            existing = self._read(worktree)
            if self.path_for(worktree).exists() and not valid_lease(existing, worktree):
                raise LifecycleError("Existing lease record is invalid; refusing to overwrite it")
            if existing and lease_is_live(existing, now) and existing.get("session") != session:
                raise LifecycleError("Worktree already has a live lease owned by another session")
            value = {
                "schema_version": SCHEMA_VERSION,
                "repository": str(repo),
                "worktree": str(worktree),
                "branch": branch or "detached",
                "head_at_registration": head,
                "owner": owner.strip(),
                "session": session.strip(),
                "purpose": purpose.strip(),
                "issue": issue.strip(),
                "cleanup_condition": cleanup_condition.strip(),
                "status": "active",
                "created_at": existing.get("created_at", iso(now)) if existing else iso(now),
                "heartbeat_at": iso(now),
                "ttl_hours": ttl_hours,
            }
            atomic_json(self.path_for(worktree), value)
            return value
        finally:
            handle.close()

    def heartbeat(self, worktree: Path, session: str,
                  now: dt.datetime | None = None) -> dict[str, Any]:
        now = now or utc_now()
        handle = self._locked()
        try:
            value = self._read(worktree)
            if not valid_lease(value, worktree):
                raise LifecycleError("No valid lease exists for this worktree")
            if value["session"] != session:
                raise LifecycleError("Only the owning session may refresh this lease")
            if value["status"] != "active":
                raise LifecycleError("Only an active lease may be refreshed")
            value["heartbeat_at"] = iso(now)
            atomic_json(self.path_for(worktree), value)
            return value
        finally:
            handle.close()

    def set_status(self, worktree: Path, session: str, status: str,
                   reason: str = "", now: dt.datetime | None = None) -> dict[str, Any]:
        if status not in {"active", "parked", "released"}:
            raise LifecycleError("Unsupported lease status")
        now = now or utc_now()
        handle = self._locked()
        try:
            value = self._read(worktree)
            if not valid_lease(value, worktree):
                raise LifecycleError("No valid lease exists for this worktree")
            if value["session"] != session:
                raise LifecycleError("Only the owning session may change this lease")
            value["status"] = status
            value["heartbeat_at"] = iso(now)
            if reason.strip():
                value["status_reason"] = reason.strip()
            atomic_json(self.path_for(worktree), value)
            return value
        finally:
            handle.close()

    def get(self, worktree: Path) -> dict[str, Any] | None:
        return self._read(worktree)


def valid_lease(value: Any, worktree: Path | None = None) -> bool:
    if not isinstance(value, dict) or value.get("schema_version") != SCHEMA_VERSION:
        return False
    required = ("repository", "worktree", "owner", "session", "purpose",
                "cleanup_condition", "status", "heartbeat_at", "ttl_hours")
    if not all(value.get(key) not in (None, "") for key in required):
        return False
    if value.get("status") not in {"active", "parked", "released"}:
        return False
    if not isinstance(value.get("ttl_hours"), int) or value["ttl_hours"] < 1:
        return False
    try:
        parse_time(str(value["heartbeat_at"]))
    except (ValueError, TypeError):
        return False
    if worktree is not None and value.get("worktree") != str(worktree.resolve()):
        return False
    return True


def lease_is_live(value: Any, now: dt.datetime | None = None) -> bool:
    now = now or utc_now()
    if not valid_lease(value):
        return False
    if value["status"] == "parked":
        return True
    if value["status"] != "active":
        return False
    expiry = parse_time(value["heartbeat_at"]) + dt.timedelta(hours=value["ttl_hours"])
    return now <= expiry


def parse_worktrees(repo: Path) -> list[dict[str, Any]]:
    output = git(repo, "worktree", "list", "--porcelain").stdout
    records = []
    for block in (part for part in output.strip().split("\n\n") if part.strip()):
        record: dict[str, Any] = {}
        for line in block.splitlines():
            if " " in line:
                key, value = line.split(" ", 1)
                record[key] = value
            else:
                record[line] = True
        if record.get("worktree"):
            record["path"] = Path(record["worktree"])
            record["branch"] = str(record.get("branch", "detached")).removeprefix("refs/heads/")
            records.append(record)
    return records


def ignored_paths(worktree: Path) -> list[str]:
    output = git(
        worktree, "status", "--porcelain=v1", "--ignored=matching",
        "--untracked-files=all",
    ).stdout
    return [line[3:] for line in output.splitlines() if line.startswith("!! ")]


def ignored_path_is_generated(path: str) -> bool:
    normalized = path.rstrip("/")
    parts = Path(normalized).parts
    first = parts[0] if parts else ""
    return (
        first in GENERATED_IGNORED_ROOTS
        or "__pycache__" in parts
        or normalized.endswith((".pyc", ".pyo"))
    )


def active_task(worktree: Path, base_ref: str) -> tuple[str, str]:
    path = worktree / ".claude" / "tasks" / "active.json"
    try:
        raw = path.read_text()
        value = json.loads(raw)
    except FileNotFoundError:
        return "missing", ""
    except (json.JSONDecodeError, OSError):
        return "invalid", ""
    if not isinstance(value, dict):
        return "invalid", ""
    task = value.get("activeTask") if isinstance(value, dict) else None
    task = str(task).strip() if task else ""
    base = git(worktree, "show", f"{base_ref}:.claude/tasks/active.json", check=False)
    if base.returncode == 0 and base.stdout == raw:
        return "inherited", task
    return "active", task


def process_uses_path(path: Path) -> bool | None:
    if shutil.which("lsof") is None:
        return None
    result = run("lsof", "-a", "-d", "cwd", "-Fn", check=False, timeout=30)
    if result.returncode not in (0, 1):
        return None
    target = str(path.resolve())
    for line in result.stdout.splitlines():
        if not line.startswith("n"):
            continue
        candidate = line[1:]
        if candidate == target or candidate.startswith(target + os.sep):
            return True
    return False


def head_is_merged(worktree: Path, base_ref: str) -> bool | None:
    result = git(worktree, "merge-base", "--is-ancestor", "HEAD", base_ref, check=False)
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    return None


def inspect_worktree(repo: Path, record: dict[str, Any], store: LeaseStore,
                     *, base_ref: str = "origin/main",
                     now: dt.datetime | None = None,
                     check_process: bool = False) -> dict[str, Any]:
    now = now or utc_now()
    repo = repo.resolve()
    path = Path(record["path"])
    result: dict[str, Any] = {
        "repository": str(repo), "worktree": str(path),
        "branch": record.get("branch", "detached"),
        "head": record.get("HEAD", ""), "classification": "preserve",
        "reasons": [], "recovery": "",
    }
    if not path.is_dir():
        result.update(classification="prunable_registration")
        result["reasons"].append("registered path is missing; Git branch/commit refs remain")
        result["recovery"] = f"git -C {repo} worktree prune --expire now"
        return result
    path = path.resolve()
    result["worktree"] = str(path)
    if path == repo:
        result["reasons"].append("primary repository checkout")
        return result
    if record.get("locked"):
        result["reasons"].append("Git worktree is locked")
        return result
    task_state, task = active_task(path, base_ref)
    if task_state == "invalid":
        result["reasons"].append("active task state is invalid; absence cannot be proven")
        return result
    if task_state == "inherited" and task:
        result["inherited_task_pointer"] = task
        result["reasons"].append("base branch task pointer is unchanged and not worktree-specific")
    elif task:
        result["reasons"].append("active task pointer exists")
        result["active_task"] = task
        return result
    status = git(path, "status", "--porcelain=v1", "--untracked-files=all").stdout
    if status.strip():
        result["reasons"].append("tracked or untracked changes exist")
        return result
    ignored = ignored_paths(path)
    blocked_ignored = [item for item in ignored if not ignored_path_is_generated(item)]
    if blocked_ignored:
        result["reasons"].append("non-generated ignored files exist")
        result["ignored_blocker_count"] = len(blocked_ignored)
        return result
    lease = store.get(path)
    if store.path_for(path).exists() and lease is None:
        result["reasons"].append("lease record is unreadable or malformed")
        return result
    if lease is not None and not valid_lease(lease, path):
        result["reasons"].append("lease record is invalid")
        return result
    if lease_is_live(lease, now):
        result["reasons"].append(f"{lease['status']} lease owned by {lease['owner']}")
        return result
    if lease and lease.get("status") == "active":
        result["reasons"].append("active lease heartbeat expired; explicit release or reassignment is required")
        result["stale_lease"] = True
        return result
    merged = head_is_merged(path, base_ref)
    if merged is not True:
        result["reasons"].append(
            "HEAD is not contained by the configured base" if merged is False
            else "base ancestry could not be verified"
        )
        return result
    process = process_uses_path(path) if check_process else None
    result["process_check"] = (
        "clear" if process is False else "in_use" if process is True else "not_checked"
    )
    if process is True:
        result["reasons"].append("a running process has its cwd inside the worktree")
        return result
    if check_process and process is None:
        result["reasons"].append("process ownership could not be verified")
        return result
    result["classification"] = "reclaim_candidate"
    result["reasons"].append("clean, unlocked, inactive and fully contained by base")
    if ignored:
        result["reasons"].append("only recognized reproducible ignored directories exist")
    result["recovery"] = (
        f"git -C {repo} worktree add {path} "
        f"{result['branch'] if result['branch'] != 'detached' else '--detach ' + result['head']}"
    )
    return result


def inventory_repository(repo: Path, store: LeaseStore, *, base_ref: str,
                         check_process: bool = False) -> list[dict[str, Any]]:
    return [
        inspect_worktree(repo, record, store, base_ref=base_ref,
                         check_process=check_process)
        for record in parse_worktrees(repo)
    ]


def discover_repositories(workspace: Path) -> list[Path]:
    repositories = []
    for relative in PROJECTS:
        candidate = (workspace / relative).resolve()
        if (candidate / ".git").exists():
            repositories.append(candidate)
    return repositories


def disk_kib(path: Path) -> int:
    result = run("du", "-sk", str(path), check=False, timeout=120)
    if result.returncode != 0:
        return 0
    try:
        return int(result.stdout.split()[0])
    except (ValueError, IndexError):
        return 0


def reclaim(repo: Path, worktree: Path, expected_head: str, store: LeaseStore,
            *, base_ref: str, apply: bool) -> dict[str, Any]:
    repo, worktree = repo.resolve(), worktree.resolve()
    match = next((item for item in parse_worktrees(repo)
                  if Path(item["path"]).resolve() == worktree), None)
    if match is None:
        raise LifecycleError("Target is not a registered worktree of this repository")
    checked = inspect_worktree(repo, match, store, base_ref=base_ref, check_process=True)
    actual_head = git(worktree, "rev-parse", "HEAD").stdout.strip()
    if not expected_head or actual_head != expected_head:
        raise LifecycleError("Target HEAD changed or does not match the required exact value")
    if checked["classification"] != "reclaim_candidate":
        raise LifecycleError("Target failed safe reclamation checks")
    size_before = disk_kib(worktree)
    outcome = {
        "action": "remove-worktree", "applied": False,
        "repository": str(repo), "worktree": str(worktree),
        "head": actual_head, "size_kib_before": size_before,
        "recovery": checked["recovery"], "reasons": checked["reasons"],
    }
    if apply:
        handle = store._locked()
        try:
            # Measurement can take minutes. Check again after it, under the
            # same lock used by cooperating lease writers, until Git finishes.
            fresh = next((item for item in parse_worktrees(repo)
                          if Path(item["path"]).resolve() == worktree), None)
            if fresh is None:
                raise LifecycleError("Target registration changed before removal")
            final = inspect_worktree(repo, fresh, store, base_ref=base_ref, check_process=True)
            if final["classification"] != "reclaim_candidate":
                raise LifecycleError("Target failed final reclamation checks")
            if git(worktree, "rev-parse", "HEAD").stdout.strip() != expected_head:
                raise LifecycleError("Target HEAD changed before removal")
            git(repo, "worktree", "remove", str(worktree))
            outcome["applied"] = True
            outcome["removed"] = not worktree.exists()
        finally:
            handle.close()
    return outcome


def prune_missing_registrations(repo: Path, *, apply: bool) -> dict[str, Any]:
    repo = repo.resolve()
    missing = [
        str(item["path"]) for item in parse_worktrees(repo)
        if not Path(item["path"]).is_dir()
    ]
    outcome = {
        "action": "prune-missing-registrations", "applied": False,
        "repository": str(repo), "missing": missing,
        "safety": "removes stale Git metadata only; branches and commits are retained",
    }
    if apply and missing:
        git(repo, "worktree", "prune", "--expire", "now")
        outcome["applied"] = True
        outcome["remaining_missing"] = [
            str(item["path"]) for item in parse_worktrees(repo)
            if not Path(item["path"]).is_dir()
        ]
    return outcome


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def lock_identity(worktree: Path) -> dict[str, str]:
    return {
        name: file_sha256(worktree / name)
        for name in LOCKFILES if (worktree / name).is_file()
    }


def dependency_kind(worktree: Path) -> str:
    locks = lock_identity(worktree)
    if "composer.lock" in locks:
        return "composer"
    if any(name in locks for name in LOCKFILES[:4]):
        return "node"
    return ""


def dependency_donors(repo: Path, target: Path) -> list[dict[str, Any]]:
    target, target_locks = target.resolve(), lock_identity(target)
    kind = dependency_kind(target)
    if not kind or not target_locks:
        return []
    dep_dir = DEPENDENCY_DIRS[kind]
    donors = []
    for record in parse_worktrees(repo.resolve()):
        path = Path(record["path"])
        if not path.is_dir() or path.resolve() == target:
            continue
        if lock_identity(path) == target_locks and (path / dep_dir).is_dir():
            donors.append({
                "worktree": str(path.resolve()), "kind": kind,
                "dependency_dir": dep_dir,
                "lock_identity": target_locks,
            })
    return donors


def seed_dependencies(source: Path, target: Path, *, apply: bool) -> dict[str, Any]:
    source, target = source.resolve(), target.resolve()
    source_kind, target_kind = dependency_kind(source), dependency_kind(target)
    if not source_kind or source_kind != target_kind:
        raise LifecycleError("Source and target dependency kinds do not match")
    source_locks, target_locks = lock_identity(source), lock_identity(target)
    if not source_locks or source_locks != target_locks:
        raise LifecycleError("Source and target lockfiles are not identical")
    name = DEPENDENCY_DIRS[source_kind]
    src, dst = source / name, target / name
    if not src.is_dir():
        raise LifecycleError("Source dependency directory does not exist")
    if dst.exists():
        raise LifecycleError("Target dependency directory already exists")
    if platform.system() == "Darwin":
        command = ["cp", "-cR", str(src), str(dst)]
    else:
        command = ["cp", "-a", "--reflink=auto", str(src), str(dst)]
    result = {
        "action": "seed-dependencies", "applied": False,
        "kind": source_kind, "source": str(src), "target": str(dst),
        "lock_identity": source_locks,
        "method": "copy-on-write clone when supported",
        "next_check": (
            "composer dump-autoload --no-interaction --no-scripts"
            if source_kind == "composer"
            else "run the project dependency/version check and focused build/tests"
        ),
    }
    if apply:
        completed = run(*command, check=False, timeout=600)
        if completed.returncode != 0:
            raise LifecycleError("Copy-on-write dependency seed failed")
        result["applied"] = True
    return result


def emit(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=default_state_dir())
    sub = parser.add_subparsers(dest="command", required=True)

    lease = sub.add_parser("lease")
    lease.add_argument("--repo", type=Path, required=True)
    lease.add_argument("--worktree", type=Path, required=True)
    lease.add_argument("--owner", required=True)
    lease.add_argument("--session", required=True)
    lease.add_argument("--purpose", required=True)
    lease.add_argument("--issue", default="")
    lease.add_argument("--cleanup-condition", required=True)
    lease.add_argument("--ttl-hours", type=int, default=DEFAULT_TTL_HOURS)

    heartbeat = sub.add_parser("heartbeat")
    heartbeat.add_argument("--worktree", type=Path, required=True)
    heartbeat.add_argument("--session", required=True)

    status = sub.add_parser("lease-status")
    status.add_argument("--worktree", type=Path, required=True)
    status.add_argument("--session", required=True)
    status.add_argument("--status", choices=("active", "parked", "released"), required=True)
    status.add_argument("--reason", default="")

    inventory = sub.add_parser("inventory")
    inventory.add_argument("--workspace", type=Path, required=True)
    inventory.add_argument("--base-ref", default="origin/main")

    remove = sub.add_parser("reclaim")
    remove.add_argument("--repo", type=Path, required=True)
    remove.add_argument("--worktree", type=Path, required=True)
    remove.add_argument("--expected-head", required=True)
    remove.add_argument("--base-ref", default="origin/main")
    remove.add_argument("--apply", action="store_true")

    prune = sub.add_parser("prune-missing")
    prune.add_argument("--repo", type=Path, required=True)
    prune.add_argument("--apply", action="store_true")

    donors = sub.add_parser("dependency-donors")
    donors.add_argument("--repo", type=Path, required=True)
    donors.add_argument("--worktree", type=Path, required=True)

    seed = sub.add_parser("seed-dependencies")
    seed.add_argument("--source", type=Path, required=True)
    seed.add_argument("--target", type=Path, required=True)
    seed.add_argument("--apply", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    store = LeaseStore(args.state_dir)
    try:
        if args.command == "lease":
            emit(store.create(
                repo=args.repo, worktree=args.worktree, owner=args.owner,
                session=args.session, purpose=args.purpose, issue=args.issue,
                cleanup_condition=args.cleanup_condition, ttl_hours=args.ttl_hours,
            ))
        elif args.command == "heartbeat":
            emit(store.heartbeat(args.worktree, args.session))
        elif args.command == "lease-status":
            emit(store.set_status(args.worktree, args.session, args.status, args.reason))
        elif args.command == "inventory":
            records = []
            for repo in discover_repositories(args.workspace.resolve()):
                records.extend(inventory_repository(repo, store, base_ref=args.base_ref))
            emit({
                "schema_version": SCHEMA_VERSION,
                "workspace": str(args.workspace.resolve()),
                "summary": {
                    "registered": len(records),
                    "reclaim_candidates": sum(item["classification"] == "reclaim_candidate" for item in records),
                    "prunable_registrations": sum(item["classification"] == "prunable_registration" for item in records),
                    "preserved": sum(item["classification"] == "preserve" for item in records),
                },
                "worktrees": records,
            })
        elif args.command == "reclaim":
            emit(reclaim(args.repo, args.worktree, args.expected_head, store,
                         base_ref=args.base_ref, apply=args.apply))
        elif args.command == "prune-missing":
            emit(prune_missing_registrations(args.repo, apply=args.apply))
        elif args.command == "dependency-donors":
            emit(dependency_donors(args.repo, args.worktree))
        elif args.command == "seed-dependencies":
            emit(seed_dependencies(args.source, args.target, apply=args.apply))
        return 0
    except LifecycleError as exc:
        print(f"worktree-lifecycle: refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
