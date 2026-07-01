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

## Execution Depth

Lane intensity answers:

```text
How much process does this task need?
```

Execution depth answers:

```text
How far should the agent carry this specific task before stopping?
```

Plain meaning:

```text
Do not make Hafiz remember the whole path.
Tell him the practical finish state, recommend the safest useful stop point,
then work until that point or a real gate.
```

Use these finish states in plain language:

| Finish state | Use when Hafiz wants | What the agent should do | Stop before |
| --- | --- | --- | --- |
| Answer only | Understanding, comparison, or recommendation. | Explain, compare options, recommend one next step. | Durable edits. |
| Drafted | A living plan, PRD, UX shape, or workflow idea. | Create/update the smallest useful planning artifact. | Implementation. |
| Changed locally | A safe docs/tooling/code change without saving history yet. | Edit scoped files and run the relevant local checks. | Commit unless approved. |
| Local proof | Confidence that the change works locally. | Run focused tests, lint/build, browser/API/mobile checks, or docs health checks. | Commit/push/PR. |
| Committed | A clean local history point. | Guard, stage exact files, commit the approved package. | Push unless approved. |
| PR ready | GitHub review state is prepared. | Push branch, open/update PR, write body, monitor CI, and fix in-scope CI only if approved. | Merge unless approved. |
| Merged | Shared source of truth includes the change. | Review/merge only inside an approved boundary. | Deploy unless approved. |
| Deployed | Staging or production received the approved commit. | Run release preflight and deploy to the named environment only when approved. | Live claims without smoke. |
| Live checked | The real environment passed the agreed smoke or journey check. | Run safe smoke/API/browser/monitoring evidence for the deployed state. | New fixes, rollback, or broader risk acceptance unless approved. |
| Monitored | Post-release health has been watched. | Check read-only logs/monitoring for the agreed window or scope. | Final acceptance when business judgment is still needed. |
| Accepted or closed | Hafiz/staff/business owner accepts the result. | State what is proven, what is accepted, and what is closed. | Calling unaccepted risk accepted. |

These are not rigid phases.
A tiny docs typo may go from `Changed locally` to `Committed`.
A production release may need `PR ready -> merged -> deployed -> live checked
-> monitored`.
A discussion may stop at `Answer only`.

## Depth Selection

At task start, choose the depth from Hafiz's wording, current state, and risk.

| Hafiz says or implies | Recommended depth | Practical response |
| --- | --- | --- |
| `why`, `what is this`, `can we discuss` | Answer only | Explain and recommend. Do not edit unless Hafiz says to document it. |
| `let's design`, `brainstorm`, `plan properly` | Drafted | Use chat, Quick Brief, Product Shape, Build-Ready Pack, or Session Map. |
| `proceed` after a docs/workflow recommendation | Changed locally + local proof | Update the scoped docs and checks. Stop before commit/push unless included. |
| `fix this` | Local proof, then recommend commit/PR path | Diagnose, change, verify, QA/review as needed, then name the next gate. |
| `proceed until commit` | Committed | Work through checks/review/commit and stop before push. |
| `proceed until PR ready` | PR ready | Commit, push, open PR, monitor CI, then stop before merge. |
| `proceed until merged` | Merged | Reach merged state if checks and approval boundary allow, then stop before deploy. |
| `proceed until production` | Deployed + live checked, and monitoring if named | Explain the release path, require deploy approval, deploy, smoke, and report monitoring boundary. |
| `proceed until done` | Translate first | Say what done means for this task, how far the agent can go now, and what still needs approval. |

When unsure, recommend a depth instead of asking Hafiz to pick from a menu.

Good:

```text
For this bug, I recommend stopping at PR ready first: diagnose, fix, prove the
browser journey, commit, push, open PR, and monitor CI. Production deploy stays
separate.
```

Bad:

```text
What do you want me to do next?
```

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
- execution depth: the practical finish state for this task
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
- check Mission Ledger for bigger goals or related follow-ups when relevant
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
