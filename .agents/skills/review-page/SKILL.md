---
name: review-page
description: Use when a change staff will see on screen is about to be coded (plan mode), or shippable work is ready for Hafiz's confirmation before deploy (ship mode), in any Sifututor project. Takes `plan` or `ship` and a project. Must follow docs/agent-playbooks/review-page.md.
---

# Review Page

Use this skill to make the one page Hafiz reads to understand a change.

## Arguments

```text
plan <project>   before coding: today's real screen, the proposed screen from
                 real components with fictional data, decisions, risks,
                 done means, evidence plan
ship <project>   before deploy: real screenshots of every UI
                 change, test and Codex results, release state, approvals
```

If the mode is missing, infer it: no code yet means `plan`, built work means
`ship`. If the project is missing, infer it from the conversation.

## Core Rule

Read and follow:

```text
docs/agent-playbooks/review-page.md
```

It owns when each page is due, the page structure, where proposed screens come
from, privacy, and the non-blocking rule: without Hafiz's go, send the link and
wait; with his go, open the page for him and keep working.

## Human-Facing Alias

```text
Claude: /review-page plan|ship <project>
Codex: $review-page plan|ship <project>
```
