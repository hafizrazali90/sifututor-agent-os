#!/usr/bin/env python3
"""Release readiness file for the home PC release loop (issue #350).

One JSON file describes a release: a checklist of items, each with an owner.
Items owned by `pc` are what the home PC loop works through. Items owned by
`hafiz` or `mac` are Hafiz's gates (review page confirmed, merge, production
deploy go, production smoke and monitoring, accepted). Gates are listed and
never counted into PC readiness, and the PC never does them.

    release_readiness.py init  --release NAME --repo agent-os|ripple-suite --branch B ... --out FILE
    release_readiness.py show  FILE
    release_readiness.py score FILE     PC readiness percent, open items, Hafiz gates
    release_readiness.py mark  FILE ID --status green|open|blocked|na [evidence flags]
    release_readiness.py next  FILE     the next open PC item whose dependencies are green

The scripted checks (pr_exists, commit_in_branch, file_contains,
commands_exit_zero, failing_first, verdict_file, all_of) are small and safe. A command's real
exit code is always kept: a failing command is never reported green.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import Any, Callable
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TEMPLATE_PATH = ROOT / "docs" / "agent-playbooks" / "templates" / "release-readiness.json"
MYT = ZoneInfo("Asia/Kuala_Lumpur")

SCHEMA = 1
OWNERS = ("pc", "hafiz", "mac")
GATE_OWNERS = ("hafiz", "mac")
STATUSES = ("open", "green", "blocked", "na")
ACTIONS = ("script", "builder", "reviewer", "none")
REPOS = ("agent-os", "ripple-suite")
LOOP_STATUSES = ("new", "running", "waiting", "ready_for_prod_go", "blocked", "stuck", "stopped")
ROUTES = ("staging-first", "direct-prod")
DIRECT_PROD_REASON = "Hafiz chose direct to production"
PROTECTED_BRANCHES = ("main", "master", "production", "prod", "staging")

# AGENTS.md names these exceptions for a missing browser or E2E run.
E2E_EXCEPTIONS = ("missing credential", "no safe representative data", "destructive workflow",
                  "tooling unavailable", "not user-facing")

VERDICT_RE = re.compile(r"Verdict:?\**\s*(ACCEPT|CHANGES NEEDED|BLOCKED)")
ENV_FILE_OK = (".env.example", ".env.sample", ".env.dist")

# What the PC must never run (merge, deploy, migrate, write production data).
# These patterns are shaped like commands, so ordinary prose such as "write the
# deploy plan" does not match. An item that matches becomes a Hafiz gate.
FORBIDDEN_PATTERNS: tuple[tuple[str, str], ...] = (
    ("merge", r"\bgh\s+pr\s+merge\b"),
    ("merge", r"\bgh\s+api\b[^\n]*\b(merge|deployments?)\b"),
    ("merge", r"\bgit\s+merge\b"),
    ("merge", r"\bgit\s+push\b[^\n]*(\b(main|master|production|prod)\b|--force|--delete|\s-f\b)"),
    ("migrate", r"\bartisan\s+migrate\b"),
    ("migrate", r"\b(prisma|knex|sequelize|typeorm|drizzle-kit)\b[^\n]*\bmigrat\w*"),
    ("migrate", r"\bdb:migrate\b|\bmigrate:(fresh|refresh|rollback|reset)\b|\balembic\s+upgrade\b|\bflyway\s+migrate\b"),
    ("deploy", r"\b(npm|pnpm|yarn)\s+(run\s+)?deploy\b"),
    ("deploy", r"\bdeploy[-_.\w]*\.sh\b|(^|\s)\./deploy\b|\bset-runtime-flag\b"),
    ("deploy", r"\bpm2\s+(restart|reload|start|deploy)\b|\bsystemctl\s+(restart|start|reload)\b"),
    ("deploy", r"\bkubectl\s+(apply|rollout|set|delete)\b|\bvercel\s+(--prod|deploy)\b"),
    ("deploy", r"(^|\s)(ssh|scp|sftp)\s|\brsync\b[^\n]*:"),
    ("production data write", r"\b(mysql|mysqldump|psql|mongosh|redis-cli|sqlcmd)\b"),
    ("production data write", r"(?-i:\b(DROP\s+TABLE|DELETE\s+FROM|INSERT\s+INTO|TRUNCATE\s+TABLE|UPDATE\s+\w+\s+SET)\b)"),
    ("production data write", r"\bcurl\b[^\n]*\s(-X|--request)\s*(POST|PUT|PATCH|DELETE)\b"),
)
FORBIDDEN_ACTION_WORDS = ("merge", "deploy", "migrate", "release", "publish", "prod_write", "production")
_FORBIDDEN_RE = tuple((name, re.compile(rx, re.IGNORECASE)) for name, rx in FORBIDDEN_PATTERNS)

SECRET_RES = (
    re.compile(r"(?i)\b([a-z0-9_]*(?:token|secret|passw(?:or)?d|apikey|api_key|private_key)[a-z0-9_]*)\s*[=:]\s*\S+"),
    re.compile(r"(?i)\bbearer\s+[a-z0-9._~+/=-]{8,}"),
    re.compile(r"\b(?:ghp|gho|ghs|github_pat)_[A-Za-z0-9_]{10,}"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}"),
)


class ReadinessError(ValueError):
    """The readiness file or a request about it is wrong."""


class StopRequested(Exception):
    """A STOP file appeared while a command was running."""


# ----------------------------------------------------------------- time ----

def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def myt_text(moment: dt.datetime | None = None) -> str:
    return (moment or now_utc()).astimezone(MYT).strftime("%d/%m/%Y %H:%M:%S MYT")


# ----------------------------------------------------------- file i/o ------

def load(path: Path | str) -> dict[str, Any]:
    try:
        data = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ReadinessError(f"cannot read readiness file {path}: {exc}") from exc
    if not isinstance(data, dict) or "items" not in data:
        raise ReadinessError(f"{path} is not a readiness file")
    return data


def save(path: Path | str, data: dict[str, Any]) -> None:
    """Checkpoint the file atomically: a reader sees the old file or the new one, never half."""
    target = Path(path)
    tmp = target.with_name(target.name + ".tmp")
    payload = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    with open(tmp, "w", encoding="utf-8") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, target)


def redact(text: str) -> str:
    for rx in SECRET_RES:
        text = rx.sub(lambda m: (m.group(1) + "=[redacted]") if m.re is SECRET_RES[0] else "[redacted]", text)
    return text


def tail(text: str, lines: int = 40) -> str:
    return "\n".join(redact(text).replace("\x00", "").splitlines()[-lines:])


# ----------------------------------------------------- item helpers --------

def item_map(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in data["items"]}


def is_applicable(item: dict[str, Any]) -> bool:
    return item.get("applicable", True) is not False and item.get("status") != "na"


def is_pc_item(item: dict[str, Any]) -> bool:
    return item.get("owner") == "pc"


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ("release", "repo", "branch", "items"):
        if not data.get(key):
            errors.append(f"missing {key}")
    if data.get("repo") and data["repo"] not in REPOS:
        errors.append(f"repo must be one of {', '.join(REPOS)}")
    if data.get("route") not in ROUTES:
        errors.append(f"route must be one of {', '.join(ROUTES)}")
    branch = data.get("branch", "")
    if branch in PROTECTED_BRANCHES or branch == str(data.get("base", "")).removeprefix("origin/"):
        errors.append("the release branch must not be the base or a protected branch")
    seen: set[str] = set()
    items = data.get("items", [])
    for item in items:
        iid = item.get("id")
        if not iid or iid in seen:
            errors.append(f"item id {iid!r} is missing or duplicated")
        seen.add(str(iid))
    for item in items:
        iid = item.get("id")
        if item.get("owner") not in OWNERS:
            errors.append(f"item {iid}: owner must be one of {', '.join(OWNERS)}")
        if item.get("status") not in STATUSES:
            errors.append(f"item {iid}: status must be one of {', '.join(STATUSES)}")
        # an action that names a forbidden step is allowed here so the loop can hand it to Hafiz
        if item.get("route_only") not in (None, *ROUTES):
            errors.append(f"item {iid}: route_only must be one of {', '.join(ROUTES)}")
        if is_pc_item(item) and item.get("action") not in ACTIONS + FORBIDDEN_ACTION_WORDS:
            errors.append(f"item {iid}: action must be one of {', '.join(ACTIONS)}")
        if (item.get("applicable") is False or item.get("status") == "na") and not item.get("na_reason"):
            errors.append(f"item {iid}: a not-applicable item needs an na_reason")
        for dep in item.get("depends_on", []):
            if dep not in seen:
                errors.append(f"item {iid}: depends_on {dep!r} does not exist")
    # a dependency cycle would make the loop wait forever
    graph = {i["id"]: i.get("depends_on", []) for i in items if "id" in i}
    visiting: set[str] = set()
    done: set[str] = set()

    def visit(node: str) -> bool:
        if node in done:
            return False
        if node in visiting:
            return True
        visiting.add(node)
        cyclic = any(visit(dep) for dep in graph.get(node, []) if dep in graph)
        visiting.discard(node)
        done.add(node)
        return cyclic

    if any(visit(node) for node in graph):
        errors.append("depends_on contains a cycle")
    return errors


# ------------------------------------------------------------ scoring ------

def is_gate(item: dict[str, Any]) -> bool:
    return item.get("owner") in GATE_OWNERS


def is_after_go(item: dict[str, Any]) -> bool:
    """The production deploy go, production smoke, monitoring and acceptance come after Hafiz's go."""
    return item.get("after_go") is True


def score(data: dict[str, Any]) -> dict[str, Any]:
    """Two measures.

    PC readiness: green items among applicable items owned by `pc`.
    Prod readiness: green items among ALL applicable items that must close BEFORE
    the production deploy go: the PC items plus the gates of the chosen route.
    Items after the go (deploy go, production smoke, monitoring, acceptance) are
    listed and never counted in either measure.
    """
    pc = [i for i in data["items"] if is_pc_item(i) and is_applicable(i)]
    green = [i for i in pc if i.get("status") == "green"]
    gates = [i for i in data["items"] if is_gate(i)]
    before = [i for i in data["items"] if is_applicable(i) and not is_after_go(i) and (is_pc_item(i) or is_gate(i))]
    before_green = [i for i in before if i.get("status") == "green"]
    total = len(pc)
    percent = 100.0 if total == 0 else round(100.0 * len(green) / total, 1)
    prod_total = len(before)
    return {
        "route": data.get("route", ""),
        "pc_total": total,
        "pc_green": len(green),
        "percent": percent,
        "ready": len(green) == total,
        "prod_total": prod_total,
        "prod_green": len(before_green),
        "prod_percent": 100.0 if prod_total == 0 else round(100.0 * len(before_green) / prod_total, 1),
        "prod_ready": len(before_green) == prod_total,
        "open_pc": [i["id"] for i in pc if i.get("status") == "open"],
        "blocked_pc": [i["id"] for i in pc if i.get("status") == "blocked"],
        "waiting_for": waiting_gates(data),
        "gates": [{"id": g["id"], "title": g.get("title", ""), "owner": g["owner"],
                   "status": g.get("status", "open"), "applicable": is_applicable(g),
                   "na_reason": g.get("na_reason", ""), "after_go": is_after_go(g),
                   "simulated": any(e.get("simulated") for e in g.get("evidence", []))} for g in gates],
    }


def waiting_gates(data: dict[str, Any]) -> list[str]:
    """Open gates that must close before the production go."""
    return [i["id"] for i in data["items"] if is_gate(i) and is_applicable(i) and not is_after_go(i)
            and i.get("status") == "open"]


def next_item(data: dict[str, Any]) -> dict[str, Any] | None:
    """The first open PC item, in file order, whose dependencies are all green or not applicable."""
    items = item_map(data)
    for item in data["items"]:
        if not (is_pc_item(item) and is_applicable(item) and item.get("status") == "open"):
            continue
        if all(items[d].get("status") in ("green", "na") or not is_applicable(items[d])
               for d in item.get("depends_on", [])):
            return item
    return None


def evidence_key(entry: dict[str, Any]) -> str:
    return json.dumps({k: v for k, v in entry.items() if k not in ("at", "at_utc")}, sort_keys=True)


def evidence_count(data: dict[str, Any]) -> int:
    return len({(i["id"], evidence_key(e)) for i in data["items"] for e in i.get("evidence", [])})


def add_evidence(item: dict[str, Any], **fields: Any) -> bool:
    """Append an evidence entry. A repeat of an identical entry is not new evidence."""
    entry = {k: v for k, v in fields.items() if v not in (None, "")}
    if not entry:
        raise ReadinessError("evidence needs at least one field")
    if any(evidence_key(e) == evidence_key(entry) for e in item.setdefault("evidence", [])):
        return False
    entry["at"] = myt_text()
    entry["at_utc"] = now_utc().isoformat()
    item["evidence"].append(entry)
    return True


def set_status(item: dict[str, Any], status: str, **evidence: Any) -> None:
    if status not in STATUSES:
        raise ReadinessError(f"status must be one of {', '.join(STATUSES)}")
    if status == "green" and is_pc_item(item) and not (item.get("evidence") or evidence):
        raise ReadinessError(f"item {item['id']}: a PC item cannot be green without evidence")
    if evidence:
        add_evidence(item, **evidence)
    item["status"] = status


# ------------------------------------------- route, gates and the inbox ------

def apply_route(data: dict[str, Any], route: str) -> None:
    """Recompute which route-only items apply. direct-prod marks the staging items not applicable."""
    if route not in ROUTES:
        raise ReadinessError(f"route must be one of {', '.join(ROUTES)}")
    data["route"] = route
    for item in data["items"]:
        only = item.get("route_only")
        if not only:
            continue
        if only == route:
            if item.get("na_by_route"):
                item["applicable"] = True
                item["status"] = item.pop("status_before_route_na", "open")
                item.pop("na_reason", None)
                item.pop("na_by_route", None)
        elif not item.get("na_by_route"):
            item["status_before_route_na"] = item.get("status", "open")
            item.update(status="na", applicable=False, na_by_route=True,
                        na_reason=DIRECT_PROD_REASON if route == "direct-prod" else f"the route is {route}")


def record_route(data: dict[str, Any], route: str, by: str) -> None:
    """Set the route, recompute applicability, and record who chose it and when (item G0)."""
    apply_route(data, route)
    history = data.setdefault("route_history", [])
    history.append({"route": route, "by": by or "unspecified", "at": myt_text()})
    gate = item_map(data).get("G0")
    if gate is not None:
        add_evidence(gate, note=f"route {route} chosen by {by or 'unspecified'} (record {len(history)})", by=by or "unspecified")
        gate["status"] = "green"


def close_gate_in_data(data: dict[str, Any], item_id: str, evidence: str, *, by: str = "", sha: str = "",
                       simulated: bool = False) -> None:
    """A person closes a gate by giving evidence. The PC's own items can never be closed this way."""
    item = item_map(data).get(item_id)
    if item is None:
        raise ReadinessError(f"no item {item_id}")
    if not is_gate(item):
        raise ReadinessError(f"item {item_id} is a PC item: the PC proves it, a person cannot close it with a gate")
    if not is_applicable(item):
        raise ReadinessError(f"item {item_id} is not applicable ({item.get('na_reason', '')})")
    if not evidence.strip():
        raise ReadinessError("a gate needs evidence: text or a path")
    fields: dict[str, Any] = {"note": ("SIMULATED: " if simulated else "") + evidence.strip(), "by": by or "unspecified"}
    if simulated:
        fields["simulated"] = True
    if sha:
        fields["sha"] = sha
    add_evidence(item, **fields)
    item["status"] = "green"
    if sha and item.get("records"):
        data[item["records"]] = sha


def apply_op(data: dict[str, Any], op: dict[str, Any]) -> None:
    kind = op.get("op")
    if kind == "gate":
        close_gate_in_data(data, str(op.get("item", "")), str(op.get("evidence", "")), by=str(op.get("by", "")),
                           sha=str(op.get("sha", "")), simulated=bool(op.get("simulated")))
    elif kind == "route":
        record_route(data, str(op.get("route", "")), str(op.get("by", "")))
    else:
        raise ReadinessError(f"unknown request {kind!r}")


def acquire_lock(directory: Path | str):
    """The loop's lock. Whoever holds it owns the checkpoint; everyone else queues a request in the inbox."""
    handle = open(Path(directory) / "loop.lock", "w")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        handle.close()
        return None
    return handle


def submit_op(directory: Path | str, op: dict[str, Any]) -> Path:
    inbox = Path(directory) / "inbox"
    inbox.mkdir(exist_ok=True)
    name = f"{now_utc().strftime('%Y%m%dT%H%M%S%f')}-{os.getpid()}.json"
    tmp = inbox / (name + ".tmp")
    tmp.write_text(json.dumps({**op, "submitted_at": myt_text()}))
    final = inbox / name
    os.replace(tmp, final)
    return final


def pending_ops(directory: Path | str) -> list[Path]:
    inbox = Path(directory) / "inbox"
    return sorted(inbox.glob("*.json")) if inbox.is_dir() else []


def drain_inbox(directory: Path | str, data: dict[str, Any]) -> tuple[list[Path], list[str]]:
    """Apply queued requests to `data`. The caller saves, then removes the returned files."""
    applied: list[Path] = []
    problems: list[str] = []
    for path in pending_ops(directory):
        try:
            apply_op(data, json.loads(path.read_text()))
            applied.append(path)
        except (ReadinessError, json.JSONDecodeError, OSError) as exc:
            problems.append(f"{path.name}: {exc}")
            rejected = path.parent / "rejected"
            rejected.mkdir(exist_ok=True)
            os.replace(path, rejected / path.name)
    return applied, problems


def request(readiness_path: Path | str, op: dict[str, Any]) -> str:
    """Apply a gate or route request now when no loop is running, otherwise queue it for the loop."""
    path = Path(readiness_path)
    if not path.is_file():
        raise ReadinessError(f"cannot read {path}")
    lock = acquire_lock(path.parent)
    if lock is None:
        probe = load(path)  # reject a bad request at once instead of silently queueing it
        apply_op(probe, op)
        submit_op(path.parent, op)
        return "queued"
    try:
        data = load(path)
        apply_op(data, op)
        save(path, data)
        return "applied"
    finally:
        lock.close()


# ------------------------------------------------- forbidden actions -------

def forbidden_text(text: str) -> str | None:
    for name, rx in _FORBIDDEN_RE:
        if rx.search(text):
            return name
    return None


def _check_commands(check: dict[str, Any] | None) -> list[str]:
    if not check:
        return []
    kind = check.get("type")
    if kind == "commands_exit_zero":
        return [c["run"] if isinstance(c, dict) else c for c in check.get("commands", [])]
    if kind == "all_of":
        return [cmd for sub in check.get("checks", []) for cmd in _check_commands(sub)]
    return []


def forbidden_in_item(item: dict[str, Any]) -> str | None:
    """Why the PC must not run this item, or None. A reason turns the item into a Hafiz gate."""
    action = str(item.get("action", ""))
    if action.lower() in FORBIDDEN_ACTION_WORDS:
        return f"action {action!r} would {action}; that is Hafiz's gate"
    for command in _check_commands(item.get("check")) + [str(item.get("instruction", ""))]:
        found = forbidden_text(command)
        if found:
            return f"it would {found} ({command.strip()[:80]})"
    return None


# ---------------------------------------------------------- shell ----------

class RealShell:
    """Runs a command without a shell. The real exit code always comes back."""

    def run(self, argv: list[str], cwd: Path | str | None = None,
            stop_check: Callable[[], bool] | None = None) -> tuple[int, str]:
        try:
            proc = subprocess.Popen(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        except FileNotFoundError:
            return 127, f"command not found: {argv[0]}"
        except OSError as exc:
            return 126, f"could not start {argv[0]}: {exc}"
        while True:
            try:
                out, _ = proc.communicate(timeout=2)
                return proc.returncode, out or ""
            except subprocess.TimeoutExpired:
                if stop_check and stop_check():
                    proc.terminate()
                    try:
                        proc.communicate(timeout=10)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.communicate()
                    raise StopRequested() from None


# ---------------------------------------------------------- checks ---------

class CheckContext:
    def __init__(self, data: dict[str, Any], pack_dir: Path, worktree: Path | None, repo_dir: Path | None,
                 shell: Any, stop_check: Callable[[], bool] | None = None) -> None:
        self.data = data
        self.pack_dir = Path(pack_dir)
        self.worktree = Path(worktree) if worktree else None
        self.repo_dir = Path(repo_dir) if repo_dir else None
        self.shell = shell
        self.stop_check = stop_check
        self.scratch_dir = self.pack_dir.parent / "scratch"


def result(ok: bool, summary: str, evidence: list[dict[str, Any]] | None = None, detail: str = "") -> dict[str, Any]:
    return {"ok": ok, "summary": summary, "evidence": evidence or [], "detail": detail}


def _safe_file(base: Path | None, relative: str) -> tuple[Path | None, str]:
    if base is None:
        return None, "the folder to read from is not available yet"
    if not relative or relative.startswith("/") or ".." in Path(relative).parts:
        return None, f"path {relative!r} leaves the release folder"
    name = Path(relative).name
    if name.startswith(".env") and name not in ENV_FILE_OK:
        return None, f"{name} is an environment file and is never read"
    if name.endswith((".pem", ".key")) or name.startswith("id_"):
        return None, f"{name} looks like a key file and is never read"
    return base / relative, ""


def check_file_contains(check: dict[str, Any], ctx: CheckContext) -> dict[str, Any]:
    base = ctx.pack_dir.parent if check.get("base") == "pack" else ctx.worktree
    path, problem = _safe_file(base, str(check.get("path", "")))
    if problem:
        return result(False, problem)
    try:
        text = path.read_text(errors="replace")
    except OSError:
        return result(False, f"{check['path']} does not exist")
    needles = list(check.get("needles", []))
    if "needle" in check:
        needles.append(check["needle"])
    missing = [n for n in needles if str(n) not in text]
    any_of = [str(n) for n in check.get("any_of", [])]
    if any_of and not any(n.lower() in text.lower() for n in any_of):
        missing.append("one of: " + " | ".join(any_of))
    evidence = [{"path": check["path"], "note": f"read {len(text)} characters"}]
    if missing:
        return result(False, f"{check['path']} is missing: {', '.join(map(str, missing))}", evidence)
    return result(True, f"{check['path']} has everything required", evidence)


def check_verdict_file(check: dict[str, Any], ctx: CheckContext) -> dict[str, Any]:
    base = ctx.pack_dir.parent if check.get("base", "pack") == "pack" else ctx.worktree
    path, problem = _safe_file(base, str(check.get("path", "")))
    if problem:
        return result(False, problem)
    try:
        text = path.read_text(errors="replace")
    except OSError:
        return result(False, f"{check['path']} does not exist yet")
    found = VERDICT_RE.search(text)
    verdict = found.group(1) if found else "none"
    evidence = [{"path": check["path"], "verdict": verdict}]
    if verdict == "ACCEPT":
        return result(True, "the reviewer said ACCEPT", evidence)
    return result(False, f"the reviewer verdict is {verdict}", evidence, detail=text)


def _commands(check: dict[str, Any]) -> list[tuple[str, str]]:
    out = []
    for entry in check.get("commands", []):
        if isinstance(entry, dict):
            out.append((entry["run"], entry.get("baseline_reason", "")))
        else:
            out.append((str(entry), ""))
    return out


def check_commands_exit_zero(check: dict[str, Any], ctx: CheckContext) -> dict[str, Any]:
    if ctx.worktree is None:
        return result(False, "the release worktree is not available")
    evidence: list[dict[str, Any]] = []
    failures: list[str] = []
    baseline: list[str] = []
    detail_parts: list[str] = []
    for command, baseline_reason in _commands(check):
        found = forbidden_text(command)
        if found:
            return result(False, f"refused: {command[:60]} would {found}")
        try:
            argv = shlex.split(command)
        except ValueError as exc:
            return result(False, f"cannot read command {command!r}: {exc}")
        if not argv:
            continue
        code, output = ctx.shell.run(argv, cwd=ctx.worktree, stop_check=ctx.stop_check)
        entry = {"command": command, "exit_code": code, "output_tail": tail(output, 12)}
        if code != 0 and baseline_reason:
            entry["baseline_failure"] = baseline_reason
            baseline.append(f"{command} (exit {code})")
        elif code != 0:
            failures.append(f"{command} (exit {code})")
            detail_parts.append(f"$ {command}\nexit code {code}\n{tail(output, 60)}")
        evidence.append(entry)
    summary = f"{len(evidence) - len(failures)} of {len(evidence)} commands passed"
    if baseline:
        summary += "; baseline failures reported separately: " + ", ".join(baseline)
    if failures:
        return result(False, summary + "; failed: " + ", ".join(failures), evidence, "\n\n".join(detail_parts))
    return result(True, summary, evidence)


def pr_numbers(check: dict[str, Any], data: dict[str, Any]) -> list[int]:
    value = check.get("pr", "@pr_numbers")
    raw = data.get("pr_numbers", []) if value == "@pr_numbers" else value
    return [int(n) for n in (raw if isinstance(raw, list) else [raw])]


def check_pr_exists(check: dict[str, Any], ctx: CheckContext) -> dict[str, Any]:
    github_repo, branch = ctx.data.get("github_repo", ""), ctx.data.get("branch", "")
    numbers = pr_numbers(check, ctx.data)
    evidence: list[dict[str, Any]] = []
    if not numbers:
        code, output = ctx.shell.run(["git", "ls-remote", "--exit-code", "--heads", "origin", branch],
                                     cwd=ctx.repo_dir, stop_check=ctx.stop_check)
        sha = output.split()[0] if code == 0 and output.split() else ""
        evidence.append({"command": f"git ls-remote --heads origin {branch}", "exit_code": code, "sha": sha})
        return result(code == 0 and bool(sha), f"branch {branch} " + (f"is on origin at {sha[:10]}" if sha else "is not on origin"), evidence)
    for number in numbers:
        code, output = ctx.shell.run(["gh", "pr", "view", str(number), "--repo", github_repo, "--json",
                                      "number,state,headRefName,headRefOid,baseRefName"],
                                     cwd=ctx.repo_dir, stop_check=ctx.stop_check)
        if code != 0:
            return result(False, f"gh pr view {number} failed (exit {code})",
                          evidence + [{"command": f"gh pr view {number}", "exit_code": code}], tail(output, 10))
        try:
            info = json.loads(output)
        except json.JSONDecodeError:
            return result(False, f"gh pr view {number} did not return readable data")
        evidence.append({"pr": number, "state": info.get("state"), "sha": info.get("headRefOid", ""),
                         "branch": info.get("headRefName")})
        if info.get("state") != "OPEN":
            return result(False, f"PR {number} is {info.get('state')}, not OPEN", evidence)
        if branch and info.get("headRefName") != branch:
            return result(False, f"PR {number} is on branch {info.get('headRefName')}, not {branch}", evidence)
        if not info.get("headRefOid"):
            return result(False, f"PR {number} has no head commit", evidence)
    shas = ", ".join(f"{e['pr']}@{e['sha'][:10]}" for e in evidence)
    return result(True, f"open PR with exact head commit: {shas}", evidence)


def check_commit_in_branch(check: dict[str, Any], ctx: CheckContext) -> dict[str, Any]:
    sha = str(check.get("sha", "")).strip()
    if sha.startswith("@"):
        sha = str(ctx.data.get(sha[1:], "")).strip()
        if not sha:
            return result(False, "no commit has been recorded for this check yet (close the staging deploy gate with --sha)")
    if not re.fullmatch(r"[0-9a-f]{7,40}", sha):
        return result(False, f"{sha!r} is not a commit SHA")
    branch = ctx.data.get("branch", "")
    code, output = ctx.shell.run(["git", "merge-base", "--is-ancestor", sha, f"origin/{branch}"],
                                 cwd=ctx.repo_dir, stop_check=ctx.stop_check)
    evidence = [{"command": f"git merge-base --is-ancestor {sha[:10]} origin/{branch}", "exit_code": code}]
    if code == 0:
        return result(True, f"the release contains commit {sha[:10]}", evidence)
    return result(False, f"the release does not contain commit {sha[:10]} (exit {code})", evidence, tail(output, 10))


TEST_FILE_RE = re.compile(r"(\.test\.|\.spec\.|/__tests__/|(^|/)test_[^/]*\.py$)")


def check_failing_first(check: dict[str, Any], ctx: CheckContext) -> dict[str, Any]:
    """Each new or changed test fails on the release base and passes on the release.

    The loop does this itself, so the proof does not rest on a builder's word:
    it copies the release's test files onto a scratch checkout of the merge
    base, expects the test command to fail there, then expects it to pass in
    the release worktree.
    """
    if ctx.worktree is None or ctx.repo_dir is None:
        return result(False, "the release worktree is not available")
    base, branch = str(ctx.data.get("base", "origin/main")), str(ctx.data.get("branch", ""))
    shell, cwd = ctx.shell, ctx.repo_dir
    code, listing = shell.run(["git", "diff", "--name-only", "--diff-filter=AM", f"{base}...origin/{branch}"],
                              cwd=cwd, stop_check=ctx.stop_check)
    if code != 0:
        return result(False, f"could not list the release's changed files (exit {code})", detail=tail(listing, 10))
    files = [f for f in listing.splitlines() if TEST_FILE_RE.search(f)]
    if not files:
        return result(False, "the release adds or changes no test file, so failing-first cannot be shown")
    code, merge_base = shell.run(["git", "merge-base", base, f"origin/{branch}"], cwd=cwd, stop_check=ctx.stop_check)
    if code != 0 or not merge_base.strip():
        return result(False, f"no merge base between {base} and {branch} (exit {code})")
    scratch = ctx.scratch_dir / "failing-first"
    evidence: list[dict[str, Any]] = []
    shell.run(["git", "worktree", "remove", "--force", str(scratch)], cwd=cwd, stop_check=ctx.stop_check)
    scratch.parent.mkdir(parents=True, exist_ok=True)
    try:
        code, output = shell.run(["git", "worktree", "add", "--detach", str(scratch), merge_base.strip()],
                                 cwd=cwd, stop_check=ctx.stop_check)
        if code != 0:
            return result(False, f"could not make the scratch checkout (exit {code})", detail=tail(output, 10))
        code, output = shell.run(["git", "checkout", f"origin/{branch}", "--", *files], cwd=scratch, stop_check=ctx.stop_check)
        if code != 0:
            return result(False, f"could not copy the test files to the base (exit {code})", detail=tail(output, 10))
        for install in check.get("install", []):
            code, output = shell.run(shlex.split(install), cwd=scratch, stop_check=ctx.stop_check)
            evidence.append({"command": install + " (on the base)", "exit_code": code})
            if code != 0:
                return result(False, f"{install} failed on the base (exit {code}), so the before run is not trustworthy",
                              evidence, tail(output, 40))
        command = str(check.get("test_command", "")).replace("{files}", " ".join(shlex.quote(f) for f in files))
        found = forbidden_text(command)
        if found:
            return result(False, f"refused: the test command would {found}")
        argv = shlex.split(command)
        before_code, before_out = shell.run(argv, cwd=scratch, stop_check=ctx.stop_check)
        evidence.append({"command": command + " (on the base, must fail)", "exit_code": before_code,
                         "output_tail": tail(before_out, 12)})
        after_code, after_out = shell.run(argv, cwd=ctx.worktree, stop_check=ctx.stop_check)
        evidence.append({"command": command + " (on the release, must pass)", "exit_code": after_code,
                         "output_tail": tail(after_out, 12)})
    finally:
        shell.run(["git", "worktree", "remove", "--force", str(scratch)], cwd=cwd)
    if before_code == 0:
        return result(False, "the new tests PASS on the base, so they do not prove the change", evidence,
                      "The test command exited 0 on the base with the release's test files:\n" + tail(before_out, 40))
    if after_code != 0:
        return result(False, f"the tests fail on the release (exit {after_code})", evidence, tail(after_out, 60))
    return result(True, f"{len(files)} test file(s) fail on the base (exit {before_code}) and pass on the release", evidence)


def check_all_of(check: dict[str, Any], ctx: CheckContext) -> dict[str, Any]:
    evidence: list[dict[str, Any]] = []
    summaries: list[str] = []
    details: list[str] = []
    ok = True
    for sub in check.get("checks", []):
        sub_result = run_check(sub, ctx)
        evidence += sub_result["evidence"]
        summaries.append(sub_result["summary"])
        if sub_result.get("detail"):
            details.append(sub_result["detail"])
        ok = ok and sub_result["ok"]
    return result(ok, "; ".join(summaries), evidence, "\n\n".join(details))


CHECKS: dict[str, Callable[[dict[str, Any], CheckContext], dict[str, Any]]] = {
    "file_contains": check_file_contains,
    "verdict_file": check_verdict_file,
    "commands_exit_zero": check_commands_exit_zero,
    "pr_exists": check_pr_exists,
    "commit_in_branch": check_commit_in_branch,
    "failing_first": check_failing_first,
    "all_of": check_all_of,
}


def run_check(check: dict[str, Any], ctx: CheckContext) -> dict[str, Any]:
    runner = CHECKS.get(str(check.get("type")))
    if runner is None:
        return result(False, f"unknown check type {check.get('type')!r}")
    return runner(check, ctx)


def effective_check(item: dict[str, Any]) -> dict[str, Any] | None:
    """The item's own check, or for a document item the check that its headings are present."""
    if item.get("check"):
        return item["check"]
    doc = item.get("doc")
    if doc:
        return {"type": "file_contains", "base": "pack", "path": doc["path"], "needles": doc.get("headings", [])}
    return None


# ------------------------------------------------------------ init ---------

def substitute(node: Any, values: dict[str, Any]) -> Any:
    """Replace "@key" (whole string) with the value and <<key>> inside text."""
    if isinstance(node, dict):
        return {k: substitute(v, values) for k, v in node.items()}
    if isinstance(node, list):
        return [substitute(v, values) for v in node]
    if isinstance(node, str):
        if node.startswith("@") and node[1:] in values:
            return copy.deepcopy(values[node[1:]])
        for key, value in values.items():
            if isinstance(value, (str, int)):
                node = node.replace(f"<<{key}>>", str(value))
        return node
    return node


def build_from_template(template: dict[str, Any], *, release: str, repo: str, branch: str, base: str,
                        pr_numbers_: list[int], issue: str, serving_commit: str, approval: str,
                        github_repo: str | None, suite_commands: list[str] | None, e2e_commands: list[str],
                        e2e_exception: str, fix_paths: list[str] | None, na: dict[str, str],
                        route: str = "direct-prod", route_by: str = "Hafiz") -> dict[str, Any]:
    defaults = template["defaults"][repo]
    values = {
        "release": release, "repo": repo, "branch": branch, "base": base, "issue": issue or "0",
        "github_repo": github_repo or defaults["github_repo"], "serving_commit": serving_commit,
        "pr_numbers": list(pr_numbers_), "suite_commands": suite_commands or defaults["suite_commands"],
        "fix_allowed_paths": fix_paths or defaults["fix_allowed_paths"], "e2e_commands": e2e_commands,
        "umbrella_script_dir": defaults.get("umbrella_script_dir", "scripts/agent-checks"), "route": route,
        "failing_first_command": defaults["failing_first_command"],
        "failing_first_install": defaults["failing_first_install"],
    }
    items = substitute(template["items"], values)
    for item in items:
        item.setdefault("evidence", [])
        item.setdefault("depends_on", [])
        item.setdefault("applicable", True)
        item.setdefault("status", "open")
        item.setdefault("failures", 0)
    by_id = {i["id"]: i for i in items}
    if not serving_commit:
        by_id["2"]["check"]["checks"] = [c for c in by_id["2"]["check"]["checks"] if c["type"] != "commit_in_branch"]
    if e2e_commands:
        by_id["6"]["action"] = "script"
        by_id["6"]["check"] = {"type": "commands_exit_zero", "commands": list(e2e_commands)}
        by_id["6"].pop("doc", None)
    elif e2e_exception:
        named = [e for e in E2E_EXCEPTIONS if e2e_exception.lower().startswith(e)]
        if not named:
            raise ReadinessError("e2e exception must start with one of: " + ", ".join(E2E_EXCEPTIONS))
        by_id["6"].update(applicable=False, status="na", na_reason=f"Named exception from AGENTS.md: {e2e_exception}")
    for iid, reason in na.items():
        if iid not in by_id:
            raise ReadinessError(f"--na {iid}: no such item")
        by_id[iid].update(applicable=False, status="na", na_reason=reason)
    data = {
        "schema": SCHEMA, "release": release, "repo": repo, "github_repo": values["github_repo"],
        "branch": branch, "base": base, "pr_numbers": list(pr_numbers_), "issue": issue or "0",
        "serving_commit": serving_commit, "approval": approval, "fix_allowed_paths": values["fix_allowed_paths"],
        "route": route, "created_at": myt_text(), "items": items,
        "loop": {"status": "new", "reason": "", "rounds": 0, "job_seq": 0, "fingerprints": [], "jobs": []},
    }
    if route not in ROUTES:
        raise ReadinessError(f"route must be one of {', '.join(ROUTES)}")
    record_route(data, route, route_by)
    for iid, reason in na.items():  # explicit --na wins over the route
        by_id[iid].update(applicable=False, status="na", na_reason=reason)
    errors = validate(data)
    if errors:
        raise ReadinessError("; ".join(errors))
    return data


# ------------------------------------------------------------- CLI ---------

def render_score(data: dict[str, Any], directory: Path | str | None = None) -> str:
    s = score(data)
    loop = data.get("loop", {})
    lines = [f"Route: {s['route'] or 'not set'}",
             f"PC readiness: {s['percent']}% ({s['pc_green']} of {s['pc_total']} applicable PC items green)",
             f"Prod readiness: {s['prod_percent']}% ({s['prod_green']} of {s['prod_total']} items before your production go are green)",
             "Open PC items: " + (", ".join(s["open_pc"]) or "none")]
    if s["blocked_pc"]:
        lines.append("Blocked PC items: " + ", ".join(s["blocked_pc"]))
    if s["waiting_for"]:
        lines.append("waiting_for_gate: " + ", ".join(s["waiting_for"]))
    before = [g for g in s["gates"] if not g["after_go"]]
    after = [g for g in s["gates"] if g["after_go"]]

    def gate_line(g: dict[str, Any]) -> str:
        state = g["status"] if g["applicable"] else f"not applicable ({g['na_reason']})"
        return f"  - {g['id']} {g['title']} [{g['owner']}] {state}" + (" (SIMULATED)" if g["simulated"] else "")

    lines.append("Gates before your go (counted in Prod readiness, the PC never does them):")
    lines += [gate_line(g) for g in before]
    lines.append("After your go (listed, never counted):")
    lines += [gate_line(g) for g in after]
    pending = len(pending_ops(directory)) if directory else 0
    lines.append(f"Loop: {loop.get('status', 'new')}"
                 + (f" ({loop['reason']})" if loop.get("reason") else "")
                 + f", {loop.get('rounds', 0)} rounds, {len(loop.get('jobs', []))} jobs"
                 + (f", {pending} request(s) queued" if pending else ""))
    if s["prod_ready"]:
        lines.append("READY FOR YOUR GO: Prod readiness is 100%, nothing before the production deploy is open")
    elif s["ready"]:
        lines.append("PC checks are all green; waiting for the gates above")
    return "\n".join(lines)


def render_show(data: dict[str, Any]) -> str:
    lines = [f"Release {data['release']} ({data['repo']}, branch {data['branch']})"]
    for item in data["items"]:
        mark = {"green": "GREEN", "open": "open", "blocked": "BLOCKED", "na": "n/a"}[item["status"]]
        extra = f" - {item['na_reason']}" if item["status"] == "na" else ""
        lines.append(f"  {item['id']:>3} [{item['owner']}] {mark:7} {item['title']}{extra}")
    return "\n".join(lines)


def main(argv: list[str] | None = None, out: Callable[[str], None] = print) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init")
    p.add_argument("--release", required=True); p.add_argument("--repo", required=True, choices=REPOS)
    p.add_argument("--branch", required=True); p.add_argument("--base", default="origin/main")
    p.add_argument("--pr", type=int, action="append", default=[]); p.add_argument("--issue", default="")
    p.add_argument("--route", required=True, choices=ROUTES,
                   help="staging-first (staging, then production) or direct-prod (straight to production)")
    p.add_argument("--route-by", default="Hafiz", help="who chose the route; recorded with the date")
    p.add_argument("--serving-commit", default=""); p.add_argument("--approval", default="")
    p.add_argument("--github-repo"); p.add_argument("--suite-command", action="append")
    p.add_argument("--e2e-command", action="append", default=[]); p.add_argument("--e2e-exception", default="")
    p.add_argument("--fix-path", action="append"); p.add_argument("--na", action="append", default=[],
                                                                  help="ITEM=reason, mark an item not applicable")
    p.add_argument("--template", type=Path, default=TEMPLATE_PATH)
    p.add_argument("--out", type=Path, required=True); p.add_argument("--force", action="store_true")
    for name in ("show", "score", "next"):
        p = sub.add_parser(name); p.add_argument("file", type=Path)
    p = sub.add_parser("gate", help="close a gate (an item owned by hafiz or mac) with evidence")
    p.add_argument("file", type=Path); p.add_argument("item"); p.add_argument("--evidence", required=True)
    p.add_argument("--by", default=""); p.add_argument("--sha", default="")
    p.add_argument("--simulated", action="store_true", help="a proof run: marks the evidence SIMULATED in every report")
    p = sub.add_parser("route", help="change the route before the release is ready")
    p.add_argument("file", type=Path); p.add_argument("new_route", choices=ROUTES); p.add_argument("--by", default="Hafiz")
    p = sub.add_parser("mark"); p.add_argument("file", type=Path); p.add_argument("item")
    p.add_argument("--status", required=True, choices=STATUSES)
    p.add_argument("--note"); p.add_argument("--path"); p.add_argument("--command")
    p.add_argument("--exit-code", type=int); p.add_argument("--pr", type=int); p.add_argument("--job-id")
    p.add_argument("--reset-failures", action="store_true", help="clear the failure count so the loop can try again")
    args = parser.parse_args(argv)
    try:
        if args.cmd == "init":
            if args.out.exists() and not args.force:
                raise ReadinessError(f"{args.out} exists; use --force to replace it")
            na = {}
            for entry in args.na:
                key, _, reason = entry.partition("=")
                if not reason.strip():
                    raise ReadinessError(f"--na {key}: give a reason after =")
                na[key.strip()] = reason.strip()
            data = build_from_template(
                json.loads(args.template.read_text()), release=args.release, repo=args.repo, branch=args.branch,
                base=args.base, pr_numbers_=args.pr, issue=args.issue, serving_commit=args.serving_commit,
                approval=args.approval, github_repo=args.github_repo, suite_commands=args.suite_command,
                e2e_commands=args.e2e_command, e2e_exception=args.e2e_exception, fix_paths=args.fix_path, na=na,
                route=args.route, route_by=args.route_by)
            save(args.out, data)
            out(f"Wrote {args.out}")
            out(render_score(data))
            return 0
        if args.cmd == "gate":
            how = request(args.file, {"op": "gate", "item": args.item, "evidence": args.evidence, "by": args.by,
                                      "sha": args.sha, "simulated": args.simulated})
            out(f"Gate {args.item}: {how}" + (" (the loop applies it before its next action)" if how == "queued" else ""))
            return 0
        if args.cmd == "route":
            how = request(args.file, {"op": "route", "route": args.new_route, "by": args.by})
            out(f"Route {args.new_route}: {how}" + (" (the loop applies it before its next action)" if how == "queued"
                                                    else ". Start or resume the loop to continue."))
            return 0
        data = load(args.file)
        if args.cmd == "show":
            out(render_show(data))
        elif args.cmd == "score":
            out(render_score(data, args.file.parent))
        elif args.cmd == "next":
            item = next_item(data)
            out(f"{item['id']}: {item['title']} (action {item.get('action')})" if item else "none")
        elif args.cmd == "mark":
            items = item_map(data)
            if args.item not in items:
                raise ReadinessError(f"no item {args.item}")
            evidence = {k: v for k, v in dict(note=args.note, path=args.path, command=args.command,
                                              exit_code=args.exit_code, pr=args.pr, job_id=args.job_id).items()
                        if v is not None}
            set_status(items[args.item], args.status, **evidence)
            if args.reset_failures:
                items[args.item]["failures"] = 0
                items[args.item].pop("pending_fix", None)
                items[args.item].pop("blocked_reason", None)
            save(args.file, data)
            out(render_score(data, args.file.parent))
        return 0
    except ReadinessError as exc:
        out(f"REFUSED: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
