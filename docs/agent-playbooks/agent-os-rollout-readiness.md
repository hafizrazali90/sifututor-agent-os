# Agent OS Rollout Readiness

Use this document when deciding whether the Sifututor Agent OS is ready for
internal use, project installation, or staff rollout.

## Core Idea

Build for Hafiz and the engineering workflow first. Roll out to staff only
after the internal system is boring, understandable, and safe.

Plain version:

```text
First make the Agent OS reliable for us.
Then package the smallest safe version for staff.
Then add tools only when a person needs them and the access can be checked.
```

## Readiness Ladder

| Level | Name | Who Uses It | Purpose |
| --- | --- | --- | --- |
| 0 | Research / draft | Hafiz + agent | Discuss, design, and document the operating model. |
| 1 | Internal Agent OS | Hafiz + Codex + Claude | Run Sifututor work with shared rules, memory, checks, and close-out. |
| 2 | Project Baseline | Product repos | Install common files, task state, hooks, and guard scripts. |
| 3 | Staff-Safe Kit | Staff using any LLM | Report bugs, run QA, draft docs, and prepare handoffs safely. |
| 4 | Approved Builder Kit | Trusted dev/agent users | Make scoped code changes with repo access and normal approval gates. |
| 5 | Advanced Operations | Explicitly approved people only | Production, deploy, payment, auth, invoice, commission, migration, or mobile API contract work. |

Do not jump from Level 1 to Level 5. Most staff should start at Level 3.

## Minimum Internal Kit

This is the minimum we should keep working for Hafiz before expanding rollout:

- root `AGENTS.md`
- Agent OS overview and quick start
- working-with-Hafiz model
- routing model
- approval gates
- communication model
- context authority
- memory architecture
- capability model
- workflow lanes
- evidence model
- state model
- eval cases
- Koda CLI fallback
- health check
- pre-commit guard
- installer dry-run

If these are unclear or failing, staff rollout should pause.

## Staff-Safe Kit

The staff-safe kit should help staff report, verify, document, and hand off work
without giving risky permissions by default.

Include:

- `AGENTS.md` or a staff-facing summary of it
- project `AGENTS.md`
- project `CLAUDE.md` or equivalent reference
- staff quick start
- QA and evidence playbooks
- bug report / reproduction template
- close-out template
- local memory fallback
- dry-run install/check commands

Allow by default:

- read docs and source code
- write notes, QA reports, screenshots, and draft docs
- run safe local checks when trained
- prepare reproduction steps and handoff notes

Do not allow by default:

- `.env*` reads
- `live/` edits
- production data changes
- deploys
- force pushes
- hook bypass
- payment/auth/invoice/commission/migration/mobile API contract changes
- Koda write access unless approved

## Builder Kit

Give this only to trusted users who need to make code changes.

Add:

- repo write access
- issue/task routing
- branch and commit rules
- verify/QA/review path
- exact file-list approval before commit
- explicit approval before push, PR, merge, deploy, or critical implementation

Builder access is still not production access.

## Advanced Operations Kit

This is not a default staff package.

Use only after Hafiz approves the person, scope, and access path.

Examples:

- production deploy
- production log monitoring
- payment gateway work
- auth/session changes
- invoice/commission logic
- migrations
- mobile API contract changes
- real notification blasts

Required behavior:

1. Read-only diagnosis first.
2. Clear recommendation and risk.
3. Explicit approval.
4. Implementation.
5. Strong evidence.
6. Human review or risk acceptance.

## Install Readiness Checklist

Before calling a repo Agent OS-ready:

- `scripts/agent-checks/agent-os-health.sh` passes in the umbrella repo
- `scripts/agent-checks/agent-os-install.sh --target <project>` passes or only
  reports understood warnings
- target repo has `AGENTS.md`
- target repo has `CLAUDE.md` or equivalent reference
- target repo has `.claude/tasks/active.json` if it uses state-file workflow
- pre-commit guard passes from the target repo
- no required workflow file points to missing docs
- staff/agent permissions match the intended readiness level

## Rollout Order

Recommended order:

1. Finish internal Agent OS docs and evals.
2. Run the health and installer checks on the umbrella repo.
3. Pick one low-risk project repo as the pilot.
4. Install/check the baseline in dry-run mode.
5. Apply only missing safe baseline files if needed.
6. Run one real internal task through the system.
7. Create staff-safe templates.
8. Pilot with one trusted staff member on reporting or QA only.
9. Expand to builder access only after evidence shows the workflow is working.

## What Not To Roll Out Yet

Do not roll out these by default:

- full Koda write access
- production credentials
- deploy permissions
- database write access
- payment/auth/invoice/commission/migration capabilities
- broad MCP connectors with write permissions
- automatic issue closure
- automatic PR/merge/deploy flows

## Acceptance Criteria

The rollout is ready when a new staff member can:

1. understand the working agreement without reading the whole repo
2. ask the agent for the right kind of help
3. avoid forbidden files and production actions
4. produce a useful bug report, QA note, or handoff
5. end with clear status, evidence, next action, and decision needed

The builder rollout is ready only when a trusted dev/agent user can:

1. route a task correctly
2. make a scoped change
3. run the right checks
4. report evidence in plain language
5. stop before commit/push/deploy unless approval exists
6. avoid confusing local, pushed, merged, deployed, and live-smoke states
