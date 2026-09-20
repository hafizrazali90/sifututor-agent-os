# Agent Access Map

Single source of truth for all approved Sifututor agent access lanes.
Covers Claude Code, Codex, and future agents.

Current registry count: 23 lanes — 21 scoped files under
`~/.config/sifututor/agent-access/`, the Microsoft 365 Planner env lane, and
the delegated SharePoint read-only lane.

**Rule for agents**: Before declaring access unavailable, consult this map and run
the relevant wrapper script in `scripts/agent-access/`. Access that appears in this
map is already approved for the stated tier. If the lane is `auto-read` and it is
relevant to the active task, use it proactively instead of asking Hafiz to remind
the agent to check. This applies across diagnosis, planning, verify, QA, review,
monitoring, release checks, and safe current-state evidence gathering.

Credential files live in `~/.config/sifututor/agent-access/`.
Do NOT read, echo, print, log, or commit secret values from any lane.

---

## Approval Tiers

| Tier | Meaning | Hafiz approval needed? |
|------|---------|----------------------|
| **auto-read** | Read-only; expected whenever the task needs current evidence | No |
| **write** | Modifies data, DNS, or config | Yes — state exact scope before acting |
| **admin** | Full management plane; can break production | Yes — per-session explicit approval |
| **critical** | Real money, real users, production DB writes | Yes — diagnosis first, then separate approval |
| **destructive** | Deletes data, forces keys, drops tables | Yes — always separate current-session approval |

---

## Lane Registry

### 1. `production-smoke` — SIMS Production Smoke Login

| Field | Value |
|-------|-------|
| **Conf file** | `production-smoke.conf` |
| **Base URL** | `https://st.admin.sifututor.my` |
| **Purpose** | Verify SIMS production responds and login endpoint is reachable |
| **Tier** | auto-read |
| **Allowed operations** | HTTP GET/HEAD smoke requests; verify HTTP response codes |
| **Hafiz approval** | Not required |
| **Safe verification** | `scripts/agent-access/check-ripple-prod.sh` |
| **Forbidden** | Do not log in with real credentials to read production data; do not POST admin actions |

---

### 2. `staging-smoke` — SIMS Staging Smoke Login

| Field | Value |
|-------|-------|
| **Conf file** | `staging-smoke.conf` |
| **Base URL** | `https://sifu-staging.tutorla.tech` |
| **Purpose** | Verify SIMS staging responds and login is reachable after a deploy |
| **Tier** | auto-read |
| **Allowed operations** | HTTP GET/HEAD smoke requests; verify response codes |
| **Hafiz approval** | Not required |
| **Safe verification** | `curl -sI https://sifu-staging.tutorla.tech/login` |
| **Forbidden** | Do not use staging to test production-only behavior |

---

### 3. `creative-hub-production-smoke` — Creative Hub Smoke

| Field | Value |
|-------|-------|
| **Conf file** | `creative-hub-production-smoke.conf` |
| **Base URL** | `https://creative.admin.sifututor.my` |
| **Purpose** | Verify Creative Hub production is responding |
| **Tier** | auto-read |
| **Allowed operations** | HTTP GET/HEAD smoke requests |
| **Hafiz approval** | Not required |
| **Safe verification** | `curl -sI https://creative.admin.sifututor.my/login` |
| **Forbidden** | Do not write data or trigger builds |

---

### 4. `database-readonly` — SIMS Production Database (Read-Only)

| Field | Value |
|-------|-------|
| **Conf file** | `database-readonly.conf` |
| **Host** | `151.246.1.164:3306` |
| **Database** | `sifututortutorla_LiveDB` |
| **Username** | `sims_agent_readonly` |
| **Purpose** | Read SIMS production data for analysis, debugging, reporting |
| **Tier** | auto-read |
| **Allowed operations** | `SELECT` only; `EXPLAIN`; `SHOW COLUMNS`; `SHOW INDEX` |
| **Hafiz approval** | Not required for reads; required if results will be stored/shared |
| **Safe verification** | `scripts/agent-access/check-sims-db-readonly.sh` |
| **Forbidden** | No `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`; do not export full tables; do not print PII columns (emails, phones, IC numbers) to terminal |

---

### 5. `lls-database-readonly` — LLS Production Database (Read-Only)

| Field | Value |
|-------|-------|
| **Conf file** | `lls-database-readonly.conf` |
| **Host** | `187.77.157.173:3306` |
| **Database** | `learnest_lls` |
| **Username** | `lls_agent_readonly` |
| **Purpose** | Read Learnest (LLS) production data for analysis and debugging |
| **Tier** | auto-read |
| **Allowed operations** | `SELECT` only |
| **Hafiz approval** | Not required for reads |
| **Safe verification** | `mysql -h 187.77.157.173 -P 3306 -u lls_agent_readonly -p"$LLS_DB_READONLY_PASSWORD" -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='learnest_lls';"` (after sourcing conf) |
| **Forbidden** | No writes; do not print PII |

---

### 6. `database-admin` — SIMS Production Database (Admin) ⚠️ CRITICAL

| Field | Value |
|-------|-------|
| **Conf file** | `database-admin.conf` |
| **Host** | `151.246.1.164:3306` |
| **Database** | `sifututortutorla_LiveDB` |
| **Allowed actions** | `approved-sql-only` |
| **Purpose** | Admin-level SQL operations: migrations, schema fixes, data repairs |
| **Tier** | critical |
| **Hafiz approval** | **Required per-operation.** State exact SQL before executing. |
| **Safe verification** | Use `database-readonly` lane first to diagnose; present SQL for approval |
| **Forbidden** | Never run without exact pre-approval; never run mass `DELETE`/`TRUNCATE`; always include `WHERE`; never drop tables |

---

### 7. `cloudflare-readonly` — Cloudflare Read-Only

| Field | Value |
|-------|-------|
| **Conf file** | `cloudflare-readonly.conf` |
| **Zones** | `tutorla.tech` (primary) |
| **Allowed actions** | `read-zone-read-dns-read-ssl-read-waf` |
| **Purpose** | Inspect DNS records, SSL status, WAF rules, zone settings |
| **Tier** | auto-read |
| **Hafiz approval** | Not required |
| **Safe verification** | `scripts/agent-access/check-cloudflare-dns.sh` |
| **Forbidden** | This token is read-only; do not attempt writes (they will fail) |

---

### 8. `cloudflare-dns-write` — Cloudflare DNS Write (tutorla.tech)

| Field | Value |
|-------|-------|
| **Conf file** | `cloudflare-dns-write.conf` |
| **Zones** | `tutorla.tech` |
| **Allowed actions** | `edit-dns-only` |
| **Purpose** | Add, update, or delete DNS records for `tutorla.tech` |
| **Tier** | write |
| **Hafiz approval** | Required — state exact record type/name/value before change |
| **Safe verification** | Check with `cloudflare-readonly` first; present planned change for approval |
| **Forbidden** | Do not change zone proxied status; do not touch Page Rules or WAF; do not delete wildcard records without approval |

---

### 9. `cloudflare-sifututormy-dns-write` — Cloudflare DNS Write (sifututor.my)

| Field | Value |
|-------|-------|
| **Conf file** | `cloudflare-sifututormy-dns-write.conf` |
| **Zones** | `sifututor.my` (zone ID `443fcca6`) |
| **Allowed actions** | `edit-dns-only` |
| **Purpose** | Add, update, or delete DNS records for `sifututor.my` |
| **Tier** | write |
| **Hafiz approval** | Required — state exact record before change |
| **Safe verification** | Read current records with `cloudflare-readonly` if zone overlaps; otherwise use this token for GET first |
| **Forbidden** | Do not change proxy status; do not touch MX or SPF records without approval |

---

### 10. `cloudflare-admin` — Cloudflare Zone Admin ⚠️ HIGH RISK

| Field | Value |
|-------|-------|
| **Conf file** | `cloudflare-admin.conf` |
| **Allowed actions** | `zone-admin` |
| **Purpose** | Full zone management: SSL modes, Page Rules, WAF, redirect rules, Workers |
| **Tier** | admin |
| **Hafiz approval** | **Required per change.** Zone admin can affect all Sifututor traffic. |
| **Safe verification** | Use `cloudflare-readonly` for inspection; only escalate to admin after approval |
| **Forbidden** | Do not change zone SSL mode to "Off"; do not disable WAF; do not add redirect rules that affect `st.admin.*` or payment paths without approval |

---

### 11. `cpanel-admin` — cPanel / WHM Admin (Web Voyager Staging)

| Field | Value |
|-------|-------|
| **Conf file** | `cpanel-admin.conf` |
| **Base URL** | `https://151.246.1.218:2087` (WebVoyager WHM) |
| **Username** | `root` |
| **Allowed actions** | `approved-cpanel-actions-only` |
| **Purpose** | Manage staging server: SSL installs, vhost config, AutoSSL, cPanel accounts |
| **Tier** | admin |
| **Hafiz approval** | Required for any change; SSH + WHM API writes affect shared staging hosting |
| **Safe verification** | `scripts/agent-access/check-cpanel-autossl.sh` |
| **Forbidden** | Do not add/remove cPanel accounts; do not change PHP version without approval; do not touch production server (151.246.1.164) via this lane — use `server-admin` SSH instead |

---

### 12. `server-ssh` — Production and Staging SSH (Standard)

| Field | Value |
|-------|-------|
| **Conf file** | `server-ssh.conf` |
| **Production alias** | `production` → `151.246.1.164:19199` |
| **Production app dir** | `/home/sifututortutorla/public_html` |
| **Staging alias** | `webvoyager` → `151.246.1.218:19199` |
| **Purpose** | SSH read access: read logs, check config, verify app state, SSL cert inspection |
| **Tier** | auto-read for non-destructive reads; write-tier for any file modification |
| **Hafiz approval** | Not required for reads; required for writes, restarts, or any command that changes server state |
| **Safe verification** | `ssh production "echo connected && php -v"` |
| **Forbidden** | Do not run `rm`, `mv`, destructive SQL, or `systemctl stop` without approval; do not modify `.env` files; do not push code via SSH directly |

---

### 13. `server-admin` — Production and Staging SSH (Admin) ⚠️ HIGH RISK

| Field | Value |
|-------|-------|
| **Conf file** | `server-admin.conf` |
| **Notes** | `high-risk-server-access` |
| **Purpose** | Admin server operations: SSL renewal, nginx reload, PHP config, cron edits, AutoSSL repair |
| **Tier** | admin |
| **Hafiz approval** | Required for any destructive or service-affecting command |
| **Safe verification** | State exact command before running; use `server-ssh` lane for reads first |
| **Forbidden** | Never `rm -rf` app directories; never kill php-fpm or nginx without a restart plan; never modify production `.htaccess` in ways that break auth |

---

### 14. `monitoring-readonly` — Sentry + BetterStack (Read-Only)

| Field | Value |
|-------|-------|
| **Conf file** | `monitoring-readonly.conf` |
| **Sentry org** | `sifu-edu-learning-sdn-bhd` |
| **Sentry project** | `sims-sifu-tutor` |
| **BetterStack team** | `sifututor` |
| **Purpose** | Read error events, uptime monitors, log drain; diagnose production issues |
| **Tier** | auto-read |
| **Hafiz approval** | Not required for reads; required if resolving/snoozing Sentry issues at scale |
| **Safe verification** | `scripts/agent-access/check-monitoring.sh` |
| **Forbidden** | Do not bulk-resolve Sentry issues without review; do not create or delete BetterStack monitors |

---

### 15. `payment-readonly` — FIUU Payment Gateway (Read-Only)

| Field | Value |
|-------|-------|
| **Conf file** | `payment-readonly.conf` |
| **Purpose** | Verify FIUU transaction status; look up payment references for debugging |
| **Tier** | auto-read |
| **Hafiz approval** | Not required for status lookups |
| **Safe verification** | `scripts/agent-access/check-ripple-prod.sh` (includes payment API reachability) |
| **Forbidden** | Do not use this lane to trigger charges, refunds, or voids — use `payment-write` which requires approval |

---

### 16. `payment-write` — FIUU Payment Gateway (Write) ⚠️ CRITICAL

| Field | Value |
|-------|-------|
| **Conf file** | `payment-write.conf` |
| **API host** | `https://api.fiuu.com` |
| **App** | `sifututormy` |
| **Allowed actions** | `approved-payment-actions-only` |
| **Purpose** | Trigger refunds or voids under direct Hafiz approval; approved payment write-backs |
| **Tier** | critical |
| **Hafiz approval** | **Required per transaction.** State invoice ID, amount, and action before any call. |
| **Safe verification** | Use `payment-readonly` to verify status first; never write without a verified read |
| **Forbidden** | Never trigger a charge or refund speculatively; never retry a failed charge; do not share or log the secret key |

---

### 17. `backup-readonly` — Backup Storage (Read-Only)

| Field | Value |
|-------|-------|
| **Conf file** | `backup-readonly.conf` |
| **Provider** | S3 (compatible) |
| **Region** | `us-east-1` |
| **Purpose** | Verify backups exist; list objects; check last backup timestamp |
| **Tier** | auto-read |
| **Hafiz approval** | Not required for listing |
| **Safe verification** | `scripts/agent-access/check-backups.sh` |
| **Forbidden** | Do not download full backup archives; do not delete objects |

---

### 18. `backup-admin` — Backup Storage (Admin) ⚠️ DESTRUCTIVE RISK

| Field | Value |
|-------|-------|
| **Conf file** | `backup-admin.conf` |
| **Allowed actions** | `approved-backup-actions-only` |
| **Purpose** | Emergency restore operations; backup lifecycle management |
| **Tier** | destructive |
| **Hafiz approval** | **Required per operation.** Deleting backups is irreversible. |
| **Safe verification** | Use `backup-readonly` lane first to verify what exists |
| **Forbidden** | Never delete backup objects without explicit approval naming the specific object; never overwrite an existing backup |

---

### 19. `wasabi-ripple-storage-scoped` — Wasabi Storage (Scoped Ripple)

| Field | Value |
|-------|-------|
| **Conf file** | `wasabi-ripple-storage-scoped.conf` |
| **Bucket** | `sifututor-ripple-suite` |
| **Region** | `ap-southeast-1` |
| **Purpose** | Read/write Ripple Suite user uploads (tutor photos, documents) with scoped key |
| **Tier** | auto-read for reads; write-tier for uploads or deletes |
| **Hafiz approval** | Not required for listing/reading; required for deletes |
| **Safe verification** | `scripts/agent-access/check-backups.sh --wasabi` |
| **Forbidden** | Do not delete user uploads without approval; do not list/copy to external storage |

---

### 20. `wasabi-ripple-storage` — Wasabi Storage (Full Bucket)

| Field | Value |
|-------|-------|
| **Conf file** | `wasabi-ripple-storage.conf` |
| **Bucket** | `sifututor-ripple-suite` |
| **Region** | `ap-southeast-1` |
| **Purpose** | Full bucket management for Ripple Suite storage; migration or lifecycle operations |
| **Tier** | write |
| **Hafiz approval** | Required for deletes or lifecycle changes; reads allowed |
| **Safe verification** | `scripts/agent-access/check-backups.sh --wasabi` |
| **Forbidden** | Do not delete objects without approval; do not change bucket policy or ACLs |

---

### 21. `m365-readonly` — Microsoft 365 / Teams Planner (Read-Only)

| Field | Value |
|-------|-------|
| **Conf file** | `~/.config/sifututor/m365-readonly.env` |
| **Access method** | Lokka MCP (`mcp__microsoft365__Lokka-Microsoft`) or `~/.codex/bin/m365-lokka-from-agent-access.sh` |
| **Purpose** | Read Teams Planner cards (`Development & Support > Task Management Board`) for staff-reported issues and intake |
| **Tier** | auto-read |
| **Hafiz approval** | Not required for reading intake cards |
| **Safe verification** | `scripts/agent-access/check-microsoft-planner.sh` |
| **Forbidden** | Do not change Planner card state, assignment, or priority; do not post to Teams channels; read-only intake only |

---

### 22. `ripple-staging-smoke` — Ripple Staging Authenticated Luna QA

| Field | Value |
|-------|-------|
| **Conf file** | `ripple-staging-smoke.conf` |
| **Base URL** | `https://ripple-staging.tutorla.tech` |
| **Purpose** | Reusable authenticated staging QA with separate Luna Superadmin and restricted identities |
| **Tier** | write on staging only |
| **Hafiz approval** | Required before authenticated journeys that create or change staging data; read-only login and GET checks may be reused after the task boundary is approved |
| **Safe verification** | `scripts/agent-access/check-ripple-staging-auth.sh` |
| **Allowed operations** | Luna staging login, role/permission checks, temporary conversation creation and mode selection, dashboard/settings redaction checks, Eval access checks; clean up temporary rows |
| **Session cache** | Playwright auth states may be cached only under the external mode-700 `agent-access/runtime/` directory; files must be mode 600, revalidated through `/api/auth/me`, and expire from reuse after 15 minutes |
| **Forbidden** | Never use on production; never print or commit credentials, cookies, or tokens; never send a paid AI request unless separately approved; never leave temporary conversations or Eval runs behind |

Expected variable names:

```bash
RIPPLE_STAGING_BASE_URL=...
RIPPLE_STAGING_SUPERADMIN_EMAIL=...
RIPPLE_STAGING_SUPERADMIN_PASSWORD=...
RIPPLE_STAGING_RESTRICTED_EMAIL=...
RIPPLE_STAGING_RESTRICTED_PASSWORD=...
```

Set `RIPPLE_STAGING_FORCE_RELOGIN=1` for the first smoke after changing either
QA credential or Ripple role/permission assignment. Respect the login limiter;
do not restart the app or bypass the control to force an immediate run.

---

### 23. `sharepoint-readonly` — SharePoint Files (Delegated Read-Only)

| Field | Value |
|-------|-------|
| **Config** | `~/.config/sifututor/sharepoint-readonly.json` (mode 600) |
| **Token cache** | `~/.config/sifututor/runtime/sharepoint-token.json` (mode 600) |
| **Access method** | `scripts/agent-access/sharepoint-readonly.py` from any ordinary shell or agent |
| **Purpose** | List approved folders, inspect safe metadata, and download explicitly requested files into an approved local root |
| **Tier** | auto-read after Hafiz completes the one-time delegated Microsoft sign-in |
| **Hafiz approval** | Required for first login/consent and expanding site, drive, path, host, or download boundaries; not required for later reads inside the approved boundary |
| **Safe verification** | `scripts/agent-access/sharepoint-readonly.py probe` |
| **Allowed operations** | `probe`, `login`, `list`, `metadata`, `download` |
| **Forbidden** | No upload, create, edit, move, rename, share, permission change, or delete; never print tokens; never access outside the configured drive/path/download boundary |

The public-client registration should request the least delegated scope that
works for the approved library. Prefer `Files.Read`; use broader read scope
only when Microsoft requires it and Hafiz accepts that scope. Microsoft
`Selected` scopes need a separate resource assignment and must not be guessed
or granted by an agent.

The mode-600 configuration contains identifiers and boundaries, not a client
secret:

```json
{
  "tenant_id": "<tenant id>",
  "client_id": "<public client application id>",
  "drive_id": "<approved document-library drive id>",
  "allowed_path_prefixes": ["Shared Documents/Approved Folder"],
  "allowed_download_hosts": ["*.sharepoint.com"],
  "download_root": "/absolute/local/approved/download/root",
  "max_download_bytes": 26214400,
  "scopes": ["Files.Read", "offline_access"]
}
```

Device sign-in and consent are owner actions. Agents must not initiate `login`
unless Hafiz explicitly asks in the current session. The probe never initiates
sign-in and prints status only.

Microsoft references: [device code flow](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-device-code),
[Graph paging](https://learn.microsoft.com/en-us/graph/paging),
[list folder contents](https://learn.microsoft.com/en-us/graph/api/driveitem-list-children),
and [selected SharePoint permissions](https://learn.microsoft.com/en-us/graph/permissions-selected-overview).

---

## Quick Reference: Approval Matrix

| Lane | Conf file | Tier | Approval |
|------|-----------|------|----------|
| `production-smoke` | `production-smoke.conf` | auto-read | Never |
| `staging-smoke` | `staging-smoke.conf` | auto-read | Never |
| `creative-hub-production-smoke` | `creative-hub-production-smoke.conf` | auto-read | Never |
| `database-readonly` | `database-readonly.conf` | auto-read | Never |
| `lls-database-readonly` | `lls-database-readonly.conf` | auto-read | Never |
| `cloudflare-readonly` | `cloudflare-readonly.conf` | auto-read | Never |
| `monitoring-readonly` | `monitoring-readonly.conf` | auto-read | Never |
| `payment-readonly` | `payment-readonly.conf` | auto-read | Never |
| `server-ssh` (reads) | `server-ssh.conf` | auto-read | Never |
| `backup-readonly` | `backup-readonly.conf` | auto-read | Never |
| `wasabi-ripple-storage-scoped` (reads) | `wasabi-ripple-storage-scoped.conf` | auto-read | Never |
| `m365-readonly` | `m365-readonly.env` | auto-read | Never |
| `sharepoint-readonly` | `sharepoint-readonly.json` + private runtime token cache | auto-read after first consent | First login and boundary expansion only |
| `ripple-staging-smoke` | `ripple-staging-smoke.conf` | write (staging only) | Yes — authenticated mutation scope |
| `cloudflare-dns-write` | `cloudflare-dns-write.conf` | write | Yes — state record |
| `cloudflare-sifututormy-dns-write` | `cloudflare-sifututormy-dns-write.conf` | write | Yes — state record |
| `server-ssh` (writes) | `server-ssh.conf` | write | Yes — state command |
| `wasabi-ripple-storage` (writes) | `wasabi-ripple-storage.conf` | write | Yes — state object |
| `cpanel-admin` | `cpanel-admin.conf` | admin | Yes — per action |
| `cloudflare-admin` | `cloudflare-admin.conf` | admin | Yes — per change |
| `server-admin` | `server-admin.conf` | admin | Yes — per command |
| `database-admin` | `database-admin.conf` | critical | Yes — per SQL |
| `payment-write` | `payment-write.conf` | critical | Yes — per transaction |
| `backup-admin` | `backup-admin.conf` | destructive | Yes — per object |

---

## Safe Wrapper Scripts

All wrappers live in `scripts/agent-access/`. They source conf files safely and
never print secret values.

| Script | What it checks |
|--------|---------------|
| `agent-access-doctor.sh` | All lanes — connectivity and config presence |
| `check-st-admin-cert.sh` | SSL cert for `st.admin.sifututor.my` (expiry, issuer, SANs) |
| `check-ripple-prod.sh` | Ripple Suite production: PM2 status, HTTP login check, SIMS API reachability |
| `check-ripple-staging-auth.sh` | Ripple staging: reusable authenticated Luna Superadmin/restricted RBAC journey |
| `check-sims-db-readonly.sh` | SIMS DB readonly lane: connection test, row count spot-check |
| `check-cloudflare-dns.sh` | DNS records for key domains via CF read-only API |
| `check-cpanel-autossl.sh` | AutoSSL last-run status on production by default; pass `--staging` for WebVoyager |
| `check-monitoring.sh` | Sentry unresolved issues count; BetterStack monitor status |
| `check-microsoft-planner.sh` | Lokka / M365 access availability |
| `check-backups.sh` | Backup storage object count and latest timestamp |

---

## Codex Usage Pattern

When Codex needs infrastructure access for a task:

```text
1. Identify the required lane from this map.
2. Check the tier. If auto-read and relevant → proceed without asking.
3. If write/admin/critical → state the exact action and lane to Hafiz, wait for approval.
4. Run the safe wrapper first to confirm access is working.
5. Source the conf file in a subshell. Do not echo secrets.
6. Perform the approved operation.
7. Report results without including raw credentials or connection strings.
```

Example (read-only DB check):
```bash
# Allowed without approval — auto-read tier
source ~/.config/sifututor/agent-access/database-readonly.conf
mysql -h "$SIMS_DB_READONLY_HOST" -P "$SIMS_DB_READONLY_PORT" \
      -u "$SIMS_DB_READONLY_USERNAME" -p"$SIMS_DB_READONLY_PASSWORD" \
      "$SIMS_DB_READONLY_DATABASE" \
      -e "SELECT COUNT(*) AS total_tutors FROM tutors WHERE deleted_at IS NULL;" 2>/dev/null
```

Example (DNS write — requires approval):
```text
Agent: I need to update the A record for api.tutorla.tech from 1.2.3.4 to 5.6.7.8
       using the cloudflare-dns-write lane. Shall I proceed?
Hafiz: approve
Agent: [sources cloudflare-dns-write.conf, makes the specific API call]
```
