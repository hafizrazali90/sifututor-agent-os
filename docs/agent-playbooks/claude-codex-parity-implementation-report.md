# Claude to Codex Parity Implementation Report

Last updated: 2026-05-26

This report tells the full story of the Claude Code to Codex parity work in the
Sifututor workspace: why we did it, what existed before, what would break if we
only added `AGENTS.md`, what we built, what was pushed, what was intentionally
left alone, and how future agents should continue from here.

The shorter runbooks in this folder are for day-to-day execution. This document
is the human-readable history and architecture explanation.

## Table Of Contents

- [Executive Summary](#executive-summary)
- [Current Operating Checklist](#current-operating-checklist)
- [Read This Based On Your Role](#read-this-based-on-your-role)
- [Key Files](#key-files)
- [1. The Original Idea](#1-the-original-idea)
- [2. What Claude Had Before We Started](#2-what-claude-had-before-we-started)
- [3. What Would Break With `AGENTS.md` Only](#3-what-would-break-with-agentsmd-only)
- [4. The Architecture Decision](#4-the-architecture-decision)
- [5. What We Built](#5-what-we-built)
- [6. Implementation Waves](#6-implementation-waves)
- [7. What Was Pushed](#7-what-was-pushed)
- [8. Team Inbox Decision](#8-team-inbox-decision)
- [9. Current Status](#9-current-status)
- [10. What Improved](#10-what-improved)
- [11. What Is Still Not Perfect](#11-what-is-still-not-perfect)
- [12. How To Switch Between Claude And Codex Now](#12-how-to-switch-between-claude-and-codex-now)
- [13. What Future Agents Should Read First](#13-what-future-agents-should-read-first)
- [14. Recommended Next Improvements](#14-recommended-next-improvements)
- [15. Glossary](#15-glossary)
- [16. The Human Summary](#16-the-human-summary)

## Executive Summary

Before this work, Claude Code had a mature hidden operating system in the
Sifututor workspace. It loaded global rules, parent workspace rules,
sub-project `CLAUDE.md` files, hook behavior, skills, active task files, and
Koda memories. Codex did not automatically get the same context.

The migration made that system explicit. The shared contract now lives in
`AGENTS.md` files, the reusable workflow lives in `docs/agent-playbooks/`, and
portable guardrails live in `scripts/agent-checks/`. Claude can still use its
skills and hooks, but Codex now has a readable path to the same behavior.

The end result is not perfect mechanical equivalence, because Claude and Codex
do not expose the same lifecycle hooks or skill system. It is practical parity:
both agents can read the same project rules, find the same active task state,
use the same Koda memory, run the same guard scripts, and follow the same
definition of done.

## Current Operating Checklist

Use this whenever starting meaningful work in the Sifututor workspace:

1. Start from `/Users/hafizrazali/Projects/Sifututor`.
2. Read the root `AGENTS.md`.
3. Read the target project's `AGENTS.md`.
4. Read the target project's `CLAUDE.md` for deep context.
5. Search Koda memory for the task unless the change is trivial.
6. Read `.claude/tasks/active.json` when present.
7. Use the relevant playbook in `docs/agent-playbooks/`.
8. Before committing, run:

```bash
../scripts/agent-checks/pre-commit-guard.sh
```

From the umbrella root:

```bash
scripts/agent-checks/pre-commit-guard.sh
```

9. Store durable Koda lessons or corrections before reporting complete.
10. Never push, deploy, open a PR, or bypass verification without explicit
    current-session approval from Hafiz.

## Read This Based On Your Role

### Hafiz

Read this report for the overall story. For the day-to-day state, use:

- `docs/agent-playbooks/parity-status.md`
- `docs/agent-playbooks/active-tasks.md`
- `docs/agent-playbooks/commit-plan.md`
- `docs/agent-playbooks/product-push-map.md`

The important thing to remember: the parity system is now versioned, pushed, and
usable. Remaining dirty files are mostly active product work, not missing parity
plumbing.

### Claude

Read `AGENTS.md` first even if you also load `CLAUDE.md`. The purpose is to
avoid drifting away from Codex. Then use your normal skills and hooks, but write
state into files and Koda so Codex can resume.

### Codex

Do not assume Claude's hidden context exists. Read the nearest `AGENTS.md`, then
project `CLAUDE.md`, then task state, then Koda. Use the playbooks when you
would otherwise guess what a Claude skill would have done.

### Future Developer

Use this document to understand the architecture. Use the project `AGENTS.md`
files and playbooks to understand how to work safely. Do not delete `.claude/`
just because Codex can read `AGENTS.md`; `.claude/` is still Claude's
orchestration layer.

## Key Files

| File | Purpose |
| --- | --- |
| `AGENTS.md` | Root shared operating contract for Claude, Codex, and future agents. |
| `<project>/AGENTS.md` | Project-specific shared rules. |
| `<project>/CLAUDE.md` | Deep project context and Claude-oriented reference. |
| `docs/agent-playbooks/README.md` | Index of all shared playbooks. |
| `docs/agent-playbooks/parity-status.md` | Current baseline status across projects. |
| `docs/agent-playbooks/switching-claude-codex.md` | How to hand work between Claude and Codex. |
| `docs/agent-playbooks/task-router.md` | Shared task routing behavior. |
| `docs/agent-playbooks/verify.md` | Gate 2A verification behavior. |
| `docs/agent-playbooks/qa.md` | QA and regression behavior. |
| `docs/agent-playbooks/commit.md` | Commit preparation behavior. |
| `docs/agent-playbooks/save-session.md` | Koda and handoff behavior. |
| `docs/agent-playbooks/active-tasks.md` | Current active task overview. |
| `docs/agent-playbooks/commit-plan.md` | What was pushed and what remains dirty. |
| `docs/agent-playbooks/product-push-map.md` | Product repo remotes, branches, and push state. |
| `scripts/agent-checks/pre-commit-guard.sh` | Portable guard for branch, sensitive path, and task-state checks. |

## 1. The Original Idea

The starting point was simple but important: Hafiz already had a strong Claude
Code setup in VS Code. Claude knew the projects, the rules, the workflow, the
hooks, the Koda memory system, the quality gates, and the sub-project context.

The new goal was not merely "make Codex read an `AGENTS.md` file." The real goal
was stronger:

> Be able to switch between Claude and Codex in VS Code without losing the
> workflow, memory, standards, task state, safety rails, or project knowledge.

In plain language, Hafiz wanted the two agents to act like different workers on
the same team, using the same notebook, same checklist, same memory, and same
definition of done.

The target was "close to 100%" parity. We knew true 100% parity is not possible
because Claude Code and Codex do not expose exactly the same lifecycle hooks,
skill system, or context-loading behavior. But we can get close by making the
shared system explicit and portable.

## 2. What Claude Had Before We Started

Claude Code had a layered system. It was not just reading one file.

### 2.1 Global Claude Layer

Claude automatically loaded global instructions from `~/.claude/CLAUDE.md`.
That file contained identity, server infrastructure notes, branch conventions,
TDD rules, quality gates, and critical safety rules.

Claude also had access to global workflow history in
`~/.claude/WORKFLOW-CHANGELOG.md`, plus project memory indexes under
`~/.claude/projects/.../memory/MEMORY.md`.

This meant Claude started every session with context Codex would not naturally
have.

### 2.2 Umbrella Workspace Layer

At `/Users/hafizrazali/Projects/Sifututor`, Claude loaded the umbrella
`CLAUDE.md`. That file described the workspace, sub-projects, architecture, MCP
usage, and the Koda protocol.

The workspace also had `.claude/settings.json` and
`.claude/settings.local.json`. Those were important because Claude used them to
load additional directories, configure hooks, and enforce permissions.

### 2.3 Sub-Project Layer

Claude loaded many sub-project `CLAUDE.md` files through
`additionalDirectories`.

Examples:

- `ripple-suite/CLAUDE.md`
- `sifu-tutor/CLAUDE.md`
- `sifututor_tutor/CLAUDE.md`
- `sifututor_parent/CLAUDE.md`
- `lls/CLAUDE.md`

This was a major parity problem. Claude could be launched from the parent
workspace and still know project-specific rules. Codex normally reads only the
nearest `AGENTS.md`.

### 2.4 Koda Runtime Memory Injection

Claude had a Koda context injection hook. On user prompt submit, it searched
memory, selected relevant entries, and injected them before Claude answered.

This is one of the most important differences between Claude and Codex. Claude
was not only reading static files. It was also getting dynamic memory context at
runtime.

Without a workaround, Codex would repeat old mistakes Claude had already learned
from.

### 2.5 Hooks

Claude had hooks for:

- Koda context injection
- branch name validation
- conventional commit validation
- friction logging
- workflow gate checks
- quality gate reminders
- memory flush
- session start banners

Some hooks were global or parent-level. Some were project-level.

This mattered because some behavior was not "agent discipline"; it was enforced
by scripts. For example, workflow gates could block commits when required steps
were not complete.

### 2.6 Skills

Claude had many workflow skills, including:

- task routing
- verify
- QA
- commit
- save session
- generate tests
- regression test
- code review
- release notes
- diagnose
- handoff
- snapshot

These were not decorative. They were the actual operating system for the
workflow.

Codex cannot invoke Claude's Skill tool directly. That was another core parity
gap.

### 2.7 MCP Servers

The important MCP servers were:

- Koda memory
- Neon
- Chrome DevTools
- Figma
- Wasabi for LLS

Koda was the load-bearing one. It stores durable lessons, corrections, and
cross-session project knowledge.

## 3. What Would Break With `AGENTS.md` Only

The first big realization was that adding `AGENTS.md` alone would not give
Codex the same system.

Here is what would degrade:

- Codex would not automatically get Koda memory on every prompt.
- Codex would not get Claude's `additionalDirectories` cascade.
- Codex would not invoke Claude skills.
- Codex would not automatically flush memory on session end.
- Codex would not see active task state unless told to read it.
- Codex would not know project-specific financial or safety rules unless they
  were duplicated or moved into shared files.
- Codex might modify `live/` or other sensitive paths unless the rule was made
  explicit.
- Codex might use HEREDOC commit messages that Claude's commit hook rejects.
- Codex might miss financial-module human review requirements.

So the right solution was not one file. It was a portable shared workflow layer.

## 4. The Architecture Decision

We settled on a clear separation:

> `AGENTS.md` is the shared contract. `CLAUDE.md` is deep technical reference.
> `.claude/` remains Claude orchestration.

That means:

- Rules both agents need go into `AGENTS.md`.
- Deep project context stays in `CLAUDE.md`.
- Claude-only mechanics stay in `.claude/`.
- Codex-readable workflow playbooks live in `docs/agent-playbooks/`.
- Guard scripts live in `scripts/agent-checks/`.
- Koda remains the shared long-term memory layer.

This is the anti-drift contract. If a rule applies to both Claude and Codex, it
belongs in `AGENTS.md`. If `CLAUDE.md` needs to mention it, it should point to
`AGENTS.md` instead of restating it.

## 5. What We Built

### 5.1 Root Workspace `AGENTS.md`

We created a root `AGENTS.md` for the umbrella workspace.

It contains:

- universal safety rules
- branch naming
- commit format
- TDD and gate rules
- Koda memory obligations
- project-specific lookup rules
- shared guard script references
- shared playbook references

This gives Codex a starting point when launched from the workspace root.

### 5.2 Global Codex Contract

We added the Codex operating contract under `~/.codex/AGENTS.md`.

That gives Codex machine-level behavior similar to the Claude global layer:

- treat repo `AGENTS.md` as the shared contract
- do not push or deploy without explicit current-session approval
- never bypass hooks
- search Koda at task start for non-trivial tasks
- store durable lessons before reporting complete
- use the standard completion report shape

### 5.3 Per-Project `AGENTS.md`

We created or upgraded project-level `AGENTS.md` files.

Projects covered:

- `sifu-tutor`
- `ripple-suite`
- `sifututor_tutor`
- `sifututor_parent`
- `lls`
- `lls-frontend`
- `lls-mobile`
- `creative-hub`
- `team-inbox`
- `finch-inbox`

These files make each project safer for Codex to work in without relying on
Claude's hidden context cascade.

### 5.4 Shared Agent Playbooks

We created `docs/agent-playbooks/` as the Codex-readable equivalent of the core
Claude workflow skills.

Important files:

- `README.md`
- `task-router.md`
- `verify.md`
- `qa.md`
- `commit.md`
- `save-session.md`
- `switching-claude-codex.md`
- `quick-check.md`
- `active-tasks.md`
- `parity-status.md`
- `commit-plan.md`
- `product-push-map.md`
- `lls-workflow-migration.md`
- `workflow-rollout-cleanup.md`

The playbooks do not replace Claude skills. They let Codex and future agents
follow the same workflow when they cannot invoke Claude's Skill tool.

### 5.5 Shared Guard Scripts

We added `scripts/agent-checks/`.

The key guard is:

```bash
scripts/agent-checks/pre-commit-guard.sh
```

From inside a project:

```bash
../scripts/agent-checks/pre-commit-guard.sh
```

It checks:

- branch naming
- sensitive paths
- active task state

This is the portable fallback while Claude and Codex hook behavior differs.

### 5.6 Task State Baseline

We standardized `.claude/tasks/active.json` across projects.

This matters because task state should live in files, not in one agent's chat
memory. When Claude hands work to Codex, or Codex hands work back to Claude,
both can read the same active task pointer.

### 5.7 LLS Workflow Migration

LLS was a special case. It had been created by another developer and used a
Superpowers-style workflow, not the Sifututor Claude workflow.

We decided not to preserve that difference as the desired architecture. LLS was
migrated toward the shared task-state model.

This was documented in:

- `docs/agent-playbooks/lls-workflow-migration.md`
- `lls/AGENTS.md`
- `lls/.claude/tasks/active.json`
- LLS workflow skills

### 5.8 Anti-Drift Cleanup

We cleaned up duplication between `AGENTS.md` and `CLAUDE.md`.

The idea is:

- `AGENTS.md` owns shared rules.
- `CLAUDE.md` keeps deep project reference.
- `CLAUDE.md` points to `AGENTS.md` for shared rules instead of restating them.

This reduces the chance that Claude and Codex drift apart over time.

### 5.9 Umbrella Git Repo

We created a private GitHub repo:

```text
hafizrazali90/sifututor-agent-os
```

This repo tracks only the shared workspace layer:

- root `AGENTS.md`
- root `README.md`
- `docs/agent-playbooks/`
- `scripts/agent-checks/`
- root `.gitignore`

It intentionally does not track product repos, `live/`, `.claude/`, `.mcp.json`,
secret docs, caches, or generated files.

This keeps the shared AI workflow versioned without mixing it into product
repositories.

## 6. Implementation Waves

### Wave 1: Foundation

We created the global and root shared contract:

- global Codex contract
- root `AGENTS.md`
- initial shared playbooks
- guard scripts

This gave Codex a stable operating layer.

### Wave 2: Active Project Coverage

We added or upgraded `AGENTS.md`, hooks, settings, and task state in active
projects.

The main goal was that every project should have enough local instructions for
Codex to work safely.

### Wave 3: Anti-Drift

We cleaned up the relationship between `AGENTS.md` and `CLAUDE.md`.

This was not glamorous work, but it is important. If both files restate the same
rule, they will eventually disagree. The fix was to make `AGENTS.md` the owner
of shared rules.

### Wave 4: Secondary Projects

We covered projects that were less active or less formalized:

- `lls-mobile`
- `creative-hub`
- `team-inbox`
- `finch-inbox`

These got baseline shared playbook support, even if they do not yet have full
project-specific workflow skills.

### Wave 5: Cleanup

We removed the stale `.workflow-rollout/` staging directory after confirming it
was obsolete.

We also cleaned local artifact handling so generated Claude/Codex runtime files
do not constantly pollute `git status`.

## 7. What Was Pushed

### 7.1 Umbrella Repo

Pushed to:

```text
https://github.com/hafizrazali90/sifututor-agent-os
```

Key commits:

- `0574378 chore(workspace): initialize ai workflow repo`
- `f6d95f3 docs(workspace): update project commit plan`
- `9a9ca31 docs(workspace): refresh parity commit ledger`
- `3a6eba7 docs(workspace): add product push map`
- `f928701 docs(workspace): record product push results`
- `b51af98 docs(workspace): record team inbox archive and artifact cleanup`

### 7.2 Product Repos

Hafiz approved pushing product repo workflow commits to the `Sifututor`
organization.

Pushed:

- `sifu-tutor`
- `ripple-suite`
- `sifututor_tutor`
- `sifututor_parent`
- `lls`
- `lls-frontend`
- `lls-mobile`
- `creative-hub`
- `finch-inbox`

`team-inbox` was not pushed because its local branch was stale relative to
remote.

### 7.3 Important Push Caveat

`sifu-tutor` had an existing product fix commit on the branch head:

```text
d90d14ce4 fix(tutor-requests): restore staging lifecycle status
```

Because pushing a branch pushes the branch head, that commit went up with
`sifu-staging` together with the workflow commits.

This is documented so there is no hidden surprise later.

## 8. Team Inbox Decision

`team-inbox` required special care.

Local `main` was:

- ahead by 1 local workflow commit
- behind remote by 344 commits

Remote `main` had evolved into the newer Finch-style codebase and already
contained a GitHub-workflow `AGENTS.md`.

Pushing the old local `team-inbox` baseline would have been wrong. Instead we:

1. Preserved the stale local commit on:

```text
backup/team-inbox-stale-parity-20260526
```

2. Aligned local `main` to `origin/main`.

This keeps the old work recoverable without polluting the real remote branch.

## 9. Current Status

### 9.1 Parity Baseline

All active workspace projects now have the shared baseline:

- project `AGENTS.md`
- task state pointer
- hooks or equivalent guard path
- shared playbook references
- Koda memory rules

### 9.2 Guard Verification

The shared guard passed in all ten projects:

- `sifu-tutor`
- `ripple-suite`
- `sifututor_tutor`
- `sifututor_parent`
- `lls`
- `lls-frontend`
- `lls-mobile`
- `creative-hub`
- `team-inbox`
- `finch-inbox`

### 9.3 Remaining Visible Local Work

Remaining dirty files are real project work or local context, not parity
plumbing.

Important examples:

- `sifu-tutor`: active QA/bugfix files, browser-test YAML, manual QA docs,
  ST-40 task file.
- `ripple-suite`: memory index, old task archives, one-off ops script.
- `sifututor_tutor`: active auth first-run product work and Maestro QA files.
- `sifututor_parent`: untracked `e2e/`.
- `lls-frontend`: modified `package-lock.json`.

These should be reviewed as product work, not bundled into parity commits.

## 10. What Improved

### 10.1 Codex Can Now Start Safely

Codex now has a clear sequence:

1. Read nearest `AGENTS.md`.
2. Read project `CLAUDE.md` for deep context.
3. Search Koda memory.
4. Read `.claude/tasks/active.json`.
5. Use `docs/agent-playbooks/`.
6. Run guard scripts before commit.

That gets Codex much closer to Claude's starting point.

### 10.2 Claude And Codex Share One Contract

Before this, Claude had the richer system and Codex would have been the weaker
side. Now both agents can follow the same shared contract.

### 10.3 Task State Is File-Based

The active task is no longer only in Claude's mind or a chat transcript. It is
in `.claude/tasks/active.json` and the referenced task file.

### 10.4 Koda Is Explicit

Codex cannot rely on Claude's automatic memory injection, so the obligation is
now written down:

- search Koda at task start
- store corrections immediately
- store non-obvious lessons before completion
- use valid Koda schema values

### 10.5 Local Artifact Noise Is Lower

We added ignore rules for local agent artifacts in:

- `ripple-suite`
- `sifututor_tutor`
- `lls`

This makes `git status` more meaningful. Real product work still remains
visible.

## 11. What Is Still Not Perfect

This system is close to parity, but not magic.

### 11.1 Codex Still Does Not Have Claude's Exact Hooks

Claude has lifecycle hooks like prompt submit, pre-compact, stop, and session
start. Codex does not currently mirror all of that behavior.

The workaround is explicit workflow instructions and guard scripts.

### 11.2 Codex Still Does Not Have Claude's Skill Tool

Codex can read the playbooks, but it cannot directly invoke Claude's Skill tool.

The playbooks are therefore written as readable procedures, not executable
skills.

### 11.3 Koda Search Must Be Habitual

Claude had automatic memory injection. Codex needs to remember to search Koda.

This is why the rule appears in global Codex instructions, root `AGENTS.md`, and
project `AGENTS.md`.

### 11.4 Some Projects Are Still Pre-Formalization

`lls-mobile`, `creative-hub`, and `team-inbox` do not yet have the same depth of
project-specific workflow skills as `ripple-suite`, `sifu-tutor`, or
`sifututor_tutor`.

They are safe enough to operate with shared playbooks, but deeper project
skills can be added later if their cadence justifies it.

## 12. How To Switch Between Claude And Codex Now

Before switching:

1. Update active task state.
2. Store Koda lessons and corrections.
3. Run the shared guard.
4. Mention files changed and commands run.
5. Tell the next agent which project `AGENTS.md` to read.

Claude to Codex:

- Claude should write state to files and Koda, not rely on hidden chat context.
- Codex should read `AGENTS.md`, `CLAUDE.md`, Koda, and active task state.

Codex to Claude:

- Codex should update task evidence and Koda.
- Claude should resume from files, not only from memory.

The detailed switching procedure is in:

```text
docs/agent-playbooks/switching-claude-codex.md
```

## 13. What Future Agents Should Read First

For a new agent session in the umbrella workspace:

1. `AGENTS.md`
2. `docs/agent-playbooks/README.md`
3. `docs/agent-playbooks/parity-status.md`
4. `docs/agent-playbooks/active-tasks.md`
5. The target project's `AGENTS.md`
6. The target project's `CLAUDE.md`
7. Koda memory search results

For push or repo status questions:

1. `docs/agent-playbooks/commit-plan.md`
2. `docs/agent-playbooks/product-push-map.md`

For LLS:

1. `docs/agent-playbooks/lls-workflow-migration.md`

## 14. Recommended Next Improvements

These are optional future hardening tasks:

1. Create Flutter-specific workflow skills for `lls-mobile` if it becomes more
   active.
2. Create project-specific workflow skills for `creative-hub` if the team uses
   it heavily.
3. Decide whether `team-inbox` should be archived, treated as legacy, or given a
   fresh parity commit on top of current remote.
4. Re-test native Codex hook behavior inside the VS Code extension once the hook
   path is stable.
5. Review whether tracked `.claude/memory/MEMORY.md` files should stay tracked
   or become generated local-only references.
6. Continue reducing duplicated shared rules from `CLAUDE.md` files whenever new
   drift appears.

## 15. Glossary

### `AGENTS.md`

The shared instruction file for AI coding agents. In this workspace it owns the
rules that both Claude and Codex must follow: safety, branch names, commit
format, Koda obligations, and workflow entry points.

### `CLAUDE.md`

The deeper project reference file. It can contain architecture, module details,
deployment notes, and Claude-specific context. It should not duplicate shared
rules already owned by `AGENTS.md`.

### `.claude/`

Claude's orchestration folder. It contains hooks, settings, skills, task state,
and sometimes memory or session files. Codex can read useful parts of it, but it
does not execute Claude's Skill tool directly.

### Active Task State

The file-based workflow pointer in `.claude/tasks/active.json`. It points to the
current task JSON file and tells agents what route and next step are active.

### Koda

The shared long-term memory system. It stores durable facts, lessons,
corrections, decisions, and preferences across Claude and Codex sessions.

### MCP

Model Context Protocol. MCP servers connect agents to tools like Koda memory,
Neon, Chrome DevTools, Figma, and Wasabi.

### Playbooks

Markdown procedures in `docs/agent-playbooks/`. They translate important Claude
skills into a form Codex and future agents can read and follow.

### Guard Scripts

Portable shell scripts in `scripts/agent-checks/`. They are the fallback
enforcement layer when Claude and Codex hooks do not behave identically.

### Anti-Drift

The rule that shared behavior should have one owner. If both `AGENTS.md` and
`CLAUDE.md` restate the same rule, they will eventually disagree. Shared rules
belong in `AGENTS.md`; `CLAUDE.md` should point to them.

### Practical Parity

The realistic goal. Claude and Codex cannot be mechanically identical because
their extension runtimes differ, but both can operate from the same contract,
state, memory, and verification process.

## 16. The Human Summary

Before this work, Claude was operating with a rich hidden system and Codex would
have entered the workspace almost blind by comparison.

After this work, the system is much more explicit:

- both agents have shared rules
- both agents can find task state
- both agents know where memory lives
- both agents have a common verification and commit path
- the workspace workflow is versioned in a private repo
- product repos have project-level agent contracts
- the remaining gaps are known and documented

The deepest change is not any single file. The deepest change is that the
workflow moved from "Claude knows this because Claude's environment injects it"
to "the workspace knows this, and any serious agent can read it."

That is what makes switching between Claude and Codex realistic.
