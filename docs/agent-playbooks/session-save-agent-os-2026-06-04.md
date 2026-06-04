# Agent OS Session Save - 2026-06-04

## Scope

Workspace: Sifututor umbrella workspace.

This session built and stabilized the internal Sifututor Agent OS baseline, then
cleaned and pushed the parent app workflow state.

## Commits Pushed

Umbrella repo:

- `c66acdb` - `docs(workflow): add internal Agent OS foundation`
- `5a2ae95` - `docs(workflow): rename umbrella repo to Agent OS`
- `35f33a0` - `docs(workflow): include Agent OS health in quick check`

Parent app repo:

- `689066a` - `docs(qa): add parent app mobile bug ledger`
- `70b927d` - `docs(workflow): add parent app Agent OS baseline`
- `3fbcbe5` - `docs(workflow): align parent issue intake rule`
- `b338e1a` - `chore(release): prepare parent app 1.20.0`

## Current State

- Umbrella repo is clean and synced with `origin/main`.
- `sifututor_parent` is clean and synced with `origin/main`.
- `scripts/agent-checks/workflow-doctor.sh` passes.
- `scripts/agent-checks/agent-os-health.sh` passes through the doctor.
- `sifututor_parent` now has `.claude/settings.json`, `.claude/hooks/`,
  and `.claude/tasks/active.json`.

## Durable Lessons

- For product repos that only need standard workflow guardrails, prefer a small
  local `.claude/settings.json` pointing at shared umbrella hooks plus
  `active.json` and `SCHEMA.md`.
- Avoid duplicating per-project hook scripts unless the project needs behavior
  that cannot be shared safely.
- Discussion, retrospective, research, and workflow-design prompts should not be
  routed by keyword alone into implementation or commit playbooks.
- `sifututor_parent` version source of truth is `version.json`; use
  `npm run check-version` to verify Android, iOS project, and `package.json`.
- `scripts/sync-version.js` does not update `package-lock.json`; if the package
  version changes, refresh the lockfile metadata so it matches.

## Koda Status

Direct Koda health check passed through:

```bash
python3 scripts/agent-checks/codex-lifecycle-hook.py --check-koda
```

However, chat-level Koda MCP `memory_search` and `memory_store` calls timed out
during save-session. This file is the fallback session save. When Koda MCP calls
are reliable again, store the durable lessons above as concise memories tagged
with `sifututor`, `sifututor_parent`, `agent-os`, and `codex-parity`.

## Recommended Next

Make Agent OS installable for staff:

1. Add an install/check script for applying the baseline to a project.
2. Document the required local prerequisites.
3. Add a dry-run mode that reports missing `.claude` baseline files, Codex
   skills, Koda config, and guard scripts without changing the repo.
