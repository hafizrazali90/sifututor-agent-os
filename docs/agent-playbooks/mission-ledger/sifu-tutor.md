# SIMS / sifu-tutor Mission Ledger

Use this for SIMS missions, child tasks, adjacent ideas, and paused follow-ups.

## Missions

### SIMS-BACKUP-DR-001 — Reliable SIMS Backup And Disaster Recovery

- **Project:** sifu-tutor
- **Status:** promoted
- **Type:** mission
- **Parent:** none
- **End goal:** SIMS database records, uploaded files, and server/account configuration have separate off-server backups, monitored retention, and proven restore paths without filling the production disk.
- **Why it matters:** The 2026-07-12 and 2026-07-19 local cPanel backups filled the production disk and disrupted WHM, Redis-backed application work, logging, and API/control-panel availability. The current design uses six-hour database backups, Wasabi as primary with OneDrive temporarily secondary, tiered database retention, and daily incremental upload backups while off-server account/configuration recovery is completed.
- **Source:** Hafiz and Codex SIMS backup design discussion, 2026-07-13.
- **Next action:** Core mission is done. All layered lanes (database, uploads, account home, configuration, account metadata) and the composed recovery point are deployed and proven on production as of 2026-07-28: `recovery-point:compose` succeeded (run `01KYKQTJBJBA0TMGPQ633GAR4Y`), all 7 components verified (6 `remote_verified`, plus `secret_recovery` `verified`), and the remote manifest/runtime objects were independently exact-version GET/HEAD verified (checksum/size, GOVERNANCE retention to 2026-10-26). All 6 BetterStack heartbeats and 3 endpoint monitors are unpaused and `up`. Getting there required 3 real fixes discovered only by running the deployed command for the first time: a scoped Wasabi IAM `GetObjectVersion` addition (database/uploads credentials), #1811/PR #1813 (account_metadata freshness threshold, cron-grounded), and #1816/PR #1817 (secret_recovery freshness threshold, a weaker/borrowed assumption per independent review, plus a production evidence-file reference-scheme correction). Documentation-only PR #1820 saved both required production-smoke reports without redeploying runtime code. Remaining work is follow-up, not core-mission-blocking: see `SIMS-BACKUP-DR-001.2` (progress telemetry), `SIMS-BACKUP-DR-001.3` (database credential scope tightening), and existing `SIMS-BACKUP-DR-001.A1` (live-file optimization). Queue-worker mutex backlog from the original July 19 incident is unrelated and still needs a separate approved repair.
- **Promote to:** PRD
- **Links:** `sifu-tutor/docs/features/backup-disaster-recovery/prd.md`, `sifu-tutor/docs/features/backup-disaster-recovery/build-prompts.md`, `Sifututor/sifu-tutor#1697`, `Sifututor/sifu-tutor#1698`, `Sifututor/sifu-tutor#1811`, `Sifututor/sifu-tutor#1816`, `Sifututor/sifu-tutor#1820`, Koda `mem_a62330809b28`, Koda `mem_18d2c2d5068b`, Koda `mem_286b4aed36fe`, Koda `mem_7433526c84fc`

### SIMS-BACKUP-DR-001.1 — Prove SIMS Backup Scheduler And Heartbeat Recovery

- **Project:** sifu-tutor
- **Status:** done
- **Type:** task
- **Parent:** SIMS-BACKUP-DR-001
- **End goal:** The scheduled production database and uploaded-file backup commands create and remotely verify fresh Wasabi recovery points and keep their BetterStack heartbeats healthy after the July 19 disk-full incident.
- **Why it matters:** The latest database and uploaded-file manifests are remote-verified and recorded sent heartbeats, but later scheduled cycles were missed during the disk-full/Redis incident, leaving both BetterStack monitors down. Without fresh scheduler proof, a silent missed backup may not alert the team.
- **Source:** Codex production backup credential repair and July 19 disk-full recovery, 2026-07-18 to 2026-07-19.
- **Next action:** None — closed 2026-07-28. All 6 BetterStack heartbeats (Database, Uploads, Disk, Account Home, Configuration, Composed Recovery) confirmed `up` and unpaused; all 3 endpoint monitors `up`. No monitor created or deleted.
- **Promote to:** GitHub issue
- **Links:** BetterStack heartbeat API docs; production proof run `01KXRKZFRKASP2W5D8FZ37S7EJ`; final proof run `01KYKQTJBJBA0TMGPQ633GAR4Y`

### SIMS-BACKUP-DR-001.2 — Safe Upload-Backup Progress Telemetry

- **Project:** sifu-tutor
- **Status:** triaged
- **Type:** research
- **Parent:** SIMS-BACKUP-DR-001
- **End goal:** Operators can read processed-objects count, total, percentage, and ETA for a running upload backup without listing filenames, exposing secrets, running a second heavy scan, or keeping an AI session actively polling for hours.
- **Why it matters:** The July 19 supervised upload run's rclone log stayed empty because stats were emitted below the configured log level, leaving only a time-based estimate during a multi-hour operation. There was no safe way to check live progress without re-scanning or exposing more than intended.
- **Source:** SIMS backup production close-out session, 2026-07-28.
- **Next action:** Design a small mode-600 status record or sanitized monitoring metric (processed/total/percentage/ETA only), define update frequency and cleanup, and preserve the existing low CPU/bandwidth safety limits. Related Agent OS lesson: multi-hour external operations should use a background/recheck workflow instead of an agent session actively polling in real time; a request to "stop watching" should stop only the watcher, not the underlying production job, unless explicitly asked.
- **Promote to:** GitHub issue
- **Links:** none yet

### SIMS-BACKUP-DR-001.3 — Tighten Database Backup Credential IAM Scope

- **Project:** sifu-tutor
- **Status:** triaged
- **Type:** task
- **Parent:** SIMS-BACKUP-DR-001
- **End goal:** The `sims-production-backup-uploader` Wasabi IAM policy is scoped to `sims/database/*` only, matching its description, instead of the current broader `sims/*`.
- **Why it matters:** Discovered while diagnosing composed recovery on 2026-07-28: this credential's resource scope already covered all of `sims/*` before this session touched anything. This session only added `s3:GetObjectVersion` to the existing scope per Hafiz's explicit approval and did not widen it further, but the pre-existing breadth itself does not match least-privilege intent and should be tightened separately.
- **Source:** SIMS backup production close-out session, 2026-07-28.
- **Next action:** Confirm no other automation depends on this credential reading outside `sims/database/*`, then narrow the IAM policy's resource ARNs to `sims/database/*` only, and re-prove the database backup lane still succeeds.
- **Promote to:** GitHub issue
- **Links:** none yet

### SIMS-BACKUP-DR-001.A1 — Audit And Optimize SIMS Live File Storage

- **Project:** sifu-tutor
- **Status:** triaged
- **Type:** research
- **Parent:** SIMS-BACKUP-DR-001
- **End goal:** Verify whether SIMS uploaded-file storage is already organized efficiently and design any justified improvements to naming, duplication, compression, retention, serving, deletion, and direct Wasabi storage without risking historical documents.
- **Why it matters:** SIMS currently holds about 55 GB across roughly 223,000 uploaded files. Moving live uploads directly to Wasabi is a promising future option, but it should be treated as a separate storage architecture project after the current backup system is made safe and after existing file behavior is audited rather than assumed.
- **Source:** Hafiz backup brainstorm, 2026-07-13.
- **Next action:** Later run a read-only file-storage audit covering directory conventions, file types and size distribution, duplicates, orphan detection, database references, public/private access rules, deletion behavior, and compatibility requirements before recommending migration or cleanup.
- **Promote to:** PRD
- **Links:** none

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
- **Next action:** When Option C resumes, design a reservation table/ledger contract covering create, cancel, reschedule, attended/verify conversion, admin visibility, parent visibility, allocator handoff, and migration from hidden draft buckets. Include an attendance timing guard before allowing deeper future scheduling: tutors should not be able to mark far-future scheduled classes as attended just because planning capacity exists. The backend should define the allowed attendance window, for example class date is today/past or within an approved start-time grace window.
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
- **Status:** done
- **Type:** adjacent
- **Parent:** SIMS-NOTIF-MATCH-001
- **End goal:** Production failed notification jobs are classified and handled without blindly retrying stale or confusing notifications.
- **Why it matters:** The production investigation separated 787 historical failure records from healthy future-delayed reminder rows. The hotfix corrected payment-mail retry semantics, added provider-call deadlines and duplicate protection, cleaned stale reminder sources, recovered all 728 affected payment emails, and removed the obsolete stuck worker without blindly retrying old serialized jobs.
- **Source:** Codex request-amendment production deployment closeout, 2026-06-17; superseded by the production queue reliability diagnosis and PR #1746 on 2026-07-18.
- **Next action:** Closed for production and staging reliability. PR #1746 is live at `a58f4818c`; 728/728 replacement emails completed with zero new target failures; obsolete worker PID `2297006` was removed under exact approval. PR #1748 was corrected and merged, and the exact staging deployment line is live-checked at `0af99c92c`. Keep historical failed-row deletion/archive as a separate destructive decision.
- **Promote to:** GitHub issue
- **Links:** `Sifututor/sifu-tutor#1742`, `Sifututor/sifu-tutor#1746`, `Sifututor/sifu-tutor#1748`, `.agent-os/session-maps/2026-07-18-164340-codex-production-queue-reliability.md`, earlier context `Sifututor/sifu-tutor#1579`, `Sifututor/sifu-tutor#1580`

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

### SIMS-FIUU-RETRY-001 — Status-Aware Retry Across All SIMS Payments

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** Every FIUU payment flow owned by SIMS uses a consistent, customer-friendly retry contract: a 15-minute hosted checkout, immediate retry only after a verified failure or cancellation, protection while payment is paid/pending/unknown, a separate 30-minute safety fallback, and clear countdown/status UI.
- **Why it matters:** Tutor commitment-fee staging UAT showed that closing or abandoning FIUU can leave customers facing a confusing 30-minute lock. Fixing only that page would leave parent commitment fees, invoice links, Pay All, direct invoice payment, and other SIMS-owned FIUU entry points with inconsistent retry and duplicate-payment protection.
- **Source:** Hafiz decision during tutor commitment-fee payment-link UAT, 2026-07-17.
- **Next action:** Start a dedicated future product-design and implementation session for the complete cross-SIMS FIUU retry programme; do not include it in the current Tutor Commitment Fee release/UAT.
- **Promote to:** PRD and GitHub issue in that dedicated future session
- **Links:** `.agent-os/session-maps/2026-07-17-172051-codex-tutor-commitment-fee-links.md`

### SIMS-DEPLOY-SAFETY-001 — Migration-Backed Release Ordering

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** Production deploys that add public/API code depending on new tables avoid any window where live requests can hit the new code before the required migration has run.
- **Why it matters:** PR #1690 deployed safely after migration/import, but production logged brief `app_text_versions` missing-table errors during the window between code pull and migration. The app recovered and smoke passed, yet the release process should avoid that class of transient public API error.
- **Source:** Codex PR #1690 app-text production deployment, 2026-07-10.
- **Next action:** Review the production deploy playbook for migration-backed public APIs; consider a two-phase deploy, maintenance window, pre-created compatible tables, or route-safe fallback before code that references new tables is exposed.
- **Promote to:** GitHub issue
- **Links:** `Sifututor/sifu-tutor#1690`, production deploy `e7795dccf`, Koda `mem_5142b503a88e`, Koda `mem_ef97d14fb34b`
