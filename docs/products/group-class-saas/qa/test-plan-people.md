# Test plan: People (Students, Guardians, Enrolments) (M2)

> Exhaustive manual catalog for the People module. Format + method: [QA-METHODOLOGY.md](QA-METHODOLOGY.md).
> Grounded in `src/features/students/{schema,service,service.test}.ts`, `src/features/guardians/{schema,service,service.test}.ts`,
> `src/features/enrollments/{schema,service,service.test}.ts`, `src/utils/validators.ts`, `SensitiveValue.tsx`,
> `IdNumberField.tsx`, the shared DataTable suite (`src/features/ui/DataTable.tsx`, `data-table/toolbar.tsx`, `data-table/pagination.tsx`),
> the student/guardian detail pages, and [FLOWS.md](../FLOWS.md) §2.
> Default tier T2 (PII + family links). T1 where flagged: IC validation, cross-tenant guardian link, fee override.
> Roles: operator (full), staff (admin subset, same People access), teacher (no access). Sign-in is Better Auth
> email + password (Clerk removed 2026-07-02); the teacher role is assigned on the org membership, not inferred from an email match.
> Dev logins: operator `operator@kelastest.local` / `newpassword6789`; teacher `teacher@kelastest.local` / `password12345`.
> Money RM, dates DD/MM/YYYY, EN/BM messages.
>
> Updated 2026-07-04 for the post-catalog commits: linked-children count (b98afe1), enrolled-classes column (b4faa68),
> table usability pass (746df0b, df2e3f1), success toasts (6e45620), surfaced action failures (31777bd),
> enrol entry-point changes (fee1221, 63c3365, 135ff13), shared status tones (a9737aa).
> CSV import cases live in `test-plan-import.md`, not here. 74 cases.
>
> Smoke subset (@smoke): TC-STU-001, TC-STU-010, TC-STU-040, TC-GRD-001, TC-ENR-001, TC-ENR-020, TC-ENR-040, TC-STU-090.

---

## A. Students: create (happy + identity)

### TC-STU-001: Create a student with the minimum (name only) lands them in the list
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Linked**: US-stu-create **Risk**: R-stu-create **Type**: Feature
**Before you start**: Log in as operator. Go to Students.
**Test Data**: name = `Nur Aisyah binti Ahmad`. Leave every other field empty.
| Step | Action |
|------|--------|
| 1 | Click Add student |
| 2 | Type the name into Full name; leave all other fields blank |
| 3 | Click Add student to save |
**What you should see**: A success toast "Student saved" (BM: "Pelajar disimpan") appears and you return to the Students list; `Nur Aisyah binti Ahmad` appears as a row with status Active (green badge), Level `-`, Classes `-` (muted), Guardian `-`.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-STU-002: Create a student with the full profile persists every field
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator; one guardian already exists (Guardians has at least one active row; note its name).
**Test Data**: name `Adam bin Razali`; IC `120304-14-5566`; DOB `04/03/2012` (enter 2012-03-04 in the picker); gender Male; phone `012-345 6789`; email `adam@example.com`; existing guardian; level `Iqra 3`; address `12 Jalan Mawar, Shah Alam`; notes `Allergic to peanuts`.
| Step | Action |
|------|--------|
| 1 | Add student, fill every field with the test data, pick the existing guardian |
| 2 | Save, then open the new student from the list |
**What you should see**: Detail page shows the name, masked IC ending `5566`, DOB `04/03/2012`, gender Male, level `Iqra 3`, phone, email, the guardian name as a clickable link, the address, and the notes block. Status badge Active.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-003: Name is required and blank/whitespace is rejected
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on Add student.
**Test Data**: Full name = empty, then a single space.
| Step | Action |
|------|--------|
| 1 | Leave Full name empty and click Add student |
| 2 | Type one space into Full name and click Add student |
**What you should see**: Both blocked under the Full name field with the message "This field is required." (BM: "Medan ini wajib diisi."). No student is created; you stay on the form.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## B. Students: IC vs passport toggle

### TC-STU-010: Valid 12-digit IC is accepted and auto-dashed
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T1 | **Linked**: US-stu-ic **Risk**: R-ic-validation **Type**: Feature
**Before you start**: Operator on Add student. The IC / passport toggle is set to IC (default).
**Test Data**: name `Hafiz IC Test`; IC keystrokes `120304145566`.
| Step | Action |
|------|--------|
| 1 | Confirm the type toggle shows IC selected |
| 2 | Type `120304145566` into the IC field |
| 3 | Fill Full name and save |
**What you should see**: As you type, the field auto-formats to `120304-14-5566`. Save succeeds; the detail page shows the IC masked as dots ending `5566`.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-011: IC must be 12 digits with a valid birth month, day and state code
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T1 | **Risk**: R-ic-validation **Type**: Feature
**Before you start**: Operator on Add student with the IC toggle on IC; Full name filled.
**Test Data**: try in order: `12030414556` (11 digits); `121304145566` (month 13); `120300145566` (day 00); `120304175566` (state code 17, unassigned); `120304005566` (state code 00).
| Step | Action |
|------|--------|
| 1 | Enter `12030414556` and try to save |
| 2 | Enter `121304145566` (month 13) and try to save |
| 3 | Enter `120300145566` (day 00) and try to save |
| 4 | Enter `120304175566` (state code 17) and try to save |
| 5 | Enter `120304005566` (state code 00) and try to save |
**What you should see**: Each one is blocked under the IC field with "Enter a valid IC, e.g. 920101-14-5567." (BM: "Masukkan IC yang sah, cth. 920101-14-5567."). No student is saved for any of them.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-012: Boundary state codes are accepted (01, 16, 21, 85, 98, 99)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Risk**: R-ic-validation **Type**: Feature
**Before you start**: Operator on Add student, IC toggle on IC, Full name filled.
**Test Data**: ICs differing only in the state-code pair: `120304015566`, `120304165566`, `120304215566`, `120304855566`, `120304985566`, `120304995566`.
| Step | Action |
|------|--------|
| 1 | Enter each IC in turn and confirm the field shows no validation error |
| 2 | Save one of them (e.g. `120304-98-5566`) |
**What you should see**: None of these six raise an IC error (codes 01-16, 21-85, 98, 99 are all valid); the saved one persists.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-013: Switching to Passport accepts a loose alphanumeric and uppercases it
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on Add student; Full name filled.
**Test Data**: passport `a1234567` typed in lower case.
| Step | Action |
|------|--------|
| 1 | Click the Passport segment of the IC / passport toggle |
| 2 | Type `a1234567` |
| 3 | Save and open the detail page |
**What you should see**: Input shows `A1234567` (uppercased, alphanumeric only). Save succeeds; detail shows it masked ending `4567`.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-014: Passport length boundaries (6-12) enforced
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on Add student, Passport toggle selected, Full name filled.
**Test Data**: `AB123` (5 chars, too short); `ABCDEF123456` (12, valid); attempt to type `ABCDEF1234567` (13).
| Step | Action |
|------|--------|
| 1 | Enter `AB123` and try to save |
| 2 | Enter `ABCDEF123456` and confirm no error |
| 3 | Try to type a 13th character onto a 12-char value |
**What you should see**: `AB123` blocked with "Enter a valid passport number, e.g. A12345678." (BM: "Masukkan nombor pasport yang sah, cth. A12345678."); `ABCDEF123456` accepted; the field refuses the 13th character (capped at 12).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-015: A value valid as a passport but switched to IC is rejected per the chosen type
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on Add student, Full name filled.
**Test Data**: enter passport `A1234567` with the toggle on Passport, then switch the toggle to IC.
| Step | Action |
|------|--------|
| 1 | With Passport selected, enter `A1234567` |
| 2 | Click the IC segment of the toggle |
| 3 | Try to save |
**What you should see**: On switching to IC, the value is re-normalised to digits only (letters stripped). If the remaining digits are not a valid 12-digit IC, saving is blocked with the IC error. The chosen type governs validation.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-016: API backstop accepts either an IC or a passport in the same field
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: API
**Before you start**: Operator session; POST directly to `/api/students` (the API uses `studentInputSchema`, which accepts either type).
**Test Data**: body `{ "name": "API Id", "icNumber": "A1234567" }`, then `{ "name": "API Id2", "icNumber": "120304-14-5566" }`, then `{ "name": "API Bad", "icNumber": "12" }`.
| Step | Action |
|------|--------|
| 1 | POST the passport body |
| 2 | POST the IC body |
| 3 | POST the `12` body |
**What you should see**: The first two return 201 created (either form passes the `icOrPassportField` backstop). The `12` body returns 422 with an "Invalid input" issue on `icNumber` ("Enter a valid IC or passport number.").
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## C. Students: phone / email / DOB validation

### TC-STU-020: Valid Malaysian phone formats are accepted
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on Add student, Full name filled.
**Test Data**: `012-345 6789` (mobile), `+60 12-345 6789` (international), `03-7788 9900` (landline).
| Step | Action |
|------|--------|
| 1 | Enter each phone in turn into Student phone and confirm no error, then save one |
**What you should see**: All three pass (01X mobile, +60/60 normalised, 0[3-9] landline). No phone validation error appears.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-021: Invalid phone is hard-blocked
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on Add student, Full name filled.
**Test Data**: `12345` (too short, no 0), `0212345678` (area 02, invalid), `abcdef`.
| Step | Action |
|------|--------|
| 1 | Enter each value into Student phone and try to save |
**What you should see**: Each is blocked under the phone field with "Enter a valid Malaysian phone number, e.g. 012-345 6789." (BM: "Masukkan nombor telefon Malaysia yang sah, cth. 012-345 6789."). No student saved.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-022: Malformed email is rejected
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on Add student, Full name filled.
**Test Data**: `adam@`, then `adam example.com`, then a valid `adam@example.com`.
| Step | Action |
|------|--------|
| 1 | Enter `adam@` and try to save |
| 2 | Enter `adam example.com` and try to save |
| 3 | Enter `adam@example.com` and save |
**What you should see**: The first two are blocked under email with "Enter a valid email address." (BM: "Masukkan alamat e-mel yang sah."). The valid one saves. An empty email is also allowed (optional field).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-023: DOB in the future is rejected
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on Add student, Full name filled.
**Test Data**: a DOB one year from today.
| Step | Action |
|------|--------|
| 1 | Pick a date of birth in the future and try to save |
**What you should see**: Blocked under DOB with "Enter a valid date of birth (not in the future)." (BM: "Masukkan tarikh lahir yang sah (bukan masa hadapan)."). No student saved.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-024: DOB before 1900 and impossible calendar dates are rejected
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on Add student, Full name filled. (If the picker prevents typing, send the value via `/api/students` to confirm server enforcement.)
**Test Data**: `1899-12-31` (pre-1900); `2011-02-31` (31 Feb, impossible).
| Step | Action |
|------|--------|
| 1 | Enter/submit `1899-12-31` |
| 2 | Enter/submit `2011-02-31` |
**What you should see**: Both rejected with the DOB invalid message; the impossible 31 Feb is caught (the date rolls over and fails the calendar check). No student saved.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## D. Students: list, search, status filter, empty states

### TC-STU-030: Search box filters the list (case-insensitive, matches any column)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator; at least two students with distinct names (e.g. `Zarina Ahmad` and `Faris Iqbal`).
**Test Data**: search term `zarina`.
| Step | Action |
|------|--------|
| 1 | Go to Students |
| 2 | Type `zarina` into the search box (placeholder "Search name, guardian, phone..."; BM: "Cari nama, penjaga, telefon...") |
**What you should see**: Only `Zarina Ahmad` remains in the table; `Faris Iqbal` is filtered out. The single box matches against every visible column (name, level, classes, guardian, phone, status), not name only (see TC-STU-104 for the null-column regression). Clearing the box restores all rows.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Search widened from name-only to all columns in 746df0b.

### TC-STU-031: Status facet filter narrows by status
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator; one Active and one Paused student exist.
| Step | Action |
|------|--------|
| 1 | Go to Students, open the Status filter |
| 2 | Tick only Paused |
**What you should see**: Only Paused students show. The status options are exactly Active, Paused, Dropped, Graduated.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-032: Empty students list shows the explicit empty message
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator in an org with no students.
| Step | Action |
|------|--------|
| 1 | Go to Students |
**What you should see**: A rich empty state, never a blank table: heading "No students yet" (BM: "Tiada pelajar lagi"), text "Add your first student to start enrolling and billing." (BM: "Tambah pelajar pertama anda untuk mula mendaftar dan mengebil."), with an "Add student" button and an import button beside it.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-033: Search/filter with no match shows the filtered empty message
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator; at least one student exists.
**Test Data**: search term `zzzzznomatch`.
| Step | Action |
|------|--------|
| 1 | Search for `zzzzznomatch` |
| 2 | Click the Reset button under the message |
**What you should see**: "No matches for your search or filters." (BM: "Tiada padanan untuk carian atau tapisan anda.") with a "Reset" (BM: "Set semula") button beneath it, distinct from the no-students-yet empty state. Clicking Reset clears the search box and any status filter and restores all rows.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Filter-miss message + reset button standardised in 746df0b.

## E. Students: status lifecycle

### TC-STU-040: Dropped status removes a student from the default service list
**Tags**: @smoke @regression @data-integrity **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Linked**: US-stu-status **Risk**: R-stu-list **Type**: Feature
**Before you start**: Operator; a student currently Active (note their name). The default list (e.g. the enrollment student picker, billing scope) uses active-only.
| Step | Action |
|------|--------|
| 1 | Open the student detail, click Edit |
| 2 | Set Status to Dropped, Save changes |
| 3 | On the Students list, open the Status filter and tick only Active |
**What you should see**: The student no longer appears under the Active filter; the badge reads Dropped (red) when All statuses is shown. They remain reachable via the Dropped filter (default list = active only; dropped is still searchable).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-041: Each status renders the correct badge tone
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator; students in each of Active, Paused, Dropped, Graduated.
| Step | Action |
|------|--------|
| 1 | View the Students list with All statuses |
**What you should see**: Active = positive (green), Paused = warning (amber), Dropped = negative (red), Graduated = neutral (grey). Labels are the localised status names.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-042: Status field appears only when editing, not on create
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator.
| Step | Action |
|------|--------|
| 1 | Open Add student and look for a Status control |
| 2 | Open an existing student's Edit form and look for Status |
**What you should see**: Add student has no Status control (new students are created Active). Edit shows a Status dropdown with the four statuses.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## F. Students: level history

### TC-STU-050: Creating with an initial level records the first history row
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-stu-level **Risk**: R-level-history **Type**: Feature
**Before you start**: Operator on Add student.
**Test Data**: name `Hadi Level`; current level `Iqra 2`.
| Step | Action |
|------|--------|
| 1 | Create the student with level `Iqra 2` |
| 2 | Open the detail page, read the Level history card |
**What you should see**: Level history shows exactly one row: `Iqra 2` with today's date. Creating with no level shows "No level recorded yet."
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-051: Changing the level adds a new history row, newest first
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Risk**: R-level-history **Type**: Feature
**Before you start**: Operator; the student from TC-STU-050 (current level `Iqra 2`).
**Test Data**: new level `Iqra 3`.
| Step | Action |
|------|--------|
| 1 | Edit the student, change Current level to `Iqra 3`, save |
| 2 | Open the detail page |
**What you should see**: Level history now lists `Iqra 3` (today) at the top and `Iqra 2` below; profile Current level reads `Iqra 3`.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-052: Saving the same level (or other-field edits) does not add a history row
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Risk**: R-level-history **Type**: Feature
**Before you start**: Operator; the student from TC-STU-051 (current level `Iqra 3`, 2 history rows).
| Step | Action |
|------|--------|
| 1 | Edit the student, leave Current level as `Iqra 3`, change the phone, save |
| 2 | Open the detail page and count the history rows |
**What you should see**: Still exactly 2 history rows (no new row when the level is unchanged). A row is only written when the level changes to a new non-empty value.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## G. Students: inline add-new-guardian + guardian linking

### TC-STU-060: Add a new guardian inline while creating a student
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-stu-guardian **Type**: Feature
**Before you start**: Operator on Add student.
**Test Data**: student name `Linked Child`; guardian selection = "+ Add new guardian"; new guardian name `Encik Ahmad`; new guardian phone `012-345 6789`.
| Step | Action |
|------|--------|
| 1 | In the Guardian dropdown choose "+ Add new guardian" |
| 2 | Enter the new guardian name and phone in the panel that appears |
| 3 | Fill the student name and save |
**What you should see**: One flow creates `Encik Ahmad` as a guardian and `Linked Child` linked to him. The student detail shows `Encik Ahmad` as a clickable guardian link; Guardians list now includes `Encik Ahmad`.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-061: Inline new-guardian requires a name
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on Add student.
| Step | Action |
|------|--------|
| 1 | Choose "+ Add new guardian", leave the new guardian name blank |
| 2 | Fill the student name and try to save |
**What you should see**: Blocked with "Enter the new guardian name, or choose None." No guardian and no student are created.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-062: Linking an existing same-org guardian populates the link
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator; one active guardian exists (note its name).
| Step | Action |
|------|--------|
| 1 | Add student, pick the existing guardian from the dropdown, save |
| 2 | Open the student detail |
**What you should see**: Guardian field shows the picked guardian as a clickable link to that guardian's detail page.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-063: Linking a guardian from another org is silently ignored (link stored null)
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-stu-tenant **Risk**: R-cross-tenant-guardian **Type**: API
**Before you start**: Two orgs A and B. As operator of org B, obtain a guardian id that belongs to org A (from a known fixture or another session). POST directly to `/api/students` while authed as org B.
**Test Data**: body `{ "name": "Cross Org Child", "guardianId": "<org-A-guardian-id>" }`.
| Step | Action |
|------|--------|
| 1 | POST the body with org A's guardianId while signed in as org B |
| 2 | Open the created student in org B and read the Guardian field |
**What you should see**: The student is created (201) but with NO guardian: the cross-org id is validated against org B and dropped to null (not an error). Guardian shows `-`. Org A's guardian is never linked or leaked.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## H. Students: sensitive data masking + detail

### TC-STU-070: IC is masked by default on the detail page with a reveal toggle
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-stu-pii **Risk**: R-pii-masking **Type**: Feature
**Before you start**: Operator; a student whose IC is `120304-14-5566`. Open their detail page.
| Step | Action |
|------|--------|
| 1 | Look at the IC field |
| 2 | Click the eye icon next to it |
| 3 | Click the eye icon again |
**What you should see**: By default the IC shows dots with only the last 4 visible (e.g. `••••••••••5566`). The eye reveals the full `120304-14-5566`; clicking again re-masks it. The aria-label toggles Show/Hide.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-071: A student with no IC shows a dash, no toggle
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator; a student created without an IC/passport.
| Step | Action |
|------|--------|
| 1 | Open the detail page and look at the IC field |
**What you should see**: The IC shows `-` with no eye/reveal control (nothing sensitive to mask).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-072: Phone and email are shown in full (never masked)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator; a student with phone and email set.
| Step | Action |
|------|--------|
| 1 | Open the detail page, read phone and email |
**What you should see**: Both are shown in full, no masking (operators need them to contact families). Only IC is masked.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-073: Notes with a script payload render escaped, no execution
**Tags**: @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on Add/Edit student.
**Test Data**: notes = `<script>alert('xss')</script>`.
| Step | Action |
|------|--------|
| 1 | Save a student with that notes value |
| 2 | Open the detail page |
**What you should see**: The notes block shows the literal text escaped; no alert pops. (Repeat for the address field.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## I. Guardians: CRUD, archive, cleanup, detail

### TC-GRD-001: Create a guardian with name only
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Linked**: US-grd-create **Type**: Feature
**Before you start**: Operator. Go to Guardians.
**Test Data**: name `Encik Ali`.
| Step | Action |
|------|--------|
| 1 | Click Add (guardian) |
| 2 | Type the name, leave phone/email/notes blank, save |
**What you should see**: A success toast "Guardian saved" (BM: "Penjaga disimpan") appears and you return to Guardians; `Encik Ali` appears with phone/email `-` and Children `0` (rendered muted). Detail page shows phone/email as `-` and an Active badge.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-GRD-002: Guardian name is required
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on Add guardian.
| Step | Action |
|------|--------|
| 1 | Leave Full name blank and try to save |
**What you should see**: Blocked with "This field is required." (BM equivalent). No guardian created.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-GRD-003: Guardian phone/email validation matches the shared rules
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on Add guardian; Full name filled.
**Test Data**: phone `0212345678` (invalid); email `puan@` (invalid).
| Step | Action |
|------|--------|
| 1 | Enter the invalid phone and try to save |
| 2 | Enter the invalid email and try to save |
**What you should see**: Phone blocked with the MY phone message; email blocked with the email message (same shared validators as Students).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-GRD-004: Empty optional fields are cleaned to null on create
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-grd-cleanup **Type**: Feature
**Before you start**: Operator on Add guardian.
**Test Data**: name `Puan Aminah`; phone `012-3456789`; email left empty; notes left empty.
| Step | Action |
|------|--------|
| 1 | Create the guardian with email and notes blank |
| 2 | Open the detail page |
**What you should see**: Phone stored and shown; email and notes show `-` (empty strings are stored as null, never blank strings). Status Active.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-GRD-005: Edit a guardian updates the saved fields
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator; a guardian with a phone set (note it).
**Test Data**: change phone to `019-876 5432`, add email `aminah@example.com`.
| Step | Action |
|------|--------|
| 1 | Open the guardian, click Edit, change phone and email, save |
| 2 | Reopen the detail page |
**What you should see**: Detail shows the new phone and email. Clearing a field on edit stores null (shows `-`).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-GRD-006: Archive removes a guardian from the active list (kept for history)
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-grd-archive **Type**: Feature
**Before you start**: Operator; two active guardians (note their names).
| Step | Action |
|------|--------|
| 1 | On Guardians, open the row kebab for one guardian and choose Archive |
| 2 | Read the confirm dialog, then confirm with the Archive button |
| 3 | Scan the Guardians list |
**What you should see**: The dialog is titled "Archive <name>?" and explains the record is kept. On confirming, a success toast "Guardian archived" (BM: "Penjaga diarkibkan") appears and the archived guardian leaves the active list; the other remains. (Archive is a status change, not a hard delete: the record persists for invoice history.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-GRD-007: Guardian detail shows linked students and their invoices
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-grd-detail **Type**: Feature
**Before you start**: Operator; a guardian linked to at least one student, and that family has at least one invoice (run billing first if needed).
| Step | Action |
|------|--------|
| 1 | Open the guardian detail page |
**What you should see**: Profile (phone/email, status badge), a "Linked students" (BM: "Pelajar berkait") card listing each linked student as a clickable link with their level and status badge, and an "Invoices" card listing month, invoice number, status badge, total (RM) and paid (RM). Empty states read "No students linked to this guardian." / "No invoices for this guardian yet." when nothing exists.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-GRD-008: Empty Guardians list shows the explicit empty message
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator in an org with no guardians.
| Step | Action |
|------|--------|
| 1 | Go to Guardians |
**What you should see**: A rich empty state, never a blank table: heading "No guardians yet" (BM: "Tiada penjaga lagi"), text "Add a parent or wali, then link their children." (BM: "Tambah ibu bapa atau wali, kemudian pautkan anak mereka."), with an "Add guardian" button and an import button beside it.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-GRD-009: Notes with a script payload render escaped
**Tags**: @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on Add/Edit guardian.
**Test Data**: notes = `<script>alert('xss')</script>`.
| Step | Action |
|------|--------|
| 1 | Save a guardian with that notes value |
| 2 | Open the detail page |
**What you should see**: Notes shown as literal escaped text; no alert pops.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## J. Enrolments: create from both sides

### TC-ENR-001: Enrol a student from the class side appears on both roster and student
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Linked**: US-enr-create **Risk**: R-enroll **Type**: Feature
**Before you start**: Operator; one class and one active student (both same org). Open the class detail page.
**Test Data**: start date = today; no fee override.
| Step | Action |
|------|--------|
| 1 | On the class roster, click Enroll student |
| 2 | Pick the student, keep today as the start date, click Enroll |
| 3 | Open the student detail and read Enrolled classes |
**What you should see**: The student appears on the class roster (Active badge) and on the student's Enrolled classes table (the class as a clickable link, today's start date, Active). Fee shown = the class monthly fee.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ENR-002: Enrol into a class from the student side
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator; a student not yet enrolled in some class. Open the student detail page.
| Step | Action |
|------|--------|
| 1 | In Enrolled classes, click Enroll in a class |
| 2 | Pick a class, set the start date, optionally a mid-join note, click Enroll |
**What you should see**: The class appears in the student's Enrolled classes; the student shows on that class's roster. The class picker only lists classes the student is not already actively enrolled in.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ENR-003: Nothing to pick: the enroll control becomes a guidance link, not a dead button
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator; a student already actively enrolled in every existing class (so no class remains to pick). Open that student's detail page.
| Step | Action |
|------|--------|
| 1 | Look at the Enrolled classes card header where the Enroll button normally sits |
| 2 | Hover the link inside the guidance text |
| 3 | On a class detail page whose roster already holds every student, look at the same spot |
**What you should see**: Instead of a disabled button, the student side shows "You need a class first." with a "Create a class" link (BM: "Anda perlu kelas dahulu." / "Cipta kelas") that goes to the new-class form; the link is plain at rest and underlines only on hover. The class side shows "You need a student first." with an "Add a student" link (BM: "Anda perlu pelajar dahulu." / "Tambah pelajar").
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Disabled dead button replaced with a guidance link in fee1221; hover-only underline in 135ff13.

### TC-ENR-004: Enrolling with no target selected shows a choose error
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator; the Enroll panel open with no class/student picked.
| Step | Action |
|------|--------|
| 1 | Click Enroll without choosing a class (or student) |
**What you should see**: An inline error "Choose a class." (BM: "Pilih kelas.") on the student side, or "Choose a student." (BM: "Pilih pelajar.") on the class side; no request is sent.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## K. Enrolments: duplicate + cross-org guards

### TC-ENR-010: Duplicate enrolment (same student + class + start date) is rejected as 409
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-enr-dup **Risk**: R-enroll-dup **Type**: Feature
**Before you start**: Operator; a student already enrolled in a class with a known start date (note both). Open that student or class to re-enroll.
**Test Data**: same student, same class, same start date as the existing enrolment.
| Step | Action |
|------|--------|
| 1 | Enroll the same student into the same class with the same start date |
**What you should see**: Rejected with the message "This student is already enrolled in this class with that start date." (the API returns 409). No second enrolment row is created. A different start date for the same student+class is allowed.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ENR-011: Cross-org student or class is rejected as invalid refs (422)
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-enr-tenant **Risk**: R-cross-tenant-enroll **Type**: API
**Before you start**: Two orgs A and B. As operator of org B, obtain a student id from org A (and separately a class id from org A). POST to `/api/enrollments` while authed as org B.
**Test Data**: body `{ "studentId": "<org-A-student-id>", "classId": "<org-B-class-id>", "startedAt": "2026-06-01" }`; then a body with org B's student and org A's class.
| Step | Action |
|------|--------|
| 1 | POST with org A's studentId + org B's classId |
| 2 | POST with org B's studentId + org A's classId |
**What you should see**: Both return 422 with "Student or class not found." No enrolment is created; org A's records are never linked into org B.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ENR-012: Malformed enrolment payload is rejected (422)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: API
**Before you start**: Operator session; POST to `/api/enrollments`.
**Test Data**: `{ "studentId": "not-a-uuid", "classId": "<valid>", "startedAt": "01/06/2026" }` (bad uuid + wrong date format).
| Step | Action |
|------|--------|
| 1 | POST the malformed body |
**What you should see**: 422 "Invalid input" with an issues object flagging `studentId` (not a valid uuid) and `startedAt` (message key `date_ymd`; the raw API returns the key, and the matching form message is "Use the date format YYYY-MM-DD (example: 2026-07-03)."). No enrolment created.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## L. Enrolments: fee override

### TC-ENR-020: Fee override drives the effective fee (override else class fee)
**Tags**: @smoke @regression @data-integrity **Severity**: S2 High | **Priority**: P1 | **Tier**: T1 | **Linked**: US-enr-fee **Risk**: R-fee-override **Type**: Feature
**Before you start**: Operator; a class with a known monthly fee (e.g. RM 100.00) and an active student. Note the class fee.
**Test Data**: enroll with fee override = `60.00`.
| Step | Action |
|------|--------|
| 1 | Enroll the student into the class, set Fee override to 60.00, Enroll |
| 2 | Open the student detail, read the Fee column for that enrolment |
**What you should see**: The Fee column shows RM 60.00 (the override), not RM 100.00. A second enrolment with no override would show RM 100.00 (the class monthly fee). Effective fee = override else class fee.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ENR-021: Fee override with more than 2 decimals is rejected
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator; the Enroll panel open with a class/student picked.
**Test Data**: fee override `60.999`.
| Step | Action |
|------|--------|
| 1 | Enter `60.999` as the fee override and click Enroll |
**What you should see**: Rejected (the API 422s on `feeOverride`) with the at-most-2-decimal-places rule; no enrolment created. An empty override is allowed (means "use the class fee").
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ENR-022: Negative fee override is rejected
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: API
**Before you start**: Operator; POST to `/api/enrollments` with a valid student+class.
**Test Data**: `feeOverride: -10`.
| Step | Action |
|------|--------|
| 1 | POST the body with feeOverride -10 |
**What you should see**: 422 (money must be non-negative); no enrolment created.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## M. Enrolments: pause / resume / end lifecycle

### TC-ENR-030: Pause an enrolment then resume it
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-enr-pause **Type**: Feature
**Before you start**: Operator; a student with an Active enrolment. Open the student (or class) detail.
| Step | Action |
|------|--------|
| 1 | Open the enrolment row kebab, click Pause |
| 2 | Open the kebab again, click Resume |
**What you should see**: After Pause the status badge reads Paused (amber) and the row stays on the roster; the kebab now offers Resume. After Resume it returns to Active. (Paused enrolments are skipped by billing - cross-ref billing TC-BILL-004.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ENR-040: Ending an enrolment stamps an end date, keeps the row off the active roster
**Tags**: @smoke @regression @data-integrity **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Linked**: US-enr-end **Risk**: R-enroll-end **Type**: Feature
**Before you start**: Operator; an Active enrolment on a known class. Note the class roster.
| Step | Action |
|------|--------|
| 1 | On the enrolment row, open the kebab, click End, confirm in the dialog |
| 2 | Open the class roster |
| 3 | Open the student detail, read Enrolled classes |
**What you should see**: The enrolment is removed from the class roster (roster excludes ended). On the student detail it still shows in the history with status Ended (neutral) and an end date = today. The row kebab now shows just "Ended" (no further actions).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ENR-041: Re-activating an ended enrolment clears the end date
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: API
**Before you start**: Operator; an Ended enrolment (note its id from the student detail / API). PATCH `/api/enrollments/<id>`.
**Test Data**: `{ "status": "active" }`.
| Step | Action |
|------|--------|
| 1 | PATCH the enrolment to status active |
| 2 | Re-read the enrolment |
**What you should see**: Status active and endedAt cleared to null (reactivating clears the end date); it reappears on the roster.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ENR-042: Ended enrolment row offers no Pause/Resume/End actions
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator; an Ended enrolment visible on a student detail.
| Step | Action |
|------|--------|
| 1 | Look at the Actions cell of the ended enrolment row |
**What you should see**: It shows the static label "Ended", no kebab menu (ended is terminal in the UI).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## N. Permissions + tenant isolation (People)

### TC-STU-090: Teacher cannot reach People pages or APIs
**Tags**: @smoke @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-people-roles **Risk**: R-people-rbac **Type**: Feature
**Before you start**: Log in as a teacher: `teacher@kelastest.local` / `password12345` (an org member whose Better Auth membership role is teacher; the role is assigned on the membership, and the account is linked to its teachers row on first login).
| Step | Action |
|------|--------|
| 1 | Navigate directly to /dashboard/students |
| 2 | Navigate directly to /dashboard/guardians |
| 3 | Call `/api/students` (GET) directly while authed as the teacher |
| 4 | Call `/api/enrollments?studentId=<any>` directly |
**What you should see**: Both pages redirect to /dashboard/attendance (operator route guard). Both API calls return 401 with "Forbidden: operators only" (requireOperatorContext rejects teachers). No student, guardian, or enrolment data is shown.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-091: Cross-tenant: one org cannot open another org's student/guardian
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-people-tenant **Risk**: R-cross-tenant-read **Type**: Feature
**Before you start**: Two orgs A and B. As operator of org B, obtain org A's student id and guardian id (from a fixture or another session).
| Step | Action |
|------|--------|
| 1 | As org B, open /dashboard/students/<org-A-student-id> |
| 2 | As org B, open /dashboard/guardians/<org-A-guardian-id> |
| 3 | As org B, GET `/api/students/<org-A-student-id>` and `/api/guardians/<org-A-guardian-id>` |
**What you should see**: Both pages render the not-found page; both API calls return 404 "Not found". Org A's records never render or return for org B.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-092: Cross-tenant write: org B cannot edit or archive org A's records
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Risk**: R-cross-tenant-write **Type**: API
**Before you start**: As org B operator, with org A's student id, guardian id, and enrolment id.
| Step | Action |
|------|--------|
| 1 | PATCH `/api/students/<org-A-student-id>` with `{ "name": "Hacked" }` |
| 2 | DELETE `/api/guardians/<org-A-guardian-id>` (archive) |
| 3 | PATCH `/api/enrollments/<org-A-enrollment-id>` with `{ "status": "ended" }` |
**What you should see**: All three return 404 "Not found"; org A's student name is unchanged, its guardian stays active, and its enrolment is untouched. No cross-org mutation occurs.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-093: Lists show only the current org's people
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Org B operator; org A also has students and guardians.
| Step | Action |
|------|--------|
| 1 | Open Students as org B and scan the list |
| 2 | Open Guardians as org B and scan the list |
**What you should see**: Only org B's students and guardians; none from org A.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-094: No active org context: People pages redirect, APIs 401
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: A signed-in user with no organisation selected.
| Step | Action |
|------|--------|
| 1 | Navigate to /dashboard/students |
| 2 | Call `/api/guardians` (GET) directly |
**What you should see**: The page redirects to /onboarding/organization-selection; the API returns 401 "No active organisation selected". No data is shown.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## O. Internationalisation

### TC-STU-100: People forms and lists render in BM with no missing keys
**Tags**: @regression @i18n **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Linked**: US-i18n **Type**: Feature
**Before you start**: Operator; switch the app language to BM (Bahasa Melayu).
| Step | Action |
|------|--------|
| 1 | Visit Students list, Add student, the student detail, Guardians list, Add guardian, and the Enroll panel |
| 2 | Trigger one validation error on each form (e.g. blank name) |
**What you should see**: All labels, buttons, placeholders, empty states, status badges, and validation messages are Malay (e.g. name required = "Medan ini wajib diisi.", IC = "Masukkan IC yang sah, cth. 920101-14-5567."). No raw key strings (like `Students.add`) and no English leakage. Switching back to EN restores English.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-STU-101: Dates and money use Malaysian locale across People
**Tags**: @regression @i18n @data-integrity **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator; a student with a DOB and an enrolment with a fee.
| Step | Action |
|------|--------|
| 1 | Read the DOB and level-history dates on the student detail |
| 2 | Read the enrolment Fee and the guardian Invoices totals |
**What you should see**: Dates are DD/MM/YYYY; money is shown as RM (never MYR/$); times, where present, are Asia/Kuala_Lumpur. Consistent in both EN and BM.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## P. Students list: classes column, search, numbering, export (added 2026-07-04)

### TC-STU-102: Classes column shows the student's current classes (none / one / many)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2 | **Linked**: US-stu-list **Type**: Feature
**Before you start**: Operator; three students: one with no enrolment, one actively enrolled in exactly one class (e.g. `Iqra 1`), one enrolled in two classes (e.g. `Iqra 1` and `Hafazan`).
| Step | Action |
|------|--------|
| 1 | Go to Students and read the Classes column (BM header: "Kelas") for each of the three rows |
| 2 | Hover the cell of the student with two classes |
**What you should see**: No enrolment shows a muted `-`. One class shows the class name. Two classes collapse to the first name plus a small muted `+1`; hovering the cell reveals the full comma-separated list as a tooltip.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Column added in b4faa68.

### TC-STU-103: Classes column reflects enrolment status only (ended hidden, paused shown) and stays tenant-scoped
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Risk**: R-stu-list **Type**: Feature
**Before you start**: Operator; one student enrolled in three different classes: one enrolment Active, one Paused, one Ended (pause/end via the enrolment row kebab on the student detail).
| Step | Action |
|------|--------|
| 1 | Go to Students and read that student's Classes cell (hover for the full list) |
| 2 | Try to archive one of the classes still listed (Classes list, row kebab, Archive) while its enrolment stays active or paused |
| 3 | End that enrolment and re-check the cell |
**What you should see**: Step 1: only the Active and Paused classes are listed; the Ended class never appears (paused still counts as current). Step 2: the archive is REFUSED with "Cannot archive yet: N student(s) are still enrolled in this class..." (the 667eecb guard, see TC-CLS-151), so a class name in this column can never belong to a freshly archived class; legacy data archived before the guard may still show, which is truthful (its enrolment is still current and still billing). Step 3: after ending the enrolment the name disappears. Another org's enrolments never leak into the list (the aggregation joins on this org's id; service-tested).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Grounded in `listStudents` (b4faa68) and its service test "lists each student's enrolled class names (active and paused enrolments)". Finding re-triage 2026-07-04: the remedy chosen was the archive guard (667eecb), not hiding archived names; the column stays enrolment-driven by design.

### TC-STU-104: Search matches a column even when the first row's value is empty
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on Students. Arrange that the alphabetically FIRST student has no phone: create `Aisyah Tanpa Telefon` with no phone if needed. Also create `Zarina Bertelefon` with phone `019-876 5432`, linked to guardian `Encik Ahmad bin Ismail`.
**Test Data**: search terms `019-876`, then `Ismail`.
| Step | Action |
|------|--------|
| 1 | Confirm `Aisyah Tanpa Telefon` is the first row and its Phone cell shows `-` |
| 2 | Type `019-876` into the search box |
| 3 | Clear it and type `Ismail` |
**What you should see**: `019-876` leaves only `Zarina Bertelefon` (the phone column matched even though the first row's phone is empty). `Ismail` also leaves only `Zarina Bertelefon` (the guardian column is searched too). A blank value in the first row never knocks a column out of the search.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: TanStack's default column probing skipped any column whose first-row value was null, silently excluding it from global search (phone/guardian searches matched nothing); fixed in 746df0b with a null-safe `includesString` and `getColumnCanGlobalFilter: () => true`.

### TC-STU-105: Positional # column, range-of-total count, and remembered rows-per-page
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator; at least three students exist.
| Step | Action |
|------|--------|
| 1 | Go to Students; read the first (#) column and the count text under the table |
| 2 | Open the Name column header menu and pick Desc |
| 3 | Search until one row remains |
| 4 | Under the table set rows per page to 10, reload the page, then open Guardians |
**What you should see**: The # column runs 1, 2, 3... top to bottom and renumbers with the current view (after the sort flip it still reads 1..N while the names reorder; the single filtered row shows #1). The count reads like "1-3 of 3" (BM: "1-3 daripada 3"). Rows-per-page defaults to 25; after picking 10 it survives the reload AND applies on Guardians too (one remembered preference across tables and visits).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Table usability pass 746df0b.

### TC-STU-106: CSV export downloads the current view with on-screen labels
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on Students in a desktop-width window (the export button is hidden on narrow screens). Students exist with mixed statuses; at least one is enrolled in two classes. English UI.
| Step | Action |
|------|--------|
| 1 | Filter Status to Active only |
| 2 | Click "Export CSV" (BM: "Eksport CSV") and open the downloaded file in Excel |
| 3 | Repeat once on Guardians |
**What you should see**: The file is named `students-<today as YYYY-MM-DD>.csv`. The header row uses the on-screen labels (Name, Level, Classes, Guardian, Phone, Status); the # and Actions columns are not exported. Only the filtered (Active) rows are in the file. Status exports the label shown on screen (`Active`, not `active`). A student with two classes exports the FULL comma-separated list, never the collapsed `+1` form. Malay characters display correctly in Excel. The Guardians export is `guardians-<date>.csv` with Name, Phone, Email, Children.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Export added in 746df0b; the Classes export value joins the full list (b4faa68).

### TC-STU-107: No selection checkboxes on the people lists
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator.
| Step | Action |
|------|--------|
| 1 | Open Students and inspect the header row and any data row |
| 2 | Open Guardians and do the same |
**What you should see**: No select-all checkbox in the header and no per-row checkboxes; the leftmost column is the positional #. (Checkboxes only return together with a real bulk action.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: six list tables rendered dead selection checkboxes with no bulk action behind them, promising functionality that did not exist; removed in df2e3f1.

### TC-STU-108: Saving a student shows a success toast (create and edit)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator.
**Test Data**: name `Toast Test`; on edit, change the phone to `012-345 6789`.
| Step | Action |
|------|--------|
| 1 | Add a student named `Toast Test` and save |
| 2 | Open the student, click Edit, change the phone, save |
**What you should see**: Both saves show a success toast "Student saved" (BM: "Pelajar disimpan") and then return you to the Students list. The same pattern on the guardian form shows "Guardian saved" (BM: "Penjaga disimpan").
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: create/edit forms redirected silently, so operators could not tell whether a save worked and keyed records twice; toasts added in 6e45620.

## Q. Guardians: children count + detail badge tones (added 2026-07-04)

### TC-GRD-010: Guardian detail status badge uses the shared tones (Active green, Archived grey)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator; one active guardian. Open their detail page and copy the URL.
| Step | Action |
|------|--------|
| 1 | Read the badge next to the Profile card title |
| 2 | Go back to Guardians and archive that guardian from the row kebab (confirm) |
| 3 | Paste the copied URL to reopen the detail page |
**What you should see**: Step 1: badge "Active" (BM: "Aktif") in the positive (green) tone, the same tone the lists use. Step 3: the page still opens (archived records stay readable by URL) and the badge reads "Archived" (BM: "Diarkibkan") in the neutral (grey) tone. The student detail badge likewise matches the list tone for the same status.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Status-to-tone maps centralised in a9737aa so one status can never render two colours on two screens.

### TC-GRD-011: Children column counts linked students; 0 renders muted; tenant-scoped
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-grd-list **Type**: Feature
**Before you start**: Operator; guardian `Puan Dua Anak` linked (via each student's Guardian field) to two students; guardian `Encik Tiada Anak` linked to none.
| Step | Action |
|------|--------|
| 1 | Go to Guardians and read the Children column (BM header: "Anak") for both rows |
| 2 | Edit one of the two linked students, set their Status to Dropped, save, and re-check the count |
**What you should see**: `Puan Dua Anak` shows 2; `Encik Tiada Anak` shows 0 rendered in muted grey (a 0 flags a likely duplicate or data-entry leftover). After dropping one child the count is STILL 2: the column counts linked students of any status, not active only. Students in another org pointing at the same guardian id never inflate the count (service-tested; the join is scoped to this org).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Column + tenant-scoped count added in b98afe1 (service test "counts each guardian's linked children, scoped to the org").

## R. Enrolment entry points + failure surfacing (added 2026-07-04)

### TC-ENR-043: Onboarding checklist enrol step deep-links to the first class page
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator in an org that has at least one class but no enrolment yet, with the dashboard Getting-started checklist visible (not dismissed).
| Step | Action |
|------|--------|
| 1 | On the dashboard checklist, click the step "Enrol a student" (BM: "Daftar pelajar") |
| 2 | Enrol any student from the page you land on, then return to the dashboard |
| 3 | In an org with no class at all, click the same step |
**What you should see**: Step 1 lands on the FIRST class's detail page (URL `/dashboard/classes/<id>`), where the "Enroll a student" button lives, not on the students list. Step 2: back on the dashboard the enrol step is ticked and struck through. Step 3: with no class yet, the step falls back to the classes list (`/dashboard/classes`). The first-class shortcut only ever picks a class from your own org (service-tested).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Deep-link added in 63c3365 (`firstClassId`, tenant-scoped, onboarding service test).

### TC-ENR-044: A failed End/Archive action shows an error instead of closing as if it worked
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator with two browser tabs on the same login: tab 1 on a student detail with an Active enrolment, tab 2 anywhere in the dashboard.
| Step | Action |
|------|--------|
| 1 | In tab 2, sign out (this invalidates the session for both tabs) |
| 2 | In tab 1 (do not reload), open the enrolment row kebab, click End, and click "End enrollment" in the confirm dialog |
| 3 | Sign back in and reopen the student detail |
**What you should see**: Step 2: the dialog STAYS OPEN and shows "That did not work. Please try again." (BM: "Itu tidak berjaya. Sila cuba lagi."); it never closes pretending success. Step 3: the enrolment is still Active with no end date. A guardian Archive that fails surfaces the same message in its own dialog.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: destructive row actions (archive class/teacher/guardian, end enrolment) failed silently and closed as if they had worked; surfaced in 31777bd. Since c679357 (2026-07-04) a TRUE network drop (DevTools offline) is also caught and shows the same message, so offline mode is a valid alternative trigger for step 2.

## Coverage note
Techniques walked across Students / Guardians / Enrolments:
- **Happy path:** STU-001/002, GRD-001, ENR-001/002.
- **Equivalence + boundary:** IC state-code boundaries (STU-012), passport length 6-12 (STU-014), DOB pre-1900 / impossible date (STU-024), fee-override decimals/negative (ENR-021/022).
- **Negative / validation + server bypass:** name required (STU-003, GRD-002), phone/email (STU-021/022, GRD-003), IC structure (STU-011), API backstop (STU-016), malformed enrolment (ENR-012).
- **Format / locale:** IC auto-dash + passport uppercase (STU-010/013), MY phone forms (STU-020), i18n + RM/dates (STU-100/101).
- **Permissions / role:** teacher denied pages + APIs (STU-090); no-org redirect/401 (STU-094).
- **Cross-tenant / IDOR:** guardian link dropped (STU-063), enrolment refs (ENR-011), reads (STU-091), writes (STU-092), list scoping (STU-093).
- **State transition:** student status incl. dropped-leaves-list (STU-040/041/042), enrolment pause/resume/end + reactivate (ENR-030/040/041/042).
- **Empty / loading states:** student/guardian empty + filtered-empty (STU-032/033, GRD-008), disabled enroll (ENR-003).
- **Data integrity:** level history on create + change + no-op (STU-050/051/052), effective fee (ENR-020), end-date stamping (ENR-040), empty-field cleanup (GRD-004).
- **Security (XSS):** notes/address payloads (STU-073, GRD-009).
- **PII masking:** IC masked + reveal (STU-070/071), phone/email never masked (STU-072).
- **Detail composition:** student detail link history + enrolled classes (STU-002, ENR-001), guardian detail linked students + invoices (GRD-007), shared badge tones on detail pages (GRD-010).
- **List columns (2026-07-04):** enrolled-classes column none/one/many + status/tenant integrity (STU-102/103), children count incl. 0-muted, any-status counting, and tenant scope (GRD-011).
- **Table usability + export (2026-07-04):** search across all columns incl. the null-first-row regression (STU-030/104), # column + range-of-total + remembered rows-per-page (STU-105), CSV export contents (STU-106), dead selection checkboxes removed (STU-107), filter-miss message + Reset (STU-033).
- **Feedback + failure surfacing (2026-07-04):** save/archive success toasts (STU-001/108, GRD-001/006), failed destructive action surfaced in the dialog (ENR-044).
- **Enrolment entry points (2026-07-04):** onboarding checklist deep-link to the first class page (ENR-043), nothing-to-pick guidance link replacing the disabled button (ENR-003 rewritten).

Not separately cased here: concurrency/double-submit on enroll (relies on the duplicate guard, see ENR-010; load-tested separately) and accessibility spot checks (covered in `test-plan-crosscutting.md`). Billing interactions of paused enrolments are cross-referenced to `test-plan-billing.md` (TC-BILL-004/005). CSV import of students/guardians is covered in `test-plan-import.md`, not here.

2026-07-04 update: the catalog was never executed, so stale cases were rewritten in place keeping their IDs: TC-STU-001, TC-STU-030, TC-STU-032, TC-STU-033, TC-STU-090 (Better Auth login note), TC-GRD-001, TC-GRD-006, TC-GRD-007, TC-GRD-008, TC-ENR-003, TC-ENR-004, TC-ENR-012. New cases appended with the next free numbers: TC-STU-102..108, TC-GRD-010/011, TC-ENR-043/044. Deletions: none (no covered feature was removed; TC-ENR-003's disabled-button behaviour was replaced by the guidance link and the case now tests the replacement). Regression provenance carried in Notes lines citing commits b98afe1, b4faa68, 746df0b, df2e3f1, 6e45620, 31777bd, 63c3365, a9737aa, fee1221, 135ff13.

Total cases: 74 (Students 47 incl. permissions + i18n under the TC-STU- prefix, Guardians 11, Enrolments 16).
Smoke subset (8, unchanged): TC-STU-001, TC-STU-010, TC-STU-040, TC-GRD-001, TC-ENR-001, TC-ENR-020, TC-ENR-040, TC-STU-090.
