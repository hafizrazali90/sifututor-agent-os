# Save Session Playbook

Use this when wrapping up, handing off, compacting context, or when the user asks
to save the session.

Codex note: Claude may have a `/save-session` command. Codex does not currently
have the same Claude slash-command lifecycle, so Codex must follow this playbook
manually before ending meaningful work.

## Goal

Make knowledge portable between Claude and Codex. The session is not really
saved until non-obvious lessons and corrections are in Koda or explicitly
reported as not saved.

## When To Run

Run this at the end of every non-trivial session, especially when:

- work was committed or pushed
- workflow or project rules changed
- the user corrected the agent
- a bug root cause or fix pattern was discovered
- a task is being handed from Claude to Codex or Codex to Claude
- context is about to compact or the agent is about to stop

Skip only for trivial read-only answers where no durable knowledge changed.

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

## Codex End-Of-Session Checklist

Before Codex gives the final "done" answer for meaningful work:

1. Search Koda for duplicate memories when a durable lesson exists.
2. Store or update Koda memories for corrections, decisions, and non-obvious
   lessons.
3. Read `.claude/tasks/active.json` when present and report the active task
   state.
4. Run the shared guard when code or workflow files changed:

```bash
../scripts/agent-checks/pre-commit-guard.sh
```

5. Report what changed, why, tests/guards run, files or commits touched, and
   what remains.
6. If Koda is unavailable, say that explicitly and write the durable lesson into
   a repo doc or handoff note instead.
