# Parallel Work And Worktrees

Use this when more than one agent, session, branch, PR, fix, or long-running
task may be active at the same time.

Plain meaning:

```text
If two tasks may touch code at the same time, give them separate counters.
Do not let agents cook different dishes in the same workspace and then guess
which ingredient belongs to which dish.
```

This is inspired by Kun Chen's treehouse pattern, but Sifututor starts with a
lightweight local rule: use normal Git branches and worktrees intentionally,
record their state, and clean them up when the work is merged or parked.

## Why This Exists

Parallel work creates expensive confusion:

- one agent edits files while another assumes the repo is clean
- one branch contains unrelated fixes
- a local commit is mistaken for pushed work
- a PR is mistaken for merged work
- a merged change is mistaken for deployed or live work
- Hafiz asks "what next?" and the agent cannot name the active task
- a future session resumes stale context from the wrong branch or worktree

The goal is not to create more ceremony. The goal is to make concurrent work
safe enough that Hafiz does not need to micromanage branch state.

## When To Use Same Workspace

Same workspace is fine when:

- discussion only
- tiny docs edit
- one focused normal task
- no other agent/session is editing the same repo
- no existing dirty files conflict with the task
- the agent can explain the current branch and Git state clearly

Even then, check `git status --short --branch` before staging, committing,
pushing, PR, merge, deploy, save-session, or handoff.

## When To Use A Separate Worktree

Use or recommend a separate worktree when:

- another agent or session is working in parallel
- the task is long-running or risky
- the task may need its own PR
- the current repo is dirty with unrelated changes
- a production hotfix must stay clean
- a branch already contains unrelated work
- a PR cleanup should not disturb the main workspace
- profile/readiness verification should use clean `origin/main`
- the current session contains multiple fixes with different target states

Hard rule:

```text
Two active code tasks that may edit the same repo should not share one dirty
workspace.
```

## Recommended Workspace Choice

| Situation | Workspace recommendation |
| --- | --- |
| Tiny discussion or docs note | Same workspace. |
| One focused normal task | Same workspace or normal branch. |
| Multiple fixes in one chat | Same workspace only with Session Release Ledger; separate worktree if branches diverge. |
| Another agent works in parallel | Separate worktree required. |
| Long-running feature | Separate worktree required. |
| Risky product fix | Separate branch/worktree recommended. |
| Production hotfix | Clean dedicated branch/worktree required. |
| PR cleanup after another branch exists | Separate worktree preferred. |
| Clean profile/readiness audit | Temporary clean worktree from `origin/main` preferred. |

## Naming Standard

Use names that make the work obvious:

```text
.worktrees/<project>-<short-purpose>
```

Examples:

```text
.worktrees/sifu-invoice-adjustments-docs
.worktrees/ripple-remove-vercel
.worktrees/sifu-tutor-hotfix-mobile-filter-api
```

Branches should still follow the project branch naming rules. The worktree name
helps humans and agents scan local folders; the branch name is the Git truth.

## Required State Record

Whenever a separate worktree is created, used, handed off, or closed, record:

```text
Project:
Repo/worktree:
Branch:
Base branch:
Purpose:
Owner/session:
Issue:
PR:
Commit(s):
Highest proven state:
Next action:
Cleanup condition:
```

Save this in the Session Map, Session Release Ledger, handoff, PR body, or
save-session report depending on the work.

## Before Switching Work

Before moving from one task/worktree to another, say:

```text
Current worktree:
Branch:
Dirty files:
Local-only commits:
Pushed/PR/merged/deployed state:
Next action:
```

If anything is local-only, say it plainly. Do not let a local commit disappear
from the story.

## Before Push, PR, Merge, Deploy, Or Save

Run a stranded-work check:

```bash
git status --short --branch
git worktree list
git log --oneline --decorate --all --max-count=40
```

For every active task, answer:

```text
Which worktree owns it?
Which branch owns it?
Is it dirty?
Is it committed locally?
Is it pushed?
Is there a PR?
Is it merged?
Is it deployed or live checked?
What is the next action?
```

Use [session-release-ledger.md](session-release-ledger.md) when more than one
fix, branch, commit, PR, or deploy candidate is in play.

## Cleanup Rule

Do not delete a worktree just because the local task feels finished.

Cleanup is safe only when:

- the work is merged or intentionally abandoned
- no useful uncommitted files remain
- no local-only commits need preservation
- Hafiz or the task boundary does not need the worktree retained
- the final state is recorded in Session Map, save-session, PR, or handoff

If unsure, park it instead of deleting it:

```text
Parked worktree:
Reason:
Resume condition:
Cleanup condition:
```

## Relationship To Existing Playbooks

| Existing playbook | How this connects |
| --- | --- |
| `task-router.md` | Decide whether the task can use the current workspace or needs isolation. |
| `session-map.md` | Track long-running or parallel session state. |
| `session-release-ledger.md` | Track multiple fixes, branches, commits, PRs, and deploy states. |
| `push-pr-ci-automation.md` | Confirm the exact branch/worktree before pushing or opening a PR. |
| `save-session.md` | Preserve worktree/branch/local-only commit state before ending. |
| `no-mistakes-lite.md` | Final honesty pass before claiming ready/done/outbound state. |

## Future Automation

Do not install a treehouse-style manager yet.

First, use this playbook in real work. If repeated confusion remains, add a
small local script that prints active worktrees, branches, dirty state,
ahead/behind state, PR links when available, and suggested cleanup candidates.

Possible later script:

```text
scripts/agent-checks/worktree-inventory.sh
```

Plain version:

```text
Use simple Git worktrees now.
Automate the inventory only after the manual rule proves useful.
```
