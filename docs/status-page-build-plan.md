# Status page build plan

Written 04/10/2026 for Hafiz. Issue: hafizrazali90/sifututor-agent-os#240.
Inputs: [status-page-prd.md](status-page-prd.md), [user stories](features/monitoring/user-stories.md), [accepted mockup v4](features/monitoring/status-mockup-v4.html).

Status (04/10/2026, about 12:50 MYT): stages 0 and 1 are APPROVED, BUILT and LIVE at https://status.sifututor.my (see the progress log, newest entry first below the plan). Stages 2 to 5 are NOT approved and not built; each needs its own go. Stage 4 (Telegram) is the recommended next package, prepared in docs/status-page-stage4-telegram-plan.md.

## The idea in one paragraph

Build it in five stages, safest first. Stage 1 gives you a real, working page using only the outside services we already read (Better Stack, Sentry, certificate and domain dates). It touches no production server. Every later stage adds one kind of information and one kind of access, and each can be switched off without breaking the earlier ones.

## How it works (plain terms)

- **The site:** a small program on Cloudflare (a Worker) that serves the page and answers a few addresses. Free plan.
- **Its memory:** a small Cloudflare database (D1) that stores one status record per check every 5 minutes, and the change notes. 30 days kept.
- **The gate:** Cloudflare Access. Only approved emails (you and the developers) can open it.
- **The clock:** a Cloudflare timer runs every 5 minutes, asks the outside services for their state and saves it.
- **The collectors (later stage):** a tiny script on each server that sends a few numbers to the site. It only sends. The site never logs in to any server and holds no production password.
- **The notes:** one address any tool or person can post a short note to, with a private key. Author shown on every note.
- **Telegram:** a bot that posts when a state changes, and one summary at 10:00 MYT.

Rule kept everywhere: a source that stops answering shows "No data", never "Online".

## Stages

| Stage | What you get | Touches production? | Access needed | Proof it works |
| --- | --- | --- | --- | --- |
| **0. Foundations** | Empty private site behind the login gate, repo, database, deploy pipeline | No | Cloudflare account (Workers, D1, Access), a new repo in the Sifututor account, a site address | You open the address, sign in, see a placeholder. A stranger is refused |
| **1. Live page from outside services** | Banner, system map, system detail, "Can we trust this page", "Running out soon". Real data, 5-minute refresh | No | Read-only Better Stack and Sentry keys stored as Cloudflare secrets | Page matches Better Stack and Sentry for 24 hours. Pause one test monitor: page turns red, then recovers. Cut a key: page shows "No data", not green |
| **2. Change feed** | "What changed" with plain title, why, who, approval, technical line. Notes posted by Claude, Codex or a developer | No | One notes key. GitHub webhook for merges (read-only event) | A posted note appears within a minute with its author. A note without the key is refused |
| **3. Server facts (collectors)** | Outreach robot panel, backup freshness, disk, queue state. One server at a time | **Yes, small:** adds one read-only script and one timer per server | Per server, with that server's owning session: Ripple host, Finch and Analytics host, SIMS production, Learnest server | For each server: numbers on the page match a manual read. Stop the script: its values turn "No data" after 15 minutes |
| **4. Telegram** | Alert when something breaks, recovery message, daily summary at 10:00 MYT | No | A Telegram bot you create and the group id | One test message, one real red and recovery from a paused test monitor, one 10:00 summary |
| **5. Finish** | 30-day timeline, "Needs you" rules, phone polish, app cards as "No data" until app monitoring exists | No | None new | Walk through all 10 user stories (US-MON-001 to 010) with screenshots on desktop and phone |

## What each stage needs from you

1. **Stage 0:** approve creating the repo and the Cloudflare pieces, and pick the address. Suggested: `status.tutorla.tech` (the zone is already in Cloudflare).
2. **Stage 1:** approve storing the two read-only keys as Cloudflare secrets.
3. **Stage 2:** approve the notes key and the GitHub webhook.
4. **Stage 3:** approve each server separately. This is the only stage that changes production servers, so the owning session reviews its own server first.
5. **Stage 4:** create the Telegram bot and group, save the bot token to a protected file (I will guide you, as with the Better Stack token).
6. **Stage 5:** review the finished page against the mockup.

## Safety boundaries

- The site holds read-only keys and never a production password or database login.
- Collectors send only counts and states. Never log text, names, phone numbers or message content.
- Each collector has its own key that can only send data, so a leaked key cannot read anything.
- Every stage ships to a preview address first, is checked, then goes live.
- Rollback for stages 0, 1, 2, 4 and 5: redeploy the previous version (one command). Stage 3: remove the timer and the script on that server.
- Outreach robot: the collector only reads its counters. It never pauses, resumes or sends.

## How it will be tested

- **Rules as tests first.** The roll-up rules get written as tests before the code: unknown is never green, one red system makes the banner red, stale data shows a warning.
- **Real incidents as test cases.** The 03/10 full disk, the 32 failed queue checks, the week of rejected Sentry data and tonight's failed Analytics refresh each become a fixture. The page must show each one correctly.
- **Browser check.** An automated browser opens the page on desktop and phone sizes and compares it with the accepted mockup.
- **Independent review.** Codex reviews each stage before you see it.

## Cost

- Cloudflare free plan is expected to be enough (a timer every 5 minutes and a handful of readers). To confirm against the current free limits at Stage 0, before anything depends on it.
- Telegram bot: free.
- Better Stack: stays on the free plan for this. Extra heartbeats are a separate, parked decision.

## Risks

| Risk | What it would cause | How the plan handles it |
| --- | --- | --- |
| Page says "fine" while a source is dead | False confidence | "No data" state, stale warning, tested by cutting a source in Stage 1 |
| A collector adds risk to a production server | Security or load problem | Stage 3 is last of the data stages, one server at a time, read-only, owner reviewed |
| Too many Telegram messages | Alerts get ignored | One message per incident, quiet daily summary, tested before going live |
| Free limits change or are lower than expected | Missing updates | Check limits in Stage 0, record them in the repo |
| Notes are wrong or missing | Misleading feed | Author on every note, corrections are new notes, "not recorded" shown when nobody wrote one |

## Not in this plan

- Mobile app releases (excluded).
- Automatic investigation or fixing.
- A public page for customers.
- The extra heartbeats (parked on #240).

## First decision

Approve Stage 0 and Stage 1 together. They touch no production system, and at the end you have a real page with real data to judge before anything else is built.

## Progress log

Newest entries first. Earlier entries are kept as written, so a value that changed later (for example who can sign in) is corrected in the entry above it, not rewritten.

**04/10/2026, about 12:50 MYT. Current state and Stage 1 corrections.**

- Sign-in: Cloudflare account and One-time PIN are both switched on (PIN on since 04/10). Allowed emails: `hafiz.razali@sifututor.my`, `sifututor@gmail.com`, `syamil.yusoff@sifututor.my`. This replaces the "PIN not switched on, two emails" line in the 05:10 entry below.
- Readings: 98 stored readings from 04:20 to 12:25 MYT, no gap above 7 minutes. All 20 Better Stack checks match Better Stack's incident history for that window (interim, 8.1 of 24 hours; the full 24-hour comparison completes after 04:25 MYT on 05/10).
- Codex review of the live page found two truthfulness gaps. Both are fixed on branch `fix/240-truthful-rollup-and-sentry-proof` in `sifututor-status` (PR https://github.com/Sifututor/sifututor-status/pull/1, approved to push by Hafiz 04/10; deploy is a separate step):
  1. A silent optional check kept a system Online and the card said "All N checks are passing". Now Online requires every check to pass; a silent optional check makes the system Degraded and the card names what is not answering.
  2. Zero Sentry errors was shown as "Error tracker is receiving". Now the check says the tracker answers and is not rejecting records, zero errors is a quiet day (never an incident), and the trust panel lists which systems have not been seen sending an error in 24 hours. Proof that a running app delivers errors still needs a separately approved test event.
- Tests: 68 unit tests and 25 stored browser tests (desktop 1440x900 and phone 390x844, fixture readings, no login or network) pass.
- Still unproven: a real One-time PIN sign-in (needs a person to receive the code), and the full 24-hour comparison.
- Not approved and not started: stages 2 to 5, any server collector, Telegram, extra heartbeats (parked). Mobile apps excluded.

**04/10/2026, about 05:10 MYT. Stages 0 and 1 are live.** Approved by Hafiz in session ("Approve both", then "do until complete").

- Address: https://status.sifututor.my, behind the Cloudflare Access application "Sifututor Status" (team `flat-mouse-b011`, Zero Trust Free).
- Allowed: `hafiz.razali@sifututor.my`, `sifututor@gmail.com`. Only the "Cloudflare" sign-in method is on, so today only the Gmail (the Cloudflare account) can sign in. One-time PIN is not switched on yet; it is free and is what developers will need. (Superseded the same day: PIN was switched on and a third email added, see the 12:50 MYT entry above.)
- Repo: https://github.com/Sifututor/sifututor-status (private), first commit `0f0b4c9`. Cloudflare Worker `sifututor-status`, D1 database `sifututor-status`.
- Proven: 52 tests pass; the timer stores a reading every 5 minutes; readings match Better Stack and Sentry; a stranger is redirected to the login; the workers.dev address returns not found; Hafiz signed in and saw the page.
- Codex adversarial review ran before going live. Five findings, all fixed with tests (stale readings shown as old green, silent systems missing from Needs you, blind periods erased from the daily strip, key hardening, list paging).
- Known gaps: no automated browser test stored in the project yet; the outreach robot and the apps show No data until Stage 3; certificate and domain dates are entered by hand in `src/config.js`.
- Cloudflare login used: `wrangler login` (OAuth) on this Mac, broader than this project needs. The Access application was created through the dashboard because that login does not cover Access.
