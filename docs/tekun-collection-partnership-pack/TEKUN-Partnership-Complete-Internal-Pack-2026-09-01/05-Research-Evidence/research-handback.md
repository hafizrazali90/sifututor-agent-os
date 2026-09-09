# Research Handback

**Assignment:** deep online research and a governed research reference pack for a
proposed TEKUN Corporation collection partnership.
**Completed:** 31 August 2026, Asia/Kuala Lumpur.
**Governing workflow:** `docs/agent-playbooks/document-production.md`, governed
stakeholder lane, research phases only.
**Next owner:** Codex.

---

## 1. What was completed

| Phase | Done |
| --- | --- |
| Workflow setup | Read `AGENTS.md`, parent `CLAUDE.md`, `document-production.md`, and the document-contract, claim-register and adversarial-review templates |
| Memory | Searched Koda at session start and again at save time. The document-production workflow memory (`mem_2c6f205f69cb`) was found and followed. **Correction:** the session-start search returned empty for TEKUN, but two prior TEKUN memories do exist and were found on the save-time search - see the note below |
| Repository state | Checked `git status`. All pre-existing modifications preserved and untouched |
| Session Map | Created `.agent-os/session-maps/2026-08-31-113513-claude-tekun-collection-research.md` |
| Pass A - landscape discovery | Terminology, entities, regulators, legislation, TCorp's public model, its collection ecosystem, procurement structures, technology categories, operating and commercial models |
| Pass B - evidence-grade investigation | Every material claim traced to an opened primary source. Four PDFs downloaded and read in full |
| Pass C - contradiction and reverification | All volatile regulatory sources reopened before completion; eight contradictions logged; four corrections applied |
| Adversarial review | Full checklist run; six findings raised and corrected; zero blocking and zero material findings remain |
| Deterministic checks | File completeness, internal links, claim and source ID integrity, forbidden terminology, placeholders, sensitive content, Mermaid block integrity |

### Koda correction, recorded honestly

The session-start Koda search (query "TEKUN collection debt recovery partnership
proposal") returned an empty result. A second search at save time, using the
query "TEKUN Corporation collection partnership research pack", returned two
pre-existing memories:

| ID | Content |
| --- | --- |
| `mem_39afdedaea41` | TEKUN Corporation, not TEKUN Nasional, is the direct client; TCorp owns and governs the platform; the delivery partner builds, operates, maintains and improves it and performs authorised collection work. Portfolios may originate from appointing organisations, but this must not be assumed for any named principal until confirmed |
| `mem_1b967f573b0e` | TEKUN owns and controls the platform while Sifututor develops, operates and improves it; durability comes from outcomes, operating knowledge, integrations, governance and continuous improvement, not data hostage or opaque lock-in; external wording uses long-term capability partnership language |

**Effect on this pack: none adverse.** Both memories are consistent with the
owner-confirmed direction in the assignment brief and with what this pack
concluded independently. `mem_39afdedaea41`'s caution that portfolio origin "must
not be assumed for any named principal until confirmed" is the same discipline
applied throughout the third-party file.

**Effect on process: a real lesson.** The first search missed relevant memories
that existed. Future sessions should not treat a single empty Koda search as
proof that no prior context exists - vary the query and search again before
concluding a topic is new. Stored as `mem_8e0c6fd263e3`'s companion lesson.

---

## 2. Files created

All under `docs/tekun-collection-research/`. Nothing else in the repository was
modified.

| File | Purpose |
| --- | --- |
| `README.md` | Purpose, scope, index, evidence classifications, freshness rules, disclaimers |
| `executive-research-brief.md` | Non-technical summary, strongest findings, implications, unknowns, cautions |
| `tekun-corporation-profile.md` | Entity, mandate, collection business, clients, 2026 appointments, governance |
| `current-third-party-and-commercial-model.md` | Research areas C, D, E, M: who hires TCorp, who TCorp hires, money flow, fees, transition |
| `regulatory-and-responsible-collection.md` | Research areas F, G, H: the Act, the regulator's standards, PDPA, responsible practice |
| `operating-model-and-stakeholders.md` | Research area I: stakeholder map, RACI, governance layers, escalation, assumptions |
| `platform-capability-benchmark.md` | Research area J: nine capability domains, tiered, with regulatory linkage |
| `performance-and-commercial-framework.md` | Research areas K, L: full KPI dictionary, baseline and pilot design, commercial archetypes |
| `partnership-durability-strategy.md` | Research area N: value-based retention, ethical boundaries, external-safe wording |
| `unknowns-and-discovery-questions.md` | Research area O: 82 TEKUN questions, our own questions, legal, compliance, finance, executive, prioritised agenda, 30 documents to request |
| `claim-register.md` | 114 registered claims with classification, confidence, source, limits, freshness and permitted use; contradiction log |
| `source-register.md` | 36 registered sources with URLs, dates, type, authority, quality notes; broken-URL corrections |
| `adversarial-review.md` | The challenge pass, findings, corrections, mechanical checks, limitations |
| `research-handback.md` | This file |

Plus the Session Map at
`.agent-os/session-maps/2026-08-31-113513-claude-tekun-collection-research.md`.

---

## 3. Research method used

Three passes, as required.

- **Pass A** established terminology in both Bahasa Melayu and English, identified
  the entities and regulators, and mapped the two relationship layers.
- **Pass B** opened the underlying source for every important claim. Search results
  were used only to locate sources, never as evidence. Four PDFs were downloaded
  and read in full: the Consumer Credit Act 2025 (134 pages), the SKP Conduct
  Standards (97 pages), the SKP Authorisation Standards (43 pages), and the
  Auditor-General's report on TEKUN Nasional. Two further primary PDFs were read:
  the PDPA Amendment Act A1727 and its commencement gazette P.U. (B) 522, plus the
  Data Breach Notification Guideline and the CGAP consensus guidelines.
- **Pass C** reopened every volatile regulatory source before completion, which
  produced four corrections including the Part V commencement boundary and the
  regulator's phased approach.

Searches were run in both languages using the suggested terms and beyond them.

---

## 4. Strongest conclusions

1. **TEKUN Corporation is an established collection business, not a prospect
   starting from zero.** Company 1082602-T, SSM-registered 27 February 2014,
   subsidiary of TEKUN Nasional, running a Customer Call Centre for debt
   collection since 15 September 2015, registered with MOF under field code
   221105, and stating that 30 agencies and companies have appointed it.

2. **Its collection business was visibly expanding during 2026.** Awqaf Education
   Sdn Bhd on 7 May 2026, and MOCCIS across three events on 7 July, 23 July and
   7 August 2026, the last witnessed by the Minister of Entrepreneur Development
   and Cooperatives.

3. **The regulatory position changed fundamentally in 2026 and readiness is
   time-sensitive.** The Consumer Credit Act 2025 took effect 1 March 2026 except
   Part V; Part V, covering licensing and registration, took effect 1 June 2026.
   For an existing affected operator, section 135(1) requires an application
   within six months from that date. Section 57 creates an offence for carrying
   on an applicable credit service business without registration and Schedule 7
   excludes that breach from the section 106 administrative monetary-penalty
   route. Applicability, status and enforcement consequences require legal and
   regulatory confirmation before use in any TEKUN-facing material.

4. **The conduct rules are specific enough to function as a product
   specification.** Contact only 8am to 9pm. No more than 3 contacts per week or
   12 per month. A written 7-day recovery notice with six mandatory disclosures.
   Identity verified before any debt discussion. No disclosure to spouse or
   family without explicit written consent. No agent may accept payment. Recovery
   must cease immediately on settlement. Records of all communication attempts
   retained. Detection of unusual viewing and downloading of consumer data.

5. **Accountability cannot be outsourced.** The authorised entity remains
   accountable for its representatives' conduct, an outsourced collector must
   itself be SKP-registered, and an offence by an agent is deemed committed by
   the principal.

6. **Whether the Act applies to TEKUN's portfolios is genuinely unresolved.**
   Schedule 1 excludes credit provided by entities receiving government funding
   to run micro-financing schemes, which appears to describe TEKUN Nasional. But
   TCorp collects for around 30 principals, including co-operatives and motor
   dealers, and the analysis differs for each. This requires legal counsel.

7. **The regulatory perimeter is still widening.** Phase 2 will move hire purchase
   and credit sales from KPDN, and moneylending and pawnbroking from KPKT, to
   SKP. Three of TCorp's named clients are motor dealers, so the transfer may
   become relevant if their assigned portfolios involve those products. The
   actual portfolio products are not publicly disclosed, and no Phase 2 date is
   published.

8. **A partner operating the platform may carry direct data-protection duties.**
   If the partner is legally a data processor, the amended PDPA extends the
   Security Principle and applicable DPO obligations to that processor. The
   actual controller-processor relationship, thresholds and resulting duties
   require confirmation from counsel and the parties' compliance functions.

---

## 5. Direct answers to the questions asked

| Question | Answer |
| --- | --- |
| **Current third party identified?** | **No.** Searched thoroughly in both languages across TCorp's site, TEKUN Nasional's procurement pages, government procurement portals, the Auditor-General's report and news. **Not publicly disclosed.** Absence of evidence is not evidence of absence |
| **Provider role verified?** | **No.** No provider identified, so no role could be verified |
| **Contract value verified?** | **No.** No contract value for TCorp's collection business was found in any public source. The MOCCIS and Awqaf announcements disclose no values |
| **Commission model verified?** | **No.** No commission percentage, success fee, management fee, per-account or per-agent fee was found. **Not publicly disclosed** |
| **Who appoints TCorp?** | **Answered.** Around 30 agencies and companies, at least 24 identifiable, plus two documented 2026 appointments |
| **Current regulatory requirements?** | **Answered in detail** from the Act, the gazette, and the regulator's own standards and FAQs, all reverified on 31 August 2026 |

---

## 6. Contradictions found

| ID | Issue | Status |
| --- | --- | --- |
| CON-001 | Transition window direction: a secondary summary said it ended 1 June 2026 | **Resolved** by the Act and both regulator releases. It begins 1 June 2026 |
| CON-002 | CGAP treatment of restructured loans in PAR | **Resolved** by the primary document, which excludes them |
| CON-003 | Whether the Act applies to TEKUN's portfolios | **Open and disclosed.** Requires legal counsel |
| CON-004 | TCorp's client count of 30 is undated and may predate 2026 appointments | **Disclosed.** Always attribute and reverify |
| CON-005 | TCorp's published objectives omit collection | **Disclosed** as an observation, not a conclusion |
| CON-006 | Whether an incumbent third-party provider exists | **Disclosed** as not publicly disclosed |
| CON-007 | MOF code 221105 label variants | **Resolved.** Only TCorp's first-party wording is cited |
| CON-008 | ADMP guideline status, final or in consultation | **Open.** Must be checked before designing automated prioritisation |

---

## 7. Unverified assumptions, clearly labelled

Ten operating assumptions are listed at
[operating-model-and-stakeholders.md §8](operating-model-and-stakeholders.md#8-labelled-assumptions),
each with the risk if wrong and a confirming question. The most consequential:

- that TCorp retains settlement, write-off and legal-escalation authority;
- that customers pay into the principal's or authorised entity's account;
- that TCorp is the data controller and a partner would be a data processor;
- that partner staff could act as TCorp's representatives under its authorisation
  rather than needing separate registration.

The probable money-flow diagram is **explicitly marked unverified** and is
prohibited from external use.

---

## 8. Recommended proposal narrative

> **Modernise, integrate, scale and continuously improve TEKUN Corporation's
> established collection and credit-recovery business** - with TEKUN Corporation
> owning and governing the platform, and our team building, operating and
> improving it under TEKUN Corporation's policy and authority.

Three supporting arguments, in order of strength:

1. **Provable conduct compliance.** The new rules are precise and testable, and
   accountability stays with the authorised entity. A platform that enforces
   contact windows, frequency caps, notice periods, identity verification and
   cessation triggers, and can prove it did, converts a regulatory burden into an
   operating asset.
2. **Multi-principal capacity.** TCorp added two principals in 2026. Its
   constraint is plausibly the ability to take on more principals safely.
3. **Evidence for its own clients.** Around 30 principals each need reporting they
   can trust. Reporting quality is a retention asset for TCorp.

Commercial direction: **a bounded pilot first**, because it limits risk, supports
regulatory readiness, and produces the baseline that no public source supplies.
Then **a hybrid fixed-plus-performance structure**, because pure
commission creates exactly the pressures the conduct rules exist to prevent, and
the regulator requires collection remuneration to promote fair outcomes.

**Propose no price yet.** Ten Tier-1 unknowns block it.

---

## 9. Exact next action for Codex

1. **Read this file, then `README.md`, then `executive-research-brief.md`.**
2. **Before writing any proposal content, read `claim-register.md`** and treat the
   DO NOT USE rows as hard constraints. There are eight of them.
3. **Reverify the regulatory claims** before any external use. Freshness rules are
   in `README.md` §6; the regulatory claims require monthly reverification until
   31 December 2026.
4. **Do not fill any "Not publicly disclosed" gap with a benchmark.** Convert it
   into a discovery question instead. The questions already exist.
5. **The single recommended next step in the real world:** put the ten Tier-1
   discovery questions to TEKUN Corporation, leading with the SKP registration
   question. That question is the most time-sensitive, and asking it is genuinely
   useful to them rather than a sales move.

### If Codex disagrees with anything here

Every claim carries a source ID. Reopen the source. The primary documents are
listed with direct URLs in `source-register.md`, and four of them are large PDFs
that were read in full. Disagreement should be resolved against the source, not
against this summary.

---

## 10. Boundary compliance

| Boundary | Status |
| --- | --- |
| Write the final stakeholder proposal | **Not done.** Research and documentation only |
| Implement software | **Not done.** No product code touched |
| Decide final pricing | **Not done.** Pricing explicitly blocked behind ten unknowns |
| Claim legal compliance | **Not done.** All legal applicability flagged for counsel |
| Contact TEKUN or any external party | **Not done.** No contact of any kind |
| Commit | **Not done** |
| Push | **Not done** |
| Upload or publish | **Not done** |
| Read or modify `.env*` | **Not done** |
| Touch anything under `live/` | **Not done** |
| Preserve unrelated working-tree changes | **Done.** Only new files under `docs/tekun-collection-research/` and one new Session Map were created. No pre-existing file was modified. The 37 modified tracked files in the working tree are all pre-existing and were untouched |

### One thing Hafiz should know about where this lives

This umbrella repository uses an allowlist `.gitignore`: line 3 ignores
everything (`*`), and only named paths are re-included. Under `docs/`, only
`docs/agent-playbooks/**` and `docs/onboarding/**` are tracked, because
`.gitignore` line 12 re-ignores `docs/*`.

**Consequence:** `docs/tekun-collection-research/` exists on disk but git does not
see it, and neither does `git status`. The same applies to the Session Map, since
`.agent-os/session-maps/` is not in the allowlist either.

That is the repository's deliberate design, not a mistake, and it does not affect
this assignment because committing was outside the approved boundary. But if the
pack should be version-controlled or shared through the repo, a negation rule
such as `!docs/tekun-collection-research/` plus
`!docs/tekun-collection-research/**` would be needed first. **That is Hafiz's
decision, not an action taken here.**

---

## 11. Close-out

```text
Status:              Research pack complete and locally reviewed.
Meaning:             Codex now has an evidence-backed base for a TEKUN Corporation
                     stakeholder document, with every gap converted into a question.
Governed source:     docs/tekun-collection-research/ (13 Markdown files)
Generated formats:   Markdown only. No HTML, PDF or DOCX was requested or produced.
Research and evidence: 36 registered sources; 114 registered claims; primary
                     legislation, gazette notification, regulator standards,
                     government audit report and first-party publications, all
                     opened and read. Two search-snippet errors caught and corrected
                     against primary sources.
Independent review:  Adversarial self-review complete; 6 findings raised and
                     corrected; 0 blocking, 0 material remaining; 3 minor accepted
                     and disclosed. NOT an independent fresh-context review.
Checks:              File completeness, internal links, claim and source ID
                     integrity, forbidden terminology, placeholders, sensitive
                     content, Mermaid integrity, volatile-source reverification.
                     All passed.
Highest proven state: Complete governed research pack, local only.
Publication/share state: Nothing committed, pushed, uploaded, published or shared.
Recommended next:    Take the ten Tier-1 discovery questions to TEKUN Corporation,
                     leading with SKP registration status.
Decision needed:     Whether to approach TEKUN Corporation now, and whether to
                     commission independent fresh-context review of the legal
                     interpretation before any external document is drafted.
```
