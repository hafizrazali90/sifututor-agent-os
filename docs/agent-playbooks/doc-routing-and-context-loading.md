# Doc Routing And Context Loading

Use this when deciding which docs, playbooks, project files, or memories the
agent must read before acting.

Plain meaning:

```text
Do not make the agent read the whole library.
Make it open the right books for the current job.
```

This playbook exists because the Agent OS now has many docs.
A useful doc system needs routing, not volume.

## Core Rule

The agent should load context in layers:

```text
minimum contract -> current task route -> required docs -> triggered docs
-> current evidence
```

In normal words:

```text
Start with the shared rules.
Decide what kind of work this is.
Read the required docs for that kind of work.
Open extra docs only when the task trigger appears.
Then verify the current repo/tool state before acting.
```

Do not solve context misses by reading every file.
That wastes tokens, increases confusion, and makes the agent more likely to
miss the practical decision.

## Loading Levels

| Level | What it means | Examples |
| --- | --- | --- |
| Always | Small rules every agent needs. | `AGENTS.md`, current user instruction, nearest project `AGENTS.md` when editing a project. |
| Route required | Docs required by the chosen workflow. | `task-router.md`, `diagnose.md`, `commit.md`, `product-design.md`. |
| Triggered | Docs required only when a condition appears. | `TESTING.md` for user-facing work, UI/UX docs for SIMS UI, critical-lane docs for payments/auth/invoices/mobile API. |
| Evidence | Current state that proves what is true now. | `git status`, active task file, tests, browser evidence, PR/CI/deploy/monitoring state. |
| Deep reference | Detailed docs opened only when the first docs point there or the agent is blocked. | architecture notes, feature docs, old research, long historical reports. |

## Required Doc Matrix

Use this matrix after Task Router identifies the route.

| Work type | Must read first | Then read if triggered |
| --- | --- | --- |
| Any meaningful work | `AGENTS.md`, current user instruction, active Session Map when resuming, relevant Koda memories when available. | Project `AGENTS.md` when editing inside a project. `CLAUDE.md` is loaded for Claude automatically and adds only Claude mechanics; it is not a second contract. |
| Agent OS docs or workflow improvement | `task-router.md`, `agent-os-improvement-loop.md`, this doc, `doc-owner-route-index.md`, relevant owning playbook. | `agent-os-skill-registry.md`, `agent-os-evals.md`, hook/dispatcher docs, parity docs, Koda, Session Map. |
| Documentation-only change | The owner doc of the section being edited; `commit.md` when it will be committed. | `doc-owner-route-index.md` when adding, moving, or archiving an Agent OS doc; `release-documentation.md` only when the doc is staff-facing. No deployment, incident, or implementation-readiness docs. |
| Brainstorming or product design | `product-design.md`, `planning-artifacts.md`, relevant feature/project docs. | `ai-implementation-readiness.md` for handoff/cross-module/critical workflows; UI/UX docs for interface design. |
| Bug or staff symptom | `diagnose.md`, `task-router.md`, current project rules. | Planner context for staff-reported SIMS/mobile issues; `related-impact-audit.md`; `TESTING.md`; feature docs. |
| User-facing feature or fix | `task-router.md`, `verify.md`, `qa.md`, project rules, `TESTING.md` when present. | UI/UX docs, feature docs, E2E specs, `agent-os-evidence-model.md`, release communication rules. |
| Critical lane | `diagnose.md`, `ai-implementation-readiness.md`, `agent-os-approval-gates.md`. | Domain docs for auth, payments, invoices, commission, migration, deploy, or mobile API contract; safe read-only access map. |
| Verify or QA | `verify.md` or `qa.md`, `agent-os-evidence-model.md`, project rules. | `TESTING.md`, feature docs, Playwright/mobile docs, monitoring/access docs if evidence depends on them. |
| Review, push, PR, merge, deploy, or live claim | `review.md`, `no-mistakes-lite.md`, state/evidence docs. | `push-pr-ci-automation.md`, `release-deploy-live-monitoring.md`, `incident-workflow.md`, Session Release Ledger when multiple fixes exist. |
| Commit | `commit.md`, `review.md`, `no-mistakes-lite.md`, current git diff/status. | Session Release Ledger for multiple fixes; release communication docs for staff-facing changes. |
| Save, handoff, snapshot, or continuation | `save-session.md`, `handoff.md` or `snapshot.md`, `session-map.md`. | Koda memory docs, Mission Ledger when the item is future/parked, Git/PR/deploy state. |
| Project adoption or staff rollout | `project-adoption.md`, `agent-os-rollout-readiness.md`, `agent-os-installation.md`, capability model. | staff quick start, project profile, access registry, parity/adapter docs. |

## Trigger Rules

Open these docs when the trigger is present.

| Trigger | Open |
| --- | --- |
| `sifu-tutor` browser UI, SIMS page layout, staff-facing copy, visual QA | `sifu-tutor/docs/ui-ux/README.md` and the relevant feature docs it points to. |
| User-facing behavior changes | Project `TESTING.md` if present, existing E2E specs, `test-coverage.md`, `agent-os-evidence-model.md`. |
| Staff-reported SIMS/tutor/parent app issue | Planner intake context when available, then normal engineering route. |
| Auth, payment, invoice, commission, migration, deploy, production data, or mobile API contract | Critical-lane diagnosis docs and approval gates before implementation. |
| Multiple fixes, branches, PRs, or deploy candidates in one chat | `session-release-ledger.md` and the active Session Map. |
| Long, confusing, or multi-goal session | `session-map.md`; update the current map before going deeper. |
| Agent OS behavior change | `agent-os-improvement-loop.md`, owning playbook, skill registry, evals, and Session Map. |
| Claude/Codex behavior mismatch | `agent-os-parity-contract.md`, `agent-os-skill-registry.md`, adapter docs, and evals. |
| Tool/access uncertainty | `agent-os-capability-model.md`, `agent-access-map.md`, relevant probe/wrapper docs. |
| Production/live-state claim | Git/PR/deploy evidence, `release-deploy-live-monitoring.md`, monitoring docs. |

## Skip Rules

Do not load extra docs just because they exist.

Skip deep docs when:

- the task is a tiny typo or formatting-only change;
- the doc is about a different project;
- the doc is historical and the current route already has a source of truth;
- the task is discussion-only and Hafiz has not asked to document or implement;
- the next action is only a local commit of an already-approved exact bundle.

Plain version:

```text
Context should help the agent decide and act.
If a doc does not change the decision, proof, safety boundary, or next action,
do not spend context on it yet.
```

## Readback Requirement

After loading docs for a meaningful task, the agent should be able to say:

```text
I read the route docs for this work.
The important rule is...
The next action is...
```

Do not list every file mechanically in normal conversation.
Use natural language unless Hafiz asks for the audit trail.

Example:

```text
I treated this as Agent OS workflow improvement, so I used the improvement loop,
the skill registry, and evals. The practical rule is: update the owner doc, then
check the connected docs so the behavior does not drift.
```

## Missed-Doc Recovery

If the agent realizes it missed a relevant doc:

1. Stop before further edits if the missing doc may change the decision,
   safety boundary, evidence, or file scope.
2. Read the missed doc.
3. Compare it with what was already done.
4. Adjust the work if needed.
5. Say plainly what changed.
6. Add an eval or Koda lesson only if the miss is likely to repeat.

Plain version:

```text
Missing a doc is recoverable.
Pretending the doc was not needed is not.
```

## Knowledge Architecture

The Agent OS is a linked-Markdown library with progressive disclosure. There
is no graph database, generator, or service behind it: entry points are small,
and everything else is opened by path when a task triggers it.

### Entry Points Per Model

Verified 2026-09-22 with fresh `claude -p` and `codex exec` runs on marker
files; the record is in [agent-os-research.md](agent-os-research.md).

| Reader | Loaded at launch | How it reaches the shared rules |
| --- | --- | --- |
| Codex CLI (0.154) | `~/.codex/AGENTS.md`, then `AGENTS.md` from the Git root down to the cwd, at most one file per directory, 32 KiB across the chain (the file that crosses the cap is truncated and later files are dropped). | Natively. Inside a nested product repo it loads only that repo's chain, so every project `AGENTS.md` must link to `../AGENTS.md`. Codex never reads `CLAUDE.md`. |
| Claude Code (2.1.222) | `~/.claude/CLAUDE.md`, `CLAUDE.md` in the cwd and every parent directory, and their `@imports`; auto-memory. | Through the `@AGENTS.md` line in `CLAUDE.md`. This version does not read `AGENTS.md` on its own; from 2.1.277 Claude reads it only where no `CLAUDE.md` exists, and the import is documented as never double-loading. Sub-project `CLAUDE.md` and `AGENTS.md` are not loaded at the umbrella cwd; `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` stays unset by decision. |
| Kilo Code | `.kilo/agents/sifututor-agent-os.md` | Reads `AGENTS.md` first, then the `.agents/skills/` wrappers. |
| Future adapter | One small file for that tool | Imports or opens `AGENTS.md` first, adds tool mechanics only, stays under 8 KiB, and passes scenario NAV-11 of the navigation check. |

Skill bodies, playbooks, project profiles, Session Maps, handoffs, and Koda
are never loaded at launch by any model. Skill names and descriptions are.

### Layers

| Layer | Files | Loaded | Holds |
| --- | --- | --- | --- |
| Shared contract | `AGENTS.md` | always | rules every session needs; pointers to owners |
| Adapters | `CLAUDE.md`, `~/.claude/CLAUDE.md`, `.kilo/agents/*`, `.agents/skills/*/SKILL.md`, `~/.claude/skills/*` | adapter file always; skill body on invocation | tool mechanics and command names only |
| Router | `task-router.md`, this doc, `doc-owner-route-index.md` | when work starts | route, required docs, owner map |
| Owner playbooks | `docs/agent-playbooks/*.md` | when the route or a trigger names them | one owner per rule |
| Project contracts | `<project>/AGENTS.md`, `<project>/CLAUDE.md`, `project-profiles/*.md` | when working in that project | project-specific rules, kept near the project |
| Runtime state | `.claude/tasks/active.json`, Session Maps, ledgers, handoffs, `.agent-os/` | on demand | current truth, never instructions |
| Durable memory | Koda | on search | lessons and corrections, never copies of docs |
| Archive | `archive/`, historical reports | never automatically | past record; overrides nothing |

### Rules

- One owner per rule, named in the owner index. Other files link to the owner
  and do not restate it. Adapters never carry a rule that is not already in
  `AGENTS.md` or a playbook.
- Budgets: `AGENTS.md` at most 16 KiB, `CLAUDE.md` at most 8 KiB, any adapter
  file at most 8 KiB, root plus project `AGENTS.md` at most 32 KiB. Entry files
  hold no dated status, rollout notes, or tables that a config file already
  owns; those belong to the owner doc or the config itself.
- `@import` loads at launch, so `CLAUDE.md` imports `AGENTS.md` and nothing
  else. Playbooks are referenced by path, never imported.
- Naming: playbooks are lowercase-kebab `.md` files at the top of
  `docs/agent-playbooks/`; Agent OS wide docs keep the `agent-os-` prefix;
  project profiles live under `project-profiles/`, templates under
  `templates/`, retired material under `archive/` with its original name.
- A new doc is justified only through
  [skill-quality-and-pruning.md](skill-quality-and-pruning.md), and the owner
  index changes in the same commit.
- Archive when a doc has no active route, no inbound link, and a superseding
  owner: `git mv` it into `archive/` and move its index entry to the historical
  list. Delete only after one audit cycle with no recall need. Historical docs
  never override `AGENTS.md`, active playbooks, or current Git state.
- Links are relative Markdown links and must resolve.
  `scripts/agent-checks/agent-os-doc-navigation-check.py` runs inside
  `agent-os-health.sh` and fails on broken links or imports, unindexed
  playbooks, adapter drift, budget overruns, archived docs linked from the
  entry layer, or a scenario that loses its safety wiring.
- Sub-project rules are found by reading the nearest `AGENTS.md`, never by
  auto-loading every project into the umbrella session.
- Claude and Codex parity is tested by the navigation scenarios, by
  `agent-os-parity-fixture-runner.py`, and by the recorded live loading tests;
  rerun the live test when either CLI is upgraded.
- Context size is measured with a fresh `claude -p "..." --output-format json`
  at the umbrella root (prompt tokens are `input_tokens` plus the two cache
  fields) and with `codex exec` (`tokens used`). Record before and after in the
  PR whenever an entry file changes.

## What Future Automation Should Check

`agent-os-doc-navigation-check.py` already proves the static wiring. The
ideal future hook does not need to read every doc; it should warn when the
selected route is missing a required doc family.

Examples:

- commit request without `commit.md`
- Agent OS change without `agent-os-improvement-loop.md`
- user-facing product change without `TESTING.md` decision
- SIMS UI work without UI/UX docs
- push/deploy/live claim without review/evidence/state docs

These warnings should be guidance first.
Only secrets, forbidden paths, destructive actions, critical-lane implementation,
and hook/test bypasses should become hard blocks.
