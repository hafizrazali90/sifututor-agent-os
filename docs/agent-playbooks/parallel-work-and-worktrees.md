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

## Launch The Session Inside The Worktree

Creating the worktree is only half the move. For any session that will run
commands in it, start the session inside that worktree:

```bash
cd <worktree> && claude
```

Why this matters:

- Claude binds `CLAUDE_PROJECT_DIR` and the loaded hook configuration at launch.
- A session launched in the umbrella keeps the umbrella project directory even
  after the conversation moves into a sub-project worktree, so project hooks
  configured as `cd "$CLAUDE_PROJECT_DIR" && python3 .claude/hooks/<hook>.py`
  look in the umbrella for a sub-project-only script.
- A missing `PreToolUse` script exits 2, which Claude reads as a hard block, so
  every Bash call in the session is cancelled.
- Hook configuration is effectively fixed for the running session. Editing
  settings after the session has started does not repair that session; only a
  new session picks the change up.

The umbrella now ships project-aware dispatcher wrappers for the Python, shell,
and PowerShell hook names used by active projects, so an umbrella-launched
session resolves the real hook from its payload working directory. Treat that
as defense in depth, not as permission to skip this rule: a future project can
introduce a new hook name before the umbrella baseline learns it. See
[agent-os-hook-dispatcher.md](agent-os-hook-dispatcher.md).

Staying in the umbrella is still fine for discussion, reading, and light docs
work that does not depend on a sub-project's own gates.

### Local Hook Settings Add, They Do Not Replace

Reported during issue 96: a `.claude/settings.local.json` hook entry merges with
the tracked hook array rather than replacing it. The local entry adds another
hook; it does not disable or override the tracked command.

Practical consequence:

```text
A broken tracked hook cannot be worked around with a local override.
Fix the tracked hook, or launch the session where the tracked hook resolves.
```

Evidence status, stated plainly:

- The merge behavior above comes from the issue-96 session report. It is not
  independently re-tested here and it is not a documented vendor guarantee.
- No `.claude/settings.local.json` in this workspace configures hooks today;
  the local files carry `permissions` and MCP toggles only. So the repo cannot
  currently confirm or contradict the reported behavior.

Re-verify before relying on this. Do not design a workaround that assumes a
local file can disable a tracked hook.

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

A tracked `.claude/tasks/active.json` that is byte-for-byte identical to the
configured base branch is inherited repository state, not proof that this
specific worktree owns the named task. The lifecycle helper reports that
pointer but continues evaluating the worktree's lease, dirty state, ancestry,
locks, ignored files, and live process ownership. A worktree-specific or
malformed task pointer still blocks cleanup.

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

For normal task completion, use the single close-out command instead of
manually releasing the lease and then reclaiming the checkout:

```bash
python3 scripts/agent-checks/worktree-lifecycle.py close \
  --repo <repository> --worktree <exact-path> \
  --session <exact-session-id> --expected-head <full-sha> \
  --base-ref origin/main --apply
```

Run it without `--apply` for a read-only preview. The command verifies that the
session owns the lease, the HEAD is exactly the expected task commit, the work
is clean and merged, ignored files are reproducible, no worktree-specific task
is active, and no process is using the checkout. If all checks pass, it releases
the lease and reclaims the checkout without deleting its branch. If any check
fails or state changes during the final check, it keeps the checkout and parks
the lease with the exact reason. Report the removed path and measured size, or
the parking reason and next action, in the task summary.

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

Age never creates permission. `close` is the normal owner-session path;
`reclaim` remains the lower-level administrator action for an already released
worktree. Before applying reclamation, the helper requires
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

After measuring size, apply repeats the safety checks while holding the same
lock used for lease updates, through completion of Git removal. This prevents
cooperating sessions from acquiring ownership between that check and removal.
Malformed lease records, including valid JSON with an invalid schema, must be
preserved for investigation. This lock does not coordinate arbitrary tools
that ignore the lease system; no universal filesystem race protection is claimed.

Git maintenance and other concurrent sessions may prune registrations while an
inventory is running. Therefore, never use a before/after registration count as
proof that this helper removed a checkout. Report only the exact paths whose
`reclaim --apply` result says `applied: true` and `removed: true`, plus exact
paths returned by an explicit `prune-missing --apply` action. Treat every other
count change as concurrent or implicit metadata maintenance until independently
proved.

### Dependency reuse

For a new task, prefer the single creation command instead of manually chaining
`git worktree add`, lease registration, donor discovery, and dependency setup:

```bash
python3 scripts/agent-checks/worktree-lifecycle.py create \
  --repo <repository> --worktree <new-worktree> \
  --branch <type/description> --base-ref origin/main \
  --owner <agent-or-human> --session <exact-session-id> \
  --purpose <short-purpose> --issue <issue-url-or-number> \
  --cleanup-condition <plain-condition> --install-if-needed
```

The command refuses an existing path, existing branch, invalid branch, or
missing base commit. It creates the worktree, immediately registers its lease,
then reuses the first registered donor with identical lockfiles. If no donor
exists, `--install-if-needed` uses the detected package manager's frozen-lockfile
installation. Without that flag it reports the exact install command instead
of running it. A failed setup parks the lease for inspection; it never force
deletes a partial checkout. The result records whether dependencies were
seeded, installed, not applicable, or still required.

### Local development environment attachment

When an isolated worktree cannot start because its local development
environment file is intentionally untracked, do not ask Hafiz to build a raw
symlink and do not inspect or copy the file. Preview, then apply the governed
attachment:

```bash
python3 scripts/agent-checks/worktree-lifecycle.py attach-local-env \
  --source <existing-repository-env-file> \
  --worktree <leased-worktree> --session <exact-session-id>

python3 scripts/agent-checks/worktree-lifecycle.py attach-local-env \
  --source <existing-repository-env-file> \
  --worktree <leased-worktree> --session <exact-session-id> --apply
```

The source must be an existing regular `.env*` file inside another registered
worktree of the same repository. The target is the same repository-relative
path inside an active worktree leased to the current session. The helper
refuses external sources, inactive or foreign leases, source symlinks,
pre-existing files, and links to a different source. Its output contains only
path/status metadata; it never opens, copies, or prints configuration values.
Applied attachments are recorded in the machine-local lease so lifecycle
cleanup can remove the worktree later, but only while the ignored entry remains
the exact recorded symlink; replacements or changed links still block cleanup.

This is a local-development convenience, not authority to inspect secrets or
use production credentials. Agents must still keep these files out of chat,
logs, screenshots, Git, Koda, and delegation artifacts.

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

Treat this primarily as a disk- and download-saving seed, not a guaranteed
speed improvement. A warm package-manager cache can make a clean install as
fast as or faster than cloning a large dependency tree. Project-native checks
remain mandatory, and generated build caches such as `.next` should not be
copied as dependencies.
