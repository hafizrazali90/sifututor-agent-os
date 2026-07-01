# Skill Quality And Pruning

Use this when deciding whether to create, update, merge, park, or delete an
Agent OS skill, playbook, workflow doc, hook, or eval.

Plain meaning:

```text
The Agent OS should get smarter without becoming a pile of rules.
Every new skill or doc must earn its place.
```

This playbook exists because Sifututor Agent OS now has enough docs and skills
that the main risk is sprawl: agents may miss the right rule, duplicate an old
one, or make the workflow feel heavier than the work.

## Core Rule

Before adding a skill or playbook, ask:

```text
Does this create a clearer route, stronger proof, safer boundary, or easier
continuation than updating an existing owner?
```

If the answer is no, do not create a new thing.
Update the existing owner instead.

## The Five Outcomes

Every proposed Agent OS addition should end in one of these outcomes:

| Outcome | Use when | What to do |
| --- | --- | --- |
| Update | An existing playbook already owns the behavior. | Edit that playbook and link any secondary docs back to it. |
| Create | The behavior is repeatable, distinct, and needs its own route or source of truth. | Add a playbook, registry entry, route link, eval, and checks. |
| Merge | Two docs or skills answer the same workflow question. | Choose one owner, move useful content there, and turn the other into a pointer or remove it when safe. |
| Park | The idea is useful later but not part of the current core. | Record it in Mission Ledger, roadmap, or a parked section with a return condition. |
| Delete | The artifact is obsolete, misleading, duplicated, or unsafe and no longer needed. | Remove it only after checking references and explaining the replacement. |

Non-technical version:

```text
Do we improve the existing manual, write a new manual, combine two manuals,
put the idea on the shelf, or throw away the old manual?
```

## When To Create A New Skill

Create a new skill only when most of these are true:

- Hafiz or agents repeat the same kind of work often.
- The work has a clear trigger.
- The work has a different evidence path, approval boundary, or stop point from
  existing skills.
- The instructions would make an existing playbook too large or confusing.
- The behavior needs reliable discovery by Claude, Codex, or future LLMs.
- The route can be tested with evals, fixtures, health checks, or real use.

Examples that deserve skills:

- commit
- verify
- QA
- save-session
- workflow improvement
- production monitoring

Examples that usually do not deserve a new skill:

- one-off preference wording
- a single project-specific command
- a temporary research topic
- an idea not yet used in real workflow
- a rule that belongs in `AGENTS.md`
- a durable lesson that belongs only in Koda

## When To Update Instead

Update an existing skill/playbook when the new behavior is a refinement of the
same job.

Examples:

| New behavior | Update |
| --- | --- |
| Commit close-out should say the next action. | `commit.md` and communication checks. |
| Agent should read UI/UX docs before SIMS UI work. | `task-router.md` and doc routing. |
| Agent should distinguish local commit from pushed state. | `agent-os-state-model.md`, `commit.md`, and close-out rules. |
| Agent should not add co-author. | `commit.md` and general guidelines. |

Plain rule:

```text
If the user would expect the same command or natural-language request to handle
it, update the existing workflow.
```

## When To Merge

Merge docs or skills when they create duplicate decision points.

Signs of duplication:

- two docs claim to be the source of truth for the same route;
- the agent must read both to know one workflow;
- one doc repeats another doc instead of linking to it;
- evals cannot clearly say which file owns the behavior;
- Hafiz asks "why do we have both?"

Merging does not always mean deleting immediately.
For safety:

1. Choose the owner.
2. Move missing useful rules into the owner.
3. Convert the secondary doc into a short pointer when external links may still
   exist.
4. Delete the secondary doc only after references are updated and checks pass.

## When To Park

Park instead of implementing when an idea is valid but not needed now.

Good parked items:

- staff rollout beyond current readiness;
- optional terminal/editor environment setup;
- future automation after manual rules prove useful;
- external tool adoption that needs a pilot;
- ideas that require business or team policy.

Parking requires:

- where it is parked;
- why it is not active now;
- what would make us return to it;
- who owns the decision.

## When To Delete

Delete only when the artifact is clearly obsolete or harmful.

Before deleting:

```bash
rg "file-or-skill-name"
```

Then confirm:

- no active skill wrapper points to it;
- no README/router/registry reference still needs it;
- no eval or health check expects it;
- no current Session Map depends on it;
- the replacement is clear.

Do not delete historical session saves just because they are old.
Mark them historical or reference-only unless they are actively misleading.

## Quality Checklist

Every active skill/playbook should have:

| Requirement | Why it matters |
| --- | --- |
| Clear trigger | Agents know when to use it. |
| Source owner | One file owns the behavior. |
| Plain-language meaning | Hafiz can understand what it does. |
| Scope boundary | The skill does not silently do more than expected. |
| Evidence/check rule | The agent knows how to prove the workflow. |
| Stop point | The agent knows where to pause. |
| Registry or index entry | Future agents can discover it. |
| Eval/check coverage when useful | Repeated mistakes are caught. |

If a skill/playbook lacks three or more of these, do not expand it.
Repair the quality first.

## Pruning Review Rhythm

Run a pruning review when:

- a new skill is proposed;
- a workflow doc crosses into another workflow's responsibility;
- Hafiz says the Agent OS feels confusing or too heavy;
- an agent misses a doc because there are too many similar docs;
- a release/push batch contains several Agent OS docs with unclear ownership.

Use this short review:

```text
What problem does this solve?
Who owns it?
Does an existing doc already solve it?
What should be updated, created, merged, parked, or deleted?
How will future agents find it?
How will we know it worked?
```

## Anti-Sprawl Rules

- Do not create a new skill because a concept has a catchy name.
- Do not create a new doc when a section in the owner doc is enough.
- Do not duplicate the same rule across many files.
- Do not turn a preference into a hard gate unless the mistake is expensive.
- Do not make hooks enforce judgment-heavy rules before the playbook/eval shape
  is proven.
- Do not leave a new workflow without a registry/index entry.
- Do not call the Agent OS "improved" if future agents cannot discover the
  improvement.

## Close-Out

When changing skills or playbooks, report:

- whether you updated, created, merged, parked, or deleted;
- the source owner;
- what future agents should do differently;
- what checks passed;
- whether Koda was updated;
- whether the change is local, committed, or pushed.
