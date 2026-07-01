# Doc Owner And Route Index

Use this as the map of Agent OS documents by owner and route.

Plain meaning:

```text
This is the library shelf map.
It tells future agents where a rule belongs before they add another file.
```

This index is intentionally higher level than [README.md](README.md).
The README lists available docs.
This index explains who owns the decision.

## Core Owners

| Owner | Owns | Main docs |
| --- | --- | --- |
| Operating contract | Rules every agent must obey. | `AGENTS.md`, `agent-os.md`, `agent-os-general-guidelines.md` |
| Routing and context loading | What workflow applies and which docs to read. | `task-router.md`, `agent-os-routing-model.md`, `doc-routing-and-context-loading.md`, `agent-os-workflow-lanes.md`, `agent-os-runtime-reliability.md` |
| Skill and doc quality | Whether to create, update, merge, park, or delete Agent OS artifacts. | `skill-quality-and-pruning.md`, `agent-os-skill-registry.md`, this index |
| Communication with Hafiz | How to explain work, status, risk, and next steps. | `working-with-hafiz.md`, `agent-os-communication.md` |
| State and continuation | What is drafted, local, committed, pushed, PR-open, merged, deployed, live, parked, or handed off. | `agent-os-state-model.md`, `session-map.md`, `save-session.md`, `handoff.md`, `snapshot.md`, `session-release-ledger.md` |
| Memory | What belongs in Koda, docs, Session Map, Mission Ledger, or nowhere. | `agent-os-memory.md`, `agent-os-memory-architecture.md`, `context-authority.md` |
| Evidence and testing | How the agent proves work. | `agent-os-evidence-model.md`, `verify.md`, `qa.md`, `test-coverage.md`, `review.md`, `no-mistakes-lite.md` |
| Safety and approvals | What needs approval or must never happen. | `agent-os-approval-gates.md`, `agent-access-map.md`, `agent-os-capability-model.md`, `commit.md` |
| Workflow improvement and governance | How the Agent OS changes itself safely. | `agent-os-improvement-loop.md`, `agent-os-governance.md`, `agent-os-enforcement-drift.md`, `agent-os-evals.md`, `agent-os-eval-coverage-map.md`, `agent-os-evaluation-harness.md`, `agent-os-scenario-lab.md` |
| Multi-agent and adapters | How Claude, Codex, and future LLMs use the same core. | `agent-os-parity-contract.md`, `agent-os-skill-registry.md`, `agent-os-adapter-readiness.md`, `agent-os-hook-dispatcher.md`, `multi-agent-adapter-workflow.md`, `switching-claude-codex.md` |
| Planning and product design | How vague ideas become understandable build work. | `planning-artifacts.md`, `product-design.md`, `ai-implementation-readiness.md` |
| Delivery and release | How PR, CI, merge, deploy, smoke, monitoring, and incidents work. | `push-pr-ci-automation.md`, `release-deploy-live-monitoring.md`, `monitor-production-logs.md`, `incident-workflow.md` |
| Project adoption and rollout | How repos and developer staff adopt the Agent OS. | `project-adoption.md`, `agent-os-rollout-readiness.md`, `agent-os-installation.md`, `agent-os-staff-quick-start.md`, project profiles |
| Bigger goals and future work | What is useful but not execution-ready. | `mission-ledger.md`, `mission-ledger/*`, `workflow-efficiency-audit.md` |
| Research and history | Why decisions were made or what happened in old sessions. | `agent-os-research.md`, `agent-os-review-roadmap.md`, session-save docs, parity/status reports |

## Route Quick Map

| If the user asks... | Start with | Then use |
| --- | --- | --- |
| "What should we do next?" | `task-router.md` | active Session Map, state model, doc routing, runtime reliability |
| "Improve the workflow" | `agent-os-improvement-loop.md` | skill registry, skill quality, evals, Koda, Session Map |
| "Which docs should the LLM read?" | `doc-routing-and-context-loading.md` | this index, task router |
| "Should this be a skill?" | `skill-quality-and-pruning.md` | skill registry, parity contract |
| "Why is Agent OS confusing?" | `agent-os-architecture-map.md` | infrastructure map, this index, roadmap |
| "Fix a bug" | `diagnose.md` | related-impact audit, verify, QA, review, TESTING.md if present |
| "Build a feature" | `task-router.md` | planning artifacts, product design, implementation readiness, verify, QA |
| "Verify or QA this" | `verify.md` or `qa.md` | evidence model, TESTING.md, project docs |
| "Review this" | `review.md` | no-mistakes-lite, evidence/state docs |
| "Commit this" | `commit.md` | review/no-mistakes-lite, current git diff/status |
| "Push/open PR/merge/deploy" | `review.md` | push-pr-ci automation or release monitoring, approval gates |
| "Save or hand off" | `save-session.md` or `handoff.md` | Session Map, Koda, state model |

## Active Doc Inventory

Use this inventory to avoid creating duplicate docs.
If a new idea fits one of these rows, update that owner first.

| Owner | Active docs |
| --- | --- |
| Overview and architecture | `agent-os.md`, `agent-os-architecture-map.md`, `agent-os-infrastructure.md`, `agent-os-internal-build-plan.md`, `agent-os-quick-start.md` |
| Routing and workflow weight | `task-router.md`, `agent-os-routing-model.md`, `agent-os-workflow-lanes.md`, `doc-routing-and-context-loading.md`, `doc-owner-route-index.md`, `agent-os-runtime-reliability.md` |
| Skill and adapter system | `agent-os-skill-registry.md`, `skill-quality-and-pruning.md`, `agent-os-parity-contract.md`, `agent-os-adapter-readiness.md`, `multi-agent-adapter-workflow.md`, `switching-claude-codex.md`, `agent-os-hook-dispatcher.md`, `codex-hook-trust.md` |
| Hafiz working model and communication | `working-with-hafiz.md`, `agent-os-communication.md`, `agent-os-roles.md`, `agent-os-general-guidelines.md` |
| Planning and implementation readiness | `planning-artifacts.md`, `product-design.md`, `ai-implementation-readiness.md`, `agent-os-workflows.md` |
| Diagnosis, implementation proof, and QA | `diagnose.md`, `verify.md`, `qa.md`, `review.md`, `no-mistakes-lite.md`, `related-impact-audit.md`, `test-coverage.md`, `agent-os-evidence-model.md` |
| State, continuation, and session control | `agent-os-state-model.md`, `context-authority.md`, `session-map.md`, `session-release-ledger.md`, `save-session.md`, `handoff.md`, `snapshot.md`, `active-tasks.md` |
| Memory | `agent-os-memory.md`, `agent-os-memory-architecture.md` |
| Safety, capability, and access | `agent-os-approval-gates.md`, `agent-os-capability-model.md`, `agent-access-map.md`, `commit.md` |
| GitHub, PR, release, deploy, and incidents | `push-pr-ci-automation.md`, `release-deploy-live-monitoring.md`, `monitor-production-logs.md`, `incident-workflow.md`, `product-push-map.md` |
| Governance, improvement, and evals | `agent-os-improvement-loop.md`, `agent-os-governance.md`, `agent-os-enforcement-drift.md`, `agent-os-evals.md`, `agent-os-eval-coverage-map.md`, `agent-os-evaluation-harness.md`, `agent-os-scenario-lab.md`, `agent-os-coverage-audit.md`, `workflow-efficiency-audit.md` |
| Installation, rollout, and project profiles | `agent-os-installation.md`, `agent-os-install-manifest.json`, `agent-os-rollout-readiness.md`, `agent-os-staff-quick-start.md`, `project-adoption.md`, `agent-os-profile-registry-operations.md`, project profiles under `project-profiles/` |
| Mission and future work | `mission-ledger.md`, `mission-ledger/*`, `plane.md` |
| Research and roadmap | `agent-os-research.md`, `agent-os-review-roadmap.md`, `parity-status.md`, `claude-codex-parity-implementation-report.md`, `commit-plan.md`, `lls-workflow-migration.md`, `workflow-rollout-cleanup.md`, `README.md` |
| Historical session saves | `session-save-*.md` |

## Historical Or Reference-Only Docs

Historical docs may be useful, but they should not silently control new work.

Treat these as reference unless the active route points to them:

- `claude-codex-parity-implementation-report.md`
- `commit-plan.md`
- `parity-status.md`
- `product-push-map.md`
- `session-save-*.md`
- `lls-workflow-migration.md`
- `workflow-rollout-cleanup.md`

If a historical doc conflicts with current `AGENTS.md`, active playbooks, or
current Git state, the current source wins.

## When Adding A New Doc

Before adding a new Agent OS doc, update this index or explain why not.

The new doc must answer:

```text
Who owns this rule?
Which route reads it?
Which existing docs should link to it?
Is it active, parked, or historical?
How will future agents know it exists?
```

If these questions are hard to answer, the new doc probably belongs as a
section inside an existing owner instead.

## When A Doc Feels Duplicated

Use [skill-quality-and-pruning.md](skill-quality-and-pruning.md).

Plain version:

```text
Pick one owner.
Move the useful rule there.
Turn the duplicate into a pointer or park it.
Delete only when references are clean.
```
