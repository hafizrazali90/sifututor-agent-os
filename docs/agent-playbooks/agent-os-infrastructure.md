# Agent OS Infrastructure

Status: draft for internal Sifututor Agent OS use.

This document explains how the Sifututor Agent OS is assembled.

Plain meaning: this is the map of the machine. It explains what is a skill,
what is a hook, what is a playbook, what is memory, what is a guard, and how
one Hafiz request moves through the system.

## Short Version

The Sifututor Agent OS has these layers:

| Layer | Plain meaning | Main location |
| --- | --- | --- |
| Operating contract | The shared rules agents must obey. | `AGENTS.md` |
| Project reference | Deep project context and Claude-specific orchestration. | `CLAUDE.md` in each project when present |
| Workflow skill | The job mode the agent uses, such as Task Router, Verify, QA, Commit, or Product Design. | `.agents/skills/*/SKILL.md` |
| Playbook | The actual written workflow steps behind a skill. | `docs/agent-playbooks/*.md` |
| Hook / dispatcher | The automatic layer that gives Codex startup context, prompt routing hints, and tool guardrails. | `.codex/config.toml`, `scripts/agent-checks/codex-lifecycle-hook.py`, `agent-os-hook-dispatcher.md` |
| Guard script | A local check that prevents unsafe or invalid actions. | `scripts/agent-checks/*` |
| Memory | Durable lessons, corrections, and preferences. | Koda through `scripts/agent-checks/koda` |
| State systems | Places that track work status and evidence. | GitHub, Plane, Planner, `.claude/tasks`, Mission Ledger |
| Evidence system | Rules for proving work like a developer/tester would. | `verify.md`, `qa.md`, `agent-os-evidence-model.md` |
| Install/check system | The portable baseline for applying and checking Agent OS files. | `agent-os-install-manifest.json`, `agent-os-health.sh` |

## What Is Sifututor-Made Vs External

| Component | Owner / source | Notes |
| --- | --- | --- |
| Root `AGENTS.md` | Sifututor Agent OS | Shared contract for Codex and Claude. |
| `docs/agent-playbooks/*.md` | Sifututor Agent OS | Human-readable workflow source of truth. |
| `.agents/skills/*/SKILL.md` | Sifututor Agent OS | Codex workflow skill wrappers that point to playbooks. |
| `.codex/config.toml` | Sifututor Agent OS config for Codex | Registers local Codex hooks for this workspace. |
| `scripts/agent-checks/*` | Sifututor Agent OS | Health checks, guardrails, eval runners, and Koda CLI wrapper. |
| Koda | Shared memory service used by Sifututor Agent OS | Stores durable lessons, not raw transcripts or secrets. |
| Claude Code skills | Claude-side workflow commands | Claude reads its own skill system and `CLAUDE.md`. |
| Codex system skills | OpenAI/Codex | Examples: `openai-docs`, `imagegen`, `skill-creator`. |
| Plugin skills | Plugin provider | Examples: Google Drive Docs/Sheets/Slides skills. |

Non-technical version:

```text
Sifututor owns the workflow rules.
Codex and Claude provide the agent runtime.
Hooks help route the request.
Skills choose the job mode.
Playbooks explain the job.
Guards stop dangerous actions.
Koda remembers durable lessons.
GitHub/Plane/Planner track different kinds of work.
```

## Core Terms

### Agent OS

The whole collaboration system: rules, skills, hooks, docs, memory, tools,
checks, and state tracking.

### Workflow

One route inside the Agent OS, such as bugfix, feature, product design, QA,
review, commit, release, or save-session.

### Workflow Skill

A named Codex job mode.

Examples:

- `$task-router`
- `$diagnose`
- `$verify`
- `$qa`
- `$review`
- `$commit`
- `$product-design`
- `$save-session`

The skill wrapper is small. It usually says: "read this playbook and follow
it."

### Skill Wrapper

The local Codex skill file under `.agents/skills/<skill>/SKILL.md`.

Example:

```text
.agents/skills/commit/SKILL.md
```

### Playbook

The real instruction manual behind the skill.

Example:

```text
$commit skill wrapper -> docs/agent-playbooks/commit.md
```

### Hook / Dispatcher

The automatic Codex layer that runs at session start, prompt submit, tool use,
compaction, and stop.

Hooks should help the agent. They should not become invisible magic. The agent
is still responsible for confirming the route.

### Guard

A script or rule that blocks unsafe or invalid actions.

Examples:

- block `.env*`, secrets, and `live/`
- check branch names
- check mission-ledger shape
- prevent commit without required checks
- run Agent OS health checks

### Koda

The durable memory layer for corrections, preferences, facts, and lessons.
Koda is not a task tracker and should not store secrets or raw transcripts.

### State System

A place that owns a specific kind of work state:

| System | Owns |
| --- | --- |
| GitHub | Engineering execution issues, PRs, code work. |
| Plane | Hafiz-visible mission status and broader progress. |
| Planner | Staff-reported intake context, not engineering source of truth. |
| Mission Ledger | Future/paused/contextual work not ready for GitHub or Plane. |
| `.claude/tasks` | Active task state for projects that use task files. |
| Koda | Durable lessons and preferences. |
| Git | Local and remote code history. |

## Workflow Skills

These are Sifututor Agent OS workflow skills, not default Codex skills.

| Skill | What it is for | Wrapper | Playbook | Claude equivalent |
| --- | --- | --- | --- | --- |
| `$task-router` | Start, classify, resume, or route work. | `.agents/skills/task-router/SKILL.md` | `docs/agent-playbooks/task-router.md` | `/task-router` or project router skill |
| `$diagnose` | Read-first debugging and root cause. | `.agents/skills/diagnose/SKILL.md` | `docs/agent-playbooks/diagnose.md` | `/diagnose` |
| `$verify` | Prove implementation works before QA/commit. | `.agents/skills/verify/SKILL.md` | `docs/agent-playbooks/verify.md` | `/verify` |
| `$qa` | Regression, smoke, browser, visual, or route-level QA. | `.agents/skills/qa/SKILL.md` | `docs/agent-playbooks/qa.md` | `/qa` |
| `$review` | Adversarial risk review before commit/push/PR/deploy. | `.agents/skills/review/SKILL.md` | `docs/agent-playbooks/review.md` | `/review` |
| `$commit` | Prepare or create a local commit. | `.agents/skills/commit/SKILL.md` | `docs/agent-playbooks/commit.md` | `/commit` |
| `$product-design` | Brainstorm, PRD, UX spec, backend contract, build prompts. | `.agents/skills/product-design/SKILL.md` | `docs/agent-playbooks/product-design.md` | `/lite-prd`, `/prd-clarifier`, `/prd-to-ux`, `/ux-to-prompts` |
| `$save-session` | Preserve durable close-out and next-step context. | `.agents/skills/save-session/SKILL.md` | `docs/agent-playbooks/save-session.md` | `/save-session` |
| `$handoff` | Handoff to Claude, Codex, or a human. | `.agents/skills/handoff/SKILL.md` | `docs/agent-playbooks/handoff.md` | `/handoff` |
| `$snapshot` | Snapshot context before pause or compaction. | `.agents/skills/snapshot/SKILL.md` | `docs/agent-playbooks/snapshot.md` | `/snapshot` |
| `$quick-check` | Check workflow health before starting work. | `.agents/skills/quick-check/SKILL.md` | `docs/agent-playbooks/quick-check.md` | `/quick-check` or doctor script |

## Who Determines The Skill

Skill selection is:

```text
agent-owned, hook-assisted, Hafiz-overridable, and safety-constrained.
```

| Decision layer | Responsibility |
| --- | --- |
| Hook / dispatcher | Makes the first routing guess from the prompt. |
| Agent | Confirms or corrects the route after reading context. |
| Hafiz | Can override naturally at any time. |
| `AGENTS.md` and safety rules | Force stricter behavior when risk appears. |

The hook should not be treated as the boss. It is a routing assistant.

Example:

```text
Hafiz: "fix invoice missing"
Hook: likely selects diagnose or task-router.
Agent: confirms invoice is a critical lane and starts read-only diagnosis.
Safety rules: block implementation until Hafiz approves Phase B.
```

## Codex Hook Layer

Codex hooks are configured in:

```text
.codex/config.toml
```

The current hook events are:

| Hook | What it does |
| --- | --- |
| `SessionStart` | Loads Sifututor context and checks Koda health. |
| `UserPromptSubmit` | Adds task, memory, and workflow routing context before Codex answers. |
| `PreToolUse` | Checks Bash guardrails before commands. |
| `PostToolUse` | Records failed Bash commands for diagnostics. |
| `PreCompact` | Reminds Codex to snapshot/save before context compaction. |
| `Stop` | Reminds Codex to save meaningful session state. |

The hook can inject a selected workflow skill, but the agent must still decide
whether the route is correct.

## How A Prompt Moves Through The System

Normal flow:

```text
Hafiz prompt
-> Codex hook adds context and suggested skill
-> Codex reads the selected skill wrapper
-> skill wrapper points to the playbook
-> Codex confirms the route and risk lane
-> Codex uses tools and repo context
-> guard scripts block unsafe actions
-> verify/QA/review gather evidence
-> commit/push/deploy only happen with required approval
-> save-session/Koda/mission ledger preserve durable context
```

Non-technical version:

```text
Request comes in.
Reception routes it.
Worker checks if the routing is right.
Manual explains the job.
Tools do the work.
Safety checks stop dangerous moves.
Evidence proves the work.
Memory saves the lesson.
```

## Example: Commit Request

```text
Hafiz: "commit this"
Hook suggests: $commit
Codex reads: .agents/skills/commit/SKILL.md
Skill points to: docs/agent-playbooks/commit.md
Codex checks: git status, diff, guard script, exact file list
Approval needed: exact file-list approval
Forbidden: --no-verify, secrets, .env*, live/, push without explicit approval
Output: commit SHA, message, files committed
```

## Example: Staff Bug Report

```text
Outside intake: staff says "parent cannot see invoice"
Hook may suggest: $diagnose or $task-router
Codex confirms: staff symptom, not verified root cause
Quick diagnosis: read-only, enough evidence to know if engineering work exists
If likely dev work: create/link GitHub issue before implementation
If invoice/payment risk appears: stay critical-lane read-only until approved
Evidence: symptom, likely module, non-destructive proof, next action
```

## Example: Product Design Request

```text
Hafiz: "let's design invoice adjustment"
Hook suggests: $product-design
Codex reads: .agents/skills/product-design/SKILL.md
Skill points to: docs/agent-playbooks/product-design.md
Flow: brainstorm -> PRD if needed -> clarifier -> UX spec -> backend contract -> build prompts
Implementation: waits for approval, especially if invoices/payments are involved
```

## Tools And Capabilities

The Agent OS does not assume every agent can do everything.

Before relying on a tool, the agent should know whether it is available:

- filesystem and git
- browser or Playwright
- terminal commands
- Koda
- GitHub
- Plane
- Planner
- Google Drive
- production logs
- deploy access

Use [agent-os-capability-model.md](agent-os-capability-model.md) for the
detailed capability rules.

## Approval Boundaries

Some actions require exact or explicit approval even if the hook selected the
right skill:

| Action | Approval |
| --- | --- |
| Commit | Exact file-list approval. |
| Push, PR, merge | Explicit current-session approval. |
| Deploy | Explicit current-session approval. |
| Critical-lane implementation | Read-only diagnosis first, then approval. |
| Destructive action | Explicit approval and clear scope. |
| Secrets, `.env*`, `live/` modification | Not allowed. |

Use [agent-os-approval-gates.md](agent-os-approval-gates.md) for the full
approval model.

## Evidence And Checks

Evidence is how the agent proves work is real.

| Need | Source |
| --- | --- |
| Prove code works | `verify.md` |
| Prove user/staff journey works | `qa.md` and `agent-os-evidence-model.md` |
| Catch risk before commit/push | `review.md` |
| Commit safely | `commit.md` and `pre-commit-guard.sh` |
| Check Agent OS health | `agent-os-health.sh` |
| Check install baseline | `agent-os-install-manifest.json` and `agent-os-install.sh` |

## What This Doc Does Not Replace

This document is a map. It does not replace:

- `AGENTS.md` for rules,
- `.agents/skills/*/SKILL.md` for Codex skill entrypoints,
- `docs/agent-playbooks/*.md` for detailed workflows,
- `scripts/agent-checks/*` for executable checks,
- Koda for durable memory,
- GitHub, Plane, Planner, or Mission Ledger for their own state.

## Reading Path For Hafiz

If you want to understand the Agent OS without reading everything:

1. Read this file first.
2. Read [agent-os.md](agent-os.md) for the big picture.
3. Read [agent-os-workflows.md](agent-os-workflows.md) for day-to-day paths.
4. Read [agent-os-approval-gates.md](agent-os-approval-gates.md) for what
   needs permission.
5. Read [agent-os-capability-model.md](agent-os-capability-model.md) for what
   agents can actually do.
6. Read [README.md](README.md) when you want the full playbook index.

## Current Gap

This document explains the infrastructure. Use
[agent-os-skill-registry.md](agent-os-skill-registry.md) for the workflow skill
roster, and [agent-os-hook-dispatcher.md](agent-os-hook-dispatcher.md) for the
Codex hook and prompt-dispatch behavior.
