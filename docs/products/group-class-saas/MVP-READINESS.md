# Kelasapp — Final MVP-Readiness Audit (2026-07-02)

> Deep pre-beta audit run with a 4-agent parallel code sweep (API auth/tenancy, Better Auth
> surface, UI journey completeness, money/data integrity) + an ops-readiness pass, reconciled and
> spot-verified against source. Scope: everything that gates handing Kelasapp to **Sopan** (first
> real centre, migrating from Mudeer). **Already-deferred items are excluded** (M7 AI, Stripe/billing
> enforcement, CSV export, rate limiting, marketing-copy reframe, LHDN, gateway, super-admin).
>
> Method: agents were told to verify-before-flagging and cite `file:line`; the four HIGH findings
> and the sidebar issue were independently re-read against the code before writing this.

## Verdict

**No blockers. The MVP is functionally complete and structurally sound.** Production build passes;
money is summed in integer cents everywhere; every service query is org-scoped (no cross-tenant read
or write found by any agent); status transitions, payroll idempotency, rate-freezing, PDF scoping,
and the public token surface are all clean; the old Clerk email-guess role footgun is genuinely gone.

> **UPDATE 2026-07-03: all 4 HIGH + the entire MEDIUM cluster (M1–M9) + both ops items are FIXED,**
> committed on `feat/finish-mvp-polish`, each TDD'd and/or browser-verified, with the production
> build green. See the resolution notes inline below and the 2026-07-03 BUILD-LOG entry. The only
> deferred items now are the LOW tier and the QA-catalog refresh (part of the testing phase).

---

## HIGH — fix before Sopan's beta (4) — ✅ ALL FIXED 2026-07-03

- **H1** ✅ `2b53ee7` — `resolveMemberRole` throws when the membership row is absent (removed member denied); browser-verified.
- **H2** ✅ `a39c059` + `c1ee98d` — the whole payment-flow package: submit caps amount at balance, `verifyPayment` re-checks balance, per-invoice outstanding clamp, admin **Remove payment**, plus status badges + inline verify/reject and the void-with-money guard; browser-verified EN+BM.
- **H3** ✅ `f31491a` — `markAttendance` rejects marks for students not on the class roster (`not_on_roster`); TDD.
- **H4** ✅ `f31491a` + `a5d67a2` — `Email.ts` refuses to log reset links in production; `assertProductionEnv()` (from `instrumentation.ts register()`) blocks a prod boot without the mailer.

| # | Finding | Evidence | Failure scenario | Fix |
|---|---------|----------|------------------|-----|
| H1 | ✅ **FIXED 2026-07-02 (`2b53ee7`).** Removed member silently defaulted to `staff` (`Access.ts` `toAppRole(m?.role)`; no membership row ⇒ `'staff'`). Now `resolveMemberRole` throws `OrgRequiredError` when the membership row is absent → onboarding redirect / 401. Pure role logic extracted to `access-role.ts` + unit-tested; browser-verified (removed member redirected to onboarding, valid member unaffected). | — | — | — |
| H2 | **`verifyPayment` has no `exceeds_balance` guard** | `service.ts:539-554` (verify has only a `status==='pending'` check) vs `service.ts:316` (record blocks `paid+amount > total`). Public submit has no amount ceiling (`submit/route.ts:20,31`). | Parent submits RM 600 self-service against a RM 100 invoice (typo/overpay); operator taps Verify. Invoice goes `paid` with `paidAmount=600`; `guardianOutstanding` clamps the aggregate to RM 0, **masking the RM 300 the family still owes on another invoice**. | Add the same balance cap to `verifyPayment`; bound the public submit with a zod schema (max amount, 2dp, reference length). |
| H3 | **Attendance marks not checked against roster/org** | `attendance/service.ts:377-404` inserts a record per `m.studentId` straight from the body; `markAttendanceSchema` only checks UUID shape. `presentCount` (no enrollment join) freezes the per-student pay snapshot → payout. | A teacher of a per-student-pay class POSTs extra valid student UUIDs as `present`, inflating `presentCount` → their own frozen session pay → payout. Foreign-org UUIDs also insert as orphan rows (stamped with the actor's orgId). | Validate each mark's `studentId` is enrolled in that class (and in the org) before insert. |
| H4 | **`Email.ts` prod fallback logs reset links** (conditional on deploy) | `src/libs/Email.ts:18-22` — if `RESEND_API_KEY` is falsy it `logger.warn`s the full email body (the reset link + single-use token) and returns success, no `NODE_ENV` guard. `Env.ts:12` marks the key optional with no prod assertion. | If prod is ever deployed without `RESEND_API_KEY`, every forgot-password writes a working account-takeover link to the server logs + Better Stack sink while the user sees "sent" — and nothing fails to signal the misconfig. | Hard-fail (or refuse to log the body) when `NODE_ENV==='production'`; assert `RESEND_API_KEY` present in prod in `Env.ts`. |

---

## MEDIUM — ✅ ALL FIXED 2026-07-03

- **M1** ✅ `c1ee98d` — void refuses while an invoice holds verified money (remove/refund first); a mistaken void is recoverable (rebill mints a fresh invoice, migration 0015); Refund made discoverable.
- **M2** ✅ `e86b941` — DatePicker/MonthPicker render month names in the active language (Julai/Ogos, grid Jan..Dis); browser-verified BM.
- **M3** ✅ `31777bd` — issue/void-payout/archive/end-enrolment surface failures instead of failing silently.
- **M4** ✅ `6ddce23` — `generateInvoices` is one transaction; unique invoice-number index (migration 0016).
- **M5** ✅ `3cddbee` — public submit rejects oversized bodies before buffering, caps file/reference/amount.
- **M6** ✅ `3cddbee` — invite activates the accepted org (not a guess); centre switcher for multi-centre users; browser-verified.
- **M7** ✅ `31777bd` — public invoice page has a loading skeleton.
- **M8** ✅ `e86b941` — "Powered by" localized on the public page + 3 PDFs (Dikuasakan oleh).
- **M9** ✅ `e86b941` — sidebar uses the locale-aware Link; browser-verified BM stays on /ms.
- **Ops-1** ✅ `99e4d05` — `.env.local.example` rewritten for Better Auth (Clerk keys removed).
- **Ops-2** ✅ `f31491a` + `a5d67a2` — `NEXT_PUBLIC_SENTRY_DSN` validated + required at prod start.

<details><summary>Original MEDIUM detail (for history)</summary>

| # | Finding | Evidence | Note |
|---|---------|----------|------|
| M1 | **`voidInvoice` with verified payments strands money** | `service.ts:396-411` — void only flips status; no recompute, no refund, no guard. `dashboard/service.ts:109` drops the paidAmount from "collected" while `:160` still lists the payment. A pending payment can still be verified onto a voided invoice. | Two dashboards disagree; received cash silently leaves the collected series. |
| M2 | **BM users see English month names** | `ui/DatePicker.tsx:106,111` and `ui/MonthPicker.tsx:54` hardcode `toLocaleDateString('en-MY', …)`. | Every date field + the billing/payroll month selectors show "August 2026" not "Ogos" for BM operators — directly hits Sopan if he runs BM. `Format.formatMonth(value, locale)` already exists. |
| M3 | **Silent fetch failures on money paths** | `InvoiceActions.tsx:101` (issue), `:480` (void); `PayoutActions.tsx:59` (void payout); `PendingActions.tsx:14` (verify/reject); `RowActions.tsx:113` (delete/archive callers). No `res.ok` check → dialog closes, refresh, nothing shown. | A failed action (FK block, closed window, 500) is invisible. Good error-handling pattern already exists elsewhere in the codebase (`AttendanceSheet`, `EnrollPanel`, `PaymentSheet`); just not applied here. |
| M4 | **`generateInvoices` not transactional; `invoiceNumber` not unique-indexed** | `service.ts:173-255` inserts per-invoice with no wrapping transaction; number from a live `COUNT` (`:56`); only `publicToken` has a unique index (`Schema.ts:319`). | Concurrent "Run billing" can mint duplicate numbers / 500 mid-run. Single-user safe today. Wrap in a transaction; add a unique index. |
| M5 | **Public submit unvalidated; upload buffered before size cap** | `submit/route.ts:19-33` — no zod, unbounded `reference`, no amount ceiling. `media/service.ts:82` checks 10MB only after `Buffer.from(await file.arrayBuffer())`. Token-gated but unauthenticated. | Robustness/DoS hardening; idempotency + org-from-token are already correct. Overlaps H2's schema fix. |
| M6 | **`AcceptInvite` overrides the correct active org** | `AcceptInvite.tsx:33-37` — after accept, calls `organization.list()` + `setActive(list[last])`, but `acceptInvitation` already set the correct org server-side and list order isn't guaranteed. | A multi-org user accepting an invite can land in the WRONG centre's dashboard. Drop the manual `list`/`setActive`. |
| M7 | **No `loading.tsx` for the public invoice route** | `invoice/[token]/` has none; it does sequential awaits (invoice + up to 2 media URLs). | Parents see a blank beat on a slow open. |
| M8 | **Two hardcoded user-facing strings** | `"Max:"` (`InvoiceActions.tsx:275`), `"Powered by"` (`invoice/[token]/page.tsx:176`, the parent-facing page). | BM users see English. |
| M9 | **Sidebar uses plain `next/link`** | `Sidebar.tsx:7` (every primary nav item) vs the localized `Link` from `@/libs/I18nNavigation` used by 50+ other files. With `localePrefix:'as-needed'`. | A BM operator's core navigation round-trips back toward EN. One-line import swap. |

</details>

---

## LOW / polish (deferred — still open)

- `media/upload` returns internal `thumbnailKey` (private bucket, signed-URL only — minor info exposure).
- Client-supplied `receiptFileId`/`logoFileId`/`duitNowQrFileId`/adjustment `studentId` not ownership-checked at write time (FKs guarantee existence; every read is org-scoped, so a foreign id resolves to null/blank — dangling ref only, no leak).
- Soft-delete filter (`isNull(deletedAt)`) missing on a few queries — **currently harmless because nothing ever writes `deletedAt`**; `findInvoiceForPayer` (`service.ts:146`) + the payer-month partial unique index are the ones to fix when soft-delete is actually wired.
- Page reload generates a fresh self-service `idempotencyKey`, so a reload+resubmit makes a second pending payment (operator verifies, so bounded).
- Teacher auto-link: duplicate-email picks arbitrarily; an inactive teacher record silently yields `teacherId=null` (empty my-classes/my-pay, blocked attendance). Both benign/self-correcting.
- Guest-controlled `idempotencyKey` is org-unique not invoice-unique (self-inflicted only).

## Ops / hygiene (pre-deploy)

- **`.env.local.example` is stale** — still documents `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` / `CLERK_SECRET_KEY` and omits `BETTER_AUTH_SECRET`/`BETTER_AUTH_URL`/`RESEND_API_KEY`/`EMAIL_FROM`/`WASABI_*`. Update to match `Env.ts` so the VPS deploy doesn't chase phantom Clerk vars.
- **Sentry DSN unvalidated** — `instrumentation*.ts` reads `NEXT_PUBLIC_SENTRY_DSN` but it isn't in `Env.ts` (still LAUNCH-READINESS D1). Add it + set the DSN at deploy so prod isn't blind during the riskiest phase.
- **QA catalog is stale post-migration** — 4 plans reference Clerk (`test-plan-auth-tenancy.md` ×17, attendance ×4, teachers ×3, classes ×1). Refresh before using the 486-case catalog as the E2E source.
- **Deploy artifacts not built** — no Dockerfile / process manager config yet; expected, but it's the gap between "build passes" and "running on the VPS."

## What came back CLEAN (so it isn't re-audited later)

- No cross-tenant read or write on any of 34 API routes; no route trusts a client-supplied `orgId`/`userId`/`teacherId`; no error response leaks stack/SQL.
- Owner-gating correct on the three money-routing settings; payslip/invoice PDFs org- and role-scoped; a teacher cannot fetch another teacher's payslip.
- Money math is integer-cents throughout; refunds can't exceed paid; no double-issue/double-verify; payroll re-run can't double-pay (partial unique index) and never touches a paid payout; rate frozen at attendance time.
- Public invoice token: 144-bit, unique-indexed, exposes only the payer's own line items + org pay details — **no guardian phone, no other children, no payment history**; media `kind` hardcoded to `receipt` on the public path.
- Better Auth: role assigned on membership (footgun gone), invite email-mismatch + double-accept + expiry enforced server-side, invitationId cryptographically random, reset/verify tokens single-use + time-limited, no account enumeration, no open redirects, sign-out revokes server-side, org switch re-verifies membership.
- i18n: EN/BM key parity exact (978 = 978), zero em dashes in copy, disciplined `Format.ts` on page-level money/dates, actionable empty states, model disabled-button affordances, consistent kebab/action-bar system.

---

## Recommended sequence

1. **HIGH tier (H1–H4)** — the security/money-visibility set. TDD each; browser-verify H2/H3. ~half a day.
2. **MEDIUM money + BM-facing (M1, M2, M3, M9)** — the ones a real beta operator/parent actually hits. ~half a day.
3. **MEDIUM robustness (M4–M8)** + ops hygiene (env example, Sentry DSN). ~half a day.
4. Refresh the 4 stale QA plans, then freeze → E2E on the now-verified journeys → Sopan private beta.
