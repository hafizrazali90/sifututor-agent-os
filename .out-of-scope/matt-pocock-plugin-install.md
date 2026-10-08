# Installing the mattpocock/skills plugin

## What was proposed

Install the whole `mattpocock/skills` plugin (or run its `npx skills` installer)
to get his skills.

## Why it is out of scope

- It brings about 27 skills, and the names of several collide with ours:
  `grill-me`, `tdd`, `triage`, `handoff`, and a `code-review` that clashes with
  the built-in Claude Code command.
- The plugin is a read-only bundle pinned to a commit that can lag by days or
  weeks.
- His versions assume his process (batched interviews, committing to the current
  branch, no approval gates). Several break our rules.
- Our own gap register decided 34 ideas one by one. Only the chosen ideas are
  copied, as text, into our files.

## What would change our mind

A skill we need that we cannot reasonably copy as text, or a decision to follow
his process as a whole instead of ours.

## Decided

08/10/2026 (MYT), Hafiz: copy chosen text only; do not install the plugin.
