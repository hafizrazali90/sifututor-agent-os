# Status page user stories (approved by Hafiz 04/10/2026)

Source: docs/status-page-prd.md. Issue: hafizrazali90/sifututor-agent-os#240. Stages 0 and 1 of the build plan are live (04/10/2026); stages 2 to 5 are not approved.


US-MON-001: As the CTO, I want one banner that says whether anything is wrong so that I know in under 5 seconds whether I need to act.

Acceptance Criteria:
- [ ] Banner shows normal, attention or down, with last-check time in MYT
- [ ] Banner turns to attention if any card is red or data is stale
- [ ] Unknown data never shows as normal

US-MON-002: As the CTO, I want a "Needs you" list so that I only see items waiting on a human.

Acceptance Criteria:
- [ ] Lists approvals pending, expiries within 30 days and failed backups
- [ ] Empty list shows "Nothing needs you"
- [ ] Each item says what, since when and where to act

US-MON-003: As the CTO, I want a card per system with a plain sentence so that I understand its state without opening other tools.

Acceptance Criteria:
- [ ] Cards exist for SIMS, Ripple, Finch, LLS, Kelasapp and Owner Analytics
- [ ] Each shows state, one plain reason and last-check time
- [ ] A card links to its evidence

US-MON-004: As the CTO, I want a robot panel so that I can see whether outreach is sending safely.

Acceptance Criteria:
- [ ] Shows running or paused and slices completed and failed today
- [ ] Shows whether we are inside the 09:00 to 21:00 MYT window
- [ ] Flags any send outside the window

US-MON-005: As the CTO, I want backup freshness per system so that I know recovery is possible.

Acceptance Criteria:
- [ ] Shows last good backup time and allowed age
- [ ] Turns red when older than allowed
- [ ] Covers SIMS, Ripple, LLS, Kelasapp, Finch and Koda

US-MON-006: As the CTO, I want renewal countdowns so that no domain, certificate or plan lapses.

Acceptance Criteria:
- [ ] Lists domains, SSL and hosting renewals with date and days left
- [ ] Warns at 30 days and again at 7 days
- [ ] Renewal dates can be entered by hand where no API exists

US-MON-007: As the CTO, I want an activity feed so that I can see what changed before something broke.

Acceptance Criteria:
- [ ] Deploys appear automatically with time in MYT
- [ ] Notes can be added with what, why and who
- [ ] Feed is newest first, last 30 days

US-MON-008: As the CTO, I want monitoring health shown so that I know the monitoring itself works.

Acceptance Criteria:
- [ ] Shows heartbeats arriving and any missing
- [ ] Shows Sentry accepted vs rejected and quota used
- [ ] Shows last alert test time

US-MON-009: As the CTO, I want a Telegram message when something breaks and when it recovers so that I do not need to watch the page.

Acceptance Criteria:
- [ ] One plain message per incident with what, since when and who is affected
- [ ] A recovery message when it clears
- [ ] A quiet daily summary at 10:00 MYT

US-MON-010: As the CTO, I want the page private so that no one without access sees our systems.

Acceptance Criteria:
- [ ] Unauthenticated visitors cannot see any status data
- [ ] Access is limited to approved emails through Cloudflare Access
- [ ] The site holds no production write credentials
