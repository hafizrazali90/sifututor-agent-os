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
- Agents must not hand off checks that they can safely run themselves. Before
  asking Hafiz, staff, or another human to verify, exhaust the available
  non-destructive evidence channels in this order: automated tests, Playwright
  browser smoke, API/curl smoke, server-side read-only inspection, and screenshot
  capture. Human QA is for judgment, sign-off, credentials/data that are truly
  unavailable, or destructive/business decisions; it is not a substitute for
  agent-run evidence.
- After any staging or production deploy, smoke-test the actual changed
  user-facing functionality, not only generic route availability. Route-only
  checks are acceptable only when a safe login, test account, or representative
  data is unavailable; report that limitation clearly and state the strongest
  functional evidence gathered instead.
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

If no automated regression test is feasible, say why and provide the strongest
manual or browser evidence available. Do not pretend manual evidence is the same
as an automated regression.

## Handoff Bar

Do not write "please manually check" or equivalent as the next step until you
have tried the checks an agent can run in the current environment. If you cannot
run Playwright, API, CLI, or server-side evidence, state the exact blocker
(`missing credential`, `no representative data`, `destructive action required`,
or `tooling unavailable`) and what evidence you gathered instead.

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

Regression coverage:
- <covered | not feasible, reason>

Permanent E2E:
- <added/updated file path | not added, reason and follow-up fixture/test>
Changed workflows:
- <workflow>: <permanent E2E file | explicit exception>

TESTING.md:
- <feature row checked, status, named test file, or not applicable>

SIMS UI/UX:
- <docs checked, findings, or not applicable>

Blockers:
- none | <list>
```
