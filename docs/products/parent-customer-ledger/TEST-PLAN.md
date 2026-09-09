# Verification, QA, And Rollout Plan

## Evidence Standard

Green unit tests alone are insufficient. Acceptance requires source-level tests,
API contract/security tests, the real App -> SIMS -> Ripple journey, and an
independent verifier mapping each product rule to evidence.

## Golden Fixture Matrix

| Fixture | Required proof |
| --- | --- |
| No activity | Zero balances, empty state, no fabricated rows. |
| Single FIUU payment | One charge, one payment, correct timestamp/method/transaction ID. |
| Historical paid invoice | Null missing metadata with `historical_missing_fields`. |
| Bundled FIUU payment | One payment event and multiple allocations. |
| Partial confirmed receipt | One credit effect, remaining invoice balance is correct. |
| Multi-invoice bank receipt | One receipt event, allocations sum correctly. |
| Overpayment | Full payment counted once, negative closing balance/available credit. |
| Later credit application | Allocation changes, customer balance does not reduce twice. |
| Commitment fee | Linked charge/payment, net zero, one understandable mobile card. |
| Processed refund | `Refund credit`, correct negative delta, no false cash-transfer claim. |
| Approved SIMS adjustment | Invoice uses `amount_due`; breakdown does not double count. |
| Legacy Ripple note | Classified according to the launch-gate audit and counted at most once. |
| Rejected/voided/pending finance record | Excluded from finalized feed and balance. |
| Same-timestamp charge/payment | Deterministic order and running balance. |
| Page boundary | Stable cursor, no duplicate/missing event, correct running balance. |
| Ripple source failure | Stale complete result or 503; never partial 200. |

Each fixture includes amounts that would fail if status-based arithmetic,
per-invoice payment duplication, receipt/payment-record duplication, or credit
double counting returns.

## Ripple Tests

### Unit

- `resolveInvoicePayableBase`: `amount_due`, legacy deductions fallback, zero.
- Canonical identity and source-priority decision table.
- Bundled payment grouping by attempt/provider transaction.
- Receipt-backed payment-record exclusion.
- Orphan/legacy payment inclusion rule.
- Overpayment and credit-application balance semantics.
- Commitment fee compound/group behavior.
- Refund-credit behavior.
- Opening/running/closing balance, negative credit balance, deterministic sort.
- Date boundaries in `Asia/Kuala_Lumpur`.
- Serializer redaction allowlist.

### Route/Integration

- Valid EdDSA/RS256 test token.
- Bad signature, algorithm confusion, unknown `kid`, issuer, audience, scope,
  subject format, expired/future token, and excessive lifetime.
- No parent ID override.
- Invalid cursor/date/limit.
- Paired date enforcement and `range=all` mutual exclusion.
- Required-source timeout/failure does not return complete success.
- Staff route response compatibility after engine extraction.
- Query-count/performance guard for transaction volume.

## SIMS Tests

### Feature/Contract

- Existing parent Sanctum token obtains only its own statement.
- Unauthenticated/expired token follows the current app session contract.
- A malicious parent ID in query/header/body is ignored or rejected.
- Correct signed service claims and correlation ID are sent.
- Ripple v1 success maps exactly to the public DTO; extra internal fields drop.
- Unknown/breaking contract version fails safely.
- Complete response caches; incomplete/error response never overwrites cache.
- Fresh, stale-within-window, stale-expired, and no-cache cases.
- 422 validation and 503 safe error envelopes.
- Existing `get-invoices` and payment endpoints remain unchanged.

### Negative Security

- Cross-parent/BOLA attempts.
- Cache key isolation between parents and date ranges.
- Response/log redaction for staff notes, bank IDs, internal metadata, raw
  callbacks, and receipt proof URLs.
- Timeout and retry do not multiply load.

## Parent App Tests

### Unit/Component

- Strict response parsing and null historical fields.
- Positive due, negative available credit, and settled summaries.
- Debit/credit/informational cards.
- Completed payment metadata and allocation expansion.
- Grouped commitment-fee presentation.
- Loading, empty, search-empty, stale, offline, and unavailable states.
- Period change resets cursor; pagination appends without duplicates.
- Pending tab remains functional when statement fails.
- Payment success invalidates invoice and statement keys.
- Accessibility labels include type, amount, status, and balance.

### Permanent Mobile E2E

Extend the existing Invoice feature flow or add a dedicated stable Statement
flow. It must:

1. log in with seeded parent data;
2. open Invoice and confirm Pending still works;
3. open Statement;
4. assert the balance summary and at least one debit and completed payment;
5. expand a payment and verify method, timestamp, transaction/reference, and
   allocation;
6. change the period;
7. verify the explicit empty or populated state;
8. exercise pull-to-refresh;
9. prove the 503 state does not disable Pending, using controlled fixture/mock
   support rather than production failure.

## Cross-System Contract Test

Use generated non-production signing keys and seeded/sanitized data. Drive an
HTTP call through SIMS and assert against the canonical Ripple fixture. The test
must prove:

- identity travels only from authenticated SIMS context to signed subject;
- contract version and decimal strings survive mapping;
- one payment remains one event across both services;
- running balance is not recalculated by SIMS;
- forbidden internal fields do not cross the boundary.

## Read-Only Production-Safe Smoke

After approved deploy, use dedicated safe parent accounts representing the
fixture classes where available. Do not create payments, modify allocations, or
repair records during smoke.

Check:

- authenticated own-account response;
- no cross-parent route/path parameter exists;
- default and custom date ranges;
- one known FIUU payment and one historical sparse payment;
- response freshness, latency, correlation ID, and logs;
- app Statement render and Pending independence.

## Shadow Comparison

Sample parents from these cohorts: FIUU single, FIUU bundled, bank receipt,
partial receipt, overpayment, credit application, commitment fee, refund,
legacy metadata gap, and no activity.

Compare canonical events to source facts and the staff view. Do not require the
new engine to preserve known legacy mistakes such as excluding a reconciled
receipt from running balance. Every difference must be classified as:

- expected correction;
- parent-field redaction/grouping;
- historical missing source data; or
- unexplained blocker.

Launch requires zero unexplained balance differences.

## Performance And Observability

Record:

- P50/P95/P99 latency by SIMS and Ripple hop;
- source query latency/failure;
- response/event count;
- dedupe exclusions by reason;
- stale-cache responses and age;
- 401/403/422/503 rates;
- balance invariant failures;
- app query failure and crash-free sessions.

Alert immediately on balance invariant failure or cross-parent authorization
failure. Logs must use request IDs and stable internal identifiers without raw
payment payloads or unnecessary parent PII.

## Rollout Gates

| Gate | Pass condition |
| --- | --- |
| Documentation | All readiness items answered; legacy notes classified. |
| Ripple | Golden, compatibility, security, type, lint/build tests pass. |
| SIMS | Feature/contract/security tests pass; cache failure semantics proven. |
| App | Unit/component and permanent mobile E2E pass. |
| Integration | App -> SIMS -> Ripple seeded journey passes. |
| Shadow | Zero unexplained balances or duplicate physical payments. |
| Cohort | Metrics healthy for agreed window; no finance/support regression. |
| General release | Independent review accepted; rollback tested; monitoring active. |

## Stop Conditions

Stop rollout if any of these occurs:

- one physical payment appears more than once;
- the balance invariant fails;
- parent ownership can be bypassed or cache data crosses parents;
- a required source fails while API returns a normal complete success;
- legacy adjustments produce unexplained differences;
- parent-charged and merchant fees are confused;
- Statement failure blocks Pending/payment behavior;
- permanent E2E or independent verification is absent.
