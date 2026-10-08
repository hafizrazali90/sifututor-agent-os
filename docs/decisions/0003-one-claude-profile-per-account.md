# 0003: Keep one Claude profile per account on the PC

Status: Accepted. Decided: 08/10/2026 (MYT), Hafiz.

## Context

The Windows side of the PC already had Claude Code signed in as another person's
account. Hafiz needed his own account there without signing that one out.

## Decision

Use a separate settings folder per account. Work runs in Ubuntu, where Claude
Code is signed in as Hafiz's own account. On Windows, Hafiz's own profile is
started with `claude-hafiz.cmd`, which keeps its login in its own folder. The
other account is left as it was and is not used.

## Why

- A second settings folder keeps two logins side by side without logging either
  out.
- Jobs on the other person's plan would spend their usage and show under their
  name.

## What we gave up

- Two sign-ins to keep track of on one machine.
- The Windows Claude Code is old (version 2.1.94) and could not update over SSH.

## Revisit if

The other account is removed from the PC, or Windows-side Claude Code becomes
part of a job.
