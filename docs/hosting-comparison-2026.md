# Sifututor Production Hosting & Performance Analysis

**Scope:** `sifu-tutor` Laravel 11 backend, MySQL 8.4, Redis, React Native mobile API, Malaysian user base  
**Updated:** 2026-06-01  
**Purpose:** Decide whether to stay on HostArmada or migrate, without confusing application bottlenecks with infrastructure bottlenecks.

---

## Executive Summary

The current production performance problem is mainly application and database configuration, not raw server size. The clearest bottleneck is the `notifications` table: 768,876 rows with only the primary key indexed, while production queries filter by `user_id`, `type`, `sender`, `status`, soft deletes, and JSON fields. Redis is installed but unused for cache and queues, so MySQL is also doing avoidable cache, queue, and session work.

Hosting should be evaluated separately from those fixes. Hostinger KVM8 is the strongest cost/latency/spec option if Sifututor is comfortable operating a self-managed VPS with Codex/Claude acting as technical operator and Hafiz making the go/no-go decisions. HostArmada is more expensive, but it includes cPanel/WHM, managed security conveniences, and support that reduce operational burden. My recommendation is: fix database/Redis/queues first on the current server, then migrate only after a rehearsed staging run proves the bare-VPS operating model is reliable.

This 2026-06-01 revision fixes the earlier analysis risks:

- Do not frame HostArmada as generic shared hosting; production behaves like a KVM VPS with root access and cPanel/WHM.
- Do not use stale or region-mismatched public pricing as final authority; provider pricing must be rechecked at checkout.
- Do not treat Hostinger KVM8 as the immediate fix for slow queries; it is a migration target after app-layer fixes and rehearsal.
- Do not present generated-column JSON indexing as a quick migration; it is a second-phase table-definition change that needs production-copy testing.
- Do not let AI-assisted operations imply autonomous production control; Hafiz still approves production-impacting gates.

---

## Decision Model: Hafiz Decides, LLM Operates

This comparison should not assume a traditional solo CTO who personally performs every sysadmin step. Sifututor's real operating model is:

| Responsibility | Owner |
|---|---|
| Business decision: stay, migrate, timing, budget, acceptable risk | Hafiz |
| Technical diagnosis, option comparison, runbook drafting | Codex / Claude |
| Command execution, config edits, verification evidence | Codex / Claude, with explicit approval for production-impacting steps |
| Production go/no-go and rollback decisions | Hafiz |
| Post-change monitoring and incident summaries | Codex / Claude |

This changes the hosting trade-off. Self-managed VPS is less scary because an LLM can prepare commands, check logs, maintain runbooks, and verify outcomes. But it does **not** remove accountability or risk. The LLM should never independently decide to migrate, deploy, cut DNS, change payment callbacks, or cancel the old server.

Practical implication:

- Hostinger KVM8 becomes viable because Sifututor has an AI-assisted technical operator.
- Managed hosting still has value because provider support can help when the problem is below the app layer: network, disk, hypervisor, cPanel/WHM, malware tooling, backups.
- The correct pattern is "LLM executes a checklist; Hafiz approves each production gate."

---

## Current Production Server

### HostArmada Site Carrier

| Item | Current state |
|---|---|
| IP | `151.246.1.164` |
| Virtualisation | KVM confirmed |
| CPU | 6x AMD EPYC 7413 |
| RAM | 16 GB |
| Disk | 320 GB NVMe, about 50% used |
| OS | AlmaLinux 9.8 + cPanel/WHM |
| Price | $74.23/mo promo, $148.45/mo regular, from account/server data |
| Datacenter | US-based estimate; confirm in HostArmada panel/support before final decision |
| CloudLinux LVE | Not active on this server |
| MySQL Governor | Not installed |
| Redis | Installed, running on `127.0.0.1:6379`, idle |
| Supervisor | Not installed |
| Queue method | `queue:work --stop-when-empty` from cron every minute |
| Queue driver | `database` |
| Cache driver | `database` |
| Slow query log | 36,396 entries at 3s threshold |
| MySQL CPU | Around 22% sustained |

Important correction: this is not behaving like a throttled shared-hosting account. It is a KVM VPS with root access and cPanel/WHM. That means many production improvements can be made **without** changing host.

Related documentation note: if any older Sifututor infrastructure reference still calls this server "shared hosting", treat that as stale shorthand unless a fresh HostArmada panel/support check proves otherwise.

---

## Performance Diagnosis

### 1. `notifications` Is The Primary Database Bottleneck

Current table shape from the local migrations:

- `id`
- `user_id`
- `title`
- `message`
- `type`
- `status`
- `sender`
- `data` JSON
- `acknowledged_at`
- timestamps
- `deleted_at`

The production table has 768,876 rows and only `PRIMARY KEY(id)`.

Slow query patterns found in the codebase:

```php
Notification::where('user_id', $userId)
    ->where('type', $type)
    ->whereNull('deleted_at')
    ->orderBy('id', 'desc')
    ->paginate(...)
```

```php
Notification::where('user_id', $tutorId)
    ->where('type', 'tutor')
    ->where('sender', 'EvaluationReport')
    ->where('status', 'new')
    ->whereJsonContains('data->student_id', $studentId)
    ->whereJsonContains('data->subject_id', $subjectId)
    ->whereJsonContains('data->request_id', $requestId)
    ->delete();
```

Why these are slow:

- No index begins with `user_id`, so MySQL must scan a large part of the table for user-specific notification lists.
- `ORDER BY id DESC` cannot be satisfied efficiently for each user without a composite index ending in `id`.
- JSON filters cannot use a normal B-tree index unless the JSON values are extracted into generated or functional indexed columns.
- Long scans and delete/update operations create lock waits. That explains why even primary-key inserts and updates can show multi-second delay.

Recommended Phase 1 indexes:

```php
Schema::table('notifications', function (Blueprint $table) {
    $table->index(
        ['user_id', 'type', 'deleted_at', 'id'],
        'idx_notif_user_type_deleted_id'
    );

    $table->index(
        ['user_id', 'status', 'deleted_at', 'id'],
        'idx_notif_user_status_deleted_id'
    );

    $table->index(
        ['user_id', 'sender', 'status', 'deleted_at'],
        'idx_notif_user_sender_status_deleted'
    );

    $table->index(
        ['sender', 'type', 'deleted_at', 'created_at'],
        'idx_notif_sender_type_deleted_created'
    );
});
```

Production rollout notes:

- Add indexes in a migration, but test the migration on a recent production copy first.
- Capture `SHOW INDEX FROM notifications`, representative `EXPLAIN` output, slow-query volume, and endpoint timing before the change.
- Run during a low-traffic window and confirm whether the exact MySQL version supports the chosen online DDL behavior.
- Keep the rollback plan practical: usually a follow-up `DROP INDEX`, not a full database rollback.

Expected impact:

- Mobile notification list queries should move from table scans to index range scans.
- Lock waits on notification insert/update should fall sharply.
- MySQL CPU should drop, but the exact number must be measured with `EXPLAIN ANALYZE`, slow-query log deltas, and MySQL CPU after deployment.

Do **not** claim this will definitely reduce MySQL CPU from 22% to 3%. That is plausible but not proven until measured.

Recommended Phase 2 for JSON-heavy queries:

```sql
ALTER TABLE notifications
  ADD COLUMN data_student_id BIGINT GENERATED ALWAYS AS (
    CAST(JSON_UNQUOTE(JSON_EXTRACT(data, '$.student_id')) AS UNSIGNED)
  ) STORED,
  ADD COLUMN data_subject_id BIGINT GENERATED ALWAYS AS (
    CAST(JSON_UNQUOTE(JSON_EXTRACT(data, '$.subject_id')) AS UNSIGNED)
  ) STORED,
  ADD COLUMN data_request_id BIGINT GENERATED ALWAYS AS (
    CAST(JSON_UNQUOTE(JSON_EXTRACT(data, '$.request_id')) AS UNSIGNED)
  ) STORED,
  ADD COLUMN data_notification_id VARCHAR(32) GENERATED ALWAYS AS (
    JSON_UNQUOTE(JSON_EXTRACT(data, '$.notification_id'))
  ) STORED;

CREATE INDEX idx_notif_dedupe_report
ON notifications (
  user_id, type, sender, status, deleted_at,
  data_student_id, data_subject_id, data_request_id
);

CREATE INDEX idx_notif_user_request_notification
ON notifications (
  user_id, sender, deleted_at,
  data_request_id, data_notification_id
);
```

Phase 2 needs more caution than Phase 1 because it changes the table definition and generated expressions can fail if dirty JSON values cannot cast cleanly. Before writing this migration, first profile the real JSON values and prefer defensive expressions that safely return `NULL` for missing, empty, non-numeric, or malformed values.

### 2. Redis Is Installed But MySQL Is Doing Redis' Job

Current production settings:

```env
CACHE_STORE=database
QUEUE_CONNECTION=database
SESSION_DRIVER=database
```

Impact:

- Cache writes and reads hit MySQL.
- Queue jobs are inserted, polled, reserved, and deleted from MySQL.
- Sessions create more reads/writes in MySQL.
- MySQL is already strained by notification scans, so this compounds the bottleneck.
- Redis sits idle despite being the correct tool for fast ephemeral data.

Recommended change order:

1. Switch `CACHE_STORE=redis`.
2. Switch `QUEUE_CONNECTION=redis`.
3. Add Supervisor persistent workers.
4. Consider `SESSION_DRIVER=redis` after confirming session behavior and logout expectations.

I would not switch cache, queue, and session all at once in production. Cache and queue are the obvious first move; sessions can follow after a short test because users may be forced to re-login.

Production rollout notes:

- Confirm the Laravel Redis client and PHP Redis extension are installed before changing production configuration.
- Run `php artisan config:clear` / `php artisan config:cache` as part of the approved deployment steps, not by ad hoc shell changes.
- For queues, stop the cron-based `queue:work --stop-when-empty` path before enabling persistent workers so the same jobs are not processed twice.
- After switching queues, verify failed jobs, queue wait time, and one real notification/email job path.

### 3. Current Queue Architecture Works, But It Is A Workaround

Current method:

```bash
php artisan queue:work --stop-when-empty
```

run every minute by cron.

Pros:

- Simple.
- Survives without Supervisor.
- Fine for low queue volume.

Cons:

- Up to one-minute latency before jobs start.
- Boots Laravel repeatedly.
- Poor visibility into worker health.
- Poor control over concurrency.
- Easier to double-process jobs during migration if cron exists on two servers.

Recommended production model:

- Redis queue driver.
- Supervisor-managed persistent workers.
- Separate queues if needed: `default`, `notifications`, `emails`.
- Deploy process includes `php artisan queue:restart`.
- Worker logs are rotated.

Supervisor can be installed on the current HostArmada VPS because root access exists. This is not dependent on migration.

---

## Hosting Comparison

### Pricing Notes

All public pricing should be rechecked at checkout because hosting providers show different prices by country, term length, promo, currency, tax, and account state. Public plan pages are planning inputs, not purchase authority.

Key research corrections, rechecked on 2026-06-01:

- Hostinger's Malaysia VPS page currently shows KVM8 at $25.99/mo promotional and $49.99/mo renewal for 2 years, with 8 vCPU, 32 GB RAM, 400 GB NVMe, and 32 TB bandwidth. Localised RM pricing may appear by account, URL, currency, or checkout state; use checkout as final authority.
- Hetzner CPX42 at about $29.99/mo is Germany/Finland pricing. Official Hetzner 2026 pricing lists Singapore CPX42 at $65.99/mo.
- DigitalOcean Basic 8 GiB is $48/mo; Basic 16 GiB is $96/mo.
- Cloudways 8 GB managed plan is $88/mo on the currently visible pricing page.
- HostArmada Site Carrier exact $148.45/mo regular price is from Sifututor account/server data, not a currently visible public plan page.

### Infrastructure Table

| Option | Region fit | Specs | Public/account price | Management | Sifututor fit |
|---|---|---:|---:|---|---|
| HostArmada Site Carrier | Weak if US-based | 6 vCPU, 16 GB RAM, 320 GB NVMe | $148.45/mo regular, account data | Managed VPS + cPanel/WHM | Safest operational continuity, worst cost/latency value |
| Hostinger KVM8 Malaysia | Strong if KL selected | 8 vCPU, 32 GB RAM, 400 GB NVMe, 32 TB | $49.99/mo renewal on current Malaysia public page; checkout may localise currency | Self-managed VPS | Best cost/spec/latency if AI-assisted ops is accepted |
| Hetzner CPX42 Singapore | Good | 8 shared vCPU, 16 GB RAM, 320 GB | $65.99/mo official 2026 Singapore price | Self-managed VPS | No longer a bargain; good engineering provider, less compelling than Hostinger for MY |
| DigitalOcean Basic 8 GiB Singapore | Good | 4 vCPU, 8 GiB RAM, 160 GiB | $48/mo | Self-managed VPS | Reliable platform, but underpowered vs current 16 GB RAM server |
| DigitalOcean Basic 16 GiB Singapore | Good | 8 vCPU, 16 GiB RAM, 320 GiB | $96/mo | Self-managed VPS | Cleaner platform alternative; costlier and less RAM than Hostinger KVM8 |
| Cloudways 8 GB Singapore | Good | 4 vCPU, 8 GB RAM, 160 GB | $88/mo visible plan | Managed platform | Managed comfort, but weak specs for price |

### Provider-by-Provider Analysis

#### HostArmada Site Carrier

Best reason to stay:

- Least migration risk.
- cPanel/WHM convenience.
- Managed security tooling and support.
- Current production already works.
- Root access means Redis/Supervisor/index fixes can be implemented now.

Main problem:

- High regular cost for the resources.
- Likely worse latency to Malaysian users if the server is US-based.
- cPanel convenience does not solve database design issues.

Verdict:

Stay temporarily while fixing the application bottlenecks. Do not treat HostArmada as the cause of the current slow queries.

#### Hostinger KVM8

Best reason to choose:

- Strongest value: 8 vCPU, 32 GB RAM, 400 GB NVMe.
- Malaysia/KL availability is highly attractive for Malaysian users.
- Existing Sifututor/LLS experience with Hostinger lowers learning cost.
- Hostinger exposes VPS features useful for AI-assisted ops: API, templates, CloudPanel/cPanel options, weekly backups, snapshots.

Main risk:

- Self-managed means Sifututor owns OS patching, firewall, monitoring, MySQL tuning, backups, incident response, and restore drills.
- Public user reports about Hostinger VPS performance are mixed; CPU steal/noisy-neighbor risk should be checked on the actual node.
- Support is not a replacement for a managed sysadmin.

Verdict:

Best migration target if the team accepts the AI-assisted bare-VPS operating model. Buy only after confirming Malaysia/KL location at checkout and after a staging rehearsal.

#### Hetzner Singapore

Best reason to choose:

- Strong cloud engineering reputation.
- Singapore is close enough to Malaysia for low latency.
- Official, transparent pricing.

Main problem:

- CPX42 Singapore is $65.99/mo after Hetzner's 2026 price adjustment, not the old EU ~$28/mo figure.
- 16 GB RAM, not 32 GB.
- No existing Sifututor account/runbook familiarity compared with Hostinger.

Verdict:

Good provider, but not the value winner for this use case.

#### DigitalOcean Singapore

Best reason to choose:

- Mature platform, documentation, monitoring, snapshots, firewalls.
- Predictable pricing.
- Singapore region.

Main problem:

- $48/mo plan has only 8 GB RAM, which is a downgrade from current production.
- The comparable 16 GB plan is $96/mo, still less RAM than Hostinger KVM8.

Verdict:

Good conservative self-managed option if Hostinger reliability tests fail.

#### Cloudways

Best reason to choose:

- Managed platform reduces sysadmin burden.
- Includes useful operational conveniences: dashboard, backups, monitoring, SSL, support.

Main problem:

- Higher price for weaker specs.
- Platform abstraction can make Laravel queue/Supervisor/MySQL tuning less direct than a raw VPS.

Verdict:

Worth considering only if Hafiz wants managed comfort more than cost/spec efficiency.

---

## Recommendation

### Immediate Recommendation: Fix The App Layer First

Do these on the current HostArmada server before any migration:

1. Add Phase 1 `notifications` indexes.
2. Switch cache to Redis.
3. Switch queues to Redis.
4. Install Supervisor and run persistent workers.
5. Measure before/after:
   - MySQL CPU
   - slow-query count per hour
   - top 10 slow queries
   - mobile notification endpoint response time
   - queue wait time

This gives two benefits:

- It improves production immediately.
- It reduces migration risk because the app becomes quieter and easier to move.

Do not combine these into one production change. The safer sequence is:

1. Measure baseline and deploy Phase 1 indexes.
2. Re-measure slow queries and notification endpoint timing.
3. Switch cache to Redis.
4. Switch queues to Redis with Supervisor.
5. Decide separately whether sessions should move to Redis.

### Hosting Recommendation: Migrate To Hostinger KVM8, But Only After A Rehearsal

Hostinger KVM8 is the best target for Sifututor **if** these conditions are true:

- Checkout confirms Malaysia/KL datacenter for the purchased server.
- A staging clone runs successfully for at least several days.
- Backups and restore are tested, not merely configured.
- Monitoring exists before cutover.
- Hafiz is comfortable approving an AI-operated self-managed VPS process.

If any of those fail, stay on HostArmada longer or choose DigitalOcean Singapore as the more conservative cloud platform.

### Decision Matrix

| If Hafiz prioritises... | Best option |
|---|---|
| Lowest migration risk | Stay on HostArmada for now |
| Best cost/spec/latency | Hostinger KVM8 Malaysia |
| Better cloud platform predictability | DigitalOcean Singapore 16 GiB |
| Managed support over raw value | Cloudways or stay HostArmada |
| Lowest Singapore Hetzner-style cost | Not available; CPX42 Singapore is now $65.99/mo |

---

## Migration Plan

This is the safe path if Hostinger KVM8 is approved after the app-layer fixes.

### Phase 0: Pre-Migration Decisions

- Confirm target provider and datacenter.
- Confirm whether the new server will use a control panel, CloudPanel, or no panel; this affects web server, SSL, cron, backup, and mail operations.
- Confirm acceptable maintenance window.
- Confirm rollback rule: what error rate or failed smoke test triggers rollback.
- Confirm old HostArmada server remains paid and untouched for at least 7-14 days after cutover.

### Phase 1: Build New Server

- Provision KVM8 in Malaysia/KL.
- Install OS stack: Nginx or Apache, PHP 8.2, MySQL 8.4-compatible server, Redis, Supervisor, Certbot, firewall, log rotation.
- Match production PHP extensions and image/PDF tooling before moving traffic.
- Configure backups and snapshots.
- Configure monitoring for disk, CPU, RAM, MySQL, Redis, queue, SSL expiry, Laravel errors.
- Deploy code and build assets.

### Phase 2: Data And File Rehearsal

- Restore a production DB dump into the new server.
- Sync storage/uploads.
- Verify file permissions.
- Run smoke tests against a temporary domain or hosts-file override.
- Run mobile API checks for tutor and parent app flows.
- Verify queue jobs, email, push notification paths, and scheduled commands.

### Phase 3: Cutover Preparation

- Lower Cloudflare TTL at least 24 hours before cutover.
- Confirm FIUU/payment callbacks, OAuth redirects, mail DNS, SPF, DKIM, DMARC, and any IP allowlists.
- Confirm Cloudflare proxy mode and cookie/session behavior for every production hostname before changing origins.
- Freeze risky production changes.
- Prepare exact rollback commands and DNS rollback target.

### Phase 4: Cutover

- Put current app briefly into maintenance mode or read-only mode.
- Stop cron and queues on HostArmada.
- Take final DB dump.
- Sync final uploads/storage delta.
- Import final DB on new server.
- Start queues and cron on new server.
- Run smoke tests.
- Update Cloudflare origin/A records.
- Monitor logs and user-facing flows.

### Phase 5: Post-Cutover

- Keep HostArmada live as rollback for 7-14 days.
- Compare slow-query logs before/after.
- Verify mobile app behavior across real devices.
- Verify email deliverability.
- Verify payment callbacks.
- Only cancel HostArmada after the rollback window and backup restore test pass.

---

## Migration Risks

| Risk | Why it matters | Mitigation |
|---|---|---|
| Local uploads/files missed | User documents or images may disappear | Inventory and sync `storage/`, public uploads, symlinks |
| Queue double-processing | Old and new servers may process same jobs | Stop old cron/workers before starting new workers |
| Payment callback failure | FIUU may depend on URL/IP/cert behavior | Confirm callback URLs and allowlisting before cutover |
| Mail deliverability | New server IP changes SPF/DKIM/DMARC reputation | Use external SMTP where possible; test before cutover |
| MySQL config mismatch | Same app can behave differently under different SQL modes/tuning | Match versions/configs and test on production copy |
| Redis/session switch logs out users | Session backend change can invalidate sessions | Schedule and communicate if needed |
| Cron/scheduler drift | Missing or duplicated scheduled commands can affect invoices, notifications, reminders, and cleanup jobs | Inventory current cron before cutover; enable exactly once on the new server |
| PHP extension mismatch | Composer, image handling, PDFs, payments, or uploads may fail only after traffic moves | Compare current production extensions with the new server before rehearsal |
| DNS rollback confusion | Multiple domains point at production | Document every A/CNAME record before changing |
| Self-managed patching neglected | Security work becomes Sifututor's responsibility | Monthly AI-assisted maintenance checklist |
| Hostinger noisy neighbor / CPU steal | Cheap VPS value can vary by node | Benchmark actual node; monitor steal time; be ready to request move |

---

## Operating Runbook After Migration

If Sifututor moves to a self-managed VPS, the missing managed-hosting work must become a recurring checklist.

Weekly:

- Check disk usage.
- Check MySQL slow queries.
- Check Laravel production errors.
- Check queue failures and queue wait time.
- Confirm backups completed.

Monthly:

- Apply OS security updates during a low-traffic window.
- Test at least one backup restore to a non-production location.
- Review SSL expiry and DNS records.
- Review Redis memory usage.
- Review MySQL table growth: `notifications`, `user_logs`, `app_issue_reports`, `cache`.

Before every production change:

- Hafiz approves intent and timing.
- Codex/Claude prepares commands and rollback.
- Codex/Claude executes only approved steps.
- Hafiz makes go/no-go and rollback decisions.

---

## Open Questions

1. Can Hostinger checkout explicitly guarantee Malaysia/KL for the new KVM8?
2. Are production uploads/files fully local, or partly cloud-backed?
3. Is Sifututor using cPanel mail, external SMTP, or both?
4. Does FIUU allowlist callback IPs?
5. What exact HostArmada datacenter is production in? Confirm in panel/support instead of relying only on IP geolocation.
6. Is every production hostname behind Cloudflare in the same proxy mode, and will that mode stay unchanged during cutover?
7. Which MySQL-compatible server should KVM8 run: MySQL 8.4, MariaDB, or match current production exactly?
8. What is the real low-traffic window for Malaysian users based on access logs?

---

## Sources Checked

- Hostinger Malaysia VPS pricing and KVM8 specs, rechecked 2026-06-01: https://www.hostinger.com/vps/servers/malaysia
- Hostinger plan limits: https://www.hostinger.com/support/6976044-parameters-and-limits-of-hosting-plans-in-hostinger/
- HostArmada VPS page: https://hostarmada.com/vps-hosting/
- Hetzner 2026 price adjustment, including Singapore CPX42 at $65.99/mo, rechecked 2026-06-01: https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/
- DigitalOcean Droplet pricing, rechecked 2026-06-01: https://www.digitalocean.com/pricing/droplets
- Cloudways pricing, rechecked 2026-06-01: https://www.cloudways.com/en/pricing.php
- Laravel queues and Supervisor guidance: https://laravel.com/docs/11.x/queues
- Laravel cache stores: https://laravel.com/docs/11.x/cache
- MySQL index optimization: https://dev.mysql.com/doc/mysql/en/optimization-indexes.html
- MySQL multi-column indexes: https://dev.mysql.com/doc/refman/8.4/en/multiple-column-indexes.html
