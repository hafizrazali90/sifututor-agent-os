# Build Handoff Prompts

Use these prompts only after the plan is approved and the target repository has
a clean issue/branch. Each builder must reread current project instructions and
verify the named files because paths may drift.

## Prompt 1 - Ripple Canonical Engine

```text
ripple-suite work - Build the canonical parent customer-ledger projection.

Purpose:
Create one accounting engine used by Ripple's staff Customer Ledger and the
future parent-safe internal endpoint. Fix semantic duplication/balance problems
without changing finance write workflows.

Pre-read:
- repository AGENTS.md and CLAUDE.md
- docs/products/parent-customer-ledger/{README,DECISIONS,PRD,BACKEND-CONTRACT,IMPLEMENTATION-PLAN,TEST-PLAN}.md
- src/app/api/accounts/[parentId]/statement/route.ts
- src/modules/accounts/lib/{statement,invoice-amount,sql-helpers}.ts
- src/modules/accounts/types/accounts.ts
- src/modules/reconciliation/lib/customer-receipts.ts
- docs/audits/2026-06-05-ripple-accounts-reconciliation-phase-a-audit.md

Real entry point:
GET /api/accounts/[parentId]/statement and its SIMS/Neon source queries.

Business rules:
- positive delta is debt; negative delta is payment/credit
- one physical payment is one event; allocations are children
- group bundled SIMS/FIUU attempts
- confirmed customer_receipts are primary; linked payment_records are mirrors
- amount_due is invoice authority, with documented legacy fallback
- receipt-origin credit applications have zero customer-level delta
- status never controls arithmetic; use affects_balance/balance_delta
- processed SIMS refund is refund credit
- invoice_payment_status is derived, not payment evidence
- preserve deterministic opening/running/closing balance invariant

Backward compatibility:
Preserve the existing staff statement response shape and permissions while
moving calculation to the shared engine.

Out of scope:
No public endpoint yet, no finance writes, no data repair/migration, no UI
redesign, no FIUU/reconciliation changes, no deployment.

Tests first:
Add golden fixtures for single and bundled FIUU, partial/multi-invoice receipt,
overpayment and later credit application, commitment fee, refund, adjusted
invoice, pending/rejected/voided records, legacy sparse data, same-time events,
and pagination boundary. Tests must fail under per-invoice payment duplication,
receipt/payment mirror duplication, status-based balance exclusion, or credit
double counting.

Likely changes:
Extract server-only source adapters, canonical types/engine, staff serializer,
and parent serializer under src/modules/accounts/server; adapt existing route.

Verification:
Run focused tests, full relevant Accounts/Reconciliation tests, typecheck, lint,
build, diff/security review, and staff response compatibility evidence.

Stop:
Stop before internal endpoint, commit, push, PR, deploy, or production data.
Report every acceptance rule with its test evidence and any legacy-data gap.
```

## Prompt 2 - Ripple Internal Endpoint

```text
ripple-suite work - Add the private v1 parent-ledger endpoint on the approved
canonical engine.

Pre-read the full Build-Ready Pack, src/proxy.ts, auth patterns, and the accepted
canonical engine. Implement GET /api/internal/v1/parent-ledger with a separate
deny-by-default internal auth branch, not PUBLIC_PREFIXES and not staff cookies.

Accept only a short-lived asymmetric SIMS JWT. Validate alg, kid, iss=sims,
aud=ripple-parent-ledger, sub=parent:<id>, scope=parent-ledger:read, iat/exp <=
120 seconds, jti, and request_id. Derive parent identity only from sub.

Return contract v1 parent-safe data plus projection_complete and source
freshness. Validate filters/range/cursor/limit, enforce GET-only/rate/timeouts, redact
all staff/reconciliation/raw fields, propagate correlation IDs, and add a
disabled-by-default flag.

Tests first include valid key rotation and every negative token case, identity
override, invalid filters, required-source failure, completeness, and forbidden
field assertions using production-shaped tokens/payloads.

Out of scope: SIMS/app changes, public exposure, finance writes, data repair,
deployment. Stop before commit/push/PR/deploy and report requirement-to-evidence.
```

## Prompt 3 - SIMS Parent Facade

```text
sifu-tutor work - Add the parent-owned payment-statement facade for Ripple.

Pre-read project instructions, TESTING.md if present, the full Build-Ready Pack,
routes/api.php, VerifyApiToken, current parent controller/resource patterns, and
the accepted Ripple v1 contract.

Real entry point:
GET /api/parent/payment-statement under existing VerifyApiToken middleware.

Derive parent from Auth::user; accept no parent authorization ID. Validate
from/to/range/cursor/limit. Sign a <=120-second asymmetric service JWT whose sub is
that parent, call Ripple with bounded timeout, require contract v1 and
projection_complete=true, and map through an explicit public allowlist DTO.

Cache only complete success. Serve last-known-good for no more than 15 minutes
with is_stale/as_of; otherwise return safe 503
STATEMENT_TEMPORARILY_UNAVAILABLE. Preserve existing responseCode/session
behavior and propagate request ID.

Tests first:
self-only/BOLA, signed claims, filter validation, field allowlist, version and
incomplete response rejection, fresh/stale/expired/no-cache cases, timeout/retry,
cache isolation, safe logs, and unchanged get-invoices/payment behavior.

Out of scope:
No get-invoices rewrite, payment/FIUU/refund/reconciliation write changes,
finance data writes, app changes, deployment, or secrets in repo.

Run focused feature/contract/security tests, relevant suite, formatting/static
analysis, permanent API regression decision, and independent review. Stop before
commit/push/PR/deploy and map acceptance to evidence.
```

## Prompt 4 - Parent App Statement

```text
sifututor_parent work - Replace Invoice's simplified Receipt feed with the
canonical Statement while keeping Pending/payment behavior unchanged.

Pre-read project instructions, TESTING.md if present, UX-SPEC, BACKEND-CONTRACT,
TEST-PLAN, Constant/Endpoints.ts, Screens/Invoice/index.tsx,
Components/Invoice/*, hooks/useAppQuery.ts, current invoice types/tests, and the
existing permanent Invoice Maestro flow.

Use only existing SIMS apiClient and bearer auth. Add strict v1 statement types
and Endpoints.Invoice.STATEMENT. Keep get-invoices for Pending. Load statement
only for the Statement tab, with query key for parent/period/cursor/version.

Render summary, date presets/custom range, search, newest-first cards, running
balance, completed payment metadata, grouped allocations/commitment fee,
historical nulls, pagination, loading/empty/stale/offline/503 states, and
accessibility from UX-SPEC. Never calculate balances/dedupe in the app.

Tests first:
positive/negative/zero summary, all transaction types, bundled allocation,
historical gaps, filters/pagination, stale/503, Pending independence, cache
invalidation after payment, accessibility. Add/extend permanent Maestro E2E for
the real Statement journey and update coverage/QA documentation.

Out of scope:
No direct Ripple client, payment-flow redesign, PDF/CSV/proof download, support
workflow, broad Invoice refactor, deployment.

Run unit/component tests, typecheck/lint, Android/iOS build checks as applicable,
focused permanent E2E, and visual/accessibility QA. Stop before commit/push/PR/
release and map acceptance to evidence.
```

## Prompt 5 - Independent Cross-System Verification

```text
Verify the Parent Customer Ledger across ripple-suite, sifu-tutor, and
sifututor_parent. Do not implement unless a failed acceptance item is separately
approved for correction.

Read the full Build-Ready Pack and all three accepted diffs. Map every PRD story
and API/security rule to concrete evidence. Run focused suites, contract flow,
permanent mobile E2E, build/type/lint checks, and adversarial review. Prove one
physical payment appears once, balance invariants hold, parent ownership/cache
isolation cannot be bypassed, staff fields are redacted, and Ripple failure is
stale-or-503 rather than partial success.

Classify every staff/source shadow difference. Stop and reject readiness for any
unexplained balance, duplicate, BOLA/cache leak, legacy-note ambiguity, missing
permanent E2E, or Pending/payment regression. Report accepted, needs-fix, and
unverified items with exact evidence.
```
