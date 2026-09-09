# SIMS Owner Analytics — Combined Bundle A Read-Only Preparation Packet

> **SUPERSEDED FOR EXECUTION:** The original Combined A run is complete. Do
> not run this packet again. The only current action is the separately gated
> [`sims-analytics-bundle-a-correction-packet.md`](sims-analytics-bundle-a-correction-packet.md).
> This file remains as the historical contract for evidence already collected.

Status: **HISTORICAL — EXECUTED ONCE, BLUEPRINT SUPERSEDED**  
Parent plan: `docs/sims-analytics-replica-plan.md` v4.1  
Prepared by: Codex  
Future executor: Claude  
Last revised: 13 August 2026

## 1. One continuous preparation bundle

Bundle A is one read-only approval with two internal stages:

- **A1 — facts only:** local repository inventory, production metadata, and
  KVM8 capacity/runtime inventory. It returns no production row values.
- **A2 — complete blueprint:** immediately after A1 passes, Claude converts
  the live facts into the final table/field/extraction/DDL/grant/MCP design. It
  may run only machine-validated `EXPLAIN FORMAT=JSON` statements through the
  same read-only account. It never executes the underlying business SELECT.

Claude does not pause between A1 and A2 unless a stop condition fires. It
returns one complete Bundle A handback for one Codex review. Bundle A does not
authorize a migration, grant, account, tunnel, KVM8 write, installation, data
copy, DNS, secret, token, rollback or later bundle.

## 2. Bundle A objective and highest possible result

A1 proves:

1. the exact current repository revision and repository-discovered schema;
2. the live database identity, version, timezone and schema inventory;
3. live tables, columns, indexes, foreign keys, triggers and approximate size;
4. repository-only and production-only tables;
5. KVM8 CPU, memory, disk, swap, mounts, listening ports, container runtime,
   existing container networks and failed services without inspecting secrets;
6. which facts are still unavailable, especially Hostinger snapshot settings.

A2 then finishes the complete construction blueprint listed in section 9.
Bundle A's highest possible result is “read-only facts and complete blueprint
captured; awaiting Codex review before any construction.”

## 3. Approved identities and boundaries

| Target | Identity/lane | Permitted in Bundle A | Forbidden |
|---|---|---|---|
| Local repository | Current macOS user | Repository reads and protected evidence/blueprint creation outside `.env*` and `live/` | Product-code edits, reading `.env*`, reading `live/` |
| SIMS production MySQL | `database-readonly.conf` / `sims_agent_readonly` | A1 constant/`information_schema` SELECTs; A2 validated `EXPLAIN FORMAT=JSON SELECT ... LIMIT ...` only | Executing business-row SELECT, writes, admin/replication statements, root fallback |
| KVM8 | `server-ssh` read lane, legacy alias `ssh finch` | Host/container/network metadata reads listed below | `sudo`, writes, restart/reload, package install, container changes, secret/config/env inspection |
| Hostinger hPanel | Hafiz manual observation | Snapshot capability/retention/encryption notes only | Any setting change in A1 |

The existing `scripts/agent-access/check-sims-db-readonly.sh` is **not run** in
A1 because it issues a `CREATE TABLE` denial probe. A1 is metadata-only.

## 4. Evidence directory and handling

Claude creates one local evidence directory with restrictive permissions. The
directory contains schema/host metadata only. It must never contain passwords,
tokens, command tracing, MySQL connection strings, production row values, or
KVM8 environment/configuration contents.

Use a timestamped exact directory. Do not overwrite a prior run.

```bash
cd /Users/hafizrazali/Projects/Sifututor
umask 077
BUNDLE_A_RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
BUNDLE_A_EVIDENCE_DIR=".agent-os/evidence/sims-owner-analytics/${BUNDLE_A_RUN_ID}-a1"
mkdir -p "$BUNDLE_A_EVIDENCE_DIR"
chmod 700 "$BUNDLE_A_EVIDENCE_DIR"
printf '%s\n' "$BUNDLE_A_EVIDENCE_DIR"
```

Protected evidence and blueprint files are the only local state changes
authorised by Bundle A. They are planning artifacts, not infrastructure. If
the resolved path is not below
`.agent-os/evidence/sims-owner-analytics/`, stop.

## 5. A1 execution sequence

The canonical executable is
`scripts/agent-access/sims-analytics-bundle-a1.sh`. The blocks below are its
annotated review copy. If the script and this packet differ materially, Claude
stops before execution. Claude must not reconstruct, paste or modify individual
blocks while running A1.

After approval, the only top-level execution command is:

```bash
cd /Users/hafizrazali/Projects/Sifututor
bash scripts/agent-access/sims-analytics-bundle-a1.sh
```

Claude records the script SHA-256 before execution, runs it once, saves its
checkpoint output and reports any stop condition. A stopped section does not
permit manual continuation with later commands.

On success, the canonical script writes the non-secret evidence path to:

```text
.agent-os/evidence/sims-owner-analytics/current-bundle-a-run.txt
```

All A2 commands resolve the run from that file. If it already exists before a
new run, the script stops rather than overwriting or mixing evidence.

### A1.1 Local repository identity and table inventory

Exact commands:

```bash
cd /Users/hafizrazali/Projects/Sifututor

git rev-parse --show-toplevel \
  > "$BUNDLE_A_EVIDENCE_DIR/00-repository-root.txt"
git rev-parse HEAD \
  > "$BUNDLE_A_EVIDENCE_DIR/01-repository-head.txt"
git status --short \
  > "$BUNDLE_A_EVIDENCE_DIR/02-repository-status.txt"

rg -o "Schema::create\\(['\"][A-Za-z0-9_]+" \
  sifu-tutor/database/migrations --glob '*.php' \
  | sed -E "s/.*Schema::create\\(['\"]//" \
  | sort -u \
  > "$BUNDLE_A_EVIDENCE_DIR/03-repository-created-tables.txt"

rg -o "Schema::table\\(['\"][A-Za-z0-9_]+" \
  sifu-tutor/database/migrations --glob '*.php' \
  | sed -E "s/.*Schema::table\\(['\"]//" \
  | sort -u \
  > "$BUNDLE_A_EVIDENCE_DIR/04-repository-altered-tables.txt"

rg -n "protected \\$table|protected \\$fillable|protected function casts|function [A-Za-z0-9_]+\\(" \
  sifu-tutor/app/Models --glob '*.php' \
  > "$BUNDLE_A_EVIDENCE_DIR/05-model-contract-locations.txt"

wc -l \
  "$BUNDLE_A_EVIDENCE_DIR/03-repository-created-tables.txt" \
  "$BUNDLE_A_EVIDENCE_DIR/04-repository-altered-tables.txt" \
  "$BUNDLE_A_EVIDENCE_DIR/05-model-contract-locations.txt" \
  > "$BUNDLE_A_EVIDENCE_DIR/06-repository-inventory-counts.txt"
```

Expected checkpoint:

- repository root is exactly `/Users/hafizrazali/Projects/Sifututor`;
- created-table list contains 108 unique names at the current reviewed state;
- no command touches `.env*` or `live/`;
- dirty Git state is recorded, not changed or cleaned.

Stop if the root differs, the migration command fails, the created-table count
is not 108, or the named plan/catalog files are missing.

### A1.2 Production identity and server facts

This block sources the approved credential file without printing it. It places
the password in a mode-600 temporary MySQL option file rather than the process
argument list. `set -x` is forbidden.

```bash
cd /Users/hafizrazali/Projects/Sifututor
set +x
umask 077

BUNDLE_A_DB_CONF="$HOME/.config/sifututor/agent-access/database-readonly.conf"
test -f "$BUNDLE_A_DB_CONF" || exit 20

# shellcheck disable=SC1090
source "$BUNDLE_A_DB_CONF"

test "$SIMS_DB_READONLY_USERNAME" = "sims_agent_readonly" || exit 21
test "$SIMS_DB_READONLY_DATABASE" = "sifututortutorla_LiveDB" || exit 22

BUNDLE_A_MYSQL_CNF="$(mktemp)"
chmod 600 "$BUNDLE_A_MYSQL_CNF"
trap 'rm -f "$BUNDLE_A_MYSQL_CNF"' EXIT INT TERM

printf '[client]\nhost=%s\nport=%s\nuser=%s\npassword=%s\ndatabase=%s\nssl-mode=REQUIRED\n' \
  "$SIMS_DB_READONLY_HOST" \
  "$SIMS_DB_READONLY_PORT" \
  "$SIMS_DB_READONLY_USERNAME" \
  "$SIMS_DB_READONLY_PASSWORD" \
  "$SIMS_DB_READONLY_DATABASE" \
  > "$BUNDLE_A_MYSQL_CNF"

mysql --defaults-extra-file="$BUNDLE_A_MYSQL_CNF" \
  --batch --raw --connect-timeout=8 \
  --execute="
SELECT
  CURRENT_USER() AS authenticated_identity,
  DATABASE() AS selected_database,
  VERSION() AS mysql_version,
  @@version_comment AS version_comment,
  @@time_zone AS session_time_zone,
  @@system_time_zone AS system_time_zone,
  @@transaction_isolation AS transaction_isolation,
  NOW() AS server_now,
  UTC_TIMESTAMP() AS server_utc_now;
" > "$BUNDLE_A_EVIDENCE_DIR/10-production-identity-and-runtime.tsv"
```

Expected checkpoint:

- authenticated identity contains `sims_agent_readonly`;
- selected database is exactly `sifututortutorla_LiveDB`;
- configured host/port are exactly `151.246.1.164:3306` and the connection
  refuses to fall back to unencrypted MySQL transport (`ssl-mode=REQUIRED`);
- command contains no business table and returns no business row;
- MySQL client produces no warning containing the password.

Stop on any identity/database mismatch, connection failure, TLS/certificate
warning requiring an exception, credential output, or unexpected server.
Never retry with another credential or SSH/root path.

### A1.3 Production schema metadata

The following are the only production SQL statements authorised in A1.

```bash
mysql --defaults-extra-file="$BUNDLE_A_MYSQL_CNF" \
  --batch --raw --connect-timeout=8 \
  --execute="
SELECT
  TABLE_NAME,
  TABLE_TYPE,
  ENGINE,
  TABLE_ROWS,
  DATA_LENGTH,
  INDEX_LENGTH,
  AUTO_INCREMENT,
  CREATE_TIME,
  UPDATE_TIME,
  TABLE_COLLATION
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = DATABASE()
ORDER BY TABLE_NAME;
" > "$BUNDLE_A_EVIDENCE_DIR/11-production-tables.tsv"

mysql --defaults-extra-file="$BUNDLE_A_MYSQL_CNF" \
  --batch --raw --connect-timeout=8 \
  --execute="
SELECT
  TABLE_NAME,
  ORDINAL_POSITION,
  COLUMN_NAME,
  COLUMN_TYPE,
  IS_NULLABLE,
  COLUMN_DEFAULT,
  COLUMN_KEY,
  EXTRA,
  CHARACTER_SET_NAME,
  COLLATION_NAME
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
ORDER BY TABLE_NAME, ORDINAL_POSITION;
" > "$BUNDLE_A_EVIDENCE_DIR/12-production-columns.tsv"

mysql --defaults-extra-file="$BUNDLE_A_MYSQL_CNF" \
  --batch --raw --connect-timeout=8 \
  --execute="
SELECT
  TABLE_NAME,
  INDEX_NAME,
  NON_UNIQUE,
  SEQ_IN_INDEX,
  COLUMN_NAME,
  COLLATION,
  CARDINALITY,
  SUB_PART,
  NULLABLE,
  INDEX_TYPE
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = DATABASE()
ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;
" > "$BUNDLE_A_EVIDENCE_DIR/13-production-indexes.tsv"

mysql --defaults-extra-file="$BUNDLE_A_MYSQL_CNF" \
  --batch --raw --connect-timeout=8 \
  --execute="
SELECT
  k.TABLE_NAME,
  k.CONSTRAINT_NAME,
  k.COLUMN_NAME,
  k.ORDINAL_POSITION,
  k.REFERENCED_TABLE_NAME,
  k.REFERENCED_COLUMN_NAME,
  r.UPDATE_RULE,
  r.DELETE_RULE
FROM information_schema.KEY_COLUMN_USAGE k
LEFT JOIN information_schema.REFERENTIAL_CONSTRAINTS r
  ON r.CONSTRAINT_SCHEMA = k.CONSTRAINT_SCHEMA
 AND r.TABLE_NAME = k.TABLE_NAME
 AND r.CONSTRAINT_NAME = k.CONSTRAINT_NAME
WHERE k.CONSTRAINT_SCHEMA = DATABASE()
ORDER BY k.TABLE_NAME, k.CONSTRAINT_NAME, k.ORDINAL_POSITION;
" > "$BUNDLE_A_EVIDENCE_DIR/14-production-constraints.tsv"

mysql --defaults-extra-file="$BUNDLE_A_MYSQL_CNF" \
  --batch --raw --connect-timeout=8 \
  --execute="
SELECT
  EVENT_OBJECT_TABLE AS TABLE_NAME,
  TRIGGER_NAME,
  EVENT_MANIPULATION,
  ACTION_TIMING
FROM information_schema.TRIGGERS
WHERE TRIGGER_SCHEMA = DATABASE()
ORDER BY EVENT_OBJECT_TABLE, TRIGGER_NAME;
" > "$BUNDLE_A_EVIDENCE_DIR/15-production-trigger-metadata.tsv"
```

Do not add `SHOW CREATE TABLE`, trigger bodies, routines, events, views,
business-table counts, `MIN`, `MAX`, samples, names, contacts, IDs or financial
values during A1. Those are either unnecessary or belong in the exact A2
packet after classification.

Expected checkpoint:

- files contain schema metadata only;
- every table name is unique in the table inventory;
- no output line contains an obvious email, telephone, token or row payload;
- commands complete within the connection timeout without retry loops.

### A1.4 Repository/live table comparison

```bash
tail -n +2 "$BUNDLE_A_EVIDENCE_DIR/11-production-tables.tsv" \
  | cut -f1 \
  | sort -u \
  > "$BUNDLE_A_EVIDENCE_DIR/16-production-table-names.txt"

comm -23 \
  "$BUNDLE_A_EVIDENCE_DIR/03-repository-created-tables.txt" \
  "$BUNDLE_A_EVIDENCE_DIR/16-production-table-names.txt" \
  > "$BUNDLE_A_EVIDENCE_DIR/17-repository-only-tables.txt"

comm -13 \
  "$BUNDLE_A_EVIDENCE_DIR/03-repository-created-tables.txt" \
  "$BUNDLE_A_EVIDENCE_DIR/16-production-table-names.txt" \
  > "$BUNDLE_A_EVIDENCE_DIR/18-production-only-tables.txt"

wc -l \
  "$BUNDLE_A_EVIDENCE_DIR/16-production-table-names.txt" \
  "$BUNDLE_A_EVIDENCE_DIR/17-repository-only-tables.txt" \
  "$BUNDLE_A_EVIDENCE_DIR/18-production-only-tables.txt" \
  > "$BUNDLE_A_EVIDENCE_DIR/19-table-diff-counts.txt"
```

No production-only table is automatically included. No repository-only table
is treated as live. Both lists become explicit `pending` or `exclude` entries
in A2.

### A1.5 KVM8 read-only inventory

The legacy SSH alias is `finch`; evidence and prose name the server KVM8. The
canonical script first proves `ssh -G finch` resolves to `187.127.98.182`. Do
not source or display server config files. Do not use `sudo` if a command is
denied.

```bash
RESOLVED_KVM8_HOST="$(ssh -G finch | awk '$1 == "hostname" { print $2; exit }')"
RESOLVED_KVM8_PORT="$(ssh -G finch | awk '$1 == "port" { print $2; exit }')"
test "$RESOLVED_KVM8_HOST" = "187.127.98.182" || exit 27
printf 'alias=%s\nhost=%s\nport=%s\n' \
  "finch" "$RESOLVED_KVM8_HOST" "$RESOLVED_KVM8_PORT" \
  > "$BUNDLE_A_EVIDENCE_DIR/20-kvm8-ssh-target.txt"

ssh -o BatchMode=yes -o ConnectTimeout=10 finch '
set -eu
printf "section=identity\n"
hostname
uname -srmo
date -Ins
timedatectl show -p Timezone -p NTPSynchronized --value 2>/dev/null || true
printf "section=cpu-memory\n"
nproc
free -b
printf "section=storage\n"
df -B1 -T
findmnt -rno TARGET,SOURCE,FSTYPE,OPTIONS
lsblk -b -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS
printf "section=swap\n"
swapon --show --bytes --noheadings 2>/dev/null || true
printf "section=listening-tcp\n"
ss -lntH
printf "section=failed-services\n"
systemctl --failed --no-pager --plain 2>/dev/null || true
printf "section=container-runtime\n"
docker version --format "client={{.Client.Version}} server={{.Server.Version}}" 2>/dev/null || true
docker info --format "driver={{.Driver}} root={{.DockerRootDir}} containers={{.Containers}} images={{.Images}}" 2>/dev/null || true
printf "section=container-networks\n"
docker network ls --format "{{.ID}} {{.Name}} {{.Driver}}" 2>/dev/null || true
for network_id in $(docker network ls -q 2>/dev/null || true); do
  docker network inspect --format "{{.Name}} {{range .IPAM.Config}}{{.Subnet}} {{end}}" "$network_id" 2>/dev/null || true
done
' > "$BUNDLE_A_EVIDENCE_DIR/21-kvm8-readonly-inventory.txt"
```

The `|| true` clauses prevent an unavailable optional metadata command from
turning into a privilege escalation attempt. Claude records the unavailable
fact; it does not retry with `sudo`, another user or a broader command.

Forbidden KVM8 reads include `docker inspect` of containers, `docker compose
config`, `systemctl cat`, `/proc/*/environ`, shell history, `/etc/prod-env`,
`.env*`, secret mounts, application configuration, database files and logs.

Stop on hostname/IP uncertainty, any output containing a credential/token,
evidence that the alias reaches a different server, or a need for privileged
inspection.

### A1.6 Secret cleanup and local canary scan

First close the MySQL section and delete its exact temporary option file:

```bash
rm -f "$BUNDLE_A_MYSQL_CNF"
trap - EXIT INT TERM
unset SIMS_DB_READONLY_PASSWORD
unset BUNDLE_A_MYSQL_CNF
```

Then scan evidence for obvious secret/PII shapes. This is a defensive canary,
not proof that arbitrary text is safe.

```bash
if rg -n -i \
  'password=|authorization:|bearer[[:space:]]|secret=|token=|-----BEGIN|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' \
  "$BUNDLE_A_EVIDENCE_DIR" \
  > "$BUNDLE_A_EVIDENCE_DIR/22-possible-sensitive-patterns.txt"; then
  chmod 600 "$BUNDLE_A_EVIDENCE_DIR/22-possible-sensitive-patterns.txt"
  printf '%s\n' 'STOP: possible secret or PII in Bundle A1 evidence; do not paste matches into chat' >&2
  exit 30
fi
rm -f "$BUNDLE_A_EVIDENCE_DIR/22-possible-sensitive-patterns.txt"

find "$BUNDLE_A_EVIDENCE_DIR" -type f -exec chmod 600 {} \;
find "$BUNDLE_A_EVIDENCE_DIR" -type d -exec chmod 700 {} \;
```

If the canary fires, Claude reports only the filename and pattern class to
Hafiz/Codex. It does not paste the matching value into chat. Sanitisation or
deletion of material evidence is a new, exact local operation reviewed before
execution.

## 6. A1 stop conditions

Claude stops immediately if:

- current workspace/root or target database differs;
- the authenticated production identity is not `sims_agent_readonly`;
- any command would require root, admin, `sudo`, write SQL or a new tunnel;
- the MySQL client cannot connect safely or emits a credential/TLS warning;
- production output contains real business row values or a secret;
- KVM8 hostname/target identity is uncertain;
- a command needs `.env*`, `live/`, application config, logs or container env;
- the repository table count differs from the expected 108;
- an unexpected command, schema, version or permission suggests the packet is
  stale;
- any optional failure tempts a broader fallback;
- evidence canary detects possible PII/secret content.

There is no retry loop. One reasoned retry is allowed only for a transient
network timeout using the identical command and identity. A second failure
ends A1.

## 7. A1 internal checkpoint

Positive proof:

- exact workspace, repository SHA and dirty state recorded;
- 108 repository migration-created tables recorded;
- production identity/database/version/timezone recorded;
- live table/column/index/constraint/trigger metadata recorded;
- repository/live differences recorded;
- KVM8 capacity/runtime/network metadata recorded;
- evidence canary finds no obvious secret/PII pattern.

Negative proof:

- command transcript contains no business-table SELECT;
- no `INSERT`, `UPDATE`, `DELETE`, `CREATE`, `ALTER`, `DROP`, `TRUNCATE`,
  `GRANT`, `REVOKE`, replication statement, `sudo`, restart/reload/install,
  container change, DNS operation, secret creation or token creation;
- no root/admin fallback occurred;
- no production/KVM8 state changed.

Required internal checkpoint before A2:

```text
Stage: A1 — repository/live-schema/KVM8 read-only facts
Approval sentence received:
Repository root and SHA:
Evidence directory:
Commands actually executed:
Production identity/database confirmed:
Repository table count:
Live table count:
Repository-only table count:
Production-only table count:
KVM8 identity/capacity summary:
Unavailable facts:
Positive proof:
Negative proof:
Possible PII/secret scan result:
Unexpected findings:
Changed state: local evidence directory only | other (STOP)
Rollback: none required; no infrastructure/production state changed
Highest proven state: A1 facts captured
Next action: Continue directly to A2 unless a stop condition fired
```

Claude writes this checkpoint into the evidence directory. It does not send an
intermediate chat handback or wait for approval when all A1 checks pass.

## 8. Exact combined Bundle A approval sentence

Hafiz may authorise the full read-only preparation using this exact sentence:

```text
I approve the combined SIMS Owner Analytics Bundle A exactly as written in
docs/sims-analytics-bundle-a-packet.md. Execute A1 facts gathering and then A2
blueprint preparation continuously. Use only the canonical reviewed scripts,
production information_schema reads and validated EXPLAIN statements as
sims_agent_readonly, plus KVM8 read-only inventory through ssh finch. Create
only protected local evidence and blueprint files. Do not execute business-row
queries, use root/admin/sudo, make any production or KVM8 change, or begin
Track P or Bundles B-H. Return one complete Bundle A handback and stop for
Codex verification.
```

## 9. A2 complete blueprint contract

After A1 passes, Claude creates a `blueprint/` directory inside the same
evidence run. It must produce:

```bash
cd /Users/hafizrazali/Projects/Sifututor
BUNDLE_A_EVIDENCE_DIR="$(cat .agent-os/evidence/sims-owner-analytics/current-bundle-a-run.txt)"
case "$BUNDLE_A_EVIDENCE_DIR" in
  /Users/hafizrazali/Projects/Sifututor/.agent-os/evidence/sims-owner-analytics/*-a1) ;;
  *) exit 40 ;;
esac
test ! -e "$BUNDLE_A_EVIDENCE_DIR/blueprint"
mkdir "$BUNDLE_A_EVIDENCE_DIR/blueprint"
chmod 700 "$BUNDLE_A_EVIDENCE_DIR/blueprint"
```

1. a complete table disposition covering all repository and live tables;
2. the one-row-per-column field matrix required by plan section 4.5;
3. a plain-language owner data dictionary;
4. exact extraction SELECTs with no `SELECT *`;
5. destination DDL with decimal/timezone/null/delete semantics;
6. exact column grants and denied-table/column tests;
7. per-table mode: watermark, bounded full refresh, aggregate, or excluded;
8. exact composite-index requirements based on live indexes;
9. one single-line `EXPLAIN FORMAT=JSON ... LIMIT ...;` statement for each
   proposed extraction query in `query-plans.sql`;
10. KVM8 resource/load model and network-subnet selection;
11. MCP dataset/field/operator/sort/join/metric registry draft;
12. five useful-answer fixtures/tests per dataset;
13. credential/secret/free-text/PII leak tests;
14. revised risks, residuals, O2–O7 decisions and later prerequisites; and
15. exact proposed Bundle B–H packets, each still separately gated.

Required filenames are defined and machine-checked by
`scripts/agent-access/sims-analytics-validate-blueprint.py` and
`docs/sims-analytics-artifact-templates.md`. Table disposition and field matrix
must be CSV files using the exact validator headers.

### A2.1 Query-plan safety

Claude creates `blueprint/query-plans.sql` but may not pass it directly to
MySQL. It must use only:

```bash
cd /Users/hafizrazali/Projects/Sifututor
BUNDLE_A_EVIDENCE_DIR="$(cat .agent-os/evidence/sims-owner-analytics/current-bundle-a-run.txt)"
test -d "$BUNDLE_A_EVIDENCE_DIR/blueprint"
bash scripts/agent-access/sims-analytics-bundle-a-explain.sh \
  "$BUNDLE_A_EVIDENCE_DIR/blueprint/query-plans.sql" \
  "$BUNDLE_A_EVIDENCE_DIR/blueprint/query-plans-output.txt"
```

The helper rejects comments, multiple/multiline statements, unqualified or
qualified wildcards, missing deterministic `ORDER BY`, limits outside 1–5,000,
non-EXPLAIN statements, mutations, file output, sleep/lock operations and
other unsafe tokens. It pins MySQL 8.4, the exact read-only
account/host/database and TLS. If validation fails, Claude stops; it does not
weaken the validator or run MySQL manually.

### A2.2 Blueprint validation

After all artifacts and query-plan output exist:

```bash
cd /Users/hafizrazali/Projects/Sifututor
BUNDLE_A_EVIDENCE_DIR="$(cat .agent-os/evidence/sims-owner-analytics/current-bundle-a-run.txt)"
python3 scripts/agent-access/sims-analytics-validate-blueprint.py \
  "$BUNDLE_A_EVIDENCE_DIR"
```

The validator requires disposition of every repository/live table and exactly
one field-matrix row for every live column. It forces known credential/security
tables and fields to `exclude`, rejects destination/grant data on excluded
fields, rejects missing owner-field contracts, `SELECT *`, database-wide
grants and missing blueprint artifacts.

Claude may correct local blueprint content when validation finds an ordinary
documentation omission. It may make at most one correction pass. Any required
change to a canonical script, policy, security classification or production
query ends Bundle A for review.

### A2.3 Final handback

```text
Bundle: Combined A — read-only facts and complete blueprint
Approval sentence received:
Canonical script hashes:
Repository root and SHA:
Evidence directory:
A1 identity/table/KVM8 summary:
Unavailable facts:
Table-disposition count:
Field-matrix count:
Owner datasets designed:
Excluded credential/security classes:
Query-plan statement count and validator result:
Blueprint validator result:
Track P indexes proposed (not executed):
Bundle B-H packets created (not executed):
Positive proof:
Negative proof:
Possible PII/secret scan result:
Unexpected findings and unresolved owner decisions:
Changed state: protected local evidence/blueprint only | other (STOP)
Rollback: none required; no production/KVM8/infrastructure state changed
Highest proven state: complete blueprint awaiting Codex review
Next action: Codex verifies Bundle A; no construction authorised
```

Claude points to the evidence directory and does not paste metadata, field
matrices or possible sensitive matches into chat. It then stops.

## 10. Hostinger manual facts

Claude cannot infer these from SSH. Hafiz or an approved Hostinger read tool
must provide, without changing settings:

- whether snapshots are whole-VPS;
- whether a path/volume can be excluded;
- encryption at rest and restore-access model;
- snapshot frequency and retention;
- backup destination and deletion controls;
- whether an isolated restore can be tested;
- whether host swap is active/encrypted or can capture sensitive pages.

Unknown is an acceptable Bundle A result and becomes a named blocker for the
relevant later bundle. Guessing or changing hPanel is not allowed.
