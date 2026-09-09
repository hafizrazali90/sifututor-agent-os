# Native Agent OS Workspace — Omnigent Build-Ready Plan

Status: product direction confirmed; Slice 0 plus Slice 1 local implementation
experiment approved 2026-08-06. Commit, push, PR, merge, pilot upgrade, staff
rollout, and production remain separate gates.

## 1. Plain-Language Outcome

Improve the isolated Omnigent-based Agent OS workspace so Hafiz can start,
understand, supervise, pause, resume, and complete several real work sessions
without remembering what happened in every chat.

The product remains a chat-first working environment. It does not become a
traditional project-management application. The chat is where Hafiz asks for
work; the surrounding interface explains what each session is doing, what it
needs, what remains, and what tools or permissions are active.

The finished experience has four working surfaces:

1. **Control Room** — several live sessions visible and directly replyable at
   once.
2. **Focus Workspace** — one complete chat-led task with files, terminal,
   evidence, workers, and a Session Work Tree.
3. **Worker Sidebar** — the current orchestrator and delegated workers, their
   activity, evidence, and approval boundary.
4. **Split Focus** — two or more complete Focus Workspaces open together.

Global supporting surfaces add `Needs You`, `Future Work`, `Projects`, and
`Usage` without replacing the real sessions where work happens.

## 2. Sources And Ownership

This plan consolidates Hafiz's confirmed decisions from the 2026-08-04 to
2026-08-06 personal-pilot review. It should be read with:

- `docs/agent-playbooks/mission-ledger/cross-project.md`, especially
  `AO-CONTINUITY-001` and `AO-RUNTIME-001`;
- `docs/agent-playbooks/agent-os-omnigent-foundation-fit-test.md` for runtime,
  policy, isolation, and checkpoint evidence;
- `docs/agent-playbooks/agent-os-responsibility-inbox-product-shape.md`;
- `docs/agent-playbooks/agent-os-responsibility-inbox-prd.md`;
- `docs/agent-playbooks/agent-os-responsibility-inbox-ux-spec.md`; and
- the isolated pilot at
  `/Users/hafizrazali/Projects/Omnigent-pilots/agent-os-local-pilot`.

Ownership boundaries:

- Omnigent owns sessions, projects, providers, workers, tools, and the native
  interface.
- Agent OS owns workflow meaning, task continuity, evidence rules, approval
  boundaries, memory routing, and responsibility state.
- Provider adapters transport Claude/Codex events; they do not own the shared
  product model.
- The Responsibility Inbox is a read model for attention. It does not silently
  mutate GitHub, Planner, Git, deployment state, or session work.

## 3. Problem Being Solved

The current pilot can run genuine Claude and Codex subscription sessions, show
several sessions in Control Room and Split Focus, expose workers, and collect
cross-session attention. The remaining experience is still too dependent on
Hafiz remembering the meaning of each chat.

The pilot currently has these practical gaps:

- permission mode is mainly a launch-time setting and is not visible like the
  familiar Claude/Codex controls inside a running session;
- conversation context is visible, but subscription usage does not have one
  reliable home;
- `New session` exists in the primary navigation but is not treated as the
  most common global action;
- Codex starts all globally enabled MCP servers, including tools unrelated to
  the task, which creates slow startup and misleading failure warnings;
- Projects exist, but project discovery, visible correction, unfiled sessions,
  and multi-project work are not explained well enough;
- Control Room needs a clear session-first lifecycle so active, waiting,
  paused, completed, and historical sessions do not become one undifferentiated
  list;
- the current right-side checklist mirrors provider todos and can disappear or
  lose context; it does not yet represent a durable multi-task session;
- deferred and newly discovered work needs one reliable future-work home rather
  than being buried inside old chat.

## 4. Confirmed Product Decisions

### 4.1 Chat remains the control surface

Hafiz describes work naturally in chat. The agent creates and maintains
structure behind the conversation. Hafiz does not have to select a work-tree
row before discussing it; mentioning the task normally is enough.

Clicking a work item opens its context and evidence. It does not change which
task the next chat message is allowed to discuss.

### 4.2 Session Work Tree lives inside the session

The existing right-side checklist area becomes the Session Work Tree. It shows
what is happening in this conversation, including multiple tasks, subtasks,
discoveries, waiting items, and completed work.

The tree supports at most three visible levels:

```text
Programme or session goal
└── Task
    └── Subtask
```

Deeper technical activity belongs in expandable evidence, not another nesting
level.

Each visible row contains:

- a short plain-language title;
- one status icon;
- an optional one-sentence brief when the title alone is unclear;
- project identity when it differs from the session's home project; and
- an expandable detail containing why it matters, evidence, exact delivery
  state, blockers, source, and next action.

Use six work-status icons:

| Icon | Meaning |
| --- | --- |
| `○` | Not started |
| `●` | Working now |
| `◷` | Waiting for a person, check, or external result |
| `Ⅱ` | Paused or intentionally deferred |
| `!` | Blocked by a problem |
| `✓` | Done for its stated finish line |

Delivery state remains separate and appears in details: local only, committed,
pushed, PR open, merged, deployed, live checked, monitored, accepted, or
closed. A green work-status icon must never imply production delivery.

Completed branches remain visible for continuity but collapse automatically.
The user can reopen them. A meaningful development session receives a work
tree automatically; casual questions do not require one.

### 4.3 Intelligent discovery routing

When work discovers another item, the orchestrator classifies it visibly:

- required for the accepted finish line: add it under the current task;
- related but safe for later: add it paused under `Related later`;
- unrelated: add it under `Discovered work` and offer to defer it;
- changes scope, business meaning, permissions, risk, or approval: stop and ask
  Hafiz before adopting it.

The agent proposes the classification. Hafiz may correct it in chat or edit the
tree directly.

### 4.4 Deferred work has a global home

`Future Work` is a global, searchable list with project filters. A deferred
item preserves:

- a plain-language explanation;
- its source session and source work item;
- home and related projects;
- why it was deferred;
- the highest freshly proven state;
- the exact next useful action;
- dependencies, staff impact, and any meaningful review date; and
- whether it should resume in the original session, a new session, or another
  project.

Future work resurfaces intelligently through digests, dependencies, real
deadlines, or people waiting. It never restarts itself silently.

### 4.5 Control Room is session-first

Every Control Room lane represents one session, not one individual task. It
preserves the existing full live-chat behavior: independently scrollable
conversation, reply composer, status, project, model, finish line, evidence
summary, and current work item.

The default view contains:

- actively working sessions;
- sessions waiting for Hafiz or another person;
- blocked sessions; and
- recently completed sessions for a short, configurable period.

Filters reveal `Active`, `Needs you`, `Waiting`, `Paused`, `Completed`, and
`All sessions`. Older completed sessions remain searchable history. The
application never changes the active Focus Workspace because another session
updates.

Operational state is detected automatically. Hafiz controls lifecycle state:
active, pause, defer, complete, reopen, or archive. An explicit user lifecycle
choice overrides automatic inference until Hafiz changes it or the agreed
expiry rule applies.

### 4.6 Projects are visible, correctable, and safe

Starting a session automatically proposes the project from the selected
workspace. The proposed project is visible and correctable before or after the
first message.

The system must not silently create a new Project. If no project matches, the
session remains `Unfiled` and presents `Add project` or `Choose project`.

A multi-project session has:

- one home project for ownership and default workspace;
- zero or more related projects; and
- an optional per-work-item project assignment.

This prevents one cross-project session from being duplicated into several
unrelated sessions while still keeping project filters accurate.

### 4.7 New Session is a primary action

`New session` remains the first primary-navigation action and gains an
always-visible top-level compose button or icon. It must be reachable without
scrolling project/session lists.

The New Session surface stays chat-first. Advanced configuration is compact,
not a mandatory wizard.

Before the first message it shows:

- Agent OS orchestrator engine: Auto, Codex, Claude, or another proven engine;
- provider/model variant when available;
- permission mode;
- `Tools: Auto` summary;
- proposed home project and related projects;
- workspace/worktree selection; and
- the editable finish-line understanding after the request is interpreted.

### 4.8 Permission control uses provider-native meaning

Every session displays an always-visible shield near the composer. It uses the
provider's real supported modes and explains them in normal language instead
of pretending Claude and Codex have identical technical controls.

Requirements:

- show the current effective mode, not only the selected preference;
- preserve existing global Claude/Codex permissions and authentication;
- show a strong warning for unrestricted/full-access modes;
- keep bypass or dangerous modes under an explicit `Advanced` disclosure;
- never weaken Agent OS approval gates because the provider mode is broader;
- allow an in-session change when supported; and
- when the provider requires relaunch, restart only that worker while
  preserving the same session, transcript, Work Tree, project, and pending
  message draft.

If safe restart fails, return to the prior proven mode and show the error. Do
not leave the interface claiming that the requested mode is active.

### 4.9 Usage is truthful and separated by meaning

Each chat keeps its existing context-window meter. This answers: `How full is
this conversation?`

A global `Usage` entry in the sidebar footer opens a provider breakdown. This
answers: `How much Claude or Codex subscription availability remains, and when
does it reset?`

The global panel may show only provider-confirmed values:

- provider and authenticated account identity when safely available;
- plan or subscription type when officially exposed;
- current limit window and remaining/reset information;
- last successful refresh and degraded/unavailable state; and
- a provider-native link or instruction when the value must be checked outside
  Omnigent.

Never infer subscription usage from local token counts or invent a percentage.
`Not available from provider` is an acceptable result.

### 4.10 MCP tools load by task, not all at startup

The default Core profile is engine-aware:

- `omnigent` — required for every native session bridge; and
- `codex_apps` — connector/app gateway when the active engine is Codex.

Claude must not be asked to load a nonexistent `codex_apps` equivalent. It
starts with the shared Omnigent bridge and adds its own available task-specific
tools. The interface still calls both variants `Core`; its expanded detail
shows the exact engine-specific contents.

Task-triggered MCP choices are:

| Need | MCP |
| --- | --- |
| Browser/UI/QA | `chrome-devtools` |
| Staff intake and Planner | `microsoft365` |
| Design files | `figma` |
| Claude design-pattern research | `mobbin` when available to Claude |
| DNS/Cloudflare infrastructure | `cloudflare` |
| Backup/object storage | `wasabi` |

`plane` is removed from the workspace MCP choices. `neon` is not currently
used and stays hidden as a future optional integration unless Hafiz explicitly
enables it later.

Koda remains the approved direct Agent OS helper, not a chat-level MCP startup
dependency. GitHub, shell, local files, and native web capabilities also do not
become MCP profile entries merely because the agent can use them.

The New Session screen shows:

```text
Tools: Auto — Core tools loaded, more added when needed
```

Clicking it reveals selected, suggested, available, unavailable, and failed
tools. Hafiz may override the selection.

Quality rules:

- preflight known task requirements before the worker starts;
- activate a newly required tool before relying on it;
- preserve transcript and Work Tree if activation needs a worker restart;
- distinguish required-tool failure from an irrelevant optional failure;
- never claim an external check passed when its tool was not active; and
- allow manual `All tools` only as an Advanced choice, not the default.

## 5. Information Architecture

```text
Global shell
├── + New Session
├── Control Room
│   └── live session lanes
├── Split Focus
│   └── two or more complete workspaces
├── Needs You
│   └── approvals, questions, failures, completed work needing review
├── Future Work
│   └── deferred and discovered work across projects
├── Automations
├── Projects
│   └── project folders and their sessions
├── Sessions
│   └── unfiled and recent sessions
└── Footer
    ├── Usage
    ├── Source/tool health
    └── Settings

Focus Workspace
├── chat transcript and composer
├── files/editor/diff/evidence/terminal panels
└── right sidebar
    ├── Session Work Tree
    ├── Current worker and delegated workers
    ├── finish line and proven state
    └── approval and attention state
```

`Needs You` and `Future Work` are distinct:

- Needs You contains an action, decision, failure, or completed outcome that
  currently deserves Hafiz's attention.
- Future Work contains intentionally deferred commitments and ideas that do not
  currently deserve interruption.

## 6. Core User Journeys

### Journey A — Start a normal development session

1. Hafiz selects the global New Session action.
2. The interface remembers Codex as the usual orchestrator but allows Auto or
   Claude.
3. Workspace selection proposes a home project.
4. `Tools: Auto` preselects the engine-specific Core profile for an ordinary
   code task.
5. Permission mode is visible before send.
6. Hafiz describes the work naturally.
7. Agent OS shows a small correctable understanding and finish line.
8. The first meaningful Work Tree appears without a setup form.

### Journey B — Work discovers another task

1. The agent finds a related problem while building the accepted task.
2. It classifies the item as required, related later, unrelated discovered
   work, or scope-changing.
3. The Work Tree updates with a short title and brief.
4. Hafiz continues talking normally or corrects the classification.
5. If Hafiz stops early, remaining items are paused or moved to Future Work
   with source, evidence, and next action intact.

### Journey C — Supervise several sessions

1. Control Room shows each active conversation as one live session lane.
2. Normal progress changes the lane status without stealing focus.
3. Hafiz replies directly in any lane or opens it in Focus Workspace.
4. A real blocker appears in Needs You and on the affected lane.
5. Completed work remains recent, then moves to searchable history.

### Journey D — Add a tool during a session

1. A code task later requires browser QA.
2. The orchestrator says Chrome DevTools is required and why.
3. It activates that MCP or performs a safe worker restart.
4. The transcript, Work Tree, draft, project, and finish line survive.
5. Only after successful activation may browser evidence be claimed.

### Journey E — Resume deferred work

1. Hafiz opens Future Work or asks what can be done next.
2. The assistant explains why an item resurfaced and shows fresh/stale source
   state.
3. Hafiz resumes the original session, starts a new session, or moves it to a
   different project.
4. The new active Work Tree links back to the deferred source without copying
   stale completion claims.

## 7. Durable Data Model

The current provider todo stream is transient and in-memory. It may remain an
input, but it cannot be the canonical Session Work Tree.

### 7.1 Session work item

Add a provider-neutral persisted work-item model. Suggested fields:

| Field | Purpose |
| --- | --- |
| `id` | Stable work-item identity |
| `session_id` | Owning Omnigent session |
| `parent_id` | Optional parent; enforce maximum depth three |
| `title` | Short plain-language row title |
| `brief` | Optional one-sentence context |
| `status` | not_started, working, waiting, paused, blocked, done |
| `delivery_state` | local, committed, pushed, pr_open, merged, deployed, live_checked, monitored, accepted, closed, or null |
| `home_project_id` | Project owning this work item when different from session home |
| `source_kind` | user, orchestrator, worker, provider_todo, discovered, resumed |
| `source_ref` | Safe reference to message, provider todo, issue, or deferred item |
| `discovery_class` | required, related_later, unrelated, scope_change, or null |
| `why` | Why it belongs in the tree |
| `next_action` | One practical next move |
| `evidence_summary` | Human-readable highest proven state |
| `sort_order` | Stable sibling order |
| `collapsed` | User display preference for this tree |
| `version` | Optimistic-concurrency revision |
| timestamps | Created, updated, completed, deferred |

Do not encode the complete tree into conversation labels. Labels are useful for
small routing facts, but the existing value width, concurrent updates, and
query requirements make them the wrong owner for a durable tree.

### 7.2 Session work tree API

Add session-scoped endpoints, following existing session authorization:

```text
GET    /v1/sessions/{id}/work-tree
POST   /v1/sessions/{id}/work-items
PATCH  /v1/sessions/{id}/work-items/{item_id}
DELETE /v1/sessions/{id}/work-items/{item_id}
POST   /v1/sessions/{id}/work-items/{item_id}/defer
POST   /v1/sessions/{id}/work-items/{item_id}/resume
```

Mutations require the current item version. Conflicting edits return an
explicit conflict and refresh the tree instead of silently overwriting user
changes.

Publish `session.work_tree` events so Control Room, Focus Workspace, and Split
Focus stay synchronized without polling each lane independently.

### 7.3 Provider todo normalization

Claude `TodoWrite` and Codex plan updates become observations, not authority.
The normalization layer:

1. receives provider todo updates;
2. matches them to stable work items through provider source IDs or conservative
   normalized matching;
3. proposes new items when no safe match exists;
4. never deletes user-created context because a provider emitted a shorter
   list; and
5. records the provider observation separately from the Agent OS status.

Manual user edits win over provider wording. Provider completion may move a
work item to `done` only for its work status; it does not infer commit, merge,
deploy, or live state.

### 7.4 Session lifecycle and project relationships

Keep the existing first-class `projects` table and session `project_id` as the
home project. Add a related-project relation instead of duplicating sessions.

Persist user lifecycle state separately from computed operational state:

```text
user lifecycle: active | paused | deferred | completed | archived
operational: idle | working | waiting | needs_you | blocked | failed
```

Views combine both but never overwrite an explicit lifecycle choice merely
because the runner becomes idle.

### 7.5 Future work

Future Work should reuse or link to the Responsibility Inbox's normalized
source contract, but own a persistent deferred-work record. Deferring a work
item is transactional:

1. create/update the deferred record;
2. link source session and work item;
3. mark the session item paused/deferred;
4. publish both session and responsibility events; and
5. retain an audit entry.

Resuming creates a new active link; it does not destroy the deferral history.

### 7.6 Permission, tool, and usage state

Persist requested and effective permission mode separately. Persist the
per-session tool profile and each tool's selected/required/startup state. Never
store credentials in these records.

Usage snapshots contain only provider-returned limits and timestamps. Treat
them as short-lived read data, not permanent billing truth.

## 8. Real Implementation Entry Points

The builder must confirm current upstream paths before editing, but the pilot
currently exposes these ownership points:

| Concern | Existing owner to evolve |
| --- | --- |
| Global navigation and New Session placement | `web/src/shell/Sidebar.tsx` and the existing home composer |
| Focus chat, composer, context meter, model/effort config | `web/src/pages/ChatPage.tsx` |
| Worker rail and current Task Brief | `web/src/shell/SubagentsPanel.tsx` |
| Session-first multi-chat view | `web/src/pages/ControlRoomPage.tsx` |
| Multiple complete workspaces | `web/src/pages/SplitFocusPage.tsx` |
| Session client state and SSE | `web/src/store/chatStore.ts`, `web/src/lib/sse.ts`, session hooks/APIs |
| First-class project CRUD | `web/src/lib/projectsApi.ts`, `web/src/hooks/useConversations.ts`, server project/session routes |
| Claude todo observations | `omnigent/claude_native_bridge.py`, `omnigent/claude_native_forwarder.py` |
| Codex plan/todo observations | `omnigent/codex_native_forwarder.py` |
| Codex MCP startup and subscription app-server | `omnigent/codex_native_app_server.py`, `omnigent/codex_native_forwarder.py` |
| Shared session schemas and events | `omnigent/server/schemas.py`, `omnigent/server/routes/sessions/` |
| Durable storage and migrations | `omnigent/db/db_models.py`, `omnigent/db/migrations/`, a dedicated store matching existing store patterns |
| Permission launch configuration | native coding-agent definitions, session creation payload, native runner orchestration |

Do not expand `ChatPage.tsx` indefinitely. Extract dedicated components and
hooks for Permission Mode, Tool Profile, Usage, and Work Tree. Keep framework
workflow instructions in the shared runtime prompt owner, not duplicated in
Claude and Codex adapters.

## 9. Implementation Slices

Each slice gets its own GitHub issue, permanent regression evidence, and review.
Normally it also gets its own branch/worktree. The approved Slice 0 plus Slice 1
usage-saving experiment is the narrow exception: those two dependency-bound
slices share one integration branch, one Claude builder loop, and one reviewed
PR while keeping separate acceptance evidence for issues #53 and #54. Later
slices return to separate branches/worktrees. Do not implement the complete
programme as one large PR.

### Slice 0 — Contract and persistence foundation

Purpose: establish provider-neutral state before changing the interface.

- create work-item, related-project, lifecycle, deferral, tool-profile, and
  permission-state contracts;
- add migrations and stores;
- add session-scoped APIs and SSE events;
- define concurrency, authorization, and audit behavior; and
- preserve old sessions with empty/new defaults.

Stop point: APIs and migrations verified; no visible UI dependency required.

### Slice 1 — Durable Session Work Tree

Purpose: replace the transient checklist with the agreed in-session work view.

- render the Work Tree in the existing right-side task/checklist surface;
- support three levels, six statuses, briefs, details, edits, reorder, collapse,
  and per-item project;
- normalize existing Claude and Codex todo observations;
- auto-create meaningful trees and skip casual chats;
- preserve trees across reload, worker restart, resume, and provider change;
  and
- show exact delivery state only from evidence-backed sources.

Stop point: one Claude and one Codex session can create, update, reload, and
resume the same durable tree.

### Slice 2 — New Session control centre

Purpose: make the common action fast and understandable.

- add the persistent top-level New Session action;
- keep it first in primary navigation;
- show orchestrator/model, permission, Tools Auto, project, workspace/worktree,
  and smart understanding without creating a setup wizard;
- automatically propose but never silently create a project; and
- support one home plus related projects.

Stop point: a user can start correctly scoped Codex and Claude sessions from
the same consistent surface.

### Slice 3 — Runtime permission and smart-tool controls

Purpose: expose current authority and avoid unnecessary MCP startup.

- add the always-visible session shield;
- map provider-native permission modes and effective state;
- implement safe single-worker restart with state preservation;
- add Core and task-triggered MCP selection;
- add the Tools Auto inspector and manual override;
- remove Plane from choices and hide Neon; and
- make required-tool failures actionable while suppressing irrelevant optional
  startup noise.

Stop point: a running session can change a supported permission or add a
required browser tool without losing its transcript or Work Tree.

### Slice 4 — Session lifecycle, Control Room, and project visibility

Purpose: make many sessions understandable without reducing them to cards.

- preserve full live Control Room lanes;
- add lifecycle filters and recent-completion behavior;
- show home/related projects, current work item, finish line, and needs-you
  state;
- ensure explicit pause/defer/complete/reopen overrides automatic state;
- improve Unfiled and Add Project affordances; and
- keep Split Focus consistent with the same session truth.

Stop point: active, waiting, paused, completed, and historical sessions appear
in the correct view and remain directly replyable.

### Slice 5 — Future Work and discovery continuation

Purpose: ensure stopping early does not lose work.

- add the global Future Work view;
- connect `Related later` and `Discovered work` to deferral;
- preserve explanation, source, proof, reason, and next action;
- support resume original/new/move project;
- integrate intelligent low-noise resurfacing with Needs You and digests; and
- never auto-start deferred work.

Stop point: a discovered item can be deferred, found globally, and resumed with
fresh state.

### Slice 6 — Usage and source health

Purpose: show useful availability without making up numbers.

- retain per-chat context usage;
- add the global Usage footer entry and drawer/page;
- integrate official Codex rate-limit/usage interfaces where supported;
- use only official Claude availability exposed by its CLI/service;
- show unavailable, stale, loading, and failed states honestly; and
- keep subscription usage separate from local tokens and API-key spend.

Stop point: Hafiz can distinguish conversation fullness from provider
availability for both orchestrators.

### Slice 7 — Integrated acceptance and personal-pilot upgrade

Purpose: prove the complete daily workflow before staff design.

- merge the slices through normal review;
- upgrade only the isolated personal pilot;
- preserve existing normal Omnigent, Claude, and Codex configuration;
- run real non-critical Claude and Codex sessions;
- verify Control Room, Focus Workspace, Split Focus, Needs You, Future Work,
  tools, permissions, usage, and resume behavior; and
- document rollback and remaining staff-readiness gaps.

Stop point: Hafiz accepts or rejects the improved personal workflow. Staff
rollout remains a separate decision.

## 10. Test And Evidence Plan

### Backend and contract tests

- migration up/down and existing-database compatibility;
- work-tree depth, parent ownership, sort, version conflict, and authorization;
- atomic defer/resume behavior;
- home/related-project membership and deleted-project handling;
- requested-versus-effective permission state;
- tool-profile validation, required-tool failure, and no credential storage;
- usage freshness and unknown-value handling; and
- SSE reconnect/snapshot recovery.

### Adapter tests

- Claude TodoWrite creates or updates observations without deleting user
  context;
- Codex plan updates map conservatively and preserve manual wording;
- provider completion does not invent delivery state;
- provider switch and worker restart keep stable work-item IDs; and
- optional MCP failures do not mark the core session failed.

### Web unit/component tests

- all six Work Tree statuses and delivery-state details;
- three-level maximum and accessible expand/collapse behavior;
- short title plus optional understandable brief;
- New Session placement and keyboard accessibility;
- project proposal, Unfiled state, explicit Add Project, and related projects;
- permission warnings, effective-mode mismatch, restart rollback;
- Tools Auto selection and manual override;
- Control Room filters and manual lifecycle precedence;
- Future Work source/freshness/resume choices; and
- Usage confirmed/unavailable/stale states.

### Permanent E2E journeys

1. Start a Codex session with Core tools, inferred project, and visible
   permission mode.
2. Start a Claude research session and load only its required research tools.
3. Create a multi-task Work Tree, discover a related item, defer it, reload the
   app, and recover the same tree.
4. Change permission mode through a safe worker restart and prove the
   transcript, draft, project, and tree survive.
5. Add Chrome DevTools on demand and prove browser evidence is impossible to
   claim before successful activation.
6. Run four independent sessions in Control Room, reply to each, filter states,
   and verify no transcript crosses session IDs.
7. Open two complete sessions in Split Focus and confirm their work trees and
   worker states remain isolated.
8. Resume one Future Work item into a new session with source and fresh-state
   reconciliation.
9. Show context usage and provider usage independently, including a provider
   that reports `Not available`.

### Visual and human-journey evidence

- screenshot the New Session surface, focused Work Tree, permission selector,
  Tools Auto drawer, Control Room at 2/3/4 columns, Future Work, and Usage;
- inspect light and dark themes at laptop and wide-desktop sizes;
- verify copy is understandable without workflow knowledge;
- test keyboard navigation, focus order, screen-reader labels, reduced motion,
  empty/loading/error/degraded states, and narrow viewport behavior; and
- provide a short personal acceptance script after the isolated pilot upgrade.

## 11. Edge Cases And Failure Rules

- If project inference is ambiguous, keep the session Unfiled and ask; never
  create a folder silently.
- If one session touches several projects, do not clone or duplicate the
  conversation.
- If provider todos are reordered or rewritten, do not recreate the whole tree
  or erase user briefs.
- If the agent discovers many noisy implementation details, group them under
  evidence rather than exceeding three visible levels.
- If a worker dies during permission/tool restart, preserve state and offer
  retry, revert, or continue without the optional tool.
- If a required MCP fails, block only the dependent evidence/action, not the
  entire unrelated session.
- If usage cannot be read, say so. Never infer a subscription balance from
  token counts.
- If a project is deleted, retain sessions and work items as Unfiled with their
  former project name in audit history.
- If two windows edit the same work item, reject the stale revision and explain
  the conflict.
- If a completed item later regresses, reopen it with a visible reason rather
  than silently removing its completion history.
- If a deferred item's source becomes unavailable, keep the last known record
  visibly stale.
- If a task is casual conversation, do not manufacture a project plan merely
  to fill the panel.

## 12. Security And Approval Boundaries

- No slice may modify or import normal `~/.claude`, `~/.codex`, or
  `~/.omnigent` authentication, settings, permissions, or secrets.
- Permission modes govern provider actions but never replace Agent OS commit,
  push, PR, merge, deploy, production, critical-lane, or destructive gates.
- Tool profiles store names and state only; never tokens or credential values.
- Usage integration uses official provider interfaces and does not scrape or
  copy authentication caches.
- Work Tree and Future Work details must not expose secrets, raw tool payloads,
  or unnecessary staff/customer data.
- The personal isolated pilot remains the first rollout target. Staff design,
  messaging rollout, production deployment, and automatic self-improvement are
  out of scope.

## 13. Out Of Scope

- staff rollout or multi-user administration;
- WhatsApp or Telegram implementation;
- replacing Koda, GitHub, Planner, Mission Ledger, or Git as source owners;
- changing existing Claude/Codex global permissions or authentication;
- enabling Plane or Neon;
- automatic push, PR, merge, deploy, or destructive actions;
- redesigning the complete Omnigent visual language;
- uncontrolled autonomous skill or Agent OS self-rewriting; and
- production adoption before personal acceptance.

## 14. Claude Builder Usage-Savings Experiment

Slice 0 and Slice 1 are also a measured delegation experiment. The purpose is
not merely to prove that Claude can write the code; it is to determine whether
Claude can own the long implementation-and-repair loop while Codex preserves
architecture and quality with materially less reasoning and rework.

The live record is:

`.agent-os/session-maps/artifacts/omnigent-session-work-tree-claude-builder-usage-experiment-2026-08-06.md`

Operating boundary:

- Codex owns one build-ready contract, architecture and risk decisions, and
  one narrow final evidence review.
- One Claude builder owns repository discovery, implementation, tests, repair,
  and the sanitized handback for Slice 0 and Slice 1.
- A fresh Claude session performs adversarial review without editing.
- The builder receives at most one consolidated correction packet. A second
  material miss stops the experiment for contract/test improvement instead of
  starting an open-ended back-and-forth loop.
- Routine progress checks use the delegation status script and do not consume
  another model turn.

Initial targets:

- zero Codex product-code edits unless the experiment is declared failed;
- one builder job and one fresh reviewer job, excluding a genuinely required
  setup recovery;
- no more than one consolidated correction round;
- zero escaped blocking or major defects at the final Codex review;
- no routine Hafiz approvals between launch and the next genuine risk gate;
- all Slice 0 and Slice 1 migration, API, event, UI, adapter, and permanent E2E
  evidence remains mandatory; and
- exact token savings are reported only when both providers expose comparable
  counters. Otherwise the decision uses the operational measures above and
  marks token savings `unavailable`.

Only a measured, repeatable improvement should become the default Agent OS
delegation method.

## 15. Success Measures

The personal pilot succeeds when:

- Hafiz can identify what every visible session is doing in under one minute;
- a session with several tasks remains understandable after reload or model
  switch;
- stopping early produces recoverable Future Work without manual documentation;
- four concurrent sessions remain isolated and directly replyable;
- the interface never confuses work completion with delivery state;
- normal sessions no longer wait on irrelevant MCP failures;
- permission and active tools are visible and truthful;
- context usage and subscription availability are not confused;
- resuming work does not require searching old chat history; and
- no ordinary workflow loses quality because a required tool was not loaded.

## 16. Implementation Approval Gate

This document does not approve coding. Before Slice 0 begins:

1. review this plan with Hafiz in plain language;
2. resolve any remaining product corrections;
3. create one parent GitHub issue plus narrowly scoped slice issues;
4. reconcile the Omnigent fork with current upstream in a clean worktree;
5. apply the AI implementation-readiness review to Slice 0 and Slice 1;
6. state the exact first-slice finish line and evidence; and
7. obtain explicit implementation approval.

Recommended first build boundary after approval:

```text
Implement Slice 0 and Slice 1 through a reviewed PR, then upgrade the isolated
personal pilot and let Hafiz test the durable Session Work Tree before building
the remaining controls.
```
