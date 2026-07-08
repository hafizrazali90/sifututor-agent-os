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
