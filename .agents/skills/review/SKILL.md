---
name: review
description: Use when Hafiz asks Codex for code review, pre-commit review, risk review, or adversarial quality checks in the Sifututor workspace. For SIMS UI/UX visual review use sims-ui-audit alongside this. Must follow docs/agent-playbooks/review.md.
---

# Review

Use this skill for review-first work. Lead with findings and keep summaries
secondary.

## Core Rule

Read and follow:

```text
docs/agent-playbooks/review.md
```

For `sifu-tutor` browser UI/UX changes, also read and apply:

```text
docs/agent-playbooks/sims-ui-audit.md
```

If no issue is found, say that clearly and still mention any remaining test gap
or residual risk.

## Human-Facing Alias

```text
Claude: /review
Codex: $review
```
