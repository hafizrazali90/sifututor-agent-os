# Kelasapp UI Conventions

Shared UI rules for the whole dashboard. Apply to current and future modules.

## Action bars and action menus

Never render a long inline row of equal action buttons (a "wall"). Group by intent and push rare/destructive actions into an overflow menu.

**Rules**
1. **Primary action**: the single most likely next step is one filled button, leftmost.
2. **Common secondary actions**: outline buttons, grouped by intent (e.g. a "send to customer" cluster: copy link, WhatsApp, PDF).
3. **Rare or destructive actions** (delete, archive, void, refund): inside a **"More" (⋯) overflow dropdown**. Destructive items are red (`text-destructive`) and separated from the rest by a divider. Never a bare destructive button sitting inline among many actions.
4. **Destructive actions always confirm** (AlertDialog) before running.
5. **Table rows**: actions live in a trailing **kebab (⋯) menu**, not a row of inline buttons.
6. **Threshold**: up to ~2 actions may sit inline; **3 or more** (or any destructive mixed among others) must use primary + group + overflow.

**Why**: a 7-button inline invoice bar read as a wall and put a destructive "Void" one mis-click away. This matches Stripe / Xero / QuickBooks invoice screens.

**Reference implementations**
- Detail-page action bar (primary + share cluster + More menu): `src/features/invoicing/InvoiceActions.tsx`
- Table-row kebab menu: `src/features/ui/RowActions.tsx` (shared; pass a list of link / action / confirm items)

**Primitives**: `dropdown-menu` (overflow + kebab), `alert-dialog` (confirms), `sheet` (forms in a side panel).

## File uploads

Never expose the native `<input type="file">` ("Choose File / No file chosen"), it is unstyled and inconsistent across browsers. Use the shared `src/features/ui/FileButton.tsx`: a styled button triggers a hidden input, the chosen file name shows beside it with a clear (x), and a short helper (file types) shows when empty. The parent owns the `File` and passes translated copy. For a single existing image (QR, future logo), show the image preview above and label the button "Replace ..." instead of "Upload ...". Used by the DuitNow QR upload and both receipt uploads.

## Sensitive data (PII / financial)

Mask sensitive identifiers by default and reveal only on a deliberate user action, the "show password" pattern banks/fintech use. Use the shared `src/features/ui/SensitiveValue.tsx`: it shows the last 4 characters with the rest as bullets and an eye (Eye / EyeOff) toggle to reveal the full value. Never print these in full on initial render.

**Apply to**: IC / passport (NRIC) and bank account numbers. Currently used on the teacher and student detail pages.

**Do NOT mask**: the org's own receiving bank account / DuitNow QR on the public invoice (the parent must see it to pay), and phone / email (operators need them to make contact). Edit-form inputs stay plain while actively editing.

**Why**: NRIC and bank numbers are high-value PII; showing them only on demand limits shoulder-surfing and accidental exposure while keeping them one click away for staff who need them.

**Known limitation (accepted, decided 2026-06-30)**: the masking is display-only. The full value is sent to the browser and is recoverable by a technical user (dev tools / view source); the mask prevents accidental / over-the-shoulder exposure, not access by someone who can already load the page. This is acceptable because only operator + staff reach these pages and both are authorised to reveal the value anyway (no role can see the page but not the PII). Revisit with server-side redaction only if such a role is introduced.

## Input validation

Validate every user input from one shared Zod schema (the form's `zodResolver` and the API's `safeParse` use the same schema, so client + server agree). Shared validators live in `src/utils/validators.ts`.

- **Malaysian formats:** IC (`isValidMyIc`: 12 digits + valid birth date + state code), phone (`normalizeMyPhone`: mobile + landline + `+60`), bank account (digits, 5-20). MyKad has no checksum digit, so format + date + state code is the maximum sensible depth.
- **IC / passport** uses the `IdNumberField` toggle (`src/features/ui/IdNumberField.tsx`): an ID-type selector + one value input whose validation switches by type. IC mode auto-dashes; passport mode is loose (6-12 alphanumeric, never strict-regex foreign passports). The `idType` is form-only and stripped before the request; the API accepts either type as a backstop.
- **Money** uses `money()` / `max2dp` (at most 2 decimal places). **Dates** that must be in the past (DOB) use `isValidPastDate`.
- **Strictness:** hard-block deterministic format errors; if you ever add a heuristic check (e.g. IC gender digit vs the gender field), make it a soft warning, not a block.
- **Messages are bilingual.** Schema messages are i18n keys in the `Validation` namespace (en.json + ms.json); the shared `FormMessage` translates them (legacy English strings fall through untouched). Never hardcode an English validation message in a new schema.

## Formatting

ALL user-facing dates, times, and money go through `src/utils/Format.ts`. Never `en-US`, never a raw `toLocaleDateString` / `Intl` in a feature (computing a canonical value like a `YYYY-MM` key is fine; *displaying* is not). There is ONE canonical set of Malaysia-friendly variants; pick the variant by usage (multiple formats is intentional, not inconsistency):

| Variant | Output | Helper | Use for |
|---|---|---|---|
| Date, numeric | `01/06/2026` | `formatDate` | on-screen tables, lists, compact UI |
| Date, long | `1 Jun 2026` | `formatDateLong` | printed/exported docs: reports, payslips, invoices |
| Date + time | `01/06/2026, 8:00 PM` | `formatDateTime` | timestamps (created / paid at) |
| Time | `8:00 PM` | `formatTime` | class schedule + session times (12-hour) |
| Month + year | `June 2026` | `formatMonth` | billing month / payroll period headings |
| Month, short | `Jun` | `formatMonthShort` | chart axes (compact) |
| Money | `RM1,234.50` | `formatMoney` | all amounts |
| Money, short | `RM1,235` | `formatMoneyShort` | chart axes, KPI cards |

Rules: dates day-first (never US month-first); times 12-hour in Asia/Kuala_Lumpur; money is RM (never "MYR"). Locale `ms` renders Bahasa month names. If a new display need appears, add a named helper here, do not inline a format.

## Copy

No em dashes anywhere in UI copy (use commas, colons, parentheses, or rewrite). Product name is always "Kelasapp".

## Bilingual

Every screen is built bilingual (EN + BM) from the start via next-intl; add keys to both `en.json` and `ms.json` (use `scripts/i18n-add.cjs`). No hardcoded user-facing strings.
