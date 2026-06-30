# Agent OS Rollout Readiness

Use this document when deciding whether the Sifututor Agent OS is ready for
internal use, project installation, or developer-staff rollout.

## Core Idea

Build for Hafiz and the engineering workflow first. Roll out Agent OS only to
developer staff who work in code/project repos. Ordinary non-developer staff
continue using Microsoft Teams Planner for issue intake.

Plain version:

```text
First make the Agent OS reliable for us.
Then package it for developer staff working on other projects.
Ordinary staff keep reporting through Teams Planner.
```

## Readiness Ladder

| Level | Name | Who Uses It | Purpose |
| --- | --- | --- | --- |
| 0 | Research / draft | Hafiz + agent | Discuss, design, and document the operating model. |
| 1 | Internal Agent OS | Hafiz + Codex + Claude | Run Sifututor work with shared rules, memory, checks, and close-out. |
| 2 | Project Baseline | Product repos | Install common files, task state, hooks, and guard scripts. |
| 2A | Project Profile Verified | Product repos | Document repo-specific commands, evidence, deploy path, critical lanes, and "done" meaning. |
| 3 | Planner Intake Only | Non-developer staff | Report issues through Teams Planner. They do not install or use Agent OS by default. |
| 4 | Developer Staff Kit | Developer staff / trusted dev-agent users | Make scoped code changes with repo access and normal approval gates. |
| 5 | Advanced Operations | Explicitly approved people only | Production, deploy, payment, auth, invoice, commission, migration, or mobile API contract work. |

Do not jump from Level 1 to Level 5. Non-developer staff stay at Level 3
Planner intake unless Hafiz explicitly changes the operating model.

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

## Project Adoption Rule

Before using a product repo for developer-staff rollout, run the
[project-adoption.md](project-adoption.md) workflow.

Project Baseline means the files and hooks exist. Project Profile Verified
means the local repo is understandable enough for a future agent:

- project purpose and users are clear
- source docs are known
- install/test/build/E2E/deploy commands are mapped or gaps are named
- critical lanes are explicit
- human-journey evidence expectations are clear
- "done" is defined for that repo

Do not skip from Project Baseline to developer-staff rollout. A repo can pass
the installer and still be confusing for real work.

## Non-Developer Staff Intake

Non-developer staff use Microsoft Teams Planner only.

Use Planner for:

- bug reports
- screenshots
- reproduction notes
- operational context
- support/task intake

They should not install Agent OS, use repo-connected LLM tooling, receive Koda
write access, or get production/deploy/secret access by default.

Planner is intake, not engineering truth. The agent or developer staff still
verify the report through the normal workflow before coding.

## Developer Staff Kit

Give this only to developer staff who need to work in another project repo.

Choose the narrowest profile from
[agent-os-capability-model.md](agent-os-capability-model.md):

- **Developer staff - reader/QA** for reproduction, checks, QA evidence, and
  issue/PR reading.
- **Developer staff - builder** only when the person needs scoped repo writes
  and can follow the normal verify/QA/review/commit gates.

Do not give a builder profile just because the person is technical. Match the
profile to the actual job.

Include:

- repo write access
- issue/task routing
- local project profile from [project-adoption.md](project-adoption.md)
- branch and commit rules
- verify/QA/review path
- exact file-list approval before commit
- explicit approval before push, PR, merge, deploy, or critical implementation

Developer Staff Kit access is still not production access.

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
7. Confirm ordinary staff continue using Teams Planner for reports.
8. Pilot with one developer staff member on a low-risk project repo.
9. Expand developer staff access only after evidence shows the workflow is working.

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

Developer-staff rollout is ready when a trusted developer staff member can:

1. understand the working agreement without reading the whole repo
2. ask the agent for the right kind of help
3. avoid forbidden files and production actions
4. produce a useful bug report, QA note, or handoff
5. end with clear status, evidence, next action, and decision needed

The developer-staff builder rollout is ready only when a trusted dev/agent user can:

1. route a task correctly
2. make a scoped change
3. run the right checks
4. report evidence in plain language
5. stop before commit/push/deploy unless approval exists
6. avoid confusing local, pushed, merged, deployed, and live-smoke states
