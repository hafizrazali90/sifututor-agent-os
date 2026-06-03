# Parity Commit Ledger

Last updated: 2026-05-26

The umbrella directory is the private GitHub repo
`hafizrazali90/sifututor-agent-os`. It tracks shared workspace files only:
root `AGENTS.md`, `README.md`, `docs/agent-playbooks/`,
`scripts/agent-checks/`, and `.gitignore`.

Product repositories are nested independent Git repos. Hafiz approved product
repo pushes on 2026-05-26. Most workflow parity commits are now pushed to the
`Sifututor` GitHub organization.

## Umbrella Repo

Pushed to `hafizrazali90/sifututor-agent-os`:

- `0574378 chore(workspace): initialize ai workflow repo`
- `f6d95f3 docs(workspace): update project commit plan`
- `9a9ca31 docs(workspace): refresh parity commit ledger`
- `3a6eba7 docs(workspace): add product push map`
- `f928701 docs(workspace): record product push results`

## Pushed Product Workflow Commits

These commits were pushed after explicit approval. Some hashes changed during
safe rebases over newer remote workflow-template commits.

| Project | Branch | Pushed commit(s) |
| --- | --- | --- |
| `sifu-tutor` | `sifu-staging` | `dee189a98` point Claude rules to Agents; `32c730c9a` fix Sifu session and commit skills; note: existing product fix `d90d14ce4` was also on the branch head and pushed with `sifu-staging` |
| `ripple-suite` | `main` | `e243f13` align shared agent rules; `87cae49` strengthen Ripple workflow automation |
| `ripple-suite` | `main` | `4d84112` ignore local agent artifacts |
| `sifututor_tutor` | `feat/tut-auth-firstrun-rebuild` | `b4de3a2` align tutor agent docs; `20af12c` align hooks/tracking; `05434c1` add review and release skills; `4764b17` ignore local agent artifacts |
| `sifututor_parent` | `chore/phase4-staging-config` | `1df2d04` add parent app agent workflow |
| `lls` | `main` | `f4641f8` add standard agent task state; `8c4050a` ignore local agent artifacts |
| `lls-frontend` | `main` | `12892ab6` add frontend agent workflow |
| `lls-mobile` | `main` | `e959382` add mobile agent baseline |
| `creative-hub` | `main` | `d7b9e32` add creative hub agent baseline |
| `finch-inbox` | `main` | `efeb002` add shared agent task pointer |

## Team Inbox

`team-inbox` was not pushed. Its stale local workflow commit was preserved on
backup branch `backup/team-inbox-stale-parity-20260526`, then local `main` was
aligned to `origin/main`.

Reason: local `main` was ahead by 1 old workflow commit but behind remote `main`
by 344 commits. The remote has evolved into the newer Finch-style codebase and
already contains a GitHub-workflow `AGENTS.md`. Pushing the stale local Team
Inbox baseline onto that remote would be risky and likely wrong.

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
  `.understand-anything/`, and `graphify-out/` are now ignored local/generated
  artifacts.
- `.claude/tasks/archive/*` and task JSON files are historical/session state.
- `.claude/memory/MEMORY.md` is fast-moving local/Koda context.
- `scripts/retry-stuck-sync.ts` is a one-off ops script and should be reviewed
  separately before any commit.

### `sifututor_tutor`

- Auth first-run product files, screens, components, images, Maestro flows, and
  PRD/QA docs are active feature work.
- `.taskmaster/`, `.claude/.current-session-id`, `.claude/plans/`, and
  `.claude/memory/` are now ignored local/session state.
- `config/devConfig.ts` has QA-only state; confirm `USE_MOCK_DATA` before any
  product commit.

### `sifututor_parent`

- Untracked `e2e/` is product QA work and should be reviewed separately.

### `lls`

- `.claude/memory/` contains local memory index content, including operational
  references. It is now ignored.

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
