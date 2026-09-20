# Active Task Review

Canonical active-task pointers, and how to tell whether one still describes
current work.

Last observed: 2026-09-20 (issue 113). Observed, not reconciled: this page
records what the checker proved, and repairing a product repository's pointer
is a separate change owned by that repository.

## Why This Page Exists

A `.claude/tasks/active.json` file can be perfectly valid JSON and still be
months out of date. Until issue 113 the only automated check was
`python3 -m json.tool`, so a pointer naming a finished task on a merged branch
passed every gate, and a fresh agent reading it resumed obsolete work with full
confidence.

Do not hand-maintain the list below from memory. Refresh it from evidence:

```bash
python3 scripts/agent-checks/agent_os_active_task_freshness.py
python3 scripts/agent-checks/agent_os_active_task_freshness.py --json
```

## What Counts As Authority

Only the **canonical project checkout** owns task state: a registered project
directory directly under the workspace root whose `.git` is a directory.

Never treat these as authority:

- any pointer under `.worktrees/` or `Sifututor-worktrees/`. A linked worktree
  carries a `.git` *file*, and the workspace holds dozens of historical lanes
  with their own frozen pointers
- an open IDE tab, a recent terminal, or the branch a checkout happens to sit on
- a pointer's file mtime in a fresh clone, which is rewritten by the checkout

## Dispositions

| State | Meaning | Severity |
| --- | --- | --- |
| `active` | Claimed task has unfinished steps and the pointer kept pace with the repository. | ok |
| `idle` | `activeTask` is empty. Nothing is claimed, so nothing stale can be resumed. Age is irrelevant. | ok |
| `stale_completed` | Every recorded step is `done` or `skipped`. The pointer describes shipped work. | fail |
| `stale_drifted` | Steps are unfinished, but the repository moved far past the last change to either claim artifact. | fail |
| `dangling` | The named task file does not exist. | fail |
| `invalid` | The pointer is not parseable JSON. | fail |
| `unprovable` | A claim exists but the evidence to judge it does not. Report it; do not reset it. | warn |
| `absent` | A canonical project has no pointer file installed. | warn |
| `no_checkout` | The project is not present in this checkout, e.g. a standalone Agent OS worktree. | info |
| `non_canonical` | The pointer lives in a linked worktree. Never a failure. | info |

Freshness is measured against the project's own Git activity, not the wall
clock. A genuinely paused project cannot drift, and the result is reproducible
on any day.

Two rules were deliberately narrowed so the signal stays trustworthy:

- **A claim is two files.** `active.json` names the task; the task file it
  points at carries the steps. Drift is measured from whichever moved last, so
  a task that runs for months without the pointer changing is not failed for
  it.
- **A merged branch is evidence, not a verdict.** `push`, `deploy`, and
  `smoke` run after the merge, and a trunk branch is always its own ancestor,
  so merge state alone would fail honest work. It is printed on the `merge:`
  evidence line and nothing more. Work that really did ship is caught by
  `stale_completed`; an abandoned claim is caught by drift.

## Current Dispositions (2026-09-20)

| Project | State | Evidence |
| --- | --- | --- |
| `ripple-suite` | `stale_completed` (**open finding**) | Pointer claims `crm-v3-worklist`, whose 10 recorded steps are all `done` through `push` and whose branch `feature/181-crm-v3-worklist` is merged into `origin/main`, while the repository kept moving to 2026-09-20. Diagnosed by the checker; **not** repaired here. Repairing it means editing `ripple-suite/.claude/tasks/active.json`, which this Agent OS change does not own. Follow-up: reset that pointer to idle in the `ripple-suite` repository. |
| `finch-inbox` | `absent` | No `.claude/tasks/` directory in the canonical checkout. Adoption gap, not drift. |
| `kelas` | `idle` | Pointer claims no task. |
| `sifu-tutor` | `idle` | Pointer claims no task. |
| `sifututor_tutor` | `idle` | Pointer claims no task. |
| `sifututor_parent` | `idle` | Pointer claims no task. |
| `lls` | `idle` | Pointer claims no task. |
| `lls-frontend` | `idle` | Pointer claims no task. |
| `lls-mobile` | `idle` | Pointer claims no task. |
| `creative-hub` | `idle` | Pointer claims no task. |
| `cx-call-capture-android` | `idle` | Pointer claims no task. |
| `sims-owner-analytics` | `idle` | Pointer claims no task. |

## Handling A Stale Pointer

1. Say plainly that the pointer is stale and name the evidence the checker
   printed. Do not silently resume it.
2. Reset it to idle only when the disposition is `stale_completed`,
   `stale_drifted`, or `dangling` **and** the evidence is certain:

   ```json
   { "activeTask": null, "taskFile": null, "route": null }
   ```

3. If the state is `unprovable`, report it and stop. Confirm with the task
   owner. Never invent a replacement task to make the check pass.
4. Do not "fix" a historical worktree's pointer. It is a record of what
   happened in that lane.

## All Other Projects

Projects with no resumable claim at the last observation. Every one below is
`idle` except `finch-inbox`, which has no pointer file installed at all.
`ripple-suite` is deliberately absent from this list: it carries the one open
`stale_completed` finding in the table above.

- `kelas`
- `sifu-tutor`
- `sifututor_tutor`
- `sifututor_parent`
- `lls`
- `lls-frontend`
- `lls-mobile`
- `creative-hub`
- `finch-inbox`
- `cx-call-capture-android`
- `sims-owner-analytics`

Run `quick-check.md` commands, then the freshness checker above, to refresh
this list from evidence rather than memory.
