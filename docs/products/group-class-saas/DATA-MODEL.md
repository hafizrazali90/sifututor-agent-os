# Kelasapp: Multi-Tenant PostgreSQL Data Model
**Last updated:** 2026-06-27 (as-built reconciliation)
**ORM:** Drizzle ORM (PostgreSQL)
**Tenancy:** Better Auth organisation id (`org_id` = Better Auth `orgId` string) on every tenant-scoped table

> **Source of truth:** the live schema is `kelas/src/models/Schema.ts` (with migrations in `kelas/migrations/`).
> This narrative is reconciled to it as of 2026-06-27. Key changes from the original draft:
> - **Sessions are LAZY**, not pre-generated (no 60-day cron). A `sessions` row is created on first action.
> - **Teacher pay moved to the class** (`classes.teacher_rate_per_session`); the `teacher_rates` table was **dropped**.
> - **Guardian is its own table** (`guardians`); students link via `guardian_id` (no guardian_* fields on the student).
> - **New taxonomy tables** `programs` + `levels` (org-managed); classes carry `program_id` + `level_id`.
> - `classes.class_type` is a fixed preset; added `classes.meeting_url`; `sessions.taught_by_teacher_id`; `attendance_records.source`.

---

## Design Principles

1. **Tenant isolation is the top-level constraint.** Every table that holds operator data carries `org_id`. Every query filters by it. No exceptions.
2. **Better Auth is the auth source of truth (self-hosted).** Users live in our own Postgres (`src/models/AuthSchema.ts`), not a third-party service. The `clerk_user_id` columns are legacy-named but now hold the Better Auth user id (the column rename is deferred).
3. **Soft deletes on financial records.** Invoices and payments are never hard-deleted; they use `deleted_at`. All other tables use hard deletes or status fields.
4. **Sessions are LAZY (as-built 2026-06-27).** Class sessions are NOT pre-generated. Upcoming dates are computed from the class schedule; a `sessions` row is materialised only when acted on (attendance taken or cancelled). No background "calendar filler" job.
5. **Immutable audit log for money.** Every invoice status change and payment write is appended to `invoice_events`, never updated in place.

---

## Table Map

```
TENANT BOUNDARY (org_id on all tables below)
│
├── programs                 ← org-managed taxonomy: what is taught (Quran, Math)
├── levels                   ← org-managed taxonomy: the stage (Asas, SPM)
│
├── classes                  ← the core entity (program_id, level_id, teacher_rate_per_session, meeting_url)
│   ├── class_teachers       ← M:N teacher assignment (single teacher used today)
│   └── sessions             ← LAZY: materialised on first action (taught_by_teacher_id)
│
├── guardians                ← parent/wali; one guardian, many students
├── students                 ← guardian_id → guardians; current_level + level history
│   ├── student_level_history
│   └── enrollments          ← student ↔ class link (fee override, mid-join note)
│
├── attendance_records       ← student ↔ session mark (status, source)
│
├── teachers                 ← profile only; grade nullable. (teacher_rates table REMOVED)
│   └── teacher_grade_history
│
├── invoices                 ← FAMILY invoice: one per payer (guardian, or student) per month   [M4 building]
│   ├── invoice_line_items    ← grouped by child; plus non-class discount/adjustment/credit lines
│   ├── payments              ← payment | refund; verified vs pending (self-service); receipt_file_id
│   └── invoice_events
│
├── media_files              ← uploaded/generated files (receipts, DuitNow QR, logos); Wasabi + signed URLs
│
└── org_settings             ← per-tenant config (billing day, burn policy, timezone, DuitNow QR + bank details)

PLATFORM (no org_id, managed by Kelasapp, not operators)
│
└── (Better Auth organisation metadata is read via the Better Auth org plugin / org_settings mirror)
```

---

## Tables (Drizzle schema notation)

### `org_settings`
Per-tenant configuration. One row per Better Auth organisation.

```ts
org_settings {
  org_id              text        PK          -- Better Auth orgId
  display_name        text        NOT NULL
  currency            text        DEFAULT 'MYR'  -- ISO 4217: 'MYR' | 'SGD' | 'IDR' etc.
  invoice_prefix      text        DEFAULT 'INV'  -- prefix for invoice numbers e.g. 'INV' → INV-202508-0042
  invoice_day         smallint    DEFAULT 25  -- day of month invoices are generated
  default_due_days    smallint    DEFAULT 14  -- days after issue before overdue
  default_burn_policy text        DEFAULT 'always_bill' -- 'always_bill' | 'prorate'
  timezone            text        DEFAULT 'Asia/Kuala_Lumpur'
  -- M4: shown on the public payment page (slice 1.5) so guardians can transfer
  duitnow_qr_file_id  uuid                  -- FK → media_files.id (the org's DuitNow QR image)
  bank_name           text
  bank_account_number text
  bank_account_holder text
  created_at          timestamptz DEFAULT now()
  updated_at          timestamptz DEFAULT now()
}
```

---

### `teachers`
```ts
teachers {
  id                  uuid        PK DEFAULT gen_random_uuid()
  org_id              text        NOT NULL  -- FK → org_settings.org_id
  clerk_user_id       text                  -- set when teacher has a login; nullable (can be added later)
  name                text        NOT NULL
  ic_number           text                  -- IC or passport
  phone               text
  email               text
  bank_name           text
  bank_account        text
  grade               text                  -- 'A' | 'B' | 'C' | null (nullable: new teacher is "Not graded"). Set manually.
  status              text        DEFAULT 'active'  -- 'active' | 'inactive'
  created_at          timestamptz DEFAULT now()
  updated_at          timestamptz DEFAULT now()

  INDEX (org_id)
  INDEX (clerk_user_id)
}

teacher_grade_history {
  id          uuid        PK DEFAULT gen_random_uuid()
  teacher_id  uuid        NOT NULL  -- FK → teachers.id
  org_id      text        NOT NULL
  grade       text        NOT NULL
  changed_by  text        NOT NULL  -- clerk_user_id of admin
  changed_at  timestamptz DEFAULT now()
}
```

---

### `programs` + `levels` (org-managed taxonomy)
Two simple lookup tables the operator manages themselves (Option C, 2026-06-26). A **program** = what is taught (Quran, Math, English); a **level** = the stage (Asas/Mahir, Iqra 1-6, Form 4, SPM). Classes optionally reference one of each for filtering and finding. Both are org-scoped and labelled "Program" / "Level" in the UI.

```ts
programs {
  id          uuid        PK DEFAULT gen_random_uuid()
  org_id      text        NOT NULL
  name        text        NOT NULL
  status      text        DEFAULT 'active'  -- 'active' | 'archived'
  created_at  timestamptz DEFAULT now()
  updated_at  timestamptz DEFAULT now()

  INDEX (org_id)
  INDEX (org_id, status)
}

levels {
  id          uuid        PK DEFAULT gen_random_uuid()
  org_id      text        NOT NULL
  name        text        NOT NULL
  status      text        DEFAULT 'active'  -- 'active' | 'archived'
  created_at  timestamptz DEFAULT now()
  updated_at  timestamptz DEFAULT now()

  INDEX (org_id)
  INDEX (org_id, status)
}
```

---

### `classes`
```ts
classes {
  id                       uuid        PK DEFAULT gen_random_uuid()
  org_id                   text        NOT NULL
  name                     text        NOT NULL
  program_id               uuid                  -- FK → programs.id (nullable: optional org-managed taxonomy)
  level_id                 uuid                  -- FK → levels.id (nullable: optional org-managed taxonomy)
  class_type               text        NOT NULL  -- preset format: 'individual' | 'small_group' | 'large_group' | 'family'
  mode                     text        NOT NULL  -- 'online' | 'physical' | 'hybrid'
  capacity_min             smallint    DEFAULT 1
  capacity_max             smallint    DEFAULT 30
  monthly_fee              numeric(10,2) NOT NULL  -- student fee, frozen at creation
  teacher_rate_per_session numeric(10,2)         -- teacher PAY, frozen at creation (pay lives on the class, not the teacher)
  meeting_url              text                  -- online classes: Zoom/Meet link (also enables Phase 2 auto-attendance)
  burn_policy              text        DEFAULT 'always_bill'  -- inherits from org_settings unless overridden
  status                   text        DEFAULT 'active'  -- 'active' | 'paused' | 'archived'
  schedule                 jsonb       NOT NULL  -- per-day slots, see shape below
  notes                    text
  created_at               timestamptz DEFAULT now()
  updated_at               timestamptz DEFAULT now()

  INDEX (org_id)
  INDEX (org_id, status)
  INDEX (org_id, program_id)
  INDEX (org_id, level_id)
}
```

**Schedule JSONB shape (as built):** each day carries its own time, so a class can meet at different times on different days.
```json
{
  "recurrence": "weekly",
  "slots": [
    { "day": "tue", "time": "20:00" },
    { "day": "thu", "time": "21:30" }
  ],
  "durationMinutes": 60
}
```

---

### `class_teachers`
M:N between classes and teachers. One teacher may be marked primary. Today a class is taught by a single assigned teacher; this table keeps the door open for co-teachers/substitutes.

```ts
class_teachers {
  id          uuid        PK DEFAULT gen_random_uuid()
  org_id      text        NOT NULL
  class_id    uuid        NOT NULL  -- FK → classes.id
  teacher_id  uuid        NOT NULL  -- FK → teachers.id
  is_primary  boolean     DEFAULT false
  rate_override numeric(10,2)       -- null = use the class's teacher_rate_per_session (rare per-teacher override, e.g. senior substitute)
  assigned_at timestamptz DEFAULT now()

  UNIQUE (class_id, teacher_id)
  INDEX (org_id, class_id)
  INDEX (org_id, teacher_id)
}
```

> **REMOVED:** the original draft had a `teacher_rates` table (per-teacher rate keyed by class_type). It was **dropped** in migration 0002. Teacher pay now lives on the class (`classes.teacher_rate_per_session`), with `class_teachers.rate_override` as the per-assignment exception. See research 2026-06-26.

---

### `sessions`
**LAZY (as-built 2026-06-27).** Sessions are NOT pre-generated. Each class stores its weekly schedule; upcoming dates are computed on the fly. A real row is materialised only when acted on (attendance taken, or the session is cancelled). `taught_by_teacher_id` = who actually taught (drives pay in M4); defaults to the class's assigned teacher, overridable for substitutes.

```ts
sessions {
  id                   uuid        PK DEFAULT gen_random_uuid()
  org_id               text        NOT NULL
  class_id             uuid        NOT NULL  -- FK → classes.id
  scheduled_at         timestamptz NOT NULL  -- exact date+time of the session
  taught_by_teacher_id uuid                  -- FK → teachers.id (who taught this occurrence; null until set)
  status               text        DEFAULT 'scheduled'  -- 'scheduled' | 'complete' | 'cancelled'
  cancelled_at         timestamptz
  cancelled_by         text                  -- clerk_user_id
  cancel_reason        text
  notes                text
  created_at           timestamptz DEFAULT now()

  UNIQUE (class_id, scheduled_at)  -- one materialised row per class occurrence (idempotent lazy create)
  INDEX (org_id, class_id)
  INDEX (org_id, scheduled_at)
  INDEX (class_id, scheduled_at)
}
```

---

### `guardians`
The parent/wali: the paying contact for one or more students. A first-class entity: the billing target (M4), the family link (siblings share one guardian), and the future parent-app login. One guardian, many students.

```ts
guardians {
  id              uuid        PK DEFAULT gen_random_uuid()
  org_id          text        NOT NULL
  clerk_user_id   text                  -- future: parent self-service login
  name            text        NOT NULL
  phone           text
  email           text
  notes           text
  status          text        DEFAULT 'active'  -- 'active' | 'archived'
  created_at      timestamptz DEFAULT now()
  updated_at      timestamptz DEFAULT now()

  INDEX (org_id)
  INDEX (org_id, status)
}
```

---

### `students`
The guardian's contact details are **not** duplicated on the student; they live on `guardians`, linked via `guardian_id`.

```ts
students {
  id              uuid        PK DEFAULT gen_random_uuid()
  org_id          text        NOT NULL
  clerk_user_id   text                  -- set if student has a login (future)
  name            text        NOT NULL
  ic_number       text
  date_of_birth   date
  gender          text                  -- 'male' | 'female' | 'prefer_not_to_say'
  phone           text
  email           text
  guardian_id     uuid                  -- FK → guardians.id (the paying contact; nullable)
  address         text
  current_level   text                  -- free text: "Grade 5", "Iqra' 3", "IELTS Band 6"
  status          text        DEFAULT 'active'  -- 'active' | 'paused' | 'dropped' | 'graduated'
  notes           text
  created_at      timestamptz DEFAULT now()
  updated_at      timestamptz DEFAULT now()

  INDEX (org_id)
  INDEX (org_id, status)
}

student_level_history {
  id          uuid        PK DEFAULT gen_random_uuid()
  student_id  uuid        NOT NULL  -- FK → students.id
  org_id      text        NOT NULL
  level       text        NOT NULL
  changed_by  text        NOT NULL  -- clerk_user_id
  changed_at  timestamptz DEFAULT now()
}
```

---

### `enrollments`
The link between a student and a class. Drives billing and attendance inclusion.

```ts
enrollments {
  id                  uuid        PK DEFAULT gen_random_uuid()
  org_id              text        NOT NULL
  student_id          uuid        NOT NULL  -- FK → students.id
  class_id            uuid        NOT NULL  -- FK → classes.id
  started_at          date        NOT NULL
  ended_at            date                  -- null if still active
  status              text        DEFAULT 'active'  -- 'active' | 'paused' | 'ended'
  fee_override        numeric(10,2)         -- if null, use class.monthly_fee
  discount_type       text                  -- 'flat' | 'percent' | null
  discount_value      numeric(10,2)         -- amount or percent
  mid_join_session_id uuid                  -- FK → sessions.id (null if enrolled from start)
  mid_join_notes      text                  -- e.g. "Started at Surah Al-Baqarah ayat 45"
  created_at          timestamptz DEFAULT now()
  updated_at          timestamptz DEFAULT now()

  UNIQUE (student_id, class_id, started_at)
  INDEX (org_id, class_id)
  INDEX (org_id, student_id)
  INDEX (org_id, status)
}
```

---

### `attendance_records`
One row per (student, session) pair.

```ts
attendance_records {
  id              uuid        PK DEFAULT gen_random_uuid()
  org_id          text        NOT NULL
  session_id      uuid        NOT NULL  -- FK → sessions.id
  student_id      uuid        NOT NULL  -- FK → students.id
  class_id        uuid        NOT NULL  -- denormalised for query performance
  status          text        NOT NULL  -- 'present' | 'absent' | 'late' | 'excused' | 'unmarked'
  source          text        DEFAULT 'manual'  -- 'manual' | 'zoom' | 'meet' (Phase 2 auto-attendance)
  marked_by       text        NOT NULL  -- clerk_user_id (teacher or admin)
  marked_at       timestamptz DEFAULT now()
  notes           text
  updated_at      timestamptz DEFAULT now()

  UNIQUE (session_id, student_id)
  INDEX (org_id, session_id)
  INDEX (org_id, student_id)
  INDEX (org_id, class_id, marked_at)
}
```

**Attendance rate query (per class, last N sessions):**
```sql
SELECT
  COUNT(*) FILTER (WHERE status = 'present' OR status = 'late') AS attended,
  COUNT(*) FILTER (WHERE status != 'unmarked') AS marked,
  ROUND(
    COUNT(*) FILTER (WHERE status = 'present' OR status = 'late')::numeric
    / NULLIF(COUNT(*) FILTER (WHERE status != 'unmarked'), 0) * 100, 1
  ) AS rate_pct
FROM attendance_records
WHERE org_id = $orgId
  AND class_id = $classId
  AND session_id IN (
    SELECT id FROM sessions
    WHERE class_id = $classId AND status = 'complete'
    ORDER BY scheduled_at DESC
    LIMIT 4
  )
```

---

### `invoices`
**M4 (2026-06-27): FAMILY invoice.** One invoice per **payer** per month, covering all that payer's children's active enrollments. The payer is normally the **guardian**; for an adult learner with no guardian, `student_id` is the payer (fallback). Exactly one of `guardian_id` / `student_id` is set. Created on demand by the manual "Run billing" action (born as `draft`). **Overdue is computed** (issued/partial past `due_at`), not a stored status.

```ts
invoices {
  id                uuid        PK DEFAULT gen_random_uuid()
  org_id            text        NOT NULL
  guardian_id       uuid                  -- FK → guardians.id (the payer; null for adult-learner invoices)
  student_id        uuid                  -- FK → students.id (payer fallback when no guardian; null for family invoices)
  public_token      text        NOT NULL  -- hard-to-guess token for the shareable invoice/payment link
  invoice_number    text        NOT NULL  -- e.g. INV-202508-0042 (prefix from org_settings)
  billing_month     date        NOT NULL  -- first day of the billed month (e.g. 2025-08-01)
  issued_at         timestamptz
  due_at            timestamptz
  total_amount      numeric(10,2) NOT NULL
  paid_amount       numeric(10,2) DEFAULT 0  -- sum of VERIFIED payments minus refunds
  status            text        DEFAULT 'draft'
    -- 'draft' | 'issued' | 'partially_paid' | 'paid' | 'voided'  (overdue is computed)
  notes             text
  deleted_at        timestamptz           -- soft delete only
  created_at        timestamptz DEFAULT now()
  updated_at        timestamptz DEFAULT now()

  UNIQUE (org_id, guardian_id, billing_month) WHERE guardian_id IS NOT NULL  -- one family invoice per guardian per month
  UNIQUE (org_id, student_id, billing_month)  WHERE guardian_id IS NULL      -- one per adult-learner per month
  UNIQUE (public_token)
  INDEX (org_id, guardian_id)
  INDEX (org_id, student_id)
  INDEX (org_id, status)
  INDEX (org_id, billing_month)
}
```

---

### `invoice_line_items`
One row per child's class enrollment per invoice, plus optional non-class lines (manual discount / adjustment / credit). `student_id` groups lines by child on the family invoice. For non-class lines, `enrollment_id` / `class_id` / `class_name` are null and `line_total` may be **negative**.

```ts
invoice_line_items {
  id              uuid        PK DEFAULT gen_random_uuid()
  org_id          text        NOT NULL
  invoice_id      uuid        NOT NULL  -- FK → invoices.id
  item_type       text        DEFAULT 'tuition'  -- 'tuition' | 'discount' | 'adjustment' | 'credit'
  student_id      uuid                  -- FK → students.id (which child; null = family-level line)
  student_name    text                  -- snapshot of the child's name (null for family-level lines)
  enrollment_id   uuid                  -- FK → enrollments.id (null for non-class lines)
  class_id        uuid                  -- FK → classes.id (null for non-class lines)
  class_name      text                  -- snapshot at invoice time (null for non-class lines)
  description     text                  -- free text for adjustment / credit lines
  base_amount     numeric(10,2) NOT NULL
  discount_type   text                  -- 'flat' | 'percent' | null
  discount_value  numeric(10,2)
  discount_amount numeric(10,2) DEFAULT 0  -- computed: if flat = discount_value, if percent = base * discount_value/100
  sessions_total  smallint              -- total sessions in billing month (for future prorate)
  sessions_absent smallint              -- absent sessions (for future prorate burn policy)
  line_total      numeric(10,2) NOT NULL  -- base_amount - discount_amount; may be negative for credit/adjustment
  created_at      timestamptz DEFAULT now()

  INDEX (invoice_id)
  INDEX (org_id, class_id)
  INDEX (org_id, student_id)
}
```

---

### `payments`
Money received against an invoice (or paid back as a refund). `amount` is always positive; `kind` distinguishes payment vs refund. **Only `verified` payments count** toward the invoice `paid_amount`. Operator-recorded payments are verified immediately; customer self-service uploads (slice 1.5) start `pending` until an operator verifies.

```ts
payments {
  id              uuid        PK DEFAULT gen_random_uuid()
  org_id          text        NOT NULL
  invoice_id      uuid        NOT NULL  -- FK → invoices.id
  student_id      uuid                  -- FK → students.id (nullable for family invoices)
  kind            text        DEFAULT 'payment'  -- 'payment' | 'refund'
  amount          numeric(10,2) NOT NULL  -- always positive
  method          text        NOT NULL  -- 'cash' | 'bank_transfer' | 'duitnow' | 'other' | (later 'fpx_online')
  status          text        DEFAULT 'verified'  -- 'pending' | 'verified' | 'rejected'
  source          text        DEFAULT 'operator'  -- 'operator' | 'self_service'
  reference       text                  -- transaction ID, receipt no., etc.
  receipt_file_id uuid                  -- FK → media_files.id (attached proof image/PDF)
  paid_at         timestamptz NOT NULL
  recorded_by     text        NOT NULL  -- clerk_user_id, 'system', or 'self_service'
  verified_by     text                  -- clerk_user_id who verified a self-service payment
  verified_at     timestamptz
  gateway_name            text          -- 'fiuu' | 'stripe' | 'ipay88' | null (reserved for slice 2)
  gateway_transaction_id  text
  gateway_status          text
  notes           text
  deleted_at      timestamptz           -- soft delete only
  created_at      timestamptz DEFAULT now()

  INDEX (org_id, invoice_id)
  INDEX (org_id, student_id)
  INDEX (org_id, status)
}
```

---

### `invoice_events`
Immutable append-only audit log for every invoice status change.

```ts
invoice_events {
  id          uuid        PK DEFAULT gen_random_uuid()
  org_id      text        NOT NULL
  invoice_id  uuid        NOT NULL  -- FK → invoices.id
  event_type  text        NOT NULL
    -- 'created' | 'issued' | 'payment_recorded' | 'payment_submitted' | 'payment_verified'
    -- | 'payment_rejected' | 'partially_paid' | 'paid' | 'refunded' | 'adjusted' | 'voided'
    -- | 'reminder_copied' | 'note_added'
  payload     jsonb                 -- event-specific data (payment amount, old/new status, etc.)
  actor       text        NOT NULL  -- clerk_user_id or 'system'
  occurred_at timestamptz DEFAULT now()

  INDEX (invoice_id)
  INDEX (org_id, invoice_id)
}
```

---

### `media_files`
**M4 (2026-06-27).** Every uploaded or generated file (payment receipts, the org's DuitNow QR, future logos/photos). The central media service stores optimised derivatives in a private Wasabi bucket (WebP for images, original + first-page preview for PDFs) and returns a row; the app references files by id and fetches via short-lived signed URLs.

```ts
media_files {
  id            uuid        PK DEFAULT gen_random_uuid()
  org_id        text        NOT NULL
  kind          text        NOT NULL  -- 'receipt' | 'duitnow_qr' | 'logo' | 'other'
  original_name text
  mime_type     text        NOT NULL  -- stored type (image/webp, application/pdf)
  byte_size     integer     NOT NULL  -- size of the stored (optimised) file
  storage_key   text        NOT NULL  -- Wasabi object key for the view/full file
  thumbnail_key text                  -- Wasabi object key for the thumbnail (null if none)
  width         integer
  height        integer
  uploaded_by   text        NOT NULL  -- clerk_user_id or 'self_service'
  created_at    timestamptz DEFAULT now()

  INDEX (org_id)
  INDEX (org_id, kind)
}
```

---

## Derived / Computed Values

These are never stored; always computed at query time:

| Value | How computed |
|---|---|
| Class health (green/yellow/red) | Enrolment count vs capacity + attendance rate last 4 sessions |
| Outstanding balance per student | SUM(invoices.total_amount) - SUM(payments.amount) WHERE status != 'voided' |
| Teacher session count (month) | COUNT(sessions) WHERE taught_by_teacher_id = teacher AND scheduled_at in pay period (drives M4 pay) |
| Consecutive absences | Window function over attendance_records ORDER BY session scheduled_at |
| Invoice `overdue` status | Scheduled job: UPDATE invoices SET status='overdue' WHERE due_at < now() AND status IN ('issued','partially_paid') |

---

## Background Jobs

> The original draft had a `generate-sessions` daily cron. With the LAZY session model (2026-06-27) it no longer exists: session dates are computed from the class schedule and rows are created on demand. The two billing jobs below belong to M4 (not built yet).

| Job | Trigger | What it does |
|---|---|---|
| `generate-invoices` | Monthly (day 25 at 06:00 MYT) | For each org: create invoices for all active enrollments for next month [M4, not built] |
| `mark-overdue` | Daily cron (00:01 MYT) | Flip `issued` to `overdue` for invoices past due_at [M4, not built] |

---

## Tenant Isolation Rules for Query Layer

Every Drizzle query that touches a tenant-scoped table MUST:

```ts
// ✅ Correct
db.select().from(classes).where(
  and(eq(classes.org_id, orgId), eq(classes.status, 'active'))
)

// ❌ Wrong: no org_id filter
db.select().from(classes).where(eq(classes.status, 'active'))
```

Server Actions and API routes pull `orgId` from the Better Auth session (via `requireOrgId` / `getAccessContext`), never from the request body or URL params:

```ts
const { orgId } = await auth()
if (!orgId) throw new Error('No active organization')
// orgId is now safe to use in queries
```

---

## Migration Plan

Migrations are generated by `drizzle-kit` and live in `kelas/migrations/` (numbered `0000`, `0001`, ...). The as-built deltas in this doc landed across `0001` (additions: programs, levels, guardians, new class/session/attendance columns) and `0002` (dropped `teacher_rates`). Run `npm run db:migrate`; seed dev data with `npm run db:seed`.

---

*Data model is the source of truth before any code is written. PRD requirements trace back to this schema. Changes here cascade to build prompts and test cases.*
