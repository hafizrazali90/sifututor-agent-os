---
name: verify
description: Use when Hafiz asks Codex to verify work, run Gate 2A, prove an implementation works, or prepare evidence before QA or commit in the Sifututor workspace. For SIMS UI/UX proof use sims-ui-audit before claiming review readiness. Must follow docs/agent-playbooks/verify.md.
---

# Verify

Use this skill for Gate 2A verification, before QA, and before any commit that
depends on implementation evidence.

## Core Rule

Read and follow:

```text
docs/agent-playbooks/verify.md
```

That playbook is the source of truth. Use stricter project `AGENTS.md`,
`CLAUDE.md`, or `CODEX-WORKFLOW.md` commands when they apply.

## Quick Workflow

1. Identify the project being verified.
2. Read the project command matrix in the verify playbook.
3. Run verification from the project directory, not the umbrella root.
4. Separate baseline failures from task-caused failures.
5. For `sifu-tutor` browser UI/UX changes, name whether `$sims-ui-audit` still
   needs to run before Hafiz review or commit.
6. Report using the playbook's `VERIFY - PASS | FAIL | PARTIAL` shape.
7. Treat failing verification as a commit blocker unless the user explicitly
   changes the scope.

## Human-Facing Alias

When explaining this to Hafiz, describe it as:

```text
Claude: /verify
Codex: $verify
```
