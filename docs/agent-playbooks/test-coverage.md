# Test Coverage Manifest Playbook

Use this whenever an agent starts implementation work, verifies a change, runs
QA, prepares a commit, or reviews a PR in a Sifututor project that has
`TESTING.md`.

Use [agent-os-evidence-model.md](agent-os-evidence-model.md) with this playbook.
`TESTING.md` maps what should be protected; the evidence model defines how an
agent proves the protection behaves like the real user journey.

## Practical Rule

`TESTING.md` is the project coverage map. Before changing user-facing behavior,
check the map so the agent knows whether the affected feature already has real
tests, partial tests, or no tests.

The rule is simple:

```text
No user-facing feature change should leave the project with missing or fake test
coverage for that feature, and no user-facing workflow should be called done
without permanent E2E coverage plus human-journey evidence.

Any function a staff member, admin, parent, tutor, student, customer, or mobile
user can perform should be mapped to a permanent E2E test. The purpose is not
only to prove today's fix; it is to let the team periodically run the full E2E
suite and catch regressions across the product.
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
   - browser flow: Playwright E2E by default
   - mobile flow: Maestro, Detox, Playwright-compatible mobile web, or
     simulator/device E2E by default
   - backend-only API flow: API/curl smoke plus paired frontend/mobile evidence
     when a real user depends on the response
6. Name the permanent E2E file that already covers the workflow, or add/update
   one as part of the task. Browser/mobile smoke and manual QA can supplement
   the E2E, but they do not replace it when automation is feasible.
7. If no row matches, treat that as a coverage-manifest gap and add/update the
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
or agent-run smoke check themselves. Agent-run smoke and manual QA are
supporting evidence; for repeatable regression protection, add/update the
permanent E2E whenever the workflow can be automated safely. If E2E is not
feasible, record why:
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

## Enforcement

One script enforces every rule above, for every agent:

```text
scripts/agent-checks/coverage_enforcement.py
```

Claude, Codex, Kilo, and any future tool run the same file and get the same
answer. There is no Claude-only and Codex-only version of "is this covered?".

It has three modes. Pick the one that matches what you are about to do.

| Mode | Scope | Use it when |
| --- | --- | --- |
| `manifest` | Every row in `TESTING.md` | Auditing a project, or reporting the whole coverage picture. |
| `change` | Only the rows this change touches | Before commit. This is what the shared guard runs. |
| `release` | Only the rows this release touches | Before push, PR, merge, or deploy. |

```bash
# Whole manifest, from inside the project
python3 ../scripts/agent-checks/coverage_enforcement.py --project . --mode manifest

# What this commit is answerable for
python3 ../scripts/agent-checks/coverage_enforcement.py --project . --mode change --staged

# What this release is answerable for
python3 ../scripts/agent-checks/coverage_enforcement.py --project . --mode release --base main
```

From the umbrella root, pass the project path instead:

```bash
python3 scripts/agent-checks/coverage_enforcement.py --project sifu-tutor --mode manifest
```

`scripts/agent-checks/test-coverage-manifest-check.py` is still the audit
entrypoint named by `AGENTS.md`. Its command line and summary output have not
changed; it now calls the same engine instead of carrying a second copy of the
rules.

### Change mode never blocks on somebody else's debt

`--mode change` evaluates a row only when the change edits a test the row
declares, edits a source file the row claims, or edits the row itself.
A project that already carries a long tail of `❌ Missing` rows stays committable.
Use `--mode manifest` to see that tail; use `--mode release` to stop it shipping.

### What the engine proves, and what it does not

It proves a row is honest. A row that claims coverage cannot be satisfied by:

- an empty, dash, or placeholder test cell
- a path that does not exist
- a file that is empty, comments only, a config, or a bare directory
- evidence weaker than the row's own declared Test Type, so a unit test cannot
  be presented as a browser journey
- a path outside the project, an absolute path, a `..` escape, or an
  environment file

It does not prove a test is meaningful. Nothing automated can. The agent and the
reviewer still read intent, and the "What Counts As A Real Test" section above is
still the bar.

### Framework-agnostic by design

Nothing in the engine is keyed to a language or a test runner. A declared
`.dart`, `.py`, `.rb`, `.go`, `.kt`, `.feature`, or Maestro `.yaml` path is
validated exactly as strictly as a `.spec.ts`. A project does not have to adopt
anyone else's framework to be enforceable; it only has to name real files.

### Evidence that lives in the paired product

A SIMS API whose only human surface is a Ripple screen proves its journey in
Ripple's E2E suite. Say so in the row:

```text
`tests/Feature/API/RippleSignalsApiTest.php`; paired Ripple `tests/e2e/crm/workspace.spec.ts`
```

The engine records that as named external evidence and counts it in the report.
It does not demand a duplicate local E2E, and it does not go quiet: the local
half of the same cell must still exist.

### Named exceptions

A user-facing workflow may ship without permanent E2E only as a named exception.
Write it in the row, in full:

```text
Exception, reason: destructive workflow, approved by Hafiz on 2026-09-20
```

Both halves are required. The allowed reasons are fixed:
`missing credential`, `no safe representative data`, `destructive workflow`,
`tooling unavailable`, `external system unreliable`, `not user-facing`.
An unlisted reason fails the gate. A builder cannot approve their own exception.

### When there is no manifest

A project without `TESTING.md`, or with a `TESTING.md` that has no parseable
table, reports `UNAVAILABLE`. That is reported, never silently rendered as a
pass. `--mode change` still exits 0, so a project that has not adopted a manifest
is not blocked from committing. `--mode release` exits non-zero: there is nothing
to prove the release with.

A table needs a `Feature` column and a `Status` (or `State`) column to be read.

## Verification And QA

Run the project checks from `verify.md` and `qa.md`, then run the enforcement in
`change` mode. The shared guard
(`scripts/agent-checks/pre-commit-guard.sh`) already does this for you before
every commit, for Claude and Codex alike, so a separate per-tool hook is not the
source of truth.

## Commit And Review Bar

Before commit or PR review, answer these questions:

1. Which feature row in `TESTING.md` matches the change?
2. Is the status still accurate?
3. Which test proves the changed behavior?
4. Would that test fail if the old bug or risky behavior returned?
5. Which permanent E2E file covers every changed user workflow?
6. What human-journey evidence proves the user can complete the workflow?
7. If E2E/manual QA was not run, is the reason explicit and acceptable?
8. If coverage is partial or missing, is that explicitly reported with the next
   test to add?

If the answer to any question is unclear, do not call the work complete.

## Release And CI

The shared guard proves coverage honesty on the machine that makes the commit.
That is enough for a local gate and it is not enough for a release: a dirty
working tree, a stale branch, or an unresolved merge can make a local run say
things a clean checkout would not.

For a repository with GitHub CI, install
`docs/agent-playbooks/templates/product-test-coverage-ci.yml` into the product
repository as a separate reviewed change. It re-runs `change` and `release` mode
on a clean checkout against the pull request base.

Known gap: `sifu-tutor` has no `.github/workflows` directory, so today nothing
re-checks its coverage claims before merge. Until that template is installed
there, the honest statement for a `sifu-tutor` release is that coverage was
proved locally and not re-proved on a clean checkout.

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
