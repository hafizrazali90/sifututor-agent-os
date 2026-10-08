# Snapshot Playbook

Use this before compaction, context loss, risky switching, or a long pause.

## Goal

A snapshot freezes the working context without pretending the task is complete.

Plain meaning:

```text
Use snapshot when the same work should continue after compaction, interruption,
or a pause. Use handoff when another agent or human should take over.
```

## Steps

1. Record the current goal in one sentence.
2. Record the active project and task state.
3. List the last meaningful decision.
4. List the next command or file to inspect.
5. Mention dirty files and whether they are yours.
6. Save only durable lessons to Koda; keep temporary breadcrumbs in the final
   snapshot text.
7. Name the highest proven state so the resumed agent does not confuse local
   work with pushed, merged, deployed, live checked, or accepted work.
8. Include the return path: the exact next action and the first source to read.

## Context Moves At A Phase Boundary

A phase is a chunk of work that ends when you think "that is done". Decide what
to do with the session's context only at that boundary, never in the middle.
Ask these in order; the first yes wins:

1. **Continue** in the same session if the next phase needs this one as a
   primary source, or there is plenty of room left.
2. **Clear** the context if everything in this session is disposable. It is the
   cheapest move but one-way: the reasons behind past decisions are lost.
3. **Hand off** only when changing tool, folder or repository, or person, or
   when splitting off a side task. It buys portability. See `handoff.md`.
4. **Send to a subagent or an unattended job** (see
   scripts/agent-checks/pc_job.py) if the task is tight enough to run without
   steering. Automated review is the standard case.
5. **Compact** otherwise: the context is relevant, the tool stays the same, and
   you need to stay in the loop. Pass an instruction that says what to keep.
   Compact is the fallback, not the first reach.

Every move except Continue replaces the real session with a summary (or, for
Clear, with nothing), which loses detail.

Adapted from the mattpocock/skills repository (MIT licence).

## Output Shape

```text
SNAPSHOT - <project>

Goal:
- <current goal>

Current position:
- <task/branch/status>

Last decision:
- <decision>

Next move:
- <specific next step>

Dirty state:
- <none or summary>

Highest proven state:
- <drafted | changed locally | committed locally | pushed | PR open | merged | deployed | live checked | accepted/closed>

Read first:
- <Session Map, file, command, PR, issue, or evidence>
```
