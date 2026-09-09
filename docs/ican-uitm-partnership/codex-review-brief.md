# Adversarial review brief: ICAN UiTM partnership deck

You are a fresh-context adversarial reviewer. You did not build this deck. Your job is to find what is wrong, weak, misleading, inconsistent or visually broken before it is presented. Do not edit any file. Write your findings only.

## What you are reviewing

- `ican-uitm-deck-v2.html`: a self-contained 12-slide HTML presentation (fixed 1920x1080 stage). Read the markup and CSS.
- The 12 rendered slides are attached as images (slide-01 to slide-12, in order). Inspect every one at full size.

## Context you must use

- Presenter: Hafiz Razali, CTO and co-founder of Sifututor (academic tutoring marketplace) and Nakngaji (Quran and Islamic studies tutoring). Both operate since 2018 on one in-house platform.
- Meeting: 9 September 2026, 11:00, Rumah Alumni, Intekma Resort, UiTM Shah Alam. Host is ICAN (Office of Industry, Community and Alumni Network), specifically its Division of Community and Sustainability Network (BJKK). Attendees: BJKK director and unit heads (Community Impact Lab; Social Innovation and Knowledge Transfer Unit; Environmental Sustainability Unit), one Faculty of Education academic (educational technology research), one officer from CyberSecurity Malaysia (the national agency). No prior relationship; the meeting came from Sifututor's cold email.
- Purpose: propose three tracks (UiTM students and alumni as verified tutors and asatizah; practicum placements; joint technology and artificial intelligence projects), framed around community impact. Ask is owners and a first pilot, not a signature.
- Approved external figures (do not accept anything beyond these): since 2018; RM25m+ paid to tutors and asatizah (payout, never revenue; RM60m must never appear); 20,000+ tutors and asatizah engaged; about 2,000 delivering monthly; 1,000,000+ teaching hours; 50,000+ students; 10,000+ classes a month and ~69 new requests a day (verified July 2026); public rate range RM9 to RM84 per hour; tutor commitment fee exists; Nakngaji applicants take a screening quiz on teaching procedure and tajwid; a tutor is confirmed to a family only after the Tutor Experience team approves verification.
- Precedents cited: ZTE with Multimedia University; IBM SkillsBuild with UTAR; UiTM's 18 industry partners through 8 MoUs and 10 MoAs (one college). Regulatory context cited: Child Protection Code under the Online Safety Act 2025 effective 1 June 2026; National Cyber Ethics Module rollout in schools from January 2026 with CyberSecurity Malaysia as technical partner; Personal Data Protection Act 2010; National Guidelines on AI Governance and Ethics (2024).
- House writing rules: no em dashes; expand abbreviations on first use; "Sifututor" always in full, never "Sifu"; "Nakngaji" one word; never bare "AI" in body copy (spell out artificial intelligence; quoted titles excepted); plain professional English; no left accent bars on cards; assertion headlines; nothing presented as current capability that is only proposed; generated or illustrative images must be labelled.

## Review dimensions (from the document-production adversarial review)

1. Truth and evidence: any claim not covered by the approved facts above, any overclaim, any "proposed" thing written as if it exists, any figure or citation that reads stronger than its source.
2. Narrative credibility: does the argument hold for a senior university community-engagement audience? Anything that would make them distrust us? Anything presumptuous about UiTM units, faculties or people?
3. Completeness: what a BJKK director would expect to see and cannot find (for example, what it costs UiTM, safeguarding, data, who does the work, what happens after the pilot).
4. Audience comprehension: jargon, unexplained acronyms, sentences a non-technical reader would stumble on, headlines that are labels rather than assertions.
5. Visual and output quality: check every slide image for overlap, clipping, cut-off text, misalignment, uneven margins, inconsistent spacing between cards, wrong or low-contrast colours (for example text that should be white on a coloured circle), inconsistent chip or pill styles, orphaned words, empty areas that look unfinished, elements too close to edges or to each other, arrows or connectors badly placed, logo sizing or balance, and anything inconsistent between slides.
6. Confidentiality and publication risk: anything that should not be shown to an external audience.
7. Maintenance: anything volatile that will be wrong soon.

## Output format

Write to stdout a Markdown report with these sections:

- Summary: one paragraph.
- Findings table with columns: ID, Severity (Blocking / Material / Minor / Preference), Slide, Element or exact text, Problem, Concrete fix. Be specific: quote the text, name the CSS class or region, say exactly what to change.
- Visual issues per slide: a short list per slide, or "none found" for that slide.
- Counts: blocking, material, minor, preference.

Severity meanings: Blocking = unsafe, materially false, contradictory, unusable. Material = likely to change the audience's interpretation, credibility or a major decision. Minor = worth improving. Preference = style only.

Be adversarial and thorough. Do not praise. Do not soften. Do not invent facts about Sifututor beyond the list above; if something cannot be verified from this brief, flag it as unverified rather than asserting it is wrong.
