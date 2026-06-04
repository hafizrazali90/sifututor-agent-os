# Agent OS Evidence Model

Use this document when deciding how much proof an agent must gather before
calling work verified, ready for QA, ready for review, or ready for Hafiz's
decision.

## Core Idea

The agent is Hafiz's bridge into code.

Hafiz can think technically and understand systems, but he should not have to
do the coding or basic tester work that the agent can safely do with tools. The
agent should use the terminal, browser, API clients, mobile tools, logs,
database-safe reads, screenshots, MCP, CLI, and project scripts to gather the
same kind of evidence a capable human tester would gather.

Plain version:

```text
The agent checks what a developer/tester can check.
Hafiz checks what only the owner/user/business person can judge.
```

## What Testing Means Here

Testing is not only "unit tests passed".

In the Agent OS, testing means evidence that the real thing works:

- the code engine behaves correctly
- the API contract returns the expected shape and rules
- the UI or mobile app lets a real user complete the journey
- the important state actually changes
- old bugs cannot quietly return
- risky edge cases have been considered
- any remaining human check is clearly explained

This matches existing Sifututor testing standards:

- `TEST-PLAN.md` says manual tests should include setup, action, expected
  outcome, how to verify, and what failure looks like.
- `docs/agent-playbooks/test-coverage.md` says no user-facing workflow should
  be called done without human-journey evidence.
- project QA docs such as `sifu-tutor-1375-tests/docs/manual-qa-standard.md`
  require observable expected results, severity, priority, test data, and
  failure notes.
- mobile QA docs such as `sifututor_tutor/docs/qa-framework.md` say tests must
  reflect user behavior, not implementation details.
- Ripple QA docs such as `ripple-suite/qa/WHAT-WE-TEST.md` explain tests in
  plain language so non-coding stakeholders can understand what is protected.

## Evidence Ladder

Use the strongest practical evidence available, without turning every task into
heavy ceremony.

| Level | Evidence | Practical Meaning |
| --- | --- | --- |
| 1 | Static checks, lint, typecheck, build | The code is shaped correctly and can compile/run. |
| 2 | Unit/service tests | The calculation, rule, helper, or isolated behavior is correct. |
| 3 | Feature/API/contract tests | The server, endpoint, permissions, and response shape behave correctly. |
| 4 | Automated browser/mobile E2E | A real user journey works in an automated browser/device flow. |
| 5 | Agent-run smoke with screenshots/API evidence | The agent used the app/API like a tester and captured proof. |
| 6 | Manual QA checklist | A human follows exact steps when automation is unavailable or unsafe. |
| 7 | Hafiz sign-off | Owner judgment for product fit, business risk, wording, release timing, or final acceptance. |

Non-technical version:

```text
Lower levels prove the machine parts.
Higher levels prove a person can actually use the thing.
Hafiz should mostly live at the top, not at the bottom.
```

## Agent-As-Tester Rule

Before asking Hafiz to verify something, the agent must ask:

```text
Can I safely check this myself with the tools I have?
```

If yes, the agent should do it.

Examples:

- If a button was fixed, the agent should open the page with Playwright or a
  browser tool and click the button.
- If a modal was broken, the agent should reproduce the modal opening and check
  the visible result.
- If an API changed, the agent should run the API/client/contract check and
  inspect the response shape.
- If a list was filtered wrongly, the agent should use representative data and
  verify the row appears or disappears as expected.
- If a mobile flow changed, the agent should run Jest/screen tests and, when
  practical, simulator/device smoke.
- If a financial status changed, the agent should verify the business state
  using safe test data, API evidence, and server-side read-only checks.

"Please check manually" is not enough when the agent had safe access to gather
evidence.

## What Hafiz Should Verify

Hafiz should verify things the agent cannot safely or honestly decide:

- business judgment: "is this the right rule?"
- subjective product fit: "does this wording/design feel right?"
- real-world acceptance: "will staff accept this workflow?"
- unavailable access: credential, device, account, or data the agent does not
  have
- destructive workflow: payment capture, deletion, production mutation, real
  notification blast, or anything unsafe to test automatically
- final risk acceptance: shipping despite a known gap
- priority and scope decisions: whether to fix now, defer, or expand

When the agent asks Hafiz to verify, it should also say what it already checked
and why the remaining check needs Hafiz.

## Human-Journey Test Shape

Every human-style test should be understandable without reading code.

Use this shape:

| Field | Meaning |
| --- | --- |
| Setup | What state/account/data is needed before the test starts. |
| Action | What the user or system does. |
| Expected result | What should be visibly or measurably true. |
| How to verify | Browser screenshot, API response, database-safe read, log line, test assertion, or manual observation. |
| Failure looks like | What would prove the bug still exists or the feature failed. |

This format works for automated E2E, agent-run smoke, manual QA, and plain
language test documentation.

## Evidence By Work Type

| Work Type | Minimum Evidence |
| --- | --- |
| Discussion or architecture docs | Readback, link/path check, guard script when useful. |
| Small non-user-facing code change | Focused unit/test/build check around the changed surface. |
| User-facing UI bugfix | Regression test or permanent E2E decision, plus browser/mobile evidence for the real action. |
| User-facing feature | Happy path, important edge cases, affected `TESTING.md` row, and human-journey evidence. |
| API contract change | Contract/API test plus paired frontend/mobile evidence when a real user depends on it. |
| Auth, payment, invoice, commission, migration, mobile API critical lane | Read-only diagnosis first, then approved implementation, then tests plus human-journey or safe staging evidence. |
| Release/deploy | Changed workflow smoke on the deployed environment when safe, plus log/monitoring check where relevant. |

## Permanent Regression Decision

For user-facing bugs and features, one-off proof is not enough by itself.

The agent should either:

- add/update a permanent E2E or equivalent regression test, or
- clearly state why it is not feasible now and name the follow-up fixture/test.

Allowed reasons:

- `missing credential`
- `no representative data`
- `destructive action required`
- `external system unreliable`
- `tooling unavailable`
- `not user-facing`

## Close-Out Standard

When reporting evidence to Hafiz, use plain language first:

```text
I checked this like a staff member would use it:
opened the page, clicked the action, confirmed the modal appeared, and verified
the saved state through the API.

What still needs you:
only the wording/UX acceptance, because that is a product judgment.
```

Use formal labels only when useful for QA, commit, handoff, or audit trail.
