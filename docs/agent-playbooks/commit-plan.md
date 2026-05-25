# Parity Commit Ledger

Last updated: 2026-05-26

The umbrella directory is the private GitHub repo
`hafizrazali90/sifututor-ai-workspace`. It tracks shared workspace files only:
root `AGENTS.md`, `README.md`, `docs/agent-playbooks/`,
`scripts/agent-checks/`, and `.gitignore`.

Product repositories are nested independent Git repos. Workflow parity commits
were made locally in those repos, but product repos were not pushed.

## Umbrella Repo

Pushed to `hafizrazali90/sifututor-ai-workspace`:

- `0574378 chore(workspace): initialize ai workflow repo`
- `f6d95f3 docs(workspace): update project commit plan`

## Local Product Workflow Commits

These commits are local and need explicit approval before pushing.

| Project | Branch | Local workflow commit(s) |
| --- | --- | --- |
| `sifu-tutor` | `sifu-staging` | `dee189a98` point Claude rules to Agents; `32c730c9a` fix Sifu session and commit skills |
| `ripple-suite` | `main` | `ae4fd56` align shared agent rules; `504e26f` strengthen Ripple workflow automation |
| `sifututor_tutor` | `feat/tut-auth-firstrun-rebuild` | `b4de3a2` align tutor agent docs; `20af12c` align hooks/tracking; `05434c1` add review and release skills |
| `sifututor_parent` | `chore/phase4-staging-config` | `1df2d04` add parent app agent workflow |
| `lls` | `main` | `f4641f8` add standard agent task state |
| `lls-frontend` | `main` | `12892ab6` add frontend agent workflow |
| `lls-mobile` | `main` | `ff89d35` add mobile agent baseline |
| `creative-hub` | `main` | `76034a6` add creative hub agent baseline |
| `team-inbox` | `main` | `1be3af5` add team inbox agent baseline |
| `finch-inbox` | `main` | `8498194` add shared agent task pointer |

## Intentionally Left Uncommitted

These are not parity commits and should not be staged blindly.

### `sifu-tutor`

- Active QA/bugfix work: controller/service/test/documentation changes.
- `.claude/tasks/bugfix-20260524-4023.json` belongs to the active ST-40 bugfix.
- `.claude/browser-test.yaml` is a large QA-suite update tied to current
  staging validation.
- `.claude/memory/MEMORY.md` is fast-moving local/Koda context.

### `ripple-suite`

- `.claude/.current-session-id`, `compact-state-*`, `handoffs/`,
  `.understand-anything/`, and `graphify-out/` are local/generated artifacts.
- `.claude/tasks/archive/*` and task JSON files are historical/session state.
- `.claude/memory/MEMORY.md` is fast-moving local/Koda context.
- `scripts/retry-stuck-sync.ts` is a one-off ops script and should be reviewed
  separately before any commit.

### `sifututor_tutor`

- Auth first-run product files, screens, components, images, Maestro flows, and
  PRD/QA docs are active feature work.
- `.taskmaster/`, `.claude/.current-session-id`, `.claude/plans/`, and
  `.claude/memory/` are local/session state.
- `config/devConfig.ts` has QA-only state; confirm `USE_MOCK_DATA` before any
  product commit.

### `sifututor_parent`

- Untracked `e2e/` is product QA work and should be reviewed separately.

### `lls`

- `.claude/memory/` contains local memory index content, including operational
  references. Do not commit without a credential/sensitivity review.

### `lls-frontend`

- `package-lock.json` is modified and unrelated to parity work unless a
  dependency change is intentionally approved.

## Required Checks Before Any Product Repo Commit

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

Ask Hafiz to approve the exact staged file list before pushing any product
repository.
