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

## Relationship To Save Session

This playbook narrows the Koda rules for Agent OS work.

For full session wrap-up, still follow [save-session.md](save-session.md).
