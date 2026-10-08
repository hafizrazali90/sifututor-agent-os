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

## Feedback Loop Gate

Before any theory about the cause, name one command you have already run that
goes red (fails the way the user saw the bug fail) on this exact bug, and show
its output with secrets redacted. The command must be:

- red-capable: it drives the real code path and checks the user's exact
  symptom. "Runs without errors" does not count.
- deterministic: same result every run. For a random bug, pin a high repeat rate.
- fast: it finishes in seconds.
- agent-runnable: an agent can run it without a person.

If you catch yourself reading code to form a theory before that command exists,
stop. A theory without a failing command is the failure this gate prevents.
If you forced the failure by editing code or data, compare against a pristine
copy to prove the edit really landed before you trust the red result.

For critical lanes (payments, commission, auth, migrations, production data),
build the loop read-only first: against a copy, a replay of captured input, or a
test, never against production data. Phase A stays read-only.

If no loop can be built, stop and say so. List what you tried and ask for the
access or captured example you need.

Adapted from the mattpocock/skills repository (MIT licence).

## Steps

1. Pass the Feedback Loop Gate above: run a command that goes red on the exact
   symptom before tracing any cause.
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

Command that goes red: <command and its output>

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
