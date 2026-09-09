# SIMS / sifu-tutor Mission Ledger

Use this for SIMS missions, child tasks, adjacent ideas, and paused follow-ups.

## Missions

### SIMS-ASSESSMENT-CONTENT-REVIEW-001 — Complete Human Review And Publish Assessment Banks

- **Project:** sifu-tutor
- **Status:** paused
- **Type:** mission
- **Parent:** none
- **End goal:** The versioned Sifututor SOP, Nakngaji SOP, and Nakngaji Tajwid assessment banks are operationally approved, religiously reviewed where required, corrected from reviewer feedback, imported, published, and enabled without using AI drafts as production authority.
- **Why it matters:** The 236-question draft has been source-audited and adversarially corrected, but operational policy and Quran/Tajwid correctness remain human-owned. Publishing before those reviews could teach an incorrect fee, attendance, resignation, or recitation rule.
- **Source:** Hafiz-requested AI draft, Claude adversarial review, and staff-review preparation, 2026-08-21.
- **Next action:** Staff review every assigned row in the shared Sheet, record decisions/comments and reviewer names, and return the completed Sheet. A qualified Quran/Tajwid reviewer must review all 80 Tajwid rows and resolve the held NN-TJW-17 Mutajanisain-versus-Mutaqaribain terminology before the content is reconciled and considered for import.
- **Do not do yet:** Do not import, publish, or enable the draft bank; do not hardcode a commitment-fee amount or exact resignation-notice period into durable questions while those policies are deliberately expressed through server-owned or neutral wording.
- **Promote to:** Final publication-readiness review and the existing assessment release implementation after all review decisions are closed
- **Links:** Staff-review Sheet `https://docs.google.com/spreadsheets/d/1UrJNp_zYtJuhc8PeHj1m0fXxn_Q2fyvOiB-7uaF1FfA/edit`, `Sifututor/sifu-tutor#2232`, Koda `mem_67dee23d1d21`, Koda `mem_c0184d1e7c60`

### SIMS-ORPHANED-CLASS-REVIEW-001 — Resolve Remaining Historical Class Exceptions

- **Project:** sifu-tutor
- **Status:** paused
- **Type:** mission
- **Parent:** none
- **End goal:** Operations and Finance give an evidence-backed outcome for each remaining October 2025 historical class exception, after which any required payment or cancellation is handled as a separately approved, guarded operation without rewriting invoices or payments by assumption.
- **Why it matters:** Issue #2090 prevented new orphaned class history and safely repaired the one approved duplicate pair, but four records remain intentionally untouched because the system cannot safely infer their business meaning. Guessing could either erase a genuine tutor debt or alter history linked to a paid parent invoice.
- **Source:** TREQ-255874 / issue #2090 production reconciliation and close-out, 2026-08-13.
- **Next action:** Wait for the developer to return the Operations/Finance answer for each record: whether attended class `112802` is genuine and should be verified/paid or is stale; the Finance treatment for `108879` / paid sibling `118404` and `111803` / paid sibling `117408`, whose old parent invoices are paid; and whether `10116` / `10722` is one lesson recorded with the wrong subject or two valid classes. Resume with a fresh read-only production check before proposing any write.
- **Promote to:** Separate GitHub issue or exact critical-lane production operation only after the business decision and evidence are available
- **Links:** `Sifututor/sifu-tutor#2090`, `Sifututor/sifu-tutor#2094`, `.agent-os/session-maps/2026-08-13-155246-codex-orphaned-class-reconciliation.md`, Koda `mem_b5355df095c6`

### SIMS-TEST-ISOLATION-001 — Isolate Destructive Migration Rollback Tests

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** The repository-wide Pest suite can run sequentially on its disposable test database without an earlier migration rollback test removing shared tables needed by later unrelated tests.
- **Why it matters:** During #2090 verification, the focused tests passed, but the full-suite attempt became unreliable after pre-existing rollback tests dropped shared tables. This does not invalidate the focused #2090 evidence, but it prevents the full suite from serving as trustworthy broad regression proof.
- **Source:** Issue #2090 verification, 2026-08-13.
- **Next action:** When prioritised, reproduce the suite contamination on a disposable database, identify the rollback tests that remove shared schema, and redesign their isolation before changing application behavior. Create a focused GitHub issue before implementation.
- **Promote to:** GitHub issue after a fresh reproduction identifies the exact contaminating tests
- **Links:** `Sifututor/sifu-tutor#2090`, `.agent-os/session-maps/2026-08-13-155246-codex-orphaned-class-reconciliation.md`

### SIMS-TUTOR-IDENTITY-EXCEPTIONS-001 — Review Preserved Tutor Identity Exceptions

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** Every remaining tutor phone-identity exception has a reviewed outcome without guessing identity, rewriting financial/class history, or treating malformed phone data as a safe duplicate.
- **Why it matters:** Production issue #2017 safely reconciled all 962 automatically provable no-money groups, but deliberately preserved 147 uncertain groups, including 12 with financial or class ownership. A separate 621 tutor rows have invalid phone values and were outside canonical-phone duplicate matching. Broad automatic cleanup would risk combining different people or damaging business history.
- **Source:** Tutor duplicate-identity production remediation and close-out, 2026-08-11.
- **Next action:** Only when Hafiz prioritises this mission, begin with a fresh read-only audit. Split the 147 preserved groups by exact reason and treat financial/class cases as individually reviewed critical operations; separately classify the 621 invalid-phone rows into correctable formatting, missing/unusable data, and identity-recovery cases. Do not reuse the completed 962-group apply plan.
- **Promote to:** Product decision and separate critical-lane GitHub issues after the cohorts and evidence rules are agreed
- **Links:** `Sifututor/sifu-tutor#2017`, `.agent-os/session-maps/2026-08-11-132951-codex-tutor-identity-audit.md`, Koda `mem_efca724422db`

### SIMS-TAC-SUPPORT-001 — Replace Readable OTP Listing With Governed TAC Support

- **Project:** cross-project (`sifu-tutor`, `sifututor_tutor`, `sifututor_parent`)
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** Support can help a genuine tutor or parent who cannot receive a
  TAC without exposing a bulk list of active login codes. The future workflow
  uses narrowly authorised access, one searched user at a time, audited reveal
  or recovery actions, automatic expiry, resend and attempt limits, and no
  bulk copy, CSV, Excel, or PDF export of active TACs.
- **Why it matters:** Hafiz chose to restore the former readable Verification
  Codes behaviour immediately because QA and support currently depend on it.
  That restores operations quickly but deliberately accepts the old security
  risk: a readable TAC functions as a temporary password, and broad page access
  or exports could enable account takeover.
- **Source:** Hafiz's tutor-app Verification Codes diagnosis and explicit
  follow-up instruction to record the safer future improvement, 2026-08-11.
- **Next action:** After the immediate compatibility restoration is stable,
  run product design for authorised roles, user-identity checks, alternate
  delivery and resend behavior, audited code reveal versus newly generated
  recovery code, expiry and rate limits, emergency access, and permanent SIMS
  plus tutor/parent mobile regression coverage.
- **Do not do yet:** Do not widen the immediate restoration into this redesign,
  remove the support fallback before its replacement is proven, or introduce a
  universal production master code.
- **Promote to:** Product design, then a separate critical-lane GitHub issue
- **Links:** Koda `mem_b8770a9def5f`

### SIMS-PARENT-LIFECYCLE-001 — Review Exceptional Terminal Parent Status Correction

- **Project:** sifu-tutor
- **Status:** done
- **Type:** mission
- **Parent:** none
- **End goal:** Decide whether the specific resigned parent record PRT-660981
  should remain terminal or receive a separately authorised, audited lifecycle
  correction based on verified operational evidence.
- **Why it matters:** The Edit Parent safety release correctly keeps ordinary
  profile editing from changing lifecycle status. Correcting this record would
  deliberately override a terminal Resigned status and therefore must not be
  hidden inside a code deployment or generic profile edit.
- **Source:** Parent status production-release handoff and close-out,
  2026-08-11.
- **Outcome:** Hafiz explicitly approved the dedicated one-record production
  correction on 2026-08-11. Parent `PRT-660981` was changed from `resigned` to
  `active` with an optimistic exact-row guard and audit log `2254426`; linked
  students, requests, invoices, commitment fees, and identity fields were not
  changed. Read-only post-check and production monitoring passed.
- **Next action:** Closed. Staff can re-check the parent record in SIMS; any
  future lifecycle change must use the dedicated lifecycle process.
- **Do not do:** Do not alter the related pending commitment fee or other linked
  records without separate evidence and approval.
- **Promote to:** A dedicated production-data operation only after explicit
  per-operation approval
- **Links:** `Sifututor/sifu-tutor#2009`, `Sifututor/sifu-tutor#2010`

### SIMS-STAFF-PHONE-UX-001 — Show Invalid Staff Phone Feedback Immediately

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** During Add Staff and Edit Staff, SIMS validates the phone when
  staff leave the phone field, shows a clear inline error beside that field,
  and prevents moving to the next wizard step until the number is valid.
  Valid local and international formats continue to normalize to E.164, and
  existing duplicate-account guidance remains unchanged.
- **Why it matters:** During issue #1979 staging UAT, an invalid but
  possible-length Malaysian number produced no feedback during the Personal
  information step. SIMS waited until final submission, then showed a generic
  server validation error on the Attachments step. The validation rule was
  correct, but staff had to work out which earlier field caused it.
- **Source:** Hafiz's Add Staff staging UAT and explicit instruction to record
  this for future work rather than fix it now, 2026-08-07.
- **Next action:** When prioritised, diagnose the duplicate-phone endpoint and
  Add/Edit Staff field-state contract, then create a focused GitHub bug with
  permanent Playwright coverage for valid local input, valid international
  input, invalid input, normalization, duplicate detection, and blocking the
  wizard from advancing while invalid.
- **Do not do yet:** Do not loosen phone validity rules, accept fake numbers,
  change duplicate-account policy, add a country selector, or include this in
  the current #1979 production release.
- **Promote to:** GitHub issue when Hafiz prioritises implementation
- **Links:** `Sifututor/sifu-tutor#1979`, `.agent-os/session-maps/artifacts/crm-workforce-identity-release-ledger-2026-08-07.md`, Koda `mem_c4409bd27f21`

### SIMS-PHONE-RECOVERY-001 — Admin-First Verified Phone Account Recovery

- **Project:** cross-project (`sifu-tutor`, `sifututor_tutor`, `sifututor_parent`)
- **Status:** done
- **Type:** mission
- **Parent:** none
- **End goal:** An authorised SIMS admin can safely reconnect an existing tutor
  or parent account to a genuinely new phone number when the person has lost
  access to the registered number, without creating or merging the wrong
  account.
- **Why it matters:** Phone normalization can correct the same number written
  differently, but it cannot prove that a genuinely different number belongs
  to the same person. Without a governed recovery path, users who lose their
  old number may create duplicate accounts or require unsafe direct data edits.
- **Source:** Hafiz's phone identity clarification during tutor-request sharing
  follow-up, 2026-08-05. The governed admin-first Tutor/Parent recovery was
  subsequently designed, implemented, released, and closed through issues
  #2070 and #2078 on 2026-08-13.
- **Next action:** None required. Reopen only for a new defect or separately
  approved product expansion.
- **Do not do:** Do not add public self-service recovery, match or merge accounts
  by name/email similarity, bypass new-number verification, or automatically
  process the excluded historical identity mismatches.
- **Promote to:** Completed GitHub issues #2070 and #2078; production release complete
- **Links:** `.agent-os/session-maps/2026-08-12-193916-codex-admin-phone-recovery.md`,
  `Sifututor/sifu-tutor#2070`, `Sifututor/sifu-tutor#2078`,
  `Sifututor/sifu-tutor#2080`

### SIMS-TUTOR-BANK-DETAILS-001 — Decide The Future Of Legacy Tutor Bank Fields

- **Project:** sifu-tutor
- **Status:** paused
- **Type:** mission
- **Parent:** none
- **End goal:** Staff have one unambiguous, reliable place to maintain tutor payout bank details, and the legacy SIMS Tutor Edit fields either save correctly for every valid tutor status or are safely disabled/removed once Ripple is confirmed as the only intended workflow.
- **Why it matters:** The 2026-08-03 production diagnosis found that a verified tutor's required Status dropdown can render empty and block the entire SIMS Tutor Edit Save action before the bank change is submitted. The official TX workflow is now Ripple, but leaving an apparently editable SIMS bank form can still confuse staff if they return to it later.
- **Source:** Hafiz's staff report, SIMS/Ripple production diagnosis, and request to preserve the unfixed SIMS follow-up for a future session, 2026-08-03.
- **Next action:** Only when Hafiz reopens this work, begin with a fresh read-only production diagnosis and confirm the intended product direction: align the authoritative TutorStatus lifecycle with Settings/Edit/filter options, or disable/remove the legacy SIMS bank fields. Then promote the approved scope to a separate critical-lane GitHub issue with permanent E2E coverage for editing a verified tutor without changing status.
- **Promote to:** GitHub issue after fresh diagnosis and product decision
- **Links:** `.agent-os/session-maps/2026-08-03-codex-ripple-help-centre-guides.md`, `Sifututor/ripple-suite#318`, `Sifututor/ripple-suite#320`, https://ripple.admin.sifututor.my/help/tutor-payments/add-or-update-tutor-bank-details, Koda `mem_005f423c20f0`

### SIMS-TUTOR-CONSENT-GUARD-001 — Prevent Consent-Free Tutor Activation

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** SIMS cannot move a tutor into a verified/active state through legacy approval or commitment-fee settlement while the required tutor consent evidence is missing, and any broader protected-endpoint consent enforcement is introduced only through a backward-compatible release plan after mobile adoption.
- **Why it matters:** The completed consent repair found exactly two verified tutors, `TUT-579928` and `TUT-619769`, with zero required consent records. Both reached verified through legacy approval plus payment activation. The repaired mobile app will let them accept properly, but a backend transition guard is needed to prevent the same state from recurring without unexpectedly blocking tutors on an older app build.
- **Source:** Tutor declaration/consent diagnosis, backend deployment, production repair, residual audit, and mobile follow-up review, 2026-07-29 to 2026-08-01.
- **Next action:** Backend issue #1912 / PR #1913 is merged, deployed, live-smoked, and monitored; the exact AASA and shared tutor-request links are production-proven. Mobile PR #36 remains open and mergeable for Mubashir's independent review, fresh-install iPhone universal-link QA, exact-build Android/iOS evidence, normal store release, and post-release smoke. Do not start the bridge-removal countdown until the corrected app version/build is verified live in both stores. After confirmed release, disable the temporary legacy OTP bridge from backend issue #1879 only when app `1.26.7` and older are below 5% of OTP traffic for 48 hours, no new legacy login report appears for 24 hours, and current staff cases are resolved. Then map every tutor verification/activation transition and protected API compatibility requirement. Decide the narrow activation guard first, then determine whether server-wide consent middleware is needed; promote the approved, backward-compatible contract to a separate critical-lane GitHub issue before implementation.
- **Promote to:** GitHub issue after mobile release/adoption and contract review
- **Links:** `Sifututor/sifu-tutor#1839`, `Sifututor/sifu-tutor#1851`, `Sifututor/sifu-tutor#1879`, `Sifututor/sifu-tutor#1912`, `Sifututor/sifu-tutor#1913`, `Sifututor/sifututor_tutor#28`, `Sifututor/sifututor_tutor#29`, `Sifututor/sifututor_tutor#30`, `Sifututor/sifututor_tutor#31`, `Sifututor/sifututor_tutor#36`, `.agent-os/session-maps/2026-07-29-160203-codex-tutor-declaration-consent-diagnosis.md`, Koda `mem_f5544c4f7ce0`, Koda `mem_de5745401a19`, Koda `mem_c084b37c2546`, Koda `mem_a00707258cc1`, Koda `mem_877df682b786`

### SIMS-TUTOR-STATUS-NORMALIZATION-001 — Retire Legacy Active Tutor Status Safely

- **Project:** sifu-tutor, with Ripple Suite and Tutor App compatibility impact
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** `verified` is the one canonical active tutor-account status for new and safely migrated tutors; no supported workflow writes the legacy `active` value; staff see one unambiguous status vocabulary; and every migrated tutor retains correct verification, commitment-fee, consent, assignment, payment, mobile-access, and audit behavior.
- **Why it matters:** Staff currently see both `Active` and `Verified` even though both can pass normal tutor-work eligibility. `Verified` is now the governed result of verification approval plus settlement, while `Active` survives through legacy compatibility paths. A blind `active -> verified` update could certify tutors without the required approval, payment, or consent evidence and could break current exact-`active` consumers in invoice generation, Tutor Request selection, ad-hoc bonuses, resignation, dashboard counts, and reports. Import, edit, and legacy settlement paths can also write `active` again after a one-off migration.
- **Source:** Hafiz's Tutor List staff question, read-only SIMS/Ripple lifecycle diagnosis, and request to preserve the migration plan for future work, 2026-08-03.
- **Next action:** When Hafiz reopens this mission, begin with a fresh critical-lane Phase A read-only migration-readiness audit. Map every `active` reader and writer across SIMS, Ripple, and Tutor App; obtain aggregate production cohort evidence without exposing PII; define the explicit grandfathering rule for legacy tutors; coordinate with `SIMS-TUTOR-CONSENT-GUARD-001`; and only then promote the approved contract to a GitHub issue and Build-Ready Pack. Do not run a status migration during the audit.
- **Promote to:** GitHub issue and critical-lane Build-Ready Pack after the read-only audit and business-rule decision
- **Links:** `SIMS-TUTOR-CONSENT-GUARD-001`, `SIMS-TUTOR-BANK-DETAILS-001`, Koda `mem_2fb9c78a7306`, Koda `mem_08a68c1fe6ad`

Future migration sequence:

1. **Confirm status meaning and cohort policy.** Decide whether legacy `Active` tutors are grandfathered from established historical evidence or must satisfy current verification approval, completed RM100 commitment fee, and required consent. Define excluded states such as suspended, resigned, terminated, unresolved payment review, or incomplete evidence.
2. **Ship compatibility code before touching data.** Replace exact-`active` guards and queries with the canonical active-workflow policy where business behavior should accept `verified`; update assignment, invoice, matching, bonus, resignation, notification, reporting, dashboard, API, and mobile consumers; and preserve temporary reads of both values during rollout.
3. **Stop creating new legacy rows.** Remove `active` from staff-edit settings and import normalization, route every commitment-fee settlement through the canonical verified transition, prevent direct/manual status bypasses, and add a regression guard that fails if a supported path writes `active` again.
4. **Produce a read-only production dry run.** Reconcile aggregate counts for status, onboarding approval, completed fee, consent, suspension/termination, active work, and audit history. Classify rows into `safe to migrate`, `needs remediation or decision`, and `excluded`; record an exact count and deterministic cohort fingerprint so later drift forces a new preview.
5. **Build a reversible migration.** Use an idempotent, chunked operation with an explicit approved cohort, per-tutor before/after audit evidence, rollback mapping, fresh backup verification, and no broad unresolved status update. Recheck the cohort immediately before applying it.
6. **Prove every affected journey.** Add focused backend tests and permanent E2E/API coverage for Tutor List/Edit, Ripple Tutor Experience, assignment and matching, invoice generation, bonuses, resignation, notifications, reports/dashboard counts, Tutor App access, suspended/terminated protections, retry/idempotency, and rollback/reconciliation behavior.
7. **Release in two controlled stages.** Deploy and monitor compatibility/writer-removal code first. After it is proven stable, obtain separate explicit approval for the production data migration, run the fresh dry run, apply only the approved cohort, reconcile counts and audit evidence, smoke the changed journeys, and monitor logs before closing the mission.

Completion evidence:

- No supported code, import, staff UI, API, settlement, or mobile path writes `active`.
- No exact-`active` consumer incorrectly excludes canonical `verified` tutors.
- Every migrated row belongs to the approved fingerprinted cohort and has a documented verification/grandfathering basis.
- Consent, payment, suspension, termination, request-specific exceptions, and audit history remain truthful.
- Pre/post counts reconcile, rollback evidence exists, permanent tests pass, and production smoke/monitoring show no workflow regression.

### SIMS-BONUS-AUTOMATION-001 — Event-Driven Welcome Bonus Entitlement

- **Project:** sifu-tutor
- **Status:** done
- **Type:** mission
- **Parent:** none
- **End goal:** An active or verified tutor who legitimately reaches 40 weighted verified hours on or after 2026-07-01 automatically receives exactly one unpaid RM200 welcome-bonus entitlement. The fixed reset cohort still starts counting from 2026-07-01; only requests to restore that cohort's pre-July history remain individually reviewed.
- **Why it matters:** Production previously ran the midnight welcome-bonus check in report-only mode, so July-onward tutors could reach 40 hours in the app without receiving the financial entitlement. Hafiz clarified on 2026-08-25 that request-only handling was never intended for new July-onward qualification.
- **Source:** TUT-319699 welcome-bonus diagnosis and event-driven design, 2026-07-29 to 2026-07-30; corrected automation boundary stated by Hafiz on 2026-08-25.
- **Next action:** None required. The schema-first release, event-first evaluation, nightly recovery, automatic activation, Tutor App contract proof, idempotent replay, notification processing, production smoke, and monitoring all completed on 2026-08-25. Reopen only for a new defect or a separately approved pre-July exception.
- **Promote to:** Completed GitHub issues #2277 and #2279; production release complete
- **Links:** `.agent-os/session-maps/artifacts/tut-319699-welcome-bonus-finance-review/welcome-bonus-event-driven-build-ready-pack.md`, `Sifututor/sifu-tutor#1847`, `Sifututor/sifu-tutor#1862`, `Sifututor/sifu-tutor#2277`, `Sifututor/sifu-tutor#2279`, PRs `#2280`, `#2281`, `#2282`, `#2283`, `#2284`, `sifu-tutor/docs/qa/release-evidence-2026-08-25-issue-2277.md`, Koda `mem_80a077f63a8c`

### SIMS-BONUS-IDEMPOTENCY-001 — Repeated Monthly Performance Bonus Insert

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** Realtime monthly performance-bonus evaluation treats an existing dedupe key as an already-awarded result instead of repeatedly attempting the same insert and logging a production error.
- **Why it matters:** Production monitoring for the unrelated TUT-319699 welcome-bonus display release found repeated `MonthlyBonus RealtimeTrigger` duplicate-key errors for tutor 2732 and July 2026. The same error occurred before and after that deployment, so it is not a regression from the display fix, but repeated retries create noisy error monitoring and may hide a genuine award-state mismatch.
- **Source:** TUT-319699 production monitoring, 2026-07-30.
- **Next action:** Run a separate read-only diagnosis of the existing performance row, soft-delete/category/rule matching, and realtime evaluation path; then define an idempotent existing-award outcome and permanent regression before any code or production-data change.
- **Promote to:** GitHub issue after read-only diagnosis
- **Links:** `Sifututor/sifu-tutor#1872`, `sifu-tutor/docs/qa/production-smoke-2026-07-30-ca3dcb57d-awarded-welcome-bonus-progress.md`

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
- **Type:** mission
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
- **Next action:** Design a small mode-600 status record or sanitized monitoring metric (processed/total/percentage/ETA only), define update frequency and cleanup, and preserve the existing low CPU/bandwidth safety limits. Related Agent OS lesson: multi-hour external operations should use a background/recheck workflow (e.g. a scheduled check-in) instead of an agent session actively polling in real time; a request to "stop watching" should stop only the watcher, not the underlying production job, unless explicitly asked.
- **Promote to:** GitHub issue
- **Links:** none yet

### SIMS-BACKUP-DR-001.3 — Tighten Database Backup Credential IAM Scope

- **Project:** sifu-tutor
- **Status:** triaged
- **Type:** task
- **Parent:** SIMS-BACKUP-DR-001
- **End goal:** The `sims-production-backup-uploader` Wasabi IAM policy is scoped to `sims/database/*` only, matching its description, instead of the current broader `sims/*`.
- **Why it matters:** Discovered while diagnosing composed recovery on 2026-07-28: this credential's resource scope already covered all of `sims/*` before this session touched anything (verified via a safe cross-prefix read probe: a read into the uploads lane returned 404 Not Found rather than 403 Forbidden, meaning it was authorized). This session only added `s3:GetObjectVersion` to the existing scope per Hafiz's explicit approval and did not widen it further, but the pre-existing breadth itself doesn't match least-privilege intent and should be tightened separately.
- **Source:** SIMS backup production close-out session, 2026-07-28.
- **Next action:** Confirm no other automation depends on this credential reading outside `sims/database/*`, then narrow the IAM policy's resource ARNs to `sims/database/*` only, and re-prove the database backup lane still succeeds.
- **Promote to:** GitHub issue
- **Links:** none yet

### SIMS-BACKUP-DR-001.A1 — Audit And Optimize SIMS Live File Storage

- **Project:** sifu-tutor
- **Status:** active
- **Type:** mission
- **Parent:** SIMS-BACKUP-DR-001
- **End goal:** Verify whether SIMS uploaded-file storage is already organized efficiently and design any justified improvements to naming, duplication, compression, retention, serving, deletion, and direct Wasabi storage without risking historical documents.
- **Why it matters:** SIMS currently holds about 55 GB across roughly 223,000 uploaded files. Moving live uploads directly to Wasabi is a promising future option, but it should be treated as a separate storage architecture project after the current backup system is made safe and after existing file behavior is audited rather than assumed.
- **Source:** Hafiz backup brainstorm, 2026-07-13.
- **Next action:** Issue #2328 is executing the approved production programme. The first campaign completed 13 windows, then stopped fail-closed at IDs `341934–342933` on two zero-byte image placeholders. On 2026-09-03, the 888 already-migrated rows in that partial window were freshly verified, exactly deleted, and post-verified, reclaiming 1,735,263,977 bytes with zero failures; the two zero-byte public rows remain unchanged. Fresh database recovery point `01M1JRFQQ8S9QHWDW4X8CX25DG` is Wasabi-version-verified through 2026-10-03. Detached PID `718726` now runs the remaining exact range `255934–341933` in 86 fail-closed windows at production SHA `75bfdac7317d08107e6f5fee0fee829a3e433d7f`; inspect its aggregate log without restarting or overlapping it. Ticket/offline-payment/backdate routing remains safely dormant pending the exact IAM grants in #2371/#2375/#2378; Tutor App iOS release remains externally outstanding in issue #129.
- **Promote to:** PRD
- **Links:** Sifututor/sifu-tutor#2328; #2371; #2375; #2378; Sifututor/sifututor_tutor#129; `.agent-os/session-maps/2026-09-01-220551-codex-historical-attendance-media.md`

### SIMS-CLASS-CF-GATE-001 — First-Class Commitment-Fee Scheduling Policy

- **Project:** sifu-tutor
- **Status:** done
- **Type:** mission
- **Parent:** none
- **End goal:** SIMS blocks the first class until the request's Parent RM50 commitment fee is completed or validly waived. Tutor commitment-fee status does not block scheduling, and returning-parent waivers are allowed only after a genuine prior positive, non-refunded Parent commitment fee.
- **Why it matters:** TREQ-199498 proved SIMS could schedule a first class while the Parent fee was still pending. The live gate now prevents that recurrence while preserving the separately approved returning-parent rule and keeping Tutor commitment fees out of the scheduling decision.
- **Source:** TREQ-199498 / issue #1902 production investigation, Hafiz's approved Parent-only policy, issue #1907 implementation, and 2026-08-04 production verification.
- **Next action:** None for this incident. Monitor normal scheduling traffic. Do not bulk-link planning classes or backfill pristine planning invoices; any new historical exception or financial repair needs a fresh exact review and approval.
- **Completion evidence:** PR #1908 is merged and live. Focused Parent CF service and first-class gate tests passed, the production workflow was smoked, five genuinely eligible returning-parent waivers were audited, and the two explicitly approved pre-gate classes (TREQ-199498 and TREQ-364397) received one-time grandfathered waivers without making either parent eligible for a future waiver.
- **Promote to:** completed through GitHub issue #1907
- **Links:** `Sifututor/sifu-tutor#1902`, `Sifututor/sifu-tutor#1907`, `Sifututor/sifu-tutor#1908`, `.agent-os/session-maps/2026-08-03-205811-codex-sims-credit-clockout-repair.md`, Koda `mem_946aee609545`, Koda `mem_d770c7cf205f`

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

### SIMS-BILLING-ALLOC-LEGACY-001.1 — Guided Parent Commitment-Fee Historical Invoice Review

- **Project:** sifu-tutor
- **Status:** paused
- **Type:** task
- **Parent:** SIMS-BILLING-ALLOC-LEGACY-001
- **End goal:** Finance receives a guided, case-by-case review pack for all 99 historical malformed parent commitment-fee invoice offsets, approves the correct treatment for each case, and hands Engineering an exact approved repair manifest without anyone bulk-editing or silently rewriting invoice history.
- **Why it matters:** The forward prevention fix is live, but the historical cohort still contains 57 missing offsets, 4 under-offsets, 28 over-offsets, 10 correct totals on the wrong invoice, and 3 stale stored balances. Seventy-four affected first invoices are already paid and 25 are unpaid. An unexplained anomaly list would leave Finance guessing what to change, while a net RM1,797.51 bulk adjustment would incorrectly combine different customers' over- and under-applied balances.
- **Source:** Hafiz commitment-fee invoice audit and guided-finance-review decision, 2026-07-29.
- **Next action:** Deferred by Hafiz on 2026-07-29. Keep the verified 25-case guided Sheet as the evidence pack and make no production change. Resume for a staff-reported case or a later deliberate review; refresh the read-only audit, obtain Finance's exact treatment and communication decision, and promote only an approved repair manifest to a separate critical-lane GitHub issue.
- **Promote to:** GitHub issue only after Finance approves an exact repair set
- **Links:** `Sifututor/sifu-tutor#1837`, `Sifututor/sifu-tutor#1838`, `.agent-os/session-maps/2026-07-29-011557-codex-commitment-fee-invoice-audit.md`, `.agent-os/session-maps/2026-07-29-150940-codex-commitment-fee-unpaid-review.md`, [Phase 1 Finance review Sheet](https://docs.google.com/spreadsheets/d/1kK93YPMe6BOjAyirllkyMf-iQxZA_UhddEvbAK_H4wc/edit), Koda `mem_4df7c94d9813`, Koda `mem_f40cc54f9450`, Koda `mem_36d7397c9664`

- **2026-08-13 status note:** The separate false-Unpaid status cohort from issues #2089/#2101 was handled under its own exact critical-lane approval: 19 fingerprint-locked invoices totalling RM3,660.00 were repaired and verified live, while ten ambiguous invoices remained untouched for individual Finance review. This does not authorize or silently reclassify the broader 99-case malformed-offset programme above; that programme remains paused and requires refreshed read-only evidence plus case-by-case Finance decisions before any new repair issue.

- **Phase 1 evidence:** The production preview remained read-only and still returned exactly 25 unpaid cases: 10 missing, 2 under-credit, 9 duplicate/excess-credit, and 4 wrong-invoice cases. The Sheet contains 25 unique Finance rows and 25 matching technical-evidence rows. All decisions remain `Pending`, all rows remain `Ready for Engineering = No`, and no SIMS production data was changed. One exception would otherwise produce a negative invoice balance, three wrong-invoice cases touch paid history, and one duplicate case contains a stale stored `amount_due`.

Review lanes:

- **Phase 1 — 25 unpaid invoices:** 10 missing, 2 under-credit, 9 duplicate/excess-credit, and 4 correct-total/wrong-invoice cases. Finance confirms the intended customer balance and any communication; Engineering later performs only the approved fee-linked deduction repair and balance recalculation.
- **Phase 2 — 74 paid invoices:** 47 missing, 2 under-offset, 19 over-offset, and 6 correct-total/wrong-invoice cases. Finance must choose customer credit, refund, additional collection, historical note, or no change after ledger verification. Paid invoices must not be silently rewritten.
- **Separate product-decision lane:** Exclude 22 pending and 333 waived requests with an active offset but no completed sibling until the waived-fee business rule is confirmed. Exclude 68 completed-fee requests with no invoice because they are currently inactive and outside this repair cohort.

Required guidance for every case:

- Identify the parent, request, commitment fee, canonical first invoice, affected invoice, and direct SIMS review location.
- Show fee amount, current offset, correct offset, difference, stored amount due, recalculated amount due, and paid/unpaid state.
- Explain the problem in plain language and show the expected result after the recommended action.
- State the recommended treatment: add a missing linked offset, correct an under/over offset, move an offset to the first invoice and recalculate both invoices, recalculate a stale balance, or make no change with a recorded reason.
- Separate the Finance responsibility (review, customer/accounting decision, approval, communication) from the Engineering responsibility (controlled data repair, audit record, rollback metadata, and verification). Finance must never be told to edit database rows directly.

Completion evidence:

- All 99 cases are present exactly once and classified without using the aggregate net variance as a repair instruction.
- Finance records one approved treatment or explicit no-change decision per case, including approver and reason.
- The 25 unpaid and 74 paid lanes reconcile independently to the read-only audit.
- The review stage produces no production writes.
- Any approved repair is promoted into a separate critical-lane GitHub issue with exact IDs and before/after values, fresh backup, preview/dry run, transactional and idempotent execution, rollback evidence, post-repair audit, and Finance/QA sign-off.

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

### SIMS-BILLING-TIME-BACKSTOP-001 — Paid Monthly Invoice Backstop

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** SIMS creates the next invoice as a time-based backup when the latest invoice is paid and its billing date is at least one calendar month old, without weakening quota-based billing or exposing an invoice at the wrong time.
- **Why it matters:** The quota-based cycle is the primary billing rule, but a paid request can otherwise go too long without a new invoice when class activity stalls or the expected trigger does not happen. Hafiz wants a one-month paid-invoice condition as the next billing-cycle improvement.
- **Source:** Hafiz billing-cycle staff-guide discussion, 2026-07-21.
- **Next action:** Before implementation, define how the one-month backstop interacts with unfinished quota, requests with no upcoming class, paused or inactive requests, hidden-draft visibility, duplicate prevention, and invoice dates; then promote the approved rule to a GitHub issue and critical-lane build plan.
- **Promote to:** GitHub issue after the billing rules are confirmed
- **Links:** Koda `mem_54891697237d`

### SIMS-BILLING-PAUSE-001 — Payment-Aware Pause Assistance

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** When authorised staff pauses a tutor request because of non-payment, SIMS detects the relevant unpaid invoice and prefills clear payment-follow-up context instead of requiring staff to find and type it manually.
- **Why it matters:** SIMS already knows which invoices are unpaid, but the current Pause Request form does not connect that information to a manual payment hold. Automatic context reduces staff effort and makes the reason for the pause clearer to everyone reviewing the request.
- **Source:** Hafiz billing-cycle staff-guide discussion, 2026-07-21.
- **Next action:** Design the selection rule when more than one invoice is unpaid, the suggested reason and follow-up date, staff override behavior, audit logging, and compatibility with the currently disabled automatic payment-suspension flow; then promote the approved behavior to a GitHub issue.
- **Promote to:** GitHub issue after the interaction rules are confirmed
- **Links:** Koda `mem_72e65cdadb20`

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

### SIMS-CLASS-LIFECYCLE-001.A2 — Issue #1672 Historical Duplicate Slot Review

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** adjacent
- **Parent:** SIMS-CLASS-LIFECYCLE-001
- **End goal:** The three historical duplicate-slot incidents that exposed the
  stale-snapshot gap are reviewed individually and either retained with a clear
  audit explanation or repaired through an exact approved manifest, without
  silently changing class, invoice, parent-payment, tutor-payment or commission
  history.
- **Why it matters:** The forward concurrency fix is live and monitored, but
  automatically deleting or moving either row from an old duplicate pair could
  alter invoice allocation, attendance, quota or tutor earnings. The production
  release intentionally left every historical row untouched.
- **Source:** Issue #1672 production investigation and release, 2026-08-20.
- **Next action:** If Hafiz chooses to clean the historical incidents, refresh
  their current read-only state, classify each pair with Finance/Operations,
  obtain one explicit treatment per incident, and promote only the approved
  fingerprint-locked repair set through a separate critical-lane issue. Do not
  bulk-repair them as part of the forward guard.
- **Promote to:** GitHub issue only after the individual business treatments are approved
- **Links:** `Sifututor/sifu-tutor#1672`, PRs `#2221`, `#2222`, `#2223`, Koda `mem_a0fef012adf9`, Koda `mem_828e90962145`

### SIMS-CLASS-LIFECYCLE-001.A3 — Decide Current-Cycle Package Top-Up Contract

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** adjacent
- **Parent:** SIMS-CLASS-LIFECYCLE-001
- **End goal:** Staff have a separately authorised workflow for increasing a matched Request's package immediately when the business intends to add credits to the current billing cycle, with the additional charge, payment state, class capacity, tutor commission, and audit history updated as one explicit contract.
- **Why it matters:** Issue #2514 confirms that the current Amend Request workflow intentionally changes the next invoice while preserving already issued invoice terms. Treating a package edit as an automatic current-cycle top-up would silently rewrite financial history or grant unbilled credits, while staff may still need a legitimate same-cycle upgrade path.
- **Source:** TREQ-808361 and TREQ-691783 production diagnosis for issue #2514, 2026-09-08.
- **Next action:** Run product and Finance design for unpaid, partially consumed, and paid invoices; define whether the workflow creates a supplemental invoice or approved adjustment, when credits become available, how retries remain idempotent, and how class allocation and commission reconcile. Promote only the approved contract to a new critical-lane GitHub issue.
- **Promote to:** Product design, then a separate critical-lane GitHub issue
- **Links:** `Sifututor/sifu-tutor#2514`, Koda `mem_243104186d54`

### SIMS-NOTIF-MATCH-001 — Connect SIMS opportunity notifications to the platform matching engine

- **Project:** sifu-tutor
- **Status:** paused
- **Type:** mission
- **Parent:** none
- **End goal:** Tutor opportunity notifications consume the same canonical
  matching result used by Ripple and the Tutor App, while notification code
  handles only delivery limits, dedupe, daily caps, and channel rules.
- **Why it matters:** The live notification spam fix reduced volume, but the notification-specific matcher still uses a simpler level/mode/city rule. That can make opportunity notifications less accurate than the shared matching engine, especially when subject data exists.
- **Source:** Codex notification batching/matching session, 2026-06-12.
- **Next action:** Treat this as a child of the cross-project direction in
  `XP-MATCH-001`. Ripple is the confirmed canonical engine. Redesign this SIMS
  mission as the governed prepared-opportunity consumer, Tutor App delivery
  owner, authoritative action handler, and final eligibility gate. Do not
  implement the earlier SIMS-only canonical-engine extraction.
- **Promote to:** GitHub issue
- **Links:** `sifu-tutor/docs/features/tutor-opportunity-matching/design-brief.md`,
  `sifu-tutor/docs/features/tutor-opportunity-matching/ranking-service-refactor-brief.md`,
  `ripple-suite/docs/features/matching/platform-matching-opportunity-engine-design-brief-2026-07-31.md`,
  Mission `XP-MATCH-001`

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

### SIMS-TUTOR-PROFILE-001.A3 — Cross-Platform Tutor Preference Parity

- **Project:** cross-project (`sifu-tutor`, `sifututor_tutor`, `ripple-suite`)
- **Status:** captured
- **Type:** adjacent
- **Parent:** SIMS-TUTOR-PROFILE-001
- **End goal:** Every existing SIMS, Tutor App, and Ripple surface that presents, edits, documents, tests, or evaluates Tutor Preferences uses the same complete field set and correctly includes teaching availability.
- **Why it matters:** The Tutor Request sharing-acquisition audit found broader pre-existing drift: SIMS Tutor Create has a reduced preference form, Ripple profile correction omits advanced preferences and availability, several checklists treat any `tutor_services` row as complete, API documentation omits availability, and mobile Maestro coverage still describes only two steps. These are real platform-consistency gaps, but fixing every unrelated surface would unnecessarily delay the Tutor Request sharing journey.
- **Source:** Hafiz's Tutor Request sharing-acquisition clarification and cross-surface read-only audit, 2026-08-05.
- **Next action:** Keep Release 2 scoped to the shared-link journey and only the preference contract it directly needs. Later, run a separate impact review for SIMS Create, Ripple correction, onboarding/commitment-fee gating, API documentation, and existing E2E coverage; then promote the approved slices to separate GitHub issues without coupling them to the sharing release.
- **Promote to:** Product design review, then separate GitHub issues
- **Links:** `sifu-tutor/docs/features/tutor-request-sharing-acquisition/`, Koda `mem_736ad78054d1`, Koda `mem_cdf714cbcabf`

### SIMS-SUBJECT-IDENTITY-001 — Remove Remaining Name-As-Identity Risks

- **Project:** cross-project (`sifu-tutor`, Tutor App reporting consumers)
- **Status:** captured
- **Type:** adjacent
- **Parent:** SIMS-TUTOR-PROFILE-001.A3
- **End goal:** Every workflow that needs an exact subject preserves the subject database ID and level context instead of grouping, filtering, or joining by subject name alone.
- **Why it matters:** The #1962/#45 related-impact sweep found candidate name-as-identity risks outside Tutor Preferences in tutor class filtering, daily-ticket/application reporting, student schedules, dashboard/parent queries, report chart labels, and two currently unused SubjectService grouping helpers. Some may be display-only or intentional, so changing them together would broaden business behavior and matching/report semantics without proof.
- **Source:** Independent related-impact audit for `Sifututor/sifu-tutor#1962` and `Sifututor/sifututor_tutor#45`, 2026-08-06.
- **Next action:** Run a separate read-only audit of each consumer with representative same-name/different-level data; split confirmed defects into small GitHub issues by user workflow. Do not bundle them into #1962/#45, matching changes, or historical data cleanup.
- **Promote to:** Separate GitHub issues after behavior is confirmed
- **Links:** `ClassService.php`, `ReportService.php`, `Portal/ClassController.php`, `Portal/DashboardController.php`, `ParentService.php`, `Portal/ReportController.php`, `SubjectService.php`

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

### SIMS-DEPLOY-SAFETY-001.A1 — Reconcile The SIMS Staging Branch And Server Checkout

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** adjacent
- **Parent:** SIMS-DEPLOY-SAFETY-001
- **End goal:** The remote `sifu-staging` branch and the staging server use one documented, current release-candidate path that can include `main` cleanly without branch rewrites or operators switching among old feature branches.
- **Why it matters:** During the PR #1788 release, the old staging checkout used an earlier commitment-fee feature branch. After Web Voyager was cancelled, staging was rebuilt fresh on the shared Hostinger KVM8 server (legacy SSH alias `finch`) and deployed from a Git bundle at the exact remote `sifu-staging` commit `ce1976f13f878da872e56ad384a71757321fd8e3`. That fixes the stale server checkout, but the long-term branch strategy and bundle-based redeploy runbook still need an explicit decision.
- **Source:** Codex PR #1788 staging and production release, 2026-07-28; SIMS staging rebuild handoff, 2026-08-10.
- **Next action:** Run a read-only branch-history audit, decide whether `sifu-staging` remains the release-candidate branch or staging should use exact `main` commits, then document the Git-bundle redeploy path for `/var/www/staging/sifu-tutor`. Do not force-rewrite the remote branch without a separate reviewed decision.
- **Promote to:** GitHub issue after the branch strategy is chosen
- **Links:** `Sifututor/sifu-tutor#1798`, `Sifututor/sifu-tutor#1788`, `.agent-os/session-maps/2026-07-28-032813-codex-pr1788-parent-ticket-release.md`

### SIMS-DEPLOY-SAFETY-001.A1.1 — Decide Whether Backport QA Still Needs A Host

- **Project:** sifu-tutor
- **Status:** paused
- **Type:** adjacent
- **Parent:** SIMS-DEPLOY-SAFETY-001.A1
- **End goal:** Hafiz explicitly decides whether `sifu-backport.tutorla.tech` is still required; if it is, it receives a separately scoped, isolated rebuild rather than being assumed to exist on the cancelled Web Voyager VPS.
- **Why it matters:** The 2026-08-10 rebuild restored only `sifu-staging.tutorla.tech`. The former backport environment disappeared with Web Voyager, and silently treating it as available could invalidate future backport QA evidence.
- **Source:** SIMS staging rebuild handoff, 2026-08-10.
- **Next action:** Ask Hafiz only when a real backport QA need arises. If retained, plan capacity, data isolation, credentials, DNS/TLS, safe integrations, and browser evidence before implementation.
- **Do not do yet:** Do not rebuild or repoint the backport domain without explicit approval; do not conflate this with the still-unexecuted production Hostinger migration.
- **Promote to:** GitHub issue only if Hafiz confirms the environment is still needed
- **Links:** `docs/agent-playbooks/agent-access-map.md`, `docs/sims-hostinger-migration-considerations-2026-07.md`, Koda `mem_4db682ae44da`

### SIMS-DEPLOY-SAFETY-001.A2 — Prevent Orphaned Production Maintenance Windows

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** risk
- **Parent:** SIMS-DEPLOY-SAFETY-001
- **End goal:** A SIMS production deployment has one identifiable owner, normal releases avoid unnecessary maintenance mode, and any approved maintenance window is automatically restored if its command or agent session exits.
- **Why it matters:** On 2026-07-29, a seven-second root SSH session created Laravel's maintenance marker and disconnected without cleanup. Both SIMS hosts then returned 503 for approximately 29 minutes; the actual recovery deployment did not begin until nearly 27 minutes after maintenance started because concurrent production-capable sessions had no shared owner or lease.
- **Source:** Hafiz request to remember the July 29 production-maintenance incident improvement, 2026-07-29.
- **Next action:** In a dedicated future workflow-improvement session, design a single atomic deployment lease containing owner/session/target SHA/start time, keep standard releases out of maintenance where safe, wrap any approved maintenance activation with guaranteed `artisan up` cleanup, alert on maximum age, and use a genuinely read-only status check instead of `php artisan down --status`.
- **Promote to:** GitHub issue after the lease, cleanup, timeout, and break-glass rules are reviewed
- **Links:** `.agent-os/session-maps/2026-07-29-170653-codex-payment-receipts-last-updated.md`, Koda `mem_0545aea07ddf`

### SIMS-DEPLOY-SAFETY-001.A3 — Audit Preserved Production Lockfile Drift

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** adjacent
- **Parent:** SIMS-DEPLOY-SAFETY-001
- **End goal:** Production deploys begin from a clean tracked checkout, and any server-only `package-lock.json` change has an identified owner and reviewed disposition instead of being silently overwritten or reused for an asset build.
- **Why it matters:** Before the Issue #2124 production release, the live checkout had a 171-line uncommitted `package-lock.json` diff even though the reviewed release did not change dependencies. The deploy preserved it recoverably as production `stash@{0}` named `pre-2124-production-package-lock-20260816`, restored the canonical reviewed lockfile, and completed successfully. Reapplying or deleting that stash without understanding its origin could either reintroduce unreviewed dependency state or discard intentional work.
- **Source:** Codex Issue #2124 production deployment, 2026-08-16.
- **Next action:** In a separate read-only production hygiene review, compare the stash to its parent lockfile, identify which prior command or release created it, and decide whether to discard it or turn a legitimate dependency change into a normal GitHub issue/PR. Do not apply the stash to the live checkout.
- **Promote to:** GitHub issue if the diff represents a legitimate required dependency change
- **Links:** `Sifututor/sifu-tutor#2124`, production deploy `693d908b937fc0383c3d29d25e413d5d3154f230`, `.agent-os/session-maps/2026-08-16-175754-codex-mode-aware-tutor-request-duplicates.md`

### SIMS-DEPLOY-SAFETY-001.A4 — Design A Cleanup-Safe Production Tutor Request Canary

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** adjacent
- **Parent:** SIMS-DEPLOY-SAFETY-001
- **End goal:** Production Tutor Request releases can safely prove the exact authenticated creation journey without contacting real customers, sending notifications, or leaving Request, invoice, commitment-fee, admission-batch, or related records behind.
- **Why it matters:** Issue #2124 was fully exercised by permanent local E2E and its deployed duplicate decision was proven read-only against production data in both mode directions, but a real production HTTP submission was intentionally excluded because creation fans out into financial and notification state. A governed canary would close that evidence gap for future releases without turning customer data into test fixtures.
- **Source:** Codex Issue #2124 production verification and Hafiz follow-up, 2026-08-16.
- **Next action:** In a separate product-design and critical-lane review, define the dedicated QA family, external-effect suppression, exact marker, transaction/cleanup contract, audit visibility, failure recovery, and approval boundary before creating any implementation issue.
- **Promote to:** PRD and GitHub issue after the safety contract is approved
- **Links:** `Sifututor/sifu-tutor#2124`, `.agent-os/session-maps/2026-08-16-175754-codex-mode-aware-tutor-request-duplicates.md`, Koda `mem_3084ee4be3aa`

### SIMS-DEPLOY-SAFETY-001.A5 — Return Production From The #2214 Hotfix Branch To Main

- **Project:** sifu-tutor
- **Status:** paused
- **Type:** task
- **Parent:** SIMS-DEPLOY-SAFETY-001
- **End goal:** SIMS production returns to the canonical `main` branch through a separately planned and verified full backend release, without losing the live #2214 and #2224 referral fixes or accidentally releasing an unreviewed backlog.
- **Why it matters:** Issue #2214 was safely deployed from the exact former live SHA because `main` contained 85 unrelated commits, 29 new migrations, and substantial runtime work. The temporary production line later advanced through CRM fee-readiness PR #2217, duplicate-class concurrency PR #2223, and the #2224 first-OTP referral fix. Production is currently running `hotfix/2224-first-otp-referral-production` at `1ebb308cc4075255a232033feb91e88e0e129078`; the original #2214 hotfix `f9afe78eecb23c08395c99e1011c4ab94d0326b9` remains an ancestor. Leaving this divergence undocumented could cause a future operator to pull `main` casually or misunderstand which code is live.
- **Source:** Hafiz-requested #2214 and #2224 targeted production hotfix deployments, #1672 production concurrency release, and explicit save-session follow-ups, 2026-08-20.
- **Next action:** No action now. At the next properly planned full backend release, first re-check the live branch/SHA and current `origin/main`, reconcile the #2214 and #2224 implementations into the release candidate, run the canonical schema-first deployment gates, obtain fresh production approval, then return the production checkout to `main` only after deploy, changed-workflow smoke, and monitoring pass.
- **Promote to:** The next planned full backend release checklist; create a GitHub release issue when that release is scheduled
- **Links:** `Sifututor/sifu-tutor#2214`, `Sifututor/sifu-tutor#2215`, `Sifututor/sifu-tutor#2217`, `Sifututor/sifu-tutor#1672`, `Sifututor/sifu-tutor#2223`, `Sifututor/sifu-tutor#2224`, `Sifututor/sifu-tutor#2225`, `Sifututor/sifututor_tutor#70`, `Sifututor/sifututor_tutor#71`, Koda `mem_99dcfa3c28ba`, Koda `mem_828e90962145`

### SIMS-PAYMENT-AUTHORITY-001 — Review Six Grandfathered Tutor-Payment Overlap Groups

- **Project:** sifu-tutor
- **Status:** paused
- **Type:** mission
- **Parent:** none
- **End goal:** Finance makes an evidence-backed decision for each of the six active legacy class-overlap groups without altering legitimate replacement history or weakening the new atomic payment authority.
- **Why it matters:** Issue #2275 safely isolated all legacy tutor-payment history from new authority keys, but its read-only production audit found six active overlaps across three payment-pair clusters. The correct financial row cannot be inferred from technical fields alone, and a broad deduplication could erase legitimate payment evidence.
- **Source:** Issue #2275 production migration audit and Hafiz's decision to defer historical repair, 2026-08-26.
- **Next action:** Only when Finance is ready, refresh the read-only audit and fingerprint, prepare exact before-images and a per-group decision sheet, obtain Finance's canonical treatment plus Hafiz's separate critical data-mutation approval, then create a scoped GitHub issue for the approved manifest.
- **Do not do yet:** Do not merge, delete, rewrite, or mark any legacy payment/breakdown row canonical automatically. Do not treat the successful authority migration as approval for historical repair.
- **Promote to:** GitHub issue only after Finance approves an exact deterministic repair manifest
- **Links:** `Sifututor/sifu-tutor#2275`, PR `#2291`, release evidence `docs/qa/release-evidence-2026-08-26-e41142969.md`, Koda `mem_0e441718c8c3`

### SIMS-UIUX-AUDIT-2026-08 — Fix The August 2026 Portal-Wide UI/UX Audit Findings

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** The confirmed breaking and urgent findings from the August 2026 staging + production UI/UX audit are triaged into GitHub issues, prioritized by Hafiz, fixed, and re-verified with screenshots against production.
- **Why it matters:** The audit confirmed live production defects, not cosmetics: Sliders cannot be edited or deleted (Actions column hard-coded `display:none`), Cancelled Class Journal stat cards are disconnected from live data (128 shown vs 75,784 real rows), Tutor-Vs-Subject and Parent-Vs-Subject analytics show all-zero rows against non-zero headers, DataTables tables are 100% unreachable on mobile via the shared `dt-no-scroll` class, and real records carry data corruption (mojibake tutor name, double-encoded apostrophes, truncated user email).
- **Source:** Hafiz-requested deep UI/UX scan, sessions 2026-08-11 through 2026-08-13.
- **Next action:** Run `/to-issues` over the audit artifact's Breaking + Urgent findings, leading with the shared-component fixes that clear many pages at once (mobile header-button component, `dt-no-scroll` mobile table CSS, panel-header accent-bar component), then the four data-integrity bugs.
- **Do not do yet:** Do not fix ad hoc without triage — several findings share one root component and piecemeal fixes would waste the leverage. Do not share the artifact link outward without a PII scrub pass (screenshots contain real customer and financial data).
- **Promote to:** GitHub issues at triage time
- **Links:** Audit artifact `https://claude.ai/code/artifact/35913e2e-7ff8-468e-bfc2-f9718f440aac`, `.agent-os/session-maps/2026-08-13-claude-sims-uiux-audit-staging-prod.md`, Koda tag `sifu-tutor` + `audit`

### SIMS-CANCEL-001 — Pilot the governed early Parent cancellation command

- **Project:** sifu-tutor
- **Status:** promoted
- **Type:** mission
- **Parent:** none
- **End goal:** `POST /api/ripple/integration/v1/tutor-request-early-cancellations` (#2452) is merged, its lifecycle-state and permission-grant migrations are applied, and `sims.integration.tutor_request_early_cancellation_admission_enabled` is switched on for an approved pilot with Ripple #841 following.
- **Why it matters:** SIMS is the only decider that a Request may be cancelled early (no class, invoice, fee, payment or in-flight acceptance history), and the command never runs the deactivation cascade; until it is live, Ripple staff still have no governed way to record a parent's early cancellation.
- **Source:** Claude delegation lane 2026-09-07, four local commits on `fix/2451-v7-v8-tutor-workflows` (also carries the #2451 queue contract)
- **Next action:** Follow the Session Release Ledger and activation handback for the paired release and monitoring state; do not repeat the original integration or the already-proven staging cancellation.
- **Do not do yet:** Do not switch the admission flag on before the Ripple capability flag and the permission grant migration are both live; do not reuse `TutorRequestService::updateStatus` for this path.
- **Promote to:** [SIMS PR #2495](https://github.com/Sifututor/sifu-tutor/pull/2495) and [Ripple PR #863](https://github.com/Sifututor/ripple-suite/pull/863); activation handback `.agent-os/delegations/v7-v8-claude-run-2026-09-07/activation-production-handback.md`
- **Links:** sifu-tutor #2451 #2452, ripple-suite #841, handback `.agent-os/delegations/v7-v8-claude-run-2026-09-07/handback.md`, Koda mem_109c55f90864

### SIMS-CLASH-001 — Student-side class clash detection across different tutors

- **Project:** sifu-tutor
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** When any scheduling flow (tutor app add/reschedule, staff portal add/edit) books a slot for a student, the system also checks that STUDENT's other classes with DIFFERENT tutors, so a student cannot be double-booked across tutors.
- **Why it matters:** During the #2482 diagnosis (staff question about reschedule clash rules) we confirmed every clash guard in SIMS is tutor-scoped only. Nobody checks the student's timetable against other tutors, so a student can silently end up with two simultaneous classes with two tutors. Tutors and parents would only discover this when someone shows up.
- **Source:** Issue #2482 diagnosis, 2026-09-08 (see PR #2488 scope notes).
- **Next action:** Product decision from Hafiz — should student-side clashes be hard-blocked (like tutor clashes) or soft-warned (staff/tutor overrides allowed, since parents may genuinely accept back-to-back overlap)? Then promote to a GitHub issue covering all four scheduling flows plus the shared guard location in ClassService.
- **Do not do yet:** Do not implement before the hard-block vs warn decision; changing guard semantics for live schedules without that decision risks blocking legitimate existing bookings.
- **Promote to:** GitHub issue after Hafiz decides the semantics
- **Links:** sifu-tutor #2482, PR #2488, Koda mem_920902be2190 (corrected), mem_60f146d89e82
