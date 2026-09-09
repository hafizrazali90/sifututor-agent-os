# Codex Verification Checklist — SIMS Owner Analytics

Status: independent review checklist; no execution authority

Hafiz gives each Claude handback and referenced evidence to Codex before the
next bundle is approved. Codex reports `CLEAR` or `HOLD` for the next exact
operation, not for the whole project.

## Combined Bundle A verification

Claude runs A1 facts and A2 blueprint preparation continuously. Codex reviews
the complete result once; an A1 failure still stops the whole bundle.

### A1 facts

### Target identity

- Evidence path resolves below
  `.agent-os/evidence/sims-owner-analytics/<UTC>-a1`.
- Repository root and SHA are recorded.
- Executed script SHA matches the reviewed local script.
- MySQL identity is `sims_agent_readonly` and database is
  `sifututortutorla_LiveDB`.
- Production target is `151.246.1.164:3306` with MySQL TLS required.
- SSH alias resolved to the known KVM8 host; evidence calls it KVM8, not Finch.

### Scope and safety

- Only the canonical top-level A1 script ran.
- No business table was queried for row values.
- SQL contains only constant/runtime and `information_schema` SELECTs.
- No root/admin/sudo/write/restart/install/DNS/container-change command ran.
- No `.env*`, `live/`, logs, application config or secret/container env was
  read.
- Temporary option file was removed and no secret appeared in process output.
- Evidence scan passed or any match was contained and not pasted into chat.

### Completeness

- Original A1 records its umbrella SHA/count only as historical evidence; the
  corrected blueprint records the nested `sifu-tutor` path, reviewed ref, SHA
  and 152 repository-created tables. The umbrella SHA is never accepted as
  application-schema provenance.
- Live table, column, index, constraint and trigger metadata files exist and
  are non-empty where applicable.
- Repository-only and production-only lists exist, even when empty.
- KVM8 CPU, memory, storage, swap, mounts, ports and available container/
  network facts are recorded.
- Unavailable optional facts are named rather than filled by assumption.
- Hostinger snapshot facts remain explicitly manual/unknown until evidenced.

### A2 blueprint

- Every repository or live table has one disposition.
- Every candidate column has one field-matrix row and classification.
- Owner-authorised real identity/contact/finance fields are not accidentally
  removed by obsolete staff-cleaning rules.
- Password/auth/token/secret/gateway-security/bank-auth/proof classes receive
  no grant, destination column or MCP field.
- Individual tutor and staff finance is available only to the two owner
  identities; future staff datasets remain separate.
- Extraction SQL has no `SELECT *` and names every source field.
- Money is decimal; timezone/null/delete behavior is explicit.
- Every watermark query has an exact successful query plan and composite-index
  conclusion.
- Timestamp-bypassing writes are covered by L1/L2/L3.
- Grants are column exact and denial tests cover renamed/unknown credential
  equivalents.
- Destination DDL, MCP registry, useful-answer fixtures, leak tests, load model
  and risks agree with the same field matrix.
- A2 contains only reads and produces a separate next-bundle recommendation.
- The canonical blueprint validator passes with exact live table/column
  coverage.
- Query-plan SQL passes the canonical EXPLAIN validator and the output contains
  plans only, never business rows.
- Bounded full-refresh contracts use a consistent source snapshot, explicit
  row/byte caps, primary-key pagination and one complete destination
  transaction. A 5,001+ row test cannot truncate at 5,000.
- Append-only mode is limited to repository/test-proven immutable tables and
  still has L2/L3 mutation/delete detection.
- Consent has exact aggregate SQL, a valid composite destination key, balanced
  totals and no raw `user_id` in destination/MCP/logs.
- MCP field IDs are globally unique and exact joins preserve one child row;
  reverse joins and parent-side metrics are forbidden.
- Destination DDL has reviewed secondary indexes and realistic-volume query
  plans for large MCP access paths.
- `source-index-plan.csv` exactly matches watermark tables and separates large
  tables into individual approval slices and small tables into no more than
  five indexes per slice.

### Corrected Bundle A proof

- Correction evidence path is
  `.agent-os/evidence/sims-owner-analytics/20260813T124159Z-a2r1`.
- The four hashes match
  `sims-analytics-bundle-a-correction-packet.md`.
- Local structure validator passes for 160 tables, 2,000 columns and 17
  required artifacts.
- Exactly 101 corrected EXPLAIN statements validate and exactly 101 `EXPLAIN`
  headers appear in the mode-600 output.
- Validator passes with `--require-live-plans` and the canary scan passes.
- No KVM8 contact or production state change occurred.

### Decision

`CLEAR to prepare the first construction bundle` requires all A1 and A2 items.
It does not authorize Track P or Bundles B-H. Any identity mismatch, leaked
value, unapproved command, missing schema/blueprint evidence, validator bypass
or broadened access is `HOLD`.

## Later-bundle invariant checks

For B–H, Codex checks before clearing the next operation:

1. exact approved packet/version and target identity;
2. preconditions from all earlier verified bundles;
3. exact changed files/hosts/accounts/tables/columns;
4. positive and negative proof;
5. secret/PII-safe evidence;
6. rollback classification and approval boundary;
7. baseline failures separated from task-caused failures;
8. no silent widening from owner v1 to ordinary staff;
9. highest state honestly proven;
10. next bundle explicitly not executed.

## Final owner journey

Before v1 is accepted, Codex independently proves:

- each owner has a different token;
- revoked/expired/wrong token fails uniformly;
- the public endpoint reaches only the MCP, not MySQL or production;
- owner queries return correct real business data from KVM8;
- individual tutor and staff finance works for owners;
- excluded credential/security fields cannot be discovered or returned;
- two interleaved owners do not exchange identity, cursor or result state;
- stale/paused datasets identify themselves honestly;
- writes fail at tool, service and DB privilege layers;
- logs/audit/metrics contain operation shape but no values/results;
- the KVM8 updater is the only production-connected component;
- production remains unaffected by owner queries;
- backup restore and token/credential rotation have evidence;
- no ordinary staff access exists.
