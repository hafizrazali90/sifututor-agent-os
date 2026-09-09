# Test plan: Teacher pay / Payroll (M4 slice 2)

> Exhaustive manual catalog for teacher pay / payroll. Format + method: [QA-METHODOLOGY.md](QA-METHODOLOGY.md).
> Grounded in `src/features/payouts/service.ts` + `service.test.ts`, `src/features/payouts/schema.ts`,
> the pay snapshot in `src/features/attendance/service.ts` (markAttendance, incl. the f31491a roster guard),
> `src/features/classes/ClassForm.tsx` (pay model selector), the payroll pages + `PayrollTable.tsx` +
> `PayoutActions.tsx` + `BulkMarkPaid.tsx` + `PayoutAdjustments.tsx` + `PayslipPdf.tsx`, the teacher's
> `my-pay/page.tsx`, the `src/app/api/payouts/*` routes, and [FLOWS.md](../FLOWS.md) §7.
> Default tier T1 (money out + immutability). Roles: operator/staff (full payroll access);
> teacher (self-service read-only: My pay list + own payslip download; no payroll pages or mutations).
> Auth is Better Auth (roles come from the org membership); no public surface.
>
> Pay model recap (from the code): rate is frozen onto each session when attendance is marked.
> per_session = flat rate per completed session (turnout ignored); per_student = rate x students present+late.
> Run payroll picks only `status = 'complete'` sessions in the KL month, snapshots each into a draft payout
> line, and is idempotent (paid is skipped, draft is refreshed, no session is paid twice). Re-runs preserve
> operator-added adjustment lines. Gross = session lines only; Net = gross + adjustments (bonus /
> reimbursement / correction add, deduction subtracts). The month list's "Amount" column shows GROSS;
> the detail header, "Net pay" row, payslip, and the teacher's My pay show NET.
>
> Cases: 60 (was 46 on 2026-06-30). Last updated: 2026-07-04, reconciled to code on feat/finish-mvp-polish
> through commits b175d3e (teacher self-service), 1ee30f4 (My Pay status), ab86cf3 (bulk mark-paid),
> e86b941 (payslip BM), 31777bd (action failures surfaced), a9737aa (status tones), 746df0b (table pass),
> f31491a (roster guard), 215a3c8/e8dc921 (adjustments). No cases deleted.
>
> Smoke subset (@smoke): TC-PAY-001, TC-PAY-002, TC-PAY-020, TC-PAY-030, TC-PAY-040, TC-PAY-100, TC-PAY-110,
> TC-PAY-123, TC-PAY-127.
>
> Dev logins: operator `operator@kelastest.local` / `newpassword6789`; teacher `teacher@kelastest.local` /
> `password12345` (linked to teacher "Ustazah Fatimah").

## A. Run payroll (generation)

### TC-PAY-001: Run payroll (per_session) creates one draft payout per teacher: flat rate x completed sessions
**Tags**: @smoke @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Log in as operator. Have a class whose Teacher pay method is "Per session" with a rate (note it, e.g. RM 30.00) and an assigned teacher. Mark attendance for one session of that class this month (go to Attendance, open the class today, mark at least one student present, Save). Note the teacher name.
**Test Data**: rate RM 30.00; mark 2 students present, 0 absent; the current KL month.
| Step | Action |
|------|--------|
| 1 | Go to Dashboard > Teacher pay (/dashboard/payroll) |
| 2 | Set the Month picker to the current month |
| 3 | Click Run payroll |
| 4 | Click the teacher's name to open their payout |
**What you should see**: A result line "1 created, 0 refreshed, 0 already paid." One Draft payout row for the teacher with Sessions = 1 and Amount RM 30.00. On the detail page, one line: today's date, the class name, Rate RM 30.00, Present "-" (per_session shows no headcount), Amount RM 30.00; a "Sessions subtotal" row of RM 30.00 and "Net pay" RM 30.00 at the bottom. Turnout does NOT change the amount.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-002: Run payroll (per_student) pays rate x students present, absentees excluded
**Tags**: @smoke @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator. A class whose Teacher pay method is "Per student" with a per-student rate (note it, e.g. RM 10.00), assigned teacher. Mark a session this month with a known present/absent split.
**Test Data**: rate RM 10.00; 2 present, 1 absent; current month.
| Step | Action |
|------|--------|
| 1 | Open Teacher pay, set the current month, click Run payroll |
| 2 | Open that teacher's payout |
**What you should see**: Amount RM 20.00 (RM 10.00 x 2 present, the absent student is not paid). The line shows Present = 2 and Amount RM 20.00. Sessions = 1.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-003: Late counts as present for per_student pay
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator. A per_student class (rate RM 10.00) with a teacher. Mark a session this month with at least one student marked Late.
**Test Data**: rate RM 10.00; 1 present, 1 late, 1 absent.
| Step | Action |
|------|--------|
| 1 | Mark the session: 1 present, 1 late, 1 absent, Save |
| 2 | Run payroll for the month and open the payout |
**What you should see**: Present = 2 (present + late both count); Amount RM 20.00. The absent student is excluded.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-004: Only completed sessions pay: a cancelled or not-yet-marked session is excluded
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator. A class with a teacher that meets twice this month: mark attendance for ONE session (it becomes complete) and leave the other session unmarked / cancelled (status not "complete").
| Step | Action |
|------|--------|
| 1 | Run payroll for the month |
| 2 | Open the teacher's payout |
**What you should see**: Sessions = 1 (only the completed/marked session). The unmarked or cancelled session contributes no line and no amount.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-005: Multiple completed sessions for one teacher sum into a single payout
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator. A per_session class (rate RM 30.00) with a teacher, with TWO sessions marked complete this month (mark on two different meeting days within the 7-day window).
| Step | Action |
|------|--------|
| 1 | Run payroll for the month |
| 2 | Open the teacher's payout |
**What you should see**: ONE payout for the teacher, Sessions = 2, Amount RM 60.00, two line items (one per session date), "Sessions subtotal" RM 60.00 and "Net pay" RM 60.00.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-006: A teacher with completed sessions across two classes is paid once, lines from both classes
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator. The same teacher is the assigned teacher of two different classes, each with one completed session this month (rates may differ, note both).
| Step | Action |
|------|--------|
| 1 | Run payroll for the month |
| 2 | Open that teacher's payout |
**What you should see**: ONE payout for the teacher; two lines (one per class, each showing its own class name and frozen rate); "Sessions subtotal" = the sum of the two line amounts, and "Net pay" equals it (no adjustments added).
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-007: Run payroll with no completed sessions reports zero and creates nothing
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator in a month with no completed (marked) sessions for any teacher.
| Step | Action |
|------|--------|
| 1 | Set the Month picker to that empty month |
| 2 | Click Run payroll |
**What you should see**: The result reads "0 created, 0 refreshed, 0 already paid." The table area shows the rich empty state: title "No teacher payouts for this month yet" with the hint "Take attendance first, then use \"Run payroll\" above." (BM: "Tiada bayaran guru untuk bulan ini lagi" / "Ambil kehadiran dahulu, kemudian guna \"Jana bayaran\" di atas."). No error, no blank screen.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-008: Period is KL-month bounded: a session in another month is not picked up
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator. A teacher with a completed session in the previous month only (none this month).
| Step | Action |
|------|--------|
| 1 | Run payroll for the CURRENT month and check the list |
| 2 | Switch the Month picker to the PREVIOUS month and Run payroll |
**What you should see**: Current month: no payout for that teacher. Previous month: a payout appears with that session. Sessions are matched to the month they were taught (Asia/Kuala_Lumpur), not the run date.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

## B. Idempotency (re-run)

### TC-PAY-020: Re-running payroll refreshes the draft without duplicating lines or pay
**Tags**: @smoke @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator. Payroll already run once this month for a teacher (a Draft payout exists; note its Sessions count and Amount).
| Step | Action |
|------|--------|
| 1 | Click Run payroll again for the same month |
| 2 | Open the teacher's payout |
**What you should see**: The result reads "0 created, 1 refreshed, 0 already paid." Still ONE payout for the teacher (no duplicate row). Sessions count and Amount unchanged; the line count is identical (not doubled).
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-021: Re-run after a new session is marked tops up the draft
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator. A Draft payout for a teacher (note Sessions = N, Amount). Mark one more completed session for the same teacher this month.
| Step | Action |
|------|--------|
| 1 | Run payroll again for the month |
| 2 | Open the teacher's payout |
**What you should see**: Still ONE payout (result shows "0 created, 1 refreshed"). Sessions = N+1; the new session appears as an added line; Amount increased by that session's pay.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-022: A session is paid at most once across re-runs (no double-pay)
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator. A teacher with one completed session this month.
| Step | Action |
|------|--------|
| 1 | Run payroll for the month |
| 2 | Run payroll a second and third time for the same month |
| 3 | Open the teacher's payout |
**What you should see**: Exactly one line for that session every time; Sessions stays 1; Amount stays the single session's pay. The same session never produces a second line on this or any other payout.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-023: Rapid double-click of Run payroll does not create duplicate payouts
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator with completed sessions this month for at least one teacher.
| Step | Action |
|------|--------|
| 1 | Click Run payroll, then immediately click it again before the first finishes (the button shows "Running...") |
| 2 | Refresh the page and scan the list |
**What you should see**: One payout per teacher (no duplicates). The button is disabled while running, and the unique(org, session) constraint prevents a session landing on two payouts.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

## C. Rate freeze + substitute + rate missing

### TC-PAY-030: Rate freeze: editing the class rate after teaching does not change pay
**Tags**: @smoke @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator. A per_session class (rate RM 40.00) with a teacher; mark a session complete this month, then run payroll (Amount RM 40.00). Note the payout.
**Test Data**: change the class rate to RM 999.00 after teaching.
| Step | Action |
|------|--------|
| 1 | Go to Classes, edit that class, change "Rate per session" to RM 999.00, Save |
| 2 | Go back to Teacher pay and Run payroll again for the same month |
| 3 | Open the teacher's payout |
**What you should see**: Amount still RM 40.00 (the rate was frozen onto the session when attendance was marked). The line Rate shows RM 40.00, not RM 999.00.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-031: New session after a rate change uses the new rate (freeze is per session)
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Continue from TC-PAY-030 (old session frozen at RM 40.00; class rate now RM 999.00). Mark a NEW session of the same class complete this month.
| Step | Action |
|------|--------|
| 1 | Run payroll for the month |
| 2 | Open the teacher's payout and read both lines |
**What you should see**: Two lines: the old session at RM 40.00, the new session at RM 999.00. Each session keeps the rate that was in effect when it was marked.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-032: Teacher per-session rate override beats the class rate at mark time
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator. A class with a class rate (e.g. RM 30.00) whose primary teacher has a per-session rate override set (e.g. RM 50.00). Mark a session complete this month.
| Step | Action |
|------|--------|
| 1 | Run payroll for the month |
| 2 | Open the teacher's payout |
**What you should see**: The line Rate and Amount use the teacher override RM 50.00, not the class rate RM 30.00.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-033: Substitute is paid via taughtBy: the actual teacher, not the assigned one
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator. A class whose primary/assigned teacher is Teacher A. A session this month was actually taught by Teacher B (the session's taughtBy is B). Mark/confirm that session complete.
**Before you start (note)**: taughtBy is set from the primary teacher when the session is created; this case checks that whoever is recorded as taughtBy on the completed session is the one paid. Confirm the completed session's taughtBy = Teacher B before running.
| Step | Action |
|------|--------|
| 1 | Run payroll for the month |
| 2 | Look at which teacher's payout includes that session |
**What you should see**: Teacher B (the actual teacher / taughtBy) has the payout and the line for that session. Teacher A is not paid for it.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-034: Class with no rate set produces an RM 0.00 line flagged "Rate not set"
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator. A class with a teacher whose teacher rate is left empty / unset (no class rate and no teacher override). Mark a session complete this month.
| Step | Action |
|------|--------|
| 1 | Run payroll for the month |
| 2 | Open the teacher's payout |
**What you should see**: A line for the session with Amount RM 0.00 and the Rate column showing "Rate not set" (Malay: "Kadar belum ditetapkan") in a warning/red style. The session is still counted (Sessions includes it) so the operator can spot and fix the missing rate.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-035: Zero-students-present per_student session pays RM 0.00 (rate set, nobody present)
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator. A per_student class (rate RM 10.00) with a teacher; mark a session this month with everyone absent (0 present, 0 late).
| Step | Action |
|------|--------|
| 1 | Run payroll for the month |
| 2 | Open the payout |
**What you should see**: A line with Present = 0 and Amount RM 0.00 (RM 10.00 x 0). The rate is shown (not flagged "Rate not set", because a rate exists).
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

## D. Mark as paid

### TC-PAY-040: Mark a draft payout as paid records method, date, and reference; it freezes
**Tags**: @smoke @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator. A Draft payout (open it from Teacher pay; note the Amount).
**Test Data**: method = Bank transfer; Paid on = today; Reference = "TX-12345".
| Step | Action |
|------|--------|
| 1 | On the payout detail, click Mark as paid |
| 2 | Pick Bank transfer, set Paid on to today, type "TX-12345" |
| 3 | Click Mark as paid in the panel |
**What you should see**: Status badge changes to Paid (green). A summary line "Paid on DD/MM/YYYY via Bank transfer · TX-12345". The Mark as paid button no longer appears (only Download payslip and Void remain). Amount unchanged.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-041: Mark as paid with method Cash and no reference succeeds (reference is optional)
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator. A Draft payout.
**Test Data**: method = Cash; Paid on = today; Reference left blank.
| Step | Action |
|------|--------|
| 1 | Mark as paid: Cash, today, leave Reference empty, confirm |
**What you should see**: Status Paid; summary "Paid on DD/MM/YYYY via Cash" with no reference shown. No validation error for the blank reference.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-042: Reference over 120 characters is rejected (server-side)
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: API
**Before you start**: Operator. A Draft payout (note its id from the URL /dashboard/payroll/<id>).
**Test Data**: reference = 121 characters (e.g. "A" x 121).
| Step | Action |
|------|--------|
| 1 | Send PATCH /api/payouts/<id> with body {"action":"mark_paid","paidMethod":"bank_transfer","paidAt":"<today YYYY-MM-DD>","reference":"<121 A's>"} |
**What you should see**: HTTP 422 "Invalid input" with a max-length issue (reference max 120). The payout stays Draft; nothing recorded.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-043: Mark as paid with an invalid method or malformed date is rejected (server-side)
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: API
**Before you start**: Operator. A Draft payout id.
**Test Data**: paidMethod = "cheque" (not allowed); then paidAt = "31/06/2026" (wrong format).
| Step | Action |
|------|--------|
| 1 | PATCH /api/payouts/<id> with {"action":"mark_paid","paidMethod":"cheque","paidAt":"2026-06-30"} |
| 2 | PATCH again with {"action":"mark_paid","paidMethod":"cash","paidAt":"31/06/2026"} |
**What you should see**: Each returns HTTP 422 "Invalid input". Method must be one of bank_transfer / cash / other; date must be YYYY-MM-DD. Payout stays Draft; nothing recorded.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-044: Unknown lifecycle action is rejected
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: API
**Before you start**: Operator. A payout id.
| Step | Action |
|------|--------|
| 1 | PATCH /api/payouts/<id> with {"action":"delete"} |
**What you should see**: HTTP 422 "Unknown action". The payout is unchanged.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

## E. State transitions (paid + void)

### TC-PAY-050: Paid period is immutable: re-running payroll skips it, unchanged
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator. A Paid payout for a teacher this month (note Amount and Reference).
| Step | Action |
|------|--------|
| 1 | Click Run payroll again for the same month |
| 2 | Open the teacher's payout |
**What you should see**: The result reads "0 created, 0 refreshed, 1 already paid." The payout stays Paid; Amount, lines, and Reference are unchanged (the paid record is never mutated).
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-051: Cannot mark a non-draft (already paid) payout paid again
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: API
**Before you start**: Operator. A Paid payout (note its id; the UI hides Mark as paid once paid, so confirm server enforcement via the API).
| Step | Action |
|------|--------|
| 1 | PATCH /api/payouts/<id> with {"action":"mark_paid","paidMethod":"cash","paidAt":"<today>"} |
**What you should see**: HTTP 409 with reason "not_draft". The payout is unchanged (still its original paid details). No second payment recorded.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-052: Void a draft payout: it disappears from the month list and frees its sessions
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator. A Draft payout for a teacher with one completed session (note the teacher).
| Step | Action |
|------|--------|
| 1 | On the payout detail, click Void payout, confirm in the dialog |
| 2 | Go back to Teacher pay for the month |
| 3 | Click Run payroll again for the same month |
**What you should see**: After void, the payout no longer appears in the month list (void rows are hidden). After re-run, the freed session is picked up again: a fresh Draft payout for the teacher with Sessions = 1 and the same Amount.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-053: Void a paid-by-mistake payout, then regenerate the period
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator. A Paid payout entered in error (note the teacher and Amount).
| Step | Action |
|------|--------|
| 1 | Open the paid payout, click Void payout, confirm |
| 2 | Check the month list, then Run payroll again |
**What you should see**: The voided payout drops out of the list. The teacher's sessions are freed and re-claimed on the next run as a new Draft payout with the same Amount. The void records who voided it (audit).
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-054: Voiding an already-void payout is rejected
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: API
**Before you start**: Operator. A payout that is already Void (note its id; the UI hides the Void button on void payouts, so confirm via the API).
| Step | Action |
|------|--------|
| 1 | PATCH /api/payouts/<id> with {"action":"void"} |
**What you should see**: HTTP 409 with reason "already_void". No change.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-055: Lifecycle action on a non-existent payout returns not found
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: API
**Before you start**: Operator authenticated in an org.
**Test Data**: a random/invalid payout id (e.g. 00000000-0000-0000-0000-000000000000).
| Step | Action |
|------|--------|
| 1 | PATCH /api/payouts/<random-id> with {"action":"mark_paid","paidMethod":"cash","paidAt":"<today>"} |
| 2 | PATCH /api/payouts/<random-id> with {"action":"void"} |
**What you should see**: HTTP 404 with reason "not_found" for both. No 500, no leak of any other payout.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

## F. Payout list + detail display

### TC-PAY-060: Month list shows only active (non-void) payouts, sorted by teacher name
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator with several payouts this month (at least one Draft, one Paid, one Void).
| Step | Action |
|------|--------|
| 1 | Open Teacher pay for that month |
**What you should see**: Draft and Paid payouts are listed, ordered alphabetically by teacher name, each with Sessions, Amount (RM), and a status badge (Draft = warning, Paid = positive). The Void payout is NOT listed.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-061: All-column search on the list narrows rows; zero matches offer a Reset
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator; a month with multiple payouts of mixed status (at least one Draft and one Paid) and several teachers. There is no separate status dropdown on this table; one search box ("Search teacher, status...") matches against every visible column.
**Test Data**: part of a real teacher's name; the word "paid"; the gibberish "zzzz".
| Step | Action |
|------|--------|
| 1 | Type part of a teacher's name into the search box "Search teacher, status..." |
| 2 | Clear it, then type "paid" |
| 3 | Clear it, then type "zzzz" |
**What you should see**: Step 1 narrows to that teacher's row(s) and a "Reset" button appears next to the box. Step 2 shows only Paid payouts (the search also matches the status column). Step 3 shows "No matches for your search or filters." with a Reset button; clicking Reset restores the full list. (BM: placeholder "Cari guru, status...", zero-match message "Tiada padanan untuk carian atau tapisan anda.", button "Set semula".)
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-062: Detail page line layout differs by pay model (Present shown only for per_student)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator. One per_session payout and one per_student payout.
| Step | Action |
|------|--------|
| 1 | Open the per_session payout and read a line |
| 2 | Open the per_student payout and read a line |
**What you should see**: per_session lines show "-" in the Present column; per_student lines show the headcount. Both show Date, Class, Rate, Amount, a "Sessions subtotal" row equal to the sum of the session lines, and a "Net pay" row below the table that matches the amount in the card header.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-063: Empty payout detail (no lines) shows the no-sessions message, not a broken table
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator. A payout whose lines were freed (e.g. immediately after Void, opened directly by id) or a 0-line edge case.
| Step | Action |
|------|--------|
| 1 | Open the payout detail page directly by its id |
**What you should see**: The message "No sessions on this payout." in place of the line table. No empty/garbled table, no error.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

## G. Payslip PDF

### TC-PAY-070: Payslip PDF (EN) shows lines, RM amounts, and the correct total
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator with the app language EN. A payout with at least two lines (note the on-screen Total).
| Step | Action |
|------|--------|
| 1 | On the payout detail, click Download payslip |
| 2 | Open the PDF |
**What you should see**: A PDF titled "PAYSLIP" with the centre's brand, the teacher name, the month (e.g. "July 2026"), and a status badge; a table with columns Date, Class, Rate, Present, Amount; one row per session; a highlighted "Net pay" box whose figure equals the on-screen "Net pay". The footer reads "<brand>  ·  <month>" and "Powered by Kelasapp". Money shows the RM symbol (never "MYR"); dates DD/MM/YYYY.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-071: Payslip PDF (BM) uses Malay labels and RM, totals still reconcile
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator; switch the app language to Bahasa Melayu (BM). The same payout as TC-PAY-070.
| Step | Action |
|------|--------|
| 1 | With the app in BM, open the payout and Download payslip |
| 2 | Open the PDF |
**What you should see**: The PDF title is "SLIP GAJI", the column heads read Tarikh / Kelas / Kadar / Hadir / Jumlah, the highlighted box label is "Bayaran bersih", the month name is Malay (e.g. "Julai 2026"), a missing rate shows "Kadar belum ditetapkan", and the footer reads "Dikuasakan oleh Kelasapp". Amounts still show RM and "Bayaran bersih" equals the on-screen amount. No English leakage in the labels.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: the payslip PDF "Powered by" line and month names used to render in English regardless of language; fixed in e86b941.

### TC-PAY-072: Payslip filename carries the pay period
**Tags**: @regression **Severity**: S4 Low | **Priority**: P4 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator. Any payout (note its month).
| Step | Action |
|------|--------|
| 1 | Click Download payslip and note the saved filename |
**What you should see**: The file downloads as "payslip-YYYY-MM-01.pdf" (the period is stored as the first day of the pay month, e.g. payslip-2026-07-01.pdf for July 2026), with Content-Type application/pdf.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-073: Payslip for a "Rate not set" payout shows the flag and RM 0.00 line
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator. The "Rate not set" payout from TC-PAY-034.
| Step | Action |
|------|--------|
| 1 | Download its payslip and open the PDF |
**What you should see**: The Rate cell reads "Rate not set" (or "Kadar belum ditetapkan" in BM) and the Amount is RM 0.00, matching the on-screen detail. The "Net pay" box reflects the RM 0.00 line.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

## H. Permissions

### TC-PAY-100: Teacher cannot access the payroll pages
**Tags**: @smoke @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Log in as the teacher `teacher@kelastest.local` / `password12345` (linked to teacher "Ustazah Fatimah").
| Step | Action |
|------|--------|
| 1 | Navigate directly to /dashboard/payroll |
| 2 | Navigate directly to a known payout detail URL /dashboard/payroll/<id> |
**What you should see**: Both redirect to /dashboard/attendance (the operator route group guard). No payout list, amounts, or detail are shown. (The teacher's own pay surface is /dashboard/my-pay, covered in TC-PAY-127/128; it must NOT expose other teachers' pay.)
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-101: Teacher cannot call the payroll mutation APIs directly (server 401, even if UI is bypassed)
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: API
**Before you start**: Authenticated as the teacher `teacher@kelastest.local` / `password12345` (reuse the teacher's browser session). Note a payout id from the operator's payroll list URL (any status).
| Step | Action |
|------|--------|
| 1 | POST /api/payouts/generate with {"period":"<current YYYY-MM>"} |
| 2 | PATCH /api/payouts/<that payout id> with {"action":"void"} |
| 3 | PATCH /api/payouts/<that payout id> with {"action":"mark_paid","paidMethod":"cash","paidAt":"<today YYYY-MM-DD>"} |
| 4 | PATCH /api/payouts/<that payout id> with {"action":"add_adjustment","category":"bonus","amount":10} |
**What you should see**: Each returns HTTP 401 with "Forbidden: operators only". No payout is generated, voided, paid, or adjusted (requireOperatorContext rejects the teacher role). Note: GET /api/payouts/<id>/pdf is deliberately NOT operator-only any more; since b175d3e a teacher may fetch their OWN payslip (covered in TC-PAY-128).
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-102: Unauthenticated / no-org request is rejected
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: API
**Before you start**: No login session (incognito), or a user with no active organisation.
| Step | Action |
|------|--------|
| 1 | POST /api/payouts/generate with {"period":"<current YYYY-MM>"} and no session |
| 2 | In a browser, open /dashboard/payroll with no session |
**What you should see**: The API returns HTTP 401; the page redirects to onboarding / organisation selection (or sign-in). No payroll data is reachable.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

## I. Cross-tenant isolation (IDOR)

### TC-PAY-110: Org B cannot open or download org A's payout
**Tags**: @smoke @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: API
**Before you start**: Two orgs (A and B). As operator of org A, create a payout and copy its id from the URL. Then switch to / log in as operator of org B.
| Step | Action |
|------|--------|
| 1 | As org B, open /dashboard/payroll/<org-A-payout-id> |
| 2 | As org B, GET /api/payouts/<org-A-payout-id>/pdf |
| 3 | As org B, PATCH /api/payouts/<org-A-payout-id> with {"action":"void"} |
**What you should see**: The page shows Not found (404); the PDF endpoint returns 404 "Not found"; the PATCH returns 404 "not_found". Org A's payout is never rendered, downloaded, or mutated. No teacher names or amounts from org A leak.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-111: Running payroll for org B never touches org A's sessions or payouts
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Two orgs, each with completed sessions for the same month. Log in as operator of org B.
| Step | Action |
|------|--------|
| 1 | As org B, Run payroll for the month |
| 2 | Open Teacher pay and read the list |
| 3 | (Optional) As org A, confirm org A's payouts are unaffected |
**What you should see**: Only org B teachers and amounts appear. Org A has no payout created by org B's run; org A's existing payouts are unchanged. Generation is scoped to the caller's org.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-112: Mark-paid / void cannot reach another org's payout via the id in the body or URL
**Tags**: @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: API
**Before you start**: Org A has a Draft payout (note its id). Authenticated as org B operator.
| Step | Action |
|------|--------|
| 1 | As org B, PATCH /api/payouts/<org-A-payout-id> with {"action":"mark_paid","paidMethod":"cash","paidAt":"<today>"} |
**What you should see**: HTTP 404 "not_found" (the org scope on the lookup means org B's query never matches org A's row). Org A's payout stays Draft. No cross-org state change.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

## J. Generation input validation

### TC-PAY-120: Run payroll with a malformed period is rejected (server-side)
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: API
**Before you start**: Operator authenticated.
**Test Data**: period values "2026-13" (bad month), "2026/06" (wrong separator), "June 2026", "" (empty).
| Step | Action |
|------|--------|
| 1 | POST /api/payouts/generate with {"period":"2026-13"} |
| 2 | Repeat with {"period":"2026/06"}, then "June 2026", then "" |
**What you should see**: Each returns HTTP 422 "Invalid period" with a "month_ym" issue. No payout is generated. The schema requires the YYYY-MM format.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-121: Missing period field is rejected
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: API
**Before you start**: Operator authenticated.
| Step | Action |
|------|--------|
| 1 | POST /api/payouts/generate with {} (no period) |
**What you should see**: HTTP 422 "Invalid period". Nothing generated.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-122: Month picker normalises an out-of-range month param in the URL
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator on Teacher pay.
**Test Data**: append ?month=banana then ?month=2026-13 to the page URL.
| Step | Action |
|------|--------|
| 1 | Open /dashboard/payroll?month=banana |
| 2 | Open /dashboard/payroll?month=2026-13 |
**What you should see**: The page does not crash; an invalid month param falls back to the current KL month (the page only honours a YYYY-MM month). The list reflects the current month.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

## K. Bulk mark-paid (list) [added 2026-07-04, ab86cf3 CX11]

### TC-PAY-123: Bulk mark-paid pays every selected draft with one method and date
**Tags**: @smoke @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Log in as the operator `operator@kelastest.local` / `newpassword6789`. A month with at least two Draft payouts for different teachers (mark a session for each teacher this month, then Run payroll; note both teacher names and Amounts).
**Test Data**: method = Bank transfer; Paid on = today; Reference = "BULK-TX-01".
| Step | Action |
|------|--------|
| 1 | On Teacher pay, tick the checkbox on two Draft rows |
| 2 | In the bar that appears above the table, click "Mark paid (2)" |
| 3 | In the sheet, keep Bank transfer, set Paid on to today, type "BULK-TX-01", click "Mark paid (2)" |
**What you should see**: While rows are ticked, the bar reads "2 selected" next to the button "Mark paid (2)". The sheet says "The method and date below apply to all 2 selected payouts." After confirming: a success toast "2 payouts marked paid", the sheet closes, the selection clears, and both rows show the Paid badge. Each payout's detail now reads "Paid on DD/MM/YYYY via Bank transfer · BULK-TX-01" and its amounts are unchanged. (BM: button "Tandakan dibayar (2)", toast "2 bayaran ditandakan sebagai dibayar".)
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked
**Notes**: Each selected payout goes through the same PATCH /api/payouts/<id> endpoint and draft-only service guard as single mark-paid (TC-PAY-040).

### TC-PAY-124: Bulk partial failure is reported per teacher and never overwrites an existing payment
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator, with the payroll list open in two browser tabs. A month with three Draft payouts (note the three teacher names).
**Test Data**: tab B pays ONE of the three with method Cash first; tab A then bulk-pays all three with Bank transfer, today.
| Step | Action |
|------|--------|
| 1 | Tab A: tick all three Draft rows, but do NOT submit yet |
| 2 | Tab B: open one of those three payouts, Mark as paid with Cash, today |
| 3 | Tab A (without refreshing): click "Mark paid (3)", set Bank transfer and today, confirm |
**What you should see**: The sheet STAYS OPEN and shows "Not marked (check each): <the teacher already paid in tab B>". A toast "2 payouts marked paid" still appears for the two that went through. After refreshing, those two show Paid via Bank transfer, while the tab-B payout keeps its ORIGINAL "Paid on DD/MM/YYYY via Cash" summary: the failed attempt answered HTTP 409 "not_draft" and recorded nothing, so no payout is paid twice or overwritten. (BM failure line: "Tidak ditandakan (semak satu persatu): <name>".)
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-125: Double-clicking the bulk confirm button cannot pay a payout twice
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator. A month with two Draft payouts.
| Step | Action |
|------|--------|
| 1 | Tick both rows, click "Mark paid (2)", fill in method and date |
| 2 | Click the confirm button "Mark paid (2)" twice in fast succession |
| 3 | Open each payout's detail |
**What you should see**: During the run the confirm button is disabled and reads "Marking...", so the second click does nothing. Each payout carries exactly ONE "Paid on ... via ..." summary and its amount is unchanged. Even if a duplicate request slipped through, the server's draft-only guard answers 409 "not_draft" without recording a second payment. After success the sheet closes and the selection clears; the now-Paid rows can no longer be selected, so the same batch cannot be resubmitted.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-126: Row selection offers only Draft payouts; select-all skips Paid rows
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator; a month with at least one Draft and one Paid payout (Void payouts never appear in this list at all).
| Step | Action |
|------|--------|
| 1 | Look at the leftmost checkbox column |
| 2 | Try to tick the Paid row's checkbox |
| 3 | Tick the header ("Select all") checkbox |
| 4 | Untick the header checkbox |
**What you should see**: Only Draft rows have an active checkbox; the Paid row's checkbox is disabled and cannot be ticked. The header checkbox selects every selectable (Draft) row on the current page; the bar above the table then reads "<n> selected" where n counts only the Draft rows, next to "Mark paid (n)". Unticking the header clears the selection and the bar disappears. There is no way to aim a bulk action at a Paid or Void payout from this list.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

## L. Teacher self-service: My pay + own payslip [added 2026-07-04, b175d3e + 1ee30f4]

### TC-PAY-127: Teacher's My pay shows each month's status: In process while draft, Paid with date once paid, void hidden
**Tags**: @smoke @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Teacher `teacher@kelastest.local` / `password12345` (Ustazah Fatimah) has a completed (marked) session this month, and the operator has NOT yet run payroll for the month. Keep the operator signed in on a second browser.
| Step | Action |
|------|--------|
| 1 | As the teacher, open Dashboard > My pay (/dashboard/my-pay) |
| 2 | As the operator, run payroll for the current month |
| 3 | As the teacher, reload My pay |
| 4 | As the operator, open that payout and Mark as paid (Bank transfer, today) |
| 5 | As the teacher, reload My pay |
| 6 | As the operator, Void the payout; as the teacher, reload once more |
**What you should see**: Step 1: "No payslips yet. They'll appear here once your centre marks a payout as paid." Step 3: a row for the month (e.g. "July 2026") with the NET amount and the badge "In process"; no download button while the payout is a draft. Step 5: the badge becomes "Paid DD/MM/YYYY" and a "Download payslip" button appears. Step 6: the month disappears (void payouts are hidden from the teacher). BM: "Dalam proses", "Dibayar DD/MM/YYYY", "Muat turun slip gaji".
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: My Pay used to list only already-paid months, so a generated-but-unpaid month was invisible and the page could not answer "has my money been sent?"; fixed in 1ee30f4 (CX7). Draft visibility is intended (service test "my-pay shows draft and paid payouts, hides void, scoped to the teacher").

### TC-PAY-128: Teacher downloads their OWN payslip; another teacher's payslip id returns 404 (IDOR)
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: API
**Before you start**: The teacher from TC-PAY-127 signed in, with at least one Paid payout. Separately, as the operator, open a payout belonging to a DIFFERENT teacher and copy its id from the URL /dashboard/payroll/<id>.
| Step | Action |
|------|--------|
| 1 | On My pay, click "Download payslip" on the paid month |
| 2 | In the same teacher browser, GET /api/payouts/<other-teacher-payout-id>/pdf |
| 3 | Scan the My pay list for anyone else's months |
**What you should see**: Step 1 downloads the teacher's own payslip PDF (title "PAYSLIP", their own name, net figure matching the on-screen row). Step 2 returns HTTP 404 {"error":"Not found"}: deliberately not-found rather than 403, so the response does not even confirm the payout exists; no PDF bytes are returned. Step 3: only Ustazah Fatimah's own months are listed, never another teacher's pay. ALSO: a teacher who crafts the URL of their OWN DRAFT payout gets the same 404; drafts are downloadable only once marked paid.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked
**Notes**: Teacher payslip access added in b175d3e (before it, this endpoint was operator-only). REGRESSION: the ownership check used to be status-independent, so a teacher could URL-fetch their own still-draft payslip and see provisional numbers; locked to paid-only in 346b4d5 (decided 2026-07-04). Operators still preview drafts as before.

## M. Adjustments (bonus / deduction / reimbursement / correction) [feature 215a3c8, catalogued 2026-07-04]

### TC-PAY-129: Bonus raises Net pay, leaves the sessions subtotal and the list's gross untouched
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator. A Draft payout whose "Sessions subtotal" is a known figure (e.g. RM 100.00 from one per_session RM 100.00 session).
**Test Data**: Type = Bonus; Amount (RM) = 50.00; Note = "Raya bonus".
| Step | Action |
|------|--------|
| 1 | On the payout detail, under "Adjustments", click "Add adjustment" |
| 2 | Pick Bonus, enter 50.00, note "Raya bonus", save |
| 3 | Click Download payslip and open the PDF |
**What you should see**: The Adjustments list shows "Bonus Raya bonus" at RM 50.00. "Sessions subtotal" stays RM 100.00; "Net pay" and the amount in the card header become RM 150.00. Back on the month list, the Amount column still shows RM 100.00 (the list shows gross session pay only, by design). The payslip gains an "Adjustments" block with "Sessions subtotal" RM 100.00 and "Bonus (Raya bonus)" RM 50.00, and its "Net pay" box reads RM 150.00.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-130: Deduction is stored negative and subtracts from Net pay; removing it restores the total
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator. A Draft payout with "Sessions subtotal" RM 100.00 and no adjustments yet.
**Test Data**: Type = Deduction; Amount (RM) = 30.00; Note = "Advance".
| Step | Action |
|------|--------|
| 1 | Add the adjustment: Deduction, 30.00, "Advance" |
| 2 | Read the Adjustments list and Net pay |
| 3 | Click the X next to the deduction line |
**What you should see**: The deduction line shows -RM 30.00 (displayed negative even though 30.00 was typed); "Net pay" drops to RM 70.00 while "Sessions subtotal" stays RM 100.00. The form's helper text reads "Deductions (advances, penalties) are subtracted; bonuses and reimbursements are added." (BM: "Potongan (pendahuluan, penalti) ditolak; bonus dan bayaran balik ditambah.") After removing the line, Net pay returns to RM 100.00 and the list shows "No adjustments."
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-131: Re-running payroll preserves adjustments and never duplicates them
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator. A Draft payout with one session line (RM 100.00) plus a Bonus of RM 25.00 (Net pay RM 125.00).
| Step | Action |
|------|--------|
| 1 | Click Run payroll again for the same month |
| 2 | Reopen the payout |
**What you should see**: The result reads "0 created, 1 refreshed, 0 already paid." The payout still has exactly one session line and exactly one Bonus line; Net pay stays RM 125.00. A re-run re-snapshots the session lines but never wipes or doubles operator-added adjustments.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-132: A paid payout's adjustments are frozen (read-only in UI, 409 via API)
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: API
**Before you start**: Operator. A PAID payout that carries at least one adjustment (note its id from the URL /dashboard/payroll/<id>).
| Step | Action |
|------|--------|
| 1 | Open the paid payout's detail and inspect the Adjustments block |
| 2 | PATCH /api/payouts/<id> with {"action":"add_adjustment","category":"bonus","amount":10} |
| 3 | PATCH /api/payouts/<id> with {"action":"remove_adjustment","lineId":"00000000-0000-0000-0000-000000000000"} |
**What you should see**: The detail lists the existing adjustments read-only: no "Add adjustment" button and no X remove control. Both API calls return HTTP 409 {"error":"not_draft"}; Net pay is unchanged. Once paid, the whole pay statement is frozen.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-PAY-133: Adjustment input limits are enforced server-side
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: API
**Before you start**: Operator. A Draft payout id (from the detail URL). Note its Net pay first.
**Test Data**: amounts 0, -5, 10.123, 1000001; category "penalty"; a note of 201 characters ("A" x 201).
| Step | Action |
|------|--------|
| 1 | PATCH /api/payouts/<id> with {"action":"add_adjustment","category":"bonus","amount":0} |
| 2 | Repeat with amount -5, then 10.123, then 1000001 |
| 3 | Repeat with {"action":"add_adjustment","category":"penalty","amount":10} |
| 4 | Repeat with a valid amount but a 201-character note |
**What you should see**: Every request returns HTTP 422 "Invalid input" (amount must be positive, at most 2 decimal places, at most 1,000,000; category must be one of bonus / deduction / reimbursement / correction; note at most 200 characters). No line is added and Net pay is unchanged. In the UI, the save button stays disabled while the amount box is empty.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

## N. Regression guards from fixed bugs [added 2026-07-04]

### TC-PAY-134: A crafted attendance mark for a non-enrolled student is rejected, so per-student pay cannot be inflated
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: API
**Before you start**: Operator. A per_student class (rate RM 10.00) that meets today, with its enrolled students known. Also note the id of a student NOT enrolled in that class (open another class's student, the id is in the URL).
| Step | Action |
|------|--------|
| 1 | POST /api/attendance with {"classId":"<class id>","date":"<today YYYY-MM-DD>","marks":[{"studentId":"<non-enrolled student id>","status":"present"}]} |
| 2 | Run payroll for the month and open the teacher's payout |
**What you should see**: Step 1 returns HTTP 422 {"error":"not_on_roster"} and stores nothing. The payout's Present headcount and Amount count only genuinely enrolled students; the crafted mark adds no pay.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: markAttendance used to accept marks for students not enrolled in the class on that date, letting a crafted request inflate a per-student session's frozen pay or insert orphan rows; fixed in f31491a (H3).

### TC-PAY-135: A failed void is shown in the dialog instead of closing silently
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator; the SAME Draft payout's detail page open in two browser tabs.
| Step | Action |
|------|--------|
| 1 | Tab B: click Void payout and confirm (this succeeds) |
| 2 | Tab A (stale, still showing the old status): click Void payout and confirm |
**What you should see**: In tab A the confirmation dialog STAYS OPEN and shows "Something went wrong. Please try again." (BM: "Sesuatu tidak kena. Sila cuba lagi."). It must not close as if the action worked; the server answered 409 "already_void". After refreshing, the payout is gone from the month list (tab B's void stands, exactly one void recorded).
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: the void and mark-paid buttons used to fail silently (the dialog closed with no message on a non-OK response); surfaced in 31777bd.

### TC-PAY-136: Payroll table basics: # column, range-of-total count, CSV export, remembered page size
**Tags**: @regression **Severity**: S4 Low | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator; a month with several payouts (count them first).
| Step | Action |
|------|--------|
| 1 | Read the leftmost "#" column and the count in the table footer |
| 2 | Sort by Teacher descending, read "#" again |
| 3 | Click "Export CSV" and open the downloaded file |
| 4 | Change "Rows per page" to 10, then reload the page |
**What you should see**: "#" numbers the rows 1..n for the current view and renumbers after the sort (it is positional, not an id). The footer shows a range-of-total count in the pattern "1-25 of 87" (BM: "1-25 daripada 87"). The CSV is named payroll-YYYY-MM-DD.csv (today's date), its header row uses the on-screen labels (Teacher, Sessions, Amount, Status), and it contains one row per payout in the current (filtered) view with the translated status labels. The rows-per-page choice (default 25) survives the reload.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked
**Notes**: Table usability pass 746df0b (all list pages share this DataTable).

## Coverage note
Techniques walked (per §5 matrix): happy path (A: PAY-001 per_session, PAY-002 per_student, PAY-005/006
multi-session/multi-class; K: PAY-123 bulk mark-paid; L: PAY-127 teacher My pay; M: PAY-129/130 adjustments);
equivalence + boundary (PAY-035 zero present, PAY-042 reference 120+1, PAY-008/122 month bounds, PAY-133
adjustment amount 0 / negative / 3dp / over-max and note 200+1); negative / validation incl. server-side
bypass (PAY-042/043/044 mark-paid, PAY-120/121 generation period, PAY-101 UI-bypass via API, PAY-132/133
adjustments, PAY-134 crafted attendance mark); format / locale (PAY-070/071 RM + EN/BM incl. "Bayaran
bersih" and "Dikuasakan oleh Kelasapp", PAY-072 filename, PAY-043 date format, bulk/My-pay BM strings in
PAY-123/124/127); permissions / role (PAY-100 teacher route redirect, PAY-101 mutation APIs 401, PAY-102
unauth, PAY-127/128 teacher self-service read-only scope); cross-tenant / IDOR (PAY-110 open/download,
PAY-111 generation isolation, PAY-112 mark-paid/void scope, PAY-128 teacher-vs-teacher payslip IDOR inside
one org); state transition incl. illegal (PAY-050 paid skipped, PAY-051 mark non-draft paid, PAY-052/053
void then regen, PAY-054 void a void, PAY-055 not-found action, PAY-124 bulk hitting a just-paid draft,
PAY-132 adjust a paid payout, PAY-135 void a just-voided payout); concurrency / idempotency (PAY-020
refresh, PAY-021 top-up, PAY-022 no double-pay, PAY-023 double-click generate, PAY-125 bulk double-submit);
empty / loading / error states (PAY-007 zero generated with the rich empty state, PAY-063 no-line detail,
PAY-061 filtered-to-zero + Reset, PAY-127 teacher empty state, PAY-135 surfaced failure); data integrity
(PAY-004 completed-only, PAY-022 at-most-once, gross-vs-net reconciliation across PAY-129/130/131 and the
payslip in PAY-070/071/073, PAY-134 roster guard on frozen pay); rate freeze + substitute + rate-missing
(PAY-030/031/032/033/034/035); selection / bulk UI (PAY-126); table basics (PAY-136).

Reconciliation record 2026-07-04 (catalog was assembled 2026-06-30 and never executed, so stale cases were
rewritten IN PLACE keeping their TC IDs; nothing was renumbered): PAY-001/005/006/062/073 (detail totals are
now "Sessions subtotal" + "Net pay", not a single "Total"); PAY-007 (rich empty state replaced the plain
empty message); PAY-061 (the separate teacher filter + status dropdown no longer exist; one all-column
search box "Search teacher, status..." with Reset); PAY-070/071 (payslip now has a "Net pay" box,
adjustments block, and localized footer; BM title is "SLIP GAJI", net label "Bayaran bersih"); PAY-072
(filename is payslip-YYYY-MM-01.pdf, not payslip-YYYY-MM.pdf); PAY-100 (teacher self-service pages now
exist; redirect assertion unchanged); PAY-101 (the payslip GET is no longer operator-only since b175d3e, so
the 401 assertion now covers only generate / mark_paid / void / add_adjustment). No cases were deleted: no
tested feature was removed. The catalog contained no Clerk-specific steps; the header's role model was
updated for Better Auth (roles from org membership; teachers get My pay + own payslip).

Observed behaviors a tester must NOT report as bugs: the month list's Amount column shows GROSS while the
detail header / Net pay / payslip / My pay show NET (by design, PAY-129); a teacher can fetch their OWN
draft payslip by direct URL because the ownership check is status-independent (PAY-128 note); the global
table search matches the RAW status value ("paid"/"draft" in English) even in the BM UI (PAY-061).

Not applicable / out of scope here: XSS/SQLi at render-or-store (payouts expose no free-text user input
that reaches render beyond the operator-only optional Reference and adjustment note, covered by the
max-length guards PAY-042/133; a Reference XSS spot-check belongs in the cross-cutting catalog where the
escaping convention is verified once); accessibility (keyboard/contrast) is covered once in
test-plan-crosscutting.md for the shared DataTable / Sheet / AlertDialog components rather than repeated
per module; non-functional (Run payroll fan-out / N+1 at ~100 teachers across many sessions, and bulk
mark-paid latency since it is sequential by design) is flagged for the load pass, not this functional
catalog.
