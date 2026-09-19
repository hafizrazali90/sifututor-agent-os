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

## Secret-output prevention

Credential safety is a hard guard because a warning after tool execution is too
late. The shared owner is `scripts/agent-checks/secret_output_guard.py`.

Use these layers together:

1. The shared pre-tool guard blocks known whole-environment, raw process,
   container, secret-store, credential-file, shell-tracing, and verbose
   authenticated-request output before execution.
2. Agents use reviewed `scripts/agent-access/` wrappers that return status,
   counts, names, or boolean comparisons without returning credentials.
3. A reveal/capture request creates a metadata-only session marker. While it is
   active, the shared pre-tool guard blocks every tool, because a generic
   browser open/read or arbitrary script could return the credential without
   using a screenshot command. Hafiz uses hidden owner-only entry. The marker
   stores no prompt, URL, page content, or credential; it clears only when the
   credential surface is explicitly closed/hidden, at session stop, or at the
   start of a replacement session.
4. `secret_artifact_scan.py` inspects staged additions before commit and
   reports only the file, line, and detection rule.
5. Claude and Codex failure logs retain metadata only; command arguments and
   error output are redacted before persistence.

Do not weaken a block by adding an inline pipe such as `grep`, `jq`, or `sed`
after a raw environment command. The sensitive output already exists inside
the tool path. Add or update a reviewed wrapper instead.

If a new dangerous pattern is found, add one failing regression, extend the
shared guard, prove the safe alternative still works, then update the eval or
playbook only when agent judgment is also involved.

### Direct patch data is not a shell command

The shared guard classifies exact direct tool names `apply_patch` and
`functions.apply_patch` as inert patch data only when the input is a patch
string, or a single-key `input`, `patch`, or `command` object containing that
string. It must start with the patch opening marker and end with its closing
marker. The actual local adapter's `command` object shape was observed during
the issue #86 repair; other supported shapes have deterministic fixture proof,
not a claim that every adapter emits them.
`Edit`, `Write`, and other aliases are not added by this narrow change.

The all-tool credential-reveal quarantine is checked first and still denies
patches. Unknown or suffixed tool names, mixed/malformed objects, and execution
tools retain command inspection. There is no blanket exemption for
`functions.exec`; mixed orchestration with an executable call is still checked.
Native protected-path permissions, secret-artifact scanning, and approval
controls remain separate and unchanged: classifying patch prose as data does
not authorize its target path or make arbitrary patch content safe to publish.

`test_secret_guard_reconciliation.py` includes literal direct-tool and actual
hook-CLI regression journeys, including metadata-only denials and quarantine.
The installed edit path must also be retried normally after activation; mocked
routing tests alone missed the adapter's actual payload shape in issue #86.
Do not disable guards or encode/re-route edits to make a failing trial pass.

### Inspection formats are not automatically safe

`docker inspect --format` is not a safety boundary by itself: a template can
return the whole object, including its environment. The shared guard accepts
only literal scalar templates for `State.Status`, `State.Running`,
`State.Restarting`, `State.Paused`, `State.Dead`, `State.ExitCode`,
`State.Health.Status`, `RestartCount`, and `Id`, optionally using `json` on
that scalar. Whitespace and the ordinary `--format`, `--format=`, `-f`, and
attached `-f` forms are supported. Every supplied format must be safe.
Formats in comments or later commands cannot satisfy an earlier inspect.
Docker global-option and line-continuation forms are deliberately refused;
use the reviewed wrapper instead of trying alternate spellings.
For recognized simple invocations, shell tokenization ensures a quoted
positional argument cannot masquerade as an option; `--` ends options.
Dynamic expressions, redirections, and ambiguous nested quoting are refused.

Whole objects, health logs, error text, dynamic templates, and other fields
need a reviewed non-printing wrapper; do not bypass the guard or pipe unsafe
output into a filter. Ordinary approved wrappers and documentation searches
remain available without additional routine approval.

Permanent synthetic coverage lives in
`scripts/agent-checks/test_secret_guard_reconciliation.py`. It exercises the
actual pre-tool CLI without executing Docker or reading a real credential.
This recognizer is deliberately narrow, not a complete shell/JavaScript
interpreter or proof that all indirect command construction is safe.

### Reconcile shipped protection before reviving old patches

PRs #70, #72, and #73 established the shared output guard, metadata-only
failure logs, staged-artifact scan, and session-wide reveal quarantine.
Compare source and adapter registration separately: a merged guard file does
not prove a particular live agent invokes it. Deterministic tests prove only
their covered paths; fresh installed-agent evidence is a separate release
check. Never describe fixture success as universal model compliance.

Cost safety is separate from secret-output safety. The existing Claude
delegation runner strips `ANTHROPIC_API_KEY` for probes and worker launch and
requires an authenticated `claude.ai` Max result during preflight. An older
#28 worktree adds refusal when the parent has that variable; do not blindly
port it or call the current protection missing. Review that remaining policy
delta separately. Absence of a key alone never proves subscription billing,
and those Claude-specific checks do not establish another provider's billing
mode. Provider/auth configuration changes and paid evaluations stay outside
this local secret-guard reconciliation. Keep #28 open until its owner resolves
the remaining policy and verification scope.

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

## Promotion Path

Rules should earn stronger enforcement.

Plain meaning:

```text
Do not turn every good rule into a hook.
Promote a rule only when real use proves it needs stronger protection.
```

Use this path:

| Stage | Use when | Promote when | Do not promote when |
| --- | --- | --- | --- |
| Manual guidance | The rule is new, judgment-heavy, or still being shaped with Hafiz. | The same mistake repeats or the rule becomes clear enough to test. | The rule is mainly tone, style, preference, or product judgment. |
| Playbook or skill wrapper | The rule belongs inside a repeatable workflow. | Agents keep missing it even after route docs are loaded. | The issue is one-off or better handled by a clearer example. |
| Markdown eval | The expected behavior should be named and reviewed. | The behavior is repeated, expensive, or likely to drift between agents. | The behavior cannot be stated clearly yet. |
| Local fixture or runner | The behavior can be checked deterministically without live credentials. | The fixture would catch the mistake without false confidence. | The check needs real session judgment, external state, or product acceptance. |
| Script or guard | The rule can be checked safely against files, commands, or repo state. | A local deterministic check prevents a real mistake. | The check would block valid work or require broad access. |
| Hook reminder | The rule is often missed at prompt or tool-use time. | A reminder prevents repeated routing/context mistakes. | The hook would become noisy or try to decide judgment-heavy work. |
| Hard hook/block | The action is unsafe before it happens. | The action crosses secrets, `live/`, destructive, bypass, or unapproved outbound boundaries. | The rule is only about quality, wording, or workflow preference. |

Decision shortcut:

```text
Manual if it needs judgment.
Eval if it should not quietly return.
Script if it is deterministic.
Hook if it must happen at prompt/tool time.
Hard block only for real danger.
```

## Promotion Questions

Before promoting a rule, answer:

1. What exact mistake are we preventing?
2. Has it happened more than once, or is it dangerous enough once?
3. Which layer owns the truth: docs, skill, Koda, Session Map, git, tests, hook,
   or external service?
4. Can it be checked locally without guessing?
5. Would automation create false confidence or annoying false blocks?
6. What is the lightest layer that would have caught the mistake?
7. How will Hafiz understand the new behavior in plain language?

If those questions are unclear, keep the rule manual and add a better example
first.

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

Use Markdown evals first when the behavior is important but not yet
deterministic. Promote to a runner only when the expected answer can be checked
without needing live session judgment.

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

When in doubt, prefer:

```text
better example -> Markdown eval -> local fixture -> script -> hook -> hard block
```

Do not skip straight from "Hafiz prefers this" to "the hook must enforce it."
