# Kelasapp Mission Ledger

Use this for Kelasapp missions, child tasks, adjacent ideas, and paused
follow-ups.

## Missions

### KELAS-DEV-001 — Pilot Jivan's repeatable PR and release-learning workflow

- **Project:** kelas
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** Jivan consistently prepares Kelasapp PRs from a clean Node 24
  environment with scoped, accessible evidence; permanent E2E for visible
  journeys; negative-case and critical-lane checks; and an honest stop at
  `PR opened with evidence`. Every deployed staff-built release ends with one
  constructive learning message covering what shipped, what review corrected,
  why it mattered, the exact habit to adopt, and the developer's independent
  verification.
- **Why it matters:** The five-PR review found that green local checks did not
  initially prove clean installation, duplicate-enrolment/double-billing
  safety, failed-job retry, archived-parent access revocation, independent
  stacked-PR migrations, or current browser journeys. A repeatable feedback
  loop should turn those release corrections into better future submissions
  instead of one-off reminders.
- **Source:** Kelasapp five-PR release and developer-feedback closeout,
  2026-07-24
- **Next action:** Hafiz sends the curated integrated feedback message; Jivan
  reviews final `main`, reports what he learned and his updated PR checklist,
  then pilots the workflow on one low-risk Kelas issue. Keep Jivan scoped as
  Developer staff - builder for Kelas only: no production, deploy, secrets,
  Koda write, or critical-lane implementation authority by default.
- **Promote to:** A concrete GitHub issue only when the next low-risk Kelas
  implementation task is selected
- **Links:** Session Map
  `.agent-os/session-maps/2026-07-22-143659-codex-kelas-five-pr-review.md`;
  Koda `mem_744b59abffe5`

### KELAS-DEPLOY-001 — Restore scoped unattended GitHub fetch for Kelasapp

- **Project:** kelas
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** The production deploy webhook can fetch the exact approved
  `main` commit using a narrowly scoped GitHub credential without relying on a
  broad personal token.
- **Why it matters:** The webhook and deploy helper target `main`, but the
  existing server key is not accepted and organization policy disables
  repository deploy keys. Production releases currently require the verified
  Git-bundle fallback over the approved SSH lane.
- **Source:** Kelasapp email-verification outage closeout, 2026-07-13
- **Next action:** Provision a repository-scoped GitHub App or dedicated
  machine-account credential, verify unattended fetch without exposing the
  credential, then run a non-production webhook rehearsal before relying on it
  for production releases.
- **Promote to:** GitHub issue when Hafiz schedules deployment automation work
- **Links:** Kelasapp issue `Learnest-Lab/kelasapp#34`, PR
  `Learnest-Lab/kelasapp#35`

### KELAS-SEC-001 — Remove the residual nested-Sharp mitigation safely

- **Project:** kelas
- **Status:** paused
- **Type:** mission
- **Parent:** none
- **End goal:** Kelasapp keeps zero critical production advisories and moves
  from the current runtime mitigation to a stable Next.js release whose private
  Sharp dependency is fixed, without introducing a forced override or breaking
  normal images.
- **Why it matters:** PR #58 removed all four critical advisories and disabled
  the unused Next Image Optimization API, but stable Next.js still installs a
  private vulnerable `sharp@0.34.5`. The package remains on disk and visible in
  the five-warning production audit even though its relevant runtime route is
  disabled.
- **Source:** Kelasapp dependency-security issue #57 / PR #58 production
  closeout, 2026-07-28
- **Next action:** Watch stable Next.js security releases. When stable Next
  bundles fixed Sharp, open a narrow GitHub issue to upgrade, re-run full and
  production-only audits, retain or deliberately reconsider
  `images.unoptimized`, and prove normal images plus `/_next/image` behavior in
  staging before production. Revisit the other four production audit packages
  only when non-breaking fixes exist or their exposure changes.
- **Promote to:** GitHub issue when a stable upstream fix exists or a new
  advisory changes the current risk
- **Links:** Kelasapp issue `Learnest-Lab/kelasapp#57`, PR
  `Learnest-Lab/kelasapp#58`; Koda `mem_123c796943ba`,
  `mem_0b52ca0fac63`

### KELAS-AUDIT-001 — Proper app-wide audit logging after MVP

- **Project:** kelas
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** Kelasapp has a consistent audit logging layer across sensitive
  workflows so operators and support can answer who changed what, when, why,
  and what the previous state was.
- **Why it matters:** Kelasapp handles student data, guardian contacts,
  invoices, receipts, teacher payouts, roles, and tenant boundaries. The MVP
  should stay focused, but after MVP the app needs a proper audit trail instead
  of one-off logs hidden inside individual features.
- **Source:** Hafiz request during Kelasapp audit follow-up, 2026-07-05
- **Next action:** After MVP, create a product/design brief that defines audit
  event coverage, storage model, redaction rules, viewer permissions, retention,
  export needs, and LLM-debuggable trace context before opening engineering
  implementation issues.
- **Promote to:** PRD / GitHub issues after MVP
- **Links:** Session Map `.agent-os/session-maps/2026-07-05-140038-codex-kelas-audit-followup.md`
