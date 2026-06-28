# Handoff Playbook

Use this when the user asks to hand work to Claude, Codex, or a future human.

## Goal

A handoff should let the next session continue without archaeology. It is
lighter than a full report, but more specific than "done."

Plain meaning:

```text
The next person or agent should know the main goal, the current position, what
is proven, what is not proven, and exactly where to continue.
```

## Steps

1. Identify the project, branch, and active task.
2. Summarize what changed in plain language.
3. List files or areas the next agent should inspect first.
4. State what is safe to continue and what needs approval.
5. Store durable lessons in Koda when they are not already recorded.
6. Point to verification, QA, or blockers.
7. Name the highest proven state: changed locally, committed locally, pushed,
   PR open, merged, deployed, live checked, accepted, or closed.
8. Include the return path: the single next action the receiver should take.

## Continuation Pack

For non-trivial handoff, include:

- main goal and why the work started
- current focus and exact next step
- branch, dirty state, ahead/behind state, and local-only commits
- files, commits, PRs, issues, Session Map, or Mission Ledger references
- checks that passed, checks that failed, and checks not run
- open decisions for Hafiz or a human owner
- approval boundaries: push, PR, merge, deploy, production, critical-lane,
  destructive, secret, or broad access
- do-not-redo context: what the next agent can reuse, and what it should verify
  from current sources before acting

If the work is only local, say so clearly. A local commit is not visible to
GitHub or another machine until it is pushed.

If the receiver is another LLM, add a short continuation prompt:

```text
Continue from <Session Map or file>.
Main goal: <goal>.
Current focus: <focus>.
Next action: <action>.
Check first: <git status / files / docs / evidence>.
Do not change: <boundaries>.
```

## Output Shape

```text
HANDOFF - <project>

Current state:
- <branch/task/status/highest proven state>

What changed:
- <summary>

Next best step:
- <specific action>

Read first:
- <files/docs/session map/PR/issue>

Watchouts:
- <risk or none>

Evidence:
- <tests, guards, or not run>

Continuation prompt:
- <copy-paste prompt when another LLM should resume>
```
