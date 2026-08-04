# No-Mistakes-Lite

Use this before an agent says work is ready, commits, pushes, opens a PR,
merges, deploys, closes a task, or asks Hafiz to trust a next state.

Plain meaning:

```text
Before work moves outward or gets called done, pause once and ask:
Am I about to make Hafiz trust something that is not actually proven yet?
```

This is inspired by Kun Chen's `no-mistakes` idea, but it is intentionally
lighter. The first Sifututor version is a playbook gate that uses our existing
verify, QA, review, evidence, state, approval, and guardrail rules. It is not
yet a separate external automation pipeline.

## Why This Exists

Sifututor already has many strong checks:

- pre-commit guard
- verify
- QA
- review and risk checkpoint
- evidence model
- state ladder
- permanent E2E rule
- related-impact audit
- release/deploy monitoring rules
- Session Map and Session Release Ledger

The problem is not that each check is missing. The problem is that an agent can
run some checks, forget others, then report a stronger state than the evidence
proves.

No-mistakes-lite is the final honesty pass.

## When To Run It

Run it before:

- saying `ready`, `done`, `safe`, `merge-ready`, `deploy-ready`, or `live`
- commit
- push
- PR open
- PR merge
- staging or production deploy
- release close-out
- save-session or handoff after meaningful work
- any final answer where missing proof would mislead Hafiz

For tiny discussion-only answers, skip it. For small docs-only edits, use the
short version below.

## Short Version

For safe docs or Agent OS changes:

```text
1. Scope: are the changed files the intended files?
2. State: is it only changed locally, committed, pushed, or something else?
3. Checks: did the relevant docs/health/guard checks pass?
4. Memory: does Koda need the durable lesson?
5. Next: what should Hafiz do next?
```

## Full Gate

For product work, user-facing work, critical lanes, releases, multi-fix
sessions, or anything leaving local:

| Question | Practical meaning |
| --- | --- |
| What changed? | Can the agent explain the product/workflow change in plain English? |
| Is scope still correct? | Are all changed files inside the approved task? |
| What proof exists? | Tests, E2E, browser/mobile smoke, API checks, screenshots, logs, CI, or monitoring. |
| What proof is missing? | Missing evidence must be named before calling work ready. |
| Is a user journey affected? | If yes, code tests alone are not enough. |
| Is permanent E2E required? | Add/update it or name the valid exception and follow-up. |
| Did related-impact need a check? | Bugfixes, hotfixes, and user-facing small changes need the right related-impact audit. |
| Is there a critical lane? | Auth, payment, invoice, commission, migration, deploy, production data, and mobile API contracts need stronger gates. |
| Is release communication needed? | Staff-facing changes may need changelog, help text, What's New, or ops note. |
| Is this a multi-fix session? | Session Release Ledger must show no fix is stranded or overstated. |
| Is fresh-context review needed? | If this is user-facing, critical, outbound, complex, autonomous, or multi-fix work, review it like the builder's assumptions may be wrong. |
| What state is actually proven? | Changed locally, committed, pushed, PR open, merged, deployed, live checked, monitored, or accepted. |
| Is approval needed? | Push, PR, merge, deploy, destructive, production, critical-lane, and secret boundaries need explicit approval. |
| What is the recommended next action? | Hafiz should not have to ask "what next?" |

## State Honesty Rule

Never say only:

```text
Done.
Ready.
Looks good.
```

Say ready for what:

```text
Ready to commit locally.
Ready to push.
Ready for PR review.
Ready to merge.
Production deployed, but not monitored yet.
Changed locally, not committed yet.
```

If proof is missing, say the highest honest state:

```text
The backend test passed, but the browser journey is still unproven. This is
ready for code confidence, not ready for user-workflow confidence.
```

For a native Agent OS task with a visible finish line, compare that target with
fresh owner evidence during this honesty pass. When the strongest state changes,
run `agent-os-set-proven-state` with a short evidence pointer. Do not call the
finish line reached while current proof is lower. If the helper was unavailable
or did not confirm its update, say the visible current proof remains unchanged.

## Relationship To Existing Playbooks

No-mistakes-lite does not replace the existing playbooks.

| Existing playbook | What it owns | No-mistakes-lite asks |
| --- | --- | --- |
| `verify.md` | Does the implementation work technically? | Was the right verification actually run? |
| `qa.md` | Can a real user journey be trusted? | Is journey proof required and present? |
| `review.md` | Is it scoped, evidenced, safe, and honest? | Did review catch blockers before the next state, and did risky/outbound work get fresh-context review? |
| `commit.md` | How to stage and commit safely. | Is this truly commit-ready? |
| `push-pr-ci-automation.md` | How to automate push, PR, and CI inside an approved boundary. | Is the outbound boundary approved and evidence current? |
| `release-deploy-live-monitoring.md` | How to release, smoke, and monitor. | Is the live/deploy claim honest? |
| `save-session.md` | How to preserve state and lessons. | Is the handoff/ending state clear enough for the next session? |

## Stop Conditions

Stop before the next state when:

- required evidence is missing
- required tests/checks fail
- user-facing journey proof is missing without a valid exception
- permanent E2E decision is missing for a changed user workflow
- critical-lane approval or reviewer is missing
- push, PR, merge, deploy, destructive, or production approval is missing
- release communication is relevant but absent
- Session Release Ledger is required but stale or missing
- the agent cannot explain the highest proven state

Stopping does not mean failure. It means the agent is being honest about what
is proven.

## Output Shape

Keep the report natural, but make these points clear:

```text
Status:
Meaning:
Checked:
Missing or not applicable:
Highest proven state:
Recommended next:
Decision needed:
```

Use formal labels only when useful for commit, QA, audit trail, or handoff.

## Future Automation

Do not install or clone a full external `no-mistakes` system yet.

First, use this playbook manually through real Sifututor work. If it repeatedly
catches the same mistake, promote that part into a script, fixture, hook, or
stricter gate.

Good automation candidates later:

- required file/link presence
- state wording fixtures
- missing permanent E2E decision detection
- missing Session Release Ledger in multi-fix sessions
- pre-push/PR evidence summary generation
- release state report validation

Plain version:

```text
Stabilize the behavior first.
Automate the repeated parts later.
```
