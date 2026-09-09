# Responsibility Inbox UX Spec

Status: first UX direction confirmed by Hafiz on 2026-08-03, including smart
landing, interruption threshold, deferred resurfacing, old-chat confirmation,
staged actions, and risk-scaled Telegram approvals; no implementation approved

## UX Goal

The product should feel like Hafiz has walked into a prepared workroom. The
assistant has already gathered what matters, placed the most important item on
top, and kept the actual projects, chats, files, terminals, and evidence within
reach.

It should not feel like opening another project-management tool.

## Pass 1 — User Intent And Mental Model

Hafiz's question is not normally `Which system should I check?` It is:

```text
What needs me, why does it matter, and can I continue the real work now?
```

The mental model is a personal chief-of-staff desk:

- the assistant gathers the morning folder;
- urgent staff blockers sit on top;
- every note says where it came from;
- Hafiz can ask questions conversationally;
- choosing an item opens the real workroom rather than another tracking page.

## Pass 2 — Information Architecture

### Native application shell

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Global bar: project/session search · Ask assistant · source health       │
├──────────────┬──────────────────────────────────────┬────────────────────┤
│ Navigation   │ Main work surface                    │ Assistant/context  │
│              │                                      │                    │
│ Today        │ Today / Inbox / Project / Session    │ Explain            │
│ Needs me     │ Chat / Files / Editor / Diff         │ Recommend          │
│ Staff blocked│ Terminal / Evidence                  │ Continue work      │
│ Active work  │                                      │                    │
│ Deferred     │                                      │                    │
│ Projects     │                                      │                    │
│ Sessions     │                                      │                    │
└──────────────┴──────────────────────────────────────┴────────────────────┘
```

The shell combines responsibility awareness with the existing native work
surface. The Inbox is a doorway into work, not a replacement for Projects or
Sessions.

### Responsibility views

| View | Purpose |
| --- | --- |
| `Today` | Top five recommended responsibilities plus the assistant's first recommendation. |
| `Needs me` | All unresolved decisions, reviews, and actions that require Hafiz. |
| `Staff blocked` | People who cannot continue without Hafiz, grouped with their related approval or evidence. |
| `Active work` | Current development and operational work with a safe next action. |
| `Deferred` | Future work and snoozed reminders, separated from urgent work. |
| `Source health` | Fresh, stale, unavailable, or unconfigured sources and last successful checks. |

## Pass 3 — Affordances And Action Clarity

Every card has one primary action based on its real next step:

- `Review evidence`
- `Resume session`
- `Open staff request`
- `Continue task`
- `Answer decision`

Secondary actions are consistent:

- `Why this first?`
- `Open source`
- `Snooze`
- `Mark seen`

Do not show `Complete` unless the owning source and workflow can safely perform
and verify completion. An inbox acknowledgement is never labelled complete.

## Pass 4 — Cognitive Load And Decision Minimization

- Show five recommended items at most on `Today`.
- Put one recommendation above the list rather than presenting equal choices.
- Group related sources under one card.
- Translate source-specific status into plain language first.
- Hide technical provenance behind a readable `Sources and evidence` section.
- Use a single visible reason for priority, with deeper reasoning on demand.
- Separate `Deferred` from `Needs me` so future ideas do not compete with staff
  blockers.
- Preserve the global assistant input so Hafiz can ask instead of learning
  filters.

## Pass 5 — State Design And Feedback

| State | What Hafiz sees |
| --- | --- |
| New | `New` dot and a short explanation of why it appeared. |
| Seen | Normal card without urgency animation. |
| Changed | `Changed since you last saw this` plus the exact meaningful change. |
| Snoozed | Hidden from Today until the chosen time unless the source becomes materially more urgent. |
| Stale | Last known information with `Could not refresh` and the last successful check. |
| Source unavailable | A visible degraded-state banner; never a false empty inbox. |
| Resolved at source | Removed from active views after refresh and available in recent history. |
| Conflicting sources | Warning that names the disagreement and directs Hafiz to the owning evidence. |
| No responsibilities | Calm empty state: `Nothing currently needs you. Your sources were checked.` |
| Loading | Existing items remain readable with a subtle refresh state; do not blank the screen. |

## Pass 6 — Flow Integrity Check

The experience is complete only if these transitions work:

```text
Responsibility discovered
-> source and freshness proven
-> related items linked
-> priority explained
-> Hafiz opens evidence or work
-> normal Agent OS approval boundary applies
-> source state changes
-> inbox refresh confirms the change
-> notification stops or next action appears
```

The flow fails if it ends at a card that cannot open the real work, if
acknowledgement is confused with completion, or if an old chat claim overrides
fresh source evidence.

## Screen 1 — Today

```text
Good morning, Hafiz                         Sources checked 8:42 AM

3 things need you · 1 person is blocked · 2 items changed

┌─ Recommended first ─────────────────────────────────────────────────────┐
│ A developer is waiting for your approval                               │
│ CRM · Staff blocked · checked 4 minutes ago                             │
│                                                                         │
│ Why first: your approval lets the developer continue today.            │
│ Recommended: review the evidence and approve or return with comments.   │
│                                                                         │
│ [Review evidence]   [Why this first?]   [Snooze]                        │
└─────────────────────────────────────────────────────────────────────────┘

Next
2. Resume the paused Agent OS design session              [Resume session]
3. Review a GitHub PR with passing checks                 [Review evidence]

Later
4. Deferred CRM reporting idea                            [Open] [Snooze]

Ask the assistant: [What should I do after the approval?_______________]
```

Key behavior:

- The headline describes workload in ordinary language.
- The top recommendation explains the human impact.
- `Sources checked` opens source health.
- The assistant input remains available without opening another chat.

## Screen 2 — Responsibility Detail

The detail opens as a drawer or side panel so Hafiz does not lose the Today
list.

```text
Developer waiting for CRM approval

What is needed
Review the completed work and approve it or return comments.

Who is waiting
Development staff · blocked since this morning

Why this is first
One approval unblocks active staff work; no higher-risk item is overdue.

Recommended action
[Review evidence]

Sources and evidence
✓ Planner staff request        checked 4 minutes ago · reported
✓ GitHub pull request          checked 3 minutes ago · verified remote state
✓ Session Map approval point  read now · trusted

Related work
CRM project · Review session · PR checks

[Open source] [Snooze] [Mark seen]
```

The detail never hides a source disagreement. If the Planner card says blocked
but GitHub shows no reviewable work, it reports that mismatch rather than
inventing an approval action.

## Screen 3 — Active Work Session

After `Resume session` or `Review evidence`, the main work surface changes to
the relevant project and session:

```text
┌ Project/files ┬ Chat, editor, diff, terminal, or evidence ┬ Context ────┐
│ CRM           │ Actual development/review work             │ Goal        │
│ files         │                                            │ Next action │
│ sessions      │                                            │ Approval    │
│               │                                            │ Inbox: 2    │
└───────────────┴────────────────────────────────────────────┴─────────────┘
```

A compact notification appears only if another person becomes blocked while
Hafiz is working. It should not force navigation away from the active task.

## Screen 4 — All Responsibilities

Use a scannable list, not a complicated project-management board.

Filters:

- project;
- category;
- who is waiting;
- new/changed/snoozed;
- source health;
- due or age.

Default grouping is by attention category, with staff blocked first. A Kanban
view may remain available for agent execution, but it is not the default human
Responsibility Inbox.

## Screen 5 — Source Health

```text
Source             State          Last checked        Meaning
Session Maps       Fresh          now                 3 active maps read
Mission Ledger     Fresh          now                 4 unresolved items
GitHub             Fresh          2 minutes ago       2 items need review
Planner            Unavailable    35 minutes ago      last known blocker kept
Active tasks       Fresh          now                 1 active task
```

The screen explains the practical impact of a failure. `Planner unavailable`
means the assistant cannot prove whether staff state changed; it does not mean
no staff are waiting.

## Telegram — Normal Digest

```text
Good morning, Hafiz. Three things need you today.

1. A developer is waiting for your CRM approval.
   Why first: approving it lets staff continue.
   Next: review the evidence.

2. Your Agent OS design session is ready to resume.
3. One GitHub review is waiting and its checks passed.

Two lower-priority items are deferred.

Reply: show 1 · why 1 · snooze 1 until Monday · open 1 on desktop
```

If nothing materially changed and no reminder threshold was reached, no
message is sent.

## Telegram — Immediate Staff Blocker

```text
A staff member is now waiting for your decision.

CRM approval · checked just now
Why now: their work cannot continue until you respond.
Recommended: review the evidence when available.

Reply: show evidence · snooze 30 minutes · open on desktop
```

The phone message contains only the minimum safe context. Detailed staff or
customer information remains in the approved source and desktop evidence view.

## Telegram — Degraded Source

```text
I could not refresh Planner.

I am keeping the last known staff blocker visible, but its current state is
not confirmed. GitHub, Session Maps, and Mission Ledger refreshed normally.

I will notify you when Planner is available again or if another trusted source
changes the priority.
```

## Empty, Error, And Partial States

- **Nothing needs Hafiz:** confirm which sources were successfully checked.
- **Some sources unavailable:** show known responsibilities and name the gap.
- **All sources unavailable:** show no priority recommendation; provide retry
  and last-known-state access.
- **Relationship uncertain:** show separate cards with a possible-link hint
  rather than incorrectly merging them.
- **Notification delivery failed:** keep desktop state current and surface the
  delivery failure in source/notification health.

## Accessibility And Responsive Behavior

- Keyboard access to navigation, cards, filters, drawer actions, and assistant
  input.
- Visible focus and non-color indicators for new, stale, blocked, and changed.
- Plain text labels alongside icons.
- No urgency conveyed only through animation.
- Narrow desktop collapses the right context panel before hiding the main
  responsibility explanation.
- Telegram remains a concise companion, not a compressed copy of every desktop
  control.

## First Journey To Prototype

Use fictional source fixtures to prove:

1. a staff blocker and related approval are linked;
2. the blocker is ranked first and the reason is understandable;
3. `Review evidence` opens a realistic evidence surface;
4. snooze changes only attention state;
5. a source-state update removes or changes the responsibility;
6. an unchanged scheduled scan stays silent;
7. a Telegram digest and urgent blocker message contain no sensitive data;
8. the protected live Hermes installation remains untouched.

## Visual Review Artifact

The first connected desktop-and-phone prototype is available locally at:

```text
.agent-os/session-maps/artifacts/responsibility-inbox-ux-review-2026-08-03/index.html
```

It shows five linked scenes: Today, low-risk Telegram approval, high-risk
secure mobile evidence and confirmation, honest desktop fallback, and return
to the real development workspace. Every example is fictional and every
button is prototype-only; it does not connect to Telegram, Hermes, a product
repository, or any live action.

## Confirmed Decision 1 — What Should Open First?

### A. Smart landing — selected by Hafiz on 2026-08-03

- On the first launch of the day or after a long break, open `Today`.
- When Hafiz returns shortly to an active task, reopen that work session and
  show a compact Inbox indicator.

Why: it protects forgotten responsibilities without interrupting focused work.

Tradeoff: the product must remember whether Hafiz is starting fresh or
continuing a work block.

### B. Always open Today

Why: the simplest and most predictable behavior.

Tradeoff: reopening the app during active development adds one navigation step
before returning to work.

### C. Always reopen the last workspace

Why: fastest for uninterrupted development.

Tradeoff: the most important reason for this product—preventing missed staff
and deferred responsibilities—becomes easier to overlook.

Confirmed behavior: use A, the smart landing behavior. This approval covers UX
direction only, not implementation.

## Confirmed Decision 2 — What Deserves An Immediate Telegram Alert?

### A. Only real interruption-worthy changes — selected by Hafiz on 2026-08-03

Send immediately when:

- a person becomes blocked waiting for Hafiz;
- an approved critical or time-sensitive threshold is reached;
- an existing responsibility materially increases in impact.

Put ordinary new tasks, resumed sessions, reviews, and deferred reminders in
the next digest.

Why: Hafiz is protected from missed staff blockers without Telegram becoming
another noisy task feed.

Tradeoff: a normal new task may wait until the next digest unless Hafiz asks
the assistant directly.

### B. Every new item that needs Hafiz

Why: the fastest awareness of all new responsibilities.

Tradeoff: frequent interruptions make important alerts easier to ignore.

### C. Digest only

Why: the quietest and simplest behavior.

Tradeoff: staff may remain blocked until the next scheduled digest.

Confirmed behavior: use A, immediate alerts only for real
interruption-worthy changes. This approval covers UX direction only, not
implementation.

## Confirmed Decision 3 — How Should Deferred Work Return?

### A. Smart resurfacing with a safety review — selected by Hafiz on 2026-08-03

- If Hafiz gives a date or condition, use it.
- If no date is given, the assistant proposes a reasonable review time in
  plain language.
- Undated items also appear in a quiet weekly deferred-work review so nothing
  disappears forever.
- A material change can bring an item back earlier with an explanation.

Why: this lets Hafiz say `remember this later` without needing to invent a date
every time, while keeping the assistant predictable and reviewable.

Tradeoff: the assistant must suggest timing, and Hafiz may occasionally adjust
an unsuitable suggestion.

### B. Only return on a date Hafiz explicitly sets

Why: complete control and no assistant timing guesses.

Tradeoff: any item captured without a date can remain hidden indefinitely.

### C. Show every deferred item in a fixed weekly review

Why: simple and reliable; nothing is permanently lost.

Tradeoff: the weekly list may become long and repeatedly show work that is not
yet relevant.

Confirmed behavior: use A, smart resurfacing with a weekly safety review. This
approval covers UX direction only, not implementation.

## Confirmed Decision 4 — What If An Old Chat Contains A Possible Promise?

### A. Put it in `Needs confirmation` — selected by Hafiz on 2026-08-03

The assistant may detect wording such as `do this later`, `come back to this`,
or `staff needs my answer`, but it does not immediately treat the wording as a
real task.

It shows Hafiz:

- the possible responsibility in plain language;
- the original chat/session and date;
- why it may still matter;
- the recommended owner, such as Mission Ledger or GitHub;
- actions: `Keep`, `Ignore`, or `Open original context`.

Only `Keep` promotes it into the correct trusted source and allows it to enter
normal responsibility ranking.

Why: this recovers useful promises from many old sessions without letting an
AI misunderstanding create false work or urgent alerts.

Tradeoff: Hafiz must occasionally confirm a short candidate list.

### B. Automatically add every likely promise

Why: maximum automatic recovery and the least manual confirmation.

Tradeoff: old brainstorming, rejected ideas, and casual language can become
false responsibilities and create noise.

### C. Ignore old chats entirely

Why: only structured trusted sources appear, giving the cleanest data.

Tradeoff: legitimate commitments that were never saved properly remain lost.

Confirmed behavior: use A, a private `Needs confirmation` queue with source
context. This approval covers UX direction only, not implementation.

## Confirmed Decision 5 — What Can The Assistant Do Directly?

### A. Staged actions based on risk — selected by Hafiz on 2026-08-03

The assistant may perform personal attention actions immediately:

- mark seen;
- snooze or change reminder timing;
- open the source;
- resume a work session;
- explain priority and evidence.

For actions that change another system or affect other people, the assistant
prepares the action, shows the exact effect, and follows the existing approval
workflow. Examples include replying to staff, changing Planner or GitHub,
committing, pushing, opening or merging a PR, deploying, and critical-lane
actions.

Why: Hafiz can work quickly from desktop or phone while retaining the same
Agent OS safety and evidence boundaries.

Tradeoff: some actions require a confirmation step instead of happening from
one tap.

### B. Read-only assistant

The assistant can explain, open, and resume, but never prepare or perform a
source change.

Why: simplest and safest first product.

Tradeoff: Hafiz must leave the assistant and manually complete routine actions
in other tools, weakening the goal of one complete work environment.

### C. Direct actions wherever access exists

The assistant carries out requested source actions immediately whenever its
credentials permit them.

Why: fastest and most automated experience.

Tradeoff: possession of access would be mistaken for approval, weakening the
existing safeguards around external, critical, and destructive actions.

Confirmed behavior: use A, staged actions based on risk and existing Agent OS
gates. This approval covers UX direction only, not implementation.

## Confirmed Decision 6 — Which Approvals Can Happen From Telegram?

### A+C. Any approval may happen from the phone, with risk-scaled evidence

Telegram may be used to approve any class of action, but the channel never
reduces the evidence, separation, or confirmation required by the existing
Agent OS rule for that action.

For clear, reversible, low-risk actions, Telegram may show a concise exact-
effect preview followed by one explicit confirmation.

Examples may include keeping an old-chat candidate, approving a prepared
low-risk staff reply, or confirming a clearly scoped reversible task update.

For evidence-heavy, outward, production, critical-lane, permission, or
destructive actions, the phone must provide a secure mobile evidence view that
shows the exact target, current state, proposed effect, material evidence,
consequences, and the existing approval boundary. The final action requires a
stronger, separate confirmation for that exact operation. Critical-lane phase
separation and per-operation approval remain intact.

Examples include substantial code review, commit/push/PR decisions, merge,
deploy, production, auth, payment, invoice, commission, migration, mobile API,
permission, and destructive actions.

If the phone cannot display the required evidence safely or completely, it must
end with `Open on desktop to review` rather than offering an unsafe approval.
Possession of credentials or tool access never counts as approval.

Why: Hafiz gets C's remote-control freedom with A's risk-based safety. The
decision depends on the quality of evidence and confirmation, not an arbitrary
device restriction.

Tradeoff: high-risk mobile approval is substantially more complex to design and
secure than a short Telegram reply. Some actions will still fall back to
desktop when the evidence cannot fit a safe mobile review.

Confirmed behavior: use the A+C hybrid. Any class of action may be approved
from the phone only through evidence and confirmation proportionate to its
risk; otherwise the flow falls back to desktop. This approval covers UX
direction only, not implementation. The major first UX decisions are now
complete, and the recommended next design artifact is a visual prototype for
review.
