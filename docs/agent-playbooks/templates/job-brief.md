---
title: Short name of the job, 80 characters or fewer
role: builder                 # builder edits files on its own branch; reviewer is read-only
branch: docs/000-short-name   # builder only: type/lowercase-kebab-description, never main
base: origin/main             # the branch the work starts from
finish: local                 # local | committed | pr-open. Missing means local. merged and deployed are refused
# approval: Hafiz, chat 08/10/2026: push and open the PR   (required when finish is pr-open)
issue: 0                      # GitHub issue number, if there is one
max_usd: 2                    # spend cap per job, 0.5 to 20. Missing means 2
max_turns: 30                 # turn cap, 1 to 100. Missing means 30
max_minutes: 30               # wall-clock limit, 1 to 180. Missing means 30
allowed_paths: docs/agent-playbooks/example.md   # builder only: files or folders it may change, comma separated
# target: feat/265-hook-wiring-template          # reviewer only: the branch on origin to review
---
# Goal

One or two sentences: what must be true when the job is done.

# Why

Who asked for it and what problem it solves. Link the issue.

# What to do

1. The first concrete step.
2. The next step.

# Out of scope

Anything the job must not touch, even if it looks related.

# Proof I expect

The commands to run and what they must show before the job calls itself done.
