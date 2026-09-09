# Test plan: Classes & Taxonomy (M1)

> Exhaustive manual catalog for class groups + their org-managed taxonomy (programs / levels).
> Format + method: [QA-METHODOLOGY.md](QA-METHODOLOGY.md). Style/depth matched to
> [test-plan-billing.md](test-plan-billing.md).
> Grounded in `src/features/classes/{schema,service,service.test}.ts`, `ClassForm.tsx`,
> `ClassesTable.tsx`, `ClassActions.tsx`, `classes/[id]/page.tsx`, `classes/[id]/edit/page.tsx`,
> the shared table suite (`src/features/ui/DataTable.tsx` + `data-table/{toolbar,pagination}.tsx`,
> `RowActions.tsx`, `statusTones.ts`), the taxonomy feature
> (`src/features/taxonomy/{schema,service,service.test}.ts`, `TaxonomyManager.tsx`), the four API
> routes (`/api/classes`, `/api/classes/[id]`, `/api/taxonomy/[kind]`, `/api/taxonomy/[kind]/[id]`),
> the shared validators (`src/utils/validators.ts`), `src/utils/Format.ts`, `src/libs/Access.ts`,
> the teacher self-service page (`dashboard/my-classes/page.tsx`), and [FLOWS.md](../FLOWS.md) §1.
>
> **Updated 2026-07-04** against the post-catalog commits: 55f4251 (single Class size field, 12-hour
> times, teacher-rate dash fix, owner-only payment settings), 746df0b + df2e3f1 (table usability
> pass), a9737aa (shared status tones), 6e45620 (success toasts), 31777bd (action failures
> surfaced), 8ecc138 (phone-width layout), 63c3365 (onboarding deep-link), b691bbc (RM 0 fee
> warning), and the Better Auth migration (Jul 2, replaced Clerk) + b175d3e (teacher my-classes).
>
> Default tier **T2** (config). Exception: fee, teacher rate, and pay model feed money downstream
> (billing + payroll freeze these values), so those cases are **T1**. Tenant isolation is **T1**
> everywhere (100-org SaaS). Roles: operator (owner) + staff manage classes
> (`requireOperatorContext`); a teacher has NO management access, only the read-only
> `/dashboard/my-classes` self-service list (TC-CLS-150); no public surface for this module.
>
> Smoke subset (@smoke, 9): TC-CLS-001, TC-CLS-020, TC-CLS-040, TC-CLS-070, TC-CLS-090, TC-CLS-100,
> TC-CLS-113, TC-TAX-001, TC-TAX-020.

---

## Conventions for this catalog

- **Dev logins** (Better Auth email + password at `/sign-in`): operator
  `operator@kelastest.local` / `newpassword6789`; teacher `teacher@kelastest.local` /
  `password12345`.
- **How to find a class id**: open Classes, click a class name, read the id in the URL
  (`/dashboard/classes/<id>`). Never hardcode an id.
- **Money on screen**: rendered via `formatMoney(..., 'MYR', locale)` -> shows the **RM** symbol
  (e.g. `RM120.00`), never `MYR`. Fee + teacher rate are stored as 2dp strings (`"120.00"`).
- **Validation messages are bilingual**: the field stores an i18n key; the form translates it. EN
  + BM strings are named per case from `Validation` in `en.json` / `ms.json`.
- **Schedule on screen**: 12-hour with uppercase AM/PM (`formatTime`, since 55f4251):
  `<dshort_day> <h:mm AM/PM>, ... · <minutes> min` e.g. `Mon 8:00 PM, Wed 5:00 PM · 90 min`.
  The form's TimePicker is three selects: hour 01-12, minutes in 5-minute steps, AM/PM. The value
  is stored as 24-hour `HH:mm`.
- **Capacity**: a SINGLE number (max students). Form field `Class size (max students)`; the list
  `Capacity` column and the detail card show e.g. `30`. The old min-max range is gone (55f4251).
- **Server-side enforcement**: the form (`zodResolver(classInputSchema)`) and the API
  (`classInputSchema.safeParse`) validate with the SAME schema. A bad payload sent straight to the
  API returns **422** `{ error: "Invalid input", issues }`. Bad input never reaches the DB.
- **Out of scope here**: the `Import` menu on the Classes list header (`Import classes` /
  `Import enrollments`, the CSV migration hub) is covered by `test-plan-import.md`, not this file.

---

## A. Create a class (happy path + field-by-field)

### TC-CLS-001: Create a class with the minimum required fields lands it on the active list
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Type**: Feature
**Before you start**: Log in as operator (`operator@kelastest.local` / `newpassword6789`). Go to Classes, click Add class (`/dashboard/classes/new`).
**Test Data**: name `Kelas Mengaji Asas`; type Small group; mode Physical; class size 30; monthly fee 120; pay model Per session (flat); rate 30; schedule one day Monday 8:00 PM; duration 60; notes blank.
| Step | Action |
|------|--------|
| 1 | Type the class name |
| 2 | Leave Program, Level, Teacher unset; keep type/mode defaults |
| 3 | Keep Class size 30, set the monthly fee 120 |
| 4 | Keep pay model Per session, set the rate 30 |
| 5 | Keep the single Monday 08:00 PM slot, duration 60 |
| 6 | Click Add class |
**What you should see**: A success toast `Class saved` (BM `Kelas disimpan`); redirect to `/dashboard/classes`; the new class appears at the TOP of the list (newest first); name is a link; status badge Active; fee column shows `RM120.00`; Capacity column `30`; schedule `Mon 8:00 PM · 60 min` (12-hour, never `20:00`).
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-CLS-002: Create a fully-specified class persists program, level, teacher, per-day schedule
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator with at least one program, one level, and one teacher already set up (see TC-TAX-001 and Teachers module). New class form open.
**Test Data**: name `Quran Asas Petang`; program (pick the existing one); level (pick the existing one); teacher (pick the existing one); type Large group; mode Hybrid; class size 25; fee 150.50; pay model Per student attended; rate 8.00; two slots Mon 8:00 PM and Wed 5:00 PM; duration 90.
| Step | Action |
|------|--------|
| 1 | Fill name, pick program, level, teacher |
| 2 | Set type Large group, mode Hybrid, class size 25, fee 150.50 |
| 3 | Set pay model Per student attended, rate 8.00 |
| 4 | Click Add day; set slot 1 Mon 08:00 PM, slot 2 Wed 05:00 PM; duration 90 |
| 5 | Click Add class, then open the class detail page |
**What you should see**: Detail card shows the teacher as a LINK to that teacher; Type Large group; Mode Hybrid; Capacity `25`; Fee `RM150.50`; Teacher rate `RM8.00`; Schedule `Mon 8:00 PM, Wed 5:00 PM · 90 min`. List row shows the program + level names.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-003: Type and Mode are independent (mode is not a class type)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator on the new class form.
| Step | Action |
|------|--------|
| 1 | Open the Type dropdown; note the options |
| 2 | Open the Mode dropdown; note the options |
**What you should see**: Type offers Individual / Small group / Large group / Family ONLY. Mode offers Online / Physical / Hybrid ONLY. Online/Physical/Hybrid never appear as a Type.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-004: Decimal monthly fee is accepted and stored to 2dp
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator on the new class form (feeds billing line amounts).
**Test Data**: monthly fee 99.9 (one decimal).
| Step | Action |
|------|--------|
| 1 | Fill the required fields, set monthly fee 99.9 |
| 2 | Save and open the detail page |
**What you should see**: Fee shows `RM99.90` (normalised to 2dp). The list fee column matches.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## B. Required-field validation

### TC-CLS-010: Empty name is hard-blocked with a bilingual required message
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on the new class form.
| Step | Action |
|------|--------|
| 1 | Leave the class name blank (or type spaces only) |
| 2 | Fill the other required fields, click Add class |
| 3 | Switch the app language to BM and repeat |
**What you should see**: Blocked under the name field. EN: `This field is required.` BM: `Medan ini wajib diisi.` (`required`). Whitespace-only is also rejected (name is trimmed). No redirect, nothing created.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-011: Name over 120 characters is rejected
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator on the new class form.
**Test Data**: a name of 121 characters (e.g. paste "A" x 121).
| Step | Action |
|------|--------|
| 1 | Paste the 121-character name, fill the rest, click Add class |
| 2 | Reduce to exactly 120 characters and save |
**What you should see**: 121 chars blocked (max 120); 120 chars saves successfully. Boundary: 120 = pass, 121 = fail.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-012: Server rejects an empty name even if the UI is bypassed
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: API
**Before you start**: Operator session (copy your auth cookie or use the browser network tab). POST `/api/classes`.
**Test Data**: a valid body but with `"name": ""`.
| Step | Action |
|------|--------|
| 1 | POST `/api/classes` with name empty and all else valid |
**What you should see**: HTTP **422**, body `{ "error": "Invalid input", "issues": ... }` with a `name` issue. No class row created (re-open Classes to confirm).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## C. Class size boundaries

> Class size became a SINGLE field (max students, `capacityMax`) in 55f4251: the unused
> min-capacity field and its `capacity_order` refine were removed, which also removed the
> backwards-range gap flagged as catalog finding #2 (TC-CLS-083). The DB `capacity_min` column
> remains (default 1) but no UI or schema reads it.

### TC-CLS-020: Class size is one single field; the old minimum-capacity input is gone
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on the new class form.
| Step | Action |
|------|--------|
| 1 | Scan the whole form for capacity inputs |
| 2 | Read the class-size label and the hint beneath it |
**What you should see**: Exactly ONE capacity input: label `Class size (max students)` (`class_size`), hint `The maximum number of students in this class.` (`class_size_hint`). BM: `Saiz kelas (maks pelajar)` / `Bilangan maksimum pelajar dalam kelas ini.` No separate minimum field anywhere, so a backwards min>max range can no longer be entered.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: catalog finding #2 (update schema allowed max below min) resolved by removing the min field, commit 55f4251.

### TC-CLS-021: Class size 1 is allowed (individual class)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator on the new class form.
**Test Data**: class size 1.
| Step | Action |
|------|--------|
| 1 | Set Class size 1, fill the rest, save |
**What you should see**: Saved (`min(1)` boundary is inclusive). Detail card Capacity shows `1`.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-022: Class size 0 is rejected (minimum is 1)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator on the new class form.
**Test Data**: class size 0.
| Step | Action |
|------|--------|
| 1 | Set Class size 0, fill the rest, try to save |
**What you should see**: Blocked under the Class size field: capacity must be an integer 1-500 (`min(1)`); no class created. Boundary: 0 = fail, 1 = pass (TC-CLS-021).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-023: Class size above 500 is rejected; 500 is the accepted maximum
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator on the new class form.
**Test Data**: class size 501, then 500.
| Step | Action |
|------|--------|
| 1 | Set Class size 501, try to save |
| 2 | Set Class size 500 and save |
**What you should see**: 501 rejected (`max(500)`); 500 saved. Boundary: 500 = pass, 501 = fail.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-024: Non-integer / negative class size is rejected (server-side too)
**Tags**: @regression @security **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: API
**Before you start**: Operator. POST `/api/classes`.
**Test Data**: `"capacityMax": 2.5`, then `"capacityMax": -1`.
| Step | Action |
|------|--------|
| 1 | POST a body with `capacityMax` = 2.5 |
| 2 | POST a body with `capacityMax` = -1 |
**What you should see**: Both **422** (`int().min(1)`); no class created. The UI number field also blocks letters.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## D. Fee / rate validation (money -> T1)

### TC-CLS-030: Negative monthly fee is rejected
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator on the new class form (fee drives billing line amounts).
**Test Data**: monthly fee -50.
| Step | Action |
|------|--------|
| 1 | Set monthly fee -50, fill the rest, try to save |
**What you should see**: Blocked under the fee field (`money()` is `nonnegative()`). No class created. No negative fee can reach billing.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-031: Monthly fee zero is allowed (free class) but shows a non-blocking warning
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on the new class form.
**Test Data**: monthly fee 0.
| Step | Action |
|------|--------|
| 1 | Set monthly fee 0 and read the text under the fee field |
| 2 | Fill the rest, save and open detail |
**What you should see**: While the fee is 0, a warning renders under the field: `Fee is RM 0 - this class will generate free invoices. Make sure that is intentional.` (`monthly_fee_zero_warn`, added in b691bbc). It does NOT block: the class still saves; detail fee shows `RM0.00` (zero is nonnegative, so a free class is valid). Live warning behaviour is covered in TC-CLS-148.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-032: Monthly fee with more than 2 decimals is rejected
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator on the new class form.
**Test Data**: monthly fee 99.999.
| Step | Action |
|------|--------|
| 1 | Set monthly fee 99.999, try to save |
| 2 | Switch to BM and repeat |
**What you should see**: Blocked under the fee field. EN: `Use at most 2 decimal places.` BM: `Guna paling banyak 2 tempat perpuluhan.` (`amount_decimals`). No class created.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-033: Teacher rate negative / >2dp is rejected; zero is allowed
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator on the new class form (rate is frozen onto sessions for payroll).
**Test Data**: rate -1, then 10.001, then 0.
| Step | Action |
|------|--------|
| 1 | Set the rate -1, try to save |
| 2 | Set the rate 10.001, try to save |
| 3 | Set the rate 0 and save |
**What you should see**: -1 blocked (`nonnegative`); 10.001 blocked (`Use at most 2 decimal places.` / `Guna paling banyak 2 tempat perpuluhan.`); 0 saved (a rate of `RM0.00` is valid; the detail card now shows `RM0.00` for a saved zero, see TC-CLS-035).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-034: Fee above the 1,000,000 cap is rejected (server-side)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: API
**Before you start**: Operator. POST `/api/classes`.
**Test Data**: `"monthlyFee": 1000001`.
| Step | Action |
|------|--------|
| 1 | POST a valid body with monthlyFee = 1000001 |
| 2 | POST with monthlyFee = 1000000 |
**What you should see**: 1000001 -> **422** (`money()` max 1,000,000); 1000000 accepted. Boundary at the cap.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-035: A saved zero teacher rate shows RM0.00 on the detail card, not a dash
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator; create a class with rate 0 (TC-CLS-033 step 3), open its detail page.
| Step | Action |
|------|--------|
| 1 | Read the Teacher rate field on the detail card |
**What you should see**: Teacher rate shows `RM0.00`. The dash `-` is reserved for a genuinely UNSET rate (a null DB value on legacy rows; the detail check is now `!= null`, not falsy). The fee field still shows its RM value.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: catalog finding #5 (zero rate rendered as a dash via a falsy check) fixed in commit 55f4251.

## E. Pay model selector (label adapts): money -> T1

### TC-CLS-040: Selecting Per session shows the per-session rate label and hint
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator on the new class form. The default pay model is Per session.
| Step | Action |
|------|--------|
| 1 | Confirm pay model is Per session (flat) |
| 2 | Read the rate field label and the hint beneath it |
**What you should see**: Label `Rate per session (RM)` (`rate_per_session`); hint `What the teacher earns per session.` (`teacher_rate_hint`). The pay-model hint reads `Per session pays a flat rate for teaching the class. Per student pays the rate for each student who attends.`
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-041: Switching to Per student attended changes the rate label live (no reload)
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator on the new class form.
| Step | Action |
|------|--------|
| 1 | Change pay model from Per session to Per student attended |
| 2 | Watch the rate field label and hint |
**What you should see**: WITHOUT a page reload (`form.watch('payModel')`), the rate label switches to `Rate per student (RM)` (`rate_per_student`); the hint switches to `Paid for each student who attends a session.` (`rate_per_student_hint`).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-042: Pay model options are exactly the two supported values
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on the new class form.
| Step | Action |
|------|--------|
| 1 | Open the pay model dropdown |
**What you should see**: Exactly two options: `Per session (flat)` (`pay_per_session`) and `Per student attended` (`pay_per_student`). No third option.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-043: Pay model + rate persist on the chosen model
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator on the new class form (the saved pay model + rate are what payroll freezes per session).
**Test Data**: pay model Per student attended; rate 8.50.
| Step | Action |
|------|--------|
| 1 | Set pay model Per student attended, rate 8.50, fill the rest, save |
| 2 | Open Edit for the class |
**What you should see**: Edit form pre-selects Per student attended; rate field reads 8.50; rate label is `Rate per student (RM)`. The stored model is per_student, not per_session.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## F. Schedule

### TC-CLS-050: Removing all schedule rows / saving with no day is blocked
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on the new class form. The form starts with one Monday slot and the Remove button is hidden when only one slot remains.
| Step | Action |
|------|--------|
| 1 | Note you cannot remove the last slot via the UI (Remove hidden when one row left) |
| 2 | To prove the rule, POST `/api/classes` with `schedule.slots = []` |
| 3 | Switch to BM and check the message wording |
**What you should see**: API returns **422** (`slots.min(1)`); the bilingual message key is `schedule_min` -> EN `Add at least one day.` BM `Tambah sekurang-kurangnya satu hari.` No class created.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-051: Multiple per-day slots with different times are saved per slot
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on the new class form.
**Test Data**: slot 1 Mon 08:00 PM; slot 2 Wed 05:00 PM; slot 3 Sat 09:30 AM; duration 90.
| Step | Action |
|------|--------|
| 1 | Click Add day twice to get three rows |
| 2 | Set Mon 08:00 PM, Wed 05:00 PM, Sat 09:30 AM on the hour/minute/AM-PM selects, duration 90 |
| 3 | Save and open the detail page |
**What you should see**: Schedule renders `Mon 8:00 PM, Wed 5:00 PM, Sat 9:30 AM · 90 min` (each day keeps its own time; this is the per-day-times decision; display is 12-hour since 55f4251).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-052: Invalid schedule time is rejected with the 24-hour message
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: API
**Before you start**: Operator. POST `/api/classes` (the TimePicker's hour/minute/AM-PM selects constrain UI input, so prove the rule via API).
**Test Data**: `time` = `25:00`, then `8:00` (missing leading zero), then `20:60`.
| Step | Action |
|------|--------|
| 1 | POST with a slot time `25:00` |
| 2 | POST with a slot time `8:00` |
| 3 | POST with a slot time `20:60` |
**What you should see**: All three **422** (regex `^([01]\d|2[0-3]):[0-5]\d$`, key `time_hhmm`). Bilingual: EN `Use 24-hour time, e.g. 20:00.` BM `Guna masa 24 jam, cth. 20:00.` No class created.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-053: Valid boundary times are accepted
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: API
**Before you start**: Operator. POST `/api/classes`.
**Test Data**: times `00:00` and `23:59`.
| Step | Action |
|------|--------|
| 1 | POST one class with a slot at `00:00` |
| 2 | POST another with a slot at `23:59` |
**What you should see**: Both accepted (201). The regex bounds are inclusive at 00:00 and 23:59.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-054: Duration must be a positive integer at most 600 minutes
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: API
**Before you start**: Operator. POST `/api/classes`.
**Test Data**: duration 0, then -30, then 601, then 600, then 90.5.
| Step | Action |
|------|--------|
| 1 | POST with durationMinutes 0 |
| 2 | POST with durationMinutes -30 |
| 3 | POST with durationMinutes 601 |
| 4 | POST with durationMinutes 600 |
| 5 | POST with durationMinutes 90.5 |
**What you should see**: 0, -30, 601, 90.5 all **422** (`int().positive().max(600)`); 600 accepted. Boundary: 600 = pass, 601 = fail; non-integer 90.5 = fail.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-055: Add day then Remove day adjusts the slot list
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator on the new class form (starts with one slot).
| Step | Action |
|------|--------|
| 1 | Click Add day twice (now three rows; Remove now visible on each) |
| 2 | Click Remove on the middle row |
| 3 | Reduce to one row |
**What you should see**: Add day appends a row defaulting to `Mon` at `08 : 00 PM`; Remove deletes that row; once only one row remains, the Remove button disappears (cannot remove the last slot in the UI).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## G. Program / Level optional + empty-state hint

### TC-CLS-060: Program and Level are optional; a class saves uncategorised
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on the new class form with at least one program and one level set up.
| Step | Action |
|------|--------|
| 1 | Leave Program on `None` and Level on `None` |
| 2 | Fill the required fields and save |
| 3 | Open Classes and find the row |
**What you should see**: Saved. Both fields carry the `(optional)` marker. In the list, the Program and Level cells show `-` (null mapped to `-`).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-061: Empty taxonomy shows a Setup hint instead of a dropdown
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator in an org with NO programs and NO levels yet. Open the new class form.
| Step | Action |
|------|--------|
| 1 | Look at the Program field |
| 2 | Look at the Level field |
| 3 | Click the Program hint link |
**What you should see**: Program shows `No programs yet.` + a `Add programs in Setup →` link to `/dashboard/setup/programs`. Level shows `No levels yet.` + `Add levels in Setup →` to `/dashboard/setup/levels`. No empty dropdown is rendered. The link navigates to the Setup page.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-062: Empty teacher list shows an add-teacher hint
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator in an org with NO teachers yet. New class form open.
| Step | Action |
|------|--------|
| 1 | Look at the Teacher field |
| 2 | Click the hint link |
**What you should see**: Teacher shows `No teachers yet.` + `Add a teacher →` link to `/dashboard/teachers/new`. No empty teacher dropdown.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-063: List Program/Level filters appear only when taxonomy exists
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator with at least one program and several classes (some with a program, some `None`). Open Classes.
| Step | Action |
|------|--------|
| 1 | Open the Program faceted filter in the table toolbar, tick the existing program |
| 2 | Click the `Reset` button that appears next to the filters |
**What you should see**: The Program filter exists (taxonomy non-empty); ticking it narrows the table to rows with that program name; classes with no program drop out; `Reset` (with an X icon) restores all rows and disappears again. (If an org has zero programs, the Program filter chip is absent.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## H. Teacher assignment

### TC-CLS-070: Assign a teacher; detail page links to that teacher
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator with one teacher (note the teacher's name). New class form open.
| Step | Action |
|------|--------|
| 1 | Pick the teacher in the Teacher dropdown, fill the rest, save |
| 2 | Open the class detail page |
| 3 | Click the teacher name on the detail card |
**What you should see**: Detail Teacher field shows the teacher's name as a LINK to `/dashboard/teachers/<teacherId>`; the list Teacher column shows the same name. Clicking it opens that teacher's profile. (Service stores one `class_teachers` row, `isPrimary=true`.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-071: Reassign the teacher replaces the previous one
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator; a class assigned to teacher A; a second teacher B exists.
| Step | Action |
|------|--------|
| 1 | Open the class Edit page |
| 2 | Change the teacher to B, Save changes |
| 3 | Open the class detail page |
**What you should see**: Detail Teacher now shows B (links to B). A is no longer the assigned teacher (the old `class_teachers` row was deleted and replaced, so `getClassTeacherId` returns B). No duplicate assignment.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-072: Unassign the teacher leaves the class unassigned
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator; a class with a teacher assigned.
| Step | Action |
|------|--------|
| 1 | Open Edit, set the Teacher dropdown to Unassigned |
| 2 | Save changes, open the detail page |
**What you should see**: Detail Teacher shows `Unassigned` (`unassigned`, BM `Belum ditugaskan`) in muted text (no link); the list Teacher column shows `-`. (`getClassTeacherId` returns null.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-073: Assigning a teacher from another org is silently ignored (tenant guard)
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: API
**Before you start**: Operator of org B. Obtain a teacher id that belongs to org A (from a known fixture or another session). This mirrors the service test "refuses to assign a teacher from another org".
| Step | Action |
|------|--------|
| 1 | As org B, create a class via the form/API with `teacherId` = org A's teacher id |
| 2 | Open the new class detail page (or call `getClassTeacherId`) |
**What you should see**: The class is created (request succeeds), but the foreign teacher is NOT assigned: Teacher shows `Unassigned`; `getClassTeacherId` is null. No error leaks the foreign teacher's existence; org A's teacher never appears on org B's class.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## I. Edit

### TC-CLS-080: Edit form is prefilled from the saved class
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator; an existing class with program, level, teacher, two schedule slots, notes. Open its Edit page.
| Step | Action |
|------|--------|
| 1 | Read every field on the Edit form |
**What you should see**: Title `Edit class`; subtitle `Editing "<class name>"` (`editing`). Name, program, level, teacher, type, mode, class size, fee (as a number, e.g. 150.5), pay model + rate, both schedule slots (hour/minute/AM-PM selects showing the saved times), duration, and notes are all prefilled to match the saved class. Submit button reads `Save changes` (`save_changes`).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-081: Edit a field updates the class and returns to the list
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator; an existing class (note its current fee).
**Test Data**: change monthly fee to 200.00 and rename to `Quran Asas Pagi`.
| Step | Action |
|------|--------|
| 1 | Open Edit, change the name and fee, Save changes |
| 2 | Open the class detail page |
**What you should see**: A success toast `Class saved` (`saved_toast`); redirect to Classes; the row shows the new name and `RM200.00`; detail page confirms both. The class id is unchanged (no duplicate).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-082: Editing the pay model/rate affects future sessions only (frozen-pay rule)
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator; a class whose teacher already taught a marked session (frozen pay exists). Note the existing session's pay in Teacher pay. (Cross-references payroll; verify the value does not change.)
| Step | Action |
|------|--------|
| 1 | Open Edit, change the teacher rate to a new value, Save changes |
| 2 | Re-open Teacher pay and look at the already-taught session line |
**What you should see**: The already-marked session keeps its ORIGINAL frozen pay (unchanged); only sessions marked AFTER the edit use the new rate. The rate edit does not retroactively rewrite past pay.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-083: Edit validation matches create (class size bounds enforced on update)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: API
**Before you start**: Operator on a class Edit page; have the class id for the API steps.
**Test Data**: class size 0, then 501; PATCH body with a stray `"capacityMin": 400`.
| Step | Action |
|------|--------|
| 1 | On Edit, set Class size 0, click Save changes |
| 2 | Set Class size 501, click Save changes |
| 3 | PATCH `/api/classes/<id>` with `{ "capacityMin": 400 }` |
**What you should see**: 0 and 501 are blocked under the Class size field, same bounds as create (`classUpdateSchema` `capacityMax` is `int().min(1).max(500).optional()`). The PATCH with only the removed `capacityMin` key succeeds as a no-op (unknown keys are stripped; the field no longer exists in the schema) and the class is unchanged.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: this case previously documented finding #2 (update schema skipped the `capacity_order` refine). The min/max pair itself was removed in commit 55f4251, closing the gap.

## J. Archive

### TC-CLS-090: Archive a class removes it from the active list, keeps it in archive
**Tags**: @smoke @regression @data-integrity **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator; an active class with NO current enrolments (end any Active/Paused enrolments first, or use a freshly created class): since 667eecb archiving is refused while students are enrolled (see TC-CLS-151).
| Step | Action |
|------|--------|
| 1 | On Classes, open the row kebab, click Archive |
| 2 | Confirm in the dialog `Archive this class?` |
| 3 | Re-scan the active Classes list |
**What you should see**: Confirm dialog title `Archive this class?` (`archive_title`), body `The class will be moved to your archive and no longer appear in the active list...` (`archive_desc`); the confirm button reads `Archive` and shows `Archiving...` while busy. After confirm, a success toast `Class archived` (`archived_toast`, BM `Kelas diarkibkan`) appears and the class disappears from the active list (`listClasses` filters `ne(status, 'archived')`). It is NOT deleted (`updateClass status: 'archived'`, soft-delete).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-091: Archived class is excluded from the operator dashboard class-health grid
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator; an active class that appears in the dashboard Class health grid, with at least one active enrolment. Note it is listed.
| Step | Action |
|------|--------|
| 1 | Archive that class (TC-CLS-090) |
| 2 | Open the operator Dashboard and read the Class health section |
**What you should see**: The archived class no longer appears in Class health (`getClassHealth` filters `eq(classes.status, 'active')`). Active classes still appear.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-092: Archive via the detail/edit path and via the list kebab both work
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator; two active classes.
| Step | Action |
|------|--------|
| 1 | Archive one via the list-row kebab Archive |
| 2 | Archive the other by DELETE `/api/classes/<id>` |
| 3 | Re-scan the active list |
**What you should see**: Both leave the active list. DELETE returns the archived row `{ data }` (status archived), not a hard delete. A second DELETE on the same id still returns the row (idempotent archive: it stays archived).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-093: DELETE a non-existent / wrong-org class id returns Not found
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T1 | **Type**: API
**Before you start**: Operator. Have a made-up UUID and (optionally) an org A class id while authed as org B.
| Step | Action |
|------|--------|
| 1 | DELETE `/api/classes/<random-uuid>` |
| 2 | DELETE `/api/classes/<org-A-class-id>` while authed as org B |
**What you should see**: Both return HTTP **404** `{ "error": "Not found" }` (`archiveClass` returns undefined when not theirs). No org A class is archived.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## K. List / empty / detail display

### TC-CLS-100: Empty Classes list shows the rich empty state with a create CTA
**Tags**: @smoke @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator in a brand-new org with no classes. Open Classes.
| Step | Action |
|------|--------|
| 1 | Read the table body |
| 2 | Click the Add class button inside the empty state |
**What you should see**: A rich empty state (book icon) with title `No classes yet` (`empty_title`, BM `Tiada kelas lagi`) and description `Create your first class to set a schedule and fee, then enrol students.` (`empty_desc`, BM `Cipta kelas pertama anda untuk menetapkan jadual dan yuran, kemudian daftarkan pelajar.`); NOT a blank table. Its `Add class` button opens `/dashboard/classes/new`. (A search/filter that matches nothing shows a different message, TC-CLS-141.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-101: Classes are listed newest first
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator; create class X, then class Y a moment later.
| Step | Action |
|------|--------|
| 1 | Open Classes and read the top two rows (before sorting any column) |
**What you should see**: Y (the newer) is above X (`orderBy desc(createdAt)`).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-102: Detail attendance rate shows a dash when nothing is marked
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator; a class with NO attendance marked yet. Open its detail page.
| Step | Action |
|------|--------|
| 1 | Read the Attendance rate (30 days) field |
**What you should see**: Shows `-` when the rate is null (nothing marked). The field label is `Attendance rate (30 days)` / BM `Kadar kehadiran (30 hari)`.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-103: Notes accept a long entry up to 2000 chars; over-limit rejected
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: API
**Before you start**: Operator. POST `/api/classes`.
**Test Data**: notes of 2000 chars, then 2001 chars.
| Step | Action |
|------|--------|
| 1 | POST a class with 2000-char notes |
| 2 | POST a class with 2001-char notes |
**What you should see**: 2000 accepted; 2001 -> **422** (`notes.max(2000)`). Boundary at 2000.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## L. Permissions + tenant isolation (classes)

### TC-CLS-110: Teacher cannot reach the Classes management area
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Log in as the teacher (`teacher@kelastest.local` / `password12345`, a Better Auth member whose org role is teacher, linked to a teachers row).
| Step | Action |
|------|--------|
| 1 | Navigate directly to `/dashboard/classes` |
| 2 | Navigate directly to `/dashboard/classes/new` |
**What you should see**: Redirected to `/dashboard/attendance` (operator route group layout guard, `requireOperator` redirects teachers). No class management UI is shown. The teacher's read-only view of their own classes is `/dashboard/my-classes` (TC-CLS-150), which has no add/edit/archive controls.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-111: Teacher calling a classes API directly is rejected
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: API
**Before you start**: Authenticated as a teacher (use the teacher's session cookie).
| Step | Action |
|------|--------|
| 1 | GET `/api/classes` |
| 2 | POST `/api/classes` with a valid body |
| 3 | PATCH `/api/classes/<any-id>` |
**What you should see**: All return HTTP **401** `{ "error": "Forbidden: operators only" }` (`requireOperatorContext` throws `OrgRequiredError` for a teacher). No class data returned, nothing created/changed.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-112: No org context: classes pages redirect, APIs return 401
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T1 | **Type**: Feature
**Before you start**: A signed-in user with NO active organisation selected.
| Step | Action |
|------|--------|
| 1 | Navigate to `/dashboard/classes` |
| 2 | GET `/api/classes` |
**What you should see**: Page redirects to `/onboarding/organization-selection`; the API returns **401** with the `OrgRequiredError` message. No class data.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-113: Cross-tenant: org B cannot open org A's class detail page
**Tags**: @smoke @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Two orgs A and B. As operator of org A, create a class and copy its id from the URL. Switch to org B (operator).
| Step | Action |
|------|--------|
| 1 | As org B, open `/dashboard/classes/<org-A-class-id>` |
| 2 | As org B, GET `/api/classes/<org-A-class-id>` |
**What you should see**: Page shows Next.js Not found (`getClass` returns undefined -> `notFound()`); API returns **404** `{ "error": "Not found" }`. Org A's class never renders for org B; no data leak.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-114: Cross-tenant: org B cannot edit/archive org A's class
**Tags**: @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: API
**Before you start**: Org A class id known; authed as org B operator.
| Step | Action |
|------|--------|
| 1 | PATCH `/api/classes/<org-A-class-id>` with `{ "name": "Hacked" }` as org B |
| 2 | DELETE `/api/classes/<org-A-class-id>` as org B |
| 3 | Switch back to org A and open the class |
**What you should see**: PATCH and DELETE both return **404** `{ "error": "Not found" }` (the WHERE is scoped `and(eq(id), eq(orgId))`). Back in org A, the class is unchanged (still its original name, still active).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-115: Classes list shows only the current org's classes
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Org A and org B each have at least one class with a distinctive name. Log in as org B operator.
| Step | Action |
|------|--------|
| 1 | Open Classes as org B and scan every row |
**What you should see**: Only org B's classes; none of org A's (mirrors the service test "listClasses returns only the requesting org's classes"). No filter or sort exposes another org's data.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## M. Security (input that reaches render)

### TC-CLS-120: Class name with a script payload is shown escaped, never executed
**Tags**: @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on the new class form.
**Test Data**: name = `<script>alert('xss')</script>`.
| Step | Action |
|------|--------|
| 1 | Save a class with that name |
| 2 | View the class in the list, the detail title, and the Edit subtitle |
**What you should see**: The literal text is shown escaped everywhere it renders (list link, detail TitleBar, `Editing "<...>"`); no alert dialog pops (React escapes by default). No script runs.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-121: Mass-assignment: unknown fields in the create body are ignored
**Tags**: @security @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: API
**Before you start**: Operator. POST `/api/classes`.
**Test Data**: a valid body plus extra keys `"orgId": "org_other"`, `"id": "forced-id"`, `"status": "archived"`.
| Step | Action |
|------|--------|
| 1 | POST the body with the extra keys |
| 2 | Open the created class detail page |
**What you should see**: Class created under the CALLER's org (server sets `orgId` from `requireOperatorContext`, not the body); a fresh server id (not `forced-id`); status Active (create ignores a body status, since `createClass` never reads it). The injected fields have no effect.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## N. i18n (classes)

### TC-CLS-130: All class screens render in BM with RM money and Malay day labels
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator. A class with two schedule slots and a fee. Switch the app language to BM.
| Step | Action |
|------|--------|
| 1 | Open Classes (BM); read title, Add button, column headers |
| 2 | Open the class detail (BM); read field labels and the schedule |
| 3 | Open the new class form (BM); read the pay-model + rate labels |
**What you should see**: BM throughout: title `Kelas`; `Tambah kelas`; columns `Nama / Program / Tahap / Guru / Jenis / Mod / Jadual / Kapasiti / Yuran / Status`. Schedule days use BM short labels `Isn / Sel / Rab / Kha / Jum / Sab / Ahd`, the `min` suffix, and 12-hour times with `AM`/`PM` (e.g. `Isn 8:00 PM`; `formatTime` does not localise the AM/PM marker). Money still shows `RM` (never MYR). Pay model `Bagaimana guru dibayar?`, options `Per sesi (tetap)` / `Per pelajar hadir`. Class size field `Saiz kelas (maks pelajar)`.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## U. List table usability (added 2026-07-04, commits 746df0b + df2e3f1)

### TC-CLS-140: Classes table shows a # column, range-of-total count, and 25 rows per page
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator with at least 3 classes (create them via TC-CLS-001 if needed). Open Classes.
| Step | Action |
|------|--------|
| 1 | Read the first table column header and the first three rows of that column |
| 2 | Read the count at the bottom-left of the table |
| 3 | Read the rows-per-page select and open it |
| 4 | Change rows-per-page to 10, reload the page, and read the select again |
**What you should see**: The leading column is `#` with positional numbers 1, 2, 3 (it renumbers with the current sort/filter/page, Excel-style). The footer shows `1-<n> of <n>` (`range_of_total`, e.g. `1-3 of 3`; BM `1-3 daripada 3`) next to `Rows per page` (BM `Baris per halaman`) with options 10 / 25 / 50 / 100 and 25 selected by default. The choice survives a reload (stored under localStorage `kelasapp.rows-per-page`).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-141: Search box matches every visible column; no-match state offers Reset
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator with at least two classes, one assigned to a teacher whose name is unique (note it). Open Classes.
**Test Data**: search the teacher's name; then search `zzzznothing`.
| Step | Action |
|------|--------|
| 1 | Type the teacher's name in the toolbar search box (`Search class, program, teacher...`) |
| 2 | Clear it and type `zzzznothing` |
| 3 | Click `Reset` |
**What you should see**: Step 1 keeps only the classes taught by that teacher, proving search is NOT name-only (it matches every visible column, including teacher, program, schedule). Step 2 shows `No matches for your search or filters.` (`no_results_filtered`, BM `Tiada padanan untuk carian atau tapisan anda.`) with a `Reset` button, NOT the new-org empty state (TC-CLS-100). Reset restores all rows.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-142: Export CSV downloads the current filtered view
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator with several classes, at least one with a program set, on a desktop-width window (the button is hidden below the `lg` breakpoint). Open Classes.
| Step | Action |
|------|--------|
| 1 | Filter the table by one program (faceted filter) |
| 2 | Click `Export CSV` in the toolbar |
| 3 | Open the downloaded file in a spreadsheet |
**What you should see**: A file named `classes-<YYYY-MM-DD>.csv` (today's date) downloads. It contains ONLY the filtered rows (all pages, not just the visible page), with a header row of the visible column labels (Name, Program, ...). Malay/diacritic characters open correctly in Excel (the file carries a UTF-8 BOM).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-143: No selection checkboxes on the Classes table
**Tags**: @regression **Severity**: S4 Low | **Priority**: P4 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator with at least one class. Open Classes.
| Step | Action |
|------|--------|
| 1 | Inspect the leading columns of the header and every row |
**What you should see**: No checkbox column anywhere: the row starts with the `#` number, then Name. (Classes has no bulk actions, so a checkbox would select into nothing.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: dead selection checkboxes removed in commit df2e3f1.

## V. Feedback, status tones, responsive (added 2026-07-04)

### TC-CLS-144: Class status badge uses the same tone on the list and the detail card
**Tags**: @regression **Severity**: S4 Low | **Priority**: P4 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator with an active class. Open Classes, then the class detail page.
| Step | Action |
|------|--------|
| 1 | Note the colour and text of the Status badge on the class's list row |
| 2 | Open the class detail page and note the badge in the Details card header |
**What you should see**: Both read `Active` (BM `Aktif`) with the SAME tone (shared `CLASS_TONE` map since a9737aa): active = success tint, paused = amber tint, archived = neutral. No mismatch between list and detail.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-CLS-145: Success toasts fire on class save and archive, in both languages
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator; one existing class to archive. App language EN first.
| Step | Action |
|------|--------|
| 1 | Create a class (TC-CLS-001) and watch the top of the screen after clicking Add class |
| 2 | Edit any class, Save changes, watch again |
| 3 | Archive a class (TC-CLS-090), watch again |
| 4 | Switch the app language to BM and repeat step 2 and 3 with another class |
**What you should see**: Create and edit both show a toast `Class saved` (`saved_toast`); archive shows `Class archived` (`archived_toast`). In BM: `Kelas disimpan` and `Kelas diarkibkan`. Each toast disappears on its own; the action still completes if the toast is missed.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Toasts added in commit 6e45620 (silent saves before that).

### TC-CLS-146: A failed archive keeps the dialog open and shows the failure message
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator with one class, logged in from TWO browser tabs (same account). This forces a server refusal: sign out in tab B, then act in tab A.
| Step | Action |
|------|--------|
| 1 | In tab A, open Classes and open the row kebab, click Archive (leave the confirm dialog open) |
| 2 | In tab B, sign out (this invalidates the session) |
| 3 | Back in tab A, click the `Archive` confirm button |
**What you should see**: The DELETE fails (401), so the dialog STAYS OPEN and shows `That did not work. Please try again.` (`action_failed`, BM `Itu tidak berjaya. Sila cuba lagi.`) in red inside the dialog. No success toast, and the class is still on the list after a reload (and sign-in).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: failures were swallowed silently (dialog closed, nothing happened) before commit 31777bd. Since c679357 (2026-07-04) a TRUE network drop (DevTools offline) is also caught with the same message, so offline mode is a valid alternative to the two-tab sign-out trigger.

### TC-CLS-147: Class form schedule row is fully usable at phone width
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator on the new class form, browser viewport at 375px wide (e.g. DevTools iPhone SE emulation).
| Step | Action |
|------|--------|
| 1 | Click Add day so the form has two schedule rows |
| 2 | On the second row, open the AM/PM select and change it |
| 3 | Click Remove on the second row |
| 4 | Scan the page for horizontal scrolling |
**What you should see**: The schedule row wraps into stacked lines: the day select, all three time selects (hour / minutes / AM-PM), and the Remove button are all visible and tappable without sideways scrolling. The two-column `Day` / `Start time` header row is hidden at this width. No horizontal overflow anywhere on the form.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: at 375px the AM/PM select was clipped off-screen and Remove was unreachable before commit 8ecc138.

### TC-CLS-148: RM 0 fee warning appears and disappears live, on create and edit
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator. Open the new class form; also have one existing class with a non-zero fee.
| Step | Action |
|------|--------|
| 1 | On the fresh form, read under the Monthly fee field before touching it (the default fee is 0) |
| 2 | Type 120 in the fee field and watch the warning |
| 3 | Clear it back to 0 and watch again |
| 4 | Open the existing class's Edit page, set the fee to 0, and read under the field; switch the app language to BM and re-check |
**What you should see**: With the fee at 0 the warning `Fee is RM 0 - this class will generate free invoices. Make sure that is intentional.` (`monthly_fee_zero_warn`) shows under the field, including on the untouched fresh form. It vanishes the moment the fee is non-zero and returns at 0, with no reload. Same behaviour on Edit. BM: `Yuran RM 0 - kelas ini akan menjana invois percuma. Pastikan ia disengajakan.` It never blocks saving (TC-CLS-031).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Warning added in commit b691bbc (warn, never block: RM 0 is legal for sponsored/free classes).

## W. Onboarding deep-link + teacher self-service (added 2026-07-04)

### TC-CLS-149: Creating a class from the onboarding checklist returns to the dashboard
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator in an org that still shows the Getting started checklist on the dashboard (class step not yet ticked).
| Step | Action |
|------|--------|
| 1 | On the dashboard checklist, click the create-a-class step and note the URL |
| 2 | Fill the form and click Add class |
| 3 | Read the checklist again; note where the enrol step now points |
| 4 | Later, open `/dashboard/classes/new` directly (no query string), save another class |
**What you should see**: Step 1 opens `/dashboard/classes/new?from=onboarding`. After saving, you return to `/dashboard` (NOT the classes list) and the class step shows as ticked. The enrol step now deep-links to the FIRST class's detail page `/dashboard/classes/<id>` where the Enroll panel lives (before any class exists it pointed to `/dashboard/classes`). Step 4 (normal entry) still returns to `/dashboard/classes`.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Deep-link + pull-through added in commit 63c3365.

### TC-CLS-150: Teacher sees only their own assigned classes on My classes (read-only)
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator has at least two classes: one assigned to the teacher `teacher@kelastest.local`, one assigned to nobody (or another teacher). Log in as the teacher (`teacher@kelastest.local` / `password12345`).
| Step | Action |
|------|--------|
| 1 | Open `/dashboard/my-classes` (also reachable from the teacher sidebar) |
| 2 | Compare the listed classes against the operator's class list |
| 3 | Look for any add / edit / archive control |
| 4 | As operator, archive the teacher's class, then reload My classes as the teacher |
**What you should see**: Title `My classes`, description `Classes you teach and their schedule.` (BM `Kelas saya` / `Kelas yang anda ajar dan jadualnya.`). Only classes assigned to THIS teacher are listed (name, 12-hour schedule line, program · level when set); the unassigned/other class never appears. There are no management controls of any kind. With no assignments the card reads `You're not assigned to any classes yet.` (BM `Anda belum ditugaskan ke mana-mana kelas.`), and an archived class drops off the list. An operator opening `/dashboard/my-classes` is redirected to `/dashboard` (`requireTeacher`).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Page added in commit b175d3e (Better Auth PR): the teacher role is assigned on org membership, not email inference.

### TC-CLS-151: Archiving is refused while students are still enrolled (billing-trap guard)
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Operator; a class with at least one Active or Paused enrolment (check the roster on the class detail; enrol a student first if needed). Note how many current (non-ended) enrolments it has.
| Step | Action |
|------|--------|
| 1 | On Classes, open that class's row kebab, click Archive, and confirm in the dialog |
| 2 | Read the message inside the dialog; then Cancel and re-scan the list |
| 3 | (API bypass) In DevTools: `fetch('/api/classes/<id>', { method: 'DELETE' }).then(r => r.json().then(b => [r.status, b]))` |
| 4 | End every current enrolment on the class, then archive again |
**What you should see**: Step 2: the dialog STAYS OPEN and shows "Cannot archive yet: N student(s) are still enrolled in this class. End their enrolments first." (BM: "Belum boleh diarkibkan: N pelajar masih berdaftar dalam kelas ini. Tamatkan pendaftaran mereka dahulu."), with N matching the current-enrolment count; no success toast; the class stays Active on the list. Step 3: HTTP 409 `{"error":"has_active_enrollments","count":N}` (the guard is server-side, not just UI). Step 4: with every enrolment ended, the archive succeeds as in TC-CLS-090.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: archiving used to flip the class status only, leaving Active enrolments that Run Billing kept invoicing every month with the class hidden from every list; guard added in 667eecb (decided 2026-07-04; TDD service test + browser-verified with a 3-student class). Paused enrolments also block (they count as current).

---

## TAXONOMY (Programs & Levels)

> Programs ("what is taught", e.g. Quran, Math) and Levels ("the stage", e.g. Asas, SPM) share one
> shape/service (`tableFor(kind)`). Managed at `/dashboard/setup/programs` and `/dashboard/setup/levels`
> via `TaxonomyManager`. Default tier **T2** (config; tenant cases T1).

## O. Taxonomy add / list / empty

### TC-TAX-001: Add a program appears immediately, sorted alphabetically
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator. Open `/dashboard/setup/programs`.
**Test Data**: add `Quran`, then `Mathematics`, then `English`.
| Step | Action |
|------|--------|
| 1 | Type `Quran` in the add box, click Add |
| 2 | Add `Mathematics`, then `English` |
**What you should see**: Each appears in the list without a page reload; the list is sorted A-Z client-side, so the order becomes `English, Mathematics, Quran`. The add box clears after each add (`listTaxonomy` server order is `asc(name)` too).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TAX-002: Add a level on the Levels page is separate from Programs
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator with at least one program. Open `/dashboard/setup/levels`.
**Test Data**: add `Asas`.
| Step | Action |
|------|--------|
| 1 | Add `Asas` on the Levels page |
| 2 | Open `/dashboard/setup/programs` |
**What you should see**: `Asas` appears under Levels only; it does NOT appear under Programs (separate tables; mirrors the service test "lists levels separately from programs"). Programs still shows only its own items.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TAX-003: Empty taxonomy list shows the explicit empty message
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator in an org with no programs. Open `/dashboard/setup/programs`.
| Step | Action |
|------|--------|
| 1 | Read the card body |
**What you should see**: `Nothing here yet. Add your first one above.` (`empty`, BM `Belum ada apa-apa di sini. Tambah yang pertama di atas.`); NOT a blank card.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TAX-004: Add button disabled until a non-blank name is typed
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator on `/dashboard/setup/programs`.
| Step | Action |
|------|--------|
| 1 | Look at the Add button with the box empty |
| 2 | Type only spaces |
| 3 | Type `Quran` |
**What you should see**: Add is disabled while the box is empty or whitespace-only (`disabled={busy || !newName.trim()}`); pressing Enter on an empty box does nothing; Add enables once real text is typed.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TAX-005: Add via the Enter key works
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator on `/dashboard/setup/programs`.
**Test Data**: `Tajweed`.
| Step | Action |
|------|--------|
| 1 | Type `Tajweed`, press Enter (do not click Add) |
**What you should see**: `Tajweed` is added (Enter triggers `handleAdd`); the box clears.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## P. Taxonomy validation

### TC-TAX-010: Blank / whitespace name is not added
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on `/dashboard/setup/programs`.
| Step | Action |
|------|--------|
| 1 | With the box empty, attempt to add (button disabled; try Enter) |
| 2 | POST `/api/taxonomy/programs` with `{ "name": "" }` directly |
**What you should see**: UI never submits a blank (`handleAdd` returns early on empty trim, button disabled). API returns **422** `{ error: "Invalid input" }` (`taxonomyInputSchema` `min(1)`, key `required`). Nothing created.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TAX-011: Name over 80 characters is rejected (server-side)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: API
**Before you start**: Operator. POST `/api/taxonomy/levels`.
**Test Data**: a name of 81 chars, then 80 chars.
| Step | Action |
|------|--------|
| 1 | POST an 81-char name |
| 2 | POST an 80-char name |
**What you should see**: 81 -> **422** (`max(80)`); 80 accepted (201). Boundary at 80.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TAX-012: Duplicate names are allowed (free-text list)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on `/dashboard/setup/programs` with `Quran` already added.
**Test Data**: add `Quran` a second time.
| Step | Action |
|------|--------|
| 1 | Add `Quran` again |
**What you should see**: A SECOND `Quran` row is created (no uniqueness constraint; duplicate names are intentionally allowed per FLOWS §1). Both appear in the list.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TAX-013: Unknown taxonomy kind in the URL returns Not found
**Tags**: @regression @security **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: API
**Before you start**: Operator. Hit a bad kind.
| Step | Action |
|------|--------|
| 1 | POST `/api/taxonomy/subjects` (not a real kind) |
| 2 | GET `/api/taxonomy/foo` |
**What you should see**: HTTP **404** `{ "error": "Unknown taxonomy" }` (`parseKind` only allows `programs` / `levels`). No data.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## Q. Taxonomy rename

### TC-TAX-020: Rename a program updates it everywhere it is used as a filter
**Tags**: @smoke @regression @data-integrity **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator with a program `Quran` used by at least one class. Open `/dashboard/setup/programs`.
**Test Data**: rename `Quran` to `Quran Tilawah`.
| Step | Action |
|------|--------|
| 1 | Click the pencil (edit) icon on `Quran` |
| 2 | Change the text to `Quran Tilawah`, click Save (or press Enter) |
| 3 | Re-list, then open Classes |
**What you should see**: The row now reads `Quran Tilawah`, re-sorted alphabetically; the class that used it shows the new name in the Program column and in the Program filter (existing classes keep the link, see TC-TAX-022). Pressing Escape during edit cancels without saving.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TAX-021: Rename to blank is not saved
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Type**: Feature
**Before you start**: Operator editing a program inline.
| Step | Action |
|------|--------|
| 1 | Clear the edit box, click Save |
**What you should see**: Nothing saved (`handleRename` returns early on empty trim); the original name remains; the edit box closes. If forced via PATCH with `{"name":""}` the API returns **422** (`required`).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TAX-022: Renaming keeps the label on classes already using it
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator; a program assigned to a class.
| Step | Action |
|------|--------|
| 1 | Rename the program |
| 2 | Open the class list / detail |
**What you should see**: The class still shows the program (now the new name): the class stores the program id, not the text, so the rename flows through (the archive_desc copy "Existing classes that use it keep their label" reflects the id-based link).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## R. Taxonomy archive

### TC-TAX-030: Archive a program removes it from the active list and the class-form dropdown
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator with two programs `Tajweed` and `Hafazan`. Open `/dashboard/setup/programs`.
| Step | Action |
|------|--------|
| 1 | Click the trash (archive) icon on `Tajweed` |
| 2 | Confirm the dialog `Archive "Tajweed"?` |
| 3 | Re-list, then open the new class form's Program dropdown |
**What you should see**: Confirm dialog title `Archive "Tajweed"?` (`archive_title` with name), body `It will no longer appear when creating or filtering classes. Existing classes that use it keep their label.` (`archive_desc`). After confirm, `Tajweed` leaves the list (only `Hafazan` remains; `listTaxonomy` filters `ne(status, 'archived')`); the class-form Program dropdown no longer offers `Tajweed`. It is soft-archived, not deleted.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TAX-031: Archived items are excluded from the active list (mirrors the service test)
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator; add `Tajweed` and `Hafazan`, archive `Tajweed`.
| Step | Action |
|------|--------|
| 1 | Re-load `/dashboard/setup/programs` |
**What you should see**: List shows `Hafazan` only (`Tajweed` excluded). Matches service test "excludes archived items from the active list".
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TAX-032: A class already using an archived program keeps its label
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator; a class assigned program `Quran`. Archive `Quran`.
| Step | Action |
|------|--------|
| 1 | Open the class list / detail |
**What you should see**: The class still shows `Quran` (the program row still exists, only `status=archived`; the join still resolves the name). Only the dropdown/filter hides it for NEW selection.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## S. Taxonomy permissions + tenant isolation

### TC-TAX-040: Cannot archive another org's taxonomy item (tenant guard)
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: API
**Before you start**: Org A operator creates a program (note its id). Switch to org B operator. Mirrors the service test "cannot archive another org's item".
| Step | Action |
|------|--------|
| 1 | As org B, DELETE `/api/taxonomy/programs/<org-A-program-id>` |
| 2 | As org B, PATCH `/api/taxonomy/programs/<org-A-program-id>` with `{"name":"Hacked"}` |
| 3 | Switch back to org A and re-list programs |
**What you should see**: Both return **404** `{ "error": "Not found" }` (`updateTaxonomy`/`archiveTaxonomy` scope `and(eq(id), eq(orgId))` and return undefined). Org A's program is unchanged (still active, original name).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TAX-041: Taxonomy list is org-scoped (no cross-tenant leak)
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: Feature
**Before you start**: Org A has program `Quran`; org B has program `Mathematics`. Log in as org B. Mirrors service test "isolates programs by org".
| Step | Action |
|------|--------|
| 1 | Open `/dashboard/setup/programs` as org B |
| 2 | GET `/api/taxonomy/programs` as org B |
**What you should see**: Only `Mathematics`; never `Quran`. The API `data` array contains only org B items.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TAX-042: Teacher cannot manage taxonomy
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Type**: API
**Before you start**: Authenticated as a teacher.
| Step | Action |
|------|--------|
| 1 | Navigate to `/dashboard/setup/programs` |
| 2 | POST `/api/taxonomy/programs` with `{"name":"X"}` |
| 3 | DELETE `/api/taxonomy/programs/<any-id>` |
**What you should see**: The Setup page redirects a teacher to `/dashboard/attendance` (operator route group); the APIs return **401** `{ "error": "Forbidden: operators only" }` (`requireOperatorContext`). Nothing created/archived.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TAX-043: No org context: taxonomy API returns 401
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T1 | **Type**: API
**Before you start**: Signed-in user with no active org.
| Step | Action |
|------|--------|
| 1 | GET `/api/taxonomy/programs` |
| 2 | POST `/api/taxonomy/levels` with a valid name |
**What you should see**: Both **401** with the `OrgRequiredError` message; no data returned, nothing created.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## T. Taxonomy security + i18n

### TC-TAX-050: Taxonomy name with a script payload is shown escaped
**Tags**: @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator on `/dashboard/setup/programs`.
**Test Data**: name = `<script>alert('xss')</script>`.
| Step | Action |
|------|--------|
| 1 | Add a program with that name |
| 2 | View it in the list and in the new class form's Program dropdown |
**What you should see**: The literal text renders escaped in the list row and the dropdown option; no alert pops. No script executes.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TAX-051: Taxonomy pages render in BM
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Type**: Feature
**Before you start**: Operator. Switch the app language to BM. Open `/dashboard/setup/programs` and `/dashboard/setup/levels`.
| Step | Action |
|------|--------|
| 1 | Read the Programs page heading/description and the Add button |
| 2 | Open the archive confirm dialog on an item |
| 3 | Read the empty-state on a fresh kind |
**What you should see**: Programs title `Program`, Levels title `Tahap`; Add button `Tambah`; archive dialog `Arkibkan "<name>"?` body `Ia tidak lagi muncul semasa mencipta atau menapis kelas...`; empty `Belum ada apa-apa di sini. Tambah yang pertama di atas.`
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

---

## Coverage note

Updated **2026-07-04** (catalog originally assembled 2026-06-30, never executed, so stale cases
were rewritten in place keeping their TC IDs; new cases appended as TC-CLS-140..150, then
TC-CLS-151 for the archive guard shipped later the same day in 667eecb).

Cases: **90 total**: 69 classes (TC-CLS-001..151) + 21 taxonomy (TC-TAX-001..051). No cases
deleted.

Smoke subset (@smoke, 9, unchanged IDs): TC-CLS-001 (create), TC-CLS-020 (single class-size
field), TC-CLS-040 (pay-model label), TC-CLS-070 (teacher assign + link), TC-CLS-090 (archive),
TC-CLS-100 (empty state), TC-CLS-113 (cross-tenant detail), TC-TAX-001 (taxonomy add) and
TC-TAX-020 (rename). These are the thin happy-path-per-area go/no-go set.

Rewritten for post-catalog code changes:
- **55f4251** (finding triage, 2026-06-30 after assembly): capacity is one `Class size` field
  (CLS-001/002/020/021/022/023/024/080/083 rewritten); schedule times display 12-hour AM/PM
  (CLS-001/002/051/052/055/130); zero teacher rate now shows `RM0.00` (CLS-033/035).
- **746df0b/df2e3f1/a9737aa** (table + tones): CLS-063/100 rewritten; CLS-140..144 added.
- **6e45620/31777bd** (toasts + failure surfacing): CLS-001/081/090 updated; CLS-145/146 added.
- **8ecc138** (phone width): CLS-147 added.
- **b691bbc** (RM 0 fee warning): CLS-031 updated; CLS-148 added.
- **63c3365** (onboarding deep-link): CLS-149 added.
- **Better Auth migration + b175d3e**: Clerk references removed (CLS-110); dev logins added to
  the conventions; teacher self-service my-classes covered by CLS-150. The teacher/no-org
  gating semantics (redirects + 401s) are unchanged, so CLS-111/112 and the TAX permission
  cases stand as written.

Findings re-triage (from qa/README.md):
- **Finding #2 (TC-CLS-083)**: RESOLVED. `capacityMin` and the `capacity_order` refine were
  removed outright in 55f4251; `classUpdateSchema.capacityMax` keeps the same 1..500 bounds as
  create, so no update-only validation gap remains.
- **Finding #5 (TC-CLS-035)**: FIXED. The detail card check is now `teacherRatePerSession != null`,
  so a saved 0 renders `RM0.00`; the dash only appears for a null (unset legacy) value.

Techniques walked (per QA-METHODOLOGY §5):
- **Happy path**: CLS-001/002, TAX-001/002/020/030.
- **Equivalence + boundary**: name 120/121 (CLS-011), class size 0/1, 500/501 (CLS-021/022/023),
  fee 0/negative/cap (CLS-030/031/034), >2dp money (CLS-032/033), duration 600/601/non-int
  (CLS-054), time 00:00/23:59/25:00 (CLS-052/053), notes 2000/2001 (CLS-103), taxonomy name
  80/81 (TAX-011).
- **Negative / validation + server bypass**: CLS-012/024/034/050/052/054/083/103,
  TAX-010/011/013/021.
- **Format / locale**: CLS-130, TAX-051 (RM, BM labels, BM day shorts, 12-hour AM/PM times),
  CSV export with UTF-8 BOM (CLS-142).
- **Permissions / role**: CLS-110/111/112, CLS-150 (teacher-only page, operator redirected),
  TAX-042/043 (teacher redirect + 401, no-org 401).
- **Cross-tenant / IDOR**: CLS-073/093/113/114/115, CLS-150 (teacher sees only own assignments),
  TAX-040/041 (foreign teacher ignored; 404 not-found; org-scoped lists; mirrors the service tests).
- **State transition**: archive (CLS-090/091/092), reassign/unassign teacher (CLS-071/072),
  edit pay model frozen-pay (CLS-082), taxonomy archive/rename (TAX-020/030/031/032).
- **Idempotency**: double archive (CLS-092 step), rename re-sort (TAX-020).
- **Empty / loading / error states**: CLS-061/062/100/102, filtered-empty vs true-empty
  (CLS-141), failure surfaced in dialog (CLS-146), TAX-003.
- **Data integrity**: fee/rate 2dp persistence (CLS-004/043), per-day slot persistence (CLS-051),
  archived excluded from list + class-health (CLS-090/091), export matches the filtered view
  (CLS-142), rename flows by id (TAX-022/032).
- **Security (input -> render / mass-assign)**: CLS-120/121, CLS-083 (stray removed field
  stripped), TAX-050 (XSS escaped; orgId/id/status not mass-assignable).
- **Responsive**: phone-width schedule row (CLS-147); the rest stays in
  `test-plan-crosscutting.md`.

Deliberately skipped rows with reason:
- **Accessibility (a11y)** and **Non-functional (perf/N+1)**: tracked in `test-plan-crosscutting.md`
  and the load pass, not duplicated here per the methodology's "skip with reason" rule.
- **Concurrency**: two operators editing the same class at once relies on a single PATCH transaction;
  no unique-constraint race exists for classes, so it is noted, not enumerated (see FLOWS "Known gaps").
- **Class/enrolment CSV import** (`Import` menu on the Classes list, added with the Better Auth
  PR): owned by `test-plan-import.md` (separate author); intentionally NOT covered here beyond
  noting the menu's presence. This file contains no import cases.
