# Responsibility Inbox Product Shape

Status: Product Shape direction approved by Hafiz on 2026-08-03; PRD and UX
design not started

## Product Goal

Give Hafiz one dependable place that answers:

```text
What needs me now, who is waiting for me, and what should I do next?
```

The Responsibility Inbox is a product layer inside the future native Agent OS
work environment. It should find responsibilities across projects and work
systems, explain why each one matters, and bring forward the few items where a
missed response would stop staff or delay important work.

It is not only a reminder list. From an inbox item, Hafiz should be able to open
the relevant project or work session, understand the evidence, make the needed
decision, and continue the actual task in the same environment.

## Problem

Hafiz works through many Claude, Codex, Hermes, project, GitHub, and staff
sessions. Useful commitments appear while another task is active:

- a developer needs approval before continuing;
- a session has paused at a decision boundary;
- a future idea should be remembered but is not ready for coding;
- an active issue has no next action;
- staff are waiting on a response in Planner;
- local work exists but has not been pushed, reviewed, or deployed;
- a promised follow-up becomes old without anyone surfacing it.

The information already exists, but it lives in different systems. Chat history
alone is not dependable enough to recover it, and asking Hafiz to remember
which session or tool owns each item defeats the purpose of the Agent OS.

## Primary Users

### Hafiz

The main user. He needs a short, trustworthy view of:

- what requires his decision;
- which staff member or agent is blocked;
- what is time-sensitive;
- what active work can continue next;
- what was intentionally deferred;
- what has changed since he last checked.

### Agent OS assistant

The assistant gathers current evidence, links related items, explains priority,
and recommends one next action. It must distinguish current verified state from
old chat or memory.

### Staff and development agents

They are indirect users. Their requests and blockers should reach Hafiz without
requiring them to move into a new task system. Their existing source remains
authoritative.

## Current Workflow

Today, the Agent OS already assigns different truths to different sources:

| Information | Current owner |
| --- | --- |
| Current session goal, blockers, and return path | Session Map |
| Bigger goals, deferred ideas, paused decisions, future follow-ups | Mission Ledger |
| Execution-ready engineering work and PR state | GitHub |
| Current routed project work | Project active-task file, where used |
| Staff-reported SIMS and mobile work | Microsoft Teams Planner |
| Durable lessons, preferences, and corrections | Koda |
| Exact local work state | Git |
| Deployment and user-facing truth | Deploy records, QA, smoke, and monitoring evidence |

The weakness is not the absence of storage. The weakness is the absence of a
trusted cross-source view that detects what needs Hafiz and returns it at the
right time.

## Recommended Product Principle

```text
One inbox, many owners.
```

The Responsibility Inbox should be a linked read model over the existing
sources of truth. It should not copy every task into another editable task
database.

For example:

- “defer this for later” is captured in the Mission Ledger and then appears in
  the inbox;
- a staff request remains in Planner and appears in the inbox when Hafiz is
  needed;
- an execution-ready coding task remains in GitHub;
- a paused session remains in its Session Map;
- Koda can help discover a possible forgotten commitment, but cannot make it
  authoritative without promotion to an owned source.

The inbox may own personal presentation state such as `last seen`, `snoozed
until`, and notification preference. It must not claim that the underlying work
is complete, approved, pushed, merged, or deployed unless the owning source
proves that state.

## Trusted-Source Contract

### First-version sources

| Source | What the inbox may surface | Freshness behavior | Allowed first-version action |
| --- | --- | --- | --- |
| Session Maps | waiting decisions, blockers, exact next actions, incomplete session work | Read active maps and verify mutable Git/GitHub claims fresh | Open the session or source evidence |
| Mission Ledger | active, paused, triaged, and captured future work | Read relevant project items; promote when execution-ready | Open item, request triage, or snooze the reminder |
| GitHub | issues, PR review needs, failed checks, and assigned next actions | Query current remote state | Open GitHub or begin an approved Agent OS workflow |
| Active task files | current routed work and blockers | Read current project state | Open/resume the task |
| Teams Planner | staff reports and staff waiting for Hafiz | Query current card state; treat reported symptoms as reported, not proven | Open the card or prepare a response; do not mutate Planner without approval |

### Discovery-only sources

| Source | Rule |
| --- | --- |
| Koda | Use for durable preferences, corrections, and historical leads; never use as current task-state proof. |
| Prior chat and saved session history | Use to find a candidate responsibility, then confirm or promote it into the correct owner. |
| Hermes Kanban | Use for agent execution and orchestration when appropriate; do not automatically make it the owner of GitHub, Planner, Mission Ledger, or Session Map state. |

### Inbox-owned overlay

The inbox may store only fields that belong to the personal attention
experience:

- stable link to the source item;
- `last_seen_at`;
- `snoozed_until`;
- notification preference;
- acknowledgement state;
- the last source revision or timestamp observed, for change detection.

Acknowledging or snoozing an item means “do not remind me until this time.” It
does not mean the source task is done.

## Responsibility Card

Every visible responsibility should be normalized into a small card:

| Field | Meaning |
| --- | --- |
| Title | The decision or action in plain language |
| Project | Which project or cross-project mission it belongs to |
| Category | `staff blocked`, `waiting on Hafiz`, `active next action`, `time-sensitive`, or `deferred` |
| Who is waiting | Staff member, agent, Hafiz, or nobody |
| Why now | The evidence-backed reason it is being shown today |
| Recommended action | One concrete next move |
| Source and confidence | Owning source plus `verified`, `trusted`, `reported`, or `historical` |
| Freshness | When the source was last checked |
| Due or age | Real due date when one exists; otherwise clearly labelled age, not an invented deadline |
| Related items | Approval, issue, session, or staff blocker linked to the same outcome |
| Attention state | New, seen, snoozed, or changed since seen |

## Priority Model

The first version should use transparent rules rather than an opaque AI score.

Rank items in this order:

1. A person is blocked waiting for Hafiz.
2. A critical or time-sensitive approval needs Hafiz.
3. An active task cannot continue without a decision or missing capability.
4. A real due date is approaching or overdue.
5. Active work has a clear next action and is becoming stale.
6. Deferred or future work is due for review.

Within the same level, prefer:

1. greater number of people or projects unblocked;
2. verified and freshly checked evidence;
3. older unresolved responsibility;
4. explicit business priority;
5. the item with the clearest safe next action.

AI may explain the ranking and group duplicates, but it should not silently
override these rules. Every card must answer “Why is this above the next item?”

## Notification Behavior

The system should help without becoming another noisy channel.

### Desktop

- Persistent Responsibility Inbox in the native work environment.
- Default views: `Needs me`, `Staff blocked`, `Active`, and `Deferred`.
- A daily “what changed” summary instead of repeating every unchanged item.
- Opening a card takes Hafiz to the actual source, evidence, or work session.

### Telegram

- Morning digest with the top responsibilities and one recommended first action.
- Immediate alert only when a person becomes blocked, an approved urgent rule
  matches, or a time-sensitive item crosses its reminder threshold.
- `[SILENT]` behavior when nothing materially changed.
- Short commands or conversation for `show why`, `open`, `snooze`, and `what
  should I do next?`.
- No secrets, raw tokens, private payloads, or unnecessary staff data in the
  notification.

### Reminder policy

- Do not alert again merely because the scheduled check ran.
- Alert on a new responsibility, a meaningful source change, a due threshold,
  or the end of a snooze period.
- Escalate only when the blast radius or waiting dependency increases.
- Explain when evidence is stale or a source could not be checked.

## Hermes Fit

Hermes already provides reusable foundation pieces:

- scheduled jobs and script-only checks;
- `[SILENT]` notification suppression;
- Telegram home-channel delivery;
- task notifications and blocked-task types;
- a native Kanban surface and agent dispatcher;
- project chat, files, terminal, diffs, and persistent sessions.

The recommended integration is removable and Agent-OS-owned:

1. A deterministic collector reads approved Agent OS sources and produces a
   normalized responsibility snapshot.
2. A rule-based ranker prioritizes the snapshot and detects changes.
3. Hermes presents the snapshot in desktop and delivers scheduled Telegram
   summaries.
4. The LLM explains, groups, and recommends; it does not invent source state.
5. A single Hermes gateway owns Kanban dispatch and notification polling, as
   required by Hermes's multi-gateway design.

Hermes cron sessions start without the current chat's memory. Therefore a
scheduled inbox check should use a deterministic script or a fully
self-contained prompt and source manifest. Mechanical collection should not
spend model tokens when no relevant state changed.

## Options

### Option A — Linked read model over existing sources

Recommended.

The inbox combines current source records, stores only attention metadata, and
links Hafiz back to the owner for action.

Benefits:

- no migration before value is proven;
- staff keep using Planner and developers keep using GitHub;
- state claims remain auditable;
- lower risk of duplicate or stale tasks;
- fits the existing Agent OS ownership model.

Tradeoff: each connector needs a clear freshness and failure rule, and some
actions initially open the owner rather than completing directly in the inbox.

### Option B — New central Responsibility database

Every responsibility is copied into a new database and managed there.

Benefit: one consistent schema and full control over the UI.

Tradeoff: creates two-way synchronization, conflict resolution, migration, and
the risk that staff, GitHub, or session state says something different. This is
the most expensive option and is not recommended for the first version.

### Option C — Scheduled conversational digest only

A scheduled Hermes job reads selected files and sends a summary without a
persistent inbox view.

Benefit: quickest prototype.

Tradeoff: weak inspection, deduplication, acknowledgement, and source-change
tracking. It proves reminder wording, but it does not satisfy the complete work
environment goal.

## Recommended First Usable Slice

Build only after the authority model is approved.

The smallest useful slice should:

1. read Mission Ledger, Session Maps, GitHub, active task files, and Planner
   through approved read-only lanes;
2. normalize only unresolved responsibilities that may need Hafiz;
3. deduplicate linked items without rewriting their owner;
4. show the top five in a desktop inbox with source, freshness, why now, and one
   next action;
5. deliver a Telegram digest only when the set materially changes;
6. let Hafiz snooze a reminder without marking the real task complete;
7. record unavailable or stale sources honestly;
8. prove one real journey: a staff blocker and its related approval appear as
   one priority responsibility, Hafiz opens the evidence, and staff can
   continue after the owning workflow is updated.

## Out Of Scope For The First Slice

- replacing GitHub, Planner, Mission Ledger, Session Maps, or Koda;
- automatically closing or mutating source tasks;
- automatic approval, merge, deploy, payment, auth, migration, or destructive
  actions;
- scanning every old chat and declaring inferred promises to be real tasks;
- WhatsApp delivery;
- staff rollout;
- upgrading or changing the protected live Hermes installation;
- a permanent Hermes fork before an upstream-extension gap is proven.

## Risks And Controls

| Risk | Control |
| --- | --- |
| Duplicate representations of one responsibility | Stable source identity plus relationship links; one displayed card may group several sources. |
| Stale “done” or “deployed” claims | Verify from the owning live source; label unavailable evidence honestly. |
| Too many alerts | Notify on material change, due threshold, or ended snooze; otherwise stay silent. |
| AI invents urgency | Deterministic priority tiers and visible “why now.” |
| Acknowledgement mistaken for completion | Keep attention state separate from source task state. |
| Sensitive data leaks to phone notifications | Minimal summaries, no secrets/private payloads, and privacy-hardening before production use. |
| Scheduler spends unnecessary model usage | Script-first collection and change detection; call the model only for a changed digest or explanation. |
| Multiple Hermes gateways contend for Kanban state | Exactly one dispatch-owning gateway; other profiles do not poll the Kanban databases. |
| Inbox silently becomes another task manager | Source-owner contract, read-only first slice, and tests that reject unsupported state claims. |

## Evidence Plan

Before calling the first slice useful, prove:

- **Contract tests:** each source maps only allowed fields and cannot claim a
  stronger state than it owns.
- **Freshness tests:** unavailable, stale, and conflicting sources remain
  visible and honestly labelled.
- **Priority fixtures:** staff-blocked and time-sensitive responsibilities rank
  above ordinary active and deferred work.
- **Deduplication fixtures:** a Planner blocker, Session Map approval, and
  Mission Ledger follow-up for the same outcome become one linked card.
- **Notification fixtures:** unchanged scans are silent; new, changed, due, and
  unsnoozed items notify once.
- **Desktop journey:** Hafiz can understand why the first item is first and open
  the source/work session.
- **Telegram journey:** a changed digest arrives without exposing sensitive
  identifiers or private payloads.
- **Cost evidence:** a no-change scan performs deterministic collection without
  an LLM call.
- **Isolation evidence:** no change to the protected live Hermes source,
  configuration, gateway, permissions, or credentials during development.

## Confirmed Authority Decision

Hafiz selected Option A on 2026-08-03:

```text
Use one linked Responsibility Inbox over the existing trusted sources.
Do not create a second central task database.
```

The alternatives considered were:

- **A — Linked read model (recommended):** existing systems keep ownership; the
  inbox combines them and owns only attention metadata.
- **B — New central database:** the inbox becomes the main owner of copied
  responsibility records.
- **C — Digest-only prototype:** test scheduled summaries without building the
  persistent inbox experience yet.

This decision gives Hafiz one place to see what matters while preserving the
Agent OS rule that current verified evidence and the proper source owner decide
what is true. It approves the product direction, not implementation.
