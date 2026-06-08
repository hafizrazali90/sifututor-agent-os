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

