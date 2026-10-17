#!/usr/bin/env python3
"""Destructive and production command rules for the shared command guard.

Agreed with Hafiz on 17/10/2026:
- Destructive commands are always refused, and nothing can waive them.
- Production deploy and merge into main or a production branch pass only while
  Hafiz's typed "deploy ok" note exists for this session (see deploy_ok_note.py).
- Staging, feature-branch pushes, commits and tests are not touched.

Both rules work on an already parsed command (the program and its arguments), so
text inside an echo, a commit message or a grep pattern is not mistaken for a command.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deploy_ok_note  # noqa: E402

PRODUCTION_BRANCHES = frozenset({"main", "master", "production", "prod", "release"})
SQL_CLIENTS = frozenset({"mysql", "mariadb", "psql", "sqlite3", "mysqlsh", "sqlcmd", "clickhouse-client"})
ARTISAN_WIPES = frozenset({"migrate:fresh", "migrate:reset", "migrate:refresh", "db:wipe"})
TEMP_ROOTS = ("/tmp/", "/private/tmp/", "/var/folders/", "/private/var/folders/")
GIT_VALUE_OPTIONS = frozenset({"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--super-prefix", "--config-env"})
SQL_DESTRUCTIVE = re.compile(r"\b(?:drop\s+(?:database|schema|table)|truncate(?:\s+table)?\s+\S)", re.I)

DESTRUCTIVE_REASON = (
    "This command is destructive (force push, hard reset, git clean -f, forced branch delete, "
    "dropping or wiping data, or deleting a home or system folder), so it is refused. "
    "If Hafiz really wants it, he runs it himself."
)
NOTE_FOLDER = re.compile(r"approvals/deploy-ok|AGENT_OS_APPROVAL_DIR")
NOTE_FOLDER_REASON = (
    "Only Hafiz can create a deploy ok note, by typing the phrase himself. "
    "Commands and file tools may not touch that folder."
)
FILE_TOOLS = frozenset({"Write", "Edit", "MultiEdit", "NotebookEdit"})
PRODUCTION_REASON = (
    "Production deploy and merge into main or a production branch need Hafiz's go for this session. "
    "Ask him to type deploy ok (alone, or as the last words of a message), then run it again."
)


def note_folder_reason(texts: list[str]) -> str | None:
    """Refuse a command that mentions the note folder, so an agent cannot write its own approval."""
    return NOTE_FOLDER_REASON if any(NOTE_FOLDER.search(text) for text in texts) else None


def note_folder_reason_for_tool(tool_name: str, tool_input) -> str | None:
    if tool_name in FILE_TOOLS and isinstance(tool_input, dict):
        for key in ("file_path", "notebook_path", "path"):
            value = tool_input.get(key)
            if isinstance(value, str) and NOTE_FOLDER.search(value):
                return NOTE_FOLDER_REASON
    return None


def _git(args: list[str]) -> tuple[str | None, list[str]]:
    index = 0
    while index < len(args):
        token = args[index]
        if token in GIT_VALUE_OPTIONS:
            index += 2
            continue
        if token.startswith("-"):
            index += 1
            continue
        return token, args[index + 1 :]
    return None, []


def _short(args: list[str], letters: str) -> bool:
    """A single-dash flag cluster such as -fu holds one of the letters."""
    return any(
        len(token) > 1 and token[0] == "-" and token[1] != "-" and any(letter in token[1:] for letter in letters)
        for token in args
    )


def _positionals(args: list[str]) -> list[str]:
    return [token for token in args if not token.startswith("-")]


def _dangerous_rm_target(raw: str) -> bool:
    target = raw.strip("'\"")
    if target in {"/", "/*", "~", "~/", "~/*", "$HOME", "$HOME/", "$HOME/*", "${HOME}", "${HOME}/", ".", "./", "..", "../", "*", "./*", ".git", "./.git"}:
        return True
    if target.startswith("..") or "/../" in target:
        return True
    home = os.path.expanduser("~")
    for prefix in ("~/", "$HOME/", "${HOME}/", home + "/"):
        if target.startswith(prefix):
            below = [part for part in target[len(prefix) :].split("/") if part and part != "."]
            return len(below) <= 1  # the home folder itself or one of its direct children
    if target.startswith("/"):
        return not target.startswith(TEMP_ROOTS)
    return False


def _git_destructive(sub: str | None, rest: list[str]) -> bool:
    if sub == "push":
        if any(token in {"--force", "--mirror", "--delete"} or token.startswith("--force-with-lease") for token in rest):
            return True
        if _short(rest, "fd"):
            return True
        return any(token.startswith(("+", ":")) for token in _positionals(rest))
    if sub == "reset":
        return "--hard" in rest
    if sub == "clean":
        force = "--force" in rest or _short(rest, "f")
        dry = "--dry-run" in rest or _short(rest, "n")
        return force and not dry
    if sub == "branch":
        if _short(rest, "D"):
            return True
        return ("--delete" in rest or _short(rest, "d")) and ("--force" in rest or _short(rest, "f"))
    return False


def destructive_reason(exe: str, args: list[str]) -> str | None:
    if exe == "git" and _git_destructive(*_git(args)):
        return DESTRUCTIVE_REASON
    if exe in SQL_CLIENTS and SQL_DESTRUCTIVE.search(" ".join(args)):
        return DESTRUCTIVE_REASON
    if exe in {"php", "artisan"} or exe.endswith("/artisan"):
        if any(token in ARTISAN_WIPES for token in args):
            return DESTRUCTIVE_REASON
    if exe == "rm":
        recursive = any(token in {"--recursive"} for token in args) or _short(args, "rR")
        if recursive:
            after_dashes = False
            for token in args:
                if token == "--":
                    after_dashes = True
                    continue
                if (after_dashes or not token.startswith("-")) and _dangerous_rm_target(token):
                    return DESTRUCTIVE_REASON
    return None


def pr_base_branch(args: list[str]) -> str | None:
    """The branch a pull request merges into, or None when it cannot be read."""
    after = args[args.index("merge") + 1 :] if "merge" in args else []
    target = next((token for token in after if not token.startswith("-")), None)
    command = ["gh", "pr", "view"]
    if target:
        command.append(target)
    for flag in ("-R", "--repo"):
        if flag in args and args.index(flag) + 1 < len(args):
            command += [flag, args[args.index(flag) + 1]]
    command += ["--json", "baseRefName", "--jq", ".baseRefName"]
    try:
        done = subprocess.run(command, capture_output=True, text=True, timeout=8, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    base = done.stdout.strip()
    return base if done.returncode == 0 and base else None


def _is_production(exe: str, args: list[str]) -> bool:
    vercel_args: list[str] | None = None
    if exe == "vercel":
        vercel_args = args
    elif exe in {"npx", "bunx"} and args[:1] == ["vercel"]:
        vercel_args = args[1:]
    elif exe == "pnpm" and args[:2] == ["dlx", "vercel"]:
        vercel_args = args[2:]
    if vercel_args is not None:
        return "--prod" in vercel_args or "--production" in vercel_args or "promote" in vercel_args
    if exe == "git":
        sub, rest = _git(args)
        if sub == "push":
            for ref in _positionals(rest)[1:]:  # the first one is the remote
                target = ref.lstrip("+").split(":")[-1]
                if target.removeprefix("refs/heads/") in PRODUCTION_BRANCHES:
                    return True
        return False
    if exe == "gh" and args[:2] == ["pr", "merge"]:
        base = pr_base_branch(args)
        return base is None or base in PRODUCTION_BRANCHES
    return False


def production_reason(exe: str, args: list[str], session: str | None) -> str | None:
    if not _is_production(exe, args):
        return None
    if session and deploy_ok_note.note_active(session):
        return None
    return PRODUCTION_REASON
