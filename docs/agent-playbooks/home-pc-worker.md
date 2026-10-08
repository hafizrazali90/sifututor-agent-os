# Home PC Worker

The home Windows PC runs unattended Claude jobs while Hafiz's Mac is closed.
The Mac is where Hafiz discusses and decides. The PC is where a job runs after
the brief is agreed. This playbook is the owner for how that machine is set up
and used. It holds no passwords, keys or sign-in codes.

Status on 08/10/2026 (MYT): the machine, the repo and the guards are in place.
The job runner, the spend caps and the reviewer role are not built yet, so no
unattended job should run until issues #272 to #275 and #305 are done.

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

## Reaching it from the Mac

- `ssh homepc` opens Windows. Commands for Ubuntu go through
  `wsl -d Ubuntu -u hafiz -e <command>`.
- Windows prints Ubuntu output with extra null bytes. Strip them with
  `tr -d '\000'`.
- Quoting through SSH, Windows and WSL breaks easily. Send a script on standard
  input instead: `ssh homepc 'wsl -d Ubuntu -u hafiz -e sh -s' < script.sh`.
- A job started as a plain SSH child process can die when the connection drops.
  Windows jobs use the Task Scheduler (`schtasks`). Ubuntu jobs will use tmux,
  once the runner exists.

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

- Every job has a brief with a finish state: local, committed, PR-open, merged or
  deployed. A brief without one means local only.
- Every unattended job has a spend cap, a turn cap and a wall-clock limit.
- A job never merges or deploys. It stops at the finish state in its brief.
- The reviewer role reads cold, is read-only, and writes findings to a file.

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
