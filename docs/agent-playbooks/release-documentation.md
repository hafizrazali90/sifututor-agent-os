# Staff Documentation Release Playbook

This playbook owns one rule for the whole Agent OS:

```text
A staff-facing change ships with the staff documentation it needs, in the same
release bundle, or it records why it did not.
```

Plain meaning:

```text
If a staff member has to do something differently after this release, the thing
that tells them so must ship with it. Not next week. Not "we'll write it up
later". The same bundle.
```

`commit.md`, `review.md`, `release-deploy-live-monitoring.md`, and
`no-mistakes-lite.md` used to each carry their own half-version of this rule.
They now point here. When this rule changes, it changes in this file only.

Use [test-coverage.md](test-coverage.md) alongside this playbook. That one asks
"is the behavior proved?". This one asks "does the person who uses it know?".

## Why This Exists

The rule was already written down. It was still skipped, and it was skipped
most often on the release where it mattered most: the urgent one, shipped under
pressure, where "I'll document it tomorrow" is said sincerely and then never
happens because the next fire starts.

So the deferral is allowed - but it has to name a person and a follow-up issue.
A deferral nobody owns is not a deferral. It is a quiet decision to never do it.

## The Three Decisions

Every staff-facing change records exactly one of these. Not zero, not two.

| Decision | Means | Must carry |
| --- | --- | --- |
| `relevant` | Staff need to be told or shown something. | The documentation files, in this same change. |
| `not relevant` | Nothing staff see or do changes. | A concrete reason a reviewer could disagree with. |
| `urgent deferral` | It is relevant, but it cannot wait for the docs. | A named person, a real GitHub follow-up issue, and the reason. |

What a decision is not:

```text
"TBD" is not a decision.
"See the PR" is not a decision.
"Probably fine" is not a decision.
```

### When it is `relevant`

Ask the practical question, not the process question:

```text
After this ships, will a staff member do something differently, see something
new, or be confused by something that moved?
```

If yes, it is relevant. Typical artifacts, depending on the project:

- the changelog entry, in plain English, for what actually changed
- the in-page help or module guidance staff read while doing the task
- the What's New / release entry that tells staff the change landed
- the staff guide for a workflow that now has different steps

Name the files you actually changed. Do not name a file you did not touch and
do not name a documentation file that already existed from an earlier release -
the checker treats both as a change that did not document itself.

### When it is `not relevant`

Give the reason in one sentence, in terms of the staff member:

```text
Good:  Database index only; nothing staff see or do changes.
Good:  Internal API rename; the staff screens and steps are identical.
Bad:   n/a
Bad:   not needed
Bad:   internal
```

"Internal" alone is not a reason, it is a category. Say what stays the same.

### When it is `urgent deferral`

This is the escape hatch, and it is deliberately narrow.

Required:

- **Owner**: a named person. `Hafiz Razali` or `@hafizrazali90`. Not "the team",
  not "TBD", and never the agent - Claude and Codex cannot own a commitment
  that outlives the session.
- **Follow-up**: a real GitHub issue. `#431`, `Sifututor/sifu-tutor#431`, or the
  full issue URL. Not "later", not "TODO", and not this change's own issue -
  a follow-up that points at the work you just finished tracks nothing.
- **Reason**: why the documentation could not ship with the release.

The checker validates the *shape* of the issue reference. It does not open
GitHub. Whether the issue exists, is open, and says the right thing is still
the reviewer's job.

## Where The Decision Lives

Each project keeps a decision ledger. By default it is `RELEASE-DOCS.md` at the
project root, and it is a Markdown table:

```markdown
| Change | Decision | Artifacts | Owner | Follow-up | Reason |
| --- | --- | --- | --- | --- | --- |
| #418 invoice status filter | relevant | `CHANGELOG.md`, `src/modules/finance/lib/help.ts` | Hafiz Razali | - | Staff pick the filter themselves |
| #421 invoice query index | not relevant | - | - | - | Database index only; nothing staff see or do changes |
| #430 payout rounding hotfix | urgent deferral | - | Hafiz Razali | #431 | Shipped mid payout window; the guide follows this week |
```

Copy [templates/release-docs-ledger.md](templates/release-docs-ledger.md) to
start one.

The ledger is a record, not a worksheet. Add your row; do not edit or delete
somebody else's. Deleting a past decision is reported as a finding.

## Projects Do Not Share Paths

`sifu-tutor` is Laravel with staff guides kept as documents. `ripple-suite` is
Next.js with per-module `help.ts`. A rule that hardcoded one of those would be
wrong in the other repository on the day it was written.

So the engine resolves each project's shape in this order:

1. `.agent-os/release-docs.json` in the project, when it exists. This is
   authoritative - copy
   [templates/release-docs.example.json](templates/release-docs.example.json).
2. Otherwise a convention detected from what the repository actually contains:
   a Next.js repo with `src/modules/*/lib/help.ts`, a Laravel repo with
   `artisan`, or any repo that keeps a `CHANGELOG.md`. The Laravel convention
   accepts SIMS's dated `docs/changelogs/release-notes-*.md` files; the Next.js
   convention recognises Ripple's `scripts/seed-releases-*.ts` What's New entries.
3. Otherwise **unavailable** - reported honestly, never reported as passed.

Two things the engine deliberately will not do:

- It will not treat a repository as gated just because it *has* staff
  documentation facilities. A build script, a dependency bump, or a test-only
  change stays shippable. Only paths the project calls staff-facing trigger a
  decision.
- It will not invent a required artifact, an audience, or a report source the
  change did not establish. A project's own configuration says which artifacts
  are always required; everything else is checked only when the decision names
  it.

## Running It

```text
scripts/agent-checks/release_documentation.py
```

One file, for every agent. Claude, Codex, Kilo, and anything that comes next run
the same script and get the same answer. There is no Claude-only and
Codex-only version of "does this release need a staff guide?".

Two modes, same rules:

| Mode | Exit code | Use it when |
| --- | --- | --- |
| `advisory` | always `0` | Before commit. This is what the shared guard runs. |
| `blocking` | `1` on findings | Before push, PR, merge, or deploy. |

```bash
# What this commit is answerable for, from inside the project
python3 ../scripts/agent-checks/release_documentation.py --project . --mode advisory --staged

# What this release is answerable for
python3 ../scripts/agent-checks/release_documentation.py --project . --mode blocking --base main
```

From the umbrella root, pass the project path instead:

```bash
python3 scripts/agent-checks/release_documentation.py --project sifu-tutor --mode blocking --base main
```

It is read-only. It writes nothing, opens no network connection, and reads no
credentials.

### It only asks about the change in front of it

The engine evaluates a decision only when this change added or edited it.
A decision recorded for a release six months ago is settled and is never
re-opened. A project that adopts the ledger today does not have to
retro-document its history before it may ship a fix.

This check also never asks for tests. Test coverage is
[test-coverage.md](test-coverage.md)'s job, and mixing the two is how a small
fix turns into an unrelated audit.

### When it cannot answer

`UNAVAILABLE` means the engine could not resolve the project's shape or could
not read the previous ledger revision to scope the change. That is reported, not
converted into a pass. In `blocking` mode an unresolvable project is a finding,
because a release that cannot be proved is not a release that passed.

## What It Proves, And What It Does Not

It proves:

- exactly one decision was recorded for this change
- a `relevant` decision named documentation that exists and shipped in this same
  bundle, including every artifact the project always requires
- an `urgent deferral` named a real person, a real follow-up issue that is not
  this change's own issue, and a reason
- a `not relevant` decision gave a reason

It does not prove:

- that the guide is well written, complete, or aimed at the right audience
- that the follow-up issue is open or will be done
- that the change is genuinely staff-facing when the project's path patterns
  disagree with reality

Those stay with the reviewer. The engine removes the cheap failures so the
review can spend its attention on the real ones.

## Worked Examples

Copy these. They are the three shapes an agent will meet.

### Relevant

A staff member picks an invoice status filter, refreshes, and the filter used to
reset. Now it stays.

```markdown
| #418 invoice status filter | relevant | `CHANGELOG.md`, `src/modules/finance/lib/help.ts` | Hafiz Razali | - | Staff pick the filter themselves and need to know it now persists |
```

In the same commit: the code fix, the changelog line, the module help line.

Close-out sentence:

```text
Staff documentation: relevant. The changelog entry and the finance module help
text ship in this commit.
```

### Not relevant

An index was added so the invoice list query stops timing out. The screen, the
steps, and the wording are identical.

```markdown
| #421 invoice query index | not relevant | - | - | - | Database index only; the invoice screen, steps and wording are unchanged |
```

Close-out sentence:

```text
Staff documentation: not relevant. Only the query plan changed; nothing staff
see or do is different.
```

### Urgent deferral

A payout rounding bug is losing money mid payout window. The fix ships now; the
guide for the changed reconciliation step does not exist yet.

```markdown
| #430 payout rounding hotfix | urgent deferral | - | Hafiz Razali | #431 | Shipped mid payout window to stop incorrect payouts; the reconciliation guide follows this week |
```

Close-out sentence:

```text
Staff documentation: urgently deferred. Hafiz owns it and issue #431 tracks the
reconciliation guide. This is a debt, not a decision that it was unnecessary.
```

What would have failed:

```markdown
| #430 payout rounding hotfix | urgent deferral | - | TBD | later | - |
```

Nobody is named, nothing tracks it, and no reason is given. The checker says so
in those words.

## Adopting It In A Project

1. Copy [templates/release-docs-ledger.md](templates/release-docs-ledger.md) to
   the project root as `RELEASE-DOCS.md`.
2. Run the advisory check on a real change and read what it says about the
   project's detected shape.
3. If the detected convention is wrong for that repository, copy
   [templates/release-docs.example.json](templates/release-docs.example.json) to
   `.agent-os/release-docs.json` and correct `staff_facing` and `artifacts`.
4. Leave the shared guard on `advisory` while the project is learning the habit.
   Move the release path to `blocking` once the ledger is real.

## Close-Out Line

Every commit, review, and release close-out on a staff-facing change says one
line, in plain language:

```text
Staff documentation: <relevant, and the files that shipped | not relevant, and
why | urgently deferred, who owns it and which issue tracks it>
```

If the change is not staff-facing, say nothing. Silence is correct there, and
adding a line for it is ceremony.
