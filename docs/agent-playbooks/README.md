# Shared Agent Playbooks

Model-agnostic procedures for Claude, Codex, Kilo, and future agents. The root
`AGENTS.md` is the shared entry point; the router and the owner index tell an
agent which playbook to open for the current task. Nobody reads this directory
top to bottom.

## Start Here

1. `../AGENTS.md`: the shared contract. Codex loads it natively; Claude loads
   it through the `@AGENTS.md` import in `../CLAUDE.md`.
2. [task-router.md](task-router.md): choose the route, intensity, finish
   state, and isolation need.
3. [doc-routing-and-context-loading.md](doc-routing-and-context-loading.md):
   which documents each route requires or triggers, and how each model loads
   its entry point.
4. [doc-owner-route-index.md](doc-owner-route-index.md): who owns which rule,
   the complete active inventory, and the historical list.

Command aliases per agent (`/verify`, `$verify`, Kilo skills) are owned by
[agent-os-skill-registry.md](agent-os-skill-registry.md) and checked by
`scripts/agent-checks/agent-os-parity-fixture-runner.py`. Hook layers are
owned by [agent-os-hook-dispatcher.md](agent-os-hook-dispatcher.md). Reporting
style and the close-out shape are owned by
[agent-os-communication.md](agent-os-communication.md).

## Project Families

| Family | Projects | Workflow state |
| --- | --- | --- |
| State-file workflow | `ripple-suite`, `sifu-tutor`, `sifututor_tutor`, `sifututor_parent`, `lls` | `.claude/tasks/active.json` points to the active task file |
| Paired frontend | `lls-frontend` | Has state workflow and dedicated frontend skills; verify with `lls` when API contracts or RTK Query slices change |
| Shared-playbook workflow | `lls-mobile`, `creative-hub` | Has task state and hooks, but no project-specific skills yet |
| Existing custom workflow plus task pointer | `finch-inbox` | Keeps Finch workflow, adds `.claude/tasks/active.json` for parity |
| Shared baseline plus strict project authority | `cx-call-capture-android`, `sims-owner-analytics` | Shared task state and hooks are installed; each project keeps its stricter product/safety authority (`AI-RULES.md` or project `AGENTS.md`) |

`team-inbox` is retired and replaced by `finch-inbox`. Do not add it back to
this table or use it as a Koda project tag.

## Where Rules Live

- One owner per rule. Adapters, skills, and this README point at the owner;
  they do not restate it.
- Before adding, splitting, or removing a playbook use
  [skill-quality-and-pruning.md](skill-quality-and-pruning.md) and update the
  owner index in the same change.
- `scripts/agent-checks/agent-os-doc-navigation-check.py` (run by health) fails
  on broken links, playbooks missing from the owner index, an adapter that
  stops importing `AGENTS.md`, oversized entry files, or routes that lose their
  safety wiring.
- Historical material lives under [archive/](archive/) or is listed as
  historical in the owner index; it never overrides an active playbook.
- The remaining `lls` workflow migration is tracked in
  [lls-workflow-migration.md](lls-workflow-migration.md).
