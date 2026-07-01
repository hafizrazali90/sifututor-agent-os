# Autonomous Work Packets

Use this when Hafiz asks the agent to keep working for a longer stretch without
asking for every small step.

Plain meaning:

```text
Hafiz can say normal things like "autopilot this" or "proceed until done".
The agent must translate that into a safe work packet, then loop inside that
packet without inventing a new mission or hiding uncertainty.
```

This is inspired by Kun Chen's `gnhf` pattern, but Sifututor starts with a
controlled playbook. Do not install or clone a separate autonomous-loop tool
yet.

## What This Adds

Sifututor already has approval boundaries such as `proceed until commit`,
`proceed until PR ready`, and `proceed until production monitored`.

Those rules answer:

```text
How far may the agent go?
```

This playbook answers:

```text
How should the agent behave while it is working inside that boundary?
```

## How Hafiz Uses It

Hafiz should not need to memorize exact commands.

These phrases are enough:

| Hafiz says | Agent should do |
| --- | --- |
| `one step only` | Do the next action, then stop. |
| `one by one` | Ask before each major gate. |
| `proceed until commit` | Work, check, review, commit locally, then stop. |
| `proceed until PR ready` | Commit, push, open PR, monitor CI, fix in-scope CI, then stop before merge. |
| `autopilot this docs batch` | Improve the agreed docs until coherent and checked, then stop for review or commit approval. |
| `keep going until fixed` | Define what fixed means, then work until that finish point or a stop rule. |
| `proceed until done` | Translate done into a practical finish point before acting. |

The agent must reply with the practical translation before a long-running packet:

```text
I will continue until:
<finish point>

I will work in loops of:
<small repeatable step>

I will stop if:
<stop rules>

I will report progress:
<cadence>

I will not do:
<out of scope / approval gates>
```

## Packet Types

Use the smallest packet that fits the work.

| Packet | Use for | Default stop point |
| --- | --- | --- |
| One-step packet | Hafiz wants tight control. | After one action. |
| Local proof packet | Fix/check work until local proof exists. | Evidence gathered, no commit unless approved. |
| Commit packet | Build/check/review/commit local work. | Local commit, not pushed. |
| PR-ready packet | Mechanical GitHub work after approval. | PR open/CI checked, not merged unless included. |
| Release packet | Approved staging/production release work. | The approved release state only. |
| Docs/research packet | Repeated documentation or research cleanup. | Coherent checked batch, then review or commit approval. |

## Loop Rules

Inside an autonomous packet, work in small loops:

```text
choose next slice -> change -> check -> record state -> decide continue/stop
```

Default loop size:

- one focused docs section
- one failing test or one implementation slice
- one workflow example group
- one CI failure diagnosis/fix
- one release/smoke/monitoring step

Do not batch so much work that the agent cannot explain what changed.

## Loop Limits

Use these defaults unless Hafiz names a different boundary:

| Situation | Default limit |
| --- | --- |
| Docs/research cleanup | 3 loops, then report progress or commit-ready state. |
| Product implementation | 1 vertical slice at a time. |
| Test/CI failure fix | 2 attempts, then stop and explain. |
| Repeated unknown error | 2 failed attempts, then stop. |
| New adjacent issue found | Record follow-up instead of expanding unless clearly in scope. |
| Long-running command | Give a progress update after about 30 seconds when possible. |

Plain version:

```text
Autonomy should make progress, not wander forever.
```

## Stop Rules

Stop and report when:

- the finish point is reached
- Hafiz's product/business decision is needed
- scope changes
- a new task or feature appears
- a critical lane appears
- evidence is missing and no safe fallback exists
- the same loop fails twice
- tests fail for an unclear reason
- a push, PR, merge, deploy, destructive, production, or secret boundary appears
- branch/worktree state becomes confusing
- a rollback/retry decision is needed
- the work should become a follow-up issue, Mission Ledger item, or separate
  worktree

Stopping is not failure. It is the safe edge of the packet.

## Commit Behavior

The agent may commit only when the approved boundary includes commit and the
commit playbook rules are satisfied.

For long-running docs or workflow packets:

- one coherent batch can become one commit
- repeated commits need the packet to say that up front
- every commit still needs exact file-list approval unless the approved packet
  already included an exact commit bundle

For product code:

- prefer one coherent vertical-slice commit
- do not create many hidden commits while Hafiz thinks the agent is only
  diagnosing or drafting
- push/PR/merge/deploy remain separate approval boundaries unless explicitly
  included

## Rollback And Retry

When a loop makes things worse:

1. Stop changing more files.
2. Identify the last good state from git, tests, or diff.
3. Prefer a targeted fix over a broad revert.
4. Do not use destructive reset/checkout commands unless Hafiz explicitly asks.
5. If the bad loop cannot be safely repaired, report the practical blocker and
   recommend whether to revert, park, or start a cleaner worktree.

## Progress Reporting

Keep progress updates short.

Use this shape:

```text
Progress: <what loop just completed>.
Checked: <what passed or failed>.
Next: <what loop I am starting>.
Still inside boundary: <yes/no>.
```

Do not spam every tiny command. Do update when the agent changes phase, a check
fails, work takes longer than expected, or a decision/risk appears.

## Interrupt And Resume

If interrupted, compacted, or paused:

- update the Session Map when the work is multi-step
- name the loop number or current slice
- record changed files, checks, failures, and next loop
- record whether the packet is still active, parked, handed off, or ready for
  review
- use Koda only for durable lessons or corrections, not raw progress

## Relationship To Other Playbooks

| Playbook | Relationship |
| --- | --- |
| `agent-os-approval-gates.md` | Defines how far the packet may go. |
| `no-mistakes-lite.md` | Final honesty gate before ready/done/outbound claims. |
| `parallel-work-and-worktrees.md` | Isolation rules when autonomous work could collide with other work. |
| `session-map.md` | Tracks long-running packet state and return path. |
| `save-session.md` | Saves the packet if interrupted or ending. |
| `push-pr-ci-automation.md` | Owns PR-ready mechanics. |
| `release-deploy-live-monitoring.md` | Owns deploy/smoke/monitoring mechanics. |

## Common Failure Modes

Avoid these:

- treating `autopilot` as permission to do anything
- expanding a docs cleanup into product code
- continuing after two failed loops without reporting
- repeatedly finding adjacent issues and fixing them silently
- committing multiple times without the packet saying that is allowed
- saying "done" without the no-mistakes-lite check
- losing state after compaction because the Session Map was not updated

## Future Automation

Do not automate the loop runner yet.

First, use this playbook manually. If repeated patterns appear, automate only
the stable parts, such as:

- packet state template
- loop counter
- progress log
- changed-file inventory
- repeated failure stop
- Session Map packet section

Plain version:

```text
Use human-readable rules first.
Automate the parts that repeat and prove useful.
```
