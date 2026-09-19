# Parallel Work And Worktrees

Use this when more than one agent, session, branch, PR, fix, or long-running
task may be active at the same time.

Plain meaning:

```text
If two tasks may touch code at the same time, give them separate counters.
Do not let agents cook different dishes in the same workspace and then guess
which ingredient belongs to which dish.
```

This is inspired by Kun Chen's treehouse pattern, but Sifututor starts with a
lightweight local rule: use normal Git branches and worktrees intentionally,
record their state, and clean them up when the work is merged or parked.

## Why This Exists

Parallel work creates expensive confusion:

- one agent edits files while another assumes the repo is clean
- one branch contains unrelated fixes
- a local commit is mistaken for pushed work
- a PR is mistaken for merged work
- a merged change is mistaken for deployed or live work
- Hafiz asks "what next?" and the agent cannot name the active task
- a future session resumes stale context from the wrong branch or worktree

The goal is not to create more ceremony. The goal is to make concurrent work
safe enough that Hafiz does not need to micromanage branch state.

## When To Use Same Workspace

Same workspace is fine when:

- discussion only
- tiny docs edit
- one focused normal task
- no other agent/session is editing the same repo
- no existing dirty files conflict with the task
- the agent can explain the current branch and Git state clearly

Even then, check `git status --short --branch` before staging, committing,
pushing, PR, merge, deploy, save-session, or handoff.

## When To Use A Separate Worktree

Use or recommend a separate worktree when:

- another agent or session is working in parallel
- the task is long-running or risky
- the task may need its own PR
- the current repo is dirty with unrelated changes
- a production hotfix must stay clean
- a branch already contains unrelated work
- a PR cleanup should not disturb the main workspace
- profile/readiness verification should use clean `origin/main`
- the current session contains multiple fixes with different target states

Hard rule:

```text
Two active code tasks that may edit the same repo should not share one dirty
workspace.
```

## Recommended Workspace Choice

| Situation | Workspace recommendation |
| --- | --- |
| Tiny discussion or docs note | Same workspace. |
| One focused normal task | Same workspace or normal branch. |
| Multiple fixes in one chat | Same workspace only with Session Release Ledger; separate worktree if branches diverge. |
| Another agent works in parallel | Separate worktree required. |
| Long-running feature | Separate worktree required. |
| Risky product fix | Separate branch/worktree recommended. |
| Production hotfix | Clean dedicated branch/worktree required. |
| PR cleanup after another branch exists | Separate worktree preferred. |
| Clean profile/readiness audit | Temporary clean worktree from `origin/main` preferred. |

## Naming Standard

Use names that make the work obvious:

```text
.worktrees/<project>-<short-purpose>
```

Examples:

```text
.worktrees/sifu-invoice-adjustments-docs
.worktrees/ripple-remove-vercel
.worktrees/sifu-tutor-hotfix-mobile-filter-api
```

Branches should still follow the project branch naming rules. The worktree name
helps humans and agents scan local folders; the branch name is the Git truth.

## Required State Record

Whenever a separate worktree is created, used, handed off, or closed, record:

```text
Project:
Repo/worktree:
Branch:
Base branch:
Purpose:
Owner/session:
Issue:
PR:
Commit(s):
Highest proven state:
Next action:
Cleanup condition:
```

Save this in the Session Map, Session Release Ledger, handoff, PR body, or
save-session report depending on the work.

## Before Switching Work

Before moving from one task/worktree to another, say:

```text
Current worktree:
Branch:
Dirty files:
Local-only commits:
Pushed/PR/merged/deployed state:
Next action:
```

If anything is local-only, say it plainly. Do not let a local commit disappear
from the story.

## Before Push, PR, Merge, Deploy, Or Save

Run a stranded-work check:

```bash
git status --short --branch
git worktree list
git log --oneline --decorate --all --max-count=40
```

For every active task, answer:

```text
Which worktree owns it?
Which branch owns it?
Is it dirty?
Is it committed locally?
Is it pushed?
Is there a PR?
Is it merged?
Is it deployed or live checked?
What is the next action?
```

Use [session-release-ledger.md](session-release-ledger.md) when more than one
fix, branch, commit, PR, or deploy candidate is in play.

## Cleanup Rule

Do not delete a worktree just because the local task feels finished.

Cleanup is safe only when:

- the work is merged or intentionally abandoned
- no useful uncommitted files remain
- no local-only commits need preservation
- Hafiz or the task boundary does not need the worktree retained
- the final state is recorded in Session Map, save-session, PR, or handoff

If unsure, park it instead of deleting it:

```text
Parked worktree:
Reason:
Resume condition:
Cleanup condition:
```

## Relationship To Existing Playbooks

| Existing playbook | How this connects |
| --- | --- |
| `task-router.md` | Decide whether the task can use the current workspace or needs isolation. |
| `session-map.md` | Track long-running or parallel session state. |
| `session-release-ledger.md` | Track multiple fixes, branches, commits, PRs, and deploy states. |
| `push-pr-ci-automation.md` | Confirm the exact branch/worktree before pushing or opening a PR. |
| `save-session.md` | Preserve worktree/branch/local-only commit state before ending. |
| `no-mistakes-lite.md` | Final honesty pass before claiming ready/done/outbound state. |

## Read-Only Inventory Helper

The manual rule proved useful and repeated discovery became noisy. Use the
small read-only inventory helper instead of assembling the same state with many
separate commands:

```text
scripts/agent-checks/worktree-inventory.sh
```

For current GitHub PR evidence as well:

```bash
git fetch origin
scripts/agent-checks/worktree-inventory.sh --with-pr
```

The helper never stages, commits, pushes, removes, or prunes. Remote-branch
presence is based on local remote refs, so fetch first whenever freshness
matters. PR queries are read-only and opt-in so ordinary local inventory stays
fast.

Plain version:

```text
Use one inventory command to prove worktree state; keep all mutations explicit.
```

## Executable Lifecycle Helper

Use the provider-neutral lifecycle helper when a dedicated worktree will live
beyond one quick command or when several sessions may run together:

```bash
python3 scripts/agent-checks/worktree-lifecycle.py lease \
  --repo <repository> \
  --worktree <worktree> \
  --owner <agent-or-human> \
  --session <exact-session-id> \
  --purpose <short-purpose> \
  --issue <issue-url-or-number> \
  --cleanup-condition <plain-condition>
```

Lease state is machine-local under
`~/.local/state/sifututor-agent-os/worktrees/` by default. It must contain only
non-secret ownership metadata. Ten or more separate worktrees may hold leases
at once; the helper serializes updates and refuses a second live owner for the
same canonical path.

Refresh long-running work periodically:

```bash
python3 scripts/agent-checks/worktree-lifecycle.py heartbeat \
  --worktree <worktree> --session <exact-session-id>
```

At handback, mark it `parked` when work remains or `released` when the cleanup
condition is satisfied. A parked lease does not expire automatically. An
expired active heartbeat is a review signal, not deletion authority.

### Cross-repository proposal

Run this from the umbrella workspace:

```bash
python3 scripts/agent-checks/worktree-lifecycle.py inventory \
  --workspace /Users/hafizrazali/Projects/Sifututor
```

The classifications mean:

| Classification | Meaning | Mutation allowed |
| --- | --- | --- |
| `preserve` | Primary, dirty, locked, leased, active-task, unmerged or uncertain work. | None. Investigate or park. |
| `reclaim_candidate` | Clean, unlocked, inactive and fully contained by the configured base. Process ownership is still rechecked at apply time. | Exact-path removal may be considered. |
| `prunable_registration` | The checkout path is already missing; only stale Git administration metadata remains. | `prune-missing --apply` may remove the registration; branches/commits remain. |

Age never creates permission. Before applying reclamation, the helper requires
the exact expected HEAD and re-runs status, ignored-file, task, lease, ancestry,
lock and process-cwd checks. It uses ordinary `git worktree remove`, never
`--force`, and never deletes branches:

```bash
python3 scripts/agent-checks/worktree-lifecycle.py reclaim \
  --repo <repository> --worktree <exact-path> \
  --expected-head <full-sha> --apply
```

The output records measured size, reason, exact HEAD and recovery command for
the final summary. If any check is unavailable or changes between proposal and
apply, the action refuses safely.

Git maintenance and other concurrent sessions may prune registrations while an
inventory is running. Therefore, never use a before/after registration count as
proof that this helper removed a checkout. Report only the exact paths whose
`reclaim --apply` result says `applied: true` and `removed: true`, plus exact
paths returned by an explicit `prune-missing --apply` action. Treat every other
count change as concurrent or implicit metadata maintenance until independently
proved.

### Dependency reuse

Do not symlink mutable dependency directories between worktrees. First find a
donor with byte-identical lockfiles:

```bash
python3 scripts/agent-checks/worktree-lifecycle.py dependency-donors \
  --repo <repository> --worktree <new-worktree>
```

Then use the exact donor in proposal mode before adding `--apply`:

```bash
python3 scripts/agent-checks/worktree-lifecycle.py seed-dependencies \
  --source <donor-worktree> --target <new-worktree>
```

The helper uses APFS copy-on-write cloning on this Mac (or reflink-capable copy
elsewhere), refuses a pre-existing target dependency directory, and refuses
any lockfile mismatch. Node projects still run their normal project dependency
version check and focused build/tests. Composer projects must run
`composer dump-autoload --no-interaction --no-scripts` in the target before
tests so absolute autoload paths are regenerated.

This is a fast seed, not proof the environment is ready. Project-native checks
remain mandatory.
