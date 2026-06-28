# Agent OS Enforcement And Drift Detection

Use this when deciding how an Agent OS rule should be enforced and how to catch
Claude, Codex, hooks, skills, docs, or checks drifting apart.

Plain meaning:

```text
Good rules are not enough. The Agent OS also needs reminders, checks, and
guardrails so agents actually follow the rules.
```

## Core Rule

Do not enforce every rule with a hook.

Use the lightest reliable enforcement:

| Rule type | Best home | Why |
| --- | --- | --- |
| Dangerous action | Hook, guard script, or hard rule | It should be blocked before damage happens. |
| Workflow behavior | Skill wrapper plus playbook | The agent needs judgment and context, not only a script. |
| Repeated drift | Eval or fixture | It should fail a check if the behavior comes back. |
| Human understanding | Communication and close-out standard | Hafiz should see what happened and what comes next. |
| Current-session continuity | Session Map | Long work needs a visible return path. |
| Durable lesson | Koda plus docs when needed | Future agents need the lesson without reading old chat. |

Short version:

```text
Hooks stop danger.
Skills guide the work.
Evals catch repeated drift.
Health checks prove the wiring.
Session Map keeps the story visible.
Koda remembers durable lessons.
```

## Enforcement Ladder

Use this ladder before adding new automation.

| Strength | Use when | Example |
| --- | --- | --- |
| Document | The rule guides judgment and is still being refined. | Explain in plain language before implementation. |
| Skill/playbook | The rule belongs to a repeatable workflow. | `$commit` reads `commit.md` before committing. |
| Hook reminder | The rule is often forgotten at prompt/tool boundaries. | `proceed` should trigger smart resume context. |
| Script/guard | The rule can be checked safely and deterministically. | Block `.env*`, `live/`, or `--no-verify`. |
| Eval/fixture | A behavior mistake should never quietly return. | Commit-only approval must not push. |
| Health/doctor | The repo wiring must stay installed and discoverable. | Skills, playbooks, hooks, and parity fixtures exist. |

Plain meaning:

```text
Start with the weakest enforcement that works. Move up the ladder only when
the mistake is expensive, repeated, or easy to check automatically.
```

## What Must Be Hard-Blocked

Hard-block these through `AGENTS.md`, hooks, guards, or scripts where possible:

- reading or modifying `.env*`
- exposing secrets, raw tokens, credentials, or private payloads
- modifying `live/`
- bypassing hooks or tests with `--no-verify`
- destructive actions without explicit current-session approval
- commit without exact approved file list
- push, PR, merge, deploy, production mutation, or critical-lane implementation
  without the required approval

These are not preference rules. They are safety boundaries.

## What Should Be Guided, Not Hard-Blocked

Guide these through playbooks, skills, close-outs, and evals:

- choosing Light, Medium, Full, or Critical work intensity
- deciding whether a task needs quick explanation, build-ready brief, or full
  implementation design
- deciding what evidence level a change needs
- deciding where information belongs: Session Map, Koda, Mission Ledger,
  GitHub, git commit, or chat
- deciding when to ask Hafiz versus using approved read-only evidence
- deciding whether a Session Map is needed

These need agent judgment. A hard hook would become too rigid and annoying.

## Drift Types

Treat these as different problems:

| Drift type | Meaning | Fix |
| --- | --- | --- |
| Documentation drift | Two docs say different things. | Pick the source of truth, update links, and remove stale wording. |
| Adapter drift | Claude and Codex expose different commands or phases. | Update the parity contract, skill registry, or adapter wrapper. |
| Behavior drift | Agent chooses the wrong route, skips evidence, or oversteps approval. | Add or update an eval/fixture and the relevant playbook. |
| Hook drift | Dispatcher suggests the wrong skill or misses context. | Add fixture first, then update hook if repeated or risky. |
| State drift | Chat, Session Map, git, PR, deploy, or Koda disagree. | Trust current source of truth and update stale state. |
| Memory drift | Koda memory is stale, vague, duplicated, or conflicts with docs. | Update/supersede memory after verification. |

Plain meaning:

```text
Do not patch everything in the hook. First identify what kind of drift happened.
Then fix the layer that owns that kind of truth.
```

## When To Add An Eval

Add or update an eval when:

- Hafiz corrects the same behavior more than once
- an approval boundary was misunderstood
- a critical-lane, deploy, production, secret, or destructive rule was at risk
- Claude and Codex behave differently for the same workflow
- an agent says "done" while state/evidence says otherwise
- a hook/routing mistake can be tested without needing live credentials

Do not add an eval for every awkward answer. Use the eval suite for repeated or
expensive mistakes.

## When To Change A Hook

Change hook code only when:

- a dangerous action should be blocked before tool use
- a repeated prompt category is misrouted
- a new workflow skill needs dispatcher support
- a short-command meaning was confirmed and needs automation
- an eval/fixture already describes the expected behavior

Before hook changes, update or add the relevant fixture where possible. After
hook changes, run focused fixture checks and full Agent OS health.

## Review Rhythm

Use this practical rhythm:

1. **Notice**: What went wrong or may drift?
2. **Classify**: safety, workflow, behavior, state, adapter, memory, or docs?
3. **Choose home**: docs, skill, hook, guard, eval, health, Session Map, or Koda.
4. **Update**: make the smallest change in the owning layer.
5. **Check**: run the focused check and Agent OS health.
6. **Close out**: explain what changed, what was checked, and what next.

## Minimum Checks

For docs/playbook changes:

```bash
git diff --check
scripts/agent-checks/agent-os-eval-runner.py --self-test
scripts/agent-checks/agent-os-health.sh
```

For hook/dispatcher changes:

```bash
scripts/agent-checks/agent-os-conversation-fixture-runner.py
scripts/agent-checks/agent-os-eval-runner.py --self-test
scripts/agent-checks/agent-os-health.sh
scripts/agent-checks/workflow-doctor.sh
```

For skill registry or parity changes:

```bash
scripts/agent-checks/agent-os-parity-fixture-runner.py
scripts/agent-checks/agent-os-health.sh
scripts/agent-checks/workflow-doctor.sh
```

Before commit:

```bash
scripts/agent-checks/pre-commit-guard.sh
git diff --check
```

## Decision Rule

When deciding whether to automate a rule, ask:

```text
If this fails, is it dangerous, repeated, or easy to check?
```

If yes, move it up the enforcement ladder.

If no, keep it as a playbook, example, close-out expectation, or Koda lesson.
