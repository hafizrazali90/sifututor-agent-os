# Running Agent OS on native Windows

## What was proposed

Run Agent OS directly on the home Windows PC, with PowerShell or Git Bash, and
fix the scripts so they work there.

## Why it is out of scope

- The scripts and tests are written for Mac and Linux: file locking with
  `fcntl`, `python3`, GNU or BSD shell tools, `/bin/zsh`.
- Ubuntu on WSL2 on the same PC runs everything unchanged. The full test suite
  passed there (587 tests, 0 failures, 08/10/2026) once Node.js was installed.
- Claude Code's sandbox is not supported on native Windows; it needs WSL2.
- The fixes would cost days and add Windows-only code paths to maintain. One
  such fix, a portable file lock (issue #267), was built and then parked because
  Ubuntu does not need it.

## What would change our mind

WSL2 becoming unusable on the PC (it cannot start, or Hafiz must run Windows
only), or a job that truly has to use a Windows-only tool.

## Decided

08/10/2026 (MYT), Hafiz: run Agent OS inside Ubuntu on WSL2.
