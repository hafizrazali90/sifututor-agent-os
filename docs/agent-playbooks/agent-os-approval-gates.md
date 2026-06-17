# Agent OS Approval Gates

Status: draft accepted for Agent OS, docs, and workflow work; review again
after real use.

This playbook defines what Codex, Claude, and future agents may do alone, what
can be approved as one work packet, and what must always get separate Hafiz
approval.

The model is:

```text
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

The practical compromise: for multi-step work, the agent should ask Hafiz for
one clear stopping point, then keep moving until that point. The stopping point
can be "one by one", "PR opened", "merged", "staging QA passed", "deployed",
or "monitoring complete". Anything outside that named boundary still needs a
fresh explicit decision.

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
| Update living draft docs | Only when Hafiz asked to document the discussion or said to proceed. |
| Link a new docs source from indexes | Only when it is part of the current docs/workflow packet. |
| Save a clear correction to Koda | Only behavior-changing lessons; no secrets or vague progress notes. |
| Recommend the next step | Give one practical next action, not a long menu. |

### 2. Work Packet Approval

When Hafiz says `proceed`, `proceed next`, or confirms the recommendation, the
agent may complete the safe packet without asking for each substep.

For any packet with more than one natural step, the agent should name the
autopilot boundary before or at the start of execution.

Examples:

```text
Autopilot boundary: I will continue until the PR is opened, then stop.
```

```text
Autopilot boundary: I will continue until staging QA passes, then report before
production.
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
- commit, push, merge, PR, deploy, destructive, secret, or production action is
  needed
- a critical-lane implementation decision is needed

### 3. Exact Bundled Approval

The agent may ask once for a bundle when the bundle is exact and naturally
belongs together.

Allowed bundles:

| Bundle | Requires |
| --- | --- |
| stage + commit | Exact file list and commit message. |
| commit + push | Exact file list, commit message, branch, remote target, and checks. |
| commit + close issue | Issue number and completion evidence. |
| push + close issue | Commit already made, exact branch/remote, and issue clearly complete. |
| docs edit + checks | Exact docs scope and non-destructive checks. |
| verify + QA | Exact non-destructive commands or safe check scope. |

If Hafiz says `approve` after the agent asked for an exact bundle, approval
covers the whole named bundle.

If the agent asked only for commit, `approve` means commit only. If the agent
asked for commit and push, `approve` means commit and push.

If the agent asked for an autopilot boundary such as "until merged, stop before
deploy", `approve` covers all normal steps required to reach that boundary:
review, checks, commit if exact file list was named, push, PR, and merge when
allowed. It does not cover deploy because deploy was explicitly excluded.

### 4. Separate Approval Always

These actions must not be hidden inside a larger bundle:

| Action | Why |
| --- | --- |
| Deploy or production release | Can affect real users and revenue. |
| Merge to protected branch | Changes shared source of truth. |
| Open PR | Creates external review/state; ask unless explicitly requested. |
| Production log access or production data action | May expose sensitive operational data. |
| Auth/payment/invoice/commission/migration/mobile API implementation | Critical-lane changes need diagnosis first and approval before implementation. |
| Destructive cleanup | File/data loss risk. |
| Force push, reset, rebase, or history rewrite | Can destroy or confuse shared work. |
| `.env*`, secrets, credentials, raw tokens | Forbidden to read, expose, or commit. |
| Modify `live/` | `live/` is read-only reference. |
| Change Plane scope, priority, owner, roadmap direction, or production state | Hafiz owns planning and business priority decisions. |

## Short Command Semantics

| Hafiz says | Meaning |
| --- | --- |
| `proceed` | Continue the last clear safe recommendation. |
| `proceed next` | Continue the next review/action from visible chat context. |
| `approve` | Approve the last exact approval request, including a bundle if the request named it. |
| `yes` | Confirm the current recommendation or discussion point; act if the action is clear and safe. |
| `what next` | Recommend one next step; do not scatter options unless there is a real decision. |
| `autopilot until <boundary>` | Continue through the named safe path and stop at the boundary or any unapproved risk gate. |

If there is no clear previous recommendation or exact approval request, ask one
short clarification.

## Agent Behavior

During a safe work packet, the agent should:

- ask for or state the autopilot boundary when the work has multiple connected
  steps
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

## Review Later

This model should be reviewed after real use.

Watch for:

- bundled actions that still feel annoying
- packets that feel too broad
- places where the agent should have stopped earlier
- places where the agent asked for approval too often
- any near-miss around production, secrets, critical lanes, or git history
