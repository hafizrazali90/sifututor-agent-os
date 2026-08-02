# Handoff Playbook

Use this when the user asks to hand work to Claude, Codex, or a future human.

## Goal

A handoff should let the next session continue without archaeology. It is
lighter than a full report, but more specific than "done."

Plain meaning:

```text
The next person or agent should know the main goal, the current position, what
is proven, what is not proven, and exactly where to continue.
```

## Steps

1. Identify the project, branch, and active task.
2. Summarize what changed in plain language.
3. List files or areas the next agent should inspect first.
4. State what is safe to continue and what needs approval.
5. Store durable lessons in Koda when they are not already recorded.
6. Point to verification, QA, or blockers.
7. Name the highest proven state: changed locally, committed locally, pushed,
   PR open, merged, deployed, live checked, accepted, or closed.
8. Include the return path: the single next action the receiver should take.

## Continuation Pack

For non-trivial handoff, include:

- main goal and why the work started
- current focus and exact next step
- branch, dirty state, ahead/behind state, and local-only commits
- files, commits, PRs, issues, Session Map, or Mission Ledger references
- checks that passed, checks that failed, and checks not run
- open decisions for Hafiz or a human owner
- approval boundaries: push, PR, merge, deploy, production, critical-lane,
  destructive, secret, or broad access
- do-not-redo context: what the next agent can reuse, and what it should verify
  from current sources before acting

If the work is only local, say so clearly. A local commit is not visible to
GitHub or another machine until it is pushed.

If the receiver is another LLM, add a short continuation prompt:

```text
Continue from <Session Map or file>.
Main goal: <goal>.
Current focus: <focus>.
Next action: <action>.
Check first: <git status / files / docs / evidence>.
Do not change: <boundaries>.
```

## Codex-To-Claude Max Delegation

Use this path when Claude is the bounded execution worker and Codex remains the
owner of supervision, evidence reconciliation, and independent review.

Plain meaning:

```text
Claude can carry the heavy implementation load, but the job must prove it can
start, remain visible while quiet, return evidence, and stop at the agreed line.
Codex still checks the result independently before the next approval gate.
```

### Standard Job Brief

Prepare two ignored local files under the delegated worktree's
`.agent-os/delegations/` directory:

1. A JSON job contract copied from
   `docs/agent-playbooks/templates/claude-delegation-job.json`.
2. A human-readable brief based on
   `docs/agent-playbooks/templates/codex-to-claude.md`.

The contract must name the goal, approved stop point, forbidden actions,
worktree, branch, lane owner, required proof, reporting cadence, brief path,
handback path, and Claude arguments. The brief must explain the real entry
point, business rule, scope, evidence, and exact return contract. Use the
Build-Ready Pack from `ai-implementation-readiness.md` for critical,
cross-module, user-facing, or AI-to-AI implementation work.

The first runner release refuses merge, deploy, production, live-check, and
monitoring finish points. Those remain normal human-approved release workflows,
not delegation automation.

### Readiness And Launch

Run the filtered preflight before Claude starts:

```bash
scripts/agent-checks/agent-os-claude-delegation.py preflight \
  --job .agent-os/delegations/<job-id>.json
```

The preflight proves:

- Claude CLI, version, and read-only installation doctor are healthy;
- authentication is logged in through `claude.ai` with a Max subscription;
- `ANTHROPIC_API_KEY` is removed from every Claude child process, so an unused
  API credit path cannot silently replace the subscription;
- required MCP servers are connected when the job names them;
- the declared worktree and branch match current Git state;
- no live worker owns the same worktree;
- non-interactive stream output is enabled for liveness;
- unsafe permission-bypass flags are absent; and
- the brief/state/handback paths stay inside the worktree's Git-ignored
  `.agent-os/delegations/` runtime area; and
- the state directory and handback are fresh.

Identity fields, organization identifiers, raw auth output, prompts, and Claude
response text are not written into preflight or evidence files.

Start the bounded worker only after `READY`:

```bash
scripts/agent-checks/agent-os-claude-delegation.py run \
  --job .agent-os/delegations/<job-id>.json
```

The watchdog writes `state.json`, `preflight.json`, `evidence.json`, and
`evidence.md` under the job's ignored state directory. Claude must write its
separate sanitized `handback.md` to the exact contract path.

### Non-Token Status And Worker States

Check a running worker without another Claude/Codex model call:

```bash
scripts/agent-checks/agent-os-claude-delegation.py status \
  --state-dir .agent-os/delegations/<job-id>-state
```

| State | Practical meaning | Codex action |
| --- | --- | --- |
| `starting` | Preflight passed and the worker is launching. | Wait briefly, then check status. |
| `working` | The worker process is alive and emitting events. | Continue normal supervision. |
| `working_silent` | The process is alive but has emitted no recent event. | No intervention yet; the watchdog heartbeat proves supervision is alive. |
| `stalled` | The process is alive but quiet beyond the job threshold. | Inspect status/evidence and decide whether human intervention is needed. Do not auto-restart. |
| `waiting_setup` | Authentication, trust, MCP, or another first-run setup prompt was detected. | Resolve the named setup outside the worker, rerun preflight, then launch a fresh job. |
| `unmonitored` | Claude is still alive, but the local watchdog process has stopped. | Tell Hafiz immediately, preserve the lane lock, and reconcile the worker before any relaunch. |
| `stale` | State says active but the recorded worker process is gone. | Reconcile Git and handback evidence before deciding whether to relaunch. |
| `finished` | Claude exited successfully and the required handback exists. | Begin independent Codex review; do not call the product work accepted yet. |
| `incomplete` or `failed` | The handback is missing or the worker exited unsuccessfully. | Preserve evidence, diagnose, and report the exact next action. |

The watchdog never kills, restarts, resumes, approves, commits, pushes, merges,
deploys, or mutates production. A stall is an alert, not permission to act.

### Evidence And Independent Review

The evidence report stores timestamps, state transitions, event counts, Git
start/end state, brief/handback hashes, available usage counters, and whether a
stall occurred. It deliberately stores no raw Claude stream content. If the CLI
does not expose usage, record `unavailable`; never estimate savings.

After `finished`, Codex must still:

1. read the sanitized handback;
2. inspect the real diff and Git state;
3. rerun or challenge the required proof;
4. check scope, test strength, human-journey evidence, and approval boundaries;
5. name the highest honestly proven state; and
6. ask Hafiz only for the next real gate that was not already approved.

## Copy-Safe Human Handoffs

When Hafiz asks for a handoff message he will send to a developer, staff member,
or another person, follow the copy-ready outbound-message rule in
[agent-os-communication.md](agent-os-communication.md):

- put the complete send-ready message in one fenced plain-text block
- use bare URLs instead of rendered Markdown links
- preserve blank lines, bullets, and channel-native formatting
- keep agent explanations outside the block

This is different from the continuation pack above. A continuation pack records
working state for the next agent; a copy-safe human handoff is the exact message
Hafiz can paste into WhatsApp or another destination.

## Output Shape

```text
HANDOFF - <project>

Current state:
- <branch/task/status/highest proven state>

What changed:
- <summary>

Next best step:
- <specific action>

Read first:
- <files/docs/session map/PR/issue>

Watchouts:
- <risk or none>

Evidence:
- <tests, guards, or not run>

Continuation prompt:
- <copy-paste prompt when another LLM should resume>
```
