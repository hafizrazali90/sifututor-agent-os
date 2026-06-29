# Workflow Efficiency Audit

Use this when Hafiz asks why the Agent OS feels slow, repetitive, confusing, too
tight, too loose, or when he asks whether parts of the workflow can be
automated.

Plain meaning: this is the agent's way to inspect the workflow itself. It looks
for wasted steps, repeated approvals, unclear next actions, tool failures,
missing automation, and places where the workflow is making Hafiz do work the
agent should do.

## When To Run It

Run a lightweight audit when:

- Hafiz says the workflow is annoying, confusing, slow, or too manual
- the agent repeatedly asks "what next" or fails to recommend the next action
- the session has many local commits waiting to be pushed
- PR/CI/merge/deploy steps create repeated approval friction
- a hook, skill, Koda, Session Map, or playbook keeps failing or drifting
- multiple agents behave differently for the same task
- the agent skips available read-only evidence and Hafiz has to prompt for it

Run a fuller audit before changing the Agent OS rules, skills, hooks, evals, or
memory behavior.

## What To Inspect

| Area | Question |
| --- | --- |
| Approval friction | Did the agent ask for approval too often, too late, or at the wrong boundary? |
| Missing next action | Did Hafiz have to ask "what next?" after a meaningful step? |
| State confusion | Did the agent blur local, committed, pushed, PR open, merged, deployed, live checked, or accepted states? |
| Evidence friction | Did the agent skip tests, CI, browser/mobile checks, logs, or approved read-only tools it could have used? |
| Tool friction | Did MCP, CLI, hooks, Koda, GitHub, Planner, or browser tooling fail repeatedly? |
| Context friction | Did the agent lose the main goal, sub-goal, return path, Session Map, or Reference Pack? |
| Skill drift | Did Claude and Codex route the same task differently? |
| Doc drift | Did one rule get updated but linked playbooks, skills, hooks, evals, or README stay stale? |
| Over-automation risk | Would automation remove Hafiz's real risk decision instead of only removing repetitive work? |
| Under-automation waste | Is Hafiz approving a step 99% of the time because the agent should bundle it? |

## Output Shape

Use this table when the audit needs to be saved:

| Friction | Practical impact | Suggested fix | Automation behavior | Risk guard |
| --- | --- | --- | --- | --- |
| <what slowed us down> | <why it matters to Hafiz/workflow> | <doc/skill/hook/eval/Koda change> | <none/read-only/mechanical/boundary-based> | <what must still stop> |

Automation behavior:

| Behavior | Meaning |
| --- | --- |
| None | Keep it manual because the decision is business/risk/product judgment. |
| Read-only | Agent can gather evidence without asking again. |
| Mechanical | Agent can do repetitive work after one clear boundary. |
| Boundary-based | Agent can continue through outward actions only when Hafiz names the stop point. |

Avoid numeric level names in user-facing chat unless Hafiz asks for formal
terminology. Say the practical behavior instead.

## How To Improve The Workflow Safely

Use [agent-os-improvement-loop.md](agent-os-improvement-loop.md) after the audit
finds a real behavior change.

The improvement should usually update:

- the owning playbook
- the related skill wrapper or command alias
- router wording if the route changes
- evals or health checks when the behavior is important enough to enforce
- Koda only for durable behavior lessons or corrections
- Session Map when the change matters to the current session story

Do not silently edit one doc and call the workflow fixed when the behavior
depends on several layers.

## Recommended Cadence

For everyday work, the audit can be a short note in the final close-out:

```text
Workflow note: this step was approved manually again. I recommend bundling
push + PR open + CI monitoring next time, while still stopping before merge.
```

For bigger Agent OS work, save a fuller audit before changing automation rules.

