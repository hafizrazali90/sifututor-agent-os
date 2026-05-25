# Parity Commit Plan

Last updated: 2026-05-26

The umbrella directory is now the private GitHub repo
`hafizrazali90/sifututor-ai-workspace`. It tracks shared workspace files only:
root `AGENTS.md`, `README.md`, `docs/agent-playbooks/`,
`scripts/agent-checks/`, and `.gitignore`.

Commit project-owned workflow changes per sub-project repository. Do not mix
product work and workflow parity work in the same commit.

## Recommended Commit Groups

Commit per project, not as one mixed change:

1. `sifu-tutor`
   - Stage: `CLAUDE.md`
   - Existing active bugfix files are separate task work; do not mix unless the
     user asks to commit that task.
   - Do not stage product/test files from the active bugfix.

2. `ripple-suite`
   - Stage: `AGENTS.md`, `CLAUDE.md`
   - Consider a separate workflow-tools commit for hook/skill changes only
     after reviewing the existing uncommitted hook/skill edits.
   - Do not stage `.claude/.current-session-id`, compact states, handoffs,
     `.understand-anything/`, `graphify-out/`, or unrelated scripts.

3. `sifututor_tutor`
   - Stage: `AGENTS.md`, `CLAUDE.md`, `CODEX-WORKFLOW.md` if the branch-pattern
     fix is still unstaged.
   - Active feature files should stay separate from workflow parity commits.
   - Do not stage auth first-run product files, Maestro flows, images,
     `.taskmaster/`, or session scratch files in the parity commit.

4. `sifututor_parent`
   - Stage: `AGENTS.md`, `CLAUDE.md`, `.claude/tasks/`, `.claude/hooks/`,
     `.claude/settings.json` if present and intended.
   - Review `GOALS.md` and `e2e/` before staging; they may be separate work.

5. `lls`
   - Stage: `AGENTS.md`, `CLAUDE.md`, `.claude/hooks/`,
     `.claude/settings.json`, `.claude/tasks/`, and the five `lls-*` workflow
     skills.
   - Review `.claude/memory/` and `GOALS.md` before staging.

6. `lls-frontend`
   - Stage: `AGENTS.md`, `CLAUDE.md`, `.claude/hooks/`,
     `.claude/settings.json`, `.claude/tasks/`, `.claude/skills/`.
   - Do not stage `package-lock.json` unless a dependency change was intended.
   - Review `GOALS.md` before staging.

7. `lls-mobile`
   - New `AGENTS.md`, `CLAUDE.md`, `GOALS.md`, `.claude/`, and `.gitignore`
     change allowing workflow files to be tracked.

8. `creative-hub`
   - New `.claude/` baseline and `GOALS.md` update.
   - `AGENTS.md` is already tracked/clean at last audit.

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
