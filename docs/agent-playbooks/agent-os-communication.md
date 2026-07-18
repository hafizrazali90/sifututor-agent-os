# Agent OS Communication

Status: draft accepted for day-to-day use; refine after real work.

This playbook defines how agents should explain work to Hafiz without making
him read process noise.

The default style is:

```text
Code translated into natural language.
```

That means the agent explains what happened, why it matters, what changed, how
it was checked, and what should happen next in normal human language first.
Technical details come after the practical meaning.

## Core Rule

Use plain language by default. Use workflow labels only when they help.

Formal labels such as `Gate 2A`, `PARTIAL`, `BLOCKER`, or `Critical Save` are
allowed when they are useful for:

- commit records
- QA evidence
- audit trail
- handoff to another agent or human
- teaching Hafiz what the industry or the Agent OS calls a pattern

Do not use those labels as filler. If the label does not make the message
clearer, leave it out.

## PR Reviews In Chat

When Hafiz says he needs to review a PR, the agent should make the chat the
review surface. Hafiz should not have to open GitHub and read the code diff by
default.

The agent must still do the technical work underneath: read the PR, issue,
changed files, diff, tests, CI, release ledger, and relevant rules. Then explain
the PR in normal language:

- what changes for the business or user journey
- who is affected
- before vs after behavior
- risks and business rules
- what evidence was checked
- what remains uncertain
- the decision Hafiz is being asked to make

If there is a blocker, lead with it in plain language. Put file names, function
names, and line references after the plain-language review, or only where they
prove a finding.

Approving the review in chat is enough for Hafiz's review decision. It is not
permission to merge, deploy, or change production unless he explicitly says so in
the current session.

## Open Review Artifacts Automatically

When the agent creates or updates an important review artifact that Hafiz should
inspect, open it on Hafiz's Mac automatically instead of only giving a path.

Examples:

- generated Session Map HTML dashboard
- important Markdown review board
- generated HTML mockup
- QA report or screenshot index
- PR/release review document
- handoff or save-session document Hafiz must inspect

Use the narrowest safe local command, usually:

```bash
open <path>
```

Plain meaning:

```text
If I need Hafiz to review a local doc, I should put it in front of him.
Do not make him hunt for the file.
```

Still include the file path in the chat so Hafiz can reopen it later. Do not
auto-open files that contain secrets, credentials, raw tokens, `.env*` content,
or production-sensitive private payloads.

## Explanation Layers

When something is technical, explain it in layers.

### 1. Practical Meaning

Start with what Hafiz needs to understand as the owner:

```text
The checkout is failing because the app sends the payment amount in the wrong
format.
```

### 2. Easier Explanation

If the topic is twisted, add a simple non-technical version:

```text
Simple version: the cashier and the bank are reading the amount differently, so
the bank rejects the payment.
```

### 3. Technical Detail

Then add the code-level detail:

```text
Technically, `PaymentRequest::amount` is being converted to cents twice before
the FIUU payload is signed.
```

The agent should not force all three layers when the task is simple. Use the
extra layer when it helps Hafiz learn or when the explanation would otherwise
feel too dense.

When the change involves logic, routing, hooks, checks, automation, API
contracts, data flow, or code behavior, include the technical explanation too.
Do not hide the technical part; translate it.

Good pattern:

```text
What this means for you: the agent will no longer push a half-finished docs
batch just because some commits already exist locally.

Technical detail in normal language: before pushing, the agent compares local
commits against GitHub, checks whether any docs or workflow rules are still
unfinished, runs the required Agent OS checks, and then asks for one exact push
approval with the branch and remote target named.
```

Bad pattern:

```text
Updated push workflow.
```

That is too thin. It does not explain the behavior, the logic, or the practical
effect.

## Close-Out Shape

For meaningful work, close out with the information Hafiz needs to continue.
The exact formatting can be relaxed.

Default to a **Normal Close-Out** for daily docs, workflow, and product
discussion steps:

```text
Done. <one sentence about what changed and how it was checked.>

Current state: <Continue | Save Only | Park | Hand Off | Close>.
Still waiting: <what is not true yet, or "nothing required">.
Recommended next: <one concrete next action>.
Decision needed: <yes/no, and what Hafiz needs to decide>.
```

Use a **Full Close-Out** when the step changes commit state, push/GitHub state,
PR/merge state, QA/test evidence, deploy/production state, handoff/save-session
state, or critical-lane risk:

```text
What changed:
- <change>

Checked:
- <evidence>

Current state:
- <ending state and git/release/task state>

Still waiting:
- <remaining work, approvals, unknowns, or "nothing required">

Recommended next:
- <one concrete next action>

Decision needed:
- <yes/no and what decision>
```

Required meaning in either shape:

- what changed
- how it was checked
- the current runtime mode when it helps prevent confusion, such as discuss,
  plan, diagnose, build, verify, QA, review, commit, push/PR, release, or save
- the loaded context when missed docs or too much context could change the work
- what remains unclear or unverified
- the single recommended next step
- whether Hafiz needs to decide anything
- the honest ending state when the work is meaningful: Continue, Save Only,
  Park, Hand Off, or Close
- the highest proven work state when GitHub, PR, merge, deploy, QA, or live
  status matters: drafted, changed locally, committed locally, pushed to
  GitHub, PR open, merged, deployed, live checked, or accepted / closed

Good relaxed close-out:

```text
I documented the approval model and linked it from the Agent OS index. The
health check and pre-commit guard both passed.

Current state: Continue.
Still waiting: the docs batch is committed locally, not pushed to GitHub.
Recommended next: review Communication and Close-Out before committing.
Decision needed: no.
```

Use a structured close-out only when it improves scanning, such as after a long
task, QA run, handoff, commit prep, or incomplete work.

Use [agent-os-runtime-reliability.md](agent-os-runtime-reliability.md) when a
session becomes stateful or long-running. Plain meaning: the close-out should
make the mode, context, state, proof, and next action clear enough that Hafiz
does not have to reconstruct where we are.

The executable response-shape subset lives at:

```bash
scripts/agent-checks/agent-os-response-shape-runner.py
```

It checks sample close-outs for the required meaning above. Plain meaning: it
does not judge style perfectly, but it catches vague "done" replies that do not
tell Hafiz what changed, what was checked, what state the work is in, what
remains, and what should happen next.

## Progress Updates

During longer work, give short updates that explain what is happening and why.

Good:

```text
I found the rule exists in `AGENTS.md`, but it is still a little too template
heavy. I am moving the softer communication rule into its own playbook and then
linking the other docs to it.
```

Avoid:

```text
Running workflow phase. Status pending. Proceeding to next gate.
```

## Copy-Ready Outbound Messages

When Hafiz asks for a WhatsApp reply, a message to a developer or staff member,
or any equivalent text he wants to copy and send, the output must be copy-safe
by default.

Put the complete send-ready message inside one fenced `text` block. Inside that
block:

- use bare URLs such as `https://example.com/pr/123`
- preserve the intended blank lines, bullets, numbering, and paragraph breaks
- use the destination channel's native formatting, such as WhatsApp `*bold*`
- do not use rendered Markdown links such as `[PR #123](https://example.com)`
- do not use Markdown blockquotes unless Hafiz explicitly wants quoted text

Keep any explanation, warning, or alternative wording outside the block. The
message inside the block must be complete enough to copy without editing or
reconstructing content from the surrounding answer.

This applies to WhatsApp and to phrases such as:

```text
give me a copy-paste reply
write a message to my dev
provide a send-ready handoff
draft something I can send to staff
```

If Hafiz explicitly asks for rich email HTML, Markdown, or another destination
format, use that requested format instead. The default remains copy-safe plain
text.

Good:

````text
Copy and send this:

```text
*Malay Content Localisation is live.*

Backend PR:
https://github.com/example/project/pull/123

- Please complete native-device UAT.
- Share the results here when finished.
```
````

Avoid:

```text
> *Malay Content Localisation is live.*
>
> [Backend PR](https://github.com/example/project/pull/123)
```

The second version may look neat in chat, but copying it can include quote
markers or Markdown link syntax that Hafiz did not intend to send.

## Teaching Industry Terms

Hafiz wants to learn useful terminology, but not be buried under it.

Good pattern:

```text
In workflow terms, this is a verification gate. In normal language, it means I
need to prove the change works before we commit it.
```

Bad pattern:

```text
Gate 2A is required before Gate 2B and Critical Save.
```

Use the term, then translate it.

## Examples

### Bug Diagnosis

Good:

```text
The list is empty because the filter runs twice. First the backend returns only
active tutors, then the frontend filters again using an older status name.
Simple version: we are removing the same tutors twice.
```

### Docs Work

Good:

```text
I added the communication rule and linked it from the Agent OS overview. This
does not change product code. The docs checks passed, and the next best step is
to review Context Authority.
```

### Incomplete Work

Good:

```text
I updated the docs, but Koda did not save the correction because the memory tool
timed out. The practical risk is small because the rule is now in versioned
docs, but I should retry Koda before we close the session.
```

### Commit Prep

Good:

```text
The docs are ready to commit. I checked the file list and the guard passed.
Recommended commit message: `📝 docs(agent-os): refine communication and
approval rules`. I need your approval before I commit.
```

### After Local Commit

Good:

```text
Committed locally: `414e48d 📝 docs(agent-os): add session map skill`.
The pre-commit guard passed and the working tree is clean. This is not on
GitHub yet.

Recommended next: approve push if you want this available on GitHub; otherwise
we can continue local work from this commit.
```

Bad:

```text
Committed locally. Not pushed yet.
```

The bad version tells Hafiz the state, but not what to do next.

Important rule: the final line should usually tell Hafiz the next move. Do not
end meaningful work with only "done" or "not pushed yet."
