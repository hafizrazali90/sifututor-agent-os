# Agent OS Review Roadmap

Use this document to review the Sifututor Agent OS one layer at a time with
Hafiz.

The purpose is to make the Agent OS fit how Hafiz actually wants Codex and
Claude to work with him. Staff rollout comes later.

## Why This Exists

We started with the right question: how should Hafiz and agents work together
without causing frustration or adding too much ceremony?

During the first build pass, we also created useful rollout pieces such as an
installer and staff quick start. Those are valuable, but the core remains the
internal Hafiz-Agent operating model.

The core is still the Hafiz-Agent operating model:

- how Hafiz gives instructions
- how agents decide whether to discuss, act, ask, verify, commit, or push
- how approval should work
- how much explanation is helpful
- how memory should prevent repeated mistakes
- how the system should make Hafiz stop needing to ask "what next?"

## Current Agent OS State

This section is the inventory. It answers: what exists today, what each layer is
supposed to do, where it lives, and what still needs review.

## Architecture Map

| Layer | What It Should Do | Current Assets | Current Weakness | Improve Or Add |
| --- | --- | --- | --- | --- |
| Human operating model | Define how Hafiz and agents work together day to day | `AGENTS.md` communication rules, close-out standard | Not explicit enough; too much reactive "what next" behavior | `working-with-hafiz.md`, examples, preference matrix |
| Intent router | Convert Hafiz's prompt into the right lane | `task-router.md`, Codex lifecycle hook, eval notes | Ambiguous prompts still need clearer semantics | routing matrix, more evals, examples for `approve`, `proceed`, `what next` |
| Context authority | Decide what is true enough to act on | `context-authority.md` | Needs real Sifututor examples and source-of-truth ownership | source map, conflict examples, promotion checklist |
| Memory | Store only durable lessons and corrections | Koda, `agent-os-memory.md`, `save-session.md` | Koda MCP timeout path needs better handling | memory reliability plan, fallback standard, dedup rules |
| Workflow lanes | Define routes for discussion, design, diagnosis, build, QA, review, commit, save | playbooks and Codex skills | Some lanes feel heavy during discussion | lane simplification, "light mode" rules |
| Approval gates | Prevent risky actions without Hafiz approval | `AGENTS.md`, `commit.md`, hooks, guard scripts | `approve` can be ambiguous if prior step is unclear | approval matrix, approval scope examples |
| Tool capability model | Say what the current agent can actually access | `agent-os-health.sh`, capability example | Capability is conservative and not deeply modeled | capability matrix, connected-tool report, risk by tool |
| Verification and evidence | Prove work is correct at the right strength | `verify.md`, `qa.md`, E2E rules, doctor scripts | Evidence level can be hard to choose quickly | evidence matrix by work type |
| Task/state model | Show where current work, decisions, and status live | GitHub, Plane, Planner, active task files, ledger | State is powerful but scattered | state source-of-truth map |
| Distribution/staff | Let staff use the OS safely later | installer, install guide, staff quick start, readiness ladder | Needs pilot templates and real staff trial later | keep internal-first; expand through readiness levels |
| Evaluation | Test whether Agent OS behavior is improving | `agent-os-evals.md` | Mostly Markdown cases; not yet run as a suite | eval checklist, scripted smoke cases |
| Architecture documentation | Keep the map of what exists and what changes | this roadmap | New; needs review with Hafiz | decision log, touch map, review register |

## Architecture Principles To Review

These principles come from the earlier research and from our own mistakes so
far. Review them explicitly before changing more files.

1. **Internal first, staff later**
   - Hafiz-Agent workflow must work before staff rollout expands.
   - Existing installer/staff docs are useful but parked.

2. **Capability beats role label**
   - "Codex", "Claude", and "staff" are not security boundaries.
   - Real boundaries are connected tools, credentials, filesystem, and approval.

3. **Light where conversation is exploratory**
   - Discussion, learning, architecture review, and retrospective prompts should
     not trigger heavy implementation or commit machinery.

4. **Strict where mistakes are expensive**
   - Auth, payment, invoices, commissions, migrations, deploys, mobile API
     contracts, secrets, and production access need stronger gates.

5. **Versioned docs over private chat memory**
   - Architecture decisions should land in docs or Koda, not vanish in chat.

6. **Memory is distilled, not dumped**
   - Koda stores durable corrections and lessons.
   - It does not store raw transcripts or vague progress.

7. **Every layer needs a source of truth**
   - If a rule exists in many places, one file should be named as the source and
     the others should link to it or be generated from it.

8. **Every review should produce a trace**
   - We should know what topic was reviewed, what decision was made, which files
     changed, and what remains unresolved.

## Review Register

Use this as the master tracker while reviewing the architecture.

| # | Review Area | Source Files To Read | Likely Files To Update | Status | Output |
| --- | --- | --- | --- | --- | --- |
| 1 | Hafiz-Agent Working Model | `AGENTS.md`, `agent-os.md`, this roadmap, Koda corrections | `working-with-hafiz.md`, `AGENTS.md`, `agent-os-evals.md` | Draft accepted | personal operating model |
| 2 | Intent Routing | `task-router.md`, `agent-os-evals.md`, `codex-lifecycle-hook.py` | `agent-os-routing-model.md`, `task-router.md`, `agent-os-evals.md`, hook script later | Draft accepted | routing matrix and prompt examples |
| 3 | Approval Gates | `AGENTS.md`, `commit.md`, `review.md`, `agent-os-quick-start.md` | `agent-os-approval-gates.md`, `working-with-hafiz.md`, `agent-os-evals.md` | Draft accepted for Agent OS/docs | approval matrix |
| 4 | Communication And Close-Out | `AGENTS.md`, `README.md`, playbook reports | `agent-os-communication.md`, `working-with-hafiz.md`, `AGENTS.md`, playbooks | Draft accepted | answer/update examples |
| 5 | Context Authority | `context-authority.md`, Koda memories, task-state docs | `context-authority.md`, evals | Draft accepted | source and confidence examples |
| 6 | Memory System | `agent-os-memory.md`, `save-session.md`, Koda behavior | `agent-os-memory.md`, `agent-os-memory-architecture.md`, `save-session.md`, evals | Draft accepted | memory reliability and v2 architecture plan |
| 7 | Tool Capability Model | `capabilities.example.json`, `agent-os-health.sh`, installer | `agent-os-capability-model.md`, `capabilities.example.json`, `agent-os-health.sh`, evals | Draft accepted | capability matrix |
| 8 | Workflows And Lanes | all core playbooks and skills | `agent-os-workflow-lanes.md`, `task-router.md`, evals | Draft accepted | lane intensity model |
| 9 | Verification And Evidence | `verify.md`, `qa.md`, `test-coverage.md`, past QA docs | `agent-os-evidence-model.md`, verify/QA/test-coverage/review docs, evals | Draft accepted | agent-as-tester evidence model |
| 10 | GitHub/Plane/Planner/Task State | `task-router.md`, `plane.md`, session ledger, active-task docs | `agent-os-state-model.md`, task/router/Plane/save-session/ledger docs, evals | Draft accepted | state source map |
| 11 | Staff Rollout Readiness | install docs, staff quick start, research note | `agent-os-rollout-readiness.md`, installer manifest, staff docs, evals | Draft accepted | readiness ladder |
| 12 | Save Session And Handoff Quality | `save-session.md`, `handoff.md`, `snapshot.md`, `session-map.md` | save-session/handoff/snapshot docs, workflow docs, evals | Draft accepted | continuation pack standard |
| 13 | Implementation Readiness And Build Handoff Quality | `ai-implementation-readiness.md`, `product-design.md`, `agent-os-workflows.md` | readiness/product/workflow docs, evals | Draft accepted | build-ready brief standard |
| 14 | Enforcement And Drift Detection | `agent-os-hook-dispatcher.md`, `agent-os-skill-registry.md`, `agent-os-parity-contract.md`, health/eval scripts | enforcement docs, infrastructure, hook/parity docs, evals | Draft accepted | enforcement ladder and drift map |
| 15 | Agent OS Improvement Loop | `agent-os-enforcement-drift.md`, `agent-os-memory.md`, `agent-os-skill-registry.md`, evals, Koda corrections | `agent-os-improvement-loop.md`, workflow-improvement skill, task-router, workflow map, evals | Draft accepted for Track A | controlled self-learning workflow |

## Touch Map

Use this to avoid scattering changes across the wrong files.

| If Reviewing | Primary Source Of Truth | Secondary Files |
| --- | --- | --- |
| Global rules every agent must obey | `AGENTS.md` | project `AGENTS.md`, `CLAUDE.md` |
| Claude-specific deep context | `CLAUDE.md` | project `CLAUDE.md` |
| How Hafiz wants agents to collaborate | planned `working-with-hafiz.md` | `AGENTS.md`, `agent-os.md`, evals |
| Route selection | `task-router.md` | Codex lifecycle hook, skills, evals |
| Prompt classification model | `agent-os-routing-model.md` | `task-router.md`, lifecycle hook, evals |
| Approval gates and work packets | `agent-os-approval-gates.md` | `working-with-hafiz.md`, `AGENTS.md`, evals |
| Communication and close-out style | `agent-os-communication.md` | `working-with-hafiz.md`, `AGENTS.md`, `README.md`, evals |
| Product design workflow | `product-design.md` | product-design skill |
| Verification | `verify.md` | project verify skills, scripts |
| QA | `qa.md` | test coverage docs, project QA skills |
| Review | `review.md` | commit playbook, evals |
| Commit rules | `commit.md` | `AGENTS.md`, hooks |
| Save-session and Koda | `save-session.md`, `agent-os-memory.md` | Koda memories, fallback notes |
| Memory architecture and performance | `agent-os-memory-architecture.md` | `agent-os-memory.md`, `save-session.md`, evals, future audit script |
| Tool and capability model | `agent-os-capability-model.md` | `capabilities.example.json`, `agent-os-health.sh`, quick-check, evals |
| Enforcement and drift detection | `agent-os-enforcement-drift.md` | hook dispatcher, skill registry, parity contract, evals, health checks |
| Agent OS self-improvement and workflow cleanup | `agent-os-improvement-loop.md` | task router, skill registry, workflow map, evals, Koda, Session Map |
| Workflow lane intensity | `agent-os-workflow-lanes.md` | `task-router.md`, evals, specific lane playbooks |
| Verification and human-journey evidence | `agent-os-evidence-model.md` | `verify.md`, `qa.md`, `test-coverage.md`, `review.md`, evals |
| Task and release state | `agent-os-state-model.md` | `task-router.md`, `plane.md`, `session-release-ledger.md`, `save-session.md`, evals |
| Staff rollout readiness | `agent-os-rollout-readiness.md` | `agent-os-installation.md`, `agent-os-staff-quick-start.md`, install manifest, health check, evals |
| Context accuracy | `context-authority.md` | task router, evals |
| Capability/connected tools | `capabilities.example.json`, `agent-os-health.sh` | installer, quick-check |
| Staff install | `agent-os-installation.md`, install manifest | staff quick start, installer |
| Staff onboarding | `agent-os-staff-quick-start.md` | templates later |
| Architecture review state | this roadmap | issue tracker, Koda corrections |

## Decision Log

Record architecture decisions here until a more specific source-of-truth file is
created.

| Date | Decision | Why | Follow-Up |
| --- | --- | --- | --- |
| 2026-06-04 | Staff rollout assets are parked until the Hafiz-Agent operating model is reviewed. | We started building distribution before discussing the architecture deeply enough. | Start review with Hafiz-Agent Working Model. |
| 2026-06-04 | Future Agent OS planning must document architecture, current assets, gaps, touched files, and review order before implementation. | Hafiz corrected reactive planning; future sessions need a stable map. | Keep this roadmap updated and store durable corrections in Koda. |
| 2026-06-04 | The first architecture review output is a draft `working-with-hafiz.md` playbook, not staff rollout. | The personal operating model is the missing core of the Agent OS. | Review the draft with Hafiz before marking it stable. |
| 2026-06-04 | Hafiz accepted the Working With Hafiz draft preferences: `proceed` acts on the last clear recommendation; bundled approvals are allowed when the agent asks for the bundle; architecture discussion should be back-and-forth with a living draft; wrong order should be softly challenged; final answers should be summary + checks + next step. | This reduces repeated nagging, preserves Hafiz's decisions, and makes agent behavior less reactive. | Update routing and approval evals next. |
| 2026-06-04 | Koda should store mistakes only when they should change future agent behavior; safe one-approval bundles are allowed for exact low/medium-risk adjacent actions, while critical/deploy/destructive/secret/production actions stay separate. | This gives the agent useful memory without turning Koda into a noisy transcript archive, and reduces approval nagging without weakening high-risk gates. | Add routing/approval evals for bundled approvals and Koda mistake saves. |
| 2026-06-04 | Intent Routing review drafted `agent-os-routing-model.md` as the source model before changing router code. | Router behavior should follow a reviewed model rather than keyword improvisation. | Review open questions about last-recommendation and approval-bundle state before hook changes. |
| 2026-06-04 | Approval Gates review accepts relaxed work-packet approval for Agent OS/docs/workflow work first. | Hafiz wants fewer repeated approvals during safe architecture/docs work, while commit/push, deploy, production, secrets, destructive actions, and critical lanes stay strict. | Use `agent-os-approval-gates.md` as the source of truth and test it with routing/approval evals. |
| 2026-06-04 | Communication and Close-Out review accepts natural plain-language reporting as the default. | Hafiz wants explanations to feel like code translated into normal language, with easier non-technical explanations when needed. Formal labels should be avoided unless they are useful for audit trail, handoff, QA, commit records, or teaching terminology. | Use `agent-os-communication.md` as the source of truth and add evals for label translation and simple explanations. |
| 2026-06-04 | Context Authority review accepts the ladder model: forbidden boundaries, Hafiz decisions, current verified evidence, approved docs, task systems, memory/history, then agent assumptions. | This prevents agents from treating reported symptoms, old memory, prior chat, or assumptions as current truth. | Update context evals and apply the ladder before high-risk or user-facing work. |
| 2026-06-04 | Memory System review accepts Memory Architecture v2: docs store the system, Koda stores lessons, chat stores the moment, and git stores proof. | Hafiz asked whether the whole memory structure should be upgraded to improve performance, not only patched with fallbacks. | Use v2 taxonomy for new memories, add lifecycle/risk tags, and plan a read-only memory audit before migration. |
| 2026-06-04 | Tool and Capability Model review accepts the Capability Manifest model. | Capability depends on connected tools, credentials, filesystem access, approval gates, and forbidden boundaries, not role labels like Codex, Claude, or staff. | Report capability as available, fallback, unknown, not_connected, blocked, or forbidden. |
| 2026-06-05 | Workflows and Lanes review accepts the Lane Intensity Model: Light, Medium, Full, and Critical. | This matches current agent best practice: route by task type, use guardrails by risk, avoid approval fatigue, and keep critical domains strict. | Use `agent-os-workflow-lanes.md` as the source and refine individual lane playbooks through real use. |
| 2026-06-05 | Verification and Evidence review accepts the Agent-As-Tester Evidence Model. | Hafiz wants agents to be the bridge between him and coding, including tester work the agent can safely perform. Testing should validate the same observable workflow a human tester would validate, while Hafiz verifies business judgment, unavailable access, destructive actions, and final risk acceptance. | Use `agent-os-evidence-model.md` as the source and make verify/QA/review enforce human-journey evidence. |
| 2026-06-29 | Verification, QA, and Evidence accepts the Proof Standard. | Hafiz needs the agent to distinguish code proof, journey proof, and release proof so "tests passed" is not mistaken for "users can do it" or "it is live." | Use `agent-os-evidence-model.md`, `verify.md`, `qa.md`, `review.md`, and workflow close-outs to report the highest proven state. |
| 2026-06-05 | GitHub/Plane/Planner/Task State review accepts the State Model. | Hafiz needs agents to stop using vague "done" language when work may only be local, pushed, PR-open, merged, deployed, or live-smoke-passed. Each tool should own a specific kind of truth. | Use `agent-os-state-model.md` as the source for state language and source-of-truth ownership. |
| 2026-06-29 | Task State and Work Tracking accepts the State Ownership Rule. | Hafiz needs agents to use the right source for the right question instead of treating Planner, Koda, chat, GitHub, git, deploy records, and QA evidence as interchangeable truth. | Use `agent-os-state-model.md`, `task-router.md`, and `agent-os-workflows.md` before trusting or updating task state. |
| 2026-06-05 | Staff Rollout Readiness review accepts the readiness ladder: internal Agent OS, project baseline, staff-safe kit, approved builder kit, advanced operations. | Staff rollout should not mean giving every person every tool. The safe path is internal-first, then staff reporting/QA/docs, then code builder access only for trusted users, and advanced operations only by explicit approval. | Use `agent-os-rollout-readiness.md` before installing or expanding staff capabilities. |
| 2026-06-29 | Work Intake and Task State review accepts quick diagnosis before GitHub issue creation or implementation. | Hafiz wants traceability without noise: agents should not create GitHub issues from vague symptoms too early, but should not start real coding work with no trace. | Use `agent-os-state-model.md`, `task-router.md`, and `agent-os-workflows.md` for intake routing. |
| 2026-06-29 | Review and Risk Before Commit/Push accepts a risk checkpoint before outward state changes. | Hafiz needs the agent to catch scope creep, missing evidence, state confusion, critical-lane gaps, release communication gaps, multi-fix confusion, and product/business risk before commit, push, PR, merge, or deploy. | Use `review.md`, `commit.md`, and `agent-os-workflows.md` before saying the next state is safe. |
| 2026-06-29 | Save Session and Handoff Quality accepts the Continuation Pack standard. | Hafiz needs long sessions, compacted context, and agent-to-agent handoffs to resume from the main goal, current focus, highest proven state, evidence, boundaries, and next action instead of forcing the next agent to rediscover everything. | Use `save-session.md`, `handoff.md`, `snapshot.md`, and Session Maps when sessions need continuity. |
| 2026-06-29 | Implementation Readiness and Build Handoff Quality accepts the build-ready brief standard. | Hafiz needs to understand intended code behavior in plain English before coding starts, and future builders need enough context to find the real entry point, preserve the business rule, prove the right behavior, and stop at the approved boundary. | Use `ai-implementation-readiness.md`, `product-design.md`, and `agent-os-workflows.md` before non-trivial implementation or build handoff. |
| 2026-06-29 | Enforcement and Drift Detection accepts the enforcement ladder. | Hafiz needs Agent OS rules to be followed without turning every preference into brittle hook automation. Dangerous actions need hard blocks, workflow behavior needs skills/playbooks, repeated drift needs evals, wiring needs health checks, current story needs Session Map, and durable lessons need Koda. | Use `agent-os-enforcement-drift.md` to choose the right layer before changing hooks, skills, evals, or memory. |

### Core Operating Layer

Already present:

- root `AGENTS.md` as the shared operating contract
- project-specific `AGENTS.md` and `CLAUDE.md` files
- Agent OS overview: [agent-os.md](agent-os.md)
- fresh-session quick start: [agent-os-quick-start.md](agent-os-quick-start.md)
- internal build plan: [agent-os-internal-build-plan.md](agent-os-internal-build-plan.md)
- research notes: [agent-os-research.md](agent-os-research.md)
- context authority rules: [context-authority.md](context-authority.md)
- memory discipline: [agent-os-memory.md](agent-os-memory.md)
- eval cases: [agent-os-evals.md](agent-os-evals.md)

Practical meaning: we have the written skeleton for how the Agent OS should
think, route, verify, remember, and close out.

### Workflow Playbooks

Already present:

- task routing
- product design
- diagnosis
- verification
- QA
- review
- commit
- save-session
- handoff
- snapshot
- production log monitoring
- Plane mission-board guidance
- test coverage manifest guidance
- session release ledger

Practical meaning: most repeated work routes have a source-of-truth playbook.

### Codex And Claude Parity

Already present:

- Codex skill wrappers under `.agents/skills/`
- shared Markdown playbooks under `docs/agent-playbooks/`
- Codex lifecycle hook scripts
- Claude/Codex switching guidance
- quick-check workflow
- workflow doctor

Practical meaning: Codex can follow much of the same workflow Claude follows,
even when Claude-specific skills are not directly callable.

### Guardrails And Checks

Already present:

- `scripts/agent-checks/pre-commit-guard.sh`
- `scripts/agent-checks/workflow-doctor.sh`
- `scripts/agent-checks/agent-os-health.sh`
- `scripts/agent-checks/agent-os-install.sh`
- sensitive path checks
- branch-name checks
- active-task checks
- test coverage manifest checker
- critical-lane rules in `AGENTS.md`

Practical meaning: the OS has basic safety checks for local work, commits,
workflow drift, and install readiness.

### Memory

Already present:

- Koda direct health checks
- Koda memory rules in `AGENTS.md`
- Agent OS memory discipline in [agent-os-memory.md](agent-os-memory.md)
- save-session playbook
- session save fallback note from 2026-06-04

Known issue:

- chat-level Koda MCP calls can time out even when direct Koda health passes.

Practical meaning: Koda is part of the OS, but the save path still needs a
reliability review.

### Staff Rollout Pieces

Already present:

- install manifest
- installer/checker
- installation guide
- staff quick start

Current decision:

- staff rollout follows the readiness ladder in
  [agent-os-rollout-readiness.md](agent-os-rollout-readiness.md)
- keep expanding internal reliability first
- start staff later with the staff-safe kit, not full tool access

Practical meaning: we have early distribution assets and a rollout model, but
real staff rollout should wait for a pilot plan and templates.

## Review Order

Review these in order. Each review should end with one of three outcomes:

- keep as-is
- change the Agent OS rule/playbook/script
- mark as unresolved and create a follow-up issue

### 1. Hafiz-Agent Working Model

Question: how should Codex/Claude work with Hafiz day to day?

Review:

- how Hafiz uses short commands like `ok`, `approve`, `proceed`, and
  `what next`
- when the agent should act immediately
- when the agent should stop and discuss
- when the agent should ask for clarification
- how much analysis Hafiz wants before execution
- what final answer shape feels helpful instead of heavy

Output:

- create or update a `working-with-hafiz` playbook
- add examples of good and bad agent behavior

### 2. Intent Routing

Question: how does the OS know whether the user wants discussion, planning,
implementation, verification, commit, push, or save-session?

Review:

- discussion prompts
- research prompts
- retrospective prompts
- `proceed`
- `approve`
- `what next`
- commit and push prompts
- critical-lane prompts

Output:

- update task router and lifecycle hook rules
- add eval cases for ambiguous prompts

### 3. Approval Gates

Question: what can agents decide alone, and what must Hafiz approve?

Review:

- file edits
- commits
- pushes
- PRs
- merges
- deploys
- GitHub issue creation
- Plane updates
- Koda memories
- critical-lane diagnosis versus implementation

Output:

- approval matrix for low, medium, high, and critical actions

### 4. Communication And Close-Out

Question: how do agents keep Hafiz informed without making him read process
noise?

Review:

- plain-language explanation
- status updates while working
- final answer format
- when to include file paths and commands
- how to avoid making Hafiz ask "what next?"
- when workflow labels are useful versus annoying

Output:

- refine the mandatory close-out standard
- add example close-outs for docs, bugs, QA, commits, and blocked work

### 5. Context Authority

Question: how does the OS decide what is true enough to act on?

Review:

- Koda memory
- prior chat/session notes
- GitHub issues
- Plane cards
- Planner/staff reports
- screenshots
- code/tests
- external research

Output:

- update [context-authority.md](context-authority.md)
- add examples from real Sifututor work

### 6. Memory System

Question: what should be remembered, where, and by whom?

Review:

- Koda as episodic memory
- docs as semantic/procedural memory
- task files as working state
- save-session fallback
- duplicate memory prevention
- what staff should or should not remember

Output:

- update [agent-os-memory.md](agent-os-memory.md)
- decide how to handle Koda MCP timeouts

### 7. Tool And Capability Model

Question: what matters more, agent role or connected tools?

Review:

- Codex capabilities
- Claude capabilities
- GitHub CLI
- Koda
- Plane
- Planner
- Google Drive
- production logs
- deploy tools

Output:

- update capability manifest guidance
- make health checks clearer about what is connected now versus assumed

### 8. Workflows And Lanes

Question: are the workflow routes right for real Sifututor work?

Review:

- discussion / learning
- product design
- diagnosis
- small change
- normal engineering
- critical lane
- verify
- QA
- review
- commit
- save-session
- handoff

Output:

- update playbooks that feel too heavy or too loose
- identify missing workflow routes

### 9. Verification, QA, And Evidence

Question: how much proof is enough for each kind of work?

Decision: use the Proof Standard. Separate code proof, journey proof, and
release proof, then report the highest proven state.

Review:

- docs-only changes
- workflow/script changes
- UI behavior
- backend/API behavior
- mobile behavior
- user-facing E2E decisions
- production health checks

Output:

- refine verify/QA playbooks
- add examples of acceptable evidence by task type

### 10. GitHub, Plane, Planner, And Task State

Question: what belongs where so Hafiz does not have to reconstruct status from
chat?

Decision: use the State Ownership Rule. Every source gets one job; use the
source that owns the question and report the highest proven state.

Review:

- GitHub issue creation
- Plane mission board updates
- Planner as staff intake
- `.claude/tasks/active.json`
- session release ledger
- commit/push state

Output:

- source-of-truth map for task state
- decide when automatic issue creation is helpful versus noisy

### 11. Staff Rollout Readiness

Question: when is the Agent OS good enough to distribute?

This has a draft decision now. Use
[agent-os-rollout-readiness.md](agent-os-rollout-readiness.md) as the source
before expanding staff access.

Review:

- installer
- staff quick start
- templates
- staff permission profiles
- local memory fallback
- tool-specific shims
- examples for support, QA, developer, and product/design staff

Output:

- staff rollout plan
- starter-kit templates
- onboarding checklist

## Review Session Format

Each review session should use this shape:

```text
Topic:
<one review area>

Current rule:
<what the Agent OS says now>

What Hafiz wants:
<preference, frustration, or correction>

Decision:
<keep / change / unresolved>

Update needed:
<docs, hook, skill, script, memory, issue, or none>

Next:
<single next review topic>
```

## Per-Review Worksheet

When reviewing a layer, fill this in before changing files.

```text
Review area:
<one layer from the review register>

Why this layer matters:
<plain-language reason>

Current behavior:
<what Codex/Claude/system does today>

Current assets:
<docs, scripts, hooks, skills, memories, issues>

Hafiz friction:
<what feels frustrating, slow, unclear, or unsafe>

Research principle:
<relevant principle from agent-os-research.md or external source>

Gap:
<missing, weak, too strict, too loose, duplicated, or unclear>

Options:
1. <option>
2. <option>
3. <option>

Recommendation:
<agent recommendation, with tradeoff>

Hafiz decision:
<approved, rejected, changed, unresolved>

Files to touch:
<exact file list>

Verification:
<health check, eval, guard, doc review, script test>

Memory:
<Koda store/update/skip and why>

Next review:
<one next topic>
```

## Review Completion Rule

A review area is not done until all of these are true:

- the current behavior is documented
- Hafiz's preference or correction is captured
- the decision is written down
- touched files are listed
- checks are named
- Koda is stored, updated, or intentionally skipped
- the next review topic is stated

## Decision Log

| Date | Decision | Why it matters | Use it |
| --- | --- | --- | --- |
| 2026-06-29 | Session Map Lifecycle accepts the one meaningful session, one map rule. | Hafiz needs parallel and long-running sessions to stay understandable without duplicate maps for the same mission or one map stretched across unrelated work. | Use `session-map.md` lifecycle states and split rules before creating, reusing, parking, handing off, promoting, or closing a Session Map. |

## Immediate Next Review

Continue with section 9: **Verification, QA, And Evidence**.

Reason: we have drafted the personal working model, intent routing, approval
gates, communication style, context authority, memory system, and capability
model, and workflow lanes. The next friction point is deciding how much proof
is enough for each type of work.
