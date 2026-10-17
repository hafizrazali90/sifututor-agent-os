#!/usr/bin/env python3
"""Claude Code status line that also saves the plan usage reading for this account.

Claude Code passes the status line a JSON document. For claude.ai Pro and Max
subscribers it includes rate_limits.five_hour and rate_limits.seven_day with
used_percentage and resets_at. That is the only documented way to read plan
usage, so this script saves the latest reading per account for the Session Map
page (see usage_readings.py) and prints a short line for the terminal.

It never fails the session: any problem prints nothing and exits 0.
Agreed with Hafiz on 17/10/2026.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
import time


def usage_dir() -> Path:
    override = os.environ.get("AGENT_OS_USAGE_DIR")
    return Path(override) if override else Path.home() / ".agent-os" / "usage"


def machine() -> str:
    return "Mac" if sys.platform == "darwin" else "PC"


def account_name() -> str:
    """The part of the signed-in email before the @, read from this profile only."""
    config = os.environ.get("CLAUDE_CONFIG_DIR")
    path = (Path(config) / ".claude.json") if config else (Path.home() / ".claude.json")
    try:
        email = json.loads(path.read_text(encoding="utf-8"))["oauthAccount"]["emailAddress"]
        name = str(email).split("@")[0]
    except (OSError, ValueError, KeyError, TypeError):
        return "unknown"
    return re.sub(r"[^A-Za-z0-9._-]", "", name)[:60] or "unknown"


def _window(raw) -> dict | None:
    if not isinstance(raw, dict):
        return None
    used = raw.get("used_percentage")
    if isinstance(used, bool) or not isinstance(used, (int, float)):
        return None
    resets = raw.get("resets_at")
    return {"used": float(used), "resets_at": float(resets) if isinstance(resets, (int, float)) else None}


def handle(payload: dict, now: float | None = None) -> str:
    limits = payload.get("rate_limits")
    if not isinstance(limits, dict):
        return ""
    five, week = _window(limits.get("five_hour")), _window(limits.get("seven_day"))
    if five is None and week is None:
        return ""
    stamp = time.time() if now is None else now
    account = account_name()
    directory = usage_dir()
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"claude-{account}.json"
    reading = {"account": account, "machine": machine(), "read_at": stamp, "five_hour": five, "seven_day": week}
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(reading), encoding="utf-8")
    temporary.replace(target)
    parts = []
    if five is not None:
        parts.append(f"5h {round(five['used'])}%")
    if week is not None:
        parts.append(f"week {round(week['used'])}%")
    return " · ".join(parts)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        text = handle(payload) if isinstance(payload, dict) else ""
        if text:
            print(text)
    except Exception:  # a status line must never break the session
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
