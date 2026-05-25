# Save Session Playbook

Use this when wrapping up, handing off, compacting context, or when the user asks
to save the session.

## Goal

Make knowledge portable between Claude and Codex. The session is not really
saved until non-obvious lessons and corrections are in Koda or explicitly
reported as not saved.

## Koda Schema

Use only these values:

```text
category: decision | lesson | rule | preference | fact
source: user-stated | auto-captured | correction
```

Every memory needs at least one project tag:

```text
sifu-tutor | ripple-suite | sifututor_tutor | sifututor_parent |
lls | lls-frontend | lls-mobile | creative-hub | team-inbox
```

Never store secrets, raw tokens, credentials, payload bodies, or ephemeral state
such as the current branch.

## What To Capture

Capture:

- user corrections
- root cause and fix pattern for bugs
- project-specific gotchas that will matter next time
- API contract decisions
- financial, auth, migration, or mobile compatibility lessons
- test strategy that proved a hard-to-test behavior

Do not capture:

- vague summaries like "made progress"
- command output with no durable lesson
- temporary branch names or transient file paths
- secrets or production data

## Dedup First

Before storing a new memory:

1. Search Koda for the topic.
2. If a similar memory exists, update or confirm it instead of duplicating.
3. If no similar memory exists, store a concise actionable memory.

## Project State

State-file projects:

1. Read `.claude/tasks/active.json`.
2. If the task is complete, archive only when every required step is `done` or
   `skipped`.
3. If incomplete, report the next unblocked step.

`lls`:

1. Use `.claude/tasks/active.json` like the other active projects.
2. Mention paired `lls-frontend` work when API contracts changed.
3. Treat old Superpowers specs as reference only unless the user explicitly
   asks to preserve them as planning artifacts.

## Report

```text
SESSION SAVED - <project>

Koda memories stored/updated: <count or "not available">
Active task/state: <id + next step | none>
Local memory index: <updated | unchanged | not present>

Key learnings:
- <lesson>
- <lesson>

Next:
- <next step or "none">
```
