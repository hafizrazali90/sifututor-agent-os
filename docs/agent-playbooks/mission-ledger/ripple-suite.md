# Ripple Suite Mission Ledger

Use this for Ripple Suite missions, child tasks, adjacent ideas, and paused
follow-ups.

## Missions

### RS-STAFF-WORKSPACE-001 — Make Ripple the primary workspace for staff operations

- **Project:** ripple-suite + sifu-tutor
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** Staff complete their normal operational work in Ripple while
  SIMS remains the authoritative backend for Tutor Requests, pricing, invoices,
  classes, permissions, and audit history.
- **Why it matters:** Splitting ordinary work between Ripple and SIMS makes
  staff learn two interfaces and increases the chance that they use a display
  or legacy edit path instead of the governed business workflow.
- **Source:** Hafiz follow-up after the production class-frequency and session-duration capability check, 2026-08-26
- **Next action:** Prioritise one governed SIMS-backed workflow at a time and
  design the Ripple entry point, authoritative API contract, permission and
  failure states, permanent E2E journey, and release communication before
  implementation.
- **Promote to:** Cross-project PRD / backend contract and GitHub issues when prioritised
- **Links:** Koda architecture memory `mem_b18563d136b0`

### RS-STAFF-WORKSPACE-001.1 — Amend Sifututor class frequency and duration from Ripple

- **Project:** ripple-suite + sifu-tutor
- **Status:** captured
- **Type:** task
- **Parent:** RS-STAFF-WORKSPACE-001
- **End goal:** An authorised staff member can change an existing normal
  Sifututor Tutor Request's classes per month and duration per session from its
  Ripple Request workspace, with the same governed result currently available
  through SIMS `Amend Request`.
- **Why it matters:** Ripple is intended to be the staff workspace, but the
  current production Ripple amendment panel is limited to Nakngaji. Staff must
  return to SIMS to amend an ordinary Sifututor request even though Ripple
  already owns their operational workspace.
- **Source:** Hafiz follow-up after the production SIMS/Ripple capability check, 2026-08-26
- **Next action:** Produce a cross-project Product Shape or Build-Ready Pack
  that reuses SIMS as the source of truth and specifies the real Request entry
  point; eligibility and permission parity; current/proposed price, invoice,
  commission, tutor-payment and class consequences; reason and effective-point
  rules; audit history; idempotent command and recovery behavior; Ripple/SIMS
  refresh; backwards compatibility; and permanent browser/API contract
  evidence. Do not implement this as a direct Ripple database edit or duplicate
  SIMS pricing logic.
- **Promote to:** Cross-project PRD / backend contract, then linked Ripple and SIMS GitHub issues
- **Links:** Existing SIMS `Amend Request` workflow and Ripple Nakngaji `Change request details` workflow; Koda architecture memory `mem_b18563d136b0`

### RS-STAFF-WORKSPACE-001.2 — Seal and review the historical CRM source artifact

- **Project:** ripple-suite + sifu-tutor
- **Status:** promoted
- **Type:** research
- **Parent:** RS-STAFF-WORKSPACE-001
- **End goal:** The legacy CX onboarding spreadsheets can be imported into the
  live canonical CRM with source receipts, target fingerprints, deterministic
  links, idempotent replay, ownership review, and rollback evidence.
- **Why it matters:** The canonical application and schema foundation is live,
  but enabling historical recovery without the protected receipts and target
  fingerprints could attach old Tutor Requests to the wrong Lead or staff
  owner.
- **Source:** Canonical CRM recovery production release, 2026-08-27
- **Next action:** Obtain the protected legacy migration receipts and target
  fingerprints through an approved read-only evidence lane, then regenerate
  and independently review the sealed apply artifact before any import or flag
  activation.
- **Promote to:** GitHub issue and controlled migration runbook after the source artifact is sealed
- **Links:** `.agent-os/evidence/crm-canonical-recovery-source-readiness-2026-08-27.json`, `.agent-os/evidence/crm-canonical-recovery-session-release-ledger-2026-08-27.md`, `Sifututor/ripple-suite#685`

### RS-RELEASE-001 — Restore Ripple staging as a trustworthy release rehearsal

- **Project:** ripple-suite
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** The Ripple staging branch and environment can receive current
  main releases without large conflict sets and can prove the same deployment,
  migration, auth, and user journeys expected in production.
- **Why it matters:** During the role-access release, staging was 308 main
  commits behind and also carried 165 staging-only commits. Both a main merge
  and a narrow release cherry-pick produced extensive conflicts, so calling
  that environment a production rehearsal would have created false confidence.
- **Source:** Ripple issue #634 production release, 2026-08-26
- **Next action:** Audit the 165 staging-only commits, classify disposable
  environment changes versus product history, then prepare a dedicated
  reconciliation plan with backup, reset/rebuild, migration, permanent E2E and
  rollback evidence before changing the staging branch.
- **Promote to:** GitHub issue and release-infrastructure plan when prioritised
- **Links:** `Sifututor/ripple-suite#634`,
  `.agent-os/session-maps/2026-08-26-codex-ripple-rbac-release.md`

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

### RS-RECON-001.10 — Deep financial integrity audit following staff allocation reports

- **Project:** ripple-suite / sifu-tutor
- **Status:** paused
- **Type:** research
- **Parent:** RS-RECON-001
- **End goal:** Explain and reconcile the complete money trail across receipts,
  invoice allocations, deductions, advance credits, credit applications,
  customer ledgers, coverage caches, and SIMS payment status; identify other
  affected records and prevent recurrence with lasting regression coverage.
- **Why it matters:** The current staff reports expose both incorrect historical
  allocation repair and invoice eligibility depending on ledger display filters.
  Fixing individual examples alone does not establish financial integrity.
- **Source:** Hafiz explicitly requested a later deep analysis and audit of all
  financial issues in the staff-report diagnosis batch, 2026-09-06.
- **Scope:** Use RCPT-543 (PINV-230298, PINV-108337, PINV-175714) and
  PINV-916659 / RCPT-1838 as starting cases, plus further financial reports in
  this batch. Revalidate current evidence before relying on earlier diagnoses.
  Review allocation versus credit conservation without double counting mirrored
  payment records; gross/net/deduction calculations; rounding; invoice eligibility
  across date/request filters; stale caches; SIMS synchronisation; bank-match
  corrections, reversals, retries and concurrent actions; staff permissions and
  audit trails; prior repair scripts and regression gaps. Run scoped read-only
  scans for the same failure patterns across other customers.
- **Deliverable:** Evidence-backed findings with root causes, affected records
  and amounts, severity, reconciled before/after expectations, proposed repairs
  and prevention, and permanent API/browser regression requirements. Separate
  confirmed findings from hypotheses and record what remains unverified.
- **Boundary:** Parked for later; this note does not start the audit or authorise
  financial data changes. Tutor login-phone recovery stays a separate auth item.
- **Update 2026-09-08:** Scoped pattern checks and approved production repairs
  are recorded in the local staff-issue Session Map; this does not establish
  completion of the broader financial audit. Remaining business questions:
  ownership of RCPT-76, RCPT-934, RCPT-1056 and RCPT-1312; the SIMS unpaid
  reversal for PINV-645649; and settlement of the RM57.50 difference on
  PINV-373652. Combined Accounts message drafted, sending not confirmed.
- **Next action:** Obtain Accounts' ownership and settlement evidence, then
  revalidate live records read-only and propose exact guarded corrections.
  Do not infer a credit/refund or change ownership from shared contact details.
- **Promote to:** Financial audit report and linked GitHub issues after findings
  establish execution-ready scope
- **Links:** Koda `mem_1857`, `mem_97af8231ec6e`; staff-report diagnosis session
  dated 2026-09-06

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

### RS-RECON-001.6 — Review remaining Ripple and SIMS invoice-state mismatches

- **Project:** ripple-suite
- **Status:** paused
- **Type:** question
- **Parent:** RS-RECON-001
- **End goal:** Every verified Ripple payment has the correct SIMS invoice
  state, and every SIMS-paid invoice has an evidence-backed Ripple state.
- **Why it matters:** The production audit found six fully covered invoices
  waiting for their first authorised SIMS update and two older SIMS-paid
  invoices whose Ripple status still needs evidence review.
- **Source:** Ripple-to-SIMS payment sync audit and staff-guide release,
  2026-07-28 to 2026-07-29
- **Next action:** Resume as a separate critical-lane task only after Hafiz
  explicitly approves the exact invoice targets and proposed write plan.
- **Promote to:** GitHub issue or controlled production repair plan after
  approval
- **Links:** `.agent-os/session-maps/2026-07-28-232644-codex-ripple-sims-payment-sync-audit.md`

### RS-RECON-001.7 — Decide whether to publish the Invoice Payment Updates announcement

- **Project:** ripple-suite
- **Status:** paused
- **Type:** question
- **Parent:** RS-RECON-001
- **End goal:** Staff receive the right amount of release communication without
  duplicating the live Help guide and WhatsApp announcement.
- **Why it matters:** A tested v1.18.3 What's New entry and safe publisher exist,
  but production publication was intentionally excluded from the approved
  release. The Help guide and external staff message are already live.
- **Source:** Issue #265 and PR #270 release close-out, 2026-07-29
- **Next action:** Publish only if Hafiz decides the in-app announcement still
  adds value after staff receive the WhatsApp guide link.
- **Promote to:** none yet
- **Links:** `Sifututor/ripple-suite#265`, `Sifututor/ripple-suite#270`

### RS-RECON-001.8 — Align the legacy match-detail SIMS action with finance safeguards

- **Project:** ripple-suite
- **Status:** promoted
- **Type:** risk
- **Parent:** RS-RECON-001
- **End goal:** Every path that can mark an invoice paid in SIMS uses the same
  finance-approval boundary and current-evidence safeguards.
- **Why it matters:** The legacy reconciliation match-detail action uses a
  different permission and safeguard path from Invoice Payment Updates.
- **Source:** Related-impact review for issue #265, 2026-07-28
- **Next action:** Diagnose GitHub issue #268 before changing any permission or
  payment behavior.
- **Promote to:** GitHub issue
- **Links:** `Sifututor/ripple-suite#268`

### RS-RECON-001.9 — Let authorised staff move an applied customer credit safely

- **Project:** ripple-suite
- **Status:** captured
- **Type:** task
- **Parent:** RS-RECON-001
- **End goal:** An authorised Accounts administrator can move a customer-credit
  application from the wrong unpaid invoice to the correct unpaid invoice for
  the same parent without deleting the receipt, losing bank evidence, or
  requiring a direct production database correction.
- **Why it matters:** RCPT-1806 had a valid confirmed RM52.50 bank payment, but
  its fully applied customer credit was attached to the wrong invoice. Ripple
  correctly blocked unlinking, yet offered no reversal or move action, so the
  correction required an approved guarded production transaction.
- **Source:** RCPT-1806 / PINV-367391 production correction session, 2026-08-19
- **Next action:** When Hafiz chooses this slice, define an admin-only atomic
  move workflow with a mandatory reason, same-parent and remaining-capacity
  validation, synced-invoice guards, row locking, coverage recalculation,
  append-only audit evidence, and permanent API plus browser regression tests.
- **Promote to:** GitHub issue after product/permission scope approval
- **Links:** Koda `mem_a5e4b2cc47a8`; production audit entry `#73803`

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

### RS-CRM-INTEGRATION-001 — Activate Ripple–SIMS CRM admission safely

- **Project:** cross-project (ripple-suite + sifu-tutor + separately handed-off Tutor App contract)
- **Status:** active
- **Type:** mission
- **Parent:** none
- **End goal:** Ripple can send governed CRM commands to SIMS and receive signed
  SIMS events in production with exact actor authority, idempotency, recovery,
  visible incidents, monitored rollback, and no unsafe effect on real customer
  or financial work.
- **Why it matters:** Production admission is now active for the approved CRM
  capabilities. A later SIMS config-cache rebuild disabled the acceptance-lease
  gate while Ripple still exposed Contact outcome, causing truthful staff
  submissions to fail with `503`; the live correction is proven, but the paired
  flags need a durable release/health guard.
- **Source:** Issues Ripple #294/#295/#296 and SIMS #1842/#1865; protected
  staging matrix completed 2026-07-30; production Contact outcome incident and
  recovery verified 2026-08-26.
- **Next action:** Promote the recurrence prevention into a cross-project
  engineering issue: release and health checks must compare every Ripple-live
  capability with its paired SIMS admission flag and fail clearly before or
  immediately after a config-cache rebuild.
- **Promote to:** GitHub issue
- **Links:** `Sifututor/ripple-suite#294`, `Sifututor/ripple-suite#295`,
  `Sifututor/ripple-suite#296`, `Sifututor/sifu-tutor#1842`,
  `Sifututor/sifu-tutor#1865`,
  `.agent-os/session-maps/artifacts/ripple-crm-stage0b-staging/staging-proof-2026-07-30.md`,
  Koda `mem_a5e1d6fa4cac`

### RS-CRM-CORRECTIONS-001 — Correct CRM foundations before the next business slice

- **Project:** cross-project (ripple-suite + sifu-tutor)
- **Status:** active
- **Type:** mission
- **Parent:** none
- **End goal:** Real Tutor Request creation is durable across Ripple and SIMS,
  staff see truthful broadcast and Profile delivery states, consequential actions
  have verified actor and atomic audit, controls are explicit, stale-Request
  behavior is measured before replacement, and first-class creation survives
  notification failure.
- **Why it matters:** Building more CRM screens on the current gaps could create
  duplicate Requests, false funnel states, incomplete audit, unsafe hidden
  controls, or class operations coupled to notification delivery.
- **Source:** Final CRM implementation gap analysis and pre-slice corrections
  Build-Ready Pack, 2026-08-02.
- **Current decision:** Hafiz approved the first-class Ripple Family foundation
  and the complete safe production CRM programme. SIMS production runs
  `8a3b2a75`; Ripple production runs the first-class PostgreSQL hotfix
  `4c1a89b3`. Ripple migrations 089 through 097 and the reviewed SIMS
  permission migration are applied. The correct CX roles, exact Profile
  delivery evidence, and first-class exception monitoring are live.
  Authenticated production smoke and post-hotfix idempotency checks passed.
  Tutor Request creation remains disabled by both safety switches. Do not
  continue aliasing `crm_leads.id` as the Family identity. One stable Family
  retains several Lead journeys and independent Tutor Requests without
  rewriting old acquisition outcomes.
- **Next action:** prepare the separate Tutor Request creation activation
  release only when Hafiz explicitly approves that go-live decision. Preserve
  the current disabled switches until the protected activation rehearsal,
  Hafiz-led UAT, rollback steps, and monitoring plan are current.
- **Promote to:** Separate Ripple and SIMS GitHub issues when each correction
  release is approved for implementation.
- **Links:** `ripple-suite/docs/features/crm/pre-slice-corrections-build-ready-pack-2026-08-02.md`,
  `ripple-suite/docs/features/crm/c1-safe-tutor-request-creation-build-ready-pack-2026-08-02.md`,
  `ripple-suite/docs/features/crm/final-overall-implementation-gap-analysis-2026-08-02.md`,
  `.agent-os/session-maps/2026-07-18-210856-codex-ripple-crm-rereview.md`,
  SIMS production PRs `Sifututor/sifu-tutor#1905` and
  `Sifututor/sifu-tutor#1909`, Ripple production PRs
  `Sifututor/ripple-suite#328`, `Sifututor/ripple-suite#329`,
  `Sifututor/ripple-suite#333`, `Sifututor/ripple-suite#334`, and
  `Sifututor/ripple-suite#337`,
  `.agent-os/session-maps/artifacts/crm-production-release-2026-08-04/release-evidence.md`,
  Koda `mem_ca9a7277d374`, `mem_4891cebab10b`, `mem_5320b5039ac4`,
  `mem_7bbe1758373c`

### RS-CRM-MATCHING-001 — Complete the Request-to-first-class matching journey

- **Project:** cross-project (ripple-suite + sifu-tutor)
- **Status:** paused
- **Type:** mission
- **Parent:** RS-CRM-CORRECTIONS-001
- **End goal:** CX Support can open one exact Tutor Request workspace and move
  from the canonical Ripple matching engine through controlled sourcing, exact tutor interest, independent
  Tutor Profile delivery, one parent decision, Tutor Experience verification,
  authoritative assignment and the first verified class with truthful audit and
  recovery throughout.
- **Why it matters:** Current matching, Tutor Profiles and CRM worklists are
  separate journeys. Ripple cannot yet prove which profile was delivered, retain
  valid backups safely, or converge parent choice with SIMS verification,
  assignment and class truth without parallel manual status updates.
- **Source:** Hafiz CRM matching and candidate journey discussion, 2026-08-14.
- **Current decision:** S1-S11, G2 and the complete S12 staging release are
  accepted by the execution session. The S12 checker is GREEN with 266/266
  obligations resolved; staging GJ-01-GJ-10 passed 12/12, the role/operation
  matrix passed 105/105 and browser/visual QA passed 136/136 with 12 reviewed
  screenshots. The feature branches are merged, the exact CRM trees are
  staged, the pre-UAT safe configuration is restored and production remains
  untouched for the separately gated full S12 rollout. A narrower CRM usability
  release is live as of 2026-08-25 at exact production SHA
  `a43eeb4da97e518a59fd8508277d2299f27f3faa`: Tutor sourcing setup is automatic,
  staff can shortlist several tutors together, incomplete Student and stale-data
  failures give actionable explanations, and the reviewed headings, task filters,
  navigation, metric cards and staff language are included. This release applied
  no database migration and deliberately excluded the unrelated Nakngaji work.
- **Next action:** Return `s12-final-handback.md` to the original CRM review
  chat for independent challenge and the separate G3 decision. Do not deploy,
  migrate, mutate data, activate flags or begin a cohort in production without
  that later explicit authority.
- **Promote to:** Existing GitHub issues Ripple #420, SIMS #2110 and Tutor App
  #54 are merged. Any production rollout begins only after independent G3
  approval; this mission is not live.
- **Links:** `ripple-suite/docs/features/crm/tutor-matching-candidate-product-shape-2026-08-14.md`,
  `ripple-suite/docs/features/crm/tutor-matching-candidate-build-ready-pack-2026-08-14.md`,
  `.agent-os/session-maps/2026-08-14-194707-codex-crm-matching-candidate-design.md`,
  `Sifututor/ripple-suite#581`, `Sifututor/ripple-suite#582`,
  `Sifututor/ripple-suite#583`, `Sifututor/ripple-suite#584`,
  `Sifututor/ripple-suite#585`, `Sifututor/ripple-suite#586`,
  `Sifututor/ripple-suite#587`, `Sifututor/ripple-suite#590`

### RS-CRM-MATCHING-001.1 — Continue the adversarial CRM usability review

- **Project:** ripple-suite
- **Status:** triaged
- **Type:** task
- **Parent:** RS-CRM-MATCHING-001
- **End goal:** Review the remaining CRM staff journeys one by one and remove
  controls, hidden prerequisites, vague failures and unnecessary navigation
  that make normal work harder than the business process requires.
- **Why it matters:** The sourcing and shortlist release proved that technically
  valid internal states can still create a confusing staff journey. Similar
  friction should be found proactively rather than waiting for another staff
  complaint.
- **Source:** Hafiz's full CRM adversarial-review direction and production
  close-out, 2026-08-25.
- **Next action:** Start from current production evidence, select the next single
  high-impact staff journey, explain the friction and recommended simpler model
  in non-technical language, then promote the concrete fix to a GitHub issue
  before implementation.
- **Promote to:** GitHub issue after the next exact journey is selected
- **Links:** `Sifututor/ripple-suite#589`, Koda `mem_b0a3fa209029`

### RS-CRM-COMMS-001 — Connect CX customer communications to Ripple CRM

- **Project:** ripple-suite (with Finch and a future business telephony provider)
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** Ripple has a truthful, replay-safe customer communication
  timeline and task automation from manual CX outcomes, Finch WhatsApp events,
  and provider-verified business calls, with transparent CX activity and
  quality coaching.
- **Why it matters:** Current `tel:` and `wa.me` links return no result to
  Ripple, so replies, failures, call activity, follow-up work, and coaching
  evidence remain manual and can create blind spots.
- **Source:** Hafiz CRM re-review confirmation, 2026-07-19
- **Next action:** Continue the CRM status decisions; when this mission is
  prioritised, run provider/privacy discovery and promote it into a
  cross-project Build-Ready Pack before creating implementation issues.
- **Promote to:** PRD / UX / backend integration contract, then cross-project
  GitHub issues
- **Links:** `ripple-suite/docs/features/crm/communication-integration-future-plan.md`, `.agent-os/session-maps/2026-07-18-210856-codex-ripple-crm-rereview.md`

### RS-CRM-COMMS-001.1 — Sync Finch WhatsApp evidence to Ripple

- **Project:** ripple-suite + finch-inbox
- **Status:** captured
- **Type:** task
- **Parent:** RS-CRM-COMMS-001
- **End goal:** Signed, versioned, idempotent Finch sent/delivered/read/failed
  and inbound events link to the correct Ripple Lead/family and create safe
  response/failure work without guessing customer intent.
- **Why it matters:** Finch can observe WhatsApp events internally, but Ripple
  currently has no event bridge and cannot close the operational loop.
- **Source:** Hafiz CRM re-review confirmation, 2026-07-19
- **Next action:** Confirm tenant/session scope, identity-link rules, event
  contract, message-content boundary, retry/replay behavior, and shadow rollout.
- **Promote to:** Cross-project PRD/backend contract and GitHub issues
- **Links:** `ripple-suite/docs/features/crm/communication-integration-future-plan.md`

### RS-CRM-COMMS-001.4 — Make CRM work easier from Finch with guarded AI assistance

- **Project:** ripple-suite + finch-inbox
- **Status:** captured
- **Type:** adjacent
- **Parent:** RS-CRM-COMMS-001
- **End goal:** After the core Ripple CRM journey is complete and stable, authorised staff can work from the Finch conversation with the correct canonical Family, Lead, Request, task, candidate and Tutor Profile context; record one truthful outcome directly to Ripple; share profiles through governed paths; and use AI-assisted chat interpretation where it safely reduces manual work.
- **Why it matters:** Staff is more likely to record an outcome while reading the parent conversation, but an outcome-only shortcut bolted onto matching would start too late. The integration must first solve contact identity, Family/Lead/Request linking, several-Request ambiguity, permissions, command ownership and replay safety. AI may draft or suggest the likely outcome, but customer meaning must not silently become CRM truth until accuracy, confidence, staff confirmation, correction, privacy, multilingual and audit rules are separately proven and approved.
- **Source:** Hafiz CRM matching discussion, 2026-08-14. Hafiz explicitly deferred Finch integration until the core CRM is done and asked to preserve the possibility of AI-based updates from chat.
- **Next action:** Do not include Finch UI implementation in the current CRM matching Build-Ready Pack. After the core CRM is accepted, run a separate full cross-project Product Shape and Build-Ready Pack covering conversation/contact identity; Family, Lead and Request entry; unresolved and multi-Request routing; matching/profile/outcome actions; trusted provider delivery evidence; Ripple command APIs; Finch tenant/RBAC boundaries; idempotency and outage recovery; AI suggestion-versus-automation policy; correction and audit; privacy/retention; rollout; and realistic end-to-end evidence.
- **Promote to:** Separate cross-project PRD, UX, backend/event/AI contract and build prompts, then project-specific GitHub issues after explicit approval
- **Links:** `ripple-suite/docs/features/crm/communication-integration-future-plan.md`, `.agent-os/session-maps/2026-08-14-194707-codex-crm-matching-candidate-design.md`, `RS-CRM-COMMS-001.1`

### RS-CRM-COMMS-001.2 — Track CX Onboarding business-call activity

- **Project:** ripple-suite + future telephony provider
- **Status:** captured
- **Type:** research
- **Parent:** RS-CRM-COMMS-001
- **End goal:** A company telephony/click-to-call integration reports reliable
  CX, Lead, call-state, timestamp, and duration evidence to Ripple while manual
  external calls remain available and clearly labelled.
- **Why it matters:** Personal-device `tel:` calls provide no trustworthy call
  outcome or activity evidence and should not be replaced by invasive personal
  call-log collection.
- **Source:** Hafiz CRM re-review confirmation, 2026-07-19
- **Next action:** Compare business telephony approaches for Malaysian numbers,
  staff devices, inbound/outbound needs, provider events, reliability, security,
  and cost before selecting a provider.
- **Promote to:** Provider research, PRD/backend contract, and GitHub issues
- **Links:** `ripple-suite/docs/features/crm/communication-integration-future-plan.md`

### RS-CRM-COMMS-001.3 — Build transparent CX call-quality coaching

- **Project:** ripple-suite + future telephony provider
- **Status:** paused
- **Type:** task
- **Parent:** RS-CRM-COMMS-001
- **End goal:** Authorised Supervisors can sample calls, use an approved
  scorecard, give auditable coaching, and review fair service metrics without
  treating raw call count or unreviewed AI scoring as quality.
- **Why it matters:** Call evidence can improve onboarding consistency, but
  recording, transcription, retention, access, corrections, and employment use
  need explicit company and privacy governance first.
- **Source:** Hafiz CRM re-review confirmation, 2026-07-19
- **Next action:** Resume only after the telephony direction is known; then
  decide recording/transcription policy, legal/privacy review, scorecard,
  sampling, retention, permissions, and staff transparency.
- **Promote to:** Company policy review, PRD/UX, QA plan, then GitHub issues
- **Links:** `ripple-suite/docs/features/crm/communication-integration-future-plan.md`

### RS-TUTOR-EXPERIENCE-001 — Build the TX-owned tutor lead and onboarding journey

- **Project:** ripple-suite + sifu-tutor + sifututor_tutor
- **Status:** paused
- **Type:** mission
- **Parent:** none
- **End goal:** All tutor leads, including Facebook leads, enter one Tutor
  Experience journey owned by TX Onboarding for duplicate-safe intake,
  registration, profile completion, verification, eligibility, and availability
  before CX Support approaches or selects them for a customer Tutor Request.
- **Why it matters:** Current paths split tutor registration, staff creation,
  local tracking, and verification. Without one owner and one authoritative
  journey, CX Support could create an out-of-system tutor or treat an
  unverified tutor as ready for assignment.
- **Source:** Hafiz CRM re-review correction, 2026-07-19
- **Current CRM boundary:** CX Support may search and approach only tutors who
  already exist in the authoritative tutor system. An existing unverified tutor
  may be considered while TX completes verification. An authorised request
  approver may also grant a logged, request-specific exception that allows the
  tutor to be assigned while the RM100 commitment fee remains unpaid. The
  exception does not make the tutor Verified, does not apply to another
  request, and remains subject to TX follow-up. Tutor lead acquisition,
  invitation, and registration are outside the current CRM scope.
- **Next action:** When prioritised, run separate product discovery covering
  tutor lead sources/imports, TX assignment, duplicate resolution, consent and
  account claiming, Tutor App onboarding, verification, availability,
  failed/expired leads, supervisor monitoring, cross-Request reuse,
  notifications, and comprehensive end-to-end tests.
- **Promote to:** Cross-project PRD / UX / SIMS and Tutor App backend contract /
  build prompts, then GitHub issues
- **Links:** Ripple CRM re-review docs and a future dedicated Session Map

### RS-TUTOR-ACCOUNT-001 — Build the Tutor Account financial ledger

- **Project:** ripple-suite + sifu-tutor
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** The Tutor Account module provides one authoritative debit and
  credit ledger for tutor financial obligations and settlements, including
  partial commitment-fee payments, split deductions across tutor payouts,
  mixed payment sources, reversals, remaining balances, and a complete audit
  trail.
- **Why it matters:** Ripple can currently place manual commitment-fee
  deductions on tutor payment slips, but those deductions are not linked to one
  RM100 obligation. The system therefore cannot safely calculate the remaining
  balance or prevent duplicate and excess deductions. Adding isolated
  commitment-fee automation before the complete Tutor Account module would
  create a second incomplete financial model.
- **Source:** Hafiz tutor-verification and commitment-fee design decision,
  2026-07-25
- **Current boundary:** Keep commitment-fee deductions, cumulative tracking,
  settlement confirmation, verification follow-up, and any correction fully
  manual. Do not add partial balance tracking or automatic closure as an
  isolated change. Introduce those controls only as part of the Tutor Account
  module rollout, following the Customer Account module pattern. SIMS remains
  the authoritative financial system; Ripple owns the staff workflow and
  presentation.
- **Next action:** When prioritised, run a dedicated cross-project product
  design covering ledger ownership, charge and settlement entries, source
  linkage, idempotency, reversals, permissions, migration of historical manual
  deductions, reconciliation, payment-slip presentation, and end-to-end
  evidence.
- **Promote to:** Cross-project PRD / UX / financial contract / migration plan /
  QA plan, then GitHub issues
- **Links:** Tutor commitment-fee design session, 2026-07-25

### RS-REVENUE-001 — Build the governed Ripple Revenue Ledger and QB invoice export

- **Project:** ripple-suite (with read-only SIMS invoice and class data)
- **Status:** done
- **Type:** mission
- **Parent:** none
- **End goal:** Finance has one Ripple Revenue Ledger that reproduces the real
  Transaction Pro invoice workbook, detects source changes and data-quality
  exceptions, creates immutable manual QuickBooks export batches, reconciles
  row-level import results, preserves all historical invoices, and provides
  the complete validated Finance analytics scope—including revenue, cash,
  receivables, adjustments, customer cohorts, profitability, retention, QB
  operations, data quality, DSO, and forecasting—without creating a second
  invoice book.
- **Why it matters:** Staff currently prepare and track the QuickBooks invoice
  import manually. Without a governed ledger, missed invoices, duplicate
  imports, partial failures, silent SIMS changes, and inconsistent revenue
  reporting are difficult to detect or explain.
- **Source:** Hafiz Revenue Ledger and Transaction Pro product-design session,
  2026-08-24 to 2026-08-25
- **Current production state (verified 2026-09-01):** The governed Revenue
  Ledger, bounded Invoice and warning workspaces, two-company historical QB
  reconciliation, normal Transaction Pro export/results workflow, MyInvois
  recording, Core Analytics, Full Finance Analytics and Finance Pack are live.
  Issues #721, #723, #726, #728, #730, #732 and #734 are merged, deployed and
  production-checked. All 28 permanent Revenue browser journeys pass. The final
  authenticated Analytics proof measured Core visible at p75 1.415s and p95
  2.025s, with Advanced Finance completing independently at p75 3.716s and p95
  4.227s. Desktop and 390px phone QA, PM2, Ripple HTTPS, SIMS connectivity and
  monitoring passed. Ripple still performs no automatic QB import or LHDN
  submission.
- **Next action:** Closed. Finance may use the complete normal Revenue workflow.
  Historical review queues remain ordinary Finance operations, and external QB
  imports and LHDN submissions remain authorised staff actions.
- **Promote to:** A new execution-ready GitHub issue that inventories the
  already-deployed slices and covers activation/backfill/reconciliation rather
  than repeating the original readiness work
- **Links:** `ripple-suite/docs/features/revenue/README.md`, Koda
  `mem_92f455b87358`, `mem_33af395a87fb`, `mem_ad374de20f3e`,
  `mem_b765c5647308`, `mem_71db66012e9f`

### RS-REVENUE-001.A1 — Add durable SIMS invoice events after the Ripple-only launch

- **Project:** cross-project (ripple-suite + sifu-tutor)
- **Status:** captured
- **Type:** adjacent
- **Parent:** RS-REVENUE-001
- **End goal:** After the Ripple-only Revenue Ledger is stable, SIMS records
  durable invoice and qualifying-class events through an outbox so Ripple can
  update near real time, while scheduled reconciliation remains as the
  independent recovery path.
- **Why it matters:** The first release deliberately avoids SIMS changes and
  uses read-only incremental polling, nightly reconciliation, and manual
  refresh. A durable source event can later reduce detection delay and polling
  load, but must not replace reconciliation or weaken idempotency.
- **Source:** Hafiz explicit future-SIMS decision during the Revenue Ledger
  product-design session, 2026-08-25
- **Next action:** Keep this outside the first release. After launch, measure
  sync lag, polling load, and missed-change recovery; only then prepare a
  separate cross-project event/outbox contract with retry, replay, ordering,
  versioning, monitoring, and rollback rules.
- **Promote to:** Cross-project PRD/backend event contract and separate Ripple
  and SIMS GitHub issues after explicit approval
- **Links:** `RS-REVENUE-001`

### RS-REVENUE-001.A2 — Complete the full validated Finance analytics scope

- **Project:** ripple-suite
- **Status:** done
- **Type:** adjacent
- **Parent:** RS-REVENUE-001
- **End goal:** Ripple's Finance Command Centre includes the complete governed
  analytics scope: a canonical metric dictionary; revenue, cash collection,
  receivables and aging; adjustments and refunds; customer and cohort analysis;
  profitability and tutor costs; retention; QuickBooks operations; data-quality
  controls; DSO; and forecasting.
- **Why it matters:** A smaller first release must not quietly become the final
  product. Finance decisions are only safe when every reported metric has an
  agreed definition, traceable source, row-level explanation, and reconciliation
  evidence.
- **Source:** Hafiz explicit full-scope decision during the Revenue Ledger
  product-design session, 2026-08-25
- **Result:** Issues #721 and #723 delivered and production-proved the complete
  governed metric dictionary, revenue and cash trends, receivables and aging,
  adjustments, First-versus-Recurring mix, profitability and tutor costs,
  recurring movement, three-complete-month churn, DSO honesty, forecasting,
  drill-down evidence, metric approvals and the private 17-sheet Finance Pack.
  Issues #728 and #734 then bounded the production payloads and made the verified
  Core summary usable before Advanced Finance completes.
- **Next action:** Closed. New metrics or changed Finance definitions require a
  separate governed product decision and regression evidence.
- **Promote to:** The parent Revenue PRD / UX / backend and data contract / QA
  plan, followed by linked implementation issues after Phase B approval
- **Links:** `RS-REVENUE-001`, Koda `mem_5cfff0a6eb4d`,
  `mem_258a1a66105e`, `mem_c3f66c4f6c44`, `mem_e7c8d1d1f3e4`,
  `mem_22ce6ae850b3`, GitHub issues #721, #723, #728 and #734

### RS-REVENUE-001.A3 — Reduce manual handling for large QB exception sets

- **Project:** ripple-suite
- **Status:** paused
- **Type:** adjacent
- **Parent:** RS-REVENUE-001
- **End goal:** Finance can classify and evidence a material set of Failed or
  Not Attempted Transaction Pro rows efficiently without weakening invoice-level
  audit history or accidentally changing successful rows.
- **Why it matters:** The live Issue #851 workflow already bulk-fills one overall
  reference across all successful rows, but staff still handles each exception
  individually. That is appropriate when only a few of 979 rows are exceptions,
  but becomes burdensome if a real batch contains many exceptions.
- **Source:** Finance staff follow-up after Issue #851 production release,
  2026-09-08
- **Next action:** Observe the real exception count from Finance's current batch.
  If it is material, clarify selection, shared reason, mixed-status and review
  safeguards before creating an implementation issue.
- **Promote to:** GitHub issue after product clarification and critical-lane
  approval
- **Links:** `RS-REVENUE-001`, GitHub issue #851, PR #855,
  `.agent-os/session-maps/2026-09-08-012430-codex-qb-results-safety.md`

### RS-INFRA-DISK-001 — Prevent Ripple KVM8 disk exhaustion from recurring

- **Project:** ripple-suite infrastructure
- **Status:** done
- **Type:** mission
- **Parent:** none
- **End goal:** Ripple KVM8 retains enough verified rollback coverage without
  unbounded backup or log growth, and operators receive an alert before free
  space threatens a deployment.
- **Why it matters:** The existing ordinary-backup retention job worked, but
  specially named migration backups, staging configuration snapshots, Creative
  Hub autodeploy snapshots, and PM2 logs remained outside retention. The host
  reached 99% again during a production deployment even after earlier manual
  cleanup.
- **Source:** Whole-host production disk audit and guarded cleanup, 2026-08-28
- **Result:** PR #709 merged as `df41805c`, deployed to KVM8 production, and
  activated with guarded daily retention, PM2 log rotation for both process
  owners, and dedicated 85% warning / 90% critical BetterStack heartbeats.
  Dry-run and apply both selected zero current artifacts, both alert monitors
  passed controlled failure/recovery tests, the real cron daemon ran the guard,
  and all KVM8 services and public sites passed smoke checks.
- **Next action:** Closed. Keep the automated retention and five-minute disk
  checks running; investigate only if BetterStack alerts or the 85% threshold
  are reached.
- **Promote to:** `Sifututor/ripple-suite#708`
- **Links:** `.agent-os/session-maps/2026-08-28-020556-claude-ripple-kvm8-disk-audit.md`,
  Koda `mem_7d92f5314407`, `https://github.com/Sifututor/ripple-suite/issues/708`,
  `https://github.com/Sifututor/ripple-suite/pull/709`

### RS-INFRA-DISK-001.A1 — Recheck post-deploy backup headroom

- **Project:** ripple-suite infrastructure
- **Status:** captured
- **Type:** risk
- **Parent:** RS-INFRA-DISK-001
- **End goal:** A normal Ripple production deploy can create its required fresh
  rollback backup without manual deletion, and automated retention restores
  comfortable headroom afterward.
- **Why it matters:** The #734 deploy initially found 3.9GB free and required
  Hafiz's explicit approval to remove one retention-eligible old backup. The new
  rollback backup later left 3GB free; automated retention subsequently restored
  23GB, but the 387GB host still reports 95% used.
- **Source:** Revenue Analytics production release and Critical Save,
  2026-09-01
- **Next action:** In a separate read-only infrastructure diagnosis, verify the
  retention run and disk-alert evidence, identify the remaining governed backup
  classes consuming space, and recommend a safe target headroom before proposing
  any deletion or policy change.
- **Promote to:** GitHub issue if the read-only diagnosis confirms the current
  guard cannot keep deployment-safe headroom
- **Links:** `RS-INFRA-DISK-001`, Revenue Issue #734 production evidence

### RS-LINT-001 — Decide Biome formatter scope for machine-written JSON

- **Project:** ripple-suite
- **Status:** captured
- **Type:** adjacent
- **Parent:** RS-RELEASE-001
- **End goal:** `npx @biomejs/biome ci .` stays green on `main` after hooks
  rewrite `.claude/tasks/*.json` or audit runs add `docs/audits/artifacts/*.json`.
- **Why it matters:** The #817 cleanup formatted 22 machine-written JSON files
  because `biome.json` excludes `.claude/**` from the linter but not the
  formatter. The next task-router or hook write will turn the baseline red
  again, hiding new findings in noise.
- **Source:** Ripple lint baseline cleanup, GitHub issue #817, 2026-09-06
- **Next action:** After Codex reviews the #817 branch, Hafiz decides whether
  to exclude `.claude/**` and `docs/audits/artifacts/**` from the Biome
  formatter (mirroring the linter and ESLint ignores) or keep formatting them
  and teach the JSON writers to emit Biome style. Also decide who owns the
  pre-existing failing `workforce-access-prod-release.test.ts` on `main`.
- **Promote to:** GitHub issue once Hafiz picks a direction
- **Links:** `RS-RELEASE-001`, ripple-suite issue #817 and its handback comment, Koda
  mem_f9ee5b8f6834

### RS-TOB-001 — Integrate and activate the V7-7 Tutor module, Tutor Onboarding CRM and V8-4 early cancellation

- **Project:** ripple-suite
- **Status:** promoted
- **Type:** mission
- **Parent:** none
- **End goal:** The Claude lane's eight local commits on `fix/839-v7-v8-tutor-workflows` (#839, #840, #841) are integrated by Codex, pushed, reviewed, migrated (151 to 154 with rollbacks) and activated: Tutor Onboarding switched on for the Tutor Experience team, then the early Parent cancellation capability flag turned on after the SIMS pilot.
- **Why it matters:** Tutor Details, the full-population verification queue, the onboarding CRM and the governed cancellation are complete and proven locally but invisible to anyone else until pushed; every switch ships off, so nothing reaches staff without a deliberate activation.
- **Source:** Claude delegation lane 2026-09-07, `.agent-os/delegations/v7-v8-claude-run-2026-09-07/handback.md`
- **Next action:** Follow the Session Release Ledger and activation handback for current release/monitoring state; do not repeat the original integration or request the same activation approval again.
- **Do not do yet:** Do not turn on `crm.request_early_cancellation` before the paired SIMS admission switch and permission grant migration are live; do not run the v1.25.0 release seed until migration 151 exists in production.
- **Promote to:** [Ripple PR #863](https://github.com/Sifututor/ripple-suite/pull/863) and [SIMS PR #2495](https://github.com/Sifututor/sifu-tutor/pull/2495); activation handback `.agent-os/delegations/v7-v8-claude-run-2026-09-07/activation-production-handback.md`
- **Links:** ripple-suite #839 #840 #841, sifu-tutor #2451 #2452, handback `.agent-os/delegations/v7-v8-claude-run-2026-09-07/handback.md`, Koda mem_36ed2b714f78, mem_109c55f90864, mem_0970da00b57f

### RS-TOB-001.A1 — Close the honest test gaps the second review named

- **Project:** ripple-suite
- **Status:** captured
- **Type:** adjacent
- **Parent:** RS-TOB-001
- **End goal:** `confirmImport` is exercised against the disposable PostgreSQL harness, and the cancellation `expected_version` deviation (always 0) is either accepted in the contract or replaced with a read of the SIMS lifecycle version.
- **Why it matters:** The CSV confirm path is proven only by mocked-API browser tests and unit tests; the reviewer showed how mocked SQL hid a real CHECK violation once already.
- **Source:** `evidence/independent-review-840-841-2452.md` in the delegation run folder
- **Next action:** Add a `confirmImport` case to `prospects.db.test.ts` on the next touch of the module; decide the version question during PR review.
- **Promote to:** part of the #840/#841 PR review checklist
- **Links:** `RS-TOB-001`
