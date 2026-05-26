---
name: quick-check
description: Use when Hafiz asks Codex to check whether the Sifututor Claude/Codex workflow system is healthy, wired correctly, or ready before starting work. Must follow docs/agent-playbooks/quick-check.md.
---

# Quick Check

Use this skill for a fast workflow health check before starting real work.

## Core Rule

Read and follow:

```text
docs/agent-playbooks/quick-check.md
```

Run the workflow doctor from the umbrella root:

```bash
scripts/agent-checks/workflow-doctor.sh
```

## Human-Facing Alias

```text
Claude: /quick-check or shared doctor script
Codex: $quick-check
```
