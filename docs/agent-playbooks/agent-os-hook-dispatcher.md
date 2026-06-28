# Agent OS Hook And Dispatcher

Status: draft for internal Sifututor Agent OS use.

Use this file to understand the Codex hook layer and how it suggests workflow
skills.

Plain meaning: this is the routing assistant. It helps Codex start with the
right context and likely skill, but it does not own the final decision.

## What This Layer Is

The hook layer is configured in:

```text
.codex/config.toml
```

The main implementation is:

```text
scripts/agent-checks/codex-lifecycle-hook.py
```

The hook runs automatically at certain Codex events. It can add context,
suggest a skill, check Koda health, remind Codex to save, and run guardrails
before Bash commands.

## What This Layer Is Not

The hook is not:

- a replacement for Hafiz approval,
- a replacement for agent judgment,
- a hidden executor,
- a deploy/commit/push tool,
- the source of product truth,
- allowed to bypass `AGENTS.md`.

The hook should never silently perform expensive state changes.

## Hook Events

| Event | When it runs | What it does |
| --- | --- | --- |
| `SessionStart` | Startup, resume, clear, or compact session start. | Loads Sifututor context and verifies Koda read/write health. |
| `UserPromptSubmit` | Every Hafiz prompt. | Detects project, active task, likely workflow skill, and relevant Koda memories. |
| `PreToolUse` | Before Bash commands. | Runs Bash guardrails before command execution. |
| `PostToolUse` | After Bash commands. | Records failed Bash commands for diagnostics. |
| `PreCompact` | Before context compaction. | Reminds Codex to snapshot or save meaningful context. |
| `Stop` | When Codex is about to stop. | Reminds Codex to save meaningful session state. |

## Dispatch Rule

Skill selection is:

```text
agent-owned, hook-assisted, Hafiz-overridable, and safety-constrained.
```

That means:

1. The hook suggests a workflow skill.
2. Codex reads the selected skill wrapper and linked playbook.
3. Codex confirms whether the selected skill is actually right.
4. Hafiz can override the route.
5. Safety rules force stricter behavior when needed.

The hook is the first guess, not the boss.

## What UserPromptSubmit Adds

For a non-trivial prompt, `UserPromptSubmit` can add:

- detected project,
- active task summary,
- selected workflow skill,
- reason for selected skill,
- required actions,
- relevant Koda memories,
- communication defaults,
- standing task access reminder,
- critical-lane reminder.

This is why a Codex turn may start with a message like:

```text
Sifututor workflow dispatcher:
- Detected project: Sifututor.
- Selected workflow skill: $product-design.
- Reason: Prompt is asking for product design...
```

## Dispatch Inputs

The dispatcher uses these signals:

| Signal | Example |
| --- | --- |
| Explicit skill request | `$commit`, `$verify`, `$product-design` |
| Protected action words | push, deploy, merge, PR, commit |
| Risk domains | auth, payment, invoice, commission, migration, mobile API |
| Intent words | fix, verify, QA, review, diagnose, save, brainstorm |
| Discussion words | explain, discuss, why, what should, architecture |
| Prompt length / non-triviality | Longer prompts are routed instead of ignored. |
| Project hint | `sifu-tutor`, `ripple-suite`, tutor app, parent app, LLS |
| Smart resume signals | `continue`, `go next`, recent Session Map, or local commits ahead of GitHub |
| Koda search | Relevant durable lessons are injected when safe. |

The dispatcher should not route by keyword alone. The agent must still inspect
context.

## Dispatch Priority

Use this mental model:

| Priority | Route |
| --- | --- |
| 1 | Forbidden or unsafe behavior is blocked by rules and guards. |
| 2 | Critical lanes route to read-only diagnosis before implementation. |
| 3 | Explicitly requested skill wins if safe. |
| 4 | Push, deploy, merge, PR route to review first. |
| 5 | Commit routes to commit playbook and exact file-list approval. |
| 6 | Verify, QA, review, diagnose route to their workflow skills. |
| 7 | Product/workflow design routes to product-design. |
| 8 | Normal non-trivial work routes to task-router. |
| 9 | Tiny trivial prompts may need no workflow skill. |

## Current Skill Mapping

| Prompt intent | Suggested skill |
| --- | --- |
| Start, continue, proceed, implement | `$task-router` |
| Bug, broken behavior, failing test, root cause | `$diagnose` |
| Verify, run checks, prove it works, Gate 2A | `$verify` |
| QA, smoke, regression, visual/manual check | `$qa` |
| Review, audit, pre-commit risk check | `$review` |
| Quick check, health check, workflow doctor | `$quick-check` |
| Commit, stage, prepare commit | `$commit` |
| Save session, wrap up, finish session | `$save-session` |
| Handoff to Claude, Codex, or human | `$handoff` |
| Snapshot, pause, compact/context save | `$snapshot` |
| Session map, mindmap, progress board, return path | `$session-map` |
| Push, deploy, merge, PR | `$review` first, then explicit approval |
| Brainstorm, PRD, UX spec, build prompts, major redesign | `$product-design` |

## Short Replies

Short replies depend on visible conversation context.

| Hafiz says | Hook/agent meaning |
| --- | --- |
| `proceed` | Continue the last clear safe recommendation. |
| `proceed next` | Continue the next review/action from visible chat context. |
| `approve` | Execute the last exact approval request only. |
| `what next` | Give one next recommended action. |

For continuation-like prompts, the hook should add a smart resume hint when
there is an active Session Map or local Git state waiting. Codex should read
the Session Map Reference Pack first, then say whether the map matches the
prompt. If it matches, continue from the map. If it does not, treat the prompt
as new work unless Hafiz asks to resume the old map.

The hook should not guess an old hidden approval. If visible context is missing
or risky, Codex must ask a short clarification.

## Critical Lane Override

Even if a prompt looks simple, these domains force stricter routing:

- auth,
- payment,
- invoice,
- commission,
- migration,
- deployment,
- production data,
- mobile API contract.

Default behavior:

```text
read-only diagnosis first,
recommendation second,
implementation only after Hafiz approves.
```

## Hook Boundaries

The hook may:

- add context,
- suggest a skill,
- inject Koda memories,
- check Koda health,
- remind Codex about save-session,
- remind Codex about session-map,
- block unsafe Bash patterns through guard scripts.

The hook must not:

- commit,
- push,
- merge,
- open a PR,
- deploy,
- mutate production,
- read `.env*`,
- reveal secrets,
- modify `live/`,
- approve its own action,
- override Hafiz.

## When To Change The Dispatcher

Change the dispatcher only when:

- a routing mistake repeats,
- a new workflow skill is added,
- a safety boundary changes,
- a prompt category is consistently misclassified,
- Hafiz confirms a new short-command meaning,
- an eval fixture is added or updated to lock the behavior.

Do not change dispatcher code just because one prompt was awkward. First update
the docs or add a scenario example unless the bug is clearly dangerous.

## Required Checks After Dispatcher Changes

Run the focused checks first:

```bash
scripts/agent-checks/agent-os-conversation-fixture-runner.py
scripts/agent-checks/agent-os-eval-runner.py
scripts/agent-checks/agent-os-health.sh
```

Before commit, also run:

```bash
scripts/agent-checks/pre-commit-guard.sh
git diff --check
```

## Related Docs

- [codex-hook-trust.md](codex-hook-trust.md): what hook commands Hafiz should
  trust.
- [agent-os-skill-registry.md](agent-os-skill-registry.md): what workflow
  skills exist and what they do.
- [agent-os-routing-model.md](agent-os-routing-model.md): routing model and
  prompt categories.
- [agent-os-approval-gates.md](agent-os-approval-gates.md): approval
  boundaries.
- [agent-os-infrastructure.md](agent-os-infrastructure.md): full Agent OS
  infrastructure map.
