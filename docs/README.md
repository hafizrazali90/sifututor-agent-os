# Workspace documents

This folder holds documents that belong to the Sifututor workspace itself:
shared agent playbooks, onboarding notes, product and QA references, staff
guides, analytics packets and partnership decks prepared here.

## Client and programme documents live in Papertrail

Proposals, reports and decks for a client, prospect or programme belong in
[`Learnest-Lab/papertrail`](https://github.com/Learnest-Lab/papertrail), not
here. That repository is the reference library: one package per client or
subject, with the research, the documents, the decisions and the inputs kept
together, and a filing convention described in its `STRUCTURE.md`.

Already filed there:

| Package | What it holds |
| --- | --- |
| `prospects/kota-buku` | Kota Buku / KPM teacher-iPad concept, research, specifications and deck editions |
| `prospects/tekun` | TEKUN partnership pack, sourcebook, derivatives and research |
| `prospects/kesuma` | KESUMA ecosystem research dossier |
| `prospects/cybersecurity-malaysia` | CyberSecurity Malaysia incident-response ticketing research |
| `company/sifututor-ecosystem` | Ecosystem sourcebook and executive deck |

Those packages were migrated to Papertrail on 8 September 2026 and removed from
this repository on 9 September 2026 so there is a single source of truth. Look
for them there before recreating anything.

## What belongs in this folder

- `agent-playbooks/` shared Agent OS playbooks, the routing and quality rules
- `onboarding/` joining notes
- `products/`, `qa/`, `e2e/` product, QA and end-to-end test references
- `staff-guides/` internal how-to guides
- `review-artifacts/` evidence captured during reviews
- `sims-analytics-*`, `sims-hostinger-migration-*` analytics and migration packets
- `ican-uitm-partnership/` the ICAN UiTM partnership deck and its sources

## The same filing rule applies here

Keep research, documents, decisions and the inputs a document is built from.
Do not commit rebuildable output: screenshots and renders of a document that is
already tracked, PDF-page exports, or zip archives of tracked folders. If
deleting a file loses knowledge, keep it. If it only costs a re-render from a
source that is already here, leave it out and record how to regenerate it.
