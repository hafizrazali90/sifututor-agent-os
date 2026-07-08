---
name: qa
description: Use when Hafiz asks Codex for QA, regression evidence, smoke testing, visual QA, or route-level quality checks in the Sifututor workspace. For SIMS UI/UX visual audit use sims-ui-audit alongside this. Must follow docs/agent-playbooks/qa.md.
---

# QA

Use this skill when implementation verification is not enough and the task needs
regression, smoke, manual, browser, or route-level QA evidence.

## Core Rule

Read and follow:

```text
docs/agent-playbooks/qa.md
```

That playbook is the source of truth. Use stricter project-specific QA rules
when `AGENTS.md`, `CLAUDE.md`, or `CODEX-WORKFLOW.md` requires them.

## Quick Workflow

1. Identify the task route: docs, small-change, bugfix, hotfix, feature, or
   refactor.
2. Pick the QA tier from the playbook.
3. Run the strongest feasible automated checks.
4. Add manual or browser evidence when the changed surface requires it.
5. For `sifu-tutor` browser UI/UX QA, also run `$sims-ui-audit` or follow
   `docs/agent-playbooks/sims-ui-audit.md` inside the QA report.
6. For bugfix/hotfix work, explicitly state the old failure mode and how the
   regression is now covered.
7. Report using the playbook's `QA - PASS | FAIL | PARTIAL` shape.

## Human-Facing Alias

When explaining this to Hafiz, describe it as:

```text
Claude: /qa
Codex: $qa
```
