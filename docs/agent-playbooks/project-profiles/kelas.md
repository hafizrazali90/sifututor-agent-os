# Agent OS Project Profile: Kelasapp

Use this profile before starting Kelas app work from the Sifututor Agent OS.

Plain meaning:

```text
The shared Agent OS says how to work.
This profile says how the Kelas app actually builds, tests, deploys, and proves
work.
```

## Profile Status

| Field | Value |
| --- | --- |
| Project | `kelas` / `kelasapp` |
| Adoption state | `profile drafted; local Agent OS integration installed` |
| Last verified | `2026-07-02 from local checkout on feat/launch-readiness` |
| Verified by | `Codex` |
| Main owner | `Hafiz / Learnest Lab` |
| Profile location | Umbrella draft: `docs/agent-playbooks/project-profiles/kelas.md`; product profile: `kelas/.agent-os/project-profile.md`; product rules: `kelas/AGENTS.md`, `kelas/CLAUDE.md` |

This is a draft profile with local Agent OS integration installed, not yet a
verified developer-staff rollout profile. It was created from safe read-only
evidence in the local checkout at `/Users/hafizrazali/Projects/Sifututor/kelas`,
which points to `https://github.com/Learnest-Lab/kelasapp.git`. The checkout is
currently on `feat/launch-readiness`, and the working tree has untracked
`audit-screenshots/` plus unrelated PDF/report files. Product `AGENTS.md`,
`CLAUDE.md`, `.agent-os/project-profile.md`, and `.claude/tasks` wiring were
added and committed locally on 2026-07-02 in Kelas commit `d72c4b5`.

## Plain Summary

Kelasapp is a web-first SaaS for Malaysian tuition and mengaji centres. It helps
centres manage classes, teachers, guardians, students, enrolments, attendance,
reports, invoicing, payments, public invoice links, receipt upload, and
operator verification. It is multi-tenant through Clerk Organizations,
bilingual through `next-intl`, and uses Malaysian defaults for dates, timezone,
and RM money formatting.

## Repo Facts

| Field | Value |
| --- | --- |
| Purpose | Group-class management for Malaysian tutor and mengaji centres. |
| Primary users | Centre operators/staff, teachers, guardians/parents, and public invoice visitors. |
| Stack/runtime | Next.js 16 App Router, React 19, TypeScript, Clerk Organizations, Drizzle ORM, PostgreSQL, PGlite for local/tests, Tailwind/shadcn UI, next-intl, Wasabi S3, React PDF, Playwright, Vitest, Storybook, Chromatic. |
| Main source docs | `AGENTS.md`, `CLAUDE.md`, `.agent-os/project-profile.md`, `README.md`, `DEPLOY.md`, `package.json`, `.github/workflows/CI.yml`, `playwright.config.ts`, `vitest.config.ts`, `docs/legal/`, product screenshots/docs under `docs/`. |
| Active task state | `.claude/tasks/active.json` exists and is currently null. |
| Important modules | Classes, teachers, guardians, students, enrolments, attendance, reports, invoicing, media, messaging, onboarding, payouts, dashboard, import, taxonomy. |
| Known local conventions | Node 24 required; bilingual English + Bahasa Melayu is mandatory; strings should use `next-intl`; dates/money should use Malaysian formatting helpers; services are org-scoped and tested with PGlite; branches follow short-lived `feat/*`, `fix/*`, `chore/*`, `docs/*`; commits use gitmoji conventional commits. |

## Commands

Commands below are verified from `README.md`, `DEPLOY.md`, `package.json`, and
GitHub Actions. They were not executed as readiness proof because the current
local shell is Node `v20.20.2`, while Kelas requires Node 24.

| Purpose | Command | Verified? | Notes |
| --- | --- | --- | --- |
| Install JS deps | `npm ci` | yes, not run | CI and deploy docs use npm. Requires Node 24. |
| Local dev server | `npm run dev` | yes, not run | Runs PGlite file server plus Next dev server. |
| Build | `npm run build-local` or `npm run build` | yes, not run | CI uses `build-local`; production build runs migrations then `next build`. |
| Start production server | `npm run start` | yes, not run | Runs `next start`, usually behind PM2/reverse proxy. |
| Lint | `npm run lint` | yes, not run | `DEPLOY.md` says lint could not run on Node 20; must run on Node 24. |
| Typecheck | `npm run check:types` | yes, not run | Runs `tsc --noEmit --pretty`. |
| Dependency check | `npm run check:deps` | yes, not run | Runs `knip`. |
| I18n check | `npm run check:i18n` | yes, not run | Validates translation keys. |
| Unit/UI tests | `npm run test` | yes, not run | Vitest unit + browser tests; services use PGlite. |
| E2E tests | `npm run test:e2e` | yes, not run | Playwright starts app on port 3008 with PGlite. |
| Storybook tests | `npm run storybook:test` | yes, not run | CI runs in Playwright Docker image. |
| DB migrations | `npm run db:migrate` | yes, not run | Uses `dotenv -c -- drizzle-kit migrate`; do not read `.env*`. |
| Dev seed | `npm run db:seed` | yes, not run | Dev only; `DEPLOY.md` says do not run in production because it wipes/reseeds demo data. |
| Bucket check | `npm run check:bucket` | yes, not run | Requires Wasabi env; use only with approved scoped access. |
| Media check | `npm run check:media` | yes, not run | Requires env/storage access. |

## Evidence Expectations

| Work type | Expected proof |
| --- | --- |
| Docs-only | Diff/readback plus Agent OS health when workflow docs change. |
| Backend/API/service | Focused Vitest service tests with PGlite, API/route evidence where relevant, tenant `orgId` scoping proof, and migration impact review if schema changes. |
| Browser UI | Browser/Playwright journey or screenshot-backed evidence, bilingual copy check, loading/empty/error states, and responsive check for staff/operator flows. |
| Public invoice/receipt upload | Public unauthenticated invoice journey, invalid/expired token behavior, receipt upload proof, storage boundary review, and operator verification queue proof. |
| Billing/payment/refund/invoicing | Read-only diagnosis first for risky changes, focused tests, cents-based calculation proof, invoice lifecycle proof, idempotency/duplicate-payment thinking, and Hafiz review before release. |
| Auth/tenant/roles | Clerk organization and app-role proof; verify every query is `orgId` scoped and access helpers are used correctly. |
| Storage/media | Wasabi bucket check only through approved scoped access; prove private bucket behavior and safe object references. |
| Release/deploy | Node 24 quality gate, build, migration plan, Hostinger VPS deploy proof, smoke test, and monitoring/log review where available. |

## Critical Lanes

These areas need read-only diagnosis first and explicit approval before
implementation when behavior or risk changes.

| Lane | Why it is sensitive | Required approval/evidence |
| --- | --- | --- |
| Auth/Clerk Organizations/app roles | Can expose tenant data or block operators/teachers. | Read-only diagnosis, tenant isolation proof, role/access tests. |
| Multi-tenancy / `orgId` scoping | Every centre's data must stay isolated. | Query/service review, tests proving cross-org isolation, no unscoped data access. |
| Billing/invoices/payments/refunds | Money state, public invoice pages, receipts, and balance calculations affect customers. | Approval before implementation, cents-based tests, lifecycle proof, public/private journey evidence. |
| Migrations/database schema | Production Postgres data can be damaged or app can fail to boot. | Migration review, local/CI proof, production migration approval. |
| Wasabi media/storage | Receipt uploads and QR assets involve private files and credentials. | Approved access only, no secret exposure, bucket/object proof. |
| Public invoice tokens | Public unauthenticated surface can leak invoice data. | Token validity tests, invalid-token proof, public journey evidence. |
| Deployment/production env | Hostinger VPS deploy affects live product. | Explicit approval, Node 24 build, migrations, smoke test, monitoring. |

## Access And Boundaries

| Area | Rule |
| --- | --- |
| Safe read-only access | Repo docs/code, Git status/diff, package scripts, CI config, local non-secret docs, tests. |
| Forbidden paths | Do not read or modify `.env*`, secrets, raw credentials, or production data dumps. |
| Local generated/runtime dirs | Treat `.next/`, `local.db/`, screenshots, and audit artifacts as generated/runtime evidence unless explicitly assigned. |
| Push/PR/merge/deploy | Requires explicit current-session approval and exact boundary. |
| Production data/actions | No mutation without exact approval; use read-only evidence paths only when scoped. |
| Staff/developer access | Developer reads Agent OS repo plus Kelas repo; normal builder work happens on branches/PRs; Agent OS rule changes are separate workflow-improvement work. |

## Deploy And Release

| Field | Value |
| --- | --- |
| Deploy target | Hostinger VPS according to `DEPLOY.md`. |
| Runtime | Node 24, Postgres, Wasabi storage, Clerk auth, `poppler-utils`, libvips/HEIF considerations for iPhone receipts. |
| Environments | local/dev via PGlite; production via real Postgres and Hostinger VPS; exact staging/preview path unknown. |
| Deploy path | `npm ci`, `npm run build`, `npm run start` under PM2/reverse proxy after env and migrations are approved. |
| Release proof | Source SHA/branch, Node 24 quality gate, migration result, build result, process/reverse-proxy proof. |
| Smoke proof | Sign in, create/select organization, set up class/guardian/student/enrolment, run billing, issue invoice, record payment, open public invoice link, upload receipt, verify pending receipt. |
| Monitoring proof | Sentry/BetterStack/Checkly/host logs if configured and approved; exact production monitoring path is unknown. |

## What Done Means

For normal Kelas code work, done usually means:

```text
The GitHub issue/task is clear, the change is implemented on a branch in the
Kelas repo, Node 24 checks relevant to the change pass, bilingual copy and
Malaysian formatting are respected, the real user journey is proved with
Playwright/browser/API evidence when feasible, critical-lane evidence is
complete when relevant, and the work is committed or prepared for PR at the
approved stop point.
```

What is not done:

```text
Committed is not pushed.
Pushed is not PR-open.
PR-open is not merged.
Merged is not deployed to Hostinger.
Deployed is not smoke-checked.
Smoke-checked is not accepted until Hafiz or the responsible reviewer accepts
the remaining product/business risk.
```

For developer-staff adoption, the first practical finish point should usually
be `PR opened with evidence`, not merge or deploy.

## Known Gaps

| Gap | Impact | Recommended next |
| --- | --- | --- |
| Product repo integration is committed locally but not pushed. | Claude/Codex can use the files locally, but GitHub and other machines will not see them until pushed. | Push Kelas commit `d72c4b5` when approved. |
| Current shell is Node `v20.20.2`, but Kelas requires Node 24. | Local lint/build/test readiness cannot be honestly claimed from this session. | Run Node 24 checks locally through nvm or rely on GitHub Actions for first readiness proof. |
| Existing E2E tests still contain boilerplate French/SaaS-template expectations. | Current E2E suite may not prove real Kelas workflows or bilingual English/Bahasa Melayu behavior. | Replace or extend E2E with Kelas journeys: onboarding/org, classes, guardians/students/enrolments, attendance, billing, public invoice, receipt upload. |
| `DEPLOY.md` says the repo had no remote, but local Git now points to `Learnest-Lab/kelasapp`. | Deploy docs are partly stale. | Update deploy docs after confirming the intended remote/branch/release path. |
| Untracked `audit-screenshots/` exists in the local checkout. | Local worktree has unrelated evidence/artifacts. | Leave untouched unless Hafiz assigns cleanup or review. |
| Exact production URL, staging URL, and monitoring path are unknown. | Release/live proof cannot be fully planned yet. | Confirm deployment environment before release work. |

## Verification Notes

Checked on 2026-07-02 from local checkout
`/Users/hafizrazali/Projects/Sifututor/kelas` on branch
`feat/launch-readiness`:

- `README.md`
- `DEPLOY.md`
- `package.json`
- `.github/workflows/CI.yml`
- `.github/actions/setup-project/action.yml`
- `playwright.config.ts`
- `vitest.config.ts`
- `tests/e2e/*.ts`
- `src/features/*/service.ts` and related service tests list
- Agent OS installer dry-run from umbrella root:
  `scripts/agent-checks/agent-os-install.sh --target kelas`
- Agent OS installer apply from umbrella root:
  `scripts/agent-checks/agent-os-install.sh --target kelas --apply`
- Agent OS installer re-check from umbrella root:
  `scripts/agent-checks/agent-os-install.sh --target kelas`

Still unknown:

- production/staging URLs
- whether the current feature branch is the intended handoff branch
- whether `audit-screenshots/` should be kept, ignored, or cleaned
- whether Kelas integration should be pushed on `feat/launch-readiness` or
  moved to a dedicated Agent OS integration branch

Recommended next:

- Push Kelas commit `d72c4b5` after deciding the correct branch/PR path.
