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
