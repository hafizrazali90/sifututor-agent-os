# Task Router Playbook

Use this when starting a non-trivial task or when the user asks to route,
classify, resume, or create work.

## Start

1. Identify the active project from cwd and user prompt.
2. Read the project `AGENTS.md`; if absent, read project `CLAUDE.md`.
3. Search Koda memory for the task topic when available.
4. Check workflow state before editing.
5. If the session is resuming after a long pause, compact, branch switch,
   remote reconciliation, or possible outside edits, run a quick reconciliation
   audit before continuing. For Agent OS discussion, keep it light: umbrella
   repo status, recent commits, Koda/health state, and relevant docs. For
   product work, audit only the selected repo before editing.
6. Use smart resume behavior when context signals matter: Hafiz says
   `continue`, `resume`, `go next`, `proceed`, `what next`, or similar; a
   recent active Session Map exists; local Git is ahead of GitHub; the chat
   resumed after compaction or a long pause; or the work is a multi-step Agent
   OS/workflow/product task. Read the latest relevant Session Map Reference
   Pack before broad exploration. If it matches the prompt, summarize the main
   goal, current focus, waiting items, Git state, and recommended next action.
   If it does not match, say it looks unrelated and treat the prompt as new
   unless Hafiz wants to resume it.
7. If the project has `TESTING.md` and the task may change user-facing
   behavior, read it and identify the affected feature row before
   implementation. Use [test-coverage.md](test-coverage.md).
8. If the active project is `sifu-tutor` and the task touches SIMS browser UI,
   UX design, page layout, React/Inertia components, staff-facing copy, or
   visual QA, read `sifu-tutor/docs/ui-ux/README.md` before routing the build or
   review. Then read the relevant files it points to plus the nearest
   `sifu-tutor/docs/features/<feature>/` docs.
   If the prompt asks for a visual audit, screenshot review, design-system
   consistency check, or whether the page looks right, route the evidence step
   through [sims-ui-audit.md](sims-ui-audit.md).
9. If the user is brainstorming, redesigning, asking for a PRD/UX spec/build
   prompts, or describing a new cross-module workflow, route to
   [product-design.md](product-design.md) before implementation. Use it only
   when the design risk is real; small fixes stay on the normal route.
   For SIMS module redesigns or module-wide UI/UX transformation work, always
   treat the first phase as discussion-first product design. Do not start
   coding because Hafiz says "proceed" unless the current discussion already
   produced the module scope, user/system flow decisions, screen inventory,
   state coverage, evidence plan, and explicit implementation approval.
10. For critical-lane work, cross-module workflows, or any task being handed
    from one AI/human developer to another, apply
    [ai-implementation-readiness.md](ai-implementation-readiness.md) before
    coding. If the plan/build prompt is missing real entry points, contract
    moments, retry/idempotency, realistic payloads, or exact evidence, close the
    documentation gap first.
11. For SIMS, tutor app, parent app, support-ticket, TREQ/TUT, or
   staff-reported operational issues, check Microsoft Teams Planner
   `Development & Support > Task Management Board` as intake/context before
   deciding scope. Treat Planner as staff-reported issue context, not the
   engineering source of truth. Do not modify Planner unless Hafiz explicitly
   asks in the current session.
12. Do not check or create Plane cards by default. If mission-level context is
   needed, use the Mission Ledger or the project active task state. Use Plane
   only when Hafiz explicitly asks in the current session.
13. If the prompt sounds like a follow-up, adjacent task, paused question, or
    part of a bigger goal, check the Mission Ledger before treating it as an
    isolated task. Use [mission-ledger.md](mission-ledger.md), but search first
    and read only the relevant project section.

## Native Workspace Understanding

Starting work in the native Agent OS workspace must still feel like opening a
normal chat. Do not put a project/workflow form in front of Hafiz.

After identifying the active project and workflow, and before delegating or
starting significant implementation, make the route visible when the current
chat exposes Omnigent's task-scoped coordinates:

```bash
agent-os-set-understanding \
  --project <project> \
  --workflow <workflow> \
  --finish-line "<practical outcome>"
```

Initialize the separate current-proof display honestly before implementation:

```bash
agent-os-set-proven-state \
  --state "Routed; implementation not started" \
  --evidence "Task Router completed; no implementation evidence exists yet"
```

Use the project name already selected by this playbook, such as
`sifu-tutor`, `ripple-suite`, or `umbrella`. Use the route name already selected
by the routing model, such as `bugfix`, `review`, `feature`, or
`workflow-improvement`. Do not invent a second classifier just for the UI.
Use the practical finish state already selected by the Execution Depth rules
below, written as a short outcome such as `Local fix verified`, `PR opened`,
`Staging verified`, or `Production monitored`. Do not turn it into a checklist
or a promise to cross an unapproved boundary.

If the request is materially ambiguous, keep the conservative route visible
and include exactly one short question:

```bash
agent-os-set-understanding \
  --project umbrella \
  --workflow triage \
  --finish-line "Route confirmed" \
  --question "Which product should this change?"
```

Ask the same practical question in the conversation and wait only when the
answer could change scope, risk, product meaning, or approval. Do not mark an
ordinary low-impact uncertainty as blocked.

The helper takes no session-id argument and changes only the current chat's
bounded `agent_os.*` understanding labels. The Worker Sidebar is a visible
reflection of this router decision, not a new task database. Hafiz may correct
the project, workflow, or finish line there; that correction is saved to the
same task and sent into the same orchestrator conversation. Treat the
correction as fresh user evidence. The finish line records the agreed practical
outcome; it does not grant approval for push, PR, merge, deploy, production,
critical-lane, or destructive actions.

If the helper or native coordinates are unavailable, continue with the normal
task-router report and say the visible native summary was not updated. Never
claim it was set when the command did not run.

The finish line is the target. Current proof is a separate evidence-backed
state and must be updated at meaningful boundaries through the State Model
rules. Never use the finish-line text itself as evidence that the task reached
that outcome.

## Intent Routing Model

Use [agent-os-routing-model.md](agent-os-routing-model.md) for Agent OS prompt
classification rules.

Use [agent-os-workflow-lanes.md](agent-os-workflow-lanes.md) to choose the
right intensity: Light, Medium, Full, or Critical.
Also use its Execution Depth section to choose the practical finish state:
answer only, drafted, changed locally, local proof, committed, PR ready, merged,
deployed, live checked, monitored, or accepted/closed. Plain meaning: after the
route is known, the router should recommend how far this task should go before
it stops.

Use [doc-routing-and-context-loading.md](doc-routing-and-context-loading.md)
after choosing the route to decide which docs are mandatory, which are triggered
by the task, and which should be skipped for now. Plain meaning: Task Router
should not make the agent read everything. It should make the agent read the
right source-of-truth docs for the current job.

Use [doc-owner-route-index.md](doc-owner-route-index.md) when a doc owner is
unclear or the agent might add a new doc. Use
[skill-quality-and-pruning.md](skill-quality-and-pruning.md) before creating,
splitting, merging, parking, or deleting workflow skills/playbooks. Plain
meaning: first find the owner; then decide whether the Agent OS needs a new
artifact at all.

Use [agent-os-runtime-reliability.md](agent-os-runtime-reliability.md) after
choosing the route to keep the active mode, loaded context, proof/state, and
next action visible. Plain meaning: the router should not only pick the route;
it should help the agent stay in the right gear while working.

Use [planning-artifacts.md](planning-artifacts.md) when the task needs
brainstorming, option comparison, Product Shape, Build-Ready Pack, a visual
review board, or a clear explanation before implementation. Plain meaning: do
not jump from vague agreement into code. Choose the smallest useful planning
artifact, explain why it is enough, and stop before coding when Hafiz still
needs to decide product direction, risk, scope, or acceptance.

Use [agent-os-state-model.md](agent-os-state-model.md) when deciding where the
current task, issue, mission status, evidence, and release state should be
recorded.
Use [context-authority.md](context-authority.md) when sources disagree. Plain
meaning: if Koda, chat, Session Map, GitHub, Git, deploy state, QA evidence,
Planner, docs, or Hafiz's current instruction do not line up, the router should
name the question, choose the source that owns that question, check current
evidence, and stop only when the conflict changes scope, risk, product meaning,
or approval.

Use [agent-os-capability-model.md](agent-os-capability-model.md) when deciding
what tools the agent should use for current evidence. Plain meaning: after the
route is clear, the agent should choose the narrowest safe tool path itself for
ordinary read-only checks instead of asking Hafiz to name the tool. Ask only
when the tool choice changes product direction, crosses an approval gate,
requires unavailable/broad access, or the target project/account/environment is
unclear.

Use the State Ownership Rule in
[agent-os-state-model.md](agent-os-state-model.md) before trusting or updating
task state. Plain meaning: Planner is staff intake, GitHub is engineering
execution, Koda is durable memory, Session Map is current-session story, Git is
exact changed files, deploy records prove deployed code, and QA evidence proves
real behavior.
If two sources disagree, route through the Conflict Handling Routine in
[context-authority.md](context-authority.md) before editing or reporting a
stronger state.

Use the Routing New Information section in
[agent-os-state-model.md](agent-os-state-model.md) before storing a new idea,
correction, issue, or follow-up. Plain meaning: do not put everything in Koda,
Mission Ledger, Session Map, and GitHub at the same time. Route it by purpose:
current-session continuity to Session Map, durable behavior lessons to Koda,
future goals/follow-ups to Mission Ledger, execution-ready engineering work to
GitHub, and exact changed files to Git commits.

Use [session-map.md](session-map.md) when the current conversation has a main
goal plus side paths, multiple sub-goals, unclear return path, enough moving
parts that Hafiz or the next agent could lose the story, or non-trivial
development/workflow work that may move through diagnosis, implementation,
verification, QA, commit, push, PR, deploy, handoff, or save-session. Skip it
only for tiny one-shot work.

Use [agent-os-improvement-loop.md](agent-os-improvement-loop.md) when Hafiz asks
to improve the workflow, fix Agent OS behavior, make future agents handle
something better, resolve Claude/Codex workflow drift, or clean up docs, skills,
hooks, evals, Koda, and Session Map consistency. Plain meaning: do not patch one
file and call the Agent OS fixed when the behavior depends on several layers.

Use [no-mistakes-lite.md](no-mistakes-lite.md) before saying work is ready,
done, safe, merge-ready, deploy-ready, or live, and before commit, push, PR,
merge, deploy, release close-out, save-session, or handoff after meaningful
work. Plain meaning: one final honesty pass should confirm scope, proof,
missing evidence, real state, approval boundary, and recommended next action.

Use [parallel-work-and-worktrees.md](parallel-work-and-worktrees.md) when
multiple agents, sessions, branches, PRs, fixes, or long-running tasks may be
active at the same time. Plain meaning: if two active code tasks may edit the
same repo, isolate them in separate worktrees or clearly record why the current
workspace is safe.

Use [autonomous-work-packets.md](autonomous-work-packets.md) when Hafiz asks the
agent to autopilot, keep going, proceed until done, clean up a whole batch, or
work for a longer stretch without micro-approval. Plain meaning: approval gates
define how far the agent may go; autonomous work packets define how the agent
loops safely while going there.

Use [mission-ledger.md](mission-ledger.md) when the prompt belongs to a bigger
goal or should be captured for later but is not ready for GitHub yet.
To keep routing lightweight, use `rg` against `docs/agent-playbooks/mission-ledger`
and open only the relevant matching section.

Use the Work Intake And Task State Rules in
[agent-os-state-model.md](agent-os-state-model.md) before creating GitHub
issues or starting real coding work. Plain meaning: quick-diagnose the signal,
then choose the lightest useful home. Do not create issues from vague symptoms
too early, and do not start execution-ready coding with no trace.
When the signal comes from Hafiz chat, Planner/staff, GitHub, Koda, production
monitoring, another session, or an agent-discovered issue, use the Intake
Scenario Matrix in that same file to avoid restarting the discussion or routing
the work into the wrong home.

First-mate routing belongs here. Plain meaning: Task Router is the front desk
of the Agent OS. It should translate Hafiz's natural-language request into the
current workflow stage, practical finish point, best worker/tool, evidence
need, approval stop point, and next recommended action before the agent gets
deep into work. Do not create a separate first-mate agent yet; use
[agent-os-routing-model.md](agent-os-routing-model.md) as the source of truth.
Use [agent-os-workflow-lanes.md](agent-os-workflow-lanes.md) when the practical
finish point is unclear. Plain meaning: Hafiz should not need to remember
whether the next stop is local proof, commit, PR ready, merged, deployed, live
checked, or monitored. The router should recommend that stop point.

Important routing principles:

- Do not route by keyword alone.
- Discussion, learning, architecture review, and retrospectives should stay
  light unless Hafiz asks to document or implement.
- Workflow-improvement prompts should route to the Agent OS Improvement Loop,
  not to ordinary product implementation or Koda-only memory saving.
- Task Router owns first-mate routing for now. It should answer: what Hafiz is
  trying to achieve, what workflow stage applies, what done means, which
  worker/tool fits, what proof is needed, where to stop, and what to recommend
  next.
- When a session becomes hard to follow, or when real work starts moving through
  multiple states, start or update the Session Map before continuing deeper.
- `proceed` means act on the last clear recommended step.
- `approve` means execute the last exact approval request, including a safe
  bundle if the agent clearly asked for that bundle.
- Push, deploy, merge, PR, critical-lane, destructive, secret, and production
  actions still need their stricter gates.

## State-File Projects

Applies to `ripple-suite`, `sifu-tutor`, `sifututor_tutor`, and
`sifututor_parent`.

1. Read `.claude/tasks/active.json`.
2. If `activeTask` is set, read the referenced `taskFile`.
3. Compare the active task to GitHub, Mission Ledger, or current chat context
   when relevant.
4. Resume the active task unless the user explicitly starts a new task.
5. Report the current route and next unblocked step before editing.
6. At the end of each completed step, state the recommended next unblocked
   action so Hafiz does not have to ask what should happen next.

## Multiple-Fix Sessions

If a chat/session contains more than one bug, fix, branch, PR, or deploy
candidate, start or update the Session Release Ledger before continuing. Use
[session-release-ledger.md](session-release-ledger.md).

This is mandatory when:

- A second staff-reported issue enters the same chat.
- The session switches from one bug to another before the first is live.
- A fix is rebuilt on a cleaner branch after first being committed elsewhere.
- Hafiz asks whether all fixes from the session are live.
- Hafiz asks to commit, merge, push, PR, release, or deploy after multiple
  fixes were discussed.

Before switching tasks, say whether each current fix is `local only`, `pushed`,
`PR open`, `merged`, `deployed`, or `smoke passed`.

Common route shapes:

| Route | Use for | Core path |
| --- | --- | --- |
| `feature` | New user-facing behavior | plan -> build -> generate_tests -> e2e_regression -> qa_full -> verify -> review -> commit |
| `bugfix` | Non-emergency defect | describe -> diagnose -> related_impact_audit -> fix -> regression_test -> e2e_regression -> verify -> qa -> review -> commit |
| `hotfix` | Production or staging breakage | describe -> diagnose -> related_impact_audit -> fix -> regression_test -> e2e_regression -> verify -> qa -> review -> commit |
| `small-change` | Copy, label, config, minor UI | describe -> fix -> e2e_regression_if_user_facing -> verify -> qa -> commit |
| `refactor` | Structure change without behavior change | analyze -> plan -> refactor -> verify -> qa -> review -> commit |
| `docs` | Documentation only | write -> verify -> commit |
| `product-design` | PRD, UX spec, build prompts, major workflow design | design_brief -> prd -> clarifier_if_needed -> ux_spec -> backend_contract_if_needed -> build_prompts -> implementation_handoff |

## Lane Intensity

| Intensity | Use For | Practical Behavior |
| --- | --- | --- |
| Light | discussion, learning, architecture thinking | Explain, recommend, avoid edit/verify/commit ceremony. |
| Medium | docs, Agent OS, tooling, small safe work | Update scoped files, run non-destructive checks, stop before commit/push approval. |
| Full | product code, user-facing work, behavior changes | Implement with verify, QA, review, E2E/release decisions when relevant. |
| Critical | auth, payment, invoice, commission, migration, deploy, mobile API contract | Read-only diagnosis first, then implementation approval. |

Do not force every prompt through the full product path. Escalate only when
risk, behavior change, or critical domains require it.

## E2E Regression Step

For `feature`, `bugfix`, `hotfix`, and user-facing `small-change` routes, the
agent must make an explicit permanent E2E decision before reporting the work as
ready:

- `added`: name the `tests/e2e/...` file, stable fixture/seed used, and focused
  Playwright command that passed.
- `updated`: name the existing spec and command that passed.
- `not feasible`: give the exact blocker (`missing credential`, `no safe
  representative data`, `destructive workflow`, `tooling unavailable`, or
  `not user-facing`) and the follow-up fixture/test needed.

If the change fixes a browser-visible staff/parent/tutor/admin issue, default
to adding or updating Playwright E2E. Unit, Pest, feature, or API tests do not
satisfy the E2E regression step by themselves.

The default is stronger for real workflows: every staff/admin/parent/tutor/
student/customer function that can be performed in the product must have a
permanent E2E regression path so the team can run full E2E periodically and
catch regressions. This applies to new user stories and features as much as to
bug fixes. Do not treat backend tests, route smoke, production smoke, or manual
verification as a substitute when the workflow can be automated safely.

Before push, PR, merge, or deploy, report the permanent E2E file covering each
changed user workflow. If one is missing, the route is not ready; add the E2E
or record an explicit exception with the blocker and follow-up fixture/test.

## Related Impact Audit Step

For `bugfix`, `hotfix`, and user-facing `small-change` routes, use
[related-impact-audit.md](related-impact-audit.md).

Default:

- every bugfix gets a local related check
- reusable root causes get a same-pattern sweep
- critical lanes get a critical impact audit

The related-impact audit does not automatically expand implementation scope.
Fix clearly in-scope related issues; ask Hafiz or track follow-up work when the
related finding changes business behavior, crosses modules/apps, touches a
critical lane, or becomes a redesign.

## Staff Issue Intake

Use Microsoft Teams Planner `Development & Support > Task Management Board`
when the task starts from or may relate to internal staff reports about:

- SIMS production behavior in `sifu-tutor`
- tutor app behavior in `sifututor_tutor`
- parent app behavior in `sifututor_parent`
- support tickets, TREQ/TUT references, app reports, operational bugs, or staff
  complaints about what is happening in SIMS or either app

Planner cards provide the human-reported symptom and support context. For
outside intake, do a quick read-only diagnosis before creating engineering
noise: understand the symptom, identify the affected user or role, locate the
likely project/module, check whether it looks like real engineering work, and
gather one or two pieces of non-destructive evidence. Stop before code edits,
data mutation, commit, deploy, destructive action, or broad investigation.
Convert confirmed or likely engineering work into the normal Sifututor
workflow: create or link a GitHub issue for coding work, capture bigger or
future follow-ups in the Mission Ledger, read/update project active task state
where applicable, and run the normal verify/QA/review path. Keep Planner
read-only unless Hafiz explicitly asks for a Planner update.

If there is no active task file, do not invent one unless the user asks to start
a routed task. For simple tasks, state that no active task exists and proceed
under `AGENTS.md`.

## LLS Migration Note

`lls` previously used Superpowers docs instead of the standard Sifututor
`.claude/tasks/active.json` workflow. That was workflow drift, not the desired
long-term architecture. The state-file foundation now exists; continue aligning
LLS skills and hooks with the shared route/state model.

For LLS tasks:

1. Read `lls/CLAUDE.md` for current technical rules.
2. Read `lls/.claude/tasks/active.json`.
3. Route work using the same route names as the other active projects.
4. Do not teach future agents that Superpowers-only is the target state.

Target migration:

- continue improving `lls-task-router` route file creation
- update `lls-verify`, `lls-qa`, `lls-commit`, and `lls-save-session` to read
  and update active task state consistently
- keep relevant Superpowers specs only as planning/reference input

## Critical Lanes

For auth, payments, invoices, commissions, migrations, mobile API contracts, or
deployment work:

1. Phase A: read-only diagnosis and recommendation.
2. Wait for explicit approval.
3. Phase B: implementation.

Do not collapse these phases unless the user explicitly authorizes emergency
hotfix risk.

## SIMS Module Redesign Guard

Use this guard for module-wide SIMS UI/UX work such as Tutor Requests, Parent
Invoices, Classes, Student Reports, payments, finance, dashboards, and shell
navigation.

The learned Tutor Requests and SIMS Shell workflow is:

1. Diagnose first: read code, docs, current staging/local UI, current branch,
   `origin/integration`, and relevant Koda memories.
2. Inventory the whole module: list pages, subpages, modals, drawers, popovers,
   buttons/actions, copy, fields, empty/loading/error states, desktop/mobile
   layouts, permissions, and downstream side effects.
3. Discuss decisions one by one with Hafiz. For each decision, explain the
   current behavior, the problem, options, recommendation, why, and tradeoff.
4. Record confirmed decisions before moving on. Do not silently reinterpret an
   earlier choice when later work becomes complex.
5. Produce or update the PRD/UX spec/backend contract/build prompts only after
   the discussion direction is clear.
6. Implement in safe slices only after approval, especially for critical lanes.
7. Capture browser screenshots and a consistent HTML review board after each
   visible slice; update it whenever screenshots change.
8. Verify the real changed workflow on staging after deploy, not only route
   availability or local screenshots.
9. Update reusable docs when a mistake reveals a missing rule, such as spacing,
   copy style, action labels, mobile responsiveness, menu behavior, or review
   board format.

If Hafiz asks "are we brainstorming?", "why are we coding?", or similar, stop
and return to this guard instead of continuing implementation.
