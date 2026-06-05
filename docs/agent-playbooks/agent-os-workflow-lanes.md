# Agent OS Workflow Lanes

Status: draft accepted for internal Agent OS use.

This playbook defines how the Agent OS chooses the right amount of process for
the work.

Simple version:

```text
Use lane intensity, not one fixed process for everything.
```

The agent should stay light when Hafiz is thinking, become structured when work
is being changed, and become strict when mistakes are expensive.

## Why This Exists

Too little process causes missed checks, lost context, and risky changes.

Too much process makes Hafiz feel trapped inside ceremony and causes approval
fatigue.

The Agent OS should choose the lightest lane that honestly fits the risk.

## Lane Intensity Model

| Intensity | Meaning | Example |
| --- | --- | --- |
| Light | Talk, think, explain, compare, decide | Agent OS discussion, retrospective, learning |
| Medium | Scoped docs/tooling/small safe change with checks | Agent OS docs update, Koda CLI wrapper |
| Full | Product code or user-facing behavior with verification, QA, review, commit discipline | Staff UI bugfix, new feature |
| Critical | Expensive mistake zone; read-only diagnosis first, implementation after approval | Auth, payment, invoice, commission, migration, deploy, mobile API contract |

## Lane Checklist

Each lane should define:

- entry criteria: when to use it
- exit criteria: when the lane is done
- required evidence: what proof is enough
- approval boundary: what needs Hafiz approval
- escalation trigger: when to move to a stricter lane

## Light Lane

Use for:

- discussion
- learning
- architecture thinking
- retrospective
- naming and terminology
- "what should we do?" questions
- explaining code or workflow

Entry criteria:

- Hafiz is thinking with the agent, not asking for a concrete edit.
- The prompt asks why, what, how, options, tradeoffs, or recommendation.

Agent behavior:

- explain plainly
- ask only useful questions
- recommend one next step
- update Koda only for durable corrections
- avoid verify/QA/commit ceremony

Exit criteria:

- Hafiz makes a decision
- a living draft needs updating
- work moves to Medium, Full, or Critical

Approval boundary:

- no code/product edits
- no commit/push
- no production/secret/destructive action

## Medium Lane

Use for:

- Agent OS docs and playbooks
- workflow/tooling scripts
- small non-product changes
- scoped documentation updates
- safe local checks

Entry criteria:

- Hafiz says `proceed`, `proceed next`, or approves a clear docs/workflow step.
- The work is non-critical and scoped.

Agent behavior:

- update the source-of-truth docs/scripts
- update indexes/evals when needed
- save durable decisions to Koda
- run non-destructive checks
- stop before commit/push unless exactly approved

Exit criteria:

- docs/scripts updated
- relevant checks passed or failures explained
- next recommended step stated

Required evidence:

- readback/search evidence when useful
- script syntax check for scripts
- JSON validation for JSON
- Agent OS health check for Agent OS changes
- pre-commit guard before commit

Approval boundary:

- relaxed work-packet approval applies inside the safe packet
- stage/commit/push still need exact approval

## Full Lane

Use for:

- product features
- product bugfixes
- user-facing changes
- backend/API behavior changes
- mobile behavior changes
- refactors that could affect behavior

Entry criteria:

- the task changes product code or user behavior
- the task needs implementation, not just discussion

Agent behavior:

- route task and check active state
- create/link GitHub issue when required
- check Plane for meaningful work
- use vertical-slice TDD when applicable
- verify with focused commands
- run QA/human-journey evidence when user-facing
- review risks before commit/push

Exit criteria:

- implementation complete
- required tests/checks run
- permanent E2E file named for every changed user workflow, or explicit
  accepted exception recorded
- QA/review evidence reported
- commit prepared or completed with approval

Required evidence:

- tests/type/lint/build as appropriate
- browser/mobile/API evidence when relevant
- permanent E2E coverage for every changed user workflow by default
- release communication decision for staff-facing product changes

Approval boundary:

- commit requires exact file-list approval
- push/PR/merge requires explicit current-session approval
- deploy remains separate

## Critical Lane

Use for:

- auth
- payments
- invoices
- commissions
- migrations
- deployment
- mobile API contracts
- production data/log actions
- anything with financial, security, or irreversible risk

Entry criteria:

- the task touches a critical domain, even if the requested change looks small.

Agent behavior:

- Phase A: read-only diagnosis and recommendation
- explain risk in plain language
- identify affected files/systems/tests
- wait for Hafiz approval before implementation

Exit criteria for Phase A:

- cause or likely cause identified
- recommended implementation path stated
- risk and verification plan stated
- approval request is clear

Required evidence:

- read-only code/config/log/test inspection
- no mutation unless explicitly approved

Approval boundary:

- implementation requires explicit approval after diagnosis
- commit does not replace human review when required
- deploy is always separate approval

## Escalation Rules

Move to a stricter lane when:

- discussion turns into implementation
- docs/tooling change starts affecting product behavior
- small change touches user-facing workflow
- any critical domain appears
- verification reveals unexpected behavior
- task scope expands beyond the original packet
- tool capability is unknown for a risky action

Move lighter when:

- Hafiz is only asking to understand or compare
- no files need changing
- the right output is a recommendation, not implementation

## Missing Or Future Lanes

Potential lanes to add later:

- research lane: external sources, citations, and current-date checks
- data lane: analytics/database inspection with privacy boundaries
- incident lane: production monitoring, mitigation, communication, postmortem
- staff intake lane: Planner/support triage before engineering work
- release lane: PR, deploy, smoke, monitor, close loop

Do not add these as heavy process until real use shows the need.

## Current Decision

Adopt the Lane Intensity Model:

```text
Light for thinking.
Medium for docs/tooling.
Full for product code.
Critical for expensive mistakes.
```
