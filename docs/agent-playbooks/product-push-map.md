# Product Push Map

Last updated: 2026-05-26

The product repositories below are nested Git repos. Their remotes point to the
`Sifututor` GitHub organization. Do not push them without explicit approval in
the current session.

The umbrella workflow repo is separate:

- `/Users/hafizrazali/Projects/Sifututor`
- Remote: `https://github.com/hafizrazali90/sifututor-ai-workspace.git`
- Purpose: shared AI workflow docs/scripts only

## Current Product Push Targets

| Project | Remote | Current branch | Local state |
| --- | --- | --- | --- |
| `sifu-tutor` | `https://github.com/Sifututor/sifu-tutor.git` | `sifu-staging` | ahead of `origin/sifu-staging` by 2 commits |
| `ripple-suite` | `https://github.com/Sifututor/ripple-suite.git` | `main` | ahead of `origin/main` by 6 commits |
| `sifututor_tutor` | `https://github.com/Sifututor/sifututor_tutor.git` | `feat/tut-auth-firstrun-rebuild` | local branch, no upstream shown |
| `sifututor_parent` | `https://github.com/Sifututor/sifututor_parent.git` | `chore/phase4-staging-config` | local branch, no upstream shown |
| `lls` | `https://github.com/Sifututor/lls.git` | `main` | ahead of `origin/main` by 1 commit |
| `lls-frontend` | `https://github.com/Sifututor/lls-frontend.git` | `main` | ahead of `origin/main` by 1 commit |
| `lls-mobile` | `https://github.com/Sifututor/lls-mobile.git` | `main` | ahead of `origin/main` by 1 commit |
| `creative-hub` | `https://github.com/Sifututor/creative-hub.git` | `main` | ahead of `origin/main` by 1 commit |
| `team-inbox` | `https://github.com/Sifututor/team-inbox.git` | `main` | ahead of `origin/main` by 1 commit |
| `finch-inbox` | `https://github.com/Sifututor/finch-inbox.git` | `main` | ahead of `origin/main` by 1 commit |

## Approval-Safe Push Commands

Use these only after Hafiz explicitly approves product repo pushes.

```bash
git -C sifu-tutor push origin sifu-staging
git -C ripple-suite push origin main
git -C sifututor_tutor push -u origin feat/tut-auth-firstrun-rebuild
git -C sifututor_parent push -u origin chore/phase4-staging-config
git -C lls push origin main
git -C lls-frontend push origin main
git -C lls-mobile push origin main
git -C creative-hub push origin main
git -C team-inbox push origin main
git -C finch-inbox push origin main
```

Before pushing any project, run:

```bash
(cd <project> && ../scripts/agent-checks/pre-commit-guard.sh)
```

Then inspect:

```bash
git -C <project> status --short --branch
git -C <project> log --oneline origin/<branch>..HEAD
```

## Important Caveats

- `sifu-tutor` has active product/QA files still modified.
- `ripple-suite` has local/generated artifacts and a one-off ops script still
  uncommitted.
- `sifututor_tutor` has active auth first-run product work and QA files still
  uncommitted.
- `sifututor_parent` has untracked `e2e/` product QA work.
- `lls` has untracked `.claude/memory/` with operational references.
- `lls-frontend` has an unrelated modified `package-lock.json`.
