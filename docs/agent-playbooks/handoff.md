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

### Sequential Acceptance Runbook For Large Builds

When the delegated job is cross-module, critical-lane, user-facing, or has a
large requirement/UAT pack, do not hand Claude only a narrative brief. Before
handoff, Codex must prepare one executable runbook that turns the approved
scope into an ordered loop.

The runbook must:

1. name the complete authority set and state which older prompts it supersedes;
2. give every requirement, defect and test obligation a stable ID;
3. require a materialised acceptance ledger with one row per obligation and
   per required matrix cell, rather than one family row standing in for many
   unexecuted variants;
4. sequence each implementation item as failing proof -> smallest fix ->
   focused pass -> related-impact check -> real user/system proof -> checkpoint;
5. prevent the next item starting until the current checkpoint is recorded;
6. expand operation, role, feature-flag, platform, viewport, fault and recovery
   dimensions explicitly, with `Not Applicable` allowed only with a reason;
7. require a machine-checkable exit gate, or an equivalent deterministic
   set-equality check, that detects missing, duplicate, failed, blocked and
   not-run primary obligations;
8. require every defect discovered during UAT to re-enter the same
   fail-fix-rerun loop, followed by the affected journeys; after the last
   change, use the evidence-freshness rules in `qa.md` to decide whether the
   final proof needs a complete replay or a checker-backed incremental
   campaign; and
9. forbid a completion claim when the ledger or exit checker is not clean.

For long jobs, examples and exact commands should accompany the rules. A green
unit suite, a route-exists browser check, generated-but-unreviewed screenshots,
or one test mapped to several materially different requirements does not
satisfy the runbook.

Codex remains responsible for checking that the runbook covers the approved
requirement set before delegation and for independently challenging the final
ledger, diff and evidence after Claude returns.

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

### Net Codex Usage Experiment

When the purpose of delegation includes saving Codex usage, create one durable
experiment record before launching the builder. Reuse the structure of
`.agent-os/session-maps/artifacts/crm-c4b-claude-builder-usage-experiment-2026-08-05.md`
instead of inventing a new reporting format.

The record must name the baseline, target, measurement source, and final result
for:

- provider-confirmed Codex and Claude usage, or `unavailable` when the tools do
  not expose comparable counters;
- Codex contract/planning passes, implementation edits, interventions, routine
  status model calls, final-review effort, and any work Codex took back;
- Claude jobs, restarts, handback size, and bounded correction rounds;
- wall-clock, active, blocked, and silent time when available;
- Hafiz interruptions and approval requests;
- defects found after handback, classified as blocking, major, minor, or none,
  plus whether the cause was the contract, repository, data, or execution; and
- the normal quality floor: tests, human-journey evidence, security, release
  safety, and independent review.

Transferred work is not itself proof of savings. The experiment succeeds only
when Codex performs less implementation and avoidable rework, correction loops
and user interruptions fall, and quality remains equal or better. Prefer one
complete build-ready contract, one builder loop, one fresh independent Claude
review, one narrow Codex risk/evidence review, and at most one consolidated
correction round. If a repeated defect survives, improve the contract or a
deterministic test before the next experiment instead of adding more ad hoc
review turns.

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
