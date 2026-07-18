# Agent OS Parity Contract

Status: draft for Sifututor Agent OS.

This contract explains how Claude, Codex, and future LLM agents should behave
the same way inside the Sifututor Agent OS.

Plain meaning: Claude and Codex may have different buttons, commands, hooks, or
UI affordances, but Hafiz should be able to predict the same decision flow from
both of them.

## Core Principle

The Agent OS does not require every agent to think identically.

It requires every agent to follow the same:

- source of truth,
- routing decision,
- approval boundary,
- safety guardrail,
- evidence standard,
- state update,
- handoff shape,
- plain-language close-out.

Use [multi-agent-adapter-workflow.md](multi-agent-adapter-workflow.md) when
deciding which agent, adapter, subagent, or human should do a stage of work.
That workflow owns the rule that the workflow stage comes first and agent
strength is only a recommendation.

Different agents can expose different command shapes. For example, Claude may
have four visible product-design commands while Codex uses one umbrella
`$product-design` skill. That is acceptable only if the underlying phases,
questions, decisions, evidence, and stopping points match.

## What Must Be Identical

| Area | Must match across agents |
| --- | --- |
| Source of truth | Read `AGENTS.md`, relevant project rules, Koda, active task state, and current files before acting. |
| Routing | Classify the work into the same workflow: discussion, task-router, diagnose, product design, verify, QA, review, commit, save-session, handoff, or monitor. |
| Approval gates | Stop at the same gates: commit, push, PR, merge, deploy, destructive action, production mutation, critical-lane implementation. |
| Safety | Never read `.env*`, expose secrets, bypass hooks, or modify `live/`. |
| Critical lanes | Payments, auth, invoices, commissions, migrations, mobile API contracts, and deploys start with read-only diagnosis unless Hafiz explicitly authorizes a different emergency path. |
| Evidence | User-facing behavior needs human-journey evidence where feasible, not only code-level tests. |
| State | Do not confuse local, committed, pushed, PR open, merged, deployed, and live-smoke-passed. |
| Memory | Koda stores durable lessons and corrections, not noisy progress or secrets. |
| Communication | Explain in natural language first; use formal labels only when they help audit, QA, commit, or handoff. |
| Close-out | End meaningful work with what changed, how checked, what remains, and the recommended next step. |

## What May Differ

| Area | Allowed difference |
| --- | --- |
| Command name | Claude can use slash commands. Codex can use `$skill` wrappers. Future agents can use another adapter. |
| Internal tool | One agent may use MCP; another may use CLI or local scripts. The result and evidence standard must match. |
| UI | Claude, Codex, Cursor, Copilot, Gemini, or another tool can show different interfaces. |
| Packaging | Claude may split a workflow into several commands while Codex exposes one umbrella skill. |
| Automation strength | Hooks may differ by tool. Missing hooks must be compensated by shared scripts, playbooks, and explicit checks. |

## Workflow Parity Matrix

| Workflow | Claude adapter | Codex adapter | Shared source | Parity requirement |
| --- | --- | --- | --- | --- |
| Task Router | `/task-router` or project router | `$task-router` | `task-router.md` | Same route, context checks, approval boundary, next action. |
| Diagnose | `/diagnose` | `$diagnose` | `diagnose.md` | Same read-only diagnosis before critical-lane implementation. |
| Product Design | `/lite-prd`, `/prd-clarifier`, `/prd-to-ux`, `/ux-to-prompts` | `$product-design` phases | `product-design.md` | Same brainstorm-first behavior, questions, decisions, and output phases. |
| Verify | `/verify` | `$verify` | `verify.md` | Same focused proof, baseline failure handling, and evidence report. |
| QA | `/qa` | `$qa` | `qa.md` | Same human-journey and regression evidence standard. |
| Review | `/review` | `$review` | `review.md` | Same risk-first review behavior and no quiet fixing in review-only mode. |
| Commit | `/commit` | `$commit` | `commit.md` | Same guard checks, exact file-list approval, local commit boundary. |
| Save Session | `/save-session` | `$save-session` | `save-session.md` | Same durable memory, state, evidence, and next-action preservation. |
| Handoff | `/handoff` | `$handoff` | `handoff.md` | Same written state transfer and no reliance on hidden chat context. |
| Snapshot | `/snapshot` | `$snapshot` | `snapshot.md` | Same pause/compact context capture. |
| Session Map | `/session-map` or natural-language update | `$session-map` | `session-map.md` | Same human-first current-session map, side paths, decisions, evidence, and continuation prompt. |
| Quick Check | `/quick-check` or doctor | `$quick-check` | `quick-check.md` | Same health and drift check before real work. |
| Production Monitor | `/monitor-production-logs` | `$monitor-production-logs` | `monitor-production-logs.md` | Same read-only post-deploy monitoring boundary. |
| Workflow Improvement | `/workflow-improvement` later or natural-language workflow improvement | `$workflow-improvement` | `agent-os-improvement-loop.md` | Same controlled self-learning loop: classify the Agent OS mistake, update the owning layer and connected files, avoid Koda-only fixes, run checks, and stop before uncontrolled self-rewriting. |
| SIMS UI Audit | `/sims-ui-audit` plus `ux-reviewer` | `$sims-ui-audit` | `sims-ui-audit.md` | Same screenshot-backed UI/UX judgment, design-doc checks, evidence requirements, and pass/fail findings before Hafiz review. |

## Product Design Special Case

Claude currently exposes product design as four visible steps:

```text
/lite-prd -> /prd-clarifier -> /prd-to-ux -> /ux-to-prompts
```

Codex currently exposes the same route as one umbrella skill:

```text
$product-design
```

This is acceptable only if Codex clearly names the current phase in plain
language:

| Phase | Plain meaning | Claude command | Codex phase |
| --- | --- | --- | --- |
| Design brief | What are we trying to build and why? | `/lite-prd` | `$product-design` brief phase |
| Clarify | What is still unclear or risky? | `/prd-clarifier` | `$product-design` clarification phase |
| UX spec | How should the user experience work? | `/prd-to-ux` | `$product-design` UX phase |
| Build prompts | How should implementation be handed to a builder agent? | `/ux-to-prompts` | `$product-design` build-prompt phase |

If Hafiz wants more control later, create Codex aliases for these phases. The
aliases should still read `product-design.md`; they should not become separate
sources of truth.

## Best-Practice Baseline From Research

The external pattern is clear:

- OpenAI Agents SDK separates agents, handoffs, guardrails, and tracing.
- LangGraph separates durable orchestration, persistence, interrupts, and
  human-in-the-loop pauses.
- Claude Code separates instructions, skills, hooks, subagents, and memory.
- AutoGen Magentic-One uses an orchestrator, task ledger, progress ledger, and
  human oversight.
- CrewAI separates autonomous crews from deterministic flows with state and
  routing.

Sifututor implication: parity should be tested at the workflow boundary, not by
expecting every model/tool to expose identical UI.

## Current Gap Map

| Gap | Practical meaning | Recommended fix |
| --- | --- | --- |
| Parity contract was implied, not explicit | Hafiz had to infer whether Claude and Codex should behave the same. | Keep this contract as the single parity map. |
| Product Design packaging differs | Claude shows four steps; Codex shows one umbrella skill, which can feel like less control. | Require Codex to name the current phase; optionally add Codex phase aliases later. |
| Evals mostly test Codex routing | We can prove Codex hook behavior better than live Claude extension behavior. | Use `agent-os-adapter-readiness.py` for wiring, behavior trace for deterministic Codex routing, and live Claude prompts only as optional evidence until the extension has a stable non-interactive test path. |
| Hook behavior differs by tool | Claude and Codex lifecycle hooks are not mechanically identical. | Treat hooks as adapter helpers; enforce core rules through shared playbooks and scripts. |
| Claude adapter overfits old task-state mechanics | Live Claude transcript tests showed safe but rigid answers that required `active.json`, Claude-only gate fields, or old command names for every workflow. | Treat `active.json`, Claude hooks, and project slash commands as adapter helpers. The shared behavior comes from `AGENTS.md`, this contract, and the playbooks. |
| Real sessions still omit a usable close-out | Transcript retrospective found both adapters often checked work but left Hafiz to ask what remains or what next. | Keep the shared close-out contract in the communication owner, inject the same compact reminder through both prompt adapters, and protect it with response-shape fixtures. |
| Agents explain findings before the user story | Real transcripts repeatedly show Hafiz asking what the feature/issue actually is, what the user does, and to review one item at a time. | Keep explanation order in the communication/review owners, inject the same explanation-first and one-by-one reminder through both adapters, and protect representative shapes with fixtures/evals. |
| Browser proof can come from the wrong checkout or stale port | Real UI sessions showed correct code being judged through an old worktree, server, sidebar shell, or local port. | Require target-identity proof in verification and QA before either adapter treats screenshots/browser evidence as proof. |
| Traceability is file-based, not full runtime tracing | We have docs, Koda, task files, guards, and evals, but not a full run trace dashboard. | Keep lightweight file-based evidence now; consider trace logging only after the workflow stabilizes. |
| Future LLM support is conceptual | The core is model-agnostic, but adapters for Cursor, Copilot, Gemini, or staff LLMs are not built yet. | Build future adapters from this contract only after Claude/Codex parity feels predictable. |

## Parity Eval Requirements

Add or maintain checks that prove:

- every workflow in the skill registry has a shared playbook,
- every shared playbook has a Claude adapter or stated exception,
- every shared playbook has a Codex adapter or stated exception,
- Product Design phase mapping remains documented,
- commit/push/deploy gates are identical across adapters,
- save-session produces the same durable state shape,
- staff/Planner intake does not bypass GitHub/task workflow,
- Plane remains exception-only unless Hafiz explicitly asks.

## Behavioral Parity Fixtures

These scenarios define the same behavior Claude, Codex, and future adapters
must produce even when their command names differ.

| ID | Scenario | Expected shared behavior |
| --- | --- | --- |
| BP-001 | Hafiz approves a commit-only bundle | Commit only the exact approved file list. Do not push. |
| BP-002 | Hafiz approves commit plus push | Run pre-push review, commit/push only the exact approved bundle, and report remote state. |
| BP-003 | Hafiz asks to design a feature or workflow | Start with brainstorm/product design, explain options and tradeoffs, and do not implement until approval. |
| BP-004 | Hafiz reports payment, invoice, auth, migration, deploy, commission, or mobile API contract work | Start with read-only diagnosis and recommendation. Wait for approval before implementation. |
| BP-005 | Hafiz asks to verify or QA a user-facing workflow | Gather agent-run human-journey evidence where feasible, and do not ask Hafiz to check what the agent can safely check. |
| BP-006 | Hafiz asks to save or hand off the session | Preserve current state, evidence, next action, and durable Koda lessons without relying on hidden chat context. |
| BP-007 | Staff or Planner reports a bug | Treat the report as a symptom, reproduce or inspect current evidence first, then route confirmed engineering work through GitHub/task workflow. |
| BP-008 | Hafiz asks for Plane status without explicitly requesting Plane | Do not use Plane by default. Use GitHub, active task state, Mission Ledger, Koda, and close-out instead. |
| BP-009 | A session has multiple goals, side paths, or parallel agent work | Create or update the Session Map so Hafiz and future agents can see the main goal, current focus, decisions, side paths, evidence, and return path. |
| BP-010 | Hafiz asks to improve the workflow or make future agents handle a mistake better | Use the Agent OS Improvement Loop: classify the mistake, choose the owning source of truth, check connected docs/skills/hooks/evals/Koda/Session Map, update the smallest coherent set, and do not silently self-rewrite. |
| BP-011 | A project has `.claude/tasks/active.json` | Read it as workflow state when the project uses it, but do not treat it as the only truth. Cross-check chat, Git, Session Map, Koda, GitHub, Planner, and current files based on the question being answered. |
| BP-012 | A project or session does not have a relevant active task file | Do not invent `active.json` fields or block ordinary discussion/docs work on missing gate values. Use the route playbook, current evidence, and approval boundary instead. |
| BP-013 | Claude uses project-specific slash commands such as `/sifu-save-session` | Treat them as adapter conveniences only. The shared workflow name is `/save-session`, `$save-session`, or natural-language "save session", and all must follow `save-session.md`. |

## Adapter Helper Boundaries

Some tools have helpful mechanics that are not universal Agent OS rules.

| Helper | Correct use | Drift to avoid |
| --- | --- | --- |
| `.claude/tasks/active.json` | Current execution pointer for projects that use state files. Read it when present and relevant. | Requiring it for every parent-workspace discussion, workflow improvement, or commit explanation. |
| Claude workflow hooks | Extra safety for branch names, commit messages, quality gates, Koda context, and project state. | Saying a hook-only field such as `gate4_evidence` is the shared proof standard when the playbook defines a broader evidence requirement. |
| Project slash commands | Convenient Claude entrypoints for the same shared workflows. | Calling `/sifu-save-session`, `/ripple-commit`, or another project alias the source of truth instead of the shared playbook. |
| Gate labels | Useful audit shorthand inside verification, QA, review, commit, or handoff records. | Leading Hafiz-facing explanations with labels when plain language would be clearer. |

Plain meaning:

```text
Use adapter mechanics when they help. Do not let them replace the shared
workflow, evidence standard, or state model.
```

## Behavior Parity Review Standard

Use this when comparing Claude, Codex, or another LLM on the same prompt.

Plain meaning:

```text
Different wording is fine. Different workflow behavior is not fine.
```

Compare the answer against these behavior points:

| Behavior point | What must match |
| --- | --- |
| Route | Both agents choose the same workflow or explain why the route changed. |
| First move | Both agents start with the same kind of action: discuss, diagnose, design, verify, QA, review, commit, save, or stop. |
| Approval boundary | Both agents stop at the same commit, push, PR, merge, deploy, production, destructive, or critical-lane gate. |
| Evidence standard | Both agents ask for or gather the same level of proof for the claimed state. |
| State language | Both agents distinguish local, committed, pushed, PR open, merged, deployed, live checked, and accepted / closed. |
| Memory and task routing | Both agents store durable lessons in Koda, current session story in the Session Map, and execution work in GitHub/task state where appropriate. |
| Close-out | Both agents explain what changed, how checked, what remains, and the recommended next step in plain language. |
| Explanation order | Both agents explain the user/business story and current-versus-expected flow before technical findings; both honor one-by-one review pacing when requested. |
| Target identity | Both agents prove the URL/environment, serving source, branch/worktree, and commit/version before trusting browser, screenshot, staging, or production evidence. |

Allowed adapter differences:

- command name, such as `/verify` versus `$verify`,
- UI wording or button labels,
- MCP versus CLI tool access,
- one umbrella skill versus several phase-specific commands,
- different internal implementation as long as the shared behavior is preserved.

Parity drift:

```text
If one agent would proceed and the other would stop, if one asks Hafiz to test
what it can safely test, if one treats local work as pushed/live, or if one
crosses a harder approval gate, that is behavior drift.
```

When behavior drift is found, update the shared source first: playbook, parity
contract, skill registry, adapter wrapper, hook/fixture, or Koda correction.
Do not patch only one agent unless the difference is truly adapter-specific.

## Decision Rule

When Claude and Codex differ, ask this:

```text
Is this only a UI/tool difference, or does it change the decision, safety,
evidence, approval, memory, or state behavior?
```

If it is only UI/tool difference, document it as an adapter difference.

If it changes behavior, treat it as parity drift and fix the shared playbook,
adapter wrapper, hook, eval, or Koda memory.

Use [agent-os-enforcement-drift.md](agent-os-enforcement-drift.md) to decide
which layer owns the fix. Plain meaning: do not automatically patch Claude,
Codex, and hooks separately. First identify whether the drift is docs, adapter,
behavior, hook, state, or memory drift, then fix the owning layer.
