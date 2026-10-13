#!/usr/bin/env python3
"""Staging deploy from the home PC (issue #356). Runs on the PC or the Mac.

This is the deterministic deploy script: no Claude, no environment argument.
It can reach STAGING only: the two targets and their ssh aliases are written
here (ripple -> `staging`, sims -> `finch`), and the box-side program
(staging_remote.py, sent over ssh and re-checked there) repeats every rule.

    staging_deploy.py check   ripple|sims --ref REF [--sha SHA] [--mode M] [--base SHA] [--repo-dir DIR]
                              [--holder NAME] [--override-lease "REASON"]
    staging_deploy.py deploy  ripple|sims --ref REF [--sha SHA] [--mode M] [--base SHA] [--repo-dir DIR]
                              [--holder NAME] [--override-lease "REASON"]
    staging_deploy.py status  ripple|sims [RUN_ID]                (Ripple: also who holds the staging lease)
    staging_deploy.py lease   ripple --holder NAME --purpose TEXT --minutes N [--branch REF]   (take or extend)
    staging_deploy.py release-lease ripple [--holder NAME]
    staging_deploy.py verify  ripple|sims SHA [--ref REF]
    staging_deploy.py switch  ripple|sims on|off|show     (STOP switch on the box)
    staging_deploy.py report  READINESS.json              (the staging gates of a release)
    staging_deploy.py contract ripple|sims                (gate S5 by hand: copied columns against current staging, read-only)

The loop (release_loop.py) uses the same code through the readiness checks
staging_candidate (S1), staging_deployed (S2), staging_smoke (S3),
patch_equivalent (S4 for SIMS) and analytics_contract (S5). The production
deploy is never reachable from here and is always Hafiz's.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import http.cookiejar
import json
import os
from pathlib import Path
import re
import shlex
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import release_readiness as rr  # noqa: E402
import staging_remote as sr  # noqa: E402

ALIASES = {"ripple": "staging", "sims": "finch"}
BASE_URLS = {"ripple": "https://ripple-staging.tutorla.tech", "sims": "https://sifu-staging.tutorla.tech"}
REMOTE_DIR = sr.STATE_DIR + "/bin"
REMOTE_SOURCE = HERE / "staging_remote.py"
LANE_DIR_ENV = "SIFU_AGENT_ACCESS_DIR"
PC_STOP_ENV = "SIFU_STAGING_DEPLOY_STOP"
POLL_SECONDS = 30
LOST_CONTACT_LIMIT = 20  # 20 polls in a row without an answer (10 minutes); the deploy itself keeps going on the box
STAGING_KEYS = {"target", "ref", "mode", "commit", "smoke_commands", "smoke_exception", "approval", "candidate_sha",
                "candidate_ref", "deploy", "deploys", "smoke", "last_status", "contract_baseline", "lease_holder"}
SMOKE_COMMAND_PREFIXES = ("npx playwright test ", "npm run test:", "bash scripts/qa/", "builtin:login", "builtin:page ")
PLAYWRIGHT_HOST = "ubuntu24.04-x64"
DOCS_EXTRA_OK = ("docs/", "CHANGELOG.md", "RELEASE-DOCS.md", "TESTING.md")
OA_DIR_ENV = "SIFU_OWNER_ANALYTICS_DIR"
OA_REF = "origin/main"
CONTRACT_FILES = {"sims": "extractor/registry.json", "ripple": "extractor/registry-ripple.json"}


class DeployError(RuntimeError):
    """The deploy script cannot go on; the message becomes the failure."""


def pc_stop_path() -> Path:
    return Path(os.environ.get(PC_STOP_ENV) or Path.home() / ".config" / "sifututor" / "staging-deploy.STOP")


def result(ok: bool, summary: str, evidence: list[dict[str, Any]] | None = None, detail: str = "") -> dict[str, Any]:
    return rr.result(ok, summary, evidence, detail)


# --------------------------------------------------------- readiness data ---

def validate_staging(data: dict[str, Any]) -> list[str]:
    """Problems with the `staging` section of a readiness file. Production can never be named: there is no key for it."""
    cfg = data.get("staging")
    if cfg is None:
        return []
    if not isinstance(cfg, dict):
        return ["staging must be an object"]
    errors: list[str] = []
    unknown = sorted(set(cfg) - STAGING_KEYS)
    if unknown:
        errors.append("staging has keys that are not allowed (" + ", ".join(unknown) + "); there is no environment, host or alias to set")
    target = cfg.get("target")
    if target not in sr.TARGETS:
        errors.append(f"staging.target must be one of {', '.join(sr.TARGETS)}")
        return errors
    if cfg.get("mode", "normal") not in sr.MODES:
        errors.append(f"staging.mode must be one of {', '.join(sr.MODES)}")
    ref = cfg.get("ref") or data.get("branch", "")
    if not sr.ref_ok(target, ref):
        errors.append(f"staging ref {ref!r} is not an allowed {target} staging branch name")
    if cfg.get("lease_holder") and not sr.NAME_RE.fullmatch(str(cfg["lease_holder"])):
        errors.append("staging.lease_holder must be a plain name (the holder of the Ripple staging lease the loop deploys under)")
    if cfg.get("commit") and not sr.valid_sha(cfg["commit"]):
        errors.append("staging.commit must be 40 lowercase hex characters")
    if cfg.get("mode") == "redeploy-served" and not cfg.get("commit"):
        errors.append("staging.mode redeploy-served needs staging.commit (the commit staging serves now)")
    if not str(cfg.get("approval", "")).strip():
        errors.append("staging needs an approval line (who allowed the PC to deploy staging, and when)")
    expected_repo = {"ripple": "ripple-suite", "sims": "sifu-tutor"}[target]
    if data.get("repo") != expected_repo:
        errors.append(f"a {target} staging deploy belongs to a {expected_repo} release")
    for command in cfg.get("smoke_commands", []) or []:
        errors += smoke_command_problems(str(command))
    return errors


def smoke_command_problems(command: str) -> list[str]:
    """A change-smoke command must be a known test command: never a shell line, never a deploy, merge or write."""
    command = command.strip()
    if not command.startswith(SMOKE_COMMAND_PREFIXES):
        return [f"smoke command {command[:50]!r} must start with one of: " + ", ".join(p.strip() for p in SMOKE_COMMAND_PREFIXES)]
    if re.search(r"[;|&<>$`\n]|\$\(", command):
        return [f"smoke command {command[:50]!r} must be one plain command (no ; | & < > $ or backticks)"]
    found = rr.forbidden_text(command)
    if found:
        return [f"smoke command {command[:50]!r} would {found}"]
    return []


def staging_cfg(data: dict[str, Any]) -> dict[str, Any]:
    cfg = data.get("staging")
    if not isinstance(cfg, dict):
        raise DeployError("this release has no staging section (init --staging-deploy)")
    errors = validate_staging(data)
    if errors:
        raise DeployError("; ".join(errors))
    return cfg


def candidate_ref(data: dict[str, Any], cfg: dict[str, Any]) -> str:
    return str(cfg.get("ref") or data.get("branch", ""))


# --------------------------------------------------------------- lanes ------

def lane_dir() -> Path:
    return Path(os.environ.get(LANE_DIR_ENV) or Path.home() / ".config" / "sifututor" / "agent-access")


def load_lane(name: str) -> dict[str, str]:
    """Read KEY=VALUE lines of a credential lane file. Values are returned to the caller and never printed or logged."""
    path = lane_dir() / name
    try:
        mode = path.stat().st_mode & 0o777
        text = path.read_text()
    except OSError as exc:
        raise DeployError(f"credential lane {name} is not available ({exc.__class__.__name__})") from exc
    if mode & 0o077:
        raise DeployError(f"credential lane {name} is too open (mode {oct(mode)}); it must be 600")
    values: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        line = re.sub(r"^export\s+", "", line)
        key, sep, value = line.partition("=")
        if not sep or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        values[key] = value
    return values


def scrub(text: str, secrets: list[str]) -> str:
    for value in secrets:
        if len(value) >= 4:
            text = text.replace(value, "[redacted]")
    return rr.redact(text)


# ------------------------------------------------------ patch equivalence ---

def change_lines(diff_text: str) -> "collections.Counter[tuple[str, str, str]]":
    """The changed lines of a `git diff -U0` as (file, + or -, line with whitespace squeezed). Context and line numbers are ignored,
    so the same change made on a different base counts the same."""
    counter: collections.Counter[tuple[str, str, str]] = collections.Counter()
    current = ""
    in_hunk = False
    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            current = line.split(" b/", 1)[-1]
            in_hunk = False
            continue
        if line.startswith("@@"):
            in_hunk = True
            continue
        if line.startswith("Binary files "):
            counter[(current, "bin", line)] += 1
            continue
        if in_hunk and line[:1] in ("+", "-"):
            squeezed = " ".join(line[1:].split())
            if squeezed:
                counter[(current, line[0], squeezed)] += 1
    return counter


def compare_changes(staged: "collections.Counter[Any]", promo: "collections.Counter[Any]") -> dict[str, Any]:
    missing = staged - promo
    extra = promo - staged
    extra_files = sorted({key[0] for key in extra})
    risky_extra = [f for f in extra_files if not f.startswith(DOCS_EXTRA_OK)]
    return {"missing": sum(missing.values()), "missing_files": sorted({key[0] for key in missing}), "extra": sum(extra.values()),
            "extra_files": extra_files, "risky_extra_files": risky_extra, "staged_lines": sum(staged.values()),
            "promo_lines": sum(promo.values())}


def patch_equivalence(shell: Any, repo_dir: Path | str, base_ref: str, staged_sha: str, promo_ref: str,
                      stop_check: Callable[[], bool] | None = None) -> dict[str, Any]:
    """Is the change tested on staging the change in the promotion branch, even though the commit ids differ?"""
    def git(*args: str) -> tuple[int, str]:
        return shell.run(["git", *args], cwd=repo_dir, stop_check=stop_check)

    if not sr.valid_sha(staged_sha):
        return {"ok": False, "why": f"{staged_sha!r} is not a full commit id"}
    code, _ = git("merge-base", "--is-ancestor", staged_sha, promo_ref)
    if code == 0:
        return {"ok": True, "how": "the promotion branch contains the exact staged commit", "missing": 0, "extra": 0}
    mbs = []
    for tip in (staged_sha, promo_ref):
        code, out = git("merge-base", base_ref, tip)
        if code != 0 or not out.strip():
            return {"ok": False, "why": f"no merge base between {base_ref} and {tip[:12]} (exit {code})"}
        mbs.append(out.strip().splitlines()[-1])
    diffs = []
    for mb, tip in zip(mbs, (staged_sha, promo_ref)):
        code, out = git("diff", "-U0", "--no-renames", "--no-color", "--no-ext-diff", mb, tip)
        if code != 0:
            return {"ok": False, "why": f"git diff failed (exit {code})"}
        diffs.append(change_lines(out))
    staged, promo = diffs
    if not staged:
        return {"ok": False, "why": "the staged change is empty against its base (already in the base?), so nothing can be compared"}
    info = compare_changes(staged, promo)
    ok = info["missing"] == 0 and not info["risky_extra_files"]
    info.update(ok=ok, how="same changed lines on a different base (commit ids differ)")
    if not ok:
        info["why"] = (f"{info['missing']} staged changed line(s) are not in the promotion branch"
                       + (f" ({', '.join(info['missing_files'][:4])})" if info["missing"] else "")
                       + (f"; the promotion branch also changes untested files: {', '.join(info['risky_extra_files'][:4])}"
                          if info["risky_extra_files"] else ""))
    return info


# ------------------------------------------------- analytics contract (S5) --

def normalize_type(value: Any) -> str:
    """The copier's own type rule (normalizeType in engine.mjs, normalizePgType in pg-types.mjs): lower case, no whitespace."""
    return re.sub(r"\s+", "", str(value).lower())


def compare_contract(entries: list[dict[str, Any]], rows: list[list[str]]) -> dict[str, list[dict[str, str]]]:
    """Registry entries against (table, column, type) rows read from a database.

    breaking: a copied table or column is missing, or its type differs after normalisation (the copier would stop that table with
    SourceSchemaDriftError or SourceSchemaTypeDriftError). new: a column or table the contract does not copy; information only."""
    actual: dict[str, dict[str, str]] = {}
    for table, column, kind in rows:
        actual.setdefault(table, {})[column] = kind
    breaking: list[dict[str, str]] = []
    copied: dict[str, set[str]] = {}
    for entry in entries:
        table = entry["source_table"]
        copied.setdefault(table, set()).update(entry["source_columns"])
        if table not in actual:
            item = {"table": table, "column": "", "why": "table missing", "expected": "", "found": ""}
            if item not in breaking:
                breaking.append(item)
            continue
        for column in entry["source_columns"]:
            expected = entry["source_types"][column]
            if column not in actual[table]:
                item = {"table": table, "column": column, "why": "column missing", "expected": expected, "found": ""}
            elif normalize_type(actual[table][column]) != normalize_type(expected):
                item = {"table": table, "column": column, "why": "type changed", "expected": expected, "found": actual[table][column]}
            else:
                continue
            if item not in breaking:
                breaking.append(item)
    new: list[dict[str, str]] = []
    for table, columns in actual.items():
        if table not in copied:
            new.append({"table": table, "column": "", "type": "", "why": "new table"})
            continue
        new += [{"table": table, "column": c, "type": t, "why": "new column"} for c, t in columns.items() if c not in copied[table]]
    return {"breaking": breaking, "new": new}


def owner_analytics_dir() -> Path:
    """The owner-analytics checkout: SIFU_OWNER_ANALYTICS_DIR, else the umbrella's sims-owner-analytics folder."""
    if os.environ.get(OA_DIR_ENV):
        return Path(os.environ[OA_DIR_ENV])
    beside = HERE.parent.parent / "sims-owner-analytics"
    return beside if beside.is_dir() else Path.home() / "Projects" / "Sifututor" / "sims-owner-analytics"


def load_contract(shell: Any, target: str, stop_check: Callable[[], bool] | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """What Owner Analytics copies from this target, read from owner-analytics main (not the working tree, which can be behind).

    Fails closed (DeployError) when the checkout, the commit or the registry cannot be read: without the contract S5 cannot pass."""
    oa = owner_analytics_dir()
    closed = "; S5 cannot know what Owner Analytics copies, so it fails closed"
    if not (oa / ".git").exists():
        raise DeployError(f"the owner-analytics checkout is missing at {oa} (set {OA_DIR_ENV}){closed}")
    path = CONTRACT_FILES[target]
    fetch_code, _ = shell.run(["git", "fetch", "--quiet", "origin", "main"], cwd=oa, stop_check=stop_check, timeout=120)
    code, out = shell.run(["git", "rev-parse", "--verify", f"{OA_REF}^{{commit}}"], cwd=oa, stop_check=stop_check)
    sha = out.strip().splitlines()[-1] if code == 0 and out.strip() else ""
    if not sr.valid_sha(sha):
        raise DeployError(f"the owner-analytics checkout has no readable {OA_REF} (exit {code}){closed}")
    code, text = shell.run(["git", "show", f"{sha}:{path}"], cwd=oa, stop_check=stop_check)
    if code != 0:
        raise DeployError(f"{path} cannot be read from owner-analytics {OA_REF} {sha[:10]} (exit {code}){closed}")
    try:
        tables = json.loads(text)["tables"]
    except (ValueError, KeyError, TypeError) as exc:
        raise DeployError(f"{path} on owner-analytics {OA_REF} is not a readable registry ({exc.__class__.__name__}){closed}") from exc
    entries = [t for t in tables if isinstance(t, dict) and t.get("source", target) == target]
    for entry in entries:
        columns, types = entry.get("source_columns"), entry.get("source_types")
        if (not sr.TABLE_RE.fullmatch(str(entry.get("source_table", ""))) or not isinstance(columns, list) or not columns
                or not isinstance(types, dict) or not all(isinstance(c, str) and isinstance(types.get(c), str) for c in columns)):
            raise DeployError(f"{path} has an entry without a plain table name, columns and a type per column "
                              f"({str(entry.get('source_table'))[:40]!r}){closed}")
    if not entries:
        raise DeployError(f"{path} on owner-analytics {OA_REF} lists no {target} table{closed}")
    info = {"sha": sha, "path": path, "fetched": fetch_code == 0, "dir": str(oa)}
    return entries, info


def contract_key(item: dict[str, str]) -> tuple[str, str, str, str]:
    """What makes two breaking items the same break: the column, the kind of break and what staging has (not the expected type,
    which can move when the registry on owner-analytics main is updated between S1 and S5)."""
    return item.get("table", ""), item.get("column", ""), item.get("why", ""), item.get("found", "")


def wants_baseline(data: dict[str, Any]) -> bool:
    item = rr.item_map({"items": data.get("items", [])}).get("S5")
    return item is not None and rr.is_applicable(item)


def read_contract_baseline(ctx: Any, cfg: dict[str, Any], sha: str) -> dict[str, Any]:
    """S1 part two: what already breaks the contract on staging BEFORE the candidate is deployed, so S5 judges only what the
    release adds (13/10/2026: both staging databases already differed from production). Never taken once the candidate reached
    staging, because then the release's own breaks would hide in it."""
    if ctx.data.get("staging_sha") == sha or any(isinstance(d, dict) and d.get("sha") == sha for d in cfg.get("deploys") or []):
        raise DeployError(f"the S5 baseline cannot be read now: staging was already deployed with {sha[:10]}, so it would hide "
                          "what this release breaks; S5 fails closed until the staging candidate moves and S1 runs again")
    entries, contract = load_contract(ctx.shell, cfg["target"], ctx.stop_check)
    rows = deployer_for(ctx, cfg).schema(sorted({e["source_table"] for e in entries}))
    return {"candidate_sha": sha, "read_at": rr.myt_text(), "contract_sha": contract["sha"], "columns_read": len(rows),
            "breaking": compare_contract(entries, rows)["breaking"]}


def contract_item_text(item: dict[str, str]) -> str:
    name = f"{item['table']}.{item['column']}" if item.get("column") else item["table"]
    if item["why"] == "type changed":
        return f"{name} (type {item['expected']} -> {item['found']})"
    if item["why"] in ("new column", "new table"):
        return f"{name} ({item['why']}{', ' + item['type'] if item.get('type') else ''})"
    return f"{name} ({item['why']})"


# ----------------------------------------------------------- the deployer ---

class Deployer:
    """Talks to one staging box through its ssh alias. The target decides the alias; nothing else can."""

    def __init__(self, target: str, shell: Any, *, remote_source: Path | str | None = None, actor: str = "pc-loop",
                 release: str = "none", sleep: Callable[[float], None] = time.sleep, poll_seconds: float | None = None,
                 stop_check: Callable[[], bool] | None = None, holder: str = "", override_lease: str = "") -> None:
        if target not in sr.TARGETS:
            raise DeployError(f"target must be one of {', '.join(sr.TARGETS)}")
        self.target = target
        self.alias = ALIASES[target]
        self.shell = shell
        self.source = Path(remote_source or REMOTE_SOURCE).read_text()
        self.digest = hashlib.sha256(self.source.encode()).hexdigest()[:12]
        self.actor, self.release = actor, release
        self.holder, self.override_lease = holder or actor, override_lease
        self.sleep, self.stop_check = sleep, stop_check
        self.poll_seconds = POLL_SECONDS if poll_seconds is None else poll_seconds

    # ---- one ssh call ----
    def remote_command(self, verb: str, args: list[str], flags: list[str]) -> str:
        name = f"staging_remote-{self.digest}.py"
        path = f"{REMOTE_DIR}/{name}"
        parts = ["python3", path, "remote", self.target, verb, *args, *flags]
        return (f"umask 022; mkdir -p {REMOTE_DIR} && cat > {path}.tmp$$ && mv {path}.tmp$$ {path} && "
                "exec " + " ".join(shlex.quote(p) for p in parts))

    def call(self, verb: str, args: list[str] | None = None, *, mode: str | None = None, base: str = "", ref: str | None = None,
             timeout: float = 600, extra: list[str] | None = None) -> tuple[int, str]:
        flags = ["--actor", self.actor, "--release", self.release, "--holder", self.holder]
        if self.override_lease and verb in ("check", "start"):
            flags += ["--override-lease", self.override_lease]
        flags += extra or []
        if mode:
            flags += ["--mode", mode]
        if base:
            flags += ["--base", base]
        if ref:
            flags += ["--ref", ref]
        argv = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", "-o", "ServerAliveInterval=30", "-o", "ServerAliveCountMax=4",
                self.alias, self.remote_command(verb, args or [], flags)]
        return self.shell.run(argv, input_text=self.source, stop_check=self.stop_check, timeout=timeout)

    # ---- local rules before any ssh ----
    def local_rules(self, ref: str, sha: str, mode: str, base: str = "") -> None:
        if pc_stop_path().exists():
            raise DeployError(f"the PC staging-deploy STOP file exists ({pc_stop_path()}); unattended staging deploys are off")
        if mode not in sr.MODES:
            raise DeployError(f"mode must be one of {', '.join(sr.MODES)}")
        if not sr.valid_sha(sha):
            raise DeployError("the commit must be 40 lowercase hex characters")
        if not sr.ref_ok(self.target, ref):
            raise DeployError(f"{ref!r} is not an allowed {self.target} staging branch name")
        if base and not sr.valid_sha(base):
            raise DeployError("the base commit must be 40 lowercase hex characters")
        for name, value, rx in (("actor", self.actor, sr.NAME_RE), ("release", self.release, sr.RELEASE_RE),
                                ("holder", self.holder, sr.NAME_RE)):
            if not rx.fullmatch(value):
                raise DeployError(f"{name} is not a valid name")
        if self.override_lease and not sr.LEASE_TEXT_RE.fullmatch(self.override_lease):
            raise DeployError("the lease override reason must be 3 to 160 plain characters (no = or quotes)")

    # ---- verbs ----
    @staticmethod
    def refusal(text: str) -> str:
        for line in text.splitlines():
            if line.startswith("REFUSED:"):
                return line.removeprefix("REFUSED:").strip()
        return text.strip().splitlines()[-1][:200] if text.strip() else "no answer"

    def check(self, ref: str, sha: str, mode: str = "normal", base: str = "") -> tuple[bool, str]:
        self.local_rules(ref, sha, mode, base)
        code, out = self.call("check", [ref, sha], mode=mode, base=base)
        line = next((l for l in out.splitlines() if l.startswith("CHECK OK")), "")
        if code == 0 and line:
            return True, line
        return False, self.refusal(out) if code == 2 else f"the check did not answer (exit {code}): {self.refusal(out)}"

    def start(self, ref: str, sha: str, mode: str = "normal", base: str = "") -> str:
        self.local_rules(ref, sha, mode, base)
        code, out = self.call("start", [ref, sha], mode=mode, base=base)
        found = re.search(r"STARTED run=(\S+)", out)
        if code != 0 or not found:
            raise DeployError("the deploy did not start: " + (self.refusal(out) if code == 2 else f"exit {code}: {self.refusal(out)}"))
        return found.group(1)

    def status(self, run: str | None = None) -> dict[str, Any]:
        code, out = self.call("status", [run] if run else [], timeout=120)
        state = re.search(r"run=(\S+) state=(\S+)", out)
        step = re.search(r"step=(\S*)", out)
        final = re.search(r"^RESULT .*$", out, re.MULTILINE)
        none = "state=none" in out
        return {"code": code, "run": state.group(1) if state else "", "state": state.group(2) if state else ("none" if none else "unknown"),
                "step": step.group(1) if step else "", "result": final.group(0) if final else "", "raw": out}

    def wait(self, run: str, on_poll: Callable[[dict[str, Any]], None] | None = None) -> dict[str, Any]:
        """Poll until the run is finished. A dropped connection never stops the deploy on the box; it only pauses the polling."""
        lost = 0
        while True:
            if self.stop_check and self.stop_check():
                raise rr.StopRequested()
            info = self.status(run)
            if info["code"] != 0 or info["state"] in ("unknown", "none"):
                lost += 1
                if lost >= LOST_CONTACT_LIMIT:
                    raise DeployError(f"lost contact with the box for {lost} polls; the deploy may still be running (run {run})")
            else:
                lost = 0
                if on_poll:
                    on_poll(info)
                if info["state"] in ("finished", "died"):
                    return info
            self.sleep(self.poll_seconds)

    def verify(self, sha: str, ref: str | None = None) -> tuple[bool, str]:
        if not sr.valid_sha(sha):
            raise DeployError("the commit must be 40 lowercase hex characters")
        code, out = self.call("verify", [sha], ref=ref, timeout=180)
        return code == 0 and "VERIFY OK" in out, out.strip()

    def schema(self, tables: list[str]) -> list[list[str]]:
        """The (table, column, type) rows of these tables on the staging database, read-only on the box."""
        if not tables or not all(sr.TABLE_RE.fullmatch(t) for t in tables):
            raise DeployError("schema needs plain lowercase table names")
        code, out = self.call("schema", sorted(set(tables)), timeout=300)
        line = next((l for l in out.splitlines() if l.startswith("SCHEMA [")), "")
        if code != 0 or not line:
            raise DeployError("the staging column list could not be read: " +
                              (self.refusal(out) if code == 2 else f"exit {code}: {self.refusal(out)}"))
        try:
            rows = json.loads(line.removeprefix("SCHEMA "))
        except ValueError as exc:
            raise DeployError("the staging column list came back unreadable") from exc
        if not all(isinstance(r, list) and len(r) == 3 and all(isinstance(v, str) for v in r) for r in rows):
            raise DeployError("the staging column list came back in an unexpected shape")
        return rows

    def lease(self, purpose: str, minutes: int, branch: str = "") -> tuple[bool, str]:
        """Take or extend the Ripple staging lease for this holder. The box writes the file and re-checks every value."""
        if self.target != "ripple":
            raise DeployError("the staging lease exists for ripple only")
        if not sr.NAME_RE.fullmatch(self.holder):
            raise DeployError("holder is not a valid name")
        if not sr.LEASE_TEXT_RE.fullmatch(purpose):
            raise DeployError("purpose must be 3 to 160 plain characters (no = or quotes)")
        if branch and not sr.LEASE_BRANCH_RE.fullmatch(branch):
            raise DeployError("branch is not a valid branch name")
        if not 1 <= minutes <= sr.LEASE_MAX_MINUTES:
            raise DeployError(f"minutes must be between 1 and {sr.LEASE_MAX_MINUTES}")
        extra = ["--purpose", purpose, "--minutes", str(minutes)] + (["--branch", branch] if branch else [])
        code, out = self.call("lease", extra=extra, timeout=120)
        return code == 0 and "LEASE " in out, self.refusal(out) if code == 2 else out.strip()

    def release_lease(self) -> tuple[bool, str]:
        if self.target != "ripple":
            raise DeployError("the staging lease exists for ripple only")
        code, out = self.call("release-lease", timeout=120)
        return code == 0, self.refusal(out) if code == 2 else out.strip()

    def switch(self, action: str) -> str:
        if action not in ("on", "off", "show"):
            raise DeployError("switch takes on, off or show")
        return self.call("switch", [action], timeout=120)[1].strip()

    def deploy_and_verify(self, ref: str, sha: str, mode: str = "normal", base: str = "", *,
                          run: str | None = None, on_run: Callable[[str], None] | None = None,
                          on_poll: Callable[[dict[str, Any]], None] | None = None) -> dict[str, Any]:
        """check, start (or attach to `run`), poll to the end, verify. Returns evidence; never claims success without the read-back."""
        started_at = time.time()
        evidence: list[dict[str, Any]] = []
        if self.override_lease:
            evidence.append({"note": f"lease override given by {self.holder}: {self.override_lease}"})
        if run is None:
            ok, line = self.check(ref, sha, mode, base)
            evidence.append({"command": f"remote {self.target} check {ref} {sha[:12]}", "note": line})
            if not ok:
                return {"ok": False, "refused": True, "summary": f"refused: {line}", "evidence": evidence, "run": ""}
            run = self.start(ref, sha, mode, base)
            evidence.append({"command": f"remote {self.target} start {ref} {sha[:12]}", "note": f"STARTED run={run}"})
            if on_run:
                on_run(run)
        final = self.wait(run, on_poll)
        evidence.append({"note": final["result"] or f"run {run} state {final['state']}"})
        if final["state"] != "finished" or " status=ok " not in final["result"] + " ":
            return {"ok": False, "refused": False, "run": run, "evidence": evidence,
                    "summary": f"the deploy did not finish ok: {final['result'] or 'state ' + final['state']}",
                    "detail": final["raw"][-1500:]}
        ok, text = self.verify(sha, ref)
        evidence.append({"command": f"remote {self.target} verify {sha[:12]}", "note": text.splitlines()[-1] if text else "no answer"})
        if not ok:
            return {"ok": False, "refused": False, "run": run, "evidence": evidence,
                    "summary": "the deploy finished but the read-back from the server does not show the commit", "detail": text}
        seconds = int(time.time() - started_at)
        evidence.append({"sha": sha, "note": f"deployed commit read back from the server (run {run}, {seconds} s)"})
        return {"ok": True, "refused": False, "run": run, "evidence": evidence, "seconds": seconds,
                "summary": f"staging serves {sha[:10]} ({ref}), read back from the server after run {run}"}


# ------------------------------------------------------------------ smoke ---

class RealHttp:
    """Plain HTTP with a cookie jar. No redirects are followed, so a bounce back to the login page is visible."""

    class _NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args: Any, **kwargs: Any) -> None:
            return None

    def __init__(self) -> None:
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar), self._NoRedirect())

    def request(self, method: str, url: str, headers: dict[str, str] | None = None, body: bytes | None = None,
                timeout: float = 30) -> tuple[int, dict[str, str], str]:
        req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
        try:
            with self.opener.open(req, timeout=timeout) as resp:
                return resp.status, {k.lower(): v for k, v in resp.headers.items()}, resp.read(2_000_000).decode("utf-8", "replace")
        except urllib.error.HTTPError as err:
            return err.code, {k.lower(): v for k, v in err.headers.items()}, err.read(200_000).decode("utf-8", "replace")
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            return 0, {}, f"{exc.__class__.__name__}: {exc}"

    def cookie(self, name: str) -> str | None:
        return next((c.value for c in self.jar if c.name == name), None)


def public_get(http_: Any, target: str, path: str) -> tuple[bool, str]:
    status, _, _ = http_.request("GET", BASE_URLS[target] + path)
    return status in (200, 302, 307, 308), f"GET {path} -> HTTP {status}"


LOGIN_LANE = ("staging-lifecycle-qa.conf", "STAGING_LIFECYCLE_QA_EMAIL", "STAGING_LIFECYCLE_QA_PASSWORD")


def lane_for(target: str) -> tuple[str, dict[str, str], str, str]:
    """(lane file, values, email key, password key) for the scripted login. The staging lifecycle QA account is a non-admin
    account that works on both staging sites (on 09/10/2026 the admin logins in the other lane files were rejected)."""
    name, email_key, password_key = LOGIN_LANE
    return name, load_lane(name), email_key, password_key


def login_smoke(http_: Any, target: str, page_paths: list[str] | None = None) -> tuple[bool, list[str], list[str]]:
    """Scripted login on staging, then GET the given pages as that user. Returns (ok, lines, secrets to scrub)."""
    _, lane, email_key, password_key = lane_for(target)
    email, password = lane.get(email_key, ""), lane.get(password_key, "")
    if not email or not password:
        return False, [f"the staging login lane has no {email_key}/{password_key}"], []
    secrets = [email, password]
    base = BASE_URLS[target]
    lines: list[str] = []
    if target == "ripple":
        status, _, _ = http_.request("POST", base + "/api/auth/login", {"Content-Type": "application/json"},
                                     json.dumps({"email": email, "password": password}).encode())
        lines.append(f"POST /api/auth/login -> HTTP {status}")
        if status != 200:
            return False, lines, secrets
        status, _, body = http_.request("GET", base + "/api/auth/me")
        lines.append(f"GET /api/auth/me -> HTTP {status}")
        if status != 200:
            return False, lines, secrets
        paths = page_paths if page_paths is not None else ["/requests"]
    else:
        status, _, page = http_.request("GET", base + "/login")
        token = re.search(r'name="csrf-token" content="([^"]+)"', page)
        lines.append(f"GET /login -> HTTP {status}")
        if status != 200 or not token:
            return False, lines + ["no CSRF token on the login page"], secrets
        headers = {"Content-Type": "application/json", "X-CSRF-TOKEN": token.group(1), "X-Requested-With": "XMLHttpRequest",
                   "Accept": "text/html"}
        status, resp_headers, _ = http_.request("POST", base + "/login", headers,
                                                json.dumps({"email": email, "password": password}).encode())
        lines.append(f"POST /login -> HTTP {status}")
        if status not in (200, 204, 302, 303):
            return False, lines, secrets
        if resp_headers.get("location", "").rstrip("/").endswith("/login"):
            return False, lines + ["login sent the user back to /login (credentials refused)"], secrets
        paths = page_paths if page_paths is not None else ["/"]
    for path in paths:
        status, headers, _ = http_.request("GET", base + path)
        bounced = headers.get("location", "").rstrip("/").endswith("/login")
        lines.append(f"GET {path} -> HTTP {status}" + (" (sent back to login)" if bounced else ""))
        if status != 200 or bounced:
            return False, lines, secrets
    return True, lines, secrets


def playwright_env(target: str) -> tuple[dict[str, str], list[str]]:
    """Environment for a change-smoke command: the headless Chromium that works on the PC without sudo, and the staging login
    the test harnesses read. Returns (env, secret values to scrub from output)."""
    home = Path.home()
    libs = f"{home}/.local/chromium-libs/root/usr/lib:{home}/.local/chromium-libs/root/usr/lib/x86_64-linux-gnu"
    env = dict(os.environ)
    env["PLAYWRIGHT_HOST_PLATFORM_OVERRIDE"] = PLAYWRIGHT_HOST
    env["LD_LIBRARY_PATH"] = libs + (":" + env["LD_LIBRARY_PATH"] if env.get("LD_LIBRARY_PATH") else "")
    env["PLAYWRIGHT_BASE_URL"] = BASE_URLS[target]
    local_bin = home / ".local" / "bin"  # the Linux npm and npx; the Windows copies under /mnt/c cannot build here
    if local_bin.is_dir():
        env["PATH"] = str(local_bin) + os.pathsep + os.pathsep.join(p for p in env.get("PATH", "").split(os.pathsep) if p != str(local_bin))
    secrets: list[str] = []
    _, qa, email_key, password_key = lane_for(target)
    env["TEST_USER_EMAIL"], env["TEST_USER_PASSWORD"] = qa.get(email_key, ""), qa.get(password_key, "")
    secrets += [qa.get(email_key, ""), qa.get(password_key, "")]
    runtime = lane_dir() / "runtime"
    runtime.mkdir(mode=0o700, exist_ok=True)
    env["PLAYWRIGHT_AUTH_STATE_PATH"] = str(runtime / f"pc-deploy-{target}-qa.json")
    env.setdefault("PLAYWRIGHT_AUTH_VERIFY_PATH", "/requests" if target == "ripple" else "/")
    env["PLAYWRIGHT_REUSE_REMOTE_AUTH_STATE"] = "1"
    env["PLAYWRIGHT_AUTH_STATE_MAX_AGE_SECONDS"] = "900"
    names = ("ripple-staging-smoke.conf",) if target == "ripple" else ("staging-smoke.conf", "sims-staging-browser-qa.conf",
                                                                       "sims-staging-e2e.conf")
    for name in names:
        try:
            lane = load_lane(name)
        except DeployError:
            continue
        env.update({k: v for k, v in lane.items() if k not in env or k.startswith(("RIPPLE_", "SIMS_", "E2E_"))})
        secrets += [v for k, v in lane.items() if "PASSWORD" in k or "EMAIL" in k]
    return env, [s for s in secrets if s]


# ------------------------------------------------------------ the checks ----

def local_tip(shell: Any, repo_dir: Path | None, ref: str, stop_check: Callable[[], bool] | None) -> tuple[str, str]:
    """The tip of the branch on GitHub as the PC sees it: (sha, error)."""
    code, out = shell.run(["git", "ls-remote", "--heads", "origin", f"refs/heads/{ref}"], cwd=repo_dir, stop_check=stop_check)
    rows = [l.split() for l in out.splitlines() if len(l.split()) == 2 and l.split()[1] == f"refs/heads/{ref}"]
    if code != 0 or not rows:
        return "", f"branch {ref} is not on origin (exit {code})"
    return rows[0][0], ""


def deployer_for(ctx: Any, cfg: dict[str, Any]) -> Deployer:
    release = re.sub(r"[^A-Za-z0-9._-]+", "-", str(ctx.data.get("release_id") or ctx.data.get("release", "release"))).strip("-")[:60] or "release"
    if not sr.RELEASE_RE.fullmatch(release):
        release = "release"
    return Deployer(cfg["target"], ctx.shell, release=release, stop_check=ctx.stop_check,
                    sleep=getattr(ctx, "sleep", time.sleep), poll_seconds=getattr(ctx, "poll_seconds", None),
                    holder=str(cfg.get("lease_holder") or ""))


def check_candidate(check: dict[str, Any], ctx: Any) -> dict[str, Any]:
    """S1: the staging candidate is identified (exact ref and commit) and passes every acceptance rule, checked on the box."""
    try:
        cfg = staging_cfg(ctx.data)
        ref = candidate_ref(ctx.data, cfg)
        sha, why = local_tip(ctx.shell, ctx.repo_dir, ref, ctx.stop_check)
        if why:
            return result(False, why)
        if cfg.get("commit") and cfg["commit"] != sha:
            return result(False, f"the tip of {ref} is {sha[:10]} but the readiness file pins {cfg['commit'][:10]}")
        mode = cfg.get("mode", "normal")
        base = str(ctx.data.get("serving_commit") or "") if cfg["target"] == "sims" else ""
        ok, line = deployer_for(ctx, cfg).check(ref, sha, mode, base)
    except DeployError as exc:
        return result(False, str(exc))
    evidence = [{"command": f"git ls-remote --heads origin {ref}", "sha": sha, "note": f"candidate {ref} at {sha}"},
                {"command": f"remote {cfg['target']} check", "note": line[:400]}]
    if not ok:
        return result(False, f"the candidate {ref} at {sha[:10]} was refused: {line}", evidence)
    baseline = cfg.get("contract_baseline")
    if wants_baseline(ctx.data):
        kept = isinstance(baseline, dict) and baseline.get("candidate_sha") == sha
        if not kept:
            try:
                baseline = read_contract_baseline(ctx, cfg, sha)
            except DeployError as exc:
                return result(False, f"the S5 baseline (what already breaks the analytics contract on staging) could not be "
                                     f"read, so S1 fails closed: {exc}", evidence)
        evidence.append({"command": f"remote {cfg['target']} schema (S5 baseline, before the deploy, read-only)",
                         "note": ("kept the baseline already read for this commit at " if kept else "read at ") + baseline["read_at"]
                                 + f": {baseline['columns_read']} columns read; {len(baseline['breaking'])} already breaking "
                                 + f"(owner-analytics main {baseline['contract_sha'][:10]})",
                         "breaking": [contract_item_text(i) for i in baseline["breaking"]]})
        cfg["contract_baseline"] = baseline
    cfg["candidate_sha"], cfg["candidate_ref"] = sha, ref
    return result(True, f"candidate {ref} at {sha[:10]} passes the {cfg['target']} staging rules", evidence)


def check_deployed(check: dict[str, Any], ctx: Any) -> dict[str, Any]:
    """S2: deploy staging, or attach to the run already started, then read the commit back from the server."""
    try:
        cfg = staging_cfg(ctx.data)
        sha, ref = str(cfg.get("candidate_sha", "")), str(cfg.get("candidate_ref", ""))
        if not sr.valid_sha(sha) or not ref:
            return result(False, "no candidate has been accepted yet (S1 comes first)")
        mode = cfg.get("mode", "normal")
        base = str(ctx.data.get("serving_commit") or "") if cfg["target"] == "sims" else ""
        deployer = deployer_for(ctx, cfg)
        run = None
        pending = cfg.get("deploy")
        if isinstance(pending, dict) and pending.get("sha") == sha and pending.get("run"):
            run = pending["run"]  # the loop was stopped while this run was going: attach to it, never start a second

        def remember(new_run: str) -> None:
            cfg["deploy"] = {"run": new_run, "sha": sha, "ref": ref, "started": rr.myt_text()}
            if getattr(ctx, "checkpoint", None):
                ctx.checkpoint()

        outcome = deployer.deploy_and_verify(ref, sha, mode, base, run=run, on_run=remember)
    except DeployError as exc:
        return result(False, str(exc))
    cfg.setdefault("deploys", []).append({"run": outcome.get("run", ""), "sha": sha, "ok": outcome["ok"], "at": rr.myt_text()})
    cfg["deploy"] = None  # the run is over (ok or not); a retry starts a fresh check and run
    if not outcome["ok"]:
        return result(False, outcome["summary"], outcome["evidence"], outcome.get("detail", ""))
    ctx.data["staging_sha"] = sha
    return result(True, outcome["summary"], outcome["evidence"])


def run_smoke_command(ctx: Any, command: str, target: str, base_env: dict[str, str], secrets: list[str]) -> tuple[bool, dict[str, Any]]:
    problems = smoke_command_problems(command)
    if problems:
        return False, {"command": command[:80], "exit_code": 126, "output_tail": problems[0]}
    code, out = ctx.shell.run(shlex.split(command), cwd=ctx.worktree, stop_check=ctx.stop_check, env=base_env)
    return code == 0, {"command": command, "exit_code": code, "output_tail": rr.tail(scrub(out, secrets), 12)}


def check_smoke(check: dict[str, Any], ctx: Any) -> dict[str, Any]:
    """S3: staging still serves the deployed commit, the normal smoke passes, and each change-smoke command passes."""
    try:
        cfg = staging_cfg(ctx.data)
        sha, ref = str(cfg.get("candidate_sha", "")), str(cfg.get("candidate_ref", ""))
        target = cfg["target"]
        if not sr.valid_sha(sha) or ctx.data.get("staging_sha") != sha:
            return result(False, "staging has not been deployed with the candidate yet (S2 comes first)")
        evidence: list[dict[str, Any]] = []
        ok, text = deployer_for(ctx, cfg).verify(sha, ref)
        evidence.append({"command": f"remote {target} verify {sha[:12]}", "note": (text.splitlines() or ["no answer"])[-1]})
        if not ok:
            return result(False, "staging no longer serves the deployed commit, so a smoke would test something else", evidence)
        http_ = getattr(ctx, "http", None) or RealHttp()
        up, line = public_get(http_, target, "/login")
        evidence.append({"command": f"GET {BASE_URLS[target]}/login", "note": line})
        if not up:
            return result(False, f"normal smoke: {line}", evidence)
        logged, lines, secrets = login_smoke(http_, target)
        evidence.append({"command": f"scripted login on {target} staging (lane file, values never shown)", "note": "; ".join(lines)})
        if not logged:
            return result(False, "normal smoke: the scripted login failed (" + "; ".join(lines) + ")", evidence)
        env, env_secrets = playwright_env(target)
        secrets = secrets + env_secrets
        commands = [str(c) for c in cfg.get("smoke_commands", []) or []]
        if not commands and not cfg.get("smoke_exception"):
            return result(False, "no change smoke is listed (staging.smoke_commands) and no named exception is given", evidence)
        ran = 0
        for command in commands:
            if command.startswith("builtin:"):
                page = command.split(" ", 1)[1] if " " in command else None
                ok_page, page_lines, more = login_smoke(http_, target, [page] if page else None)
                secrets += more
                evidence.append({"command": command, "note": "; ".join(page_lines)})
                if not ok_page:
                    return result(False, f"change smoke {command!r} failed (" + "; ".join(page_lines) + ")", evidence)
                ran += 1
                continue
            good, entry = run_smoke_command(ctx, command, target, env, secrets)
            evidence.append(entry)
            if not good:
                return result(False, f"change smoke failed: {command} (exit {entry['exit_code']})", evidence, entry["output_tail"])
            ran += 1
    except DeployError as exc:
        return result(False, str(exc))
    except rr.StopRequested:
        raise
    named = f"; named exception: {cfg['smoke_exception']}" if cfg.get("smoke_exception") and not commands else ""
    return result(True, f"normal smoke passed and {ran} change smoke command(s) passed on {target} staging{named}", evidence)


def check_patch_equivalent(check: dict[str, Any], ctx: Any) -> dict[str, Any]:
    """S4 for SIMS: the promotion branch holds the change tested on staging, even though the commit ids differ."""
    sha = str(ctx.data.get("staging_sha", ""))
    if not sha:
        return result(False, "no staged commit has been recorded yet (S2 closes first)")
    branch, base = str(ctx.data.get("branch", "")), str(ctx.data.get("base", "origin/main"))
    info = patch_equivalence(ctx.shell, ctx.repo_dir, base, sha, f"origin/{branch}", ctx.stop_check)
    evidence = [{"command": f"patch equivalence of {sha[:10]} and origin/{branch} against {base}",
                 "note": info.get("how") or info.get("why", ""),
                 "staged_lines": info.get("staged_lines", 0), "missing": info.get("missing", 0), "extra": info.get("extra", 0)}]
    if info["ok"]:
        return result(True, f"the promotion branch holds the tested change ({info['how']})", evidence)
    return result(False, info.get("why", "not equivalent"), evidence)


def check_analytics_contract(check: dict[str, Any], ctx: Any) -> dict[str, Any]:
    """S5: staging still has every table and column Owner Analytics copies, with the same type (Sifututor/owner-analytics#134).

    Only what the release adds counts: a copied column that the release removes or retypes fails and is named. What already broke
    the contract on staging before the deploy (the baseline S1 read) is listed and counted, never failed. New tables and columns
    are listed as information only."""
    try:
        cfg = staging_cfg(ctx.data)
        sha, ref = str(cfg.get("candidate_sha", "")), str(cfg.get("candidate_ref", ""))
        target = cfg["target"]
        if not sr.valid_sha(sha) or ctx.data.get("staging_sha") != sha:
            return result(False, "staging has not been deployed with the candidate yet (S2 comes first)")
        baseline = cfg.get("contract_baseline")
        if not isinstance(baseline, dict) or baseline.get("candidate_sha") != sha or not isinstance(baseline.get("breaking"), list):
            return result(False, f"there is no S5 baseline for {sha[:10]} (what already broke the contract on staging before this "
                                 "release; older release states have none), so S5 fails closed: rerun S1 before staging is "
                                 "deployed, which happens when the staging candidate moves")
        entries, contract = load_contract(ctx.shell, target, ctx.stop_check)
        tables = sorted({e["source_table"] for e in entries})
        columns = sum(len(e["source_columns"]) for e in entries)
        evidence: list[dict[str, Any]] = [{
            "command": f"git show {contract['sha'][:12]}:{contract['path']} (owner-analytics {OA_REF})",
            "sha": contract["sha"],
            "note": f"{len(tables)} copied tables, {columns} copied columns"
                    + ("" if contract["fetched"] else "; could not refresh from GitHub, so the last fetched main was used")}]
        deployer = deployer_for(ctx, cfg)
        ok, text = deployer.verify(sha, ref)
        evidence.append({"command": f"remote {target} verify {sha[:12]}", "note": (text.splitlines() or ["no answer"])[-1]})
        if not ok:
            return result(False, "staging no longer serves the deployed commit, so its columns would belong to something else", evidence)
        rows = deployer.schema(tables)
    except DeployError as exc:
        return result(False, str(exc))
    diff = compare_contract(entries, rows)
    before = {contract_key(i) for i in baseline["breaking"] if isinstance(i, dict)}
    breaking = [contract_item_text(i) for i in diff["breaking"] if contract_key(i) not in before]
    already = [contract_item_text(i) for i in diff["breaking"] if contract_key(i) in before]
    new = [contract_item_text(i) for i in diff["new"]]
    evidence.append({"command": f"remote {target} schema ({len(tables)} copied tables, one read-only SELECT on staging)",
                     "note": f"{len(rows)} columns read; {len(breaking)} breaking added by this release; {len(already)} already on "
                             f"staging before it (baseline read {baseline.get('read_at', '?')}); {len(new)} new",
                     "breaking": breaking, "already_on_staging": already, "new": new})
    old = (f"; {len(already)} already on staging before this release (not caused by it): {', '.join(already[:8])}"
           f"{' and more' if len(already) > 8 else ''}") if already else ""
    info = f"; for information, not copied yet: {', '.join(new[:8])}{' and more' if len(new) > 8 else ''}" if new else ""
    if breaking:
        return result(False, f"{len(breaking)} copied column(s) would stop the Owner Analytics copy: {', '.join(breaking[:10])}"
                      + (" and more" if len(breaking) > 10 else "") + old + info, evidence,
                      "Breaking, added by this release (the copier stops these tables):\n" + "\n".join(breaking)
                      + ("\n\nAlready on staging before this release (not caused by it):\n" + "\n".join(already) if already else "")
                      + ("\n\nNew, information only:\n" + "\n".join(new) if new else ""))
    return result(True, f"this release breaks no copied table or column on {target} staging ({len(tables)} tables, "
                  f"{columns} columns, owner-analytics main {contract['sha'][:10]}){old}{info}", evidence)


# ------------------------------------------------------------------- CLI ----

def report(path: Path, out: Callable[[str], None]) -> int:
    data = rr.load(path)
    cfg = data.get("staging")
    if not cfg:
        out("This release has no staging deploy section (S1 to S3 are Mac gates).")
        return 0
    out(f"Release {data['release']}: PC staging deploy to {cfg.get('target')} (mode {cfg.get('mode', 'normal')})")
    out(f"  candidate: {cfg.get('candidate_ref') or candidate_ref(data, cfg)} at {cfg.get('candidate_sha', 'not accepted yet')}")
    out(f"  deployed commit read back: {data.get('staging_sha', 'none yet')}")
    baseline = cfg.get("contract_baseline")
    if isinstance(baseline, dict):
        out(f"  S5 baseline: {len(baseline.get('breaking') or [])} breaking already on staging before this release, "
            f"read {baseline.get('read_at', '?')} for {str(baseline.get('candidate_sha', ''))[:10]}")
    items = rr.item_map(data)
    for iid in ("S1", "S2", "S3", "S4", "S5"):
        if iid in items and rr.is_applicable(items[iid]):
            out(f"  {iid} {items[iid].get('title', '')[:70]} [{items[iid].get('owner')}]: {items[iid].get('status')}")
    if cfg.get("deploy"):
        out(f"  deploy in flight: run {cfg['deploy'].get('run')} since {cfg['deploy'].get('started')}")
    for entry in (cfg.get("deploys") or [])[-3:]:
        out(f"  earlier run {entry.get('run')} {'ok' if entry.get('ok') else 'not ok'} at {entry.get('at')}")
    try:
        live = Deployer(cfg["target"], rr.RealShell()).status(cfg.get("deploy", {}).get("run") if cfg.get("deploy") else None)
        out("  live status from the box: " + (live["result"] or f"state {live['state']}"))
    except (DeployError, KeyError) as exc:
        out(f"  live status unavailable: {exc}")
    return 0


def print_baseline(path: Path, out: Callable[[str], None]) -> None:
    """The S5 baseline S1 stored for the current release: what already broke the contract on staging before its deploy."""
    try:
        data = rr.load(path)
    except rr.ReadinessError as exc:
        out(f"no S5 baseline: {exc}")
        return
    baseline = (data.get("staging") or {}).get("contract_baseline")
    if not isinstance(baseline, dict):
        out(f"no S5 baseline in release {data.get('release', '?')} yet (S1 reads it before staging is deployed)")
        return
    items = baseline.get("breaking") or []
    out(f"baseline of release {data.get('release', '?')}: read {baseline.get('read_at', '?')} for candidate "
        f"{str(baseline.get('candidate_sha', ''))[:10]}, owner-analytics main {str(baseline.get('contract_sha', ''))[:10]}, "
        f"{len(items)} breaking already on staging before this release (not caused by it)")
    for item in items:
        out("  baseline " + contract_item_text(item))


def main(argv: list[str] | None = None, out: Callable[[str], None] = print, shell: Any = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("check", "deploy"):
        p = sub.add_parser(name)
        p.add_argument("target", choices=sr.TARGETS)
        p.add_argument("--ref", required=True)
        p.add_argument("--sha", default="")
        p.add_argument("--mode", default="normal", choices=sr.MODES)
        p.add_argument("--base", default="")
        p.add_argument("--repo-dir", type=Path)
        p.add_argument("--actor", default="pc-cli")
        p.add_argument("--release", default="manual")
        p.add_argument("--holder", default="", help="who deploys, for the Ripple staging lease (default: the actor)")
        p.add_argument("--override-lease", default="", metavar="REASON",
                       help="deploy although someone else holds the Ripple staging lease; the reason is logged and printed")
    p = sub.add_parser("status"); p.add_argument("target", choices=sr.TARGETS); p.add_argument("run", nargs="?")
    p = sub.add_parser("lease", help="take or extend the Ripple staging lease")
    p.add_argument("target", choices=("ripple",))
    p.add_argument("--holder", required=True)
    p.add_argument("--purpose", required=True)
    p.add_argument("--minutes", required=True, type=int)
    p.add_argument("--branch", default="")
    p = sub.add_parser("release-lease", help="release the Ripple staging lease")
    p.add_argument("target", choices=("ripple",))
    p.add_argument("--holder", default="", help="who releases it, for the box log (default: pc-cli)")
    p = sub.add_parser("verify"); p.add_argument("target", choices=sr.TARGETS); p.add_argument("sha"); p.add_argument("--ref")
    p = sub.add_parser("switch"); p.add_argument("target", choices=sr.TARGETS); p.add_argument("action", choices=("on", "off", "show"))
    p = sub.add_parser("report"); p.add_argument("readiness", type=Path)
    p = sub.add_parser("contract"); p.add_argument("target", choices=sr.TARGETS)
    p.add_argument("--baseline", nargs="?", const=Path("readiness.json"), type=Path,
                   help="also print the S5 baseline of the current release (default readiness.json in the release folder)")
    args = parser.parse_args(argv)
    shell = shell or rr.RealShell()
    try:
        if args.cmd == "report":
            return report(args.readiness, out)
        if args.cmd == "contract":
            entries, contract = load_contract(shell, args.target)
            rows = Deployer(args.target, shell).schema(sorted({e["source_table"] for e in entries}))
            diff = compare_contract(entries, rows)
            out(f"owner-analytics {OA_REF} {contract['sha'][:10]} {contract['path']}"
                + ("" if contract["fetched"] else " (could not refresh from GitHub)"))
            out(f"{args.target} staging: {len(rows)} columns read, {len(diff['breaking'])} breaking, {len(diff['new'])} new")
            for item in diff["breaking"]:
                out("  BREAKING " + contract_item_text(item))
            for item in diff["new"]:
                out("  new      " + contract_item_text(item))
            if args.baseline:
                print_baseline(args.baseline, out)
            return 1 if diff["breaking"] else 0
        if args.cmd in ("check", "deploy"):
            sha = args.sha
            if not sha:
                sha, why = local_tip(shell, args.repo_dir, args.ref, None)
                if why:
                    raise DeployError(why)
            deployer = Deployer(args.target, shell, actor=args.actor, release=args.release, holder=args.holder,
                                override_lease=args.override_lease)
            if args.cmd == "check":
                ok, line = deployer.check(args.ref, sha, args.mode, args.base)
                out(line if ok else f"REFUSED: {line}")
                return 0 if ok else 2
            t0 = time.time()
            outcome = deployer.deploy_and_verify(args.ref, sha, args.mode, args.base, on_poll=lambda i: out(
                f"  [{rr.myt_text()}] {i['state']} step {i['step']}"))
            for entry in outcome["evidence"]:
                out("  " + (entry.get("note") or entry.get("command", "")))
            out(("DEPLOYED: " if outcome["ok"] else "NOT DEPLOYED: ") + outcome["summary"] + f" ({int(time.time() - t0)} s)")
            return 0 if outcome["ok"] else 1
        if args.cmd in ("lease", "release-lease"):
            deployer = Deployer(args.target, shell, actor="pc-cli", holder=args.holder)
            ok, text = deployer.lease(args.purpose, args.minutes, args.branch) if args.cmd == "lease" else deployer.release_lease()
            out(text if ok else f"REFUSED: {text}")
            return 0 if ok else 2
        deployer = Deployer(args.target, shell)
        if args.cmd == "status":
            out(deployer.status(args.run)["raw"].strip())
        elif args.cmd == "verify":
            ok, text = deployer.verify(args.sha, args.ref)
            out(text)
            return 0 if ok else 1
        elif args.cmd == "switch":
            out(deployer.switch(args.action))
        return 0
    except DeployError as exc:
        out(f"REFUSED: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
