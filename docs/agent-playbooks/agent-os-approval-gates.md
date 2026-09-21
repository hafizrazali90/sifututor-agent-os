# Agent OS Approval Gates

Status: draft accepted for Agent OS, docs, and workflow work; review again
after real use.

This playbook defines what Codex, Claude, and future agents may do alone, what
can be approved as one work packet, and what must always get separate Hafiz
approval.

The model is:

```text
Explain what done means first.
Relaxed inside a clear safe work packet.
Strict at risk boundaries.
Ask for one clear autopilot boundary instead of many micro-approvals.
```

## Why This Exists

Hafiz wants agents to be proactive without becoming annoying. The agent should
not ask for permission after every small docs edit, check, or living-draft
update when the direction is already clear.

At the same time, the Agent OS must not let convenience weaken expensive
boundaries such as deploys, production, secrets, payment, auth, invoices,
commissions, migrations, mobile API contracts, protected branches, or
destructive git actions.

The practical compromise: for multi-step work, the agent should explain what
done means first, then ask Hafiz for one clear stopping point, then keep moving
until that point. "Done" may mean diagnosed only, fixed locally, committed, PR
opened, staging verified, production live, or production monitored. Anything
outside that named boundary still needs a fresh explicit decision.

Use [agent-os-workflow-lanes.md](agent-os-workflow-lanes.md) to name the
execution depth before asking for approval. Plain meaning: first say the
recommended finish state, then say which boundary needs approval.

Previously agreed context counts. If the current task context already contains
the scope, path, approvals, and stop point, the agent should continue through
that approved path without asking again for the same decision. The agent pauses
only when something new changes scope, risk, evidence, access, or approval.

## Current Scope

This relaxed model applies immediately to:

- Agent OS architecture review
- docs and playbook updates
- workflow design
- eval updates
- non-destructive health checks
- living drafts during a discussion Hafiz has asked to document

Product development can reuse this model later, but only after the workflow
lanes, verification rules, and critical-lane behavior are reviewed.

## Approval Modes

### 1. No Approval Needed

Agents may do these during non-trivial work without stopping to ask, as long as
the action is non-destructive and inside the current request:

| Action | Conditions |
| --- | --- |
| Read normal docs and code | Do not read `.env*`, production secrets, or modify `live/`. |
| Search files, git status, and git diff | Keep it scoped to the current repo/task. |
| Run safe local checks | Commands must be non-destructive and not require production access. |
| Use approved auto-read access | Only the narrowest task-relevant read-only lane from `agent-access-map.md`; no writes, deploys, mutation, or secret output. |
| Update living draft docs | Only when Hafiz asked to document the discussion or said to proceed. |
| Link a new docs source from indexes | Only when it is part of the current docs/workflow packet. |
| Save a clear correction to Koda | Only behavior-changing lessons; no secrets or vague progress notes. |
| Recommend the next step | Give one practical next action, not a long menu. |

### 2. Work Packet Approval

When Hafiz says `proceed`, `proceed next`, or confirms the recommendation, the
agent may complete the safe packet without asking for each substep.

For any packet with more than one natural step, the agent should explain what
done means, recommend the stop point, show the suggested path, and name the
autopilot boundary before or at the start of execution.

Use the compact version for simple work and the full version for risky or
multi-step work. The goal is clarity, not ceremony.

Examples:

```text
What done means: docs are updated and checks pass.
I will proceed until: local docs checks pass.
I will only pause if: scope changes or checks fail.
```

```text
What done means: the PR is opened and ready for review.
My recommended stop point: PR opened.
Suggested path: diagnose -> fix -> test -> review -> commit -> push -> open PR.
Autopilot boundary: I will continue until the PR is opened, then stop.
I will only pause if: new scope, risk, evidence, access, or approval issues appear.
```

```text
What done means: staging QA passes for the changed workflow.
My recommended stop point: staging verified.
Suggested path: diagnose -> fix -> test -> review -> PR -> staging deploy -> staging QA.
Autopilot boundary: I will continue until staging QA passes, then report before
production.
I will only pause if: staging evidence fails, scope changes, or production/critical risk appears.
```

```text
Autopilot boundary: I will work one by one and ask before each major gate.
```

Allowed work-packet actions:

| Packet | Agent May Include |
| --- | --- |
| Agent OS architecture/docs review | Discuss next layer, update source docs, update roadmap, update evals, run docs checks. |
| Docs edit + checks | Edit playbooks/docs, update links, run Agent OS health/guard checks. |
| Create issue + document plan | Create a GitHub issue and write or update the plan when scope is clear and non-critical. |
| Verify + QA | Run non-destructive verification and QA checks, then report evidence and gaps. |

Stop the packet when:

- the next step is ambiguous
- the scope changes materially
- a separate-approval boundary appears
- required evidence is missing for the state being claimed
- commit, push, merge, PR, deploy, destructive, secret, or production action is
  needed
- a critical-lane implementation decision is needed

Use the Evidence Gap Stop Rules in
[agent-os-evidence-model.md](agent-os-evidence-model.md) before saying a work
packet is ready. Plain meaning: an agent may continue through safe docs/checks
inside an approved packet, but it must stop or clearly name the limitation when
missing proof would make the next state misleading.

Before asking to push a local batch, apply the Batch Completion Rule from
[working-with-hafiz.md](working-with-hafiz.md). The batch must tell one clear
story, have no half-written rules or workflows inside it, have passing required
checks, and clearly separate future work that is not included yet. If any of
those are false, keep working locally instead of asking for push approval.

Use [push-pr-ci-automation.md](push-pr-ci-automation.md) when the packet may
include push, PR creation, CI monitoring, or merge. Plain meaning: PR opening
and CI watching can be automated after one clear boundary, but PR approval,
merge, deploy, production, destructive actions, and critical-lane work stay
tied to the approved stop point.

Use [release-deploy-live-monitoring.md](release-deploy-live-monitoring.md) when
the packet may include staging deploy, production deploy, live smoke, or
monitoring. Plain meaning: deploy and production release stay explicit, but the
agent can automate preflight, safe smoke, read-only monitoring, and final state
reporting inside an approved release boundary.

Use [autonomous-work-packets.md](autonomous-work-packets.md) when the packet is
long-running or loop-based. Plain meaning: this playbook decides the approval
boundary, while autonomous work packets decide loop limits, progress cadence,
retry behavior, commit behavior, and stop rules inside that boundary.

### 3. Standing Task Access Approval

Hafiz has granted standing task-scoped approval for agents to use the narrowest
required local access files and connected tools when he has already asked the
agent to finish a task end-to-end.

This also applies to evidence gathering inside all Agent OS workflows. When
accuracy depends on current evidence, the agent should proactively use the
narrowest relevant approved read-only access instead of waiting for Hafiz to
say "check the tool" or "verify with access".

This means the agent should not stop to ask another permission question just to
read an approved local agent-access file or run a connected read-only tool that
is needed for the active task. Examples:

- safe read-only access during diagnosis, planning, verify, QA, review, and
  monitoring
- authenticated production smoke after Hafiz says to continue until deploy
- read-only monitoring tokens after Hafiz asks for post-deploy monitoring
- scoped server access when a deploy/preflight task already requires it
- backup access when a production release playbook requires a pre-deploy backup

Plain rule:

```text
Auto-read by default when it helps accuracy.
Limit by scope and safety, not by unnecessary permission prompts.
```

Standing access approval is not blanket access. The agent must still:

- use the narrowest relevant access file or tool
- explain the evidence source used when it affects the recommendation
- keep secrets out of chat, docs, screenshots, logs, commits, and Koda
- avoid repository `.env*` files and `live/`
- avoid unrelated credentials or systems
- avoid broad evidence gathering outside the active task
- stop before destructive data/file actions unless Hafiz explicitly requested
  that destructive action
- keep deploy, push, PR, merge, and critical-lane implementation tied to an
  explicit current-session task instruction

### 4. Exact Bundled Approval

The agent may ask once for a bundle when the bundle is exact and naturally
belongs together.

Allowed bundles:

| Bundle | Requires |
| --- | --- |
| stage + commit | Exact file list and commit message. |
| commit + push | Exact file list, commit message, branch, remote target, checks, and a human-first Push Package Summary. |
| commit + close issue | Issue number and completion evidence. |
| push + close issue | Commit already made, exact branch/remote, human-first Push Package Summary, and issue clearly complete. |
| docs edit + checks | Exact docs scope and non-destructive checks. |
| verify + QA | Exact non-destructive commands or safe check scope. |
| push + open PR + monitor CI | Exact branch/remote, PR target, evidence plan, and stop-before-merge boundary. |
| PR ready + merge if CI passes | Exact branch/PR target, merge boundary, no critical-lane risk, required checks, and stop-before-deploy boundary. |
| deploy + smoke + monitor | Exact source commit/PR, target environment, deploy approval, smoke scope, monitoring scope, and stop-before-new-fix/rollback boundary. |

If Hafiz says `approve` after the agent asked for an exact bundle, approval
covers the whole named bundle.

If the agent asked only for commit, `approve` means commit only. If the agent
asked for commit and push, `approve` means commit and push.

If the agent asked for an autopilot boundary such as "until merged, stop before
deploy", `approve` covers all normal steps required to reach that boundary:
review, checks, exact file-list inspection and reporting, commit when the files
remain inside the agreed scope, push, PR, and merge when allowed. It does not
cover deploy because deploy was explicitly excluded. Do not pause for a second
file-list approval unless review discovers material new scope, risk,
destructive work, critical-lane expansion, or a boundary conflict.

If the boundary is "until PR ready", `approve` covers branch push, PR creation,
PR body/checklist, CI monitoring, and in-scope CI fixes. It does not cover merge
unless merge was named.

If the boundary is "until production monitored", `approve` covers release
preflight, deploy execution only after deploy approval is explicit, deployed
state verification, safe smoke checks, read-only monitoring, and final release
reporting. It does not cover rollback, new fixes, destructive action, critical
lane widening, or final business risk acceptance unless those were named.

### 5. Separate Approval Always

These actions must not be hidden inside a larger bundle:

| Action | Why |
| --- | --- |
| Deploy or production release | Can affect real users and revenue. |
| Merge to protected branch | Changes shared source of truth. |
| Open PR | Creates external review/state; ask unless explicitly requested. |
| Production log access or production data action outside the active task | May expose sensitive operational data; use standing task access only when the current task already requires the scoped check. |
| Auth/payment/invoice/commission/migration/mobile API implementation | Critical-lane changes need diagnosis first and approval before implementation. |
| Destructive cleanup | File/data loss risk. |
| Force push, reset, rebase, or history rewrite | Can destroy or confuse shared work. |
| `.env*`, secrets, credentials, raw tokens | Forbidden to read, expose, or commit. |
| Modify `live/` | `live/` is read-only reference. |
| Use or change Plane | Plane is not part of the default Agent OS path; use it only if Hafiz explicitly asks in the current session. |

## Short Command Semantics

| Hafiz says | Meaning |
| --- | --- |
| `proceed` | Continue the last clear safe recommendation. |
| `proceed` / `continue` / `yes` / `ok` after an exact commit-only recommendation | Commit exactly that listed bundle, after guard/checks, and stop before push. |
| `proceed next` | Continue the next review/action from visible chat context. |
| `proceed until done` / `continue until done` | Treat as end-to-end intent. Explain what done means, how far the agent can go now, and what approval is needed to go further. |
| `proceed until production` | Treat as release intent. Name whether the practical finish state is deployed, live checked, monitored, or accepted/closed; then require the needed deploy/release approvals. |
| `proceed until finish` after a clear approved path | Continue using the already-approved path. Do not re-ask for approvals already included in the current task context. |
| `approve` | Approve the last exact approval request, including a bundle if the request named it. |
| `yes` | Confirm the current recommendation or discussion point; act if the action is clear and safe. |
| `what next` | Recommend one next step; do not scatter options unless there is a real decision. |
| `autopilot until <boundary>` / `finish this end to end` / `do everything needed` | Continue through the named or natural safe path and stop at the boundary or any unapproved risk gate. |
| `autopilot this` / `keep going until fixed` / `clean up this batch` | Translate it into an autonomous work packet with finish point, loop rules, stop rules, progress cadence, and out-of-scope actions. |

If there is no clear previous recommendation or exact approval request, ask one
short clarification.

## Agent Behavior

During a safe work packet, the agent should:

- explain what done means, then ask for or state the autopilot boundary when the
  work has multiple connected steps
- recommend the stop point and suggested path so Hafiz does not need to know or
  list every workflow step
- treat short replies as commit-only approval only when the immediately previous
  recommendation named an exact commit-only bundle and stop-before-push boundary
- recognize natural end-to-end intent instead of requiring the exact word
  `autopilot`
- check whether the path was already approved in the current task context before
  pausing at a normal approval boundary
- say "I will only pause if..." using context-aware reasons, not a generic wall
  of approval labels
- keep moving until the packet is complete or hits a boundary
- give short progress updates while working
- update living docs as decisions are made
- run relevant non-destructive checks
- report what changed, how it was checked, and the next recommended action

The agent should not:

- ask Hafiz to approve every small docs edit
- ask separately for every natural substep after a boundary has already been
  approved
- treat a relaxed docs packet as approval to commit or push
- silently expand from architecture/docs into product code
- bundle deploy, production, secrets, destructive actions, or critical-lane
  implementation with ordinary workflow work
- ask for another access approval when Hafiz already asked the agent to finish
  an end-to-end task and the scoped access is necessary to complete it

## Machine-checkable transfer status

`scripts/agent-checks/agent-os-task-context.py` provides schema-validated,
task-specific approval transfer and a guarded callback seam. Transfer preserves
the same task and owner-approval reference; adding operations or removing
exclusions is rejected even if a worker invents a different reference string.
Only a trusted adapter that independently verifies actual owner authorization
may issue a new boundary. Initial boundary creation is a trusted-caller API,
not proof that arbitrary files or worker-supplied references are authentic.

The controlled fixture worker exercises reload -> check -> invoke, routine
failure -> diagnosis -> correction -> rerun, follow-up tracking -> return to
main, and rejection before an unapproved tool is invoked.

The shared `scripts/agent-checks/agent-os-approval-guard.py` is registered locally
in Codex and Claude `UserPromptSubmit`, `PreToolUse`, and `SessionStart` hooks.
It reloads `.agent-os/approval-state/tool-packets/<session-key>.json` on each
invocation. Registered paths are absolute for this machine so a subdirectory cwd
does not lose the guard. Claude's `.claude/settings.json` is local/gitignored;
the registration is not a committed cross-machine rollout.

`UserPromptSubmit --identity` exposes only the provider's exact current session
identifier and canonical cwd. `SessionStart --resume` provides the same identity
at startup/resume/compaction, then appends a saved boundary only when it validates
for that same identity. The identity and lifecycle commands share one matching
hook group per event so every required command is reviewed and dispatched
together. Neither path stores prompt text, inspects approval words, chooses a
newest session, or creates authority. Interleaved
sessions therefore carry their own identity instead of inheriting whichever task
ran most recently. Missing or invalid identity emits no usable enrollment data.

Trusted-supervisor enrollment uses `supervised_enroll`: verify the real owner's
task instruction, retain its approval reference, review exact NON-SECRET tool
calls inside the approved operations, and pass the current hook payload so the
packet binds to that payload's session and canonical worktree. The lower-level
`activate_approval_packet` remains available for controlled adapters/tests.
When the task later needs another exact call inside the same owner-approved
operations, `supervisor_extend_packet` appends the newly reviewed signature while
deriving task identity, scope, exclusions, and provenance only from the existing
validated packet. It cannot change the boundary, use another session/worktree,
or add a call mapped to an excluded operation. Repeated calls are deduplicated.
Only hashes of these reviewed calls are persisted, never raw commands or secret
values/fingerprints. Never enroll credential-bearing input. Runtime checks use
actual `tool_name` and full `tool_input`; labels/approval references supplied in
the payload are not authority. Different inputs (including another workdir),
unknown calls, corrupt enrolled state, and a mismatched cwd are denied. Matching
produces context, never `permissionDecision: allow`, so other guards and native
permission checks remain effective. Transfers cannot add grants silently;
new invocations require supervisor review inside existing owner scope through
the extension API, not a routine request for Hafiz to repeat the same approval.
Codex normalizes unified shell execution to canonical hook tool name `Bash` with
the command in `tool_input.command`; enrollment must use the provider's canonical
hook payload rather than its user-facing tool alias.

Unenrolled sessions or providers without a supported session identifier fall
back quietly to existing gates; this is NOT an authorization or enforcement
success. A resume hook restores included/excluded operations only for the
matching session and canonical worktree. No newest-map discovery or automatic
natural-language approval parser can create a packet.

Automated tests prove local guard subprocess dispatch, current-identity output,
supervised enrollment/extension, and temporary enrolled packets. A bounded live
check on 2026-09-19 additionally proved identity delivery and enrolled allow/deny
behavior in fresh Claude Code 2.1.222 and Codex CLI 0.154.0 sessions: reviewed
`pwd` executed, while unreviewed `pwd -P` was denied in both adapters. Codex hook
trust was then persisted interactively and a fresh non-interactive session loaded
the identity hook without the automation-only trust override. This proves the
current machine/configuration, not cross-machine rollout or every provider/tool.
Fresh owner-authorization authentication remains intentionally outside the
natural-language worker. A trusted Agent OS supervisor can enroll and extend the
current session from verified owner scope without asking Hafiz to repeat it, but
prompt wording alone must never trigger enrollment. Writable local metadata/hooks
are not a security sandbox against a malicious worker with filesystem access.
Existing approval/safety rules apply.

Protocol references checked during implementation: [OpenAI hooks](https://developers.openai.com/es-419/docs/hooks)
and [Claude Code hooks](https://code.claude.com/docs/en/hooks). Provider support
does not prove installed dispatch.

## Review Later

This model should be reviewed after real use.

Watch for:

- bundled actions that still feel annoying
- packets that feel too broad
- places where the agent should have stopped earlier
- places where the agent asked for approval too often
- any near-miss around production, secrets, critical lanes, or git history

Use [workflow-efficiency-audit.md](workflow-efficiency-audit.md) when this
review finds repeated friction. Plain meaning: do not keep adding approval
rules blindly; inspect where the workflow is wasting Hafiz's time, where the
agent should automate mechanical work, and where risk decisions still belong to
Hafiz.
