---
name: commit
description: Use when Hafiz asks Codex to prepare or create a commit in the Sifututor workspace. Must follow docs/agent-playbooks/commit.md, including guard checks, exact file list review, and commit format rules.
---

# Commit

Use this skill when the user asks to commit, prepare a commit, or check whether
the current work is ready to commit.

## Core Rule

Read and follow:

```text
docs/agent-playbooks/commit.md
```

That playbook is the source of truth. Do not bypass it with a simpler git flow.

## Quick Workflow

1. Confirm the user has asked for commit work in the current session.
2. Run the shared guard from the project or umbrella root.
3. Read active task state when present.
4. Review `git status --short`, `git diff`, and `git diff --staged`.
5. Stage only the approved files.
6. Use direct `git commit -m` flags with the required emoji conventional commit
   format.
7. Never push, merge, deploy, open a PR, use `--no-verify`, or commit secrets.

## Human-Facing Alias

When explaining this to Hafiz, describe it as:

```text
Claude: /commit
Codex: $commit
```
