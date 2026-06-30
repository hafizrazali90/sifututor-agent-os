# Agent OS Architecture Map

Use this when the Agent OS feels confusing, too abstract, or too deep in
individual playbooks.

Plain meaning:

```text
This is the floor plan.
It explains what the Agent OS is, what each part does, and where we are in the
build.
```

This document is human-first. It does not replace the detailed playbooks. It
helps Hafiz, Codex, Claude, and future LLMs understand the whole system before
changing another part of it.

## What Agent OS Is

The Sifututor Agent OS is the operating layer for how Hafiz, AI agents,
developer staff, tools, memory, GitHub, Planner, and project repos work
together.

It is not only a workflow.

It is also not only memory, skills, hooks, prompts, or documentation.

The Agent OS is the combined system that decides:

- how work starts
- how the right workflow is chosen
- how the agent explains the work to Hafiz
- what the agent can safely do by itself
- when Hafiz must decide
- what evidence proves the work
- where context and lessons are stored
- how Codex, Claude, and future LLMs behave consistently
- how the OS improves when something frustrates Hafiz

Short version:

```text
Agent OS makes AI-assisted development predictable.
```

## Why We Are Building It

Hafiz is technical and self-taught, but does not want to personally read every
line of code to manage development.

The agent should be the bridge between Hafiz and code:

- understand the problem
- suggest options
- explain tradeoffs in normal language
- implement when approved
- test like a capable human tester
- prove what is done
- remember durable lessons
- guide the next step

The goal is not to make Hafiz follow a rigid process.

The goal is to let Hafiz stay in control of direction and risk while the agent
handles the technical work properly.

## The Seven Core Parts

Use these seven parts as the simple mental model.

| Part | Plain meaning | Main sources |
| --- | --- | --- |
| 1. Working Agreement | How Hafiz and agents talk, decide, approve, and close work. | `working-with-hafiz.md`, `agent-os-communication.md`, `agent-os-approval-gates.md` |
| 2. Workflow Playbooks | The routes for bugfix, feature, QA, review, commit, release, incident, and save-session work. | `agent-os-workflows.md`, `task-router.md`, `verify.md`, `qa.md`, `review.md`, `commit.md`, `save-session.md` |
| 3. Skills And Adapters | The buttons or wrappers each agent uses to follow the same playbooks. | `agent-os-skill-registry.md`, `multi-agent-adapter-workflow.md`, `.agents/skills/*` |
| 4. State And Memory | Where the truth lives: current session, durable lessons, exact file changes, PR state, deployment state, and future follow-ups. | `agent-os-state-model.md`, `agent-os-memory.md`, `agent-os-memory-architecture.md`, `session-map.md`, `mission-ledger.md` |
| 5. Tools And Permission Profiles | What tools the agent or developer staff can use, how access is checked, and what requires approval. | `agent-os-capability-model.md`, `agent-access-map.md`, `agent-os-approval-gates.md` |
| 6. Evidence And Testing | How the agent proves the work like a human tester would, not only by reading code. | `agent-os-evidence-model.md`, `verify.md`, `qa.md`, `test-coverage.md` |
| 7. Improvement And Governance | How the Agent OS learns from repeated mistakes without becoming messy. | `agent-os-improvement-loop.md`, `agent-os-governance.md`, `agent-os-evaluation-harness.md`, `agent-os-evals.md` |

Non-technical version:

```text
Agreement tells us how to work.
Workflows tell us what path to follow.
Skills let each LLM use the path.
State and memory stop us losing the story.
Tools and profiles control what agents can access.
Evidence proves the work.
Improvement fixes the OS when it annoys or fails us.
```

## How The Parts Work Together

When Hafiz asks for something, the Agent OS should move like this:

```text
Request
-> understand the signal
-> choose the workflow
-> check current state and memory
-> explain the practical goal and stop point
-> use the right tools
-> implement or document
-> verify with the right evidence
-> review risk before outward state changes
-> commit/push/deploy only inside approved boundaries
-> save lessons and next action
```

Example:

```text
Hafiz: "Fix this staff bug."

Agent OS path:
1. Treat the report as a signal, not proof yet.
2. Diagnose current code/UI/data/logs where safe.
3. Decide if it is bugfix, feature, training gap, or support issue.
4. Create or link engineering task when ready.
5. Fix with focused tests.
6. Prove the human journey works.
7. Review same-pattern and regression risk.
8. Commit only after guard/checks.
9. Explain what changed, what was checked, and what is next.
```

## What We Have Built So Far

This is the current foundation status.

| Area | Current state | Practical meaning |
| --- | --- | --- |
| Working Agreement | Built and improving | Agents should explain in plain language, recommend next steps, and avoid making Hafiz ask "what next?" repeatedly. |
| Workflow Playbooks | Built for the main routes | Bugfix, feature, verify, QA, review, commit, save-session, release, incident, and workflow-improvement have shared references. |
| Claude/Codex Parity | Built for the core workflows | Claude and Codex may use different commands, but should follow the same playbooks. |
| Session Map | Built and active | Long sessions should keep a map of goal, side paths, state, evidence, and next action. |
| State Ownership | Built | Planner, GitHub, Koda, Session Map, Git, PRs, deploy records, and QA evidence each own different truth. |
| Evidence Model | Built | The agent should prove code behavior, user journey, and release state separately. |
| Improvement Loop | Built | Workflow mistakes should update the right docs, skills, checks, Koda, or session map instead of becoming another apology. |
| Tool Decision Flow | Built locally | Agents should choose CLI, connector, API wrapper, browser, or native app control based on the task and evidence need. |
| Permission Profiles | Built locally | Access starts least-privilege; tool connection, permission, approval, and proof are separate. |
| Profile Records | Built locally | Public docs define rules; real person/agent assignments belong in a private registry or task approval trail. |

## What Is Still Missing Or Not Final

These are not failures. They are open construction areas.

| Area | What is missing | Why it matters |
| --- | --- | --- |
| Private profile registry operations | We have the rule and template, but not the exact daily routine for creating, reviewing, and cleaning real entries. | Without this, access records can become stale or confusing. |
| Staff/developer rollout | Parked by Hafiz for now. | The core OS should be stable before developer staff use it. Ordinary staff stay in Teams Planner. |
| Project-by-project adoption | Some repos still need verified local profiles. | A shared Agent OS needs local project commands, evidence, deploy path, and critical-lane rules. |
| More eval coverage | Existing checks cover important behaviors, but more real scenarios can be added. | Rules are stronger when checks catch drift. |
| Cleaner human dashboard | Session Map HTML exists, but the overall Agent OS map can become easier to scan. | Hafiz should not need to read walls of text to know where we are. |
| Long-term distribution kit | Not the priority yet. | Build for ourselves first, then package for staff or other LLMs later. |

## What Hafiz Controls

Hafiz owns decisions where judgment, risk, money, product direction, or external
state matter.

Examples:

- product direction
- priority
- whether a workflow feels right
- accepting subjective UX
- push, PR, merge, deploy, production, or destructive boundaries
- auth, payment, invoice, commission, migration, and mobile API contract risk
- giving a person or agent stronger tool access
- final business acceptance

The agent should recommend clearly, but Hafiz decides.

## What The Agent Can Autopilot

Inside an approved safe boundary, the agent should do the technical work instead
of making Hafiz micromanage.

Examples:

- read relevant docs and current files
- search Koda for durable lessons
- inspect git state
- run safe local checks
- use approved read-only evidence lanes when relevant
- update scoped docs/playbooks
- run Agent OS health/eval checks
- commit locally when the commit bundle was clearly approved
- explain what changed and what comes next

Plain version:

```text
Hafiz decides direction and risk.
The agent handles the technical path and proof.
```

## What Must Stop For Approval

Even in autopilot, some boundaries should stop unless already explicitly
included in the approved path.

| Boundary | Why |
| --- | --- |
| Push to GitHub | It changes shared remote state. |
| Open PR | It creates reviewable external state. |
| Merge | It changes main/shared integration state. |
| Deploy | It changes an environment. |
| Production action | It can affect real users or business operations. |
| Destructive action | It can delete or damage data/state. |
| Critical-lane implementation | Auth, payment, invoice, commission, migration, and mobile API contracts need stronger review. |
| Secrets or `.env*` access | Forbidden in repo context. Use scoped wrappers only when approved and never print secrets. |

## How To Use This Map

At the start of an Agent OS session:

1. Read this map if the topic feels broad or confusing.
2. Check the active Session Map for current state.
3. Choose the one Agent OS part being discussed now.
4. Explain that part in plain language.
5. Only then update the detailed docs, skills, checks, or Koda.

When Hafiz says "I do not understand what we are doing":

```text
Stop adding new rules.
Return to this map.
Say which part of the Agent OS we are currently touching.
Explain why that part matters before continuing.
```

## Current Recommended Review Order

Use this order when continuing the Agent OS build:

1. Architecture map and current status.
2. Private profile registry operations.
3. Project adoption profiles.
4. Staff/developer rollout after core stability.
5. More evals and dashboard improvements.
6. Distribution kit for other LLMs or staff.

This order is not permanent. It is the current practical path from confusion to
control.

