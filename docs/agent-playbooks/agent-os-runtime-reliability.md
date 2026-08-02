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

When work has more than one natural step, also name:

```text
finish state -> pause point
```

Plain meaning:

```text
Mode says what kind of work the agent is doing.
Finish state says how far this task is meant to go.
Pause point says where Hafiz needs to decide again.
```

Use the finish states from
[agent-os-workflow-lanes.md](agent-os-workflow-lanes.md): answer only,
drafted, changed locally, local proof, committed, PR ready, merged, deployed,
live checked, monitored, or accepted/closed.

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
| Source conflict | Koda, chat, Session Map, GitHub, Git, deploy, QA, docs, or Planner disagree. | Use `context-authority.md`: name the question, choose the owner source, check current evidence, then continue or stop. |
| Closure drift | Agent says accepted, closed, or done when the work is only pushed, parked, or waiting for Hafiz/business acceptance. | Use `agent-os-workflow-lanes.md` and `agent-os-state-model.md` to name the real closure state. |
| Stale Session Map | Current focus or continuation prompt points to old work. | Update the map or say it is stale before relying on it. |
| Map not updated after state change | The work moved from changed locally to committed/pushed/deployed, but the map still says the old state. | Use the Session Map live update loop and correct only the current pointer. |

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

Target finish:
<answer only, drafted, local proof, committed, PR ready, merged, deployed,
live checked, monitored, or accepted/closed when useful>

Checked:
<tests/checks/evidence or why not needed>

Recommended next:
<one action>
```

Do not force this shape into every casual answer.
Use it when the work is multi-step, stateful, risky, or easy to lose.

## Delegated Worker Runtime

For Codex-supervised Claude Max work, keep two liveness signals separate:

```text
watchdog heartbeat -> the local supervisor is alive
worker event time -> Claude last emitted observable activity
```

This distinction prevents a quiet Claude worker from disappearing in silence
without spending model tokens on repeated status prompts. Use
`scripts/agent-checks/agent-os-claude-delegation.py status` and the state table
in `handoff.md`.

Do not translate `stalled` into automatic recovery. Report the state, preserve
the evidence, and let the supervising Codex or human decide whether setup,
retry, or a fresh job is safe. A `finished` worker is ready for independent
review, not automatically accepted or ready for release.

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

## Daily Operating Examples

Use these examples as the practical daily pattern.
They are not scripts.
They show what the agent should make visible while still sounding natural.

Plain meaning:

```text
Hafiz should feel where the work is heading without memorizing the workflow.
The agent should know what to load, what to prove, where to stop, and what to
recommend next.
```

| Situation | Runtime mode | Loaded context | Proof or state to name | Stop point | Good response shape |
| --- | --- | --- | --- | --- | --- |
| Hafiz says `ok proceed` after a clear Agent OS recommendation | Build or Plan, depending on the last recommendation | Active Session Map, Task Router, owning Agent OS playbook, relevant eval/owner docs | Current git state and what is already accepted or pushed | Commit or push only if the approved packet included it | "I will continue the last recommended Agent OS step. I will update the owner doc, check the connected eval/index files, run Agent OS checks, and stop before any unapproved outbound step." |
| Hafiz says `let's discuss` or asks why something matters | Discuss | Current decision, relevant roadmap/Koda only if prior context matters | No file change unless Hafiz asks to document | Stop before durable edits | "We are still deciding. The choice is between A and B; I recommend A because..., but I will not change docs until you say proceed." |
| Hafiz says `proceed until done` for safe Agent OS docs | Build -> Verify -> Review -> Commit, and Push only if included | Improvement loop, owner playbook, doc routing, evals, Session Map | Changed files, checks, highest proven Git state | Stop at the approved boundary or a failed check | "Done for this packet means the docs are updated, checks pass, the Session Map is current, and the package is committed. Push needs to be included in the boundary." |
| Hafiz says `proceed until done` for a product bug | Diagnose -> Build -> Verify -> QA -> Review | Project docs, active task/GitHub issue, diagnose/verify/QA/review playbooks, TESTING/UI docs when triggered | Reproduction, fix evidence, journey/E2E decision, highest Git state | Recommend local proof, commit, PR ready, or production path based on risk | "For this bug, I recommend stopping at PR ready first: reproduce, fix, prove the user journey, commit, push, open PR, and monitor CI. Production stays separate unless you approve that boundary." |
| Hafiz says `proceed until production` | Review -> Release -> Smoke -> Monitor | Release playbook, approved source commit/PR, deploy path, smoke and monitoring tools | Deploy source, environment, smoke result, monitoring result | Stop before rollback, new fixes, destructive actions, or final business risk acceptance unless named | "For production, the finish state is live checked first, then monitored if included. I will name the commit, deploy target, smoke checks, and monitoring window before calling it live." |
| Hafiz says `commit` after a checked package | Commit | Commit playbook, current git diff/status, pre-commit guard | Exact staged file list and guard output | Stop before push unless push was approved | "I will commit only these files. The unrelated dirty file stays out. After commit, the next action is either push or continue the next Agent OS topic." |
| Hafiz says `push` after local commits | Review -> Push | Review/no-mistakes-lite, git ahead/dirty state, latest checks | Ahead commits, uncommitted files, last health/guard result | Stop before PR/merge/deploy unless approved | "I am doing the outbound review first: one commit is ahead, checks passed, and no unrelated files are staged. If clean, I will push main." |
| Hafiz asks `what next?` | Task Router / Discuss | Active Session Map, current git state, recent pushed commits, relevant Koda | Current focus, waiting decisions, dirty/ahead state | Recommend one next action | "The Runtime Reliability packet is pushed. The next useful step is to add daily examples so the rule is easier to apply in real work." |
| Hafiz reports an agent mistake | Diagnose or Workflow Improvement | Improvement loop, communication/routing/approval owner docs, evals, Koda, Session Map | What failed, likely owner, whether it is repeated or one-off | Stop before durable edits if the behavior is not agreed | "The mistake is not just wording; it is a routing/close-out gap. I recommend updating the owner playbook and adding an eval, then checking health." |
| Hafiz asks to fix a product bug | Diagnose | Project AGENTS, active task, diagnose playbook, Planner when staff-reported, project docs as triggered | Reproduction or read-only evidence; do not treat symptom as cause | Stop before critical-lane implementation or unclear scope | "I will first prove what is actually broken. If it is a normal bug, I will propose the fix path; if it touches payment/auth/mobile API, I stop after diagnosis for approval." |
| Hafiz asks to verify or QA | Verify or QA | Verify/QA playbook, evidence model, project rules, TESTING/UI docs when triggered | Exact command, browser/mobile/API evidence, missing evidence if any | Stop if proof is missing or unsafe | "Code tests prove the engine; for this staff workflow I also need browser evidence or a named reason why that is not feasible." |
| Hafiz says `save session` or the chat is getting long | Save or Handoff | Session Map, save-session/handoff docs, Git state, Koda memory rules | Main goal, current focus, highest proven state, dirty files, next action | Stop when future agent can resume | "I will save the story, not just the last command: goal, subgoals, decisions, pushed/local state, evidence, and the first next action." |
| A long packet changes state from local to committed or pushed | Build -> Commit -> Push/PR | Session Map live update loop, Git state, review/commit playbooks | Highest proven Git state, remaining dirty files, next action | Stop at the approved boundary | "The map still says changed locally, but Git shows the packet is pushed. I will update only the current pointer and progress row before continuing." |
| Sources disagree about state | Task Router / Review | Context authority, state model, owner source for the question | Highest proven state and the source that proves it | Stop if the conflict changes scope, risk, product meaning, approval, or critical-lane behavior | "Koda says this was accepted, but current docs do not contain the rule. I will treat Koda as history, use the docs as the adoption source, and update the owner doc before claiming the rule is adopted." |
| Hafiz asks whether an Agent OS topic is done | Task Router / Review | Workflow lanes, state model, roadmap, Git state, Session Map | Whether it is discussed, changed locally, pushed, adopted for use, parked, or accepted/closed | Stop before pretending Hafiz accepted a remaining review/risk point | "This packet is pushed and adopted for future agents because the owner docs and checks are in GitHub. It is not fully closed if you still want to review the concept; the next action is accept it, park it, or revise it." |

## What To Avoid

Avoid these runtime mistakes:

| Mistake | Why it hurts | Better behavior |
| --- | --- | --- |
| Saying only `done` | Hafiz cannot tell whether it is local, committed, pushed, live, or only discussed. | Name the highest proven state and next action. |
| Asking for every tiny step after a safe packet was approved | It makes Hafiz manage the workflow instead of directing the outcome. | Continue inside the approved boundary and stop at real gates. |
| Treating `proceed` as permission to invent new scope | It breaks trust and makes the OS unpredictable. | Return to the last clear recommendation. |
| Reading every Agent OS doc for every Agent OS task | It wastes context and can make the agent less focused. | Use doc routing and the owner index. |
| Trusting a stale Session Map current focus | The agent may continue old work after newer commits changed the real state. | Check Git/chat/Koda evidence and update the pointer. |
| Calling a user workflow verified from code tests only | Code proof may not prove the real staff/parent/tutor journey. | Add journey proof or name the honest blocker. |

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
