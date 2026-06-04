# Plane Mission Board Playbook

Use this playbook whenever an agent creates, updates, reviews, or relies on a
Plane work item for Sifututor work.

Plane is Hafiz's human mission board. It should answer, in plain language:

- where we are now
- what we are trying to finish
- what sub-goals are done or still open
- who owns the next move
- what is blocked or waiting for approval
- where the evidence lives

Plane is not the evidence store and not a replacement for repo docs, Koda, or
GitHub issues.

Use [agent-os-state-model.md](agent-os-state-model.md) for the broader source
of truth split between Plane, GitHub, Planner, active task files, git, QA
evidence, and Koda.

## Source Split

| Source | Role |
| --- | --- |
| Plane | Human mission board: goal, status, next action, owner, blocker, evidence links |
| Koda | Durable memory: rules, corrections, and non-obvious lessons |
| Repo docs | Evidence, runbooks, QA reports, release notes, and technical records |
| GitHub issues | Developer execution tickets when code work must be assigned to devs |
| `.claude/tasks/active.json` | Current agent execution pointer for active task workflow |

For small Claude/Codex-only work, Plane alone is enough. For developer work,
create or link a GitHub issue from the Plane card so Plane remains the control
board and GitHub carries the implementation ticket.

## Card Standard

Every useful Plane card must explain:

1. What this is.
2. Why it matters.
3. Current status.
4. Next action.
5. Owner of the next action.
6. Evidence or links.

Use this structure in the card description when creating or refreshing cards:

```text
Goal
What outcome are we trying to finish?

Why This Matters
Why this task exists, in plain business/product language.

Session Progress
- [x] Step already completed
- [ ] Current step
- [ ] Later step

Current Step
What is happening right now?

Next Action
The next concrete thing to do.

Owner
Hafiz / Codex / Claude / dev / QA human / FIUU / device test

Waiting On
Decision, access, test result, approval, deploy window, etc.
If nothing is blocking, write "Nothing".

Evidence
Links to docs, commits, reports, screenshots, QA sheets, or monitoring results.

Notes
Important context that should not be lost. Keep it short.
```

When using Plane's `description_html`, keep the same sections but write compact
HTML. Do not leave cards with empty descriptions.

## State Rules

Use states consistently so Hafiz can read the board without decoding agent
jargon.

| State | Meaning |
| --- | --- |
| Backlog | Captured or future work. Not selected yet. |
| Todo | Selected next, but nobody has started. |
| In Progress | Actively being worked on now. Keep this small, ideally 1-3 cards. |
| In Review | Work is done by an agent/dev and waiting for Hafiz, QA, device/FIUU testing, production monitoring, or final approval. |
| Blocked | Cannot continue until a named blocker is resolved. The blocker must be written in the card. |
| Done | Practical outcome is complete and evidence exists. |
| Cancelled | Intentionally dropped, merged into another card, or no longer needed. The reason must be written in the card. |

Do not leave work in Backlog when it is really waiting for Hafiz or QA. Use In
Review for waiting states.

## Session Tracking

For non-trivial active work, the Plane card must show goal/sub-goal progress.
At any time, Hafiz should be able to open Plane and understand the current
session without reading the chat transcript.

Use one active card with a Session Progress checklist for normal focused work.
Use a parent card plus child/subtask cards for releases, multi-day work, or
multi-person work.

Examples:

- Normal session: one card with checklist.
- Production release: parent release card plus child cards for QA, deploy,
  smoke, monitoring, and follow-ups.
- Developer app bug: Plane card tracks context and status, GitHub issue carries
  technical implementation details.

## Auto-Update Vs Ask First

Agents may update Plane automatically when they are only recording reality.
Agents must ask Hafiz before changing direction, scope, priority, ownership, or
production state.

Auto-update is allowed for:

- marking a completed step after it really passed
- adding test, QA, commit, deploy, or monitoring evidence
- adding a commit SHA to the relevant card
- moving In Progress to In Review when waiting for Hafiz/QA/device/FIUU
- moving In Review to Done after the agreed approval or test result is complete
- saving factual session progress and the obvious next action

Ask Hafiz first before:

- creating a new major card or release card
- cancelling a task
- changing priority
- changing owner
- splitting or merging tasks
- deciding work is no longer needed
- adding high-risk work in auth, payments, invoices, commissions, migrations,
  mobile API contracts, or production deployment
- marking a high-risk release/deploy card Done
- pushing, merging, deploying, opening a PR, or any other outbound action

Short rule:

```text
Autoupdate Plane for factual progress.
Ask Hafiz before changing plan, priority, owner, scope, or production state.
```

## Workflow Hooks

At task start:

1. Check whether a relevant Plane item exists.
2. Check `.claude/tasks/active.json` when present.
3. Confirm the Plane card status, next action, and owner match the real work.
4. If there is no card for meaningful work, ask Hafiz before creating a major
   new one.

During work:

- Update Plane only at meaningful state changes.
- Keep the Session Progress checklist current.
- Record blockers in plain language.

When committing:

- Add the commit SHA and short summary to the Plane card.

When deploying:

- The release card should show release scope, backup evidence, deploy commit,
  smoke test result, monitoring result, rollback anchor, and close-out status.

When saving session:

- Update Plane with what changed, current step, next action, owner, blockers,
  and evidence links.

## Card Quality

When touching Plane through Claude's Plane tooling, also follow the Plane card
quality rules in `~/.claude/skills/plane-update/SKILL.md`, including required
title, state, priority, dates, assignee, and compact HTML description.
