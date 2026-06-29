# Switching Between Claude And Codex

Use this when handing the same task from Claude to Codex, Codex to Claude, or a
fresh agent session. The goal is one shared state, not two separate agent
memories.

Use [multi-agent-adapter-workflow.md](multi-agent-adapter-workflow.md) before
switching when the real question is which worker should own the next workflow
stage. Switching is a state-transfer action, not a way to let each agent invent
a different process.

## Before Switching

1. Save the current task state:
   - Read `.claude/tasks/active.json`.
   - Read the referenced task file if one exists.
   - Update the current step evidence before stopping.
2. Save durable knowledge:
   - Store user corrections immediately with `source: "correction"`.
   - Store non-obvious implementation lessons before handoff.
   - Use valid Koda categories: `decision`, `lesson`, `rule`, `preference`,
     or `fact`.
3. Verify guardrails:

```bash
../scripts/agent-checks/pre-commit-guard.sh
```

From the umbrella root:

```bash
scripts/agent-checks/pre-commit-guard.sh
```

4. Write a handoff note using one of the templates in
   `docs/agent-playbooks/templates/`.

## Claude To Codex

Claude must not rely on hidden session context. Before asking Codex to continue:

- Put active task progress in `.claude/tasks/<task-id>.json`.
- Put durable lessons in Koda.
- Mention exact files changed and exact commands already run.
- Include the next unblocked step.
- Tell Codex which project `AGENTS.md` to read first.

Codex should then:

1. Read nearest `AGENTS.md`.
2. Read project `CLAUDE.md` for technical context.
3. Search Koda memory for the task.
4. Read `.claude/tasks/active.json`.
5. Continue from the first incomplete step.

## Codex To Claude

Codex must not rely on chat-only summaries. Before asking Claude to continue:

- Update active task evidence.
- Store Koda lessons/corrections.
- Run the shared pre-commit guard.
- Provide a concise status report with files changed and tests run.

Claude should then:

1. Read `AGENTS.md` for shared rules.
2. Read `CLAUDE.md` for deep context.
3. Read `.claude/tasks/active.json`.
4. Resume from the task file, not from memory alone.

## Fresh Agent Resume

For any fresh agent:

1. Read `AGENTS.md`.
2. Read `docs/agent-playbooks/parity-status.md`.
3. Read the project `CLAUDE.md`.
4. Read `.claude/tasks/active.json`.
5. Search Koda memory.
6. Run the shared guard before committing or claiming gate readiness.

## Do Not Switch When

- A critical-lane task is mid-edit and the diagnosis is not written down.
- Tests are failing and the failing command/output is not captured.
- The active task state is stale or points to a missing task file.
- The next agent would need unstated IDE or terminal context to continue.
