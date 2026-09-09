# Agent OS History Retrospective — 2026-08-22

Last updated: 2026-08-22

This is the committable summary of a real-session retrospective mined from
Hafiz's own Claude Code and Codex CLI history across the Sifututor workspace
and Omnigent. It reports findings, confidence, severity, and recommended
fixes only — it deliberately excludes verbatim transcript quotes, per
[`agent-os-improvement-loop.md`](agent-os-improvement-loop.md)'s Real-Session
Retrospective rule that raw-conversation excerpts stay local diagnostic
evidence, not a committed artifact. The full evidence version (with quotes,
file citations, and per-finding verifier notes) lives locally, git-ignored,
at `.local/agent-os-history-mining-2026-08-22/full-report-with-evidence.md`
— read that copy for the underlying transcript evidence behind any finding
below.

## Immediate action needed (read this first)

Finding F6 below includes a live issue that should not wait for this doc to
be acted on in order: a 2026-08-16 Koda self-audit found **8 creative-hub
memories still holding a raw plaintext secret**, despite already being
flagged outdated. All 3 independent verifiers in this retrospective
reconfirmed it directly against that session. Locate and remove/rotate those
memories now, separately from the rest of this report.

## Methodology & Scope

A grep-anchored multi-agent mining pass ran across 31 history slices covering
roughly 1,530 session/transcript files (~18.9GB) spanning Claude Code and
Codex CLI usage across the Sifututor workspace and Omnigent, from
approximately May 2026 through 2026-08-22. This produced 317 raw candidate
findings, clustered from two independent lenses, merged into 18 themes, each
then checked by 3 independent adversarial verifiers who re-opened the cited
source files and either confirmed, partially confirmed, or rejected the
claim. All 18 themes reached majority verifier confirmation; none fell into
a weaker-signal bucket this round.

**Process gap, stated plainly:** this pass did not run the canonical tool
`agent-os-improvement-loop.md`'s Real-Session Retrospective section already
names for this exact exercise —
`python3 scripts/agent-checks/agent-os-transcript-retrospective.py` (present
in the repo, confirmed). It used a parallel ad hoc process instead. Running
the canonical script and reconciling its output against the 18 themes here
is the natural next step, not a new one-off ask.

**Coverage:** not every available transcript file was parsed by the
canonical tool this round — 31 manually-selected history slices (~1,530
files, ~18.9GB) were parsed, grep-filtered, and deduplicated by the ad hoc
process instead.

**Depth:** aggregate patterns were measured across the 317 raw candidates,
and every one of the 18 surviving themes was manually re-opened and
re-verified by 3 independent adversarial reviewers directly against the raw
transcripts before being confirmed.

**Honest limits:** counts (evidence totals, "X times across Y weeks") are
directional/minimum-bound, not precise — verifiers repeatedly found
individual example-file citations mismatched to the wrong session, or a
duplicate Codex session-fork replay inflating a raw count. Where that
happened it's noted under the specific finding. Section "Claude vs Codex
Parity" below is narrower than the report's other goals — see the
coverage-gap note at the end of that section. Some issues found here
(notably the Koda MCP transport timeout, F5) were already root-caused and
fixed during the window this data covers — flagged as fixed-but-worth
documenting, not open bugs.

---

## Executive Summary — Highest-Priority Findings

Ranked by how much money/trust/time they cost:

1. **A green test suite is not proof of a working feature.** Across SIMS
   #1842, #1918, the CRM Request Workspace, an 11-round Ripple build/review
   cycle, and the assessment-content bank, focused test suites repeatedly
   passed while real production-affecting bugs (a live Postgres type error,
   an owner-settlement bug, a concurrency test that deadlocked on itself,
   gamed pass metrics) slipped through — caught only when a second,
   independently-run Codex review looked with fresh eyes. The single
   most evidence-backed pattern in the corpus (30 pieces of evidence, high
   severity by all 3 verifiers).
2. **Completion/verification claims have stated things that weren't true,
   more than once.** A staff UAT guide was declared fully verified for a
   workspace nothing in the app actually links to; a production-readiness
   claim missed a hardcoded production hostname; a UX audit reported feature
   flags as off when the live database said otherwise. Each was caught by
   Hafiz or an independent Codex pass, not by the agent itself.
3. **Koda has a live security problem, not just a workflow annoyance.** See
   "Immediate action needed" above, plus 32+ memories carrying a deprecated
   tag and a mechanism where simply reading a memory silently corrupts its
   own staleness metrics. Koda is also structurally skipped in plan mode and
   at least one delegated worker session, even where the session's own
   instructions said to search it.
4. **A quality-gate hook has been silently dead for a month.**
   `test-coverage-gate.py` throws on almost every Bash call due to a Python
   version-compatibility bug, since late July. It fails open (blocks
   nothing), so the coverage gate going silent went unnoticed.
5. **Production deploys keep tripping on the same handful of mechanical
   problems, and billing bugs recur without a regression test after the
   first fix.** SSH keys not registered mid-deploy, `sudo` breaking PM2
   restarts via the wrong `HOME`, an Apache proxy silently routing a domain
   to the wrong host for days — rediscovered rather than checked for.
   Separately, duplicate class-scheduling in SIMS was fixed once in late
   June, then had to be fixed again three weeks later via a different code
   path, and an integration-vs-backport route-skip warning recurred across
   many sessions.
6. **The permission classifier blocks work Hafiz already authorized, with no
   escalation path.** Routine, already-agreed production-adjacent actions
   have been denied mid-task with no way to self-grant, forcing Hafiz to
   step in manually.
7. **Delegated background workers regularly finish and skip their required
   handback file.** The watchdog catches it every time, but each miss costs
   a full redispatch cycle — confirmed across at least 3 distinct jobs on 2
   projects.
8. **Every fresh git worktree starts from zero**, re-triggering the same
   setup problems each time: missing `node_modules`, no private test DB, a
   broken local MySQL auth plugin, scripts that can't resolve dependencies
   from `/tmp`. Rediscovered fresh, session after session.

---

## Findings By Category

Grouped using the Mistake Types taxonomy from
[`agent-os-improvement-loop.md`](agent-os-improvement-loop.md).

### Communication

**F17 — Explanations stay too technical or dense despite the standing
plain-language rule.** Despite `working-with-hafiz.md`'s explicit rule to
explain like code translated into plain English, Hafiz repeatedly has to
stop mid-session and ask for a plain explanation, across both Claude and
Codex, across multiple projects. Confirmed (3/3 verifiers), low-medium
severity — a trust/communication cost, not correctness risk. One cited
frequency claim was an overcount from duplicate log lines; corrected in the
full report. *Fix:* extend the existing
`scripts/agent-checks/agent-os-response-shape-runner.py` `explanation_first`
check family (which already flags ordering problems) with a jargon-detection
case, since the gap here is dense unexplained jargon, not wrong ordering.
*Owner:* [`agent-os-communication.md`](agent-os-communication.md),
[`working-with-hafiz.md`](working-with-hafiz.md).

### Routing

**F10 — Task/prompt routing misfires.** The Agent OS's own eval `AO-002`
(a short imperative like "Commit this." should route to `$commit`) is
already documented in `agent-os-evals.md` and the eval runner, and the
classifier fails it today — confirmed live, not a mining artifact. A
separate live misroute (a workflow-optimization prompt sent to save-session
instead of workflow-improvement) was self-flagged by the agent as a known,
recurring gap. Confirmed for the core dispatcher-misroute claim, medium
severity — it misroutes exactly the short natural commands Hafiz uses most.
*Fix:* this is a classifier fix, not a missing-eval problem — AO-002 already
exists and fails; fix short-imperative-command handling directly, then
broaden the eval suite with more short-imperative variants. *Owner:*
[`task-router.md`](task-router.md),
[`agent-os-routing-model.md`](agent-os-routing-model.md),
[`agent-os-evals.md`](agent-os-evals.md).

### Approval

**F2 — Permission classifier and unattended-session default-deny block
legitimate, already-authorized actions.** Claude Code's auto-mode classifier
has repeatedly denied routine, already-authorized production-adjacent
actions (a PR merge, an SSH tunnel to production, a Laravel tinker session
over SSH) with no self-grant path. Separately, fully unattended background
sessions hit a stricter default-deny even for allowlisted patterns.
Confirmed for the classifier-blocks-authorized-actions half (3/3, strong
evidence), medium severity; the unattended-session half is real but a
weaker, distinct sub-claim. *Fix:* define an explicit escalation/self-grant
path in the approval-gates playbook for classifier-blocked-but-already
-authorized actions; document a degraded-but-visible behavior for
unattended sessions instead of full default-deny. *Owner:*
[`agent-os-approval-gates.md`](agent-os-approval-gates.md), cross-check
[`handoff.md`](handoff.md).

**F16 — Stopping-point calibration is inconsistent in both directions.** Two
mirror-image mistakes recur: the agent stops to ask permission on work
already authorized (and admits afterward it shouldn't have), and the agent
silently broadens scope beyond what was requested. Two clean, dated,
verbatim-confirmed instances anchor this (2026-08-15 and 2026-07-17), plus a
standing correction note from 2026-06-18. Confirmed (3/3), medium severity
— the underlying rule already exists on paper in `working-with-hafiz.md` and
self-correction worked every time it was observed, but the miss still costs
real turns. Evidence-citation quality for this theme was mediocre and
should be tightened before promotion to a fixture. *Fix:* promote the
existing autopilot-boundary rule from documented guidance to an eval/fixture
per the enforcement ladder in
[`agent-os-enforcement-drift.md`](agent-os-enforcement-drift.md) — repeat
mistakes are exactly its promotion trigger. *Owner:*
[`agent-os-approval-gates.md`](agent-os-approval-gates.md) and
[`working-with-hafiz.md`](working-with-hafiz.md).

### State

**F7 — Completion, verification, or deployment claims don't match
reality.** A staff UAT guide claimed a workflow was verified working with no
actual way to navigate to it; a production-readiness claim missed a
hardcoded production hostname; a UX audit inferred live feature-flag state
from migration defaults instead of the actual database, misreporting most
flags. All 8 pieces of evidence span ripple-suite across 3 distinct weeks.
Confirmed (3/3), high severity — each was caught by Hafiz or an independent
Codex pass, never the agent's own self-check, and directly undermines the
evidence model the whole Agent OS depends on. *Fix:* require checking live
system state (not a cached doc line, migration default, or nav assumption)
before any "verified/deployed/live" claim — this is exactly what
`no-mistakes-lite.md`'s State Honesty Rule already asks for; the gap is
consistency. *Owner:* [`agent-os-state-model.md`](agent-os-state-model.md);
cross-reference [`no-mistakes-lite.md`](no-mistakes-lite.md) and
[`commit.md`](commit.md)'s close-out rule.

**F8 — Delegated background worker jobs exit "successfully" without writing
the required handback.** Across multiple SIMS and Ripple issues, a bounded
background worker completes and exits cleanly but skips the mandatory
handback file, forcing a fresh session to reconstruct state and redispatch.
3 clean, distinct, verbatim-confirmed instances across 2 projects and 3
dates. Confirmed (3/3) for the core pattern, low-medium severity — the
watchdog catches every confirmed miss, so no work is silently lost, but each
miss costs a full redispatch cycle. The originally-cited evidence count was
found to be inflated by one weak citation; the core pattern still holds.
*Fix:* make the handback file a hard exit-gate for bounded/background
workers, not a watchdog-detected-after-the-fact convention. *Owner:*
[`handoff.md`](handoff.md); cross-reference
[`agent-os-state-model.md`](agent-os-state-model.md).

**F9 — Multi-worktree/multi-agent layout causes state bleed and stale
task-state files.** The parallel git-worktree architecture has leaked state
across concurrent sessions: branch-name collisions, unrelated dirty files
from a concurrent session appearing mid-run, competing drafts written into a
shared delegation directory, and a stale `active.json` pointing at an
unrelated, already-finished feature. 4 distinct sub-patterns confirmed
across at least 3 dates and 2 projects. Confirmed (3/3), medium severity —
self-detection worked every verified time, but this is exactly the kind of
risk that eventually won't self-detect. *Fix:* add multi-worktree
concurrency guidance — branch-collision pre-checks, `active.json` staleness
detection against the actual current branch, and shared delegation
-directory locking/ownership marking. *Owner:*
[`agent-os-state-model.md`](agent-os-state-model.md) and
[`parallel-work-and-worktrees.md`](parallel-work-and-worktrees.md).

### Skill/Playbook Drift

**F3 — Pre-commit guard and commit mechanics create friction unrelated to
the change being committed.** The Mission Ledger checker has blocked
otherwise-ready commits over an invalid `Status` value, a malformed
`Parent`/`Links` field, or a nonexistent parent ID elsewhere in the repo;
unrelated large-file churn has slipped into feature commits; heredoc/quoting
issues have repeatedly broken agent-authored commit commands (a rule
`AGENTS.md` already documents but that doesn't consistently land in
practice). A broader grep beyond the originally-cited evidence found 30+
distinct Mission Ledger check failures from June through August, confirming
this is genuinely frequent. Confirmed (3/3), medium severity — real,
frequent friction on the highest-traffic part of the workflow, though no
observed instance permanently blocked a correct commit. *Fix:* scope the
pre-commit guard's Mission Ledger check to files actually touched by the
current change; make the safe heredoc/quoting pattern more visible at the
point commit messages are composed. *Owner:* [`commit.md`](commit.md) and
`docs/agent-playbooks/mission-ledger/*.md`.

### Hook/Automation Drift

**F1 — `test-coverage-gate.py` hook crashes on nearly every Bash call.** A
`PreToolUse` hook uses a Python type-hint syntax the running interpreter
can't parse, throwing on almost every Bash command. Non-blocking, so the
coverage gate has silently done nothing for roughly a month. All 3
verifiers independently reproduced the exact crash live against the current
repo file and the machine's actual Python interpreter, and confirmed the
identical traceback firing hundreds to over a thousand times across 4
distinct sessions. Confirmed (3/3, reproduced live), high severity — the
strongest-evidenced single bug in this report; a core quality gate silently
inert for a month. *Fix:* fix the Python compatibility bug directly; more
importantly, add a health check that detects "a hook crashed on almost
every call this session" so a fail-open hook crashing 100% of the time
can't go unnoticed again. *Owner:*
[`agent-os-hook-dispatcher.md`](agent-os-hook-dispatcher.md) plus a new
check in [`agent-os-evals.md`](agent-os-evals.md)'s health suite.

**F18 — Session-start hook injects the wrong project context into Kelasapp
worktrees.** The global session-start hook `~/.claude/hooks/inject-skill
-context.py` injected identical, byte-for-byte wrong "Ripple Suite" project
context into two separate Kelasapp worktree sessions, five days apart, at
two different worktree path conventions. In both cases the agent
self-corrected using `CLAUDE.md`/`AGENTS.md` before doing any wrong work.
Confirmed (3/3, by opening the raw injected-context attachments directly,
not just paraphrase), medium severity — no wrong action was taken either
observed time, but the failure mode risks a future session silently
following the wrong project's skills. *Correction from an earlier pass of
this analysis:* the responsible file is `inject-skill-context.py`, not "the
skill-context-router hook" (no file by that name exists in the repo), and
`agent-os-hook-dispatcher.md` currently documents this hook under no name at
all. *Fix:* fix the worktree-cwd project-detection logic in
`inject-skill-context.py` directly, add a fixture regression test using a
Kelas worktree path, and add the missing entry for this hook to
`agent-os-hook-dispatcher.md`. *Owner:* `~/.claude/hooks/inject-skill
-context.py` (global hook); [`agent-os-hook-dispatcher.md`](agent-os-hook-dispatcher.md)
needs a new entry.

### Eval/Check Gap

**F11 — Tests/lint pass green, but independent Codex review still finds
release-blocking defects.** The single largest recurring pattern in the
whole corpus (30 pieces of evidence, the largest evidence base of any
finding here). On SIMS #1842, #1918, the CRM Request Workspace, an
11-round Ripple build/review cycle, and the assessment-content bank, a
green focused test suite repeatedly missed real contract, security,
atomicity, or scoping defects that only surfaced under a fresh, independent
review. Recurring root causes: tests fully mocked with a shape that doesn't
match the real adapter, a concurrency test that deadlocks on its own
uncommitted transaction, and a DB dialect check that silently skips its own
assertions when it reads empty pre-connection. Confirmed (3/3), high
severity — release-blocking; "tests pass" has repeatedly not been
sufficient evidence for a completion claim, and the thing that actually
caught the real bugs was a second, differently-motivated reviewer, which is
exactly the mechanism the review/verify separation is supposed to provide
but isn't yet a hard requirement before a "ready" claim. *Fix:* require at
least one non-mocked/real-infrastructure test per release-blocking claim;
treat a green focused suite as necessary but not sufficient before a
completion or verified claim — concretizing what `no-mistakes-lite.md`
already says in principle for this specific failure mode. *Owner:*
[`verify.md`](verify.md), [`review.md`](review.md), and
[`agent-os-evals.md`](agent-os-evals.md).

**F12 — Fresh worktrees and sandboxed sessions repeatedly lack a working
dev/test environment.** Nearly every fresh git worktree starts with no
`node_modules`, no local test DB, or missing native tooling, forcing the
same setup gap to be rediscovered each session: a private test-DB instance
must be stood up from scratch each time (the shared test DB isn't safe to
use directly), a local MySQL client is missing a required auth plugin, and
scripts written to `/tmp` can't resolve dependencies. Confirmed (3/3),
medium severity, spanning 4 projects and multiple weeks — genuinely broad,
not isolated to one project. *Fix:* add an environment-bootstrap checklist
(private test DB setup, dependency-presence check, native tooling checks)
referenced from `verify.md` and `qa.md`. *Owner:*
[`parallel-work-and-worktrees.md`](parallel-work-and-worktrees.md).

**F13 — Deploy pipeline and production-access friction, plus recurring
product bug classes, lack a documented check.** Mechanically-similar deploy
failures keep costing time and are rediscovered ad hoc: a production SSH
key not registered mid-deploy, `sudo` preserving the wrong `HOME` and
breaking process-manager restarts, an Apache proxy silently routing a
domain to the wrong host (masking days of fixes that were never actually
served), and build-permission errors from root-owned artifacts (confirmed
across roughly 9 distinct sessions from May through August). Separately, the
same production bug classes recur without a regression test after the first
fix: duplicate class-scheduling in SIMS was fixed once in late June, then
independently again roughly three weeks later via a different code path;
and an integration-vs-backport route-skip warning recurred far more broadly
than first estimated (traced across roughly 70 distinct session files
spanning 3 months by one verifier). Confirmed (3/3), high severity given the
financial/production relevance — some of these bugs affect production
billing/class-count correctness directly, and the Apache-misroute item is a
genuine near-incident, not a minor annoyance. *Fix:* add a pre-deploy
checklist (SSH key registration, `sudo`/`HOME` handling, proxy verification,
storage permissions); add regression tests for the named recurring SIMS bug
classes so a fix earns permanent coverage the first time. *Owner:*
[`release-deploy-live-monitoring.md`](release-deploy-live-monitoring.md) for
the deploy checklist; [`qa.md`](qa.md) plus project `TESTING.md` manifests
for regression coverage.

### Workflow Weight

**F15 — Workflow feels too heavy, and orchestration fan-outs ignore real
shared resource limits.** Hafiz has repeatedly pushed back that step-by-step
gates are too slow on tightly-coupled work. Separately, Codex's own
self-audit found parallel multi-agent builds were not actually saving time
on tightly-coupled SIMS/Ripple work, and found real redundant internal work
(an eval self-test rerunning multiple times in one session). Independently,
orchestrator-generated research briefs assumed resources that didn't scale
with the fan-out — a large research wave told roughly 71 subagents to each
run 30-40 searches against one shared 200-call search budget, exhausting it
almost immediately, and an account-level rate limit killed 5 concurrent
research threads mid-run with real, named, unrecoverable lost work (not
just delayed). Confirmed (3/3), medium severity — real, self-measured
evidence that heavy sequential gating adds time without adding safety on
tightly-coupled work, and a real data-loss problem in the lost-research
-threads case, though not a correctness or safety failure. One verifier
corrected the stated cause of the lost-work event from "a fixed concurrency
cap" to "an account-level rate limit" — the lost-work event itself is real,
but that mechanism detail should be corrected in any follow-up. *Fix:*
remove redundant internal reruns; size fan-out briefs against the real
shared budget before dispatch (divide the total call budget by planned
agent count) rather than telling every agent to use the budget
"extensively." *Owner:*
[`agent-os-workflow-lanes.md`](agent-os-workflow-lanes.md) and the
`orchestrate` skill playbook.

---

## Koda Memory System Findings

Three confirmed themes, spanning the schema, transport, and usage-discipline
layers. Read together with [`agent-os-memory.md`](agent-os-memory.md), which
already defines most of the correct behavior — the gap in every case below
is that real sessions aren't consistently following what the doc already
says.

**F4 — `memory_store` rejects `category: "correction"` — a schema confusion
that recurs for weeks.** Codex sessions (and, less clearly, at least one
Claude session) have repeatedly called `memory_store` with
`category: "correction"`; Koda's schema only accepts
`decision | lesson | rule | preference | fact` as a category —
`"correction"` is a valid `source` value, not a `category` value.
`agent-os-memory.md` already documents this correctly, but nothing catches
the mistake client-side before the call goes out. Confirmed (3/3) for the
Codex-side pattern across at least 4 distinct dates spanning 6+ weeks, low
severity — each occurrence self-corrects in the same turn at the cost of
one wasted retry, but is trivially preventable. The one cited Claude example
turned out to be a different, distinct schema-confusion failure mode
(malformed tool-call serialization), not this exact mistake — the "both
tools" framing should be narrowed to primarily-Codex. *Fix:* add a
client-side enum check to `scripts/agent-checks/koda store` that
rejects/auto-corrects `category: "correction"` before the MCP call; make
the existing warning in `agent-os-memory.md` more prominent at the point of
the actual command example. *Owner:*
[`agent-os-memory.md`](agent-os-memory.md) (Required Fields / Koda CLI
section), cross-reference [`save-session.md`](save-session.md)'s Koda
schema list.

**F5 — Koda MCP transport hangs, times out, or registers stale (root-caused
and fixed 2026-08-13/14).** `memory_search`/`memory_store` repeatedly hung
or timed out at 120 seconds even when the health check reported healthy,
and Codex's MCP registration drifted between a stale bridge and direct HTTP
more than once. Root-caused to a long-lived managed MCP transport surviving
past a 5-minute idle timeout and holding a dead session open. Confirmed
(3/3) across at least 3-4 genuinely independent dated incidents over a
2.5-month window (one apparent duplicate was actually a Codex session-fork
replaying the same event into a second file), plus a genuine, detailed
2026-08-13 root-cause diagnosis session confirming the fix was applied.
Medium severity going forward specifically because the root cause is
already fixed — the value here is documenting it so the fix doesn't get
silently reverted or the lesson lost; this degraded agent reliability for
months before being fixed, and the health probe itself was misleading
during that whole period because it wasn't doing a real round-trip. *Fix:*
document the idle-timeout root cause explicitly; make the health probe an
actual `memory_search` round-trip, not a ping, so a regression of this
exact failure mode would be caught by the health check itself. *Owner:*
[`agent-os-memory-architecture.md`](agent-os-memory-architecture.md) (new
`koda-reliability` subsection).

**F6 — Koda is skipped where it matters most, and stored knowledge is stale
or unenforced when it is consulted.** Two bundled problems. First, Koda is
structurally missing from exactly the sessions where it would matter most:
`memory_store` is blocked while in plan mode with no documented
deferred-write behavior; a 16-issue batch session admitted afterward it
never ran the mandated per-issue search; at least one delegated worker
session's own injected instructions explicitly required a Koda search at
task start, yet made zero such calls. Second, even when Koda is consulted
it under-delivers: reading a memory silently bumps its own staleness
-tracking metric (corrupting the audit signal), 32+ memories still carry a
deprecated project tag already invalid per `agent-os-memory.md`'s own list,
and — most seriously — see "Immediate action needed" above. Confirmed
(3/3) — all three verifiers independently opened the 2026-08-16 self-audit
session and confirmed the deprecated-tag count, the plaintext-secret
finding, and the read-bumps-metric mechanism directly. High severity,
primarily because of the confirmed plaintext secret and the self-corrupting
audit mechanism, both integrity/security risks rather than pure workflow
friction. The delegated-worker "no Koda search made" sub-claim was the
weakest under verification: one verifier found strong direct corroboration
in a different real session than originally cited; the specific supporting
quote originally attached to this sub-claim could not be located in real
history by two other verifiers and appears to be a contamination artifact
from this verification exercise itself, not historical evidence — the
broader sub-claim held up via the independently-found session, but that
specific citation should not be trusted. *Fix, in priority order:* (1)
remove/rotate the plaintext-secret memories now, outside normal doc
process; (2) fix reads silently bumping staleness metrics; (3) run the
read-only audit `agent-os-memory.md` already requires before any bulk
retag, then retag/archive the deprecated-tag memories; (4) require explicit
memory search at delegated/subagent/plan-mode session boundaries, and
document deferred-write behavior for plan mode. *Owner:*
[`agent-os-memory.md`](agent-os-memory.md) for the search-discipline and
tag-audit fixes; the plaintext-secret remediation is flagged directly to
Hafiz as an out-of-band action, not a docs edit.

---

## Claude vs Codex Parity Findings

**F14 — Parity gaps in hooks, product-design workflow, and tool
inventory.** Multiple sessions independently surfaced concrete, not
theoretical, parity gaps: LLS only had one hook wired up, missing the
branch/commit/workflow/session/memory hooks other active projects have;
Codex's own self-assessment confirmed its lifecycle-hook behavior isn't
fully identical to Claude Code's; Codex initially lacked the
PRD/clarifier/UX-spec/build-prompt design chain Claude routinely uses; a
formal 4-test parity suite run on 2026-08-01 showed Claude passing only 1 of
4, including proposing invalid Koda project tags that `agent-os-memory.md`
already documents as wrong; and when Codex drives Claude as a subagent,
Claude can silently stall for 3-5+ minutes on large diffs with no visible
progress. Confirmed (3/3) for the core claim — the LLS hook-gap and the
1-of-4 parity-test failure are the two strongest-evidenced sub-claims and
alone establish the theme as real across a 2+ month window; the other
sub-claims are genuine, recurring phenomena but had weaker example-file
citation precision under verification. Medium severity — tracked, known
-shape parity gaps rather than a live incident, though the invalid-Koda-tag
failure doubles as a direct contributor to F6's stale-tag problem.
`agent-os-parity-contract.md`'s existing Current Gap Map already names
several of these gaps in principle; what this retrospective adds is live
confirmation with dates and transcripts that they are real, not
theoretical. *Fix:* close the LLS hook-suite gap; fix Claude proposing
invalid Koda project tags (a one-line correction against the documented
list); continue formalizing the Codex product-design phase chain per the
parity contract's existing special-case section; document a
timeout/watchdog convention for cross-tool delegation. *Owner:*
[`agent-os-parity-contract.md`](agent-os-parity-contract.md).

**Coverage gap in this section:** this pass checked "do Claude and Codex
behave the same" (parity) but not "does Codex have an equivalent mechanism
to this Claude-specific one, and does it share the same bug" for several
Claude-specific mechanics found elsewhere in this report — F1
(`test-coverage-gate.py`, a Claude Code `PreToolUse` hook), F2 (Claude
Code's auto-mode classifier specifically), and F18
(`inject-skill-context.py`, a Claude-only global hook). Whether Codex has
equivalent mechanisms, and if so whether they share the same bugs, was not
checked this round and should be the next retrospective's Section 5 target
before it can be called complete against its own stated goal.

---

## What's Working Well — Preserve These

Not every pattern in this corpus is friction. Several mechanisms are
functioning exactly as designed and should be protected from being
"simplified away" in future workflow-weight reductions (see F15):

- **The independent, fresh-context Codex review is doing its job.** F11's
  entire evidence base is, from another angle, proof the adversarial-review
  mechanism works — every release-blocking defect it surfaced was caught
  before shipping because a second reviewer looked with fresh eyes instead
  of trusting the first pass's green tests. The fix from F11 is "require
  this more consistently before a ready claim," not "the review step is
  broken."
- **The handback watchdog catches every miss it was tested against
  (F8).** In every verified instance, a missing handback file was correctly
  detected and triggered a redispatch, with no silent work loss. The fix
  needed is to make the check happen earlier, not to distrust the detection
  mechanism.
- **Self-correction under direct challenge is genuine, not defensive.**
  Across F16 and elsewhere, when Hafiz pushes back on a mistake, the agent
  consistently and immediately admits the specific error in plain language
  rather than justifying it — the correction loop `working-with-hafiz.md`
  asks for, actually happening in real transcripts.
- **The Koda transport bug got properly root-caused and fixed (F5).** The
  improvement loop working end-to-end: a real, months-long reliability
  problem was diagnosed to its actual mechanism and fixed at the source,
  with a documented incident report, rather than patched symptom-by
  -symptom.
- **Hook failures fall back to the correct source of truth.** F18's session
  -context misdetection was self-corrected both observed times by the agent
  reading `CLAUDE.md`/`AGENTS.md` directly rather than trusting the injected
  wrong hook context — confirming the "docs are the system, hooks only
  remind" layering in `agent-os-memory-architecture.md`'s memory model
  actually holds in practice.
- **Self-audit is genuinely catching Agent OS problems before Hafiz has
  to.** Both the 2026-08-01 Koda-tag parity-test failure and the 2026-08-16
  Koda health self-audit (deprecated tags, plaintext secret, metric
  corruption) were discovered by the system auditing itself, not an
  external complaint. The self-improve loop is functioning — the remaining
  gap is turning what self-audit finds into fixes fast enough (the
  plaintext secret sat there past its own outdated-flag).
- **Near-misses are being caught before they become incidents.** A
  branch-mismatch check in F10's evidence stopped a wrong-repository push
  before it happened — a safety check working exactly as intended.

---

## Prioritized Action List

Two independent axes: each finding's stated **severity** above (how much
harm/cost it causes) and each action's **bucket** here (how much effort the
fix takes). Bucketing tracks fix cost, not severity — a high-severity
finding with a cheap mechanical fix (F1) is a Quick Win; a lower-severity
finding whose fix needs new tooling (F17) is Structural. Within Quick Wins,
ordering follows severity/urgency first (the plaintext-secret item leads),
then groups by owner doc.

### Quick Wins (small, high-confidence, cheap to fix)

| # | Action | Owner doc / file | Finding |
|---|---|---|---|
| 1 | **Locate and remove/rotate the 8 creative-hub Koda memories holding a plaintext secret** — urgent, outside normal doc process | Koda directly, flagged to Hafiz | F6 |
| 2 | Fix `test-coverage-gate.py`'s Python type-hint compatibility bug | `.claude/hooks/test-coverage-gate.py`, [`agent-os-hook-dispatcher.md`](agent-os-hook-dispatcher.md) | F1 |
| 3 | Add a client-side enum check to `scripts/agent-checks/koda store` rejecting `category: "correction"` before the MCP call | [`agent-os-memory.md`](agent-os-memory.md) | F4 |
| 4 | Fix `inject-skill-context.py`'s Kelasapp worktree misdetection; add a fixture regression test; add the missing hook entry to `agent-os-hook-dispatcher.md` | `~/.claude/hooks/inject-skill-context.py`, [`agent-os-hook-dispatcher.md`](agent-os-hook-dispatcher.md) | F18 |
| 5 | Fix Claude proposing invalid Koda project tags | [`agent-os-memory.md`](agent-os-memory.md), [`agent-os-parity-contract.md`](agent-os-parity-contract.md) | F6, F14 |
| 6 | Scope the pre-commit guard's Mission Ledger check to files actually touched by the current change | [`commit.md`](commit.md), `docs/agent-playbooks/mission-ledger/*.md` | F3 |
| 7 | Document the Koda-transport idle-timeout root cause; make the health probe a real round-trip, not a ping | [`agent-os-memory-architecture.md`](agent-os-memory-architecture.md) | F5 |
| 8 | Fix the classifier's short-imperative-command handling (AO-002 already tests this and fails); add further short-imperative eval variants once fixed | [`agent-os-evals.md`](agent-os-evals.md), [`task-router.md`](task-router.md) | F10 |
| 9 | Add a health check that detects "a hook crashed on almost every call this session" | [`agent-os-evals.md`](agent-os-evals.md) | F1 |
| 10 | Fix memory reads silently bumping staleness-audit metrics | Koda service itself | F6 |

### Bigger Structural Changes (need design/discussion before implementation)

| # | Action | Owner doc / file | Finding |
|---|---|---|---|
| 1 | Require at least one non-mocked/real-infrastructure test per release-blocking claim; treat a green focused suite as necessary but not sufficient before a ready/verified claim | [`verify.md`](verify.md), [`review.md`](review.md), [`agent-os-evals.md`](agent-os-evals.md) | F11 |
| 2 | Add an environment-bootstrap checklist for fresh worktrees | [`parallel-work-and-worktrees.md`](parallel-work-and-worktrees.md) | F12 |
| 3 | Make the handback file a hard exit-gate for bounded/background workers | [`handoff.md`](handoff.md), [`agent-os-state-model.md`](agent-os-state-model.md) | F8 |
| 4 | Add a pre-deploy checklist (SSH key registration, `sudo`/`HOME`, proxy verification, storage permissions) | [`release-deploy-live-monitoring.md`](release-deploy-live-monitoring.md) | F13 |
| 5 | Add regression tests for the named recurring SIMS bug classes | [`qa.md`](qa.md), project `TESTING.md` | F13 |
| 6 | Define an explicit escalation/self-grant path for classifier-blocked-but-already-authorized actions | [`agent-os-approval-gates.md`](agent-os-approval-gates.md) | F2 |
| 7 | Promote the autopilot-boundary rule from documented guidance to an eval/fixture | [`working-with-hafiz.md`](working-with-hafiz.md), [`agent-os-approval-gates.md`](agent-os-approval-gates.md) | F16 |
| 8 | Add multi-worktree concurrency guidance (branch-collision pre-checks, `active.json` staleness detection, delegation-directory locking) | [`agent-os-state-model.md`](agent-os-state-model.md), [`parallel-work-and-worktrees.md`](parallel-work-and-worktrees.md) | F9 |
| 9 | Close the LLS hook-suite parity gap; formalize the Codex product-design phase-naming requirement; document a cross-tool delegation timeout convention | [`agent-os-parity-contract.md`](agent-os-parity-contract.md) | F14 |
| 10 | Require memory search at delegated/subagent/plan-mode boundaries; document deferred-store behavior for plan mode; audit and retag/archive deprecated-tag memories | [`agent-os-memory.md`](agent-os-memory.md) | F6 |
| 11 | Size orchestrator fan-out briefs against real shared resource budgets before dispatch width is chosen | [`agent-os-workflow-lanes.md`](agent-os-workflow-lanes.md), `orchestrate` skill | F15 |
| 12 | Extend `agent-os-response-shape-runner.py`'s `explanation_first` checks with a jargon-detection case | [`agent-os-communication.md`](agent-os-communication.md) | F17 |

---

*18 findings above were independently re-verified against raw session
transcripts by 3 adversarial reviewers before inclusion; several evidence
counts and file citations were found overstated or mismatched during
verification and are called out within each finding rather than smoothed
into a clean number. Full evidence (verbatim quotes, exact file citations,
per-finding verifier notes) is local-only at
`.local/agent-os-history-mining-2026-08-22/full-report-with-evidence.md`,
per the Real-Session Retrospective rule in
[`agent-os-improvement-loop.md`](agent-os-improvement-loop.md).*
