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

- `sifu-tutor`: use Pest for backend behavior, Playwright smoke for UI or
  browser-visible bugfixes, and manual QA references in `docs/` when the module
  has a checklist. Financial modules need human review before commit.
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

## QA Report

```text
QA - PASS | FAIL | PARTIAL

Tier: <docs|small-change|bugfix|hotfix|feature|refactor>
Automated evidence:
- <command>: <result>

Manual/browser evidence:
- <flow checked or not applicable>

Regression coverage:
- <covered | not feasible, reason>

Blockers:
- none | <list>
```
