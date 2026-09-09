# Kelasapp — Comprehensive Deep-Review Brief (for Codex)

> Paste everything below the line into Codex as the task. It is self-contained.

---

## 0. Your role and mission

You are a **senior staff engineer + security auditor** performing a **comprehensive, read-only deep review** of the entire Kelasapp codebase, its features, its business logic, its data model, its tests, and its documentation. Produce a rigorous **analysis with comments and recommendations** — not fixes. Think like someone who will be on call for this system: find what will break, what will leak data, what is wrong, what is missing, and what is merely fragile.

Be **skeptical and evidence-based**. Verify every claim against the actual code (read both the frontend and backend of any flow before asserting how it behaves). When you are unsure, say so and pose it as a **question**, do not assert. Cite `file:line` for every finding. Do not flatter the code; do not invent problems either.

Output language: **English** (this is a deliverable for the owner, Hafiz).

## 1. What Kelasapp is

A multi-tenant SaaS for **Malaysian tuition and *mengaji* (Quran) centres** to run classes, students, guardians, enrolments, attendance, reports, invoicing, payments/receipts, and teacher pay. One centre = one tenant (organisation). Bilingual **English + Bahasa Melayu**. Malaysian by default: dates **DD/MM/YYYY**, timezone **Asia/Kuala_Lumpur**, currency **RM**, 12-hour times.

**Status: LIVE in a private Beta** (deployed 2026-07-05). It has real infrastructure but, as of now, essentially no end-user data yet (a real customer's data import is imminent). Treat it as **production**.

## 2. Stack

- **Next.js 16** (App Router, React Server Components), **React 19**, **TypeScript**, **Tailwind v4**, **shadcn/ui**
- **Better Auth** (self-hosted; the `organization` plugin is the tenant boundary) — **not Clerk** (see §6)
- **Drizzle ORM**; **PGlite** in dev/test, real **PostgreSQL 16** in prod
- **next-intl** (locales `en`, `ms`), **Wasabi** (S3) for media, `@react-pdf/renderer` for PDFs, `sharp` for images, poppler `pdftoppm` for PDF previews
- **Resend** for transactional email, **Sentry** for error monitoring
- Tooling: **ESLint** (antfu flat config — requires **Node 24**), `tsc`, **knip**, **Vitest**, **Playwright**
- **Node 24 is required** (the ESLint flat config uses `Object.groupBy`; Node < 21 crashes the toolchain)

## 3. Where everything lives

- **Code:** `~/Projects/Sifututor/kelas/` (this is the repo; remote `github.com/Learnest-Lab/kelasapp`, active branch `feat/finish-mvp-polish`).
  - `src/app/[locale]/` — App Router: `(marketing)` (landing, `/privacy`, `/terms`), `(auth)/dashboard` (the product), public `/invoice/[token]`, `/api/*` route handlers
  - `src/features/<domain>/` — one folder per domain, each with an org-scoped `service.ts` (+ `service.test.ts`) and its UI. Domains: classes, teachers, guardians, students, enrolments, attendance, reports, invoicing, taxonomy, media, messaging, import, payouts, dashboard, landing, ui
  - `src/models/Schema.ts` + `src/models/AuthSchema.ts` — Drizzle schema (source of truth); `migrations/` — drizzle-kit SQL
  - `src/libs/` — `Env.ts` (validated env, `@t3-oss/env`), `auth-server.ts`, `auth-client.ts`, `auth-permissions.ts` (access-control model), `Access.ts` (`getAccessContext`, `requireOperator/Owner/Teacher`), `auth.ts` (`requireOrgId`), `Email.ts`
  - `src/proxy.ts` — the Next 16 middleware (next-intl + Better Auth session gate)
  - `src/utils/Format.ts` — Malaysian date/time/money formatters
  - `tests/e2e/{smoke,t1,t2}/` — Playwright suites (~548 cases total)
- **Product docs (LOCAL-ONLY, gitignored):** `~/Projects/Sifututor/docs/products/group-class-saas/` — the real planning/spec/history set: `PRD.md`, `DATA-MODEL.md`, `OVERVIEW.md`, `FLOWS.md`, `BUILD-LOG.md`, `SESSION-HANDOFF.md`, `LAUNCH-READINESS.md`, `MVP-READINESS.md`, `EXECUTIVE-SUMMARY.md`, `BETA-GO-LIVE.md`, design/UX audits, and a **`qa/` folder** (a ~700-case QA catalog + findings). **Review these too.**
- **Repo docs:** `kelas/README.md`, `kelas/DEPLOY.md`, `kelas/AGENTS.md`, `kelas/CLAUDE.md`, `kelas/.agent-os/project-profile.md`, `kelas/docs/legal/` (privacy/terms drafts — gitignored).

## 4. Read these FIRST to orient (before going deep)

`kelas/CLAUDE.md`, `kelas/AGENTS.md`, `kelas/README.md`, then `docs/products/group-class-saas/PRD.md`, `DATA-MODEL.md`, `OVERVIEW.md`, `FLOWS.md`, and skim `BUILD-LOG.md` + `SESSION-HANDOFF.md` for history and current state. Then inspect `src/models/Schema.ts` and a couple of `src/features/*/service.ts` to learn the patterns before auditing breadth.

## 5. Review dimensions (be exhaustive; organise your report by these)

1. **Tenant isolation / multi-tenancy (highest priority).** This is a multi-tenant system — a cross-tenant data leak is a P0. Verify that **every** DB query, route handler, server action, and public endpoint is scoped by the active organisation (`orgId`) and respects soft-deletes. Look specifically for any query that could return or mutate another tenant's rows, any `orgId` taken from client input instead of the session, and any place a resource id is trusted without an ownership check.
2. **Auth & authorization.** The Better Auth org model with **assigned** roles `operator / staff / teacher` (see `auth-permissions.ts`, `Access.ts`). Verify role enforcement on every protected route/action, the middleware (`src/proxy.ts`), removed-member handling, invite acceptance, and teacher self-service (a teacher must only see their own classes/pay/payslip). Look for privilege-escalation and missing guards.
3. **Public / unauthenticated surface.** The tokenised public invoice page `/invoice/[token]`, the self-service **receipt upload** (parents upload files + amounts, no login), password reset/verification, and the Sentry `/monitoring` tunnel route. Audit for: token guessability, IDOR, file-upload abuse (type/size/content, HEIC/PDF handling via sharp + `pdftoppm`), input validation, rate-limiting, and data exposure.
4. **Money / billing correctness.** Amounts are stored as strings and computed in **integer cents**. Deeply check: invoice lifecycle (draft → issued → partially paid → paid → overdue → voided), payments, refunds, discounts/adjustments, the void-guard on paid/partly-paid invoices, self-service claim caps, and **teacher-pay/payouts** (per-class rate frozen at attendance, pay-run draft/paid/void, adjustments). Look for rounding drift, float leaks, negative-amount handling, and re-run idempotency.
5. **Data model & migrations.** Schema integrity, foreign keys, indexes (and missing ones), soft-delete consistency, N+1 query patterns (services claim to batch reference lookups — verify), and migration safety/ordering. Confirm `Schema.ts` matches the migrations and the running DB expectations.
6. **Feature completeness vs. the PRD.** Cross-check each domain against `PRD.md` and `MVP-READINESS.md`/`MVP-GAP-CHECK.md`: what is claimed done, what is actually done, what is stubbed, what diverges. Flag PRD ↔ code drift in both directions.
7. **i18n & Malaysian formatting.** EN/BM key parity (`src/locales/en.json` vs `ms.json`), all user-facing strings routed through next-intl, all dates/money/times through `src/utils/Format.ts` (never `en-US`). Find hard-coded strings and format leaks.
8. **Testing.** Assess the Vitest unit/service tests and the Playwright suites (`tests/e2e/{smoke,t1,t2}`) for **coverage gaps and quality** — which critical paths (esp. money, tenant isolation, public endpoints) are under-tested or only happy-path tested. Do not just count tests; judge what they actually prove.
9. **Code quality & correctness.** Error handling (silent failures, swallowed catches), type safety (any `as`/`any` escape hatches, unchecked nullables), transaction boundaries (multi-write operations must be atomic), race conditions, and adherence to the stated service-layer pattern.
10. **UX/UI & accessibility.** Design-system consistency, responsive behaviour (down to 375px), light/dark, accessibility (labels, focus, contrast), and the project's stated UI conventions (see `UI-CONVENTIONS.md` + `DESIGN-AUDIT.md`): action-bar pattern (primary + grouped + overflow), and **no side/accent bars** (background tint + coloured text instead).
11. **Security (general).** Input validation (zod on both client and server), SQL injection (Drizzle parameterisation), secrets handling, CSRF/origin checks, security headers/CSP (`next.config.ts` ships a report-only CSP — assess it), and dependency risk.
12. **Docs quality.** Accuracy, internal consistency, and gaps across the repo + product docs (they were recently synced — verify that and find what's still stale, thin, or contradictory). Include the legal drafts (`docs/legal/`, PDPA + minors' data).
13. **Ops / deploy / resilience.** Read `DEPLOY.md` and `BETA-GO-LIVE.md`: assess the deployment model, env/secret handling, backup + restore story, monitoring, and single-points-of-failure. Comment on what a real customer's data going live would stress.

## 6. Grounding facts & INTENTIONAL decisions — do NOT flag these as bugs

- **Clerk was fully removed (2026-07-02); auth is Better Auth.** BUT the DB columns named `clerk_user_id` were **deliberately kept** and now hold the Better Auth user id (a rename is deferred). Do not flag the column names as a bug — note it once, at most.
- **The product docs and `kelas/docs/legal/` are gitignored** by design (local-only working docs). That is intentional, not a mistake.
- **Landing + Terms carry parked "paid tiers / 30-day free trial" copy that is NOT yet true** (the beta is free). This is a **known, accepted pre-public-launch gate** (tracked as items E1-E3 in `LAUNCH-READINESS.md`) — flag only as a pre-public reminder, not a defect.
- **DuitNow QR is a self-minted static display; there is no payment gateway (PSP) yet.** Payments are manual: parents upload receipts, operators verify. Auto-confirmation / dynamic QR / PSP are explicitly deferred. Do not flag "no online payments" as a gap.
- **Deploys are currently manual** (the org blocks GitHub deploy keys at the enterprise level; a webhook receiver exists but is unused). Known.
- **Prod/staging secrets live in `.env.local` (gitignored), never the tracked `.env`.** The tracked `.env` is boilerplate. Do not "fix" that.
- **`next start` runs with NO `-H` flag on purpose** (binding to localhost breaks next-intl rewrites behind the TLS proxy). Do not recommend adding `-H`.
- Money as integer cents, lazy session materialisation, and manual-first billing are deliberate architecture, documented in the PRD/DATA-MODEL — critique their implementation, not their existence.

## 7. Guardrails (hard rules)

- **READ-ONLY.** Do not modify, refactor, or "fix" any code, and do not open PRs. Analysis and comments only. (If asked to fix later, that will be a separate task.)
- **Do not touch the live servers.** Do not SSH to, deploy to, run migrations against, or send traffic to prod/staging (`kelasapp.learnestlab.com` / `staging.kelasapp.learnestlab.com`). This is a live system.
- **Never read `.env` / `.env.local` / any secrets**, and never print secret values.
- **Do not run destructive or state-changing commands.** Safe local read-only checks are fine (e.g. `npm run check:types`, `npm run lint`, `npx knip`, `npm run check:i18n`, `npm run test`) **only if** you can run them on **Node 24** — otherwise just read. Do not run `db:seed` (it wipes data). Do not `db:migrate` against anything real.
- Stop the dev server (if you start one) with SIGTERM — **never `kill -9`** (it corrupts the PGlite `local.db`).

## 8. How to work

- Ground yourself in the orientation docs (§4) before judging.
- **Verify behaviour in the code**, reading both client and server layers of a flow, before asserting how it behaves (e.g. don't claim a validation exists/doesn't without checking both the zod schema and the handler).
- Prefer **depth on the critical lanes** (tenant isolation, auth, money, public endpoints) over breadth on trivia.
- Separate **defects** (it's wrong / it leaks / it crashes) from **risks** (fragile, untested) from **improvements** (nicer) from **questions** (I need the owner to confirm intent).
- Be concrete: every finding needs `file:line`, a one-line statement of the problem, a concrete failure scenario or reason it matters, and a suggested direction (not a full patch).

## 9. Deliverable format

Produce a single structured report:

1. **Executive summary** — the overall health verdict, the top 5–10 things that matter most, and an honest read on "is this safe to take a real customer's data on Monday?"
2. **Findings by dimension** (§5), each finding tagged with a **severity**: `Critical` (data loss / cross-tenant leak / auth bypass / money wrong) · `High` · `Medium` · `Low` · `Nit`, plus a type: `Defect` / `Risk` / `Improvement` / `Question`. Include `file:line`, the problem, why it matters (concrete scenario), and a recommended direction.
3. **Prioritised action list** — the findings ranked as a to-do (most severe first), so the owner can work top-down.
4. **What's good** — call out genuinely solid patterns worth preserving (so refactors don't regress them).
5. **Open questions for the owner** — anything where intent is ambiguous and a wrong assumption would make your finding wrong.

Take the time to be thorough. This is the foundation for the next phase of work on a system about to hold a real Malaysian tuition centre's students', guardians', and financial data.
