# Agent OS Project Profile: ripple-suite

Use this profile before starting `ripple-suite` work from the Sifututor umbrella
workspace.

Plain meaning:

```text
This tells the shared Agent OS how Ripple Suite actually works.
It is verified as an umbrella project profile, but it is not yet promoted into
the product repo and it is not yet a developer-staff rollout profile.
```

## Profile Status

| Field | Value |
| --- | --- |
| Project | `ripple-suite` |
| Adoption state | `profile verified` |
| Last verified | `2026-06-30 against clean origin/main checkout af0222b` |
| Verified by | `Codex` |
| Main owner | `Hafiz / Sifututor Engineering` |
| Profile location | Umbrella profile: `docs/agent-playbooks/project-profiles/ripple-suite.md`; product rules: `ripple-suite/AGENTS.md`, `ripple-suite/CLAUDE.md`, `ripple-suite/GOALS.md`, `ripple-suite/TESTING.md`, `ripple-suite/AI-RULES.md` |

This is verified as an umbrella profile because it was checked against a clean
temporary worktree from `origin/main` at `af0222b`, with safe command-manifest
readback, testing-manifest readback, deployment-doc readback, and Agent OS
install dry-run evidence. It is not yet `ready for developer staff use` because
the profile has not been promoted or linked inside the product repo, optional
local Agent OS baseline files are still missing, and product test/build commands
were not executed as readiness proof.

## Plain Summary

`ripple-suite` is the internal staff hub for Sifututor operations. It is a
Next.js dashboard for matching, profiles, roles, AI usage, tutor ratings,
accounts, bank/gateway reconciliation, knowledge assistant, tutor payments,
payment vouchers, CRM, collection, help, settings, and release/admin workflows.
It reads SIMS MySQL as source-of-truth data, writes Ripple-owned data to
PostgreSQL, and handles finance/operations workflows where test evidence and
release proof need to be stronger than ordinary UI changes.

## Repo Facts

| Field | Value |
| --- | --- |
| Purpose | Internal staff operations hub running alongside SIMS. |
| Primary users | Internal staff/admins, finance, matching, collection, sales/CRM, operations, and admins. |
| Stack/runtime | Next.js 16 App Router, React 19, TypeScript 5, Tailwind v4, MySQL via `mysql2` for read-only SIMS data, PostgreSQL on KVM8 for Ripple-owned data, Playwright, Vitest. |
| Main source docs | `ripple-suite/AGENTS.md`, `ripple-suite/CLAUDE.md`, `GOALS.md`, `TESTING.md`, `AI-RULES.md`, `CODEX-WORKFLOW.md`, `CONTEXT.md`, `docs/INDEX.md`, `docs/guides/`, `docs/deployment/infrastructure.md`. |
| Active task state | `.claude/tasks/active.json` exists; active task was `null` when checked. |
| Important modules | Matching, profiles, roles, usage, rating, accounts, reconciliation, knowledge, tutor-payments, collection, CRM, PV, settings, help, releases. |
| Known local conventions | Read `GOALS.md` first; read `TESTING.md` before dashboard/API/sync/finance/operations behavior changes; use TDD for feature/bugfix/hotfix work; keep module `spec.md` files current; add every new API route to `src/middleware.ts` permissions; branch names include GitHub issue number for coding work. |

## Commands

Commands below were verified from a clean `origin/main` checkout using
`npm pkg get scripts` and project docs. Marked `yes` means the command exists in
current repo manifests or docs. It does not mean the full command was run.

| Purpose | Command | Verified? | Notes |
| --- | --- | --- | --- |
| Install JS deps | `npm install` or `npm ci` | yes | Local setup docs and normal npm project conventions apply; exact environment setup still depends on approved credentials/config outside the repo. |
| Local dev server | `npm run dev` | yes | Runs `next dev`; project docs say local dev uses configured dev/staging DBs. |
| Build | `npm run build` | yes | Runs `next build`. |
| Typecheck | `npx tsc --noEmit` | yes | Listed in `AGENTS.md`. |
| Lint | `npm run lint` or `npx @biomejs/biome ci .` | yes | `package.json` has `npm run lint`; `AGENTS.md` also lists Biome CI. Use the repo's current route requirement before completion. |
| Unit tests | `npm run test:unit` | yes | Runs `vitest run`. |
| Unit coverage | `npm run test:unit:coverage` | yes | Runs `vitest run --coverage`. |
| QA runner | `npm run qa` | yes | Runs `tsx scripts/qa/run.ts`. |
| QA preflight | `npm run qa:preflight` | yes | Runs `tsx scripts/qa/preflight.ts`. |
| Playwright E2E | `npm run test:e2e` | yes | Runs `npx playwright test --project=e2e`. |
| Playwright API | `npm run test:api` | yes | Runs `npx playwright test --project=api`. |
| Smoke tests | `npm run test:smoke` or `npx playwright test --grep @smoke` | yes | Listed in package scripts and `AGENTS.md`. |
| DB checks | `npm run test:db` | yes | Runs `tsx scripts/qa/db-checks.ts`. |
| All browsers | `npm run test:all-browsers` | yes | Runs selected Playwright browser projects. |
| Payment audit | `npm run audit:payments` | yes | Read/audit-oriented payment integrity check. |
| Payment repair planning | `npm run repair:payments:plan` and `npm run repair:standalone-payments:plan` | yes | Planning commands; do not treat as write approval. |
| Local PostgreSQL | `docker compose up -d postgres` | yes | Listed in `AGENTS.md` for local PostgreSQL. |
| Test coverage manifest check | `python3 ../scripts/agent-checks/test-coverage-manifest-check.py --project .` | yes | Required by shared Agent OS when changing user-facing behavior. |

## Evidence Expectations

| Work type | Expected proof |
| --- | --- |
| Docs-only | Readback/diff checks plus Agent OS checks when docs affect workflow. |
| Backend/API | Focused API/server tests, permission checks, contract shape evidence, and SIMS read-only/soft-delete review when SIMS data is touched. |
| Browser/dashboard UI | `TESTING.md` row identified, focused Playwright/browser evidence, screenshot or human-journey proof where useful, and loading/error/empty states. |
| Finance/reconciliation/accounts/PV/tutor payments | Read-only diagnosis first, focused tests, API/E2E proof, idempotency/error evidence, SIMS/Ripple parity review where relevant, and release communication if staff behavior changes. |
| SIMS data access | Prove SIMS queries are read-only and include `deleted_at IS NULL` on every SIMS table. |
| Route/API permission changes | `src/middleware.ts` `ROUTE_PERMISSIONS` updated and permission tests or smoke evidence included. |
| Migrations/production DB changes | Migration SQL with safe guards, staging application proof, explicit production migration approval, production application proof, and monitoring/smoke evidence. |
| Release/deploy | Branch/SHA, KVM8 deploy proof, smoke, PM2/HTTP/API/browser evidence, and monitoring/log review where relevant. |

## Critical Lanes

These areas need read-only diagnosis first and explicit Hafiz approval before
implementation when the task changes behavior or risk.

| Lane | Why it is sensitive | Required approval/evidence |
| --- | --- | --- |
| SIMS MySQL access | SIMS is source-of-truth and must be read-only from Ripple. | Prove no SIMS writes, `deleted_at IS NULL` filters, and safe query paths. |
| Auth/RBAC/route permissions | New API routes can 403 or expose sensitive staff/finance data. | Update `src/middleware.ts`, run permission/API tests, and review access impact. |
| Accounts/reconciliation/payment receipts/PV/tutor payments | Money records, finance workflows, SIMS sync, QuickBooks/FIUU/bank evidence, and staff decisions can be affected. | Read-only diagnosis, focused approval, API/E2E/unit proof, negative cases, audit trail. |
| Tutor payment SIMS write-back | Can change payment state across systems. | Explicit approval, sync evidence, rollback/repair thinking, and monitoring. |
| KVM8 PostgreSQL migrations | Production deploy script does not automatically apply all production migrations. | Staging migration proof, explicit production migration approval, production apply proof. |
| Public profile pages | Public unauthenticated surface can leak or break customer-facing tutor profile links. | Public/unauthenticated E2E or API evidence and invalid-token proof. |
| Knowledge Assistant / AI data tools | Can return operational data and consume API budget. | Tool permission review, data boundary evidence, cost/usage checks where relevant. |
| Production push/deploy/rollback | Affects internal staff operations. | Explicit approval, KVM8 deploy playbook, smoke, PM2/HTTP proof, monitoring. |

## Access And Boundaries

| Area | Rule |
| --- | --- |
| Safe read-only access | Repo docs/code, Git status/diff, safe local checks, approved read-only wrapper scripts, GitHub issue/PR reads, monitoring reads when relevant. |
| Forbidden paths | Do not read or modify repo `.env*` files, secrets, raw credentials, or anything under `live/`. |
| SIMS data | Read-only only; no INSERT/UPDATE/DELETE from Ripple. |
| Push/PR/merge/deploy | Requires explicit current-session approval and exact boundary. |
| Production DB/actions | No mutation without exact approval; production migration/deploy actions follow `docs/deployment/infrastructure.md`. |
| Staff/developer access | Ordinary staff stay in Teams Planner/support intake. Developer staff need a verified project profile, least-privilege access, and clear issue/branch/QA expectations before builder work. |

## Deploy And Release

| Field | Value |
| --- | --- |
| Staging target | `https://ripple-staging.tutorla.tech`; branch `staging`; KVM8 deploy path in `docs/deployment/infrastructure.md`. |
| Production target | `https://ripple.admin.sifututor.my`; branch `main`; KVM8 PM2 process `ripple-suite-prod`. |
| Legacy host | `https://ripple-suite.vercel.app` redirects to production and must not be used as proof that production is live. |
| Deploy path | Manual KVM8 deploy via `ssh staging` and `sudo -u deploy /usr/local/bin/deploy-ripple-suite prod` after approval. |
| Release proof | Source branch/SHA, KVM8 deploy output, PM2/HTTP proof, migration status when relevant. |
| Smoke proof | Authenticated browser/API smoke on the changed workflow plus public HTTP checks where relevant. |
| Monitoring proof | PM2/log/monitoring review where available and approved. |

## What Done Means

For normal `ripple-suite` code work, done usually means:

```text
The linked GitHub issue is clear, the change is implemented on the correct
branch, the matching TESTING.md row is identified and updated when needed,
focused unit/API/E2E checks pass, the real staff workflow is proved with
Playwright/browser/API evidence when feasible, critical-lane evidence is
complete when relevant, release notes are handled when staff behavior changes,
and the work is committed.
```

What is not done:

```text
Committed is not pushed.
Pushed is not PR-open.
PR-open is not merged.
Merged to main is not deployed to KVM8.
Deployed is not smoke-checked.
Smoke-checked is not accepted until Hafiz or the required QA/reviewer accepts
the remaining product/business risk.
```

For production release work, done means the approved KVM8 stop point is reached:
prepared only, deployed, smoke checked, monitored, or accepted/closed.

## Known Gaps

| Gap | Impact | Recommended next |
| --- | --- | --- |
| Agent OS install dry-run reported two optional baseline files that would be created. | Baseline is not fully applied in the product repo. | Decide whether to apply missing optional baseline files in a separate approved product-repo adoption task. |
| Full product test/build commands were not executed. | Profile is verified for orientation, but not a fresh readiness proof for staff/builder rollout. | Run selected product checks before declaring ready for internal agent or developer staff use. |
| Product profile is currently in umbrella docs, not product repo. | Agents editing only `ripple-suite` may not see this profile first. | Promote or link the profile from product `AGENTS.md`/`CLAUDE.md` after Hafiz approves product repo edits. |
| Local checkout was on a stale feature branch with gone upstream when checked. | Current local branch state should not be used as product readiness evidence. | Use clean `origin/main` worktrees for profile/readiness checks until the local branch is reset or intentionally resumed. |

## Verification Notes

Checked on 2026-06-30 against a temporary clean worktree from `origin/main` at
`af0222b`:

- `ripple-suite/AGENTS.md`
- `ripple-suite/CLAUDE.md`
- `ripple-suite/GOALS.md`
- `ripple-suite/TESTING.md`
- `ripple-suite/AI-RULES.md`
- `ripple-suite/docs/deployment/infrastructure.md`
- `ripple-suite/.claude/tasks/active.json`
- `ripple-suite/package.json`
- `scripts/agent-checks/agent-os-install.sh --target ripple-suite`
- `npm pkg get scripts`
- Test inventory under `tests/`, `qa/`, and `src/**/__tests__/`

Install dry-run result:

```text
AGENT OS INSTALL: PASS (2 warning(s), 0 file(s) created)
```

Still unknown:

- Whether all listed commands pass on the current branch when executed.
- Whether missing optional Agent OS baseline files should be applied to
  `ripple-suite` now or later.
- Whether the umbrella profile should be promoted or linked inside the product
  repo before developer-staff use.

Recommended next:

- Decide whether to promote/link this profile into the product repo, apply the
  optional local Agent OS baseline files, or continue drafting profiles for the
  next product repo first.
