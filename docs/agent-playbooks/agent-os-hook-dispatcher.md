# Agent OS Hook And Dispatcher

Status: draft for internal Sifututor Agent OS use.

Use this file to understand the Codex hook layer and how it suggests workflow
skills.

Plain meaning: this is the routing assistant. It helps Codex start with the
right context and likely skill, but it does not own the final decision.

## What This Layer Is

The hook layer is configured in:

```text
.codex/config.toml
```

The main implementation is:

```text
scripts/agent-checks/codex-lifecycle-hook.py
```

The hook runs automatically at certain Codex events. It can add context,
suggest a skill, check Koda health, remind Codex to save, and run guardrails
before Bash commands.

## What This Layer Is Not

The hook is not:

- a replacement for Hafiz approval,
- a replacement for agent judgment,
- a hidden executor,
- a deploy/commit/push tool,
- the source of product truth,
- allowed to bypass `AGENTS.md`.

The hook should never silently perform expensive state changes.

## Hook Events

| Event | When it runs | What it does |
| --- | --- | --- |
| `SessionStart` | Startup, resume, clear, or compact session start. | Loads Sifututor context and verifies Koda read/write health once for the session. |
| `UserPromptSubmit` | Every Hafiz prompt. | Emits one compact route hint when a workflow skill is genuinely useful. |
| `PreToolUse` | Before tools run. | Blocks secret-bearing command output and visual capture while a provider credential-reveal boundary is active; Bash-specific guardrails still run only for shell/exec commands. |
| `PostToolUse` | After shell/exec commands. | Records metadata-only failed-command diagnostics without command arguments or raw output. |
| `PreCompact` | Before context compaction. | Reminds Codex to snapshot or save meaningful context. |
| `Stop` | When Codex is about to stop. | Reminds Codex to save meaningful session state. |

## Codex Hook Notes

`SessionStart` is also a Koda startup gate. If it reports `Koda: FAILED`, repair
Koda before non-trivial work:

```bash
python3 scripts/agent-checks/codex-lifecycle-hook.py --check-koda
```

The Codex Bash guard blocks `--no-verify`, destructive resets, unsafe branch
names, protected-path removals, and `.env` reads; it runs
`scripts/agent-checks/pre-commit-guard.sh` before `git commit`; and it logs
failed Bash commands to `~/.codex-friction.log`. Codex may ask to review or
trust project hooks through `/hooks` after the config changes; that is expected.

## Dispatch Rule

Skill selection is:

```text
agent-owned, hook-assisted, Hafiz-overridable, and safety-constrained.
```

That means:

1. The hook suggests a workflow skill.
2. Codex reads the selected skill wrapper and linked playbook.
3. Codex confirms whether the selected skill is actually right.
4. Hafiz can override the route.
5. Safety rules force stricter behavior when needed.

The hook is the first guess, not the boss.

## What UserPromptSubmit Adds

For a non-trivial prompt, `UserPromptSubmit` adds only:

- one compact project/route/reason line,
- the active task when one exists,
- route-specific actions that materially change the next move,
- Koda context only for product design, diagnosis, or session continuity.

Do not repeat the full working agreement, communication rules, skill list,
approval model, or default delivery pipeline on every prompt. Those remain in
the source documents and selected skill. Ordinary task routing should stay
quiet enough that it does not compete with the actual work.

A route hint looks like:

```text
Sifututor route: $product-design for Sifututor (Prompt asks for product design.)
```

Claude receives the same explanation-first, pre-implementation preview, and close-out behavior through the shared
`.claude/hooks/koda-context-injector.py` prompt bridge. Memory lookup may fail
silently, but both non-trivial-prompt communication reminders must still be emitted.
This is adapter parity at the behavior boundary; the two hook mechanisms do
not need identical internal code.

### Jev shadow advice

Both prompt adapters also call one shared observer:

```text
scripts/agent-checks/agent_os_jev_shadow.py
```

It asks Jev for a workflow-route opinion only after local secret/PII and
critical-lane checks pass. Jev receives a bounded first-sentence summary and
route tags, never the raw prompt. Its answer is displayed as advice and cannot
approve, block, continue, clean up, commit, merge, deploy, or override the
deterministic route. Missing credentials, missing SDK files, timeouts, and bad
answers fall back silently to the existing Agent OS behavior.

The observer stores one metadata-only daily aggregate under
`~/.local/state/sifututor-agent-os/jev-shadow/`. It never stores prompt text,
provider answers, project names, or reasons. Set `SIFUTUTOR_JEV_SHADOW=0` for
an immediate local kill switch.

Owner activation is one-time:

1. Install the pinned sidecar dependency with `npm ci --omit=dev` inside
   `scripts/agent-checks/decision-layer/jev-sidecar/`.
2. Put `TYPESAFE_API_KEY=<value>` in the owner-only file
   `~/.config/sifututor/agent-access/typesafe-jev.conf` and set mode `0600`.
3. Run `python3 scripts/agent-access/check-jev-shadow.py --live`.

Do not paste the key into chat, repository files, hook settings, logs, or Koda.

## Dispatch Inputs

The dispatcher uses these signals:

| Signal | Example |
| --- | --- |
| Explicit skill request | `$commit`, `$verify`, `$product-design` |
| Protected action words | push, deploy, merge, PR, commit |
| Risk domains | auth, payment, invoice, commission, migration, mobile API |
| Intent words | fix, verify, QA, review, diagnose, save, brainstorm |
| Discussion words | explain, discuss, why, what should, architecture |
| Prompt length / non-triviality | Longer prompts are routed instead of ignored. |
| Project hint | `sifu-tutor`, `ripple-suite`, tutor app, parent app, LLS |
| Smart resume signals | `continue`, `go next`, recent Session Map, or local commits ahead of GitHub |
| Koda search | Relevant durable lessons are injected when safe. |

The dispatcher should not route by keyword alone. The agent must still inspect
context.

Evidence reports and quoted text are context, not commands. A pasted report
that says `--no-verify` was not used, or that nothing was committed/pushed,
must not become a bypass or outbound-action request. The top-level user intent
controls the route. Questions about reducing Agent OS ceremony, redundancy, or
development time route to `$workflow-improvement`.

## Dispatch Priority

Use this mental model:

| Priority | Route |
| --- | --- |
| 1 | Forbidden or unsafe behavior is blocked by rules and guards. |
| 2 | Critical lanes route to read-only diagnosis before implementation. |
| 3 | Explicitly requested skill wins if safe. |
| 4 | Push, deploy, merge, PR route to review first. |
| 5 | Commit routes to commit playbook and exact file-list approval. |
| 6 | Verify, QA, review, diagnose route to their workflow skills. |
| 7 | Product/workflow design routes to product-design. |
| 8 | Normal non-trivial work routes to task-router. |
| 9 | Tiny trivial prompts may need no workflow skill. |

## Current Skill Mapping

| Prompt intent | Suggested skill |
| --- | --- |
| Start, continue, proceed, implement | `$task-router` |
| Bug, broken behavior, failing test, root cause | `$diagnose` |
| Verify, run checks, prove it works, Gate 2A | `$verify` |
| QA, smoke, regression, visual/manual check | `$qa` |
| Review, audit, pre-commit risk check | `$review` |
| Quick check, health check, workflow doctor | `$quick-check` |
| Commit, stage, prepare commit | `$commit` |
| Save session, wrap up, finish session | `$save-session` |
| Handoff to Claude, Codex, or human | `$handoff` |
| Snapshot, pause, compact/context save | `$snapshot` |
| Session map, mindmap, progress board, return path | `$session-map` |
| Push, deploy, merge, PR | `$review` first, then explicit approval |
| Brainstorm, PRD, UX spec, build prompts, major redesign | `$product-design` |

## Claude Project Hook Resolution

The Codex hook layer above is one dispatcher. Claude has a second, smaller one
with a different job: finding the right *project* hook when a session was not
launched inside that project.

### The problem it solves

Sub-project settings run their gates like this:

```text
cd "$CLAUDE_PROJECT_DIR" && python3 .claude/hooks/quality-gate.py
```

A session launched from the umbrella workspace keeps the umbrella
`CLAUDE_PROJECT_DIR` even after the work moves into a sub-project worktree. The
command then looks for a sub-project-only script inside the umbrella. `python3`
exits 2 for a missing file, and a `PreToolUse` exit 2 cancels every Bash call,
so the session looks broken for reasons that have nothing to do with the gate.

### Owner

One shared implementation, thin compatibility wrappers:

```text
scripts/agent-checks/claude_hook_dispatch.py   <- all behavior
.claude/hooks/quality-gate.py                  <- wrapper
.claude/hooks/workflow-gate.py                 <- wrapper
.claude/hooks/claude-hook.cjs                  <- Node wrapper used by Finch
```

The wrappers only name their hook and hand over. Change behavior in the shared
module, never in a wrapper.

### What the dispatcher does

1. Reads the hook payload from stdin once.
2. Takes `cwd` from the payload. Only an absolute path to an existing directory
   is accepted; a relative or malformed value is refused rather than resolved
   against the process directory.
3. Walks upward from that directory for the nearest real
   `.claude/hooks/<hook name>`. The walk stops at the owning repository or
   worktree root, at the filesystem root, or after a fixed depth, so one project
   can never borrow another project's gate.
4. Skips any candidate that is a dispatcher wrapper itself, including this file,
   so the dispatcher cannot call itself. An environment re-entry guard backs
   this up.
5. Runs the real hook with the project/worktree as cwd and forwards the exact
   stdin bytes.

### The two outcomes must stay separate

This is the part that is easy to get wrong:

| Situation | Behavior |
| --- | --- |
| No applicable project hook exists | Metadata-only warning on stderr, exit 0. |
| The real hook ran | Its stdout, stderr, and exit code pass through unchanged. |
| The real hook timed out or could not start | Error exit, never a pass. |

Never collapse these into one branch. A pattern like:

```text
[ -f gate.py ] && python3 gate.py || exit 0
```

turns a genuine gate rejection into a success, which is worse than the bug it
appears to fix. Missing infrastructure and a real rejection are different
answers and must stay different code paths.

Warnings are metadata-only on purpose: no command content, no payload body, no
filesystem paths.

### Scope

The dispatcher covers every project hook name currently referenced by an
active Sifututor project when that name is otherwise missing from the umbrella.
Thin Python, Node, shell, and PowerShell wrappers all delegate to the same bounded
Python owner. Wrapper arguments are forwarded, which preserves Finch's
multi-mode `claude-hook.cjs <mode>` contract and Kelas's
`run-shared-hook.sh <shared-hook>` contract. PowerShell wrappers are installed
and configuration-tested on macOS; actual PowerShell execution is tested only
on a host with `powershell.exe`, `pwsh`, or `powershell` available.

Readiness never relies on a hard-coded list of important gate names. Any
unresolved `PreToolUse` hook fails readiness because an unknown safety gate can
block commands just as completely as a known one. Missing hooks for lifecycle
events remain advisory, but the current baseline provides wrappers for them so
context and memory events are not silently lost in umbrella-launched sessions.

### Readiness check

```bash
python3 scripts/agent-checks/claude_hook_dispatch.py
python3 scripts/agent-checks/claude_hook_dispatch.py --root <workspace> --json
```

`agent-os-adapter-readiness.py` owns this as `CL-052` (dispatcher fixtures) and
`CL-053`/`CL-054` (configured hook paths that cannot resolve for the current
launch scenario). `CL-053` fails; `CL-054` reports the non-blocking residue.
`agent-os-health.sh` runs the readiness script, so the fixtures execute once in
the normal sweep rather than twice.

### Defense in depth, not a substitute

The wrappers make an umbrella-launched session survive. They do not make it
equivalent to a session launched inside the worktree. For heavy command work,
launch the session inside the intended worktree; see
[parallel-work-and-worktrees.md](parallel-work-and-worktrees.md).

## Short Replies

Short replies depend on visible conversation context.

| Hafiz says | Hook/agent meaning |
| --- | --- |
| `proceed` | Continue the last clear safe recommendation. |
| `proceed next` | Continue the next review/action from visible chat context. |
| `approve` | Execute the last exact approval request only. |
| `what next` | Give one next recommended action. |

Only continuation-like prompts should trigger smart resume. The mere presence
of an old Session Map or diverged Git state must not turn a new prompt into a
recovery workflow. For `continue`, `resume`, `go next`, and equivalent prompts,
Codex should read
the Session Map Reference Pack first, then say whether the map matches the
prompt. If it matches, continue from the map. If it does not, treat the prompt
as new work unless Hafiz asks to resume the old map.

The hook should not guess an old hidden approval. If visible context is missing
or risky, Codex must ask a short clarification.

## Critical Lane Override

Even if a prompt looks simple, these domains force stricter routing:

- auth,
- payment,
- invoice,
- commission,
- migration,
- deployment,
- production data,
- mobile API contract.

Default behavior:

```text
read-only diagnosis first,
recommendation second,
implementation only after Hafiz approves.
```

## Hook Boundaries

The hook may:

- add context,
- suggest a skill,
- inject Koda memories,
- check Koda health,
- remind Codex about save-session,
- remind Codex about session-map,
- block unsafe Bash patterns through guard scripts,
- mark a provider credential-reveal boundary without storing prompt or page
  content,
- block whole-environment, raw credential-file, secret-store, and every tool
  during a provider-key reveal boundary before any arbitrary browser/script
  path can return the sensitive value,
- clear the quarantine after an explicit safe-state prompt, session stop, or
  replacement session start.
- request and emit a non-authoritative Jev shadow route after local critical
  and secret checks pass.

The hook must not:

- commit,
- push,
- merge,
- open a PR,
- deploy,
- mutate production,
- read `.env*`,
- reveal secrets,
- modify `live/`,
- approve its own action,
- override Hafiz.

## When To Change The Dispatcher

Change the dispatcher only when:

- a routing mistake repeats,
- a new workflow skill is added,
- a safety boundary changes,
- a prompt category is consistently misclassified,
- Hafiz confirms a new short-command meaning,
- an eval fixture is added or updated to lock the behavior.

Do not change dispatcher code just because one prompt was awkward. First update
the docs or add a scenario example unless the bug is clearly dangerous.

Use [agent-os-enforcement-drift.md](agent-os-enforcement-drift.md) before
turning a workflow preference into hook behavior. Plain meaning: if the mistake
is dangerous, repeated, and easy to detect, a hook may be right. If it needs
judgment, keep it in the playbook/skill and test it with evals instead.

## Required Checks After Dispatcher Changes

Run the focused checks first:

```bash
scripts/agent-checks/agent-os-conversation-fixture-runner.py
scripts/agent-checks/agent-os-eval-runner.py
scripts/agent-checks/agent-os-response-shape-runner.py
scripts/agent-checks/agent-os-adapter-readiness.py
scripts/agent-checks/workflow-doctor.sh
```

After a change to the Claude project hook dispatcher, run its fixtures first:

```bash
python3 -m unittest discover -s scripts/agent-checks -p 'test_claude_hook_dispatch.py'
```

`workflow-doctor.sh` owns the full completion sweep and runs
`agent-os-health.sh` internally. Do not run both back-to-back.

Before commit, also run:

```bash
scripts/agent-checks/pre-commit-guard.sh
git diff --check
```

## Related Docs

- [codex-hook-trust.md](codex-hook-trust.md): what hook commands Hafiz should
  trust.
- [agent-os-skill-registry.md](agent-os-skill-registry.md): what workflow
  skills exist and what they do.
- [agent-os-routing-model.md](agent-os-routing-model.md): routing model and
  prompt categories.
- [agent-os-approval-gates.md](agent-os-approval-gates.md): approval
  boundaries.
- [agent-os-infrastructure.md](agent-os-infrastructure.md): full Agent OS
  infrastructure map.
