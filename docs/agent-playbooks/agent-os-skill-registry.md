# Agent OS Skill Registry

Status: draft for internal Sifututor Agent OS use.

Use this file to understand which Sifututor workflow skills exist, who owns
them, where they are defined, what playbook they follow, and what they are not
allowed to do.

Plain meaning: this is the roster. It prevents skills from feeling like hidden
Codex magic.

## Skill Types

| Type | Owner | Location | Example |
| --- | --- | --- | --- |
| Sifututor workflow skills | Sifututor Agent OS | `.agents/skills/*/SKILL.md` | `$task-router`, `$verify`, `$qa`, `$commit`, `$product-design` |
| Sifututor playbooks | Sifututor Agent OS | `docs/agent-playbooks/*.md` | `task-router.md`, `verify.md`, `commit.md` |
| Codex system skills | OpenAI/Codex | `~/.codex/skills/.system/` | `openai-docs`, `imagegen`, `skill-creator` |
| Plugin skills | Plugin provider | `~/.codex/plugins/cache/.../skills/` | Google Docs, Sheets, Slides |
| Custom local skills | Local/custom setup | `~/.codex/skills/` | `sifu-qa-plan-audit` |

This registry is for the first two rows: Sifututor workflow skills and their
playbooks.

## Ownership Rule

Sifututor workflow skills are:

```text
designed by the Sifututor Agent OS process,
owned by the Sifututor workspace,
implemented as Codex skill wrappers,
and governed by AGENTS.md plus the linked playbooks.
```

They are not default Codex behavior.

The git author may show Hafiz's git identity because the files are committed in
this workspace. That does not mean the skill is personal or ad hoc. The
intended owner is the Sifututor Agent OS.

## How To Read A Skill

Each workflow skill has two parts:

| Part | Meaning |
| --- | --- |
| Skill wrapper | Small Codex entrypoint that says when to use the skill. |
| Playbook | The full workflow instruction and source of truth. |

Example:

```text
$commit
-> .agents/skills/commit/SKILL.md
-> docs/agent-playbooks/commit.md
```

The playbook wins when the wrapper is too brief.

## Routing Rule

Skill selection is:

```text
agent-owned, hook-assisted, Hafiz-overridable, and safety-constrained.
```

| Layer | Role |
| --- | --- |
| Hook / dispatcher | Suggests a skill from the prompt. |
| Agent | Confirms or corrects the selected skill. |
| Hafiz | Can override the route naturally. |
| Safety rules | Force stricter behavior for critical or forbidden actions. |

The hook is not the boss. The agent cannot blame the hook for using the wrong
skill.

## Core Workflow Skills

| Skill | Human name | Use when | Wrapper | Playbook | Claude equivalent | Not for |
| --- | --- | --- | --- | --- | --- | --- |
| `$task-router` | Task Router | Starting, classifying, resuming, or routing meaningful work. | `.agents/skills/task-router/SKILL.md` | `docs/agent-playbooks/task-router.md` | `/task-router` or project router skill | Direct commit, deploy, or implementation without checking route and state. |
| `$diagnose` | Diagnose | Bugs, failing tests, unexpected behavior, unclear root cause, or quick read-only intake diagnosis. | `.agents/skills/diagnose/SKILL.md` | `docs/agent-playbooks/diagnose.md` | `/diagnose` | Implementation before approval in critical lanes. |
| `$verify` | Verify | Proving implementation works before QA, review, or commit. | `.agents/skills/verify/SKILL.md` | `docs/agent-playbooks/verify.md` | `/verify` | Product acceptance or broad manual QA by itself. |
| `$qa` | QA | Regression, smoke, browser, visual, manual-style, or route-level quality checks. | `.agents/skills/qa/SKILL.md` | `docs/agent-playbooks/qa.md` | `/qa` | Replacing focused implementation verification. |
| `$review` | Review | Code review, risk review, PR review, pre-commit review, or pre-push/deploy risk check. | `.agents/skills/review/SKILL.md` | `docs/agent-playbooks/review.md` | `/review` | Quietly fixing findings without scope/approval when review-only was requested. |
| `$commit` | Commit | Preparing or creating a local commit. | `.agents/skills/commit/SKILL.md` | `docs/agent-playbooks/commit.md` | `/commit` | Push, merge, deploy, PR, `--no-verify`, secrets, `.env*`, or `live/`. |
| `$product-design` | Product Design | Brainstorming, workflow design, PRD, UX spec, backend contract, build prompts, or major redesign. | `.agents/skills/product-design/SKILL.md` | `docs/agent-playbooks/product-design.md` | `/lite-prd`, `/prd-clarifier`, `/prd-to-ux`, `/ux-to-prompts` | Ordinary narrow bugfixes, small copy edits, or implementation before approval. |

## Continuation Skills

| Skill | Human name | Use when | Wrapper | Playbook | Claude equivalent | Not for |
| --- | --- | --- | --- | --- | --- | --- |
| `$save-session` | Save Session | Ending meaningful work, preserving durable lessons, or preparing future continuation. | `.agents/skills/save-session/SKILL.md` | `docs/agent-playbooks/save-session.md` | `/save-session` | Vague memory dumps or storing secrets/raw payloads. |
| `$handoff` | Handoff | Passing work to Claude, another Codex session, or a human. | `.agents/skills/handoff/SKILL.md` | `docs/agent-playbooks/handoff.md` | `/handoff` | Full session close-out when save-session is needed. |
| `$snapshot` | Snapshot | Freezing current context before compaction, interruption, or pause. | `.agents/skills/snapshot/SKILL.md` | `docs/agent-playbooks/snapshot.md` | `/snapshot` | Marking work complete. |
| `$session-map` | Session Map | Creating, updating, inspecting, or closing a live session map for multi-goal, parallel, or confusing sessions. | `.agents/skills/session-map/SKILL.md` | `docs/agent-playbooks/session-map.md` | `/session-map` or "update the session map" | Replacing GitHub issues, Mission Ledger, Koda, Session Release Ledger, or save-session. |
| `$quick-check` | Quick Check | Checking whether the Sifututor workflow system is healthy before starting work. | `.agents/skills/quick-check/SKILL.md` | `docs/agent-playbooks/quick-check.md` | `/quick-check` or doctor script | Deep QA or implementation verification. |
| `$monitor-production-logs` | Monitor Production Logs | Read-only post-deploy monitoring, Sentry/BetterStack checks, or production log watch. | `.agents/skills/monitor-production-logs/SKILL.md` | `docs/agent-playbooks/monitor-production-logs.md` | `/monitor-production-logs` | Deploying, migrating, editing production, or reading secrets. |

## Normal Skill Chains

Normal coding work:

```text
$task-router
-> implementation
-> $verify
-> $qa
-> $review
-> $commit
-> $save-session
```

Bug or staff symptom:

```text
$diagnose
-> GitHub issue if confirmed or likely engineering work
-> implementation after correct approval
-> $verify
-> $qa
-> $review
-> $commit
```

Product/workflow design:

```text
$product-design
-> brainstorm
-> PRD if needed
-> clarifier if needed
-> UX spec
-> backend contract if needed
-> build prompts
-> implementation approval
```

Session map update:

```text
$session-map
-> update Human Snapshot
-> update mindmap/progress/side paths/decisions as needed
-> preserve continuation prompt
-> promote durable items to Koda, GitHub, Mission Ledger, or save-session only when appropriate
```

Commit request:

```text
$commit
-> guard checks
-> exact file-list review
-> local commit only
```

Push, PR, merge, or deploy request:

```text
$review first
-> explicit current-session approval
-> requested outbound action only
```

## Skill Boundaries

Always separate these:

| Boundary | Meaning |
| --- | --- |
| Diagnose vs implement | Reading and recommending is not the same as changing code. |
| Verify vs QA | Verify proves the change works; QA checks user journey and regression risk. |
| Commit vs push | Commit is local; push changes remote state. |
| Push vs deploy | Pushed or merged code is not automatically live. |
| Planner vs GitHub | Planner is intake context; GitHub owns engineering execution. |
| Koda vs task tracker | Koda remembers lessons; it does not own active task status. |
| Session Map vs memory | Session Map tracks one live session; Koda stores durable lessons. |

## What A Skill Must Not Hide

A skill must not silently hide:

- commit,
- push,
- merge,
- PR creation,
- deploy,
- production mutation,
- destructive cleanup,
- `.env*` access,
- secret/token exposure,
- modification under `live/`,
- critical-lane implementation without Phase A approval.

## When To Add A New Skill

Add a new Sifututor workflow skill only when:

- a repeated workflow has its own entry conditions,
- the workflow needs a distinct playbook,
- routing it separately reduces mistakes,
- the skill can be explained in plain language,
- the boundary with existing skills is clear.

Do not add a skill just because a topic appears once.

## Registry Maintenance

Update this registry whenever:

- a new `.agents/skills/*/SKILL.md` is added,
- a skill wrapper changes its purpose,
- a playbook path changes,
- a Claude equivalent changes,
- a hook begins dispatching to a new skill,
- a skill boundary changes.

Run Agent OS health after registry changes.

For the hook layer that suggests these skills, read
[agent-os-hook-dispatcher.md](agent-os-hook-dispatcher.md).

For Claude/Codex command parity, read
[agent-os-parity-contract.md](agent-os-parity-contract.md). The registry says
what skills exist; the parity contract says which behavior must stay identical
across agents even when the command names differ.
