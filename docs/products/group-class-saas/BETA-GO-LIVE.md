# Kelasapp — Private Beta Go-Live Plan

> How Kelasapp goes from a tested MVP on feature branches to a real, hosted **private beta** for
> Sopan (one white-glove centre, real Mudeer data). Decided with Hafiz 2026-07-05.
> This is NOT a public launch: no marketing, no open sign-up, so the pricing/Terms/legal gate
> (LAUNCH-READINESS E1-E3) does not apply yet.

## Decisions locked

| Decision | Choice | Why |
|---|---|---|
| **Phase label** | **Beta** (not Alpha) | Feature-complete, 548 E2E + 156 unit green, build passes, Sopan runs real data. Alpha implies half-built / data-loss risk and would undersell + unsettle a real customer. |
| **Scope** | Private beta on real infra | Matches the agreed sequencing (Sopan beta -> stabilize -> public). Sidesteps the marketing/legal gate. |
| **Hosting** | **KVM8 (`72.62.251.97` / srv1297548)** — co-locate with ripple-suite + creative-hub | It IS the Sifututor Next.js app server: 8 vCPU / 31 GB RAM (28 free) / 387 GB (17% used), Ubuntu 24.04. Already runs two sibling Next.js apps the exact way Kelasapp needs. Massive headroom; no new box to provision or harden. |
| **App runtime** | **PM2 + Node + nginx** (replicate the ripple-suite pattern) | The box's established convention (no Docker). Proven template: nginx vhost + PM2 prod/staging + deploy-webhook per app. Next.js stays portable regardless (future move = repo + env + pg_dump). |
| **Database** | **Postgres 16 on KVM8** — a new `kelasapp_prod` DB + scoped user | Postgres 16 already installed and hosting ripple/creative DBs. Kelasapp gets its OWN DB + user (never sharing another app's DB). Localhost, lowest latency. |
| **Node** | Install **Node 24** for Kelasapp's PM2 process | Kelasapp requires Node 24; box default is Node 22 (multiple Node versions already run here). |
| **Backups** | Automated `pg_dump` + WAL -> **Wasabi** (off-box), with a TESTED restore | The one real risk of self-hosted DB is data loss; off-box + automated + tested closes it. Wasabi is already in the stack. |
| **Environments** | **prod + staging pair** (matches ripple-suite/creative-hub) | Never test on Sopan's live box; rehearse the Mudeer migration on staging first; safe beta feedback loop. Staging is isolated (own DB + process + vhost) and does NOT send real email (test sender / file sink only, so a staging invite can't reach a real parent). |
| **Domain (now)** | prod **`kelasapp.learnestlab.com`** + staging `staging.kelasapp.learnestlab.com` | Apex of the kelasapp subdomain (landing + app are one deployment, so no "app." prefix). Same name is the verified email identity. DNS on Namecheap. |
| **Landing** | Full public landing stays up on the prod URL (no holding page) | Private beta is unmarketed, so the non-advertised subdomain has minimal exposure. NOTE: the landing still carries the parked E1-E3 pricing/"free trial" copy — fine for a private beta, but reframe before PUBLIC launch. |
| **Domain (future)** | A dedicated **kelasapp** apex domain (e.g. `kelasapp.my` / `.com` / `.app`) | Own the brand, not a subdomain under learnestlab.com. See "Domain future" for the migration-safe path. |

## What needs Hafiz vs what Claude can do

**Hafiz (accounts / access / decisions — Claude cannot do these):**
- Namecheap DNS (learnestlab.com zone), two A-records -> `72.62.251.97` (KVM8): host `kelasapp` (prod, `kelasapp.learnestlab.com`) and host `staging.kelasapp` (staging). Optional: `_dmarc.kelasapp` TXT for deliverability.
- Create a **Kelasapp Sentry project** -> DSN (prod refuses to boot without it).
- Confirm the Resend API key is **Sending-only** scope and belongs to the account owning the verified domain.
- Go-ahead + confirm the `deploy` user on KVM8 is the right home for Kelasapp (alongside ripple-suite/creative-hub).
- Register the future kelasapp apex domain when ready.

**Claude (has SSH to KVM8 via `staging` alias; staging-first, snapshot-before-destructive):**
- Everything app-layer: Node 24 for Kelasapp, the `kelasapp_prod` DB + scoped user, the migrations, the nginx vhost + certbot SSL, the PM2 prod+staging processes + deploy webhook (replicating ripple-suite), the Wasabi backup cron + a tested restore, prod env wiring, and the live smoke test.
- The Beta branding (DONE — commit 76583a5).

## Provisioned so far (safe groundwork done 2026-07-05)

Isolated, reversible prerequisites completed on KVM8 (nothing touching ripple/creative):

- **Postgres pair created + verified** on the local Postgres 16: databases `kelasapp_staging` + `kelasapp_prod`, each owned by a scoped login role `kelasapp_staging_user` / `kelasapp_prod_user` (matches the `ripple_suite_*` / `creative_hub_*` convention). Each role confirmed it can connect to its own DB. `public` schema owned by the app role so migrations can create tables (PG15+ locks `public` by default).
- **DATABASE_URL stored** in root-only env fragments `/etc/kelasapp-env/kelasapp-staging.env` + `kelasapp-prod.env` (perms 600, root:root — mirrors ripple's `/etc/staging-env` pattern). Passwords are auto-generated, never printed.
- **Node 24 installed isolated** for the `deploy` user via nvm: `/home/deploy/.nvm/versions/node/v24.18.0/bin/node` (aliased `kelasapp`). System Node stays v22.22.3 for ripple/creative. Kelasapp's PM2 process + webhook build will point at this path.

Discovered ground truth (the on-box `ecosystem.config.js` / `run-pg-migrations.sh` in the ripple repo are stale templates — ignore them):
- Real DB = **local Postgres 16** on KVM8 (not Neon). Convention: DB `<app>_<env>`, role `<app>_<env>_user`.
- PM2: `<app>-prod`, `<app>-staging`, `<app>-deploy-webhook`, all under `deploy`, fork mode.
- nginx vhosts: `/etc/nginx/sites-available/<app>-<env>`, HTTPS reverse-proxy to a localhost port, SSL managed by certbot.
- Migrations: `kelas/migrations/` applied by `drizzle-kit migrate` inside `npm run build` (`run-s db:migrate build:next`).
- Repo: `github.com/Learnest-Lab/kelasapp`, deploy branch `feat/finish-mvp-polish` (local is 2 commits ahead of origin — push before deploy).

## STAGING IS LIVE — https://staging.kelasapp.learnestlab.com (2026-07-05)

Full staging environment stood up and browser-verified:
- Code delivered via a git bundle (repo is in the `Learnest-Lab` org the box can't reach yet — deploy key generated, awaiting Hafiz to add it for the webhook). Cloned to `/opt/deploy/kelasapp/repo-staging`, origin + `core.sshCommand` wired to the `kelasapp_deploy` key for future GitHub pulls.
- `npm ci` (Node 24) + `npm run build` → **migrations applied** to `kelasapp_staging`, Next build clean.
- PM2 `kelasapp-staging` on `0.0.0.0:3310` (firewalled; only nginx reaches it), Node 24 interpreter, `pm2 save`d.
- nginx vhost `kelasapp-staging` + Let's Encrypt cert (expires 2026-10-02, auto-renew), 80→443 redirect.
- Env: `APP_ENV=staging` (so it boots without Sentry/Resend), email unset → mailer logs instead of sending (no real mail can leave staging).
- Verified: landing + `/sign-in` (with Beta badge) + `/terms` + `/privacy` all 200 over HTTPS; `/dashboard` correctly bounces to sign-in; console clean.

**Critical config learning (applies to PROD too):** start Next with `next start -p <port>` and **NO `-H` flag**. Passing `-H 127.0.0.1` pins Next's origin to localhost, so next-intl builds cross-origin absolute rewrites to `localhost:<port>` → 500 `EPROTO`/rewrite-loop behind the TLS proxy. Dropping `-H` makes the rewrite same-origin (`/en`) and everything works. Standard nginx headers (Host + X-Forwarded-For + X-Forwarded-Proto) are correct. See Koda mem_e9f2faf4c1f4.

## PRODUCTION IS LIVE — https://kelasapp.learnestlab.com (2026-07-05)

Booted first try (all staging fixes carried over):
- `repo-prod` cloned from `repo-staging`; prod `.env` = `APP_ENV=production` + generated `BETTER_AUTH_SECRET` + `DATABASE_URL`→`kelasapp_prod` + `NEXT_PUBLIC_SENTRY_DSN` (baked at build) + branded `EMAIL_FROM` (`Kelasapp <no-reply@kelasapp.learnestlab.com>`) + `RESEND_API_KEY`.
- **Sentry**: `kelasapp` project (org `sifu-edu-learning-sdn-bhd`); client events flow via the `/monitoring` tunnel route (confirmed working — a 429 there under burst testing is just ingest rate-limiting, not an error).
- **Resend**: live test send from the verified domain succeeded (id `33f00299…`) BEFORE wiring the key in; `assertProductionEnv` passes (Resend + EMAIL_FROM + Sentry all present).
- PM2 `kelasapp-prod` on `0.0.0.0:4310` (Node 24 interpreter, no `-H`, firewalled), `pm2 save`d.
- nginx vhost `kelasapp-prod` + Let's Encrypt cert (expires 2026-10-02, auto-renew), 80→443 redirect.
- Verified over HTTPS: landing + `/sign-in` (Beta badge) + `/sign-up` + `/terms` + `/privacy` all 200; `/dashboard` bounces to sign-in; console clean apart from the benign Sentry-tunnel 429.

Both environments now live: **prod** `kelasapp.learnestlab.com`, **staging** `staging.kelasapp.learnestlab.com`.

**Backups (DONE 2026-07-05):** nightly cron 02:30 → `pg_dump kelasapp_prod` → local (`/opt/deploy/kelasapp/backups`, keep 14) **+ off-box to Wasabi** (`sifututor-kelasapp-backups-prod`, ap-southeast-1). Restore **verified from both** the local dump and a fresh Wasabi download (27 tables). See Koda mem_ed51bac4d5f5.

Still open (not blocking a working beta): (1) **auto-deploy webhook** — receiver is built + running, but the `Learnest-Lab` org blocks deploy keys (enterprise policy) and the token route was declined for now, so deploys are **manual on request** (revisit with a GitHub App if the pace picks up); (2) rehearse Sopan's Mudeer import on staging, then real import on prod (waiting on his export).

## Go-live steps (ordered) — KVM8, ripple-suite pattern

**Phase 0 — go-ahead (Hafiz):** confirm KVM8 + the DNS A-record + a Kelasapp Sentry DSN.

**Phase 1 — box prep (Claude, no provisioning needed — box exists):** install/confirm Node 24 available for the `deploy` user; create the Kelasapp deploy path (mirror `/opt/deploy/creative-hub`); nginx vhost `kelasapp-prod` (+ `kelasapp-staging`).

**Phase 2 — database (Claude):** `createdb kelasapp_prod` + a scoped `kelasapp` user on the existing Postgres 16 (isolated from ripple/creative DBs); run the Drizzle migrations (`kelas/migrations/`); set up the Wasabi backup cron (nightly `pg_dump` + WAL off-box) and **verify a restore** to a scratch DB.

**Phase 3 — app deploy (Claude):** build (`npm run build`) + PM2 start (`kelasapp-prod`, mirror the ripple-suite ecosystem config); wire prod env (`DATABASE_URL` -> localhost `kelasapp_prod`, generated `BETTER_AUTH_SECRET`, `BETTER_AUTH_URL` + `NEXT_PUBLIC_APP_URL` -> `https://kelasapp.learnestlab.com`, branded `EMAIL_FROM` + `RESEND_API_KEY`, Kelasapp `NEXT_PUBLIC_SENTRY_DSN`, `WASABI_*`); certbot SSL for `kelasapp.learnestlab.com` (+ staging) via the existing nginx.

**Phase 4 — staging + deploy pipeline (Claude):** stand up the full **staging** mirror first — `kelasapp_staging` DB, `kelasapp-staging` PM2 process, `staging.kelasapp.learnestlab.com` vhost + SSL, tracking a `staging` branch, with email set to the test sender / file sink (NEVER real mail). Then the `kelasapp-deploy-webhook` (pull -> build -> migrate -> reload) mirroring `ripple-suite-deploy-webhook`. Prod deploys are promotions of what passed on staging.

Env order in practice: build + verify staging first, then prod. Every fix during the beta lands on staging, is checked, then promoted.

**Phase 5 — pre-flight (Claude + Hafiz):**
- **Beta branding** shipped (see below).
- Merge path: for beta, deploy from `feat/finish-mvp-polish`; merge the PR stack to `main` when convenient (PR #4 checks must pass first).
- **Rehearse the Mudeer migration on STAGING** first (real data, dry-run) via `/dashboard/import`; catch any mapping issues before prod.
- Live smoke test against the real prod URL (sign up -> centre -> the money flow -> a real branded email actually arrives to a non-owner inbox).
- Then **Sopan's Mudeer data migration on PROD**, having proven it on staging.

## Beta branding (requirement 1)

A subtle, honest "Beta" signal so users understand it is early software — not a scary banner.
- A small **"Beta" pill** next to the Kelasapp wordmark (sidebar header + auth screens).
- Driven by a single `AppConfig.phase` flag so it is one-line to change to a launch banner or remove at GA.
- Optional later: a one-line dismissible note on first login ("Kelasapp is in beta - your feedback shapes it; please report anything odd").
- Wording intent: "early, still improving, tell us what breaks" — NOT "we might lose your data."

## Domain future (requirement 2)

Now: `app.kelasapp.learnestlab.com`. Future: a dedicated kelasapp apex domain.

Migration-safe path (so the future switch is painless):
- The base URL is already **env-driven** (`NEXT_PUBLIC_APP_URL` / `getBaseUrl()`), so moving domains is a DNS change + env update + re-issued SSL, **no code change**.
- **Caveat — public invoice links embed the base URL.** Any invoice link a parent already received on the old domain would break after a domain move unless we keep a redirect. For Sopan's small private beta this is low-risk, but **lock the final apex domain before parents receive invoice links at scale** (i.e. before public launch), and add a 301 redirect from the old host when we migrate.
- Recommendation: register the kelasapp apex domain during beta so the public launch starts on the final domain and this migration never touches real parent traffic.
