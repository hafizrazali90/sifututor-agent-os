# Agent OS Installation

Use this when applying the Sifututor Agent OS baseline to a product repo or when
checking whether a staff machine/project is ready.

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

## Manifest

The install/check source of truth is:

```text
docs/agent-playbooks/agent-os-install-manifest.json
```

Update that manifest when the baseline changes, then update this installation
guide and run the installer in dry-run mode.
