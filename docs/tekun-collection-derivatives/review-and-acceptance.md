# TEKUN Derivative Package — Review And Acceptance

| Item | Result |
| --- | --- |
| Review date | 1 September 2026 |
| Governed source | TEKUN Corporation Integrated Collection Growth Partnership Sourcebook v1.0 |
| Executive package | 18-slide Markdown, HTML and PDF |
| Controlled proposal | 25-page Markdown, HTML, PDF and editable DOCX |
| Internal package | 35-slide core plus 7-slide optional appendix; Markdown, HTML and PDF |
| Highest proven state | Locally produced, rendered, reviewed and accepted; not committed, uploaded, shared or externally approved |

## Deterministic checks

- `python3 docs/tekun-collection-derivatives/check-derivative-package.py` — **PASS**.
- Executive and internal deck overflow/top-edge checker — **0 failures**.
- Executive PDF — **18 pages**, 16:9 landscape.
- Controlled proposal PDF — **25 A4 pages**.
- Internal PDF — **42 pages**: slide 35 is the core decision; slides 36–42 are optional appendices.
- External internal-claim-ID scan — **none**.
- Diagram-reference manifest — **exact**.
- Proposal DOCX ZIP integrity — **valid**; embedded media present.

## Visual QA

All three PDFs were rasterised and inspected through contact sheets and targeted full-page checks. Corrections included:

- rebuilding the three-responsibility slide as semantic columns;
- detecting and correcting shifted diagram mappings for payment, reporting, service management and pilot visuals;
- adding top-edge detection after appendix titles exposed a clipping case;
- separating the 35-slide internal core from its optional reference appendix;
- preventing orphaned proposal sections with controlled page breaks;
- confirming the final payment sequence, pilot, reporting and assurance visuals at full-page size.

## Executive frontend presentation enhancement

On 1 September 2026, the executive stakeholder deck was upgraded from a printable HTML treatment into a self-contained presentation while retaining the Markdown deck as the governed content source.

- The presentation now uses a fixed 1920 × 1080 stage with uniform desktop and mobile scaling.
- Keyboard, wheel, touch, fullscreen, slide-progress and per-slide evidence controls are included.
- Public evidence links are clickable and open independently from the presentation.
- Fonts and presentation assets are embedded locally; the deck does not depend on a live font service.
- Six diagram-heavy slides use presentation-native HTML/CSS diagrams so labels remain readable at slide scale. The governed Markdown references remain unchanged.
- The cover proposition and the two-column opportunity slide were corrected after full-page visual inspection exposed contrast and semantic-grouping defects.

Fresh public-source verification covered the Consumer Credit Commission implementation notice, authorisation and conduct standards release, debt-collection guidance, TEKUN Corporation collection-service page, and the MOCCIS appointment and contract announcements. The Awqaf Education page did not return reviewable content during this final pass, so no new verification is claimed for it; its original governed research-pack treatment remains unchanged.

Enhancement checks:

- `node docs/tekun-collection-derivatives/check-executive-frontend-deck.cjs docs/tekun-collection-derivatives/tekun-executive-stakeholder-deck.html` — **PASS**: 18 slides, 9 external links, navigation, evidence drawer, desktop scaling, phone scaling and zero overflow.
- Executive PDF regeneration — **18 pages**, 16:9 landscape.
- Full-page visual QA — cover, opportunity framing and all six native diagram slides inspected after correction; no clipped or unreadable presentation labels remain.
- Content boundary — no pricing, guaranteed outcomes, legal conclusion or artificial-lock-in claim was added.

Enhancement adversarial pass:

| Review focus | Blocking | Material | Minor | Outcome |
| --- | ---: | ---: | ---: | --- |
| Visual and interaction regression | 0 | 2 | 0 | Cover contrast and two-column semantic grouping corrected |
| Diagram readability | 0 | 1 | 0 | Clipped SVG labels replaced by presentation-native diagrams |
| Final contract, extraction and claim-boundary review | 0 | 0 | 0 | **PASS** — the presentation remains within its executive audience, decision and disclosure boundaries |

## Adversarial review record

An independent read-only adversarial reviewer compared the derivatives with the sourcebook, derivative contract and extraction matrix.

| Round | Blocking | Material | Minor | Outcome |
| --- | ---: | ---: | ---: | --- |
| Initial | 0 | 5 | 3 | Source attribution, KPI/discovery completeness, transition/assurance detail, proposer identification boundary and three wording/content gaps corrected |
| Correction review | 0 | 1 | 3 | Core-versus-appendix packaging and three residual wording gaps corrected |
| Final clean review | 0 | 0 | 0 | **PASS** — no factual, legal, commercial, audience-separation or structural regression found |

The strongest content preserved through correction is the respectful established-operator framing, bounded discovery/pilot decision, separation of promise/payment/reconciliation, human consequential authority, balanced evidence gate, source-limited Sifututor capability claim and evidence-gated H0–H5 roadmap.

## Claude review status

The requested supervised Claude critique was prepared and passed its initial preflight, but Claude Code reported `logged_in: false` at launch. No Claude review is claimed. The bounded critique contract remains at `.agent-os/delegations/tekun-derivatives-adversarial-review.json` for a future run after Claude authentication is restored. An independent Codex reviewer completed the three review rounds above as the transparent fallback.

## Gates before external circulation

1. Confirm the proposing legal entity, brand relationship and authorised proposal contact.
2. Reverify the volatile public sources named in the proposal endnotes.
3. Obtain document-owner approval for the intended recipient list and classification.
4. Keep the internal technical/operations deck internal.
5. Do not treat the proposal as a contract, price, legal opinion, implementation commitment or guaranteed performance result.

## Acceptance decision

The local three-document package is accepted for owner review. It is ready to read and adapt, but external circulation remains controlled by the gates above.
