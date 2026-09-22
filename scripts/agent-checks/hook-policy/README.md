# hook-policy

Issue [#161](https://github.com/hafizrazali90/sifututor-agent-os/issues/161),
bundle 8: a standalone, consolidated command-safety dispatcher module, plus
fixtures proving it behaves identically to today's scattered hooks for
representative inputs.

**This module is inert.** Nothing here is imported by any live
`.claude/hooks/*.py` file, `.codex/config.toml`, `codex-pre-tool-use.py`, or
any `settings.json` hook registration, anywhere in this repo or in the
sibling `~/Projects/Sifututor` sub-projects. It is a proposal awaiting a
separate, careful cutover decision — see the PR body for the full
statement, and `SURVEY.md` for exactly what was read (never modified) to
build it.

## Read first

`SURVEY.md` — what each existing hook actually does (inputs, decision
logic, outputs), read from the real scripts, not from memory. Includes two
genuine findings made while writing this module's parity fixtures: a
drifted `validate-branch-name.py` copy in `sifu-tutor`, and a regex bug in
`codex-pre-tool-use.py`'s `git checkout --` guard that makes it miss the
common `git checkout -- <path>` form.

## Layout

```text
models.py                          Decision/Outcome/Severity/HookRequest — the shared vocabulary
dispatcher.py                      HookDispatcher: runs checks, timeout-wraps expensive ones,
                                    enforces required->block / advisory->degrade on failure
hook_output.py                     One DispatchResult -> hookSpecificOutput JSON formatter

check_branch_name.py               mirrors .claude/hooks/validate-branch-name.py
check_commit_message.py            mirrors .claude/hooks/conventional-commits.py
check_heredoc_guard.py             mirrors codex-pre-tool-use.py's HEREDOC-commit block
check_codex_safety_guards.py       mirrors codex-pre-tool-use.py's --no-verify / reset --hard /
                                    checkout -- / rm -rf live| .workflow-rollout / .env-read guards
check_command_safety.py            thin wrapper around the REAL secret_output_guard.evaluate_command
check_quality_gate.py              config-driven version of ripple-suite's quality-gate.py
check_workflow_gate.py             config-driven version of ripple-suite's workflow-gate.py
check_expensive_examples.py        two representative network/model-backed check shapes
                                    (REQUIRED + ADVISORY), backend injected -- see its docstring

default_checks.py                  the concrete "one shared list" assembly (build item 2)
adapter_claude.py                  thin Claude PreToolUse payload -> HookRequest -> hook JSON
adapter_codex.py                   thin Codex PreToolUse payload -> HookRequest -> hook JSON

measure.py                         measurement harness (build item 3) -- run directly for a report

fixtures/originals/README.md       what "original" means for each parity test
fixtures/originals/ripple_quality_gate_snapshot.py    frozen 2026-09-22 snapshot, parity-test-only
fixtures/originals/ripple_workflow_gate_snapshot.py   frozen 2026-09-22 snapshot, parity-test-only

test_models.py, test_check_*.py, test_dispatcher.py, test_hook_output.py,
test_default_checks.py, test_adapter_*.py, test_measure.py
                                    unit tests, one per module above

test_parity_branch_name.py         BranchNameCheck vs the REAL validate-branch-name.py AND
                                    the REAL codex-pre-tool-use.py, by subprocess, live paths
test_parity_commit_message.py      CommitMessageCheck vs the REAL conventional-commits.py
test_parity_heredoc_guard.py       HeredocCommitGuard vs the REAL codex-pre-tool-use.py
test_parity_codex_safety_guards.py the three codex safety guards vs the REAL codex-pre-tool-use.py
test_parity_quality_gate.py        QualityGateCheck vs the frozen quality-gate.py snapshot,
                                    in a real temp git repo
test_parity_workflow_gate.py       WorkflowGateCheck vs the frozen workflow-gate.py snapshot,
                                    against real temp .claude/tasks/ files
```

No `__init__.py` / package structure, matching the sibling `decision-layer/`
module's convention: flat files, each test inserts its own directory onto
`sys.path`, run with `unittest discover`.

## Run the tests

```bash
cd scripts/agent-checks/hook-policy
python3 -m unittest discover -s . -p 'test_*.py'
```

or, from the repo root:

```bash
python3 -m unittest discover -s scripts/agent-checks/hook-policy -p 'test_*.py'
```

## Run the measurement harness

```bash
python3 scripts/agent-checks/hook-policy/measure.py
```

Prints a JSON report: fixture count, route accuracy, false-block rate,
dispatch latency (mean/median/max, ms), startup cost (cold-import time +
raw source size, both explicitly labeled as proxies), and token/cost
(explicitly `null` — no real per-hook token/cost meter exists in this repo;
see `measure.py`'s docstring for exactly why that figure is not fabricated).

## What "parity" means here

Two different techniques are used, both explained in `fixtures/originals/README.md`:

1. For hooks that already live inside **this** repo (`validate-branch-name.py`,
   `conventional-commits.py`, `codex-pre-tool-use.py`) — the parity tests
   invoke the real file, by its real path, as a subprocess. No copy exists.
2. For hooks that live in a **sibling** repo (`ripple-suite`'s
   `quality-gate.py` / `workflow-gate.py`) — a byte-for-byte snapshot, taken
   and dated, lives in `fixtures/originals/` so the test is hermetic and
   reviewable inside this PR. `check_command_safety.py` uses neither
   technique: it imports and calls the real
   `scripts/agent-checks/secret_output_guard.py` function directly, because
   that module is already the one shared implementation every existing hook
   is supposed to route through.
