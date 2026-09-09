# Kelasapp — External Audit: Design, UX, Flows, Customer Experience (2026-07-03)

> The product-side counterpart to MVP-READINESS.md (which covered code). Method: 4 parallel
> code-side auditors (flow friction, design consistency, a11y/mobile, copy & tone in EN+BM)
> + a hands-on visual walkthrough of all three personas at phone size (375px) and desktop
> + Lighthouse. Scope: what Sopan, his teachers, and parents will actually see and feel.
> Already-parked items excluded (marketing copy reframe, fake logo marquee, brand palette).

## Resolution status (final - 2026-07-03)

**ALL 16 findings + the LOW batch are closed.** Everything on `feat/finish-mvp-polish`,
151 unit tests green, every change browser-verified (real 375px emulation where relevant).

**HIGH:** CX1 `917c612` · CX2 `de4be04` · CX3 `998a2b5` (true bulk-send deferred - WhatsApp
policy) · CX4 `8e3d66d`.

**MEDIUM:** CX5 `6e45620` · CX6 `df2e3f1` (checkboxes removed; selection returned with CX11)
· CX7 `1ee30f4` · CX8 `4580941` · CX9 `8ecc138` · CX10 `b68ac79` · CX11 `ab86cf3` (bulk
mark-paid: draft-only selection, one method+date sheet, per-teacher failure report, each
payout through the tested single endpoint) · CX12 `63c3365` (checklist pull-through via
?from=onboarding + enrol step deep-links to the first class) · CX13 `a9737aa` (shared
statusTones module, --success token, billing/payroll empty states) + `ebb792c` (settings
forms on Form primitives with inline zod validation) · CX14 `2a7804c` (dark mode wired:
next-themes, account-menu picker Cerah/Gelap/Ikut peranti, light default for public pages;
dark sweep found + fixed washed-out selected attendance buttons) · CX15 `390b663`
(Cara-bayar fallback when the org has no payment method) · CX16 `8da4c9e` (migration hub
/dashboard/import: five wizards in dependency order with live tenant-scoped counts +
checklist entry point).

**Table-usability build (Hafiz's follow-up ask):** `746df0b` central pass (# column, range
count, search-all-columns, filter-miss reset, 25 rows remembered, CSV export) + `b98afe1`
guardians children count + `5cc82b9` teachers class count + `b4faa68` students enrolled
classes.

**LOW batch:** `b691bbc` RM0 fee warning · `6e2b993` Enter submits the public receipt form ·
`6974f69` five dead template locale namespaces deleted · `b6f474d` Members icon +
sentence-case titles.

**Accepted debt (consciously deferred):** true bulk WhatsApp send (needs Business API /
finch-lite) · parent notify-on-verify (messaging infra) · DatePicker arrow-key grid ·
FileButton label wiring · prefers-reduced-motion on the marketing marquee · billing header
button-size + heading-size nits.

## Verdict

**The product reads as one coherent, carefully built system — and the three persona cores are
genuinely good.** The teacher's attendance screen is excellent on a phone (2×2 tap grid, mark-all,
inline saved). The parent invoice page is clean, mobile-first, and scores Lighthouse 98
accessibility. The design system is real (shared TitleBar/DataTable/StatusBadge/EmptyState/tokens,
consistent status colors everywhere, coherent PDFs). EN/BM key parity is exact.

**The gaps are not visual — they are feedback loops.** The app does things correctly but often
doesn't *tell anyone*: parents don't know their receipt was received; operators don't know
receipts are waiting; forms save without saying "saved"; six tables show checkboxes that do
nothing. Plus one BM money-dialog bug and a cluster of BM terminology drift.

Lighthouse: public invoice (mobile) A11y **98** / BP 96 / SEO 91 · dashboard A11y **94** / BP 96.

---

## HIGH — the four findings that shape beta trust

### CX1 — A returning parent has no idea their receipt was received (double-pay risk)
The "thank you" after upload is only in-memory; on reload/revisit of the WhatsApp link, a parent
with a **pending** claim sees the same "you owe RM X, upload receipt" screen — zero acknowledgement
(`invoice/[token]/page.tsx` branches only on paid/voided; pending is invisible). And when the
operator verifies/rejects, **nothing** notifies the parent. Risk: re-upload, re-pay, or a confused
WhatsApp message to the centre. Fix: a "Receipt received — pending confirmation by the centre"
state on the public page when an unverified claim exists (+later: notify on verify).

### CX2 — The operator has no ambient signal that receipts are waiting
A submitted claim is only discoverable via the "Pending (N)" link *on the billing page itself*.
The dashboard (KPIs, queues, alerts) has **no "receipts to verify" card**; no header/sidebar badge.
Claims can sit for days while the parent is being chased (compounding CX1). Fix: dashboard card +
sidebar badge on Billing.

### CX3 — Sending/chasing invoices is one-at-a-time (30 taps for 30 families)
WhatsApp/copy-link live only on each invoice's detail page. The billing LIST has no per-row share,
no bulk send, and after "Issue all" nothing suggests sending. Chasing overdue = same loop. This is
the operator's biggest monthly-loop cost. Fix: per-row WhatsApp/copy on BillingTable + a "send
them now" prompt after Issue all (+wire the dead checkboxes into "remind selected" later).

### CX4 — BM void dialog: confirm and cancel both say "Batal"
`Invoicing.void` = "Batal" and `Common.cancel` = "Batal" — the void-invoice dialog (a money
action) renders two identical buttons. A BM operator cannot tell which button destroys the
invoice. Fix: confirm = "Batalkan invois", dismiss = "Kembali"; `Payroll.status_void` →
"Dibatalkan".

---

## MEDIUM — friction a beta user will notice

- **CX5 — No success feedback on create/edit.** All CRUD forms silently redirect; the app has NO
  toast system at all (no sonner/toaster dependency). Attendance/settings already show inline
  "Saved" — apply that pattern (or add a toaster) to the entity forms.
- **CX6 — Dead selection checkboxes** on 6 tables (students/guardians/classes/teachers/billing/
  pending): selecting does nothing. Remove `enableSelection` or wire real bulk actions.
- **CX7 — Teacher "My Pay" doesn't show paid/unpaid status** — the one question the page exists
  to answer (`my-pay/page.tsx` renders month + amount + download only).
- **CX8 — Teacher-phone ergonomics bundle:** attendance status buttons are 32px tall (h-8 →
  ~h-11), no `aria-pressed` on the selected status (screen-reader gap), and selected "Late"
  is white-on-amber-500 (~2.1:1 contrast, fails AA). Also `text-amber-600` balances (~3.3:1).
- **CX9 — Mobile form ergonomics:** the record-payment/adjustment Sheet is 75% width (~281px) on
  phones (→ `w-full sm:max-w-sm`); ClassForm's schedule row doesn't wrap at 375px (fixed-width
  day+time selects overflow → add `flex-wrap`).
- **CX10 — BM terminology normalisation pass** (one sitting, locales only):
  "Tertunggak" means BOTH outstanding and overdue (different money states); "pending" rendered 4
  ways incl. wrong "Jemputan tertunggak"; pengebilan/bil drift; pembayaran/bayaran drift;
  Emel/E-mel/e-mel (DBP: e-mel); Diarkibkan/Diarkib; centre vs organisation; EN enrol/enroll split;
  "Every learner at your center" (learner+center); **"Resit (pilihan)" on the public form but the
  receipt is REQUIRED** (label borrowed from operator dialog); `err_wrong_state` too vague where
  cause is known; "log audit" jargon in void dialog; `voided_msg` gives the parent no next step;
  Validation hints say YYYY-MM-DD (house rule is DD/MM/YYYY — confirm input context);
  bank placeholder shows spaces while the hint says no spaces; BM placeholder domain
  example.com vs contoh.com.
- **CX11 — Payroll has no bulk "mark paid"** — 10 teachers = 10 open→mark→back cycles (billing
  at least has "Issue all").
- **CX12 — Getting-started checklist doesn't pull through:** forms redirect to lists, never back
  to the dashboard, so the user never sees their tick; the "enrol" step links to the students
  LIST, not an enrol action.
- **CX13 — Design-token cleanups:** add a semantic success token (green is hand-rolled in 3
  shades across 7 files); rebuild the 3 settings forms on the shared Form primitives; rich
  EmptyState for billing/pending/payroll lists; centralize the ~8 copy-pasted STATUS_TONE maps.
- **CX14 — Dark mode is fully authored but unreachable** (complete `.dark` token set + dark:
  variants everywhere, but no ThemeProvider/toggle — dead code). Decide: wire next-themes + a
  toggle, or delete the dark styles.
- **CX15 — "Cara bayar" renders an empty section** when the org hasn't set bank/QR — a parent
  sees a heading promising payment instructions with none. Add a fallback line ("Contact the
  centre for payment details").
- **CX16 — Migration has no guided hub:** 5 separate import wizards with an implicit order
  (students/guardians/teachers → classes → enrolments). Sopan must know the sequence. A simple
  ordered checklist page would de-risk migration day.

## LOW (batch later)
Enter-to-submit missing on non-form panels (public payment form included); monthlyFee defaults to
0 with no positive-value warning (RM0 invoices possible); DatePicker keyboard = tab-through-42-days
(no arrow-key grid) and day buttons announce only the number; FileButton Label points at a hidden
input; no prefers-reduced-motion (marketing marquee); `Users` icon reused for students AND members;
billing header buttons size-sm vs default elsewhere; sub-section heading sizes vary; Title-Case
outliers ("User Profile", "Organisation Settings"); template leftovers (PricingFeatures storage/
transfer strings; SponsorLogos) — confirm unused and delete.

## What is genuinely GOOD (protect these)
Teacher flow end-to-end (role-gated, attendance-first, no operator leakage); attendance marking UX;
the parent page's mobile layout (fluid, no fixed widths, big touch targets); sign-up → centre in
one field; Generate → Issue-all with real counts; payment-settings care (QR validate/redraw/
confirm); the import wizard itself (template, auto-map, preview, warnings); verify/reject in
context; inline "add a class first →" affordances; date defaults to today everywhere; every big
list has search; form values survive errors; icon/status/PDF consistency; exact EN/BM parity.

---

## Suggested batching (for the one-by-one decisions)

1. **Feedback-loop batch (CX1+CX2+CX3+CX4)** — the four HIGHs; parent trust + operator daily loop. ~4-5h.
2. **Teacher/phone batch (CX8+CX9+CX7)** — bigger buttons, contrast, aria-pressed, full-width sheets, schedule wrap, My Pay status. ~2h.
3. **Copy batch (CX10)** — one locales-only normalisation pass + the required-receipt label. ~1.5h; then a 1-2h native-speaker BM sweep pre-beta.
4. **Flow-polish batch (CX5+CX12+CX15)** — saved feedback, checklist pull-through, Cara-bayar fallback. ~2-3h.
5. **Structural decisions (CX6, CX11, CX13, CX14, CX16)** — each needs a decision (wire vs remove checkboxes; bulk pay; token cleanups; dark mode fate; migration hub). Discuss individually.
