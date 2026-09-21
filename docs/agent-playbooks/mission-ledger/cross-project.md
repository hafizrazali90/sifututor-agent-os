# Cross-Project Mission Ledger

Use this for Agent OS, shared workflow, infrastructure, or product-system tasks
that span more than one project.

## Missions

### AO-LEDGER-001 — Make follow-up work visible across sessions

- **Project:** cross-project
- **Status:** active
- **Type:** mission
- **Parent:** none
- **End goal:** Agents can see bigger goals, child tasks, adjacent ideas, and
  paused decisions without relying only on chat or memory.
- **Why it matters:** Hafiz should not lose important follow-up tasks when a
  Codex or Claude session closes.
- **Source:** Hafiz request, 2026-06-12
- **Next action:** Use this ledger during the next `$save-session` and refine
  the workflow if anything feels awkward.
- **Promote to:** GitHub issue or Plane card if this becomes an implementation
  project beyond docs.
- **Links:** [mission-ledger playbook](../../agent-playbooks/mission-ledger.md)

### AO-LEDGER-001.1 — Wire Mission Ledger into Agent OS playbooks

- **Project:** cross-project
- **Status:** triaged
- **Type:** task
- **Parent:** AO-LEDGER-001
- **End goal:** `$task-router` and `$save-session` both check the Mission
  Ledger at the right time.
- **Why it matters:** A ledger only works if agents remember to use it.
- **Source:** Hafiz request, 2026-06-12
- **Next action:** Keep the playbook references current as the workflow evolves.
- **Promote to:** none yet
- **Links:** [task-router](../../agent-playbooks/task-router.md),
  [save-session](../../agent-playbooks/save-session.md)

### AO-LEDGER-001.2 — Add Session Map for live conversation tracking

- **Project:** cross-project
- **Status:** active
- **Type:** task
- **Parent:** AO-LEDGER-001
- **End goal:** Agents can maintain a lightweight live map of the current
  session so Hafiz can see the main goal, current focus, side paths, decisions,
  and return path without rereading the chat.
- **Why it matters:** Long Agent OS and development sessions often start with
  one goal, branch into side problems, then need to return to the original
  problem. Without a live map, both Hafiz and the agent can lose the story.
- **Source:** Hafiz request, 2026-06-28
- **Current state:** Session Map playbook, template, validator, HTML dashboard,
  auto-open habit, lifecycle trigger, close-state model, and dashboard v2
  structure exist locally for review.
- **Next action:** Use the Session Map in this Agent OS build session and
  review the dashboard v2 first-screen scan, Progress Flow, Decision Board,
  Side Paths, Evidence / Checks, Reference Pack, and Continuation Prompt.
- **Promote to:** Keep as Agent OS playbook/template; promote dashboard changes
  into reusable tooling when the design stabilizes.
- **Links:** [session map playbook](../../agent-playbooks/session-map.md),
  [session map template](../../agent-playbooks/templates/session-map.md)

### AO-LEDGER-001.3 — Add recipient-specific release close-out handoffs

- **Project:** cross-project
- **Status:** done
- **Type:** task
- **Parent:** AO-LEDGER-001
- **End goal:** Every reviewed, improved, merged, or deployed PR closes with a
  copy-ready message for each relevant audience without making Hafiz reconstruct
  the technical story himself.
- **Why it matters:** Staff need a short operational explanation, while the
  developer needs one integrated continuation of their PR that explains what
  review changed, why it changed, what their submission missed, what final
  evidence passed, and what they must independently verify and teach their AI
  workflow.
- **Source:** Hafiz correction during PR #1751 close-out, 2026-07-21
- **Next action:** Use the rule in the next reviewed or improved PR close-out
  and refine it only if real-session evidence shows another repeatable gap.
- **Promote to:** GitHub issue #23; implemented in the shared Agent OS contract,
  communication/review/release playbooks, and executable response fixtures
- **Links:** [issue #23](https://github.com/hafizrazali90/sifututor-agent-os/issues/23),
  [PR #1751](https://github.com/Sifututor/sifu-tutor/pull/1751),
  [communication owner](../../agent-playbooks/agent-os-communication.md),
  [review playbook](../../agent-playbooks/review.md),
  `scripts/agent-checks/agent-os-response-shape-runner.py`, Koda
  `mem_2421d7aecd53`

### AO-DELEGATION-001 — Operationalize Codex-to-Claude Max delegation

- **Project:** cross-project
- **Status:** done
- **Type:** mission
- **Parent:** none
- **End goal:** Codex can delegate repository-heavy implementation, testing,
  QA, review, and approved release work to Claude Max to reduce Codex usage,
  while preserving or improving quality, approval safety, visibility, and
  independent verification.
- **Why it matters:** Hafiz has an available Claude Max subscription and wants
  to use it efficiently without allowing background work to stop silently or
  lowering product/release confidence.
- **Source:** Hafiz correction and approval, 2026-07-21. Parent CF #1768,
  Ripple Luna #201, referral #1718, and the Billing Guide supplemental pilot
  supplied the implementation evidence.
- **Current state:** The smallest implementation packet is complete through
  GitHub issue #25 and merged PR #26 at `7adfa8f`. The existing
  handoff/autonomous/runtime owners define the contract; the runner proves
  Claude Max auth, safe ignored runtime paths, worktree ownership, and
  metadata-only evidence; nine deterministic worker fixtures pass; the real
  local Max preflight passes; and the full Agent OS validation reaches 254/254.
  Independent Codex review and all normal approval gates remain part of the
  workflow. Quantitative net Codex savings remain unavailable and must not be
  estimated.
- **Next action:** None required. Tune thresholds or reporting only when future
  real pilots provide evidence that a change is needed.
- **Do not do yet:** Do not add automatic merge/deploy, a new skill/blocking
  hook, or Luna product follow-ups without a separate issue and approval.
- **Promote to:** Promoted to umbrella GitHub issue #25 on 2026-07-22.
- **Links:** `.agent-os/session-maps/2026-07-21-225940-codex-claude-three-pilot-reconciliation.md`,
  Koda `mem_61f13ce52269`, Koda `mem_5dd96ba87cf4`,
  https://github.com/hafizrazali90/sifututor-agent-os/issues/25,
  https://github.com/hafizrazali90/sifututor-agent-os/pull/26

### FINCH-SIMS-001 — Selective Finch↔SIMS integration for Sifu Edu tenant only

- **Project:** cross-project (finch-inbox + ripple-suite + sifu-tutor)
- **Status:** triaged
- **Type:** mission
- **Parent:** none
- **End goal:** New Finch features (starting with a document feature) link to
  SIMS data ONLY for the internal "Sifu Edu" tenant (company_guid
  F4B3221C-C1E1-4D69-B35E-28D9B6ABC549); every other Finch tenant gets the
  same feature standalone, no SIMS awareness. Maximizes staff automation and
  experience for the internal org without leaking the linkage to external
  paying customers.
- **Why it matters:** Finch is becoming a real multi-tenant SaaS; SIMS is the
  single source of truth for the tutoring business. Getting the tenant-gating
  and cross-system integration boundary right prevents both a security/PII
  leak risk (external tenants seeing internal wiring) and a maintainability
  trap (SIMS-specific logic scattered through Finch's general product code).
- **Source:** Hafiz request, 2026-07-18
- **Current state:** Full architecture analysis complete, refined through two
  follow-up verification passes per Hafiz's questions. Findings: (1) Finch's
  `documents/` feature is NOT a general document system — it's a live
  payment-receipt reconciliation triage tool (36,893 chat media messages,
  3,294 approved bank-transfer/e-wallet receipts for tuition fees); overlap
  with SIMS is narrow (payment-proof only — no tutor/staff HR paperwork
  analogue exists on the Finch side). (2) Routing should go through
  ripple-suite, not a new SIMS-facing API — ripple already has read-only SIMS
  MySQL access, a write-back-via-SIMS-API precedent, existing document/
  attachment infra, and a bearer-token pattern for external callers; this
  avoids giving SIMS a second external consumer to trust. Recommended shape:
  new `sims_linkage_enabled` EntitlementFlag on Finch gates a
  `SimsIntegrationService` adapter that calls a new bearer-token route on
  ripple-suite; ripple looks up/confirms/marks the matching SIMS invoice.
  Full writeup: [ANALYSIS.md](../../products/finch-sims-integration/ANALYSIS.md).
- **Next action:** Hafiz gave the concrete end-to-end spec (2026-07-18): staff
  approve a Finch receipt with confirmed details → syncs to ripple's
  `customer_receipts`/`collection_receipts` → updates the collection
  worklist/my-queue accordingly. Full flow designed against ripple's actual
  (already-built) receipt/collection/reconciliation pipeline in
  ANALYSIS.md §11 — reuses the existing manual-upload transaction via a new
  bearer-token-gated `/api/finch/collection-receipts` endpoint, keeps the
  existing bank-match → manual-SIMS-sync guardrail intact (a Finch approval
  alone should never auto-mark a SIMS invoice paid), and lists concrete field
  gaps to close (Finch needs a Receipt Date field + Brand dropdown; ripple's
  schema needs a source_channel/external_approver_name slot since every
  existing receipt route assumes a real Ripple staff user id). One scope flag:
  ripple's collection worklist has no NN-brand support yet (§11.5) — confirm
  brand scope before build. Also corrected a wrong prior Koda memory
  (mem_5c8e3552bd4b) that fabricated a "Nenji Finance Collection channel"
  legacy-migration source — see ANALYSIS.md §13.
  **Scope decisions locked 2026-07-18** (ANALYSIS.md §12.1): ST-brand
  receipts only for this build (NN worklist support is separate future work);
  the SIMS-sync guardrail is kept exactly as-is (Finch approval never
  auto-marks SIMS invoices paid — bank-match + explicit human sync stays
  required). Analysis is now complete and ready for implementation planning.
- **Next action (revised):** Break into GitHub issues (finch-inbox: entitlement
  flag + RippleIntegrationService adapter + receipt-approval UI changes;
  ripple-suite: new bearer-token `/api/finch/collection-receipts` endpoint +
  schema additions for source_channel/external_approver_name) whenever Hafiz
  wants to proceed to build. Remaining non-blocking opens: the separately
  planned "WhatsApp via Finch" notification channel relationship; other
  future Finch features to validate the entitlement/adapter pattern against.
- **Promote to:** GitHub issue in finch-inbox (Finch dev, Helmi, implements
  independently) + direct implementation in ripple-suite/SIMS by Hafiz's own
  sessions (no separate dev handoff needed there — no SIMS code changes
  expected, ripple-suite gets the new endpoint + schema migration).
- **Links:** [ANALYSIS.md](../../products/finch-sims-integration/ANALYSIS.md)

### AO-RUNTIME-001 — Evaluate Omnigent as staff-distributable Agent OS runtime

- **Project:** cross-project
- **Status:** paused
- **Type:** mission
- **Parent:** none
- **End goal:** Decide whether Omnigent (Databricks open-source meta-harness)
  becomes the installable, updatable, platform-agnostic runtime that carries
  the Agent OS workflow for Hafiz and staff, replacing per-machine
  harness-specific setups.
- **Why it matters:** Hafiz wants one chat-first program anyone can install
  that follows his workflow and connects to any LLM. Omnigent is the only
  existing tool combining harness-agnosticism, server-enforced policies
  (gates staff cannot bypass), and web/phone access, but it is alpha and the
  gate-compatibility question is unproven.
- **Source:** Hafiz request, 2026-07-13 (Omnigent research session)
- **Next action:** When Hafiz gives the go: 2-week pilot — self-host the
  Omnigent server on a KVM, connect Koda via MCP, encode ONE route (bugfix,
  with gates) as a YAML agent + policy, run the mandatory gate-compatibility
  test, verify Claude/Codex subscription auth, then give two staff one real
  QA task each. Control comparison: same route in Goose desktop (stable
  fallback); OpenCode as the decentralized alternative.
- **Promote to:** GitHub issue in the umbrella repo when the pilot starts;
  feeds the public llm-agent-os brief's research comparison either way.
- **Links:** [omnigent repo](https://github.com/omnigent-ai/omnigent),
  Koda mem_227cab004cef (research), mem_750a3a6858f6 (tooling vision),
  mem_a91d4eed0f1d (advisory lesson)

### JEV-EVAL-001 — Evaluate TypeSafe's Jev as a typed-decision layer across Finch/Ripple/SIMS

- **Project:** cross-project
- **Status:** paused
- **Type:** mission
- **Parent:** none
- **End goal:** Decide whether to pilot Jev (TypeSafe AI's non-LLM "System One
  Model" — typed Choice/Score/Noul answers, 70-500ms, near-zero cost, claims
  calibrated confidence) as a cheap fast-decision layer, and if so, in which
  product first.
- **Why it matters:** Three concrete, code-grounded opportunities exist:
  finch-inbox Helpdesk-number message triage (fast routing call + background
  sentiment/urgency job), ripple-suite's two already-hand-rolled "zero-LLM"
  Luna classifiers (intent-classifier.ts, luna-router.ts) plus the manual
  tutor-WhatsApp-reply "positive_response" step, and sifu-tutor's
  never-built 7-factor ProfileStrengthService. None of these are urgent;
  none should be built until Jev's calibration claims are checked against
  real Sifututor data, since Jev launched 2026-09-15 (5 days old at research
  time) and is gated behind an early-access waitlist.
- **Source:** Hafiz request, 2026-09-20 (Jev research + Finch/Ripple/SIMS deep
  analysis session)
- **Current state:** Research complete. Four reference artifacts published
  (Jev end-to-end explainer, Jev x Finch, Jev x Ripple, Jev x SIMS), each with
  a ranked list of integration points and an explicit recommended starting
  point per product. See Koda fact memory (tags: finch-inbox, ripple-suite,
  sifu-tutor, jev, typesafe-ai) for the full grounded findings.
- **Next action:** When Hafiz decides to move: (1) get off the TypeSafe
  waitlist, (2) start with finch-inbox's background sentiment/urgency job
  (lowest risk, mirrors the existing document-ai job pattern, cannot break
  current routing) OR ripple-suite's shadow-test against
  intent-classifier.ts (reuses Ripple's existing shadow-mode safety pattern).
  Do not start with sifu-tutor's TutorMatchingService or any tutor-matching
  scoring signal in ripple-suite — both are explicitly flagged don't-build /
  not-yet in the research.
- **Promote to:** GitHub issue in whichever project Hafiz picks to pilot
  first, once he decides to proceed.
- **Links:** Koda fact memory (jev/typesafe-ai research, stored 2026-09-20).

### JEV-EVAL-001.A1 — Finch has no database access lane in the agent access map

- **Project:** cross-project
- **Status:** triaged
- **Type:** adjacent
- **Parent:** JEV-EVAL-001
- **End goal:** Add a `finch-database-readonly` lane to
  `docs/agent-playbooks/agent-access-map.md` so Claude/Codex can verify
  Finch's real tenant/routing/schema state directly instead of asking Hafiz
  or guessing from migration files.
- **Why it matters:** Discovered mid-session when a question about how
  Finch's four WhatsApp numbers route to teams couldn't be verified against
  real data — the access map has read-only DB lanes for SIMS and LLS but
  none for Finch, and the local Docker MSSQL container present on this
  machine is stale/unrelated test data, not real tenant config. Every other
  DB-shaped question about Finch will hit the same wall until this exists.
- **Source:** Discovered during JEV-EVAL-001 research, 2026-09-20.
- **Next action:** Hafiz decides whether to add this lane (owner, credential
  scope, read-only tier) the same way SIMS/LLS already have one.
- **Promote to:** GitHub issue or direct edit to agent-access-map.md whenever
  Hafiz wants to close this gap.
- **Links:** none yet.

### SIMSOA-PROBATION-001 — sims-owner-analytics probation and alerting follow-up

- **Project:** sims-owner-analytics
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** Formally close the reliability probation on the nightly
  refresh timer so a single future failure alerts and lets the next
  scheduled cycle retry on its own, instead of disabling the timer and
  waiting for a human to notice, as happened for eighteen days after the
  2026-09-02 failure. Separately, confirm the operator actually receives
  the monitoring alert this system sends on failure.
- **Why it matters:** The nightly refresh failed once on 2026-09-02 and sat
  disabled for eighteen days with stale owner-facing analytics data before
  anyone checked. The exact original crash cause is unrecoverable now (log
  retention had already rotated past it), but two systemic gaps let it go
  unnoticed this long: the probation mode's own over-cautious auto-disable
  behavior, a deliberate but supposed-to-be-temporary safety net still
  active over a month after this system first deployed, and no confirmed
  human-reachable alert path.
- **Source:** Diagnosed and resolved (resumed the timer, deployed better
  failure diagnostics) during the 2026-09-20/21 session. This entry is only
  for the two things that session did not close.
- **Update 2026-09-21:** The resumed timer failed again on its first real
  attempt, a genuinely different and real cause this time, a production
  column type no longer matches what the extraction registry expects for
  one specific table. Data is unaffected. Could not identify which table
  from the logs, so a follow-up fix now logs table and dataset on any
  fatal per-table failure, deployed live. Timer is re-enabled again; the
  next scheduled cycle will either succeed or, for the first time, name
  the exact table that needs its schema reconciled.
- **Next action:** Check whether the next scheduled cycle (2026-09-22 around
  02:14 MYT) succeeded or failed. If it failed, the log will now name the
  exact table and dataset involved, use that to reconcile the schema
  difference between production and the extraction registry. Separately,
  confirm the failure alert from the original 2026-09-02 incident was
  actually received, and decide whether to accept reliability probation
  now, or leave it on.
- **Promote to:** GitHub issue in sims-owner-analytics once the drifted
  table is identified, or once a decision is made on formally closing
  probation.
- **Links:** GitHub issues 69, 70, 72, 73 (closed/merged, original
  incident), 74, 75, 76, 78, 80 (closed/merged, table-logging fix and its
  deploy script corrections), 71, 77, 79 (closed, drift and correction
  follow-ups filed along the way).
