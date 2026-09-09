# Test plan: Billing & Invoicing (M4)

> Exhaustive manual catalog for billing. Format + method: [QA-METHODOLOGY.md](QA-METHODOLOGY.md).
> Grounded in `src/features/invoicing/service.ts`, the 36 invoicing service tests, and [FLOWS.md](../FLOWS.md) §4.
> Default tier T1 (money). Roles: operator (full), staff (subset; no payment settings), teacher (no access), public (token).
> Updated 2026-07-04 for the Jul 2-4 billing commits (claims-in-flow a39c059, recoverable void c1ee98d,
> all-or-nothing run billing 6ddce23, receipt fix 261e141, public pending state 917c612, verification
> queue surfacing de4be04, row share 998a2b5, public hardening 3cddbee, and the UI/BM passes).
> 61 cases. Auth is Better Auth (Clerk removed 2026-07-02).
>
> Dev logins (local dev DB): operator `operator@kelastest.local` / `newpassword6789`;
> teacher `teacher@kelastest.local` / `password12345`. Billing lives at `/dashboard/billing`
> (nav item "Billing"). Public invoice pages live at `/invoice/<token>` (no login).
>
> Smoke subset (@smoke): TC-BILL-001, 010, 020, 070, 073, 102.

## A. Generation ("Run billing")

### TC-BILL-001: Run billing creates one family invoice per guardian, lines grouped by child
**Tags**: @smoke @regression **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Log in as operator. Have a guardian with 2 enrolled children in active classes (go to Students > Guardians, open one, confirm 2 students with active enrolments).
**Test Data**: the month with active enrolments (current month).
| Step | Action |
|------|--------|
| 1 | Go to Billing |
| 2 | Set the billing month picker to the current month |
| 3 | Click "Generate invoices" |
| 4 | Open the new invoice for that guardian |
**What you should see**: The result line reads "N created, 0 updated, 0 skipped". ONE invoice for the guardian with status "Draft", numbered `INV-YYYYMM-NNNN` (prefix from settings), with a line item per child across all their classes grouped under each child's name; total = sum of the children's fees.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-BILL-002: Adult learner with no guardian is billed directly
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator; a student with no guardian, enrolled + active.
| Step | Action |
|------|--------|
| 1 | Run billing (Generate invoices) for the month |
| 2 | Find the invoice for that student in the list |
**What you should see**: An invoice with the student as "Bill to" payer (not skipped). Total = their fee.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-003: Re-running billing is idempotent and tops up a draft
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator; billing already run once for the month (a draft exists for a guardian).
| Step | Action |
|------|--------|
| 1 | Enrol a new child under that guardian into an active class |
| 2 | Click "Generate invoices" again for the same month |
| 3 | Open the guardian's invoice |
**What you should see**: The result line reads "0 created, 1 updated, ... skipped". Still ONE invoice for the guardian (no duplicate); the new child appears as an added line; total updated. Issued/paid invoices are never modified (they count under "skipped").
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-004: Paused enrolment is skipped in generation
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator; a student whose enrolment is Paused.
| Step | Action |
|------|--------|
| 1 | Run billing for the month |
| 2 | Open the payer's invoice (or note none is created if that was the only enrolment) |
**What you should see**: No line item for the paused enrolment. Only enrolments with status Active are billed.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-005: Fee override is reflected in the line amount
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator; an enrolment with a fee override different from the class monthly fee (set it on the enrolment first; note the override value, e.g. RM 80.00 where the class fee is RM 100.00).
| Step | Action |
|------|--------|
| 1 | Run billing for the month |
| 2 | Open the invoice and read that child's line amount |
**What you should see**: The line uses the override amount (RM 80.00), not the class fee.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-006: Run billing with no active enrolments produces nothing, with a clear result
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Before you start**: Operator in an org/month with no active enrolments.
| Step | Action |
|------|--------|
| 1 | Click "Generate invoices" for that month |
**What you should see**: The result line reads "0 created, 0 updated, 0 skipped" (not an error, not a blank screen). The empty table shows "No invoices for this month yet" with the hint to use "Generate invoices".
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-007: Double-clicking Generate never produces a partial or duplicated run
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator; 2+ payers with active enrolments and no invoices yet for the month.
| Step | Action |
|------|--------|
| 1 | Click "Generate invoices" twice in fast succession (double-click) |
| 2 | When both requests finish, scan the invoice list for the month |
**What you should see**: Exactly ONE invoice per payer, no duplicates and no half-created set. The run is a single all-or-nothing transaction: a failure or a concurrent second click rolls back rather than leaving some families invoiced and some not.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: partial run-billing / concurrent double-click, commit 6ddce23.

### TC-BILL-008: Invoice numbers are unique and sequential within the centre
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator; 2+ payers with active enrolments; run billing for the month.
| Step | Action |
|------|--------|
| 1 | Read the invoice numbers of every invoice created for the month |
| 2 | (API check) Attempt to create a second invoice reusing an existing number via direct DB/API insert if you have tooling; otherwise skip this step |
**What you should see**: All numbers distinct and sequential (`INV-YYYYMM-0001`, `-0002`, ...). The database refuses a duplicate (org + invoice number) with a unique-constraint error, so duplicate numbers on parent-facing documents are impossible even under a race.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: duplicate invoice numbers, commit 6ddce23 (unique index `invoices_org_invoice_number_unique`, migration 0016).

### TC-BILL-009: Enrolment starting after the billed month is not billed (boundary)
**Tags**: @regression **Severity**: S2 High | **Priority**: P3 | **Tier**: T2
**Before you start**: Operator; one enrolment starting on the LAST day of the billed month, one starting on the 1st of the NEXT month (set the start dates on the enrolments first).
| Step | Action |
|------|--------|
| 1 | Run billing for the billed month |
| 2 | Open the payer's invoice(s) |
**What you should see**: The enrolment starting on the last day of the month IS billed; the one starting next month is NOT (generation includes enrolments with a start date on or before the month's last day).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## B. Issue

### TC-BILL-010: Issue a draft sets status Issued and a due date
**Tags**: @smoke @regression **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator; a Draft invoice exists. Note the centre's default due days (Billing > Settings area; default 14).
| Step | Action |
|------|--------|
| 1 | Open the draft invoice |
| 2 | Click "Issue invoice" |
**What you should see**: Status badge changes to "Issued"; the Due date shows today + the default due days (DD/MM/YYYY); the invoice now appears under the "Unpaid" filter on the billing list.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-011: Issue all issues every draft for the month and prompts the send step
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator; multiple drafts for the month.
| Step | Action |
|------|--------|
| 1 | On Billing, click "Issue all drafts" |
**What you should see**: Every draft for that month becomes Issued. The message reads "N invoices issued" followed by "Now send them: tap the WhatsApp icon on each row below." (points at the per-row share icons).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## C. Record payment

### TC-BILL-020: Record a full payment moves the invoice to Paid
**Tags**: @smoke @regression **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator; an Issued invoice with a known total (note the total).
**Test Data**: amount = the full total; method = "Bank transfer"; today's date.
| Step | Action |
|------|--------|
| 1 | Open the invoice, click "Record payment" |
| 2 | Enter the full amount, pick "Bank transfer", keep today's date |
| 3 | Save |
**What you should see**: Status becomes "Paid"; Balance shows RM 0.00; the payment appears in the Payments table with method "Bank transfer", type "Payment", and status "Verified" (operator-recorded payments count immediately, no verification queue).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-021: Partial payment moves to Partially paid and tracks the balance
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator; an Issued invoice (note the total, e.g. RM 250.00).
**Test Data**: amount = half the total (e.g. RM 125.00).
| Step | Action |
|------|--------|
| 1 | Record a payment of half the total |
**What you should see**: Status "Partially paid"; Balance = remaining half exactly (e.g. RM 125.00).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-022: Overpayment is rejected
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator; an Issued invoice (note the total).
**Test Data**: amount = total + RM 1.00.
| Step | Action |
|------|--------|
| 1 | Open "Record payment"; note the "Max: RM ..." hint under the amount field |
| 2 | Enter an amount greater than the balance and save |
**What you should see**: Rejected with "That is more than the balance owing." (BM: "Itu melebihi baki yang perlu dibayar."); invoice unchanged; no payment recorded. The server enforces the same cap (422 `exceeds_balance`) if the UI is bypassed.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-023: Recording a payment on a Draft or Voided invoice is rejected
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator; a Draft invoice and (separately) a Voided invoice.
| Step | Action |
|------|--------|
| 1 | Open the draft invoice: confirm no "Record payment" button is shown |
| 2 | Send POST `/api/invoicing/invoices/<id>/payments` directly with a valid body against the draft |
| 3 | Repeat step 2 against the voided invoice |
**What you should see**: The UI offers no Record payment on drafts or voided invoices. The API returns 409 with error `wrong_state` for both; no payment row is created.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-024: Payment amount zero / negative / >2 decimals is rejected
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator; an Issued invoice; open "Record payment".
**Test Data**: try 0, then -50, then 10.999.
| Step | Action |
|------|--------|
| 1 | Enter 0 as the amount and try to save |
| 2 | Enter -50 and try to save |
| 3 | Enter 10.999 and try to save |
**What you should see**: 0 and -50 are blocked with "Amount must be greater than 0." (BM: "Jumlah mesti lebih besar daripada 0."); 10.999 is blocked with "Use at most 2 decimal places." (BM: "Guna paling banyak 2 tempat perpuluhan."). No payment recorded. The API re-validates the same rules (422) if the UI is bypassed.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-025: Receipt attachment: valid image/PDF accepted, wrong type/oversize rejected
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator recording a payment (the "Receipt (optional)" field, hint "Image or PDF, up to 10MB").
**Test Data**: a JPG receipt; then a .exe renamed to .jpg; then a file over 10MB.
| Step | Action |
|------|--------|
| 1 | Attach the JPG and save the payment |
| 2 | New payment: attach the renamed .exe and save |
| 3 | New payment: attach the >10MB file and save |
**What you should see**: JPG stored (converted to WebP server-side) and viewable via "View receipt" in the payment row's kebab. The renamed .exe is rejected (the server sniffs the real file type from content, not the filename) and the oversize file is rejected; in both cases the UI shows "Something went wrong. Please try again." and no payment is saved with a bad file.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-026: Operator can view, replace, and remove a payment's receipt (settled rows only)
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator; an invoice with (a) a verified payment that has a receipt attached and (b) a pending self-service claim (submit one via the public page if needed).
**Test Data**: two different JPG files.
| Step | Action |
|------|--------|
| 1 | On the verified payment row, open the kebab menu: use "View receipt" |
| 2 | Use "Replace receipt" and pick the second JPG |
| 3 | Use "Remove receipt" and confirm in the "Remove this receipt?" dialog |
| 4 | Open the kebab on the PENDING claim row |
**What you should see**: Step 1 opens the stored receipt in a new tab. Step 2 swaps the file (row shows "Attached"). Step 3 dialog says "The payment stays recorded; only the attached proof is removed. You can add a new one later."; after confirming the row shows "None" and the payment amount/status are unchanged. Step 4: the pending row offers "View receipt" (and "Remove payment") but NOT replace/remove receipt: a pending claim's receipt is the parent's evidence.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: NEW FEATURE: receipt correction, commit 261e141.

### TC-BILL-027: Remove payment is a recoverable admin undo that recomputes the balance
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator; a Paid invoice whose full payment was recorded by mistake (record one if needed; note the amount).
| Step | Action |
|------|--------|
| 1 | On the payment row, open the kebab and choose "Remove payment" |
| 2 | Read the confirmation dialog, then confirm |
| 3 | Re-read the invoice summary |
**What you should see**: Dialog title "Remove this payment?" with "The amount stops counting toward this invoice and the balance recalculates. The record is kept for audit." After confirming: the row disappears from the Payments table (soft delete; kept for audit in the database), Paid drops by the amount, Balance reopens, and status returns to "Issued" (or "Partially paid" if other payments remain).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: NEW FEATURE: admin-reversible payments, commit a39c059.

## D. Refund

### TC-BILL-030: Refund with "reduce the bill" keeps the invoice settled
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator; a Paid invoice (note the total, e.g. RM 250.00).
**Test Data**: refund RM 50.00; "Also reduce the bill by this amount" = ticked (the default).
| Step | Action |
|------|--------|
| 1 | Open the invoice, open "More" > "Refund" |
| 2 | Enter RM 50.00, keep "Also reduce the bill by this amount" ticked, save |
**What you should see**: A credit line "Refund credit" of -RM 50.00 appears under "Other charges"; Total drops to RM 200.00; Paid nets to RM 200.00; Balance stays RM 0.00 and status stays "Paid" (settled). The refund row shows in Payments as type "Refund" with a minus amount.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-031: Refund only (no reduce) reopens the balance
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator; a Paid invoice (e.g. total RM 250.00, fully paid).
**Test Data**: refund RM 50.00; untick "Also reduce the bill by this amount".
| Step | Action |
|------|--------|
| 1 | "More" > "Refund"; enter RM 50.00; untick the reduce checkbox (hint reads "Recommended: keeps the invoice settled. Uncheck if they still owe this and will pay again."); save |
**What you should see**: Total unchanged (RM 250.00); Paid drops to RM 200.00; Balance reopens at RM 50.00; status moves to "Partially paid".
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-032: Refund is visible but disabled when there is nothing to refund
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator; an Issued invoice with no payments.
| Step | Action |
|------|--------|
| 1 | Open the invoice and open the "More" menu |
| 2 | (API check) POST a refund via `/api/invoicing/invoices/<id>/payments` with `kind: "refund"` |
**What you should see**: "Refund" is listed but greyed out with the hint "No payments yet" (BM: "Tiada bayaran lagi"), so operators can discover the action exists. The API returns 422 with `no_payment_to_refund`; the UI message for that reason is "There is no payment to refund."
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: CHANGED by commit c1ee98d: Refund used to hide itself entirely; it is now always listed, disabled with a hint.

## E. Adjustments

### TC-BILL-040: Manual discount/credit with a negative amount lowers the total
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator; an Issued invoice (note the total). Adjustments are offered on draft/issued/partially-paid invoices only.
**Test Data**: type = Discount, description "Sibling discount", amount -20.00 (the amount field label reads "Amount (use a negative number to reduce the total)").
| Step | Action |
|------|--------|
| 1 | Open the invoice, "More" > "Add adjustment" |
| 2 | Pick type "Discount", description "Sibling discount", amount -20.00, save |
**What you should see**: Total drops by RM 20.00; a "Sibling discount" line of -RM 20.00 appears under "Other charges". (Server contract: the API accepts any non-zero amount up to 2dp; a negative amount reduces the total, per the service tests.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: the client schema used to refuse negatives ("Amount must be greater than 0.") while the label and API allowed them; fixed in 70edbfa (2026-07-04, browser-verified: -10 on a draft dropped RM 300.00 to RM 290.00). A refusal of a negative amount here is a regression of that fix.

### TC-BILL-041: Adjustment requires a description and a non-zero amount
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Before you start**: Operator adding an adjustment.
| Step | Action |
|------|--------|
| 1 | Leave description blank, try to save |
| 2 | Enter amount 0, try to save |
**What you should see**: Blank description is blocked with "Add a short description." (BM: "Tambah penerangan ringkas."). Amount 0 is blocked ("Amount must be greater than 0." in the UI; the API separately rejects 0 with "Amount cannot be 0."). Nothing is saved.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-042: Adjustment description with a script payload is not executed
**Tags**: @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator adding an adjustment.
**Test Data**: description = `<script>alert(1)</script>`, amount -1.00.
| Step | Action |
|------|--------|
| 1 | Save an adjustment with that description |
| 2 | Open the invoice detail, the public invoice page, and download the invoice PDF |
**What you should see**: The text is shown escaped everywhere (no alert pops, no broken layout). No script runs in the dashboard, the public page, or the PDF.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## F. Void

### TC-BILL-050: Voiding an unpaid invoice excludes it from outstanding but keeps the record
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator; an Issued invoice with NO payments, contributing to a guardian's outstanding (note the guardian's outstanding figure first).
| Step | Action |
|------|--------|
| 1 | Open the invoice, "More" > "Void"; the dialog says "It stays in your records but no longer counts as owed. Give a reason." |
| 2 | Enter a reason (e.g. "Created in error") and confirm |
| 3 | Check the guardian's outstanding and the billing list |
**What you should see**: Status badge "Voided"; the guardian's outstanding drops by the invoice balance; the invoice stays visible in the list (filterable by status "Voided") as an audit record; the public link now shows the cancelled message instead of payment instructions.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-051: Void reason is optional in the UI, required non-empty at the API
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Before you start**: Operator voiding an unpaid invoice; plus API access for step 2.
| Step | Action |
|------|--------|
| 1 | Confirm the void with the reason box left blank |
| 2 | (API check) PATCH `/api/invoicing/invoices/<id>` with `{ "action": "void", "reason": "" }` on another voidable invoice |
**What you should see**: Step 1 succeeds: the UI substitutes "-" as the stored reason. Step 2 returns 422 "Invalid input" (the API requires a non-empty reason, max 300 chars).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: CHANGED: earlier drafts of this catalog asserted "blocked until a reason is given"; the shipped UI sends "-" for a blank reason.

### TC-BILL-052: Void refuses while verified money sits on the invoice, and tells the way out
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator; a Paid (or Partially paid) invoice with a verified payment on it.
| Step | Action |
|------|--------|
| 1 | "More" > "Void", enter a reason, confirm |
| 2 | Note the message shown in the dialog |
| 3 | Remove the payment (kebab > "Remove payment", confirm), then void again |
**What you should see**: Step 1-2: the void is refused and the dialog stays open showing "This invoice has verified payments. Remove or refund them first, then void." (BM: "Invois ini mempunyai bayaran yang disahkan. Buang atau pulangkan bayaran itu dahulu, kemudian batalkan."). The invoice is untouched. Step 3: after the payment is removed, the void succeeds.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: void stranding received money, commit c1ee98d.

### TC-BILL-053: A fully refunded invoice voids fine (money accounted for, not stranded)
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator; a Paid invoice. Refund the FULL paid amount ("More" > "Refund", untick "Also reduce the bill"), so net paid is RM 0.00.
| Step | Action |
|------|--------|
| 1 | "More" > "Void", enter a reason, confirm |
**What you should see**: The void succeeds (net verified money is zero). The payment and refund rows are both kept in the Payments table for audit.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: commit c1ee98d.

### TC-BILL-054: A mistaken void is recoverable: re-running billing mints a fresh invoice
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator; a voided invoice for a payer + month whose enrolments are still active (note its invoice number).
| Step | Action |
|------|--------|
| 1 | On Billing, click "Generate invoices" for the same month |
| 2 | Scan the list for that payer |
**What you should see**: A fresh Draft invoice is created for the same payer and month (the result line reads "1 created, ..."). Its invoice number is DIFFERENT from the voided one (numbers are never reused). Both invoices are listed: the old one "Voided", the new one "Draft".
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: void as a dead end, commits c1ee98d (partial unique indexes ignore voided, migration 0015) + 6ddce23 (distinct numbers).

### TC-BILL-055: A pending claim stuck on a voided invoice can be rejected but never verified
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator; an Issued invoice with a pending self-service claim (submit one via the public page), then void the invoice (it has no VERIFIED money, so the void succeeds).
| Step | Action |
|------|--------|
| 1 | Go to Billing > "Pending payments" and click "Verify" on that claim |
| 2 | Read the inline message, then click "Reject" |
**What you should see**: Verify is refused with "This invoice can no longer accept payments. Reject this claim instead." (BM: "Invois ini tidak lagi boleh menerima bayaran. Tolak tuntutan ini."). Reject succeeds and clears the claim; the voided invoice's paid amount stays RM 0.00.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: money verified onto a bill that no longer exists, commit c1ee98d.

## G. Overdue

### TC-BILL-060: Issued invoice past its due date shows Overdue
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator; an Issued or Partially paid invoice whose due date is in the past (back-date `due_at` in the dev DB, or use a seeded past-due invoice).
| Step | Action |
|------|--------|
| 1 | Open Billing and click the "Overdue" filter |
| 2 | Open the invoice detail |
**What you should see**: The invoice carries a red "Overdue" badge next to its status badge in both the list and the detail; its balance renders in the destructive tone. Overdue is computed, never stored: a Paid, Voided, or Draft invoice never shows it.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## H. Public page, self-service, verification

### TC-BILL-070: Public invoice link shows the invoice + payment details with no login
**Tags**: @smoke @regression **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator; an Issued invoice for a centre with a DuitNow QR and bank details configured. Copy its public link ("Copy link"). Open it in a private/incognito window (no session).
| Step | Action |
|------|--------|
| 1 | Open the copied public link with no login |
**What you should see**: Title "Pay your invoice" under the centre's name/logo; the invoice number, payer, month, line items, and "Amount due" in bold; a "How to pay" card with "Scan this DuitNow QR with your banking app" + the QR image and "Or transfer to" with Bank / Account number / Account name; below it the "Upload payment receipt" form; footer "Powered by Kelasapp". No dashboard, no login prompt.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-071: Public link to a Draft is hidden
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: A Draft invoice and its token (read `public_token` via the operator API `GET /api/invoicing/invoices/<id>`; the UI hides share actions on drafts).
| Step | Action |
|------|--------|
| 1 | Open `/invoice/<draft-token>` in a private window |
**What you should see**: The 404 not-found page. Drafts never render publicly; only issued/paid/voided invoices resolve by token.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-072: Self-service receipt upload creates a pending payment that does not count
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Public invoice page open (as a parent) for an invoice with a balance.
**Test Data**: a JPG receipt; amount = the balance; reference "TRX123". Note the receipt file is REQUIRED.
| Step | Action |
|------|--------|
| 1 | Try to submit with no file attached |
| 2 | Attach the JPG, enter the amount and reference, submit |
| 3 | As operator, open the invoice detail and the billing list |
**What you should see**: Step 1: blocked with "Please attach your receipt." Step 2: green confirmation "Thank you. Your payment has been submitted and is pending confirmation by the centre." Step 3: the invoice balance is UNCHANGED; the payment row shows status "Pending" with inline Verify/Reject; the billing list row carries a "1 pending" chip.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-073: Verifying a pending payment makes it count
**Tags**: @smoke @regression **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator; a pending self-service payment exists (from TC-BILL-072). Go to Billing > "Pending payments".
| Step | Action |
|------|--------|
| 1 | On the claim row, click "View receipt" and confirm it opens |
| 2 | Click "Verify" |
| 3 | Open the invoice |
**What you should see**: The claim leaves the queue ("No payments waiting for verification." when it was the last). On the invoice: the payment row now shows status "Verified", Paid increases by the amount, balance drops, and the invoice status updates (Partially paid or Paid).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-074: Rejecting a pending payment leaves the invoice untouched
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator; a pending self-service payment.
| Step | Action |
|------|--------|
| 1 | In "Pending payments", click "Reject" on the claim |
| 2 | Open the invoice |
**What you should see**: Balance and Paid unchanged; the claim leaves the queue; on the invoice the row shows status "Rejected" and renders dimmed (kept for audit, counts nothing).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-075: Self-service is blocked on a voided invoice
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: An invoice that is Voided but whose public token a parent still has.
| Step | Action |
|------|--------|
| 1 | Open the public link |
| 2 | (API check) POST a submit to `/api/invoice/<token>/submit` with a valid amount + file |
**What you should see**: The page shows "This invoice has been cancelled. Please contact the centre if you have any questions." with NO payment instructions and NO upload form. The direct API returns 422 `wrong_state`; no pending payment is created.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-076: Tampered invoice token is not found (IDOR)
**Tags**: @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: A valid public link.
| Step | Action |
|------|--------|
| 1 | Change a few characters of the token in the URL and open it |
| 2 | Try a token from a different org's invoice (if known) |
**What you should see**: The 404 not-found page in both cases; no invoice data leaks; no other org's invoice is reachable. Tokens are unguessable (`inv_` + 18 random bytes) and looked up exactly.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-077: A returning parent sees "receipt received", not a second payment demand
**Tags**: @regression **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: A pending self-service claim exists on an invoice (from TC-BILL-072); the parent's public link at hand.
| Step | Action |
|------|--------|
| 1 | Reopen the public link in a private window |
| 2 | Expand the collapsed link under the acknowledgement |
| 3 | As operator, Reject the claim; then reload the public link |
**What you should see**: Step 1: instead of the pay form, an acknowledgement "We have received your receipt" with "Your receipt (RM <amount>, sent <date>) is being checked by the centre. Nothing more to do for now." (BM: "Resit anda telah diterima" / "... sedang disemak oleh pusat ..."). Step 2: a collapsed escape hatch "Made another payment? Upload another receipt" reveals the how-to-pay card and the form (a genuine second payment is never blocked). Step 3: after rejection the acknowledgement disappears and the normal pay form is back.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: double-pay risk for returning parents, commit 917c612.

### TC-BILL-078: A public claim can be partial but never more than the amount due
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Public page for an Issued invoice (note the amount due, e.g. RM 250.00). For step 3, first have the operator record a partial payment (e.g. RM 200.00) so the balance is RM 50.00.
**Test Data**: claims of RM 251.00, RM 100.00, RM 100.00 (after balance drops to RM 50.00).
| Step | Action |
|------|--------|
| 1 | Submit a claim of RM 251.00 (above the amount due) with a receipt |
| 2 | Submit a claim of RM 100.00 (partial) |
| 3 | After the operator payment lands (balance RM 50.00), submit a claim of RM 100.00 |
**What you should see**: Steps 1 and 3 are rejected with "That is more than the amount due on this invoice." (BM: "Itu melebihi jumlah yang perlu dibayar pada invois ini."); step 2 succeeds. The cap is checked against VERIFIED money only (other pending claims do not reserve balance; the verify-time guard in TC-BILL-110 covers stacked claims).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: typo overpays via the public form, commit a39c059.

### TC-BILL-079: Double-tapping Submit creates exactly one claim; Enter submits the form
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Public page for an Issued invoice with a balance; a JPG receipt ready.
| Step | Action |
|------|--------|
| 1 | Fill amount + attach the receipt, then double-click "Submit receipt" as fast as you can |
| 2 | As operator, open Billing > "Pending payments" and count that payer's claims |
| 3 | Back on a fresh public form (new private window): fill the fields and press Enter in the amount field |
**What you should see**: Steps 1-2: exactly ONE pending claim (an idempotency key dedupes the double-tap/retry server-side). Step 3: Enter submits the form like clicking the button (it is a real form) and the thank-you confirmation appears.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Enter-key submit: commit 6e2b993.

## I. Sharing + PDF

### TC-BILL-080: WhatsApp reminder opens a prefilled chat for a valid MY phone
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Before you start**: Operator; an Issued invoice whose payer has a valid MY mobile.
| Step | Action |
|------|--------|
| 1 | On the invoice detail, click "WhatsApp reminder" |
**What you should see**: A wa.me chat opens to the payer's normalised number, prefilled exactly with: "Hi <name>, here is invoice <number> for <month>: <amount> due. View and pay here: <link>. Thank you." where <link> is the public invoice URL.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-081: WhatsApp reminder is disabled when the phone is missing
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Before you start**: A payer with no phone number on file.
| Step | Action |
|------|--------|
| 1 | Open their invoice detail and hover the WhatsApp button |
| 2 | On the billing list, hover the row's WhatsApp icon |
**What you should see**: Both are disabled with the tooltip "No phone number on file for this payer." (BM: "Tiada nombor telefon untuk pembayar ini."). No broken wa.me link opens.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-082: Invoice PDF has correct totals, RM, and localised labels (EN + BM)
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator viewing an invoice with a partial payment + an adjustment; centre bank details configured.
| Step | Action |
|------|--------|
| 1 | Click "Download PDF" (EN) |
| 2 | Switch the app language to BM and download again |
**What you should see**: Both PDFs show the centre brand/logo, line items, Subtotal, Paid, and "Balance due" matching the on-screen figures; money shows RM (never "MYR" text); dates DD/MM/YYYY; a "How to pay" block with the bank details; footer "Powered by Kelasapp". The BM PDF uses Malay labels throughout (e.g. "Jumlah kecil", "Baki perlu dibayar", "Dikeluarkan").
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: BM PDF localisation: commit e86b941.

### TC-BILL-083: Per-row share actions on the billing list (one tap per family)
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator; a month with a mix of Draft, Issued, and Voided invoices; at least one issued payer with a phone and one without.
| Step | Action |
|------|--------|
| 1 | Scan the last column of the billing list |
| 2 | Click the WhatsApp icon on an issued row (payer with phone) |
| 3 | Click the copy icon on the same row, then paste somewhere |
**What you should see**: Step 1: issued/paid rows carry WhatsApp + copy-link icons; Draft and Voided rows carry NONE (drafts are not parent-ready; voided must not be shared); the WhatsApp icon is disabled on the no-phone payer. Step 2: wa.me opens with the full prefilled reminder (same message as TC-BILL-080). Step 3: the icon flips to a check ("Copied!") and the clipboard holds the public `/invoice/<token>` link.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: NEW FEATURE: commit 998a2b5.

## J. Payment settings

### TC-BILL-090: Set bank (dropdown), account (digits-only), and DuitNow QR
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator (owner); Billing > "Payment settings".
**Test Data**: bank = Maybank; account typed as "1234 5678 90" (with spaces); a valid DuitNow Receive QR image.
| Step | Action |
|------|--------|
| 1 | Pick Maybank from the bank dropdown |
| 2 | Type the account number with spaces |
| 3 | Upload the QR; in the "Confirm your DuitNow QR" modal, scan it with a bank app, tick "I have scanned this QR and confirmed it is correct.", click "Use this QR" |
| 4 | Save |
**What you should see**: The account field strips non-digits as you type (shows 1234567890; hint "Numbers only, no spaces or dashes."). The QR modal reports "Valid DuitNow QR. Paying to <name>." before you can confirm. After saving: "Saved" confirmation, and the public invoice page now shows the QR + bank block.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-091: Account number and bank pairing are enforced server-side too
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator on Payment settings; API access for the bypass steps.
**Test Data**: account "abc123"; then account "123" (too short); then bank filled with account empty.
| Step | Action |
|------|--------|
| 1 | Try to type letters into the account field (UI) |
| 2 | PUT `/api/invoicing/settings` with `{ "bankName": "Maybank", "bankAccountNumber": "abc123" }` |
| 3 | PUT with `{ "bankName": "Maybank", "bankAccountNumber": "123" }` |
| 4 | Fill only the bank in the UI, leave account empty, save |
**What you should see**: Step 1: letters never appear (input strips non-digits). Steps 2-3: 422 "Invalid input" (the API enforces 5-20 digits; message key "Account number must be 5 to 20 digits."). Step 4: blocked with "Enter both the bank and the account number, or leave both empty." (a half-filled bank block never reaches parents).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-092: Unreadable QR is hard-blocked at confirm
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator uploading a QR on Payment settings.
**Test Data**: a non-QR image (random photo).
| Step | Action |
|------|--------|
| 1 | Upload the non-QR image |
**What you should see**: The confirm modal shows "We could not read this QR" with "This image is not a readable DuitNow QR. Please upload a clear image of your Receive QR (not blurry or cropped)."; the confirm/save path is blocked.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## K. Permissions + tenant isolation

### TC-BILL-100: Teacher cannot access billing
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Log in as the teacher (`teacher@kelastest.local` / `password12345`).
| Step | Action |
|------|--------|
| 1 | Navigate directly to `/dashboard/billing` |
| 2 | Call `GET /api/invoicing/invoices` directly with the teacher session |
**What you should see**: The page redirects to `/dashboard/attendance` (the teacher's area); the API returns 401 ("Forbidden: operators only"). No billing data is shown or returned.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-101: Cross-tenant: one org cannot open another org's invoice
**Tags**: @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Two orgs (A and B). As operator of org B, obtain org A's invoice id (from a known fixture or another session).
| Step | Action |
|------|--------|
| 1 | As org B, open `/dashboard/billing/<org-A-invoice-id>` |
| 2 | Call `GET /api/invoicing/invoices/<org-A-invoice-id>` while authed as org B |
**What you should see**: 404 not found in both; org A's invoice never renders or returns; no data leak (every query is org-scoped).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-102: Billing list shows only the current org's invoices
**Tags**: @smoke @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Org B operator; org A also has invoices.
| Step | Action |
|------|--------|
| 1 | Open Billing as org B and scan the list |
**What you should see**: Only org B invoices; none from org A. The pending-payments queue and its counts are also org-scoped.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-BILL-103: Payment settings are owner-only (staff blocked)
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: A staff-role login for the centre (invite one via the centre's team/organisation settings if none exists; otherwise mark Blocked). Payment settings control where parents' money is sent.
| Step | Action |
|------|--------|
| 1 | As staff, open Billing and look for the "Payment settings" button |
| 2 | Navigate directly to `/dashboard/billing/settings` |
| 3 | PUT `/api/invoicing/settings` with a valid body using the staff session |
**What you should see**: The settings button is hidden for staff; the direct URL redirects back to `/dashboard/billing`; the API returns 401 ("Forbidden: owner only"). Staff can still run billing and record payments.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## L. Verification queue surfacing + payment statuses

### TC-BILL-110: Verify refuses when a stacked claim no longer fits the balance
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator; an Issued invoice (e.g. total RM 250.00) with a pending claim of RM 200.00 (submit via the public page). Then record an operator payment of RM 200.00 so the balance drops to RM 50.00.
| Step | Action |
|------|--------|
| 1 | Go to Billing > "Pending payments" and click "Verify" on the RM 200.00 claim |
| 2 | Read the inline message |
| 3 | Click "Reject" on the same claim |
**What you should see**: Verify is refused with "This is more than the balance owing. Reject it, then record the correct amount manually." (BM: "Ini melebihi baki yang perlu dibayar. Tolak dahulu, kemudian rekodkan jumlah yang betul secara manual."). The claim stays pending (invoice untouched) until step 3 rejects it. Verifying can never push Paid above Total.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: stacked claims overpaying an invoice, commit a39c059.

### TC-BILL-111: Waiting receipts surface on the dashboard and the sidebar badge
**Tags**: @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator; start with ZERO pending claims, then submit 2 claims via public invoice links.
| Step | Action |
|------|--------|
| 1 | With zero claims, open the operator dashboard and the sidebar |
| 2 | Submit 2 public claims, reload the dashboard |
| 3 | Click "View all" on the card; verify one claim; return to the dashboard |
**What you should see**: Step 1: no receipts card, no badge on the Billing nav item. Step 2: a "Receipts to verify (2)" card (BM: "Resit untuk disahkan (2)") listing each claim (payer linked to its invoice, RM amount) and the Billing nav item carries a "2" badge on every page. Step 3: "View all" lands on Billing > Pending payments; after verifying one, the count drops to 1.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: NEW FEATURE: commit de4be04 (completes the CX1 loop with TC-BILL-077).

### TC-BILL-112: Invoice detail shows honest payment statuses with inline decisions
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator; one invoice carrying a verified operator payment, a pending public claim, and a rejected claim (build via TC-BILL-020/072/074).
| Step | Action |
|------|--------|
| 1 | Open the invoice's Payments table and read each row's Status |
| 2 | On the pending row, use the inline "Verify" or "Reject" buttons |
**What you should see**: Rows show badges "Verified" / "Pending" / "Rejected" (BM: "Disahkan" / "Menunggu" / "Ditolak"); rejected rows render dimmed. Pending rows carry inline Verify/Reject right next to the balance (no trip to the queue needed); deciding one refreshes the totals immediately.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: NEW FEATURE: commit a39c059.

## M. Public endpoint hardening + resilience

### TC-BILL-120: Public submit rejects oversized, absurd, and overlong inputs
**Tags**: @security @regression **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: A valid public invoice token; curl or a REST client for multipart POSTs to `/api/invoice/<token>/submit` (fields: amount, reference, file, idempotencyKey).
**Test Data**: a >10MB file; amount 1000001; a 300-character reference string.
| Step | Action |
|------|--------|
| 1 | POST with the >10MB file |
| 2 | POST with amount 1000001 and a small valid file |
| 3 | POST with a valid amount + file and the 300-char reference; then view the created claim as operator |
**What you should see**: Step 1: 413 `too_large`, rejected via Content-Length BEFORE the body is buffered into memory. Step 2: 422 `invalid_amount` (cap RM 1,000,000.00, matching the operator-side schema; NaN/Infinity also rejected). Step 3: accepted, but the stored reference is truncated to 120 characters.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: unguarded public inputs, commit 3cddbee.

### TC-BILL-121: Public page guides the parent when the centre has no payment method set
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: A centre with NO DuitNow QR and NO complete bank details (bank + account); an issued invoice's public link. Also test the half-filled case: bank name saved without an account number is impossible via settings (TC-BILL-091), but if legacy data has one, the bank block must not render.
| Step | Action |
|------|--------|
| 1 | Open the public link |
**What you should see**: The "How to pay" card shows "The centre hasn't set up online payment details yet. Please contact the centre directly for how to pay." (BM: "Pusat belum menetapkan cara pembayaran dalam talian. Sila hubungi pusat secara terus untuk cara membayar.") instead of an empty card. The bank block renders only when BOTH bank and account number exist. The receipt upload form still works below.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: parent staring at an empty payment card (CX15), commit 390b663.

### TC-BILL-122: Public invoice page shows a loading skeleton, never a blank screen
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Before you start**: A valid public link; browser DevTools network throttling set to "Slow 3G".
| Step | Action |
|------|--------|
| 1 | Open the public link with throttling on and watch the first paint |
**What you should see**: A skeleton mirroring the real layout (logo, amount card, pay section) renders immediately while the server resolves the invoice and signed QR/logo URLs; it is replaced by the real content. Never a blank white screen.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Added in commit 31777bd.

## N. Locale + table usability

### TC-BILL-130: BM: destructive Void is worded distinctly from Cancel, money terms consistent
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Switch the app language to BM. Operator; any voidable invoice.
| Step | Action |
|------|--------|
| 1 | Open "More" and read the void action, then open the void dialog and read both buttons |
| 2 | Scan the billing list column heads and status badges in BM |
**What you should see**: The destructive action reads "Batalkan invois" while the dismiss button reads "Batal" (a tester or operator can never confuse "cancel the dialog" with "void the invoice"). Money terms are consistent across billing screens: "Jumlah" (Total/Amount), "Baki" (Balance), "Telah dibayar" (Paid), "Sebahagian dibayar" (Partially paid), "Dikeluarkan" (Issued), "Dibatalkan" (Voided).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: BM void/cancel ambiguity (CX4) commit 8e3d66d; BM money terms alignment (CX10) commit b68ac79.

### TC-BILL-131: Billing table: # column, all-column search, count, CSV export, no dead checkboxes
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Before you start**: Operator; a month with 26+ invoices (seed or generate; otherwise verify with what exists and note the count).
| Step | Action |
|------|--------|
| 1 | Open Billing and look at the first column and the footer |
| 2 | Type a payer name in the search box; then clear and type an invoice number |
| 3 | Use the Status filter chips/facet; click "Export CSV" |
**What you should see**: A positional "#" column renumbers with the current sort/filter/page; the footer shows "1-25 of N" (25 rows per page by default). Search matches across columns (payer AND invoice number). The status facet filters (Draft/Issued/Partially paid/Paid/Voided). "Export CSV" downloads the visible dataset. There are NO row-selection checkboxes (removed as dead UI).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Table usability pass commit 746df0b; dead selection checkboxes removed commit df2e3f1.

## Coverage note

61 cases (was 39 in the 2026-06-30 catalog). Updated 2026-07-04 against branch `feat/finish-mvp-polish`.

Techniques walked: happy (A,B,C,H), boundary (009/022/024/078/120), negative/validation (024/041/072/091/120),
state-transition (003/023/030/031/050-055/075), idempotency/concurrency (003/007/079), permissions (100/103),
cross-tenant/IDOR (076/101/102), i18n (082/130), data integrity (003/008/021/027/040/052-055/078/110),
security/XSS (042), file-type (025/026/091/092/120), empty/loading state (006/111/121/122).
Non-functional (perf/N+1 on Run billing at 200 guardians) remains tracked separately for the load pass.

Changes in this revision:
- Rewritten in place (catalog never executed, so bodies were updated under their original IDs):
  001, 003, 006 (exact run-result strings), 010, 011 (issue-all + send hint), 020 (operator payments are
  auto-verified), 022, 023, 024, 025 (content-sniffed types, WebP conversion), 030, 031 (refund now under
  More; exact checkbox strings), 032 (refund now visible-but-disabled, c1ee98d), 040 (negative-amount
  contract + suspected client-validation defect flagged), 041 (exact bilingual messages), 050 (void guard
  context), 051 (reason optional in UI, required at API: the old "blocked until reason" assertion was wrong),
  060, 070 (current public page composition), 071 (404, token via API), 072 (receipt now REQUIRED; pending
  chip on the list), 073 (queue page naming + verified status), 074 (rejected rows kept + dimmed), 075
  (exact cancelled message + 422), 080 (exact reminder message), 081 (disabled + tooltip, list row too),
  082 (BM PDF labels, e86b941), 090/091/092 (rebuilt settings forms ebb792c: digit stripping, pairing rule,
  QR confirm flow), 100 (Better Auth teacher login + redirect target), 102 (org-scoped queue note).
- Added: 007, 008 (run-billing atomicity + unique numbers, @regression 6ddce23), 009 (start-date boundary),
  026 (receipt fix, 261e141), 027 (remove payment, a39c059), 052-055 (void lifecycle guards + recoverable
  void, @regression c1ee98d/6ddce23), 077 (returning-parent pending state, 917c612), 078 (public claim cap,
  a39c059), 079 (idempotent double-tap + Enter submit, 6e2b993), 083 (row share, 998a2b5), 103 (owner-only
  settings), 110 (verify balance guard, a39c059), 111 (dashboard card + badge, de4be04), 112 (payment status
  badges + inline decisions, a39c059), 120 (public submit hardening, 3cddbee), 121 (no-payment-method
  guidance, 390b663), 122 (public loading skeleton, 31777bd), 130 (BM void/cancel + money terms, 8e3d66d/
  b68ac79), 131 (table usability, 746df0b/df2e3f1).
- Deleted: none (no billing feature was removed).
- Auth: no case referenced Clerk-specific behaviour; the catalog now names the Better Auth dev logins and
  the teacher redirect target verified in `src/libs/Access.ts`.
- Suspected defect logged while grounding TC-BILL-040: the client zod schema in `InvoiceActions.tsx`
  requires a positive adjustment amount while the field label instructs "use a negative number to reduce
  the total" and the API/service accept negatives. The case is written to surface this on first run.
