# Push, PR, CI, And Merge Automation

Use this when Hafiz asks whether pushing, opening a PR, watching CI, approving,
or merging can be automated.

Plain meaning: automate the mechanical work, but keep authority clear. The
agent can prepare, push, open, monitor, summarize, and fix in-scope CI failures
inside an approved boundary. It must not pretend to be Hafiz, silently approve a
review, merge, deploy, or change production state without the boundary Hafiz
approved in the current session.

## The Two Kinds Of Automation

| Kind | What it means | Default |
| --- | --- | --- |
| Mechanical automation | Repetitive agent work: prepare branch, push, open PR, write PR body, monitor CI, summarize results, diagnose in-scope CI failures. | Recommended when the boundary is clear. |
| Authority automation | Decisions that change shared state or accept risk: PR approval, merge, deploy, production action, destructive action, critical-lane implementation. | Boundary-based only; never silent. |

The easy version:

```text
The agent can do the boring steps.
Hafiz still owns the risk decision.
One clear approval can cover many boring steps.
```

## Recommended Boundaries

| Hafiz says | Agent may do | Agent stops before |
| --- | --- | --- |
| `proceed until PR ready` | Review risk, run required checks, commit if exact bundle is approved, push branch, open PR, fill PR body, monitor CI, fix in-scope CI failures, report PR state. | Merge, deploy, production, destructive action, critical-lane widening. |
| `proceed until PR open` | Same as PR ready, but stop once the PR exists even if CI is still running. | CI-fix work unless separately approved by the boundary. |
| `proceed until merged if CI passes` | Do the PR-ready path, wait for CI, merge only when the branch rules allow it, no blocking review/risk findings remain, and the task is non-critical. | Deploy, production, destructive action, critical-lane work. |
| `proceed until pushed` | Review risk, run required checks, push exact approved branch/commits, report remote state. | Open PR, merge, deploy. |
| `one by one` | Ask before each major outbound boundary. | The next unapproved boundary. |

If Hafiz says a looser phrase such as `finish this`, `do everything needed`, or
`proceed until done`, the agent should translate it into one of the boundaries
above before acting. Example:

```text
For this task, "done" can mean PR ready. I can continue until the PR is opened,
CI is checked, and any in-scope CI failure is fixed. I will stop before merge or
deploy unless you explicitly include that boundary.
```

## What Can Be Automated After One Approval

The agent may include these in one approved PR-ready packet:

- final local review and state inventory
- required guards, tests, and docs checks
- exact commit, when the file list and commit message are already named
- branch push
- PR creation
- PR title/body/checklist
- CI polling or check summary
- in-scope CI diagnosis and fix
- final plain-language PR review for Hafiz

The agent should not ask Hafiz to approve each small step in that packet.

## What Must Stay Explicit

These are separate authority decisions unless the current-session boundary
explicitly includes them:

- merge
- deploy
- production smoke that requires a write or state mutation
- destructive cleanup
- critical-lane implementation or widening
- force push, reset, rebase, or history rewrite
- reading or exposing secrets
- changing `.env*` or `live/`

PR approval needs special care. The agent may record that Hafiz approved the PR
in chat and may act on that approval if the merge boundary includes it. The
agent should not submit a GitHub review as Hafiz or use review approval as a
fake second reviewer.

## CI Behavior

CI is mechanical evidence, so the agent should automate it where possible:

1. After PR creation or push, check the CI status.
2. If CI is still running, say it is waiting and keep polling when the boundary
   includes CI monitoring.
3. If CI fails, read the logs, explain the practical meaning, and fix only when
   the failure is clearly inside the approved scope.
4. If the failure is unrelated, flaky, infrastructure-only, critical-lane, or
   requires new scope, report it and recommend the next action.
5. Do not call the work merge-ready until CI and required local evidence match
   the claimed state.

## Before Merge

Before merging, the agent must confirm:

- the approved boundary included merge
- the target branch and PR are correct
- CI passed or the named exception was accepted
- required review/risk checks passed
- no permanent E2E, release communication, related-impact, or session-ledger
  blocker applies
- the work is not a critical lane waiting for human review
- deploy is not implied by merge

If any item is missing, stop and explain the practical blocker.

Before push, PR open, CI-ready, or merge-ready claims, apply
[no-mistakes-lite.md](no-mistakes-lite.md). Plain meaning: outbound automation
can be bundled, but the final report must still name what is proven, what is
missing, the real GitHub state, and the next decision.

If multiple worktrees, branches, PRs, agents, or fixes are active, apply
[parallel-work-and-worktrees.md](parallel-work-and-worktrees.md) before pushing
or opening a PR. Plain meaning: confirm the exact workspace and branch that
owns the outbound change so unrelated local work is not shipped accidentally.

## Close-Out Shape

Use natural language:

```text
Status: PR is open and CI passed.
Meaning: the change is reviewable on GitHub, but it is not merged or live.
Checked: <CI/local checks>.
Recommended next: merge this PR, or hold if you want another review.
Decision needed: yes, merge approval.
```

For docs-only or Agent OS work, a shorter close-out is fine as long as it names
the highest proven state.
