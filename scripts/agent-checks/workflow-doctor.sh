#!/usr/bin/env bash
set -u

ROOT="/Users/hafizrazali/Projects/Sifututor"
PROJECTS=(
  sifu-tutor
  ripple-suite
  sifututor_tutor
  sifututor_parent
  lls
  lls-frontend
  lls-mobile
  creative-hub
  team-inbox
  finch-inbox
)
SKILLS=(
  task-router
  verify
  qa
  commit
  save-session
  handoff
  snapshot
  diagnose
  review
  quick-check
)

failures=0

pass() {
  printf 'PASS %-24s %s\n' "$1" "$2"
}

fail() {
  printf 'FAIL %-24s %s\n' "$1" "$2"
  failures=$((failures + 1))
}

check_file() {
  local label="$1"
  local path="$2"
  if [[ -f "$path" ]]; then
    pass "$label" "$path"
  else
    fail "$label" "$path missing"
  fi
}

cd "$ROOT" || {
  echo "FAIL root cannot cd to $ROOT"
  exit 1
}

echo "Sifututor workflow doctor"
echo "Root: $ROOT"
echo

check_file "root AGENTS" "$ROOT/AGENTS.md"
check_file "codex config" "$ROOT/.codex/config.toml"
check_file "parity status" "$ROOT/docs/agent-playbooks/parity-status.md"

echo
echo "Projects"
for project in "${PROJECTS[@]}"; do
  dir="$ROOT/$project"
  [[ -d "$dir" ]] || { fail "$project" "directory missing"; continue; }
  [[ -f "$dir/AGENTS.md" ]] && ag="AGENTS" || ag="missing AGENTS"
  [[ -f "$dir/CLAUDE.md" ]] && cl="CLAUDE" || cl="missing CLAUDE"
  [[ -f "$dir/.claude/tasks/active.json" ]] && ac="active" || ac="missing active"
  [[ -d "$dir/.claude/hooks" ]] && hk="hooks" || hk="missing hooks"
  if [[ "$ag $cl $ac $hk" == "AGENTS CLAUDE active hooks" ]]; then
    pass "$project" "$ag, $cl, $ac, $hk"
  else
    fail "$project" "$ag, $cl, $ac, $hk"
  fi
  if [[ -f "$dir/.claude/tasks/active.json" ]]; then
    python3 -m json.tool "$dir/.claude/tasks/active.json" >/dev/null 2>&1 \
      && pass "$project active json" "valid" \
      || fail "$project active json" "invalid"
  fi
done

echo
echo "Codex skills"
for skill in "${SKILLS[@]}"; do
  check_file "skill $skill" "$ROOT/.agents/skills/$skill/SKILL.md"
done

echo
echo "Scripts"
python3 -m py_compile "$ROOT"/scripts/agent-checks/*.py >/dev/null 2>&1 \
  && pass "python hooks" "py_compile ok" \
  || fail "python hooks" "py_compile failed"

"$ROOT/scripts/agent-checks/pre-commit-guard.sh" >/dev/null 2>&1 \
  && pass "root guard" "passed" \
  || fail "root guard" "failed"

echo
echo "All-project guard sweep"
for project in "${PROJECTS[@]}"; do
  if (cd "$ROOT/$project" && "$ROOT/scripts/agent-checks/pre-commit-guard.sh" >/dev/null 2>&1); then
    pass "$project guard" "passed"
  else
    fail "$project guard" "failed"
  fi
done

echo
echo "Codex prompt visibility"
if command -v codex >/dev/null 2>&1; then
  prompt_file="$(mktemp)"
  if codex debug prompt-input '$quick-check' >"$prompt_file" 2>/dev/null &&
    grep -q "quick-check" "$prompt_file" &&
    grep -q "save-session" "$prompt_file"; then
    pass "codex skills" "visible in prompt input"
  else
    fail "codex skills" "not visible in prompt input"
  fi
  rm -f "$prompt_file"
else
  fail "codex cli" "not found"
fi

echo
echo "Claude parent config"
python3 - "$ROOT" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
projects = [
    "sifu-tutor", "ripple-suite", "sifututor_tutor", "sifututor_parent",
    "lls", "lls-frontend", "lls-mobile", "creative-hub", "team-inbox",
    "finch-inbox",
]
settings = json.loads((root / ".claude/settings.json").read_text())
missing = [p for p in projects if p not in settings.get("additionalDirectories", [])]
if missing:
    print("MISSING " + ", ".join(missing))
    raise SystemExit(1)
print("OK")
PY
if [[ $? -eq 0 ]]; then
  pass "claude dirs" "all projects present"
else
  fail "claude dirs" "missing projects"
fi

echo
if [[ "$failures" -eq 0 ]]; then
  echo "WORKFLOW DOCTOR: PASS"
  exit 0
fi

echo "WORKFLOW DOCTOR: FAIL ($failures issue(s))"
exit 1
