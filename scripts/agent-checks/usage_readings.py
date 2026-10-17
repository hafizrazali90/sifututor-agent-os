#!/usr/bin/env python3
"""Real plan usage per account, as rows for the Session Map page.

Claude readings come from the files the status line saves
(claude_usage_statusline.py). The Codex reading comes from the newest limit
event in Codex's own session log. Nothing is estimated: an account with no
reading gets used = null and the note "No reading yet". Every reading shows the
time it was taken, in Malaysian time.

Usage: python3 scripts/agent-checks/usage_readings.py [--accounts a,b]
prints the JSON list to put in the page's `usage` field.
Agreed with Hafiz on 17/10/2026.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
import sys
import time

MYT = timezone(timedelta(hours=8))
OLD_AFTER_SECONDS = 6 * 3600


def usage_dir() -> Path:
    override = os.environ.get("AGENT_OS_USAGE_DIR")
    return Path(override) if override else Path.home() / ".agent-os" / "usage"


def machine() -> str:
    return "Mac" if sys.platform == "darwin" else "PC"


def fmt(stamp: float | None) -> str:
    if stamp is None:
        return ""
    return datetime.fromtimestamp(stamp, MYT).strftime("%d/%m %H:%M MYT")


def _safe(account: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "", account)[:60] or "unknown"


def claude_rows(accounts: list[str], now: float | None = None) -> list[dict]:
    moment = time.time() if now is None else now
    rows = []
    for account in accounts:
        path = usage_dir() / f"claude-{_safe(account)}.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = None
        if not isinstance(data, dict) or not (data.get("seven_day") or data.get("five_hour")):
            rows.append(
                {
                    "n": account,
                    "where": "Unknown machine",
                    "plan": "Claude",
                    "used": None,
                    "note": "No reading yet. It appears after this account's status line has run.",
                }
            )
            continue
        week, five = data.get("seven_day"), data.get("five_hour")
        main_window = week or five
        notes = []
        if week and five:
            notes.append(f"5-hour window {round(five['used'])}%, resets {fmt(five.get('resets_at'))}.")
        read_at = float(data.get("read_at") or 0)
        if moment - read_at > OLD_AFTER_SECONDS:
            notes.append(f"Old reading, from {int((moment - read_at) // 3600)} hours ago.")
        rows.append(
            {
                "n": account,
                "where": data.get("machine") or "Unknown machine",
                "plan": "Claude",
                "used": round(float(main_window["used"]), 1),
                "window": "Weekly limit" if week else "5-hour limit",
                "resets": fmt(main_window.get("resets_at")),
                "read": fmt(read_at),
                "note": " ".join(notes),
            }
        )
    return rows


def codex_row(sessions: Path | None = None) -> dict:
    folder = sessions or (Path.home() / ".codex" / "sessions")
    best: tuple[str, dict] | None = None
    try:
        files = sorted(folder.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:40]
    except OSError:
        files = []
    for file in files:
        try:
            lines = file.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for line in lines:
            if '"token_count"' not in line:
                continue
            try:
                event = json.loads(line)
            except ValueError:
                continue
            payload = event.get("payload") or {}
            limits = payload.get("rate_limits") or {}
            primary = limits.get("primary")
            stamp = str(event.get("timestamp") or "")
            if payload.get("type") == "token_count" and isinstance(primary, dict) and stamp and (best is None or stamp > best[0]):
                best = (stamp, limits)
    if best is None:
        return {
            "n": "Codex",
            "where": machine(),
            "plan": "Codex",
            "used": None,
            "note": "No reading yet. Codex has not logged a limit.",
        }
    stamp, limits = best
    primary = limits["primary"]
    minutes = primary.get("window_minutes")
    window = "Weekly limit" if minutes == 10080 else "5-hour limit" if minutes == 300 else f"{minutes}-minute limit"
    read_at = datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp()
    return {
        "n": "Codex",
        "where": machine(),
        "plan": str(limits.get("plan_type") or "Codex").capitalize(),
        "used": round(float(primary.get("used_percent") or 0), 1),
        "window": window,
        "resets": fmt(primary.get("resets_at")),
        "read": fmt(read_at),
        "note": "Latest reading in Codex's own log.",
    }


def discover_accounts() -> list[str]:
    """Accounts with a saved reading, plus the accounts signed in to Claude profiles on this machine."""
    names: list[str] = []
    for file in sorted(usage_dir().glob("claude-*.json")) if usage_dir().is_dir() else []:
        names.append(file.stem.removeprefix("claude-"))
    home = Path.home()
    candidates = [home / ".claude.json", *sorted(home.glob(".claude-*/.claude.json"))]
    for config in candidates:
        try:
            email = json.loads(config.read_text(encoding="utf-8"))["oauthAccount"]["emailAddress"]
        except (OSError, ValueError, KeyError, TypeError):
            continue
        names.append(_safe(str(email).split("@")[0]))
    seen: list[str] = []
    for name in names:
        if name not in seen:
            seen.append(name)
    return seen


def main(argv: list[str]) -> int:
    accounts = discover_accounts()
    if "--accounts" in argv and argv.index("--accounts") + 1 < len(argv):
        accounts = [a for a in argv[argv.index("--accounts") + 1].split(",") if a]
    print(json.dumps([*claude_rows(accounts), codex_row()], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
