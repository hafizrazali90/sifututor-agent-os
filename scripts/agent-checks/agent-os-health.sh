#!/usr/bin/env bash
set -u

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
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
check_file "Agent OS infrastructure" "$ROOT/docs/agent-playbooks/agent-os-infrastructure.md"
check_file "Agent OS parity contract" "$ROOT/docs/agent-playbooks/agent-os-parity-contract.md"
check_file "Agent OS roles" "$ROOT/docs/agent-playbooks/agent-os-roles.md"
check_file "Agent OS skill registry" "$ROOT/docs/agent-playbooks/agent-os-skill-registry.md"
check_file "Agent OS hook dispatcher" "$ROOT/docs/agent-playbooks/agent-os-hook-dispatcher.md"
check_file "Agent OS quick start" "$ROOT/docs/agent-playbooks/agent-os-quick-start.md"
check_file "working with Hafiz" "$ROOT/docs/agent-playbooks/working-with-hafiz.md"
check_file "Agent OS routing model" "$ROOT/docs/agent-playbooks/agent-os-routing-model.md"
check_file "Agent OS approval gates" "$ROOT/docs/agent-playbooks/agent-os-approval-gates.md"
check_file "push PR CI automation" "$ROOT/docs/agent-playbooks/push-pr-ci-automation.md"
check_file "release deploy live monitoring" "$ROOT/docs/agent-playbooks/release-deploy-live-monitoring.md"
check_file "incident workflow" "$ROOT/docs/agent-playbooks/incident-workflow.md"
check_file "project adoption" "$ROOT/docs/agent-playbooks/project-adoption.md"
check_file "workflow efficiency audit" "$ROOT/docs/agent-playbooks/workflow-efficiency-audit.md"
check_file "Agent OS communication" "$ROOT/docs/agent-playbooks/agent-os-communication.md"
check_file "internal build plan" "$ROOT/docs/agent-playbooks/agent-os-internal-build-plan.md"
check_file "context authority" "$ROOT/docs/agent-playbooks/context-authority.md"
check_file "Agent OS evals" "$ROOT/docs/agent-playbooks/agent-os-evals.md"
check_file "Agent OS memory" "$ROOT/docs/agent-playbooks/agent-os-memory.md"
check_file "Agent OS memory architecture" "$ROOT/docs/agent-playbooks/agent-os-memory-architecture.md"
check_file "Agent OS capability model" "$ROOT/docs/agent-playbooks/agent-os-capability-model.md"
check_file "Agent OS workflow lanes" "$ROOT/docs/agent-playbooks/agent-os-workflow-lanes.md"
check_file "Agent OS workflows" "$ROOT/docs/agent-playbooks/agent-os-workflows.md"
check_file "Agent OS governance" "$ROOT/docs/agent-playbooks/agent-os-governance.md"
check_file "Agent OS improvement loop" "$ROOT/docs/agent-playbooks/agent-os-improvement-loop.md"
check_file "Agent OS evidence model" "$ROOT/docs/agent-playbooks/agent-os-evidence-model.md"
check_file "Agent OS state model" "$ROOT/docs/agent-playbooks/agent-os-state-model.md"
check_file "Agent OS enforcement drift" "$ROOT/docs/agent-playbooks/agent-os-enforcement-drift.md"
check_file "Agent OS session map" "$ROOT/docs/agent-playbooks/session-map.md"
check_file "Agent OS rollout readiness" "$ROOT/docs/agent-playbooks/agent-os-rollout-readiness.md"
check_file "Agent OS eval coverage" "$ROOT/docs/agent-playbooks/agent-os-eval-coverage-map.md"
check_file "Agent OS evaluation harness" "$ROOT/docs/agent-playbooks/agent-os-evaluation-harness.md"
check_file "related impact audit" "$ROOT/docs/agent-playbooks/related-impact-audit.md"
check_file "Koda CLI" "$ROOT/scripts/agent-checks/koda"
check_file "Agent OS install doc" "$ROOT/docs/agent-playbooks/agent-os-installation.md"
check_file "Agent OS install manifest" "$ROOT/docs/agent-playbooks/agent-os-install-manifest.json"
check_file "Agent OS installer" "$ROOT/scripts/agent-checks/agent-os-install.sh"
check_file "Agent OS eval runner" "$ROOT/scripts/agent-checks/agent-os-eval-runner.py"
check_file "Agent OS response shape" "$ROOT/scripts/agent-checks/agent-os-response-shape-runner.py"
check_file "Agent OS state fixtures" "$ROOT/scripts/agent-checks/agent-os-state-fixture-runner.py"
check_file "Agent OS session map check" "$ROOT/scripts/agent-checks/session-map-check.py"
check_file "Agent OS session map HTML" "$ROOT/scripts/agent-checks/session-map-html.py"
check_file "Agent OS Koda fixtures" "$ROOT/scripts/agent-checks/agent-os-koda-fixture-runner.py"
check_file "Agent OS capability fixtures" "$ROOT/scripts/agent-checks/agent-os-capability-fixture-runner.py"
check_file "Agent OS conversation fixtures" "$ROOT/scripts/agent-checks/agent-os-conversation-fixture-runner.py"
check_file "Agent OS parity fixtures" "$ROOT/scripts/agent-checks/agent-os-parity-fixture-runner.py"
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

if "$ROOT/scripts/agent-checks/agent-os-response-shape-runner.py" >/tmp/agent-os-response-shape.out 2>/tmp/agent-os-response-shape.err; then
  response_shape_summary="$(tail -1 /tmp/agent-os-response-shape.out 2>/dev/null || true)"
  pass "Agent OS response shape" "${response_shape_summary:-passed}"
else
  fail "Agent OS response shape" "response-shape runner failed"
  sed -n '1,12p' /tmp/agent-os-response-shape.out 2>/dev/null || true
  sed -n '1,8p' /tmp/agent-os-response-shape.err 2>/dev/null || true
fi
rm -f /tmp/agent-os-response-shape.out /tmp/agent-os-response-shape.err

if "$ROOT/scripts/agent-checks/agent-os-state-fixture-runner.py" >/tmp/agent-os-state-fixtures.out 2>/tmp/agent-os-state-fixtures.err; then
  state_fixture_summary="$(tail -1 /tmp/agent-os-state-fixtures.out 2>/dev/null || true)"
  pass "Agent OS state fixtures" "${state_fixture_summary:-passed}"
else
  fail "Agent OS state fixtures" "state fixture runner failed"
  sed -n '1,12p' /tmp/agent-os-state-fixtures.out 2>/dev/null || true
  sed -n '1,8p' /tmp/agent-os-state-fixtures.err 2>/dev/null || true
fi
rm -f /tmp/agent-os-state-fixtures.out /tmp/agent-os-state-fixtures.err

if python3 "$ROOT/scripts/agent-checks/session-map-check.py" >/tmp/agent-os-session-map.out 2>/tmp/agent-os-session-map.err; then
  session_map_summary="$(tail -1 /tmp/agent-os-session-map.out 2>/dev/null || true)"
  pass "Agent OS session map check" "${session_map_summary:-passed}"
else
  fail "Agent OS session map check" "session-map checker failed"
  sed -n '1,12p' /tmp/agent-os-session-map.out 2>/dev/null || true
  sed -n '1,8p' /tmp/agent-os-session-map.err 2>/dev/null || true
fi
rm -f /tmp/agent-os-session-map.out /tmp/agent-os-session-map.err

if python3 "$ROOT/scripts/agent-checks/session-map-html.py" "$ROOT/docs/agent-playbooks/templates/session-map.md" -o /tmp/agent-os-session-map.html >/tmp/agent-os-session-map-html.out 2>/tmp/agent-os-session-map-html.err; then
  html_summary="$(tail -1 /tmp/agent-os-session-map-html.out 2>/dev/null || true)"
  pass "Agent OS session map HTML" "${html_summary:-passed}"
else
  fail "Agent OS session map HTML" "HTML generator failed"
  sed -n '1,12p' /tmp/agent-os-session-map-html.out 2>/dev/null || true
  sed -n '1,8p' /tmp/agent-os-session-map-html.err 2>/dev/null || true
fi
rm -f /tmp/agent-os-session-map.html /tmp/agent-os-session-map-html.out /tmp/agent-os-session-map-html.err

if "$ROOT/scripts/agent-checks/agent-os-koda-fixture-runner.py" >/tmp/agent-os-koda-fixtures.out 2>/tmp/agent-os-koda-fixtures.err; then
  koda_fixture_summary="$(tail -1 /tmp/agent-os-koda-fixtures.out 2>/dev/null || true)"
  pass "Agent OS Koda fixtures" "${koda_fixture_summary:-passed}"
else
  fail "Agent OS Koda fixtures" "Koda fixture runner failed"
  sed -n '1,12p' /tmp/agent-os-koda-fixtures.out 2>/dev/null || true
  sed -n '1,8p' /tmp/agent-os-koda-fixtures.err 2>/dev/null || true
fi
rm -f /tmp/agent-os-koda-fixtures.out /tmp/agent-os-koda-fixtures.err

if "$ROOT/scripts/agent-checks/agent-os-capability-fixture-runner.py" >/tmp/agent-os-capability-fixtures.out 2>/tmp/agent-os-capability-fixtures.err; then
  capability_fixture_summary="$(tail -1 /tmp/agent-os-capability-fixtures.out 2>/dev/null || true)"
  pass "Agent OS capability fixtures" "${capability_fixture_summary:-passed}"
else
  fail "Agent OS capability fixtures" "capability fixture runner failed"
  sed -n '1,12p' /tmp/agent-os-capability-fixtures.out 2>/dev/null || true
  sed -n '1,8p' /tmp/agent-os-capability-fixtures.err 2>/dev/null || true
fi
rm -f /tmp/agent-os-capability-fixtures.out /tmp/agent-os-capability-fixtures.err

if "$ROOT/scripts/agent-checks/agent-os-conversation-fixture-runner.py" >/tmp/agent-os-conversation-fixtures.out 2>/tmp/agent-os-conversation-fixtures.err; then
  conversation_fixture_summary="$(tail -1 /tmp/agent-os-conversation-fixtures.out 2>/dev/null || true)"
  pass "Agent OS conversation fixtures" "${conversation_fixture_summary:-passed}"
else
  fail "Agent OS conversation fixtures" "conversation fixture runner failed"
  sed -n '1,12p' /tmp/agent-os-conversation-fixtures.out 2>/dev/null || true
  sed -n '1,8p' /tmp/agent-os-conversation-fixtures.err 2>/dev/null || true
fi
rm -f /tmp/agent-os-conversation-fixtures.out /tmp/agent-os-conversation-fixtures.err

if "$ROOT/scripts/agent-checks/agent-os-parity-fixture-runner.py" >/tmp/agent-os-parity-fixtures.out 2>/tmp/agent-os-parity-fixtures.err; then
  parity_fixture_summary="$(tail -1 /tmp/agent-os-parity-fixtures.out 2>/dev/null || true)"
  pass "Agent OS parity fixtures" "${parity_fixture_summary:-passed}"
else
  fail "Agent OS parity fixtures" "parity fixture runner failed"
  sed -n '1,12p' /tmp/agent-os-parity-fixtures.out 2>/dev/null || true
  sed -n '1,8p' /tmp/agent-os-parity-fixtures.err 2>/dev/null || true
fi
rm -f /tmp/agent-os-parity-fixtures.out /tmp/agent-os-parity-fixtures.err

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
echo "- plane: exception-only; do not use unless Hafiz explicitly asks in the current session"
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
