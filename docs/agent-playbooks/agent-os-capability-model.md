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
| Plane | `unknown` | Check session tooling before claiming. |
| Planner | `unknown` | Read-only intake when connected and relevant. |
| Google Drive | `unknown` | Check connector/tooling before claiming. |
| Production logs | `unknown` | Must be explicitly connected and risk-reviewed. |
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
| Codex in this workspace | CLI-first | Use `scripts/agent-checks/koda`; chat MCP is optional/unreliable until proven healthy. |
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
- change Plane priority/owner/roadmap
- close engineering issues without evidence

## Current Decision

Adopt the Capability Manifest model:

```text
Track what is verified, fallback, unknown, blocked, and forbidden.
Do not infer capability from role name.
```
