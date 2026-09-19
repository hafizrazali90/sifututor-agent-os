# Codex To Claude Handoff

Use this as the human-readable brief referenced by a local copy of
`claude-delegation-job.json`. Keep the filled job file and worker state under
the worktree's ignored `.agent-os/delegations/` directory; do not commit runtime
state or raw conversations.

## Project

`<project-name>`

## Active Task

- Task id:
- Route:
- Current step:
- Task file:

## Delegation Contract

- Job id:
- Goal in one sentence:
- Approved stop point:
- Worktree and branch:
- Lane owner:
- Progress cadence:
- Forbidden actions:
- Required proof:
- Required MCP servers, or none:

## What Codex Changed

- Files changed:
- Why:
- Scope intentionally avoided:

## Evidence

- Commands run:
- Results:
- Guard status:
- Koda memories stored:

## Risks Or Open Questions

- Product/UX:
- Technical:
- Test gaps:

## Next Step For Claude

Resume from:

```text
<next step>
```

Read first:

- `AGENTS.md`
- `CLAUDE.md`
- `.claude/tasks/active.json`
- `<task file>`

## Required Return Contract

Write one handback file at the exact path named in the job JSON. It must contain:

- final worker state: returned, failed, waiting, or incomplete; report the
  worker-process outcome separately from the return-contract state
- plain-English summary of what changed
- exact changed-file inventory
- commands/checks run and their results
- failures, unavailable measurements, and unverified claims
- current branch, commit, dirty state, and highest proven product state
- whether the approved stop point was reached
- any decision or intervention still needed
- the single next action for independent Codex review

For delegated, cross-system, cross-module, user-facing, or AI-to-AI work, the
handback must also apply the [Builder Completion Proof
Contract](../agent-os-evidence-model.md#builder-completion-proof-contract), or
say plainly that it does not apply and why:

- the acceptance-to-proof map for every requirement
- the real entry point and every production caller exercised
- the bypass-path sweep disposition (legacy screens, alternate writers, jobs)
- the authoritative result and cross-system convergence after success or failure
- permission/configuration reachability for every supported role and mode
- flag-off/unavailable, retry, duplicate, stale, and recovery behavior
- one negative-control or failing-first proof, or a named gap
- that this is builder evidence, not independent acceptance

When the job's `builder_completion_proof.mode` is `required`, record every
item below as its own nonempty `field: value` line. These are structural
records for the runner and claims for the independent reviewer to challenge:

```text
acceptance_to_proof_map: <requirements mapped to evidence>
entrypoint: <normal entry and result>
production_caller: <real callers inspected or exercised>
authoritative_result: <owning state and convergence result>
bypass_paths: <search boundary and disposition>
permissions_configuration: <roles, ownership, and configuration result>
disabled_unavailable: <flag-off and unavailable behavior>
failure_retry: <failure, duplicate, stale, retry, and recovery result>
negative_control: <precise weaker behavior rejected>
journey: <real journey evidence or named gap>
regression: <permanent regression evidence>
builder_evidence_not_acceptance: true
```

Only a genuinely non-implementation task may use `mode: not_applicable`. Its
handback must contain `builder_proof_not_applicable: <reason>` exactly matching
the nonempty reason configured before launch. The worker cannot downgrade a
required contract after launch.

Do not include secrets, raw credentials, `.env*` values, or raw production data.
Do not claim acceptance from Claude's own review. Codex independently checks the
diff, evidence, scope, and next-state safety before Hafiz approves a later gate.
