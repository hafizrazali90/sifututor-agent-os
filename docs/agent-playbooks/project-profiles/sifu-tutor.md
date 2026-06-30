# Agent OS Project Profile: sifu-tutor

Use this profile before starting `sifu-tutor` work from the Sifututor umbrella
workspace.

Plain meaning:

```text
This tells the shared Agent OS how SIMS actually works.
It is a draft profile until the remaining gaps are verified from the current
repo state and safe command output.
```

## Profile Status

| Field | Value |
| --- | --- |
| Project | `sifu-tutor` |
| Adoption state | `profile drafted` |
| Last verified | `not yet; drafted 2026-06-30` |
| Verified by | `not verified; drafted by Codex` |
| Main owner | `Hafiz / Sifututor Engineering` |
| Profile location | Umbrella profile: `docs/agent-playbooks/project-profiles/sifu-tutor.md`; product rules: `sifu-tutor/AGENTS.md`, `sifu-tutor/CLAUDE.md` |

This is not yet `profile verified` because product commands were identified
from docs/manifests but not executed in this pass, the local `sifu-tutor`
worktree had existing uncommitted changes, and the Agent OS install dry-run
reported optional local baseline files that would be created in apply mode.

## Plain Summary

`sifu-tutor` is the Laravel SIMS admin portal used by internal staff to manage
tutors, parents, students, tutor requests, classes, invoices, payments,
commissions, reports, notifications, CMS content, analytics, staff roles, and
tickets. It also owns API contracts consumed by the tutor and parent mobile
apps, so UI, backend, and mobile compatibility evidence often need to be checked
together.

## Repo Facts

| Field | Value |
| --- | --- |
| Purpose | SIMS admin and operations system for Sifututor. |
| Primary users | Internal staff/admins; mobile API consumers include tutors and parents. |
| Stack/runtime | Laravel 11, PHP 8.2+, Inertia.js, React/TypeScript, MySQL, Tailwind CSS, Playwright, Pest/Vitest. |
| Main source docs | `sifu-tutor/AGENTS.md`, `sifu-tutor/CLAUDE.md`, `.ai/README.md`, `.ai/modules/README.md`, `.ai/workflows/README.md`, `docs/ui-ux/README.md`, `docs/qa/`, `docs/deployment/`. |
| Active task state | `.claude/tasks/active.json` exists; active task was `null` when checked. |
| Important modules | Financial, operational, secondary modules from `CLAUDE.md` and `.ai/modules/README.md`. |
| Known local conventions | GitHub issue required before coding; branch should include issue number; SIMS UI/UX docs required for browser UI work; permanent Playwright E2E expected for automatable user-facing workflows. |

## Commands

Commands below are identified from `composer.json`, `package.json`, `AGENTS.md`,
`CLAUDE.md`, and deployment/QA docs. Marked `yes` means the command is present
in the repo docs or manifests, not that it was executed in this profile pass.

| Purpose | Command | Verified? | Notes |
| --- | --- | --- | --- |
| Install PHP deps | `composer install` | yes | Required before PHP/Laravel work. Production uses optimized install during deploy. |
| Install JS deps | `npm install` or `npm ci` | yes | Deployment docs use npm install/ci depending on server path. |
| Local dev stack | `composer dev` | yes | Runs Laravel server, queue listener, pail logs, and Vite via concurrently. |
| Frontend dev server | `npm run dev` | yes | Vite dev server. |
| Typecheck | `npm run typecheck` | yes | Runs `tsc --noEmit`. |
| Frontend build | `npm run build` | yes | Runs `tsc --noEmit && vite build`. |
| Backend tests | `composer test` | yes | Runs `php artisan test --parallel --processes=4 --no-coverage`. |
| Single-process backend tests | `composer test:single` | yes | Runs `php artisan test --no-coverage`. |
| Frontend unit tests | `npm run test:run` | yes | Runs `vitest run`. |
| Playwright E2E | `npm run test:e2e` | yes | Runs Chromium Playwright project. |
| Local E2E | `npm run test:e2e:local` | yes | Same Chromium Playwright path for local target. |
| External E2E | `npm run test:e2e:external` | yes | Sets `E2E_START_SERVER=false`. |
| Staging E2E | `npm run test:e2e:staging` | yes | Uses `playwright.staging.config.ts`. |
| Read-only staging smoke | `npm run test:e2e:staging:smoke:readonly` | yes | Uses `E2E_SKIP_SEED=true` for selected smoke/API specs. |
| Format/lint | `./vendor/bin/pint --test` | yes | Named in staging deploy preflight docs. |
| Permission contract test | `php artisan test tests/Feature/Audit/PermissionCompletenessTest.php` | yes | Required before commit/deploy when permissions change. |

## Evidence Expectations

| Work type | Expected proof |
| --- | --- |
| Docs-only | Readback/diff checks plus Agent OS checks when the docs affect workflow. |
| Backend/API | Focused Pest/feature/API tests, contract shape evidence, permission/error-path checks when relevant. |
| Browser UI | SIMS UI/UX docs read, focused tests where useful, Playwright/browser journey or screenshot evidence, and permanent E2E decision. |
| Mobile API contract | SIMS API proof plus `sifututor_tutor` and `sifututor_parent` compatibility review when contracts change. |
| Financial/payment/invoice/commission | Read-only diagnosis first, focused implementation approval, negative/idempotency evidence, FIUU/payment evidence where relevant, and QA/release proof. |
| Permission/RBAC | Route/controller checks, seeder/catalog consistency, focused permission tests, and `PermissionCompletenessTest`. |
| Migration | New migration only; never edit deployed migrations; migration safety proof before deploy. |
| Release/deploy | Release evidence pack, staging proof, backup/rollback readiness, production preflight, smoke, and monitoring. |

## Critical Lanes

These areas need read-only diagnosis first and explicit Hafiz approval before
implementation when the task changes behavior or risk.

| Lane | Why it is sensitive | Required approval/evidence |
| --- | --- | --- |
| Auth/RBAC/permissions | Can expose staff, financial, parent, tutor, or admin data. | Approval for implementation, permission contract checks, focused tests. |
| Payments/FIUU/bank flows | Can affect real payment state and callbacks. | Read-only diagnosis, approved scope, FIUU/payment evidence, negative cases. |
| Invoices/commitment fees/refunds/payment transfers | LHDN/accounting impact and customer-facing money records. | Financial review, focused tests, audit trail, staging/prod evidence as applicable. |
| Tutor payments/commissions/staff payroll/bonuses | Payout and payroll correctness. | Calculation proof, regression tests, review before release. |
| Migrations/destructive DB commands | Can damage live/staging data or break deploys. | New migration only, dry-run/clone proof when critical, explicit approval. |
| Mobile API contracts | Tutor/parent apps depend on response shape and behavior. | Cross-app contract review and compatibility evidence. |
| Production push/deploy/rollback | Affects live users and business operations. | Production deployment playbook, explicit approval, smoke, monitoring, rollback plan. |
| Queue/idempotency/scheduled jobs | Can duplicate notifications, payments, or state transitions. | Idempotency/retry evidence and post-change monitoring when relevant. |

## Access And Boundaries

| Area | Rule |
| --- | --- |
| Safe read-only access | Repo docs/code, Git status/diff, safe local checks, approved read-only wrapper scripts, Planner intake context when staff-reported, monitoring reads when relevant. |
| Forbidden paths | Do not read or modify repo `.env*` files, secrets, raw credentials, or anything under `live/`. |
| Push/PR/merge/deploy | Requires explicit current-session approval and exact boundary. |
| Production data/actions | No mutation without exact approval; read-only evidence only through approved scoped lanes. |
| Staff/developer access | Ordinary staff stay in Teams Planner. Developer staff need a verified project profile and least-privilege Agent OS permission profile before builder work. |

## Deploy And Release

| Field | Value |
| --- | --- |
| Staging target | `https://sifu-staging.tutorla.tech`; branch `sifu-staging`; deploy docs in `docs/deployment/staging-deploy-runbook.md`. |
| Production target | `https://sifu-tutor.tutorla.tech`; branch `main`; production playbook in `docs/deployment/production-deployment-playbook.md`. |
| Production candidate | `sifu-staging` is the production candidate according to current deployment memory and production playbook. |
| Deploy path | Git pull on server plus Composer/npm/build/migration/cache/queue steps as approved in deploy docs. |
| Release proof | Source branch/SHA, deploy SHA/version, release evidence pack, migration/permission evidence when relevant. |
| Smoke proof | Target-environment HTTP/browser/API smoke, changed workflow proof, mobile API/app smoke when relevant. |
| Monitoring proof | Sentry/BetterStack/Pulse/log evidence where available and approved. |

## What Done Means

For normal `sifu-tutor` code work, done usually means:

```text
The linked GitHub issue is clear, the change is implemented on the correct
branch, focused backend/frontend tests pass, the real user journey is proved
with Playwright/browser/API evidence when feasible, permanent E2E coverage or a
named exception is recorded for user-facing workflows, critical-lane evidence is
complete when relevant, and the work is committed.
```

What is not done:

```text
Committed is not pushed.
Pushed is not PR-open.
PR-open is not merged.
Merged is not deployed.
Deployed is not live-smoked.
Live-smoked is not accepted until Hafiz or the required QA/reviewer accepts the
remaining product/business risk.
```

For production release work, done means the production playbook reaches the
approved stop point: prepared only, deployed, smoke checked, monitored, or
accepted/closed.

## Known Gaps

| Gap | Impact | Recommended next |
| --- | --- | --- |
| Product worktree had existing dirty files during this profile pass. | The profile should not be treated as final proof of the current product repo state. | Re-run profile verification from a clean/current `sifu-tutor` branch before staff/builder rollout. |
| Agent OS install dry-run reported optional baseline files that would be created. | Baseline is not fully applied in the product repo. | Decide whether to apply missing baseline files in a separate approved product-repo adoption task. |
| No `TESTING.md` found at repo root. | Agent OS test coverage manifest workflow cannot use a root manifest yet. | Decide whether SIMS should add a root `TESTING.md` or rely on existing `docs/qa/` and E2E docs. |
| Commands were identified from docs/manifests, not executed. | Profile is drafted, not fully verified. | Run safe command verification from an appropriate branch/worktree. |
| Product profile is currently in umbrella docs, not product repo. | Agents editing only `sifu-tutor` may not see this profile first. | Promote or link the profile from product `AGENTS.md`/`CLAUDE.md` after Hafiz approves product repo edits. |

## Verification Notes

Checked on 2026-06-30:

- `sifu-tutor/AGENTS.md`
- `sifu-tutor/CLAUDE.md`
- `sifu-tutor/.claude/tasks/active.json`
- `sifu-tutor/.ai/README.md`
- `sifu-tutor/.ai/modules/README.md`
- `sifu-tutor/.ai/workflows/README.md`
- `sifu-tutor/package.json`
- `sifu-tutor/composer.json`
- `sifu-tutor/docs/deployment/production-deployment-playbook.md`
- `sifu-tutor/docs/deployment/staging-deploy-runbook.md`
- `sifu-tutor/docs/qa/qa-framework.md`
- `sifu-tutor/docs/qa/manual-qa-standard.md`
- `scripts/agent-checks/agent-os-install.sh --target sifu-tutor`

Install dry-run result:

```text
AGENT OS INSTALL: PASS (4 warning(s), 0 file(s) created)
```

Still unknown:

- Whether all listed commands pass on the current branch.
- Whether missing optional Agent OS baseline files should be applied to
  `sifu-tutor` now or later.
- Whether a root `TESTING.md` should be introduced or existing QA docs should
  remain the test coverage source.

Recommended next:

- Decide whether to verify this profile from a clean/current `sifu-tutor`
  branch and promote/link it into the product repo, or continue drafting
  profiles for the next product repo first.
