# Sifututor AI Workspace

This repository tracks the shared Claude/Codex operating layer for the
Sifututor workspace.

It does not own product code. Each product remains an independent nested Git
repository, for example `sifu-tutor/`, `ripple-suite/`, `lls/`, and the mobile
apps.

## What This Repo Owns

- `AGENTS.md` - universal workspace rules for Codex and other agents.
- `docs/agent-playbooks/` - shared workflow playbooks for task routing,
  verification, QA, commits, session saving, and Claude/Codex handoff.
- `scripts/agent-checks/` - portable guard scripts used before commits.

## What This Repo Does Not Own

- Product source code.
- Project-specific `AGENTS.md` and `CLAUDE.md` files.
- Project `.claude/` hooks, skills, and task state.
- Local global config such as `~/.codex/` or `~/.claude/`.
- Secrets, `.env*`, production snapshots, or `live/`.

## Daily Use

Start with:

```bash
cat AGENTS.md
```

For switching between Claude and Codex:

```bash
cat docs/agent-playbooks/switching-claude-codex.md
```

For a workspace health check:

```bash
cat docs/agent-playbooks/quick-check.md
```

Then run the guard from the project you are about to commit:

```bash
../scripts/agent-checks/pre-commit-guard.sh
```

## Repository Boundary

The umbrella repo protects the shared AI workflow. Product changes should be
committed inside their own project repositories.
