# Status Page PRD (private monitoring site)

Status (04/10/2026, about 12:50 MYT): user stories APPROVED. Build plan stages 0 and 1 are BUILT and LIVE at https://status.sifututor.my (approved by Hafiz 04/10, see the build plan progress log). Stages 2 to 5 are NOT approved and not built. Issue: hafizrazali90/sifututor-agent-os#240 (kept open).

Assumptions are marked **(A)**. Earlier decisions already made by Hafiz: private site on Cloudflare free plan behind Cloudflare Access; Telegram group via bot for alerts; scope covers SIMS, Ripple, the outreach robot, Finch, tutor and parent apps, Learnest (LLS), Kelasapp, Owner Analytics; Claude activity feed from automatic deploys plus explicit notes; repo inside the Sifututor account.

## 1. One-Sentence Problem

> Hafiz struggles to see in one place whether SIMS, Ripple, Finch, Learnest and Kelasapp are healthy and what changed, because status lives in many tools and chat sessions, resulting in problems found late (a full disk, a week of rejected Sentry data, a missed backup) and constant manual checking.

## 2. Demo Goal (What Success Looks Like)

- Hafiz opens one private page on his phone and in under 5 seconds knows: is anything wrong, and does it need me?
- The page shows real data for at least SIMS, Ripple (including the robot), Finch and LLS, and is clearly fresher than 5 minutes.
- A red state sends one plain-language Telegram message, and a recovery message when it clears.

Non-goals (out of scope for the demo):
- Public customer status page, incident posting by customers.
- Mobile app release monitoring (mobile releases are excluded).
- Automatic investigator or auto-fix.
- Writing to any production system. The site is read-only.

## 3. Target User (Role-Based)

- **Role:** the CTO (Hafiz) and the developers he approves. **Decided 04/10/2026:** readers are Hafiz and developers; CX staff are not v1 readers. Access list kept in Cloudflare Access.
- **Skill level:** knows logic, data, backend and frontend, not code. Needs plain sentences, real terms defined once.
- **Key constraint:** reads it on a phone, often between other work. Time is the scarce resource.

## 4. Core Use Case (Happy Path)

Start: Hafiz opens the status URL and signs in through Cloudflare Access.

1. The banner reads "All systems normal" with the last check time in MYT.
2. The "Needs you" list is empty.
3. System cards show green for SIMS, Ripple, Finch, LLS, Kelasapp and Owner Analytics.
4. He glances at the robot panel (running, slices today, 0 failed).
5. He scrolls to backups and renewals (all fresh, nearest expiry shown).
6. He reads the last three activity entries ("Ripple released 22:21 MYT").

End: he closes the page without opening any other tool. If something is red, the banner says what, since when, and links to the evidence.

## 5. Functional Decisions (What It Must Do)

| ID | Function | Notes |
| --- | --- | --- |
| F1 | Show an overall banner (normal, attention, down) with last-check time in MYT | Computed from all cards |
| F2 | Show a "Needs you" list of urgent items only | Failed backups, red systems, expiry within 30 days. Pending approvals are not listed (decided). Empty on a normal day |
| F3 | Show one status card per system with a plain one-line reason | SIMS, Ripple, Finch, LLS, Kelasapp, Owner Analytics, tutor and parent apps (apps included in v1 per decision; grey "no data" until app monitoring exists) |
| F4 | Show the outreach robot panel | Running or paused, slices completed and failed today, inside or outside the 09:00 to 21:00 MYT window |
| F5 | Show backup freshness per system | Last good backup time and its allowed age |
| F6 | Show renewal and expiry countdowns | Domains, SSL certificates, hosting plans, subscriptions |
| F7 | Show an activity feed | Automatic deploys plus explicit notes entered by Claude or Hafiz |
| F8 | Show monitoring health | Heartbeats arriving, Sentry accepted vs rejected, quota used, last alert test |
| F9 | Send Telegram alerts on red and recovery | One short message per incident, plain language, MYT |
| F10 | Keep 30 days of status history | Per-system timeline (decided) |
| F11 | Restrict access to approved people | Cloudflare Access, no public view |

## 6. UX Decisions (What the Experience Is Like)

### 6.1 Entry Point
- A single private URL behind Cloudflare Access. First thing seen: the banner with overall state and time.

### 6.2 Inputs
- None from the viewer in v1 except sign-in. **Decided:** activity notes come from whichever AI tool (Codex, Claude, others) or developer made the change, through one simple tool-agnostic note endpoint with a private key. Every note shows its author and time; corrections are new notes, never silent edits.

### 6.3 Outputs
- A phone-first single page, refreshed every 5 minutes (decided), plus Telegram messages. Order: banner, Needs you, system cards, robot, backups and renewals, activity, monitoring health.

### 6.4 Feedback & States
- **Loading:** skeleton cards, never an empty white page.
- **Success:** green dot and one sentence.
- **Failure:** red card at the top of its section, banner updates, with "since" time.
- **Partial:** a source that did not answer shows grey "no data since HH:MM MYT", never green. Missing data is never treated as healthy.

### 6.5 Errors (Minimum Viable Handling)
- **Source API fails:** card turns grey with the last known time.
- **Collector stops reporting:** after 15 minutes the page shows "data is stale" on the banner.
- **User does nothing:** the page does not auto-alert; Telegram is the push channel.

## 7. Data & Logic (At a Glance)

### 7.1 Inputs
- Better Stack monitors and heartbeats (API), and Healthchecks.io later **(A)**.
- Sentry stats, quota and issues (read-only key).
- Domain and certificate dates (small daily check).
- Server facts (PM2 state, backup ages, disk, robot counters) pushed by small read-only collectors on each host. The site never logs into production.
- GitHub release events and explicit notes for the activity feed.

### 7.2 Processing
- Fetch or receive → normalise to one status record per check (ok, warn, fail, unknown) → roll up per system → roll up to banner → store snapshot → alert on state change.

### 7.3 Outputs
- UI, a stored 30-day history, and Telegram messages. Logs of the site itself are kept for the status of the status page.

## 8. Logical Dependency Chain

1. **Foundation:** repo, Cloudflare Access gate, storage for status records, one collector contract (what a check reports), Telegram bot and group.
2. **Core:** banner and system cards for SIMS, Ripple, Finch and LLS from Better Stack and HTTP checks, with the "unknown is not green" rule.
3. **Extensions:** robot panel, backups and renewals, monitoring health (Sentry quota), activity feed, Telegram alerts and recovery, 30-day history.
4. **Polish:** needs-you rules, copy review in plain language, mobile pass, empty and stale states, owner analytics and app cards.

## 9. Risks & Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Status page shows green while a source is silently dead | False confidence, the exact failure we are fixing | "Unknown" is a first-class state, stale-data banner, test by cutting a source |
| Collectors on production hosts add access and attack surface | Security incident | Read-only, push-only, scoped token per host, reviewed per host before install |
| Free-tier limits (Cloudflare, Better Stack heartbeats) | Missing checks | Plan capacity recorded; Healthchecks.io for extra heartbeats |
| Scope creep (many systems, many panels) | Never ships | Ship Core for four systems first |
| Alert noise in Telegram | Alerts ignored | One message per incident, quiet daily summary, severity levels |

## 10. User Stories (approved by Hafiz 04/10/2026)

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

## UX direction (decided 04/10/2026, from Mobbin and web research)

- Reference: Railway (service boxes with an Online label, click opens a side panel of details), plus Customer.io for the verdict and last-updated line and Mintlify for activity rows. Mobbin links: Customer.io b9743841-5a29-4454-bc39-133d7b0d7d9c, Mintlify 31bc9279-f1e6-449c-9143-583e558609b4, Railway 5d0430e0-67d6-46f1-ba26-25106f7614cd, Plain 4b396c6e-917b-4dcf-bea8-0587c3dd4b1e.
- Desktop: a connected map of systems (boxes with lines showing what feeds what). A red box visibly tints the systems that depend on it.
- Click a box: a side panel opens with details and the 30-day timeline.
- Dark theme by default.
- Phone: the map becomes a plain list, one row per system, with the same verdict, Needs you and activity sections above and below.
- Always shown: banner verdict with last-checked time (MYT), grey for unknown, a stale-data marker.
- Map lines: SIMS to Ripple, SIMS to Owner Analytics, Finch to SIMS (receipt matching), apps to SIMS. Finch to Ripple (receipt sync) is dashed because it is staging-only. Learnest and Kelasapp stand alone. Lines to be confirmed by each owning session before build.
- Side panel order (decided): 1 plain status sentence with since-time, 2 30-day timeline bar, 3 the checks behind it (monitors, heartbeats, errors), 4 recent changes for that system, 5 evidence links (Sentry, Better Stack).
- State words (decided): Online (green, all checks pass), Degraded (amber, working but something is off, e.g. disk 88% or a failing check with no user impact), Down (red, people cannot use it or a critical job failed), No data (grey, source stopped answering; never shown as healthy).

## Mockup accepted (04/10/2026, about 03:25 MYT)

Hafiz reviewed version 4 of the static mockup and said it looks good. Link (private): https://claude.ai/artifact/XGVcWadhMZBNqWcozfRehn. Source file kept in the session scratchpad as status-mockup.html; copy it into the repo before the build starts.

What version 4 fixes as the design:
- Desktop: the system map is the full-screen header. Verdict and counts sit on the canvas, the detail drawer floats on the right. Clicking a system traces its connections and fades the rest.
- Motion that carries meaning: dots travel along live links, a failed link is red with no dots, a down system pulses, bars grow in. All motion is off under reduced-motion.
- Phone: a health ring (one segment per system), swipeable system cards, a bottom sheet for detail, a fixed tab bar (Systems, Changes, Needs you).
- Change feed: system, verb label, plain title, one sentence of why, who did it, who approved, expandable detail with the technical line and a before and after value. Filter by system.
- Copy rule: plain words first, the technical term underneath in small text, each term explained once (for example: each job sends an "I ran" signal, called a heartbeat).
- Side sections: Needs you, Running out soon, Can we trust this page.

Still not approved: the change feed (stage 2), the collectors on each host (stage 3), the Telegram bot and summary (stage 4), and the finish stage (stage 5). Stages 0 and 1 are live; the rest of this PRD is the design they follow.
