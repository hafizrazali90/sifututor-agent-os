#!/usr/bin/env python3
"""Safely verify Microsoft Teams Planner read capability for staff intake."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENV = Path.home() / ".config/sifututor/m365-readonly.env"
DEFAULT_GROUP = "Development & Support"
DEFAULT_PLAN = "Task Management Board"
GRAPH_ROOT = "https://graph.microsoft.com/v1.0"


def read_env(path: Path) -> dict[str, str]:
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


def load_json(request: urllib.request.Request, timeout: int) -> dict:
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as error:
        body = error.read().decode()
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            data = {"error": {"code": f"http_{error.code}", "message": "non-json error response"}}
        data.setdefault("error", {})
        data["error"].setdefault("status", error.code)
        return data
    except (TimeoutError, urllib.error.URLError) as error:
        return {"error": {"code": "network_error", "message": str(error)}}


def post_form(url: str, data: dict[str, str], timeout: int = 20) -> dict:
    request = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(data).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    return load_json(request, timeout)


def get_json(url: str, token: str, timeout: int = 20) -> dict:
    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        method="GET",
    )
    return load_json(request, timeout)


def graph_url(path: str, params: dict[str, str] | None = None) -> str:
    url = f"{GRAPH_ROOT}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    return url


def error_code(data: dict) -> str | None:
    error = data.get("error")
    if isinstance(error, dict):
        return str(error.get("code") or error.get("status") or "error")
    return None


def build_result(env_path: Path, group_name: str, plan_name: str) -> dict:
    env = read_env(env_path)
    required = ["M365_TENANT_ID", "M365_CLIENT_ID", "M365_CLIENT_SECRET"]
    missing = [key for key in required if not env.get(key)]
    if missing:
        return {
            "name": "planner",
            "state": "not_connected",
            "method": "microsoft-graph-direct",
            "evidence": "m365 read-only config missing required keys",
            "missing_keys": missing,
            "note": "No secret values are printed by this probe.",
        }

    token_response = post_form(
        f"https://login.microsoftonline.com/{env['M365_TENANT_ID']}/oauth2/v2.0/token",
        {
            "client_id": env["M365_CLIENT_ID"],
            "client_secret": env["M365_CLIENT_SECRET"],
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        },
    )
    token = token_response.get("access_token")
    if not token:
        return {
            "name": "planner",
            "state": "not_connected",
            "method": "microsoft-graph-direct",
            "evidence": "Microsoft Graph token request failed",
            "error": error_code(token_response),
            "note": "No token or secret values are printed by this probe.",
        }

    safe_group_name = group_name.replace("'", "''")
    groups = get_json(
        graph_url(
            "/groups",
            {
                "$filter": f"displayName eq '{safe_group_name}'",
                "$select": "id,displayName",
                "$top": "5",
            },
        ),
        token,
    )
    if error_code(groups):
        return {
            "name": "planner",
            "state": "unknown",
            "method": "microsoft-graph-direct",
            "evidence": "Microsoft Graph group lookup failed",
            "target_group": group_name,
            "error": error_code(groups),
            "note": "Check app permissions for group reads.",
        }

    group_matches = groups.get("value") or []
    if not group_matches:
        return {
            "name": "planner",
            "state": "unknown",
            "method": "microsoft-graph-direct",
            "evidence": "target Microsoft 365 group not found",
            "target_group": group_name,
            "note": "Graph auth worked, but the expected staff intake group was not visible.",
        }

    plans = get_json(graph_url(f"/groups/{group_matches[0].get('id')}/planner/plans"), token)
    if error_code(plans):
        return {
            "name": "planner",
            "state": "unknown",
            "method": "microsoft-graph-direct",
            "evidence": "Planner plan lookup failed",
            "target_group": group_name,
            "target_plan": plan_name,
            "error": error_code(plans),
            "note": "Check Planner read permissions.",
        }

    plan_values = plans.get("value") or []
    matching_plan = next((plan for plan in plan_values if plan.get("title") == plan_name), None)
    if not matching_plan:
        return {
            "name": "planner",
            "state": "unknown",
            "method": "microsoft-graph-direct",
            "evidence": "target Planner board not found",
            "target_group": group_name,
            "target_plan": plan_name,
            "plan_count": len(plan_values),
            "note": "Graph auth worked, but the expected Planner board was not visible.",
        }

    tasks = get_json(
        graph_url(
            f"/planner/plans/{matching_plan.get('id')}/tasks",
            {"$select": "id,percentComplete,createdDateTime"},
        ),
        token,
    )
    if error_code(tasks):
        return {
            "name": "planner",
            "state": "unknown",
            "method": "microsoft-graph-direct",
            "evidence": "Planner task metadata read failed",
            "target_group": group_name,
            "target_plan": plan_name,
            "plan_count": len(plan_values),
            "error": error_code(tasks),
            "note": "No task titles, descriptions, assignees, or card content are printed.",
        }

    task_values = tasks.get("value") or []
    return {
        "name": "planner",
        "state": "available",
        "method": "microsoft-graph-direct",
        "evidence": "Graph auth, group lookup, plan lookup, and task metadata read passed",
        "target_group": group_name,
        "target_plan": plan_name,
        "plan_count": len(plan_values),
        "returned_task_metadata_count": len(task_values),
        "write_actions": "blocked_until_explicit_approval",
        "note": "This probe prints counts/status only; it does not print Planner card content or secret values.",
    }


def print_text(result: dict) -> None:
    print("Sifututor Agent OS Planner Probe")
    print(f"Root: {ROOT}")
    print()
    print(f"{result['state'].upper():14} planner                 {result['evidence']}")
    if result.get("target_group"):
        print(f"{'':14} {'':24} group={result['target_group']}")
    if result.get("target_plan"):
        print(f"{'':14} {'':24} plan={result['target_plan']}")
    if "plan_count" in result:
        print(f"{'':14} {'':24} visible_plans={result['plan_count']}")
    if "returned_task_metadata_count" in result:
        print(f"{'':14} {'':24} task_metadata_rows={result['returned_task_metadata_count']}")
    if result.get("error"):
        print(f"{'':14} {'':24} error={result['error']}")
    if result.get("note"):
        print(f"{'':14} {'':24} {result['note']}")
    if result.get("write_actions"):
        print(f"{'':14} {'':24} write_actions={result['write_actions']}")
    print()
    print("Practical rule: Planner may be used as read-only staff intake; card edits still need approval.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Teams Planner read capability through Microsoft Graph.")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    parser.add_argument("--env", default=str(DEFAULT_ENV), help="path to m365 read-only env file")
    parser.add_argument("--group", default=DEFAULT_GROUP, help="Microsoft 365 group display name")
    parser.add_argument("--plan", default=DEFAULT_PLAN, help="Planner plan title")
    args = parser.parse_args()

    result = build_result(Path(args.env).expanduser(), args.group, args.plan)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_text(result)
    return 0 if result["state"] == "available" else 1


if __name__ == "__main__":
    sys.exit(main())
