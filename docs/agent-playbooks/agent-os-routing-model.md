# Agent OS Routing Model

Status: draft for review.

This document defines how the Sifututor Agent OS should classify Hafiz's prompt
before choosing discussion, planning, implementation, verification, QA, review,
commit, push, save-session, or critical-lane behavior.

The purpose is to avoid two bad extremes:

- too heavy: discussion triggers implementation or commit machinery
- too loose: risky work skips diagnosis, approval, evidence, or review

## Best-Practice Baseline

Treat routing as **policy-based orchestration**, not just keyword
classification.

Plain meaning:

```text
The router decides the safest useful work mode first.
Only after that should the agent choose tools.
```

This matches common patterns from reputable agent frameworks:

- LangChain / LangGraph use human-in-the-loop middleware and interrupts to
  pause before sensitive tool calls, then resume after a human decision such as
  approve, edit, reject, or respond.
- OpenAI Agents SDK separates agents, tools, handoffs, guardrails, tracing, and
  stateful runs so behavior can be controlled and inspected instead of hidden
  inside one free-form prompt.
- Microsoft Agent Framework describes production agents as needing
  orchestration, durability, restartability, observability, governance,
  human-in-the-loop control, and provider flexibility.
- AutoGen uses team orchestration and user-proxy feedback. Its human-in-the-loop
  model reinforces that human input should happen at meaningful control points,
  not as constant micro-approval.

Sifututor adopts this principle:

```text
The Agent OS should understand Hafiz's intent, choose the lightest safe
workflow, use tools only when the route needs them, pause for human approval at
meaningful risk points, and record enough state/evidence so the work can resume
or be audited later.
```

Non-technical version:

```text
First decide whether we are thinking, checking, building, testing, or shipping.
Then use the tools that fit that mode.
Stop before dangerous actions.
Leave a clear trail.
```

## First-Mate Routing

Use this as the human-friendly name for the router's orchestration
responsibility.

Plain meaning:

```text
The router is the front desk of the Agent OS.
Hafiz should not need to remember every workflow, skill, tool, or stop point.
```

This is not a separate agent yet. For now, first-mate routing is an upgraded
responsibility of Task Router.

When a task starts or resumes, Task Router should answer these questions before
the agent gets deep into work:

1. What is Hafiz trying to achieve?
2. Is this discussion, diagnosis, design, build, verify, QA, review, commit,
   push/PR, deploy, monitoring, save-session, or handoff?
3. What is the practical finish point for this task: diagnosed only, fixed
   locally, committed, PR opened, merged, deployed, live-smoke-passed, or
   monitored?
4. Which worker or tool fits the current stage: Codex, Claude, future LLM,
   subagent, browser, CLI, connector, Koda, GitHub, Planner, or human?
5. What evidence will prove the current stage?
6. Where must the agent stop for Hafiz's approval, risk acceptance, or product
   judgment?
7. What is the next recommended action after this step?

Non-technical version:

```text
Do not make Hafiz manage the crew.
Translate his request into a safe route, pick the right worker/tool, explain
where the work will pause, and keep the next move visible.
```

Current implementation decision:

```text
Do not create a separate "first-mate agent" yet.
Make Task Router own this behavior first.
Split it into a dedicated agent/tool only if the router becomes too heavy or
repeated evals show one router cannot manage the orchestration cleanly.
```

Useful references:

- LangChain human-in-the-loop:
  <https://docs.langchain.com/oss/python/langchain/human-in-the-loop>
- LangGraph interrupts:
  <https://docs.langchain.com/oss/python/langgraph/interrupts>
- OpenAI Agents SDK guardrails:
  <https://openai.github.io/openai-agents-python/guardrails/>
- OpenAI Agents SDK tracing:
  <https://openai.github.io/openai-agents-python/tracing/>
- Microsoft Agent Framework:
  <https://github.com/microsoft/agent-framework>
- AutoGen human-in-the-loop:
  <https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/human-in-the-loop.html>

## Routing Decision Tree

Use this quick tree before choosing tools or editing files:

1. **Is the request forbidden or unsafe?**
   If it asks to read or modify `.env*`, secrets, raw tokens, or `live/`, stop
   and explain the boundary.
2. **Is it a critical lane?**
   If it touches auth, payment, invoice, commission, migration, deployment, or
   mobile API contracts, do read-only diagnosis first and wait for approval
   before implementation.
3. **Is Hafiz asking to think, understand, compare, or decide?**
   Stay in discussion mode. Explain options, recommend softly, and do not edit
   unless Hafiz asks to document the decision.
4. **Is Hafiz asking for product/design/architecture direction?**
   Use product-design/planning mode. Keep a living draft and discuss one
   decision at a time before implementation.
5. **Is Hafiz asking to check, prove, review, QA, or diagnose?**
   Use the evidence route first. Read and test before changing code unless the
   fix is already clearly approved and low-risk.
6. **Is Hafiz asking to implement a scoped change?**
   Use the normal build route. Create or link the engineering issue when
   needed, implement in safe slices, verify, QA, review, then stop before commit
   unless commit was approved.
7. **Is Hafiz asking to commit, push, open PR, merge, deploy, or release?**
   Treat it as an outbound action. Inventory status, run the required guards,
   and require the correct explicit approval for that boundary.
8. **Is Hafiz using a short command like `go next`, `proceed`, or `approve`?**
   Follow the last clear recommendation or exact approval request. If the last
   step is missing, stale, ambiguous, or risky, ask a short clarification.

Plain version:

```text
Unsafe? Stop.
Critical? Diagnose first.
Thinking? Discuss.
Designing? Draft and decide.
Checking? Gather evidence.
Building? Implement and verify.
Shipping? Guard and ask approval.
Short command? Follow the last clear step.
```

## Human Decision Types

When the router pauses for Hafiz, it should be clear what kind of decision is
needed. Use these decision types:

| Decision type | Meaning | Example |
| --- | --- | --- |
| approve | Hafiz accepts the proposed action or bundle. | `Approve commit+push for these files?` |
| edit | Hafiz wants the agent to change the plan first. | `Use GitHub issue, not Plane, for this one.` |
| reject | Hafiz does not want the proposed action. | `Do not deploy yet.` |
| explain | Hafiz wants more understanding before deciding. | `Why do we need this test?` |
| continue until boundary | Hafiz lets the agent continue through a safe packet. | `Continue until PR opened, but stop before merge.` |

The agent should avoid vague approval questions. Ask for a named action and a
boundary, such as "approve docs edit + checks" or "approve commit+push for
these three files."

## Route Confidence

Most routing should be decisive. Ask Hafiz only when the route changes the risk
or when intent is genuinely unclear.

Use this behavior:

- **High confidence**: act on the route and explain the practical meaning.
- **Medium confidence**: state the assumed route and continue only if the risk
  is low, such as docs or discussion.
- **Low confidence**: ask one short clarification before editing, committing,
  pushing, deploying, or touching critical domains.

Examples:

| Situation | Router behavior |
| --- | --- |
| Hafiz says `go next` after the agent recommended reviewing Routing. | Continue Routing review. |
| Hafiz says `go next` after a long pause with dirty repos. | Run reconciliation audit first. |
| Hafiz says `approve` after the agent asked only for commit approval. | Commit only, not push. |
| Hafiz says `approve` after the agent asked for commit+push with exact files. | Commit and push that exact bundle. |
| Hafiz asks "why are we doing this?" during implementation. | Stop building and return to explanation/discussion. |

## Source Inputs

Route classification should use these signals in order:

1. Explicit tool or skill request, such as `$verify` or `$commit`.
2. Hafiz's last approved/recommended step in the current conversation.
3. Current repo state, such as dirty files, staged files, branch, active task,
   and whether work is already committed or pushed.
4. Risk words and protected domains: auth, payments, invoices, commissions,
   migrations, deploys, mobile API contracts, secrets, `.env*`, and `live/`.
5. Intent words: discuss, plan, fix, verify, QA, review, commit, push, save.
6. Context authority: whether the prompt is verified, trusted, reported,
   historical, or unverified.

Do not route by keyword alone.

## Routing Priority

Use this order when signals conflict:

| Priority | Route | Why |
| --- | --- | --- |
| 1 | blocked boundary | secrets, `.env*`, and `live/` protection override all other intent |
| 2 | critical lane diagnosis | high-risk domains require diagnosis first |
| 3 | explicit skill request | Hafiz named a tool/workflow directly |
| 4 | save/handoff/snapshot | preserves context before it is lost |
| 5 | push/deploy/merge/PR review | outbound actions need risk check and explicit approval |
| 6 | commit | local history mutation needs exact file list and approval |
| 7 | verify/QA/review/diagnose | evidence and analysis routes |
| 8 | product design/planning | PRD, UX, architecture, or workflow design |
| 9 | implementation/task-router | non-trivial safe work |
| 10 | discussion/light mode | learning, architecture discussion, retrospective, naming, options |

Plain meaning: when risk is high, route to safety first. When the prompt is
thinking-oriented, stay light.

## Prompt Categories

| Prompt type | Examples | Expected route | Expected behavior |
| --- | --- | --- | --- |
| discussion | `why are we doing this?`, `can we discuss architecture?`, `what mistakes did we make?` | discussion/light mode | Think with Hafiz. Do not edit unless asked to document. |
| architecture planning | `plan it properly`, `map what Agent OS should have` | planning/product-design or docs | Keep a living draft, map assets/gaps/touched files, ask or recommend next topic. |
| proceed | `proceed`, `ok proceed`, `proceed next` | last clear recommended step | Act immediately if clear and safe; ask only if ambiguous/risky. |
| approve | `approve` | last explicit approval request | Execute the approved action or bundle exactly. |
| what next | `what next`, `next?` | recommendation | Give one next action, not a vague list. |
| commit | `commit this`, `prepare commit` | commit | Guard, inspect diff/status, require exact file-list approval. |
| bundled commit+push | `approve` after agent asks `approve commit+push?` | commit+push bundle | Commit and push exactly; report final status. |
| push/PR/merge | `push this`, `open PR`, `merge` | review first | Risk review, inventory status, explicit approval. |
| deploy/release | `deploy this`, `release to prod` | review/critical release gate | Strong evidence, explicit approval, no bundling by default. |
| save session | `save session`, `wrap up` | save-session | Preserve durable state and lessons. |
| bug/diagnosis | `why is this failing?`, `debug this` | diagnose | Read-only diagnosis before edits unless safe/simple. |
| critical domain | `fix payment`, `auth migration`, `mobile API contract` | critical lane diagnosis | Phase A diagnosis, then wait for approval. |
| forbidden path | `open .env`, `patch live/` | blocked | Refuse and explain boundary. |

## Short Command Rules

Short commands depend on the last clear recommendation.

| Command | Rule |
| --- | --- |
| `proceed` | Act on the last recommended step if it is clear and safe. |
| `approve` | Execute the last exact approval request, including a bundle if the bundle was explicitly named. |
| `ok` | Treat as acknowledgement unless the previous message asked for a clear approval. |
| `next` | Recommend one next action. |

If the last recommendation was "review routing model next," `proceed next`
means start that review. If the last request was "approve commit+push for these
files," `approve` means commit and push.

## Smart Resume

Use smart automatic resume for continuation-like prompts. The agent should look
for evidence that the user is returning to an existing thread before starting
from zero.

Resume signals:

- Hafiz says `continue`, `resume`, `go next`, `proceed`, `what next`, or
  similar.
- A recent active Session Map exists.
- Local Git is ahead of GitHub or another state boundary is waiting.
- The chat resumed after compaction or a long pause.
- The task is multi-step Agent OS, workflow, product, QA, release, or handoff
  work.

Expected behavior:

1. Read the latest relevant Session Map Reference Pack before broad
   exploration.
2. Check Git state.
3. Summarize the main goal, current focus, waiting items, and recommended next
   action.
4. Continue if the map matches the prompt.
5. If the map looks unrelated, say so and treat the prompt as new work unless
   Hafiz says to resume it.

Plain meaning: if Hafiz says "continue", check the whiteboard first. If Hafiz
asks a tiny unrelated question, answer the question.

## Conversation-State Fixture Check

Run this local fixture runner when changing short-command behavior:

```bash
scripts/agent-checks/agent-os-conversation-fixture-runner.py
```

It checks short replies against visible prior assistant context. Plain meaning:
`approve` follows the last exact approval request, `proceed` follows the last
clear safe recommendation, `what next` returns one next action, and missing
previous context should trigger clarification instead of guessing.

Decision: for now, this uses visible chat context only. Do not add hidden
lifecycle-hook or session-file state for last recommended step yet. Add stored
state later only if repeated failures show chat context is not enough.

## Bundled Approval Routing

Bundled approvals are allowed only when the agent asks clearly and the scope is
exact.

Decision: for now, bundled approval context also uses visible chat context
only. The immediately previous approval request must clearly name the exact
bundle. Do not add hidden pending-approval session state yet. Add stored state
later only if repeated failures show chat context is not enough.

Allowed bundles:

- stage + commit
- commit + push
- create issue + document plan
- docs edit + checks
- verify + QA
- commit + close issue
- push + close issue

Never bundle by default:

- deploy + smoke + close issue
- migration + deploy
- payment/auth/invoice/commission/mobile API changes + commit
- production log access + fix + deploy
- destructive cleanup
- secrets or `.env*`
- changes under `live/`

## Living Draft Rule

For architecture and workflow design, keep a living draft updated while
discussing. Hafiz should not need to repeat decisions already made in the same
thread.

The agent should update the draft when:

- Hafiz states a preference
- Hafiz corrects the agent's plan
- a review layer decision is made
- a new gap or source-of-truth file is identified

## Router Implementation Guidance

The lifecycle hook may inject workflow skill hints, but it should stay
conservative:

- discussion and architecture prompts should avoid forced workflow skills
- short `proceed` should route through the last recommended step when state is
  available; if not available, use `$task-router`
- `approve` alone should not be guessed without prior approval context
- push/deploy/merge/PR words should trigger review unless clearly part of a
  previously approved safe bundle
- critical-domain words should trigger diagnosis-first behavior

The router can start as Markdown rules and eval cases. Only update code after
the model is reviewed.

## First Automated Eval Set

Decision: the first automated Agent OS tests should verify routing behavior,
not product behavior.

Initial cases:

- discussion must not trigger commit
- `proceed next` follows the last clear recommendation
- `approve` follows the last exact approval request
- bundled commit+push works only when explicitly asked
- deploy cannot be bundled by default
- payment/auth/invoice/mobile API prompts route to diagnosis first
- `.env*` and `live/` stay blocked

These tests protect how Codex/Claude behave with Hafiz. Product tests still
protect product behavior.

## Open Questions

- None for the first routing model draft.
