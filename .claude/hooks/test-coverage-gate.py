#!/usr/bin/env python3
"""
test-coverage-gate.py — PreToolUse(Bash) hook

Fires when git push is detected. Checks whether critical user-facing files
changed in the current branch have corresponding test coverage declared in
TESTING.md. If a coverage gap is found:

  - First 2 times: warn with an educational message (does NOT block the push)
  - 3rd+ time for the same gap: hard-block until the gap is resolved

Gap state is tracked in .claude/coverage-gaps.log so repeat offenders
accumulate across sessions.

Stack-agnostic — works for Laravel, React Native, Next.js, React SPA projects.

TESTING.md manifest table format expected (any columns in this order):
  | Feature / User Story | Source Files | Test File(s) | Type | Status |
  |---|---|---|---|---|
  | Login flow | app/Http/Controllers/Auth/ | tests/Feature/AuthTest.php | Feature | ✅ |

The hook resolves the project root by looking for the nearest TESTING.md
above cwd (walks up to /Users/hafizrazali/Projects/Sifututor).

Hard constraints:
  - Silent on non-push commands
  - Never hard-blocks on first or second offense (warn only)
  - Never hard-blocks when TESTING.md does not exist (skips gracefully)
  - Stdlib only — no third-party deps
  - Append-only gap log — never rewrites past entries
"""

import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

WORKSPACE_ROOT = Path(
    os.environ.get("SIFUTUTOR_AGENT_OS_ROOT", Path(__file__).resolve().parents[2])
).resolve()
GAP_LOG_RELATIVE = Path(".claude/coverage-gaps.log")

# Hard-block threshold: same gap seen this many times → deny
HARD_BLOCK_THRESHOLD = 3

# Files in these directories are considered critical user-facing paths.
# A changed file must match at least one of these patterns to be checked.
CRITICAL_PATH_PATTERNS = [
    # Laravel
    r"app/Http/Controllers/",
    r"app/Models/",
    r"app/Services/",
    r"app/Repositories/",
    r"app/Jobs/",
    r"routes/",
    # React Native / React SPA
    r"src/screens/",
    r"src/pages/",
    r"src/components/",
    r"src/hooks/",
    r"src/api/",
    r"src/store/",
    r"src/context/",
    r"src/services/",
    # Next.js
    r"app/",
    r"pages/",
    r"components/",
    r"lib/",
    r"actions/",
    r"server/",
    # General
    r"src/",
]

# Files matching these patterns are always ignored — not user-facing code.
IGNORE_PATTERNS = [
    r"\.md$",
    r"\.json$",
    r"\.lock$",
    r"\.log$",
    r"\.env",
    r"\.gitignore",
    r"\.claude/",
    r"docs/",
    r"\.github/",
    r"node_modules/",
    r"vendor/",
    r"storage/",
    r"public/",
    r"__pycache__/",
    r"\.test\.",
    r"\.spec\.",
    r"_test\.",
    r"tests/",
    r"test/",
    r"__tests__/",
]

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────


def _detect_push(command: str) -> bool:
    """Return True if the command contains a git push."""
    return bool(re.search(r'\bgit\s+push\b', command))


def _find_project_root(start: Path) -> Path | None:
    """Walk up from start looking for TESTING.md or .git, capped at WORKSPACE_ROOT."""
    candidate = start.resolve()
    ceiling = WORKSPACE_ROOT.resolve()
    while True:
        if (candidate / "TESTING.md").exists():
            return candidate
        if (candidate / ".git").exists():
            return candidate
        if candidate == ceiling or candidate.parent == candidate:
            return None
        candidate = candidate.parent


def _read_testing_md(project_root: Path) -> str | None:
    testing_path = project_root / "TESTING.md"
    if not testing_path.exists():
        return None
    try:
        return testing_path.read_text(encoding="utf-8")
    except OSError:
        return None


def _parse_manifest(content: str) -> list[dict]:
    """
    Parse TESTING.md markdown tables into feature rows.

    Each row becomes:
      { "feature": str, "sources": [str, ...], "tests": [str, ...], "status": str }

    Columns are matched positionally from the header row of each table.
    Only tables that contain a column named "source" or "file" (case-insensitive)
    in their header are parsed.
    """
    rows = []
    lines = content.splitlines()
    header: list[str] | None = None

    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            header = None
            continue
        # Separator row (|---|---|) — reset header pointer
        if re.match(r'^\|[-| :]+\|$', stripped):
            continue
        # Parse pipe-separated cells.
        # Split on "|" then strip each part — but preserve empty internal cells
        # (they represent intentionally blank table cells).  Drop only the leading
        # and trailing empty strings produced by the surrounding "|…|" delimiters.
        raw_parts = [c.strip() for c in stripped.split("|")]
        # raw_parts[0] and raw_parts[-1] are always "" for a valid markdown row
        if len(raw_parts) >= 2:
            cells = raw_parts[1:-1]
        else:
            cells = raw_parts
        if not cells:
            continue
        # Header detection: only attempt when we don't already have a header for
        # this table. A data row may also contain "feature" (e.g. a test path
        # "tests/Feature/…"), so we must not re-trigger once header is set.
        lower_cells = [c.lower() for c in cells]
        if header is None:
            if any("feature" in c or "user story" in c or "scenario" in c for c in lower_cells):
                header = lower_cells
            continue

        # Map known columns
        def _col(name: str) -> str:
            for fragment in name.split("|"):
                for i, h in enumerate(header):
                    if fragment.strip() in h:
                        return cells[i] if i < len(cells) else ""
            return ""

        feature = _col("feature|user story|scenario|description")
        sources_raw = _col("source|file|path|implementation")
        tests_raw = _col("test|spec|coverage")
        status = _col("status|coverage|done")

        # Split multi-value cells on comma, newline, space
        def _split(raw: str) -> list[str]:
            if not raw:
                return []
            parts = re.split(r"[,\s]+", raw.strip())
            return [p.strip() for p in parts if p.strip() and p != "|"]

        rows.append({
            "feature": feature,
            "sources": _split(sources_raw),
            "tests": _split(tests_raw),
            "status": status,
        })

    return rows


def _get_changed_files(project_root: Path) -> list[str]:
    """
    Return files changed in current branch vs the branch's merge base with
    main or integration. Falls back to HEAD~1 diff if no base branch found.
    """
    try:
        # Discover base branch
        for base in ("main", "integration", "master", "develop"):
            result = subprocess.run(
                ["git", "rev-parse", "--verify", base],
                cwd=project_root,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                merge_base = subprocess.run(
                    ["git", "merge-base", "HEAD", base],
                    cwd=project_root,
                    capture_output=True,
                    text=True,
                )
                if merge_base.returncode == 0:
                    diff = subprocess.run(
                        ["git", "diff", "--name-only", merge_base.stdout.strip(), "HEAD"],
                        cwd=project_root,
                        capture_output=True,
                        text=True,
                    )
                    if diff.returncode == 0:
                        return [f for f in diff.stdout.splitlines() if f.strip()]
        # Fallback: diff HEAD~1
        diff = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        return [f for f in diff.stdout.splitlines() if f.strip()]
    except Exception:
        return []


def _is_critical(path: str) -> bool:
    """True if the file path matches a critical user-facing pattern AND is not ignored."""
    for ignore in IGNORE_PATTERNS:
        if re.search(ignore, path):
            return False
    for critical in CRITICAL_PATH_PATTERNS:
        if re.search(critical, path):
            return True
    return False


def _file_has_coverage(filepath: str, manifest: list[dict]) -> tuple[bool, str]:
    """
    Return (covered, reason).
    covered=True  → at least one manifest row declares coverage and status is ✅/pass/done
    covered=False → file is critical with no test entry, or has an entry with failing status

    Matching strategy (stack-agnostic keyword matching):
      1. Direct substring match: filepath in row["sources"]
      2. Basename match
      3. Directory component match (e.g., "Auth" matches "AuthController.php")
      4. Feature keyword match (e.g., "login" in "LoginController.php")
    """
    basename = Path(filepath).name
    parts = set(Path(filepath).parts)
    lower_path = filepath.lower()

    for row in manifest:
        matched = False
        # Source path matching
        for src in row["sources"]:
            src_lower = src.lower()
            if (src_lower in filepath.lower()
                    or filepath.lower() in src_lower
                    or basename.lower() in src_lower
                    or src_lower in basename.lower()):
                matched = True
                break
        # Keyword match via feature name
        if not matched and row["feature"]:
            words = re.findall(r'[a-z]{3,}', row["feature"].lower())
            for word in words:
                if word in lower_path:
                    matched = True
                    break

        if matched:
            # Check if tests are declared
            if not row["tests"]:
                return False, f"Feature '{row['feature']}' maps to this file but has NO test entries."
            # Check status
            status = row["status"].lower()
            if any(x in status for x in ["❌", "✗", "fail", "missing", "none", "no"]):
                return False, (
                    f"Feature '{row['feature']}' maps to this file "
                    f"but test status is: {row['status']}"
                )
            return True, f"Covered under '{row['feature']}'"

    return False, "No TESTING.md entry found for this file."


def _gap_log_path(project_root: Path) -> Path:
    return project_root / GAP_LOG_RELATIVE


def _load_gap_counts(log_path: Path) -> dict[str, int]:
    """Parse the gap log and return {gap_key: warn_count}."""
    counts: dict[str, int] = {}
    if not log_path.exists():
        return counts
    try:
        for line in log_path.read_text(encoding="utf-8").splitlines():
            m = re.search(r'\[GAP\]\s+(.+?)\s*\|', line)
            if m:
                key = m.group(1).strip()
                counts[key] = counts.get(key, 0) + 1
    except OSError:
        pass
    return counts


def _append_gap_log(log_path: Path, entries: list[tuple[str, str]]) -> None:
    """Append gap entries: list of (gap_key, reason)."""
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with log_path.open("a", encoding="utf-8") as f:
            for key, reason in entries:
                f.write(f"[{timestamp}] [GAP] {key} | {reason}\n")
    except OSError:
        pass


def _current_branch(project_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _format_warning(
    gaps: list[dict],
    branch: str,
    project_root: Path,
    hard_block_gaps: list[dict],
) -> str:
    """
    Build the educational warning message shown to Claude/the user.

    gaps:            all gaps found this push
    hard_block_gaps: subset that have crossed HARD_BLOCK_THRESHOLD
    """
    gap_log_display = project_root / GAP_LOG_RELATIVE

    lines = []
    lines.append("=" * 72)
    lines.append("  TEST COVERAGE GATE — Coverage Gaps Detected")
    lines.append("=" * 72)
    lines.append(f"  Branch : {branch}")
    lines.append(f"  Project: {project_root.name}")
    lines.append(f"  Gap log: {gap_log_display}")
    lines.append("")

    if hard_block_gaps:
        lines.append("  🔴  HARD BLOCK — Repeat Offender Gaps (seen 3+ times)")
        lines.append("  " + "-" * 68)
        lines.append("  These gaps were warned in prior pushes and remain unresolved.")
        lines.append("  You MUST add test coverage before this push can proceed.")
        lines.append("")
        for g in hard_block_gaps:
            lines.append(f"  • {g['file']}")
            lines.append(f"    Reason  : {g['reason']}")
            lines.append(f"    Seen    : {g['count']} times (threshold: {HARD_BLOCK_THRESHOLD})")
            lines.append("")

    warn_only_gaps = [g for g in gaps if g not in hard_block_gaps]
    if warn_only_gaps:
        lines.append("  🟡  WARNING — New / Low-Count Coverage Gaps")
        lines.append("  " + "-" * 68)
        lines.append("  Push is NOT blocked yet. Fix before the 3rd repeat.")
        lines.append("")
        for g in warn_only_gaps:
            lines.append(f"  • {g['file']}")
            lines.append(f"    Reason  : {g['reason']}")
            lines.append(f"    Seen    : {g['count']} time(s)")
            lines.append("")

    lines.append("  HOW TO RESOLVE")
    lines.append("  " + "-" * 68)
    lines.append("  1. Open TESTING.md in your project root.")
    lines.append("  2. Locate or add a row in the manifest table for the feature")
    lines.append("     that the changed file implements.")
    lines.append("  3. Add a test file reference in the 'Test File(s)' column.")
    lines.append("  4. Mark the 'Status' column ✅ once the test passes.")
    lines.append("")
    lines.append("  TESTING.md table format:")
    lines.append("  | Feature / User Story | Source Files | Test File(s) | Type | Status |")
    lines.append("  |---|---|---|---|---|")
    lines.append("  | Login flow | app/Http/Controllers/Auth/ | tests/Feature/AuthTest.php | Feature | ✅ |")
    lines.append("")
    lines.append("  WHY THIS MATTERS")
    lines.append("  " + "-" * 68)
    lines.append("  User-facing code without a declared test is invisible to QA.")
    lines.append("  TESTING.md is the single source of truth for what is covered.")
    lines.append("  A gap today becomes a regression tomorrow.")
    lines.append("=" * 72)

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────


def main():
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")
    cwd_str = input_data.get("cwd", "") or os.environ.get("CLAUDE_PROJECT_DIR", "") or os.getcwd()

    # Only act on git push
    if tool_name != "Bash" or not _detect_push(command):
        sys.exit(0)

    # Skip pushes that are explicitly dry-run or no-op
    if "--dry-run" in command or "-n " in command:
        sys.exit(0)

    cwd = Path(cwd_str).resolve()
    project_root = _find_project_root(cwd)
    if project_root is None:
        sys.exit(0)

    # Read TESTING.md — skip gracefully if absent
    content = _read_testing_md(project_root)
    if content is None:
        sys.exit(0)

    manifest = _parse_manifest(content)
    if not manifest:
        # TESTING.md exists but has no parseable manifest — skip
        sys.exit(0)

    changed_files = _get_changed_files(project_root)
    critical_files = [f for f in changed_files if _is_critical(f)]
    if not critical_files:
        sys.exit(0)

    # Find gaps
    raw_gaps: list[tuple[str, str]] = []  # (filepath, reason)
    for filepath in critical_files:
        covered, reason = _file_has_coverage(filepath, manifest)
        if not covered:
            raw_gaps.append((filepath, reason))

    if not raw_gaps:
        sys.exit(0)

    # Load historical gap counts
    log_path = _gap_log_path(project_root)
    gap_counts = _load_gap_counts(log_path)

    # Build gap dicts with counts
    gaps = []
    for filepath, reason in raw_gaps:
        key = filepath
        prior_count = gap_counts.get(key, 0)
        gaps.append({
            "file": filepath,
            "reason": reason,
            "key": key,
            "count": prior_count + 1,  # including this push
        })

    # Persist new gap entries
    _append_gap_log(log_path, [(g["key"], g["reason"]) for g in gaps])

    # Separate hard-block gaps from warn-only gaps
    hard_block_gaps = [g for g in gaps if g["count"] >= HARD_BLOCK_THRESHOLD]
    branch = _current_branch(project_root)

    message = _format_warning(gaps, branch, project_root, hard_block_gaps)

    if hard_block_gaps:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": message,
            }
        }
        print(json.dumps(output))
        sys.exit(0)

    # Warn-only: output informational message but allow the push
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": message,
        }
    }
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
