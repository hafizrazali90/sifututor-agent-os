# 0004: Start every PC job through Task Scheduler

Status: Accepted. Decided: 08/10/2026 (MYT), Claude, from a measurement; reported to Hafiz.

## Context

The obvious way to keep a job alive after the Mac disconnects is tmux inside
Ubuntu. It did not survive.

## Decision

Each job is started by a one-time Windows Task Scheduler task that runs
`wsl.exe` on the job's start script. The task is deleted when the job ends.

## Why

- Test on 08/10/2026: a tmux loop started over SSH was gone about 100 seconds
  after the connection closed. Ubuntu had restarted, with an uptime of 1 second.
  WSL shuts the Ubuntu machine down when no Windows process is attached.
- A scheduler task keeps a Windows-side `wsl.exe` running for the whole job.
  The same test with a 150 second job ran all 30 steps and finished, with the
  Mac disconnected.

## What we gave up

- Jobs run only while Windows is on and Hafiz is signed in. A restart or sign-out
  stops a running job, and its status file stays on `running`.
- There is no queue and no automatic restart.

## Revisit if

Windows or WSL changes how idle machines are handled, or we need jobs to survive
a restart (for example with a service that starts at boot).
