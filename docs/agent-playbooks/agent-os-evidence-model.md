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

## Proof Standard

Every evidence report should separate proof into three practical layers:

| Layer | Proves | Typical evidence |
| --- | --- | --- |
| Code proof | The engine, rule, or build is not obviously broken. | Unit/service tests, feature/API tests, lint, typecheck, build, static checks. |
| Journey proof | A real user or system can complete the changed workflow. | Playwright/browser/mobile flow, API/curl smoke, screenshots, read-only state checks, manual QA checklist when automation is unsafe. |
| Release proof | The fix reached the claimed environment and was checked there. | Git/PR/merge state, deployed SHA/version, staging/production smoke, logs, monitoring. |

Plain meaning:

```text
Code proof says the parts work.
Journey proof says a person can use it.
Release proof says the right version reached the right place.
```

The agent must report the highest proven state, not the hoped-for state.

Examples:

| Do not say | Say instead |
| --- | --- |
| fixed | changed locally, not committed yet |
| done | committed locally, not pushed |
| ready | ready for commit, but UI journey still unproven |
| deployed | deployed to staging, production not touched |
| live | deployed and route reachable, but live workflow smoke is still missing |
| Hafiz can check | agent-run checks passed; Hafiz still needs to judge wording/risk |

Use this sentence shape when the distinction matters:

```text
Highest proven state: <state>.
What proves it: <tests/checks/evidence>.
What is not proven yet: <gap or none>.
Recommended next: <next action>.
```

This keeps Hafiz from having to translate test output into practical status.
The agent should say whether work is ready for commit, PR, staging QA, deploy,
live check, or Hafiz acceptance.

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

Use this matrix before saying work is ready.

| Work Type | Minimum Evidence Before Saying Ready |
| --- | --- |
| Discussion / planning | Clear summary, captured decision, named next step, and any open question made explicit. |
| Docs / Agent OS changes | Readback or diff review, link/path check where relevant, Agent OS health/doctor for workflow changes, and pre-commit guard when committing. |
| Small non-user-facing code | Focused unit/service/lint/type/build check around the changed surface. |
| Backend logic | Unit/service/feature test proving the rule, plus meaningful edge-case coverage when the rule has business or data risk. |
| API contract | API/contract test, response shape checked, permission/error behavior where relevant, and paired frontend/mobile evidence when a real user depends on it. |
| UI bugfix | Old failure reproduced or clearly described, focused regression proof, browser/Playwright proof of the real action, screenshot when useful, and permanent E2E by default. |
| New user-facing feature | Happy path, important edge cases, role/permission/state coverage, affected `TESTING.md` row, permanent E2E for each new/changed workflow, and human-journey evidence. |
| Mobile app change | Unit/screen tests, lint/type checks, and simulator/device/build smoke when native behavior or a real journey changes. |
| Auth, payment, invoice, commission, migration, or mobile API critical lane | Read-only diagnosis first, Hafiz approval, then implementation tests plus safe staging/human-journey evidence before release. |
| Deploy / release | Confirm deployed version, smoke the changed workflow on the target environment when safe, check logs/monitoring, and name anything not live checked. |
| Production incident | Confirm symptom, scope impact, mitigation, fix evidence, deploy/smoke/monitor result, and durable post-incident lesson when useful. |

Plain meaning:

```text
Lower-level evidence proves the engine.
Human-journey evidence proves a real person can use the workflow.
Deployment evidence proves the version is running.
Live-check evidence proves the changed workflow works where it was deployed.
```

Every final report should say the evidence level reached.

Examples:

```text
Docs evidence: Agent OS health and workflow doctor passed.
Backend evidence: feature test passed; no browser journey needed.
UI evidence: Playwright clicked the real button and captured a screenshot.
Deploy evidence: commit is deployed, but live workflow smoke is still waiting.
```

Do not say "ready" without saying ready for what:

```text
ready for commit
ready for PR review
ready for staging QA
ready for deploy
deployed, live check still waiting
live checked, waiting for Hafiz acceptance
```

## Evidence Gap Stop Rules

An evidence gap is any missing proof that the work type normally requires.

Plain version:

```text
Missing proof is not the same as failure, but it must be named.
The agent must say what is proven, what is still unproven, and whether the next
step is still safe.
```

Use this table before moving to commit, push, PR, merge, deploy, or "done".

| Gap Type | Practical Meaning | What The Agent Should Do |
| --- | --- | --- |
| Low-risk note | The missing check does not affect the claim being made. Example: docs-only work has no browser journey. | Continue, but say why the stronger evidence is not needed. |
| Named exception | The right check matters, but cannot be run safely now because of a concrete blocker. | State the blocker, strongest evidence gathered, risk if continuing, and follow-up test/fixture. Do not pretend this equals full proof. |
| Blocks commit/PR/push | The missing proof is required to trust the changed workflow. Example: UI workflow has no browser/mobile evidence or permanent E2E decision. | Stop before calling it ready. Gather the evidence or ask Hafiz to accept a specifically named exception when policy allows it. |
| Blocks deploy/live/production | The missing proof affects real users, money, data, critical lanes, deployed version, smoke, or monitoring. | Stop before deploy/live claim. Get the missing evidence or explicit Hafiz approval for the exact risk boundary. |
| Cannot be accepted as done | The action would cross a forbidden boundary or the evidence is actively failing. Example: secrets, destructive action, failed required tests, unapproved critical-lane implementation. | Stop. Do not downgrade it to "manual check later" or "ready with risk." |

Allowed named-exception reasons are:

- `missing credential`
- `no representative data`
- `destructive action required`
- `external system unreliable`
- `tooling unavailable`
- `not user-facing`

When reporting a gap, use this shape in normal language:

```text
What I proved:
What I could not prove:
Why it is missing:
Risk if we continue:
Recommended next:
Can Hafiz accept the risk here: yes/no, and why.
```

Examples:

```text
I proved the backend rule with a feature test, but I have not proved the real
staff browser journey. This is ready for backend confidence, not ready for UI
workflow confidence. Recommended next: run Playwright and add/update the
permanent E2E coverage.
```

```text
I confirmed the deployed route is reachable, but I could not smoke the real
payment workflow because it would require a destructive real transaction. This
cannot be called live-verified. Recommended next: use safe staging/test payment
evidence or get explicit finance risk acceptance for the production limitation.
```

Some gaps can be accepted by Hafiz as a business or release-risk decision.
Examples: wording acceptance, subjective UX fit, a non-critical check that is
tooling-blocked, or a manual QA exception with clear follow-up.

Some gaps cannot be accepted as "done" by wording alone. Examples: forbidden
secret access, failed required tests, unapproved critical-lane implementation,
destructive action without explicit approval, or a user-facing workflow called
ready without either human-journey evidence or a valid named exception.

## Permanent Regression Decision

For user-facing bugs and features, one-off proof is not enough by itself.

The agent should either:

- add/update a permanent E2E test for every changed staff/admin/parent/tutor/
  student/customer workflow, or
- clearly state why it is not feasible now and name the follow-up fixture/test.

Backend, API, service, route-smoke, production-smoke, and manual QA evidence can
support the E2E, but they do not replace permanent E2E coverage when the real
workflow can be automated safely.

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
