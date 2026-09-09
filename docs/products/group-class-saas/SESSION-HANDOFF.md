# Kelasapp — Session Handoff / Session Map

**Last updated:** 2026-07-05 — **DEPLOYED: Kelasapp is live in private Beta** (prod <https://kelasapp.learnestlab.com> + staging <https://staging.kelasapp.learnestlab.com> on Hostinger KVM8; Sentry + verified Resend + nightly backups; full record in [BETA-GO-LIVE.md](BETA-GO-LIVE.md)). Prior 2026-07-04 (branch consolidation DONE: build-local green, branches pushed, PR #4 + stacked PR #5 open; QA CATALOG FULLY REVISED: 486 -> 700 cases / 10 modules / 90 smoke, new import plan, findings re-triaged + 9 new findings in qa/README.md; next: findings triage with Hafiz -> T1 smoke E2E conversion; W3 landing unification post-beta)
**Read this FIRST when starting a new Kelasapp session.** It is the pickup point.

---

## 1. One-line status

**PICKUP POINT (2026-07-03, end of day): the external UX/CX audit ([UX-CX-AUDIT.md](UX-CX-AUDIT.md)) is FULLY WORKED - all 16 findings + the LOW batch, one-by-one with Hafiz (explain plainly -> do/defer/skip -> build -> browser-verify -> commit). 25 commits on `feat/finish-mvp-polish` (`917c612`..`b6f474d`), 151 unit tests green. See the BUILD-LOG 2026-07-03 entry for the full per-commit record and the audit doc's "Resolution status (final)" for the finding->commit map. Also shipped along the way: the full table-usability build (# column, search-everything, CSV export, count columns), dark mode with a theme picker, payroll bulk mark-paid, and the /dashboard/import migration hub.**

**Resume with:** the app is **live in private Beta** (deployed 2026-07-05, both environments verified) — the next real step is **Sopan beta prep**: get his Mudeer export, dry-run the migration on **staging** via `/dashboard/import`, then run it for real on prod. (Resend domain is now verified + wired; the ~153 T3 display-polish cases remain an optional visual-QA pass, DuitNow-QR-actually-scans human-only.) ALL PUSHED 2026-07-04 (through `cef754f`): PR #5 = 67 commits + four addenda (triage, smoke, T1, T2). DONE 2026-07-04 (latest): the FULL catalog through T2 is automated: 548 Playwright cases (90 smoke + 149 T1 + 309 T2) green together in 12.5 min on a fresh in-memory DB (`npx playwright test tests/e2e/`, dev stack stopped). T2 specs at kelas/tests/e2e/t2/ (11 files). Ride-along product fix 7539c66: pay/billing period month constrained to 01-12 (was a 500 on "2026-13"). Earlier same day: T1 gate + smoke gate + 12 triage commits pushed (PR #5 = 64 commits, three addenda). DONE 2026-07-04 (latest): the FULL T1 E2E gate is automated: 239 Playwright cases (90 smoke + 149 non-smoke T1) green together in ~5 min on a fresh in-memory DB (`npx playwright test tests/e2e/` with the dev stack stopped). T1 specs at kelas/tests/e2e/t1/ (10 files, auth split a/b). Removed 3 dead starter-template specs. Earlier same day: smoke gate (90 cases) + 12 triage commits pushed. DONE 2026-07-04 (late): ALL 90 @smoke cases automated as Playwright E2E at kelas/tests/e2e/smoke/, full suite green in 1.8 min on a fresh in-memory DB (run with dev stack stopped: `npx playwright test tests/e2e/smoke/`); harness = own-org-per-spec via real sign-up, EMAIL_FILE_SINK inbox for the reset journey, 1 worker (PGlite single-writer), TC ids in test titles. Earlier same day: 12 triage commits pushed (`135ff13..f29ee0b`), PR #5 carries 55 commits + triage addendum. DONE 2026-07-04, in order: branch consolidation (build-local green, branches pushed, PR #5 stacked on PR #4); FULL QA catalog revision (10 parallel module agents; auth plan Clerk -> Better Auth 40 -> 75; NEW test-plan-import.md; 701 cases / 90 smoke); FINDINGS TRIAGE COMPLETE with Hafiz: 6 clear defects fixed (CSV formula guard 421bbac, report BM dates + tooltip 17cc0ed, negative adjustments 70edbfa, import 422 380a374, dialog network-catch c679357, badge filter f406a4c) + 5 product calls decided and shipped (staff rule official f29ee0b, real PII masking b498d68, draft payslips locked 346b4d5, archive guard 667eecb, public pages forced light 4fe0ace). All gates green (160 tests). Only accepted i18n residuals remain (weekday row, import server warning strings).

(Resolved: the earlier "working-tree discovery" warning about uncommitted CX11 work - that WAS this session's in-flight scaffold, since completed and committed as `ab86cf3`. Nothing foreign.)

Dev fixtures as of end of session: teacher@kelastest.local linked to Ustazah Fatimah; ALL July payouts now paid (2 staged drafts were paid via the real bulk flow); RM 40 pending claim on INV-202607-0003 = pending-receipt fixture; org payment settings intentionally EMPTY (exercises the CX15 fallback); browser theme reset to light.

Two big things landed (2026-07-02): (1) **class + enrolment CSV import** (finish-MVP item 1) built + committed; (2) a **full migration off Clerk to Better Auth** — self-hosted auth in our own Postgres, done as a 6-slice cutover: foundation, cutover + Clerk removal, **link/WhatsApp member invites with ASSIGNED roles** (the old email-guess footgun is gone), **password reset + email verification via Resend**, and **teacher self-service** (my-classes, my-pay, own-payslip download). All verified in-browser, **production build passes**, all gates green on every commit. On branch `feat/better-auth-migration`.

**Resend: RESOLVED 2026-07-05.** Domain `kelasapp.learnestlab.com` verified; `EMAIL_FROM` switched to branded `no-reply@kelasapp.learnestlab.com`; a real branded send was confirmed; the prod key is Sending-only. Email is fully wired in production.

## 2. Where the code is

- **Repo:** `kelas/` (Next.js 16, at `~/Projects/Sifututor/kelas`). Remote: `github.com/Learnest-Lab/kelasapp`.
- **Active branch:** `feat/finish-mvp-polish` (stacked on `feat/better-auth-migration` on `feat/launch-readiness`). **ALL PUSHED (2026-07-04).** Open PRs: **#4** better-auth-migration -> launch-readiness (auth review) and **#5** finish-mvp-polish -> better-auth-migration (UX/CX audit + tables + design system, 43 commits, build-local green). Merge order: #4 then #5, then launch-readiness -> main when ready for beta.
- **Commits (newest first):**
  - `b175d3e` teacher self-service (my-classes, my-pay, own payslip)
  - `06b08ab` password reset + email verification via Resend
  - `37d499e` link-based member invites with assigned roles
  - `ddb9f4d` Clerk → Better Auth cutover + Clerk fully removed
  - `684d456` Better Auth core + org role model + schema (migration 0014)
  - `22edd5b` ghost-button UI affordance fixes · `f32d068` class + enrolment CSV import (on `feat/launch-readiness`)
- **Polish batch + QA fixes on `feat/finish-mvp-polish`** (branched off `feat/better-auth-migration`): `ac1926b` CSV import fixes (tolerant time parsing + no more silent row drop, from the first manual QA pass) · `261e141` remove/replace payment receipt · `2d5ff12` teacher grade-history · `f182293` invite-row align · `561d9ab` auth-screen branding.
- Working tree clean apart from gitignored `local.db*` + untracked `audit-screenshots/`.

## 2b. Auth migration state (read before touching auth)

- **Model:** Better Auth `organization` plugin = tenant boundary (one org = one centre). Roles **operator / staff / teacher** are defined in `src/libs/auth-permissions.ts` (access-control statements) and **assigned on the membership** (creatorRole=operator; invitees get the role the operator picked). Server instance: `src/libs/auth-server.ts`. Client: `src/libs/auth-client.ts`. Route handler: `src/app/api/auth/[...all]`.
- `src/libs/Access.ts` (`getAccessContext`, `requireOperator/Owner/Teacher`) + `src/libs/auth.ts` (`requireOrgId`) read the Better Auth session + active org + member role. Middleware = `src/proxy.ts` (`getSessionCookie`). **Clerk is fully removed** (no packages, env, code, CSS). Schema: `src/models/AuthSchema.ts` (user/session/account/verification/organization/member/invitation).
- **Teacher linking:** a teacher-role member auto-links to the `teachers` record matching their email on first login (column still named `clerkUserId`, repurposed to hold the Better Auth user id; rename is a deferred cleanup). Role is ASSIGNED, email only picks which teacher record.
- **Invites:** link-based (no email). Operator creates an invite (Members section of `/dashboard/organization-profile`), shares the `/accept-invite?invitationId=…` link via copy/WhatsApp. Invitee signs up with the invited email → joins with the assigned role.
- **Env (`.env.local`, gitignored):** `BETTER_AUTH_SECRET`, `BETTER_AUTH_URL=http://localhost:3000` (dev). **Production** (on KVM8) uses `APP_ENV=production`, a Sending-only `RESEND_API_KEY`, branded `EMAIL_FROM=Kelasapp <no-reply@kelasapp.learnestlab.com>`, `NEXT_PUBLIC_SENTRY_DSN`, and the prod URLs. Dev `.env.local` may still use the `onboarding@resend.dev` test sender.
- **Resend:** domain `kelasapp.learnestlab.com` id `21896fa1-631e-478d-89a9-becdd8394ee3`, region `ap-northeast-1`. Namecheap records (all live + correct per dig): DKIM TXT `resend._domainkey.kelasapp`, MX `send.kelasapp` → `feedback-smtp.ap-northeast-1.amazonses.com` prio 10, SPF TXT `send.kelasapp`. M365 root email untouched (subdomain isolation).
- **Dev test accounts (in local.db):** `operator@kelastest.local` (pw `newpassword6789`, org "Sinar Ilmu Test Centre", operator) · `teacher@kelastest.local` (pw `password12345`, teacher, joined via invite) · `hafiz.razali@sifututor.my` (throwaway, pw `temp-Reset-Me-12345`, for the email test).
- **DEV DB LESSON:** stop the dev server with **SIGTERM** (`pkill -TERM …` / normal stop), **never `kill -9`** — it corrupts the PGLite `local.db`. (It was corrupted + recovered this session; corrupt copy preserved as `local.db.corrupt-*`.)
- **Deploy: DONE 2026-07-05.** Live on Hostinger **KVM8** (Node 24 + PM2 + nginx + local Postgres 16): prod `kelasapp.learnestlab.com`, staging `staging.kelasapp.learnestlab.com`. DNS on Namecheap (A records live); `learnestlab.com` stays on Namecheap (M365 email untouched). `BETTER_AUTH_URL`/`NEXT_PUBLIC_APP_URL` set to the real domains; `APP_ENV` gates prod-only monitoring/email. Deploys are manual (org blocks deploy keys). See [BETA-GO-LIVE.md](BETA-GO-LIVE.md).

## 2c. Remaining follow-ups
- ~~Finish Resend~~ — **DONE 2026-07-05** (domain verified, branded `EMAIL_FROM`, real send confirmed, Sending-only key).
- Open PR(s) to merge `feat/better-auth-migration` (brings the import work too) into the main dev line.
- Marketing copy still says "30-day free trial" (parked Wave 7) — contradicts the free-beta model; fix before public.
- Optional: update `scripts/seed-dev.cjs` to create a Better Auth org so a fresh login sees sample data (currently seeds under the old Clerk-style org id).
- ~~Finish-MVP item 3 polish batch~~ — **DONE 2026-07-02** on branch `feat/finish-mvp-polish` (a grade-history `2d5ff12`; b ClassForm hint + c payroll empty state already present; d remove/replace receipt `261e141`, browser-verified). **Finish-MVP scope (items 1–3) complete; item 4 deferred.**
- **NEXT PHASE = testing, IN PROGRESS.** First manual QA pass done 2026-07-02 (fixed 2 CSV-import bugs `ac1926b` + an attendance plural). Then a **deep 4-agent MVP-readiness audit** (2026-07-02/03, see [MVP-READINESS.md](MVP-READINESS.md)) found no blockers but 4 HIGH + a 9-item MEDIUM cluster + 2 ops items — **all now fixed** on `feat/finish-mvp-polish` (commits `2b53ee7` → `a5d67a2`), each TDD'd/browser-verified EN+BM, **production build green**. Highlights: removed-member deny (H1), the whole payment-claim flow reshaped incl. Remove-payment + void-money guard (H2/M1), attendance roster check (H3), prod mailer/Sentry guards (H4/Ops-2), billing made transactional (M4), BM date pickers + sidebar + Powered-by (M2/M8/M9), silent-failure surfacing (M3), public-endpoint hardening (M5), invite-landing + centre switcher (M6). Full list in BUILD-LOG's 2026-07-02/03 entry.
- **Only deferred now:** the LOW tier + the 486-case QA-catalog refresh (testing-phase work).
- **Still to decide:** build Playwright E2E for the now-hardened journeys, or continue manual QA (self-service payment, teacher self-service, invites) toward Sopan's private beta. Also: the branch stack (`feat/finish-mvp-polish` → `feat/better-auth-migration` = PR #4, still open → `feat/launch-readiness`) needs consolidating/merging at some point.

## 3. Node / dev / verify (Node 24 required)

- Node: `~/.nvm/versions/node/v24.18.0/bin` — prefix commands with `export PATH="$HOME/.nvm/versions/node/v24.18.0/bin:$PATH"`. Commit hooks (commitlint) need Node 24 or they silently fail.
- Dev server: `npm run dev` (was running on localhost:3000 during this session; kelas_dev Postgres on :5432, all migrations applied).
- Verify: `npm run check:types` · `./node_modules/eslint/bin/eslint.js --fix <files>` · `npm run check:deps` (knip) · `npm run check:i18n` · `npx vitest run <file>`.
- **i18n note:** `check:i18n` will always flag `FAQ.items` + `Help.faq` as "undefined keys" — that's the array-access pattern, NOT a real error (keys exist in both locales).
- **Tests:** node project = `*.test.{js,ts}` (unit, node env); `*.test.tsx` = browser project (Playwright, chromium not installed here — avoid). Put pure-logic + PDF-render tests in `.test.ts`.
- **Standing rule:** after any schema/migration change, run `npm run db:migrate` on the dev DB + load the affected page before calling it done (green tsc/tests is not enough — tests use fresh PGlite).

## 4. What this session did

- **Launch gate (waves 1-6)** — safety net, company setup, onboarding checklist, CSV importer, in-app help + legal, branding (logo + "Powered by Kelasapp"). (Committed earlier in branch.)
- **Customer-facing document redesign** (`3eb37b1`, `ca1dee5`), user-approved after viewing rendered PDFs:
  - New dedicated `InvoicePdf` + `PayslipPdf` components + shared `tokens.ts` (slate + teal). Old generic-report reuse was the "data dump" cause.
  - Direction chosen: **Minimal + tinted total** (whitespace, thin rules, teal only as accent, totals in a subtle grey box with Balance Due / Net pay in teal).
  - Fixed the **logo not rendering on PDFs**: `getBrandLogoUrl` now fetches the image and returns a **base64 data URI** (react-pdf couldn't reliably fetch remote signed URLs during server render).
  - Public payment page matched to the same style (line items + tinted totals box). Payment logic untouched.
  - Render smoke tests added (invoice/payslip/attendance).
- **MVP gap check** — 3 parallel read-only audits (billing, attendance/payroll, onboarding/settings/CRUD) + PRD/BUILD-LOG review. Full report: **`MVP-GAP-CHECK.md`** (same folder).
- **Finish-MVP item 1: class + enrolment CSV import — BUILT** (TDD). Full detail in BUILD-LOG.md's 2026-07-02 "finish-MVP item 1" entry. Short version: `config.ts` gained `classes`/`enrollments` entity definitions with raw-row schemas that parse free-text days ("Mon,Wed,Fri" + English/Malay names)/enum labels and apply the manual form's defaults for blanks; `server.ts` resolves program/level/teacher/student/class by case-insensitive name (fetched once per run, not per row) and fails just that row on a not-found/ambiguous name; fixed a latent `ImportWizard.tsx` bug that hardcoded the preview gate to a `name` column (would have broken `enrollments`, which has none). 19 new tests + full regression green, tsc/lint/knip/i18n all clean. **Not yet committed. Live browser walkthrough not done** (no dev login in the automated browser this session) — click through `Import classes` / `Import enrolments` for real before treating it as fully verified.

## 5. Decisions locked / pending (IMPORTANT for pickup)

- **Roadmap (locked):** finish MVP → revisit test plan + run full E2E → fix → manual QA → hand to **Sopan** (first real user, migrates data from **Mudeer**) → stabilise in private use → **only when opening to public** do Wave 7 (marketing/Terms copy) + deferred items. (See memory `kelasapp_launch_sequencing`.)
- **Wave 7 (marketing/Terms "free beta / early adopters" copy reframe): PARKED** until public open. Approved wording is ready in `LAUNCH-READINESS.md` → "Parked copy drafts". Do NOT apply it for the Sopan beta.
- **Class + enrolment CSV import: CONFIRMED — build it** (extends the Wave 4 importer at `src/features/import/`, currently students/teachers/guardians only). Biggest lever for Sopan's Mudeer migration.
- **Teacher self-service payslip: CONFIRMED (2026-07-02) — build it.** Current invite flow (works today): operator creates a teacher record with the teacher's email → invites that same email as a Clerk org member (Settings → Members) → on first login `getAccessContext()` (`src/libs/Access.ts`) matches the member's email to the unlinked active teacher record (`linkTeacherByEmail`), sets `teachers.clerkUserId`, and resolves them to the **Teacher** role (Attendance + own classes only). **To build:** teacher can view their OWN payslip (today `/api/payouts/[id]/pdf` is `requireOperatorContext` — operator-only) + a teacher payout list + a `/dashboard/my-classes` schedule page. **Gotcha to fix/guard:** role is derived from the email match, so inviting a member whose email does NOT match a teacher record silently makes them **staff**, not a teacher.
- **M7 AI Layer: deferred post-beta** (the one unbuilt PRD module; not needed to run a centre).

## 6. Agreed "finish MVP" build scope (start here next session)

1. ~~**Class + enrolment CSV import**~~ — **DONE 2026-07-02** (see section 4). Not yet committed; live browser walkthrough still pending.
2. **Teacher self-service** (CONFIRMED) — **start here next.** Teacher-scoped payslip view (allow a teacher to fetch their OWN payout PDF; currently `/api/payouts/[id]/pdf` is `requireOperatorContext`) + a teacher-visible payout list + a `/dashboard/my-classes` schedule page. Also consider guarding the invite footgun (member whose email doesn't match a teacher record silently becomes staff).
3. **Should-fix polish batch:** (a) write `teacher_grade_history` on grade change in `updateTeacher` (table exists, never written); (b) ClassForm "create a teacher first" hint when none exist (mirror `EnrollPanel`); (c) payroll page empty-state message; (d) remove/replace-receipt action on a payment.
4. **Defer:** M7 AI + all "Minor / post-beta" items in `MVP-GAP-CHECK.md`.

Then: freeze → revisit the parked **486-case QA catalog** (`docs/products/group-class-saas/qa/`) → convert smoke cases to E2E → run full E2E → fix everything → manual QA.

## 7. Authoritative docs (all in `docs/products/group-class-saas/`, gitignored/local)

- **`SESSION-HANDOFF.md`** (this file) — pickup point.
- **`MVP-GAP-CHECK.md`** — full gap audit + prioritized list (2026-07-02).
- **`PRD.md`** — MVP requirements. NOTE its "Build status" table is STALE (dated 2026-06-27, pre-M4/M6); trust BUILD-LOG + the gap check for what's actually built.
- **`BUILD-LOG.md`** — running decision/build log (has a 2026-07-02 entry for this session).
- **`LAUNCH-READINESS.md`** — launch punch-list; waves 1-6 done; Wave 7 parked copy drafts live here.
- **`FLOWS.md`, `DATA-MODEL.md`, `UI-CONVENTIONS.md`** — flows, schema, UI rules. `src/models/Schema.ts` is the schema source of truth.

## 8. Key product facts (so the next session doesn't re-derive)

- Product name is **Kelasapp** (never just "Kelas"). Malaysian formats (DD/MM/YYYY, Asia/KL 12h, RM) via `src/utils/Format.ts`. **No em dashes** in any copy/UI/docs.
- Teachers are **sessional contractors** — pay = sessions × class rate, NO statutory deductions.
- 3 roles: Operator (Clerk admin) / Staff (member) / Teacher (member linked). Owner-only gates on payment settings.
- Every SIMS-style rule does NOT apply here (this is Postgres/Drizzle, not the SIMS MySQL). Multi-tenant by Clerk org; every query scoped by `orgId`.
- DuitNow QR self-mint does NOT embed amount without a PSP (tested) — Kelasapp uses static QR display.
