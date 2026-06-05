# Review Playbook

Use this for code review, pre-commit review, or adversarial quality checks.

## Review Stance

Lead with findings. Prioritize correctness, regressions, security, missing
tests, workflow violations, and user-facing behavior. Keep summaries secondary.

Use [agent-os-evidence-model.md](agent-os-evidence-model.md) when judging
whether the agent gathered enough proof before handing work to Hafiz or staff.

## Steps

1. Identify the intended scope.
2. Inspect `git diff` or the requested files.
3. Check project rules in `AGENTS.md` and relevant `CLAUDE.md`.
4. Look for broken contracts, missing tests, unsafe paths, and unverified
   critical behavior.
5. Treat "human should check this" as a finding unless Playwright, API, CLI, or
   server-side evidence is genuinely unavailable or unsafe. The review should
   push the agent to gather its own non-destructive evidence first.
6. For user-facing feature, bugfix, hotfix, or small-change work, treat a
   missing permanent E2E regression decision as a review finding. If the change
   affects browser/mobile behavior and no E2E was added or updated, require a
   specific blocker and follow-up fixture/test.
   For any staff/admin/parent/tutor/student/customer workflow, treat missing
   permanent E2E coverage as a blocking review finding unless the workflow is
   explicitly not safely automatable.
7. For staff-facing feature, bugfix, hotfix, or small-change work, treat
   missing release communication as a review finding when relevant. Check for a
   `CHANGELOG.md` entry, affected module help updates, and a What's New release
   entry or seed script. If any item is intentionally not needed, the PR or
   final answer must say why.
8. For multi-fix sessions, treat a missing or stale Session Release Ledger as a
   review finding. Before push, merge, PR, or deploy, verify every session fix
   is classified as local-only, pushed, PR-open, merged, deployed, or excluded.
9. Report findings by severity with file and line references where possible.

## Output Shape

```text
REVIEW - PASS | FAIL | PARTIAL

Findings:
- <severity> <file:line> <issue>

Open questions:
- <question or none>

Test gaps:
- <gap or none>

Permanent E2E:
- <added/updated file path | missing finding | not feasible with reason>
Changed workflow E2E map:
- <workflow>: <permanent E2E file | missing finding | explicit exception>

Release communication:
- <CHANGELOG/help/What's New current | missing finding | not relevant with reason>

Session release ledger:
- <not applicable | current | missing finding>

Summary:
- <brief context>
```
