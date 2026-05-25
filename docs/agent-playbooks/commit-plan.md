# Parity Commit Plan

Last updated: 2026-05-26

The umbrella directory `/Users/hafizrazali/Projects/Sifututor` is not itself a
Git repository. Commit workflow changes per sub-project repository. Shared
workspace files under `docs/agent-playbooks/` and `scripts/agent-checks/` are
currently filesystem-level workspace assets unless a parent repository is
created later.

## Recommended Commit Groups

Commit per project, not as one mixed change:

1. `sifu-tutor`
   - Anti-drift `CLAUDE.md` cleanup.
   - Existing active bugfix files are separate task work; do not mix unless the
     user asks to commit that task.

2. `ripple-suite`
   - `AGENTS.md` Koda/rule hardening.
   - `CLAUDE.md` anti-drift cleanup.
   - Existing ripple hook/skill changes should be reviewed as their own group.

3. `sifututor_tutor`
   - `AGENTS.md` source-of-truth and Koda rule update.
   - `CLAUDE.md` anti-drift cleanup.
   - Active feature files should stay separate from workflow parity commits.

4. `sifututor_parent`
   - New `AGENTS.md`, `.claude/tasks/`, and anti-drift `CLAUDE.md` cleanup.

5. `lls`
   - Standard task workflow migration: `AGENTS.md`, `CLAUDE.md`, hooks,
     settings, task files, and workflow skills.

6. `lls-frontend`
   - New full frontend workflow parity: `AGENTS.md`, `CLAUDE.md`, hooks,
     settings, tasks, and workflow skills.
   - Existing `package-lock.json` change appears unrelated; review before
     staging.

7. `lls-mobile`
   - New `AGENTS.md`, `CLAUDE.md`, `GOALS.md`, `.claude/`, and `.gitignore`
     change allowing workflow files to be tracked.

8. `creative-hub`
   - New `.claude/` baseline and `GOALS.md` update.
   - `AGENTS.md` already exists in the working tree but may be untracked from a
     prior wave; include it if this repo owns the file.

9. `team-inbox`
   - New `AGENTS.md`, `CLAUDE.md`, `GOALS.md`, and `.claude/` baseline.

10. `finch-inbox`
    - `AGENTS.md`/`CLAUDE.md` anti-drift cleanup.
    - `.claude/tasks/` active task pointer.

## Do Not Stage Automatically

Review these before any commit:

- `.claude/.current-session-id`
- `.claude/compact-state-*`
- `.claude/handoffs/`
- `.understand-anything/`
- `graphify-out/`
- unrelated product files already modified before this parity work
- `package-lock.json` changes not caused by an intentional dependency update

## Required Checks Before Any Commit

From the project being committed:

```bash
../scripts/agent-checks/pre-commit-guard.sh
```

Then inspect:

```bash
git status --short
git diff
git diff --staged
```

Ask Hafiz to approve the exact staged file list before committing.
