#!/usr/bin/env python3
"""Collect trustworthy, team-level weekly GitHub delivery facts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from typing import Callable, Sequence


Runner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


@dataclass
class RepoResult:
    repo: str
    status: str
    exit_code: int
    item_count: int
    expected_count: int | None
    collected_at: str
    items: list[dict]


def run_command(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def search_query(repo: str, since: str, asof: str) -> str:
    return f"repo:{repo} is:pr is:merged merged:{since}..{asof}"


def collect_repo(repo: str, since: str, asof: str, runner: Runner = run_command) -> RepoResult:
    collected_at = dt.datetime.now(dt.timezone.utc).isoformat()
    query = search_query(repo, since, asof)
    item_result = runner([
        "gh", "search", "prs", "--repo", repo, "--merged", "--merged-at",
        f"{since}..{asof}", "--limit", "1000", "--json",
        "number,title,url,closedAt,author",
    ])
    if item_result.returncode != 0:
        return RepoResult(repo, "failed", item_result.returncode, 0, None, collected_at, [])

    try:
        items = json.loads(item_result.stdout)
    except (json.JSONDecodeError, TypeError):
        return RepoResult(repo, "failed", 1, 0, None, collected_at, [])
    if not isinstance(items, list):
        return RepoResult(repo, "failed", 1, 0, None, collected_at, [])

    count_result = runner([
        "gh", "api", "graphql", "-f",
        "query=query($q:String!){search(query:$q,type:ISSUE){issueCount}}",
        "-F", f"q={query}", "--jq", ".data.search.issueCount",
    ])
    if count_result.returncode != 0:
        return RepoResult(repo, "partial", count_result.returncode, len(items), None, collected_at, items)
    try:
        expected_count = int(count_result.stdout.strip())
    except (TypeError, ValueError):
        return RepoResult(repo, "partial", 1, len(items), None, collected_at, items)

    status = "empty" if expected_count == 0 else "ok"
    if expected_count != len(items):
        status = "partial"
    return RepoResult(repo, status, 0, len(items), expected_count, collected_at, items)


def overall_status(results: list[RepoResult]) -> str:
    healthy = {"ok", "empty"}
    healthy_count = sum(result.status in healthy for result in results)
    if healthy_count == len(results):
        return "quiet" if all(result.status == "empty" for result in results) else "available"
    return "unavailable" if healthy_count == 0 else "partial"


def build_report(repos: list[str], since: str, asof: str, runner: Runner = run_command) -> dict:
    results = [collect_repo(repo, since, asof, runner) for repo in repos]
    status = overall_status(results)
    return {
        "schema_version": 1,
        "window": {"since": since, "asof": asof},
        "status": status,
        "coverage": {
            "repos_expected": len(results),
            "repos_healthy": sum(result.status in {"ok", "empty"} for result in results),
        },
        "shareable_summary_allowed": status in {"available", "quiet"},
        "repositories": [asdict(result) for result in results],
    }


def valid_date(value: str) -> str:
    dt.date.fromisoformat(value)
    return value


def main(argv: list[str] | None = None) -> int:
    today = dt.date.today()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", action="append", required=True, help="GitHub OWNER/REPO; repeat for each repository")
    parser.add_argument("--since", type=valid_date, default=(today - dt.timedelta(days=7)).isoformat())
    parser.add_argument("--asof", type=valid_date, default=today.isoformat())
    args = parser.parse_args(argv)
    if args.since > args.asof:
        parser.error("--since must not be later than --asof")

    report = build_report(args.repo, args.since, args.asof)
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if report["status"] in {"available", "quiet"} else 4


if __name__ == "__main__":
    raise SystemExit(main())
