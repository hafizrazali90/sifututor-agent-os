# Mission Ledger Playbook

Use this when a task, adjacent idea, follow-up, or discussion point must not be
lost, but is not ready to become a GitHub issue, PRD, QA plan, Koda memory, or
active task yet.

Plain version:

```text
Koda remembers lessons.
GitHub tracks engineering tickets.
The Mission Ledger remembers what we should come back to and why.
```

## What It Is

The Mission Ledger is the Agent OS parking lot for work that needs context:

- bigger goals and end states
- child tasks under those goals
- adjacent ideas discovered during a session
- paused questions waiting for Hafiz or staff
- follow-ups that should later become GitHub issues, PRDs, QA plans, or Koda

It lives at:

```text
docs/agent-playbooks/mission-ledger/
```

## When To Use It

Add or update a ledger item when:

- Hafiz says "remember this later"
- a session discovers an adjacent system improvement
- the agent says "later we should..."
- a task is too early for GitHub but too important for memory only
- a task belongs to a bigger goal and that relationship matters
- save-session would otherwise leave a dangling follow-up

Do not use it for:

- exact code work that is already ready for a GitHub issue
- active release state in the current chat; use the Session Release Ledger
- durable behavior lessons; use Koda
- staff-reported support intake; use Planner as intake context

## Low-Token Usage Rule

Do not load the whole Mission Ledger by default.

For normal task routing, use this order:

1. Search for likely keywords with `rg`.
2. Open only the matching project file.
3. Read only the matching mission/task section.
4. Open `_inbox.md` only when checking for untriaged follow-ups.
5. Read every ledger file only when doing ledger maintenance or a full Agent OS
   audit.

Example:

```bash
rg -n "receipt|preview|reconciliation|matching" docs/agent-playbooks/mission-ledger
```

Then read the relevant section only, such as `RS-RECEIPT-001` in
`ripple-suite.md`.

Plain meaning: the ledger should make context easier to find, not consume a lot
of tokens at the start of every session.

## Automation

The shared pre-commit guard runs:

```bash
python3 scripts/agent-checks/mission-ledger-check.py
```

The checker validates:

- allowed statuses and types
- required fields on every ledger item
- duplicate item IDs
- parent links that point to real ledger items
- non-mission items have a parent
- promoted items have a link or promotion target

Plain meaning: agents can still make judgment calls about priority, but they
cannot commit a malformed ledger item unnoticed.

## Relationship Model

Every non-trivial item should point to a parent mission.

```text
Mission
-> child task
-> adjacent idea
-> promoted GitHub issue / PRD / QA plan / Koda memory when ready
```

Use IDs that show the relationship:

```text
RS-RECON-001        # Ripple reconciliation reliability mission
RS-RECON-001.1      # child task
RS-RECON-001.A1     # adjacent idea
```

## Statuses

| Status | Meaning |
| --- | --- |
| `captured` | Written down, not triaged yet. |
| `triaged` | Understood; next action is clear. |
| `active` | Currently being worked through GitHub, PRD/QA docs, or active task state. |
| `promoted` | Moved to GitHub, PRD, QA plan, Koda, or another source of truth. |
| `paused` | Waiting for Hafiz, staff, evidence, or a dependency. |
| `done` | Completed and linked to evidence. |
| `dropped` | Intentionally not doing. |

## Types

| Type | Use For |
| --- | --- |
| `mission` | A bigger goal with a clear end state. |
| `task` | A concrete piece of work under a mission. |
| `adjacent` | A useful nearby idea discovered while doing something else. |
| `question` | A decision or clarification to revisit. |
| `risk` | A known risk or failure mode to design around later. |
| `research` | A topic that needs investigation before implementation. |

## Required Fields

Use this compact block for each item:

```md
### <ID> — <short title>

- **Project:** <project or cross-project>
- **Status:** <captured | triaged | active | promoted | paused | done | dropped>
- **Type:** <mission | task | adjacent | question | risk | research>
- **Parent:** <mission ID or none>
- **End goal:** <what good looks like>
- **Why it matters:** <plain-language reason>
- **Source:** <chat/session/date/staff issue/PR>
- **Next action:** <one concrete next step>
- **Promote to:** <GitHub issue | PRD | QA plan | Koda | none yet>
- **Links:** <GitHub/PR/docs/evidence or none>
```

## Save-Session Rule

Before ending meaningful work, check whether any "later", "remember", "adjacent
task", "follow-up", or "we should improve" item belongs in the Mission Ledger.

If yes, update the relevant file and mention it in the save-session report:

```text
Mission Ledger: updated RS-RECON-001.A2 in ripple-suite.md
```

If no, say:

```text
Mission Ledger: no new follow-up captured
```

## Task-Router Rule

At task start, if the prompt sounds like it belongs to a bigger goal, check the
relevant project ledger before creating a new isolated plan.

This prevents:

- treating a child task as a random one-off
- forgetting a previously paused design decision
- creating duplicate GitHub issues
- missing the real end state behind a small UI or data fix

## Promotion Rules

Move an item out of the ledger when it becomes execution-ready:

| Ready For | Promote To |
| --- | --- |
| exact code/docs work | GitHub issue |
| large new workflow or redesign | PRD / UX spec |
| behavior lesson or future guardrail | Koda |
| test coverage plan | QA/test docs |

Keep the ledger item, but mark it `promoted` and link the new source of truth.

## File Routing

| Scope | File |
| --- | --- |
| Unsure / quick capture | `_inbox.md` |
| Cross-project or Agent OS | `cross-project.md` |
| Ripple Suite | `ripple-suite.md` |
| SIMS / Laravel | `sifu-tutor.md` |
| Tutor mobile app | `sifututor_tutor.md` |
| Parent mobile app | `sifututor_parent.md` |
| Learnest backend | `lls.md` |
| Learnest frontend | `lls-frontend.md` |
| Learnest mobile | `lls-mobile.md` |
| Other internal apps | create a project file when needed |
