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
if mode == "setup":
    print("Authentication required before continuing", file=sys.stderr, flush=True)
    time.sleep(0.08)
    raise SystemExit(3)
if mode in {"silent", "blocking"}:
    time.sleep(0.30 if mode == "silent" else 0.75)
    if handback:
        Path(handback).write_text("# Fixture handback\n\nCompleted without raw output capture.\n")
    raise SystemExit(0)

print(json.dumps({"type": "system", "subtype": "init", "session_id": "fixture-session"}), flush=True)
print(json.dumps({"type": "assistant", "usage": {"input_tokens": 999}, "message": {"content": [{"type": "text", "text": "SENSITIVE RAW OUTPUT and authentication required as ordinary prose"}]}}), flush=True)
print(json.dumps({"type": "result", "subtype": "success", "usage": {"input_tokens": 12, "output_tokens": 7}}), flush=True)
if handback:
    Path(handback).write_text("# Fixture handback\n\nCompleted without secrets.\n")
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


def make_job(base: Path, worktree: Path, job_id: str, lane: str = "fixture-lane") -> Path:
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
        check(evidence.get("final_state") == "finished", "happy worker did not finish", errors)
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
        check(evidence.get("final_state") == "finished", "watchdog killed or misreported successful worker", errors)
        check(evidence.get("usage", {}).get("state") == "unavailable", "missing usage was not honest", errors)
        print(("PASS" if not errors else "FAIL") + " DF-003 non-token silent-stall detection")
        failures.extend(f"DF-003: {error}" for error in errors)

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

    if failures:
        for failure in failures:
            print(f"  - {failure}")
        print(f"agent-os-claude-delegation-fixtures: FAIL ({len(failures)} issue(s))")
        return 1
    print("agent-os-claude-delegation-fixtures: 17/17 passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
