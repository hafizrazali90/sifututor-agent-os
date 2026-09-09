# SIMS Owner Analytics — Bundle A Correction Packet

Status: **HOLD — exact read-only approval required**  
Prepared by: Codex  
Date: 13 August 2026

## Plain-language purpose

The first Combined A run collected useful facts but built its comparison from
the wrong Git repository identity. Codex corrected the blueprint locally. The
corrected design contains 101 included source tables, so the old 80 EXPLAIN
plans cannot prove it.

This packet permits Claude to ask MySQL how it would execute the 101 corrected
SELECT shapes. `EXPLAIN FORMAT=JSON` returns plans, not business rows. The
packet then runs the strict local validator and stops. It does not contact
KVM8 and changes no production state.

## Exact scope

Allowed:

- verify the four hashes below;
- locally validate all 101 corrected EXPLAIN statements;
- connect only as `sims_agent_readonly` to the already-approved production
  target with TLS required;
- execute only those 101 `EXPLAIN FORMAT=JSON SELECT` statements through the
  canonical helper;
- write one mode-600 local output file under the protected correction evidence
  directory;
- run the blueprint validator with `--require-live-plans`;
- return a sanitized handback and stop.

Forbidden:

- any business-row SELECT or output;
- KVM8/SSH contact;
- root, sudo or a different MySQL identity;
- writes, migrations, indexes, grants, users, tunnels, databases, containers,
  DNS, secrets, tokens, backups or rollback;
- editing SQL/helper/validator files after approval;
- reusing the superseded 80-plan output.

## Canonical files and reviewed hashes

| File | SHA-256 |
|---|---|
| `scripts/agent-access/sims-analytics-bundle-a-explain.sh` | `c4107b7f3666f5b4f329b7d981a50318c9472dd36dd05481c8bf502d92e0cf77` |
| `scripts/agent-access/sims-analytics-build-blueprint.py` | `f0da24969b975f5d48211a97e6c86ed37a0d0931ba716237ed5e0bca6f135795` |
| `scripts/agent-access/sims-analytics-validate-blueprint.py` | `02552f0793b3561846a5e312323750077c196dc34c40340bf4f97f058d685637` |
| `.agent-os/evidence/sims-owner-analytics/20260813T124159Z-a2r1/blueprint/query-plans.sql` | `a7b2cd101e9324a7f589c6097cd01b8c0625a2304c607a7726b489f6ed8923b2` |

The builder is hashed for provenance but is **not run** in this correction
packet. Any hash mismatch stops before production contact.

## Preconditions and local-only preflight

Claude runs exactly:

```bash
cd /Users/hafizrazali/Projects/Sifututor

EVIDENCE_DIR=".agent-os/evidence/sims-owner-analytics/20260813T124159Z-a2r1"
SQL_FILE="$EVIDENCE_DIR/blueprint/query-plans.sql"
OUTPUT_FILE="$EVIDENCE_DIR/blueprint/query-plans-output.txt"

test ! -e "$OUTPUT_FILE"
test "$(wc -l < "$SQL_FILE" | tr -d ' ')" = "101"

test "$(shasum -a 256 scripts/agent-access/sims-analytics-bundle-a-explain.sh | awk '{print $1}')" = "c4107b7f3666f5b4f329b7d981a50318c9472dd36dd05481c8bf502d92e0cf77"
test "$(shasum -a 256 scripts/agent-access/sims-analytics-build-blueprint.py | awk '{print $1}')" = "f0da24969b975f5d48211a97e6c86ed37a0d0931ba716237ed5e0bca6f135795"
test "$(shasum -a 256 scripts/agent-access/sims-analytics-validate-blueprint.py | awk '{print $1}')" = "02552f0793b3561846a5e312323750077c196dc34c40340bf4f97f058d685637"
test "$(shasum -a 256 "$SQL_FILE" | awk '{print $1}')" = "a7b2cd101e9324a7f589c6097cd01b8c0625a2304c607a7726b489f6ed8923b2"

python3 scripts/agent-access/sims-analytics-validate-blueprint.py "$EVIDENCE_DIR"

scripts/agent-access/sims-analytics-bundle-a-explain.sh \
  "$SQL_FILE" "$OUTPUT_FILE" --validate-only
```

Expected final preflight lines:

```text
Blueprint validation passed: tables=160 live_columns=2000 required_artifacts=17
Validated 101 EXPLAIN statements
Validation-only mode: no database connection attempted
```

Any other count, existing output file, validation error or hash mismatch stops
the packet before production contact.

## Single production read-only command

After every precondition passes, Claude runs exactly:

```bash
cd /Users/hafizrazali/Projects/Sifututor

EVIDENCE_DIR=".agent-os/evidence/sims-owner-analytics/20260813T124159Z-a2r1"

scripts/agent-access/sims-analytics-bundle-a-explain.sh \
  "$EVIDENCE_DIR/blueprint/query-plans.sql" \
  "$EVIDENCE_DIR/blueprint/query-plans-output.txt"
```

Expected safe output:

```text
Validated 101 EXPLAIN statements
EXPLAIN evidence written: <protected path>/query-plans-output.txt
```

## Verification and negative proof

Claude then runs exactly:

```bash
cd /Users/hafizrazali/Projects/Sifututor

EVIDENCE_DIR=".agent-os/evidence/sims-owner-analytics/20260813T124159Z-a2r1"
OUTPUT_FILE="$EVIDENCE_DIR/blueprint/query-plans-output.txt"

test "$(stat -f '%Lp' "$OUTPUT_FILE")" = "600"
test "$(rg -c '^EXPLAIN$' "$OUTPUT_FILE")" = "101"

python3 scripts/agent-access/sims-analytics-validate-blueprint.py \
  --require-live-plans "$EVIDENCE_DIR"

if rg -n -i \
  'password=|authorization:|bearer[[:space:]]|secret=|token=|-----BEGIN|[[:alnum:]._%+-]+@[[:alnum:].-]+\.[[:alpha:]]{2,}' \
  "$OUTPUT_FILE" > "$EVIDENCE_DIR/27-corrected-plan-canary-findings.txt"; then
  chmod 600 "$EVIDENCE_DIR/27-corrected-plan-canary-findings.txt"
  echo "STOP: possible PII/secret pattern in corrected EXPLAIN evidence"
  exit 1
else
  rm -f "$EVIDENCE_DIR/27-corrected-plan-canary-findings.txt"
  echo "Corrected EXPLAIN evidence canary: PASS"
fi
```

Expected proof:

- output mode is 600;
- exactly 101 `EXPLAIN` headers exist;
- strict validator passes with `--require-live-plans`;
- canary prints `PASS`;
- no business-row value is pasted into chat.

## Stop conditions

Stop immediately on:

- any identity/host/database/TLS mismatch from the helper;
- any hash, statement-count or validator mismatch;
- an existing output target;
- any MySQL error or unexpected result shape;
- any possible PII/secret canary finding;
- a need to edit, retry with broader access or run a different command.

No retry is approved except one identical retry for a transient connection
timeout before MySQL returns any plan. Every other correction needs a new
reviewed packet/hash.

## Rollback

No production rollback exists because EXPLAIN is read-only. The local output
is evidence and is not deleted automatically. If it is malformed or contains
a canary finding, Claude locks it to mode 600, reports the path without its
contents and stops for Codex/Hafiz direction.

## Exact approval sentence

```text
I approve the SIMS Owner Analytics Bundle A correction packet dated 13/08/2026, limited to the 101 reviewed EXPLAIN FORMAT=JSON statements through sims_agent_readonly, protected local evidence, strict validation and stop. No KVM8 contact, production write, index, grant, user, tunnel, database, container, DNS, secret, token, data copy, rollback or construction bundle is approved.
```

## Required handback

```text
Bundle: A correction — corrected query-plan evidence only
Approved sentence received:
Four hashes verified:
Preflight result:
Production identity/target confirmed by helper:
EXPLAIN statement/header count:
Strict validator result:
Canary result:
Unexpected findings:
Production state changed: none
KVM8 contacted: no
Local file created and mode:
Highest proven state:
Next action: Codex verification; no Track P or construction authorised
```
