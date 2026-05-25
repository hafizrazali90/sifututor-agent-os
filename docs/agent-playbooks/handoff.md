# Handoff Playbook

Use this when the user asks to hand work to Claude, Codex, or a future human.

## Goal

A handoff should let the next session continue without archaeology. It is
lighter than a full report, but more specific than "done."

## Steps

1. Identify the project, branch, and active task.
2. Summarize what changed in plain language.
3. List files or areas the next agent should inspect first.
4. State what is safe to continue and what needs approval.
5. Store durable lessons in Koda when they are not already recorded.
6. Point to verification, QA, or blockers.

## Output Shape

```text
HANDOFF - <project>

Current state:
- <branch/task/status>

What changed:
- <summary>

Next best step:
- <specific action>

Watchouts:
- <risk or none>

Evidence:
- <tests, guards, or not run>
```
