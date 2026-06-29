# Agent OS Workflows

Status: draft for internal Sifututor Agent OS use.

Use this as the master workflow map. It connects the separate Agent OS
playbooks into the day-to-day paths Hafiz, Codex, Claude, Koda, GitHub,
Planner, Mission Ledger, and project tools should follow.

Plain meaning: this file tells the agent what journey it is in, what proof is
needed, what Hafiz owns, and where the result should be saved.

## Best-Practice Baseline

Use workflows as controlled paths, not as heavy ceremony.

Research-backed agent systems such as LangGraph, LangChain human-in-the-loop,
OpenAI Agents SDK, Microsoft Agent Framework, AutoGen, and CrewAI Flows all
point to the same broad lesson: reliable agents need orchestration, state,
approval points, observability, and tool policy. The model can reason inside a
step, but the workflow should decide the shape of the journey.

Sifututor's workflow baseline:

```text
intake -> route -> prepare context -> act in safe slice -> verify evidence
-> review risk -> approval boundary -> save state -> next recommended action
```

Plain meaning:

```text
Understand the job, choose the right path, prepare properly, do one safe chunk,
prove it works, check risk, ask approval only where it matters, then leave a
clear trail for the next session.
```

Do not build the Sifututor Agent OS around one agent framework yet. Keep the
portable layer in Markdown, scripts, hooks, skills, Koda, GitHub, Planner,
Mission Ledger, and project docs. Add a framework runtime later only when a
specific workflow needs durable execution beyond what the local tools provide.

## Related Playbooks

Read only the playbooks that match the current route:

- [task-router.md](task-router.md) for classifying the request.
- [agent-os-workflow-lanes.md](agent-os-workflow-lanes.md) for process
  intensity.
- [agent-os-approval-gates.md](agent-os-approval-gates.md) for approval
  boundaries.
- [context-authority.md](context-authority.md) for deciding what source is true
  enough to act on.
- [agent-os-evidence-model.md](agent-os-evidence-model.md) for proof strength.
- [product-design.md](product-design.md) for PRD, UX, backend contract, and
  build prompts.
- [diagnose.md](diagnose.md), [verify.md](verify.md), [qa.md](qa.md), and
  [review.md](review.md) for build evidence and risk checks.
- [commit.md](commit.md) for local commits.
- [monitor-production-logs.md](monitor-production-logs.md) for read-only
  production monitoring.
- [mission-ledger.md](mission-ledger.md) for paused or future work.
- [save-session.md](save-session.md) for durable close-out.

## Shared Workflow Contract

Every workflow should answer these questions before it is called done:

| Question | Plain meaning |
| --- | --- |
| When does it start? | What kind of user request or repo state triggered it? |
| Who owns decisions? | What can the agent decide, and what must Hafiz decide? |
| What tools/state systems are used? | Chat, docs, GitHub, Planner, Koda, Mission Ledger, tests, browser, server, or logs. |
| What evidence is required? | What proof shows the work is real and not just described? |
| What approval is required? | What boundary needs explicit Hafiz approval? |
| What does done mean? | Should this task end at diagnosis, local fix, commit, PR, staging, production, or monitored live state? |
| When does it exit? | What state means the workflow is finished or ready for the next workflow? |
| What should be saved? | What goes to docs, Koda, GitHub, Planner, Mission Ledger, or final reply? |
| What can go wrong? | The common failure mode the agent must watch for. |

## Universal Rules

- Use the lightest lane that honestly fits the risk.
- Explain in plain language first, then give technical detail.
- Prefer checking the real source over asking Hafiz when the answer is
  discoverable.
- Keep living drafts updated during architecture and workflow discussions.
- For meaningful work, explain what done means before asking how far to
  continue. "Fixed" can mean diagnosed only, fixed locally, committed, PR
  opened, staging verified, production live, or production monitored.
- Recommend the stop point and suggested path. Hafiz should not need to remember
  or list the workflow steps; the agent should suggest the route and explain why
  that route fits the task.
- Treat natural end-to-end phrases by intent, not exact wording. "Proceed until
  done", "continue until done", "do everything needed", and "finish this end to
  end" all mean the agent should explain what done means, say how far it can go
  now, name what approval is needed to go further, and then continue until the
  approved stop point or a hard gate.
- Check the current task context before pausing. If the scope, path, approvals,
  and stop point were already clearly agreed, continue through that approved
  path. Pause only if new scope, risk, evidence, access failure, or an
  unapproved boundary appears.
- Say "I will only pause if..." before meaningful execution. Pause reasons
  should be specific to the task, such as new scope, contradictory evidence,
  unavailable access, product/business decision, unapproved production action,
  destructive action, or critical-lane risk.
- Use the Proof Standard from
  [agent-os-evidence-model.md](agent-os-evidence-model.md): code proof proves
  the parts, journey proof proves the user/system flow, and release proof proves
  where the change actually reached. Always report the highest proven state.
- Use compact control wording for simple work and full control wording for
  bugfixes, features, production, critical lanes, multi-step work, or whenever
  Hafiz may not know the workflow path.
- Before implementation, explain the intended code/workflow change in plain
  English: options, recommendation, what will change, what will not change,
  risks/tradeoffs, and evidence plan.
- Do not treat memory, old chat, staff symptoms, or a screenshot as stronger
  than current code, docs, data, tests, or production evidence.
- Use the State Ownership Rule from
  [agent-os-state-model.md](agent-os-state-model.md): each state source gets
  one job, and the agent should use the source that owns the question instead
  of duplicating or upgrading weak evidence.
- When current evidence needs approved read-only access, use the narrowest
  relevant auto-read lane proactively instead of asking Hafiz to prompt for it.
- Ask Hafiz to verify only business judgment, subjective acceptance, unsafe
  actions, unavailable access, final risk acceptance, priority, or scope.
- Never read or modify `.env*`, secrets, raw tokens, or files under `live/`.
- Never commit, push, merge, open a PR, deploy, or run destructive actions
  without the approval required by [agent-os-approval-gates.md](agent-os-approval-gates.md).

## Workflow Index

| Workflow | Lane | Use when |
| --- | --- | --- |
| Idea and discussion | Light | Hafiz wants to think, compare, understand, or decide. |
| Work intake | Light to Medium | A request, staff report, Planner card, GitHub issue, Mission Ledger item, or production signal becomes work. |
| Product design | Medium | A feature, redesign, workflow, PRD, UX spec, or build prompt is needed. |
| Implementation readiness | Medium to Critical | A task is moving from idea/design into coding or to another builder. |
| Agent OS improvement loop | Medium | Hafiz wants the Agent OS itself to learn, fix workflow behavior, update skills/playbooks/evals consistently, or make future agents handle something better. |
| Enforcement and drift detection | Medium | Agent OS rules need stronger enforcement, hooks/skills/evals need alignment, or Claude/Codex behavior diverges. |
| Bugfix | Full or Critical | Something is broken and needs diagnosis, fix, proof, and close loop. |
| Related impact audit | Full or Critical | A product fix needs same-pattern search, adjacent regression review, or scope-boundary tracking. |
| Feature | Full or Critical | New behavior or a product workflow needs to be built. |
| Staff issue | Full or Critical | Staff report a SIMS/mobile/support problem through Planner or chat. |
| Critical lane | Critical | Auth, payment, invoice, commission, migration, deploy, production data, or mobile API contract is involved. |
| Implementation | Medium to Full | A scoped change is approved and ready to edit. |
| Verification | Medium to Full | The agent must prove the changed behavior works. |
| QA | Full | Real user/admin/staff journeys need human-style checking. |
| Review | Medium to Full | Risk, scope, evidence, and release state need adversarial review. |
| Commit, push, and PR | Medium to Full | Work is ready to save in git and optionally sync outward. |
| Release, deploy, and monitor | Critical | Merged work needs to reach live safely and be watched. |
| Incident | Critical | Production is failing or may be affecting users/revenue. |
| Project adoption | Medium | A product repo needs the shared Agent OS adapted to its local commands, evidence, risks, and done state. |
| Governance and versioning | Medium | Agent OS changes need source ownership, checks, memory, commit state, and version clarity. |
| Memory, save-session, and handoff | Medium to Critical | Context must survive chat end, compaction, or agent switch. |
| Mission ledger | Light to Medium | Important future work is not ready for GitHub or active task. |
| Developer staff rollout | Medium | Agent OS is prepared for developer staff or another LLM setup. |

## 1. Idea And Discussion Workflow

Starts when Hafiz asks why, what, how, naming, architecture, options, tradeoffs,
or "is this doable?"

Hafiz owns product direction, risk appetite, and final preference. The agent
owns reading available context, explaining options, recommending one next step,
and keeping a living draft when Hafiz asked to document the discussion.

Use chat, local docs, Koda, and lightweight repo search. Do not add commit,
push, deploy, or QA ceremony unless the discussion turns into actual work.

The practical job of this workflow is to protect Hafiz's thinking space. If
Hafiz is still shaping the idea, the agent should help him see the problem,
options, tradeoffs, and likely next move before trying to produce a final
answer or implementation plan.

Use this behavior:

- explain the current understanding in plain language
- ask a small number of useful questions only when needed
- suggest options with tradeoffs instead of presenting one rigid answer
- give a soft recommendation and explain why
- wait for Hafiz's decision when the choice changes product direction, risk,
  priority, UX, architecture, rollout, or approval boundaries
- update a living draft when the discussion is meant to become durable
- keep the next recommended action concrete so Hafiz does not have to ask
  "what next?" repeatedly

Do not:

- turn a thinking question into coding
- create issues, PRDs, commits, branches, or tickets just because the topic
  sounds important
- overload Hafiz with formal workflow labels when normal language is enough
- hide behind process when a direct explanation would help more
- ask for approval on every tiny substep inside a safe discussion/docs packet

Scenario examples:

| Hafiz says | Agent should do |
| --- | --- |
| `why are we doing this?` | Stop action and explain the reason, tradeoff, and practical value. |
| `is this doable?` | Explain feasibility, constraints, risks, and the simplest first version. |
| `what do you suggest and why?` | Give options, recommend one, and justify it plainly. |
| `I don't like this discussion` | Reset the approach, restate the goal, and ask what decision style would help. |
| `ok proceed` after a discussion decision | Document or perform the last agreed safe step, staying inside the stated boundary. |

Evidence required:

- Relevant docs or memory checked when prior context matters.
- Options and recommendation stated in plain language.
- Confirmed decisions recorded in the draft if the discussion is meant to be
  durable.

Exit when Hafiz makes a decision, asks to document, asks to build, or chooses
the next workflow.

Save to:

- living draft docs when the discussion is part of Agent OS or product design,
- Koda only for durable corrections or future-agent rules,
- mission ledger for important future work that is not execution-ready.

Common failure: the agent turns thinking into implementation too early.

## 2. Work Intake Workflow

Starts when work arrives from Hafiz chat, staff report, Planner, GitHub,
production signal, Koda reminder, or Mission Ledger item.

Hafiz owns scope, priority, and major planning decisions. The agent owns
classifying the source, finding the real source of truth, and choosing the
right workflow lane.

Use:

- [task-router.md](task-router.md) to classify the request.
- Planner as staff-reported intake for SIMS/mobile/support work.
- GitHub for execution-ready engineering tickets.
- Mission Ledger for important but not-ready follow-ups.
- Koda for durable lessons, not task tracking.

The practical job of this workflow is to stop messy inputs from becoming messy
engineering work. Intake should identify what was reported, what is actually
known, what is still assumption, and where the work belongs next.

Confirmed decision:

```text
Every input is a signal first, not truth yet.
The agent classifies it, checks enough current evidence, then routes it.
```

Official principle:

```text
Staff and Planner reports are symptoms, not engineering truth.
Hafiz requests are current direction.
GitHub issues are engineering execution.
Mission Ledger is for important later or bigger work.
Koda is durable memory, not current task state.
Current repo/test/production evidence decides what is true now.
```

Use this source split:

| Source | Treat it as | First move |
| --- | --- | --- |
| Hafiz direct request | Current direction | Route immediately, then decide whether to discuss, design, diagnose, or build. If it conflicts with existing GitHub scope, explain the mismatch before expanding work. |
| Staff report | Real-world symptom | Gather reproduction context and quick read-only evidence before treating it as engineering work. |
| Planner card | Staff intake/context | Read as operational context for SIMS/mobile/support work; do not treat as engineering truth or modify Planner unless Hafiz asks. |
| GitHub issue / PR | Engineering execution record | Check scope, current branch/state, and whether the issue is still true. |
| Koda memory | Durable memory/lesson | Treat as historical/trusted context and verify against current files/state before acting. |
| Production signal/log | Live system evidence | Use read-only evidence first; route critical domains through critical lane. |
| Mission Ledger | Bigger goal, future work, or parked decision | Promote to GitHub, PRD, QA plan, or Koda only when ready. |
| Agent-discovered issue | Finding that needs routing | Report it, then fix if in scope, create/link GitHub if execution-ready, or park it in Mission Ledger if bigger/future. |

Intake outcomes:

| Outcome | Use when |
| --- | --- |
| discuss | The request is still an idea, preference, architecture question, or tradeoff. |
| diagnose | There is a symptom but not enough evidence for a fix. |
| design | The work changes workflow, UX, product rules, or multi-module behavior. |
| create/link GitHub issue | There is likely engineering work with a titleable scope. |
| capture in Mission Ledger | The follow-up matters but is not ready for execution. |
| store in Koda | The lesson/preference/correction should guide future agents. |
| reject/close | The report is duplicate, not reproducible enough, out of scope, or intentionally not doing. |

For coding work, prefer creating or linking a GitHub issue after quick
diagnosis. Do not create an issue from a vague symptom if the agent has not yet
identified the affected role, likely project/module, and one or two pieces of
supporting evidence. Also do not begin real implementation with no trace. Once
quick diagnosis shows likely engineering work, create/link the GitHub issue or
use the approved active task/work packet before editing code.

Detailed intake rules:

- Planner should not automatically become a GitHub issue without quick
  diagnosis.
- Staff reports should always be treated as symptoms first.
- Agent-discovered issues should be reported before action unless they are
  clearly inside the approved scope and safe to fix.
- Hafiz chat can override priority or direction, but if it expands a GitHub
  issue, the agent must explain the scope mismatch before expanding work.
- Koda can explain why a rule exists, but current files, tests, runtime
  evidence, or production-safe evidence decide whether the old memory still
  applies.
- If a relevant auto-read lane exists, the agent should use it during quick
  diagnosis instead of skipping evidence or asking Hafiz to repeat the access
  instruction.

Scenario examples:

| Input | Agent should do |
| --- | --- |
| `Staff says invoice button does nothing` | Treat as symptom, check Planner/context if relevant, inspect route/code/browser evidence if safe, then create/link GitHub issue only if likely engineering work. |
| `I want to redesign tutor requests` | Route to product design, inventory current behavior, discuss decisions before build. |
| `Fix this known bug, issue #123` | Read the issue, verify current state, check active task/branch, then build if safe. |
| `Remember later we need better QA for this` | Capture in Mission Ledger or Koda depending on whether it is a follow-up or durable lesson. |
| `Production payment failed` | Critical lane: read-only diagnosis first, no code/data mutation before approval. |

Evidence required:

- Source identified: chat, Planner, GitHub, production, Koda, or ledger.
- Current state checked enough to avoid duplicate or stale work.
- For outside intake such as staff reports, screenshots, Planner cards,
  WhatsApp notes, customer complaints, or vague symptoms, run a quick read-only
  diagnosis before creating a GitHub issue. Create or link the GitHub issue
  once there is confirmed or likely engineering work.
- Quick diagnosis means enough read-only checking to avoid creating a bad
  GitHub issue, not a hidden implementation phase. It should identify the
  reported symptom, affected user or role, likely project/module, whether this
  looks like engineering work, and one or two pieces of evidence such as code
  search, existing issue search, screenshot review, safe data read, or safe log
  check when already within the task scope.
- Quick diagnosis must stop before code edits, data mutation, commit, deploy,
  destructive action, or broad investigation. If the report touches auth,
  payment, invoice, commission, migration, deployment, production data, or
  mobile API contracts, keep it in critical-lane read-only diagnosis until
  Hafiz approves implementation.
- For clear development requests from Hafiz, create or link the GitHub issue
  before implementation begins when the project requires one.

Exit when the work is routed to discussion, product design, diagnose, build,
verify, QA, review, commit, release, save-session, or blocked/clarification.

Save to:

- GitHub issue for execution-ready coding work,
- mission ledger for future or adjacent work,
- final response with the chosen next workflow.

Common failure: treating a staff symptom as verified root cause.

## 3. Product Design Workflow

Starts when Hafiz asks for a PRD, UX, build prompts, workflow redesign, new
module, or a cross-module product decision.

Hafiz owns business rules, staff workflow acceptance, priorities, and final
product direction. The agent owns reading current behavior, drafting artifacts,
surfacing tradeoffs, and keeping decisions updated as Hafiz answers.

Use [product-design.md](product-design.md). For SIMS browser UI/UX work, read
the tracked `sifu-tutor/docs/ui-ux/` package before specifying screens,
components, copy, states, or quality gates.

Confirmed implementation-readiness rule:

```text
Before code is written, Hafiz should understand the intended implementation in
plain English. The agent should explain options, recommendation, what will
change, what will not change, likely files/modules, risks, and evidence plan.
```

This does not mean Hafiz must manually review code. It means the agent must
translate the implementation plan into understandable behavior before build
starts.

Use conversational preparation depth, not numeric labels:

| Phrase | Use when |
| --- | --- |
| `Quick Brief` | Small safe changes where a short English explanation is enough before implementation. |
| `Product Shape` | User workflow, staff process, unclear expected behavior, or multiple implementation options. |
| `Build-Ready Pack` | Major workflow, critical lane, multi-role/module work, backend/frontend contract, or handoff to another builder. |

The agent should recommend the lightest safe preparation, but risk can force
deeper preparation. Hafiz can ask for more or less, and the agent should explain
any safety concern in normal language.

Content standard:

- Quick Brief answers what is wrong, what will change, what will not be
  touched, and how it will be checked.
- Product Shape explains the problem, current behavior, affected users, options,
  recommendation, tradeoffs, evidence plan, and decision needed.
- Build-Ready Pack maps the workflow/spec/contract/test plan/build prompt before
  implementation.

Evidence required:

- Current-state evidence from code, docs, Planner, Koda, or production-safe
  reads when relevant.
- Confirmed decisions log.
- Open questions limited to decisions that change behavior, risk, scope, UX,
  RBAC, data contract, or acceptance tests.
- Backend contract for controllers, services, jobs, invoices, payments, class
  scheduling, commissions, auth, mobile APIs, or data repair.

Exit when the artifact is clear enough for implementation handoff, or when the
remaining decision is explicitly waiting for Hafiz.

Save to:

- project feature docs for confirmed PRD/UX/build prompts,
- mission ledger for bigger follow-ups,
- Koda for durable product/workflow rules.

Common failure: building from a weak prompt that lets another agent satisfy a
nearby behavior instead of the actual requirement.

## 3A. Implementation Readiness And Build Handoff Workflow

Starts when a task is about to move from discussion, PRD, UX, diagnosis, or
issue intake into coding, especially when another agent or human builder will
implement it.

Hafiz owns business meaning, risk acceptance, and final scope. The agent owns
making sure the implementation is clear enough to build without guessing.

Use [ai-implementation-readiness.md](ai-implementation-readiness.md).

Plain meaning:

```text
Before an agent writes code, it should know what problem is being solved, where
the behavior starts, what rule must be preserved, what state changes, what must
not change, how edge cases behave, how the work will be proven, and where the
task should stop.
```

Use conversational readiness:

- Quick Brief for tiny safe changes
- Product Shape for real implementation work that still needs product clarity
- Build-Ready Pack for critical lanes, cross-module work, mobile/API
  contracts, new modules, or handoff to another builder

Evidence required:

- current understanding in plain language
- options considered when there is more than one valid path
- recommendation and why
- real entry point or explicit investigation needed
- business rule and state transition
- out-of-scope list
- evidence plan and permanent E2E decision when user-facing
- stop point and approval boundary

Exit when the task is either build-ready, intentionally sent back for more
diagnosis/design, or waiting for Hafiz's decision.

Save to:

- PRD/UX/build prompt when product work is being handed off,
- GitHub issue when engineering work is execution-ready,
- Mission Ledger for future or adjacent work,
- Koda for durable readiness rules.

Common failure: the agent starts coding from a vague instruction because it can
find a nearby file, then proves a weaker behavior than Hafiz actually needed.

## 3B. Agent OS Improvement Loop

Starts when Hafiz asks to improve the workflow, fix Agent OS behavior, make
future agents handle something better, or prevent a repeated agent mistake.

Hafiz owns the desired collaboration behavior and whether the system should get
stricter or more relaxed. The agent owns classifying the mistake, choosing the
source of truth, checking connected files, updating the smallest coherent set
of docs/skills/evals/Koda/Session Map, and proving the wiring still works.

Use [agent-os-improvement-loop.md](agent-os-improvement-loop.md).

Plain meaning:

```text
Do not add one random rule somewhere. Work out what went wrong, update the
layer that owns it, check connected files, and add proof if the mistake should
not quietly return.
```

Evidence required:

- What Agent OS behavior was wrong or confusing.
- The mistake type: communication, routing, approval, memory, state,
  skill/playbook drift, hook drift, eval gap, parity issue, or workflow weight.
- The source of truth that owns the fix.
- Which connected files were checked or intentionally left alone.
- Which checks prove the workflow still works.
- Whether Koda was stored, updated, or skipped.

Exit when Hafiz understands the improvement, the right layers are updated, the
checks pass or gaps are named, and the next Agent OS or product workflow is
clear.

Save to:

- the owning Agent OS playbook,
- skill registry or adapter files when skill behavior changes,
- evals/fixtures when repeated behavior should be caught,
- Koda for durable corrections and lessons,
- Session Map for current-session continuity.

Common failure: saving a Koda memory or adding a sentence to one doc while the
skill, router, eval, or hook that actually controls the behavior stays stale.

## 3C. Enforcement And Drift Detection Workflow

Starts when a rule is being ignored, hooks/skills/evals need alignment, Claude
and Codex behave differently, or Hafiz asks how the Agent OS will make agents
actually follow the workflow.

Hafiz owns the desired behavior and tolerance for automation. The agent owns
identifying the drift type, choosing the right enforcement layer, updating the
smallest useful source, and running the right checks.

Use [agent-os-enforcement-drift.md](agent-os-enforcement-drift.md).

Plain meaning:

```text
Do not make every rule a hook. Hooks stop dangerous mistakes. Skills guide
normal workflow. Evals catch repeated drift. Health checks prove the wiring.
```

Evidence required:

- What drift or enforcement gap exists.
- Which layer owns it: docs, skill/playbook, hook, guard, eval, health,
  Session Map, or Koda.
- Why the chosen enforcement strength is enough.
- Which checks prove the wiring still works.

Exit when the rule is documented, enforced or tested at the right strength, and
the next action is clear.

Save to:

- enforcement/drift docs,
- hook dispatcher or skill registry when their behavior changes,
- evals/fixtures when a repeated behavior must be locked,
- Koda for durable corrections,
- Session Map for current-session continuity.

Common failure: adding hook complexity for a rule that needs agent judgment, or
leaving a repeated approval/safety mistake as a loose doc note.

## 3D. Session Map Lifecycle Workflow

Starts when a conversation is long, multi-goal, resumed after a pause, split
across agents, or at risk of losing the main story.

Hafiz owns the real mission and whether a new topic is actually separate. The
agent owns keeping the map honest: current focus, side paths, evidence, Git
state, waiting decisions, and next action.

Use [session-map.md](session-map.md).

Plain meaning:

```text
One meaningful session gets one map. Keep using that map for the same mission.
Start a new map only when the work becomes a different mission.
```

Evidence required:

- The map matches the current main goal, project, branch, and next action.
- Side paths are inside the current map unless they become a different mission.
- Multiple possible maps are resolved before editing.
- The lifecycle state is clear: Active, Continued, Parked, Handed off,
  Promoted, or Closed.

Exit when the map tells the next reader whether to continue, park, hand off,
promote, close, or create a new map.

Save to:

- active Session Map for current-session continuity,
- Koda for durable Session Map rules or Hafiz corrections,
- Mission Ledger when a side path becomes future work,
- GitHub issue when a side path becomes execution-ready coding work,
- save-session or handoff when another session or person must continue.

Common failure: creating several maps for one continuing mission, or keeping
one map after the work has become a different project, branch, release path,
owner, or unrelated mission.

## 4. Bugfix Workflow

Starts when something is broken, failing, confusing, or reported as not working.

Hafiz owns business acceptance and risk decisions. The agent owns reproduction,
root-cause diagnosis, implementation after the right approval, regression
coverage, verification, QA, and review.

Use [diagnose.md](diagnose.md), then build only after the scope and approval
are clear. If the bug touches a critical domain, route through the Critical Lane
workflow first.

Use [related-impact-audit.md](related-impact-audit.md) throughout bugfix work.
Plain meaning: every bugfix gets a local related check, reusable root causes get
a same-pattern sweep, and critical lanes get a critical impact audit.

Simple version:

```text
Do not just change code and ask Hafiz to test.
Understand the symptom, check the current truth, explain the planned fix,
implement the smallest real cause, then prove both the code and the real user
journey where the behavior is user-facing.
```

Evidence required:

- Symptom and affected user journey described in plain language.
- Reproduction or best available evidence.
- Root cause or most likely cause.
- Related-impact audit strength and result.
- Focused test that fails before or would have caught the bug, where feasible.
- Permanent E2E regression decision for user-facing workflows.
- Agent-run human-journey proof when safe.

Scenario:

| Staff says | Agent should do |
| --- | --- |
| `The invoice button does nothing` | Treat this as a symptom first. Identify the page, role, and expected action; check current code/browser/API/log evidence where safe; explain the likely cause and planned fix in English; fix the smallest cause; add or update a regression test; run focused checks; use browser or Playwright proof when feasible; then report what changed, what was checked, what remains, and the recommended next action. |

Bugfix scenario matrix:

| Scenario | Preparation | Core path | Evidence | Stop point |
| --- | --- | --- | --- | --- |
| Tiny obvious bug, typo, or copy-only issue | Quick Brief. | Explain the small change, edit the narrow file, run the smallest useful check. | Diff/readback or focused command. E2E only when user-facing behavior changed. | Commit if approved; push only if separately approved. |
| Staff-reported UI bug | Quick diagnosis first, then Quick Brief or Product Shape depending on ambiguity. | Treat report as symptom, reproduce or inspect, identify affected role/page/action, fix smallest cause, related-impact local check, E2E decision, QA/review. | Focused code test where useful, browser/Playwright or screenshot evidence when feasible, permanent E2E file or named exception. | Usually commit-ready after verify/QA/review; push/PR only with approval. |
| Backend/API bug with no visible workflow | Quick Brief or Product Shape if contract impact is unclear. | Diagnose request/response/service path, fix exact rule, related-impact local check or same-pattern sweep. | Unit/feature/API tests, contract evidence, consumer compatibility note. | Commit-ready after verify/review. |
| Reusable root-cause bug | Product Shape for scope and related findings. | Diagnose root pattern, run same-pattern sweep, fix in-scope occurrences, track out-of-scope findings. | Regression test for original bug and pattern, related-impact report. | Stop before broad refactor or cross-module expansion unless Hafiz approves. |
| Critical invoice/payment/auth/commission/migration/mobile API bug | Build-Ready Pack, but Phase A is read-only diagnosis first. | Diagnose safely, name impact/risk, recommend fix path, wait for implementation approval, then implement in a controlled slice. | Critical impact audit, negative tests, idempotency/retry/state evidence, human-journey/API proof, release risk notes. | Diagnosis first unless implementation boundary is explicitly approved; deploy/live remain separate approvals. |
| Production incident | Incident workflow, not ordinary bugfix first. | Protect users, triage read-only, identify severity, mitigation, rollback/fix-forward options, then implement only after required approval. | Monitoring/log evidence, smoke/live-check after release, postmortem or durable lesson when material. | Stop at the approved incident boundary: triage, fix, deploy, monitor, or postmortem. |

Related-impact default:

```text
Every bugfix gets at least a local related check.
Reusable root causes get a same-pattern sweep.
Critical lanes get a critical impact audit.
```

Scope boundary:

```text
Find related risks proactively. Fix only clearly in-scope related issues. Ask
or track anything that expands scope.
```

What done means examples:

| Situation | What done means | Why |
| --- | --- | --- |
| Clear low-risk bug | Fixed, tested, reviewed, and committed | The useful end is a saved fix, but push/PR still depends on approval. |
| User-facing staff workflow bug | Staging verified when staging exists and is safe | The real proof is that the affected journey works outside local code. |
| Production incident | Production monitored after explicit deploy approval | The job is not done until live behavior is healthy after release. |
| Critical invoice/payment/auth/mobile API bug | Diagnosis first, then Hafiz approves how far to continue | The first end state is understanding risk before implementation. |

Daily control shape:

```text
What done means:
<true end goal>

My recommended stop point:
<where I think we should stop for this task>

Why:
<short reason>

Suggested path:
<plain workflow steps>

I will proceed until:
<current approved boundary>

I will only pause if:
<new scope, risk, evidence, access, approval, or owner decision appears>

To go further:
<approval phrase or decision needed>
```

Compact shape for simple work:

```text
What done means:
<simple end goal>

I will proceed until:
<near stop point>

I will only pause if:
<small set of likely blockers>
```

Exit when the fix is verified, QA/review risk is addressed, and the repo state
is clear: local-only, committed, pushed, PR open, merged, deployed, or live
smoke passed.

Save to:

- GitHub issue/PR where applicable,
- TESTING.md or test docs when coverage changed,
- Koda for non-obvious fix patterns,
- save-session if the task is meaningful or spans context.

Common failure: "fixed in code" is mistaken for "merged" or "live".

## 5. Feature Workflow

Starts when new behavior, a new page, a new module, or changed user workflow is
ready to build.

Hafiz owns product acceptance, priority, and scope changes. The agent owns
turning the approved design into vertical slices, implementing each slice,
testing, verifying, and reporting gaps.

Use product design artifacts first when the feature is more than a narrow
change. Use vertical-slice TDD where applicable: one failing test, one
implementation, one passing test, repeat.

Simple version:

```text
For features, the agent is not only the coder. It is also the first tester and
workflow checker. Backend/unit tests prove the engine; E2E, browser/mobile
smoke, API evidence, screenshots, or a clear QA checklist prove that a real
staff/admin/parent/tutor/student/customer can complete the journey.
```

Evidence required:

- Clear acceptance rules.
- What done means and why: local, committed, PR, staging, production, or
  monitored live state.
- Suggested path and stop point, in plain workflow steps.
- Pause conditions: the specific situations that would make the agent stop and
  ask Hafiz instead of continuing.
- Control message size: compact for simple work, full for risky/multi-step work.
- Backend/API/state contract when behavior crosses modules.
- Tests at the right layer.
- Permanent E2E coverage for changed user workflows by default.
- QA or browser/mobile/API smoke for the real journey.
- Release communication decision for staff-facing changes.

Feature scenario matrix:

| Scenario | Preparation | Core path | Evidence | Stop point |
| --- | --- | --- | --- | --- |
| Tiny feature or field/copy addition | Quick Brief. | Explain what changes and what stays out of scope, implement the narrow slice, run focused checks. | Diff/readback, focused tests when behavior changed, E2E decision if user-facing. | Commit if approved; push/PR only if separately approved. |
| Small feature slice with clear behavior | Product Shape when choices or user impact exist. | Confirm acceptance rules, build one vertical slice, add/update tests, verify and QA the changed journey. | Unit/feature/API test plus browser/mobile/API journey evidence where relevant. | Commit or PR-ready after review, depending on approved boundary. |
| Bigger feature or changed workflow | Product Shape first, then Build-Ready Pack before coding. | PRD/UX/contract as needed, split into vertical slices, build slice-by-slice, verify each accepted behavior. | Tests at the right layer, permanent E2E for changed user workflows, QA evidence, release communication decision. | Usually Build-Ready Pack or first slice only; continue only within approved boundary. |
| Cross-module, mobile/API, invoice/payment/auth, or migration feature | Build-Ready Pack and critical-lane rules where relevant. | Map roles, state transitions, contracts, idempotency/retry, backwards compatibility, rollback, tests, and approval gates before coding. | Negative and production-shaped tests, API/mobile compatibility, human-journey proof, critical review. | Stop before implementation, deploy, data mutation, or critical-lane widening unless approved. |
| Feature handed to another agent/dev | Build-Ready Pack. | Provide goal, scope, pre-read files, entry points, business rules, out-of-scope list, test plan, evidence, pause conditions, final report shape. | Handoff can be checked against implementation-readiness requirements; receiver must re-verify current files before editing. | Handoff-ready, not implemented, unless implementation is also approved. |
| Feature discovered while fixing another issue | Usually Mission Ledger or GitHub follow-up first. | Report the finding and compare it to the current scope. | Clear reason why it is in scope, or a follow-up record if not. | Do not silently add it to the current fix/PR. |

Exit when all accepted slices are implemented, evidence is gathered, review is
clean or risks are accepted, and the next git/release state is explicit.

Save to:

- feature docs, TESTING.md, GitHub issue/PR, Mission Ledger for bigger
  follow-ups, Koda for durable lessons, and final close-out.

Common failure: implementing all backend or all UI first instead of proving one
complete slice.

## 6. Staff Issue Workflow

Starts when staff report a SIMS, tutor app, parent app, support-ticket, TREQ,
TUT, or operational problem.

Hafiz owns priority and staff communication decisions. The agent owns reading
Planner or the provided report as intake, proving whether the symptom is real,
and converting confirmed engineering work into the normal GitHub/task flow.

Use Planner as context, not the engineering source of truth. Do not modify
Planner state, assignment, priority, or content unless Hafiz asks.

Evidence required:

- Staff symptom captured in plain language.
- Current code/data/UI/log evidence checked where safe.
- Impact and affected role identified.
- If fixed, human-journey proof that matches what staff do.
- Staff-facing release communication decision when behavior changes.

Exit when the issue is disproven, routed to design, routed to bugfix, converted
to GitHub, fixed and verified, captured in Mission Ledger, or waiting for
staff/Hafiz evidence.

Save to:

- GitHub for confirmed coding work,
- Mission Ledger for bigger operational goals or future follow-ups,
- Planner only when Hafiz explicitly asks,
- Koda for durable staff-workflow lessons.

Common failure: asking Hafiz or staff to retest before the agent has used
available safe tools.

## 7. Critical Lane Workflow

Starts whenever auth, payments, invoices, commissions, migrations, deployment,
production data/log actions, mobile API contracts, or irreversible risk appear.

Hafiz owns implementation approval, final risk acceptance, and production
release decisions. The agent owns read-only diagnosis first, risk explanation,
implementation plan, and exact verification plan.

Evidence required in Phase A:

- Read-only code/docs/data/log inspection.
- Likely cause or explicit uncertainty.
- Recommended implementation path.
- Risk and rollback considerations.
- Exact tests/smoke needed after approval.

Approval required:

- Explicit Phase B approval before implementation.
- Separate approval for commit, push, merge, PR, deploy, destructive action, or
  production mutation as defined by the relevant playbook.

Exit when Phase A is handed to Hafiz for decision, or Phase B is completed with
tests, human-review status, and remaining risks stated.

Save to:

- docs/issue/PR for evidence,
- Koda for non-obvious critical-lane lessons,
- Critical Save when the session ends.

Common failure: a small-looking invoice/payment/API change is treated like an
ordinary bugfix.

## 8. Implementation Workflow

Starts when a scoped change is approved or clearly requested and is safe to
edit.

Hafiz owns scope changes and final acceptance. The agent owns editing the
smallest correct set of files, following repo patterns, preserving unrelated
dirty work, and checking the result.

Use project `AGENTS.md`, active task state, nearest docs, and existing code
patterns. For user-facing work, read TESTING.md when present before changing
behavior.

Evidence required:

- Files changed are inside the requested scope.
- Existing conventions reused.
- No unrelated cleanup or broad refactor unless requested.
- Focused tests or checks run as soon as useful.

Exit when implementation is ready for verification, or when blocked by missing
decision/access/safe data.

Save to:

- code/docs/tests,
- active task state when the project uses it,
- final response with changed files and verification next.

Common failure: adjacent cleanup creates a larger review and more risk than the
actual task.

## 9. Verification Workflow

Starts after implementation, before QA/review/commit, or when Hafiz asks the
agent to prove something works.

Hafiz owns only the checks that require owner judgment or unsafe access. The
agent owns all safe developer/tester checks it can run.

Use [verify.md](verify.md) and [agent-os-evidence-model.md](agent-os-evidence-model.md).

Evidence required:

- Focused command results.
- TESTING.md row checked when present.
- Permanent E2E regression decision for user-facing workflows.
- Human-journey evidence when a real user depends on the behavior.
- SIMS UI/UX quality-gate evidence for `sifu-tutor` browser UI-visible work.
- Highest proven state and which proof layers were reached: code proof,
  journey proof, and/or release proof.

Exit when the changed behavior is proven, failures are separated into baseline
vs task-caused, or a named blocker prevents honest verification.

Save to:

- final answer, PR body, QA notes, TESTING.md, or task state as appropriate.

Common failure: unit tests pass but the user journey is still untested.

Verification scenario matrix:

| Scenario | What verify should prove | Enough evidence | Not enough |
| --- | --- | --- | --- |
| Docs or Agent OS workflow change | The written rule, link, or workflow wiring is coherent and not broken. | Diff/readback, link/path check where relevant, Agent OS eval/health checks for workflow behavior. | Saying the wording looks fine without running the related workflow checks. |
| Backend rule or calculation | The rule behaves correctly in the engine. | Focused unit/service/feature test, edge case for business/data risk, baseline failure separated if present. | UI smoke only, or tests that do not cover the changed rule. |
| API contract | The endpoint, permission, response shape, and error path still match consumers. | API/contract test or curl/client evidence, permission/error check, paired frontend/mobile evidence when affected. | A controller/unit test that never checks the real response shape. |
| Browser UI workflow | A real staff/admin/parent/tutor/student/customer action works. | Focused code test where useful plus Playwright/browser proof, screenshot when helpful, permanent E2E file or named exception. | Unit tests only, or asking Hafiz to click it when the agent can safely check. |
| Mobile workflow | The changed mobile screen or native behavior works for the user path. | Unit/screen tests, lint/type/build checks, simulator/device smoke when practical for real journey/native behavior. | Snapshot/unit proof only when the issue is an interactive mobile journey. |
| Critical lane | The safe diagnosis and approved implementation behave without hidden money/data/security risk. | Read-only diagnosis first, approved implementation boundary, negative tests, idempotency/retry/state evidence, safe staging or API proof. | Green happy-path tests with no critical risk evidence. |
| Deploy/release check | The claimed environment actually has the right version and changed behavior. | Deployed SHA/version, target-environment smoke of changed workflow when safe, logs/monitoring check. | Local tests or route availability while claiming staging/production is ready. |

## 10. QA Workflow

Starts after verification or when the task needs user-role, browser/mobile,
regression, visual, release, or manual-style testing.

Hafiz owns subjective product acceptance and final release risk. The agent owns
safe QA evidence before asking Hafiz or staff to check.

Use [qa.md](qa.md). For SIMS UI/UX, check the tracked UI/UX quality gate and
relevant design docs.

Evidence required:

- Role and journey being tested.
- Setup, action, expected result, how to verify, and what failure looks like.
- Browser/mobile/API/screenshot evidence when feasible.
- Highest proven state for the journey and release/live state.
- Clear list of untested areas and why.

Exit when the journey is QA-passed, blocked with a specific reason, or handed
to Hafiz/staff for the parts only they can judge.

Save to:

- QA docs, screenshots/evidence paths where used, PR body, TESTING.md, final
  close-out.

Common failure: "manual QA needed" becomes a shortcut for checks the agent
could have done itself.

QA scenario matrix:

| Scenario | What QA should test like a human | Enough evidence | When to ask Hafiz/staff |
| --- | --- | --- | --- |
| Docs or Agent OS change | The instruction is understandable and points to the right source. | Readback, generated dashboard/render if relevant, health/eval output. | Tone, wording preference, or strategic direction. |
| Backend/API behavior | The system response matches the expected business rule and consumer need. | API/client smoke, response/error evidence, safe state read when useful. | Business rule acceptance or unavailable representative data. |
| Staff-facing browser bug | The exact staff journey that failed now works and old failure is blocked. | Setup/action/expected/failure shape, browser/Playwright or screenshot proof, regression/E2E coverage. | Staff acceptance, subjective workflow fit, or credentials/data the agent lacks. |
| New user-facing feature | Happy path, key roles/states, important edge cases, empty/loading/error states, and release communication. | Permanent E2E or named exception, browser/mobile/API smoke, TESTING.md row where present, screenshots when useful. | Product fit, wording, operational rollout, or risk acceptance. |
| Mobile app change | The screen flow, API state, and native behavior behave for a real tutor/parent path. | Screen/unit tests, simulator/device smoke when practical, build/lint/type evidence. | Physical device/account limitations or subjective UX acceptance. |
| Critical lane or incident | The safe workflow, fallback, logs, and post-change monitoring support the claimed state. | Staging/API proof, negative cases, read-only logs/monitoring, smoke after deploy if approved. | Final risk acceptance, production mutation, rollback, or destructive/manual business decision. |

## 11. Review Workflow

Starts before commit, push, PR, merge, deploy, or whenever Hafiz asks for a
review.

Hafiz owns final go/no-go when risk remains. The agent owns adversarial review:
bugs, regressions, missing evidence, state confusion, scope creep, release
communication, UI/UX drift, and critical-lane gaps.

Use [review.md](review.md).

Plain version:

```text
Verify proves the work behaves.
QA proves the journey makes sense.
Review protects the next state from hidden risk.
```

Evidence required:

- Current diff and changed files inspected.
- Tests/evidence checked against the changed behavior.
- Code proof, journey proof, and release proof separated where relevant.
- User-facing E2E decision checked.
- Multi-fix session state checked when more than one issue is involved.
- Scope, evidence, state, release communication, critical-lane, multi-fix, and
  product/business risks checked before commit, push, PR, merge, or deploy.
- Findings listed by severity with file/line references where possible.

Exit when findings are fixed, accepted, or clearly blocking.

Save to:

- final answer, PR review, task state, mission ledger for future follow-ups.

Common failure: review reads the code but does not translate risk into product
meaning for Hafiz.

Review scenario matrix:

| Scenario | Review should challenge | Blocks the next state when |
| --- | --- | --- |
| Before local commit | Scope, changed files, evidence, guard result, commit message, and whether the claimed proof matches the work type. | File list is unclear, guard/check failed, required evidence is missing, or unrelated changes are staged. |
| Before push or PR | Everything needed for other agents/CI/reviewers to trust the change. | Local state is dirty/confusing, verify/QA is incomplete, Session Release Ledger is stale for multi-fix work, or E2E/release communication gaps are hidden. |
| Before merge | PR state, CI, review comments, evidence gaps, release communication, and whether the branch is safe to integrate. | CI/review is unresolved, critical-lane approval is missing, product decision is unresolved, or the PR claims more than evidence proves. |
| Before deploy | Source commit, target environment, rollback/mitigation, critical-lane risk, smoke plan, and monitoring plan. | Deploy approval is missing, smoke/monitoring cannot be run safely, or the change touches production-sensitive behavior without the right review. |
| Before saying live/done | Release proof and acceptance proof. | There is no deployed version evidence, changed workflow was not live-smoked, monitoring was not checked, or Hafiz still needs to accept business/product risk. |
| PR/chat review for Hafiz | Product meaning, before/after behavior, risks, evidence, and decision point in natural language. | Hafiz would need to read the code diff to understand the decision, or the agent hides a blocker in a summary. |

## 12. Commit, Push, And PR Workflow

Starts when Hafiz asks to prepare a commit, commit, push, open PR, merge, or
approve an exact commit/push bundle.

Hafiz owns approval for file list, commit, push, PR, and merge boundaries. The
agent owns guard checks, exact inventory, clean staging, commit message shape,
and final state reporting.

Use [commit.md](commit.md) for local commit. Use review before outbound state
changes.

Evidence required before commit:

- `git status --short` and relevant diffs inspected.
- Guard script passed.
- Required verify/QA/review steps completed or explicitly accepted.
- Exact file list approved.
- Commit message follows project format.

Push/PR/merge approval must be explicit in the current session. A commit
approval does not imply push. A push approval does not imply deploy.

Use [push-pr-ci-automation.md](push-pr-ci-automation.md) when Hafiz wants PR
opening, CI checking, PR readiness, or merge to be less manual. Plain meaning:
the agent should automate repetitive GitHub work after one clear boundary, then
stop at the next real authority decision. For example, "proceed until PR ready"
can include push, PR creation, PR body, CI monitoring, and in-scope CI fixes,
but it stops before merge. "Proceed until merged if CI passes" may include
merge only when the boundary explicitly says so and the work is not blocked by
critical-lane, evidence, review, or branch-protection risk.

Exit when the requested git action is completed, refused for safety, or waiting
for exact approval.

Save to:

- git commit SHA, pushed branch/PR URL when created, final state, Koda only for
  durable workflow lessons.

Common failure: local-only work is described as done without saying it is not
pushed, merged, or live.

Another common failure: the agent asks Hafiz to approve push, PR open, CI
monitoring, and PR summary as four separate steps when one PR-ready boundary
would be clearer.

## 12A. Workflow Efficiency Audit

Starts when Hafiz says the workflow is inefficient, confusing, too strict, too
loose, or when repeated manual approval happens for steps he normally accepts.

Use [workflow-efficiency-audit.md](workflow-efficiency-audit.md).

Plain meaning: inspect the workflow like a product. Find where Hafiz is doing
work the agent should do, where the agent is skipping evidence it could gather,
where state is confusing, and where automation would help without removing real
risk decisions.

Evidence required:

- The repeated friction or confusing step is named.
- The practical impact on Hafiz or the agent workflow is explained.
- The suggested fix names the owning layer: playbook, skill, hook, eval, Koda,
  Session Map, GitHub, or final response shape.
- The automation boundary is named: read-only, mechanical, or boundary-based.
- The remaining risk guard is named.

Exit when the audit either recommends no change, captures a future follow-up, or
routes to [agent-os-improvement-loop.md](agent-os-improvement-loop.md) for a
coherent docs/skills/hooks/evals update.

## 13. Release, Deploy, And Monitor Workflow

Starts when merged or approved work needs to reach staging/production, or Hafiz
explicitly asks to deploy/release/monitor.

Hafiz owns production approval and final risk acceptance. The agent owns
preflight, deploy execution only after approval, smoke checks, monitoring, and
clear live-state reporting.

Use project deploy docs plus [monitor-production-logs.md](monitor-production-logs.md).
Do not deploy from this master workflow alone.

Use [release-deploy-live-monitoring.md](release-deploy-live-monitoring.md) for
the exact post-merge boundary. Plain meaning: the agent must distinguish merged,
staging deployed, staging smoke checked, production deployed, production smoke
checked, production monitored, and accepted / closed. "Proceed until production
monitored" can include deploy only after explicit deploy approval, safe smoke
checks, and read-only monitoring; it does not include new fixes, rollback,
critical-lane widening, destructive action, or final business risk acceptance
unless those are named.

Evidence required:

- Source commit/branch/PR identified.
- Preflight and backup requirements checked according to project playbook.
- Deploy approval explicit.
- Deployed commit/state verified.
- Changed workflow smoked on deployed environment where safe.
- Logs/monitoring checked when relevant.

Exit when deploy is complete and monitored, rolled back, or stopped before
release due to risk/blocker.

Save to:

- release notes, PR/issue state, production smoke evidence, Koda for
  durable deploy lessons, Critical Save if session ends.

Common failure: pushed or merged code is mistaken for live behavior.

## 14. Incident Workflow

Starts when production is failing, staff/users are blocked, money/security/data
may be affected, or monitoring shows a serious regression.

Hafiz owns severity, user communication, emergency-risk acceptance, and
production mutation approval. The agent owns read-only triage, impact
assessment, safest mitigation options, implementation only after approval, and
post-fix monitoring.

Use [incident-workflow.md](incident-workflow.md). Plain meaning: incidents are
protection-first work. The agent should triage with safe read-only evidence,
name impact and severity, recommend mitigation options, then stop for Hafiz
before production deploy, rollback, destructive action, data mutation,
critical-lane widening, or business communication decisions.

Evidence required:

- What happened and who is affected.
- Whether the issue is ongoing, intermittent, or already stopped.
- Whether there is a safe mitigation before code changes.
- Read-only evidence from logs, HTTP checks, code, data-safe reads, or staff
  reproduction.
- Fix/rollback/monitoring plan before mutation.

Exit when the incident is mitigated, fixed, handed off, or waiting for a
business decision.

Save to:

- incident note/postmortem when material,
- GitHub issue/PR,
- Mission Ledger for follow-up prevention work,
- Koda for durable root-cause and prevention lessons.

Common failure: an incident is handled like a normal low-risk bugfix.

## 14A. Project Adoption Workflow

Starts when Hafiz wants Agent OS applied to a product repo, asks whether a repo
is Agent OS-ready, prepares a repo for Claude/Codex/another LLM, or wants staff
or trusted builders to use a product repo safely.

Hafiz owns rollout priority, who gets access, and which gaps are acceptable.
The agent owns reading the current repo docs, running safe dry-run checks,
drafting the local project profile, and naming unknowns instead of guessing.

Use [project-adoption.md](project-adoption.md), install docs, rollout
readiness, capability model, evidence model, and approval gates.

Plain meaning:

```text
Keep one shared Agent OS, then give each product repo a small adapter that says
how this repo builds, tests, deploys, proves user journeys, and defines done.
```

Evidence required:

- Root `AGENTS.md` and target project `AGENTS.md` read.
- Target `CLAUDE.md` or equivalent reference checked.
- Active task state checked when present.
- `TESTING.md`, deploy docs, QA/E2E docs, and project-specific commands checked
  when present.
- Installer dry-run run from the umbrella root.
- Local project profile drafted or verified with unknowns named.

Exit when the repo state is reported as not adopted, baseline present, profile
drafted, profile verified, ready for internal agent use, ready for staff-safe
use, or ready for builder use.

Save to:

- product `AGENTS.md` or linked project profile,
- Session Map for current adoption progress,
- Koda for durable lessons,
- Mission Ledger for important future adoption gaps.

Common failure: treating file installation as the same thing as a verified
project workflow.

## 14B. Governance And Versioning Workflow

Starts when Hafiz changes how the Agent OS itself should work, when an agent
adds a new playbook/skill/hook/eval, or when a correction needs to become a
durable rule.

Hafiz owns the operating preference and risk tolerance. The agent owns choosing
the source of truth, checking connected files, running the right checks, saving
Koda only when useful, and reporting the highest proven Git state.

Use [agent-os-governance.md](agent-os-governance.md).

Plain meaning:

```text
This is the workflow for changing the workflow system.
```

Evidence required:

- Change type named.
- Source of truth selected.
- Connected files checked.
- Required checks run for the changed layer.
- Koda stored, updated, or intentionally skipped.
- Git state reported as discussed, changed locally, committed locally, pushed,
  or adopted.

Exit when the Agent OS change is only discussed, changed locally, committed,
pushed, or parked with a clear return path.

Common failure: treating a local dirty docs change as if future agents already
have the new rule.

## 15. Memory, Save-Session, And Handoff Workflow

Starts when Hafiz asks to save, hand off, compact context, switch agents, pause,
close a meaningful session, or when the work would be hard to resume from chat
alone.

Hafiz owns whether to continue, pause, or close. The agent owns preserving
current state, durable lessons, task status, risks, and exact next step.

Use [save-session.md](save-session.md), Koda CLI when available, and the
handoff/snapshot playbooks when applicable.

Plain meaning:

```text
Save-session and handoff are restart packs, not diaries. The next agent should
know the goal, current focus, highest proven state, evidence, boundaries, and
single next action without rereading the whole chat.
```

Evidence required:

- Current git state.
- Active task state when present.
- What changed and what was checked.
- Koda search/store result or honest failure/fallback.
- Mission Ledger state when relevant.
- Remaining work and next recommended action.
- Continuation Pack details: main goal, current focus, highest proven state,
  dirty/ahead/behind Git state, local-only commits, links/files, evidence gaps,
  approval boundaries, and do-not-redo context.

Exit when the next agent or future session can continue without guessing.

Save to:

- Koda for durable lessons,
- docs/handoff/QA notes when needed,
- mission ledger for future follow-ups,
- final response.

Common failure: storing vague memory noise instead of actionable lessons.

Another common failure: a handoff says "done" but omits that the work is only
committed locally, not pushed, merged, deployed, or live checked.

## 16. Mission Ledger Workflow

Starts when a future task, adjacent idea, paused question, risk, research topic,
or bigger goal should not be lost but is not execution-ready.

Hafiz owns whether to promote it into active work. The agent owns capturing the
context compactly and linking it to the right project and parent mission.

Use [mission-ledger.md](mission-ledger.md).

Evidence required:

- Project, status, type, parent, end goal, why it matters, source, next action,
  promotion target, and links.
- Parent exists for child, adjacent, question, risk, or research items.
- Checker passes before commit.

Exit when the item is captured, promoted, done, dropped, or paused with a clear
next action.

Save to:

- `docs/agent-playbooks/mission-ledger/<project>.md`.

Common failure: the ledger becomes a second GitHub issue tracker instead of a
parking lot for contextual future work.

## 17. Developer Staff Rollout Workflow

Starts when Agent OS is ready to be distributed to developer staff, another LLM,
another machine, or another project.

Hafiz owns rollout scope, developer-staff permissions, training direction, and
who gets what capability. The agent owns making installation, rules, checks,
and support paths clear enough that developer staff can use the system safely.

Ordinary non-developer staff do not use Agent OS by default. They use Microsoft
Teams Planner for bug reports, screenshots, reproduction notes, and support
context.

Use install docs, rollout readiness, capability model, approval gates, and
health checks.

Evidence required:

- Target user group and allowed tools/capabilities.
- Installation path tested.
- Health check passes.
- Developer-staff boundaries documented.
- Training checklist and support escalation path exist.
- Pilot feedback loop defined before broad rollout.

Exit when the pilot group can install, pass health checks, understand what they
may ask the agent to do, and know when to escalate to Hafiz or technical owner.

Save to:

- onboarding docs, install manifest, developer staff quick start, support FAQ, Koda for
  rollout lessons, mission ledger for future improvements.

Common failure: ordinary staff are accidentally pulled into Agent OS instead of
Teams Planner, or developer staff receive powerful tools without clear
capability limits.

## Recommended Use

At the start of meaningful work, the agent should say the route in normal
language, not as a label dump:

```text
This is a staff issue, so I will first treat the report as a symptom, verify
what is actually happening, then route confirmed engineering work through the
normal bugfix path.
```

At close-out, use the practical result:

```text
The workflow draft is updated, the referenced files exist, the guard and health
checks pass, and the next best step is to review work intake in more detail.
```

Formal terms like lane, Gate 2A, Critical Save, or mission ledger are useful for
audits and handoffs, but day-to-day explanations should stay human-readable.
