---
name: workflow-improvement
description: Use when Hafiz asks Codex to improve the Sifututor Agent OS workflow, fix agent behavior, make future agents handle something better, resolve Claude/Codex workflow drift, create or update workflow skills, or clean up Agent OS docs/skills/hooks/evals/Koda consistency. Must follow docs/agent-playbooks/agent-os-improvement-loop.md.
---

# Workflow Improvement

Use this skill when Hafiz wants the Agent OS itself to improve.

This is not for ordinary product bugs. It is for improving how Codex, Claude,
Koda, skills, hooks, playbooks, evals, and workflow docs behave together.

## Core Rule

Read and follow:

```text
docs/agent-playbooks/agent-os-improvement-loop.md
```

That playbook is the source of truth. Do not patch one file and call the Agent
OS fixed if the behavior depends on docs, skills, hooks, evals, Koda, or the
Session Map.

## Quick Workflow

1. Restate the workflow behavior Hafiz wants changed.
2. Classify the mistake type before editing.
3. Identify the source of truth that owns the behavior.
4. Check the relevant connected files, not the whole workspace by default.
5. Explain the proposed change in plain English before durable edits.
6. Update the smallest coherent set of docs, skills, evals, Koda, or Session
   Map entries.
7. Run the checks named by the improvement-loop playbook.
8. Close out with what future agents should do differently.

## Human-Facing Alias

When explaining this to Hafiz, describe it as:

```text
Claude: /workflow-improvement later, or natural-language "improve the workflow"
Codex: $workflow-improvement
```
