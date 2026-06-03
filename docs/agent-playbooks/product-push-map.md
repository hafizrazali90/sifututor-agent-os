# Product Push Map

Last updated: 2026-05-26

The product repositories below are nested Git repos. Their remotes point to the
`Sifututor` GitHub organization. Hafiz approved the workflow/parity push on
2026-05-26.

The umbrella workflow repo is separate:

- `/Users/hafizrazali/Projects/Sifututor`
- Remote: `https://github.com/hafizrazali90/sifututor-agent-os.git`
- Purpose: shared AI workflow docs/scripts only

## Current Product Push State

| Project | Remote | Current branch | Local state |
| --- | --- | --- | --- |
| `sifu-tutor` | `https://github.com/Sifututor/sifu-tutor.git` | `sifu-staging` | pushed; still has local uncommitted QA/product files |
| `ripple-suite` | `https://github.com/Sifututor/ripple-suite.git` | `main` | pushed after rebase over remote workflow-template commit; local session artifacts ignored |
| `sifututor_tutor` | `https://github.com/Sifututor/sifututor_tutor.git` | `feat/tut-auth-firstrun-rebuild` | pushed and upstream set; local agent artifacts ignored |
| `sifututor_parent` | `https://github.com/Sifututor/sifututor_parent.git` | `chore/phase4-staging-config` | pushed and upstream set |
| `lls` | `https://github.com/Sifututor/lls.git` | `main` | pushed; local memory artifacts ignored |
| `lls-frontend` | `https://github.com/Sifututor/lls-frontend.git` | `main` | pushed; local `package-lock.json` remains modified |
| `lls-mobile` | `https://github.com/Sifututor/lls-mobile.git` | `main` | pushed after rebase over remote workflow-template commit |
| `creative-hub` | `https://github.com/Sifututor/creative-hub.git` | `main` | pushed after rebase over remote work |
| `team-inbox` | `https://github.com/Sifututor/team-inbox.git` | `main` | local main now matches origin/main; stale workflow commit preserved on `backup/team-inbox-stale-parity-20260526` |
| `finch-inbox` | `https://github.com/Sifututor/finch-inbox.git` | `main` | pushed after rebase over remote webhook fix |

## Commands Used / Still Relevant

The approved push has already been performed for all projects except
`team-inbox`. Do not run the `team-inbox` push below without a fresh decision,
because the remote has diverged heavily.

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
- `team-inbox` stale local parity commit is archived on backup branch
  `backup/team-inbox-stale-parity-20260526`; do not push that branch unless
  intentionally reviewing/recovering the old baseline.
