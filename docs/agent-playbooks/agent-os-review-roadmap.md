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
| 11 | Developer Staff Rollout Readiness | install docs, developer staff quick start, research note | `agent-os-rollout-readiness.md`, installer manifest, developer staff docs, evals | Draft accepted | readiness ladder |
| 12 | Save Session And Handoff Quality | `save-session.md`, `handoff.md`, `snapshot.md`, `session-map.md` | save-session/handoff/snapshot docs, workflow docs, evals | Draft accepted | continuation pack standard |
| 13 | Implementation Readiness And Build Handoff Quality | `ai-implementation-readiness.md`, `product-design.md`, `agent-os-workflows.md` | readiness/product/workflow docs, evals | Draft accepted | build-ready brief standard |
| 14 | Enforcement And Drift Detection | `agent-os-hook-dispatcher.md`, `agent-os-skill-registry.md`, `agent-os-parity-contract.md`, health/eval scripts | enforcement docs, infrastructure, hook/parity docs, evals | Draft accepted | enforcement ladder and drift map |
| 15 | Agent OS Improvement Loop | `agent-os-enforcement-drift.md`, `agent-os-memory.md`, `agent-os-skill-registry.md`, evals, Koda corrections | `agent-os-improvement-loop.md`, workflow-improvement skill, task-router, workflow map, evals | Draft accepted for Track A | controlled self-learning workflow |
| 16 | Project Related-Impact Audit | `diagnose.md`, `verify.md`, `qa.md`, `review.md`, bugfix workflow, Koda bug-pattern memories | `related-impact-audit.md`, diagnose/verify/QA/review/workflow docs, evals | Draft accepted for Track B | daily bugfix related-impact standard |
| 17 | Push / PR / Release Lifecycle | `commit.md`, `review.md`, `agent-os-state-model.md`, session ledger, GitHub/PR workflow docs | `push-pr-ci-automation.md`, `workflow-efficiency-audit.md`, approval/workflow/eval docs | Draft accepted | PR-ready boundary and workflow efficiency audit |
| 18 | Release / Deploy / Live Monitoring | `monitor-production-logs.md`, `agent-os-evidence-model.md`, `agent-os-state-model.md`, project deploy docs | `release-deploy-live-monitoring.md`, approval/workflow/eval docs | Draft accepted | post-merge state ladder and production-monitored boundary |
| 19 | Incident Workflow | `monitor-production-logs.md`, `agent-os-evidence-model.md`, `related-impact-audit.md`, critical-lane rules | `incident-workflow.md`, workflow/eval/docs | Draft accepted | protection-first incident path and postmortem standard |
| 20 | Project Adoption | install docs, rollout readiness, product `AGENTS.md`/`CLAUDE.md`, workflow doctor | `project-adoption.md`, install/readiness/workflow docs, health/manifest/evals | Draft accepted | shared core plus local project profile |
| 21 | Governance and Versioning | review roadmap, research update procedure, improvement loop, evals, health/manifest | `agent-os-governance.md`, workflow/docs/evals/health/manifest | Draft accepted | Agent OS change-control workflow |
| 22 | Evaluation Harness | eval coverage map, eval table, local fixture runners, health, workflow doctor | `agent-os-evaluation-harness.md`, response/state fixtures, coverage docs, health/manifest | Draft accepted | harness layers and first stronger local fixtures |
| 23 | Multi-Agent And Adapter Workflow | parity contract, roles, switching docs, handoff/save-session, skill registry, coverage audit | `multi-agent-adapter-workflow.md`, parity/roles/switching links, health/manifest | Draft accepted | stage-first worker selection |

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
| Agent OS governance and versioning | `agent-os-governance.md` | `AGENTS.md`, `agent-os.md`, workflow map, specific playbook, skills, hooks, evals, health, install manifest, Koda, Session Map |
| Agent OS evaluation harness | `agent-os-evaluation-harness.md` | `agent-os-evals.md`, eval coverage map, fixture runners, health, workflow doctor, governance |
| Multi-agent and adapter workflow | `multi-agent-adapter-workflow.md` | parity contract, roles, switching, handoff, save-session, skill registry, evals |
| Workflow lane intensity | `agent-os-workflow-lanes.md` | `task-router.md`, evals, specific lane playbooks |
| Verification and human-journey evidence | `agent-os-evidence-model.md` | `verify.md`, `qa.md`, `test-coverage.md`, `review.md`, evals |
| Related issue and regression impact after fixes | `related-impact-audit.md` | `diagnose.md`, `verify.md`, `qa.md`, `review.md`, bugfix workflow, evals |
| Task and release state | `agent-os-state-model.md` | `task-router.md`, `plane.md`, `session-release-ledger.md`, `save-session.md`, evals |
| Developer staff rollout readiness | `agent-os-rollout-readiness.md` | `agent-os-installation.md`, `agent-os-staff-quick-start.md`, install manifest, health check, evals |
| Project adoption by product repo | `project-adoption.md` | install docs, rollout readiness, product `AGENTS.md`, product `CLAUDE.md`, workflow doctor, evals |
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
| 2026-06-05 | Staff Rollout Readiness review accepted an early readiness ladder, later corrected on 2026-06-29. | The early draft mixed ordinary staff intake with developer-staff Agent OS rollout. | Superseded by the 2026-06-29 correction: ordinary staff use Teams Planner only; Agent OS rollout is for developer staff. |
| 2026-06-29 | Work Intake and Task State review accepts quick diagnosis before GitHub issue creation or implementation. | Hafiz wants traceability without noise: agents should not create GitHub issues from vague symptoms too early, but should not start real coding work with no trace. | Use `agent-os-state-model.md`, `task-router.md`, and `agent-os-workflows.md` for intake routing. |
| 2026-06-29 | Review and Risk Before Commit/Push accepts a risk checkpoint before outward state changes. | Hafiz needs the agent to catch scope creep, missing evidence, state confusion, critical-lane gaps, release communication gaps, multi-fix confusion, and product/business risk before commit, push, PR, merge, or deploy. | Use `review.md`, `commit.md`, and `agent-os-workflows.md` before saying the next state is safe. |
| 2026-06-29 | Save Session and Handoff Quality accepts the Continuation Pack standard. | Hafiz needs long sessions, compacted context, and agent-to-agent handoffs to resume from the main goal, current focus, highest proven state, evidence, boundaries, and next action instead of forcing the next agent to rediscover everything. | Use `save-session.md`, `handoff.md`, `snapshot.md`, and Session Maps when sessions need continuity. |
| 2026-06-29 | Implementation Readiness and Build Handoff Quality accepts the build-ready brief standard. | Hafiz needs to understand intended code behavior in plain English before coding starts, and future builders need enough context to find the real entry point, preserve the business rule, prove the right behavior, and stop at the approved boundary. | Use `ai-implementation-readiness.md`, `product-design.md`, and `agent-os-workflows.md` before non-trivial implementation or build handoff. |
| 2026-06-29 | Enforcement and Drift Detection accepts the enforcement ladder. | Hafiz needs Agent OS rules to be followed without turning every preference into brittle hook automation. Dangerous actions need hard blocks, workflow behavior needs skills/playbooks, repeated drift needs evals, wiring needs health checks, current story needs Session Map, and durable lessons need Koda. | Use `agent-os-enforcement-drift.md` to choose the right layer before changing hooks, skills, evals, or memory. |
| 2026-06-29 | Push / PR / Release Lifecycle accepts PR-ready automation. | Hafiz approves PR open and CI pass most of the time, so agents should bundle mechanical GitHub work after one clear boundary instead of asking for every micro-step. Authority decisions such as merge, deploy, production, destructive actions, and critical lanes still need the approved stop point. | Use `push-pr-ci-automation.md`, `workflow-efficiency-audit.md`, and approval-gate evals before automating outbound workflow steps. |
| 2026-06-29 | Release / Deploy / Live Monitoring accepts the post-merge state ladder. | Hafiz needs agents to stop treating merged, deployed, smoke checked, monitored, and accepted as the same thing. Agents should automate preflight, safe smoke, read-only monitoring, and release reports inside an approved boundary, while production deploy, rollback, destructive actions, critical-lane widening, and business acceptance remain explicit. | Use `release-deploy-live-monitoring.md`, `monitor-production-logs.md`, and release-state evals before saying work is live or healthy. |
| 2026-06-29 | Incident Workflow accepts the protection-first path. | Production incidents should not be handled like ordinary bugfixes. Agents must triage read-only first, name impact/severity, recommend mitigation, pause for production/critical authority decisions, prove stability after fix or rollback, and save a postmortem/lesson when material. | Use `incident-workflow.md`, `monitor-production-logs.md`, and incident evals before coding or closing serious production issues. |
| 2026-06-29 | Project Adoption accepts shared core plus local project profile. | The umbrella Agent OS should stay portable, but each product repo needs a small verified adapter for commands, evidence, deploy path, critical lanes, and what done means. Installer pass is only baseline, not full readiness. | Use `project-adoption.md` before developer-staff rollout in product repos. |
| 2026-06-29 | Ordinary staff use Teams Planner only; Agent OS rollout is for developer staff. | Hafiz clarified that non-developer staff should not use Agent OS or LLM workflow kits directly. They report through Teams Planner. The OS is for developer staff working on other projects. | Update rollout docs, evals, and future discussion wording to say developer staff rollout. |
| 2026-06-29 | Governance and Versioning accepts the Agent OS change-control workflow. | Hafiz wants the Agent OS core strengthened before rollout. Future Agent OS changes need change type, source owner, connected-file check, checks, Koda decision, Git state, and clear close-out. | Use `agent-os-governance.md` before adding or changing Agent OS rules, workflows, skills, hooks, evals, or installer files. |
| 2026-07-01 | Kun Chen workflow review topic 1 accepts the Operating Posture principle. | Hafiz agreed this is better than the current blurry setup because it makes the relationship explicit: Hafiz owns intent, priority, product/business judgment, and risk; the agent owns technical execution, testing, evidence, memory, and next-step guidance. | Use `agent-os.md`, `agent-os-roles.md`, and `working-with-hafiz.md` as the first-principle source before refining memory/skills next. |
| 2026-07-01 | Kun Chen workflow review topic 2 accepts the Memory/Skill Ownership Rule. | Hafiz agreed the Agent OS should be stricter about where information belongs so agents stop dumping the same lesson everywhere. Always-loaded memory stays small; detailed procedures live in skills/playbooks; durable lessons live in Koda; current story lives in Session Map; execution state lives in GitHub/PRs/active task/git. | Use `agent-os-memory-architecture.md` and `agent-os-skill-registry.md`; next discuss planning artifacts and whether complex work should use interactive HTML, Markdown, or both. |
| 2026-07-01 | Kun Chen workflow review topic 3 accepts the Planning Artifact Standard. | Hafiz wants brainstorming and understandable English before implementation, without forcing heavy process for every small task. The Agent OS now chooses the smallest useful artifact: chat-only, Quick Brief, Product Shape, Build-Ready Pack, Session Map, or Markdown + generated HTML view. | Use `planning-artifacts.md` as the source of truth for artifact choice, source-of-truth rules, required content, visual review, and implementation boundary. |
| 2026-07-01 | Kun Chen workflow review topic 4 accepts the Tool Connector Standard. | Hafiz agreed agents should not keep asking which connector to use for ordinary read/check work. The agent should choose the smallest reliable tool that proves the task safely: CLI first for local truth, wrappers for repeatable safe probes, connectors/MCP for rich service workflows, API wrappers when MCP is too broad or unreliable, browser/Playwright for user journeys, and GUI only when the real task is inside a native app. | Use `agent-os-capability-model.md` as the source of truth for connector choice, probing, fallback, and automatic tool selection. |
| 2026-07-01 | Kun Chen workflow review topic 5 accepts No-Mistakes-Lite. | Hafiz wants the protection idea from Kun's `no-mistakes` without adding a heavy external pipeline too early. Sifututor starts with a final honesty playbook before ready/done/outbound claims, commit, push, PR, merge, deploy, save-session, or handoff. | Use `no-mistakes-lite.md` as the source of truth for the final scope/proof/state/approval/next-action gate. Automate later only after repeated real use proves which parts should become scripts or fixtures. |
| 2026-07-01 | Kun Chen workflow review topic 6 accepts Parallel Work and Worktree Isolation. | Hafiz wants multiple agents/sessions to work without overwriting each other or confusing branch, PR, commit, deploy, and live state. Sifututor starts with a lightweight Git worktree standard instead of installing a treehouse-style manager immediately. | Use `parallel-work-and-worktrees.md` as the source of truth for when to isolate work, how to name worktrees, what state to record, how to avoid stranded local commits, and when cleanup is safe. |
| 2026-07-01 | Kun Chen workflow review topic 7 accepts Autonomous Work Packets. | Hafiz already has natural phrases like "proceed until done" and approval boundaries, but the missing layer is how agents behave during long-running loops. Sifututor starts with controlled packet rules instead of installing a gnhf-style autonomous runner. | Use `autonomous-work-packets.md` as the source of truth for finish point translation, loop size, loop limits, progress cadence, retry/rollback behavior, commit behavior, stop rules, and save/resume behavior. |
| 2026-07-01 | Kun Chen workflow review topic 8 accepts First-Mate Routing as a Task Router responsibility first. | Hafiz wants the Agent OS to feel like one coordinated system, not many separate skills that he must manually steer. Creating a separate first-mate agent now would add confusion before the router behavior is proven. | Use `agent-os-routing-model.md` and `task-router.md` as the source of truth: Task Router translates Hafiz's request into workflow stage, finish point, worker/tool, proof, approval stop point, and next action. Split into a dedicated agent/tool only if real use shows the router is too heavy. |
| 2026-07-01 | Kun Chen workflow review topic 9 accepts the Continuation Pack as the source of truth for remote/device/session continuity. | Hafiz wants future sessions and other LLMs to feel like continuing the same work, not restarting from fragments. Persistent terminal tools can help, but they should not become hidden state that only one machine/session can understand. | Use `save-session.md`, `session-map.md`, and `agent-os.md`: continuation must name main goal, current focus, highest proven state, Git/local-only state, evidence, waiting decisions, first source/check to run, and the single next action. Terminal tools such as tmux/WezTerm/SSH/Tailscale/mosh are optional environment helpers, not the source of truth. |
| 2026-07-01 | Kun Chen workflow review topic 10 is parked as optional daily environment helpers. | Hafiz asked whether we can skip terminal/editor setup. We can, because correctness now comes from Session Map, save-session, Git, Koda, GitHub, evidence, and routing, not from a required tmux/WezTerm/voice setup. | Do not install or require WezTerm, tmux, Neovim, voice input, SSH/Tailscale/mosh, or a fixed developer layout now. Revisit later as an optional developer environment profile if daily setup friction appears. |
| 2026-07-01 | Kun Chen workflow review topic 11 accepts Fresh-Context Review. | Hafiz wants the agent to maximize capability but not over-trust its own work. A builder can become too confident after implementing; before important outbound states, review should challenge assumptions from the outside. | Use `review.md` and `no-mistakes-lite.md`: before push, PR, merge, deploy, live/done claims, critical lanes, user-facing work, long autonomous packets, multi-fix sessions, or complex Agent OS behavior changes, review the diff/state/evidence as if the reviewer did not build it. Do not create a separate skill by default. |
| 2026-07-01 | Kun Chen general guidelines are adapted for Sifututor instead of copied blindly. | Hafiz asked whether the screenshot rules from the video had been discussed. Some were already covered, but commit co-author, generated-file handling, long Markdown style, and quality-vs-scope needed explicit Sifututor rules. | Use `agent-os-general-guidelines.md`, `commit.md`, `review.md`, and evals. No agent co-author unless Hafiz asks; do not hand-edit generated files; long Markdown can use one sentence per line where practical; prioritize quality, simplicity, robustness, scalability, and maintainability; prove bug fixes through real user behavior; report/rout unrelated UI/lint/test/flaky issues instead of hiding them or silently expanding scope. |
| 2026-07-01 | Doc routing and context loading is accepted as the answer to Agent OS doc sprawl. | Hafiz asked how we make sure LLMs read the relevant docs instead of missing them or wasting context. More docs alone make the problem worse unless the router tells the agent which docs matter for each work type. | Use `doc-routing-and-context-loading.md` from `task-router.md` after the route is chosen. Read always-required docs, route-required docs, triggered docs, and current evidence. Skip unrelated deep docs until needed. Add evals for missed route owner docs, Agent OS improvement docs, and SIMS UI/TESTING triggered docs. |
| 2026-07-01 | Skill quality and pruning is accepted as the answer to Agent OS sprawl. | Hafiz approved a proceed-until-done packet because he accepts the direction but wants the Agent OS to stop growing randomly. With many docs and skills, the system needs a rule for when to update, create, merge, park, or delete. | Use `skill-quality-and-pruning.md` before creating/splitting skills or workflow docs. Use `doc-owner-route-index.md` so every active Agent OS doc has an owner and route. Add evals for duplicate skill creation, missing index entries, and duplicated docs. |
| 2026-07-01 | Runtime Reliability is the next Agent OS core phase after doc routing and pruning. | Hafiz asked to continue the Agent OS phase after the core packet was pushed. The next risk is not missing docs; it is runtime drift: wrong mode, stale Session Map, missed context, state confusion, or no next action. | Use `agent-os-runtime-reliability.md`: keep mode, loaded context, proof/state, and next action visible during meaningful work. Add evals for wrong-mode drift, stale Session Map, and no-next-action close-outs. |

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

### Developer Staff Rollout Pieces

Already present:

- install manifest
- installer/checker
- installation guide
- developer staff quick start

Current decision:

- developer staff rollout follows the readiness ladder in
  [agent-os-rollout-readiness.md](agent-os-rollout-readiness.md)
- keep expanding internal reliability first
- ordinary staff stay in Teams Planner
- start developer staff later with the developer staff kit, not full tool access

Practical meaning: we have early distribution assets and a rollout model, but
developer-staff rollout should wait for a pilot plan and templates.

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

### 11. Developer Staff Rollout Readiness

Question: when is the Agent OS good enough to distribute to developer staff?

This has a draft decision now. Use
[agent-os-rollout-readiness.md](agent-os-rollout-readiness.md) as the source
before expanding developer-staff access.

Review:

- installer
- developer staff quick start
- templates
- developer staff permission profiles
- local memory fallback
- tool-specific shims
- examples for developer, QA, and product/design developer staff

Output:

- developer staff rollout plan
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

Continue with section 17: **Push / PR / Release Lifecycle**.

Reason: the Agent OS now has stronger commit, evidence, state, self-improvement,
and related-impact rules. The next weak point is the outward path after local
commits: push, PR, merge, deploy, live check, and how agents explain the
highest proven state without making Hafiz ask what is actually on GitHub or
live.
