# Decisions

Technical and workflow decisions that are hard to undo. One short file per
decision. Business-rule decisions stay in
[docs/business-rules/decision-reasons.md](../business-rules/decision-reasons.md).
Ideas we decided against go in [.out-of-scope/](../../.out-of-scope/README.md).

## When a decision gets a file

All three must be true:

1. **Hard to reverse.** Undoing it later costs real time, money or trust.
2. **Surprising without context.** A new person would ask "why on earth did
   they do it this way?".
3. **A real trade-off.** There was a sensible alternative, and we gave
   something up.

If any is false, write it in the owning playbook or the issue, not here.

## Format

File name `NNNN-short-title.md`, numbered in order. Headings, in this order:

- `# NNNN: Title`
- `Status`, `Decided` (DD/MM/YYYY, MYT, and by whom)
- `## Context`: what forced the choice, in a few sentences.
- `## Decision`: what we do, in plain words.
- `## Why`: the reasons, with evidence.
- `## What we gave up`: the cost of this choice.
- `## Revisit if`: what would make us reopen it.

Do not edit an accepted decision to change its meaning. Write a new file that
supersedes it and set the old status to `Superseded by NNNN`.

## Index

| No. | Decision | Status |
| --- | --- | --- |
| 0001 | [Run Agent OS on the home PC inside WSL2](0001-run-agent-os-on-wsl2.md) | Accepted |
| 0002 | [Give the PC full GitHub access and control it with the job brief](0002-pc-github-access-and-job-brief.md) | Accepted |
| 0003 | [Keep one Claude profile per account on the PC](0003-one-claude-profile-per-account.md) | Accepted |
| 0004 | [Start every PC job through Task Scheduler](0004-start-pc-jobs-through-task-scheduler.md) | Accepted |
