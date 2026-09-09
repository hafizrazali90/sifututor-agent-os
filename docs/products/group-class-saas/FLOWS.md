# Kelasapp - User Flows (happy path + edge cases)

> Per-module catalog of what actually happens, step by step, for every built module:
> the happy path plus the edge cases and failure paths the system handles.
>
> Source of truth: this is reconciled to the **built behaviour** (services, routes, and
> the 83 unit/integration tests), not aspirations. The PRD holds the user stories and
> requirements; this holds the flows. A "(test)" tag means the edge case is covered by
> an automated test. Last reconciled: 2026-06-30.

## Conventions used below

- **Roles:** `operator` (full access), `staff` (admin subset), `teacher` (linked to a `teachers` row by email on first login, scoped to attendance + their own classes). These are assigned Better Auth organisation membership roles, not derived from an auth-provider admin/member flag.
- **Tenant rule (all modules):** every read/write is scoped to the signed-in org. A request for another org's record returns not-found / is rejected, never leaked (covered by a tenant-isolation test in every service).
- **Money/format:** RM, DD/MM/YYYY, Asia/Kuala_Lumpur, validation messages bilingual EN/BM.
- **Empty state:** every list renders an explicit "nothing yet" message, never a blank table.

---

## 0. Auth, roles & onboarding (cross-cutting)

**Happy path**
1. User signs in via Better Auth. With no org, they are redirected to org onboarding/selection.
2. With an org, an `operator`/`staff` lands on the dashboard; a `teacher` lands on Attendance.
3. Role is the assigned Better Auth organisation membership role (operator/staff/teacher); a member linked to a teacher row resolves as teacher.

**Edge cases**
| Situation | Behaviour |
|---|---|
| No org context | Pages redirect to org selection; APIs return 401 |
| Teacher opens an operator page (e.g. /payroll) | Redirected to Attendance (operator route group guard) |
| Teacher calls an admin API directly | 401 (requireOperatorContext throws) |
| Teacher accesses a class they do not teach | 403 (attendance APIs ownership-scoped) |
| New teacher's first login | Linked to their `teachers` row by matching email |

---

## 1. Classes (M1) + Taxonomy

**Happy path (create a class)**
1. Operator opens Classes, clicks Add.
2. Fills name; optionally Program + Level; optionally a single Teacher; type, mode, capacity min/max; monthly fee; **how the teacher is paid** (per session / per student) + rate; per-day weekly schedule; notes.
3. Saves. Class appears in the active list; name links to the class detail page (roster, assigned teacher, attendance rate).

**Edge cases**
| Situation | Behaviour |
|---|---|
| Required field empty (name) | Hard-blocked, bilingual "required" message |
| Capacity max < min | Blocked, "max must be >= min" (schema refine) |
| Fee/rate with >2 decimals | Blocked, "use at most 2 decimal places" |
| Invalid schedule time / no day added | Blocked ("use 24-hour time" / "add at least one day") |
| No programs/levels set up yet | Field shows an empty-state hint with a link to set them up |
| Assigning a teacher from another org | Silently ignored (tenant guard) (test) |
| Archive a class | Removed from the active list, kept for history (test); excluded from class-health |
| Edit changes the pay model/rate | Affects future sessions only; already-taught sessions keep their frozen pay |

**Taxonomy (Programs / Levels)**
- Happy: add, rename, archive an org-managed list item; used to categorise/filter classes.
- Edge: archived items excluded from the active list (test); cannot archive another org's item (test); duplicate names allowed (free-text list).

---

## 2. Students, Guardians, Enrolments (M2)

### Students
**Happy path:** create student (name + optional IC/passport, DOB, gender, phone, email, guardian, level, address, notes) -> appears in list -> detail page shows profile, level history, enrolled classes; IC is masked by default with a reveal toggle.

**Edge cases**
| Situation | Behaviour |
|---|---|
| IC vs passport | Toggle picks the type; IC hard-validated (12 digits + DOB + state code), passport loose alphanumeric |
| Invalid phone / email / DOB (future or pre-1900) | Hard-blocked, bilingual message |
| Link a guardian from another org | Rejected (test) |
| Change level | New `student_level_history` row recorded; initial level recorded on create (test) |
| Status = dropped | Drops out of the default list; still searchable via filter (test) |
| Add a new guardian inline | Creates the guardian, then the student, in one flow |

### Guardians
- Happy: CRUD; detail page shows linked students + their invoices.
- Edge: empty optional fields cleaned to null (test); archive removes from active list (test); cannot read/archive another org's guardian (test).

### Enrolments
**Happy path:** from a class (pick student) or from a student (pick class); set start date; optional fee override; optional mid-join note. Appears on both the class roster and the student's class list.

**Edge cases**
| Situation | Behaviour |
|---|---|
| Duplicate (same student + class + start date) | Rejected as duplicate (409) (test) |
| Student and class in different orgs | Rejected, invalid refs (422) (test) |
| Fee override set | Effective fee = override, else class monthly fee (test) |
| End an enrolment | Stamped with an end date, dropped from the roster, kept in student history (test) |
| Pause / resume | Status toggles; paused enrolments are skipped by billing |

---

## 3. Attendance + Reports (M3)

**Happy path (mark attendance)**
1. Operator (or the assigned teacher) opens Attendance, sees today's classes with status (pending/complete).
2. Opens a class: roster of enrolled students, each toggled present / absent / late / excused (or "Mark all present"), optional per-student note.
3. Saves once. The session row is **materialised on first mark** (lazy), status set to complete, and **teacher pay is frozen** onto the session (per-session = rate; per-student = rate x present).

**Edge cases**
| Situation | Behaviour |
|---|---|
| Marking on a day the class does not meet | Rejected, `no_session_day` (test) |
| Editing older than the 7-day window | Rejected, `window_closed` (test) |
| A student left unmarked | Stays unmarked, never counted as absent (test) |
| "Today" near midnight | Computed in Asia/Kuala_Lumpur |
| Teacher marks a class they do not teach | 403 (ownership-scoped) |
| Re-marking (within window) | Upserts statuses; recomputes the frozen pay |
| 3+ consecutive absences | Surfaced as an absence alert (test) |

**Reports**
- Happy: per-student and per-class attendance over a date range; on-screen + server PDF + CSV; weekly trend chart.
- Edge: empty range shows a no-data state; rate excludes unmarked + excused; org-isolated (test).

---

## 4. Billing & Invoicing (M4)

**Happy path (run billing -> collect)**
1. Operator picks a month, clicks **Run billing**: one **family invoice per guardian** (line items grouped by child across all their classes); adult learners billed directly. Born as drafts.
2. Issues all (or one). Shares via WhatsApp click-to-chat or Copy link; downloads the invoice PDF.
3. Records a payment (cash / bank transfer / other), optionally attaching a receipt; or the guardian self-serves on the public invoice page.
4. Invoice moves issued -> partially_paid -> paid.

**Edge cases**
| Situation | Behaviour |
|---|---|
| Re-run billing for the same month | Idempotent: no duplicates; tops up a draft with newly-enrolled children (test) |
| Paused enrolment | Skipped in generation (test) |
| Overpayment | Rejected, `exceeds_balance` (test) |
| Recording payment on a draft | Rejected (must be issued) (test) |
| Refund + "reduce the bill" | Adds a matching credit so the invoice stays settled (test) |
| Refund only (no reduce) | Reopens the balance (test) |
| Manual discount / credit | Lowers the total (test) |
| Void an invoice | Excluded from guardian outstanding; audit kept (test) |
| Public link to a draft | Hidden by token; only an issued invoice is returned (test) |
| Self-service receipt upload | Creates a **pending** payment that does not count until an operator verifies (test) |
| Operator rejects a pending upload | Invoice left untouched (test) |
| Self-service submit on a voided invoice | Blocked (test) |
| Overdue | Computed for issued invoices past the due date (test) |

**Deferred (post-MVP):** FPX gateway + webhook, auto-cron generation, auto-proration, LHDN e-invoice, follow-up status tracking.

---

## 5. Teachers (M5)

- **Happy:** create teacher (name + optional IC/passport, phone, email, bank name/account, grade); detail page shows profile, payout (bank) details, and assigned classes; bank account + IC masked by default.
- **Edge:** grade defaults to null/ungraded, empty optional fields cleaned (test); bank account digits-only; deactivate moves them off the active list but keeps records (test); a deactivated teacher who taught is still paid for those sessions; cannot read/deactivate another org's teacher (test).

---

## 6. Operator Dashboard (M6)

- **Happy:** KPI cards (active students, active classes, outstanding RM, 30-day attendance); billed-vs-collected 12-month chart; recent verified payments (payer links to their detail); absence-alerts queue; unpaid-invoices queue; per-class health grid.
- **Edge:** attendance rate null when nothing marked (test); trend zero-fills empty months and excludes voided (test); recent payments newest-first with payer name + this-month count (test); class health counts active enrolments only and excludes archived classes (test); each section has an empty state.

---

## 7. Teacher pay / Payroll (M4 slice 2)

**Happy path**
1. Each class is set to pay **per session** (flat) or **per student** (rate x attendees); the rate is frozen onto every session when attendance is marked.
2. Operator opens Teacher pay, picks a month, clicks **Run payroll**: a draft payout per teacher, summing their completed sessions x frozen pay.
3. Reviews a teacher's payout (line per session: date, class, rate, present, amount), pays them outside the app, then **Mark as paid** (method + date + reference). Downloads the payslip PDF.

**Edge cases**
| Situation | Behaviour |
|---|---|
| Re-run payroll | Idempotent: refreshes drafts, never duplicates lines/pay (test) |
| Class rate edited after teaching | Pay unchanged (rate frozen per session) (test) |
| Per-student class | Pay = rate x students present that session (test) |
| Cancelled session | Excluded (only completed sessions pay) |
| Substitute taught the class | The actual teacher (taughtBy) is paid, not the assigned one |
| Class rate never set | Line shows RM0 with a "rate not set" flag |
| Mark paid, then re-run | The paid period is skipped, untouched (test) |
| Mark a non-draft paid again | Rejected, `not_draft` (test) |
| Void a payout | Frees its sessions so the month can be regenerated; hidden from the list (test) |
| Void an already-void payout | Rejected, `already_void` |
| Session completed after the period was paid | Stays unclaimed (a straggler); handle next period (paid record never mutated) |

**Deferred:** adjustments/bonuses, partial payments, bank automation. (Statutory deductions do not apply: teachers are sessional contractors, not staff.)

---

## 8. Cross-cutting flows

**Input validation (every form):** invalid IC/passport, phone, bank account, money precision, and DOB are hard-blocked with bilingual messages from one shared Zod layer (form + API). 11 validator tests.

**Sensitive data:** IC and bank account masked by default with a reveal toggle (teacher + student detail). Never masked: the org's own receiving account / DuitNow QR on the public invoice (the payer must see it), and phone/email (operators need them).

**Multi-tenancy:** every service has a tenant-isolation test; cross-org reads/writes are rejected or not-found.

**Localisation:** every screen EN + BM; en/ms key parity enforced.

---

## 9. AI Layer (M7) - NOT BUILT

Planned in the PRD (health narratives, draft WhatsApp, at-risk detection, placement). No flows yet; this section is a placeholder until the module is designed and built.

---

## Known flow gaps / not yet covered

- **UI/flow edge cases are not E2E-tested** (empty states, role-denied redirects, double-submit, validation display). They are smoke-checked manually; service-layer edge cases are the ones with automated tests.
- **Concurrency** (two operators acting on the same invoice/payout at once) relies on DB transactions + `FOR UPDATE` + unique constraints; not explicitly load-tested.
- **Teacher pay straggler** (session completed after a paid period) is defined behaviour but has no dedicated UI surface yet.
