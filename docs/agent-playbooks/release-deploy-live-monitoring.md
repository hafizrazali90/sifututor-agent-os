# Release, Deploy, Live Smoke, And Monitoring

Use this when Hafiz asks whether work is live, asks to deploy, says to continue
until production is monitored, or when a merged PR needs to reach staging or
production.

Plain meaning: merged is not live. Deployed is not automatically healthy. A
release is only trustworthy when the agent can name the exact state reached and
what evidence proves it.

Project-wide release rule: after any staging or production deploy in any
Sifututor project, changed-workflow smoke is mandatory before the release is
called done. Generic route availability can support the report, but it does not
replace a safe smoke of the actual user-facing functionality that changed. If a
changed-workflow smoke cannot be run safely, name the blocker and the strongest
evidence gathered instead.

## State Ladder

Use these words exactly when the distinction matters:

| State | Meaning | What proves it |
| --- | --- | --- |
| Merged | The change is in the target source branch. | GitHub PR state or `origin/main` commit. |
| Staging deployed | The target commit reached staging. | Deploy record, server SHA, release output, or project deploy evidence. |
| Staging smoke checked | Staging is reachable and the changed workflow was checked where safe. | Smoke command, browser/API check, screenshot, or read-only state check. |
| Production deployed | The target commit reached production. | Deploy record, production SHA/version, release output, or server evidence. |
| Production smoke checked | Production is reachable and the changed workflow was checked where safe. | Public HTTP smoke, safe browser/API check, screenshot, or read-only evidence. |
| Production monitored | Logs, errors, uptime, and known regression signatures were checked after release. | Sentry/BetterStack/log output summary and time window. |
| Accepted / closed | Hafiz accepts the outcome and any remaining business risk. | Hafiz approval, issue/PR closure, or release sign-off note. |

Do not skip words. If production is deployed but monitoring was not checked,
say so directly.

## Recommended Boundaries

| Hafiz says | Agent may do | Agent stops before |
| --- | --- | --- |
| `proceed until staging verified` | Preflight, deploy to staging if approved, smoke staging, report gaps. | Production deploy. |
| `proceed until production deployed` | Preflight, confirm source commit, deploy production after approval, verify deployed state. | Calling it healthy/live-accepted without smoke/monitoring. |
| `proceed until production smoke checked` | Production deploy path plus safe production smoke checks. | Monitoring sign-off and final business acceptance. |
| `proceed until production monitored` | Production deploy path, smoke checks, read-only logs/alerts/monitoring, final state report. | New fixes, rollback, destructive action, critical-lane widening, or business acceptance if risk remains. |
| `deploy only` | Run the approved deploy, verify deployed state, and run the mandatory changed-workflow smoke when safe. | Monitoring unless the boundary includes it. |
| `monitor only` | Read-only production logs, alerts, uptime, and known regression patterns. | Deploy, mutation, issue resolution, or production writes. |

If Hafiz says a loose phrase such as `release this`, `ship it`, or `finish until
live`, the agent should translate it into a boundary before acting:

```text
For this task, "live" can mean production deployed, smoke checked, and monitored
for new errors. I can continue until production monitoring is complete. I will
pause before deploy approval, destructive action, rollback, critical-lane
widening, or final business risk acceptance.
```

## What The Agent Can Automate

After the correct boundary is approved, the agent should handle the mechanical
release work:

- source commit/PR identification
- local and CI evidence review
- release preflight
- backup/pre-deploy checklist where the project requires it
- staging or production deploy command only when deploy is approved
- deployed SHA/version check
- safe public HTTP smoke checks
- safe browser/API smoke checks when credentials and data are approved
- read-only monitoring through approved lanes
- final state report

The agent should not ask Hafiz to list these steps. The agent should recommend
the path and explain where it will stop.

## What Must Stay Explicit

These remain separate authority decisions:

- production deploy approval
- rollback or hotfix decision
- database migration approval
- data mutation
- payment, auth, invoice, commission, migration, mobile API contract, or
  security-sensitive implementation
- destructive server/file action
- changing DNS, cPanel, Cloudflare, server config, or production credentials
- final business risk acceptance when evidence is incomplete or user impact is
  meaningful

Read-only monitoring and safe HTTP smoke checks may use the standing task access
approval when they are necessary for the active release task. They do not allow
deploys, production writes, secret reads, broad data browsing, or unrelated
infrastructure exploration.

Before saying staging or production is ready, deployed, live, smoke checked,
monitored, or accepted, apply [no-mistakes-lite.md](no-mistakes-lite.md). Plain
meaning: merged, deployed, smoke checked, monitored, and accepted are different
states, and the agent must not collapse them into "done."

## Minimum Release Report

Use this natural-language shape:

```text
Release state:
- Source: <commit/PR/branch>.
- Highest proven state: <merged | staging deployed | staging smoke checked | production deployed | production smoke checked | production monitored | accepted / closed>.
- What proves it: <deploy record, SHA, smoke, logs, monitoring>.
- What is not proven yet: <gap or none>.
- User impact: <what changed for staff/parents/tutors/admins/customers>.
- Recommended next: <monitor longer | rollback | fix | accept/close | deploy production>.
- Decision needed: <yes/no and exact decision>.
```

After the release state is proven, apply Recipient-Specific PR And Release
Close-Out from [agent-os-communication.md](agent-os-communication.md). Infer
the relevant audiences and prepare one copy-ready message per distinct
audience. If another developer's PR was materially improved, their single
integrated message must explain the final delta and reasoning, identify what
the original evidence missed, state the verified release result, and request
their independent verification with evidence. Use only confirmed ticket or
report sources.

## Monitoring Window

Use the smallest honest window:

| Release type | Suggested monitoring |
| --- | --- |
| Docs/tooling only | No production monitoring needed; say not relevant. |
| Low-risk app change | Check logs/alerts shortly after deploy and name the time checked. |
| Staff-facing workflow | Smoke the workflow and check logs/alerts after release. |
| Payment/auth/invoice/mobile API/critical lane | Smoke, read-only state evidence, monitoring, and Hafiz risk sign-off. |
| Incident/hotfix | Monitor until the known regression pattern stays quiet or a rollback/follow-up is chosen. |

## Rollback Or Failure

If smoke or monitoring fails:

1. Say what failed in practical terms.
2. Name the affected user/system flow.
3. Stop before new implementation unless the boundary already covers a hotfix.
4. Recommend the safest option: rollback, hold, diagnose, fix forward, or watch
   longer.
5. Do not hide failed release evidence behind "mostly done".

## Common Mistakes

- Saying `live` when only merged.
- Saying `deployed` without checking deployed SHA/version.
- Saying `healthy` without smoke or monitoring evidence.
- Asking Hafiz to remember the deploy checklist.
- Treating read-only monitoring access as permission to mutate production.
- Deploying a critical-lane change without diagnosis, stronger evidence, and
  explicit approval.
