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

## Steps

1. Reproduce or inspect the symptom.
2. Read the nearest project `AGENTS.md` and relevant `CLAUDE.md`.
3. Search Koda for related past failures.
4. Trace the smallest path that can explain the symptom.
5. List hypotheses and evidence.
6. Recommend the smallest fix and tests.

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

Needs approval:
- yes/no and why
```
