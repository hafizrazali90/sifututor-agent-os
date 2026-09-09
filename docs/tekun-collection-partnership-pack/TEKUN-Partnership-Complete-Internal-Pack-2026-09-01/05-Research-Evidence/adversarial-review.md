# Adversarial Review - TEKUN Collection Research Pack

**Review date:** 31 August 2026. **Reviewer role:** critique of the pack against
the research brief's own adversarial checklist. **Method:** fresh re-read of
every file against the primary sources, plus mechanical checks.

---

## 1. Review contract

- **Artifacts reviewed:** all 13 files in `docs/tekun-collection-research/`
- **Governing workflow:** `docs/agent-playbooks/document-production.md`, governed stakeholder lane
- **Audience and confidentiality:** internal research pack; not for external distribution; contains no confidential TEKUN information because none was available
- **Forbidden actions during review:** no commit, push, upload, publication or external sharing. None were performed
- **Limitation of this review:** it was conducted by the same agent that produced the pack. It is a disciplined self-challenge, **not an independent fresh-context review.** An independent reviewer would add value, particularly on the legal-interpretation sections

---

## 2. Verdict

| Severity | Count |
| --- | ---: |
| Blocking | 0 |
| Material | 0 |
| Minor | 3 (accepted, disclosed) |
| Preference | 2 (accepted) |

All findings raised during the review that were Blocking or Material were
corrected before this file was written. They are recorded below with their
corrections so the correction history is auditable.

---

## 3. Findings raised and corrected during review

### F-001

```text
ID:            F-001
Severity:      Material (corrected)
Location:      regulatory-and-responsible-collection.md §6.6
Reader impact: The pack asserted "ISO/IEC 27001 is the widely recognised standard
               for information security management systems" while simultaneously
               stating that no ISO claim is made anywhere. That is an internal
               contradiction, and it is a content claim sourced from model
               recollection rather than an opened source.
Evidence:      iso.org/standard/27001 returned HTTP 403; the page was never read.
Required fix:  Remove the characterising sentence; state only that the source was
               inaccessible, that no claim is made, and that no secondary source
               was substituted. Redirect the reader to the verified Malaysian
               security requirements instead.
Verification:  §6.6 rewritten. All 10 remaining ISO mentions across the pack are
               now prohibitions or gap records. Confirmed by grep.
```

### F-002

```text
ID:            F-002
Severity:      Material (corrected)
Location:      All 12 files
Reader impact: The pack used 523 em dashes, violating Hafiz's standing rule that
               em dashes must never appear in copy, UI, docs or comments.
Evidence:      Standing instruction in the global adapter and auto-memory
               [[feedback_no_emdash]].
Required fix:  Remove every em dash. Standalone table-cell dashes became "n/a";
               spaced em dashes became spaced hyphens.
Verification:  grep for the character across all files returns zero. Mermaid
               blocks and RACI tables re-inspected after replacement and render
               correctly.
```

### F-003

```text
ID:            F-003
Severity:      Material (corrected)
Location:      regulatory-and-responsible-collection.md §2; executive-research-brief.md §2
Reader impact: The pack said "the Act came into force 1 March 2026" without the
               Part V carve-out. The regulator states it more precisely: except
               for Part V, the Act took effect 1 March 2026, and Part V - which
               covers licensing and registration - took effect 1 June 2026. The
               looser wording could mislead a reader into thinking registration
               duties bit from March.
Evidence:      SKP FAQs, reverified 31 August 2026 (SRC-036).
Required fix:  State the Part V boundary explicitly in both files.
Verification:  Both files corrected; CLM-109 added to the claim register.
```

### F-004

```text
ID:            F-004
Severity:      Material (corrected)
Location:      regulatory-and-responsible-collection.md; executive-research-brief.md
Reader impact: The pack omitted the regulator's phased approach entirely. Phase 2
               moves hire purchase and credit sales from KPDN to SKP. Three of
               TEKUN Corporation's named clients are motor dealers. If portfolios
               assigned by those clients involve those products, the future
               transfer may become relevant. Omitting this conditional point
               understated the regulatory trajectory that TCorp should assess.
Evidence:      SKP FAQs (SRC-036); TCorp client panel (SRC-016).
Required fix:  Add the phased-approach table, make the motor-dealer implication
               conditional on confirmed assigned products, and note that no
               Phase 2 date is published.
Verification:  Added to the regulatory file and the executive brief; CLM-110 and
               CLM-111 added, with CLM-111 marked Interpretation.
```

### F-005

```text
ID:            F-005
Severity:      Material (corrected during research, not after)
Location:      Would have affected regulatory-and-responsible-collection.md §2
Reader impact: A secondary summary stated the CCA transition period was "six
               months ending 1 June 2026". Had that been used, every deadline in
               the pack would have been wrong by six months, and the single most
               time-critical finding would have been inverted.
Evidence:      Act 873 s.135(1) requires application within six months FROM the
               appointed date; MOF release 2 March 2026 and SKP release 5 June
               2026 both describe a six-month window beginning 1 June 2026.
Required fix:  Use the primary sources; log the contradiction.
Verification:  CON-001 logged in the claim register. The snippet was never used.
```

### F-006

```text
ID:            F-006
Severity:      Material (corrected during research, not after)
Location:      Would have affected performance-and-commercial-framework.md §1
Reader impact: A search summary claimed CGAP/MicroRate standards are "explicit
               that rescheduled and restructured loans belong in the PAR
               numerator regardless of payment status". The CGAP primary document
               says the opposite at item B3, and treats inclusion as a disclosure
               choice at R11. Using the snippet would have embedded a wrong
               formula into a framework intended to govern payment.
Evidence:      CGAP Microfinance Consensus Guidelines, items B3 and R11 (SRC-029).
Required fix:  Use the primary text; log the contradiction prominently.
Verification:  CON-002 logged; the contradiction is stated in the KPI file itself
               as a worked example of why snippets are not evidence.
```

---

## 4. Checklist from the research brief

Each item was tested, not assumed.

| # | Risk | Test applied | Result |
| --- | --- | --- | --- |
| 1 | **Entity confusion** | Every TEKUN Nasional fact traced to its source and checked for a label | **Pass.** All TEKUN Nasional material is labelled "TEKUN Nasional context". CLM-090 explicitly marks attributing audit findings to TCorp as DO NOT USE. The profile file carries an entity warning against merging the two registration numbers |
| 2 | **Client versus vendor confusion** | Checked every mention of the ~30 organisations | **Pass.** Consistently described as organisations that appointed TCorp. The third-party file opens with a two-layer diagram and an explicit "most common error to avoid" note. CLM-020 states the distinction; CLM-021 marks the inverse as DO NOT USE |
| 3 | **Outdated regulations** | All regulatory sources reopened on 31 August 2026 during Pass C | **Pass.** Dates now carry the Part V precision from the regulator's own FAQ. Freshness rules require monthly reverification until 31 December 2026 |
| 4 | **Legal overstatement** | Searched for any assertion that the Act does or does not apply, or that anything is compliant | **Pass.** CON-003 is left explicitly open. Thirteen questions in the regulatory file and fifteen in the discovery file are marked as requiring counsel. All four "compliant" hits in the pack are prohibitions |
| 5 | **Unsupported provider names** | Searched for any named third-party collection vendor | **Pass.** None. CLM-017 records the negative finding; CLM-021 forbids naming one |
| 6 | **Invented commercial terms** | Checked every fee, rate and value | **Pass.** The only quantified money figures are regulator-published: RM500,000 equity, RM5,000-RM50,000 annual fees, RM300,000 MSE threshold. All TEKUN commercial terms are marked "Not publicly disclosed in the sources reviewed" |
| 7 | **Unsupported figures** | Traced every number to a source | **Pass.** TEKUN Nasional figures carry their years and entity label. TCorp's "30" is flagged as undated and attributed to TCorp |
| 8 | **Search snippets used as evidence** | Reviewed how each search result was used | **Pass.** Every search led to a primary source that was then opened. Two snippet errors were caught (F-005, F-006). A third, the MOF code label, was noted and deliberately not relied upon (CON-007) |
| 9 | **Weak sources** | Reviewed the source register authority column | **Pass.** Legislation, gazette, regulator standards and a government audit carry the load. The inaccessible ISO source was left unread rather than substituted |
| 10 | **Missing contradictions** | Reviewed against the research log | **Pass.** Eight contradictions logged, including three left open and disclosed |
| 11 | **Benchmark rates as TEKUN facts** | Checked the commercial file | **Pass.** No rate appears anywhere. Archetypes carry no numbers. CLM-098 marks the error as DO NOT USE |
| 12 | **Unfair criticism of incumbents** | Checked the transition file | **Pass.** No incumbent is identified, and the pack explicitly forbids "your current provider is failing" and "TEKUN has no collection capability" |
| 13 | **Misuse of "grant recipient"** | grep | **Pass.** All three occurrences are prohibitions |
| 14 | **Profit guarantees** | grep on "guarantee" | **Pass.** All non-"limited by guarantee" hits are prohibitions or the explicit "No profit is guaranteed" statement |
| 15 | **Unethical lock-in language** | Reviewed the durability file | **Pass.** The internal phrase is named and forbidden externally. Seven prohibited practices are listed with alternatives. A transition-readiness commitment is included |
| 16 | **Missing transition considerations** | Reviewed against the brief's list | **Pass.** Eleven transition areas covered, including in-flight complaints, live legal matters, reconciliation during transition, and the registration-deadline collision |
| 17 | **Missing compliance controls** | Cross-checked Conduct Standards Chapter 12-16 against the platform file | **Pass.** A traceability table maps 15 rules to controls; the platform file marks organisational-only controls as not solved by software |

---

## 5. Additional challenges applied

Beyond the brief's checklist.

| Challenge | Result |
| --- | --- |
| Does the pack ever present the unverified money flow as real? | **No.** The diagram carries a warning heading, dashed edges, "UNVERIFIED" on every step, and CLM-025 marks external use as prohibited |
| Does it claim TEKUN is already a client? | **No.** CLM-106 marks it as false and DO NOT USE; the README disclaimers repeat it |
| Is the recommended narrative actually supported? | **Yes, and it is labelled.** CLM-103 is marked Interpretation, with its six supporting claims listed |
| Is "hybrid fixed plus performance is best" overreach? | **Partly, and it is labelled.** CLM-105 is marked Illustrative option, reasoned from the fair-outcomes rule and the absence of a baseline. It is not presented as a decision |
| Does the pack write proposal content it was told not to write? | **No.** It produces framing guidance and prohibited-claim lists, not proposal prose |
| Does it decide pricing? | **No.** Section 9 of the commercial file blocks pricing behind ten Tier-1 unknowns |
| Are negative findings honest about their limits? | **Yes.** Each states that absence of evidence is not evidence of absence, and each names the search perimeter |
| Does the KPI framework risk creating perverse incentives? | **Addressed.** Each KPI carries a misinterpretation risk; conduct measures target zero; compliance reports separately from performance |
| Is the Malaysian source hierarchy respected over international benchmarks? | **Yes.** The responsible-collection table separates binding Malaysian rules from benchmark-only gaps |
| Are the diagrams honest about certainty? | **Yes.** Verified flows use solid edges; unverified use dashed edges with explicit labels |
| Was anything committed, pushed or shared? | **No.** Working tree only |
| Were any prohibited files touched? | **No.** No `.env*`, no `live/`, no credentials |

---

## 6. Minor findings, accepted and disclosed

```text
ID:            M-001
Severity:      Minor (accepted)
Location:      platform-capability-benchmark.md
Reader impact: Only one product vendor's first-party documentation was reviewed in
               depth, so capability vocabulary leans on Microsoft Dynamics 365
               terminology. A reader could mistake vendor naming for industry
               standard naming.
Why accepted:  The limitation is disclosed twice - in §1 and in the gaps table at
               §13 - and every benchmark row is marked as a benchmark rather than
               a requirement. The binding requirements come from the Malaysian
               regulator, not the vendor.
Follow-up:     Gap G16. Review three or four further platforms before any external
               capability comparison is published.
```

```text
ID:            M-002
Severity:      Minor (accepted)
Location:      regulatory-and-responsible-collection.md §6.4
Reader impact: Five of the six Personal Data Protection Commissioner guidelines
               were identified but not read. Data-design advice therefore rests on
               the Act, the gazette and the one guideline that was read.
Why accepted:  Disclosed in the file, in the source register (SRC-013) and as gap
               G14. No claim is made about the unread guidelines beyond their
               existence.
Follow-up:     Open them before any data-handling commitment, especially ADMP and
               cross-border transfer.
```

```text
ID:            M-003
Severity:      Minor (accepted)
Location:      tekun-corporation-profile.md §6.1
Reader impact: Client organisation names were read from logo image filenames and
               the rendered panel. Exact legal names are unverified, and six of
               the claimed 30 could not be identified.
Why accepted:  The method is stated in the file, and CLM-007 restricts external
               use until names are verified.
Follow-up:     Verify legal names before any external use.
```

---

## 7. Preference-level observations, not defects

```text
ID:            P-001
Severity:      Preference
Observation:   The claim register is long. A reader wanting only the prohibited
               claims must scan several sections.
Response:      Not changed. The register is a governance artifact, and the
               DO NOT USE rows are deliberately placed alongside the claims they
               contradict. A condensed prohibited-claims list already exists at
               unknowns-and-discovery-questions.md §8.
```

```text
ID:            P-002
Severity:      Preference
Observation:   The RACI table is wide and, after em dash removal, uses "n/a" where
               a blank previously indicated non-involvement.
Response:      Accepted as-is. "n/a" is unambiguous, and the legend defines R, A,
               C and S. Narrowing the table would lose the stakeholder columns
               that make the accountability argument.
```

---

## 8. Mechanical checks repeated

| Check | Result |
| --- | --- |
| **File completeness** | 13 of 13 required files present |
| **Internal links** | All relative Markdown links resolve to existing files. Verified by script |
| **Claim ID integrity** | CLM-001 to CLM-114 present; no duplicate IDs; no orphan IDs referenced from prose |
| **Source ID integrity** | SRC-001 to SRC-036 present; every source cited in a claim exists in the register |
| **Contradiction IDs** | CON-001 to CON-008 present |
| **Research area coverage** | All areas A to O covered, with a coverage summary at source-register.md §9 |
| **Forbidden terminology** | Zero em dashes. No "grant recipient" outside prohibitions. No miscapitalised company name (the shared rule is `Sifututor`) |
| **Unresolved placeholders** | None. No unfilled task markers or angle-bracket template fields remain |
| **Sensitive content** | No credentials, no personal data, no confidential TEKUN information, no `.env*` or `live/` access |
| **Mermaid diagrams** | 13 blocks across 6 files; all opened and closed correctly; node labels re-inspected after em dash removal |
| **Diagram honesty** | Unverified diagrams carry warning headings and dashed edges |
| **Volatile-source reverification** | Consumer Credit Act commencement, Part V boundary, transition window, phased approach, MSE threshold, registration thresholds and fees, and conduct standard effective dates all reopened at their primary sources on 31 August 2026 |

---

## 9. What this review could not do

Stated so the limitation is not silently absorbed.

1. **It was not independent.** The same agent produced and reviewed the pack.
   Independent fresh-context review would add most value on the legal
   interpretation in §4 of the regulatory file.
2. **It could not verify TEKUN Corporation's private facts.** Everything about
   contracts, fees, portfolios, systems and registration remains outside public
   evidence.
3. **It could not test the legal conclusions.** CON-003 is a genuine open legal
   question and is left open deliberately.
4. **It could not check the SKP register.** No public register was located, so
   the pack's most time-critical unknown remains unresolved.

---

## 10. Exit statement

```text
blocking findings remaining: 0
material findings remaining: 0
minor findings: 3, all accepted and disclosed with follow-ups
preference findings: 2, accepted
```

---

## 11. Highest proven state and next action

- **Highest proven state:** a complete, governed research reference pack of 13
  files, with 114 registered claims and 36 registered sources, in which every
  material regulatory claim rests on legislation, a gazette notification, a
  regulator standard or a government audit report that was opened and read;
  every TEKUN commercial fact is explicitly marked as not publicly disclosed; and
  every unsupported claim is marked DO NOT USE. Local files only. Nothing
  committed, pushed, uploaded, published or externally shared.

- **Single next action for the document owner:** read
  [research-handback.md](research-handback.md), then decide whether to take the
  ten Tier-1 discovery questions to TEKUN Corporation, leading with the SKP
  registration question.
