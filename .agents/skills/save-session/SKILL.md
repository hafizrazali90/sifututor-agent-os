---
name: save-session
description: Use when Hafiz asks to save the session, finish a handoff, compact context, or preserve what Codex learned in the Sifututor workspace. This is the Codex equivalent of Claude's /save-session habit and must follow docs/agent-playbooks/save-session.md.
---

# Save Session

Use this skill at the end of meaningful Sifututor work, when the user asks
"save session", or when preparing a handoff between Codex, Claude, and a human.

## Core Rule

Read and follow:

```text
docs/agent-playbooks/save-session.md
```

That playbook is the source of truth. Do not duplicate or invent a different
save flow inside this skill.

## Quick Workflow

1. Identify the project or workspace being saved.
2. Read the save-session playbook.
3. Choose Quick Save, Normal Save, or Critical Save.
4. Run the required status and guard checks for that level.
5. Search Koda before storing durable lessons, then store or update the memory.
6. Resolve the current dedicated leased worktree through the shared close-out
   rule: preview then safely close finished work, or park unfinished work.
7. Report the active task state, guards, commits/pushes, key learnings,
   remaining work, and blockers using the playbook's final report shape.

## Important Constraints

- Never store secrets, raw tokens, credentials, `.env` values, customer private
  data, or production payloads in Koda.
- Koda `source` must be only `user-stated`, `auto-captured`, or `correction`.
- Every stored memory must include at least one project tag.
- If Koda fails, say so plainly and use the fallback section in the playbook.
- For critical work involving auth, payment, invoice, commission, migration,
  deployment, financial behavior, or mobile API contracts, use Critical Save.

## Human-Facing Alias

When explaining this to Hafiz, describe it as:

```text
Claude: /save-session
Codex: $save-session
```
