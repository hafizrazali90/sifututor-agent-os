# Sifututor Agent OS

This repository tracks the **Sifututor Agent OS**: the shared operating layer
for Hafiz, Claude, Codex, Koda, GitHub, Plane, Planner, and project-specific
tools to plan, build, verify, remember, and ship work without losing context.

It does not own product code. Each product remains an independent nested Git
repository, for example `sifu-tutor/`, `ripple-suite/`, `lls/`, and the mobile
apps.

## Naming

Use **Sifututor Agent OS** for the whole collaboration system.

- **Agent OS** - the shared operating layer across humans, agents, memory,
  task state, quality gates, and project tools.
- **Workflow** - one route inside the Agent OS, such as bugfix, feature,
  product design, QA, commit, or save-session.
- **Playbook** - the written steps for a workflow.
- **Router** - the part that decides which workflow applies.
- **Guardrails** - rules and scripts that prevent expensive mistakes.
- **Working Agreement** - how Hafiz, Codex, Claude, and reviewers collaborate.

See `docs/agent-playbooks/agent-os.md` for the short operating model.

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

The umbrella repo protects the shared Agent OS. Product changes should be
committed inside their own project repositories.
