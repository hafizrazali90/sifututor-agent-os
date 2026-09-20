# Release Documentation Decisions

Copy this file to the project root as `RELEASE-DOCS.md`.

One row per change. Record exactly one decision: `relevant`, `not relevant`, or
`urgent deferral`. The rule, the reasons, and the checker live in
[../release-documentation.md](../release-documentation.md).

This ledger is a record, not a worksheet. Add your row. Do not edit or delete
somebody else's - deleting a past decision is reported as a finding.

| Change | Decision | Artifacts | Owner | Follow-up | Reason |
| --- | --- | --- | --- | --- | --- |
| #418 invoice status filter | relevant | `CHANGELOG.md`, `src/modules/finance/lib/help.ts` | Hafiz Razali | - | Staff pick the filter themselves and need to know it now persists |
| #421 invoice query index | not relevant | - | - | - | Database index only; the invoice screen, steps and wording are unchanged |
| #430 payout rounding hotfix | urgent deferral | - | Hafiz Razali | #431 | Shipped mid payout window to stop incorrect payouts; the reconciliation guide follows this week |

## How to fill each column

| Column | What goes in it |
| --- | --- |
| Change | The issue reference and a short human description. `#418 invoice status filter`. |
| Decision | `relevant`, `not relevant`, or `urgent deferral`. Nothing else reads as a decision. |
| Artifacts | For `relevant`: the documentation files changed in this same bundle, in backticks. Otherwise `-`. |
| Owner | Required for `urgent deferral`: a named person who will write it. Never a role, a queue, or an agent. |
| Follow-up | Required for `urgent deferral`: a real GitHub issue such as `#431` or `Sifututor/sifu-tutor#431`. Never this change's own issue. |
| Reason | Required for `not relevant` and `urgent deferral`. One sentence, in terms of what the staff member sees or does. |

## Check it before you commit

```bash
python3 ../scripts/agent-checks/release_documentation.py --project . --mode advisory --staged
```

Before push, PR, merge, or deploy:

```bash
python3 ../scripts/agent-checks/release_documentation.py --project . --mode blocking --base main
```
