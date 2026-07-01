# Agent OS Improvement Loop

Use this when Hafiz asks to improve the Agent OS itself, fix workflow behavior,
make future agents handle something better, or prevent a repeated agent mistake.

Plain meaning:

```text
This is how the Agent OS gets better without becoming a pile of random rules.
```

This playbook is for improving the operating system around the agents. It is
not for fixing product bugs. Product bugfix quality belongs to the normal
diagnose, verify, QA, review, and future related-impact audit workflows.

## Core Rule

Do not fix Agent OS behavior in only one place unless one place truly owns it.

Use this loop:

```text
notice -> classify -> choose owner -> check connected files -> explain
-> update -> test -> remember -> close out
```

In normal words:

```text
First understand the workflow mistake. Then update the layer that owns the
behavior, check the nearby layers that depend on it, prove the wiring still
works, and leave a clear trail for future agents.
```

## When To Use

Use this playbook when Hafiz says things like:

- `improve the workflow`
- `fix this Agent OS behavior`
- `make future agents handle this better`
- `why did this happen again`
- `this is confusing`
- `Claude and Codex are behaving differently`
- `the skill/hook/workflow is not doing what we agreed`

Also use it when an agent notices repeated or expensive workflow drift.

Do not use it for:

- normal product implementation
- ordinary bugfixes
- user-facing QA
- production incidents
- one-time wording preferences that do not change future behavior

## Mistake Types

Classify the problem before editing.

| Mistake type | Meaning | Likely owner |
| --- | --- | --- |
| Communication | Hafiz did not get clear meaning, checks, state, or next action. | `agent-os-communication.md`, `working-with-hafiz.md`, response-shape checks |
| Routing | The agent picked the wrong workflow or misunderstood `proceed`, `approve`, `go next`, or `what next`. | `task-router.md`, `agent-os-routing-model.md`, evals, hook dispatcher |
| Approval | The agent asked too often, bundled too much, or crossed a boundary. | `agent-os-approval-gates.md`, `AGENTS.md`, commit/review playbooks |
| Memory | Koda was noisy, stale, missing, or treated as proof. | `agent-os-memory.md`, `agent-os-memory-architecture.md`, Koda fixtures |
| State | The agent mixed local, pushed, PR, merged, deployed, or live states. | `agent-os-state-model.md`, session ledger, close-out docs |
| Skill/playbook drift | A skill wrapper, playbook, or registry disagrees. | `agent-os-skill-registry.md`, `.agents/skills/*`, shared playbook |
| Hook/automation drift | A hook routes, blocks, or reminds incorrectly. | `agent-os-hook-dispatcher.md`, lifecycle hook, conversation fixtures |
| Eval/check gap | The mistake can repeat because no check catches it. | `agent-os-evals.md`, eval runner, fixture runners, health checks |
| Claude/Codex parity | Claude and Codex expose different behavior for the same workflow. | `agent-os-parity-contract.md`, skill registry, adapter docs |
| Workflow weight | The system is too heavy, too loose, or too annoying. | `agent-os-workflow-lanes.md`, workflow docs, Hafiz working model |

## Owner Decision

Use the lightest reliable home:

| If the fix is mainly... | Put it here |
| --- | --- |
| A durable lesson or correction | Koda, plus docs if behavior must change |
| A shared rule | `AGENTS.md` or the owning playbook |
| A repeated workflow path | A playbook and skill wrapper |
| A command/adapter gap | Skill registry, parity contract, Codex skill, Claude command |
| A dangerous action | Guard, hook, or hard rule |
| A repeated behavior mistake | Eval or fixture |
| Current-session continuity | Session Map |

Plain rule:

```text
Koda remembers. Docs define. Skills guide. Hooks remind or block. Evals catch
repeat mistakes. Health checks prove the wiring.
```

## Connected File Check

After choosing the owner, check only the relevant connected files. Do not scan
the whole workspace by default.

Common chains:

| Problem | Check these first |
| --- | --- |
| Agent did not explain next action | `agent-os-communication.md`, `working-with-hafiz.md`, `commit.md` or active playbook, response-shape runner |
| Wrong route selected | `task-router.md`, `agent-os-routing-model.md`, `agent-os-evals.md`, lifecycle hook |
| New workflow skill needed | `agent-os-skill-registry.md`, `.agents/skills/*`, `agent-os-workflows.md`, `README.md`, install manifest |
| New doc, duplicate doc, or skill sprawl | `skill-quality-and-pruning.md`, `doc-owner-route-index.md`, `agent-os-skill-registry.md`, `README.md`, evals |
| Claude/Codex mismatch | `agent-os-parity-contract.md`, registry, shared playbook, both adapters |
| Memory behavior wrong | `agent-os-memory.md`, memory architecture, Koda fixtures, Koda search/update |
| Hook behavior wrong | hook dispatcher doc, fixture first, hook code second |

## Required Explanation Before Editing

Before changing durable Agent OS files, explain:

- what behavior is wrong
- why it matters to Hafiz or future agents
- which source of truth owns it
- which connected files will be checked or updated
- what will not be touched
- how it will be checked
- whether Koda needs a memory

This keeps Hafiz in control without forcing him to read the diff manually.

## Update Rules

When updating:

- make the smallest coherent change
- avoid duplicate rules in many files
- link secondary files back to the source of truth
- use `skill-quality-and-pruning.md` before creating or splitting skills,
  playbooks, hooks, evals, or workflow docs
- update `doc-owner-route-index.md` when a new active Agent OS doc is added or
  ownership changes
- add an eval or fixture when the mistake is repeated, expensive, or easy to
  check
- update the skill registry when a skill changes or is added
- update the install manifest when distributable baseline files change
- update the Session Map when the current session direction changes
- save Koda only for durable behavior-changing lessons or corrections

Do not:

- create hook automation before the playbook/skill/eval shape is clear
- treat every preference as a hard-blocking rule
- save vague progress notes to Koda
- let old Koda memory override current docs or repo state
- mix this with product bug related-impact audits

## Checks

For documentation and skill-wrapper changes:

```bash
git diff --check
scripts/agent-checks/agent-os-eval-runner.py --self-test
scripts/agent-checks/agent-os-health.sh
scripts/agent-checks/workflow-doctor.sh
```

For hook or dispatcher changes, also run:

```bash
scripts/agent-checks/agent-os-conversation-fixture-runner.py
```

For skill registry, parity, or installer changes, also run:

```bash
scripts/agent-checks/agent-os-parity-fixture-runner.py
```

Before commit:

```bash
scripts/agent-checks/pre-commit-guard.sh
```

## Close-Out

End with:

- what behavior future agents should do differently
- what files changed
- what checks passed
- Koda stored/updated/skipped and why
- whether the change is local, committed, pushed, or still only discussed
- the next recommended action

## Example

Hafiz says:

```text
You committed but did not guide me what next.
```

The agent should classify it as:

```text
communication mistake + commit close-out gap + eval/check gap
```

Then it should check:

```text
agent-os-communication.md
commit.md
AGENTS.md close-out rule
.agents/skills/commit/SKILL.md
agent-os-evals.md or response-shape checks
Koda
Session Map
```

The fix should explain the new behavior in plain language and add a check if
the mistake should not quietly return.
