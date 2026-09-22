# CLAUDE.md - Claude Code adapter for the Sifututor umbrella

@AGENTS.md

`AGENTS.md` above is the shared operating contract for every agent and is
loaded here through that import. This file adds only what Claude Code needs
to run inside this workspace. It must not restate a rule that `AGENTS.md` or a
playbook owns. If it ever contradicts them, that is adapter drift: stop and
report the exact conflicting lines instead of picking a side.

## What Claude loads here

At launch Claude Code loads `~/.claude/CLAUDE.md`, this file, and `AGENTS.md`
through the import. Inside a sub-project it still loads this file, because
parent-directory `CLAUDE.md` files are concatenated.

It does not load, unless a file is opened: sub-project `AGENTS.md` and
`CLAUDE.md` from the umbrella cwd (`CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD`
stays unset by decision), `docs/agent-playbooks/`, `.agents/skills/`, or skill
bodies. Read the project `AGENTS.md` before editing inside a project, as the
contract says. Loading rules per model and how they were verified live in
[doc-routing-and-context-loading.md](docs/agent-playbooks/doc-routing-and-context-loading.md).

## Starting a chat

- Declare the project in the first message (`sifu-tutor work - ...`).
  Dispatcher skills (`/task-router`, `/verify`, `/qa`, `/commit`,
  `/save-session`) accept an explicit project argument such as
  `/save-session ripple-suite` and otherwise infer it from the conversation.
- Launch the session inside the sub-project for heavy commit cycles. Project
  hooks (`workflow-gate`, `quality-gate`, `memory-flush`, `session-start`) bind
  to the launch cwd; umbrella-launched sessions survive through the shared
  dispatcher described in
  [agent-os-hook-dispatcher.md](docs/agent-playbooks/agent-os-hook-dispatcher.md).
- Read `GOALS.md` here and in the project when the task needs current focus.

## Claude mechanics in this workspace

- Parent hooks from `.claude/settings.json`: approval guard, secret-output
  guard, branch-name and conventional-commit validators, test-coverage gate,
  and the Koda context injector. Owner:
  [agent-os-hook-dispatcher.md](docs/agent-playbooks/agent-os-hook-dispatcher.md).
- `.claude/settings.local.json` denies Edit and Write under `live/` and
  `.workflow-rollout/`. Bash is not pattern-blocked there, so the `live/` rule
  in `AGENTS.md` still applies to shell commands.
- MCP servers come from the parent `.mcp.json`; Koda is the `memory` server.
  If the Koda MCP is missing, use `scripts/agent-checks/koda`; never ask for
  `KODA_API_KEY`. Memory rules:
  [agent-os-memory.md](docs/agent-playbooks/agent-os-memory.md).
- `.claude/tasks/active.json`, project slash commands (`/sifu-commit`,
  `/ripple-qa`, ...), and Claude hooks are adapter helpers, not the Agent OS.
  Do not require them for discussion, explanations, or save-session, and do not
  invent gate fields such as `gate4_evidence` unless the project task file uses
  them. Shared workflows are `/save-session`, `$save-session`, or the plain
  request, all following the shared playbook.
- Plane is exception-only and Planner is read-only intake; `AGENTS.md` owns
  both rules.
- Naming: write `Sifututor` in prose; keep literal casing for identifiers.

## Find the right document

[doc-owner-route-index.md](docs/agent-playbooks/doc-owner-route-index.md) is
the shelf map and [task-router.md](docs/agent-playbooks/task-router.md) picks
the route. After changing this file, `AGENTS.md`, the index, or the routing
matrix, run `scripts/agent-checks/agent-os-doc-navigation-check.py`.
