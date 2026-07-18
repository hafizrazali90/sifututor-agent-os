# Kelasapp Mission Ledger

Use this for Kelasapp missions, child tasks, adjacent ideas, and paused
follow-ups.

## Missions

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
