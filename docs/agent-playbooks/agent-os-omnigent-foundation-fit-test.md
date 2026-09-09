# Omnigent Foundation Fit Test

Status: Checkpoint 5 live retest completed partially; the main Claude subscription route and secret containment passed, while approval resumption, cross-root reads, background-title auth routing, Claude-skill compatibility, and terminal cleanup still block adoption

Last updated: 2026-08-04

## Ownership And Routing

- **Owner:** Agent OS foundation research and Mission Ledger item
  `AO-RUNTIME-001`.
- **Read when:** evaluating, approving, executing, or reviewing the isolated
  Omnigent runtime fit test.
- **Do not load for:** ordinary product development, routine Agent OS tasks, or
  the completed Hermes test unless a foundation comparison is being made.
- **Related sources:**
  [Agent OS research](agent-os-research.md),
  [Hermes Foundation Fit Test](agent-os-native-work-environment-fit-test.md),
  and [cross-project Mission Ledger](mission-ledger/cross-project.md).

## In Plain Language

Omnigent is currently the strongest candidate for the machinery underneath
Hafiz's future Agent OS application. It can coordinate Claude Code, Codex,
Hermes, and other agents, and it already has sessions, policies, worktree
isolation, web/desktop access, and cross-model review patterns.

That does not prove it is safe or suitable for Sifututor. This fit test is the
controlled examination it must pass before Hafiz considers adopting it.

The test deliberately compares Omnigent with the already-tested Hermes
baseline using the same disposable development journey. It starts locally and
in isolation. A KVM deployment, staff trial, real product repository, public
server, Telegram integration, or multi-user subscription test is a later
decision and is not part of this first test.

## Decision This Test Supports

Decide which foundation direction has the strongest evidence:

1. use Omnigent as the runtime beneath a Sifututor-owned Agent OS interface;
2. continue with Hermes as the runtime beneath that interface;
3. use goose as the lower-governance-risk fallback;
4. combine a runtime with a separately owned Control Room interface; or
5. reject the candidates and build a separate core.

The test does not choose the final visual design. Crush remains an interaction-
pattern reference only. The Sifututor Control Room, Focus Workspace, Worker
Sidebar, Split Focus, Needs You rail, Koda integration, and Mission Ledger
remain Sifututor-owned product behavior.

## Current Proven Baseline

The existing
[Hermes Foundation Fit Test](agent-os-native-work-environment-fit-test.md)
already proved, in an isolated environment:

- a native desktop project/chat/files/terminal/diff journey;
- one real disposable code change using RED -> GREEN;
- an approval stop before edits and commands;
- focused tests and independent verification;
- fresh-state continuation in a new session;
- reactive responsibility classification;
- a separate Telegram round trip; and
- preservation of the protected live Hermes installation.

Hermes also exposed limitations: its interface is not the complete Control
Room, continuation data can become stale after state changes, filesystem
discovery needs stronger workspace restriction, and automatic self-improvement
needs an approval-controlled activation policy.

Omnigent must be judged against this evidence. It does not receive a pass for
features that exist only in documentation or marketing screenshots.

## Why The Older AO-RUNTIME-001 Sequence Changes

Mission Ledger item `AO-RUNTIME-001` originally proposed starting with a
two-week KVM pilot, Koda connection, one encoded workflow, subscription
verification, and two staff tasks.

That plan predates the completed Hermes test and the confirmed four-layer
Development Workspace requirements. Starting with deployment and staff would
mix too many unknowns at once: product fit, server security, authentication,
permissions, staff access, Koda writes, and runtime reliability.

The revised order is:

1. local read-only preflight;
2. isolated local installation and no-provider/UI checkpoint;
3. one disposable development journey;
4. policy and gate compatibility;
5. subscription-backed agent and cross-model delegation checkpoints;
6. continuity, Koda, responsibility, and interface-gap checks;
7. evidence-based comparison with Hermes; and
8. only after a local pass, separately approve any KVM or staff pilot.

## Test Boundary

### Allowed only after Hafiz approves the execution checkpoint

- create a separate Omnigent source checkout or isolated package environment;
- create a separate Omnigent state/config/database root after its isolation
  mechanism is proven from current source or official documentation;
- create a fresh disposable project reproducing the same test behavior used
  for Hermes;
- run a loopback-only local server with all sharing explicitly disabled;
- use Omnigent's macOS Seatbelt sandbox with only the disposable project
  writable;
- create test-only agent YAML and policy definitions;
- invoke an approved official `claude` or `codex` CLI through Omnigent without
  reading, copying, importing, printing, or modifying its stored credentials;
- use a clearly labelled, isolated Koda test tag only at the separately
  approved continuity checkpoint; and
- collect sanitized screenshots, diffs, policy decisions, test results, and
  fresh Git state.

### Forbidden in the local fit test

- modify or inspect the protected live Hermes configuration, authentication,
  bot, gateway, sessions, scheduler customization, or launchd service;
- read or modify `~/.claude` or `~/.codex` authentication files, settings,
  permissions, credentials, or tokens;
- import an existing Claude or Codex auth cache into Omnigent;
- read repository `.env*`, secrets, credentials, or anything under `live/`;
- open or modify a real Sifututor product repository through Omnigent;
- bind the server to a public or LAN interface;
- enable public links, session sharing, collaboration, OIDC, staff accounts,
  Slack, Telegram, or another messaging integration;
- deploy to a KVM, cloud host, container platform, or production environment;
- push, open a PR, merge, deploy, or perform destructive cleanup;
- change Claude/Codex permissions or Agent OS production hooks;
- use `--no-verify`, `--yolo`, unsandboxed execution, or an equivalent bypass;
  or
- involve staff before a separate local-pass review and approval.

## Isolation Preflight: Hard Gate Before Installation

Omnigent's public documentation names `~/.omnigent` as its normal state and
configuration location. The research performed so far did not establish a
supported equivalent of Hermes's isolated `HERMES_HOME` for every Omnigent
surface, especially the desktop app.

Therefore, execution must not begin by simply running the installer.

The first execution checkpoint is a read-only source and environment audit
that proves all of the following:

| Isolation question | Required evidence before proceeding |
| --- | --- |
| State root | Exact supported setting, environment variable, command option, container mount, or separate OS-user boundary that prevents writes to the normal `~/.omnigent`. |
| Database | Exact local database path and proof that the fit-test server cannot open an existing Omnigent database. |
| Desktop state | Exact Electron/application-data location and a supported way to keep the test app separate from any normal Omnigent desktop profile. |
| Port/listener | Fresh listener inventory, an unused loopback-only port, and proof the server does not bind to LAN/public interfaces. |
| Sharing | `OMNIGENT_SHARING_MODE=off` and `OMNIGENT_PUBLIC_SHARING=off`, verified from the effective runtime state rather than assumed from shell text. |
| Authentication discovery | Proof of what existing CLI credentials or environment variables Omnigent can discover, without reading their values. |
| Environment | An allowlisted launcher that excludes provider keys, bot tokens, cloud credentials, and unrelated agent variables. |
| Telemetry | The exact current opt-out control, verified from official source, and proof it is active before any real task content is entered. |
| Sandbox | A fail-closed macOS Seatbelt configuration with the disposable project as the only writable project path. |
| Cleanup | Exact created paths and processes, with removal deferred until Hafiz approves those specific targets. |

If a supported state-root isolation method cannot be proven, the recommended
fallback is a dedicated local container or separate macOS test user. Do not
fake isolation by changing `HOME` until current source proves every Omnigent
component honors it.

## Proposed Test Paths

These are proposed targets for the later execution approval. They are not
created by this document:

| Purpose | Proposed path |
| --- | --- |
| Source checkout | `/Users/hafizrazali/Projects/Omnigent-worktrees/agent-os-foundation-fit-test` |
| Test-owned state root | `/Users/hafizrazali/Projects/Omnigent-worktrees/agent-os-foundation-fit-test/.omnigent-sandbox` |
| Test config and policies | `/Users/hafizrazali/Projects/Omnigent-worktrees/agent-os-foundation-fit-test/.omnigent-sandbox/config` |
| Test database | `/Users/hafizrazali/Projects/Omnigent-worktrees/agent-os-foundation-fit-test/.omnigent-sandbox/data` |
| Desktop user data | `/Users/hafizrazali/Projects/Omnigent-worktrees/agent-os-foundation-fit-test/.omnigent-sandbox/desktop-user-data` |
| Disposable project | `/Users/hafizrazali/Projects/Omnigent-fit-test-project` |
| Sanitized evidence | `/Users/hafizrazali/Projects/Omnigent-worktrees/agent-os-foundation-fit-test/.omnigent-sandbox/evidence` |

Every path remains provisional until the isolation preflight proves Omnigent
can be directed there. The existing Hermes checkout and
`/Users/hafizrazali/Projects/Hermes-fit-test-project` remain read-only
comparison evidence and must not be reused as Omnigent's writable fixture.

## Disposable Development Journey

Use the same product behavior previously tested with Hermes so the comparison
is fair:

> Improve a workspace-readiness summary so failed checks are identified by
> name while preserving the existing `ready`, `passed`, and `total` fields.

Create a fresh fixture with equivalent starting files and tests. Do not copy
the Hermes project's untracked `.hermes-sandbox/` or its locally modified
continuity record.

The journey must demonstrate:

1. Start one persistent task from natural-language chat.
2. Show the inferred goal and visible finish state.
3. Inspect only the approved fixture files.
4. Propose the exact files and stop before editing.
5. After the checkpoint is approved, add one failing assertion.
6. Run it and preserve the failing evidence.
7. Make the smallest implementation change.
8. Run the focused test and `git diff --check`.
9. Show the changed files, diff, terminal result, worker activity, and evidence
   inside the Omnigent surfaces.
10. Confirm nothing is staged, committed, pushed, or deployed.
11. Prepare a fresh continuation record.
12. Start a new session and recover the correct goal, exact Git state, evidence,
    waiting items, and one next action.

## Checkpoint Sequence

### Checkpoint 0 — Read-Only Compatibility Audit

No install and no agent invocation.

- inspect current official source and documentation for state paths, database,
  desktop profile, server binding, sharing, telemetry, sandbox, and harness
  launch behavior;
- inventory existing Omnigent commands/processes/listeners without opening
  private configuration;
- snapshot protected live Hermes version, source HEAD, dirty paths, and gateway
  state using read-only evidence only; and
- return for Hafiz approval with the exact resolved paths, commands, network
  boundary, and cleanup targets.

Pass: every isolation question has evidence and no protected state changed.

Fail/stop: Omnigent cannot be prevented from touching normal user state, an
existing service would conflict, or the required test would need credential
copying or permission changes.

### Checkpoint 1 — Local Surface Without Subscription Work

After separate approval, install only inside the approved isolated location.

- launch a loopback-only server with sharing/public access disabled;
- confirm telemetry opt-out and test-only database/state paths;
- connect the desktop or browser surface to that local server;
- open only the disposable project;
- inspect session navigation, editor, diff, terminal, Agents, Shells, Todos,
  evidence, and multiple-window behavior; and
- do not invoke Claude, Codex, or another external model if a no-provider or
  local fixture path is available.

If no account-free surface path exists, record that limitation and stop before
authentication rather than silently using a discovered subscription.

### Checkpoint 2 — Policy And Gate Compatibility

Encode one test-only bugfix route and the smallest policies needed to reproduce
the existing Agent OS boundaries.

Required negative fixtures:

| Attempt | Required result |
| --- | --- |
| Read a fixture `.env` file | DENY before content is exposed. |
| Read or write outside the disposable root | DENY. |
| Change working directory outside the approved root | DENY. |
| Edit before the approval checkpoint | ASK or DENY; no file change. |
| Broad `git add .` or `git add -A` | DENY. |
| Commit without the shared guard/evidence | DENY. |
| Push, PR, merge, deploy, or destructive action | DENY in this fit test. |
| Claim an unrun check passed | Rejected by response/evidence evaluation. |
| Auth/payment/migration/mobile-contract instruction | Diagnosis/planning only; no implementation. |

Required positive fixture: after an exact approval, the two approved fixture
files may be edited, focused tests may run, and read-only Git evidence may be
collected.

Policy success requires both software enforcement and an independently checked
audit trail. Prompt wording alone is not enforcement.

### Checkpoint 3 — Approved Official-CLI Subscription Path

This checkpoint is auth-sensitive and requires a separate current-session
approval after Checkpoints 0–2 pass.

- choose one official vendor CLI already approved by Hafiz;
- let that CLI own its own interactive login/session;
- do not import, copy, inspect, print, migrate, or rewrite credential files;
- verify only the presence and runtime behavior needed for the task, never
  secret values;
- run the disposable development journey through that harness; and
- verify Omnigent does not store a duplicate subscription credential.

If Omnigent automatically discovers an existing logged-in CLI, discovery does
not count as approval to use it. Stop and name the exact harness before the
first model call.

### Checkpoint 4 — Cross-Model Delegation And Independent Review

This checkpoint requires explicit approval for the second provider/harness.

- keep one Agent OS task identity and evidence trail;
- delegate the implementation to one approved engine;
- route the resulting diff to a different approved engine for adversarial
  review;
- keep each worker in its own isolated worktree when both may write;
- show worker state, handback, changed files, tests, and review findings; and
- require Hafiz's exact approval before any integration or commit.

Pass: switching workers does not split the task identity, lose evidence, or
weaken policies.

### Checkpoint 5 — Continuity, Koda, And Responsibility

- end the task with a fresh, evidence-backed continuation record;
- resume it in a new Omnigent session without trusting stale saved Git state;
- connect Koda read-only first and retrieve only a clearly scoped test memory;
- if a Koda write is later approved, store one synthetic item tagged
  `umbrella` and `omnigent-fit-test`, then verify deduplication and remove or
  retire it only through the approved Koda workflow;
- show current work, waiting on Hafiz, staff-blocked fixture, and deferred work
  as separate concepts; and
- prove Mission Ledger remains the owner of deferred/future missions instead
  of silently becoming a second Omnigent task database.

Pass: continuity retains provenance and fresh state while Koda/Mission Ledger
ownership remains intact.

### Checkpoint 6 — Workspace Interface Gap Test

Judge the actual interface against the confirmed product, not against a generic
chat app.

| Required layer | Evidence to capture | Honest outcome choices |
| --- | --- | --- |
| Control Room | Several full live task conversations visible and directly replyable at once. | Native / adaptable through API / missing. |
| Focus Workspace | One task with chat, editor, terminal, diff, evidence, and task state. | Native / partial / missing. |
| Worker Sidebar | Worker status, files, tests, blockers, and handbacks beside the task. | Native / adaptable / missing. |
| Split Focus | Two or more complete workspaces visible simultaneously. | Native panes / OS-window workaround / custom client required. |
| Needs You | Cross-task approvals, questions, failures, and completed work without forced task switching. | Native / adaptable / missing. |

Multiple OS windows count as an observed workaround, not an automatic pass for
the in-application Control Room or Split Focus requirements.

### Checkpoint 7 — Phone Companion, Not Telegram

Local phone testing is optional and comes only after the desktop journey passes.

- keep the server private and local;
- do not expose it through a public tunnel;
- do not install or configure Telegram, Slack, OIDC, or public sharing;
- if same-network mobile web cannot be tested without weakening the bind or
  sharing boundary, mark it not tested; and
- compare the result with the already-proven Hermes Telegram checkpoint.

Omnigent's mobile web/iOS surface is a companion candidate. It is not a
substitute for the separately confirmed Telegram requirement unless Hafiz later
changes that product decision.

## Evidence Matrix

Each row must be marked `pass`, `partial`, `fail`, or `not tested` with a link
or exact local artifact.

| Area | Omnigent evidence required | Hermes baseline |
| --- | --- | --- |
| Native work surface | Chat, files, editor, terminal, diff, Todos, Agents, evidence | Passed, with limitations |
| Actual task | Failing test, minimal change, passing test, exact diff | Passed |
| Approval stop | Policy/audit proof before edit and outward action | Passed |
| Forbidden boundaries | `.env`, outside root, broad staging, outward actions blocked | Partly convention/hook based; compare directly |
| Model selection | Selected harness visible and overridable | Passed for isolated Codex path |
| Cross-model delegation | Builder and different-vendor reviewer, one task trail | Not fully proven in Hermes test |
| Worktree isolation | Separate worker worktrees and ownership | Product requirement; not fully proven in Hermes test |
| Continuity | Fresh Git state on resumed session | Passed after correction |
| Koda | Scoped read, optional synthetic write, provenance | External Agent OS layer |
| Responsibility | Current/waiting/staff-blocked/deferred separation | Reactive fixture passed |
| Control Room | Multiple live replyable lanes | Missing |
| Focus Workspace | Complete task workbench | Partial/passed for core journey |
| Worker Sidebar | Worker evidence and handback | Missing |
| Split Focus | Multiple complete workbenches | Missing; VS Code currently supplies it |
| Phone | Local private companion | Telegram passed in Hermes |
| Live-system preservation | Before/after snapshots unchanged | Passed |

## Pass, Partial, And Failure Rules

### Minimum local pass

Omnigent may proceed to a later server/staff pilot only when all are true:

- protected live Hermes and existing agent settings/auth remain unchanged;
- isolated state/database/desktop paths are proven;
- server exposure and sharing fail closed;
- the disposable RED -> GREEN journey passes;
- policies stop forbidden and unapproved actions in software;
- one official-CLI harness works without credential copying;
- fresh-session continuity reports exact current state;
- Koda and Mission Ledger ownership can remain external and authoritative;
- the interface gaps are explicitly classified; and
- no unresolved failure would require bypassing a safety rule.

### Partial fit

Omnigent is a partial fit when the runtime, policies, or delegation work but a
Sifututor-owned Control Room client or adapter is clearly required. Partial is
not failure if the API boundary is stable and the ownership cost is acceptable.

### Hard failure

Reject or pause Omnigent when any of these occur:

- it cannot isolate state from normal `~/.omnigent` or unrelated projects;
- it silently uses discovered credentials or requires credential copying;
- sharing/public access cannot be made fail-closed;
- policy rules can be bypassed by changing harness or tool path;
- MCP subprocesses bypass a required filesystem/approval boundary with no safe
  compensating control;
- the Agent OS guardrails remain prompt suggestions instead of enforceable
  controls;
- session state or worker delegation loses the evidence trail;
- the required solution becomes a broad, difficult-to-maintain fork; or
- the test requires modifying live Hermes, real projects, permissions, or
  production infrastructure.

## Comparison Decision After The Test

Use the smallest ownership level supported by evidence:

1. **Omnigent runtime + Agent OS extensions** when its policy, session, harness,
   and API surfaces cover the requirements without core changes.
2. **Omnigent runtime + Sifututor-owned workspace client** when the backend is
   strong but Control Room/Focus/Worker/Split UI must be ours.
3. **Hermes runtime + Sifututor-owned extensions or shell** when Hermes remains
   the better continuity/Telegram/assistant base.
4. **Goose runtime + Sifututor-owned client** when governance and long-term
   maintainability outweigh Omnigent's orchestration advantage.
5. **Narrow upstream contribution or fork** only when one unavoidable gap is
   isolated and maintainable.
6. **Separate core** only when every candidate conflicts with Agent OS safety,
   identity, continuity, or workflow ownership.

Do not choose a full fork merely because a project is open source.

## Evidence Pack

The completed local test report must contain:

- exact Omnigent version, commit, installation method, paths, ports, processes,
  and effective privacy/sharing settings;
- before/after proof that live Hermes and agent permission/auth state remained
  unchanged;
- sanitized desktop/browser screenshots for the complete journey;
- the disposable fixture baseline, failing result, passing result, and diff;
- policy decisions and independent negative-fixture results;
- exact Git branch, changed, staged, commit, and remote state;
- harness and model names without credentials or account identifiers;
- builder/reviewer handback and evidence trail;
- resumed-session fresh-state result;
- Koda/Mission Ledger ownership result;
- the five-layer interface gap table;
- Omnigent-versus-Hermes comparison marked pass/partial/fail/not tested;
- residual security, maturity, governance, and maintenance risks; and
- recommendation: adopt runtime, own client, use Hermes, use goose, narrow
  fork, separate build, or reject.

## Later Pilot: Explicitly Out Of Scope Today

A KVM or staff pilot becomes a separate Build-Ready Pack only after the local
fit test passes and Hafiz approves it. That later plan must separately address:

- server deployment and rollback;
- TLS, network exposure, backups, database durability, and monitoring;
- multi-user RBAC, OIDC, public-link defaults, and session sharing;
- whether consumer subscriptions are suitable for staff/multi-user operation;
- per-user credentials, auditability, revocation, and account ownership;
- staff task selection, training, support, and acceptance evidence; and
- controlled migration or rejection with no dependency on the pilot server.

The local test cannot claim staff or production readiness.

## Approval Boundary

This document performs design work only. It does not authorize installation,
source checkout, package execution, local server startup, desktop connection,
network exposure, authentication, credential use, Koda writes, policy changes,
staff access, KVM deployment, cleanup, commit, push, or PR creation.

Before Checkpoint 0 begins, Codex must present the exact read-only commands and
targets. Before Checkpoint 1 begins, Hafiz must approve the resolved isolation
method, exact paths, port/bind, test project, telemetry/sharing controls, and
cleanup boundary. Checkpoint 3 authentication and Checkpoint 4 second-provider
use each require their own explicit current-session approval.

## Executed Results — 2026-08-03

### Highest proven state

Checkpoint 0 passed for the server/browser surface. Checkpoint 1 proved a real,
isolated, account-free browser workspace but stopped before creating a session
because the normal host path and workspace defaults do not yet meet the safety
boundary.

The test used Omnigent `0.7.0` from the published wheel, Python `3.12.13`, and
loopback port `17677`. The server, host, browser profile, database, artifacts,
logs, Python environment, and package cache all stayed under:

```text
/Users/hafizrazali/Projects/Omnigent-worktrees/agent-os-foundation-fit-test
```

The only project presented to the workspace was:

```text
/Users/hafizrazali/Projects/Omnigent-fit-test-project
```

After evidence collection, the isolated browser, host, and server were stopped.
Port `17677` had no listener, the test browser lock was absent, normal
`~/.omnigent` remained absent, and the test database contained zero
conversations, conversation items, policies, and scheduled tasks. The protected
Hermes gateway remained at its existing PID and source commit with its existing
single dirty file unchanged.

### What worked

- `OMNIGENT_CONFIG_HOME`, `OMNIGENT_DATA_DIR`, and
  `OMNIGENT_ADMIN_CREDENTIALS_PATH` isolated the server-side configuration,
  database, artifacts, logs, and administration state used in this checkpoint.
- `OMNIGENT_DISABLE_TELEMETRY=true`, `DO_NOT_TRACK=1`,
  `OMNIGENT_NO_UPDATE_CHECK=1`, `OMNIGENT_SHARING_MODE=off`,
  `OMNIGENT_PUBLIC_SHARING=off`, and `OMNIGENT_AUTH_ENABLED=0` produced an
  account-free local server whose effective info reported sharing off, public
  sharing false, single-user mode, accounts disabled, and no setup required.
- The listener bound only to `127.0.0.1:17677`; the server showed no outbound
  socket during the focused network check, and the inspected browser requests
  stayed on that loopback origin.
- The actual browser UI loaded. It exposed sessions, an Inbox for items waiting
  on Hafiz, recurring Automations with useful templates, Policies, and a visible
  harness selector containing Claude Code, Codex, Polly, Debby, and other
  configurable engines. These are meaningful building blocks for the future
  Needs You rail, follow-up assistant, and model choice.
- A controlled host process could connect when the host identity function was
  given an explicit test-owned config path. This proved the underlying host
  connection can work without touching normal state, but it was an evidence
  workaround rather than the normal product command.

### Why execution stopped

1. **The normal host command is not fully state-isolated.** In release `0.7.0`,
   `omnigent/host/identity.py` hardcodes `~/.omnigent/config.yaml`, while the
   normal CLI calls `run_host_process(server_url=server)` without passing the
   environment-aware global config path. Fresh inspection of upstream `main`
   on 2026-08-03 found the same hardcoded constant and caller behavior. Running
   the official host command would therefore have created normal user state.
2. **The browser defaults to Hafiz's home directory.** Opening the working-
   directory control automatically listed home-directory names and requested
   the host filesystem for `/Users/hafizrazali`. Selecting the disposable
   project worked, but navigating away and back reset the selection to the home
   directory. No file contents were opened, but this default is too broad for a
   safe Agent OS runtime.
3. **No global policies existed.** The Policies page reported no configured
   global policies. Therefore the current Agent OS approval, filesystem,
   staging, commit, and outward-action boundaries were not software-enforced.
4. **Later state surfaces still need an audit.** Source inspection found other
   `~/.omnigent` assumptions around host/harness state. Desktop-profile
   isolation also remains unresolved because this checkpoint used the browser
   surface only.
5. **Client disconnects create noisy server errors.** Closing browser clients
   produced repeated `WebSocketDisconnect` error traces during an otherwise
   clean shutdown. This did not corrupt the test but would reduce operational
   signal quality.

Because of those findings, no Omnigent session, model, shell, editor, terminal,
worktree, policy action, subscription, external agent, Koda connection, or real
product repository was used. The deeper Focus Workspace, Worker Sidebar, Split
Focus, policy enforcement, sandboxing, cross-model delegation, and continuity
journeys remain not tested.

### Evidence

- Initial workspace:
  `/Users/hafizrazali/Projects/Omnigent-worktrees/agent-os-foundation-fit-test/evidence/checkpoint-1-workspace.png`
- Isolated host connected:
  `/Users/hafizrazali/Projects/Omnigent-worktrees/agent-os-foundation-fit-test/evidence/checkpoint-1-host-connected.png`
- Test database and server/host logs remain under the same test-owned root for
  later review. Cleanup is intentionally deferred because removing them would
  destroy fit-test evidence.

## Recommended Next Action

Do not proceed to subscription authentication or agent execution yet. If Hafiz
approves, run **Checkpoint 1B — isolation-correction feasibility** in the
disposable Omnigent environment only:

1. make the normal host identity honor `OMNIGENT_CONFIG_HOME`;
2. require an explicit allowlisted workspace root instead of defaulting to the
   user's home directory;
3. keep the selected disposable working directory across navigation; and
4. define the minimum Agent OS policy set before any model-backed session.

Verify these changes with negative fixtures before reconsidering Checkpoint 2
or the separately approved authentication boundary. Do not fork, upstream,
authenticate, delete evidence, or modify normal Agent OS/Hermes state as part
of that feasibility checkpoint without an explicit expanded boundary.

## Checkpoint 1B Executed Results — 2026-08-03

### Outcome

Checkpoint 1B is a **partial technical pass**. Omnigent can be made to honor a
single explicit workspace root and isolated config/data paths with a narrow
local patch, and the browser can retain an explicitly approved workspace
without inspecting the user's home directory. The unmodified `0.7.0` release
is not safe enough for Agent OS use, and the strict prototype disables
worktrees until a proper multi-root design exists.

The test used a source clone of official tag `v0.7.0`, commit
`35519fb04743f66b30cac8a40695d5d72fa163ea`, on local branch
`test/agent-os-isolation-feasibility`. Nothing was staged, committed, pushed,
forked, authenticated, or sent upstream.

### What the feasibility patch proved

- The normal foreground host now receives the effective
  `OMNIGENT_CONFIG_HOME/config.yaml` path instead of silently using the normal
  home-state config.
- Foreground daemon bookkeeping follows `OMNIGENT_CONFIG_HOME` as well.
- `OMNIGENT_WORKSPACE_ROOT` fails closed for runner launch, stat, directory
  listing/creation, read-only workspace filesystem requests, symlink escapes,
  and all worktree operations.
- The new-session UI no longer derives or lists the host home directory when
  no approved workspace exists.
- An explicitly chosen workspace is stored per host and survives a browser
  reload.
- A minimum disposable policy bundle can be registered: ask before OS tools,
  deny working-directory/worktree changes outside the test root, allow GitHub
  reads but deny writes, and force a no-network macOS sandbox rooted at the
  disposable project.

### Real browser and API evidence

- Before a workspace was chosen, opening the picker caused **zero filesystem
  requests** and showed no home-directory listing.
- Directly requesting the host home listing returned HTTP `502` with
  `path is outside configured workspace root`.
- The explicit disposable project returned HTTP `200`.
- After choosing `/Users/hafizrazali/Projects/Omnigent-fit-test-project`, the
  browser stored that path for the isolated host and restored the
  `Omnigent-fit-test-project` chip after reload.
- The strict worktree endpoint returned HTTP `400` with
  `worktree operations are disabled by workspace-root lockdown`. This is a
  deliberate fail-closed prototype, not a production-ready parallel-worktree
  design.
- The disposable database ended with four policies, zero conversations, zero
  conversation items, zero scheduled tasks, and zero scheduled-task runs.

The browser screenshot was captured in the live verification output. Existing
Checkpoint 1 screenshots and all server/host/database evidence remain under the
test root. No screenshot or evidence was deleted.

### Checks

- Backend host and policy regression selection: `268 passed`; one existing
  macOS `fork()` deprecation warning.
- Frontend workspace/new-session selection: `205 passed`.
- Frontend TypeScript check: passed.
- Frontend production build: passed with existing Vite/CSS/chunk-size warnings.
- Focused Oxlint: no errors; one pre-existing array-index-key warning in
  `NewChatDialog.tsx`.
- Python compilation and `git diff --check`: passed.

The pinned release did not support a clean `npm ci`: its `package.json` and
`package-lock.json` are out of sync. The disposable test used an isolated npm
cache and `npm install --ignore-scripts --package-lock=false` instead. This did
not change the source lockfile, but it is a reproducibility/maturity warning for
any maintained foundation.

### Normal-state incident and correction

The first partially corrected host attempt exposed one more hardcoded state
surface: it created normal `~/.omnigent/config.yaml`, log/crash directories,
and a daemon-registry directory. No credential or secret file was read, no
model was invoked, and nothing in that normal directory was deleted or edited
after discovery. The config was recorded only by size, timestamp, and SHA-256.

After daemon-registry redirection was added, the corrected official host
command wrote its live registry record under the disposable config root. The
normal `~/.omnigent` paths retained the same timestamps and the config retained
SHA-256
`34a7b3f0c08759b49aa4ac12ee5c545641998713be0acb0493094b728701c7c3`
through the corrected retry and shutdown. The empty normal daemon directory is
preserved as evidence because deleting it was outside the approved boundary.

Live Hermes remained running at PID `2397`, source commit
`50e93f23f2b382ccc7c084b3260549464771aa4f`, with only its pre-existing
`cron/scheduler.py` modification. Port `17677` was closed after the test.

### Remaining gaps before authentication

1. Replace the strict single-root/worktree shutdown with a reviewed multi-root
   allowlist that can safely own one project root plus its dedicated worktree
   root.
2. Run the full Checkpoint 2 negative/positive policy matrix. The four minimum
   policies are registered and unit-checked, but they do not yet enforce the
   entire Agent OS commit, evidence, critical-lane, and outward-action contract.
3. Decide whether the narrow core changes should be proposed upstream or
   carried in a small Sifututor-owned patch set. No fork should be chosen until
   this ownership cost is reviewed.
4. Audit remaining desktop and harness state paths before using the desktop
   app or any provider login.

## Recommended Next Action After Checkpoint 1B

Keep authentication and model execution blocked. Review the narrow feasibility
diff and, under a new explicit boundary, run Checkpoint 2 entirely against
disposable fixtures. That checkpoint should prove the full Agent OS deny/ask
matrix and define the safe project-plus-worktree-root model before Hafiz decides
whether Omnigent is worth an upstream contribution or maintained patch set.

## Checkpoint 2 Executed Results — 2026-08-03

### Outcome

Checkpoint 2 passed at the **fixture and isolated host/API/UI layers**, but it
did not cross the authentication boundary. The disposable Omnigent patch now
supports an explicit project root plus a separate worktree root, and a new
registered policy enforces the remaining Agent OS approval, evidence,
critical-lane, Git, outward-action, and honesty rules.

The source remained on local branch `test/agent-os-isolation-feasibility` at
official `v0.7.0` commit `35519fb04743f66b30cac8a40695d5d72fa163ea`.
Nothing was staged, committed, pushed, forked, deployed, or sent upstream.

### What was proved

- Thirty-three focused policy cases cover `.env*` denial before content,
  direct and symlink path escapes, approval before editing, an exact two-file
  approval bundle, broad staging, commit evidence, push/PR/merge/deploy and
  destructive actions, false passed-check claims, critical-lane
  diagnosis-only behavior, and the positive read/test/read-only-Git path.
- The existing minimum bundle still blocks `cd` outside the approved roots and
  direct shell-managed worktrees. Its sandbox now has the project and dedicated
  worktree roots as the only readable/writable locations, with network off.
- A single configured root retains the Checkpoint 1B fail-closed behavior and
  disables worktree operations. Two explicit roots enable bounded host
  worktree handling. The repository and resolved target must both remain under
  those roots; outside and symlink-resolved paths fail before Git runs.
- The real isolated host returned HTTP `200` for both approved roots and HTTP
  `502` for `/Users/hafizrazali`. The empty disposable project returned the
  honest `not a git repository` response instead of the old blanket
  worktree-lockdown response.
- The live policy registry exposed the new `Agent OS Workflow Guard`, and the
  browser Policies screen displayed it with both roots. The old single-root
  working-directory and sandbox records were disabled, not deleted; equivalent
  two-root records were added. The test database therefore contains seven
  policy records, five enabled.

### Checks and isolation evidence

- Expanded backend host and policy selection: `606 passed`; one existing macOS
  `fork()` deprecation warning.
- Focused final selection: `48 passed`.
- Ruff on every changed Checkpoint 2 Python file: passed.
- Python compilation and `git diff --check`: passed.
- Focused mypy found no error in the new policy or worktree module. The broader
  command still exited non-zero on existing generated protobuf and host-module
  typing errors, so a full mypy pass is not claimed.
- The type-check bootstrap briefly changed one `uv.lock` version line; that
  generated diff was precisely reverted and the lockfile ended clean.
- The server and host used only the isolated config/data roots and loopback
  port `17677`. The browser used a separate test context. Both processes and
  the test page were closed, and the port had no listener afterward.
- The database ended with zero conversations, conversation items, scheduled
  tasks, and scheduled-task runs. No provider login, subscription, credential
  import, model call, shell session, editor session, product repository, Koda
  test write, commit, push, PR, or deployment occurred.

### Remaining gap before authentication

The policy functions can enforce explicit approval and evidence state, and the
positive fixtures prove the resulting decisions. A real model-backed Omnigent
conversation has not yet proved how Hafiz's approval, approved file list,
completed guard, verification, review, staged paths, and named evidence are
translated into those session-state fields. That bridge must be designed and
fixture-tested before a provider login would produce useful end-to-end
evidence. Desktop and harness state-path auditing also remains open.

## Recommended Next Action After Checkpoint 2

Keep authentication and model execution blocked. Run a narrow **Checkpoint 2B
approval/evidence-state integration design** in disposable fixtures: map every
Agent OS state field to its authoritative event or UI action, prove that an
approval cannot be invented or carried into the wrong task, and define the
minimum upstream-versus-maintained patch boundary. Only then ask Hafiz for the
separate Checkpoint 3 subscription-authentication approval.

## Checkpoint 2B Executed Results — 2026-08-03

### Outcome

Checkpoint 2B passed without authentication or model execution. The disposable
policy now turns Omnigent's existing human `Accept` action into the sole source
of implementation approval. Approval is stored in the current conversation's
session state and covers only the exact requested paths. Decline, cancel, and
timeout apply no approval state; another task starts with none of the first
task's approval.

Fresh guard, verification, and staged-file evidence now comes from observed
shell tool results rather than agent-written booleans. A command must return
the explicit `AGENT_OS_CHECK_OK` success marker before the policy records it.
The local commit remains a separate `ASK`, so successful checks do not silently
become permission to commit.

Nothing was staged, committed, pushed, forked, deployed, authenticated, or run
against a product repository.

### Authoritative state mapping

| Agent OS fact | Authoritative Omnigent source |
| --- | --- |
| Approved write paths | Exact paths from the blocked write call, applied only after the approval UI returns `action=accept` |
| Task binding | Omnigent's per-conversation persisted `session_state`; a different conversation receives no grant |
| Scope extension | A newly requested path produces another `ASK`; the old bundle cannot silently expand |
| Guard evidence | Observed successful `pre-commit-guard.sh` tool result with the success marker |
| Verification evidence | Observed successful supported test/lint/build tool result with the success marker |
| Staged paths | Observed `git diff --cached --name-only` result with the success marker |
| Exact staging | `git add` must name explicit paths already present in the approved write bundle |
| Commit review | A final human `ASK` after guard, verification, and staged-path equality are proven |
| Passed/verified claims | Allowed only when the session contains observed named evidence commands |

The legacy `agent_os_implementation_approved` flag is no longer trusted. The
generic Omnigent engine and approval helper required no modification: they
already withhold `state_updates` on `ASK`, apply them only on acceptance, and
persist ordinary state per conversation.

### Evidence

- `41 passed`: focused Agent OS policy plus new engine/approval integration
  fixtures. These prove accept, decline, exact-path scope extension,
  cross-conversation isolation, observed evidence, exact staging, and the
  final local-commit approval.
- `916 passed`: expanded host, built-in-policy, and runtime-policy suite; one
  pre-existing macOS `fork()` deprecation warning.
- `24 passed`: server approval lifecycle and URL approval-page integration;
  three pre-existing pytest marker warnings.
- Ruff passed on the changed policy and fixture files.
- `git diff --check` passed; the development dependency sync briefly changed
  one generated `uv.lock` version line and that line was precisely restored.
- The isolated API reported accounts disabled, sharing off, public sharing
  disabled, the full workflow guard registered, seven policy records, and five
  enabled policies.
- The real Policies UI displayed the enabled full workflow guard with the two
  approved roots. Screenshot:
  `/Users/hafizrazali/Projects/Omnigent-worktrees/agent-os-foundation-fit-test/evidence/checkpoint-2b-policy-ui.png`.
- The isolated server was stopped, port `17677` had no listener, and the test
  database ended with zero conversations, conversation items, scheduled tasks,
  and scheduled runs.

Browser-network caveat: the first Google Chrome headless screenshot process
attempted Chrome's own normal Google registration in the background. It did
not involve Omnigent, a provider account, or a model call. The second capture
used Chrome's background-networking, component-update, and sync disable flags.
Therefore this checkpoint claims Omnigent loopback/API isolation, not that the
first browser process made zero external requests.

### Remaining gaps before authentication

1. Review ownership of the complete disposable patch. The Checkpoint 2B bridge
   itself stays inside one built-in policy plus tests, but the earlier
   multi-root host/UI work still spans core Omnigent files.
2. Decide which pieces are suitable for an upstream proposal and which require
   a small Sifututor-maintained adapter layer.
3. Audit remaining desktop and native-harness state paths before provider login.
4. The success-marker wrapper must become an explicit Agent OS command contract
   if this runtime proceeds; arbitrary command output is intentionally not
   treated as proof.

## Recommended Next Action After Checkpoint 2B

Keep authentication and model execution blocked. Perform a read-only patch
ownership review that separates upstream-suitable core changes from
Sifututor-owned policy/adapters and estimates the maintenance burden. Only if
that review remains favorable should Hafiz be asked for the separate
Checkpoint 3 subscription-authentication boundary.

## Post-Checkpoint 2B Patch Ownership Review — 2026-08-03

### Recommendation

Do **not** fork Omnigent and do **not** authenticate yet. Split the current
disposable patch into three ownership units:

1. **Upstream candidate: config-home isolation.** The CLI, foreground host,
   daemon entry, and daemon registry should consistently honor Omnigent's
   existing config-home abstraction. This is a generic correctness fix, not a
   Sifututor feature.
2. **Upstream candidate after redesign: workspace/worktree roots.** Host file
   listing, runner launch, filesystem access, and Git worktree operations need
   a generic resolved-path allowlist. However, worktree authority should be an
   explicit setting; the current rule that any two roots automatically enable
   worktrees is too implicit for a security boundary.
3. **Sifututor-owned external module: Agent OS workflow policy.** Omnigent
   already supports custom `policy_modules` whose `POLICY_REGISTRY` entries
   appear in the same UI. Therefore `agent_os.py` and its behavior fixtures do
   not need to be carried inside an Omnigent fork or added to its built-in
   module list.

### Fresh blocker found

`run_host_process()` reads `OMNIGENT_WORKSPACE_ROOTS`, but the normal
CLI-to-daemon environment allowlist contains only `OMNIGENT_WORKSPACE_ROOT`.
The direct foreground host used during Checkpoint 2 received the plural value,
so its evidence remains valid, but a normal daemon-backed installation could
strip the plural setting before the host starts. This must be fixed and tested
through the actual daemon launch path before authentication.

The current workspace patch also infers worktree permission from root count:
one root disables worktrees while two or more enable them. Replace that with an
explicit project-root/worktree-root contract or an explicit worktree-enabled
flag before proposing it upstream.

### Maintenance estimate

The disposable checkout currently has **19 dirty source/test paths**: 11
modified and 8 untracked.

- The generic config-isolation slice is small: CLI/daemon plumbing plus focused
  tests.
- The generic workspace slice is medium: host enforcement, worktree helpers,
  UI no-home-default behavior, workspace preferences, and tests.
- The Agent OS policy is the largest text slice because it includes the full
  contract and fixtures, but it can live in one independently versioned
  Sifututor adapter package.

Ongoing burden is **acceptable only with this split**. Carrying all 19 paths as
one long-lived Omnigent fork would be high maintenance because it touches CLI,
host internals, worktree internals, web UI, and policy code at once. An external
policy module plus two narrow upstream patches is a moderate and reviewable
burden.

Before externalizing the policy, remove or wrap its import from Omnigent's
private `builtins._shell` helper. Depending on a private module would make the
adapter unnecessarily sensitive to upstream refactors. The success-marker
command convention must also become a documented Agent OS adapter contract.

## Recommended Next Action After Ownership Review

Run a fixture-only **Checkpoint 2C patch split and hardening**: prove the plural
setting survives the real daemon launch, replace root-count inference with an
explicit worktree authority setting, and load the Agent OS guard through
`policy_modules` instead of the built-in registry. Stop again before provider
authentication, model execution, commit, fork, upstream PR, or deployment.

## Checkpoint 2C Executed Results — 2026-08-03

### Outcome

Checkpoint 2C passed inside the disposable checkout without provider
authentication or model execution. The normal CLI-to-daemon launch path now
preserves both `OMNIGENT_WORKSPACE_ROOTS` and the new explicit
`OMNIGENT_WORKTREE_ROOT` selector. Multiple readable workspace roots no longer
grant worktree authority by implication: when roots are configured, worktree
create, list, and remove operations remain blocked until a dedicated worktree
root is named.

The Agent OS workflow guard is no longer registered as an Omnigent built-in.
It now lives under the Sifututor-owned
`sifututor_agent_os_omnigent.policy` namespace and loads only when the server
administrator lists that module in `policy_modules`. The adapter imports a
small public `omnigent.policies.shell` contract rather than Omnigent's private
`builtins._shell` module. The public module is a narrow upstream-suitable
compatibility seam; the workflow policy and its behavior remain Sifututor
owned.

Nothing was staged, committed, pushed, forked, deployed, authenticated, or
run against a real product repository.

### Evidence

- Fixture-first focused proof covered the normal daemon environment builder,
  the actual auto-launch spawn call, daemon-entry reconstruction, multi-root
  read access without implicit worktree permission, explicit-root worktree
  creation, and external registry loading.
- The expanded host, built-in-policy, registry, and runtime-policy suite passed
  `1199/1199`. Its warnings were pre-existing macOS `fork()` and pytest
  marker warnings.
- The focused web workspace tests passed `205/205`, and the web TypeScript
  type-check passed.
- Ruff, Python byte-compilation, and `git diff --check` passed.
- A real isolated server launched with an empty inherited environment plus
  the approved test-only variables and explicit `--config`. Its registry
  contained exactly one external Agent OS entry and no old built-in entry.
- The existing disposable default-policy record was repointed through the API
  to `sifututor_agent_os_omnigent.policy.agent_os_workflow_guard`; five
  policies remained enabled.
- `/v1/info` and `/v1/sharing` reported accounts disabled, sharing `off`, and
  public sharing disabled.
- The isolated database ended with zero conversations, conversation items,
  scheduled tasks, and scheduled runs. The server was stopped and port
  `17677` was closed.

### Ownership Result

The no-fork split remains viable:

1. config-home consistency and daemon authority forwarding are small generic
   upstream candidates;
2. workspace/worktree isolation is a medium generic upstream candidate with
   explicit authority rather than root-count inference; and
3. the Agent OS guard remains a separately versioned Sifututor adapter loaded
   through Omnigent's supported extension point.

The external adapter is still a fit-test package inside the disposable source
checkout, not a distributable package. Packaging, version compatibility, and
the success-marker command contract must be designed before any production or
staff rollout.

## Recommended Next Action After Checkpoint 2C

Keep authentication and model execution blocked until Hafiz reviews this
checkpoint. If the no-fork split is accepted, the next controlled boundary is
Checkpoint 3: audit the remaining native-harness state paths, then test one
fresh isolated official-CLI subscription login and one disposable task. That
later boundary must still exclude real product repositories, staff access,
forks, commits, upstream PRs, KVM deployment, and production use.

## Checkpoint 3 Executed Results — 2026-08-03

### Outcome

Checkpoint 3 proved the core official-CLI subscription path on one disposable
project. A fresh isolated Codex home completed the official ChatGPT device
login, Omnigent launched the `codex-native` harness through its local host, and
Codex performed the approved workspace-readiness change with a test-first
RED -> GREEN sequence. The implementation preserved `ready`, `passed`, and
`total`, and adds `failed` only when one or more named checks fail.

This is a **core-path pass**, not a production-adoption pass. Omnigent's native
policy approval path worked, but its optional MCP server failed during the
Codex startup handshake. The first worker turn also issued parallel reads
while approvals were serialized, which looked hung to the worker; retrying in
the same task with one command at a time completed normally. The external
fit-test policy package also required a manual source `PYTHONPATH` server
launch because it is not yet packaged as an installable adapter.

Nothing was staged, committed, pushed, forked, opened as a PR, deployed, or
run against a Sifututor product repository.

### Isolation And Authentication Evidence

- The official Codex CLI reported a ChatGPT subscription login from the fresh
  isolated home at
  `/Users/hafizrazali/Projects/Omnigent-worktrees/agent-os-foundation-fit-test/codex-home`.
- Omnigent's per-session `auth.json` was a symlink to that isolated home, not
  the normal user Codex home. Credential contents were never read, printed,
  copied into Omnigent, or committed.
- The Codex bridge root was corrected to honor Omnigent's configured data root
  instead of defaulting to `~/.omnigent/codex-native`.
- `CODEX_HOME` is now forwarded through the host runner's explicit environment
  allowlist.
- Native Codex host identity now uses the same effective Omnigent config path
  as the daemon, fixing the observed default-host mismatch.
- The server bound only to `127.0.0.1:17677`; accounts and public sharing were
  not enabled. The database recorded zero scheduled tasks and zero scheduled
  task runs.
- The completed conversation was idle with zero pending elicitations and
  pointed only to `/Users/hafizrazali/Projects/Omnigent-fit-test-project`.
- Shutdown was exact and local: the server, host, runner, Codex app server,
  harness, and fit-test tmux server were stopped; ports `17677` and `6767` and
  the fit-test tmux socket were closed afterward.

### Real Development Journey Evidence

- Only `src/workspace-status.js` and `test/workspace-status.test.js` changed in
  the disposable project.
- The worker first changed the expected result, then captured the intended
  failure because `failed` was missing.
- The smallest implementation then derived failed check names from the input.
- The focused fixture suite passed `3/3` independently after the worker
  finished.
- Additional independent cases proved an all-pass shape, two named failures,
  and the unchanged empty-checklist shape.
- Baseline diffs confirmed no change to the fixture's `AGENTS.md` or
  `package.json` and no unrelated source change.
- The Omnigent conversation remained unstaged and uncommitted because the
  disposable fixture is intentionally not a Git repository.

### Omnigent Corrections And Regression Evidence

Three fixture-first corrections were required for the isolated native journey:

1. forward `CODEX_HOME` through the runner environment;
2. place native Codex bridge state under Omnigent's configured data root; and
3. load the daemon host identity from the effective global config path.

The affected host, policy, runtime, and native-Codex suite passed
`1530/1530`. Ruff, Python byte-compilation, and `git diff --check` also passed.
The suite emitted 60 existing deprecation/pytest-marker warnings and no
failures. All Omnigent source changes remain unstaged on the disposable
`test/agent-os-isolation-feasibility` branch.

The native harness requires `tmux`; Homebrew installed `tmux 3.7b`, `utf8proc`,
and upgraded/installed the required `libevent` dependency for this local test.
Those machine-level packages were not removed because cleanup was outside the
approved boundary.

### Remaining Gaps

1. **MCP startup:** `codex_apps` initialized, but the Omnigent MCP client closed
   during its initialize response. Native edits and approvals still worked
   through the app-server/policy hook, but the MCP tool surface is not proven.
2. **Approval concurrency:** parallel native tool requests interact poorly with
   serialized `ASK` decisions. Serial worker instructions are a workaround,
   not the final product behavior.
3. **Adapter packaging:** the external policy module works from source but is
   not yet an installable/versioned package loaded by an ordinary launch.
4. **Skill discovery noise:** Omnigent reported invalid-frontmatter warnings
   while scanning existing Claude skills. It did not change Claude state, but
   production discovery must be scoped or normalized.
5. **Remaining checkpoints:** cross-model review, fresh-session continuity,
   scoped Koda integration, responsibility ownership, and the required Control
   Room interface are still untested.

## Recommended Next Action After Checkpoint 3

Do not adopt or deploy Omnigent yet. Run one narrow local remediation
checkpoint for the MCP startup failure, serialized-approval behavior, and
external-adapter packaging. If those pass, proceed to Checkpoint 4 with a
separately approved second official provider for independent review. Keep real
product repositories, staff, KVM deployment, public sharing, commits, forks,
and upstream actions outside that checkpoint.

## Checkpoint 3 Remediation Results — 2026-08-03

The narrow local remediation passed all three previously blocked areas:

1. **MCP startup fixed.** The Codex app server now preserves the isolated
   `OMNIGENT_DATA_DIR` and writes it explicitly into the generated Omnigent MCP
   child configuration. The final real run recorded both `codex_apps` and
   `omnigent` as `ready`, with no startup error, and Codex saw the
   `mcp__omnigent__*` tool inventory.
2. **Parallel safe reads fixed.** The full Agent OS guard already permits safe
   reads and serializes meaningful write approvals correctly. The isolated
   database's redundant `ask_on_os_tools` policy was disabled after a backup;
   the adapter now declares that blanket policy incompatible. A real
   subscription-backed turn read two fixture files in parallel with no
   approval prompt or hang. Exact writes remain approval-gated by the full
   guard and its approval-bridge fixtures.
3. **External adapter packaged.** `sifututor_agent_os_omnigent` now builds as
   its own wheel instead of joining Omnigent's framework wheel. It installed
   into the isolated environment and imported from the disposable project
   without a source `PYTHONPATH` workaround. The locally corrected Omnigent
   framework was installed editable into that same isolated environment so
   the adapter's public policy seam was present.

Focused tests passed `4/4`, the affected MCP/policy/runtime suite passed
`636/636` after the final correction, and Ruff, byte-compilation, and
`git diff --check` passed. An attempted full `16,944`-item repository
collection could not start because this deliberately narrow environment lacks
the optional Databricks SDK; no test assertion failed, and unrelated provider
dependencies were not installed.

The first real rerun correctly proved parallel reads but exposed that Codex MCP
children require an explicit configured environment. The corrected second run
then proved both parallel reads and MCP readiness. Both trial sessions were
stopped, their explicit Codex app-server and MCP child processes were
terminated, ports `17677` and `6767` were closed, and scheduled tasks remained
zero. Nothing was staged, committed, pushed, forked, opened as a PR, deployed,
or run against a product repository. Normal Codex auth and all Claude settings
remained untouched.

The next permitted checkpoint is not automatic: Checkpoint 4 requires a new
explicit boundary because it introduces a second official provider for
independent cross-model review.

## Checkpoint 4 Executed Results — 2026-08-03

Checkpoint 4 successfully proved the cross-model review mechanism, but the
candidate itself **failed acceptance**. A fresh isolated Claude Max
subscription login ran through Omnigent, independently reviewed the Agent OS
patch, and produced a concrete safety report. Codex then reproduced the most
material bypasses directly instead of accepting the report on trust.

The Claude reviewer used isolated Omnigent and Claude homes, with provider API
keys and unrelated auth variables unset. The isolated first-run flow trusted
only the exact source worktree, and unrelated project MCP servers were
rejected. Claude made no file changes. The completed review conversation was
`488ef811c93f4307b7760ffc811dc9e3`; an earlier pre-fix conversation
`186b522ad5c044b3bb5336ced110d015` was empty and made no model call.

Two fixture-first isolation corrections were needed before the review could
run honestly:

1. `CLAUDE_CONFIG_DIR` was forwarded through the host-to-runner environment
   allowlist.
2. the Claude remote-daemon path was changed to load its host identity from the
   effective isolated Omnigent configuration path rather than the normal user
   home.

The independent review found these adoption blockers:

1. **Check evidence can be forged.** `policy.py` accepts a matching command
   string plus agent-emitted `AGENT_OS_CHECK_OK` text without proving a real
   successful exit status or an absolute allowlisted guard path. Codex
   independently reproduced forged guard and verification evidence being
   accepted.
2. **Commit shortcuts can escape the approved bundle.** `git commit -am` and
   hook-bypass forms reach an approval path instead of being denied, so exact
   staged-file ownership is not guaranteed immediately before commit.
3. **Claude isolation is incomplete.** Parts of the native bridge and state
   layer still read or write normal `~/.claude` and `~/.claude.json` paths or
   ignore the isolated Omnigent data root.
4. **The external adapter's version claim is premature.** It declares
   compatibility with published Omnigent `0.7.x` while importing a new policy
   seam that is only present in the local untracked framework patch.
5. **Runtime boundaries still have gaps.** PID bookkeeping is split between
   isolated and normal homes; shell commands are not confined like direct file
   tools; secret protection is too narrow; and critical-lane state needs a
   scoped human reset.
6. **Quality checks are not yet clean.** The reviewer and Codex reproduced
   formatting/lint issues, and the reviewer identified real policy typing
   errors in addition to generated-stub noise.

Positive evidence remains useful but does not override those bypasses. The
clean focused Agent OS/root suite passed `63/63`; Claude's focused web suite
passed `205/205`; `git diff --check` passed. The review also confirmed that
direct path-taking host handlers fail closed against allowed roots, worktree
authority is explicit, the adapter is excluded from the Omnigent framework
wheel, and the UI no longer invents a workspace by probing the home directory.

The shared evidence model is now proven as **one issue-scoped trail with
independent model conversations**, not one shared model chat. Each provider
retains separate approval and policy state, while GitHub issue #34, this brief,
the Session Map, Mission Ledger, and Koda carry the reconciled outcome. The
reviewer's statement that no live run occurred was inconsistent with the live
run that produced its own report; it is not treated as a code finding.

After evidence capture, the exact trial host, server, runner, Claude process,
and trial tmux server were stopped. Ports `17677` and `6767` were closed, and
no trial process remained. Nothing was staged, committed, pushed, forked,
opened as a PR, deployed, or run against a product repository. Normal Claude
access, permissions, settings, and authentication were not changed.

The next action is a narrow **Checkpoint 4 remediation**, not Checkpoint 5 or
adoption. It must make evidence non-forgeable, deny commit broadening and hook
bypass, complete Claude/data/PID isolation, correct the adapter dependency
seam, confine shell and secret access, add a scoped critical-lane reset, and
make format/lint/type checks clean before another independent review.

## Checkpoint 4 Remediation And Re-Review — 2026-08-03

The bounded remediation is complete and passed the independent review path.
This is a foundation-fit result, not an adoption, deployment, or upstreaming
decision.

The implementation now:

1. records guard and verification evidence only from observed successful tool
   results instead of trusting an agent-written success marker;
2. enforces the absolute approved guard path and invalidates staged evidence
   after writes that can change the bundle;
3. hard-denies commit broadening, hook bypass, commit-producing shortcuts,
   positional pathspecs, and valued forms such as
   `--pathspec-from-file=paths.txt`;
4. detects unquoted shell redirects even without whitespace, blocks shell
   mutation and egress paths, and treats unknown shell commands conservatively;
5. keeps Claude, Codex, Omnigent data, PID, daemon, bridge, and project
   discovery paths on their effective isolated roots;
6. makes worktree authority and host workspace roots explicit instead of
   silently inferring broad access;
7. carries approval state only within the correct task/session and provides a
   scoped critical-lane reset; and
8. packages the Sifututor adapter against the honest public compatibility seam
   with clean focused type, lint, and formatting checks.

Claude reviewed the correction in several read-only passes. The broad
re-review found two final parser gaps: redirects attached directly to an
allowlisted command and `sed --in-place`. After those were fixed, a narrower
review found the valued Git option `--pathspec-from-file=...` and showed that
its first regression fixture was not reaching the intended rule. The final
fixture supplies complete evidence state, the option is normalized before the
denylist check, and the final Claude confirmation returned **GO** in
conversation `5b1f9d9c00df4c3187acd170b05af39e`.

Final evidence on the corrected tree:

- affected Python regression suite: `1781 passed`;
- focused final policy/runtime suite: `196 passed`;
- all 32 changed Python files: Ruff format and lint clean;
- external adapter: focused mypy clean across four source files;
- `git diff --check`: clean;
- prior changed web surface: `4706 passed`, changed-file lint and production
  build passed; and
- nothing staged, committed, pushed, opened as a PR, deployed, or run against
  a product repository.

The upstream repository's one-command full suite was not repeated. An earlier
attempt lacked the optional Databricks dependency and also started a server
against normal `~/.omnigent` before test execution. That process was stopped;
repeating an unsafe command would not add honest evidence. The explicit
changed-surface suite is the final deterministic proof for this fit test.

The fit test also exposed product/runtime gaps that are not security blockers
for the isolated candidate but matter before adoption:

- a Claude final answer can be delivered while the Omnigent session later
  reports `failed` because its terminal/runner exits or disconnects;
- Claude plan mode attempts to write its own plan file and conflicts with a
  strict read-only review sandbox;
- the shared shell parser can ask unnecessarily for compound read commands or
  quoted operator characters;
- native non-interactive permissions prevented Claude from running its own
  tests, so Codex supplied the independent execution evidence; and
- host workspace roots remain intentionally opt-in and must be present in the
  launch environment.

All review-only processes were stopped, ports `6767` and `17677` were closed,
and the isolated database was restored to fixture-only read/write and working
directory roots. The Sifututor root remains only in the full guard's allowed
roots so it can invoke the exact shared read-only guard script; it is not a
sandbox read or write root.

**Decision:** Omnigent remains the leading runtime candidate and Checkpoint 4
no longer blocks Checkpoint 5. Adoption, staff use, product repositories,
forking, upstream changes, commits, KVM, and deployment remain blocked until
their own later boundaries and evidence.

## Checkpoint 5 Attempt And Authentication Blocker — 2026-08-03

Checkpoint 5 began under an explicit fixture-only boundary but stopped before
the first model response, Koda lookup, synthetic memory write, continuation
record, or responsibility classification.

The isolated Claude launch used `--use-native-config`, which is intended to
ignore configured providers and let Claude Code use its own isolated
subscription login. On Omnigent's remote host/runner path, that choice was not
preserved. The runner resolved the configured Anthropic provider instead,
converted its static credential into an `apiKeyHelper` command, and embedded
that helper inside Claude's JSON `--settings` command-line argument. A local
process inventory therefore exposed the credential value.

The trial stopped immediately. The Claude terminal, runner, host, and server
were terminated; ports `6767` and `17677` were closed; the database policies
were restored to fixture-only sandbox and working-directory roots; and no
fit-test processes remained. A credential-pattern scan found no matching value
in the isolated Omnigent log directory. The process inventory itself was
captured during diagnostics, so the affected Anthropic credential must still
be treated as exposed and rotated before another Claude run.

Read-only root-cause evidence:

1. `run_claude_native()` honors `use_claude_config` only while resolving the
   local `claude_config` object.
2. Its remote path explicitly passes neither `use_claude_config` nor
   `claude_config` to the daemon/runner.
3. the runner independently resolves the configured provider;
4. `_provider_config_for_native_claude()` converts a static key into a
   `printf`-based `apiKeyHelper`; and
5. `build_hook_settings()` serializes that helper into the `--settings` argv.

The existing CLI fixture proves only that Click forwards
`use_claude_config=True` into `run_claude_native`. It does not prove the choice
survives remote session creation. Another fixture explicitly expects the
static-key `printf` helper, so the unsafe transport is currently encoded as
desired behavior.

Required remediation before Checkpoint 5 can resume:

- persist the native-config/provider choice across remote session creation and
  make the runner skip configured-provider resolution when requested;
- never place static credentials, bearer values, or secret-bearing helper
  commands in process argv, JSON `--settings`, logs, session events, or status
  output;
- transport any supported configured-provider credential through an
  owner-only file, file descriptor, keychain reference, or equivalent
  non-argv secret lane;
- add a remote-path fixture proving `--use-native-config` ignores a configured
  provider and uses only the isolated `CLAUDE_CONFIG_DIR`;
- add negative fixtures proving a sentinel secret never appears in spawned
  argv, settings JSON, logs, or session resources; and
- independently review the authentication correction before any new Claude
  invocation.

### Local Authentication Remediation — 2026-08-03

Hafiz approved the critical implementation boundary. The isolated Omnigent
worktree now carries a local, unstaged correction:

- `--use-native-config` is persisted in the generated wrapper spec and survives
  the Omnigent compatibility translation, so the remote runner returns to
  Claude Code's own isolated subscription login instead of selecting a
  configured provider;
- resolved static Anthropic keys are no longer converted into a secret-bearing
  `printf` command. The value stays out of `--settings` and process argv, is
  atomically written to an owner-only `0600` file under the private bridge
  directory, and the helper command contains only that file path;
- the same private-file lane is used by runner-owned Claude terminals, direct
  terminal requests, and background-title subprocesses; and
- regression fixtures use synthetic sentinel values to prove the native-login
  choice wins remotely and the secret value is absent from serialized launch
  arguments.

Code-only verification passed: 187 focused native-Claude/title tests, 105
Omnigent-translation and native-terminal auto-create tests, Ruff, Python byte
compilation, and `git diff --check`. A direct mypy invocation remains unsuitable
as a completion gate because the selected modules currently report 121
pre-existing project-wide typing errors, including generated protobuf stubs;
none pointed at the new authentication helpers.

No Claude process or model was invoked, no real credential was read or used,
and nothing was staged, committed, pushed, deployed, or sent upstream. The
affected credential rotation is still unconfirmed. Checkpoint 5 therefore
remains blocked until Hafiz confirms rotation and a separate independent
code-only review accepts this correction. Only then may a fresh isolated live
retest be considered.

No synthetic Koda memory was created, so there is nothing to retire. The next
step is credential-rotation confirmation followed by independent code-only
review, not a workaround through another engine. Checkpoint 5, adoption, staff
use, product repositories, KVM, and deployment remain blocked.

## Checkpoint 5 Controlled Live Retest — 2026-08-04

Hafiz approved the separately controlled live retest after credential rotation,
expanded code verification, and two independent Claude reviews had completed.
The run stayed inside the disposable project, isolated Omnigent data/config,
and isolated `CLAUDE_CONFIG_DIR`. It did not touch a product repository, normal
Claude permissions/settings, live Hermes, staff access, Git publication, or a
deployment.

The main authentication correction passed in the real runner:

- the isolated Claude CLI reported the existing `claude.ai` Max subscription;
- the generated wrapper spec and persisted session label both carried
  `use_native_config: true`;
- the actual Claude terminal resolved `configured=False`, with no Anthropic
  provider environment, key helper, or provider-selected model;
- all ambient `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, and
  `ANTHROPIC_BASE_URL` values were removed from the server, host, and live task
  launch before the accepted run;
- a configured synthetic Anthropic provider was pointed at a dead loopback
  endpoint, and its sentinel value never appeared in process argv, Omnigent
  logs, persisted databases, or provider-secret artifacts; and
- the terminal, runner, host, and server were stopped, port `17677` closed, and
  zero provider-secret artifacts remained.

The real continuity journey did not pass end to end:

1. **Approval resumption failed.** The Agent OS guard correctly parked exact
   `node --test test/` and Koda-search commands. The server accepted both
   approval resolutions with HTTP `202`, but Claude still received
   `This command requires approval`; neither command executed. The final report
   therefore had no test or Koda result. The runner log shows each accepted
   approval being forwarded to `http://harness.local/v1/sessions/.../events`
   and receiving HTTP `404` immediately before the waiting tool returned, which
   identifies a native approval-event routing mismatch rather than a missing
   Hafiz approval.
2. **Cross-root read authority diverged.** Omnigent received both the disposable
   project and Sifututor as approved host roots, but Claude Code was launched
   without equivalent per-session `--add-dir` authority. Direct and shell reads
   of the Mission Ledger were blocked, so `AO-RUNTIME-001` could not be quoted
   from fresh evidence.
3. **Background-title auth ignored the session choice.** The main Claude worker
   used the subscription correctly, but a separate Claude background-title
   process still resolved the configured provider endpoint because its resolver
   uses `spec=None`. The dead loopback endpoint prevented external contact, and
   the sentinel remained contained, but a real provider could receive task-title
   context through the wrong auth route.
4. **Global skill parsing is incompatible.** Omnigent skipped 15 installed
   Claude skills whose frontmatter Claude accepts but Omnigent's stricter YAML
   parser rejects. The fit-test task could still run, but Agent OS parity cannot
   be claimed while those skills disappear from Omnigent sessions.
5. **Terminal cleanup leaked a process.** Claude completed and Omnigent deleted
   the terminal resource, and the runner, host, server, and port stopped, but
   the isolated `tmux` server remained alive with no socket. `tmux kill-server`
   could not reach it; an exact PID-scoped `SIGTERM` was required. The final
   inventory then showed zero isolated processes. This disproves the claimed
   clean terminal lifecycle at the live boundary even though no secret file
   remained.
6. **Headless attachment is imperfect.** The CLI could not clear the automation
   terminal and detached while the worker continued. Omnigent still captured
   the full conversation and final response, so this did not cause the task
   failure, but native non-screen clients need a cleaner attach/follow path.

Claude did prove the remaining safe parts of the journey: it read the three
fixture files, identified the existing readiness-summary behavior, reported the
fixture's non-Git state honestly, separated the fictional `Aina QA` item from
real responsibilities, created no task for the deferred mission, and made no
writes.

**Decision:** Omnigent remains the leading runtime candidate, but Checkpoint 5
is a partial result rather than an adoption pass. The next implementation slice
must be fixture-first and limited to the five blocking integration gaps above:
approval resume, scoped cross-root propagation, session-scoped background-title
auth, shared Claude-skill frontmatter compatibility, and terminal cleanup.
Because three of those surfaces affect authentication or permissions,
implementation requires a fresh critical-lane approval. Product repositories,
staff use, KVM, commit, push, fork, upstream action, and deployment remain
blocked.

## Checkpoint 6 Workspace Interface Prototype — 2026-08-04

Checkpoint 6 produced a local, disposable interface prototype inside the
isolated Omnigent web client. It is available only through the dedicated route
`/agent-os-workspace-prototype` and uses fictional fixtures. It does not start
an Omnigent host, runner, provider, subscription, model session, or product
repository.

### What the prototype proves

| Required layer | Observed prototype behavior | Honest classification |
| --- | --- | --- |
| Control Room | Four full task conversations are visible, independently scrollable, and directly replyable in one view. Each lane preserves its project, model, finish line, worker state, and changed-file summary. | Custom client is feasible; live session binding remains unproven. |
| Focus Workspace | One task keeps chat primary while exposing project/worktree state, editor, diff, evidence, terminal/file affordances, and a visible finish line. | Adaptable from Omnigent's existing task surfaces; fixture composition proven. |
| Worker Sidebar | Orchestrator and worker cards show engine, current action, state, checks, blocker/handback, and the approval boundary beside the focused task. | Custom presentation is feasible; real child-session/event mapping remains unproven. |
| Split Focus | Two complete workbenches remain visible and independently switchable rather than collapsing into summaries or terminal panes. | Custom in-app layout is feasible; live multi-session resource behavior remains unproven. |
| Needs You | A global rail overlays the current workspace with blockers, approvals, and meaningful completions without switching the active task; normal updates remain in a digest. | Custom Responsibility read model is required; attention interaction is proven with fixtures. |

The prototype also makes the persistent Agent OS identity explicit while
showing Codex, Claude, or a routine worker as visible task engines. It keeps a
task's finish line, isolation state, evidence, and approval boundary present so
the interface does not turn into an unstructured collection of chats.

### Files and route

- `web/src/pages/AgentOSWorkspacePrototype.tsx`
- `web/src/pages/AgentOSWorkspacePrototype.css`
- `web/src/pages/AgentOSWorkspacePrototype.test.tsx`
- `web/src/App.tsx` (local dedicated route only)
- review route: `http://127.0.0.1:4177/agent-os-workspace-prototype`
- query views: `?view=focus`, `?view=split`, and `?needs=1`

### Verification

- focused Vitest interaction suite: `5/5` passed;
- TypeScript project type-check: passed;
- production web build: passed;
- Prettier check: passed after formatting the three prototype files;
- browser inspection: Control Room, Focus Workspace, Split Focus, and Needs You
  were rendered at `1600x1000` in headless Chrome and visually inspected;
- `git diff --check`: passed;
- screenshots:
  `evidence/checkpoint-6/control-room.png`,
  `evidence/checkpoint-6/focus-workspace.png`,
  `evidence/checkpoint-6/split-focus.png`, and
  `evidence/checkpoint-6/needs-you.png` under the isolated fit-test root.

The web build printed existing Vite configuration, CSS Highlight API, and
large-chunk warnings. They did not fail the build and were not introduced or
expanded as part of this prototype.

### Decision

Checkpoint 6 passes as a product-shape and client-feasibility prototype, not as
an integrated product. The accumulated evidence now supports this architecture:

```text
Omnigent runtime and policy/session APIs
        +
Sifututor-owned Agent OS workspace client
```

The next controlled slice should bind one real read-only Omnigent session to a
single Control Room lane and one Focus Workspace, including worker events and
fresh task state. Do not implement all sources or actions at once. Commit,
publication, upstream contribution, product repositories, staff access, KVM,
and deployment remain separate approval boundaries.
