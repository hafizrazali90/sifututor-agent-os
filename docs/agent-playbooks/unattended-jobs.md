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

## Related

- [home-pc-worker.md](home-pc-worker.md)
- [autonomous-work-packets.md](autonomous-work-packets.md)
- [parallel-work-and-worktrees.md](parallel-work-and-worktrees.md)
- [agent-os-approval-gates.md](agent-os-approval-gates.md)
