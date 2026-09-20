#!/usr/bin/env bash
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PROJECTS=(
  kelas
  sifu-tutor
  ripple-suite
  sifututor_tutor
  sifututor_parent
  lls
  lls-frontend
  lls-mobile
  creative-hub
  finch-inbox
  cx-call-capture-android
  sims-owner-analytics
)
# issue 103: active projects whose Claude/Codex adapter rollout is not finished
# yet. They stay in PROJECTS so the live registry is complete, but a missing
# adapter file is reported as a warning instead of a failure.
ADAPTER_PENDING=(
  cx-call-capture-android
  sims-owner-analytics
)
SKILLS=(
  task-router
  verify
  qa
  sims-ui-audit
  commit
  save-session
  handoff
  snapshot
  session-map
  diagnose
  review
  quick-check
  workflow-improvement
)

failures=0
warnings=0
existing_projects=()

pass() {
  printf 'PASS %-24s %s\n' "$1" "$2"
}

warn() {
  printf 'WARN %-24s %s\n' "$1" "$2"
  warnings=$((warnings + 1))
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
echo "Agent OS health"
health_out="$(mktemp)"
health_err="$(mktemp)"
if "$ROOT/scripts/agent-checks/agent-os-health.sh" >"$health_out" 2>"$health_err"; then
  pass "agent os health" "passed"
else
  fail "agent os health" "failed"
  grep '^FAIL ' "$health_out" | sed -n '1,8p' || true
  sed -n '1,4p' "$health_err" || true
fi
rm -f "$health_out" "$health_err"

echo
echo "Projects"
for project in "${PROJECTS[@]}"; do
  dir="$ROOT/$project"
  [[ -d "$dir" ]] || { warn "$project" "directory missing; skipped"; continue; }
  existing_projects+=("$project")
  [[ -f "$dir/AGENTS.md" ]] && ag="AGENTS" || ag="missing AGENTS"
  [[ -f "$dir/CLAUDE.md" ]] && cl="CLAUDE" || cl="missing CLAUDE"
  [[ -f "$dir/.claude/tasks/active.json" ]] && ac="active" || ac="missing active"
  [[ -d "$dir/.claude/hooks" ]] && hk="hooks" || hk="missing hooks"
  pending=0
  for candidate in "${ADAPTER_PENDING[@]}"; do
    [[ "$candidate" == "$project" ]] && pending=1
  done
  if [[ "$ag $cl $ac $hk" == "AGENTS CLAUDE active hooks" ]]; then
    pass "$project" "$ag, $cl, $ac, $hk"
  elif [[ "$pending" -eq 1 ]]; then
    warn "$project" "adapter rollout pending: $ag, $cl, $ac, $hk"
  else
    fail "$project" "$ag, $cl, $ac, $hk"
  fi
  if [[ -f "$dir/.claude/tasks/active.json" ]]; then
    python3 -m json.tool "$dir/.claude/tasks/active.json" >/dev/null 2>&1 \
      && pass "$project active json" "valid" \
      || fail "$project active json" "invalid"
  fi
done

if [[ "${#existing_projects[@]}" -eq 0 ]]; then
  if [[ -f "$ROOT/.git" ]]; then
    warn "projects" "standalone Git worktree; product project checks skipped"
  else
    fail "projects" "no product project directories found"
  fi
fi

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

python3 "$ROOT/scripts/agent-checks/session-map-check.py" >/dev/null 2>&1 \
  && pass "session map check" "passed" \
  || fail "session map check" "failed"

python3 "$ROOT/scripts/agent-checks/session-map-html.py" "$ROOT/docs/agent-playbooks/templates/session-map.md" -o /tmp/sifututor-session-map-doctor.html >/dev/null 2>&1 \
  && pass "session map html" "passed" \
  || fail "session map html" "failed"
rm -f /tmp/sifututor-session-map-doctor.html

echo
echo "All-project guard sweep"
if [[ "${#existing_projects[@]}" -eq 0 ]]; then
  warn "project guards" "no product projects in this checkout; skipped"
else
  for project in "${existing_projects[@]}"; do
    if (cd "$ROOT/$project" && "$ROOT/scripts/agent-checks/pre-commit-guard.sh" >/dev/null 2>&1); then
      pass "$project guard" "passed"
    else
      fail "$project guard" "failed"
    fi
  done
fi

echo
echo "Codex prompt visibility"
if command -v codex >/dev/null 2>&1; then
  prompt_file="$(mktemp)"
  if codex debug prompt-input '$quick-check' >"$prompt_file" 2>/dev/null; then
    if grep -q "quick-check" "$prompt_file" &&
      grep -q "save-session" "$prompt_file"; then
      pass "codex skills" "visible in prompt input"
    else
      fail "codex skills" "not visible in prompt input"
    fi
  else
    warn "codex cli" "installed but debug prompt-input failed; repair global Codex install"
  fi
  rm -f "$prompt_file"
else
  warn "codex cli" "not found; skipped live Codex prompt visibility"
fi

echo
echo "Claude parent config"
claude_args=("$ROOT")
if [[ "${#existing_projects[@]}" -gt 0 ]]; then
  claude_args+=("${existing_projects[@]}")
fi
python3 - "${claude_args[@]}" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
projects = sys.argv[2:]
settings_path = root / ".claude/settings.json"
if not settings_path.is_file():
    print("NO_ROOT_SETTINGS")
    raise SystemExit(2)
settings = json.loads(settings_path.read_text())
missing = [p for p in projects if p not in settings.get("additionalDirectories", [])]
if missing:
    print("MISSING " + ", ".join(missing))
    raise SystemExit(1)
print("OK")
PY
claude_status=$?
if [[ "$claude_status" -eq 0 ]]; then
  pass "claude dirs" "all projects present"
elif [[ "$claude_status" -eq 2 ]]; then
  warn "claude dirs" "root .claude/settings.json missing; project-level Claude settings checked above"
else
  fail "claude dirs" "missing projects"
fi

echo
if [[ "$failures" -eq 0 ]]; then
  echo "WORKFLOW DOCTOR: PASS ($warnings warning(s))"
  exit 0
fi

echo "WORKFLOW DOCTOR: FAIL ($failures issue(s), $warnings warning(s))"
exit 1
