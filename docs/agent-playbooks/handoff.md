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

### Provider-neutral packet and reconciliation

Use the same task contract for every worker, with provider-specific execution
remaining in the proven adapter. `delegation_packet.py` supports `check`,
`brief`, `preflight` and `assess-handback`. It does not launch a provider, grant
permission, run evidence commands, restart a worker or certify semantic truth.
The existing Claude Max runner below keeps its version-1 job format unchanged.
Other workers may consume the portable brief through their approved adapter;
an unsupported launch path remains unsupported, not a guessed CLI command.

Start from `templates/delegation-packet.json` and fill in the real task, issue,
supervisor/worker IDs, exact worktree/branch/base revision, expiry, owned paths,
acceptance IDs, exclusions and source-backed brief. This envelope supplements
the Build-Ready Pack, not replaces it. Use the model-neutral completion receipt
defined in `agent-os-evidence-model.md`; do not invent another handback schema.

`brief_sha256` pins the original brief's exact bytes; both preflight and return
reconciliation verify those bytes (maximum 1 MiB). Pin source requirements and
their meaning inside the brief, not just mutable links. An unchanged brief path
is not an unchanged contract. A revised brief requires a new supervisor-approved
packet and digest, never a worker silently renewing the old one.

```bash
python3 scripts/agent-checks/delegation_packet.py check --packet /absolute/path/packet.json
python3 scripts/agent-checks/delegation_packet.py brief --packet /absolute/path/packet.json
python3 scripts/agent-checks/delegation_packet.py preflight --packet /absolute/path/packet.json --capabilities /absolute/path/capabilities.json
python3 scripts/agent-checks/delegation_packet.py assess-handback --packet /absolute/path/packet.json --receipt /absolute/path/receipt.json --expected-contract-sha256 <supervisor-pinned-sha256> --expected-target-revision <reviewed-diff-snapshot>
```

Keep packets and handbacks in the worktree's ignored `.agent-os/delegations/`
area. Keep the digest and task-to-contract binding in the supervisor's own
session record before launch, outside worker control. A digest supplied by the
worker or recomputed after it changes the packet is not approval. The capability
record must match the supervisor-selected tool/version/provider/model/config
and environment identity, be current, and contain observed evidence for every
required capability. It is still an attestation; the supervisor verifies access
through the approved adapter. Never weaken capability requirements to pass.

Also pin the independently reviewed target snapshot separately from the starting
Git commit. For uncommitted work, inventory and hash the complete relevant dirty
diff and new files; the base commit alone cannot identify the tested candidate.
`--expected-target-revision` compares that supervisor-controlled identifier to
the receipt. The local-only receipt must name the exact worktree as environment
and `changed_locally` as state. The helper does not generate or authenticate the
snapshot: the supervisor must retain and inspect its underlying evidence.

The loop is prepare -> adapter preflight -> scoped worker -> receipt -> exact
binding/obligation check -> independent evidence review. A process exit only
starts reconciliation. A receipt with missing obligations or wrong task/worker
or contract binding cannot advance. A structurally valid accepted receipt still
requires reading the actual diff and challenging its evidence. Retain per-round
counts in supervisor state; `--correction-round` is an input, not a tamper-proof
counter. At the packet's correction limit, reconcile the failure before creating
a new packet; do not restart blindly or widen access automatically.

This release's neutral helper accepts local implementation/local proof only.
It does not silently inherit release authority or extend the existing runner's
merge/deploy restrictions. Release-capable adapters and unattended supervision
remain separate work requiring exact approval and live adapter proof. Unknown
usage stays `unavailable`; faster parallel execution is not measured net savings.

`check` returns 0 for valid structure, not authority. `preflight` returns 0 for
matching Git identity and declared observations, not an authenticated provider
launch. `assess-handback` returns 0 for valid receipt shape and binding, never
product acceptance. Metadata always says `semantic_acceptance_proven: false`.
The `brief` action intentionally prints the supplied task content; supply only
sanitized context. Other results contain field codes, not raw input/errors.

Use this path when Claude is the bounded execution worker and Codex remains the
owner of supervision, evidence reconciliation, and independent review.

Plain meaning:

```text
Claude can carry the heavy implementation load, but the job must prove it can
start, remain visible while quiet, return evidence, and stop at the agreed line.
Codex still checks the result independently before the next approval gate.
```

### Standard Job Brief

### Literal artifact acceptance (optional, model-neutral)

Before launch, pin known failure patterns in the packet's optional
`artifact_checks` list. Each entry has `path` (worktree-relative),
`required_lines`, `forbidden_lines`, `max_words` and `sha256` (null or an exact
source-content hash). Required/forbidden values match whole lines, not meaning.
The packet digest includes these checks; keep the trusted digest outside the
worker's control. Paths must stay inside the worktree and outside protected paths.

Run `delegation_packet.py check-artifacts --packet <packet.json>
--expected-contract-sha256 <supervisor-pin>` before accepting the handback.
`assess-handback` also runs declared artifact checks. Results contain only error
codes; no artifact text is printed, no commands executed, no authority granted.
Old version-1 packets without this optional field remain valid.

Use unchanged-source hashes for archival inputs and short exact assertions for
facts that must not drift. Limit ordinary handbacks to 300 words unless the
task requires more. Pin the actual worker worktree separately from the eventual
installation target. A local candidate is never automatically installed in root.
Check repeated sections and stale continuation instructions independently:
literal matches can be satisfied inside quotes and cannot prove semantic truth.
Unknown dates, owners, runtime identities and status remain explicitly unknown;
do not invent them or relabel historical status to make formatting checks pass.

After one consolidated correction, reconcile surviving defects and decide whether
to take back narrowly scoped work; do not launch repeated review-only jobs blindly.
Record parent edits, setup errors and actual elapsed time. A clean process exit,
short report or passed assertions does not prove net savings or autonomous quality.

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

For the return side, `required_proof` and the brief's return contract must
also apply the [Builder Completion Proof
Contract](agent-os-evidence-model.md#builder-completion-proof-contract) for
delegated, cross-system, cross-module, and user-facing work: the
acceptance-to-proof map, real entry point and production callers, the
bypass-path sweep, authoritative-result convergence, permission/configuration
reachability, flag-off/unavailable behavior, and a negative-control or
failing-first proof. The Build-Ready Pack governs what to build; the Builder
Completion Proof Contract governs what a completion claim must prove. A
handback that only satisfies the brief's literal checklist without this
evidence is builder evidence, not a proven completion state.

The job must set `builder_completion_proof.mode` explicitly. Normal delegated
implementation uses `required`; the runner then requires every named proof
field from the return template as a nonempty `field: value` record. Generic
`required_proof` labels cannot substitute for those fields. A genuinely
non-implementation task may use `not_applicable` only with a nonempty reason
configured before launch, and the handback must repeat that exact reason in
`builder_proof_not_applicable`. The worker cannot downgrade the contract after
launch. Supplementary `required_proof` labels must still occur verbatim. These
checks prove structural completeness only, not that the associated claims are
true.

The first runner release refuses merge, deploy, production, live-check, and
monitoring finish points. Those remain normal human-approved release workflows,
not delegation automation.

### Readiness And Launch

Run the filtered preflight before Claude starts. Do not launch delegated work
with a direct `claude` command; the watchdog is the only approved launcher.

```bash
scripts/agent-checks/agent-os-claude-delegation.py preflight \
  --job .agent-os/delegations/<job-id>.json
```

The preflight proves:

- the runner itself did not inherit a Claude auth token, API key, endpoint, or
  provider-selection override; it fails closed before probing Claude at all
  and reports only unsafe variable names, never their values. Unset every
  named variable before relaunch; never edit the job file to route around this
  block;
- Claude CLI, version, and read-only installation doctor are healthy;
- authentication is a genuine first-party Max subscription: `authMethod`,
  `subscriptionType`, and `apiProvider` must all agree. A login that looks
  like Max on the first two fields but reports a non-first-party `apiProvider`
  is exactly the reported #28 incident (Max login shown, request actually
  billed through an inherited API key) and still fails closed;
- recognized billing override variables are also removed from every Claude child process as
  defence in depth;
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

#### Paid provider evaluation or canary work

This watchdog is Max-only. A job may optionally declare `paid_evaluation`
metadata (`approved_by`, `estimate_usd`, `hard_cap_usd`, with the hard cap at
or above the estimate) for planning visibility. Because the job file is locally
editable, it is explicitly an untrusted declaration: it does not prove Hafiz
approved spending and never unlocks paid billing here. Preflight still fails
closed on an inherited override or non-Max auth. If paid provider evaluation
or canary work is genuinely needed, run it through a separate,
manually-supervised path outside this automated runner. That path must obtain
Hafiz's approval from a trusted current-session source and record a visible
cost estimate and hard spend cap before the first call; never infer authority
from `paid_evaluation` in this job file.

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
| `returned` | Claude exited successfully and the configured handback items are structurally present. This is not semantic acceptance. | Begin independent Codex review; do not call the product work accepted yet. |
| `incomplete` or `failed` | The handback is missing or the worker exited unsuccessfully. | Preserve evidence, diagnose, and report the exact next action. |

The watchdog never kills, restarts, resumes, approves, commits, pushes, merges,
deploys, or mutates production. A stall is an alert, not permission to act.

### Evidence And Independent Review

The evidence report stores timestamps, state transitions, event counts, Git
start/end state, brief/handback hashes, available usage counters, and whether a
stall occurred. It deliberately stores no raw Claude stream content. If the CLI
does not expose usage, record `unavailable`; never estimate savings.

After `returned`, Codex must still:

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
