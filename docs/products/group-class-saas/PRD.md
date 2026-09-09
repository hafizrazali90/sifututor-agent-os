# Kelasapp — Product Requirements Document (MVP)
**Product:** Kelasapp (`kelasapp.learnestlab.com`)
**Status:** In build — M1, M2, M3, M5 + Taxonomy shipped; M4, M6, M7 pending
**Last updated:** 2026-06-27 (as-built reconciliation)
**Author:** Hafiz (CTO) + Claude Code
**Scope:** MVP — enough to migrate Sopan off Mudeer and onboard 10 operators

> **Auth updated 2026-07-02:** Clerk → Better Auth (self-hosted organisation plugin;
> assigned operator/staff/teacher roles; users live in our own Postgres; no per-MAU cost;
> no admin/member inference). Deployed live in private Beta 2026-07-05.

> **Reading this in 2026-06-27 or later:** each shipped module has an **"As built"** block at the end of its
> section that is authoritative for what actually exists; where it conflicts with an original requirement, the
> requirement is marked **(SUPERSEDED)**. The full decision log with dates and rationale lives in
> **BUILD-LOG.md** (same folder). Product name is **Kelasapp** (the older "Kelas" in this doc means the same product).

---

## Build status (as-built, 2026-06-27)

| Module | Status | Key deltas from original spec (see the module's "As built" block) |
|---|---|---|
| Foundation (Clerk multi-tenancy, dashboard shell) | ✅ Shipped | Roles are **Operator / Staff / Teacher** (app-level over Clerk admin/member), not owner/admin/teacher/viewer |
| Taxonomy (Programs + Levels) | ✅ Shipped (new, not in original PRD) | Org-managed Programs + Levels for categorising/filtering classes |
| M1 Class Management | ✅ Shipped | `classType` is a fixed preset (no online/physical there); **lazy** sessions (not pre-generated); single teacher at class level (M:N foundation); class **health badge not built yet** (lives with M6) |
| M2 Student Management | ✅ Shipped | **Guardian is a separate entity** (not student fields); enrollments with fee override + mid-join note |
| M3 Attendance | ✅ Shipped | Lazy sessions; teacher accounts; admin dashboard (rate + absence alerts); reports + **server PDF/CSV** + trend chart; auto-attendance (Meet/Zoom) is Phase 2 |
| M5 Teacher Management | ✅ Shipped (profile) | **Pay is on the class** (`teacherRatePerSession`), not per-teacher rates; pay calculation / pay slips **not built** (with M4) |
| M4 Billing & Invoicing | ⏳ Not built (next) | Will reuse the M3 server-PDF pipeline for invoices |
| M6 Operator Dashboard | ⏳ Not built | Class-health grid lives here |
| M7 AI Layer | ⏳ Not built | — |

Cross-cutting that shipped beyond the original spec: the **entire dashboard is bilingual (EN + Bahasa Malaysia)**, and admin pages + APIs are **role-gated** (teachers restricted to attendance + their own classes).

---

## How to read this document

Each module follows the same structure:
- **Context** — why this module exists, what pain it solves
- **User stories** — who needs what and why
- **Requirements** — what the system must do (functional)
- **Acceptance criteria** — how we know a requirement is done (testable)
- **Out of scope for MVP** — explicit boundary to prevent scope creep

For the step-by-step **happy-path and edge-case flows** of every built module (reconciled to the built behaviour + the test suite), see [FLOWS.md](FLOWS.md).

Roles in this document:
- **Operator** — the business owner (e.g., Ustaz Azim / Sopan). Pays Kelas subscription.
- **Teacher/Ustaz** — runs sessions, marks attendance, gets paid per session.
- **Student** — enrolled in one or more classes. Pays fees to operator.
- **Guardian/Parent** — responsible adult for a student. Receives invoices and notices.

---

## Module 1 — Class Management

### Context
The group class is Kelas's core entity. Competitors (Mudeer, SMAP) model the student or the centre as the primary object. Kelas models the **class group** — one teacher, one cohort, one recurring schedule, one syllabus track. Every other module (attendance, billing, teacher pay) hangs off the class.

Pain from Sopan discovery: admin cannot see all classes at a glance without clicking into each one. No health signal (is this class growing, dying, full?). Class types are not structured — "kumpulan kecil" vs "kumpulan besar" is tracked in a spreadsheet.

### User Stories

| # | As a... | I want to... | So that... |
|---|---------|-------------|------------|
| M1-US1 | Operator | Create a class with type, capacity, schedule, and assigned teacher | I have a single record that represents a running cohort |
| M1-US2 | Operator | See all my classes on one screen with colour-coded health | I know at a glance which classes need attention |
| M1-US3 | Operator | Archive a class that has ended without losing its history | Old data stays queryable but doesn't clutter the active view |
| M1-US4 | Operator | Edit class details mid-cycle | I can update capacity or schedule without recreating the class |
| M1-US5 | Teacher | See which classes I'm assigned to | I know my schedule without asking admin |

### Requirements

**Class entity**
- R1.1 A class has: name, type, mode, capacity (min/max), assigned teacher(s), schedule (days + time), status, and org association.
- R1.2 Class types. **(SUPERSEDED 2026-06-27)** Shipped as a fixed preset: `individual`, `small_group`, `large_group`, `family`. `online`/`physical` were removed from type (they are `mode`, R1.3). Categorisation by Program + Level is the new org-managed taxonomy.
- R1.3 Class mode: `online`, `physical`, `hybrid`.
- R1.4 Class status: `active`, `paused`, `archived`. Archived classes are read-only. (`paused` exists in the schema; pause-a-class UI deferred to M4.)
- R1.5 A class can have multiple teachers. **(SUPERSEDED 2026-06-27)** Shipped as a **single** teacher at the class level, stored via the `class_teachers` M:N table (one row, `isPrimary`) so multi-teacher can be enabled later with no migration. Substitutes are handled per-session (M3), not at class level.
- R1.6 Schedule supports recurring patterns: daily, weekly (select days), bi-weekly.
- R1.7 Each class belongs to exactly one Better Auth organisation (operator tenant). No cross-tenant reads.

**Class health**
- R1.8 Health is computed automatically:
  - `green` — enrolled ≥ 70% of capacity AND attendance rate last 4 sessions ≥ 70%
  - `yellow` — enrolled 40–69% capacity OR attendance rate 40–69%
  - `red` — enrolled < 40% capacity OR attendance rate < 40% OR 0 sessions logged in 14 days
- R1.9 Health badge is visible on the class list (no click required).

**Sessions**
- R1.10 Each scheduled occurrence of a class is a **session**. **(SUPERSEDED 2026-06-27, now LAZY)** Sessions are NOT pre-generated. Upcoming session dates are computed on the fly from the class schedule; a `sessions` row is materialised only when acted on (attendance taken or cancelled). No background "calendar filler" job. Reason: avoids a cron dependency and empty future rows at small-operator scale.
- R1.11 Sessions can be cancelled (with optional reason) by admin or teacher.
- R1.12 A cancelled session is excluded from attendance rate and teacher pay calculations.

### Acceptance Criteria

| ID | Criterion | Test type |
|----|-----------|-----------|
| M1-AC1 | Operator can create a class and see it in the class list within the same page load | E2E |
| M1-AC2 | Health badge updates without manual refresh when attendance data changes | Unit (computed field) |
| M1-AC3 | Archived class is not shown in the active class list but is accessible via filter | E2E |
| M1-AC4 | ~~Sessions 60 days ahead are pre-generated on class creation~~ **(SUPERSEDED — lazy model; no pre-generation)** | n/a |
| M1-AC5 | Cancelling a session removes it from teacher pay calculation | Unit |
| M1-AC6 | A class created by Operator A is never visible to Operator B | Integration (tenant isolation) |

### Out of scope (MVP)
- Sub-classes or class hierarchies (e.g., Level 1 → Level 1A, 1B)
- Waiting list management
- Google Meet / Zoom integration (Phase 2)
- Class transfer between teachers

### As built (2026-06-27)
- **CRUD shipped:** create / edit / archive class; list with Program / Level / Teacher columns + filters; class detail page with roster.
- **Fields:** name, optional Program + Level (org taxonomy), single Teacher, `classType` preset, `mode`, capacity min/max, `monthlyFee` (student fee) + `teacherRatePerSession` (teacher pay, both frozen at creation), `meetingUrl` (for Phase 2 auto-attendance), per-day weekly `schedule` (each slot has its own day + time), notes.
- **Sessions are lazy** (see R1.10 superseded). **Class health badge (R1.8/R1.9, M1-AC2) NOT built yet** — only a per-class attendance rate (30-day) is shown; the green/yellow/red health grid is part of M6 (Operator Dashboard).
- Tenant isolation (M1-AC6) enforced and tested. Full bilingual.

---

## Module 2 — Student Management

### Context
Operators need to track who is enrolled, at what level, in which class, and whether they are active. Mid-cycle joins are common — a student joining Surah Al-Baqarah halfway through needs their "starting point" noted so the teacher knows where to pick up.

Pain from Sopan: student intake is manual, placement relies on teacher memory, no record of where a mid-join student entered.

### User Stories

| # | As a... | I want to... | So that... |
|---|---------|-------------|------------|
| M2-US1 | Operator | Add a student with profile and contact details | I have a single source of truth for each learner |
| M2-US2 | Operator | Enroll a student into a class with a start date | The student appears in attendance from day one |
| M2-US3 | Operator | Record a student's current level at intake | Placement decisions are data-driven |
| M2-US4 | Operator | Mark a student as paused or dropped | Billing stops and they don't count in attendance |
| M2-US5 | Operator | See all students across all classes in one view | I can search without knowing which class they're in |
| M2-US6 | Teacher | See the student roster for my class | I know who should be present at each session |
| M2-US7 | Operator | Record mid-cycle join — which session/syllabus point the student started | Teacher knows what content the student has missed |

### Requirements

**Student entity**
- R2.1 A student has: name, IC/passport, date of birth, gender, contact (phone + email), guardian, address, notes. **(REVISED 2026-06-27)** The **guardian is a separate entity** (its own `guardians` table), linked from the student by `guardianId`, NOT name/phone fields on the student. One guardian can have several children (siblings), and it is the future parent-app login + billing target.
- R2.2 A student belongs to one org (tenant). Transferring between orgs is out of scope.
- R2.3 Student status: `active`, `paused`, `dropped`, `graduated`.
- R2.4 Paused and dropped students are excluded from active billing and attendance marking.

**Enrollment**
- R2.5 An enrollment links a student to a class with: start date, end date (optional), mid-join session reference (optional), status.
- R2.6 A student can be enrolled in multiple classes simultaneously.
- R2.7 Enrollment status: `active`, `paused`, `ended`.
- R2.8 When enrollment is paused, billing for that class pauses (does not generate invoice for that month).
- R2.9 Mid-join reference: free-text field noting session number or syllabus point where student entered.

**Level**
- R2.10 Level is operator-defined (free text, e.g., "Iqra' 3", "Juz' 5", "Surah Al-Baqarah", "Form 4 Add Maths").
- R2.11 Level can be updated at any time and history is retained (with timestamp and who changed it).

### Acceptance Criteria

| ID | Criterion | Test type |
|----|-----------|-----------|
| M2-AC1 | Student can be enrolled in a class; they appear in next session's attendance sheet | E2E |
| M2-AC2 | Pausing an enrollment stops invoice generation for subsequent months | Unit |
| M2-AC3 | Level update is timestamped and previous levels are queryable | Unit |
| M2-AC4 | Global student search returns results across all classes | E2E |
| M2-AC5 | Dropping a student prevents them appearing in attendance or billing | Unit |

### Out of scope (MVP)
- Student self-registration portal
- Guardian mobile app
- Level assessment rubrics or automated placement logic
- Document uploads (IC scan, consent form)

### As built (2026-06-27)
- **Guardians** are their own module (CRUD), separate from students; a student links to one guardian (optional). Siblings share one guardian. The student form can pick an existing guardian or add a new one inline.
- **Students:** profile CRUD, status `active`/`paused`/`dropped`/`graduated`, free-text `currentLevel` with **level-change history** (who + when), and **global search** by name. Detail page shows profile + level history + enrolled classes.
- **Enrollments:** link a student to a class with start date, status (`active`/`paused`/`ended`), **fee override**, and a **mid-join note** (free text). The exact mid-join *session* reference (R2.9 FK) is deferred until it is needed; the note covers it. Enroll from either the student page or the class roster. Tenant-safety + duplicate guards enforced and tested.

---

## Module 3 — Attendance

### Context
Attendance is the highest-frequency action in the system — teachers mark it every session. It must be fast (≤3 taps), work on mobile, and require no training. The admin's current pain with Mudeer is having to click into each class separately to see attendance — Kelas solves this with a cross-class attendance dashboard.

Pain from Sopan: teachers mark attendance in a group chat or Mudeer, admin compiles manually for each class. No automatic absence follow-up. Admin cannot see all classes' attendance at once.

### User Stories

| # | As a... | I want to... | So that... |
|---|---------|-------------|------------|
| M3-US1 | Teacher | Mark each student present, absent, or late with one tap per student | Attendance is recorded in under 2 minutes for any class size |
| M3-US2 | Teacher | See my class roster pre-loaded for today's session | I don't need to type names or scroll endlessly |
| M3-US3 | Operator | See attendance across ALL classes on one screen without clicking into each | I get the full picture at a glance |
| M3-US4 | Operator | See which students have missed 3+ consecutive sessions | I can follow up proactively |
| M3-US5 | Operator | See per-class attendance rate over time | I can identify struggling classes |
| M3-US6 | Teacher | Submit attendance for a past session I forgot to mark | Historical data is still accurate |

### Requirements

**Attendance record**
- R3.1 Each attendance record links: student → session → status → timestamp → marked_by.
- R3.2 Status options: `present`, `absent`, `late`, `excused`.
- R3.3 Default status for all students at session start is `unmarked`. "Unmarked" is distinct from "absent".
- R3.4 Attendance can be marked and edited up to 7 days after the session date.
- R3.5 A session is considered "complete" when at least one student has been marked (any status).

**Teacher attendance UI**
- R3.6 Teacher sees today's sessions (their assigned classes) on a dashboard card.
- R3.7 Tapping a session opens the roster: list of enrolled students with one-tap status buttons.
- R3.8 Bulk mark: "Mark all present" button, then individual corrections.
- R3.9 UI must be usable on a mobile browser (no dedicated app required for MVP).
- R3.10 Teacher can add a note per student per session (optional, e.g., "arrived late — car trouble").

**Admin attendance dashboard**
- R3.11 Admin view shows all classes as a grid with today's session status: `pending`, `in-progress`, `complete`, `cancelled`, `no-session-today`.
- R3.12 Admin can drill into any class to see the full session roster.
- R3.13 Absence alert list: students with ≥3 consecutive absences, sortable by class.
- R3.14 Attendance rate per class visible on the class list (links back to Module 1 health).

**Reporting**
- R3.15 Per-student attendance report: total sessions, present count, absent count, rate (%), for a selectable date range.
- R3.16 Per-class attendance report: per-session breakdown, overall rate, trend chart.
- R3.17 Reports export to PDF and CSV.

### Acceptance Criteria

| ID | Criterion | Test type |
|----|-----------|-----------|
| M3-AC1 | Teacher marks full roster attendance in ≤10 taps for a 10-student class | E2E |
| M3-AC2 | `unmarked` is never counted as `absent` in rate calculations | Unit |
| M3-AC3 | Admin dashboard shows all classes' attendance status without navigating away | E2E |
| M3-AC4 | Student with 3 consecutive absences appears in absence alert list | Unit |
| M3-AC5 | Attendance for a session 5 days ago can be edited | E2E |
| M3-AC6 | Attendance rate on class health matches per-class report calculation | Unit |
| M3-AC7 | PDF and CSV export contain correct data for selected date range | E2E |

### Out of scope (MVP)
- QR code check-in (Phase 2)
- RFID attendance
- Google Meet / Zoom auto-attendance via join detection (Phase 2 — schema is ready: `attendance_records.source` + class `meetingUrl`)
- SMS/WhatsApp notification to absent student's guardian (Phase 2 — requires WA integration)

### As built (2026-06-27)
- **Take attendance:** lazy session materialisation (a session row is created on first mark); roster of enrolled students; one-tap `present`/`absent`/`late`/`excused` per student; "Mark all present"; per-student note; **7-day edit window**; "today" computed in Asia/Kuala_Lumpur. `unmarked` is never counted as absent. Mobile-first.
- **Teacher self-service (M3-US1/US2 satisfied):** teacher accounts shipped — roles **Operator / Staff / Teacher** (app-level over Clerk admin/member). Teachers see only Attendance, scoped to their own classes (pages + APIs gated). Session records `taughtByTeacherId` (who actually taught) for M4 pay.
- **Admin attendance dashboard (M3-US3/US4/US5):** today summary (complete/pending), per-class 30-day rate, and absence alerts (students with 3+ consecutive absences). Rate = (present+late)/(present+late+absent); excused + unmarked excluded.
- **Reports + export (M3-US?, R3.15–R3.17):** per-student and per-class attendance reports over a date range, **server-generated PDF** + **CSV**, plus an on-screen weekly **trend chart**.

---

## Module 4 — Billing & Invoicing

### Context
Fee collection is manual and high-friction for most operators: teachers collect cash, admin chases non-payers via WhatsApp, no record of who paid what. Kelas automates invoice generation, payment link sharing, and non-payment follow-up queuing.

Key rule from Sopan: **burn policy** — absent students still get billed (they "burn" their slot). Operators set this policy; it must be configurable.

Two payment flows exist:
1. **Platform billing** — operator pays Kelas subscription (Stripe/Billplz)
2. **Class billing** — student/guardian pays operator (FIUU/FPX/manual)

This module covers class billing only. Platform billing is handled by the boilerplate's Stripe integration.

> **Status (2026-06-28): MVP DONE and verified end-to-end.** Brainstormed decision-by-decision with Hafiz; the authoritative build plan is [features/m4-billing/DESIGN.md](features/m4-billing/DESIGN.md). The MVP is a **lean manual-first** billing tool: family invoices, full lifecycle, manual payments/refunds + receipts, public payment page (DuitNow QR + bank details) with self-service receipt upload + an operator verification queue, WhatsApp + copy-link sharing, invoice PDF. The online gateway / auto-confirmation / dynamic QR / teacher pay / auto-cron are **post-MVP (slice 2)**. Several original requirements below are superseded by those decisions (marked inline); see the **"As planned"** subsection for the MVP shape. Foundations already in place: each class carries a frozen `monthlyFee` + `teacherRatePerSession`; enrollments carry `feeOverride`; the `burnPolicy` column exists on classes; the `invoices` / `invoiceLineItems` / `payments` / `invoiceEvents` tables exist; and the M3 server-PDF pipeline (`@react-pdf/renderer`) is reused for invoice PDFs.

### User Stories

| # | As a... | I want to... | So that... |
|---|---------|-------------|------------|
| M4-US1 | Operator | Have invoices generated automatically each month | I don't manually create 200 invoices |
| M4-US2 | Operator | Copy a payment link and send it to a guardian via WhatsApp | The guardian can pay with one tap |
| M4-US3 | Operator | Record a manual payment (bank transfer) against an invoice | Cash and transfer payments are tracked |
| M4-US4 | Operator | See all unpaid invoices in one list | I know exactly who owes money |
| M4-US5 | Operator | Set a different monthly fee per class | Kumpulan kecil and kumpulan besar have different rates |
| M4-US6 | Guardian | Pay via FPX online through a link | I don't need to go to the centre |
| M4-US7 | Operator | Apply a discount or one-off credit to a student's invoice | I can handle sibling discounts or goodwill credits |
| M4-US8 | Operator | Configure the burn policy per class | I control whether absent students still pay |

### Requirements

**Fee structure**
- R4.1 Each class has a `monthly_fee` (per student, per calendar month).
- R4.2 Operators can override the fee per enrollment (student-level exception).
- R4.3 Discounts: flat (RM) or percentage, applied per invoice or recurring per enrollment.
- R4.4 Burn policy (per class): `always_bill` (absent students pay full fee) or `prorate` (absent sessions deducted). Default: `always_bill`.

**Invoice generation**
- R4.5 Invoices are generated automatically on the 25th of each month for the following month. **(SUPERSEDED 2026-06-27)** MVP generation is a **manual "Run billing" button** (invoices born as drafts, idempotent re-runs), written so a scheduler can call the same function later. Auto-cron deferred to slice 2.
- R4.6 One invoice per student per month (if enrolled in multiple classes, one invoice covers all classes). **(SUPERSEDED 2026-06-27)** Invoice is a **family invoice: one per guardian per month**, with line items grouped by child across all their classes. Adult learners with no guardian are billed directly. The invoice is keyed to a **payer** (guardian, or student as fallback), not the student.
- R4.7 Invoice line items: one row per class enrollment for that month, with class name, monthly fee, and any discounts.
- R4.8 Invoices are generated only for `active` enrollments. Paused enrollments are skipped.
- R4.9 Manual invoice generation available (operator can trigger for a specific student or the whole org).
- R4.10 Invoice number format: `[ORG_CODE]-[YEAR][MONTH]-[SEQUENCE]` e.g. `SPN-202508-0042`.

**Invoice lifecycle**
- R4.11 Invoice statuses: `draft`, `issued`, `partially_paid`, `paid`, `overdue`, `voided`.
- R4.12 `draft` → `issued` on generation (or manual issue).
- R4.13 `issued` → `overdue` automatically after due date passes (configurable, default 14 days from issue).
- R4.14 `issued` or `partially_paid` → `paid` when payment(s) cover the total.
- R4.15 Voiding an invoice removes it from payment obligations but retains audit history.

**Payment recording**
- R4.16 Payments can be: `fpx_online` (via FIUU gateway), `manual_bank_transfer`, `cash`, `other`. **(REVISED 2026-06-27)** MVP methods are **cash / bank transfer / other** (manual recording); `fpx_online` gateway deferred to slice 2. Every manual payment can carry an attached **receipt** (image or PDF).
- R4.17 Partial payments supported: operator records amount received; invoice moves to `partially_paid`.
- R4.18 FPX payment link: a unique, time-limited URL generated per invoice for FIUU payment gateway. **(DEFERRED to slice 2.)** Slice 1.5 instead adds a tokenised **public invoice page** showing the org's **DuitNow QR** + bank details and a **self-service receipt upload** (no gateway). Uploaded receipts are pending until an operator verifies them.
- R4.19 FIUU webhook updates invoice status automatically on confirmed payment. **(DEFERRED to slice 2.)**
- R4.20 Manual payments are recorded by admin with: amount, date, payment method, optional reference (receipt no. / transaction ID).

**Non-payment follow-up**
- R4.21 Overdue invoice list shows: student name, class, amount, days overdue, last contact date.
- R4.22 Operator can mark a follow-up action on each overdue invoice (contacted, payment promised, escalate).
- R4.23 One-click: copy a follow-up message template (pre-filled with student name, amount, invoice number) for WhatsApp sending. **(REVISED 2026-06-27)** Implemented as a **WhatsApp click-to-chat button** (`wa.me`, prefilled with name/amount/invoice no./link, opens the customer's chat). Follow-up status tracking (contacted/promised/escalate, R4.22) deferred. Built behind a **messaging seam** so finch-lite (in-app send + inbox) can replace it later with no rework.

**LHDN e-invoice compliance**
- R4.24 Each invoice stores fields required for LHDN MyInvois: supplier TIN, buyer TIN (optional), invoice date, MSIC code, total tax, classification. **(DEFERRED 2026-06-27, skipped for MVP.)** LHDN columns were deliberately removed from the schema to keep it multi-country; revisit when MyInvois support is scheduled.
- R4.25 LHDN submission is a manual operator action (not automated in MVP). Fields are captured; submission tooling is Phase 2. **(DEFERRED 2026-06-27.)**

### Acceptance Criteria

| ID | Criterion | Test type |
|----|-----------|-----------|
| M4-AC1 | Invoice auto-generation on 25th creates one invoice per active student | Unit (scheduled job) |
| M4-AC2 | Student enrolled in 2 classes gets one invoice with 2 line items | Unit |
| M4-AC3 | Paused enrollment generates no invoice that month | Unit |
| M4-AC4 | FPX payment link opens FIUU checkout; confirmed payment moves invoice to `paid` | E2E |
| M4-AC5 | Partial payment moves invoice to `partially_paid`; remainder is tracked | Unit |
| M4-AC6 | Invoice overdue date is 14 days after issue (configurable) | Unit |
| M4-AC7 | Voided invoice remains in audit log but is excluded from outstanding balance | Unit |
| M4-AC8 | Overdue list is accurate: all invoices past due date with status `issued` or `partially_paid` | Unit |
| M4-AC9 | Burn policy `prorate` deducts absent sessions from invoice amount | Unit |
| M4-AC10 | LHDN fields are present on every invoice record | Unit |

### Out of scope (MVP)
- LHDN MyInvois fields + API submission (deferred)
- Online FPX/FIUU gateway + webhook (slice 2)
- Teacher pay computation + pay slips (slice 2, own design)
- Auto-generation cron (slice 2; manual button is C-ready)
- Auto-proration of absent sessions (fields kept; manual deductions cover the need)
- Automated WhatsApp/email sending (Phase 2; MVP uses click-to-chat). finch-lite in-app WhatsApp (deferred, behind a messaging seam)
- Follow-up status tracking, credit balances, recurring auto-debit, multi-currency

### As planned (2026-06-27): MVP shape

Authoritative plan: [features/m4-billing/DESIGN.md](features/m4-billing/DESIGN.md). Decided with Hafiz, decision-by-decision.

- **Scope:** lean manual-first. **Slice 1** = invoice lifecycle run by hand + media service + WhatsApp button. **Slice 1.5** = self-service DuitNow-QR receipt-upload page + verification queue. **Slice 2** = teacher pay, FPX gateway, optional auto-cron.
- **Family invoice:** one per guardian (payer), lines grouped by child; adult learners billed directly.
- **Lifecycle (no dead ends):** draft -> issue -> partial/full payment -> paid; overdue is a computed label (no cron); void (with refund if already paid); corrections via draft-edit or void+reissue.
- **Amount:** flat monthly fee (always-bill). Manual **discounts**, **adjustment/credit lines**, and **refunds** are in the MVP for case-by-case deductions.
- **Payments:** manual cash / bank transfer / other; partial + refund; each can attach a **receipt** (image or PDF). Self-service uploads (slice 1.5) are pending until an operator verifies.
- **Delivery:** WhatsApp **click-to-chat** button (`wa.me`, prefilled) + invoice PDF, behind a messaging seam for finch-lite later.
- **Media service (built first):** sharp + WebP (thumbnail + view), PDF first-page preview via poppler, stored in a private Wasabi bucket with signed URLs; HEIC supported.
- **Access:** operator/staff only; teachers never see billing or payments.
- **Bilingual:** all UI built en + ms from the start.

Acceptance criteria above are partially superseded: M4-AC1 (auto-gen on 25th) becomes manual-button generation; M4-AC2 reads as one **family** invoice with grouped lines; M4-AC4 (FPX) and M4-AC9 (prorate) and M4-AC10 (LHDN) move to later slices.

---

## Module 5 — Teacher Management

### Context
Teachers need to see their classes, log their sessions (which drives pay calculation), and view their pay slips. Operators need to know how many sessions each teacher ran, calculate pay, and track teacher quality over time.

Pay model from Sopan: teachers are paid per session, not a fixed salary. Rate varies by class type (kumpulan kecil pays differently from kumpulan besar).

### User Stories

| # | As a... | I want to... | So that... |
|---|---------|-------------|------------|
| M5-US1 | Operator | Add a teacher profile with contact details and pay rates | Teachers are properly set up before being assigned classes |
| M5-US2 | Operator | Assign a teacher to one or more classes | Classes have a responsible instructor |
| M5-US3 | Teacher | See my assigned classes and their schedules | I know where I need to be and when |
| M5-US4 | Teacher | Log that I completed a session | My session count drives my monthly pay |
| M5-US5 | Operator | See how many sessions each teacher completed this month | I can calculate pay accurately |
| M5-US6 | Operator | Calculate teacher pay automatically at month-end | Manual pay calculation errors are eliminated |
| M5-US7 | Operator | Grade a teacher (A/B/C) based on class health and feedback | Quality trends are tracked over time |
| M5-US8 | Teacher | View my pay slip for the current and past months | I can see how my pay was calculated |

### Requirements

**Teacher entity**
- R5.1 A teacher has: name, IC/passport, phone, email, bank account details (for pay), grade (A/B/C), status (active/inactive). Built; `grade` is **nullable** (a new teacher is "Not graded" until assessed).
- R5.2 Pay rate. **(SUPERSEDED 2026-06-27)** Pay is **not** stored per teacher. The rate lives **on the class** (`teacherRatePerSession`, frozen at creation). Reason: matches Jackrabbit/Teachworks + sifu-tutor, and invoicing/payroll need the rate frozen on the class. The `teacher_rates` table was dropped.
- R5.3 Rate override per assignment. **(SUPERSEDED — see R5.2)** `class_teachers.rateOverride` exists for the rare per-teacher-per-class exception; UI deferred.

**Session logging**
- R5.4 When a teacher marks attendance for a session, that session is automatically counted as "completed" for pay purposes.
- R5.5 If attendance was marked by admin on behalf of a teacher, the assigned teacher still gets credit.
- R5.6 Cancelled sessions do not count toward teacher pay.

**Pay calculation**
- R5.7 Monthly pay = Σ (completed sessions × rate per class type) for the pay period.
- R5.8 Pay period: configurable (default: 1st–last of month).
- R5.9 Pay calculation is triggered manually by operator (not auto-disbursed in MVP).
- R5.10 Pay slip shows: teacher name, pay period, class breakdown (sessions × rate), total.
- R5.11 Pay slips are stored and accessible to the teacher via their login.

**Teacher grading**
- R5.12 Grade (A/B/C) is set manually by operator.
- R5.13 Grade history is retained (timestamped).
- R5.14 Grade is visible on teacher profile and in class listings.

### Acceptance Criteria

| ID | Criterion | Test type |
|----|-----------|-----------|
| M5-AC1 | Session marked as attended auto-increments teacher's session count for the month | Unit |
| M5-AC2 | Cancelled session is excluded from session count | Unit |
| M5-AC3 | Pay calculation produces correct total for teacher with 2 classes at different rates | Unit |
| M5-AC4 | Teacher can view their pay slip but cannot view another teacher's | E2E (auth) |
| M5-AC5 | Grade update is timestamped; previous grades are in history | Unit |

### Out of scope (MVP)
- Automated bank transfer for teacher pay (Phase 2)
- Teacher self-registration / onboarding flow
- Substitute teacher management
- EPF / SOCSO deduction calculation
- Performance review workflow

### As built (2026-06-27)
- **Teacher profile CRUD** shipped: name, IC, phone, email, bank name + account, grade (A/B/C or "Not graded"), active/inactive. Grade set manually; **grade history (R5.13) not built yet**.
- **Pay model changed** (see R5.2/R5.3): pay is on the class, not per-teacher. **Pay calculation + pay slips (R5.7–R5.11, M5-AC3/AC4) NOT built** — they belong with M4 Billing. Per-session "who taught" is captured on the session (`taughtByTeacherId`) and will drive that.
- **Teacher login** shipped (see M3 As built): a teacher = a Clerk member linked to a teacher record (by email on first login). Assignment to a class = single teacher (M:N foundation).

---

## Module 6 — Operator Dashboard

### Context
The operator dashboard is the first screen after login. It must answer "how is my business doing right now?" without any drilling. Sopan's current state: zero visibility without manually compiling reports from Mudeer + Excel.

> **Status (2026-06-27): not built yet.** The **class health badge (M1 R1.8/R1.9) belongs here**, not in M1. A partial attendance dashboard already exists (M3 As built: today summary, per-class rate, absence alerts); M6 will add the class-health grid, revenue summary, student-count trend, and the action queue.

### User Stories

| # | As a... | I want to... | So that... |
|---|---------|-------------|------------|
| M6-US1 | Operator | See my class health at a glance (all classes, colour coded) | I know which classes need attention in under 10 seconds |
| M6-US2 | Operator | See revenue collected vs outstanding this month | I know my cash position |
| M6-US3 | Operator | See overall attendance rate across all classes | I can spot trends before they become problems |
| M6-US4 | Operator | See student count trend (this month vs last month) | I know if my business is growing or shrinking |
| M6-US5 | Operator | See pending actions (overdue invoices, absence alerts, unmarked sessions) | I have a prioritised to-do list when I log in |

### Requirements

**Dashboard cards (above the fold)**
- R6.1 Class health grid: all active classes as cards showing name, teacher, current enrolment vs capacity, health badge.
- R6.2 Revenue summary: total invoiced this month, total collected, total outstanding, collection rate %.
- R6.3 Attendance summary: average attendance rate across all classes this month.
- R6.4 Student count: total active students, delta vs previous month (▲ or ▼).

**Action queue**
- R6.5 Overdue invoices count — links to invoice list filtered to overdue.
- R6.6 Consecutive absence alerts count — links to absence alert list.
- R6.7 Sessions not yet marked count — links to sessions list filtered to `pending` for past sessions.

**Performance**
- R6.8 Dashboard data loads within 2 seconds on initial render.
- R6.9 Dashboard auto-refreshes every 60 seconds (or on-demand refresh button).

### Acceptance Criteria

| ID | Criterion | Test type |
|----|-----------|-----------|
| M6-AC1 | All active classes visible on dashboard without scrolling for up to 12 classes | Visual / E2E |
| M6-AC2 | Revenue figures match the sum of invoices in the billing module | Unit |
| M6-AC3 | Overdue count matches overdue invoices list | Unit |
| M6-AC4 | Dashboard loads within 2 seconds with 500 students and 20 classes | Performance |
| M6-AC5 | Each action queue item links to the correct filtered view | E2E |

### Out of scope (MVP)
- Historical trend charts (Phase 2)
- Multi-branch / multi-location consolidation (Phase 2)
- Export dashboard as PDF/image
- Role-specific dashboards for teachers (teachers get a simpler "my classes today" view only)

---

## Module 7 — AI Layer (differentiator)

### Context
No competitor has real AI. This module wraps the other 6 modules in intelligence — surfacing insights the operator would have to compile manually, drafting communications, and recommending actions. Built on Vercel AI SDK + Anthropic Claude.

This module ships incrementally alongside other modules, not as a standalone phase.

### User Stories

| # | As a... | I want to... | So that... |
|---|---------|-------------|------------|
| M7-US1 | Operator | See a plain-English narrative about a class that has been red 3 weeks | I understand the root cause without interpreting raw data |
| M7-US2 | Operator | Click a button and get a draft WhatsApp message to an absent student's guardian | I send follow-ups in seconds, not minutes |
| M7-US3 | Operator | Ask "which students are at risk of dropping?" and get a ranked list | I can intervene before they actually drop |
| M7-US4 | Operator | Get a placement recommendation when adding a new student | I don't rely on teacher memory for level placement |

### Requirements

**AI narrative — class health**
- R7.1 Each class with `yellow` or `red` health status shows an AI-generated narrative: "This class has been below 50% attendance for 3 consecutive weeks. 4 students have unpaid invoices since June. Two students joined mid-cycle and may need additional support."
- R7.2 Narrative is generated server-side (Server Action or API route) on demand, streamed to the client.
- R7.3 Narrative is regenerated when the operator clicks "Refresh insight".

**AI message drafting**
- R7.4 On the absence alert list and overdue invoice list, each row has a "Draft message" button.
- R7.5 Clicking opens a drawer with a pre-drafted WhatsApp-style message (student name, context, operator's tone).
- R7.6 Operator can edit the draft before copying to clipboard.
- R7.7 Tone is configurable: `formal_malay`, `casual_malay`, `english`.

**AI at-risk detection**
- R7.8 "At-risk" query: returns students ranked by risk score, computed from attendance rate + payment history + days since last session.
- R7.9 Results surface on the dashboard as a dismissable card.

**Placement recommendation**
- R7.10 When operator inputs a new student's level (free text), AI suggests the 1–3 best matching classes from available capacity.
- R7.11 Recommendation rationale is shown: "Based on Iqra' 3 level and available slots, Kelas Asas A (Tue/Thu 7pm) is the closest match."

### Acceptance Criteria

| ID | Criterion | Test type |
|----|-----------|-----------|
| M7-AC1 | Class health narrative streams to the UI within 3 seconds of trigger | E2E |
| M7-AC2 | Draft message includes correct student name and context from live data | Unit (prompt injection test) |
| M7-AC3 | At-risk list is accurate: students with attendance rate < 60% or 2+ unpaid invoices appear | Unit |
| M7-AC4 | Placement recommendation only suggests classes with available capacity | Unit |
| M7-AC5 | AI features degrade gracefully if Anthropic API is unavailable (show "AI unavailable, try again later") | Unit |

### Out of scope (MVP)
- Hafazan/Quran progress AI coaching
- Automated syllabus gap analysis for mid-join students
- RAG over uploaded class materials
- Teacher performance AI insights

---

## Module 8: Onboarding & Activation

### Context
There's no dedicated support team and no time to personally walk every new org admin through the product. Without proactive guidance, a newly registered admin can stall before reaching first value.

**Correction, 2026-07-05:** the checklist and dismissible-banner portion of this module was designed without first checking the codebase, and duplicates a getting-started checklist that already shipped 2026-07-02/07-03 (`src/features/onboarding/service.ts` + `GettingStartedChecklist.tsx`, already live on `(operator)/page.tsx`, already tested, already bilingual, 6 steps: payment/teacher/class/enrol/attendance/invoice). That existing feature stays as-is; M8-US1, M8-US3, and their requirements below (R8.1-R8.4) are already satisfied by it, not new work. The real remaining scope of this module is the **contextual spotlight tour**, which does not exist yet. Full design, decision rationale, and build notes: [features/onboarding-activation/DESIGN.md](features/onboarding-activation/DESIGN.md).

### User Stories

| # | As a... | I want to... | So that... | Status |
|---|---------|-------------|------------|--------|
| M8-US1 | New org admin | See a dismissible checklist right after my first login | I know exactly what to do first without reading documentation | Already shipped |
| M8-US2 | New org admin | Get a spotlighted tooltip on the exact button to click when I land on a page with nothing set up yet | I don't have to guess where to start | Built 2026-07-06 |
| M8-US3 | New org admin | See my checklist automatically check off steps as I actually do them | I trust the progress shown reflects what's really true | Already shipped |

### Requirements

**Golden path & checklist (already shipped, no new work)**
- R8.1 Checklist covers 6 steps (payment, teacher, class, enrol, attendance, invoice), each deep-linking to its page, `?from=onboarding` pull-through.
- R8.2 Checklist widget lives on the operator dashboard home (`(operator)/page.tsx`).
- R8.3 Checklist completion state is derived live from existing data; no dedicated progress table.
- R8.4 Dismiss state persists via `localStorage`. Not a forced full-screen tour.

**Contextual tooltips (to build)**
- R8.5 Spotlight tooltips fire per-page, triggered by the org's actual state (e.g. zero classes on the Classes page), not by a fixed step counter.
- R8.6 Built with Onborda + Framer Motion.
- R8.7 Tooltip copy is capped at one sentence, one action.
- R8.8 Tooltip strings are bilingual (EN + BM) via `next-intl`, in their own namespace (kept separate from the existing `Onboarding` checklist namespace).

**Content maintenance**
- R8.9 Any change touching a golden-path route (levels/programs, classes, teachers, students, guardians, billing/invoicing) triggers a drafted content update for the affected tooltip copy.
- R8.10 Drafted content is reviewed and approved by Hafiz before merge. Never auto-published.

### Acceptance Criteria

| ID | Criterion | Test type | Status |
|----|-----------|-----------|--------|
| M8-AC1 | Checklist item state matches real data: creating a class checks off the class step without any extra write | Unit | Already passing (existing suite) |
| M8-AC2 | Spotlight tooltip appears on Classes page only when the org has zero classes | E2E | Built + browser-verified 2026-07-06 |
| M8-AC3 | Every tooltip string renders correctly in both `en` and `ms` locales | Unit (i18n check) | Built; BM copy is a draft pending native review |

### Out of scope (MVP)
- Teacher- and guardian-specific onboarding flows (Decision 1: admin only for now)
- Full DB-backed Help Center: search, taxonomy, editorial CMS, article feedback/analytics (Decision 8, deferred)
- PostHog / Microsoft Clarity analytics (Decision 6, deferred)
- Automated enforcement (hooks/CI) for the content maintenance workflow, stays a manual convention (Decision 7)

---

## Cross-cutting Requirements

### Multi-tenancy
- CX1 Every database table that stores operator data has an `org_id` column.
- CX2 Every API route and server action verifies the requesting user's Better Auth session `orgId` before any DB operation. No exceptions.
- CX3 A user with access to Org A can never read, write, or infer data belonging to Org B.
- CX4 Better Auth organisation = one operator tenant. Each operator signs up, creates their org, and all their data lives under that org.

### Authentication & Roles
- CX5 Roles within an org. **(REVISED 2026-06-27; auth migrated to Better Auth 2026-07-02)** Three **assigned** organisation membership roles in Better Auth (roles are stored on membership, never inferred from an admin/member flag):
  - **Operator** = the `operator` role. Full access (the owner).
  - **Staff** = the `staff` role, not linked to a teacher record. "Subset of admin": full operational access today; owner-only areas (billing, settings, staff admin) gated as those features land.
  - **Teacher** = the `teacher` role, linked to a `teachers` record (by email on first login). Attendance + their own classes only.
  - (`viewer` from the original spec not built.)
- CX6 Better Auth (self-hosted) handles auth (social login, magic link, passkeys). No third-party auth service.
- CX7 Teacher login gives access only to assigned classes. **Built** — enforced at both the page layer (a `(operator)` route-group guard) and the API layer (`requireOperatorContext`).

### Localisation (added 2026-06-27)
- CX-L1 The entire product (marketing site + dashboard) is **bilingual: English + Bahasa Malaysia**, via next-intl, with a language switcher. Every new module must ship with both locales (en.json + ms.json). Better Auth sign-in and account screens are localised too.

### Mobile responsiveness
- CX8 Attendance marking UI must be fully usable on a 390px-wide mobile browser (iPhone SE breakpoint).
- CX9 All other views should be usable on tablet (768px). Desktop is the primary surface for operator/admin.

### Performance
- CX10 All list views paginate at 50 rows. No infinite unbounded queries.
- CX11 Dashboard aggregation queries must complete in < 500ms with 1,000 students and 30 classes.

### Audit trail
- CX12 All writes (create / update / delete) to invoices, payments, and enrollments are logged with: timestamp, user ID, change description.

---

## Delivery Priority (Build Order)

| Priority | Module | Reason |
|---|---|---|
| P0 | Org setup + Better Auth multi-tenancy | Nothing else works without this |
| P0 | Class Management (M1) | Core entity everything hangs off |
| P0 | Student Management (M2) | Required for attendance and billing |
| P1 | Attendance (M3) | Sopan's #1 pain point |
| P1 | Teacher Management (M5) | Needed to complete attendance flow |
| P2 | Billing & Invoicing (M4) | Revenue-critical, but complex — needs M1+M2+M3 stable first |
| P2 | Operator Dashboard (M6) | Needs all other modules to have data |
| P3 | AI Layer (M7) | Differentiator — layered in after M1–M6 have live data |

---

## Platform Administration (post-MVP)

Kelasapp's `/dashboard` is the **per-operator** admin — one Better Auth organisation = one operator tenant, with roles owner/admin/teacher/viewer. A **platform-level super-admin** — for Kelasapp HQ to oversee *all* operators at once (cross-tenant metrics, subscription management, support/impersonation, suspending a bad actor) — is **explicitly out of scope for MVP**.

Interim, platform administration uses existing tools:
- **Better Auth admin (our own)** — view/manage all users and organisations.
- **Stripe / billing dashboard** — subscriptions and revenue (once platform billing is live).

Build a custom internal admin panel (or a tool like Retool) **later**, once there are ~5–10 live operators and concrete support needs those tools can't cover. (Decision 2026-06-26.)

---

*This PRD is the requirements source of truth. Data model, UX specs, and build prompts are derived from it.*
