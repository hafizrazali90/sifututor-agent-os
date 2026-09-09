# Kelasapp QA Test Catalog

> The exhaustive, human-runnable, E2E-convertible test catalog for Kelasapp. Built by applying
> the method in [QA-METHODOLOGY.md](QA-METHODOLOGY.md) to every module, grounded in the real code +
> the unit/integration tests (151 as of this revision) + [FLOWS.md](../FLOWS.md).
> First assembled: 2026-06-30. **Fully revised: 2026-07-04** against `feat/finish-mvp-polish`
> (the catalog predated the Better Auth migration of 2026-07-02 and the 43-commit MVP polish pass;
> every module was re-grounded, stale cases rewritten in place, new features covered, and a new
> import module added).
>
> **701 test cases across 10 modules; 90 in the @smoke go/no-go subset.**

## How to use

- **Manual run:** open the module file, run each case top to bottom, fill "What you actually saw" and
  set Status (Pass / Fail / Blocked / Skipped). Each case is self-contained: a non-technical tester
  can run it without prior knowledge (it says how to find its own data, no hardcoded IDs).
- **Release gate:** run the `@smoke` subset first (fast go/no-go). Then T1, then T2/T3 by time.
- **As the E2E source:** each case maps 1:1 to a `browser-test` YAML case (see methodology §7), so the
  same list becomes the automated suite that "tests like a human" (navigates, types, clicks, looks).

## Coverage matrix (revised 2026-07-04)

| Module | File | Cases | @smoke | Default tier |
|---|---|---:|---:|---|
| Billing & Invoicing | [test-plan-billing.md](test-plan-billing.md) | 61 | 6 | T1 |
| Teacher pay (payroll) | [test-plan-teacher-pay.md](test-plan-teacher-pay.md) | 60 | 9 | T1 |
| Auth, roles & tenancy | [test-plan-auth-tenancy.md](test-plan-auth-tenancy.md) | 75 | 13 | T1 |
| Classes + Taxonomy | [test-plan-classes.md](test-plan-classes.md) | 90 | 9 | T2 |
| People (students/guardians/enrolments) | [test-plan-people.md](test-plan-people.md) | 74 | 8 | T2 |
| Attendance + Reports | [test-plan-attendance.md](test-plan-attendance.md) | 65 | 11 | T2 |
| Teachers | [test-plan-teachers.md](test-plan-teachers.md) | 85 | 6 | T2 |
| Data import (wizard + migration hub) | [test-plan-import.md](test-plan-import.md) | 53 | 8 | T2 (T1 on billing-adjacent rows) |
| Operator Dashboard | [test-plan-dashboard.md](test-plan-dashboard.md) | 60 | 11 | T3 |
| Cross-cutting (validation/i18n/theme/PII/responsive/a11y) | [test-plan-crosscutting.md](test-plan-crosscutting.md) | 78 | 9 | mixed |
| **Total** | | **701** | **90** | |

Each file walks the §5 technique matrix (happy, boundary, negative + server-side bypass, permissions,
cross-tenant/IDOR, state transition, idempotency, format/locale, empty/error states, data integrity,
a11y, security) and ends with a coverage note listing techniques applied, rows skipped with reason,
and the 2026-07-04 revision delta (cases rewritten/added with commit provenance).

## What the 2026-07-04 revision covered

The original catalog was assembled hours before two large batches landed, so it described a
Clerk-era app. The revision re-grounded every case against `feat/finish-mvp-polish` HEAD:

- **Better Auth migration (Jul 2):** first-party sign-in/sign-up, password reset, email flows,
  link-based invites with roles, teacher self-service (my-classes, my-pay, own payslip),
  owner-only gates, membership-row denial. Auth plan rewritten 40 -> 75 cases.
- **Invoicing lifecycle changes:** payment claims -> pending verification -> verify/reject,
  recoverable void that cannot strand money, all-or-nothing Run Billing with unique invoice
  numbers, receipt fix/replace, per-row WhatsApp/copy-link share.
- **Payroll:** bulk mark-paid with per-teacher failure reporting, teacher My Pay status.
- **UX/CX audit output (CX1-CX16 + LOW batch):** toasts, empty states, dark mode, BM terminology,
  44px touch targets, phone-width fixes, onboarding pull-through, migration hub.
- **Table usability pass:** # column, range-of-total, all-column search, CSV export, 25-row default.
- **New module:** the class/enrolment/people CSV import wizard + /dashboard/import hub (zero
  coverage before; 53 new cases).

## Release exit criteria

- **Staging deploy:** all T1 `@smoke` pass.
- **Production gate:** all **T1** pass (money: billing + teacher pay; auth + tenant isolation;
  import rows that can double-bill).
- T2/T3 tracked, not blocking. Any new bug found: add a `REGRESSION:` case (append-only) before the fix.

## Findings triage

### Original findings (2026-06-30) status after re-triage on 2026-07-04

1. **Staff role is not gated** - **CLOSED as official policy (2026-07-04).** Hafiz decided: staff =
   full operational access including taxonomy and payroll; owner-only = business/invoicing/payment
   settings + member management. `auth-permissions.ts` now states exactly that (separate taxonomy
   key, f29ee0b); enforcement stays in Access.ts. The old table/route contradiction is gone.
2. **Class update skips the capacity refine** - **RESOLVED.** 55f4251 removed `capacityMin` and the
   refine entirely; `classUpdateSchema` bounds now match create (TC-CLS-083 rewritten).
3. **PII masking is client-side only** - **FIXED `b498d68` (2026-07-04).** Server-side masking: pages
   ship only the masked tail (utils/Mask.ts); the eye toggle fetches the full value from
   operator-gated /sensitive endpoints. Browser-verified: full IC absent from served HTML.
   (TC-TCH-084, TC-PII-001 rewritten to assert it.)
4. **Report export date format** - **RESOLVED BY CONVENTION.** 55f4251 unified exports onto the shared
   `formatDateLong`; UI-CONVENTIONS.md now documents the two-format convention (long "1 Jun 2026"
   for printed/exported docs, DD/MM/YYYY on-screen). **Residual i18n gap:** the report period line
   calls `formatDateLong` without a locale, so BM reports/PDF/CSV show English month names
   (TC-RPT-041 notes it).
5. **Zero teacher rate renders as a dash** - **FIXED.** 55f4251: saved RM 0 shows `RM0.00`; the dash
   appears only when the rate is unset (TC-CLS-035 rewritten).

### New findings surfaced by the 2026-07-04 revision

Triage ran the same day and is COMPLETE: six were clear defects fixed immediately; the five
product questions were decided one-by-one with Hafiz and their fixes shipped the same day
(all gates green, browser-verified). Only accepted i18n residuals remain (item 8).

1. **Invoice adjustment sign contradiction** (TC-BILL-040): **FIXED `70edbfa`.** The client schema
   now mirrors the server contract (any nonzero amount); a -10 adjustment browser-verified to
   reduce the total.
2. **CSV export formula injection** (TC-IMP-052, @security): **FIXED `421bbac`.** Shared
   formula-guarded `csvCell` (`src/utils/Csv.ts`, unit-tested) used by both the list-table export
   and the report CSV writer; numbers, RM money, and the dash placeholder stay untouched.
3. **Import API 500 on malformed JSON** (TC-IMP-043): **FIXED `380a374`.** Malformed bodies now
   return the same 422 Invalid input as a wrong shape; verified against the running API.
4. **Students list shows archived class names** (TC-STU-103): **FIXED at the root `667eecb`
   (2026-07-04).** The real trap was that archiving never stopped billing: Run Billing invoices
   active enrolments regardless of class status. Archiving is now REFUSED while non-ended
   enrolments exist (409 + dialog message, TDD service test, browser-verified); the column stays
   enrolment-driven by design (new TC-CLS-151).
5. **Pending badge vs card divergence risk** (dashboard plan section K): **FIXED `f406a4c`.**
   `countPendingPayments` now uses the queue's self-service filter, so the badge can never
   disagree with the queue it links to; service-tested.
6. **Network failures bypass error handling in row actions** (TC-ENR-044 note, TC-CLS-146 note):
   **FIXED `c679357`.** The shared confirm dialog catches a thrown fetch and shows the standard
   try-again message instead of hanging on its busy label.
7. **Own draft payslip fetchable by URL** (TC-PAY-128): **FIXED `346b4d5` (2026-07-04).** Teachers
   download payslips only once marked paid; drafts 404 like any non-owned payout. Operators still
   preview drafts.
8. **Hardcoded-English residuals**: **PARTLY FIXED `17cc0ed`** (report period line now formats in
   the request locale, trend tooltip translated). Still open: calendar weekday row Mo..Su
   (TC-I18N-009 note) and import server warning strings + row-error codes (TC-IMP-050).
9. **Public pages are light-theme only for anonymous browsers** (TC-THEME-004): **FIXED `4fe0ace`
   (2026-07-04).** A pure-CSS force-light scope pins the public invoice pages to the light theme
   for every viewer; the stored preference and the dashboard are untouched. Browser-verified in
   dark mode.

## E2E status: the FULL catalog is AUTOMATED through T2 (2026-07-04)

**548 Playwright cases, all green** against a fresh in-memory database on port 3008 (never the dev
DB): all 90 `@smoke` (`kelas/tests/e2e/smoke/`), all 149 non-smoke T1 (`kelas/tests/e2e/t1/`), and
all 309 non-smoke T2 (`kelas/tests/e2e/t2/`, 11 specs incl. people split students / guardians+
enrolments, auth split a/b). Only the ~153 T3 display-polish cases remain unautomated (visual
tier, better as the manual pass). Test titles carry the catalog TC ids. Run with the dev stack
STOPPED (both want port 5432): `npx playwright test tests/e2e/`.

T2 conversion surfaced one real (minor) app defect, fixed in-flight (`7539c66`): the pay-run and
billing period schemas accepted an impossible month like "2026-13", which then crashed generation
with a 500 instead of a clean 422; both now constrain the month to 01-12.

Design + adapted-assertion notes (all commented inline where they occur):
- Every spec signs up its own centre through the real UI; emails land in a file-sink inbox
  (EMAIL_FILE_SINK) so reset-token journeys are testable; 1 worker (in-memory PGlite is
  single-writer); BETTER_AUTH_URL pinned to the test origin.
- Dev-mode `notFound()` returns HTTP 200, so page cases assert the "Page not found" heading; API
  status contracts stay strict.
- RM amounts carry a non-breaking space: string matchers, never space-regexes.
- Removed-member denial cases assert the API BEFORE the page visit (the onboarding bounce clears
  the active org and changes the 401 message).
- Money-fee decimal rejection asserts form-blocked + API 422 (native step vs zod fires
  browser-dependently); recharts tooltip reads dropped as flaky; report CSV Overall row is last.
- A `/ms` visit sets the NEXT_LOCALE cookie: specs that switch language reset it per test.

Removed the three dead starter-template specs (I18n/Sanity/Visual, French + boilerplate copy).
Next per methodology §7: T2 conversion (post-beta), then formalise the `qa-plan` skill (§11).
The catalog stays the single source for both manual QA and E2E.
