#!/usr/bin/env python3
"""Safely verify GitHub read capability for the current repository."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run_command(command: list[str], timeout: int = 15) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def safe_lines(value: str) -> list[str]:
    lines = []
    for line in value.splitlines():
        if "Token:" in line:
            continue
        lines.append(line.strip())
    return [line for line in lines if line]


def extract_account(lines: list[str]) -> str:
    for line in lines:
        match = re.search(r"account\s+([A-Za-z0-9_.-]+)", line)
        if match:
            return match.group(1)
    for line in lines:
        if "Active account:" in line:
            return line.split(":", 1)[1].strip().lower()
    return "unknown"


def build_result(repo: str | None = None) -> dict:
    gh_path = shutil.which("gh")
    if not gh_path:
        return {
            "name": "github",
            "state": "not_connected",
            "method": "gh-cli",
            "evidence": "gh command not found",
            "repo": None,
            "note": "Install/authenticate GitHub CLI or use a scoped read-only MCP/API probe.",
        }

    auth = run_command(["gh", "auth", "status", "--hostname", "github.com"])
    auth_lines = safe_lines(auth.stdout + "\n" + auth.stderr)
    if auth.returncode != 0:
        return {
            "name": "github",
            "state": "not_connected",
            "method": "gh-cli",
            "evidence": "gh auth status failed",
            "repo": None,
            "note": "No token or account details are printed by this probe.",
        }

    command = [
        "gh",
        "repo",
        "view",
    ]
    if repo:
        command.append(repo)
    command.extend(["--json", "nameWithOwner,defaultBranchRef,viewerPermission,isPrivate,url"])
    view = run_command(command)
    if view.returncode != 0:
        return {
            "name": "github",
            "state": "unknown",
            "method": "gh-cli",
            "evidence": "gh authenticated but repo metadata read failed",
            "repo": None,
            "account": extract_account(auth_lines),
            "note": "Check current directory remote or pass --repo OWNER/REPO.",
        }

    data = json.loads(view.stdout)
    default_branch = data.get("defaultBranchRef") or {}
    permission = data.get("viewerPermission") or "UNKNOWN"
    return {
        "name": "github",
        "state": "available",
        "method": "gh-cli",
        "evidence": "gh auth and repo metadata read passed",
        "account": extract_account(auth_lines),
        "repo": {
            "nameWithOwner": data.get("nameWithOwner"),
            "defaultBranch": default_branch.get("name"),
            "viewerPermission": permission,
            "isPrivate": bool(data.get("isPrivate")),
            "url": data.get("url"),
        },
        "write_actions": "blocked_until_explicit_approval",
        "note": "This probe performs read-only auth and repo metadata checks only.",
    }


def print_text(result: dict) -> None:
    print("Sifututor Agent OS GitHub Probe")
    print(f"Root: {ROOT}")
    print()
    print(f"{result['state'].upper():14} github                  {result['evidence']}")
    if result.get("account"):
        print(f"{'':14} {'':24} account={result['account']}")
    repo = result.get("repo")
    if repo:
        print(
            f"{'':14} {'':24} repo={repo.get('nameWithOwner')} "
            f"default={repo.get('defaultBranch')} permission={repo.get('viewerPermission')}"
        )
        print(f"{'':14} {'':24} private={repo.get('isPrivate')} url={repo.get('url')}")
    if result.get("note"):
        print(f"{'':14} {'':24} {result['note']}")
    if result.get("write_actions"):
        print(f"{'':14} {'':24} write_actions={result['write_actions']}")
    print()
    print("Practical rule: GitHub read metadata may be used for evidence; push, PR, merge, and edits still need approval.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify GitHub read capability through gh CLI.")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    parser.add_argument("--repo", help="optional OWNER/REPO instead of current directory")
    args = parser.parse_args()

    result = build_result(args.repo)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_text(result)
    return 0 if result["state"] == "available" else 1


if __name__ == "__main__":
    raise SystemExit(main())
