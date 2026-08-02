# Codex To Claude Handoff

Use this as the human-readable brief referenced by a local copy of
`claude-delegation-job.json`. Keep the filled job file and worker state under
the worktree's ignored `.agent-os/delegations/` directory; do not commit runtime
state or raw conversations.

## Project

`<project-name>`

## Active Task

- Task id:
- Route:
- Current step:
- Task file:

## Delegation Contract

- Job id:
- Goal in one sentence:
- Approved stop point:
- Worktree and branch:
- Lane owner:
- Progress cadence:
- Forbidden actions:
- Required proof:
- Required MCP servers, or none:

## What Codex Changed

- Files changed:
- Why:
- Scope intentionally avoided:

## Evidence

- Commands run:
- Results:
- Guard status:
- Koda memories stored:

## Risks Or Open Questions

- Product/UX:
- Technical:
- Test gaps:

## Next Step For Claude

Resume from:

```text
<next step>
```

Read first:

- `AGENTS.md`
- `CLAUDE.md`
- `.claude/tasks/active.json`
- `<task file>`

## Required Return Contract

Write one handback file at the exact path named in the job JSON. It must contain:

- final worker state: finished, failed, waiting, or incomplete
- plain-English summary of what changed
- exact changed-file inventory
- commands/checks run and their results
- failures, unavailable measurements, and unverified claims
- current branch, commit, dirty state, and highest proven product state
- whether the approved stop point was reached
- any decision or intervention still needed
- the single next action for independent Codex review

Do not include secrets, raw credentials, `.env*` values, or raw production data.
Do not claim acceptance from Claude's own review. Codex independently checks the
diff, evidence, scope, and next-state safety before Hafiz approves a later gate.
