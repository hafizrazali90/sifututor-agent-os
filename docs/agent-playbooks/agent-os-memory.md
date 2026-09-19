# Agent OS Memory

Use this playbook when deciding whether an Agent OS lesson belongs in Koda.

Koda is the Agent OS episodic memory. It stores distilled lessons from past
work so future sessions do not repeat mistakes. It is not a transcript archive
and not a replacement for `AGENTS.md`, playbooks, task files, or git history.

## Core Rule

Save only memories that should change future behavior.

If the note would not help a future Codex, Claude, or Hafiz make a better
decision, do not store it in Koda.

## Memory Types And Homes

| Memory type | Home | Koda role |
| --- | --- | --- |
| Working | current chat, active task, scratch notes | none |
| Semantic | `AGENTS.md`, `CLAUDE.md`, README, docs, `TESTING.md` | reference only |
| Procedural | playbooks, skills, scripts, templates | reference only |
| Episodic | Koda, save-session, handoff, snapshot | primary durable store |

## Save To Koda

Save:

- Hafiz corrections
- approved workflow decisions
- repeated mistakes we want to prevent
- non-obvious implementation lessons
- tool behavior lessons
- context authority corrections
- critical-lane lessons after safe diagnosis or implementation
- router, guard, hook, skill, or playbook behavior lessons
- project-specific gotchas that will matter next time

Examples:

- "Discussion prompts about commit mistakes must not trigger `$commit`."
- "Koda memory about an old workaround must be checked against current files
  before acting."
- "FIUU declined callbacks must not mutate paid invoice state."

## Do Not Save To Koda

Do not save:

- raw chat transcripts
- secrets, tokens, credentials, `.env*` values, or private payloads
- temporary branch names unless the branch itself is the decision
- vague progress notes
- full command output with no durable lesson
- every file touched
- speculative ideas not yet accepted
- duplicate memories when an existing memory should be updated
- production data or customer private messages

## Required Fields

Every memory must include:

- `category`: `decision`, `lesson`, `rule`, `preference`, or `fact`
- `source`: `user-stated`, `auto-captured`, or `correction`
- at least one project tag from the approved project list below
- a short `why` explaining why future sessions need it

## Project Tags Versus Domain Tags

These are two different things. Every memory needs a project tag. Domain tags
are optional extras that never replace it.

| Tag kind | Purpose | Required? | Allowed values |
| --- | --- | --- | --- |
| Project tag | Says which product or workspace the lesson belongs to. | Yes, at least one. | The project list in [save-session.md](save-session.md): `sifu-tutor`, `ripple-suite`, `sifututor_tutor`, `sifututor_parent`, `lls`, `lls-frontend`, `lls-mobile`, `creative-hub`, `team-inbox`, `finch-inbox`, `sifututor`, `codex-parity`. |
| Domain tag | Says what the lesson is about. | No, but usually helpful. | Free-form topic tags such as `agent-os`, `router`, `workflow`, `memory`, `guardrails`, `koda`, `payment`, `qa`. |

For umbrella Agent OS work that is not owned by one product, use `sifututor`
or `codex-parity` as the project tag.

Plain meaning:

```text
A domain tag such as agent-os, payment, or qa is not a project tag. A memory
tagged only agent-os is missing its required project tag.
```

`umbrella` is not a valid project tag. Do not invent new project tags; if a new
project genuinely needs one, add it to the save-session project list first.

For Agent OS memories, a good tag set looks like:

```text
sifututor, agent-os, router, workflow, memory, guardrails, koda
```

Here `sifututor` is the required project tag and the rest are domain tags.

## Source Selection

Use:

- `correction` when Hafiz corrects agent behavior or facts.
- `user-stated` when Hafiz states a preference, rule, or decision.
- `auto-captured` when the agent records a lesson learned from verified work.

Do not mark an agent inference as `user-stated`.

## Dedup First

Before storing:

1. Search Koda for the topic through the direct CLI/helper path.
2. If a similar memory exists, update it instead of creating a duplicate.
3. For Codex, do not rely on the chat-level `mcp__memory` wrapper.
4. If Koda is unavailable, include the durable lesson in the final response and
   note the fallback.

Koda CLI commands:

```bash
scripts/agent-checks/koda health
scripts/agent-checks/koda health --write-check
scripts/agent-checks/koda search '{"query":"<topic>","tags":["sifututor"],"limit":5}'
scripts/agent-checks/koda store '{"category":"lesson","content":"<memory>","project":"sifututor","source":"auto-captured","tags":["sifututor","agent-os"],"why":"<why future sessions need this>"}'
scripts/agent-checks/koda update '{"id":"mem_XXXX","content":"<safe corrected memory>","source":"correction","tags":["sifututor","agent-os"],"why":"<why this memory was corrected>"}'
```

Use the Koda CLI as the Codex-first memory path in this workspace. It uses the
same MCP HTTP endpoint and `KODA_API_KEY`, but avoids the chat-level
`mcp__memory` wrapper. Do not install the Codex `memory` MCP unless Hafiz
explicitly reverses this decision. Do not print or paste secret values.

`koda health` is read-only. SessionStart owns the once-per-session read/write
probe; use `koda health --write-check` only for startup/setup repair or when the
write path itself must be proved. Do not rerun health after every prompt.

`koda store` performs an exact-content search first. If the same normalized
content already exists, it returns the canonical memory ID and skips the new
write. Use `koda update` when the existing memory needs correction or sharper
wording. Similar-but-not-exact memories still require the normal human dedup
decision.

## Executable Memory Discipline Check

Run this local fixture check when changing Agent OS memory rules:

```bash
scripts/agent-checks/agent-os-koda-fixture-runner.py
```

This check does not write to Koda. It validates the memory discipline rules
locally: allowed schema values, project tags, secret-like content rejection,
vague-progress rejection, stale-memory handling, and CLI fallback behavior when
chat MCP is unreliable.

Agent defaults:

| Agent | Koda path |
| --- | --- |
| Codex in this workspace | CLI-first |
| Claude Code | MCP-first if stable; CLI fallback if available and needed |
| Staff or general chat LLM | no Koda write access by default; use docs/local notes unless approved |
| Automation/scripts | CLI-first |

When Claude's Koda MCP is missing or unavailable inside a workspace session,
use the approved workspace helper's `scripts/agent-checks/koda search` path for
the required read-only lookup. The helper owns credential handling. Never ask
Hafiz to set, paste, export, or expose `KODA_API_KEY`, and never treat a missing
chat-level MCP tool as proof that Koda itself is unavailable.

If a memory is found to contain a secret, raw token, credential, or private
payload, update or remove it immediately through the safe path. Do not quote the
secret in chat, docs, commits, or follow-up memories.

## Memory Shape

Good memory:

```text
Sifututor Agent OS router lesson: discussion, learning, research, analysis, and
retrospective prompts must not be routed by keyword alone. The lifecycle hook
uses a discussion-mode bypass before action routing, and commit routing uses
narrower commit-intent patterns.
```

Bad memory:

```text
Updated router today.
```

Good memory:

```text
Hafiz prefers Codex to present full analysis first, let Hafiz comment and
decide, then execute. This applies especially to workflow and design changes.
```

Bad memory:

```text
Hafiz said ok.
```

## When To Save

Save immediately when:

- Hafiz gives a correction
- Hafiz approves a new durable workflow rule
- an Agent OS eval reveals a repeated failure pattern
- a tool behaves differently than expected
- a critical-lane lesson changes future safety behavior

Save before closing when:

- workflow docs, hooks, skills, or guards changed
- a session produced a reusable lesson
- a handoff would otherwise lose important context

Skip Koda when:

- the work was a trivial typo or formatting change
- the repo docs already fully capture the decision and no future behavior
  change is needed
- the idea is still being debated

## Close-Out Language

When Agent OS memory mattered, report:

```text
Koda: stored/updated/skipped/failed
Reason: <why>
Memory type: episodic lesson / correction / decision / preference
Fallback: <none | doc path | final response>
```

If the direct fallback was used, say so plainly:

```text
Koda: stored through CLI because the chat memory tool timed out.
```

## Relationship To Save Session

This playbook narrows the Koda rules for Agent OS work.

For full session wrap-up, still follow [save-session.md](save-session.md).

## Memory Architecture v2

Use [agent-os-memory-architecture.md](agent-os-memory-architecture.md) as the
source of truth for the upgraded memory structure.

The short model is:

```text
Docs store the system.
Koda stores the lesson.
Chat stores the moment.
Git stores the proof.
```

New Agent OS memories should prefer sharper tags:

- project tag, such as `sifututor` (required; see Project Tags Versus Domain
  Tags above)
- domain tag, such as `agent-os`, `payment`, `qa`, `router`, or `koda`
  (optional; never a substitute for the project tag)
- lifecycle tag, such as `lifecycle-active`, `lifecycle-superseded`,
  `lifecycle-stale`, or `lifecycle-archived`
- risk tag, such as `risk-critical`, `risk-normal`, or `risk-low`

Do not bulk migrate old memories without a read-only audit report first.

## Verify accepted writes

Repository integration: the shared lifecycle hook now routes store/update through
the verification module. Permanent CLI tests exercise all three entrypoints;
the install manifest and health runner include the implementation and tests.
This does not by itself prove installed adapters were updated or a live server
write was verified. Check the release evidence before claiming either.

An accepted write is not proof that the saved record matches the request.
The `koda_write` client verifies `memory_store` and `memory_update` by calling
`memory_recall` with the exact returned ID. It compares supplied supported
fields, treats tags as an unordered set, and does not invent expectations for
omitted server defaults. A duplicate result also needs exact-ID verification;
it is an existing record, never a newly verified save.

The client returns safe JSON metadata and exit status:

| Verification state | Exit | Meaning |
| --- | --- | --- |
| `verified` | 0 | Supplied supported fields matched at readback time. |
| `persisted_but_mismatched` | 1 | A record was read, but named fields differ. |
| `verification_unavailable` | 1 | The contract could not be fully checked. |

Always inspect `write_outcome`: `accepted`, `existing_record`, `unknown`,
`rejected`, or `not_attempted`. Exit 1 does **not** mean no write occurred.
Keep `id`/`existing_id` for reconciliation. Do not automatically retry a write,
retag, confirm, or repair a record; a concurrent edit or ownership denial is
not permission to overwrite it. Diagnostics contain field names and safe IDs,
never requested/stored values, raw errors, or provider payloads.

The inspected server accepts `scope` on store but does not expose it on recall.
An explicit scope request therefore remains `verification_unavailable` unless
a future compatible read response exposes scope. Do not infer scope from
creator, project, tags, or visibility. Store does not support `confidence`;
update does not support category/project/scope. Unsupported fields are rejected
before writing. Omitted fields remain server defaults, outside the verification
claim. See [memory architecture](agent-os-memory-architecture.md) for ownership
and rollout boundaries.

One empty broad search is not evidence that no memory exists. Retry narrower
individual task topics with the **same project and scope constraints**. Do not
relax filters to obtain results or interpret an unavailable search as empty.
