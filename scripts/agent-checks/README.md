# Agent Checks

Shared guardrail scripts for Claude, Codex, and any other coding agent.

These scripts are the portable safety layer underneath Claude hooks, Codex
hooks, and manual workflows. Run them explicitly before commit or any risky
change.

Codex hook scripts have been direct-tested with sample hook payloads in this
workspace. Codex may still require `/hooks` trust review before project-local
hooks run in a new UI/CLI session.

## Checks

```bash
scripts/agent-checks/pre-commit-guard.sh
```

Runs:

- branch name validation
- sensitive path check
- Mission Ledger structure and parent-link check
- active task state summary

These checks are intentionally conservative. A failing check means stop and ask
the user or run the project-specific Claude workflow step.

Sensitive path matching has a focused fixture runner:

```bash
scripts/agent-checks/check-sensitive-paths-fixture-runner.sh
```

## Project Registry Consistency

```bash
scripts/agent-checks/agent-os-project-registry-check.py
scripts/agent-checks/agent-os-project-registry-check.py --json
```

The same "which projects are active" fact is repeated in `AGENTS.md`, the
workflow doctor, the workspace snapshot, the Claude and Codex Koda intent
routers, the Koda fixture allowlist, the response-shape project tag markers,
and several playbook tables. This check parses each of those live lists and
fails when they stop agreeing:

- `team-inbox` is retired and must not appear as an active project or as a
  valid Koda project tag
- `finch-inbox`, `cx-call-capture-android`, and `sims-owner-analytics` must
  appear in every live list
- the Claude and Codex project alias maps must be identical, so the same prompt
  routes to the same project in both adapters

Historical statements are left alone on purpose. Past reports, migration notes,
backup-branch records, and archived-checkout fixtures still say `team-inbox`
because that is what happened; only the live lists are parsed, and a markdown
line that marks the mention as retired or archived is allowed.

Regression fixtures:

```bash
python3 -m unittest discover -s scripts/agent-checks -p 'test_agent_os_project_registry.py'
```

Both run inside `agent-os-health.sh`, so `workflow-doctor.sh` covers them too.

## Active Task Freshness

```bash
scripts/agent-checks/agent_os_active_task_freshness.py
scripts/agent-checks/agent_os_active_task_freshness.py --json
scripts/agent-checks/agent_os_active_task_freshness.py --self-test
```

Issue 113. Every project keeps its agent work pointer in
`.claude/tasks/active.json`, and the only automated check used to be
`python3 -m json.tool`. A pointer naming a finished task on a long-merged
branch therefore passed every gate, and a fresh agent resumed obsolete work
with full confidence.

This check asks whether current repository evidence still supports the claim:

- an idle pointer (`activeTask: null`) claims nothing, so it is never stale at
  any age
- only canonical checkouts are judged, meaning a registered project directly
  under the workspace root whose `.git` is a directory; a linked worktree under
  `.worktrees/` or `Sifututor-worktrees/` carries a `.git` file and is history,
  never a failure
- freshness is measured against the project's own Git activity rather than the
  wall clock, so a paused project cannot drift and the answer is reproducible
- a claim is two files: `active.json` names the task and the task file carries
  the steps, so drift is measured from whichever moved last. A long task whose
  pointer never changes is not failed for it
- a merged declared branch is reported on the `merge:` evidence line and never
  fails a pointer on its own. `push`, `deploy`, and `smoke` are post-merge
  steps, and a trunk branch is always its own ancestor; shipped work is caught
  by `stale_completed` and abandoned work by drift
- file mtime is trusted only for an uncommitted or untracked pointer, because a
  clone rewrites every mtime and would hide real staleness
- missing evidence produces `unprovable`, which is reported and never repaired
  by guessing

Exit codes: 0 clean or nothing canonical to check, 1 actionable drift, 2 the
root could not be read.

Regression fixtures:

```bash
PYTHONPATH=scripts/agent-checks python3 -m unittest test_agent_os_active_task_freshness
```

`--self-test` runs inside `agent-os-health.sh` and the validation loop; the
full workspace scan runs inside `workflow-doctor.sh`. Owning playbook:
`docs/agent-playbooks/active-tasks.md`.

## Doctor

```bash
scripts/agent-checks/workflow-doctor.sh
```

Checks every active project, Codex skills, hook scripts, active task JSON, and
Claude parent `additionalDirectories`. Every active project must have the full
shared adapter baseline; a missing `AGENTS.md`, `CLAUDE.md`, active-task
pointer, or hook directory is a failure.

## Agent OS Evals

```bash
scripts/agent-checks/agent-os-eval-runner.py
```

Runs the first route and behavior eval batch against the real Codex lifecycle
classifier. Use `--verbose` to see every prompt, expected skill, observed skill,
required actions, and reason.

`agent-os-health.sh` runs this eval runner as part of the umbrella baseline.
