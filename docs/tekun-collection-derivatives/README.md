# TEKUN Collection Derivative Package

For the complete partnership document map and compiled internal/external bundles, start with [`../tekun-collection-partnership-pack/TEKUN-PARTNERSHIP-PACK-START-HERE.pdf`](../tekun-collection-partnership-pack/TEKUN-PARTNERSHIP-PACK-START-HERE.pdf).

This folder contains three audience-specific documents governed by `docs/tekun-collection-partnership-sourcebook.md` v1.0.

## Which document to use

| Need | Use | Format |
| --- | --- | --- |
| Brief leadership and obtain approval for discovery/pilot co-design | Executive stakeholder presentation | `tekun-executive-stakeholder-deck.pdf` or `.html`; edit the `.md` source |
| Give authorised TEKUN stakeholders a complete controlled proposal | Controlled external proposal | `tekun-controlled-external-proposal.pdf` or `.docx`; govern changes in the `.md` source |
| Prepare internal product, engineering, operations, finance and compliance teams | Internal technical and operations presentation | `tekun-internal-technical-operations-deck.pdf` or `.html`; slides 1–35 are the core and 36–42 are optional appendices |

## Distribution boundaries

- Executive deck and proposal: confidential, controlled stakeholder use.
- Internal deck: internal working use only; do not circulate externally.
- Before external circulation, confirm the proposing legal entity and authorised contact in the proposal.
- Reverify volatile TEKUN Corporation and Consumer Credit Commission public sources.
- Do not add prices, guaranteed recovery, profit promises, provider identities, portfolio facts or legal conclusions without the required owner approval and evidence.

## Package governance

- `derivative-contract.md` — audience, scope and acceptance contract.
- `extraction-matrix.md` — what each audience receives and what remains internal.
- `review-and-acceptance.md` — checks, review rounds and remaining circulation gates.
- `check-derivative-package.py` — deterministic package checker.
- `render-deck.mjs` / `render-proposal.mjs` — regenerate derived HTML.
- `render-executive-frontend-deck.mjs` — regenerate the executive HTML with
  the governed fixed-stage presentation system, embedded fonts, navigation and
  evidence drawer.
- `check-executive-frontend-deck.cjs` — verify 16:9 scaling, navigation,
  source links, source drawer and overflow at desktop and phone viewports.
- `render-deck-pdf.cjs` / `render-proposal-pdf.cjs` — regenerate PDFs.

The Markdown sources are authoritative for the three derivatives. HTML, PDF and DOCX files must be regenerated after material edits.
