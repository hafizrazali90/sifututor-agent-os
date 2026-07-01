# Sifututor Agent OS

The **Sifututor Agent OS** is the shared operating layer for Hafiz, AI agents,
Koda, GitHub, Planner, Mission Ledger, and project-specific tools.

Its job is simple: help us plan, build, verify, remember, and ship work without
losing context or adding unnecessary ceremony.

## Core Terms

- **Agent OS**: the whole collaboration system.
- **Workflow**: one route inside the Agent OS, such as bugfix, feature,
  product design, QA, commit, or save-session.
- **Playbook**: the written steps for a workflow.
- **Router**: the part that decides which workflow applies.
- **First-mate routing**: the router's front-desk responsibility: translate
  Hafiz's request into workflow stage, finish point, worker/tool, evidence,
  approval stop point, and next action.
- **Guardrails**: rules and scripts that prevent expensive mistakes.
- **Working Agreement**: how Hafiz, Codex, Claude, and reviewers collaborate.

## Practical Meaning

The Agent OS is bigger than a workflow. A workflow is one path through the
system. The Agent OS includes:

- shared rules in `AGENTS.md`
- deeper project context in `CLAUDE.md`
- model-agnostic workflow rules that any capable LLM can follow
- Koda memory for durable lessons and preferences
- task state files for active work
- GitHub for engineering tickets and PRs
- Mission Ledger for bigger goals, paused decisions, and future follow-ups
- Planner for staff-reported intake where relevant
- playbooks under `docs/agent-playbooks/`
- guard scripts under `scripts/agent-checks/`
- agent adapters such as Codex skills/hooks and Claude skills

## First Operating Principle

Hafiz owns intent, product direction, business judgment, and risk acceptance.
The agent owns technical execution, testing, evidence, memory, and next-step
guidance.

Plain version:

```text
Hafiz decides what matters and what risk is acceptable.
The agent figures out the technical path, does the work, proves it, explains it,
remembers the lesson, and recommends the next move.
```

This is the main difference between a passive coding assistant and the
Sifututor Agent OS. Hafiz should not have to manage every command, test,
workflow step, or reminder. The agent should carry the technical burden and
pause only when a decision genuinely belongs to Hafiz: product direction,
business rules, subjective acceptance, external state, production, money, data,
access, critical lanes, destructive action, or final risk acceptance.

## Phased Purpose

Start narrow enough to work. Design wide enough to grow.

Phase 1 focuses on Hafiz and development delivery:

- Hafiz as the main user, owner, and decision maker.
- AI agents as the bridge between Hafiz and coding.
- Development work moving from idea or report to diagnosis, implementation,
  verification, QA, review, commit, release when approved, and memory.
- Staff as intake/report sources, not full Agent OS users yet.

Later phases expand into the full operating layer:

- Hafiz personal development OS.
- Staff-safe AI work system.
- Engineering delivery OS.
- Company-wide operating layer connecting people, agents, tools, memory,
  work intake, delivery, and rollout.

Plain version:

```text
Build first for Hafiz + development delivery.
Keep the core LLM-agnostic so Codex, Claude, Cursor, Copilot, Gemini, or future
agents can use adapters later.
Bring staff in as full users only after the internal workflow is stable.
```

## Core Layers

Use these twelve layers as the high-level table of contents for the Agent OS:

| Layer | Plain meaning |
| --- | --- |
| Purpose | Why the Agent OS exists and what good looks like. |
| People | Hafiz, agents, staff, developers, reviewers, and tool owners. |
| Intake | How work enters from chat, staff reports, Planner, GitHub, Koda, Mission Ledger, or production signals. |
| Routing | How the OS chooses discuss, diagnose, design, implement, verify, QA, review, commit, deploy, or save. |
| Workflows | The actual paths for bugfix, feature, critical lane, release, incident, and handoff. |
| Tools | What the active agent can access and how capability is checked. |
| Memory | What goes to Koda, docs, GitHub, Mission Ledger, or nowhere. |
| Testing | How the agent proves work through tests, E2E, smoke, screenshots, API checks, or monitoring. |
| Safety | Approval gates, forbidden actions, critical lanes, and destructive boundaries. |
| Continuation | How work resumes across chats, devices, agents, terminal sessions, compaction, or long pauses. |
| Agent Adapters | How Codex, Claude, and future LLMs connect to the same core rules. |
| Change Control | How Agent OS changes are proposed, reviewed, committed, and versioned. |
| Rollout | How the system is installed, trained, and expanded to staff or projects. |

Phase 1 should deeply build Purpose through Safety, with basic Codex/Claude
adapters. Change Control and Rollout stay lighter until the core is stable.

## First-Mate Routing

Task Router is the first-mate layer for now.

Plain version:

```text
Hafiz should be able to say the goal in normal language.
The router should decide the safest route, best worker/tool, proof needed,
where to stop, and the next action.
```

Do not create a separate first-mate agent yet. Start by strengthening
Task Router and split it out only if repeated real use shows the router is too
heavy or unclear.

## Continuation Standard

The Agent OS should feel continuous even when the chat, device, agent, or
terminal changes.

Plain version:

```text
The work should resume from a clear continuation pack, not from someone trying
to remember the old chat.
```

Use Session Map for the current story, save-session for the restart pack, Git
for exact file state, GitHub/PRs for engineering state, Koda for durable
lessons, and Mission Ledger for future or parked work.

Persistent environment tools such as tmux, WezTerm, SSH, Tailscale, or mosh are
optional helpers. They can keep a session alive, but they are not the source of
truth. A future agent should still be able to resume from the written
Continuation Pack.

## Collaboration Model

Use the lightest lane that fits the work:

- **Discussion / learning**: think together, explain, compare options. No code
  changes unless Hafiz asks to proceed.
- **Small change**: narrow edit, focused check, short close-out.
- **Normal engineering task**: route, implement, verify, QA, review, commit
  when approved.
- **Critical lane**: auth, payments, invoices, commissions, migrations,
  deployment, and mobile API contracts require read-only diagnosis first, then
  explicit approval before implementation.

## Resume Reconciliation

When a chat, project, or worktree has been idle long enough that another agent,
human, PR, or background process may have changed the state, start with a quick
reconciliation audit before continuing.

Plain version:

```text
Before we continue, first check what changed.
Do not assume the chat memory, open editor tabs, current branch, product repo,
or Koda memories are still the newest truth.
```

Use the lightest audit that fits:

- **Agent OS discussion**: check umbrella `git status`, recent commits, Koda
  health, and the relevant Agent OS docs. Do not deep-audit every product repo.
- **Product repo work**: check only the selected repo's branch, dirty files,
  active task state, recent commits, relevant docs, and safety rules before
  editing.
- **Cross-project confusion**: create a short workspace drift summary that
  separates clean/current repos from dirty, stale, sensitive, or blocked repos.

This is not a full review of every changed file. It is a map that tells Hafiz
and the agent what is safe to use now, what needs a focused audit later, and
what should not be touched without a scoped task.

## Internal-First Build

Build the Agent OS for the Sifututor workspace first. Staff distribution and
full multi-LLM rollout come later, after the internal system works reliably for
Hafiz, AI agents, Koda, GitHub, Planner, Mission Ledger, and the existing
product repos.

Internal-first means:

- prefer improving this umbrella repo before creating a separate public kit
- detect connected capabilities before relying on role labels
- keep Hafiz approval gates for push, deploy, production, and critical lanes
- verify important context before acting on it
- make the router understand intent, not only keywords
- keep Koda for distilled episodic lessons, not raw transcripts
- prove the OS with small workflow evals before expanding it to staff

## Default Agent Roles

- **Codex**: investigate, implement, run focused checks, explain practical
  meaning.
- **Claude**: adversarial review, broader QA, and final confidence checks when
  useful.
- **Future LLM adapters**: use the same core rules through their own adapter
  layer when the workflow is mature enough.
- **Hafiz**: owns product direction, risk tolerance, and ship decisions.

## North Star

The Agent OS should make the work safer and faster without making Hafiz feel
trapped inside process. Strict where mistakes are expensive. Lightweight when
we are thinking, learning, or making small safe changes.

Use [agent-os-general-guidelines.md](agent-os-general-guidelines.md) for the
baseline quality habits underneath every workflow: writing style, generated
files, commit co-author rules, quality-over-shortcut decisions, user-journey
bug proof, visible UI quality, lint/test/flaky-check handling, and scope
control.

## Architecture Index

Read these as the core internal kit:

| Layer | Source |
| --- | --- |
| Human-first architecture map | [agent-os-architecture-map.md](agent-os-architecture-map.md) |
| Full infrastructure map | [agent-os-infrastructure.md](agent-os-infrastructure.md) |
| Claude/Codex parity contract | [agent-os-parity-contract.md](agent-os-parity-contract.md) |
| Roles and responsibilities | [agent-os-roles.md](agent-os-roles.md) |
| Multi-agent and adapter workflow | [multi-agent-adapter-workflow.md](multi-agent-adapter-workflow.md) |
| Workflow skill registry | [agent-os-skill-registry.md](agent-os-skill-registry.md) |
| Hook and dispatcher map | [agent-os-hook-dispatcher.md](agent-os-hook-dispatcher.md) |
| How Hafiz and agents work together | [working-with-hafiz.md](working-with-hafiz.md) |
| Prompt routing | [agent-os-routing-model.md](agent-os-routing-model.md) |
| Approval boundaries | [agent-os-approval-gates.md](agent-os-approval-gates.md) |
| Plain-language communication | [agent-os-communication.md](agent-os-communication.md) |
| Context accuracy | [context-authority.md](context-authority.md) |
| Memory | [agent-os-memory.md](agent-os-memory.md), [agent-os-memory-architecture.md](agent-os-memory-architecture.md) |
| Tools and capability | [agent-os-capability-model.md](agent-os-capability-model.md) |
| Profile registry operations | [agent-os-profile-registry-operations.md](agent-os-profile-registry-operations.md) |
| Workflow intensity | [agent-os-workflow-lanes.md](agent-os-workflow-lanes.md) |
| General quality guidelines | [agent-os-general-guidelines.md](agent-os-general-guidelines.md) |
| Master workflow map | [agent-os-workflows.md](agent-os-workflows.md) |
| Planning artifacts | [planning-artifacts.md](planning-artifacts.md) |
| Change control and versioning | [agent-os-governance.md](agent-os-governance.md) |
| Verification and human-journey evidence | [agent-os-evidence-model.md](agent-os-evidence-model.md) |
| Final honesty gate | [no-mistakes-lite.md](no-mistakes-lite.md) |
| Parallel work and worktrees | [parallel-work-and-worktrees.md](parallel-work-and-worktrees.md) |
| Autonomous work packets | [autonomous-work-packets.md](autonomous-work-packets.md) |
| Task and release state | [agent-os-state-model.md](agent-os-state-model.md) |
| Bigger goals and remembered follow-ups | [mission-ledger.md](mission-ledger.md), [mission-ledger/README.md](mission-ledger/README.md) |
| Rollout readiness | [agent-os-rollout-readiness.md](agent-os-rollout-readiness.md) |
| Behavior checks | [agent-os-evals.md](agent-os-evals.md) |
| Evaluation harness | [agent-os-evaluation-harness.md](agent-os-evaluation-harness.md) |

## Research

Use [agent-os-research.md](agent-os-research.md) as the living research note for
external references, source-backed design lessons, and the distributable staff
starter-kit direction.

Use [agent-os-architecture-map.md](agent-os-architecture-map.md) when the Agent
OS feels confusing or too deep in details. It explains the whole system in
human-first language before diving into the infrastructure map, workflow
playbooks, skills, hooks, memory, and evidence rules.

Use [agent-os-infrastructure.md](agent-os-infrastructure.md) to understand how
Agent OS pieces fit together: hooks, workflow skills, playbooks, guards, Koda,
GitHub, Planner, Mission Ledger, evidence, and install checks.

Use [agent-os-skill-registry.md](agent-os-skill-registry.md) to understand
which Sifututor workflow skills exist, who owns them, what triggers them, which
playbook they follow, and what they must not hide.

Use [agent-os-hook-dispatcher.md](agent-os-hook-dispatcher.md) to understand
how Codex hooks add context, suggest workflow skills, inject Koda memories, and
where the hook must stop.

Use [agent-os-review-roadmap.md](agent-os-review-roadmap.md) to document what
exists today and review the internal Hafiz-Agent operating model one layer at a
time before expanding staff rollout.

Use [working-with-hafiz.md](working-with-hafiz.md) as the draft personal
operating model for how agents should interpret Hafiz's instructions, approval,
discussion, and close-out expectations.

Use [agent-os-routing-model.md](agent-os-routing-model.md) as the prompt
classification model before changing router hooks or playbooks.

Use [agent-os-approval-gates.md](agent-os-approval-gates.md) as the approval
model for relaxed work packets, exact bundles, and strict boundaries.

Use [agent-os-communication.md](agent-os-communication.md) as the communication
model for natural-language explanation, close-out, and workflow labels.

Use [agent-os-internal-build-plan.md](agent-os-internal-build-plan.md) for the
current internal MVP plan.

Use [agent-os-quick-start.md](agent-os-quick-start.md) at the start of a fresh
Codex or Claude session.

Use [context-authority.md](context-authority.md) when deciding whether context
is accurate enough to act on.

Use [agent-os-evals.md](agent-os-evals.md) to check whether the Agent OS routes,
guards, and approval gates behave correctly.

Use [agent-os-memory.md](agent-os-memory.md) when deciding whether an Agent OS
lesson belongs in Koda.

Use [agent-os-memory-architecture.md](agent-os-memory-architecture.md) for the
Memory System v2 plan: taxonomy, lifecycle tags, retrieval order, cleanup, and
active memory pack direction.

Use [agent-os-capability-model.md](agent-os-capability-model.md) to decide what
an agent can actually do based on connected tools, fallback paths, approval
gates, and forbidden boundaries.

Use [agent-os-profile-registry-operations.md](agent-os-profile-registry-operations.md)
when creating, updating, reviewing, auditing, downgrading, suspending, or closing
private profile assignment records.

Use [agent-os-workflow-lanes.md](agent-os-workflow-lanes.md) to choose the
right workflow intensity: Light, Medium, Full, or Critical.

Use [agent-os-workflows.md](agent-os-workflows.md) to map a request from intake
to design, build, verification, QA, review, commit, release, save-session, or
mission-ledger capture.

Use [agent-os-evidence-model.md](agent-os-evidence-model.md) to decide what the
agent should verify itself and what should be left for Hafiz's judgment.

Use [agent-os-state-model.md](agent-os-state-model.md) to decide where task
status, evidence, approvals, and release state should live.

Use [mission-ledger.md](mission-ledger.md) when a task, adjacent idea, paused
decision, or follow-up needs to stay linked to a bigger goal before it is ready
for GitHub, PRD, QA, or Koda.

Use [agent-os-rollout-readiness.md](agent-os-rollout-readiness.md) before
expanding the Agent OS from Hafiz/internal use to staff or project installs.

Use [agent-os-installation.md](agent-os-installation.md) and
[agent-os-install-manifest.json](agent-os-install-manifest.json) when checking
or applying the Agent OS baseline to another project.

Use [agent-os-staff-quick-start.md](agent-os-staff-quick-start.md) when rolling
out the Agent OS to staff using Codex, Claude, Copilot, Cursor, Gemini, or
another LLM-assisted tool.
