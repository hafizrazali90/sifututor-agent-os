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
- at least one project tag, usually `sifututor`
- a short `why` explaining why future sessions need it

For Agent OS memories, prefer tags such as:

```text
sifututor, agent-os, router, workflow, memory, guardrails, koda
```

## Source Selection

Use:

- `correction` when Hafiz corrects agent behavior or facts.
- `user-stated` when Hafiz states a preference, rule, or decision.
- `auto-captured` when the agent records a lesson learned from verified work.

Do not mark an agent inference as `user-stated`.

## Dedup First

Before storing:

1. Search Koda for the topic when the MCP path is working.
2. If a similar memory exists, update it instead of creating a duplicate.
3. If Koda MCP is timing out but direct health works, use the direct safe path
   or report that memory save is deferred.
4. If Koda is unavailable, include the durable lesson in the final response and
   note the fallback.

Koda CLI commands:

```bash
scripts/agent-checks/koda health
scripts/agent-checks/koda search '{"query":"<topic>","tags":["sifututor"],"limit":5}'
scripts/agent-checks/koda store '{"category":"lesson","content":"<memory>","project":"sifututor","source":"auto-captured","tags":["sifututor","agent-os"],"why":"<why future sessions need this>"}'
scripts/agent-checks/koda update '{"id":"mem_XXXX","content":"<safe corrected memory>","source":"correction","tags":["sifututor","agent-os"],"why":"<why this memory was corrected>"}'
```

Use the Koda CLI as the Codex-first memory path in this workspace. It uses the
same MCP HTTP endpoint and `KODA_API_KEY`, but avoids the chat-level
`mcp__memory` wrapper when that wrapper is unreliable. Do not print or paste
secret values.

Agent defaults:

| Agent | Koda path |
| --- | --- |
| Codex in this workspace | CLI-first |
| Claude Code | MCP-first if stable; CLI fallback if available and needed |
| Staff or general chat LLM | no Koda write access by default; use docs/local notes unless approved |
| Automation/scripts | CLI-first |

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

- project tag, such as `sifututor`
- domain tag, such as `agent-os`, `payment`, `qa`, `router`, or `koda`
- lifecycle tag, such as `lifecycle-active`, `lifecycle-superseded`,
  `lifecycle-stale`, or `lifecycle-archived`
- risk tag, such as `risk-critical`, `risk-normal`, or `risk-low`

Do not bulk migrate old memories without a read-only audit report first.
