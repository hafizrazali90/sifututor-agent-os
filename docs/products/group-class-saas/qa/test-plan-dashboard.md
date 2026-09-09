# Test plan: Operator Dashboard (M6)

> Exhaustive manual catalog for the operator dashboard. Format + method: [QA-METHODOLOGY.md](QA-METHODOLOGY.md).
> Grounded in `src/features/dashboard/service.ts`, its 5 service tests (`service.test.ts`),
> `src/app/[locale]/(auth)/dashboard/(operator)/page.tsx`, `dashboard/layout.tsx`, the
> `ClassHealth` / `RecentPayments` / `BillingTrendChart` / `Sidebar` / `TitleBar` components,
> `src/features/attendance/service.ts` (`getAbsenceAlerts`, `getAttendanceRatesByClass`),
> `src/features/onboarding/service.ts` + `GettingStartedChecklist.tsx` (+ its 4 service tests),
> `src/features/invoicing/service.ts` (`countPendingPayments`, `listPendingPayments`),
> and [FLOWS.md](../FLOWS.md) §6.
> Default tier **T3** (display / aggregation). Cases where the figures must reconcile with the
> underlying data are raised to **T2** (a wrong number on a money/attendance card is a real defect,
> not a cosmetic one). Roles: operator (sees the dashboard), teacher (redirected away, no access).
> Auth is Better Auth (roles are assigned on the org membership); no case depends on Clerk.
> Last updated: 2026-07-04 (post-catalog commits de4be04, 63c3365, 8da4c9e, 91a3820, 4580941,
> b6f474d, e86b941 folded in).
>
> Smoke subset (@smoke): TC-DASH-001, 010, 020, 021, 030, 040, 070, 080, 090, 092, 093.

---

The dashboard reads only; nothing here mutates data (the checklist dismiss writes a browser-local
flag only). The risk it carries is a **false number**: a KPI that shows a stale, cross-org, or
miscomputed figure, or a section that hides instead of showing an empty state. Every "What you
should see" below names the exact observable so a tester cannot false-pass on a plausible-but-wrong
figure. Set up data via the other modules (Classes, People, Billing, Attendance) first, then read
the dashboard at `/dashboard`.

Dev logins (local/dev environment): operator `operator@kelastest.local` / `newpassword6789`;
teacher `teacher@kelastest.local` / `password12345`.

**Empty-org gate (new since the 2026-06-30 catalog)**: a brand-new org (no teacher, class,
enrolment, or issued invoice) does NOT render the KPI cards, trend, queues, or class-health grid.
It shows only the "Getting started" checklist (see section L). Any case below that needs the KPI
row in a near-empty org must first make the org non-empty, e.g. by adding one teacher.

## A. KPI cards: counts

### TC-DASH-001: Active students card counts only active students in this org
**Tags**: @smoke @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: M6 KPI (active students) | **Risk**: stale/cross-org count | **Type**: Feature
**Before you start**: Log in as operator. In Students, count the rows whose status is Active (note the number, call it N). Make sure at least one student exists with a non-active status (Dropped) so the filter is being exercised; if none, open a student and set status to Dropped first.
**Test Data**: N = your counted active-student total.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Read the "Active students" KPI card value |
**What you should see**: The card shows exactly N (the count of `status = active` students for this org). Dropped students are NOT counted. The value is a whole number, not RM.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-DASH-002: Active classes card counts only active (non-archived) classes
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: M6 KPI (active classes) | **Risk**: archived class leaks into count | **Type**: Feature
**Before you start**: Operator. In Classes, count the classes that are NOT archived (call it C). Confirm at least one class is archived; if none, archive one first.
**Test Data**: C = your counted active-class total.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Read the "Active classes" KPI card value |
**What you should see**: The card shows exactly C. Archived classes are excluded (matches `getDashboardStats`: `classes.status = active`).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-003: Active counts read zero in a minimally set-up org (no stale / cross-org number)
**Tags**: @regression @data-integrity @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: M6 KPI | **Risk**: cross-tenant figure shown | **Type**: Feature
**Before you start**: Sign in as operator to a brand-new org and add exactly ONE teacher (Teachers > New teacher, name `Ustaz Ali`) and nothing else: no students, no classes. The teacher makes the org non-empty so the KPI row renders at all (a totally empty org shows only the checklist, see TC-DASH-099). Another org in the system DOES have students and classes.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard as this org |
| 2 | Read "Active students" and "Active classes" |
**What you should see**: Both cards show `0`, NOT the other org's numbers and NOT a blank. (Reconciles with the `org_EMPTY` service test: activeStudents may be > 0 only if that org itself has them; it never inherits another org's totals.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## B. KPI cards: outstanding (money)

### TC-DASH-010: Outstanding sums issued + partially-paid balances only
**Tags**: @smoke @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T2
**Linked**: M6 KPI (outstanding) | **Risk**: wrong money figure | **Type**: Feature
**Before you start**: Operator. In Billing, set up for the org: one Issued invoice of RM 100.00 with nothing paid; one Partially-paid invoice with total RM 100.00 and RM 40.00 paid (balance RM 60.00); one fully Paid invoice RM 50.00; one Voided invoice RM 80.00. (This mirrors the service test fixture D1-D4: expected outstanding = 100 + 60 = RM 160.00.)
**Test Data**: expected outstanding = RM 160.00; expected unpaid count = 2.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Read the "Outstanding" KPI card value and its sub-line |
**What you should see**: Card shows `RM 160.00` (the sum of `totalAmount - paidAmount` over issued + partially-paid invoices). The Paid (50) and Voided (80) invoices contribute nothing. The sub-line states 2 unpaid invoices.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-011: Outstanding ignores fully-paid and voided invoices
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T2
**Linked**: M6 KPI (outstanding) | **Risk**: paid/void counted | **Type**: Feature
**Before you start**: Operator. Note the current Outstanding figure. Pick an Issued invoice contributing to it (note its balance B). Record a full payment so it becomes Paid; then on another contributing invoice, Void it (note balance V).
| Step | Action |
|------|--------|
| 1 | Note Outstanding before any change |
| 2 | Fully pay one contributing invoice, then void another |
| 3 | Reload /dashboard and read Outstanding |
**What you should see**: Outstanding drops by exactly B + V. A Paid invoice and a Voided invoice each contribute RM 0.00 (status no longer in issued/partially_paid). No negative or stale figure.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-012: Outstanding reconciles with the unpaid-invoices queue total
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: M6 KPI + unpaid queue | **Risk**: card disagrees with list | **Type**: Feature
**Before you start**: Operator in an org with at most 6 unpaid invoices (so the queue shows all of them, not a "view all" subset).
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Read the Outstanding card |
| 3 | Sum the balance figures shown in the "Unpaid invoices" queue card |
**What you should see**: The Outstanding card equals the sum of the per-invoice balances in the queue (when the queue is not truncated). Card and list reconcile; neither double-counts.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-013: Outstanding renders RM, never MYR; zero shows RM 0.00
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: M6 KPI (outstanding) | **Risk**: wrong currency symbol | **Type**: Feature
**Before you start**: Operator. Run once in an org with outstanding money and once in an org with none. Repeat each run with app language EN, then BM.
| Step | Action |
|------|--------|
| 1 | Read the Outstanding card in the org with money owed |
| 2 | Read it in the org with nothing owed |
| 3 | Switch language EN <-> BM and re-read |
**What you should see**: Money is shown as `RM` (e.g. `RM 160.00`, `RM 0.00`), never the ISO code `MYR`, in both EN and BM (matches `formatMoney`). Two decimals always.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## C. KPI card: 30-day attendance rate

### TC-DASH-020: Attendance KPI is (present + late) / marked over 30 days
**Tags**: @smoke @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: M6 KPI (attendance) | **Risk**: wrong rate | **Type**: Feature
**Before you start**: Operator. In one active class, mark attendance across recent sessions (inside the last 30 days) so the org totals are: 2 present, 1 late, 1 absent. (This mirrors the service test: (2+1)/4 = 75%.)
**Test Data**: expected rate = 75%.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Read the "Attendance" KPI card value |
**What you should see**: Card shows `75%`. Late counts as attended (numerator = present + late); the denominator is all marked records (present + late + absent). Unmarked sessions do not count. Value is rounded to a whole percent.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-021: Attendance KPI shows a dash when nothing is marked
**Tags**: @smoke @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: M6 KPI (attendance, null) | **Risk**: shows 0% instead of dash | **Type**: Feature
**Before you start**: Operator in an org with NO marked attendance in the last 30 days but at least one teacher or class (so the KPI row renders; a totally empty org shows only the checklist, TC-DASH-099). E.g. an org with a class whose sessions are all unmarked. Mirrors the `org_EMPTY` service test where attendanceRate is null.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Read the "Attendance" KPI card value and sub-line |
**What you should see**: The card shows a dash `-` (NOT `0%`), and the sub-line shows the "no attendance marked" empty text. A dash means "nothing to measure"; 0% would falsely imply everyone was absent.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-022: Attendance KPI window excludes records older than 30 days
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2
**Linked**: M6 KPI (attendance window) | **Risk**: old data inflates rate | **Type**: Feature
**Before you start**: Operator in a class with some marked attendance inside the last 30 days and clearly different marks dated more than 30 days ago (e.g. all-absent old sessions). Note what the rate should be from the in-window records only.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Read the Attendance KPI |
**What you should see**: The rate reflects only sessions in the last 30 days; the older marks do not change it (service filters `sessions.scheduledAt >= now - 30 days`).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## D. Billed-vs-collected trend chart (12 months)

### TC-DASH-030: Trend shows 12 months billed vs collected, current-month figures correct
**Tags**: @smoke @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: M6 trend chart | **Risk**: wrong bar heights | **Type**: Feature
**Before you start**: Operator. For the current billing month create: a Paid invoice RM 100.00 (paid 100), a Partially-paid invoice total RM 100.00 (paid 40); for last month an Issued invoice RM 50.00 (paid 0). (Mirrors the trend test: current billed 200 / collected 140; last month billed 50 / collected 0.)
**Test Data**: current month billed = RM 200, collected = RM 140; last month billed = RM 50, collected = RM 0.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Hover the current-month bars and read the tooltip; then last month's |
**What you should see**: The chart spans 12 month columns (oldest to newest, KL time). Current month: billed bar = RM 200, collected bar = RM 140. Last month: billed = RM 50, collected = RM 0. The tooltip labels read "Billed" and "Collected" and show RM values.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-031: Trend excludes voided invoices from the billed total
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T2
**Linked**: M6 trend chart | **Risk**: voided inflates billed | **Type**: Feature
**Before you start**: Operator. In the current billing month, on top of the TC-DASH-030 invoices, add a Voided invoice of RM 999.00. (Mirrors the trend test: voided 999 must be excluded so billed stays 200.)
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Hover the current-month billed bar |
**What you should see**: Current-month billed is still RM 200 (the voided RM 999 is NOT added). Voided invoices never contribute to billed or collected.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-032: Trend zero-fills months that have no invoices
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2
**Linked**: M6 trend chart | **Risk**: missing/gap columns | **Type**: Feature
**Before you start**: Operator in an org whose invoices only cover a couple of recent months, leaving earlier months with none.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Look at the month columns that have no invoices |
**What you should see**: Every one of the 12 months has a column; empty months render as RM 0 / RM 0 (a flat zero bar), NOT a gap or a skipped month. The series is continuous (matches the zero-fill in `getOrgBillingTrend`).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-033: Trend empty state when there is no billing at all
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Linked**: M6 trend empty state | **Risk**: blank panel | **Type**: Feature
**Before you start**: Operator in an org that has never run billing (no invoices, or all months zero) but has at least a class or teacher so the dashboard grid renders (see the empty-org gate in the preamble).
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Look at the trend panel |
**What you should see**: Instead of an all-zero chart, the panel shows the "no billing yet" empty message (the page renders the empty text when no month has billed > 0 or collected > 0). No chart axes, no broken canvas.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-034: Trend month labels are short months in the current locale
**Tags**: @regression **Severity**: S4 Low | **Priority**: P4 | **Tier**: T3
**Linked**: M6 trend labels (i18n) | **Risk**: wrong month names | **Type**: Feature
**Before you start**: Operator with trend data present. Run once in EN, once in BM.
| Step | Action |
|------|--------|
| 1 | Read the x-axis month labels in EN |
| 2 | Switch language to BM and re-read |
**What you should see**: Labels are short month names in KL time (e.g. "Jan", "Feb" in EN; the Malay short forms in BM, per `formatMonthShort`). Y-axis ticks show compact RM values (no decimals), never MYR.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## E. Recent payments

### TC-DASH-040: Recent payments lists verified payments, newest first, with payer name
**Tags**: @smoke @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: M6 recent payments | **Risk**: wrong/ordered list | **Type**: Feature
**Before you start**: Operator. For one guardian (e.g. "Puan Mariam") with a family invoice, record two VERIFIED payments: RM 200.00 by DuitNow dated today, then RM 100.00 by cash dated an earlier month. (Mirrors the recent-payments service test.)
**Test Data**: expected list top-to-bottom: RM 200.00 (DuitNow), RM 100.00 (cash); payer name "Puan Mariam".
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Read the "Recent payments" card rows top to bottom |
**What you should see**: Rows ordered newest first: RM 200.00 then RM 100.00. Each row shows the payer name ("Puan Mariam") and the payment method label. Amounts are prefixed with `+` and shown in RM.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-041: Recent payments excludes pending and refund entries
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: M6 recent payments | **Risk**: unverified money shown | **Type**: Feature
**Before you start**: Operator. On the same payer add: a PENDING self-service payment of RM 50.00 dated today, and a verified REFUND of RM 30.00 dated today, alongside the verified payments from TC-DASH-040.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Scan the Recent payments rows |
**What you should see**: Neither the RM 50.00 pending payment nor the RM 30.00 refund appears. Only `status = verified`, `kind = payment` rows are listed (matches the service filter). The list still reads RM 200.00, RM 100.00.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-042: This-month payment count counts only this month's verified payments
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: M6 recent payments (monthCount) | **Risk**: wrong count | **Type**: Feature
**Before you start**: Same data as TC-DASH-040/041: one verified payment dated today (this month), one verified payment dated an earlier month, plus the excluded pending + refund.
**Test Data**: expected this-month count = 1.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Read the "Recent payments" card sub-line (the count) |
**What you should see**: The sub-line reports 1 payment this month. The earlier-month verified payment, the pending payment, and the refund are all excluded from the count.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-043: Recent payment row links to the guardian for a family invoice
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T3
**Linked**: M6 recent payments (guardian link) | **Risk**: dead/wrong link | **Type**: Feature
**Before you start**: Operator. A verified payment exists on a guardian (family) invoice. Note the guardian's name.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Click the payer name on that row |
**What you should see**: Navigates to `/dashboard/guardians/<guardianId>` and the guardian detail page for that exact guardian opens. The name is a link (underlines on hover).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-044: Recent payment row links to the student for an adult-learner invoice
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T3
**Linked**: M6 recent payments (student link) | **Risk**: wrong link target | **Type**: Feature
**Before you start**: Operator. A verified payment exists on an invoice billed directly to a student (adult learner, no guardian). Note the student's name.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Click the payer name on that row |
**What you should see**: Navigates to `/dashboard/students/<studentId>` (not a guardian page). The fallback order is guardian first, else student (matches the page's href logic).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-045: Recent payment with no payer name falls back to a dash, no broken link
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Linked**: M6 recent payments (missing name) | **Risk**: blank row / broken link | **Type**: Feature
**Before you start**: Operator. A verified payment whose invoice has no guardian and no student name resolvable (edge fixture). If unavailable, document as not reproducible.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Inspect the row for that payment |
**What you should see**: The name shows `-` and is plain text (not a link, since neither guardianId nor studentId is present). The avatar initials show `?`. The amount still renders in RM.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-046: Recent payments empty state
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Linked**: M6 recent payments (empty) | **Risk**: blank card | **Type**: Feature
**Before you start**: Operator in an org with no verified payments yet (the org must be non-empty, e.g. have a class, so the card renders at all).
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Look at the Recent payments card |
**What you should see**: A "no recent payments" empty message inside the card (not a blank card, not a zero-row table). The sub-line count reads 0 this month.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## F. Absence-alerts queue

### TC-DASH-050: Absence-alerts queue lists students with 3+ consecutive absences, name links to student
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T3
**Linked**: M6 absence alerts | **Risk**: wrong roster / dead link | **Type**: Feature
**Before you start**: Operator. In one class, mark a student absent for their 3 most recent marked sessions in a row (no present/late in between). Note the student name and class.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Find that student in the "Absence alerts" card |
| 3 | Click the student name |
**What you should see**: The student appears with "3 absences in a row" (the consecutive run) and the class name beneath. Clicking the name opens `/dashboard/students/<studentId>` for that student. (Run computed by `getAbsenceAlerts`, threshold 3.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-051: A non-absent mark breaks the streak so the student drops off the queue
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T3
**Linked**: M6 absence alerts (streak) | **Risk**: stale alert | **Type**: Feature
**Before you start**: Operator. Start from TC-DASH-050's student (currently alerting on 3 absences). Add a newer session and mark them Present.
| Step | Action |
|------|--------|
| 1 | Mark the student Present in a session newer than their absent run |
| 2 | Reload /dashboard |
**What you should see**: The student no longer appears in Absence alerts (the most-recent mark is now Present, so the consecutive-absent run resets below the threshold of 3).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-052: Absence-alerts queue caps at 6 with a View all link to attendance
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Linked**: M6 absence alerts (cap) | **Risk**: unbounded list | **Type**: Feature
**Before you start**: Operator in an org with more than 6 students currently in an absence alert state.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Count the rows in Absence alerts |
| 3 | Click "View all" |
**What you should see**: At most 6 rows are shown (page slices to 6). "View all" navigates to `/dashboard/attendance`.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-053: Absence-alerts empty state
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Linked**: M6 absence alerts (empty) | **Risk**: blank card | **Type**: Feature
**Before you start**: Operator in an org where no student has 3+ consecutive absences.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Look at the Absence alerts card |
**What you should see**: A "no absence alerts" empty message in the card body (not an empty bordered list).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## G. Unpaid-invoices queue

### TC-DASH-060: Unpaid queue lists unpaid invoices; invoice number links to invoice detail
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T3
**Linked**: M6 unpaid queue | **Risk**: wrong list / dead link | **Type**: Feature
**Before you start**: Operator with at least one Issued or Partially-paid invoice. Note an invoice number and its balance.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Find that invoice in the "Unpaid invoices" card |
| 3 | Click its invoice number |
**What you should see**: The row shows the invoice number, the payer name beneath, and the outstanding balance in RM on the right. Clicking the number opens `/dashboard/billing/<invoiceId>` for that invoice. Paid and Voided invoices do not appear.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-061: Overdue invoices in the queue show an Overdue badge in red
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Linked**: M6 unpaid queue (overdue) | **Risk**: overdue not flagged | **Type**: Feature
**Before you start**: Operator with one unpaid invoice whose due date is in the past (overdue) and one unpaid invoice not yet overdue.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Compare the two rows in the Unpaid invoices card |
**What you should see**: The past-due invoice shows an "Overdue" status badge (negative tone) and its balance is in the destructive/red colour; the not-yet-due one shows no badge and an amber balance.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-062: Unpaid queue caps at 6 with a View all link to billing
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Linked**: M6 unpaid queue (cap) | **Risk**: unbounded list | **Type**: Feature
**Before you start**: Operator in an org with more than 6 unpaid invoices.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Count the rows in Unpaid invoices |
| 3 | Click "View all" |
**What you should see**: At most 6 rows (page slices to 6). "View all" navigates to `/dashboard/billing`.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-063: Unpaid-invoices empty state
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Linked**: M6 unpaid queue (empty) | **Risk**: blank card | **Type**: Feature
**Before you start**: Operator in an org with no unpaid invoices (none issued, or all paid/voided). If the org has never issued any invoice it must have a teacher or class so the grid renders (empty-org gate, preamble).
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Look at the Unpaid invoices card |
**What you should see**: A "no unpaid invoices" empty message in the card; this is consistent with the Outstanding KPI showing RM 0.00.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## H. Class-health grid

### TC-DASH-070: Class health shows active enrolment vs capacity and 30-day attendance, archived excluded
**Tags**: @smoke @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: M6 class health | **Risk**: wrong enrolment / archived leak | **Type**: Feature
**Before you start**: Operator. In an active class "Quran H" (capacity max 10), enrol 3 students then END one enrolment, leaving 2 active. Mark today's session for that class: 1 present, 1 absent. Also have one ARCHIVED class. (Mirrors the class-health service test: enrolled 2, capacity 10, rate 50%, archived excluded.)
**Test Data**: expected row "Quran H": students "2 / 10", attendance "50%".
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Read the "Quran H" row in the Class health grid |
**What you should see**: One row for "Quran H" showing students `2 / 10` (active enrolments only; the ended enrolment is not counted) and attendance `50%`. The archived class is NOT a row in the grid.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-071: Health band: 85%+ shows Healthy
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2
**Linked**: M6 class health (band) | **Risk**: wrong band label | **Type**: Feature
**Before you start**: Operator. In an active class, mark recent attendance so the 30-day rate is at least 85% (e.g. all present across several sessions; note the rate it should produce).
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Read that class's Health badge |
**What you should see**: The health badge reads "Healthy" (positive/green tone). Boundary: a rate of exactly 85% is Healthy (`>= 85`).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-072: Health band: 70-84% shows Watch
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2
**Linked**: M6 class health (band) | **Risk**: band boundary wrong | **Type**: Feature
**Before you start**: Operator. Mark a class's recent attendance so the 30-day rate falls in 70-84% (e.g. the 75% mix: present + late vs one absent). Note the rate.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Read that class's Health badge |
**What you should see**: The badge reads "Watch" (warning/amber tone). Boundary: exactly 70% is Watch (`>= 70` and `< 85`); 84% is still Watch.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-073: Health band: below 70% shows At risk
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2
**Linked**: M6 class health (band) | **Risk**: band boundary wrong | **Type**: Feature
**Before you start**: Operator. Mark a class's recent attendance so the 30-day rate is under 70% (more absences than present + late). Note the rate (e.g. 50%).
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Read that class's Health badge |
**What you should see**: The badge reads "At risk" (negative/red tone). Boundary: 69% is At risk, 70% flips to Watch.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-074: Health band: no marked attendance shows No data with a dash rate
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2
**Linked**: M6 class health (null band) | **Risk**: 0%/At-risk shown for unmarked | **Type**: Feature
**Before you start**: Operator. An active class with active enrolments but NO marked attendance in the last 30 days. Note the enrolment count and capacity.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Read that class's row |
**What you should see**: The attendance cell shows `-` (dash) and the Health badge reads "No data" (neutral tone), NOT "At risk" and NOT 0%. The students count still shows the active enrolment / capacity correctly.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-075: Class name in the health grid links to the class detail page
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Linked**: M6 class health (link) | **Risk**: dead/wrong link | **Type**: Feature
**Before you start**: Operator with at least one active class in the grid. Note its name.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Click the class name in the Class health grid |
**What you should see**: Navigates to `/dashboard/classes/<classId>` and opens that class's detail page. The name is a link (underlines on hover).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-076: Class-health empty state when there are no active classes
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Linked**: M6 class health (empty) | **Risk**: empty table headers shown | **Type**: Feature
**Before you start**: Operator in an org with no active classes: all archived, or none created (in that case the org needs a teacher so the dashboard grid renders; an archived class also keeps the org non-empty).
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Look at the Class health panel |
**What you should see**: A "no classes yet" empty message (not an empty table with just headers). Consistent with the Active classes KPI showing 0.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-077: Class-health enrolment over capacity is shown honestly (n / max)
**Tags**: @regression @data-integrity **Severity**: S4 Low | **Priority**: P4 | **Tier**: T3
**Linked**: M6 class health (overfill) | **Risk**: count clamped/hidden | **Type**: Feature
**Before you start**: Operator. A class whose active enrolment count exceeds its capacity max (enrol more than the max if the system allows it; otherwise document as not reproducible).
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Read that class's students cell |
**What you should see**: The cell shows the true `enrolled / capacityMax` (e.g. `12 / 10`), not clamped to the max and not hidden. The grid reports reality.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## I. Reconciliation across the dashboard

### TC-DASH-080: KPI cards reconcile with their underlying queues and grid
**Tags**: @smoke @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: M6 whole dashboard | **Risk**: cards disagree with lists | **Type**: Feature
**Before you start**: Operator in an org with a small, fully-known data set (few students, few classes, a handful of invoices, some attendance). Count by hand from the source modules: active students, active classes, total outstanding, unpaid count, and the 30-day attendance rate.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Compare each KPI to your hand-counted figures and to the queues/grid below |
**What you should see**: Active students = the Students module active count; Active classes = the count of non-archived classes (and = the number of rows in the Class health grid); Outstanding = sum of the unpaid-queue balances (when not truncated) and the unpaid sub-line count matches the queue length; Attendance KPI is consistent with the per-class rates in the grid. Nothing contradicts.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-081: A void elsewhere flows through to outstanding, trend, and unpaid queue together
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: M6 cross-section consistency | **Risk**: partial update | **Type**: Feature
**Before you start**: Operator. Pick an Issued invoice that currently appears in the unpaid queue, contributes to Outstanding, and is in the current billing-month billed bar (note all three before).
| Step | Action |
|------|--------|
| 1 | Note Outstanding, the current-month billed bar, and the unpaid queue |
| 2 | Void that invoice in Billing |
| 3 | Reload /dashboard |
**What you should see**: After voiding, the invoice disappears from the unpaid queue, Outstanding drops by its balance, AND the current-month billed bar drops by its total. All three update consistently (void excluded everywhere).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## J. Permissions + tenant isolation

### TC-DASH-090: Teacher does not see the operator dashboard (redirected to attendance)
**Tags**: @smoke @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Linked**: M6 access control | **Risk**: teacher sees org money/KPIs | **Type**: Feature
**Before you start**: Log in as a teacher: `teacher@kelastest.local` / `password12345` (a member whose Better Auth org-membership role is teacher; the role lives on the membership, it is not inferred from email).
| Step | Action |
|------|--------|
| 1 | Navigate directly to /dashboard |
**What you should see**: The page does NOT render the operator dashboard. The teacher is redirected to `/dashboard/attendance` (the `(operator)` route group's layout calls `requireOperator`, which redirects teachers). No KPI cards, no outstanding money, no recent payments are shown to the teacher. The sidebar shows only the teacher nav (Attendance, My classes, My pay) with no Billing item and no receipts badge.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-091: Operator with no organisation is redirected to org selection
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: M6 access control (no org) | **Risk**: dashboard renders with no tenant | **Type**: Feature
**Before you start**: An authenticated account whose Better Auth session has no active organisation selected (e.g. a fresh sign-up that has not created or joined a centre yet).
| Step | Action |
|------|--------|
| 1 | Navigate to /dashboard |
**What you should see**: Redirected to `/onboarding/organization-selection` (both the `(operator)` layout's `requireOperator` guard and the page's own `requireOrgId` catch send a no-org session there). The dashboard never renders without a tenant context.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-092: Every figure on the dashboard is scoped to the current org only
**Tags**: @smoke @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Linked**: M6 tenant isolation | **Risk**: cross-tenant data leak | **Type**: Feature
**Before you start**: Two orgs, A and B, each with their own students, classes, invoices, payments, and attendance. As operator of org A, know org A's expected figures; org B has clearly different (larger) numbers.
| Step | Action |
|------|--------|
| 1 | Sign in as org A operator and open /dashboard |
| 2 | Read every KPI, the trend, recent payments, both queues, and the class-health grid |
| 3 | Switch to org B and reload /dashboard |
**What you should see**: Org A's dashboard shows only org A's figures (no org B students, classes, invoices, payments, alerts, or classes appear). Org B's dashboard shows only org B's. Every aggregate filters on `orgId` (matches the `org_EMPTY` isolation test). No row, name, amount, or count crosses the tenant boundary.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## K. Receipts awaiting verification (card + sidebar badge)

Added by commit de4be04 (CX1/CX2 loop): a parent's uploaded receipt used to be discoverable only if
the operator happened to open the billing page. The dashboard now shows a "Receipts to verify (N)"
card in the "Needs action" zone (only when N > 0), and the Billing sidebar item carries a count
badge on every dashboard page. Card list = `listPendingPayments` (this org's payments with status
pending, source self-service, not soft-deleted, newest first). Badge = `countPendingPayments`,
which since f406a4c (2026-07-04) uses the SAME self-service filter as the queue (service-tested:
a pending payment from another source never inflates the badge), so the two counts can never
disagree; a mismatch is a defect.

### TC-DASH-093: Receipts card appears only when a receipt is waiting, with the exact count
**Tags**: @smoke @regression @data-integrity **Severity**: S2 High | **Priority**: P1 | **Tier**: T2
**Linked**: CX1/CX2 receipts loop (de4be04) | **Risk**: parent claims sit invisible / ghost card | **Type**: Feature
**Before you start**: Operator (`operator@kelastest.local` / `newpassword6789`) in an org with NO pending receipts (open /dashboard/billing/pending first and verify or reject anything waiting until it reads "No payments waiting for verification."). Have one Issued invoice and its public payment link (Billing > open the invoice > copy the public link).
**Test Data**: one self-service claim of RM 50.00 with any receipt image, submitted on the invoice's public page.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard and look through the whole page for a card titled "Receipts to verify" |
| 2 | On the invoice's public page, submit a payment claim of RM 50.00 with a receipt file |
| 3 | Reload /dashboard |
**What you should see**: Step 1: no such card exists anywhere (the card renders only when the pending count is above zero; there is no empty-state version of it). Step 3: a card titled "Receipts to verify (1)" (BM: "Resit untuk disahkan (1)") appears under the "Needs action" section label, showing the payer name as a link, the invoice number beneath it, and `RM 50.00` on the right.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-094: Receipts card rows open the invoice; View all opens the pending queue
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: CX1/CX2 receipts loop (de4be04) | **Risk**: dead/wrong link on a money queue | **Type**: Feature
**Before you start**: Operator with at least one pending receipt (set up as in TC-DASH-093). Note the payer name and invoice number on the card row.
| Step | Action |
|------|--------|
| 1 | Go to /dashboard and click the payer name on a receipts-card row |
| 2 | Go back to /dashboard and click "View all" on the receipts card |
**What you should see**: Step 1 opens `/dashboard/billing/<invoiceId>` (the invoice detail, where the Verify/Reject actions live) for that exact invoice. Step 2 opens `/dashboard/billing/pending`, titled "Pending payments" (BM: "Pembayaran menunggu") with the description "Receipts uploaded by parents, waiting for your confirmation." and the same claim listed. Row text is the payer name; when no payer name resolves, the row shows the invoice number instead (never a blank link).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-095: Sidebar Billing badge shows the waiting count on every page, hidden at zero
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: CX1/CX2 receipts loop (de4be04) | **Risk**: badge disagrees with the queue / ghost badge | **Type**: Feature
**Before you start**: Operator with exactly one pending receipt (as in TC-DASH-093).
| Step | Action |
|------|--------|
| 1 | On /dashboard, read the badge on the "Billing" item in the sidebar's Finance group |
| 2 | Navigate to /dashboard/classes, then /dashboard/students, and re-read the badge |
| 3 | Verify or reject the claim at /dashboard/billing/pending, then reload any dashboard page |
**What you should see**: Steps 1-2: the Billing item carries a numeric badge reading `1`, equal to the receipts-card count, and it is visible from every dashboard page (the layout computes it once for all pages). Step 3: the badge disappears entirely; there is never a `0` badge.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-096: Deciding a claim drops the count; card and badge vanish at zero
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: CX2 state transition (de4be04) | **Risk**: stale count after verify/reject | **Type**: Feature
**Before you start**: Operator with exactly TWO pending receipts: submit self-service claims of RM 50.00 and RM 60.00 (as in TC-DASH-093, on one or two issued invoices).
| Step | Action |
|------|--------|
| 1 | On /dashboard, confirm the card reads "Receipts to verify (2)" and the Billing badge reads 2 |
| 2 | Go to /dashboard/billing/pending and click Verify on the RM 50.00 claim |
| 3 | Return to /dashboard and re-read card + badge |
| 4 | Reject the RM 60.00 claim, then return to /dashboard |
**What you should see**: Step 3: card title now "Receipts to verify (1)", badge `1` (a verified claim leaves pending). Step 4: the card is gone from the page entirely and the badge is absent (a rejected claim also leaves pending; it does not count toward the invoice). Mirrors the service test "counts waiting claims org-wide and drops as they are decided".
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-097: Receipts count, card, and badge are tenant-scoped
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Linked**: tenant isolation (de4be04 service test, tenant-scoped assertion) | **Risk**: cross-tenant money-claim leak | **Type**: Feature
**Before you start**: Org A has two pending receipts (as in TC-DASH-096 step 1); org B has none. You can operate both orgs (switch centre from the account menu, or use two operator accounts).
| Step | Action |
|------|--------|
| 1 | As org A operator, confirm "Receipts to verify (2)" and Billing badge 2 |
| 2 | Switch to org B and open /dashboard |
| 3 | Read the whole page and the sidebar |
**What you should see**: Org B shows NO receipts card and NO Billing badge; none of org A's payer names, invoice numbers, or amounts appear anywhere. Switching back to org A still shows (2). `countPendingPayments` and `listPendingPayments` both filter on the org id (the CX2 service test asserts the count for another org stays 0).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-098: Receipts card caps at 6 rows while the title shows the full count
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Linked**: CX1/CX2 receipts loop (de4be04) | **Risk**: unbounded list / hidden backlog | **Type**: Feature
**Before you start**: Operator in an org with 7 or more pending receipts (submit 7 self-service claims of RM 10.00 each across one or more issued invoices).
| Step | Action |
|------|--------|
| 1 | Go to /dashboard and count the rows in the receipts card |
| 2 | Read the number in the card title |
| 3 | Click "View all" |
**What you should see**: Exactly 6 rows are listed (the page slices to 6, newest first) but the title reads "Receipts to verify (7)" (the full count, not the sliced count). "View all" opens /dashboard/billing/pending listing all 7.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## L. Getting-started checklist + migration hub

The checklist (6 steps) renders at the top of the dashboard while fewer than 6 are done, and its
done-state is computed live from real data on every load (no stored flags): payment details
(bank name + account, or a DuitNow QR), a teacher, a class, an enrolment, an attendance record,
and a non-draft invoice. Commit 63c3365 added pull-through (form steps carry `?from=onboarding`
and return to the dashboard) and the enrol deep-link; commit 8da4c9e added the migration hub at
/dashboard/import, linked from the checklist foot.

### TC-DASH-099: A brand-new org sees the checklist only, not the KPI dashboard
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: first-run experience (onboarding service `isEmpty`) | **Risk**: empty org faces a wall of zeros / non-empty org loses its dashboard | **Type**: Feature
**Before you start**: Operator in a brand-new org: no teacher, no class, no enrolment, no invoice. (Payment details may be set or not; they do not affect the gate.)
| Step | Action |
|------|--------|
| 1 | Go to /dashboard |
| 2 | Inventory everything on the page |
**What you should see**: Only the "Dashboard" title bar and a card titled "Getting started" (BM: "Mula di sini") with the subtitle "A few steps to get your centre up and running." and six steps: "Add your payment details", "Add a teacher", "Create a class", "Enrol a student", "Take attendance", "Send your first invoice". NO KPI cards, no "Billed vs collected", no "Recent payments", no "Absence alerts", no "Unpaid invoices", no "Class health", no section labels (the whole grid is gated off while the org is empty: no teacher, class, enrolment, or issued invoice). With nothing done the progress line reads "0 of 6 done" and 0%.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-100: Completing a step elsewhere ticks on return; form steps return to the dashboard
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: CX12 pull-through (63c3365) | **Risk**: tick never seen, thread lost on a list page | **Type**: Feature
**Before you start**: Operator in the org from TC-DASH-099, checklist showing, "Add a teacher" unticked.
**Test Data**: teacher name `Ustaz Ali`.
| Step | Action |
|------|--------|
| 1 | Click "Add a teacher" on the checklist and read the URL |
| 2 | Fill in the teacher name `Ustaz Ali` and save |
| 3 | On the page you land on, read the checklist |
**What you should see**: Step 1: the form opens at `/dashboard/teachers/new?from=onboarding`. Step 2: saving returns you to /dashboard (NOT the teachers list; without `from=onboarding` it would go to the list). Step 3: "Add a teacher" now shows a filled tick and the label is struck through; the progress line advances (e.g. "1 of 6 done", 17%). Because done-state is live from data, a step completed by any other path (list pages, import) also shows ticked on the next dashboard visit. Same pull-through applies to "Create a class" (`/dashboard/classes/new?from=onboarding`) and "Add your payment details" (`/dashboard/billing/settings?from=onboarding`).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-101: Enrol step deep-links to the first class page once a class exists
**Tags**: @regression **Severity**: S2 High | **Priority**: P3 | **Tier**: T3
**Linked**: CX12 enrol deep-link (63c3365; onboarding service test "exposes the first class id for the enrol deep-link, tenant-scoped") | **Risk**: step dumps the user where enrolment cannot be done | **Type**: Feature
**Before you start**: Operator with the checklist showing. Run twice: (a) before the org has any class; (b) after creating a class named `Quran Asas`.
| Step | Action |
|------|--------|
| 1 | Click "Enrol a student" on the checklist |
| 2 | Read the URL and the page you land on |
**What you should see**: Run (a): opens `/dashboard/classes` (the classes list; there is no class to deep-link to yet). Run (b): opens `/dashboard/classes/<classId>` for `Quran Asas`, the class detail page where the Enrol action actually lives. The deep-linked class always belongs to the current org (the service test asserts another org's `firstClassId` stays null).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-102: Payment-details step completes with bank name + account OR a DuitNow QR
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: onboarding service `hasPayment` | **Risk**: step never ticks / ticks on half-set details | **Type**: Feature
**Before you start**: Two orgs where "Add your payment details" is unticked and no payment settings are saved.
**Test Data**: bank name `Maybank`, account number `1234567890`; separately, any DuitNow QR image file.
| Step | Action |
|------|--------|
| 1 | Org 1: click "Add your payment details", enter bank name `Maybank` and account `1234567890`, save |
| 2 | Read the checklist on return |
| 3 | Org 2: click "Add your payment details", upload only a DuitNow QR image (no bank fields), save |
| 4 | Read the checklist on return |
**What you should see**: Both saves return to /dashboard (the `?from=onboarding` pull-through) and in both orgs "Add your payment details" is ticked. Either complete bank details (name AND account together) or a DuitNow QR alone completes the step (the service checks bank name + account as a pair, OR the QR file).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-103: A draft invoice does not tick the invoice step; checklist disappears at 6 of 6
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2
**Linked**: onboarding service `hasInvoice` (non-draft only) + the `done < total` render gate | **Risk**: checklist lingers forever / ticks on an unsent draft | **Type**: Feature
**Before you start**: Operator in an org with 5 of 6 steps done: everything except "Send your first invoice". Billing has generated a DRAFT invoice that has not been issued.
| Step | Action |
|------|--------|
| 1 | On /dashboard, read the progress line and the invoice step |
| 2 | In Billing, issue the draft invoice |
| 3 | Return to /dashboard |
**What you should see**: Step 1: "5 of 6 done" (83%) and "Send your first invoice" still unticked; a draft does not count (the service counts only non-draft invoices). Step 3: the checklist card is gone entirely (it renders only while fewer than 6 steps are done) and the page opens straight at the "Summary" KPI zone.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-104: Dismissing the checklist hides it persistently in this browser only
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Linked**: checklist dismiss (localStorage `kelas.onboarding.dismissed`) | **Risk**: dismiss does not stick / dismiss hides for everyone | **Type**: Feature
**Before you start**: Operator with the checklist visible and steps incomplete.
| Step | Action |
|------|--------|
| 1 | Click the X (Dismiss) at the top right of the "Getting started" card |
| 2 | Reload /dashboard |
| 3 | Open /dashboard in a different browser or a private window and sign in as the same operator |
**What you should see**: Steps 1-2: the card hides immediately and stays hidden after reload (the flag is saved in this browser's localStorage, key `kelas.onboarding.dismissed`). Step 3: the checklist appears again; dismissal is per-browser, not stored on the server. Note honestly: in a still-empty org (TC-DASH-099), dismissing leaves only the title bar on the page; record what you see.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-105: Checklist import hint opens the guided migration hub with ordered, tenant-scoped counts
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: CX16 migration hub (8da4c9e) | **Risk**: existing-data centres hand-type 60 students / cross-org counts | **Type**: Feature
**Before you start**: Operator with the checklist visible. The org already has exactly 2 teachers and nothing else imported. Another org in the system has many records.
| Step | Action |
|------|--------|
| 1 | At the foot of the checklist, click "Have existing data? Import it from Excel instead." (BM: "Ada data sedia ada? Import dari Excel.") |
| 2 | Read the page title, the step order, and each step's count |
| 3 | Click the "Import" button on the Teachers step |
**What you should see**: Step 1 opens `/dashboard/import`, titled "Move your data in" (BM: "Pindah data ke Kelasapp") with the description "Bring your centre over from Excel or an old system. Follow the order below - later steps link to earlier ones." Step 2: five steps in this exact order: Teachers, Classes, Guardians, Students, Enrolments, each with a one-line reason (Teachers reads "Start here. Classes need a teacher."). The Teachers step shows a check mark and "2 already in" (BM: "2 sedia ada"); the four others show their step number (2-5) and no count line. Counts are this org's rows only, never another org's. Step 3 opens the teachers import wizard at `/dashboard/teachers/import`.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## M. Visual hierarchy + sidebar navigation

### TC-DASH-106: Dashboard zones, KPI micro-labels, and the amber hero stat
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Linked**: W2 hierarchy pass (91a3820) | **Risk**: zones/hero regress silently in a restyle | **Type**: Feature
**Before you start**: Operator in a non-empty org with some outstanding money. Run once in EN, once in BM.
| Step | Action |
|------|--------|
| 1 | On /dashboard, read the small uppercase labels between sections, top to bottom |
| 2 | Compare the four KPI cards: label style, value size, icon colour |
**What you should see**: Three uppercase eyebrow labels chapter the page in this order: "Summary" above the KPI row, "Performance" above the trend + recent payments, "Needs action" above the receipts/alerts/unpaid zone (BM: "Ringkasan", "Prestasi", "Perlu tindakan"). KPI titles are small uppercase micro-labels. The Outstanding value is visibly larger than the other three KPI values and rendered in amber ink (the hero stat, the one number the centre runs on); each KPI icon is a plain coloured glyph with no tile box: brand colour for Active students and Active classes, amber for Outstanding, green for Attendance.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-107: Members and Students have distinct sidebar icons
**Tags**: @regression **Severity**: S4 Low | **Priority**: P3 | **Tier**: T3
**Linked**: sidebar icons | **Risk**: two nav items look identical | **Type**: Feature
**Before you start**: Operator on any dashboard page with the sidebar expanded.
| Step | Action |
|------|--------|
| 1 | Compare the icon next to "Students" (People group) with the icon next to "Members" (Settings group) |
**What you should see**: The two icons are different: Members shows a person-with-cog glyph, Students a multi-person glyph. Neither duplicates the other.
**Notes**: REGRESSION: Students and Members shared the same icon; fixed in commit b6f474d.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-108: Sidebar navigation keeps the BM locale prefix and BM labels
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Linked**: i18n nav (e86b941, M9) | **Risk**: a BM operator is silently bounced to EN routes | **Type**: Feature
**Before you start**: Operator with the app language set to Bahasa Melayu (URL starts with `/ms/`).
| Step | Action |
|------|--------|
| 1 | Read the sidebar group labels and item labels |
| 2 | Click through Kelas, Pelajar, and Bil, reading the URL after each click |
**What you should see**: Group labels read "Utama", "Akademik", "Orang", "Kewangan", "Tetapan"; items include "Papan Pemuka", "Kelas", "Guru", "Kehadiran", "Pelajar", "Penjaga", "Bil", "Bayaran guru", "Perniagaan", "Pembayaran", "Invois", "Program", "Tahap", "Ahli", "Bantuan". Every navigation stays under `/ms/...` (e.g. `/ms/dashboard/classes`); the locale prefix is never dropped mid-session.
**Notes**: REGRESSION: the sidebar used a plain next/link, so a BM operator was dropped onto EN routes; fixed in commit e86b941 (locale-aware Link).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-DASH-109: Outstanding amounts use the darker AA-contrast amber
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Linked**: CX8 contrast fixes (4580941) + W1 warning token | **Risk**: low-contrast money figures | **Type**: Feature
**Before you start**: Operator in light mode with outstanding money: at least one unpaid invoice NOT yet overdue (its balance renders amber in the Unpaid invoices card) and one overdue (renders red). A browser contrast checker (DevTools or axe) helps but eyeballing against TC evidence is acceptable.
| Step | Action |
|------|--------|
| 1 | On /dashboard, look at the Outstanding hero value and the not-yet-overdue balance in the Unpaid invoices card |
| 2 | If a checker is available, sample the amber text colour against the card background |
**What you should see**: Both amber figures use the dark warning amber (the design token, light mode #B45309), giving at least 4.5:1 contrast on the card background. The overdue balance stays red (destructive), clearly distinct from the amber. No figure renders in the lighter amber that fails AA.
**Notes**: REGRESSION: dashboard outstanding amounts were amber-600 (below 4.5:1); darkened in commit 4580941, later tokenised as `--warning`.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## Coverage note

Techniques walked (per QA-METHODOLOGY §5): happy path (001, 010, 020, 030, 040, 050, 060, 070, 093,
100, 105); equivalence + boundary (health bands 071/072/073/074, attendance window 022, capacity
overfill 077, receipts row cap vs full count 098, draft-vs-issued invoice step 103, bank-pair-OR-QR
102); negative / null handling (attendance dash 021, no-data band 074, missing payer name 045,
payer fallback on receipts rows 094); format / locale (RM-not-MYR 013, month labels + axis 034, BM
receipts/checklist/hub strings 093/099/105, BM sidebar + locale-prefix routing 108, BM runs across
the money/date cases); permissions / role (teacher redirect + teacher nav 090, no-org redirect 091);
cross-tenant isolation (003, 092, receipts 097, import-hub counts + enrol deep-link 105/101); state /
lifecycle flow-through (paid/void effects 011, streak break 051, void cross-section 081, claim
verify/reject 096, checklist pull-through 100/103); empty / loading / error states (033, 046, 053,
063, 076, 091, empty-org checklist-only gate 099, no ghost receipts card/badge 093/095); data
integrity / reconciliation (010, 012, 020, 030, 031, 032, 040, 041, 042, 070, 080, 081, 092, badge
= card count 095: every figure reconciled to the underlying lists or to a named service test).
Anti false-pass is enforced throughout: cards must read 0 / dash, never a stale or cross-org number
(003, 011, 021, 074, 095, 096). Regression provenance recorded where a real bug was fixed: duplicate
sidebar icon (107, commit b6f474d), EN-route bounce for BM operators (108, commit e86b941), AA
contrast on outstanding amber (109, commit 4580941). Accessibility beyond 109 (keyboard reach of
the section links) and non-functional load (dashboard fan-out of 8 parallel aggregate queries at
100 orgs / 10k users) are deferred to `test-plan-crosscutting.md` and the load pass, not duplicated
here. Security beyond access control (XSS via stored names rendered in payer/student/class cells)
is owned by the modules that capture those names (People, Classes) and their catalogs; the dashboard
only displays them. Deletions since the 2026-06-30 catalog: none (no dashboard feature was removed);
TC-DASH-003 was rewritten in place because the new empty-org gate (099) means a truly empty org no
longer renders the KPI cards at all.

**Total cases: 60** (43 original + 17 added 2026-07-04 for the receipts-verification loop, the
getting-started checklist + migration hub, and the hierarchy/sidebar passes). Smoke subset
(11 @smoke): TC-DASH-001, 010, 020, 021, 030, 040, 070, 080, 093 (the display/aggregation and
receipts go/no-go) plus the T1 security gates TC-DASH-090 and TC-DASH-092, which must also pass
for the dashboard to be deployable.
