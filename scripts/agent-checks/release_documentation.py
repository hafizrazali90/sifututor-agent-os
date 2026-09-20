#!/usr/bin/env python3
"""Shared, model-agnostic staff documentation release enforcement (issue 112).

Issue 112 asked for the half that was only ever written down in prose: the
playbooks already said a worthy staff-facing SIMS/Ripple change should ship with
its changelog entry, staff guide, in-app help, What's New entry, or audience
message, but nothing checked it. A rule nobody can run is a rule that quietly
stops happening on the day it matters most - the urgent release.

This module is the single enforcement entrypoint for that rule. It owns the
ledger parser, the project-awareness, the three decisions, and the two gate
modes. Playbooks point here instead of re-stating the rule, and there is no
Claude-only or Codex-only copy of "does this release need a staff guide?".

What it proves, and what it does not:

- It proves the change recorded ONE explicit relevance decision, that a
  `relevant` decision actually shipped its named artifacts in the same bundle,
  and that an `urgent deferral` named a real human and a real follow-up issue.
- It does NOT judge whether a guide is well written, whether the audience is
  right, or whether the follow-up issue is open. It never reads the network,
  never infers an audience or a report source the change did not establish, and
  never invents a required artifact the project did not declare.

Two modes, same rules:

    advisory  report and explain, always exit 0. The shared pre-commit guard.
    blocking  the same findings, exit 1. Pre-push / release / CI.

Scope is always the active change bundle. An entry recorded for an older
release is never re-evaluated, so this can never turn into "go back and
document a feature from six months ago before you may ship today's fix".

Stdlib only, read-only, no network, no framework assumptions.
"""

from __future__ import annotations

import argparse
import fnmatch
import importlib.util
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


# ──────────────────────────────────────────────────────────────────────────────
# Shared helpers
#
# The markdown table parser, the project-relative path safety rules, and the git
# scope helpers already exist in coverage_enforcement.py (issue 2 / CP-11).
# Importing them keeps one parser in the Agent OS instead of a second copy that
# drifts.
# ──────────────────────────────────────────────────────────────────────────────


def _load_shared() -> object:
    module_path = Path(__file__).with_name("coverage_enforcement.py")
    existing = sys.modules.get("coverage_enforcement")
    if existing is not None and getattr(existing, "__file__", None) == str(module_path):
        return existing
    if not module_path.is_file():
        raise SystemExit(
            "release_documentation: coverage_enforcement.py is missing next to this "
            "script; the shared markdown table parser lives there"
        )
    spec = importlib.util.spec_from_file_location("coverage_enforcement", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_SHARED = _load_shared()

normalize_text = _SHARED.normalize_text
split_row = _SHARED.split_row
is_separator = _SHARED.is_separator
is_safe_project_relative = _SHARED.is_safe_project_relative
within = _SHARED.within
read_text_safely = _SHARED.read_text_safely
path_matches_change = _SHARED.path_matches_change
git = _SHARED.git
staged_changed_files = _SHARED.staged_changed_files
base_changed_files = _SHARED.base_changed_files


# ──────────────────────────────────────────────────────────────────────────────
# Vocabulary
# ──────────────────────────────────────────────────────────────────────────────

LEDGER_NAME = "RELEASE-DOCS.md"
CONFIG_NAME = ".agent-os/release-docs.json"

MODE_ADVISORY = "advisory"
MODE_BLOCKING = "blocking"
MODES = (MODE_ADVISORY, MODE_BLOCKING)

STATE_OK = "ok"
STATE_UNAVAILABLE = "unavailable"

RELEVANT = "relevant"
NOT_RELEVANT = "not-relevant"
URGENT_DEFERRAL = "urgent-deferral"
UNREADABLE = "unreadable"

CODE_CONFIG_UNAVAILABLE = "RD001_CONFIG_UNAVAILABLE"
CODE_CONFIG_UNREADABLE = "RD002_CONFIG_UNREADABLE"
CODE_SCOPE_UNAVAILABLE = "RD003_SCOPE_UNAVAILABLE"
CODE_LEDGER_MISSING = "RD004_LEDGER_MISSING"
CODE_LEDGER_UNPARSEABLE = "RD005_LEDGER_UNPARSEABLE"
CODE_DECISION_MISSING = "RD006_DECISION_MISSING"
CODE_DECISION_UNREADABLE = "RD007_DECISION_UNREADABLE"
CODE_ENTRY_REMOVED = "RD008_ENTRY_REMOVED"
CODE_ARTIFACT_NOT_DECLARED = "RD009_ARTIFACT_NOT_DECLARED"
CODE_ARTIFACT_ABSENT = "RD010_ARTIFACT_ABSENT"
CODE_ARTIFACT_NOT_IN_BUNDLE = "RD011_ARTIFACT_NOT_IN_BUNDLE"
CODE_ARTIFACT_IS_LEDGER = "RD012_ARTIFACT_IS_LEDGER"
CODE_ARTIFACT_UNSAFE_PATH = "RD013_ARTIFACT_UNSAFE_PATH"
CODE_REQUIRED_ARTIFACT_MISSING = "RD014_REQUIRED_ARTIFACT_MISSING"
CODE_REASON_MISSING = "RD015_REASON_MISSING"
CODE_OWNER_MISSING = "RD016_OWNER_MISSING"
CODE_FOLLOW_UP_MISSING = "RD017_FOLLOW_UP_MISSING"
CODE_FOLLOW_UP_SELF_REFERENCE = "RD018_FOLLOW_UP_SELF_REFERENCE"


# A cell that says nothing. These are the words a hurried release reaches for,
# which is exactly why they have to be rejected rather than accepted as a value.
PLACEHOLDERS = frozenset(
    {
        "",
        "-",
        "--",
        "---",
        "n/a",
        "na",
        "n.a.",
        "none",
        "nil",
        "tbd",
        "tba",
        "to be decided",
        "to be confirmed",
        "todo",
        "to do",
        "later",
        "follow up later",
        "follow-up later",
        "soon",
        "eventually",
        "next sprint",
        "next release",
        "pending",
        "unknown",
        "?",
        "??",
        "...",
        "x",
        "tbc",
    }
)

# An owner has to be a person who can be asked. A role, a queue, or the agent
# that wrote the deferral is not an owner.
NON_OWNERS = frozenset(
    {
        "team",
        "the team",
        "dev",
        "devs",
        "dev team",
        "engineering",
        "someone",
        "anyone",
        "somebody",
        "nobody",
        "unassigned",
        "owner",
        "staff",
        "support",
        "ops",
        "agent",
        "ai",
        "bot",
        "claude",
        "codex",
        "kilo",
        "chatgpt",
        "copilot",
        "assistant",
        "me",
        "us",
        "we",
    }
)

ISSUE_PATTERNS = (
    re.compile(r"^#(?P<number>\d+)$"),
    re.compile(r"^(?:gh-)(?P<number>\d+)$", re.IGNORECASE),
    re.compile(r"^[\w.-]+/[\w.-]+#(?P<number>\d+)$"),
    re.compile(
        r"^https?://github\.com/[\w.-]+/[\w.-]+/issues/(?P<number>\d+)/?$",
        re.IGNORECASE,
    ),
)

ISSUE_IN_TEXT = re.compile(r"(?:^|\s)(?:[\w.-]+/[\w.-]+)?#(\d+)\b")


DECISION_WORDS = (
    # Ordered most specific first: "not relevant" must never read as "relevant".
    (URGENT_DEFERRAL, ("urgent deferral", "urgent-deferral", "urgent defer", "deferred", "defer")),
    (NOT_RELEVANT, ("not relevant", "not-relevant", "not applicable", "no docs needed", "no documentation needed")),
    (RELEVANT, ("relevant", "documented", "docs shipped", "required")),
)


# ──────────────────────────────────────────────────────────────────────────────
# Project awareness
#
# Projects do not share paths. sifu-tutor is Laravel with staff guides under
# docs/; ripple-suite is Next.js with per-module help.ts. The engine therefore
# never hardcodes one product's layout: a project states its own shape in
# .agent-os/release-docs.json, and when it has not, a convention is detected
# from what the repository actually contains.
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ArtifactKind:
    name: str
    patterns: tuple[str, ...]
    required: bool
    meaning: str


@dataclass(frozen=True)
class ProjectConfig:
    source: str
    ledger: str
    staff_facing: tuple[str, ...]
    not_staff_facing: tuple[str, ...]
    artifacts: tuple[ArtifactKind, ...]

    @property
    def required_kinds(self) -> tuple[ArtifactKind, ...]:
        return tuple(kind for kind in self.artifacts if kind.required)


DEFAULT_NOT_STAFF_FACING = (
    "tests/**",
    "test/**",
    "**/tests/**",
    "**/test/**",
    "**/__tests__/**",
    "**/*.test.*",
    "**/*.spec.*",
    "**/fixtures/**",
    "**/node_modules/**",
    "**/vendor/**",
    "docs/**",
    ".github/**",
    ".agent-os/**",
    ".agents/**",
    ".claude/**",
    ".codex/**",
    ".kilo/**",
    "*.md",
    "*.lock",
    "*.json",
    "**/*.lock",
    "**/*.snap",
)


CONVENTIONS: tuple[tuple[str, tuple[str, ...], tuple[str, ...], tuple[ArtifactKind, ...]], ...] = (
    (
        # ripple-suite shape: Next.js app with per-module staff help content.
        "next-modules",
        ("src/modules/*/lib/help.ts",),
        ("src/modules/**", "src/app/**", "src/components/**", "app/**"),
        (
            ArtifactKind(
                "release note",
                (
                    "CHANGELOG.md",
                    "docs/CHANGELOG.md",
                    "docs/changelogs/release-notes-*.md",
                ),
                True,
                "the plain-English release note staff and Hafiz read to see what changed",
            ),
            ArtifactKind(
                "module help",
                ("src/modules/*/lib/help.ts", "src/modules/*/lib/help.tsx"),
                False,
                "the in-page guidance staff see inside the changed module",
            ),
            ArtifactKind(
                "what's new",
                (
                    "**/whats-new/**",
                    "**/what-s-new/**",
                    "scripts/*whats-new*",
                    "scripts/seed-releases-*.ts",
                    "**/release-notes/**",
                ),
                False,
                "the in-app release entry that tells staff a change landed",
            ),
        ),
    ),
    (
        # sifu-tutor shape: Laravel SIMS with staff guides kept as documents.
        "laravel",
        ("artisan",),
        ("app/**", "resources/views/**", "resources/js/**", "routes/**"),
        (
            ArtifactKind(
                "release note",
                (
                    "CHANGELOG.md",
                    "docs/CHANGELOG.md",
                    "docs/changelogs/release-notes-*.md",
                ),
                True,
                "the plain-English release note staff and Hafiz read to see what changed",
            ),
            ArtifactKind(
                "staff guide",
                ("docs/staff-guides/**", "docs/guides/**", "resources/docs/**"),
                False,
                "the guide a staff member opens to learn the changed workflow",
            ),
            ArtifactKind(
                "what's new",
                (
                    "database/seeders/*WhatsNew*",
                    "database/seeders/*ReleaseNote*",
                    "**/release-notes/**",
                ),
                False,
                "the in-app release entry that tells staff a change landed",
            ),
        ),
    ),
    (
        # Anything else that still keeps a changelog.
        "generic-changelog",
        ("CHANGELOG.md",),
        ("src/**", "app/**", "lib/**", "resources/**"),
        (
            ArtifactKind(
                "changelog",
                ("CHANGELOG.md", "docs/CHANGELOG.md"),
                True,
                "the plain-English entry staff and Hafiz read to see what changed",
            ),
        ),
    ),
)


def glob_match(path: str, pattern: str) -> bool:
    """Match a repo-relative path against a config glob.

    `fnmatch` has no separate `**`, so `**/tests/**` alone would miss a
    top-level `tests/`. The extra attempts below make the obvious human-written
    patterns behave the way the person writing them expected.
    """
    path = (path or "").strip().replace("\\", "/").lstrip("./")
    pattern = (pattern or "").strip().replace("\\", "/").lstrip("./")
    if not path or not pattern:
        return False
    if fnmatch.fnmatch(path, pattern):
        return True
    if pattern.startswith("**/") and fnmatch.fnmatch(path, pattern[3:]):
        return True
    if pattern.endswith("/**") and fnmatch.fnmatch(path, pattern[:-3]):
        return True
    if "/**/" in pattern and fnmatch.fnmatch(path, pattern.replace("/**/", "/")):
        return True
    if not any(char in pattern for char in "*?[") and fnmatch.fnmatch(path, pattern.rstrip("/") + "/*"):
        return True
    return False


def matches_any(path: str, patterns: tuple[str, ...]) -> bool:
    return any(glob_match(path, pattern) for pattern in patterns)


def project_contains(project: Path, patterns: tuple[str, ...]) -> bool:
    for pattern in patterns:
        try:
            if next(project.glob(pattern), None) is not None:
                return True
        except (OSError, ValueError, IndexError, NotImplementedError):
            continue
    return False


def parse_config(project: Path, raw: dict, source: str) -> tuple[ProjectConfig | None, str | None]:
    """Turn a project's release-docs.json into a config, or explain the refusal."""
    if not isinstance(raw, dict):
        return None, f"{source} must contain a JSON object"

    ledger = raw.get("ledger", LEDGER_NAME)
    if not isinstance(ledger, str) or not ledger.strip():
        return None, f"{source} has an empty or non-text 'ledger' value"
    if not is_safe_project_relative(ledger.strip()):
        return None, f"{source} points 'ledger' outside the project"

    def string_list(value, key) -> tuple[tuple[str, ...] | None, str | None]:
        if value is None:
            return None, None
        if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
            return None, f"{source} needs '{key}' to be a list of non-empty path patterns"
        return tuple(item.strip() for item in value), None

    staff_facing, error = string_list(raw.get("staff_facing"), "staff_facing")
    if error:
        return None, error
    not_staff_facing, error = string_list(raw.get("not_staff_facing"), "not_staff_facing")
    if error:
        return None, error

    artifacts_raw = raw.get("artifacts")
    artifacts: list[ArtifactKind] = []
    if artifacts_raw is not None:
        if not isinstance(artifacts_raw, dict) or not artifacts_raw:
            return None, f"{source} needs 'artifacts' to be a non-empty object of artifact kinds"
        for name, spec in artifacts_raw.items():
            if not isinstance(spec, dict):
                return None, f"{source} artifact '{name}' must be an object"
            patterns, error = string_list(spec.get("paths"), f"artifacts.{name}.paths")
            if error:
                return None, error
            if not patterns:
                return None, f"{source} artifact '{name}' must list at least one path pattern"
            required = spec.get("required", False)
            if not isinstance(required, bool):
                return None, f"{source} artifact '{name}' needs 'required' to be true or false"
            meaning = spec.get("meaning", "")
            if not isinstance(meaning, str):
                return None, f"{source} artifact '{name}' needs 'meaning' to be text"
            artifacts.append(ArtifactKind(str(name), patterns, required, meaning.strip()))

    if staff_facing is None and not artifacts:
        return None, f"{source} declares neither 'staff_facing' paths nor 'artifacts'"

    return (
        ProjectConfig(
            source=source,
            ledger=ledger.strip(),
            staff_facing=staff_facing or (),
            not_staff_facing=not_staff_facing if not_staff_facing is not None else DEFAULT_NOT_STAFF_FACING,
            artifacts=tuple(artifacts),
        ),
        None,
    )


def resolve_config(project: Path) -> tuple[ProjectConfig | None, str | None]:
    """Find the project's configuration, or detect its convention.

    Returns (config, problem). A `None` config with a `None` problem means the
    repository has no recognisable staff-documentation shape at all - reported
    as unavailable, never as passed.
    """
    config_path = project / CONFIG_NAME
    if config_path.is_file():
        try:
            raw = json.loads(read_text_safely(config_path))
        except json.JSONDecodeError as error:
            return None, f"{CONFIG_NAME} is not valid JSON ({error.msg} on line {error.lineno})"
        return parse_config(project, raw, CONFIG_NAME)

    for name, markers, staff_facing, artifacts in CONVENTIONS:
        if project_contains(project, markers):
            return (
                ProjectConfig(
                    source=f"convention:{name}",
                    ledger=LEDGER_NAME,
                    staff_facing=staff_facing,
                    not_staff_facing=DEFAULT_NOT_STAFF_FACING,
                    artifacts=artifacts,
                ),
                None,
            )

    return None, None


def is_staff_facing(path: str, config: ProjectConfig) -> bool:
    """A change is staff-facing only when the project says that path is.

    The presence of a CHANGELOG.md in a repository is never the trigger. A
    build script, a dependency bump, or a test-only change must stay shippable
    without a staff guide.
    """
    if matches_any(path, config.not_staff_facing):
        return False
    return matches_any(path, config.staff_facing)


# ──────────────────────────────────────────────────────────────────────────────
# Ledger parsing
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class Entry:
    change: str
    decision: str
    line_number: int
    raw: str
    decision_cell: str = ""
    artifacts_cell: str = ""
    owner_cell: str = ""
    follow_up_cell: str = ""
    reason_cell: str = ""

    @property
    def key(self) -> str:
        return normalize_text(self.change)

    @property
    def fingerprint(self) -> str:
        return normalize_text(self.raw)


def pick_column(header: list[str], require: tuple[str, ...], reject: tuple[str, ...] = ()) -> int | None:
    for wanted in require:
        for index, cell in enumerate(header):
            if wanted in cell and not any(bad in cell for bad in reject):
                return index
    return None


def cell(cells: list[str], index: int | None) -> str:
    if index is None or index >= len(cells):
        return ""
    return cells[index].strip()


def classify_decision(value: str) -> str:
    text = normalize_text(value)
    if not text or text in PLACEHOLDERS:
        return UNREADABLE
    for decision, words in DECISION_WORDS:
        if any(word in text for word in words):
            return decision
    return UNREADABLE


def parse_ledger_tables(text: str) -> tuple[list[Entry], bool]:
    """Parse a ledger file into decisions, and say whether a table was found.

    The two answers are different problems. "There is no decision table here"
    needs a different sentence from "the table is there and this change has not
    added its row yet", and a checker that confuses them teaches the wrong fix.
    """
    entries: list[Entry] = []
    columns: dict[str, int | None] = {}
    in_table = False
    saw_table = False

    for line_number, line in enumerate((text or "").splitlines(), start=1):
        stripped = line.strip()
        if not stripped.startswith("|"):
            in_table = False
            columns = {}
            continue

        cells = split_row(stripped)
        if not cells:
            continue
        if is_separator(cells):
            continue

        lowered = [normalize_text(item) for item in cells]
        change_index = pick_column(lowered, ("change", "release item", "item", "bundle"), reject=("decision",))
        decision_index = pick_column(lowered, ("decision", "relevance"))

        if change_index is not None and decision_index is not None and not in_table:
            in_table = True
            saw_table = True
            columns = {
                "change": change_index,
                "decision": decision_index,
                "artifacts": pick_column(lowered, ("artifact", "documentation", "docs", "release doc")),
                "owner": pick_column(lowered, ("owner", "accountable", "deferral owner")),
                "follow_up": pick_column(
                    lowered, ("follow-up", "follow up", "followup", "follow", "issue", "ticket")
                ),
                "reason": pick_column(lowered, ("reason", "why", "note")),
            }
            continue

        if not in_table:
            continue

        change = cell(cells, columns["change"])
        if not change or normalize_text(change) in PLACEHOLDERS:
            continue

        decision_cell = cell(cells, columns["decision"])
        entries.append(
            Entry(
                change=change,
                decision=classify_decision(decision_cell),
                line_number=line_number,
                raw=stripped,
                decision_cell=decision_cell,
                artifacts_cell=cell(cells, columns["artifacts"]),
                owner_cell=cell(cells, columns["owner"]),
                follow_up_cell=cell(cells, columns["follow_up"]),
                reason_cell=cell(cells, columns["reason"]),
            )
        )

    return entries, saw_table


def parse_ledger(text: str) -> list[Entry]:
    return parse_ledger_tables(text)[0]


# ──────────────────────────────────────────────────────────────────────────────
# Cell readers
# ──────────────────────────────────────────────────────────────────────────────


def is_placeholder(value: str) -> bool:
    return normalize_text(value) in PLACEHOLDERS


def declared_paths(value: str) -> list[str]:
    """Pull artifact paths out of a cell.

    Backticked values win when present. Otherwise the cell is split on the
    separators humans actually use, and a token only counts when it looks like
    a path rather than prose.
    """
    if is_placeholder(value):
        return []

    quoted = re.findall(r"`([^`]+)`", value or "")
    candidates = quoted if quoted else re.split(r",|;|<br\s*/?>|\n|\s+", value or "")

    paths: list[str] = []
    for raw in candidates:
        token = raw.strip().strip("*_ ").strip("`").rstrip(".,;")
        if not token or is_placeholder(token):
            continue
        if not quoted and "/" not in token and "." not in token:
            continue
        if not quoted and token.endswith((".", ":")):
            continue
        if token.startswith(("http://", "https://")):
            continue
        if token not in paths:
            paths.append(token)
    return paths


def is_concrete_owner(value: str) -> bool:
    text = normalize_text(value)
    if not text or text in PLACEHOLDERS or text in NON_OWNERS:
        return False
    bare = text.lstrip("@")
    if bare in NON_OWNERS or bare in PLACEHOLDERS:
        return False
    if len(bare) < 2 or not re.search(r"[a-z]", bare):
        return False
    return True


def issue_reference(value: str) -> str | None:
    """Return the canonical issue number when the cell names a real GitHub issue."""
    text = (value or "").strip().strip("`").rstrip(".,;")
    if not text or is_placeholder(text):
        return None
    for pattern in ISSUE_PATTERNS:
        match = pattern.match(text)
        if match:
            number = match.group("number")
            return None if number == "0" else number
    return None


def change_issue_numbers(value: str) -> set[str]:
    return {match for match in ISSUE_IN_TEXT.findall(value or "")}


# ──────────────────────────────────────────────────────────────────────────────
# Findings and report
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class Finding:
    code: str
    change: str
    line_number: int
    detail: str

    def as_dict(self) -> dict:
        return {
            "code": self.code,
            "change": self.change,
            "line": self.line_number,
            "detail": self.detail,
        }


@dataclass
class Report:
    mode: str
    state: str
    ledger_path: str | None
    config_source: str | None
    entries_total: int
    entries_in_scope: int
    staff_facing_changes: list[str]
    findings: list[Finding]
    notes: list[str]
    summary_counts: dict[str, int] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.findings

    @property
    def blocking(self) -> bool:
        return self.mode == MODE_BLOCKING and not self.ok

    def as_dict(self) -> dict:
        return {
            "mode": self.mode,
            "state": self.state,
            "ok": self.ok,
            "ledger": self.ledger_path,
            "config_source": self.config_source,
            "entries_total": self.entries_total,
            "entries_in_scope": self.entries_in_scope,
            "staff_facing_changes": list(self.staff_facing_changes),
            "summary_counts": dict(self.summary_counts),
            "notes": list(self.notes),
            "findings": [finding.as_dict() for finding in self.findings],
        }


# ──────────────────────────────────────────────────────────────────────────────
# Scoping - which decisions this change is answerable for
# ──────────────────────────────────────────────────────────────────────────────


def entries_in_scope(current: list[Entry], previous: list[Entry] | None) -> list[Entry]:
    """Only decisions this change added or edited.

    A decision recorded for an earlier release is settled. Re-opening it here
    would turn every commit into an audit of the project's entire history,
    which is exactly the failure mode issue 112 asked to avoid.
    """
    if previous is None:
        return []
    known = {entry.key: entry.fingerprint for entry in previous}
    return [entry for entry in current if known.get(entry.key) != entry.fingerprint]


def removed_entries(current: list[Entry], previous: list[Entry] | None) -> list[Entry]:
    if previous is None:
        return []
    present = {entry.key for entry in current}
    return [entry for entry in previous if entry.key not in present]


# ──────────────────────────────────────────────────────────────────────────────
# Rules
# ──────────────────────────────────────────────────────────────────────────────


def evaluate_artifacts(
    project: Path,
    config: ProjectConfig,
    entry: Entry,
    changed_files: list[str],
) -> list[Finding]:
    findings: list[Finding] = []
    paths = declared_paths(entry.artifacts_cell)

    if not paths:
        findings.append(
            Finding(
                CODE_ARTIFACT_NOT_DECLARED,
                entry.change,
                entry.line_number,
                "this change was decided relevant, so it must name the staff documentation "
                "it ships; the Artifacts cell names no file",
            )
        )
        return findings

    ledger_names = {config.ledger, Path(config.ledger).name}
    for declared in paths:
        if declared in ledger_names or Path(declared).name == Path(config.ledger).name:
            findings.append(
                Finding(
                    CODE_ARTIFACT_IS_LEDGER,
                    entry.change,
                    entry.line_number,
                    f"'{declared}' is the decision ledger itself; recording the decision is not "
                    "the same as writing the staff documentation",
                )
            )
            continue

        if not is_safe_project_relative(declared):
            findings.append(
                Finding(
                    CODE_ARTIFACT_UNSAFE_PATH,
                    entry.change,
                    entry.line_number,
                    f"'{declared}' is not a readable path inside this project, so it cannot be "
                    "checked as part of this release",
                )
            )
            continue

        if any(char in declared for char in "*?["):
            matches = [match for match in project.glob(declared) if within(project, match)]
            exists = bool(matches)
        else:
            candidate = project / declared
            exists = within(project, candidate) and candidate.exists()

        if not exists:
            findings.append(
                Finding(
                    CODE_ARTIFACT_ABSENT,
                    entry.change,
                    entry.line_number,
                    f"'{declared}' does not exist in this project; the decision names staff "
                    "documentation that was never written",
                )
            )
            continue

        if not any(path_matches_change(declared, changed) for changed in changed_files):
            findings.append(
                Finding(
                    CODE_ARTIFACT_NOT_IN_BUNDLE,
                    entry.change,
                    entry.line_number,
                    f"'{declared}' exists but is not part of this change, so it is documentation "
                    "from an earlier release being counted twice",
                )
            )

    satisfied = {
        kind.name
        for kind in config.artifacts
        if any(matches_any(declared, kind.patterns) for declared in paths)
    }
    for kind in config.required_kinds:
        if kind.name not in satisfied:
            where = ", ".join(kind.patterns)
            meaning = f" ({kind.meaning})" if kind.meaning else ""
            findings.append(
                Finding(
                    CODE_REQUIRED_ARTIFACT_MISSING,
                    entry.change,
                    entry.line_number,
                    f"this project always requires the {kind.name}{meaning} for a relevant "
                    f"staff-facing change; nothing in the Artifacts cell matches {where}",
                )
            )

    return findings


def evaluate_entry(
    project: Path,
    config: ProjectConfig,
    entry: Entry,
    changed_files: list[str],
) -> list[Finding]:
    if entry.decision == UNREADABLE:
        shown = entry.decision_cell.strip() or "(empty)"
        return [
            Finding(
                CODE_DECISION_UNREADABLE,
                entry.change,
                entry.line_number,
                f"'{shown}' is not one of the three decisions; write 'relevant', "
                "'not relevant', or 'urgent deferral' so the release records what was chosen",
            )
        ]

    if entry.decision == RELEVANT:
        return evaluate_artifacts(project, config, entry, changed_files)

    if entry.decision == NOT_RELEVANT:
        if is_placeholder(entry.reason_cell) or not entry.reason_cell.strip():
            return [
                Finding(
                    CODE_REASON_MISSING,
                    entry.change,
                    entry.line_number,
                    "deciding staff documentation is not relevant needs a concrete reason a "
                    "reviewer can disagree with; the Reason cell says nothing",
                )
            ]
        return []

    # urgent deferral
    findings: list[Finding] = []
    if not is_concrete_owner(entry.owner_cell):
        shown = entry.owner_cell.strip() or "(empty)"
        findings.append(
            Finding(
                CODE_OWNER_MISSING,
                entry.change,
                entry.line_number,
                f"an urgent deferral needs a named person who will write the documentation; "
                f"'{shown}' is not a person anyone can ask",
            )
        )

    follow_up = issue_reference(entry.follow_up_cell)
    if follow_up is None:
        shown = entry.follow_up_cell.strip() or "(empty)"
        findings.append(
            Finding(
                CODE_FOLLOW_UP_MISSING,
                entry.change,
                entry.line_number,
                f"an urgent deferral needs a real GitHub follow-up issue such as #123 or "
                f"owner/repo#123; '{shown}' is not one",
            )
        )
    elif follow_up in change_issue_numbers(entry.change):
        findings.append(
            Finding(
                CODE_FOLLOW_UP_SELF_REFERENCE,
                entry.change,
                entry.line_number,
                f"issue #{follow_up} is this change's own issue, so it cannot also be the "
                "follow-up that tracks the deferred documentation",
            )
        )

    if is_placeholder(entry.reason_cell) or not entry.reason_cell.strip():
        findings.append(
            Finding(
                CODE_REASON_MISSING,
                entry.change,
                entry.line_number,
                "an urgent deferral needs a reason the documentation could not ship with the "
                "release; the Reason cell says nothing",
            )
        )

    return findings


# ──────────────────────────────────────────────────────────────────────────────
# Engine
# ──────────────────────────────────────────────────────────────────────────────


def run(
    project: Path | str,
    mode: str = MODE_ADVISORY,
    changed_files: list[str] | None = None,
    previous_ledger_text: str | None = None,
    ledger_text: str | None = None,
) -> Report:
    project = Path(project).resolve()
    changed_files = [path.strip() for path in (changed_files or []) if path.strip()]

    config, problem = resolve_config(project)

    if problem is not None:
        return Report(
            mode=mode,
            state=STATE_UNAVAILABLE,
            ledger_path=None,
            config_source=CONFIG_NAME,
            entries_total=0,
            entries_in_scope=0,
            staff_facing_changes=[],
            findings=[Finding(CODE_CONFIG_UNREADABLE, "-", 0, problem)],
            notes=[
                "staff documentation enforcement could not run: the project configuration "
                "is unreadable, so this is reported as unavailable, not as passed"
            ],
        )

    if config is None:
        findings = []
        if mode == MODE_BLOCKING:
            findings.append(
                Finding(
                    CODE_CONFIG_UNAVAILABLE,
                    "-",
                    0,
                    f"this project has no {CONFIG_NAME} and no recognisable staff-documentation "
                    "convention, so a release cannot prove its documentation decision here",
                )
            )
        return Report(
            mode=mode,
            state=STATE_UNAVAILABLE,
            ledger_path=None,
            config_source=None,
            entries_total=0,
            entries_in_scope=0,
            staff_facing_changes=[],
            findings=findings,
            notes=[
                f"no {CONFIG_NAME} and no detected convention in {project}: staff documentation "
                "enforcement reported as unavailable, not as passed"
            ],
        )

    staff_facing = [path for path in changed_files if is_staff_facing(path, config)]

    ledger_path = project / config.ledger
    if ledger_text is None:
        ledger_text = read_text_safely(ledger_path) if ledger_path.is_file() else None

    notes: list[str] = [f"project shape resolved from {config.source}"]
    findings: list[Finding] = []

    if ledger_text is None:
        if staff_facing:
            findings.append(
                Finding(
                    CODE_LEDGER_MISSING,
                    "-",
                    0,
                    f"this change touches {len(staff_facing)} staff-facing file(s) "
                    f"({', '.join(staff_facing[:3])}"
                    f"{', ...' if len(staff_facing) > 3 else ''}) but {config.ledger} is not "
                    "there to record the documentation decision",
                )
            )
        else:
            notes.append(
                f"no {config.ledger} in {project} and no staff-facing file changed: nothing to decide"
            )
        # The configuration resolved and the changed files were read, so this is a
        # real answer either way: a finding when a staff-facing change has nowhere
        # to record its decision, a pass when nothing needed one.
        return Report(
            mode=mode,
            state=STATE_OK,
            ledger_path=None,
            config_source=config.source,
            entries_total=0,
            entries_in_scope=0,
            staff_facing_changes=staff_facing,
            findings=findings,
            notes=notes,
        )

    current, saw_table = parse_ledger_tables(ledger_text)
    previous = parse_ledger(previous_ledger_text) if previous_ledger_text is not None else None

    if not saw_table and staff_facing:
        findings.append(
            Finding(
                CODE_LEDGER_UNPARSEABLE,
                "-",
                0,
                f"{config.ledger} has no readable decision table; add one with Change, Decision, "
                "Artifacts, Owner, Follow-up and Reason columns",
            )
        )
        return Report(
            mode=mode,
            state=STATE_UNAVAILABLE,
            ledger_path=str(ledger_path),
            config_source=config.source,
            entries_total=0,
            entries_in_scope=0,
            staff_facing_changes=staff_facing,
            findings=findings,
            notes=notes,
        )

    if previous is None:
        notes.append(
            "the previous ledger revision could not be read, so no decision was scoped to this "
            "change; pass --base, --staged, or --previous-ledger to scope it"
        )
        if mode == MODE_BLOCKING and staff_facing:
            findings.append(
                Finding(
                    CODE_SCOPE_UNAVAILABLE,
                    "-",
                    0,
                    "this change touches staff-facing files but the previous ledger revision is "
                    "unreadable, so the engine cannot tell which decision belongs to this release",
                )
            )
        return Report(
            mode=mode,
            state=STATE_UNAVAILABLE,
            ledger_path=str(ledger_path),
            config_source=config.source,
            entries_total=len(current),
            entries_in_scope=0,
            staff_facing_changes=staff_facing,
            findings=findings,
            notes=notes,
        )

    scoped = entries_in_scope(current, previous)

    for entry in removed_entries(current, previous):
        findings.append(
            Finding(
                CODE_ENTRY_REMOVED,
                entry.change,
                entry.line_number,
                f"the recorded decision for '{entry.change}' was deleted from {config.ledger}; "
                "past release decisions are a record, not something a later change may erase",
            )
        )

    if staff_facing and not scoped:
        findings.append(
            Finding(
                CODE_DECISION_MISSING,
                "-",
                0,
                f"this change touches {len(staff_facing)} staff-facing file(s) "
                f"({', '.join(staff_facing[:3])}"
                f"{', ...' if len(staff_facing) > 3 else ''}) but adds no decision to "
                f"{config.ledger}; say whether staff documentation is relevant, not relevant "
                "with a reason, or urgently deferred with an owner and a follow-up issue",
            )
        )

    counts: dict[str, int] = {}
    for entry in scoped:
        counts[entry.decision] = counts.get(entry.decision, 0) + 1
        findings.extend(evaluate_entry(project, config, entry, changed_files))

    notes.append(
        f"{len(scoped)} of {len(current)} recorded decisions are in scope for this change; "
        "decisions from earlier releases are not re-opened here"
    )

    return Report(
        mode=mode,
        state=STATE_OK,
        ledger_path=str(ledger_path),
        config_source=config.source,
        entries_total=len(current),
        entries_in_scope=len(scoped),
        staff_facing_changes=staff_facing,
        findings=findings,
        notes=notes,
        summary_counts=counts,
    )


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────


def ledger_text_at(project: Path, revision: str, ledger: str) -> str | None:
    code, out = git(project, "show", f"{revision}:{ledger}")
    if code != 0:
        return ""
    return out


def format_report(report: Report) -> str:
    lines: list[str] = []
    for note in report.notes:
        lines.append(f"NOTE  {note}")

    if report.summary_counts:
        summary = ", ".join(f"{name}={count}" for name, count in sorted(report.summary_counts.items()))
        lines.append(f"DECISIONS  {summary}")

    for finding in report.findings:
        location = f" (line {finding.line_number})" if finding.line_number else ""
        lines.append(f"FAIL  {finding.code}{location} {finding.change}: {finding.detail}")

    headline = "STAFF DOCUMENTATION RELEASE GATE"
    scope = f"decisions_in_scope={report.entries_in_scope}/{report.entries_total}"
    if report.ok and report.state == STATE_UNAVAILABLE:
        lines.append(f"{headline}: UNAVAILABLE (mode={report.mode}) reported, not assumed passed")
    elif report.ok:
        lines.append(f"{headline}: PASS (mode={report.mode}, {scope}, findings=0)")
    elif report.mode == MODE_ADVISORY:
        lines.append(
            f"{headline}: ADVISORY FINDINGS (mode={report.mode}, {scope}, "
            f"findings={len(report.findings)}) not blocking here; blocked at release"
        )
    else:
        lines.append(f"{headline}: FAIL (mode={report.mode}, {scope}, findings={len(report.findings)})")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Enforce a project's staff documentation release decisions.",
    )
    parser.add_argument("--project", default=".", help="Project directory to check")
    parser.add_argument(
        "--mode",
        choices=MODES,
        default=MODE_ADVISORY,
        help="advisory reports and exits 0; blocking exits 1 on findings",
    )
    parser.add_argument("--staged", action="store_true", help="Scope to files staged in git")
    parser.add_argument("--base", help="Scope to files changed since this git ref")
    parser.add_argument(
        "--changed-file",
        action="append",
        default=[],
        dest="changed_file",
        help="Scope to an explicit path (repeatable)",
    )
    parser.add_argument(
        "--previous-ledger",
        help="Path to the ledger as it was before this change (for non-git scoping)",
    )
    parser.add_argument("--json", action="store_true", help="Emit the report as JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    project = Path(args.project).resolve()
    if not project.is_dir():
        print(f"STAFF DOCUMENTATION RELEASE GATE: ERROR project {project} is not a directory")
        return 2

    if not (args.staged or args.base or args.changed_file):
        parser.error("needs a change source: --staged, --base <ref>, or --changed-file <path>")

    config, _ = resolve_config(project)
    ledger_name = config.ledger if config else LEDGER_NAME

    changed_files: list[str] = []
    previous_ledger_text: str | None = None

    if args.changed_file:
        changed_files = list(args.changed_file)
    elif args.staged:
        staged = staged_changed_files(project)
        if staged is None:
            print(
                f"STAFF DOCUMENTATION RELEASE GATE: UNAVAILABLE (mode={args.mode}) not a git "
                "work tree; staged scope could not be read"
            )
            return 0 if args.mode == MODE_ADVISORY else 2
        changed_files = staged
        previous_ledger_text = ledger_text_at(project, "HEAD", ledger_name)
    else:
        based = base_changed_files(project, args.base)
        if based is None:
            print(
                f"STAFF DOCUMENTATION RELEASE GATE: UNAVAILABLE (mode={args.mode}) base ref "
                f"'{args.base}' is not resolvable here"
            )
            return 0 if args.mode == MODE_ADVISORY else 2
        changed_files = based
        previous_ledger_text = ledger_text_at(project, args.base, ledger_name)

    if args.previous_ledger:
        previous_path = Path(args.previous_ledger)
        previous_ledger_text = read_text_safely(previous_path) if previous_path.is_file() else ""

    report = run(
        project=project,
        mode=args.mode,
        changed_files=changed_files,
        previous_ledger_text=previous_ledger_text,
    )

    if args.json:
        print(json.dumps(report.as_dict(), indent=2))
    else:
        print(format_report(report))

    return 1 if report.blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
