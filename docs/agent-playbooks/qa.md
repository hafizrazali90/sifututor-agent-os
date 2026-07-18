# QA Playbook

Use this for `/qa`, smoke tests, regression tests, visual QA, and route-level
quality evidence.

Use [agent-os-evidence-model.md](agent-os-evidence-model.md) as the source of
truth for human-journey evidence and for deciding what the agent should test
itself before asking Hafiz or staff for manual verification.

Use the Evidence By Work Type matrix in
[agent-os-evidence-model.md](agent-os-evidence-model.md) to decide the minimum
QA proof for the changed surface. Plain meaning: docs, backend logic, API
contracts, UI, mobile, deploys, and incidents do not need the same proof, but
each must name the strongest evidence actually gathered.

Use the Proof Standard in
[agent-os-evidence-model.md](agent-os-evidence-model.md). Plain meaning: QA
should say whether it proved the real journey, whether the release/live state
was checked, and what is still only code-level confidence.

Use the Evidence Gap Stop Rules in
[agent-os-evidence-model.md](agent-os-evidence-model.md) when the strongest
available evidence is weaker than the workflow normally requires. Plain
meaning: QA may say "tested this part, still missing this proof"; it must not
turn missing proof into a generic "please check" note.

Use [related-impact-audit.md](related-impact-audit.md) for bugfix and hotfix QA
so the check includes related behavior and regression risk, not only the exact
reported symptom.

## Pick The QA Tier

| Route | QA expectation |
| --- | --- |
| `docs` | Link/render check or documentation validation where applicable |
| `small-change` | Targeted check for the changed surface |
| `bugfix` | Regression test proving the old failure cannot recur |
| `hotfix` | Regression test plus focused smoke check |
| `feature` | Happy path, important edge cases, and route smoke |
| `refactor` | Existing behavior tests plus one targeted check around touched code |

## Project Notes

- For projects with `TESTING.md`, QA must state the affected feature row,
  whether the row is covered/partial/missing, and whether the named test really
  protects the workflow being changed. Use [test-coverage.md](test-coverage.md).
- User-facing behavior needs human-journey evidence. Prefer automated E2E
  first, then agent-run browser/mobile/API smoke with screenshots or response
  evidence, then manual QA checklist/sign-off only when automation is not safe
  or feasible.
- Any staff/admin/parent/tutor/student/customer workflow that can be performed
  in the product should have permanent E2E coverage. QA must name the E2E file
  that protects the changed workflow, or mark QA as incomplete with a named
  exception and follow-up test/fixture.
- QA should validate what a real person would validate: setup, action, expected
  result, how to verify, and what failure looks like. The agent should translate
  technical checks into this human-test shape when reporting back to Hafiz.
- When an agent creates a meaningful browser/Playwright smoke for a feature or
  bugfix, convert that check into a permanent E2E regression test with stable
  seed or fixture data whenever feasible. If it cannot be made permanent in the
  same task, report the exact reason and the fixture/test follow-up needed.
- `sifu-tutor`: use Pest for backend behavior, Playwright smoke for UI or
  browser-visible bugfixes, and manual QA references in `docs/` when the module
  has a checklist. Financial modules need human review before commit.
- `sifu-tutor` UI/UX QA must also check `sifu-tutor/docs/ui-ux/quality-gate.md`
  plus the relevant surface-map, design-system, page/component/content,
  accessibility/state, and review-checklist docs. Report any token drift,
  missing loading/empty/error states, unclear critical-action copy, or invented
  one-off patterns as QA findings.
- For `sifu-tutor` UI-visible changes, use the project `ux-reviewer` subagent
  when Claude is available, or perform the same screenshot-backed review from
  `sifu-tutor/docs/ui-ux/review-and-qa-checklist.md` in Codex. QA is incomplete
  if changed modals, dropdowns, disabled controls, dense tables, or empty states
  are skipped without a named blocker.
- Visual QA must inspect the complete interactive surface, not only the page
  shell. Check embedded forms, third-party widgets, browser/native controls,
  submit buttons, focus/hover/disabled/error/loading states, and inherited
  colors/tokens. A correct surrounding page does not prove an embedded control
  follows the active design system.
- Before accepting local browser or screenshot evidence, prove target identity:
  exact URL, serving process, checkout/worktree, branch, commit or local-dirty
  state, and restart/rebuild state. For staging/production, confirm the deployed
  SHA/version. Evidence from a stale port, wrong checkout, or old UI shell is
  inconclusive even when the screenshot itself looks correct.
- Technical UAT and agent-run user-story checks prove journey behavior; they do
  not prove Hafiz's product acceptance. Report these states separately until
  Hafiz or the named owner completes or explicitly accepts the walkthrough.
- Agents must not hand off checks that they can safely run themselves. Before
  asking Hafiz, staff, or another human to verify, exhaust the available
  non-destructive evidence channels in this order: automated tests, Playwright
  browser smoke, API/curl smoke, server-side read-only inspection, and screenshot
  capture. Human QA is for judgment, sign-off, credentials/data that are truly
  unavailable, or destructive/business decisions; it is not a substitute for
  agent-run evidence.
- After any staging or production deploy in any Sifututor project, smoke-test
  the actual changed user-facing functionality before calling the release done.
  Generic route availability alone is not enough when a safe changed-workflow
  smoke is possible. Route-only checks are acceptable only when a safe login,
  test account, or representative data is unavailable; report that limitation
  clearly and state the strongest functional evidence gathered instead.
- `ripple-suite`: use Playwright smoke and the route tier from
  `CODEX-WORKFLOW.md`; protect SIMS read-only behavior and Neon writes.
- `sifututor_tutor` and `sifututor_parent`: use Jest/unit tests for logic,
  `npm run check` where available, and iOS/Android build evidence when native
  behavior changes.
- `lls`: use feature tests for HTTP behavior; for API contract changes, include
  paired `lls-frontend` evidence.

## Regression Evidence

For bugfix and hotfix tasks, state:

1. the old failure mode
2. the test or check that fails before the fix or directly covers the old bug
3. the command proving it now passes
4. any related behavior that was smoke-checked
5. the related-impact audit strength and result from
   [related-impact-audit.md](related-impact-audit.md)

If no automated regression test is feasible, say why and provide the strongest
manual or browser evidence available. Do not pretend manual evidence is the same
as an automated regression.

## Handoff Bar

Do not write "please manually check" or equivalent as the next step until you
have tried the checks an agent can run in the current environment. If you cannot
run Playwright, API, CLI, or server-side evidence, state the exact blocker
(`missing credential`, `no representative data`, `destructive action required`,
or `tooling unavailable`) and what evidence you gathered instead.

If the missing evidence blocks the next state, say that directly:

```text
This is QA-checked at the API level, but not ready for UI workflow confidence
because the browser journey is still unproven.
```

## QA Report

```text
QA - PASS | FAIL | PARTIAL

Tier: <docs|small-change|bugfix|hotfix|feature|refactor>
Automated evidence:
- <command>: <result>

Manual/browser evidence:
- <flow checked or not applicable>

Human journey:
- <automated E2E | agent-run smoke | manual QA checklist | not applicable>
- <why this is enough, or why stronger evidence was not feasible>
Highest proven state:
- <code proof only | journey proof | staging checked | production live checked | accepted / closed>

Regression coverage:
- <covered | not feasible, reason>

Related impact:
- <strength, checked, found, fixed now, follow-up>

Permanent E2E:
- <added/updated file path | not added, reason and follow-up fixture/test>
Changed workflows:
- <workflow>: <permanent E2E file | explicit exception>

TESTING.md:
- <feature row checked, status, named test file, or not applicable>

SIMS UI/UX:
- <docs checked, findings, or not applicable>

Target identity:
- <URL/environment, process, worktree/branch, commit or local-dirty state, restart/rebuild>

Blockers:
- none | <list>
```
