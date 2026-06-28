# Diagnose Playbook

Use this for bugs, failing tests, unexpected behavior, or unclear root cause.

## Rules

- Start read-only unless the user explicitly approved implementation.
- Use relevant approved auto-read access proactively during diagnosis. Do not
  ask Hafiz to prompt for safe read-only evidence that the active task needs.
- Separate symptoms, hypotheses, evidence, and fix recommendation.
- For auth, payments, invoices, commissions, migrations, deployment, financial
  behavior, or mobile API contracts, this is Phase A and must stop before
  implementation.
- Use [related-impact-audit.md](related-impact-audit.md) after identifying a
  likely root cause for bugfix/hotfix work. At diagnosis time, this means
  naming the root-cause pattern, the likely audit strength, and obvious related
  surfaces to inspect before or during the fix.

## Steps

1. Reproduce or inspect the symptom.
2. Read the nearest project `AGENTS.md` and relevant `CLAUDE.md`.
3. Search Koda for related past failures.
4. Trace the smallest path that can explain the symptom.
5. List hypotheses and evidence.
6. Recommend the smallest fix and tests.
7. For bugfix/hotfix work, recommend the related-impact audit strength:
   local related check, same-pattern sweep, or critical impact audit.

## Output Shape

```text
DIAGNOSE - <project>

Symptom:
- <what is wrong>

Evidence:
- <files, commands, traces>

Likely root cause:
- <cause or unknown>

Recommended fix:
- <smallest safe fix>

Tests to prove it:
- <checks>

Related impact:
- <audit strength, related surfaces to inspect, and scope boundary>

Needs approval:
- yes/no and why
```
