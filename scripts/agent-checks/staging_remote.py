#!/usr/bin/env python3
"""Box-side staging deploy program for the home PC (issue #356).

This ONE file is sent over ssh to a staging box by staging_deploy.py and run as
root there. It is plain Python (standard library only). It can only reach
STAGING: the two targets and every path, user, host name, port, controller and
service name are written in this file. There is no environment argument and no
way to name production.

    staging_remote.py remote ripple|sims check  REF SHA [--mode M] [--base SHA]
    staging_remote.py remote ripple|sims start  REF SHA [--mode M] [--base SHA] [--actor A] [--release R]
    staging_remote.py remote ripple|sims status [RUN_ID]
    staging_remote.py remote ripple|sims verify SHA [--ref REF]
    staging_remote.py remote ripple|sims switch on|off|show

ripple: runs the sealed controller `deploy-ripple-suite staging --release-ref REF
        --commit SHA` as the `deploy` user. Refuses anything that adds or changes
        a migration, a deploy script, a dependency file or a build config.
sims:   runs the staging runbook steps as `www-data`: ownership check, fetch and
        checkout, install and build, backup, migrations (scanned first, rolled
        back on failure), cache clears, queue restart, writable gate, read back.

Safety lives here, not in a server user: STOP switch, one deploy at a time, a
lock probe of every deploy lock, a clean checkout on the served commit, a
bounded run time, a log line with who, what and when (MYT), and a read-only
verify at the end. Nothing here prints an environment or a secret.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any, Callable

TARGETS = ("ripple", "sims")
MODES = ("normal", "redeploy-served")
EXPECT_HOST = {"ripple": "srv1297548", "sims": "srv1701812"}

STATE_DIR = "/var/lib/sifututor-pc-deploy"
SWITCH_DIR = "/etc/sifututor-pc-deploy"
SWITCH_FILE = SWITCH_DIR + "/STOP"
MYT_OFFSET = dt.timezone(dt.timedelta(hours=8))

SHA_RE = re.compile(r"[0-9a-f]{40}")
NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,39}")
RELEASE_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,59}")
RUN_RE = re.compile(r"[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}")

RIPPLE_REF_RE = re.compile(r"release/[0-9]+-[a-z0-9]+([a-z0-9-]*[a-z0-9])?")
SIMS_REF_RES = (
    re.compile(r"(release|release-base)/[0-9]+-[a-z0-9]+(-[a-z0-9]+)*"),
    re.compile(r"(test|fix|chore|feat|feature)/[0-9]+-([a-z0-9]+-)*staging-(candidate|serving)(-[a-z0-9]+)*"),
)
MAX_REF = 90

# Paths a Ripple release may not change when the PC deploys it: new SQL migrations, deploy scripts, the two scripts the
# controller runs, dependency files and build config. A release that touches them is run by a person from the Mac.
RIPPLE_HUMAN_ONLY_RE = re.compile(
    r"^(src/lib/migrations/[^/]+\.sql$|scripts/deployment/|scripts/(sims-identity-canary|run-outreach-queue)\.ts$|"
    r"package(-lock)?\.json$|\.npmrc$|next\.config\.|\.github/|ecosystem[^/]*$|Dockerfile)")


class Refused(Exception):
    """A rule said no. The message is the plain reason; nothing has been changed."""


# ------------------------------------------------------------ validators ----

def valid_sha(value: str) -> bool:
    return isinstance(value, str) and SHA_RE.fullmatch(value) is not None


def ripple_ref_ok(ref: str) -> bool:
    return (isinstance(ref, str) and len(ref) <= MAX_REF and RIPPLE_REF_RE.fullmatch(ref) is not None
            and not ref.startswith("release/1080-"))


def sims_ref_ok(ref: str) -> bool:
    return isinstance(ref, str) and len(ref) <= MAX_REF and any(rx.fullmatch(ref) for rx in SIMS_REF_RES)


def ref_ok(target: str, ref: str) -> bool:
    if target == "ripple":
        return ripple_ref_ok(ref)
    if target == "sims":
        return sims_ref_ok(ref)
    return False


def ripple_human_only(changed: list[str]) -> list[str]:
    return [path for path in changed if RIPPLE_HUMAN_ONLY_RE.match(path)]


def myt(moment: dt.datetime) -> str:
    return moment.astimezone(MYT_OFFSET).strftime("%Y-%m-%dT%H:%M:%S%z")


# ----------------------------------------------------- migration scanner ----

def _php_views(text: str) -> tuple[str, str] | None:
    """(code without comments, the same with every string's content blanked). None when a string or comment never ends."""
    out: list[str] = []
    mask: list[str] = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if ch == "/" and nxt == "/" or (ch == "#" and nxt != "["):
            end = text.find("\n", i)
            i = n if end < 0 else end
            out.append(" ")
            mask.append(" ")
            continue
        if ch == "/" and nxt == "*":
            end = text.find("*/", i + 2)
            if end < 0:
                return None
            i = end + 2
            out.append(" ")
            mask.append(" ")
            continue
        heredoc = re.match(r"<<<[ \t]*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1[ \t]*\r?\n", text[i:i + 80]) if ch == "<" else None
        if heredoc:
            ident = heredoc.group(2)
            end = re.search(r"(?m)^[ \t]*" + re.escape(ident) + r"(?![A-Za-z0-9_])", text[i + heredoc.end():])
            if end is None:
                return None
            stop = i + heredoc.end() + end.end()
            chunk = text[i:stop]
            out.append(chunk)
            mask.append("x" * len(chunk))
            i = stop
            continue
        if ch in ("'", '"'):
            j = i + 1
            while j < n and text[j] != ch:
                j += 2 if text[j] == "\\" else 1
            if j >= n:
                return None
            chunk = text[i:j + 1]
            out.append(chunk)
            mask.append(ch + "x" * (len(chunk) - 2) + ch)
            i = j + 1
            continue
        out.append(ch)
        mask.append(ch)
        i += 1
    return "".join(out), "".join(mask)


def _up_body(text: str) -> str | None:
    views = _php_views(text)
    if views is None:
        return None
    code, mask = views
    found = re.search(r"function\s+up\s*\(", mask)
    if not found:
        return None
    open_at = mask.find("{", found.end())
    if open_at < 0:
        return None
    depth = 0
    for i in range(open_at, len(mask)):
        if mask[i] == "{":
            depth += 1
        elif mask[i] == "}":
            depth -= 1
            if depth == 0:
                return code[open_at + 1:i]
    return None


_SQL_RES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("drop statement", re.compile(r"\bdrop\s+(table|column|index|key|database|schema|view|foreign|primary|constraint|check|trigger|"
                                  r"procedure|function|event|user|role)\b", re.IGNORECASE)),
    ("truncate statement", re.compile(r"\btruncate\s+(table\s+)?[`\"\w]", re.IGNORECASE)),
    ("delete-all statement", re.compile(r"\bdelete\s+from\b", re.IGNORECASE)),
    ("rename statement", re.compile(r"\brename\s+(table|column|index|key|to)\b", re.IGNORECASE)),
    ("column rewrite", re.compile(r"\balter\s+table\b[^;]*?\b(modify|change)\b", re.IGNORECASE)),
    ("drop inside alter", re.compile(r"\balter\s+table\b[^;]*?\bdrop\b", re.IGNORECASE)),
)
_CODE_RES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("drop (Schema::drop...)", re.compile(r"\bSchema\s*::\s*(drop\w*|dropIfExists)\s*\(", re.IGNORECASE)),
    ("rename (Schema::rename)", re.compile(r"\bSchema\s*::\s*rename\s*\(", re.IGNORECASE)),
    ("drop (->drop...)", re.compile(r"->\s*drop\w*\s*\(", re.IGNORECASE)),
    ("rename (->rename...)", re.compile(r"->\s*rename\w*\s*\(", re.IGNORECASE)),
    ("truncate (->truncate)", re.compile(r"->\s*truncate\s*\(", re.IGNORECASE)),
    ("delete (->delete)", re.compile(r"->\s*(delete|forceDelete)\s*\(", re.IGNORECASE)),
    ("column change (->change) can cut data", re.compile(r"->\s*change\s*\(\s*\)", re.IGNORECASE)),
    ("wipes the database (Artisan::call)", re.compile(
        r"\bArtisan\s*::\s*call\s*\(\s*['\"](migrate:(fresh|reset|refresh|rollback)|db:(wipe|seed))", re.IGNORECASE)),
    ("runs a shell command", re.compile(r"\b(exec|shell_exec|system|passthru|proc_open|popen)\s*\(", re.IGNORECASE)),
)


def scan_sql(sql: str) -> list[str]:
    """Destructive statements in SQL text (also used on the output of `migrate --pretend`)."""
    return [name for name, rx in _SQL_RES if rx.search(sql)]


def scan_migration(text: str) -> list[str]:
    """Reasons a migration file must not run unattended. Only up() is read: down() legitimately drops. Empty list = clean.

    Fails closed: a file whose up() cannot be found or whose strings or comments never end is refused."""
    body = _up_body(text)
    if body is None:
        return ["cannot read up() (not found, or a string, comment or brace never ends), so it cannot be proved safe"]
    findings: list[str] = []
    for name, rx in _CODE_RES:
        match = rx.search(body)
        if match:
            findings.append(f"{name}: {' '.join(match.group(0).split())[:60]}")
    for name in scan_sql(body):
        findings.append(f"{name} in SQL text")
    return findings


def split_migration_changes(name_status_lines: list[str]) -> tuple[list[str], list[str]]:
    """From `git diff --name-status` lines: (added migration files, other changes that touch database/migrations)."""
    added: list[str] = []
    others: list[str] = []
    for line in name_status_lines:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 2:
            continue
        status, paths = parts[0], parts[1:]
        touching = [p for p in paths if p.startswith("database/migrations/")]
        if not touching:
            continue
        if status.startswith("A") and len(paths) == 1 and paths[0].endswith(".php"):
            added.append(paths[0])
        else:
            others.append(line.strip())
    return added, others


# -------------------------------------------------------------- system ------

class RealSys:
    """The few things the programs do to the box. Tests replace this object."""

    def hostname(self) -> str:
        return os.uname().nodename

    def now(self) -> dt.datetime:
        return dt.datetime.now(dt.timezone.utc)

    def run(self, argv: list[str], *, timeout: float | None = None, cwd: str | None = None,
            env: dict[str, str] | None = None) -> tuple[int, str]:
        try:
            proc = subprocess.run(argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, text=True, timeout=timeout, check=False, errors="replace")
        except subprocess.TimeoutExpired:
            return 124, f"timed out after {timeout} seconds: {argv[0]}"
        except FileNotFoundError:
            return 127, f"command not found: {argv[0]}"
        except OSError as exc:
            return 126, f"could not start {argv[0]}: {exc}"
        return proc.returncode, proc.stdout or ""

    def exists(self, path: str) -> bool:
        return os.path.lexists(path)

    def is_link(self, path: str) -> bool:
        return os.path.islink(path)

    def owner_mode(self, path: str) -> tuple[str, int]:
        import pwd
        info = os.stat(path)
        try:
            owner = pwd.getpwuid(info.st_uid).pw_name
        except KeyError:
            owner = str(info.st_uid)
        return owner, info.st_mode & 0o7777

    def read_text(self, path: str, limit: int = 4_000_000) -> str:
        with open(path, "rb") as handle:
            return handle.read(limit).decode("utf-8", "replace")

    def read_tail(self, path: str, nbytes: int = 400_000) -> str:
        with open(path, "rb") as handle:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            handle.seek(max(0, size - nbytes))
            return handle.read().decode("utf-8", "replace")

    def write_text(self, path: str, text: str) -> None:
        tmp = f"{path}.tmp{os.getpid()}"
        with open(tmp, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)

    def append_line(self, path: str, line: str) -> None:
        try:
            with open(path, "a", encoding="utf-8") as handle:
                handle.write(line + "\n")
        except OSError:
            pass

    def remove(self, path: str) -> None:
        os.remove(path)

    def mkdir(self, path: str, mode: int = 0o755) -> None:
        os.makedirs(path, mode=mode, exist_ok=True)

    def listdir(self, path: str) -> list[str]:
        try:
            return sorted(os.listdir(path))
        except OSError:
            return []

    def free_kb(self, path: str) -> int:
        info = os.statvfs(path)
        return info.f_bavail * info.f_frsize // 1024

    def lock_held(self, path: str) -> bool:
        """True when some process holds a flock on the file right now. Fails closed: any doubt counts as held.

        /proc/locks is NOT used: it cannot see the way the deploy controller takes its lock (tested 09/10/2026)."""
        if not os.path.exists(path):
            return False
        try:
            fd = os.open(path, os.O_RDONLY)
        except OSError:
            return True
        try:
            fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
            fcntl.flock(fd, fcntl.LOCK_UN)
            return False
        except OSError:
            return True
        finally:
            os.close(fd)

    def take_lock(self, path: str) -> int | None:
        fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            os.close(fd)
            return None
        return fd

    def spawn_detached(self, argv: list[str], log_path: str, keep_fd: int | None) -> int:
        handle = open(log_path, "ab")
        proc = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=handle, stderr=subprocess.STDOUT, start_new_session=True,
                                close_fds=True, pass_fds=(keep_fd,) if keep_fd is not None else ())
        handle.close()
        return proc.pid

    def run_bounded(self, argv: list[str], timeout: float, kill_after: float = 120.0) -> tuple[int, bool]:
        """Run with output going straight to our own stdout (the run log). Returns (exit code, timed out)."""
        sys.stdout.flush()
        proc = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=sys.stdout, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            return proc.wait(timeout=timeout), False
        except subprocess.TimeoutExpired:
            import signal
            for sig, wait in ((signal.SIGTERM, kill_after), (signal.SIGKILL, 30)):
                try:
                    os.killpg(proc.pid, sig)
                except OSError:
                    pass
                try:
                    proc.wait(timeout=wait)
                    break
                except subprocess.TimeoutExpired:
                    continue
            return 124, True

    def self_path(self) -> str:
        return os.path.abspath(__file__)

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)


def mask(text: str) -> str:
    text = re.sub(r"(://[^:/@\s]+:)[^@\s]+@", r"\1***@", text)
    return re.sub(r"(?i)(bearer\s+|token=|secret=|password=|passwd=)\S+", r"\1***", text)


# ------------------------------------------------------- shared helpers -----

class Base:
    target = ""
    log_path = ""
    own_lock = ""
    max_seconds = 3600
    lock_names: tuple[str, ...] = ()

    def __init__(self, s: Any, actor: str = "pc-loop", release: str = "none") -> None:
        self.s = s
        self.actor = actor
        self.release = release

    # ---- log ----
    def log(self, text: str) -> None:
        now = self.s.now()
        line = (f"ts_myt={myt(now)} ts_utc={now.strftime('%Y-%m-%dT%H:%M:%SZ')} target={self.target} "
                f"actor={self.actor} release={self.release} {text}")
        self.s.append_line(self.log_path, mask(line))

    def refuse(self, message: str) -> None:
        self.log(f"REFUSED {message}")
        raise Refused(message)

    # ---- generic checks ----
    def check_host(self) -> None:
        if self.s.hostname() != EXPECT_HOST[self.target]:
            self.refuse(f"this box is {self.s.hostname()!r}, not the {self.target} staging box ({EXPECT_HOST[self.target]})")

    def check_switch(self) -> None:
        if self.s.exists(SWITCH_FILE):
            self.refuse(f"the STOP switch is on ({SWITCH_FILE} exists); unattended staging deploys are switched off")

    def check_shapes(self, ref: str, sha: str, mode: str) -> None:
        if self.target not in TARGETS:
            self.refuse("unknown target")
        if mode not in MODES:
            self.refuse(f"mode must be one of {', '.join(MODES)}")
        if not valid_sha(sha):
            self.refuse("the commit must be 40 lowercase hex characters")
        if not ref_ok(self.target, ref):
            self.refuse(f"{ref!r} is not an allowed {self.target} staging ref name")

    def check_identity(self) -> None:
        for name, value, rx in (("actor", self.actor, NAME_RE), ("release", self.release, RELEASE_RE)):
            if not rx.fullmatch(value or ""):
                self.refuse(f"{name} is not a valid name")

    def held_locks(self) -> list[str]:
        raise NotImplementedError

    # ---- run store ----
    def run_dir(self, runid: str) -> str:
        return f"{STATE_DIR}/runs/{self.target}-{runid}"

    def write_state(self, runid: str, **fields: Any) -> dict[str, Any]:
        path = self.run_dir(runid) + "/state.json"
        state: dict[str, Any] = {}
        try:
            state = json.loads(self.s.read_text(path))
        except (OSError, ValueError):
            pass
        state.update(fields)
        self.s.write_text(path, json.dumps(state, indent=1, sort_keys=True) + "\n")
        return state

    def latest_run(self) -> str | None:
        names = [n[len(self.target) + 1:] for n in self.s.listdir(f"{STATE_DIR}/runs") if n.startswith(self.target + "-")]
        names = [n for n in names if RUN_RE.fullmatch(n)]
        return sorted(names)[-1] if names else None

    def status_lines(self, runid: str | None) -> list[str]:
        runid = runid or self.latest_run()
        if not runid:
            return ["state=none (no PC staging deploy has run on this box)"]
        if not RUN_RE.fullmatch(runid):
            raise Refused("bad run id")
        try:
            state = json.loads(self.s.read_text(self.run_dir(runid) + "/state.json"))
        except (OSError, ValueError):
            return [f"run={runid} state=unknown (no state file)"]
        running = self.s.lock_held(self.own_lock)
        shown = state.get("state", "unknown")
        if shown == "running" and not running:
            shown = "died"  # the runner is gone but never wrote a result
        lines = [f"run={runid} state={shown} step={state.get('step', '')}"]
        if state.get("result_line"):
            lines.append(state["result_line"])
        try:
            tail = self.s.read_tail(self.run_dir(runid) + "/run.log", 8000).splitlines()[-25:]
        except OSError:
            tail = []
        lines.append("--- last lines of the run log (masked) ---")
        lines += [mask(line) for line in tail]
        return lines

    def switch(self, action: str) -> list[str]:
        if action == "off":
            self.s.mkdir(SWITCH_DIR)
            self.s.write_text(SWITCH_FILE, f"stopped {myt(self.s.now())} by {self.actor}\n")
            self.log("SWITCH off")
            return [f"STOP switch is ON ({SWITCH_FILE}): unattended staging deploys are refused; a deploy already running finishes"]
        if action == "on":
            if self.s.exists(SWITCH_FILE):
                self.s.remove(SWITCH_FILE)
            self.log("SWITCH on")
            return ["STOP switch is OFF: unattended staging deploys are allowed again"]
        if action == "show":
            return ["STOP switch is " + ("ON" if self.s.exists(SWITCH_FILE) else "OFF")]
        raise Refused("switch takes on, off or show")

    # ---- start / run ----
    def start(self, ref: str, sha: str, mode: str, base: str, detach: bool = True) -> list[str]:
        self.check_host()
        fd = self.s.take_lock(self.own_lock)
        if fd is None:
            self.refuse("a PC staging deploy is already running on this box")
        info = self.preflight(ref, sha, mode, base, own_lock_counts=False)
        now = self.s.now()
        runid = f"{now.strftime('%Y%m%dT%H%M%SZ')}-{sha[:8]}"
        self.s.mkdir(self.run_dir(runid), 0o750)
        self.write_state(runid, run=runid, target=self.target, state="starting", step="starting", ref=ref, sha=sha, mode=mode,
                         actor=self.actor, release=self.release, base=base, started_myt=myt(now), started_utc=now.isoformat(),
                         previous_sha=info.get("served", ""))
        self.log(f"START run={runid} ref={ref} sha={sha} mode={mode} previous={info.get('served', '')}")
        argv = [sys.executable, self.s.self_path(), "remote", self.target, "_run", runid, ref, sha, mode,
                "--base", base or "-", "--actor", self.actor, "--release", self.release, "--lock-fd", str(fd)]
        self.s.spawn_detached(argv, self.run_dir(runid) + "/run.log", fd)
        return [f"STARTED run={runid} target={self.target} ref={ref} sha={sha} mode={mode} (poll with: status)"]

    def run_body(self, runid: str, ref: str, sha: str, mode: str, base: str, lock_fd: int) -> int:
        """The detached runner. It holds the deploy lock until it ends."""
        raise NotImplementedError

    def finish(self, runid: str, status: str, exit_code: int, started: float, ref: str, sha: str, extra: str = "") -> int:
        seconds = int(time.time() - started)
        line = f"RESULT run={runid} status={status} exit={exit_code} seconds={seconds} ref={ref} sha={sha}{extra}"
        print(line, flush=True)
        self.write_state(runid, state="finished", status=status, exit=exit_code, seconds=seconds, result_line=line,
                         ended_myt=myt(self.s.now()))
        self.log(line)
        return 0 if status == "ok" else 1


# ------------------------------------------------------------- ripple -------

class RippleRemote(Base):
    target = "ripple"
    log_path = "/var/log/apps/ripple-staging-pc.log"
    base_dir = "/opt/deploy/ripple-suite"
    own_lock = base_dir + "/.pc-staging-release.lock"
    repo = base_dir + "/repo-staging"
    app_dir = "/var/www/staging/ripple-suite"
    controller = "/usr/local/bin/deploy-ripple-suite"
    serving_prod = base_dir + "/.serving-prod.json"
    staging_log = "/var/log/apps/ripple-suite-staging-deploy.log"
    pm2_app = "ripple-suite-staging"
    pm2_home = "/home/deploy/.pm2"
    port = 3201
    min_free_kb = 20 * 1024 * 1024
    max_seconds = 3600
    git_ssh = "ssh -i /home/deploy/.ssh/ripple_suite_deploy -o IdentitiesOnly=yes -o BatchMode=yes"
    COMPLETE_RE = re.compile(r"^Deploy complete: staging ([0-9a-f]{40}) \(release:([^)]*)\)", re.MULTILINE)

    def dgit(self, *args: str, timeout: float = 60) -> tuple[int, str]:
        argv = ["sudo", "-n", "-u", "deploy", "env", f"GIT_SSH_COMMAND={self.git_ssh}", "GIT_TERMINAL_PROMPT=0",
                "GIT_OPTIONAL_LOCKS=0", "git", "-C", self.repo, *args]
        return self.s.run(argv, timeout=timeout)

    def held_locks(self) -> list[str]:
        held = []
        for name in self.s.listdir(self.base_dir):
            if name.startswith(".") and name.endswith(".lock"):
                path = f"{self.base_dir}/{name}"
                if path != self.own_lock and not self.s.is_link(path) and self.s.lock_held(path):
                    held.append(name)
        return held

    def pm2_state(self) -> tuple[str, str]:
        """(status, commit) of the staging app only. Nothing else from PM2 ever leaves this function."""
        code, out = self.s.run(["sudo", "-n", "-u", "deploy", "env", f"PM2_HOME={self.pm2_home}", "pm2", "jlist"], timeout=60)
        if code != 0:
            return "unknown", "none"
        start, end = out.find("["), out.rfind("]")
        try:
            apps = [a for a in json.loads(out[start:end + 1]) if a.get("name") == self.pm2_app]
        except ValueError:
            return "unknown", "none"
        if len(apps) != 1:
            return "unknown", "none"
        env = apps[0].get("pm2_env") or {}
        sha = env.get("RIPPLE_DEPLOY_COMMIT", "")
        status = env.get("status", "")
        return (status if re.fullmatch(r"[a-z]{3,12}", status or "") else "unknown"), (sha if valid_sha(sha) else "none")

    def last_complete(self) -> tuple[str, str]:
        try:
            text = self.s.read_tail(self.staging_log, 600_000)
        except OSError:
            return "none", "none"
        found = self.COMPLETE_RE.findall(text)
        return (found[-1][0], found[-1][1]) if found else ("none", "none")

    def preflight(self, ref: str, sha: str, mode: str, base: str, own_lock_counts: bool) -> dict[str, str]:
        self.check_host()
        self.check_switch()
        self.check_shapes(ref, sha, mode)
        self.check_identity()
        for path, what in ((self.controller, "the deploy controller"),):
            if self.s.is_link(path):
                self.refuse(f"{what} is a symlink")
            owner, perm = self.s.owner_mode(path)
            if owner != "root" or perm != 0o755:
                self.refuse(f"{what} is not root-owned mode 755")
        if not self.s.exists(self.repo + "/.git") or self.s.is_link(self.repo) or self.s.is_link(self.repo + "/.git"):
            self.refuse("the staging checkout is missing or a symlink")
        if own_lock_counts and self.s.lock_held(self.own_lock):
            self.refuse("a PC staging deploy is already running on this box")
        held = self.held_locks()
        if held:
            self.refuse(f"another deploy or migration lane is running (locks held: {', '.join(held)})")
        code, out = self.dgit("ls-remote", "--heads", "origin", f"refs/heads/{ref}")
        tips = [line.split()[0] for line in out.splitlines() if len(line.split()) == 2 and line.split()[1] == f"refs/heads/{ref}"]
        tip = tips[0] if code == 0 and tips else ""
        if tip != sha:
            self.refuse(f"the remote tip of {ref} is {tip or 'missing'}, not the requested commit {sha}")
        code, out = self.dgit("fetch", "--no-tags", "-q", "origin", f"refs/heads/{ref}:refs/remotes/origin/{ref}", timeout=300)
        if code != 0:
            self.refuse(f"could not fetch {ref}")
        code, out = self.dgit("rev-parse", f"refs/remotes/origin/{ref}^{{commit}}")
        if code != 0 or out.strip() != sha:
            self.refuse("the fetched tip differs from the requested commit")
        _, served = self.pm2_state()
        if not valid_sha(served):
            self.refuse("what staging serves now is unknown, so the change cannot be compared")
        if self.dgit("cat-file", "-e", f"{served}^{{commit}}")[0] != 0:
            self.refuse(f"the serving commit {served} is not in the staging checkout")
        code, head = self.dgit("rev-parse", "HEAD")
        code2, dirty = self.dgit("status", "--porcelain", "--untracked-files=all")
        if code != 0 or code2 != 0 or head.strip() != served or dirty.strip():
            self.refuse("the staging checkout is not clean on the serving commit (a hand step may be open, or the last deploy "
                        "failed); a person looks first")
        # The controller refuses (after about 3 seconds) when root left files in the build tree; say so before a run is started.
        code, uid = self.s.run(["id", "-u", "deploy"], timeout=30)
        if code != 0 or not uid.strip().isdigit():
            self.refuse("cannot read the deploy user id")
        for tree in (self.app_dir + "/node_modules", self.app_dir + "/.next"):
            if self.s.exists(tree):
                code, found = self.s.run(["find", tree, "-xdev", "!", "-uid", uid.strip(), "-print", "-quit"], timeout=120)
                if code != 0 or found.strip():
                    self.refuse(f"foreign-owned files exist in the application build tree {tree} ({found.strip()[:100] or 'find failed'}); "
                                "a person repairs that staging build tree as root first")
        code, names = self.dgit("diff", "--no-renames", "--name-only", served, sha)
        if code != 0:
            self.refuse("could not compare the release with what staging serves")
        blocked = ripple_human_only([n for n in names.splitlines() if n.strip()])
        if blocked:
            self.refuse("the release changes migration, script or build-control files (" + ", ".join(blocked[:5]) +
                        "); this needs a Mac session")
        containment = "checked"
        if mode == "redeploy-served":
            done_sha, done_ref = self.last_complete()
            if sha != served or done_sha != sha or done_ref != f"{ref}":
                self.refuse("redeploy-served needs the commit and ref staging serves now (deploy log and PM2 must agree)")
            containment = "skipped: redeploy of the commit staging already serves"
            prod = "n/a"
        else:
            try:
                prod = json.loads(self.s.read_text(self.serving_prod))["commit"]
            except (OSError, ValueError, KeyError, TypeError):
                prod = ""
            if not valid_sha(prod):
                self.refuse("the production serving commit is unreadable, so the release base cannot be proved")
            if self.dgit("cat-file", "-e", f"{prod}^{{commit}}")[0] != 0:
                self.dgit("fetch", "--no-tags", "-q", "origin", prod, timeout=120)
            if self.dgit("merge-base", "--is-ancestor", prod, sha)[0] != 0:
                self.refuse(f"the release does not contain the commit production serves ({prod}); rebuild it on that commit")
        if self.s.free_kb(self.base_dir) < self.min_free_kb:
            self.refuse("less than 20 GiB free on the deploy disk")
        self.log(f"PREFLIGHT_OK ref={ref} sha={sha} mode={mode} served={served} prod={prod} containment={containment}")
        return {"served": served, "prod": prod, "containment": containment}

    def check(self, ref: str, sha: str, mode: str, base: str) -> list[str]:
        info = self.preflight(ref, sha, mode, base, own_lock_counts=True)
        return [f"CHECK OK: {sha} on {ref} would be accepted for ripple staging now (mode {mode}, served {info['served']}, "
                f"production base {info['prod']}, containment {info['containment']})"]

    def run_body(self, runid: str, ref: str, sha: str, mode: str, base: str, lock_fd: int) -> int:
        started = time.time()
        if not self.s.lock_held(self.own_lock):
            return self.finish(runid, "failed", 1, started, ref, sha, " reason=runner-lost-the-lock")
        self.write_state(runid, state="running", step="controller")
        self.log(f"RUN run={runid} controller=staging ref={ref} sha={sha}")
        # The word "staging" is written here and nowhere else. sudo's env_reset drops every inherited variable,
        # including any confirm phrase.
        argv = ["sudo", "-n", "-u", "deploy", self.controller, "staging", "--release-ref", ref, "--commit", sha]
        code, timed_out = self.s.run_bounded(argv, self.max_seconds)
        status = "ok" if code == 0 else ("timeout" if timed_out else "failed")
        if status == "ok":
            self.write_state(runid, step="verify")
            ok, line = self.verify(sha, ref)
            print(line, flush=True)
            if not ok:
                return self.finish(runid, "failed", 3, started, ref, sha, " reason=verify-failed-after-controller-ok")
        return self.finish(runid, status, code, started, ref, sha)

    def verify(self, sha: str, ref: str | None = None) -> tuple[bool, str]:
        status, pm2_sha = self.pm2_state()
        code, head = self.dgit("rev-parse", "HEAD")
        head = head.strip() if code == 0 else "unknown"
        done_sha, done_ref = self.last_complete()
        _, http = self.s.run(["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "20",
                              f"http://127.0.0.1:{self.port}/login"], timeout=40)
        http = http.strip()[-3:] if http.strip() else "000"
        ok = (status == "online" and pm2_sha == sha and head == sha and done_sha == sha and http in ("200", "302", "307", "308")
              and (ref is None or done_ref == ref))
        line = (f"expected={sha} pm2_status={status} pm2_commit={pm2_sha} repo_head={head} deploy_log_commit={done_sha} "
                f"deploy_log_ref={done_ref} local_login_http={http}")
        return ok, line + ("\nVERIFY OK" if ok else "\nVERIFY FAILED")


# --------------------------------------------------------------- sims -------

class SimsRemote(Base):
    target = "sims"
    log_path = "/var/log/sims-staging-pc-deploy.log"
    own_lock = STATE_DIR + "/sims-staging.lock"
    app = "/var/www/staging/sifu-tutor"
    owner = "www-data"
    remote_url = "git@github.com:Sifututor/sifu-tutor.git"
    login_url = "https://sifu-staging.tutorla.tech/login"
    worker_unit = "sifu-staging-worker"
    max_seconds = 2400
    busy_words = ("install-and-optimize-protected-runtime", "check-runtime-writable", "artisan migrate", "artisan db:",
                  "composer install", "composer update", "composer require", "check-checkout-ownership")
    MIGRATION_RE = re.compile(r"\b(\d{4}_\d{2}_\d{2}_\d{6}_[A-Za-z0-9_]+)\b")

    def www(self, *argv: str) -> list[str]:
        return ["runuser", "-u", self.owner, "--", *argv]

    def wgit(self, *args: str, timeout: float = 120) -> tuple[int, str]:
        return self.s.run(self.www("git", *args), cwd=self.app, timeout=timeout)

    def art(self, *args: str, timeout: float = 900) -> tuple[int, str]:
        return self.s.run(self.www("php", "artisan", *args), cwd=self.app, timeout=timeout)

    def held_locks(self) -> list[str]:
        return []

    def head(self) -> str:
        code, out = self.wgit("rev-parse", "HEAD")
        return out.strip() if code == 0 and valid_sha(out.strip()) else ""

    def busy_processes(self) -> list[str]:
        code, out = self.s.run(["ps", "-eo", "pid,args"], timeout=30)
        if code != 0:
            return ["cannot list processes"]
        mine = str(os.getpid())
        hits = []
        for line in out.splitlines()[1:]:
            pid, _, args = line.strip().partition(" ")
            if pid == mine or "staging_deploy" in args or "staging_remote" in args:
                continue
            if any(word in args for word in self.busy_words):
                hits.append(args.strip()[:90])
        return hits

    def ran_migrations(self) -> set[str] | None:
        code, out = self.art("tinker", "--execute=echo json_encode(DB::table('migrations')->pluck('migration')->all());", timeout=120)
        if code != 0:
            return None
        for line in reversed(out.splitlines()):
            line = line.strip()
            if line.startswith("["):
                try:
                    return set(json.loads(line))
                except ValueError:
                    return None
        return None

    def tree_migrations(self, rev: str) -> list[str] | None:
        code, out = self.wgit("ls-tree", "--name-only", rev, "database/migrations/")
        if code != 0:
            return None
        return [p for p in out.splitlines() if p.endswith(".php")]

    @staticmethod
    def stem(path: str) -> str:
        return path.rsplit("/", 1)[-1].removesuffix(".php")

    def pending_names(self) -> list[str] | None:
        code, out = self.art("migrate:status", "--pending", "--no-ansi", timeout=300)
        if code != 0:
            return None
        if "No pending migrations" in out:
            return []
        return [m.group(1) for line in out.splitlines() if "Pending" in line or "pending" in line
                for m in [self.MIGRATION_RE.search(line)] if m]

    def migration_plan(self, cur: str, sha: str) -> dict[str, Any]:
        """Which migration files the target would run (not yet in the database) and why any of them is unsafe."""
        ran = self.ran_migrations()
        cur_files = self.tree_migrations(cur)
        new_files = self.tree_migrations(sha)
        if ran is None or cur_files is None or new_files is None:
            return {"error": "cannot read the migration state, so migrations cannot be checked", "would_run": [], "findings": []}
        stuck = [self.stem(p) for p in cur_files if self.stem(p) not in ran]
        if stuck:
            return {"error": f"the database already has {len(stuck)} pending migration(s) for the code now on staging; a person decides",
                    "would_run": [], "findings": []}
        would_run = [p for p in new_files if self.stem(p) not in ran]
        findings: list[str] = []
        for path in would_run:
            code, text = self.wgit("show", f"{sha}:{path}")
            if code != 0:
                findings.append(f"{path}: cannot be read")
                continue
            findings += [f"{self.stem(path)}: {f}" for f in scan_migration(text)]
        return {"error": "", "would_run": would_run, "findings": findings}

    def preflight(self, ref: str, sha: str, mode: str, base: str, own_lock_counts: bool) -> dict[str, Any]:
        self.check_host()
        self.check_switch()
        self.check_shapes(ref, sha, mode)
        self.check_identity()
        if base and base != "-" and not valid_sha(base):
            self.refuse("the base commit must be 40 lowercase hex characters")
        if self.s.is_link(self.app) or not self.s.exists(self.app + "/artisan"):
            self.refuse("the SIMS staging checkout is missing or a symlink")
        if self.s.owner_mode(self.app)[0] != self.owner:
            self.refuse(f"the checkout is not owned by {self.owner}")
        if own_lock_counts and self.s.lock_held(self.own_lock):
            self.refuse("a PC staging deploy is already running on this box")
        busy = self.busy_processes()
        if busy:
            self.refuse("a deploy, install or artisan job is running by hand (" + busy[0] + ")")
        code, url = self.wgit("config", "--get", "remote.origin.url")
        if code != 0 or url.strip() != self.remote_url:
            self.refuse("the checkout's git remote is not the SIMS repository")
        code, env = self.art("env", "--no-ansi", timeout=120)
        if code != 0 or "[staging]" not in env:
            self.refuse("the application environment is not staging")
        cur = self.head()
        if not cur:
            self.refuse("cannot read what staging serves now")
        code, dirty = self.wgit("status", "--porcelain", "--untracked-files=no")
        if code != 0 or dirty.strip():
            self.refuse("tracked files in the staging checkout have local changes; a person looks first")
        code, _ = self.wgit("fetch", "--no-tags", "-q", "origin", f"+refs/heads/{ref}:refs/remotes/origin/{ref}", timeout=300)
        if code != 0:
            self.refuse(f"could not fetch {ref} from GitHub")
        code, tip = self.wgit("rev-parse", f"refs/remotes/origin/{ref}^{{commit}}")
        if code != 0 or tip.strip() != sha:
            self.refuse(f"the remote tip of {ref} is {tip.strip() or 'missing'}, not the requested commit {sha}")
        if mode == "redeploy-served":
            if sha != cur:
                self.refuse("redeploy-served needs the commit staging serves now")
            base_source = "skipped: redeploy of the commit staging already serves"
        else:
            if base and base != "-":
                if self.wgit("cat-file", "-e", f"{base}^{{commit}}")[0] != 0:
                    self.wgit("fetch", "--no-tags", "-q", "origin", base, timeout=180)
                if self.wgit("cat-file", "-e", f"{base}^{{commit}}")[0] != 0:
                    self.refuse(f"the production base commit {base} cannot be found")
                required, base_source = base, "serving commit given in the readiness file"
            else:
                code, _ = self.wgit("fetch", "--no-tags", "-q", "origin", "+refs/heads/main:refs/remotes/origin/main", timeout=300)
                code2, main_tip = self.wgit("rev-parse", "refs/remotes/origin/main^{commit}")
                if code != 0 or code2 != 0 or not valid_sha(main_tip.strip()):
                    self.refuse("cannot read origin/main, so the release base cannot be proved")
                required, base_source = main_tip.strip(), "no serving commit is recorded for SIMS; origin/main tip used"
            if self.wgit("merge-base", "--is-ancestor", required, sha)[0] != 0:
                self.refuse(f"the candidate does not contain {required} ({base_source}); rebuild it on that commit")
        plan = self.migration_plan(cur, sha)
        would_run, findings = plan["would_run"], plan["findings"]
        if plan["error"]:
            self.refuse(plan["error"])
        if findings:
            self.refuse("a pending migration is not safe to run unattended (" + "; ".join(findings[:4]) + "); a person decides")
        code, changes = self.wgit("diff", "--no-renames", "--name-status", cur, sha, "--", "database/migrations")
        if code != 0:
            self.refuse("could not compare the migrations")
        _, others = split_migration_changes(changes.splitlines())
        self.log(f"PREFLIGHT_OK ref={ref} sha={sha} mode={mode} current={cur} base={base_source} migrations_to_run={len(would_run)} "
                 f"migration_files_changed_or_removed={len(others)}")
        return {"served": cur, "would_run": [self.stem(p) for p in would_run], "base_source": base_source}

    def check(self, ref: str, sha: str, mode: str, base: str) -> list[str]:
        info = self.preflight(ref, sha, mode, base, own_lock_counts=True)
        return [f"CHECK OK: {sha} on {ref} would be accepted for sims staging now (mode {mode}, now serving {info['served']}, "
                f"base: {info['base_source']}, migrations to run: {len(info['would_run'])})"]

    # ---- the deploy ----
    def step(self, runid: str, name: str) -> None:
        print(f"STEP {name}", flush=True)
        self.write_state(runid, step=name)

    def sh(self, argv: list[str], timeout: float, label: str) -> tuple[int, str]:
        code, out = self.s.run(argv, cwd=self.app, timeout=timeout)
        tail = "\n".join(mask(out).splitlines()[-12:])
        print(f"[{label}] exit {code}\n{tail}", flush=True)
        return code, out

    def restore_previous(self, runid: str, prev: str) -> bool:
        self.step(runid, "restore-previous-code")
        code, _ = self.sh(self.www("git", "checkout", "--detach", prev), 180, "git checkout previous")
        if code != 0:
            return False
        code, _ = self.sh(self.www("scripts/deployment/install-and-optimize-protected-runtime.sh", self.app, "--uncached-staging"),
                          1500, "installer previous")
        if code != 0:
            return False
        for name in ("config:clear", "cache:clear", "route:clear", "view:clear", "queue:restart"):
            self.sh(self.www("php", "artisan", name), 120, name)
        return self.head() == prev

    def run_body(self, runid: str, ref: str, sha: str, mode: str, base: str, lock_fd: int) -> int:
        started = time.time()
        if not self.s.lock_held(self.own_lock):
            return self.finish(runid, "failed", 1, started, ref, sha, " reason=runner-lost-the-lock")
        prev = self.head()
        self.log(f"RUN run={runid} ref={ref} sha={sha} previous={prev}")
        deadline = started + self.max_seconds

        def left() -> float:
            return max(60.0, deadline - time.time())

        def fail(step: str, code: int, why: str, status: str = "failed") -> int:
            return self.finish(runid, status, code, started, ref, sha, f" reason={step}: {why}")

        self.write_state(runid, state="running")
        plan = self.migration_plan(prev, sha)
        if plan["error"] or plan["findings"]:
            return fail("migration-plan", 70, plan["error"] or "; ".join(plan["findings"][:3]), "refused")
        expected = {self.stem(p) for p in plan["would_run"]}
        self.step(runid, "ownership")
        code, _ = self.sh(["scripts/deployment/check-checkout-ownership.sh", self.app, f"--owner={self.owner}"], 120, "ownership")
        if code != 0:
            return fail("ownership", code, "the checkout ownership check failed")
        if self.s.exists(SWITCH_FILE):
            return fail("stop", 10, "the STOP switch appeared before the checkout", "refused")
        self.step(runid, "checkout")
        code, _ = self.sh(self.www("git", "checkout", "--detach", sha), 180, "git checkout")
        if code != 0 or self.head() != sha:
            return fail("checkout", code or 61, "git checkout did not land on the requested commit")
        self.step(runid, "install-and-build")
        code, _ = self.sh(self.www("nice", "-n", "10", "scripts/deployment/install-and-optimize-protected-runtime.sh", self.app,
                                   "--uncached-staging"), left(), "install-and-build")
        if code != 0:
            ok = self.restore_previous(runid, prev) if prev and prev != sha else False
            return fail("install-and-build", code, "install or build failed; previous code " + ("restored" if ok else "NOT restored: a person decides"))
        self.step(runid, "migrations")
        pending = self.pending_names()
        if pending is None:
            ok = self.restore_previous(runid, prev) if prev and prev != sha else False
            return fail("migrations", 62, "cannot read the pending migrations; previous code " + ("restored" if ok else "NOT restored"))
        unexpected = [n for n in pending if n not in expected]
        if unexpected:
            ok = self.restore_previous(runid, prev) if prev and prev != sha else False
            return fail("migrations", 75, f"{len(unexpected)} pending migration(s) were not in the scanned plan ({unexpected[0]}); "
                        "previous code " + ("restored" if ok else "NOT restored: a person decides"))
        if pending:
            rc = self.migration_lane(runid, pending, prev, sha, left)
            if rc:
                return fail("migrations", rc, "the migration lane stopped; see the run log")
        self.step(runid, "clear-caches")
        for name in ("config:clear", "cache:clear", "route:clear", "view:clear"):
            code, _ = self.sh(self.www("php", "artisan", name), 180, name)
            if code != 0:
                return fail("clear-caches", code, f"{name} failed")
        self.step(runid, "queue-restart")
        code, _ = self.sh(self.www("php", "artisan", "queue:restart"), 120, "queue:restart")
        if code != 0:
            return fail("queue-restart", code, "queue:restart failed")
        self.step(runid, "runtime-writable")
        code, _ = self.sh(["scripts/deployment/check-runtime-writable.sh", self.app, f"--owner={self.owner}"], 300, "runtime-writable")
        if code != 0:
            return fail("runtime-writable", code, "the runtime writable gate failed")
        self.step(runid, "verify")
        ok, text = self.verify(sha)
        print(text, flush=True)
        if not ok:
            return fail("verify", 3, "the read-back after the deploy failed")
        return self.finish(runid, "ok", 0, started, ref, sha, f" previous={prev} migrations_run={len(pending)}")

    def migration_lane(self, runid: str, pending: list[str], prev: str, sha: str, left: Callable[[], float]) -> int:
        """Pretend-scan, back up, migrate; on failure roll back what ran and put the previous code back. Returns 0 or an exit code."""
        names = ", ".join(pending[:6])
        print(f"MIGRATION LANE: {len(pending)} pending: {names}", flush=True)
        code, out = self.sh(self.www("php", "artisan", "migrate", "--pretend", "--force"), 600, "migrate --pretend")
        findings = scan_sql(out) if code == 0 else ["pretend run failed"]
        if findings:
            self.restore_previous(runid, prev)
            print("MIGRATION LANE REFUSED: " + "; ".join(findings), flush=True)
            return 70
        self.step(runid, "backup")
        code, _ = self.sh(self.www("php", "artisan", "db:backup", "--no-email", "--no-onedrive"), 1500, "db:backup")
        if code != 0:
            ok = self.restore_previous(runid, prev)
            print("MIGRATION LANE: the backup failed, nothing was migrated; previous code " + ("restored" if ok else "NOT restored"), flush=True)
            return 71
        self.step(runid, "migrate")
        code, _ = self.sh(self.www("php", "artisan", "migrate", "--force"), left(), "migrate --force")
        if code == 0:
            return 0
        ran = self.ran_migrations()
        done = [n for n in pending if ran is not None and n in ran]
        print(f"MIGRATION LANE FAILED: {len(done)} of {len(pending)} ran before the failure", flush=True)
        if ran is None:
            print("MIGRATION LANE: cannot read which migrations ran; NOT rolling back; a person decides (a backup was taken)", flush=True)
            return 72
        if done:
            rcode, _ = self.sh(self.www("php", "artisan", "migrate:rollback", f"--step={len(done)}", "--force"), 900, "migrate:rollback")
            again = self.ran_migrations()
            clean = rcode == 0 and again is not None and not any(n in again for n in pending)
            print("MIGRATION LANE: rollback " + ("done, the schema is back to before" if clean else "INCOMPLETE: a person decides (a backup was taken)"), flush=True)
            if not clean:
                return 73
        ok = self.restore_previous(runid, prev)
        print("MIGRATION LANE: previous code " + ("restored" if ok else "NOT restored: a person decides"), flush=True)
        return 74

    def verify(self, sha: str, ref: str | None = None) -> tuple[bool, str]:
        head = self.head() or "unknown"
        pending = self.pending_names()
        code, http = self.s.run(["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "20", self.login_url], timeout=40)
        http = http.strip()[-3:] if http.strip() else "000"
        wcode, worker = self.s.run(["systemctl", "is-active", self.worker_unit], timeout=30)
        worker = worker.strip() or "unknown"
        ok = head == sha and pending == [] and http in ("200", "302") and worker == "active"
        line = (f"expected={sha} head={head} pending_migrations={'none' if pending == [] else ('unknown' if pending is None else len(pending))} "
                f"login_http={http} worker={worker}")
        return ok, line + ("\nVERIFY OK" if ok else "\nVERIFY FAILED")


# ----------------------------------------------------------------- CLI ------

def make(target: str, s: Any, actor: str, release: str) -> Base:
    if target == "ripple":
        return RippleRemote(s, actor, release)
    if target == "sims":
        return SimsRemote(s, actor, release)
    raise Refused("unknown target")


def main(argv: list[str] | None = None, s: Any = None, out: Callable[[str], None] = print) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("remote_word", choices=["remote"])
    parser.add_argument("target", choices=TARGETS)
    parser.add_argument("verb", choices=["check", "start", "_run", "status", "verify", "switch"])
    parser.add_argument("rest", nargs="*")
    parser.add_argument("--mode", default="normal")
    parser.add_argument("--base", default="")
    parser.add_argument("--actor", default="pc-loop")
    parser.add_argument("--release", default="none")
    parser.add_argument("--ref", default=None)
    parser.add_argument("--lock-fd", type=int, default=None)
    args = parser.parse_args(argv)
    s = s or RealSys()
    box = make(args.target, s, args.actor, args.release)
    base = "" if args.base in ("-", "") else args.base
    try:
        if args.verb in ("check", "start"):
            if len(args.rest) != 2:
                raise Refused(f"{args.verb} needs a ref and a commit")
            ref, sha = args.rest
            lines = box.check(ref, sha, args.mode, base) if args.verb == "check" else box.start(ref, sha, args.mode, base)
            for line in lines:
                out(line)
            return 0
        if args.verb == "_run":
            if len(args.rest) != 4 or not RUN_RE.fullmatch(args.rest[0]) or args.lock_fd is None:
                raise Refused("bad runner call")
            runid, ref, sha, mode = args.rest
            box.check_shapes(ref, sha, mode)
            box.check_identity()
            return box.run_body(runid, ref, sha, mode, base, args.lock_fd)
        if args.verb == "status":
            if len(args.rest) > 1:
                raise Refused("status takes at most one run id")
            for line in box.status_lines(args.rest[0] if args.rest else None):
                out(line)
            return 0
        if args.verb == "verify":
            if len(args.rest) != 1 or not valid_sha(args.rest[0]):
                raise Refused("verify needs one 40-hex commit")
            if args.ref is not None and not ref_ok(args.target, args.ref):
                raise Refused("bad ref")
            box.check_host()
            ok, text = box.verify(args.rest[0], args.ref)
            out(text)
            return 0 if ok else 1
        if args.verb == "switch":
            if len(args.rest) != 1:
                raise Refused("switch takes on, off or show")
            box.check_host()
            for line in box.switch(args.rest[0]):
                out(line)
            return 0
    except Refused as exc:
        out(f"REFUSED: {exc}")
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
