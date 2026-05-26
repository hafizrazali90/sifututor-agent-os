# Shared Agent Playbooks

These playbooks translate the Claude skill workflow into plain Markdown that
Codex, Claude, and future agents can all read. Claude still owns the executable
`.claude/skills/*/SKILL.md` commands. These files are the shared reference when
an agent needs the same workflow but cannot invoke Claude skills directly.

Use these when the user asks for:

- task routing or session start: [task-router.md](task-router.md)
- verification or Gate 2A: [verify.md](verify.md)
- QA or regression evidence: [qa.md](qa.md)
- staging and committing: [commit.md](commit.md)
- saving knowledge at the end of work: [save-session.md](save-session.md)
- handoff to another agent or human: [handoff.md](handoff.md)
- context snapshot before switching or compaction: [snapshot.md](snapshot.md)
- bug diagnosis or root-cause analysis: [diagnose.md](diagnose.md)
- code or workflow review: [review.md](review.md)
- switching between Claude and Codex: [switching-claude-codex.md](switching-claude-codex.md)
- checking workspace parity: [quick-check.md](quick-check.md)
- reviewing current active tasks: [active-tasks.md](active-tasks.md)
- checking finished parity baseline: [parity-status.md](parity-status.md)
- reading the full idea-to-implementation history: [claude-codex-parity-implementation-report.md](claude-codex-parity-implementation-report.md)
- reviewing local parity commits and dirty-file caveats: [commit-plan.md](commit-plan.md)
- checking exact product repo push targets: [product-push-map.md](product-push-map.md)

## Agent Command Aliases

| Agent | User command | Shared source of truth |
| --- | --- | --- |
| Claude Code | `/task-router` or project router skill | [task-router.md](task-router.md) |
| Codex | `$task-router` | [task-router.md](task-router.md) |
| Claude Code | `/verify` | [verify.md](verify.md) |
| Codex | `$verify` | [verify.md](verify.md) |
| Claude Code | `/qa` | [qa.md](qa.md) |
| Codex | `$qa` | [qa.md](qa.md) |
| Claude Code | `/commit` | [commit.md](commit.md) |
| Codex | `$commit` | [commit.md](commit.md) |
| Claude Code | `/save-session` | [save-session.md](save-session.md) |
| Codex | `$save-session` or "save session" | [save-session.md](save-session.md) |
| Claude Code | `/handoff` | [handoff.md](handoff.md) |
| Codex | `$handoff` | [handoff.md](handoff.md) |
| Claude Code | `/snapshot` | [snapshot.md](snapshot.md) |
| Codex | `$snapshot` | [snapshot.md](snapshot.md) |
| Claude Code | `/diagnose` | [diagnose.md](diagnose.md) |
| Codex | `$diagnose` | [diagnose.md](diagnose.md) |
| Claude Code | `/review` | [review.md](review.md) |
| Codex | `$review` | [review.md](review.md) |

## Codex Hook Layer

The umbrella repo also contains a project-local Codex hook config:

```text
.codex/config.toml
```

It registers these hooks:

| Hook | Purpose |
| --- | --- |
| `SessionStart` | Adds startup context: detected project, active task summary, and available workflow skills |
| `UserPromptSubmit` | Adds a Koda/task-state reminder for non-trivial prompts |
| `PreToolUse` | Checks Bash guardrails before risky commands |
| `PostToolUse` | Logs failed Bash commands |
| `PreCompact` | Reminds Codex to snapshot/save before relying on compacted context |
| `Stop` | Reminds Codex to run `$save-session` after meaningful work |

The Bash guard hooks:

- block `--no-verify`, destructive resets, unsafe branch names, protected path
  removals, and `.env` reads
- run `scripts/agent-checks/pre-commit-guard.sh` before `git commit`
- log failed Bash commands to `~/.codex-friction.log`

Codex may ask the user to review/trust these project hooks through `/hooks`
after the config changes. That is expected for local hook safety.

## Project Families

| Family | Projects | Workflow state |
| --- | --- | --- |
| State-file workflow | `ripple-suite`, `sifu-tutor`, `sifututor_tutor`, `sifututor_parent`, `lls` | `.claude/tasks/active.json` points to the active task file |
| Paired frontend | `lls-frontend` | Has state workflow and dedicated frontend skills; verify with `lls` when API contracts or RTK Query slices change |
| Shared-playbook workflow | `lls-mobile`, `creative-hub`, `team-inbox` | Has task state and hooks, but no project-specific skills yet |
| Existing custom workflow plus task pointer | `finch-inbox` | Keeps Finch workflow, adds `.claude/tasks/active.json` for parity |

## Universal Order

1. Read the nearest `AGENTS.md`.
2. Read project `CLAUDE.md` for deeper technical context.
3. Search Koda memory for non-trivial tasks when the MCP is available.
4. Check workflow state:
   - state-file projects: read `.claude/tasks/active.json`
   - if any active project is missing task state, treat it as workflow drift to fix
5. Use the specific playbook for the workflow action.
6. At the end of meaningful work, use Claude `/save-session`, Codex
   `$save-session`, or the natural-language request "save session"; all three
   follow [save-session.md](save-session.md).

## Improvements Over The Old Split

- Keeps Codex from guessing what Claude skills would have done.
- Records the LLS workflow correction: it now belongs in the same task-state
  workflow family as the other active projects.
- Standardizes Koda memory values to the current MCP schema:
  `category` is `decision`, `lesson`, `rule`, `preference`, or `fact`;
  `source` is `user-stated`, `auto-captured`, or `correction`.
- Standardizes commit behavior: direct `git commit -m` flags only, no HEREDOC
  command substitution.

## LLS Migration Target

`lls` was created outside the current Sifututor Claude workflow. Do not preserve
its Superpowers-only setup as the desired architecture. The target state is:

- `.claude/tasks/active.json` support (foundation added)
- `lls-task-router`, `lls-verify`, `lls-qa`, `lls-commit`, and
  `lls-save-session` aligned with the shared route/state model
- hooks equivalent to the other active projects where applicable
- Superpowers docs retained only as historical/reference material unless the
  user explicitly wants them kept as an additional planning aid
