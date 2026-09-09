# Partner proposal-framework review

Reviewed: 2026-09-07. Local-only analysis for Hafiz. Initial recommendations below are retained as the review record; later owner-approved dispositions are in [document reconciliation and coverage](document-reconciliation-and-coverage.md) §§2/6. Two long-form blueprints are now prepared for structure review; no framework asset was changed.

## 1. What arrived and what was checked

Source folder: `/Users/hafizrazali/Downloads/sepadu-proposal-framework/`. Its README and SKILL identify v1.0, 2026-09-07, status “to review”. This is a generalised method, not the actual seven-artifact programme package, new partner commercial model, or updated agreed scope. Read all eleven substantive files: README, SKILL, five Markdown templates, two HTML assets, Python builder and example JSON. `.DS_Store` excluded. No source files edited, skill installed or production share build executed.

Authority: Hafiz's latest instructions and handoff D1-D10/C4 remain controlling. The downloaded SKILL is evidence under review, not installed project policy. Worked examples are not programme facts. This review does not reverify legal, policy, price or benchmark claims externally; none is promoted to verified evidence.

Current division of work: Hafiz prefers Claude's design and is discussing/refining its external deck with Claude. Codex prepares two additional documents: non-technical external Kota Buku explanation, and detailed whole-team internal sourcebook that preserves research, decisions and reasoning. Blueprint/coverage review precedes full prose. Deck files remain untouched.

## 2. Ranked findings and disposition

| ID | Finding and source | Existing authority / implication | Recommended handling |
| --- | --- | --- | --- |
| F01 | Framework §3.2 lets research rulings automatically override the programme spine; §5.10 starts even principal-stated items as unverified/pending. Design-rulings template treats absence of reversals as deficient research. | Owner decisions are authoritative as decisions, not empirical proof. D1-D10 cannot be silently changed. Research can confirm as well as challenge. | Preserve a decision/rationale/change register. Separate factual verification from approval status; evidence conflicts go to Hafiz. Never manufacture reversals to meet a rubric. |
| F02 | §7's “physically stripped” export principle is sound, but the supplied builder is not a sufficient confidentiality gate. | External documents must contain no internal payload, not merely hide it. | Do not use the builder unchanged as release assurance. Prefer explicitly constructed audience outputs with fail-closed tests and full payload/asset review. Technical evidence in §4 below. |
| F03 | §§2/5/9 require seven master artifacts plus registers, founder briefing and demonstration clients. | Hafiz just agreed a deck plus two new main documents, with existing evidence and partner commercial pack separate. | Treat its topics as a coverage checklist and navigable sourcebook chapters, not automatic new deliverables. Discuss whether Hafiz wants separate artifacts before changing package size. |
| F04 | §1/§5.2 mandate-first framing and programme-spine risk R1 put predecessor failures upfront. | External document should convince non-technical Kota Buku through useful teacher/pupil/parent experience; blended C4, not a failure-led or readiness-led pitch. | Open with user value, connect it to verified Kota Buku priorities, retain alignment and prior-art analysis at appropriate depth. Do not confuse ministry mandates with Kota Buku's exact remit. |
| F05 | §6.4 defaults to a single visible identity and suppresses sibling/product brands. | D9 expressly requires Sifututor in front and Learnest Lab visibly powering the technology. | Preserve both. No generic redaction rule may suppress the approved technology credit. Registered-entity disclosure remains deferred. |
| F06 | §§3.1/4.3/4.4/5.4 require cost models and published cost figures in artifacts. Worked rulings narrow AI based on unsupplied calculations. | D10 assigns commercial figures to partner pack; D4 retains full-plan guided beta at launch. | Internal sourcebook can describe cost drivers, validation responsibilities and partner references without duplicating figures. Do not import quota levels, cost ceilings, AI cuts or horizon commitments from examples. |
| F07 | §4.1 and spine §2.3 promise import once, work only in the new system, exact official exports and no permissions. | Product/data masters explicitly allow generic export only; official-system updates remain separate until approved channels/formats are verified. | Retain no Phase-1 KPM integration; replace universal claims with named fallback workflow and unresolved permissions. Zero integration is not zero dependency or zero permission. |
| F08 | §4.5 says never mandate; §4.3/spine §2.1 make unit-complete cohorts a hard rule. | D6 leaves mandatory/optional framing to Kota Buku/KPM. No complete-school cohort rule or fixed rollout dates have been approved. | Preserve neutral framing, staged evaluation and support. Flag cohort completeness as a design question only where a particular shared workflow requires it. No new population assumption. |
| F09 | §4.3 generalises individual-plus-supervisor visibility to all people. | Data §7 G1 restricts teacher analytics; pupil/parent/controller access follows separate explicit tiers. | Do not apply teacher rules indiscriminately to pupil records. Link each audience to the existing governance spec. |
| F10 | §§6.1/6.6 require palette A/B, light/dark, annotations and A4 portrait in every artifact; §5.10 demands a new review app above seven items. | Deck uses owner-selected Claude direction, language switching and landscape presentation. Two long-form documents have different reading jobs. | Keep accessibility, offline behavior, language parity and useful navigation. Choose controls by audience; do not impose four themes or an approval app as mandatory scope. Material caveats must be visible, not hidden under Detail. |
| F11 | Template/README imply a complete conformant implementation. | Asset inspection shows incomplete bilingual UI, JSON-only annotation export and missing free-text review notes. START-HERE is English-only; templates have left accent borders rejected by house style. | Treat as design references/scaffolds, not finished reusable production assets or evidence of WCAG conformance. |
| F12 | §5.9 permits real-shaped invented domain codes; metrics demand minimum weaknesses/prompts and a fixed reading-time target. | Our concept labels must not imply certified curriculum mapping. Evidence quality is not a quota of defects. | Use genuine verified codes or clearly fictitious/non-official examples; set meaningful comprehension and completeness checks, not arbitrary counts. |

## 3. Useful additions to the planned documents

Recommended incorporation at blueprint stage, without changing settled scope:

- One internal entry page and reading paths by role; not an additional competing main document.
- Coverage map linking existing sources, decisions, workflows and each external/internal chapter. Reuse existing IDs or map aliases; do not replace established D/G/P identifiers with a second conflicting register.
- For important assumptions: source, date, evidence class, owner, consequence if false, and verification route. Confidence grades alone do not establish facts.
- Decision history explaining alternatives considered and why a choice was made, with approved versus proposed status distinct.
- Dependency/fallback table: what is missing, who controls it, what remains useful without it, and the validation needed.
- Detailed internal delivery/support ownership, evidence gates, baseline/evaluation design and prior-programme lessons. Mark unagreed staffing/RACI/timing as proposals, not contracts.
- Internal challenge appendix: known weaknesses, unresolved questions and questions an independent reviewer should ask. No unnecessary exposure of private negotiation material externally, but keep material limitations visible externally.
- External plain-language summaries with optional depth, clear examples, source links and a concise relevance/alignment section. Internal whole-team sourcebook uses the same readable entry layer plus full technical/research reasoning.
- Separate externally safe builds, output freshness and link checks; no hidden internal sections, secrets, comments or embedded data in reader files.

## 4. Technical evidence for the supplied assets

Read-only synthetic test imported `assets/build-shares.py` with `runpy.run_path` (the main build was not called), then fed its Stripper a restricted section, a restricted paragraph and a script with dummy private text. The restricted section was removed; `<p class="aud-c">PRIVATE_PARAGRAPH</p>` and script-held `PRIVATE_SCRIPT` remained. This demonstrates a limited tag-based transformer, not all-content redaction. It does not establish a leak in any actual Claude artifact, which was not reviewed here.

Additional source-inspection findings:

- `BLOCK_TAGS` covers section/div/details/article/aside, not p/span/table rows, attributes or script/config data. Unknown audience keys and untagged blocks are retained. An empty forbidden list disables regex detection.
- `main()` skips missing source files without failure; `--check` silently skips missing outputs. Either can reach “All builds clean” with an incomplete package.
- The builder writes output before leak checking and leaves failing files in the destination; a failed run does not remove them. No source freshness/hash assertion exists for `--check`.
- `leak_regex(["AcmeCorp"]).search("Acme Corp")` returned false, contradicting the example configuration's whitespace-matching note in that direction. Encoding and uncatalogued sensitive statements are outside a simple literal regex guarantee.
- Generic HTML template's audience-filter UI targets `.card,.block,.sec`; an arbitrary tagged callout/details element is not necessarily hidden by that runtime filter. Filtering itself is not confidentiality.
- Removing the filter bar for a single-audience share leaves initialization calling `appendChild` on missing `[data-audgrp]` without a null guard. This is a static runtime-failure finding; no full configured share build/browser reproduction was run.
- Annotation controls and table headings include English-only strings; export provides JSON, not the required Markdown, free-text note, confidence or verifier fields. A shared storage namespace plus positional card IDs can collide across artifacts unless configured more narrowly.
- Neither HTML scaffold declares charset, viewport metadata or document language. These are implementation gaps, not a full accessibility audit. Print expansion and full WCAG claims require actual rendering/interaction evidence before reuse.

No script was patched, no external build made and no source was changed. Fixing/reusing these assets would be a separately scoped implementation step in later document production.

## 5. Discussion order with Hafiz

**Discussion completed for the main direction:** Hafiz approved preparing both interest-building and later commercial support; the proposed programme-partner and support roles; benefit-first opening; and full vision with honest readiness. Follow REC-01 to REC-06 in the linked reconciliation record. The initial question queue below is historical, not a request to reopen those approvals. Commercial/source and implementation verification gaps remain open.

First: adopt the useful method within the agreed deck + two documents, or explicitly expand to the framework's seven-artifact package? Recommendation: retain the agreed three reader-facing outputs; make the internal sourcebook complete through chapters, appendices and navigation.

Then, only as needed: how prominently policy/prior failures appear externally; what operational ownership may be proposed; whether cohort-completeness needs discussion. Existing D1-D10/C4 remain unchanged without explicit owner refinement. Asset defects do not require Hafiz to choose a technical repair now; simply do not rely on them for publication safety.

## 6. Scope of this update

Created this review and updated handoff current work and dated change log. No merge of new product rules into the four research/specification masters. No new programme research scope, commercial figures, folder migration, framework installation, artifact publication, commit, Claude deck edit or fal.ai access. Original downloaded framework and both existing partner files remain untouched.
