---
name: sifututor-workflow
description: Use when Codex needs the packaged Sifututor workflow overview, including how to find repo-local skills, hooks, guards, and shared playbooks.
---

# Sifututor Workflow Plugin

This plugin is a portable package entry point. In the live workspace, prefer the
repo-local skills under:

```text
.agents/skills/
```

Use the shared playbook index:

```text
docs/agent-playbooks/README.md
```

Core commands:

```text
$quick-check
$task-router
$diagnose
$verify
$qa
$review
$commit
$save-session
$handoff
$snapshot
```

Run the doctor:

```bash
scripts/agent-checks/workflow-doctor.sh
```
