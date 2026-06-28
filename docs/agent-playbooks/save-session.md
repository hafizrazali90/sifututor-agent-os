# Save Session Playbook

Use this when wrapping up, handing off, compacting context, or when the user asks
to save the session.

In normal words: saving the session means the next Claude, Codex, or human can
continue without guessing what happened.

Use [agent-os-state-model.md](agent-os-state-model.md) to report the exact
state of the work, such as done locally, committed locally, pushed, PR open,
merged, deployed, live smoke passed, or waiting for Hafiz.

Claude may use `/save-session`. Codex should use the repo-local `$save-session`
skill when available. Both entry points must follow this playbook before ending
meaningful work.

## The Simple Rule

Do not end a meaningful session with only "done." End it with:

1. what changed
2. what was learned
3. what was saved to Koda
4. what the current status and next action are
5. what task is still active
6. what remains next
7. whether the Session Map is current or closed, if the session needed one
8. what was captured in the Mission Ledger, if anything
9. whether the session can be closed now or should continue with QA, commit,
   review, deploy preparation, or another named next step

If those things are clear, the session is saved well.

## Continuation Pack Standard

A save-session is not a transcript. It is a restart pack.

Plain meaning:

```text
The next Claude, Codex, or human should be able to continue in a few minutes,
not reconstruct the whole story from chat.
```

For meaningful sessions, the save report must include these facts:

1. Main goal: why the session started.
2. Current focus: what the agent was doing when the session stopped.
3. Highest proven state: drafted, changed locally, committed locally, pushed,
   PR open, merged, deployed, live checked, accepted, or closed.
4. Git state: branch, dirty/staged state, ahead/behind state, and important
   local-only commits.
5. What changed: files, commits, PRs, issues, docs, or Session Map links.
6. Evidence: checks, tests, QA, screenshots, smoke checks, monitoring, or what
   could not be checked.
7. Open decisions: what Hafiz must decide versus what the agent can continue.
8. Boundaries: stop-before-push, stop-before-deploy, critical-lane,
   destructive, production, secret, or approval limits.
9. Return path: the single recommended next action.
10. Do-not-redo context: what the next agent should trust from this session
    and what it should still verify from current evidence.

If the session has multiple fixes, branches, PRs, or deploy candidates, include
or update the Session Release Ledger before saving. Do not let "fixed in code"
sound like "merged", "deployed", or "live checked".

If local commits are not pushed, say that plainly:

```text
Committed locally, not pushed to GitHub yet.
```

That sentence matters because another machine, another agent, or GitHub will
not see the work until it is pushed.

If the session used a Session Map, close or update it using
[session-map.md](session-map.md) before the final save report. In normal words:
the map should say whether the work should continue, is parked, was handed off,
is closed, or did not need a map.

For normal step-by-step close-outs inside a session, use the lighter wording
from [agent-os-communication.md](agent-os-communication.md):

```text
Done. <what changed and how it was checked.>

Current state: <Continue | Save Only | Park | Hand Off | Close>.
Still waiting: <what is not true yet>.
Recommended next: <one concrete next action>.
Decision needed: <yes/no and what decision>.
```

Use the fuller save-session report below when the user asks to save, hand off,
compact, end, or when the session is complex enough that the next agent would
otherwise need to reconstruct the story.

## Ending State

Before the final save report, choose the honest ending state.

| Ending state | Use when | Required before using it |
| --- | --- | --- |
| Continue | The same thread should keep going. | Current focus, next action, and waiting decision are clear. |
| Save Only | The work is not finished, but context must be preserved before stopping. | Session Map, Reference Pack, Git state, Koda saves, and next action are current. |
| Park | Work is intentionally paused. | Reason for pause, what is waiting, resume condition, and where it is recorded are clear. |
| Hand Off | Another agent or human should continue. | Owner, continuation prompt, boundaries, files/commits/links, and evidence are listed. |
| Close | Nothing required remains. | Checks are done, durable saves are done, Git/push/PR/deploy state is clear, no waiting decision remains, and next action is none or optional. |

Plain meaning:

```text
Do not call a session closed just because the chat is ending. Close only when
nothing required remains.
```

If commits are local-only, checks are missing, Koda was not saved, Hafiz still
needs to decide, or the next action is unclear, the session is not closed. Use
Continue, Save Only, Park, or Hand Off instead.

## Choose A Save Level

Pick the smallest level that honestly fits the session.

| Level | Use When | Required Work |
| --- | --- | --- |
| Quick Save | Read-only discussion, small doc note, no code changed | Final summary only; Koda optional |
| Normal Save | Code/docs/workflow changed, commits/pushes happened, or task state matters | Koda check, status check, active task check, final save report |
| Critical Save | Auth, payment, invoice, commission, migration, deployment, financial, or mobile API contract work | Normal Save plus explicit risks, tests, human-review status, and blockers |

If unsure, use Normal Save.

## Exact Commands

From the umbrella root:

```bash
git status --short --branch
scripts/agent-checks/pre-commit-guard.sh
```

From a product project:

```bash
git status --short --branch
../scripts/agent-checks/pre-commit-guard.sh
```

For all product projects from the umbrella root:

```bash
for d in sifu-tutor ripple-suite sifututor_tutor sifututor_parent lls lls-frontend lls-mobile creative-hub team-inbox finch-inbox; do
  echo "## $d"
  (cd "$d" && ../scripts/agent-checks/pre-commit-guard.sh)
done
```

Use the all-project sweep after workspace-wide parity or workflow changes. For a
single project task, the project-level guard is enough.

## Koda Schema

Use only these values:

```text
category: decision | lesson | rule | preference | fact
source: user-stated | auto-captured | correction
```

Every memory needs at least one project tag:

```text
sifu-tutor | ripple-suite | sifututor_tutor | sifututor_parent |
lls | lls-frontend | lls-mobile | creative-hub | team-inbox | finch-inbox |
sifututor | codex-parity
```

Never store secrets, raw tokens, credentials, payload bodies, customer private
messages, `.env` values, or production data.

## What To Save In Koda

Save:

- user corrections
- root cause and fix pattern for bugs
- project-specific gotchas that will matter next time
- API contract decisions
- financial, auth, migration, deployment, or mobile compatibility lessons
- test strategy that proved a hard-to-test behavior
- workflow decisions that future agents must obey

Do not save:

- vague summaries like "made progress"
- raw command output with no durable lesson
- temporary branch names unless the branch itself is the decision
- secrets or production data
- every file touched if the repo already records that in git

## Good And Bad Koda Examples

Bad:

```text
Fixed the payment bug.
```

Good:

```text
In sifu-tutor, InvoiceStatus only supports UnPaid and Paid. Declined FIUU
callbacks must keep invoices as UnPaid instead of introducing a Failed status.
```

Bad:

```text
Updated docs.
```

Good:

```text
Codex sessions in the Sifututor workspace should use the repo-local
$save-session skill, which follows docs/agent-playbooks/save-session.md as the
same source of truth as Claude's /save-session habit.
```

## Dedup First

Before storing a new memory:

1. Search Koda for the topic.
2. If a similar memory exists, update or confirm it instead of duplicating.
3. If no similar memory exists, store a concise actionable memory.

This keeps Koda useful instead of noisy.

## Active Task State

If `.claude/tasks/active.json` exists:

1. Read it.
2. Read the referenced task file when one is active.
3. Report the active task ID, route, and next step.
4. Do not mark a task complete unless every required step is `done` or
   explicitly `skipped` with evidence.
5. If the task is incomplete, report the next unblocked step.

For `lls`, use `.claude/tasks/active.json` like the other active projects.
Mention paired `lls-frontend` work when API contracts changed. Treat old
Superpowers specs as reference only unless Hafiz explicitly asks to preserve
them as planning artifacts.

## Mission And Status Tracking

Do not update Plane by default. For non-trivial work, report the current status,
evidence, and next action in the save-session close-out. Use GitHub for
execution-ready engineering work, active task files for routed project work, and
Mission Ledger for bigger goals, paused decisions, adjacent ideas, or important
follow-ups that are not ready for GitHub.

## If Koda Fails

Do not pretend the session is fully saved.

Say clearly:

```text
Koda save failed: <short reason>
Fallback saved in: <file path or handoff note>
```

Fallback options:

- update the relevant repo doc
- write a handoff note under `docs/agent-playbooks/templates/` format
- include the durable lesson in the final response

When Koda works again, store the durable lesson there.

## Snapshot Versus Handoff

Use these differently:

| Situation | Use | Practical meaning |
| --- | --- | --- |
| Same agent continues after compaction or a long pause | Snapshot | Freeze the current working context without ending the work. |
| Another agent, another session, or a human should continue | Handoff | Package the work so the next owner starts from the right place. |
| The session is ending or Hafiz asks to save | Save-session | Save state, durable lessons, evidence, and next action. |

Do not use Koda as a raw transcript store. Koda gets durable corrections,
preferences, rules, and non-obvious lessons. Session Map gets the current story.
Save-session gets the restart pack.

## Critical Save Extra Checks

For critical work, explicitly answer:

- Did this touch auth, payment, invoice, commission, migration, deployment, or
  mobile API contract behavior?
- Was human review required?
- Was human review completed or still pending?
- What tests or manual checks prove it?
- What would be risky to do next?

If human review is required but not complete, say that plainly in the final
report.

## Final Report Template

Use this exact shape for Normal or Critical Save:

```text
SESSION SAVED - <project or workspace>

Main goal: <why the session existed>
Current focus: <what was being worked on when saved>
Highest proven state: <drafted | changed locally | committed locally | pushed | PR open | merged | deployed | live checked | accepted/closed>
Koda: <stored/updated/skipped/failed> <memory ids if available>
Active task: <id + route + next step | none>
Session Map: <updated/current/not needed>
Mission Ledger: <updated item | no new follow-up | skipped>
Guards: <passed/failed/not run>
Commits/pushes: <summary or none>
Git state: <branch, dirty/staged state, ahead/behind, local-only commits if any>
Ending state: <Continue | Save Only | Park | Hand Off | Close>

Key learnings:
- <lesson>
- <lesson>

Continuation pack:
- What changed: <files/commits/PRs/issues/docs>
- Evidence: <checks and gaps>
- Boundaries: <what needs approval before continuing>
- Return path: <single recommended next action>

Remaining work:
- <next step>
- <next step>

Notes:
- <risk, blocker, or "none">
```

For Quick Save, a shorter version is fine:

```text
SESSION SAVED - <project>
Koda: skipped, no durable lesson
Session Map: <updated/current/not needed>
Mission Ledger: <updated item | no new follow-up | skipped>
Ending state: <Continue | Save Only | Park | Hand Off | Close>
Next: <next step or none>
```

## Codex End-Of-Session Checklist

Before Codex gives the final answer for meaningful work:

1. Choose Quick, Normal, or Critical Save.
2. Search Koda for duplicate memories when a durable lesson exists.
3. Store or update Koda memories for corrections, decisions, and non-obvious
   lessons.
4. Read `.claude/tasks/active.json` when present and report the active task
   state.
5. Check the Mission Ledger for new follow-ups, adjacent tasks, paused
   decisions, or bigger-goal links. Update it when needed. See
   [mission-ledger.md](mission-ledger.md). Search/open only the relevant project
   file unless doing a full ledger cleanup.
6. If the session had side paths, multiple sub-goals, or a confusing return
   path, update or reference the Session Map using [session-map.md](session-map.md).
7. Run the shared guard when code or workflow files changed.
8. Choose the honest ending state: Continue, Save Only, Park, Hand Off, or
   Close. Do not use Close if real work or decisions remain.
9. Report what changed, why, tests/guards run, files or commits touched, and
   what remains.
10. If Koda is unavailable, say so and use the fallback path.
