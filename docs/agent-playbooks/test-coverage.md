# Test Coverage Manifest Playbook

Use this whenever an agent starts implementation work, verifies a change, runs
QA, prepares a commit, or reviews a PR in a Sifututor project that has
`TESTING.md`.

## Practical Rule

`TESTING.md` is the project coverage map. Before changing user-facing behavior,
check the map so the agent knows whether the affected feature already has real
tests, partial tests, or no tests.

The rule is simple:

```text
No user-facing feature change should leave the project with missing or fake test
coverage for that feature, and no user-facing workflow should be called done
without human-journey evidence.
```

## Start Of Work

1. Read the project `TESTING.md` after `AGENTS.md` and `CLAUDE.md`.
2. Identify the feature area touched by the task.
3. Find the matching feature row in the coverage table.
4. Report the current status in plain English:
   - covered: name the test file that protects it
   - partial: say what is missing and recommend the smallest useful test
   - missing: stop before implementation unless Hafiz explicitly asks for docs
     or investigation only
5. For user-facing work, identify the human journey that needs proof:
   - browser flow: Playwright, browser smoke, screenshot-backed QA, or manual
     checklist
   - mobile flow: Maestro, Detox, simulator/device smoke, screenshot-backed QA,
     or manual checklist
   - backend-only API flow: API/curl smoke plus paired frontend/mobile evidence
     when a real user depends on the response
6. If no row matches, treat that as a coverage-manifest gap and add/update the
   manifest as part of the work.

## What Counts As A Real Test

A real test proves behavior that matters to a user, staff member, admin,
customer, mobile app, integration, or business rule.

Real tests usually include:

- setup data that matches the real workflow
- the action a real user, API client, job, or integration performs
- an assertion on the important result, state change, response shape, permission
  guard, notification, payment/invoice state, or visible UI
- at least one failure or edge case for risky flows

Fake or weak tests include:

- tests that only assert a component renders without checking behavior
- snapshots with no meaningful assertion for the bug or rule
- endpoint smoke tests that only check HTTP 200 for a complex business rule
- mocked tests where the mocked value is the same thing being asserted
- tests that do not fail if the production bug returns

## During Implementation

For feature, bugfix, hotfix, and refactor work:

1. Add or update the test first when the change is testable.
2. Keep the test at the right level:
   - business rule or calculation: unit/service test
   - controller/API contract: feature/API test
   - browser or mobile user journey: E2E/smoke test
   - cross-system contract: API contract test plus paired frontend/mobile check
3. Update `TESTING.md` when coverage status, test files, or critical gaps
   change.
4. Do not mark a feature covered just because a file exists. The named test must
   assert the behavior.

## Human Journey Verification

Human-journey evidence proves that the workflow works the way a real person
uses it. It sits above code tests.

Use this ladder:

1. Automated E2E: Playwright, Maestro, Detox, or equivalent.
2. Agent-run smoke: browser/mobile/API flow with screenshots or response
   evidence.
3. Manual QA checklist: exact steps, expected result, actual result, tester, and
   date.
4. Human sign-off: required for judgment, wording, destructive action, external
   systems, unavailable credentials, or business decisions.

Agents must not jump straight to human QA when they can safely run an automated
or agent-run smoke check themselves. If E2E is not feasible, record why:
`missing credential`, `no representative data`, `destructive action required`,
`external system unreliable`, or `tooling unavailable`.

Examples:

- TAC/SMS: API test for code validation, plus mobile/browser journey evidence
  showing request, entry, retry/expiry, and success/failure states.
- Change Level: feature test for state transition, plus Playwright/staff-flow
  evidence showing the staff action and visible result.
- Deactivate Request: service/API test for status change, plus E2E/manual QA
  evidence showing the request can be deactivated and no longer appears as
  active.

## Verification And QA

Run the project checks from `verify.md` and `qa.md`, then run the manifest check
when available:

```bash
python3 ../scripts/agent-checks/test-coverage-manifest-check.py --project .
```

From the umbrella root, pass the project path:

```bash
python3 scripts/agent-checks/test-coverage-manifest-check.py --project sifu-tutor
```

This script validates that test files named in `TESTING.md` exist. It does not
prove the tests are meaningful; the agent and reviewer still need to inspect
test intent.

## Commit And Review Bar

Before commit or PR review, answer these questions:

1. Which feature row in `TESTING.md` matches the change?
2. Is the status still accurate?
3. Which test proves the changed behavior?
4. Would that test fail if the old bug or risky behavior returned?
5. What human-journey evidence proves the user can complete the workflow?
6. If E2E/manual QA was not run, is the reason explicit and acceptable?
7. If coverage is partial or missing, is that explicitly reported with the next
   test to add?

If the answer to any question is unclear, do not call the work complete.

## Universal AI Tooling

Each project with a coverage manifest should also have:

- `AI-RULES.md`: stable project rules that any AI assistant can read
- `ONBOARDING-PROMPT.md`: the prompt a developer can paste into any AI tool at
  the start of a session

Claude-specific hooks are useful, but they are not the source of truth. The
portable source of truth is:

```text
AGENTS.md -> TESTING.md -> AI-RULES.md -> this playbook -> verify/QA/review
```
