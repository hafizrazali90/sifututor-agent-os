---
name: task-router
description: Use when Hafiz asks Codex to start, route, classify, resume, or create a Sifututor task. This is the Codex equivalent of Claude task-router skills and must follow docs/agent-playbooks/task-router.md.
---

# Task Router

Use this skill before meaningful implementation work, when the user asks what
to do next, or when a task needs to be classified into a workflow route.

## Core Rule

Read and follow:

```text
docs/agent-playbooks/task-router.md
```

That playbook is the source of truth. Do not duplicate a separate routing
system inside this skill.

## Quick Workflow

1. Identify the active project from cwd and the user prompt.
2. Read the nearest `AGENTS.md`; read project `CLAUDE.md` for deeper context.
3. Search Koda for relevant memories when the task is non-trivial.
4. Read `.claude/tasks/active.json` when present.
5. If a task is active, read the referenced task file and report the route plus
   next unblocked step.
6. For critical lanes, do read-only Phase A first and wait for approval before
   implementation.

## Human-Facing Alias

When explaining this to Hafiz, describe it as:

```text
Claude: /task-router or project task-router skill
Codex: $task-router
```
