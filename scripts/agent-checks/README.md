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
- active task state summary

These checks are intentionally conservative. A failing check means stop and ask
the user or run the project-specific Claude workflow step.

## Doctor

```bash
scripts/agent-checks/workflow-doctor.sh
```

Checks all ten projects, Codex skills, hook scripts, active task JSON, and
Claude parent `additionalDirectories`.
