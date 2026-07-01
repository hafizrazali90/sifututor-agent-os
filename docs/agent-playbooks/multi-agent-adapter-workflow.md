# Multi-Agent And Adapter Workflow

Use this when deciding how Hafiz, Codex, Claude, future LLMs, subagents, human
developers, and staff should divide work inside the Sifututor Agent OS.

Plain meaning:

```text
The workflow decides what should happen. The agent/tool only decides how that
workflow is accessed.
```

This prevents every LLM from behaving like a different operating system.

## Core Decision

Workflow stage is the source of truth. Agent strength is a recommendation.

In normal words:

```text
First decide what stage the work is in. Then choose the best worker for that
stage.
```

This means any capable LLM can follow the Agent OS if it reads the shared
playbook, but the OS can still recommend the best tool for the job.

## Shared Core, Adapter, Role Boundary

| Layer | Meaning | Example |
| --- | --- | --- |
| Shared core | The rulebook every agent follows. | `task-router.md`, `verify.md`, `qa.md`, `commit.md`. |
| Adapter | The command/tool shape for one agent. | Claude `/verify`, Codex `$verify`, future LLM reading `verify.md`. |
| Role boundary | Who owns the decision or work. | Agent tests; Hafiz accepts business risk; staff report symptoms. |
| Parity | The behavior must match even when the adapter differs. | Commit-only approval never pushes in Claude, Codex, or another LLM. |

Non-technical version:

```text
The SOP is shared. Each worker may use a different form, app, or command, but
the approval, evidence, and done-state must stay the same.
```

## Stage First, Worker Second

Use this order:

1. Identify the workflow stage.
2. Read the shared playbook for that stage.
3. Choose the best worker/tool for the stage.
4. Use that worker's adapter.
5. Preserve state in the shared system, not only in the worker's chat.

Do not choose the worker first and let the worker invent the process.

Task Router owns the first pass of this decision. In normal words, Task Router
acts as the first-mate layer: it decides the workflow stage, then recommends
the best worker/tool for that stage. This keeps Codex, Claude, future LLMs,
subagents, and humans aligned without forcing every adapter to expose the same
commands.

## Workflow Stage Map

| Stage | Shared source | Best default worker | Why |
| --- | --- | --- | --- |
| Brainstorm / product thinking | `product-design.md`, `agent-os-workflows.md` | Claude or Codex, discussion-first | Needs options, tradeoffs, and Hafiz decision. |
| Build-ready brief | `ai-implementation-readiness.md`, `product-design.md` | Claude or Codex | Needs clear entry point, behavior, risks, and evidence plan. |
| Code implementation | project `AGENTS.md`, task playbook | Codex by default | Strong terminal/repo workflow and direct implementation loop. |
| Diagnosis | `diagnose.md` | Codex by default, Claude acceptable | Needs current repo evidence and root-cause discipline. |
| Verification | `verify.md` | Codex by default | Needs commands, safe tool checks, and evidence. |
| QA / human journey | `qa.md` | Codex by default, human/staff for unavailable checks | Agent should test first; humans handle subjective or unavailable paths. |
| Risk review | `review.md` | Codex or Claude | Needs adversarial thinking and state/evidence check. |
| Commit / push / PR | `commit.md`, `review.md`, push/PR playbooks | Codex by default | Needs exact file state and guard scripts. |
| Save / handoff | `save-session.md`, `handoff.md`, `snapshot.md` | Current agent | The agent holding context must preserve it before switching. |
| Narrow research | relevant playbook plus source docs | Subagent or main agent | Useful when bounded and source-based. |
| Product/risk decision | `agent-os-roles.md` | Hafiz | Agent recommends; Hafiz decides direction or accepts risk. |
| Staff report / feedback | Planner intake rules | Staff through Teams Planner | Staff provide reality/context, not engineering state. |

## Agent Strengths

These are recommendations, not hard ownership.

| Worker | Strong at | Should avoid |
| --- | --- | --- |
| Codex | Repo work, terminal checks, implementation, test loops, commits, scripted verification. | Making final business/risk decisions, guessing subjective UX acceptance. |
| Claude | Long-form thinking, product/design exploration, structured docs, explaining options. | Acting as engineering source of truth without current repo evidence. |
| Future LLM | Any stage it can support through the shared playbook and available tools. | Treating its native UI or prompt style as a new source of truth. |
| Subagent | Bounded research, focused review, source gathering, parallel inspection. | Owning final decisions, editing broad scope, relying on hidden context. |
| Human developer | Implementation/review when assigned, following shared playbooks. | Bypassing guards or keeping state only in private chat. |
| Hafiz | Product direction, business rules, priorities, risk acceptance, approvals. | Repeating checks agents can safely run. |
| Staff | Reports, reproduction context, screenshots, real-world feedback. | Direct Agent OS builder role, deploy/production/code approvals by default. |

## Adapter Rules

Adapters may differ in command shape, but not in behavior.

Allowed:

- Claude exposes four product-design commands while Codex exposes one
  `$product-design` skill.
- Codex uses CLI when MCP is unreliable.
- A future LLM reads the Markdown playbook directly.
- A human developer follows the checklist manually.

Not allowed:

- Claude asks for push approval but Codex pushes after commit-only approval.
- One agent treats unit tests as enough for a real staff UI workflow while
  another requires browser evidence.
- One tool stores noisy progress in Koda while another stores only durable
  lessons.
- One adapter treats local commit as pushed, merged, deployed, or live.

## Subagent Rules

Use a subagent only when the task is bounded.

Good subagent tasks:

- "Search these docs and summarize the relevant rule."
- "Review this diff for missing tests."
- "Compare these two playbooks for drift."
- "Find similar route names in the repo."

Bad subagent tasks:

- "Own this feature end to end."
- "Decide whether to deploy."
- "Rewrite the Agent OS."
- "Use broad credentials and see what you can find."

Subagents must return:

- sources checked
- findings
- confidence
- gaps
- recommended next action

The main agent remains responsible for final synthesis, edits, checks, and
close-out unless Hafiz explicitly assigns ownership elsewhere.

## Handoff Rules

Switching workers is allowed only when state is portable.

Before switching:

- update active task state or Session Map
- save durable Koda lessons when useful
- name exact files changed
- name commands/checks already run
- name current Git state
- name the next unblocked action
- preserve approval boundaries

Do not rely on hidden chat context.

Use [switching-claude-codex.md](switching-claude-codex.md),
[handoff.md](handoff.md), [snapshot.md](snapshot.md), and
[save-session.md](save-session.md).

## Drift Rule

When two agents behave differently, ask:

```text
Is the difference only adapter/UI/tooling, or did the workflow behavior change?
```

Adapter difference:

- command name changed
- UI looks different
- one tool uses CLI and another uses MCP

Workflow drift:

- approval boundary changed
- evidence standard changed
- state wording changed
- memory behavior changed
- critical-lane safety changed
- close-out quality changed

Adapter differences are documented. Workflow drift must be fixed through the
shared playbook, adapter wrapper, eval, hook, Koda lesson, or Session Map.

## Default Recommendation

Use this default unless Hafiz says otherwise:

```text
Stage decides the workflow. Codex executes repo-heavy work. Claude is useful for
deep product/design thinking. Subagents do bounded research/review. Hafiz owns
direction and risk. Staff report through Planner.
```

Easier explanation:

```text
Do not ask "which LLM do we like?" first. Ask "what stage is the work in?" Then
pick the worker that fits that stage.
```

## Close-Out

When using this workflow, report:

- the current workflow stage
- the recommended worker/tool
- why that worker/tool fits
- which shared playbook controls the behavior
- what state must be saved before switching
- what Hafiz still needs to decide
