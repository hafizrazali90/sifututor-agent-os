# QA Playbook

Use this for `/qa`, smoke tests, regression tests, visual QA, and route-level
quality evidence.

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
- `sifu-tutor`: use Pest for backend behavior, Playwright smoke for UI or
  browser-visible bugfixes, and manual QA references in `docs/` when the module
  has a checklist. Financial modules need human review before commit.
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

TESTING.md:
- <feature row checked, status, named test file, or not applicable>

Blockers:
- none | <list>
```
