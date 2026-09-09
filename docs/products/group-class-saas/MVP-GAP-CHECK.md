# Kelasapp — MVP Gap Check (2026-07-02)

Purpose: determine what's left to "finish the MVP" before the test/E2E phase and the Sopan private beta (migrating from Mudeer). Method: PRD + BUILD-LOG review + three parallel read-only code audits (billing/payments, attendance/payroll, onboarding/settings/CRUD/cross-cutting), reconciled against each other.

## Verdict

**No functional blockers. The MVP runs end-to-end.** M1-M6 + cross-cutting (roles, tenant isolation, i18n EN/BM parity, empty states) are built, wired, and largely tested. The one unbuilt module is **M7 AI** (a post-core differentiator). What remains is a small set of scope decisions + minor polish, not core features.

## Confirmed complete (built + wired, cross-verified)

- **M1 Classes** — CRUD, schedule, program/level/teacher, fee + teacher rate, roster
- **M2 Students / Guardians / Enrolments** — CRUD, level history, global search, enrol from both sides, fee override, mid-join note
- **M3 Attendance** — take attendance (lazy sessions, one-tap, mark-all, notes, 7-day window, KL timezone), admin dashboard (today summary, per-class rate, absence alerts), reports (per-student/class, PDF + CSV, trend chart)
- **M4 Billing** — run billing (family invoices, idempotent), lifecycle (draft→issue→partial→paid→void), manual payments (cash/bank/duitnow/other), partial payments, refunds (with/without reduce), discounts/adjustments/credits, **public payment page + self-service receipt upload + operator verification queue**, WhatsApp click-to-chat, copy link, invoice PDF. Money math is cents-based, idempotent, and tested. No dead-ends.
- **M5 Teachers + Payroll** — teacher CRUD (grade, bank, PII masking), teacher login (Clerk member linked by email), **payroll run (draft/paid/void, idempotent), typed adjustments, payslip PDF** — all wired under `/dashboard/payroll`
- **M6 Operator Dashboard** — KPI cards, billed-vs-collected chart, recent payments, absence + unpaid action queues, **class-health grid**, getting-started checklist
- **Cross-cutting** — 3-role model (operator/staff/teacher) with page + API gating, tenant isolation, EN/BM parity, actionable empty states, branded error/404 pages, security headers, payment idempotency

## Gaps — scope decisions (define "MVP finish" here)

| # | Gap | Impact | Recommendation |
|---|-----|--------|----------------|
| D1 | **M7 AI Layer not built** | The one unbuilt module. Differentiator, not required to run a centre. | **Defer to post-beta.** Not needed for Sopan. |
| D2 | **No class / enrolment CSV import** — importer covers students/teachers/guardians only. Sopan must create classes + enrolments manually (~60-90 min for a real centre). | Biggest Sopan-migration friction. Not a functional blocker (manual pages work). | **Decide:** build a lightweight class + enrolment importer (extends the Wave 4 importer), or accept manual setup for Sopan. Depends on how many classes/enrolments he has. |
| D3 | **Teacher self-service payslip + "my classes"** — payslip PDF is operator-only; teachers can't view own payslips or their schedule outside the attendance page (PRD M5-US8/AC4). | Real MVP requirement; teachers already log in. | **DECIDED 2026-07-02: build it.** Add own-payslip view + teacher payout list + `/dashboard/my-classes`. |

## Should-fix (small, batch before Sopan)

- **Grade history not written** — `teacher_grade_history` table exists but `updateTeacher` never writes to it (R5.13). Small.
- **ClassForm teacher prerequisite hint** — if no teachers exist, the teacher dropdown is empty with no "create one first" link (EnrollPanel does this well). Small UX.
- **Payroll empty state** — `/dashboard/payroll` shows a bare empty table when no payouts for the month; add an empty-state message. Trivial.
- **Remove/replace receipt on a payment** — if an operator attaches the wrong receipt, there's no way to correct it except reject + resubmit. Small.

## Minor / post-beta (defer)

- Bulk-verify pending receipts (currently one-at-a-time); in-UI audit-log viewer (data exists in `invoiceEvents`); cap/guard on adjustment amount (fat-finger)
- Auto-billing cron (deferred by design; manual "Run billing" is cron-ready)
- Bulk enrolment; class duplication/template; multi-teacher-per-class UI (schema ready)
- Import extras: gender/DOB columns, student↔guardian linking, class-health *badge on the class list* (grid exists on dashboard), pause-a-class UI

## Corrected agent errors (already built — not gaps)

- Self-service receipt upload + verification queue → **built** (M4 slice 1.5, 2026-06-28)
- Payroll UI + sidebar link → **built and wired** (`/dashboard/payroll`, "Teacher pay" nav)

## Suggested "finish MVP" shortlist (for approval)

1. **Build class + enrolment CSV import** (D2) — the highest-value item for a clean Mudeer migration.
2. **Batch the 4 should-fix polish items** — grade history, ClassForm hint, payroll empty state, remove-receipt.
3. **Build teacher self-service** (D3, DECIDED) — own-payslip view + teacher payout list + `/dashboard/my-classes`.
4. **Confirm D1** (M7 AI) stays post-beta.

Then freeze → revisit the 486-case QA catalog → full E2E → fix → manual QA → hand to Sopan.
