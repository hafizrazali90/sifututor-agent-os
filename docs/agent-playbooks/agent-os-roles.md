# Agent OS Roles And Responsibilities

Status: accepted for internal Sifututor Agent OS use after Hafiz discussion.

This document defines who owns what inside the Sifututor Agent OS.

Plain meaning: the agent should do as much useful technical work as it safely
can, but Hafiz still owns product direction, business judgment, risk acceptance,
and permission for actions that change external state.

## Core Split

```text
Hafiz decides direction and accepts risk.
The agent executes, verifies, explains, and remembers.
Staff report reality and validate real-world fit.
The system records state, evidence, and guardrails.
```

Non-technical version:

```text
Hafiz is the owner.
The agent is the technical operator and tester.
Staff are users/reporters.
The Agent OS is the shared checklist and memory.
```

## Confirmed Role Decisions

These were reviewed with Hafiz one by one.

| Area | Decision |
| --- | --- |
| A. Hafiz role | Hafiz is the hybrid owner/operator: product owner, business-rule owner, priority setter, risk acceptor, and approval owner for external-state or critical actions. |
| B. Agent role | The agent is the technical operator, tester, and workflow secretary. It carries the technical burden before asking Hafiz. |
| C. Staff role | Staff are reporters, context providers, and QA feedback sources by default. They are not engineering source of truth or full builders in Phase 1. |
| D. Tools/system role | Tools are record systems and guardrails, not bosses. No single tool is truth for everything. |
| E. Approval boundaries | Safe technical work can proceed inside the agreed task boundary. External state, money, data, production, access, risk, direction, critical lanes, and destructive actions need Hafiz approval. |

## Role Map

| Role | Owns | Does not own |
| --- | --- | --- |
| Hafiz | Product direction, priorities, final risk acceptance, business rules, UX/product judgment, approval for push/PR/merge/deploy/critical/destructive actions. | Repeating technical checks the agent can safely run, reading code to understand every implementation detail, reminding the agent what next after every step. |
| Agent | Technical diagnosis, implementation, tests, QA evidence, risk review, docs updates, Koda lessons, clear close-out, and recommended next action. | Final business judgment, unsafe production mutation without approval, secret access, broad scope expansion, hiding uncertainty, or treating staff reports as proven root cause. |
| Staff | Reporting symptoms, giving reproduction context, checking real-world workflow fit, attaching screenshots or examples, confirming whether a fix solves their operational issue. | Direct production/deploy/code permissions by default, closing engineering work without evidence, approving critical technical risk. |
| Human developer/reviewer | Code implementation or review when assigned, following Agent OS playbooks, producing evidence, respecting approval gates. | Bypassing guardrails, changing scope silently, relying on private chat context instead of saved state. |
| GitHub | Engineering execution record: issue, PR, review, CI, linked commits, and code history. | Product memory, staff intake truth, production/live status by itself. |
| Planner | Staff-reported intake and operational context for SIMS/mobile issues. | Engineering source of truth, root cause proof, approval to code, approval to close engineering work. |
| Mission Ledger | Bigger goals, parked decisions, adjacent ideas, future follow-ups not ready for GitHub. | Current implementation truth, live/deployed status, evidence replacement. |
| Koda | Durable lessons, corrections, preferences, non-obvious rules, and repeated mistakes. | Current task status, secrets, raw credentials, noisy progress, proof that old context is still true. |
| Guard scripts/evals | Catch known workflow mistakes before commit/push or future drift. | Human judgment, complete product QA, or permission to cross approval gates. |

## What Hafiz Should Not Need To Do

Hafiz should not need to:

- remind the agent to run safe tests/checks,
- ask "what next?" after every meaningful step,
- approve every tiny docs/workflow edit after a clear safe work packet,
- read code just to understand what changed,
- manually test basic user journeys the agent can safely test,
- repeat durable corrections that should live in Koda/docs.

## What Hafiz Must Still Decide

Hafiz must still decide:

- product direction and priorities,
- business rules,
- subjective UX/copy acceptance,
- final risk acceptance when evidence has gaps,
- whether to expand scope,
- push, PR, merge, deploy, production mutation, destructive action, or critical-lane implementation,
- whether staff are ready for more Agent OS capability.

## What The Agent Must Do Before Asking Hafiz

Before asking Hafiz to verify or decide, the agent should:

1. Read the current source of truth.
2. Check relevant Koda memories.
3. Inspect current files/state instead of trusting old chat.
4. Run safe technical checks it can run.
5. Gather human-journey evidence where feasible.
6. Explain what was checked and what remains.
7. Ask only for the decision Hafiz is actually needed for.

Example:

```text
I checked the code path, ran the focused test, opened the page, and confirmed
the button now opens the modal. What still needs you is whether the wording is
acceptable for staff.
```

## Staff Role In Phase 1

For now, staff are mainly:

- source of reports,
- source of reproduction context,
- QA feedback providers,
- real-world workflow validators.

Staff are not full Agent OS builders by default.

Do not give staff production, deploy, Koda write, GitHub write, or critical-lane
capability unless Hafiz approves the person, scope, and access profile.

## Approval Boundaries

Use this simple rule:

```text
If it is safe technical work, the agent proceeds.
If it changes external state, money, data, production, access, risk, or
direction, Hafiz approves.
If it is real-world workflow feedback, staff can confirm but not own the
engineering decision.
```

Agent can usually do these inside the agreed task boundary:

- read normal repo docs/code,
- search Koda,
- inspect git status/diff,
- run safe tests/checks,
- update living Agent OS docs after Hafiz says to proceed,
- create a draft plan,
- recommend the next step.

Hafiz approval is required for:

- commit,
- push,
- opening a PR,
- merge,
- deploy,
- production mutation,
- DNS/server/config changes,
- payment, invoice, commission, auth, migration, or mobile API contract
  implementation,
- destructive actions,
- scope expansion,
- final risk acceptance.

Staff can confirm:

- what they saw,
- whether a real workflow feels fixed,
- whether the issue still happens,
- whether wording or process is confusing.

Staff cannot approve by default:

- deploy,
- production mutation,
- critical business rules,
- engineering issue closure,
- Koda write access,
- code push or merge.

Tools can record or check. Tools do not approve.

## Agent Ownership By Workflow

| Workflow | Agent owns | Hafiz owns |
| --- | --- | --- |
| Discussion / brainstorming | Explain options, tradeoffs, recommendation, and update living draft when asked. | Direction, preference, and final choice. |
| Product design | Draft brief, clarify gaps, UX flow, backend contract, build prompts, and risks. | Product direction, priorities, accepted tradeoffs, implementation approval. |
| Bug diagnosis | Reproduce/inspect, identify likely root cause, gather evidence, recommend fix. | Whether to proceed, defer, expand, or accept risk. |
| Implementation | Code/docs changes, focused checks, regression decision, evidence. | Approval for risky or expanded scope. |
| Verify / QA | Safe tests, browser/mobile/API checks, screenshots/evidence, remaining gaps. | Subjective acceptance and unsafe/unavailable checks. |
| Review | Risk findings, missing evidence, state clarity, recommended decision. | Final approval when business risk remains. |
| Commit | Guard checks, exact file list, commit message, local commit after approval. | Exact commit approval. |
| Push / PR / merge / deploy | Pre-push/release review, status inventory, evidence summary. | Explicit current-session approval for each outbound boundary unless an exact approved bundle includes it. |
| Save session / handoff | Preserve state, evidence, next action, Koda lessons, and handoff note. | Confirm whether to close, continue, or change priority when needed. |

## Common Failure Modes

| Failure | What should happen instead |
| --- | --- |
| Agent asks Hafiz to test something it can safely test. | Agent runs the safe check first, then asks only for judgment it cannot make. |
| Agent follows a staff report as root cause. | Treat it as a symptom, diagnose current evidence, then route engineering work. |
| Agent decides product direction alone. | Recommend and justify, then let Hafiz decide. |
| Agent waits for approval on every tiny safe docs edit. | Use a clear safe work packet and stop at commit/push/risky boundaries. |
| Agent uses old Koda/chat as truth. | Treat old context as historical and verify current files/state. |
| Agent says "done" when work is only local. | State the exact state: local, committed, pushed, PR open, merged, deployed, or live-smoke-passed. |

## Operating Rule

When unsure who owns a decision, ask:

```text
Is this technical execution the agent can safely verify, or is this business,
product, risk, access, or external-state approval?
```

If it is technical execution, the agent should do it.

If it is business/product/risk/access/external state, Hafiz decides.
