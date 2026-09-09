# Hermes Foundation Fit Test

Status: Real-agent desktop task, fresh-state continuity recovery, and isolated
Telegram round trip passed

Approved direction: Hafiz approved the fully isolated Option C on 2026-08-02,
conditional on checking for a Hermes update before proceeding.

## Product Goal

Build one native Agent OS work environment, comparable in role to VS Code,
Claude Code, the Codex app, or Hermes, where Hafiz performs the actual work.
The product must combine agent chat, project navigation, code and document
editing, terminal and tool execution, delegation, evidence review, approvals,
and cross-session responsibility awareness.

A reminder assistant beside another development environment does not meet the
goal.

## Why Test Hermes First

Current Hermes already provides many expensive foundation pieces:

- a native desktop application and messaging gateway,
- persistent searchable sessions,
- projects and profiles,
- model/provider selection including Claude and Codex paths,
- tools, terminal work, diffs, skills, plugins, and ACP editor integration,
- scheduled jobs and Telegram delivery,
- a durable multi-project Kanban and agent dispatcher.

Hermes is therefore worth testing as a foundation before Sifututor builds or
forks a complete application. The test is not permission to make Hermes the
product. It is an evidence-gathering step.

## Verified Local Constraint

The existing Mac installation is Hermes v0.14.0 with an active launchd gateway.
Its source checkout is behind current upstream and contains a local
`cron/scheduler.py` customization for human-readable Telegram failure alerts.

The live installation must remain untouched during the fit test.

## Fresh Update Check

The official read-only command `hermes update --check` was run on 2026-08-02.
It fetched remote references and reported that the installed checkout is 11,371
commits behind `origin/main`. No update was installed and the live source
worktree remained on v0.14.0 with its existing local scheduler modification.

The normal `hermes --version` output still displayed an older 381-commit
summary after the fetch. Treat the explicit update check and Git comparison as
the fresh evidence; do not use the stale summary to choose a test version.

The newest fetched stable tag is `v2026.7.30`, identified by its signed release
message as Hermes Agent v0.19.1. Use that immutable tag for the fit test rather
than the moving `origin/main` branch. The release accepts Node 20.19 or newer;
the Mac currently has Node 20.20.2, npm 10.8.2, Python 3.11.15, and uv 0.11.13.
Current `origin/main` already requires a newer Node version, so testing `main`
would add an unrelated system-toolchain change.

## Options Considered

### Option A — Upgrade and test the existing installation

Fastest in theory, but rejected. It risks the running Telegram assistant,
existing sessions/configuration, and the local scheduler customization.

### Option B — Use another profile on the existing installation

Better data isolation, but insufficient here. Hermes profiles isolate config,
sessions, memory, skills, logs, cron jobs, and gateways, while still relying on
the installed source/runtime. That would test old locally modified code rather
than current upstream.

### Option C — Separate current-version checkout and disposable Hermes home

Recommended. Use a separate source checkout, separate `HERMES_HOME`, separate
desktop application identity/user data, a disposable test project, and no
connection to the existing Telegram bot. This tests current Hermes without
changing the live service.

### Option D — Fork Hermes immediately

Rejected for the first test. A full fork creates ongoing update and merge work
before we know which changes are truly necessary.

## Recommended Test Boundary

The fit test uses Option C and stops after evidence and a recommendation. It
does not replace, update, stop, restart, or reconfigure the existing Hermes
installation. It does not create a production service, deploy a gateway, reuse
the live Telegram bot token, push a fork, or change Claude/Codex permissions.

Any credential or messaging setup needed for the test must be separately
scoped and must not expose secret values in files, logs, reports, or commits.

## Exact Isolated Preflight

Use these currently available paths:

| Purpose | Exact path |
| --- | --- |
| Current-version source checkout | `/Users/hafizrazali/Projects/Hermes-worktrees/agent-os-native-fit-test` |
| Persistent sandbox root | `/Users/hafizrazali/Projects/Hermes-worktrees/agent-os-native-fit-test/.hermes-sandbox` |
| Isolated Hermes home | `/Users/hafizrazali/Projects/Hermes-worktrees/agent-os-native-fit-test/.hermes-sandbox/hermes-home` |
| Isolated Electron user data | `/Users/hafizrazali/Projects/Hermes-worktrees/agent-os-native-fit-test/.hermes-sandbox/user-data` |
| Disposable test project | `/Users/hafizrazali/Projects/Hermes-fit-test-project` |

Hermes's own `scripts/dev-sandbox.sh --persistent` exports the isolated
`HERMES_HOME`, Electron user-data directory, and a per-worktree application
name. Use that supported path instead of inventing another launcher. Do not use
its `--from ~/.hermes` option because that would copy live configuration,
sessions, skills, and authentication material into the test.

The supported sandbox isolates files but does not remove credentials inherited
from the terminal that starts it. The first doctor run detected an inherited
Anthropic environment variable and attempted a connectivity check; its value
was never read or printed. All subsequent test commands must therefore run
through `.hermes-sandbox/run-isolated.sh`. That local ignored wrapper starts
with an allowlisted environment, then calls the upstream sandbox script. This
keeps provider keys, messaging tokens, and other agent credentials out of the
fit-test process while preserving the upstream file-isolation behavior.

The stable checkout, Python 3.11 virtual environment, and desktop dependencies
are installed. `Hermes Agent v0.19.1 (2026.7.30)` runs from the isolated path,
the native desktop production build succeeds on Node 20.20.2, and the source
checkout is clean. npm reported Node 22 preferences in several development
dependencies and nine dependency advisories; those are recorded evidence, not
automatically rewritten with `npm audit fix` during this pinned test.

### Model/provider access

Nous Portal is optional; it is not required to use or evaluate Hermes. The
first device-login link led Hafiz to a subscription landing page rather than a
clear approval screen, so that login was cancelled. Do not ask Hafiz to buy a
Nous plan for this fit test.

Prove the native interface first with Hermes's built-in local mock provider,
which needs no account or external model usage. If the interface itself is a
promising fit, use a subscription OAuth route rather than an API key for the
actual agent task. Any real provider authentication must happen interactively
inside the isolated home; the agent does not read, copy, print, or migrate
credentials from live Hermes. Do not use the existing Codex OAuth files because
earlier sessions found competing-client refresh-token instability.

For this fit test, the recommended subscription path is a fresh ChatGPT/Codex
device login written only to the isolated Hermes auth store. This is supported
by Hermes and does not require Nous or an API key. Anthropic OAuth is not an
equivalent use of an ordinary Claude subscription: current Hermes documentation
says it requires Claude Max plus separately purchased extra-usage credits and
does not consume the normal included Claude allowance. Do not start either
login until Hafiz confirms which subscription account should be used.

The sanitized doctor check also showed that Hermes can discover GitHub CLI
authentication even when provider environment variables are removed. Do not
treat discovered CLI credentials as approved fit-test credentials and do not
use them for outward Git actions.

### Telegram approach

Split the test into two checkpoints:

1. Prove the native desktop development and continuity journey first.
2. Only after that passes, connect a separate Telegram test bot created for the
   sandbox. Never reuse the live bot token or run two gateways against it.

The Telegram Phase A preflight completed on 2026-08-02. The isolated profile
has no Telegram bot token, allowed-user list, or home channel configured. Use a
new manual `@BotFather` test bot rather than Hermes's Nous-managed QR onboarding
so the channel remains independent of the Nous Portal. Restrict it to Hafiz's
numeric Telegram user ID; never leave the test bot open to unknown users.

One important runtime boundary was confirmed: `hermes gateway status` resolves
the machine-global launchd service `ai.hermes.gateway`, which is the protected
live Hermes gateway at PID 2397. Therefore the isolated test must never run
`hermes gateway start`, `restart`, `stop`, or `install`. After the separate bot
is configured, run the current checkout directly through
`.hermes-sandbox/run-isolated.sh` with a foreground `gateway run --force`
process. Its PID and runtime files remain under the isolated `HERMES_HOME`, and
the separate bot identity avoids Hermes's machine-local duplicate-token lock.
Stop before entering any token until Hafiz creates the test bot and can enter
the credential privately; do not paste the token into chat, docs, logs, Koda,
or Git. The isolated Messaging screen may save the manual bot fields, but do
not click its `Restart gateway` button: that button spawns the same global
service command. Save the isolated fields only, then let Codex start the exact
checkout with the approved foreground command.

Phase B reached the connected checkpoint on 2026-08-03. Hafiz privately saved
a separate bot token and numeric allowed-user ID; the optional home channel is
still unset. Codex verified presence only, never the values, then started the
exact v0.19.1 checkout through the sanitized wrapper with foreground
`gateway run --force`. The isolated gateway is PID 84865, secret redaction is
enabled, Telegram connected in polling mode, and exactly one platform is
active. The protected live gateway remains separately running at PID 2397.

The controlled round trip then passed. From Telegram, Hafiz asked Hermes to
read only the disposable project's `AGENTS.md` and `.agent-os/continuity.md` and
report the current goal and exact next action without writes. Hermes returned
the correct goal, distinguished local commit `fc3093f` from the modified
unstaged continuity record and untracked sandbox, and proposed only fresh
read-only Git verification. Independent checks matched that report: branch
`main`, `fc3093f` at HEAD, no remote or upstream, `.agent-os/continuity.md`
modified, `.hermes-sandbox/` untracked, and nothing staged. A background native
app snapshot then confirmed the same fit-test project, sessions, files, terminal
evidence, and Telegram-connected state remained available on desktop. Codex
stopped only isolated PID 84865 with SIGINT; it disconnected cleanly in 0.68
seconds, while protected live gateway PID 2397 remained running unchanged.

Two privacy-hardening gaps were found. Gateway diagnostics log Telegram's
numeric chat/user identifier, and the desktop Messaging screen partially masks
the bot token rather than fully concealing it. No credential value was copied
into Git, docs, Koda, or the final report. The temporary desktop screenshot that
contained the partial display was deleted immediately. Production adoption
should redact messaging identifiers in routine logs and fully conceal stored
secrets in the UI and accessibility tree.

### Pre-change snapshot and cleanup

Before creating anything, record the live Hermes source HEAD, dirty path list,
gateway status, and version. After the test, compare them again. Keep the
sandbox and disposable project until Hafiz has reviewed the evidence. Removal
is a separate destructive cleanup action and requires approval for these exact
paths.

## Mock-Provider Desktop Checkpoint

The account-free desktop checkpoint passed on 2026-08-02 using Hermes Agent
v0.19.1, its local mock provider, the isolated home, and the disposable
project. This proves the work-surface foundation without treating a canned
model reply as real agent work.

Proven in the native application:

- project-scoped sessions and chat,
- a project file tree and readable document preview/source/diff controls,
- a direct file-editing surface with an explicit save/cancel boundary,
- an embedded terminal that ran `npm test` in the disposable project with
  3 passing tests and 0 failures,
- visible Git branch/change-count context,
- no Nous login, subscription, or real model credential.

The checkpoint remains partial for the complete product goal. The mock reply
cannot inspect, change, or verify code, so actual agent-driven editing,
approval-stop behavior, continuity recovery, delegation, and Telegram are not
yet proven. A real provider must be chosen and authorized separately before
that part of the journey.

Two foundation limitations were also observed:

- starting the desktop development build brought Electron to the foreground;
- separating Hermes state does not create an operating-system filesystem
  sandbox: the Projects view could discover other folders under the user's
  home directory. No unrelated project was opened or changed, but production
  use will need explicit workspace allowlisting or stronger process isolation.

Screenshot evidence is currently local under `/tmp`, including
`hermes-fit-test-readme.png`, `hermes-fit-test-readme-edit.png`, and
`hermes-fit-test-terminal-result.png`.

## Subscription And Real-Agent Checkpoint

Hafiz confirmed ChatGPT/Codex subscription OAuth. A fresh device login was
completed through the allowlisted isolated launcher after explicitly declining
Hermes's offer to import existing Codex credentials. Hermes stored one OAuth
credential only in the isolated auth store, selected `gpt-5.6-sol`, and returned
the exact expected response in a minimal connectivity check. The already-open
desktop discovered the new provider without a restart.

The first real desktop task then passed:

- Hermes read only the four approved fixture files, proposed a two-file change,
  and stopped for approval before editing or running commands.
- After approval it used RED -> GREEN: the new assertions failed first for the
  missing `failed` field, then the minimal implementation passed 4 tests with
  0 failures.
- It changed only `src/workspace-status.js` and
  `test/workspace-status.test.js`, reported the patch cards inside the desktop,
  passed `git diff --check`, and confirmed nothing was staged.
- Independent verification reproduced the 4/4 passing result.
- It created `.agent-os/continuity.md` as the separately approved pause record.

Two important foundation gaps emerged:

1. The post-turn self-improvement review created an active
   `approval-gated-code-changes` skill in the isolated Hermes home. Hafiz
   confirmed that automatic self-improvement is a valuable Hermes capability;
   the product question is how activation should be controlled, not whether
   the capability should exist. The isolated config currently sets
   `skills.write_approval: true`, and a harmless probe proved that this mode
   stages proposed skills for review instead of activating them immediately.
   Initial read-only review found the generated skill relevant and well
   structured: it preserved independent approval boundaries, RED -> GREEN,
   exact-scope verification, and honest handling of untracked repositories.
   The skill remains untouched while the long-term activation policy is chosen.
2. Project-scoped new-session creation initially failed because the disposable
   repository had no first commit: Hermes ran `git switch main`, but an unborn
   `main` is not a valid reference. Hafiz approved an exact seven-file local
   checkpoint commit, `fc3093f`, excluding `.hermes-sandbox/`. A new session
   then opened successfully and read only `AGENTS.md` plus
   `.agent-os/continuity.md`. It recovered the correct project, goal,
   implementation, 4/4 test evidence, next boundary, and sandbox warning.
   However, the continuity record had been written before the commit, so it
   repeated the stale claim that nothing was committed. The capability works,
   but continuation packs must be refreshed after every commit, push, PR,
   merge, deploy, or other state-changing boundary before they are trusted as
   current state.

The continuity gap was then corrected and retested. The shared save-session
owner now requires refreshing continuation packs after every state-changing
boundary and verifying fresh Git or external state on resume. The disposable
continuity record was refreshed after `fc3093f`, and a brand-new Hermes chat
read only `AGENTS.md` plus `.agent-os/continuity.md` before running the three
approved read-only Git checks. It correctly reported `main`, latest commit
`fc3093f`, the unstaged `.agent-os/continuity.md` change, the untracked
`.hermes-sandbox/`, nothing staged, no configured remote, local-only/unpushed
state, and the fresh approval boundary. It made no file or Git changes. Desktop
continuity therefore passes; Telegram remains a separate next checkpoint.

One Codex orchestration mistake also created an untracked
`/Users/hafizrazali/Projects/Hermes-fit-test-project/.hermes-sandbox/` while a
connectivity command was launched from the wrong cwd. It contains no imported
Codex credential and the command failed closed. The folder is preserved and
must not be deleted without explicit approval.

## The One Complete Test Journey

The test is successful only if Hafiz can perform a small real development task
inside the working environment from beginning to end.

1. Open a disposable project from the native desktop interface.
2. Ask the Agent OS in normal language to make one safe, visible documentation
   or code change.
3. Inspect the relevant project files inside the interface.
4. Edit or patch the file through the agent and, where supported, directly in
   the interface.
5. Run a focused terminal check from the same work environment.
6. Review the resulting diff, tool activity, and evidence without switching to
   a separate development application for the normal path.
7. Exercise an approval boundary and confirm the assistant stops honestly
   before an unapproved outward action.
8. End or pause the session and produce a reviewed continuity draft containing:
   current goal, proven state, changed files, evidence, deferred work, anything
   waiting on Hafiz, and one next action.
9. Start a new session and recover the correct project and next action without
   relying on the old chat scrollback.
10. Deliver a test reminder through a separate Telegram test bot or an approved
    non-live equivalent, then return to the same work state from desktop.

## Responsibility-Awareness Checkpoint

A bounded native-desktop scenario passed on 2026-08-03. Codex added one
clearly labelled disposable fixture,
`.agent-os/responsibility-test.md`, containing fictional current work, a
fictional approval waiting on Hafiz, a fictional staff blocker depending on
that approval, and fictional deferred work. A fresh Hermes project session was
instructed to read only `AGENTS.md`, `.agent-os/continuity.md`, and that fixture.

Hermes produced a Responsibility Briefing that:

- kept current work, waiting on Hafiz, staff blocked, and deferred work in
  separate sections;
- linked `TEST-STAFF-001` to `TEST-APPROVAL-001`;
- recommended the approval first because it unblocks the fictional staff
  member;
- preserved the real repository approval boundary separately;
- stated that every `TEST-*` entry was fictional and no action was taken or
  recorded elsewhere; and
- used only file-read actions, with no file, Git, task, memory, message, or
  external-system write.

This proves reactive classification and prioritization from structured local
state. It does not yet prove the complete assistant behavior Hafiz wants:
automatic discovery across projects and sessions, proactive reminders, staff
dependency intake, overdue detection, or phone alerts without Hafiz first
asking the right question. Treat those as the next product layer, not as
already provided by this response.

## What Must Be Proven

| Area | Passing evidence |
| --- | --- |
| Native work surface | Project, chat, files, terminal/tool activity, diffs, and evidence are usable as one coherent workflow. |
| Actual task execution | A real disposable change is made and checked; this is not a mock conversation. |
| Agent OS behavior | Routing, explanation, approval stop, verification, and close-out follow the shared playbooks. |
| Model delegation | At least one worker path can be selected without making that model the permanent orchestrator. |
| Continuity | A new session can recover the correct goal, state, dependencies, and next action. |
| Responsibility awareness | The interface can surface deferred work and something waiting on Hafiz separately from generic memory. |
| Telegram | A separate test channel can deliver a useful reminder without coupling to the live bot. |
| Isolation | The current v0.14 gateway, sessions, configuration, bot, and local scheduler patch remain unchanged. |

## Honest Failure Conditions

The foundation test fails or becomes only a partial fit when any of these are
true:

- the normal development journey still requires VS Code for routine file or
  diff work,
- the desktop surface only previews files and cannot support an acceptable
  edit/review loop,
- Agent OS guardrails exist only as prompt suggestions and cannot reliably
  stop protected actions,
- sessions are searchable but cannot become structured, reviewable work state,
- deferred work and Hafiz dependencies collapse into generic chat memory,
- model delegation cannot preserve one orchestrator and one evidence trail,
- supported plugins, skills, ACP, or APIs cannot close the gap without changing
  Hermes core,
- isolation requires touching the live installation.

## Decision After The Test

Use the smallest ownership level supported by evidence:

1. **Use upstream Hermes plus Agent OS extensions** when supported extension
   points cover the journey.
2. **Use upstream Hermes core with a Sifututor-owned native desktop shell** when
   the backend fits but the working interface does not.
3. **Maintain a narrow desktop fork** when specific upstream desktop changes
   are unavoidable and can be kept isolated.
4. **Build a separate product** only when Hermes core, state, or enforcement
   conflicts with the Agent OS requirements.

Do not choose a full fork merely because customization is possible.

## Evidence Pack

The test report should include:

- exact Hermes source version and isolated paths used,
- proof that the live installation was unchanged,
- screenshots of the native journey where safe,
- the disposable project diff and focused check result,
- the approval-stop evidence,
- the session continuation draft and resumed-session result,
- Telegram delivery evidence without tokens or private payloads,
- a requirement matrix marked pass, partial, fail, or not tested,
- recommendation: extend upstream, own the shell, narrow fork, or separate build.

## Out Of Scope For This Test

- WhatsApp integration,
- production deployment,
- staff rollout,
- real product-repository changes,
- migration of existing Hermes sessions or configuration,
- modification of Claude or Codex access permissions,
- automatic push, PR, merge, deploy, or destructive behavior,
- final visual design of the future product.

## Approval Boundary

This document approves no installation or configuration change by itself.
Implementation begins only after Hafiz approves the isolated test boundary and
the exact local paths, test project, model/provider access approach, and
Telegram test-channel approach.
