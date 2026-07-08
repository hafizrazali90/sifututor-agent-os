# SIMS / sifu-tutor Mission Ledger

Use this for SIMS missions, child tasks, adjacent ideas, and paused follow-ups.

## Missions

### SIMS-BILLING-ALLOC-LEGACY-001 — Paid/Legacy Billing Allocation Backlog

- **Project:** sifu-tutor
- **Status:** promoted
- **Type:** mission
- **Parent:** none
- **End goal:** Historical paid/legacy invoice allocation findings are reviewed and repaired with finance-safe rules, without bulk-mutating paid invoice history.
- **Why it matters:** The June 2026 production repair closed the urgent tutor-blocking allocator issues: missing hidden next-cycle drafts, hidden-draft `total_classes` deficits, and Tier A unpaid-to-unpaid class allocation mismatches. A separate `billing:audit --summary` still reported a large paid/legacy backlog (`tier_b`, `tier_c`, and duplicate empty invoice findings). These are not safe for broad auto-repair because paid invoice history, parent payment records, tutor commission, and reporting may depend on them.
- **Source:** Codex billing-cycle production repair session, 2026-06-16.
- **Next action:** Design a finance-reviewed audit plan that classifies paid/legacy findings by risk and identifies which can be safely repaired, ignored, or need manual admin review.
- **Promote to:** GitHub issue
- **Links:** `Sifututor/sifu-tutor#1572`, `Sifututor/sifu-tutor#1573`, `Sifututor/sifu-tutor#1574`

### SIMS-BILLING-ALLOC-LEGACY-001.A1 — Paid-Invoice Duplicate Postponed Class Review

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** adjacent
- **Parent:** SIMS-BILLING-ALLOC-LEGACY-001
- **End goal:** Historical duplicate postponed class rows on paid invoices are classified and either left alone or cleaned with finance-approved rules, without altering paid invoice or tutor-payment history accidentally.
- **Why it matters:** The 2026-06-24 production repair cleaned only 8 active unpaid/draft duplicate postponed rows after a fresh DB backup. The same diagnosis still showed 221 active and 104 inactive clean-looking duplicate postponed extras on paid invoices; these were intentionally not touched because paid invoice history is finance-sensitive.
- **Source:** Codex postponed duplicate class production repair session, 2026-06-24.
- **Next action:** Decide with finance/product whether paid-invoice duplicate postponed rows should remain as historical audit noise or be cleaned through a separate reviewed script.
- **Promote to:** GitHub issue
- **Links:** `Sifututor/sifu-tutor#1637`, `Sifututor/sifu-tutor#1640`, production deploy `7794f9e67`, Koda `mem_5b825d408b45`

### SIMS-CLASS-LIFECYCLE-001 — Clear Class Lifecycle Model

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** SIMS has a clearer class/session model where schedule, reschedule/postpone history, attendance, verification, quota, invoice allocation, and tutor-payment state are understandable without reading raw duplicate-looking rows in `classes`.
- **Why it matters:** The current model stores both the live class and lifecycle history in the same table, so postponed/rescheduled flows can look like extra classes, confuse staff review, and make quota/invoice diagnosis harder even when the allocator excludes postponed rows correctly.
- **Source:** Hafiz class lifecycle redesign discussion and postponed duplicate repair session, 2026-06-24.
- **Next action:** Hafiz decision gate for Phase 4: approve or adjust the tutor-app-only same-row postpone backend contract, then create the implementation issue/branch before coding.
- **Promote to:** PRD
- **Links:** `Sifututor/sifu-tutor#1637`, `Sifututor/sifu-tutor#1640`, `Sifututor/sifu-tutor#1648`, Koda `mem_5b825d408b45`, `sifu-tutor/docs/features/class-lifecycle-option-c/phase-4-readiness.md`

### SIMS-CLASS-LIFECYCLE-001.A1 — Planning Reservation Ledger For Future Scheduling

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** adjacent
- **Parent:** SIMS-CLASS-LIFECYCLE-001
- **End goal:** Scheduled future classes reserve quota through a dedicated planning reservation ledger instead of using hidden draft invoice rows as the temporary bucket.
- **Why it matters:** Issue #1683 uses a hidden recurring draft invoice as the short-term fix for tutors who schedule ahead after quota is planning-full. That is safe for the current schema, but the cleaner long-term model is shadow planning data that becomes real invoice membership only when a class is attended or verified.
- **Source:** Hafiz billing allocator timing-gap session, 2026-07-08.
- **Next action:** When Option C resumes, design a reservation table/ledger contract covering create, cancel, reschedule, attended/verify conversion, admin visibility, parent visibility, allocator handoff, and migration from hidden draft buckets.
- **Promote to:** PRD
- **Links:** `Sifututor/sifu-tutor#1683`, `sifu-tutor/docs/features/class-lifecycle-option-c/prd.md`, `sifu-tutor/docs/features/billing-cycle-revamp/DECISIONS-AND-OPERATIONS.md`

### SIMS-NOTIF-MATCH-001 — Shared Tutor Candidate Ranking For Opportunity Notifications

- **Project:** sifu-tutor
- **Status:** paused
- **Type:** mission
- **Parent:** none
- **End goal:** Tutor opportunity notifications use the same subject-aware matching/ranking logic as the rest of SIMS, while notification code only handles delivery limits, dedupe, daily caps, and channel rules.
- **Why it matters:** The live notification spam fix reduced volume, but the notification-specific matcher still uses a simpler level/mode/city rule. That can make opportunity notifications less accurate than the shared matching engine, especially when subject data exists.
- **Source:** Codex notification batching/matching session, 2026-06-12.
- **Next action:** Discuss architecture with Claude before implementation: direct `TutorMatchingService` reuse versus extracting a shared `TutorCandidateRankingService`.
- **Promote to:** GitHub issue
- **Links:** `sifu-tutor/docs/features/tutor-opportunity-matching/design-brief.md`, `sifu-tutor/docs/features/tutor-opportunity-matching/ranking-service-refactor-brief.md`

### SIMS-NOTIF-MATCH-001.A1 — Notification Queue Hygiene And Failed Job Policy

- **Project:** sifu-tutor
- **Status:** done
- **Type:** adjacent
- **Parent:** SIMS-NOTIF-MATCH-001
- **End goal:** SIMS has a clear operational policy for old failed notification jobs and future-delayed class reminder queue depth, so staff can distinguish healthy delayed reminders from real queue failures.
- **Why it matters:** After the quiet-hours retry fix, old failed notification jobs remained in production. Some were stale reminders and should not be retried blindly, but the queue depth could still look alarming without a dashboard/policy.
- **Source:** Codex production notification queue investigation and PR #1558, 2026-06-14.
- **Next action:** Closed for queue hygiene. Track the remaining two `SendPushNotificationJob` provider/token failures as a separate push-token hygiene follow-up if they keep recurring.
- **Promote to:** GitHub issue
- **Links:** `Sifututor/sifu-tutor#1557`, `Sifututor/sifu-tutor#1558`, `Sifututor/sifu-tutor#1577`, `Sifututor/sifu-tutor#1578`, production deploy `b2782479c`, cleanup archive `queue-cleanup/notification-failed-jobs-20260617-041115.json`

### SIMS-NOTIF-MATCH-001.A2 — Production Failed Notification Job Follow-Up

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** adjacent
- **Parent:** SIMS-NOTIF-MATCH-001
- **End goal:** Production failed notification jobs are classified and handled without blindly retrying stale or confusing notifications.
- **Why it matters:** During the 2026-06-17 request-amendment production release, production stayed healthy on the new SHA, but `failed_jobs` remained at 54 and pending jobs were about 16k, mostly notification-related. Failed count did not increase during the release monitor window, so this was not caused by PR #1579, but it still needs a safe queue-cleanup policy.
- **Source:** Codex request-amendment production deployment closeout, 2026-06-17; reconfirmed during profile-features production deployment closeout later the same day.
- **Next action:** Run a read-only failed-job classification by job type, notification type, created time, and likely user-facing risk; do not retry or delete until Hafiz approves a cleanup plan.
- **Promote to:** GitHub issue
- **Links:** `Sifututor/sifu-tutor#1579`, `Sifututor/sifu-tutor#1580`, production deploys `213c1b020`, `652023846`

### SIMS-TUTOR-PROFILE-001 — Tutor Profile And Service Preference Reliability

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** Tutor profile/service-preference data stays consistent across the tutor app, SIMS portal, and future enhanced-data collection rollouts.
- **Why it matters:** Availability, language proficiency, mode/class-type options, and mobile logout behavior now cross the backend, portal, and mobile API boundary. Small contract drift can affect old app builds or staff profile edits.
- **Source:** Codex review/fix/deploy of profile-features PR #1580, 2026-06-17; production EDC availability-save flag cutover, 2026-06-19.
- **Next action:** Have the tutor/app side retry Service Preference Step 3 availability save with a real tutor session; promote remaining cleanup items to GitHub issues when they become implementation-ready.
- **Promote to:** none yet
- **Links:** `Sifututor/sifu-tutor#1580`, production deploy `652023846`

### SIMS-TUTOR-PROFILE-001.A1 — Tutor Details Availability Slot Response Cleanup

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** adjacent
- **Parent:** SIMS-TUTOR-PROFILE-001
- **End goal:** The tutor details API returns availability slots in the same minimal `{day_group, time_band}` shape expected by the mobile app, without leaking row metadata when enhanced data collection is enabled.
- **Why it matters:** PR #1580 shipped availability storage, language proficiency storage, portal edit support, and mobile logout cleanup safely behind `enhanced_data_collection_enabled=false`. The remaining cosmetic follow-up is to keep the future enabled response shape tidy and consistent.
- **Source:** Codex review/fix/deploy of profile-features PR #1580, 2026-06-17.
- **Next action:** Open a small GitHub issue/PR to normalize `availability_slots` in tutor details and keep the existing API-contract tests focused on the minimal shape.
- **Promote to:** GitHub issue
- **Links:** `Sifututor/sifu-tutor#1580`, production deploy `652023846`

### SIMS-TUTOR-PROFILE-001.A2 — Tutor App M10 Notification Preferences Cleanup

- **Project:** sifututor_tutor
- **Status:** captured
- **Type:** adjacent
- **Parent:** SIMS-TUTOR-PROFILE-001
- **End goal:** The tutor app M10 Settings notification preferences screen uses the backend canonical 5-category wording and keys while keeping critical account-status notifications untoggleable.
- **Why it matters:** PR #1610 made the backend production-safe by accepting both the current app's legacy keys and the new canonical keys. The app does not need an emergency fix, but aligning it later avoids long-term API-contract drift.
- **Source:** Codex review/fix/merge/deploy of profile-features PR #1610, 2026-06-18.
- **Next action:** Mobile dev should open a small app cleanup task to update the M10 screen labels/keys to `job_opportunities`, `class_reminders`, `payments_earnings`, `reports_scheduling`, and `tips_guidance`; do not show `account_status`.
- **Promote to:** GitHub issue
- **Links:** `Sifututor/sifu-tutor#1610`, production deploy `696cb0704`

### SIMS-FIUU-PAYMENT-REVIEW-001 — FIUU Pending Review Alerts And Dashboard

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** FIUU payments that cannot be automatically reconciled are visible to Finance/Admin through alerts and a pending-review queue.
- **Why it matters:** PR #1609 fixed the silent ordering-guard drop for successful FIUU callbacks, but `mismatch_review` still depends on staff noticing the issue manually. Successful bank payments should never stay invisible until a parent complaint.
- **Source:** Codex FIUU ordering-guard hotfix/deploy/data-repair session, 2026-06-18.
- **Next action:** Open a GitHub issue for Finance/Admin alerting on `mismatch_review`, plus an Operations Centre pending-payment-review section with safe manual resolution steps.
- **Promote to:** GitHub issue
- **Links:** `Sifututor/sifu-tutor#1609`, production deploy `696cb0704`
