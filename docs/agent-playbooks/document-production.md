# Document Production Playbook

Use this for substantial professional Sifututor documents that require
research, evidence control, deliberate narrative, polished presentation, or
several output formats.

Plain meaning:

```text
Hafiz decides what the document must achieve and approves its direction once.
The agent then researches, structures, drafts, challenges, corrects, renders,
checks, and packages it autonomously inside that agreed boundary.
```

This playbook is based on the completed Sifututor ecosystem sourcebook
workflow. It is not a slide-order generator and it is not a replacement for
ordinary one-file documentation edits.

## When To Use

Use this workflow for:

- company, platform, ecosystem, capability, or operating sourcebooks;
- stakeholder, partner, board, strategy, or expansion papers;
- evidence-backed reports and professional internal knowledge documents;
- long-form guides that must serve technical and non-technical readers;
- living documents with governed claims and scheduled updates;
- documents requiring polished Markdown, HTML, PDF, or DOCX outputs;
- major updates to an existing governed document.

Do not use it for:

- a typo or narrow copy edit;
- a short answer that belongs only in chat;
- product requirements, UX specifications, or build prompts, which use
  `product-design.md`;
- code/API documentation whose main proof is implementation and tests;
- slide editing when an existing Google Slides deck is the requested target;
- external publication or distribution without explicit approval.

## Relationship To Other Workflows

| Workflow | Relationship |
| --- | --- |
| `task-router.md` | Classifies the request and practical finish point. |
| `product-design.md` | Owns product PRDs, UX, backend contracts and build prompts. |
| `agent-os-research.md` | Supplies general source-quality and external-research context; this playbook owns document-specific research execution. |
| `autonomous-work-packets.md` | Governs how the agent loops after the document contract is approved. |
| `review.md` | Supplies fresh-context and risk-review behavior when the finished document needs independent challenge. |
| `no-mistakes-lite.md` | Final honesty check before calling the document ready. |
| `save-session.md` | Preserves the finished or paused document state. |

## Document Lanes

Choose the lightest lane that fits the audience, evidence and output risk.

| Lane | Examples | Minimum path |
| --- | --- | --- |
| Quick | Memo, short brief, small internal guide | Contract summary -> targeted research -> draft -> one check |
| Professional internal | SOP, strategy paper, department guide | Contract -> evidence map -> blueprint -> draft -> local QA |
| Governed stakeholder | Ecosystem sourcebook, capability brief, partner paper | Full research -> governed claims -> blueprint approval -> draft -> formats -> adversarial review |
| Public or high-stakes | Public claims, regulatory or financial material | Full workflow plus current authoritative verification and owner publication approval |

Escalate the lane when the document contains sensitive business facts, current
law or regulation, financial claims, public comparisons, named launch
commitments, or information that could materially affect trust.

## Default Finish Point

For a governed stakeholder document, the default local finish point is:

```text
Governed Markdown master complete.
Required local formats generated.
Deterministic and visual checks passed.
Independent review has zero blocking and zero material findings.
Session state and durable lessons preserved.
Nothing committed, uploaded, published, or externally distributed.
```

Commit, Google Drive upload, email, public publication, or external sharing are
separate boundaries unless Hafiz explicitly included them.

## Phase 1 — Build The Document Contract

Start from known context. Do not ask Hafiz to repeat information that can be
found in the current conversation, Koda, project docs, a supplied reference,
or the existing document.

Use
[`templates/document-production/document-contract.md`](templates/document-production/document-contract.md).

The contract must answer:

- purpose;
- primary and secondary audiences;
- what readers should understand, decide, or be able to do;
- central story or governing argument;
- desired tone and depth;
- required output formats;
- current capability versus future direction treatment;
- confidentiality and sensitive-information boundary;
- freshness and update model;
- approved autonomous stop point;
- owner decisions still required.

### Noise-control rule

Ask only questions that materially change audience, narrative, evidence,
confidentiality, format, or acceptance. Prefer one consolidated contract over a
long chain of A/B questions.

After a correction, restate the corrected full fact. For example:

```text
Sifututor has operated since 2018 using the previous system; the new SIMS went
live in May 2025.
```

Do not preserve only the corrected fragment and leave the surrounding
timeline ambiguous.

## Phase 2 — Build The Research Plan

Translate the document contract into research questions before opening many
sources.

For every research area record:

| Field | Purpose |
| --- | --- |
| Research question | What must be known before writing? |
| Decision supported | Which narrative, chapter, claim or roadmap choice depends on it? |
| Preferred evidence | Internal system truth, official source, regulator, standard, research, or first-party product evidence. |
| Freshness | How current must the answer be? |
| Stop condition | What evidence is sufficient? |

Research should cover both:

1. **Internal truth:** what Sifututor has, how it works, what is approved, and
   which system or owner is authoritative.
2. **External context:** why it matters, how the domain is changing, which
   standards or regulations apply, and what evidence should influence the
   roadmap.

## Phase 3 — Deep Internal Research

Use the narrowest relevant sources:

- project `AGENTS.md` and relevant `CLAUDE.md`;
- current product and architecture docs;
- existing governed reports and sourcebooks;
- active task state when the project uses it;
- relevant Koda memories;
- relevant Mission Ledger sections;
- current code or tests only when the document's technical truth requires it;
- approved read-only operational evidence when current state matters.

Do not read repository `.env*`, secrets, credentials, private customer
payloads, or anything under `live/`.

Treat internal plans and old status documents as context, not automatic proof
of current capability. Resolve conflicts through `context-authority.md`.

## Phase 4 — Deep Online Research

Deep online research is mandatory for governed stakeholder and public/high-
stakes lanes unless the contract explicitly limits the document to internal
facts and explains why external context is unnecessary.

Research basis for this phase:

- OpenAI describes deep research as appropriate for multi-step synthesis across
  sources with citations that readers can verify:
  https://help.openai.com/en/articles/10500283-deep-research
- W3C PROV defines provenance as information about the entities, activities and
  responsible agents involved in producing something so its quality,
  reliability and trustworthiness can be assessed:
  https://www.w3.org/TR/prov-overview/
- The GOV.UK Service Manual recommends defining research objectives and
  questions, turning unsupported assumptions into research questions, choosing
  methods that provide strong evidence efficiently, and feeding findings into
  decisions:
  https://www.gov.uk/service-manual/user-research/plan-user-research-for-your-service
- NIST's AI Resource Center emphasises documentation plus testing, evaluation,
  verification and validation for trustworthy AI-assisted work:
  https://airc.nist.gov/

### Three-pass method

#### Pass A — Landscape discovery

- identify domain language, standards, regulators, market structures, trends,
  comparable operating models, and likely contradictions;
- expand research questions as new terminology appears;
- use search results and secondary sources to locate stronger originals;
- do not draft claims from snippets.

#### Pass B — Evidence-grade investigation

Open and inspect the underlying source. Prefer:

1. laws, regulators and government publications;
2. standards bodies and official technical guidance;
3. first-party company or product documentation;
4. peer-reviewed research and university publications;
5. recognised industry institutions;
6. reputable secondary reporting;
7. community or opinion sources only as clearly labelled context.

For technical questions, use primary documentation or research papers. For
law, regulation, financial, medical, public-statistic, market or product-state
claims, browse again near final acceptance because the information may change.

#### Pass C — Final claim reverification

After drafting, reopen every volatile or high-impact source and confirm that
the final wording—not only the general topic—is supported.

Reverify at least:

- current laws and regulations;
- public statistics and market numbers;
- third-party product capabilities;
- public ratings or review counts;
- named officeholders or organisations where identity can change;
- comparative claims;
- claims that could materially affect partner or stakeholder confidence.

### Source record

Use
[`templates/document-production/claim-register.md`](templates/document-production/claim-register.md)
to preserve:

- source organisation and title;
- direct URL;
- publication and access dates;
- source type and authority;
- exact claim supported;
- agent interpretation;
- limitations and geography;
- contradictory evidence;
- freshness/review rule;
- permitted document use.

Search snippets, generated summaries and model recollection are never final
evidence.

### Contradiction testing

For every material conclusion ask:

- What supports it?
- What challenges it?
- Are the sources measuring the same concept?
- Do geography, population, product or time period differ?
- Is this a requirement, recommendation, observation, interpretation, or
  commercial opinion?
- Could the final wording make a reasonable reader infer more than the source
  proves?

Keep a private contradiction and uncertainty list. Resolve material conflicts
before the blueprint or name the owner decision required.

### Research saturation

Do not use an arbitrary link count. Research is sufficient when:

- every material question has an evidence-grade answer or an explicit gap;
- new searches mostly repeat known findings;
- primary or authoritative sources support high-impact claims;
- material contradictions are resolved or disclosed;
- volatile evidence has a final-review trigger;
- the blueprint can be written without inventing facts.

## Phase 5 — Build The Evidence Map

Classify each meaningful statement before drafting:

| Reader-facing status | Meaning |
| --- | --- |
| Established | Verified current capability or operating fact. |
| Verified history | A dated fact supported by internal or public evidence. |
| Publicly stated | A first-party public claim whose wording and date are known. |
| Approved strategic direction | Owner-approved direction, not a current capability. |
| Interpretation | The agent or organisation's reasoned conclusion from evidence. |
| Illustrative option | A possible example, not a commitment. |
| Unsupported | Must not enter the publishable draft. |

Keep source class separate from reader-facing status. An owner decision may
support either an established internal fact or strategic direction, but those
statements must be expressed differently.

For governed documents, assign stable claim IDs and use one claim register as
the single source referenced by chapters, milestones, roadmap items, KPIs and
appendices.

## Phase 6 — Create The Blueprint

Use
[`templates/document-production/blueprint.md`](templates/document-production/blueprint.md).

The blueprint must define:

- title and subtitle;
- audience and reading paths;
- central narrative and proof hierarchy;
- positive-truth standard;
- explicit non-goals;
- chapter/section structure and purpose;
- visual ownership;
- evidence and citation model;
- terminology and brand rules;
- confidentiality treatment;
- update governance;
- required formats;
- deterministic and human acceptance criteria.

Keep numbering and visual ownership deterministic. Separate named systems,
products, brands, capabilities, future verticals and illustrative examples.

### Main owner checkpoint

For a new governed stakeholder or public/high-stakes document, Hafiz approves
the document contract and blueprint before the agent starts the full draft.

After approval, continue autonomously. Pause only if research reveals a
material conflict that changes the approved story, scope, confidentiality,
business meaning or acceptance rule.

## Phase 7 — Blueprint Challenge

Use an independent fresh-context reviewer for governed stakeholder and
public/high-stakes documents. The brief should be bounded and ask whether:

- the structure proves the central narrative;
- an important audience or workflow is missing;
- positive framing omits context that changes meaning;
- facts, strategy, interpretation and illustration are distinct;
- evidence and visual ownership are deterministic;
- sensitive information is protected;
- another writer could draft from the blueprint without guessing.

The reviewer critiques. Codex owns reconciliation, accepted direction and
final document changes.

## Phase 8 — Draft The Governed Master

Markdown is the default source of truth. Do not maintain independent competing
truth in HTML, PDF and DOCX.

Use this reader ladder for substantial chapters:

1. In plain language.
2. Why it matters.
3. How it works.
4. Technical or operational depth.
5. Evidence.
6. What it enables.

Write for non-technical readers first, then add technical depth. Define terms
before using acronyms or architecture language.

### Positive truth standard

Positive framing is welcome, but a positive claim must not omit material
context that would change a reasonable reader's interpretation.

Do not use:

- unsupported superlatives;
- self-awarded maturity scores;
- planned capability written in present tense;
- volatile sprint or completion percentages in an evergreen document;
- confidential economics or technical topology outside the approved audience;
- weakness lists when the document's purpose is capability communication.

Use a progress pattern such as:

```text
Foundation established -> capability expanded -> business value created ->
future leverage enabled
```

Stop that sequence honestly where the evidence stops.

## Phase 9 — Visual And Output Production

Every visual must explain a relationship more clearly than prose.

For self-contained HTML presentations, use
[frontend-slides.md](frontend-slides.md) for slide density, fixed-stage
rendering, navigation, local PDF export and slide-by-slide visual QA. This
document-production playbook continues to own the governed source, claims,
evidence, approved blueprint, adversarial review and publication boundary.

Use:

- flow for process;
- layered architecture for platform structure;
- matrix for ownership or system relationships;
- timeline for milestones;
- tree for capability-to-value relationships;
- roadmap for dependencies and horizons;
- mindmap for portfolio or expansion optionality.

For long documents with Mermaid diagrams:

```text
Mermaid source -> independent static SVG -> offline HTML/PDF
                              -> PNG fallback -> DOCX
```

Do not rely on client-side Mermaid rendering in a long headless-PDF job.

Default major-document package:

- governed Markdown master;
- standalone offline HTML;
- polished A4 PDF;
- editable DOCX;
- blueprint;
- evidence/claim register;
- diagram sources and generated assets.

Use metadata rather than hard-coded title/date/owner values in reusable
renderers. Do not generalise a renderer until it has been proven on a real
second document.

## Phase 10 — Deterministic Document QA

Check what machines can check before spending reviewer attention:

- required chapters, parts and appendices;
- sequential numbering and duplicate headings;
- broken internal links;
- claim IDs used versus registered;
- orphaned or duplicate claims;
- milestone, roadmap and KPI identifiers;
- forbidden terminology and unresolved placeholders;
- sensitive strings and prohibited details;
- output metadata and review date;
- generated-output freshness against the Markdown source;
- HTML completeness;
- PDF page count and required headings;
- DOCX text completeness and embedded media;
- expected diagram count.

Then visually inspect:

- cover and contents;
- representative dense tables;
- every diagram;
- page breaks around major headings;
- small labels and legends;
- final pages and appendices.

A successful render command does not prove readability.

## Phase 11 — Adversarial Review And Correction

Use
[`templates/document-production/adversarial-review.md`](templates/document-production/adversarial-review.md).

Challenge:

1. truth and evidence;
2. narrative credibility;
3. completeness;
4. technical or operational accuracy;
5. audience comprehension;
6. visual and output quality;
7. confidentiality and publication risk;
8. maintenance and freshness.

Classify findings:

- **Blocking:** unsafe, materially false, contradictory, unusable, or missing
  essential proof.
- **Material:** likely to change stakeholder interpretation, credibility, or a
  major decision.
- **Minor:** worth improving but does not invalidate acceptance.
- **Preference:** stylistic choice with no evidence or usability defect.

Correct blocking and material findings, regenerate affected formats, and use a
targeted correction review. If the same material disagreement survives two
correction cycles, pause for owner judgment instead of looping indefinitely.

## Phase 12 — Acceptance And Handoff

Use
[`templates/document-production/acceptance-checklist.md`](templates/document-production/acceptance-checklist.md).

Do not claim `100% perfect`. Use this measurable exit:

```text
Blocking findings remaining: 0.
Material findings remaining: 0.
Minor findings corrected or explicitly accepted.
Required deterministic checks pass.
Every diagram and representative document pages are visually inspected.
Final volatile claims are reverified.
The highest proven state and sharing boundary are explicit.
```

Final handback must say:

- what the document is for;
- which formats exist;
- which sources/evidence classes were used;
- what independent review occurred;
- what checks passed;
- what remains local-only;
- whether anything was committed or externally shared;
- when the document should next be reviewed;
- the single recommended next action;
- whether Hafiz needs to decide anything.

## Autonomous Packet Rules

After blueprint approval, the agent may autonomously:

- conduct in-scope internal and online research;
- draft and restructure the governed master;
- create and repair diagrams;
- generate local formats;
- run deterministic, visual and sensitive-content checks;
- commission bounded independent critique when an approved reviewer lane exists;
- reconcile evidence-backed findings;
- update the Session Map and save durable lessons.

Pause when:

- authoritative sources materially conflict;
- audience or confidentiality changes;
- unpublished financial, customer-private or sensitive data would be needed;
- a named country, product or launch becomes a commitment rather than an
  illustration;
- positive framing would become misleading;
- a material reviewer disagreement survives two correction cycles;
- commit, upload, publication or external distribution is next and was not
  already approved.

Default loop:

```text
choose next document slice -> research/draft -> check -> record evidence ->
continue or stop under the approved boundary
```

## Living-Document Updates

For an existing governed document:

1. Read the document contract, blueprint, claim register and last review note.
2. Identify the milestone or scheduled-review trigger.
3. Reverify affected and volatile claims.
4. Update the Markdown master and claim register together.
5. Regenerate every derived format.
6. Rerun deterministic and visual checks proportionate to the change.
7. Record version, review date, owner and major changes only.

Do not turn an evergreen sourcebook into a daily development tracker.

## Close-Out

Report:

```text
Status:
Meaning:
Governed source:
Generated formats:
Research and evidence:
Independent review:
Checks:
Highest proven state:
Publication/share state:
Recommended next:
Decision needed:
```
