# Claude Handoff — SIMS Owner Analytics

Status: **READY ONLY FOR THE BUNDLE A CORRECTION PACKET AFTER HAFIZ APPROVAL**

## Authority

Read completely before acting:

1. `docs/sims-analytics-replica-plan.md`
2. `docs/sims-analytics-data-catalog.md`
3. `docs/sims-analytics-bundle-a-packet.md`
4. `docs/sims-analytics-bundle-a-correction-packet.md`
5. `docs/sims-analytics-artifact-templates.md`
6. `docs/agent-playbooks/agent-access-map.md`

If these conflict, stop and report the exact conflict. Do not use v1–v3.3
rules or older Koda memories to override v4.

## Confirmed product

- The Hostinger server is KVM8. Finch/Finch-Inbox is a project; `ssh finch` is
  only the legacy KVM8 alias.
- MCP users never query SIMS production.
- A restricted updater will later maintain a separate KVM8 business replica.
- Owner v1 is for Hafiz and one named business-owner partner only.
- Both owners may access real names, contacts, identifiers, exact operational
  dates, individual tutor finance and individual staff salary/payroll/
  commission business records.
- Passwords, sessions, tokens, reset/verification codes, secrets, bank/payout
  authentication data, proofs/files and raw gateway security material are
  never copied.
- Future ordinary-staff analytics is a separate cleaned product.
- v1 is read-only analytics, not disaster recovery.

## Current assignment

The original Combined Bundle A has already stopped. Its raw facts remain
evidence, but Codex rejected its generated blueprint and produced corrected
revision `.agent-os/evidence/sims-owner-analytics/20260813T124159Z-a2r1/`.

Do not rerun A1, regenerate the blueprint, contact KVM8, redesign the
architecture or begin construction. Your only assignment is the 101-statement
read-only EXPLAIN correction after Hafiz sends the exact approval sentence
from `sims-analytics-bundle-a-correction-packet.md`.

Before executing, compare the packet's commands byte-for-byte with the local
file and report any syntax, environment, safety or access concern. If you
propose any change, stop; the changed packet needs Codex/Hafiz review.

The canonical correction files are:

- `scripts/agent-access/sims-analytics-bundle-a-explain.sh`; and
- `scripts/agent-access/sims-analytics-build-blueprint.py`;
- `scripts/agent-access/sims-analytics-validate-blueprint.py`; and
- `.agent-os/evidence/sims-owner-analytics/20260813T124159Z-a2r1/blueprint/query-plans.sql`.

Record their SHA-256 values and use them only as the packet specifies. Do not
reconstruct, weaken or edit their shell/SQL/validation rules during execution.

Reviewed hashes for this handoff:

| File | SHA-256 |
|---|---|
| `sims-analytics-bundle-a-explain.sh` | `c4107b7f3666f5b4f329b7d981a50318c9472dd36dd05481c8bf502d92e0cf77` |
| `sims-analytics-build-blueprint.py` | `f0da24969b975f5d48211a97e6c86ed37a0d0931ba716237ed5e0bca6f135795` |
| `sims-analytics-validate-blueprint.py` | `02552f0793b3561846a5e312323750077c196dc34c40340bf4f97f058d685637` |
| corrected `query-plans.sql` | `a7b2cd101e9324a7f589c6097cd01b8c0625a2304c607a7726b489f6ed8923b2` |

Any mismatch stops Bundle A before production or KVM8 contact.

After approval, execute only the correction packet literally. Use only
`sims_agent_readonly`, make no SSH/KVM8/root/admin fallback, query no business
rows, create only the named protected EXPLAIN output, run the strict validator,
return the correction handback and stop for Codex verification.

Bundle A does not authorize Track P, KVM8 installation, production accounts,
grants, tunnels, indexes, data copying, DNS, secrets, MCP deployment, tokens,
rollback or another bundle.

## Repeated-failure rule

One identical retry is allowed only for a transient network timeout. On a
second failure, unexpected output, identity mismatch, schema surprise, PII/
secret canary or permission problem, stop and hand back the evidence gathered.
Do not broaden access or silently continue.

## Completion rule

A shell exit code is not completion. Bundle A completes only when A1 evidence,
the validated A2 blueprint, query-plan evidence and full combined handback
exist. Its highest state is “complete blueprint awaiting Codex review.”
