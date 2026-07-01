# Agent OS Memory Architecture

Status: draft accepted as the Memory System v2 direction; migration/audit
scripts are not implemented yet.

This document defines how memory should be structured so the Sifututor Agent OS
gets faster, less noisy, and safer over time.

Simple version:

```text
Docs store the system.
Koda stores the lesson.
Chat stores the moment.
Git stores the proof.
```

Koda should not become a pile of notes. It should behave like a curated memory
layer that helps Codex, Claude, and Hafiz avoid repeated mistakes.

## Why Upgrade Memory

Koda is useful, but performance and relevance can degrade when:

- too many memories use broad tags
- duplicate memories describe the same rule
- old memories remain active after the system changes
- secrets or private payloads accidentally enter memory
- every task is saved as if it matters forever
- startup search pulls unrelated memories
- the chat-level MCP wrapper times out even though direct Koda works

The fix is not only better tooling. The memory structure itself needs stronger
taxonomy, lifecycle, retrieval order, and cleanup rules.

## Memory Layers

| Layer | Purpose | Home |
| --- | --- | --- |
| Working memory | Current conversation, current active step, temporary reasoning | chat, active task, scratch note |
| Hot memory | Small set of active rules needed at session start | curated Koda search or generated active memory pack |
| Episodic memory | Durable lessons, corrections, decisions, gotchas, tool behavior | Koda |
| Semantic memory | Stable rules, architecture, project contracts | `AGENTS.md`, `CLAUDE.md`, docs, README, `TESTING.md` |
| Procedural memory | How to do repeated work | playbooks, skills, scripts, templates |
| Archive memory | Old, superseded, historical, or low-relevance memories | Koda with lifecycle tags, or future archive store |

## Memory And Skill Ownership Rule

Use this rule before saving, moving, or duplicating information:

```text
Always-loaded memory should stay small.
Detailed procedures belong in skills and playbooks.
Durable lessons belong in Koda.
The current working story belongs in the Session Map.
Execution state belongs in GitHub, PRs, active task files, and git.
```

Plain version:

```text
Do not make every agent memorize the whole company handbook every morning.
Give the agent the core rules first, then let it open the right SOP when the
task needs it.
```

| Information | Correct home | Why |
| --- | --- | --- |
| Permanent universal behavior | Root `AGENTS.md` | Every agent must always follow it. |
| Repo-specific must-follow rules | Project `AGENTS.md` | Closest project rules should win. |
| Deep project reference or Claude-specific context | `CLAUDE.md` and project docs | Useful, but too detailed for universal rules. |
| Repeatable task procedure | Skills, playbooks, scripts, templates | Load only when the task needs that workflow. |
| Durable correction, preference, gotcha, or lesson | Koda | Future sessions should remember it without treating it as current task state. |
| Current multi-goal session story | Session Map | Helps this session and the next agent resume without becoming permanent memory. |
| Execution-ready engineering task | GitHub issue or PR | Owns coding work, review, CI, and code history. |
| Bigger parked goal or adjacent idea | Mission Ledger | Keeps future work visible without creating engineering noise too early. |
| Staff-reported symptom | Teams Planner / intake notes | Context for diagnosis, not root-cause truth. |

If a note seems to belong everywhere, distill it first:

1. Put the permanent rule in the owning doc or playbook.
2. Put the reusable procedure in a skill/playbook/script.
3. Put only the why or correction in Koda.
4. Put the live status in the Session Map or task tracker.

Do not duplicate the same rule across many files unless one file is clearly the
source of truth and the others only point to it.

## Memory Taxonomy

Every durable Koda memory should be easy to filter.

Required dimensions:

| Dimension | Examples | Why |
| --- | --- | --- |
| project | `sifututor`, `sifu-tutor`, `ripple-suite`, `lls` | Prevents unrelated project memories from dominating search. |
| domain | `agent-os`, `payment`, `qa`, `router`, `koda`, `mobile-api` | Lets agents retrieve the right type of lesson. |
| category | `decision`, `lesson`, `rule`, `preference`, `fact` | Matches Koda schema. |
| lifecycle | `active`, `superseded`, `stale`, `archived` | Prevents old truth from looking current. |
| risk | `critical`, `normal`, `low` | Helps agents know how strongly to verify before action. |

Koda currently supports `category`, `source`, `tags`, `project`, and `why`.
Until Koda has first-class lifecycle/risk fields, encode lifecycle and risk as
tags:

```text
lifecycle-active
lifecycle-superseded
lifecycle-stale
lifecycle-archived
risk-critical
risk-normal
risk-low
```

## What Belongs Where

| Situation | Correct Home |
| --- | --- |
| Hafiz corrects agent behavior | Koda plus docs if it changes the Agent OS |
| A rule becomes permanent | docs/playbook as source of truth; Koda keeps the lesson/why |
| A tool command is needed repeatedly | script or playbook |
| A task is merely in progress | active task, final response, or Plane; not Koda by default |
| A bug fix pattern will recur | Koda, with project/domain/risk tags |
| A memory contains a secret | sanitize or remove immediately; never quote the secret |
| Old memory disagrees with current docs/code | mark superseded or update; do not leave as active truth |

## Promotion And Demotion

Promote memory when a lesson becomes system behavior:

```text
Koda lesson -> docs/playbook/source-of-truth rule
```

After promotion, Koda should keep only the distilled why:

```text
Hafiz corrected X because Y kept causing friction. The rule now lives in docs/...
```

Demote memory when it is no longer current:

```text
active -> superseded -> archived
```

Do not delete useful history just because it is old. Mark it clearly so future
agents know it is background, not instruction.

## Retrieval Order

Agents should retrieve memory in this order:

1. exact project + exact domain + active lifecycle
2. exact project + broader domain
3. `sifututor` or `umbrella` cross-project Agent OS lessons
4. critical-risk memories for the lane
5. historical/superseded/archive memories only when investigating history

Do not start with a broad search if the task has a clear project and domain.
Broad search is useful for discovery, but it creates noise during execution.

## Active Memory Pack

The Agent OS should eventually generate a small active memory pack for startup.

It should contain:

- Hafiz working preferences
- current Agent OS routing rules
- approval gates
- communication style
- Koda/tooling gotchas
- critical safety boundaries
- project-specific active gotchas when a project is selected

It should not contain:

- raw chat transcripts
- old completed task summaries
- broad historical facts
- secrets or credentials
- memories marked `stale`, `superseded`, or `archived`

This can later become a generated Markdown or JSON file, such as:

```text
docs/agent-playbooks/generated/active-memory-pack.md
```

For now, keep it as a planned improvement.

## Cleanup And Audit

Memory needs regular cleanup.

An audit should find:

- duplicate memories
- memories with raw secrets, tokens, credentials, `.env*` values, or private
  payloads
- memories missing project/domain tags
- broad memories that should be split
- stale memories that should be marked superseded
- memories that should be promoted into docs
- memories whose source is wrong, such as agent inference marked `user-stated`

Future script idea:

```text
scripts/agent-checks/koda-memory-audit.py
```

The first version should be read-only and produce a report. Cleanup should be
separate and explicit.

Current fixture check:

```text
scripts/agent-checks/agent-os-koda-fixture-runner.py
```

This is a non-writing local check. It proves the basic memory discipline rules
without creating test memories: safe schema values, project/domain tags,
secret-like content rejection, vague-memory rejection, stale-memory safeguards,
and direct CLI fallback behavior.

## Performance Principles

To improve memory performance:

- keep startup searches narrow
- prefer active lifecycle tags
- use exact project and domain tags
- limit result counts
- avoid storing duplicate summaries
- promote permanent rules into docs
- archive or supersede old memories
- use direct fallback when the chat MCP wrapper times out

## Safety Rules

- Never store secrets, raw tokens, credentials, `.env*` values, production data,
  customer private messages, or private payload bodies.
- If unsafe memory is found, sanitize or remove it immediately.
- Do not quote the unsafe value while cleaning it.
- Koda is historical/trusted context, not automatic truth.
- Old memory must pass Context Authority before action.

## Migration Plan

Do this gradually.

1. Use the v2 taxonomy for all new Agent OS memories.
2. Add lifecycle/risk tags to new memories.
3. Build a read-only memory audit report.
4. Review duplicates, stale memories, and unsafe memories with Hafiz.
5. Promote stable rules from Koda into docs.
6. Mark old memories as superseded or archived.
7. Generate an active memory pack only after the taxonomy is stable.

Do not bulk rewrite all memories without a report and review.

## Current Decision

Adopt the Distilled Memory Model:

```text
Save less, but save sharper.
```

Koda stores behavior-changing lessons. Docs hold the system rules. Agents must
deduplicate, sanitize, tag, and verify memory before relying on it.
