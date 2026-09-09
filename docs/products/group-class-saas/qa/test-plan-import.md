# Test plan: Data import (CSV wizards + migration hub)

> Exhaustive manual catalog for the data-import module. Format + method: [QA-METHODOLOGY.md](QA-METHODOLOGY.md).
> Grounded in `src/features/import/{config,server,service,service.test}.ts`, `ImportWizard.tsx`,
> `src/app/api/import/route.ts`, the five wizard pages under `src/app/[locale]/(auth)/dashboard/(operator)/`,
> the migration hub page `.../(operator)/import/page.tsx`, `src/features/onboarding/GettingStartedChecklist.tsx`,
> `src/libs/Access.ts`, `src/features/ui/FileButton.tsx`, `src/locales/{en,ms}.json`, and commits
> `ac1926b` (tolerant time parsing + no silent row drops) and `8da4c9e` (guided migration hub, CX16).
> This module was built AFTER the 2026-06-30 catalog and had zero coverage until this plan.
>
> Default tier T2. T1 where flagged: enrolment fee links (money), the duplicate-enrolment guard
> (double-billing protection), role guard, tenant isolation, and server-side re-validation.
> Roles: operator and staff can import; teacher is blocked. Dev logins: operator
> `operator@kelastest.local` / `newpassword6789`; teacher `teacher@kelastest.local` / `password12345`.
> Wizard routes: `/dashboard/teachers/import`, `/dashboard/classes/import`, `/dashboard/guardians/import`,
> `/dashboard/students/import`, `/dashboard/classes/import-enrollments`; hub: `/dashboard/import`.
>
> Row-error display convention (verified in `ImportWizard.tsx` + `service.ts`): errors and warnings read
> `Row N: field: code`, where Row 2 is the FIRST data row (row 1 = the header line). The codes are internal
> validation keys shown untranslated in both EN and BM: `required`, `email`, `phone_my`, `ic_or_passport`,
> `bank_account`, `money_format`, `time_hhmm`, `unknown_day:<token>`, `required_int`, `unknown_value`, `date_ymd`.
>
> Smoke subset (@smoke): TC-IMP-014, TC-IMP-016, TC-IMP-019, TC-IMP-021, TC-IMP-022, TC-IMP-031, TC-IMP-033, TC-IMP-048.

---

## A. Entry points + templates

### TC-IMP-001: Every list page exposes its import wizard entry point
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2 | **Linked**: US-imp-entry **Type**: Feature
**Before you start**: Log in as operator (`operator@kelastest.local` / `newpassword6789`).
| Step | Action |
|------|--------|
| 1 | Go to Students; click the outline "Import" button in the title bar |
| 2 | Go to Teachers; click "Import" |
| 3 | Go to Guardians; click "Import" |
| 4 | Go to Classes; click the "Import" dropdown and read its two items |
| 5 | Pick "Import classes", go back, pick "Import enrollments" |
**What you should see**: Steps 1-3 land on `/dashboard/students/import`, `/dashboard/teachers/import`, `/dashboard/guardians/import`, each showing a card titled "Import from a spreadsheet" with section "1. Upload your file", a "Download template" button, and a "Choose CSV file" button with hint "Upload a .csv from Excel or Google Sheets. The first row should be column headers." Step 4's dropdown shows exactly "Import classes" and "Import enrollments"; they open `/dashboard/classes/import` and `/dashboard/classes/import-enrollments`.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-IMP-002: Students template downloads with canonical headers and one example row
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator on `/dashboard/students/import`.
| Step | Action |
|------|--------|
| 1 | Click "Download template" |
| 2 | Open the downloaded file in a text editor |
**What you should see**: A file named `students-template.csv` containing exactly the headers `Name,Level,IC,Phone,Email` and one example row `Adam bin Ali,Iqra 3,120101101234,0123456789,adam@example.com`.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-003: Classes and enrolments templates carry their full column sets
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator; open each wizard from the Classes list Import dropdown.
| Step | Action |
|------|--------|
| 1 | On the classes wizard, download the template and read the header line |
| 2 | On the enrolments wizard, download the template and read the header line |
**What you should see**: `classes-template.csv` headers: `Class name,Program,Level,Teacher,Days,Time,Duration (minutes),Monthly fee (RM),Class type,Mode,Teacher rate (RM),Pay model,Capacity,Notes` with example row values `Iqra Pagi`, `Al-Quran`, `Iqra 3`, `Ustaz Ali`, `Mon,Wed,Fri`, `16:00`, `60`, `150`, `Small group`, `Physical`, `20`, `Per session`, `15`. `enrollments-template.csv` headers: `Student,Class,Start date,Fee override (RM),Notes` with example `Adam bin Ali,Iqra Pagi,2026-01-15,,`.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## B. Upload + parse boundaries

### TC-IMP-004: Header-only CSV yields zero rows and a disabled import button
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on `/dashboard/students/import`.
**Test Data**: a file `header-only.csv` containing the single line:
```
Name,Level,IC,Phone,Email
```
| Step | Action |
|------|--------|
| 1 | Upload `header-only.csv` |
| 2 | Read the review section |
**What you should see**: Columns auto-map (all five show a tick). The review summary reads "0 ready to import, 0 with problems." and the button "Import 0 rows" is disabled. Nothing can be imported.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-005: A completely empty (0-byte) file does not crash the wizard
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on `/dashboard/students/import`. Create an empty file: in Terminal, `touch empty.csv`.
| Step | Action |
|------|--------|
| 1 | Upload `empty.csv` |
**What you should see**: No crash or blank screen. Either the parse error "Could not read that file. Make sure it is a CSV." appears, or the mapping step renders with no header options (every field "(Not imported)") and the message "Map all required columns (marked *) to continue." blocks the import. Record which of the two you got.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-006: A non-CSV file degrades gracefully
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on `/dashboard/students/import`. Prepare `notes.txt` containing one paragraph of plain prose (no commas). The file picker filters to `.csv`; choose "All files" / "Options > All files" in the OS dialog to select it.
| Step | Action |
|------|--------|
| 1 | Upload `notes.txt` |
**What you should see**: No crash. Either "Could not read that file. Make sure it is a CSV." or the first text line is treated as a single header, nothing auto-maps, and "Map all required columns (marked *) to continue." blocks the import. In no outcome does an import run.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-007: Blank lines and empty rows are skipped from the row count
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on `/dashboard/students/import`.
**Test Data**: `blanks.csv`:
```
Name,Level,IC,Phone,Email
Nur Aisyah binti Ahmad,Iqra 3,,,

,,,,
Adam bin Razali,,,,

```
| Step | Action |
|------|--------|
| 1 | Upload `blanks.csv` and read the review summary |
**What you should see**: "2 ready to import, 0 with problems." The blank line and the commas-only row are not counted or imported.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-008: More than 2000 data rows is rejected by the server cap
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on `/dashboard/students/import`. In a spreadsheet, create a `Name` column and fill down `Student 1` ... `Student 2001` (2001 data rows); save as `big.csv`. Note your current student count first.
| Step | Action |
|------|--------|
| 1 | Upload `big.csv`, confirm the summary shows "2001 ready to import, 0 with problems." |
| 2 | Click "Import 2001 rows" |
| 3 | Go back to Students and re-check the count |
**What you should see**: The import fails with "Import failed. Please try again." (the API caps `rows` at 2000 and returns 422). The student count is unchanged: nothing partially imported. A 2000-row file, by contrast, is accepted.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## C. Column mapping

### TC-IMP-009: Canonical template headers auto-map with tick marks
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-imp-map **Type**: Feature
**Before you start**: Operator on `/dashboard/students/import` with the downloaded template (TC-IMP-002) plus one real data row added.
| Step | Action |
|------|--------|
| 1 | Upload the file and read section "2. Match your columns" |
**What you should see**: All five fields (Name marked with a red `*`, Level, IC / Passport, Phone, Email) show a tick and their dropdowns are pre-selected to the matching CSV header. The review section unlocks.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-010: Malay and messy headers auto-map by alias (case/punctuation-insensitive)
**Tags**: @regression @i18n **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-imp-map **Type**: Feature
**Before you start**: Operator on `/dashboard/students/import`.
**Test Data**: `bm-headers.csv`:
```
Nama Pelajar,Tahap,Kad Pengenalan,No. Telefon,Emel
Nur Aisyah binti Ahmad,Iqra 3,120304145566,0123456789,aisyah@example.com
```
| Step | Action |
|------|--------|
| 1 | Upload the file and read the mapping |
**What you should see**: Every field auto-maps: Name -> `Nama Pelajar`, Level -> `Tahap`, IC / Passport -> `Kad Pengenalan`, Phone -> `No. Telefon` (the dot is ignored), Email -> `Emel`. Review shows "1 ready to import, 0 with problems."
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-011: An unrecognised header stays unmapped and can be mapped manually
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on `/dashboard/students/import`.
**Test Data**: `odd-header.csv` (note: `Full Name` is NOT a known alias):
```
Full Name,Level
Adam bin Razali,Form 4
```
| Step | Action |
|------|--------|
| 1 | Upload the file; read the Name row in the mapping |
| 2 | Open the Name dropdown and pick `Full Name` |
**What you should see**: On upload, Name shows "(Not imported)" with no tick and the review is blocked with "Map all required columns (marked *) to continue." After step 2 the tick appears and the review unlocks showing "1 ready to import, 0 with problems."
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-012: Unmapping a required column re-blocks the import
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator with any valid students CSV uploaded and fully mapped.
| Step | Action |
|------|--------|
| 1 | In the mapping, set Name to "(Not imported)" |
**What you should see**: The review section is replaced by "Map all required columns (marked *) to continue." No preview, no import button. Optional columns (Level, IC, Phone, Email) set to "(Not imported)" do NOT block; those cells are simply not imported.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## D. Preview + row-error reporting

### TC-IMP-013: Preview shows the first 5 rows and the full valid/invalid count
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator on `/dashboard/students/import` with a CSV of 7 valid student rows (headers `Name,Level`; names `Pelajar Satu` ... `Pelajar Tujuh`).
| Step | Action |
|------|--------|
| 1 | Upload the file and read the review section |
**What you should see**: Summary "7 ready to import, 0 with problems." The preview table shows only the first 5 rows (Pelajar Satu to Pelajar Lima); unmapped cells show `-`. The button reads "Import 7 rows".
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-014: Row errors are reported per row with correct spreadsheet row numbers, capped at 8 shown
**Tags**: @smoke @regression @data-integrity **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Linked**: US-imp-errors **Risk**: R-imp-silent-drop **Type**: Feature
**Before you start**: Operator on `/dashboard/students/import`.
**Test Data**: `errors.csv` with 3 valid + 10 invalid rows (rows 2-4 valid; rows 5-14 have an empty Name):
```
Name,Level,IC,Phone,Email
Valid Satu,Iqra 1,,,
Valid Dua,,,,
Valid Tiga,,,,
,Iqra 2,,,
,Iqra 2,,,
,Iqra 2,,,
,Iqra 2,,,
,Iqra 2,,,
,Iqra 2,,,
,Iqra 2,,,
,Iqra 2,,,
,Iqra 2,,,
,Iqra 2,,,
```
| Step | Action |
|------|--------|
| 1 | Upload the file and read the review section |
**What you should see**: Summary "3 ready to import, 10 with problems." Below the preview, an error list shows the first 8 problem rows only, each formatted like "Row 5: name: required" (Row 5 = the first empty-name line; row numbers match the spreadsheet, header = row 1). The button reads "Import 3 rows" and is enabled. No invalid row is silently ignored: every problem row is either listed or included in the "10 with problems" count.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked
**Notes**: Core of the no-silent-drop contract (see also TC-IMP-024, REGRESSION ac1926b).

### TC-IMP-015: Zero valid rows disables the import button
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on `/dashboard/students/import`.
**Test Data**: a CSV whose only data row has an empty Name (`,Iqra 1,,,` under the standard headers).
| Step | Action |
|------|--------|
| 1 | Upload it and inspect the review section |
**What you should see**: "0 ready to import, 1 with problems.", the error line "Row 2: name: required", and the "Import 0 rows" button disabled.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## E. Students import

### TC-IMP-016: Happy path: import three students end to end
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Linked**: US-imp-students **Risk**: R-imp-students **Type**: Feature
**Before you start**: Operator on `/dashboard/students/import`. Note the current student count.
**Test Data**: `students.csv`:
```
Name,Level,IC,Phone,Email
Nur Aisyah binti Ahmad,Iqra 3,120304145566,012-345 6789,aisyah@example.com
Adam bin Razali,Form 4,,0198765432,
Mei Ling Tan,,A1234567,,
```
| Step | Action |
|------|--------|
| 1 | Upload the file; confirm "3 ready to import, 0 with problems." |
| 2 | Click "Import 3 rows"; watch the button while it runs |
| 3 | On the result screen, click "Back to the list" |
**What you should see**: While running, the button reads "Importing..." and is disabled. Then "Import complete" with "3 imported, 0 skipped." and no warnings block. "Back to the list" lands on `/dashboard/students`, where all three appear with status Active; levels show `Iqra 3`, `Form 4`, and `-`. The third row's `A1234567` is accepted (the shared field takes an IC or a passport).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-017: Student field validation matches the manual form, per row
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on `/dashboard/students/import`.
**Test Data**: `bad-students.csv`:
```
Name,Level,IC,Phone,Email
,Iqra 1,,,
Salah Telefon,,,12345,
Salah Emel,,,,not-an-email
Salah IC,,12,,
```
| Step | Action |
|------|--------|
| 1 | Upload the file and read the error list |
**What you should see**: "0 ready to import, 4 with problems." with exactly: "Row 2: name: required", "Row 3: phone: phone_my", "Row 4: email: email", "Row 5: icNumber: ic_or_passport". Import disabled. The rules are the same shared validators as the Add student form.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-018: Name length boundary (120 accepted, 121 rejected)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on `/dashboard/students/import`.
**Test Data**: two rows under header `Name`: row A = the letter `A` repeated exactly 120 times; row B = `A` repeated exactly 121 times.
| Step | Action |
|------|--------|
| 1 | Upload and read the review |
**What you should see**: "1 ready to import, 1 with problems." Row 3 (the 121-char name) is listed with an error on `name` (zod max-length message). The 120-char row imports.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## F. Teachers import

### TC-IMP-019: Happy path: import teachers with bank details
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Linked**: US-imp-teachers **Type**: Feature
**Before you start**: Operator on `/dashboard/teachers/import`.
**Test Data**: `teachers.csv`:
```
Name,Phone,Email,Bank,Account Number
Ustaz Ali,0123456789,ali@example.com,Maybank,1234567890
Cikgu Siti,,,,
```
| Step | Action |
|------|--------|
| 1 | Upload; confirm "2 ready to import, 0 with problems."; click "Import 2 rows" |
| 2 | Back to the list; open Ustaz Ali's detail page |
**What you should see**: "2 imported, 0 skipped." Both teachers appear in the Teachers list. Ustaz Ali's detail shows bank `Maybank` and the account number stored (displayed per the teachers module's masking rules, see test-plan-teachers). Cikgu Siti has all optional fields as `-`.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-020: Bank account digits boundary (5-20 digits)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on `/dashboard/teachers/import`.
**Test Data**: rows under `Name,Account Number`: `Guru A,1234` (4 digits, too short), `Guru B,ABCDE` (no digits), `Guru C,12345` (5 digits, minimum valid).
| Step | Action |
|------|--------|
| 1 | Upload and read the review |
**What you should see**: "1 ready to import, 2 with problems." Rows 2 and 3 list "bankAccount: bank_account"; Guru C is importable.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## G. Guardians import

### TC-IMP-021: Happy path: import guardians
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Linked**: US-imp-guardians **Type**: Feature
**Before you start**: Operator on `/dashboard/guardians/import`.
**Test Data**: `guardians.csv`:
```
Name,Phone,Email
Puan Aisyah,012-345 6789,aisyah@example.com
Encik Ahmad,,
```
| Step | Action |
|------|--------|
| 1 | Upload; click "Import 2 rows"; back to the list |
**What you should see**: "2 imported, 0 skipped." Both guardians appear on Guardians with status Active; Encik Ahmad's phone/email show `-`. (Note: the import cannot link students to guardians; the wizard only creates guardian records. Linking is a manual step or a deferred import feature.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## H. Classes import

### TC-IMP-022: Happy path: full class row with program/level/teacher resolved by name
**Tags**: @smoke @regression @data-integrity **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Linked**: US-imp-classes **Risk**: R-imp-classes **Type**: Feature
**Before you start**: Operator. A teacher named `Ustaz Ali` exists (import via TC-IMP-019 or add manually); the taxonomy has a program `Al-Quran` and a level `Iqra 3` (Settings > programs/levels). Open `/dashboard/classes/import`.
**Test Data**: `classes.csv` (note the lower-case names to prove case-insensitive matching):
```
Class name,Program,Level,Teacher,Days,Time,Duration (minutes),Monthly fee (RM),Class type,Mode,Teacher rate (RM),Pay model,Capacity,Notes
Iqra Pagi,al-quran,iqra 3,ustaz ali,"Mon,Wed,Fri",16:00,60,150,Small group,Physical,20,Per session,15,
```
| Step | Action |
|------|--------|
| 1 | Upload; confirm "1 ready to import, 0 with problems."; click "Import 1 rows" |
| 2 | Back to the list; open the new class `Iqra Pagi` |
**What you should see**: "1 imported, 0 skipped." with NO warnings block (all three names matched despite the case difference). The class detail shows teacher `Ustaz Ali`, program `Al-Quran`, level `Iqra 3`, a weekly schedule on Mon, Wed and Fri at 4:00 PM, duration 60 minutes, monthly fee RM 150.00, small group, physical, capacity 15, pay model per session at RM 20.00.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-023: Tolerant time parsing accepts 12-hour and Malay formats (REGRESSION ac1926b)
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Linked**: US-imp-time **Risk**: R-imp-time **Type**: Feature
**Before you start**: Operator on `/dashboard/classes/import`.
**Test Data**: `times.csv`:
```
Class name,Days,Time,Duration (minutes),Monthly fee (RM)
Kelas A,Mon,5:00 PM,60,100
Kelas B,Mon,5pm,60,100
Kelas C,Mon,9:00,60,100
Kelas D,Mon,5.00 petang,60,100
Kelas E,Mon,12:00 AM,60,100
Kelas F,Mon,7 pagi,60,100
Kelas G,Mon,3.00pm,60,100
```
| Step | Action |
|------|--------|
| 1 | Upload; confirm "7 ready to import, 0 with problems."; import |
| 2 | Open each class and read its schedule time |
**What you should see**: All 7 rows import with no errors. Stored times normalise to 24h and display 12-hour: Kelas A 5:00 PM, B 5:00 PM, C 9:00 AM, D 5:00 PM, E 12:00 AM, F 7:00 AM, G 3:00 PM.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: before commit `ac1926b` only strict 24h `HH:MM` was accepted, so real-world spreadsheets with `5:00 PM` / `5.00 petang` failed. This case pins the tolerant parser.

### TC-IMP-024: Unmatched optional program/level/teacher imports the row WITH a warning, never a silent drop (REGRESSION ac1926b)
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Linked**: US-imp-warnings **Risk**: R-imp-silent-drop **Type**: Feature
**Before you start**: Operator on `/dashboard/classes/import`. Confirm NO teacher named `Ustaz Tiada` exists.
**Test Data**: `typo-teacher.csv`:
```
Class name,Teacher,Days,Time,Duration (minutes),Monthly fee (RM)
Kelas Typo,Ustaz Tiada,Sun,09:00,60,100
```
| Step | Action |
|------|--------|
| 1 | Upload; the review shows "1 ready to import, 0 with problems."; import |
| 2 | Read the result screen carefully |
| 3 | Open the class `Kelas Typo` |
**What you should see**: "1 imported, 0 skipped." AND a warnings block titled "Imported, but check these:" listing `Row 2: Teacher "Ustaz Tiada" was not found, so it was left blank.` The class exists with no teacher assigned; everything else on the row is saved. The same pattern applies to an unmatched Program or Level name (message `Program "X" was not found, so it was left blank.` / `Level "X" ...`).
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: before `ac1926b` an unmatched optional name silently dropped the WHOLE row: it vanished from the import with no error and no count. This case pins import-with-warning behaviour.

### TC-IMP-025: Unparseable times are still rejected with a row error
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Risk**: R-imp-time **Type**: Feature
**Before you start**: Operator on `/dashboard/classes/import`.
**Test Data**: rows under `Class name,Days,Time,Duration (minutes),Monthly fee (RM)`: times `sometime after lunch`, `25:00`, `16.00` (24h with a dot is NOT supported), `5:60 pm`.
| Step | Action |
|------|--------|
| 1 | Upload and read the error list |
**What you should see**: "0 ready to import, 4 with problems."; each row listed with "time: time_hhmm". Tolerance has limits: only 24h `HH:MM`, 12h am/pm, and Malay pagi/tengah hari/petang/malam forms parse.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-026: Malay day names, mixed separators, and duplicate days dedupe
**Tags**: @regression @i18n **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on `/dashboard/classes/import`.
**Test Data**: two rows under the TC-IMP-025 headers: `Kelas BM` with Days `Isnin, Rabu; Jumaat` and `Kelas Dup` with Days `Mon,Monday` (both Time `10:00`, Duration `60`, Fee `100`).
| Step | Action |
|------|--------|
| 1 | Upload; confirm "2 ready to import, 0 with problems."; import |
| 2 | Open each class's schedule |
**What you should see**: `Kelas BM` meets Monday, Wednesday and Friday (BM day names + comma/semicolon separators all parse). `Kelas Dup` has exactly ONE Monday slot (the duplicate `Monday` token dedupes, not two slots).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-027: An unknown day token names itself in the row error
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on `/dashboard/classes/import`.
**Test Data**: one row with Days `Mon,Funday` (Time `10:00`, Duration `60`, Fee `100`).
| Step | Action |
|------|--------|
| 1 | Upload and read the error list |
**What you should see**: "0 ready to import, 1 with problems." with "Row 2: days: unknown_day:Funday" (the bad token is echoed). The row does not import.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-028: Enum aliases (EN + BM) resolve; blanks take form defaults; unknown values error
**Tags**: @regression @i18n **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on `/dashboard/classes/import`.
**Test Data**: three rows under `Class name,Days,Time,Duration (minutes),Monthly fee (RM),Class type,Mode,Pay model`:
```
Kelas Alias,Mon,10:00,60,100,kumpulan besar,dalam talian,per pelajar
Kelas Default,Mon,10:00,60,100,,,
Kelas Salah,Mon,10:00,60,100,Mega group,,
```
| Step | Action |
|------|--------|
| 1 | Upload and read the review |
| 2 | Import, then open the two imported classes |
**What you should see**: "2 ready to import, 1 with problems."; `Kelas Salah` errors with "classType: unknown_value". `Kelas Alias` saves as large group / online / per student (BM labels resolved). `Kelas Default` saves the manual-form defaults: small group / physical / per session, capacity 30, teacher rate RM 0.00.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-029: Duration and capacity integer boundaries
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on `/dashboard/classes/import`.
**Test Data**: rows under `Class name,Days,Time,Duration (minutes),Monthly fee (RM),Capacity`: durations `1` (min ok), `600` (max ok), `0`, `601`, `60.5`; and one row with Duration `60` and Capacity `501`.
| Step | Action |
|------|--------|
| 1 | Upload and read the review |
**What you should see**: The `1` and `600` rows are valid. `0`, `601` and `60.5` each error "durationMinutes: required_int". Capacity `501` errors "capacityMax: required_int" (valid range 1-500; blank capacity defaults to 30).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-030: Money format on fee and rate: digits with at most 2 decimals, no prefix, no negatives
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Risk**: R-imp-money-format **Type**: Feature
**Before you start**: Operator on `/dashboard/classes/import`.
**Test Data**: rows under `Class name,Days,Time,Duration (minutes),Monthly fee (RM)` with fees `150.50` (valid), `RM150`, `free`, `-50`, `150.505`.
| Step | Action |
|------|--------|
| 1 | Upload and read the review |
| 2 | Separately upload one row with fee `1000001` and import it |
**What you should see**: Step 1: "1 ready to import, 4 with problems."; each bad row errors "monthlyFee: money_format" (type the number only: `150` or `150.50`, never `RM150`). Step 2: the 1000001 row passes the preview but the server-side schema (max RM 1,000,000) rejects it at create time: result reads "0 imported, 1 skipped.", counted, never silently lost.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## I. Enrolments import

### TC-IMP-031: Happy path: enrolment resolves student and class by case-insensitive name
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Linked**: US-imp-enrol **Risk**: R-imp-enrol **Type**: Feature
**Before you start**: Operator. A student `Adam bin Razali` and a class `Iqra Pagi` exist (from TC-IMP-016/022). Open `/dashboard/classes/import-enrollments`.
**Test Data**: `enrol.csv`:
```
Student,Class,Start date,Fee override (RM),Notes
adam bin razali,iqra pagi,2026-01-15,,
```
| Step | Action |
|------|--------|
| 1 | Upload; confirm "1 ready to import, 0 with problems."; import |
| 2 | Open the class `Iqra Pagi` roster |
**What you should see**: "1 imported, 0 skipped." Adam bin Razali appears on the roster with status Active and start date 15/01/2026, despite the lower-case names in the CSV.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-032: Blank start date defaults to today; blank fee override uses the class fee
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P1 | **Tier**: T1 | **Linked**: US-imp-enrol-fee **Risk**: R-imp-fee-link **Type**: Feature
**Before you start**: Operator; a student and a class with a known monthly fee exist (e.g. `Iqra Pagi` at RM 150.00) and the student is NOT yet enrolled in it. Open the enrolments wizard.
**Test Data**: one row `Nur Aisyah binti Ahmad,Iqra Pagi,,,` under the standard headers (Start date and Fee override both blank).
| Step | Action |
|------|--------|
| 1 | Upload and import |
| 2 | Open the student's detail page and read the Enrolled classes row |
**What you should see**: The enrolment's start date is today (DD/MM/YYYY) and its Fee column shows RM 150.00, the class monthly fee (blank override = use class fee, exactly like the manual Enrol form). This fee is what billing will invoice: it must never come out blank or zero.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-033: Fee override in the CSV drives the effective fee (money path)
**Tags**: @smoke @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-imp-enrol-fee **Risk**: R-imp-fee-link **Type**: Feature
**Before you start**: Operator; a class with monthly fee RM 150.00 and a student not yet enrolled in it. Open the enrolments wizard.
**Test Data**: one row `Mei Ling Tan,Iqra Pagi,2026-02-01,60,` (Fee override = 60).
| Step | Action |
|------|--------|
| 1 | Upload and import |
| 2 | Open the student's detail; read the Fee column of the new enrolment |
| 3 | If a billing month can be generated safely in this environment, run billing for a month covering the enrolment and open the draft invoice |
**What you should see**: The Fee column shows RM 60.00, NOT RM 150.00. The generated invoice line for this enrolment bills RM 60.00 (effective fee = override else class fee; cross-ref test-plan-billing). A wrong number here corrupts real family bills, which is why this is T1.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-034: Enrolment date and fee formats are validated per row
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on the enrolments wizard.
**Test Data**: rows under the standard headers: Start date `15/01/2026` (DD/MM/YYYY not accepted here); Fee override `nope`; Fee override `-10`; Fee override `60.999`.
| Step | Action |
|------|--------|
| 1 | Upload and read the error list |
**What you should see**: "0 ready to import, 4 with problems." with "startedAt: date_ymd" on the first row and "feeOverride: money_format" on the other three. The CSV date format is `YYYY-MM-DD` (as in the template example `2026-01-15`); the wizard does not accept Malaysian display format in the file.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-035: An unmatched student or class name fails that row, counted in the summary
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on the enrolments wizard. Confirm no class named `Kelas Tiada` exists.
**Test Data**: one row `Adam bin Razali,Kelas Tiada,2026-01-15,,`.
| Step | Action |
|------|--------|
| 1 | Upload (preview shows "1 ready to import": names are only resolved server-side); import |
**What you should see**: Result "0 imported, 1 skipped." No enrolment is created. Unlike a class's optional teacher (TC-IMP-024), the enrolment's student and class are REQUIRED references: an unmatched name fails the row rather than importing something half-linked.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-036: An ambiguous student name (two students with the same name) fails the row rather than guessing
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Risk**: R-imp-ambiguous **Type**: Feature
**Before you start**: Operator; create TWO students both named exactly `Ali` (Add student twice), and have any class available.
**Test Data**: one row `Ali,Iqra Pagi,2026-01-15,,`.
| Step | Action |
|------|--------|
| 1 | Upload and import |
| 2 | Check both `Ali` students' detail pages |
**What you should see**: "0 imported, 1 skipped." NEITHER Ali gets enrolled: the importer refuses to guess between duplicate names. (Enrolling the right Ali must be done manually.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-037: A duplicate enrolment row inside one file imports once
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T1 | **Risk**: R-imp-double-bill **Type**: Feature
**Before you start**: Operator; a student and class not yet linked. Open the enrolments wizard.
**Test Data**: the SAME row twice:
```
Student,Class,Start date,Fee override (RM),Notes
Nur Aisyah binti Ahmad,Kelas BM,2026-03-01,,
Nur Aisyah binti Ahmad,Kelas BM,2026-03-01,,
```
| Step | Action |
|------|--------|
| 1 | Upload (preview: "2 ready to import"); import |
| 2 | Open the class roster |
**What you should see**: "1 imported, 1 skipped." The roster shows exactly ONE enrolment for the student (the duplicate guard on student+class+start date catches the second row). Two enrolments would double the family's invoice.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## J. Idempotency + summary reconciliation

### TC-IMP-038: Re-running the same enrolments file imports nothing new
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-imp-idempotent **Risk**: R-imp-double-bill **Type**: Feature
**Before you start**: Operator; you have just completed TC-IMP-031 (its file imported once already).
| Step | Action |
|------|--------|
| 1 | Open the enrolments wizard again and upload the exact same `enrol.csv` |
| 2 | Import; read the result; re-open the class roster |
**What you should see**: "0 imported, 1 skipped." The roster still shows exactly one enrolment row for that student + class + start date. Re-running an enrolment import is safe: it can never double-enrol (and thus never double-bill).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-039: Re-running the same students file DOES create duplicates (documented behaviour)
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator; you have just completed TC-IMP-016 (3 students imported). Note the student count.
| Step | Action |
|------|--------|
| 1 | Upload the same `students.csv` again and import |
| 2 | Search the Students list for `Nur Aisyah binti Ahmad` |
**What you should see**: "3 imported, 0 skipped." and the list now shows TWO students of each name: students (like teachers and guardians) have no natural key, so the importer intentionally does not dedupe them. This is expected today, but record it, because duplicate names then break enrolment import for those students (see TC-IMP-036). Testers should warn centres to import each people file only once.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-040: The result summary reconciles: imported + skipped = data rows; no double submit
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Linked**: US-imp-summary **Risk**: R-imp-counts **Type**: Feature
**Before you start**: Operator on `/dashboard/students/import`. Note the current student count.
**Test Data**: `mixed.csv` (3 valid, 2 invalid):
```
Name,Level,IC,Phone,Email
Baik Satu,Iqra 1,,,
Baik Dua,,,,
Baik Tiga,,,,
,Iqra 2,,,
Salah Emel,,,,bukan-emel
```
| Step | Action |
|------|--------|
| 1 | Upload; confirm "3 ready to import, 2 with problems." |
| 2 | Click "Import 3 rows"; while it shows "Importing...", try clicking again |
| 3 | Read the result; click "Back to the list"; count the new students |
**What you should see**: The button is disabled while "Importing..." (the second click does nothing, so no double import). Result: "Import complete", "3 imported, 2 skipped." 3 + 2 = 5 = the file's data rows; exactly 3 new students exist. "Back to the list" lands on `/dashboard/students`.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## K. API direct / server-side bypass

### TC-IMP-041: Teacher role is rejected by the import API
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-imp-rbac **Risk**: R-imp-rbac **Type**: API
**Before you start**: Log in as the teacher (`teacher@kelastest.local` / `password12345`). In the browser DevTools console, POST to the API with the session cookie.
**Test Data**: `fetch('/api/import', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ entity: 'students', rows: [{ name: 'Hacked Student' }] }) }).then(r => r.status)`
| Step | Action |
|------|--------|
| 1 | Run the fetch and note the status and body |
| 2 | As operator, search Students for `Hacked Student` |
**What you should see**: Status 401 with body `{"error":"Forbidden: operators only"}` (requireOperatorContext rejects teachers). No student named `Hacked Student` exists.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-042: The server re-validates every row; UI validation cannot be bypassed
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-imp-server-validate **Risk**: R-imp-bypass **Type**: API
**Before you start**: Operator session; POST directly to `/api/import` from DevTools (bypassing the wizard's preview).
**Test Data**: body `{"entity":"students","rows":[{"name":"API Sah"},{"name":""},{"name":"API Emel","email":"nope"}]}`
| Step | Action |
|------|--------|
| 1 | POST the body and read the JSON response |
| 2 | Check the Students list |
**What you should see**: 200 with `{"data":{"imported":1,"failed":0,"invalidRows":2,"warnings":[]}}`. Only `API Sah` was created; the empty-name and bad-email rows were rejected server-side even though no UI validation ran.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-043: Malformed payloads get a 4xx validation response, never a 500
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: API
**Before you start**: Operator session; POST to `/api/import` from DevTools.
**Test Data**: (a) `{"entity":"invoices","rows":[]}` (unknown entity); (b) `{"entity":"students","rows":[{"name":123}]}` (non-string cell); (c) a `rows` array of 2001 items `{"name":"x"}`; (d) a raw body of `{not json` with content-type application/json.
| Step | Action |
|------|--------|
| 1 | POST each body in turn and note each status |
**What you should see**: All four return 422 `{"error":"Invalid input"}`: (a) entity enum, (b) string-only cells, (c) 2000-row cap, (d) malformed JSON. REGRESSION note for (d): the route used to parse `request.json()` outside its validation guard and 500ed on a malformed body; fixed in 380a374 (2026-07-04, verified against the running API). A 500 on (d) is a regression of that fix.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-044: No active organisation: pages redirect, API 401s
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: A signed-in user with no organisation selected (fresh account that has not completed org onboarding).
| Step | Action |
|------|--------|
| 1 | Navigate to `/dashboard/import` and `/dashboard/students/import` |
| 2 | POST `{"entity":"students","rows":[]}` to `/api/import` from DevTools |
**What you should see**: Both pages redirect to `/onboarding/organization-selection`. The API returns 401 with the no-organisation error ("No active organisation selected", same contract as the People module, see TC-STU-094). Nothing imports.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## L. Permissions + tenant isolation

### TC-IMP-045: Teacher cannot reach any import page
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-imp-rbac **Risk**: R-imp-rbac **Type**: Feature
**Before you start**: Log in as the teacher (`teacher@kelastest.local` / `password12345`).
| Step | Action |
|------|--------|
| 1 | Navigate directly to `/dashboard/import` |
| 2 | Navigate directly to `/dashboard/students/import` |
| 3 | Navigate directly to `/dashboard/classes/import-enrollments` |
**What you should see**: Every URL redirects to `/dashboard/attendance` (the operator route-group guard). No wizard or hub content ever renders for a teacher.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-046: Imported rows land only in the caller's org; cross-org names never resolve
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-imp-tenant **Risk**: R-imp-cross-tenant **Type**: Feature
**Before you start**: Two orgs A and B (create a second org via onboarding if needed). Org A has a teacher `Ustaz Org A` and a student `Pelajar Org A`; org B has neither. Log in as org B's operator.
| Step | Action |
|------|--------|
| 1 | As org B, import a class CSV whose Teacher column says `Ustaz Org A` |
| 2 | As org B, import an enrolment CSV whose Student column says `Pelajar Org A` |
| 3 | As org B, import a students CSV with a new name `Pelajar Import B` |
| 4 | Switch to org A: check its Teachers, Students, Classes lists |
**What you should see**: Step 1: the class imports with a warning (`Teacher "Ustaz Org A" was not found...`) and NO teacher assigned: name resolution only searches org B. Step 2: "0 imported, 1 skipped." (org A's student is invisible). Step 3's student appears ONLY in org B. Step 4: org A's lists are completely unchanged; nothing from org B's imports leaks in.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-047: Migration hub counts are tenant-scoped
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Risk**: R-imp-cross-tenant **Type**: Feature
**Before you start**: Two orgs: one with data (teachers/students imported), one brand new.
| Step | Action |
|------|--------|
| 1 | Open `/dashboard/import` in the org with data; note the ticks and counts |
| 2 | Switch to the fresh org and open `/dashboard/import` |
**What you should see**: The data org shows green ticks with "N already in" matching ITS own record counts. The fresh org shows numbered circles 1-5 with no ticks and no counts: the other org's data never bleeds into its progress.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## M. Migration hub (CX16, commit 8da4c9e)

### TC-IMP-048: The hub lists the five imports in dependency order with live done-ticks
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Linked**: US-imp-hub **Risk**: R-imp-hub **Type**: Feature
**Before you start**: Operator in an org with at least one teacher but no classes (import one teacher first if needed). Go to `/dashboard/import`.
| Step | Action |
|------|--------|
| 1 | Read the page title, step order and per-step text |
| 2 | Click the "Import" button on the Classes step |
| 3 | Go back to `/dashboard/import` after importing one class |
**What you should see**: Title "Move your data in" with description "Bring your centre over from Excel or an old system. Follow the order below - later steps link to earlier ones." Five cards in this exact order: Teachers ("Start here. Classes need a teacher."), Classes ("Each class links to a teacher from step 1."), Guardians ("Parents must exist before students link to them."), Students ("Student rows can reference guardians from step 3."), Enrolments ("Finally: connect students to classes."). The Teachers card shows a tick and "1 already in" (its Import button styled as outline); the others show their step number. Step 2's button opens `/dashboard/classes/import`; after step 3, the Classes card also shows a tick and its count.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-049: The getting-started checklist links existing-data centres to the hub
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: US-imp-hub **Type**: Feature
**Before you start**: Operator in an org where the getting-started checklist still shows on the dashboard home (a new org that has not completed all checklist steps).
| Step | Action |
|------|--------|
| 1 | On `/dashboard`, find the checklist card and read the footer line |
| 2 | Click it |
**What you should see**: A link reading "Have existing data? Import it from Excel instead." (BM: "Ada data sedia ada? Import dari Excel.") that navigates to `/dashboard/import`. Note: this checklist link and the direct URL are the only ways into the hub; there is no sidebar item.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## N. Internationalisation

### TC-IMP-050: The wizard and hub render fully in BM; known English leaks are recorded
**Tags**: @regression @i18n **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Linked**: US-i18n **Type**: Feature
**Before you start**: Operator; switch the app language to Bahasa Melayu. Have a small students CSV ready, including one bad row (empty name) and, for step 3, the TC-IMP-024 typo-teacher classes CSV.
| Step | Action |
|------|--------|
| 1 | Open a wizard and walk it end to end with the students CSV |
| 2 | Read every label along the way |
| 3 | Run the classes import with the unmatched teacher and read the result warnings |
| 4 | Open `/dashboard/import` |
**What you should see**: Step 1-2: "Import daripada hamparan", "Muat turun templat", "Pilih fail CSV", "1. Muat naik fail anda", "2. Padankan lajur anda", "(Tidak diimport)", "Padankan semua lajur wajib (bertanda *) untuk teruskan.", "3. Semak dan import", "N sedia diimport, N bermasalah.", "Import N baris", "Mengimport...", "Import selesai", "N diimport, N dilangkau.", "Kembali ke senarai". Step 3: the warnings title is BM ("Diimport, tetapi semak yang berikut:") BUT the warning sentence itself (`Teacher "..." was not found, so it was left blank.`) is hardcoded English in the server, and row-error codes (`required`, `phone_my`...) are untranslated keys in both languages: record both as known i18n gaps, not test failures. Step 4: hub in BM ("Pindah data ke Kelasapp", "Mula di sini. Kelas memerlukan guru.", "N sedia ada"). No raw keys like `Import.title` anywhere.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## O. Security

### TC-IMP-051: Script payloads in CSV cells render escaped, never execute
**Tags**: @security @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Risk**: R-imp-xss **Type**: Feature
**Before you start**: Operator on `/dashboard/students/import`.
**Test Data**: one row under `Name,Level`: name `<script>alert(1)</script>`, level `<img src=x onerror=alert(2)>`.
| Step | Action |
|------|--------|
| 1 | Upload the file and look at the preview table |
| 2 | Import, then open the Students list and the new student's detail |
**What you should see**: No alert pops anywhere: not in the preview, not in the list, not on the detail page. Both values render as literal escaped text.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-IMP-052: Spreadsheet formula payloads stay inert through import AND re-export
**Tags**: @security @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Risk**: R-imp-formula-injection **Type**: Feature
**Before you start**: Operator on `/dashboard/students/import`. You will need a spreadsheet app (Excel or LibreOffice) for step 3.
**Test Data**: two rows under `Name`: `=SUM(A1:A9)` and `+HYPERLINK("http://evil.example","klik")`.
| Step | Action |
|------|--------|
| 1 | Upload and import (both are valid strings, so they import) |
| 2 | Confirm both names display as literal text in the Students list |
| 3 | On the Students list, use "Export CSV" and open the downloaded file in the spreadsheet app |
**What you should see**: Step 2: literal text in the app. Step 3: the exported cells appear as inert text prefixed with a `'` (Excel's literal-text marker), NOT evaluated as a formula or clickable hyperlink. Normal cells (numbers, RM money, the "-" placeholder) carry no prefix. REGRESSION: the old `csvEscape` did not neutralise leading formula characters; fixed in 421bbac (2026-07-04) via the shared unit-tested `csvCell` in `src/utils/Csv.ts`, used by both the list-table export and the report CSV. A spreadsheet evaluating an exported cell is a regression of that fix.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## P. Accessibility

### TC-IMP-053: The wizard is operable by keyboard and the file controls are labelled
**Tags**: @regression @a11y **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on `/dashboard/students/import` with a small valid CSV ready. Use only the keyboard.
| Step | Action |
|------|--------|
| 1 | Tab to "Download template" and then "Choose CSV file"; press Enter on the latter and pick the file via the OS dialog |
| 2 | Tab through the mapping dropdowns; open one with Enter/Space and change it with the arrow keys |
| 3 | Tab to "Import N rows" and activate it with Enter |
| 4 | With a file chosen, inspect the clear (x) control next to the file name |
**What you should see**: Every control is reachable and operable by keyboard in reading order (the upload, mapping and review sections are numbered headings on one page, no focus trap). "Choose CSV file" is a real button that opens the file dialog (the native input is hidden but triggered). The clear control has an accessible name "Remove" (BM: "Buang") via aria-label. Focus is visible on each stop.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## Coverage note

Techniques walked across the five import kinds (students, teachers, guardians, classes, enrolments), the wizard steps, the API, and the migration hub:
- **Happy path (per kind):** IMP-016 (students), IMP-019 (teachers), IMP-021 (guardians), IMP-022 (classes), IMP-031 (enrolments); entry points + templates IMP-001/002/003; hub IMP-048.
- **Equivalence + boundary:** header-only / empty / blank rows (IMP-004/005/007), 2000-row cap (IMP-008, IMP-043c), name length 120/121 (IMP-018), bank digits 5-20 (IMP-020), duration 1-600 + capacity 1-500 (IMP-029), fee > RM 1,000,000 server-side (IMP-030), preview capped at 5 rows / 8 errors (IMP-013/014).
- **Negative / validation + server-side bypass:** per-field row errors (IMP-017/025/027/028/029/030/034), non-CSV file (IMP-006), API re-validation (IMP-042), malformed payloads incl. unknown entity / non-string cells / bad JSON (IMP-043).
- **Format / locale:** tolerant time parsing 12h + Malay words (IMP-023, REGRESSION ac1926b), BM day names + separators (IMP-026), BM enum labels + defaults (IMP-028), BM headers auto-map (IMP-010), money format rules (IMP-030/034), `YYYY-MM-DD` CSV date vs DD/MM/YYYY display (IMP-032/034), full BM UI walk (IMP-050).
- **Permissions / role:** teacher blocked from pages (IMP-045) and API (IMP-041); no-org redirect/401 (IMP-044).
- **Cross-tenant / IDOR:** name resolution scoped to the caller's org + imported rows land in caller's org only (IMP-046); hub counts scoped (IMP-047). (The import payload carries no IDs, only names, so classic URL/body IDOR does not apply; the name-resolution cases are the equivalent surface.)
- **State transition:** the import itself has no persisted lifecycle; its nearest equivalents are walked as re-run and partial-failure behaviour: unmatched refs fail vs warn (IMP-024/035), ambiguous names (IMP-036), in-file duplicates (IMP-037), counts reconcile (IMP-040).
- **Concurrency / idempotency:** double-submit blocked by the busy state (IMP-040 step 2), re-run enrolments file = no duplicates (IMP-038, T1), re-run people file = duplicates by design, documented (IMP-039), duplicate enrolment inside one file (IMP-037). True parallel double-POST load testing is out of scope for the manual catalog.
- **Empty / loading / error states:** empty and header-only files (IMP-004/005), parse error string (IMP-005/006), "Importing..." busy state (IMP-016/040), disabled import at 0 valid rows (IMP-015), API failure surface "Import failed. Please try again." (IMP-008).
- **Data integrity:** row error report with true spreadsheet row numbers and no silent drops (IMP-014, and IMP-024 REGRESSION ac1926b), imported enrolment fee links: blank override = class fee, override drives billing (IMP-032/033, T1), summary reconciliation imported + skipped = rows (IMP-040), duplicate-enrolment guard protects billing (IMP-037/038).
- **Accessibility:** keyboard walk + labelled file controls (IMP-053); deeper axe/contrast sweeps stay in `test-plan-crosscutting.md`.
- **Security:** XSS via CSV cells (IMP-051), spreadsheet formula injection incl. the re-export leg (IMP-052, likely finding: `csvEscape` does not neutralise leading formula characters), role + bypass + payload hardening (IMP-041/042/043).
- **Non-functional (row 13):** skipped; no perf SLA is defined for import. The only scale guard, the 2000-row cap, is covered as a boundary (IMP-008). A large-file timing pass can be added post-beta if centres hit it.

Also skipped with reason: SQLi payload cases (all queries go through Drizzle parameterised builders and the same create fns as manual forms, whose SQLi coverage lives in the per-module plans); guardian-student linking via import (not built: slice 1 imports plain fields only, per the note in `config.ts`; IMP-021 documents the limitation); the EN pluralisation fix that rode along in ac1926b (`students_count`) belongs to the Attendance module, not import.

Known verification gaps (behaviour written from code, not a live run): exact Papa.parse outcome for 0-byte/binary files (IMP-005/006 accept either graceful outcome); malformed-JSON body likely 500s today (IMP-043d expects 4xx and says to file the bug); the export leg of IMP-052 is expected to fail today; server warning sentences are hardcoded English (recorded as an i18n gap in IMP-050, not a failure).

Total cases: 53 (entry/templates 3, upload boundaries 5, mapping 4, preview/errors 3, students 3, teachers 2, guardians 1, classes 9, enrolments 7, idempotency/summary 3, API 4, permissions/tenant 3, hub 2, i18n 1, security 2, a11y 1).
Smoke subset (8): TC-IMP-014, TC-IMP-016, TC-IMP-019, TC-IMP-021, TC-IMP-022, TC-IMP-031, TC-IMP-033, TC-IMP-048.
