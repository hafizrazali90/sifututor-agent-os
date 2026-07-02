# Agent OS Developer Staff Quick Start

Use this guide when a Sifututor developer staff member wants to use the Agent
OS with Codex, Claude, GitHub Copilot, Cursor, Gemini, or another LLM-assisted
coding tool.

Ordinary non-developer staff do not use this guide. They report issues through
Microsoft Teams Planner. Agent OS is for Hafiz and developer staff who work in
project repos.

The goal is for developer staff to adopt the full Agent OS workflow, not a
tiny slice of it. They should learn how to move from intake to diagnosis,
planning, build, verification, QA, review, PR, and close-out. Tool permissions
are handled by the Agent OS as the work reaches approval boundaries.

Use [agent-os-rollout-readiness.md](agent-os-rollout-readiness.md) to decide
which readiness level a developer staff member should receive. Non-developer
staff stay in Teams Planner intake.

For the practical handout that a developer can follow during their first real
task, use [developer-full-adoption-pack.md](developer-full-adoption-pack.md).

Developer adoption assumes the developer can read the Agent OS repo as the
workflow handbook, and can access the assigned product repo for actual project
work. Agent OS repo write access is different: changing shared workflow rules
should go through reviewed workflow-improvement work.

## First Rule

Adopt the full workflow first. Let the Agent OS stop the work when approval is
needed.

Plain version:

```text
The developer should work naturally through the whole route.
The Agent OS should say when to continue, when to ask, and when to stop.
```

The developer does not need to memorize every permission rule before starting.
They do need to respect the stop point when the Agent OS says an action needs
Hafiz approval, engineering-lead approval, or a higher access profile.

Developer staff should not get production, deploy, payment, auth, database, or
secret access by default. Add those only when the active work reaches that
boundary, Hafiz approves the need, and the access can be audited.

Before installing or enabling tools, choose the profile from
[agent-os-capability-model.md](agent-os-capability-model.md):

| Profile | Use when | Starting access |
| --- | --- | --- |
| Reader/QA | The developer staff member is reproducing, checking, reviewing, or gathering evidence. | Repo/docs read, local checks, QA docs, issue/PR read, browser/Playwright if configured. |
| Builder | The developer staff member needs to make scoped code changes. | Reader/QA access plus scoped repo write and normal verify/QA/review/commit gates. |
| Advanced operations | The work touches deploy, production, payment, auth, invoice, commission, migration, mobile API contract, or admin systems. | No default access; requires Hafiz approval for person, scope, tool, and boundary. |

Ordinary non-developer staff are not in these profiles. They use Teams Planner
only.

After choosing the profile, use the Profile Activation Checklist in
[agent-os-installation.md](agent-os-installation.md). A profile is not ready
until the required tools are connected, probed, and reported as available,
fallback, unknown, blocked, or forbidden.

## Full Workflow Adoption

Developer staff should learn the same route that Hafiz, Codex, and Claude use.
The first training task should be safe, but the workflow should be complete:

1. **Intake** - understand the issue, report, GitHub issue, or requested
   improvement.
2. **Diagnosis** - inspect current behavior before changing it.
3. **Plan** - explain the likely cause, intended change, proof needed, and stop
   point in plain language.
4. **Build** - make the smallest scoped change that solves the task.
5. **Verify** - run the checks that prove the changed behavior.
6. **QA** - test like a real user would, not only like a programmer.
7. **Review** - check risk, regressions, scope creep, missing evidence, and
   whether the task is actually ready for the next state.
8. **Commit / PR** - prepare the change with clear evidence and get approval at
   the required boundary.
9. **Close out** - state what changed, how it was checked, what remains, and the
   single recommended next action.

This is how the developer becomes useful as Hafiz's tester. They are testing
two things at once:

- whether the product change works for a real user
- whether the Agent OS instructions are clear enough for another developer to
  follow without Hafiz explaining every step

## Approval Boundaries

Permission is not the first thing the developer has to think about. It is the
Agent OS job to detect the boundary and tell the developer what is needed next.

Examples:

| Moment | What the Agent OS should say |
| --- | --- |
| Safe read-only diagnosis | Continue without asking for extra permission. |
| Scoped local code change in an approved builder task | Continue, then verify and QA before commit. |
| Commit | Ask for approval with exact changed files and checks. |
| Push, PR, merge, deploy, or production action | Ask for explicit approval before acting. |
| Payment, auth, invoice, commission, migration, or mobile API contract work | Start with read-only diagnosis, then stop for approval before implementation. |
| Tool or account is not connected | Explain what access is needed, why, scope, and what proof it will support. |
| Secret, `.env*`, `live/` edit, destructive action, or unsafe broad access | Stop; this is forbidden or requires a separate explicit approval path. |

Plain version:

```text
Do the work normally.
When the work reaches a risky door, the Agent OS tells you to knock first.
```

## Which Path To Use

| Developer staff need | Recommended path | What they can do first |
| --- | --- | --- |
| QA or regression checks | Codex or Claude with project docs | Run guided checks and produce evidence |
| Developer work | Codex or Claude with repo access | Make small scoped changes after issue/task routing |
| Product/design thinking | Codex, Claude, or chat LLM | Draft PRDs, UX notes, and build prompts |

Non-developer staff path:

```text
Use Teams Planner only. The developer or agent reads the Planner report later
as intake/context, then verifies it before coding.
```

## Install Or Check A Project

From the umbrella Agent OS repo:

```bash
scripts/agent-checks/agent-os-install.sh
```

To check a product repo:

```bash
scripts/agent-checks/agent-os-install.sh --target path/to/project
```

To create missing baseline files after reading the dry-run output:

```bash
scripts/agent-checks/agent-os-install.sh --target path/to/project --apply
```

The installer source of truth is
[agent-os-install-manifest.json](agent-os-install-manifest.json). Do not copy
baseline rules by hand if the manifest or installer can check them.

## Tool Setup Paths

### Codex

Use Codex when the developer staff member needs code reading, implementation
help, local checks, or Git-aware work.

First commands:

```bash
cat AGENTS.md
scripts/agent-checks/agent-os-health.sh
scripts/agent-checks/agent-os-install.sh --target path/to/project
```

Codex should follow the repo-local playbooks and ask for explicit approval
before commit, push, PR, merge, deploy, or critical implementation.

### Claude Code

Use Claude Code when the developer staff member benefits from Claude skills,
review, QA, or broader reasoning over project files.

First commands:

```bash
cat AGENTS.md
cat CLAUDE.md
scripts/agent-checks/agent-os-install.sh --target path/to/project
```

Claude should use the same shared playbooks under `docs/agent-playbooks/` and
the same approval gates as Codex.

### Other LLM Or Editor Tool

Use this path for GitHub Copilot, Cursor, Gemini, or a general chat model.

Give the tool these files as the starting context:

- `AGENTS.md`
- the target project's `AGENTS.md`
- the target project's `CLAUDE.md` or equivalent project reference
- [agent-os.md](agent-os.md)
- [agent-os-quick-start.md](agent-os-quick-start.md)
- the relevant workflow playbook, such as [diagnose.md](diagnose.md),
  [qa.md](qa.md), [review.md](review.md), or [product-design.md](product-design.md)

If the tool cannot run guard scripts, the developer staff member must run the
commands manually and paste the result into the tool.

## Safe Default Permissions

Allowed by default:

- read project docs
- read source code
- run local non-destructive checks
- write notes, QA evidence, and draft docs
- prepare proposed changes for review

Needs explicit approval:

- edit source code
- create commits
- push branches
- open PRs
- change GitHub issue state
- update Plane ownership, priority, or roadmap direction

Never allowed by default:

- read `.env*`
- modify `live/`
- reveal or copy secrets
- deploy
- push with `--force`
- bypass hooks with `--no-verify`
- change production data
- touch payment, auth, invoice, commission, migration, or mobile API contract
  behavior without diagnosis and approval

## Memory

Koda is preferred for Hafiz and approved engineering agents because it gives
durable cross-session memory.

Developer staff without Koda should use a local memory fallback:

- keep short notes in a project handoff doc
- save only durable lessons, not raw transcripts
- include date, project, issue/task link, what was learned, and next action
- never store secrets, customer private data, tokens, or raw production payloads

Good local memory note:

```text
2026-06-04 - sifututor_parent - QA
Lesson: parent app release versions must be checked with npm run check-version.
Next: verify package-lock metadata if package.json version changes.
```

Bad local memory note:

```text
Here is the whole chat transcript and copied credentials.
```

## First-Run Verification

After setup, run:

```bash
scripts/agent-checks/agent-os-health.sh
scripts/agent-checks/agent-os-install.sh --target path/to/project
```

From the product repo, run:

```bash
../scripts/agent-checks/pre-commit-guard.sh
```

If any check fails, do not continue into implementation. Fix the baseline first
or ask Hafiz/engineering lead for help.

## How Developer Staff Should Ask The Agent

Good prompts:

```text
Read AGENTS.md and the project AGENTS.md. I want to report a bug. Help me write
clear reproduction steps without changing code.
```

```text
Use the QA playbook. Check this screen and tell me what evidence is missing.
Do not commit or push.
```

```text
Use the product-design playbook. Help me turn this idea into a small PRD.
No implementation yet.
```

Risky prompts:

```text
Fix everything and push it.
```

```text
Deploy this now.
```

```text
Read all files including env and production snapshots.
```

## Escalation

Escalate to Hafiz or an engineering lead when:

- the task involves production, secrets, deploy, payments, auth, invoices,
  commissions, migrations, or mobile API contracts
- the agent asks for access the developer staff member does not understand
- the checks fail and the reason is unclear
- the staff report and reproduction evidence disagree
- the change would affect customers, billing, tutors, parents, or staff workflow

## Close-Out Shape

Every developer-staff-assisted session should end with:

```text
Status: done / partly done / blocked
Meaning: what changed or what was learned
Checked: commands, evidence, or why not checked
Recommended next: one next action
Decision needed: yes/no, and what decision
```
