# Planning Artifacts

Use this playbook when a task needs thinking before implementation, but Hafiz
should not be forced to read code or a rigid PRD to understand what will happen.

Plain meaning:

```text
Before building something complex, create the smallest useful thinking board.
It should help Hafiz understand the goal, options, recommendation, risk, proof,
and next decision before the agent starts changing code.
```

## Why This Exists

The Agent OS already has Session Maps, Product Design artifacts, Koda, GitHub,
and workflow playbooks. The missing rule is how to choose the right planning
artifact before implementation.

This playbook prevents two bad extremes:

- building too fast from a vague prompt
- creating heavy documents for small safe work

## Source Of Truth

Markdown is the source of truth. HTML is a generated or review-only view.

Plain version:

```text
Update one readable Markdown source.
Generate a visual HTML view only when Hafiz needs to scan or review it.
Do not maintain two separate truths.
```

If an HTML view is manually annotated, copy the accepted decision back into the
Markdown source before treating it as final.

## Artifact Choices

Use the lightest artifact that makes the work understandable and safe.

| Artifact | Use when | What Hafiz should understand |
| --- | --- | --- |
| Chat only | Tiny question, learning, or no implementation yet. | The answer or recommendation. |
| Quick Brief | Small safe edit, typo, narrow bug, simple docs/tooling change, or obvious behavior. | What is wrong, what will change, what will not change, and how it will be checked. |
| Product Shape | User workflow, staff process, unclear expected behavior, multiple options, or multi-file change. | Current behavior, options, recommendation, tradeoff, evidence plan, and decision needed. |
| Build-Ready Pack | Major workflow, critical lane, multi-role/module work, backend/frontend contract, mobile/API contract, or handoff to another builder. | Full workflow, rules, contracts, edge cases, risks, build slices, proof plan, and stop point. |
| Session Map | Long-running session, side paths, many decisions, parallel agents, or unclear return path. | Where we are, why we are here, what changed, what is waiting, and what happens next. |
| Markdown + HTML view | Complex plan or long session where visual scanning matters. | Same truth as Markdown, easier to inspect as a board or dashboard. |

Do not use numeric labels such as `level 1`, `level 2`, or `level 3` when
talking to Hafiz. Say the practical artifact name and explain why.

## Required Content

Every planning artifact should answer only what is relevant for the task.

### Quick Brief

- What is wrong or requested?
- What will change?
- What will not be touched?
- How will the agent check it?
- Where will the agent stop?

### Product Shape

- What problem are we solving?
- What is the current behavior or current workflow?
- Who is affected?
- What options exist?
- What does the agent recommend, and why?
- What will change?
- What will not change?
- What are the risks or tradeoffs?
- How will it be proven?
- What decision does Hafiz need to make?

### Build-Ready Pack

- Goal and practical finish state.
- Users, roles, permissions, and affected workflows.
- Current workflow and target workflow.
- Business rules and edge cases.
- Entry points, state transitions, data/API/backend contracts, and
  compatibility requirements.
- Options, recommendation, and rejected alternatives.
- Out-of-scope list.
- Implementation slices.
- Evidence plan: tests, E2E, smoke, screenshots, API checks, monitoring, or
  manual business acceptance.
- Stop conditions and approval gates.
- Final build prompt or handoff instructions if another agent or developer will
  implement.

## Visual Review

Generate or open a visual view when Hafiz needs to scan the artifact quickly.
This applies especially to Session Maps, module redesigns, big workflow
decisions, release boards, and multi-session work.

Good visual view:

- starts with the goal and current state
- shows the recommended next action near the top
- separates decisions, risks, evidence, and waiting items
- uses cards, columns, flow, or tables so it is not a wall of text
- avoids decorative layouts that hide the actual work

When the visual artifact is local and safe to inspect, open it automatically:

```bash
open <path>
```

Do not auto-open files that contain secrets, credentials, raw tokens, `.env*`
content, or production-sensitive private payloads.

## Implementation Boundary

Before coding starts, the agent must be able to explain the intended
implementation in plain English:

```text
What will change, what will not change, why this approach is recommended, how
it will be proven, and where the agent will stop.
```

If the agent cannot explain that clearly, keep planning. Do not start coding
just because a document exists.

## Where To Save

| Information | Save to |
| --- | --- |
| Current session story and return path | Session Map |
| Confirmed product or UX artifact | Project feature docs |
| Durable workflow lesson or correction | Koda |
| Future goal or parked idea | Mission Ledger |
| Execution-ready coding work | GitHub issue or project active task |
| Exact changed files | Git commit |

Plain version:

```text
Planning artifacts explain the work.
They do not replace Koda, GitHub, Session Map, Mission Ledger, tests, or commits.
```

## Common Failure Modes

Avoid these:

- turning every small task into a heavy artifact
- building from vague agreement without naming the finish state
- making HTML the only truth
- copying the same decision into many docs without naming the source
- leaving Hafiz with options but no recommendation
- asking Hafiz to approve code he has not understood in plain English
- saying "done" when the artifact is only drafted and not approved, checked, or
  connected to implementation

## Recommended Close-Out

End a planning step with:

```text
Status:
Meaning:
Recommended next:
Decision needed:
```

Keep it natural. The goal is that Hafiz knows what just became clearer and what
the agent recommends next.
