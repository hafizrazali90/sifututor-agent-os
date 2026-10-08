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
- a builder may only change the paths listed in `allowed_paths`.
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
    "approval", "max_usd", "max_turns", "max_minutes", "allowed_paths",
)

DEFAULT_USD, MIN_USD, MAX_USD = 2.0, 0.5, 20.0
DEFAULT_TURNS, MIN_TURNS, MAX_TURNS = 30, 1, 100
DEFAULT_MINUTES, MIN_MINUTES, MAX_MINUTES = 30, 1, 180

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


def _number(value: str, kind: type, name: str, low: float, high: float, errors: list[str]):
    try:
        number = kind(value)
    except ValueError:
        errors.append(f"{name} must be a number, got {value!r}")
        return None
    if number < low:
        errors.append(f"{name} must be at least {low:g}"
                      + (" (below that a single turn can exceed the cap)" if name == "max_usd" else ""))
    elif number > high:
        errors.append(f"{name} must be at most {high:g} for an unattended job")
    return number


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
        if key not in ALLOWED_KEYS:
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

    defaulted: list[str] = []
    for name, kind, default, low, high in (
        ("max_usd", float, DEFAULT_USD, MIN_USD, MAX_USD),
        ("max_turns", int, DEFAULT_TURNS, MIN_TURNS, MAX_TURNS),
        ("max_minutes", int, DEFAULT_MINUTES, MIN_MINUTES, MAX_MINUTES),
    ):
        raw = fields.get(name, "")
        if raw == "":
            normal[name] = default
            defaulted.append(name)
        else:
            value = _number(raw, kind, name, low, high, errors)
            normal[name] = value if value is not None else default
    normal["caps_defaulted"] = defaulted

    issue = fields.get("issue", "")
    if issue and not issue.isdigit():
        errors.append("issue must be a number")
    normal["issue"] = issue

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
