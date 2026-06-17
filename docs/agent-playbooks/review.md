# Review Playbook

Use this for code review, pre-commit review, or adversarial quality checks.

## Review Stance

Lead with findings. Prioritize correctness, regressions, security, missing
tests, workflow violations, and user-facing behavior. Keep summaries secondary.

Use [agent-os-evidence-model.md](agent-os-evidence-model.md) when judging
whether the agent gathered enough proof before handing work to Hafiz or staff.

## Natural-Language PR Review With Hafiz

When Hafiz asks to review a PR, the default review surface is the same chat, not
the GitHub code diff. The agent still reads the PR metadata, issue, changed
files, diff, tests, CI, and release state internally, then translates the result
into natural language for Hafiz to review.

The chat review must explain:

- what the PR changes in product or workflow terms
- what staff, parents, tutors, students, or admins will see differently
- the before/after behavior
- the important business rules and risk areas
- the evidence checked, including tests, E2E, build, CI, or manual smoke
- gaps, unknowns, or decisions that still need Hafiz's judgment
- the recommended decision: approve, request changes, QA first, hold, or merge-ready

If there are blocking findings, start with those in plain language before the
summary. Code-level file references should appear as proof for a finding or in a
technical appendix, but Hafiz should not need to read the diff unless he asks or
the decision depends on product judgment only he can make.

Approval in chat can count as Hafiz's PR review decision. Merge, deploy, and
production state changes still require explicit current-session approval.

## Steps

1. Identify the intended scope.
2. Inspect `git diff` or the requested files.
3. Check project rules in `AGENTS.md` and relevant `CLAUDE.md`.
4. Look for broken contracts, missing tests, unsafe paths, and unverified
   critical behavior.
5. For `sifu-tutor` browser UI/UX changes, read
   `sifu-tutor/docs/ui-ux/README.md` and check the diff against the SIMS
   surface-map, design-system, page-pattern, component-pattern, content-style,
   accessibility/state, review-checklist, and quality-gate docs. Treat missing
   state coverage, invented one-off UI patterns, token drift, unclear
   critical-action copy, or missing browser/screenshot evidence as review
   findings.
6. Treat "human should check this" as a finding unless Playwright, API, CLI, or
   server-side evidence is genuinely unavailable or unsafe. The review should
   push the agent to gather its own non-destructive evidence first.
7. For user-facing feature, bugfix, hotfix, or small-change work, treat a
   missing permanent E2E regression decision as a review finding. If the change
   affects browser/mobile behavior and no E2E was added or updated, require a
   specific blocker and follow-up fixture/test.
   For any staff/admin/parent/tutor/student/customer workflow, treat missing
   permanent E2E coverage as a blocking review finding unless the workflow is
   explicitly not safely automatable.
8. For staff-facing feature, bugfix, hotfix, or small-change work, treat
   missing release communication as a review finding when relevant. Check for a
   `CHANGELOG.md` entry, affected module help updates, and a What's New release
   entry or seed script. If any item is intentionally not needed, the PR or
   final answer must say why.
9. For multi-fix sessions, treat a missing or stale Session Release Ledger as a
   review finding. Before push, merge, PR, or deploy, verify every session fix
   is classified as local-only, pushed, PR-open, merged, deployed, or excluded.
10. Report findings by severity with file and line references where possible.

## PR Chat Output Shape

Use this shape when Hafiz is reviewing a PR in chat. Keep it natural; the labels
are prompts for meaning, not rigid ceremony.

```text
PR review:

Recommendation:
- <approve | request changes | QA first | hold | merge-ready>

What changes for users:
- <plain-language behavior change>

Before vs after:
- <old behavior>
- <new behavior>

Risk areas:
- <business rule, permission, payment, invoice, mobile contract, or data risk>

Evidence checked:
- <tests, E2E, build, CI, smoke, or not checked with reason>

What Hafiz needs to decide:
- <decision or none>

Technical appendix:
- <only when useful: key files, functions, or line references>
```

## Output Shape

```text
REVIEW - PASS | FAIL | PARTIAL

Findings:
- <severity> <file:line> <issue>

Open questions:
- <question or none>

Test gaps:
- <gap or none>

Permanent E2E:
- <added/updated file path | missing finding | not feasible with reason>
Changed workflow E2E map:
- <workflow>: <permanent E2E file | missing finding | explicit exception>

Release communication:
- <CHANGELOG/help/What's New current | missing finding | not relevant with reason>

Session release ledger:
- <not applicable | current | missing finding>

Summary:
- <brief context>
```
