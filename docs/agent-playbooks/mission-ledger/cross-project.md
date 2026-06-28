# Cross-Project Mission Ledger

Use this for Agent OS, shared workflow, infrastructure, or product-system tasks
that span more than one project.

## Missions

### AO-LEDGER-001 — Make follow-up work visible across sessions

- **Project:** cross-project
- **Status:** active
- **Type:** mission
- **Parent:** none
- **End goal:** Agents can see bigger goals, child tasks, adjacent ideas, and
  paused decisions without relying only on chat or memory.
- **Why it matters:** Hafiz should not lose important follow-up tasks when a
  Codex or Claude session closes.
- **Source:** Hafiz request, 2026-06-12
- **Next action:** Use this ledger during the next `$save-session` and refine
  the workflow if anything feels awkward.
- **Promote to:** GitHub issue or Plane card if this becomes an implementation
  project beyond docs.
- **Links:** [mission-ledger playbook](../../agent-playbooks/mission-ledger.md)

### AO-LEDGER-001.1 — Wire Mission Ledger into Agent OS playbooks

- **Project:** cross-project
- **Status:** triaged
- **Type:** task
- **Parent:** AO-LEDGER-001
- **End goal:** `$task-router` and `$save-session` both check the Mission
  Ledger at the right time.
- **Why it matters:** A ledger only works if agents remember to use it.
- **Source:** Hafiz request, 2026-06-12
- **Next action:** Keep the playbook references current as the workflow evolves.
- **Promote to:** none yet
- **Links:** [task-router](../../agent-playbooks/task-router.md),
  [save-session](../../agent-playbooks/save-session.md)

### AO-LEDGER-001.2 — Add Session Map for live conversation tracking

- **Project:** cross-project
- **Status:** active
- **Type:** task
- **Parent:** AO-LEDGER-001
- **End goal:** Agents can maintain a lightweight live map of the current
  session so Hafiz can see the main goal, current focus, side paths, decisions,
  and return path without rereading the chat.
- **Why it matters:** Long Agent OS and development sessions often start with
  one goal, branch into side problems, then need to return to the original
  problem. Without a live map, both Hafiz and the agent can lose the story.
- **Source:** Hafiz request, 2026-06-28
- **Current state:** Session Map playbook, template, validator, HTML dashboard,
  auto-open habit, lifecycle trigger, close-state model, and dashboard v2
  structure exist locally for review.
- **Next action:** Use the Session Map in this Agent OS build session and
  review the dashboard v2 first-screen scan, Progress Flow, Decision Board,
  Side Paths, Evidence / Checks, Reference Pack, and Continuation Prompt.
- **Promote to:** Keep as Agent OS playbook/template; promote dashboard changes
  into reusable tooling when the design stabilizes.
- **Links:** [session map playbook](../../agent-playbooks/session-map.md),
  [session map template](../../agent-playbooks/templates/session-map.md)
