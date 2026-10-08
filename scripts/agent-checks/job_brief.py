"""Parse and validate the brief for an unattended job on the home PC.

A brief is a small Markdown file: a front-matter block of `key: value` lines
between two `---` markers, then the instructions for the job. This module has
no dependencies so it can run on the Mac, on the PC and in tests.

Rules enforced here (issues #272, #273, #274):
- every job has a spend cap, a turn cap and a time limit, with safe defaults
  and hard upper limits;
- every job has a finish state; a missing one means `local`;
- an unattended job can never merge or deploy;
- a job that pushes a branch and opens a pull request needs a recorded approval;
- a builder may only change the paths listed in `allowed_paths`;
- a job may name a project repo (issue #347), only from `PROJECT_REPOS`.
"""

from __future__ import annotations

import re
from typing import Any

BUILDER = "builder"
REVIEWER = "reviewer"
ROLES = (BUILDER, REVIEWER)

FINISH_STATES = ("local", "committed", "pr-open")
REFUSED_FINISH_STATES = ("merged", "deployed")

ALLOWED_KEYS = (
    "title", "role", "base", "branch", "target", "finish", "issue",
    "approval", "allowed_paths", "repo",
)

# Jobs run on Hafiz's Claude subscription exactly as a session on the Mac does,
# so there is no spend, turn or time cap (Hafiz, 09/10/2026: "never cap"). A
# brief that still carries a cap line is refused so the line gets deleted.
REMOVED_CAP_KEYS = ("max_usd", "max_turns", "max_minutes")

# Project repos a job may work in, as folder names under the umbrella checkout
# on the PC. Missing `repo` means the umbrella (Agent OS) repo itself.
PROJECT_REPOS = ("ripple-suite",)

BRANCH_TYPES = ("feat", "feature", "fix", "refactor", "hotfix", "chore", "docs", "perf", "test", "ci")
BRANCH_RE = re.compile(r"^(%s)/[a-z0-9][a-z0-9-]*$" % "|".join(BRANCH_TYPES))
TARGET_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
COMMENT_RE = re.compile(r"\s+#\s.*$")


class BriefError(ValueError):
    """The brief cannot be read at all."""


def parse(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise BriefError("brief must start with a --- front-matter block")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        raise BriefError("front-matter block is not closed with ---") from None
    fields: dict[str, str] = {}
    for raw in lines[1:end]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if ":" not in raw:
            raise BriefError(f"front-matter line has no colon: {raw!r}")
        key, value = raw.split(":", 1)
        fields[key.strip()] = COMMENT_RE.sub("", value).strip()
    return {"fields": fields, "body": "\n".join(lines[end + 1:]).strip()}


def _paths(value: str, errors: list[str]) -> list[str]:
    paths = [p.strip() for p in value.split(",") if p.strip()]
    if not paths:
        errors.append("allowed_paths is required for a builder: list the files or folders it may change")
    for path in paths:
        if path in {".", "/", "*", "**"} or path.startswith("/") or ".." in path.split("/"):
            errors.append(f"allowed_paths entry {path!r} is too broad or leaves the repo")
    return paths


def validate(parsed: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    """Return (errors, normalised brief). The brief is usable only if errors is empty."""
    fields: dict[str, str] = parsed["fields"]
    errors: list[str] = []
    normal: dict[str, Any] = {"body": parsed["body"]}

    for key in fields:
        if key in REMOVED_CAP_KEYS:
            errors.append(f"{key} was removed: jobs have no caps (Hafiz, 09/10/2026), so delete this line")
        elif key not in ALLOWED_KEYS:
            errors.append(f"unknown key {key!r}")

    title = fields.get("title", "")
    if not title:
        errors.append("title is required")
    elif len(title) > 80:
        errors.append("title must be 80 characters or fewer")
    normal["title"] = title

    role = fields.get("role", "")
    if role not in ROLES:
        errors.append(f"role must be one of {', '.join(ROLES)}")
    normal["role"] = role

    finish = fields.get("finish", "")
    normal["finish_defaulted"] = finish == ""
    if finish == "":
        finish = "local"
    if finish in REFUSED_FINISH_STATES:
        errors.append(f"finish {finish!r} is refused: an unattended job cannot merge or deploy")
    elif finish not in FINISH_STATES:
        errors.append(f"finish must be one of {', '.join(FINISH_STATES)}")
    normal["finish"] = finish
    approval = fields.get("approval", "")
    if finish == "pr-open" and not approval:
        errors.append("finish pr-open needs an approval line: who approved pushing, and when")
    normal["approval"] = approval
    if role == REVIEWER and finish != "local":
        errors.append("a reviewer is read-only, so its finish must be local")

    issue = fields.get("issue", "")
    if issue and not issue.isdigit():
        errors.append("issue must be a number")
    normal["issue"] = issue

    repo = fields.get("repo", "")
    if repo and repo not in PROJECT_REPOS:
        errors.append(f"repo must be one of {', '.join(PROJECT_REPOS)}, or left out for the Agent OS repo")
    normal["repo"] = repo

    normal["base"] = fields.get("base", "origin/main")
    if not normal["base"].startswith("origin/"):
        errors.append("base must start with origin/")

    if role == BUILDER:
        branch = fields.get("branch", "")
        if not BRANCH_RE.match(branch):
            errors.append("branch must look like type/lowercase-kebab-description, for example docs/277-writing-rules")
        normal["branch"] = branch
        normal["allowed_paths"] = _paths(fields.get("allowed_paths", ""), errors)
        normal["target"] = ""
    elif role == REVIEWER:
        target = fields.get("target", "")
        if not target or not TARGET_RE.match(target):
            errors.append("target is required for a reviewer: the branch on origin to review")
        normal["target"] = target
        normal["branch"] = ""
        normal["allowed_paths"] = []

    if len(parsed["body"]) < 10:
        errors.append("the brief body is empty: write what the job must do")
    return errors, normal
