# 2026-08-26 cross-module session release ledger

## Ripple governed role access

- Issue: `#643`
- Branch: `feat/643-governed-official-role-access`
- Worktree: `/Users/hafizrazali/Projects/Sifututor-worktrees/ripple-643-governed-permissions`
- Commit / PR: Ripple PRs `#644`, `#649`, `#650`, and `#651`
- Tests: 44 focused files, 870 tests passed; Biome and clean-cache TypeScript passed
- E2E: `tests/e2e/roles/role-management.spec.ts`, 4/4 passed
- Main status: merged; production release SHA `41270715c896`
- Live status: deployed and production smoke passed
- Next action: none for this release

## SIMS governed role and staff access

- Issue: `#2296`
- Branch: `feature/2296-governed-permission-access`
- Worktree: `/Users/hafizrazali/Projects/Sifututor-worktrees/sifu-2296-governed-permissions`
- Commit / PR: SIMS schema PR `#2299` and application PR `#2297`
- Tests: 43 focused Laravel tests passed; Pint, TypeScript, and Vite build passed
- E2E: `tests/e2e/settings/governed-permissions.spec.ts`, 3/3 setup/journeys passed with desktop and 390px screenshots
- Main status: merged; production application SHA `4256093b0`
- Live status: deployed and production smoke passed
- Next action: none for this release

## Ripple Revenue Ledger activation and production backfill

- Issue: `#652`
- Branch: `fix/652-revenue-ledger-activation`
- Worktree: `/Users/hafizrazali/Projects/Sifututor-worktrees/ripple-revenue-activation`
- Commit / PR: `68e66f66`; Ripple PR `#653`, merged as `c5c35fe7`
- Tests: 34 Revenue files / 147 tests, all seven disposable PostgreSQL proofs, TypeScript, changed-file ESLint/Biome, migration source proofs, shell syntax, coverage-manifest check, and the 333-route production build passed. Repository-wide lint retains unrelated baseline failures; changed files are clean.
- E2E: `tests/e2e/revenue/invoice-ledger.spec.ts` includes `REV-E2E-019`; the complete clean-session Revenue suite passed 19/19. Authenticated production Playwright verified the populated ledger and a real cross-month invoice detail without an accounting mutation.
- Main status: merged to `main` and deployed at exact production SHA `c5c35fe7997b045d792fafa34b05cf4532849272`
- Live status: protected migrations `131/132/136` applied; internal read-only projection is active; backfill completed `85,969/85,969`, with `55,388` eligible, `0` source-missing, and no run error. Manual incremental completed `559/559` and the first installed cron-triggered incremental completed `555/555` as safe no-ops. QB, MyInvois, Core Analytics, and Full Analytics remain disabled. Production health and observability checks are clean.
- Next action: none for this release
