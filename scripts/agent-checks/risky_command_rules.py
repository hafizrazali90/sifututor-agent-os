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


PATCH_TOOLS = frozenset({"apply_patch", "functions.apply_patch"})
PATCH_FILE_HEADER = re.compile(r"^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+)$", re.M)
NOTE_WRITER = "deploy_ok_note"
PYTHON_EXE = re.compile(r"^python(?:\d+(?:\.\d+)*)?$")


def note_folder_reason(texts: list[str]) -> str | None:
    """Refuse a command that mentions the note folder, so an agent cannot write its own approval."""
    return NOTE_FOLDER_REASON if any(NOTE_FOLDER.search(text) for text in texts) else None


def note_writer_reason(exe: str, args: list[str], codes: list[str]) -> str | None:
    """Refuse running the note writer itself: it would turn the agent's own words into Hafiz's approval.

    Reading, committing or unit-testing the file is fine; only executing it is refused.
    """
    base = os.path.basename(exe)
    if base == f"{NOTE_WRITER}.py":
        return NOTE_FOLDER_REASON
    if not PYTHON_EXE.match(base):
        return None
    for index, token in enumerate(args):
        if os.path.basename(token) == f"{NOTE_WRITER}.py" and not (index and args[index - 1] in {"-m", "-c"}):
            return NOTE_FOLDER_REASON
        if token == "-m" and args[index + 1 : index + 2] == [NOTE_WRITER]:
            return NOTE_FOLDER_REASON
        if token == "-c" and NOTE_WRITER in "".join(args[index + 1 : index + 2]):
            return NOTE_FOLDER_REASON
    return NOTE_FOLDER_REASON if any(NOTE_WRITER in code for code in codes) else None


def _patch_text(tool_input) -> str:
    if isinstance(tool_input, dict):
        return "\n".join(value for value in tool_input.values() if isinstance(value, str))
    return tool_input if isinstance(tool_input, str) else ""


def note_folder_reason_for_tool(tool_name: str, tool_input) -> str | None:
    if tool_name in FILE_TOOLS and isinstance(tool_input, dict):
        for key in ("file_path", "notebook_path", "path"):
            value = tool_input.get(key)
            if isinstance(value, str) and NOTE_FOLDER.search(value):
                return NOTE_FOLDER_REASON
    if tool_name in PATCH_TOOLS:
        # Only the file headers count: a patch may legitimately mention the folder in its text.
        if any(NOTE_FOLDER.search(path) for path in PATCH_FILE_HEADER.findall(_patch_text(tool_input))):
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


def _git_dir(args: list[str]) -> str | None:
    for index, token in enumerate(args):
        if token == "-C" and index + 1 < len(args):
            return args[index + 1]
        if token in {"push", "pull", "fetch", "commit", "merge"}:
            break
    return None


def current_branch(directory: str | None = None) -> str | None:
    """The checked-out branch, or None when it cannot be read (detached head, no repository)."""
    command = ["git"] + (["-C", directory] if directory else []) + ["rev-parse", "--abbrev-ref", "HEAD"]
    try:
        done = subprocess.run(command, capture_output=True, text=True, timeout=5, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    branch = done.stdout.strip()
    return branch if done.returncode == 0 and branch and branch != "HEAD" else None


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


GH_API_DESTRUCTIVE_PATH = re.compile(r"(?:^|/)git/refs/|/protection(?:/|$)|^/?repos/[^/]+/[^/]+/?$")
GH_API_MERGE_PATH = re.compile(r"/pulls/\d+/merge/?$")


def _gh_api(args: list[str]) -> tuple[str, str] | None:
    """The HTTP method and path of a `gh api` call, or None when it is not one."""
    if args[:1] != ["api"]:
        return None
    method, path, index = "GET", "", 1
    value_flags = {"-f", "-F", "--field", "--raw-field", "-H", "--header", "--jq", "-q", "-t", "--template", "--input", "--hostname", "--cache"}
    while index < len(args):
        token = args[index]
        if token in {"-X", "--method"} and index + 1 < len(args):
            method, index = args[index + 1].upper(), index + 2
            continue
        if token.startswith("--method="):
            method = token.split("=", 1)[1].upper()
        elif token.startswith("-X") and len(token) > 2:
            method = token[2:].upper()
        elif token in value_flags:
            index += 2
            continue
        elif not token.startswith("-") and not path:
            path = token
        index += 1
    return method, path


def destructive_reason(exe: str, args: list[str]) -> str | None:
    if exe == "git" and _git_destructive(*_git(args)):
        return DESTRUCTIVE_REASON
    if exe == "gh":
        call = _gh_api(args)
        if call and call[0] == "DELETE" and GH_API_DESTRUCTIVE_PATH.search(call[1]):
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


PR_MERGE_VALUE_FLAGS = frozenset({"-R", "--repo", "-b", "--body", "-F", "--body-file", "-t", "--subject", "-A", "--author-email", "--match-head-commit"})


def pr_base_branch(args: list[str]) -> str | None:
    """The branch a pull request merges into, or None when it cannot be read."""
    after = args[args.index("merge") + 1 :] if "merge" in args else []
    target, index = None, 0
    while index < len(after):
        token = after[index]
        if token in PR_MERGE_VALUE_FLAGS:
            index += 2
            continue
        if not token.startswith("-"):
            target = token
            break
        index += 1
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


def _unwrap_runner(exe: str, args: list[str]) -> tuple[str, list[str]]:
    """See through npx, npm exec, yarn, pnpm and bunx to the program they start."""
    if exe in {"npx", "bunx"}:
        rest = args
    elif exe == "npm" and args[:1] in (["exec"], ["x"]):
        rest = args[1:]
    elif exe in {"yarn", "pnpm"}:
        rest = args[1:] if args[:1] in (["dlx"], ["exec"]) else args
    else:
        return exe, args
    index = 0
    while index < len(rest) and rest[index].startswith("-"):
        index += 1
    return (rest[index], rest[index + 1 :]) if index < len(rest) else (exe, args)


def _push_targets_production(args: list[str]) -> bool:
    sub, rest = _git(args)
    if sub != "push":
        return False
    refs = _positionals(rest)[1:]  # the first one is the remote
    for ref in refs:
        target = ref.lstrip("+").split(":")[-1].removeprefix("refs/heads/")
        if target in PRODUCTION_BRANCHES:
            return True
    # No branch named, or HEAD: git pushes the checked-out branch.
    if not refs or all(ref.lstrip("+").split(":")[-1] == "HEAD" for ref in refs):
        return current_branch(_git_dir(args)) in PRODUCTION_BRANCHES
    return False


def _is_production(exe: str, args: list[str]) -> bool:
    exe, args = _unwrap_runner(exe, args)
    if exe == "vercel":
        return "--prod" in args or "--production" in args or "promote" in args
    if exe == "git":
        return _push_targets_production(args)
    if exe == "gh" and args[:2] == ["pr", "merge"]:
        base = pr_base_branch(args)
        return base is None or base in PRODUCTION_BRANCHES
    if exe == "gh":
        call = _gh_api(args)
        return bool(call and call[0] == "PUT" and GH_API_MERGE_PATH.search(call[1]))
    return False


def production_reason(exe: str, args: list[str], session: str | None) -> str | None:
    if not _is_production(exe, args):
        return None
    if session and deploy_ok_note.note_active(session):
        return None
    return PRODUCTION_REASON
