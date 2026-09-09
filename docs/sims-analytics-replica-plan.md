# SIMS Owner Analytics on KVM8 — Build-Ready Plan (v4.2)

Status: **ACTIVE BUILD — BUNDLES A/B COMPLETE; HOLD FOR PRODUCTION WRITES**
Owner: Hafiz  
Design reviewer: Codex  
Future executor: Codex or Claude within the currently approved boundary
Last revised: 14 August 2026 (Bundle B completion and C1 preparation)

This document is the execution contract. If a command, table, column, tool,
account, hostname, retention period, rollback, or proof is not specified here
or in an approved appendix, Claude must stop and ask. “Make it work,” “finish
the bundle,” and approval of one bundle never authorize an adjacent action.

### v4.2 progress record

- Bundle A is complete with 101 live-verified query plans and the corrected
  160-table/2,000-field blueprint.
- Bundle B is complete at private repository main commit
  `2287f458c58ffac382d5741faa10e78c80393a2b`; the KVM8 synthetic foundation
  passed full verification with one localhost-only MySQL root account, no
  public port and zero owner/business rows.
- Bundle C1 read-only discovery confirmed the exact tunnel design: KVM8
  loopback `127.0.0.1:13307` to production SSH `151.246.1.164:19199`, then
  production MySQL loopback `127.0.0.1:3306`.
- Production MySQL currently resolves the tunnel's loopback TCP source to
  `localhost`, so the future C2 account is exact `'extract_kvm8'@'localhost'`,
  not KVM8's public IP, literal `127.0.0.1`, or `%`. C2 must prove the actual
  `CURRENT_USER()` through the tunnel and fail closed if name-resolution
  behavior changes.
- The tested local C1 implementation package lives under issue #5 in the
  private analytics repository. It remains uncommitted/unexecuted until
  independent review and an exact production/KVM8 approval.

### v4.1 correction record

v4.1 supersedes the generated v4.0 Combined A blueprint, while preserving its
raw read-only evidence as an audit record. The corrected blueprint is under
`.agent-os/evidence/sims-owner-analytics/20260813T124159Z-a2r1/`.

The correction:

- records the nested `sifu-tutor` repository/ref/SHA as application-schema
  provenance instead of the umbrella workspace SHA;
- reconciles the 52 alleged production-only tables: 44 exist in the locally
  available `sifu-tutor/origin/main`, leaving only eight truly live-only;
- replaces single-page bounded refresh with capped primary-key pagination,
  one consistent source snapshot and one atomic destination publication;
- adds an explicit append-only `id` cursor for repository-proven immutable
  event/log tables;
- fixes the exact consent aggregate, composite key and raw-ID boundary;
- resolves every field classification: useful owner business text, HR
  identifiers, duty-of-care and operational fields are included; raw
  diagnostics/config/payloads, file paths and bank-account labels are
  excluded;
- gives every MCP field a stable `table.field` identifier and compiles exact
  many-to-one joins from live foreign-key evidence;
- adds destination secondary indexes and an exact proposed source-index plan;
- strengthens the validator to reject every defect found in Codex review; and
- treats the B-H document as a forward outline, not an executable packet.

Corrected read-only EXPLAIN evidence is complete: all 101 plans passed the
strict validator. The superseded 80-plan output remains audit history only.

## 0. Plain-language design

SIMS production remains the system staff use to run the business. We will not
let Claude users query that live database.

A background updater will read approved business information from production
and maintain a separate, automatically refreshed business-data copy on the
Hostinger server named **KVM8**. Finch/Finch-Inbox is one project hosted on
KVM8; it is not the server. The existing command `ssh finch` is only a legacy
SSH alias for KVM8.

The first MCP is for **Hafiz and the business-owner partner only**. It reads
the KVM8 copy, never production. It may return real business information,
including names and contact details, because the initial users already have
owner-level business authority. It is read-only: neither Claude nor an MCP
user can change SIMS or the KVM8 copy.

This is a broad **business replica**, not a byte-for-byte clone. Passwords,
sessions, access tokens, reset codes, secrets, raw payment-gateway callbacks,
and other security/system material are never copied. They are unnecessary for
analytics and would turn KVM8 into a complete second breach target.

A future ordinary-staff MCP may be built from the same KVM8 source, but it is
a separate product and approval. Staff must never receive an owner token or
inherit owner-level fields by default.

```text
SIMS production (HostArmada)
        |
        | approved read-only business columns only
        v
KVM8 updater ----> KVM8 owner business database
                         |
                         | internal read-only DB account
                         v
                  Owner Analytics MCP
                         |
                         v
                 Hafiz + owner partner

Future, separate approval:
KVM8 owner business database -> cleaned staff datasets -> Staff MCP
```

## 1. Binding decisions

These decisions are confirmed unless Hafiz explicitly changes them in a later
revision.

| ID | Decision | Implementation meaning |
|---|---|---|
| D1 | Production is never the interactive analytics target | MCP has no production hostname, credential, tunnel, or code path |
| D2 | The automatically refreshed copy lives on KVM8 | All owner queries execute against KVM8 |
| D3 | KVM8 is the server name | “Finch” may refer only to the project or the legacy `ssh finch` alias |
| D4 | Launch is owner-first | Initial tokens may be issued only to Hafiz and the named owner partner |
| D5 | Owners receive broad business data | Real names, business identifiers, contact details, exact operational dates, statuses, amounts, and relationships may be available where catalogued |
| D6 | Copy only useful business data | Credential, secret, authentication, raw security, and irrelevant framework/system data are excluded at the production grant boundary |
| D7 | Read-only analytics | MCP cannot write; its DB account cannot write; no mutation tools exist |
| D8 | Automatic updates use restricted SELECT polling | No native GTID replica, binlog privilege, broad DB clone, or `mysqldump` |
| D9 | One approval bundle at a time | Every production write, KVM8 write, DNS write, secret issuance, token issuance, and destructive rollback has its own pause |
| D10 | v1 is analytics, not disaster recovery | No failover, promotion, application cutover, or production restore claim |
| D11 | Logs are root-only for four weeks | Logs record identity and operation shape, never returned values or result rows |
| D12 | Future staff access is separate | No staff recipient, sanitisation rule, or staff token is part of owner v1 |

### 1.1 Decisions not silently overridden

Earlier drafts contained rules for a cleaned ordinary-staff surface, including
pseudonyms and month buckets. Those rules remain useful for a future staff
product, but they do **not** describe the owner MCP. Claude must not remove
owner-useful fields merely because an older section or memory discussed staff.

Hafiz has confirmed that the owner MCP may return individual tutor earnings,
tutor payment/payout details, and individual staff salary, payroll and
commission records. These are owner-authorised business records, not a reason
to copy bank authentication details, credentials, proofs/files or secrets.
This approval applies only to the two owner identities; future staff access
remains separately cleaned and authorised. See O1 in section 15.

## 2. Scope and non-goals

### 2.1 In scope for owner v1

- A production read-only extractor identity restricted to an exact business
  column allowlist.
- A KVM8 MySQL database containing the approved owner business replica.
- Initial backfill plus incremental refresh and reconciliation.
- A structured MCP that lets owners discover datasets, inspect fields, search
  records, retrieve paginated rows, aggregate, and check freshness.
- Per-owner tokens, revocation, audit records, monitoring, backups, incident
  response, and teardown instructions.
- Repository and live-schema evidence proving that each copied field has an
  owner use and each excluded security field is unreachable.

### 2.2 Explicitly out of scope

- Connecting the MCP directly to production.
- Giving owners or staff SSH, MySQL, updater, production, or server secrets.
- Arbitrary production SQL, write SQL, stored procedures, or database admin.
- Native MySQL GTID/binlog replication.
- A byte-for-byte clone, credential tables, security tables, or framework
  operational tables with no analytics purpose.
- A disaster-recovery standby, failover, promotion, or application cutover.
- Ordinary-staff onboarding or owner-to-staff token sharing.
- Changing SIMS business behavior except the separately reviewed source-index
  migrations required for safe extraction.
- Copying files, uploads, identity documents, proof images, or media objects.

## 3. Sources of truth and precedence

Implementation must use the following authority order:

1. Hafiz's latest explicit decision in the current review.
2. This v4 plan and its approved version-controlled appendices.
3. [`sims-analytics-data-catalog.md`](sims-analytics-data-catalog.md) for
   dataset and field classification.
4. Live read-only `SHOW CREATE TABLE`, `DESCRIBE`, index, size, and query-plan
   evidence gathered in Bundle A.
5. The nested `/Users/hafizrazali/Projects/Sifututor/sifu-tutor` repository at
   an explicitly recorded reviewed ref and SHA. The umbrella workspace SHA is
   not SIMS application-schema provenance.
6. Historical drafts and Koda memories only as background.

Before comparison, the executor records the nested repository path, current
branch/status, selected authoritative ref and resolved SHA. A stale feature
branch must never be treated as the current migration catalog. If live schema
still differs from that recorded source, Bundle A records the difference and
this plan/catalog must be revised before any grant or copy. Claude must not
guess which is correct.

### 3.1 Required version-controlled artifact set

The approved implementation home is the dedicated private GitHub repository
`Sifututor/sims-owner-analytics` (O7). Bundle B creates its reviewed initial
commit and records its exact SHA before transferring the same commit to KVM8.
Chat output, files under `/tmp`, or an uncommitted KVM8-only copy do not count.
The repository must contain these stable artifacts as the relevant bundles are
implemented:

```text
README.md                         # plain-language architecture and local proof
docs/table-disposition.md         # every discovered source table
docs/field-matrix.md              # every candidate source column
docs/data-dictionary.md           # owner-facing dataset/field meaning
docs/risk-register.md             # current mitigations and accepted residuals
docs/decisions.md                 # D1-D12, O1-O7 and later owner decisions
docs/bundles/A.md ... H.md        # packets, approval, evidence and handback
docs/runbooks/                    # operation/recovery/incident/teardown
grants/extractor.sql              # exact allowlisted source grants
grants/extractor-denials.sql      # excluded/pending negative tests
schema/owner-analytics.sql        # destination DDL
extractor/                        # reviewed updater and tests
mcp/                              # policy adapter, registry and tests
deploy/                           # pinned compose/service/proxy definitions
fixtures/                         # synthetic only; no copied production rows
```

Secret files, real data, command output containing personal data, and generated
backups are forbidden in this repository. Every bundle handback links to the
exact committed artifact version it executed; Claude must not run commands
from an unrecorded chat-only draft.

## 4. Data contract

### 4.1 Default inclusion rule

A field may enter the owner replica only when all are true:

1. it answers a named owner/business question or joins two useful datasets;
2. the exact live column exists and its meaning is verified;
3. its extraction mode, destination type, null handling, deletion behavior,
   reconciliation, and leak tests are written in the approved field matrix;
4. the production extractor grant names that exact column; and
5. the KVM8 MCP registry names whether it is searchable, filterable,
   sortable, aggregatable, or returnable.

“Copy the whole table,” `SELECT *`, and table-level `database.*` grants are
forbidden even for tables believed to be safe.

### 4.2 Owner-allowed classes

Subject to the catalog, owner v1 may include:

- real student, parent, tutor, and staff names;
- SIMS business IDs and human-facing request/invoice/class/report references;
- email, telephone, WhatsApp, business address, city, state, and postcode;
- exact operational dates and times where useful;
- statuses, categories, types, flags, outcomes, and lifecycle history;
- amounts, balances, rates, hours, counts, durations, and approved finance
  relationships;
- individual tutor earnings, invoices, payments, additions, deductions,
  bonuses and commissions, plus individual staff salary, payroll and
  commission business records;
- classes, attendance, tutor requests, matching, invoices, payments, refunds,
  reports, support/follow-up, and reference/master data;
- operational free text only when specifically classified as useful and tested
  for embedded secrets; there is no blanket free-text grant.

### 4.3 Never-copy classes

These are excluded from production grants, extraction SQL, KVM8 tables,
backups, MCP fields, logs, fixtures, and error messages:

- password and `plain_password` fields;
- remember tokens, sessions, personal/API access tokens, OAuth secrets;
- password-reset, email/phone verification, OTP, and recovery codes;
- private keys, encryption keys, webhook secrets, environment values;
- raw payment-gateway callbacks, signatures, hashes, and credentials;
- raw device tokens and notification credentials;
- bank account credentials or payout authentication material;
- framework/cache/queue/job/debug/pulse/telescope/system tables unless a
  separately approved operational dataset proves a business purpose;
- raw files, uploads, ID documents, profile images, payment proofs, and paths
  that could grant object access;
- raw stack traces and payloads that may contain credentials or personal data.

At minimum, the source account must have no privileges on `users`, `sessions`,
`password_reset_tokens`, `personal_access_tokens`, or
`verification_codes`. Bundle A must discover equivalent or renamed tables and
columns rather than treating this example list as exhaustive.

### 4.4 No hidden transformation promise

Owner rows are not pseudonymised unless a field-specific catalog rule says so.
The KVM8 copy therefore contains personal data and must be protected as a
sensitive business system. This is deliberate and must not be described as a
“PII-safe replica.”

The future staff product will need its own transformation contract. Its
pseudonyms, date buckets, minimum cohort sizes, and free-text removal must be
derived from the owner copy into separate staff tables or views; they must not
weaken owner v1 or expose owner tables to staff.

### 4.5 Required field-matrix artifact

Before Bundle C, Claude must produce a version-controlled CSV or Markdown
matrix with one row per source column:

```text
source_table
source_column
live_type
business_meaning
owner_question
classification: owner-allow | aggregate-only | exclude | pending
destination_dataset
destination_field
destination_type
extract_mode
cursor_dependency
nullable/default behavior
soft/hard-delete behavior
MCP capabilities
production_grant
leak-test ID
approval decision/reference
```

No row may be marked `owner-allow` merely because its name looks harmless.
Every literal source table discovered in the repository must appear in the
table disposition, including `exclude` rows.

## 5. Production least privilege

### 5.1 Identities

- Bundle A discovery uses only the existing approved read-only lane
  `sims_agent_readonly`. It has no root fallback.
- The updater receives a new MySQL identity, planned name `extract_kvm8`.
- Host scope is the exact tunnel/source address proven in Bundle C, never `%`.
- It receives `SELECT` only on the exact approved columns plus the minimum
  metadata access proven necessary.
- It receives no `INSERT`, `UPDATE`, `DELETE`, `CREATE`, `ALTER`, `DROP`,
  `FILE`, `PROCESS`, `SUPER`, `REPLICATION`, routine, trigger, event, or grant
  privilege.
- Apply conservative connection/query limits after Bundle A measures the
  required workload.

### 5.2 Grant compilation, not handwritten improvisation

The field matrix is compiled into an exact grant artifact. Before application,
Claude must prove both directions:

- every allowed extraction column has the intended grant; and
- every excluded/pending column and table fails when queried as
  `extract_kvm8`.

The grant artifact, denial-test list, `SHOW GRANTS` expected output, exact
apply command, exact verification command, and exact rollback statements are
presented at the Bundle C pause. A later schema change causes extraction to
pause; it does not inherit access automatically.

### 5.3 Network path

The updater runs on KVM8 and reaches production through a dedicated outbound
SSH tunnel with a restricted key. The production-side key must:

- permit forwarding only to the verified MySQL target/port;
- forbid shell, PTY, agent forwarding, X11 forwarding, user rc, and unrelated
  local/remote forwarding;
- use an account whose shell and file permissions are independently checked;
- be negative-tested for shell, TTY, `-R`, and other-port denial.

MySQL `SOURCE_SSL=0` no longer applies because native replication is not used.
If the MySQL client connection inside the SSH tunnel does not use TLS, the plan
must state accurately that SSH protects the network hop while MySQL itself is
plaintext inside that tunnel. Bundle A/C must verify no unencrypted segment
exists outside the local tunnel endpoints. Prefer MySQL TLS as defense in
depth when the production server supports a verifiable certificate without
adding unsafe certificate exceptions.

## 6. Extraction and refresh correctness

### 6.0 Real entry points and state transitions

The updater's only automatic entry point is a named systemd timer invoking one
version-controlled command. Manual runs invoke the same command with an
explicit table/slice and dry-run or apply mode; there is no second extraction
implementation.

For each dataset, the lifecycle is:

```text
unbuilt -> synthetic-tested -> backfilling -> reconciling -> unpublished-ready
       -> published-current -> stale-or-paused -> reconciled -> published-current
```

Only a successful destination transaction changes copied rows/cursor state.
Only successful required reconciliation changes publication from unpublished
or paused to current. A process exit, partial page, alert acknowledgement, or
manual database edit never publishes data.

The MCP's only public entry point is the approved HTTPS route. Authentication
and authorization complete before dataset lookup or DB checkout. The response
is committed to the caller only after its row/byte limits and audit metadata
have been computed; audit failure behavior must be decided and tested before G
so requests are not ambiguously half-recorded.

### 6.1 Why SELECT polling is retained

Native GTID replication would copy whole rows/tables and requires broad
replication privileges. It cannot enforce the field-level never-copy boundary.
The updater therefore executes fixed, reviewed SELECT statements and writes
only their approved output to KVM8.

`mysqldump`, `mysqlpump`, physical snapshots, ad hoc export files, and
`SELECT *` are forbidden for the initial copy and later refreshes.

### 6.2 Per-table modes

Every dataset receives one explicit mode:

1. **Watermark incremental:** large tables with a reliable `(updated_at,id)`
   cursor and an approved composite index.
2. **Append-only incremental:** a repository- and test-proven immutable table
   uses `id > ? ORDER BY id LIMIT ?`; L2/L3 still detect hard deletes or an
   unexpected update to an earlier ID.
3. **Bounded full refresh:** a small table uses one REPEATABLE READ consistent
   source snapshot, exact count/byte caps, primary-key pagination and one
   complete destination transaction. A page limit is never a table limit.
4. **Derived aggregate refresh:** approved aggregate-only data recomputed for
   a bounded time window and atomically replaced.
5. **Excluded:** never queried.

There is no undocumented “best effort” mode. Tables without a safe mode remain
unavailable.

For every bounded full refresh, the contract records an explicit maximum row
count and transformed-byte count. The updater checks the exact source count
inside the consistent snapshot, pages until that count is collected, rejects
duplicates/gaps, and then performs `DELETE + complete INSERT` in one KVM8
transaction. Crossing a cap pauses the dataset for reclassification; it never
publishes the first 5,000 rows as if they were complete.

### 6.3 Incremental algorithm

For a watermark table, persist a composite cursor `(watermark_updated_at,
watermark_id)` in root-only pipeline metadata.

Each run:

1. Acquire a per-table lock. Refuse overlapping runs.
2. Read the last committed cursor.
3. Query a fixed-size page using:
   `(updated_at > ?) OR (updated_at = ? AND id > ?)` ordered by
   `updated_at,id`.
4. Transform and validate the complete page in memory.
5. In one KVM8 transaction, upsert approved rows and advance the cursor only
   after all rows succeed.
6. Commit. On any failure, roll back both rows and cursor.
7. Pace pages and stop at the approved run-time/query budget.

If a run crashes after reading but before commit, it replays the same page.
Upserts must be idempotent. Poison rows cause the table to pause and alert;
they are never silently skipped.

### 6.4 Deletes and timestamp-bypassing writes

Repository history already proves some writes can bypass normal timestamp
updates. Therefore watermark polling alone is insufficient.

Mandatory reconciliation:

- **L1 daily:** source/destination counts and safe aggregates by bounded
  partition; mismatch pauses affected publication and alerts.
- **L2 weekly:** complete run-scoped source identity sweep per included table;
  hard-delete KVM8-only rows only after the source sweep completes
  successfully. Partial sweeps never delete.
- **L3 monthly, after production data surgery, and once before go-live:**
  chunked full-content digests using approved columns and stable canonical
  encoding. Mismatch is investigated and repaired before access resumes.

Soft-deleted source rows remain represented with an explicit deletion flag
where business analysis needs history. Each table must document whether a
hard source delete removes or tombstones the KVM8 row.

### 6.5 Source indexes are a separate critical track

No target production table was assumed to have the needed `updated_at` index.
Bundle A must prove every live query plan. Required composite
`(updated_at,id)` indexes are application migrations in separate Track P:

- repository migration and rollback;
- staging-size rehearsal and query-plan evidence;
- production migration approval;
- production execution and verification;
- post-migration query-plan rerun.

Bundle D cannot start until every required index is live and verified. No
offset pagination, unindexed polling, or large interim full scan is allowed.

The exact proposal is compiled into `blueprint/source-index-plan.csv`. It
records table, cursor columns, current estimated rows/bytes, existing-index
result, proposed DDL, rollback DDL, approval slice and required proof. Large
tables receive one approval slice each; a small-table slice may contain at
most five indexes. A CSV row is a proposal, not migration authority: Track P
still requires Laravel migrations, focused migration tests, representative
staging rehearsal, before/after EXPLAIN, online-DDL/lock/disk observation and
fresh per-slice production approval.

### 6.6 Initial backfill

Initial backfill uses the same allowlisted extraction code as steady state.
For each table:

1. record source count/range and query plan;
2. copy in bounded, paced pages;
3. record page counts, rejects, duration, and final cursor without values;
4. run a second incremental catch-up;
5. run L1, L2, and full L3;
6. keep the dataset unpublished until all checks pass.

The window is chosen from Bundle A load evidence. The prior suggested
02:00–06:00 MYT window is not automatically approved.

## 7. KVM8 data plane

### 7.1 Separation

- Dedicated database/schema and service network for SIMS owner analytics.
- Database port is never public and is not bound to the host's public
  interface.
- Updater has write privileges only on destination business tables and
  pipeline metadata required for its own job.
- MCP account `mcp_owner_reader` has SELECT only on approved owner datasets;
  it cannot read pipeline metadata or write anything.
- No other KVM8 project receives database, volume, network, or secret access.
- Finch-Inbox, SIMS staging, Ripple, and other KVM8 workloads must not share
  credentials or container namespaces with this service.

### 7.2 Sensitive-data protections

Because KVM8 will contain real PII:

- root/host access remains limited to Hafiz's existing infrastructure lane;
- database and service secrets are generated directly into root-readable
  files, never printed, pasted into chat, committed, or placed in command
  history;
- images are pinned by digest/version and run as non-root with read-only root
  filesystems, minimal capabilities, bounded resources, and tmpfs scratch;
- MySQL general query logging stays off;
- application logs, core dumps, swap, backups, snapshots, support bundles,
  and crash reports are checked for personal-data leakage;
- disk/snapshot/backup encryption and restoration access are recorded before
  real data arrives;
- provider whole-VPS snapshots are an explicit owner decision because KVM8
  hosts multiple projects. Do not disable shared-server recovery blindly.

### 7.3 Publish safely

Datasets are unpublished while backfilling or reconciling. Incremental page
upserts are transactional. Bounded full-refresh/aggregate datasets replace
their contents in one transaction so the MCP sees the old complete version or
the new complete version, never an empty or partial surface.

Every dataset exposes freshness and last-success state. A stale/paused dataset
returns a clear availability error; the MCP must not present stale data as
current without stating the timestamp.

### 7.4 Destination query indexes

Destination DDL includes secondary indexes for the exact extraction cursor,
approved relationship IDs, status/time filtering and created-time pagination.
The MCP implementation must run its registry-generated SQL against synthetic
fixtures at realistic row volumes and record EXPLAIN plans for the largest
datasets, including `user_logs`, `notification_logs`, `classes`,
`student_reports`, invoices and payments. An owner query that full-scans a
large table is not enabled merely because the SQL is correct; the registry or
DDL is corrected first.

## 8. Owner MCP contract

### 8.1 Product behavior

The owner connects Claude to one HTTPS MCP endpoint using a personal bearer
token. The MCP exposes broad approved business data from KVM8 and supports:

- `list_datasets()`;
- `describe_dataset(dataset)`;
- `data_freshness(dataset?)`;
- `search_records(dataset, query, fields, filters, limit, page_cursor)`;
- `rows(dataset, fields, filters, order, limit, page_cursor)`; and
- `aggregate(dataset, dimensions, metrics, filters, date_range, limit)`.

The exact input/output JSON schemas, allowed datasets, fields, operators,
sorts, joins, metrics, null behavior, pagination semantics, and example calls
must be version-controlled before Bundle G.

Every client-visible field has a globally unambiguous registry identifier in
`table.field` form (for example `classes.id` and
`class_attendance_logs.id`). A bare repeated name such as `id`, `status`,
`amount` or `created_at` is never accepted. These are logical registry IDs,
not client SQL identifiers.

Allowed joins are compiled in `mcp-joins.csv` from verified live foreign keys.
v1 permits only named child-to-parent many-to-one joins. A rows call preserves
exactly one result row per base child row. Reverse one-to-many traversal is a
separate query, not an implicit join. For aggregate calls, metrics come from
the child/base table and parent fields may only be dimensions; this prevents a
join from multiplying an invoice, payment or salary total. Unknown, reversed
or unregistered joins fail uniformly.

There is no generic `query(sql)` tool and no client-provided SQL fragment,
function, expression, table name, join, or comment. The service constructs
parameterized SQL from a reviewed registry. This gives owners broad data
access without turning a Claude prompt into a database console.

Response/page caps protect KVM8 and Claude context; they are not hidden data
filters. A valid opaque cursor lets the owner continue. Bulk export is not a
v1 tool unless Hafiz separately approves its format, storage, expiry, and
audit behavior.

### 8.2 Identity and authorization

- Initial recipient registry contains Hafiz and the named owner partner only.
- Each person gets a separate high-entropy token with identity, purpose,
  scope, issue date, expiry, and revocation state.
- Token values are delivered through Hafiz's password manager and stored only
  as hashes in the root-managed registry.
- Tokens are never shared between people or reused for staff.
- Authorization is checked on every request and every page.
- Issuance, rotation, expiry, and revocation have tested admin commands and
  atomic registry reload behavior.
- A future staff identity has no access until a separate staff MCP/scope and
  cleaned datasets are reviewed and approved.

### 8.3 Transport and service safety

- HTTPS only through an approved hostname, reverse proxy, and DNS record.
- Exact Host/Origin/method/content-type allowlists.
- Body-size, nesting-depth, row, response-byte, time, rate, pool, global
  concurrency, and per-token concurrency limits.
- Every request uses isolated identity/request/response/transport state. No
  mutable cross-user global state.
- Timeouts cancel database work; errors never expose SQL, driver details,
  stack traces, secrets, or record values.
- Every returned free-text field is registry-marked
  `content_trust=untrusted_business_data` and remains a JSON string inside the
  tool result; it is never concatenated into server prompts, SQL, tool
  descriptions, logs or control messages. Tests include stored prompt-like
  instructions, HTML/Markdown, delimiter text and secret-shaped canaries and
  prove they cannot invoke another tool, change authorization or escape the
  result field.
- Official maintained MCP server/transport packages are used and lockfile
  pinned. Claude must not invent a custom HTTP/JSON-RPC transport. A thin
  custom policy/data adapter is expected.
- Package choice and security advisories are re-verified at implementation
  time; this design does not freeze a stale version from an earlier draft.

### 8.4 Audit

Root-only audit records are retained four weeks and contain:

- timestamp, token/owner identity, tool and dataset;
- selected field/metric/operator names;
- returned row/count/byte totals, duration, status, and error class.

They never contain SQL text, filter/search values, result rows, contact
details, names, tokens, or secrets. This is deliberate: attribution remains
possible without creating another PII database in logs.

Audit is fail-closed for owner requests. The service writes a sanitized
request-start record before database checkout and a sanitized completion/error
record before returning the response. If the audit destination is unavailable
at either point, the request returns a uniform temporary-unavailable error and
does not return data. Bundle G must prove this behavior and prove that recovery
does not replay or duplicate a previously returned page.

## 9. Dataset completeness

The companion catalog is the data-product authority. Before owner launch it
must cover, at minimum:

- students, parents, tutors, staff and owner-relevant organisation data;
- tutor services, subjects, curricula, languages, availability and education;
- tutor emergency contacts for owner duty-of-care and declaration-completion
  records without raw declaration text;
- tutor requests, students, addresses, activities, broadcasts, matches,
  reassignments and level changes;
- classes, attendance and related billing links;
- class lifecycle events and structured session engagement records (raw notes
  and concerns excluded by default);
- parent invoices, payment attempts/items, fees, deductions, adjustments,
  transfers, commitment-fee attempts and refunds;
- individual and aggregate tutor finance and staff finance, excluding bank/
  payout authentication data, credentials, secrets and proofs/files;
- tutor commitment-fee attempts/offline-review outcomes, onboarding-hour
  exclusions, referral rewards and reward allocations;
- tutor onboarding cases/events, request creation attribution, request owner
  state, verification exceptions, amendments and stale-request outcomes;
- expected/student reports and useful answer categories;
- follow-up cases, tickets and app issue reports;
- structured notification-delivery and request-sharing funnel events, while
  raw callbacks, provider errors, metadata payloads and free text remain
  excluded;
- safe master/reference data used to explain codes and relationships.

Each dataset needs five useful-answer examples written from the owner's point
of view, including at least one detailed row lookup, one relationship/join,
one aggregate, one date-range query, and one empty/error case. Claude must run
these against synthetic fixtures before real data.

“All useful data” means complete catalog coverage, not copying every source
column. Tables with no owner analytics use are explicitly dispositioned as
excluded so their absence is visible and reviewable.

## 10. Monitoring and operations

Monitoring exists before owner access:

- updater success/failure and run duration;
- per-dataset freshness, cursor age, paused state, row/count variance;
- L1/L2/L3 reconciliation state;
- tunnel and database health;
- disk usage thresholds and projected growth;
- container restart/health, memory and CPU limits;
- certificate expiry and endpoint health;
- failed authentication, rate-limit, timeout, and server-error counts;
- backup success and a tested restore into an isolated empty destination.

Alerts contain only dataset names, counters, durations and error classes. No
record values are sent to BetterStack or another monitoring provider.

The 48-hour clean-running gate begins only after backfill, reconciliation,
monitoring, and alert-delivery tests pass. Owner tokens are not issued during
that gate.

KVM8 host reboot is not a routine resilience test because the server hosts
multiple projects. Any reboot requires its own owner-approved maintenance
window. Container/tunnel/process restart drills may occur within their bundle.

## 11. Backup, recovery, incident response, and teardown

### 11.1 Backup/recovery

- The approved analytics backup is a daily logical MySQL backup, encrypted on
  KVM8 before upload to a dedicated SIMS-owner-analytics Wasabi bucket/prefix,
  retained for 30 days. Hostinger snapshots are optional additional recovery
  coverage and are never the required analytics backup.
- The analytics backup target and credentials are separate from the SIMS
  production-backup pipeline. Bundle B must not reuse or weaken any existing
  production bucket, key, retention rule, lifecycle rule, or Object Lock rule.
- KVM8 receives only a narrowly scoped deposit credential that can create new
  analytics backup objects at the approved prefix. It must not list, read,
  overwrite, or delete backups. Restore uses a separate, temporary read
  credential supplied only for an approved restore operation.
- Every backup is written to a unique, non-overwriting object name and is
  client-side encrypted. The private decryption key must not reside on KVM8,
  in GitHub, in container images, or in logs/evidence.
- Remote Wasabi provisioning is a separately approved write operation. Bundle
  B may document and prepare the disabled local backup contract, but may not
  create a bucket, credential, lifecycle rule, Object Lock rule, timer, or
  backup object unless the packet explicitly enumerates and approves it.
- Before real data is copied, an encrypted synthetic backup must be restored
  into an isolated empty destination. Proof verifies decryption, schema and
  row counts, least privilege, retention configuration, and absence of public
  exposure. The first real-data backfill is blocked until this succeeds.
- Retention is exactly 30 days for this analytics workload. Deletion after the
  retention period is performed by the reviewed remote retention mechanism,
  not by a broad delete credential stored on KVM8.

### 11.2 Incident response

Runbook must cover suspected token leak, owner-account compromise, MCP bug,
KVM8 host compromise, leaked backup, production grant widening, schema drift,
and incorrect analytics data. The default response is:

1. disable/revoke the affected surface;
2. preserve root-only metadata without copying PII into tickets/chat;
3. identify affected period/datasets/identities;
4. rotate relevant tokens/credentials;
5. repair and re-run security/reconciliation tests;
6. obtain Hafiz approval before re-enabling.

### 11.3 Teardown

Teardown is destructive and separately approved. The runbook inventories and
removes, in order: owner tokens, DNS/proxy exposure, MCP, timers, updater,
production DB grants/user, tunnel key, KVM8 schemas/volumes, backups/snapshots,
and retained logs according to policy. Every target is resolved explicitly;
no broad `rm -rf`, wildcard user drop, or shared-volume deletion.

## 12. Claude execution protocol — mandatory

This section exists because prior builds acknowledged findings but still left
room for unsafe interpretation.

### 12.1 Before every bundle

Claude must create a bundle packet containing:

1. goal and exact approved scope;
2. preconditions and evidence that they are true;
3. files/hosts/accounts/tables/columns affected;
4. exact commands or version-controlled scripts;
5. expected output with secrets and PII redacted;
6. positive verification;
7. negative verification proving forbidden access/action fails;
8. failure stop conditions;
9. rollback and whether rollback is read, write, critical, or destructive;
10. artifacts that will be handed back;
11. the exact approval sentence requested from Hafiz.

Claude stops after presenting the packet. Discussion, edits to the packet, or
approval of a different bundle do not authorize execution.

### 12.2 During every bundle

- Execute only commands shown in the approved packet.
- Never replace a failed scoped identity with root/admin.
- Never broaden a grant, firewall rule, hostname, table list, or command to
  “get past” a failure.
- Never print secrets or real row values as evidence.
- Stop on unexpected output, version, host, schema, row volume, query plan,
  permission, or existing configuration.
- Do not execute rollback automatically unless it is non-destructive and was
  explicitly included in the same approval. Critical/destructive rollback
  requires fresh approval.

### 12.3 After every bundle

Claude returns one handback with:

```text
Bundle:
Approved operation:
Actually executed:
Changed state:
Positive proof:
Negative proof:
Unexpected findings:
Rollback status:
Secrets/PII handling confirmation:
Highest proven state:
Next bundle (not authorized):
```

No next-bundle command is run. A successful shell exit without the complete
handback is not a completed bundle.

### 12.4 Small vertical slices

Claude should not attempt the entire project in one silent run. Within an
approved bundle it must checkpoint after each bounded slice (for example one
table family, one container, or one test group), save partial evidence before
slow tests, and make at most one reasoned recovery attempt after a failure.
Repeated loops or “try until green” are forbidden.

## 13. Approval bundles

Every bundle starts in HOLD and ends at a new pause.

### Bundle A — Read-only discovery and exact design artifacts

Bundle A is one continuous read-only preparation approval with two internal
stages because exact query shapes cannot be known until A1 proves the live
schema:

- **A1 — facts only:** repository inventory, production `information_schema`
  metadata and KVM8 capacity/runtime inventory. It runs no business-row query
  or `EXPLAIN`.
- **A2 — exact blueprint:** after A1 passes its automatic stop checks, Claude
  immediately creates the complete table/field/grant/DDL/MCP design and may
  run only validated `EXPLAIN FORMAT=JSON` statements through the same
  read-only identity. It executes no business-row SELECT.

The executable A1 packet and A2 preparation contract are in
[`sims-analytics-bundle-a-packet.md`](sims-analytics-bundle-a-packet.md).
The future executor reads
[`sims-analytics-claude-handoff.md`](sims-analytics-claude-handoff.md); Codex
reviews each handback with
[`sims-analytics-codex-verification-checklist.md`](sims-analytics-codex-verification-checklist.md).

Allowed after the single explicit Bundle A approval:

- repository reads;
- production schema/index/size/query-plan reads using
  `sims_agent_readonly` only;
- KVM8 read-only capacity/network/runtime inventory using the approved SSH
  lane;
- Hostinger snapshot facts recorded by Hafiz when no agent read lane exists.

A1 deliverables: live schema metadata, repository/live table differences and
KVM8 read-only capacity/runtime evidence. A2 deliverables: complete table
disposition, field matrix, exact query plans, data-volume/load model, approved
snapshot/swap facts, source SQL, destination DDL, grants/denial tests, MCP
registry draft, and revised risk/decision table. No writes. Claude stops after
the full Bundle A handback for one Codex review. Bundle A never authorizes
Track P or Bundles B–H.

The first Combined A run gathered valid live/KVM8 facts but its generated
blueprint used the umbrella repository SHA and a stale nested working branch.
Codex generated corrected revision
`.agent-os/evidence/sims-owner-analytics/20260813T124159Z-a2r1/` from the
existing evidence and the explicitly recorded nested `sifu-tutor/origin/main`
ref. Local structural validation passes. The old query-plan output is
superseded because the corrected blueprint contains 101 included tables rather
than 80. The only remaining Bundle A action is the separately approved
read-only EXPLAIN correction packet; it makes no KVM8 contact and no state
change beyond protected local evidence.

### Track P — Production source indexes

Separate critical application-migration lane. One or more approved migrations
may add only the composite indexes proven necessary by A. Requires its own
repo plan, staging rehearsal, production approval, migration, verification,
and rollback. It is not implied by A or C.

`blueprint/source-index-plan.csv` is design input, not an executable packet.
Track P must be split as described in section 6.5 and each exact migration
packet reviewed independently.

### Bundle B — KVM8 foundation

Creates dedicated directories, network, database/container configuration,
service identities, root-managed secret files, resource limits, one disabled
foundation service, and synthetic-only fixtures. It bootstraps the reviewed
package into the private `Sifututor/sims-owner-analytics` repository and deploys
that exact commit to KVM8. No production credential, real row, public port,
DNS change, backup credential, backup object, updater, MCP service, or enabled
timer is permitted. O4/O7 are approved; remote backup provisioning remains a
separately packeted write before Bundle D can copy real data.

### Bundle C1 — Production SSH tunnel identity

Creates only the restricted KVM8 and production tunnel identities, a pinned
host key, the root-managed client key, one scoped production sshd Match block,
and one disabled KVM8 systemd unit. The only permitted route is KVM8
`127.0.0.1:13307` through production SSH to `127.0.0.1:3306`. Shell, TTY,
agent/X11/user-rc, stream-local, reverse and other-destination forwarding must
all fail. C1 ends with the service disabled/inactive and no listener. The exact
Build-Ready Pack is `Sifututor/sims-owner-analytics:docs/bundles/c1-tunnel.md`.
Removal is a separately reviewed production/KVM8 write.

### Bundle C2 — Production MySQL extractor identity

Critical database operation. Creates only `extract_kvm8`, applies the exact
compiled column grants, shows grants, and proves every denial test. C1 does
not authorize C2. Any rollback `DROP USER` or revoke is separately approved.

### Bundle D — Updater, security gates, and initial backfill

Deploys the reviewed extractor with timers disabled; runs synthetic injection,
crash/retry/idempotency, logging-leak, schema-drift, poison-row, delete, and
reconciliation tests on the actual KVM8 stack; then performs the approved
paced backfill and L1/L2/L3 verification. Publication stays off. Any truncate,
reseed, or real-data removal is destructive and separately approved.

### Bundle E — Steady state and monitoring

Enables updater/monitoring timers, tests alerts and container-level recovery,
and completes the 48-hour clean gate. No owner token or public endpoint.

### Bundle F — Owner access registry and internal DB reader

Hafiz approves the exact two-person recipient list, purpose, expiry and
operation ownership. Creates only `mcp_owner_reader` and proves allowed
owner datasets work while writes, pipeline metadata, excluded fields, and
other schemas fail. No bearer token yet.

### Bundle G — MCP, HTTPS/DNS, tokens, and owner onboarding

Deploys the pinned MCP policy adapter and reverse proxy; applies the exact
approved DNS record; runs security, cross-user-isolation, leak, load, timeout,
revocation, and useful-answer tests; then issues separate expiring tokens to
the two approved owners through the password manager. External-network smoke
must prove that only the MCP endpoint is reachable.

### Bundle H — Close-out

Produces operating, recovery, incident, restore, rotation, schema-change,
recipient-change, future-staff, and teardown runbooks; verifies the access
registry; records sanitized evidence/Koda lessons; and hands the completed
system to Codex for independent review. It does not authorize staff access.

## 14. Acceptance tests

Before owner access, evidence must prove:

1. MCP has no production credential, hostname, tunnel route, or code path.
2. Production account can read every approved column and cannot read every
   excluded/pending column or perform any write/admin/replication action.
3. No credential/security table or field exists in KVM8, backups, logs, or
   MCP registry.
4. Real owner data is available only through owner datasets and the two
   individually authorized tokens.
5. Database port is unreachable externally; other KVM8 projects cannot access
   the analytics network/volume/credentials.
6. MCP DB identity can SELECT approved owner datasets but cannot write or read
   pipeline metadata/other schemas.
7. SQL injection, unknown fields/operators/joins, oversized input/output,
   timeout, cancellation, rate, and concurrency tests fail safely.
8. Two interleaved owner sessions cannot exchange identity, cursors, results,
   errors, or transport state.
9. Logs/errors/metrics contain no canary token, name, phone, email, address,
   search value, SQL, or row result.
10. Initial catch-up plus L1/L2/L3 prove source/destination agreement for
    every published dataset.
11. Schema drift and timestamp-bypassing test cases pause/alert rather than
    silently serving incomplete data.
12. Token expiry, rotation, revocation, and service restart behave as written.
13. Backup and isolated restore preserve data and least privilege without
    public exposure.
14. Five useful-answer examples per dataset return correct synthetic and
    reconciled results, including empty/error cases.
15. The endpoint identifies stale/paused datasets honestly.
16. A bounded snapshot with 5,001+ rows copies every row or stops at its
    declared cap; it can never publish exactly the first 5,000 as complete.
17. A crash during bounded replacement preserves the prior complete dataset;
    no source page becomes independently visible.
18. Consent aggregation stores no raw `user_id`, balances grouped totals to
    the source snapshot and accepts duplicate `records_count` values across
    different groups.
19. Every MCP field ID is unique; bare duplicate names, unknown/reverse joins
    and parent-side metrics across child joins fail.
20. Representative large-dataset queries use reviewed destination indexes and
    remain within the approved time/row/byte budgets.

## 15. Owner decisions and open items

O1 is now confirmed. Only Hafiz can answer the remaining items; each blocks
the named later bundle, not Bundle A.

| ID | Decision | Recommendation / confirmed outcome | Status or gate |
|---|---|---|---|
| O1 | Owner financial visibility | **Approved:** both authorised owners may access individual tutor and staff finance business records. Credentials, bank/payout authentication data, secrets and proofs/files remain excluded. This does not approve ordinary-staff access. | Approved 13/08/2026; implement in finance field matrix |
| O2 | Exact initial owner partner identity and token lifetime | Two separate 90-day renewable tokens: Hafiz + named partner. | F/G |
| O3 | Owner MCP hostname | `sims-analytics.tutorla.tech`, subject to DNS conflict check. | G |
| O4 | KVM8 snapshot/backup model and retention | **Approved:** daily client-side-encrypted logical analytics backup to a dedicated Wasabi bucket/prefix; 30-day retention; KVM8 has deposit-only credentials; decryption/restore credentials stay off KVM8; isolated synthetic restore must pass before real data. Hostinger snapshots are optional additional coverage only. | Approved 13/08/2026; remote provisioning separately gated before D |
| O5 | Whether approved raw operational free text is needed in v1 | **Resolved:** include useful owner business text and mark it untrusted in the MCP registry; exclude raw diagnostics, error logs, config/payload JSON, file paths and bank-account labels. | Implemented in corrected field matrix; no pending fields |
| O6 | Acceptance of sending owner-authorized PII through the chosen Claude account/service | Use only the owner-controlled business account with appropriate organisational privacy settings; record Hafiz's acceptance before token issue. | G |
| O7 | Version-controlled implementation home | **Approved:** dedicated private GitHub repository `Sifututor/sims-owner-analytics`. Bundle B records the exact private-repository commit deployed to KVM8; secrets, real rows, backups and sensitive evidence are forbidden from the repository. | Approved 13/08/2026; B and all implementation |

## 16. Current verdict and next step

**Bundles A and B: CLEAR and complete. Bundle C1: locally implemented and
under independent review; HOLD for commit, merge and execution.** Production
read-only facts prove the proposed restricted tunnel is feasible, but no
production account, key, sshd file/reload, tunnel, MySQL grant, index or data
change has occurred. KVM8 remains at the accepted synthetic Bundle B state.

The next safe step is to finish adversarial review of the C1 package, commit
and merge it through issue #5, freeze the merged hashes and prepare one exact
execution packet. C1 execution will then require one approval covering the
named KVM8 writes, production account/drop-in, guarded sshd reload, temporary
negative tests and success-only cleanup. That approval cannot imply C2, Track
P, backup provisioning, updater deployment or real-data copying.

## 17. Lessons deliberately encoded from earlier Claude work

- One large silent job is forbidden; use bounded slices and checkpointed
  evidence.
- A successful command is not completion; the required handback is completion.
- Exact source behavior is proven before drafting grants or transforms.
- Live schema and query plans outrank migration assumptions.
- No fallback from a scoped identity to root/admin.
- No broad phrase such as “all access” becomes `SELECT *`, raw SQL, or a full
  database clone.
- Owner and staff products are separate, so privacy rules cannot drift between
  them.
- Package/API versions are verified at build time, not copied blindly from an
  old plan.
- Tests must prove the exact forbidden paths as well as the happy path.
- Every rollback is classified; destructive and critical rollback is never
  automatic.
- Claude implements one approved bundle, returns evidence, and stops.
