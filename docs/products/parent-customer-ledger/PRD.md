# Product Requirements

## Problem

The parent app currently shows pending invoices and a simplified receipt feed
made from SIMS paid invoices, commitment fees, and refunds. Ripple's staff
Customer Ledger contains a richer view of receipts, partial payments, advances,
credits, and allocations. A parent cannot currently see one trustworthy running
account that explains what was charged, what was paid, and what remains.

## Product Goal

A logged-in parent can open Invoice -> Statement and understand their full
account history and current balance without knowing whether a record originated
in SIMS, FIUU, a bank receipt, or Ripple.

## Users And Roles

- Parent: may read only their own statement.
- SIMS: authenticates the parent and is the public API boundary.
- Ripple: privately calculates the canonical projection.
- Finance staff: continue using Ripple's richer staff ledger and internal
  evidence; this feature does not reduce staff permissions or functionality.

## Functional Requirements

### Statement Contents

The statement must support finalized, parent-visible entries for:

- invoice charges using SIMS `amount_due`;
- completed FIUU payments;
- confirmed customer receipts, including partial and multi-invoice receipts;
- standalone valid legacy payments that are not mirrors of a receipt;
- commitment-fee charge and payment pairs;
- refund credits;
- customer credit originating from an overpayment;
- credit applications as non-balance-changing allocation details when the
  source payment was already represented;
- audited legacy adjustments only when not already reflected in SIMS.

### Required Payment Fields

For every completed payment, return:

- real payment timestamp when available;
- date-only value and precision marker when only a date is known;
- payment method code and parent-friendly label;
- FIUU/provider transaction ID when available;
- receipt number when distinct from invoice number;
- customer-charged tax and fee amounts, defaulting to `null` when unknown;
- completed payment status;
- gross payment amount and allocations to invoices.

Historical missing values must be `null`. The API must never infer FIUU IDs,
methods, timestamps, tax, fees, or receipts from unrelated rows.

### Balance Rules

1. Charge entries have positive `balance_delta`.
2. Payment, refund-credit, and genuine credit entries have negative
   `balance_delta`.
3. Informational allocation entries have zero `balance_delta`.
4. `closing_balance = opening_balance + sum(balance_delta)`.
5. `outstanding_balance = max(0, closing_balance)`.
6. `available_credit = max(0, -closing_balance)`.
7. Every row carries `affects_balance`; clients must not derive it from status.
8. The server computes running balances oldest-first, even when returning rows
   newest-first.
9. Equal-time events sort deterministically: charge before its payment, then by
   stable source key.

### Deduplication And Allocation Rules

- One physical payment appears once.
- A bundled FIUU transaction covering multiple invoices is one payment with
  multiple allocations.
- A confirmed customer receipt is the primary Ripple money-received object.
- A `payment_record` linked to that receipt is a compatibility mirror and is
  excluded.
- An overpayment reduces the customer balance once at receipt time. Creating or
  applying the resulting credit does not reduce the customer balance again.
- A legacy/orphan credit without a represented source may affect the balance
  once and must be labelled `legacy_derived`.
- `invoice_payment_status` is a derived cache and cannot be used as primary
  evidence for money received.

### Commitment Fee Rule

The canonical ledger preserves a linked charge and payment, normally netting to
zero. The mobile UI may render the pair as one grouped `Commitment fee paid`
card, but the API must retain both accounting effects or an equivalent compound
event. Invoice payable values remain based on SIMS `amount_due`.

### Refund Rule

A processed SIMS refund currently means value credited back to the parent
account. Display `Refund credit` with negative balance effect. A future actual
cash transfer must be a separate event type with transfer evidence and must not
be assumed by this release.

### Filtering And Pagination

- Filters: 1, 3, 6, 12 months, paired custom `from`/`to`, and all history via
  `range=all`.
- Dates are inclusive in `Asia/Kuala_Lumpur`.
- No period parameters means the previous 12 months through today.
- `from` and `to` must be supplied together; `range=all` is mutually exclusive.
- Cursor pagination; default 50 rows, allowed 20-100.
- Response order defaults to newest-first.
- Opening balance includes all finalized balance effects before `from`.

### Parent-Safe Presentation

The response may include parent-friendly descriptions, invoice/receipt/provider
references, student/subject context, allocations, and data-quality notices. It
must not include staff names or IDs, internal notes, bank transaction IDs,
reconciliation scores, raw callback data, internal proof URLs, or approval audit
trails.

## Availability Requirements

- SIMS must never silently replace the canonical response with a SIMS-only
  subset.
- Fresh successful responses may be cached for normal performance.
- If Ripple fails, SIMS may serve a last-known-good complete response up to 15
  minutes old with `is_stale=true`, `as_of`, and a user-safe notice.
- If no acceptable complete cache exists, return 503 with
  `STATEMENT_TEMPORARILY_UNAVAILABLE`.
- Pending invoices and payment actions remain usable when Statement is down.

## Non-Functional Requirements

- Parent ownership is enforced in SIMS and re-bound in the signed Ripple token.
- No parent ID supplied by the app is trusted as authorization.
- End-to-end request/correlation ID propagation.
- P95 server response target: under 1.5 seconds for the default range after
  warm-up; hard timeout budget documented per hop.
- No N+1 query per transaction.
- Money uses decimal strings with two fractional digits; never floating-point
  JSON numbers for contract amounts.
- Logs contain identifiers needed for support but no raw payment payload or
  unnecessary PII.

## Success Measures

- Zero known duplicate physical payments in launch fixtures and shadow samples.
- Balance invariant passes for every response.
- 100% of parent API authorization tests reject cross-parent access.
- Parent can find payment date, method, FIUU ID, receipt number, fees/tax, and
  completed status when the source genuinely contains them.
- Historical missing metadata is clearly absent rather than misleading.
- Statement error never blocks the Pending invoice/payment workflow.

## Acceptance Stories

1. A parent with one paid FIUU invoice sees one charge and one completed payment
   with the correct FIUU transaction ID and resulting balance.
2. A bundled FIUU payment for three invoices appears once with three allocations.
3. A partial confirmed receipt lowers the balance once and shows the allocated
   and unallocated amounts.
4. An overpayment creates available credit without a second balance reduction.
5. Applying existing credit to another invoice changes allocation coverage but
   not the customer's total balance again.
6. A commitment fee reads naturally in the app while preserving its charge and
   payment accounting.
7. A processed refund is labelled as credit unless outbound-transfer evidence
   exists.
8. A parent cannot request or infer another parent's statement.
9. Ripple downtime produces an explicit stale response or 503, never an
   incomplete success.
