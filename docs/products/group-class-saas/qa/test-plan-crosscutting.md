# Test plan: Cross-cutting (validation, i18n, PII masking, responsive, a11y, theme, tables, feedback)

> Exhaustive manual catalog for the concerns that apply across every form and screen.
> Format + method: [QA-METHODOLOGY.md](QA-METHODOLOGY.md). Matched to [test-plan-billing.md](test-plan-billing.md).
> Grounded in `src/utils/validators.ts` (+ `validators.test.ts`, 11 validator tests), `src/features/ui/IdNumberField.tsx`,
> `src/components/ui/form.tsx` (`FormMessage` translates `Validation.*` keys), `src/features/ui/SensitiveValue.tsx`,
> `src/utils/Format.ts`, `src/features/ui/TimePicker.tsx`, `src/features/ui/DatePicker.tsx` + `MonthPicker.tsx`,
> `src/components/LocaleSwitcher.tsx`, `src/locales/{en,ms}.json`, `src/styles/global.css` (light + dark design tokens),
> `src/app/[locale]/layout.tsx` (next-themes `ThemeProvider`, light default), `src/features/dashboard/account-menu.tsx`
> (theme picker), `src/features/ui/DataTable.tsx` + `data-table/{toolbar,pagination}.tsx` (shared list table),
> `src/features/ui/RowActions.tsx` (confirm + toast), and [FLOWS.md](../FLOWS.md) §8 + [UI-CONVENTIONS.md](../UI-CONVENTIONS.md).
>
> Assembled 2026-06-30; **updated 2026-07-04** for the post-catalog work: Better Auth first-party sign-in pages
> (replacing Clerk), dark mode (2a7804c), the design-system pass (b300923/91a3820/e8dc921/135ff13: teal primary,
> slate wash, tabular numerals, uppercase table headers, text-safe success/warning tokens, Geist Mono removed),
> the table usability pass (746df0b, df2e3f1), success/error feedback + public skeleton (6e45620, 31777bd), and the
> i18n fixes (e86b941, b68ac79, 8e3d66d, 6974f69). **78 cases; 9 @smoke.** No cases deleted; new sections M, N, O.
>
> These concerns repeat in every form, so cases pick representative forms rather than re-testing each one: class fee/rate
> (`/dashboard/classes/new`), student IC/phone/DOB (`/dashboard/students/new`), teacher bank account (`/dashboard/teachers/new`),
> payment amount (Billing > Record payment), payout mark-paid (`/dashboard/payroll`). The same rule applies on every other
> form by inheritance.
>
> Tiers: **T1** where money or PII is at stake (validation of amounts/IC/bank, masking); **T2/T3** for display-only i18n,
> responsive, theme, tables, feedback, and accessibility. Roles: operator (full dashboard), public (invoice token page,
> no login). Dev logins: operator `operator@kelastest.local` / `newpassword6789`; teacher `teacher@kelastest.local` /
> `password12345`.
>
> Locale note: the language toggle is the globe icon in the dashboard header (`LocaleSwitcher`, a dropdown with radio items
> "English" / "Bahasa Malaysia"); switching changes the URL prefix between `/en/...` and `/ms/...`. Validation messages are
> i18n keys in the `Validation` namespace; `FormMessage` resolves them, so a raw key on screen (e.g. `Validation.ic_invalid`)
> is always a failure.
>
> Theme note: the theme picker lives in the account menu (click your avatar in the header, or the user chip at the bottom
> of the sidebar) under the "Theme" label, with options "Light" / "Dark" / "Follow device" (BM "Tema": "Cerah" / "Gelap" /
> "Ikut peranti"). Light is the default; dark is an explicit per-browser choice (stored in localStorage key `theme`).
>
> Smoke subset (@smoke): TC-VAL-001, TC-VAL-020, TC-VAL-030, TC-VAL-050, TC-I18N-001, TC-PII-001, TC-PII-010,
> TC-THEME-001, TC-TBL-002.

## A. Validation: Malaysian IC (`isValidMyIc`, `IdNumberField` IC mode)

### TC-VAL-001: A well-formed IC is accepted and auto-dashed
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T1
**Before you start**: Log in as operator. Go to Students > New. The ID field shows an IC / Passport toggle; leave it on IC.
**Test Data**: type `920101145567` (no dashes).
| Step | Action |
|------|--------|
| 1 | Click into the ID number field with IC selected |
| 2 | Type `920101145567` |
| 3 | Fill the other required fields with valid data and Save |
**What you should see**: As you type, the field auto-formats to `920101-14-5567`. No validation error appears on the ID field; the student saves.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-VAL-002: A foreigner state code (99) is accepted
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T1
**Before you start**: Operator on Students > New, IC mode.
**Test Data**: `920101-99-5567` (state code 99 = foreigner / stateless).
| Step | Action |
|------|--------|
| 1 | Type `920101995567` in the IC field |
| 2 | Fill other required fields, Save |
**What you should see**: The IC is accepted (state code 99 is valid); the student saves with `920101-99-5567`. No "invalid IC" error.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-VAL-003: IC with an impossible month is rejected
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T1
**Before you start**: Operator on Students > New, IC mode.
**Test Data**: `921301-14-5567` (month 13).
| Step | Action |
|------|--------|
| 1 | Type `921301145567` in the IC field |
| 2 | Try to Save |
**What you should see**: Blocked with the bilingual IC message ("Enter a valid IC, e.g. 920101-14-5567." in EN). The exact text is shown, never the raw key `Validation.ic_invalid`. The student is not saved.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-VAL-004: IC with a bad state code (00) is rejected
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T1
**Before you start**: Operator on Students > New, IC mode.
**Test Data**: `920101-00-5567` (state code 00 is unassigned).
| Step | Action |
|------|--------|
| 1 | Type `920101005567` in the IC field |
| 2 | Try to Save |
**What you should see**: Blocked with the bilingual IC validation message; no save. (State codes 17-20 behave the same; 01-16, 21-85, 98, 99 are the only valid ranges.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-VAL-005: IC of the wrong length is rejected
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T1
**Before you start**: Operator on Students > New, IC mode.
**Test Data**: `92010114556` (11 digits).
| Step | Action |
|------|--------|
| 1 | Type `92010114556` in the IC field |
| 2 | Try to Save |
**What you should see**: Blocked: an IC must be exactly 12 digits. The bilingual IC message is shown; no save.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-VAL-006: IC field rejects letters and an empty value where required
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator on Students > New, IC mode.
**Test Data**: try `A12345678` (letters in IC mode); then clear the field.
| Step | Action |
|------|--------|
| 1 | Type `A12345678` while IC mode is selected |
| 2 | Observe what the field keeps |
| 3 | If the ID is required for this form, clear it and try to Save |
**What you should see**: IC mode strips non-digits as you type (letters do not appear); a non-IC value is blocked at save. If the field is required and left blank, the required message appears ("This field is required." / BM equivalent), not the raw key.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## B. Validation: Passport (`isValidPassport`, `IdNumberField` passport mode)

### TC-VAL-010: Passport mode accepts loose 6-12 alphanumeric and uppercases input
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator on Students > New. Click the Passport segment of the ID toggle.
**Test Data**: type `a1234567` (lower case, 8 chars).
| Step | Action |
|------|--------|
| 1 | Switch the ID toggle to Passport |
| 2 | Type `a1234567` |
| 3 | Fill other required fields, Save |
**What you should see**: The value uppercases to `A1234567` as you type; it is accepted (passports are intentionally loose, no strict per-country regex). The student saves.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-VAL-011: Passport too short or with symbols is rejected
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2
**Before you start**: Operator on Students > New, Passport mode.
**Test Data**: try `12345` (5 chars, too short); then `ABC!@#` (symbols).
| Step | Action |
|------|--------|
| 1 | Type `12345` and try to Save |
| 2 | Clear, type `ABC!@#`, observe the field, try to Save |
**What you should see**: `12345` is blocked (minimum 6 alphanumeric). Symbols are stripped on entry (`ABC` remains, which is then too short) and the passport message is shown; no save.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-VAL-012: Toggling IC <-> Passport re-normalises the existing value
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Before you start**: Operator on Students > New.
**Test Data**: in IC mode type `920101145567`, then switch to Passport.
| Step | Action |
|------|--------|
| 1 | In IC mode type `920101145567` (shows `920101-14-5567`) |
| 2 | Click the Passport segment |
| 3 | Switch back to IC |
**What you should see**: Switching to Passport re-formats the held value (uppercased alphanumeric, dashes removed); switching back to IC re-applies the dashed IC format. No crash, no stale half-formatted value.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## C. Validation: Phone (`normalizeMyPhone`, `phoneField`)

### TC-VAL-020: Mobile, landline, and +60 international forms all normalise and save
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator on Students > New (or Guardians > New). Find the phone field.
**Test Data**: try, one at a time: `012-345 6789` (mobile), `03-8888 9999` (landline), `+60123456789` (international).
| Step | Action |
|------|--------|
| 1 | Type `012-345 6789` and Save |
| 2 | New record: type `03-8888 9999` and Save |
| 3 | New record: type `+60123456789` and Save |
**What you should see**: Each saves with no phone error. The stored value normalises to local 0-prefixed digits (`0123456789`, `0388889999`, `0123456789`). All three are accepted.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-VAL-021: Junk phone input is rejected with the bilingual message
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator on a form with a phone field.
**Test Data**: try `123` (too short), then `abc` (letters).
| Step | Action |
|------|--------|
| 1 | Type `123` and try to Save |
| 2 | Type `abc` and try to Save |
**What you should see**: Each is blocked with the phone message ("Enter a valid Malaysian phone number, e.g. 012-345 6789." in EN). The exact sentence is shown, not the raw key `Validation.phone_my`. No save.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-VAL-022: Server rejects a bad phone when the UI rule is bypassed
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T1
**Before you start**: Operator. Have a valid create/update request body for a record with a phone field (capture one via DevTools Network while saving a valid record).
**Test Data**: replay the request with `phone: "123"`.
| Step | Action |
|------|--------|
| 1 | Submit the create/update API directly with `phone` set to `123` |
**What you should see**: The API rejects it (the same Zod `phoneField` runs server-side via `safeParse`); no record is stored with an invalid phone. The response is a validation error, not a 500.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## D. Validation: Bank account (`bankAccountField`, `formatAccountNumber`)

### TC-VAL-030: Account number strips formatting and stores digits only
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator on Teachers > New. Find the bank account field.
**Test Data**: type `1234-5678 90` (with a dash and a space).
| Step | Action |
|------|--------|
| 1 | Type `1234-5678 90` in the account field |
| 2 | Fill other required fields, Save |
| 3 | Open the saved teacher detail and reveal the account |
**What you should see**: Non-digits are stripped on entry; the saved value is `1234567890` (digits only). No validation error. (Same rule on Billing > Settings org account, see TC-BILL-090/091.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-VAL-031: Account shorter than 5 or longer than 20 digits is rejected
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T1
**Before you start**: Operator on Teachers > New.
**Test Data**: try `1234` (4 digits); then `123456789012345678901` (21 digits).
| Step | Action |
|------|--------|
| 1 | Type `1234` and try to Save |
| 2 | Type a 21-digit number and observe the field, try to Save |
**What you should see**: `1234` is blocked with the bank message ("Account number must be 5 to 20 digits." in EN); the 21st digit is not accepted into the field (max 20). The raw key `Validation.bank_account` is never shown. No save on the too-short value.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-VAL-032: Letters in the account number are stripped (UI) and rejected (server)
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T1
**Before you start**: Operator on Teachers > New, then a captured save request for server bypass.
**Test Data**: type `abc123` in the UI; then replay the save API with `bankAccount: "abc123"`.
| Step | Action |
|------|--------|
| 1 | Type `abc123` in the account field; observe what remains |
| 2 | Submit the save API directly with `bankAccount` = `abc123` |
**What you should see**: The UI keeps only `123` (then blocks it as < 5 digits). The API rejects `abc123` (the `bankAccountField` regex `^\d{5,20}$` runs server-side); no alphabetic account is stored.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## E. Validation: Money (`money()`, `max2dp`)

### TC-VAL-040: A valid 2-decimal fee/amount is accepted
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T1
**Before you start**: Operator on Classes > New (the monthly fee field) and/or Billing > Record payment.
**Test Data**: `120.50`.
| Step | Action |
|------|--------|
| 1 | Enter `120.50` in the fee/amount field |
| 2 | Save |
**What you should see**: Accepted; the value persists as `120.50` and displays as `RM120.50` everywhere it is shown.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-VAL-041: Amount with more than 2 decimals is rejected
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T1
**Before you start**: Operator on a money field (class fee, teacher rate, payment amount).
**Test Data**: `10.999`.
| Step | Action |
|------|--------|
| 1 | Enter `10.999` and try to Save |
**What you should see**: Blocked with the decimals message ("Use at most 2 decimal places." in EN). The raw key `Validation.amount_decimals` is never shown. No save.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-VAL-042: Negative amount is rejected
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T1
**Before you start**: Operator on a money field.
**Test Data**: `-50`.
| Step | Action |
|------|--------|
| 1 | Enter `-50` and try to Save |
**What you should see**: Blocked (money is non-negative). A validation message is shown, not a stored negative value and not a raw key.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-VAL-043: Zero where a positive amount is required is rejected
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2
**Before you start**: Operator on Billing > Record payment (a payment must be > 0) or an adjustment.
**Test Data**: `0`.
| Step | Action |
|------|--------|
| 1 | Enter `0` as a payment amount and try to Save |
**What you should see**: Blocked with the positive-amount message ("Amount must be greater than 0." in EN, key `amount_positive`) or, for an adjustment, the non-zero message ("Amount cannot be 0.", key `amount_nonzero`). No payment recorded. (Cross-references TC-BILL-024.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-VAL-044: Server rejects a >2dp / negative amount when the UI is bypassed
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator. Capture a valid Record-payment request via DevTools Network.
**Test Data**: replay with `amount: 10.999`, then `amount: -50`.
| Step | Action |
|------|--------|
| 1 | Replay the payment API with `amount` = `10.999` |
| 2 | Replay with `amount` = `-50` |
**What you should see**: Both rejected server-side (the same `money()` schema runs in the API `safeParse`); no payment is recorded; the balance is unchanged. Response is a validation error, not a 500.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## F. Validation: Date of birth (`isValidPastDate`, `dobField`)

### TC-VAL-050: A real past date is accepted, including a leap day
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator on Students > New. Find the DOB field.
**Test Data**: `2000-02-29` (a real leap day).
| Step | Action |
|------|--------|
| 1 | Enter DOB `2000-02-29` |
| 2 | Fill other required fields, Save |
**What you should see**: Accepted; the student saves. On the detail page the DOB renders day-first as `29/02/2000`.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-VAL-051: A future DOB is rejected
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T1
**Before you start**: Operator on Students > New.
**Test Data**: a date in 2999 (e.g. `2999-01-01`).
| Step | Action |
|------|--------|
| 1 | Enter DOB `2999-01-01` and try to Save |
**What you should see**: Blocked with the DOB message ("Enter a valid date of birth (not in the future)." in EN, key `dob_invalid`). The raw key is never shown; no save.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-VAL-052: A pre-1900 DOB is rejected
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2
**Before you start**: Operator on Students > New.
**Test Data**: `1899-01-01`.
| Step | Action |
|------|--------|
| 1 | Enter DOB `1899-01-01` and try to Save |
**What you should see**: Blocked (dates must be 1900 onward); the bilingual DOB message is shown; no save.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-VAL-053: An impossible calendar date is rejected (31 Feb / 29 Feb non-leap)
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2
**Before you start**: Operator on Students > New. (If the picker prevents typing, send the value via the API per the bypass note.)
**Test Data**: `2001-02-29` (2001 is not a leap year); also `2000-02-30`.
| Step | Action |
|------|--------|
| 1 | Set DOB to `2001-02-29` and try to Save |
| 2 | Set DOB to `2000-02-30` and try to Save |
**What you should see**: Both rejected: the validator does not let a bad day "roll over" to the next month. The bilingual DOB message is shown; no save.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## G. Validation: required fields + server-side enforcement (general)

### TC-VAL-060: Submitting a form with a required field blank shows the required message
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator on any create form (Classes > New is representative).
| Step | Action |
|------|--------|
| 1 | Leave a required field (e.g. class name) blank |
| 2 | Click Save |
**What you should see**: Save is blocked; the field shows the required message ("This field is required." / BM "Medan ini wajib diisi."). Focus / error styling marks the offending field; no raw key `Validation.required` appears.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-VAL-061: Validation errors clear once the field is corrected
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Before you start**: Operator on a form showing a validation error (from any earlier case).
| Step | Action |
|------|--------|
| 1 | Trigger a validation error (e.g. bad IC) |
| 2 | Correct the value to a valid one |
**What you should see**: The error message disappears once the value is valid; the field returns to its normal (non-error) styling. Save then proceeds.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-VAL-062: Server is the source of truth: a tampered IC is rejected on submit
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator. Capture a valid student create request via DevTools Network.
**Test Data**: replay with `icNumber: "921301145567"` (bad month) and idType `ic`.
| Step | Action |
|------|--------|
| 1 | Replay the create API with the invalid IC |
**What you should see**: The API rejects it (the shared validators run server-side; the API accepts either IC or passport as a backstop but still rejects a malformed IC). No student is created. Response is a validation error, not a 500. (Confirms the form rule is not the only gate.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## H. Localisation / i18n (EN <-> BM)

### TC-I18N-001: Switching to BM translates every label on a representative form
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T2
**Before you start**: Operator on Students > New (rich form: ID toggle, phone, DOB, fee fields).
| Step | Action |
|------|--------|
| 1 | Note the EN field labels and buttons |
| 2 | Open the globe (language) menu in the header, pick Bahasa Malaysia |
| 3 | Re-read the same form |
**What you should see**: The URL prefix changes from `/en/` to `/ms/`. Every label, button, placeholder and the ID-type toggle ("IC" / "Pasport") is in Malay. No raw key like `Students.ic` or `Common.save` is visible anywhere on the page.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-I18N-002: Validation messages are bilingual (BM run)
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator with language set to Bahasa Malaysia, on Students > New.
**Test Data**: bad IC `921301145567`, junk phone `abc`, future DOB `2999-01-01`.
| Step | Action |
|------|--------|
| 1 | Enter the bad IC and try to Save |
| 2 | Enter the junk phone and try to Save |
| 3 | Enter the future DOB and try to Save |
**What you should see**: Each message is the Malay string: IC "Masukkan IC yang sah, cth. 920101-14-5567.", phone "Masukkan nombor telefon Malaysia yang sah, cth. 012-345 6789.", DOB "Masukkan tarikh lahir yang sah (bukan masa hadapan)." No English fallback and no raw `Validation.*` key.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-I18N-003: Money always shows RM, never MYR, in both languages
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T1
**Before you start**: Operator viewing a screen with money (Billing list, an invoice, or the dashboard) in EN, then BM.
| Step | Action |
|------|--------|
| 1 | Read a money figure in EN (e.g. an invoice total) |
| 2 | Switch to Bahasa Malaysia and read the same figure |
**What you should see**: Money renders with the `RM` symbol (e.g. `RM120.50`) in both languages. The string `MYR` never appears in front of an amount on screen or in the PDF. (The formatter passes `MYR` as the currency code but `en-MY` / `ms-MY` renders it as `RM`.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-I18N-004: Dates render day-first (DD/MM/YYYY) in both languages
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator viewing a record with a date (a student DOB, an invoice due date) in EN, then BM.
| Step | Action |
|------|--------|
| 1 | Read a date in EN |
| 2 | Switch to BM and read the same date |
**What you should see**: The date is day-first `DD/MM/YYYY` (e.g. `29/02/2000`) in both languages, never US month-first `MM/DD/YYYY`. Month names, where spelled out (e.g. a billing month), use Malay month names in BM.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-I18N-005: Times render in Malaysia time, 12-hour, in both languages
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Before you start**: Operator viewing a screen with a time (a class schedule time or a timestamped record) in EN, then BM.
| Step | Action |
|------|--------|
| 1 | Read a time value in EN |
| 2 | Switch to BM and read the same time |
**What you should see**: Time is shown 12-hour with am/pm in Asia/Kuala_Lumpur (UTC+8), e.g. `8:00 PM`, in both languages. Not a 24-hour or UTC value.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-I18N-006: Public invoice page is bilingual via the URL locale
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: An issued invoice's public link. Open it once with `/en/` and once with `/ms/` in the path (no login).
| Step | Action |
|------|--------|
| 1 | Open the public link with the `/en/invoice/<token>` path |
| 2 | Open the same token with the `/ms/invoice/<token>` path |
**What you should see**: EN page in English, BM page in Malay; both render labels (no raw keys), money as `RM`, and dates as `DD/MM/YYYY`. The DuitNow QR and bank details show on both.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-I18N-007: en/ms key parity holds (no missing translations)
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: A checkout of the kelas repo with dev tooling. (Automated cross-check that backs every i18n case.)
| Step | Action |
|------|--------|
| 1 | From `kelas/`, run `npm run check:i18n` |
**What you should see**: The `i18n-check` (source `en`, used keys scanned in `src`, next-intl format) passes: no missing keys in `ms.json` versus `en.json`, and no used-but-undefined keys. A failure here predicts a raw key showing up in the BM UI.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-I18N-008: Selected language persists across sidebar navigation
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator on the dashboard.
| Step | Action |
|------|--------|
| 1 | Switch to Bahasa Malaysia via the globe menu |
| 2 | Using the SIDEBAR links, navigate to Kelas (Classes), then Guru (Teachers), then back to Papan Pemuka (Dashboard) |
| 3 | Read the URL after each click |
**What you should see**: Every page stays in Malay and the URL keeps the `/ms/` prefix on each sidebar navigation; the language never silently reverts to English between pages.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: sidebar items used a plain `next/link`, dropping the locale prefix, so a BM operator fell back to English on every sidebar click; locale-aware `Link` since commit e86b941.

### TC-I18N-009: Date and month pickers speak the active language
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator in Bahasa Malaysia. Open Students > New (the DOB field uses the DatePicker) and Billing > run billing / Teacher pay > run payroll (the month field uses the MonthPicker).
| Step | Action |
|------|--------|
| 1 | Open the DOB date picker; read the month/year header and page through a few months |
| 2 | Pick a date (e.g. 3 July 2026) and read the closed field |
| 3 | Open the billing/payroll month picker; read the 12-month grid and the header |
**What you should see**: Month names are Malay: the picker header shows e.g. `Julai 2026`, the month grid runs `Jan Feb Mac Apr Mei Jun Jul Ogo Sep Okt Nov Dis`, and the picked date shows a BM short month (e.g. `3 Jul 2026`). Known limit, NOT a fail for this case: the date picker's weekday header row keeps the two-letter `Mo Tu We Th Fr Sa Su` abbreviations.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: both pickers rendered month names in hardcoded `en-MY` regardless of language; localized via the shared `intlLocale` helper in commit e86b941.

### TC-I18N-010: "Powered by" is translated on the public page and the PDFs
**Tags**: @regression **Severity**: S4 Low | **Priority**: P3 | **Tier**: T3
**Before you start**: An issued invoice's public link, plus operator access in Bahasa Malaysia to download an invoice PDF, a payslip PDF (Teacher pay), and an attendance report PDF.
| Step | Action |
|------|--------|
| 1 | Open the public link with the `/ms/invoice/<token>` path and read the page footer |
| 2 | With BM active, download the invoice PDF, a payslip PDF, and an attendance report PDF; read each footer |
**What you should see**: The footer reads `Dikuasakan oleh Kelasapp` in BM (`Powered by Kelasapp` in EN) on the public page and in all three PDFs; no half-English footer in a BM document.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: "Powered by" was hardcoded English on the public invoice page and the invoice/payslip/attendance PDFs; translated in commit e86b941.

### TC-I18N-011: BM void wording is distinct from cancel
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator in Bahasa Malaysia with an issued, unneeded test invoice (create one via run billing if needed).
| Step | Action |
|------|--------|
| 1 | On the invoice detail, open the void action and read BOTH buttons in the confirm dialog |
| 2 | Void the invoice with a reason |
| 3 | Read the invoice's status chip |
| 4 | Open the invoice's public link with the `/ms/` prefix |
**What you should see**: The confirm button reads `Batalkan invois` while the dismiss button reads `Batal` (two clearly different labels, never two identical "Batal" buttons). After voiding, the status shows `Dibatalkan` (not "Batal"). The public page tells the parent `Invois ini telah dibatalkan. Sila hubungi pusat jika ada pertanyaan.`
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: BM used "Batal" for both the void action and the cancel button, making the destructive dialog ambiguous; fixed in commit 8e3d66d (CX4).

### TC-I18N-012: BM terminology is aligned on the money and auth screens (first-party sign-in)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2
**Before you start**: Signed out. Open `/ms/sign-in`. (The sign-in, sign-up, and forgot-password pages are first-party since the Better Auth migration; there is no third-party hosted widget, so their BM strings come from `ms.json`.)
**Test Data**: operator email `operator@kelastest.local` with a wrong password `wrongpass123`.
| Step | Action |
|------|--------|
| 1 | Read the BM sign-in page: title, field labels, button |
| 2 | Submit the operator email with the wrong password and read the error |
| 3 | Click `Lupa kata laluan?` and read the forgot-password screen |
| 4 | Sign in correctly and read the dashboard KPI tiles in BM |
**What you should see**: Sign-in shows `Log masuk ke Kelasapp`, fields `E-mel` and `Kata laluan`, button `Log masuk`. The wrong password shows `Tidak dapat log masuk. Semak e-mel dan kata laluan anda.` The forgot-password subtitle reads `Kami akan e-mel pautan untuk set kata laluan baharu.` The spelling is `E-mel` everywhere (never "Emel"). The dashboard outstanding tile reads `Belum dikutip` (not "Tertunggak").
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: mixed "Emel"/"E-mel" spellings and the ambiguous "Tertunggak" KPI were aligned in commit b68ac79 (CX10).

## I. PII masking (`SensitiveValue`)

### TC-PII-001: Teacher IC and bank account are masked by default with a reveal toggle
**Tags**: @smoke @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator. Open a teacher who has both an IC and a bank account (Teachers > open one with a complete profile).
| Step | Action |
|------|--------|
| 1 | Read the IC field and the bank account field on the detail page |
| 2 | Click the eye toggle next to the IC |
| 3 | Click it again |
**What you should see**: On first render both show only the last 4 characters with the rest as bullets (e.g. `••••••••5567`); the full number is not printed. Clicking the eye reveals the full value; clicking again re-masks it. The bank account behaves the same.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Finding #3 CLOSED 2026-07-04 (b498d68): masking is now server-side; the page ships only the masked tail and the eye toggle fetches the full value from the operator-gated /api/teachers/[id]/sensitive endpoint (watch the Network tab on reveal). TC-TCH-084 asserts the view-source proof; a full value found in the served page is a regression.

### TC-PII-002: Student IC is masked by default on the student detail page
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: Operator. Open a student who has an IC.
| Step | Action |
|------|--------|
| 1 | Read the IC field on the student detail page |
| 2 | Click the eye toggle to reveal, then again to hide |
**What you should see**: IC shows masked (last 4 only) on first render; reveal shows the full IC; re-toggle re-masks. Never printed in full on initial load.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-PII-003: A short or empty sensitive value renders safely
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2
**Before you start**: Operator. Find or create a teacher with no bank account set (empty), and conceptually a value of <= 4 characters.
| Step | Action |
|------|--------|
| 1 | Open the detail of a teacher with no bank account |
| 2 | Read the bank account field |
**What you should see**: An empty value shows a plain dash (`-`), not bullets and not a crash. A value of 4 or fewer characters shows as all bullets (no characters revealed). No layout break.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## J. PII: what must NOT be masked

### TC-PII-010: The org's receiving account + DuitNow QR are shown in full on the public invoice
**Tags**: @smoke @regression **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1
**Before you start**: An issued invoice with org payment settings configured (bank account + DuitNow QR). Open its public link (incognito, no login).
| Step | Action |
|------|--------|
| 1 | Open the public invoice page |
| 2 | Read the org's bank account number and the DuitNow QR |
**What you should see**: The org's own receiving bank account is shown in full (not masked, no eye toggle) and the DuitNow QR is fully visible and scannable. A payer must be able to read and use them. (Masking here would be a defect.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-PII-011: Phone and email are shown in full to operators (not masked)
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator. Open a teacher, student, or guardian detail with a phone and email on file.
| Step | Action |
|------|--------|
| 1 | Read the phone and email fields on the detail page |
**What you should see**: Phone and email are shown in full with no eye toggle (operators need them to make contact). Only IC/passport and bank account use the masked `SensitiveValue` treatment.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-PII-012: Edit-form inputs for IC and bank account are plain while editing
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Before you start**: Operator. Open a teacher with an IC + bank account and click Edit.
| Step | Action |
|------|--------|
| 1 | Open the teacher edit form |
| 2 | Look at the IC and bank account inputs |
**What you should see**: While editing, the IC and bank account are shown as plain editable inputs (not bullet-masked), so the operator can verify and change them. Masking is a read-only detail-page concern, not an edit-time one.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## K. Responsive (RWD)

### TC-RWD-001: A list table scrolls horizontally on a phone instead of overflowing
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator. Open a wide list (Billing list or Students list). Set the browser/device to 375px wide (iPhone SE).
| Step | Action |
|------|--------|
| 1 | Resize the viewport to 375px wide |
| 2 | Try to read the far-right columns of the table |
**What you should see**: The table scrolls horizontally within its own container; columns are not clipped off-screen and the page itself does not develop a broken double-scrollbar. All columns are reachable by scrolling the table.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-RWD-002: A page toolbar / action bar wraps cleanly at 375px
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Before you start**: Operator on an invoice detail (which has a primary action + share cluster + More menu). Viewport 375px.
| Step | Action |
|------|--------|
| 1 | At 375px, look at the action bar above the invoice |
**What you should see**: The buttons wrap to a second line or collapse into the More (⋯) overflow rather than overflowing horizontally or being cut off. The primary action stays reachable; nothing is hidden under the edge of the screen.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-RWD-003: TimePicker AM/PM is fully visible, not truncated
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator on Classes > New (schedule uses the TimePicker: hour, minute, AM/PM selects). Test at 375px and at desktop width.
| Step | Action |
|------|--------|
| 1 | Open the class schedule time picker |
| 2 | Set the period to PM, then to AM |
| 3 | Read the period select at 375px and at desktop |
**What you should see**: The third select shows the full word: the "M" in "AM" and "PM" is fully visible (not clipped to "A" / "P", not showing an ellipsis). The widened select (`w-20`) holds the whole label at every width. (Regression guard for the AM/PM truncation fix.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-RWD-004: The sidebar collapses to a drawer on mobile
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Before you start**: Operator on the dashboard at 375px.
| Step | Action |
|------|--------|
| 1 | At 375px, look for the main navigation |
| 2 | Open it, pick a section, then close it |
**What you should see**: The desktop sidebar is replaced by a menu/hamburger that opens a drawer; tapping a nav item navigates and the drawer closes. The nav does not eat the whole narrow screen permanently.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-RWD-005: A create form is fully usable at 375px
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator on Students > New at 375px.
| Step | Action |
|------|--------|
| 1 | At 375px, scroll through the whole form |
| 2 | Fill the ID toggle, phone, DOB, and a fee field |
| 3 | Save |
**What you should see**: Every field and the ID toggle stack vertically and stay within the viewport (no horizontal page scroll); labels are not clipped; the Save button is reachable. The form submits successfully on a phone-width screen.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-RWD-006: Side sheets fill the screen at phone width
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator at a 375px viewport. Open a screen that uses a slide-in sheet: Billing > open an issued invoice > Record payment, and Teacher pay > mark a draft payout paid.
| Step | Action |
|------|--------|
| 1 | At 375px, open the Record payment sheet and scroll through it |
| 2 | Fill the amount field and read every label and button |
| 3 | Repeat with the Teacher pay mark-paid sheet |
| 4 | Widen to desktop and open the same sheet again |
**What you should see**: At 375px the sheet covers the full screen width; every field, label, and button fits with no horizontal scrolling and no cropped inputs. At desktop width the same sheet is a side panel (roughly a third of the screen), not full-screen.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: sheets were fixed at 3/4 width, cramping payment forms on phones; made full-width at phone size in commit 8ecc138 (CX9).

### TC-RWD-007: The attendance save row wraps at 375px instead of bursting the card (BM)
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator (or teacher `teacher@kelastest.local` / `password12345`) in Bahasa Malaysia, on the attendance sheet of a class that has enrolled students, viewport 375px. (BM labels are the longest, which is what broke the layout.)
| Step | Action |
|------|--------|
| 1 | At 375px, read the row containing `Tandakan semua hadir` and `Simpan kehadiran` |
| 2 | Check the right edge of the card and try to scroll the page horizontally |
| 3 | Switch to English and re-check (`Mark all present` / `Save attendance`) |
**What you should see**: The header row wraps so the save group drops to its own line inside the card; the `Simpan kehadiran` button stays fully inside the card border and the page has no horizontal scroll, in both languages.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: a non-wrapping flex row pushed the save button 11px past the card border at 375px; flex-wrap added in commit 031eb53.

## L. Accessibility (a11y)

### TC-A11Y-001: Every form field has an associated label
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator on Students > New.
| Step | Action |
|------|--------|
| 1 | Click each field's visible label text |
| 2 | (Optional) Run an axe / Lighthouse accessibility spot-check on the page |
**What you should see**: Clicking a label focuses its input (label `htmlFor` is wired to the field id via the shared `FormItem`/`FormLabel`). No field is unlabeled; the a11y spot-check reports no "form element has no label" violations.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-A11Y-002: The whole form is reachable and operable by keyboard
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator on Students > New. Use Tab / Shift+Tab / Enter / arrow keys only (no mouse).
| Step | Action |
|------|--------|
| 1 | Tab from the first field through every control to Save |
| 2 | Operate the ID-type toggle and the TimePicker selects with the keyboard |
| 3 | Press Enter / Space on Save |
**What you should see**: Tab order is logical top-to-bottom; every field, the IC/Passport toggle buttons, the select dropdowns, and Save are reachable and operable without a mouse. No control is keyboard-trapped or skipped.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-A11Y-003: A validation error is announced to the field, not just colour-coded
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator on Students > New. (Inspect with DevTools or a screen reader.)
| Step | Action |
|------|--------|
| 1 | Enter a bad IC and try to Save |
| 2 | Inspect the IC input's attributes |
**What you should see**: The input gets `aria-invalid="true"` and its `aria-describedby` points at the message element (wired by the shared `FormControl`), so the error is conveyed to assistive tech, not by red colour alone. The message text is present in the DOM.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-A11Y-004: The PII reveal toggle has an accessible label and pressed state
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator on a teacher detail page with a masked IC / bank account. (Inspect the eye button.)
| Step | Action |
|------|--------|
| 1 | Inspect the eye toggle button next to the masked IC |
| 2 | Click it to reveal and inspect again |
**What you should see**: The button has an `aria-label` ("Show" when masked, "Hide" when revealed, from `Common.show` / `Common.hide`) and `aria-pressed` reflecting the state (false then true). It is a real `<button>` reachable by Tab, not a bare icon.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-A11Y-005: The language switcher has an accessible label
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Before you start**: Operator on the dashboard. (Inspect the globe button in the header.)
| Step | Action |
|------|--------|
| 1 | Inspect the globe (language) button |
| 2 | Open it and check the menu items |
**What you should see**: The icon-only globe button carries an `aria-label` (from `LocaleSwitcher.button_label`); the menu is a radio group whose current language is marked selected. It is reachable and operable by keyboard.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-A11Y-006: Visible focus state on interactive controls
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Before you start**: Operator on any form or list. Use Tab only.
| Step | Action |
|------|--------|
| 1 | Tab through inputs, buttons, toggles, and links |
**What you should see**: The currently focused control has a clearly visible focus ring / outline at each stop, so a keyboard user can always tell where they are. No control receives focus invisibly.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-A11Y-007: The status text tokens meet AA contrast in light mode
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2
**Before you start**: Operator in the Light theme on the dashboard and on an invoice detail with an outstanding balance. Optional: axe / Lighthouse contrast scan.
| Step | Action |
|------|--------|
| 1 | Read a success-toned status/money text (e.g. a paid/collected figure on the dashboard or billing) |
| 2 | Read an outstanding (not yet overdue) balance amount on the dashboard and on an invoice detail |
| 3 | (Optional) Run an axe / Lighthouse contrast spot-check on both pages |
**What you should see**: Success text renders as a deep emerald (token `#157F62`, 4.9:1 on white) and warning text as a dark amber ink (token `#B45309`, 4.6:1); outstanding balance amounts use a dark amber, not a pale mid-amber. All pass WCAG AA 4.5:1 for normal text; the axe spot-check reports no contrast violations on these elements.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: The `--success` / `--warning` text-safe tokens landed in the design-system pass (a9737aa, b300923); outstanding amounts moved from amber-600 to amber-700 in commit 4580941.

### TC-A11Y-008: Attendance marking buttons are touch-sized with AA-contrast selected states
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Attendance sheet of a class with students, at a 375px viewport and again at desktop width. (Marking is done one-handed in a classroom.)
| Step | Action |
|------|--------|
| 1 | At 375px, measure (DevTools) or thumb-tap the Present / Absent / Late / Excused buttons |
| 2 | Select each of the four states on a row and read the label against its fill |
| 3 | Inspect a selected button's attributes |
| 4 | Re-check the button height at desktop width |
**What you should see**: At phone width each marking button is 44px tall; at desktop 36px. Selected colours meet AA 4.5:1: `Late` (BM `Lewat`) is dark text on an amber fill, and Present / Absent / Excused are dark solid fills with white text, never white text on a pale mid-tone. The selected button exposes `aria-pressed="true"`; unselected buttons `aria-pressed="false"`.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: buttons were 32px and Late was white-on-amber at 2.3:1; fixed in commit 4580941 (CX8).

## M. Theme (light / dark mode)

New cross-cutting dimension added 2026-07-04 (commit 2a7804c): dark mode is wired app-wide via next-themes. Light is
the default; the choice is per-browser (localStorage key `theme`). Dark tokens live in the `.dark` block of
`src/styles/global.css`.

### TC-THEME-001: Dark mode switches on from the account-menu theme picker
**Tags**: @smoke **Severity**: S3 Medium | **Priority**: P1 | **Tier**: T2
**Before you start**: Log in as operator (`operator@kelastest.local` / `newpassword6789`). App in the default Light theme.
| Step | Action |
|------|--------|
| 1 | Open the account menu (click your avatar in the header, or the user chip at the bottom of the sidebar) |
| 2 | Read the "Theme" group and its three options |
| 3 | Pick "Dark" |
| 4 | Visit the dashboard, Students, and Billing |
**What you should see**: The menu shows a "Theme" label (BM "Tema") with options "Light", "Dark", "Follow device" (BM "Cerah", "Gelap", "Ikut peranti"); the active option carries a check mark on its right. Picking Dark flips the whole app immediately: dark page background, dark cards and tables, light text, dark sidebar. Every dashboard screen follows; no screen stays white.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-THEME-002: The theme choice persists across reload and navigation
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T3
**Before you start**: Operator with Dark picked (TC-THEME-001).
| Step | Action |
|------|--------|
| 1 | Reload the page (F5 / Cmd+R) |
| 2 | Navigate to Classes, Teachers, and back to the dashboard |
| 3 | (Optional) DevTools > Application > Local Storage: read the `theme` key |
**What you should see**: The app stays dark after the reload and on every page; no white flash back to light. The localStorage key `theme` holds `dark`. (The choice is per-browser, not per-account: a different browser/device starts on Light until picked there.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-THEME-003: A fresh browser gets Light even when the device prefers dark
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2
**Before you start**: Set the operating system to dark appearance (macOS: System Settings > Appearance > Dark; Windows: Settings > Personalization > Colors > Dark). Open a fresh incognito/private window (no stored choice).
| Step | Action |
|------|--------|
| 1 | Open the app landing page in the incognito window |
| 2 | Sign in as operator and read the dashboard |
**What you should see**: Landing, sign-in, and the dashboard all render the Light theme (white/pale background, dark text) despite the OS dark preference. Dark is an explicit opt-in from the account menu, never automatic on first visit.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-THEME-004: The public invoice page ALWAYS renders light, even for a dark-mode user
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: An issued invoice's public link. Two checks: (a) an incognito window on a device with OS dark mode ON; (b) the normal browser AFTER picking "Dark" in the account menu.
| Step | Action |
|------|--------|
| 1 | Open the public invoice link in the incognito window |
| 2 | In the normal browser, set the theme to Dark, then open the public link in a new tab |
| 3 | Read the page in both: amounts, bank details, DuitNow QR; then return to the dashboard tab |
**What you should see**: BOTH windows render the light theme (slate wash, white cards, dark readable text, RM amounts, scannable QR). The dashboard tab stays dark: the stored preference is untouched; only the public page pins light (a CSS force-light scope, not a theme change). Reset the theme to Light afterwards.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: the public page used to follow the browser's stored theme (dark for a dark-mode operator); pinned light in 4fe0ace (decided 2026-07-04, browser-verified in dark mode).

### TC-THEME-005: "Follow device" tracks the OS appearance
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Before you start**: Operator on the dashboard.
| Step | Action |
|------|--------|
| 1 | In the account menu's Theme group, pick "Follow device" (BM "Ikut peranti") |
| 2 | Switch the OS to dark appearance, then back to light (macOS: System Settings > Appearance) |
**What you should see**: With "Follow device" checked, the app turns dark when the OS is dark and light when the OS is light, without a reload. The check mark sits on "Follow device".
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-THEME-006: Dark-mode contrast spot-check on key controls
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator in the Dark theme, on Students > New and the dashboard. Optional: axe / Lighthouse contrast scan.
| Step | Action |
|------|--------|
| 1 | Read the primary Save/submit button's label against its fill |
| 2 | On Students > New, read the active segment of the IC / Passport toggle |
| 3 | Read a success-toned figure and an outstanding/warning amount on the dashboard |
| 4 | (Optional) Run an axe contrast scan on both pages in dark mode |
**What you should see**: The primary button is a lighter mint-teal fill with dark ink text (not white-on-mint); the active IC pill's label is clearly legible on its teal fill; success text renders a brighter green and warning/outstanding a lighter amber, both readable on the dark background. The axe spot-check reports no contrast violations on these controls.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: the active ID-type pill hardcoded `text-white`, which the dark-mode token pair breaks; switched to `text-brand-foreground` in commit 135ff13.

## N. Shared list table (all list pages)

The table usability pass (commit 746df0b) applies to every list page (Classes, Teachers, Students, Guardians,
Billing, Pending receipts, Teacher pay), so its behaviours are cross-cutting. Cases pick a representative list;
the same contract holds on the others by inheritance.

### TC-TBL-001: The # column numbers rows Excel-style and renumbers with the view
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Before you start**: Operator on the Students list with more than 25 students (add test students if the dev DB has fewer, or use whichever list has the most rows).
| Step | Action |
|------|--------|
| 1 | Read the leftmost `#` column on page 1 |
| 2 | Go to page 2 and read the first row's number |
| 3 | Click the Name header to reverse the sort and re-read the column |
| 4 | Type a search that matches a few rows |
**What you should see**: Page 1 numbers rows 1-25 top to bottom; page 2 starts at 26. After re-sorting, the numbers still read 1, 2, 3... by position (they do not travel with the moved rows). A filtered view renumbers from 1. The `#` column is narrow and right-aligned.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TBL-002: Global search matches any column, not just the name
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T2
**Before you start**: Operator on the Students list. Open any student who has a phone number and note the digits (e.g. `0123456789`); go back to the list.
| Step | Action |
|------|--------|
| 1 | Type that phone number into the list's search box |
| 2 | Read the rows and the count under the table |
**What you should see**: The student's row is found by the phone number (a non-name column). The count updates to the filtered range, e.g. `1-1 of 1` (BM `1-1 daripada 1`). Clearing the search restores all rows.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TBL-003: A column whose first row is blank still participates in search
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator on the Students (or Guardians) list arranged so the FIRST row has an empty phone cell and a LATER row has a phone. If needed, create two records: `Aisyah binti Kamal` with no phone, and `Badrul bin Osman` with phone `019-876 5432`; sort by name ascending so Aisyah is row 1.
**Test Data**: search `0198765432`.
| Step | Action |
|------|--------|
| 1 | Confirm the first visible row's phone cell is empty |
| 2 | Type `0198765432` into the search box |
**What you should see**: Badrul's row matches even though the first row's phone is blank. A column with a gap in row 1 is never silently dropped from the search.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: the table library's default column probing skipped any column whose first-row value was null, so phone columns with a blank first row fell out of global search entirely; fixed with a null-safe filter in commit 746df0b.

### TC-TBL-004: Filtering to zero rows offers a one-click reset
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T3
**Before you start**: Operator on any list page that has rows.
**Test Data**: search `zzzz-no-match`.
| Step | Action |
|------|--------|
| 1 | Type `zzzz-no-match` in the search box |
| 2 | Read the table body |
| 3 | Click the reset button shown in the body |
**What you should see**: The body shows `No matches for your search or filters.` (BM `Tiada padanan untuk carian atau tapisan anda.`) with a `Reset` (BM `Set semula`) button under it; NOT the module's rich "no data yet" empty state. Clicking Reset clears the search box and any faceted filters, and all rows return.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TBL-005: Rows-per-page defaults to 25 and the choice is remembered everywhere
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Before you start**: Operator in a browser where the app has not had its rows-per-page changed (or clear the `kelasapp.rows-per-page` localStorage key first).
| Step | Action |
|------|--------|
| 1 | Open the Students list and read the rows-per-page select |
| 2 | Change it to 50 |
| 3 | Reload the page and re-read the select |
| 4 | Open the Teachers list and read its select |
**What you should see**: The default is 25 and the options are 10 / 25 / 50 / 100. After picking 50, both the reload and the Teachers list show 50: one shared per-browser preference (localStorage key `kelasapp.rows-per-page`), not a per-table setting.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TBL-006: CSV export downloads the current view with on-screen labels
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator on the Students list at desktop width (the export button hides on small screens). Have at least one student whose name contains a non-ASCII character (e.g. `Nur'ain binti Zulkifli`).
| Step | Action |
|------|--------|
| 1 | Apply a search that narrows the list to a subset |
| 2 | Click `Export CSV` (BM `Eksport CSV`) |
| 3 | Open the downloaded file in Excel |
**What you should see**: A file named like `students-2026-07-04.csv` (today's date) downloads. The header row uses the on-screen column labels in the active language, not internal field ids. The rows are exactly the filtered + sorted view across ALL of its pages; hidden columns and the `#` / actions columns are not exported. Names with apostrophes/Malay characters open correctly in Excel (no mojibake).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-TBL-007: The pagination footer keeps a gap between its two halves (BM)
**Tags**: @regression **Severity**: S4 Low | **Priority**: P3 | **Tier**: T3
**Before you start**: Operator in Bahasa Malaysia on any list with rows. Narrow the window until the count, the rows-per-page control, and the page buttons sit close together.
| Step | Action |
|------|--------|
| 1 | Read the strip under the table at several window widths |
**What you should see**: `Baris per halaman` and `Halaman X daripada Y` render as separate labels with visible spacing at every width; they never run together as `Baris per halamanHalaman 1 daripada 3`.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: the footer's flex container had no gap, gluing the two BM labels together; `gap-4` added in commit 135ff13.

### TC-TBL-008: List tables carry no selection checkboxes, except Teacher pay bulk mark-paid
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3
**Before you start**: Operator with a few draft payouts generated (Teacher pay > run payroll for a month with attendance).
| Step | Action |
|------|--------|
| 1 | Open the Students, Classes, Teachers, Guardians, and Billing lists; look at the leftmost columns |
| 2 | Open Teacher pay and look at the draft payout rows |
| 3 | Tick two draft payouts |
**What you should see**: Students/Classes/Teachers/Guardians/Billing show NO checkbox column (the `#` column is leftmost). On Teacher pay, draft rows do have checkboxes; ticking some shows the bulk action `Mark paid (2)` (BM `Tandakan dibayar (2)`). That is the one intended selection use; a checkbox that drives no action anywhere is a defect.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: dead selection checkboxes that drove no action were removed in commit df2e3f1 (CX6); payroll selection returned purposefully with bulk mark-paid (ab86cf3, CX11).

## O. Feedback (toasts and loading states)

Success toasts on entity save/archive landed app-wide in commit 6e45620; failed actions surface an error and the
public invoice gained a loading skeleton in commit 31777bd.

### TC-FDBK-001: Saving an entity confirms with a success toast
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator on Students > New (or edit an existing student).
| Step | Action |
|------|--------|
| 1 | Fill the form with valid data and Save |
| 2 | Watch the corner of the screen after the redirect |
**What you should see**: A toast appears reading `Student saved` (BM `Pelajar disimpan`) and fades on its own. The same pattern holds app-wide: `Class saved` / `Kelas disimpan`, `Teacher saved` / `Guru disimpan`, `Guardian saved` / `Penjaga disimpan`. A silent save with no confirmation is a fail.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-FDBK-002: Archiving from the row menu confirms, then toasts
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator on the Classes list with a disposable test class.
| Step | Action |
|------|--------|
| 1 | Open the row's kebab (⋯) menu and pick Archive |
| 2 | Read the confirm dialog, then confirm |
**What you should see**: A confirmation dialog appears first (title + consequence text + `Cancel` / BM `Batal`). On confirm, the dialog closes, a toast reads `Class archived` (BM `Kelas diarkibkan`), and the list refreshes without the archived class.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-FDBK-003: A failed action shows an error in the dialog, never a silent success
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2
**Before you start**: Operator with one issued, disposable invoice. Open the SAME invoice detail in two browser tabs (deterministic server failure: the second void hits an already-voided invoice).
| Step | Action |
|------|--------|
| 1 | In tab 1, void the invoice with a reason and confirm it succeeds |
| 2 | In tab 2 (still showing the stale issued state), open the void action and confirm it |
**What you should see**: In tab 2 the confirm dialog STAYS OPEN and shows the red error `That did not work. Please try again.` (BM `Itu tidak berjaya. Sila cuba lagi.`). No success toast fires for the failed attempt, and after refreshing, the invoice shows the single void from tab 1.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: destructive actions fired their API call without checking the response, so failures looked identical to success; surfaced in commit 31777bd. Since c679357 (2026-07-04) a thrown fetch (true network drop, DevTools offline) is also caught in the shared dialog with the same message; offline mode is a valid alternative trigger.

### TC-FDBK-004: The public invoice shows a skeleton while loading, not a blank page
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2
**Before you start**: An issued invoice's public link. DevTools > Network tab > throttling set to "Slow 3G". Open the link in an incognito window (parents open these from WhatsApp on slow mobile connections).
| Step | Action |
|------|--------|
| 1 | With throttling on, open the public invoice link |
| 2 | Watch the first seconds before the content arrives |
**What you should see**: Grey placeholder blocks appear immediately, mirroring the final layout (centre logo block, an amount card, a pay section), then the real invoice replaces them. The page is never a plain blank white screen while the server resolves the invoice and the signed logo/QR URLs.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: slow connections showed a white screen until the server responded; `loading.tsx` skeleton added in commit 31777bd.

## Coverage note
Techniques walked (per QA-METHODOLOGY §5): format/locale (the whole catalog: IC/passport, phone, bank, money, DOB, RM,
DD/MM/YYYY, Asia/KL, EN+BM; picker month names I18N-009; PDF footers I18N-010; BM terminology I18N-011/012), equivalence +
boundary (VAL-005 length, VAL-031 5/20 digits, VAL-041 >2dp, VAL-052/053 date bounds, PII-003 <=4-char value),
negative/validation (VAL-003/004/011/021/041/042/043/051/052/053/060), server-side bypass (VAL-022/032/044/062), happy
path (VAL-001/010/020/030/040/050, PII-001/010, I18N-001, THEME-001, TBL-001/002/005/006, FDBK-001/002), state-transition
(VAL-012 toggle re-normalise, PII-001/002 reveal/hide, THEME-001/002/005 theme lifecycle), i18n (all I18N-*), key parity
(I18N-007), data integrity (VAL-041/042/044/062, I18N-003, TBL-006 export matches view), security/PII exposure
(PII-001/002 masking + PII-010/011 deliberate non-masking, VAL-022/032/044/062 server gate), accessibility (all A11Y-*,
incl. A11Y-007 light-token contrast and A11Y-008 touch targets; THEME-006 dark-mode contrast), responsive (all RWD-*),
error/empty/loading states (TBL-004 filter-miss reset, FDBK-003 failure surfacing, FDBK-004 loading skeleton),
concurrency (FDBK-003 stale-tab double-void).
2026-07-04 update: 26 cases added (I18N-009..012, RWD-006/007, A11Y-007/008, THEME-001..006, TBL-001..008,
FDBK-001..004), TC-I18N-008 and TC-PII-001 rewritten in place (regression provenance e86b941; README finding #3
annotation), header + smoke subset updated (52 -> 78 cases, 7 -> 9 @smoke). **No cases deleted.** Regression provenance
in this file: 746df0b (null-first-row search), 135ff13 (pagination glue + dark pill), 031eb53 (attendance save overflow),
4580941 (touch size + AA), 8ecc138 (phone-width sheets), e86b941 (picker/sidebar/Powered-by i18n), 8e3d66d (BM void),
b68ac79 (BM terms), 31777bd (failure surfacing + skeleton), df2e3f1 (dead checkboxes).
Not walked here, by design: cross-tenant/IDOR and permissions/role (covered per-module, e.g. test-plan-billing §K), XSS in
rendered free text (covered where input hits render, e.g. TC-BILL-042), file-type validation (TC-BILL-025/092). Clerk no
longer exists anywhere in the product (Better Auth migration, Jul 2026); the first-party auth screens are exercised here
for i18n (I18N-012) and owned functionally by test-plan-auth-tenancy. These cross-cutting cases assume the per-module
catalogs own those rows; this file owns the input/locale/PII/theme/table/feedback/responsive/a11y rows that repeat on
every screen. Non-functional (perf, axe full-page audit at scale) is tracked separately, not in this functional catalog.
