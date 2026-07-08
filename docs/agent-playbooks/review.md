# Review Playbook

Use this for code review, pre-commit review, or adversarial quality checks.

## Review Stance

Lead with findings. Prioritize correctness, regressions, security, missing
tests, workflow violations, and user-facing behavior. Keep summaries secondary.

Use [agent-os-evidence-model.md](agent-os-evidence-model.md) when judging
whether the agent gathered enough proof before handing work to Hafiz or staff.
Use its Proof Standard to separate code proof, journey proof, and release proof
before allowing the next state to be described as ready.

Use [no-mistakes-lite.md](no-mistakes-lite.md) as the final honesty gate before
the review allows a commit, push, PR, merge, deploy, or ready/done claim.

Use [related-impact-audit.md](related-impact-audit.md) for bugfix, hotfix, and
user-facing small-change review. Plain meaning: review should check whether the
agent looked for obvious same-pattern bugs, adjacent regression risk, and scope
expansion before saving or sending work outward.

Use [agent-os-general-guidelines.md](agent-os-general-guidelines.md) for
baseline quality habits: do not hide generated-file edits, do not ignore
lint/test/flaky-check failures, be picky about touched UI, and keep quality
high without silently widening scope.

## Fresh-Context Review

Use fresh-context review when the next state matters enough that the builder's
own confidence is not sufficient.

Plain meaning:

```text
Review the work like you did not build it.
Do not trust the implementation story until the diff, state, and evidence
support it.
```

Fresh-context review is a stronger mode inside this playbook, not a separate
skill by default.

Use it before:

- push, PR, merge, deploy, release close-out, or live/done claims
- critical-lane work
- user-facing feature, bugfix, hotfix, or small-change work
- long autonomous work packets
- multi-fix sessions
- complex Agent OS changes that affect future agent behavior

Skip the full version for tiny docs-only, typo, or copy edits unless the edit
changes approval, safety, memory, evidence, routing, or deployment behavior.

Fresh-context review should ask:

1. What would I check first if I did not trust the builder's explanation?
2. Does the diff match the intended scope?
3. Does the evidence prove the acceptance rule, or only a weaker behavior?
4. Could a real user journey still fail?
5. Is the state honest: local, committed, pushed, PR open, merged, deployed,
   live checked, monitored, accepted, or closed?
6. Did the builder miss related impact, release communication, permanent E2E,
   Session Release Ledger, or approval boundary?
7. What should happen next, and what should not happen yet?

If another agent, Claude, a subagent, or a human reviewer is available and the
risk justifies it, the main agent may ask for bounded fresh review. The main
agent still owns synthesis, final checks, and close-out unless Hafiz assigns
ownership elsewhere.

## Review And Risk Checkpoint

Review is the agent's second-brain check before work is saved or sent outward.

Plain version:

```text
Verify asks: does it work?
QA asks: can a real user complete the journey?
Review asks: is it scoped, evidenced, safe, and honest about its state?
```

Run this checkpoint before commit, push, PR, merge, deploy, or whenever Hafiz
asks whether work is safe to approve.

| Risk Area | What To Check | Blocks Next State When |
| --- | --- | --- |
| Scope creep | Did the agent change files, behavior, copy, dependencies, or cleanup outside the approved task? | Unapproved adjacent work is included or the review cannot explain why each changed file belongs. |
| Evidence gap | Does the evidence match the work type and state being claimed? | Required tests, browser/mobile proof, permanent E2E decision, or live smoke are missing without a valid named exception. |
| Related impact | Did the fix include the right local related check, same-pattern sweep, or critical impact audit? | The same root-cause pattern or adjacent regression risk is obvious but uninspected, or related findings were silently fixed outside scope. |
| State confusion | Is the work only changed locally, committed, pushed, PR-open, merged, deployed, live checked, or accepted? | The report implies a higher state than Git/PR/deploy/QA evidence proves. |
| Critical-lane boundary | Did auth, payment, invoice, commission, migration, deploy, production data, or mobile API contract behavior change? | Read-only diagnosis, approval, reviewer, or safe evidence is missing. |
| Release communication | Do staff/users need changelog, help text, What's New, or operational notice? | A relevant staff-facing change has no release communication and no reason it is unnecessary. |
| Generated files | Were generated files edited manually instead of changing the source? | A generated artifact was hand-edited without project rules saying it is human-maintained. |
| Visible UI quality | If UI changed, does it look coherent and match the project pattern? | The changed UI has obvious layout, copy, state, accessibility, or consistency issues that are in scope or unreported. |
| Lint/test/flaky checks | Are failures caused by this change, pre-existing, unrelated, or flaky? | Failures caused by the change remain, or unrelated failures are hidden instead of reported and routed. |
| Multi-fix state | Are there multiple fixes, branches, commits, PRs, or deploy candidates in this session? | Session Release Ledger is missing/stale or any fix state is unclear before push/merge/deploy. |
| Product/business risk | Does Hafiz need to decide wording, UX fit, staff workflow, policy, timing, or risk acceptance? | The agent presents a business/product judgment as already decided. |

When review finds a risk, say the practical meaning first:

```text
This can be committed locally, but it is not ready to push because the browser
journey is still unproven.
```

Then name the next action:

```text
Recommended next: run the focused Playwright path, then re-review before push.
```

Do not bury a blocking risk inside a long summary. If something blocks commit,
push, PR, merge, deploy, or a "ready" claim, lead with it.

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
   Use [sims-ui-audit.md](sims-ui-audit.md) when the review needs a dedicated
   visual/screenshot audit.
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
8. For bugfix, hotfix, or user-facing small-change work, treat missing
   related-impact audit as a review finding. Use
   [related-impact-audit.md](related-impact-audit.md) to decide whether the work
   needed only a local related check, a same-pattern sweep, or a critical
   impact audit.
9. For staff-facing feature, bugfix, hotfix, or small-change work, treat
   missing release communication as a review finding when relevant. Check for a
   `CHANGELOG.md` entry, affected module help updates, and a What's New release
   entry or seed script. If any item is intentionally not needed, the PR or
   final answer must say why.
10. For multi-fix sessions, treat a missing or stale Session Release Ledger as a
   review finding. Before push, merge, PR, or deploy, verify every session fix
   is classified as local-only, pushed, PR-open, merged, deployed, or excluded.
11. Run the Review And Risk Checkpoint before saying the work is safe for the
    next state.
12. Report findings by severity with file and line references where possible.

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

Related impact:
- <current | missing finding | not applicable, with reason>

Session release ledger:
- <not applicable | current | missing finding>

Next state:
- <safe for commit | safe for push | safe for PR | safe for merge | safe for deploy | not safe yet, with reason>

Summary:
- <brief context>
```
