# 0001: Run Agent OS on the home PC inside WSL2

Status: Accepted. Decided: 08/10/2026 (MYT), Hafiz.

## Context

Unattended jobs need to run on the home Windows PC while the Mac is closed. The
Agent OS scripts and tests are written for Mac and Linux.

## Decision

Run everything inside Ubuntu on WSL2 on that PC. Do not port Agent OS to native
Windows.

## Why

- Ubuntu on the PC ran the unfixed scripts and the full test suite: 587 tests,
  0 failures (08/10/2026).
- Native Windows has no `fcntl`, a different Python launcher and different shell
  tools. Fixing them costs days and adds Windows-only code.
- Claude Code's sandbox needs WSL2 on Windows.

## What we gave up

- Windows-only tools are not available to jobs.
- Ubuntu is shut down by WSL when nothing is attached (see 0004).
- The repo for jobs lives inside Ubuntu, not in the Windows user folder.

## Revisit if

WSL2 stops working on the PC, or a job needs a Windows-only tool. See
[.out-of-scope/native-windows-agent-os.md](../../.out-of-scope/native-windows-agent-os.md).
