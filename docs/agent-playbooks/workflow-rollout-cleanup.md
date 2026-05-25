# `.workflow-rollout/` Cleanup Note

Last audited: 2026-05-26
Cleanup completed: 2026-05-26

`.workflow-rollout/` is a stale rollout staging area in the umbrella workspace.
It is not part of the active Claude/Codex parity system.

## Finding Before Cleanup

- Size: about 240 MB.
- Contains clones or snapshots for:
  - `creative-hub`
  - `lls`
  - `lls-frontend`
  - `lls-mobile`
  - `ripple-suite`
  - `sifu-tutor`
  - `sifututor_parent`
  - `sifututor_tutor`
  - `team-inbox`
- Contains environment example files and production-named env files inside the
  snapshots, including:
  - `.workflow-rollout/lls-frontend/.env.production`
  - `.workflow-rollout/team-inbox/frontend/.env.production`

## Result

Hafiz approved cleanup and `.workflow-rollout/` was removed. The active parity
work now lives in:

- root `AGENTS.md`
- project `AGENTS.md`
- project `.claude/tasks/active.json`
- project `.claude/hooks/`
- project `.claude/settings.json`
- `docs/agent-playbooks/`

After deletion, the shared guard passed in all ten projects.
