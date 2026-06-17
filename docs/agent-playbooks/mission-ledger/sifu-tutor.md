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
- **Source:** Codex review/fix/deploy of profile-features PR #1580, 2026-06-17.
- **Next action:** Promote concrete cleanup items to GitHub issues when they become implementation-ready.
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
