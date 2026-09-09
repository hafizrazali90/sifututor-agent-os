# Decision Log

## Recommended Decisions Used By This Plan

| Area | Decision | Reason |
| --- | --- | --- |
| Mobile integration | The parent app calls SIMS only. | SIMS already owns parent authentication and mobile contracts. |
| Ledger ownership | Ripple owns the canonical customer-ledger projection. | Ripple combines SIMS billing with receipts, credits, allocations, and reconciliation facts. |
| Public API | SIMS exposes `GET /api/parent/payment-statement`. | One secure, stable parent-facing API. |
| Ripple API | Ripple exposes a private signed-service endpoint only. | Avoids making the staff dashboard or its data public. |
| Shared calculation | Ripple staff and parent outputs use the same canonical projection engine with different serializers. | Prevents two balances for the same parent. |
| App navigation | Keep `Pending`; replace the current `Receipt` feed with `Statement`. | Avoids a third tab containing duplicate paid records. |
| Default range | Last 12 months; parent may choose 1, 3, 6, 12 months, custom, or all history. | Useful default while preserving full history. |
| Main feed | Show finalized parent-visible entries only. | Pending/rejected finance workflow is not a completed statement. |
| Historical gaps | Return unknown fields as `null`; show only useful parent-safe fields. | Old data is incomplete and must not be invented. |
| Refund wording | Use `Refund credit` unless actual outbound transfer evidence exists. | Current SIMS refund behavior reduces the parent's balance; it does not prove cash was returned. |
| Adjustments | Use SIMS `amount_due`; show approved adjustment breakdown inside the invoice detail. | Avoids counting old Ripple CN/DN separately from the adjusted invoice. |
| Fees | Expose only tax or fees charged to the parent. | Merchant settlement fees are internal company costs. |
| Availability | Serve last-known-good data for up to 15 minutes with a visible stale marker; otherwise return 503. | Never present a partial SIMS-only response as a complete ledger. |
| V1 exports | No PDF, CSV, or receipt-proof download. | The first release is a trustworthy in-app statement; exports can follow. |

## Hard Launch Gate

Before enabling parents, audit all approved legacy Ripple credit/debit notes.
For every note, prove one of the following:

1. it is already reflected in SIMS `amount_due`, so it must not become a
   separate balance event;
2. it is a genuine historical balance event not reflected in SIMS, so it must
   be migrated or represented once as `legacy_adjustment`; or
3. it is invalid/dormant and must remain excluded.

The feature must not launch while an affected parent could receive a different
balance depending on whether the old Ripple note is included.

## Decisions Hafiz Should Confirm Before Build

Approval of the plan should explicitly confirm these three points:

1. The app's current `Receipt` tab becomes `Statement`; `Pending` stays as-is.
2. V1 excludes exports and uploaded receipt files.
3. A 15-minute last-known-good window is acceptable when Ripple is temporarily
   unavailable.

Other values are implementation defaults and can be tuned without changing the
architecture.

## Out Of Scope

- Letting the mobile app authenticate directly with Ripple.
- Changing how parents pay invoices or commitment fees.
- Changing FIUU callback processing or reconciliation write workflows.
- Repairing production finance data as part of the read API.
- Exposing staff identities, notes, bank transaction IDs, reconciliation
  confidence, raw gateway payloads, or receipt proof URLs.
- Turning internal merchant fees into parent charges.
- Producing a legally certified tax invoice or bank statement.
