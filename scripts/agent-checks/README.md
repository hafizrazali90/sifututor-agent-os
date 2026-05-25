# Agent Checks

Shared guardrail scripts for Claude, Codex, and any other coding agent.

These scripts exist because Claude hooks and Codex hooks do not currently have
identical, verified behavior on this machine. Run them explicitly before commit
or any risky change.

As of `codex-cli 0.130.0`, MCP parity is verified, but `PreToolUse` hook tests
in `codex exec` did not fire with either inline TOML or `hooks.json` test
configuration, including after a VS Code restart on 2026-05-26. Treat native
Codex hooks as unverified until tested in the VS Code extension or interactive
CLI.

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
