# Parent App UX Specification

## Navigation Decision

The existing Invoice screen keeps two tabs:

```text
[ Pending ] [ Statement ]
```

`Pending` continues using `GET /api/parent/get-invoices` and all existing pay,
pay-all, commitment-fee, older-invoice gating, and invoice-detail behavior.
`Statement` replaces the simplified Receipt feed and uses the new statement
endpoint. This avoids showing the same paid invoice in both Paid and Statement.

## Statement Screen Structure

1. Existing Invoice header and two-tab control.
2. Balance summary card:
   - Amount due when closing balance is positive.
   - Available credit when closing balance is negative.
   - `RM 0.00 - Account settled` when zero.
3. Date-range control: 1M, 3M, 6M, 12M, All; custom range behind `Custom`.
4. Optional search across visible description, invoice, receipt, provider
   transaction ID, student, and subject.
5. Chronological feed, newest first.
6. Pull-to-refresh and cursor-based `Load more`/infinite loading.

## Transaction Card

Collapsed card shows:

- type icon and parent-friendly title;
- date and time when precision is `second`, otherwise date only;
- primary reference such as invoice, receipt, or FIUU transaction ID;
- debit or credit amount with accessible label, not color alone;
- running balance after that event;
- `Completed` badge for payments;
- `Details unavailable for older record` only when the gap matters.

Expanded card or bottom sheet shows:

- payment method;
- real payment date/time;
- FIUU/provider transaction ID;
- receipt number when different from invoice number;
- gross, parent-charged fee, tax, and net amounts when present;
- invoice allocations with invoice, student, subject, and amount;
- unallocated amount/available credit;
- approved invoice adjustment breakdown;
- a short explanation when an event is informational and does not change the
  total balance.

Never show internal source-system labels (`SIMS`, `Neon`, database IDs), staff
notes, bank reconciliation IDs, or raw status codes.

## Grouped Events

### Bundled Payment

Render one payment card. Expanded content lists all invoice allocations. Do not
render one FIUU payment card per invoice.

### Commitment Fee

Render one `Commitment fee paid` card linked by `group_id`, with a note that the
fee charge and payment balance each other. The API retains the two effects so
the arithmetic remains auditable.

### Overpayment And Credit

The payment card shows the full amount received and the unallocated remainder.
The summary shows available credit. A later credit application can appear in
the affected invoice's details but should not look like a second payment.

### Refund

Label as `Refund credit` and explain `Credited to your account` unless the API
provides a future cash-transfer event type.

## States

| State | User experience |
| --- | --- |
| Initial loading | Balance and transaction skeletons matching final layout. |
| Pull refresh | Keep existing content visible with refresh indicator. |
| Empty | `No statement activity for this period` and an action to change the date range. |
| Search empty | `No matching statement records`; keep filter controls. |
| Stale success | Non-blocking banner: `Showing your latest available statement as of <time>. Pull to refresh later.` |
| 503 | Error card: `Your statement is temporarily unavailable. Your pending invoices and payment options are still available.` Retry button. |
| Offline with cache | Show app-cached response with offline wording; never label it live. |
| Historical gap | Omit empty rows; use `Not available for this older payment` for a specifically requested field. |

The Statement error state must not replace or disable the Pending tab.

## Amount And Status Language

- Debit: `Charge` / `Amount charged`.
- Credit from payment: `Payment` / `Amount paid`.
- Credit from refund: `Refund credit`.
- Positive closing balance: `Amount due`.
- Negative closing balance: `Available credit`.
- Payment status: `Completed`.
- Invoice status may be `Paid` or `Outstanding`; it is separate from posting
  status and must not be used to decide balance arithmetic.

## Accessibility And Locale

- Money: Malaysian Ringgit with two decimal places.
- Date/time: parent locale, sourced from `Asia/Kuala_Lumpur` timestamps.
- Every icon and color has a text label.
- Expand controls have accessible state and target size.
- Dynamic type supports wrapping references and allocation rows.
- Screen readers announce `Payment, credit RM 600, completed, balance RM 120`.

## App Data Behavior

- Add `Endpoints.Invoice.STATEMENT`.
- Use the existing authenticated `apiClient` and `useAppQuery`; no second host or
  direct Ripple client.
- Query key includes parent, period, cursor, and contract version.
- Recommended stale time: two minutes.
- Changing period resets cursor and list while retaining previous content until
  the replacement succeeds.
- On focus, refetch only according to the existing stale-aware pattern.
- Payment success invalidates both invoice and statement query keys.
- Client displays server-provided running balance; it never recalculates ledger
  arithmetic or deduplicates events.

## Existing Components

Likely reuse/adapt:

- `Screens/Invoice/index.tsx`
- `Components/CustomTabView`
- `Components/SearchBar`
- `Components/ErrorState`
- invoice skeleton visual patterns
- `hooks/useAppQuery.ts`

New components should have statement-specific names rather than changing
`ReceiptCard` semantics in place. Existing paid invoice detail and downloadable
receipt behavior remain reachable only where still used elsewhere; deleting or
consolidating them is out of scope.

## V1 Exclusions

- PDF/CSV export.
- Uploaded receipt-proof viewing.
- Dispute or support-ticket action from a ledger row.
- Parent-entered notes.
- Push notifications for new ledger entries.
- A separate legal/tax statement certification.
