#!/usr/bin/env bash
set -u

ROOT="/Users/hafizrazali/Projects/Sifututor"
failures=0

pass() {
  printf 'PASS %-28s %s\n' "$1" "$2"
}

warn() {
  printf 'WARN %-28s %s\n' "$1" "$2"
}

fail() {
  printf 'FAIL %-28s %s\n' "$1" "$2"
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

echo "Sifututor Agent OS Health"
echo "Root: $ROOT"
echo

if [[ -d "$ROOT" ]]; then
  pass "workspace" "found"
else
  fail "workspace" "missing"
  echo
  echo "AGENT OS HEALTH: FAIL ($failures issue(s))"
  exit 1
fi

cd "$ROOT" || {
  fail "workspace" "cannot cd to $ROOT"
  echo
  echo "AGENT OS HEALTH: FAIL ($failures issue(s))"
  exit 1
}

echo "Detected"
check_file "root AGENTS" "$ROOT/AGENTS.md"
check_file "Agent OS overview" "$ROOT/docs/agent-playbooks/agent-os.md"
check_file "Agent OS quick start" "$ROOT/docs/agent-playbooks/agent-os-quick-start.md"
check_file "internal build plan" "$ROOT/docs/agent-playbooks/agent-os-internal-build-plan.md"
check_file "context authority" "$ROOT/docs/agent-playbooks/context-authority.md"
check_file "Agent OS evals" "$ROOT/docs/agent-playbooks/agent-os-evals.md"
check_file "Agent OS memory" "$ROOT/docs/agent-playbooks/agent-os-memory.md"
check_file "Agent OS install doc" "$ROOT/docs/agent-playbooks/agent-os-installation.md"
check_file "Agent OS install manifest" "$ROOT/docs/agent-playbooks/agent-os-install-manifest.json"
check_file "Agent OS installer" "$ROOT/scripts/agent-checks/agent-os-install.sh"
check_file "capability example" "$ROOT/docs/agent-playbooks/capabilities.example.json"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  pass "git repo" "yes"
  branch="$(git branch --show-current 2>/dev/null || true)"
  if [[ -n "$branch" ]]; then
    pass "git branch" "$branch"
  else
    warn "git branch" "detached or unavailable"
  fi
else
  fail "git repo" "not detected"
fi

tmp_file="$ROOT/.agent-os-health.tmp"
if : >"$tmp_file" 2>/dev/null; then
  rm -f "$tmp_file"
  pass "filesystem write" "workspace write available"
else
  warn "filesystem write" "not available in workspace"
fi

if [[ -f "$ROOT/.claude/tasks/active.json" ]]; then
  if python3 -m json.tool "$ROOT/.claude/tasks/active.json" >/dev/null 2>&1; then
    pass "active task" "valid active.json present"
  else
    fail "active task" "active.json invalid"
  fi
else
  pass "active task" "none"
fi

echo
echo "Koda"
if python3 "$ROOT/scripts/agent-checks/codex-lifecycle-hook.py" --check-koda >/tmp/agent-os-koda-check.out 2>/tmp/agent-os-koda-check.err; then
  pass "Koda direct health" "pass"
else
  warn "Koda direct health" "failed or unavailable"
  sed -n '1,8p' /tmp/agent-os-koda-check.err 2>/dev/null || true
fi
rm -f /tmp/agent-os-koda-check.out /tmp/agent-os-koda-check.err

echo
echo "Capability Summary"
echo "- filesystem: workspace_write if detected above"
echo "- git: local_write if git repo detected above"
echo "- koda: read_write if direct health passed"
echo "- github: unknown unless a session-specific tool is connected"
echo "- plane: unknown unless a session-specific tool is connected"
echo "- planner: unknown unless a session-specific tool is connected"
echo "- google_drive: unknown unless a session-specific tool is connected"
echo "- deploy: none by default"

echo
echo "Approval Required"
echo "- commit: exact file-list approval"
echo "- push / PR / merge: explicit current-session approval"
echo "- deploy: explicit current-session approval"
echo "- critical-lane implementation: diagnosis first, then approval"

echo
echo "Never Allowed"
echo "- read or modify .env* files"
echo "- modify live/"
echo "- bypass hooks or tests with --no-verify"
echo "- reveal, commit, or copy secret values"

echo
if [[ "$failures" -eq 0 ]]; then
  echo "AGENT OS HEALTH: PASS"
  exit 0
fi

echo "AGENT OS HEALTH: FAIL ($failures issue(s))"
exit 1
