# Test plan: Teachers (M5)

> Exhaustive manual catalog for the Teachers module (profiles + detail + grade history + teacher accounts). Format + method: [QA-METHODOLOGY.md](QA-METHODOLOGY.md).
> Grounded in `src/features/teachers/{schema,service,service.test}.ts`, `TeacherForm.tsx`, `TeachersTable.tsx`,
> `TeacherActions.tsx`, `teachers/[id]/page.tsx`, `src/features/ui/{SensitiveValue,IdNumberField,RowActions,DataTable}.tsx`,
> `src/features/ui/data-table/{toolbar,pagination}.tsx`, `src/utils/validators.ts`, `src/libs/{Access,access-role}.ts`,
> the 8 teachers service tests (5 CRUD/tenancy + 3 grade history) + the access-role and validator tests, and [FLOWS.md](../FLOWS.md) §5.
> Updated 2026-07-04 against branch `feat/finish-mvp-polish` (post Better Auth migration; Clerk is gone).
> Default tier T2 (PII: IC + bank account).
>
> Roles (Better Auth, assigned on the organisation MEMBERSHIP, not inferred from email; `src/libs/access-role.ts`):
> operator = org owner/admin (full access); staff = member without the teacher role (operational access, no payment
> settings / member management); teacher = member with the teacher role, linked to a `teachers` record (attendance +
> own classes/pay only). Teachers now have real logins (self-service `/dashboard/my-classes`, `/dashboard/my-pay`).
> Dev logins: operator `operator@kelastest.local` / `newpassword6789`; teacher `teacher@kelastest.local` / `password12345`
> (linked to teacher `Ustazah Fatimah`).
>
> Smoke subset (@smoke): TC-TCH-001, TC-TCH-040, TC-TCH-050, TC-TCH-060, TC-TCH-080, TC-TCH-090.

## A. Create teacher

### TC-TCH-001: Create a teacher with the full happy path
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Linked**: M5-US1 **Type**: Feature
**Before you start**: Log in as operator. Go to Teachers (left nav). Click Add teacher (top-right button).
**Test Data**: name `Ustaz Ahmad bin Ali`; IC type IC, IC `920101-14-5567`; phone `012-345 6789`; email `ustaz@example.com`; bank `Maybank`; account `1234567890`; grade `A`.
| Step | Action |
|------|--------|
| 1 | Type the name in Full name |
| 2 | Leave the ID toggle on IC, type the IC number (it auto-dashes to 920101-14-5567) |
| 3 | Pick grade A from the Grade dropdown |
| 4 | Type the phone and email |
| 5 | Pick Maybank from the Bank name dropdown |
| 6 | Type the account number |
| 7 | Click Add teacher |
**What you should see**: A success toast "Teacher saved" / BM "Guru disimpan" appears, then you are returned to the Teachers list; `Ustaz Ahmad bin Ali` appears as a row, name linked (teal), grade A shown as a green badge, phone and email shown in their columns, and the Classes column shows `0` (greyed, no classes assigned yet).
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: saves used to redirect silently and operators keyed records in twice; toast added in commit 6e45620.

### TC-TCH-002: Create a teacher with only the required name
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US1 **Type**: Feature
**Before you start**: Operator on Teachers > Add teacher. All optional fields left blank.
**Test Data**: name `Cikgu Siti`.
| Step | Action |
|------|--------|
| 1 | Type only the name |
| 2 | Click Add teacher |
**What you should see**: Saved with the "Teacher saved" toast; `Cikgu Siti` appears in the list with `-` for phone and email, "Not graded" in the Grade column, and `0` in the Classes column. (Service test: "defaults grade to null (ungraded) and cleans empty optional fields".)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-003: Name is required
**Tags**: @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Linked**: M5-US1 **Type**: Feature
**Before you start**: Operator on Teachers > Add teacher.
| Step | Action |
|------|--------|
| 1 | Leave Full name blank, fill nothing else |
| 2 | Click Add teacher |
**What you should see**: Hard-blocked, no navigation; a bilingual message under Full name: EN "This field is required." / BM "Medan ini wajib diisi." (schema `name.min(1, 'required')`).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-004: Name of only whitespace is rejected
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US1 **Type**: Feature
**Before you start**: Operator on Teachers > Add teacher.
**Test Data**: name = three spaces `   `.
| Step | Action |
|------|--------|
| 1 | Type three spaces in Full name |
| 2 | Click Add teacher |
**What you should see**: Blocked with "required" (schema trims then enforces min 1). No teacher created.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-005: Name over 120 characters is rejected
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US1 **Type**: Feature
**Before you start**: Operator on Teachers > Add teacher.
**Test Data**: name = 121 letters (e.g. paste `A` x 121).
| Step | Action |
|------|--------|
| 1 | Paste 121 characters into Full name |
| 2 | Click Add teacher |
**What you should see**: Blocked (schema `name.max(120)`); no teacher created. A 120-character name is accepted (boundary).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-006: Empty optional fields are stored as null, not empty strings
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US1 **Risk**: R-TCH-clean **Type**: Feature
**Before you start**: Operator. Create a teacher with name only (e.g. `Cikgu Kosong`), email field left blank, phone `012-3456789`.
| Step | Action |
|------|--------|
| 1 | Create the teacher with email blank |
| 2 | Open the teacher detail page |
**What you should see**: Email shows `-` (stored as null, not ""), phone shows `012-3456789`, grade shows "Not graded". (Service test asserts `email` is `null`, `phone` kept, `grade` null, `status` `active` after this exact input.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## B. IC vs passport toggle

### TC-TCH-010: Valid IC is accepted and auto-formatted
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US2 **Type**: Feature
**Before you start**: Operator on Teachers > Add teacher. ID toggle is on IC by default.
**Test Data**: type `9201011455 67` then continue to `920101145567`.
| Step | Action |
|------|--------|
| 1 | With the toggle on IC, type the 12 IC digits without dashes |
| 2 | Click Add teacher (give a name first) |
**What you should see**: The field auto-dashes to `920101-14-5567` as you type; saves without an IC error. (validators `formatIc` + `isValidMyIc`.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-011: Invalid IC is hard-blocked
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US2 **Type**: Feature
**Before you start**: Operator on Teachers > Add teacher, ID toggle on IC, name filled.
**Test Data**: IC `999999-99-9999` (month 99, invalid state code).
| Step | Action |
|------|--------|
| 1 | Type the invalid IC |
| 2 | Click Add teacher |
**What you should see**: Blocked with EN "Enter a valid IC, e.g. 920101-14-5567." / BM "Masukkan IC yang sah, cth. 920101-14-5567." (form `superRefine` -> `ic_invalid`). No teacher created.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-012: IC with the wrong digit count is blocked (boundary)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US2 **Type**: Feature
**Before you start**: Operator, IC mode, name filled.
**Test Data**: try `92010114556` (11 digits), then `920101145567` (12, valid).
| Step | Action |
|------|--------|
| 1 | Type the 11-digit value and submit |
| 2 | Add the 12th digit and submit |
**What you should see**: 11 digits blocked ("Enter a valid IC..."); the input never accepts a 13th digit (`formatIc` caps at 12); 12 valid digits save.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-013: Switch the toggle to Passport and accept a valid passport
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US2 **Type**: Feature
**Before you start**: Operator on Teachers > Add teacher, name filled.
**Test Data**: passport `A1234567`.
| Step | Action |
|------|--------|
| 1 | Click the Passport segment of the ID toggle |
| 2 | Type `a1234567` |
| 3 | Click Add teacher |
**What you should see**: The toggle highlights Passport (teal); input uppercases to `A1234567` (`formatPassport`); saves without error (`isValidPassport`, 6-12 alphanumeric).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-014: Invalid passport (too short / symbols) is blocked
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US2 **Type**: Feature
**Before you start**: Operator, Passport mode, name filled.
**Test Data**: `A12` (3 chars after format -> below the 6-char minimum).
| Step | Action |
|------|--------|
| 1 | Type `A12` and submit |
| 2 | Type `A12345!!` (symbols are stripped, leaving `A12345`) and submit |
**What you should see**: `A12` blocked with EN "Enter a valid passport number, e.g. A12345678." / BM "Masukkan nombor pasport yang sah, cth. A12345678." (superRefine -> `passport_invalid`); the input never shows the `!` symbols (`formatPassport` strips non-alphanumeric).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-015: Switching IC -> Passport re-normalises the typed value
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US2 **Type**: Feature
**Before you start**: Operator, IC mode, name filled.
**Test Data**: IC `920101-14-5567`.
| Step | Action |
|------|--------|
| 1 | Type the dashed IC in IC mode |
| 2 | Click the Passport segment |
**What you should see**: The value re-formats to `920101145567` (dashes stripped; exactly 12 alphanumeric remain, within `formatPassport`'s 12-char cap); the field no longer shows dashes. (IdNumberField `setType` re-normalises.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-016: API accepts either IC or passport as a backstop
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US2 **Type**: API
**Before you start**: Operator session. Send POST `/api/teachers` directly (browser console fetch or curl with the session cookie).
**Test Data**: body `{ "name": "API Teacher", "icNumber": "A1234567" }`, then a second with `{ "name": "API Teacher 2", "icNumber": "bad!" }`.
| Step | Action |
|------|--------|
| 1 | POST the valid-passport body |
| 2 | POST the malformed body |
**What you should see**: Valid passport returns 201 (`icOrPassportField` accepts IC OR passport); `bad!` returns 422 with `error: "Invalid input"` and an `issues` payload (`ic_or_passport`). The UI's per-type strictness is enforced only in the form, not the API.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## C. Phone & email validation

### TC-TCH-020: Valid Malaysian phone is accepted
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US3 **Type**: Feature
**Before you start**: Operator on Teachers > Add teacher, name filled.
**Test Data**: phone `012-345 6789`.
| Step | Action |
|------|--------|
| 1 | Type the phone with the dash and space |
| 2 | Click Add teacher |
**What you should see**: Saved; the teacher row shows the phone (`normalizeMyPhone` accepts `01X` mobile). +60 / 60 prefixed forms are also accepted.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-021: Invalid phone is hard-blocked
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US3 **Type**: Feature
**Before you start**: Operator on Teachers > Add teacher, name filled.
**Test Data**: phone `123` (no leading 0, too short).
| Step | Action |
|------|--------|
| 1 | Type `123` in Phone |
| 2 | Click Add teacher |
**What you should see**: Blocked with EN "Enter a valid Malaysian phone number, e.g. 012-345 6789." / BM "Masukkan nombor telefon Malaysia yang sah, cth. 012-345 6789." (`phoneField` -> `phone_my`). No teacher created.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-022: Invalid email is hard-blocked
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US3 **Type**: Feature
**Before you start**: Operator on Teachers > Add teacher, name filled.
**Test Data**: email `not-an-email`.
| Step | Action |
|------|--------|
| 1 | Type `not-an-email` in Email |
| 2 | Click Add teacher |
**What you should see**: Blocked with EN "Enter a valid email address." / BM "Masukkan alamat e-mel yang sah." (schema `.email('email')`). No teacher created.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-023: Empty email is allowed (optional)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US3 **Type**: Feature
**Before you start**: Operator on Teachers > Add teacher, name filled, email blank.
| Step | Action |
|------|--------|
| 1 | Leave Email blank and submit |
**What you should see**: Saved (schema allows `""` / null); detail shows email `-`. (No "required" error: email is optional.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## D. Bank name dropdown & account number

### TC-TCH-030: Pick a bank from the dropdown
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US4 **Type**: Feature
**Before you start**: Operator on Teachers > Add teacher, name filled.
**Test Data**: bank `CIMB Bank`.
| Step | Action |
|------|--------|
| 1 | Open the Bank name dropdown |
| 2 | Pick `CIMB Bank` |
| 3 | Submit |
**What you should see**: The dropdown lists the Malaysian banks (Maybank, CIMB Bank, Public Bank ... 22 entries) plus an "Other bank" option at the bottom; `CIMB Bank` is stored and shown on the detail Payout details card.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-031: "Other bank" reveals a free-text field
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US4 **Type**: Feature
**Before you start**: Operator on Teachers > Add teacher, name filled.
**Test Data**: bank name typed `Koperasi Guru Berhad`.
| Step | Action |
|------|--------|
| 1 | Open the Bank name dropdown, pick "Other bank" (EN) / "Bank lain" (BM) |
| 2 | A text input appears below the dropdown; type `Koperasi Guru Berhad` |
| 3 | Submit |
**What you should see**: A free-text input with placeholder "Type the bank name" / "Taip nama bank" appears; `Koperasi Guru Berhad` is saved and shown on the detail page.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-032: Editing a teacher whose bank is a custom name reopens in "Other" mode
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US4 **Type**: Feature
**Before you start**: Operator. Have a teacher saved with a custom bank (from TC-TCH-031, `Koperasi Guru Berhad`). Open that teacher, click Edit.
| Step | Action |
|------|--------|
| 1 | Open the edit form for that teacher |
**What you should see**: The Bank name dropdown shows "Other bank" selected and the free-text input is pre-filled with `Koperasi Guru Berhad` (TeacherForm `bankOther` initial = stored name not in the bank list).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-033: Bank account strips non-digits in the UI
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US4 **Risk**: R-TCH-bank **Type**: Feature
**Before you start**: Operator on Teachers > Add teacher, name filled.
**Test Data**: type `1234 5678 90` (with spaces), then try typing letters `abc`.
| Step | Action |
|------|--------|
| 1 | Type `1234 5678 90` in Bank account number |
| 2 | Try to type letters into the field |
**What you should see**: The field shows `1234567890` (spaces removed by `formatAccountNumber`); letters never appear; the field accepts at most 20 digits.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-034: Server rejects a non-digit bank account (API bypass)
**Tags**: @regression @security @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US4 **Risk**: R-TCH-bank **Type**: API
**Before you start**: Operator session. Send the request directly to bypass the UI strip.
**Test Data**: POST `/api/teachers` body `{ "name": "Bank Bypass", "bankAccount": "abc123" }`.
| Step | Action |
|------|--------|
| 1 | POST the body with letters in the account |
**What you should see**: 422 `error: "Invalid input"` with a `bankAccount` issue (`bankAccountField` requires 5-20 digits after stripping; `abc123` -> `123` is < 5 digits and also fails the digit rule). No alphabetic account stored.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-035: Bank account below the 5-digit minimum is rejected (boundary)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US4 **Type**: API
**Before you start**: Operator session.
**Test Data**: POST `/api/teachers` with `bankAccount` `1234` (4 digits), then `12345` (5 digits).
| Step | Action |
|------|--------|
| 1 | POST with `1234` |
| 2 | POST with `12345` |
**What you should see**: 4 digits -> 422 with EN "Account number must be 5 to 20 digits." / BM "Nombor akaun mesti 5 hingga 20 digit." (`bank_account`); 5 digits -> 201 created.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## E. Grade

### TC-TCH-040: Grade defaults to ungraded (null)
**Tags**: @smoke @regression @data-integrity **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Linked**: M5-US7 **Type**: Feature
**Before you start**: Operator on Teachers > Add teacher. Do not touch the Grade dropdown.
**Test Data**: name `Cikgu Ungraded`.
| Step | Action |
|------|--------|
| 1 | Create with name only |
| 2 | Look at the new row's Grade column and the detail page |
**What you should see**: Grade column shows "Not graded" / "Belum dinilai" (grey text, not a badge); detail Grade field shows the same. (Service test asserts `grade` is `null`; form default `grade: null`.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-041: Set grade A / B / C and see the coloured badge
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US7 **Type**: Feature
**Before you start**: Operator on Teachers > Add teacher, name filled.
| Step | Action |
|------|--------|
| 1 | Pick grade A, save; note the row badge colour |
| 2 | Edit, change to B, save |
| 3 | Edit, change to C, save |
**What you should see**: A renders as a green (positive) badge, B as a blue (info) badge, C as an amber (warning) badge, in both the list and the detail header (GRADE_TONE map A=positive, B=info, C=warning). Only A/B/C are selectable (`TEACHER_GRADES`).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-042: Clear a grade back to ungraded
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US7 **Type**: Feature
**Before you start**: Operator. Have a teacher graded A. Open Edit.
| Step | Action |
|------|--------|
| 1 | Open the Grade dropdown |
| 2 | Pick "Not graded" |
| 3 | Save changes |
**What you should see**: Grade reverts to "Not graded" everywhere (form maps the "__ungraded__" option to `null`; service `set.grade = null`).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-043: API rejects an invalid grade value
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US7 **Type**: API
**Before you start**: Operator session.
**Test Data**: POST `/api/teachers` body `{ "name": "Grade Bypass", "grade": "D" }`.
| Step | Action |
|------|--------|
| 1 | POST with grade `D` |
**What you should see**: 422 `error: "Invalid input"` (`z.enum(['A','B','C'])`); no teacher created with an out-of-range grade.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-044: Filter the list by grade
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US7 **Type**: Feature
**Before you start**: Operator on Teachers with at least one A, one B, one C, and one ungraded teacher.
| Step | Action |
|------|--------|
| 1 | Open the Grade filter on the table toolbar |
| 2 | Tick A |
**What you should see**: The list shows only grade-A teachers; clearing the filter restores all. (TeachersTable `filters` config + `filterFn`.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## F. Edit teacher

### TC-TCH-050: Edit a teacher's contact details
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Linked**: M5-US5 **Type**: Feature
**Before you start**: Operator. Open any teacher, click Edit (top-right) or use the row kebab > Edit.
**Test Data**: new phone `019-876 5432`, new email `updated@example.com`.
| Step | Action |
|------|--------|
| 1 | Change the phone and email |
| 2 | Click Save changes |
**What you should see**: A success toast "Teacher saved" / BM "Guru disimpan" fires, then you are returned to the Teachers list; opening the teacher shows the new phone and email. The button reads "Save changes" / "Simpan perubahan" (not "Add teacher") in edit mode, with busy text "Saving..." / "Menyimpan..." while submitting.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-051: Editing a passport-holder reopens in Passport mode
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US5 **Type**: Feature
**Before you start**: Operator. Have a teacher saved with a passport (e.g. `A1234567`). Open Edit.
| Step | Action |
|------|--------|
| 1 | Open the edit form |
**What you should see**: The ID toggle opens on Passport (TeacherForm `initialIdType`: a stored value containing a letter -> passport); the value shows `A1234567`.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-052: Clearing an optional field on edit stores null
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US5 **Risk**: R-TCH-clean **Type**: Feature
**Before you start**: Operator. Have a teacher with a phone set. Open Edit.
| Step | Action |
|------|--------|
| 1 | Delete the phone value, leave it blank |
| 2 | Save changes |
| 3 | Open the teacher detail |
**What you should see**: Phone shows `-` (service `clean('')` -> null on the patched field). The other fields are unchanged.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-053: Cancel discards edits
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US5 **Type**: Feature
**Before you start**: Operator editing a teacher.
| Step | Action |
|------|--------|
| 1 | Change the name in the form |
| 2 | Click Cancel |
| 3 | Reopen the teacher |
**What you should see**: Returned to the Teachers list; the name is unchanged (Cancel routes back without saving).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-054: Edit validation matches create (invalid IC blocked)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US5 **Type**: Feature
**Before you start**: Operator editing a teacher, ID toggle on IC.
**Test Data**: IC `111111-99-1111` (invalid state code 99 is valid; use `131301-00-1234` with state code 00 = unassigned -> invalid).
| Step | Action |
|------|--------|
| 1 | Replace the IC with `131301-00-1234` |
| 2 | Click Save changes |
**What you should see**: Blocked with "Enter a valid IC..." (same `superRefine` as create; state code 00 is rejected by `isValidMyIc`). No change saved.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## G. Deactivate / reactivate

### TC-TCH-060: Deactivate moves a teacher off the active list, records kept
**Tags**: @smoke @regression @data-integrity **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Linked**: M5-US6 **Risk**: R-TCH-deact **Type**: Feature
**Before you start**: Operator on Teachers. Pick a teacher (note the name).
| Step | Action |
|------|--------|
| 1 | Open the row kebab menu, click Deactivate |
| 2 | Read the confirm dialog, then confirm |
| 3 | Look at the Teachers list |
**What you should see**: Confirm dialog titled "Deactivate {name}?" / "Nyahaktifkan {name}?" with the body "...records are kept." On confirm, a success toast "Teacher deactivated" / BM "Guru dinyahaktifkan" fires and the teacher disappears from the active list (`listTeachers` filters status active). The record is not deleted: it still resolves on its detail URL with an Inactive badge. (Service test: "deactivate moves a teacher off the active list".)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-061: Deactivate requires a confirm (cancel keeps active)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US6 **Type**: Feature
**Before you start**: Operator on Teachers, row kebab open on a teacher.
| Step | Action |
|------|--------|
| 1 | Click Deactivate to open the dialog |
| 2 | Dismiss / cancel the dialog |
| 3 | Look at the list |
**What you should see**: No DELETE is sent; the teacher stays in the active list (RowActions `kind: 'confirm'` only fires `onConfirm` on confirm).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-062: Deactivated teacher detail still loads with an Inactive badge
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US6 **Type**: Feature
**Before you start**: Operator. Have a deactivated teacher; copy/keep their detail URL `/dashboard/teachers/<id>` (note the id from the URL before deactivating, or reach it via the inactive record).
| Step | Action |
|------|--------|
| 1 | Open the deactivated teacher's detail URL |
**What you should see**: The page renders (record kept); the Profile card header shows a neutral "Inactive" / "Tidak aktif" badge instead of "Active". All profile + payout fields are still present. (Detail uses `getTeacher`, which is status-agnostic.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-063: Deactivated teacher who taught is still paid (cross-link)
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US6 **Type**: Feature
**Before you start**: Operator. A teacher who has completed (attendance-marked) sessions this month, then deactivate them. Cross-references [test-plan-teacher-pay.md](test-plan-teacher-pay.md); verify the payroll outcome there.
| Step | Action |
|------|--------|
| 1 | Deactivate a teacher who taught marked sessions this month |
| 2 | Go to Teacher pay, run payroll for the month |
**What you should see**: The deactivated teacher still appears in payroll with a draft payout for the sessions they taught (payroll pays `taughtBy` from frozen sessions; FLOWS §5/§7 "a deactivated teacher who taught is still paid for those sessions"). Deactivation only hides them from the active assignment list, not from earned pay.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-064: Reactivation path (current behaviour: no UI control)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US6 **Type**: Feature
**Before you start**: Operator. Have a deactivated teacher.
| Step | Action |
|------|--------|
| 1 | Look across the Teachers list, detail page, and edit form for a "Reactivate" / inactive-list control |
| 2 | If you have operator session access, send PATCH `/api/teachers/<id>` body `{ "status": "active" }` |
**What you should see**: No reactivate button is exposed in the UI today, and no inactive-list view is surfaced (`listInactiveTeachers` exists in the service but is not rendered). The PATCH with `status: "active"` DOES succeed at the API (`teacherUpdateSchema` allows `status`), returning the teacher to the active list. NOTE: this documents a known UI gap (server supports reactivation; the UI does not). Flag if product expects a UI control.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## H. Detail page

### TC-TCH-070: Detail shows profile, payout, and assigned classes
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US8 **Type**: Feature
**Before you start**: Operator. Have a teacher assigned to at least one class (assign them as the class teacher in Classes first). Open the teacher from the list.
| Step | Action |
|------|--------|
| 1 | Open the teacher detail |
**What you should see**: Three regions: Profile card (IC, grade, phone, email + Active/Inactive badge), Payout details card (bank name + masked bank account), and an Assigned classes table listing each class with name, type, schedule, monthly fee (RM), and teacher rate (RM).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-071: Assigned-class name links to the class detail
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T3 | **Linked**: M5-US8 **Type**: Feature
**Before you start**: Operator on a teacher detail with assigned classes.
| Step | Action |
|------|--------|
| 1 | Click a class name in the Assigned classes table |
**What you should see**: Navigates to `/dashboard/classes/<id>` for that class (teal link, hover underline). The id matches the class clicked.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-072: Teacher with no classes shows the empty state
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US8 **Type**: Feature
**Before you start**: Operator. Have a teacher not assigned to any class. Open their detail.
| Step | Action |
|------|--------|
| 1 | Look at the Assigned classes card |
**What you should see**: An explicit message "Not assigned to any classes yet." / "Belum ditugaskan kepada mana-mana kelas.", not a blank table (`no_classes`).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-073: Money on the detail shows RM and Malaysian locale
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US8 **Type**: Feature
**Before you start**: Operator on a teacher detail with an assigned class that has a monthly fee and a teacher rate.
| Step | Action |
|------|--------|
| 1 | Read the Fee and Teacher rate columns |
**What you should see**: Amounts render as RM (e.g. RM 120.00), never `MYR`, formatted via `formatMoney`. Two decimal places.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-074: A non-existent teacher id returns not-found (404, not 500)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US8 **Type**: Feature
**Before you start**: Operator.
**Test Data**: a random UUID that is not a teacher in this org.
| Step | Action |
|------|--------|
| 1 | Open `/dashboard/teachers/<random-uuid>` |
**What you should see**: The Next.js not-found page (page calls `notFound()` when `getTeacher` returns undefined). No server error / 500.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## I. PII masking (IC + bank account)

### TC-TCH-080: IC and bank account are masked by default on the detail page
**Tags**: @smoke @regression @security @data-integrity **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Linked**: M5-US9 **Risk**: R-TCH-pii **Type**: Feature
**Before you start**: Operator. Open a teacher whose IC is `920101-14-5567` and bank account is `1234567890`.
| Step | Action |
|------|--------|
| 1 | Open the teacher detail page and look at the IC field and the Payout > Bank account field on first load |
**What you should see**: Neither the full IC nor the full account is shown on load. Both render with bullets masking all but the last 4 characters (e.g. account shows `••••••7890`; IC shows bullets then `5567`). Each has an eye icon. (SensitiveValue: masked by default, last `tail`=4 visible.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-081: Reveal toggle shows the full value, then re-masks
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US9 **Risk**: R-TCH-pii **Type**: Feature
**Before you start**: Operator on a teacher detail with a masked IC + bank account.
| Step | Action |
|------|--------|
| 1 | Click the eye icon next to the bank account |
| 2 | Click it again |
| 3 | Repeat for the IC field |
**What you should see**: First click reveals the full `1234567890`; the icon switches to eye-off; its accessible label changes from "Show" / "Tunjuk" to "Hide" / "Sembunyi" (`aria-pressed` true). Second click re-masks. Each field toggles independently.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-082: Phone and email are NOT masked (operators need them)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US9 **Type**: Feature
**Before you start**: Operator on a teacher detail with a phone + email set.
| Step | Action |
|------|--------|
| 1 | Look at the Phone and Email fields |
**What you should see**: Both are shown in full with no eye toggle (only IC + bank account use SensitiveValue; FLOWS §8 "Never masked: ... phone/email").
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-083: Teacher with no IC / no bank account shows a dash
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US9 **Type**: Feature
**Before you start**: Operator. Open a teacher with no IC and no bank account saved.
| Step | Action |
|------|--------|
| 1 | Look at the IC field and the Bank account field |
**What you should see**: Each shows `-` (SensitiveValue renders `-` for a null/empty value), no bullets, no eye icon.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-084: IC is not exposed in page source while masked
**Tags**: @security @data-integrity @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US9 **Risk**: R-TCH-pii **Type**: Feature
**Before you start**: Operator on a teacher detail with a masked IC. Masking is now server-side: the page ships ONLY the masked tail; the eye toggle fetches the full value from GET /api/teachers/[id]/sensitive?field=ic|bank (operator-gated, no-store).
| Step | Action |
|------|--------|
| 1 | View page source (Ctrl+U or DevTools) and search for the teacher's full IC without clicking reveal |
| 2 | Click the eye toggle and watch the Network tab |
**What you should see**: Step 1: the full IC is NOWHERE in the served HTML or props; only the masked form (bullets + last 4) appears. Step 2: a request to /api/teachers/<id>/sensitive?field=ic returns the full value, which then renders; toggling hides it again without refetching. The same applies to the bank account (field=bank).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Finding #3 CLOSED 2026-07-04: masking was presentation-only (full value in client props); fixed in b498d68 with server-side masking (utils/Mask.ts) + reveal endpoints, browser-verified that the full IC is absent from the served page. A full value found in page source is a regression of that fix.

## J. List / table

### TC-TCH-090: Empty teachers list shows a clear message
**Tags**: @smoke @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T3 | **Linked**: M5-US1 **Type**: Feature
**Before you start**: Operator in an org with no active teachers.
| Step | Action |
|------|--------|
| 1 | Open Teachers |
**What you should see**: A rich empty state inside the table area (graduation-cap icon), titled "No teachers yet" / BM "Tiada guru lagi" with the description "Add your teachers so you can assign them to classes." / BM "Tambah guru anda supaya boleh ditugaskan ke kelas.", plus an "Add teacher" / "Tambah guru" button and an "Import" button (links to `/dashboard/teachers/import`). Not a blank table. The page header also has its own Import and Add teacher buttons.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-091: List is sorted alphabetically by name
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US1 **Type**: Feature
**Before you start**: Operator with teachers `Zulkifli`, `Ahmad`, `Mariam` created.
| Step | Action |
|------|--------|
| 1 | Open Teachers (default order) |
**What you should see**: Rows in alphabetical name order: Ahmad, Mariam, Zulkifli (`listTeachers` `orderBy(asc(name))`). Column headers are also sortable on click.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-092: Search matches any visible column, not just the name
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US1 **Type**: Feature
**Before you start**: Operator with several teachers including `Ahmad` (phone `012-345 6789`, email `ustaz@example.com`) and at least one teacher with NO phone saved.
| Step | Action |
|------|--------|
| 1 | Type `Ahm` in the search box (placeholder "Search name, phone, email..." / BM "Cari nama, telefon, e-mel...") |
| 2 | Clear it, then search by a phone fragment, e.g. `345 6789` |
| 3 | Clear it, then search by an email fragment, e.g. `ustaz@` |
| 4 | Search gibberish, e.g. `zzzz` |
**What you should see**: Steps 1-3 each keep only the matching rows (the toolbar search is a global filter across every visible column via `includesString`; columns with null first-row values are still searchable per `getColumnCanGlobalFilter: () => true`). Step 4 shows "No matches for your search or filters." / BM "Tiada padanan untuk carian atau tapisan anda." with a "Reset" / "Set semula" button that restores all rows.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Rewritten 2026-07-04: the old per-name `searchKey` filter and "Filter by name..." placeholder were replaced by all-column search in commit 746df0b.

### TC-TCH-093: List row name links to the detail page
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US8 **Type**: Feature
**Before you start**: Operator on Teachers with at least one teacher.
| Step | Action |
|------|--------|
| 1 | Click a teacher's name |
**What you should see**: Navigates to `/dashboard/teachers/<id>` for that teacher (teal link).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## K. Security: XSS / injection

### TC-TCH-100: Script payload in the name is rendered escaped, not executed
**Tags**: @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US1 **Type**: Feature
**Before you start**: Operator on Teachers > Add teacher.
**Test Data**: name `<script>alert('xss')</script>`.
| Step | Action |
|------|--------|
| 1 | Create a teacher with that name |
| 2 | View the list, the detail page header, and the deactivate-confirm dialog title |
**What you should see**: The literal text is shown escaped everywhere it renders; no alert pops (React escapes by default). The deactivate dialog title shows the escaped name too.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-101: Mass-assignment of an unknown field is ignored
**Tags**: @security @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US1 **Type**: API
**Before you start**: Operator session.
**Test Data**: POST `/api/teachers` body `{ "name": "Mass Assign", "orgId": "org_someone_else", "status": "inactive", "id": "forced-id" }`.
| Step | Action |
|------|--------|
| 1 | POST the body with extra fields |
| 2 | Read the created teacher |
**What you should see**: 201 with `name` `Mass Assign`, status `active` (create ignores `status`; the schema does not accept it), `orgId` = the caller's org (forced server-side in `createTeacher`), and a server-generated id (not `forced-id`). No cross-org write.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## L. Permissions & roles

### TC-TCH-110: Teacher cannot open the Teachers pages (redirected)
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: M5-US10 **Risk**: R-TCH-role **Type**: Feature
**Before you start**: Log in as a teacher: `teacher@kelastest.local` / `password12345` (a Better Auth org member whose membership role is `teacher`, linked to the teacher record `Ustazah Fatimah`). Teachers land on Attendance and see only Attendance / My classes / My pay in the sidebar.
| Step | Action |
|------|--------|
| 1 | Navigate directly to `/dashboard/teachers` |
| 2 | Navigate directly to `/dashboard/teachers/new` |
| 3 | Navigate directly to `/dashboard/teachers/<any-id>` |
**What you should see**: Each redirects to `/dashboard/attendance` (the `(operator)` route-group layout calls `requireOperator`, which redirects role `teacher`). No teacher list, no form, no detail rendered.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-111: Teacher cannot call the teachers API (401)
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: M5-US10 **Risk**: R-TCH-role **Type**: API
**Before you start**: Authenticated as the teacher `teacher@kelastest.local` / `password12345`; send the request directly from that browser session's console (the UI hides it, the server must still block).
| Step | Action |
|------|--------|
| 1 | GET `/api/teachers` |
| 2 | POST `/api/teachers` with a valid body |
| 3 | DELETE `/api/teachers/<id>` for any teacher |
**What you should see**: Each returns 401 with `error: "Forbidden: operators only"` (`requireOperatorContext` throws `OrgRequiredError` for role teacher; the route maps it to 401). No data returned, no teacher created or deactivated.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-112: Unauthenticated / no-org access is blocked
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: M5-US10 **Type**: Feature
**Before you start**: A signed-in user with NO active organisation selected (or a fully signed-out session).
| Step | Action |
|------|--------|
| 1 | Open `/dashboard/teachers` |
| 2 | Call GET `/api/teachers` |
**What you should see**: The page redirects to `/onboarding/organization-selection`; the API returns 401 (`OrgRequiredError` -> 401). No teacher data.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-113: Staff can manage teachers; owner-only areas stay closed to staff
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US10 **Risk**: R-TCH-role **Type**: Feature
**Before you start**: Log in as a staff member (a Better Auth org member whose membership role maps to `staff`: role `member`/`staff`, not `teacher`, not owner/admin). If no staff login exists in the dev org, have the operator invite one first. POLICY UPDATE 2026-07-04: staff having operational access (including managing teachers) is now the DOCUMENTED intent (`src/libs/access-role.ts`: "staff: ... Operational access, no payment settings / member mgmt"), superseding the pre-migration "operator only" reading that was flagged as catalog finding #1.
| Step | Action |
|------|--------|
| 1 | Navigate to `/dashboard/teachers` |
| 2 | Create a teacher `Staff Made` via the form (or POST `/api/teachers` with `{ "name": "Staff Made" }`) |
| 3 | Navigate to `/dashboard/billing/settings` (owner-only payment settings, for contrast) |
**What you should see**: Steps 1-2 succeed: staff passes `requireOperator` / `requireOperatorContext` (those guards only block role `teacher`), the list renders, and `Staff Made` is created with the "Teacher saved" toast. Step 3 is refused for staff: the owner-only guard (`requireOwner` / `requireOwnerContext`, "Forbidden: owner only") redirects staff to `/dashboard/billing`. If staff is blocked from the Teachers pages, that is a behaviour change from the documented role model; record and flag it.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Rewritten 2026-07-04. Finding #1 re-triage: resolved by design in the Better Auth migration; roles are explicit on the membership and staff operational access is intended.

## M. Cross-tenant isolation

### TC-TCH-120: Cross-tenant: org B cannot open org A's teacher
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: M5-US11 **Risk**: R-TCH-tenant **Type**: Feature
**Before you start**: Two orgs (A and B). As operator of org A, create a teacher and note its id from the URL. Switch to org B (operator).
| Step | Action |
|------|--------|
| 1 | As org B, open `/dashboard/teachers/<org-A-teacher-id>` |
**What you should see**: Not-found page; org A's teacher never renders (`getTeacher` filters by `orgId`; page calls `notFound()`). No name, IC, or bank leaks. (Service test: "cannot read or deactivate another org's teacher".)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-121: Cross-tenant: org B cannot read org A's teacher via the API
**Tags**: @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: M5-US11 **Risk**: R-TCH-tenant **Type**: API
**Before you start**: Org A's teacher id known. Authenticated as org B operator.
| Step | Action |
|------|--------|
| 1 | GET `/api/teachers/<org-A-teacher-id>` while authed as org B |
**What you should see**: 404 `error: "Not found"` (route returns 404 when `getTeacher` is undefined for the org). No teacher payload.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-122: Cross-tenant: org B cannot deactivate or edit org A's teacher
**Tags**: @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: M5-US11 **Risk**: R-TCH-tenant **Type**: API
**Before you start**: Org A's teacher id known and still active. Authenticated as org B operator.
| Step | Action |
|------|--------|
| 1 | DELETE `/api/teachers/<org-A-teacher-id>` as org B |
| 2 | PATCH `/api/teachers/<org-A-teacher-id>` body `{ "name": "Hacked" }` as org B |
| 3 | As org A, reopen the teacher |
**What you should see**: Both return 404 `error: "Not found"` (`deactivateTeacher` / `updateTeacher` are org-scoped and return undefined -> 404). As org A, the teacher is still active and the name is unchanged. (Service test: "cannot read or deactivate another org's teacher".)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-123: Teachers list shows only the current org's teachers
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: M5-US11 **Risk**: R-TCH-tenant **Type**: Feature
**Before you start**: Org A and org B both have teachers (different names). Operator of org B.
| Step | Action |
|------|--------|
| 1 | Open Teachers as org B and scan every row |
**What you should see**: Only org B's teachers; none of org A's names appear (`listTeachers` filters by `orgId`). (Service test seeds `org_A`/`org_B` and asserts each list is its own.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## N. Internationalisation (EN + BM)

### TC-TCH-130: Teachers list + form labels switch to BM
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US12 **Type**: Feature
**Before you start**: Operator. Switch the app language to Bahasa Melayu.
| Step | Action |
|------|--------|
| 1 | Open Teachers |
| 2 | Open Add teacher |
**What you should see**: Title "Guru", description "Urus guru dan butiran mereka.", buttons "Tambah guru" and "Import"; search placeholder "Cari nama, telefon, e-mel..."; columns "Nama", "Telefon", "E-mel", "Gred", "Kelas"; form labels "Nama penuh", "Nombor IC / pasport", "Gred", "Telefon", "E-mel", "Nama bank", "Nombor akaun bank", each optional field marked "(pilihan)"; ID toggle "IC" / "Pasport". No raw key strings (e.g. no `Teachers.title`) and no English left over ("Import" is the same word in both languages).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-131: Detail page + grade labels are bilingual
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US12 **Type**: Feature
**Before you start**: Operator in BM. Open a teacher detail (one ungraded, one graded).
| Step | Action |
|------|--------|
| 1 | Read the card titles and the Grade field for an ungraded teacher |
**What you should see**: "Profil", "Butiran pembayaran", "Kelas ditugaskan"; status badge "Aktif" / "Tidak aktif"; ungraded shows "Belum dinilai". The grade letters A/B/C themselves are the same in both languages (codes, not translated).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-132: Validation messages are bilingual
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US12 **Type**: Feature
**Before you start**: Operator in BM on Teachers > Add teacher.
| Step | Action |
|------|--------|
| 1 | Submit with name blank |
| 2 | Enter an invalid IC and submit |
| 3 | Enter an invalid phone and submit |
**What you should see**: BM messages: "Medan ini wajib diisi.", "Masukkan IC yang sah, cth. 920101-14-5567.", "Masukkan nombor telefon Malaysia yang sah, cth. 012-345 6789." (Validation namespace, ms.json).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-133: Deactivate dialog + empty state are bilingual
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US12 **Type**: Feature
**Before you start**: Operator in BM. One org with teachers (for the dialog) and one mental note of the empty-state copy.
| Step | Action |
|------|--------|
| 1 | Open a teacher's kebab > Nyahaktif |
| 2 | (Separately) view an org with no teachers |
**What you should see**: Dialog title "Nyahaktifkan {name}?", body ends "...Rekod mereka disimpan.", confirm "Nyahaktif", busy "Menyahaktifkan..."; empty state "Belum ada guru. Tambah guru pertama anda untuk bermula."
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## O. Accessibility (UI)

### TC-TCH-140: Reveal toggle is keyboard reachable and labelled
**Tags**: @regression @security **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US9 **Type**: Feature
**Before you start**: Operator on a teacher detail with a masked IC + bank account.
| Step | Action |
|------|--------|
| 1 | Tab to the bank-account eye button |
| 2 | Press Enter / Space |
| 3 | Inspect its accessible name |
**What you should see**: The button receives keyboard focus, toggles reveal on Enter/Space, and exposes an accessible label "Show"/"Hide" (EN) or "Tunjuk"/"Sembunyi" (BM) with `aria-pressed` reflecting state (SensitiveValue `aria-label` + `aria-pressed`).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-141: Form fields have associated labels
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US1 **Type**: Feature
**Before you start**: Operator on Teachers > Add teacher.
| Step | Action |
|------|--------|
| 1 | Tab through the form from Full name to the Save button |
| 2 | Run an axe / Lighthouse a11y spot-check on the page |
**What you should see**: Every input is reachable in a logical order and has a programmatic label (FormLabel/FormControl wiring); no critical "form field without label" axe violations.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## P. Grade history (audit trail, added 2026-07-04)

New behaviour from commit 2d5ff12: `updateTeacher` writes a `teacher_grade_history` row inside the same
transaction whenever the grade changes to a new, non-null value. Each row stores the NEW grade,
`changed_by` (the acting user id) and `changed_at`; there is no old-grade column, so the previous value
is read from the preceding row of the same teacher's trail. There is no UI or API that displays this
table yet, so verification is on the dev database (e.g. `npm run db:studio`, or SQL against
`teacher_grade_history`). Service tests: "writes a grade-history row when the grade changes to a new
value", "does not write history when the grade is unchanged or only other fields change", "records each
distinct grade change (promotion trail)".

### TC-TCH-150: Changing the grade writes one grade-history row
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US7 **Risk**: R-TCH-audit **Type**: Feature
**Before you start**: Operator `operator@kelastest.local` / `newpassword6789` on the dev environment, with dev-database access (`npm run db:studio` or SQL). Create a fresh teacher `Ustaz Audit Trail` with NO grade, and note today's date/time.
**Test Data**: teacher name `Ustaz Audit Trail`; grade change: ungraded to `A`.
| Step | Action |
|------|--------|
| 1 | Edit `Ustaz Audit Trail`, set Grade to A, click Save changes |
| 2 | In the dev DB, find the teacher's id: `SELECT id FROM teachers WHERE name = 'Ustaz Audit Trail'` |
| 3 | Read the trail: `SELECT grade, changed_by, changed_at FROM teacher_grade_history WHERE teacher_id = '<id from step 2>'` |
**What you should see**: Exactly ONE row: `grade` = `A` (the new value), `changed_by` = the operator's user id (not empty), `changed_at` within the last few minutes. The previous value is implicit: no earlier row exists, so the trail starts at ungraded. The row's `org_id` matches the operator's org.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: New behaviour, commit 2d5ff12 (R5.13: the table existed but was never written before).

### TC-TCH-151: Non-grade edits, same-grade saves, and deactivation write NO history row
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Linked**: M5-US7 **Risk**: R-TCH-audit **Type**: Feature
**Before you start**: Continue from TC-TCH-150 (`Ustaz Audit Trail` at grade A, trail has exactly 1 row).
| Step | Action |
|------|--------|
| 1 | Edit the teacher, change ONLY the phone to `019-876 5432`, save |
| 2 | Edit again, reopen the Grade dropdown, re-pick A (unchanged), save |
| 3 | Deactivate the teacher from the list kebab, confirm |
| 4 | Re-run the trail query from TC-TCH-150 step 3 |
**What you should see**: Still exactly ONE row (the original A change). Neither the phone-only edit, nor re-saving the same grade, nor deactivation (a status-only update routed through the same `updateTeacher`) added a row. (Service test: "does not write history when the grade is unchanged or only other fields change"; `deactivateTeacher` doc: "Status-only, so it records no grade history".)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-152: Clearing the grade back to "Not graded" leaves no trace in the trail
**Tags**: @data-integrity **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US7 **Risk**: R-TCH-audit **Type**: Feature
**Before you start**: Operator with dev-database access. A teacher currently graded B.
| Step | Action |
|------|--------|
| 1 | Note the teacher's current row count in `teacher_grade_history` |
| 2 | Edit the teacher, set Grade to "Not graded", save |
| 3 | Re-run the trail query |
**What you should see**: Record the observable. CURRENT CODE: the row count is UNCHANGED. Only changes to a non-null grade are recorded (`if ('grade' in patch && newGrade && ...)`), so a downgrade to ungraded is invisible in the audit trail: the trail's last row still says B while the teacher shows "Not graded". This is a documented gap, not an assertion of correctness; flag if product wants un-grading audited.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-153: A promotion trail records each distinct change in order
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US7 **Risk**: R-TCH-audit **Type**: Feature
**Before you start**: Operator with dev-database access. A fresh ungraded teacher `Cikgu Naik Pangkat`.
| Step | Action |
|------|--------|
| 1 | Set the grade to C, save; then edit to B, save; then edit to A, save |
| 2 | Query the trail ordered by `changed_at` |
**What you should see**: Exactly THREE rows in order C, B, A, each with `changed_by` set and ascending `changed_at`. Read together, row N's grade is the "old value" of row N+1: that is how the old/new pair is reconstructed. (Service test: "records each distinct grade change (promotion trail)".)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-154: No UI displays the grade history yet (documented gap)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US7 **Type**: Feature
**Before you start**: Operator. A teacher with at least two rows in `teacher_grade_history` (from TC-TCH-153).
| Step | Action |
|------|--------|
| 1 | Open the teacher's detail page and the edit form; look for any grade-history / "changed on" display |
**What you should see**: Record the observable. CURRENT CODE: no page renders the grade history (the table is written by the service and read by nothing; the detail page shows only the current grade badge). Not a bug by itself; flag for product if operators expect to see when/who changed a grade.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## Q. Active-class count on the list (added 2026-07-04)

### TC-TCH-160: Classes column shows how many active classes the teacher teaches
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US8 **Type**: Feature
**Before you start**: Operator. One teacher assigned to exactly TWO active classes (assign via each class's teacher field / teachers list in Classes), and one teacher assigned to none.
| Step | Action |
|------|--------|
| 1 | Open Teachers and read the "Classes" / BM "Kelas" column (right-aligned, last data column) |
| 2 | Click the Classes column header to sort by it |
**What you should see**: The two-class teacher shows `2`; the unassigned teacher shows `0` rendered in grey (muted). The column sorts numerically. The count is tenant-scoped (`listTeachers` joins `class_teachers` filtered by the org). (Service test: "counts each teacher's active classes on the list".)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: New column, commit 5cc82b9.

### TC-TCH-161: Archived classes are excluded from the class count
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US8 **Type**: Feature
**Before you start**: Operator. A teacher assigned to two active classes (from TC-TCH-160).
| Step | Action |
|------|--------|
| 1 | Archive one of the two classes (Classes list kebab, archive, confirm) |
| 2 | Return to Teachers and read that teacher's Classes column |
**What you should see**: The count drops from `2` to `1`: the join counts only classes with status `active` (`eq(classes.status, 'active')`), so an archived class no longer inflates the teaching load. (Service test seeds an archived class and asserts `classCount` is 2, not 3.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## R. Table usability (toolbar, numbering, export; added 2026-07-04)

Commit 746df0b converted every list page to the shared data-table suite: a positional `#` column,
a range-of-total count, all-column search (covered in TC-TCH-092), CSV export, and 25 rows per page
default. Commit df2e3f1 removed the dead row-selection checkboxes.

### TC-TCH-170: Positional # column renumbers with sort, filter, and page
**Tags**: @regression **Severity**: S4 Low | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US1 **Type**: Feature
**Before you start**: Operator with at least 5 teachers (varied names).
| Step | Action |
|------|--------|
| 1 | Open Teachers; read the unlabeled `#` column at the far left |
| 2 | Click the Name header to reverse the sort |
| 3 | Search so only 2 rows remain |
**What you should see**: The `#` column always reads 1, 2, 3... from the top of the CURRENT view (Excel-style positional numbering, `pageIndex * pageSize + i + 1`), renumbering after the sort flip and after the filter; it is not a stored id.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-171: Pagination shows a range-of-total count and 25 rows by default
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US1 **Type**: Feature
**Before you start**: Operator in an org with more than 25 active teachers (seed via import or repeat-create; e.g. 30).
| Step | Action |
|------|--------|
| 1 | Open Teachers; read the footer under the table |
| 2 | Click the next-page chevron |
**What you should see**: Page 1 shows 25 rows and the footer reads "1-25 of 30" / BM "1-25 daripada 30" plus "Rows per page" / "Baris per halaman" set to 25 and "Page 1 of 2" / "Halaman 1 daripada 2" with numbered page buttons. Page 2 shows the remaining 5 rows and "26-30 of 30".
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-172: Rows-per-page choice is remembered across tables and visits
**Tags**: @regression **Severity**: S4 Low | **Priority**: P4 | **Tier**: T3 | **Linked**: M5-US1 **Type**: Feature
**Before you start**: Operator on Teachers with more than 10 teachers.
| Step | Action |
|------|--------|
| 1 | Change "Rows per page" to 10 |
| 2 | Navigate to Students, then back to Teachers |
| 3 | Reload the browser tab |
**What you should see**: Every list table now opens at 10 rows per page, surviving navigation and reload (stored in localStorage key `kelasapp.rows-per-page`; allowed values 10/25/50/100).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-173: CSV export downloads the current view and contains NO IC or bank data
**Tags**: @regression @security @data-integrity **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US1 **Risk**: R-TCH-pii **Type**: Feature
**Before you start**: Operator on Teachers (desktop-width window: the export button is hidden on small screens) with several teachers that have IC + bank account saved. Today's date in YYYY-MM-DD form for the filename check.
| Step | Action |
|------|--------|
| 1 | Search so only some rows remain, and hide the Email column via the column-visibility (view options) toggle |
| 2 | Click "Export CSV" / BM "Eksport CSV" |
| 3 | Open the downloaded file in a spreadsheet |
**What you should see**: A file named `teachers-<YYYY-MM-DD>.csv` downloads. It contains ONLY the filtered rows and ONLY the visible columns (no Email column after hiding it; header labels are the human column names). Crucially, NO IC number and NO bank account appear anywhere in the file: those fields are not list columns, so the export cannot leak them. Malay characters render correctly in Excel (UTF-8 BOM).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-174: No row-selection checkboxes on the teachers list
**Tags**: @regression **Severity**: S4 Low | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US1 **Type**: Feature
**Before you start**: Operator on Teachers with at least one row.
| Step | Action |
|------|--------|
| 1 | Look at the header row and each data row's leading edge |
**What you should see**: No checkbox column anywhere: the first column is the positional `#`, then Name. (TeachersTable does not pass `enableSelection`, and there are no teacher bulk actions.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: the list used to render selection checkboxes that selected rows but drove no action (dead UI); removed in commit df2e3f1 (CX6).

## S. Save and action feedback (added 2026-07-04)

### TC-TCH-180: A failed deactivate keeps the dialog open and shows the failure message
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US6 **Type**: Feature
**Before you start**: Operator on Teachers in TWO browser tabs (same session). This forces a real server refusal: sign out in one tab, then act in the other.
| Step | Action |
|------|--------|
| 1 | In tab A, open a teacher's kebab and click Deactivate (dialog opens, do NOT confirm yet) |
| 2 | In tab B, sign out of the app |
| 3 | Back in tab A, click the Deactivate confirm button |
**What you should see**: The DELETE returns non-OK (401), so the dialog STAYS OPEN and shows the red message "That did not work. Please try again." / BM "Itu tidak berjaya. Sila cuba lagi." No success toast fires and the dialog does not close as if it worked. (RowActions: a string returned from `onConfirm` is rendered as an error and blocks the close.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: destructive row actions used to fail silently, closing as if they had worked; surfaced in commit 31777bd (M3).

### TC-TCH-181: A failed form save shows an inline error and stays on the form
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: M5-US1 **Type**: Feature
**Before you start**: Operator on Teachers > Add teacher in tab A, name `Cikgu Gagal` typed; a second tab B on the same session.
| Step | Action |
|------|--------|
| 1 | In tab B, sign out of the app |
| 2 | In tab A, click Add teacher |
**What you should see**: You STAY on the form (no navigation, no "Teacher saved" toast). A red inline message appears under the form: the server's error text when the response has one (e.g. "Not authenticated"), else the fallback "Could not save the teacher. Please try again." / BM "Tidak dapat menyimpan guru. Sila cuba lagi." (TeacherForm `submitError`: `body?.error ?? t('error')`.) No teacher is created.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## T. Teacher accounts and record linking (Better Auth, added 2026-07-04)

Since the Better Auth migration plus commit b175d3e, a teacher is a real login: an org member whose
membership role is `teacher`, linked to a `teachers` record. On first sign-in, `getAccessContext`
links the account to the ACTIVE teacher record whose email matches the invited user's email (the role
itself comes from the membership, never from the email match). Self-service pages: `/dashboard/my-classes`
and `/dashboard/my-pay`.

### TC-TCH-190: First teacher sign-in links the account to their teacher record by email
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Linked**: M5-US10 **Risk**: R-TCH-role **Type**: Feature
**Before you start**: Operator has created a teacher record `Ustazah Fatimah` with email `teacher@kelastest.local` and assigned her to at least one class; the org member with that email has membership role `teacher`. Log in as `teacher@kelastest.local` / `password12345`.
| Step | Action |
|------|--------|
| 1 | Sign in and land on the dashboard |
| 2 | Open "My classes" / BM "Kelas saya" from the sidebar |
**What you should see**: You land on Attendance (teacher home). My classes is titled "My classes" with the description "Classes you teach and their schedule." and lists exactly the classes assigned to the teacher record `Ustazah Fatimah` (name + schedule), proving the login is linked to HER record and no one else's. No operator nav items (Teachers, Billing, Payroll) appear in the sidebar.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-191: A deactivated teacher record is never auto-linked on first sign-in
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: M5-US10 **Risk**: R-TCH-role **Type**: Feature
**Before you start**: Operator: create a teacher record `Cikgu Lapsed` with a fresh email (e.g. `lapsed@kelastest.local`), then DEACTIVATE it. Invite that email as an org member with the teacher role and complete the sign-up, so the first sign-in happens while the only matching record is inactive.
| Step | Action |
|------|--------|
| 1 | Sign in as `lapsed@kelastest.local` and open "My classes" |
**What you should see**: The auto-link candidate query filters `status = 'active'` and unlinked records only, so NO record is linked: My classes shows the empty message "You're not assigned to any classes yet." / BM "Anda belum ditugaskan ke mana-mana kelas." instead of the deactivated teacher's data. The role gate still applies (redirected away from operator pages).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TCH-192: A member removed from the org is denied, never downgraded to staff
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: M5-US10 **Risk**: R-TCH-role **Type**: Feature
**Before you start**: Two logins: the operator, and a second member of the org (any role) who is currently signed in on another browser. Better Auth does NOT revoke the removed member's session, so their session still points at the org after removal; the code must deny it at lookup time.
| Step | Action |
|------|--------|
| 1 | As the operator, remove the second member from the organisation (member management) |
| 2 | In the removed member's still-open browser, load `/dashboard/teachers` |
| 3 | In the same browser, call GET `/api/teachers` from the console |
**What you should see**: The page redirects to `/onboarding/organization-selection` and the API returns 401 with `error: "Not a member of this organisation"`. The removed member is NEVER treated as staff: a missing membership row throws (`resolveMemberRole`), it does not default. (Unit test: "denies (throws OrgRequiredError) when there is no membership row".)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## Coverage note

Techniques walked (per [QA-METHODOLOGY.md](QA-METHODOLOGY.md) §5):
- **Happy path** (1): 001, 002, 030, 050, 060, 070, 080, 160, 190.
- **Equivalence + boundary** (2): name length 005, IC digit count 012, passport length 014, bank account 5-digit boundary 035, account 20-digit cap 033.
- **Negative / validation + server bypass** (3): 003, 004, 011, 016, 021, 022, 034, 043, 101, plus failure surfacing 180/181.
- **Format / locale** (4): IC auto-dash 010, passport uppercase 013, phone normalise 020, RM money 073, CSV UTF-8 BOM 173, plus the i18n set 130-133.
- **Permissions / role** (5): teacher page redirect 110, teacher API 401 111, no-org 112, staff operational access + owner-only contrast 113, teacher-record linking 190/191, removed-member denial 192.
- **Cross-tenant / IDOR** (6): 120, 121, 122, 123; class count org-scoped 160.
- **State transition** (7): deactivate 060, deactivated detail 062, deactivated-still-paid 063, reactivation gap 064, grade trail transitions 150-153.
- **Concurrency / idempotency** (8): same-grade re-save writes no duplicate history 151; otherwise not applicable to teacher CRUD (no generation/double-effect step); covered in teacher-pay/billing catalogs.
- **Empty / loading / error states** (9): empty list 090, filtered-no-match 092, no-classes 072, 404 detail 074, unlinked teacher empty self-service 191.
- **Data integrity** (10): empty-field cleanup to null 006/052, grade null default 040, tenant isolation 123, grade-history audit trail 150-153, active-class count correctness 160/161, export excludes IC/bank 173.
- **Accessibility** (11): 140, 141.
- **Security (input -> render/store)** (12): XSS in name 100, mass-assignment 101, PII presentation-only masking caveat 084, PII-free CSV export 173.
- **Non-functional** (13): no perf/N+1 surface in teacher CRUD; not in this functional catalog.

Grounding: every expected result is reconciled to the service (`createTeacher`/`updateTeacher`/`deactivateTeacher`/`listTeachers`/`getTeacher`/`listInactiveTeachers`), the 8 teachers service tests (including the 3 grade-history tests from commit 2d5ff12), the shared validators + their tests, the Zod schemas (`teacherInputSchema`/`teacherUpdateSchema`/`teacherFormSchema`), the API routes (status codes), `Access.ts` + `access-role.ts` + its unit tests (Better Auth role gating), `SensitiveValue` (masking), `RowActions` (confirm/toast/error contract), the shared `DataTable` suite (search/pagination/export), and the en/ms locale files (exact strings).

2026-07-04 refresh (catalog was never executed, so stale cases were rewritten in place keeping their IDs; all new behaviour got new appended IDs; nothing was renumbered):
- Rewritten for post-catalog commits: 001, 002, 050, 060 (success toasts, 6e45620), 090 (rich empty state + Import CTA), 092 (all-column search, 746df0b), 130 (new toolbar strings), 110-113 (Better Auth roles replace Clerk; staff policy update), 084 (finding #3 note). 014 and 015 were corrected as case defects (wrong boundary text / wrong re-format value; `formatPassport` keeps all 12 chars of a 12-digit IC).
- Added: grade history 150-154 (2d5ff12), active-class count 160-161 (5cc82b9), table usability 170-174 (746df0b, df2e3f1), failure feedback 180-181 (31777bd), teacher accounts + linking 190-192 (Better Auth migration, b175d3e).
- Deleted: none (no covered feature was removed; the dead selection checkboxes had no case asserting them).

Documented code-vs-expectation gaps flagged inline, not silently asserted as passes:
1. **TC-TCH-064**: no reactivate UI control exists (server supports `status: active`, the UI does not surface it or an inactive list). Still true 2026-07-04.
2. **TC-TCH-084**: PII masking is presentation-only; the full IC/bank value reaches the operator's browser in client props. Still true 2026-07-04 (finding #3).
3. **TC-TCH-152**: clearing a grade to ungraded is not recorded in the grade-history trail.
4. **TC-TCH-154**: the grade-history table has no UI/API reader yet.
Resolved: the former gap #1 (staff not gated, finding #1) is now the documented role model after the Better Auth migration; TC-TCH-113 was rewritten to assert staff operational access plus the owner-only contrast.

**Case count: 85** (was 68 on 2026-06-30). Smoke subset (@smoke, 6, unchanged): TC-TCH-001, TC-TCH-040, TC-TCH-050, TC-TCH-060, TC-TCH-080, TC-TCH-090.
