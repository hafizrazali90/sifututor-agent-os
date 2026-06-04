#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MANIFEST="$ROOT/docs/agent-playbooks/agent-os-install-manifest.json"
TARGET="$ROOT"
APPLY=0
failures=0
warnings=0
changes=0

pass() {
  printf 'PASS %-28s %s\n' "$1" "$2"
}

warn() {
  printf 'WARN %-28s %s\n' "$1" "$2"
  warnings=$((warnings + 1))
}

fail() {
  printf 'FAIL %-28s %s\n' "$1" "$2"
  failures=$((failures + 1))
}

usage() {
  cat <<'EOF'
Sifututor Agent OS installer/checker

Usage:
  scripts/agent-checks/agent-os-install.sh [--target PATH] [--dry-run|--apply]

Defaults:
  --target current umbrella root
  --dry-run

Rules:
  - Dry-run never writes files.
  - Apply creates missing project baseline files only.
  - Existing files are never overwritten.
  - Targets under live/ are refused.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET="${2:-}"
      shift 2
      ;;
    --target=*)
      TARGET="${1#--target=}"
      shift
      ;;
    --apply)
      APPLY=1
      shift
      ;;
    --dry-run)
      APPLY=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "argument" "unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$TARGET" ]]; then
  fail "target" "empty target path"
  exit 1
fi

if [[ "$TARGET" != /* ]]; then
  TARGET="$ROOT/$TARGET"
fi

TARGET="$(cd "$(dirname "$TARGET")" 2>/dev/null && pwd)/$(basename "$TARGET")"

echo "Sifututor Agent OS Install Check"
echo "Root: $ROOT"
echo "Target: $TARGET"
if [[ "$APPLY" -eq 1 ]]; then
  echo "Mode: apply missing baseline files"
else
  echo "Mode: dry-run"
fi
echo

if [[ "$TARGET" == "$ROOT/live"* || "$TARGET" == *"/live/"* ]]; then
  fail "target" "refusing live/ target"
  echo
  echo "AGENT OS INSTALL: FAIL ($failures issue(s), $warnings warning(s))"
  exit 1
fi

if [[ ! -f "$MANIFEST" ]]; then
  fail "manifest" "$MANIFEST missing"
  echo
  echo "AGENT OS INSTALL: FAIL ($failures issue(s), $warnings warning(s))"
  exit 1
fi

if python3 -m json.tool "$MANIFEST" >/dev/null 2>&1; then
  pass "manifest" "valid JSON"
else
  fail "manifest" "invalid JSON"
fi

json_list() {
  local key="$1"
  python3 - "$MANIFEST" "$key" <<'PY'
import json
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text())
value = manifest
for part in sys.argv[2].split("."):
    value = value[part]
for item in value:
    print(item)
PY
}

check_root_file() {
  local rel="$1"
  if [[ -f "$ROOT/$rel" ]]; then
    pass "umbrella file" "$rel"
  else
    fail "umbrella file" "$rel missing"
  fi
}

check_target_file() {
  local rel="$1"
  if [[ -f "$TARGET/$rel" ]]; then
    pass "target file" "$rel"
  else
    fail "target file" "$rel missing"
  fi
}

check_target_recommended() {
  local rel="$1"
  if [[ -f "$TARGET/$rel" ]]; then
    pass "recommended file" "$rel"
  else
    warn "recommended file" "$rel missing"
  fi
}

write_if_missing() {
  local rel="$1"
  local content="$2"
  local path="$TARGET/$rel"

  if [[ -f "$path" ]]; then
    pass "existing file" "$rel"
    return
  fi

  if [[ "$APPLY" -eq 0 ]]; then
    warn "would create" "$rel"
    return
  fi

  mkdir -p "$(dirname "$path")"
  printf '%s' "$content" >"$path"
  pass "created" "$rel"
  changes=$((changes + 1))
}

echo "Umbrella Baseline"
while IFS= read -r rel; do
  check_root_file "$rel"
done < <(json_list "umbrella_required_files")

echo
echo "Codex Skills"
while IFS= read -r rel; do
  check_root_file "$rel"
done < <(json_list "codex_skill_files")

echo
echo "Shared Hooks"
while IFS= read -r rel; do
  check_root_file "$rel"
done < <(json_list "shared_hook_files")

echo
echo "Target Baseline"
if [[ -d "$TARGET" ]]; then
  pass "target" "directory exists"
else
  fail "target" "directory missing"
fi

if [[ -d "$TARGET" ]] && (cd "$TARGET" && git rev-parse --is-inside-work-tree >/dev/null 2>&1); then
  pass "target git" "yes"
else
  warn "target git" "not detected"
fi

if [[ "$TARGET" == "$ROOT" ]]; then
  pass "target baseline" "umbrella root; project baseline skipped"
  echo
  echo "Health"
  if "$ROOT/scripts/agent-checks/agent-os-health.sh" >/dev/null 2>&1; then
    pass "agent os health" "passed"
  else
    warn "agent os health" "failed or unavailable"
  fi

  echo
  if [[ "$failures" -eq 0 ]]; then
    echo "AGENT OS INSTALL: PASS ($warnings warning(s), $changes file(s) created)"
    exit 0
  fi

  echo "AGENT OS INSTALL: FAIL ($failures issue(s), $warnings warning(s), $changes file(s) created)"
  exit 1
fi

while IFS= read -r rel; do
  check_target_file "$rel"
done < <(json_list "project_baseline.required_existing_files")

while IFS= read -r rel; do
  check_target_recommended "$rel"
done < <(json_list "project_baseline.recommended_existing_files")

settings_json='{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "model": "opusplan",
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 '"$ROOT"'/.claude/hooks/koda-context-injector.py",
            "timeout": 3
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 '"$ROOT"'/.claude/hooks/validate-branch-name.py"
          },
          {
            "type": "command",
            "command": "python3 '"$ROOT"'/.claude/hooks/conventional-commits.py"
          },
          {
            "type": "command",
            "command": "python3 '"$ROOT"'/.claude/hooks/test-coverage-gate.py"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 '"$ROOT"'/.claude/hooks/friction-logger.py",
            "timeout": 3
          }
        ]
      }
    ]
  }
}
'

hooks_readme='# Project Hooks

This project uses shared Sifututor Agent OS hooks from the umbrella workspace.

Keep project-specific hooks here only when this project needs behavior that
cannot be shared safely across the workspace.
'

active_json='{
  "activeTask": null,
  "taskFile": null,
  "route": null
}
'

schema_md='# Task State Schema

`active.json` is the shared Claude/Codex active task pointer for this project.

When there is no active task:

```json
{
  "activeTask": null,
  "taskFile": null,
  "route": null
}
```

Use the umbrella playbooks for routing, verification, QA, commit, and
save-session.
'

echo
echo "Project Files"
write_if_missing ".claude/settings.json" "$settings_json"
write_if_missing ".claude/hooks/README.md" "$hooks_readme"
write_if_missing ".claude/tasks/active.json" "$active_json"
write_if_missing ".claude/tasks/SCHEMA.md" "$schema_md"
write_if_missing ".claude/tasks/archive/.gitkeep" ""

echo
echo "Health"
if "$ROOT/scripts/agent-checks/agent-os-health.sh" >/dev/null 2>&1; then
  pass "agent os health" "passed"
else
  warn "agent os health" "failed or unavailable"
fi

echo
if [[ "$failures" -eq 0 ]]; then
  echo "AGENT OS INSTALL: PASS ($warnings warning(s), $changes file(s) created)"
  exit 0
fi

echo "AGENT OS INSTALL: FAIL ($failures issue(s), $warnings warning(s), $changes file(s) created)"
exit 1
