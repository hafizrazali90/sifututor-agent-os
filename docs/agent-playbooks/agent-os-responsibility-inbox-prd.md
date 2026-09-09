# Responsibility Inbox PRD

Status: draft for product clarification; linked read-model direction approved
by Hafiz on 2026-08-03; implementation not approved

## 1. One-Sentence Problem

Hafiz cannot reliably see which staff request, paused development session,
approval, active task, or deferred commitment needs him next because the work
is spread across several projects, sessions, and trusted systems.

## 2. Goal And Success Outcome

Create one personal Responsibility Inbox inside the native Agent OS work
environment that answers:

```text
What needs me now, who is waiting, why is it important, and what should I do
next?
```

Success means Hafiz can open the product, understand the top responsibility in
under a minute, inspect its source and evidence, and continue the real task
without remembering which project, chat, or task system contains it.

## 3. Target Users And Departments

### Primary user

- Hafiz, as product owner, developer, reviewer, approver, and staff unblocker.

### Indirect users

- Sifututor development and support staff whose Planner requests may need
  Hafiz's answer or approval.
- Claude, Codex, Hermes, and future agents performing work that reaches a human
  decision boundary.

Staff continue using their existing tools. The first version does not require
them to learn or log into the Responsibility Inbox.

## 4. Core Happy Path

1. The approved collector checks Session Maps, Mission Ledger, GitHub, active
   task files, and Teams Planner using the narrowest read-only access.
2. It finds a staff request blocked on Hafiz's approval, a paused development
   session, and two deferred ideas.
3. The inbox links the staff request and its related approval into one card
   instead of showing duplicates.
4. The rule-based ranker places that card first because another person cannot
   continue without Hafiz.
5. Hafiz opens the app and sees a short explanation: who is waiting, why this
   is first, how fresh the evidence is, and the recommended action.
6. Hafiz opens the evidence or resumes the related work session.
7. The owning Agent OS workflow performs any approved action. The inbox itself
   does not silently change Planner, GitHub, Git, or deployment state.
8. On the next scan, the source confirms that the blocker changed or was
   resolved, and the inbox updates accordingly.
9. Telegram stays silent unless something materially changed or a real reminder
   threshold was reached.

## 5. Functional Requirements

### Source collection

- Read active Session Maps for decisions, blockers, and exact next actions.
- Read Mission Ledger items with unresolved statuses.
- Query current GitHub issue and PR state.
- Read project active-task files when present.
- Query relevant Teams Planner staff intake without mutating cards.
- Report each source as fresh, stale, unavailable, or not configured.
- Never treat Koda or old chat as current responsibility truth without
  confirming or promoting the candidate into an owned source.

### Normalization and linking

- Convert each candidate into the approved Responsibility Card contract.
- Preserve the source identity, project, confidence, and freshness.
- Link related items that describe the same outcome.
- Show one primary card with its supporting sources rather than duplicate
  cards.
- Never infer `approved`, `complete`, `pushed`, `merged`, `deployed`, or `live`
  from a weaker source.

### Ranking

- Use the transparent priority order in the Product Shape.
- Put people blocked on Hafiz above ordinary active and deferred work.
- Explain why the first item ranks above the next item.
- Allow explicit business priority to influence ordering without hiding the
  original priority reason.
- Use AI for explanation and grouping assistance, not as the sole source of
  priority truth.

### Personal attention state

- Support new, seen, snoozed, and changed-since-seen states.
- Store the end of a snooze and the last observed source revision.
- Make clear that snoozing or acknowledging does not complete the source work.
- Bring a snoozed item back when the snooze ends or when its source materially
  changes.

### Actions

- Open the owning source.
- Resume the related native work session when available.
- Inspect linked evidence and source freshness.
- Ask the assistant to explain why the item matters.
- Snooze the reminder using a date or natural-language duration.
- Mark the item seen.
- Begin the appropriate Agent OS workflow for a response, review, approval, or
  task continuation.
- Require normal approval and permission gates for source mutations or outward
  actions.

### Source health

- Show when a connector could not be checked.
- Keep the last known item visible when useful, but label it stale.
- Do not silently remove a responsibility merely because its source is
  unavailable.
- Show the last successful check time without exposing credentials or private
  payloads.

## 6. UX Requirements And Entry Points

### Desktop entry points

- A `Today` or Responsibility Inbox entry in the native app navigation.
- A visible count for new or changed items that genuinely need Hafiz.
- A compact responsibility strip inside an active work session when another
  person becomes blocked.
- Global assistant input that accepts questions such as `What needs me?`,
  `What is staff waiting for?`, and `What should I do next?`.

### Desktop experience

- The first screen must show no more than five recommended items.
- The top card must identify who is waiting, why it is first, and one next
  action.
- Technical source names remain available but secondary to the plain-language
  meaning.
- Opening a card reveals sources, evidence, freshness, related work, and safe
  actions.
- Resuming work takes Hafiz into the actual chat, project, files, terminal, or
  review surface rather than a dead-end task page.

### Telegram entry points

- A morning or user-selected digest.
- Immediate messages only for a newly blocked person, an approved urgent rule,
  or a real reminder threshold.
- Natural-language follow-ups: `show why`, `what changed`, `snooze until
  Monday`, and `open on desktop`.
- A concise deep link or continuation instruction when the full work requires
  desktop.

## 7. Data And Business Logic

### Canonical responsibility fields

- stable source identity;
- source type and source link;
- project;
- title and plain-language explanation;
- category;
- who is waiting;
- recommended action;
- source confidence;
- source freshness and revision;
- real due date or clearly labelled age;
- related source identities;
- attention state and snooze end.

### Source ownership rule

The inbox owns only the personal attention overlay. The underlying systems own
the work state. A source refresh replaces old source-derived fields but
preserves valid attention preferences.

### Change detection

A material change includes:

- a new person becomes blocked;
- the requested decision or next action changes;
- the source status changes;
- a real due threshold is crossed;
- a linked item is added or removed;
- a stale or unavailable source becomes fresh again;
- the risk or affected audience increases.

Minor wording or timestamp-only changes must not create another alert.

## 8. Roles And Permissions

- The first version is private to Hafiz.
- Telegram access remains allowlisted.
- Source connectors begin read-only.
- Opening or resuming work does not grant stronger repository, GitHub, Planner,
  production, Claude, or Codex permissions.
- Planner changes, GitHub writes, commits, pushes, PRs, merges, deploys,
  production actions, critical-lane work, and destructive actions keep their
  existing Agent OS approval boundaries.
- The inbox must never display, log, or persist tokens, secret values, private
  authentication details, or unnecessary staff/customer payloads.

## 9. Notifications And Communication Rules

- Send a digest only when there are actionable responsibilities or meaningful
  changes.
- Use `[SILENT]` when a scheduled scan finds nothing new.
- Show at most the top three items in a normal Telegram digest, followed by a
  count of lower-priority items.
- Lead with practical meaning, not workflow labels.
- Every notification must include why it was sent now.
- Do not repeat an unchanged alert before its reminder policy permits it.
- A source failure notification should say what could not be checked and what
  remains known; it must not claim that no work exists.

## 10. Audit And Logging Requirements

- Record each collection run's time, source health, item count, and result.
- Record relationship and priority decisions in a form that can be explained.
- Record notification sent, suppressed, failed, and acknowledged events.
- Record snooze changes without treating them as task-state changes.
- Redact messaging identifiers and private payloads from routine logs.
- Keep enough provenance to answer why a card appeared or disappeared.

## 11. Edge Cases And Exception Handling

- Two sources disagree about whether work is complete.
- A Session Map contains stale Git, PR, or deployment wording.
- Planner reports a symptom that current technical evidence has not verified.
- One responsibility appears in Planner, GitHub, and a Session Map.
- A source is unavailable during the scan.
- Hafiz snoozes an item and its blast radius increases before the snooze ends.
- A due date is absent; the UI must show age rather than inventing a deadline.
- A task is waiting on someone other than Hafiz.
- A responsibility is resolved at source while its notification is in flight.
- Telegram delivery fails but desktop state remains current.
- A historical chat suggests a promise that was never promoted into a trusted
  source.
- Multiple Hermes profiles or gateways are running; only one may own Kanban
  dispatch and notification polling.

## 12. Rollout And Historical Data

1. Keep the protected live Hermes installation unchanged.
2. Build and test against an isolated current-version Hermes profile or a
   removable Agent OS integration.
3. Start with fictional fixtures for every source and failure state.
4. Add read-only local Agent OS sources.
5. Add read-only GitHub and Planner connectors through approved access lanes.
6. Run a private Hafiz-only pilot on desktop.
7. Add quiet Telegram delivery after privacy-hardening checks pass.
8. Review whether chat-history discovery adds value; do not bulk-import old
   chats into authoritative responsibility state.

There is no first-version migration into a central task database because the
approved design deliberately preserves existing owners.

## 13. Success Metrics

- Hafiz can identify the top responsibility and why it is first without
  opening another system.
- A person blocked on Hafiz is ranked above normal active or deferred work.
- Linked duplicates appear as one responsibility.
- An unchanged scan produces no Telegram message and no model call for
  mechanical collection.
- Every visible item names its source and freshness.
- Source outages create honest degraded states, not false empty results.
- No attention action is mistaken for source completion.
- Opening a responsibility reaches the correct evidence or work session.
- No protected live Hermes, permissions, credentials, or source-system state is
  changed during the isolated first-slice proof.

## 14. Risks And Mitigations

| Risk | Mitigation |
| --- | --- |
| Inbox becomes noisy | Material-change detection, priority thresholds, digest limits, and snooze. |
| Duplicate or conflicting task truth | Linked read model, source provenance, and context-authority conflict rules. |
| False AI urgency | Deterministic ranking and visible `why now`. |
| Stale state misleads Hafiz | Fresh checks, source health, and explicit stale labels. |
| Phone notification leaks information | Minimal summaries, redaction, allowlist, and privacy tests. |
| Integration becomes a permanent Hermes fork | Removable Agent OS layer first; fork only from proven upstream gaps. |
| No-change scans waste subscription usage | Script-first collection and comparison before model explanation. |

## 15. User Stories

- As Hafiz, I want to see who is waiting for me so I do not accidentally stop
  staff work.
- As Hafiz, I want one recommended next action so I do not need to reconstruct
  priorities from many chats.
- As Hafiz, I want to understand why an item is first so I can override it with
  informed judgment.
- As Hafiz, I want to resume the actual work from the responsibility card so
  the inbox is part of my work environment, not a separate reminder app.
- As Hafiz, I want to snooze a reminder without falsely marking the work done.
- As Hafiz, I want Telegram to alert me only when something meaningful changes.
- As a staff member, I want my existing Planner request to reach Hafiz when I
  am blocked without learning another system.
- As an agent, I want a clear human-decision boundary so I can stop, notify
  Hafiz, and resume with the correct evidence.

## Confirmed Decisions

- The product is a complete native work environment, not a reminder-only app.
- Desktop and Telegram are the first interfaces; WhatsApp is deferred.
- Agent OS owns orchestration; model workers remain selectable.
- The Responsibility Inbox uses the linked read model in Option A.
- Existing systems keep ownership; the inbox owns attention metadata only.
- The desktop uses smart landing: open Today for a fresh start and reopen the
  active workspace when Hafiz is continuing recent work.
- Telegram interrupts immediately only for a newly blocked person, an approved
  critical/time-sensitive threshold, or a material increase in impact; normal
  changes wait for the digest.
- Deferred work uses smart resurfacing: honor explicit dates or conditions,
  propose a review time when none is provided, and include undated items in a
  quiet weekly safety review.
- Possible promises found in old chats enter a private `Needs confirmation`
  queue with original context; they become real responsibilities only when
  Hafiz selects `Keep` and promotes them to the correct trusted source.
- Assistant actions are staged by risk: personal attention actions happen
  directly, while source-system, outward, critical, or destructive actions
  keep their preview, evidence, and existing Agent OS approval boundary.
- Telegram may be used to approve any class of action, but it never weakens
  the evidence or approval required for that action. Low-risk actions may use
  concise confirmation; higher-risk actions require a secure mobile evidence
  view, exact consequences, and stronger per-operation confirmation. If the
  required evidence cannot be shown safely on the phone, the flow must open
  the desktop evidence view instead. Tool access alone never counts as
  approval.
- The first version is Hafiz-only and read-only toward source systems.
- Implementation is not approved by this PRD draft.

## Current Design State

The major first UX decisions are confirmed. A local visual prototype now
demonstrates the Today screen, low-risk Telegram approval, evidence-rich mobile
approval, desktop fallback, and the transition back into active work at
`.agent-os/session-maps/artifacts/responsibility-inbox-ux-review-2026-08-03/index.html`.
This is still product design only; implementation requires separate approval.
