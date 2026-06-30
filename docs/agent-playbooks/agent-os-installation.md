# Agent OS Installation

Use this when applying the Sifututor Agent OS baseline to a product repo or when
checking whether a staff machine/project is ready.

Use [agent-os-rollout-readiness.md](agent-os-rollout-readiness.md) before
deciding whether the target should receive the internal kit, staff-safe kit,
builder kit, or advanced operations access.

Use [project-adoption.md](project-adoption.md) when the question is not only
"are files present?" but "can a future agent actually work in this product repo
without guessing?"

The installer is deliberately boring:

- dry-run by default
- refuses `live/`
- never reads `.env*`
- does not overwrite existing project workflow files
- points project-level Claude settings to shared umbrella hooks where possible

## Prerequisites

- Local clone of the umbrella Agent OS repo.
- Local clone of the target product repo.
- Git available on the machine.
- Python 3 available for JSON checks and guard scripts.
- Optional: Koda configured for richer memory checks.

## Check The Umbrella Repo

From the umbrella root:

```bash
scripts/agent-checks/agent-os-install.sh
```

This checks:

- Agent OS docs
- guard scripts
- Codex skills
- shared hook files
- Koda direct health through `agent-os-health.sh`
- local capability reporting through `agent-os-capability-probe.py`

To see the current capability report directly:

```bash
scripts/agent-checks/agent-os-capability-probe.py
```

Plain meaning: this tells the agent what is available, unknown, blocked, or
forbidden on the current machine before it claims tool access.

To verify GitHub read access for the current repo:

```bash
scripts/agent-checks/agent-os-github-probe.py
```

Plain meaning: this checks the GitHub CLI login and reads tiny repo metadata.
It does not push, create PRs, edit issues, merge, or change anything.

To verify Microsoft Teams Planner read access for staff intake:

```bash
scripts/agent-checks/agent-os-planner-probe.py
```

Plain meaning: this checks Microsoft Graph login, the staff intake team, the
Planner board, and task metadata visibility. It does not print card content,
post to Teams, edit Planner cards, or change anything.

To check Google Drive connector readiness:

```bash
scripts/agent-checks/agent-os-google-drive-probe.py
```

Plain meaning: this checks whether the Google Drive connector metadata and
small read tools are installed. It does not read Drive files by itself. When
the connector tools are available in a chat, use a tiny search, folder listing,
or file metadata read before fetching any file contents.

To verify production monitoring/log-readiness access:

```bash
scripts/agent-checks/agent-os-production-logs-probe.py
```

Plain meaning: this checks read-only Sentry and BetterStack access with tiny
status/count reads. It does not print raw logs, issue titles, monitor URLs,
tokens, or secrets, and it does not resolve alerts or change monitors.

## Check A Product Repo

From the umbrella root:

```bash
scripts/agent-checks/agent-os-install.sh --target sifututor_parent
```

The target can be relative to the umbrella root or an absolute path.

## Apply Missing Project Baseline Files

Only run apply after reading the dry-run output:

```bash
scripts/agent-checks/agent-os-install.sh --target path/to/project --apply
```

Apply mode creates missing baseline files only:

- `.claude/settings.json`
- `.claude/hooks/README.md`
- `.claude/tasks/active.json`
- `.claude/tasks/SCHEMA.md`
- `.claude/tasks/archive/.gitkeep`

If any of those files already exist, the installer leaves them alone.

## Draft The Local Project Profile

After the dry-run check, do not call the repo fully adopted yet. Fill the local
project profile from [project-adoption.md](project-adoption.md):

- purpose and primary users
- stack/runtime
- source docs
- install, test, build, E2E, and deploy commands
- critical lanes
- safe access lanes
- human-journey evidence expectations
- what "done" means in that repo

Plain meaning:

```text
The installer proves the basic files exist. The project profile proves the
agent understands how this repo actually works.
```

## Verify After Install

From the umbrella root:

```bash
scripts/agent-checks/agent-os-health.sh
scripts/agent-checks/workflow-doctor.sh
scripts/agent-checks/pre-commit-guard.sh
```

From the target product repo:

```bash
../scripts/agent-checks/pre-commit-guard.sh
```

## Staff Rollout Rule

Start staff with the smallest safe setup:

1. The working agreement in `AGENTS.md`.
2. A readable project `CLAUDE.md` or equivalent project reference.
3. Shared guards and dry-run checks.
4. Koda or a documented local memory fallback.
5. No production, deploy, payment, auth, or secret access by default.

Before enabling tools, pick the permission profile from
[agent-os-capability-model.md](agent-os-capability-model.md). Use Reader/QA for
developer staff who only need evidence and reproduction, Builder only for
scoped repo changes, and Advanced Operations only after Hafiz approves the
person, scope, tool, and boundary. Ordinary non-developer staff stay in Teams
Planner intake.

## Profile Activation Checklist

Use this before saying a profile is ready.

Plain meaning:

```text
Choosing a profile is not enough. The needed tools must be connected, checked,
and limited to that profile.
```

1. **Name the person/agent and profile.**
   Example: `Nadia - Developer staff Reader/QA for sifu-tutor`.
2. **Name the project or service boundary.**
   Example: `sifu-tutor only`, `GitHub read only`, or `Planner intake only`.
3. **Connect only the tools needed for the profile.**
   Do not enable Drive, GitHub write, Koda write, deploy, or monitoring just
   because they exist.
4. **Run the smallest safe probe/check for each connected tool.**
   Use the capability probes in this guide where available.
5. **Record the capability state.**
   Use `available`, `fallback`, `unknown`, `not_connected`, `blocked`, or
   `forbidden` from [agent-os-capability-model.md](agent-os-capability-model.md).
6. **Explain what is still blocked.**
   A connected tool may still be blocked by profile, approval, missing
   project profile, missing credentials, or critical-lane rules.
7. **Run a small real task before expanding access.**
   Reader/QA should produce evidence. Builder should make a scoped local
   change and stop before push/PR/deploy unless approved.
8. **Review before escalation.**
   Escalate only after the profile worked safely and the next tool is truly
   needed.

Activation report shape:

```text
Profile: <person/agent> - <profile> - <project/service>
Connected: <tools connected and probed>
Available: <what works now>
Blocked: <what is intentionally not allowed>
Unknown: <what was not checked or not connected>
Next safe task: <small task to prove this profile works>
Escalation needed: <none or exact approval needed>
```

## Profile Review Checklist

Use this when reviewing, downgrading, suspending, upgrading, or closing a
profile.

Plain meaning:

```text
Do not let access stay high just because it was once needed.
```

Review:

1. What profile is active now?
2. What project/service boundary does it cover?
3. Which tools are still connected?
4. Which tools were actually used recently?
5. Did any probe, guard, health check, or workflow check fail?
6. Is the original reason for access still active?
7. Can a lower profile do the job now?
8. Is any requested escalation tied to a specific approved task?

Decision:

| Decision | Use when | Action |
| --- | --- | --- |
| Keep | Same profile is still needed and checks are healthy. | Keep profile and set the next review point. |
| Downgrade | Less access is enough. | Remove write/broad/advanced tools and record the lower profile. |
| Suspend | Need, identity, tool state, or risk is unclear. | Stop using the profile until clarified. |
| Upgrade | Current profile cannot complete approved work safely. | Get Hafiz approval for person, scope, tool, boundary, evidence, and review point. |
| Close | Work is done or access is no longer needed. | Remove temporary tools and keep only durable lessons. |

Profile review report shape:

```text
Profile reviewed: <person/agent> - <profile> - <project/service>
Current tools: <connected/probed tools>
Recent use: <what was actually used>
Decision: <keep | downgrade | suspend | upgrade | close>
Why: <plain reason>
Next review: <date/event/none>
Approval needed: <none or exact approval>
```

## Profile Assignment Records

Use [templates/profile-assignment-record.md](templates/profile-assignment-record.md)
when creating a real profile record.

Recommended private registry:

```text
~/.config/sifututor/agent-os/profile-assignments.md
```

Public repo docs should define the profiles, lifecycle, and template. Real
assignments should live in the private registry or a task-specific approval
trail such as chat, GitHub issue, PR, or handoff. Do not store real profile
assignments in Koda unless the content is a durable rule rather than a current
access state.

Use [agent-os-profile-registry-operations.md](agent-os-profile-registry-operations.md)
for the actual operating routine: when to create records, when to review them,
how to summarize audits, and how to close or downgrade access without leaking
private assignment details.

Give extra tools only when the staff member has a real need and the capability
can be checked.

For the staff-facing first-run guide, use
[agent-os-staff-quick-start.md](agent-os-staff-quick-start.md).

## Manifest

The install/check source of truth is:

```text
docs/agent-playbooks/agent-os-install-manifest.json
```

Update that manifest when the baseline changes, then update this installation
guide and run the installer in dry-run mode.
