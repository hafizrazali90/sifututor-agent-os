---
name: snapshot
description: Use when Hafiz asks Codex to snapshot current context before compaction, interruption, switching agents, or a long pause in Sifututor work. Must follow docs/agent-playbooks/snapshot.md.
---

# Snapshot

Use this skill to freeze the current working context without marking the task
complete.

## Core Rule

Read and follow:

```text
docs/agent-playbooks/snapshot.md
```

Use `$save-session` when the user wants the complete session closeout.

## Human-Facing Alias

```text
Claude: /snapshot
Codex: $snapshot
```
