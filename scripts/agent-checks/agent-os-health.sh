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

check_max_bytes() {
  local label="$1"
  local path="$2"
  local maximum="$3"
  local actual
  if [[ ! -f "$path" ]]; then
    return
  fi
  actual="$(wc -c < "$path" | tr -d ' ')"
  if (( actual <= maximum )); then
    pass "$label" "$actual/$maximum bytes"
  else
    fail "$label" "$actual bytes exceeds $maximum-byte budget"
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

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/agent-os-health.XXXXXX")"
trap 'rm -rf "$TMP_DIR"' EXIT

echo "Detected"
check_file "root AGENTS" "$ROOT/AGENTS.md"
check_max_bytes "root AGENTS budget" "$ROOT/AGENTS.md" 16384
check_max_bytes "task router budget" "$ROOT/docs/agent-playbooks/task-router.md" 12288
check_file "Kilo Agent OS adapter" "$ROOT/.kilo/agents/sifututor-agent-os.md"
check_file "Agent OS overview" "$ROOT/docs/agent-playbooks/agent-os.md"
check_file "Agent OS infrastructure" "$ROOT/docs/agent-playbooks/agent-os-infrastructure.md"
check_file "Agent OS parity contract" "$ROOT/docs/agent-playbooks/agent-os-parity-contract.md"
check_file "Agent OS roles" "$ROOT/docs/agent-playbooks/agent-os-roles.md"
check_file "Agent OS multi-agent workflow" "$ROOT/docs/agent-playbooks/multi-agent-adapter-workflow.md"
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
check_file "SIMS UI audit playbook" "$ROOT/docs/agent-playbooks/sims-ui-audit.md"
check_file "Agent OS state model" "$ROOT/docs/agent-playbooks/agent-os-state-model.md"
check_file "Agent OS enforcement drift" "$ROOT/docs/agent-playbooks/agent-os-enforcement-drift.md"
check_file "Agent OS session map" "$ROOT/docs/agent-playbooks/session-map.md"
check_file "Agent OS rollout readiness" "$ROOT/docs/agent-playbooks/agent-os-rollout-readiness.md"
check_file "Agent OS eval coverage" "$ROOT/docs/agent-playbooks/agent-os-eval-coverage-map.md"
check_file "Agent OS evaluation harness" "$ROOT/docs/agent-playbooks/agent-os-evaluation-harness.md"
check_file "Agent OS scenario lab" "$ROOT/docs/agent-playbooks/agent-os-scenario-lab.md"
check_file "related impact audit" "$ROOT/docs/agent-playbooks/related-impact-audit.md"
check_file "live evidence template" "$ROOT/docs/agent-playbooks/templates/live-evidence-probe-report.md"
check_file "Koda CLI" "$ROOT/scripts/agent-checks/koda"
check_file "worktree inventory" "$ROOT/scripts/agent-checks/worktree-inventory.sh"
check_file "worktree lifecycle" "$ROOT/scripts/agent-checks/worktree-lifecycle.py"
check_file "worktree lifecycle fixtures" "$ROOT/scripts/agent-checks/test_worktree_lifecycle.py"
check_file "Claude hook dispatcher" "$ROOT/scripts/agent-checks/claude_hook_dispatch.py"
check_file "Claude hook dispatcher fixtures" "$ROOT/scripts/agent-checks/test_claude_hook_dispatch.py"
check_file "Claude quality-gate wrapper" "$ROOT/.claude/hooks/quality-gate.py"
check_file "Claude workflow-gate wrapper" "$ROOT/.claude/hooks/workflow-gate.py"
check_file "Claude shell hook dispatcher" "$ROOT/.claude/hooks/project-hook-dispatch.sh"
check_file "Claude PowerShell dispatcher" "$ROOT/.claude/hooks/project-hook-dispatch.ps1"
for hook in session-start.py memory-flush.py freshness-reminder.py koda-nudge.py \
  consolidate-check.sh inject-context.sh enforce-migration-pair.sh \
  cap-active-blocker-size.sh warn-unstamped-specs.sh run-shared-hook.sh \
  validate-branch.ps1 validate-commit-msg.ps1 session-start.ps1; do
  check_file "Claude project hook wrapper" "$ROOT/.claude/hooks/$hook"
done
check_file "Agent OS install doc" "$ROOT/docs/agent-playbooks/agent-os-installation.md"
check_file "Agent OS install manifest" "$ROOT/docs/agent-playbooks/agent-os-install-manifest.json"
check_file "Agent OS installer" "$ROOT/scripts/agent-checks/agent-os-install.sh"
check_file "Agent OS eval runner" "$ROOT/scripts/agent-checks/agent-os-eval-runner.py"
check_file "Agent OS response shape" "$ROOT/scripts/agent-checks/agent-os-response-shape-runner.py"
check_file "Agent OS transcript retrospective" "$ROOT/scripts/agent-checks/agent-os-transcript-retrospective.py"
check_file "Agent OS workflow examples" "$ROOT/scripts/agent-checks/agent-os-workflow-example-runner.py"
check_file "Agent OS state fixtures" "$ROOT/scripts/agent-checks/agent-os-state-fixture-runner.py"
check_file "Agent OS session map check" "$ROOT/scripts/agent-checks/session-map-check.py"
check_file "Agent OS session map HTML" "$ROOT/scripts/agent-checks/session-map-html.py"
check_file "Agent OS Koda fixtures" "$ROOT/scripts/agent-checks/agent-os-koda-fixture-runner.py"
check_file "Agent OS capability fixtures" "$ROOT/scripts/agent-checks/agent-os-capability-fixture-runner.py"
check_file "Agent OS capability probe" "$ROOT/scripts/agent-checks/agent-os-capability-probe.py"
check_file "Agent OS Google Drive probe" "$ROOT/scripts/agent-checks/agent-os-google-drive-probe.py"
check_file "Agent OS GitHub probe" "$ROOT/scripts/agent-checks/agent-os-github-probe.py"
check_file "Agent OS Planner probe" "$ROOT/scripts/agent-checks/agent-os-planner-probe.py"
check_file "SharePoint read-only lane" "$ROOT/scripts/agent-access/sharepoint-readonly.py"
check_file "SharePoint read-only fixtures" "$ROOT/scripts/agent-checks/test_sharepoint_readonly.py"
check_file "Agent OS today snapshot" "$ROOT/scripts/agent-checks/agent-os-today-snapshot.py"
check_file "Agent OS today fixtures" "$ROOT/scripts/agent-checks/test_agent_os_today_snapshot.py"
check_file "coverage enforcement" "$ROOT/scripts/agent-checks/coverage_enforcement.py"
check_file "release documentation enforcement" "$ROOT/scripts/agent-checks/release_documentation.py"
check_file "coverage enforcement fixtures" "$ROOT/scripts/agent-checks/test_coverage_enforcement.py"
check_file "coverage manifest check" "$ROOT/scripts/agent-checks/test-coverage-manifest-check.py"
check_file "test coverage playbook" "$ROOT/docs/agent-playbooks/test-coverage.md"
check_file "product coverage CI template" "$ROOT/docs/agent-playbooks/templates/product-test-coverage-ci.yml"
check_file "project registry check" "$ROOT/scripts/agent-checks/agent-os-project-registry-check.py"
check_file "project registry fixtures" "$ROOT/scripts/agent-checks/test_agent_os_project_registry.py"
check_file "Agent OS production logs probe" "$ROOT/scripts/agent-checks/agent-os-production-logs-probe.py"
check_file "Agent OS live evidence report" "$ROOT/scripts/agent-checks/agent-os-live-evidence-report.py"
check_file "Agent OS conversation fixtures" "$ROOT/scripts/agent-checks/agent-os-conversation-fixture-runner.py"
check_file "Agent OS parity fixtures" "$ROOT/scripts/agent-checks/agent-os-parity-fixture-runner.py"
check_file "Agent OS validation loop" "$ROOT/scripts/agent-checks/agent-os-validation-loop.py"
check_file "Agent OS scenario lab" "$ROOT/scripts/agent-checks/agent-os-scenario-lab-runner.py"
check_file "Agent OS behavior trace" "$ROOT/scripts/agent-checks/agent-os-behavior-trace-runner.py"
check_file "Claude delegation runner" "$ROOT/scripts/agent-checks/agent-os-claude-delegation.py"
check_file "Claude delegation fixtures" "$ROOT/scripts/agent-checks/agent-os-claude-delegation-fixture-runner.py"
check_file "Claude delegation template" "$ROOT/docs/agent-playbooks/templates/claude-delegation-job.json"
check_file "Agent OS Koda retrieval" "$ROOT/scripts/agent-checks/agent-os-koda-retrieval-quality.py"
check_file "Agent OS adapter readiness" "$ROOT/scripts/agent-checks/agent-os-adapter-readiness.py"
check_file "Kilo adapter check" "$ROOT/scripts/agent-checks/kilo-agent-os-adapter-check.py"
check_file "secret output guard" "$ROOT/scripts/agent-checks/secret_output_guard.py"
check_file "secret artifact scan" "$ROOT/scripts/agent-checks/secret_artifact_scan.py"
check_file "capability example" "$ROOT/docs/agent-playbooks/capabilities.example.json"
check_file "Codex SIMS UI audit skill" "$ROOT/.agents/skills/sims-ui-audit/SKILL.md"
if [[ -d "$ROOT/sifu-tutor" ]]; then
  check_file "Claude SIMS UI audit skill" "$ROOT/sifu-tutor/.claude/skills/sims-ui-audit/SKILL.md"
else
  warn "Claude SIMS UI audit skill" "sifu-tutor not cloned; skipped for scoped staff workspace"
fi

if "$ROOT/scripts/agent-checks/agent-os-eval-runner.py" >$TMP_DIR/agent-os-eval-runner.out 2>$TMP_DIR/agent-os-eval-runner.err; then
  eval_summary="$(tail -1 $TMP_DIR/agent-os-eval-runner.out 2>/dev/null || true)"
  pass "Agent OS evals" "${eval_summary:-passed}"
else
  fail "Agent OS evals" "routing/behavior eval runner failed"
  sed -n '1,12p' $TMP_DIR/agent-os-eval-runner.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/agent-os-eval-runner.err 2>/dev/null || true
fi
rm -f $TMP_DIR/agent-os-eval-runner.out $TMP_DIR/agent-os-eval-runner.err

if "$ROOT/scripts/agent-checks/agent-os-eval-runner.py" --self-test >$TMP_DIR/agent-os-eval-self-test.out 2>$TMP_DIR/agent-os-eval-self-test.err; then
  self_test_summary="$(tail -1 $TMP_DIR/agent-os-eval-self-test.out 2>/dev/null || true)"
  pass "Agent OS eval self-test" "${self_test_summary:-passed}"
else
  fail "Agent OS eval self-test" "negative eval self-test failed"
  sed -n '1,12p' $TMP_DIR/agent-os-eval-self-test.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/agent-os-eval-self-test.err 2>/dev/null || true
fi
rm -f $TMP_DIR/agent-os-eval-self-test.out $TMP_DIR/agent-os-eval-self-test.err

if "$ROOT/scripts/agent-checks/agent-os-response-shape-runner.py" >$TMP_DIR/agent-os-response-shape.out 2>$TMP_DIR/agent-os-response-shape.err; then
  response_shape_summary="$(tail -1 $TMP_DIR/agent-os-response-shape.out 2>/dev/null || true)"
  pass "Agent OS response shape" "${response_shape_summary:-passed}"
else
  fail "Agent OS response shape" "response-shape runner failed"
  sed -n '1,12p' $TMP_DIR/agent-os-response-shape.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/agent-os-response-shape.err 2>/dev/null || true
fi
rm -f $TMP_DIR/agent-os-response-shape.out $TMP_DIR/agent-os-response-shape.err

if python3 -m unittest discover -s "$ROOT/scripts/agent-checks" -p 'test_communication_samples.py' >$TMP_DIR/communication-samples.out 2>$TMP_DIR/communication-samples.err; then
  pass "communication samples" "sample input, manual-review state and CLI regressions passed"
else
  fail "communication samples" "sample regression tests failed"
fi
rm -f "$TMP_DIR/communication-samples.out" "$TMP_DIR/communication-samples.err"

if PYTHONPATH="$ROOT/scripts/agent-checks" python3 -m unittest test_completion_receipt test_delegation_packet test_agent_os_adapter_contract test_secret_guard_reconciliation test_agent_os_active_task_freshness >$TMP_DIR/delegation-contracts.out 2>$TMP_DIR/delegation-contracts.err; then
  pass "delegation contracts" "completion, packet, capability and secret-format regressions passed"
else
  fail "delegation contracts" "focused contract tests failed; inspect local sanitized test output"
fi
rm -f "$TMP_DIR/delegation-contracts.out" "$TMP_DIR/delegation-contracts.err"

if python3 "$ROOT/scripts/agent-checks/agent-os-transcript-retrospective.py" --self-test >$TMP_DIR/agent-os-transcript-retrospective.out 2>$TMP_DIR/agent-os-transcript-retrospective.err; then
  transcript_summary="$(tail -1 $TMP_DIR/agent-os-transcript-retrospective.out 2>/dev/null || true)"
  pass "Agent OS transcript safety" "${transcript_summary:-passed}"
else
  fail "Agent OS transcript safety" "privacy/filter/dedup self-test failed"
  sed -n '1,12p' $TMP_DIR/agent-os-transcript-retrospective.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/agent-os-transcript-retrospective.err 2>/dev/null || true
fi
rm -f $TMP_DIR/agent-os-transcript-retrospective.out $TMP_DIR/agent-os-transcript-retrospective.err

if "$ROOT/scripts/agent-checks/agent-os-workflow-example-runner.py" >$TMP_DIR/agent-os-workflow-examples.out 2>$TMP_DIR/agent-os-workflow-examples.err; then
  workflow_example_summary="$(tail -1 $TMP_DIR/agent-os-workflow-examples.out 2>/dev/null || true)"
  pass "Agent OS workflow examples" "${workflow_example_summary:-passed}"
else
  fail "Agent OS workflow examples" "workflow example runner failed"
  sed -n '1,12p' $TMP_DIR/agent-os-workflow-examples.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/agent-os-workflow-examples.err 2>/dev/null || true
fi
rm -f $TMP_DIR/agent-os-workflow-examples.out $TMP_DIR/agent-os-workflow-examples.err

if "$ROOT/scripts/agent-checks/agent-os-state-fixture-runner.py" >$TMP_DIR/agent-os-state-fixtures.out 2>$TMP_DIR/agent-os-state-fixtures.err; then
  state_fixture_summary="$(tail -1 $TMP_DIR/agent-os-state-fixtures.out 2>/dev/null || true)"
  pass "Agent OS state fixtures" "${state_fixture_summary:-passed}"
else
  fail "Agent OS state fixtures" "state fixture runner failed"
  sed -n '1,12p' $TMP_DIR/agent-os-state-fixtures.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/agent-os-state-fixtures.err 2>/dev/null || true
fi
rm -f $TMP_DIR/agent-os-state-fixtures.out $TMP_DIR/agent-os-state-fixtures.err

if python3 "$ROOT/scripts/agent-checks/session-map-check.py" >$TMP_DIR/agent-os-session-map.out 2>$TMP_DIR/agent-os-session-map.err; then
  session_map_summary="$(tail -1 $TMP_DIR/agent-os-session-map.out 2>/dev/null || true)"
  pass "Agent OS session map check" "${session_map_summary:-passed}"
else
  fail "Agent OS session map check" "session-map checker failed"
  sed -n '1,12p' $TMP_DIR/agent-os-session-map.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/agent-os-session-map.err 2>/dev/null || true
fi
rm -f $TMP_DIR/agent-os-session-map.out $TMP_DIR/agent-os-session-map.err

if python3 "$ROOT/scripts/agent-checks/session-map-html.py" "$ROOT/docs/agent-playbooks/templates/session-map.md" -o $TMP_DIR/agent-os-session-map.html >$TMP_DIR/agent-os-session-map-html.out 2>$TMP_DIR/agent-os-session-map-html.err; then
  html_summary="$(tail -1 $TMP_DIR/agent-os-session-map-html.out 2>/dev/null || true)"
  pass "Agent OS session map HTML" "${html_summary:-passed}"
else
  fail "Agent OS session map HTML" "HTML generator failed"
  sed -n '1,12p' $TMP_DIR/agent-os-session-map-html.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/agent-os-session-map-html.err 2>/dev/null || true
fi
rm -f $TMP_DIR/agent-os-session-map.html $TMP_DIR/agent-os-session-map-html.out $TMP_DIR/agent-os-session-map-html.err

if "$ROOT/scripts/agent-checks/agent-os-koda-fixture-runner.py" >$TMP_DIR/agent-os-koda-fixtures.out 2>$TMP_DIR/agent-os-koda-fixtures.err; then
  koda_fixture_summary="$(tail -1 $TMP_DIR/agent-os-koda-fixtures.out 2>/dev/null || true)"
  pass "Agent OS Koda fixtures" "${koda_fixture_summary:-passed}"
else
  fail "Agent OS Koda fixtures" "Koda fixture runner failed"
  sed -n '1,12p' $TMP_DIR/agent-os-koda-fixtures.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/agent-os-koda-fixtures.err 2>/dev/null || true
fi
rm -f $TMP_DIR/agent-os-koda-fixtures.out $TMP_DIR/agent-os-koda-fixtures.err

if python3 -m unittest discover -s "$ROOT/scripts/agent-checks" -p 'test_*koda*.py' >$TMP_DIR/koda-write-tests.out 2>$TMP_DIR/koda-write-tests.err; then
  pass "Koda write integrity" "client contracts and CLI readback journeys passed"
else
  fail "Koda write integrity" "client regression tests failed; inspect locally without exposing provider data"
fi
rm -f "$TMP_DIR/koda-write-tests.out" "$TMP_DIR/koda-write-tests.err"

if "$ROOT/scripts/agent-checks/agent-os-capability-fixture-runner.py" >$TMP_DIR/agent-os-capability-fixtures.out 2>$TMP_DIR/agent-os-capability-fixtures.err; then
  capability_fixture_summary="$(tail -1 $TMP_DIR/agent-os-capability-fixtures.out 2>/dev/null || true)"
  pass "Agent OS capability fixtures" "${capability_fixture_summary:-passed}"
else
  fail "Agent OS capability fixtures" "capability fixture runner failed"
  sed -n '1,12p' $TMP_DIR/agent-os-capability-fixtures.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/agent-os-capability-fixtures.err 2>/dev/null || true
fi
rm -f $TMP_DIR/agent-os-capability-fixtures.out $TMP_DIR/agent-os-capability-fixtures.err

if "$ROOT/scripts/agent-checks/agent-os-capability-probe.py" --json >$TMP_DIR/agent-os-capability-probe.out 2>$TMP_DIR/agent-os-capability-probe.err; then
  capability_probe_summary="$(TMP_DIR="$TMP_DIR" python3 - <<'PY' 2>/dev/null
import json
import os
from pathlib import Path

data = json.loads((Path(os.environ["TMP_DIR"]) / "agent-os-capability-probe.out").read_text())
print(len(data.get("capabilities", [])))
PY
)"
  if [[ "$capability_probe_summary" =~ ^[0-9]+$ ]] && [[ "$capability_probe_summary" -gt 0 ]]; then
    pass "Agent OS capability probe" "$capability_probe_summary capabilities reported"
  else
    fail "Agent OS capability probe" "capability probe returned no capabilities"
    sed -n '1,12p' $TMP_DIR/agent-os-capability-probe.out 2>/dev/null || true
    sed -n '1,8p' $TMP_DIR/agent-os-capability-probe.err 2>/dev/null || true
  fi
else
  fail "Agent OS capability probe" "capability probe failed"
  sed -n '1,12p' $TMP_DIR/agent-os-capability-probe.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/agent-os-capability-probe.err 2>/dev/null || true
fi
rm -f $TMP_DIR/agent-os-capability-probe.out $TMP_DIR/agent-os-capability-probe.err

if python3 -m unittest "$ROOT/scripts/agent-checks/test_sharepoint_readonly.py" >$TMP_DIR/sharepoint-readonly.out 2>$TMP_DIR/sharepoint-readonly.err; then
  pass "SharePoint read-only fixtures" "auth, allow-list, pagination, download and error boundaries passed"
else
  fail "SharePoint read-only fixtures" "read-only boundary fixtures failed"
  sed -n '1,12p' $TMP_DIR/sharepoint-readonly.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/sharepoint-readonly.err 2>/dev/null || true
fi
rm -f $TMP_DIR/sharepoint-readonly.out $TMP_DIR/sharepoint-readonly.err

if python3 -m py_compile "$ROOT/scripts/agent-checks/agent-os-live-evidence-report.py" >$TMP_DIR/agent-os-live-evidence-report.out 2>$TMP_DIR/agent-os-live-evidence-report.err; then
  pass "Agent OS live evidence report" "py_compile ok"
else
  fail "Agent OS live evidence report" "py_compile failed"
  sed -n '1,12p' $TMP_DIR/agent-os-live-evidence-report.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/agent-os-live-evidence-report.err 2>/dev/null || true
fi
rm -f $TMP_DIR/agent-os-live-evidence-report.out $TMP_DIR/agent-os-live-evidence-report.err

if python3 -m unittest scripts/agent-checks/test_agent_os_today_snapshot.py >$TMP_DIR/agent-os-today-snapshot.out 2>$TMP_DIR/agent-os-today-snapshot.err; then
  today_snapshot_summary="$(tail -2 $TMP_DIR/agent-os-today-snapshot.out 2>/dev/null | head -1 || true)"
  pass "Agent OS today snapshot" "${today_snapshot_summary:-fixtures passed}"
else
  fail "Agent OS today snapshot" "bounded snapshot/Planner/response fixtures failed"
  sed -n '1,12p' $TMP_DIR/agent-os-today-snapshot.out 2>/dev/null || true
  sed -n '1,12p' $TMP_DIR/agent-os-today-snapshot.err 2>/dev/null || true
fi

if python3 -m unittest scripts/agent-checks/test_secret_output_guard.py scripts/agent-checks/test_secret_artifact_scan.py >$TMP_DIR/agent-os-secret-guards.out 2>$TMP_DIR/agent-os-secret-guards.err; then
  pass "secret output guards" "command, visual-capture, and artifact regressions passed"
else
  fail "secret output guards" "regression tests failed"
  sed -n '1,12p' $TMP_DIR/agent-os-secret-guards.out 2>/dev/null || true
  sed -n '1,12p' $TMP_DIR/agent-os-secret-guards.err 2>/dev/null || true
fi
rm -f $TMP_DIR/agent-os-secret-guards.out $TMP_DIR/agent-os-secret-guards.err
rm -f $TMP_DIR/agent-os-today-snapshot.out $TMP_DIR/agent-os-today-snapshot.err

if "$ROOT/scripts/agent-checks/agent-os-conversation-fixture-runner.py" >$TMP_DIR/agent-os-conversation-fixtures.out 2>$TMP_DIR/agent-os-conversation-fixtures.err; then
  conversation_fixture_summary="$(tail -1 $TMP_DIR/agent-os-conversation-fixtures.out 2>/dev/null || true)"
  pass "Agent OS conversation fixtures" "${conversation_fixture_summary:-passed}"
else
  fail "Agent OS conversation fixtures" "conversation fixture runner failed"
  sed -n '1,12p' $TMP_DIR/agent-os-conversation-fixtures.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/agent-os-conversation-fixtures.err 2>/dev/null || true
fi
rm -f $TMP_DIR/agent-os-conversation-fixtures.out $TMP_DIR/agent-os-conversation-fixtures.err

if "$ROOT/scripts/agent-checks/agent-os-parity-fixture-runner.py" >$TMP_DIR/agent-os-parity-fixtures.out 2>$TMP_DIR/agent-os-parity-fixtures.err; then
  parity_fixture_summary="$(tail -1 $TMP_DIR/agent-os-parity-fixtures.out 2>/dev/null || true)"
  pass "Agent OS parity fixtures" "${parity_fixture_summary:-passed}"
else
  fail "Agent OS parity fixtures" "parity fixture runner failed"
  sed -n '1,12p' $TMP_DIR/agent-os-parity-fixtures.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/agent-os-parity-fixtures.err 2>/dev/null || true
fi
rm -f $TMP_DIR/agent-os-parity-fixtures.out $TMP_DIR/agent-os-parity-fixtures.err

if python3 "$ROOT/scripts/agent-checks/agent-os-scenario-lab-runner.py" --target 0.90 >$TMP_DIR/agent-os-scenario-lab.out 2>$TMP_DIR/agent-os-scenario-lab.err; then
  scenario_lab_summary="$(tail -1 $TMP_DIR/agent-os-scenario-lab.out 2>/dev/null || true)"
  pass "Agent OS scenario lab" "${scenario_lab_summary:-passed}"
else
  fail "Agent OS scenario lab" "scenario lab runner failed"
  sed -n '1,12p' $TMP_DIR/agent-os-scenario-lab.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/agent-os-scenario-lab.err 2>/dev/null || true
fi
rm -f $TMP_DIR/agent-os-scenario-lab.out $TMP_DIR/agent-os-scenario-lab.err

if "$ROOT/scripts/agent-checks/agent-os-behavior-trace-runner.py" >$TMP_DIR/agent-os-behavior-trace.out 2>$TMP_DIR/agent-os-behavior-trace.err; then
  behavior_trace_summary="$(tail -1 $TMP_DIR/agent-os-behavior-trace.out 2>/dev/null || true)"
  pass "Agent OS behavior trace" "${behavior_trace_summary:-passed}"
else
  fail "Agent OS behavior trace" "behavior trace runner failed"
  sed -n '1,12p' $TMP_DIR/agent-os-behavior-trace.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/agent-os-behavior-trace.err 2>/dev/null || true
fi
rm -f $TMP_DIR/agent-os-behavior-trace.out $TMP_DIR/agent-os-behavior-trace.err

if python3 -m unittest discover -s "$ROOT/scripts/agent-checks" -p 'test_worktree_lifecycle.py' >$TMP_DIR/worktree-lifecycle.out 2>$TMP_DIR/worktree-lifecycle.err; then
  worktree_lifecycle_summary="$(tail -1 $TMP_DIR/worktree-lifecycle.out 2>/dev/null || true)"
  pass "worktree lifecycle" "${worktree_lifecycle_summary:-lease, classification, reclaim and dependency fixtures passed}"
else
  fail "worktree lifecycle" "worktree lifecycle regression tests failed"
  sed -n '1,12p' $TMP_DIR/worktree-lifecycle.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/worktree-lifecycle.err 2>/dev/null || true
fi
rm -f $TMP_DIR/worktree-lifecycle.out $TMP_DIR/worktree-lifecycle.err

if "$ROOT/scripts/agent-checks/agent-os-project-registry-check.py" --root "$ROOT" >$TMP_DIR/project-registry.out 2>$TMP_DIR/project-registry.err; then
  project_registry_summary="$(tail -1 $TMP_DIR/project-registry.out 2>/dev/null || true)"
  pass "project registries" "${project_registry_summary:-live project registries agree}"
else
  fail "project registries" "live project registries disagree (issue 103)"
  sed -n '1,12p' $TMP_DIR/project-registry.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/project-registry.err 2>/dev/null || true
fi
rm -f $TMP_DIR/project-registry.out $TMP_DIR/project-registry.err

if python3 -m unittest discover -s "$ROOT/scripts/agent-checks" -p 'test_agent_os_project_registry.py' >$TMP_DIR/project-registry-tests.out 2>$TMP_DIR/project-registry-tests.err; then
  pass "project registry fixtures" "drift, routing-parity and history-preservation fixtures passed"
else
  fail "project registry fixtures" "project registry regression tests failed"
  sed -n '1,12p' $TMP_DIR/project-registry-tests.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/project-registry-tests.err 2>/dev/null || true
fi
rm -f $TMP_DIR/project-registry-tests.out $TMP_DIR/project-registry-tests.err

if python3 -m unittest discover -s "$ROOT/scripts/agent-checks" -p 'test_coverage_enforcement.py' >$TMP_DIR/coverage-enforcement.out 2>$TMP_DIR/coverage-enforcement.err; then
  pass "test coverage enforcement" "manifest, change, release, bypass and containment fixtures passed"
else
  fail "test coverage enforcement" "coverage enforcement regression tests failed"
  sed -n '1,12p' $TMP_DIR/coverage-enforcement.out 2>/dev/null || true
  sed -n '1,12p' $TMP_DIR/coverage-enforcement.err 2>/dev/null || true
fi
rm -f "$TMP_DIR/coverage-enforcement.out" "$TMP_DIR/coverage-enforcement.err"

if python3 -m unittest discover -s "$ROOT/scripts/agent-checks" -p 'test_release_documentation.py' >$TMP_DIR/release-documentation.out 2>$TMP_DIR/release-documentation.err; then
  pass "staff documentation release gate" "relevance, deferral owner/issue, project shape, scope and bypass fixtures passed"
else
  fail "staff documentation release gate" "release documentation regression tests failed"
  sed -n '1,12p' $TMP_DIR/release-documentation.out 2>/dev/null || true
  sed -n '1,12p' $TMP_DIR/release-documentation.err 2>/dev/null || true
fi
rm -f "$TMP_DIR/release-documentation.out" "$TMP_DIR/release-documentation.err"

if python3 -m unittest discover -s "$ROOT/scripts/agent-checks" -p 'test_agent_os_task_context.py' >$TMP_DIR/task-context.out 2>$TMP_DIR/task-context.err; then
  pass "Agent OS task context" "session isolation, approval transfer and controlled continuation passed"
else
  fail "Agent OS task context" "task-context regression tests failed"
fi
rm -f "$TMP_DIR/task-context.out" "$TMP_DIR/task-context.err"

if "$ROOT/scripts/agent-checks/agent-os-claude-delegation-fixture-runner.py" >$TMP_DIR/agent-os-claude-delegation.out 2>$TMP_DIR/agent-os-claude-delegation.err; then
  claude_delegation_summary="$(tail -1 $TMP_DIR/agent-os-claude-delegation.out 2>/dev/null || true)"
  pass "Claude delegation fixtures" "${claude_delegation_summary:-passed}"
else
  fail "Claude delegation fixtures" "preflight/watchdog/evidence fixtures failed"
  sed -n '1,12p' $TMP_DIR/agent-os-claude-delegation.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/agent-os-claude-delegation.err 2>/dev/null || true
fi
rm -f $TMP_DIR/agent-os-claude-delegation.out $TMP_DIR/agent-os-claude-delegation.err

if "$ROOT/scripts/agent-checks/agent-os-adapter-readiness.py" >$TMP_DIR/agent-os-adapter-readiness.out 2>$TMP_DIR/agent-os-adapter-readiness.err; then
  adapter_readiness_summary="$(tail -1 $TMP_DIR/agent-os-adapter-readiness.out 2>/dev/null || true)"
  pass "Agent OS adapter readiness" "${adapter_readiness_summary:-passed}"
else
  fail "Agent OS adapter readiness" "adapter readiness runner failed"
  sed -n '1,12p' $TMP_DIR/agent-os-adapter-readiness.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/agent-os-adapter-readiness.err 2>/dev/null || true
fi
rm -f $TMP_DIR/agent-os-adapter-readiness.out $TMP_DIR/agent-os-adapter-readiness.err

if python3 "$ROOT/scripts/agent-checks/kilo-agent-os-adapter-check.py" >$TMP_DIR/kilo-agent-os-adapter.out 2>$TMP_DIR/kilo-agent-os-adapter.err; then
  kilo_adapter_summary="$(tail -1 $TMP_DIR/kilo-agent-os-adapter.out 2>/dev/null || true)"
  pass "Kilo Agent OS adapter" "${kilo_adapter_summary:-passed}"
else
  fail "Kilo Agent OS adapter" "portable adapter validation failed"
  sed -n '1,12p' $TMP_DIR/kilo-agent-os-adapter.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/kilo-agent-os-adapter.err 2>/dev/null || true
fi
rm -f $TMP_DIR/kilo-agent-os-adapter.out $TMP_DIR/kilo-agent-os-adapter.err

if python3 -m py_compile "$ROOT/scripts/agent-checks/agent-os-koda-retrieval-quality.py" >$TMP_DIR/agent-os-koda-retrieval.out 2>$TMP_DIR/agent-os-koda-retrieval.err; then
  pass "Agent OS Koda retrieval" "py_compile ok; run directly for live retrieval quality"
else
  fail "Agent OS Koda retrieval" "py_compile failed"
  sed -n '1,12p' $TMP_DIR/agent-os-koda-retrieval.out 2>/dev/null || true
  sed -n '1,8p' $TMP_DIR/agent-os-koda-retrieval.err 2>/dev/null || true
fi
rm -f $TMP_DIR/agent-os-koda-retrieval.out $TMP_DIR/agent-os-koda-retrieval.err

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

# Issue 113: valid JSON never proved the pointer still describes current work.
if python3 "$ROOT/scripts/agent-checks/agent_os_active_task_freshness.py" --self-test \
  >$TMP_DIR/agent-os-task-freshness.out 2>$TMP_DIR/agent-os-task-freshness.err; then
  pass "active task freshness" "$(grep 'fixtures:' $TMP_DIR/agent-os-task-freshness.out | tail -1)"
else
  fail "active task freshness" "fixture drift"
  grep '^FAIL ' $TMP_DIR/agent-os-task-freshness.out | sed -n '1,6p' || true
  sed -n '1,4p' $TMP_DIR/agent-os-task-freshness.err 2>/dev/null || true
fi
rm -f $TMP_DIR/agent-os-task-freshness.out $TMP_DIR/agent-os-task-freshness.err

echo
echo "Koda"
if "$ROOT/scripts/agent-checks/koda" health >$TMP_DIR/agent-os-koda-check.out 2>$TMP_DIR/agent-os-koda-check.err; then
  pass "Koda direct health" "pass"
else
  warn "Koda direct health" "failed or unavailable"
  sed -n '1,8p' $TMP_DIR/agent-os-koda-check.err 2>/dev/null || true
fi
rm -f $TMP_DIR/agent-os-koda-check.out $TMP_DIR/agent-os-koda-check.err

echo
echo "Capability Summary"
echo "- filesystem: available if workspace write detected above"
echo "- git status/diff: available if git repo detected above"
echo "- git commit: blocked until exact file-list approval and guard checks"
echo "- git push / PR / merge: blocked until explicit current-session approval"
echo "- koda: available through CLI if direct health passed; chat MCP wrapper is optional"
echo "- github: check on demand with scripts/agent-checks/agent-os-github-probe.py before claiming read access"
echo "- plane: exception-only; do not use unless Hafiz explicitly asks in the current session"
echo "- planner: check on demand with scripts/agent-checks/agent-os-planner-probe.py before claiming read access"
echo "- google_drive: check connector readiness with scripts/agent-checks/agent-os-google-drive-probe.py; live read still needs exposed connector tools"
echo "- production_logs: check on demand with scripts/agent-checks/agent-os-production-logs-probe.py before claiming monitoring read access"
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
