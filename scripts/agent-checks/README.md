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

## Doctor

```bash
scripts/agent-checks/workflow-doctor.sh
```

Checks every active project, Codex skills, hook scripts, active task JSON, and
Claude parent `additionalDirectories`. Projects listed in `ADAPTER_PENDING`
are active but have not finished their Claude/Codex adapter rollout, so a
missing adapter file there is reported as a warning instead of a failure.

## Agent OS Evals

```bash
scripts/agent-checks/agent-os-eval-runner.py
```

Runs the first route and behavior eval batch against the real Codex lifecycle
classifier. Use `--verbose` to see every prompt, expected skill, observed skill,
required actions, and reason.

`agent-os-health.sh` runs this eval runner as part of the umbrella baseline.
