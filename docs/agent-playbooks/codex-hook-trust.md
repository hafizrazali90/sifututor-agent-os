# Codex Hook Trust Guide

Use this when Codex asks you to review or trust project hooks through `/hooks`.

## What To Trust

For this workspace, expected project hooks live in:

```text
.codex/config.toml
```

Expected commands:

```text
python3 /Users/hafizrazali/Projects/Sifututor/scripts/agent-checks/codex-pre-tool-use.py
python3 /Users/hafizrazali/Projects/Sifututor/scripts/agent-checks/codex-post-tool-use.py
python3 /Users/hafizrazali/Projects/Sifututor/scripts/agent-checks/codex-lifecycle-hook.py
```

## What They Do

| Hook | Purpose |
| --- | --- |
| `SessionStart` | Adds startup project/task context and verifies Koda read/write health |
| `UserPromptSubmit` | Dispatches the right Codex workflow skill and injects Koda context when safe |
| `PreToolUse` | Blocks unsafe Bash patterns and runs the shared guard before commit |
| `PostToolUse` | Logs failed Bash commands to `~/.codex-friction.log` |
| `PreCompact` | Reminds Codex to snapshot or save |
| `Stop` | Reminds Codex to run `$save-session` after meaningful work |

## Koda Startup Gate

`SessionStart` must verify Koda before normal work:

- `KODA_API_KEY` is present, without printing the value
- Codex `memory` MCP points to `https://koda.tutorla.tech/mcp`
- `bearer_token_env_var` is `KODA_API_KEY`
- Koda MCP initializes and returns a session id
- required tools exist: `memory_search`, `memory_store`, `memory_context`, `session_start`
- read check passes via `memory_search`
- write check passes by storing or updating a small `koda-health` sentinel memory

If Koda fails, Codex must fix Koda before non-trivial Sifututor work. Check it
manually with:

```bash
python3 scripts/agent-checks/codex-lifecycle-hook.py --check-koda
```

## What Not To Trust

Do not trust a hook if it:

- points outside `/Users/hafizrazali/Projects/Sifututor/scripts/agent-checks/`
- reads `.env` files or secrets
- pushes, deploys, commits, or mutates repos by itself
- uses `curl`/network calls other than the Koda memory helper behavior
- hides errors by modifying files silently

## Trust Workflow

1. Run `/hooks` in Codex.
2. Review each changed hook command.
3. Confirm it matches the expected command list above.
4. Trust only the expected hooks.
5. Run `$quick-check` after trusting.

The hooks are guardrails and workflow reminders. They do not replace human
approval for commit, push, deploy, merge, or PR actions.
