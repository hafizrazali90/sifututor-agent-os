---
status: active
audience: OpenAI Codex (verification + decision discussion)
branch: chore/13-sims-ui-audit-workflow
goal: Migrate SIMS (sifu-tutor) production + staging off HostArmada onto Hostinger, planned but not executed.
next-action: Independently re-verify the current-state facts in Section 3 (read-only SSH audit), then walk decisions D1..D6 with Hafiz one at a time.
koda_status: flushed
created: 2026-07-18T19:44:25+0800
project: Sifututor / sifu-tutor
commit: 8c6039cf74c85c6b919e24ad983970926e59b26d
---

# Handoff to Codex: SIMS to Hostinger Migration (planning)

## 0. Your job, Codex

Hafiz wants you to **independently verify what Claude produced so far, then discuss each decision with him in detail** before anything is provisioned or moved. Nothing has been migrated. This is still a planning and verification phase.

Two rules for how to work here:
1. **Verify, do not trust.** Every "verified" fact below includes how it was checked. Re-run the read-only checks yourself and flag anything that does not match. Claude has been wrong before (see Section 4: the repo/memory said MariaDB and mislocated staging).
2. **Read-only until Hafiz approves.** Do not provision servers, buy plans, change DNS, touch payment callbacks, write to the SIMS production database, or cut over anything. Hafiz approves every production-impacting step. Never modify anything under `live/`.

The full detail lives in **`docs/sims-hostinger-migration-considerations-2026-07.md`** (the considerations + phased plan). This handoff is the orientation layer; that doc is the substance. Also read the prior analysis **`docs/hosting-comparison-2026.md`** (2026-06-01).

---

## 1. Primary request (what Hafiz asked)

> "I am planning to migrate SIMS project (prod+staging) to Hostinger. Please do deep research online, analyze current SIMS project and first list down all the things that we need to consider (server spec based on current and future needs, proper migration steps, and so on). Also access everything you need (database, current server, and so on) so that you get the correct and accurate context."

Then: fix every contradiction found; questioned whether cPanel is needed; decided **Laravel Forge "for now"** for server management; and asked for this handoff so you can verify and discuss each decision.

---

## 2. Why migrate (the motivation)

- **Disk pressure:** production is at **83%** (55 GB free) and the upload tree grows ~1 to 2 GB/week. The 2026-07-12 outage was a cPanel local backup filling the disk (Koda `mem_a62330809b28`).
- **Cost:** HostArmada Site Carrier is ~**$148/mo**; a Hostinger KVM8 is ~**$50/mo** with better specs.
- **Latency:** Hostinger has a **Kuala Lumpur** datacenter (confirmed, opened ~Aug 2025). Current box is US-region.
- **Specs:** KVM8 = 8 vCPU / 32 GB / 400 GB vs current 6 / 16 / 320.

This is not a raw-performance fix (load is ~1.0; CPU is not the bottleneck). The real drivers are disk, cost, latency, and finishing the app-layer fixes.

---

## 3. Verified current state (and HOW it was verified, so you can re-check)

All checked live on **2026-07-18** via `ssh production` and `ssh webvoyager` (read-only), plus reading `sifu-tutor/composer.json` and the runtime `.env` (secrets never printed). Re-verify the volatile numbers (disk %, job counts) as they drift.

### Production: HostArmada Site Carrier `151.246.1.164`
| Fact | Value | How to re-verify |
|---|---|---|
| OS / panel | AlmaLinux 9.8, Apache 2.4.68, cPanel/WHM (KVM VPS, root) | `ssh production 'cat /etc/redhat-release; httpd -v'` |
| CPU / RAM / disk | 6 vCPU (EPYC 7413) / 16 GB / 320 GB NVMe, **83% used** | `ssh production 'nproc; free -h; df -h /'` |
| PHP | 8.2.32 | `ssh production 'php -v'` |
| **DB engine** | **MySQL 8.4.10 Community** (NOT MariaDB) | `ssh production 'mysql --version'` |
| Redis | 6.2.22, local | `ssh production 'redis-cli ping; redis-cli info server'` |
| App path | `/home/sifututortutorla/public_html` | `ssh production 'ls -d /home/sifututortutorla/public_html'` |
| DB name | `sifututortutorla_LiveDB` | from `.env` `DB_DATABASE` |
| DB size | 3.1 GB logical / 12 GB on disk / 129 tables / 7.6M rows | `information_schema.tables` sum; `du -sh /var/lib/mysql` |
| Uploads | **62 GB** in `storage/app/public`, `FILESYSTEM_DISK=local` (Spatie Medialibrary) | `ssh production 'du -sh /home/sifututortutorla/public_html/storage/app'` |
| Biggest tables | pulse_entries 809MB, user_logs 600MB, notifications 382MB (892k rows, only PRIMARY KEY) | `information_schema.tables ORDER BY size` |
| App URL | `sifu-tutor.tutorla.tech` (also `cloud.tutorla.tech` via Cloudflare) | `.env` `APP_URL`; `dig` |
| Mail | Office365 SMTP (external) | `.env` `MAIL_*` |
| Broadcast | Pusher (external) | `.env` `BROADCAST_DRIVER` |

### App-layer gaps still open (the June plan is only half done)
| Setting | State | Note |
|---|---|---|
| `CACHE_STORE` | `redis` (via **predis**, pure PHP) | Done. phpredis extension NOT installed. |
| `QUEUE_CONNECTION` | **`database`** | Not moved to Redis. Runs via scheduler `queue:work --stop-when-empty` every minute (`routes/console.php:79-80`). |
| `SESSION_DRIVER` | **`database`** | Not moved to Redis. |
| Supervisor | **not installed** | Still the cron workaround. |
| Queue backlog | **29,090 `jobs` + 787 `failed_jobs`** | Mostly future-dated reminders; handle carefully at cutover. |

### App stack (from `sifu-tutor/composer.json`)
Laravel 11 (`^11.31`), PHP `^8.2`, Inertia + React (build needs Node + Vite + `tsc --noEmit`), Laravel **Pulse** (the `pulse_entries` bloat), Spatie **Medialibrary** (the 62 GB), Sanctum, Pusher, Sentry, Logtail/BetterStack, QuickBooks SDK, Google API client, DomPDF, libphonenumber. Extensions in use: bcmath, curl, exif, fileinfo, gd, intl, mbstring, pdo_mysql, zip (no imagick).

### Staging: webvoyager `151.246.1.218` (HostArmada, hostname `stg.cloud.tutorla.tech`)
- `sifu-staging.tutorla.tech` + `sifu-backport.tutorla.tech`, cPanel users `sifustaging` / `sifubackport`.
- Verify: `dig +short sifu-staging.tutorla.tech` (returns 151.246.1.218) and `ssh webvoyager 'ls -d /home/sifustaging /home/sifubackport'`.

---

## 4. Contradictions we found and FIXED (verify we fixed them correctly)

The repo and Koda contained wrong facts. Ground truth was established live, then corrected at source. **Spot-check these:**

| Was (wrong) | Now (verified) | Fixed in |
|---|---|---|
| "Laravel 11 + **MariaDB**" | **MySQL 8.4.10** | parent `CLAUDE.md` (gitignored, on disk), `docs/onboarding/claude-code-setup.md` |
| webvoyager = **139.162.57.42** (dead; `nc -z` fails) | **151.246.1.218** | global `~/.claude/CLAUDE.md`, `docs/agent-playbooks/agent-access-map.md`, `docs/onboarding/claude-code-setup.md`, `sifu-tutor/docs/deployment/incident-runbook.md`, `scripts/agent-access/check-cpanel-autossl.sh` |
| production = "**cPanel shared hosting**" | **cPanel/WHM KVM VPS** (root) | global `~/.claude/CLAUDE.md` |
| Koda: staging on Hostinger KVM8 `72.62.251.97` | webvoyager `151.246.1.218` | Koda `mem_0134`, `mem_0413` updated |

**Trap to remember:** the SSH alias literally named `staging` points to the **Hostinger KVM8 `72.62.251.97`**, which hosts ripple-suite / creative-hub / kelasapp, **NOT** sifu-tutor staging. Do not conflate "the staging alias" with "SIMS staging" (which is on webvoyager). That KVM8 also has a `/var/www/sifututor-migration` directory of unknown origin, worth inspecting before any reuse.

---

## 5. Decisions: made vs open (discuss each with Hafiz)

### Made
- **D2 (server management): Laravel Forge "for now."** Not cPanel (~$36/mo, features we mostly do not use since mail=Office365, DNS=Cloudflare, SSL=acme.sh, backups=Wasabi), not fully hand-managed (too much ops burden for the payments/mobile-API backend). Forge (~$12/mo Hobby, ~$19 Growth for prod+staging) provisions and manages Nginx + PHP-FPM + MySQL + Redis + **Supervisor queue workers** + scheduler + Let's Encrypt + zero-downtime deploys, which also closes the open queue/Supervisor gap. Requires plain **Ubuntu 24.04**. Koda `mem_2ecb069323b9`.
  - **Open sub-item for you to verify:** can Forge provision/pin **MySQL 8.4.x** to match prod (8.4.10)? If it only offers 8.0, decide: accept 8.0 (test a 8.4→8.0 dump/restore) or install 8.4 manually and point Forge at it.

### Open (recommendations in the considerations doc, not yet decided)
- **D1 Target box:** new dedicated KVM8 (recommended) vs co-locate on the existing shared KVM8. Blast-radius argument: SIMS is payments + mobile API; do not share with 3 other prod apps.
- **D3 DB engine:** MySQL 8.4.x (recommended, match prod exactly).
- **D4 Uploads:** migrate the 62 GB as-is now vs move to Wasabi first (Mission `SIMS-BACKUP-DR-001.A1`). Object storage is the real future-proofing.
- **D5 Staging:** keep on webvoyager until prod cutover proven, then move to a KVM2/4 in KL.
- **D6 App-layer fixes timing:** bake Redis queue + Supervisor + notifications indexes + phpredis + Pulse retention into the new box.

### Other open questions needing Hafiz input
1. Acceptable maintenance window (needs a real low-traffic hour from access logs).
2. **Does FIUU allowlist callback source IPs?** Blocking question for payments; the new server IP must be registered if so.
3. Move uploads to Wasabi before or after the host move.

---

## 6. Guardrails (non-negotiable)

- **Read-only** until Hafiz approves each step. No provisioning, buying, DNS changes, payment-callback changes, or cutover.
- **Never write to the SIMS production database.** Every SIMS query includes `deleted_at IS NULL`.
- **Never send mail from the VPS** (Hostinger caps outbound at 5 emails/min). Keep the Office365 relay.
- **Never touch `live/`.** Reference only.
- **Decision model:** Hafiz decides stay/migrate/timing/budget/rollback and go/no-go. You diagnose, draft runbooks, execute only approved steps, and verify.
- **No Friday / pre-holiday** financial or cutover deploys.
- Codex access lanes: see `docs/agent-playbooks/agent-access-map.md` (production and staging SSH read lanes, cPanel admin lane).

## 7. Do Not Repeat / known traps

- Do not trust any doc or memory that says **MariaDB** or that **SIMS staging is on `72.62.251.97`**. Both were wrong and are fixed; if you see them again, they are stale.
- Do not assume the **June app-layer fixes are done** — only cache moved to Redis. Queue + sessions are still on the database; Supervisor is not installed.
- Do not run **queue workers or cron on both old and new servers at once** (double-processing: duplicate emails/notifications/invoicing).
- Do not size for CPU (it is idle). The constraints are **disk capacity** and **CPU-steal variance** on Hostinger nodes.
- Hostinger specifics to keep in mind: KL region is selected **post-checkout** in hPanel (not at checkout); VPS is **locked during backup/restore**; **no managed S3** (keep Wasabi); free weekly backup, daily is a ~$6/mo add-on.

## 8. Artifacts and pointers

| Path | What |
|---|---|
| `docs/sims-hostinger-migration-considerations-2026-07.md` | **Primary.** Full considerations, sizing, checklist, phased steps, risks, cost, decisions log. (gitignored, on disk) |
| `docs/hosting-comparison-2026.md` | Prior 2026-06-01 analysis: app-layer diagnosis + phase structure + provider comparison. |
| `docs/agent-playbooks/agent-access-map.md` | Access lanes for production/staging (updated IPs). |
| `docs/agent-playbooks/mission-ledger/sifu-tutor.md` | Related missions: `SIMS-BACKUP-DR-001` (backup/DR), `SIMS-BACKUP-DR-001.A1` (move uploads to Wasabi), `SIMS-NOTIF-MATCH-001.A2` (queue/failed jobs). |
| Koda memories | `mem_2ecb069323b9` (Forge decision), `mem_a9892ee8f4b7` (verified prod snapshot), `mem_0134`/`mem_0413` (corrected staging location), `mem_a62330809b28` (2026-07-12 disk outage). |

Note: `docs/*` and `CLAUDE.md` are gitignored in the parent repo, so the two migration docs and the parent CLAUDE.md edit are **on disk only, not committed**. Tracked edits this session: `docs/agent-playbooks/agent-access-map.md`, `docs/onboarding/claude-code-setup.md`, `scripts/agent-access/check-cpanel-autossl.sh`, and `sifu-tutor/docs/deployment/incident-runbook.md` (in the sifu-tutor subrepo).

---

## 9. Kick-off prompt for Codex (paste this to start)

---
You are helping verify and pressure-test a migration plan: **SIMS (sifu-tutor) from HostArmada to Hostinger**. Nothing is migrated yet. Work **read-only**; Hafiz approves every production-impacting step; never write to the SIMS production DB; never touch `live/`.

1. Read `docs/sims-hostinger-migration-codex-handoff.md`, then `docs/sims-hostinger-migration-considerations-2026-07.md`, then `docs/hosting-comparison-2026.md`.
2. **Independently re-verify** the current-state facts in Section 3 of the handoff using the read-only SSH checks listed there (`ssh production`, `ssh webvoyager`). Report any fact that does not match.
3. Then discuss decisions **D1 through D6** with me one at a time: state the trade-off in plain language, how reputable teams handle it, your recommendation, and your justification. Start with **D1 (dedicated vs co-located box)** and the open sub-item on **D2 (can Forge pin MySQL 8.4?)**.
4. Do not provision, buy, change DNS, or cut over anything.

Context: current prod is a HostArmada cPanel/WHM KVM VPS (MySQL 8.4.10, PHP 8.2, 62 GB local uploads, 83% disk). We decided on Laravel Forge for server management "for now." Open blocking question: does FIUU allowlist callback IPs?
---
