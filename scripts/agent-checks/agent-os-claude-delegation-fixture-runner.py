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

args = sys.argv[1:]
if args[:2] == ["auth", "status"]:
    print(json.dumps({
        "loggedIn": True,
        "authMethod": "claude.ai",
        "apiProvider": "firstParty",
        "subscriptionType": "max",
        "email": "must-not-persist@example.test",
        "orgId": "must-not-persist",
    }))
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
        base_env = os.environ.copy()
        base_env["PATH"] = f"{fake_bin}{os.pathsep}{base_env.get('PATH', '')}"
        base_env["ANTHROPIC_API_KEY"] = "fixture-key-must-be-unset"
        base_env["FAKE_API_KEY_MARKER"] = str(marker)
        base_env["FAKE_PROMPT_ARG_MARKER"] = str(prompt_marker)

        job = make_job(tmp, worktree, "DF-001")
        result = run([sys.executable, str(RUNNER), "preflight", "--job", str(job), "--json"], base_env)
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            payload = {}
        errors: list[str] = []
        check(result.returncode == 0, f"preflight exit={result.returncode}: {result.stderr}", errors)
        check(payload.get("ready") is True, "preflight did not report ready", errors)
        auth = payload.get("checks", {}).get("auth", {})
        check(auth.get("subscription_type") == "max", "Claude Max subscription not proven", errors)
        serialized = json.dumps(payload)
        check("must-not-persist" not in serialized, "identity fields leaked into preflight", errors)
        check(not marker.exists(), "ANTHROPIC_API_KEY reached Claude child process", errors)
        print(("PASS" if not errors else "FAIL") + " DF-001 filtered Claude Max preflight")
        failures.extend(f"DF-001: {error}" for error in errors)

        (worktree / "README.md").write_text("fixture\nchanged\n")
        happy_job = make_job(tmp, worktree, "DF-002")
        happy_spec = json.loads(happy_job.read_text())
        happy_env = base_env | {
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
        silent_env = base_env | {
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
        setup_env = base_env | {"FAKE_CLAUDE_MODE": "setup"}
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
        block_env = base_env | {
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
            base_env,
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
        result = run([sys.executable, str(RUNNER), "preflight", "--job", str(unsafe_job), "--json"], base_env)
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
        result = run([sys.executable, str(RUNNER), "preflight", "--job", str(release_job), "--json"], base_env)
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

    if failures:
        for failure in failures:
            print(f"  - {failure}")
        print(f"agent-os-claude-delegation-fixtures: FAIL ({len(failures)} issue(s))")
        return 1
    print("agent-os-claude-delegation-fixtures: 9/9 passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
