# Cross-Project Mission Ledger

Use this for Agent OS, shared workflow, infrastructure, or product-system tasks
that span more than one project.

## Missions

### AI-CLASSROOM-001 — AI Classroom teacher app proposal to Perbadanan Kota Buku

- **Storage/filing update, 2026-09-08:** Hafiz approved private storage in Learnest-Lab/papertrail and the team filing convention. PRs #1/#2 adopted guides and the preserved Kota Buku package; PR #4 added the structure checker plus TEKUN, Sifututor Ecosystem and KESUMA references, merged at `b0c34f5b31e78a6f8ea99210ffba126da533f08f`. Fresh main clone verified 623 preserved files; 12 checker tests passed. This completes repository filing, not the proposal mission or external-release approval. Current filing instructions are Papertrail README.md/STRUCTURE.md; older local-only storage notes below are historical. Save record: `.agent-os/session-maps/2026-09-08-122047-codex-papertrail-closeout.md`. No new required follow-up; optional enforcement/build work remains in Papertrail TEAM-SETUP.md.
- **Project:** cross-project (new concept; draws on `kelas` and `lls` engineering patterns only, no home project yet)
- **Status:** active
- **Type:** mission
- **Parent:** none
- **End goal:** A credible, evidence-backed proposal to Perbadanan Kota Buku positioning the Kota Buku app, powered by Learnest Lab, as the complete software solution (device + application + content) occupying the "Kota Buku Application" slot in redONE Mobile's Teacher Digital Empowerment Programme (iPad + 300GB data + insurance + app for up to 182,757 KPM teachers, pending MCMC USP Fund approval). Scope: teacher-centric native iPadOS app, Standard 1 to Form 5, covering student data collection, class conduct tools, AI content generation, AI teaching-assistant personalization, adjacent efficiency features, and a separate parent/student access surface.
- **Why it matters:** Inbound opportunity — Kota Buku contacted Sifututor asking what should be built. The 06/09/2026 research suggests value beyond its reader, but sparse app ratings do not establish usage, no AI feature found is not proof of absence, and no procurement example found is not proof of a closed route. The inbound creates a conversation, not an approval.
- **Source:** Hafiz, 2026-09-06 session; redONE deck at `~/Downloads/Teacher-Digital-Empowerment-Programme.pptx` (USP Fund proposal, Aug 2026).
- **Current state:** 06/09/2026, second pass complete. Hafiz's partner (Faiz Samion, CSO) shared a commercial pack, "SEPADU v1.0 Founder Briefing" (figures live only in that pack, D10). Filed verbatim at `docs/ai-classroom-concept/partner/SEPADU-v1.0-Founder-Briefing.md`; Claude's verification and reconciliation at `partner/SEPADU-review.md` (arithmetic reconciles; RPM quotes verbatim; MySG hours, Korea cause, three population figures and the AWS residency claim need correction; RPH-generator claim withdrawn; new regulatory findings on Act 854, government procurement law, contract norms, service tax, AI governance). Codex applied review §10 to all five masters the same day (handoff §13 "Second-pass SEPADU reconciliation") with corrections to the review that stay recorded there, not in the read-only review file: the procurement statute is the **Government Procurement Act 2026 (Act 882)**, and its s.35 covers unapproved transfer, assignment and novation, not a blanket subcontracting offence; the RPM 80:20 passage is printed page 179; the early LKAN report-year (2013 Series 3 published 2014 vs 2014) stays unresolved; teachers-only devices keep the separate parent and pupil web access; the full-RPH guided beta stays at launch. Earlier the same day: first Codex review pass including a separate read-only governance critique. Corrected decision/tier drift, evidence overreach, hardware terminology, consent law, data/measurement claims and source references. All seven original decisions stand; decisions 1 and 5 carry Hafiz-authorised wording refinements (D9 delivery-versus-technology brand, D10 partner-owned figures) recorded in handoff §7, and D8 to D10 are appended there. Level 1 is general at launch; Level 2 full RPH is a guided pilot beta on the same backend, not deferred. Reading artifacts could not be opened; no artifact parity/visual check or publication claimed. Ranked findings, unresolved evidence and full change log: `docs/ai-classroom-concept/CODEX-HANDOFF.md` §13.
- **Current state, 07/09/2026 (deck):** the five reading-version artifacts were republished from the corrected masters (same URLs; handoff §13 list). Codex then produced the document direction, the twelve-beat reading draft (`production/deck-reading-draft.md`), deck research and the first visual samples; Hafiz corrected the samples (one language at a time with a switcher, no heavy bezel, Apple-style pacing) and reviewed Claude's independent three-slide sample point by point. On his instruction Claude built the full deck on autopilot: `production/visual-samples/claude/kota-buku-deck.html` (sixteen slides, English / BM switcher, live demos, "i" context cards, persistent honesty line, launch boundary where relevant), a partner share copy, English and BM PDFs, generated supporting images, screenshots and a README with the decisions, checks and the adversarial-review change log (3 blocking, 9 material and 19 minor findings; all blocking and material fixed). Recorded in handoff §13 "Claude full deck built from the reading draft" and Koda `mem_c567806edfa4`. Local-only; nothing published, committed or sent. Hafiz also reviewed the partner's SEPADU proposal framework (Codex intake record in handoff §13).
- **Update, 07/09/2026 (later):** Hafiz reviewed the first build against Codex's sequence and directed, one point at a time: Codex's grey ground and light chrome, the cover in Codex's opening style, an analytics and assistant story (missing from the reading draft; sourced from the feature spec pillars 4 and 5), and a slimmer fourteen-slide deck with real hierarchy on every non-sample slide. Rebuilt the same day; checks clean. Open decision recorded in handoff §13: the AI analysis and assistant are presented as a guided trial at launch (same framing as full AI lesson plans); Hafiz to confirm, Codex to carry into the masters and reading draft.
- **Update, 07/09/2026 (third build):** Hafiz's ten-point review led to a slide-by-slide rebuild against Mobbin references he chose in his browser, a new data slide (fifteen slides), and two copy rules for every document: "student" not "pupil" in English, real-looking fictional names and data in mockups. Recorded in handoff §13.
- **Decided (Hafiz, 07/09/2026, D11):** the deck's tiers stand and the masters follow: class view, flags and rule-based suggestions at launch for all teachers; plain-language AI analysis, the teacher assistant and AI-written admin drafts as a guided trial with selected teachers at the same launch. Codex updates the feature spec, blueprint and reading draft. Two reviews (Codex CLI read-only, Claude) plus a first-glance test ran on the third build; all blocking and material findings fixed the same day (handoff §13, README "Third-build reviews and fixes").
- **Handoff, 07/09/2026:** Hafiz handed the deck to Codex. Complete record in handoff §13 "Claude to Codex: complete deck handoff"; build pipeline moved into `production/visual-samples/claude/build/`; partner files in `share/`; Session Map `.agent-os/session-maps/2026-09-07-152600-claude-ai-classroom-kota-buku-deck.md`.
- **Next action:** Hafiz pastes the new continuation prompt from `CODEX-HANDOFF.md` into Codex. Codex applies D11 and the copy rules to the masters and reading draft, refreshes the index, then continues the one-by-one deck review; Codex's document lane (non-technical external explanation and the internal sourcebook) references the deck's slide list and decisions. Hafiz takes review §11 back to Faiz (device base, brand, RPH claim, corrections, 30% vs 25% advance norm, s.35 subcontract disclosure, their B2 PDPA exposure, positioning). Native-speaker read of the BM copy before any external use. No outreach, publication, commit or build authorised.
- **Do not do yet:** No agent outreach to Kota Buku, redONE, MCMC, KPM, Apple or schools; no build, proposal drafting, artifact publishing, commit or un-ignore of concept docs. Local-only status is decided, not an open choice.
- **Decided (Hafiz, 2026-09-06):** Deal structure = co-branded white-label — Kota Buku's name, "powered by **Learnest Lab**"; we own IP/code, act as PDPA processor, no exclusivity beyond KPM, retain the right to sell the Learnest-Lab-branded version to private/international schools. **Refined later the same day (D9):** Sifututor is the main contracting and fronting entity (better audit history, financials and track record); Learnest Lab stays visible as the product technology. Overrides the partner's "STNN.LLM, no Sifututor name" identity rule. Exact legal entity and registration to be confirmed by Hafiz before any document names it.
- **Decided (Hafiz, 2026-09-06):** Device stance = state "M1 or later" as recommended spec with reasons, base A16 as minimum fully supported, show the per-unit cost delta; hardware choice stays with redONE/Kota Buku.
- **Decided (Hafiz, 2026-09-06):** Research docs stay local-only (gitignored, current convention); Codex must run on this Mac or copy the folder by hand.
- **Decided (Hafiz, 2026-09-06):** Commercial structure = one-off platform build/setup fee + per-teacher-per-month run fee inside the existing RM10 slot. **Refined later the same day (D10):** the partner's SEPADU pack owns the commercial numbers (RM37.46M over 24 months, subject to the corrections in review §3 and §7, notably re-basing to teachers only); our five documents stay figure-free and point to the pack. Reveal timing still after the first Kota Buku meeting.
- **Decided (Hafiz, 2026-09-06, D8):** Device population = teachers only (182,757). The partner's 682,757-device base with about 500,000 pupil devices is wrong; Hafiz tells Faiz. Our documents' teacher-only framing stands.
- **Decided (Hafiz, 2026-09-06):** Mandatory-vs-optional AI framing is left to Kota Buku/KPM; the proposal presents AI capability neutrally, carries the staged teacher-pilot rollout as the mechanism, and keeps the Korea rollback evidence as a talking point only.
- **Requirement added (Hafiz, 2026-09-06):** collect every data point from students and teachers throughout the learning journey so the government can later use it for the country and education — to be designed as a government-owned national education data asset (KPM/Kota Buku controller, Learnest Lab processor, Malaysia-resident) with a governance layer (stated purposes, anonymised/aggregated policy views, controller-gated individual access, audit logs). Precedent: DIKSHA/Sunbird telemetry + Obsrv. Risk precedent: Korea NEIS.
- **Decided (Hafiz, 2026-09-06):** the data asset is built fully but pitched quietly — the proposal calls it "reporting and analytics"; the government-data-asset value is raised in conversation, not in the document. Research on the Malaysian school journey completed (8 agents: teacher records system by system, Std 1–Form 5 transitions, KPM KPIs and gaps, five national data-governance models); collection spec written at `docs/ai-classroom-concept/data-collection-spec.md` (timeline, read-vs-add per KPM system, event model, bounded exclusions, governance layer, KPM interface sequencing, verification table).
- **Open decisions for Hafiz:** positioning with Faiz (review §9 C4: lead with the partner's Dasar 80:20 workload anchor and present our pillars as the modules that return time; Claude's recommendation, not decided). Review attention: hardware/distribution rationales conflict with narrower evidence; existing-scope coverage and capture gaps need later prioritisation. Human verification questions remain in data spec §11. Proposal authoring still requires Hafiz's instruction.
- **Decided (Hafiz, 2026-09-06):** AI lesson-plan generation = one backend, staged switch-on — Level 1 (template + AI practice items) for all teachers at launch; Level 2 (AI-written RPH text) live on the same backend as a guided beta for pilot teachers, then general release; grounded on public DSKP first, Kota Buku textbooks as they arrive.
- **Promote to:** Proposal/pitch document (via `doc-design` skill) once Hafiz approves direction; PRD only after Kota Buku responds to the proposal.
- **Links:** `docs/ai-classroom-concept/research-findings.md`, `technical-build-blueprint.md`, `product-feature-spec.md`, `data-collection-spec.md`, `CODEX-HANDOFF.md` (all local-only), `sources/`, and `partner/` (SEPADU pack verbatim plus `SEPADU-review.md`); Session Map `.agent-os/session-maps/2026-09-06-220039-claude-ai-classroom-kota-buku.md`; Koda mem_a330ad6c47bf (entry point), mem_ce912bf852f0 (current state), mem_b07d50fad82f (Codex review mandate), mem_8821ccb2e9dd (review lessons), mem_69414c2e0b25 (data spec), mem_bc10964b03af (artifact URLs), plus the research pointers mem_5d3b07184852, mem_8f0201fd75af, mem_da43b33d5d8e, mem_d869a836a22a.

### ST-REQUEST-STOP-001 — Safe parent-requested end to ongoing tuition

- **Project:** cross-project (sifu-tutor, ripple-suite; parent/tutor apps if later required)
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** Parents can request an end to active tuition with existing classes and invoices through a clear, safe process that preserves history and handles outstanding obligations explicitly.
- **Why it matters:** Stopping an active request affects future classes, delivered lessons, invoices and payments. Existing SIMS deactivation can cancel scheduled classes and alter invoice visibility; it must not be treated as a simple status button.
- **Source:** Hafiz, V7/V8 discussion, 2026-09-06: include this workflow later, separately from early-stage cancellation.
- **Next action:** After the V7/V8 scope, diagnose existing stop/pause flows and discuss effective stop date, future classes, delivered classes, unpaid invoices, prepaid balances/refunds, tutor notice and staff responsibility. These are design questions, not approved financial rules. Decide whether parent self-service or staff-assisted intake is appropriate before selecting app changes.
- **Promote to:** PRD after discussion and read-only financial diagnosis
- **Links:** Local Session Release Ledger `.agent-os/session-release-ledgers/2026-09-04-v7-tab-review-ledger-codex.md`; excluded from current V7/V8 implementation bundle. No implementation, production changes or financial actions authorised by this capture.

### WEB-TRACKING-001 — Finish Google Ads API audit and close open website design decisions

- **Project:** cross-project (`sifututor` marketing sites: sifututor.my + nakngaji.my)
- **Status:** paused
- **Type:** mission
- **Parent:** none
- **End goal:** Audit both Google Ads accounts end to end via the API, confirm
  whether the legacy conversion action `TquICKHR2asaEKzi4osC` ("Nakngaji Signup
  | Mar 25") is still referenced by any live campaign, and close the two
  remaining website design decisions.
- **Why it matters:** The legacy conversion snippet was removed from production
  on 07/08/2026 after being verified as never firing, but whether that Ads
  conversion action still matters is unanswered. Singapore conversion tracking
  was fixed the same day and should be confirmed against real Ads data.
- **Source:** Production responsive/QA sweep of both marketing sites,
  07/08/2026.
- **Current state:** Google Ads API lane is fully configured and auth verified,
  but blocked: the developer token is Test Access only, so queries fail with
  `DEVELOPER_TOKEN_NOT_APPROVED`. Basic Access applied for on 07/08/2026.
  GTM access works (service account, no expiry) for both containers.
- **Next action:** When Google grants Basic Access, run
  `./scripts/agent-access/check-google-ads.sh` and audit conversion actions for
  both Ads accounts (`701777403` sifututor, `561557804` nakngaji).
- **Do not do yet:** Do not change campaigns, budgets, or bids; the Ads lane is
  registered read-only. Do not alter punctuation in the legal pages'
  remaining content without Hafiz's say-so.
- **Open decisions for Hafiz:** (1) video thumbnails on `/reviews/` and
  `/how-it-works/` cards are cropped mid-word (portrait thumbnails in landscape
  cards) — crop vs letterbox is a design call; (2) `/reviews/` hero
  speech-bubble text renders ~7px on mobile and needs re-sizing as a designed
  graphic, not a CSS tweak; (3) a payment-method warning on Ads account
  739-847-9444 may mean campaigns have stopped serving.
- **Promote to:** GitHub issue only if the Ads audit surfaces engineering work.
- **Links:** `docs/agent-playbooks/agent-access-map.md` (lanes 23-24),
  Koda mem_3138c4550d5d (Elementor CLS root cause),
  mem_1ddc248f3f22 (Meta Pixel headless suppression),
  mem_2015ae07074e (bulk-regex CSS corruption rule),
  mem_32f8faee38fc (Google access lane facts)

### WEB-PERF-SEO-001 — SEO/GEO/performance/accessibility research and Phase 1 implementation

- **Project:** cross-project (`sifututor` marketing sites: sifututor.my + nakngaji.my)
- **Status:** active
- **Type:** mission
- **Parent:** none
- **Related mission:** WEB-TRACKING-001 is adjacent but has a different scope:
  Google Ads and two design decisions, while this mission covers
  SEO/GEO/performance/content Phase 1 fixes.
- **End goal:** Research current (2026) SEO/GEO-AEO/performance/accessibility
  best practice, audit both sites against it and against local/global
  competitors, then execute every fix that does not require a UI/UX design
  pass. Phase 2 (new components: stat bars, tutor credential cards, rate
  tables, named guarantees, etc.) is intentionally out of scope here.
- **Why it matters:** Hafiz asked for a deep gap analysis to be compiled for
  reuse across sessions, then asked to execute Phase 1 fixes directly rather
  than leave them as a backlog.
- **Source:** Hafiz-directed research + implementation session, 07-09/08/2026.
- **Current state:** Phase 1 is essentially complete and verified live on both
  sites. Delivered: competitive UX gap analysis, technical SEO/GEO/performance/
  accessibility audit, and a phased implementation plan, all in `docs/`. Executed
  and verified: Nakngaji h1/lang/OG-Twitter/hello-world-stub fixes; Sifututor
  footer demo-content removal + real social links; tutor-count reconciliation
  (4,500+ to 10,000+, fixed in 4 separate storage locations); footer tagline
  rewrite (dropped "home tuition" venue-anchor + unsubstantiated "the best"
  superlative); a "malayian" typo fixed across 3 shared templates; `LocalBusiness`
  schema with real Google Business Profile links on both sites; `FAQPage` schema
  on Sifututor (81 questions); 13 mislabeled non-heading widgets fixed (verified
  screenshot-identical); Sifututor mobile performance 68→73 (removed unused
  gum-elementor-addon assets); Nakngaji mobile performance 49→72 (root-caused to
  Cloudflare Bot Fight Mode's JS challenge costing ~2.5s of mobile main-thread
  time — disabled on nakngaji.my only, Sifututor's setting left untouched);
  Cloudflare edge caching enabled on 7 confirmed form-free pages only (Sifututor
  ×6, Nakngaji ×1), with every page containing a lead-capture form explicitly
  excluded by design, not just given a short TTL.
- **Next action:** Watch nakngaji.my form-spam volume for 1-2 weeks now that
  Bot Fight Mode is off (FluentForm's own controls are the only remaining
  defense). If it becomes a problem: re-enable (accepts the ~2.5s mobile
  penalty) or evaluate Cloudflare Pro (~USD 20/mo) for Super Bot Fight Mode,
  which allows bot protection without the JS-challenge cost.
- **Do not do yet:** Phase 2 (new UI/UX components) without a dedicated design
  pass per `feedback_decision_protocol`. Sifututor's remaining render-blocking
  cleanup (28 small per-widget CSS files) needs an optimisation plugin
  (Autoptimize/WP Rocket/FlyingPress) — Hafiz explicitly chose to stop rather
  than add new production software in the same session. Do not re-enable
  Nakngaji's Bot Fight Mode or touch Sifututor's without checking current spam
  volume first.
- **Promote to:** GitHub issue only if Phase 2 gets scheduled as real dev work.
- **Links:** `docs/sifututor-nakngaji-competitive-gap-analysis-2026-08.md`,
  `docs/sifututor-nakngaji-seo-geo-performance-audit-2026-08.md`,
  `docs/sifututor-nakngaji-implementation-plan-phase1-2026-08.md`,
  auto-memory `reference_wordpress_sites_access.md`,
  auto-memory `reference_cloudflare_credentials.md` (Bot Management API
  dependency gotcha), auto-memory `project_competitive_gap_analysis_2026-08.md`

### OPS-CRED-001 — Rotate environment values exposed by an unsafe process-status check

- **Project:** cross-project (`creative-hub` infrastructure + Ripple staging/production)
- **Status:** active
- **Type:** mission
- **Parent:** none
- **End goal:** Rotate every credential value returned in private agent tool
  output by an over-broad PM2 status command, verify the affected services, and
  replace the command with a metadata-only status check.
- **Why it matters:** Even though the values were not copied into code, reports,
  Koda, or GitHub, process environment must never appear in diagnostic output.
- **Source:** Ripple Luna Issue #244/#269 release sessions, 2026-07-28 to
  2026-07-29, the Tutor DOB production release session on 2026-08-12, and the
  Ripple tutor-payment bonus production release on 2026-09-07.
- **Current state:** The affected feature releases are complete. Over-broad PM2
  diagnostics returned process environment values in private agent tool output
  during both staging and production release checks. On 2026-09-07, an
  over-broad process-list check also returned Ripple's production PostgreSQL
  connection credential from a running backup command. No value was copied
  into commentary, reports, files, Koda, commits, or GitHub. The safe
  replacement is a filtered metadata-only process check that never prints
  process arguments or environment values.
- **Next action:** Hafiz must approve separate, exact Creative Hub, affected
  Ripple environment, and Ripple production PostgreSQL rotation scopes. For
  PostgreSQL, inventory the application and deployment-backup consumers first,
  rotate the credential atomically, then restart and smoke-test Ripple plus its
  standard backup path.
- **Do not do yet:** Do not rotate unrelated JWT, webhook, provider, or database
  credentials as part of another feature release. Do not rotate the affected
  PostgreSQL credential until its consumers and rollback path are confirmed.
- **Promote to:** Ripple engineering repair is tracked in
  [ripple-suite#806](https://github.com/Sifututor/ripple-suite/issues/806);
  credential rotation remains a separate critical action after the repair and
  exact-scope approval
- **Links:** `.agent-os/session-maps/2026-07-28-161738-codex-luna-244-release-safety.md`,
  `.agent-os/session-maps/2026-08-11-210948-codex-tutor-dob-release-parked.md`

### OPS-CRED-002 — Redact leaked credential literals from creative-hub Koda memories

- **Project:** cross-project (Koda memory system, `creative-hub` project scope)
- **Status:** done
- **Type:** mission
- **Parent:** none
- **End goal:** Remove the raw plaintext credential strings from the 8
  `creative-hub` Koda memories that still contain them, without losing the
  underlying lessons (git-history credential scrub, STATUS.md cleanup, etc.).
- **Why it matters:** A `/koda-audit` session on 2026-08-16 found 8
  `creative-hub` memories with a raw secret literal in their `content` field —
  4 with a dev "playground" login password (low stakes, intentional dev
  convenience), 4 with a production superadmin password that was already
  rotated and scrubbed from git history (dead, but still shouldn't sit in a
  searchable memory store). All 8 already had `confidence: outdated`, but that
  label does not redact the text.
- **Source:** `/koda-audit` session, 2026-08-16.
- **Current state:** Completed during the approved 2026-08-26 Koda
  maintenance. All eight identified memory IDs were rechecked: four historical
  rows are soft-deleted and four remain active, with no credential literal
  detected in any of the eight. The two active Creative Hub memories
  encountered in the final pass were rewritten to preserve their lessons
  without login values, their FTS rows were rebuilt, and stale embeddings were
  removed.
- **Next action:** None. Keep the executable secret-pattern audit in future
  Koda maintenance and sanitize immediately when it finds a real value.
- **Promote to:** Completed in Koda `mem_e55cef2a0d81`.
- **Links:** `.agent-os/session-maps/2026-08-16-100223-claude-koda-audit-mcp-fix-credential-leak.md`,
  Koda `mem_7eac84b71aa9` (ownership no-op bug),
  affected memory IDs: `mem_0b022974ae9e`, `mem_2042d5eca013`,
  `mem_48bbbf9cd091`, `mem_54cf76c505fc`, `mem_42b7601a3c5f`,
  `mem_79d5427fdbdd`, `mem_816c137dca47`, `mem_57024d33c69d`

### SIMS-IDENTITY-001 — Unify User and Staff account lifecycle

- **Project:** cross-project (`sifu-tutor` + `ripple-suite`)
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** Manage a person's login identity, linked staff/employment
  profile, roles, permissions, and employment lifecycle through one coherent
  User + Staff feature.
- **Why it matters:** Operational permissions can currently be assigned to a
  user whose SIMS staff link is missing or inactive. That creates menu access
  in Ripple followed by authorization failure in SIMS and encourages unsafe
  one-off data repairs.
- **Source:** Hafiz decision after the Tutor Experience production staff-link
  repair, 2026-07-28.
- **Current state:** The confirmed production data mismatches were repaired
  separately. Hafiz explicitly declined a Tutor Experience-specific
  validation workaround and wants the complete User + Staff feature designed
  later.
- **Next action:** When Hafiz prioritizes this mission, run product design for
  account creation, linking an existing user, employment status transitions,
  role/permission ownership, duplicate resolution, audit history, and
  Ripple/SIMS synchronization.
- **Do not do yet:** Do not auto-create staff profiles, reactivate former
  staff, auto-link ambiguous users, or add isolated module-specific guards.
- **Promote to:** GitHub issues only after the product and migration boundaries
  are agreed.
- **Links:** Koda `mem_5f299fe8f3fe`, Koda `mem_5478e6bc37b7`

### XP-MATCH-001 — Build one platform matching and opportunity decision engine

- **Project:** cross-project (`ripple-suite` + `sifu-tutor` +
  `sifututor_parent` + `sifututor_tutor`)
- **Status:** active
- **Type:** mission
- **Parent:** none
- **End goal:** One explainable and configurable engine powers CX Support tutor
  recommendations, Tutor App opportunities, targeted notifications, difficult
  and old Request expansion, fair new-tutor exposure, performance-aware
  distribution, and separately governed incentive recommendations.
- **Why it matters:** A formula built only for today's staff matching screen
  would create another dead end. Sifututor needs the same decision logic to
  balance customer fit, tutor needs, new-tutor development, and platform
  fulfilment across every future channel.
- **Source:** Hafiz CRM and tutor-matching review, 2026-07-31.
- **Current state:** The long-term product direction and staged decision model
  are captured. Active, verified, and suitable unverified tutors remain part
  of discovery, while assignment readiness stays a separate SIMS safety rule.
  Hybrid refresh is confirmed: change-driven updates, configurable scheduled
  reconciliation, manual staff refresh, duplicate-safe versioned jobs, and
  final current SIMS action checks. Ripple is confirmed as the canonical engine
  owner. SIMS remains authoritative for tutor, Request, application,
  assignment, and class truth, supplies the Tutor App, and performs final
  safety checks. The earlier SIMS-only ranking-service placement is
  superseded. The candidate workflow now uses one simple current position,
  separate verification state, and separate final reason. CRM reuses the
  existing Tutor Profile module and binds a sent profile to its exact published
  version. A parent choice is an explicit CX Support confirmation today; Ripple
  automates only the resulting work after that confirmation. The exact
  Request-specific delivery is a versioned Candidate Presentation that binds
  the Tutor Profile version and Request Revision. Missing delivery
  administration is recorded truthfully, while material Request changes make
  the old presentation Outdated and require revalidation without rewriting
  history. Current SIMS main already provides the low-level safety for a
  request-specific unverified-tutor exception: Tutor Experience verification
  must be Approved, the exception belongs to one exact Request, the grant and
  assignment are atomic, hard-blocked tutors remain ineligible, and the parent
  path cannot create an exception. The target Ripple journey now records the
  parent choice and the CX Support approval information once, links the waiting
  Request to the tutor's single Tutor Experience verification case, and waits.
  The first detailed eligibility reconciliation has also compared the actual
  Ripple matcher, both current SIMS matching services, current-main SIMS
  assignment safety, the approved CRM documents, and an independent Claude
  review. The target uses four separate permissions: suitable active, verified,
  and unverified tutors may be discovered; only safe and contactable tutors may
  be approached; only tutors with a current Request-bound application and an
  exact prepared profile may be shown to the parent; and assignment or class access
  requires a fresh SIMS safety result. For an unverified tutor, that final step
  requires Tutor Experience approval and the exact Request exception. Existing
  matching paths disagree on whether unverified tutors appear, and their blanket
  prior-activity exclusion must be replaced by outcome-aware reconsideration.
  Hafiz confirmed Option A on 2026-08-01: the parent-facing profile shows no
  internal verification-in-progress label and no verified badge unless SIMS
  confirms it, while staff see the internal warning and the final safety gate
  remains enforced. Tutor Experience work starts only after the parent selects
  an unverified tutor, not at discovery, contact, reservation, preparation, or
  profile delivery.
  Hafiz then confirmed Option B for candidate ordering: Ripple always shows
  Strong Matches first, Other Suitable Tutors second, and Wider Options third.
  Readiness, responsiveness, workload, performance, and fair new-tutor
  exposure may reorder tutors only within one fit group. A same-level,
  category, inferred, or missing subject fact cannot be presented as an exact
  subject match, and verification status remains separate from fit.
  A trusted SIMS Tutor Experience approval event then triggers one fresh,
  duplicate-safe assignment attempt. Hafiz approved the complete waiting
  state: CX Support sees `Waiting for Tutor Verification`, TX receives one
  verification task, schedule information remains preparatory only, and no
  assignment, class, or class notification occurs before approval. A missed
  event is recovered by scheduled SIMS reconciliation. Fresh Request, parent
  choice, assignment, verification, and hard-block checks prevent stale work;
  duplicate events and uncertain responses reconcile to one result. Delay does
  not invent rejection; rejection
  returns the same Request to candidate selection; a material later revocation
  blocks work and creates visible repair work. An unpaid tutor commitment fee
  alone does not revoke a Tutor Experience approval or interrupt an existing
  request-specific assignment. Hafiz corrected the tutor-confirmation boundary
  after current SIMS was rechecked. Before profile readiness, the Tutor App
  shows the current Request days/time. In the target, only a Revision-bound
  application with the immutable accepted-facts snapshot proves interest plus
  acceptance of that displayed schedule. The current generic application does
  not. CX Support does not
  duplicate the confirmation. The application still does not create or
  authoritatively set the official first class. After the parent selects the tutor and the tutor is approved,
  CX Support remains the direct customer-facing owner and completes the
  Request. CX Onboarding supports the journey specifically by following up
  commitment-fee payment when it is required. Current
  SIMS requires the mutually agreed first class date/time and, when the
  Request's parent commitment fee is pending, payment recording or an
  authorised waiver before it creates the class. Hafiz reconfirmed that every
  parent must first complete one genuine positive commitment-fee payment; only
  a later Request's pending fee may qualify for waiver. Ripple will preserve
  SIMS's current interaction: CX Support normally performs the manual waiver
  for an eligible later fee and must enter a reason; the waiver is never
  applied silently or automatically. The target Ripple page is
  named `Confirm First Class`, not the misleading `Complete request`. It is one
  CX Support work item with selected-tutor context, SIMS-derived fee state,
  protected payment/waiver handling, and the agreed first-class date/time. It
  remains an explicit CX Support confirmation even when payment arrives first.
  When payment is pending, CX Onboarding receives the collection follow-up
  while CX Support sees that completion is waiting for payment.
  Hafiz approved the detailed unpaid-fee state: Ripple derives
  `payment_required` from the exact SIMS Request, auto-saves the proposed class
  time only as a draft, creates one CX Onboarding follow-up, and never treats a
  parent's payment claim as settlement. FIUU-confirmed SIMS payment, or a
  controlled offline payment recorded by CX Support from shared evidence,
  closes the follow-up and unlocks final confirmation. A qualified manual
  waiver makes collection unnecessary. Stale schedules require reconfirmation,
  payment/waiver races are resolved by a fresh SIMS check, ambiguous money goes
  to Finance review, and non-payment remains visible and overdue without
  silently completing, cancelling, or losing the Request.
  Hafiz approved the first-class schedule-expiry and conflict policy. Ripple
  stores an agreed time as provisional information while payment or Tutor
  Experience work is pending, creates no class or notification, and shows a
  visible warning rather than hard-reserving the tutor. An expired time creates
  CX Support work to agree a replacement without changing the Request,
  candidate, payment, or customer outcome. Final confirmation remains a
  duplicate-safe SIMS command with fresh future-time, Request, tutor,
  verification, fee, quota, tutor-overlap, student-overlap, and existing-class
  checks. Conflicts preserve the draft and any earlier completed payment while
  same-command fee or waiver work rolls back with a failed class creation.
  The next current-main audit found that SIMS still couples first-class
  notifications unsafely to class creation: several emails, app-notification
  rows, push dispatches, and request broadcasts occur before the class and
  outer completion transaction are committed. Some delivery errors are ignored
  while others can roll back the class operation. The target contract already
  requires durable same-command reconciliation and post-commit notification
  delivery. Hafiz approved Option B: Ripple persists the exact operation before
  dispatch, shows `Checking confirmation` after an unclear result, blocks a
  second business action, and reconciles only the same operation ID. SIMS
  commits the class, fee/waiver, invoice effects, audit, result and outbox
  before external delivery. Notification failure never reverses a confirmed
  class; automatic retries and one grouped CX Support exception cover the
  affected parent/tutor recipients. The default unknown-result escalation for
  this time-sensitive command is configurable 15 minutes with Supervisor
  visibility, replacing the generic four-business-hour delay. Confirmation
  copy states the scheduled time, while invoice/payment communication remains
  separate.
  Hafiz approved the first post-confirmation correction rule. A staff mistake
  in the recorded first-class schedule is `Correct Schedule Entry`; a real
  later change to the parent/tutor agreement is `Reschedule Class`. The
  assigned tutor must retain the existing Tutor App ability to reschedule their
  still-Scheduled first class. The target SIMS path keeps the same class and
  Request identity, records the old and new time, actor, source and reason,
  rejects stale or conflicting changes, and publishes the authoritative result
  to Ripple. Ripple then moves reminders and first-class monitoring to the new
  class end. The legacy replacement-class-row implementation is not the target.
  Hafiz also approved the pre-service tutor-change rule. A wrong tutor recorded
  by staff uses a Supervisor-protected correction because assignment, class and
  notification consequences already exist. A genuine parent or tutor change
  uses the normal CX Support `Change Tutor` journey with reason and Supervisor
  visibility. Both keep the same Request and owner, remove the old tutor's
  Scheduled classes from the current schedule without erasing history, and
  never transfer the old first-class time to the replacement tutor. A ready
  replacement continues through parent choice, verification, assignment and a
  fresh first-class confirmation; otherwise the Request returns to valid backup
  selection or Finding Tutor. An existing paid or waived parent commitment fee
  remains valid.
  Hafiz simplified the post-confirmation commitment-fee correction rule. The
  normal workflow assumes an honest staff mistake, not fraud. Ripple provides
  one authorised correction action where staff records the correct value and a
  reason. SIMS updates the fee and directly connected invoice effect safely;
  Ripple refreshes the result and opens or closes the one CX Onboarding
  collection task. The correction preserves the old value, new value, actor,
  time and reason, but it never automatically changes the scheduled first
  class. A real returned payment continues through the existing refund flow.
  Suspected fraud or deliberate manipulation is outside this normal feature and
  requires manual staff investigation plus controlled developer data
  correction.
  The first-class follow-through review found one remaining dead end. The
  previously confirmed 24-hour exception-only monitor belongs to CX Support,
  not the old Helpdesk label: Ripple watches the earliest valid class and
  creates one `Check First Class` task only if it is still Scheduled 24 elapsed
  hours after class end. Current SIMS moves tutor-recorded completion to
  Attended and requires parent or authorised staff verification before
  Verified. Its existing seven-day auto-verification command is not scheduled
  on main or integration. Hafiz decided that automatic attendance verification
  must remain paused because attendance is not yet enforced strongly enough.
  Time alone must not change an Attended class to Verified in this release;
  parent or authorised-staff verification remains required. Ripple shows
  `Awaiting Verification` immediately and, after seven calendar days, creates
  one `Follow Up First Class Verification` task for the current CX Support
  owner with Supervisor visibility, without changing the SIMS class status.
  Authoritative manual verification closes the same task, and reassignment
  moves an open task to the new CX Support owner.
  Final reconciliation section 1, staged Lead intake through successful first
  Request creation, is complete with independent Claude review and direct
  Codex source verification. No new business conflict was found. Three current
  implementation defects are now explicit inputs to the build plan:
  `round_robin` and `unassigned` imports create neither owner nor First Contact
  task; SIMS may create the Request before Ripple local linkage fails without a
  durable recovery item; and the first `find_tutor` task relies on a legacy
  `sales_support` Lead assignment instead of deliberate CX Support routing.
  Final reconciliation section 2 is also complete with independent Claude
  review and direct Codex verification. Every successfully created or adopted
  actionable Request starts its own Finding Tutor journey, receives zero or one
  eligible CX Support Request owner through same-Family continuity then weighted
  routing, or remains explicitly Unassigned plus Blocked when nobody is
  eligible. It receives one owned or claimable `find_tutor` task that is Open
  immediately and reaches its first sourcing review after seven business days.
  Assignment, Continue, pause/resume, retry, and replay do not restart that
  sourcing cycle. CX Onboarding remains the Family PIC, keeps full journey
  visibility, and receives one informational Request-created/initial-owner
  Update rather than Request ownership. Current Ripple has a nullable
  per-Request support field but no governed Request-owner assignment writer;
  the creation and watcher paths still fall back to Lead-level `sales_support`,
  same-day dates, silent null assignment, and no sourcing-cycle state. The
  active Lead page also still exposes both the target multi-Request flow and an
  obsolete single-Request route/button that uses the older Lead-scoped stage
  and task path. The target durable command/event/reconciliation aggregate must
  repair a SIMS commit followed by Ripple projection failure without
  duplicating a Request, invoice, owner reservation, task, Update, or
  notification.
  Ripple calls one duplicate-safe SIMS-owned command; SIMS rechecks the current
  Request, assignment, tutor safety, fee, quota and class conflict. Only a
  successful class creation closes the task, produces existing parent/tutor
  notifications, and moves the Request into first-class monitoring. Declines and
  withdrawals close only the affected candidate and return the same Request to
  the correct stage without erasing history. Customer engagement does not
  bounce back while CX Support performs supply-side repair.
- **Current subject-evidence decision:** Read-only production evidence found
  26,994 active tutors, but only 1,688 with recorded service-preference subject
  IDs, 2,845 with application-derived subject rows, 215 in both groups, and
  22,677 in neither. All 6,980 `tutor_subjects` rows are inferred; none is
  tutor-confirmed or staff-confirmed. Hafiz confirmed that a tutor-originated
  application means the tutor prefers that Request subject. The target
  therefore preserves six truthful sources: successfully taught, staff
  confirmed, Tutor-App selected, application-derived preference, recorded
  preference with unknown source, and broader/missing/conflicting. Tutor-App,
  application-derived, or staff exact-subject preference can place a new or
  unverified tutor in Strong Matches; verified class history is stronger within
  that group. An application-derived preference must say where it came from
  and never claim manual confirmation or proven teaching ability. Legacy
  unknown-source preferences are Other Suitable.
  Verification remains a separate class-start gate. Latest Tutor App main
  already sends authenticated subject selections through the Service Preference
  endpoint and SIMS main stores them in `tutor_services.subject_ids`; the actual
  current gap is that Ripple supplies an empty exact-subject list and the richer
  SIMS evidence table is not synchronized. Historical repair is confirmed as a
  dry-run-first, resumable, duplicate-safe backfill with source labels, conflict
  reporting, and shadow comparison before ranking changes. Existing and future
  proven tutor applications are merged into current Service Preferences with
  application/Request provenance and used immediately. For legacy applications
  without the future accepted-facts snapshot, use the Request's current subject
  as best available and label that limitation. The Tutor App first-open review
  trigger is explicitly deferred to a future separately designed release and
  is not a dependency of the current backfill or matching rollout. The
  integration-branch migration/refresh behavior that marks an
  application-derived preference as manually tutor-confirmed must not ship.
- **Current controlled-expansion decision:** All three groups are visible to CX
  Support immediately, but targeted Tutor App interruptions are staged. The
  configurable initial defaults are ten Strong tutors immediately, expansion
  into remaining Strong then Other Suitable after four delivered hours when
  fewer than three Parent-profile-ready candidates exist, and Wider Options
  after one business day. Positive responses waiting for staff review create a
  four-business-hour review hold. Delivery is current-fact checked,
  duplicate-safe, capped, and resumed from the next uncontacted tutor when
  usable supply falls. CX Support may expand, pause, or adjust the target with
  a reason under Supervisor visibility. Tutor App actions synchronize through
  SIMS; WhatsApp remains manual until Finch. The confirmed seven-business-day
  review and configurable 14-day maximum remain; expansion never auto-closes
  the Request. The SIMS integration 60-day auto-cancel lifecycle is reference
  material only and is not adopted.
- **Current schedule/availability decision:** General availability is deferred
  completely from matching until Sifututor implements accurate collection and
  has trustworthy coverage. Ripple does not score, rank, group, filter, explain,
  or select outreach using SIMS's broad weekday/weekend time-band slots. This is
  necessary because only 243 of 4,496 active/verified tutors had a slot on
  2026-08-01, and those slots cannot prove an exact day/time. The current Tutor
  App shows Request days/time before Apply, but current SIMS stores only a
  generic Request/tutor activity. The confirmed target treats Apply as interest
  plus schedule acceptance only after SIMS binds it to the exact Request
  Revision or immutable schedule snapshot the tutor saw. CX Support then does
  not duplicate this confirmation. A later withdrawal stops readiness; an
  alternative requires both parent and tutor acceptance. The application never
  updates reusable availability. Final SIMS assignment still rechecks real
  class conflicts under lock. A material schedule change creates a new Request
  Revision and makes the earlier application stale for schedule acceptance,
  never a duplicate Request.
  Future general availability needs its own exact data model, collection,
  freshness, exception, synchronization, comparison-mode, test, and approval
  gate before it can affect matching. Hafiz confirmed Option A on 2026-08-01:
  every real Request from Parent App, SIMS Admin, Ripple, import, or API requires
  at least one preferred day and one preferred time. There is no generic
  Flexible value in this release. Drafts may be incomplete, and the official
  first-class date/time remains a separate post-selection decision.
- **Source-first correction audit:** Before the next matching factor, direct
  comparison of Parent App, Tutor App, SIMS Admin, SIMS APIs/storage, the SIMS
  `integration` branch, Ripple, the decision documents, Session Map, and Koda
  found four current-versus-target gaps. No verified Request origin offers the
  previously documented `explicit Flexible` schedule choice. Parent App already
  requires a preferred day/time while SIMS Admin incompletely validates time;
  Option A now standardizes the required day/time contract. Latest Tutor App
  main already saves selected exact subjects into `tutor_services.subject_ids`,
  but Ripple does not consume them and the evidence model/backfill needs repair.
  Current Apply sends only Request ID and optional comment, so SIMS stores no
  Request Revision or immutable schedule/location snapshot. The confirmed
  target adds a signed Revision/acceptance token, current-state recheck under
  lock, duplicate-safe immutable accepted-facts snapshot, privacy-safe area,
  and a staged mobile rollout. Legacy applications remain `Unbound Legacy
  Application` and prove interest only. View and Apply are current integration
  signals; Saved, Dismissed, and a separate Interested action remain future
  inputs. These are corrections to source truth and implementation readiness,
  not a reversal of the confirmed engine direction.
- **Current location/travel decision:** Online Requests ignore location. For a
  physical Request, tutor-selected teaching city is strong reusable evidence,
  while home city is a clearly labelled fallback. Same state is never called
  Nearby and carries no invented distance or travel-time score. The current
  Tutor App already shows area and city before Apply; the target Apply action
  explicitly binds acceptance of that privacy-safe travel area together with
  schedule acceptance for the current Request Revision and cycle. It may
  resolve only the location uncertainty it proves and never rewrites reusable
  teaching cities. Full family address stays hidden until the approved later
  boundary. A material location change creates a new Revision on the same
  Request and makes the prior application/profile stale. Real route-time
  ranking is deferred because production has no adjacency rows and usable
  coordinates for only 491 of 4,496 active/verified tutors and 165 of 14,795
  physical Requests. It requires a separately approved data, privacy, provider,
  accuracy, cost, latency, comparison-mode, and test gate.
- **Confirmed curriculum deferral:** Hafiz confirmed on 2026-08-01 that
  curriculum must not affect the current matching release. Existing Tutor App
  curriculum choices remain stored for future use, but no missing, inferred,
  legacy, or conflicting curriculum value may change current fit, order,
  explanation, outreach, or readiness. A future separately approved slice must
  first repair and link level and curriculum across Parent App, SIMS Admin,
  Ripple, Tutor App, API/import paths, Request Revisions, legacy adoption, and
  synchronization, then pass coverage and shadow-comparison gates before use.
- **Confirmed special-needs current-release safety:** Hafiz confirmed on
  2026-08-01 that special needs do not affect automatic fit or ordering in the
  current release because SIMS has the student's need but no reliable
  structured tutor-capability fact. For a Request with a special need, every
  candidate starts `Learning-support experience not confirmed`. CX Support
  must record Confirmed, Cannot support, or Still checking before profile
  delivery. Only Confirmed permits delivery. The outcome is Request-specific,
  Revision-bound, multi-student aware, audited, and Supervisor-visible; it
  cannot be inferred from application, free text, education, old classes, or
  artificial intelligence. The full structured capability engine is future.
- **Confirmed special-needs information boundary:** Hafiz confirmed Option A
  on 2026-08-01. A logged-in tutor who deliberately opens the Request detail
  may see the actual teaching-relevant learning-support information before
  applying. The current release does not add a generic-label and staged-reveal
  journey. Student identity, parent contact details, exact home address, and
  unrelated private information remain hidden. Seeing or applying does not
  replace the Request-specific CX Support capability confirmation.
- **Current performance-metric correction:** Ripple already shows
  Request-specific Matching Confidence separately from tutor-global Platform
  Rating. Current Matching Confidence does not consume Platform Rating. The
  target must preserve both meanings and must not silently blend a staff
  conduct score into the Request fit number. The open decision is how a conduct
  entry becomes trusted enough to change Platform Rating and whether a
  separately validated risk flag restricts an action.
- **Confirmed Platform Rating governance:** Hafiz confirmed Option A for the
  current release on 2026-08-01. An authorised positive or negative conduct
  entry recalculates tutor-global Platform Rating immediately without
  Supervisor approval. It never changes Request-specific Matching Confidence,
  fit group, tutor status, eligibility, or fault attribution automatically.
  Option C is deferred until the complete Supervisor review operation is
  separately designed, implemented, and adopted by the team; it is not a
  current-release dependency.
- **Confirmed Verified-class evidence:** Hafiz confirmed Option B on
  2026-08-01. An authoritative SIMS Verified class creates objective
  `successfully_taught` evidence for the exact class tutor, subject, and level.
  It may strengthen relevant future matching evidence, but it does not create a
  conduct record, change Platform Rating, or claim teaching quality or parent
  satisfaction. Only Verified qualifies while automatic verification remains
  paused. Replacement, group-class, legacy attribution, correction, refund,
  duplicate-event, and historical-backfill handling must preserve truthful
  provenance and audit history.
- **Confirmed tutor-withdrawal evidence:** Hafiz confirmed Option B on
  2026-08-01. Ripple separates the immediate Request recovery, responsibility,
  and any future reliability use. Until a separately assigned Tutor App release
  adds `Withdraw Application`, Customer Experience Support records `Tutor
  Cannot Continue` after accepted tutor communication, and Ripple does not
  pretend to detect the call or WhatsApp automatically. Every stage preserves
  the same Request and history while blocking stale profiles or selections and
  routing assigned tutors through Change Tutor. Only an avoidable tutor decision
  after a valid current commitment may create separate
  `withdrawal_after_commitment` history. No withdrawal automatically changes
  Platform Rating, Matching Confidence, fit group, eligibility, or tutor status.
  Reapplication, correction, duplicate events, races, parent communication, and
  legacy Unsuccessful data must preserve truthful provenance.
- **Confirmed continued-service and early-ending evidence:** Hafiz confirmed
  Option B on 2026-08-01. Ripple automatically records objective Verified-class
  counts and calendar periods and detects a paused or terminal SIMS Request, but
  it does not infer the ending cause or tutor responsibility. Customer
  Experience Support records a structured ending reason and separate
  responsibility classification when ending service through Ripple. An ending
  received without that information creates one review task and remains Unknown
  and neutral until reviewed. After service starts, a terminal Request is Ended,
  never Lost; an in-service Tutor Replacement preserves the same non-terminal
  Request and Active Customer state. Planned one-class completion, customer
  causes, Unknown, and staff or system causes do not become negative tutor
  evidence. No continuation or ending record automatically changes Platform
  Rating, Matching Confidence, fit group, eligibility, or tutor status. Any
  future ranking use requires separately approved sample, coverage, correction,
  comparison, explanation, and test controls.
- **Confirmed current-release parent-feedback boundary:** Hafiz selected Option
  A on 2026-08-01. The current release keeps authorised staff-recorded conduct
  only and does not add direct Parent App tutor feedback. A general complaint,
  call, or WhatsApp message never becomes tutor evidence automatically. Staff
  must review the communication and take responsibility for any linked conduct
  record, which remains labelled as staff recorded. Missing parent feedback is
  neutral. Direct authenticated Parent App feedback is deferred as a complete
  future cross-project slice covering the SIMS-owned contract, exact
  parent/tutor/Request/cycle binding, mobile handoff, prompt rules, corrections,
  disputes, replacements, privacy, abuse, safety escalation, Ripple review,
  older-app compatibility, and permanent iOS, Android, SIMS, and Ripple tests.
  Its future effect on Platform Rating or matching requires a separate decision.
- **Mobile delivery ownership:** Parent App and Tutor App implementation remain
  separate work for the mobile app developer. Cross-project design must provide
  a build-ready mobile instruction pack containing the exact screens, SIMS API
  contract, old-version behaviour, release sequence, and iOS and Android
  acceptance evidence. Ripple or SIMS work must not silently include mobile
  code unless Hafiz separately assigns that implementation.
- **Confirmed Request-choice decision:** The live Parent App offers Male,
  Female, and Any from SIMS. Hafiz confirmed Option A after the source review:
  Parent App, SIMS Admin, and Ripple will use one SIMS-owned contract labelled
  Male preferred, Female preferred, and No preference, stored as `male`,
  `female`, and `any`. Blank and Any normalize to No preference. Male/Female is
  flexible, not compulsory. A different recorded gender may appear only in
  Wider Options under controlled expansion with a truthful explanation. SIMS
  Admin must remove its duplicate Any, SIMS must validate every creation path,
  Ripple must expose the field and treat Any as neutral, student gender is not
  substituted, and a later preference change stays on the same Request through
  a new Revision.
- **Confirmed repeated-problem monitoring:** Hafiz confirmed Option B on
  2026-08-01. Ripple combines authorised staff-recorded conduct with reliable
  system facts whose actor and responsibility are proven, but never guesses
  blame from calls, WhatsApp, general complaints, customer silence, unchanged
  class status, technical failure, or Unknown causes. One underlying incident
  counts once even when it has several notes or sources. Recommended
  configurable starting thresholds are three supported incidents within 90
  days for one Request or fulfilment cycle, or three within 180 days across at
  least two Requests or families. The threshold creates one Supervisor review
  task and an authorised pattern view. It does not add another Platform Rating
  penalty, change Matching Confidence, fit group, matching order, eligibility,
  verification, or tutor status. Severe safety or major policy matters continue
  through the immediate authorised process. Any future ranking effect requires
  separate evidence, fairness, correction, comparison, explanation, and test
  approval.
- **Current CRM boundary:** Tutor App Request-list ranking, controlled
  opportunity visibility, and any connected incentive or extra-commission work
  belong to the future Tutor App opportunity-feed project. The current CRM
  build must not change the Tutor App list or recommend, create, present,
  accept, or pay a new incentive.
- **Confirmed staff control of recommendations:** Hafiz confirmed Option A on
  2026-08-01. Matching order is advisory. CX Support may choose any currently
  eligible tutor shown in any fit group without entering a reason or obtaining
  Supervisor approval merely because the tutor is lower-ranked or broader.
  Ripple automatically preserves the actor, time, Request/Revision/cycle,
  tutor, action, group, position, Matching Confidence components, policy
  version, and displayed source facts. The action cannot bypass safety,
  contact, stale-state, learning-support, verification, Request-exception, or
  final SIMS eligibility rules. A higher-ranked tutor never replaces the
  parent's exact selected profile.
- **Final CRM-release reconciliation:** Complete on 2026-08-01. The first
  release orders the three fit groups first, then uses only low active assigned
  workload +5 at <=1, recent Tutor App login +5 within three calendar days, and
  emerging-tutor exposure +3 below three Verified classes. It removes the weak
  Applied-before soft bonus and excludes deferred availability, curriculum,
  language, feedback, Platform Rating, response-speed, repeated-problem,
  incentive, and commission inputs. Several profiles may remain under parent
  consideration, with exactly one selected and assigned tutor.
- **Next action:** Use the completed final audit to prepare the first exact
  implementation issue and build prompt only after Hafiz separately approves
  implementation scope.
- **Do not do yet:** Do not implement competing Ripple and SIMS formulas, train
  an opaque model, auto-change commission, or treat clicks/applications as the
  final success outcome.
- **Promote to:** Cross-project PRD, backend and event contract, Tutor App UX,
  QA plan, and GitHub implementation issues after the architecture and policy
  decisions are confirmed.
- **Links:** `ripple-suite/docs/features/matching/platform-matching-opportunity-engine-design-brief-2026-07-31.md`,
  `ripple-suite/docs/features/crm/final-consistency-and-implementation-readiness-audit-2026-08-01.md`,
  `sifu-tutor/docs/features/tutor-opportunity-matching/`

### XP-TUTOR-OPPORTUNITY-FEED-001 — Build the future Tutor App opportunity feed

- **Project:** cross-project (`ripple-suite` + `sifu-tutor` +
  `sifututor_tutor`)
- **Status:** active
- **Type:** mission
- **Parent:** XP-MATCH-001
- **End goal:** Replace the Tutor App's broad Tutor Request list with one
  explainable opportunity feed that controls which relevant Requests each tutor
  sees, orders them by fit and platform fulfilment need, provides fair exposure,
  and may show a separately approved incentive for suitable tutors on difficult
  or old Requests.
- **Why it matters:** Hafiz reports that every tutor currently sees the broad
  Tutor Request list, including Requests unrelated to their preferences. The
  future engine should improve relevance for tutors while helping Sifututor
  fulfil Requests, develop new tutors, and use governed incentives only when
  appropriate.
- **Source:** Hafiz CRM and Tutor App scope correction, 2026-08-01.
- **Current boundary:** Keep this as one future Tutor App opportunity-feed
  project. Do not add Tutor App Request-list ranking, visibility changes,
  incentive recommendations, offers, commission changes, acceptance, or
  payment to the current CRM release. SIMS remains authoritative for Request,
  application, assignment, and any future financial contract.
- **Next action:** Resume only when Hafiz prioritises this as a separate task.
  First verify the live Tutor App list and SIMS API. Then run product discovery
  covering relevance and exclusion rules, tutor preferences, exact Request
  Revision facts, controlled expansion, new-tutor exposure, old and difficult
  Request priority, notification frequency, application binding, explanations,
  staff control, legacy app behaviour, and comprehensive SIMS, Ripple, iOS, and
  Android evidence. Discuss incentive type, eligibility, amount, approval,
  budget, expiry, acceptance, payment, correction, and audit within the same
  project before enabling its financial stage.
- **Promote to:** One cross-project Build-Ready Pack with a separately approved
  financial section, followed by SIMS, Ripple, and mobile GitHub issues.
- **Links:** `ripple-suite/docs/features/matching/platform-matching-opportunity-engine-design-brief-2026-07-31.md`

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

### AO-KODA-001 — Migrate legacy `umbrella`-tagged Koda memories to `sifututor`

- **Project:** cross-project Agent OS (Koda memory system)
- **Status:** done
- **Type:** mission
- **Parent:** none
- **End goal:** Reassign the `project` field and tags on every Koda memory
  still using the retired `umbrella` value to the current `sifututor`
  convention (per `docs/agent-playbooks/agent-os-memory.md`'s Project Tags
  Versus Domain Tags section).
- **Why it matters:** `agent-os-memory.md` explicitly states `umbrella` is not
  a valid project tag and `sifututor`/`codex-parity` replaced it, but a
  `/koda-audit` session on 2026-08-16 found at least 32 memories (via sampled
  keyword search, not exhaustive) still carrying `project: "umbrella"` or an
  `"umbrella"` tag — a leftover from before that convention changed.
- **Source:** `/koda-audit` session, 2026-08-16.
- **Current state:** Completed 2026-08-26 after Hafiz approved the full cleanup.
  Codex reviewed all 433 reported rows and checked current workspace ownership
  before trusting the old allowlist. This proved `cx-call-capture-android` (7)
  and `sims-owner-analytics` (9) are legitimate projects, so their memories
  were preserved and both projects were added to the canonical registry. The
  remaining 417 rows were migrated from `umbrella` (406),
  `sifututor-agent-os` (9), and `claude-code` (2) into valid project scopes. A
  global follow-up added 1,068 missing project tags and removed 252 retired
  alias tags.
- **Evidence:** Recovery backup
  `/opt/koda/backups/brain-codex-legacy-taxonomy-20260826T124657Z.db`; 4,855
  active memories across 17 approved projects; invalid project rows 0; missing
  project tags 0; retired tags 0; missing/duplicate FTS rows 0; open or failed
  validation jobs 0; SQLite integrity check `ok`.
- **Security hardening:** The review found the live database and backups were
  readable by other local server users. The live database/sidecars and all
  existing backup files are now `0600`, with `/opt/koda/backups` at `0700`.
  Koda issue #13 and PR #14 contain the tested durable backup-script fix. PR
  #14 was squash-merged to `master` as `652861e` on 2026-08-26 and deployed to
  the canonical KVM8 service. The deployed script produced a verified backup
  with mode `0600`; source and backup integrity checks returned `ok`, public
  and authenticated health checks passed, and the post-reload log watch found
  no new errors.
- **Next action:** None. Future audits should discover live buckets and compare
  them with the canonical registry rather than restoring a hardcoded list.
- **Promote to:** Completed in Koda `mem_e55cef2a0d81` and the shared memory
  playbook/registry.
- **Links:** `.agent-os/session-maps/2026-08-16-100223-claude-koda-audit-mcp-fix-credential-leak.md`,
  `docs/agent-playbooks/agent-os-memory.md` (Project Tags Versus Domain Tags),
  Koda `mem_9dfd166c6332` (recall bumps `last_accessed` lesson)

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

### AO-DELEGATION-001.1 — Measure CRM Claude-builder usage savings

- **Project:** cross-project, using the CRM C4B SIMS and Ripple release
- **Status:** active
- **Type:** research
- **Parent:** AO-DELEGATION-001
- **End goal:** Prove whether two repository-owning Claude Max builders can
  reduce Codex usage and Hafiz back-and-forth while preserving or improving
  critical access, migration, E2E and staging quality.
- **Why it matters:** Earlier delegation moved useful coding to Claude but
  Codex still repeated discovery, read long handbacks, reconciled overlapping
  reviews and repaired gaps found only during staging. Hafiz wants measurable
  usage reduction rather than an assumed saving.
- **Source:** Hafiz correction and approval, 2026-08-05
- **Current state:** The measurement plan is recorded. The approved CRM repair
  package is paused before product/data mutation while Codex prepares one
  frozen cross-system contract and two bounded repository briefs. Actual token
  and subscription usage remains unavailable until a runner exposes it and
  must never be estimated.
- **Next action:** Launch the SIMS and Ripple Claude jobs through the supervised
  Max runner, use script-only status checks, then reconcile measured usage,
  interventions, rework, elapsed time and final staging quality.
- **Do not do yet:** Do not make this routing style the permanent default until
  the final measured retrospective is complete.
- **Promote to:** AO-DELEGATION-001 and the Agent OS delegation workflow only
  after the measured staging retrospective shows that the quality and usage
  targets were met.
- **Links:** `.agent-os/session-maps/artifacts/crm-c4b-claude-builder-usage-experiment-2026-08-05.md`,
  `.agent-os/session-maps/2026-08-05-031320-codex-crm-c4b-parallel-build.md`

### AO-DELEGATION-001.2 — Integrate comprehensive build handoffs into Agent OS

- **Project:** cross-project Agent OS, using Nakngaji Wave B as the case study
- **Status:** triaged
- **Type:** research
- **Parent:** AO-DELEGATION-001
- **End goal:** Agent OS can prepare adaptive, source-verified, machine-checkable
  Claude implementation handoffs that are complete for the task's real risk
  without imposing a 503-row critical-lane process on ordinary small work.
- **Why it matters:** The Nakngaji pilot prevented weak implementation and false
  completion through source pins, stable obligations, materialised acceptance,
  integrity freeze, independent plan review and a fail-closed checker. The
  attempt-2 independent review then proved that exact commands, stable IDs and
  green machine counts can still accept semantically weak tests when they do
  not exercise the real route, transaction, persisted state or concurrency
  mechanism. It also exposed repeatable environment, cumulative-checkpoint,
  state-freshness and branch/active-task guard gaps.
- **Source:** Hafiz request during the Nakngaji Wave B Claude handoff and B0
  infrastructure recovery, 2026-08-15
- **Current state:** The case study and live findings are updated through Claude
  attempt 3, Codex's final B1 acceptance and the B5/CRM-process comparison. Twenty-nine reusable findings
  now cover product discovery, contract generation, infrastructure, false PASS
  evidence, dead production services, route-level regression, real financial
  state mapping, frozen-command feasibility, browser/mobile provisioning,
  candidate-SHA frontend builds, cumulative checkpoint enforcement, handback
  freshness, UI consequence safety, row-scoped mutation proof, shared-test-
  resource locking and the need for named integrated human UAT above a dense technical ledger.
  B0-B5 now reach 207/503 mechanically; Codex is adding the CRM-style human-UAT gate before
  continuing through B9. No Agent OS behavior has been changed from this research item.
- **Next action:** In a separate session, use `$workflow-improvement`; read the
  linked case study; audit existing readiness/handoff/delegation/capability and
  evidence owners; then propose an adaptive Product Shape and deterministic
  eval plan before any Agent OS implementation or GitHub issue.
- **Promote to:** Agent OS Product Shape, then a GitHub issue only after Hafiz
  approves the workflow design
- **Links:** `.agent-os/session-maps/artifacts/nakngaji-wave-b-comprehensive-claude-handoff-workflow-case-study-2026-08-15.md`,
  `.agent-os/session-maps/artifacts/nakngaji-wave-b-agent-os-live-findings-2026-08-15.md`,
  `.agent-os/session-maps/2026-08-15-122831-codex-nakngaji-wave-b-handoff.md`,
  `.agent-os/delegations/nakngaji-wave-b-2026-08-15/`

### AO-DELEGATION-001.3 — Learn from CRM comprehensive Claude handoffs

- **Project:** cross-project Agent OS, using CRM-MATCHING-001 as a separate
  real-session evidence source
- **Status:** active
- **Type:** research
- **Parent:** AO-DELEGATION-001
- **End goal:** Future large, critical and cross-system handoffs give Claude or
  another builder one complete executable contract covering exact entry
  points, state/authority boundaries, failure matrices, fresh human journeys,
  deterministic evidence and an honest return contract, with fewer incomplete
  implementations and repeated Codex correction loops.
- **Why it matters:** CRM-MATCHING-001 showed that even a long, careful brief
  can still permit weaker tests, partial operation fingerprints,
  terminal-fixture E2E shortcuts, misleading screenshots and a checker whose
  truncated output hides integrity failures. The third correction also showed
  that a stronger checker can still miss contradictions inside retained logs,
  base-to-head diff failures, incomplete terminal-state identity and visual
  judgments that inspect only a positive chip while invalid controls remain.
  Hafiz wants Agent OS to learn from the complete collaboration after CRM
  finishes instead of losing these lessons in chat.
- **Source:** Hafiz request during CRM-MATCHING-001 correction-loop planning,
  2026-08-15
- **Current state:** A separate CRM learning log records how the handoff was
  prepared, what worked, material failure patterns, candidate future gates,
  minimum document contents, automation/eval ideas and an update protocol. It
  now covers the initial build, all Claude/Codex correction rounds, executable
  acceptance completion, staged/production release and the post-release staff-
  guide deployment. Later findings include authority-side commit leases, real
  rollback entry-point tests, terminal cancellation, cross-phase fixture
  resets, stale deployment-host instructions, shared-staging seed side effects,
  production-shaped dependency gaps, screenshot timing, separate Help/must-read
  publication and self-generated monitoring noise. This work remains separate
  from the Nakngaji Wave B case study and has not changed durable Agent OS
  behavior during the CRM experiment.
- **Next action:** Keep the evidence log current through the small staff pilot
  and first-case observation/correction loop; after the CRM operational
  retrospective, start a separate workflow-improvement session that compares
  the final evidence with existing handoff and implementation-readiness owners
  before proposing the smallest coherent Agent OS change.
- **Do not do yet:** Do not modify handoff skills, hooks, templates, checkers or
  evals mid-experiment; do not estimate unavailable token savings; do not
  treat the candidate future workflow as accepted.
- **Promote to:** A Sifututor Agent OS GitHub issue after the retrospective and
  Hafiz's workflow-design approval.
- **Links:** `.agent-os/delegations/crm-tutor-matching-claude-handoff-workflow-learning-log-2026-08-15.md`,
  `.agent-os/session-maps/2026-08-14-194707-codex-crm-matching-candidate-design.md`,
  `docs/agent-playbooks/handoff.md`,
  `docs/agent-playbooks/ai-implementation-readiness.md`

### FINCH-SIMS-001 — Selective Finch↔SIMS integration for Sifu Edu tenant only

- **Project:** cross-project (finch-inbox + ripple-suite + sifu-tutor)
- **Status:** active
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
- **Execution state (2026-07-19):**
  - **Finch half:** GitHub issue finch-inbox#1734 contains the revised
    SIMS-backed approval, entitlement, explicit selection, multipart v2,
    durable queue/retry, and separate-human-audit contract. Helmi owns the
    Finch implementation. The issue was updated with Ripple's staging state
    and final ready-to-connect canary evidence.
  - **Ripple half: DARK-DEPLOYED TO PRODUCTION.** PRs #198/#199 were promoted
    through release PR #200 and deployed at `8538308b`. Transactional
    migration 070, dedicated production actor 345, and a production-only
    secret are configured; the secret has not been distributed to Finch and
    production contains zero Finch receipts. Full local verification passed
    (2,406 unit tests plus
    4 skipped, 56 focused Finch tests, TypeScript, production build, focused
    lint, and two permanent browser journeys). Production-shaped staging smoke
    proved auth, invoice/phone lookup, no phone leakage, rate limiting, schema,
    and public health. A later full canary proved multipart `201` creation,
    exact `200 duplicate=true` replay, one logical receipt/allocation/audit,
    structured human/service attribution, durable S3-compatible storage,
    `429 Retry-After`, and unchanged SIMS invoice state. All synthetic receipt
    rows and the generated object were removed afterward.
    Production fail-closed smoke proved unauthorized 401s, authenticated
    validation, an empty safe candidate lookup, exact runtime/schema/config,
    and clean monitoring without writing a receipt.
  - **Classifier side path:** ripple-suite#197/PR #198 fixed the unrelated
    Knowledge policy baseline separately and is live through PR #200.
  - **SIMS staging prerequisite: COMPLETE.** Dedicated actor 2219, `Finch
    Ripple Integration (Staging)`, has zero roles, zero permissions, no staff
    profile, and a discarded random password. Ripple staging resolves that ID
    through protected configuration. It exists only for truthful technical
    attribution; the Finch human approver remains separate. Production uses
    the separate actor 345 with the same no-role/no-permission boundary.
- **Finch PR handoff (2026-08-01):** Finch PR #2058 is open against `staging`
  with the Sifu Edu-only entitlement, explicit invoice-or-map-later approval,
  durable leased export queue/retry, canonical Ripple multipart v2 request,
  honest remap/export status, permanent Playwright regression, and a staging
  runbook. Local governed evidence passed: 5,055 backend tests, 1,483 frontend
  tests, schema/migration/RC2 suites, builds, lint, pre-push, and exact
  previous-staging migration parity. All 11 final GitHub checks are green at
  head `c9e02078`. Codex did not merge, deploy, configure, distribute secrets,
  or activate production; Helmi owns those release decisions.
- **Verified staging state (2026-08-11):** Ripple PR #358 merged migration 105
  and downstream Finch-receipt invariants at `c5256a9c`; PR #359 moved staging
  to `a1206228`. GitHub delivered both staging pushes and the webhook accepted
  both with HTTP 202, but the installed `/usr/local/bin/deploy-ripple-suite`
  was older than the tracked controller and refused migration 105 after
  building the new application. A later PM2 restart loaded that newer build
  while migration 105, `finch_receipt_intake_requests`, and
  `collection_receipts.finch_approval_request_id` remained absent. The Finch
  routes currently fail closed with HTTP 503, but several ordinary finance
  mutation routes depend on the missing ledger. Production migration/source
  remain unchanged. Finch PR #2058 is still open, now at `e08d41b`; its prior
  11/11 GitHub checks belong to `c9e02078`, and the current head has no GitHub
  checks.
- **Staging recovery and lookup release (2026-08-15):** The August 11 blocked
  state is no longer current. Finch PR #2058 is merged, and Finch staging has
  the matching protected bearer/signing configuration with exactly one export
  gate set to `false`; the secrets remain distinct and were never exposed in
  chat or release evidence. Ripple issue #418/PR #419 repaired the remaining
  Finch v2 lookup contract drift and deployed to Ripple staging as `6087e6f4`.
  Fresh release evidence passed: 53 related tests, TypeScript, focused Biome,
  production build, coverage-manifest and guard checks, KVM8 deployment, PM2
  and public health, internal and public signed invoice-number lookups returning
  HTTP 200, and replay returning HTTP 409. Production was untouched. A critical
  impact audit found that the separate multipart receipt-upload endpoint still
  lacks the matching v2 signature verification, so lookup testing may resume
  but receipt export/canary activation remains blocked.
- **Representative fixture recovery (2026-08-15):** Read-only diagnosis proved
  `PINV-205820` still existed but was orphaned from its missing parent, so the
  healthy Ripple lookup correctly returned zero candidates. With Hafiz's
  staging-only invoice-data approval, SIMS staging received a protected,
  reversible fixture pack: three synthetic families/students, four matched
  requests, four attended classes, three unpaid invoices, and one paid
  negative-control invoice. Live signed internal/public checks now return one
  candidate for exact `PINV-205820`, two candidates for the multi-invoice phone
  family, and zero for the paid invoice. The authenticated Collections API
  returns all three unpaid invoices; the exact Customer Ledger source query
  returns all three families. Root-only rollback manifests are mode 600. Finch
  export remains false and production was not touched.
- **Lookup-only acceptance (2026-08-15):** Finch PR #2394 merged as
  `d5d51914`; Finch staging runs descendant `92c1e73a`. Helmi's natural
  staging journey using phone `0122222059` returned exactly `PINV-205821` and
  `PINV-205822`, allowed invoice selection, exposed no approval/export action,
  kept the document Pending, and created no export-ledger row. The export gate
  remains disabled and production integration remains inactive.
- **Receipt-upload signing execution (2026-08-15):** Hafiz approved the
  separate critical-lane safeguard through Ripple staging verification. Ripple
  issue #421 / PR #422 added tenant-bound v2 HMAC, timestamp/request identity,
  payload and exact receipt-byte digests, idempotency binding, and replay
  protection to `/api/finch/collection-receipts`. Commit `2f9706be` merged and
  deployed to staging as `169d125d`. Evidence passed: 66 focused tests,
  TypeScript, production build, changed-file Biome, coverage/guard checks, the
  frozen Finch cross-repository receipt vector, exact deployed identity,
  protected configuration invariants, deliberate missing-signature and
  tampered-byte rejection, a correctly signed request reaching safe business
  validation, and zero receipt-intake rows for the smoke reference. The deploy
  found no pending protected migrations and skipped database writes. Production
  remained on its prior SHA/process and Finch export stayed disabled.
- **Full staging capability acceptance (2026-08-16):** The real Finch document
  canary exported once to Ripple as `RCPT-4`; Finch stored Collection/Customer
  Receipt IDs 4/4, Ripple retained exact receipt/allocation/intake cardinality,
  signed replay returned the immutable first result, and Finch export returned
  to false. Because its RM10 allocation is intentionally partial, `RCPT-4`
  remained pending and `PINV-205821` remained unpaid. A separately authorised
  full-coverage final-leg canary used `RCPT-5` for RM240/RM240 on
  `PINV-205822`. Its first SIMS action failed closed on staging authentication;
  after the protected-key repair and a no-write impossible-invoice probe, Helmi
  retried exactly once. Independent Ripple database/audit/log and SIMS
  database/log evidence proves exactly one failed attempt followed by one
  success, one receipt allocation/payment/payment allocation, and one SIMS
  paid transition. `RCPT-4` and production were untouched. This is composite
  end-to-end capability proof rather than one receipt crossing all three
  systems, because the approved finance guardrail correctly forbids a partial
  receipt from marking an invoice paid.
- **Staging cron credential closure (2026-08-16):** The protected staging file
  and Ripple PM2 runtime held different cron values after a targeted restart,
  causing repeated 401s for both scheduled jobs. An automatic staging deploy at
  `9e33d925` reconciled runtime to the old protected value; Codex then completed
  the approved rotation to one new 64-character value, preserved
  `root:deploy 640`, restarted only staging, and observed natural 200 results
  from both workforce health and CRM poll. Public staging login and error logs
  remained healthy, no finance retry occurred, production config/process
  identity was unchanged, and the temporary rollback copy containing the
  retired value was removed.
- **Production lookup-only acceptance (2026-08-18):** Sifu Edu production
  invoice lookup is live through Finch → Ripple with the independent lookup
  gate true, while receipt export remains false. Matching protected/runtime
  configuration, typed tenant entitlement, signed empty technical lookup,
  Helmi's existing-Pending-receipt human journey, independent Finch/Ripple
  zero-row checks, exact deployed identity, runtime/public health, BetterStack
  4/4 and recent-log checks passed. No approval/export/SIMS action was exposed;
  the document stayed Pending and no Ripple receipt or SIMS write was created.
- **Production staff release acceptance (2026-08-20):** After a deliberate
  fail-closed rollback exposed the missing bounded lookup-reactivation path,
  Finch PRs #2622/#2623 added that operator and production was reactivated
  without changing the deployed application image. Independent evidence mode
  passed with lookup=true, export=true, exactly one eligible Sifu Edu
  subscription and active override, typed `sims_linkage_enabled=true` and
  `documents_enabled=true`, and a completely empty export ledger. Protected
  metadata remains `root:root 600`; Finch and Ripple are healthy, the canonical
  SIMS route is reachable with no recent API errors, Sentry is reachable, and
  BetterStack is 4/4 up. No receipt, Ripple allocation, or SIMS action was used
  for activation acceptance. Authorised staff may now use the workflow
  normally; a synthetic or mandatory live-customer release canary is not
  required because complete staging E2E already proved the financial journey.
- **Next action:** Helmi reviews and completes the ordinary-staff Finch → Ripple
  receipt guide in the in-app Help and printable PDF, using redacted current UI
  evidence and excluding secrets, protected configuration, deploy steps, and
  operator/rollback commands. After the guide is verified, routine production
  monitoring should observe the first organic staff receipt; this is normal
  operations, not a release blocker.
- **Promote to:** GitHub issue in finch-inbox (Finch dev, Helmi, implements
  independently) + direct implementation in ripple-suite/SIMS by Hafiz's own
  sessions (no separate dev handoff needed there — no SIMS code changes
  expected, ripple-suite gets the new endpoint + schema migration).
- **Links:** [ANALYSIS.md](../../products/finch-sims-integration/ANALYSIS.md),
  https://github.com/Sifututor/finch-inbox/issues/1734,
  https://github.com/Sifututor/finch-inbox/pull/2058,
  https://github.com/Sifututor/ripple-suite/pull/358,
  https://github.com/Sifututor/ripple-suite/pull/359,
  https://github.com/Sifututor/ripple-suite/issues/418,
  https://github.com/Sifututor/ripple-suite/pull/419,
  https://github.com/Sifututor/ripple-suite/issues/421,
  https://github.com/Sifututor/ripple-suite/pull/422,
  `.agent-os/session-maps/2026-08-11-181513-codex-ripple-staging-handoff-verification.md`,
  `.agent-os/session-maps/2026-08-14-235609-codex-finch-v2-lookup-pr.md`,
  `.agent-os/session-maps/2026-08-19-092242-codex-finch-production-export-canary.md`

### AO-CLAUDE-PARITY-002 — Complete portable Claude adapter parity

- **Project:** cross-project
- **Status:** active
- **Type:** mission
- **Parent:** none
- **End goal:** Extend the independently accepted Claude/Codex parity pattern
  beyond bootstrap, task-router, commit, save-session, and
  workflow-improvement: add thin installed Claude adapters and installed-path
  proof for handoff, snapshot, session-map, and quick-check; decide how
  machine-global adapters should be distributed or restored on another
  machine. The separate Codex pasted-report routing false positive was resolved
  through issue #32 and PR #33.
- **Why it matters:** Issue #30 proves the current machine behaves correctly,
  but those remaining adapter and portability gaps can still make another
  machine or a later workflow feel different. They should not be mixed into
  the already merged and accepted issue #30 delivery.
- **Source:** Issue #30 post-acceptance review, 2026-08-01.
- **Next action:** When Hafiz chooses to resume, route through
  `/workflow-improvement`, inspect the shared owner and existing installed
  paths, add failing fixtures first, then create a new GitHub issue for the
  handoff/snapshot/session-map/quick-check adapter or distribution slice. Keep
  Claude permissions/settings review separate and read-only unless Hafiz
  explicitly approves it.
- **Promote to:** New umbrella GitHub issue when Hafiz selects the first
  execution-ready slice.
- **Links:** https://github.com/hafizrazali90/sifututor-agent-os/issues/30,
  https://github.com/hafizrazali90/sifututor-agent-os/pull/31,
  https://github.com/hafizrazali90/sifututor-agent-os/issues/32,
  https://github.com/hafizrazali90/sifututor-agent-os/pull/33,
  `.agent-os/session-maps/2026-08-01-145916-codex-claude-agent-os-parity-audit.md`

### AO-CONTINUITY-001 — Native Agent OS work environment and continuity assistant

- **Project:** cross-project
- **Status:** active
- **Type:** mission
- **Parent:** none
- **End goal:** Give Hafiz one complete native work environment—comparable in
  role to VS Code, Claude Code, the Codex app, or Hermes—where he can perform
  the actual development and operational work through chat, inspect and edit
  code or documents, use terminals and tools, delegate to agents, review
  evidence, approve outward actions, and retain continuity across every
  project. The same environment also remembers active, paused, closed,
  deferred, and future work; recommends the next useful action; and highlights
  staff requests, reviews, approvals, or blockers waiting on Hafiz.
- **Why it matters:** Hafiz performs real development through agent chat, but
  the interface, sessions, memory, task state, evidence, and approvals are
  fragmented. Many concurrent and completed sessions make it impractical to
  remember every promise, return path, deferred idea, staff dependency, and
  approval. A reminder assistant alone does not solve this: the assistant and
  the place where the work is actually performed must be one coherent product.
- **Confirmed architecture:** The product is a Hermes-like native work
  environment with one persistent identity and memory across desktop/web and
  future phone, WhatsApp, or Telegram interfaces. Its desktop experience must
  support real task execution, including code/document inspection and editing,
  terminal and tool use, agent work, diffs, evidence review, and approval—not
  merely assistant chat or reminders. The workspace must run several
  independent task sessions concurrently, including multiple tasks from one
  project or across different projects. Each task session owns its own
  orchestrator conversation, project/worktree context, workers, evidence,
  state, and approval boundary; Hafiz can tile, focus, switch, and compare
  sessions visually without using a tmux-style terminal interface. Hafiz
  selected dockable task tabs with split/grid layouts on 2026-08-03, including
  a focus mode for one task and a control-room mode for several concurrent
  sessions. The Control Room uses full live chat lanes like Hafiz's current
  multi-chat VS Code layout, not summary-only cards: every lane has its own
  independently scrollable conversation and reply composer, while layout
  density, ordering, and the number of visible columns remain adjustable. A
  task can be continued directly from its control-room column or opened as a
  larger docked panel/focus workspace. Split Focus may keep two or more full
  task workspaces open side by side when Hafiz needs their editor, terminal,
  evidence, or worker context at the same time; this is distinct from the
  denser chat-first Control Room. Inside each focused task,
  the orchestrator conversation remains primary, a worker sidebar shows live
  worker status and evidence, optional worker detail sub-views provide deeper
  inspection, and only meaningful worker events enter the main chat. Hafiz
  selected risk-based cross-task attention on 2026-08-03: normal progress only
  changes task badges, a global `Needs you` rail collects approvals, questions,
  failures, and completed work, the application never steals active-task focus,
  genuine blockers or critical events receive a clear banner, and non-urgent
  updates wait for a digest. Hafiz selected natural-language smart start on
  2026-08-03: starting a task should feel like the current VS Code chat
  workflow—open a chat, describe the work naturally, and continue through the
  conversation. Project and workflow detection happen behind the chat, with a
  small correctable understanding summary and a question only when the request
  is genuinely ambiguous; there is no mandatory setup wizard. Hafiz selected
  same-chat smart resume on 2026-08-03: reopening a task returns to its complete
  persistent conversation and adds a compact, collapsible resume card showing
  its goal, last completed work, freshly verified state, branch/worktree,
  workers, waiting items, and one recommended next action. The card helps Hafiz
  reorient without replacing or splitting the original transcript. Hafiz
  selected assisted close-and-archive on 2026-08-03: when work appears finished,
  the orchestrator prepares a freshness-checked close-out showing what changed,
  evidence, exact local/pushed/merged/deployed state, remaining work, and
  follow-ups. Hafiz chooses `Close`, `Keep open`, or `Create follow-up`; the
  product never silently closes the task. Closed tasks leave active views but
  remain searchable and can reopen with their full conversation. Hafiz selected
  a visible goal-based finish line on 2026-08-03: the orchestrator infers and
  displays one small editable target from the natural conversation, such as
  design approved, local fix verified, PR opened, or production monitored. It
  does not require a setup form, and the task cannot claim completion until the
  stated target is reached or Hafiz explicitly accepts a named exception. Hafiz
  selected one persistent Agent OS orchestrator identity on 2026-08-03: Hafiz
  talks to the same assistant relationship across tasks while Codex, Claude,
  and future providers operate as visible, replaceable engines and specialist
  workers underneath. Conversation, memory, workflow, and task identity belong
  to Agent OS rather than one provider; the interface shows active models and
  allows an override without fragmenting the task. Hafiz selected layered
  scoped memory on 2026-08-03: personal preferences and working rules,
  project knowledge, full task context, and cross-project responsibility state
  remain distinct ownership layers. The orchestrator can connect relevant,
  source-labelled knowledge, but must not casually mix raw chats, files, or
  private context from unrelated projects. This preserves the current Agent OS
  memory architecture while making its retrieval and boundaries automatic and
  visible. Hafiz selected transparent smart delegation with calibrated
  learning on 2026-08-03: routing begins from a conservative configured worker
  registry, verifies current capabilities, matches workflow stage and risk,
  and measures exact-scope completion, evidence, review findings, corrections,
  time, and available usage data. Bounded preference tuning may happen
  automatically with visible reasons and rollback, but new providers,
  spending, access, critical-work eligibility, safety changes, or material
  self-rewrites require Hafiz's approval. Unknown usage stays unknown, and a
  worker's completion claim never substitutes for evidence or independent
  review. Hafiz selected quality-floor, usage-aware routing on 2026-08-03 and
  supplied the initial profile: Codex is his usual default orchestrator engine,
  Claude is preferred for research, and a proven non-frontier worker may handle
  routine mechanical work such as applying prepared documentation or Koda
  updates. Routing follows the judgment and evidence required rather than the
  artifact name alone: deciding what belongs in memory or authoring a major
  design may still require a stronger worker. The profile is deliberately
  incomplete and should be configured progressively from Hafiz's corrections
  and measured outcomes, while quality, safety, and critical-lane requirements
  override usage conservation. Hafiz clarified on 2026-08-03 that starting a
  task must also expose a direct orchestrator-engine selector. The stable
  identity remains Agent OS, but Hafiz can choose `Auto`, Codex, Claude, or
  another connected model before the first message without entering a setup
  wizard; the interface remembers his usual default, currently Codex, and the
  selected engine remains visible and overridable per task. Availability still
  depends on verified authentication and capability, and manual selection does
  not bypass delegation or safety policy. Hafiz confirmed the combined routing
  configuration on 2026-08-03: he can change preferences naturally in chat,
  permanent rules remain inspectable, editable, source-labelled, and
  reversible on a visible policy page, and the start-time selector provides
  temporary per-task overrides without rewriting those defaults. Specific
  model variants are selectable when a connected provider exposes them. Hafiz
  selected explicit assisted failover on 2026-08-03: a manually pinned
  orchestrator never switches silently and instead offers wait, provider/model
  fallback, or `Auto` choices. An `Auto` task may switch inside the approved
  quality/capability pool, but it must disclose and log the change while
  preserving the same task and transcript; critical work or a material quality
  downgrade still requires approval. Hafiz selected a chat-first adaptive
  Focus Workspace on 2026-08-03: the orchestrator conversation remains the
  primary task history, while editor/document, diff, evidence, optional file
  explorer, terminal/log drawer, and Worker Sidebar open beside or below it as
  needed. Panels are dockable, resizable, pinnable, and remembered per task;
  opening a technical surface never creates a separate task or loses the chat,
  and Split Focus can show multiple complete workbenches. Hafiz selected smart isolation on
  2026-08-03: a discussion can begin
  without Git
  setup, but when it becomes coding work the system automatically creates or
  attaches the session's dedicated project worktree and branch, following the
  existing parallel-work safety rule without making Hafiz manage Git folders
  manually. Agent OS owns orchestration; Claude is the default heavy worker,
  while Codex and other models remain selectable by task fit, cost, risk, and
  availability. The first usable version will include the desktop application
  plus Telegram. WhatsApp is deferred until the core assistant works and its
  platform/reliability options are separately reviewed.
- **Source:** Hafiz product-vision clarification, 2026-08-02.
- **Current design state:** The Hermes foundation fit-test Product Shape is
  drafted and Hafiz approved the fully isolated Option C on 2026-08-02. A fresh
  official update check found the live v0.14.0 checkout 11,371 commits behind
  `origin/main`; no update was installed. The preflight selects the immutable
  stable tag `v2026.7.30` (Hermes Agent v0.19.1), which matches the installed
  Node/Python toolchain, instead of moving `main`. It requires a separate
  current-version checkout and disposable
  Hermes home, one complete real development journey inside the native work
  surface, Agent OS approval/evidence behavior, reviewed session continuity,
  responsibility awareness, and isolated Telegram delivery. It defines the
  evidence and failure conditions that choose upstream extensions, a
  Sifututor-owned shell, a narrow desktop fork, or a separate build.
- **Fit-test checkpoint:** The isolated v0.19.1 native desktop passed the
  account-free interface checkpoint with Hermes's local mock provider. It
  grouped chat under the disposable project, exposed project files and
  preview/source/diff/edit controls, and ran `npm test` in its embedded terminal
  with 3 passing tests and 0 failures. This proves a promising integrated work
  surface, not actual AI development. The sandbox also revealed a required
  security design item: state isolation did not stop the Projects view from
  discovering unrelated home-directory project names, so production use needs
  explicit workspace allowlisting or stronger process isolation.
- **Provider boundary:** Hafiz requires subscription authentication rather than
  an API key. The recommended fit-test path is a fresh ChatGPT/Codex device
  login stored only in the isolated Hermes auth store; never import the current
  Codex credential files. Current Hermes documentation says ordinary Claude
  subscription allowance is not available through Anthropic OAuth: that path
  requires Claude Max plus separately purchased extra-usage credits.
- **Auth checkpoint:** A fresh ChatGPT/Codex device login completed through the
  isolated launcher. Hermes detected existing Codex credentials, but their
  import was explicitly declined. The isolated profile now contains its own
  subscription OAuth login and passed an exact connectivity check.
- **Real-agent checkpoint:** The fresh isolated OAuth login completed without
  importing existing Codex credentials. Hermes selected `gpt-5.6-sol`, stopped
  for approval before editing, then completed a two-file RED/GREEN task with
  4/4 tests, patch evidence, no staging, and a continuity record. Its background
  review also demonstrated Hermes's valuable self-improvement capability by
  generating a new skill. Hafiz confirmed this is a feature to preserve. The
  isolated config currently enables Hermes's review-before-activation mode, and
  a harmless probe proved new skill writes remain pending and inactive; the
  remaining product choice is whether activation should stay review-first or
  become automatic after the capability earns trust. Initial inspection of the
  generated skill found it relevant and well structured, including separate
  approval boundaries, RED/GREEN behavior, exact-scope evidence, and correct
  handling of an untracked repository.
- **Continuity checkpoint:** Hafiz approved the exact seven-file local fixture
  commit `fc3093f`, excluding `.hermes-sandbox/`; nothing was pushed. A fresh
  Hermes project session then opened and recovered the correct project, goal,
  implementation, 4/4 tests, next boundary, and sandbox warning from the two
  approved continuity files. It also repeated the stale pre-commit Git state
  because `.agent-os/continuity.md` had been written before the commit. This is
  a state-freshness gap, not a failure of project/session recovery.
- **Continuity correction:** Hafiz approved the shared post-boundary refresh
  rule. `save-session.md` now requires refreshing continuation packs after
  commit, push, PR, merge, deploy, live checks, approval-boundary changes, or
  later evidence, and requires fresh state verification on resume. After the
  disposable pack was refreshed, a brand-new Hermes chat correctly reported
  `main`, latest commit `fc3093f`, the unstaged continuity change, untracked
  `.hermes-sandbox/`, nothing staged, no remote, local-only/unpushed state, and
  the approval boundary. It made no changes. Desktop continuity now passes.
- **Telegram Phase A:** The isolated profile currently has no Telegram token,
  allowed-user list, or home channel. Use a new manual `@BotFather` test bot,
  restricted to Hafiz's numeric user ID, rather than Nous-managed onboarding or
  the live bot. A read-only status check proved that global `hermes gateway`
  service commands resolve the protected live launchd service at PID 2397.
  Therefore the isolated checkpoint must never call gateway start, restart,
  stop, install, or replace. After private bot setup, run the exact current
  checkout through the sanitized wrapper in foreground `gateway run --force`
  mode; the separate bot identity avoids the duplicate-token lock.
- **Telegram connected checkpoint:** Hafiz privately configured a separate bot
  token and numeric allowlist. Presence-only checks confirmed both without
  exposing values; the optional home channel remains unset. Codex started the
  exact current checkout through the sanitized wrapper in foreground
  `gateway run --force` mode. Isolated PID 84865 connected to Telegram in
  polling mode with secret redaction enabled and one active platform. The live
  gateway remains separately running at PID 2397 and was not restarted.
- **Telegram round-trip checkpoint:** The controlled phone prompt passed.
  Hermes read only the two approved fixture continuity files, returned the
  correct goal and exact next action, and accurately distinguished local commit
  `fc3093f`, the modified unstaged continuity record, the untracked sandbox,
  nothing staged, and no remote. Fresh Git checks matched its response. The
  same project, sessions, files, and terminal evidence remained available in
  the native desktop. Isolated PID 84865 then stopped cleanly while protected
  live PID 2397 remained running.
- **Privacy-hardening findings:** Routine gateway logs include the numeric
  Telegram chat/user identifier, and the native Messaging screen only partially
  masks the stored bot token. No value was retained in docs or Koda, and the
  credential-bearing temporary screenshot was deleted. Production adoption
  requires identifier redaction and full secret concealment in the UI and
  accessibility tree.
- **Responsibility checkpoint:** A bounded native-desktop test used one
  explicitly fictional local fixture. Hermes kept current work, waiting on
  Hafiz, staff blocked, and deferred work separate; linked the staff blocker to
  its approval; prioritized the approval because it unblocked staff; preserved
  real repository boundaries; and performed only file reads. This proves
  reactive classification from structured state.
- **Responsibility Inbox design:** A design-only Product Shape now defines a
  linked read model over Session Maps, Mission Ledger, GitHub, active task
  files, and Planner. The proposed inbox owns only attention metadata such as
  seen and snoozed state; it does not replace the sources that own task truth.
  It uses deterministic priority tiers, material-change notifications,
  script-first collection, desktop inspection, and quiet Telegram delivery.
  Hafiz approved this linked read-model authority on 2026-08-03. A first PRD
  and UX spec now translate the direction into the Today screen,
  responsibility detail, active work handoff, source health, and Telegram
  digest/alert journeys. Hafiz selected smart landing on 2026-08-03: open Today
  for a fresh start, but return to the active workspace when continuing recent
  work. Hafiz selected the recommended Telegram threshold on 2026-08-03:
  interrupt immediately only for a newly blocked person, an
  approved critical/time-sensitive threshold, or a material increase in
  impact; ordinary changes wait for the digest. The next decision is how
  deferred work without a date should return. Hafiz selected smart resurfacing
  on 2026-08-03: honor explicit timing, propose a review time when none is
  given, and use a quiet weekly safety review so undated work cannot disappear.
  The next decision is how possible promises found in old chats should be
  handled. Hafiz selected a private `Needs confirmation` queue on 2026-08-03:
  old-chat candidates show their original context and do not become real
  responsibilities until Hafiz keeps and promotes them. The next decision is
  which actions the assistant may perform directly from the Inbox or Telegram.
  Hafiz selected staged actions based on risk on 2026-08-03: personal attention
  actions happen directly, while source-system and outward actions retain
  previews and existing approval gates. Hafiz then selected an A+C hybrid for
  Telegram approvals on 2026-08-03: any class of action may be approved from
  the phone, but evidence and confirmation must scale with risk, existing
  critical and per-operation gates remain intact, and the flow falls back to
  desktop whenever the required evidence cannot be shown safely on mobile.
  Tool access alone never counts as approval. The major first UX decisions are
  complete; the next recommended artifact is a visual prototype. This remains
  product design only; implementation is not approved.
- **Current blocker:** Proactive responsibility awareness is not yet proven.
  Hermes has not automatically discovered responsibilities across projects,
  sessions, GitHub, Mission Ledger, or staff intake, detected overdue items, or
  alerted Hafiz before a dependency is missed.
  The token must not be pasted into chat, docs, logs, Koda, or Git. The
  generated active skill, review-first activation policy, and accidental
  untracked disposable `.hermes-sandbox/` remain preserved; none may be deleted
  or activated differently without explicit approval.
- **Next action:** Hafiz reviews the local visual prototype at
  `.agent-os/session-maps/artifacts/responsibility-inbox-ux-review-2026-08-03/index.html`,
  covering Today, low-risk Telegram approval, high-risk mobile evidence and
  confirmation, desktop fallback, and return to active work. Revise the UX
  direction from his feedback before implementation.
  Do not copy from, upgrade, restart, or reconfigure the live Hermes
  installation, and do not push or deploy the disposable fixture.
- **Channel research:** Hermes Agent's current WhatsApp support does not use
  Meta's official Business Cloud API. It uses a Baileys bridge that emulates a
  linked WhatsApp Web session, with either a dedicated bot number or personal
  self-chat. Hermes itself warns about account-restriction risk and temporary
  breakage after WhatsApp protocol updates, so copying this approach requires
  an explicit reliability and policy decision.
- **Foundation research:** Hermes is a strong candidate foundation rather than
  only a visual reference. Its current MIT-licensed project already provides a
  shared desktop/messaging agent, persistent searchable sessions, curated and
  provider-backed memory, projects spanning multiple folders, scheduled jobs,
  Telegram delivery, a durable multi-project Kanban/dispatcher, Claude and
  Codex provider paths, editor integration through ACP, and extension points
  for skills, plugins, model providers, and custom UIs. Its desktop currently
  offers file browsing/preview and agent-produced diffs, not a confirmed full
  VS Code replacement. The preferred experiment is therefore upstream Hermes
  plus a removable Sifututor Agent OS integration; avoid a long-lived full fork
  until usage proves that a core or desktop change is unavoidable.
- **Existing Hermes baseline:** A read-only check on 2026-08-02 confirmed the
  Mac already runs Hermes v0.14.0 with its launchd gateway active. The upstream
  checkout is 381 commits behind and contains a local `cron/scheduler.py`
  customization that converts raw scheduled-job failures into concise Telegram
  alerts. Do not upgrade this live installation in place. Preserve it while a
  separate current-version test profile/install is used for the foundation fit
  test, and explicitly carry or replace the local alert behavior before any
  later migration.
- **Promote to:** Umbrella GitHub issue only after the Product Shape and first
  usable slice are approved.
- **Links:** `docs/agent-playbooks/agent-os-native-work-environment-fit-test.md`,
  `docs/agent-playbooks/agent-os-responsibility-inbox-product-shape.md`,
  `docs/agent-playbooks/agent-os-responsibility-inbox-prd.md`,
  `docs/agent-playbooks/agent-os-responsibility-inbox-ux-spec.md`,
  https://github.com/hafizrazali90/sifututor-agent-os/issues/34,
  Koda `mem_976c838f13fe`; related runtime investigation
  `AO-RUNTIME-001` remains a technology candidate, not the product definition.

### AO-RUNTIME-001 — Evaluate Omnigent as staff-distributable Agent OS runtime

- **Project:** cross-project
- **Status:** active
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
- **Current state:** Checkpoint 4 remediation passed on 2026-08-03. Codex made
  guard and verification evidence depend on observed successful results,
  enforced the exact guard and staged bundle, hard-denied commit broadening and
  hook bypass, completed Claude/Codex/data/PID/worktree isolation, confined
  shell and secret access, added scoped critical-lane reset, and corrected the
  external adapter seam. Successive isolated Claude reviews found the remaining
  unspaced redirect, `sed --in-place`, and valued
  `--pathspec-from-file=...` gaps; each was fixed with a fixture that reaches
  the intended rule. Claude's final read-only confirmation returned GO in
  `5b1f9d9c00df4c3187acd170b05af39e`. The final affected suite passed
  `1781/1781`, the focused final policy/runtime suite passed `196/196`, and
  Ruff, focused mypy, and `git diff --check` passed. Review-only processes were
  stopped, ports `17677` and `6767` were closed, and the policy database was
  restored to fixture-only sandbox and working-directory roots. Nothing was
  staged, committed, pushed, opened as a PR, forked, deployed, or used against
  a product repository. Remaining candidate gaps are runtime reliability and
  usability: final responses can outlive a failed runner status, strict
  read-only review conflicts with Claude plan-file writes, compound read syntax
  can cause approval friction, and host roots must be explicit at launch.
  A first Checkpoint 5 attempt then found a critical authentication defect
  before any model response or Koda call: `--use-native-config` is dropped on
  the remote host/runner path, which re-resolves the configured Anthropic
  provider and embeds its static credential inside an `apiKeyHelper` in
  Claude's process argv. The trial stopped, all processes and ports were
  closed, fixture-only policies were restored, no synthetic Koda memory was
  written, and the isolated logs contained no matching credential pattern.
  Because process inventory captured the value, the affected credential must
  be rotated. Hafiz then approved a local critical remediation: the native-login
  choice now survives remote spec translation, while static keys use an atomic
  owner-only file and never enter Claude settings argv. Focused native-Claude,
  title, translation, and runner suites passed (`187/187` and `105/105`), plus
  Ruff, byte-compilation, and `git diff --check`. Credential rotation was then
  confirmed, expanded suites passed (`564 + 228 + 114`), and two independent
  read-only Claude reviews accepted the correction. A separately approved live
  retest on 2026-08-04 proved the main runner uses the isolated Claude Max
  subscription and that a configured fake-provider sentinel is absent from
  argv, logs, databases, and provider-secret artifacts. The full continuity
  journey still failed: server-accepted approvals did not resume the waiting
  test/Koda commands; Claude did not receive Sifututor as a scoped read
  directory; the background-title helper still resolved the configured
  provider endpoint; and Omnigent skipped 15 Claude skills due to stricter YAML
  frontmatter parsing. The final Claude report was honest but lacked test,
  Koda, and Mission Ledger evidence. All isolated processes stopped, port
  `17677` closed, but a completed no-socket `tmux` server outlived normal
  shutdown and required exact PID-scoped `SIGTERM`; the final inventory then
  showed zero isolated processes. Nothing was staged, committed, pushed,
  deployed, or used against a product repository. A separately approved
  fixture-first remediation on 2026-08-04 then closed all five live blockers.
  One accepted Agent OS approval resumed and executed the exact pytest-version
  command without the prior duplicate harness `404`; Claude read this Mission
  Ledger through propagated `--add-dir` authority; Omnigent exposed 49 host
  skills including `workflow-improvement`; the automatic title worker reused
  the main session's native subscription route (`configured=False`, no provider
  env/helper/model); and two normal session stops left no Claude or tmux
  process. The final focused suite passed `351/351`; Ruff, byte-compilation,
  and `git diff --check` passed; an additional broad run reached 690 passes and
  four expected xfails with no unexpected failure before it was stopped for
  runtime. Port `17677` and all isolated server/host/runner/Claude/tmux
  processes were closed. Nothing was staged, committed, pushed, opened as a
  PR, deployed, installed for staff, or used against a product repository.
- **Checkpoint 6 interface result:** A dedicated local Omnigent web route now
  proves the confirmed Control Room, Focus Workspace, Worker Sidebar, Split
  Focus, and Needs You interaction shape with fictional fixtures. Focused UI
  tests passed `5/5`; TypeScript type-check and production build passed; four
  browser views were inspected. This proves client feasibility, not live data
  integration. Nothing was staged, committed, pushed, deployed, or connected
  to a real product, staff user, model session, or responsibility source.
- **Foundation decision (2026-08-04):** Hafiz selected Omnigent itself as the
  complete v1 code and interface baseline instead of mixing or independently
  recreating several donor designs. Preserve the upstream application,
  desktop shell, session interface, editor, and interaction language; add
  Sifututor Agent OS capabilities as Omnigent-native extensions. Retain the
  Apache-2.0 licence and required attribution, and keep upstream trademarks
  separate from Sifututor product branding.
- **Checkpoint 7 product-baseline result:** A clean worktree from current
  Omnigent `origin/main` preserved the complete upstream interface and loaded
  Sifututor's Agent OS through an external adapter package. The focused adapter
  suite passed `146/146`; Ruff and `git diff --check` passed; the upstream
  runtime baseline reached `927/929`, with only two pre-existing macOS path
  assumption failures. One real Codex-subscription conversation
  `6700725bd60643ffbf7f36a7058f537c` ran and resumed through the original web
  interface, read the shared contract and Session Map, checked fresh Git and
  Koda state, and made no Sifututor write. The policy API returned ALLOW for a
  safe shell action. A live compatibility defect was caught and fixed before
  success: Omnigent 0.8 dropped factory arguments from the documentation-style
  `handler` plus `factory_params` server-policy form, so the adapter now uses
  native `function.path` plus `function.arguments` with a regression test.
  Screenshot evidence is at
  `/Users/hafizrazali/Projects/Omnigent-worktrees/agent-os-product-baseline/evidence/omnigent-original-ui-real-session.png`.
  The local server and its four exact isolated helper processes were stopped,
  and port `18677` was closed.
  The exact nine-file adapter bundle was then committed locally as `8aba4b8c`
  (`✨ feat(policies): add Sifututor Agent OS adapter`) after the shared guard,
  staged inventory comparison, Omnigent staged pre-commit hooks, and the final
  `146/146` focused test run passed. Hafiz then approved the backup boundary:
  Codex created https://github.com/hafizrazali90/omnigent and pushed only
  `feat/agent-os-product-baseline`. The remote branch points exactly to
  `8aba4b8c`; no PR exists on the fork or upstream. Fresh upstream `main` advanced by
  two unrelated commits after the baseline, with no changed-path overlap, so
  the backup branch is intentionally preserved and must be reconciled on a new
  current-upstream work branch before a later PR. Nothing was installed for
  staff or deployed.
- **Checkpoint 8 Control Room result:** The first real product slice is built
  and checked locally in
  `/Users/hafizrazali/Projects/Omnigent-worktrees/agent-os-control-room/source`
  on `feat/agent-os-control-room`, based on current upstream `b2b1002e` with
  the proven adapter carried forward as `57b21863`. The native
  `/control-room` route renders genuine Omnigent sessions as parallel task
  lanes, shows worker/activity/attention state, and opens each task in the
  unchanged `/c/:id` conversation workspace. Issue #35 tracks the slice.
  Five focused page tests and a sidebar-route regression pass; the full web
  suite passed `4883` tests with three expected negatives and one skip;
  TypeScript, Oxlint, Prettier, Ruff, production build, and `git diff --check`
  passed. A permanent Playwright journey created two real sessions through the
  API, rendered both lanes, opened one, and reached the original composer; a
  browser screenshot was inspected. The shared guard and repository
  pre-commit hooks passed, and the exact seven-path bundle was committed as
  `e34926fc` (`✨ feat(web): add real multi-session control room`). The clean
  local branch and `hafiz/feat/agent-os-control-room` both point to the exact
  full SHA `e34926fc4655cb2eed95514d45bc8e256dcf74ef`; no PR, staff
  installation, product access, KVM, or deployment action exists.
- **Checkpoint 9 direct-reply result:** A session-keyed lightweight state
  boundary now lets multiple real Control Room lanes show their own recent
  transcript and accept separate replies without mounting Omnigent's singleton
  full-workspace chat store. The permanent Playwright journey sent distinct
  messages through two real lanes and verified both the visible UI and each
  session's server history stayed isolated. Focused tests passed `71/71`; the
  full web suite passed `4,888` with three expected negatives and one skip;
  TypeScript, Oxlint, Prettier, production build, Ruff, `git diff --check`, and
  screenshot-backed visual inspection passed. Issue #36 tracks the slice.
  The exact five-file bundle is committed and pushed as `a899eaf8`; the clean
  local branch and `hafiz/feat/agent-os-control-room-chat` match exactly. No PR,
  installation, or deployment exists.
- **Checkpoint 10 Worker Sidebar result:** Issue #37 and local branch
  `feat/agent-os-worker-sidebar` track the fully checked five-file slice from
  pushed Checkpoint 9. Omnigent's existing Agents rail now adds real
  focused-task, active-worker, status, changed-file, checklist-progress,
  pending-input, and approval-boundary context instead of duplicating worker
  state. Focused tests passed `188/188`; the full web suite passed `4,889`
  with three expected negatives and one skip; TypeScript, Oxlint, Prettier,
  production build, Ruff, byte-compilation, `git diff --check`, the permanent
  real-session Playwright journey, screenshot inspection, repository hooks,
  and the shared guard passed. The exact five-file bundle is committed and
  pushed as `44daa286`; the clean local branch and
  `hafiz/feat/agent-os-worker-sidebar` match exactly. No PR, installation, or
  deployment exists.
- **Checkpoint 11 Split Focus result:** Issue #38 and local branch
  `feat/agent-os-split-focus` track a fully checked ten-path slice from pushed
  Checkpoint 10. The native `/split-focus` route opens two complete same-app
  workspaces by default and up to four side by side, keeps each session in its
  own browser realm so the singleton chat store cannot cross-contaminate panes,
  preserves the normal chat/files/terminal/Worker Sidebar, and restores pane
  selection after reload. Focused tests passed `166/166`; the full web suite
  passed `4,896` with three expected negatives and one skip; TypeScript,
  Oxlint, Prettier, production build, Ruff, byte-compilation,
  `git diff --check`, repository hooks, and the shared guard passed. The
  permanent real-session Playwright journey proved separate messages stayed in
  their intended server histories and restored after reload; after its
  persistence wait was hardened, it passed three consecutive final runs. A
  real browser screenshot was inspected. The exact ten-path bundle is committed
  and pushed as `274668be`; local and
  `hafiz/feat/agent-os-split-focus` match exactly. No PR, installation, or
  deployment exists.
- **Checkpoint 12 Needs You result:** Issue #39 and branch
  `feat/agent-os-needs-you` evolve Omnigent's existing cross-session
  approval/comment Inbox instead of creating a competing task database. The
  native `/needs-you` surface keeps real approvals and comments, adds
  non-duplicated failed and unseen-completed session attention, preserves the
  legacy `/inbox` route, clears completed attention when its task is opened,
  and routes multi-session native notifications to the same source of truth.
  Focused tests passed `150/150`; the full web suite passed `4,901` with three
  expected negatives and one skip; TypeScript, Oxlint, Prettier, production
  build, Ruff, byte-compilation, `git diff --check`, shared guard, and repository
  hooks passed. Permanent browser journeys proved completed-task attention,
  clear-on-open behavior, real approval resolution, and legacy-route approval
  re-parking; a trace screenshot was inspected. The exact 13-path bundle is
  committed and pushed as `177392a7`; local and
  `hafiz/feat/agent-os-needs-you` match exactly. No PR, installation, staff
  trial, external source, Telegram action, or deployment exists.
- **Checkpoint 13 Continuity Bridge result:** Issue #40 and branch
  `feat/agent-os-continuity-bridge` add an opt-in generic Omnigent extension
  seam plus a Sifututor-owned read-only adapter. A focused task can show Goal,
  Now, Next, and unresolved Mission Ledger follow-ups in its existing Worker
  Sidebar using the exact `agent_os.session_map` label. The adapter validates
  that pointer against the configured Session Map directory, rereads the
  original files on every request, returns only relative source paths, and
  refuses to guess from the most recently edited map when several sessions run
  in parallel. Focused tests passed `15/15`; broader policy/server tests passed
  `1,153/1,153`; the full web suite passed `4,905` with three expected
  negatives and one skip; type, lint, format, build, Ruff, mypy,
  byte-compilation, diff, shared guard, repository hooks, permanent browser
  journey, and screenshot inspection passed. The exact 14-file bundle is
  committed and pushed as `d9aeabfa`; local and remote match. No PR, merge,
  installation, staff trial, Telegram, external-source write, product access,
  KVM, or deployment exists.
- **Checkpoint 14 Continuity Linking result:** Issue #41 is implemented and
  pushed in two isolated branches. Omnigent commit `d15abfe6` exposes only the
  non-secret current chat id/server address to native Claude and Codex and adds
  `agent-os-link-continuity`; the helper accepts no session-id override,
  validates one exact source-relative map before PATCH, confirms the saved
  label, and leaves Session Map and Mission Ledger bytes unchanged. Shared
  Agent OS commit `fdb5753` makes that invocation part of the Session Map
  workflow after the router has selected or created the exact map. Focused
  tests passed `20/20`; policy/server `1,162/1,162`; relevant native runner
  tests `115/115`; static checks, package entry-point proof, Session Map
  checker, hooks, and guards passed. Local and remote SHAs match. No PR,
  merge, installation, staff trial, permission change, or deployment exists.
- **Checkpoint 15 Continuity Freshness result:** Issue #42 is implemented and
  pushed as exact seven-file Omnigent commit `1d266eee`. The focused task
  refreshes every 15 seconds only while open, rereads the same explicit Session
  Map pointer, and shows the newest modification time across its linked map and
  configured Mission Ledger sources. The permanent browser journey proved
  changed source content appeared in the same open task without reopening it.
  The full web suite passed `4,906` with three expected negatives and one skip;
  broader policy/server tests passed `1,163/1,163`; focused, type, lint, format,
  build, Ruff, mypy, byte-compilation, diff, hook, and guard checks passed.
  Local and remote SHAs match. No PR, merge, installation, staff trial,
  permission change, Telegram action, or deployment exists.
- **Checkpoint 16 Smart Start result:** Issue #43 is implemented and pushed in
  two isolated branches. Exact nine-file Omnigent commit `e4301dff` adds the
  editable Worker Sidebar understanding card and `agent-os-set-understanding`;
  exact one-file Agent OS commit `ef19ada` adds the shared Task Router
  instruction. A correction updates the same task and is sent as a visible user
  message into the same orchestrator conversation. Focused helper/package tests
  passed `13/13`; broader policy/server tests `1,170/1,170`; focused Worker
  Sidebar tests `111/111`; full web `4,908` plus three expected negatives and
  one skip; permanent browser E2E `1/1`; static, package, parity, readiness,
  response, state, hook, and guard checks passed. Both local/remote SHA pairs
  match. No PR, merge, installation, staff trial, permission/authentication
  change, Telegram action, or deployment exists.
- **Checkpoint 17 Task Finish Line result:** Issue #44 is implemented and
  pushed in two isolated branches. Exact seven-file Omnigent commit `43e62c79`
  extends the existing understanding helper/card with one bounded, editable
  practical finish line; exact one-file Agent OS commit `6f4a194` derives it
  from the existing Execution Depth decision and explicitly preserves stricter
  approval boundaries. Corrections update the same task and worker
  conversation. Focused helper tests passed `9/9`; focused Worker Sidebar
  `66/66`; broader policy/server `1,172/1,172`; full web `4,908` plus three
  expected negatives and one skip; permanent browser E2E `1/1`; static,
  package, parity, readiness, response, state, hook, and guard checks passed.
  Both local/remote SHA pairs match and both worktrees are clean. No PR, merge,
  installation, staff trial, permission/authentication change, Telegram
  action, or deployment exists.
- **Checkpoint 18 Proven State result:** Issue #45 is implemented and pushed
  in two isolated branches. Exact nine-file Omnigent commit `cf6c4352` adds
  `agent-os-set-proven-state` plus a separate Current Proof and bounded evidence
  display beside the task finish line. Exact four-file Agent OS commit
  `1b650a3` initializes honest routed state, requires updates from fresh owner
  evidence, and adds fixtures that reject claiming a higher finish line was
  reached. Focused helper tests passed `21/21`; focused Worker Sidebar `66/66`;
  broader policy/server `1,178/1,178`; full web `4,908` plus three expected
  negatives and one skip; state fixtures `18/18`; permanent browser E2E `1/1`;
  static, package, workflow-doctor, hook, and guard checks passed. Both
  local/remote SHA pairs match and both worktrees are clean. No PR, merge,
  installation, staff trial, permission/authentication change, Telegram
  action, or deployment exists.
- **Consolidation acceptance result:** Checkpoints 8–18 were reviewed together
  against cumulative Omnigent `cf6c4352` and shared Agent OS `1b650a3`.
  Nine combined browser journeys and 163 focused web tests passed. The C18
  branches are the recommended maintained pilot baseline, but three integration
  gaps block PR/install: Control Room omits finish-line/current-proof truth;
  Control Room and Split Focus silently stop at the first 30-session page; and
  Control Room lacks Hafiz's requested column, density, search, and ordering
  controls. The Worker Sidebar hierarchy and one assembly-level E2E should be
  corrected in the same bundle when they remain small. Full report:
  `.agent-os/session-maps/artifacts/native-agent-os-consolidation-review-2026-08-04/acceptance-review.md`.
- **Consolidation correction result:** Exact nine-file Omnigent commit
  `503af0b65d340f015e2c7a50260f1cd47e99233d` is pushed and open as
  [Omnigent PR #1](https://github.com/hafizrazali90/omnigent/pull/1) against
  `feat/agent-os-proven-state`. It adds Control Room finish-line/current-proof
  truth, `Idle` status, search, explicit older-task loading, column/density/order
  controls; Split Focus search and older-task loading; one Worker Sidebar Task
  Brief; and one permanent four-surface browser journey. The full web suite
  passed `4,912` with three expected negatives and one skip; five focused
  browser journeys, type-check, focused lint/format, production build, Ruff,
  diff check, shared guard, and screenshot-backed visual QA passed. The broad
  local Python command stopped during collection because the optional
  Databricks SDK is absent; no affected test failed. GitHub reports the PR
  mergeable and no automated checks, so CI is unrun. No merge, installation,
  staff trial, Telegram action, or deployment occurred.
- **Isolated personal installation result:** Omnigent PR #1 is merged as exact
  commit `7d749f58265dd2a2aac8299fba3f084179a4be9f`. A detached local installation
  under `/Users/hafizrazali/Projects/Omnigent-pilots/agent-os-local-pilot`
  runs the native desktop and server on `127.0.0.1:18767` with separate config,
  data, database, artifacts, logs, desktop profile, update setting, and macOS
  service definitions. Desktop tests passed `221/221`; focused workspace UI
  tests passed `81/81`; Control Room, Split Focus, and Needs You route checks
  returned 200; a stop/unload/restart cycle passed; and native screenshots
  proved Control Room and Split Focus. A local one-file desktop overlay disables
  global `omnigent://` registration. Normal `~/.omnigent` and Claude/Codex
  authentication were not imported or changed. The pilot remains running;
  rollback instructions are in the installation README. This is a personal
  local pilot, not a staff installation or production deployment.
- **Next action:** Hafiz runs a personal acceptance trial with real
  non-critical sessions. Keep Planner writes, snooze, Telegram, staff use,
  model-authentication changes, product access, KVM, and deployment separate.
- **Promote to:** GitHub issue in the umbrella repo when the pilot starts;
  feeds the public llm-agent-os brief's research comparison either way.
- **Links:** `docs/agent-playbooks/agent-os-omnigent-foundation-fit-test.md`,
  [omnigent repo](https://github.com/omnigent-ai/omnigent),
  Koda mem_227cab004cef (research), mem_750a3a6858f6 (tooling vision),
  mem_a91d4eed0f1d (advisory lesson), mem_6309bced0972 (Checkpoint 4
  remediation result and remaining reliability gaps)

### XP-TUTOR-TICKET-ATTACHMENT-001 — Repair Tutor App ticket photo uploads

- **Project:** cross-project (`sifututor_tutor` + `sifu-tutor`)
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** Tutor photos attached to extra-class requests and general
  complaints reach SIMS as real uploaded files through a reviewed multipart
  contract instead of being reduced to unusable device-local path strings.
- **Why it matters:** The Issue #129 related-impact audit found that
  `SubmitRequestExtraClass` and `SubmitRequestGeneralComplaint` pass a local
  `file://` path through `request_data[attachment_url]`, while the shared ticket
  endpoint stringifies the value. The path exists only on the tutor's phone, so
  SIMS never receives the photo even though the UI appears to attach it. This is
  separate from attendance-proof storage growth and must not expand Issue #129.
- **Source:** Mobile developer's Issue #129 implementation report, 2026-09-01.
- **Next action:** Run a read-only cross-project diagnosis of the two Tutor App
  entry points, the shared ticket endpoint, the current SIMS request validator
  and persistence path, authentication/ownership, retry/idempotency, file
  cleanup, and backward compatibility. Then create linked SIMS and Tutor App
  GitHub issues with one explicit multipart field and permanent API/mobile E2E
  evidence before implementation.
- **Promote to:** Linked `sifu-tutor` and `sifututor_tutor` GitHub issues after
  the backend/mobile contract is diagnosed and approved.
- **Links:** `Sifututor/sifututor_tutor#129`, Issue #129 developer comment
  `5489771259`

### XP-I18N-001 — Add English and Bahasa Melayu product localization

- **Project:** cross-project (`sifu-tutor` + `ripple-suite` +
  `sifututor_tutor` + `sifututor_parent`)
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** SIMS, Ripple, the Tutor App, and the Parent App share a
  maintainable English/Bahasa Melayu localization system and let each user
  choose their preferred language without changing canonical business data.
- **Why it matters:** The current applications are English-only. Catalogue and
  workflow labels therefore need English wording today, while Malay support
  should be implemented consistently across all four products instead of as
  isolated translated strings.
- **Source:** Hafiz's Nakngaji staging catalogue configuration session,
  2026-08-18.
- **Next action:** When prioritized, run cross-platform product design to define
  locale ownership, language switching, translation keys and fallback rules,
  server-generated copy, notifications/PDFs, API compatibility, persistence,
  migration strategy, and browser/mobile QA coverage.
- **Promote to:** Cross-platform PRD and separate implementation issues per
  repository after the shared localization contract is approved.
- **Links:** Koda memory for the same confirmed direction; no implementation
  artifact yet.

### AO-WEEKLY-REPORT-001 — Weekly delivery report: settle open decisions

- **Project:** cross-project (umbrella Agent OS reporting)
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** The weekly team delivery report runs every week from a committed,
  reviewed collector, reaches Codex and other machines, and keeps measuring the
  right things rather than drifting into a ranked leaderboard.
- **Why it matters:** The report format was settled on 2026-08-21 after research
  into DORA, SPACE, DX Core 4 and Google's GSM. Four decisions were deliberately
  left open at the end of that session, and each one degrades the work if it is
  never returned to.
- **Source:** Hafiz's weekly staff delivery review session, 2026-08-21.
- **Next action:** Settle four open decisions:
  (1) commit `scripts/agent-checks/weekly-delivery-data.py`, currently untracked,
  after Codex reviews it for silent-failure paths (a failed `gh` query and a
  genuinely quiet week are currently indistinguishable, both return `[]`);
  (2) decide whether `~/.claude/skills/weekly-report/SKILL.md` moves into the
  repo, since it is machine-local today and Codex/other machines cannot see it;
  (3) decide whether to share the published artifact with staff, still private;
  (4) around 2026-09-11, after roughly three runs, re-read the report and decide
  whether the per-person Volume row still earns its place or whether
  Shipped/Quality/Stuck alone says more — the research is clear that comparing
  people on volume degrades over time even without explicit ranking.
- **Promote to:** A committed collector plus a repo-resident skill, or an
  explicit decision to retire the format.
- **Links:** Koda mem_0208794de669 (five settled design decisions and the
  research behind them), mem_92b02ec6460b (review-queue finding and the
  Asim-was-not-idle correction); artifact
  https://claude.ai/code/artifact/494de27c-1277-411e-8559-ef334b7bec2d

### AO-KODA-HYGIENE-001 — Independent verification of the 2026-08-26 Koda maintenance pass

- **Project:** cross-project (umbrella Agent OS / Koda memory system)
- **Status:** done
- **Type:** mission
- **Parent:** none
- **End goal:** Codex independently verifies Claude's large Koda memory-system
  cleanup from 2026-08-26 and fixes anything found wrong, since Claude's own
  self-report is builder evidence, not acceptance.
- **Why it matters:** The session reclassified 403 memories out of a mistagged
  "default" project bucket, deduplicated content across many projects, merged
  the finch-inbox/team-inbox Koda project split, recovered a stuck validation
  pipeline, and cleaned up 115 mislabeled relationship-graph pairs — all via
  direct writes to the production Koda database using a previously-undocumented
  admin HTTP API. Claude already self-caught and fixed 5 of its own
  misclassification errors during spot-checks; there is no guarantee all
  remaining ones were found given the volume of judgment calls involved.
- **Source:** Hafiz's "so all done?" Koda audit session, 2026-08-26.
- **Current state:** Independently verified and repaired on 2026-08-26. The
  pre-retag backup contained 405 `default` rows: 403 were active when Claude
  classified them, and 398 survived the later duplicate cleanup. Codex sampled
  20 memories from each of the six largest/high-risk project groups, reviewed
  all 70 umbrella/Agent OS assignments, and compared the exact cohort by ID.
  It corrected 83 project assignments, repaired 370 tag sets, removed every
  surviving cohort `default` tag, and ensured every surviving memory carries
  its final project tag. It also moved the new maintenance summary out of
  `default`, leaving the active `default` bucket empty.
- **Security repair:** Two active memories still retained plaintext login
  credentials. Both were rewritten to preserve the lesson without the value;
  their full-text rows were rebuilt and their stale vector embeddings removed.
- **Relationship repair:** The reported seven Creative Hub contradictions were
  seven directed rows for four unique conflicts. Current `origin/staging`,
  `origin/main`, and Git history established the last valid implementation for
  each. The seven `contradicts` rows were replaced with four one-way
  `supersedes` rows.
- **Evidence:** Fresh backup
  `/opt/koda/backups/brain-codex-koda-audit-20260826T121929.db`; active cohort
  398; cohort `default` tags 0; missing project tags 0; invalid cohort projects
  0; Creative Hub contradictions 0; validation queue pending/failed/processing
  all 0.
- **Next action:** None for this verification item. The separate `AO-KODA-001`
  legacy taxonomy backlog is also closed.
- **Promote to:** Close this item once Codex reports verification results,
  fixing anything wrong along the way.
- **Links:** Koda mem_e55cef2a0d81 (full session summary); full handoff text
  given to Hafiz to relay to Codex is in the chat transcript of this session
  (not separately filed, per the handoff playbook's "no ceremony" rule for a
  single self-contained continuation prompt).

### AO-HELMI-KODA-001 — Complete Helmi's Koda administrator first login

- **Project:** cross-project (Agent OS / Koda)
- **Status:** paused
- **Type:** mission
- **Parent:** none
- **End goal:** Helmi controls his own Koda administrator account, has replaced
  the temporary credential, and the local credential handoff artifact has been
  securely removed.
- **Why it matters:** The account, authentication, and administrator authority
  are verified, but the handoff is incomplete until the recipient signs in,
  rotates the temporary password, and confirms access.
- **Source:** Hafiz-approved Koda administrator access session, 2026-09-03.
- **Next action:** Hafiz privately transfers the owner-only credential handoff;
  Helmi signs in, changes the temporary password immediately, and confirms
  administrator access; Hafiz then deletes the local handoff artifact.
- **Promote to:** none; this is an external access-handoff follow-up, not an
  engineering implementation issue.
- **Links:** Koda `mem_7cc67a795106` records the access-policy decision without
  personal identifiers or credentials.

### BD-AISB-001 — Aras Integrasi compute partnership for Learnest Lab R&D

- **Project:** cross-project (Learnest Lab company development)
- **Status:** paused
- **Type:** mission
- **Parent:** none
- **End goal:** Learnest Lab has agreed access to Aras Integrasi Sdn Bhd
  (AISB) language model API and GPU capacity for research, development and
  experimentation, on terms that give AISB first position on any resulting
  commercial product.
- **Why it matters:** Compute cost is the current limit on how fast Learnest
  Lab can experiment across its product lines. A resource partnership removes
  that limit without cash outlay, and opens a commercial channel with AISB.
- **Source:** First formal approach email sent 2026-09-03 to
  daf@arasintegrasi.ai (Faurani), CC faiz@, sm@, syamil.yusoff@ and
  danial@learnestlab.com.
- **Current state:** Email delivered from hafiz@learnestlab.com. No response
  yet. Nothing agreed, no terms, no volumes, and no numbers were named on
  purpose so the negotiation is not anchored before AISB states what is
  realistic.
- **Next action:** Wait for Faurani's reply. If a call is scheduled, prepare a
  first-phase scope: which workloads run on AISB infrastructure, expected
  volume, and what "first position on commercial products" means concretely.
- **Do not do yet:** Do not raise the TM GRC or SOCSO deal-registration
  thread, the DataFusion Syariah agency POC, or any named product in this
  thread until the resource conversation has its own footing. They were
  deliberately excluded from the first email.
- **Open decisions for Hafiz:** What a first phase should actually cover, and
  what level of exclusivity Learnest Lab is willing to commit to in return.
- **Promote to:** none; this is business development, not engineering work.
- **Links:** Koda `mem_70ab432ce9ac` records what was offered and what was
  deliberately withheld from first contact.

### BD-CSM-001 — CyberSecurity Malaysia incident response ticketing opportunity

- **Project:** cross-project (Learnest Lab company development)
- **Status:** active
- **Type:** mission
- **Parent:** none
- **End goal:** Learnest Lab Malaysia is engaged as the local implementation
  and support partner for CyberSecurity Malaysia's incident response
  ticketing system, whichever platform CSM selects.
- **Why it matters:** First real public sector delivery opportunity for
  Learnest Lab, in a sector adjacent to the GRC and risk positioning already
  being pursued with Aras Integrasi. CSM has not finalised its platform
  choice, so there is a window to help shape the requirement, which usually
  advantages whoever is in the room early.
- **Source:** Shahruzzani Mohammad asked Hafiz by WhatsApp to approach Affan
  for a discovery session. Approach email sent 2026-09-09 from
  hafiz@learnestlab.com to mohd.affan@cybersecurity.my, CC syamil.yusoff@
  and faiz@learnestlab.com.
- **Current state:** Awaiting Affan's reply. Nothing proposed, no numbers
  named, no meeting scheduled. Positioning is product-neutral local
  implementation partner, deliberately not a custom build.
- **Verified from primary source 2026-09-09:** CSM's own procurement page
  (https://www.cybersecurity.my/portal-main/procurement) was read directly.
  Findings, all public and independent of the back channel:
  (a) No incident response ticketing requirement has ever been advertised.
  The published register covers 38 procurements across 2025 and 2026 to date
  and contains no ticketing, helpdesk or ITSM item.
  (b) CSM procures almost everything as sebut harga. The register shows one
  open tender only (TB/01/2025, medical insurance) against 36 sebut harga and
  one RFP, so an invited sebut harga is the likely route, not an open tender.
  (c) Published thresholds: RFP above RM50,000, sebut harga RM50,000 to
  RM499,999.99, tender RM500,000 and above. The unverified RM120,000 figure
  would fall in the sebut harga band, which is invited rather than open.
  (d) An MOF certificate is listed in CSM's own vendor registration
  requirements, alongside SSM and SST. This confirms the MOF question is a
  real gate, not a guess.
  (e) SH/01/2026, an Integrated Business Process Management System, was
  awarded earlier in 2026. Possible scope overlap with ticketing, unverified.
- **What this changes:** Getting invited is the actual contest, not winning a
  public bid. Vendor prequalification (MOF, CSM vendor registration) is
  therefore the gating action and it does not depend on Affan replying.
- **Decision 2026-09-09, do not approach Shahruzzani:** A nine-question
  qualification message was drafted, reviewed question by question, and then
  dropped in full by Hafiz. Reason: keep the partner relationship clear of any
  information-gathering, since Shahruzzani is a CSM employee as well as a
  Learnest Lab partner and qualifying questions create the same
  conflict-of-interest exposure that already kept his CSM address off the
  vendor approach. Consistent with that earlier decision, not a reversal.
  The draft is retained, marked do-not-send, at
  `docs/csm-qualification-questions-2026-09.md`. A future session must not
  send or adapt it without an explicit new decision from Hafiz.
- **Accepted consequences of that decision:** the RM120,000 OTRS claim stays
  permanently unverified; we never test whether CSM is genuinely
  dissatisfied; and the opportunity now rests entirely on Affan replying.
- **Next action:** Wait for Affan's reply. There is no longer a parallel
  qualification track. Unblocked work that does not depend on him: confirm
  Learnest Lab's MOF field codes cover ICT software and services, and decide
  whether to complete CSM vendor registration via `pnld@cybersecurity.my`.
- **Decision 2026-09-09, vendor registration on hold:** Hafiz chose to wait for
  Affan rather than register now, to avoid approaching the agency from two
  directions at once. Revisit once a requirement is known to exist.
- **Decision 2026-09-09, Perl capability deferred:** No hire and no partner
  search until we know which platform is actually in play. Four of the five
  candidates are Perl and Learnest Lab has none, but committing before the
  platform is known risks paying for capability that is never used. This
  closes open decision (1) as deferred, not resolved.
- **Decision 2026-09-09, positioning reopened:** The earlier choice of prime
  contractor is put back on hold until Affan replies. The research surfaced
  that Learnest Lab has no security delivery record, no Perl, no prior
  Malaysian government delivery, and that CSM buys licences far more readily
  than implementation services. Nothing downstream depends on the positioning
  yet, so holding it open costs nothing. NOTE: the research brief still states
  "Positioning assumed: Learnest Lab as prime contractor" in its header, in
  this repo and in the merged papertrail copy. Correct both when the
  positioning is settled.
- **Do not do yet:** Do not put Shahruzzani's CyberSecurity Malaysia address
  (m.shahruzzani@cybersecurity.my) on any vendor correspondence without an
  explicit decision from Hafiz. He is both a Learnest Lab partner and a CSM
  staff member, and a concealed copy on a vendor approach is a procurement
  conflict risk for him personally. Do not treat the OTRS claim as
  established fact; it is third-hand and unverified against any primary
  source.
- **Open decisions for Hafiz:** (1) Perl capability, since OTRS is Perl and
  Learnest Lab has none, hire versus partner versus decline; (2) whether
  Learnest Lab is MOF-registered, now confirmed as a stated CSM vendor
  requirement rather than an assumption, so this is the highest-value
  unblocked action; (3) whether to build the platform comparison document
  before the meeting, which stays on hold until question 6 to Shahruzzani
  establishes whether any platform has actually been shortlisted.
- **Research done 2026-09-09:** Internal brief at
  `docs/csm-incident-response-ticketing-research-2026-09.md`, covering the
  platform landscape and the MyCERT operational profile, written from a prime
  contractor position. Headline corrections it makes to our working premise:
  (a) the 24x7 framing is not supported by MyCERT's own RFC 2350 profile,
  which states 09:00 to 18:00 Monday to Friday with an after-hours mobile,
  so this is on-call not round-the-clock; (b) volume is small at 6,209
  incidents in 2024, so scale is not a selection criterion; (c) the workload
  is 68% fraud, which argues against the threat-intel-centric tools;
  (d) TheHive 5's free Community licence is capped at 2 users and 1
  organisation, so TheHive means paid per-user licensing; (e) RTIR is the
  national CSIRT default, used by 8 of 17 in a 2022 peer-reviewed survey
  whose first author is MyCERT staff; (f) Act 854 statutory NCII reporting
  runs to NACSA, not to CSM, so framing this as Act 854 tooling is a scoping
  error; (g) no candidate platform vendor has a Malaysian presence, which is
  the gap our positioning fills.
- **Promote to:** none; this is business development, not engineering work.
- **Links:** Koda `mem_cf393e6dbc1e` records the opportunity, the corrected
  premise, and the conflict-of-interest decision. `mem_d6533e5b69a7` records
  the verified CSM procurement route. `mem_0ae7f0cd4892` records MOF
  registration confirmed with field codes still unknown.
