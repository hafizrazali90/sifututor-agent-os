# Cross-Project Implementation Plan

## Definition Of Done

The work is complete when a parent can view their own canonical statement in the
app, all accounting invariants and deduplication rules pass, the staff and parent
views share one projection engine, failure is explicit and safe, permanent API
and mobile regressions exist, and the feature has passed staged rollout and
production read-only monitoring.

This plan does not authorize implementation. Payments, invoices, service auth,
and mobile contracts remain in the critical lane and require explicit approval
before Phase B.

## Phase 0 - Preflight And Data Contract Freeze

Owner: cross-project lead. No production writes.

1. Create one umbrella/epic issue and one implementation issue in each affected
   repository; link acceptance criteria and this pack.
2. Confirm no conflicting active task/branch; create clean worktrees/branches.
3. Re-run read-only aggregate checks and record counts by source, missing
   metadata, and duplicate candidates.
4. Audit approved legacy Ripple CN/DN according to the hard gate in
   `DECISIONS.md`.
5. Capture sanitized golden fixtures for the required personas/scenarios.
6. Confirm EdDSA or RS256 runtime support and document key rotation/ownership.
7. Freeze contract v1 and the three product decisions.
8. Define feature flags and environment names without reading or committing
   secret values.

Exit: legacy adjustment treatment is decided, contract examples validate, and
each project has an approved build issue and clean branch.

## Phase 1 - Ripple Canonical Projection Engine

Owner: `ripple-suite`.

### Goal

Turn the existing staff statement calculation into one tested domain engine
that can safely feed both the staff UI and a parent serializer.

### Entry Points And Likely Files

- `src/app/api/accounts/[parentId]/statement/route.ts`
- `src/modules/accounts/lib/statement.ts`
- `src/modules/accounts/lib/invoice-amount.ts`
- `src/modules/reconciliation/lib/customer-receipts.ts`
- `src/modules/accounts/types/accounts.ts`
- new server-only projection/source-adapter/serializer modules under
  `src/modules/accounts/server/`

### Work

1. Write characterization tests for current source queries and staff response.
2. Define internal `CanonicalLedgerEvent` and `CanonicalStatement` types using
   integer minor units or an existing safe decimal abstraction.
3. Extract source adapters for SIMS invoices/deductions/refunds/commitment fees
   and Ripple receipts/allocations/credits/payment records/legacy notes.
4. Implement source priority and stable identity rules.
5. Group SIMS payment-attempt items so one bundled FIUU payment is emitted once.
6. Exclude receipt-backed payment-record mirrors.
7. Add explicit `affects_balance` and `balance_delta`; stop inferring arithmetic
   from display status such as `Reconciled`.
8. Compute opening/running/closing balance deterministically and assert the
   invariant.
9. Treat `invoice_payment_status` only as derived display/sync metadata.
10. Create two serializers:
    - staff serializer preserving the existing staff API shape and enrichment;
    - parent-safe serializer matching contract v1.
11. Move the existing staff endpoint to the shared engine without changing its
    public response contract.
12. Add projection metrics: source latency/failure, event counts by type,
    dedupe exclusions, balance-invariant failures, legacy-derived events.

Exit: golden fixtures pass; staff response compatibility is proven; the
canonical engine produces correct parent-safe events without an endpoint yet.

## Phase 2 - Ripple Private Read Endpoint

Owner: `ripple-suite`.

### Entry Points And Likely Files

- `src/proxy.ts`
- `src/lib/auth.ts` only for patterns, not staff-cookie reuse
- new `src/lib/internal-service-auth.ts`
- new `src/app/api/internal/v1/parent-ledger/route.ts`
- projection modules from Phase 1

### Work

1. Add a separate deny-by-default `/api/internal/v1/` proxy branch.
2. Verify signed token algorithm, `kid`, issuer, audience, subject, scope,
   issuance/expiry, and request ID.
3. Reject any client-supplied parent identity that conflicts with the token;
   preferably accept no parent identity outside `sub`.
4. Validate date/range/cursor/limit; normalize timezone boundaries.
5. Call only the canonical parent-safe serializer.
6. Return `projection_complete`, generation time, and source freshness.
7. Enforce GET-only, rate limits, request timeouts, safe logging, and structured
   error codes.
8. Add a disabled-by-default endpoint flag.
9. Add unit/integration tests for signatures, wrong parent/issuer/audience/scope,
   expired/future tokens, key rotation, filter validation, source failure, and
   field redaction.

Exit: the internal endpoint works with generated test keys, is not reachable
through staff-cookie or public-prefix auth, and exposes no forbidden field.

## Phase 3 - SIMS Parent-Facing Façade

Owner: `sifu-tutor`.

### Entry Points And Likely Files

- `routes/api.php`
- `app/Http/Middleware/VerifyApiToken.php`
- existing parent controller patterns under
  `app/Http/Controllers/API/Parent/`
- new controller, request validator, Ripple ledger client, token signer, DTO/
  resource mapper, and cache service
- configuration files using environment references, never committed secrets

### Work

1. Add `GET /api/parent/payment-statement` inside the existing parent bearer
   middleware group.
2. Derive the parent from `Auth::user()`; accept no parent ID from the app.
3. Validate and normalize period/range/cursor/limit.
4. Sign a short-lived per-request service JWT with the authenticated parent in
   `sub`, the required scope, and correlation ID.
5. Call Ripple with bounded timeout and one safe connection retry at most.
6. Validate Ripple contract version and `projection_complete=true` before
   mapping.
7. Apply an allowlist DTO/resource so internal metadata cannot leak.
8. Cache only complete successful public projections; mark stale fallback
   explicitly; return 503 when none exists.
9. Preserve the existing SIMS response envelope and session-expiry behavior.
10. Add feature flag, metrics, sanitized logs, and trace propagation.
11. Do not alter `get-invoices`, payment initiation, FIUU callback, invoice
    settlement, refund, or reconciliation write paths.

Exit: API feature/contract tests prove self-only access, mapping, cache/failure
behavior, and backward compatibility with existing parent endpoints.

## Phase 4 - Parent App Statement

Owner: `sifututor_parent`.

### Entry Points And Likely Files

- `Constant/Endpoints.ts`
- `Screens/Invoice/index.tsx`
- `Components/Invoice/*`
- `hooks/useAppQuery.ts`
- `types/api.ts` and new statement types
- `e2e/maestro/p3-invoice-detail.yaml` or a dedicated permanent statement flow
- `QA_TEST_CASES.md` / project test coverage manifest as applicable

### Work

1. Add the SIMS endpoint constant and strict v1 response types.
2. Keep the existing invoice query for Pending; create a separate statement
   query enabled only for the Statement tab.
3. Rename the visible Receipt tab to Statement and remove its local flattening/
   arithmetic as the statement data source.
4. Build balance summary, filters, cards, details, pagination, loading, empty,
   stale, offline, and unavailable states from `UX-SPEC.md`.
5. Display server values; never calculate running balance or dedupe locally.
6. Invalidate statement data after a successful payment and on relevant Pusher
   events, while respecting the two-minute stale policy.
7. Put the new view behind a remote/app feature flag with current Receipt view
   as temporary rollback fallback only during controlled rollout.
8. Add unit/component tests and permanent Maestro/mobile E2E.
9. Update QA documentation and accessible labels.

Exit: app tests pass and a representative parent completes the real Statement
journey without affecting Pending or payment flows.

## Phase 5 - Cross-System Verification

Owner: independent verifier plus project owners.

1. Run source-specific suites and build/type/lint checks.
2. Run seeded contract flows through App -> SIMS -> Ripple for every scenario in
   `TEST-PLAN.md`.
3. Verify Ripple staff and parent outputs share event identity/arithmetic while
   parent output excludes staff-only fields.
4. Shadow compare a read-only parent sample against source facts. Explain known
   expected differences from the legacy staff endpoint rather than requiring a
   blind row-for-row match.
5. Verify no production writes and no new query explosion.
6. Complete adversarial security review for BOLA, JWT confusion, cache leakage,
   cursor tampering, log leakage, and error disclosure.

Exit: independent evidence maps every acceptance story to a passing test and
human journey; all unexplained balance differences are zero.

## Phase 6 - Release And Rollback

Deployment order is backward compatible:

1. Deploy Ripple engine and internal endpoint disabled.
2. Configure/verify public key and enable only for SIMS service traffic.
3. Deploy SIMS endpoint disabled; run internal contract smoke.
4. Deploy parent app with Statement hidden.
5. Enable Ripple, then SIMS, then a small parent cohort/app flag.
6. Monitor latency, 4xx/5xx, stale responses, dedupe counts, balance invariant,
   app crashes, and support feedback.
7. Expand gradually only after the agreed monitoring window.

Rollback order:

- Disable the app Statement flag first; Pending remains operational.
- Disable the SIMS public endpoint if required.
- Disable Ripple internal endpoint last after dependent traffic stops.
- No finance data rollback is required because V1 is read-only.

## Repository And Commit Boundaries

- Never implement this cross-project feature on the current unrelated Ripple
  CRM branch or SIMS duplicate-schedule branch.
- One clean issue/branch/PR per project; no umbrella commit containing project
  code.
- Ripple PR lands first, SIMS second, app third.
- Payment/auth/mobile contract changes stop for human review before commit and
  again before deploy.
- Permanent E2E coverage is mandatory; a one-off smoke does not replace it.
