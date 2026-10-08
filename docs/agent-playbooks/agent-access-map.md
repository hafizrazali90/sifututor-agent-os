# Agent Access Map

Single source of truth for all approved Sifututor agent access lanes.
Covers Claude Code, Codex, and future agents.

Current registry count: 36 lanes (34 scoped files under
`~/.config/sifututor/agent-access/`, the Microsoft 365 Planner env lane, and
the delegated SharePoint read-only lane; lanes 40 and 41 have no file of their own).

**Rule for agents**: Before declaring access unavailable, consult this map and run
the relevant wrapper script in `scripts/agent-access/`. Access that appears in this
map is already approved for the stated tier. If the lane is `auto-read` and it is
relevant to the active task, use it proactively instead of asking Hafiz to remind
the agent to check. This applies across diagnosis, planning, verify, QA, review,
monitoring, release checks, and safe current-state evidence gathering.

Credential files live in `~/.config/sifututor/agent-access/`.
Do NOT read, echo, print, log, or commit secret values from any lane.

---

## Servers, Zones And Paths

Machine facts that were kept in the global `~/.claude/CLAUDE.md` and now live
here, so there is one place to correct them. They hold no credentials. Check
this table and the access lanes below before any production-affecting action;
Koda (`reference_server_environment_map`, `feedback_staging_environment`) is the
dated record when the two disagree.

| Alias (`~/.ssh/config`) | Address | Provider | Notes |
| --- | --- | --- | --- |
| `production` | `151.246.1.164` (port 19199) | HostArmada Site Carrier | sifu-tutor and nakngaji production |
| `staging` | `72.62.251.97` | Hostinger KVM8 | shared multi-tenant box: kelasapp, ripple-suite, creative-hub, Koda |
| `finch` | `187.127.98.182` | Hostinger KVM8 (finch) | sifu-tutor staging since 09/08/2026; also hosts finch-inbox |
| `webvoyager` | `151.246.1.218` (port 19199) | HostArmada Web Voyager | **Dead since 09/08/2026** (plan unsubscribed). Do not use. |

- `sims-staging.tutorla.tech` (the old Hostinger VPS URL) and `webvoyager` are
  both decommissioned. When Hafiz says "staging" for sifu-tutor, he means
  `sifu-staging.tutorla.tech` on the `finch` box, not Web Voyager.
- Cloudflare zone `tutorla.tech` is `ddcee6be0e754bc30573781940e5b96d`. DNS is
  DNS-only (not proxied) on the staging domains, because the Cloudflare proxy
  breaks Laravel session cookies. Cloudflare credentials are in
  `~/.cloudflare-credentials` and are never printed.
- Production SIMS app path: `/home/sifututortutorla/public_html` (cPanel/WHM KVM
  VPS), never `/var/www/sifu-tutor`.
- Never embed credential values in instruction files. Use the wrappers in
  `scripts/agent-access/` for database, admin or infrastructure checks.

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
| **Also used by** | `scripts/agent-access/check-app-firewall-blocks.sh`: aggregated analytics counts only (GraphQL `httpRequestsAdaptiveGroups`), no client addresses printed; Cloudflare keeps about 30 days |
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
| **Staging alias** | `finch` → `187.127.98.182` (sifu-tutor staging since 09/08/2026; `webvoyager` is dead, see "Servers, Zones And Paths") |
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

For FIUU sandbox investigation, check the authenticated merchant portal at
`https://sandbox-portal.fiuu.com/` before declaring simulator access unavailable.
Its left navigation includes **Bank Simulator** and a Testing Guide. Open the
Testing Guide's collapsed **FPX B2C** section for sandbox-only demo-bank login
instructions and masked credentials. This is separate from the live portal at
`https://portal.fiuu.com/` and from the FPX demo-bank login shown after a
hosted checkout. Use narrow UI inspection; do not print, log, or store portal
keys or simulator credentials.

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
| **Config** | `~/.config/sifututor/agent-access/sharepoint-readonly.conf` (mode 600); JSON is also supported for new installations |
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

The existing mode-600 conf uses `SHAREPOINT_TENANT_ID`,
`SHAREPOINT_CLIENT_ID`, `SHAREPOINT_DRIVE_ID`, one or more
`SHAREPOINT_FOLDER_<ALIAS>_ID` boundaries, and `SHAREPOINT_TOKEN_STORE`.
Agents address those roots as `@alias`, for example `@cx/report.docx`.
JSON configuration is also supported for new installations and contains
identifiers and boundaries, not a client secret:

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

### 24. `ripple-destination-readonly` — Ripple V16 Destination Read

| Field | Value |
|-------|-------|
| **Conf file** | `ripple-destination-readonly.conf` |
| **Purpose** | Read the small set of Ripple destination fields needed to confirm whether a V16 migration package still applies |
| **Tier** | auto-read |
| **Access method** | A local SSH tunnel to the production PostgreSQL service |
| **Allowed data** | `SELECT` on four purpose-built `v16_read_*` views only |
| **Hafiz approval** | Not required for reads through the existing lane; creation and initial scope were approved on 20 September 2026 |
| **Safe verification** | `scripts/agent-access/check-ripple-destination-readonly.sh` |
| **Run a scoped reader** | `scripts/agent-access/ripple-destination-readonly-run.sh -- <command>` provides `V16_DESTINATION_READ_URL` only to that child command |
| **Forbidden** | No base-table access, personal/free-text columns, writes, DDL, grants, role switching, view widening, or printing the connection URL |

The approved views are `v16_read_crm_requests`, `v16_read_tutor_conduct`,
`v16_read_onboarding_prospects`, and `v16_read_effect_receipts`. The verifier
checks their exact columns and proves that representative reads outside those
views, writes, and privilege escalation are refused. It prints only fixed
status labels and row counts.

This lane is separate from SharePoint. Do not add a V16-specific workbook
reader here; use the existing model-agnostic `sharepoint-readonly` lane for
approved SharePoint files.

---

### 25. `typesafe-jev-shadow` — TypeSafe Jev Advisory Provider

| Field | Value |
|-------|-------|
| **Conf file** | `typesafe-jev.conf` |
| **Purpose** | Supply typed, non-authoritative workflow-route advice to Claude and Codex |
| **Tier** | write (bounded external provider call) |
| **Allowed data** | A locally minimized first-sentence summary and workflow tags after secret/PII and critical-lane checks pass |
| **Hafiz approval** | Required once to enable the lane; this issue/session supplies that approval. No per-prompt approval after owner activation. |
| **Safe verification** | `python3 scripts/agent-access/check-jev-shadow.py --live` |
| **Kill switch** | Set `SIFUTUTOR_JEV_SHADOW=0` or remove the scoped conf file |
| **Forbidden** | No raw prompts, secrets, PII, approval state, production data, critical lanes, stored provider bodies, or authoritative actions |

The file must contain only `TYPESAFE_API_KEY=<value>` and must have mode
`0600`. Agents may verify only configured/not-configured status; they must
never print, copy, log, commit, or store the key.

---

### 26. `ripple-prod-smoke` — Ripple Production Authenticated Smoke

| Field | Value |
|-------|-------|
| **Conf files** | `ripple-prod-smoke.conf` (Admin smoke login); one file per extra role: `ripple-prod-smoke-helpdesk.conf` (QA Helpdesk, SIMS user 376, Helpdesk role), `ripple-prod-smoke-cxsales.conf` (QA CX Sales, SIMS user 377, Customer Experience (Sales) role) |
| **Base URL** | `https://ripple.admin.sifututor.my` |
| **Purpose** | The normal smoke and the change smoke after every Ripple production deploy ([release-deploy-live-monitoring.md](release-deploy-live-monitoring.md)) |
| **Tier** | auto-read (read-only browser and GET checks) |
| **Hafiz approval** | Not required for read-only smoke after an approved deploy; adding a new role login needs Hafiz to create the account |
| **Safe verification** | `ripple-suite/scripts/qa/prod-auth-smoke.sh`; set `RIPPLE_PROD_SMOKE_CONF` to pick the role file, and `RIPPLE_SMOKE_SPEC` / `RIPPLE_SMOKE_GREP` to run a release's read-only change-smoke spec under `tests/e2e/smoke/` |
| **Allowed operations** | Sign in, `GET` APIs, open pages, forms and dialogs, then back out; screenshots |
| **Forbidden** | Never submit or save anything (no cancel, payment, receipt, complaint, publish, assignment); never print or commit credentials, cookies or tokens |

Expected variable names in each file: `RIPPLE_PROD_SMOKE_EMAIL`, `RIPPLE_PROD_SMOKE_PASSWORD`.
A CX Sales login can open only Requests where it is the PIC, and it owns none,
so it proves role permissions (`/api/auth/me`) and refusals, not owned-Request
screens. A new SIMS staff login may get "Sign-in is temporarily unavailable"
for about a minute while Ripple catches up with the new SIMS revision.
Before saying a production login is unavailable for any project, list the file
names in `~/.config/sifututor/agent-access/` and the project's `scripts/qa/*smoke*`.

### 27. `betterstack-write` - Better Stack Telemetry (Write) ⚠️ WRITE

| Field | Value |
|-------|-------|
| **Conf file** | `betterstack-write.conf` (mode 600) |
| **Variable name** | `BETTERSTACK_TELEMETRY_API_TOKEN` (Telemetry API token Hafiz created 03/10/2026) |
| **Purpose** | Create log sources, explorations and exploration alerts; incident emails go to the current team |
| **Tier** | write |
| **Hafiz approval** | Yes: state the exact source, query and alert before creating; test incidents need approval because they email the team |
| **Safe verification** | `GET https://telemetry.betterstack.com/api/v2/sources` with the token; print only names and ids |
| **Forbidden** | Never print the token; never delete sources or alerts; never add call or SMS escalation without approval |

---

### 28. `sentry-write` - Sentry Alerts and Projects (Write) ⚠️ WRITE

| Field | Value |
|-------|-------|
| **Conf file** | `sentry-write.conf` (mode 600) |
| **Variable name** | `SENTRY_WRITE_TOKEN` |
| **Sentry org / host** | `sifu-edu-learning-sdn-bhd`, region host `https://de.sentry.io` |
| **Purpose** | Create workflows and detectors (`/organizations/{org}/workflows/`, `/detectors/`); the old `rules/` endpoints return 404 |
| **Tier** | write |
| **Hafiz approval** | Yes: state the exact alert before creating |
| **Safe verification** | `GET /api/0/organizations/{org}/workflows/` and print only names |
| **Known limits** | Members cannot create projects by API; Hafiz creates projects in the Sentry UI. Issues API `statsPeriod` accepts only `24h` or `14d` |
| **Forbidden** | Never print the token; never delete projects, workflows or issues; never bulk-resolve issues |

---

### 29. `monitoring-project-settings` - Per-Project Monitoring Addresses

| Field | Value |
|-------|-------|
| **Conf files** | `kelasapp-betterstack-prod.conf` (`KELASAPP_BS_HOST`, `KELASAPP_BS_TOKEN`), `lls-sentry-backend.conf` (`LLS_SENTRY_DSN`), `lls-sentry-frontend.conf` (`LLS_FRONTEND_SENTRY_DSN`), `ripple-sentry.conf` (`RIPPLE_SENTRY_DSN`); all mode 600 |
| **Purpose** | Hold the private ingest address of each production monitoring project so a probe or a redeploy can reuse it without asking again |
| **Server side** | LLS website build reads root-only `/etc/learnest/frontend-sentry.env`; Ripple reads `/etc/prod-env/ripple-suite.env`; Kelasapp reads `.env.local`; SIMS and LLS backend read their own `.env` (each backed up as `.pre-<change>-<time>` before the 03/10/2026 changes) |
| **Tier** | auto-read for using an address in a read-only probe; changing a server setting is write |
| **Hafiz approval** | Reads and probes: not required. Changing a server setting or sending a probe event to production Sentry: yes, exact action first |
| **Forbidden** | Never print an address or token; never copy these values into a handoff, issue, ledger or memory; a probe event must carry a clear synthetic label |

---

### 30. `sentry-issues-write` - Sentry Issue Status (Write) ⚠️ WRITE

| Field | Value |
|-------|-------|
| **Conf file** | `sentry-issues-write.conf` (mode 600) |
| **Variable name** | `SENTRY_ISSUES_TOKEN` |
| **Sentry org / host** | `sifu-edu-learning-sdn-bhd`, region host `https://de.sentry.io` |
| **Credential** | Sentry Internal Integration `sifututor-issue-resolver`, permission **Issue & Event: Read & Write** only, created by Hafiz 04/10/2026 |
| **Purpose** | Change the status of named Sentry issues (resolve a test or probe event, reopen one) |
| **Tier** | write |
| **Hafiz approval** | Yes: list the exact short IDs first. Used on 04/10/2026 for seven named test issues (RIPPLE-SUITE-1 and -2, LLS-FRONTEND-1, PHP-LARAVEL-LLS-BACKEND-5S, 5R, 5Q, SIMS-SIFU-TUTOR-7R) |
| **Safe verification** | `GET /api/0/organizations/{org}/issues/?limit=1` returns 200. Never test by writing |
| **Rules** | One issue per request, after reading its title and confirming it matches the approved description. Never a query-based or bulk update. Never delete issues. Never touch an issue another team owns without that owner's say |
| **Known limits** | Plain 64-character token with no `sntrys_` prefix is normal for an Internal Integration. A Client Secret is a different value and returns 401. Revoke the integration in Sentry when no longer needed |
| **Forbidden** | Never print the token; never paste it in chat; save it only through `save-sentry-token.sh`-style prompts that test the token and print no value |

---

### 31. `healthchecks-write` - Healthchecks.io Checks (Write) ⚠️ WRITE

| Field | Value |
|-------|-------|
| **Conf file** | `healthchecks-write.conf` (mode 600) |
| **Variable names** | `HC_API_KEY` (read-write API key), `HC_PING_KEY` (ping key) |
| **Host** | `https://healthchecks.io/api/v3` (pings go to `hc-ping.com`) |
| **Project** | `sifututor-monitoring` (free Hobbyist plan, 20 jobs), created by Hafiz 04/10/2026 |
| **Purpose** | Create, adjust, pause and list heartbeat checks for jobs on our servers. The ping key lets a job send its "I ran" signal by check name |
| **Tier** | write |
| **Hafiz approval** | Yes: list the exact checks (name, period, grace) before creating. The ping line on each server is a separate server-write approval per server |
| **Safe verification** | `GET /checks/` with the read-only key returns 200. Limits test on 04/10/2026: period 30 d with grace 5 d, and period 5 min with grace 1 min, were accepted; the two test checks were deleted |
| **Known limits** | The API cannot create integrations (email, Telegram): Hafiz adds them in the dashboard and checks are attached to them. Free plan: 20 jobs, 100 log entries per job |
| **Where the ping key lives on servers** | `/etc/sifututor/healthchecks-ping.env` (root, mode 600) on the Ripple host and the Learnest host. Used by `/opt/sifututor-monitoring/job-watcher.sh` (every minute, `/etc/cron.d/sifututor-job-watcher`) and by Koda's `/opt/koda/monitor-check.sh` and `/opt/koda/backup.sh`. The key is passed to curl on standard input, never as an argument. Reviewed watcher source: `Sifututor/sifututor-status`, `server/job-watcher.sh` |
| **Checks (04/10/2026)** | `koda-memory-check`, `koda-backup`, `ripple-offsite-backup`, `ripple-backup-retention`, `ripple-commitment-fee-settlement`, `ripple-commitment-fee-attention`, `lls-db-backup`, `kelasapp-db-backup`, and `lls-scheduler` (created, not wired: needs a signal from inside the Learnest app) |
| **Forbidden** | Never print a key or a ping address; never delete a check except one this session created; never use more than one account to get around limits |

---

### 32. `healthchecks-readonly` - Healthchecks.io Status (Read-Only)

| Field | Value |
|-------|-------|
| **Conf file** | `healthchecks-readonly.conf` (mode 600) |
| **Variable name** | `HC_READONLY_KEY` |
| **Purpose** | Read check status for the status page and for read-only checks. A read-only key omits ping addresses |
| **Tier** | auto-read |
| **Safe verification** | `GET https://healthchecks.io/api/v3/checks/` returns 200; print names and statuses only |
| **Forbidden** | Never print the key |

---

### 33. `wasabi-koda-backup-uploader` - Wasabi Koda Backups (Upload And Read Only)

| Field | Value |
|-------|-------|
| **Conf file** | `wasabi-koda-backup-uploader.conf` (mode 600). Server copy: `/etc/koda-backup/wasabi.env` on the Koda host, root only |
| **Variable names** | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION` |
| **Bucket** | `sifututor-koda-backups`, region `ap-southeast-1`, private, versioning on, objects expire after 90 days |
| **Credential** | Wasabi user `koda-backup` with policy `koda-backup-only`, created 04/10/2026 with the account keys at Hafiz's request |
| **Purpose** | The Koda server uploads its daily memory backup and reads it back to prove the copy is restorable |
| **Tier** | auto-read for listing; write for uploads (done by the server job, not by agents) |
| **Verified limits (04/10/2026)** | Allowed: list this bucket, upload, read back. Denied: delete, list other buckets, read the Ripple bucket, change versioning |
| **Restore** | 1. Stop Koda. 2. Download the wanted `daily/brain-<time>.db` with this key and compare its sha256 with the object's `sha256` metadata. 3. Replace `/opt/koda/brain.db` (and remove any `-wal` and `-shm` beside it), owner root, mode 600. 4. Start Koda and run `scripts/agent-checks/koda health`. Rehearsed 04/10/2026 up to step 2 in a scratch folder: 73 MB downloaded in 3 s, checksum matched, full integrity check ok, 50 of 50 schema objects, 6,848 memories (equal to the backup's own record), text search working. The swap under a stopped Koda (steps 3 and 4) has not been done. A daily backup means up to 24 hours of new memories can be lost |
| **Forbidden** | Never print the key; never widen the policy to delete; never use the account keys in `~/.wasabi-creds` for routine work |

### 34. `cloudflare-access-write` - Cloudflare Login Gate (Write) ⚠️ WRITE

| Field | Value |
|-------|-------|
| **Conf file** | `cloudflare-access-write.conf` (mode 600) |
| **Variable names** | `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ALLOWED_ACTIONS` |
| **Credential** | Cloudflare API token `agent-access-gate-write`, created by Hafiz 04/10/2026. Permissions: Access: Apps and Policies (Edit), Access: Service Tokens (Edit) |
| **Purpose** | Manage the Zero Trust Access login gate: applications, policies and service tokens. The other Cloudflare lanes cannot (all answer 403 on Access) |
| **Tier** | auto-read for listing applications, policies and service tokens; write needs Hafiz's approval per change |
| **Verified limits (04/10/2026)** | Allowed: read Access applications and service tokens, list zone names, list Worker script names. Denied: DNS records, account members, billing |
| **Known gate objects** | Application `Sifututor Status` (`status.sifututor.my`) with policies `Allowed people` (allow) and `robot sender` (Service Auth, reusable); service tokens `status-robot-sender`, `status-notes-claude`, `status-notes-codex`, all three included in `robot sender` |
| **Gotchas** | A policy is a reusable object: creating it does not attach it to an application, that is a second step. A service token's secret is shown once and cannot be read back. A logged-in dashboard session can read through the dashboard API but is refused on writes |
| **Forbidden** | Never print the key; never remove or widen the `Allowed people` policy; never delete a service token that a server is using |

### 35. `status-robot-sender` - Status Page Machine Pass (Hand In The Robot Report Only)

| Field | Value |
|-------|-------|
| **Conf file** | `status-robot-sender.conf` (mode 600). Server copy: `/etc/sifututor/status-robot-sender.env` on the Ripple host, root only |
| **Variable names** | `PASS_ID`, `PASS_KEY` |
| **Credential** | Cloudflare Access service token `status-robot-sender`, created by Hafiz 04/10/2026, allowed on `Sifututor Status` by the `robot sender` policy |
| **Purpose** | `/opt/sifututor-monitoring/robot-report-sender.sh` on the Ripple host hands the outreach robot's numbers to `https://status.sifututor.my/ingest/robot` every 5 minutes |
| **Tier** | Used by the server job, not by agents. Agents may use the local copy only to test that the gate still accepts it |
| **Verified limits (04/10/2026)** | The status page accepts a report only from this client id (`ROBOT_SENDER_CLIENT_ID`), keeps only agreed counts and flags, and refuses every read route to a machine pass |
| **Forbidden** | Never print the secret; never reuse this pass for another machine or another page |

### 36. `status-notes-claude` and `status-notes-codex` - Status Page Notes (Post A Note Only)

| Field | Value |
|-------|-------|
| **Conf files** | `status-notes-claude.conf`, `status-notes-codex.conf` (mode 600) |
| **Variable names** | `PASS_ID`, `PASS_KEY` |
| **Credential** | Cloudflare Access service tokens `status-notes-claude` and `status-notes-codex`, created 04/10/2026 with lane 34 on Hafiz's approval, allowed on `Sifututor Status` through the reusable policy `robot sender` |
| **Purpose** | Post one note to the status page's "What changed" list: what changed, why, and for which system |
| **How** | `sifututor-status/scripts/post-note.sh claude\|codex <system> "<what changed>" "<why>"`. Systems: `sims`, `ripple`, `robot`, `analytics`, `finch`, `apps`, `lls`, `kelas`, `koda`, `status`, `all` |
| **Tier** | auto-write for a truthful note about work the agent itself did; never to speak for another agent or for Hafiz |
| **Verified limits (04/10/2026)** | The page shows the author from the pass (`Claude` or `Codex`), never from the text. A note pass cannot post "went live" or "merged", cannot read the page, and is limited to 30 notes an hour. Notes cannot be edited or deleted |
| **Forbidden** | Never print the secret; never use one agent's pass from the other agent; never put a credential, a name of a private person or log text in a note |

### 37. `github-status-feed-readonly` - GitHub Merged Pull Requests For The Status Page (Read-Only)

| Field | Value |
|-------|-------|
| **Conf file** | `github-status-feed-readonly.conf` (mode 600). Not present until Hafiz runs `outputs/production-monitoring-verification-2026-10-04/save-github-feed-keys.sh` |
| **Variable names** | `GITHUB_TOKEN_SIFUTUTOR`, `GITHUB_TOKEN_LEARNEST_LAB` (a fine-grained key belongs to one owner, so there is one per owner) |
| **Purpose** | The status page lists merged pull requests of 10 repositories as "Merged" entries. Stored as Worker secrets of the same names with `node scripts/set-secrets.mjs <conf>`; no redeploy needed |
| **Tier** | Used by the status page, not by agents. Agents use `gh` for their own GitHub work |
| **Scope wanted** | Repository permission Pull requests: Read-only. Nothing else |
| **State (04/10/2026)** | Not created yet. Until it is, the page says "GitHub merges are not connected yet" |

### 38. `telegram-status-alerts` - Status Page Telegram Bot

| Field | Value |
|-------|-------|
| **Conf file** | `telegram-status-alerts.conf` (mode 600) |
| **Variable names** | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |
| **Credential** | Bot `@sifututor_status_bot` in the group "Sifututor Alerts", created by Hafiz 04/10/2026. Also stored as Worker secrets of the same names |
| **Purpose** | The status page sends alert messages to that group when `ALERTS_MODE` is `live` |
| **State (04/10/2026)** | `ALERTS_MODE = "dry-run"`: the page decides and logs, nothing is sent. Hafiz decided "web first, automation later"; going live needs his approval |
| **Forbidden** | Never print the token; never send a message with it by hand except a test Hafiz asked for; never change `ALERTS_MODE` without his approval |

### 39. `sims-staging-browser-qa` - SIMS Staging Browser QA Login

| Field | Value |
|-------|-------|
| **Conf files** | `sims-staging-browser-qa.conf` (mode 600): the QA login. `sims-staging-e2e.conf` (mode 600): `E2E_ADMIN_PASSWORD`, the one password shared by the 12 other seeded staging test accounts, read by the e2e fixtures and the seed commands |
| **Variable names** | `SIMS_BROWSER_QA_BASE_URL`, `SIMS_BROWSER_QA_EMAIL`, `SIMS_BROWSER_QA_PASSWORD` |
| **Base URL** | `https://sifu-staging.tutorla.tech` |
| **Credential** | The seeded staging admin (SIMS user 1, roles `admin` and `super-admin`), not a new account. On 08/10/2026, on Hafiz's instruction ("create all for me"), Claude replaced the weak shared default on the 13 staging accounts that still accepted it with random passwords written straight into these two files and never shown. The same new value was written into `staging-smoke.conf` and `ripple-staging-smoke.conf`, because Ripple staging signs in against the SIMS users table. `scripts/agent-access/setup-sims-browser-qa-lane.sh` is how Hafiz re-sets the QA login himself |
| **Purpose** | Lets the `browser-test` skill log in to SIMS staging and run the cases in `sifu-tutor/.claude/browser-test.yaml`. That file names this lane (`conf`, `email_var`, `password_var`) and holds no credential |
| **Tier** | write on staging only. This is the difference from `staging-smoke` (lane 2), which is GET and HEAD only |
| **Hafiz approval** | Required before any case that creates, edits or deletes staging data; read-only login and page checks may be reused once the task boundary is approved |
| **Safe verification** | `scripts/agent-access/agent-access-doctor.sh` (reports presence and mode 600, never values) |
| **Forbidden** | Never use on production; never print, log or commit the email, password, cookies or tokens; never put the values into a test file, a screenshot, a transcript or memory; never run the setup script for Hafiz; never create a new login-capable staff account by writing rows by hand (role assignment publishes an access event to Ripple, so it goes through the SIMS Staff and Users screens) |

### 40. `ripple-prod-sql-readonly` - Ripple Production Database, Read-Only SQL

| Field | Value |
|-------|-------|
| **Conf file** | None. The route is `ssh staging` (the KVM8 box) as the `postgres` OS account, so no password or connection string is handled |
| **Database** | `ripple_suite_prod`, local PostgreSQL on the KVM8 box (source: ripple-suite `docs/deployment/infrastructure.md`) |
| **Wrapper** | `scripts/agent-access/ripple-prod-sql-readonly.sh "<query>"` (or the query on stdin). Output is CSV by default; `RIPPLE_PROD_SQL_FORMAT=table` for a table |
| **Purpose** | Give agents the same read visibility of Ripple production data that a human operator has, for diagnosis, integrity investigations and release checks, so work does not stall or go blind |
| **Tier** | auto-read |
| **Safety** | The session is forced read-only (`default_transaction_read_only=on`) with a 60 second statement timeout. The wrapper accepts one `select`, `with`, `explain`, `show`, `table` or `values` statement and refuses the ways out of read-only mode and server file reads (`set`, `reset`, `begin`, `commit`, `copy`, `pg_read_file`, `lo_import`, `dblink`, `set_config` and similar). It does not refuse ordinary queries |
| **Safe verification** | `scripts/agent-access/ripple-prod-sql-readonly.sh "SELECT current_setting('transaction_read_only')"` returns `on` |
| **Forbidden** | No writes of any kind from this lane. Production data changes keep the private copy, rehearse and apply method with Hafiz's approval for that exact operation. Do not copy personal data into notes, issues or chat beyond what the task needs; aggregate first |

### 41. `lls-server-readonly` - Learnest (LLS) Server, Read-Only

| Field | Value |
|-------|-------|
| **Conf file** | None. The route is the existing `lls` ssh alias (Learnest box, `/var/www/learnest`, `-staging`, `-develop`), and every command runs as the `www-data` account the app itself uses, never as root. No password or key is handled by the wrapper |
| **Wrapper** | `scripts/agent-access/lls-server-readonly.sh <prod\|staging\|develop> artisan <name> [flags]`, `... logs [lines]` (default 200, max 2000), `... pm2` (queue worker names, status and restart count) |
| **Artisan allow-list** | `about`, `env`, `route:list`, `schedule:list`, `migrate:status`, `queue:failed`; flags `--json --compact --pending --no-ansi --path= --name= --method= --domain=` |
| **Purpose** | Give agents the same read view of the Learnest server that a human operator has: app state, routes, schedule, pending migrations, failed jobs, application log and queue workers. Database reads stay in lane 5 `lls-database-readonly` |
| **Related private file** | `lls-staging-admin.conf` (mode 600): `LLS_STAGING_ADMIN_URL`, `LLS_STAGING_ADMIN_EMAIL`, `LLS_STAGING_ADMIN_PASSWORD`, the Learnest staging admin login for QA. Created 08/10/2026 when the old shared value was rotated; staging only |
| **Tier** | auto-read |
| **Safe verification** | `scripts/agent-access/lls-server-readonly.sh prod artisan about` |
| **Forbidden** | No `tinker`, no `config:show`, no cache, queue, migrate or any writing command, no root. Writes (premium, suspend, refund, cancel) need their own scoped write lane and Hafiz's approval for that exact operation. Do not copy personal data from logs into notes or chat beyond what the task needs |

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
| `healthchecks-readonly` | `healthchecks-readonly.conf` | auto-read | Never |
| `payment-readonly` | `payment-readonly.conf` | auto-read | Never |
| `server-ssh` (reads) | `server-ssh.conf` | auto-read | Never |
| `backup-readonly` | `backup-readonly.conf` | auto-read | Never |
| `wasabi-ripple-storage-scoped` (reads) | `wasabi-ripple-storage-scoped.conf` | auto-read | Never |
| `m365-readonly` | `m365-readonly.env` | auto-read | Never |
| `sharepoint-readonly` | `agent-access/sharepoint-readonly.conf` + private runtime token cache | auto-read after first consent | First login and boundary expansion only |
| `ripple-destination-readonly` | `ripple-destination-readonly.conf` | auto-read | Never for existing scoped reads |
| `typesafe-jev-shadow` | `typesafe-jev.conf` | write | One-time owner activation; automatic bounded shadow calls afterward |
| `ripple-prod-smoke` | `ripple-prod-smoke*.conf` | auto-read | Never for read-only smoke; new role logins need Hafiz to create the account |
| `ripple-staging-smoke` | `ripple-staging-smoke.conf` | write (staging only) | Yes — authenticated mutation scope |
| `sims-staging-browser-qa` | `sims-staging-browser-qa.conf` | write (staging only) | Yes: before cases that change staging data |
| `ripple-prod-sql-readonly` | none (ssh staging as postgres, forced read-only) | auto-read | Never |
| `lls-server-readonly` | none (ssh lls as www-data, allow-listed read commands) | auto-read | Never |
| `betterstack-write` | `betterstack-write.conf` | write | Yes: state source, query and alert |
| `sentry-write` | `sentry-write.conf` | write | Yes: state alert |
| `sentry-issues-write` | `sentry-issues-write.conf` | write | Yes: list the exact short IDs |
| `cloudflare-access-write` | `cloudflare-access-write.conf` | write (reads auto) | Yes: per change to the login gate |
| `status-robot-sender` | `status-robot-sender.conf` | server job | Never for the server job; agents only test the gate |
| `status-notes-claude`, `status-notes-codex` | `status-notes-<agent>.conf` | auto-write (own notes) | Never for a truthful note about the agent's own work |
| `github-status-feed-readonly` | `github-status-feed-readonly.conf` | status page only | Not used by agents |
| `telegram-status-alerts` | `telegram-status-alerts.conf` | status page only | Yes: any send by hand, and any change of `ALERTS_MODE` |
| `healthchecks-write` | `healthchecks-write.conf` | write | Yes: list the exact checks first |
| `monitoring-project-settings` (server changes, probes) | `kelasapp-betterstack-prod.conf`, `lls-sentry-*.conf`, `ripple-sentry.conf` | write | Yes: state exact action; reads and local probes never |
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
| `lls-server-readonly.sh <env> artisan\|logs\|pm2` | Learnest server, allow-listed read commands as the app account (lane 41) |
| `ripple-prod-sql-readonly.sh "<query>"` | Ripple production database, one read-only query, forced read-only session, CSV output (lane 40) |
| `check-ripple-destination-readonly.sh` | Ripple destination lane: exact views and columns, plus read/write boundary checks |
| `ripple-destination-readonly-run.sh` | Runs one command with the narrow destination URL over a temporary SSH tunnel |
| `check-sims-db-readonly.sh` | SIMS DB readonly lane: connection test, row count spot-check |
| `check-runtime-flags.sh sims\|ripple\|finch` | Effective production feature flags, booleans and named modes only; diff two runs before and after a deploy or flag change. `finch` reads only named outreach switches (for example `TUTOR_OUTREACH_AUTOMATIC_ENABLED`) from Finch's production settings file, the value the next Finch (re)start loads, as true/false/unset (last definition wins), plus the control checkout SHA; it discards error text and refuses any other output (#232). For the running process, use Finch's read-only `ProductionTutorOutreachApplyTemplateStatus` operation |
| `check-cloudflare-dns.sh` | DNS records for key domains via CF read-only API |
| `check-app-firewall-blocks.sh [hours]` | Mobile app requests the SIMS production server answered with 403 (the Imunify360 block, sifu-tutor #2438), from Cloudflare analytics: total, by day, by area and by app. Exit 0 when none, 1 when some, 2 when unreadable. Run it first when a parent or tutor "cannot log in" or "cannot pay" from the app |
| `check-cpanel-autossl.sh` | AutoSSL last-run status on production by default; pass `--staging` for WebVoyager |
| `check-monitoring.sh` | Sentry unresolved issues count; BetterStack monitor status |
| `check-microsoft-planner.sh` | Lokka / M365 access availability |
| `check-backups.sh` | Backup storage object count and latest timestamp |
| `check-jev-shadow.py` | Jev credential/SDK readiness and optional non-sensitive live canary |

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
