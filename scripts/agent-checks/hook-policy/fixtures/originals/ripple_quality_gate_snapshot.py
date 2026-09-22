#!/usr/bin/env python3
"""
FROZEN FIXTURE SNAPSHOT — not a live hook, not imported by hook-policy.

Byte-for-byte copy of ~/Projects/Sifututor/ripple-suite/.claude/hooks/quality-gate.py
as read on 2026-09-22, for issue #161 parity testing only (see
scripts/agent-checks/hook-policy/fixtures/originals/README.md and
scripts/agent-checks/hook-policy/SURVEY.md). Exercised only via
subprocess.run(...) from tests/test_parity_quality_gate.py. If the real
sub-project file changes, this snapshot goes stale until manually re-synced.

Original docstring follows unmodified below.
---
quality-gate.py — PreToolUse hook for ripple-suite
Reminds developer to run lint + build when TypeScript files are staged for commit.

This is a WARNING hook (not a hard block) — it reminds, not prevents.
Hard enforcement (verify/qa steps) is handled by workflow-gate.py.

Adapted from sifututor_tutor/.claude/hooks/quality-gate.py (React Native version).
Key differences for Next.js/TypeScript (ripple-suite):
  - Checks src/ directory (Next.js App Router layout)
  - Warns to run `npm run lint && npm run build` (not `npm run check`)
  - Critical paths match Next.js patterns (API routes, auth, payments, migrations)
  - Uses hookSpecificOutput ask_user for code changes, plain stderr for minor warnings
"""
import json
import sys
import os
import subprocess

try:
    input_data = json.load(sys.stdin)
except (json.JSONDecodeError, EOFError):
    sys.exit(0)

tool_name = input_data.get("tool_name", "")
tool_input = input_data.get("tool_input", {})
command = tool_input.get("command", "")

# Only gate git commit commands
if tool_name != "Bash" or "git commit" not in command:
    sys.exit(0)

# --no-verify bypasses all checks (explicit user override)
if "--no-verify" in command:
    sys.exit(0)

# Project root: hooks dir is .claude/hooks/, go up 2 levels
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))


def get_staged_files():
    """Get list of staged files."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except Exception:
        return []


def get_ts_files(files):
    """Return only TypeScript/JavaScript source files from staged list."""
    return [f for f in files if f.endswith((".ts", ".tsx", ".js", ".jsx"))]


def has_code_changes(files):
    """Check if staged files include source code under Next.js directories."""
    code_extensions = {".ts", ".tsx", ".js", ".jsx"}
    code_dirs = {
        "src/",
        "app/",
        "pages/",
        "components/",
        "lib/",
        "hooks/",
        "utils/",
        "types/",
        "modules/",
    }
    for f in files:
        _, ext = os.path.splitext(f)
        if ext in code_extensions:
            for d in code_dirs:
                if f.startswith(d):
                    return True
    return False


def has_critical_changes(files):
    """
    Check if staged files touch critical paths in ripple-suite.
    Critical = auth, payments, migrations, middleware, API routes.
    """
    critical_paths = [
        "src/middleware.ts",
        "src/lib/db.ts",
        "src/lib/db-neon.ts",
        "src/lib/db-helpers.ts",
        "src/lib/migrations/",
        "src/app/api/auth/",
        "src/app/api/tutor-payments/",
        "src/modules/tutor-payments/",
        "src/modules/accounts/",
        "src/modules/reconciliation/",
        "src/lib/api-logger.ts",
    ]
    for f in files:
        for cp in critical_paths:
            if f.startswith(cp) or f == cp:
                return True
    return False


# --- Main Logic ---

staged = get_staged_files()
if not staged:
    sys.exit(0)  # Nothing staged, allow

ts_files = get_ts_files(staged)

if not ts_files:
    sys.exit(0)  # No TS/JS files staged, allow

# Check 1: If code changes exist, ask user to confirm lint + build ran
if has_code_changes(staged):
    file_list = "\n".join(f"  • {f}" for f in ts_files[:15])
    if len(ts_files) > 15:
        file_list += f"\n  ... and {len(ts_files) - 15} more"

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask_user",
            "permissionDecisionReason": (
                f"⚠️  Quality Gate: {len(ts_files)} TypeScript/JS file(s) staged.\n\n"
                "Confirm lint and build passed before committing:\n"
                "  npm run lint && npm run build\n\n"
                "Staged TS/JS files:\n"
                + file_list
                + "\n\nProceed with commit anyway? (Run git commit --no-verify to bypass.)"
            ),
        }
    }
    print(json.dumps(output))
    sys.exit(0)

# Check 2: Critical paths require explicit acknowledgment
if has_critical_changes(staged):
    critical_files = []
    critical_paths = [
        "src/middleware.ts",
        "src/lib/db.ts",
        "src/lib/db-neon.ts",
        "src/lib/db-helpers.ts",
        "src/lib/migrations/",
        "src/app/api/auth/",
        "src/app/api/tutor-payments/",
        "src/modules/tutor-payments/",
        "src/modules/accounts/",
        "src/modules/reconciliation/",
        "src/lib/api-logger.ts",
    ]
    for f in staged:
        for cp in critical_paths:
            if f.startswith(cp) or f == cp:
                critical_files.append(f)
                break

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask_user",
            "permissionDecisionReason": (
                "🔴 Critical Path Quality Gate\n\n"
                "These staged files touch critical paths (auth, payments, DB, migrations):\n"
                + "\n".join(f"  • {f}" for f in critical_files)
                + "\n\nBefore committing, confirm:\n"
                "  1. npm run lint passed (0 errors)\n"
                "  2. npm run build passed (no type errors)\n"
                "  3. Relevant Playwright tests green\n"
                "  4. If migrations: applied to staging Neon before push\n\n"
                "Proceed with commit?"
            ),
        }
    }
    print(json.dumps(output))
    sys.exit(0)

# All checks passed — allow
sys.exit(0)
