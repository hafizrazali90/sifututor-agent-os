# Snapshot Playbook

Use this before compaction, context loss, risky switching, or a long pause.

## Goal

A snapshot freezes the working context without pretending the task is complete.

## Steps

1. Record the current goal in one sentence.
2. Record the active project and task state.
3. List the last meaningful decision.
4. List the next command or file to inspect.
5. Mention dirty files and whether they are yours.
6. Save only durable lessons to Koda; keep temporary breadcrumbs in the final
   snapshot text.

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
```
