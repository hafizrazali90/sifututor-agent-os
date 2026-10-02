# Business rules: authority and agent loading

This is the shared entry point for Sifututor business intent. It connects a
sourced [104-rule compilation](register.md) to the existing domain owners.
Hafiz owns business decisions. This compilation does not approve drafts,
promote historical memory, authorize a financial change, or prove deployment.

[Recorded decision reasons](decision-reasons.md) preserve the why where sources supplied it.

## Read for the task

Both Claude and Codex reach this guide through the umbrella `AGENTS.md` and
`context-authority.md`. Read only the relevant rule IDs and their owning
sources before planning, coding, diagnosing or reviewing product behaviour.
Inside a product checkout, follow its existing link to the umbrella contract.
In an isolated checkout, locate the canonical umbrella; do not guess that a
missing sibling folder means the business rule does not exist.

| Task domain | Start in the register | Owning source to inspect |
| --- | --- | --- |
| Request, students, shared classes, attendance and credits | BR-001–011; BR-063; BR-070 | Current Hafiz correction for BR-001; SIMS lifecycle/billing approved addenda and linked issues |
| Matching, identity, CRM ownership and acquisition | BR-012–020; BR-073; BR-080–084; BR-092–099 | Ripple CRM approved matching, Dual CX and identity packs; exact SIMS authority |
| Fees, refunds, bonuses, staff/tutor payments | BR-021–028; BR-030–035; BR-085–091 | SIMS/Ripple fee, payout and commission approved source docs; preserve critical-lane boundaries |
| Notifications | BR-029; BR-042–045 | Notification policy review plus action-specific delivery code; outreach approved pack |
| Nakngaji | BR-036–041; BR-074–079; BR-100–104 | Nakngaji business-rule change register and corrective pack, reconciled by dated decisions |
| Other products and proposals | BR-046–062; BR-064–069; BR-071–072 | Exact named Kelas, Learnest, Finch, mobile or proposal source; do not import SIMS policy by analogy |

The source paths, hashes and reading depth are in [sources.json](sources.json).
Some sources live in separate product repositories or private Pages; a local
checkout of this umbrella does not contain those files. Do not treat a locator
as proof the source was loaded. If unavailable, record the gap and continue
unaffected work. See [open decisions](open-decisions.md) for known limits.

## Separate four questions

1. **Desired behaviour:** what did Hafiz or the approved domain source decide?
2. **Rationale:** why did the source choose it? If absent, say not recorded.
3. **Implementation:** what do the inspected code and schema actually do?
4. **Verification:** what has a test or real journey proved, on which revision?

Never answer the first question using only evidence for the third. A singular
foreign key, old record, passing test, or deployed bug cannot redefine intent.
Conversely, an approved design does not prove it is implemented or live.

## Shared-class contract: BR-001

**Confirmed by Hafiz in this session:** one Tutor Request selecting students
A, B and C for one scheduled lesson means **one shared class session with
three participants**, not one class per student. Additional genuinely separate
scheduled lessons or separate Requests are distinct arrangements.

Student ownership, participation, evaluations, price components and payout
breakdowns are different concepts. Separate student records do not authorize
splitting the class. Do not multiply duration, session credit consumption or
base session earnings merely by participant count; their exact financial
assertions require the approved domain rules. No further business rationale
was supplied for this correction; do not invent one.

For a scheduling change, record the concrete example before editing:

| Given | Expected result | Rejected interpretation |
| --- | --- | --- |
| One Request, three students, one scheduled lesson | One session, three participants | Three sessions because there are three students |
| One Request, three students, two separately scheduled lessons | Two sessions, each with its applicable participants | Six sessions by multiplying students and lessons |
| A legacy singular `student_id` on a class | Inspect Request membership and all writers/readers | Treat the column as authority for per-student sessions |
| Student-specific evaluation or earnings breakdown | Preserve its student detail within the session | Infer independent scheduling from reporting/payment granularity |

## Evidence status and conflicts

- Current explicit user decisions apply to their stated scope. Business
  implementation still obeys the normal approval and critical-lane rules.
- Approved domain documents own the rule they cover. The register is an index
  and summary, not a competing owner that silently rewrites them.
- Drafts, proposals, staff requests and uncorroborated memories are candidate
  requirements. Preserve their status and do not implement them as current law.
- Before choosing between Koda records, recall the full records: creation and
  update timestamps, confidence, outdated and supersession fields. A memory's
  stored date is not necessarily the decision date. An outdated flag without a
  replacement link does not prove every statement was reversed.
- Read the exact replacement decision. Newest-file-wins and code-wins are not
  valid business-authority rules. See [the metadata audit](memory-audit.md).
- Resolve dated, scoped corrections without asking Hafiz to decide again.
  Only unresolved material product judgments need Hafiz. Hold that dependent
  change, gather remaining questions together, and continue unrelated work.

## Required task readback

In the implementation/review record, state the applicable rule IDs, exact
governing source, status/date, expected example, observed code difference and
the verification needed. Existing domain documents remain authoritative; a
rule ID by itself is not approval. Missing rationale stays not recorded.

For Request/class scheduling plans, save the small JSON example demonstrated
in [shared-class-plan.example.json](shared-class-plan.example.json), then run:

```bash
python3 scripts/agent-checks/business-rule-check.py --proposal /path/to/plan.json
```

This validates the declared BR-001 acceptance example and rejects participant
multiplication. It does not inspect application code, certify all business
rules or replace permanent application E2E coverage. The shared health check
runs its positive/negative fixtures and checks the entry-point wiring. These
are deterministic local checks, not a live model-compliance guarantee or a
new automatic tool-blocking hook.

## Updating a decision

Update the existing domain owner first with the new explicit decision,
effective scope/date, rationale if supplied, superseded statement and evidence.
Then update the affected register entry and example; keep its stable ID.
Preserve historical sources. Update Koda with a correction/pointer, not another
independent copy claiming authority. Pages are human review views; repository
owners and Git history govern future maintenance. A rule changes only after
the owner decision changes, never because an agent inferred it from code.

## Completion and maintenance

[Review and verification](review.md) records what is locally installed, what
was checked, and where this task stops. [Source reconciliation](reconciliation.md)
preserves the research trail. The source inventory distinguishes indexing,
extraction, focused reconciliation and full metadata recall; it never claims
every historical conversation or every document line was semantically reviewed.
