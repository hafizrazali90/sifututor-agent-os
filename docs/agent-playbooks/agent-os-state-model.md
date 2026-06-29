# Agent OS State Model

Use this document when deciding where task status, evidence, approvals, and
release state should live.

## Core Idea

The Agent OS has many places that can talk about work, but each place should
own a different kind of truth.

Plain version:

```text
GitHub tells developers what to build.
Planner tells us what staff reported.
Active task files tell agents what to do next.
Git proves what changed.
QA evidence proves whether it works.
Koda remembers the lesson.
Mission Ledger remembers the bigger goal and follow-up map.
Session Map keeps the current chat's main goal, side paths, and return path
visible.
Chat/save-session tells Hafiz the current status and next action.
```

No single tool should pretend to be all of these at once.

## State Ownership Rule

Every state source gets one job.

Plain meaning:

```text
Use the source that owns the question.
Do not use the nearest source, loudest source, or oldest source as proof.
```

Use this practical ownership split:

| Source | Primary job |
| --- | --- |
| Chat | What Hafiz just asked or decided right now. |
| Session Map | Where this current session is, what side paths exist, and what happens next. |
| Koda | Durable lessons, corrections, preferences, and repeated mistakes. |
| Mission Ledger | Bigger goals, parked decisions, and future work that is not execution-ready yet. |
| Planner | Staff-reported symptoms and operational context. |
| GitHub issue | Engineering work that is ready for a developer or agent to execute. |
| Active task file | The current agent/dev work pointer inside a project. |
| Git commit | Exact files saved locally. |
| PR | Reviewable change before merge. |
| Deploy record / production SHA | What code reached staging or production. |
| QA evidence | What actually works for users. |

The agent must not promote a weaker source into a stronger claim.

Examples:

| Weak claim | Correct reading |
| --- | --- |
| Planner says fixed | Staff reported status; verify Git/PR/deploy/QA before saying fixed. |
| Koda says this was accepted | Durable memory; check current files/state before acting. |
| Chat says done | Historical conversation; check Git, PR, deploy, and evidence. |
| Commit exists | Files changed locally; not proof of push, merge, deploy, or acceptance. |
| PR merged | Source is merged; not proof that production contains it. |
| Deploy happened | Version reached an environment; not proof the user journey works. |

Before acting, answer:

```text
What question am I answering?
Which source owns that answer?
What is the highest proven state?
What should be updated, if anything?
```

If the answer belongs in another source, update or link that source instead of
duplicating the same truth everywhere.

## Ownership Questions

Use this table when Hafiz or an agent asks "where should we check this?"

| Question | Source of truth |
| --- | --- |
| What are we trying to do in this session? | Session Map |
| What did Hafiz permanently correct or prefer? | Koda |
| What bigger goal, paused decision, or future follow-up exists? | Mission Ledger |
| What exact code or docs changed? | Git commit |
| What is ready for engineering execution? | GitHub issue |
| What is ready for review or merge? | PR |
| What is actually deployed? | Deploy record or production SHA |
| What actually works for users? | QA evidence, smoke result, screenshots, tests, or monitoring |
| What should happen next right now? | Chat close-out plus Session Map |

Plain meaning:

```text
Each tool gets one job. Do not use Koda as proof that code shipped, chat as
proof that production works, or a commit as proof that Hafiz accepted the
result.
```

Technical detail in normal language:

```text
This is context authority. The agent should use the source that owns the
question. If the question is current state, fresh evidence wins. If the question
is workflow rules, approved docs win. If the question is remembered preference,
Koda is useful, but still not proof of live code or production behavior.
```

## Routing New Information

Use this when deciding where a new idea, correction, issue, or follow-up should
be recorded.

Plain meaning:

```text
Do not store everything everywhere. Put each piece of information in the place
where it will help future work the most.
```

| New information | Put it in |
| --- | --- |
| It affects the current session story, side path, decision, return path, or next step | Session Map |
| It is a durable correction, preference, repeated mistake, tool lesson, or workflow rule | Koda, and usually the relevant doc/playbook too |
| It is a bigger goal, paused decision, adjacent idea, future follow-up, research topic, or not-yet-ready task | Mission Ledger |
| It is exact engineering work ready to build, fix, test, or review | GitHub issue |
| It is exact code/docs that changed | Git commit |
| It is multiple fixes in one chat with separate PR/merge/deploy/live states | Session Release Ledger |
| It is a staff-reported symptom | Planner/support context first, then diagnosis before GitHub |
| It is only a short temporary clarification for this moment | Chat only |

Decision tree:

```text
Is it needed only for this chat?
-> Chat or Session Map.

Should future agents behave differently because of it?
-> Koda plus docs/playbook if it is a system rule.

Is it a bigger goal or follow-up but not ready to execute?
-> Mission Ledger.

Is it ready for a developer/agent to implement?
-> GitHub issue.

Does it describe exact changed files?
-> Git commit.

Does it describe whether work is pushed, PR-open, merged, deployed, or live
checked?
-> Git/PR/deploy/QA evidence, plus Session Release Ledger when multiple fixes
exist in one session.
```

When in doubt, prefer the lightest durable home:

```text
Session Map for current-session continuity.
Mission Ledger for future work.
Koda only for behavior-changing lessons.
GitHub only for execution-ready work.
```

If two sources disagree, use [context-authority.md](context-authority.md).
Plain meaning: route the information to the right home, but do not trust stale
or conflicting context without checking the source that owns the current truth.

## Work Intake And Task State Rules

Use this when a request first becomes possible work.

Plain version:

```text
Do not create GitHub issues too early.
Do not start real coding work with no trace.
Do a quick diagnosis, then put the work in the lightest useful home.
```

Separate intake into three moments:

| Moment | Practical Meaning | What To Record |
| --- | --- | --- |
| Signal | Something was reported, requested, noticed, or remembered. | Keep the source clear: Hafiz chat, Planner/support, GitHub, Koda, Mission Ledger, production signal, or Session Map. |
| Quick diagnosis | The agent checks enough current evidence to avoid routing noise. | Short finding in chat or Session Map: symptom, likely project/module, affected role, evidence checked, and recommended home. |
| Execution state | The work is ready for building, verifying, reviewing, or saving. | GitHub issue for code work, Mission Ledger for bigger/future work, active task file where the project uses one, Session Release Ledger for multi-fix sessions, and git commit for exact changed files. |

Quick diagnosis is not a hidden implementation phase. It should stay read-only
and narrow:

- identify the reported symptom or requested outcome
- identify affected user, role, project, module, or workflow when possible
- check current repo/docs/test/runtime/production-safe evidence where relevant
- decide whether the work is discussion, design, diagnosis, GitHub issue,
  Mission Ledger follow-up, Koda lesson, chat-only clarification, or reject/close
- stop before code edits, data mutation, commit, deploy, destructive action, or
  critical-lane implementation

Use this routing table:

| Intake | First Move | Create GitHub Issue When | Do Not Create Yet When |
| --- | --- | --- | --- |
| Hafiz direct coding request | Route and quick-diagnose enough to title the work. | The work is real coding and has a clear scope, likely project/module, and acceptance shape. | Hafiz is still brainstorming, scope is too vague, or the request is docs/discussion only. |
| Staff or Planner report | Treat as symptom and gather current evidence. | The symptom looks like likely engineering work after quick diagnosis. | It is only a complaint, duplicate, missing role/page/data, or may be support/training/process instead of code. |
| Agent-discovered issue | Report it and compare with current scope. | It is inside approved scope or Hafiz approves tracking it as engineering work. | It is adjacent cleanup, broader refactor, or future improvement. Use Mission Ledger instead. |
| Bigger idea or future improvement | Capture in Mission Ledger. | It becomes execution-ready with scope and acceptance. | It is still an idea, research topic, parked decision, or product direction. |
| Durable preference or repeated mistake | Save to Koda and usually docs. | Only if it also creates concrete engineering work. | It is only a workflow lesson or behavior rule. |
| Long current session with side paths | Update Session Map. | Only for execution-ready code work inside the session. | It is only current-session continuity. |
| Multiple fixes in one chat | Update Session Release Ledger. | Each fix that needs engineering execution should have or link its issue. | The ledger itself is state tracking, not a replacement for issues. |

## Intake Scenario Matrix

Use these examples when the abstract rule is not enough. The goal is to help
the agent behave predictably without making Hafiz remember the routing table.

| Scenario | What It Means | First Agent Move | Home If Real Work | Must Not Do |
| --- | --- | --- | --- | --- |
| Hafiz says `fix this` and points at a clear bug | Current direction from Hafiz, but still not proof of root cause. | Read the relevant current files, task state, and safe evidence enough to name the likely module and done state. | GitHub issue or active task for code work; Session Map if the session is already multi-step. | Start broad coding with no trace, or ask Hafiz to diagnose what the agent can inspect. |
| Hafiz says `let's discuss` or asks `is this good?` | Thinking/design mode, not implementation approval. | Explain options, tradeoffs, recommendation, and what would be documented or changed if approved. | Living doc or Mission Ledger only if Hafiz wants it saved. | Create issues, edit code, or run heavy workflow ceremony. |
| Staff or Planner says something is broken | Real-world symptom from operations, not verified engineering truth. | Check Planner/context when relevant, then do narrow read-only diagnosis against current repo, route, UI/API, logs, or safe data. | GitHub issue when likely code work is confirmed; chat-only/support/process when not code. | Treat the report as root cause, close an issue from Planner alone, or start coding before reproduction/inspection. |
| GitHub issue exists but is vague | Possible execution ticket, but the scope may be weak. | Read the issue, linked context, current code/docs, and ask or diagnose only enough to make it build-ready. | Keep or refine the GitHub issue; add implementation readiness if another builder will take it. | Build from assumptions, expand beyond the issue, or duplicate a new issue. |
| Koda says a workaround or rule exists | Durable memory/history, not current-state proof. | Search/read current docs and files that own the behavior; compare memory against current reality. | Update docs or Koda if the memory is stale; proceed only after current evidence agrees. | Treat Koda as permission, proof that a fix is live, or stronger than current code/docs. |
| Production signal or monitoring alert appears | Live evidence that something may be affecting users. | Use incident or diagnose workflow; gather read-only evidence, severity, affected surface, and safe mitigation options. | Incident workflow, GitHub issue for confirmed fix, Mission Ledger for prevention follow-up. | Mutate production, deploy, rollback, or edit critical lanes without the required approval. |
| Another session or agent hands off work | Continuation signal that may be stale or incomplete. | Read the Session Map/reference pack, git state, linked issue/PR, and latest evidence before continuing. | Continue the existing home if it still matches; otherwise update Session Map and explain the mismatch. | Restart from scratch, trust old chat over current repo state, or create duplicate state records. |
| Agent notices an adjacent issue during a task | New finding, not automatically part of the approved scope. | State the finding and compare it with the current task boundary. | Current task only if inside scope; otherwise Mission Ledger or GitHub issue if Hafiz approves execution-ready work. | Silently fix it, broaden the PR, or bury it in the final answer. |

Close-out example:

```text
I treated the Planner note as a staff-reported symptom, not root cause. I
checked the current route/component and found it likely is code work, so the
right home is a GitHub issue before implementation. I did not edit code yet.
Recommended next: create/link the issue, then diagnose the fix path.
```

Good default flow:

```text
report / idea / request
-> quick diagnosis
-> choose the lightest useful home
-> work through the right workflow
-> evidence
-> commit/push/PR/deploy state when approved
-> Koda only for durable lessons
```

Examples:

```text
Staff says "invoice button does nothing".
The agent checks the page/module, role, related route/component, existing issue,
and safe evidence first. If it looks like a real bug, create/link a GitHub
issue before coding. If it looks like training/data/process, report that and
do not create engineering noise.
```

```text
Hafiz says "we should improve the parent invoice journey later".
That is Mission Ledger first, not GitHub. Promote to GitHub only when the work
has a titleable scope and acceptance shape.
```

```text
During a bugfix, the agent notices unrelated cleanup.
Do not silently add it. Mention it, then either skip it, park it in Mission
Ledger, or create a GitHub issue if Hafiz agrees it is execution-ready.
```

## Source Of Truth Map

| Source | Owns | Does Not Own |
| --- | --- | --- |
| Chat | current conversation, immediate instructions, clarifications | durable system rules, release truth, proof that code shipped |
| `AGENTS.md` | shared operating contract and hard rules | detailed project history |
| Agent OS docs | workflow architecture, playbooks, durable operating models | current task status unless the doc is specifically a status report |
| Project `AGENTS.md` / `CLAUDE.md` | project-specific rules and deep project context | live proof that the latest code works |
| Koda | durable corrections, lessons, preferences, and non-obvious patterns | raw transcripts, temporary progress, secrets, current branch state |
| Mission Ledger | bigger goals, child tasks, adjacent ideas, paused decisions, and follow-ups not ready for GitHub | exact implementation ticket state, production truth, raw lesson memory |
| Microsoft Teams Planner | staff-reported intake and operational symptom context | engineering source of truth, final code status, production truth |
| GitHub issue | developer execution ticket for code work | whole roadmap, production smoke result unless linked |
| `.claude/tasks/active.json` | active agent execution pointer for state-file projects | business priority, production truth, cross-session release summary |
| Session Map | live session story: main goal, current focus, side paths, open decisions, return path, and recommended next step | durable memory, final release truth, exact engineering ticket ownership |
| Session Release Ledger | per-session map of fixes, commits, PRs, main state, live state | full project roadmap |
| Git branch/commit | exact code/docs change and local history | whether the change is deployed or accepted by Hafiz |
| PR | reviewable merge candidate and discussion of a code change | proof that the change is live |
| `origin/main` | merged source state | proof that production contains the change |
| deploy record / production SHA | deployed code state | proof the real workflow works |
| QA report / screenshots / tests | evidence that behavior works | task priority or ownership |

## Practical Rule

Before saying work is "done", say the highest proven state:

```text
drafted
changed locally
committed locally
pushed to GitHub
PR open
merged
deployed
live checked
accepted / closed
```

Do not use "done" alone when a user could reasonably think it means shipped or
live.

Plain meaning:

```text
Say how far the work has truly travelled. Do not describe it as more finished
than the evidence proves.
```

Example:

```text
Committed locally, not pushed yet.
```

This means Git saved it on Hafiz's machine, but GitHub and other agents do not
have it yet.

```text
Deployed, live check not done yet.
```

This means the server has the version, but the real workflow still needs to be
tested on that environment.

The executable state wording subset lives at:

```bash
scripts/agent-checks/agent-os-state-fixture-runner.py
```

It checks sample state summaries so local, committed, pushed, deployed, and
live-smoke-passed states do not get mixed together. Plain meaning: it catches
answers that say "done" or "live" when the evidence only proves a lower state.

## Normal Work State Flow

For one normal coding task:

```text
Planner or Hafiz report
-> route task
-> GitHub issue when code work is needed
-> Mission Ledger when there is a bigger/future follow-up
-> Session Map when the current conversation has side paths or multiple goals
-> active task file when the project uses one
-> branch/implementation
-> verify + QA evidence
-> review
-> commit
-> push / PR / merge when approved
-> deploy when approved
-> live smoke / monitoring evidence
-> Koda lesson if durable
-> save-session close-out
```

Not every task uses every step. Documentation-only Agent OS work usually stays
in docs, git, Koda, and the final close-out unless Hafiz asks for GitHub.

## What Each State Means

| State Phrase | Meaning |
| --- | --- |
| `not started` | Captured, but no work has begun. |
| `in discussion` | Hafiz and agent are shaping the work; no implementation yet. |
| `drafted` | Idea, doc, PRD, plan, or code direction exists, but it has not been finalized as a saved implementation state yet. |
| `in progress` | Agent/dev is actively changing or diagnosing. |
| `blocked` | Cannot move until a named blocker is resolved. |
| `waiting for Hafiz` | Agent has gathered what it can; Hafiz needs to decide, approve, or judge. |
| `waiting for QA` | Built evidence exists, but manual/device/business QA still needs to happen. |
| `changed locally` | Files changed locally on Hafiz's machine; not necessarily committed. |
| `done locally` | Older wording for `changed locally`; prefer `changed locally` unless quoting an old note. |
| `committed locally` | Commit exists only in local git. |
| `pushed to GitHub` | Branch or commit exists on remote, but may not be merged. |
| `pushed` | Short wording for `pushed to GitHub`. |
| `PR open` | Pull request exists and awaits review/merge. |
| `merged` | Change is in `origin/main` or the agreed target branch. |
| `deployed` | Target environment contains the commit. |
| `live checked` | The changed workflow was checked on the deployed target. |
| `live smoke passed` | Technical wording for `live checked`. |
| `accepted / closed` | Hafiz or the business accepted the outcome, evidence exists, and no required next action remains. |
| `closed` | Short wording for `accepted / closed`; use only when nothing required remains. |

## State Update Rules

Use the smallest update that preserves truth.

| Event | Update |
| --- | --- |
| Staff reports issue | Read Planner as symptom context; do not treat it as verified root cause. |
| Hafiz asks for meaningful work | Route the task and check GitHub, Mission Ledger, and active task state where relevant. |
| Code work is needed | Create or link a GitHub issue unless unavailable or too ambiguous. |
| Project has active task files | Read `.claude/tasks/active.json` and resume unless Hafiz starts new work. |
| Current chat becomes hard to track | Start or update the Session Map. |
| Work becomes multi-fix | Start or update the Session Release Ledger. |
| Agent finishes a step | Close out with factual progress and next action; update active task or Mission Ledger when relevant. |
| Commit created | Record commit SHA in task/session ledger when relevant. |
| Push/PR/merge/deploy requested | Inventory session fixes before acting. |
| Production deploy done | Record deploy commit, smoke result, monitoring result, and remaining risk. |
| Durable lesson found | Store concise Koda memory with project/domain/lifecycle/risk tags. |

## Conflict Rules

When sources disagree, use this order:

1. Forbidden boundaries: `.env*`, secrets, `live/`, no bypassing hooks.
2. Hafiz's current explicit decision.
3. Fresh verified evidence: git status, tests, browser/API checks, deploy SHA.
4. Approved docs: `AGENTS.md`, project `AGENTS.md`, playbooks, `CLAUDE.md`.
5. Current task systems: active task file, GitHub, Planner, Mission Ledger.
6. Koda and previous chat history.
7. Agent assumptions.

If a lower source conflicts with a higher source, say so plainly before acting.

Example:

```text
Planner says the issue is fixed, but the branch is not merged and there is no
live smoke evidence. I will treat it as staff-reported status, not shipped
truth.
```

## GitHub, Planner, Mission Ledger

Use them together, not interchangeably.

| Tool | Best Use |
| --- | --- |
| Mission Ledger | "What bigger goal does this follow-up belong to, and what should we not forget?" |
| Session Map | "Where are we in this session, what side paths exist, and where do we return next?" |
| GitHub issue | "What exact engineering task should a developer/agent implement?" |
| Planner | "What did staff report or experience operationally?" |

Mission Ledger is the map of remembered work beyond the current session.
Session Map is the live map of the current session. Planner is intake. GitHub
is engineering execution. Current release truth belongs in git, PRs, deploy
records, QA evidence, or the Session Release Ledger.

## Work Intake Source Roles

Use this model when deciding whether an input should become discussion,
diagnosis, GitHub issue, Mission Ledger item, Koda memory, or implementation.

```text
Every input is a signal first, not truth yet.
The agent classifies it, checks enough current evidence, then routes it.
```

| Source | Role |
| --- | --- |
| Hafiz chat | Current direction. |
| Staff report | Real-world symptom. |
| Planner | Staff intake/context. |
| GitHub | Engineering execution. |
| Koda | Durable memory/lesson. |
| Mission Ledger | Bigger/future/parked work. |
| Session Map | Current conversation map. |
| Production signal | Live system evidence. |
| Agent-discovered issue | Finding that needs routing. |

Current repo, test, runtime, and production-safe evidence decide what is true
now. Hafiz still owns product direction, priority, business rules, and risk
acceptance.

## Agent Close-Out Shape

Every meaningful close-out should answer:

```text
Status:
<current state phrase>

Meaning:
<what changed in plain language>

Evidence:
<tests/checks/screenshots/links/commit/deploy proof>

Still not true yet:
<not committed / not pushed / not merged / not deployed / not smoke passed / none>

Recommended next:
<single next action>
```

This prevents Hafiz from needing to ask "so what is next?" after every step.
