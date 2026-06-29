# Agent OS Governance And Versioning

Use this when changing the Sifututor Agent OS itself.

Plain meaning:

```text
This is the change-control system for the Agent OS, so future agents do not
keep adding rules randomly until the OS becomes confusing.
```

Governance is not extra ceremony for ordinary work. It is the safety rail for
changing the safety rails.

## Core Rule

Every Agent OS change must answer:

```text
What kind of change is this?
Which source of truth owns it?
Which connected files need to agree?
What check proves the wiring still works?
What should be remembered?
What is the highest proven state: discussed, changed locally, committed,
pushed, or adopted?
```

Do not add the same rule in many places. Put the rule in the source-of-truth
file, then update adapters, skills, hooks, evals, health checks, Koda, or the
Session Map only when they depend on it.

## Change Types

| Type | Plain meaning | Main owner | Typical connected files |
| --- | --- | --- | --- |
| Small correction | Fix wording or a narrow behavior mistake. | Owning playbook or doc | Evals, Koda, Session Map if current |
| Workflow change | Change how agents should act in a route. | Owning workflow playbook | Skill wrapper, dispatcher, evals, README |
| System rule | Rule every agent must obey. | `AGENTS.md` | Owning playbook, guard/hook, evals |
| New workflow | Add a new repeated route. | New playbook | README, workflow map, manifest, health, evals |
| Adapter/parity change | Align Claude, Codex, or future LLM behavior. | Parity contract or skill registry | Adapter docs, skill files, hooks, parity runner |
| Guardrail/check change | Enforce or verify behavior. | Guard/hook/check script | Fixture runner, health, evals, docs |
| Memory correction | Fix durable memory behavior. | Koda plus memory docs | Koda fixture, memory architecture, save-session |
| Experiment | Capture a possible future improvement. | Mission Ledger or roadmap | Koda only if durable lesson exists |

## Source Of Truth Rule

Use the smallest reliable home:

- `AGENTS.md`: rules every agent must obey.
- `agent-os.md`: operating model or layer map changes.
- `agent-os-workflows.md`: workflow architecture and route sequence.
- Specific playbook: one workflow's actual steps.
- `agent-os-skill-registry.md`: skill/adapter catalog changes.
- `agent-os-parity-contract.md`: Claude/Codex/future LLM parity.
- Hook or guard docs/scripts: automation behavior.
- `agent-os-evals.md`: repeated behavior that should be tested.
- `agent-os-install-manifest.json`: distributable baseline file list.
- Koda: durable correction, lesson, rule, or preference.
- Session Map: current session story and return path.
- Mission Ledger: future or paused work not ready for implementation.

Plain version:

```text
Docs define. Skills guide. Hooks and guards enforce. Evals catch repeat drift.
Koda remembers. Session Map keeps the current story. Git proves exact changes.
```

## Required Path

1. State the behavior being changed in normal language.
2. Classify the change type.
3. Pick the source of truth.
4. Check the connected files for drift.
5. Explain what will change and what will not change before durable edits.
6. Update the smallest coherent file set.
7. Add or update eval/check coverage when the mistake can repeat.
8. Update Koda only for durable corrections, decisions, lessons, rules, or
   preferences.
9. Update the Session Map when this session's current focus or return path
   changes.
10. Run the checks for the changed layer.
11. Commit only after the exact file bundle is approved.
12. Push only when Hafiz explicitly asks in the current session.

## Check Matrix

| Changed layer | Required checks |
| --- | --- |
| Docs only | `git diff --check`, readback of affected links, pre-commit guard before commit |
| Core Agent OS docs | `agent-os-health.sh`, `workflow-doctor.sh`, eval self-test |
| Eval docs or runner | eval runner self-test, health |
| Hook or dispatcher | Python compile, conversation fixture runner, eval runner, health |
| Skill registry or parity | parity fixture runner, health |
| Install manifest or health file | JSON validation, install dry-run or health |
| Session Map | session-map checker and HTML generator |
| Koda behavior | Koda fixture runner, direct Koda health when available |

Use the lightest honest check set. Do not run product test suites for docs-only
Agent OS governance work unless the change touches product behavior.

## Versioning Model

Use Git as the exact version history:

- each coherent Agent OS change gets a focused commit
- commit messages use `docs(agent-os)`, `ci(agent-os)`, `test(agent-os)`, or
  another accurate scope/type
- local-only commits must be reported as local-only
- pushed commits are on GitHub, but not automatically adopted by future agents
  until the relevant docs/checks are in the pushed state they can read

Use Koda for durable memory, not exact version proof.

Use Session Map for current conversation continuity, not permanent version
history.

## Announcement Model

Not every Agent OS change needs a formal announcement.

Use this:

| Change size | Announcement |
| --- | --- |
| Tiny wording fix | Final close-out is enough. |
| Behavior correction | Final close-out plus Koda if durable. |
| Workflow change | Final close-out plus commit summary. |
| New workflow/playbook | Final close-out, Koda lesson, and next recommended use. |
| Breaking or safety-critical rule | `AGENTS.md`/playbook update, Koda correction, checks, and explicit note in close-out. |

If developer staff rollout is active later, decide separately whether a change
needs a developer-staff note. Until then, keep announcements inside Hafiz-agent
workflow close-outs.

## Done Means

For an Agent OS governance change, "done" must name the highest proven state:

- discussed only
- drafted locally
- changed locally and checked
- committed locally
- pushed to GitHub
- adopted in future sessions after the pushed docs/checks are available

Never say "the Agent OS now does X" if the change is only discussed or dirty in
the working tree. Say "the draft says X" or "committed locally, not pushed."

## Common Failures

| Failure | Correct behavior |
| --- | --- |
| Adding a rule to one doc when several adapters depend on it | Check the connected chain and update the smallest coherent set. |
| Saving only Koda for behavior that should guide agents | Put the rule in docs or playbooks; Koda remembers why. |
| Adding hooks for every preference | Use hooks for dangerous or easily checkable behavior; use playbooks/evals for judgment. |
| Duplicating long rules across many files | Put the rule once in the owner and link secondary files. |
| Saying a change is adopted when it is local-only | Report the highest proven Git state. |
| Letting old memories override newer docs | Treat old Koda as historical; update or supersede after verification. |

## Close-Out Shape

Use:

```text
Status:
<discussed / changed locally / committed locally / pushed>

Meaning:
<what future agents should now do differently>

Checked:
<exact governance checks>

Koda:
<stored / updated / skipped and why>

Recommended next:
<commit, push, use in next workflow, or continue to next governance topic>

Decision needed:
<yes/no; exact decision if yes>
```
