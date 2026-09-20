#!/usr/bin/env python3
"""Exercise the Claude delegation preflight, watchdog, and evidence contract."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "agent-checks" / "agent-os-claude-delegation.py"
BRIEF_TEMPLATE = ROOT / "docs" / "agent-playbooks" / "templates" / "codex-to-claude.md"
JOB_TEMPLATE = ROOT / "docs" / "agent-playbooks" / "templates" / "claude-delegation-job.json"
HANDOFF_PLAYBOOK = ROOT / "docs" / "agent-playbooks" / "handoff.md"

PROOF_FIELDS = (
    "acceptance_to_proof_map", "entrypoint", "production_caller",
    "authoritative_result", "bypass_paths", "permissions_configuration",
    "disabled_unavailable", "failure_retry", "negative_control", "journey",
    "regression", "builder_evidence_not_acceptance",
)


FAKE_CLAUDE = r'''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys
import time

marker = os.environ.get("FAKE_API_KEY_MARKER")
if marker and os.environ.get("ANTHROPIC_API_KEY"):
    Path(marker).write_text("leaked")
prompt_marker = os.environ.get("FAKE_PROMPT_ARG_MARKER")
if prompt_marker and any("exercise the watchdog" in arg for arg in sys.argv[1:]):
    Path(prompt_marker).write_text("prompt exposed in argv")
probe_marker = os.environ.get("FAKE_PROBE_MARKER")
if probe_marker:
    Path(probe_marker).write_text("probed")

args = sys.argv[1:]
if args[:2] == ["auth", "status"]:
    auth_mode = os.environ.get("FAKE_AUTH_MODE", "max")
    if auth_mode == "api_key":
        response = {
            "loggedIn": True,
            "authMethod": "api-key",
            "apiProvider": "anthropic",
            "subscriptionType": None,
            "email": "must-not-persist@example.test",
            "orgId": "must-not-persist",
        }
    elif auth_mode == "ambiguous":
        response = {
            "loggedIn": True,
            "authMethod": "claude.ai",
            "apiProvider": None,
            "subscriptionType": None,
            "email": "must-not-persist@example.test",
            "orgId": "must-not-persist",
        }
    elif auth_mode == "max_login_api_billed":
        response = {
            "loggedIn": True,
            "authMethod": "claude.ai",
            "apiProvider": "anthropic",
            "subscriptionType": "max",
            "email": "must-not-persist@example.test",
            "orgId": "must-not-persist",
        }
    else:
        response = {
            "loggedIn": True,
            "authMethod": "claude.ai",
            "apiProvider": "firstParty",
            "subscriptionType": "max",
            "email": "must-not-persist@example.test",
            "orgId": "must-not-persist",
        }
    print(json.dumps(response))
    raise SystemExit(0)
if args[:2] == ["mcp", "list"]:
    print("koda: connected")
    raise SystemExit(0)
if args[:1] == ["doctor"]:
    print("No installation issues found.")
    raise SystemExit(0)
if "--version" in args:
    print("9.9.9 (fixture)")
    raise SystemExit(0)

mode = os.environ.get("FAKE_CLAUDE_MODE", "happy")
handback = os.environ.get("FAKE_HANDBACK")
proof = "\n".join(f"{name}: fixture evidence" for name in (
    "acceptance_to_proof_map", "entrypoint", "production_caller",
    "authoritative_result", "bypass_paths", "permissions_configuration",
    "disabled_unavailable", "failure_retry", "negative_control", "journey",
    "regression", "builder_evidence_not_acceptance",
))
if mode == "api_error_400":
    print(json.dumps({"type": "system", "subtype": "init", "session_id": "fixture-session"}), flush=True)
    print(json.dumps({
        "type": "result",
        "subtype": "success",
        "is_error": True,
        "api_error_status": 400,
        "terminal_reason": "api_error",
        "stop_reason": "stop_sequence",
        "num_turns": 1,
        "permission_denials": [],
        "fast_mode_state": "off",
        "fast_mode_disabled_reason": "sdk_opt_in_required",
        "session_id": "fixture-session",
        "total_cost_usd": 0,
        "usage": {"input_tokens": 0, "output_tokens": 0},
        "result": "API Error: 400 invalid request SENSITIVE RAW OUTPUT sk-ant-fixture-secret-value",
    }), flush=True)
    raise SystemExit(1)
if mode == "setup":
    print("Authentication required before continuing", file=sys.stderr, flush=True)
    time.sleep(0.08)
    raise SystemExit(3)
if mode in {"silent", "blocking"}:
    time.sleep(0.30 if mode == "silent" else 0.75)
    if handback:
        Path(handback).write_text("# Fixture handback\n\nstructured handback\n\nwatchdog evidence\n" + proof + "\n")
    raise SystemExit(0)

print(json.dumps({"type": "system", "subtype": "init", "session_id": "fixture-session"}), flush=True)
print(json.dumps({"type": "assistant", "usage": {"input_tokens": 999}, "message": {"content": [{"type": "text", "text": "SENSITIVE RAW OUTPUT and authentication required as ordinary prose"}]}}), flush=True)
recovery_modes = {
    "missing_handback_result",
    "missing_handback_secret_result",
    "missing_handback_invalid_result",
    "missing_handback_error_result",
    "missing_handback_directory_result",
}
result_payload = {"type": "result", "subtype": "success", "usage": {"input_tokens": 12, "output_tokens": 7}}
if mode in recovery_modes:
    result_text = "# Recovered fixture handback\n\nstructured handback\n\nwatchdog evidence\n" + proof + "\n"
    if mode == "missing_handback_secret_result":
        result_text += "\napi_key = " + "sk-ant-" + "abcdefghijklmnopqrstuvwxyz123456" + "\n"
    elif mode == "missing_handback_invalid_result":
        result_text = "Finished successfully, but without the configured proof fields."
    result_payload["result"] = result_text
print(json.dumps(result_payload), flush=True)
if mode == "missing_handback_error_result":
    # Two error-shaped results that a bare `is_error is not True` test misses:
    # `error_max_turns` carries no `is_error` key at all, and a non-boolean
    # truthy `is_error` slips past both that test and the centralized
    # classification. Each must discard the earlier contract-valid candidate
    # rather than become one, even though the process still exits 0.
    print(json.dumps({
        "type": "result",
        "subtype": "error_max_turns",
        "num_turns": 19,
        "usage": {"input_tokens": 12, "output_tokens": 7},
        "result": result_payload["result"],
    }), flush=True)
    print(json.dumps({
        "type": "result",
        "subtype": "success",
        "is_error": 1,
        "num_turns": 19,
        "usage": {"input_tokens": 12, "output_tokens": 7},
        "result": result_payload["result"],
    }), flush=True)
if handback and mode == "missing_handback_directory_result":
    # Leave a directory where the handback file belongs, so every recovery
    # write fails at the filesystem layer instead of at a content check.
    Path(handback).mkdir(parents=True, exist_ok=True)
if handback:
    content = "# Fixture handback\n\nstructured handback\n\nwatchdog evidence\n" + proof + "\n"
    if mode == "incomplete_handback":
        content = "# Fixture handback\n\nstructured handback\n\nwatchdog evidence\nentrypoint: only one field\n"
    elif mode == "quoted_template_handback":
        content = "# Fixture handback\n\nstructured handback\n\nwatchdog evidence\n```text\n" + proof + "\n```\n"
    elif mode == "not_applicable_handback":
        content = (
            "# Fixture handback\n\nstructured handback\n\nwatchdog evidence\n"
            "builder_proof_not_applicable: read-only inventory with no implementation or behavior change\n"
        )
    if mode not in recovery_modes:
        Path(handback).write_text(content)
'''


def run(command: list[str], env: dict[str, str], timeout: float = 10) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def make_job(
    base: Path,
    worktree: Path,
    job_id: str,
    lane: str = "fixture-lane",
    model_args: list[str] | None = None,
) -> Path:
    runtime_root = worktree / ".agent-os" / "delegations"
    runtime_root.mkdir(parents=True, exist_ok=True)
    state_dir = runtime_root / f"{job_id}-state"
    brief = runtime_root / f"{job_id}-brief.md"
    handback = state_dir / "handback.md"
    brief.write_text(
        "# Delegated fixture\n\nGoal: exercise the watchdog.\n"
        f"Write the final return contract to {handback}.\n"
    )
    job = {
        "schema_version": 1,
        "job_id": job_id,
        "goal": "exercise the deterministic Claude delegation fixture",
        "approved_stop_point": "local proof",
        "forbidden_actions": ["commit", "push", "merge", "deploy", "production mutation"],
        "worktree": str(worktree),
        "branch": "feat/fixture",
        "lane_owner": lane,
        "required_proof": ["structured handback", "watchdog evidence"],
        "builder_completion_proof": {
            "mode": "required",
            "not_applicable_reason": "",
        },
        "reporting_cadence_seconds": 60,
        "stall_after_seconds": 0.10,
        "poll_interval_seconds": 0.02,
        "brief_file": str(brief),
        "handback_file": str(handback),
        "state_dir": str(state_dir),
        "claude_args": [
            "--print",
            "--verbose",
            "--output-format",
            "stream-json",
            "--include-partial-messages",
            "--permission-mode",
            "dontAsk",
            *(["--model", "opus"] if model_args is None else model_args),
        ],
    }
    path = base / f"{job_id}.json"
    path.write_text(json.dumps(job, indent=2) + "\n")
    return path


def setup_repo(path: Path) -> None:
    path.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "feat/fixture"], cwd=path, check=True)
    (path / "README.md").write_text("fixture\n")
    (path / ".gitignore").write_text(".agent-os/\n")
    subprocess.run(["git", "add", "README.md", ".gitignore"], cwd=path, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Agent OS Fixture",
            "-c",
            "user.email=fixture@example.test",
            "commit",
            "-q",
            "-m",
            "test fixture",
        ],
        cwd=path,
        check=True,
    )


def check(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    failures: list[str] = []

    # issue-56: the Codex-To-Claude brief template's Required Return Contract
    # must itself name the Builder Completion Proof Contract fields, so a
    # filled-in delegation brief cannot satisfy the template's own checklist
    # while silently omitting the evidence issue #56 requires. The handoff
    # playbook's delegation section must also link to that contract by name,
    # not only cite the pre-work Build-Ready Pack.
    df010_errors: list[str] = []
    brief_text = BRIEF_TEMPLATE.read_text() if BRIEF_TEMPLATE.is_file() else ""
    handoff_text = HANDOFF_PLAYBOOK.read_text() if HANDOFF_PLAYBOOK.is_file() else ""
    job_template = json.loads(JOB_TEMPLATE.read_text()) if JOB_TEMPLATE.is_file() else {}
    brief_markers = (
        "acceptance-to-proof map",
        "production caller",
        "bypass-path sweep",
        "negative-control",
        "builder evidence",
        "independent acceptance",
        "authoritative",
        "permission/configuration",
        "flag-off/unavailable",
    )
    for marker in brief_markers:
        check(
            marker in brief_text.lower(),
            f"brief template Required Return Contract missing {marker!r}",
            df010_errors,
        )
    check(
        "builder completion proof" in handoff_text.lower(),
        "handoff.md delegation section does not name the Builder Completion Proof Contract",
        df010_errors,
    )
    check(
        job_template.get("builder_completion_proof")
        == {"mode": "required", "not_applicable_reason": ""},
        "canonical job template does not default to the required Builder Completion Proof mode",
        df010_errors,
    )
    # issue-100: the canonical template must select the currently proven model
    # alias explicitly, and the playbook must say why an implicit workspace
    # model selection is refused.
    template_args = job_template.get("claude_args", [])
    check(
        isinstance(template_args, list)
        and "--model" in template_args
        and template_args[template_args.index("--model") + 1 : template_args.index("--model") + 2] == ["opus"],
        "canonical job template does not select the proven explicit model alias",
        df010_errors,
    )
    check(
        "--model" in handoff_text and "explicit" in handoff_text.lower(),
        "handoff.md does not document the explicit Claude model requirement",
        df010_errors,
    )
    for field in PROOF_FIELDS:
        check(
            f"{field}:" in brief_text,
            f"brief template missing structured proof field {field!r}",
            df010_errors,
        )
    print(("PASS" if not df010_errors else "FAIL") + " DF-016 delegation template builder completion proof linkage")
    for error in df010_errors:
        print(f"  - {error}")
    failures.extend(f"DF-016: {error}" for error in df010_errors)

    with tempfile.TemporaryDirectory(prefix="agent-os-claude-delegation-fixtures.") as raw_tmp:
        tmp = Path(raw_tmp)
        fake_bin = tmp / "bin"
        fake_bin.mkdir()
        fake = fake_bin / "claude"
        fake.write_text(FAKE_CLAUDE)
        fake.chmod(0o755)
        worktree = tmp / "worktree"
        setup_repo(worktree)

        marker = tmp / "api-key-leak-marker"
        prompt_marker = tmp / "prompt-argv-marker"
        probe_marker = tmp / "probe-marker"
        base_env = os.environ.copy()
        base_env["PATH"] = f"{fake_bin}{os.pathsep}{base_env.get('PATH', '')}"
        base_env["ANTHROPIC_API_KEY"] = "fixture-key-must-be-unset"
        base_env["FAKE_API_KEY_MARKER"] = str(marker)
        base_env["FAKE_PROMPT_ARG_MARKER"] = str(prompt_marker)

        # DF-001: an inherited ANTHROPIC_API_KEY must fail preflight closed before
        # Claude is ever probed, so a stray evaluation key cannot silently replace
        # the intended Max subscription billing.
        job = make_job(tmp, worktree, "DF-001")
        probe_env = base_env | {"FAKE_PROBE_MARKER": str(probe_marker)}
        result = run([sys.executable, str(RUNNER), "preflight", "--job", str(job), "--json"], probe_env)
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            payload = {}
        errors: list[str] = []
        check(result.returncode != 0, "inherited API key unexpectedly passed preflight", errors)
        check(payload.get("ready") is False, "inherited API key preflight did not fail closed", errors)
        billing_guard = payload.get("checks", {}).get("api_billing_guard", {})
        check(billing_guard.get("state") == "blocked", "inherited API key was not identified as a billing risk", errors)
        check(
            billing_guard.get("blocked_variable_names") == ["ANTHROPIC_API_KEY"],
            "blocked result did not identify the inherited variable by name",
            errors,
        )
        serialized = json.dumps(payload)
        check("fixture-key-must-be-unset" not in serialized, "the API key value leaked into preflight output", errors)
        check(not probe_marker.exists(), "Claude was probed before the inherited API key was rejected", errors)
        print(("PASS" if not errors else "FAIL") + " DF-001 fail-closed on inherited API key")
        failures.extend(f"DF-001: {error}" for error in errors)

        # DF-002 (this file's numbering continues below): once the key is removed
        # (the documented `env -u ANTHROPIC_API_KEY` relaunch), the same job must
        # pass and prove an authenticated first-party Max subscription.
        max_only_env = dict(base_env)
        max_only_env.pop("ANTHROPIC_API_KEY")
        result = run([sys.executable, str(RUNNER), "preflight", "--job", str(job), "--json"], max_only_env)
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            payload = {}
        errors = []
        check(result.returncode == 0, f"Max-only preflight exit={result.returncode}: {result.stderr}", errors)
        check(payload.get("ready") is True, "Max-only preflight did not report ready", errors)
        billing_guard = payload.get("checks", {}).get("api_billing_guard", {})
        check(billing_guard.get("state") == "ready", "billing guard did not clear once the key was removed", errors)
        auth = payload.get("checks", {}).get("auth", {})
        check(auth.get("subscription_type") == "max", "Claude Max subscription not proven", errors)
        check(auth.get("api_provider") == "firstParty", "first-party API provider not proven", errors)
        serialized = json.dumps(payload)
        check("must-not-persist" not in serialized, "identity fields leaked into preflight", errors)
        check(not marker.exists(), "ANTHROPIC_API_KEY reached Claude child process", errors)
        print(("PASS" if not errors else "FAIL") + " DF-001B Max-only preflight after key removal")
        failures.extend(f"DF-001B: {error}" for error in errors)

        (worktree / "README.md").write_text("fixture\nchanged\n")
        happy_job = make_job(tmp, worktree, "DF-002")
        happy_spec = json.loads(happy_job.read_text())
        happy_env = max_only_env | {
            "FAKE_CLAUDE_MODE": "happy",
            "FAKE_HANDBACK": happy_spec["handback_file"],
        }
        result = run([sys.executable, str(RUNNER), "run", "--job", str(happy_job)], happy_env)
        evidence_path = Path(happy_spec["state_dir"]) / "evidence.json"
        evidence = json.loads(evidence_path.read_text()) if evidence_path.exists() else {}
        errors = []
        check(result.returncode == 0, f"happy worker exit={result.returncode}: {result.stderr}", errors)
        check(evidence.get("worker_outcome") == "finished", "happy worker process did not finish", errors)
        check(evidence.get("final_state") == "returned", "valid handback was not returned for review", errors)
        check(evidence.get("return_contract", {}).get("structure_valid") is True, "return contract was not structurally validated", errors)
        check(evidence.get("return_contract", {}).get("semantic_acceptance_proven") is False, "structural validation falsely granted semantic acceptance", errors)
        check(evidence.get("usage", {}).get("state") == "available", "usage was not captured", errors)
        check(
            evidence.get("usage", {}).get("counters", {}).get("input_tokens") == 12,
            "usage was double-counted from non-final stream events",
            errors,
        )
        check(evidence.get("handback", {}).get("exists") is True, "handback was not detected", errors)
        check(
            "README.md" in evidence.get("worktree", {}).get("end", {}).get("changed_paths", []),
            "Git porcelain path lost leading characters",
            errors,
        )
        check(
            evidence.get("review", {}).get("independent_codex_review_required") is True,
            "independent Codex review was not preserved",
            errors,
        )
        check("SENSITIVE RAW OUTPUT" not in json.dumps(evidence), "raw Claude output leaked into evidence", errors)
        check("waiting_setup" not in [item.get("state") for item in evidence.get("state_transitions", [])], "ordinary JSON prose caused a false setup state", errors)
        check(not prompt_marker.exists(), "brief text was exposed in the Claude process arguments", errors)
        print(("PASS" if not errors else "FAIL") + " DF-002 metadata-only evidence")
        failures.extend(f"DF-002: {error}" for error in errors)

        silent_job = make_job(tmp, worktree, "DF-003")
        silent_spec = json.loads(silent_job.read_text())
        silent_env = max_only_env | {
            "FAKE_CLAUDE_MODE": "silent",
            "FAKE_HANDBACK": silent_spec["handback_file"],
        }
        result = run([sys.executable, str(RUNNER), "run", "--job", str(silent_job)], silent_env)
        evidence_path = Path(silent_spec["state_dir"]) / "evidence.json"
        evidence = json.loads(evidence_path.read_text()) if evidence_path.exists() else {}
        states = [item.get("state") for item in evidence.get("state_transitions", [])]
        errors = []
        check(result.returncode == 0, f"silent worker exit={result.returncode}: {result.stderr}", errors)
        check("stalled" in states, "silent worker did not raise a stalled state", errors)
        check(evidence.get("worker_outcome") == "finished", "watchdog killed or misreported successful worker", errors)
        check(evidence.get("final_state") == "returned", "valid silent-worker handback was not returned for review", errors)
        check(evidence.get("usage", {}).get("state") == "unavailable", "missing usage was not honest", errors)
        print(("PASS" if not errors else "FAIL") + " DF-003 non-token silent-stall detection")
        failures.extend(f"DF-003: {error}" for error in errors)

        incomplete_job = make_job(tmp, worktree, "DF-017")
        incomplete_spec = json.loads(incomplete_job.read_text())
        incomplete_env = max_only_env | {
            "FAKE_CLAUDE_MODE": "incomplete_handback",
            "FAKE_HANDBACK": incomplete_spec["handback_file"],
        }
        result = run([sys.executable, str(RUNNER), "run", "--job", str(incomplete_job)], incomplete_env)
        evidence_path = Path(incomplete_spec["state_dir"]) / "evidence.json"
        evidence = json.loads(evidence_path.read_text()) if evidence_path.exists() else {}
        errors = []
        check(result.returncode != 0, "incomplete return artifact unexpectedly passed", errors)
        check(evidence.get("worker_outcome") == "finished", "worker process outcome was not preserved", errors)
        check(evidence.get("final_state") == "incomplete", "incomplete proof artifact was not rejected", errors)
        check(evidence.get("return_contract", {}).get("structure_valid") is False, "incomplete contract reported structurally valid", errors)
        check(evidence.get("return_contract", {}).get("semantic_acceptance_proven") is False, "incomplete contract granted semantic acceptance", errors)
        print(("PASS" if not errors else "FAIL") + " DF-017 configured return artifact validation")
        failures.extend(f"DF-017: {error}" for error in errors)

        quoted_job = make_job(tmp, worktree, "DF-018")
        quoted_spec = json.loads(quoted_job.read_text())
        quoted_env = max_only_env | {
            "FAKE_CLAUDE_MODE": "quoted_template_handback",
            "FAKE_HANDBACK": quoted_spec["handback_file"],
        }
        result = run([sys.executable, str(RUNNER), "run", "--job", str(quoted_job)], quoted_env)
        evidence = json.loads((Path(quoted_spec["state_dir"]) / "evidence.json").read_text())
        errors = []
        check(result.returncode != 0, "quoted template unexpectedly satisfied proof fields", errors)
        check(evidence.get("final_state") == "incomplete", "quoted template was not incomplete", errors)
        check(
            len(evidence.get("return_contract", {}).get("missing_proof_fields", [])) == len(PROOF_FIELDS),
            "proof fields inside a code fence were accepted",
            errors,
        )
        print(("PASS" if not errors else "FAIL") + " DF-018 quoted proof template rejection")
        failures.extend(f"DF-018: {error}" for error in errors)

        na_job = make_job(tmp, worktree, "DF-019")
        na_spec = json.loads(na_job.read_text())
        na_spec["builder_completion_proof"] = {
            "mode": "not_applicable",
            "not_applicable_reason": "read-only inventory with no implementation or behavior change",
        }
        na_job.write_text(json.dumps(na_spec, indent=2) + "\n")
        na_env = max_only_env | {
            "FAKE_CLAUDE_MODE": "not_applicable_handback",
            "FAKE_HANDBACK": na_spec["handback_file"],
        }
        result = run([sys.executable, str(RUNNER), "run", "--job", str(na_job)], na_env)
        evidence = json.loads((Path(na_spec["state_dir"]) / "evidence.json").read_text())
        errors = []
        check(result.returncode == 0, f"truthful not-applicable job exit={result.returncode}", errors)
        check(evidence.get("final_state") == "returned", "truthful not-applicable job did not return", errors)
        check(evidence.get("return_contract", {}).get("proof_mode") == "not_applicable", "not-applicable mode was not recorded", errors)
        check(evidence.get("return_contract", {}).get("semantic_acceptance_proven") is False, "not-applicable mode granted semantic acceptance", errors)
        print(("PASS" if not errors else "FAIL") + " DF-019 explicit not-applicable contract")
        failures.extend(f"DF-019: {error}" for error in errors)

        setup_job = make_job(tmp, worktree, "DF-004")
        setup_spec = json.loads(setup_job.read_text())
        setup_env = max_only_env | {"FAKE_CLAUDE_MODE": "setup"}
        result = run([sys.executable, str(RUNNER), "run", "--job", str(setup_job)], setup_env)
        evidence_path = Path(setup_spec["state_dir"]) / "evidence.json"
        evidence = json.loads(evidence_path.read_text()) if evidence_path.exists() else {}
        states = [item.get("state") for item in evidence.get("state_transitions", [])]
        errors = []
        check(result.returncode != 0, "setup-blocked worker unexpectedly passed", errors)
        check("waiting_setup" in states, "first-run/auth prompt was not classified", errors)
        check("Authentication required" not in json.dumps(evidence), "setup raw text leaked into evidence", errors)
        print(("PASS" if not errors else "FAIL") + " DF-004 first-run setup classification")
        failures.extend(f"DF-004: {error}" for error in errors)

        stale_state = tmp / "stale-state"
        stale_state.mkdir()
        (stale_state / "state.json").write_text(json.dumps({"state": "working", "pid": 99999999}) + "\n")
        result = run(
            [sys.executable, str(RUNNER), "status", "--state-dir", str(stale_state), "--json"],
            base_env,
        )
        status_payload = json.loads(result.stdout)
        errors = []
        check(status_payload.get("observed_state") == "stale", "dead worker was not reported stale", errors)
        print(("PASS" if not errors else "FAIL") + " DF-005 stale completion detection")
        failures.extend(f"DF-005: {error}" for error in errors)

        block_job = make_job(tmp, worktree, "DF-006-A", lane="shared-lane")
        block_spec = json.loads(block_job.read_text())
        contender_job = make_job(tmp, worktree, "DF-006-B", lane="different-owner-same-worktree")
        block_env = max_only_env | {
            "FAKE_CLAUDE_MODE": "blocking",
            "FAKE_HANDBACK": block_spec["handback_file"],
        }
        active = subprocess.Popen(
            [sys.executable, str(RUNNER), "run", "--job", str(block_job)],
            cwd=ROOT,
            env=block_env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        time.sleep(0.15)
        result = run(
            [sys.executable, str(RUNNER), "preflight", "--job", str(contender_job), "--json"],
            max_only_env,
        )
        active.communicate(timeout=5)
        contender = json.loads(result.stdout)
        errors = []
        check(result.returncode != 0, "lane contender unexpectedly passed preflight", errors)
        check(contender.get("checks", {}).get("lane", {}).get("state") == "busy", "lane contention not identified", errors)
        print(("PASS" if not errors else "FAIL") + " DF-006 lane contention")
        failures.extend(f"DF-006: {error}" for error in errors)

        unsafe_job = make_job(tmp, worktree, "DF-007")
        unsafe = json.loads(unsafe_job.read_text())
        unsafe["claude_args"].append("--dangerously-skip-permissions")
        unsafe_job.write_text(json.dumps(unsafe, indent=2) + "\n")
        result = run([sys.executable, str(RUNNER), "preflight", "--job", str(unsafe_job), "--json"], max_only_env)
        payload = json.loads(result.stdout)
        errors = []
        check(result.returncode != 0, "unsafe approval bypass unexpectedly passed", errors)
        check(payload.get("checks", {}).get("command", {}).get("state") == "blocked", "unsafe flag not blocked", errors)
        print(("PASS" if not errors else "FAIL") + " DF-007 approval-boundary enforcement")
        failures.extend(f"DF-007: {error}" for error in errors)

        release_job = make_job(tmp, worktree, "DF-008")
        release = json.loads(release_job.read_text())
        release["approved_stop_point"] = "production monitored"
        release_job.write_text(json.dumps(release, indent=2) + "\n")
        result = run([sys.executable, str(RUNNER), "preflight", "--job", str(release_job), "--json"], max_only_env)
        payload = json.loads(result.stdout)
        errors = []
        check(result.returncode != 0, "production delegation boundary unexpectedly passed", errors)
        check(
            payload.get("checks", {}).get("boundary", {}).get("state") == "blocked",
            "merge/deploy/production stop point was not blocked",
            errors,
        )
        print(("PASS" if not errors else "FAIL") + " DF-008 no automatic production lane")
        failures.extend(f"DF-008: {error}" for error in errors)

        unmonitored_state = tmp / "unmonitored-state"
        unmonitored_state.mkdir()
        now = "2026-07-22T00:00:00+00:00"
        (unmonitored_state / "state.json").write_text(
            json.dumps(
                {
                    "state": "working",
                    "pid": os.getpid(),
                    "watchdog_pid": 99999999,
                    "heartbeat_at": now,
                    "last_worker_event_at": now,
                }
            )
            + "\n"
        )
        result = run(
            [sys.executable, str(RUNNER), "status", "--state-dir", str(unmonitored_state), "--json"],
            base_env,
        )
        payload = json.loads(result.stdout)
        errors = []
        check(payload.get("observed_state") == "unmonitored", "dead watchdog was not detected", errors)
        check(payload.get("worker_alive") is True, "live worker was misreported dead", errors)
        print(("PASS" if not errors else "FAIL") + " DF-009 dead-watchdog detection")
        failures.extend(f"DF-009: {error}" for error in errors)

        # DF-010: the CLI's own reported billing identity is the authoritative
        # signal, independent of the parent shell's environment. An API-key
        # authenticated session must fail closed even with no inherited key.
        api_key_auth_job = make_job(tmp, worktree, "DF-010")
        api_key_auth_env = max_only_env | {"FAKE_AUTH_MODE": "api_key"}
        result = run(
            [sys.executable, str(RUNNER), "preflight", "--job", str(api_key_auth_job), "--json"],
            api_key_auth_env,
        )
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
        errors = []
        check(result.returncode != 0, "API-key authenticated session unexpectedly passed preflight", errors)
        check(payload.get("ready") is False, "API-key authenticated session did not fail closed", errors)
        auth = payload.get("checks", {}).get("auth", {})
        check(auth.get("state") == "failed", "API-key billing mode was not reported as failed auth", errors)
        check(auth.get("api_provider") == "anthropic", "API provider identity was not preserved for diagnosis", errors)
        print(("PASS" if not errors else "FAIL") + " DF-010 API-billed auth refusal")
        failures.extend(f"DF-010: {error}" for error in errors)

        # DF-011: an ambiguous auth response (missing subscription/provider
        # fields) must never be treated as a proven Max subscription.
        ambiguous_auth_job = make_job(tmp, worktree, "DF-011")
        ambiguous_auth_env = max_only_env | {"FAKE_AUTH_MODE": "ambiguous"}
        result = run(
            [sys.executable, str(RUNNER), "preflight", "--job", str(ambiguous_auth_job), "--json"],
            ambiguous_auth_env,
        )
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
        errors = []
        check(result.returncode != 0, "ambiguous auth unexpectedly passed preflight", errors)
        check(payload.get("ready") is False, "ambiguous auth did not fail closed", errors)
        auth = payload.get("checks", {}).get("auth", {})
        check(auth.get("state") == "failed", "ambiguous auth was not reported as failed", errors)
        print(("PASS" if not errors else "FAIL") + " DF-011 ambiguous auth refusal")
        failures.extend(f"DF-011: {error}" for error in errors)

        # DF-011B: reproduces the reported incident directly. `authMethod` and
        # `subscriptionType` alone can both look like a genuine Max login while
        # `apiProvider` shows the request is actually routed through metered API
        # billing. Checking only the first two fields would incorrectly pass.
        max_billed_job = make_job(tmp, worktree, "DF-011B")
        max_billed_env = max_only_env | {"FAKE_AUTH_MODE": "max_login_api_billed"}
        result = run(
            [sys.executable, str(RUNNER), "preflight", "--job", str(max_billed_job), "--json"],
            max_billed_env,
        )
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
        errors = []
        check(result.returncode != 0, "Max-labeled login with API billing unexpectedly passed preflight", errors)
        check(payload.get("ready") is False, "Max-labeled login with API billing did not fail closed", errors)
        auth = payload.get("checks", {}).get("auth", {})
        check(auth.get("state") == "failed", "apiProvider billing mismatch was not reported as failed auth", errors)
        check(auth.get("subscription_type") == "max", "diagnostic subscription_type was not preserved", errors)
        check(auth.get("api_provider") == "anthropic", "diagnostic api_provider was not preserved", errors)
        print(("PASS" if not errors else "FAIL") + " DF-011B Max login with API-billed provider refusal")
        failures.extend(f"DF-011B: {error}" for error in errors)

        # DF-012: a well-formed paid_evaluation declaration (approved_by, a
        # positive estimate, and a hard cap at or above the estimate) is
        # accepted as audit metadata and does not block an otherwise-ready job.
        valid_paid_job = make_job(tmp, worktree, "DF-012")
        valid_paid_spec = json.loads(valid_paid_job.read_text())
        valid_paid_spec["paid_evaluation"] = {
            "approved_by": "Hafiz Razali",
            "estimate_usd": 5.0,
            "hard_cap_usd": 10.0,
        }
        valid_paid_job.write_text(json.dumps(valid_paid_spec, indent=2) + "\n")
        result = run([sys.executable, str(RUNNER), "preflight", "--job", str(valid_paid_job), "--json"], max_only_env)
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
        errors = []
        check(result.returncode == 0, f"valid paid_evaluation exit={result.returncode}: {result.stderr}", errors)
        check(payload.get("ready") is True, "valid paid_evaluation metadata unexpectedly blocked the job", errors)
        paid = payload.get("checks", {}).get("paid_evaluation", {})
        check(paid.get("state") == "ready", "valid paid_evaluation metadata was not accepted", errors)
        check(paid.get("declared") is True, "paid_evaluation declaration was not recorded", errors)
        check(paid.get("trust") == "untrusted_job_declaration", "job metadata was presented as trusted approval", errors)
        check(paid.get("proves_human_approval") is False, "job metadata incorrectly claimed to prove approval", errors)
        check(paid.get("executes_paid_billing") is False, "paid_evaluation metadata must never claim execution authority", errors)
        print(("PASS" if not errors else "FAIL") + " DF-012 valid untrusted paid-evaluation metadata")
        failures.extend(f"DF-012: {error}" for error in errors)

        # DF-013: an incomplete or invalid paid_evaluation declaration (missing
        # approver, non-positive estimate, or a hard cap below the estimate)
        # must fail closed with the specific field errors.
        invalid_paid_job = make_job(tmp, worktree, "DF-013")
        invalid_paid_spec = json.loads(invalid_paid_job.read_text())
        invalid_paid_spec["paid_evaluation"] = {
            "approved_by": "",
            "estimate_usd": 25.0,
            "hard_cap_usd": 10.0,
        }
        invalid_paid_job.write_text(json.dumps(invalid_paid_spec, indent=2) + "\n")
        result = run([sys.executable, str(RUNNER), "preflight", "--job", str(invalid_paid_job), "--json"], max_only_env)
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
        errors = []
        check(result.returncode != 0, "invalid paid_evaluation metadata unexpectedly passed preflight", errors)
        check(payload.get("ready") is False, "invalid paid_evaluation metadata did not fail closed", errors)
        paid = payload.get("checks", {}).get("paid_evaluation", {})
        check(paid.get("state") == "blocked", "invalid paid_evaluation metadata was not blocked", errors)
        paid_errors = " ".join(paid.get("errors", []))
        check("approved_by" in paid_errors, "missing approver was not reported", errors)
        check("hard_cap_usd" in paid_errors, "hard cap below estimate was not reported", errors)
        print(("PASS" if not errors else "FAIL") + " DF-013 invalid paid-evaluation planning metadata")
        failures.extend(f"DF-013: {error}" for error in errors)

        # DF-014: a valid paid_evaluation declaration must never unlock the
        # inherited ANTHROPIC_API_KEY. This is the anti-bypass regression: this
        # Max-only watchdog never launches Claude with API billing, no matter
        # what a locally-editable job file claims.
        bypass_job = make_job(tmp, worktree, "DF-014")
        bypass_spec = json.loads(bypass_job.read_text())
        bypass_spec["paid_evaluation"] = {
            "approved_by": "Hafiz Razali",
            "estimate_usd": 5.0,
            "hard_cap_usd": 10.0,
        }
        bypass_job.write_text(json.dumps(bypass_spec, indent=2) + "\n")
        bypass_probe_marker = tmp / "df-014-probe-marker"
        bypass_env = base_env | {"FAKE_PROBE_MARKER": str(bypass_probe_marker)}
        result = run([sys.executable, str(RUNNER), "preflight", "--job", str(bypass_job), "--json"], bypass_env)
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
        errors = []
        check(result.returncode != 0, "declared paid_evaluation unlocked the inherited API key", errors)
        check(payload.get("ready") is False, "declared paid_evaluation bypassed the billing guard", errors)
        billing_guard = payload.get("checks", {}).get("api_billing_guard", {})
        check(billing_guard.get("state") == "blocked", "billing guard did not block despite a declared paid_evaluation", errors)
        check(not bypass_probe_marker.exists(), "Claude was probed despite the inherited API key", errors)
        serialized = json.dumps(payload)
        check("fixture-key-must-be-unset" not in serialized, "the API key value leaked into preflight output", errors)
        print(("PASS" if not errors else "FAIL") + " DF-014 paid-evaluation metadata cannot unlock API billing")
        failures.extend(f"DF-014: {error}" for error in errors)

        # DF-015: every supported auth, endpoint, or provider override fails
        # before the first Claude probe and its value never enters output.
        billing_overrides = [
            "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "ANTHROPIC_CUSTOM_HEADERS",
            "ANTHROPIC_BEDROCK_BASE_URL", "ANTHROPIC_BEDROCK_MANTLE_BASE_URL",
            "ANTHROPIC_VERTEX_BASE_URL", "ANTHROPIC_VERTEX_PROJECT_ID",
            "ANTHROPIC_FOUNDRY_BASE_URL", "ANTHROPIC_FOUNDRY_RESOURCE",
            "ANTHROPIC_FOUNDRY_API_KEY", "ANTHROPIC_FOUNDRY_AUTH_TOKEN",
            "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY",
            "CLAUDE_CODE_USE_MANTLE",
            "CLAUDE_CODE_USE_ANTHROPIC_AWS",
        ]
        df_015_errors: list[str] = []
        for variable in billing_overrides:
            override_job = make_job(tmp, worktree, f"DF-015-{variable}")
            override_probe = tmp / f"df-015-{variable}-probe"
            override_env = max_only_env | {
                variable: "fixture-value-must-not-reach-claude",
                "FAKE_PROBE_MARKER": str(override_probe),
            }
            result = run([sys.executable, str(RUNNER), "preflight", "--job", str(override_job), "--json"], override_env)
            payload = json.loads(result.stdout) if result.stdout.strip() else {}
            billing_guard = payload.get("checks", {}).get("api_billing_guard", {})
            check(result.returncode != 0, f"{variable} unexpectedly passed preflight", df_015_errors)
            check(billing_guard.get("state") == "blocked", f"{variable} was not blocked", df_015_errors)
            check(billing_guard.get("blocked_variable_names") == [variable], f"{variable} was not identified by name", df_015_errors)
            check(not override_probe.exists(), f"Claude was probed with inherited {variable}", df_015_errors)
            check("fixture-value-must-not-reach-claude" not in json.dumps(payload), f"{variable} value leaked", df_015_errors)
        print(("PASS" if not df_015_errors else "FAIL") + " DF-015 alternate billing override refusal")
        failures.extend(f"DF-015: {error}" for error in df_015_errors)

        # DF-020: a job that names no model inherits whatever the workspace
        # selected. That is the reported #100 launch failure, so preflight must
        # refuse it before launch and explain the fix as metadata only.
        no_model_job = make_job(tmp, worktree, "DF-020", model_args=[])
        result = run([sys.executable, str(RUNNER), "preflight", "--job", str(no_model_job), "--json"], max_only_env)
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
        errors = []
        check(result.returncode != 0, "job without an explicit model unexpectedly passed preflight", errors)
        check(payload.get("ready") is False, "job without an explicit model did not fail closed", errors)
        model_check = payload.get("checks", {}).get("model_selection", {})
        check(model_check.get("state") == "blocked", "missing explicit model was not blocked", errors)
        check(model_check.get("explicit_model_selected") is False, "missing model selection was not reported", errors)
        check(bool(model_check.get("required_action")), "missing model block gave no remediation", errors)
        check("model" not in model_check, "a model was silently chosen inside the runner", errors)
        print(("PASS" if not errors else "FAIL") + " DF-020 implicit model selection refused")
        failures.extend(f"DF-020: {error}" for error in errors)

        # DF-021: both CLI spellings of an explicit selection are accepted, and
        # a `--model` with no usable value is still refused.
        errors = []
        for label, model_args in (
            ("pair", ["--model", "opus"]),
            ("joined", ["--model=opus"]),
        ):
            accepted_job = make_job(tmp, worktree, f"DF-021-{label}", model_args=model_args)
            result = run([sys.executable, str(RUNNER), "preflight", "--job", str(accepted_job), "--json"], max_only_env)
            payload = json.loads(result.stdout) if result.stdout.strip() else {}
            model_check = payload.get("checks", {}).get("model_selection", {})
            check(result.returncode == 0, f"{label} --model form exit={result.returncode}: {result.stderr}", errors)
            check(payload.get("ready") is True, f"{label} --model form did not report ready", errors)
            check(model_check.get("state") == "ready", f"{label} --model form was not accepted", errors)
            check(model_check.get("model") == "opus", f"{label} --model form lost the selected alias", errors)
        dangling_job = make_job(tmp, worktree, "DF-021-dangling", model_args=["--model"])
        result = run([sys.executable, str(RUNNER), "preflight", "--job", str(dangling_job), "--json"], max_only_env)
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
        check(result.returncode != 0, "a --model flag with no value unexpectedly passed preflight", errors)
        check(
            payload.get("checks", {}).get("model_selection", {}).get("state") == "blocked",
            "a --model flag with no value was not blocked",
            errors,
        )
        print(("PASS" if not errors else "FAIL") + " DF-021 explicit model selection accepted")
        failures.extend(f"DF-021: {error}" for error in errors)

        # DF-022: reproduces the reported #100 terminal failure. A zero-token
        # HTTP 400 result must leave enough safe metadata to diagnose the
        # launch, and none of its raw result text or secret-looking values.
        error_job = make_job(tmp, worktree, "DF-022")
        error_spec = json.loads(error_job.read_text())
        error_env = max_only_env | {
            "FAKE_CLAUDE_MODE": "api_error_400",
            "FAKE_HANDBACK": error_spec["handback_file"],
        }
        result = run([sys.executable, str(RUNNER), "run", "--job", str(error_job)], error_env)
        state_dir = Path(error_spec["state_dir"])
        evidence = json.loads((state_dir / "evidence.json").read_text())
        markdown = (state_dir / "evidence.md").read_text()
        diagnostic = evidence.get("terminal_diagnostic", {})
        errors = []
        check(result.returncode != 0, "a failed API launch unexpectedly reported success", errors)
        check(evidence.get("final_state") == "failed", "zero-token API failure was not reported as failed", errors)
        check(evidence.get("worker_exit_code") != 0, "nonzero worker exit was not preserved", errors)
        check(diagnostic.get("result_seen") is True, "terminal result event was not recorded", errors)
        check(diagnostic.get("result_is_error") is True, "result error flag was not recorded", errors)
        check(diagnostic.get("api_error_status") == 400, "HTTP status was not recorded", errors)
        check(diagnostic.get("terminal_reason") == "api_error", "terminal reason was not recorded", errors)
        check(diagnostic.get("stop_reason") == "stop_sequence", "stop reason was not recorded", errors)
        check(diagnostic.get("result_turns") == 1, "turn count was not recorded", errors)
        check(diagnostic.get("permission_denial_count") == 0, "permission-denial count was not recorded", errors)
        check(diagnostic.get("stderr_lines") == 0, "stderr line count was not recorded", errors)
        check(diagnostic.get("category") == "invalid_request", "known failure category was not classified", errors)
        check(diagnostic.get("raw_worker_output_stored") is False, "diagnostic did not restate the raw-output contract", errors)
        check(evidence.get("model_selected") == "opus", "the selected model was not recorded for diagnosis", errors)
        check(
            evidence.get("usage", {}).get("counters", {}).get("output_tokens") == 0,
            "zero-token failure did not preserve honest usage counters",
            errors,
        )
        serialized = json.dumps(evidence)
        for secret in ("SENSITIVE RAW OUTPUT", "sk-ant-fixture-secret-value", "invalid request SENSITIVE"):
            check(secret not in serialized, f"raw result text {secret!r} leaked into evidence.json", errors)
            check(secret not in markdown, f"raw result text {secret!r} leaked into evidence.md", errors)
        check("api_error_status=400" in markdown, "evidence markdown does not surface the HTTP status", errors)
        check("result_is_error=true" in markdown, "evidence markdown does not surface the result error flag", errors)
        check("Worker failed" in markdown, "evidence markdown does not make a failed worker obvious", errors)
        print(("PASS" if not errors else "FAIL") + " DF-022 safe zero-token API failure diagnostic")
        failures.extend(f"DF-022: {error}" for error in errors)

        # DF-023: a successful worker whose own prose contains failure-sounding
        # phrases must not be labelled with a failure category.
        prose_job = make_job(tmp, worktree, "DF-023")
        prose_spec = json.loads(prose_job.read_text())
        prose_env = max_only_env | {
            "FAKE_CLAUDE_MODE": "happy",
            "FAKE_HANDBACK": prose_spec["handback_file"],
        }
        result = run([sys.executable, str(RUNNER), "run", "--job", str(prose_job)], prose_env)
        evidence = json.loads((Path(prose_spec["state_dir"]) / "evidence.json").read_text())
        diagnostic = evidence.get("terminal_diagnostic", {})
        errors = []
        check(result.returncode == 0, f"prose fixture exit={result.returncode}: {result.stderr}", errors)
        check(diagnostic.get("category") is None, "ordinary assistant prose produced a false failure category", errors)
        check(diagnostic.get("result_is_error") is None, "a result without is_error was reported as errored", errors)
        check(diagnostic.get("result_seen") is True, "successful terminal result was not recorded", errors)
        print(("PASS" if not errors else "FAIL") + " DF-023 no false failure category from worker prose")
        failures.extend(f"DF-023: {error}" for error in errors)

        # DF-024: issue #110's exact failure mode. A successful worker may put
        # the complete return contract in the terminal result but omit the
        # requested file. The runner may recover only that final result after
        # the same structural and secret checks used for a normal handback.
        recovery_job = make_job(tmp, worktree, "DF-024")
        recovery_spec = json.loads(recovery_job.read_text())
        recovery_env = max_only_env | {
            "FAKE_CLAUDE_MODE": "missing_handback_result",
            "FAKE_HANDBACK": recovery_spec["handback_file"],
        }
        result = run([sys.executable, str(RUNNER), "run", "--job", str(recovery_job)], recovery_env)
        evidence = json.loads((Path(recovery_spec["state_dir"]) / "evidence.json").read_text())
        errors = []
        check(result.returncode == 0, f"recoverable missing handback exit={result.returncode}: {result.stderr}", errors)
        check(evidence.get("final_state") == "returned", "safe terminal result was not returned for review", errors)
        check(evidence.get("handback", {}).get("exists") is True, "recovered handback file was not created", errors)
        check(evidence.get("handback_recovery", {}).get("recovered") is True, "recovery was not recorded", errors)
        check(evidence.get("return_contract", {}).get("structure_valid") is True, "recovered handback bypassed contract validation", errors)
        check(evidence.get("return_contract", {}).get("semantic_acceptance_proven") is False, "recovery falsely granted acceptance", errors)
        check("Recovered fixture handback" not in json.dumps(evidence), "recovered result text leaked into metadata evidence", errors)
        print(("PASS" if not errors else "FAIL") + " DF-024 safe missing-handback recovery")
        failures.extend(f"DF-024: {error}" for error in errors)

        # DF-025: a structurally complete terminal result containing a
        # credential-shaped value must remain incomplete and must never be
        # persisted merely because the worker exited successfully.
        secret_job = make_job(tmp, worktree, "DF-025")
        secret_spec = json.loads(secret_job.read_text())
        secret_env = max_only_env | {
            "FAKE_CLAUDE_MODE": "missing_handback_secret_result",
            "FAKE_HANDBACK": secret_spec["handback_file"],
        }
        result = run([sys.executable, str(RUNNER), "run", "--job", str(secret_job)], secret_env)
        evidence = json.loads((Path(secret_spec["state_dir"]) / "evidence.json").read_text())
        errors = []
        check(result.returncode != 0, "credential-bearing terminal result unexpectedly passed", errors)
        check(evidence.get("final_state") == "incomplete", "credential-bearing result was not left incomplete", errors)
        check(evidence.get("handback", {}).get("exists") is False, "credential-bearing result was persisted", errors)
        check(evidence.get("handback_recovery", {}).get("credential_findings", 0) >= 1, "credential rejection was not recorded", errors)
        fixture_token = "sk-ant-" + "abcdefghijklmnopqrstuvwxyz123456"
        check(fixture_token not in json.dumps(evidence), "credential leaked into metadata evidence", errors)
        print(("PASS" if not errors else "FAIL") + " DF-025 credential-bearing result rejection")
        failures.extend(f"DF-025: {error}" for error in errors)

        # DF-026: ordinary success prose is not a substitute for the configured
        # return contract. Recovery remains incomplete rather than manufacturing
        # evidence or silently accepting the worker's claim.
        invalid_job = make_job(tmp, worktree, "DF-026")
        invalid_spec = json.loads(invalid_job.read_text())
        invalid_env = max_only_env | {
            "FAKE_CLAUDE_MODE": "missing_handback_invalid_result",
            "FAKE_HANDBACK": invalid_spec["handback_file"],
        }
        result = run([sys.executable, str(RUNNER), "run", "--job", str(invalid_job)], invalid_env)
        evidence = json.loads((Path(invalid_spec["state_dir"]) / "evidence.json").read_text())
        errors = []
        check(result.returncode != 0, "unstructured terminal prose unexpectedly passed", errors)
        check(evidence.get("final_state") == "incomplete", "unstructured result was not left incomplete", errors)
        check(evidence.get("handback", {}).get("exists") is False, "unstructured result was persisted", errors)
        check(evidence.get("handback_recovery", {}).get("recovered") is False, "invalid recovery was reported successful", errors)
        print(("PASS" if not errors else "FAIL") + " DF-026 invalid result remains incomplete")
        failures.extend(f"DF-026: {error}" for error in errors)

        # DF-027: an error-shaped terminal result can still exit 0 and carry a
        # complete-looking contract. Capture must use the module's centralized
        # error classification rather than a bare `is_error is not True` test,
        # and the latest result is authoritative, so an error-shaped result also
        # discards the earlier safe candidate instead of leaving it recoverable.
        error_result_job = make_job(tmp, worktree, "DF-027")
        error_result_spec = json.loads(error_result_job.read_text())
        error_result_env = max_only_env | {
            "FAKE_CLAUDE_MODE": "missing_handback_error_result",
            "FAKE_HANDBACK": error_result_spec["handback_file"],
        }
        result = run([sys.executable, str(RUNNER), "run", "--job", str(error_result_job)], error_result_env)
        evidence = json.loads((Path(error_result_spec["state_dir"]) / "evidence.json").read_text())
        errors = []
        check(result.returncode != 0, "error-shaped exit-0 result unexpectedly passed", errors)
        check(evidence.get("final_state") == "incomplete", "error-shaped result was not left incomplete", errors)
        check(evidence.get("handback", {}).get("exists") is False, "error-shaped result was persisted as a handback", errors)
        check(evidence.get("handback_recovery", {}).get("recovered") is False, "error-result recovery was reported successful", errors)
        check(evidence.get("handback_recovery", {}).get("attempted") is False, "stale pre-error candidate survived the error-shaped result", errors)
        check(
            evidence.get("liveness", {}).get("event_counts", {}).get("result:error_max_turns") == 1,
            "the error-shaped result event never reached the watchdog",
            errors,
        )
        check(evidence.get("terminal_diagnostic", {}).get("result_seen") is True, "terminal result was not observed", errors)
        check(not Path(error_result_spec["handback_file"]).exists(), "error-shaped result left a handback artifact", errors)
        check("Recovered fixture handback" not in json.dumps(evidence), "error-result text leaked into metadata evidence", errors)
        print(("PASS" if not errors else "FAIL") + " DF-027 error-shaped exit-0 result rejection")
        failures.extend(f"DF-027: {error}" for error in errors)

        # DF-028: a filesystem failure inside recovery must fail closed without
        # costing the evidence this watchdog exists to preserve. A worker that
        # leaves a directory at the handback path makes every recovery write
        # fail, and evidence.json plus evidence.md must still be written.
        unwritable_job = make_job(tmp, worktree, "DF-028")
        unwritable_spec = json.loads(unwritable_job.read_text())
        unwritable_env = max_only_env | {
            "FAKE_CLAUDE_MODE": "missing_handback_directory_result",
            "FAKE_HANDBACK": unwritable_spec["handback_file"],
        }
        result = run([sys.executable, str(RUNNER), "run", "--job", str(unwritable_job)], unwritable_env)
        unwritable_state = Path(unwritable_spec["state_dir"])
        errors = []
        check(result.returncode != 0, "unwritable recovery path unexpectedly passed", errors)
        check((unwritable_state / "evidence.json").is_file(), "recovery filesystem failure destroyed evidence.json", errors)
        check((unwritable_state / "evidence.md").is_file(), "recovery filesystem failure destroyed evidence.md", errors)
        if (unwritable_state / "evidence.json").is_file():
            evidence = json.loads((unwritable_state / "evidence.json").read_text())
            check(evidence.get("final_state") == "incomplete", "unwritable recovery path was not left incomplete", errors)
            check(evidence.get("handback", {}).get("exists") is False, "directory handback path was reported as a file", errors)
            check(evidence.get("handback_recovery", {}).get("attempted") is True, "recovery was not attempted before the filesystem failure", errors)
            check(evidence.get("handback_recovery", {}).get("recovered") is False, "unwritable recovery was reported successful", errors)
            check("Recovered fixture handback" not in json.dumps(evidence), "recovered result text leaked into metadata evidence", errors)
        check(
            not Path(unwritable_spec["handback_file"] + ".recovery.tmp").exists(),
            "recovery temporary file was left behind after the filesystem failure",
            errors,
        )
        print(("PASS" if not errors else "FAIL") + " DF-028 recovery filesystem failure preserves evidence")
        failures.extend(f"DF-028: {error}" for error in errors)

    if failures:
        for failure in failures:
            print(f"  - {failure}")
        print(f"agent-os-claude-delegation-fixtures: FAIL ({len(failures)} issue(s))")
        return 1
    print("agent-os-claude-delegation-fixtures: 30/30 passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
