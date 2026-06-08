# AGENTS.md - Sifututor Agent OS

This file is the shared operating contract for the **Sifututor Agent OS**:
the operating layer that helps Hafiz, Claude, Codex, Koda, GitHub, Plane,
Planner, and project tools plan, build, verify, remember, and ship work without
losing context.

Claude Code also reads `CLAUDE.md`; Codex reads this file first.
Project-specific rules live in each sub-project `AGENTS.md`.

Use these names consistently:

- **Agent OS**: the whole collaboration system.
- **Workflow**: one route inside the Agent OS, such as bugfix, feature,
  product design, QA, commit, or save-session.
- **Playbook**: the written steps for a workflow.
- **Router**: the part that decides which workflow applies.
- **Guardrails**: rules and scripts that prevent expensive mistakes.
- **Working Agreement**: how Hafiz, Codex, Claude, and reviewers collaborate.

See `docs/agent-playbooks/agent-os.md` for the short operating model.

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
- If the explanation is technical or twisted, add an easier non-technical
  explanation as well.
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
- Avoid user-facing filler labels such as `PARTIAL`, `BLOCKER`, `Gate 2A`, or
  `Critical Save` unless Hafiz asks for a formal report, the label is useful
  for teaching industry/Agent OS terminology, or a playbook requires an exact
  audit trail. When a label is used for learning, translate it into normal
  language immediately.
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
- Gate 2A: verify the task works with tests, type checks, lint/build as applicable,
  including the permanent E2E regression decision for user-facing behavior.
- Gate 2B: guard against regressions, scope creep, security issues, N+1/performance
  issues, and missing human-journey coverage.
- Gate 3: stop on ambiguity.
- Gate 4: adversarial pre-push review, never skipped.

## AI Implementation Readiness

Before coding critical-lane work, cross-module workflows, or any task that will
be handed from one AI/human developer to another, apply
`docs/agent-playbooks/ai-implementation-readiness.md`.

The plan/build prompt must identify the real entry point, contract moment,
state transition, idempotency/retry behavior, realistic external payloads,
backward compatibility, and exact evidence. Green tests are not enough if the
tests prove a weaker behavior than the acceptance rule.

## Agent-As-Tester Evidence

Hafiz is technical and self-taught in IT, but the agent is the bridge into
coding and should also be the first tester. Agents must use available safe
tools to validate what a capable human tester would validate before asking
Hafiz to check it.

For user-facing behavior, do not treat code tests alone as complete proof.
Gather human-journey evidence where feasible: browser/mobile E2E, agent-run
smoke, screenshots, API/curl evidence, server-side read-only checks, or a
manual QA checklist with exact steps.

Ask Hafiz to verify only what the agent cannot safely or honestly verify:
business judgment, subjective UX/product acceptance, unavailable credentials or
representative data, destructive workflows, production-sensitive action, final
risk acceptance, priority, or scope.

Use `docs/agent-playbooks/agent-os-evidence-model.md` for the full evidence
model.

## Multiple-Fix Session Ledger

When one chat/session contains more than one bug, fix, branch, PR, or deploy
candidate, maintain a Session Release Ledger. This prevents "fixed in code"
from being mistaken for "merged to main" or "live in production".

Use `docs/agent-playbooks/session-release-ledger.md` and keep one line per
issue with: issue, branch, commit, PR, tests, E2E, main status, live status, and
next action.

Required moments:

- Start or update the ledger when a second issue enters the same session.
- Before switching to another bug, state whether the current fix is local only,
  pushed, PR open, merged, deployed, or smoke passed.
- Before commit, PR, merge, push, or deploy, inventory every session fix and
  say which ones are in `origin/main`, which are PR-only, which are local-only,
  which are already live, and which are not live.
- Never summarize multiple fixes as "done" without naming their target state:
  done locally, PR open, merged to main, deployed, or live smoke passed.

## Permanent E2E Regression Rule

Every user-facing feature, bugfix, or hotfix must either add/update a permanent
E2E regression test or explicitly document why that is not feasible in the same
task.

For any workflow a staff member, admin, parent, tutor, student, customer, or
mobile user can perform, the default requirement is a permanent E2E test. This
applies to every user story, feature, function, bugfix, hotfix, and visible
workflow change, not only staff-reported bugs. Backend, unit, feature, API, or
service tests are still required where appropriate, but they are not enough by
themselves to call a user workflow complete.

This applies especially to staff-reported SIMS bugs and browser-visible issues:
if the bug is "clicking a button does nothing", "a modal does not open", "a row
does not appear", "a status/filter/action is wrong", or any workflow a staff
member, parent, tutor, student, or admin performs in the UI, backend/unit tests
are not enough. The agent must prove the real journey with Playwright or an
equivalent browser/mobile E2E path.

Required behavior:

- First look for the existing feature/module/function spec under `tests/e2e/`
  and extend it instead of creating scattered one-off tests.
- Add or update stable seed/fixture data when the E2E needs representative data.
- Run the focused E2E command for the new/changed test and report the exact
  command and result.
- Before push, PR, merge, or deploy, state which permanent E2E file covers each
  changed user workflow. If no E2E covers it, stop and either add one or get
  explicit Hafiz acceptance of the named exception.
- If a permanent E2E is genuinely not feasible, state the blocker using one of
  these reasons: `missing credential`, `no safe representative data`,
  `destructive workflow`, `tooling unavailable`, or `not user-facing`; then name
  the follow-up fixture/test needed.
- One-off browser smoke is useful evidence, but it must not replace permanent
  E2E regression coverage when the workflow can be automated safely.

## Test Coverage Manifest

Projects may include `TESTING.md` as the feature coverage manifest. When it is
present, every agent must read it before changing user-facing behavior, identify
the affected feature row, and keep the row accurate as tests are added or
changed.

Coverage rules:

- A covered feature must name a real test file that asserts the behavior.
- A partial feature must say exactly what is still missing.
- A missing feature must not be treated as safe to ship until a real test is
  added or Hafiz explicitly accepts the risk for documentation/investigation
  work only.
- A user-facing feature must also name human-journey evidence: automated E2E,
  browser/mobile smoke, screenshot-backed agent QA, or a manual QA checklist
  with the exact steps and result.
- If no row matches the changed feature, update `TESTING.md` as part of the
  work.

Backend, API, or unit tests prove the engine. They do not by themselves prove
that a staff member, parent, tutor, student, or admin can complete the workflow
in the real UI. Agents must run non-destructive human-like checks they can run
themselves before asking Hafiz or staff for manual QA.

Use `docs/agent-playbooks/test-coverage.md` for the full shared workflow. When
available, run:

```bash
python3 ../scripts/agent-checks/test-coverage-manifest-check.py --project .
```

From the umbrella root:

```bash
python3 scripts/agent-checks/test-coverage-manifest-check.py --project <project>
```

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

## Microsoft Teams Planner Intake

The Microsoft Teams Planner board `Development & Support > Task Management
Board` is the internal staff issue tracker for SIMS (`sifu-tutor`) and both
mobile apps (`sifututor_tutor`, `sifututor_parent`). Use it as staff-reported
issue intake and operational context when work involves SIMS production
behavior, tutor app issues, parent app issues, support tickets, TREQ/TUT
reports, or staff-reported bugs.

Planner is not the engineering source of truth. After reading a relevant
Planner card, route confirmed engineering work through the normal workflow:
GitHub issue for coding work, Plane for Hafiz-visible mission status, active
task state where the project uses it, and the usual verify/QA/review gates.
Do not change Planner card state, assignment, priority, or content unless Hafiz
explicitly asks in the current session.

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
