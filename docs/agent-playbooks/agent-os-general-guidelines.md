# Agent OS General Guidelines

Use this for baseline engineering behavior that should apply across workflows.

Plain meaning:

```text
These are the everyday quality habits that sit underneath routing, build,
review, commit, QA, and save-session.
```

These guidelines are adapted from Kun Chen's L8 agentic workflow notes, but
they are Sifututor-specific.
Do not copy external rules blindly when they conflict with Hafiz's approval
boundaries, project ownership, or anti-scope-creep rules.

## Writing And Docs

- Avoid em dashes in Agent OS docs and day-to-day responses.
  Use a plain dash when punctuation is needed.
- For long Markdown docs, prefer one full sentence per physical line when
  practical.
  Preserve normal Markdown structure.
  Do not churn old docs only to reflow text.
- Do not manually edit generated files unless the source-of-truth playbook says
  that generated artifact is intentionally human-maintained.
  Prefer editing the source file and regenerating the output.
- For generated HTML Session Map views, edit the Markdown source and regenerate
  the HTML.

## Commits And Release Notes

- Do not add an agent name as a commit co-author unless Hafiz explicitly asks.
- Use the project's required commit format and direct `git commit -m` flags.
- Changelog and release-note files are not all the same.
  Some projects treat them as human-maintained communication; others generate
  them.
  Check the project rule before editing.
- If a staff-facing change needs release communication, update the human-owned
  release communication file or note why it is not needed.
  Do not hand-edit generated release output.

## Engineering Decisions

When choosing an implementation path, prefer:

- quality
- simplicity
- robustness
- scalability
- maintainability

Development speed and cost matter, but they should not justify brittle code,
hidden state, unclear ownership, weak evidence, or future workflow confusion.

Plain version:

```text
Do not take the cheap shortcut if it makes the next bug, agent, staff workflow,
or release harder to trust.
```

## Bug Fixes And User Proof

For bug fixes, start as close to the real user journey as feasible.

This does not mean full E2E must run before every diagnosis.
It means the agent should understand and prove the actual visible behavior, not
only the internal code path.

Use the existing evidence model:

- reproduce or inspect the reported symptom when safe
- identify the real user, role, page, action, API, or state transition
- add focused code proof where useful
- add browser/mobile/API journey proof when user-facing
- add or update permanent E2E coverage when feasible
- name the exception and follow-up when E2E is not feasible

## UI And Visible Quality

When a task touches UI, be picky about what the user sees:

- layout
- text clarity
- empty/loading/error states
- awkward overlap or spacing
- accessibility basics
- visual consistency with the project's design system

Do not silently turn a narrow bugfix into a redesign.
If a visible issue is clearly related and cheap/safe to fix, include it.
If it is unrelated, report it and route it as a follow-up instead of hiding it
or silently expanding scope.

## Lint, Tests, And Flaky Checks

Treat lint failures, test failures, and flaky checks as real signals.

If the issue is caused by the current change, fix it before moving outward.
If it is pre-existing or unrelated, report it plainly, separate it from the
current task, and route it to the right follow-up home.

Do not call work ready by ignoring failures.
Do not silently fix broad unrelated failures unless Hafiz approved that scope or
the failure blocks the current task and the fix is clearly safe.

## Scope Rule

High quality does not mean unlimited scope.

Use this default:

```text
Fix in-scope issues.
Report related issues.
Track unrelated issues.
Ask before widening the work.
```

