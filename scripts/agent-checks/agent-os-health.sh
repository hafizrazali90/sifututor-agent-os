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
check_file "working with Hafiz" "$ROOT/docs/agent-playbooks/working-with-hafiz.md"
check_file "Agent OS routing model" "$ROOT/docs/agent-playbooks/agent-os-routing-model.md"
check_file "Agent OS approval gates" "$ROOT/docs/agent-playbooks/agent-os-approval-gates.md"
check_file "Agent OS communication" "$ROOT/docs/agent-playbooks/agent-os-communication.md"
check_file "internal build plan" "$ROOT/docs/agent-playbooks/agent-os-internal-build-plan.md"
check_file "context authority" "$ROOT/docs/agent-playbooks/context-authority.md"
check_file "Agent OS evals" "$ROOT/docs/agent-playbooks/agent-os-evals.md"
check_file "Agent OS memory" "$ROOT/docs/agent-playbooks/agent-os-memory.md"
check_file "Agent OS memory architecture" "$ROOT/docs/agent-playbooks/agent-os-memory-architecture.md"
check_file "Agent OS capability model" "$ROOT/docs/agent-playbooks/agent-os-capability-model.md"
check_file "Agent OS workflow lanes" "$ROOT/docs/agent-playbooks/agent-os-workflow-lanes.md"
check_file "Agent OS evidence model" "$ROOT/docs/agent-playbooks/agent-os-evidence-model.md"
check_file "Agent OS state model" "$ROOT/docs/agent-playbooks/agent-os-state-model.md"
check_file "Agent OS rollout readiness" "$ROOT/docs/agent-playbooks/agent-os-rollout-readiness.md"
check_file "Agent OS eval coverage" "$ROOT/docs/agent-playbooks/agent-os-eval-coverage-map.md"
check_file "Koda CLI" "$ROOT/scripts/agent-checks/koda"
check_file "Agent OS install doc" "$ROOT/docs/agent-playbooks/agent-os-installation.md"
check_file "Agent OS install manifest" "$ROOT/docs/agent-playbooks/agent-os-install-manifest.json"
check_file "Agent OS installer" "$ROOT/scripts/agent-checks/agent-os-install.sh"
check_file "Agent OS eval runner" "$ROOT/scripts/agent-checks/agent-os-eval-runner.py"
check_file "capability example" "$ROOT/docs/agent-playbooks/capabilities.example.json"

if "$ROOT/scripts/agent-checks/agent-os-eval-runner.py" >/tmp/agent-os-eval-runner.out 2>/tmp/agent-os-eval-runner.err; then
  eval_summary="$(tail -1 /tmp/agent-os-eval-runner.out 2>/dev/null || true)"
  pass "Agent OS evals" "${eval_summary:-passed}"
else
  fail "Agent OS evals" "routing/behavior eval runner failed"
  sed -n '1,12p' /tmp/agent-os-eval-runner.out 2>/dev/null || true
  sed -n '1,8p' /tmp/agent-os-eval-runner.err 2>/dev/null || true
fi
rm -f /tmp/agent-os-eval-runner.out /tmp/agent-os-eval-runner.err

if "$ROOT/scripts/agent-checks/agent-os-eval-runner.py" --self-test >/tmp/agent-os-eval-self-test.out 2>/tmp/agent-os-eval-self-test.err; then
  self_test_summary="$(tail -1 /tmp/agent-os-eval-self-test.out 2>/dev/null || true)"
  pass "Agent OS eval self-test" "${self_test_summary:-passed}"
else
  fail "Agent OS eval self-test" "negative eval self-test failed"
  sed -n '1,12p' /tmp/agent-os-eval-self-test.out 2>/dev/null || true
  sed -n '1,8p' /tmp/agent-os-eval-self-test.err 2>/dev/null || true
fi
rm -f /tmp/agent-os-eval-self-test.out /tmp/agent-os-eval-self-test.err

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
if "$ROOT/scripts/agent-checks/koda" health >/tmp/agent-os-koda-check.out 2>/tmp/agent-os-koda-check.err; then
  pass "Koda direct health" "pass"
else
  warn "Koda direct health" "failed or unavailable"
  sed -n '1,8p' /tmp/agent-os-koda-check.err 2>/dev/null || true
fi
rm -f /tmp/agent-os-koda-check.out /tmp/agent-os-koda-check.err

echo
echo "Capability Summary"
echo "- filesystem: available if workspace write detected above"
echo "- git status/diff: available if git repo detected above"
echo "- git commit: blocked until exact file-list approval and guard checks"
echo "- git push / PR / merge: blocked until explicit current-session approval"
echo "- koda: available through CLI if direct health passed; chat MCP wrapper is optional"
echo "- github: unknown unless a session-specific tool is connected"
echo "- plane: unknown unless a session-specific tool is connected"
echo "- planner: unknown unless a session-specific tool is connected"
echo "- google_drive: unknown unless a session-specific tool is connected"
echo "- production_logs: unknown unless a session-specific tool is connected"
echo "- deploy: blocked or not_connected by default; explicit approval required"

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
