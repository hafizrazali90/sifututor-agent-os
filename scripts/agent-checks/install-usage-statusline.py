#!/usr/bin/env python3
"""Add the usage status line to Claude profiles, safely.

Dry run by default. It never overwrites a status line that is not ours, it backs
up settings.json before changing it, it does each real settings file once even
when two profiles share one through a symlink, and --undo removes only ours.

Usage:
  python3 scripts/agent-checks/install-usage-statusline.py [--apply] [--undo] [profile-folder ...]
With no folders it uses the Claude profiles found in the home folder.
Agreed with Hafiz on 17/10/2026.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import time

MARK = "claude_usage_statusline.py"


def default_command() -> str:
    return f'python3 "{Path(__file__).resolve().parent / MARK}"'


def worktree_problem(command: str) -> str | None:
    """A status line pointing into a temporary worktree breaks the day that worktree is cleaned up."""
    if "/worktrees/" in command:
        return "This script is inside a worktree, which is deleted when its work ends. Run the installer from the main checkout."
    return None


def default_profiles() -> list[Path]:
    home = Path.home()
    found = [home / ".claude", *sorted(home.glob(".claude-*"))]
    return [folder for folder in found if (folder / "settings.json").exists()]


def install(profiles: list[Path], apply: bool = False, undo: bool = False, command: str | None = None) -> list[tuple[Path, str]]:
    wanted = command or default_command()
    report: list[tuple[Path, str]] = []
    done: set[Path] = set()
    for profile in profiles:
        settings = Path(profile) / "settings.json"
        if not settings.exists():
            report.append((profile, "skipped: no settings.json"))
            continue
        real = settings.resolve()
        if real in done:
            report.append((profile, "same file as another profile, already handled"))
            continue
        done.add(real)
        try:
            data = json.loads(real.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            report.append((profile, "skipped: settings.json is not readable JSON"))
            continue
        if not isinstance(data, dict):
            report.append((profile, "skipped: settings.json is not an object"))
            continue
        current = data.get("statusLine")
        ours = isinstance(current, dict) and MARK in str(current.get("command", ""))
        if undo:
            if not ours:
                report.append((profile, "kept: the status line is not ours" if current else "nothing to remove"))
                continue
            del data["statusLine"]
            state = "removed"
        else:
            if current and not ours:
                report.append((profile, "skipped: a different status line is already set"))
                continue
            if ours and current.get("command") == wanted:
                report.append((profile, "already installed"))
                continue
            data["statusLine"] = {"type": "command", "command": wanted}
            state = "added"
        if not apply:
            report.append((profile, "would " + ("remove" if undo else "add")))
            continue
        shutil.copy2(real, real.with_name(f"{real.name}.bak-{time.strftime('%Y%m%d-%H%M%S')}"))
        real.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        report.append((profile, state))
    return report


def main(argv: list[str]) -> int:
    apply, undo = "--apply" in argv, "--undo" in argv
    problem = worktree_problem(default_command()) if apply else None
    if problem:
        print(problem)
        return 2
    folders = [Path(arg).expanduser() for arg in argv if not arg.startswith("--")] or default_profiles()
    if not folders:
        print("No Claude profiles found.")
        return 1
    for profile, state in install(folders, apply=apply, undo=undo):
        print(f"{profile}: {state}")
    if not apply:
        print("Dry run. Add --apply to make the change.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
