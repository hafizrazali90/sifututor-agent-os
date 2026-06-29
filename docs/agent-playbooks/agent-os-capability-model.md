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

Run the local fixture runner when changing capability rules:

```bash
scripts/agent-checks/agent-os-capability-fixture-runner.py
```

This fixture runner does not call external services. It checks the decision
rules before tool use: unknown tools must be checked before being claimed,
not-connected tools need a plain fallback, blocked tools need approval,
critical tools need the right gate, staff capability starts least-privilege,
and forbidden boundaries stay forbidden even when someone asks for them.

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

## Staff Rollout Implication

Staff can use the Agent OS, but staff permissions should be narrower by
default.

Typical staff capability:

- report issues
- add reproduction notes
- follow QA checklists
- attach screenshots
- read safe docs

Staff should not by default:

- push code
- merge
- deploy
- read secrets
- close engineering issues without evidence

## Current Decision

Adopt the Capability Manifest model:

```text
Track what is verified, fallback, unknown, blocked, and forbidden.
Do not infer capability from role name.
```
