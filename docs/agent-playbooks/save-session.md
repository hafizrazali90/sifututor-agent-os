# Save Session Playbook

Use this when wrapping up, handing off, compacting context, or when the user asks
to save the session.

In normal words: saving the session means the next Claude, Codex, or human can
continue without guessing what happened.

Claude may have a `/save-session` command. Codex does not currently have the
same Claude slash-command lifecycle, so Codex must follow this playbook manually
before ending meaningful work.

## The Simple Rule

Do not end a meaningful session with only "done." End it with:

1. what changed
2. what was learned
3. what was saved to Koda
4. what task is still active
5. what remains next

If those five things are clear, the session is saved well.

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
Codex sessions in the Sifututor workspace must manually follow
docs/agent-playbooks/save-session.md because Codex does not run Claude's
/save-session command.
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

Koda: <stored/updated/skipped/failed> <memory ids if available>
Active task: <id + route + next step | none>
Guards: <passed/failed/not run>
Commits/pushes: <summary or none>

Key learnings:
- <lesson>
- <lesson>

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
5. Run the shared guard when code or workflow files changed.
6. Report what changed, why, tests/guards run, files or commits touched, and
   what remains.
7. If Koda is unavailable, say so and use the fallback path.
