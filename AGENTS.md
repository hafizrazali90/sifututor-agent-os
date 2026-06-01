# AGENTS.md - Sifututor Umbrella Workspace

This file is the shared operating contract for AI coding agents in the
Sifututor umbrella workspace. Claude Code also reads `CLAUDE.md`; Codex reads
this file first. Project-specific rules live in each sub-project `AGENTS.md`.

## Workspace

Open VS Code at `/Users/hafizrazali/Projects/Sifututor` for cross-project work.
When working on one project, declare intent in the first message:

```text
sifu-tutor work - ...
ripple-suite work - ...
sifututor_tutor work - ...
lls work - ...
```

Active projects:

| Project | Purpose |
| --- | --- |
| `sifu-tutor` | Laravel SIMS rebuild |
| `ripple-suite` | Next.js dashboard rebuild |
| `sifututor_tutor` | React Native tutor app |
| `sifututor_parent` | Parent app rebuild |
| `lls` | Learnest Laravel backend |
| `lls-frontend` | Learnest React frontend |
| `lls-mobile` | Learnest mobile app |
| `creative-hub` | Creative Hub |
| `team-inbox` | WhatsApp/team inbox |
| `finch-inbox` | Finch omnichannel inbox |

`live/` contains production snapshots. Never modify anything under `live/`.
Use it only as read-only reference.

## Universal Safety Rules

- Never read or modify repository `.env*` files, production secrets, or files under
  `live/`.
- Agents may read explicitly approved, scoped credential files outside repositories
  when needed for the task, such as read-only agent access files under
  `~/.config/sifututor/`. Do not reveal, commit, copy into the repo, or log
  secret values.
- Never push, merge, deploy, or open a PR without explicit instruction in the current session.
- Never bypass hooks or verification with `--no-verify` or equivalent flags.
- Never make broad cleanup or adjacent refactors unless explicitly requested.
- If requirements conflict, stop and ask for clarification.
- If a task touches payments, commission, auth, migrations, or mobile API contracts, halt for human review before commit.

## Communication Style

- Talk to Hafiz in natural language first, like code translated into plain
  English.
- Assume Hafiz is a self-learning engineer without a computer science
  background. Explain the practical meaning first, then add technical details
  such as files, functions, commands, tests, or workflow labels.
- For bugs and API issues, include a short non-technical mental model before
  the code-level diagnosis. Example: "the list is being filtered twice, so the
  item disappears after it is assigned."
- Prefer "what happened, what I changed, how I checked it, and what comes next"
  over workflow labels.
- Do not make Hafiz ask "what next?" after each step. After every meaningful
  work step, include a short close-out in plain language:
  - `Status`: done, partly done, or blocked.
  - `Meaning`: what changed in the product or workflow.
  - `Checked`: tests, commands, review, or why it was not checked.
  - `Recommended next`: the single next action the agent recommends.
  - `Decision needed`: yes/no, and what Hafiz needs to decide.
- Before ending a session, explicitly say whether all planned work is done,
  whether tests/guards passed, whether anything remains unverified, and whether
  the recommended next action is continue, QA, commit, save-session, or close.
- Avoid leading user-facing replies with words like `PARTIAL`, `BLOCKER`,
  `Gate 2A`, or `Critical Save` unless Hafiz asks for a formal report or a
  playbook requires an exact audit trail.
- If work is incomplete, explain the practical reason and next move in normal
  words.
- Keep formal labels inside commits, QA notes, save-session reports, and agent
  handoffs when they are useful for traceability.

## Branches And Commits

## GitHub Issue Automation

For coding work, confirm whether the user provided a GitHub issue number. If no
issue number is provided, create a GitHub issue automatically before coding
instead of asking for permission. Use the best available context for the title,
body, labels, and project fields; prefer conservative defaults when priority,
severity, or environment is not explicit. Ask Hafiz only if issue creation fails,
requires credentials that are unavailable, or the task is too ambiguous to title
safely.

Allowed branch pattern:

```text
type/description
```

Valid types: `feat`, `feature`, `fix`, `refactor`, `hotfix`, `chore`, `docs`,
`perf`, `test`, `ci`.

Use lowercase kebab-case descriptions:

```text
feat/add-login-screen
fix/null-crash-on-payment
docs/update-api-reference
```

Commit format:

```text
[emoji] type(scope): description
```

Use direct `-m` flags for commit messages. Do not use HEREDOC-style command
substitution for `git commit -m "$(cat <<'EOF' ...)"`; the commit hook cannot
parse it reliably.

## TDD And Gates

For feature, bugfix, and hotfix work, use vertical-slice TDD:

```text
one failing test -> one implementation -> one passing test -> repeat
```

Do not write all tests first and then all implementation in one horizontal batch.

Quality gates:

- Gate 1: plan review before build.
- Gate 2A: verify the task works with tests, type checks, lint/build as applicable.
- Gate 2B: guard against regressions, scope creep, security issues, and N+1/performance issues.
- Gate 3: stop on ambiguity.
- Gate 4: adversarial pre-push review, never skipped.

## Koda Memory

Koda is the shared memory layer across Claude and Codex.

For non-trivial tasks:

1. Search Koda memory at task start if the MCP tool is available.
2. Store user corrections immediately with `source: "correction"`.
3. Store non-obvious implementation lessons before reporting complete.
4. Every stored memory must include at least one project tag.
5. `source` must be one of `user-stated`, `auto-captured`, or `correction`.

Do not store secrets, credentials, raw tokens, or ephemeral state.

## Plane Mission Board

Plane is Hafiz's human mission board. For non-trivial work, agents should check
or maintain the relevant Plane card so Hafiz can see the goal, sub-goals,
current step, next action, owner, blockers, and evidence without reading the
chat transcript.

Follow `docs/agent-playbooks/plane.md` before creating or updating Plane items.
Agents may auto-update factual progress, but must ask Hafiz before changing
scope, priority, owner, roadmap direction, production state, or creating major
new work.

## Project-Specific Rules

Before editing code in a sub-project, read that project's `AGENTS.md` if it
exists. If it does not exist yet, read the project `CLAUDE.md` and follow the
stricter rule.

When `.claude/tasks/active.json` exists, read it before implementation work and
resume the active task unless the user explicitly starts a new one.

## Shared Guardrail Scripts

Before committing from any project, run:

```bash
../scripts/agent-checks/pre-commit-guard.sh
```

From the umbrella root, run:

```bash
scripts/agent-checks/pre-commit-guard.sh
```

These scripts validate branch naming, sensitive paths, and active task state.
They are the portable fallback while Claude and Codex hook behavior differs.

## Shared Workflow Playbooks

For Claude-to-Codex workflow parity, use the shared playbooks in
`docs/agent-playbooks/`:

| Need | Playbook |
| --- | --- |
| Start or route a task | `docs/agent-playbooks/task-router.md` |
| Run Gate 2A / verify | `docs/agent-playbooks/verify.md` |
| Run QA or regression checks | `docs/agent-playbooks/qa.md` |
| Monitor production logs | `docs/agent-playbooks/monitor-production-logs.md` |
| Maintain Plane mission board | `docs/agent-playbooks/plane.md` |
| Prepare a commit | `docs/agent-playbooks/commit.md` |
| Save/handoff session knowledge | `docs/agent-playbooks/save-session.md` |

These do not replace Claude skills. They are the shared reference that lets
Codex follow the same workflow when it cannot invoke `.claude/skills/*`
directly.
