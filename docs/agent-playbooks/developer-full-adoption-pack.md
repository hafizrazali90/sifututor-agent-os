# Developer Full Adoption Pack

Use this when a developer staff member is expected to adopt the full Agent OS
workflow with Codex, Claude, Cursor, GitHub Copilot, Gemini, or another
LLM-assisted coding tool.

This is written for developers who work in assigned product repos. The product
repo may be inside the Sifututor workspace or in another company GitHub org,
such as the Kelas app under Learnest Lab. Ordinary non-developer staff should
keep reporting issues through Microsoft Teams Planner.

## Main Idea

The developer should use the whole Agent OS route, not only a small testing
slice.

Plain version:

```text
Work through the full route.
Let the Agent OS tell you when to continue, ask, or stop.
```

The developer does not need to memorize every approval rule before starting.
The Agent OS should detect risky boundaries such as commit, push, PR, deploy,
production, critical-lane code, secrets, or destructive actions.

## Repo Access Model

Developer adoption uses two kinds of repo access:

| Repo | What access means | Why it is needed |
| --- | --- | --- |
| Agent OS repo | Read access by default. Write access only for reviewed workflow-improvement work. | This is the workflow handbook and source of truth. Developers need to read it to follow the system. |
| Product repo | Access to the repo they are assigned to work on, even if it lives in another GitHub org such as Learnest Lab. Builder work needs normal branch/code access. | This is where the actual product task happens. |

Plain version:

```text
Read the Agent OS repo to understand how to work.
Work in the assigned product repo to do the task.
Change Agent OS rules only through reviewed workflow-improvement work.
```

Examples:

- a `ripple-suite` task means the developer reads the Agent OS repo and works
  in the `ripple-suite` repo
- a `sifu-tutor` task means the developer reads the Agent OS repo and works in
  the `sifu-tutor` repo
- a Kelas app task means the developer reads the Agent OS repo and works in the
  Kelas product repo under the Learnest Lab GitHub org
- if the developer finds the workflow confusing, they report the confusion
  first instead of quietly editing Agent OS rules

Before the first real Kelas task, create or verify a small Kelas project
profile. The Agent OS core says how to work; the Kelas profile says how that
specific app installs, runs, tests, deploys, and proves user behavior.

Changing the Agent OS itself is a separate workflow-improvement task. It should
go through review because those rules affect Hafiz, Codex, Claude, and future
developers.

## What The Developer Is Testing

The developer is testing two things at once:

1. **The product work** - whether the feature, fix, or change works like a real
   user expects.
2. **The Agent OS** - whether the workflow is clear enough for a developer to
   follow without Hafiz explaining every step.

When something is confusing, that is not failure. It is useful feedback for
improving the Agent OS.

## The Full Route

Use this route for normal developer work:

| Step | What it means | What good output looks like |
| --- | --- | --- |
| Intake | Understand the request, issue, report, or task. | "I understand the user, screen, problem, expected result, and current evidence." |
| Diagnosis | Inspect before changing. | "I checked current code/behavior and found the likely cause." |
| Plan | Explain the intended change in plain language. | "I will change X because Y, then prove it with Z." |
| Build | Make the smallest scoped change. | Code/docs changed only where needed. |
| Verify | Prove the changed behavior. | Tests, command output, API check, browser check, or screenshot evidence. |
| QA | Test like a real user. | Steps a staff/admin/tutor/parent/customer would actually do. |
| Review | Check risk before sending out. | Scope, regression, missing evidence, security, data, and user impact reviewed. |
| Commit / PR | Prepare the work for review. | Clear summary, file list, checks, evidence, and stop point. |
| Close out | Explain the real state. | What changed, checked, still uncertain, recommended next action. |

## How To Start A Task

Start with this prompt pattern:

```text
Read the Agent OS repo AGENTS.md and the assigned project AGENTS.md/CLAUDE.md.
Use the Agent OS workflow.
Task: <describe the task>.
My expected finish point is <diagnosis only / local fix / PR opened / etc>.
Tell me what you need to check first and where you will stop for approval.
```

If the finish point is not obvious, ask the agent:

```text
What should the practical finish point be for this task, and why?
```

The agent should answer in normal language. Example:

```text
For this bug, the useful finish point is PR opened with browser evidence.
I can diagnose, fix, test, and prepare the PR, but I will stop before merge or
deploy.
```

## What The Agent Should Read First

Minimum starting context:

- Agent OS repo `AGENTS.md`
- Agent OS repo `docs/agent-playbooks/developer-full-adoption-pack.md`
- target project `AGENTS.md`
- target project `CLAUDE.md` or equivalent project reference
- `docs/agent-playbooks/agent-os-quick-start.md`
- the relevant workflow playbook, such as `diagnose.md`, `qa.md`, `review.md`,
  `commit.md`, or `product-design.md`

For user-facing product work, also check:

- project `TESTING.md` if it exists
- relevant feature docs
- existing E2E or QA coverage for that workflow

## Approval Boundaries

The developer works normally until the Agent OS reaches a risky boundary.

| Boundary | Expected behavior |
| --- | --- |
| Read-only diagnosis | Continue. No extra permission needed. |
| Local scoped code change | Continue only if the task is approved for builder work. |
| Commit | Ask with exact changed files and checks. |
| Push / PR / merge | Ask for explicit approval unless the current task already approved that exact boundary. |
| Deploy / production / monitoring with write impact | Ask for explicit approval. |
| Payment, auth, invoice, commission, migration, mobile API contract | Diagnose first. Stop before implementation until approved. |
| Secret, `.env*`, `live/`, destructive action, force push, bypass hook | Stop. Do not work around the rule. |
| Missing tool access | Explain the tool needed, why, scope, and what evidence it will prove. |

Plain version:

```text
The developer does not carry the whole rulebook in their head.
The Agent OS points out the risky door before opening it.
```

## Evidence Standard

Do not say "done" just because the code changed.

Good evidence depends on the task:

| Work type | Evidence expected |
| --- | --- |
| UI bug or feature | Browser/mobile journey, screenshot/video if useful, focused E2E where feasible. |
| Backend/API | Test, API/curl result, state transition explanation, safe data check. |
| Docs/workflow | Diff review, link check, Agent OS health if workflow docs changed. |
| Critical lane | Read-only diagnosis first, then stronger tests and Hafiz risk sign-off. |
| PR review | Diff, tests, CI, product behavior, risk, missing proof, recommendation. |

The developer should prove what they can prove. Hafiz should only be asked to
judge business direction, subjective product acceptance, unavailable access,
risk acceptance, or final go/no-go.

## Human Tester Mindset

The developer should ask:

- What would the real user click, enter, see, or expect?
- Does the success message or final state actually appear?
- Did the data change correctly?
- Could a permission, role, browser, or empty state break this?
- Is there an existing test or QA checklist that should cover this forever?
- If this fails in production, how would staff notice?

For a UI issue, code tests alone are not enough when a safe human-like browser
or mobile check is possible.

## Close-Out Template

Use this shape at the end of every task:

```text
Status: <done / partly done / blocked>
Meaning: <what changed or what was learned in product terms>
Checked: <tests, browser/API evidence, review, or why not checked>
Still uncertain: <anything not proven>
Recommended next: <one action>
Decision needed: <yes/no, and what decision>
```

Good close-out:

```text
Status: done locally, PR not opened yet.
Meaning: the modal now opens after the staff clicks Assign Tutor.
Checked: focused Playwright test passed and I verified the modal in browser.
Still uncertain: production data was not touched.
Recommended next: approve push and PR.
Decision needed: yes, approve push/PR or request changes first.
```

Bad close-out:

```text
Done.
```

## How To Report Agent OS Confusion

When the workflow confuses the developer, record it like this:

```text
Confusing moment: <what happened>
What I expected: <what I thought the agent/workflow would do>
What actually happened: <what happened instead>
Impact: <slowed me down / risked wrong action / unclear evidence / unclear stop point>
Suggested improvement: <optional>
```

Useful examples:

- "I did not know whether to create a GitHub issue before diagnosis."
- "The agent asked for approval but did not explain the practical risk."
- "I could not tell whether done meant local, PR opened, merged, or live."
- "The evidence request was too vague."

## First Training Task Shape

The first adoption task should use the full route but stay low risk.

Recommended first task:

```text
One repo.
One GitHub issue.
One branch.
One low-risk bug, UI polish, docs fix, or QA improvement.
Finish point: PR opened with evidence.
Stop before merge, deploy, production, or critical-lane work.
```

For the Kelas app, the first task should be chosen from the Kelas repo after
its project profile is drafted or verified. Do not start from a Sifututor repo
unless the developer is actually assigned to that repo.

Avoid first:

- payment
- auth
- invoice
- commission
- migration
- deployment
- production data
- mobile API contract changes

## Manager Review Checklist

After the first task, Hafiz or an engineering lead should check:

- Did the developer understand where to start?
- Did the agent read the right docs?
- Did the developer know the finish point?
- Did the work include useful evidence?
- Did the close-out explain the real state?
- Did the Agent OS stop at the right approval boundary?
- What confused the developer?
- What should be improved in docs, skills, checks, or examples?

## Success Criteria

The developer has adopted the workflow when they can:

1. start a task without Hafiz rewriting the whole prompt
2. use the correct project docs and workflow playbooks
3. diagnose before changing code
4. explain the plan in plain language
5. produce human-like testing evidence
6. stop at approval boundaries without needing to memorize every rule
7. avoid confusing local, committed, pushed, PR, merged, deployed, and live
8. close out with status, meaning, checks, next action, and decision needed
9. report Agent OS confusion clearly enough for us to improve the system
