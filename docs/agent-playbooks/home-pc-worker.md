# Home PC Worker

The home Windows PC runs unattended Claude jobs while Hafiz's Mac is closed.
The Mac is where Hafiz discusses and decides. The PC is where a job runs after
the brief is agreed. This playbook is the owner for how that machine is set up
and used. It holds no passwords, keys or sign-in codes.

Status on 08/10/2026 (MYT): the machine, the repo, the guards and the job
runner are in place. How to run a job is in
[unattended-jobs.md](unattended-jobs.md). Koda access from the PC is not done
yet (issue #271).

## The machine

- A Windows 11 PC at home with Ubuntu 26.04 inside it (WSL2). Work happens in
  Ubuntu, not in Windows. Windows has no `fcntl` and other Linux tools; Ubuntu
  does, and the Agent OS scripts run there unchanged.
- It is reached over Tailscale. Both the Mac and the PC must be signed in to the
  same Tailscale account, or they cannot see each other.
- Windows is kept awake: sleep and hibernate are off while plugged in.
- Ubuntu has Python 3, git, Node.js 22 (the Claude hook dispatcher is a Node
  script), the GitHub CLI and Claude Code. npm is not installed.
- The repo is cloned at `~/Projects/Sifututor` inside Ubuntu.
- Checked on 09/10/2026 (MYT): Ubuntu has Python 3.14.4 and Node.js v22.22.1, and the GitHub CLI is signed in as `hafizrazali90`.

## Reaching it from the Mac

- `ssh homepc` opens Windows. Commands for Ubuntu go through
  `wsl -d Ubuntu -u hafiz -e <command>`.
- Windows prints Ubuntu output with extra null bytes. Strip them with
  `tr -d '\000'`.
- Quoting through SSH, Windows and WSL breaks easily. Send a script on standard
  input instead: `ssh homepc 'wsl -d Ubuntu -u hafiz -e sh -s' < script.sh`.
- A job started as a plain SSH child process can die when the connection drops.
  Ubuntu shuts down when no Windows process is attached, which also kills tmux.
  Every job, Windows or Ubuntu, is started through the Task Scheduler
  (`schtasks`) so a Windows-side process keeps the machine alive.

## Accounts

- Ubuntu's Claude Code is signed in as Hafiz's own account. Use it for all work.
- Windows also has an older Claude Code signed in as another person's account.
  Do not use it. Hafiz's own Windows profile is `claude-hafiz.cmd`, which keeps
  its login in a separate folder.
- GitHub on the PC is signed in with repo, workflow and read:org access. Anyone
  who can run code as the Ubuntu user can use it. The brief, not the sign-in,
  controls what Claude may do.
- Sign-in codes never go into chat. Hafiz pastes them into a terminal on the PC.

## Hooks on the PC

- Claude's hook wiring is not in git. Build it from the tracked template with
  `python3 scripts/agent-checks/render-claude-settings.py --apply` (see
  [agent-os-hook-dispatcher.md](agent-os-hook-dispatcher.md)).
- Checked on 08/10/2026: with the generated file, a harmless command is allowed,
  reading a repository `.env` file is denied by the secret guard, and an invalid
  branch name is denied by the branch hook.
- Koda access from the PC is a separate approved credential step and is not done
  yet.

## Rules for a job on the PC

- The rules for briefs, finish states and roles are in
  [unattended-jobs.md](unattended-jobs.md). In short: every job has a brief and
  runs until Claude finishes, with no caps, as on the Mac; a missing finish
  state means local only; a job never merges or deploys.

## Known gotchas

- Test branches need a `type/description` name, such as `chore/test-check`. A
  branch named `test` or a detached HEAD makes some Agent OS tests fail.
- Without Node.js, two hook dispatcher tests fail. With Node.js 22 the whole
  suite passes (587 tests on 08/10/2026).
- On Linux `stat -f` prints file-system status. File-mode checks must try
  `stat -c '%a'` first (see issue #269).

## Related

- [agent-os-hook-dispatcher.md](agent-os-hook-dispatcher.md)
- [parallel-work-and-worktrees.md](parallel-work-and-worktrees.md)
- [autonomous-work-packets.md](autonomous-work-packets.md)
- [agent-access-map.md](agent-access-map.md)

## Koda on the PC (one step only Hafiz can do)

Claude on the PC needs the Koda key, which Hafiz owns. In an Ubuntu terminal on the PC, in the repo folder, run:

```bash
scripts/agent-access/setup-pc-koda.sh
```

It asks for the key twice with echo off, saves it in `~/.config/sifututor/koda-key.conf` (mode 600), adds one line to `~/.bashrc` so every shell loads it, creates a Koda-only `.mcp.json` in the repo if none exists, and finishes with Koda's read-only health check, printing only PASS or FAIL. Open a new Ubuntu shell afterwards. An agent must never run this script or see what is typed. Tests: `scripts/agent-checks/test_setup_pc_koda.py`.

## Last verified run on the PC (08/10/2026, #270)

| Item | Result |
|------|--------|
| Where | Home PC, Ubuntu on WSL2 (`Linux 6.6.87.2-microsoft-standard-WSL2 x86_64`), Python 3.14.4 |
| Repo | `main` at `4c37c95` (after PR 337) |
| Command | `python3 -m unittest discover -s scripts/agent-checks -p "test_*.py"` |
| Result | 780 tests, OK, 1 skipped, exit code 0, 26 seconds |
| Doc navigation check | 22 of 22 evaluated checks passed |
| First run, same day | 44 failures of one new test (`test_every_entry_points_to_a_skill_that_exists`), because the PC had none of the global skills. Fixed by copying `~/.claude/skills` (48 skills, no trash or vendor sync folders) and the global `CLAUDE.md` from the Mac; the rerun passed |

The failing first run is the useful lesson: a test that checks the global skills exists will fail on any machine that lacks them, so a new machine needs the skills and `CLAUDE.md` copied first. Command used to copy (from the Mac):

```bash
cd ~/.claude && COPYFILE_DISABLE=1 tar --exclude='.trash' --exclude='synced' --exclude='.DS_Store' -cf - skills CLAUDE.md \
  | ssh homepc "wsl.exe -d Ubuntu -u hafiz -e tar -C /home/hafiz/.claude -xf -"
```

To rerun the suite on the PC without it being killed when the SSH session ends, start it through Task Scheduler (WSL stops detached processes): write the commands to `~/jobs/pc-tests/start.sh` in Ubuntu, then `schtasks /create /tn "job-pc-tests" /tr "wsl.exe -d Ubuntu -u hafiz -e /home/hafiz/jobs/pc-tests/start.sh" /sc once /st 00:00 /f & schtasks /run /tn "job-pc-tests"`, and read `~/jobs/pc-tests/report.txt`.
