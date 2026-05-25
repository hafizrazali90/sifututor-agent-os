# Task Router Playbook

Use this when starting a non-trivial task or when the user asks to route,
classify, resume, or create work.

## Start

1. Identify the active project from cwd and user prompt.
2. Read the project `AGENTS.md`; if absent, read project `CLAUDE.md`.
3. Search Koda memory for the task topic when available.
4. Check workflow state before editing.

## State-File Projects

Applies to `ripple-suite`, `sifu-tutor`, `sifututor_tutor`, and
`sifututor_parent`.

1. Read `.claude/tasks/active.json`.
2. If `activeTask` is set, read the referenced `taskFile`.
3. Resume the active task unless the user explicitly starts a new task.
4. Report the current route and next unblocked step before editing.

Common route shapes:

| Route | Use for | Core path |
| --- | --- | --- |
| `feature` | New user-facing behavior | plan -> build -> generate_tests -> qa_full -> verify -> review -> commit |
| `bugfix` | Non-emergency defect | describe -> fix -> regression_test -> defect_analysis -> verify -> qa -> review -> commit |
| `hotfix` | Production or staging breakage | describe -> fix -> regression_test -> verify -> qa -> review -> commit |
| `small-change` | Copy, label, config, minor UI | describe -> fix -> verify -> qa -> commit |
| `refactor` | Structure change without behavior change | analyze -> plan -> refactor -> verify -> qa -> review -> commit |
| `docs` | Documentation only | write -> verify -> commit |

If there is no active task file, do not invent one unless the user asks to start
a routed task. For simple tasks, state that no active task exists and proceed
under `AGENTS.md`.

## LLS Migration Note

`lls` previously used Superpowers docs instead of the standard Sifututor
`.claude/tasks/active.json` workflow. That was workflow drift, not the desired
long-term architecture. The state-file foundation now exists; continue aligning
LLS skills and hooks with the shared route/state model.

For LLS tasks:

1. Read `lls/CLAUDE.md` for current technical rules.
2. Read `lls/.claude/tasks/active.json`.
3. Route work using the same route names as the other active projects.
4. Do not teach future agents that Superpowers-only is the target state.

Target migration:

- continue improving `lls-task-router` route file creation
- update `lls-verify`, `lls-qa`, `lls-commit`, and `lls-save-session` to read
  and update active task state consistently
- keep relevant Superpowers specs only as planning/reference input

## Critical Lanes

For auth, payments, invoices, commissions, migrations, mobile API contracts, or
deployment work:

1. Phase A: read-only diagnosis and recommendation.
2. Wait for explicit approval.
3. Phase B: implementation.

Do not collapse these phases unless the user explicitly authorizes emergency
hotfix risk.
