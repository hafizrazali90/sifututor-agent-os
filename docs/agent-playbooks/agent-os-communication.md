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

Use the canonical name `Sifututor` in human-facing prose. Never write
`SifuTutor` as the brand name. Exact repository slugs, URLs, domains, database
or account identifiers, code namespaces, third-party display names, and
historical evidence keep their authoritative literal spelling; format those
identifiers as code where practical.

Formal labels such as `Gate 2A`, `PARTIAL`, `BLOCKER`, or `Critical Save` are
allowed when they are useful for:

- commit records
- QA evidence
- audit trail
- handoff to another agent or human
- teaching Hafiz what the industry or the Agent OS calls a pattern

Do not use those labels as filler. If the label does not make the message
clearer, leave it out.

## Language Default

Reply to Hafiz in English by default, even when the underlying report, staff
quote, screenshot, or source material is in Bahasa Malaysia or mixed
language. Translate or summarize the Malay content inline instead of
switching the whole reply into Malay.

- Quoting a Malay staff message or a Malay screenshot does not change the
  reply language; keep the reply in English and translate the quoted part.
- Switch to Malay only when Hafiz explicitly asks for a Malay reply, or when
  producing app/user-facing copy that a project's own rules already require in
  Bahasa Malaysia (for example, tutor/parent app UI, which stays EN+BM).
- If the reporter's identity or language is unclear from the source, such as
  an unattributed screenshot or a forwarded quote, say the reporter is unknown
  instead of guessing a name or channel.

Mixed-language requests also keep the English default unless Hafiz explicitly
requests another language. An explicit Malay request applies to the requested
output; it does not switch unrelated explanations or later replies. Localized
product copy follows its product contract separately from the chat language.

## Explain The Story Before Judging Or Fixing It

For a bug, PR, feature, architecture change, or unfamiliar technical concept,
start by orienting Hafiz before presenting findings or implementation detail.

Use this order:

1. who the affected user or staff member is, what they are trying to do, and
   the report origin if confirmed (otherwise keep the reporter/channel unknown);
2. what happens now;
3. what should happen instead;
4. why the difference matters;
5. the proposed solution in ordinary language (or the next investigation if
   the cause is not yet established);
6. then findings and technical evidence, what remains unverified, and the
   highest proven release state. Local tests do not mean deployed or live.

Plain meaning:

```text
Explain the movie before discussing the broken camera.
```

If Hafiz says `explain first`, `I don't understand`, or asks what the actual
user flow is, reset to the beginning. Do not continue the technical finding
with a few simpler words attached.

Before non-trivial implementation, explain the intended build in the same
plain-English order: the user/business flow, options when there is a real
choice, the recommendation, what will and will not change, risks/tradeoffs,
and the evidence plan. Get that direction understood once before building.
After Hafiz approves the plan or an autopilot boundary, continue inside it
without repeatedly asking him to approve the same implementation details.

An urgent production/security blocker may lead the first sentence, but follow
it immediately with the user/system story that makes the risk understandable.

### One-By-One Walkthroughs

When Hafiz asks to go one by one, cover one feature, fix, finding, PR, or
decision at a time. For each item explain:

- what it is;
- what it does for the user/business;
- what is wrong or changing;
- the proposed improvement and tradeoff;
- what evidence supports it;
- whether Hafiz needs to decide anything.

Then stop for `go next` or confirmation before opening the next item, unless
Hafiz already approved an autonomous full walkthrough. One-by-one discussion
is a learning/review pace; it does not create extra commit, push, deploy, or
production approval gates.

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

Before the findings, give the short product story: which page/workflow this is,
who uses it, and the before/after behavior. `Lead with findings` is an internal
review-priority rule; it does not mean Hafiz should receive code-level findings
before he understands what is being reviewed.

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

## Fit The Reply To The Task

A trivial question can receive one sentence. A diagnosis or PR review needs
more context when the user flow, risk or evidence is complex. Headings and the
examples below are optional presentation aids, not mandatory fields on every
reply. Preserve confirmed preferences; the remaining scenario catalogue still
needs Hafiz's decisions and must not be silently treated as accepted policy.

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

### Proactive Drafts When Someone Needs The Outcome

At a meaningful close-out, consider whether someone outside this chat is
waiting on the outcome or needs to take the next action. If so, draft the short
copy-ready message without waiting for Hafiz to ask. This includes completed
access changes: tell the affected person what they can now do and what to retry,
using only verified, non-secret details. Infer audiences from the issue, report
or conversation; do not invent a recipient or reporting channel. If the needed
recipient is genuinely unclear, ask one focused question.

Keep staff/user drafts short: practical outcome, honest current state and next
action. Use one fenced plain-text block per distinct audience. Drafting never
authorizes sending; send only with explicit authorization. If nobody outside
this chat needs an outcome or action, omit the message and the empty message
heading. Do not manufacture an external audience for internal/trivial work.

### Recipient-Specific PR And Release Close-Out

When an agent reviews or improves someone else's PR and the work reaches a
meaningful outward state such as pushed, merged, deployed, live checked, or
accepted, the close-out must identify who needs to receive the result.

Do not ask who the recipients are at the start of every session. Infer them
from the issue, PR author, reporter, affected user, and current conversation.
Ask Hafiz only when the intended recipient is genuinely unclear.

Use one message per distinct audience:

| Audience | Message purpose |
| --- | --- |
| Staff, reporter, or user | Short, non-technical explanation of what happened, whether it is live, and what they should do next. |
| Developer whose PR was reviewed or improved | One integrated continuation of their PR that teaches what changed and requests independent verification. |

Separate audiences may receive separate messages. Do not send two disconnected
messages to the same developer: one generic incident report followed by a
separate review report makes the relationship to their PR unclear.

The developer message should include, when applicable:

1. the PR or task they originally worked on and what it attempted;
2. the confirmed staff report, ticket, TREQ, or acceptance context;
3. what the reviewer kept, changed, or added;
4. why the final implementation or evidence decision was made;
5. what the original submission missed or proved too weakly;
6. the highest final state and the evidence that supports it;
7. a request for the developer to independently verify the final work and
   reply with evidence; and
8. the reusable lesson the developer should add to their own AI checklist.

Be factual and instructional rather than accusatory. Credit correct diagnosis
or implementation first, then name the missing proof or engineering step
precisely. Never invent the intake source. If the conversation only confirms a
staff report and a TREQ, say `original staff report` and `TREQ`; do not infer a
channel such as Tawk, Planner, email, or WhatsApp from a typo.

This handoff is not a substitute for GitHub evidence, QA, release notes, or
issue state. It translates the verified engineering record for the people who
need to act on or learn from it.

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


## Assessing Sanitized Response Samples

The default runner tests its built-in checker fixtures. A passing fixture count
proves those examples are classified as expected; it does not prove live agent
compliance. To assess actual supplied samples, use the same runner:

```bash
python3 scripts/agent-checks/agent-os-response-shape-runner.py --samples /absolute/path/sanitized-samples.json
python3 -m unittest discover -s scripts/agent-checks -p test_communication_samples.py
```

Input is a nonempty JSON list. Each sample requires `text` and `context`
(nonempty strings). Context should summarize the request, known source,
audience, authoritative identifiers and verified state without private data.
Optional `checks` selects existing `close_out` or `copy_ready` heuristics;
`brand` always runs. Do not opt a trivial answer into a meaningful-close-out
check. `copy_ready` expects one message; review multiple audiences manually.

Start without `review` to see which criteria need review:

```json
[{"text":"Yes.","context":"Trivial question: is 2 plus 2 equal to 4?"}]
```

A reviewer reads each response against its context, then records `review` keys
`C1` through `C6`. Each entry has `verdict` (`pass`, `fail`, or
`not_applicable`) and a nonempty `reason` pointing to the specific evidence or
omission. Not-applicable also needs a reason. Review means:

| Criterion | Manual question |
| --- | --- |
| C1 | Is chat English by default despite Malay/mixed sources, with explicit language requests and localized copy scoped correctly? |
| C2 | Does diagnosis/review explain affected people, confirmed or unknown origin, observed/expected behavior, impact and proposed solution before technical evidence? |
| C3 | Are necessary audience drafts copy-ready, including completed access changes, without unnecessary messages, invented recipients or implied sending permission? |
| C4 | Is prose Sifututor, with technical identifiers unchanged against authoritative context? |
| C5 | Does length fit complexity, allowing genuinely short answers? |
| C6 | Do evidence, gaps and release claims match the known facts, without presenting fixtures as live compliance? |

For example, a C1 entry is `{"verdict":"pass","reason":"English reply to a
Malay screenshot; no Malay output requested."}`. The synthetic regression
examples in `scripts/agent-checks/communication-samples.json` demonstrate the
complete format, including deliberately bad replies. Their recorded semantic
verdicts are reviewed examples, not automated semantic detection or live agent
measurements. `expected_status` in that fixture file is used only by unit tests;
the sample CLI does not treat an expected failure as a passing response.

The runner reports mechanical violations, recorded semantic failures and
pending manual criteria separately. Exit codes: `0` all manual reviews recorded
without failures; `1` mechanical or recorded semantic failures; `2` invalid
input; `3` manual review still required. `review_recorded` means supplied
verdicts were recorded, not independently verified by the script. The CLI prints
metadata only, never sample text, context or reviewer notes. It writes no files
and makes no network calls. Repeated runs do not alter the samples.

Sanitize before providing samples; this tool is not a sanitizer. Keep real
transcripts and private content out of fixtures, Git and Koda. The brand check
excludes inline code, URLs and labelled code fences, but checks plain-text
message fences. It cannot detect all identifier changes, false claims, language
switches or invented attribution. Existing keyword checks can miss paraphrases
and accept misleading wording; always perform the semantic review. No hook,
model judge or automatic live transcript collection is added here.
