# LLS Backend Mission Ledger

Use this for Learnest backend missions, child tasks, adjacent ideas, and paused
follow-ups.

## Missions

### LLS-SIMS-LIFECYCLE-001 — Reliable SIMS Student Account Lifecycle

- **Project:** lls
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** Learnest students linked through SIMS can keep their identity, Premium entitlement, account recovery, and login lifecycle reliable after initial registration.
- **Why it matters:** Secure SIMS registration is live, but longer-term entitlement refresh, Student UID password recovery, legacy endpoint retirement, and post-release rollback retirement should be designed deliberately rather than folded into the completed launch.
- **Source:** Learnest SIMS identity-linking production release session, 2026-07-17.
- **Next action:** Complete the post-release watch first, then prioritize the lifecycle child tasks based on real support evidence and product need.
- **Promote to:** PRD
- **Links:** `lls/docs/features/sims-student-identity-linking/`, Session Map `.agent-os/session-maps/2026-07-16-000644-codex-learnest-sims-identity-linking.md`, SIMS issue `#1711`, Learnest backend issue `#108`, Learnest frontend issue `#5`, Koda `mem_2ae654c32812`

### LLS-SIMS-LIFECYCLE-001.1 — Complete Production Watch And Retire Rollback Files

- **Project:** lls
- **Status:** captured
- **Type:** task
- **Parent:** LLS-SIMS-LIFECYCLE-001
- **End goal:** The release completes its longer monitoring watch and retained production database/config rollback files are removed safely after the watch period.
- **Why it matters:** Initial monitoring passed, but temporary rollback artifacts should not remain on production servers indefinitely, especially cached configuration copies that contain sensitive runtime values.
- **Source:** Learnest SIMS identity-linking production release session, 2026-07-17.
- **Next action:** Run the scheduled three-hour and 48-hour health checks; if clean, obtain the normal production-write approval and delete only the named retained rollback files.
- **Promote to:** none yet
- **Links:** Session Map `.agent-os/session-maps/2026-07-16-000644-codex-learnest-sims-identity-linking.md`, Koda `mem_2ae654c32812`

### LLS-SIMS-LIFECYCLE-001.2 — Revalidate SIMS Premium Entitlement

- **Project:** lls
- **Status:** captured
- **Type:** task
- **Parent:** LLS-SIMS-LIFECYCLE-001
- **End goal:** Learnest can safely refresh whether a SIMS-linked student should retain Premium access without weakening existing login availability.
- **Why it matters:** Initial linking grants Premium correctly, but future status changes in SIMS need an explicit lifecycle contract instead of permanent entitlement assumptions.
- **Source:** Parked lifecycle slice from the Learnest SIMS identity-linking session, 2026-07-17.
- **Next action:** Design the refresh trigger, authoritative SIMS fields, grace period, outage behavior, idempotency, audit trail, and effect on existing Student UID login before implementation.
- **Promote to:** PRD
- **Links:** `lls/docs/features/sims-student-identity-linking/`

### LLS-SIMS-LIFECYCLE-001.3 — Student UID Password Recovery

- **Project:** lls
- **Status:** captured
- **Type:** task
- **Parent:** LLS-SIMS-LIFECYCLE-001
- **End goal:** A SIMS-linked student without a real email address can recover their Learnest password through a secure, supportable identity-proof flow.
- **Why it matters:** UID/password login works after registration, but placeholder-email accounts cannot rely on ordinary email password reset.
- **Source:** Parked lifecycle slice from the Learnest SIMS identity-linking session, 2026-07-17.
- **Next action:** Product-design a recovery flow that reuses SIMS-owned identity proof or an approved support process without enabling Student UID enumeration or account takeover.
- **Promote to:** PRD
- **Links:** `lls/docs/features/sims-student-identity-linking/`

### LLS-SIMS-LIFECYCLE-001.4 — Retire Legacy Public SIMS Verification

- **Project:** lls
- **Status:** captured
- **Type:** research
- **Parent:** LLS-SIMS-LIFECYCLE-001
- **End goal:** Old public UID-verification routes are removed only after every legitimate consumer has migrated to the authenticated challenge API.
- **Why it matters:** Keeping the legacy lookup indefinitely preserves unnecessary identity exposure, but removing it without a consumer audit could break older clients.
- **Source:** Parked rollout follow-up from the Learnest SIMS identity-linking session, 2026-07-17.
- **Next action:** Run a read-only route/consumer/log audit across SIMS, Learnest, and mobile clients; then promote an exact deprecation plan to GitHub.
- **Promote to:** GitHub issue
- **Links:** `lls/docs/features/sims-student-identity-linking/`, SIMS issue `#1711`
