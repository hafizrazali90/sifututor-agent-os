# Kelasapp — Launch-Readiness Gap Plan

> Sequenced punch-list of what stands between Kelasapp's MVP and a credible public launch.
> Source: two read-only code audits (onboarding/first-run + operational plumbing) on 2026-06-30,
> benchmarked against how SaaS products actually launch. For *what's built*, see BUILD-LOG.md.
> This is a **plan for review**, not a commitment. Nothing here is built yet.

- **Created:** 30/06/2026
- **Scope of audit:** `kelas/` (Next.js 16, Better Auth, Drizzle + Postgres, Wasabi)
- **Effort key:** S = under half a day · M = 1 to 2 days · L = 3+ days · D = decision (no build until decided)

---

## Verdict

The product engine is solid. Invoicing, attendance, payroll, multi-tenancy, PDFs, SEO/metadata and CI are real and mature for this stage. **Every gap below is either "boilerplate scaffolded but never finished" or "we built the feature but never built the on-ramp to it."** None is a deep architectural hole; most fixes are small.

Gaps cluster into four themes:

1. **No on-ramp.** A new operator lands in an empty dashboard with zero guidance. (This is the quick-start / first-run gap.)
2. **Guest-facing rough edges.** Parents who click invoice links can hit raw, unstyled Next.js error/404 pages.
3. **Marketing promises that the code does not deliver.** Pricing tiers and a "30-day free trial" are advertised; nothing is enforced or built.
4. **Security and observability hardening.** Scaffolded but switched off: no Sentry DSN, no security headers, no rate limiting.

---

## DECIDED LAUNCH SCOPE — triaged with Hafiz 01/07/2026

Authoritative launch plan (supersedes the "Launch plan (phased)" section further down). Every item below was reviewed one-by-one and marked do or defer. Beta shape assumed: small, hand-held (white-glove) beta.

### Building for launch

| # | Item | From | Size | Notes |
|---|---|---|---|---|
| 1 | Getting-started checklist + empty-org detection | A1+A2 | M | New-centre dashboard becomes a guided checklist: set up company/payment, add teacher, create class, enrol student, take attendance, send first invoice. Deep-links + auto-ticks. |
| 2 | Helpful empty states + fix 3 dead-ends | A3-A5 | S | Clickable CTAs inside empty lists; explain the greyed-out enrol-from-class, enrol-from-student, and attendance-no-classes states. |
| 3 | In-app help centre (FULL) + legal links | B1+B2 | M | Real in-app help/FAQ page + contact; Terms/Privacy reachable inside the dashboard. |
| 4 | Branded 404 + styled crash page + in-page recovery | C1-C3 | S/M | Guest-facing (parents hit invoice links). Includes graceful per-section retry. |
| 5 | Sentry on | D1 | S | Error visibility from day one. |
| 6 | Duplicate-payment protection | D2 | S/M | Idempotent public invoice submit (no duplicate pending payments). |
| 7 | Cookie wording fix | H1 | S | Essential-cookies-only wording; no consent banner needed. |
| 8 | Full in-app importer | F2 | L | CSV upload → map columns → preview → import students/teachers/guardians, with error handling. Protects the on-ramp for centres migrating from spreadsheets. |
| 9 | Security headers | D3 | S | Baseline hardening (CSP can start report-only). |
| 10 | Uptime monitoring (BetterStack Uptime) | D6 | S | Point a BetterStack Uptime monitor at a health-check endpoint (added in-app). Status page + incident alerts. Consolidates on the BetterStack account already used for sifu-tutor. Full Checkly E2E still deferred. |
| 11 | Company setup section | F1 (revised) | M | One home in Setup: business name + **logo upload** + payment details + invoice settings (own **prefix**, billing day, due days, burn policy, timezone). Consolidates today's scattered/locked settings. Invoice numbers use the **centre's own prefix** (no Kelasapp in the number). |
| 12 | User-facing design polish + "Powered by Kelasapp" | new | M | Design pass + subtle Kelasapp attribution across all parent-facing surfaces: public invoice/payment page, invoice PDF, payslip PDF, receipts, prefilled WhatsApp message. Surface-by-surface with before/after review; centre brand stays primary. Depends on #11 (logo). |
| 13 | Log forwarding to BetterStack | D5 | S | Sink already coded ([Logger.ts](../../../kelas/src/libs/Logger.ts)); just set NEXT_PUBLIC_BETTER_STACK_SOURCE_TOKEN + INGESTING_HOST for a new "kelasapp" source. Searchable production logs on the same BetterStack account as sifu-tutor. Pulled out of Deferred because it is near-zero effort. |

### Deferred

- Marketing copy reframe (E1-E3) — parked, wording approved (see "Parked copy drafts")
- Sample/demo data (A6)
- Product analytics (D4) → folded into future **Super admin portal**
- Transactional email (G1/G2) — manual WhatsApp only for beta
- List/CSV exports (F3)
- Per-page titles / SEO metadata (H2)
- Product tour / coachmarks (H3)
- PWA / offline (H4)
- Billing build (E5) — post-beta milestone
- **Super admin portal (incl. platform analytics)** — future milestone. Sees across all centres, so it deliberately breaks tenant isolation and needs a platform-owner-only gate that does not exist yet. Security-sensitive; build when supporting beta centres makes it necessary.

### Build order (waves)

> **Status (2026-07-02):** ✅ Waves 1 to 6 all shipped on branch `feat/launch-readiness` (through commit cafd066). **Update: Kelasapp went LIVE in private Beta on 2026-07-05.** Includes the safety net (Workstream C branded error/404 pages done in Wave 1), A2/A3 empty-state on-ramp, B1/B2 in-app help + legal, and item 12 branding (logo + Powered by Kelasapp). The app is now live for private beta; the remaining **public/paid launch** gate is the **E1-E3 marketing/Terms copy reframe** (parked, wording approved in "Parked copy drafts") plus the deferred/nice-to-have list above.

1. **Safety net** (quick, independent): Sentry on · cookie wording · security headers · BetterStack uptime + log forwarding · branded 404/crash/in-page recovery · duplicate-payment protection. (Items 5, 7, 9, 10, 13, 4, 6.)
2. **Company foundation:** Company setup section — business name, logo, payment, invoice settings/prefix. (Item 11.)
3. **The on-ramp (centerpiece):** getting-started checklist + empty states + dead-ends. (Items 1, 2.)
4. **Data migration:** full in-app importer. (Item 8.)
5. **Help & trust:** in-app help centre + legal links. (Item 3.)
6. **User-facing design polish + branding:** all parent-facing surfaces. (Item 12; after #11 provides the logo/brand.)

---

## Workstream A — First-run on-ramp (the activation gap)

> The single highest-leverage area for launch. SaaS best practice is time-to-value in 5 to 10 minutes; today a new operator has none. This is the direct answer to "are we missing a quick-start guide / first-register flow."

| ID | Item | Effort | Evidence (now) | Acceptance criteria |
|---|---|---|---|---|
| A1 | **Getting-started checklist on the dashboard** for empty/new orgs. 3 to 5 steps: add a teacher, create a class, enrol a student, record attendance, send first invoice. Each step links to the right form and ticks off when done. Dismissible once complete. | M | New operator is dropped straight into the analytics dashboard, which for an empty org is a wall of zeros. No welcome, no checklist, no tour. | Empty org sees a checklist above (or instead of) the KPI grid; each item deep-links to its form; items auto-complete from real data; checklist hides once all done or dismissed. Bilingual EN/BM. |
| A2 | **Empty-org detection** helper (one server-side check: does this org have any classes/students/teachers yet). Drives A1 and the empty-state CTAs. | S | No such concept today; every page renders its empty state independently. | A single reusable check the dashboard and list pages can call; covered by a unit test. |
| A3 | **Make empty states actionable.** Every "Add your first…" empty state gets a real CTA button inside it, not just text. | S | Empty lists show friendly copy but the text is not clickable; only billing/payroll have an adjacent Run panel. | Students, teachers, guardians, classes, attendance empty states each contain a primary CTA button that opens the create/relevant flow. |
| A4 | **Fix the 3 silent dead-ends.** A greyed-out button with no explanation. | S | Enrol-from-class disabled with no hint (class detail ~line 174-175); enrol-from-student (student detail ~line 200, 204-205); attendance "No classes scheduled for this day" with no CTA (`attendance/page.tsx:66`). | Each disabled/empty state explains why and links to the prerequisite ("Add a student first", "Create a class first"). |
| A5 | **Replicate the ClassForm "go create one" pattern** anywhere a form references an entity that may not exist yet. | S | ClassForm already does this well (program/level/teacher optional with inline "go create one" links). It is the only good affordance of its kind. | Inline create-links added wherever a required-ish relation could be empty (e.g. enrolment needs a class + student). |
| A6 | **Sample / demo data loader** (optional "Load sample data" for a new org, clearly removable). | M | No user-facing sample data exists; the only seed is `seed-dev.cjs`, dev-only and destructive. | Operator can load a small realistic sample set (a class, a few students, a guardian, an invoice) and wipe it cleanly without touching real data. |

---

## Workstream B — In-app help & support

| ID | Item | Effort | Evidence (now) | Acceptance criteria |
|---|---|---|---|---|
| B1 | **In-app Help/Support entry point.** A persistent link (sidebar footer or header) to help: contact email/WhatsApp, FAQ, and/or docs. | S | All FAQ/contact lives on the marketing site only. The dashboard header has just the sidebar trigger, org switcher, locale switcher and Better Auth user menu. A confused operator inside the app has no path to help. | A visible Help item inside the dashboard that opens support contact and/or FAQ. Bilingual. |
| B2 | **Legal links reachable inside the app.** Terms + Privacy from a dashboard footer or the user menu. | S | Terms/Privacy are good and bilingual but linked only from the marketing footer (`Footer.tsx:123-143`); the authenticated dashboard has no footer and no legal links. | Logged-in users can reach Terms and Privacy from inside the dashboard. |

---

## Workstream C — Guest-facing polish ("don't embarrass us")

> The public surface parents touch: tokenised invoice links. Small fixes, high trust impact.

| ID | Item | Effort | Evidence (now) | Acceptance criteria |
|---|---|---|---|---|
| C1 | **Custom `not-found.tsx`** (branded, bilingual). | S | No `not-found.tsx` anywhere, yet `notFound()` is called for a bad locale (`[locale]/layout.tsx:65`) and a bad/expired invoice token (`invoice/[token]/page.tsx:17`), both falling through to Next's unstyled default 404. Parents hit the invoice case. | A mistyped/expired invoice link shows a branded, translated "not found" page with a sensible next action. |
| C2 | **Style `global-error.tsx`** (brand + translation, keep Sentry capture). | S | `global-error.tsx:1-26` is unmodified boilerplate rendering Next's bare `NextError` (unstyled, untranslated). | Uncaught top-level errors show a branded, translated page; Sentry capture preserved. |
| C3 | **Per-route `error.tsx` boundaries** for the dashboard and the public invoice route. | S/M | No `error.tsx` in any segment; any render error escalates straight to the raw `global-error.tsx`. | Dashboard and invoice render errors recover gracefully in-layout with a retry, instead of a full-page crash. |

---

## Workstream D — Security & observability hardening

| ID | Item | Effort | Evidence (now) | Acceptance criteria |
|---|---|---|---|---|
| D1 | **Turn Sentry on in production** (set the DSN; add to env validation). | S | Sentry is fully wired (`instrumentation.ts:27-39`, `instrumentation-client.ts:6-44`, `next.config.ts:35-71`, tunnel route) but the DSN is commented out (`.env.local.example:26`) and not validated in `Env.ts`. Effectively blind in prod. | Prod errors and session replays land in Sentry; DSN validated at boot. |
| D2 | **Rate-limit + idempotency** on the public invoice submit. | M | `POST /api/invoice/[token]/submit` (`route.ts:12-45`) has no throttle and **resubmitting creates duplicate pending payments**. Token entropy is strong (144-bit) so guessing is not the risk; duplicate/spam submissions are. | The endpoint rejects abusive volume (429) and is idempotent on resubmit (no duplicate pending payment). |
| D3 | **Security headers** via `next.config.ts headers()` or `proxy.ts`. | S | `proxy.ts:1-82` sets none; `next.config.ts` has no `headers()`. Missing CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy. Only `poweredByHeader:false`. | Standard security headers present on all responses; CSP at least in report-only to start. |
| D4 | **Product analytics** (PostHog/Plausible or similar). | M | None present (no PostHog/Mixpanel/Plausible/GA/Segment). Cannot measure activation or drop-off. Especially needed to validate Workstream A. Already flagged pending in the landing-page notes. | Key activation events (signup, first class, first student, first invoice) are tracked; a basic funnel is visible. |
| D5 | **Enable BetterStack log shipping** (currently console-only). | S | LogTape + optional BetterStack sink (`Logger.ts:5-31`) gated on two env vars (`Env.ts:22-23`) that are unset, so logs are console-only in prod. | Production logs ship to BetterStack. |
| D6 | **Populate Checkly uptime secrets** + write a couple of `*.check.e2e.ts`. | S/M | Checkly is configured (`checkly.config.ts`, every 24h, two regions, email alerts) and wired to CI (`checkly.yml`) but needs `CHECKLY_*` secrets and check files. | Uptime checks run against production and alert on failure. |

---

## Workstream E — Commercial model

> **DECIDED 30/06/2026: Option C — free beta with a founding-member promise.** Launch open and free; reword marketing/Terms so nothing promises a paid trial/tiers that do not exist yet; tell early centres they lock in founding pricing when paid plans launch. The Stripe/limits/trial build is deferred to a post-beta milestone (it is the only "L" here and would bake in pricing we cannot yet validate). Original framing: the marketing site sells a paid SaaS the code does not implement (Pricing page `Pricing.tsx:8-54` sells Starter/Growth/Scale tiers with limits, all CTAs to `/sign-up`; Terms `terms/page.tsx:160,165` promise a converting "free trial"; hero says "30-day free trial"), while the code has no Stripe, no plans/subscriptions/trial tables, no limit enforcement: everything is free + unlimited.

**Sub-decision (pricing display):** keep the tiers visible but reframed (a founding-member promise needs visible pricing to anchor against; hiding it makes "free" feel like bait).

| ID | Item | Effort | Detail | Acceptance criteria |
|---|---|---|---|---|
| E1 | **Pricing page reframe.** | S | Relabel every CTA from "Start trial / Sign up" to "Join the beta (free)"; add a banner "Free during beta. Founding centres lock in early pricing when paid plans launch"; mark prices as indicative/planned. | No CTA promises a trial; the founding-member message is visible; prices clearly marked not-yet-final. Bilingual EN/BM. |
| E2 | **Terms reword.** | S | Remove/soften "free trial converts to a paid plan" (`terms/page.tsx:160,165`); replace with beta terms (free during beta, pricing introduced later with notice, founding pricing for early centres). | Terms no longer promise a trial/auto-conversion that does not exist. |
| E3 | **Hero/marketing sweep.** | S | Reconcile "30-day free trial" with "free for 3 months" so they do not contradict; land on one beta message. Sweep for any other "trial" implications. | Consistent single beta message across hero, pricing, Terms. |
| E4 | **Founding-member tracking (placeholder, not launch work).** | S | A way to know who joined during beta so the price-lock can be honoured later: likely a flag or "joined before date X" check on the org. | Captured for the post-beta billing milestone, not built now. |
| E5 | **Billing build (DEFERRED, post-beta milestone).** | L | Payment provider (Stripe or a MY-friendly PSP), `plans`/`subscriptions`/`trial` tables, trial-expiry job, **limit enforcement** on `createStudent`/`createClass`/staff creation, plus soft storage/compute caps for the free tier. | Out of launch scope; scheduled after beta validates adoption + pricing. |

---

### Parked copy drafts (wording approved 01/07/2026, NOT yet applied)

Hafiz chose to skip the copy pass for now. The wording below is settled and ready to apply when we resume. Term decided: **"early adopters"** (BM: **"pengguna terawal"**); use "a lower price", not "early pricing". No em dashes.

**E1-E3 reframe (marketing + Terms):**

| Key | New EN | New BM |
|---|---|---|
| Hero.primary_button / CTA.primary_button / Footer.link_start_trial / Pricing.starter_cta / Pricing.growth_cta | Join the beta | Sertai beta |
| Hero.microcopy (dead key, skip unless wired) | No credit card. Free while Kelasapp is in beta. | Tiada kad kredit. Percuma sepanjang Kelasapp dalam beta. |
| Hero.badge (dead key, skip unless wired) | Now in beta · Free to use | Kini dalam beta · Percuma untuk digunakan |
| Trust.point4_title | Free during beta. | Percuma dalam beta. |
| Trust.point4_description | Full access while we're in beta. Early adopters lock in a lower price when paid plans launch. | Akses penuh sepanjang tempoh beta. Pengguna terawal mengunci harga lebih rendah apabila pelan berbayar dilancarkan. |
| Pricing.title_line1 / title_line2 | Free during the beta, / founding pricing after launch | Percuma dalam beta, / harga perintis selepas pelancaran |
| Pricing.subtitle | Indicative pricing. Nothing to pay during the beta. | Harga anggaran. Tiada bayaran sepanjang beta. |
| Pricing.beta_banner (NEW key + Pricing.tsx element) | Free for every centre while Kelasapp is in beta. Early adopters lock in the prices below when paid plans launch. | Percuma untuk semua pusat sepanjang Kelasapp dalam beta. Pengguna terawal mengunci harga di bawah apabila pelan berbayar dilancarkan. |
| Pricing.footnote | No credit card required. | Tiada kad kredit diperlukan. |
| SignUp.meta_title | Join the Kelasapp beta | Sertai beta Kelasapp |
| Terms section 3 (inline, both langs) | Kelasapp is currently in beta and free to use. There are no charges during the beta period. When we introduce paid plans we will give advance notice, and no account will be charged without opting in. Early adopters who join during the beta will be offered a lower price when paid plans launch. Prices, when introduced, will be stated in Malaysian Ringgit (RM). You can stop using Kelasapp at any time. | Kelasapp kini dalam beta dan percuma untuk digunakan. Tiada sebarang caj sepanjang tempoh beta. Apabila kami memperkenalkan pelan berbayar, kami akan memberi notis terlebih dahulu, dan tiada akaun akan dicaj tanpa persetujuan anda. Pengguna terawal yang menyertai sepanjang tempoh beta akan ditawarkan harga lebih rendah apabila pelan berbayar dilancarkan. Harga, apabila diperkenalkan, akan dinyatakan dalam Ringgit Malaysia (RM). Anda boleh berhenti menggunakan Kelasapp pada bila-bila masa. |

**Batch 2 (honesty cleanup, same pass):**

| Location | New EN | New BM |
|---|---|---|
| Hero logo marquee | REMOVE fake logos; keep one honest line: "Built for tuition centres, madrasahs, and online academies across Malaysia." | Dibina untuk pusat tuisyen, madrasah, dan akademi dalam talian di seluruh Malaysia. |
| Trust.point1_title | Get paid with DuitNow | Bayaran DuitNow |
| Trust.point1_description | Show your DuitNow QR on every invoice. Parents pay and upload their receipt, the way they already pay in Malaysia. | Paparkan kod QR DuitNow anda pada setiap invois. Ibu bapa membayar dan memuat naik resit, cara mereka sudah biasa membayar di Malaysia. |
| FeatureShowcase.feature_b_description | (replace tail) …tracks partial payments. Generate a whole month of invoices in one click. | …menjejaki bayaran separa. Jana invois sebulan penuh dengan satu klik. |
| FeatureShowcase.feature_b_bullet1 | One click on your billing day generates them all | Satu klik pada hari pengebilan menjana kesemuanya |
| FeatureShowcase.feature_d_title | Parents always in the loop.<br></br>One tap. | Ibu bapa sentiasa dimaklumkan.<br></br>Satu ketik. |
| FeatureShowcase.feature_d_description | Send WhatsApp reminders, attendance updates, and invoice receipts in one tap, with the message already written. No more digging for numbers. | Hantar peringatan WhatsApp, kemas kini kehadiran, dan resit invois dengan satu ketik, mesej sudah siap ditulis. Tak perlu lagi cari nombor satu-satu. |
| FAQ payment answer | Kelasapp supports DuitNow QR (show your QR on the invoice; parents upload their payment proof), manual bank transfer, and cash. Partial payments are tracked automatically. A full online gateway (FPX and card) is on the way. | Kelasapp menyokong QR DuitNow (paparkan QR pada invois; ibu bapa memuat naik bukti bayaran), pindahan bank manual, dan tunai. Bayaran separa dijejaki secara automatik. Get laluan pembayaran penuh (FPX dan kad) akan menyusul. |

Files touched when applied: `src/locales/en.json`, `src/locales/ms.json`, `src/templates/Pricing.tsx` (new banner element), `src/templates/Hero.tsx` (remove marquee), `src/app/[locale]/(marketing)/terms/page.tsx` (section 3, both langs).

---

## Workstream F — Settings & data portability (friction reducers)

| ID | Item | Effort | Evidence (now) | Acceptance criteria |
|---|---|---|---|---|
| F1 | **Expose locked operator settings** in the UI. | M | `orgSettings` (`Schema.ts:22-39`) stores 11 fields; only 5 are editable (`PaymentSettingsForm.tsx`, API `route.ts:9-20`, persist `service.ts:556-588`). Locked at defaults, require direct DB edits: `invoicePrefix` (`:26`), `invoiceDay` (`:27`), `defaultDueDays` (`:28`), `defaultBurnPolicy` (`:29`), `timezone` (`:30`), `currency` (`:25`). | Operator can edit invoice prefix, billing day, due days, burn policy and timezone from settings. Owner-gated where appropriate (see UI-CONVENTIONS owner-vs-staff). |
| F2 | **Bulk CSV import** of students/teachers/guardians. | L | No import anywhere (no papaparse/csv-parse/xlsx); every record is a single-record form. A centre migrating from spreadsheets must hand-key everything. | Operator can upload a CSV, map columns, preview, and import with validation + error report. |
| F3 | **List/CSV exports** for students/teachers/invoices/payroll + a PDPA full-data export. | M | Exports exist only per-record/report-scoped (attendance CSV/PDF, per-invoice PDF, per-payslip PDF). No bulk list export; no account-level data export. | Each list page can export its rows; an account-level export covers PDPA data-portability requests. |

---

## Workstream G — Transactional email & notifications (decision + optional build)

| ID | Item | Effort | Evidence (now) | Notes |
|---|---|---|---|---|
| G1 | **Decide email posture for launch.** | D | No email infrastructure at all (no Resend/Postmark/SES/nodemailer). Sharing is 100% manual: WhatsApp click-to-chat (`wa.ts:42-44`, `WhatsAppReminderButton.tsx`) and copy-link (`CopyLinkButton.tsx:13-15`). A code comment defers a provider ("finch-lite later"), so manual-only appears intentional for slice 1. | Either accept manual-WhatsApp-only for launch (documented), or build a minimal reminder/receipt email path. |
| G2 | **If building:** minimal transactional email (welcome + invoice reminder + receipt). | M | As above. | Provider wired; the few highest-value transactional emails send. |

---

## Workstream H — Compliance & polish (nice-to-have)

| ID | Item | Effort | Evidence (now) | Acceptance criteria |
|---|---|---|---|---|
| H1 | **Align cookie wording to reality** (and add a consent banner only when tracking is added). | S | Privacy policy describes cookies (`privacy/page.tsx:200-204`) but the app uses only essential cookies (Better Auth session + the sidebar-state cookie in `components/ui/sidebar.tsx:5-6`) and no tracking, so a consent banner is not legally required yet. PDPA itself is correctly covered (`privacy/page.tsx:39`, `:136`). | Policy says "essential cookies only." A consent banner is added the moment D4 (analytics) ships. |
| H2 | **Per-page dashboard titles** + root `description`/Twitter image. | S | Only 1 of 31 dashboard pages sets metadata (shared `dashboard/layout.tsx:14-22`); every tab shows the same browser title. Root metadata lacks `description` and a Twitter image. | Each dashboard route has a meaningful `<title>`; root metadata complete. |
| H3 | **Product tour / coachmarks + contextual tooltips.** | M | None today. | A short (under 45s), skippable first-run tour highlighting the core nav. |
| H4 | **Public/marketing `loading.tsx`; offline/PWA.** | S/M | Only one `loading.tsx` exists (`dashboard/loading.tsx`), covering all dashboard routes; none for public invoice, marketing, or auth. No service worker/manifest/offline fallback. | Public/marketing routes show skeletons; basic offline handling if PWA is pursued. |

---

## Launch plan (phased) — DECIDED 30/06/2026

> SUPERSEDED 01/07/2026 by "DECIDED LAUNCH SCOPE" near the top of this doc (finer item-by-item triage with Hafiz). Kept for history.

> Framed as launch gates, not a strict linear order. Most items are small and parallelizable; the decision is *where the launch line sits*. Two judgment calls applied: D2's idempotency half and a minimal slice of D4 are pulled into the gate (both for integrity/visibility reasons noted below).

### Phase 0 — Launch gate (must be true before any beta centre is let in)

| Item | Why it gates launch | Size |
|---|---|---|
| **E1–E3** pricing/Terms/hero copy reframe | No false promises the moment marketing is public. | S |
| **A1–A4** checklist + empty-org detection + actionable empty states + fix 3 dead-ends | The on-ramp. Without it a beta centre is lost day one. The core of the launch. | M |
| **B1–B2** in-app help + legal links | Confused beta user can reach you and reach the Terms. | S |
| **C1–C2** branded 404 + styled error page | Parents hit these via invoice links. First impression. | S |
| **D1** Sentry DSN on | See errors during the riskiest phase. | S |
| **D2 (idempotency half only)** on the public invoice submit | Money integrity: resubmit currently creates duplicate pending payments, and self-service upload is live in the MVP so parents will use it in beta. Rate-limiting half deferred to Phase 1. | S/M |
| **D4 (minimal slice only)** activation events: signup, first class, first student, first invoice | Don't ship the on-ramp (A) blind; need to see if it works. Fuller funnel/dashboards deferred to Phase 1. | S/M |
| **H1** cookie wording align | Quick PDPA-accuracy fix (no tracking beyond the minimal D4 events; revisit banner if richer tracking is added). | S |

Everything except A is small. A is the real build.

### Phase 1 — Fast-follow (first week or two of beta)

D2 (rate-limiting half) · D3 security headers · D4 (fuller funnel + dashboards) · A5 inline create-links · A6 sample data · C3 route error boundaries · F1 expose settings · G1 email decision.

### Phase 2 — On-demand / later

F2 import · F3 export · D5 log shipping · D6 uptime · H2 per-page titles · H3 tour · H4 PWA · **E5 billing (post-beta milestone).**

## Explicitly deferred (already decided, out of this plan)

- Payment gateway / dynamic DuitNow QR / auto-confirmation (rides with the slice-2 gateway; see BUILD-LOG locked decisions).
- LHDN / MyInvois e-invoicing.
- Teacher-pay partial payments, recurring allowances, bank automation.
- finch-lite stateful WhatsApp gateway/inbox.
- Auto-attendance (Meet/Zoom).
- M7 AI layer (post-MVP by Hafiz's call).
