# Product Design Playbook

Use this for design-first work before implementation: new modules, major
workflow redesigns, cross-module behavior, PRDs, UX specs, build prompts, or
ambiguous product decisions.

The goal is Claude/Codex parity without extra noise. Claude has separate skills
for `/lite-prd`, `/prd-clarifier`, `/prd-to-ux`, and `/ux-to-prompts`; Codex
uses this shared playbook to follow the same end-to-end shape.

## When To Use

Use this playbook when any of these are true:

- Hafiz asks to brainstorm, redesign, create a PRD, create a UX spec, or create
  build prompts.
- The work is a new module, a major workflow redesign, or touches 3+ screens.
- The work changes business rules across modules, departments, roles, payments,
  invoices, class scheduling, commissions, auth, mobile API contracts, or
  production operations.
- Requirements are still being decided and implementation would create rework.

Do not use this playbook for ordinary bug fixes, small copy changes, narrow UI
adjustments, test-only work, or one-file implementation tasks. Those stay on
the normal task-router, diagnose, verify, QA, review, and commit path.

## Noise-Control Rules

This workflow should remove ambiguity, not create ceremony.

- Ask only questions that change a requirement, risk, implementation boundary,
  UX flow, RBAC rule, data contract, or acceptance test.
- Prefer reading code/docs/data over asking Hafiz when the answer is discoverable.
- Ask one decision at a time when the topic is complex.
- For every decision or clarifier question, give 2-4 options, mark the
  recommended option, explain why it is recommended, and name the key tradeoff
  or risk. Do this even when Hafiz asks "what do you suggest?" so he can compare
  the choices instead of receiving only one answer.
- Mark confirmed decisions as confirmed before moving to the next decision.
- Do not repeat already-confirmed decisions unless a later answer conflicts.
- Keep "out of scope" explicit so build prompts do not grow quietly.
- For critical lanes, stop at PRD/UX/build-plan unless Hafiz approves
  implementation separately.

## SIMS Module Redesign Loop

For SIMS module redesigns or module-wide UI/UX transformations, follow the
Tutor Requests / SIMS Shell loop before implementation. This applies especially
to Parent Invoices, Classes, Student Reports, payments, finance, dashboard, and
navigation work.

1. **Diagnose the real system first.** Read code, routes, controllers, services,
   UI docs, feature docs, relevant tests, current branch behavior, staging or
   local screenshots when available, Koda memories, and `origin/integration`.
2. **Map the end-to-end surface.** Include list pages, detail pages, forms,
   wizards, modals, drawers, popovers, row actions, destructive actions,
   exports, PDFs, notifications/copy, permissions, mobile/narrow layouts,
   loading/empty/error/disabled states, and downstream side effects.
3. **Discuss one decision at a time.** Each decision must include:

```text
Current behavior:
Problem / opportunity:
Options:
Recommendation:
Why:
Tradeoff / risk:
Decision needed:
```

4. **Record confirmed decisions.** Do not move to build prompts until the major
   module choices are confirmed or explicitly deferred.
5. **Create artifacts only after direction is clear.** Use the smallest safe
   set, but for high-risk modules prefer PRD, UX spec, backend contract, and
   build prompts.
6. **Implementation is a separate approval.** Critical lanes like invoices,
   payments, commissions, migrations, deployment, auth, and mobile API
   contracts must stay in Phase A diagnosis/design until Hafiz approves Phase B.
7. **Evidence must be reviewable.** For visible UI work, plan screenshots and a
   consistent HTML review board before calling a slice complete. The review
   board format should stay stable across modules unless Hafiz approves a new
   template.
8. **Turn mistakes into reusable rules.** If review catches repeated issues
   such as spacing, color, action labels, copy capitalization, menu behavior,
   overlap, responsive layout, or staging/local mismatch, update the relevant
   `docs/ui-ux/` or Agent OS workflow doc in the same cycle.

Practical trigger: if Hafiz asks to "repeat the Tutor Requests process", "learn
from the mistake", "brainstorm first", "diagnose all", or "ask one by one",
start here and do not implement until the discussion and approval gates are
clear.

## Accuracy Rules

Before producing artifacts:

1. Read the nearest `AGENTS.md`.
2. Read the target project `AGENTS.md` and `CLAUDE.md` when a project is known.
3. Search Koda for prior product, workflow, and business-rule decisions.
4. Search existing docs under `docs/`, `.claude/plans/`, and project feature
   docs for overlapping PRDs, UX specs, or build prompts.
5. Read relevant source files when the design changes existing behavior.
6. For SIMS browser UI/UX work, compare the current branch with
   `origin/integration` before finalizing the audit, UX spec, or build prompts.
   Prefer the exact same page/component path. If it does not exist there, use
   the nearest module or page-pattern equivalent and document the fallback.
7. For SIMS browser UI/UX work, treat the tracked `docs/ui-ux/` design system
   as the color/token authority. If implementation, `tailwind.config.js`, or
   integration-branch behavior conflicts with the docs, stop and document the
   conflict before choosing colors.
8. For SIMS, tutor app, parent app, support-ticket, TREQ/TUT, or staff-reported
   operational work, read the relevant Microsoft Teams Planner card as intake
   context when available.
9. Check the Mission Ledger and relevant GitHub issues for related context
   before creating major new work. Use Plane only if Hafiz explicitly asks in
   the current session.

If the current design conflicts with `AGENTS.md`, `CLAUDE.md`, Koda, existing
docs, or production facts, stop and explain the conflict before writing a spec.

## Output Locations

Use project-local docs when a project is known.

For `sifu-tutor`, prefer:

```text
sifu-tutor/docs/features/<feature-slug>/prd.md
sifu-tutor/docs/features/<feature-slug>/prd-clarification-session.md
sifu-tutor/docs/features/<feature-slug>/ux-spec.md
sifu-tutor/docs/features/<feature-slug>/build-prompts.md
sifu-tutor/docs/features/<feature-slug>/user-stories.md
```

For SIMS browser UI/UX work, also read and reference:

```text
sifu-tutor/docs/ui-ux/README.md
sifu-tutor/docs/ui-ux/surface-map.md
sifu-tutor/docs/ui-ux/design-system.md
sifu-tutor/docs/ui-ux/page-patterns.md
sifu-tutor/docs/ui-ux/component-patterns.md
sifu-tutor/docs/ui-ux/content-style-guide.md
sifu-tutor/docs/ui-ux/accessibility-and-states.md
sifu-tutor/docs/ui-ux/review-and-qa-checklist.md
sifu-tutor/docs/ui-ux/quality-gate.md
```

Use `sifu-tutor/docs/ui-ux/templates/ux-spec-template.md` for new SIMS UX
specs unless a closer module template already exists.

If the project already uses a different nearby feature-doc pattern, follow the
existing project pattern. For early brainstorming only, `.claude/plans/` may be
used as a temporary design note, but confirmed product requirements should move
to project docs before build prompts.

## Phase 1: Design Brief

Use this when the idea is still fuzzy or Hafiz wants to discuss before a PRD.

Required sections:

- Problem statement in plain language.
- Current-state evidence from code, docs, data, Planner, or Koda.
- Users and departments affected.
- Goals and non-goals.
- Options considered.
- Confirmed decisions log.
- Open questions.
- Recommendation.

For each key decision, use:

```text
Decision needed:
Options:
Recommendation:
Why:
Tradeoff / risk:
Edge cases:
```

Do not implement during this phase.

## Phase 2: PRD

Create a PRD when the feature or workflow direction is clear enough to write
requirements.

Required sections:

1. One-sentence problem.
2. Goal and success outcome.
3. Target users and departments.
4. Core happy path.
5. Functional requirements.
6. UX requirements and entry points.
7. Data and business logic.
8. RBAC and permissions.
9. Notifications and communication rules.
10. Audit/logging requirements.
11. Edge cases and exception handling.
12. Rollout, migration, or historical-data plan.
13. Success metrics.
14. Risks and mitigations.
15. User stories.

For Sifututor operational modules, include department ownership and daily
workflow sections when staff action is involved.

## Phase 3: Clarifier

Run a clarification pass when any important requirement remains ambiguous.

Use depth based on risk:

| Depth | Use when | Questions |
| --- | --- | --- |
| Quick | Mostly clear, a few acceptance gaps | 5 |
| Medium | Normal feature/module | 10 |
| Long | Cross-module or critical-lane behavior | 20 |
| Ultralong | Large program or high financial/regulatory risk | 35 |

Noise-control exception: if prior conversation already answered a question,
record the decision in the clarification file instead of asking again.

Each clarification entry should include:

```text
Question
Why it matters
Options
Recommendation
Tradeoff / risk
Answer
Requirement clarified
Artifact section updated
```

After the clarifier, update the PRD.

## Phase 4: UX Spec

Translate the PRD into a UX spec before visual/build prompts. Follow the same
six-pass structure as Claude's `/prd-to-ux`:

1. User intent and mental model.
2. Information architecture.
3. Affordances and action clarity.
4. Cognitive load and decision minimization.
5. State design and feedback.
6. Flow integrity check.

Only after these passes, describe:

- screens and tabs,
- tables, filters, dashboards, and detail views,
- actions and forms,
- empty/loading/error/partial states,
- permission-based visibility,
- links to existing pages,
- mobile/browser considerations when relevant.

For SIMS UI, read `sifu-tutor/docs/ui-ux/README.md`, the relevant docs it
points to, and nearby pages/components before specifying components. Name the
SIMS surface, page pattern, shared components, copy rules, state coverage, and
accessibility expectations in the UX spec. Avoid inventing new patterns when the
project has an existing one.

## Phase 5: Backend Contract

Required when the work touches controller actions, services, cron jobs,
invoices, payments, class scheduling, commissions, auth, mobile APIs, or data
repair.

Map each behavior to:

- entry point: route, controller, API endpoint, command, job, or service,
- data read and write targets,
- transaction/locking needs,
- business guards,
- side effects: notifications, logs, totals, status changes, cache, exports,
- rollback behavior,
- idempotency and duplicate-prevention rules,
- tests and E2E evidence.

This phase exists to avoid UI-forward specs that miss backend cascade effects.

## Phase 6: Build Prompts

Generate build-order prompts only after the PRD and UX/backend contract are
clear enough to build.

For critical-lane work, cross-module workflows, or any AI-to-AI/human handoff,
first apply [ai-implementation-readiness.md](ai-implementation-readiness.md).
The build prompt must be strong enough that another agent cannot satisfy a
weaker nearby behavior and still claim the slice is done.

Each prompt must be self-contained:

- plain-language purpose,
- SIMS UI/UX pre-read files when the prompt touches browser UI,
- pre-read files,
- requirements,
- states,
- interactions,
- backend contract slice,
- files to create/modify,
- tests and focused verification,
- E2E regression decision for user-facing behavior,
- dependencies and blockers,
- complexity score from 1-5.

Use this build order unless the feature needs a different dependency graph:

1. Foundation: migrations/models/enums/settings/permissions.
2. Backend contract: services, commands, jobs, detectors, APIs.
3. UI shell: routes/pages/navigation.
4. Core views: dashboard, tables, detail pages.
5. Actions: forms, status updates, assignments, notes.
6. Notifications/logging/audit timeline.
7. Tests, E2E, QA, monitoring, and rollout.

Include a build sequence table and identify which prompts can run in parallel.
Do not generate parallel rounds that modify the same files.

## Phase 7: Implementation Handoff

Before coding starts:

- Confirm or create the required GitHub issue according to the target project's
  `AGENTS.md`.
- Capture bigger/future follow-ups in the Mission Ledger when they are not
  ready for GitHub or implementation.
- Create or update `.claude/tasks/active.json` only when the project workflow
  expects a routed task.
- For critical lanes, ask for explicit Phase B approval.
- State the next build prompt and the verification plan.

## Minimum Artifact Decision

Use the smallest artifact set that safely fits the work:

| Work type | Required artifact |
| --- | --- |
| Tiny copy/config | no PRD; normal task route |
| Narrow bugfix | diagnosis + regression test decision |
| Small user-facing change | mini design note + user stories if useful |
| New page or module | PRD + UX spec + build prompts |
| Cross-module business workflow | PRD + clarifier + UX spec + backend contract + build prompts |
| Critical-lane workflow | same as cross-module, plus Phase A/Phase B approval |

## Close-Out

After product-design work, report:

```text
Status:
Meaning:
Artifacts created or updated:
Confirmed decisions:
Open questions:
Checked:
Recommended next:
Decision needed:
```
