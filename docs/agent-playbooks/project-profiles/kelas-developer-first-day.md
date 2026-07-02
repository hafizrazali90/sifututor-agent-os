# Kelas Developer First-Day Agent OS Setup

Use this when Hafiz wants a developer to co-work on the Kelas app using the
Sifututor Agent OS.

Plain meaning:

```text
The developer reads the Agent OS repo for how to work.
The developer works in the Kelas repo for product code.
The first task proves both the product workflow and whether the Agent OS is
clear enough for another developer.
```

## Who This Is For

This is for a trusted developer staff member working on Kelasapp under the
Learnest Lab GitHub org.

It is not for ordinary support or operations staff. Non-developer staff should
continue reporting issues through the normal intake channel, such as Teams
Planner or the team support process.

## Access Hafiz Should Give

| Repo | Access to start | Why |
| --- | --- | --- |
| `hafizrazali90/sifututor-agent-os` | Read | The shared workflow handbook: rules, playbooks, evidence standard, approval boundaries, and handoff style. |
| `Learnest-Lab/kelasapp` | Write, if the developer is expected to code | The actual Kelas product repo where branches, fixes, tests, and PRs happen. |

Start the developer as **Developer staff - builder** only for scoped Kelas
tasks. Do not give production, deploy, secret, payment, auth, database, or
advanced operations access by default.

Plain version:

```text
Read the OS.
Work in Kelas.
Ask before risky doors: push, PR, merge, deploy, production, critical lanes, or
destructive actions.
```

## Tool Access For The Developer

Do not give the developer every tool just because they are using the full Agent
OS workflow.

Plain meaning:

```text
The workflow can be full.
The tool access should still be bounded.
```

Use this rule from the capability model:

```text
Connection gives capability.
Profile gives permission.
Approval gives authority.
Probe gives current proof that the tool works.
```

For the first Kelas task, the developer normally needs:

| Tool or access | Starting decision | Why |
| --- | --- | --- |
| Agent OS repo | Read access | Needed so Claude/Codex can read the workflow rules. |
| Kelas repo | Write access if coding | Needed for branches, local edits, tests, and PR prep. |
| GitHub issues/PRs | Read/write for Kelas | Needed to work from one issue and open one PR with evidence. |
| Local Claude/Codex in VS Code | Allowed | Needed for guided coding, diagnosis, verification, and close-out. |
| Node 24 and local checks | Required | Kelas checks are only honest on Node 24. |
| Browser/Playwright | Allowed when configured | Needed to prove visible user journeys. |
| Koda read | Allowed from day one if safely scoped | Useful for shared lessons, project history, and Agent OS context. |
| Koda write | Approval-required by default | Durable memory should not be written by a new developer until trust and rules are proven. |
| Production/deploy tools | Blocked by default | First task stops before merge, deploy, production, and monitoring. |
| Database/admin/payment/auth tools | Blocked by default | These are sensitive lanes and need separate approval. |
| `.env*`, secrets, raw credentials | Forbidden | The Agent OS never asks developers or agents to read or print secrets. |

If the developer or their agent needs a blocked tool, they should report:

```text
Tool needed:
Why it is needed:
Read/write/admin/destructive:
What evidence it will prove:
What I can still do without it:
Where I will stop:
```

Do not treat missing access as failure. It is useful evidence about the rollout.

### Koda For Developer Staff

Koda is the shared memory layer for durable lessons, corrections, and repeated
workflow behavior. It is not the first place a new developer should write.

For day one:

- the developer may use Koda read if the connection is safely scoped
- the developer records findings in the GitHub issue, PR, handoff, or task note
- the developer reports Agent OS confusion using the confusion template below
- Hafiz or a trusted internal agent decides what deserves Koda memory

Give Koda write access only after the developer has shown they can distinguish:

- a durable lesson from a temporary task detail
- a correction from an opinion
- project-safe context from secrets or private payloads
- current repo evidence from stale memory

Plain version:

```text
Koda read can help from day one.
Koda write should be earned through memory discipline.
Promote useful PR/task lessons into Koda after review.
```

## What To Tell The Developer

Send this instruction:

```text
You will use the Sifututor Agent OS while working on Kelasapp.

The Agent OS repo is the workflow reference.
The Kelas repo is where product work happens.

For the first task, do not start with payment, auth, invoice, migration,
production, deployment, or anything destructive.

Use one GitHub issue, one branch, and one low-risk task.
Expected finish point: PR opened with evidence.
Stop before merge or deploy.
```

## Suggested Local Folder Shape

Recommended:

```bash
mkdir -p ~/Projects
git clone https://github.com/hafizrazali90/sifututor-agent-os.git ~/Projects/Sifututor
cd ~/Projects/Sifututor
git clone https://github.com/Learnest-Lab/kelasapp.git kelas
cd kelas
git checkout feat/launch-readiness
```

If `feat/launch-readiness` has already been merged, use the current default
branch instead.

## First Prompt For Claude Or Codex

The developer can paste this at the start of the first Kelas task:

```text
Kelas work.

Read ../AGENTS.md first as the shared Agent OS.
Then read this repo AGENTS.md, CLAUDE.md, and .agent-os/project-profile.md.
Use the Agent OS workflow.

Task: <paste the GitHub issue or Hafiz task here>.

Before changing code, tell me:
- what task you understand
- what docs/files you need to inspect first
- what the practical finish point should be
- what evidence will prove it works
- where you will stop for approval
```

## First Task Choice

Pick something low-risk that still exercises the full route.

Good first task examples:

- fix a small UI empty state
- improve a confusing label or validation message
- add missing bilingual copy for an existing screen
- add or improve a QA checklist
- add a focused test for an existing low-risk behavior

Avoid first:

- payment
- auth
- invoice
- commission
- migration
- deployment
- production data
- public invoice token behavior
- anything that requires secrets or `.env*`

## What The First Task Should Prove

The first task is successful when the developer can show:

- the agent read the Agent OS and Kelas local rules
- the task was diagnosed before code changed
- the plan was explained in plain language
- the change stayed scoped
- relevant checks ran
- user-like evidence was collected when the change is visible
- the PR explains what changed, how it was checked, and what remains
- the agent stopped before merge, deploy, production, or critical-lane work

## How Hafiz Reviews The First Task

Hafiz does not need to read every line of code first.

Ask the developer or agent to summarize:

```text
What changed in product terms?
How did you prove it?
What files changed?
What is still uncertain?
What is the recommended next action?
Where did the Agent OS confuse you?
```

If the developer says the workflow was confusing, capture it like this:

```text
Confusing moment:
What I expected:
What actually happened:
Impact:
Suggested improvement:
```

That feedback becomes Agent OS improvement work, not a reason to abandon the
workflow.

## Current Kelas State

As of 2026-07-02:

- Agent OS integration exists in the Kelas repo on `feat/launch-readiness`.
- Kelas commit `d72c4b5` added the local Agent OS files.
- The local Kelas working tree may contain unrelated dirty PDF/report work from
  another Claude session; do not touch those files during onboarding unless
  Hafiz explicitly assigns that task.
- Kelas requires Node 24 for honest local checks.

## Recommended First Finish Point

For the first developer adoption task:

```text
PR opened with evidence.
Stop before merge, deploy, production, and critical-lane implementation.
```

Plain version:

```text
Let the developer complete a real small task, but do not let the first test
turn into a production release.
```
