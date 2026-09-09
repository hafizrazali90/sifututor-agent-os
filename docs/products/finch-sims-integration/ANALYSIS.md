# Finch ↔ SIMS Selective Integration — Architecture Analysis

**Status:** research/analysis complete, design decision pending Hafiz sign-off
**Date:** 2026-07-18
**Scope:** Cross-project (`finch-inbox` + `sifu-tutor`)
**Author:** Claude (deep-dive via 3 parallel research agents: Finch codebase+DB, SIMS codebase+DB, industry patterns)

## 1. The mission, restated precisely

Finch is becoming a real external multi-tenant WhatsApp/omnichannel inbox SaaS. Sifututor's own
tutoring business already runs inside Finch as its first tenant — internally called **"Sifu Edu"**
(`company_guid F4B3221C-C1E1-4D69-B35E-28D9B6ABC549`, plan `internal_legacy`, currently
**unrestricted** entitlements).

Goal: build new Finch features (starting with a document feature, more later) that, **only for
Sifu Edu**, also link to SIMS (Sifututor's Laravel/MySQL system — the source of truth for tutors,
staff, parents, requests, invoices). Every other Finch tenant (real paying external customers)
gets the same feature, fully standalone, with zero SIMS awareness.

This is fundamentally a **tenant-scoped entitlement problem** wrapped around a **cross-system
integration** problem. Both halves already have real precedent in the two codebases — this is not
greenfield architecture, it's extending two things that already exist.

## 2. Current state — verified against live code and live databases

### 2.1 Finch: entitlement/tenant model (read-only DB + code verified)

`backend/src/billing/entitlements/entitlement.service.ts` resolves entitlements per `company_guid`
in 3 layers (override → plan default → legacy columns), cached 30s. The shape has a `flags`
namespace (booleans, default false) and an `extras` free-form escape hatch explicitly documented as
"for keys not yet promoted into the typed surface."

Confirmed live: Sifu Edu's plan row (`plan_id=1`, `plan_code='internal_legacy'`) already carries
```json
"extras": {"meta_whatsapp_charges":"pass_through","migration_support":"internal","internal_legacy_unrestricted":true}
```
— i.e. the exact "one special tenant gets an internal flag" pattern already exists in production
for a different purpose. No per-tenant override row exists for Sifu Edu; the unrestricted state
lives entirely in the plan row.

**Important gap found:** `EntitlementFlags` resolve correctly but are **enforced nowhere in the
codebase today** — zero call sites gate any behavior on a flag. Only `StatusGuard` (lifecycle
status: active/suspended) is a real enforced guard, and it's itself dark-launched behind
`BILLING_ENFORCEMENT_ENABLED=false`. This means a `sims_linkage_enabled` flag would be the **first
real enforcement** of this machinery — low risk (isolated, single new call site) but no in-repo
precedent to copy exactly.

### 2.2 Finch: existing "documents" feature — naming collision to resolve

`backend/src/documents/` **already exists**. It is not a general file/record manager — it indexes
WhatsApp chat-attachment media (`wa_ticket_messages.media_url`) into `wa_documents`, letting staff
categorize (receipt/other), approve/reject, and annotate. Tenant-scoped, RBAC-gated
(`documents.view` permission). A working S3 upload pipeline (`backend/src/storage/`) backs it.

**This means "document feature" is ambiguous** between two very different things:
- **(A)** Extending/relabeling this existing chat-attachment module to also ingest SIMS-sourced
  documents for Sifu Edu, or
- **(B)** A new, separate capability — e.g. a "SIMS records" panel in the inbox contact view showing
  a tutor/staff/parent's SIMS-held documents (IC, contracts, certificates) — unrelated to chat
  attachments.

These have different data models, different security posture, and different UI surfaces. **This is
the single most important open question before any build work starts** — see §6.

### 2.3 SIMS: what document data actually exists (read-only DB + code verified against production)

No dedicated `Document` model. Everything rides on `spatie/laravel-medialibrary` — a single
polymorphic `media` table (`model_type`, `model_id`, `collection_name`, `file_name`, `disk`, no
`deleted_at` — hard-delete only, no soft-delete audit trail on the documents themselves).

Confirmed live collections and volumes:

| Model | Collections | Rows (prod) |
|---|---|---|
| `Tutor` | `resume`, `education_transcript`, `formal_photo`, `identity_card_front`, `tutor_image` | ~1,524–1,536 each |
| `Staff` | `employment_contract`, `nric_passport_copy`, `employment_form`, `profile_photo` | 1–6 (lightly used so far) |
| `ParentModel` | `parent_image` | 200 |
| `ParentInvoice` | `parent_invoice_attachment` | 6,712 |
| `TutorCommitmentFee` / `ParentCommitmentFees` | `*_attachment` | 9,947 / 1,159 |
| `Classes` | `check_in_proof`, `check_out_proof` | ~150K each |

**Data-quality landmines any sync/read code must handle:**
- Legacy rows exist with `model_type = 'tutor'`/`'parent'` (bare strings) alongside current FQCN
  rows — a pre-rebuild morph-map mismatch.
- 38 confirmed `Tutor` media rows whose parent `tutors` row is soft-deleted — any query **must**
  join on `deleted_at IS NULL` (the existing global SIMS rule) or it will surface documents for
  deleted tutors.

**PII sensitivity:** IC/passport/NRIC copies, employment contracts. No existing external-exposure
precedent for this data — this would be the **first time** SIMS document data leaves its own admin
portal to an external consumer. Treat as net-new security design, not "reuse an existing contract."

### 2.4 SIMS: external API surface — real, extensible precedent already in production

Three coexisting auth patterns in `routes/api.php`. The relevant one:
**`VerifyOpenApiKey`** — paired `X-Api-Key`/`X-Secret-Key` checked against an `ApiClient` model
(table `api_clients`). This is the extensible "register a new external consumer" pattern.

**Confirmed live:** one active row already exists — `name="Learnest Production"`, created
2026-07-17 (yesterday) — a sibling Sifututor product is *already* wired through this exact
mechanism, currently scoped to 4 public lookup routes (levels/subjects/states/cities, no PII). This
is strong, working, low-risk precedent for registering Finch the same way. **No rate limiting or
versioning exists on this route group today** — would need to be added before exposing document
data.

**Identity join key:** `staff.phone`/`staff.email`, `tutors.phone`/`tutors.email` are the natural
match keys against a Finch WhatsApp contact (phone-keyed).

**Adjacent, separate integration already planned:** SIMS docs (`billing-cycle-revamp/PRD.md`,
`DECISIONS-AND-OPERATIONS.md`) already name Finch as a **future outbound WhatsApp notification
channel** ("WhatsApp via Finch") — decisions locked, not yet built, currently on `NenjiErpApi`
(desk.nenjierp.com). This is the *opposite direction* of integration (SIMS → Finch, send
notifications) from the document feature (Finch → SIMS, read records). They will likely converge
on the same tenant/company_guid eventually but are two distinct integration surfaces — don't
conflate them in scoping.

### 2.5 Finch: integration surface for calling out to SIMS

Two existing outbound-HTTP patterns to reuse as a template:
- Per-tenant cached axios instance (`whatsapp-cloud.service.ts`) — built once, baseURL+token per
  `company_guid`.
- Per-call factory reading env vars, with an explicit test seam (`razorpay-client.factory.ts`) —
  better fit for a single-tenant integration like SIMS (no caching complexity needed since it's
  gated to one tenant anyway).

One piece of **untracked schema drift** worth flagging to Hafiz, not necessarily using: a
`wa_data_migration_map` table (908K rows) with a generic `source_system`/`entity_type`/`source_id`
shape already exists live in Finch's MSSQL, with zero references anywhere in the repo — likely a
leftover from a historical ad-hoc import, unrelated to SIMS. Its *shape* is a reasonable precedent
if a persistent SIMS-linkage mapping table is ever wanted, but it should not be silently reused
without understanding what populated it.

## 3. Industry pattern check

Public case studies of "vendor's own tenant gets a private backend hook inside the multi-tenant
product" are thin (companies don't blog their internal wiring, for obvious security reasons), but
the underlying principles are well established and map directly onto what's already in this repo:

- **Anchor-tenant/dogfood pattern**: Slack, Shopify, Stripe all run their own business on/around
  their own product with internal-only extensions — normal and expected, not a special case to be
  ashamed of architecturally.
- **Entitlement-flag gating, not a hardcoded tenant check**: platforms like LaunchDarkly explicitly
  support one-off per-tenant-key targeting rules alongside tier-based flags, precisely for this
  "internal/dogfood flag" case. Finch's `EntitlementService` already *is* this mechanism — it just
  isn't enforced anywhere yet.
- **Cross-system mechanism for a read-heavy "surface external records" use case**: on-demand
  synchronous API pull (or a thin adapter service) is correct here — not a webhook (no proactive
  push need) and not batch ETL (would duplicate PII into a second store with staleness/deletion
  drift). This matches the recommendation independently reached from both the Finch and SIMS
  research.
- **Document integration security precedent** (DocuSign↔Salesforce, Box/Drive↔Zendesk): scoped
  tokens + signed, time-limited URLs for file bytes; the document system remains the access-control
  point, never raw cross-database access, never bytes duplicated into the CRM's own storage unless
  explicitly required.
- **Named anti-pattern to avoid** (OWASP Multi-Tenant Security Cheat Sheet): "skip tenant isolation
  checks for our own internal tenant" is a recurring source of cross-tenant leaks. The mitigation is
  structural: keep the SIMS linkage in one bolt-on adapter module, gated by a single entitlement
  check at the boundary — never `if (companyGuid === SIFU_EDU_GUID)` scattered through core
  document/business logic.

## 4. Recommended architecture

**On the Finch side:**
1. Add `sims_linkage_enabled: boolean` (default `false`) to `EntitlementFlags`. Set `true` only on
   Sifu Edu's plan row (`entitlements_json.flags`) — or a `wa_plan_overrides` row scoped to its
   `company_guid` if `internal_legacy` is ever shared with another tenant later.
2. Build a `SimsIntegrationService` (per-call factory pattern, `SIMS_API_BASE_URL`/`SIMS_API_TOKEN`
   from env) as a self-contained adapter module — no SIMS-aware code anywhere else in Finch.
3. Whatever the "document feature" turns out to mean (§6), its service layer calls
   `entitlementService.resolveFlag(companyGuid, 'sims_linkage_enabled')` before invoking
   `SimsIntegrationService` at all. Every other tenant simply never takes that branch.

**On the SIMS side:**
1. Register Finch as a new `ApiClient` row (mirrors the Learnest precedent from yesterday).
2. Add new read-only `/open/...`-style endpoints (or a new versioned prefix) for whatever document
   scope is agreed — e.g. `GET /open/tutors/{phone}/documents`, `GET /open/staff/{phone}/documents`
   — returning **signed, short-lived URLs** to the underlying media (Spatie temporary URLs or
   equivalent), never raw file bytes proxied wholesale, never a bulk DB dump.
3. Add rate limiting (none exists on this route group today) and audit logging (who/when a
   document was fetched externally) before shipping — this is the first time this PII class leaves
   SIMS's own portal.
4. Every query joins `deleted_at IS NULL` (global SIMS rule) and normalizes `model_type` to avoid
   the legacy string-vs-FQCN mismatch found in prod.

This keeps both systems' core logic untouched: SIMS gains one new bounded API surface (like it
already does for Learnest); Finch gains one new entitlement flag plus one adapter module. Nothing
about how either system serves its non-Sifu-Edu tenants/other data changes.

## 5. Extending the pattern to future features

The same two building blocks generalize: any future Finch feature that needs a "linked mode" for
Sifu Edu reuses the *same* `sims_linkage_enabled` flag (or a more granular flag per feature if scope
grows) and the *same* `SimsIntegrationService` adapter, just calling a different SIMS endpoint. No
new gating mechanism should be invented per feature — that's exactly the "special-casing sprawl"
anti-pattern flagged in §3.

## 6. Open questions as of first pass — superseded, see §7–§9

This section is kept for the record; questions 1 and (implicitly) 2–3 below were resolved by the
§7 (route via ripple-suite) and §8 (Finch documents = payment-receipt triage, narrow overlap =
payment-proof only) follow-up passes. Questions 4–5 remain genuinely open.

1. ~~What does "document feature" mean concretely?~~ **Resolved by §8**: it's Finch's existing
   payment-receipt reconciliation triage (bank-transfer/e-wallet proofs for tuition fees), not a
   general document system — no tutor/staff HR paperwork exists on the Finch side to link.
2. ~~Read-only surfacing, or two-way sync?~~ **Refined by §7/§8**: the realistic shape is Finch
   calling ripple-suite to look up/confirm/mark the matching SIMS invoice when a receipt is
   approved — a scoped read+confirm action tied to one business event, not a general sync.
3. ~~Which SIMS documents specifically?~~ **Resolved by §8**: only
   `ParentInvoice`/`TutorCommitmentFee`/`ParentCommitmentFees` payment-proof attachments are in
   scope; tutor/staff onboarding documents have no Finch-side counterpart to link.
4. **Still open — Relationship to the already-planned "WhatsApp via Finch" notification channel**
   (SIMS → Finch, locked in PRD, unbuilt): same tenant, opposite direction, separate workstream —
   sequence or scope together?
5. **Still open — Where should the receipt-matching UI/action live**, ripple-suite or embedded in
   Finch (see §7's still-open UI-placement question and §9 for the pending decision)?
6. **Still open — What other new Finch features are in mind**, so the entitlement/adapter pattern
   can be validated against more than just the document case before locking the design?

## 7. Revised recommendation — route through ripple-suite, not a new SIMS API surface (2026-07-18, follow-up)

Hafiz asked: "why not on ripple but sync to or from sims? staff work on ripple, sims is source of
truth if related to sims function." A targeted verification pass on ripple-suite (the internal
staff dashboard) confirmed this is the better architecture than §4's original "Finch talks directly
to a new SIMS API surface" plan.

**Ripple-suite already has everything needed, verified live:**
- Direct read-only MySQL access to SIMS (`src/lib/db.ts`, raw `mysql2/promise` pool) — read-only by
  policy (`AGENTS.md:30`: "NEVER WRITE TO SIMS... No INSERT/UPDATE/DELETE ever"), not just by design
  intent; the one code path capable of writes (`execute()`) is confirmed unused anywhere in
  `src/modules`.
- An established **write-back-via-SIMS-API precedent** for anything that needs to change SIMS state:
  `src/modules/tutor-payments/lib/sims-api.ts`, `crm/lib/sims-api.ts`,
  `reconciliation/lib/sims-api.ts` all call SIMS's own Laravel REST API (bearer token
  `SIMS_RIPPLE_KEY`) rather than writing to MySQL directly — SIMS remains the sole writer of its
  own data, exactly as the existing cross-repo architecture decision requires.
- Substantial existing document/attachment infrastructure (KB document pipeline with
  upload/versioning, CRM lead-note attachments, QA defect attachments, signed blob-upload tokens,
  transfer-proof uploads for tutor payments) — directly reusable rather than building parallel
  infrastructure in Finch.
- A working bearer-token auth pattern for **external, non-browser callers**
  (`CRON_SECRET`, `QA_API_SECRET` in `src/proxy.ts`) — adding a `FINCH_API_SECRET`-gated route
  prefix is small, precedented work, not a new pattern.
- Persistent self-hosted deployment (KVM8/PM2, not serverless) — easier for another backend
  (Finch) to call reliably than exposing a brand-new surface on SIMS's own Laravel app.
- **Zero multi-tenant concept** (`tenant`/`company_id` — zero hits anywhere in `src/`) — it only
  ever serves internal Sifututor staff. This *simplifies* the isolation story: ripple doesn't need
  to enforce "only Sifu Edu" itself; Finch's own `sims_linkage_enabled` entitlement flag (§4)
  already ensures only Sifu Edu's tenant ever calls ripple's new endpoint at all.

**Revised recommendation:** replace §4's "SIMS registers a new `ApiClient` for Finch" step with
"Finch calls a new bearer-token-gated route on ripple-suite; ripple-suite talks to SIMS the way it
already does (direct read, SIMS-API write-back)." This avoids giving SIMS a *second* external
consumer to trust (Finch, in addition to ripple) and reuses proven plumbing instead of building a
parallel one. §4's Finch-side half (new `sims_linkage_enabled` entitlement flag gating a
`SimsIntegrationService` adapter module) is unchanged — only the far end of that adapter's call now
points at ripple-suite instead of a new SIMS `ApiClient`.

Still open: whether the document *work itself* (viewing/approving/matching) happens as a UI inside
ripple-suite (staff briefly leave the WhatsApp inbox to act — lower engineering cost, reuses
existing ripple UI patterns) or as a panel embedded inside Finch's own inbox (staff never leave the
chat, but Finch must build and maintain a second UI for the same data). Not yet resolved — see §9.

## 8. Revised finding — what Finch's "documents" feature actually is (2026-07-18, follow-up)

Per Hafiz's direction ("first understand what type of doc we have on finch, then we only
understand how to link with sims"), a targeted inventory pass on live Sifu Edu data settled the
§6/§2.2 ambiguity with a concrete answer instead of a hypothetical one.

**`wa_documents` is not a general document system — it's a payment-receipt reconciliation triage
tool.** Schema confirmed (`backend/sql/init.sql:274-296`): `category` is a hard 2-value enum
(`receipt`/`others`), no filename/mimetype stored in this table at all (that lives on the joined
chat message), `status` (pending/approved/rejected), `notes` (free-text JSON tags:
Student Name/Invoice No/Amount/Brand/Remarks), `approver_remarks`. **There is no upload/create
endpoint** — a row only ever comes from an inbound/outbound WhatsApp chat message that already has
`media_url`; staff categorize and approve/reject, they never attach a document unrelated to a
chat message.

Live Sifu Edu data (36,893 media messages total, 18,882 explicitly triaged): the **3,294 approved
"receipt" rows are unambiguously bank-transfer/e-wallet payment proofs for tuition fees** —
sample filenames like `M2U_20260710_2104.pdf`, `RHB_...pdf`, `HLB Receipt-2026-07-16.pdf`, and chat
text like "yuran bulan 7" (month 7 tuition fee) / "Salam yuran dh bnk in" (fee already banked in).
The 33,451-row "others/pending" backlog is mostly conversation screenshots and general media, not
paperwork. Page copy in `DocumentsSettings.tsx` confirms the intent directly: *"View and categorize
media attachments from ticket messages. Receipts can be approved for reconciliation."*

**Overlap with SIMS document types is narrow and specific, not general.** SIMS's tutor
resumes/IC/transcripts and staff employment contracts/NRIC have **no analogue** in Finch's real
data — those are structured onboarding paperwork uploaded through a form, never captured from chat.
The one genuine overlap: **Finch's approved payment-receipt screenshots and SIMS's
`ParentInvoice`/`TutorCommitmentFee`/`ParentCommitmentFees` attachment collections are both "proof
of payment" artifacts for the same real-world event** — a parent paying a tuition invoice.

**This reframes the mission concretely.** The realistic, high-value "document feature ↔ SIMS
linkage" is: when Sifu Edu staff approve a receipt in Finch, match it against the correct SIMS
invoice (by parent phone + amount + rough date) and surface/confirm the SIMS invoice/commitment-fee
status right there — potentially auto-marking it paid — instead of staff manually cross-referencing
Finch chat receipts against SIMS invoices by hand. This is a real automation win (matches the
original mission's "maximise automation" goal) with a bounded, well-understood data shape, rather
than a speculative general "sync all documents" feature. It does **not** imply linking tutor/staff
HR paperwork at all — that data has no Finch-side counterpart to link from.

This still fits the recommended architecture (§4, revised by §7's ripple-suite routing): Finch's
receipt-approval action would call ripple-suite (which already has both SIMS read access and the
`tutor-payments`/`sims-api.ts` write-back-via-SIMS-API precedent) to look up/confirm/mark the
matching SIMS invoice — gated by the same `sims_linkage_enabled` entitlement flag so only Sifu Edu's
tenant ever takes this path.

## 9. Remaining decision — where does the receipt-matching action live?

Now that the object being linked is concrete (an approved Finch receipt ↔ a specific SIMS
invoice/commitment-fee row), the §7 UI-placement question narrows to a specific choice:

- **Ripple owns it**: the "match to SIMS invoice" action is a new step in ripple-suite's existing
  reconciliation/tutor-payments UI — when a receipt is approved in Finch, ripple surfaces it in a
  reconciliation queue staff already work from. Reuses `reconciliation`/`tutor-payments` modules
  directly; staff already do reconciliation work in ripple today.
- **Finch embeds it**: the approve-receipt action in Finch's `DocumentsSettings.tsx` itself shows
  the matched SIMS invoice inline and lets staff confirm/mark-paid without leaving the chat/receipt
  view — requires Finch to call out to ripple synchronously from that same approval action and
  render the result.

Given ripple-suite already has a `reconciliation` module and staff already reconcile payments
there, extending that existing workflow to also pull in Finch-approved receipts (via a scheduled or
on-demand call from ripple to Finch's API, rather than the other direction) may be the more natural
fit than embedding SIMS-matching logic inside Finch's receipt-approval screen — but this needs
Hafiz's confirmation, since it also determines which side initiates the call (Finch → ripple on
approval, vs. ripple → Finch pulling approved receipts into its own reconciliation queue).

## 11. End-to-end design (2026-07-18, per Hafiz's spec) — "staff approve receipt in Finch → syncs to ripple customer receipt → updates collection module"

Hafiz's exact ask: staff approve a doc as a receipt with all detail confirmed in Finch; it syncs to
ripple's customer receipt and updates the collection module accordingly, end to end. Two more
verification passes (ripple's actual collection/customer-receipts pipeline; whether Finch's known
"Nenji" history has any bookkeeping overlap — it doesn't, see the memory correction above) ground
this design in real, already-built code on the ripple side. **Nothing described below is
hypothetical on the ripple side — `collection_receipts`, `customer_receipts`,
`receipt_invoice_allocations`, `invoice_payment_status`, the bank-auto-match job, and the
worklist/my-queue views all already exist and run today.**

### 11.1 Ripple's existing pipeline (verified, unchanged by this design)

- **`collection_receipts`** (intake/proof, `payment_channel` enum: `google_form`/`nenji`/`bank_transfer`/`other`
  — the `nenji` value is a legacy label from when this same product lineage was branded NenjiERP,
  worth renaming/adding a `finch` value rather than repurposing it verbatim) + **`customer_receipts`**
  (canonical financial record, `bank_match_status`, `status`) + **`receipt_invoice_allocations`**
  (supports partial/multi-invoice) + **`invoice_payment_status`** (`covered_amount`, `coverage_pct`,
  `sims_sync_status`).
- Today's manual flow (`POST /api/collection/receipts`): staff-authenticated, validates the SIMS
  invoice exists, inserts `collection_receipts` (pending_verification) + `customer_receipts`
  (pending_bank_match) + allocation in one transaction, then recalculates
  `invoice_payment_status`. **This recalculation is exactly "updates the collection module" —
  the worklist (`collection/worklist`) and per-coordinator queue (`collection/my-queue`) both read
  live off this state, so a new receipt immediately moves that invoice out of active
  chasing into an `awaitingRecon` bucket.**
- Bank-transaction matching is automatic and separate (`autoMatchPendingCustomerReceipts()`,
  RM2/3-day tolerance, auto-confirms only when unambiguous).
- **SIMS is only actually written to as an explicit separate human action** —
  `POST /api/accounts/invoice-coverage/[invoiceId]/sync-sims` (gated by `accounts_approve`
  permission), only reachable once an invoice is 100% covered by a *confirmed, bank-matched*
  receipt. Receipt creation alone never marks a SIMS invoice paid.

### 11.2 The end-to-end flow this design adds

1. **Finch**: staff approve a `wa_documents` row as a receipt with confirmed tag fields (Student
   Name, Invoice No, Brand, Amount, Remarks — already captured today) **plus two new fields
   Finch doesn't capture yet: Receipt Date, and Brand needs to become a constrained dropdown
   (`st`/`nn`) instead of free text** to match ripple's enum cleanly.
2. Finch's approve action, gated by `sims_linkage_enabled` (§4) resolving true for the
   `company_guid`, calls a new adapter (rename from `SimsIntegrationService` to
   `RippleIntegrationService` — it talks to ripple-suite, not SIMS directly, per §7) which POSTs to
   a new ripple-suite endpoint, e.g. `POST /api/finch/collection-receipts`.
3. **Ripple, new endpoint**: authenticated via a new bearer token (`FINCH_API_SECRET`) added to
   `src/proxy.ts`'s existing external-caller pattern (same shape as `CRON_SECRET`/`QA_API_SECRET`),
   bypassing the JWT-cookie `requireAuth()` path entirely for this one prefix — precedented, not
   novel.
4. **Schema gap that must be closed first**: every existing receipt-creation path assumes a real
   `AuthUser` and stores `uploaded_by`/`performed_by` as `INTEGER NOT NULL` FKs into SIMS `users.id`
   — there is no "this came from an external system, approved by X" column anywhere.
   **Recommended fix** (matches the ripple agent's own suggestion and reuses an existing pattern):
   add `source_channel` + `external_approver_name` (or a JSON `external_meta` blob, mirroring how
   `reconciliation_audit_log` already stores arbitrary JSON) to `collection_receipts`/
   `customer_receipts`, rather than fabricating a fake Ripple staff-user id for Finch approvals.
   `uploaded_by` can point at a dedicated system/service account row if a NOT NULL FK must be kept.
5. The new endpoint reuses the **exact same transaction** the manual route already runs (validate
   invoice_ref against `parent_invoices`, insert `collection_receipts` + `customer_receipts` +
   `receipt_invoice_allocations`, call `recalculateInvoicePaymentStatuses()`) — no new business
   logic, just a new entry point into logic that already exists.
6. From here, **nothing changes**: bank-transaction auto-matching still runs the same job, the
   worklist/my-queue still reflect the new receipt the same way, and the SIMS "mark paid" sync
   still requires the same explicit human `accounts_approve` action after bank-match confirmation.

### 11.3 Recommended guardrail — do not let a Finch approval alone mark SIMS invoices paid

This is a deliberate recommendation, not a neutral finding: **keep the existing bank-match →
manual-SIMS-sync gate exactly as it is.** A staff member confirming details inside a WhatsApp chat
is a lower-trust signal than a matched bank transaction; collapsing "approved in Finch" straight
into "SIMS invoice marked paid" would remove the one verification step ripple's design already
treats as load-bearing, and financial/payment flows are explicitly a human-review-required domain
per the umbrella critical rules. The Finch approval should feed the pipeline at the same point the
manual upload does today (receipt intake), not bypass it.

### 11.4 Field-mapping gaps to resolve before build

| Finch has today | Ripple needs | Gap |
|---|---|---|
| Invoice No (free text) | `invoice_ref` | Needs existence-validation against `parent_invoices` (already done server-side) |
| Brand (free text) | `brand` enum `st`/`nn` | Finch UI should become a dropdown, not free text |
| Amount (free text) | `amount` | Needs numeric parsing/validation |
| — (missing) | `receipt_date` | **New Finch field needed** — no date currently captured |
| — (missing) | `payment_channel` | New enum value needed (e.g. `finch`), defaulted server-side |
| Student Name, Remarks | no dedicated field | Concatenate into `note` (accepted by `customer_receipts`/`reconciliation_audit_log`, currently NOT accepted by the `collection_receipts` POST body — needs adding) |
| approver identity (Finch operator) | no schema slot today | New `source_channel`/`external_approver_name` columns (§11.2 point 4) |
| — | `year` (required by collection_receipts) | Derive from receipt_date once that field exists |

### 11.5 One scope flag: NN brand worklist is currently unimplemented

`getUnpaidSTInvoices()` returns `[]` for the NN brand today — a real gap if Sifu Edu's Finch tenant
handles receipts for both ST and NN brands. Confirm whether NN-brand receipts are in scope before
committing to this design, since the worklist/collection-module side wouldn't reflect them yet.

## 12. Sources

- Finch: `backend/src/billing/entitlements/*`, `backend/src/documents/*`, `backend/src/storage/*`,
  `backend/src/whatsapp-cloud/whatsapp-cloud.service.ts`,
  `backend/src/payments/curlec/razorpay-client.factory.ts`, live `teaminbox` MSSQL (companies,
  wa_subscription_plans, wa_plan_overrides, wa_data_migration_map).
- SIMS: `app/Models/Tutor.php`, `app/Models/Staff.php`, `app/Services/TutorService.php`,
  `app/Services/StaffService.php`, `app/Models/ApiClient.php`,
  `app/Http/Middleware/VerifyOpenApiKey.php`, `routes/api.php`, live production MySQL (media,
  api_clients, staff, tutors), `docs/features/billing-cycle-revamp/PRD.md`.
- Industry: LaunchDarkly entitlements/tenant targeting, ConfigCat tenant feature flags, Merge.dev
  polling-vs-webhooks, DocuSign↔Salesforce integration security model, OWASP Multi-Tenant Security
  Cheat Sheet.
- Ripple-suite: `src/lib/migrations/039-customer-receipts.sql`, `042-collections-tables.sql`
  (+047/050/051 extensions), `src/app/api/collection/receipts/route.ts`,
  `src/app/api/collection/worklist/route.ts`, `src/app/api/collection/my-queue/route.ts`,
  `src/app/api/accounts/reconciliation/resolve/route.ts`,
  `src/app/api/accounts/invoice-coverage/[invoiceId]/sync-sims/route.ts`,
  `src/modules/reconciliation/lib/customer-receipts.ts`, `src/modules/reconciliation/lib/sims-api.ts`,
  `src/lib/auth.ts`, `src/proxy.ts`, `docs/features/collection/prd.md`,
  `docs/features/reconciliation/spec.md`.
- Finch/Nenji history correction: `docs/PROJECT_JOURNEY.md`, `docs/runbooks/legacy-data-migration.md`,
  `docs/decisions/hafiz-onboarding-ask.md`, `BUSINESS_DISCOVERY.md`, `AGENTS.md` — see §13 memory
  correction.

## 12.1 Decisions locked (2026-07-18)

- **Brand scope:** ST-brand receipts only for this build. NN-brand worklist support
  (`getUnpaidSTInvoices` returning `[]` for NN, §11.5) is explicitly out of scope — a separate
  future piece of work if/when NN-brand receipts need to flow through Finch.
- **SIMS-sync guardrail:** kept exactly as-is (§11.3). A Finch-approved receipt creates the
  ripple receipt and updates the collection worklist, same as today's manual upload — it never
  auto-marks the SIMS invoice paid. Bank-transaction matching + an explicit human
  `accounts_approve` sync action remain required before SIMS is touched.

With both open items resolved, this mission is ready to move from analysis to implementation
planning (e.g. GitHub issues in finch-inbox and ripple-suite) whenever Hafiz wants to proceed.

## 13. Memory correction

A prior Koda memory (`mem_5c8e3552bd4b`) claimed Sifu Edu was "being consolidated into Finch from
two legacy sources — Zaapi (CX channels) and Nenji Finance / desk.nenjierp.com (Collection
channel)." This is **incorrect** and has been flagged for review. Verified: "Nenji"/"NenjiERP Desk"
was Finch's own former brand name before its 2026-05-25 rename, not a separate finance system; the
migration brought over only WhatsApp conversation/ticket data from a shared multi-tenant CX
platform, never invoice/collection bookkeeping; `desk.nenjierp.com` is a former developer's
unrelated separate deployment; Zaapi is a competitor product used only for UX benchmarking. No
finance/collection data or logic ever came into Finch from any "Nenji Finance" source — ripple's
`collection`/`customer-receipts` modules have always been fully independent of Finch's history.
