# SIMS Owner Analytics — Bundle A2 Artifact Templates

Status: **TEMPLATES ONLY — NOT DATA OR EXECUTION AUTHORITY**

These are the minimum artifact shapes A2 must fill from reviewed A1 evidence.
Blank, `TBD`, inferred or unapproved cells block the affected dataset.

## 1. Table disposition

One row for every table found in the repository or live database.

Required CSV filename and exact header:

```text
blueprint/table-disposition.csv
source_table,exists_repository,exists_live,domain,owner_use,classification,exclusion_reason,extraction_mode,primary_cursor_key,delete_behavior,reconciliation,source_index,destination_dataset,decision,leak_tests
```

Allowed `classification` values: `owner-row`, `owner-aggregate`, `reference`,
`exclude`, `pending`. Existence values are lowercase `yes` or `no`. Excluded
tables use `extraction_mode=excluded` and have no destination dataset; pending
tables also have no destination until approved.

| Field | Required value |
|---|---|
| Source table | Exact live name |
| Exists in repository | yes/no + migration/model evidence |
| Exists live | yes/no + A1 evidence |
| Domain | identity, operations, finance, reports, support, reference, system |
| Owner use | Named business question, or `none` |
| Classification | owner-row, owner-aggregate, reference, exclude, pending |
| Exclusion reason | Required unless included |
| Extraction mode | watermark, bounded full refresh, aggregate, excluded |
| Primary/cursor key | Exact columns or not applicable |
| Delete behavior | soft flag, hard delete, tombstone, immutable/reference |
| Reconciliation | L1/L2/L3 rule |
| Source index | Existing exact index or required Track P migration |
| Dataset | Destination name or none |
| Decision | D/O ID and approval date |
| Leak tests | Test IDs |

## 2. Field matrix

One row for every candidate source column, including excluded and pending
columns. Do not group multiple columns into one row.

Required CSV filename and exact header:

```text
blueprint/field-matrix.csv
source_table,source_column,live_type,nullable_default,business_meaning,owner_question,classification,sensitivity,destination_dataset,destination_field,destination_type,transform,source_timezone,destination_timezone,cursor_dependency,delete_behavior,mcp_capabilities,source_grant,leak_test,decision
```

Allowed `classification` values: `owner-allow`, `aggregate-only`, `exclude`,
`pending`. Every live column appears exactly once, including columns belonging
to excluded tables. Excluded and pending fields have no destination or source
grant.

| Field | Required value |
|---|---|
| source_table | Exact live name |
| source_column | Exact live name |
| live_type | Complete MySQL type |
| nullable/default | Exact schema behavior |
| business_meaning | Verified meaning, not inferred name |
| owner_question | Concrete use or `none` |
| classification | owner-allow, aggregate-only, exclude, pending |
| sensitivity | identity, contact, finance, auth, secret, free-text, system, ordinary |
| destination_dataset | Exact registry name or none |
| destination_field | Exact registry name or none |
| destination_type | Exact DDL type or none |
| transform | Verbatim rule, normally identity for owner data |
| source_timezone | Explicit or not applicable |
| destination_timezone | Explicit or not applicable |
| cursor_dependency | yes/no and reason |
| delete_behavior | Exact rule |
| MCP capabilities | return/search/filter/sort/aggregate combinations |
| source_grant | Exact column privilege or none |
| leak_test | Test ID |
| decision | D/O ID and approval date |

## 3. Extraction contract

Each table/dataset records:

```text
Dataset:
Source tables:
Fixed SELECT statement:
Bound parameters and types:
No-SELECT-star proof:
Cursor/page ordering:
Composite index/query plan:
Initial backfill rule:
Incremental rule:
Retry/idempotency rule:
Poison-row behavior:
Soft-delete behavior:
Hard-delete behavior:
L1 reconciliation:
L2 reconciliation:
L3 canonical encoding/digest:
Destination transaction boundary:
Publication transition:
Stale/paused behavior:
Expected load/cadence:
Failure stop:
```

## 4. Grant and denial contract

```text
Account and exact host scope:
Allowed tables/columns:
Exact GRANT statements:
Expected SHOW GRANTS:
Allowed SELECT tests:
Denied credential/security tables:
Denied excluded/pending columns:
Denied writes/admin/replication actions:
Schema-drift behavior:
Exact REVOKE/DROP rollback (not pre-approved):
```

Tests must prove denied access using the real restricted extractor identity,
but must not attempt a destructive statement against an account that can
succeed. Bundle C2 owns creation and denial execution.

## 5. Destination DDL contract

```text
Dataset/table:
Columns/types/null/defaults:
Primary/unique keys:
Foreign/join keys:
Indexes:
Charset/collation:
Decimal precision:
Timezone policy:
Created/updated/deleted semantics:
Publication/freshness metadata:
MCP reader grant:
Updater grant:
Backup/restore handling:
```

## 6. MCP registry contract

One entry per dataset and field:

```text
dataset name and plain-language description
required scope
availability/freshness behavior
fields: returnable, searchable, filterable, sortable, aggregatable
operators and value types
fixed joins and relationship cardinality
metrics and decimal behavior
default/max page size and response-byte cap
opaque cursor format/version/expiry
null and not-found behavior
stale/paused error contract
audit field-name contract
```

No raw SQL, table name, join, expression, function or comment may come from the
MCP client.

## 7. Useful-answer test set

Each dataset includes synthetic fixtures and expected results for:

1. detailed lookup by an owner-facing identifier;
2. cross-dataset relationship;
3. aggregate/trend;
4. date-range/filter;
5. empty/not-found/stale;
6. forbidden field/operator;
7. pagination continuation;
8. decimal/timezone/null correctness;
9. token scope and cross-user isolation;
10. audit result containing no values/rows.

## 8. Leak-test inventory

Use synthetic canaries for every prohibited class:

- password and `plain_password`;
- session/remember/reset/verification/OTP values;
- personal/API/OAuth/device/OneDrive tokens;
- secret/private/encryption/webhook keys;
- raw gateway callback/signature/hash/credential;
- bank/payout authentication and account material;
- raw files, identity documents and payment proofs/paths;
- stack trace, raw payload, debug dump and environment value;
- pending medical/special-needs/emergency/declaration/tax/identity data;
- unapproved free text.

Scan extraction output, destination rows/schema, backups, logs, errors, audit,
metrics and MCP responses. A canary in any forbidden location fails the slice.

## 9. Bundle evidence record

```text
Artifact version/SHA:
Source evidence run:
Reviewer:
Approved decision IDs:
Exact commands/scripts:
Positive proof:
Negative proof:
Baseline gaps:
Task-caused gaps:
Residual risks:
Highest proven state:
Next unapproved operation:
```
