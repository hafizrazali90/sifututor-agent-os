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
- Use compact control wording for simple work and full control wording for
  bugfixes, features, production, critical lanes, multi-step work, or whenever
  Hafiz may not know the workflow path.
- Before implementation, explain the intended code/workflow change in plain
  English: options, recommendation, what will change, what will not change,
  risks/tradeoffs, and evidence plan.
- Do not treat memory, old chat, staff symptoms, or a screenshot as stronger
  than current code, docs, data, tests, or production evidence.
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
| Bugfix | Full or Critical | Something is broken and needs diagnosis, fix, proof, and close loop. |
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
| Memory, save-session, and handoff | Medium to Critical | Context must survive chat end, compaction, or agent switch. |
| Mission ledger | Light to Medium | Important future work is not ready for GitHub or active task. |
| Staff rollout | Medium | Agent OS is prepared for other staff or another LLM setup. |

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
| `quick explanation` | Small safe changes where a short English explanation is enough before implementation. |
| `design brief` | User workflow, staff process, unclear expected behavior, or multiple implementation options. |
| `full design` | Major workflow, critical lane, multi-role/module work, backend/frontend contract, or handoff to another builder. |

The agent should recommend the lightest safe preparation, but risk can force
deeper preparation. Hafiz can ask for more or less, and the agent should explain
any safety concern in normal language.

Content standard:

- Quick explanation answers what is wrong, what will change, what will not be
  touched, and how it will be checked.
- Design brief explains the problem, current behavior, affected users, options,
  recommendation, tradeoffs, evidence plan, and decision needed.
- Full design maps the workflow/spec/contract/test plan/build prompt before
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

- quick explanation for tiny safe changes
- build-ready brief for real implementation work
- full implementation design for critical lanes, cross-module work, mobile/API
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

## 4. Bugfix Workflow

Starts when something is broken, failing, confusing, or reported as not working.

Hafiz owns business acceptance and risk decisions. The agent owns reproduction,
root-cause diagnosis, implementation after the right approval, regression
coverage, verification, QA, and review.

Use [diagnose.md](diagnose.md), then build only after the scope and approval
are clear. If the bug touches a critical domain, route through the Critical Lane
workflow first.

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
- Focused test that fails before or would have caught the bug, where feasible.
- Permanent E2E regression decision for user-facing workflows.
- Agent-run human-journey proof when safe.

Scenario:

| Staff says | Agent should do |
| --- | --- |
| `The invoice button does nothing` | Treat this as a symptom first. Identify the page, role, and expected action; check current code/browser/API/log evidence where safe; explain the likely cause and planned fix in English; fix the smallest cause; add or update a regression test; run focused checks; use browser or Playwright proof when feasible; then report what changed, what was checked, what remains, and the recommended next action. |

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

Exit when the changed behavior is proven, failures are separated into baseline
vs task-caused, or a named blocker prevents honest verification.

Save to:

- final answer, PR body, QA notes, TESTING.md, or task state as appropriate.

Common failure: unit tests pass but the user journey is still untested.

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
- Clear list of untested areas and why.

Exit when the journey is QA-passed, blocked with a specific reason, or handed
to Hafiz/staff for the parts only they can judge.

Save to:

- QA docs, screenshots/evidence paths where used, PR body, TESTING.md, final
  close-out.

Common failure: "manual QA needed" becomes a shortcut for checks the agent
could have done itself.

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

Exit when the requested git action is completed, refused for safety, or waiting
for exact approval.

Save to:

- git commit SHA, pushed branch/PR URL when created, final state, Koda only for
  durable workflow lessons.

Common failure: local-only work is described as done without saying it is not
pushed, merged, or live.

## 13. Release, Deploy, And Monitor Workflow

Starts when merged or approved work needs to reach staging/production, or Hafiz
explicitly asks to deploy/release/monitor.

Hafiz owns production approval and final risk acceptance. The agent owns
preflight, deploy execution only after approval, smoke checks, monitoring, and
clear live-state reporting.

Use project deploy docs plus [monitor-production-logs.md](monitor-production-logs.md).
Do not deploy from this master workflow alone.

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

## 17. Staff Rollout Workflow

Starts when Agent OS is ready to be distributed to staff, another LLM, another
machine, or another project.

Hafiz owns rollout scope, staff permissions, training direction, and who gets
what capability. The agent owns making installation, rules, checks, and support
paths clear enough that staff can use the system safely.

Use install docs, rollout readiness, capability model, approval gates, and
health checks.

Evidence required:

- Target user group and allowed tools/capabilities.
- Installation path tested.
- Health check passes.
- Staff-safe boundaries documented.
- Training checklist and support escalation path exist.
- Pilot feedback loop defined before broad rollout.

Exit when the pilot group can install, pass health checks, understand what they
may ask the agent to do, and know when to escalate to Hafiz or technical owner.

Save to:

- onboarding docs, install manifest, staff quick start, support FAQ, Koda for
  rollout lessons, mission ledger for future improvements.

Common failure: staff receive powerful tools without clear capability limits,
or they receive too much process and stop using the system.

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
