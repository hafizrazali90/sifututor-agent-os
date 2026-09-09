# Agent OS Project Adoption

Use this when applying the Sifututor Agent OS to a product repo, checking
whether a product repo is ready, or preparing a repo so Claude, Codex, another
LLM, or a trusted developer can work there predictably.

The target product repo does not have to live inside the Sifututor GitHub org
or local umbrella workspace. A repo in another company GitHub org, such as the
Kelas app under Learnest Lab, still follows the same adoption rule: shared
Agent OS core plus a small verified local project profile.

Plain meaning:

```text
The umbrella Agent OS is the shared brain. Each product repo needs a small
local adapter so the shared rules know how that repo actually builds, tests,
deploys, and proves work.
```

Do not copy the whole Agent OS into every product repo. Keep the shared system
in the umbrella repo, then add only the local project rules and commands that
make the product repo usable.

## Core Principle

Use:

```text
shared core + local project profile
```

Shared core means the rules that must stay the same everywhere:

- approval gates
- forbidden files and secrets rules
- communication style
- state language
- memory discipline
- evidence standard
- commit and push boundaries
- critical-lane rules

Local project profile means the repo-specific facts:

- what the project is for
- who uses it
- tech stack
- install/test/build/E2E commands
- deploy path
- important docs
- critical lanes
- safe access lanes
- human-journey QA expectations
- known local conventions

The local profile may add stricter rules. It must not weaken root `AGENTS.md`.

## When This Starts

Start this workflow when Hafiz asks:

- whether a repo is Agent OS-ready
- to install, roll out, or adopt Agent OS in a product repo
- to make Claude/Codex/another LLM work consistently in a repo
- to prepare a repo for developer staff, trusted developers, or agents
- why a product repo behaves differently from the umbrella Agent OS
- to onboard a developer into an external company repo, such as the Kelas app
  under Learnest Lab

Also use it before developer-staff rollout. Ordinary non-developer staff use
Teams Planner as intake; they do not install or operate Agent OS by default.

## What To Read First

From the umbrella root:

1. `AGENTS.md`
2. `docs/agent-playbooks/agent-os.md`
3. `docs/agent-playbooks/agent-os-rollout-readiness.md`
4. `docs/agent-playbooks/agent-os-installation.md`
5. this file

From the target product repo:

1. `AGENTS.md`
2. `CLAUDE.md` or equivalent project reference
3. `.claude/tasks/active.json` if present
4. `TESTING.md` if present
5. deploy, QA, E2E, or onboarding docs if present

If project `AGENTS.md` and `CLAUDE.md` conflict, stop and explain the conflict
before editing. Do not silently choose the convenient rule.

## Adoption States

Use these states when reporting readiness:

| State | Plain meaning |
| --- | --- |
| Not adopted | The repo exists, but no local Agent OS baseline was confirmed. |
| Baseline present | Required files exist, but repo-specific commands and evidence are not fully mapped. |
| Profile drafted | The local project profile exists, but some facts still need verification. |
| Profile verified | The local profile matches current docs/files and safe checks. |
| Ready for internal agent use | Hafiz, Codex, Claude, or trusted technical users can work with the repo using normal Agent OS rules. |
| Ready for developer staff use | Trusted developer staff can make scoped repo changes with normal evidence and approval gates. |

Do not call a repo ready for developer staff use just because the installer
passes. The installer checks files. The adoption profile checks whether a
future agent or developer understands the product repo.

## Local Project Profile

Each product repo should eventually have a short local profile in its
`AGENTS.md`, `CLAUDE.md`, or a linked project doc. Draft profiles may live under
`docs/agent-playbooks/project-profiles/` first when the target repo should not
be edited yet.

Use [templates/project-profile.md](templates/project-profile.md) as the reusable
shape. Keep the final profile close to the product repo so agents can find it
before editing that repo.

Minimum fields:

```text
Project:
Purpose:
Primary users:
Stack/runtime:
Main source docs:
Active task state:
Install command:
Lint/typecheck command:
Unit/feature test command:
E2E or human-journey test command:
Build command:
Deploy path:
Critical lanes:
Safe read-only access:
Forbidden paths:
Human-journey evidence:
Permanent regression test expectation:
Known local conventions:
What done means in this repo:
Handoff/save-session notes:
```

Explain each field in normal language. For example:

```text
What done means in this repo:
For visible SIMS UI work, done normally means the change is implemented,
focused tests pass, a browser journey or screenshot-backed check proves the
staff workflow, TESTING.md is updated when needed, and the change is committed.
It is not live until merge, deploy, smoke, and monitoring evidence prove it.
```

Do not mark a profile as verified until the commands, evidence expectations,
critical lanes, deploy path, and done state have been checked against current
repo files or safe command output. If a field is unknown, say `unknown` and add
it to the Known Gaps section.

## Product Repo Starter Map

Use this as the first audit map. Verify each row from current files before
treating it as final.

| Project | Purpose | Local adoption focus |
| --- | --- | --- |
| `sifu-tutor` | Laravel SIMS rebuild | Strongest profile first: staff/admin UI, billing, invoice, payment, commission, auth, migrations, TESTING.md, browser E2E, staging/prod path. |
| `ripple-suite` | Next.js dashboard rebuild | Frontend/API evidence, TypeScript/build checks, QuickBooks/FIUU/SIMS integration risk, PR/release state. |
| `sifututor_tutor` | React Native tutor app | Mobile journey QA, Maestro/mobile test path, API contract compatibility, release/build path. |
| `sifututor_parent` | Parent app rebuild | Parent journey QA, payment/invoice surfaces, mobile/API contract compatibility, release/build path. |
| `lls` | Learnest Laravel backend | Backend/API contracts, migrations, auth/data critical lanes, feature tests. |
| `lls-frontend` | Learnest React frontend | Browser journey QA, frontend build/tests, API contract evidence. |
| `lls-mobile` | Learnest mobile app | Mobile journey QA, API contract evidence, release/build path. |
| `creative-hub` | Creative Hub | Project-specific commands, user journeys, deployment path. |
| `finch-inbox` | Omnichannel inbox | Messaging workflows, privacy/data access, integration evidence. |
| `cx-call-capture-android` | CX call-capture Android app | Establish local contract, mobile verification commands, release path, and CRM integration evidence. |
| `sims-owner-analytics` | Owner-only SIMS analytics | Preserve its strict data boundary, document offline/live evidence levels, and add shared task-state only when adopted. |

## Adoption Workflow

1. Identify the target repo and adoption goal.
2. Read root `AGENTS.md` and the target repo's `AGENTS.md`.
3. Read the target `CLAUDE.md` or equivalent project reference.
4. Check active task state if the repo uses `.claude/tasks/active.json`.
5. Look for `TESTING.md`, E2E docs, deploy docs, and project-specific QA docs.
6. Run the installer in dry-run mode from the umbrella root:

   ```bash
   scripts/agent-checks/agent-os-install.sh --target <project>
   ```

7. Run the relevant guard or health check that is safe for the repo.
8. Draft or update the local project profile.
9. Name gaps instead of guessing missing commands or deploy paths.
10. Save durable lessons to Koda only when the lesson changes future agent
    behavior.

Plain version:

```text
First learn the repo. Then check the baseline. Then write the local adapter.
Then prove the adapter points to real commands and docs. Do not pretend a repo
is adopted just because a few files exist.
```

## Evidence Required

Minimum evidence for `Profile drafted`:

- root `AGENTS.md` read
- target repo `AGENTS.md` read
- target `CLAUDE.md` or equivalent checked
- active task state checked when present
- install dry-run output reviewed
- local project profile drafted with unknowns named

Minimum evidence for `Profile verified`:

- profile fields match current files
- install dry-run has no unexplained failures
- guard or project-safe check passed, or gap is named
- test/build/E2E commands are verified from docs or actual safe command output
- critical lanes and forbidden paths are explicit

Minimum evidence for `Ready for developer staff use`:

- profile verified
- GitHub/task routing is clear
- verify/QA/review/commit path is clear
- permanent E2E or human-journey expectation is clear
- commit/push/PR/deploy boundaries are clear
- ordinary staff intake stays in Teams Planner

## Approval Boundaries

No extra approval is needed for read-only adoption diagnosis and dry-run checks
that follow the root safety rules.

Ask Hafiz before:

- applying generated files
- changing a product repo's `AGENTS.md` or `CLAUDE.md`
- changing project test/build/deploy scripts
- granting tool access to developer staff or builders
- adding Koda write access for a new user or agent
- push, PR, merge, deploy, production action, data mutation, destructive
  action, or critical-lane implementation

## What To Save

Save to:

- product `AGENTS.md` or linked project doc for the local project profile
- umbrella `docs/agent-playbooks/project-profiles/` for draft profiles that are
  not ready to promote into a product repo yet
- `docs/agent-playbooks/agent-os-rollout-readiness.md` for readiness rules
- `docs/agent-playbooks/agent-os-installation.md` for installer behavior
- Session Map for current adoption progress
- Koda for durable lessons only
- Mission Ledger for future adoption gaps that are important but not ready
  for GitHub

Do not save:

- raw secrets
- `.env*` values
- broad transcript summaries
- vague progress notes such as "updated adoption docs"

## Common Failures

| Failure | Correct behavior |
| --- | --- |
| Copying the whole Agent OS into every repo | Keep shared core in the umbrella repo; add only a local adapter/profile. |
| Saying a repo is ready because files exist | Separate baseline files from verified project understanding. |
| Guessing test/build/deploy commands | Verify from docs or safe command output; otherwise name the gap. |
| Weakening root rules in a project | Stop. Local rules can be stricter, not weaker. |
| Starting developer-staff rollout before profile verification | Recommend project adoption first, then developer staff kit. |
| Treating all products the same | Keep the shared workflow same, but map local commands, evidence, and critical lanes per repo. |

## Close-Out Shape

When finishing an adoption step, report:

```text
Status:
<drafted / verified / ready for internal use / not ready yet>

Meaning:
<what a future agent can now understand or safely do in this repo>

Checked:
<docs read, installer/guard/check commands, gaps>

Recommended next:
<one next repo, profile field, or readiness step>

Decision needed:
<yes/no; exact decision if yes>
```
