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

## Close-Out Shape

For meaningful work, close out with the information Hafiz needs to continue.
The exact formatting can be relaxed.

Required meaning:

- what changed
- how it was checked
- what remains unclear or unverified
- the single recommended next step
- whether Hafiz needs to decide anything

Good relaxed close-out:

```text
I documented the approval model and linked it from the Agent OS index. The
health check and pre-commit guard both passed. This is local-only for now, so
the next best step is to review Communication and Close-Out before committing
the docs batch.
```

Use a structured close-out only when it improves scanning, such as after a long
task, QA run, handoff, commit prep, or incomplete work.

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
