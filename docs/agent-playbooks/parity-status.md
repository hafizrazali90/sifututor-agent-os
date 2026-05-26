# Claude/Codex Parity Status

Last updated: 2026-05-26

## Completed Baseline

All active workspace projects now have the shared Claude/Codex baseline:

| Project | AGENTS.md | `.claude/tasks/active.json` | Hooks | Notes |
| --- | --- | --- | --- | --- |
| `sifu-tutor` | yes | yes | yes | Active bugfix `bugfix-20260524-4023`, next step `fix` |
| `ripple-suite` | yes | yes | yes | No active task |
| `sifututor_tutor` | yes | yes | yes | Active feature `tut-auth-firstrun-rebuild`, next step `generate_tests` |
| `sifututor_parent` | yes | yes | yes | No active task |
| `lls` | yes | yes | yes | Migrated from Superpowers-only to standard task state |
| `lls-frontend` | yes | yes | yes | Has dedicated frontend workflow skills |
| `lls-mobile` | yes | yes | yes | Shared playbooks only; Flutter-specific skills not created yet |
| `creative-hub` | yes | yes | yes | Shared playbooks only |
| `team-inbox` | yes | yes | yes | Confirm active product direction before substantial work |
| `finch-inbox` | yes | yes | existing + tasks | Keeps Finch workflow, adds shared active task pointer |

## Source Of Truth

- `AGENTS.md` owns shared rules for both Claude and Codex: commands, critical
  safety rules, branch/commit rules, Koda obligations, and workflow playbooks.
- `CLAUDE.md` owns deep technical context and Claude-specific project reference.
- `.claude/CLAUDE.md`, `.claude/skills/`, and hooks remain Claude orchestration.
- `docs/agent-playbooks/` is the Codex-readable equivalent of the core Claude
  skills: task routing, verify, QA, commit, and save-session.
- `.agents/skills/` contains Codex wrappers for the shared playbooks.
- `.codex/config.toml` contains Codex project hooks for Bash guardrails,
  startup context, prompt reminders, pre-compaction reminders, and stop-time
  save-session reminders.

## Local Claude Parent Config

The parent machine-local Claude config has also been audited:

- `.claude/settings.json` includes all ten workspace projects in
  `additionalDirectories`, including `finch-inbox`.
- Parent `CLAUDE.md` includes `finch-inbox` in the project table and Koda tag
  list.

These files are intentionally local workflow configuration in this workspace,
not part of the pushed umbrella GitHub repo.

## Verified

- Shared guard passed in all ten projects.
- Hook Python files compiled successfully.
- Codex repo-local skills are visible in `codex debug prompt-input`.
- Codex lifecycle and Bash hook scripts passed direct sample-payload tests.
- `settings.json` and `active.json` files parsed successfully.
- Stale claims such as "no `.claude` config yet" and "read CLAUDE.md first"
  were removed or updated.

## Remaining Optional Hardening

- Create project-specific workflow skills for `lls-mobile`, `creative-hub`, and
  `team-inbox` only after their development cadence justifies it.
- Trust/review Codex project hooks through `/hooks` when Codex prompts for it.
  Continue using `scripts/agent-checks/pre-commit-guard.sh` as the portable
  manual guard.
- Finish or park active tasks in `sifu-tutor` and `sifututor_tutor` before
  starting unrelated work in those projects.
