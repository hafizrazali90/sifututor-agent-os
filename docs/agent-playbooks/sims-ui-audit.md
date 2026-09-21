# SIMS UI Audit Playbook

Use this when reviewing or verifying `sifu-tutor` browser UI, SIMS page
redesigns, screenshot evidence, visual QA, design-system consistency, changed
modals/dropdowns/tables/forms, or Hafiz asks whether a page "looks right".

Plain meaning: this is the first-class route for the mistakes Hafiz kept
catching manually: spacing, density, table fit, disabled-button contrast,
modal padding, transparent dropdowns, inconsistent filters, old-theme leakage,
copy casing, and screenshots that were generated but not judged.

This playbook is a wrapper around the existing SIMS UI/UX docs and
`ux-reviewer`. It is **not** a second design system.

## Source Of Truth

For `sifu-tutor`, read these in order:

1. `sifu-tutor/docs/ui-ux/README.md`
2. `sifu-tutor/docs/ui-ux/quality-gate.md`
3. `sifu-tutor/docs/ui-ux/review-and-qa-checklist.md`
4. Relevant surface docs linked from the README:
   `design-system.md`, `page-patterns.md`, `component-patterns.md`,
   `content-style-guide.md`, `accessibility-and-states.md`, and the relevant
   feature docs under `sifu-tutor/docs/features/<feature>/`.
5. `sifu-tutor/.claude/agents/ux-reviewer.md` when Claude/subagents are
   available. In Codex, perform the same checklist yourself.

Also read
`sifu-tutor/docs/ui-ux/sims-ui-audit-skill-recommendation.md` when changing the
audit workflow itself.

## When It Triggers

Run this audit when:

- the diff touches `sifu-tutor/resources/js/Pages/**` or
  `sifu-tutor/resources/js/Components/**` and changes visual/UI behavior;
- a task mentions SIMS UI/UX, visual QA, screenshot review, design-system
  consistency, table/filter/modal/sidebar/page layout, responsive layout, or
  "looks weird";
- a redesigned page, modal, dropdown, drawer, filter, table, form, or action
  surface is about to be shown to Hafiz;
- QA/review/verify is being run for a `sifu-tutor` browser-visible change.

Do not run the full audit for docs-only changes, backend-only changes, or
one-line copy edits that do not change layout or state behavior. Still apply
content-style rules when copy changes.

## Audit Steps

1. Identify the touched routes, components, states, and breakpoints.
2. Read the relevant UI/UX docs from the source-of-truth list.
3. Build or run the local app when needed.
4. Capture or inspect the changed surface at representative desktop and mobile
   widths when feasible. Include modals, dropdowns, drawers, empty/loading/error
   states, disabled states, pagination, filters, action menus, and the ordinary
   common case when changed.
5. Judge the screenshots, not only the code. Check alignment, density, copy
   casing, whitespace, button/control sizing, table fit, contrast, theme
   consistency, old-style leakage, and whether each action is understandable.
6. Add or update permanent E2E regression coverage for user-facing UI behavior,
   or record the exact named blocker.
7. Report findings before summary. If the audit finds UI problems inside scope,
   fix them before asking Hafiz to review.

## Checklist

Use this as the minimum checklist:

- **Theme consistency:** no old SIMS theme leakage, raw one-off patterns, or
  mixed component styles on a revamped surface.
- **Spacing and density:** page sections, modal content, filters, tables, cards,
  sidebars, and actions have intentional spacing; no large unexplained dead
  zones or cramped controls.
- **Controls:** inputs, selects, date fields, buttons, icon buttons, pagination,
  and action menus use consistent height, padding, text size, border, focus,
  hover, active, loading, and disabled treatment.
- **Disabled contrast:** disabled buttons and controls remain readable; no white
  text on pale disabled surfaces or invisible disabled icons.
- **Tables:** table columns fit the real data where reasonable; use horizontal
  scroll only when fitting would make the data unreadable. Header, row, cell,
  badge, action, and pagination styling must match the table system used by the
  current revamped module.
- **Modals and popouts:** overlays are not transparent unless intentionally
  designed that way; content has proper padding; footer actions align; title,
  helper copy, and body hierarchy are clear.
- **Copy:** labels, statuses, buttons, placeholders, helper text, and errors
  follow the content style guide. Display backend values in user-facing casing.
- **Truth and meaning:** displayed totals match their visible parts; numbers and
  comparative claims have an upstream source; copy does not promise a channel
  the system does not use; meaningful colours and icons keep one clear meaning;
  and every visible interaction has a destination or effect.
- **Responsive behavior:** desktop and mobile layouts avoid overlap, clipped
  text, hidden actions, and accidental horizontal overflow.
- **Evidence:** screenshots or browser evidence include the changed interactive
  states, not only the default page. Review a fixed current capture, identify
  the scenario/state it represents, and recapture after material changes rather
  than mixing findings from an older artifact with the current design.

## Output Shape

```text
SIMS UI AUDIT - PASS | FAIL | PARTIAL

Scope:
- routes/components/states audited

Evidence:
- screenshots/browser checks/tests run

Findings:
- severity, route/component, practical issue, and fix needed

Design docs checked:
- paths

Permanent E2E:
- file path or named blocker

Ready for Hafiz review:
- yes/no and why
```

If no findings are found, still name the remaining risk, such as untested mobile
width, unavailable fixture data, or a state that cannot be safely reproduced.
