# 0002: Give the PC full GitHub access and control it with the job brief

Status: Accepted. Decided: 08/10/2026 (MYT), Hafiz.

## Context

A job that needs a repository or a pull request cannot stop and wait for a
permission nobody is there to grant. The first proposal was a read-only key for
one repository.

## Decision

The PC is signed in to GitHub with repo, workflow and read:org access for
Hafiz's account. What a job may do is controlled by its brief and by the
runner's checks, not by the size of the sign-in.

## Why

- Hafiz does not want work to stop for a missing permission on his own machine.
- A narrow key would need a new key per repository and per finish state.
- The runner never merges or deploys, and for `pr-open` the runner, not Claude,
  pushes and opens the pull request after its checks pass.

## What we gave up

- Anyone who can run code as the Ubuntu user on the PC can use the sign-in. It
  is stored in a file only that user can read.
- The sign-in is broader than any one job needs.

## Revisit if

The PC is shared with other people, a job misbehaves, or GitHub offers a simple
way to give each job only the repository it needs.
