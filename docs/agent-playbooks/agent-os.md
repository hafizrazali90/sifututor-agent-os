# Sifututor Agent OS

The **Sifututor Agent OS** is the shared operating layer for Hafiz, Claude,
Codex, Koda, GitHub, Plane, Planner, and project-specific tools.

Its job is simple: help us plan, build, verify, remember, and ship work without
losing context or adding unnecessary ceremony.

## Core Terms

- **Agent OS**: the whole collaboration system.
- **Workflow**: one route inside the Agent OS, such as bugfix, feature,
  product design, QA, commit, or save-session.
- **Playbook**: the written steps for a workflow.
- **Router**: the part that decides which workflow applies.
- **Guardrails**: rules and scripts that prevent expensive mistakes.
- **Working Agreement**: how Hafiz, Codex, Claude, and reviewers collaborate.

## Practical Meaning

The Agent OS is bigger than a workflow. A workflow is one path through the
system. The Agent OS includes:

- shared rules in `AGENTS.md`
- deeper project context in `CLAUDE.md`
- Koda memory for durable lessons and preferences
- task state files for active work
- Plane and GitHub for human-visible tracking
- Planner for staff-reported intake where relevant
- playbooks under `docs/agent-playbooks/`
- guard scripts under `scripts/agent-checks/`
- Claude and Codex role split

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

## Internal-First Build

Build the Agent OS for the Sifututor workspace first. Staff distribution comes
later, after the internal system works reliably for Hafiz, Codex, Claude, Koda,
GitHub, Plane, Planner, and the existing product repos.

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
- **Hafiz**: owns product direction, risk tolerance, and ship decisions.

## North Star

The Agent OS should make the work safer and faster without making Hafiz feel
trapped inside process. Strict where mistakes are expensive. Lightweight when
we are thinking, learning, or making small safe changes.

## Architecture Index

Read these as the core internal kit:

| Layer | Source |
| --- | --- |
| How Hafiz and agents work together | [working-with-hafiz.md](working-with-hafiz.md) |
| Prompt routing | [agent-os-routing-model.md](agent-os-routing-model.md) |
| Approval boundaries | [agent-os-approval-gates.md](agent-os-approval-gates.md) |
| Plain-language communication | [agent-os-communication.md](agent-os-communication.md) |
| Context accuracy | [context-authority.md](context-authority.md) |
| Memory | [agent-os-memory.md](agent-os-memory.md), [agent-os-memory-architecture.md](agent-os-memory-architecture.md) |
| Tools and capability | [agent-os-capability-model.md](agent-os-capability-model.md) |
| Workflow intensity | [agent-os-workflow-lanes.md](agent-os-workflow-lanes.md) |
| Verification and human-journey evidence | [agent-os-evidence-model.md](agent-os-evidence-model.md) |
| Task and release state | [agent-os-state-model.md](agent-os-state-model.md) |
| Rollout readiness | [agent-os-rollout-readiness.md](agent-os-rollout-readiness.md) |
| Behavior checks | [agent-os-evals.md](agent-os-evals.md) |

## Research

Use [agent-os-research.md](agent-os-research.md) as the living research note for
external references, source-backed design lessons, and the distributable staff
starter-kit direction.

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

Use [agent-os-workflow-lanes.md](agent-os-workflow-lanes.md) to choose the
right workflow intensity: Light, Medium, Full, or Critical.

Use [agent-os-evidence-model.md](agent-os-evidence-model.md) to decide what the
agent should verify itself and what should be left for Hafiz's judgment.

Use [agent-os-state-model.md](agent-os-state-model.md) to decide where task
status, evidence, approvals, and release state should live.

Use [agent-os-rollout-readiness.md](agent-os-rollout-readiness.md) before
expanding the Agent OS from Hafiz/internal use to staff or project installs.

Use [agent-os-installation.md](agent-os-installation.md) and
[agent-os-install-manifest.json](agent-os-install-manifest.json) when checking
or applying the Agent OS baseline to another project.

Use [agent-os-staff-quick-start.md](agent-os-staff-quick-start.md) when rolling
out the Agent OS to staff using Codex, Claude, Copilot, Cursor, Gemini, or
another LLM-assisted tool.
