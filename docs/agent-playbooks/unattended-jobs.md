# Unattended Jobs On The Home PC

Use this when Hafiz has agreed a piece of work in a discussion and it should
finish while his Mac is closed. The Mac writes a brief; the home PC runs it with
Claude; the Mac reads the result. Machine facts are in
[home-pc-worker.md](home-pc-worker.md). The runner is `scripts/agent-checks/pc_job.py`.

## The flow

1. Write a brief from `templates/job-brief.md`. Hafiz agrees the finish state.
2. `python3 scripts/agent-checks/pc_job.py submit brief.md` checks the brief,
   copies it and the runner to the PC, and starts the job.
3. The PC re-checks the brief, makes its own git worktree, builds the hook
   wiring, runs Claude until it finishes, then checks what Claude did.
4. `status JOB_ID`, `result JOB_ID` and `list` read the files the job writes.
   Close the laptop in between; the job does not need the Mac.

`submit --dry-run` validates and prints the plan without touching the PC.

## Roles

- **builder** works on its own branch and may change only `allowed_paths`.
- **reviewer** is read-only and reads a branch on origin cold. Its verdict is
  ACCEPT, CHANGES NEEDED or BLOCKED.
- Both get the same facts and safety rules from `job-roles/shared-facts.md`.
  Only the stance differs (`builder.md`, `reviewer.md`).

## Rules (issues #272, #273, #274)

| Rule | What happens |
| --- | --- |
| No caps | Jobs run on Hafiz's Claude subscription exactly as a session on the Mac does: no spend, turn or time cap (Hafiz, 09/10/2026: "never cap"). A brief with a `max_usd`, `max_turns` or `max_minutes` line is refused so the line gets deleted. |
| Finish state | `local`, `committed` or `pr-open`. Missing means `local`. |
| `merged`, `deployed` | Refused. An unattended job cannot merge or deploy. |
| `pr-open` | Needs an `approval` line. The runner, not Claude, pushes and opens the pull request, and only after its checks pass. |
| Guards | The job refuses to start Claude unless the hook wiring was built from `.claude/settings.template.json`. |
| Git identity | A job that must commit stops before Claude starts if git has no author identity. |
| Permissions | Claude never runs with permissions skipped. Anything not on the tool list is denied, because nobody can answer a prompt. |
| Project repo `repo` | Optional (issue #347). Missing means the Agent OS repo. Allowed values are listed in `PROJECT_REPOS` in `job_brief.py`; today only `ripple-suite`. The repo must already be cloned on the PC under `~/Projects/Sifututor/<repo>`. The job worktree installs packages with `npm ci` from the lockfile, the guards come from the project's own tracked `.claude/settings.json`, and the builder may also run `npx vitest`, `npx tsc`, `npx eslint` and the umbrella commit guard by its full path. `base`, `branch` and `allowed_paths` are read inside that repo. |

## What the runner checks after Claude finishes

- A builder changed only files inside `allowed_paths`, or the job is `blocked`
  and nothing is pushed.
- A job that must commit made a commit and left a clean tree.
- A reviewer changed no file.
- A failed or blocked job says so in `status.json` and `result.md`.

## Files a job leaves, in `~/jobs/JOB_ID/` on the PC

`brief.md`, `status.json`, `result.md`, `result.json`, `claude-output.json`,
`runner.log`. States: queued, preparing, running, checking, finishing, then one
of done, failed, blocked or timeout. Times are shown in MYT.

## What was measured on 08/10/2026

- The Ubuntu machine shuts down when no Windows process is attached, and that
  kills tmux. A job started through Task Scheduler with `wsl.exe` keeps it alive.
  This is why the runner uses Task Scheduler.
- Caps were tried first and removed on 09/10/2026: the jobs run on the
  subscription, so a cap only stops real work half way.
- First real jobs: a builder changed one file and committed it in 21 seconds
  for $0.22 (10 turns); a reviewer read the hook template branch cold in 78
  seconds for $0.48 and found real test weaknesses. The first attempt was
  blocked because the PC had no git identity, and the runner caught it.

## Limits to know

- Jobs run only while Windows is on and Hafiz is signed in, because the
  scheduler task runs as him. A restart or sign-out stops a running job; its
  `status.json` then stays on `running`.
- There is no queue. Start one job at a time; two at once share the PC and the
  usage limit.
- The reviewer can read files and run `git diff`, `git log`, `git show`. It
  cannot run tests. Ask a builder job to run tests and put them in its result.
- A job cannot read Koda until the PC has its own Koda access (issue #271).

## Housekeeping

- Job worktrees stay under `~/.local/state/sifututor-agent-os/worktrees/job-*`
  until someone closes them with `worktree-lifecycle.py`. Do not delete them by
  hand.
- If the scheduler task of a finished job is still listed, `schtasks /delete
  /tn job-JOB_ID /f` removes it.

## Release readiness loop (issue #350)

A single job does one task and stops. The release readiness loop chains the
jobs for one release by itself, on the PC, and stops only when everything that
comes before the final production go is done and proven. Then it tells Hafiz
"ready for your go" with a plain report. Hafiz's request (09/10/2026): "i want
the pc can be able to proceed until prod release readiness is 100%".

### What 100% means

Two numbers for every release, kept apart on purpose:

- **PC readiness:** green items divided by applicable items whose owner is
  `pc`. At 100 percent the loop stops with status `ready`.
- **Your gates:** items owned by `hafiz` or `mac`. They are listed, never
  counted into PC readiness, and the PC never does them: review page confirmed,
  migration or data approval (when item 8 lists any), merge, production deploy
  go, production smoke, production monitoring window, accepted and closed.

An item that does not apply is marked `na` with a reason (for example item 4
"failing-first evidence" for a docs-only release). It leaves the denominator.

### The checklist

The default is `templates/release-readiness.json`, derived from
[release-deploy-live-monitoring.md](release-deploy-live-monitoring.md),
`AGENTS.md` "Build, Evidence, And Release", [test-coverage.md](test-coverage.md)
and [release-documentation.md](release-documentation.md).

| # | Item | How the PC proves it |
| --- | --- | --- |
| 1 | Scope, who is affected, business-rule IDs, acceptance example | builder job drafts it, headings checked |
| 2 | Release source: open PR naming the exact commit; built on the serving commit | script (`gh pr view`, `git merge-base`) |
| 3 | Cold review returned ACCEPT | reviewer job; CHANGES NEEDED goes to a builder fix, then a fresh reviewer |
| 4 | Failing-first: each new test fails on the base and passes on the release | script: the loop copies the release's tests onto the merge base and runs them there |
| 5 | Suite: the project's lint, type-check and unit tests | script, real exit codes; a failure becomes a builder fix job |
| 6 | Browser or E2E run, or a named exception | script commands, or the exception from `AGENTS.md` |
| 7 | Coverage and staff documentation decision | script (`release_documentation.py --mode blocking`) |
| 8 | Migrations with rollback (or "none"), flags, data changes | builder drafts it, never runs a migration |
| 9 | Deploy plan: exact commands, who runs each, in order | builder drafts it, never runs a command |
| 10 | Smoke and monitoring plan | builder drafts it |
| 11 | Review page draft, business and technical side by side | builder drafts it |
| 12 | Release notes draft | builder drafts it |

Drafts land in `release-pack/` next to the checkpoint. Screenshots of UI changes
are listed as "still needed" because the PC cannot take them.

### What the PC will never do

- Merge, deploy, run a migration, or write production data. An item whose check
  or instruction would do any of these (`gh pr merge`, `git push` to main,
  `artisan migrate`, a deploy script, `ssh`, a database client, a write call)
  is not run: the loop moves it to your gates and carries on.
- Push anywhere except a fast-forward of fix commits to the release branch, and
  only when the readiness file has an `approval` line. Without one, a fix stays
  on the PC and the item blocks.
- Read an environment file or a key file, or print a secret. Command output is
  masked before it is stored.

### How the loop works

A plain deterministic loop
([autonomous-work-packets.md](autonomous-work-packets.md), "Prefer a plain
loop"): score, pick the next open PC item whose dependencies are green, run its
action, record evidence, save the checkpoint, repeat. One Claude job at a time,
finish state `local` or `committed` only. Every action ends with an atomic save
of `readiness.json`, and the in-flight action is written before it starts, so a
restart resumes exactly and re-runs only the action that was cut off. A pushed
fix changes the release commit, so proof taken on the old commit (script and
review items) is reset and checked again on the new one.

There is no spend, turn or time cap anywhere. The only things that end a run
are stop conditions:

| Status | When | What you do |
| --- | --- | --- |
| `ready` | PC readiness is 100 percent | Read `release-report.md` and the review page draft, then decide on the gates |
| `blocked` | the same item failed or was blocked twice; or nothing can run (an item waits on a gate or is blocked); or fixes keep resetting the same item three times | Read the reason in the report. Fix the cause (or do the item by hand with `release_readiness.py mark`), then `mark ... --status open --reset-failures` and `resume` |
| `stuck` | two rounds in a row with no change in score and no new evidence | Look at the last events in `readiness.json` (`loop.events`); the job is probably changing nothing. Change the item or mark it by hand, then `resume` |
| `stopped` | a `STOP` file next to the checkpoint | `resume` when ready; the stop takes effect after the current action, or at once for a running command |

### Start, read and stop it (from the Mac)

```bash
# 1. write the readiness file (--na ITEM=reason for items that do not apply)
python3 scripts/agent-checks/release_readiness.py init --release "Ripple CX audit" \
  --repo ripple-suite --branch release/1630-cx-audit --pr 1630 --issue 1630 \
  --serving-commit <sha from .serving-prod.json> \
  --approval "Hafiz, chat DD/MM/YYYY: push fixes to the release branch" \
  --e2e-exception "tooling unavailable: no app on the PC" --out readiness.json
# 2. check it, then start it
python3 scripts/agent-checks/pc_release.py start readiness.json --dry-run
python3 scripts/agent-checks/pc_release.py start readiness.json
# 3. read it (RELEASE_ID is printed by start)
python3 scripts/agent-checks/pc_release.py status RELEASE_ID
python3 scripts/agent-checks/pc_release.py report RELEASE_ID
python3 scripts/agent-checks/pc_release.py file RELEASE_ID release-pack/11-review-page.md
# 4. stop or continue
python3 scripts/agent-checks/pc_release.py stop RELEASE_ID
python3 scripts/agent-checks/pc_release.py resume RELEASE_ID
```

The loop is started through Task Scheduler exactly like a job (WSL kills
detached processes). Files live in `~/releases/RELEASE_ID/` on the PC:
`readiness.json` (the checkpoint), `release-report.md`, `ready.flag`,
`release-pack/`, `jobs/` (one folder per Claude job), `loop.log`.

### Limits to know

- One loop per release folder (a lock refuses a second one). Do not run two
  releases at once; they share the PC and the usage limit.
- The reviewer cannot run tests, so the suite is run by the loop itself.
- The loop proves the PC side only. Browser E2E on a real app, screenshots, the
  review page confirmation, merge, deploy, production smoke and monitoring stay
  with you.
- `blocked` after one fix attempt is deliberate: a second failure of the same
  item means a person should look.

## Related

- [home-pc-worker.md](home-pc-worker.md)
- [autonomous-work-packets.md](autonomous-work-packets.md)
- [release-deploy-live-monitoring.md](release-deploy-live-monitoring.md)
- [parallel-work-and-worktrees.md](parallel-work-and-worktrees.md)
- [agent-os-approval-gates.md](agent-os-approval-gates.md)
