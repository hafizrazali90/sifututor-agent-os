#!/usr/bin/env python3
"""Check whether Google Drive connector metadata is available for safe probes."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CODEX_HOME = Path.home() / ".codex"
TOOL_CACHE_DIR = CODEX_HOME / "cache/codex_apps_tools"
PLUGIN_CACHE_DIR = CODEX_HOME / "plugins/cache"
REQUIRED_TOOLS = ["_search", "_get_file_metadata", "_list_folder"]


def load_tool_cache() -> tuple[Path | None, list[dict]]:
    if not TOOL_CACHE_DIR.exists():
        return None, []
    for path in sorted(TOOL_CACHE_DIR.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        tools = data.get("tools") if isinstance(data, dict) else None
        if not isinstance(tools, list):
            continue
        if any(item.get("connector_name") == "Google Drive" for item in tools if isinstance(item, dict)):
            return path, tools
    return None, []


def plugin_present() -> bool:
    if not PLUGIN_CACHE_DIR.exists():
        return False
    return any(path.name == "google-drive" for path in PLUGIN_CACHE_DIR.glob("**/.codex-plugin/.."))


def build_result() -> dict:
    cache_path, tools = load_tool_cache()
    drive_tools = [item for item in tools if item.get("connector_name") == "Google Drive"]
    tool_names = sorted({item.get("tool_name") for item in drive_tools if item.get("tool_name")})
    missing = [name for name in REQUIRED_TOOLS if name not in tool_names]
    cli_candidates = {name: shutil.which(name) for name in ["gdrive", "rclone"]}
    has_cli = any(cli_candidates.values())

    if drive_tools and not missing:
        return {
            "name": "google_drive",
            "state": "unknown",
            "method": "codex-google-drive-connector",
            "evidence": "Google Drive connector metadata and low-noise read tools are installed",
            "connector_metadata": "available",
            "tool_cache": str(cache_path) if cache_path else None,
            "safe_probe_tools": REQUIRED_TOOLS,
            "live_read": "not_verified_by_local_script",
            "cli": {key: bool(value) for key, value in cli_candidates.items()},
            "write_actions": "blocked_until_explicit_approval",
            "note": "Use the Google Drive app connector for a tiny search/list/metadata read when tools are exposed in the session.",
        }

    return {
        "name": "google_drive",
        "state": "not_connected" if not has_cli else "unknown",
        "method": "codex-google-drive-connector",
        "evidence": "Google Drive low-noise read tools were not found in local connector metadata",
        "connector_metadata": "missing_or_incomplete",
        "missing_tools": missing or REQUIRED_TOOLS,
        "cli": {key: bool(value) for key, value in cli_candidates.items()},
        "note": "Install/connect Google Drive plugin or provide a scoped Drive CLI/API wrapper before claiming Drive read access.",
    }


def print_text(result: dict) -> None:
    print("Sifututor Agent OS Google Drive Probe")
    print(f"Root: {ROOT}")
    print()
    print(f"{result['state'].upper():14} google_drive            {result['evidence']}")
    if result.get("safe_probe_tools"):
        print(f"{'':14} {'':24} safe_probe_tools={', '.join(result['safe_probe_tools'])}")
    if result.get("live_read"):
        print(f"{'':14} {'':24} live_read={result['live_read']}")
    if result.get("missing_tools"):
        print(f"{'':14} {'':24} missing_tools={', '.join(result['missing_tools'])}")
    print(f"{'':14} {'':24} cli_gdrive={result.get('cli', {}).get('gdrive', False)} cli_rclone={result.get('cli', {}).get('rclone', False)}")
    if result.get("note"):
        print(f"{'':14} {'':24} {result['note']}")
    if result.get("write_actions"):
        print(f"{'':14} {'':24} write_actions={result['write_actions']}")
    print()
    print("Practical rule: use tiny Drive search/list/metadata reads; do not fetch document contents unless the task needs them.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Google Drive connector metadata for safe read probes.")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    result = build_result()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_text(result)
    return 0 if result["state"] in {"available", "unknown"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
