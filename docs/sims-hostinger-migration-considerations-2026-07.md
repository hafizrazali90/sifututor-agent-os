# SIMS (sifu-tutor) to Hostinger Migration: Considerations and Plan

> **2026-08-10 staging-only update:** Web Voyager (`151.246.1.218`) became
> network-unreachable after that hosting plan was cancelled. Hafiz explicitly
> chose a fresh disposable staging database, so `sifu-staging.tutorla.tech` was
> rebuilt on the Hostinger KVM8 server (`187.127.98.182`; legacy SSH alias
> `finch`) and verified
> live with a real browser. `sifu-backport.tutorla.tech` was not rebuilt. This
> only supersedes this document's D5 staging assumption; the SIMS production
> migration described below remains unexecuted, and production remains on
> HostArmada `151.246.1.164`.

**Date:** 2026-07-18
**Scope:** Move `sifu-tutor` production (and staging) off HostArmada onto Hostinger.
**Status:** Research and considerations. No migration action taken. Every production-impacting step needs Hafiz go/no-go.
**Supersedes the current-state numbers in:** `docs/hosting-comparison-2026.md` (2026-06-01). That doc's app-layer analysis and phase structure still hold; the figures below are re-verified live on 2026-07-18.

> Decision model (unchanged): Hafiz decides stay/migrate/timing/budget/rollback. Claude/Codex diagnose, draft runbooks, execute approved steps, and verify.

### Decisions log
- **2026-07-18, D2 (server management): Laravel Forge** ("for now"). Manage the box with Forge (~$12/mo Hobby, one external server) instead of a cPanel license or fully hand-managed. Rationale: Forge provisions and manages exactly our stack (Nginx + PHP-FPM + MySQL + Redis + Supervisor queue workers + scheduler + Let's Encrypt + zero-downtime deploys), is cheaper than cPanel, and closes the outstanding Supervisor/Redis-queue gap by default. Implication: the new box is **plain Ubuntu 24.04** (Forge requires a fresh Ubuntu LTS); there is no cPanel/WHM and no WHM Transfer Tool, so migration is scripted rsync + mysqldump.

---

## 0. TL;DR recommendation

1. **Yes, migrate, but to a NEW dedicated Hostinger KVM 8 in the Kuala Lumpur datacenter**, not onto the existing shared KVM8 (72.62.251.97) that already runs ripple-suite, creative-hub, and kelasapp. SIMS is the highest-blast-radius production app (payments + tutor/parent mobile API); it should not share a box with three other prod apps.
2. **Run MySQL 8.4.x on the new box** (production is verified MySQL 8.4.10, not MariaDB). Match the engine exactly.
3. **Manage the box with Laravel Forge** (decided 2026-07-18), on plain Ubuntu 24.04. Forge provisions Nginx + PHP-FPM + MySQL + Redis + Supervisor workers + scheduler + Let's Encrypt + zero-downtime deploys, which also closes the outstanding queue/Supervisor gap. No cPanel, so migration is scripted rsync + mysqldump, not a WHM transfer.
4. **Keep uploads on the plan to move to Wasabi** (Mission `SIMS-BACKUP-DR-001.A1`). The 62 GB local upload tree is the dominant, fastest-growing footprint. Migrating it once is fine; the long-term fix is to stop growing VPS disk with user files.
5. **Do the still-outstanding app-layer fixes** (Redis queue + Supervisor, notifications indexes, Pulse retention) either before cutover or as part of the new-box build. Cache is already on Redis; queue and sessions are still on the database.
6. **Do not send transactional mail from the VPS.** Mail already uses Office365 SMTP; keep an external relay (Hostinger VPS caps outbound at 5 emails/min).
7. **Validate CPU steal on the assigned KL node under load** during Hostinger's money-back window before committing production.

Rough monthly cost: SIMS prod today is about **$148/mo** (HostArmada). The chosen path (KVM8 + Forge Hobby + daily backups) lands near **$68/mo** with better specs (8 vCPU / 32 GB / 400 GB vs 6 / 16 / 320) and KL latency. Forge Growth ($19/mo) covers prod + staging on one subscription.

---

## 1. Verified current state (ground truth, 2026-07-18)

### Production: HostArmada Site Carrier, `151.246.1.164`

| Item | Value |
|---|---|
| OS / panel | AlmaLinux 9.8, Apache 2.4.68, cPanel/WHM (KVM VPS with root, not shared hosting) |
| CPU / RAM / disk | 6 vCPU (EPYC 7413) / 16 GB / 320 GB NVMe |
| **Disk usage** | **265 GB used / 320 GB (83%), 55 GB free** (was ~50% in June; disk pressure is real) |
| Load average | ~1.0 on 6 vCPU (CPU is not the bottleneck) |
| PHP | 8.2.32 |
| **Database** | **MySQL 8.4.10 Community Server** (NOT MariaDB) |
| Redis | 6.2.22, local |
| App path | `/home/sifututortutorla/public_html` |
| App URL / hostnames | `sifu-tutor.tutorla.tech` (cPanel main domain), also reachable via Cloudflare-proxied `cloud.tutorla.tech`. Serves web SIMS + the tutor/parent mobile API. |

### App stack (from `composer.json` / live env)

- Laravel 11 (`^11.31`), PHP `^8.2`, Inertia + React front end (build needs Node + Vite + `tsc --noEmit`).
- Redis client is **predis** (pure PHP). **phpredis extension is NOT installed.** Installing phpredis on the new box is a cheap performance win.
- Laravel **Pulse** (self-monitoring, this is what fills `pulse_entries`).
- Spatie **Medialibrary** (owns the 62 GB of uploads under `storage/app/public`).
- Sanctum (mobile auth), Pusher (broadcast), Sentry + Logtail/BetterStack (errors/logs), QuickBooks SDK, Google API client, DomPDF, libphonenumber.
- PHP extensions in use: bcmath, curl, exif, fileinfo, gd, intl, mbstring, pdo_mysql, zip. (No imagick; DomPDF and gd cover PDF/image needs.)

### Current runtime config (the outstanding gaps)

| Setting | Value | Note |
|---|---|---|
| `CACHE_STORE` | `redis` | Done (June recommendation) |
| `QUEUE_CONNECTION` | `database` | **Still DB.** Queue runs via scheduler `queue:work --stop-when-empty` every minute (default + notifications queues) |
| `SESSION_DRIVER` | `database` | **Still DB** |
| Supervisor | not installed | **Still the cron workaround** |
| `FILESYSTEM_DISK` | `local` | 62 GB of uploads live on the server disk |
| Mail | Office365 SMTP (external) | Good: not tied to server IP reputation |
| Broadcast | Pusher (external) | |
| Queue backlog | **29,090 rows in `jobs`, 787 `failed_jobs`** | Large. Mostly future-dated reminders, but must be handled carefully at cutover |

### Data footprint to move (~84 GB in the home dir)

| Component | Size | Detail |
|---|---|---|
| Uploads `storage/app/public` | **62 GB** | Spatie media. `local` disk. Fastest grower (~55 GB three weeks ago). |
| MySQL on disk | **12 GB** | 3.1 GB logical across 129 tables / 7.6M rows; rest is binlogs/InnoDB overhead |
| App code + logs + rest | ~10 GB | |

Top tables (logical): `pulse_entries` 809 MB / 3.0M rows, `user_logs` 600 MB / 1.4M rows, `notifications` 382 MB / 892k rows, `notification_logs` 227 MB, `classes` 218 MB, `app_issue_reports` 215 MB, `media` 118 MB.

### Staging (re-verified, corrects stale docs)

- `sifu-staging.tutorla.tech` and `sifu-backport.tutorla.tech` run on **webvoyager = HostArmada `151.246.1.218`** (hostname `stg.cloud.tutorla.tech`, WHM :2087), cPanel users `sifustaging` / `sifubackport`.
- The old **`139.162.57.42` is dead** (not reachable). The old Koda note that staging runs on the Hostinger KVM8 (72.62.251.97) was stale and has been corrected.
- Note: the existing Hostinger KVM8 has a `/var/www/sifututor-migration` directory. Check what that is before reusing the box; it may be a prior migration attempt.

---

## 2. Sizing: current vs future needs

**CPU:** load ~1.0 on 6 vCPU. Not CPU-bound. Even KVM 4 (4 vCPU) covers current CPU. The reason to go bigger is headroom for Hostinger CPU-steal variance and for running the Vite build + Supervisor workers on-box.

**RAM:** 16 GB today, ~4 GB actually used + cache. 32 GB (KVM 8) is comfortable and lets MySQL buffer pool grow.

**Disk (the real driver):**
- Today 84 GB used, of which 62 GB is uploads growing ~1 to 2 GB/week.
- KVM 4 = 200 GB (fits today, ~1.5 to 2 years runway if uploads stay local).
- KVM 8 = 400 GB (multi-year runway).
- **The correct future-proofing is to offload uploads to Wasabi/S3** so VPS disk stops tracking user-file growth. If uploads move to object storage, even KVM 4's 200 GB is very comfortable and the DB is the only thing that grows on local disk.

**DB growth:** driven by `pulse_entries` (Pulse), `user_logs`, `notifications`. Add Pulse retention trimming and the still-missing notifications indexes; both shrink and speed up the DB regardless of host.

**Recommendation:** **KVM 8** for production (8 vCPU / 32 GB / 400 GB) for headroom and CPU-steal insurance. If uploads are moved to Wasabi first, **KVM 4** becomes a legitimate cheaper option.

---

## 3. Decisions to make first (these shape everything else)

| # | Decision | Options | Recommendation |
|---|---|---|---|
| D1 | Target box | New dedicated KVM8 vs co-locate on existing 72.62.251.97 | **New dedicated KVM8.** Isolate SIMS from ripple/creative/kelasapp blast radius. |
| D2 | Server management | cPanel (~$36/mo) vs **Laravel Forge** (~$12-19/mo) vs hand-managed | **DECIDED 2026-07-18: Laravel Forge.** Purpose-built for our stack, manages Supervisor/queue/Redis/SSL/deploys, cheaper than cPanel. Requires fresh Ubuntu 24.04. |
| D3 | DB engine | MySQL 8.4 vs MariaDB | **MySQL 8.4.x** to match production exactly (Phase-2 notification generated-column plan depends on MySQL JSON behavior). |
| D4 | Uploads | Migrate 62 GB as-is vs move to Wasabi first | Migrate as-is now to keep the move simple; schedule the Wasabi cutover right after (Mission `SIMS-BACKUP-DR-001.A1`). Decide if you want to do it before to shrink the transfer. |
| D5 | Staging | Keep on webvoyager, move to a small Hostinger box, or co-locate | Keep staging on webvoyager until prod cutover is proven, then move staging to a KVM 2/4 in KL and retire the webvoyager SIMS accounts. |
| D6 | App-layer fixes timing | Before cutover on HostArmada vs bake into new box | Bake Redis queue + Supervisor + indexes + phpredis into the new-box build; measure on the new box. |

---

## 4. Full considerations checklist

### A. Compute, OS, and stack parity
- [ ] Provision KVM 8, **select Kuala Lumpur** location in hPanel after purchase (region is chosen post-checkout, not at checkout).
- [ ] Match: PHP 8.2.x, MySQL 8.4.x, Redis, Apache (or Nginx if panel dictates), Certbot/AutoSSL, Supervisor, firewall, logrotate.
- [ ] Install the same PHP extensions plus **phpredis** (upgrade from predis).
- [ ] Install Node + build toolchain (or build assets in CI and ship the compiled `public/build`).
- [ ] Confirm timezone (Asia/KL) and locale parity.

### B. Data and files
- [ ] Inventory every path the app writes: `storage/app`, `storage/app/public`, the `public/storage` symlink, any out-of-tree upload dirs.
- [ ] Plan the 62 GB transfer (rsync in passes: bulk sync ahead of time, then a final delta at cutover). Verify counts and checksums.
- [ ] Re-create the `storage` symlink and fix ownership/permissions on the new box.
- [ ] Final MySQL dump at cutover (consistent, with routines/triggers/events); confirm SQL mode and charset/collation parity.
- [ ] Verify binlog settings and disk headroom for them.

### C. Networking, DNS, SSL
- [ ] Enumerate EVERY hostname that reaches production (at least `sifu-tutor.tutorla.tech` and `cloud.tutorla.tech`; check Cloudflare for any others, including mobile API and asset hosts).
- [ ] Lower Cloudflare TTLs 24h before cutover.
- [ ] Document current Cloudflare proxy mode per hostname (proxied vs DNS-only) and keep it identical after origin change (proxy mode changes can break Laravel session cookies).
- [ ] Provision valid SSL on the new origin before flipping DNS (AutoSSL via cPanel, or acme.sh/Certbot). Production currently renews via acme.sh.

### D. Mail
- [ ] Keep Office365 SMTP (external). Do not switch to VPS sendmail.
- [ ] Hostinger VPS caps outbound at 5 emails/min and does not document a raise path; a relay is mandatory for volume mail.
- [ ] Re-verify SPF / DKIM / DMARC still pass from the app's sending path; the sending identity is Office365, but confirm nothing sends via local PHP mail().

### E. Payments (FIUU/Molpay) [P0]
- [ ] Confirm whether FIUU allowlists callback source IPs. If yes, register the new server IP with FIUU before cutover.
- [ ] Confirm callback URLs are hostname-based (they are), so they follow DNS; test a real sandbox callback against the new origin before go-live.
- [ ] Do not cut over payments on a Friday or before a public holiday (existing rule).

### F. Queue, cron, scheduler
- [ ] Move queue to Redis + Supervisor persistent workers (default + notifications queues).
- [ ] **Never run queue workers/cron on both servers at once** (double-processing risk). Stop HostArmada workers before starting the new ones.
- [ ] Recreate the single app cron: `* * * * * php artisan schedule:run`. Confirm exactly one scheduler runs.
- [ ] Decide how to handle the 29,090 pending `jobs` and 787 `failed_jobs` at cutover (drain on old box first, or carry the table over and let the new workers process; avoid re-firing stale reminders). Coordinate with Mission `SIMS-NOTIF-MATCH-001.A2`.

### G. Redis, cache, sessions
- [ ] `CACHE_STORE=redis` already; keep it. Ensure Redis is provisioned, secured (bind localhost, requirepass), and sized.
- [ ] Move `QUEUE_CONNECTION` to redis.
- [ ] Consider `SESSION_DRIVER=redis` after cutover (note: switching sessions logs users out; schedule and communicate).

### H. Monitoring, backup, DR
- [ ] Stand up monitoring BEFORE cutover: disk, CPU, **CPU steal**, RAM, MySQL, Redis, queue depth/wait, SSL expiry, Laravel errors (Sentry/Logtail already wired).
- [ ] Wire the approved backup/DR design (Mission `SIMS-BACKUP-DR-001`): 6-hourly DB to Wasabi, daily incremental uploads, weekly config + monthly full; BetterStack heartbeats. Resolve the open DB-backup heartbeat 404 (`SIMS-BACKUP-DR-001.1`).
- [ ] Do NOT rely on cPanel local weekly backups filling the disk (that caused the 2026-07-12 outage). If cPanel backups are enabled on the new box, cap retention and push off-server.
- [ ] Hostinger weekly VPS backup is free; daily is a paid add-on (~$6/mo); manual snapshot keeps only one and self-deletes after a day. The VPS is locked during backup/restore, so treat restores as downtime.

### I. Security and patching (self-managed now)
- [ ] Firewall (only 80/443 + SSH from known IPs), fail2ban/cPHulk equivalent, SSH keys only.
- [ ] Adopt the monthly OS-patch + restore-drill runbook from `docs/hosting-comparison-2026.md`.
- [ ] Hostinger includes a free Malware Scanner and the Kodee AI assistant on VPS; useful but not a managed-sysadmin substitute.

### J. Mobile API specifics [P0]
- [ ] The tutor and parent apps hit this backend. A bad cutover is an app-wide outage (as the July disk incident showed).
- [ ] Smoke every critical mobile flow against the new origin (login/OTP, tutor requests, invoices/payments, notifications, class attendance) before flipping DNS.
- [ ] Keep the app-store-visible base URL stable (hostname unchanged); only the origin moves.

---

## 5. Outstanding app-layer fixes (do as part of the build)

From the June analysis, still not done and worth landing on the new box (measure before/after):
1. `notifications` composite indexes (table is 892k rows, still only PRIMARY KEY). Phase 1 indexes on `(user_id, type, deleted_at, id)` etc.
2. `QUEUE_CONNECTION=redis` + Supervisor workers (replace the every-minute `queue:work --stop-when-empty`). **Forge provisions Supervisor workers natively**, so this becomes config, not hand-rolled.
3. Install phpredis (replace predis).
4. Pulse data retention (trim `pulse_entries`; 809 MB and growing).
5. Optionally `SESSION_DRIVER=redis` after cutover.

---

## 6. Phased migration steps

Reuses the structure in `docs/hosting-comparison-2026.md`, tightened with current facts.

**Phase 0: Decide** (D1 to D6 above), confirm KL at checkout window, agree maintenance window (use real Malaysian low-traffic hours from access logs), agree rollback trigger, agree HostArmada stays paid and untouched 7 to 14 days post-cutover.

**Phase 1: Build new KVM8** in KL on plain **Ubuntu 24.04**, then connect it to **Laravel Forge** as an external server. Forge provisions Nginx + PHP 8.2 + MySQL + Redis + Supervisor + Certbot; add phpredis and the Node build toolchain. **Verify Forge's MySQL version and pin 8.4.x to match prod** (if Forge only offers 8.0, install 8.4 manually and point Forge at it). Configure the Forge site (web root at `public/`, queue workers for `default` + `notifications`, scheduler, deploy script, zero-downtime deploys), firewall, monitoring, SSL. Deploy code, build assets.

**Phase 2: Data + file rehearsal.** Bulk-rsync the 62 GB uploads ahead of time. Restore a recent DB dump. Fix symlink + permissions. Smoke via a temporary hostname or `/etc/hosts` override. Run mobile API checks, queue/email/push, scheduled commands. Benchmark under load and watch CPU steal.

**Phase 3: Cutover prep.** Lower Cloudflare TTLs. Confirm FIUU callbacks/allowlist, SPF/DKIM/DMARC, all hostnames + proxy modes. Freeze risky changes. Write exact rollback (DNS target + commands).

**Phase 4: Cutover.** Maintenance/read-only on old app. Stop old cron + workers. Final DB dump + final upload delta. Import on new box. Start cron + workers on new box only. Smoke. Flip Cloudflare origin/A records. Watch logs and real user flows.

**Phase 5: Post-cutover.** Keep HostArmada as rollback 7 to 14 days. Compare slow-query logs. Verify mobile on real devices, email deliverability, and payment callbacks. Only after the rollback window and a successful restore drill: retire HostArmada. Then move staging to KL and retire the webvoyager SIMS accounts.

---

## 7. Risks and mitigations

| Risk | Why it matters | Mitigation |
|---|---|---|
| **CPU steal / noisy neighbor** (Hostinger's #1 known VPS risk) | Latency-sensitive mobile API | Size to KVM8; benchmark the assigned KL node under load during the money-back window; monitor steal; request node move if bad |
| Queue double-processing | Duplicate emails/notifications/invoicing side effects | Stop old workers/cron before starting new; single scheduler |
| 62 GB upload sync gap | Missing user documents/images | Multi-pass rsync + final delta + checksum verify; keep old box as source during rollback window |
| Payment callback failure | Money flow | Confirm FIUU IP allowlist + callback URLs; sandbox test on new origin pre-cutover |
| Mail 5/min VPS cap | Silent mail loss if anything sends locally | Keep Office365 relay; audit that no code path uses local mail() |
| MySQL parity | Same app, different behavior under different engine/mode | MySQL 8.4.x; match SQL mode, charset, collation; test on prod copy |
| Session switch logs users out | Support noise | Keep sessions on DB through cutover; move to Redis later with comms |
| DNS/proxy-mode mistakes | SSL errors, session-cookie breakage | Document every hostname + proxy mode; keep proxy mode identical; valid SSL on new origin first |
| Self-managed patching neglect | Security drift (no more managed host) | Monthly AI-assisted maintenance + restore drills |
| cPanel local backups fill disk | Repeat of 2026-07-12 outage | Cap retention, push off-server, use the Wasabi DR design |

---

## 8. Cost comparison (recheck at Hostinger checkout; budget on renewal, not promo)

| Item | Now (HostArmada) | **Chosen: KVM8 + Forge** | (ref) cPanel | (ref) hand-managed |
|---|---:|---:|---:|---:|
| Prod compute | ~$148/mo (6/16/320) | $49.99/mo KVM8 (8/32/400) | $49.99/mo | $49.99/mo |
| Management | included | **$12/mo Forge Hobby** (or $19 Growth = prod+staging) | ~$36/mo cPanel | $0 |
| Daily backups | included | ~$6/mo add-on | ~$6/mo | ~$6/mo |
| **Prod subtotal** | **~$148/mo** | **~$68/mo** | ~$92/mo | ~$56/mo |
| Staging | webvoyager ~$71/mo (shared w/ LMS, nakngaji-dev) | KVM2/4 in KL, covered by Forge Growth | | |

RM reference (KL page): KVM8 RM 217.99/mo renewal, KVM4 RM 118.99/mo renewal. Hostinger does not sell managed S3, so **keep Wasabi** for uploads/backups. Migration is **self-service**; with Forge (no cPanel) the path is scripted **rsync + mysqldump** into the Forge-provisioned box, not a WHM transfer.

---

## 9. Open questions for Hafiz

1. New dedicated KVM8, or accept co-location on the existing KL box? (Recommend new/dedicated.)
2. ~~Control panel~~ RESOLVED 2026-07-18: **Laravel Forge** (see Decisions log).
3. Move uploads to Wasabi before or after the host move?
4. Staging: move to KL now, later, or keep on webvoyager?
5. What is the acceptable maintenance window (needs real low-traffic hour from access logs)?
6. Does FIUU allowlist callback IPs (blocking question for payments)?
7. Are the app-layer fixes (Redis queue, Supervisor, indexes, Pulse retention) in scope for this migration or a separate track?

---

## Sources

- Live SSH audit of production (`151.246.1.164`) and webvoyager (`151.246.1.218`), 2026-07-18.
- `composer.json` and runtime `.env` of `sifu-tutor`.
- `docs/hosting-comparison-2026.md` (2026-06-01) for app-layer diagnosis and phase structure.
- Hostinger official pages (VPS plans, Malaysia datacenter, cPanel license, backups, CPU steal, SMTP cap, hosting limits), rechecked July 2026. Full URL list retained in the research notes.
- Mission Ledger: `SIMS-BACKUP-DR-001`, `SIMS-BACKUP-DR-001.1`, `SIMS-BACKUP-DR-001.A1`, `SIMS-NOTIF-MATCH-001.A2`.
