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
