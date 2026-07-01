# Session Release Ledger Playbook

Use this when one chat/session contains more than one bug, fix, PR, or deploy
candidate. Its job is to prevent "fixed in code" from being confused with
"merged to main" or "live in production".

Use [agent-os-state-model.md](agent-os-state-model.md) for the shared status
language across local work, commits, PRs, merges, deploys, and live smoke
evidence.

Use [parallel-work-and-worktrees.md](parallel-work-and-worktrees.md) when more
than one worktree, branch, PR, agent, or long-running task may be active. Plain
meaning: the ledger should say which workspace owns each fix so no local commit
or PR gets stranded.

## Trigger

Start a Session Release Ledger as soon as any of these is true:

- A second staff-reported issue enters the same chat.
- The session switches from one bug to another before the first bug is live.
- More than one branch, PR, or commit is created or discussed.
- Hafiz asks to commit, merge, push, deploy, or check whether everything is live.
- A fix is rebuilt on a cleaner branch after being created on another branch.

For a single tiny documentation change, this is not needed.

## Ledger Template

Keep the ledger in chat, a task note, a PR body, a release evidence file, or a
handoff/save-session note. The location matters less than keeping it current.

```text
Session Release Ledger

1. <plain issue title>
   Issue:
   Branch:
   Worktree:
   Commit:
   PR:
   Tests:
   E2E:
   Main status: not started / local only / pushed / PR open / merged
   Live status: not live / deployed / smoke passed
   Next action:

2. <plain issue title>
   Issue:
   Branch:
   Worktree:
   Commit:
   PR:
   Tests:
   E2E:
   Main status:
   Live status:
   Next action:
```

## Required Status Language

Use precise status words:

- `local only`: commit exists only in a local branch.
- `pushed`: branch exists on GitHub, but no merged PR yet.
- `PR open`: PR exists and is not merged.
- `merged`: commit is an ancestor of `origin/main`.
- `deployed`: production server HEAD includes the commit.
- `smoke passed`: the changed workflow was checked on the deployed target.

Do not call a fix "done" unless the intended target state is also stated. For
example, say "done locally", "merged but not deployed", or "live and smoke
passed".

## Before Switching Bugs

Before starting another bug in the same session, update the current issue line:

```text
Current bug status:
- Code:
- Tests:
- PR/main:
- Live:
- Next action:
```

If the current fix is not merged or not live, state that plainly before moving
on.

## Before Commit, PR, Merge, Push, Or Deploy

Run a stranded-work inventory:

```bash
git status --short --branch
git log --oneline --decorate --all --since='today 00:00' --max-count=80
git branch -a --contains <commit-sha>
git merge-base --is-ancestor <commit-sha> origin/main; echo $?
```

For every ledger commit, answer:

```text
In origin/main: yes/no
In current branch: yes/no
PR exists: yes/no
Production contains it: yes/no/not checked
```

If any ledger item is local-only or PR-open, do not imply it will be included in
the deploy. Either include it intentionally or mark it as excluded.

## Release Summary Shape

Before a production deploy, report:

```text
These fixes are in main:
- <issue> <commit/PR>

These fixes are only in PR:
- <issue> <PR>

These fixes are local only:
- <issue> <branch/commit>

These fixes are already live:
- <issue> <production SHA/evidence>

These fixes are not live:
- <issue> <reason and next action>
```

This summary is mandatory when multiple fixes happened in one chat.
