# Kelasapp M4: Billing & Invoicing, Design & Build Plan

> **Status:** Approved 2026-06-27 (brainstorm with Hafiz). Implementation starting.
> **Scope owner:** this doc is the "how we build M4" reference. The PRD (Module 4) is the "what". The live schema in `kelas/src/models/Schema.ts` is the source of truth for tables.
> **Decision protocol:** every choice below was decided one at a time (plain options, how reputable tools do it, recommendation, Hafiz decides).

---

## 1. Locked decisions

| # | Decision | Choice | Why |
|---|---|---|---|
| 1 | M4 first slice size | **Lean manual-first MVP** | Useful day one with zero gateway setup; quarantines the money/auth-sensitive work; matches how MY centers operate (cash + transfer); schema already sized for the full thing so no rework |
| 2 | Who the invoice is addressed to | **Family invoice (one per guardian), lines grouped by child** | Category standard (Jackrabbit Family Account, Teachworks); one bill, one payment, one reminder per parent; siblings share a guardian; adult learners billed directly |
| 3 | How invoices are created | **Manual "Run billing" button, born as drafts; written C-ready so a scheduler is a trivial later add** | No cron infra now; operator stays in control of money the first cycles; same function a scheduler can call later. Overdue is a computed label (no cron) |
| 4 | Amount per line (burn policy) | **Flat monthly fee (always-bill), with manual discounts / adjustments / refunds in the MVP** | Matches Sopan's "burn their slot" rule; simple, trustworthy generation; auto-proration deferred (fields kept). Manual case-by-case deductions ARE supported |
| 5 | Payment recording | **Manual: cash / bank transfer / other; partial + refund supported; gateway deferred** | Direct consequence of decision 1; covers how money is collected today; gateway columns already exist for later |
| 5b | Manual payment proof | **Slice 1: operator attaches the receipt. Slice 1.5: customer self-serves (DuitNow QR + upload page + verification queue)** | Digitises the proof without a real gateway; removes WhatsApp/call friction; uploaded receipt is a CLAIM pending operator verification |
| 6 | LHDN e-invoice fields | **Skipped for MVP** | Already removed from schema to stay multi-country; PRD only ever scoped MyInvois submission as Phase 2 |
| 7 | Teacher pay | **Its own focused slice after the core invoicing slice** | Opposite direction of money, separate audience; reuses the PDF pipeline; needs its own short design; depends on session data that accrues over a cycle |
| 8 | Invoice delivery | **WhatsApp click-to-chat button (wa.me, prefilled, opens the customer's chat) + invoice PDF** | No API/cost/ban risk; one-click is better UX than copy-paste; PRD scoped automated delivery as Phase 2 |
| 9 | finch-lite (WhatsApp in-app) | **Not now. Build M4 behind a thin messaging seam so finch-lite slots in later with no rework** | finch-lite is a stateful WhatsApp gateway (Baileys / Meta Cloud API), bigger than the rest of M4; manual share is the correct day-one fallback; transport choice deserves its own brainstorm |
| 10 | File optimisation | **Central media service: sharp + WebP (thumbnail + view), PDF preview via poppler, stored in Wasabi. Built first** | Prepare early, not later; one place enforces compression so no feature dumps raw multi-MB files |
| 11 | Image library | **sharp (libvips) + WebP**, AVIF/MozJPEG available later | sharp is the Node performance leader; deploy is Hostinger VPS so no serverless limits; CDN offload only if scale ever demands |

---

## 2. Scope: slices

**Slice 1 (core, manual-first, build now)**
- Central media/document service (foundation, built first).
- Manual "Run billing" (generate draft family invoices for the month).
- Invoice lifecycle: draft, issue, partial/full payment, void, refund, manual adjustments/discounts.
- Manual payment recording with receipt attachment.
- Unpaid + overdue lists; per-guardian outstanding.
- Invoice PDF (reuse `@react-pdf`).
- WhatsApp click-to-chat reminder button (behind the messaging seam).
- Fully bilingual (en + ms), operator/staff-gated (teachers excluded).

**Slice 1.5 (next, still gateway-free)**
- Public invoice page (tokenised link) showing the invoice + the org's DuitNow QR + bank details.
- Customer self-service receipt upload on that page.
- Operator verification queue (uploaded receipt = pending payment until verified).

**Slice 2 (later)**
- Teacher pay (compute from `sessions.taughtByTeacherId` x class rate; pay slips).
- Online FPX gateway (FIUU) for instant self-pay + webhook.
- Optional auto-generation scheduler (cron calling the same generation function).

**Deferred / Phase 2+**
- LHDN MyInvois fields + submission.
- finch-lite (in-app WhatsApp send + inbox; Baileys/Cloud API gateway).
- Automated WhatsApp/email delivery, auto-proration, credit balances, recurring auto-debit.

---

## 3. The invoice lifecycle (no dead ends)

States: `draft`, `issued`, `partially_paid`, `paid`, `overdue` (computed label), `voided`.

```
 (generate / create) -> DRAFT -> (discard, never issued)
                          |
                        issue
                          v
                       ISSUED  -> VOIDED (refund if already paid)
                        | ^
            record      | | due date passes with balance > 0 => shown as OVERDUE
            payment     | |  (computed at list time, not a stored flip, no cron)
                        v |
                  PARTIALLY_PAID -> VOIDED
                        |
                  record more
                        v
                      PAID -> (void + refund only if a paid bill is later found wrong)
```

Actions available per state (every state has a next action):
- **Draft:** edit lines, add discount, add adjustment line, discard, issue.
- **Issued / Partially paid / Overdue:** record payment, copy WhatsApp reminder, download PDF, add adjustment/credit, void.
- **Paid:** view, PDF, void + refund.
- **Voided:** view only (terminal on purpose; corrected invoice lives separately).

Edge cases handled: bad line (edit draft, or void+reissue after issue), void a partly-paid bill (record refund), mid-month join (next run / add line / one-off), carry-over across months (each invoice keeps its balance; guardian view sums all unpaid), adult learner (billed directly), all children dropped (no draft, prior unpaid stay visible).

---

## 4. Family invoice model

- An invoice is addressed to a **payer**: normally the **guardian**, or the **student** when there is no guardian (adult learner). Exactly one of `guardianId` / `studentId` is set.
- One invoice per payer per billing month.
- **Line items** carry the child (`studentId` + name snapshot) so the invoice groups lines under each child. A line may also be a non-class **adjustment/discount/credit** (no class link).
- Default presentation: grouped by child (Child A: Quran, Math; Child B: English), then any family-level adjustments.

---

## 5. Generation logic (manual, draft, flat)

1. Operator picks a month and clicks "Run billing".
2. For each guardian (and each guardian-less active student) with **active** enrollments in that month, create ONE draft invoice.
3. One line per active enrollment: `baseAmount` = `enrollment.feeOverride ?? class.monthlyFee`, minus any per-enrollment recurring discount. `itemType = 'tuition'`. Paused/ended enrollments are skipped.
4. **Idempotent:** the per-payer-per-month uniqueness means re-running never double-bills; a second run only adds newly-eligible payers / new lines for an existing draft.
5. Drafts await review. "Issue all" issues the batch (sets `issuedAt`, `dueAt = issuedAt + org.defaultDueDays`). Exceptions are fixed before issuing.
6. Burn policy is `always_bill` (flat). `prorate` fields exist but are unused in MVP.

---

## 6. Manual adjustments / discounts / refunds (always available)

- **Discount on a line:** flat RM or percentage (existing line fields). E.g. "minus RM20 for 2 absences", sibling discount.
- **Adjustment/credit line:** a non-class line with a description and a (possibly negative) amount. E.g. "Goodwill credit -RM10". Requires line item class/enrollment nullable.
- **Refund:** a `kind = 'refund'` payment recorded against an invoice when money already received must go back. Net received = verified payments minus refunds.
- All of these write to `invoice_events` (who, what, why) and recompute the invoice total / balance.

---

## 7. Payment recording

- Methods: `cash`, `bank_transfer`, `other` (gateway methods reserved for later).
- Form: amount (defaults to remaining balance), date received, method, reference, note, optional **receipt attachment**.
- Partial payments accumulate (`partially_paid`); over-the-balance amounts are warned and capped (no negative-owed in MVP).
- Only **verified** payments count toward `paidAmount`. Operator-recorded payments are `verified` immediately. Self-service uploads (slice 1.5) are `pending` until an operator verifies.
- Operator / staff only. Teachers never see payments.

---

## 8. Self-service payment page (slice 1.5)

- Each invoice has a hard-to-guess **public token**; the link is what the WhatsApp button shares.
- Public page (no login) shows: the invoice (read-only), the org's **DuitNow QR** image, and **bank transfer details**.
- After transferring, the parent **uploads their receipt** (image or PDF) on the same page.
- Upload creates a `pending`, `self_service` payment with the receipt attached. It appears in the operator's **verification queue**; verifying it makes it count.

---

## 9. Delivery + the messaging seam

- **Messaging seam:** one small interface, e.g. `MessagingProvider.composeInvoiceMessage({ to, link, invoice })`. Slice 1 implementation = **WaMeProvider** (builds a `https://wa.me/<msisdn>?text=<encoded>` click-to-chat link). finch-lite later adds a provider that actually sends and receives, with no change to billing code.
- **Phone normalisation:** guardian phone normalised to MY international form (`60XXXXXXXXX`, digits only, drop leading 0) when building the link. One helper, reused.
- **Buttons:** on the invoice and on each unpaid/overdue row (one tap per family).
- Limitation (by design): opens a prefilled draft, operator taps send; no auto-send, delivery receipt, or inbound capture (that needs the gateway). The self-service page covers the return path (receipts).

---

## 10. Central media/document service (built first)

- Single helper every upload in the app goes through (receipts, DuitNow QR, future logos/photos).
- **Images** (jpeg/png/webp/heic): validate real type by content, resize (long edge ~1600px), convert to **WebP**, strip metadata, make a **thumbnail** (~200px) + a **view** size. iPhone HEIC supported (VPS libvips built with libheif).
- **PDFs** (bank receipts): validate + size-cap + store as-is (already small); render a **first-page preview** image (poppler `pdftoppm`) then thumbnail it via sharp, so the queue shows a preview without downloading.
- **Storage:** Wasabi (S3-compatible), **private** bucket, random object keys under the org namespace, served via short-lived signed URLs. Never public, never executed inline; PDFs served with safe content-disposition.
- **Engine:** sharp (libvips) + WebP. AVIF/MozJPEG available later. CDN offload only if scale demands (we store small files so likely never needed).
- Generated PDFs (invoices/reports) embed only the optimised logo/QR, staying lean.

---

## 11. Teacher pay (slice 2, own design)

- Compute payable sessions per teacher per period from `sessions.taughtByTeacherId` (substitutes flow through it), times `classTeachers.rateOverride ?? classes.teacherRatePerSession`.
- Cancelled sessions excluded. Produce a pay summary + pay slip PDF (same pipeline).
- New schema (its own slice): a `teacher_payouts` concept (period, computed amount, status, paid date). Designed when we start the slice.

---

## 12. Planned schema deltas (slice 1 + 1.5)

Source of truth stays `Schema.ts`; this is the plan for migration `0007`.

**invoices**
- add `guardian_id uuid` (nullable) FK guardians.id
- make `student_id` nullable (adult-learner payer)
- add `public_token text` (unique, for the shareable link)
- replace unique `(org, student, month)` with two partial uniques: `(org, guardian_id, billing_month)` where guardian set; `(org, student_id, billing_month)` where guardian null
- app-level invariant: exactly one of guardian_id / student_id set

**invoice_line_items**
- make `enrollment_id`, `class_id`, `class_name` nullable (for non-class adjustment lines)
- add `student_id uuid` (nullable) FK students.id + `student_name text` snapshot (which child)
- add `item_type text` default `'tuition'` ('tuition' | 'discount' | 'adjustment' | 'credit')
- add `description text` (for adjustment/credit lines); `line_total` may be negative

**payments**
- add `kind text` default `'payment'` ('payment' | 'refund')
- add `status text` default `'verified'` ('pending' | 'verified' | 'rejected'); only verified counts
- add `source text` default `'operator'` ('operator' | 'self_service')
- add `receipt_file_id uuid` (nullable) FK media_files.id
- extend method set conceptually with `'duitnow'`

**org_settings**
- add `duitnow_qr_file_id uuid` (nullable) FK media_files.id
- add `bank_name text`, `bank_account_number text`, `bank_account_holder text`

**media_files (new)**
- `id, org_id, kind ('receipt'|'duitnow_qr'|'logo'|'other'), original_name, mime_type, byte_size, storage_key, thumbnail_key, width, height, uploaded_by, created_at`
- indexes (org_id), (org_id, kind)

**invoice_events**: no schema change (free-text `event_type`); new types used: `payment_submitted`, `payment_verified`, `payment_rejected`, `refunded`, `adjusted`, `reminder_copied`.

---

## 13. Build order (slice 1)

1. Deps + Env: add `sharp`, `@aws-sdk/client-s3`, `@aws-sdk/s3-request-presigner`, `file-type`; add Wasabi env vars to `Env.ts`. (poppler is a system binary on the VPS.)
2. Schema deltas + migration `0007` + reconcile `DATA-MODEL.md`.
3. Central media service + tests.
4. Messaging seam + WaMeProvider + phone-normalise helper + tests.
5. Invoicing service (generate, issue, record payment, void, refund, adjust, totals, overdue, outstanding) with TDD vertical slices.
6. Invoicing API routes (operator-gated via `requireOperatorContext`).
7. Invoice PDF.
8. UI: billing home (run billing, drafts, unpaid, overdue), invoice detail, record-payment + receipt, WhatsApp button, guardian billing view.
9. i18n keys (en + ms).
10. Smoke test (navigate + screenshot + console) and verify (tsc + lint + tests).

The M4 feature code lives under `src/features/invoicing/` (the existing `src/features/billing/` is boilerplate marketing pricing UI, left untouched).

**Formatting rule (whole app):** all user-facing dates/times/money use Malaysian formats via `src/utils/Format.ts` (`formatDate` DD/MM/YYYY, `formatDateTime` Asia/KL 12-hour, `formatMonth`, `formatMoney` RM). Never US (`en-US`, month-first). Storage stays ISO/timestamptz.

---

## 14. Test plan (key cases, TDD)

- Generate creates one draft per guardian; a 2-child guardian gets one invoice with lines grouped by child.
- Paused/ended enrollment produces no line; re-running generation is idempotent (no duplicates).
- Adult learner (no guardian) is billed directly.
- Issue sets due date = issued + org default; "issue all" issues the batch.
- Partial payment => partially_paid with correct balance; full coverage => paid.
- Overpayment is capped/warned.
- Refund reduces net received; voiding a partly-paid invoice requires/records the refund.
- Manual discount + adjustment/credit line recompute totals; negative line allowed.
- Overdue is correctly derived (issued/partial past due) without a stored flip.
- Outstanding per guardian sums all unpaid across months.
- Tenant isolation: an invoice from org A is never visible to org B.
- Media: oversized/wrong-type rejected; image normalised to WebP with thumbnail; HEIC converted; PDF gets a preview; signed URL required to fetch.
- wa.me link: phone normalised to 60-form; message URL-encoded.
