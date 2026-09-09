# Parent App Mission Ledger

Use this for parent mobile app missions, child tasks, adjacent ideas, and paused
follow-ups.

## Missions

### PA-LINKS-001 — Migrate Parent App public links to the branded parent namespace

- **Project:** sifututor_parent
- **Status:** captured
- **Type:** mission
- **Parent:** none
- **End goal:** Parent-facing app and web handoff links use the clear `https://go.sifututor.my/parent/*` namespace, with correct Apple and Android ownership and full backward compatibility for every existing Parent App link.
- **Why it matters:** The tutor-request sharing work reserves `/tutor/*` for the Tutor App. The Parent App needs the matching `/parent/*` structure later so public links remain understandable and the two apps do not compete for overlapping paths, without breaking invoices, attendance, classes, referrals, emails, or already-shared links.
- **Source:** Hafiz decision during the tutor-request sharing product-design discussion on 2026-08-04.
- **Next action:** After the tutor-link migration is stable, inventory every Parent App public-link producer, consumer, association path, and fallback journey; then prepare a backward-compatible Parent App PRD and migration plan before creating implementation issues.
- **Promote to:** PRD
- **Links:** none
