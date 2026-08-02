# Agent OS Improvement Loop

Use this when Hafiz asks to improve the Agent OS itself, fix workflow behavior,
make future agents handle something better, or prevent a repeated agent mistake.

Plain meaning:

```text
This is how the Agent OS gets better without becoming a pile of random rules.
```

This playbook is for improving the operating system around the agents. It is
not for fixing product bugs. Product bugfix quality belongs to the normal
diagnose, verify, QA, review, and future related-impact audit workflows.

## Core Rule

Do not fix Agent OS behavior in only one place unless one place truly owns it.

Use this loop:

```text
notice -> classify -> choose owner -> check connected files -> explain
-> update -> test -> remember -> close out
```

In normal words:

```text
First understand the workflow mistake. Then update the layer that owns the
behavior, check the nearby layers that depend on it, prove the wiring still
works, and leave a clear trail for future agents.
```

## When To Use

Use this playbook when Hafiz says things like:

- `improve the workflow`
- `fix this Agent OS behavior`
- `make future agents handle this better`
- `why did this happen again`
- `this is confusing`
- `Claude and Codex are behaving differently`
- `the skill/hook/workflow is not doing what we agreed`

Also use it when an agent notices repeated or expensive workflow drift.

Do not use it for:

- normal product implementation
- ordinary bugfixes
- user-facing QA
- production incidents
- one-time wording preferences that do not change future behavior

## Mistake Types

Classify the problem before editing.

| Mistake type | Meaning | Likely owner |
| --- | --- | --- |
| Communication | Hafiz did not get clear meaning, checks, state, or next action. | `agent-os-communication.md`, `working-with-hafiz.md`, response-shape checks |
| Routing | The agent picked the wrong workflow or misunderstood `proceed`, `approve`, `go next`, or `what next`. | `task-router.md`, `agent-os-routing-model.md`, evals, hook dispatcher |
| Approval | The agent asked too often, bundled too much, or crossed a boundary. | `agent-os-approval-gates.md`, `AGENTS.md`, commit/review playbooks |
| Memory | Koda was noisy, stale, missing, or treated as proof. | `agent-os-memory.md`, `agent-os-memory-architecture.md`, Koda fixtures |
| State | The agent mixed local, pushed, PR, merged, deployed, or live states. | `agent-os-state-model.md`, session ledger, close-out docs |
| Skill/playbook drift | A skill wrapper, playbook, or registry disagrees. | `agent-os-skill-registry.md`, `.agents/skills/*`, shared playbook |
| Hook/automation drift | A hook routes, blocks, or reminds incorrectly. | `agent-os-hook-dispatcher.md`, lifecycle hook, conversation fixtures |
| Eval/check gap | The mistake can repeat because no check catches it. | `agent-os-evals.md`, eval runner, fixture runners, health checks |
| Claude/Codex parity | Claude and Codex expose different behavior for the same workflow. | `agent-os-parity-contract.md`, skill registry, adapter docs |
| Workflow weight | The system is too heavy, too loose, or too annoying. | `agent-os-workflow-lanes.md`, workflow docs, Hafiz working model |

## Owner Decision

Use the lightest reliable home:

| If the fix is mainly... | Put it here |
| --- | --- |
| A durable lesson or correction | Koda, plus docs if behavior must change |
| A shared rule | `AGENTS.md` or the owning playbook |
| A repeated workflow path | A playbook and skill wrapper |
| A command/adapter gap | Skill registry, parity contract, Codex skill, Claude command |
| A dangerous action | Guard, hook, or hard rule |
| A repeated behavior mistake | Eval or fixture |
| Current-session continuity | Session Map |

Plain rule:

```text
Koda remembers. Docs define. Skills guide. Hooks remind or block. Evals catch
repeat mistakes. Health checks prove the wiring.
```

## Connected File Check

After choosing the owner, check only the relevant connected files. Do not scan
the whole workspace by default.

Common chains:

| Problem | Check these first |
| --- | --- |
| Agent did not explain next action | `agent-os-communication.md`, `working-with-hafiz.md`, `commit.md` or active playbook, response-shape runner |
| Wrong route selected | `task-router.md`, `agent-os-routing-model.md`, `agent-os-evals.md`, lifecycle hook |
| New workflow skill needed | `agent-os-skill-registry.md`, `.agents/skills/*`, `agent-os-workflows.md`, `README.md`, install manifest |
| New doc, duplicate doc, or skill sprawl | `skill-quality-and-pruning.md`, `doc-owner-route-index.md`, `agent-os-skill-registry.md`, `README.md`, evals |
| Claude/Codex mismatch | `agent-os-parity-contract.md`, registry, shared playbook, both adapters |
| Memory behavior wrong | `agent-os-memory.md`, memory architecture, Koda fixtures, Koda search/update |
| Hook behavior wrong | hook dispatcher doc, fixture first, hook code second |

## Real-Session Retrospective

Use real Claude/Codex transcripts when Hafiz asks for a broad Agent OS audit or
when deterministic fixtures pass but the same daily-use friction continues.
This is an evidence source, not a new source of truth.

Run the privacy-safe aggregate first:

```bash
python3 scripts/agent-checks/agent-os-transcript-retrospective.py
```

The retrospective must:

- inventory the full requested transcript scope instead of sampling only easy
  or recent files;
- stream large JSONL records and avoid loading whole histories into memory;
- separate human prompts from hooks, scheduled prompts, compaction summaries,
  skill injections, tool results, and forwarded message drafts;
- deduplicate replayed Codex rollovers/forks before comparing counts;
- redact credentials, email addresses, URLs, tokens, and local paths before any
  excerpt is persisted;
- use aggregate trends to find candidates, then manually review representative
  high-signal turns before declaring a root cause;
- compare recent behavior with older periods so already-fixed drift is not
  presented as current failure.

Raw conversations must never be committed, copied into Koda, pasted into an
issue, or used as a routine health-check artifact. Optional redacted detail
reports are local diagnostic evidence only. Transcript availability also
differs by adapter and machine, so the retrospective is on-demand evidence;
its self-test belongs in health, but a full history scan does not.

Report coverage and depth separately:

```text
Coverage: every available transcript file was parsed, filtered, and
deduplicated.

Depth: aggregate patterns were measured and representative high-signal turns
were manually reviewed.
```

Do not say every transcript was fully analyzed, semantically reviewed, or read
word-for-word unless that stronger review actually happened. Full corpus
processing is not the same as manual semantic review of every conversation.

When redacted local details are enabled, use the retrospective's deduplicated
`manual_review_ranking` to choose session-level review candidates. The score is
triage only, not a failure verdict. Read correction, repeat-friction,
explanation, stop/redirect, and paired agent-response evidence in context; mix
high-ranked historical sessions with recent sessions so one old long-running
chat does not dominate the conclusions.

## Required Explanation Before Editing

Before changing durable Agent OS files, explain:

- what behavior is wrong
- why it matters to Hafiz or future agents
- which source of truth owns it
- which connected files will be checked or updated
- what will not be touched
- how it will be checked
- whether Koda needs a memory

This keeps Hafiz in control without forcing him to read the diff manually.

## Update Rules

When updating:

- make the smallest coherent change
- avoid duplicate rules in many files
- link secondary files back to the source of truth
- use `skill-quality-and-pruning.md` before creating or splitting skills,
  playbooks, hooks, evals, or workflow docs
- update `doc-owner-route-index.md` when a new active Agent OS doc is added or
  ownership changes
- add an eval or fixture when the mistake is repeated, expensive, or easy to
  check
- update the skill registry when a skill changes or is added
- update the install manifest when distributable baseline files change
- update the Session Map when the current session direction changes
- save Koda only for durable behavior-changing lessons or corrections

Do not:

- create hook automation before the playbook/skill/eval shape is clear
- treat every preference as a hard-blocking rule
- save vague progress notes to Koda
- let old Koda memory override current docs or repo state
- mix this with product bug related-impact audits

## Checks

Run focused checks while editing, then one full owner at completion. Do not run
`agent-os-health.sh` immediately before `workflow-doctor.sh`: the doctor already
runs health internally, and health already runs the deterministic eval and
fixture suite.

For documentation and skill-wrapper changes, the completion sweep is:

```bash
git diff --check
scripts/agent-checks/workflow-doctor.sh
```

For hook or dispatcher changes, run these focused checks during development:

```bash
scripts/agent-checks/agent-os-conversation-fixture-runner.py
scripts/agent-checks/agent-os-eval-runner.py
python3 scripts/agent-checks/agent-os-transcript-retrospective.py --self-test
```

For Koda helper changes, run:

```bash
python3 -m unittest discover -s scripts/agent-checks -p 'test_codex_koda_integration.py'
scripts/agent-checks/agent-os-koda-fixture-runner.py
```

For skill registry, parity, or installer changes, run this focused check while
editing:

```bash
scripts/agent-checks/agent-os-parity-fixture-runner.py
```

At completion, `workflow-doctor.sh` is the only full sweep. Run
`agent-os-health.sh` alone only when the project/environment sweep performed by
the doctor is intentionally unnecessary.

Before commit:

```bash
scripts/agent-checks/pre-commit-guard.sh
```

## Close-Out

End with:

- what behavior future agents should do differently
- what files changed
- what checks passed
- Koda stored/updated/skipped and why
- whether the change is local, committed, pushed, or still only discussed
- the next recommended action

## Example

Hafiz says:

```text
You committed but did not guide me what next.
```

The agent should classify it as:

```text
communication mistake + commit close-out gap + eval/check gap
```

Then it should check:

```text
agent-os-communication.md
commit.md
AGENTS.md close-out rule
.agents/skills/commit/SKILL.md
agent-os-evals.md or response-shape checks
Koda
Session Map
```

The fix should explain the new behavior in plain language and add a check if
the mistake should not quietly return.
