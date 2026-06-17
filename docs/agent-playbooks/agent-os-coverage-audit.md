# Agent OS Coverage Audit

Last audited: 2026-06-17

Use this audit before adding more Agent OS rules, playbooks, scripts, or staff
rollout assets.

Plain meaning: this file is the map that stops us from discovering Agent OS
gaps randomly. It shows what exists, what is deep enough, what is shallow, what
is missing, and what should be reviewed next.

## Repo State Note

This audit was first drafted during an Agent OS cleanup session, when some
playbook changes still lived in local backups and stashes.

Before publishing this audit, the durable pieces were split into separate PRs:

- Autopilot boundary rule.
- Mission Ledger workflow and checker.
- This architecture/workflow coverage batch.

Plain meaning: this file should now be read as a product/workflow audit, not as
a live report about local branch cleanliness. Use `git status`, PR state, and
the current Agent OS health check for live repo state.

## Coverage Scale

| Depth | Meaning |
| --- | --- |
| Deep | Source of truth exists, workflow is clear, checks or examples exist, and the rule has been used. |
| Medium | Source exists and direction is clear, but the workflow needs examples, integration, or stronger checks. |
| Shallow | A concept exists, but day-to-day behavior is not mapped deeply enough. |
| Missing | No proper source of truth or review artifact exists yet. |
| Drift risk | Multiple files or sessions contain related rules that may conflict or diverge. |

## Executive Summary

The Agent OS is strong in these areas:

- Hafiz-agent working style
- approval gates
- context authority
- memory rules
- capability model
- response shape
- state wording
- executable harness for routing, Koda, capability, and conversation behavior
- master workflow architecture

The Agent OS is still weak in these areas:

- workflow examples and real-world transition coverage
- work intake across Hafiz chat, Planner, Plane, GitHub, staff reports, and production signals
- project adoption by product repo
- release/deploy/monitoring path
- incident workflow
- staff rollout pilot
- governance and versioning of Agent OS changes

The biggest correction:

```text
We have tested the guardrails more deeply than we have designed the workflows.
```

## Coverage Matrix

| Area | Purpose | Current Assets | Depth | Risk If Ignored | Recommended Next Artifact |
| --- | --- | --- | --- | --- | --- |
| Working With Hafiz | Define how agents interpret Hafiz's instructions and close out work. | `working-with-hafiz.md`, `AGENTS.md`, conversation fixtures, response-shape runner. | Deep | Agents become technically correct but frustrating or too ceremonial. | Add richer examples for bugs, design, QA, and blocked work. |
| Intent Routing | Decide whether the prompt means discuss, plan, build, verify, QA, review, commit, save, or handoff. | `task-router.md`, `agent-os-routing-model.md`, Codex hook, eval runner, conversation fixtures. | Deep for prompt behavior; medium for real workflow transitions. | Agents route by keyword or miss the user's actual intent. | Add workflow transition map from intake to done. |
| Approval Gates | Define what can be bundled and what needs separate approval. | `agent-os-approval-gates.md`, `commit.md`, `review.md`, `AGENTS.md`, approval evals. | Deep | Agent oversteps commit, push, deploy, critical, or destructive boundaries. | Add examples for GitHub issue creation, Plane updates, and staff capability escalation. |
| Communication And Close-Out | Make agent reporting useful without process noise. | `agent-os-communication.md`, response-shape runner, `README.md`, `AGENTS.md`. | Deep for final shape; medium for scenario variety. | Hafiz keeps needing to ask "what next?" or decode workflow labels. | Add richer response fixtures for practical meaning and non-technical explanations. |
| Context Authority | Decide what is true enough to act on. | `context-authority.md`, routing rules, Koda guidance. | Medium | Agent trusts stale memory, staff symptom, or old chat over current source. | Add source-of-truth examples for SIMS, billing, Planner, Plane, GitHub, and production evidence. |
| Memory And Koda | Store durable lessons without turning memory into transcript noise. | `agent-os-memory.md`, `agent-os-memory-architecture.md`, Koda CLI, save-session, Koda fixtures. | Deep for rules; medium for operations. | Koda becomes noisy, stale, or unreliable during critical continuation. | Build read-only Koda audit plan before any migration. |
| Capability Model | Decide what the current agent can actually do. | `agent-os-capability-model.md`, `capabilities.example.json`, health script, capability fixtures. | Medium | Agent assumes tools exist or grants staff unsafe capability. | Add live connector probes only where safe and stable. |
| Guardrails | Prevent forbidden or expensive actions. | `AGENTS.md`, pre-commit guard, sensitive-path check, branch check, health checks, remote sensitive-path fixture. | Medium | False positives block valid work, or false negatives allow secret/live mistakes. | Merge/reconcile PR `#8` sensitive-path guard and include it in health/install coverage. |
| Workflow Lanes | Choose the intensity: Light, Medium, Full, Critical. | `agent-os-workflow-lanes.md`, `agent-os-workflows.md`, `task-router.md`. | Medium | Lanes and route maps exist, but need more real-world examples from actual Sifututor work. | Review work intake and add examples where agents still hesitate or over-ask. |
| Work Intake | Convert inputs into the right source of truth and workflow. | `task-router.md`, Planner rules, Plane playbook, GitHub issue rule, mission ledger. | Shallow | Staff reports, Hafiz chat, GitHub issues, Plane missions, and Planner cards become inconsistent. | Define intake workflow by source: Hafiz, staff, Planner, Plane, GitHub, production, Koda. |
| Mission Ledger | Capture bigger goals, adjacent ideas, and paused follow-ups before they become GitHub/Plane work. | `mission-ledger.md`, project ledger files, `mission-ledger-check.py`, local mission entries. | Medium but newly added | Follow-ups vanish in chat or get converted into noisy issues too early. | Review mission ledger workflow and decide when to promote to GitHub, Plane, PRD, or Koda. |
| Product Design | Turn ideas into PRD, clarifier, UX spec, backend contract, and build prompts. | `product-design.md`, AI implementation readiness, UI/UX pre-read changes. | Medium | Agents build before requirements, UX, RBAC, backend contract, or evidence are clear. | Review how Hafiz wants to use design artifacts in real work. |
| SIMS UI/UX Workflow | Ensure browser UI changes follow the SIMS design system and quality gate. | UI/UX pre-read, verification, QA, and review rules in `product-design.md`, `task-router.md`, `verify.md`, `qa.md`, and `review.md`; `sifu-tutor/docs/ui-ux/*`. | Medium | UI work drifts into one-off patterns, weak states, unclear copy, or missing screenshots. | Add richer examples and screenshots from real SIMS UI releases. |
| Bugfix Workflow | Diagnose, reproduce, fix, regression test, verify, QA, review, commit. | `diagnose.md`, `verify.md`, `qa.md`, `review.md`, `test-coverage.md`. | Medium | Fixes are declared done without reproduction, regression, or human-journey proof. | Write explicit bugfix workflow in `agent-os-workflows.md`. |
| Feature Workflow | Move from idea to design to implementation slices to QA/release. | `product-design.md`, `task-router.md`, `ai-implementation-readiness.md`, verify/QA/review. | Shallow to medium | Agents overbuild or implement weak adjacent behavior. | Write feature workflow with slice gates and build prompt quality rules. |
| Staff Issue Workflow | Convert staff symptoms into engineering work and close the loop. | Planner intake rules, task router, review/QA, state model. | Shallow | Staff-reported issues are treated as verified root cause or lost after fix. | Define Planner/support intake workflow and staff close-loop evidence. |
| Verification | Prove implementation works with the right strength. | `verify.md`, evidence model, test coverage rule, permanent E2E rule, UI/UX verify edits. | Medium to deep | Agent asks Hafiz to test what it could test itself. | Add matrix by work type: docs, backend, UI, mobile, payment, deploy, data. |
| QA | Test real user/admin/parent/tutor/staff journeys. | `qa.md`, evidence model, test coverage docs, UI/UX QA edits. | Medium | Unit tests pass but real workflow is broken. | Add QA workflow by product surface and user role. |
| Review | Catch risk before commit, push, PR, deploy, or handoff. | `review.md`, natural-language PR review flow, UI/UX review edits. | Medium | Review misses design drift, E2E gaps, release comms, or state confusion. | Add review workflow variants: pre-commit, pre-push, PR, design, release. |
| Commit/Push/PR | Save work cleanly and sync it without overstepping. | `commit.md`, review gate, approval fixtures, guard scripts. | Deep for local commit/push; shallow for PR lifecycle. | Local-only work mistaken for pushed/merged; PR state is unclear. | Add repo-state fixtures and PR state workflow. |
| Release/Deploy | Move merged work to live, smoke it, monitor it, and close the loop. | Critical-lane rules, monitor-production-logs, state model. | Shallow | "Pushed" or "merged" is mistaken for live; deploy risk lacks a workflow. | Define release workflow: PR, merge, deploy, smoke, monitor, rollback, close. |
| Incident Workflow | Triage production problems, mitigate, communicate, fix, monitor, postmortem. | Critical lane, monitor-production-logs, evidence model. | Missing to shallow | Production issues are handled like normal bugfixes. | Create incident workflow and postmortem template. |
| Multi-Agent Workflow | Decide when Codex, Claude, subagents, or humans should do each role. | switching docs, handoff, snapshot, save-session, templates. | Medium | Handoffs lose context or duplicate work. | Define Codex-Claude-human collaboration map by workflow. |
| State Management | Track local, pushed, PR open, merged, deployed, live smoke passed. | `agent-os-state-model.md`, state fixtures, session ledger, mission ledger. | Medium | "Done" means different things in different tools. | Add repo-state fixtures and source-of-truth ownership examples. |
| Project Adoption | Apply Agent OS to each product repo without breaking local conventions. | install guide, install manifest, project `AGENTS.md`, active task docs. | Shallow | Umbrella rules exist but product teams do not follow them consistently. | Audit each product: sifu-tutor, ripple-suite, tutor app, parent app, LLS. |
| Staff Rollout | Let staff use the OS safely with limited capability. | staff quick start, rollout readiness, install docs. | Shallow to medium | Staff get too much access or too much process and stop using it. | Create staff pilot plan, roles, permission profiles, training checklist. |
| Governance | Decide how Agent OS itself changes over time. | review roadmap, mission ledger, commits, Koda. | Shallow | Rules are changed in many chats/files without versioning or review. | Add Agent OS change-control workflow and changelog/versioning standard. |
| Evaluation Harness | Prove Agent OS behavior with repeatable checks. | eval runner, response/state/Koda/capability/conversation fixtures, health. | Deep for local fixtures; medium for real-world traces. | Docs say one thing but hooks/agents behave differently. | Add repo-state fixtures, richer response fixtures, and eventually trace-based evals. |

## Workflow Map Added

The main missing artifact was not another fixture runner. It was the actual
workflow architecture.

Created:

```text
docs/agent-playbooks/agent-os-workflows.md
```

It defines these workflows:

1. Idea and discussion workflow.
2. Work intake workflow.
3. Product design workflow.
4. Bugfix workflow.
5. Feature workflow.
6. Staff issue workflow.
7. Critical-lane workflow.
8. Implementation workflow.
9. Verification workflow.
10. QA workflow.
11. Review workflow.
12. Commit/push/PR workflow.
13. Release/deploy/monitor workflow.
14. Incident workflow.
15. Memory/save-session/handoff workflow.
16. Mission-ledger workflow.
17. Staff rollout workflow.

Each workflow should answer:

```text
When it starts
Who owns decisions
What tools/state systems are used
What evidence is required
What approval is required
When it exits
What should be saved to Koda/docs/GitHub/Plane/Planner/mission ledger
What can go wrong
```

Next improvement: review each workflow one by one with Hafiz and add scenario
examples where a real Sifututor task needs clearer behavior.

## Recommended Review Order

Do not continue randomly. Review in this order:

1. **Workflow Architecture**
   - Created the master `agent-os-workflows.md`.
   - Next: review the workflows one by one and add examples from real
     Sifututor tasks where needed.

2. **Work Intake**
   - Define how Hafiz chat, Planner, Plane, GitHub, staff reports, production
     signals, Koda, and mission ledger become work.

3. **Product Design And Build Prompt Quality**
   - Decide when PRD, clarifier, UX spec, backend contract, and build prompts
     are required.

4. **Bugfix And Feature Workflows**
   - Map diagnosis, implementation, tests, QA, review, commit, and close loop.

5. **SIMS UI/UX Workflow**
   - Integrate the new UI/UX pre-read, verify, QA, and review changes.

6. **Release / Deploy / Incident Workflow**
   - Define PR, merge, deploy, smoke, monitor, rollback, and postmortem.

7. **Project Adoption**
   - Audit product repos one by one.

8. **Staff Rollout Pilot**
   - Create staff-safe pilot plan only after internal workflows are stable.

9. **Governance And Versioning**
   - Decide how Agent OS changes are proposed, reviewed, committed, and
     announced.

## Current Recommendation

Next best architectural step after this audit is merged:

```text
Review work intake in detail.
```

Suggested artifact:

```text
Update docs/agent-playbooks/agent-os-workflows.md and task-router.md only where
the intake rules need more detail.
```

This should happen before adding more local fixture runners unless a fixture is
needed to lock in a workflow decision we just reviewed.
