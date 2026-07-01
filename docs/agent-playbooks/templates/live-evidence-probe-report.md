# Live Evidence Probe Report

Use this report when an agent needs to prove which external evidence sources
are currently usable before making claims about GitHub, Planner, production
monitoring, or Koda.

Plain meaning:

```text
This tells Hafiz which live evidence doors are actually open right now, without
pretending the agent has permission to push, merge, deploy, mutate Planner, or
change production.
```

## Summary

| Source | Current state | What this proves | What it does not approve |
| --- | --- | --- | --- |
| GitHub | `<available / unknown / not_connected>` | `<repo or PR metadata can be read>` | Push, PR edits, merge, release, deploy |
| Planner | `<available / unknown / not_connected>` | `<staff intake metadata can be read>` | Planner status, assignment, priority, or content changes |
| Production monitoring | `<available / unknown / not_connected>` | `<Sentry/BetterStack read checks can run>` | Deploy, rollback, alert resolution, monitor changes |
| Koda | `<available / unknown / not_connected>` | `<memory retrieval can run>` | Treating old memory as current truth or writing unrelated memories |

## Evidence

- **Generated at:** `<timestamp>`
- **Repository:** `<repo or unknown>`
- **Commands used:**
  - `python3 scripts/agent-checks/agent-os-github-probe.py --json`
  - `python3 scripts/agent-checks/agent-os-planner-probe.py --json`
  - `python3 scripts/agent-checks/agent-os-production-logs-probe.py --json`
  - `scripts/agent-checks/koda search '{"query":"Agent OS live evidence probe","tags":["sifututor","agent-os"],"limit":1}'`

## Practical Meaning

`<Say what the agent can safely rely on for this task.>`

## Boundaries

- Read-only probe success is not approval for writes.
- Do not print secrets, tokens, raw logs, Planner card content, private payloads,
  or unrelated service data.
- Rerun the relevant probe when current evidence matters.
- If a source is unavailable, explain the fallback or the missing evidence
  instead of guessing.

## Recommended Next

`<continue / rerun a specific probe / ask Hafiz for scope / stop before an approval gate>`
