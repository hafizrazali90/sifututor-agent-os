#!/usr/bin/env python3
"""Shared, model-agnostic test-coverage enforcement for Sifututor projects.

Issue 2 asked for TESTING.md enforcement that Claude, Codex, Kilo, and any other
agent can execute the same way. CP-11 added the practical half: the rule has to
survive the walk from a local change to a release, in repositories that do not
share a test framework and do not all have GitHub CI.

This module is the single enforcement entrypoint. It owns the manifest parser,
the evidence rules, and the three gate modes. Everything else in the Agent OS
(the legacy manifest checker, the shared pre-commit guard, the playbooks, the
product CI template) calls into it instead of re-implementing the rules.

What it proves, and what it does not:

- It proves a manifest row is honest: a declared test path exists, holds real
  executable test content, and is not weaker than the evidence the row claims.
- It proves a release has a recorded coverage decision for the rows it touches.
- It does NOT prove a test is meaningful. An agent and a reviewer still read
  intent. The engine only removes the cheap lies.

Three modes:

    manifest  every row in TESTING.md. Audits and scheduled sweeps.
    change    only the rows this change actually touches. The commit guard.
              Pre-existing coverage debt never blocks an unrelated change.
    release   the rows this release touches must carry proof, or a named
              exception that Hafiz approved. Pre-push / pre-deploy / CI.

Stdlib only, no network, no framework assumptions.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


MANIFEST_NAME = "TESTING.md"

MODE_MANIFEST = "manifest"
MODE_CHANGE = "change"
MODE_RELEASE = "release"
MODES = (MODE_MANIFEST, MODE_CHANGE, MODE_RELEASE)

STATE_OK = "ok"
STATE_UNAVAILABLE = "unavailable"

STATUS_COVERED = "covered"
STATUS_PARTIAL = "partial"
STATUS_MISSING = "missing"
STATUS_NOT_USER_FACING = "not-user-facing"
STATUS_EXCEPTION = "exception"
STATUS_UNKNOWN = "unknown"

# Evidence ladder. A row may never be proved by something below what it claims.
LEVEL_NONE = 0
LEVEL_UNIT = 1
LEVEL_INTEGRATION = 2
LEVEL_JOURNEY = 3

LEVEL_NAMES = {
    LEVEL_NONE: "none",
    LEVEL_UNIT: "unit",
    LEVEL_INTEGRATION: "integration/feature/API",
    LEVEL_JOURNEY: "permanent E2E / human journey",
}

CODE_DECLARED_WITHOUT_PATH = "declared_without_path"
CODE_MISSING_TEST_FILE = "missing_test_file"
CODE_EMPTY_OR_COMMENT_ONLY = "empty_or_comment_only_test"
CODE_EVIDENCE_WEAKER_THAN_DECLARED = "evidence_weaker_than_declared"
CODE_PARTIAL_WITHOUT_GAP = "partial_without_named_gap"
CODE_UNJUSTIFIED_NOT_USER_FACING = "unjustified_not_user_facing"
CODE_EXCEPTION_WITHOUT_APPROVAL = "exception_without_named_approval"
CODE_RELEASE_WITHOUT_PROOF = "release_without_proof"
CODE_MANIFEST_UNAVAILABLE = "manifest_unavailable"
CODE_UNREADABLE_STATUS = "unreadable_status"

# The only reasons a user-facing workflow may ship without permanent E2E.
# Source of truth: AGENTS.md "permanent E2E" rules and test-coverage.md.
ALLOWED_EXCEPTION_REASONS = (
    "missing credential",
    "no safe representative data",
    "no representative data",
    "destructive workflow",
    "destructive action required",
    "tooling unavailable",
    "external system unreliable",
    "not user-facing",
)

# Release authority. An exception is Hafiz's call, not the builder's.
APPROVAL_PATTERN = re.compile(r"\bapproved by\s+([A-Za-z][\w .'-]{1,40})", re.IGNORECASE)

# Roles that make a feature user-facing by definition.
HUMAN_ROLE_WORDS = (
    "staff",
    "admin",
    "parent",
    "tutor",
    "student",
    "customer",
    "teacher",
    "user",
    "mobile",
    "reviewer",
    "operator",
)

PLACEHOLDER_CELLS = {"", "-", "--", "—", "–", "n/a", "na", "none", "tbd", "todo", "?", "."}

HEADER_FEATURE_NAMES = frozenset(
    {
        "feature",
        "features",
        "feature / user story",
        "feature/user story",
        "user story",
        "user stories",
        "scenario",
        "scenarios",
        "workflow",
    }
)

HEADER_STATUS_NAMES = frozenset({"status", "state", "coverage status", "coverage state"})

# A header cell names a column. Anything longer than this is prose.
MAX_HEADER_CELL_LENGTH = 40

# Sibling products in the same workspace. A row may prove its human journey in
# the product that actually owns the screen.
PAIRED_PRODUCT_NAMES = (
    "ripple",
    "sifututor_parent",
    "sifututor_tutor",
    "parent app",
    "tutor app",
    "lls",
    "kelas",
)


# ──────────────────────────────────────────────────────────────────────────────
# Manifest parsing — the single parser every caller shares
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class Row:
    feature: str
    status: str
    line_number: int
    raw: str
    status_cell: str = ""
    type_cell: str = ""
    test_cell: str = ""
    source_cell: str = ""
    notes_cell: str = ""
    role_cell: str = ""
    test_paths: list[str] = field(default_factory=list)
    source_paths: list[str] = field(default_factory=list)
    evidence_paths: list[str] = field(default_factory=list)
    external_paths: list[str] = field(default_factory=list)
    external_evidence: bool = False
    required_level: int = LEVEL_NONE

    @property
    def key(self) -> str:
        return normalize_text(self.feature)


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip().lower()


def split_row(line: str) -> list[str]:
    parts = [cell.strip() for cell in line.strip().split("|")]
    if len(parts) >= 2 and parts[0] == "" and parts[-1] == "":
        return parts[1:-1]
    return [part for part in parts if part != ""]


def is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(set(cell) <= {"-", ":", " "} and cell for cell in cells)


def _pick(header: list[str], *, require: tuple[str, ...], reject: tuple[str, ...] = ()) -> int | None:
    """Return the index of the first header cell matching one of `require`.

    `require` is ordered most-specific-first so "Test File(s)" always wins over
    "Test Type", and a "Source Files" column is never mistaken for a test column.
    """
    for wanted in require:
        for index, cell in enumerate(header):
            if wanted in cell and not any(bad in cell for bad in reject):
                return index
    return None


def parse_manifest(text: str) -> list[Row]:
    """Parse every markdown coverage table in a TESTING.md into rows."""
    rows: list[Row] = []
    header: list[str] | None = None
    columns: dict[str, int | None] = {}

    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped.startswith("|"):
            header = None
            continue

        cells = split_row(stripped)
        if not cells:
            continue
        if is_separator(cells):
            continue

        lowered = [cell.lower() for cell in cells]

        if header is None:
            looks_like_header = (
                all(len(cell) <= MAX_HEADER_CELL_LENGTH for cell in lowered)
                and any(cell in HEADER_FEATURE_NAMES for cell in lowered)
                and any(cell in HEADER_STATUS_NAMES for cell in lowered)
            )
            if looks_like_header:
                header = lowered
                columns = {
                    "feature": _pick(header, require=("feature", "user story", "scenario")),
                    "status": _pick(header, require=("status", "state")),
                    "test": _pick(
                        header,
                        require=(
                            "test file",
                            "test files",
                            "test spec",
                            "spec file",
                            "coverage file",
                            "automated coverage",
                            "automated",
                            "coverage",
                            "test",
                            "evidence",
                        ),
                        reject=("type",),
                    ),
                    "type": _pick(header, require=("test type", "type")),
                    "source": _pick(header, require=("source file", "source", "implementation"), reject=("test",)),
                    "notes": _pick(header, require=("note", "journey", "evidence", "gap", "proof", "comment")),
                    "role": _pick(header, require=("role", "persona", "audience")),
                }
            continue

        feature_index = columns.get("feature")
        status_index = columns.get("status")
        if feature_index is None or status_index is None:
            continue
        if len(cells) <= max(feature_index, status_index):
            continue

        def cell_at(name: str) -> str:
            index = columns.get(name)
            if index is None or index >= len(cells):
                return ""
            return cells[index]

        feature = cells[feature_index]
        if not feature or normalize_text(feature) in PLACEHOLDER_CELLS:
            continue

        status_cell = cells[status_index]
        type_cell = cell_at("type")
        test_cell = cell_at("test")
        row = Row(
            feature=feature,
            status=classify_status(status_cell),
            line_number=line_number,
            raw=normalize_text(stripped),
            status_cell=status_cell,
            type_cell=type_cell,
            test_cell=test_cell,
            source_cell=cell_at("source"),
            notes_cell=cell_at("notes"),
            role_cell=cell_at("role"),
        )
        row.test_paths, row.external_paths = classify_declared_paths(row.test_cell)
        row.source_paths = extract_paths(row.source_cell, allow_directories=True)
        row.evidence_paths = [
            value for value in extract_paths(row.notes_cell) if value not in row.test_paths
        ]
        row.external_evidence = bool(row.external_paths) or has_external_evidence(
            row.test_cell, row.notes_cell, row.type_cell
        )
        row.required_level = declared_level(type_cell, row.status_cell)
        rows.append(row)

    return rows


PASSED_PATTERN = re.compile(r"\b(passed|passes|verified|proven)\b")
NEGATED_PASS_PATTERN = re.compile(r"\b(not|never|no)\s+(passed|passes|verified|proven)\b|\b(unverified|unproven|failing|failed)\b")


def classify_status(cell: str) -> str:
    lowered = normalize_text(cell)
    # Order matters: "not user-facing" and "exception" are decisions, not gaps,
    # and both can contain words that would otherwise read as covered/missing.
    if "not user-facing" in lowered or "not user facing" in lowered or "internal only" in lowered:
        return STATUS_NOT_USER_FACING
    if "exception" in lowered or "waived" in lowered or "accepted risk" in lowered:
        return STATUS_EXCEPTION
    if "missing" in lowered or "❌" in cell or "✗" in cell or lowered == "none":
        return STATUS_MISSING
    if "partial" in lowered or "⚠" in cell:
        return STATUS_PARTIAL
    if "covered" in lowered or "✅" in cell or "✔" in cell:
        return STATUS_COVERED
    # Live manifests also write the decision as a sentence: "Passed locally",
    # "Actual HTTP multipart passed". That is a real claim, so read it.
    if PASSED_PATTERN.search(lowered) and not NEGATED_PASS_PATTERN.search(lowered):
        return STATUS_COVERED
    return STATUS_UNKNOWN


PAIRED_EVIDENCE_PATTERN = re.compile(r"\b(paired|companion|counterpart|cross-repo|cross repo)\b", re.IGNORECASE)


def mentions_a_path(cell: str) -> bool:
    """Cheap linear scan for a path-like token.

    Deliberately not a regex: manifest notes cells run to thousands of
    characters, and a character-class-plus-extension pattern backtracks
    quadratically over them. A whitespace split is linear and answers the same
    question.
    """
    for token in cell.split():
        stripped = token.strip("`,;()[]<>\"'")
        if "/" in stripped and "." in stripped.rsplit("/", 1)[-1]:
            return True
    return False


def has_external_evidence(test_cell: str, notes_cell: str, type_cell: str = "") -> bool:
    """True when the row says its journey proof lives in the paired repository.

    `AGENTS.md` already uses this vocabulary ("paired frontend/mobile
    evidence"). A SIMS API whose only human surface is a Ripple screen proves
    the journey in Ripple's E2E suite. That row is honest; it is simply not
    verifiable from inside this repository, and the enforcement has to say so
    instead of demanding a duplicate local E2E.
    """
    for cell in (test_cell or "", notes_cell or "", type_cell or ""):
        if not cell:
            continue
        lowered = cell.lower()
        if PAIRED_EVIDENCE_PATTERN.search(cell) and (mentions_a_path(cell) or _names_a_sibling_product(lowered)):
            return True
        # "... Ripple browser E2E" names where the journey lives without using
        # the word "paired". That is still an explicit, reviewable claim.
        if _names_a_sibling_product(lowered) and any(
            marker in lowered for marker in ("e2e", "browser", "journey", "maestro", "playwright")
        ):
            return True
    return False


# Whole-token match only. A substring match would read the local Laravel test
# `RippleTutorLifecycleSignalsApiTest.php` as evidence that lives in Ripple, and
# quietly stop requiring it to exist.
PAIRED_PRODUCT_PATTERNS = tuple(
    re.compile(r"(?<![a-z0-9])" + re.escape(name) + r"(?![a-z0-9])") for name in PAIRED_PRODUCT_NAMES
)


def _names_a_sibling_product(lowered_cell: str) -> bool:
    return any(pattern.search(lowered_cell) for pattern in PAIRED_PRODUCT_PATTERNS)


def declared_level(type_cell: str, status_cell: str) -> int:
    """The evidence strength a row claims for itself."""
    lowered = normalize_text(type_cell) + " " + normalize_text(status_cell)
    if not normalize_text(type_cell):
        return LEVEL_NONE
    if normalize_text(type_cell) in PLACEHOLDER_CELLS:
        return LEVEL_NONE
    if any(
        word in lowered
        for word in ("e2e", "end-to-end", "end to end", "journey", "playwright", "maestro", "detox", "cypress", "browser")
    ):
        return LEVEL_JOURNEY
    if any(word in lowered for word in ("feature", "integration", "api", "contract", "functional", "portal")):
        return LEVEL_INTEGRATION
    if any(word in lowered for word in ("unit", "widget", "service", "component", "snapshot")):
        return LEVEL_UNIT
    return LEVEL_NONE


# A manifest is data an agent wrote. It is never allowed to point enforcement
# outside the project it describes: an absolute path, a `..` escape, a home
# expansion, or an environment file would turn a coverage check into an
# arbitrary filesystem read. `/` on its own once sent a real run walking the
# whole machine, which is how this rule was found.
UNREADABLE_PATH_NAMES = (".env",)


def is_safe_project_relative(value: str) -> bool:
    if value.startswith(("/", "~", "\\")) or ":" in value.split("/")[0]:
        return False
    parts = [part for part in value.replace("\\", "/").split("/") if part]
    if not parts or any(part == ".." for part in parts):
        return False
    name = parts[-1].lower()
    if any(name == blocked or name.startswith(blocked + ".") for blocked in UNREADABLE_PATH_NAMES):
        return False
    return True


def within(project: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(project.resolve())
    except (OSError, ValueError):
        return False
    return True


BRACE_PATTERN = re.compile(r"([\w./@-]*)\{([^{}]+)\}([\w./@-]*)")
SEGMENT_SPLIT = re.compile(r";|,|<br\s*/?>|\n")


def expand_braces(text: str) -> str:
    """Rewrite `tests/Security/{ATest,BTest}.php` into two real paths.

    Live manifests use shell brace notation to keep a long row readable. Left
    literal it reads as one path that never exists, which is a false accusation
    rather than a caught lie. Expanding first also makes comma splitting safe.
    """

    def expand(match: re.Match[str]) -> str:
        prefix, body, suffix = match.group(1), match.group(2), match.group(3)
        parts = [part.strip() for part in body.split(",") if part.strip()]
        if not parts:
            return match.group(0)
        return ", ".join(f"{prefix}{part}{suffix}" for part in parts)

    return BRACE_PATTERN.sub(expand, text or "")


def classify_declared_paths(cell: str) -> tuple[list[str], list[str]]:
    """Split a test cell into paths this repository owns and paths it does not.

    A row may legitimately read:

        `tests/Feature/ApiTest.php`; paired Ripple `tests/e2e/crm/x.spec.ts`

    The first path must exist here. The second lives in the paired product and
    cannot be checked from this repository, so it is recorded as a named
    external claim rather than reported as a missing file.
    """
    local: list[str] = []
    external: list[str] = []
    for segment in SEGMENT_SPLIT.split(expand_braces(cell)):
        paths = extract_paths(segment)
        if not paths:
            continue
        lowered = segment.lower()
        if PAIRED_EVIDENCE_PATTERN.search(segment) or _names_a_sibling_product(lowered):
            external.extend(paths)
        else:
            local.extend(paths)
    return local, external


def extract_paths(cell: str, *, allow_directories: bool = False) -> list[str]:
    """Pull declared file paths out of a manifest cell.

    Framework-agnostic on purpose. Backticked values are authoritative; without
    backticks a token counts only when it looks like a path. Nothing here is
    keyed to a language or an extension allow-list, so a Flutter `.dart`, a
    Python `.py`, a Maestro `.yaml`, or a Gherkin `.feature` path is validated
    exactly as strictly as a `.spec.ts`.
    """
    if normalize_text(cell) in PLACEHOLDER_CELLS:
        return []

    quoted = re.findall(r"`([^`]+)`", cell)
    candidates = quoted if quoted else re.split(r",|;|<br\s*/?>|\n", cell)

    paths: list[str] = []
    for raw in candidates:
        # Brace expansion can leave a stray backtick on an unquoted fragment.
        value = raw.strip().strip("*_ " + chr(96))
        # Drop a trailing test-case-ID parenthetical: `foo.spec.ts` (RG-TUT-025)
        value = re.sub(r"\s*\(.*\)\s*$", "", value).strip()
        if not value or normalize_text(value) in PLACEHOLDER_CELLS:
            continue
        if value.startswith(("http://", "https://")):
            continue
        looks_like_path = "/" in value or "*" in value or re.search(r"\.[A-Za-z0-9_]{1,10}$", value)
        if not looks_like_path:
            continue
        if not is_safe_project_relative(value):
            continue
        if " " in value and "*" not in value:
            # Prose, not a path.
            continue
        if not allow_directories and value.endswith("/"):
            paths.append(value)
            continue
        paths.append(value)

    deduped: list[str] = []
    for value in paths:
        if value not in deduped:
            deduped.append(value)
    return deduped


# ──────────────────────────────────────────────────────────────────────────────
# Evidence inspection — what a declared path actually contains
# ──────────────────────────────────────────────────────────────────────────────


JOURNEY_MARKERS = (
    "e2e",
    "end-to-end",
    "end2end",
    "playwright",
    "cypress",
    "maestro",
    "detox",
    "appium",
    "selenium",
    "browser",
    "journey",
    "smoke",
    "acceptance",
)

INTEGRATION_MARKERS = (
    "feature",
    "integration",
    "api",
    "contract",
    "functional",
    "portal",
    "request",
)

# One token from any of these means the file declares or asserts something.
# Deliberately broad: PHPUnit, Pest, Jest, Vitest, Playwright, pytest, unittest,
# Dart/Flutter, Go, JUnit, Rust, RSpec, Gherkin, and Maestro all land here.
TEST_TOKENS = (
    re.compile(r"\bdef\s+test", re.IGNORECASE),
    re.compile(r"\bfunc\s+Test[A-Z_]"),
    re.compile(r"\bfunction\s+test", re.IGNORECASE),
    re.compile(r"\bclass\s+\w*Test\b"),
    re.compile(r"\b(it|test|describe|context|scenario|testWidgets|group)\s*\("),
    re.compile(r"\bassert", re.IGNORECASE),
    re.compile(r"\bexpect\s*\("),
    re.compile(r"->(assert|should|see|expects)"),
    re.compile(r"@Test\b"),
    re.compile(r"#\[\s*test\s*\]"),
    re.compile(r"^\s*(Scenario|Feature|Given|When|Then)\s*:", re.MULTILINE),
    re.compile(r"^\s*appId\s*:", re.MULTILINE),
    re.compile(r"\bshould\s*\(", re.IGNORECASE),
)

LINE_COMMENT_PREFIXES = ("//", "#", "--", "*", "/*", "*/", "<!--", "-->", '"""', "'''", ";")


def strip_comments(text: str) -> str:
    """Remove block and line comments so a placeholder file cannot look real."""
    # All three use DOTALL with a lazy `.` rather than a `(?:.|\n)` alternation:
    # the alternation form backtracks catastrophically on large source files.
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r'""".*?"""', "", text, flags=re.DOTALL)
    kept: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(LINE_COMMENT_PREFIXES):
            continue
        kept.append(stripped)
    return "\n".join(kept)


def classify_path_level(path_value: str) -> int:
    lowered = path_value.lower()
    segments = re.split(r"[/\\.\-_]", lowered)
    if any(marker in segments for marker in JOURNEY_MARKERS) or any(
        marker in lowered for marker in ("e2e", "playwright", "maestro", "detox", "cypress")
    ):
        return LEVEL_JOURNEY
    if lowered.endswith(".feature"):
        return LEVEL_JOURNEY
    if any(marker in segments for marker in INTEGRATION_MARKERS):
        return LEVEL_INTEGRATION
    return LEVEL_UNIT


# A manifest may name a test by bare filename ("StreakMilestoneBadgeTest.php").
# That is a real convention in `lls`, so it has to resolve. It resolves by
# searching the project tree, never into dependency, build, or nested-worktree
# directories: a name that only exists under `vendor/` or `node_modules/` is a
# third-party file, not this project's proof.
UNSEARCHABLE_DIRECTORIES = frozenset(
    {
        ".git",
        ".worktrees",
        ".next",
        ".nuxt",
        ".venv",
        ".dart_tool",
        "__pycache__",
        "node_modules",
        "vendor",
        "venv",
        "dist",
        "build",
        "coverage",
        "storage",
        "target",
        "Pods",
    }
)

_FILENAME_INDEX_CACHE: dict[str, dict[str, list[Path]]] = {}


def filename_index(project: Path) -> dict[str, list[Path]]:
    """Map bare filename -> paths, ignoring dependency and build trees."""
    key = str(project)
    cached = _FILENAME_INDEX_CACHE.get(key)
    if cached is not None:
        return cached

    index: dict[str, list[Path]] = {}
    for directory, subdirectories, filenames in os.walk(project):
        subdirectories[:] = [
            name for name in subdirectories if name not in UNSEARCHABLE_DIRECTORIES and not name.startswith(".git")
        ]
        for filename in filenames:
            index.setdefault(filename, []).append(Path(directory) / filename)

    for paths in index.values():
        paths.sort()
    _FILENAME_INDEX_CACHE[key] = index
    return index


@dataclass
class PathProof:
    declared: str
    matches: list[Path]
    exists: bool
    executable: bool
    level: int


def resolve_declared_path(project: Path, declared: str) -> list[Path]:
    if not is_safe_project_relative(declared):
        return []
    if "*" in declared:
        return sorted(p for p in project.glob(declared) if p.is_file() and within(project, p))
    candidate = project / declared
    if not within(project, candidate):
        return []
    if candidate.is_file():
        return [candidate]
    if candidate.is_dir():
        # A row may point at a directory of specs. That is a real declaration,
        # but only if something inside it actually runs.
        return sorted(p for p in candidate.rglob("*") if p.is_file())
    if "/" not in declared:
        return list(filename_index(project).get(declared, []))
    return []


def read_text_safely(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def file_is_executable_test(path: Path) -> bool:
    body = strip_comments(read_text_safely(path))
    if not body.strip():
        return False
    return any(pattern.search(body) for pattern in TEST_TOKENS)


def inspect_path(project: Path, declared: str) -> PathProof:
    matches = resolve_declared_path(project, declared)
    # An empty directory resolves to no files but is still "there": report it as
    # a declaration without executable content, not as a typo'd path.
    directory = project / declared
    exists = bool(matches) or (within(project, directory) and directory.is_dir())
    runnable = [match for match in matches if file_is_executable_test(match)]
    # Level comes from where the test actually lives. A row may name a test by
    # bare filename; `StreakMilestoneBadgeTest.php` sitting in `tests/Feature/`
    # is feature-level evidence even though the declared string says nothing.
    level = LEVEL_NONE
    for match in runnable:
        try:
            relative = match.relative_to(project).as_posix()
        except ValueError:
            relative = match.as_posix()
        level = max(level, classify_path_level(relative), classify_path_level(declared))
    return PathProof(
        declared=declared,
        matches=matches,
        exists=exists,
        executable=bool(runnable),
        level=level,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Findings and report
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class Finding:
    code: str
    feature: str
    line_number: int
    detail: str

    def as_dict(self) -> dict:
        return {
            "code": self.code,
            "feature": self.feature,
            "line": self.line_number,
            "detail": self.detail,
        }


@dataclass
class Report:
    mode: str
    state: str
    manifest_path: str | None
    rows_total: int
    rows_in_scope: int
    findings: list[Finding]
    notes: list[str]
    summary_counts: dict[str, int]

    @property
    def ok(self) -> bool:
        if self.state == STATE_UNAVAILABLE:
            # Honest degradation: a project without a manifest is not proof of
            # coverage, but it is also not a reason to block ordinary work.
            # A release is different — there is nothing to prove the release with.
            return self.mode != MODE_RELEASE and not self.findings
        return not self.findings

    def as_dict(self) -> dict:
        return {
            "mode": self.mode,
            "state": self.state,
            "ok": self.ok,
            "manifest": self.manifest_path,
            "rows_total": self.rows_total,
            "rows_in_scope": self.rows_in_scope,
            "summary_counts": self.summary_counts,
            "notes": list(self.notes),
            "findings": [finding.as_dict() for finding in self.findings],
        }


# ──────────────────────────────────────────────────────────────────────────────
# Scoping — which rows this change is answerable for
# ──────────────────────────────────────────────────────────────────────────────


def path_matches_change(declared: str, changed: str) -> bool:
    declared = declared.strip().lstrip("./")
    changed = changed.strip().lstrip("./")
    if not declared:
        return False
    if "*" in declared:
        return fnmatch.fnmatch(changed, declared)
    if declared.endswith("/"):
        return changed.startswith(declared)
    return changed == declared or changed.startswith(declared.rstrip("/") + "/")


def rows_in_scope(rows: list[Row], changed_files: list[str], previous_rows: list[Row] | None) -> list[Row]:
    """Rows this change is answerable for.

    A change answers for a row when it edits a test the row declares, edits a
    source file the row claims, or edits the row itself. Untouched coverage debt
    elsewhere in the manifest is somebody else's ticket, not this commit's
    blocker — that is what keeps the guard adoptable in repositories that
    already carry a long tail of gaps.
    """
    previous_by_key = {row.key: row for row in (previous_rows or [])}
    manifest_changed = any(Path(changed).name == MANIFEST_NAME for changed in changed_files)

    scoped: list[Row] = []
    for row in rows:
        touched = False

        for declared in row.test_paths + row.source_paths:
            if any(path_matches_change(declared, changed) for changed in changed_files):
                touched = True
                break

        if not touched and manifest_changed:
            if previous_rows is None:
                # No baseline available: the manifest changed, so treat every
                # row as this change's responsibility rather than guess.
                touched = True
            else:
                previous = previous_by_key.get(row.key)
                touched = previous is None or previous.raw != row.raw

        if touched:
            scoped.append(row)

    return scoped


# ──────────────────────────────────────────────────────────────────────────────
# Rules
# ──────────────────────────────────────────────────────────────────────────────


def _row_claims_a_human_role(row: Row) -> bool:
    haystack = normalize_text(row.role_cell)
    if not haystack:
        return False
    return any(word in haystack for word in HUMAN_ROLE_WORDS)


def evaluate_integrity(project: Path, row: Row) -> list[Finding]:
    """Rules that apply to any mode: a row must not claim more than it has."""
    findings: list[Finding] = []

    if row.status == STATUS_UNKNOWN:
        findings.append(
            Finding(
                CODE_UNREADABLE_STATUS,
                row.feature,
                row.line_number,
                f"status '{row.status_cell.strip()}' cannot be read as covered, partial, missing, "
                "not-user-facing, or a named exception; a claim no gate can read is not a claim",
            )
        )
        return findings

    if row.status == STATUS_MISSING and not row.test_paths:
        return findings

    if row.status in (STATUS_COVERED, STATUS_PARTIAL) and not row.test_paths and not row.external_paths:
        findings.append(
            Finding(
                CODE_DECLARED_WITHOUT_PATH,
                row.feature,
                row.line_number,
                f"status '{row.status_cell.strip() or row.status}' names no test file; "
                "an empty, placeholder, or dash cell is not coverage",
            )
        )
        return findings

    proofs = [inspect_path(project, declared) for declared in row.test_paths]

    for proof in proofs:
        if not proof.exists:
            findings.append(
                Finding(
                    CODE_MISSING_TEST_FILE,
                    row.feature,
                    row.line_number,
                    f"declared test `{proof.declared}` does not exist in the project",
                )
            )

    # Support files, fixtures and configs may sit beside the test they serve.
    # The row is only a lie when nothing it names actually runs.
    if proofs and not any(proof.executable for proof in proofs):
        named = ", ".join(f"`{proof.declared}`" for proof in proofs if proof.exists)
        if named:
            findings.append(
                Finding(
                    CODE_EMPTY_OR_COMMENT_ONLY,
                    row.feature,
                    row.line_number,
                    f"no declared test has executable test content ({named} is empty, "
                    "comments only, a config, or a directory rather than a test)",
                )
            )

    if row.status == STATUS_PARTIAL and normalize_text(row.notes_cell) in PLACEHOLDER_CELLS:
        findings.append(
            Finding(
                CODE_PARTIAL_WITHOUT_GAP,
                row.feature,
                row.line_number,
                "partial coverage must say exactly what is still missing",
            )
        )

    if row.status == STATUS_COVERED and row.required_level > LEVEL_NONE and not row.external_evidence:
        evidence_proofs = [inspect_path(project, declared) for declared in row.evidence_paths]
        best = max((proof.level for proof in proofs + evidence_proofs), default=LEVEL_NONE)
        if best < row.required_level:
            findings.append(
                Finding(
                    CODE_EVIDENCE_WEAKER_THAN_DECLARED,
                    row.feature,
                    row.line_number,
                    f"row declares '{row.type_cell.strip()}' "
                    f"({LEVEL_NAMES[row.required_level]}) but the strongest real test found is "
                    f"{LEVEL_NAMES[best]}",
                )
            )

    if row.status == STATUS_NOT_USER_FACING:
        findings.extend(evaluate_not_user_facing(row))

    if row.status == STATUS_EXCEPTION:
        findings.extend(evaluate_exception(row))

    return findings


def evaluate_not_user_facing(row: Row) -> list[Finding]:
    notes = normalize_text(row.notes_cell)
    states_reason = "not user-facing" in notes or "not user facing" in notes or "internal only" in notes
    if notes in PLACEHOLDER_CELLS or not states_reason:
        return [
            Finding(
                CODE_UNJUSTIFIED_NOT_USER_FACING,
                row.feature,
                row.line_number,
                "a not-user-facing row must state the reason it has no human surface",
            )
        ]
    if _row_claims_a_human_role(row):
        return [
            Finding(
                CODE_UNJUSTIFIED_NOT_USER_FACING,
                row.feature,
                row.line_number,
                f"row names the human role '{row.role_cell.strip()}', so it cannot also be not-user-facing",
            )
        ]
    return []


def evaluate_exception(row: Row) -> list[Finding]:
    notes = normalize_text(row.notes_cell)
    approver = APPROVAL_PATTERN.search(row.notes_cell or "")
    reason = next((allowed for allowed in ALLOWED_EXCEPTION_REASONS if allowed in notes), None)
    if approver and reason:
        return []
    problems = []
    if not approver:
        problems.append("no named approver ('approved by <name>')")
    if not reason:
        problems.append(
            "no allowed reason (" + ", ".join(ALLOWED_EXCEPTION_REASONS) + ")"
        )
    return [
        Finding(
            CODE_EXCEPTION_WITHOUT_APPROVAL,
            row.feature,
            row.line_number,
            "coverage exception is not acceptable: " + "; ".join(problems),
        )
    ]


def evaluate_release(row: Row) -> list[Finding]:
    """A release may only carry rows that are proved or formally excused."""
    if row.status in (STATUS_COVERED, STATUS_EXCEPTION, STATUS_NOT_USER_FACING):
        return []
    if row.status == STATUS_UNKNOWN:
        # Already reported as an unreadable claim by the integrity rules.
        return []
    return [
        Finding(
            CODE_RELEASE_WITHOUT_PROOF,
            row.feature,
            row.line_number,
            f"release requires covered, a named approved exception, or an explicit "
            f"not-user-facing decision; this row is '{row.status_cell.strip() or row.status}'",
        )
    ]


# ──────────────────────────────────────────────────────────────────────────────
# Runner
# ──────────────────────────────────────────────────────────────────────────────


def run(
    project: Path | str,
    mode: str,
    changed_files: list[str] | None = None,
    previous_manifest_text: str | None = None,
    manifest_text: str | None = None,
) -> Report:
    project = Path(project).resolve()
    manifest = project / MANIFEST_NAME

    if manifest_text is None:
        if not manifest.is_file():
            return Report(
                mode=mode,
                state=STATE_UNAVAILABLE,
                manifest_path=None,
                rows_total=0,
                rows_in_scope=0,
                findings=(
                    [
                        Finding(
                            CODE_MANIFEST_UNAVAILABLE,
                            "-",
                            0,
                            f"no {MANIFEST_NAME} in {project}; a release cannot be proved without one",
                        )
                    ]
                    if mode == MODE_RELEASE
                    else []
                ),
                notes=[
                    f"no {MANIFEST_NAME} in {project}: coverage enforcement reported as "
                    "unavailable, not as passed"
                ],
                summary_counts={},
            )
        manifest_text = read_text_safely(manifest)

    rows = parse_manifest(manifest_text)
    if not rows:
        manifest_touched = changed_files is None or any(
            Path(changed).name == MANIFEST_NAME for changed in changed_files
        )
        findings = []
        if mode == MODE_RELEASE or manifest_touched:
            findings.append(
                Finding(
                    CODE_MANIFEST_UNAVAILABLE,
                    "-",
                    0,
                    f"{MANIFEST_NAME} has no parseable coverage table; add a table with "
                    "Feature, Status and Test File columns",
                )
            )
        return Report(
            mode=mode,
            state=STATE_UNAVAILABLE,
            manifest_path=str(manifest),
            rows_total=0,
            rows_in_scope=0,
            findings=findings,
            notes=[f"{manifest} has no parseable coverage rows"],
            summary_counts={},
        )

    if mode == MODE_MANIFEST or changed_files is None:
        scoped = rows
    else:
        previous_rows = parse_manifest(previous_manifest_text) if previous_manifest_text is not None else None
        scoped = rows_in_scope(rows, changed_files, previous_rows)

    counts: dict[str, int] = {}
    for row in scoped:
        counts[row.status] = counts.get(row.status, 0) + 1
        if row.external_evidence:
            counts["external-evidence"] = counts.get("external-evidence", 0) + 1

    findings: list[Finding] = []
    for row in scoped:
        findings.extend(evaluate_integrity(project, row))
        if mode == MODE_RELEASE:
            findings.extend(evaluate_release(row))

    notes: list[str] = []
    if mode in (MODE_CHANGE, MODE_RELEASE):
        notes.append(
            f"{len(scoped)} of {len(rows)} manifest rows are in scope for this change; "
            "untouched rows are reported by --mode manifest, not blocked here"
        )

    return Report(
        mode=mode,
        state=STATE_OK,
        manifest_path=str(manifest),
        rows_total=len(rows),
        rows_in_scope=len(scoped),
        findings=findings,
        notes=notes,
        summary_counts=counts,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Git helpers and CLI
# ──────────────────────────────────────────────────────────────────────────────


def git(project: Path, *args: str) -> tuple[int, str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=project,
            capture_output=True,
            text=True,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return 1, ""
    return result.returncode, result.stdout


def staged_changed_files(project: Path) -> list[str] | None:
    code, out = git(project, "rev-parse", "--is-inside-work-tree")
    if code != 0 or out.strip() != "true":
        return None
    code, out = git(project, "diff", "--cached", "--name-only")
    if code != 0:
        return None
    return [line.strip() for line in out.splitlines() if line.strip()]


def base_changed_files(project: Path, base: str) -> list[str] | None:
    code, _ = git(project, "rev-parse", "--verify", base)
    if code != 0:
        return None
    code, out = git(project, "diff", "--name-only", f"{base}...HEAD")
    if code != 0:
        code, out = git(project, "diff", "--name-only", base)
        if code != 0:
            return None
    return [line.strip() for line in out.splitlines() if line.strip()]


def manifest_text_at(project: Path, revision: str) -> str | None:
    code, out = git(project, "show", f"{revision}:{MANIFEST_NAME}")
    if code != 0:
        return None
    return out


def format_report(report: Report) -> str:
    lines: list[str] = []
    for note in report.notes:
        lines.append(f"NOTE  {note}")

    if report.summary_counts:
        summary = ", ".join(f"{name}={count}" for name, count in sorted(report.summary_counts.items()))
        lines.append(f"ROWS  {summary}")

    for finding in report.findings:
        lines.append(f"FAIL  {finding.code} (line {finding.line_number}) {finding.feature}: {finding.detail}")

    if report.state == STATE_UNAVAILABLE and report.ok:
        lines.append(
            f"TEST COVERAGE ENFORCEMENT: UNAVAILABLE (mode={report.mode}) "
            "no manifest to enforce; reported, not assumed passed"
        )
    elif report.ok:
        lines.append(
            f"TEST COVERAGE ENFORCEMENT: PASS (mode={report.mode}, "
            f"rows_in_scope={report.rows_in_scope}/{report.rows_total}, findings=0)"
        )
    else:
        lines.append(
            f"TEST COVERAGE ENFORCEMENT: FAIL (mode={report.mode}, "
            f"rows_in_scope={report.rows_in_scope}/{report.rows_total}, "
            f"findings={len(report.findings)})"
        )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Enforce a project's TESTING.md coverage decisions.",
    )
    parser.add_argument("--project", default=".", help="Project directory containing TESTING.md")
    parser.add_argument("--mode", choices=MODES, default=MODE_MANIFEST, help="Which gate to run")
    parser.add_argument("--staged", action="store_true", help="Scope to files staged in git")
    parser.add_argument("--base", help="Scope to files changed since this git ref")
    parser.add_argument(
        "--changed-file",
        action="append",
        default=[],
        dest="changed_file",
        help="Scope to an explicit path (repeatable)",
    )
    parser.add_argument("--json", action="store_true", help="Emit the report as JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    project = Path(args.project).resolve()
    if not project.is_dir():
        print(f"TEST COVERAGE ENFORCEMENT: ERROR project {project} is not a directory")
        return 2

    changed_files: list[str] | None = None
    previous_manifest_text: str | None = None

    if args.mode in (MODE_CHANGE, MODE_RELEASE):
        if not (args.staged or args.base or args.changed_file):
            parser.error(
                f"--mode {args.mode} needs a change source: --staged, --base <ref>, or --changed-file <path>"
            )

        if args.changed_file:
            changed_files = list(args.changed_file)
        elif args.staged:
            changed_files = staged_changed_files(project)
            if changed_files is None:
                print(
                    "TEST COVERAGE ENFORCEMENT: UNAVAILABLE (mode=%s) not a git work tree; "
                    "staged scope could not be read" % args.mode
                )
                return 0
            previous_manifest_text = manifest_text_at(project, "HEAD")
        else:
            changed_files = base_changed_files(project, args.base)
            if changed_files is None:
                print(
                    "TEST COVERAGE ENFORCEMENT: UNAVAILABLE (mode=%s) base ref '%s' is not "
                    "resolvable here" % (args.mode, args.base)
                )
                return 0 if args.mode != MODE_RELEASE else 2
            previous_manifest_text = manifest_text_at(project, args.base)

    report = run(
        project=project,
        mode=args.mode,
        changed_files=changed_files,
        previous_manifest_text=previous_manifest_text,
    )

    if args.json:
        print(json.dumps(report.as_dict(), indent=2))
    else:
        print(format_report(report))

    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
