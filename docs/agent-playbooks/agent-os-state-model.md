# Agent OS State Model

Use this document when deciding where task status, evidence, approvals, and
release state should live.

## Core Idea

The Agent OS has many places that can talk about work, but each place should
own a different kind of truth.

Plain version:

```text
Plane tells Hafiz what is happening.
GitHub tells developers what to build.
Planner tells us what staff reported.
Active task files tell agents what to do next.
Git proves what changed.
QA evidence proves whether it works.
Koda remembers the lesson.
```

No single tool should pretend to be all of these at once.

## Source Of Truth Map

| Source | Owns | Does Not Own |
| --- | --- | --- |
| Chat | current conversation, immediate instructions, clarifications | durable system rules, release truth, proof that code shipped |
| `AGENTS.md` | shared operating contract and hard rules | detailed project history |
| Agent OS docs | workflow architecture, playbooks, durable operating models | current task status unless the doc is specifically a status report |
| Project `AGENTS.md` / `CLAUDE.md` | project-specific rules and deep project context | live proof that the latest code works |
| Koda | durable corrections, lessons, preferences, and non-obvious patterns | raw transcripts, temporary progress, secrets, current branch state |
| Plane | Hafiz-visible mission board: goal, status, owner, blocker, next action, evidence links | code diff, detailed implementation steps, test output archive |
| Microsoft Teams Planner | staff-reported intake and operational symptom context | engineering source of truth, final code status, production truth |
| GitHub issue | developer execution ticket for code work | Hafiz's whole mission view, production smoke result unless linked |
| `.claude/tasks/active.json` | active agent execution pointer for state-file projects | business priority, production truth, cross-session release summary |
| Session Release Ledger | per-session map of fixes, commits, PRs, main state, live state | full project roadmap |
| Git branch/commit | exact code/docs change and local history | whether the change is deployed or accepted by Hafiz |
| PR | reviewable merge candidate and discussion of a code change | proof that the change is live |
| `origin/main` | merged source state | proof that production contains the change |
| deploy record / production SHA | deployed code state | proof the real workflow works |
| QA report / screenshots / tests | evidence that behavior works | task priority or ownership |

## Practical Rule

Before saying work is "done", say the target state:

```text
done locally
committed locally
pushed
PR open
merged to main
deployed
live and smoke passed
accepted by Hafiz
```

Do not use "done" alone when a user could reasonably think it means shipped or
live.

The executable state wording subset lives at:

```bash
scripts/agent-checks/agent-os-state-fixture-runner.py
```

It checks sample state summaries so local, committed, pushed, deployed, and
live-smoke-passed states do not get mixed together. Plain meaning: it catches
answers that say "done" or "live" when the evidence only proves a lower state.

## Normal Work State Flow

For one normal coding task:

```text
Planner or Hafiz report
-> route task
-> Plane mission card
-> GitHub issue when code work is needed
-> active task file when the project uses one
-> branch/implementation
-> verify + QA evidence
-> review
-> commit
-> push / PR / merge when approved
-> deploy when approved
-> live smoke / monitoring evidence
-> Koda lesson if durable
-> save-session close-out
```

Not every task uses every step. Documentation-only Agent OS work usually stays
in docs, git, Koda, and the final close-out unless Hafiz asks for Plane/GitHub.

## What Each State Means

| State Phrase | Meaning |
| --- | --- |
| `not started` | Captured, but no work has begun. |
| `in discussion` | Hafiz and agent are shaping the work; no implementation yet. |
| `in progress` | Agent/dev is actively changing or diagnosing. |
| `blocked` | Cannot move until a named blocker is resolved. |
| `waiting for Hafiz` | Agent has gathered what it can; Hafiz needs to decide, approve, or judge. |
| `waiting for QA` | Built evidence exists, but manual/device/business QA still needs to happen. |
| `done locally` | Files changed locally; not necessarily committed. |
| `committed locally` | Commit exists only in local git. |
| `pushed` | Branch or commit exists on remote, but may not be merged. |
| `PR open` | Pull request exists and awaits review/merge. |
| `merged` | Change is in `origin/main` or the agreed target branch. |
| `deployed` | Target environment contains the commit. |
| `live smoke passed` | The changed workflow was checked on the deployed target. |
| `closed` | Intended outcome is complete, evidence exists, and no next action remains. |

## State Update Rules

Use the smallest update that preserves truth.

| Event | Update |
| --- | --- |
| Staff reports issue | Read Planner as symptom context; do not treat it as verified root cause. |
| Hafiz asks for meaningful work | Route the task and check Plane/active task state where relevant. |
| Code work is needed | Create or link a GitHub issue unless unavailable or too ambiguous. |
| Project has active task files | Read `.claude/tasks/active.json` and resume unless Hafiz starts new work. |
| Work becomes multi-fix | Start or update the Session Release Ledger. |
| Agent finishes a step | Update Plane or close-out with factual progress and next action. |
| Commit created | Record commit SHA in Plane/task/session ledger when relevant. |
| Push/PR/merge/deploy requested | Inventory session fixes before acting. |
| Production deploy done | Record deploy commit, smoke result, monitoring result, and remaining risk. |
| Durable lesson found | Store concise Koda memory with project/domain/lifecycle/risk tags. |

## Conflict Rules

When sources disagree, use this order:

1. Forbidden boundaries: `.env*`, secrets, `live/`, no bypassing hooks.
2. Hafiz's current explicit decision.
3. Fresh verified evidence: git status, tests, browser/API checks, deploy SHA.
4. Approved docs: `AGENTS.md`, project `AGENTS.md`, playbooks, `CLAUDE.md`.
5. Current task systems: active task file, Plane, GitHub, Planner.
6. Koda and previous chat history.
7. Agent assumptions.

If a lower source conflicts with a higher source, say so plainly before acting.

Example:

```text
Planner says the issue is fixed, but the branch is not merged and there is no
live smoke evidence. I will treat it as staff-reported status, not shipped
truth.
```

## Plane, GitHub, Planner

Use them together, not interchangeably.

| Tool | Best Use |
| --- | --- |
| Plane | "Where are we, what is next, who owns it?" |
| GitHub issue | "What exact engineering task should a developer/agent implement?" |
| Planner | "What did staff report or experience operationally?" |

Planner is intake. GitHub is engineering execution. Plane is Hafiz's mission
board.

## Agent Close-Out Shape

Every meaningful close-out should answer:

```text
Status:
<current state phrase>

Meaning:
<what changed in plain language>

Evidence:
<tests/checks/screenshots/links/commit/deploy proof>

Still not true yet:
<not committed / not pushed / not merged / not deployed / not smoke passed / none>

Recommended next:
<single next action>
```

This prevents Hafiz from needing to ask "so what is next?" after every step.
