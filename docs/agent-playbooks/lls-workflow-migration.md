# LLS Workflow Migration Playbook

Use this when migrating `lls` from its current Superpowers-only setup into the
standard Sifututor workflow.

## Goal

Bring `lls` to parity with `ripple-suite`, `sifu-tutor`, `sifututor_tutor`, and
`sifututor_parent`:

- `.claude/tasks/active.json`
- `.claude/tasks/<task-id>.json`
- `.claude/tasks/archive/`
- route-based task state
- verify/qa/review/commit gate evidence
- Koda save-session rules using valid memory schema

## Migration Steps

1. Audit current LLS workflow files:
   - `lls/CLAUDE.md`
   - `lls/AGENTS.md`
   - `lls/.claude/skills/lls-*.md` or `lls/.claude/skills/*/SKILL.md`
   - `lls/docs/superpowers/WORKFLOW.md`
2. Create `.claude/tasks/SCHEMA.md`, `.claude/tasks/active.json`, and
   `.claude/tasks/archive/`. Done for the foundation pass.
3. Rewrite `lls-task-router` to create standard task files for:
   - `feature`
   - `bugfix`
   - `hotfix`
   - `small-change`
   - `refactor`
   - `docs`
4. Rewrite `lls-verify`, `lls-qa`, `lls-commit`, and `lls-save-session` to read
   and update the active task state.
5. Add or verify hooks equivalent to the other active projects:
   - branch validation
   - conventional commit
   - workflow gate
   - quality gate
   - memory flush/session start where supported
6. Update `lls/AGENTS.md` to full format with LLS technical rules and the
   standard workflow references.
7. Treat Superpowers files as reference only unless the user explicitly keeps
   them as an additional planning layer.

## Acceptance

LLS migration is done when:

- `lls/.claude/tasks/active.json` exists and starts empty
- `/task-router lls` creates standard task state
- `/verify lls`, `/qa lls`, `/commit lls`, and `/save-session lls` all read the
  same task state model
- committing is blocked until required route steps are complete
- root and LLS `AGENTS.md` no longer describe Superpowers as the target workflow
