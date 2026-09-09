# Parent Customer Ledger

Status: Build-Ready Pack, Phase A design only

Prepared: 17 July 2026

Projects: `ripple-suite`, `sifu-tutor`, `sifututor_parent`

## Outcome

The parent app will call one authenticated SIMS endpoint. SIMS will confirm the
logged-in parent and call a private Ripple endpoint. Ripple will produce the
canonical ledger projection from SIMS billing data and Ripple receipt, credit,
and reconciliation data.

```text
Parent app
  -> SIMS parent API (public front door and ownership check)
      -> Ripple internal API (private ledger projection)
          -> SIMS invoice/payment facts + Ripple receipt/credit facts
      <- parent-safe statement
  <- one stable mobile response
```

The app must never call Ripple directly and must never merge SIMS and Ripple
records itself.

## Why This Is The Recommended Design

- SIMS already authenticates the parent and owns the mobile API contract.
- Ripple already contains the richer customer-ledger interpretation.
- One canonical projection prevents the staff ledger and parent ledger from
  calculating payment history differently.
- Ripple remains private; staff notes, reconciliation evidence, and finance
  operations are not exposed to mobile clients.
- SIMS can protect the app from Ripple downtime with an explicit stale-cache or
  unavailable response instead of silently returning an incomplete statement.

## Key Accounting Model

- Positive `balance_delta` means the parent owes more.
- Negative `balance_delta` means the parent owes less or has more credit.
- `closing_balance = opening_balance + sum(balance_delta)`.
- One physical payment is one ledger event. Its invoice allocations are child
  details, not additional payments.
- Status is display information. Balance effect is controlled only by the
  explicit `affects_balance` and `balance_delta` fields.
- SIMS `amount_due` is the authoritative invoice payable amount.
- Receipt-backed Ripple payment records are mirrors and must not be counted
  again.
- A processed SIMS refund is shown as a refund credit unless there is separate
  evidence that cash was actually returned to the parent.

## Delivery Order

1. Ripple: characterize the current staff ledger, extract and correct a shared
   canonical projection engine, then expose a signed internal read endpoint.
2. SIMS: add the parent-facing façade, ownership enforcement, internal token
   signing, response mapping, caching policy, and error handling.
3. Parent app: replace the simplified Receipt feed with a Statement view while
   leaving the Pending/payment workflow unchanged.
4. Cross-system QA: prove balance, deduplication, authorization, historical
   gaps, stale-data behavior, and the real mobile journey.
5. Controlled rollout: deploy disabled, shadow compare, enable by cohort, and
   retain independent rollback flags at all three layers.

## Documents

- [Decision log](./DECISIONS.md)
- [Product requirements](./PRD.md)
- [UX specification](./UX-SPEC.md)
- [API and security contract](./BACKEND-CONTRACT.md)
- [Implementation plan](./IMPLEMENTATION-PLAN.md)
- [Verification and rollout plan](./TEST-PLAN.md)
- [Build prompts](./BUILD-PROMPTS.md)
- [Readiness checklist](./READINESS-CHECKLIST.md)

## Current Evidence

Read-only aggregate checks performed in July 2026 showed approximately 48,500
paid SIMS invoices, while substantially fewer historical rows contain payment
method or gateway identifiers. Newer `parent_payment_attempts` have much better
FIUU metadata. Ripple has separate customer receipts, payment records, credits,
and gateway transactions. Therefore the API must return missing historical
fields as `null` with a data-quality marker; it must never guess.

## Approval Boundary

This package authorizes no code, finance-data mutation, migration, deployment,
or credential change. Implementation starts only after Hafiz approves the
recommended decisions in `DECISIONS.md`. Each project then uses its own issue,
branch, tests, review, and release process.
