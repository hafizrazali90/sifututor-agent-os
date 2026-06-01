# Review Playbook

Use this for code review, pre-commit review, or adversarial quality checks.

## Review Stance

Lead with findings. Prioritize correctness, regressions, security, missing
tests, workflow violations, and user-facing behavior. Keep summaries secondary.

## Steps

1. Identify the intended scope.
2. Inspect `git diff` or the requested files.
3. Check project rules in `AGENTS.md` and relevant `CLAUDE.md`.
4. Look for broken contracts, missing tests, unsafe paths, and unverified
   critical behavior.
5. Treat "human should check this" as a finding unless Playwright, API, CLI, or
   server-side evidence is genuinely unavailable or unsafe. The review should
   push the agent to gather its own non-destructive evidence first.
6. Report findings by severity with file and line references where possible.

## Output Shape

```text
REVIEW - PASS | FAIL | PARTIAL

Findings:
- <severity> <file:line> <issue>

Open questions:
- <question or none>

Test gaps:
- <gap or none>

Summary:
- <brief context>
```
