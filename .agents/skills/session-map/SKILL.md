---
name: session-map
description: Use when Hafiz asks Codex to create, update, inspect, close, or generate a continuation prompt from a Sifututor Session Map, or when a session has multiple goals, side paths, parallel agent work, or unclear return path. Must follow docs/agent-playbooks/session-map.md.
---

# Session Map

Use this skill when the current Sifututor session needs a live, human-readable
map of the main goal, current focus, side paths, decisions, evidence, and next
action.

## Core Rule

Read and follow:

```text
docs/agent-playbooks/session-map.md
```

That playbook is the source of truth. Do not duplicate a second Session Map
format inside this skill.

## Quick Workflow

1. Identify whether a Session Map already exists for the current session.
2. If no map exists and the session is non-trivial, create one from
   `docs/agent-playbooks/templates/session-map.md`.
3. Use one map for one meaningful session. Reuse the same map for the same
   main goal; create a new map only for a different mission, project, branch,
   release path, owner, or confusing unrelated scope.
4. Keep the `Human Snapshot` current before changing deeper technical sections.
5. Add or update side paths when the conversation branches.
6. Record decisions, evidence, linked commits, Koda memories, GitHub issues,
   PRs, Mission Ledger items, and continuation prompts when they matter.
7. Keep active session maps local by default under `.agent-os/session-maps/`.
8. Promote only durable examples, templates, or playbook changes into committed
   docs.

## Human-Facing Alias

When explaining this to Hafiz, describe it as:

```text
Claude: /session-map or natural-language "update the session map"
Codex: $session-map
```
