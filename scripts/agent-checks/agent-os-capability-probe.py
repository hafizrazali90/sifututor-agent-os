#!/usr/bin/env python3
"""Report local Agent OS capability state without mutating external systems."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run_command(command: list[str], timeout: int = 10) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def record(name: str, state: str, evidence: str, note: str = "") -> dict[str, str]:
    return {
        "name": name,
        "state": state,
        "evidence": evidence,
        "note": note,
    }


def check_filesystem() -> dict[str, str]:
    try:
        with tempfile.NamedTemporaryFile(prefix=".agent-os-probe-", dir=ROOT, delete=True) as handle:
            handle.write(b"ok")
        return record("filesystem", "available", "workspace write probe succeeded")
    except OSError as exc:
        return record("filesystem", "not_connected", f"workspace write probe failed: {exc}")


def check_git() -> list[dict[str, str]]:
    if run_command(["git", "rev-parse", "--is-inside-work-tree"]).returncode != 0:
        return [
            record("git_status_diff", "not_connected", "not inside a git worktree"),
            record("git_commit", "not_connected", "not inside a git worktree"),
            record("git_push", "not_connected", "not inside a git worktree"),
        ]

    branch = run_command(["git", "branch", "--show-current"]).stdout.strip() or "detached"
    ahead_behind = run_command(["git", "status", "--short", "--branch"]).stdout.splitlines()
    evidence = f"branch={branch}"
    if ahead_behind:
        evidence = f"{evidence}; {ahead_behind[0]}"

    return [
        record("git_status_diff", "available", evidence, "local read-only git evidence is safe"),
        record("git_commit", "blocked", "requires exact file-list approval and pre-commit guard"),
        record("git_push", "blocked", "requires explicit current-session approval"),
        record("pull_request", "blocked", "requires explicit current-session approval"),
        record("merge", "blocked", "requires explicit current-session approval"),
    ]


def check_koda() -> dict[str, str]:
    koda = ROOT / "scripts/agent-checks/koda"
    if not koda.is_file():
        return record("koda", "not_connected", "scripts/agent-checks/koda missing")

    result = run_command([str(koda), "health"], timeout=15)
    if result.returncode == 0:
        return record("koda", "available", "direct Koda CLI health passed")
    return record("koda", "fallback", "Koda CLI exists but health did not pass", "use documented fallback/report path")


def check_local_wrappers() -> dict[str, str]:
    wrapper_dir = ROOT / "scripts/agent-access"
    wrappers = [
        "agent-access-doctor.sh",
        "check-backups.sh",
        "check-cloudflare-dns.sh",
        "check-cpanel-autossl.sh",
        "check-microsoft-planner.sh",
        "check-monitoring.sh",
        "check-ripple-prod.sh",
        "check-sims-db-readonly.sh",
        "check-st-admin-cert.sh",
    ]
    missing = [name for name in wrappers if not (wrapper_dir / name).is_file()]
    if missing:
        return record(
            "agent_access_wrappers",
            "unknown",
            f"{len(wrappers) - len(missing)}/{len(wrappers)} wrappers present",
            "missing: " + ", ".join(missing),
        )
    return record(
        "agent_access_wrappers",
        "available",
        f"{len(wrappers)}/{len(wrappers)} wrappers present",
        "presence only; run task-relevant wrapper before claiming live access",
    )


def check_local_command(name: str, command: str) -> dict[str, str]:
    result = run_command(["bash", "-lc", f"command -v {command}"], timeout=5)
    if result.returncode == 0:
        note = "connector/login still needs a safe probe"
        if name == "github":
            note = "run scripts/agent-checks/agent-os-github-probe.py before claiming GitHub read access"
        return record(name, "unknown", f"local command found: {result.stdout.strip()}", note)
    return record(name, "unknown", f"local command not found: {command}", "session connector may still exist")


def build_report() -> list[dict[str, str]]:
    items: list[dict[str, str]] = [
        check_filesystem(),
        *check_git(),
        check_koda(),
        check_local_wrappers(),
        check_local_command("github", "gh"),
        record(
            "google_drive",
            "unknown",
            "requires Google Drive connector or scoped Drive wrapper probe",
            "run scripts/agent-checks/agent-os-google-drive-probe.py before claiming Drive read access",
        ),
        record(
            "planner",
            "unknown",
            "requires Microsoft 365 connector or m365 read-only wrapper probe",
            "run scripts/agent-checks/agent-os-planner-probe.py before claiming Planner read access",
        ),
        record(
            "production_logs",
            "unknown",
            "requires task-relevant monitoring wrapper or connector read probe",
            "run scripts/agent-checks/agent-os-production-logs-probe.py before claiming monitoring read access",
        ),
        record("deploy", "blocked", "deploy approval required even when tooling exists"),
        record("plane", "exception_only", "do not use unless Hafiz explicitly asks in this session"),
        record("env_files", "forbidden", "never read or modify repository .env* files"),
        record("live_write", "forbidden", "never modify live/"),
        record("no_verify", "forbidden", "never bypass hooks or tests with --no-verify"),
    ]
    return items


def print_text(items: list[dict[str, str]]) -> None:
    print("Sifututor Agent OS Capability Probe")
    print(f"Root: {ROOT}")
    print()
    for item in items:
        print(f"{item['state'].upper():14} {item['name']:<24} {item['evidence']}")
        if item["note"]:
            print(f"{'':14} {'':24} {item['note']}")
    print()
    print("Practical rule: use available/fallback read-only evidence when task-relevant; stop at blocked/forbidden gates.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Report local Agent OS capability state.")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    os.chdir(ROOT)
    items = build_report()
    if args.json:
        print(json.dumps({"root": str(ROOT), "capabilities": items}, indent=2))
    else:
        print_text(items)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
