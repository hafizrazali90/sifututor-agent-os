# Build Readiness Checklist

## Current Understanding

- Problem: parents lack one trustworthy debit/credit account history.
- Affected role: authenticated parent; finance staff retain a richer staff view.
- Real start: parent opens Invoice -> Statement.
- Public boundary: SIMS parent API.
- Canonical calculation: Ripple shared projection engine.
- Stop point for this package: design complete, no implementation.

## Required Readiness Answers

| Area | Answer | Ready |
| --- | --- | --- |
| Real entry point | App Invoice screen -> SIMS `GET /api/parent/payment-statement` -> Ripple internal endpoint. | Yes |
| Contract moment | A row enters the statement only when its source is finalized and parent-visible; a complete projection is committed at response generation/cache write. | Yes |
| State before/after | V1 is read-only; no finance state changes. App gains a canonical view and cache only. | Yes |
| Shared source of truth | Ripple canonical projection owns ledger arithmetic; SIMS `amount_due` owns invoice payable value. | Yes |
| External payload | FIUU method/transaction/timestamp are mapped from real SIMS attempt/callback shapes; absent history stays null. | Yes |
| Idempotency/retry | GET-only; stable event IDs; one bounded connection retry; cache writes only complete projections. | Yes |
| Expiry/abandonment | Service token <=120 seconds; stale cache <=15 minutes; expired token/cache rejected. | Yes |
| Mismatch path | Incomplete source, bad contract, balance failure, or legacy ambiguity cannot return normal success. | Yes |
| RBAC/ownership | SIMS authenticated parent becomes signed subject; app supplies no trusted parent ID. | Yes |
| Audit evidence | Correlation ID, metrics, source/error categories; no raw gateway payload, notes, or unnecessary PII. | Yes |
| Backward compatibility | Existing `get-invoices`, payment flows, app bearer auth, and staff API shape remain. | Yes |
| Feature flag/rollback | Independent Ripple, SIMS, and app flags; read-only rollback. | Yes |
| Test proof | Golden source fixtures, security/contract tests, app unit/component, cross-system test. | Yes |
| Human journey | Permanent Maestro flow plus staged read-only mobile smoke. | Yes |
| Verifier acceptance | Independent rule-to-evidence review and zero unexplained balance differences. | Yes |

## Pre-Build Approval Items

- [ ] Hafiz approves replacing Receipt with Statement while retaining Pending.
- [ ] Hafiz approves V1 without PDF/CSV or receipt-proof download.
- [ ] Hafiz approves the 15-minute last-known-good fallback window.
- [ ] Legacy Ripple CN/DN audit is complete and every approved note classified.
- [ ] Contract v1 examples are validated against current model/schema names.
- [ ] Asymmetric algorithm support is confirmed in deployed PHP and Node.
- [ ] Clean project issues/branches/worktrees exist; unrelated active work is not
      mixed into this feature.

## Before Each Slice Is Accepted

- [ ] Exact business wording is proven, not a weaker nearby behavior.
- [ ] Focused tests would fail if payment duplication or balance double counting
      returned.
- [ ] Type/build/lint/static checks pass as applicable.
- [ ] Broad failures are classified as baseline or task-caused.
- [ ] No `.env*`, secrets, `live/`, production writes, or unrelated files were
      touched.
- [ ] Permanent E2E coverage is named for every changed user workflow.
- [ ] Independent verifier maps acceptance items to evidence.
- [ ] Human review occurs before payment/auth/mobile-contract commit and deploy.

## Known Risks And Controls

| Risk | Control |
| --- | --- |
| Duplicate FIUU payment per invoice | Group by payment attempt/provider transaction; allocations are children. |
| Receipt/payment-record mirror duplication | Canonical source priority and explicit exclusion test. |
| Reconciled status incorrectly excluded | Arithmetic uses explicit delta/effect, not display status. |
| Overpayment/credit double counting | Receipt carries full effect; source-linked applications carry zero effect. |
| Historical metadata gaps | Nullable fields and data-quality marker; never guess. |
| Legacy Ripple CN/DN drift | Mandatory pre-launch classification gate. |
| Cross-parent data leak | No app parent ID; signed subject; BOLA and cache-isolation tests. |
| Internal field exposure | Parent serializer plus SIMS allowlist DTO and forbidden-field tests. |
| Partial statement during outage | Complete-only cache; stale marker or 503. |
| App payment regression | Pending stays on existing API and is covered independently. |

## Readiness Verdict

The architecture and handoff package are implementation-ready after the seven
pre-build approval items above are satisfied. The three product preferences can
be approved together. The legacy CN/DN audit and runtime key-algorithm check are
evidence gates and cannot be waived silently.
