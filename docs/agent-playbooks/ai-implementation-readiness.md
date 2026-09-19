# AI Implementation Readiness Playbook

Use this before coding any non-trivial feature, critical-lane change, or handoff
to Claude, Codex, another AI agent, or a human developer.

The goal is simple: a plan is not implementation-ready just because it explains
the idea. It is implementation-ready only when another agent can build it
without weakening the business rule, guessing the entry point, or proving only a
nearby happy path.

## When Required

This playbook is required for:

- payments, invoices, billing, commissions, auth, migrations, deployment, and
  mobile API contracts;
- cross-module workflows;
- staff, parent, tutor, or admin workflows that need permanent regression
  coverage;
- any task where Hafiz plans to hand work from one AI agent to another.

For small copy/config changes, use the normal task route instead.

## Readiness Gate

Before coding starts, the PRD, test plan, and build prompt must answer every
item below. If any answer is missing, the first build prompt is not "code"; it is
"close the documentation gap."

Plain meaning:

```text
Do not let an agent start coding from a weak brief.
If the agent cannot explain the build clearly in English, the task is not ready
to build yet.
```

This is not meant to slow down every small change. It is meant to prevent the
expensive mistake where an agent guesses the wrong entry point, edits the
nearby file, writes tests for a softer behavior, and produces something that
looks complete but does not match the real workflow.

## Conversational Readiness Levels

Do not make Hafiz remember numeric levels. Use natural language.

| Say this | Use when | What must be clear before coding |
| --- | --- | --- |
| `This only needs a Quick Brief.` | Tiny docs/copy/config change, obvious one-file fix, or low-risk tool update. | What changes, what does not change, and how it will be checked. |
| `This needs Product Shape first.` | Real bugfix, feature slice, user-facing behavior, staff workflow, multiple files, or unclear implementation options. | Problem, user/role, real entry point, business rule, scope, risks, evidence plan, and stop point. |
| `This needs a Build-Ready Pack before implementation.` | Critical lane, cross-module workflow, new module, mobile/API contract, payment/invoice/commission/auth/migration/deploy work, or handoff to another builder. | Full workflow, state transitions, contracts, edge cases, rollback, tests, human-journey proof, and build handoff package. |

The agent recommends the lightest safe version. Hafiz can ask for more detail
or less ceremony, but risk can force a deeper brief.

## Build-Ready Pack

For real implementation work, the agent should be able to explain this before
editing:

```text
Current understanding:
What problem are we solving, and who is affected?

Recommendation:
What approach should we take, and why?

What I will change:
The behavior, files, modules, routes, screens, or services likely affected.

What I will not change:
Explicit out-of-scope areas, so the work does not quietly grow.

Real entry point:
Where the behavior actually starts: route, screen, controller, API call, job,
command, webhook, or mobile app call site.

Business rule:
The exact rule the code must satisfy.

State change:
What exists before, what changes after, and what must stay compatible.

Edge cases:
Duplicate click, retry, abandoned flow, expired flow, wrong role, missing data,
stale state, mismatch, or external payload quirks.

Evidence plan:
Which tests, browser/mobile/API checks, screenshots, smoke checks, or read-only
production-safe checks will prove the real behavior.

Stop point:
Where this task is intended to end: local fix, commit, push, PR, staging
verified, production live, or production monitored.
```

Plain meaning for Hafiz:

```text
You should understand the intended code behavior as if the code was translated
into normal English before the agent builds it.
```

If the agent cannot fill this in honestly, the next action is to investigate or
clarify, not code.

| Area | Required answer |
|---|---|
| Real entry point | Which route, controller, command, job, service, screen, app call site, or webhook starts the behavior? |
| Contract moment | At what exact moment does the system commit to the user/gateway/staff action? |
| State before and after | What fields/statuses/rows must exist before the action, and what must change after it? |
| Shared source of truth | Which one helper/service owns the business rule? Which other paths must call it? |
| External payload shape | What realistic third-party/mobile/browser payload must be accepted, including naming/currency/status quirks? |
| Idempotency and retry | What happens when the same request, callback, command, or button click happens twice? |
| Expiry/abandonment | What happens when a user starts but does not finish the flow? |
| Mismatch path | What happens when saved state and current state no longer match? |
| RBAC and ownership | Which role/user can see, trigger, resolve, or override the state? |
| Audit evidence | What is logged, what raw/sanitized payload is stored, and what must never be stored? |
| Backward compatibility | What existing app/API fields must remain accepted and unchanged? |
| Feature flag/rollback | How can the behavior be disabled or safely rolled back without data corruption? |
| Test proof | Which unit/feature/API/E2E tests prove the exact rule, including negative cases? |
| Human-journey proof | Which browser/mobile/API smoke or E2E proves the user workflow, or why is it not feasible? |
| Verifier acceptance | What must Codex/reviewer check before the slice can be marked accepted? |

## Proof-Bounded Builder Packets

Use the [Builder Completion Proof Contract](agent-os-evidence-model.md#builder-completion-proof-contract)
for delegated, cross-system, cross-module and user-facing work. The evidence
model owns the acceptance dimensions and optional machine receipt; do not
create provider-specific definitions of completion.

Before dispatch, bind one packet to one complete vertical slice, its approved
contract, target revision, normal entrypoint, real callers, state transition
and negative/failure/retry proof. Name bypass paths and the source of truth.
Keep explicit exclusions and an accountable integrator. A tiny safe edit may
use a brief, but must not claim a stronger state than its evidence supports.

The receiving builder checks current code against the brief before editing.
If a new finding changes the contract, record it and route it through the
existing scope/approval rules instead of silently changing acceptance criteria.
Ordinary in-scope fixes and retries continue without another routine approval.

When an independent reviewer returns a slice, correct and recheck that slice
before dependent execution. Parallel discovery for genuinely independent slices
is allowed. Builder completion, independent technical acceptance, owner product
acceptance and release authorization remain separate states.

## Anti-Weak-Test Rule

Tests must prove the specific production rule, not a softer nearby behavior.

Examples:

- If the requirement says "create payment snapshot when parent starts payment,"
  a test that creates the snapshot inside final verification is not enough.
- If the requirement says "validate FIUU callback currency," tests must include
  the production-shaped value FIUU sends, not only the internal normalized value.
- If the requirement says "amount after deductions," tests must include a
  deduction fixture.
- If the requirement says "retry abandoned attempt," tests must start the same
  payment twice and cover expiry.
- If the requirement says "audit raw callback safely," tests must assert the
  sanitized stored payload and masked sensitive fields.

## Build Prompt Standard

Every implementation prompt for this class of work must include:

1. Purpose in plain language.
2. Exact pre-read files.
3. Real entry points and call sites.
4. Business requirements.
5. State transition table or bullet list.
6. Backward compatibility contract.
7. Explicit out-of-scope list.
8. Files likely to change.
9. Tests-first list with negative and production-shaped cases.
10. Required verification commands.
11. E2E/human-journey evidence requirement or accepted exception.
12. Stop conditions.
13. Final report format that maps each acceptance item to evidence.

## Build Handoff Package

When work moves from planning to another AI agent or human builder, include a
compact handoff package:

- main goal and accepted scope
- current evidence and files already read
- exact pre-read files
- real entry points and call sites
- business rules and state transitions
- out-of-scope list
- likely files to change
- tests to add or update, including negative and production-shaped cases
- human-journey evidence requirement
- stop conditions and approval boundaries
- final report format that maps requirements to evidence

The receiver should not need to rediscover the starting point. They should
still verify current files before editing, because stale context is only a lead.

## Slice Acceptance Standard

A slice is not accepted when the implementer says "tests green." It is accepted
only when an independent verifier confirms:

- the implementation satisfies the exact acceptance wording;
- the tests would fail if the implementation used the weaker mistaken behavior;
- focused tests pass;
- build/type checks pass when relevant;
- broad-suite failures, if any, are classified as baseline or task-caused;
- mobile/API compatibility is safe or explicitly blocked;
- no forbidden files, secrets, production data, or out-of-scope modules were
  touched;
- all open risks are named before moving to the next slice.

If an independent verifier finds a gap, the task state must not mark that slice
as accepted. Use "implemented by builder, verifier needs fix" or equivalent
wording until the gap is corrected.
