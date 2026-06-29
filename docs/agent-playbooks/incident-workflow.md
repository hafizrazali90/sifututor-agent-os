# Incident Workflow

Use this when production or staging is actively broken, users or staff are
blocked, money/security/data may be affected, or monitoring shows a serious
regression.

Plain meaning: incidents are protection-first work. The first job is to
understand impact and reduce harm. Do not treat an incident like an ordinary
bugfix where the agent casually edits code, commits, and waits for later QA.

## Incident Path

Use this path unless Hafiz explicitly chooses a different emergency boundary:

```text
detect -> triage -> impact -> mitigation options -> Hafiz decision -> fix or rollback -> verify -> deploy if approved -> smoke -> monitor -> postmortem / lesson
```

The easy version:

```text
First protect users.
Then understand the cause.
Then choose rollback, hold, or fix forward.
Then prove the system is healthy again.
Then save the lesson.
```

## Severity

Use practical severity, not ceremony:

| Severity | Meaning | Default behavior |
| --- | --- | --- |
| Critical | Money, auth, data integrity, security, production outage, mobile API contract, or many users blocked. | Read-only triage first, explicit Hafiz approval before mutation, stronger evidence, monitor after fix. |
| High | Important staff/customer workflow blocked, but no obvious money/security/data corruption. | Triage, mitigation options, focused fix or rollback after approval, smoke and monitor. |
| Medium | Degraded behavior or partial workflow issue with workaround. | Diagnose, plan fix, normal verify/QA/review, release when approved. |
| Low | Cosmetic or low-impact issue discovered during monitoring. | Capture, route as normal bug or follow-up. |

If unsure, treat it as higher severity until evidence says otherwise.

## What The Agent May Do Immediately

Without another permission question, the agent should use safe read-only
evidence needed for the active incident:

- check current Git/PR/deploy state
- read relevant docs and code
- run public HTTP smoke checks
- check approved read-only monitoring/log wrappers
- check safe read-only database or API evidence when the task requires it
- inspect recent commits, deploy notes, and known regression patterns
- ask one clarifying question only when the missing answer changes the safety
  of the next action

This does not allow secret reads, `.env*`, `live/` edits, data mutation,
deployment, rollback, destructive actions, or broad unrelated exploration.

## What Must Pause For Hafiz

Pause before:

- production deploy
- rollback
- database migration or data repair
- payment/auth/invoice/commission/mobile API contract implementation
- destructive file/server action
- changing DNS, Cloudflare, cPanel, server config, or credentials
- closing the incident when evidence is incomplete
- customer/staff messaging that requires business judgment

The agent should recommend the safest option and explain the tradeoff in plain
English.

## Triage Report

Use this before mutation:

```text
Incident triage:
- Symptom: <what is happening>.
- Affected users/workflow: <who and what flow>.
- Severity guess: <critical/high/medium/low and why>.
- Current state: <ongoing/intermittent/stopped/unknown>.
- Evidence checked: <logs, smoke, deploy state, code, staff report>.
- Likely cause: <known/unknown and confidence>.
- Safe options:
  1. <rollback/hold/fix forward/monitor/disable feature>
  2. <tradeoff>
- Recommended action: <one recommendation>.
- Decision needed: <exact approval or business decision>.
```

If the agent cannot verify a claim, say so. Do not invent certainty to make the
incident feel calmer.

## Mitigation Choices

Use these words:

| Choice | Meaning |
| --- | --- |
| Monitor only | No active user harm is confirmed, so watch before changing anything. |
| Hold / pause release | Stop further release movement while investigating. |
| Rollback | Return to a known safer version or config. |
| Fix forward | Implement a targeted fix and release it. |
| Disable / feature flag | Turn off the broken path if the system supports it. |
| Manual workaround | Staff can use a safe temporary process while the fix is prepared. |

For each choice, explain:

- what it protects
- what risk it creates
- what evidence is needed after the action

## Fix Or Rollback Boundary

If Hafiz says `proceed until incident stabilized`, the agent may:

- continue read-only triage
- recommend mitigation
- implement a targeted fix only after the implementation boundary is approved
- run focused tests and smoke checks
- prepare commit/PR/deploy packet when approved
- monitor after release
- stop before broader refactors or unrelated cleanup

If Hafiz says `emergency hotfix`, the agent should still say:

```text
I can move faster, but I will still stop before production deploy, data
mutation, destructive action, or critical-lane widening unless you explicitly
approve that boundary.
```

## Post-Fix Proof

Before saying the incident is stable, report:

- what changed or rolled back
- what environment contains the fix
- the exact smoke or user-journey evidence
- monitoring/log check result
- whether the original symptom is gone
- any remaining risk or follow-up

Highest proven state matters. "Fix deployed" is not the same as "incident
stable".

## Communication

The agent should draft communication, but Hafiz owns business tone and external
send decisions.

Include:

- who is affected
- what changed for them
- workaround, if any
- whether the issue is resolved or still being monitored
- what staff should do next

Do not over-share technical root cause to staff/users unless Hafiz asks.

## Postmortem / Lesson

Create a postmortem or durable lesson when:

- money, auth, invoice, commission, data integrity, security, production outage,
  or mobile API contract was involved
- rollback or emergency hotfix was needed
- the same pattern could happen elsewhere
- monitoring caught a regression
- staff/customer trust was affected

Minimum postmortem:

```text
Incident:
<short title>

Impact:
<who/what/how long>

Root cause:
<known or unknown>

What fixed or mitigated it:
<rollback/fix/config/manual workaround>

Evidence:
<tests/smoke/logs/monitoring>

Prevention:
<test, monitor, playbook, code guard, follow-up issue>

Memory:
<Koda id or skipped with reason>
```

## Common Mistakes

- Starting implementation before read-only triage.
- Treating a critical incident as a normal bugfix.
- Saying stable when only a fix was committed.
- Deploying without explicit approval.
- Forgetting rollback as an option.
- Asking Hafiz to remember incident steps.
- Skipping monitoring after a hotfix.
- Saving no durable lesson after a serious incident.

