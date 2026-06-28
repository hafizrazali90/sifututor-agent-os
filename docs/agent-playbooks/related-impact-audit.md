# Related Impact Audit

Use this when fixing a product/project bug, hotfix, or visible behavior issue.

Plain meaning:

```text
When we fix one bug, check whether the same kind of bug exists nearby or whether
the fix could break an adjacent workflow.
```

This is separate from the Agent OS Improvement Loop. The Agent OS Improvement
Loop improves how agents work. Related Impact Audit improves product fix
quality.

## Research Baseline

This playbook follows common mature engineering practice:

- keep bugfixes focused instead of mixing unrelated refactors into one change
- identify the root cause, not only the reported symptom
- add or update regression evidence so the bug does not quietly return
- check nearby impact before claiming the fix is safe
- track related but out-of-scope work separately

Useful references:

- Google Engineering Practices: keep changes small and focused, and review
  tests appropriate to the change.
- Google Software Engineering, chapter 9: tests protect behavior and help catch
  regressions.
- Atlassian postmortem and root-cause guidance: identify causes and corrective
  actions that prevent recurrence.
- GitLab code review guidance: review correctness, maintainability, and
  security impact.
- Microsoft SDL: use stronger validation for security-sensitive or high-risk
  surfaces.

## Core Rule

Every bugfix gets at least a local related check.

Use stronger checks when the root cause is reusable or the lane is critical.

```text
local related check -> same-pattern sweep -> critical impact audit
```

In normal words:

```text
Start near the bug. If the cause looks reusable, search for the pattern. If the
bug touches money, auth, production, migrations, or mobile contracts, check the
broader impact before saying it is safe.
```

## Three Audit Strengths

| Strength | Use when | What to check |
| --- | --- | --- |
| Local related check | Every bugfix, hotfix, and user-facing small change. | Same file, same component/controller/service, same page/table/modal/action, same role/status branch, obvious adjacent behavior. |
| Same-pattern sweep | The root cause is reusable or has appeared before. | Same helper/component/service method, enum/status/action guard, null-safety boundary, stored aggregate, permission guard, API shape, event/job/listener pattern. |
| Critical impact audit | Auth, payment, invoice, commission, migration, deployment, production data, mobile API contract, or security-sensitive behavior. | Same-pattern bugs, adjacent workflow regression, state/data/security/API impact, stronger test/evidence, release/monitoring risk, and explicit approval before widening scope. |

## Scope Rule

Find related risks proactively.

Fix only clearly in-scope related issues.

Ask or track anything that expands scope.

Plain meaning:

```text
Do not miss obvious related bugs, but do not turn one bugfix into an uncontrolled
rewrite.
```

## When To Run

Run during:

- diagnosis, after the likely root cause is understood
- implementation planning, before deciding the smallest safe fix
- verification, after the fix works locally
- QA, when checking real user journeys and regression behavior
- review, before commit, push, PR, merge, or deploy

Skip only when the work is clearly not a bugfix or behavior change, such as a
pure typo, formatting-only docs edit, or investigation with no fix.

## Audit Steps

1. Name the exact fixed issue.
2. Name the root-cause pattern.
3. Choose the audit strength.
4. Search or inspect the related surface.
5. Decide which related findings are in scope.
6. Add or update regression evidence.
7. Report what was checked, what was found, and what remains.

## What To Search

Use the smallest useful search first:

| Root-cause pattern | Search examples |
| --- | --- |
| Null safety | Same property chain, optional relation, missing fallback, request field, API payload key. |
| Status/enum mismatch | Same enum value, string status, state transition, filter option, tab count. |
| Permission/action guard | Same policy, route middleware, button condition, role check, destructive action. |
| Stored aggregate | Parent total/count/status cached from child rows, recalculation after add/remove/update. |
| UI action/modal/table bug | Same component, action menu, modal trigger, DataTable/Ajax route, loading/error state. |
| API/mobile contract | Same response shape, nullable field, versioned route, mobile consumer, frontend type. |
| Queue/event/job/listener | Same event dispatch, retry/idempotency behavior, listener side effect, notification. |
| Payment/invoice/commission | Same callback/status mutation, invoice edit/download/view, receipt, ledger, commission calculation. |

## Evidence To Report

Report:

- audit strength used
- files, routes, tests, browser paths, API paths, or searches checked
- related issues found
- what was fixed now
- what was intentionally left out of scope
- follow-up issue, Mission Ledger item, or explicit Hafiz decision when needed
- regression test or evidence covering the original issue and related pattern

## Stop And Ask

Stop before expanding scope when:

- the related issue changes business behavior
- the related issue touches critical lanes
- the related issue needs production data mutation or destructive action
- fixing it would cross into another module/app/API contract
- the evidence suggests a bigger redesign rather than a narrow fix
- the related finding is real but not necessary to prove the current fix

## Output Shape

Use this concise shape in verify, QA, review, or final close-out:

```text
Related impact:
- Strength: <local related check | same-pattern sweep | critical impact audit>
- Checked: <files/routes/components/tests/searches>
- Found: <none | related risks>
- Fixed now: <items or none>
- Out of scope / follow-up: <items or none>
- Regression proof: <test/evidence or named gap>
```

## Examples

### Local Related Check

Bug: one action button does nothing on a table.

Check:

- same action menu component
- nearby modal triggers on the same page
- route names used by the same table
- loading/error state after the click

### Same-Pattern Sweep

Bug: one controller crashes on `->request->class_type`.

Check:

- same controller for other unguarded `->request->...` chains
- related invoice/edit/download methods
- test coverage for missing relation or nullable request payload

### Critical Impact Audit

Bug: invoice payment status is wrong after callback.

Check:

- callback idempotency and declined/duplicate behavior
- invoice view/edit/download state
- parent/tutor/staff-visible status
- commission or ledger side effects
- API/mobile consumers if the status is exposed
- regression test plus safe read-only state evidence
