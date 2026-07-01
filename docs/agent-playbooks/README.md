# Shared Agent Playbooks

These playbooks translate the Claude skill workflow into plain Markdown that
Codex, Claude, and future agents can all read. Claude still owns the executable
`.claude/skills/*/SKILL.md` commands. These files are the shared reference when
an agent needs the same workflow but cannot invoke Claude skills directly.

Use these when the user asks for:

- Sifututor Agent OS overview: [agent-os.md](agent-os.md)
- Agent OS infrastructure map: [agent-os-infrastructure.md](agent-os-infrastructure.md)
- Agent OS Claude/Codex parity contract: [agent-os-parity-contract.md](agent-os-parity-contract.md)
- Agent OS roles and responsibilities: [agent-os-roles.md](agent-os-roles.md)
- Agent OS multi-agent and adapter workflow: [multi-agent-adapter-workflow.md](multi-agent-adapter-workflow.md)
- Agent OS skill registry: [agent-os-skill-registry.md](agent-os-skill-registry.md)
- Agent OS hook and dispatcher map: [agent-os-hook-dispatcher.md](agent-os-hook-dispatcher.md)
- fresh Agent OS session startup: [agent-os-quick-start.md](agent-os-quick-start.md)
- internal Agent OS build plan: [agent-os-internal-build-plan.md](agent-os-internal-build-plan.md)
- Agent OS context accuracy: [context-authority.md](context-authority.md)
- Agent OS Koda memory discipline: [agent-os-memory.md](agent-os-memory.md)
- Agent OS memory architecture v2: [agent-os-memory-architecture.md](agent-os-memory-architecture.md)
- Agent OS tool and capability model: [agent-os-capability-model.md](agent-os-capability-model.md)
- Agent OS workflow lanes: [agent-os-workflow-lanes.md](agent-os-workflow-lanes.md)
- Agent OS general guidelines: [agent-os-general-guidelines.md](agent-os-general-guidelines.md)
- Agent OS doc routing and context loading: [doc-routing-and-context-loading.md](doc-routing-and-context-loading.md)
- Agent OS master workflows: [agent-os-workflows.md](agent-os-workflows.md)
- Agent OS planning artifacts: [planning-artifacts.md](planning-artifacts.md)
- Agent OS governance and versioning: [agent-os-governance.md](agent-os-governance.md)
- Agent OS improvement loop: [agent-os-improvement-loop.md](agent-os-improvement-loop.md)
- Agent OS evidence model: [agent-os-evidence-model.md](agent-os-evidence-model.md)
- Agent OS state model: [agent-os-state-model.md](agent-os-state-model.md)
- Agent OS live session map: [session-map.md](session-map.md)
- Agent OS mission ledger: [mission-ledger.md](mission-ledger.md)
- Agent OS rollout readiness: [agent-os-rollout-readiness.md](agent-os-rollout-readiness.md)
- Agent OS eval cases: [agent-os-evals.md](agent-os-evals.md)
- Agent OS evaluation harness: [agent-os-evaluation-harness.md](agent-os-evaluation-harness.md)
- Agent OS research notes: [agent-os-research.md](agent-os-research.md)
- Agent OS current state and review roadmap: [agent-os-review-roadmap.md](agent-os-review-roadmap.md)
- Agent OS routing model: [agent-os-routing-model.md](agent-os-routing-model.md)
- Agent OS approval gates: [agent-os-approval-gates.md](agent-os-approval-gates.md)
- Agent OS push, PR, CI, and merge automation: [push-pr-ci-automation.md](push-pr-ci-automation.md)
- Agent OS release, deploy, live smoke, and monitoring: [release-deploy-live-monitoring.md](release-deploy-live-monitoring.md)
- Agent OS no-mistakes-lite final honesty gate: [no-mistakes-lite.md](no-mistakes-lite.md)
- Agent OS parallel work and worktrees: [parallel-work-and-worktrees.md](parallel-work-and-worktrees.md)
- Agent OS autonomous work packets: [autonomous-work-packets.md](autonomous-work-packets.md)
- Agent OS incident workflow: [incident-workflow.md](incident-workflow.md)
- Agent OS project adoption: [project-adoption.md](project-adoption.md)
- Agent OS workflow efficiency audit: [workflow-efficiency-audit.md](workflow-efficiency-audit.md)
- Agent OS communication and close-out: [agent-os-communication.md](agent-os-communication.md)
- working with Hafiz: [working-with-hafiz.md](working-with-hafiz.md)
- Agent OS installation: [agent-os-installation.md](agent-os-installation.md)
- Agent OS staff quick start: [agent-os-staff-quick-start.md](agent-os-staff-quick-start.md)
- Agent OS capability manifest example: [capabilities.example.json](capabilities.example.json)
- task routing or session start: [task-router.md](task-router.md)
- verification or Gate 2A: [verify.md](verify.md)
- QA or regression evidence: [qa.md](qa.md)
- related-impact audits after bugfixes: [related-impact-audit.md](related-impact-audit.md)
- test coverage manifest enforcement: [test-coverage.md](test-coverage.md)
- staging and committing: [commit.md](commit.md)
- saving knowledge at the end of work: [save-session.md](save-session.md)
- remote/device/session continuation: [save-session.md](save-session.md), [session-map.md](session-map.md)
- handoff to another agent or human: [handoff.md](handoff.md)
- context snapshot before switching or compaction: [snapshot.md](snapshot.md)
- bug diagnosis or root-cause analysis: [diagnose.md](diagnose.md)
- code or workflow review: [review.md](review.md)
- final ready/done/outbound honesty check: [no-mistakes-lite.md](no-mistakes-lite.md)
- long-running autopilot, proceed-until-done, or repeated improvement loops: [autonomous-work-packets.md](autonomous-work-packets.md)
- product design, PRDs, UX specs, and build prompts: [product-design.md](product-design.md)
- planning before implementation, visual review boards, or artifact choice: [planning-artifacts.md](planning-artifacts.md)
- multiple fixes in one chat or release inventory: [session-release-ledger.md](session-release-ledger.md)
- parallel agents, concurrent tasks, branch/worktree isolation, or stranded local commits: [parallel-work-and-worktrees.md](parallel-work-and-worktrees.md)
- live mindmap and progress board for a messy session: [session-map.md](session-map.md)
- bigger goals, child tasks, adjacent ideas, or remembered follow-ups: [mission-ledger.md](mission-ledger.md)
- quick workflow health check: [quick-check.md](quick-check.md)
- Plane exception-only legacy reference: [plane.md](plane.md)
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
| Claude/Codex | TESTING.md coverage check | [test-coverage.md](test-coverage.md) |
| Claude Code | `/commit` | [commit.md](commit.md) |
| Codex | `$commit` | [commit.md](commit.md) |
| Claude Code | `/save-session` | [save-session.md](save-session.md) |
| Codex | `$save-session` or "save session" | [save-session.md](save-session.md) |
| Claude Code | `/handoff` | [handoff.md](handoff.md) |
| Codex | `$handoff` | [handoff.md](handoff.md) |
| Claude Code | `/snapshot` | [snapshot.md](snapshot.md) |
| Codex | `$snapshot` | [snapshot.md](snapshot.md) |
| Claude/Codex | `/session-map`, `$session-map`, or "update the session map" | [session-map.md](session-map.md) |
| Claude Code | `/diagnose` | [diagnose.md](diagnose.md) |
| Codex | `$diagnose` | [diagnose.md](diagnose.md) |
| Claude Code | `/review` | [review.md](review.md) |
| Codex | `$review` | [review.md](review.md) |
| Claude Code | `/lite-prd`, `/prd-clarifier`, `/prd-to-ux`, `/ux-to-prompts` | [product-design.md](product-design.md) |
| Codex | `$product-design` | [product-design.md](product-design.md) |
| Claude Code | `/quick-check` or doctor script | [quick-check.md](quick-check.md) |
| Codex | `$quick-check` | [quick-check.md](quick-check.md) |
| Claude/Codex | `/workflow-improvement` later, `$workflow-improvement`, or "improve the workflow" | [agent-os-improvement-loop.md](agent-os-improvement-loop.md) |
| Claude/Codex | Mission Ledger capture/review | [mission-ledger.md](mission-ledger.md) |
| Claude/Codex | Session Map capture/review | [session-map.md](session-map.md) |

## Codex Hook Layer

The umbrella repo also contains a project-local Codex hook config:

```text
.codex/config.toml
```

It registers these hooks:

| Hook | Purpose |
| --- | --- |
| `SessionStart` | Adds startup context and verifies Koda read/write health before non-trivial work |
| `UserPromptSubmit` | Adds a Koda/task-state reminder for non-trivial prompts |
| `PreToolUse` | Checks Bash guardrails before risky commands |
| `PostToolUse` | Logs failed Bash commands |
| `PreCompact` | Reminds Codex to snapshot/save before relying on compacted context |
| `Stop` | Reminds Codex to run `$save-session` after meaningful work |

`SessionStart` is a Koda startup gate. It checks that Codex is using the direct
Koda CLI/helper path, direct HTTP initialization, required memory tools,
`memory_search`, and a small write
sentinel. If it reports `Koda: FAILED`, Codex must repair Koda before doing
non-trivial work:

```bash
python3 scripts/agent-checks/codex-lifecycle-hook.py --check-koda
```

## Codex Automatic Workflow Dispatch

`UserPromptSubmit` now acts as a lightweight workflow dispatcher. It does not
blindly run commands; it injects the required Codex skill into the model context
before Codex answers.

| User intent | Required Codex skill |
| --- | --- |
| new work, continue work, proceed, implement | `$task-router` |
| bug, broken behavior, failing test, root cause | `$diagnose` |
| verify, run checks, prove it works, Gate 2A | `$verify` |
| QA, smoke, regression, visual/manual check | `$qa` |
| review, audit, pre-commit risk check | `$review` |
| quick check, health check, workflow doctor | `$quick-check` |
| commit, stage, prepare commit | `$commit` |
| save session, wrap up, finish session | `$save-session` |
| handoff to Claude/Codex/human | `$handoff` |
| snapshot, pause, compact/context save | `$snapshot` |
| session map, mindmap, progress board, return path | `$session-map` |
| push, deploy, merge, PR | `$review` first, then explicit approval |
| brainstorm, PRD, UX spec, build prompts, major redesign | `$product-design` |

The complete implementation path for normal coding work is:

```text
$quick-check -> $task-router -> TESTING.md check -> implementation -> $verify -> $qa -> $review -> $commit -> $save-session
```

When more than one issue/fix is handled in the same chat, insert the Session
Release Ledger into the path:

```text
$task-router -> session release ledger -> per-fix verify/qa/review -> commit/PR -> pre-deploy inventory -> deploy/smoke
```

When the conversation itself becomes hard to follow, add or update the Session
Map:

```text
$task-router -> session map -> route/design/diagnose/build/verify -> save-session
```

## Plain-Language Reporting

Use [agent-os-communication.md](agent-os-communication.md) as the source of
truth for day-to-day user-facing explanation style.

Every workflow report should teach the practical meaning before the technical
details. Start with what Hafiz needs to understand in everyday terms, especially
for bugs, API behavior, deployment risk, or test failures. Then add the exact
files, commands, evidence, and workflow labels needed for traceability.

Avoid workflow labels as filler. If labels such as `Gate 2A`, `PARTIAL`,
`BLOCKER`, or `Critical Save` are useful for audit trail, handoff, QA, commit
records, or teaching terminology, use the label and immediately translate it
into normal language.

Good default order:

1. What this means in plain language.
2. Why it happened or why the change matters.
3. What changed or what should change.
4. How it was checked.
5. Any remaining decision or risk.

## Mandatory Next-Step Close-Out

Do not end meaningful work by only saying it is done. Hafiz should not need to
ask "what next?", "are we done?", or "can we close the session?" after every
step.

After each implementation, diagnosis, verification, QA, review, commit prep, or
session save, include this short plain-language close-out:

```text
Status:
<done / partly done / blocked>

Meaning:
<what this changes for the app, customer, team, or workflow>

Checked:
<tests, commands, review evidence, or why it was not checked>

Recommended next:
<the single next action the agent recommends>

Decision needed:
<yes/no; if yes, the exact decision Hafiz needs to make>
```

Before closing a session, also answer:

- Are all planned steps complete?
- Did tests, guards, or reviews pass?
- Is anything still unverified?
- Should the next move be continue, QA, commit, save-session, or close?

Commit, push, merge, deploy, and PR actions still require explicit
current-session approval. The automation chooses the workflow, not the business
decision.

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
5. If the project has `TESTING.md`, read it and apply
   [test-coverage.md](test-coverage.md) before implementation, verify, QA,
   review, and commit.
6. Check the Mission Ledger only when the work belongs to a bigger goal,
   paused decision, adjacent idea, or remembered follow-up.
7. Use the specific playbook for the workflow action.
8. At the end of meaningful work, use Claude `/save-session`, Codex
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
