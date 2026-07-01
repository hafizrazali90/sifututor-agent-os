# Agent OS Runtime Reliability

Use this when the agent is actively working in a session and needs to stay
predictable.

Plain meaning:

```text
The Agent OS should not only have good rules.
The agent should know what mode it is in, what context it loaded, what proof it
has, and what it will do next.
```

This playbook is the runtime layer.
It turns the written Agent OS into a repeatable day-to-day operating loop.

## Core Rule

For meaningful work, the agent should keep four things visible:

```text
mode -> loaded context -> proof/state -> next action
```

In normal words:

```text
Say what kind of work we are doing.
Read the docs that fit that work.
Prove the current state honestly.
Recommend the next move.
```

This does not mean every reply needs a formal report.
It means the agent should not drift silently.

## Runtime Modes

Use these modes as practical behavior states.

| Mode | What it means | Agent should do | Stop point |
| --- | --- | --- | --- |
| Discuss | Hafiz is learning, comparing, or deciding. | Explain, brainstorm, recommend softly. | Stop before durable edits unless Hafiz says proceed. |
| Plan | The work needs shape before implementation. | Create the smallest useful planning artifact. | Stop when product/risk/scope decision is needed. |
| Diagnose | The cause is unknown or reported. | Inspect, reproduce, gather read-only evidence. | Stop before implementation for critical lanes or unclear scope. |
| Build | A scoped change is approved. | Edit in small coherent slices. | Stop before unapproved scope, critical risk, or outbound state. |
| Verify | Prove the implementation works. | Run focused checks from the right project/context. | Stop if proof is missing or failing. |
| QA | Prove the user/system journey and regression risk. | Run browser/mobile/API/smoke/manual-style checks where safe. | Stop if human-journey proof is required and missing. |
| Review | Challenge scope, evidence, state, and risk. | Review as if not the builder when the next state matters. | Stop if next state is unsafe. |
| Commit | Save local history. | Guard, stage exact files, commit approved package. | Stop before push unless push is approved. |
| Push or PR | Send work to GitHub. | Pre-push review, push/open PR/CI work inside approved boundary. | Stop before merge unless merge is approved. |
| Release | Move code toward staging/production. | Preflight, deploy if approved, smoke, monitor. | Stop before rollback/new fixes/destructive action unless approved. |
| Save or Handoff | Preserve continuation. | Update Session Map, Koda, save-session/handoff docs. | Stop when future reader can resume. |

The mode is not a fancy label for Hafiz to memorize.
It is the agent's internal operating gear.

## Mode Selection

Task Router chooses the starting mode.
The mode can change as work progresses:

```text
Discuss -> Plan -> Build -> Verify -> QA -> Review -> Commit -> Push/PR
```

or for bugs:

```text
Diagnose -> Build -> Verify -> QA -> Review -> Commit
```

or for production:

```text
Diagnose -> Review -> approved Release -> Smoke -> Monitor -> Save
```

Short commands follow the current mode:

| Hafiz says | Agent should interpret as |
| --- | --- |
| `continue`, `go next`, `proceed` | Continue the last clear recommended mode/action. |
| `proceed until done` | Translate the practical done state and continue until the approved boundary. |
| `commit` | Enter Commit mode only for the approved file package. |
| `push` | Enter Review first, then Push mode if the boundary is approved. |
| `save session` | Enter Save/Handoff mode. |

## Loaded Context Readback

For meaningful work, the agent should know what it loaded and why.

Use a natural sentence, not a mechanical file dump:

```text
I treated this as Agent OS workflow improvement, so I used the improvement loop,
doc routing, the owner index, evals, and the active Session Map.
```

Use fuller readback when:

- the task is complex;
- the previous mistake was missed context;
- the work is critical, outbound, or long-running;
- another agent will continue later.

Use lighter readback when:

- the task is a small docs edit;
- the loaded docs are obvious from the route;
- the user is trying to move quickly.

## Drift Signals

Runtime drift means the agent is no longer following the intended operating
mode.

Watch for these signals:

| Drift signal | Practical meaning | Recovery |
| --- | --- | --- |
| No next action | Hafiz has to ask what happens next. | Add recommended next action before ending. |
| Wrong mode | Agent is building when Hafiz wanted discussion, or discussing when work is approved. | State the mode and switch back. |
| Missed doc | Agent skipped a route-required or triggered doc. | Pause, read it, compare work, fix if needed. |
| State confusion | Local, pushed, PR, merged, deployed, and live are mixed. | Name highest proven state from evidence. |
| Approval drift | Agent asks for every tiny step or crosses a real gate. | Use one approved boundary, but stop at hard gates. |
| Context overload | Agent reads too many unrelated docs and loses the point. | Return to doc routing and owner index. |
| Scope expansion | Agent fixes adjacent issues silently. | Classify in-scope, blocking, pre-existing, or follow-up. |
| Stale Session Map | Current focus or continuation prompt points to old work. | Update the map or say it is stale before relying on it. |

Plain version:

```text
If the agent feels lost, check the mode, loaded context, proof/state, and next
action.
```

## Runtime Close-Out

For meaningful work, include these meanings before ending:

```text
Mode:
<current mode in plain language, only if useful>

Loaded context:
<what mattered, not every file>

State:
<changed locally, committed locally, pushed, PR open, merged, deployed, live
checked, parked, or still discussion>

Checked:
<tests/checks/evidence or why not needed>

Recommended next:
<one action>
```

Do not force this shape into every casual answer.
Use it when the work is multi-step, stateful, risky, or easy to lose.

## Session Map Reliability

Session Map is useful only if the current section is current.

When a Session Map has stale continuation text:

1. Do not trust stale current-focus lines as truth.
2. Use Git, current chat, pushed commits, Koda, and recent checks as current
   evidence.
3. Update only the current focus, progress rows, and continuation prompt unless
   a full map cleanup is needed.
4. Do not rewrite the whole historical map during unrelated work.

Plain version:

```text
The map is a dashboard.
If the dashboard points to an old road, update the pointer before driving.
```

## What Good Looks Like

Good runtime behavior:

```text
I am in Review mode because you asked to push. The committed Agent OS batch is
six commits ahead of GitHub. Health passed, the unrelated Ripple ledger file is
not staged, and the next action is to push `main`.
```

Bad runtime behavior:

```text
Done.
```

That is too thin because it hides mode, state, proof, and next action.

## Future Automation

Automate only after the manual pattern is stable.

Good future checks:

- response-shape checks for missing next action;
- fixture checks for wrong mode on `proceed`, `commit`, `push`, and
  `save session`;
- Session Map check for stale current-focus warnings;
- health summary showing current branch, ahead/behind, dirty files, and active
  mode.

Do not hard-block every mode mismatch.
Some mode choices require judgment.
