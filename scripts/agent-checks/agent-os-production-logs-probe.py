#!/usr/bin/env python3
"""Safely verify read-only production monitoring capability."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONF = Path.home() / ".config/sifututor/agent-access/monitoring-readonly.conf"


def read_conf(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_json(url: str, token: str, timeout: int = 20) -> tuple[int, dict | list | None]:
    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode()
            return response.status, json.loads(body) if body else None
    except urllib.error.HTTPError as error:
        body = error.read().decode()
        try:
            payload = json.loads(body) if body else None
        except json.JSONDecodeError:
            payload = None
        return error.code, payload
    except (TimeoutError, urllib.error.URLError):
        return 0, None


def sentry_probe(conf: dict[str, str]) -> dict:
    required = ["SENTRY_AUTH_TOKEN", "SENTRY_ORG_SLUG", "SENTRY_PROJECT_SLUG"]
    missing = [key for key in required if not conf.get(key)]
    if missing:
        return {"state": "not_connected", "missing_keys": missing}

    org = conf["SENTRY_ORG_SLUG"]
    project = conf["SENTRY_PROJECT_SLUG"]
    org_status, _ = load_json(f"https://sentry.io/api/0/organizations/{org}/", conf["SENTRY_AUTH_TOKEN"])
    params = urllib.parse.urlencode({"query": "is:unresolved", "limit": "1"})
    issues_status, issues = load_json(
        f"https://sentry.io/api/0/projects/{org}/{project}/issues/?{params}",
        conf["SENTRY_AUTH_TOKEN"],
    )
    sample_count = len(issues) if isinstance(issues, list) else None
    return {
        "state": "available" if org_status == 200 and issues_status == 200 else "unknown",
        "org_status": org_status,
        "issues_status": issues_status,
        "unresolved_issue_sample_count": sample_count,
    }


def betterstack_probe(conf: dict[str, str]) -> dict:
    required = ["BETTERSTACK_UPTIME_TOKEN"]
    missing = [key for key in required if not conf.get(key)]
    if missing:
        return {"state": "not_connected", "missing_keys": missing}

    status, monitors = load_json(
        "https://uptime.betterstack.com/api/v2/monitors?per_page=1",
        conf["BETTERSTACK_UPTIME_TOKEN"],
    )
    sample_count = len(monitors.get("data", [])) if isinstance(monitors, dict) else None
    return {
        "state": "available" if status == 200 else "unknown",
        "monitors_status": status,
        "monitor_sample_count": sample_count,
    }


def build_result(conf_path: Path) -> dict:
    conf = read_conf(conf_path)
    if not conf:
        return {
            "name": "production_logs",
            "state": "not_connected",
            "method": "sentry-betterstack-readonly",
            "evidence": "monitoring read-only config missing",
            "config": str(conf_path),
            "note": "No secret values are printed by this probe.",
        }

    sentry = sentry_probe(conf)
    betterstack = betterstack_probe(conf)
    available = sentry.get("state") == "available" and betterstack.get("state") == "available"
    partial = sentry.get("state") == "available" or betterstack.get("state") == "available"
    state = "available" if available else "unknown" if partial else "not_connected"
    return {
        "name": "production_logs",
        "state": state,
        "method": "sentry-betterstack-readonly",
        "evidence": "read-only monitoring probe completed",
        "sentry": sentry,
        "betterstack": betterstack,
        "write_actions": "blocked_until_explicit_approval",
        "note": "This probe prints HTTP status and small counts only; it does not print issue titles, events, monitor URLs, logs, tokens, or secrets.",
    }


def print_text(result: dict) -> None:
    print("Sifututor Agent OS Production Logs Probe")
    print(f"Root: {ROOT}")
    print()
    print(f"{result['state'].upper():14} production_logs          {result['evidence']}")
    sentry = result.get("sentry") or {}
    betterstack = result.get("betterstack") or {}
    if sentry:
        print(
            f"{'':14} {'':24} sentry={sentry.get('state')} "
            f"org_http={sentry.get('org_status')} issues_http={sentry.get('issues_status')} "
            f"issue_sample={sentry.get('unresolved_issue_sample_count')}"
        )
    if betterstack:
        print(
            f"{'':14} {'':24} betterstack={betterstack.get('state')} "
            f"monitors_http={betterstack.get('monitors_status')} "
            f"monitor_sample={betterstack.get('monitor_sample_count')}"
        )
    if result.get("note"):
        print(f"{'':14} {'':24} {result['note']}")
    if result.get("write_actions"):
        print(f"{'':14} {'':24} write_actions={result['write_actions']}")
    print()
    print("Practical rule: monitoring read access may gather evidence; resolving issues or changing monitors still needs approval.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify read-only production monitoring access.")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    parser.add_argument("--conf", default=str(DEFAULT_CONF), help="path to monitoring read-only conf")
    args = parser.parse_args()

    result = build_result(Path(args.conf).expanduser())
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_text(result)
    return 0 if result["state"] == "available" else 1


if __name__ == "__main__":
    raise SystemExit(main())
