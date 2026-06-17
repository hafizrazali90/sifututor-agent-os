# Agent OS Mission Ledger

This folder is the place for work we must not forget.

It is not a replacement for GitHub, Plane, Planner, Koda, or active task files.
It connects them.

Plain version:

```text
Mission Ledger = the map of bigger goals, child tasks, adjacent ideas, and
paused decisions.
```

## Why This Exists

Some important work appears in the middle of another session:

- "remember to improve this UI later"
- "this is part of a bigger reconciliation redesign"
- "staff can do this manually for now, but the system should guide them later"
- "this bug revealed a process gap"

Those items are too important to leave only in chat or memory, but too early to
turn into a full engineering ticket. This ledger keeps them visible.

## Sources Of Truth

| Need | Use |
| --- | --- |
| Current active implementation step | `.claude/tasks/active.json` where present |
| Engineering ticket ready to build | GitHub issue |
| Hafiz-visible mission board | Plane |
| Staff-reported symptom | Microsoft Planner |
| Durable lesson or correction | Koda |
| Bigger goal, child task, adjacent idea, paused follow-up | Mission Ledger |

## How To Use

1. Capture unclear or new items in `_inbox.md`.
2. Move triaged items into the relevant project file.
3. Put tasks under a parent mission whenever possible.
4. Use clear status words: `captured`, `triaged`, `active`, `promoted`,
   `paused`, `done`, `dropped`.
5. When an item becomes build-ready, promote it to GitHub or Plane and link it.
6. During `$save-session`, check this folder before closing the session.

## Fast Lookup

Do not read every ledger file during normal work.

Search first:

```bash
rg -n "<project keyword|invoice|receipt|matching|mobile|parent>" docs/agent-playbooks/mission-ledger
```

Then open only the matching project file and section. Read all files only when
doing ledger cleanup or an Agent OS audit.

## Guard Check

Before commit, the shared guard validates this folder:

```bash
scripts/agent-checks/pre-commit-guard.sh
```

For ledger-only checks:

```bash
python3 scripts/agent-checks/mission-ledger-check.py
```

## Item Template

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
- **Promote to:** <GitHub issue | Plane card | PRD | QA plan | Koda | none yet>
- **Links:** <GitHub/Plane/PR/docs/evidence or none>
```

## Current Project Files

- [_inbox.md](_inbox.md)
- [cross-project.md](cross-project.md)
- [ripple-suite.md](ripple-suite.md)
- [sifu-tutor.md](sifu-tutor.md)
- [sifututor_tutor.md](sifututor_tutor.md)
- [sifututor_parent.md](sifututor_parent.md)
- [lls.md](lls.md)
- [lls-frontend.md](lls-frontend.md)
- [lls-mobile.md](lls-mobile.md)
