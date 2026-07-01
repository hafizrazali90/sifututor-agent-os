# Doc Routing And Context Loading

Use this when deciding which docs, playbooks, project files, or memories the
agent must read before acting.

Plain meaning:

```text
Do not make the agent read the whole library.
Make it open the right books for the current job.
```

This playbook exists because the Agent OS now has many docs.
A useful doc system needs routing, not volume.

## Core Rule

The agent should load context in layers:

```text
minimum contract -> current task route -> required docs -> triggered docs
-> current evidence
```

In normal words:

```text
Start with the shared rules.
Decide what kind of work this is.
Read the required docs for that kind of work.
Open extra docs only when the task trigger appears.
Then verify the current repo/tool state before acting.
```

Do not solve context misses by reading every file.
That wastes tokens, increases confusion, and makes the agent more likely to
miss the practical decision.

## Loading Levels

| Level | What it means | Examples |
| --- | --- | --- |
| Always | Small rules every agent needs. | `AGENTS.md`, current user instruction, nearest project `AGENTS.md` when editing a project. |
| Route required | Docs required by the chosen workflow. | `task-router.md`, `diagnose.md`, `commit.md`, `product-design.md`. |
| Triggered | Docs required only when a condition appears. | `TESTING.md` for user-facing work, UI/UX docs for SIMS UI, critical-lane docs for payments/auth/invoices/mobile API. |
| Evidence | Current state that proves what is true now. | `git status`, active task file, tests, browser evidence, PR/CI/deploy/monitoring state. |
| Deep reference | Detailed docs opened only when the first docs point there or the agent is blocked. | architecture notes, feature docs, old research, long historical reports. |

## Required Doc Matrix

Use this matrix after Task Router identifies the route.

| Work type | Must read first | Then read if triggered |
| --- | --- | --- |
| Any meaningful work | `AGENTS.md`, current user instruction, active Session Map when resuming, relevant Koda memories when available. | `CLAUDE.md` for umbrella/project orientation; project `AGENTS.md` when editing inside a project. |
| Agent OS docs or workflow improvement | `task-router.md`, `agent-os-improvement-loop.md`, this doc, relevant owning playbook. | `agent-os-skill-registry.md`, `agent-os-evals.md`, hook/dispatcher docs, parity docs, Koda, Session Map. |
| Brainstorming or product design | `product-design.md`, `planning-artifacts.md`, relevant feature/project docs. | `ai-implementation-readiness.md` for handoff/cross-module/critical workflows; UI/UX docs for interface design. |
| Bug or staff symptom | `diagnose.md`, `task-router.md`, current project rules. | Planner context for staff-reported SIMS/mobile issues; `related-impact-audit.md`; `TESTING.md`; feature docs. |
| User-facing feature or fix | `task-router.md`, `verify.md`, `qa.md`, project rules, `TESTING.md` when present. | UI/UX docs, feature docs, E2E specs, `agent-os-evidence-model.md`, release communication rules. |
| Critical lane | `diagnose.md`, `ai-implementation-readiness.md`, `agent-os-approval-gates.md`. | Domain docs for auth, payments, invoices, commission, migration, deploy, or mobile API contract; safe read-only access map. |
| Verify or QA | `verify.md` or `qa.md`, `agent-os-evidence-model.md`, project rules. | `TESTING.md`, feature docs, Playwright/mobile docs, monitoring/access docs if evidence depends on them. |
| Review, push, PR, merge, deploy, or live claim | `review.md`, `no-mistakes-lite.md`, state/evidence docs. | `push-pr-ci-automation.md`, `release-deploy-live-monitoring.md`, `incident-workflow.md`, Session Release Ledger when multiple fixes exist. |
| Commit | `commit.md`, `review.md`, `no-mistakes-lite.md`, current git diff/status. | Session Release Ledger for multiple fixes; release communication docs for staff-facing changes. |
| Save, handoff, snapshot, or continuation | `save-session.md`, `handoff.md` or `snapshot.md`, `session-map.md`. | Koda memory docs, Mission Ledger when the item is future/parked, Git/PR/deploy state. |
| Project adoption or staff rollout | `project-adoption.md`, `agent-os-rollout-readiness.md`, `agent-os-installation.md`, capability model. | staff quick start, project profile, access registry, parity/adapter docs. |

## Trigger Rules

Open these docs when the trigger is present.

| Trigger | Open |
| --- | --- |
| `sifu-tutor` browser UI, SIMS page layout, staff-facing copy, visual QA | `sifu-tutor/docs/ui-ux/README.md` and the relevant feature docs it points to. |
| User-facing behavior changes | Project `TESTING.md` if present, existing E2E specs, `test-coverage.md`, `agent-os-evidence-model.md`. |
| Staff-reported SIMS/tutor/parent app issue | Planner intake context when available, then normal engineering route. |
| Auth, payment, invoice, commission, migration, deploy, production data, or mobile API contract | Critical-lane diagnosis docs and approval gates before implementation. |
| Multiple fixes, branches, PRs, or deploy candidates in one chat | `session-release-ledger.md` and the active Session Map. |
| Long, confusing, or multi-goal session | `session-map.md`; update the current map before going deeper. |
| Agent OS behavior change | `agent-os-improvement-loop.md`, owning playbook, skill registry, evals, and Session Map. |
| Claude/Codex behavior mismatch | `agent-os-parity-contract.md`, `agent-os-skill-registry.md`, adapter docs, and evals. |
| Tool/access uncertainty | `agent-os-capability-model.md`, `agent-access-map.md`, relevant probe/wrapper docs. |
| Production/live-state claim | Git/PR/deploy evidence, `release-deploy-live-monitoring.md`, monitoring docs. |

## Skip Rules

Do not load extra docs just because they exist.

Skip deep docs when:

- the task is a tiny typo or formatting-only change;
- the doc is about a different project;
- the doc is historical and the current route already has a source of truth;
- the task is discussion-only and Hafiz has not asked to document or implement;
- the next action is only a local commit of an already-approved exact bundle.

Plain version:

```text
Context should help the agent decide and act.
If a doc does not change the decision, proof, safety boundary, or next action,
do not spend context on it yet.
```

## Readback Requirement

After loading docs for a meaningful task, the agent should be able to say:

```text
I read the route docs for this work.
The important rule is...
The next action is...
```

Do not list every file mechanically in normal conversation.
Use natural language unless Hafiz asks for the audit trail.

Example:

```text
I treated this as Agent OS workflow improvement, so I used the improvement loop,
the skill registry, and evals. The practical rule is: update the owner doc, then
check the connected docs so the behavior does not drift.
```

## Missed-Doc Recovery

If the agent realizes it missed a relevant doc:

1. Stop before further edits if the missing doc may change the decision,
   safety boundary, evidence, or file scope.
2. Read the missed doc.
3. Compare it with what was already done.
4. Adjust the work if needed.
5. Say plainly what changed.
6. Add an eval or Koda lesson only if the miss is likely to repeat.

Plain version:

```text
Missing a doc is recoverable.
Pretending the doc was not needed is not.
```

## What Future Automation Should Check

The ideal future hook does not need to read every doc.
It should warn when the selected route is missing a required doc family.

Examples:

- commit request without `commit.md`
- Agent OS change without `agent-os-improvement-loop.md`
- user-facing product change without `TESTING.md` decision
- SIMS UI work without UI/UX docs
- push/deploy/live claim without review/evidence/state docs

These warnings should be guidance first.
Only secrets, forbidden paths, destructive actions, critical-lane implementation,
and hook/test bypasses should become hard blocks.
