---
name: handoff
description: Use when Hafiz asks Codex to hand off work to Claude, another Codex session, or a human in the Sifututor workspace. Must follow docs/agent-playbooks/handoff.md.
---

# Handoff

Use this skill when work needs to continue in another session or with another
agent.

## Core Rule

Read and follow:

```text
docs/agent-playbooks/handoff.md
```

Use `$save-session` instead when the user wants the full end-of-session Koda
and guard protocol.

Before returning the handoff, follow the shared playbook's worktree rule:
preview and safely close a finished dedicated leased worktree, or park and
report unfinished work with its exact resume action.

## Human-Facing Alias

```text
Claude: /handoff
Codex: $handoff
```
