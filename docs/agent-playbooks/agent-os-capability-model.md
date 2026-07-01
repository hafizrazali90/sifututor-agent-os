# Agent OS Capability Model

Status: draft accepted for internal Agent OS use.

This document defines how the Agent OS decides what an agent can actually do in
the current session.

Simple version:

```text
Capability beats role label.
```

Do not assume an agent can do something just because it is called Codex, Claude,
staff, reviewer, or developer. Real capability depends on connected tools,
credentials, filesystem access, network access, approval gates, and safety
rules.

## Why This Exists

Two agents can have the same name but different real abilities.

Example:

- Codex session A has filesystem, git, Koda, browser tools, and GitHub.
- Codex session B has chat only.

They are not the same in practice. The Agent OS must check what is connected
now instead of trusting the role name.

## Capability States

Use these states when reporting tools.

| State | Meaning |
| --- | --- |
| `available` | Tool is connected and verified in this session. |
| `fallback` | Primary tool path is broken, but a safe alternate path works. |
| `unknown` | Tool has not been checked yet. |
| `not_connected` | Tool is absent in this session. |
| `blocked` | Tool exists, but approval or risk gate prevents use now. |
| `forbidden` | Never allowed by Agent OS rules. |

## Capability Formula

An action is allowed only when all three are true:

```text
tool is available or fallback
approval gate allows it
safety boundary does not forbid it
```

If any part is missing, the agent must say what is missing in plain language.

For `auto-read` evidence lanes, "approval gate allows it" means the agent should
use the lane proactively when it is relevant to the active task. The agent should
not ask Hafiz to approve every safe read-only check, and should not skip the
check silently. The limit is scope: use the narrowest relevant read-only source,
never expose secrets, and stop before writes, deploys, mutation, destructive
actions, or critical-lane implementation.

## Auto-Read Scope Rule

Use approved read-only access by default when it helps accuracy.

Plain meaning:

```text
Do not ask Hafiz to say "yes, read it" again when the read is already approved,
safe, and needed for the active task.

The boundary is relevance and safety, not another permission prompt.
```

For diagnosis, planning, verify, QA, review, monitoring, smoke checks, and
release evidence, agents should proactively use the narrowest relevant
approved read-only lane or connected read-only tool.

Allowed:

- read current repo state, logs, monitoring, Planner intake, GitHub state, Koda,
  or access-wrapper output when that evidence is needed for the active task
- use `agent-access-map.md` and `scripts/agent-access/*` wrappers to check
  approved read-only lanes
- summarize the result without exposing secrets or unrelated private data

Not allowed:

- read repository `.env*`, production secrets, or unrelated credential files
- browse broad systems just because access exists
- inspect unrelated users, staff data, projects, tickets, logs, or services
- mutate data, deploy, restart services, resolve alerts, update Planner/GitHub,
  or write to external systems without the proper approval gate
- treat a read-only finding as approval to implement critical-lane changes

Good:

```text
This looks like a production login issue, so I will check the scoped read-only
monitoring and recent deploy evidence before recommending a fix.
```

Bad:

```text
Should I check the approved read-only monitoring first?
```

Also bad:

```text
I have read-only server access, so I scanned everything on the box.
```

## Default Internal Manifest

For a normal Sifututor umbrella Codex session:

| Capability | Default State | Meaning |
| --- | --- | --- |
| Read normal docs/code | `available` | Safe within repo rules. |
| Write docs/workflow files | `available` | Allowed in safe work packets. |
| Git local status/diff | `available` | Safe read-only local evidence. |
| Git commit | `blocked` | Requires exact file-list approval and guard checks. |
| Git push | `blocked` | Requires explicit current-session approval. |
| Koda | `available` or `fallback` | Codex uses CLI-first; Claude may use MCP-first when stable. |
| GitHub | `unknown` | Check session tooling before claiming. |
| Plane | `exception-only` | Do not use by default; only if Hafiz explicitly asks in the current session. |
| Planner | `unknown` | Read-only intake when connected and relevant. |
| Google Drive | `unknown` | Check connector/tooling before claiming. |
| Approved auto-read lanes | `unknown` | Check access map; if available and relevant, use proactively for current evidence. |
| Production logs | `unknown` | Read-only monitoring may be auto-read when scoped; writes/resolution need approval. |
| Deploy | `blocked` or `not_connected` | Always requires explicit approval; often absent by default. |
| `.env*` and secrets | `forbidden` | Do not read, reveal, store, or commit. |
| `live/` modification | `forbidden` | `live/` is read-only reference. |

## What Agents Should Say

Good:

```text
Koda is usable through direct fallback. The normal chat memory wrapper is
timing out in this session.
```

Better:

```text
For Codex, Koda is CLI-first in this workspace. The CLI talks to the same Koda
server but avoids the unreliable chat memory wrapper.
```

Good:

```text
I can prepare the deploy checklist, but I cannot claim deploy capability until
the deploy tool and approval are both confirmed.
```

Bad:

```text
Codex can deploy.
```

Bad:

```text
Anyone can do anything if connected to tools.
```

Better:

```text
Anyone can follow the Agent OS, but what they can do depends on connected
tools, permission profile, and approval gates.
```

## Capability Checks

Use:

```bash
scripts/agent-checks/agent-os-health.sh
```

The health check should report:

- what is verified now
- what is fallback
- what is unknown
- what is blocked by approval
- what is forbidden

Do not treat the health check as permission to cross approval gates. It reports
capability; it does not approve business decisions.

For a lightweight current-session capability report, use:

```bash
scripts/agent-checks/agent-os-capability-probe.py
```

Plain meaning:

```text
Before an agent says "I can use GitHub, Planner, Koda, production logs, or
deploy tooling", it should check what is actually available, unknown, blocked,
or forbidden in this session.
```

A probe is a small, safe test that answers: "Is this tool actually ready for
this task right now?"

Non-technical mental model:

```text
A probe checks whether the key works before the agent promises to open the
door. It does not mean the agent has already walked into the room and finished
the job.
```

Use probes to reduce guessing and back-and-forth:

- before claiming a connector, CLI, wrapper, or approved read lane is working
- before saying a tool is unavailable, especially when a fallback may exist
- after a connector/MCP/API error, to separate "tool not connected" from
  "task itself failed"
- before starting evidence-heavy work that depends on GitHub, Planner, Drive,
  Koda, monitoring, or other connected services

Do not use probes as permission to do the real work. A probe may prove
readiness, but it does not approve push, PR, merge, deploy, destructive action,
critical-lane implementation, or business acceptance.

When reporting a probe to Hafiz, use practical wording:

```text
I checked whether the tool is ready. GitHub read access is available, so I can
use it for repo/PR evidence. That only proves access; it does not mean anything
has been pushed or approved.
```

The first probe is local and non-mutating. It checks workspace write access,
local git state, direct Koda health, local agent-access wrapper presence, and
static boundaries such as commit/push/deploy/secrets/live. It does not call
external GitHub, Planner, Google Drive, production logs, or deploy services.
Those still need task-relevant connector probes or approved read-only wrappers
before being reported as live evidence.

For GitHub read capability, use:

```bash
scripts/agent-checks/agent-os-github-probe.py
```

This performs a tiny read-only GitHub CLI probe: `gh auth status` and
`gh repo view --json ...`. It reports whether GitHub is available for current
repo metadata reads without printing tokens and without creating, editing,
pushing, opening PRs, merging, or changing anything.

For Microsoft Teams Planner read capability, use:

```bash
scripts/agent-checks/agent-os-planner-probe.py
```

This performs a tiny read-only Microsoft Graph probe using the approved
`m365-readonly.env` lane. It checks Graph auth, finds the `Development &
Support` group, finds the `Task Management Board` plan, and reads task
metadata without printing task titles, descriptions, assignees, card content,
tokens, or secrets.

For Google Drive connector readiness, use:

```bash
scripts/agent-checks/agent-os-google-drive-probe.py
```

This checks whether the Codex Google Drive connector metadata is installed and
whether low-noise read tools such as search, folder listing, and file metadata
are available. It does not claim live Drive access by itself because local
scripts cannot invoke the chat connector. When the Google Drive app tools are
exposed in a session, verify live access with a tiny search/list/metadata read
before fetching file contents.

For production monitoring / log-readiness capability, use:

```bash
scripts/agent-checks/agent-os-production-logs-probe.py
```

This performs tiny read-only Sentry and BetterStack checks through the approved
`monitoring-readonly.conf` lane. It reports HTTP status and small sample counts
only. It does not print issue titles, events, monitor URLs, raw logs, tokens, or
secrets, and it does not resolve Sentry issues or change monitors.

## Tool Connector Standard

Use this as the source of truth when deciding between CLI, CLI wrapper, MCP,
app connector, direct API wrapper, browser/Playwright, or native GUI control.

Plain meaning:

```text
Hafiz decides the goal and acceptable risk.
The agent chooses the smallest reliable tool that can prove the task safely.
```

The agent should not ask Hafiz which connector to use for ordinary read/check
work. It should decide from the task, use the narrowest safe path, and explain
the evidence in normal language. Ask Hafiz only when the tool choice changes
product direction, crosses an approval gate, needs broad/unavailable access, or
the project/account/environment is unclear.

Default connector preferences:

| Need | Default path | Why |
| --- | --- | --- |
| Local code, docs, git state, tests, lint, guards, and health checks | CLI first | Fast, cheap, local, predictable, and easy to audit. |
| Repeatable probes, Koda for Codex, monitoring, Planner summaries, and safe operational checks | CLI wrapper first | Keeps output small, hides secrets, and makes the behavior reusable. |
| Rich service workflows such as Google Docs, PR comments, Drive files, Sheets, Slides, or issue review | App connector / MCP when exposed and scoped | Better structure and managed auth when the task needs more than a tiny probe. |
| Stable automation when MCP is too broad, too noisy, or unreliable | Direct API wrapper | Gives a narrow controlled path with sanitized output. |
| Visible product behavior | Browser or Playwright | A real user journey must be proven like a human would experience it. |
| Native desktop app work | GUI automation only when needed | Useful for real app tasks, but more fragile than structured interfaces. |

For Sifututor specifically:

- use CLI-first for local development and repo truth
- use wrapper-first for Koda in Codex sessions
- use GitHub CLI probes for quick GitHub state, then connector/app tools for
  richer PR, issue, review, or comment workflows
- use safe Planner wrappers for staff-intake summaries because Planner is
  intake context, not engineering truth
- use Google Drive connectors/apps for real document content when exposed
- use read-only production wrappers for monitoring, smoke, and operational
  evidence
- use browser/Playwright for user-facing behavior whenever feasible

Do not make connector choice a power contest. The best tool is the one that
answers the current question with the least unrelated access, token output,
secret exposure, and manual interpretation.

## Connector Path Strategy

Use the lowest-noise path that can prove the current task.

| Path | Best for | Tradeoff |
| --- | --- | --- |
| CLI wrapper | Fast repeatable probes, compact JSON, local health checks, scripts, CI-like checks. | Requires local CLI/auth and a maintained wrapper. |
| MCP / connector | Rich agent interaction across services, discovery, multi-step reads, UI-independent workflows. | Can expose a larger tool surface and more context unless narrowed. |
| Direct API | Stable automation behind a wrapper when CLI/MCP is unavailable or too broad. | Requires explicit credential handling and careful output sanitization. |

Default:

```text
CLI wrapper first for probes.
MCP/connector when the agent needs richer read-only interaction.
Direct API only inside a narrow wrapper when it is the cleanest safe path.
```

This default is a shorthand. The full standard above decides the actual path.

## Tool-Use Decision Flow

Plain meaning:

```text
Do not ask "what is the most powerful connector?"
Ask "what is the smallest reliable tool that proves this task safely?"
```

Use this order when choosing a tool path:

1. **Can the local workspace prove it?** Use shell, `rg`, `git`, test runners,
   project scripts, or Agent OS wrapper scripts. This is fastest and cheapest
   for code, docs, repo state, checks, probes, and repeatable evidence.
2. **Does the task need a human-visible web journey?** Use Playwright or the
   browser. Code and API checks do not prove that a staff/admin/parent/tutor
   can complete a UI workflow.
3. **Does the task need rich service context or managed auth?** Use the
   connector/MCP/app tool when available, narrowed to the needed service and
   operation. This is best for Google Drive docs, GitHub PR/issue interaction,
   and service data that benefits from structured tool responses.
4. **Does the task need repeatable service automation with tiny output?** Use a
   direct API wrapper script, not raw API calls in chat. This is best for
   Planner intake probes, monitoring checks, and stable low-noise operational
   evidence.
5. **Does the task happen inside a native desktop app?** Use native app control
   only when the real work is in Finder, Preview, Numbers, or another macOS app
   and no safer structured path exists.
6. **Is the action write, admin, critical, destructive, deploy, merge, PR, or
   push?** Stop at the approval gate unless Hafiz already included that exact
   boundary in the current-session approval.

If two paths can answer the same question, choose the one with:

- less secret exposure
- less irrelevant data
- smaller token output
- more repeatable evidence
- clearer audit trail
- fewer permissions

## Sifututor Tool Choice Matrix

| Job | Preferred path | Why |
| --- | --- | --- |
| Search code, inspect files, check changed docs | CLI: `rg`, `sed`, `git diff`, project scripts | Fast, local, no connector overhead. |
| Run tests, lint, health, guards, probes | CLI wrapper or project command | Repeatable and easy to report. |
| Check local Git state or commit contents | CLI: `git status`, `git log`, `git diff` | Git itself is the source of truth. |
| Check GitHub auth/repo/PR/CI state quickly | CLI probe first; GitHub connector/MCP for richer PR/issue workflows | CLI is compact; connector is better for multi-step GitHub review or comments. |
| Read Teams Planner staff intake | Direct Microsoft Graph wrapper for safe summaries; connector only if richer interaction is needed | Planner is intake, not source of engineering truth; output must stay small and private. |
| Read Google Drive/Docs/Sheets/Slides | Google Drive connector/app first; Drive API wrapper only for repeatable metadata checks | Connector handles document structure better; wrappers keep probes small. |
| Check Sentry/BetterStack monitoring | Direct read-only wrapper | Monitoring probes should return status/counts, not noisy issue details or raw logs. |
| Prove browser-visible product behavior | Playwright/browser | User-visible behavior must be checked like a human journey. |
| Operate a real macOS app | Native app control | Only when the actual task is inside that app. |
| Explain current Agent OS capability | Agent OS health/probe scripts | Standardized, low-noise capability report. |

## Fallback Rule

When the preferred path fails:

1. Do a tiny capability probe or health check.
2. Say what failed in practical language: not installed, not authenticated,
   permission blocked, tool timeout, or target data missing.
3. Try the next safest path only if it stays inside the active task and the
   approval boundary.
4. Do not silently skip evidence. If no safe path exists, say what remains
   unverified and what Hafiz would need to approve or provide.

Example:

```text
The Google Drive connector is visible but live file reads are not exposed in
this session. I can still check local docs and repo state, but I cannot claim
the Drive document itself was verified until a tiny Drive read succeeds.
```

## Automatic Tool Selection During Tasks

The agent should not ask Hafiz which tool to use for ordinary read-only
evidence. It should choose the narrowest safe path, run it, then explain the
result in plain language.

Plain meaning:

```text
Hafiz decides the goal and the risk.
The agent decides the safe tool path for normal evidence gathering.
```

Use this pattern during real tasks:

1. Identify what must be proven: code state, service state, user journey,
   release state, or business decision.
2. Pick the smallest safe tool from the Tool-Use Decision Flow.
3. Run only the read/check action needed for the active task.
4. Report the evidence and any gap in normal language.
5. Ask Hafiz only for product judgment, unavailable access, approval-gated
   actions, or named risk acceptance.

The agent should ask before choosing a tool only when:

- two safe tool paths would produce meaningfully different product decisions
- the tool would expose broad private data unrelated to the active task
- the action would write, mutate, deploy, merge, push, resolve, delete, or
  perform an admin/destructive/critical operation
- the agent cannot tell which project, account, environment, or user role is
  relevant

Do not silently downgrade evidence. If the normal tool path is unavailable,
try the next safe fallback and say what changed:

```text
I could not use Playwright because the app needs credentials I do not have in
this session. I checked the route and server response instead, but the real
browser journey is still unproven.
```

## Scenario Examples

| Scenario | Agent should do | Agent should not do |
| --- | --- | --- |
| Hafiz asks to diagnose a staff-reported UI bug | Read the relevant Planner/context if needed, inspect code, and use browser/Playwright when safe. | Ask Hafiz to click the button before trying available safe checks. |
| Hafiz asks if a PR is safe | Use GitHub CLI/connector for PR state, diff, CI, and review evidence, then explain risk. | Say "looks good" from chat memory only. |
| Hafiz asks whether production is healthy after deploy | Use approved read-only monitoring/log wrappers and smoke checks within the approved boundary. | Open broad raw logs or claim monitoring without checking current evidence. |
| Hafiz asks to read a Google Doc | Use the Google Drive connector/app when exposed; use metadata probe only for readiness. | Pretend connector metadata proves the document content was read. |
| Hafiz asks for a local code explanation | Use local files, `rg`, and git history before reaching for external connectors. | Spend tokens loading unrelated service tools. |

For token efficiency, prefer commands that return small structured output,
especially JSON fields selected with `--json`, `--jq`, or a wrapper-specific
summary. Do not dump full issues, logs, PR diffs, Planner cards, or Drive files
unless the active task needs that detail.

Research basis:

- GitHub CLI `gh auth status`
  ([manual](https://cli.github.com/manual/gh_auth_status)) reports active
  account and authentication state.
- GitHub CLI `gh repo view`
  ([manual](https://cli.github.com/manual/gh_repo_view)) supports
  current-directory repo detection. GitHub CLI formatting supports selected
  JSON fields through `--json` and `--jq`
  ([manual](https://cli.github.com/manual/gh_help_formatting)).
- GitHub MCP Server supports narrowing exposed capabilities with toolsets and
  tools, and read-only mode skips write tools
  ([README](https://github.com/github/github-mcp-server),
  [configuration](https://github.com/github/github-mcp-server/blob/main/docs/server-configuration.md)).
- MCP tools are model-controlled and discoverable, so tool exposure should stay
  clear, narrow, and human-governed for safety
  ([MCP tools spec](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)).
- Microsoft Graph Planner APIs support listing group-owned plans and listing
  tasks for a plan with `Tasks.Read.All` application permission
  ([list plans](https://learn.microsoft.com/en-us/graph/api/plannergroup-list-plans?view=graph-rest-1.0),
  [list tasks](https://learn.microsoft.com/en-us/graph/api/plannerplan-list-tasks?view=graph-rest-1.0)).
- Google Drive API supports partial responses through the `fields` parameter
  and file listing through `files.list`; use small metadata reads before
  fetching document contents
  ([performance guide](https://developers.google.com/workspace/drive/api/guides/performance),
  [files.list](https://developers.google.com/drive/api/reference/rest/v3/files/list),
  [files.get](https://developers.google.com/drive/api/reference/rest/v3/files/get)).
- Sentry supports listing project issues with query parameters; use small
  limits for capability checks
  ([project issues](https://docs.sentry.io/api/events/list-a-projects-issues/)).
- Better Stack Uptime API uses bearer authentication and paginated monitor
  endpoints; use small pages for capability checks
  ([getting started](https://betterstack.com/docs/uptime/api/getting-started-with-uptime-api/)).

Run the local fixture runner when changing capability rules:

```bash
scripts/agent-checks/agent-os-capability-fixture-runner.py
```

This fixture runner does not call external services. It checks the decision
rules before tool use: unknown tools must be checked before being claimed,
not-connected tools need a plain fallback, blocked tools need approval,
critical tools need the right gate, staff capability starts least-privilege,
and forbidden boundaries stay forbidden even when someone asks for them.

## Tool Permission Profiles

Use permission profiles to decide which tools a person, agent, or staff member
should start with. Do not give everyone the same connector set.

Plain meaning:

```text
Give the person or agent enough tools to do the job, not every tool that exists.
More access should be earned by need, evidence, and approval.
```

| Profile | Who uses it | Default tools | Blocked by default |
| --- | --- | --- | --- |
| Owner / Hafiz | Hafiz with trusted agents | Broad read evidence, repo/docs, Koda, GitHub, Planner context, Drive docs, monitoring reads when relevant, local checks. | Secrets, repo `.env*`, `live/` edits, destructive actions, and any external-state action not explicitly approved in the current session. |
| Internal agent | Codex/Claude working with Hafiz | Repo read/write in scoped files, safe local checks, Koda, approved read-only evidence lanes, browser/Playwright, GitHub/Planner/Drive/monitoring probes as relevant. | Push, PR, merge, deploy, production mutation, critical-lane implementation, broad unrelated reads, and secret access. |
| Developer staff - reader/QA | Developer staff checking or reproducing work | Repo/docs read, local checks, QA docs, browser/Playwright where configured, issue/PR read, local memory fallback. | Code writes, commits, push, PR, deploy, production data, Koda write, broad service connectors. |
| Developer staff - builder | Trusted developer staff doing scoped code work | Repo read/write, branch work, local tests, issue/PR read, project profile, safe evidence tools. | Push/PR/merge/deploy without approval, production access, secrets, critical-lane implementation without diagnosis and approval. |
| Support / ordinary staff | Non-developer staff | Microsoft Teams Planner intake only: report symptoms, screenshots, reproduction notes, workflow feedback. | Agent OS install, repo access, code tools, Koda write, GitHub write, production/deploy tools, secrets. |
| Advanced operations | Explicitly approved person/session only | Narrow tools for the approved operation, read-only diagnosis first, then approved write/deploy/admin path. | Anything outside the approved person, scope, environment, and time boundary. |

Default profile rule:

```text
Start lower. Escalate only when the work requires it and Hafiz approves the
person, project, tool, scope, and boundary.
```

Profile does not create access by itself:

```text
Connection gives capability.
Profile gives permission.
Approval gives authority.
Probe gives current proof that the tool works.
```

Use this sequence:

1. Pick the profile.
2. Connect only the tools needed for that profile.
3. Probe/check the tools before claiming they work.
4. Use the tools only inside the profile limits.
5. Stop at approval gates for push, PR, merge, deploy, production, critical
   lanes, destructive actions, and external-state changes.

Example:

```text
A developer staff member may have the Builder profile, but if GitHub is not
connected, they still cannot open PRs. If GitHub is connected, the profile may
allow PR reading, but push or merge still needs approval.
```

Escalation must name:

- who needs the access
- which project or service it affects
- what exact tool/capability is needed
- whether it is read, write, admin, critical, or destructive
- what evidence will prove the work
- when the access should stop or be reviewed again

Do not use a role label as proof of capability. A "developer" without the
right repo profile and checks is not ready for the same work as an internal
agent. An "agent" with a connector is still blocked from push, deploy, critical
implementation, or destructive action unless the approval boundary includes it.

## Profile Lifecycle

Profiles are not permanent entitlements. They are working access for a purpose.

Plain meaning:

```text
Access should have a reason, a boundary, and a review point.
If the reason is gone, reduce the access.
```

| Stage | Meaning | Required action |
| --- | --- | --- |
| Request | Someone needs access for a job. | Name person/agent, project, goal, profile, and why the lower profile is not enough. |
| Activate | Tools are connected and checked. | Follow the Profile Activation Checklist and record capability states. |
| Use | Work happens inside the profile. | Stay inside profile limits and report evidence/blocked actions clearly. |
| Review | Decide whether access is still needed. | Check recent use, risk, project status, failed guards, and whether a lower profile now works. |
| Downgrade | Less access is enough. | Remove write/broad/advanced tools and keep only needed read/check capability. |
| Suspend | Access should pause. | Disable or stop using the profile when need, identity, risk, or tool state is unclear. |
| Upgrade | More access is needed. | Require Hafiz approval naming person, scope, tool, boundary, evidence, and review point. |
| Close | The access purpose is finished. | Record final state, remove temporary tools, and keep only durable lessons. |

Review triggers:

- project or task ended
- person changed role or project
- profile has not been used recently
- tool connection failed or became unknown
- guard/check failed
- staff/user report suggests misuse or confusion
- requested action crosses push, PR, merge, deploy, production, critical,
  destructive, admin, or secret boundaries
- a lower profile can now do the job

Do not upgrade by momentum. Upgrade only when the current profile cannot
complete the approved work safely.

For real assignment records, use
[agent-os-profile-registry-operations.md](agent-os-profile-registry-operations.md).
The capability model defines the rules; the registry operations playbook defines
how private records are created, reviewed, audited, downgraded, suspended, and
closed.

## Koda Access By Agent

Use the most reliable interface for each agent.

| Agent | Default Koda path | Notes |
| --- | --- | --- |
| Codex in this workspace | CLI-first, no chat memory MCP | Use `scripts/agent-checks/koda`; do not install the Codex `memory` MCP because it has repeatedly timed out in chat sessions. |
| Claude Code | MCP-first if stable | Use normal Koda MCP when working; use CLI fallback only when needed and available. |
| Staff/general LLM | no write access by default | Staff should use docs or local notes until Koda permission/risk is reviewed. |
| Automation/scripts | CLI-first | Easier to test, log, and enforce memory rules. |

The CLI is a local interface to the same Koda memory backend. It does not weaken
Koda safety rules.

## Developer Staff Rollout Implication

Developer staff can use the Agent OS, but their permissions should be narrower
than Hafiz/internal-agent permissions by default. Ordinary non-developer staff
stay in Teams Planner intake unless Hafiz explicitly changes the rollout model.

Typical developer-staff capability:

- read safe docs
- inspect scoped repo files
- add reproduction notes
- follow QA checklists
- run local non-destructive checks
- prepare scoped code changes only when approved for builder profile

Developer staff should not by default:

- push code
- merge
- deploy
- read secrets
- write Koda
- access production systems
- close engineering issues without evidence

## Current Decision

Adopt the Capability Manifest model:

```text
Track what is verified, fallback, unknown, blocked, and forbidden.
Do not infer capability from role name.
```
