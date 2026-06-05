# Agent OS Routing Model

Status: draft for review.

This document defines how the Sifututor Agent OS should classify Hafiz's prompt
before choosing discussion, planning, implementation, verification, QA, review,
commit, push, save-session, or critical-lane behavior.

The purpose is to avoid two bad extremes:

- too heavy: discussion triggers implementation or commit machinery
- too loose: risky work skips diagnosis, approval, evidence, or review

## Source Inputs

Route classification should use these signals in order:

1. Explicit tool or skill request, such as `$verify` or `$commit`.
2. Hafiz's last approved/recommended step in the current conversation.
3. Current repo state, such as dirty files, staged files, branch, active task,
   and whether work is already committed or pushed.
4. Risk words and protected domains: auth, payments, invoices, commissions,
   migrations, deploys, mobile API contracts, secrets, `.env*`, and `live/`.
5. Intent words: discuss, plan, fix, verify, QA, review, commit, push, save.
6. Context authority: whether the prompt is verified, trusted, reported,
   historical, or unverified.

Do not route by keyword alone.

## Routing Priority

Use this order when signals conflict:

| Priority | Route | Why |
| --- | --- | --- |
| 1 | blocked boundary | secrets, `.env*`, and `live/` protection override all other intent |
| 2 | critical lane diagnosis | high-risk domains require diagnosis first |
| 3 | explicit skill request | Hafiz named a tool/workflow directly |
| 4 | save/handoff/snapshot | preserves context before it is lost |
| 5 | push/deploy/merge/PR review | outbound actions need risk check and explicit approval |
| 6 | commit | local history mutation needs exact file list and approval |
| 7 | verify/QA/review/diagnose | evidence and analysis routes |
| 8 | product design/planning | PRD, UX, architecture, or workflow design |
| 9 | implementation/task-router | non-trivial safe work |
| 10 | discussion/light mode | learning, architecture discussion, retrospective, naming, options |

Plain meaning: when risk is high, route to safety first. When the prompt is
thinking-oriented, stay light.

## Prompt Categories

| Prompt type | Examples | Expected route | Expected behavior |
| --- | --- | --- | --- |
| discussion | `why are we doing this?`, `can we discuss architecture?`, `what mistakes did we make?` | discussion/light mode | Think with Hafiz. Do not edit unless asked to document. |
| architecture planning | `plan it properly`, `map what Agent OS should have` | planning/product-design or docs | Keep a living draft, map assets/gaps/touched files, ask or recommend next topic. |
| proceed | `proceed`, `ok proceed`, `proceed next` | last clear recommended step | Act immediately if clear and safe; ask only if ambiguous/risky. |
| approve | `approve` | last explicit approval request | Execute the approved action or bundle exactly. |
| what next | `what next`, `next?` | recommendation | Give one next action, not a vague list. |
| commit | `commit this`, `prepare commit` | commit | Guard, inspect diff/status, require exact file-list approval. |
| bundled commit+push | `approve` after agent asks `approve commit+push?` | commit+push bundle | Commit and push exactly; report final status. |
| push/PR/merge | `push this`, `open PR`, `merge` | review first | Risk review, inventory status, explicit approval. |
| deploy/release | `deploy this`, `release to prod` | review/critical release gate | Strong evidence, explicit approval, no bundling by default. |
| save session | `save session`, `wrap up` | save-session | Preserve durable state and lessons. |
| bug/diagnosis | `why is this failing?`, `debug this` | diagnose | Read-only diagnosis before edits unless safe/simple. |
| critical domain | `fix payment`, `auth migration`, `mobile API contract` | critical lane diagnosis | Phase A diagnosis, then wait for approval. |
| forbidden path | `open .env`, `patch live/` | blocked | Refuse and explain boundary. |

## Short Command Rules

Short commands depend on the last clear recommendation.

| Command | Rule |
| --- | --- |
| `proceed` | Act on the last recommended step if it is clear and safe. |
| `approve` | Execute the last exact approval request, including a bundle if the bundle was explicitly named. |
| `ok` | Treat as acknowledgement unless the previous message asked for a clear approval. |
| `next` | Recommend one next action. |

If the last recommendation was "review routing model next," `proceed next`
means start that review. If the last request was "approve commit+push for these
files," `approve` means commit and push.

## Conversation-State Fixture Check

Run this local fixture runner when changing short-command behavior:

```bash
scripts/agent-checks/agent-os-conversation-fixture-runner.py
```

It checks short replies against visible prior assistant context. Plain meaning:
`approve` follows the last exact approval request, `proceed` follows the last
clear safe recommendation, `what next` returns one next action, and missing
previous context should trigger clarification instead of guessing.

Decision: for now, this uses visible chat context only. Do not add hidden
lifecycle-hook or session-file state for last recommended step yet. Add stored
state later only if repeated failures show chat context is not enough.

## Bundled Approval Routing

Bundled approvals are allowed only when the agent asks clearly and the scope is
exact.

Decision: for now, bundled approval context also uses visible chat context
only. The immediately previous approval request must clearly name the exact
bundle. Do not add hidden pending-approval session state yet. Add stored state
later only if repeated failures show chat context is not enough.

Allowed bundles:

- stage + commit
- commit + push
- create issue + document plan
- docs edit + checks
- verify + QA
- commit + close issue
- push + close issue

Never bundle by default:

- deploy + smoke + close issue
- migration + deploy
- payment/auth/invoice/commission/mobile API changes + commit
- production log access + fix + deploy
- destructive cleanup
- secrets or `.env*`
- changes under `live/`

## Living Draft Rule

For architecture and workflow design, keep a living draft updated while
discussing. Hafiz should not need to repeat decisions already made in the same
thread.

The agent should update the draft when:

- Hafiz states a preference
- Hafiz corrects the agent's plan
- a review layer decision is made
- a new gap or source-of-truth file is identified

## Router Implementation Guidance

The lifecycle hook may inject workflow skill hints, but it should stay
conservative:

- discussion and architecture prompts should avoid forced workflow skills
- short `proceed` should route through the last recommended step when state is
  available; if not available, use `$task-router`
- `approve` alone should not be guessed without prior approval context
- push/deploy/merge/PR words should trigger review unless clearly part of a
  previously approved safe bundle
- critical-domain words should trigger diagnosis-first behavior

The router can start as Markdown rules and eval cases. Only update code after
the model is reviewed.

## First Automated Eval Set

Decision: the first automated Agent OS tests should verify routing behavior,
not product behavior.

Initial cases:

- discussion must not trigger commit
- `proceed next` follows the last clear recommendation
- `approve` follows the last exact approval request
- bundled commit+push works only when explicitly asked
- deploy cannot be bundled by default
- payment/auth/invoice/mobile API prompts route to diagnosis first
- `.env*` and `live/` stay blocked

These tests protect how Codex/Claude behave with Hafiz. Product tests still
protect product behavior.

## Open Questions

- None for the first routing model draft.
