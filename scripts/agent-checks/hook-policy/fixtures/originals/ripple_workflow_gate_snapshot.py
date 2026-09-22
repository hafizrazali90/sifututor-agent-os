#!/usr/bin/env python3
"""
FROZEN FIXTURE SNAPSHOT — not a live hook, not imported by hook-policy.

Byte-for-byte copy of ~/Projects/Sifututor/ripple-suite/.claude/hooks/workflow-gate.py
as read on 2026-09-22, for issue #161 parity testing only (see
scripts/agent-checks/hook-policy/fixtures/originals/README.md and
scripts/agent-checks/hook-policy/SURVEY.md). Exercised only via
subprocess.run(...) from tests/test_parity_workflow_gate.py. If the real
sub-project file changes, this snapshot goes stale until manually re-synced.

Original docstring follows unmodified below.
---
Workflow gate: enforce mandatory workflow steps before git commit.

Checks active task state and blocks commit if required steps are not done.
Mandatory (unskippable) steps checked here:
  - verify          : lint + build must pass
  - qa              : tests must run at route's required tier
  - regression_test : RED→GREEN proof required on hotfix and bugfix routes
  - defect_analysis : bug classified + structural test + Koda lesson on hotfix and bugfix
  - release_notes   : CHANGELOG + help text + What's New (on hotfix, bugfix, feature, small-change)

Skippable steps are allowed to be force-skipped by the user (recorded in state).
The hook fires on PreToolUse for any `git commit` command.
"""
import json
import sys
import os

try:
    input_data = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
    sys.exit(1)

tool_name = input_data.get("tool_name", "")
tool_input = input_data.get("tool_input", {})
command = tool_input.get("command", "")

# Only intercept git commit commands
if tool_name != "Bash" or "git commit" not in command:
    sys.exit(0)

# --no-verify bypasses all workflow gates (explicit user override)
if "--no-verify" in command:
    sys.exit(0)

# Locate the project root (where .claude/tasks/active.json lives)
# Walk up from the hook file location
hook_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(hook_dir))  # .claude/ -> project root
active_path = os.path.join(project_root, ".claude", "tasks", "active.json")

if not os.path.exists(active_path):
    sys.exit(0)

try:
    with open(active_path) as f:
        active = json.load(f)
except Exception:
    sys.exit(0)

task_file = active.get("taskFile")
if not task_file:
    sys.exit(0)

task_path = os.path.join(project_root, task_file)
if not os.path.exists(task_path):
    sys.exit(0)

try:
    with open(task_path) as f:
        task = json.load(f)
except Exception:
    sys.exit(0)

route = task.get("route", "")
steps = task.get("steps", [])

def get_step(name):
    for s in steps:
        if s.get("name") == name:
            return s
    return None

def step_done(name):
    s = get_step(name)
    return s is not None and s.get("status") == "done"

def step_skipped(name):
    s = get_step(name)
    return s is not None and s.get("status") == "skipped"

def step_exists(name):
    return get_step(name) is not None

blocked_reasons = []

# --- verify: unskippable on all routes ---
if step_exists("verify") and not step_done("verify") and not step_skipped("verify"):
    blocked_reasons.append(
        "• verify not done — run `npm run lint && npm run build` and pass `/verify` first."
    )

# --- qa: unskippable on all routes that have it ---
if step_exists("qa") and not step_done("qa") and not step_skipped("qa"):
    qa_tier = task.get("qaTier", "smoke")
    blocked_reasons.append(
        f"• qa not done — run `/qa` at the '{qa_tier}' tier first."
    )

# --- regression_test: unskippable on hotfix and bugfix routes ---
REGRESSION_TEST_ROUTES = {"hotfix", "bugfix"}
if route in REGRESSION_TEST_ROUTES:
    rt = get_step("regression_test")
    if rt is not None:
        status = rt.get("status", "blocked")
        if status not in ("done", "skipped"):
            blocked_reasons.append(
                "• regression_test not done — write a failing test (RED) before fixing,\n"
                "  then confirm GREEN. Run /regression-test to continue."
            )
        elif status == "done":
            evidence = rt.get("evidence", {})
            red = str(evidence.get("red_output", "")).strip()
            green = str(evidence.get("green_output", "")).strip()
            if not red or not green:
                blocked_reasons.append(
                    "• regression_test evidence incomplete — red_output and green_output\n"
                    "  must both be present. Re-run /regression-test to record the proof."
                )

# --- defect_analysis: unskippable on hotfix and bugfix routes ---
DEFECT_ANALYSIS_ROUTES = {"hotfix", "bugfix"}
if route in DEFECT_ANALYSIS_ROUTES:
    da = get_step("defect_analysis")
    if da is not None:
        status = da.get("status", "blocked")
        if status not in ("done", "skipped"):
            blocked_reasons.append(
                "• defect_analysis not done — classify bug type, update structural test,\n"
                "  store Koda lesson. Run /defect-analysis to continue."
            )

# --- release_notes: required on hotfix, bugfix, feature, small-change ---
RELEASE_NOTES_ROUTES = {"hotfix", "bugfix", "feature", "small-change"}
if route in RELEASE_NOTES_ROUTES:
    rn = get_step("release_notes")
    if rn is not None:
        status = rn.get("status", "blocked")
        if status not in ("done", "skipped"):
            blocked_reasons.append(
                "• release_notes not done — complete before committing:\n"
                "    (1) CHANGELOG.md entry\n"
                "    (2) help text update (if user-facing change)\n"
                "    (3) What's New seed script (if visible to staff)\n"
                "  Mark done in the task state file or run the release_notes step."
            )
        elif status == "skipped":
            # Skipped is allowed — warn in output but don't block
            pass  # warning printed by ripple-commit skill instead

if not blocked_reasons:
    sys.exit(0)

task_desc = task.get("description", active.get("activeTask", "unknown"))
reasons_text = "\n".join(blocked_reasons)

reason = f"""Commit blocked — workflow gate failed for task: {task_desc}

{reasons_text}

Complete the missing steps first. To bypass all checks (emergency only), add --no-verify.
To mark a step done manually, update the task state file at: {task_file}"""

output = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason
    }
}
print(json.dumps(output))
sys.exit(0)
