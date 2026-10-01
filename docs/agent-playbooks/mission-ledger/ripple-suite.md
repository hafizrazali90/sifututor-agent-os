# Ripple Suite Mission Ledger

Use this for Ripple Suite missions, child tasks, adjacent ideas, and paused
follow-ups.

## Missions

### RS-SETTINGS-001 — Finish Settings and module form-control polish

- **Project:** ripple-suite
- **Status:** paused
- **Type:** mission
- **Parent:** none
- **End goal:** Settings, CRM Settings, PV QuickBooks/COA, and Collection
  settings use consistent compact navigation and 40px normal form controls
  without turning real row actions into oversized buttons.
- **Why it matters:** Slice B fixed the Settings information architecture, but
  the forms inside the selected sections still feel uneven compared with the
  stronger ledger and toolbar pages.
- **Source:** Settings form-control audit and CRM polish session, 2026-07-08
- **Next action:** Promote the first child slice, "Settings form-control
  polish", when Hafiz wants to resume.
- **Promote to:** GitHub issue if the next slice is execution-ready
- **Links:** `ripple-suite/docs/audits/2026-07-08-settings-form-control-audit.md`,
  `Sifututor/ripple-suite#178`, local commit `1281d46`

### RS-SETTINGS-001.1 — Standardize core Settings form controls

- **Project:** ripple-suite
- **Status:** captured
- **Type:** task
- **Parent:** RS-SETTINGS-001
- **End goal:** General, Operations, Finance, and AI settings use a shared
  normal-control rhythm around 40px while compact chips and row actions stay
  compact.
- **Why it matters:** The Settings IA is now correct, but the selected form
  content still has one-off 36-38px controls and inconsistent vertical rhythm.
- **Source:** Settings form-control audit, 2026-07-08
- **Next action:** Add the smallest shared settings control class/helper, apply
  it to the core settings tabs, and protect it with focused E2E/visual evidence.
- **Promote to:** GitHub issue
- **Links:** `ripple-suite/docs/audits/2026-07-08-settings-form-control-audit.md`

### RS-SETTINGS-001.2 — Clean up CRM Settings dense forms

- **Project:** ripple-suite
- **Status:** captured
- **Type:** task
- **Parent:** RS-SETTINGS-001
- **End goal:** CRM Settings feels less cramped across Remarks, Follow-up
  Rules, Round Robin, PIC Exclusions, Lead Sources, Working Days, inactivity
  threshold, and polling without changing the CRM feature model.
- **Why it matters:** CRM Settings remains one of the densest settings surfaces
  after the broader CRM toolbar and interaction-trust polish.
- **Source:** Settings form-control audit, 2026-07-08
- **Next action:** Audit the CRM Settings subsections, normalize primary
  controls, and keep true row actions compact.
- **Promote to:** GitHub issue
- **Links:** `ripple-suite/docs/audits/2026-07-08-settings-form-control-audit.md`

### RS-RECON-001 — Make Ripple reconciliation reliable and staff-safe

- **Project:** ripple-suite
- **Status:** active
- **Type:** mission
- **Parent:** none
- **End goal:** Staff can reconcile receipts, credits, bank rows, and SIMS
  sync with clear evidence, low duplicate risk, and understandable next actions.
- **Why it matters:** Reconciliation mistakes cascade into customer ledger,
  SIMS payment state, and staff confusion.
- **Source:** June 2026 reconciliation cleanup and receipt lifecycle sessions
- **Next action:** Continue promoting the highest-risk triaged child task into
  a GitHub issue or PRD when Hafiz chooses the next slice.
- **Promote to:** Plane mission if this becomes a formal broader roadmap
- **Links:** none yet

### RS-RECON-001.1 — Improve bank matching suggestions from cleanup lessons

- **Project:** ripple-suite
- **Status:** triaged
- **Type:** task
- **Parent:** RS-RECON-001
- **End goal:** Reconciliation matching should suggest safer matches based on
  the real patterns found during data cleanup, not only strict obvious matches.
- **Why it matters:** Manual cleanup showed that some valid matches were missed
  because the matcher was too strict or did not explain enough evidence.
- **Source:** June 2026 reconciliation cleanup sessions
- **Next action:** Gather the recurring cleanup patterns and turn them into a
  matching-improvement PRD or GitHub issue.
- **Promote to:** PRD or GitHub issue
- **Links:** none yet

### RS-RECON-001.2 — Explain overpayment and rounding stories in invoice coverage

- **Project:** ripple-suite
- **Status:** captured
- **Type:** adjacent
- **Parent:** RS-RECON-001
- **End goal:** When a receipt amount is more than invoice allocation, the UI
  clearly shows where the remaining amount went, such as advance credit or
  rounding tolerance.
- **Why it matters:** Staff and Hafiz should not need to infer where small
  amounts like RM0.50 went.
- **Source:** Receipt #169 discussion, June 2026
- **Next action:** Design the invoice coverage and receipt detail wording for
  overpayment/rounding/advance-credit leftovers.
- **Promote to:** GitHub issue
- **Links:** none yet

### RS-RECON-001.3 — Suggest combining duplicate proof uploads into one multi-invoice receipt

- **Project:** ripple-suite
- **Status:** captured
- **Type:** adjacent
- **Parent:** RS-RECON-001
- **End goal:** If two uploaded receipts look like the same proof and together
  equal one bank transaction, Ripple suggests combining them into one receipt
  with multiple invoice allocations.
- **Why it matters:** Staff may upload the same proof twice and then reject one,
  causing lost coverage or duplicate lifecycle confusion.
- **Source:** June 2026 historical split/duplicate receipt cleanup
- **Next action:** Define detection rules: same proof/reference/parent/date,
  combined amount equals bank transaction, and safe staff confirmation flow.
- **Promote to:** PRD or GitHub issue
- **Links:** none yet

### RS-RECON-001.4 — Repair Ripple Playwright auth setup for verification

- **Project:** ripple-suite
- **Status:** done
- **Type:** adjacent
- **Parent:** RS-RECON-001
- **End goal:** Ripple Playwright API/smoke tests can authenticate and run the
  actual test bodies instead of failing during global setup, with an
  authenticated production smoke lane available for deploy proof.
- **Why it matters:** During the Maybank M2E payer-name repair, production and
  browser verification succeeded, but local Playwright checks could not prove
  the route because `tests/global.setup.ts` received 404 from `/api/auth/login`.
  Future reconciliation changes need reliable local journey proof before
  commit, PR, and deploy.
- **Result:** GitHub issue `Sifututor/ripple-suite#174` and PR
  `Sifututor/ripple-suite#175` added configurable Playwright auth state,
  configurable auth verification route, `npm run test:prod-auth-smoke`, and a
  permanent `@prod-auth-smoke` Playwright spec. Production deployed merge
  commit `f3e91261`; authenticated production smoke passed against
  `https://ripple.admin.sifututor.my` and captured the live Customer Receipts
  table screenshot.
- **Source:** Codex Maybank M2E payer-name repair save-session, 2026-07-01;
  Ripple authenticated smoke deploy session, 2026-07-07.
- **Next action:** Optional hardening: create a dedicated low-permission SIMS
  smoke user and map it to Ripple's narrow smoke role so future smoke tests do
  not rely on the temporary admin smoke credential.
- **Promote to:** closed; optional hardening can become a GitHub issue when the
  dedicated account is ready to create.
- **Links:** `Sifututor/ripple-suite#168`, `Sifututor/ripple-suite#169`,
  `Sifututor/ripple-suite#174`, `Sifututor/ripple-suite#175`

### RS-RECON-001.5 — Prevent silent one-cent receipt amount mismatches

- **Project:** ripple-suite
- **Status:** done
- **Type:** adjacent
- **Parent:** RS-RECON-001
- **End goal:** Ripple preserves the staff-entered receipt amount exactly and
  warns clearly when it differs from the uploaded proof or matched bank amount,
  including a RM0.01 difference.
- **Why it matters:** RCPT-1481 stored RM787.49 while its proof and matched bank
  row showed RM787.50. The current matching tolerance accepted the difference,
  which later produced a false unused credit and a confusing reversal workflow.
- **Source:** RCPT-1481 production repair, 2026-07-15
- **Result:** Reproduced safely against the production-equivalent source. A
  single `ArrowDown` press while the native `number` amount field remains
  focused changes RM787.50 to RM787.49; the split request then submits RM630.00
  invoice allocation plus RM157.49 excess, exactly matching RCPT-1481's
  original audit pattern. The uploaded file does not alter the amount. Issue
  #188 now blocks ArrowUp, ArrowDown, and focused-wheel stepping, normalizes
  Customer Receipt money fields to two decimals, and requires explicit UI and
  API acknowledgement for bank differences of RM0.01 or more with audit
  metadata. PR #189 merged as `14bed6d5`, deployed to KVM8 production, and the
  authenticated non-mutating browser smoke proved both safeguards live.
- **Next action:** Closed. Keep the permanent browser/API regressions and audit
  the separately parked Collection Receipt, Record Payment, and Apply Credit
  number inputs only through a future issue if Hafiz chooses that scope.
- **Promote to:** closed via GitHub issue #188
- **Links:** `Sifututor/ripple-suite#188`, `Sifututor/ripple-suite#189`, `.agent-os/session-maps/2026-07-15-184327-codex-ripple-issue-188-prod.md`, `.agent-os/session-maps/2026-07-15-160312-codex-ripple-rcpt-1481-repair.md`

### RS-RECEIPT-001 — Make receipt proof preview clear and inspectable

- **Project:** ripple-suite
- **Status:** active
- **Type:** mission
- **Parent:** none
- **End goal:** Staff can inspect uploaded receipt proof directly inside Ripple
  without blocked PDFs, runaway page height, or confusion about original files.
- **Why it matters:** Receipt proof is finance evidence; the viewer must be
  convenient without altering the uploaded proof.
- **Source:** PDF preview and auto-fit production session, 2026-06-12
- **Next action:** Decide whether zoom controls are needed after staff try the
  bounded auto-fit viewer.
- **Promote to:** none yet
- **Links:** PR #147, PR #149

### RS-RECEIPT-001.1 — Add receipt preview zoom and fit controls

- **Project:** ripple-suite
- **Status:** triaged
- **Type:** task
- **Parent:** RS-RECEIPT-001
- **End goal:** Staff can switch between Fit page, Fit width, zoom in, and zoom
  out without opening the original file.
- **Why it matters:** Auto-fit keeps the page clean, but detailed inspection may
  need controlled zoom.
- **Source:** RCPT PDF preview session, 2026-06-12
- **Next action:** Wait for staff/Hafiz feedback on whether current auto-fit is
  enough, then promote if needed.
- **Promote to:** GitHub issue
- **Links:** PR #149

### RS-RECEIPT-001.2 — Keep original proof untouched while improving viewer

- **Project:** ripple-suite
- **Status:** triaged
- **Type:** risk
- **Parent:** RS-RECEIPT-001
- **End goal:** Any future preview improvement changes display behavior only,
  not the uploaded receipt proof file.
- **Why it matters:** Receipt files are finance evidence. Silent resizing,
  cropping, rotating, or compressing would make the original proof ambiguous.
- **Source:** Hafiz correction from auto-fit discussion, 2026-06-12
- **Next action:** Treat this as a design constraint for every receipt preview
  or upload improvement.
- **Promote to:** Koda if not already stored
- **Links:** PR #149

### RS-RECEIPT-002 — Make generated bank-confirmed receipts understandable to staff

- **Project:** ripple-suite
- **Status:** captured
- **Type:** mission
- **Parent:** RS-RECON-001
- **End goal:** Staff understand when a receipt record was generated from a bank
  match without an uploaded proof, and know how to attach the real proof later.
- **Why it matters:** Generated receipts can look like normal uploaded receipts,
  which can confuse staff during later receipt upload.
- **Source:** Receipt #704 generated receipt discussion, June 2026
- **Next action:** Review current UI after recent changes and decide whether
  normal upload should suggest attaching to generated receipt records.
- **Promote to:** GitHub issue or PRD
- **Links:** none yet

### RS-CF-001 — Record Commitment Fees from full payments and parent credit

- **Project:** ripple-suite
- **Status:** done
- **Type:** mission
- **Parent:** none
- **End goal:** A parent's payment that includes the Commitment Fee is recorded
  once and linked to the TREQ; the fee is paid in SIMS from it, and the rest
  stays as parent credit. Finance can also pay a fee from existing credit.
- **Why it matters:** Staff had no correct way to record a full advance that
  included the fee (original staff report, TREQ-505012 / CRM-98300).
- **Source:** Session f4ec316a, 1 to 2 Oct 2026; Codex handoff pack for #1376
- **Next action:** None. Reopen `Sifututor/ripple-suite#1376` if staff report a
  problem; the follow-ups below hold the remaining work.
- **Promote to:** none yet
- **Links:** `Sifututor/ripple-suite#1376`, PRs #1383, #1386, #1389, #1392,
  #1403, #1405, #1408; production releases a60ef35e and fb5ed23f; staff
  guide `docs/features/accounts/advance-credit-commitment-fees/staff-guide.md`

### RS-CF-001.1 — Resolve missing Commitment Fee records one case at a time

- **Project:** ripple-suite
- **Status:** paused
- **Type:** task
- **Parent:** RS-CF-001
- **End goal:** Finance can create a missing fee record from Ripple as owed,
  paid from credit, or waived, at most one fee per parent, without going to SIMS.
- **Why it matters:** Before 22 Jul 2026 SIMS charged one fee per parent, so
  older requests may lack a fee row. On 2 Oct 2026, 375 active requests of
  un-registered parents had none; only TREQ-505012 had a tutor matched. Hafiz
  decided no bulk backfill.
- **Source:** Session f4ec316a, 2 Oct 2026
- **Next action:** Start when another blocked older request appears; fee 22601
  for TREQ-505012 was created manually with Hafiz's approval.
- **Promote to:** GitHub issue (done)
- **Links:** `Sifututor/ripple-suite#1396`

### RS-CF-001.2 — Show a just-paid fee as paid without the 2-minute delay

- **Project:** ripple-suite
- **Status:** promoted
- **Type:** task
- **Parent:** RS-CF-001
- **End goal:** CRM screens show a Commitment Fee as paid as soon as SIMS
  settles it.
- **Why it matters:** The fee readiness display cache (#1382) can show
  "Awaiting parent fee" for up to 2 minutes (10 on the Worklist), which can
  make a PIC upload twice.
- **Source:** Cross-session check with the #1379 and #1360 sessions, 2 Oct 2026
- **Next action:** Ships inside the #1360 release (owner: #1360 session).
- **Promote to:** GitHub issue (done)
- **Links:** `Sifututor/ripple-suite#1391`, #1360

### RS-CF-001.3 — CX Sales production smoke account

- **Project:** ripple-suite
- **Status:** done
- **Type:** question
- **Parent:** RS-CF-001
- **End goal:** A read-only CX Sales test account proves role-based features in
  production, the way the QA Helpdesk account does for Helpdesk.
- **Why it matters:** The only positive production smoke account is a
  superadmin, which passes some checks through superadmin shortcuts.
- **Source:** Production smoke of fb5ed23f, 2 Oct 2026
- **Result:** Created 2 Oct 2026 with Hafiz's approval by the Helpdesk
  session through SIMS Add Staff: SIMS user 377, QA CX Sales (smoke test),
  Customer Experience (Sales). Lane file `ripple-prod-smoke-cxsales.conf`
  (access map lane 26). Read-only production check passed: role
  `customer_experience_sales` holds `crm.record_commitment_fee_receipt`, the
  fee lookup on a Request it does not own returns 403, and the Request page
  shows "You cannot view Request details" with no upload button.
- **Next action:** None. Use the lane for CX Sales permission smokes; it owns
  no Requests, so it cannot show owned-Request screens.
- **Promote to:** closed
- **Links:** `tests/e2e/smoke/commitment-fee-permission-production.spec.ts`

### RS-CF-001.4 — Check how "Payment, fee needs review" is used

- **Project:** ripple-suite
- **Status:** captured
- **Type:** task
- **Parent:** RS-CF-001
- **End goal:** Know whether the fee-review option is a rare safety net or a
  shortcut, from real use.
- **Why it matters:** Hafiz decided on 2 Oct 2026 to keep it (payment recorded
  once as credit with a Finance review case, never a fee created). Real use
  shows whether missing fee records need the #1396 action, or the wording needs
  tightening.
- **Source:** Session f4ec316a decision, 2 Oct 2026
- **Next action:** Around 2 Nov 2026, count `commitment_fee_review` cases and
  their reasons read-only and report to Hafiz.
- **Promote to:** none yet
- **Links:** `Sifututor/ripple-suite#1376`, `Sifututor/ripple-suite#1396`

### RS-CX-ROSTER-001 — Reconcile CX roster and agree work handover

- **Project:** ripple-suite
- **Status:** paused
- **Type:** mission
- **Parent:** none
- **End goal:** CX allocation roster reflects the approved current ST team, with any existing work handover explicitly agreed.
- **Why it matters:** Operations confirmed extra accounts in the eligible roster; changing eligibility must not silently redistribute existing work.
- **Source:** Hafiz allocation support session, 2026-09-21; explicitly deferred staff cleanup.
- **Next action:** Resume only when Hafiz requests it; recheck the current roster and prepare exact account corrections and recipient choices for approval. No automatic deactivation, role changes or reassignment. NakNgaji integration has not rolled out and is not part of this follow-up.
- **Promote to:** GitHub issue after scope and correction recipients are agreed
- **Links:** https://github.com/Sifututor/ripple-suite/issues/1129; .agent-os/session-maps/2026-09-21-063600-codex-1129-allocation-save.md

- **Follow-ups reaffirmed by Hafiz:** Keep for later: (1) Operations confirms CX availability for the actual operating day in CRM Settings > Team attendance before assigning leads; completion has not been verified. (2) Resigned/transferred staff cleanup and review of existing assignments remain deferred. This reminder authorises no settings, staff or assignment changes.

### RS-V16-001 — Land the V16 operational-spreadsheet migration (#1089) safely

- **Project:** ripple-suite
- **Status:** active
- **Type:** mission
- **Parent:** none
- **End goal:** The P1-P8 V16 migration build (local, uncommitted on `worktree-ripple-1089-v16-migration`) is renumbered, rebased, independently reviewed by Codex, then committed and released through the protected lane with the sealed staff workbook answered by staff.
- **Why it matters:** Seven local passes and five Codex reviews have made the build genuinely verified (rehearsal 200/200, migrations 82/82, races proven), but it is still local-only and now collides with `origin/main` migration numbers.
- **Source:** Claude V16 sessions 2026-09-19 to 2026-09-22; Codex independent reviews four and five.
- **Next action:** RS-V16-001.1 below, then hand back to Codex for its next independent review.
- **Promote to:** existing GitHub issue #1089 once renumbered and rebased
- **Links:** .agent-os/session-maps/2026-09-22-104800-claude-v16-review-holds-race-save.md; ripple-suite/.agent-os/reports/v16-migration-2026-09-19/claude-p1-p8-final-completion-handback.md

### RS-V16-001.1 — Renumber V16 migrations 190-193 and rebase onto origin/main

- **Project:** ripple-suite
- **Status:** captured
- **Type:** task
- **Parent:** RS-V16-001
- **End goal:** V16 migrations 190-193 become 192-195 (179-189 are free on both `origin/main` and `origin/staging`; main's highest is 191 from CRM PRs #1130/#1136), every reference is updated (both test scripts, dry-run schema chain, TESTING.md, handback, docs/features/v16-migration), the branch is rebased onto `origin/main` (20 behind at 2026-09-22), and the full local chain reruns green.
- **Why it matters:** Publishing with a colliding migration number is refused by the protected lane; fixing it before review avoids a wasted Codex round.
- **Source:** Fresh `git fetch` at the 2026-09-22 save-session.
- **Next action:** Do the renumber and rebase on the worktree, rerun `test-v16-migrations-181-182-postgres` and `test-v16-package-dry-run`, then update the handback numbers.
- **Promote to:** part of the #1089 PR
- **Links:** none yet

### RS-V16-001.A1 — Ingest completed staff answers from the sealed V16 workbook (Path B)

- **Project:** ripple-suite
- **Status:** captured
- **Type:** adjacent
- **Parent:** RS-V16-001
- **End goal:** A separately approved phase adds explicit immutable decision fields, reviewer identity and provenance to the three review tables, plus a safe ingestion path from `v16-staff-confirmations.xlsx`, under the same per-key advisory lock the writers already use.
- **Why it matters:** This phase deliberately records question-version and resolution-marker state only; staff answers stay in the sealed workbook until this is approved.
- **Source:** Codex fifth review, Path A/B choice, 2026-09-22.
- **Next action:** Wait for Hafiz to decide whether and when to scope it. Do not infer approval.
- **Promote to:** PRD after Hafiz decision
- **Links:** none yet

### RS-RECON-001.A1 — Automatic Ripple GitHub CI paused

- **Project:** ripple-suite
- **Status:** paused
- **Type:** adjacent
- **Parent:** RS-RECON-001
- **End goal:** Use manual local checks and staging proof as the current release path. Revisit automatic pull-request and main-branch CI only if Hafiz explicitly requests it.
- **Why it matters:** Automatic CI is paused. Releases must keep using the documented manual evidence path without making account administration a deployment topic.
- **Source:** Bank-rule release session, 2026-09-23; issue #1176 and PR #1178.
- **Next action:** No action during deployments. If Hafiz later requests CI restoration, scope it separately, restore the documented triggers in an issue and PR, run manual checks before merge, and verify automatic runs start successfully.
- **Promote to:** GitHub issue when Hafiz requests restoration
- **Links:** https://github.com/Sifututor/ripple-suite/issues/1176; https://github.com/Sifututor/ripple-suite/pull/1178; ripple-suite/docs/qa/github-actions-manual-checks.md; .agent-os/session-maps/2026-09-22-170000-codex-ripple-cdm.md


### RS-OUTREACH-HEARTBEAT-001 — Revisit external outreach heartbeat alerts later

- **Project:** ripple-suite
- **Status:** paused
- **Type:** mission
- **Parent:** none
- **Why it matters:** Preserve the owner deferral without claiming external alert delivery was verified.
- **Promote to:** GitHub issue when Hafiz explicitly resumes monitoring setup
- **End goal:** Verify delivered external failure and recovery alerts for tutor outreach when Hafiz chooses to resume monitoring setup.
- **Source:** Hafiz, 29 September 2026: "can we do thos later? please remember this".
- **Decision:** Defer heartbeat purchase/setup; earlier US$20/month approval is on hold. Nothing purchased. Do not repeatedly block outreach progress on this deferred item or represent its tests as passed.
- **Next action:** Wait until Hafiz explicitly revisits external heartbeat monitoring. Keep the staging wakeup timer running; this decision does not authorise production deployment.
- **Links:** .agent-os/handoffs/2026-09-29-tutor-outreach-bundle-2-staging-result.md; https://github.com/Sifututor/ripple-suite/pull/1300

### RS-OUTREACH-SPEED-001 — Speed up tutor outreach preview after launch

- **Project:** ripple-suite
- **Status:** active
- **Type:** mission
- **Parent:** none
- **End goal:** Prepare tutor offers quickly without reducing suitable applications, request coverage, or cost performance against current automation and the staff manual baseline.
- **Why it matters:** The live preview was still progressing after about 90 minutes; local no-send evidence and code inspection identify repeated planning across checkpointed slices as a likely contributor, but production timing has not been fully attributed.
- **Source:** Hafiz, 30 September 2026: initially defer; after the missed 09:00 send, Claude should solve and prepare a PR for independent Codex review.
- **Next action:** Claude diagnoses new production job failures first, then builds and proves the smallest preview-progress repair in an owned worktree and prepares a PR. Codex independently reviews it before release.
- **Promote to:** GitHub issue/PR through Claude's approved workflow
- **Links:** .agent-os/handoffs/2026-09-30-tutor-outreach-preview-delay-claude-handoff.md; .agent-os/session-maps/2026-09-28-codex-outreach-durable-runtime.md; .agent-os/handoffs/2026-09-28-tutor-outreach-workload-review.md
